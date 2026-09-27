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

THE SENTENCE -- Viktor's ruling, 27 September 2026, by agreeing to Claude's
suggestion

The CONSERVATIVE reason read "...but the entry quality (N/100) isn't strong
enough" in every case, including a strong entry held back by trend strength.
It now names what fell short.

WHAT THESE TESTS HOLD

The behavioural tests go through SignalRouter._build_decision_object, the one
place the engine still receives a macro reading. That path exists before and
after the change, so against the pre-G code these fail by assertion (WAIT
where CONSERVATIVE is expected; the old sentence), not by a TypeError. The
router returns an error record with no "exit" when assembly fails, so every
exact-action assertion here raises on a failed build rather than passing.

No fixtures and no pytest import: run_tests.py calls each test with no
arguments.
"""

import inspect
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.decision_model import DecisionModel
from models.signal_router import SignalRouter

MACROS = ("BULLISH", "BEARISH", "NEUTRAL")
TREND_MIN = DecisionModel.AGGRESSIVE_TREND_HEALTH_MIN
ENTRY_MIN = DecisionModel.AGGRESSIVE_ENTRY_SCORE_MIN


def _confirmed(side):
    """A complete, confirmed signal record for `side`, so the gate passes."""
    other = "short" if side == "long" else "long"
    return {f"{side}_signal": True, f"{side}_signal_blockers": [],
            f"{other}_signal": False,
            f"{other}_signal_blockers": ["structure does not agree"]}


def _route(side, macro, health=60.0, entry_score=40.0, score=60.0):
    """One run through the router. side is "long" or "short"."""
    long_side = side == "long"
    out = SignalRouter(engine_core=object())._build_decision_object(
        symbol="TESTUSDT", timeframe="4h",
        bias={"raw": "BULLISH" if long_side else "BEARISH",
              "score": score if long_side else -score},
        trend={"trend_health": health,
               "trend_direction_sign": 1 if long_side else -1,
               "momentum_divergence": False},
        structure={},
        entry={"score": entry_score, "entry_status": "APPROACHING ZONE",
               **_confirmed(side)},
        risk={"risk_valid": True, "risk_reason": "OK",
              "risk_regime": "NORMAL RISK", "validation_state": "NEUTRAL",
              "targets": [1.1, 1.2, 1.3] if long_side else [0.9, 0.8, 0.7]},
        exit_data={"current_price": 1.0},
        macro_bias=macro, chart_path="",
    )
    return out


def _conservative_reason(out):
    reasons = [r for r in out["explanation"]["reasons"]
               if r.endswith("— CONSERVATIVE LONG.")
               or r.endswith("— CONSERVATIVE SHORT.")]
    assert len(reasons) == 1, out["explanation"]["reasons"]
    return reasons[0]


# --- the tier no longer depends on macro -------------------------------------

def test_a_conservative_long_does_not_depend_on_macro():
    for macro in MACROS:
        out = _route("long", macro)
        assert out["exit"]["action"] == "CONSERVATIVE LONG", (
            f"macro {macro}: {out['exit']['action']} -- "
            f"{out['explanation']['reasons']}")


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
    """
    below = DecisionModel.CONSERVATIVE_TREND_HEALTH_MIN - 1.0
    for side in ("long", "short"):
        for macro in MACROS:
            out = _route(side, macro, health=below)
            assert out["exit"]["action"] == "WAIT", (
                f"{side}, macro {macro}, trend health {below}: "
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
            {"score": 40.0, "entry_status": "APPROACHING ZONE", **_confirmed("long")},
            {"risk_valid": True, "risk_regime": "NORMAL RISK",
             "validation_state": "NEUTRAL", "targets": [1.1, 1.2, 1.3]},
            "BULLISH",
        )
    except TypeError:
        return
    raise AssertionError("evaluate() accepted a fifth positional argument")


# --- the sentence names what fell short ---------------------------------------

def test_trend_short_is_named_and_entry_is_not_blamed():
    """The false case: entry 80 passed its line, trend 60 did not."""
    out = _route("long", "BULLISH", health=60.0, entry_score=80.0)
    reason = _conservative_reason(out)
    assert f"below the {TREND_MIN:.0f} the LONG tier needs" in reason, reason
    assert "entry quality 80/100" in reason, reason
    assert "is below" not in reason and "isn't strong" not in reason, reason


def test_entry_short_is_named_and_trend_is_not_blamed():
    out = _route("long", "BULLISH", health=95.0, entry_score=45.0)
    reason = _conservative_reason(out)
    assert (f"the entry quality (45/100) is below the {ENTRY_MIN:.0f} "
            f"the LONG tier needs") in reason, reason
    assert f"below the {TREND_MIN:.0f}" not in reason, reason


def test_both_short_are_named():
    out = _route("short", "BEARISH", health=60.0, entry_score=40.0)
    reason = _conservative_reason(out)
    assert f"below the {TREND_MIN:.0f} the SHORT tier needs" in reason, reason
    assert f"entry quality (40/100) is below its {ENTRY_MIN:.0f}" in reason, reason


def test_the_sentence_makes_no_claim_about_macro():
    """
    It read "Bias is bullish and the broader macro trend agrees" -- a claim
    about an input the tier no longer reads.
    """
    for side in ("long", "short"):
        for macro in MACROS:
            reason = _conservative_reason(_route(side, macro))
            assert "macro" not in reason.lower(), reason


def test_the_sentence_names_the_bias_side_and_the_trend_direction():
    long_reason = _conservative_reason(_route("long", "NEUTRAL"))
    short_reason = _conservative_reason(_route("short", "NEUTRAL"))
    assert long_reason.startswith("Bias is bullish, trend strength 60/100 (up)"), long_reason
    assert short_reason.startswith("Bias is bearish, trend strength 60/100 (down)"), short_reason
