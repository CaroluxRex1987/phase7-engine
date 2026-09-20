"""
Round 6 (Meta Muse Spark 1.3), F3 -- Item 13 Fail Safely / Item 8 Epistemic
Honesty, Minor, unreachable on the live path today.

THE FINDING

models/signal_router.py's _build_decision_object assembled six fields with a
finite 0.0 default when the source key was absent:

    "zone_lower":          float(entry.get("zone_lower", 0.0))
    "zone_upper":          float(entry.get("zone_upper", 0.0))
    "distance_from_zone":  float(entry.get("distance_from_zone", 0.0))
    "atr_stop":            float(risk.get("atr_stop", 0.0))
    "targets":             (float(t) for t in ...), with a (0.0, 0.0, 0.0)
                            fallback when "targets" was absent or malformed
    "current_price":       float(exit_data.get("current_price", 0.0))

A price this instrument never traded, presented downstream exactly like a
real, located level -- "$0.0000 - $0.0000 / 0.00% away" is the strongest
claim an entry-zone line can make, on the one run that located nothing.
Unreachable today because engine_core always sets every one of these keys
(confirmed by _validate_engine_output requiring the containing block to be
present, not what is under it) -- one edit upstream away from firing, the
identical fabrication shape as the close*0.99 and swing_struct=current_price
defects already removed elsewhere in this project.

THE FIX

RULED, 13 September 2026: fix. All six now go through
SignalRouter._finite_or_nan, the same treatment structure.hvn/lvn and
structure.swing_struct already get two lines above the entry block. NaN is
what an absent measurement means everywhere else in this decision object;
these six fields were the last place still capable of inventing a zero
instead.

Three of the six (zone_lower, zone_upper, distance_from_zone) reach
panel_render.py, which was ALREADY reading them with a NaN default
(safe_float(..., float("nan"))) for exactly this "not located" case -- so
this fix closes the producer half of a pair whose consumer half was fixed
earlier (the same shape as the swing_struct fix's own history, noted in this
file's module comment). atr_stop, targets and current_price reach
panel_render.py through a DIFFERENT, older safe_float() call that still
defaults a non-finite value back to 0.0 there; that mismatch is observed, not
closed, by this patch. It was closed later, by 154e534 (round 6 F4; see
docs/PHASE7_HISTORY.md, moved there from PHASE7_NEXT.md on 18 September 2026).

WHAT THESE TESTS HOLD

That the decision object no longer invents a zero for any of the six when
the engine output does not supply it, and -- the negative control, named as
such -- that a real, present value at each of the six still passes through
this assembly unchanged. A producer rewritten to return NaN unconditionally
would satisfy every "does not invent" test below and destroy the field.
"""

import math

from models.signal_router import SignalRouter


def _bias():
    return {"raw": "NEUTRAL", "detailed": "NEUTRAL", "score": 0.0,
            "regime": "NEUTRAL STRUCTURE", "volatility": "LOW VOLATILITY"}


def _trend():
    return {"trend_health": 50.0, "trend_exhaustion": False,
            "momentum_mode": "NEUTRAL", "momentum_divergence": False,
            "trend_direction": "NEUTRAL"}


def _structure():
    return {"regime": "NEUTRAL STRUCTURE", "sequence": "NONE",
            "hvn": 1.0, "lvn": 1.0, "volume_sentiment": "NEUTRAL VOLUME"}


def _build(entry=None, risk=None, exit_data=None):
    router = SignalRouter(engine_core=object())
    return router._build_decision_object(
        symbol="TESTUSDT", timeframe="4h",
        bias=_bias(), trend=_trend(), structure=_structure(),
        entry=entry if entry is not None else {},
        risk=risk if risk is not None else {},
        exit_data=exit_data if exit_data is not None else {},
        macro_bias="NEUTRAL", chart_path="",
    )


# ============================================================
# 1. Absent keys do not become zero
# ============================================================

def test_an_absent_entry_zone_is_not_located_at_zero():
    out = _build(entry={"score": 50.0})

    assert math.isnan(out["entry"]["zone_lower"]), (
        f"zone_lower with no source key came back {out['entry']['zone_lower']!r}, "
        f"not NaN"
    )
    assert math.isnan(out["entry"]["zone_upper"]), (
        f"zone_upper with no source key came back {out['entry']['zone_upper']!r}, "
        f"not NaN"
    )
    assert math.isnan(out["entry"]["distance_from_zone"]), (
        f"distance_from_zone with no source key came back "
        f"{out['entry']['distance_from_zone']!r}, not NaN"
    )


def test_an_absent_stop_is_not_a_price_of_zero():
    out = _build(risk={"risk_valid": True, "risk_reason": "ok",
                        "risk_regime": "NORMAL RISK"})

    assert math.isnan(out["risk"]["atr_stop"]), (
        f"atr_stop with no source key came back {out['risk']['atr_stop']!r}, "
        f"not NaN"
    )


def test_an_absent_targets_tuple_is_not_three_zeros():
    out = _build(risk={"risk_valid": True, "risk_reason": "ok",
                        "risk_regime": "NORMAL RISK"})

    for i, t in enumerate(out["risk"]["targets"]):
        assert math.isnan(t), (
            f"targets[{i}] with no source key came back {t!r}, not NaN"
        )


def test_a_malformed_targets_value_is_not_three_zeros():
    """The isinstance/len guard's fallback path, not just the .get default."""
    out = _build(risk={"risk_valid": True, "risk_reason": "ok",
                        "risk_regime": "NORMAL RISK", "targets": "not a tuple"})

    for i, t in enumerate(out["risk"]["targets"]):
        assert math.isnan(t), (
            f"targets[{i}] from a malformed source value came back {t!r}, "
            f"not NaN"
        )


def test_an_absent_current_price_is_not_a_price_of_zero():
    out = _build(exit_data={})

    assert math.isnan(out["exit"]["current_price"]), (
        f"current_price with no source key came back "
        f"{out['exit']['current_price']!r}, not NaN"
    )


# ============================================================
# 2. Negative controls -- a real, present value survives unchanged
# ============================================================
# MUST PASS BOTH BEFORE AND AFTER THE FIX.

def test_negative_control_a_real_entry_zone_survives():
    out = _build(entry={"score": 50.0, "zone_lower": 0.75, "zone_upper": 0.80,
                         "distance_from_zone": 2.5})

    assert out["entry"]["zone_lower"] == 0.75
    assert out["entry"]["zone_upper"] == 0.80
    assert out["entry"]["distance_from_zone"] == 2.5


def test_negative_control_a_real_stop_and_targets_survive():
    out = _build(risk={"risk_valid": True, "risk_reason": "ok",
                        "risk_regime": "NORMAL RISK", "atr_stop": 0.72,
                        "targets": (0.85, 0.90, 0.95)})

    assert out["risk"]["atr_stop"] == 0.72
    assert out["risk"]["targets"] == (0.85, 0.90, 0.95)


def test_negative_control_a_real_current_price_survives():
    out = _build(exit_data={"current_price": 0.8017})

    assert out["exit"]["current_price"] == 0.8017


def test_negative_control_a_real_zero_price_is_still_a_real_zero():
    """
    A finite 0.0 that the ENGINE actually measured (not a missing-key
    default) must still come through as 0.0, not be swallowed into NaN by
    this fix. _finite_or_nan only replaces None/non-finite/absent -- a real
    zero is finite and passes through unchanged.
    """
    out = _build(risk={"risk_valid": True, "risk_reason": "ok",
                        "risk_regime": "NORMAL RISK", "atr_stop": 0.0})

    assert out["risk"]["atr_stop"] == 0.0
