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


def test_a_last_candle_seconds_ahead_of_the_clock_is_accepted():
    """The tolerance's reason: two clocks disagree by seconds at a boundary."""
    df = _regular(LAST, 30, "4h")
    reason = validate_ohlcv(df, timeframe="4h", now=LAST - pd.Timedelta(seconds=5))
    assert reason is None, f"a candle 5 s ahead of the clock was rejected: {reason}"


def test_a_last_candle_exactly_one_bar_ahead_is_the_boundary_and_is_accepted():
    df = _regular(LAST, 30, "4h")
    assert validate_ohlcv(df, timeframe="4h", now=LAST - pd.Timedelta(hours=4)) is None
    reason = validate_ohlcv(df, timeframe="4h",
                            now=LAST - pd.Timedelta(hours=4, seconds=1))
    assert reason is not None and reason.startswith("future-dated data"), reason


def test_the_forming_candle_is_still_accepted():
    """
    A live fetch's last row is the candle still forming (finding 16): its open
    time is up to one bar BEFORE now. That is a positive age, and finding 25
    must not touch it.
    """
    df = _regular(LAST, 30, "4h")
    for minutes in (0, 1, 120, 239):
        now = LAST + pd.Timedelta(minutes=minutes)
        assert validate_ohlcv(df, timeframe="4h", now=now) is None, minutes


# --- finding 28: an aware `now` is converted, not relabelled -----------------

def test_an_aware_now_is_read_as_the_instant_it_names():
    """
    2h30m after the last 1h candle, written as Stockholm local time (UTC+2 in
    September). Converted, the age is 2h30m, inside the three-bar limit.
    Relabelled, the wall clock reads 4h30m and the series is called stale.
    """
    df = _regular(LAST, 30, "1h")
    now_utc = LAST + pd.Timedelta(hours=2, minutes=30)
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
    four bars in the future.
    """
    df = _regular(LAST, 30, "1h")
    now_ny = (LAST + pd.Timedelta(minutes=10)).tz_localize("UTC").tz_convert(
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
