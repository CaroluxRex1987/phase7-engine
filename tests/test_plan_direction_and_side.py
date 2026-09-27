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

Fixture-free, per run_tests.py.
"""

import ast
import itertools
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PRICE = 100.0
ATR = 2.0


def _plan(bias_score, trend_health=60.0, volatility_state="NORMAL"):
    from models.risk_model import RiskModel

    return RiskModel().calculate_stop_targets(
        trend_health=trend_health,
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
    # the message is asserted to name detailed_bias.
    exc = _raises(lambda: RiskModel().calculate_stop_targets(
        detailed_bias="BULLISH CONFIRMED", trend_health=60.0,
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
    6 (27 September 2026) removed it from the stop.
    """
    scores = [-100.0, -99.9, -50.0, -20.0, -0.1, 0.0, 0.1, 20.0, 50.0, 99.9, 100.0]
    healths = [0.0, 50.0, 100.0]
    vols = ["LOW VOLATILITY", "NORMAL", "HIGH VOLATILITY", "EXTREME VOLATILITY"]

    for score, health, vol in itertools.product(scores, healths, vols):
        plan = _plan(score, trend_health=health, volatility_state=vol)
        ok = _is_long(plan) if score >= 0 else _is_short(plan)
        assert ok, (score, health, vol, plan)


def test_a_stop_that_would_land_on_the_wrong_side_raises():
    """
    |bias_score| >= 300 makes bias_factor <= 0 and puts the ATR stop on the
    wrong side of price -- the only way into the branch. It used to return a
    long with its stop ABOVE the entry.
    """
    for score in (300.0, 400.0, -300.0, -400.0):
        exc = _raises(lambda: _plan(score))
        assert isinstance(exc, ValueError), (
            f"bias_score {score} returned a plan instead of refusing: "
            f"{_plan(score) if exc is None else exc!r}")
        assert "wrong side" in str(exc), exc


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
