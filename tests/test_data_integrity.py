"""
Item 3 — Data Integrity. Currently Non-compliant, rated Critical.

The invariant names the defect classes by hand: "Missing candles, duplicated
candles, impossible prices, timestamp inconsistencies, NaN/Inf values, stale
data, malformed API responses, and abnormal volume must be detected before
they become analysis."

Nothing detects any of the first six. What exists instead is ffill/bfill,
which fills the defect in and carries on, so the engine cannot distinguish
"no defect found" from "defect fabricated away."

EVERY TEST IN THIS FILE IS EXPECTED TO FAIL TODAY. That is the point. They
are written against the behaviour Item 3 requires, not the behaviour the
engine has, so they become the acceptance criteria for the fix and the
regression guard afterwards.

Each corrupted fixture is a copy of the clean pinned dataset with exactly one
defect introduced, so a failure names one cause rather than a combination.
"""

import os
import shutil
import tempfile

import pandas as pd

from conftest import fixture

CLEAN = "ohlcv_clean_4h.csv"


def _load(name=CLEAN):
    return pd.read_csv(fixture(name))


def _write(df, tmpdir, name="corrupt.csv"):
    path = os.path.join(tmpdir, name)
    df.to_csv(path, index=False)
    return path


def _validate(path):
    """
    Ask the engine to accept or reject a CSV.

    There is no validation entry point today, so this calls the loader and
    reports what came back. When Item 3 is fixed, point this at the real
    validator; the tests themselves should not need changing.
    """
    from data.data_fetcher import DataFetcher
    df = DataFetcher().load_csv(path)
    if isinstance(df, dict) and "error" in df:
        return False, df["error"]
    if hasattr(df, "attrs") and df.attrs.get("validation_error"):
        return False, df.attrs["validation_error"]
    return True, None


def _assert_rejected(path, defect):
    accepted, reason = _validate(path)
    assert not accepted, (
        f"{defect} was accepted without complaint.\n"
        "Item 3 requires this to be detected before it becomes analysis. "
        "Nothing currently detects it, so the corrupted values flow into "
        "EMA/RSI/ATR, then bias, entry quality, risk validation and the "
        "final decision."
    )


def test_rejects_a_missing_candle():
    """A four-hour gap in an otherwise continuous series."""
    df = _load()
    df = df.drop(index=200).reset_index(drop=True)
    with tempfile.TemporaryDirectory() as tmp:
        _assert_rejected(_write(df, tmp), "a missing candle (gap in the timestamp series)")


def test_rejects_a_duplicated_candle():
    """The same timestamp appearing twice."""
    df = _load()
    dup = df.iloc[[150]].copy()
    df = pd.concat([df.iloc[:151], dup, df.iloc[151:]]).reset_index(drop=True)
    with tempfile.TemporaryDirectory() as tmp:
        _assert_rejected(_write(df, tmp), "a duplicated candle")


def test_rejects_impossible_prices():
    """A candle whose high is below its low."""
    df = _load()
    df.loc[300, "high"] = df.loc[300, "low"] * 0.5
    with tempfile.TemporaryDirectory() as tmp:
        _assert_rejected(_write(df, tmp), "an impossible price (high below low)")


def test_rejects_negative_price():
    df = _load()
    df.loc[120, "close"] = -1.0
    with tempfile.TemporaryDirectory() as tmp:
        _assert_rejected(_write(df, tmp), "a negative close price")


def test_rejects_out_of_order_timestamps():
    """Two adjacent candles swapped, so the index is no longer monotonic."""
    df = _load()
    a, b = df.loc[100].copy(), df.loc[101].copy()
    df.loc[100], df.loc[101] = b, a
    with tempfile.TemporaryDirectory() as tmp:
        _assert_rejected(_write(df, tmp), "out-of-order timestamps")


def test_rejects_negative_volume():
    df = _load()
    df.loc[77, "volume"] = -5000.0
    with tempfile.TemporaryDirectory() as tmp:
        _assert_rejected(_write(df, tmp), "negative volume")


def test_rejects_stale_data():
    """
    Every candle is real and well formed, but the series ends two years ago.

    Nothing compares the last candle's age against the timeframe, so the
    engine will analyse a two-year-old snapshot and present the result with
    no indication that the data is not current.
    """
    df = _load()
    df["timestamp"] = df["timestamp"] - (730 * 24 * 60 * 60 * 1000)
    with tempfile.TemporaryDirectory() as tmp:
        _assert_rejected(_write(df, tmp), "stale data (last candle two years old)")


def test_rejects_nan_in_close():
    """
    A NaN close price. This one is arguably worse than the others because
    the engine does not ignore it — indicators.py fills it in from a
    neighbouring bar and the fabricated value is then indistinguishable
    from a measurement.
    """
    df = _load()
    df.loc[250, "close"] = float("nan")
    with tempfile.TemporaryDirectory() as tmp:
        _assert_rejected(_write(df, tmp), "a NaN close price")


def test_accepts_clean_data():
    """
    The control. A validator that rejects everything is not a validator, so
    this must pass both before and after the fix.
    """
    accepted, reason = _validate(fixture(CLEAN))
    assert accepted, f"the clean pinned dataset was rejected: {reason}"
