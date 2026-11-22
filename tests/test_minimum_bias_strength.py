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
distinct" went with the threshold.

THE REDESIGN'S STAGE 4, 15 November 2026 -- RULING 1'S SENTENCES

Ruling 1's tests held that no reason string may quote trend health without
saying which way the trend points: "trend strength 90/100 (up)", never
"strong trend health (90/100)" offered as support for a direction the
magnitude cannot speak to. The ladder does not quote trend health at all
now -- the tier comes from entry quality (ruling 4, 25 October 2026), and
trend_note went with it -- so:

  - test_a_bearish_trend_under_a_bullish_bias_is_visible_in_the_sentence and
    test_a_flat_trend_says_flat GO. There is no sentence left for the
    disagreement to be invisible in, and nothing to say "(flat)" about.
  - test_the_reason_names_the_trend_direction_not_just_its_size is REPLACED
    by test_the_ladder_quotes_no_trend_health_at_all, which holds the
    stronger thing the change makes true.
  - test_every_directional_reason_carries_the_direction keeps its sweep,
    over the new sentences, and no longer passes vacuously: it asserts that
    none of them quotes trend health, rather than only checking the ones
    that do.

Ruling 2's tests are unchanged in what they hold; their helper runs gate 9
as well as the ladder, since the tier is gate 9's.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.decision_model import DecisionModel
from models.bias_engine import direction_from_emas

NEUTRAL_SENTENCE = "The direction is NEUTRAL"
SUMS = (-100.0, -60.0, -30.01, -21.0, 0.0, 21.0, 30.01, 60.0, 100.0)


def _decide(score, raw="BULLISH", entry=80.0, inside=True):
    """
    The ladder and gate 9 -- the two stages that between them decide the
    action and its tier.

    Stage 4, 15 November 2026: the `health` and `sign` parameters built the
    trend block, which _determine_final_action no longer takes, and
    `status` was the STATUS word the AGGRESSIVE tier used to read. `inside`
    is the field it reads instead (Viktor's ruling of 7 November).
    """
    reasons = []
    model = DecisionModel()
    entry_block = {
        "score": entry, "close_inside_band": inside,
        "entry_status": "INSIDE THE BAND" if inside else "ABOVE THE BAND"}
    risk = {"risk_valid": True, "risk_regime": "NORMAL RISK",
            "validation_state": "NEUTRAL"}
    action = model._determine_final_action(
        bias={"raw": raw, "score": score},
        entry=entry_block,
        risk=risk,
        # Work order G, 27 September 2026: the ladder no longer takes
        # macro_bias, and this helper's `macro` parameter is gone with it.
        reasons=reasons,
    )
    action = model._apply_quality_gate(action, entry_block, risk, reasons)
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

    action, _ = _decide(score=-60.0, raw="NEUTRAL")
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
        short, _ = _decide(score=score, raw="BEARISH")
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

def test_the_ladder_quotes_no_trend_health_at_all():
    """
    Replaces test_the_reason_names_the_trend_direction_not_just_its_size at
    stage 4 (see the module docstring).

    Ruling 1's defect was a direction-blind magnitude offered as support for
    a direction: "Bias is bullish with strong trend health (90/100)", the
    same 90 whichever way the trend ran. The fix was to name the direction
    beside the magnitude. The magnitude is not quoted here any more, which
    is the stronger answer, and this holds it -- so that re-adding the
    sentence fails here rather than quietly bringing the old wording's
    hazard back with it.

    The number is still measured, recorded and printed on the TREND line
    until stage 5. What may not happen is the ladder or the tier reasoning
    for it.
    """
    for raw, entry, inside in (("BULLISH", 80.0, True), ("BULLISH", 60.0, False),
                               ("BEARISH", 80.0, True), ("BEARISH", 40.0, False),
                               ("NEUTRAL", 80.0, True)):
        _, reasons = _decide(score=60.0, raw=raw, entry=entry, inside=inside)
        text = " ".join(reasons)
        for gone in ("trend strength", "trend health", "(up)", "(down)",
                     "(flat)", "strong trend"):
            assert gone not in text.lower().replace("trend health,", ""), (
                f"{raw}/{entry}: the ladder quotes {gone!r} again: {text!r}")


def test_every_directional_reason_carries_the_direction():
    """
    Sweep. No reason string may quote trend health without saying which way
    the trend points -- and since stage 4 none of them quotes it at all, so
    the sweep asserts that instead of only checking the ones that do.

    It was conditional on "trend strength" appearing in the text. That
    condition is now never true, which would make this test pass whatever
    the sentences said. A test that can only pass is not a test; this is
    the same lesson as the vacuous assertion of 3 September.
    """
    seen = set()
    for raw in ("BULLISH", "BEARISH"):
        for score in SUMS:
            for entry, inside in ((80.0, True), (80.0, False), (60.0, False),
                                  (40.0, False)):
                action, reasons = _decide(score=score, raw=raw, entry=entry,
                                          inside=inside)
                seen.add(action)
                text = " ".join(reasons)
                assert "trend strength" not in text, (raw, entry, text)
                side = "LONG" if raw == "BULLISH" else "SHORT"
                # Every sentence that names a tier names its side with it,
                # so a reader can never be shown a tier without one.
                for reason in reasons:
                    if "CONSERVATIVE" in reason or "AGGRESSIVE" in reason:
                        assert side in reason, (raw, reason)
    # The sweep actually visited every tier and the quality gate's WAIT,
    # rather than one of them many times.
    assert seen == {"AGGRESSIVE LONG", "LONG", "CONSERVATIVE LONG",
                    "AGGRESSIVE SHORT", "SHORT", "CONSERVATIVE SHORT",
                    "WAIT"}, sorted(seen)
