"""
Item 3 — Data Integrity. Sequence item 8, the first Critical.

The invariant names its defect classes by hand:

    "Missing candles, duplicated candles, impossible prices, timestamp
     inconsistencies, NaN/Inf values, stale data, malformed API responses,
     and abnormal volume must be detected before they become analysis."

Before this module, nothing detected any of the first six. What existed instead
was ffill/bfill, which fills the defect in and carries on — so the engine could
not distinguish "no defect found" from "defect fabricated away". Every one of
the eight test_data_integrity fixtures was accepted without complaint.

REJECT, NOT DEGRADE — AND WHY THAT IS NOT A CONTRADICTION

Viktor's ruling of 29 August says that when an INDICATOR fails, the engine
continues in an explicitly degraded state rather than halting. That ruling
governs sequence item 9 and it is not in tension with this module.

The difference is what is being salvaged. A failed indicator leaves the rest of
the analysis standing: bias, structure and volume are still real measurements,
and a decision built on fewer of them can be reported honestly as such. A
negative price is not a measurement at all. There is no partial analysis of
impossible data to degrade to, and "degrading" would mean deciding which
fabricated number to substitute — the exact behaviour Item 3 exists to stop.

So: defective input is rejected before analysis. Defective analysis, once the
input is sound, is item 9's problem.

STALENESS TAKES AN EXPLICIT REFERENCE TIME

`now` is a parameter, and when it is omitted the staleness check does not run.

A CSV on disk is not stale — it is historical. What would be stale is treating
it as current. So the module refuses to guess: fetch_ohlc passes the wall clock,
because a live feed that claims to be current must be, and a file load asserts
every other invariant while making no currency claim.

This is also the only rule that could be satisfied durably. The clean fixture
this suite validates against spans 2025-01-01 to 2025-03-16 — 531 days old as of
30 August 2026 — and the corrupted "stale" fixture is the same data shifted back
another 730 days. A wall-clock threshold separating them has to sit between 531
and 1261 days, and the clean fixture's age grows by one every day. Any constant
chosen there is a magic number with an expiry date.

Ruled by Viktor, 30 August 2026.

ITEM 3 RE-AUDIT (Finding 1): ABNORMAL VOLUME, RULED

The independent audit found this module's volume check checks only
non-negativity, and named four cases to distinguish: negative, all-zero /
unusable, isolated extreme spikes, and non-finite. Ruled by Viktor, 31 August
2026, having delegated the ruling itself:

  negative       already rejected below (unchanged).
  non-finite     already rejected — NaN/Inf in 'volume' is caught by the
                 OHLCV loop above, since "volume" is one of the five columns
                 it walks. The audit read this module's comment ("checks only
                 that volume is finite and non-negative") and took it as a
                 complete list of what runs; it undersold its own coverage.
  all-zero       REJECTED, new below. A series where every candle reports
                 zero volume is not a quiet market — a quiet market still
                 trades something — it is an absent measurement wearing the
                 shape of one, and indicators/indicators.py's VWMA calculation
                 (and structure.py's volume-weighted reads) cannot compute
                 anything real from it. There is no partial analysis to
                 salvage, which is this module's existing rule for
                 no-measurement-at-all cases (see REJECT, NOT DEGRADE above).
  isolated spike DELIBERATELY LEFT TO indicators.py, not rejected here — see
                 below. This is the one case that stays out of this file.

**Isolated extreme spikes are not validation's job, and remain accepted here.**
The reasoning below predates the re-audit and still holds: a spike is real
market data, frequently the most informative bar in the series, and rejecting
a run because the market got busy would make the engine least available
exactly when it matters. Detecting "abnormal" requires a model of normal,
which is analysis, not validation.

What changed is that "accepted here" no longer means "reaches every downstream
calculation unflagged." indicators.add_technical_indicators() now detects an
isolated spike (a candle far above the recent rolling volume) and records it
as a degradation — Viktor's standing rule that a failed or suspect input
degrades the run rather than halting it, and that a degraded run does not by
itself authorize a trade. The spike's real value is never altered or
substituted; only the operator's confidence in the result is capped. See
indicators/indicators.py for the detection and core/engine_core.py's
`degradation` list for where it surfaces. This module still rejects nothing
over a spike — Item 3's "reject or degrade" is satisfied one layer down.

**Row count.** engine_core._validate_dataframe already requires 20 rows and
reports its own message. Duplicating it here would mean two thresholds to keep
in agreement.
"""

import math

import numpy as np
import pandas as pd

OHLCV = ["open", "high", "low", "close", "volume"]

# How many bars past the last candle before a series claiming to be current is
# not. Three is deliberately loose: an exchange can be a bar behind at a
# boundary, and a validator that cries wolf on a routine lag gets disabled.
STALE_AFTER_BARS = 3

# Minutes per candle, for the interval and staleness checks. Anything not
# listed here is not validated for spacing rather than guessed at — see
# _interval_minutes.
TIMEFRAME_MINUTES = {
    "1m": 1, "3m": 3, "5m": 5, "15m": 15, "30m": 30,
    "1h": 60, "2h": 120, "4h": 240, "6h": 360, "8h": 480, "12h": 720,
    "1d": 1440, "3d": 4320, "1w": 10080,
}


def _interval_minutes(timeframe):
    """None when the timeframe is unknown, which disables spacing checks."""
    if not timeframe:
        return None
    return TIMEFRAME_MINUTES.get(str(timeframe).lower())


def _timestamps(df):
    """
    The series' time axis, whichever form it is in.

    load_csv sets a DatetimeIndex; fetch_ohlc does too; a frame read straight
    from disk has a `timestamp` column of epoch milliseconds. All three reach
    this module, so all three are handled rather than one being assumed.
    """
    if isinstance(df.index, pd.DatetimeIndex):
        return pd.Series(df.index)
    if "timestamp" in df.columns:
        col = df["timestamp"]
        if pd.api.types.is_datetime64_any_dtype(col):
            return pd.Series(col.to_numpy())
        try:
            return pd.Series(pd.to_datetime(col, unit="ms"))
        except Exception:
            return None
    return None


def validate_ohlcv(df, timeframe=None, now=None):
    """
    Return a one-line reason the frame must not become analysis, or None.

    A string rather than an exception: every caller here already has an error
    channel — _load_pinned returns {"error": ...}, get_tf converts that to
    .attrs["fetch_error"], and engine_core surfaces it as a distinct failure
    state. Raising would mean unwinding all of that.

    Args:
        df:         the frame to check
        timeframe:  e.g. "4h". Enables the spacing and staleness checks;
                    without it, both are skipped rather than guessed.
        now:        reference time for staleness. Omitted means the caller
                    makes no claim that this data is current, and the check
                    does not run. See the module docstring.
    """
    if df is None:
        return "no data: the frame is None"
    if not isinstance(df, pd.DataFrame):
        return f"malformed data: expected a DataFrame, got {type(df).__name__}"
    if df.empty:
        return "no data: the frame is empty"

    missing = [c for c in OHLCV if c not in df.columns]
    if missing:
        return f"malformed data: missing required columns {', '.join(missing)}"

    # --- values must be numbers, and real ones ---------------------------
    for col in OHLCV:
        series = pd.to_numeric(df[col], errors="coerce")

        n_nan = int(series.isna().sum())
        if n_nan:
            first = df.index[series.isna().to_numpy().argmax()]
            return (f"{n_nan} NaN or non-numeric value(s) in '{col}', first at "
                    f"{first}. Filling these would make a fabricated value "
                    f"indistinguishable from a measurement.")

        n_inf = int(np.isinf(series.to_numpy()).sum())
        if n_inf:
            return f"{n_inf} infinite value(s) in '{col}'"

    prices = df[["open", "high", "low", "close"]].apply(pd.to_numeric, errors="coerce")
    volume = pd.to_numeric(df["volume"], errors="coerce")

    nonpositive = (prices <= 0).to_numpy().sum()
    if nonpositive:
        col = prices.columns[(prices <= 0).any().to_numpy().argmax()]
        worst = float(prices[col].min())
        return (f"{int(nonpositive)} non-positive price(s); lowest is "
                f"{worst} in '{col}'. A price of zero or less is not a "
                f"measurement error, it is not a price.")

    if (volume < 0).any():
        return f"negative volume; lowest is {float(volume.min())}"

    # ITEM 3 RE-AUDIT (Finding 1): all-zero volume is a missing measurement,
    # not a quiet market — see the module docstring. `volume` here has already
    # passed the NaN/Inf checks above, so a series that is all zero really
    # reported zero on every candle rather than failing to parse.
    if len(volume) and (volume == 0).all():
        return ("all volume values are zero; there is no genuine volume "
                "measurement in this series. VWMA and every volume-weighted "
                "read downstream would be computed from an absence, not a "
                "quiet market.")

    # --- candles must be internally possible -----------------------------
    #
    # Three ways a candle can be impossible, not one. high < low is the obvious
    # case; a high below the open or close, or a low above them, is the same
    # defect wearing a different shape and would survive a check that only
    # compared high against low.
    body_max = prices[["open", "close"]].max(axis=1)
    body_min = prices[["open", "close"]].min(axis=1)
    impossible = (prices["high"] < prices["low"]) | \
                 (prices["high"] < body_max) | \
                 (prices["low"] > body_min)
    n_bad = int(impossible.sum())
    if n_bad:
        i = int(impossible.to_numpy().argmax())
        row = prices.iloc[i]
        return (f"{n_bad} impossible candle(s); first at index {i}: "
                f"open={row['open']}, high={row['high']}, low={row['low']}, "
                f"close={row['close']}. The high must be the highest of the "
                f"four and the low the lowest.")

    # --- the time axis ---------------------------------------------------
    ts = _timestamps(df)
    if ts is None:
        # No time axis at all. Not an error by itself — some callers hand over
        # a positionally-indexed frame — but nothing below can be checked.
        return None

    n_dupes = int(ts.duplicated().sum())
    if n_dupes:
        first = ts[ts.duplicated(keep=False)].iloc[0]
        return (f"{n_dupes} duplicated timestamp(s), first at {first}. "
                f"A repeated candle double-counts one bar of history in every "
                f"rolling window that crosses it.")

    if not ts.is_monotonic_increasing:
        i = int((ts.diff() < pd.Timedelta(0)).to_numpy().argmax())
        return (f"timestamps are not in increasing order; index {i} "
                f"({ts.iloc[i]}) is earlier than the row before it. Every "
                f"indicator here assumes time runs forwards.")

    minutes = _interval_minutes(timeframe)
    if minutes is None:
        return None                       # spacing and staleness need the bar size

    expected = pd.Timedelta(minutes=minutes)

    if len(ts) > 1:
        gaps = ts.diff().dropna()
        wrong = gaps[gaps != expected]
        if len(wrong):
            i = int(gaps.to_numpy().__ne__(expected.to_timedelta64()).argmax()) + 1
            return (f"{len(wrong)} irregular interval(s) for a {timeframe} "
                    f"series; first at index {i}, gap of {wrong.iloc[0]} where "
                    f"{expected} was expected. A missing candle silently "
                    f"shortens every rolling window that spans it.")

    # --- currency, only if the caller claims it --------------------------
    if now is not None:
        now_ts = pd.Timestamp(now)
        if now_ts.tzinfo is not None:
            now_ts = now_ts.tz_localize(None)
        age = now_ts - ts.iloc[-1]
        limit = expected * STALE_AFTER_BARS
        if age > limit:
            return (f"stale data: the last candle is {ts.iloc[-1]}, which is "
                    f"{age} old against a {timeframe} bar. The engine would "
                    f"analyse it and present the result with no indication "
                    f"that the market has moved since.")

    return None


def is_valid(df, timeframe=None, now=None):
    """Convenience wrapper for callers that want a boolean."""
    return validate_ohlcv(df, timeframe=timeframe, now=now) is None
