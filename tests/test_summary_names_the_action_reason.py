"""
The one-line summary names the reason for the action it reports.

FOUND 20 SEPTEMBER 2026, while scoping five questions Viktor had raised about
the panel's numbers.

    explanation["summary"] = f"{final_action} - {reasons[-1]}"

_compute_ev appended to `reasons` last on every path through evaluate(), so
reasons[-1] was ALWAYS the illustrative expected-value sentence. The summary
of every run was therefore the EV line, whatever the run actually decided.
(The EV sentence itself is gone at the redesign's stage 5, 15 November 2026 --
see the record at the foot of this file. The fix it exposed is not: the
summary names the reason belonging to whichever stage last SET the action,
which is what these tests hold.)
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
function with no arguments, and its error count is watched; its current
figure is in docs/PHASE7_NEXT.md, "Where things stand, right now", under
"Test suite". (Part 4's test shapes, 15 October 2026: this said 32, right at
the time, and the figure is no longer written here, so it cannot go stale.)
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.decision_model import DecisionModel


def _evaluate(risk_valid=True, degradation=None, targets=(1.1, 1.2, 1.3),
              score=77.0, raw="BULLISH", health=90.0, entry_score=80.0):
    return DecisionModel().evaluate(
        # The redesign's stage 5, 15 November 2026: `trend` was the second
        # positional parameter and is gone -- _compute_trade_quality was
        # its last reader in the decision model. The `score` this bias
        # dict carried and the `validation_state` in the risk dict are
        # gone with it: neither is a field the engine writes now.
        bias={"raw": raw},
        # Work order F, 21 September 2026: a complete, confirmed long
        # signal, so the confirmation gate passes and these tests keep
        # testing the summary rather than the gate's fail-safe refusal.
        # The redesign's stage 4, 15 November 2026: AGGRESSIVE reads
        # close_inside_band, not the STATUS word "ACTIVE ENTRY ZONE" this
        # record carried (Viktor's ruling of 7 November).
        entry={"score": entry_score, "close_inside_band": True,
               "entry_status": "INSIDE THE BAND",
               "long_signal": True, "short_signal": False,
               "long_signal_blockers": [],
               "short_signal_blockers": ["structure is BULLISH TREND, not BEARISH TREND"],
               # The redesign's stage 3, 15 November 2026: and a trigger
               # that holds, so gate 8 passes too, for the same reason.
               "trigger": True, "trigger_volume": 2.0,
               "trigger_volume_median": 1.0},
        risk={"risk_valid": risk_valid,
              "risk_reason": "Stop distance exceeds maximum allowable threshold (15%).",
              "risk_regime": "NORMAL RISK",
              "validation_state": "NEUTRAL",
              "targets": list(targets)},
        degradation=list(degradation) if degradation else None,
    )


def _summary_reason(decision):
    """The part of the summary after the action."""
    return decision["explanation"]["summary"].split("—", 1)[-1].strip()


def test_a_refused_trade_is_not_summarised_as_worth_taking():
    decision = _evaluate(risk_valid=False)

    assert decision["final_action"] == "NO-TRADE (RISK TOO HIGH)", decision["final_action"]
    summary = decision["explanation"]["summary"]
    # Stage 5, 15 November 2026: there is no EV sentence to be summarised by
    # any more, so this half can no longer fail for the reason the file was
    # written for. It is kept as the guard that no sentence reading as a
    # recommendation reaches the summary of a refusal, and the positive
    # assertion below is what now carries the test.
    assert "Expected value" not in summary, (
        "the summary is the illustrative EV sentence again: %r" % summary
    )
    assert "worth taking" not in summary, summary
    assert "Risk check failed" in summary, summary


def test_the_summary_reason_is_one_of_the_reasons():
    """
    Not a tautology: it fails if the index ever points past the list or at a
    reason that was rewritten after being chosen.
    """
    decision = _evaluate(risk_valid=False)
    assert _summary_reason(decision) in decision["explanation"]["reasons"]


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
    # Stage 4, 15 November 2026: the summary named the ladder's sentence,
    # which opened "Bias is bullish, trend strength ... — AGGRESSIVE LONG."
    # The stage that sets the action is gate 9, which chooses the tier, so
    # the summary is gate 9's sentence -- and that is the point of this
    # file: the summary names the reason belonging to whichever stage last
    # set the action, not the first or the last reason in the list.
    assert "passed every gate with entry quality" in summary, summary
    assert decision["final_action"] in summary, summary


# ======================================================================
# The EV sentence -- REMOVED at the redesign's stage 5, 15 November 2026
# ======================================================================
#
# Four tests stood here, on the illustrative expected value: that its
# sentence said it was confidence restated rather than a second reading of
# the setup, that the two confidence levels it quoted were derived from
# AVG_REWARD_R and EV_BREAKEVEN_BAND_R rather than written out by hand, that
# the breakeven band constant was live (moving it moved the verdict), and
# that ev_r was a straight line in confidence -- which is what made it
# unable to disagree with confidence, and in the end the reason it went.
#
# Ruling 6 of 25 October 2026 drops confidence and the EV line
# (DECISIONS, "Ruling, 25 October 2026 -- the indicator document's eight
# questions"); _compute_ev, _compute_confidence, AVG_REWARD_R and
# EV_BREAKEVEN_BAND_R are gone in this stage, so all four tests have no
# subject. test_the_ev_sentence_is_still_present_in_the_reasons went with
# them, from the section above: it held that the fix of 20 September moved
# which reason headed the summary WITHOUT removing the EV line from the
# reasoning, "a separate call Viktor has not made". He made it on
# 25 October.
