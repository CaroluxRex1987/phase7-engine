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

THE REDESIGN'S STAGE 2, 14 November 2026 -- RULING 2's MECHANISM IS REPLACED

Viktor's ruling of 7 November 2026: the direction is EMA50's slope and the
order of EMA_20 and EMA_50, and their agreement is the floor. BULLISH and
BEARISH are no longer a sum past 20, so "a lean" is no longer a label under
30: it is the NEUTRAL direction, the two disagreeing. MIN_ACTION_BIAS is
gone from the code and from the fingerprint, and "both thresholds" above is
the dated account. Ruling 2 itself stands -- a lean is not a case -- and its
six tests became four:

  - a NEUTRAL direction authorises no side, whatever the weighted sum says,
    and says why in a sentence of its own (was: a score of 21 waits);
  - the floor is the same on the short side, at the rule itself (was: a
    score of -21 waits);
  - a direction acts whatever the sum's size (was: a score past 30 still
    acts). This one's expectation is turned round on purpose, and its
    docstring says what that leaves until stage 5;
  - the constant is gone from the module and the fingerprint (was: it is
    fingerprinted).

"A lean at the threshold still waits" and "both thresholds are live and
distinct" went with the threshold. Ruling 1's four tests are unchanged.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.decision_model import DecisionModel
from models.bias_engine import direction_from_emas

NEUTRAL_SENTENCE = "The direction is NEUTRAL"
SUMS = (-100.0, -60.0, -30.01, -21.0, 0.0, 21.0, 30.01, 60.0, 100.0)


def _decide(score, raw="BULLISH", health=90.0, sign=1, entry=80.0,
            status="ACTIVE ENTRY ZONE"):
    reasons = []
    action = DecisionModel()._determine_final_action(
        bias={"raw": raw, "score": score},
        trend={"trend_health": health, "trend_direction_sign": sign,
               "momentum_divergence": False},
        entry={"score": entry, "entry_status": status},
        risk={"risk_valid": True, "risk_regime": "NORMAL RISK",
              "validation_state": "NEUTRAL"},
        # Work order G, 27 September 2026: the ladder no longer takes
        # macro_bias, and this helper's `macro` parameter is gone with it.
        reasons=reasons,
    )
    return action, reasons


# ======================================================================
# Ruling 2 -- the floor
# ======================================================================

def test_a_neutral_direction_does_not_authorise_a_side():
    """
    The case that prompted the ruling was a score of 21 with everything else
    strong. The lean is the NEUTRAL direction now: everything else strong,
    and the weighted sum anywhere at all, 100 included.
    """
    for score in SUMS:
        action, reasons = _decide(score=score, raw="NEUTRAL")
        assert action == "WAIT", (
            f"a NEUTRAL direction with a weighted sum of {score} returned "
            f"{action!r}. The sum does not decide the direction; a lean is "
            f"not a case.")
        assert any(NEUTRAL_SENTENCE in r and "no side to act on" in r
                   for r in reasons), reasons
        assert not any("below the" in r for r in reasons), (
            "the threshold's sentence is back", reasons)


def test_the_same_floor_applies_to_the_short_side():
    """
    At the rule itself, since the ladder only sees the label. The slow
    average rising with the fast one under it is no long; the slow average
    falling with the fast one over it is no short.
    """
    assert direction_from_emas(0.1, 99.0, 100.0) == "NEUTRAL"
    assert direction_from_emas(-0.1, 101.0, 100.0) == "NEUTRAL"
    assert direction_from_emas(0.1, 101.0, 100.0) == "BULLISH"
    assert direction_from_emas(-0.1, 99.0, 100.0) == "BEARISH"

    action, _ = _decide(score=-60.0, raw="NEUTRAL", sign=-1)
    assert action == "WAIT"


def test_a_direction_acts_whatever_the_weighted_sum_says():
    """
    TURNED ROUND at stage 2, on purpose. Until then a BULLISH label with a
    sum under 30 was a lean and waited, and this test held that a sum past
    30 still acted. A BULLISH direction is now EMA50 rising with EMA20 above
    it, which is the whole floor (Viktor's ruling of 7 November 2026), so
    the sum's size gates nothing: 21, 0 and a sum pointing the other way all
    act as 60 does.

    What that leaves until stage 5: confidence is still the sum's size, so a
    run can print AGGRESSIVE LONG above CONFIDENCE 21/100, the picture the
    ruling of 5 September was made against. Confidence leaves in stage 5;
    it is not given a new meaning for three commits on a branch the
    scheduled task does not run.
    """
    wanted = _decide(score=60.0)[0]
    assert "LONG" in wanted, wanted
    for score in SUMS:
        action, reasons = _decide(score=score)
        assert action == wanted, (score, action, reasons)
        short, _ = _decide(score=score, raw="BEARISH", sign=-1)
        assert "SHORT" in short, (score, short)


def test_the_constant_is_gone_from_the_code_and_the_fingerprint():
    """
    Was test_the_constant_is_fingerprinted. A constant that stayed in the
    fingerprint after nothing read it is sequence item 14's finding; one
    that stayed in the module would be read by the fingerprint scan
    (tests/test_fingerprint_names_every_constant.py) and fail it.
    """
    from core.decision_log import FINGERPRINTED_MODULES, module_snapshot
    import models.decision_model as dm

    assert not hasattr(dm, "MIN_ACTION_BIAS")
    assert "models.decision_model" in FINGERPRINTED_MODULES
    assert "MIN_ACTION_BIAS" not in FINGERPRINTED_MODULES["models.decision_model"]
    assert "MIN_ACTION_BIAS" not in module_snapshot()["models.decision_model"]


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
    for score, raw, sign in ((60.0, "BULLISH", 1),
                             (-60.0, "BEARISH", -1),
                             (60.0, "BULLISH", -1),
                             (-60.0, "BEARISH", 1)):
        for entry, status in ((80.0, "ACTIVE ENTRY ZONE"), (40.0, "APPROACHING ZONE")):
            _, reasons = _decide(score=score, raw=raw, sign=sign,
                                 entry=entry, status=status)
            text = " ".join(reasons)
            if "trend strength" in text:
                assert ("(up)" in text or "(down)" in text or "(flat)" in text), (
                    f"score={score} sign={sign} entry={entry}: {text!r}"
                )
