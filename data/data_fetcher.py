import os

import pandas as pd
import requests
import time
from core import config
from data.validation import validate_ohlcv

# Environment variable naming a directory of pinned OHLCV CSVs. Checked at call
# time rather than import time, so it can be set after this module is loaded.
PINNED_ENV_VAR = "PHASE7_PINNED_DATA"

# Columns a pinned CSV must provide, in the shape fetch_ohlc() produces.
_OHLCV_COLUMNS = ["open", "high", "low", "close", "volume"]


class DataFetcher:
    """
    Phase‑7 Data Fetcher
    Supports:
        - Local CSV OHLC loading
        - MEXC API OHLC fetching
        - A pinned data source, for reproducible runs (sequence item 3)

    ------------------------------------------------------------------
    THE PINNED SOURCE
    ------------------------------------------------------------------
    Before this existed, get_tf() always went to the live API. That made the
    engine impossible to run twice on the same input, which in turn made most
    of the audit's Verification fields unsatisfiable: "change a knob, rerun,
    compare" cannot be done when every run sees different data.

    Point the fetcher at a directory of CSVs and every fetch is served from
    disk instead:

        set_pinned_source("tests/fixtures/pinned")     # programmatic
        PHASE7_PINNED_DATA=tests/fixtures/pinned       # or by environment

    Files are named {SYMBOL}_{TIMEFRAME}.csv — AEROUSDT_4h.csv,
    AEROUSDT_1d.csv, BTCUSDT_4h.csv. That covers all three series the engine
    fetches (base, macro, BTC context); pinning only the base series would
    leave two thirds of a run still depending on the network.

    TWO DELIBERATE CHOICES, both about failing loudly:

    1. A missing file under an active pinned source is an ERROR, never a
       silent fall-through to the live API. Falling back would reintroduce
       exactly the nondeterminism the pinned source exists to remove, and
       would do it invisibly.

    2. Nothing is cached between calls. Reading a 450-row CSV three times per
       run costs nothing, and handing the same DataFrame object to multiple
       callers was unsafe in this codebase specifically: four modules rewrote
       their caller's columns in place (T2-1). Closed at sequence item 6 —
       calculate_dynamic_bias no longer takes a frame at all, and
       calculate_structure, compute_volume_profile and plot_engine_chart each
       work on their own copy.

       The fresh copy per call stays regardless. It is the guarantee this class
       makes on its own terms rather than a workaround for someone else's bug,
       and it is what test_each_fetch_returns_an_independent_copy asserts.

    Precedence: an explicit set_pinned_source() call beats the environment
    variable, which beats the live API.
    """

    # Class-level, not instance-level, on purpose. engine_core imports the
    # module-scope `data_fetcher` singleton created at the bottom of this file,
    # but tests and callers may construct their own DataFetcher(). A class
    # attribute means every instance agrees on where data comes from.
    _pinned_dir = None

    def __init__(self):
        self.base_url = config.API_BASE_URL

    # ============================================================
    # PINNED SOURCE CONTROL
    # ============================================================

    @classmethod
    def set_pinned_source(cls, path):
        """Serve every subsequent fetch from CSVs in `path`."""
        if path is None:
            cls._pinned_dir = None
            return
        resolved = os.path.abspath(str(path))
        if not os.path.isdir(resolved):
            raise ValueError(
                f"pinned source directory does not exist: {resolved}"
            )
        cls._pinned_dir = resolved

    @classmethod
    def clear_pinned_source(cls):
        """Return to the live API. Does not clear the environment variable."""
        cls._pinned_dir = None

    @classmethod
    def pinned_source(cls):
        """
        The active pinned directory, or None if fetches go to the live API.

        Explicit set_pinned_source() wins; the environment variable is the
        fallback; otherwise live.
        """
        if cls._pinned_dir is not None:
            return cls._pinned_dir
        env = os.environ.get(PINNED_ENV_VAR)
        if env:
            resolved = os.path.abspath(env)
            if os.path.isdir(resolved):
                return resolved
        return None

    @staticmethod
    def pinned_filename(symbol, timeframe):
        """{SYMBOL}_{TIMEFRAME}.csv — symbol upper-cased, timeframe as given."""
        return f"{str(symbol).upper()}_{timeframe}.csv"

    def _load_pinned(self, directory, symbol, timeframe, limit):
        """
        Serve one series from the pinned directory.

        Returns a DataFrame shaped exactly as fetch_ohlc() returns one, or an
        {"error": ...} dict so get_tf()'s existing error path handles it
        unchanged.
        """
        path = os.path.join(directory, self.pinned_filename(symbol, timeframe))
        if not os.path.exists(path):
            return {"error": (
                f"pinned source active ({directory}) but no data for "
                f"{symbol} {timeframe} — expected "
                f"{self.pinned_filename(symbol, timeframe)}. Refusing to fall "
                f"back to the live API, which would make this run "
                f"irreproducible without saying so."
            )}

        try:
            df = self.load_csv(path, timeframe=timeframe)
        except Exception as e:
            return {"error": f"pinned data unreadable ({path}): {e}"}

        # SEQUENCE ITEM 8: checked here, before the reshape below. pandas does
        # not reliably carry .attrs through operations like the column
        # selection and astype that follow, so a later check could silently
        # find nothing wrong with a frame that is.
        #
        # No `now` is passed: a pinned file is historical by definition and
        # asserting it is current would reject the entire fixture set.
        problem = df.attrs.get("validation_error")
        if problem:
            return {"error": f"pinned data {path} failed validation: {problem}"}

        missing = [c for c in _OHLCV_COLUMNS if c not in df.columns]
        if missing:
            return {"error": (
                f"pinned data {path} is missing required columns: "
                f"{', '.join(missing)}"
            )}

        df = df[_OHLCV_COLUMNS].astype(float)

        # The API returns the most recent `limit` candles, so the pinned source
        # takes the tail to match. A pinned file shorter than `limit` is not an
        # error — it is simply all the history there is.
        if limit and len(df) > limit:
            df = df.iloc[-int(limit):]

        # A fresh copy per call. See the class docstring, choice 2.
        return df.copy()

    # ============================================================
    # LOCAL CSV LOADING
    # ============================================================

    def load_csv(self, filepath, timeframe=None, now=None):
        """
        Load OHLCV data from a CSV file.
        CSV must contain: timestamp, open, high, low, close, volume

        SEQUENCE ITEM 8: the loaded frame is validated against Item 3's defect
        classes, and any failure is recorded at `.attrs["validation_error"]`.

        Annotate rather than raise, for two reasons. The frame is still wanted
        by callers that want to look at what is wrong with it — the tests do
        exactly that. And every caller in the engine already has an error
        channel; _load_pinned turns this attribute into an {"error": ...} dict,
        get_tf turns that into .attrs["fetch_error"], and engine_core surfaces
        it. Raising here would mean unwinding all of that for no gain.

        The consequence to be aware of: an attribute is easy to ignore, and
        pandas does not reliably propagate .attrs through operations. Anything
        reading a frame from this method must check the attribute BEFORE
        reshaping it. _load_pinned does, immediately.

        `now` defaults to None, so a plain load makes no claim that the file is
        current and the staleness check does not run. See validation.py.
        """

        df = pd.read_csv(filepath)

        # Convert timestamp → datetime index
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            df.set_index("timestamp", inplace=True)

        problem = validate_ohlcv(df, timeframe=timeframe, now=now)
        if problem:
            df.attrs["validation_error"] = problem

        return df

    # ============================================================
    # MEXC API OHLC FETCHER
    # ============================================================

    def fetch_ohlc(self, symbol, timeframe, limit=300):
        """
        Fetch OHLCV candles from MEXC API.
        MEXC returns **8 fields**, not 12.
        """

        url = f"{self.base_url}/api/v3/klines"
        params = {
            "symbol": symbol,
            "interval": timeframe,
            "limit": limit
        }

        try:
            # AUDIT FINDING (c), 5 September 2026. This call had no timeout.
            # requests' default is None, which means wait forever: a server
            # that accepts the connection and then never answers hangs the run
            # indefinitely, with no error and no log line. See
            # config.API_TIMEOUT_SECONDS for the value and why it is not
            # fingerprinted.
            response = requests.get(url, params=params,
                                    timeout=config.API_TIMEOUT_SECONDS)
            response.raise_for_status()
            data = response.json()

        except Exception as e:
            return {"error": f"API request failed: {e}"}

        if not isinstance(data, list) or len(data) == 0:
            return {"error": "Empty or invalid API response."}

        # ============================================================
        # CORRECT MEXC FORMAT (8 fields)
        # ============================================================
        #
        # AUDIT FINDING (c), second half. Everything from here to
        # set_index used to sit OUTSIDE the try above, so the handler covered
        # only the network call. The shape check two lines up rejects a
        # response that is not a non-empty list, and nothing else.
        #
        # A response that IS a list and is wrong in any other way raised out of
        # this method uncaught: 8 columns declared against a different number
        # of fields (ValueError), a null where a price should be, a string
        # that is not a number (both from .astype(float)), a timestamp out of
        # range (pd.to_datetime). Every other failure in this class returns
        # {"error": ...}, which get_tf and the engine know how to report; these
        # ones escaped that contract and surfaced as an unhandled exception
        # attributed to whatever stage happened to be running.
        #
        # A malformed API response is a data defect, and data defects are
        # reported, not raised.
        try:
            df = pd.DataFrame(data, columns=[
                "timestamp",        # open time (ms)
                "open",
                "high",
                "low",
                "close",
                "volume",
                "close_time",       # close time (ms)
                "quote_volume"
            ])

            # Keep only OHLCV
            df = df[["timestamp", "open", "high", "low", "close", "volume"]]

            # Convert types
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            df["open"] = df["open"].astype(float)
            df["high"] = df["high"].astype(float)
            df["low"] = df["low"].astype(float)
            df["close"] = df["close"].astype(float)
            df["volume"] = df["volume"].astype(float)

            df.set_index("timestamp", inplace=True)

        except Exception as e:
            return {"error": (
                f"API response for {symbol} {timeframe} was correctly shaped "
                f"at the top level and malformed inside it: "
                f"{type(e).__name__}: {e}"
            )}

        # SEQUENCE ITEM 8: live data is validated too, and this is the one
        # path that DOES claim to be current — so it is the one that passes a
        # reference time and can therefore fail the staleness check.
        #
        # Item 3 lists "malformed API responses" alongside the data defects.
        # The shape checks above catch a response with the wrong number of
        # fields; this catches one that is correctly shaped and wrong, which is
        # the harder case and the one that reaches analysis.
        # MEXC timestamps are UTC epoch ms, so the reference must be UTC too.
        # Timestamp.now(tz="UTC") rather than the deprecated utcnow().
        problem = validate_ohlcv(df, timeframe=timeframe,
                                 now=pd.Timestamp.now(tz="UTC").tz_localize(None))
        if problem:
            return {"error": f"API data for {symbol} {timeframe} failed validation: {problem}"}

        return df

    # ============================================================
    # UNIFIED FETCH WRAPPER
    # ============================================================

    def get_tf(self, symbol, timeframe, limit=300):
        """
        Unified fetch wrapper used by the engine.

        A13 FIX: previously, any API failure silently returned an empty
        DataFrame with only a logger warning upstream — indistinguishable
        from a genuine "no signal" / insufficient-history condition once it
        reached engine_core.py. A real data outage would look identical to
        a normal HOLD in the panel, with no visibility into what actually
        happened.

        Now the failure reason is attached to the empty DataFrame via
        `.attrs["fetch_error"]` so engine_core.py can surface a distinct
        "data fetch failed" error state instead of the generic
        "insufficient market data" message. The return type is unchanged
        (still always a DataFrame) so nothing else calling get_tf() breaks.

        SEQUENCE ITEM 3: when a pinned source is active, data is served from
        disk instead of the API. The error handling below is shared — a
        missing pinned file surfaces through exactly the same
        `.attrs["fetch_error"]` path as an API failure, so engine_core needs
        no changes to report it.
        """

        pinned_dir = self.pinned_source()
        if pinned_dir:
            df = self._load_pinned(pinned_dir, symbol, timeframe, limit)
        else:
            df = self.fetch_ohlc(symbol, timeframe, limit)

        # If API returned an error dict, surface it as a distinct,
        # identifiable error state rather than falling through as an
        # ordinary empty-data path.
        if isinstance(df, dict) and "error" in df:
            empty_df = pd.DataFrame()
            empty_df.attrs["fetch_error"] = df["error"]
            return empty_df

        return df


# ============================================================
# GLOBAL FETCHER INSTANCE
# ============================================================

data_fetcher = DataFetcher()