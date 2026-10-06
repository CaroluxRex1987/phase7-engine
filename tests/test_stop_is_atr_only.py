"""
Finding 6 -- the stop comes from ATR alone.

Review of 21 September 2026, finding 6: the stop was pulled to the HVN, the
75-day volume point of control, with no distance limit. engine_core passed
structural_level=hvn to calculate_stop_targets, and for a long the stop was
min(HVN, ATR stop), for a short max(...). The HVN could only widen the stop,
and a trend that had moved away from it got its stop there. On Viktor's
decision log (39 usable runs, 6-27 September 2026, AEROUSDT 4h) the HVN set
the stop in 35 of 39, and the risk check refused almost every one.

Viktor's ruling, 27 September 2026 (DECISIONS, "Ruling, 27 September 2026 --
the stop comes from ATR alone (finding 6)"):
1. The stop comes from ATR alone; the HVN stays as information only.
2. The 8% (EXTREME RISK) and 15% (distance refusal) limits are unchanged.
3. No gate checks HVN proximity any more; that goes on the list for after the
   audit.
4. A swing-structure anchor was not chosen and not measured.

WHAT THESE TESTS HOLD
1. calculate_stop_targets no longer accepts a structural level -- refused by
   name, not silently ignored.
2. The stop is exactly the ATR stop, from the fingerprinted constants, on
   every combination of side and volatility state. (Trend health was a third
   axis until fix 1, 5 October 2026, took it out of the stop;
   tests/test_stop_ignores_conviction.py holds that.)
3. engine_core's call passes no structural level, and its lineage no longer
   lists one as a risk input (read from the parse tree, so this runs without
   pandas_ta).
4. On the engine path, the stop in the decision object is the ATR stop
   recomputed from what the record holds -- on a fixture where the HVN lies
   further out, so the old rule would have moved it.
5. The two limits the ruling keeps are still 8% and 15%, and still refuse.

All fixture-free, so run_tests.py runs them too.
"""

import ast
import itertools
import math
import os

import pytest

from conftest import REPO_ROOT

PINNED_DIR = os.path.join(REPO_ROOT, "tests", "fixtures", "pinned")
UNREACHABLE = "http://127.0.0.1:9"

PRICE = 100.0
ATR = 2.0


def _expected_stop(price, atr, bias_score, volatility_state):
    """
    The ATR stop, written out from the module's own constants.

    FIX 1, 5 October 2026: this took trend_health too, and the multiplier
    carried (1 + trend_health / TREND_FACTOR_DIVISOR) and
    (1 - |bias_score| / BIAS_FACTOR_DIVISOR). Both factors and both constants
    are gone; bias_score only picks the side.
    """
    from models import risk_model as rm

    vol = {"HIGH VOLATILITY": rm.VOL_MULT_HIGH,
           "LOW VOLATILITY": rm.VOL_MULT_LOW,
           "EXTREME VOLATILITY": rm.VOL_MULT_EXTREME}.get(volatility_state, 1.0)
    mult = rm.ATR_STOP_MULT * vol
    return price - atr * mult if bias_score >= 0 else price + atr * mult


def _engine_core_tree():
    path = os.path.join(REPO_ROOT, "core", "engine_core.py")
    return ast.parse(open(path, "rb").read().decode("utf-8"))


# ============================================================
# 1. No structural level is accepted
# ============================================================

def test_a_structural_level_is_no_longer_accepted():
    from models.risk_model import RiskModel

    # FIX 1, 5 October 2026: trend_health=60.0 stood first in this call. That
    # parameter is gone too, and left in it would raise the TypeError itself,
    # naming trend_health -- so it is gone from the call, and the message is
    # still asserted to name structural_level.
    try:
        RiskModel().calculate_stop_targets(
            current_price=PRICE, atr_val=ATR,
            structural_level=90.0, bias_score=40.0)
    except TypeError as exc:
        assert "structural_level" in str(exc), exc
    else:
        raise AssertionError(
            "calculate_stop_targets accepted structural_level -- the stop "
            "comes from ATR alone (finding 6), and a parameter that reads as "
            "a stop anchor while deciding nothing is a false statement")


# ============================================================
# 2. The stop is the ATR stop, exactly
# ============================================================

def test_the_stop_is_exactly_the_atr_stop():
    from models import risk_model as rm

    # FIX 1, 5 October 2026: a trend-health axis (0, 50, 100) stood here; trend
    # health no longer reaches the stop and is no longer a parameter.
    scores = [-100.0, -60.0, -0.1, 0.0, 40.0, 100.0]
    vols = ["LOW VOLATILITY", "NORMAL", "HIGH VOLATILITY", "EXTREME VOLATILITY"]
    for score, vol in itertools.product(scores, vols):
        stop, t1, t2, t3 = rm.RiskModel().calculate_stop_targets(
            current_price=PRICE, atr_val=ATR,
            bias_score=score, volatility_state=vol)
        want = _expected_stop(PRICE, ATR, score, vol)
        assert math.isclose(stop, want, rel_tol=0, abs_tol=1e-12), (
            score, vol, stop, want)
        distance = abs(PRICE - stop)
        side = 1.0 if score >= 0 else -1.0
        for target, mult in zip((t1, t2, t3), (rm.TARGET1_MULT, rm.TARGET2_MULT,
                                               rm.TARGET3_MULT)):
            assert math.isclose(target, PRICE + side * distance * mult,
                                rel_tol=0, abs_tol=1e-12), (score, target, mult)


# ============================================================
# 3. engine_core: the call and the record
# ============================================================

def test_engine_core_passes_no_structural_level_to_the_stop():
    calls = []
    for node in ast.walk(_engine_core_tree()):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == "calculate_stop_targets"):
            calls.append(node)
    assert len(calls) == 1, f"expected one call to calculate_stop_targets, found {len(calls)}"
    keywords = [kw.arg for kw in calls[0].keywords]
    assert "structural_level" not in keywords, keywords
    names = {n.id for n in ast.walk(calls[0]) if isinstance(n, ast.Name)}
    assert "hvn" not in names, (
        "the HVN reaches calculate_stop_targets again; since finding 6 it is "
        "information only")


def test_the_lineage_no_longer_lists_a_structural_level_as_a_risk_input():
    keys = None
    for node in ast.walk(_engine_core_tree()):
        if not isinstance(node, ast.Dict):
            continue
        for key, value in zip(node.keys, node.values):
            if (isinstance(key, ast.Constant) and key.value == "risk_inputs"
                    and isinstance(value, ast.Dict)):
                keys = [k.value for k in value.keys if isinstance(k, ast.Constant)]
    assert keys is not None, "risk_inputs dict literal not found"
    assert "atr" in keys and "current_price" in keys, keys
    assert "structural_level" not in keys, (
        "risk_inputs records what fed the stop; the HVN no longer does", keys)


# ============================================================
# 4. The engine path
# ============================================================

def _run_pinned():
    from data.data_fetcher import DataFetcher, data_fetcher
    from models.signal_router import SignalRouter

    original = data_fetcher.base_url
    try:
        data_fetcher.base_url = UNREACHABLE
        DataFetcher.set_pinned_source(PINNED_DIR)
        return SignalRouter().route(symbol="AEROUSDT", timeframe="4h")
    finally:
        DataFetcher.clear_pinned_source()
        data_fetcher.base_url = original


def test_on_the_engine_path_the_stop_is_the_atr_stop_not_the_hvn():
    pytest.importorskip("pandas_ta")

    decision = _run_pinned()
    inputs = decision["lineage"]["risk_inputs"]
    price = float(inputs["current_price"])
    score = float(inputs["bias_score"])
    # FIX 1, 5 October 2026: decision["trend"]["trend_health"] was read here,
    # because it fed the stop; it no longer does.
    want = _expected_stop(price, float(inputs["atr"]), score,
                          inputs["volatility_state"])
    stop = float(decision["risk"]["atr_stop"])
    assert math.isclose(stop, want, rel_tol=0, abs_tol=1e-12), (stop, want)

    # Not vacuous: on this fixture the HVN lies beyond the ATR stop, so the
    # rule finding 6 removed would have moved the stop out to it.
    hvn = float(decision["structure"]["hvn"])
    assert math.isfinite(hvn), hvn
    beyond = hvn < want if score >= 0 else hvn > want
    assert beyond, (
        f"the fixture's HVN {hvn} does not lie beyond the ATR stop {want}; "
        f"this test no longer shows the old pull is gone")
    assert stop != hvn, (stop, hvn)


# ============================================================
# 5. The limits the ruling keeps
# ============================================================

def test_the_eight_and_fifteen_percent_limits_are_unchanged():
    from models import risk_model as rm

    assert rm.REGIME_EXTREME_STOP_PCT == 8.0, rm.REGIME_EXTREME_STOP_PCT
    assert rm.MAX_STOP_DISTANCE_PCT == 15.0, rm.MAX_STOP_DISTANCE_PCT

    model = rm.RiskModel()
    # FIX 3, 6 October 2026: volatility_state="NORMAL", adx=30.0 until fix 3.
    # ADX is no longer an input, and "NORMAL" -- a state the engine never
    # produces -- is UNKNOWN RISK now; MEDIUM VOLATILITY is its NORMAL RISK.
    ok, _, regime = model.validate_risk_parameters(
        current_price=100.0, atr_stop=93.0, volatility_state="MEDIUM VOLATILITY")
    assert ok and regime == "NORMAL RISK", (ok, regime)
    ok, _, regime = model.validate_risk_parameters(
        current_price=100.0, atr_stop=91.0, volatility_state="MEDIUM VOLATILITY")
    assert not ok and regime == "EXTREME RISK", (ok, regime)
    ok, reason, regime = model.validate_risk_parameters(
        current_price=100.0, atr_stop=84.0, volatility_state="MEDIUM VOLATILITY")
    assert not ok and regime == "UNKNOWN" and "15%" in reason, (ok, reason, regime)
