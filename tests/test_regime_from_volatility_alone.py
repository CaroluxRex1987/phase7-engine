"""
Fix 3 -- the risk regime comes from volatility alone.

Round 8's triage, ruled on the night of 4 to 5 October 2026
(docs/PHASE7_DECISIONS.md, "Ruling, 5 October 2026 -- round 8 triaged ...",
point 3; round 8's F2 and the review's B8).

WHAT WAS WRONG

classify_risk_regime read raw ADX twice: under REGIME_CHOP_ADX (20) the
regime was HIGH VOLATILITY RISK whatever the volatility, and LOW VOLATILITY
reached LOW RISK only with ADX at REGIME_STRONG_ADX (25) or more. Trend
health spends up to 40 of its 100 points on the same raw ADX, and trend
health is 0.30 of bias_score, so a high ADX raised conviction and lowered the
assessed risk together -- against Item 14, "Directional conviction must never
be treated as equivalent to risk." The chop test also named the wrong cause:
a calm market with no trend printed VOLATILITY : LOW VOLATILITY beside
RISK REGIME : HIGH VOLATILITY RISK.

THE FIX

The regime reads the volatility state and the stop distance, nothing else.
EXTREME VOLATILITY, or a stop over 8%, is EXTREME RISK; HIGH VOLATILITY is
HIGH VOLATILITY RISK; MEDIUM VOLATILITY is NORMAL RISK; LOW VOLATILITY is
LOW RISK; and any other state is UNKNOWN RISK -- the patch's proposal,
Viktor's to reverse, where every unnamed state used to fall through to NORMAL
RISK. validate_risk_parameters takes three required parameters and no
**kwargs, so adx=, trend_health= and a misspelt keyword are refused by
Python. REGIME_CHOP_ADX and REGIME_STRONG_ADX are gone, from the module and
from the run-hash payload. engine_core passes no ADX to the risk check, and
lineage.risk_inputs no longer records one.

WHAT THESE TESTS HOLD

1. Neither function takes ADX. validate_risk_parameters refuses adx,
   trend_health and a misspelt keyword, and has no default for the state.
2. Each volatility state the engine produces has its regime, at every stop
   up to 8%.
3. Any other state is UNKNOWN RISK -- and that is all it decides: the risk
   check still passes. (That UNKNOWN RISK keeps AGGRESSIVE out is held in
   tests/test_no_risk_free_conviction.py, whose every-regime test lists it.)
4. A stop over 8% is EXTREME RISK in every state, unknown ones included.
5. On the engine's own numbers -- calculate_dynamic_regime's bands and the
   stop calculate_stop_targets gives -- the regime names the volatility the
   panel's VOLATILITY line prints, so B8 cannot recur. Needs pandas, not
   pandas_ta.
6. The two ADX constants are gone, from the module and from the run-hash
   payload.
7. engine_core passes no adx to the risk check, and the risk_inputs dict
   literal has no "adx" key. Read from the parse tree, so these run without
   pandas_ta.
8. On the engine path (pandas_ta), the record holds no ADX in risk_inputs,
   still holds it at the decision bar, and its regime is the one the table
   gives for its volatility state.

All fixture-free, so run_tests.py runs them too.
"""

import ast
import inspect
import os

import pytest

from conftest import REPO_ROOT

from models import risk_model as rm
from models.risk_model import RiskModel

ENGINE_CORE = os.path.join(REPO_ROOT, "core", "engine_core.py")
PINNED_DIR = os.path.join(REPO_ROOT, "tests", "fixtures", "pinned")
UNREACHABLE = "http://127.0.0.1:9"

# The four states models/bias_engine.py's calculate_dynamic_regime produces,
# and the regime each one is.
REGIME_OF = {
    "LOW VOLATILITY": "LOW RISK",
    "MEDIUM VOLATILITY": "NORMAL RISK",
    "HIGH VOLATILITY": "HIGH VOLATILITY RISK",
    "EXTREME VOLATILITY": "EXTREME RISK",
}


# ======================================================================
# 1. No ADX anywhere in the risk check
# ======================================================================

def test_neither_function_takes_adx():
    classify = list(inspect.signature(RiskModel.classify_risk_regime).parameters)
    validate = list(inspect.signature(RiskModel.validate_risk_parameters).parameters)
    assert classify == ["self", "volatility_state", "stop_distance_pct"], classify
    assert validate == ["self", "current_price", "atr_stop", "volatility_state"], validate


def test_a_keyword_the_risk_check_does_not_take_is_refused():
    """
    adx and trend_health were parameters once, and a misspelt keyword is the
    A6 defect's shape: with **kwargs each of them was swallowed and did
    nothing. Without it, Python refuses each one by name.
    """
    model = RiskModel()
    for name, value in (("adx", 30.0), ("trend_health", 80.0),
                        ("volatilty_state", "LOW VOLATILITY")):
        with pytest.raises(TypeError) as excinfo:
            model.validate_risk_parameters(
                current_price=100.0, atr_stop=99.0,
                volatility_state="LOW VOLATILITY", **{name: value})
        assert name in str(excinfo.value), (name, str(excinfo.value))


def test_the_volatility_state_has_no_default():
    """
    It defaulted to "NORMAL", a state the engine never produces. As the
    regime's only input, a default would be a reading nobody took.
    """
    with pytest.raises(TypeError) as excinfo:
        RiskModel().validate_risk_parameters(current_price=100.0, atr_stop=99.0)
    assert "volatility_state" in str(excinfo.value), str(excinfo.value)


# ======================================================================
# 2-4. The table
# ======================================================================

def test_each_volatility_state_has_its_own_regime():
    """
    LOW VOLATILITY is LOW RISK on its own: until fix 3 it needed ADX 25 or
    more, and an unmeasured ADX left it at NORMAL RISK. MEDIUM VOLATILITY is
    NORMAL RISK at any ADX: until fix 3, ADX under 20 made it HIGH
    VOLATILITY RISK. 8.0 itself is not over the line.
    """
    model = RiskModel()
    for state, regime in REGIME_OF.items():
        for stop_pct in (0.2, 0.5, 1.0, 3.0, 6.0, 8.0):
            got = model.classify_risk_regime(state, stop_pct)
            assert got == regime, (state, stop_pct, got)


def test_a_state_the_regime_does_not_know_is_unknown_risk():
    """
    The patch's proposal, Viktor's to reverse: until fix 3 these fell through
    to NORMAL RISK. Among them the engine's own UNKNOWN, the old default
    "NORMAL", and near-misses of the four real states. It decides the label
    only: the risk check still passes, because whether a trade is allowed
    at all is the stop's question, not the regime's.
    """
    model = RiskModel()
    for state in ("UNKNOWN", "NORMAL", "MEDIUM", "low volatility", "", None):
        got = model.classify_risk_regime(state, 1.0)
        assert got == "UNKNOWN RISK", (state, got)

    verdict = model.validate_risk_parameters(
        current_price=100.0, atr_stop=99.0, volatility_state="UNKNOWN")
    assert verdict == (True, "OK", "UNKNOWN RISK"), verdict


def test_a_stop_over_eight_percent_is_extreme_risk_in_every_state():
    model = RiskModel()
    for state in list(REGIME_OF) + ["UNKNOWN", "NORMAL", None]:
        got = model.classify_risk_regime(state, rm.REGIME_EXTREME_STOP_PCT + 1e-9)
        assert got == "EXTREME RISK", (state, got)
        ok, reason, regime = model.validate_risk_parameters(
            current_price=100.0, atr_stop=91.0, volatility_state=state)
        assert (ok, regime) == (False, "EXTREME RISK"), (state, ok, reason, regime)


# ======================================================================
# 5. B8 -- on the engine's own numbers
# ======================================================================

def test_the_regime_names_the_volatility_the_panel_prints():
    """
    The review's B8: a panel could print VOLATILITY : LOW VOLATILITY beside
    RISK REGIME : HIGH VOLATILITY RISK. Swept here over ATR from 0.05% to 6%
    of price, on both sides: the volatility state comes from
    calculate_dynamic_regime, the stop from calculate_stop_targets with that
    state, and the regime from the risk check. Every regime is the one the
    table gives for the state. The only other outcome is a stop under 0.2%,
    refused before any regime is classified.

    It also shows that since fix 1 the 8% test never fires below EXTREME
    VOLATILITY on the engine's own stop: at HIGH VOLATILITY the stop is at
    most 4% x 1.2 x 1.35, or 6.48% of price.
    """
    import pandas as pd
    from models.bias_engine import calculate_dynamic_regime

    model = RiskModel()
    price = 100.0
    seen = set()
    for i in range(1, 121):
        ratio = i * 0.0005
        frame = pd.DataFrame({"close": [price], "ATR": [price * ratio]})
        _, vol = calculate_dynamic_regime(frame)
        for score in (50.0, -50.0):
            stop, _, _, _ = model.calculate_stop_targets(
                current_price=price, atr_val=price * ratio,
                bias_score=score, volatility_state=vol)
            ok, reason, regime = model.validate_risk_parameters(
                current_price=price, atr_stop=stop, volatility_state=vol)
            if regime == "UNKNOWN":
                assert "too tight" in reason, (ratio, vol, reason)
                continue
            assert regime == REGIME_OF[vol], (ratio, vol, regime, reason)
            seen.add(vol)
    assert seen == set(REGIME_OF), seen


# ======================================================================
# 6-7. The constants, the call and the record
# ======================================================================

def test_the_two_adx_constants_are_gone():
    from core.decision_log import FINGERPRINTED_MODULES

    for name in ("REGIME_CHOP_ADX", "REGIME_STRONG_ADX"):
        assert not hasattr(rm, name), name
        assert name not in FINGERPRINTED_MODULES["models.risk_model"], name
    assert "REGIME_EXTREME_STOP_PCT" in FINGERPRINTED_MODULES["models.risk_model"]


def _engine_core_tree():
    with open(ENGINE_CORE, encoding="utf-8") as f:
        return ast.parse(f.read())


def test_engine_core_passes_no_adx_to_the_risk_check():
    calls = [n for n in ast.walk(_engine_core_tree())
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
             and n.func.attr == "validate_risk_parameters"]
    assert len(calls) == 1, len(calls)
    assert not calls[0].args, "the risk check is called positionally"
    keywords = [k.arg for k in calls[0].keywords]
    assert keywords == ["current_price", "atr_stop", "volatility_state"], keywords


def test_the_lineage_no_longer_lists_adx_as_a_risk_input():
    keys = None
    for node in ast.walk(_engine_core_tree()):
        if not isinstance(node, ast.Dict):
            continue
        for key, value in zip(node.keys, node.values):
            if (isinstance(key, ast.Constant) and key.value == "risk_inputs"
                    and isinstance(value, ast.Dict)):
                keys = [k.value for k in value.keys if isinstance(k, ast.Constant)]
    assert keys is not None, "risk_inputs dict literal not found"
    assert "adx" not in keys, (
        "risk_inputs records what fed the risk decision; ADX no longer does", keys)
    assert "volatility_state" in keys and "risk_regime" in keys, keys


# ======================================================================
# 8. The engine path
# ======================================================================

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


def test_on_the_engine_path_the_record_follows_the_table():
    pytest.importorskip("pandas_ta")

    decision = _run_pinned()
    inputs = decision["lineage"]["risk_inputs"]
    assert "adx" not in inputs, sorted(inputs)
    assert "ADX" in decision["lineage"]["indicators_at_decision_bar"], (
        "ADX left risk_inputs only; it is still recorded at the decision bar")

    vol = decision["bias"]["volatility"]
    assert inputs["volatility_state"] == vol, (inputs["volatility_state"], vol)
    assert vol in REGIME_OF, vol
    assert decision["risk"]["risk_regime"] == inputs["risk_regime"] == REGIME_OF[vol], (
        vol, decision["risk"]["risk_regime"], inputs["risk_regime"])
