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
round 3, which is the divergence recorded in docs/PHASE7_NEXT.md (moved to
docs/PHASE7_HISTORY.md, "What comes next", on 18 September 2026).

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

FIX 3, 6 OCTOBER 2026 -- FIVE OF THESE TESTS ARE GONE

Round 8 found the ADX read coupled too (its F2): trend health spends up to
40 of its 100 points on the same raw ADX, so the regime and bias_score still
moved together. Viktor's triage ruled that the regime comes from volatility
alone (docs/PHASE7_DECISIONS.md, "Ruling, 5 October 2026 -- round 8
triaged ...", point 3). The five tests that pinned ADX's part -- the old
trend_health boundaries read as ADX, the chop test, the strong-trend test,
the constants being read, and an absent ADX -- tested a rule that no longer
exists, and were removed rather than rewritten. What the regime does now is
pinned in tests/test_regime_from_volatility_alone.py. The two trend_health
tests and the two controls stay: the first without its ADX assertion, the
controls without their ADX arguments.
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
    # FIX 3, 6 October 2026: an assertion that "adx" IS a parameter stood
    # here. It is not, since fix 3; tests/test_regime_from_volatility_alone.py
    # pins the whole signature.


def test_validate_risk_parameters_rejects_trend_health_rather_than_ignoring_it():
    """
    validate_risk_parameters takes **kwargs, so a caller left on the old
    signature would have had trend_health silently absorbed and ADX silently
    defaulted to None -- the run would keep working while quietly losing the
    ability to reach LOW RISK. That is the A6 defect this same function
    already carries a comment about, so the stale kwarg is refused loudly.

    Fails against pre-fix code, which accepts trend_health as a real
    parameter and returns a verdict.

    FIX 3, 6 October 2026: validate_risk_parameters takes no **kwargs now,
    so Python itself refuses trend_health -- and adx, and any keyword it
    does not take. The test holds as it stands.
    """
    model = RiskModel()
    with pytest.raises(TypeError) as excinfo:
        model.validate_risk_parameters(
            current_price=100.0, atr_stop=99.0,
            volatility_state="LOW VOLATILITY", trend_health=80.0,
        )
    assert "trend_health" in str(excinfo.value)


# FIX 3, 6 October 2026: five tests stood here --
# test_the_old_trend_health_boundaries_no_longer_exist, and, in sections 2
# and 3, test_chop_grade_adx_raises_the_regime,
# test_the_strong_trend_boundary_is_adx_not_trend_health,
# test_the_adx_thresholds_are_read_from_the_fingerprinted_constants and
# test_an_absent_adx_is_not_turned_into_a_regime. They pinned that ADX
# decided the regime, at REGIME_CHOP_ADX and REGIME_STRONG_ADX, and that an
# absent ADX was no regime. The regime reads no ADX now; see the module
# docstring.


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
    # FIX 3, 6 October 2026: each call passed ADX 50.0 as a third argument
    # until fix 3.
    assert model.classify_risk_regime("EXTREME VOLATILITY", 1.0) == "EXTREME RISK"
    assert model.classify_risk_regime("NORMAL", 9.0) == "EXTREME RISK"
    assert model.classify_risk_regime("HIGH VOLATILITY", 1.0) == "HIGH VOLATILITY RISK"


def test_control_extreme_risk_still_fails_risk_valid_outright():
    """
    The other half of the same control, one level up: EXTREME RISK must still
    refuse the trade, not merely label it. Passes on both sides.
    """
    model = RiskModel()
    # FIX 3, 6 October 2026: adx=50.0 until fix 3.
    valid, reason, regime = model.validate_risk_parameters(
        current_price=100.0, atr_stop=95.0,
        volatility_state="EXTREME VOLATILITY",
    )
    assert regime == "EXTREME RISK"
    assert valid is False
    assert "EXTREME" in reason
