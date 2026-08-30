"""
Item 3 — Data Integrity. Rated Critical. Fixed at sequence item 8.

The invariant names the defect classes by hand: "Missing candles, duplicated
candles, impossible prices, timestamp inconsistencies, NaN/Inf values, stale
data, malformed API responses, and abnormal volume must be detected before
they become analysis."

Nothing detected any of the first six. What existed instead was ffill/bfill,
which fills the defect in and carries on, so the engine could not distinguish
"no defect found" from "defect fabricated away."

THESE TESTS WERE WRITTEN TO FAIL, ON PURPOSE, AND NOW PASS. They were the
acceptance criteria for the fix; they are the regression guard after it. What
changed on 30 August is `_validate` below and nothing else — the corruption
each test introduces, and the assertion each makes, are as originally written.

Each corrupted fixture is a copy of the clean pinned dataset with exactly one
defect introduced, so a failure names one cause rather than a combination.
"""

import os
import tempfile

import pandas as pd

from conftest import fixture

CLEAN = "ohlcv_clean_4h.csv"

# The fixture is a 4h series. Passing this is what enables the interval and
# staleness checks; without it validate_ohlcv skips both rather than guessing
# the bar size.
TIMEFRAME = "4h"


def _load(name=CLEAN):
    return pd.read_csv(fixture(name))


def _write(df, tmpdir, name="corrupt.csv"):
    path = os.path.join(tmpdir, name)
    df.to_csv(path, index=False)
    return path


def _validate(path, now=None):
    """
    Ask the engine to accept or reject a CSV.

    v1 of this helper called the loader and reported what came back, because
    there was no validation entry point. Its docstring said: "When Item 3 is
    fixed, point this at the real validator; the tests themselves should not
    need changing."

    That is what happened. load_csv now records any Item 3 defect at
    .attrs["validation_error"], and this reads it. The bodies of the eight
    tests below are untouched.

    `now` is passed through. See test_rejects_stale_data for why staleness is
    the one check that needs it.
    """
    from data.data_fetcher import DataFetcher
    df = DataFetcher().load_csv(path, timeframe=TIMEFRAME, now=now)
    if isinstance(df, dict) and "error" in df:
        return False, df["error"]
    if hasattr(df, "attrs") and df.attrs.get("validation_error"):
        return False, df.attrs["validation_error"]
    return True, None


def _assert_rejected(path, defect, now=None):
    accepted, reason = _validate(path, now=now)
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

    STALENESS IS THE ONE CHECK THAT NEEDS A REFERENCE TIME, and this test is
    where that shows.

    The clean fixture spans 2025-01-01 to 2025-03-16. As of 30 August 2026 its
    last candle is 531 days old; this test's corruption shifts it back another
    730, to 1261. A wall-clock threshold separating "clean" from "stale" would
    have to sit between those two numbers — and the clean fixture's age grows
    by one every day, so any constant chosen there expires.

    So validate_ohlcv takes `now` as a parameter and skips the check when it is
    omitted. A CSV on disk is not stale; it is historical. What would be stale
    is treating it as current, and only a caller knows whether it is doing
    that. fetch_ohlc passes the wall clock, because a live feed claiming to be
    current must be. This test passes a `now` anchored to the CLEAN fixture's
    own end, which makes the assertion durable: the clean data is current
    relative to that instant and the shifted data is two years behind it,
    forever, regardless of when the suite is run.

    Ruled by Viktor, 30 August 2026.
    """
    clean = _load()
    reference = pd.to_datetime(clean["timestamp"].iloc[-1], unit="ms")

    df = _load()
    df["timestamp"] = df["timestamp"] - (730 * 24 * 60 * 60 * 1000)
    with tempfile.TemporaryDirectory() as tmp:
        _assert_rejected(_write(df, tmp),
                         "stale data (last candle two years old)",
                         now=reference)


def test_clean_data_is_current_against_its_own_end():
    """
    The other half of the staleness rule, and the guard against the cheap way
    to pass the test above.

    A staleness check that rejected everything would satisfy
    test_rejects_stale_data perfectly. This is what stops that: the same clean
    fixture, measured against the same instant its own last candle sits at,
    must be accepted.

    Together the two pin the rule rather than one direction of it.
    """
    clean = _load()
    reference = pd.to_datetime(clean["timestamp"].iloc[-1], unit="ms")

    accepted, reason = _validate(fixture(CLEAN), now=reference)
    assert accepted, (
        f"the clean fixture was rejected when measured against its own last "
        f"candle: {reason}\n"
        "The staleness rule allows the most recent bar to be up to "
        "STALE_AFTER_BARS old. Data whose newest candle IS the reference "
        "instant is as current as data can be."
    )


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


def test_each_defect_is_reported_by_its_own_name():
    """
    Detection is not enough; Item 3 says defects must be DETECTED, and a
    detector that reports every defect as "invalid data" has detected that
    something is wrong, not what.

    This matters for the same reason the A13 fix mattered: an engine that
    cannot distinguish a data outage from a quiet market will present both
    identically. A validator that cannot distinguish a duplicated candle from
    a negative price sends whoever is debugging it to read all 450 rows.

    Each corruption must produce a message naming its own defect class.
    """
    df = _load()
    cases = []

    d = df.copy(); d = d.drop(index=200).reset_index(drop=True)
    cases.append((d, ("interval", "gap"), "missing candle"))

    d = df.copy(); dup = d.iloc[[150]].copy()
    d = pd.concat([d.iloc[:151], dup, d.iloc[151:]]).reset_index(drop=True)
    cases.append((d, ("duplicat",), "duplicated candle"))

    d = df.copy(); d.loc[300, "high"] = d.loc[300, "low"] * 0.5
    cases.append((d, ("impossible",), "impossible candle"))

    d = df.copy(); d.loc[120, "close"] = -1.0
    cases.append((d, ("non-positive",), "negative price"))

    d = df.copy(); d.loc[77, "volume"] = -5000.0
    cases.append((d, ("negative volume",), "negative volume"))

    d = df.copy(); d.loc[250, "close"] = float("nan")
    cases.append((d, ("nan",), "NaN"))

    d = df.copy(); a, b = d.loc[100].copy(), d.loc[101].copy()
    d.loc[100], d.loc[101] = b, a
    cases.append((d, ("increasing order", "not in increasing"), "out-of-order timestamps"))

    vague = []
    with tempfile.TemporaryDirectory() as tmp:
        for i, (frame, needles, label) in enumerate(cases):
            _, reason = _validate(_write(frame, tmp, f"c{i}.csv"))
            text = (reason or "").lower()
            if not any(n.lower() in text for n in needles):
                vague.append(f"{label}: reported as {reason!r}")

    assert not vague, (
        "defects were detected but not named:\n  " + "\n  ".join(vague)
        + "\n\nA message that says only 'invalid data' tells whoever is "
          "debugging it to go and read 450 rows."
    )
