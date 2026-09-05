"""
A lean is not a case, and a direction-blind number is not support.

TWO OF VIKTOR'S RULINGS, 5 SEPTEMBER 2026, IN ONE PATCH BECAUSE THEY TOUCH
ONE FUNCTION.

RULING 1 -- the reason strings

    "Bias is bullish with strong trend health (90/100)"

trend_health is an UNSIGNED magnitude. A strong DOWNtrend also scores 90, so
the sentence offered a number as support for a direction when the identical
number would have appeared if the trend ran the other way. It could no longer
CHOOSE the direction -- that was the Critical fixed on 2 September -- but it
was still being cited as evidence for one.

trend_direction_sign arrived on 4 September for exactly this reason. The
sentences now read "trend strength 90/100 (up)" and name the direction beside
the magnitude, so a reader can see when the two disagree.

RULING 2 -- a minimum bias strength

_determine_final_action read only the raw_bias STRING. A bias_score of 21 --
barely past bias_engine's RAW_BIAS_THRESHOLD of 20 -- with trend health above
75 and entry above 70 returned AGGRESSIVE LONG, printed directly above
CONFIDENCE 21/100.

MIN_ACTION_BIAS is 30, matching the CONFIRMED threshold where the state
machine already separates a lean from a conviction.

WHY TWO THRESHOLDS AND NOT ONE

Raising RAW_BIAS_THRESHOLD to 30 would have been simpler and was rejected.
The two answer different questions:

    RAW_BIAS_THRESHOLD (20)   does the blend lean far enough to CALL a side?
    MIN_ACTION_BIAS    (30)   is that lean strong enough to ACT on?

Collapsing them loses the distinction between leaning bullish and being
bullish enough to trade -- and risk_model builds the plan's shape from the
sign either way, so the label still has work to do below 30.

The risk of two thresholds is sequence item 14's finding: a constant nothing
reads. Both are held live below.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.decision_model import DecisionModel, MIN_ACTION_BIAS
from models.bias_engine import RAW_BIAS_THRESHOLD


def _decide(score, raw="BULLISH", health=90.0, sign=1, entry=80.0,
            status="ACTIVE ENTRY ZONE", macro="BULLISH"):
    reasons = []
    action = DecisionModel()._determine_final_action(
        bias={"raw": raw, "score": score},
        trend={"trend_health": health, "trend_direction_sign": sign,
               "momentum_divergence": False},
        entry={"score": entry, "entry_status": status},
        risk={"risk_valid": True, "risk_regime": "NORMAL RISK",
              "validation_state": "NEUTRAL"},
        macro_bias=macro,
        reasons=reasons,
    )
    return action, reasons


# ======================================================================
# Ruling 2 -- the floor
# ======================================================================

def test_a_weak_lean_does_not_authorise_a_direction():
    """
    The case that prompted the ruling: score 21, everything else strong.
    """
    action, reasons = _decide(score=21.0)

    assert action == "WAIT", (
        f"bias_score 21 returned {action!r}. That is a directional action on a "
        f"lean barely past the labelling threshold, printed above CONFIDENCE 21."
    )
    assert any("below the" in r and "act on a direction" in r for r in reasons), reasons


def test_the_same_floor_applies_to_the_short_side():
    action, _ = _decide(score=-21.0, raw="BEARISH", sign=-1, macro="BEARISH")
    assert action == "WAIT"


def test_a_lean_at_the_threshold_still_waits():
    action, _ = _decide(score=MIN_ACTION_BIAS - 0.01)
    assert action == "WAIT"


def test_a_conviction_past_the_threshold_still_acts():
    action, _ = _decide(score=MIN_ACTION_BIAS + 0.01)
    assert action != "WAIT", (
        "the floor is blocking scores it should let through -- it is a "
        "minimum, not a new gate"
    )
    assert "LONG" in action


def test_both_thresholds_are_live_and_distinct():
    """
    Sequence item 14's finding, applied before it can repeat: a fingerprinted
    constant that nothing reads makes the record name a knob that changes
    nothing.
    """
    assert MIN_ACTION_BIAS > RAW_BIAS_THRESHOLD, (
        "MIN_ACTION_BIAS no longer sits above RAW_BIAS_THRESHOLD, so it can "
        "never fire and the second threshold is dead"
    )
    below, _ = _decide(score=(RAW_BIAS_THRESHOLD + MIN_ACTION_BIAS) / 2)
    above, _ = _decide(score=MIN_ACTION_BIAS + 5)
    assert below == "WAIT" and above != "WAIT", (
        f"a score between the two thresholds gave {below!r} and one above gave "
        f"{above!r}; the two constants are not doing different work"
    )


def test_the_constant_is_fingerprinted():
    from core.decision_log import FINGERPRINTED_MODULES, module_snapshot

    assert "models.decision_model" in FINGERPRINTED_MODULES
    assert "MIN_ACTION_BIAS" in FINGERPRINTED_MODULES["models.decision_model"]
    assert module_snapshot()["models.decision_model"]["MIN_ACTION_BIAS"] == MIN_ACTION_BIAS


# ======================================================================
# Ruling 1 -- the reason strings
# ======================================================================

def test_the_reason_names_the_trend_direction_not_just_its_size():
    _, reasons = _decide(score=60.0, health=90.0, sign=1)
    text = " ".join(reasons)

    assert "trend strength 90/100 (up)" in text, text
    assert "strong trend health" not in text, (
        "the old wording is back: a direction-blind magnitude offered as "
        "support for a direction"
    )


def test_a_bearish_trend_under_a_bullish_bias_is_visible_in_the_sentence():
    """
    The point of the ruling. trend_health 90 on a DOWNtrend must not read as
    support for a long -- the reader has to be able to see the disagreement.
    """
    _, reasons = _decide(score=60.0, health=90.0, sign=-1)
    text = " ".join(reasons)

    assert "(down)" in text, (
        f"a bearish trend under a bullish bias produced: {text!r}. The "
        f"direction is invisible, which is the defect."
    )
    assert "(up)" not in text


def test_a_flat_trend_says_flat():
    _, reasons = _decide(score=60.0, health=40.0, sign=0)
    assert "(flat)" in " ".join(reasons)


def test_every_directional_reason_carries_the_direction():
    """
    Sweep. No reason string may quote trend health without saying which way
    the trend points.
    """
    for score, raw, sign, macro in ((60.0, "BULLISH", 1, "BULLISH"),
                                    (-60.0, "BEARISH", -1, "BEARISH"),
                                    (60.0, "BULLISH", -1, "BULLISH"),
                                    (-60.0, "BEARISH", 1, "BEARISH")):
        for entry, status in ((80.0, "ACTIVE ENTRY ZONE"), (40.0, "APPROACHING ZONE")):
            _, reasons = _decide(score=score, raw=raw, sign=sign,
                                 entry=entry, status=status, macro=macro)
            text = " ".join(reasons)
            if "trend strength" in text:
                assert ("(up)" in text or "(down)" in text or "(flat)" in text), (
                    f"score={score} sign={sign} entry={entry}: {text!r}"
                )
