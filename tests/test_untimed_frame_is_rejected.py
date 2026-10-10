"""
Round 8's F3 -- a frame with no readable time axis is rejected, not passed.

Viktor's ruling of 5 October 2026, point 8 (docs/PHASE7_DECISIONS.md, "Ruling,
5 October 2026 -- round 8 triaged ..."): the label and record fixes are made
now, and round 8's F3 is one of them.

WHAT WAS WRONG

data/validation.py's validate_ohlcv returned None -- accepted -- for a frame
with neither a DatetimeIndex nor a `timestamp` column, and for a `timestamp`
column it could not read. Every check on the time axis sat behind that early
return: missing candles, duplicates, order, spacing, future-dated, forming and
stale data. _load_pinned never asks for a `timestamp` column either, so a
pinned file with that column removed passed validation as clean data.

Round 8's auditor said the engine then produced a full panel and a decision
record whose decision candle was a row number. Run on 10 October 2026, on this
tip and on the package commit `e186423` (Linux sandbox, Python 3.12.3), that
part is not what happens: the run gets past validation and the indicators and
crashes in Phase7Engine._decision_candle (`int + Timedelta`), so it ends in the
pipeline's generic "Critical error" with no record written. The gap in the
validator is real; the refusal was an accident one frame further on, with an
error that names neither the file nor the defect.

WHAT THE FIX DOES

validate_ohlcv rejects a frame with no time axis, one whose `timestamp` column
cannot be read as epoch milliseconds, and one with a missing timestamp (NaT),
each with its own reason. The last was already rejected, as "not in increasing
order" at index 0, which named the wrong defect.

No pytest fixtures anywhere in this file: run_tests.py calls every test_*
function with no arguments, so a fixture parameter would become an error
there and move its watched count.
"""

import glob
import os
import shutil
import tempfile

import numpy as np
import pandas as pd
import pytest

from data.validation import validate_ohlcv


PINNED_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "fixtures", "pinned")
SYMBOL = "AEROUSDT"
TIMEFRAME = "4h"
FILENAME = f"{SYMBOL}_{TIMEFRAME}.csv"
# A port nothing listens on: a fetch that escapes the pinned source fails at
# the socket instead of reaching an exchange.
UNREACHABLE = "http://127.0.0.1:1"


def _raw():
    """The committed fixture as read from disk: a `timestamp` column of epoch ms."""
    return pd.read_csv(os.path.join(PINNED_DIR, FILENAME))


def _engine_available():
    try:
        import pandas_ta  # noqa: F401
        return True
    except Exception:
        return False


def _untimed_copy():
    """A temporary copy of the pinned directory with the 4h file's time column gone."""
    tmp = tempfile.mkdtemp(prefix="phase7_f3_")
    pinned = os.path.join(tmp, "pinned")
    shutil.copytree(PINNED_DIR, pinned)
    path = os.path.join(pinned, FILENAME)
    _raw().drop(columns=["timestamp"]).to_csv(path, index=False)
    return tmp, pinned


def test_the_clean_series_is_accepted_in_both_forms():
    """
    The control. The same candles pass with their time as a column and as a
    DatetimeIndex, so the tests below fail on the time axis and nothing else.
    """
    raw = _raw()
    assert validate_ohlcv(raw, timeframe=TIMEFRAME) is None

    indexed = raw.copy()
    indexed["timestamp"] = pd.to_datetime(indexed["timestamp"], unit="ms")
    indexed = indexed.set_index("timestamp")
    assert validate_ohlcv(indexed, timeframe=TIMEFRAME) is None


def test_a_frame_with_no_time_axis_is_rejected():
    untimed = _raw().drop(columns=["timestamp"])
    assert not isinstance(untimed.index, pd.DatetimeIndex)

    reason = validate_ohlcv(untimed, timeframe=TIMEFRAME)
    assert reason is not None, (
        "a frame with no time axis was accepted, so every time check was "
        "skipped (round 8, F3)"
    )
    assert reason.startswith("no time axis"), reason


def test_an_unreadable_timestamp_column_is_rejected():
    garbled = _raw()
    garbled["timestamp"] = "not a time"

    reason = validate_ohlcv(garbled, timeframe=TIMEFRAME)
    assert reason is not None, (
        "a `timestamp` column that cannot be read was accepted as if the "
        "frame had no time axis to check"
    )
    assert reason.startswith("unreadable time axis"), reason


def test_a_missing_timestamp_is_named_as_missing():
    holed = _raw()
    holed["timestamp"] = holed["timestamp"].astype(float)
    holed.loc[holed.index[5], "timestamp"] = np.nan

    reason = validate_ohlcv(holed, timeframe=TIMEFRAME)
    assert reason is not None
    assert reason.startswith("1 missing timestamp(s), first at index 5"), reason


def test_the_pinned_loader_refuses_an_untimed_file():
    from data.data_fetcher import DataFetcher

    tmp, pinned = _untimed_copy()
    try:
        out = DataFetcher()._load_pinned(pinned, SYMBOL, TIMEFRAME, 300)
        assert isinstance(out, dict) and "error" in out, (
            "the pinned loader served an untimed file as clean data"
        )
        assert "no time axis" in out["error"], out["error"]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_an_untimed_pinned_run_is_refused_at_the_fetch():
    """
    The auditor's reproduction, end to end: the run stops at the fetch with the
    validator's reason, and writes nothing under the log directory. Before the
    fix it stopped one frame later, in _decision_candle, with a TypeError.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    from core import config
    from data.data_fetcher import DataFetcher, data_fetcher
    from models.signal_router import SignalRouter

    tmp, pinned = _untimed_copy()
    log_dir = os.path.join(tmp, "logs")
    original_url = data_fetcher.base_url
    original_log, original_chart = config.LOG_DIR, config.CHART_DIR
    try:
        data_fetcher.base_url = UNREACHABLE
        config.LOG_DIR = log_dir
        config.CHART_DIR = os.path.join(tmp, "charts")
        DataFetcher.set_pinned_source(pinned)
        result = SignalRouter().route(symbol=SYMBOL, timeframe=TIMEFRAME)
    finally:
        DataFetcher.clear_pinned_source()
        data_fetcher.base_url = original_url
        config.LOG_DIR, config.CHART_DIR = original_log, original_chart

    try:
        error = result.get("error") if isinstance(result, dict) else None
        assert error, f"an untimed pinned run returned no error: {result!r}"
        assert error.startswith("Data fetch failed"), error
        assert "no time axis" in error, error
        written = [p for p in glob.glob(os.path.join(log_dir, "**", "*"),
                                        recursive=True) if os.path.isfile(p)]
        assert written == [], f"a refused run wrote records: {written}"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
