"""
The risk plan's direction is the sign of bias_score, and its stop is always
on the correct side of price -- or there is no plan.

FOUND 21 SEPTEMBER 2026, by reading the code during the pre-backtest review
(docs/PHASE7_NEXT.md, "Review findings", items 8 and 9). Work order C.

8. calculate_stop_targets took `detailed_bias` as its first parameter and
   tested it for "LONG" / "SHORT". Its only caller passes BiasStateMachine's
   output -- "BULLISH CONFIRMED", "BEARISH CONFIRMED" or "NEUTRAL" -- so the
   test could not pass and the direction always came from the sign of
   bias_score. The parameter decided nothing and read as the direction source.
   It is removed.
   CORRECTED 27 September 2026 (finding 18): that output -- now
   models.bias_engine.bias_label's -- also included plain "BULLISH" and
   "BEARISH" (a score past +-20 up to +-30). Still never "LONG" or "SHORT", so
   the finding stands.

9. When the stop did not land on the correct side of price, a fallback
   replaced the stop DISTANCE and left the stop where it was. Unreachable on
   the engine's path (bias_score is clipped to +-100), wrong if reached: a
   stop above a long's entry, returned as a plan. It raises now.

The grid test is the evidence for "unreachable": every combination of score,
trend health and volatility state the engine can produce gives a stop on the
correct side. (It also varied a structural level until finding 6,
27 September 2026, removed that input: the stop comes from ATR alone.
tests/test_stop_is_atr_only.py holds that.) The out-of-range tests are the evidence
that the raise is load-bearing: they reach the branch the grid proves the
engine cannot.

FIX 1, 5 October 2026: trend health no longer reaches the stop and is no
longer a parameter, so the grid lost that axis; and with bias_factor gone, no
bias_score reaches the branch either. The out-of-range test now shows those
scores give an ordinary plan, and reaches the branch through a multiplier
constant made negative for the length of the test.

Fixture-free, per run_tests.py.
"""

import ast
import itertools
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PRICE = 100.0
ATR = 2.0


def _plan(bias_score, volatility_state="NORMAL"):
    from models.risk_model import RiskModel

    # FIX 1, 5 October 2026: trend_health (default 60.0) was passed here; the
    # parameter is gone.
    return RiskModel().calculate_stop_targets(
        current_price=PRICE,
        atr_val=ATR,
        bias_score=bias_score,
        volatility_state=volatility_state,
    )


def _raises(fn):
    try:
        fn()
    except Exception as exc:          # noqa: BLE001 -- the type is asserted by the caller
        return exc
    return None


def _is_long(plan):
    stop, t1, t2, t3 = plan
    return stop < PRICE < t1 < t2 < t3


def _is_short(plan):
    stop, t1, t2, t3 = plan
    return stop > PRICE > t1 > t2 > t3


# --- 8: direction ----------------------------------------------------------

def test_detailed_bias_is_no_longer_accepted():
    from models.risk_model import RiskModel

    # structural_level=None stood in this call until finding 6 removed that
    # parameter too. Left in, it would raise the TypeError by itself and this
    # test would pass whatever became of detailed_bias -- so it is gone, and
    # the message is asserted to name detailed_bias. trend_health=60.0 went
    # from this call at fix 1 (5 October 2026), for the same reason.
    exc = _raises(lambda: RiskModel().calculate_stop_targets(
        detailed_bias="BULLISH CONFIRMED",
        current_price=PRICE, atr_val=ATR, bias_score=40.0))
    assert isinstance(exc, TypeError), (
        "calculate_stop_targets accepts detailed_bias again -- a parameter "
        "that reads as the direction source and is not one")
    assert "detailed_bias" in str(exc), exc


def test_the_plan_direction_is_the_sign_of_bias_score():
    assert _is_long(_plan(40.0))
    assert _is_short(_plan(-40.0))
    # Inside the NEUTRAL band (|score| <= 20) the plan still has a side.
    assert _is_long(_plan(5.0))
    assert _is_short(_plan(-5.0))
    # Zero is a long, as it has always been.
    assert _is_long(_plan(0.0))


def test_a_nan_bias_score_is_refused_rather_than_read_as_short():
    """
    Refused by its own check, named for its own cause. The first version of
    this test asserted only that a ValueError came back, and passed with the
    check deleted: a NaN score makes the stop NaN, and the wrong-side refusal
    below catches that too -- with a message about the stop, not the score.
    The negative control found it. Asserting the message pins the guard that
    names the real cause.
    """
    exc = _raises(lambda: _plan(float("nan")))
    assert isinstance(exc, ValueError), (
        "a NaN bias_score produced a plan; NaN >= 0 is False, so that plan "
        "was a SHORT chosen by a missing number")
    assert "bias_score" in str(exc), exc


# --- 9: side ---------------------------------------------------------------

def test_every_plan_the_engine_can_ask_for_has_its_stop_on_the_correct_side():
    """
    The unreachability claim, checked rather than argued. bias_score is
    clipped to -100..100 by bias_engine and trend_health to 0..100 by
    trend_health.py. A structural level was a fourth axis here until finding
    6 (27 September 2026) removed it from the stop, and trend health a third
    until fix 1 (5 October 2026) did the same.
    """
    scores = [-100.0, -99.9, -50.0, -20.0, -0.1, 0.0, 0.1, 20.0, 50.0, 99.9, 100.0]
    vols = ["LOW VOLATILITY", "NORMAL", "HIGH VOLATILITY", "EXTREME VOLATILITY"]

    for score, vol in itertools.product(scores, vols):
        plan = _plan(score, volatility_state=vol)
        ok = _is_long(plan) if score >= 0 else _is_short(plan)
        assert ok, (score, vol, plan)


def test_a_stop_that_would_land_on_the_wrong_side_raises():
    """
    Until fix 1 (5 October 2026), |bias_score| >= 300 made bias_factor <= 0
    and put the ATR stop on the wrong side of price -- the only way into the
    branch. It used to return a long with its stop ABOVE the entry.

    Fix 1 removed bias_factor, so those scores now give an ordinary plan,
    checked first below. What can still reach the branch is a multiplier
    constant that is not positive. Nothing in the engine sets one, so this
    test sets ATR_STOP_MULT negative for its own length -- by hand and
    restored in `finally`, because run_tests.py calls no fixtures -- to show
    the raise is still load-bearing.
    """
    from models import risk_model as rm

    for score in (300.0, 400.0, -300.0, -400.0):
        plan = _plan(score)
        ok = _is_long(plan) if score >= 0 else _is_short(plan)
        assert ok, (
            f"bias_score {score} no longer gives an ordinary plan: {plan}; "
            f"since fix 1 the size of the score does not reach the stop")

    original = rm.ATR_STOP_MULT
    try:
        rm.ATR_STOP_MULT = -original
        for score in (40.0, -40.0):
            exc = _raises(lambda: _plan(score))
            assert isinstance(exc, ValueError), (
                f"a negative stop multiplier returned a plan instead of "
                f"refusing, at bias_score {score}: {exc!r}")
            assert "wrong side" in str(exc), exc
    finally:
        rm.ATR_STOP_MULT = original
    assert rm.ATR_STOP_MULT == original, rm.ATR_STOP_MULT


# test_a_structural_level_on_the_far_side_does_not_move_the_stop_across
# stood here: a negative control for the raise, showing that min() / max()
# against a structural level on the far side of price still gave a normal
# plan. Finding 6 (27 September 2026) removed the structural level and the
# min() / max(), so there is no far side left to test; the test was removed
# with them rather than left passing on a path that no longer exists.


# --- the record ------------------------------------------------------------

def test_the_lineage_no_longer_lists_detailed_bias_as_a_risk_input():
    """
    engine_core's lineage records "what actually fed the risk decision" (its
    own comment, from Item 14). detailed_bias never did. Read from the parse
    tree of the dict literal assigned to "risk_inputs", not from source text.

    The file is parsed, not imported: importing engine_core pulls in
    pandas_ta, and this test has to run in the configuration without it.
    """
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "core", "engine_core.py")
    tree = ast.parse(open(path, "rb").read().decode("utf-8"))
    risk_inputs_keys = None
    for node in ast.walk(tree):
        if not isinstance(node, ast.Dict):
            continue
        for key, value in zip(node.keys, node.values):
            if (isinstance(key, ast.Constant) and key.value == "risk_inputs"
                    and isinstance(value, ast.Dict)):
                risk_inputs_keys = [k.value for k in value.keys
                                    if isinstance(k, ast.Constant)]
    assert risk_inputs_keys is not None, "risk_inputs dict literal not found"
    assert "bias_score" in risk_inputs_keys, risk_inputs_keys
    assert "detailed_bias" not in risk_inputs_keys, risk_inputs_keys
