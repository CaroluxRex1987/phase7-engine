"""
Findings 25, 26 and 28 (docs/PHASE7_NEXT.md, "Review findings", deferred
read of 21 September 2026) -- data/validation.py's time checks.

25. The staleness check bounded a series' age from above only. A last candle
    dated in the future was accepted as current.
26. The timeframe table was looked up lower-cased. MEXC's month "1M" was read
    as one minute, and MEXC's "60m" was not listed, which switched the spacing
    and staleness checks off for a 60m series.
28. An aware `now` was stripped of its zone without being converted to UTC,
    so a Stockholm wall-clock reading was taken as UTC. Found while fixing 25.

REWORKED 26 September 2026 for finding 16 (decisions on closed candles). A
frame validated against a `now` is a frame of CLOSED candles now: the fetcher
removes the candle still forming first. So a last candle that has not closed is
rejected here ("forming candle"), and the clock tolerance finding 25 gave a
candle opening seconds ahead is exercised where it now lives, in the fetcher's
drop (tests/test_closed_candles.py). The future-dated check itself is
unchanged. The finding-28 tests keep what they discriminate; their `now` moved
inside the one window a closed series is current in, since "2h30m after the
last 1h candle" is stale under the ruling.

Fixture-free on purpose: run_tests.py calls every test_* with no arguments.
Every frame here is built in memory; nothing reads or writes logs/.
"""

import pandas as pd

from data import validation
from data.validation import validate_ohlcv


def _series(timestamps):
    """A well-formed OHLCV frame on the given (naive UTC) open times."""
    idx = pd.DatetimeIndex(pd.to_datetime(timestamps))
    n = len(idx)
    return pd.DataFrame({
        "open": [100.0] * n, "high": [101.0] * n, "low": [99.0] * n,
        "close": [100.5] * n, "volume": [10.0] * n,
    }, index=idx)


def _regular(last, bars, freq):
    return _series(pd.date_range(end=last, periods=bars, freq=freq))


LAST = pd.Timestamp("2026-09-21 12:00:00")


# --- finding 25: a last candle in the future ---------------------------------

def test_a_last_candle_two_bars_in_the_future_is_rejected():
    df = _regular(LAST, 30, "4h")
    reason = validate_ohlcv(df, timeframe="4h", now=LAST - pd.Timedelta(hours=8))
    assert reason is not None and reason.startswith("future-dated data"), (
        f"a last candle two 4h bars after the reference time was not rejected "
        f"as future-dated; validate_ohlcv returned {reason!r}"
    )


def test_a_last_candle_seconds_ahead_of_the_clock_is_not_future_dated():
    """
    The tolerance's reason: two clocks disagree by seconds at a boundary. Such
    a candle is not future-dated. Since finding 16 it has not closed either,
    so it is rejected as a forming candle -- the fetcher drops it before
    validation (tests/test_closed_candles.py).
    """
    df = _regular(LAST, 30, "4h")
    reason = validate_ohlcv(df, timeframe="4h", now=LAST - pd.Timedelta(seconds=5))
    assert reason is not None and reason.startswith("forming candle"), reason


def test_a_last_candle_exactly_one_bar_ahead_is_the_future_dated_boundary():
    df = _regular(LAST, 30, "4h")
    reason = validate_ohlcv(df, timeframe="4h", now=LAST - pd.Timedelta(hours=4))
    assert reason is not None and not reason.startswith("future-dated data"), reason
    reason = validate_ohlcv(df, timeframe="4h",
                            now=LAST - pd.Timedelta(hours=4, seconds=1))
    assert reason is not None and reason.startswith("future-dated data"), reason


def test_a_forming_candle_is_rejected():
    """
    FINDING 16. This test used to be test_the_forming_candle_is_still_accepted:
    a last candle opened up to one bar BEFORE now passed as current. That was
    the finding -- the engine deciding on a candle still forming. Ruled 26
    September 2026: decisions are made on closed candles only, so the same
    frames are rejected now.
    """
    df = _regular(LAST, 30, "4h")
    for minutes in (0, 1, 120, 239):
        now = LAST + pd.Timedelta(minutes=minutes)
        reason = validate_ohlcv(df, timeframe="4h", now=now)
        assert reason is not None and reason.startswith("forming candle"), (
            minutes, reason)


# --- finding 28: an aware `now` is converted, not relabelled -----------------

def test_an_aware_now_is_read_as_the_instant_it_names():
    """
    Ten minutes after the last 1h candle closed, written as Stockholm local
    time (UTC+2 in September). Converted, the series is current. Relabelled,
    the wall clock reads 2h10m later and the series is called stale.
    (Before finding 16: 2h30m after the candle's open, inside the old
    three-bar limit.)
    """
    df = _regular(LAST, 30, "1h")
    now_utc = LAST + pd.Timedelta(hours=1, minutes=10)
    now_stockholm = now_utc.tz_localize("UTC").tz_convert("Europe/Stockholm")
    assert validate_ohlcv(df, timeframe="1h", now=now_utc) is None
    reason = validate_ohlcv(df, timeframe="1h", now=now_stockholm)
    assert reason is None, (
        f"the same instant, written in Stockholm time, gave a different "
        f"answer from naive UTC: {reason}"
    )


def test_an_aware_now_west_of_utc_does_not_make_a_current_series_future_dated():
    """
    The direction finding 25 made reachable: New York is UTC-4 in September,
    so a relabelled `now` sits four hours early and a current 1h series looks
    about three bars in the future. (Before finding 16 the instant was ten
    minutes after the last candle's open; it is ten minutes after its close
    now, since a series is current only once its last candle has closed.)
    """
    df = _regular(LAST, 30, "1h")
    now_ny = (LAST + pd.Timedelta(hours=1, minutes=10)).tz_localize("UTC").tz_convert(
        "America/New_York")
    reason = validate_ohlcv(df, timeframe="1h", now=now_ny)
    assert reason is None, reason


# --- finding 26: the timeframe table is case-sensitive -----------------------

def test_the_lookup_keeps_case():
    assert validation._interval_minutes("1m") == 1
    assert validation._interval_minutes("1M") is None, (
        "'1M' is MEXC's month; it must not be read as one minute"
    )
    assert validation._interval_minutes("60m") == 60
    assert validation._interval_minutes("1W") == 10080
    assert validation._interval_minutes("4h") == 240
    assert validation._interval_minutes("1d") == 1440


def test_a_monthly_series_is_not_checked_as_one_minute_bars():
    """Before the fix every monthly gap was 'irregular' against one minute."""
    months = pd.date_range("2024-01-01", periods=24, freq="MS")
    df = _series(months)
    assert validate_ohlcv(df, timeframe="1M") is None


def test_a_60m_series_with_a_missing_candle_is_rejected():
    """Before the fix '60m' was unknown and the gap went unseen."""
    ts = list(pd.date_range(end=LAST, periods=30, freq="1h"))
    del ts[10]
    reason = validate_ohlcv(_series(ts), timeframe="60m")
    assert reason is not None and "irregular interval" in reason, reason


def test_a_60m_series_is_checked_for_staleness():
    df = _regular(LAST, 30, "1h")
    reason = validate_ohlcv(df, timeframe="60m", now=LAST + pd.Timedelta(hours=5))
    assert reason is not None and reason.startswith("stale data"), reason


def test_a_1W_series_with_a_missing_candle_is_rejected():
    ts = list(pd.date_range(end=LAST, periods=30, freq="7D"))
    del ts[5]
    reason = validate_ohlcv(_series(ts), timeframe="1W")
    assert reason is not None and "irregular interval" in reason, reason
