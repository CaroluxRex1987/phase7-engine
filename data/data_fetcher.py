import os

import pandas as pd
import requests
import time
from core import config

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
       callers is unsafe in this codebase specifically: calculate_dynamic_bias
       rewrites its caller's columns in place (T2-1, open). A fresh copy per
       call means that bug cannot corrupt the pinned dataset mid-run.

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
            df = self.load_csv(path)
        except Exception as e:
            return {"error": f"pinned data unreadable ({path}): {e}"}

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

    def load_csv(self, filepath):
        """
        Load OHLCV data from a CSV file.
        CSV must contain: timestamp, open, high, low, close, volume
        """

        df = pd.read_csv(filepath)

        # Convert timestamp → datetime index
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            df.set_index("timestamp", inplace=True)

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
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        except Exception as e:
            return {"error": f"API request failed: {e}"}

        if not isinstance(data, list) or len(data) == 0:
            return {"error": "Empty or invalid API response."}

        # ============================================================
        # CORRECT MEXC FORMAT (8 fields)
        # ============================================================

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