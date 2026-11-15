"""
Work order G, 27 September 2026 (finding 17): macro no longer decides the
CONSERVATIVE tier.

WHAT WAS WRONG

models/decision_model.py's ladder read, in both CONSERVATIVE branches,

    elif trend_health >= self.CONSERVATIVE_TREND_HEALTH_MIN and macro_bias == "BULLISH":

(and "BEARISH" on the short side). Macro is already a 10% factor inside
bias_score. A hard requirement on it here counted the same evidence a second
time -- the double count Viktor removed from direction on 2 September and
from the entry signal at work order F. The two upper tiers never had the
condition; only the tier with the weakest case did. A directional bias at
CONSERVATIVE strength with a disagreeing or neutral macro came out WAIT.

THE CHANGE -- Claude's call under Viktor's delegation

The condition is gone, and so is the macro_bias parameter it was the only
reader of, from _determine_final_action and from evaluate(). The router still
takes macro_bias and records it in the decision object. Everything after
`risk` in evaluate() is keyword-only, so a caller still passing macro in
fifth place fails loudly instead of the string landing in btc_context.

WHAT THESE TESTS HOLD

The behavioural tests go through SignalRouter._build_decision_object, the one
place the engine still receives a macro reading. That path exists before and
after the change, so against the pre-G code these fail by assertion (WAIT
where CONSERVATIVE is expected), not by a TypeError. The router returns an
error record with no "exit" when assembly fails, so every exact-action
assertion here raises on a failed build rather than passing.

THE REDESIGN'S STAGE 3, 15 November 2026 -- macro is a gate on LONG

Viktor's ruling of 25 October, point 3: no LONG while the daily trend is
bearish. Macro no longer votes in the direction (stage 2), so the gate is
not a second count of it. It sits with the confirmation signal
(models/entry_model.py, gate 6), and the decision model still takes no macro
parameter. So test_a_conservative_long_does_not_depend_on_macro, which held
G's removal for the long side, is TURNED ROUND (the draft's section 14, one
of its two X). That is the ruling's consequence, not a new rule. The short
side's test holds as it was: SHORT is not gated by macro.

THE REDESIGN'S STAGE 4, 15 November 2026 -- the tier comes from entry quality

Three of this file's tests held the CONSERVATIVE SENTENCE naming which of
two lines a setup fell short of -- trend health's 75 or entry quality's 70
-- written on 21 September because the sentence had blamed the wrong one.
There is one line to name now, so there is no attribution to get wrong:
test_trend_short_is_named_and_entry_is_not_blamed, test_both_short_are_named
and test_the_sentence_names_the_bias_side_and_the_trend_direction GO with
_conservative_reason's two-line sentence, and
test_entry_short_is_named_and_trend_is_not_blamed is rewritten as
test_the_conservative_sentence_names_the_two_quality_lines. The tier the
runs below reach is set by the entry quality they are given, not by the
trend health, which the ladder no longer reads.

What this file still holds, and the reason it is worth keeping: macro's
ONLY effect on a tier is gate 6, on the long side. Every test below moves
macro and nothing else.

No fixtures and no pytest import: run_tests.py calls each test with no
arguments.
"""

import inspect
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.decision_model import DecisionModel
from models.entry_model import generate_entry_signals
from models.signal_router import SignalRouter

MACROS = ("BULLISH", "BEARISH", "NEUTRAL")
UPPER_MIN = DecisionModel.UPPER_TIER_ENTRY_QUALITY_MIN
CONSERVATIVE_MIN = DecisionModel.CONSERVATIVE_ENTRY_QUALITY_MIN


def _confirmed(side, macro="NEUTRAL"):
    """
    A complete signal record for `side` under the daily trend `macro`, as
    the engine computes it: structure agreeing with the side, a trending
    ADX, no divergence, a turnover over the floor -- and a trigger that
    holds. Under any macro but a bearish one on the long side, every gate
    up to 8 passes.
    """
    structure = "BULLISH TREND" if side == "long" else "BEARISH TREND"
    record = generate_entry_signals(
        structure_regime=structure, momentum_divergence=False,
        divergence_direction="NONE", adx=30.0,
        macro_bias=macro, quote_volume=50_000.0)
    record.update(trigger=True, trigger_volume=2.0, trigger_volume_median=1.0)
    return record


# 13 OCTOBER 2026, the fallback sweep (DECISIONS, "Ruling, 13 October 2026
# -- the fallback sweep"): the router reads these directly now, where it
# used to default each to False when absent. They are supplied here with
# exactly those values, so the record these tests read is the one they read
# before. False beside an absent blocker list is still "not computed" to the
# decision model's signal gate, as an absent signal was. score_clipped left
# the list with the redesign's stage 4.
ROUTER_READS_TREND = {"trend_exhaustion": False, "momentum_divergence": False}
ROUTER_READS_ENTRY = {"long_signal": False, "short_signal": False}


def _route(side, macro, health=60.0, entry_score=60.0, score=60.0,
           inside=False):
    """
    One run through the router. side is "long" or "short".

    `entry_score` is what sets the tier from stage 4 on: 60 is between the
    two lines, so the default reaches CONSERVATIVE. `health` is still passed
    because the router records it and the panel prints it; no gate reads it.
    """
    long_side = side == "long"
    out = SignalRouter(engine_core=object())._build_decision_object(
        symbol="TESTUSDT", timeframe="4h",
        bias={"raw": "BULLISH" if long_side else "BEARISH",
              "score": score if long_side else -score},
        trend={**ROUTER_READS_TREND, "trend_health": health,
               "trend_direction_sign": 1 if long_side else -1,
               "momentum_divergence": False},
        structure={},
        entry={**ROUTER_READS_ENTRY, "score": entry_score,
               "close_inside_band": inside,
               "entry_status": "INSIDE THE BAND" if inside else "ABOVE THE BAND",
               **_confirmed(side, macro)},
        risk={"risk_valid": True, "risk_reason": "OK",
              "risk_regime": "NORMAL RISK", "validation_state": "NEUTRAL",
              "targets": [1.1, 1.2, 1.3] if long_side else [0.9, 0.8, 0.7]},
        exit_data={"current_price": 1.0},
        macro_bias=macro, chart_path="",
    )
    return out


def _tier_reason(out):
    """The one sentence gate 9 wrote, whichever tier it chose."""
    reasons = [r for r in out["explanation"]["reasons"]
               if r.endswith(" LONG.") or r.endswith(" SHORT.")]
    assert len(reasons) == 1, out["explanation"]["reasons"]
    return reasons[0]


# --- the tier no longer depends on macro -------------------------------------

def test_a_conservative_long_is_refused_under_a_bearish_daily_trend_and_no_other():
    """
    Turned round at the redesign's stage 3 (see the module docstring). A
    bullish or neutral daily trend leaves the tier as work order G left it;
    a bearish one refuses the long, with gate 6's own label and reason.
    """
    for macro in ("BULLISH", "NEUTRAL"):
        out = _route("long", macro)
        assert out["exit"]["action"] == "CONSERVATIVE LONG", (
            f"macro {macro}: {out['exit']['action']} -- "
            f"{out['explanation']['reasons']}")
    out = _route("long", "BEARISH")
    assert out["exit"]["action"] == "NO-TRADE (MACRO AGAINST)", (
        out["exit"]["action"], out["explanation"]["reasons"])
    # Stage 4: the refusal names no tier. It read "This would have been
    # CONSERVATIVE LONG, but ..." until the tier moved to gate 9, after
    # this gate, where there is no tier yet to name.
    assert out["explanation"]["summary"] == (
        "NO-TRADE (MACRO AGAINST) — No earlier gate refused the long, "
        "but the daily trend is BEARISH, and no long is taken while the "
        "daily trend is bearish, so no trade is taken."), out["explanation"]


def test_a_conservative_short_does_not_depend_on_macro():
    for macro in MACROS:
        out = _route("short", macro)
        assert out["exit"]["action"] == "CONSERVATIVE SHORT", (
            f"macro {macro}: {out['exit']['action']} -- "
            f"{out['explanation']['reasons']}")


def test_the_record_still_carries_the_macro_reading():
    """Removed from the decision, not from the record."""
    for macro in MACROS:
        assert _route("long", macro)["macro_bias"] == macro


def test_negative_control_below_the_conservative_line_still_waits():
    """
    Without this, the two tests above would pass on a ladder that returned
    CONSERVATIVE for everything.

    Stage 4: the line is entry quality's, not trend health's. The trend
    health is left at its default, which is well above the 50 the old line
    used, so a run that waits here waits on the quality.
    """
    below = CONSERVATIVE_MIN - 1.0
    for side in ("long", "short"):
        for macro in MACROS:
            out = _route(side, macro, entry_score=below)
            expected = ("NO-TRADE (MACRO AGAINST)"
                        if side == "long" and macro == "BEARISH" else "WAIT")
            assert out["exit"]["action"] == expected, (
                f"{side}, macro {macro}, entry quality {below}: "
                f"{out['exit']['action']}")


# --- the decision model cannot receive macro --------------------------------

def test_the_decision_model_takes_no_macro_parameter():
    for fn in (DecisionModel.evaluate, DecisionModel._determine_final_action):
        params = [p for p in inspect.signature(fn).parameters if "macro" in p]
        assert not params, (
            f"{fn.__name__} takes {params} again. Work order G removed "
            f"macro_bias from the decision model; see _determine_final_action.")


def test_a_fifth_positional_argument_is_refused():
    """
    Before G the fifth positional slot was macro_bias. A caller still passing
    macro there must fail, not have "BULLISH" read as btc_context.
    """
    try:
        DecisionModel().evaluate(
            {"raw": "BULLISH", "score": 60.0},
            {"trend_health": 60.0, "trend_direction_sign": 1},
            {"score": 60.0, "close_inside_band": False,
             "entry_status": "ABOVE THE BAND", **_confirmed("long")},
            {"risk_valid": True, "risk_regime": "NORMAL RISK",
             "validation_state": "NEUTRAL", "targets": [1.1, 1.2, 1.3]},
            "BULLISH",
        )
    except TypeError:
        return
    raise AssertionError("evaluate() accepted a fifth positional argument")


# --- the sentence names the line, and makes no claim about macro ------------

def test_the_conservative_sentence_names_the_two_quality_lines():
    """
    Rewritten at stage 4 from test_entry_short_is_named_and_trend_is_not_blamed.
    The sentence named which of trend health's 75 and entry quality's 70 a
    setup fell short of; there is one line now, and the CONSERVATIVE
    sentence names both of entry quality's -- the one it passed and the one
    it is under -- and no trend health.
    """
    out = _route("long", "BULLISH", entry_score=60.0)
    reason = _tier_reason(out)
    assert reason == (
        "The bullish bias passed every gate with entry quality 60 of 100 — "
        f"at or above the {CONSERVATIVE_MIN:g} a CONSERVATIVE trade needs, "
        f"and under the {UPPER_MIN:g} the upper tiers need — "
        "CONSERVATIVE LONG."), reason
    assert "trend" not in reason.lower(), reason


def test_the_sentence_makes_no_claim_about_macro():
    """
    It read "Bias is bullish and the broader macro trend agrees" -- a claim
    about an input the tier no longer reads.
    """
    for side in ("long", "short"):
        for macro in MACROS:
            if side == "long" and macro == "BEARISH":
                # Refused by gate 6 before gate 9: there is no tier
                # sentence to read.
                continue
            reason = _tier_reason(_route(side, macro))
            assert "macro" not in reason.lower(), reason
            assert "daily trend" not in reason.lower(), reason
