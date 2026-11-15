"""
The direction is the slow trend's side: EMA50's slope and the order of EMA_20
and EMA_50, and nothing else.

THE REDESIGN'S STAGE 2, 14 November 2026.

Viktor's ruling of 7 November 2026 (docs/PHASE7_DECISIONS.md, "Ruling,
7 November 2026 -- the redesign's direction is EMA50's slope and the EMAs'
order ..."), by agreeing to Claude's suggestion:

    BULLISH   EMA50_Slope > 0 and EMA_20 > EMA_50
    BEARISH   EMA50_Slope < 0 and EMA_20 < EMA_50
    NEUTRAL   anything else -- a lean, and no side

EMA20_Slope is not read, and there is no threshold: the agreement of the two
is the floor that MIN_ACTION_BIAS was. Until this stage bias.raw was a
weighted sum of six inputs against +/-20, the plan's side was that sum's
sign, and the label added CONFIRMED past +/-30.

WHAT THIS STAGE DOES NOT REMOVE. The sum is still computed for the asset and
recorded as bias.score, because confidence is its size and confidence leaves
in stage 5. It decides no direction, no side and no label from here on, and
test 9 below shows that on the engine path: with the pinned run's sum at +77,
a direction made BEARISH is a SHORT plan and no long.

WHAT THESE TESTS HOLD

 1. The rule's nine cells: three slopes by three orders.
 2. EMA20's slope is not an input, by the function's signature.
 3. No threshold: the smallest slope and the smallest gap decide.
 4. Not measured is None, not NEUTRAL, for each of the three inputs and for
    everything that is not a finite number.
 5. The record of the comparison is the comparison: three words that
    determine the result in every cell.
 6. The rule is the one the reading of 11 November counted
    (docs/build/measure_draft_gaps.py, draft_direction), over a grid.
 7. engine_core calls the rule twice, the asset and BTC, and discards the
    label the weighted sum returns.
 8. On the pinned run: the record shows what was compared, it agrees with
    the numbers recorded beside it, the label is the direction, the plan's
    side follows it, and BTC's direction is what pandas gives on BTC's own
    candles (the draft's section 2 computed BULLISH there, where the sum
    said BEARISH).
 9. The direction alone picks the side: BEARISH under a bullish sum.
10. A measured NEUTRAL is a WAIT with its own sentence, not degraded, with a
    plan computed on the stand-in side and none printed.
11. A direction that could not be measured degrades the run, names the
    column, authorizes no trade, and is recorded as not measured.
12. The helper that reads the decision candle answers None for a column
    that is absent or a cell that is not a number, and reads the last row.

Tests 9 to 11 change what the engine reads at the decision candle, by
replacing Phase7Engine._decision_bar_value for the length of one run. The
indicators are not made to fail instead, because EMA_20 and EMA_50 each have
a manual fallback inside indicators.py and a pandas_ta failure does not
remove them.

All fixture-free, so run_tests.py runs them too. Tests 1 to 5 need neither
pandas_ta nor the engine.
"""

import ast
import importlib.util
import inspect
import itertools
import math
import os

import pytest

from conftest import REPO_ROOT

PINNED_DIR = os.path.join(REPO_ROOT, "tests", "fixtures", "pinned")
UNREACHABLE = "http://127.0.0.1:9"
DIRECTION_COLUMNS = ("EMA50_Slope", "EMA_20", "EMA_50")

SLOPES = {"RISING": 0.2, "FLAT": 0.0, "FALLING": -0.2}
ORDERS = {"ABOVE": (101.0, 100.0), "EQUAL": (100.0, 100.0), "BELOW": (99.0, 100.0)}


def _engine_available():
    try:
        import pandas_ta  # noqa: F401
        return True
    except Exception:
        return False


def _want(slope_word, order_word):
    if slope_word == "RISING" and order_word == "ABOVE":
        return "BULLISH"
    if slope_word == "FALLING" and order_word == "BELOW":
        return "BEARISH"
    return "NEUTRAL"


# ============================================================
# 1-5. The rule
# ============================================================

def test_the_rule_in_all_nine_cells():
    from models.bias_engine import direction_from_emas

    got = {}
    for (slope_word, slope), (order_word, (fast, slow)) in itertools.product(
            SLOPES.items(), ORDERS.items()):
        got[(slope_word, order_word)] = direction_from_emas(slope, fast, slow)
    want = {cell: _want(*cell) for cell in got}
    assert got == want, {c: (got[c], want[c]) for c in got if got[c] != want[c]}
    # One cell each for a side, seven for NEUTRAL.
    assert sorted(got.values()).count("BULLISH") == 1
    assert sorted(got.values()).count("BEARISH") == 1


def test_ema20s_slope_is_not_an_input():
    from models.bias_engine import direction_from_emas

    assert list(inspect.signature(direction_from_emas).parameters) == [
        "ema50_slope", "ema_20", "ema_50", "components"]
    try:
        direction_from_emas(0.2, 101.0, 100.0, ema20_slope=-5.0)
    except TypeError as exc:
        assert "ema20_slope" in str(exc), exc
    else:
        raise AssertionError("direction_from_emas accepted ema20_slope")


def test_there_is_no_threshold():
    from models.bias_engine import direction_from_emas

    tiny = 5e-324                       # the smallest positive float
    assert direction_from_emas(tiny, 100.0, math.nextafter(100.0, 0.0)) == "BULLISH"
    assert direction_from_emas(-tiny, math.nextafter(100.0, 0.0), 100.0) == "BEARISH"
    # And size buys nothing: a steep slope with the averages the wrong way
    # round is still no side.
    assert direction_from_emas(1e9, 99.0, 100.0) == "NEUTRAL"
    assert direction_from_emas(-1e9, 101.0, 100.0) == "NEUTRAL"


def test_not_measured_is_none_and_not_neutral():
    from models.bias_engine import direction_from_emas

    measured = (0.2, 101.0, 100.0)
    assert direction_from_emas(*measured) == "BULLISH"
    not_numbers = (None, float("nan"), float("inf"), float("-inf"),
                   "0.2", "", True, False, [0.2], {})
    for position, bad in itertools.product(range(3), not_numbers):
        args = list(measured)
        args[position] = bad
        components = {}
        got = direction_from_emas(*args, components=components)
        assert got is None, (position, bad, got)
        assert components["result"] is None, (position, bad, components)
        if position == 0:
            assert components["ema50_slope"] is None, components
            assert components["ema20_vs_ema50"] == "ABOVE", components
        else:
            assert components["ema50_slope"] == "RISING", components
            assert components["ema20_vs_ema50"] is None, components


def test_the_recorded_comparison_determines_the_result():
    """
    Audit finding 7: the record is the comparison that ran. Three words, and
    the first two give the third in every cell -- which two true-or-false
    fields could not, since "not rising" is FALLING or FLAT and only one of
    them can be BEARISH.
    """
    from models.bias_engine import direction_from_emas

    seen = set()
    for (slope_word, slope), (order_word, (fast, slow)) in itertools.product(
            SLOPES.items(), ORDERS.items()):
        components = {"left alone": 1}
        result = direction_from_emas(slope, fast, slow, components=components)
        assert components == {"left alone": 1, "ema50_slope": slope_word,
                              "ema20_vs_ema50": order_word, "result": result}, components
        assert result == _want(components["ema50_slope"], components["ema20_vs_ema50"])
        seen.add((slope_word, order_word))
    assert len(seen) == 9
    # Passing no dict changes nothing.
    assert direction_from_emas(0.2, 101.0, 100.0, components=None) == "BULLISH"


# ============================================================
# 6. The rule the reading counted
# ============================================================

def test_the_rule_is_the_one_the_reading_of_11_november_counted():
    pytest.importorskip("pandas_ta")
    from models.bias_engine import direction_from_emas

    path = os.path.join(REPO_ROOT, "docs", "build", "measure_draft_gaps.py")
    spec = importlib.util.spec_from_file_location("phase7_measure_draft_gaps_for_direction", path)
    tool = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tool)

    slopes = (-3.0, -1e-9, 0.0, 1e-9, 3.0, None, float("nan"))
    levels = (0.5, 1.0, 1.0000001, 2.0, None, float("inf"))
    compared = 0
    for slope, fast, slow in itertools.product(slopes, levels, levels):
        ind = {"EMA50_Slope": slope, "EMA_20": fast, "EMA_50": slow,
               "EMA20_Slope": -slope if isinstance(slope, float) else 1.0}
        assert direction_from_emas(slope, fast, slow) == tool.draft_direction(ind), (
            slope, fast, slow)
        compared += 1
    assert compared == 7 * 6 * 6, compared


# ============================================================
# 7. engine_core's two calls
# ============================================================

def test_engine_core_asks_the_rule_twice_and_discards_the_sums_label():
    path = os.path.join(REPO_ROOT, "core", "engine_core.py")
    with open(path, "rb") as fh:
        tree = ast.parse(fh.read().decode("utf-8"))

    def calls(name):
        return [n for n in ast.walk(tree) if isinstance(n, ast.Call)
                and isinstance(n.func, ast.Name) and n.func.id == name]

    assert len(calls("direction_from_emas")) == 2, len(calls("direction_from_emas"))

    sums = [n for n in ast.walk(tree) if isinstance(n, ast.Assign)
            and isinstance(n.value, ast.Call)
            and isinstance(n.value.func, ast.Name)
            and n.value.func.id == "calculate_dynamic_bias"]
    assert len(calls("calculate_dynamic_bias")) == 1 and len(sums) == 1, (
        "the weighted sum is computed once, for the asset's score, until "
        "stage 5; BTC's is no longer computed")
    target = sums[0].targets[0]
    assert isinstance(target, ast.Tuple) and len(target.elts) == 2, ast.dump(target)
    assert [e.id for e in target.elts] == ["_", "bias_score"], (
        "the label the weighted sum returns is assigned to a name again; "
        "since stage 2 the direction is direction_from_emas' alone")

    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    assert "btc_bias_score" not in names and "btc_supertrend_direction" not in names


# ============================================================
# 8-11. The engine path
# ============================================================

def _route(decision_bar_override=None):
    """
    Route the pinned AEROUSDT set. decision_bar_override maps a column to
    the value the direction is to read for the ASSET at its decision candle
    (None for "not measured"); the patch is restored in a finally. BTC's
    direction does not go through the patched helper.
    """
    from core.engine_core import Phase7Engine
    from data.data_fetcher import DataFetcher, data_fetcher
    from models.signal_router import SignalRouter

    real = Phase7Engine.__dict__["_decision_bar_value"]
    real_fn = real.__func__

    def patched(df, column):
        if decision_bar_override and column in decision_bar_override:
            return decision_bar_override[column]
        return real_fn(df, column)

    original_url = data_fetcher.base_url
    try:
        Phase7Engine._decision_bar_value = staticmethod(patched)
        data_fetcher.base_url = UNREACHABLE
        DataFetcher.set_pinned_source(PINNED_DIR)
        return SignalRouter().route(symbol="AEROUSDT", timeframe="4h")
    finally:
        Phase7Engine._decision_bar_value = real
        DataFetcher.clear_pinned_source()
        data_fetcher.base_url = original_url


def _names_a_side(action):
    return any(side in action for side in ("LONG", "SHORT"))


def test_on_the_pinned_run_the_record_shows_what_the_direction_compared():
    if not _engine_available():
        pytest.skip("pandas_ta not installed")
    import pandas as pd

    decision = _route()
    assert "error" not in decision, decision.get("error")

    direction = decision["lineage"]["direction"]
    assert direction == {"ema50_slope": "RISING", "ema20_vs_ema50": "ABOVE",
                         "result": "BULLISH"}, direction

    # It agrees with the numbers recorded beside it.
    bar = decision["lineage"]["indicators_at_decision_bar"]
    assert bar["EMA50_Slope"] > 0 and bar["EMA_20"] > bar["EMA_50"], bar

    # The label is the direction, with no word added.
    assert decision["bias"]["raw"] == decision["bias"]["detailed"] == "BULLISH", decision["bias"]
    assert decision["lineage"]["risk_inputs"]["side"] == "LONG"
    assert "bias_score" not in decision["lineage"]["risk_inputs"]
    stop = float(decision["risk"]["atr_stop"])
    targets = [float(t) for t in decision["risk"]["targets"]]
    assert stop < float(bar["close"]) < targets[0] < targets[1] < targets[2]

    # BTC, computed here from its own candles and not read from the engine.
    btc = pd.read_csv(os.path.join(PINNED_DIR, "BTCUSDT_4h.csv"))
    ema20 = btc["close"].ewm(span=20, adjust=False).mean()
    ema50 = btc["close"].ewm(span=50, adjust=False).mean()
    slope50 = (ema50.iloc[-1] - ema50.iloc[-2]) / ema50.iloc[-2] * 100.0
    assert slope50 > 0 and ema20.iloc[-1] > ema50.iloc[-1], (
        slope50, ema20.iloc[-1], ema50.iloc[-1])
    assert decision["btc_context"]["available"] is True, decision["btc_context"]
    assert decision["btc_context"]["raw"] == "BULLISH", decision["btc_context"]
    assert decision["btc_context"]["detailed"] == "BULLISH", decision["btc_context"]


def test_the_direction_alone_picks_the_side():
    """
    The pinned run's weighted sum is about +77 and its SuperTrend, structure
    and macro are bullish. With EMA50 falling and EMA20 under it at the
    decision candle, the direction is BEARISH, the plan is a short's, and no
    long is returned: the sum picks nothing.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    control = _route()
    bar = control["lineage"]["indicators_at_decision_bar"]
    decision = _route({"EMA50_Slope": -abs(bar["EMA50_Slope"]),
                       "EMA_20": bar["EMA_50"], "EMA_50": bar["EMA_20"]})
    assert "error" not in decision, decision.get("error")

    assert decision["bias"]["score"] == control["bias"]["score"] > 30, decision["bias"]
    assert decision["bias"]["raw"] == decision["bias"]["detailed"] == "BEARISH"
    assert decision["lineage"]["direction"] == {
        "ema50_slope": "FALLING", "ema20_vs_ema50": "BELOW", "result": "BEARISH"}
    assert decision["lineage"]["risk_inputs"]["side"] == "SHORT"
    price = float(decision["exit"]["current_price"])
    stop = float(decision["risk"]["atr_stop"])
    targets = [float(t) for t in decision["risk"]["targets"]]
    assert stop > price > targets[0] > targets[1] > targets[2], (stop, price, targets)
    assert "LONG" not in decision["exit"]["action"], decision["exit"]["action"]
    assert decision["degradation"]["degraded"] is False, decision["degradation"]
    # The same distance as the long's: the risk check cannot tell the sides apart.
    assert math.isclose(stop - price, price - float(control["risk"]["atr_stop"]),
                        rel_tol=0, abs_tol=1e-12)
    assert decision["risk"]["risk_valid"] == control["risk"]["risk_valid"]


def test_a_measured_neutral_waits_with_its_own_sentence_and_prints_no_plan():
    if not _engine_available():
        pytest.skip("pandas_ta not installed")
    from core.panel_render import render_panel

    control = _route()
    bar = control["lineage"]["indicators_at_decision_bar"]
    # EMA50 falling under an EMA20 that is still above it: they disagree.
    decision = _route({"EMA50_Slope": -abs(bar["EMA50_Slope"])})
    assert "error" not in decision, decision.get("error")

    assert decision["lineage"]["direction"] == {
        "ema50_slope": "FALLING", "ema20_vs_ema50": "ABOVE", "result": "NEUTRAL"}
    assert decision["bias"]["raw"] == decision["bias"]["detailed"] == "NEUTRAL"
    assert decision["degradation"]["degraded"] is False, decision["degradation"]
    assert decision["exit"]["action"] == "WAIT", decision["exit"]["action"]
    reasons = decision["explanation"]["reasons"]
    assert any("The direction is NEUTRAL" in r for r in reasons), reasons
    assert "The direction is NEUTRAL" in decision["explanation"]["summary"]

    # The plan is still computed, on the stand-in side, and is the control's.
    assert decision["lineage"]["risk_inputs"]["side"] == "LONG"
    assert decision["risk"]["atr_stop"] == control["risk"]["atr_stop"]
    assert list(decision["risk"]["targets"]) == list(control["risk"]["targets"])

    panel = render_panel(decision)
    plan = [ln for ln in panel.splitlines() if ln.startswith("PLAN")]
    assert len(plan) == 1 and "the bias is NEUTRAL" in plan[0], plan
    assert not [ln for ln in panel.splitlines() if ln.startswith("STOP LOSS")]
    assert "THIS ANALYSIS IS FOR A" not in panel


def test_a_direction_not_measured_degrades_the_run_and_is_not_recorded_as_neutral():
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    for column in DIRECTION_COLUMNS:
        decision = _route({column: None})
        assert "error" not in decision, (column, decision.get("error"))

        block = decision["degradation"]
        assert block["degraded"] is True, (column, block)
        named = [m for m in block["missing_inputs"] if m.startswith("direction (")]
        assert len(named) == 1 and f"({column} not measured)" in named[0], (column, block)
        assert not _names_a_side(decision["exit"]["action"]), (
            column, decision["exit"]["action"])

        direction = decision["lineage"]["direction"]
        assert direction["result"] is None, (column, direction)
        if column == "EMA50_Slope":
            assert direction["ema50_slope"] is None, direction
            assert direction["ema20_vs_ema50"] == "ABOVE", direction
        else:
            assert direction["ema50_slope"] == "RISING", direction
            assert direction["ema20_vs_ema50"] is None, direction

        # bias.raw has no fourth word; the record above is where the
        # difference from a measured NEUTRAL is kept.
        assert decision["bias"]["raw"] == "NEUTRAL", decision["bias"]
        assert any("DEGRADED" in r and "direction (" in r
                   for r in decision["explanation"]["reasons"]), (
            decision["explanation"]["reasons"])


# ============================================================
# 12. Reading the decision candle
# ============================================================

def test_the_decision_candle_reader_answers_none_for_what_is_not_there():
    if not _engine_available():
        pytest.skip("pandas_ta not installed")
    import pandas as pd
    from core.engine_core import Phase7Engine

    read = Phase7Engine._decision_bar_value
    frame = pd.DataFrame({"EMA_50": [1.0, 2.0, 3.5],
                          "EMA_20": [1.0, 2.0, float("nan")],
                          "EMA50_Slope": [1.0, 2.0, float("inf")],
                          "label": ["a", "b", "c"]})
    assert read(frame, "EMA_50") == 3.5                 # the last row
    assert read(frame, "EMA_20") is None                # not a number
    assert read(frame, "EMA50_Slope") is None           # not finite
    assert read(frame, "label") is None                 # not numeric
    assert read(frame, "ABSENT") is None                # no column
    assert read(frame.iloc[0:0], "EMA_50") is None      # no rows
    assert read(None, "EMA_50") is None
