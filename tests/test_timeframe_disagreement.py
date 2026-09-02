"""
The state the fixtures could not reach.

WHY THIS FILE EXISTS

On 2 September 2026 the engine printed CONSERVATIVE LONG over a stop above
price and three descending targets: a long label on a short plan. The cause was
that three sources could each open a direction, and a bullish macro read alone
was enough to override a bias that was bearish on every other measure.

It survived an independent 44-rule audit and four earlier review passes across
three models, all of which read the source and the tests. It was found by
Viktor running `python main.py` against live data.

The reason nothing caught it is not subtle and is worth stating exactly: **no
pinned fixture makes bias and macro disagree.** The committed series trends one
way, and its daily aggregate trends the same way, because the aggregate is
built from it. A suite cannot reach a state its fixtures never enter, so a
hundred and seventy tests could pass over a defect that only exists in that
state.

tests/test_direction_source.py pins the rule at the unit level, calling
DecisionModel with hand-built dicts. That is necessary and not sufficient: it
proves the function behaves, and it would keep passing if some future change
routed around the function, or if a fourth direction source appeared upstream.
This file runs the WHOLE engine -- fetch, indicators, structure, trend, bias,
entry, risk, decision, router -- on data that genuinely disagrees across
timeframes, and asserts the property an operator actually depends on.

WHY THE DATA IS GENERATED RATHER THAN COMMITTED

Same discipline as test_golden_path._write_pinned_set: one source of truth, a
pure function of it, byte-identical on every machine. No RNG -- the wobble is
sin(), so the series is the same on every numpy that has ever shipped. A
committed CSV would be a second thing to keep in step with the reason it
exists, and nobody reading it later could tell what it was for.

The shape is an ordinary market condition, not a contrivance: a long rally
followed by a sharp multi-day break. The daily EMA-50 lags, so the daily close
is still above it while the 4h structure has decisively turned. That is a real
disagreement, of the kind that happens most weeks.
"""

import math
import os
import shutil
import tempfile

import pytest


UNREACHABLE = "http://127.0.0.1:1"
SYMBOL = "AEROUSDT"
TIMEFRAME = "4h"
MACRO_TIMEFRAME = "1d"


def _engine_available():
    try:
        import pandas_ta  # noqa: F401
        return True
    except Exception:
        return False


# ============================================================
# The series
# ============================================================

def _series(rows, turn_at, start, peak, move, rising_first):
    """
    One deterministic OHLCV series in two phases.

    rising_first=True   a long rally, then a sharp break   (4h bearish, daily still bullish)
    rising_first=False  a long decline, then a sharp rally (4h bullish, daily still bearish)

    `move` is the size of the second phase as a fraction of the level reached
    by the first. It is the parameter that decides whether the two timeframes
    disagree, and the values below were chosen with margin rather than at the
    edge: a fixture that only just produces the condition stops producing it
    the first time an indicator length changes.
    """
    import numpy as np
    import pandas as pd

    closes = []
    for i in range(rows):
        if i < turn_at:
            t = i / (turn_at - 1)
            base = start + (peak - start) * (t ** 0.85)
        else:
            t = (i - turn_at + 1) / (rows - turn_at)
            base = peak * ((1.0 - move * (t ** 0.75)) if rising_first
                           else (1.0 + move * (t ** 0.75)))
        # Deterministic on every platform and every numpy: no RNG anywhere.
        closes.append(base * (1.0 + 0.006 * math.sin(i * 0.7)
                              + 0.003 * math.sin(i * 0.23)))

    close = np.array(closes)
    opens = np.concatenate(([close[0] * (0.999 if rising_first else 1.001)], close[:-1]))
    return pd.DataFrame({
        "timestamp": 1735689600000 + np.arange(rows) * 4 * 3600 * 1000,
        "open": opens,
        "high": np.maximum(opens, close) * 1.004,
        "low": np.minimum(opens, close) * 0.996,
        "close": close,
        "volume": 100_000 + 30_000 * np.abs(np.sin(np.arange(rows) * 0.37)),
    })


def _write_set(directory, rising_first):
    """The three files the pinned loader reads, all derived from one series."""
    import numpy as np

    base = (_series(450, 396, 0.42, 1.00, 0.14, True) if rising_first
            else _series(450, 396, 1.00, 0.42, 0.16, False))
    base.to_csv(os.path.join(directory, f"{SYMBOL}_{TIMEFRAME}.csv"), index=False)

    # Six 4h candles make one day -- a real aggregate, so the macro read is of
    # the same market rather than of a differently-shaped invention.
    groups = base.index // 6
    base.groupby(groups).agg(
        timestamp=("timestamp", "first"), open=("open", "first"),
        high=("high", "max"), low=("low", "min"),
        close=("close", "last"), volume=("volume", "sum"),
    ).reset_index(drop=True).to_csv(
        os.path.join(directory, f"{SYMBOL}_{MACRO_TIMEFRAME}.csv"), index=False)

    # BTC: reversed, so the asset is not correlated with itself.
    btc = base.copy()
    for column in ("open", "high", "low", "close"):
        btc[column] = btc[column].to_numpy()[::-1] * 137_000.0
    btc["volume"] = btc["volume"].to_numpy()[::-1] * 3.0
    btc.to_csv(os.path.join(directory, f"BTCUSDT_{TIMEFRAME}.csv"), index=False)


def _run(rising_first):
    from core import config
    from data.data_fetcher import DataFetcher, data_fetcher
    from models.signal_router import SignalRouter

    work = tempfile.mkdtemp(prefix="phase7_disagree_")
    original_url = data_fetcher.base_url
    original_log, original_chart = config.LOG_DIR, config.CHART_DIR
    try:
        pinned = os.path.join(work, "pinned")
        os.makedirs(pinned)
        _write_set(pinned, rising_first)
        config.LOG_DIR = os.path.join(work, "logs")
        config.CHART_DIR = os.path.join(work, "logs", "charts")
        data_fetcher.base_url = UNREACHABLE
        DataFetcher.set_pinned_source(pinned)
        return SignalRouter().route(symbol=SYMBOL, timeframe=TIMEFRAME)
    finally:
        DataFetcher.clear_pinned_source()
        data_fetcher.base_url = original_url
        config.LOG_DIR, config.CHART_DIR = original_log, original_chart
        shutil.rmtree(work, ignore_errors=True)


def _plan_direction(risk):
    """Which way the levels point, read off the levels."""
    targets = risk.get("targets") or ()
    if len(targets) < 2:
        return None
    first, last = float(targets[0]), float(targets[-1])
    return "LONG" if last > first else ("SHORT" if last < first else None)


# ============================================================
# The fixture must actually create the condition
# ============================================================
#
# Checked before anything is asserted about behaviour. Section 7.3 of the audit
# instruction names "tests whose setup contradicts what they claim to test" as
# a way a suite goes quietly useless, and this file is exactly the shape that
# fails that way: if the generated series ever stopped producing a
# disagreement -- an indicator length changes, an aggregation changes -- every
# test below would still pass, and would be testing agreement.

def test_the_fixture_really_does_split_the_two_timeframes():
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    decision = _run(rising_first=True)
    assert not decision.get("error"), decision.get("error")
    assert decision["bias"]["raw"] == "BEARISH", (
        f"the falling fixture produced a {decision['bias']['raw']} bias. It is "
        f"supposed to be bearish on the 4h."
    )
    assert decision["macro_bias"] == "BULLISH", (
        f"the falling fixture produced a {decision['macro_bias']} macro read. "
        f"The daily close is supposed to still be above its EMA-50 -- without "
        f"that there is no disagreement and this file tests nothing."
    )


def test_the_mirror_fixture_splits_them_the_other_way():
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    decision = _run(rising_first=False)
    assert not decision.get("error"), decision.get("error")
    assert decision["bias"]["raw"] == "BULLISH"
    assert decision["macro_bias"] == "BEARISH"


# ============================================================
# The property an operator depends on
# ============================================================

def test_the_action_never_contradicts_the_plan_beneath_it():
    """
    The invariant, stated once and checked on both polarities.

    Not "the engine returns WAIT here" -- that is today's answer to today's
    thresholds, and pinning it would make this test fail the next time a
    threshold legitimately moves. What must never be true, at any threshold,
    is a LONG label above descending targets.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    for rising_first in (True, False):
        decision = _run(rising_first)
        action = decision["explanation"]["summary"]
        plan = _plan_direction(decision["risk"])

        if plan is None:
            continue
        for side in ("LONG", "SHORT"):
            if side in action.split("—")[0]:
                assert plan == side, (
                    f"the engine returned an action containing {side} with a "
                    f"{plan.lower()} risk plan beneath it -- stop "
                    f"{decision['risk']['atr_stop']}, targets "
                    f"{decision['risk']['targets']}. An operator following the "
                    f"DECISION line would take the opposite side of the "
                    f"analysis."
                )


def test_a_bullish_macro_alone_cannot_produce_a_long():
    """
    The 2 September run, reconstructed from generated data rather than from a
    remembered panel.

    Against the code before commit 30408c2 this returns CONSERVATIVE LONG --
    verified, not assumed.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    decision = _run(rising_first=True)
    summary = decision["explanation"]["summary"]

    assert "LONG" not in summary.split("—")[0], (
        f"a bearish bias with a bullish macro produced {summary!r}. The macro "
        f"read has already been counted once, as a 10% weighted factor inside "
        f"bias_score."
    )


def test_a_bearish_macro_alone_cannot_produce_a_short():
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    decision = _run(rising_first=False)
    summary = decision["explanation"]["summary"]
    assert "SHORT" not in summary.split("—")[0], (
        f"a bullish bias with a bearish macro produced {summary!r}."
    )


def test_the_stated_reason_matches_the_bias_the_engine_reported():
    """
    The panel contradicted itself: "Bias is bullish and the broader macro trend
    agrees" printed four lines above "The higher timeframe disagrees with this
    bias". Item 8's class -- an engine asserting something that is not so -- in
    the sentence the operator reads first.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    decision = _run(rising_first=True)
    reasons = " ".join(decision["explanation"]["reasons"]).lower()

    assert "bias is bullish" not in reasons, (
        "the explanation calls the bias bullish on a run the engine itself "
        "reported as BEARISH."
    )


def test_the_engine_still_reaches_a_side_when_the_timeframes_agree():
    """
    The control, and the reason it matters here specifically.

    Every other test in this file passes if the engine simply stops taking
    directions. This is a series with no disagreement at all -- a plain,
    uninterrupted rally -- and the engine must still be willing to be bullish
    about it.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    from core import config
    from data.data_fetcher import DataFetcher, data_fetcher
    from models.signal_router import SignalRouter
    import numpy as np

    work = tempfile.mkdtemp(prefix="phase7_agree_")
    original_url = data_fetcher.base_url
    original_log, original_chart = config.LOG_DIR, config.CHART_DIR
    try:
        pinned = os.path.join(work, "pinned")
        os.makedirs(pinned)
        # turn_at == rows: one phase only, so both timeframes see the same rally.
        base = _series(450, 450, 0.42, 1.00, 0.0, True)
        base.to_csv(os.path.join(pinned, f"{SYMBOL}_{TIMEFRAME}.csv"), index=False)
        groups = base.index // 6
        base.groupby(groups).agg(
            timestamp=("timestamp", "first"), open=("open", "first"),
            high=("high", "max"), low=("low", "min"),
            close=("close", "last"), volume=("volume", "sum"),
        ).reset_index(drop=True).to_csv(
            os.path.join(pinned, f"{SYMBOL}_{MACRO_TIMEFRAME}.csv"), index=False)
        btc = base.copy()
        for column in ("open", "high", "low", "close"):
            btc[column] = btc[column].to_numpy()[::-1] * 137_000.0
        btc["volume"] = btc["volume"].to_numpy()[::-1] * 3.0
        btc.to_csv(os.path.join(pinned, f"BTCUSDT_{TIMEFRAME}.csv"), index=False)

        config.LOG_DIR = os.path.join(work, "logs")
        config.CHART_DIR = os.path.join(work, "logs", "charts")
        data_fetcher.base_url = UNREACHABLE
        DataFetcher.set_pinned_source(pinned)
        decision = SignalRouter().route(symbol=SYMBOL, timeframe=TIMEFRAME)
    finally:
        DataFetcher.clear_pinned_source()
        data_fetcher.base_url = original_url
        config.LOG_DIR, config.CHART_DIR = original_log, original_chart
        shutil.rmtree(work, ignore_errors=True)

    assert not decision.get("error"), decision.get("error")
    assert decision["bias"]["raw"] == "BULLISH", (
        "an uninterrupted rally did not produce a bullish bias. If the engine "
        "cannot be bullish about this, the tests above prove nothing."
    )
    assert decision["macro_bias"] == "BULLISH", (
        "the two timeframes are supposed to AGREE in this control."
    )
