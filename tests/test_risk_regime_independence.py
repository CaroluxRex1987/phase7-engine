"""
ITEM 14 — the risk regime is classified independently of the conviction pipeline.

THE DEFECT

Item 14 of the Constitution requires that directional conviction is never
treated as equivalent to risk. The 31 August fix gave decision_model.py an
independent risk-regime gate on the AGGRESSIVE label, and
core/decision_contract.py said in a comment that the gate was independent of
trend health.

It was not. risk_model.classify_risk_regime() took trend_health as a
parameter and branched on it twice: below 40 forced HIGH VOLATILITY RISK, and
70-or-above was required to reach LOW RISK. trend_health is simultaneously
WEIGHT_TREND_HEALTH = 0.30 of bias_score -- the largest single factor in the
engine's conviction number. So one reading moved the conviction gate and the
"independent" risk gate together, in the same direction: a strong trend
raised confidence AND lowered assessed risk. An independent check that
correlates with the thing it is checking is not a check.

Kimi named this as Finding 4 in round 4. GLM graded Item 14 Compliant in
round 3, which is the divergence recorded in docs/PHASE7_NEXT.md.

THE FIX, RULED BY VIKTOR, 11 SEPTEMBER 2026

The risk regime determines itself. classify_risk_regime() reads ADX, which
trend_health is computed FROM (adx_strength is one of its three terms)
rather than derived from, at the two thresholds this codebase already uses
for the same market states in indicators/trend_health.py: ADX < 20 is its
"MEAN REVERTING / CHOP" boundary, ADX >= 25 its "STRONG TREND" confirmation.

WHAT THESE TESTS PIN, AND WHAT THEY DO NOT

They pin that trend_health cannot reach the risk regime at all, that ADX now
decides it, and that an unmeasured ADX is not turned into a regime in either
direction. They do NOT pin that ADX is the correct risk proxy -- that is an
empirical question this project cannot answer before backtesting, and the
constants block in models/risk_model.py records the one honest limit: ADX
still reaches bias_score indirectly through continuation_strength.

Five of these fail against pre-fix code on behavioural assertions; two are
controls that must pass on both sides.
"""

import inspect

import pytest

from models.risk_model import RiskModel
import models.risk_model as risk_model


# ======================================================================
# 1. trend_health cannot reach the regime at all
# ======================================================================

def test_trend_health_is_not_a_parameter_of_classify_risk_regime():
    """
    The structural half. Fails against pre-fix code, where the parameter is
    literally named trend_health.
    """
    params = list(inspect.signature(RiskModel.classify_risk_regime).parameters)
    assert "trend_health" not in params, (
        f"classify_risk_regime still takes trend_health: {params}"
    )
    assert "adx" in params, f"classify_risk_regime does not take adx: {params}"


def test_validate_risk_parameters_rejects_trend_health_rather_than_ignoring_it():
    """
    validate_risk_parameters takes **kwargs, so a caller left on the old
    signature would have had trend_health silently absorbed and ADX silently
    defaulted to None -- the run would keep working while quietly losing the
    ability to reach LOW RISK. That is the A6 defect this same function
    already carries a comment about, so the stale kwarg is refused loudly.

    Fails against pre-fix code, which accepts trend_health as a real
    parameter and returns a verdict.
    """
    model = RiskModel()
    with pytest.raises(TypeError) as excinfo:
        model.validate_risk_parameters(
            current_price=100.0, atr_stop=99.0,
            volatility_state="LOW VOLATILITY", trend_health=80.0,
        )
    assert "trend_health" in str(excinfo.value)


def test_the_old_trend_health_boundaries_no_longer_exist():
    """
    The behavioural half. The two numbers that used to be branch boundaries --
    REGIME_LOW_TREND_HEALTH = 40 and REGIME_HIGH_TREND_HEALTH = 70 -- must no
    longer be boundaries of anything, because nothing reads trend_health.

    Both pairs straddle an old boundary and must now return the SAME regime as
    each other. Against pre-fix code each pair returns two different regimes,
    which is exactly the coupling Item 14 objects to.
    """
    model = RiskModel()

    # Straddling the old 40: pre-fix, 39 -> HIGH VOLATILITY RISK and
    # 41 -> NORMAL RISK. Both are ordinary trending ADX values now.
    assert (model.classify_risk_regime("NORMAL", 1.0, 39.0)
            == model.classify_risk_regime("NORMAL", 1.0, 41.0)
            == "NORMAL RISK")

    # Straddling the old 70 under low volatility: pre-fix, 69 -> NORMAL RISK
    # and 71 -> LOW RISK. Both are above REGIME_STRONG_ADX now.
    assert (model.classify_risk_regime("LOW VOLATILITY", 1.0, 69.0)
            == model.classify_risk_regime("LOW VOLATILITY", 1.0, 71.0)
            == "LOW RISK")


# ======================================================================
# 2. ADX decides it, at the documented thresholds
# ======================================================================

def test_chop_grade_adx_raises_the_regime():
    """
    ADX below REGIME_CHOP_ADX is elevated risk even when volatility_state
    itself is calm.

    Split by kind, because the two assertions behave differently pre-fix: the
    FIRST passes on both sides by coincidence (19.0 read as trend_health is
    also below the old REGIME_LOW_TREND_HEALTH of 40, so pre-fix code returns
    the same string for an unrelated reason). The SECOND is the one that
    fails: 21.0 is above the ADX chop threshold but still far below 40, so
    pre-fix code calls it HIGH VOLATILITY RISK where this asserts NORMAL RISK.
    """
    model = RiskModel()
    assert model.classify_risk_regime("NORMAL", 1.0, 19.0) == "HIGH VOLATILITY RISK"
    assert model.classify_risk_regime("NORMAL", 1.0, 21.0) == "NORMAL RISK"


def test_the_strong_trend_boundary_is_adx_not_trend_health():
    """
    LOW RISK requires low volatility AND ADX >= REGIME_STRONG_ADX (25).

    This is the test that most directly fails pre-fix: 26.0 is comfortably
    above the ADX strong-trend threshold but far BELOW the old
    REGIME_HIGH_TREND_HEALTH of 70, so pre-fix code returns NORMAL RISK where
    this asserts LOW RISK.
    """
    model = RiskModel()
    assert model.classify_risk_regime("LOW VOLATILITY", 1.0, 26.0) == "LOW RISK"
    assert model.classify_risk_regime("LOW VOLATILITY", 1.0, 24.0) == "NORMAL RISK"


def test_the_adx_thresholds_are_read_from_the_fingerprinted_constants():
    """
    A declaration test proves the names exist; this proves the arithmetic
    reads them, which is what keeps them meaningful in the run hash.

    Deliberately NOT using the monkeypatch fixture. run_tests.py is a
    fixture-free runner -- it calls every test_* function with no arguments,
    so a test taking a fixture becomes an ERROR there, and that error count is
    a watched invariant (29). Writing this one with try/finally instead of
    monkeypatch is what keeps the count at 29 rather than moving it to 30 for
    a test that had no need of a fixture in the first place.
    """
    model = RiskModel()
    original = risk_model.REGIME_CHOP_ADX
    try:
        assert model.classify_risk_regime("NORMAL", 1.0, 22.0) == "NORMAL RISK"
        risk_model.REGIME_CHOP_ADX = 30.0
        assert model.classify_risk_regime("NORMAL", 1.0, 22.0) == "HIGH VOLATILITY RISK", (
            "REGIME_CHOP_ADX is fingerprinted but classify_risk_regime does not read it"
        )
    finally:
        risk_model.REGIME_CHOP_ADX = original


# ======================================================================
# 3. An unmeasured ADX is not a regime — neither direction
# ======================================================================

def test_an_absent_adx_is_not_turned_into_a_regime():
    """
    indicators.py drops a column it could not compute rather than inventing
    one, so ADX can genuinely be absent. Absent must not be read as chop
    (which would assert instability nobody measured) and must not be read as
    a strong trend (which would hand out LOW RISK for the same reason).

    Both assertions fail against pre-fix code for the same underlying reason:
    it has no absent case at all -- None raises TypeError on the first
    comparison against a float.
    """
    model = RiskModel()
    assert model.classify_risk_regime("NORMAL", 1.0, None) == "NORMAL RISK"
    assert model.classify_risk_regime("LOW VOLATILITY", 1.0, None) == "NORMAL RISK"
    assert model.classify_risk_regime("NORMAL", 1.0, float("nan")) == "NORMAL RISK"


# ======================================================================
# 4. Negative controls — must pass on BOTH sides of the fix
# ======================================================================

def test_control_extreme_gates_are_untouched():
    """
    Item 14 adds an independent cap below EXTREME; it must not loosen the
    EXTREME gate. Neither branch reads ADX or trend_health, so this passes
    before and after and would catch a fix that rewrote more than it claimed.
    """
    model = RiskModel()
    assert model.classify_risk_regime("EXTREME VOLATILITY", 1.0, 50.0) == "EXTREME RISK"
    assert model.classify_risk_regime("NORMAL", 9.0, 50.0) == "EXTREME RISK"
    assert model.classify_risk_regime("HIGH VOLATILITY", 1.0, 50.0) == "HIGH VOLATILITY RISK"


def test_control_extreme_risk_still_fails_risk_valid_outright():
    """
    The other half of the same control, one level up: EXTREME RISK must still
    refuse the trade, not merely label it. Passes on both sides.
    """
    model = RiskModel()
    valid, reason, regime = model.validate_risk_parameters(
        current_price=100.0, atr_stop=95.0,
        volatility_state="EXTREME VOLATILITY", adx=50.0,
    )
    assert regime == "EXTREME RISK"
    assert valid is False
    assert "EXTREME" in reason
