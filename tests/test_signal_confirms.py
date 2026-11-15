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

Fix 2, 5 October 2026: the exhaustion flag left the gate and ADX under 20
blocks both sides in its place (round 8's triage, point 4). The helpers below
pass a trending ADX of 30 unless a test sets it; the fix's own cases are in
tests/test_no_trend_no_trade.py.

The redesign's stage 3, 15 November 2026: gates 6 and 7 join the signal --
no LONG under a bearish daily trend (Viktor's ruling of 25 October, point 3)
and the liquidity floor (his ruling of 31 October) -- and gate 8, the
trigger, follows it. The helpers below pass a NEUTRAL daily trend, a turnover
over the floor and a trigger that holds unless a test sets them, so each
test here still moves only what it names; the three gates' own cases are in
tests/test_gates_6_to_8.py. test_an_opposing_macro_does_not_block_a_confirmed_trade
held work order G's removal of macro from the signal and is turned round
(the draft's section 14, one of its two X): it is now
test_an_opposing_macro_blocks_a_long_and_not_a_short.

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


# Gates 6 and 7 passing, for the direct calls below that test gates 3 to 5.
PASSES = {"macro_bias": "NEUTRAL", "quote_volume": 50_000.0}

# Gate 8 passing: a resumption candle with volume over its median.
TRIGGERED = {"trigger": True, "trigger_volume": 2.0, "trigger_volume_median": 1.0}


def _signals(structure="BULLISH TREND", adx=30.0,
             divergence=False, divergence_direction="NONE",
             macro="NEUTRAL", quote_volume=50_000.0):
    return generate_entry_signals(
        structure_regime=structure,
        momentum_divergence=divergence,
        divergence_direction=divergence_direction,
        adx=adx,
        macro_bias=macro,
        quote_volume=quote_volume,
    )


def _evaluate(raw="BULLISH", score=78.0, health=90.0, entry_score=80.0,
              status="ACTIVE ENTRY ZONE", risk_valid=True,
              signals=None, degradation=None, trend_divergence=False):
    """
    A full DecisionModel.evaluate() -- the ladder AND the gate after it.
    `trend_divergence` sets the trend block's own momentum_divergence flag,
    so a divergence test shows the same fact to the ladder and to the gate,
    as the engine does.
    """
    entry = {"score": entry_score, "entry_status": status, **TRIGGERED}
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
        # Work order G, 27 September 2026: evaluate() no longer takes
        # macro_bias; the `macro` parameter this helper had is gone with it.
        degradation=degradation,
    )


# --- the signal itself ----------------------------------------------------

def test_the_signal_no_longer_takes_the_inputs_that_were_ruled_out():
    """
    CONFIRMED (a second bias threshold), trend health (decided nothing) and
    the reversal NUMBER (replaced by its parts) are not inputs any more --
    nor, since fix 2, the exhaustion flag (ADX replaced it). Re-adding one
    as a parameter fails here, before it can quietly start vetoing trades
    again.

    Macro was on this list from work order F until the redesign's stage 3:
    it was counted twice then, inside bias_score and in the signal. The
    direction no longer reads it (stage 2), and Viktor's ruling of
    25 October, point 3, makes it a gate on LONG, so it is an input again --
    keyword-only and with no default, like the turnover gate 7 reads, so a
    call that leaves either out is refused.
    """
    for fn in (signal_blockers, generate_entry_signals):
        signature = inspect.signature(fn)
        params = set(signature.parameters)
        for gone in ("detailed_bias", "trend_health",
                     "reversal_strength", "trend_exhaustion"):
            assert gone not in params, (
                f"{fn.__name__} takes {gone} again. Work order F removed it; "
                f"see the comment above generate_entry_signals.")
        for required in ("macro_bias", "quote_volume"):
            parameter = signature.parameters[required]
            assert parameter.kind is inspect.Parameter.KEYWORD_ONLY, required
            assert parameter.default is inspect.Parameter.empty, required


def test_a_clean_bullish_setup_confirms_the_long_and_not_the_short():
    out = _signals()
    assert out["long_signal"] is True and out["long_signal_blockers"] == []
    assert out["short_signal"] is False
    assert out["short_signal_blockers"] == [
        "structure is BULLISH TREND, not BEARISH TREND"]


def test_each_side_signal_is_exactly_an_empty_blocker_list():
    for kwargs in ({}, {"structure": "BEARISH TREND"},
                   {"structure": "NEUTRAL STRUCTURE"}, {"adx": 15.0},
                   {"adx": None},
                   {"divergence": True, "divergence_direction": "BEARISH"},
                   {"divergence": True, "divergence_direction": "BULLISH"}):
        out = _signals(**kwargs)
        for side in ("long", "short"):
            assert out[f"{side}_signal"] == (out[f"{side}_signal_blockers"] == []), kwargs


def test_structure_against_the_side_blocks_it():
    assert "structure is BEARISH TREND, not BULLISH TREND" in signal_blockers(
        "LONG", "BEARISH TREND", False, "NONE", adx=30.0, **PASSES)
    assert "structure is NEUTRAL STRUCTURE, not BEARISH TREND" in signal_blockers(
        "SHORT", "NEUTRAL STRUCTURE", False, "NONE", adx=30.0, **PASSES)


def test_adx_under_20_blocks_both_sides():
    """Fix 2: no trend, no trade. It replaced the exhaustion flag here."""
    for side, structure in (("LONG", "BULLISH TREND"), ("SHORT", "BEARISH TREND")):
        assert signal_blockers(side, structure, False, "NONE", adx=15.0, **PASSES) == [
            "ADX is 15.0, under the 20 the engine requires to treat the "
            "market as trending"]


def test_a_divergence_against_the_trade_blocks_it():
    # B4's labels, 14 October 2026: the sentence says what is compared.
    assert signal_blockers("LONG", "BULLISH TREND", True, "BEARISH", adx=30.0, **PASSES) == [
        "a bearish price/RSI disagreement over four candles points against "
        "the trade"]
    assert signal_blockers("SHORT", "BEARISH TREND", True, "BULLISH", adx=30.0, **PASSES) == [
        "a bullish price/RSI disagreement over four candles points against "
        "the trade"]


def test_a_divergence_pointing_with_the_trade_does_not_block_it():
    """Viktor's rule 2: only a counter-directional reversal is a threat."""
    assert signal_blockers("LONG", "BULLISH TREND", True, "BULLISH", adx=30.0, **PASSES) == []
    assert signal_blockers("SHORT", "BEARISH TREND", True, "BEARISH", adx=30.0, **PASSES) == []


def test_a_divergence_of_unrecorded_direction_is_not_a_confirmation():
    """It cannot be shown not to point against the trade."""
    for direction in ("NONE", "UNKNOWN", None):
        blockers = signal_blockers("LONG", "BULLISH TREND", True, direction, adx=30.0, **PASSES)
        assert len(blockers) == 1 and "cannot be shown" in blockers[0], direction


# --- the gate in DecisionModel.evaluate() -----------------------------------

def test_a_confirmed_long_is_still_taken():
    """The control: a gate that refused everything would pass the rest."""
    out = _evaluate(signals=_signals())
    assert out["final_action"] == "AGGRESSIVE LONG", out["explanation"]
    assert any(r.startswith("Structural confirmation holds for the long")
               for r in out["explanation"]["reasons"])


def test_a_confirmed_short_is_still_taken():
    out = _evaluate(raw="BEARISH",
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
    all. Trend health 60 and entry 40 is CONSERVATIVE LONG on the ladder (it
    also needed an agreeing macro until work order G); a bearish divergence
    now refuses it.
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
            reasons=[]))
    assert actions == ["AGGRESSIVE LONG", "AGGRESSIVE LONG"], actions


def test_an_opposing_macro_blocks_a_long_and_not_a_short():
    """
    TURNED ROUND at the redesign's stage 3 (the draft's section 14, X). As
    test_an_opposing_macro_does_not_block_a_confirmed_trade this held work
    order G: macro was out of the signal and voted inside bias_score, so a
    bearish daily trend left an AGGRESSIVE LONG standing. Macro no longer
    votes in the direction, and by Viktor's ruling of 25 October, point 3,
    no LONG is taken while the daily trend is bearish. That is the ruling's
    consequence, not a new rule. A SHORT is not gated by macro.

    Through the router, as before, so the exact-action assertion cannot pass
    on the router's error record, which has no "exit".
    """
    from models.signal_router import SignalRouter

    def routed(raw, structure, macro, targets):
        entry = {"score": 80.0, "entry_status": "ACTIVE ENTRY ZONE",
                 "score_clipped": False, **TRIGGERED,
                 **_signals(structure=structure, macro=macro)}
        sign = 1 if raw == "BULLISH" else -1
        return SignalRouter(engine_core=object())._build_decision_object(
            symbol="TESTUSDT", timeframe="4h",
            bias={"raw": raw, "score": 78.0 * sign},
            trend={"trend_health": 90.0, "trend_direction_sign": sign,
                   "trend_exhaustion": False, "momentum_divergence": False},
            structure={}, entry=entry,
            risk={"risk_valid": True, "risk_reason": "OK",
                  "risk_regime": "NORMAL RISK", "validation_state": "NEUTRAL",
                  "targets": targets},
            exit_data={"current_price": 1.0},
            macro_bias=macro, chart_path="",
        )

    long_against = routed("BULLISH", "BULLISH TREND", "BEARISH", [1.1, 1.2, 1.3])
    assert long_against["exit"]["action"] == "NO-TRADE (MACRO AGAINST)", (
        long_against["explanation"])
    assert long_against["macro_bias"] == "BEARISH"
    assert long_against["entry"]["long_signal_refusal"] == "NO-TRADE (MACRO AGAINST)"

    # The controls: the same long under a daily trend that is not bearish,
    # and a short under a bullish one.
    for macro in ("BULLISH", "NEUTRAL"):
        out = routed("BULLISH", "BULLISH TREND", macro, [1.1, 1.2, 1.3])
        assert out["exit"]["action"] == "AGGRESSIVE LONG", (macro, out["explanation"])
    short = routed("BEARISH", "BEARISH TREND", "BULLISH", [0.9, 0.8, 0.7])
    assert short["exit"]["action"] == "AGGRESSIVE SHORT", short["explanation"]


def test_a_missing_signal_record_fails_safe():
    out = _evaluate(signals=None)
    assert out["final_action"] == UNCONFIRMED
    assert any("was not computed on this run" in r
               for r in out["explanation"]["reasons"])


def test_a_signal_contradicting_its_own_blockers_is_not_a_confirmation():
    bad = _signals()
    bad["long_signal_blockers"] = ["structure is BEARISH TREND, not BULLISH TREND"]
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
