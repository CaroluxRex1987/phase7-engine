"""
The one-line summary names the reason for the action it reports.

FOUND 20 SEPTEMBER 2026, while scoping five questions Viktor had raised about
the panel's numbers.

    explanation["summary"] = f"{final_action} - {reasons[-1]}"

_compute_ev appends to `reasons` last on every path through evaluate(), so
reasons[-1] was ALWAYS the illustrative expected-value sentence. The summary
of every run was therefore the EV line, whatever the run actually decided.
tests/fixtures/golden_decision.json recorded the result for a refused trade:

    NO-TRADE (RISK TOO HIGH) - Expected value (illustrative, not
    backtested): ... +1.31R per trade - positive -- worth taking on average

A refusal summarised as worth taking. The summary reaches the decision object
and the decision log; it is not printed on the panel, which is why six audit
rounds and a year of panels did not surface it.

WHY NOT reasons[0]

_refuse_incoherent_plan and _apply_degradation can both replace final_action
after _determine_final_action has already written its reason. reasons[0]
would then describe the action that was overruled -- the same class of defect
in the other direction. evaluate() tracks which stage last SET the action.

These tests are written without fixtures: run_tests.py calls every test_*
function with no arguments, and its error count (32) is watched.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.decision_model import DecisionModel


def _evaluate(risk_valid=True, degradation=None, targets=(1.1, 1.2, 1.3),
              score=77.0, raw="BULLISH", health=90.0, entry_score=80.0):
    return DecisionModel().evaluate(
        bias={"raw": raw, "score": score},
        trend={"trend_health": health, "trend_direction_sign": 1,
               "momentum_divergence": False},
        # Work order F, 21 September 2026: a complete, confirmed long
        # signal, so the confirmation gate passes and these tests keep
        # testing the summary rather than the gate's fail-safe refusal.
        entry={"score": entry_score, "entry_status": "ACTIVE ENTRY ZONE",
               "long_signal": True, "short_signal": False,
               "long_signal_blockers": [],
               "short_signal_blockers": ["structure is BULLISH TREND, not BEARISH TREND"]},
        risk={"risk_valid": risk_valid,
              "risk_reason": "Stop distance exceeds maximum allowable threshold (15%).",
              "risk_regime": "NORMAL RISK",
              "validation_state": "NEUTRAL",
              "targets": list(targets)},
        macro_bias="BULLISH",
        degradation=list(degradation) if degradation else None,
    )


def _summary_reason(decision):
    """The part of the summary after the action."""
    return decision["explanation"]["summary"].split("—", 1)[-1].strip()


def test_a_refused_trade_is_not_summarised_as_worth_taking():
    decision = _evaluate(risk_valid=False)

    assert decision["final_action"] == "NO-TRADE (RISK TOO HIGH)", decision["final_action"]
    summary = decision["explanation"]["summary"]
    assert "Expected value" not in summary, (
        "the summary is the illustrative EV sentence again: %r" % summary
    )
    assert "Risk check failed" in summary, summary


def test_the_summary_reason_is_one_of_the_reasons():
    """
    Not a tautology: it fails if the index ever points past the list or at a
    reason that was rewritten after being chosen.
    """
    decision = _evaluate(risk_valid=False)
    assert _summary_reason(decision) in decision["explanation"]["reasons"]


def test_the_ev_sentence_is_still_present_in_the_reasons():
    """
    The fix moves which reason heads the summary. It does not remove the EV
    line from the reasoning, which is a separate call Viktor has not made.
    """
    decision = _evaluate(risk_valid=False)
    assert any(r.startswith("Expected value") for r in decision["explanation"]["reasons"])


def test_a_degraded_run_that_changes_the_action_is_summarised_by_that_change():
    decision = _evaluate(degradation=["RSI unavailable"])

    assert decision["final_action"] == "NO-TRADE (DEGRADED INPUT)", decision["final_action"]
    summary = decision["explanation"]["summary"]
    assert "would have been" in summary, (
        "a degraded run kept the pre-degradation reason in its summary: %r" % summary
    )
    assert "Expected value" not in summary, summary


def test_an_incoherent_plan_refusal_is_summarised_by_the_refusal():
    # Targets descending from the stop make the plan a SHORT while the action
    # is a LONG -- _refuse_incoherent_plan's case.
    decision = _evaluate(targets=(1.3, 1.2, 1.1))

    assert decision["final_action"] == "NO-TRADE (PLAN CONTRADICTS ACTION)", decision["final_action"]
    summary = decision["explanation"]["summary"]
    assert "Expected value" not in summary, summary
    assert "contradicts" in summary.lower() or "plan" in summary.lower(), summary


def test_a_normal_long_is_summarised_by_the_reason_it_is_a_long():
    decision = _evaluate()

    assert "LONG" in decision["final_action"], decision["final_action"]
    summary = decision["explanation"]["summary"]
    assert "Expected value" not in summary, summary
    assert "Bias is bullish" in summary, summary


# ======================================================================
# The EV sentence says what the number is
# ======================================================================

def test_the_ev_sentence_says_it_is_confidence_restated():
    decision = _evaluate(risk_valid=False)
    ev_line = [r for r in decision["explanation"]["reasons"] if r.startswith("Expected value")][0]

    assert "restated" in ev_line, ev_line
    assert "never disagree" in ev_line, ev_line


def test_the_quoted_confidence_levels_follow_the_constants():
    """
    Negative control for a hardcoded 33/43: move AVG_REWARD_R and the quoted
    levels must move with it. 1:1 puts breakeven at 50 and positive at 65.
    """
    model = DecisionModel()
    baseline = model._compute_ev(77.0, "LONG", [])
    assert baseline["avg_reward_r"] == 2.0

    original = DecisionModel.AVG_REWARD_R
    try:
        DecisionModel.AVG_REWARD_R = 1.0
        reasons = []
        DecisionModel()._compute_ev(77.0, "LONG", reasons)
        assert "50/100" in reasons[0] and "65/100" in reasons[0], reasons[0]
    finally:
        DecisionModel.AVG_REWARD_R = original

    reasons = []
    DecisionModel()._compute_ev(77.0, "LONG", reasons)
    assert "33/100" in reasons[0] and "43/100" in reasons[0], reasons[0]


def test_the_breakeven_band_constant_is_live():
    """
    Sequence item 14's rule: a named constant nothing reads is a knob that
    changes nothing. Widening the band must turn a positive verdict into a
    breakeven one.
    """
    reasons = []
    DecisionModel()._compute_ev(60.0, "LONG", reasons)
    assert "positive" in reasons[0], reasons[0]

    original = DecisionModel.EV_BREAKEVEN_BAND_R
    try:
        DecisionModel.EV_BREAKEVEN_BAND_R = 1.0
        reasons = []
        DecisionModel()._compute_ev(60.0, "LONG", reasons)
        assert "close to breakeven" in reasons[0], reasons[0]
    finally:
        DecisionModel.EV_BREAKEVEN_BAND_R = original


def test_ev_is_a_straight_line_in_confidence():
    """
    States the property the sentence now claims, so a future change that makes
    EV carry independent information fails here rather than silently making
    the sentence false.
    """
    model = DecisionModel()
    values = [model._compute_ev(c, "LONG", [])["ev_r"] for c in (0.0, 25.0, 50.0, 75.0, 100.0)]
    steps = [round(b - a, 9) for a, b in zip(values, values[1:])]
    assert len(set(steps)) == 1, (
        "ev_r is no longer linear in confidence: steps %r" % (steps,)
    )
    assert values[0] == -1.0 and values[-1] == 2.0, values
