"""
Round 6 (Meta Muse Spark 1.3), F2 -- Item 10 Consistent Semantics, Minor.

THE FINDING

core/engine_core.py's raw return value carried

    "risk": {..., "confidence_score": trend["trend_health"], ...}

-- unsigned trend magnitude -- under the exact dotted name
("risk.confidence_score") that models/signal_router.py's
_build_decision_object gives a different quantity in the final decision
object it assembles independently: DecisionModel's bias-magnitude
confidence (`float(confidence)`, where confidence = abs(bias.score)).

The router overwrites the key unconditionally rather than reading engine_core's
value, so today's operator only ever sees one meaning -- but nothing stopped a
future direct consumer of Phase7Engine.run() (as the report notes live_trading.py
once was) from reading the other one under the identical name.

THE FIX

RULED, 13 September 2026: drop rather than rename. The value engine_core's raw
"risk" dict held is not lost -- it is already recorded, correctly and without
a name collision, at decision_object["trend"]["trend_health"] a few lines
below in the same return object. A second copy under a name that means
something else downstream serves no reader.

WHAT THESE TESTS HOLD

That engine_core's raw output no longer states two things under one name --
the risk block's "confidence_score" key is gone from Phase7Engine.run()'s own
return value -- while trend_health is still there in full; and, as a negative
control, that the FINAL decision object's meaning (the one the panel, the
decision log, and every existing test of "confidence_score" reads) is
untouched: still DecisionModel's bias magnitude, unaffected by this fix
because signal_router never read engine_core's copy in the first place.
"""

import math
import os

import pytest

from conftest import REPO_ROOT

PINNED_DIR = os.path.join(REPO_ROOT, "tests", "fixtures", "pinned")
UNREACHABLE = "http://127.0.0.1:9"


def _engine_available():
    try:
        import pandas_ta  # noqa: F401
        return True
    except Exception:
        return False


def _raw_engine_output():
    """Phase7Engine.run() directly -- engine_core's own raw return value,
    bypassing SignalRouter entirely. This is the layer F2 is about."""
    import core.engine_core as ec
    from data.data_fetcher import DataFetcher, data_fetcher

    original_url = data_fetcher.base_url
    try:
        data_fetcher.base_url = UNREACHABLE
        DataFetcher.set_pinned_source(PINNED_DIR)
        return ec.Phase7Engine().run(symbol="AEROUSDT", timeframe="4h",
                                      save_chart=False)
    finally:
        DataFetcher.clear_pinned_source()
        data_fetcher.base_url = original_url


def _routed_decision():
    """The final decision object, through SignalRouter -- the layer every
    other 'confidence_score' test in this suite reads."""
    from data.data_fetcher import DataFetcher, data_fetcher
    from models.signal_router import SignalRouter

    original_url = data_fetcher.base_url
    try:
        data_fetcher.base_url = UNREACHABLE
        DataFetcher.set_pinned_source(PINNED_DIR)
        return SignalRouter().route(symbol="AEROUSDT", timeframe="4h")
    finally:
        DataFetcher.clear_pinned_source()
        data_fetcher.base_url = original_url


def test_the_raw_engine_risk_block_no_longer_states_a_second_confidence():
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    raw = _raw_engine_output()
    risk = raw.get("risk", {})

    assert "confidence_score" not in risk, (
        "engine_core.Phase7Engine.run()'s own risk block still carries "
        f"confidence_score ({risk.get('confidence_score')!r}), the exact "
        "dotted name signal_router._build_decision_object gives a different "
        "meaning (bias magnitude, not trend health) in the final decision "
        "object. Round 6 F2 is about this duplicate meaning."
    )


def test_negative_control_trend_health_is_still_recorded_in_full():
    """
    MUST PASS BOTH BEFORE AND AFTER THE FIX.

    The value dropped from risk.confidence_score is not lost information --
    it was always a duplicate of trend.trend_health, which this asserts is
    still present and finite.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    raw = _raw_engine_output()
    trend_health = raw.get("trend", {}).get("trend_health")

    assert trend_health is not None and math.isfinite(trend_health), (
        f"trend.trend_health is {trend_health!r} -- the one place this "
        f"number is now recorded"
    )


def test_negative_control_the_routed_decisions_confidence_is_unchanged():
    """
    MUST PASS BOTH BEFORE AND AFTER THE FIX.

    signal_router never read engine_core's copy of confidence_score -- it
    always overwrote the key with DecisionModel's own bias-magnitude
    confidence. Dropping the unread engine-layer duplicate must not move the
    one meaning every operator, the panel and the decision log actually see.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    decision = _routed_decision()
    risk = decision.get("risk", {})

    assert "confidence_score" in risk, "the final decision object lost its confidence_score field entirely"
    confidence = risk["confidence_score"]
    assert isinstance(confidence, (int, float)) and math.isfinite(confidence), (
        f"risk.confidence_score is {confidence!r} in the final decision object"
    )
