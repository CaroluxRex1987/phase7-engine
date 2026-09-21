"""
Work order F, 21 September 2026 -- the entry signals CONFIRM the side the
decision ladder chooses.

Finding 11 of the 21 September pre-backtest review: long_signal and
short_signal were computed every run, recorded in the decision object, the
log and the simulated order, and read by nothing that decides. Viktor ruled
that they confirm (option 2 of three), wrote the conditions first, and
delegated the remaining adjustments. The rule is documented above
generate_entry_signals in models/entry_model.py; the gate is
DecisionModel._apply_signal_gate.

Every test here is fixture-free on purpose: run_tests.py calls each test_*
function with no arguments, and a fixture would become an error there.

The entry records in the decision tests are built by the engine's own
generate_entry_signals, not written by hand, so the two modules are tested
together: a record shape one produces and the other misreads would fail here.
"""

import inspect
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.decision_model import DecisionModel
from models.entry_model import generate_entry_signals, signal_blockers

UNCONFIRMED = "NO-TRADE (SIGNAL UNCONFIRMED)"


def _signals(structure="BULLISH TREND", exhaustion=False,
             divergence=False, divergence_direction="NONE"):
    return generate_entry_signals(
        structure_regime=structure,
        trend_exhaustion=exhaustion,
        momentum_divergence=divergence,
        divergence_direction=divergence_direction,
    )


def _evaluate(raw="BULLISH", score=78.0, health=90.0, entry_score=80.0,
              status="ACTIVE ENTRY ZONE", macro="BULLISH", risk_valid=True,
              signals=None, degradation=None, trend_divergence=False):
    """
    A full DecisionModel.evaluate() -- the ladder AND the gate after it.
    `trend_divergence` sets the trend block's own momentum_divergence flag,
    so a divergence test shows the same fact to the ladder and to the gate,
    as the engine does.
    """
    entry = {"score": entry_score, "entry_status": status}
    if signals is not None:
        entry.update(signals)
    long_plan = raw != "BEARISH"
    return DecisionModel().evaluate(
        bias={"raw": raw, "score": score if long_plan else -abs(score)},
        trend={"trend_health": health,
               "trend_direction_sign": 1 if long_plan else -1,
               "momentum_divergence": trend_divergence},
        entry=entry,
        risk={"risk_valid": risk_valid,
              "risk_reason": "Stop distance exceeds maximum allowable threshold (15%).",
              "risk_regime": "NORMAL RISK",
              "validation_state": "NEUTRAL",
              "targets": [1.1, 1.2, 1.3] if long_plan else [0.9, 0.8, 0.7]},
        macro_bias=macro,
        degradation=degradation,
    )


# --- the signal itself ----------------------------------------------------

def test_the_signal_no_longer_takes_the_inputs_that_were_ruled_out():
    """
    Macro (counted twice), CONFIRMED (a second bias threshold), trend health
    (decided nothing) and the reversal NUMBER (replaced by its parts) are not
    inputs any more. Re-adding one as a parameter fails here, before it can
    quietly start vetoing trades again.
    """
    for fn in (signal_blockers, generate_entry_signals):
        params = set(inspect.signature(fn).parameters)
        for gone in ("macro_bias", "detailed_bias", "trend_health",
                     "reversal_strength"):
            assert gone not in params, (
                f"{fn.__name__} takes {gone} again. Work order F removed it; "
                f"see the comment above generate_entry_signals.")


def test_a_clean_bullish_setup_confirms_the_long_and_not_the_short():
    out = _signals()
    assert out["long_signal"] is True and out["long_signal_blockers"] == []
    assert out["short_signal"] is False
    assert out["short_signal_blockers"] == [
        "structure is BULLISH TREND, not BEARISH TREND"]


def test_each_side_signal_is_exactly_an_empty_blocker_list():
    for kwargs in ({}, {"structure": "BEARISH TREND"},
                   {"structure": "NEUTRAL STRUCTURE"}, {"exhaustion": True},
                   {"divergence": True, "divergence_direction": "BEARISH"},
                   {"divergence": True, "divergence_direction": "BULLISH"}):
        out = _signals(**kwargs)
        for side in ("long", "short"):
            assert out[f"{side}_signal"] == (out[f"{side}_signal_blockers"] == []), kwargs


def test_structure_against_the_side_blocks_it():
    assert "structure is BEARISH TREND, not BULLISH TREND" in signal_blockers(
        "LONG", "BEARISH TREND", False, False, "NONE")
    assert "structure is NEUTRAL STRUCTURE, not BEARISH TREND" in signal_blockers(
        "SHORT", "NEUTRAL STRUCTURE", False, False, "NONE")


def test_exhaustion_blocks_both_sides():
    for side, structure in (("LONG", "BULLISH TREND"), ("SHORT", "BEARISH TREND")):
        assert signal_blockers(side, structure, True, False, "NONE") == [
            "the trend is flagged exhausted"]


def test_a_divergence_against_the_trade_blocks_it():
    assert signal_blockers("LONG", "BULLISH TREND", False, True, "BEARISH") == [
        "bearish momentum divergence points against the trade"]
    assert signal_blockers("SHORT", "BEARISH TREND", False, True, "BULLISH") == [
        "bullish momentum divergence points against the trade"]


def test_a_divergence_pointing_with_the_trade_does_not_block_it():
    """Viktor's rule 2: only a counter-directional reversal is a threat."""
    assert signal_blockers("LONG", "BULLISH TREND", False, True, "BULLISH") == []
    assert signal_blockers("SHORT", "BEARISH TREND", False, True, "BEARISH") == []


def test_a_divergence_of_unrecorded_direction_is_not_a_confirmation():
    """It cannot be shown not to point against the trade."""
    for direction in ("NONE", "UNKNOWN", None):
        blockers = signal_blockers("LONG", "BULLISH TREND", False, True, direction)
        assert len(blockers) == 1 and "cannot be shown" in blockers[0], direction


# --- the gate in DecisionModel.evaluate() -----------------------------------

def test_a_confirmed_long_is_still_taken():
    """The control: a gate that refused everything would pass the rest."""
    out = _evaluate(signals=_signals())
    assert out["final_action"] == "AGGRESSIVE LONG", out["explanation"]
    assert any(r.startswith("Structural confirmation holds for the long")
               for r in out["explanation"]["reasons"])


def test_a_confirmed_short_is_still_taken():
    out = _evaluate(raw="BEARISH", macro="BEARISH",
                    signals=_signals(structure="BEARISH TREND"))
    assert out["final_action"] == "AGGRESSIVE SHORT", out["explanation"]


def test_an_unconfirmed_long_becomes_no_trade_and_says_why():
    out = _evaluate(signals=_signals(structure="BEARISH TREND"))
    assert out["final_action"] == UNCONFIRMED
    reason = ("This would have been AGGRESSIVE LONG, but the bullish bias lacked "
              "structural confirmation (structure is BEARISH TREND, not BULLISH "
              "TREND), so no trade is taken.")
    assert reason in out["explanation"]["reasons"]
    assert out["explanation"]["summary"] == f"{UNCONFIRMED} — {reason}", (
        "the summary must name the gate's reason, not the ladder's")


def test_a_counter_divergence_now_blocks_a_conservative_trade():
    """
    Before work order F the CONSERVATIVE branch had no divergence check at
    all. Trend health 60 and entry 40 with an agreeing macro is CONSERVATIVE
    LONG on the ladder; a bearish divergence now refuses it.
    """
    clean = _evaluate(health=60.0, entry_score=40.0, signals=_signals())
    assert clean["final_action"] == "CONSERVATIVE LONG", clean["explanation"]
    diverged = _evaluate(health=60.0, entry_score=40.0, trend_divergence=True,
                         signals=_signals(divergence=True, divergence_direction="BEARISH"))
    assert diverged["final_action"] == UNCONFIRMED


def test_a_counter_divergence_refuses_an_upper_tier_trade_instead_of_demoting_it():
    """
    Predicted consequence, recorded in the commit: the ladder's own
    direction-blind check used to demote this to CONSERVATIVE LONG. There is
    one divergence rule now, and it refuses.
    """
    out = _evaluate(trend_divergence=True,
                    signals=_signals(divergence=True, divergence_direction="BEARISH"))
    assert out["final_action"] == UNCONFIRMED


def test_a_divergence_pointing_with_the_trade_no_longer_demotes_it():
    """The other half of the same consequence."""
    out = _evaluate(trend_divergence=True,
                    signals=_signals(divergence=True, divergence_direction="BULLISH"))
    assert out["final_action"] == "AGGRESSIVE LONG", out["explanation"]


def test_the_ladder_no_longer_reads_divergence_at_all():
    """
    One rule, in one place. _determine_final_action alone -- no gate --
    returns the same action with and without a divergence flag in the trend.
    """
    dm = DecisionModel()
    actions = []
    for divergence in (False, True):
        actions.append(dm._determine_final_action(
            bias={"raw": "BULLISH", "score": 78.0},
            trend={"trend_health": 90.0, "trend_direction_sign": 1,
                   "momentum_divergence": divergence},
            entry={"score": 80.0, "entry_status": "ACTIVE ENTRY ZONE"},
            risk={"risk_valid": True, "risk_regime": "NORMAL RISK",
                  "validation_state": "NEUTRAL"},
            macro_bias="BULLISH", reasons=[]))
    assert actions == ["AGGRESSIVE LONG", "AGGRESSIVE LONG"], actions


def test_an_opposing_macro_does_not_block_a_confirmed_trade():
    """Macro was removed from the signal; it still votes inside bias_score."""
    out = _evaluate(macro="BEARISH", signals=_signals())
    assert out["final_action"] == "AGGRESSIVE LONG", out["explanation"]


def test_a_missing_signal_record_fails_safe():
    out = _evaluate(signals=None)
    assert out["final_action"] == UNCONFIRMED
    assert any("was not computed on this run" in r
               for r in out["explanation"]["reasons"])


def test_a_signal_contradicting_its_own_blockers_is_not_a_confirmation():
    bad = _signals()
    bad["long_signal_blockers"] = ["the trend is flagged exhausted"]
    out = _evaluate(signals=bad)
    assert out["final_action"] == UNCONFIRMED
    assert any("contradicts its own blocker list" in r
               for r in out["explanation"]["reasons"])


def test_risk_refusal_keeps_the_label_and_records_the_signal_failure_too():
    """Viktor's priority ruling: risk first, both failures in the log."""
    out = _evaluate(risk_valid=False, signals=_signals(structure="BEARISH TREND"))
    assert out["final_action"] == "NO-TRADE (RISK TOO HIGH)"
    reasons = out["explanation"]["reasons"]
    assert reasons[0].startswith("Risk check failed")
    assert reasons[1] == (
        "Separately, the bullish bias also lacked structural confirmation "
        "(structure is BEARISH TREND, not BULLISH TREND). The risk refusal is "
        "the label; this is recorded so the log shows both failures.")
    assert out["explanation"]["summary"].startswith(
        "NO-TRADE (RISK TOO HIGH) — Risk check failed")


def test_risk_refusal_with_a_confirmed_signal_adds_nothing():
    out = _evaluate(risk_valid=False, signals=_signals())
    assert not any(r.startswith("Separately")
                   for r in out["explanation"]["reasons"])


def test_a_degraded_run_keeps_the_signal_refusal_as_its_label():
    """
    Degradation only overrides actions naming a side, so an unconfirmed
    trade on a degraded run stays NO-TRADE (SIGNAL UNCONFIRMED), with the
    degradation notes appended rather than replacing the label.
    """
    out = _evaluate(signals=_signals(structure="BEARISH TREND"),
                    degradation=["RSI unavailable"])
    assert out["final_action"] == UNCONFIRMED
    assert any("DEGRADED" in r for r in out["explanation"]["reasons"])
