"""
Round 6 F3 follow-up, 13 September 2026 -- CURRENT PRICE, STOP LOSS and the
three TARGET lines in core/panel_render.py.

THE FINDING

Viktor, after F1/F2/F3 landed: "panel_render.py's atr_stop/targets/current_price
still default to 0.0 inconsistently with the NaN fix F3 just made elsewhere --
a small follow-up patch if you want it closed." Ruled: fix.

render_panel() built these three fields with a finite 0.0 default when the
source key was absent or malformed:

    targets = risk.get("targets", (0, 0, 0))
    current_price = safe_float(exit_data.get("current_price", 0.0))
    stop_loss = safe_float(risk.get("atr_stop", 0.0))

-- the exact fabrication shape signal_router.py's own defaults for these
same three fields were fixed to stop doing at the router, one layer
upstream, in Round 6 F3 (commit 9b34163). Unreachable on the live path
today for the identical reason F3's own fix was unreachable at the router
-- engine_core always sets these keys -- but nothing else on this page
assumes that (swing_struct_line, _entry_zone_lines and _correlation_lines
all already print "not located"/"not measured" instead of a fabricated
number), so this was the last inconsistency of that shape on the panel.

THE FIX

All three now go through safe_float(..., float("nan")) rather than
safe_float(..., 0.0), matching every other "not located" field on this
panel. Every print site is guarded: a NaN price prints "not available" /
"not computed" / "not located" text instead of reaching an f-string price
format directly, which is exactly how this file's own safe_float()
docstring describes fixing an earlier version of this same defect class
(the literal text "$nan" from calculate_stop_targets' NaN path).

The stop_distance / R:R chain downstream of these three fields is also
NaN-aware now: the guard used to be `if stop_loss and current_price`
(truthiness -- NaN is truthy, so this would not have stopped a NaN
current_price or stop_loss from reaching the subtraction), replaced with
an explicit math.isfinite() check on both. A real, measured stop_distance
of exactly 0.0 still reaches the "rr_t* = 0.0" branch unchanged -- a
genuine zero-distance stop is not the same claim as "unknown".

WHAT THESE TESTS HOLD

That the panel no longer prints a fabricated $0.0000 (or a literal "nan")
for any of these three when the engine output does not supply it -- and,
the negative control, that real present values (including a genuine 0.0
atr_stop) still print and compute exactly as before.
"""

import math

from core.panel_render import render_panel


def _decision(risk=None, exit_data=None):
    return {
        "symbol": "TESTUSDT", "timeframe": "4h",
        "bias": {"raw": "NEUTRAL", "detailed": "NEUTRAL", "regime": "NEUTRAL STRUCTURE",
                 "volatility": "LOW VOLATILITY"},
        "trend": {"trend_health": 50.0, "trend_direction": "NEUTRAL",
                  "momentum_mode": "NEUTRAL"},
        "structure": {"regime": "NEUTRAL STRUCTURE", "sequence": "NONE",
                      "volume_sentiment": "NEUTRAL VOLUME"},
        "entry": {"score": 45.0, "entry_status": "ACTIVE ENTRY ZONE"},
        "risk": risk if risk is not None else {},
        "exit": exit_data if exit_data is not None else {},
    }


def _lines_for(panel, prefix):
    """Only the lines starting with `prefix` -- rule 30, shape not substring."""
    return [ln for ln in panel.splitlines() if ln.lstrip().startswith(prefix)]


# ============================================================
# 1. Absent keys do not become zero
# ============================================================

def test_an_absent_current_price_is_not_a_price_of_zero():
    panel = render_panel(_decision(exit_data={}))
    assert panel is not None, "the panel failed to render at all"

    lines = _lines_for(panel, "CURRENT PRICE")
    assert len(lines) == 1, f"expected one CURRENT PRICE line, found {lines!r}"
    assert "not available" in lines[0], (
        f"the panel does not say the price is missing: {lines[0]!r}"
    )
    assert "$0.0000" not in lines[0] and "nan" not in lines[0].lower(), (
        f"the panel still prints a fabricated or literal-nan price: {lines[0]!r}"
    )


def test_an_absent_stop_is_not_a_price_of_zero():
    panel = render_panel(_decision(risk={}))
    assert panel is not None

    lines = _lines_for(panel, "STOP LOSS")
    assert len(lines) == 1, f"expected one STOP LOSS line, found {lines!r}"
    assert "not computed" in lines[0], (
        f"the panel does not say the stop is missing: {lines[0]!r}"
    )
    assert "$0.0000" not in lines[0] and "nan" not in lines[0].lower(), (
        f"the panel still prints a fabricated or literal-nan stop: {lines[0]!r}"
    )


def test_absent_targets_are_not_three_zeros():
    panel = render_panel(_decision(risk={}))
    assert panel is not None

    lines = _lines_for(panel, "TARGET")
    assert len(lines) == 3, f"expected three TARGET lines, found {lines!r}"
    for ln in lines:
        assert "not located" in ln, (
            f"the panel does not say this target is missing: {ln!r}"
        )
        assert "$0.0000" not in ln and "nan" not in ln.lower(), (
            f"the panel still prints a fabricated or literal-nan target: {ln!r}"
        )


def test_a_malformed_targets_value_is_not_three_zeros():
    """The isinstance/len guard's fallback path, not just the .get default."""
    panel = render_panel(_decision(risk={"targets": "not a tuple"}))
    assert panel is not None

    lines = _lines_for(panel, "TARGET")
    assert len(lines) == 3
    for ln in lines:
        assert "not located" in ln, f"malformed targets did not fall back safely: {ln!r}"


def test_a_target_present_without_a_known_stop_shows_rr_not_computed():
    """
    current_price and a real target are both known, but atr_stop is absent --
    stop_distance cannot be computed, so R:R must say so rather than print a
    fabricated ratio computed against a stop_distance of 0.0.
    """
    panel = render_panel(_decision(
        risk={"targets": (0.85, 0.90, 0.95)},
        exit_data={"current_price": 0.80},
    ))
    assert panel is not None

    lines = _lines_for(panel, "TARGET")
    assert len(lines) == 3
    for ln in lines:
        assert "$0.8" in ln or "$0.9" in ln, f"the known target price is missing: {ln!r}"
        assert "R:R 1 : not computed" in ln, (
            f"R:R was computed against an unknown stop distance: {ln!r}"
        )


# ============================================================
# 2. Negative controls -- real, present values survive unchanged
# ============================================================
# MUST PASS BOTH BEFORE AND AFTER THE FIX.

def test_negative_control_a_real_current_price_and_stop_survive():
    panel = render_panel(_decision(
        risk={"atr_stop": 0.72, "targets": (0.85, 0.90, 0.95)},
        exit_data={"current_price": 0.80},
    ))
    assert panel is not None

    price_lines = _lines_for(panel, "CURRENT PRICE")
    stop_lines = _lines_for(panel, "STOP LOSS")
    target_lines = _lines_for(panel, "TARGET")

    assert "$0.8000" in price_lines[0]
    assert "$0.7200" in stop_lines[0]
    assert len(target_lines) == 3
    assert "$0.8500" in target_lines[0]
    assert "$0.9000" in target_lines[1]
    assert "$0.9500" in target_lines[2]
    # stop_distance = |0.80 - 0.72| = 0.08; R:R1 = |0.85-0.80|/0.08 = 0.625
    assert "R:R 1 : 0.62" in target_lines[0] or "R:R 1 : 0.63" in target_lines[0], (
        f"R:R was not computed from the real values: {target_lines[0]!r}"
    )


def test_negative_control_a_real_zero_stop_is_still_a_real_zero():
    """
    A finite 0.0 the ENGINE actually measured (not a missing-key default)
    must still print as $0.0000, not be swallowed into "not computed" --
    safe_float(..., float("nan")) only replaces None/non-finite/absent, a
    real finite zero passes through unchanged, matching _finite_or_nan's
    own negative control at the router.
    """
    panel = render_panel(_decision(
        risk={"atr_stop": 0.0},
        exit_data={"current_price": 0.80},
    ))
    assert panel is not None

    stop_lines = _lines_for(panel, "STOP LOSS")
    assert len(stop_lines) == 1
    assert "$0.0000" in stop_lines[0], (
        f"a genuine zero stop was swallowed into 'not computed': {stop_lines[0]!r}"
    )
    assert "not computed" not in stop_lines[0]


def test_negative_control_lines_still_terminate_properly():
    """
    Shape, not substring (rule 30) -- a line-ending regression here would
    read as a false pass on every assertion above, same trap
    test_the_swing_line_occupies_a_line_of_its_own exists to catch for
    SWING STRUCT.
    """
    panel = render_panel(_decision(risk={}, exit_data={}))
    assert panel is not None

    lines = panel.splitlines()
    price_line = [ln for ln in lines if ln.lstrip().startswith("CURRENT PRICE")]
    assert len(price_line) == 1
    assert "STATUS" not in price_line[0], (
        f"CURRENT PRICE does not terminate its own line: {price_line[0]!r}"
    )

    stop_line = [ln for ln in lines if ln.lstrip().startswith("STOP LOSS")]
    assert len(stop_line) == 1
    assert "TARGET" not in stop_line[0], (
        f"STOP LOSS does not terminate its own line: {stop_line[0]!r}"
    )

    target_lines = [ln for ln in lines if ln.lstrip().startswith("TARGET")]
    assert len(target_lines) == 3, (
        f"expected three separate TARGET lines, got {target_lines!r}"
    )
