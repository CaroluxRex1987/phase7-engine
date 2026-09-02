"""
One direction source — found by running the engine, 2 September 2026.

WHAT HAPPENED

Viktor ran `python main.py` against live MEXC data on the evening Findings 6
and 7 landed. AEROUSDT 4h came back bearish on every measure the engine has:

    BIAS       : BEARISH CONFIRMED
    REGIME     : BEARISH TREND
    SEQUENCE   : BEARISH SWING SEQUENCE (LH-LL)
    VOLUME     : STRONG BEARISH DISTRIBUTION
    Exit Watch : SuperTrend flipped from BULLISH to BEARISH since the last run

with one dissenting reading, MACRO TREND: BULLISH. The engine printed:

    DECISION      : CONSERVATIVE LONG
    STOP LOSS     : $0.4889          (price was $0.4725 -- the stop is ABOVE)
    TARGET 1      : $0.4561
    TARGET 2      : $0.4397
    TARGET 3      : $0.4233          (all three BELOW price, descending)

A long label on a short plan. Every number in that plan was correctly
computed; the word attached to them was not.

THE TWO CAUSES

1. Three independent sources could each open a direction:

       if raw_bias == "BULLISH" or long_signal or macro_bias == "BULLISH":

   The macro clause alone was enough. `trend_health >= 50` then passed because
   trend health is an UNSIGNED magnitude -- a strong bearish trend scores 69 --
   so no bearish evidence anywhere in the run could block it. The bearish
   block below never ran, because the bullish one returned first. Whichever
   `if` is written first wins a disagreement.

2. Nothing compared the answer against the risk plan. risk_model builds stop
   and targets from `detailed_bias` alone (risk_model.py:84). Two direction
   sources, never reconciled.

It also printed "Bias is bullish and the broader macro trend agrees" while its
own Validation Notes said the higher timeframe DISAGREED -- two contradictory
claims in one panel, the first of them false.

VIKTOR'S RULING, 2 September: bias is the sole direction source. Macro keeps
its existing 10% vote inside bias_score and gets no second, overriding one --
letting it override the blend counts one piece of evidence twice, which is
Item 11 in the module that picks the side.

WHY THIS FILE IS NOT PART OF test_no_circular_reasoning.py

It is a decision-integrity defect that happens to have a circularity cause.
The property worth pinning is the one an operator depends on: the engine never
labels a plan with a direction the plan does not have.
"""

import math
import pytest

from models.decision_model import DecisionModel


# The live run, as close to the panel as the inputs allow.
BEARISH_BIAS = {"raw": "BEARISH", "detailed": "BEARISH CONFIRMED", "score": -61.72}
BEARISH_TREND = {"trend_health": 69.14, "trend_exhaustion": False,
                 "momentum_divergence": False, "trend_direction": "BEARISH"}
APPROACHING_ENTRY = {"score": 59.21, "entry_status": "APPROACHING ZONE",
                     "long_signal": True, "short_signal": False}
SHORT_PLAN = {"atr_stop": 0.4889, "targets": (0.4561, 0.4397, 0.4233),
              "risk_valid": True, "risk_regime": "HIGH VOLATILITY RISK",
              "validation_state": "NEUTRAL", "validation_score": 45.0}
LONG_PLAN = {"atr_stop": 0.45, "targets": (0.49, 0.51, 0.53),
             "risk_valid": True, "risk_regime": "NORMAL",
             "validation_state": "NEUTRAL", "validation_score": 45.0}


def _evaluate(bias, trend, entry, risk, macro_bias):
    return DecisionModel().evaluate(bias, trend, entry, risk,
                                    macro_bias=macro_bias, symbol="AEROUSDT")


# ============================================================
# The run itself
# ============================================================

def test_the_live_run_of_2_september_no_longer_returns_a_long():
    """The exact inputs that produced CONSERVATIVE LONG over a short plan."""
    out = _evaluate(BEARISH_BIAS, BEARISH_TREND, APPROACHING_ENTRY,
                    SHORT_PLAN, macro_bias="BULLISH")

    assert "LONG" not in out["final_action"], (
        f"the engine returned {out['final_action']} on a run whose bias, "
        f"regime, structure, sequence, volume and SuperTrend were all bearish, "
        f"because the macro read alone was bullish."
    )


def test_a_bullish_macro_cannot_open_a_direction_against_a_bearish_bias():
    """
    The specific clause: `or macro_bias == "BULLISH"`.

    Macro has already been counted once, as a 10% weighted factor inside
    bias_score. A second, overriding vote is the same evidence twice.
    """
    out = _evaluate(BEARISH_BIAS, BEARISH_TREND, APPROACHING_ENTRY,
                    SHORT_PLAN, macro_bias="BULLISH")
    assert "LONG" not in out["final_action"]


def test_a_bearish_macro_cannot_open_a_direction_against_a_bullish_bias():
    """The mirror. A defect fixed in one direction only is half fixed."""
    out = _evaluate({"raw": "BULLISH", "detailed": "BULLISH CONFIRMED", "score": 61.0},
                    {"trend_health": 69.0, "trend_exhaustion": False,
                     "momentum_divergence": False, "trend_direction": "BULLISH"},
                    {"score": 59.0, "entry_status": "APPROACHING ZONE",
                     "long_signal": False, "short_signal": True},
                    LONG_PLAN, macro_bias="BEARISH")
    assert "SHORT" not in out["final_action"]


def test_an_entry_zone_signal_cannot_open_a_direction_on_its_own():
    """
    `long_signal` was the third source in the same `or` chain, and it is the
    same defect wearing a different name: an entry-zone reading that can pick
    a side against the engine's own bias. A NEUTRAL bias means the engine has
    no directional view, and an entry signal is not one.
    """
    out = _evaluate({"raw": "NEUTRAL", "detailed": "NEUTRAL", "score": 5.0},
                    {"trend_health": 80.0, "trend_exhaustion": False,
                     "momentum_divergence": False, "trend_direction": "NEUTRAL"},
                    {"score": 85.0, "entry_status": "ACTIVE ZONE",
                     "long_signal": True, "short_signal": False},
                    LONG_PLAN, macro_bias="NEUTRAL")
    assert not any(side in out["final_action"] for side in ("LONG", "SHORT")), (
        f"a neutral bias with a long entry signal produced "
        f"{out['final_action']}. The direction came from the entry zone."
    )


# ============================================================
# The guard — for the disagreement nobody predicted
# ============================================================

def test_a_long_label_on_a_short_plan_is_refused():
    """
    Narrowing the direction source stops the two modules disagreeing for the
    reason they disagreed on 2 September. It cannot stop them disagreeing for
    a reason nobody has thought of, and the cost of that class is not a wrong
    number on a panel -- it is an operator taking the opposite side of the
    analysis.
    """
    reasons = []
    action = DecisionModel()._refuse_incoherent_plan(
        "CONSERVATIVE LONG", SHORT_PLAN, reasons)

    assert action == "NO-TRADE (PLAN CONTRADICTS ACTION)"
    assert reasons and "REFUSED" in reasons[0]


def test_a_short_label_on_a_long_plan_is_refused():
    reasons = []
    action = DecisionModel()._refuse_incoherent_plan(
        "AGGRESSIVE SHORT", LONG_PLAN, reasons)
    assert action == "NO-TRADE (PLAN CONTRADICTS ACTION)"


def test_the_guard_reads_the_plan_and_not_the_bias():
    """
    A check that asks the same source the action asked cannot detect the two
    disagreeing. Direction is read off the targets themselves.
    """
    dm = DecisionModel()
    assert dm._plan_direction({"targets": (1.0, 2.0, 3.0)}) == "LONG"
    assert dm._plan_direction({"targets": (3.0, 2.0, 1.0)}) == "SHORT"
    # A bias field in the dict must not influence the reading.
    assert dm._plan_direction(
        {"targets": (3.0, 2.0, 1.0), "detailed_bias": "BULLISH CONFIRMED"}) == "SHORT"


def test_the_guard_does_not_fire_on_coherent_plans():
    """
    A guard that refuses good runs gets switched off, and then it is not a
    guard.
    """
    dm = DecisionModel()
    for action, plan in (("LONG", LONG_PLAN), ("AGGRESSIVE LONG", LONG_PLAN),
                         ("SHORT", SHORT_PLAN), ("CONSERVATIVE SHORT", SHORT_PLAN)):
        reasons = []
        assert dm._refuse_incoherent_plan(action, plan, reasons) == action
        assert not reasons


def test_the_guard_is_silent_when_there_is_no_plan_to_read():
    """
    A degraded run, or one with no ATR, has no levels. That is a normal state
    and not a contradiction -- refusing it here would turn a missing input
    into a false accusation.
    """
    dm = DecisionModel()
    for plan in ({}, {"targets": ()}, {"targets": (float("nan"),) * 3},
                 {"targets": ("x", "y", "z")}, {"targets": (1.0, 1.0, 1.0)}):
        reasons = []
        assert dm._refuse_incoherent_plan("LONG", plan, reasons) == "LONG"
        assert not reasons


def test_a_no_trade_action_is_left_alone():
    """WAIT and NO-TRADE claim no direction, so there is nothing to contradict."""
    dm = DecisionModel()
    for action in ("WAIT", "NO-TRADE (RISK TOO HIGH)", "NO-TRADE (DEGRADED INPUT)"):
        reasons = []
        assert dm._refuse_incoherent_plan(action, SHORT_PLAN, reasons) == action
        assert not reasons


# ============================================================
# The claim the panel makes must be true
# ============================================================

def test_the_stated_reason_never_calls_a_bearish_bias_bullish():
    """
    The run printed "Bias is bullish and the broader macro trend agrees" while
    its own Validation Notes said the higher timeframe disagreed. Item 8's
    class -- an engine asserting something that is not so -- in the sentence
    the operator reads first.
    """
    out = _evaluate(BEARISH_BIAS, BEARISH_TREND, APPROACHING_ENTRY,
                    SHORT_PLAN, macro_bias="BULLISH")
    joined = " ".join(out["explanation"]["reasons"]).lower()
    assert "bias is bullish" not in joined, (
        "the explanation calls the bias bullish on a run whose bias is "
        "BEARISH CONFIRMED."
    )


def test_a_genuine_bullish_run_still_reaches_a_long():
    """
    The control. A fix that stops the engine ever taking a side would pass
    every test above and be worthless.
    """
    out = _evaluate({"raw": "BULLISH", "detailed": "BULLISH CONFIRMED", "score": 78.0},
                    {"trend_health": 80.0, "trend_exhaustion": False,
                     "momentum_divergence": False, "trend_direction": "BULLISH"},
                    {"score": 75.0, "entry_status": "ACTIVE ZONE",
                     "long_signal": True, "short_signal": False},
                    LONG_PLAN, macro_bias="BULLISH")
    assert "LONG" in out["final_action"], (
        f"a bullish bias with strong trend health, a high-quality active "
        f"entry, an agreeing macro and a long plan produced "
        f"{out['final_action']}."
    )


def test_a_genuine_bearish_run_still_reaches_a_short():
    out = _evaluate({"raw": "BEARISH", "detailed": "BEARISH CONFIRMED", "score": -78.0},
                    {"trend_health": 80.0, "trend_exhaustion": False,
                     "momentum_divergence": False, "trend_direction": "BEARISH"},
                    {"score": 75.0, "entry_status": "ACTIVE ZONE",
                     "long_signal": False, "short_signal": True},
                    SHORT_PLAN, macro_bias="BEARISH")
    assert "SHORT" in out["final_action"], (
        f"a bearish bias with strong trend health, a high-quality active "
        f"entry, an agreeing macro and a short plan produced "
        f"{out['final_action']}."
    )
