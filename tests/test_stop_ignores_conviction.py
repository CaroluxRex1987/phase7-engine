"""
Fix 1 -- the stop no longer depends on conviction or trend health.

Round 8's triage, ruled on the night of 4 to 5 October 2026 and confirmed on
5 October (docs/PHASE7_DECISIONS.md, "Ruling, 5 October 2026 -- round 8
triaged ...", point 1; the review's B2, which it calls "Finding 1").

WHAT WAS WRONG

The stop multiplier was

    ATR_STOP_MULT x (1 + trend_health / 200) x (1 - |bias_score| / 300) x vol

so trend health widened the stop by up to x1.5, and a strong bias score
narrowed it, down to x0.667 at a score of 100. The risk check refuses a stop
wider than 8% of price as EXTREME RISK, so the same market -- the same price,
ATR and volatility -- passed or failed it depending on how convinced the
engine was. Viktor ruled that a break of Item 14: "Directional conviction must
never be treated as equivalent to risk."

The same formula is why round 8's F1 held: lineage.risk_inputs, the record of
what fed the stop, did not hold trend health, and its comment said nothing
was missing.

THE FIX

The stop is ATR x ATR_STOP_MULT x the volatility factor. trend_health is no
longer a parameter (TypeError if passed), and every parameter is keyword-only.
The sign of bias_score still picks the side; its size no longer reaches the
stop.

WHAT THESE TESTS HOLD

1. trend_health is refused by name, not silently ignored.
2. A call in the old positional order is refused rather than misbound.
3. The stop is the same at every conviction: one distance for every
   |bias_score|, on both sides, in every volatility state.
4. So is the risk verdict, across a sweep of markets that crosses the 8% line,
   where the old formula let conviction decide it -- shown inside the test.
5. engine_core passes no trend_health to the stop (read from the parse tree,
   so this runs without pandas_ta).
6. On the engine path, the stop, the targets and the risk verdict are rebuilt
   from lineage.risk_inputs alone -- round 8's F1 as a test -- on a fixture
   where the old formula gives a different stop.

All fixture-free, so run_tests.py runs them too.
"""

import ast
import math
import os

import pytest

from conftest import REPO_ROOT

PINNED_DIR = os.path.join(REPO_ROOT, "tests", "fixtures", "pinned")
UNREACHABLE = "http://127.0.0.1:9"

VOLS = ["LOW VOLATILITY", "NORMAL", "HIGH VOLATILITY", "EXTREME VOLATILITY"]


def _vol_factor(volatility_state):
    from models import risk_model as rm

    return {"HIGH VOLATILITY": rm.VOL_MULT_HIGH,
            "LOW VOLATILITY": rm.VOL_MULT_LOW,
            "EXTREME VOLATILITY": rm.VOL_MULT_EXTREME}.get(volatility_state, 1.0)


def _pre_fix_stop(price, atr, bias_score, trend_health, volatility_state):
    """
    The stop as it was computed until fix 1, written out with the two divisors
    the fix removed (200 and 300), so that a test can show the market it uses
    is one where conviction decided the answer. Not a reference for the
    current code.
    """
    from models import risk_model as rm

    mult = (rm.ATR_STOP_MULT
            * (1.0 + max(0.0, min(100.0, trend_health)) / 200.0)
            * (1.0 - abs(bias_score) / 300.0)
            * _vol_factor(volatility_state))
    return price - atr * mult if bias_score >= 0 else price + atr * mult


def _stop(price, atr, bias_score, volatility_state):
    from models.risk_model import RiskModel

    stop, _, _, _ = RiskModel().calculate_stop_targets(
        current_price=price, atr_val=atr, bias_score=bias_score,
        volatility_state=volatility_state)
    return stop


# ============================================================
# 1-2. The old signature is refused
# ============================================================

def test_trend_health_is_no_longer_accepted():
    from models.risk_model import RiskModel

    try:
        RiskModel().calculate_stop_targets(
            trend_health=95.0, current_price=100.0, atr_val=2.0,
            bias_score=40.0)
    except TypeError as exc:
        assert "trend_health" in str(exc), exc
    else:
        raise AssertionError(
            "calculate_stop_targets accepted trend_health -- since fix 1 trend "
            "health does not reach the stop, and a parameter that reads as an "
            "input of the stop while deciding nothing is a false statement")


def test_a_positional_call_is_refused():
    """
    The old order was (trend_health, current_price, atr_val, bias_score,
    volatility_state). Without keyword-only parameters, a four-argument call
    in that order would bind trend health to current_price and return a plan
    for a market nobody measured.
    """
    from models.risk_model import RiskModel

    try:
        RiskModel().calculate_stop_targets(95.0, 100.0, 2.0, 40.0)
    except TypeError as exc:
        assert "positional" in str(exc), exc
    else:
        raise AssertionError(
            "calculate_stop_targets took positional arguments: a call in the "
            "old order binds trend health to the price")


# ============================================================
# 3. The stop is the same at every conviction
# ============================================================

def test_the_stop_is_the_same_at_every_conviction():
    price, atr = 100.0, 2.0
    for vol in VOLS:
        long_stops = {_stop(price, atr, s, vol)
                      for s in (0.0, 21.0, 50.0, 75.0, 100.0)}
        short_stops = {_stop(price, atr, s, vol)
                       for s in (-0.1, -21.0, -50.0, -75.0, -100.0)}
        assert len(long_stops) == 1, (vol, sorted(long_stops))
        assert len(short_stops) == 1, (vol, sorted(short_stops))
        (long_stop,), (short_stop,) = long_stops, short_stops
        assert math.isclose(price - long_stop, short_stop - price,
                            rel_tol=0, abs_tol=1e-12), (vol, long_stop, short_stop)


# ============================================================
# 4. So is the risk verdict -- Item 14
# ============================================================

def test_the_risk_verdict_is_the_same_at_every_conviction():
    """
    Item 14, on the risk check itself. Price 100, HIGH VOLATILITY (and ADX 30,
    until fix 3 took ADX out of the risk check), and
    an ATR swept from 3.0 to 9.0, so the stop runs from about 4.9% to 14.6% of
    price and crosses the 8% EXTREME RISK line on the way. On every one of
    those markets every bias score, 0 to 100 on both sides, must get the same
    verdict. A stop that scaled with the score in either direction would put
    some of them on opposite sides of the 8% line on some market of the sweep.

    Not vacuous: under the old formula, at a trend health of 95, the verdict
    on some of these markets depended on the score -- checked at the end.
    """
    from models.risk_model import RiskModel

    model = RiskModel()
    price, vol = 100.0, "HIGH VOLATILITY"
    scores = (0.0, 5.0, 21.0, 30.0, 50.0, 75.0, 100.0,
              -0.1, -5.0, -21.0, -30.0, -50.0, -75.0, -100.0)
    atrs = [3.0 + 0.25 * i for i in range(25)]          # 3.0 .. 9.0

    seen = set()
    for atr in atrs:
        verdicts = {model.validate_risk_parameters(
            current_price=price, atr_stop=_stop(price, atr, score, vol),
            volatility_state=vol) for score in scores}
        assert len(verdicts) == 1, (atr, sorted(verdicts))
        seen |= verdicts
    # The sweep crosses the line: both verdicts occur.
    assert {ok for ok, _, _ in seen} == {True, False}, sorted(seen)

    # Not vacuous: the old formula decided some of these markets by conviction.
    split = []
    for atr in atrs:
        old = {model.validate_risk_parameters(
            current_price=price,
            atr_stop=_pre_fix_stop(price, atr, score, 95.0, vol),
            volatility_state=vol)[0] for score in scores}
        if len(old) > 1:
            split.append(atr)
    assert split, (
        "no market in this sweep separated the old formula's verdicts, so the "
        "test no longer shows that conviction is out of the check")


# ============================================================
# 5. engine_core passes no trend_health
# ============================================================

def test_engine_core_passes_no_trend_health_to_the_stop():
    path = os.path.join(REPO_ROOT, "core", "engine_core.py")
    with open(path, "rb") as fh:
        tree = ast.parse(fh.read().decode("utf-8"))
    calls = [node for node in ast.walk(tree)
             if isinstance(node, ast.Call)
             and isinstance(node.func, ast.Attribute)
             and node.func.attr == "calculate_stop_targets"]
    assert len(calls) == 1, f"expected one call to calculate_stop_targets, found {len(calls)}"
    keywords = [kw.arg for kw in calls[0].keywords]
    assert "trend_health" not in keywords, keywords
    assert not calls[0].args, "the call passes arguments by position"
    strings = {n.value for n in ast.walk(calls[0]) if isinstance(n, ast.Constant)}
    assert "trend_health" not in strings, (
        "trend health reaches calculate_stop_targets again; since fix 1 it "
        "does not set the stop")


# ============================================================
# 6. The engine path -- round 8's F1
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


def test_the_record_holds_every_input_the_stop_reads():
    """
    Round 8's F1: an auditor rebuilding the plan from lineage.risk_inputs --
    what that block is for -- could not, because trend health set the stop
    and was not in it. Rebuilt here from risk_inputs alone: the stop, the
    three targets, and the risk check's verdict and regime.
    """
    pytest.importorskip("pandas_ta")
    from models import risk_model as rm

    decision = _run_pinned()
    inputs = decision["lineage"]["risk_inputs"]
    price = float(inputs["current_price"])
    atr = float(inputs["atr"])
    score = float(inputs["bias_score"])
    vol = inputs["volatility_state"]

    side = 1.0 if score >= 0 else -1.0
    want_stop = price - side * atr * rm.ATR_STOP_MULT * _vol_factor(vol)
    stop = float(decision["risk"]["atr_stop"])
    assert math.isclose(stop, want_stop, rel_tol=0, abs_tol=1e-12), (stop, want_stop)

    distance = abs(price - want_stop)
    targets = [float(t) for t in decision["risk"]["targets"]]
    for got, mult in zip(targets, (rm.TARGET1_MULT, rm.TARGET2_MULT,
                                   rm.TARGET3_MULT)):
        assert math.isclose(got, price + side * distance * mult,
                            rel_tol=0, abs_tol=1e-12), (got, mult)

    # FIX 3, 6 October 2026: adx=inputs["adx"] was passed here too. The
    # regime comes from volatility alone and risk_inputs no longer records
    # ADX, so the verdict and the regime are rebuilt from the stop and the
    # volatility state alone.
    ok, reason, regime = rm.RiskModel().validate_risk_parameters(
        current_price=price, atr_stop=want_stop, volatility_state=vol)
    assert ok == decision["risk"]["risk_valid"], (ok, decision["risk"])
    assert reason == decision["risk"]["risk_reason"], (reason, decision["risk"])
    assert regime == decision["risk"]["risk_regime"] == inputs["risk_regime"], (
        regime, decision["risk"]["risk_regime"], inputs["risk_regime"])

    # Not vacuous: on this fixture trend health and the bias score moved the
    # stop before fix 1, so a record without trend health could not rebuild it.
    old = _pre_fix_stop(price, atr, score,
                        float(decision["trend"]["trend_health"]), vol)
    assert abs(old - stop) > 1e-6, (
        f"the old formula gives {old} on this fixture, the same as the stop "
        f"{stop}; this test no longer shows that conviction left the stop")
