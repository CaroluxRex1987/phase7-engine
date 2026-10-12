"""
Round 8, F9 -- claims in the artifact that the code beside them did not support.

Round 8's auditor (MiMo-V2.6-Pro, run 2, 4 October 2026) reported four
statements that the code next to them contradicted (T1 Item 8, Epistemic
Honesty). Viktor triaged them into the label and record batch on 5 October,
and on 12 October ruled the shape of the fix and two additions, by agreeing to
Claude's suggestion:

  1. StructureEngine's "state tracking for regime persistence" persisted
     nothing -- calculate_structure() builds a fresh engine per call. Now a
     plain function of the frame (option C, as for finding 18). A frame too
     short to read returns UNKNOWN STRUCTURE, not NEUTRAL STRUCTURE.
  2. trend_health's failure labels: momentum_mode and trend_regime were
     NEUTRAL, which no measurement produces; trend_direction was NEUTRAL, a
     flat market nobody measured. All three are UNAVAILABLE.
  3. volume_agreement reported a failed volume read as "Volume sentiment is
     neutral."
  4. The ADX failure note claimed "25 of its 100 points" (the ceiling is 40)
     and left out that no trade is taken without an ADX reading.

Plus the panel's TREND line, whose fallbacks were NEUTRAL / HEALTHY.

Every test here is behavioural -- each one runs the code, none of them reads a
source file -- and none takes a pytest fixture, so run_tests.py's watched
error count does not move.
"""

import json
import os
import re

import numpy as np
import pandas as pd
import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _pandas_ta_available():
    try:
        import pandas_ta  # noqa: F401
        return True
    except Exception:
        return False


def _closes(values):
    close = pd.Series(np.asarray(values, dtype=float))
    return pd.DataFrame({
        "open": close, "high": close + 0.01, "low": close - 0.01,
        "close": close, "volume": 1000.0,
    })


def _gap_frame(gap_pct, rows=40):
    """A frame whose 5-bar vs 15-bar close-mean gap is exactly `gap_pct`.

    The last 5 closes sit at 100 * (1 + g) and the 10 before them at 100,
    so mean5 = 100(1 + g), mean15 = 100(1 + g/3), and the gap is
    (2g/3) / (1 + g/3). Solved for g so the gap comes out as asked.
    """
    g = 3.0 * gap_pct / (2.0 - gap_pct)
    values = [100.0] * (rows - 5) + [100.0 * (1.0 + g)] * 5
    return _closes(values)


# ======================================================================
# F9(1) -- the structure regime carries no state
# ======================================================================

def test_the_gap_helper_builds_the_gap_it_is_asked_for():
    """The tests below lean on this helper; check it before trusting them."""
    for want in (0.0010, -0.0010, 0.0100, -0.0100):
        closes = _gap_frame(want)["close"].to_numpy()
        got = (closes[-5:].mean() - closes[-15:].mean()) / closes[-15:].mean()
        assert abs(got - want) < 1e-12, (want, got)


def test_a_reused_engine_answers_as_a_fresh_one_does():
    """
    The assertion the old code fails. A gap of +0.10% is inside the 0.15%
    band, so a fresh engine reads NEUTRAL STRUCTURE. The old engine, reused
    after reading BULLISH TREND, held BULLISH TREND there -- its hysteresis
    branch, which only a reused instance ever reached.
    """
    from structure.structure import StructureEngine

    inside_band = _gap_frame(0.0010)
    fresh = StructureEngine()._detect_regime(inside_band)
    assert fresh == "NEUTRAL STRUCTURE", fresh

    for first in (_gap_frame(0.0100), _gap_frame(-0.0100)):
        engine = StructureEngine()
        engine._detect_regime(first)
        again = engine._detect_regime(inside_band)
        assert again == fresh, (
            f"after reading {engine._detect_regime(first)!r}, the same engine "
            f"read {again!r} on a frame a fresh engine reads as {fresh!r}: the "
            f"regime depends on what the instance saw before"
        )


def test_the_regime_reads_the_side_the_gap_points_to_outside_the_band():
    from structure.structure import StructureEngine

    t = StructureEngine.REGIME_HYSTERESIS_THRESHOLD
    assert StructureEngine()._detect_regime(_gap_frame(2 * t)) == "BULLISH TREND"
    assert StructureEngine()._detect_regime(_gap_frame(-2 * t)) == "BEARISH TREND"
    assert StructureEngine()._detect_regime(_gap_frame(t / 2)) == "NEUTRAL STRUCTURE"
    assert StructureEngine()._detect_regime(_gap_frame(-t / 2)) == "NEUTRAL STRUCTURE"


def test_a_frame_too_short_to_read_is_unknown_not_neutral():
    from structure.structure import StructureEngine

    short = _closes([100.0 + i for i in range(14)])
    assert StructureEngine()._detect_regime(short) == "UNKNOWN STRUCTURE"
    assert StructureEngine()._detect_regime(None) == "UNKNOWN STRUCTURE"

    # Still an ordinary return, not a degradation -- the decision
    # test_swing_structure_is_not_invented.py records for not-enough-data.
    out = StructureEngine().analyze(short, current_price=113.0)
    assert out["regime"] == "UNKNOWN STRUCTURE", out["regime"]
    assert not any("regime" in d for d in out["degraded_inputs"]), (
        out["degraded_inputs"])


# ======================================================================
# F9(2) -- trend_health's failure labels
# ======================================================================

def _assert_unavailable(out, how):
    for key in ("momentum_mode", "trend_regime", "trend_direction"):
        assert out[key] == "UNAVAILABLE", (
            f"{how}: {key} is {out[key]!r}; a run that measured nothing must "
            f"not print a reading")
    assert out["degraded_inputs"], f"{how}: the failure was not recorded"


def test_trend_health_with_no_frame_reports_unavailable():
    from indicators.trend_health import compute_trend_health

    _assert_unavailable(compute_trend_health(None), "no frame")


def test_trend_health_without_its_slopes_reports_unavailable():
    """The reachable one: indicators.py drops a column it could not compute."""
    from indicators.trend_health import compute_trend_health

    frame = _closes([100.0 + 0.1 * i for i in range(40)])
    _assert_unavailable(compute_trend_health(frame), "no EMA slope columns")


def test_unavailable_trend_direction_moves_no_entry_score():
    """
    The ruling rested on this: entry_model's trend multiplier is 1.0 for
    every label but BULLISH and BEARISH, so UNAVAILABLE scores exactly as
    NEUTRAL did. BULLISH must score differently on the same input, or the
    equality would prove nothing (the negative control inside the test).
    """
    if not _pandas_ta_available():
        pytest.skip("the indicator frame needs pandas_ta")
    import indicators.indicators as ind
    from models.entry_model import calculate_entry_quality

    path = os.path.join(REPO_ROOT, "tests", "fixtures", "ohlcv_clean_4h.csv")
    frame, _failures = ind.add_technical_indicators(pd.read_csv(path))
    price = float(frame["close"].iloc[-1])

    def score(direction, label):
        return calculate_entry_quality(
            frame, price * 0.98, price, trade_direction=direction,
            trend_direction=label)

    for direction, aligned in (("LONG", "BULLISH"), ("SHORT", "BEARISH")):
        neutral = score(direction, "NEUTRAL")
        unavailable = score(direction, "UNAVAILABLE")
        assert json.dumps(neutral, sort_keys=True, default=str) == \
            json.dumps(unavailable, sort_keys=True, default=str), direction
        assert score(direction, aligned)["trend_multiplier"] != \
            neutral["trend_multiplier"], (
            f"{aligned} did not move a {direction} score, so the comparison "
            f"above could not have failed")


# ======================================================================
# F9(3) -- a failed volume read is not a neutral one
# ======================================================================

def test_a_failed_volume_read_is_not_reported_as_neutral():
    if not _pandas_ta_available():
        pytest.skip("core.engine_core imports pandas_ta at module level")
    from core.engine_core import volume_agreement

    for bias in ("BULLISH", "BEARISH", "NEUTRAL"):
        delta, note = volume_agreement("UNKNOWN VOLUME", bias)
        assert delta == 0.0, (bias, delta)
        assert "neutral" not in note.lower(), (
            f"a failed volume read was reported as {note!r}")
        assert "could not be read" in note and "UNKNOWN VOLUME" in note, note


def test_a_neutral_volume_read_is_still_reported_as_neutral():
    """Negative control: the real neutral reading keeps its sentence."""
    if not _pandas_ta_available():
        pytest.skip("core.engine_core imports pandas_ta at module level")
    from core.engine_core import volume_agreement

    for bias in ("BULLISH", "BEARISH"):
        assert volume_agreement("NEUTRAL VOLUME", bias) == (
            0.0, "Volume sentiment is neutral.")


# ======================================================================
# F9(4) -- what a failed ADX actually costs
# ======================================================================

def test_the_adx_failure_note_states_what_is_lost():
    """
    Breaks ta.adx for real and reads the recorded consequence -- the way
    test_degraded_state.py simulates a failure. The note's number is checked
    against trend_health's own ceiling, not against a literal: ADX far above
    33.3 must give an adx_strength of exactly the number the note names.
    """
    if not _pandas_ta_available():
        pytest.skip("pandas_ta not installed")
    import indicators.indicators as ind
    from indicators.trend_health import compute_trend_health

    path = os.path.join(REPO_ROOT, "tests", "fixtures", "ohlcv_clean_4h.csv")
    df = pd.read_csv(path)

    original = ind.ta.adx
    try:
        ind.ta.adx = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom"))
        _frame, failures = ind.add_technical_indicators(df)
    finally:
        ind.ta.adx = original

    notes = [f.consequence for f in failures if f.indicator == "ADX"]
    assert len(notes) == 1, [f.indicator for f in failures]
    note = notes[0]

    # The ceiling, measured: trend health on rising slopes with ADX 0 and
    # ADX 99 differs by the ADX component's full worth.
    rows = 40
    base = _closes([100.0 + 0.1 * i for i in range(rows)])
    base["EMA20_Slope"] = 0.5
    base["EMA50_Slope"] = 0.5
    base["RSI"] = 55.0
    low = compute_trend_health(base.assign(ADX=0.0))["trend_health"]
    high = compute_trend_health(base.assign(ADX=99.0))["trend_health"]
    ceiling = high - low
    assert ceiling > 0, (low, high)
    assert f"up to {ceiling:g} of its 100 points" in note, (ceiling, note)
    assert "25 of its 100" not in note, note
    assert "no trade" in note, note


# ======================================================================
# The panel's TREND line
# ======================================================================

def test_the_trend_line_prints_unknown_for_a_missing_label():
    from core.panel_render import render_panel

    fixture = os.path.join(REPO_ROOT, "tests", "fixtures", "golden_decision.json")
    if not os.path.exists(fixture):
        pytest.skip("golden fixture not present")
    with open(fixture, encoding="utf-8") as fh:
        decision = json.load(fh)

    decision["trend"].pop("trend_direction", None)
    decision["trend"].pop("momentum_mode", None)
    panel = re.sub(r"\x1b\[[0-9;]*m", "", render_panel(decision))

    lines = [l for l in panel.splitlines() if l.startswith("TREND      :")]
    assert len(lines) == 1, lines
    assert "UNKNOWN / UNKNOWN" in lines[0], lines[0]
    assert "NEUTRAL" not in lines[0] and "HEALTHY" not in lines[0], lines[0]
