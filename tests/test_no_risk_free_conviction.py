"""
Item 14 re-audit, Finding 5 — "AGGRESSIVE" was selected from conviction and
entry quality with no independent risk decision.

THE DEFECT

models/decision_model.py returned "AGGRESSIVE LONG" / "AGGRESSIVE SHORT"
whenever trend_health >= 75, entry_score >= 70, no momentum divergence, and
an active entry — checking only that risk_valid was True, never distinguishing
NORMAL RISK from HIGH VOLATILITY RISK once risk_valid passed. The auditor's
concrete scenario: trend_health=80, entry_score=75, risk_valid=True, but
volatility_state=HIGH VOLATILITY (so risk_model.classify_risk_regime() would
call this HIGH VOLATILITY RISK) still produced AGGRESSIVE LONG. The "full
size" wording sequence item 13/16 removed made the label read like a sizing
decision; removing the words did not change that the label itself was chosen
from directional conviction and entry quality alone.

Item 14 requires: "Directional conviction must never be treated as equivalent
to risk. Being highly confident an asset is bullish does not automatically
justify taking on high risk."

THE FIX, RULED BY VIKTOR, 31 AUGUST 2026 (DELEGATED)

models/risk_model.py's classify_risk_regime() already computed a four-tier
risk regime (EXTREME RISK / HIGH VOLATILITY RISK / NORMAL RISK / LOW RISK);
only the EXTREME-RISK-or-not boolean reached risk_valid, and the three-tier
distinction below EXTREME never left validate_risk_parameters. That function
now returns the regime as a third value, engine_core.py carries it into the
risk dict, and decision_model.py reads it as an INDEPENDENT gate on whether
"AGGRESSIVE" may be used — never on direction (raw_bias, long/short_signal
are untouched) and never on whether a trade is allowed at all (risk_valid
above already decides that). A high-conviction, high-quality setup in an
elevated-risk regime now returns the plain LONG/SHORT it would have earned on
entry quality and trend health alone, not the qualifier claiming extra
conviction justifies extra risk.

VERIFICATION, per the audit's own list: high-conviction inputs across low,
high and extreme volatility (mapped through classify_risk_regime, not
hand-picked strings, so a change to that function's thresholds is exercised
by these tests too), and across wide and tight stops.
"""

from models.decision_model import DecisionModel
from models.risk_model import RiskModel


# A trend_health/entry_score/entry_status combination that clears every
# AGGRESSIVE threshold decision_model.py checks, so the only thing left to
# vary in the tests below is the risk regime.
HIGH_CONVICTION_TREND_HEALTH = 80.0
HIGH_CONVICTION_ENTRY_SCORE = 75.0

# 5 SEPTEMBER 2026: these fixtures never supplied a bias SCORE, only the
# label -- which worked because _determine_final_action read only the label.
# Viktor's ruling of that date added MIN_ACTION_BIAS, so an absent score now
# reads as 0 and every case here returned WAIT.
#
# Completing the fixture rather than relaxing the floor: a decision object
# with no bias score is malformed, and refusing to act on one is the correct
# behaviour. These tests are about the risk regime gating AGGRESSIVE, so the
# score just needs to be past the floor and out of their way.
HIGH_CONVICTION_BIAS_SCORE = 60.0


def _final_action(raw_bias, risk_regime, risk_valid=True,
                   long_signal=False, short_signal=False, macro_bias="NEUTRAL"):
    reasons = []
    action = DecisionModel()._determine_final_action(
        bias={"raw": raw_bias, "score": HIGH_CONVICTION_BIAS_SCORE},
        trend={
            "trend_health": HIGH_CONVICTION_TREND_HEALTH,
            "trend_direction_sign": 1 if raw_bias == "BULLISH" else -1,
            "momentum_divergence": False,
        },
        entry={
            "score": HIGH_CONVICTION_ENTRY_SCORE,
            "entry_status": "ACTIVE ENTRY ZONE",
            "long_signal": long_signal,
            "short_signal": short_signal,
        },
        risk={
            "risk_valid": risk_valid,
            "risk_reason": "OK",
            "validation_state": "NEUTRAL",
            "risk_regime": risk_regime,
        },
        macro_bias=macro_bias,
        reasons=reasons,
    )
    return action, reasons


def test_high_conviction_in_a_normal_risk_regime_is_still_aggressive():
    """
    The control. Without this, a formula that never returns AGGRESSIVE at all
    would pass every test below vacuously.
    """
    action, reasons = _final_action("BULLISH", "NORMAL RISK")
    assert action == "AGGRESSIVE LONG", (
        f"expected AGGRESSIVE LONG on a high-conviction setup in a NORMAL "
        f"RISK regime, got {action!r}.\nReasons: {reasons}"
    )


def test_high_conviction_in_a_low_risk_regime_is_still_aggressive():
    action, reasons = _final_action("BULLISH", "LOW RISK")
    assert action == "AGGRESSIVE LONG", (
        f"expected AGGRESSIVE LONG in a LOW RISK regime, got {action!r}.\n"
        f"Reasons: {reasons}"
    )


def test_the_audits_concrete_scenario_no_longer_returns_aggressive():
    """
    trend_health=80, entry_score=75, raw_bias=BULLISH, risk_valid=True,
    risk_regime=HIGH VOLATILITY RISK — the auditor's exact Finding 5 scenario.
    """
    action, reasons = _final_action("BULLISH", "HIGH VOLATILITY RISK")
    assert action == "LONG", (
        f"expected LONG (not AGGRESSIVE LONG) when the risk regime is HIGH "
        f"VOLATILITY RISK, got {action!r}.\nReasons: {reasons}\n"
        "Directional conviction and entry quality met the old thresholds; "
        "Item 14 requires that not be sufficient once risk is elevated."
    )
    assert "AGGRESSIVE" not in action


def test_high_conviction_in_an_extreme_risk_regime_is_not_aggressive():
    """
    EXTREME RISK ordinarily makes risk_valid False before this branch is ever
    reached (see risk_model.validate_risk_parameters) — this checks the
    AGGRESSIVE gate defensively, in case risk_valid and risk_regime ever
    disagree, since the gate reads risk_regime directly rather than assuming
    risk_valid already ruled it out.
    """
    action, reasons = _final_action("BULLISH", "EXTREME RISK")
    assert "AGGRESSIVE" not in action, (
        f"got {action!r} with risk_regime=EXTREME RISK.\nReasons: {reasons}"
    )


def test_the_short_side_is_gated_the_same_way():
    aggressive, _ = _final_action("BEARISH", "NORMAL RISK")
    capped, reasons = _final_action("BEARISH", "HIGH VOLATILITY RISK")

    assert aggressive == "AGGRESSIVE SHORT", aggressive
    assert capped == "SHORT", (
        f"expected SHORT (not AGGRESSIVE SHORT) in a HIGH VOLATILITY RISK "
        f"regime, got {capped!r}.\nReasons: {reasons}"
    )


def test_the_capped_reasoning_names_the_risk_regime_not_a_position_size():
    """
    The audit's other complaint about this label: "the code describes the
    alternative as not being suitable for 'full size,' even though position
    sizing has been removed." Whatever explains a capped AGGRESSIVE action
    now must name the risk regime, not an absent size.
    """
    _, reasons = _final_action("BULLISH", "HIGH VOLATILITY RISK")
    text = " ".join(reasons).lower()

    assert "full size" not in text and "position size" not in text, (
        f"the explanation for capping AGGRESSIVE still describes an absent "
        f"position size:\n  {text}"
    )
    assert "risk regime" in text and "high volatility risk" in text, (
        f"the explanation does not name the risk regime that caused the cap:"
        f"\n  {text}"
    )


def test_conviction_alone_cannot_select_aggressive_across_every_regime():
    """
    The audit's verification list, run directly: the same high-conviction
    inputs, across every regime classify_risk_regime can produce. Only the
    regimes below EXTREME/HIGH VOLATILITY RISK may return AGGRESSIVE.
    """
    for regime, allowed in (
        ("LOW RISK", True),
        ("NORMAL RISK", True),
        ("HIGH VOLATILITY RISK", False),
        ("EXTREME RISK", False),
    ):
        action, reasons = _final_action("BULLISH", regime)
        is_aggressive = "AGGRESSIVE" in action
        assert is_aggressive == allowed, (
            f"risk_regime={regime!r}: AGGRESSIVE {'was' if is_aggressive else 'was not'} "
            f"returned ({action!r}), expected "
            f"{'allowed' if allowed else 'blocked'}.\nReasons: {reasons}"
        )


# ============================================================
# risk_model.py: the regime actually reaches validate_risk_parameters' caller
# ============================================================

def test_validate_risk_parameters_returns_the_risk_regime():
    """
    classify_risk_regime() always computed this; only a boolean comparison
    against EXTREME RISK used to leave this function. This is the seam
    engine_core.py and decision_model.py now depend on.
    """
    model = RiskModel()

    # Wide stop distance (10%), NORMAL volatility, decent trend health ->
    # NORMAL RISK: not low vol + high health (LOW RISK), not high/extreme vol
    # or low health (HIGH VOLATILITY RISK), not >8% stop or EXTREME vol
    # (EXTREME RISK).
    valid, reason, regime = model.validate_risk_parameters(
        current_price=100.0, atr_stop=93.0,  # 7% stop
        volatility_state="NORMAL", trend_health=60.0,
    )
    assert valid is True
    assert regime == "NORMAL RISK", f"expected NORMAL RISK, got {regime!r} ({reason})"


def test_validate_risk_parameters_regime_across_volatility_tiers():
    """The audit's own verification list: low, high, and extreme volatility."""
    model = RiskModel()

    _, _, low_vol = model.validate_risk_parameters(
        current_price=100.0, atr_stop=99.0,  # 1% stop, comfortably inside bounds
        volatility_state="LOW VOLATILITY", trend_health=80.0,
    )
    assert low_vol == "LOW RISK", low_vol

    _, _, high_vol = model.validate_risk_parameters(
        current_price=100.0, atr_stop=95.0,  # 5% stop
        volatility_state="HIGH VOLATILITY", trend_health=80.0,
    )
    assert high_vol == "HIGH VOLATILITY RISK", high_vol

    valid, reason, extreme_vol = model.validate_risk_parameters(
        current_price=100.0, atr_stop=95.0,  # 5% stop
        volatility_state="EXTREME VOLATILITY", trend_health=80.0,
    )
    assert extreme_vol == "EXTREME RISK", extreme_vol
    assert valid is False, (
        "EXTREME RISK must still fail risk_valid outright — Item 14 adds an "
        "independent cap on AGGRESSIVE for the tier below EXTREME; it does "
        "not loosen the existing EXTREME gate."
    )


def test_validate_risk_parameters_regime_across_stop_widths():
    """The audit's own verification list: wide and tight stops."""
    model = RiskModel()

    # A stop distance just past 8% is EXTREME RISK by classify_risk_regime's
    # own threshold, regardless of volatility_state.
    _, _, wide = model.validate_risk_parameters(
        current_price=100.0, atr_stop=91.5,  # 8.5% stop
        volatility_state="NORMAL", trend_health=80.0,
    )
    assert wide == "EXTREME RISK", wide

    _, _, tight = model.validate_risk_parameters(
        current_price=100.0, atr_stop=99.5,  # 0.5% stop
        volatility_state="NORMAL", trend_health=80.0,
    )
    assert tight in ("NORMAL RISK", "LOW RISK"), tight
