"""
The risk plan's direction is the side it is given, and its stop is always
on the correct side of price -- or there is no plan.

THE REDESIGN'S STAGE 2, 14 November 2026. Until this stage the first line
read "is the sign of bias_score". The direction is no longer a score
(Viktor's ruling of 7 November 2026: EMA50's slope and the EMAs' order), so
calculate_stop_targets takes `side`, "LONG" or "SHORT", and refuses anything
else; which side a NEUTRAL run's plan is drawn on is
models.bias_engine.plan_side's, held below. Three tests are rewritten for
that (the direction, the refusal, the grid), one keeps its two halves with
the first half's reason gone (the wrong-side raise), and the record's test
reads `side` where it read bias_score. The account below is the dated one.

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


def _plan(side, volatility_state="NORMAL"):
    from models.risk_model import RiskModel

    # FIX 1, 5 October 2026: trend_health (default 60.0) was passed here; the
    # parameter is gone. Stage 2, 14 November 2026: bias_score was passed
    # here; the side is.
    return RiskModel().calculate_stop_targets(
        current_price=PRICE,
        atr_val=ATR,
        side=side,
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
        current_price=PRICE, atr_val=ATR, side="LONG"))
    assert isinstance(exc, TypeError), (
        "calculate_stop_targets accepts detailed_bias again -- a parameter "
        "that reads as the direction source and is not one")
    assert "detailed_bias" in str(exc), exc


def test_bias_score_is_no_longer_accepted():
    """
    Stage 2. The parameter is removed rather than ignored, for the reason
    detailed_bias was: left in the signature it would read as the direction
    source and decide nothing.
    """
    from models.risk_model import RiskModel

    exc = _raises(lambda: RiskModel().calculate_stop_targets(
        current_price=PRICE, atr_val=ATR, side="LONG", bias_score=40.0))
    assert isinstance(exc, TypeError), (
        "calculate_stop_targets accepts bias_score again -- the plan's side "
        "is passed, and a score beside it decides nothing")
    assert "bias_score" in str(exc), exc


def test_the_plan_direction_is_the_side():
    assert _is_long(_plan("LONG"))
    assert _is_short(_plan("SHORT"))


def test_the_side_comes_from_the_direction_and_neutral_is_drawn_as_a_long():
    """
    Where the side comes from (models.bias_engine.plan_side). Until stage 2 a
    NEUTRAL run's plan took the sign of the weighted sum, zero as a long; the
    stand-in is fixed now. The risk check reads only the stop's distance,
    which the last assertion shows is the same on either side.
    """
    from models.bias_engine import plan_side
    from models.risk_model import RiskModel

    assert plan_side("BULLISH") == "LONG"
    assert plan_side("BEARISH") == "SHORT"
    assert plan_side("NEUTRAL") == "LONG"
    assert _is_long(_plan(plan_side("NEUTRAL")))

    model = RiskModel()
    verdicts = {
        side: model.validate_risk_parameters(
            current_price=PRICE, atr_stop=_plan(side)[0],
            volatility_state="NORMAL")
        for side in ("LONG", "SHORT")
    }
    assert verdicts["LONG"] == verdicts["SHORT"], verdicts


def test_a_side_that_is_not_long_or_short_is_refused_rather_than_read_as_short():
    """
    Refused by its own check, named for its own cause. The branch under it
    is LONG or else, so before the check every other word was drawn as a
    short. Until stage 2 this test held the same for a NaN bias_score
    (`NaN >= 0` is False), and its first version passed with the check
    deleted, because the wrong-side refusal caught the NaN stop with a
    message about the stop. The negative control found that; asserting the
    message pins the guard that names the real cause. Here a deleted check
    returns a short plan, so the first assertion fails by itself.
    """
    for not_a_side in ("BULLISH", "BEARISH", "NEUTRAL", "long", "", None,
                       float("nan"), 1, -1):
        exc = _raises(lambda: _plan(not_a_side))
        assert isinstance(exc, ValueError), (
            f"a side of {not_a_side!r} produced a plan; the branch is LONG "
            f"or else, so that plan was a SHORT nobody chose")
        assert "neither LONG nor SHORT" in str(exc), exc


# --- 9: side ---------------------------------------------------------------

def test_every_plan_the_engine_can_ask_for_has_its_stop_on_the_correct_side():
    """
    The unreachability claim, checked rather than argued. The engine can ask
    for two sides and four volatility states. bias_score was an axis here
    until stage 2 (14 November 2026), when the side replaced it; a structural
    level until finding 6 (27 September 2026) removed it from the stop; and
    trend health until fix 1 (5 October 2026) did the same.
    """
    vols = ["LOW VOLATILITY", "NORMAL", "HIGH VOLATILITY", "EXTREME VOLATILITY"]

    for side, vol in itertools.product(("LONG", "SHORT"), vols):
        plan = _plan(side, volatility_state=vol)
        ok = _is_long(plan) if side == "LONG" else _is_short(plan)
        assert ok, (side, vol, plan)


def test_a_stop_that_would_land_on_the_wrong_side_raises():
    """
    Until fix 1 (5 October 2026), |bias_score| >= 300 made bias_factor <= 0
    and put the ATR stop on the wrong side of price -- the only way into the
    branch. It used to return a long with its stop ABOVE the entry.

    Fix 1 removed bias_factor, and stage 2 (14 November 2026) the score
    itself, so no argument reaches the branch. What can still reach it is a
    multiplier constant that is not positive. Nothing in the engine sets
    one, so this test sets ATR_STOP_MULT negative for its own length -- by
    hand and restored in `finally`, because run_tests.py calls no fixtures
    -- to show the raise is still load-bearing. (Until stage 2 it first
    checked that scores of 300 and 400 gave an ordinary plan; there is no
    score to pass.)
    """
    from models import risk_model as rm

    original = rm.ATR_STOP_MULT
    try:
        rm.ATR_STOP_MULT = -original
        for side in ("LONG", "SHORT"):
            exc = _raises(lambda: _plan(side))
            assert isinstance(exc, ValueError), (
                f"a negative stop multiplier returned a plan instead of "
                f"refusing, for a {side}: {exc!r}")
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
    # Stage 2, 14 November 2026: "bias_score" was asserted present here,
    # because its sign picked the side. The side is recorded, and the score
    # is not an input of the stop.
    assert "side" in risk_inputs_keys, risk_inputs_keys
    assert "bias_score" not in risk_inputs_keys, risk_inputs_keys
    assert "detailed_bias" not in risk_inputs_keys, risk_inputs_keys
