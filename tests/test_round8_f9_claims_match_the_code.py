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

THE REDESIGN'S STAGE 5, 15 November 2026 -- WHAT IS LEFT OF EACH

F9(1) stands unchanged. The other three and the TREND line lose most of
their subject, and the tests follow:

  F9(2)  All three labels are gone with trend health. What a failed run of
         that module now reports is an ADX of None and a named failure, so
         the two tests below hold that instead. The one that fed it a frame
         WITHOUT ITS EMA SLOPE COLUMNS is gone: the module does not read
         them any more, so such a frame is no longer a failure at all. The
         reachable failure is a missing ADX column, and that is what it
         tests now.
  F9(3)  volume_agreement is gone with the validation block. Both of its
         tests go: no label is scored or answered anywhere, so a failed
         volume read cannot be reported as a neutral one.
  F9(4)  The ADX note's first half named trend health's 40-point component
         and is gone with it; the half that mattered, and that F9(4) added,
         is the confirmation gate refusing both sides. The test checks that
         half and that no point budget has come back -- the third time this
         one string has outlived the calculation it described.
  TREND  The line itself is gone. That the panel no longer prints it, or
         VALIDATION, CONFIDENCE or TRADE QUALITY, is held in
         test_panel_prints_only_what_was_computed.py, beside the lines it
         does print.

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

def _assert_nothing_claimed(out, how):
    """
    A run of the trend readings that measured nothing must report that, and
    must not report a reading. Since stage 5 that is two fields: ADX is None
    rather than a number, and the failure is named.
    """
    assert out["adx"] is None, (
        f"{how}: adx is {out['adx']!r}; a run that measured nothing must not "
        f"report a number the confirmation gate would compare")
    assert out["momentum_divergence"] is False, (
        f"{how}: a divergence nobody measured was recorded as present")
    assert out["divergence_direction"] == "NONE", (
        f"{how}: divergence_direction is {out['divergence_direction']!r}")
    assert out["degraded_inputs"], f"{how}: the failure was not recorded"


def test_the_trend_readings_with_no_frame_claim_nothing():
    from indicators.trend_health import compute_trend_health

    _assert_nothing_claimed(compute_trend_health(None), "no frame")


def test_the_trend_readings_without_adx_claim_no_adx():
    """
    The reachable one: indicators.py drops a column it could not compute.
    Before stage 5 this fed a frame with no EMA SLOPE columns, which that
    module no longer reads -- see the record in this file's docstring.
    """
    from indicators.trend_health import compute_trend_health

    frame = _closes([100.0 + 0.1 * i for i in range(40)])
    out = compute_trend_health(frame)
    _assert_nothing_claimed(out, "no ADX column")
    assert any("ADX" in note for note in out["degraded_inputs"]), (
        out["degraded_inputs"])


# THE REDESIGN'S STAGE 4, 15 November 2026:
# test_unavailable_trend_direction_moves_no_entry_score stood here. It held
# that a trend direction of "UNAVAILABLE" scored a run exactly as "NEUTRAL"
# did -- that an unmeasured direction was not penalised through the entry
# score's trend multiplier -- with its own control that an AGREEING
# direction did move the multiplier, so the comparison could have failed.
# There is no trend multiplier: entry quality is D + H, with no multiplier
# at all (the draft's section 3.3, Viktor's ruling of 7 November 2026). The
# claim F9 made cannot be restated about the new score, because the input
# it was about does not reach it.

# F9(3) -- REMOVED at the redesign's stage 5, 15 November 2026. Two tests
# stood here, on volume_agreement: that a failed read ("UNKNOWN VOLUME") was
# not reported as a neutral one, and the negative control that a real neutral
# read kept its sentence. volume_agreement went with the validation block
# (core/engine_core.py), and no label the detector returns is scored or
# answered anywhere now, so neither claim has a subject. The detector's own
# labels are still swept in test_b4_labels_say_what_is_measured.py.


# ======================================================================
# F9(4) -- what a failed ADX actually costs
# ======================================================================

def test_the_adx_failure_note_states_what_is_lost():
    """
    Breaks ta.adx for real and reads the recorded consequence -- the way
    test_degraded_state.py simulates a failure.

    THE REDESIGN'S STAGE 5, 15 November 2026: the note named trend health's
    ADX component and this test measured that component's ceiling from the
    module itself, so the prose and the code could not drift apart. There is
    no component and no score: ADX reaches exactly one reader, the
    confirmation gate, which refuses both sides without a reading. So the
    assertion is that the note says THAT and names no point budget at all --
    the third correction of this one string, each time because the prose
    outlived the calculation it described.
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

    # The half that always mattered, and the only one left.
    assert "confirmation gate refuses both sides" in note, note
    assert "no trade" in note, note

    # No point budget, of any size: there is no score for ADX to be a part
    # of. "25 of its 100" was round 5's report, "40 of its 100" the fix.
    assert "of its 100" not in note, note
    assert "trend health" not in note.lower(), note
    assert "component" not in note.lower(), note

    # And ADX itself still reaches the gate as an absence rather than a
    # number, which is what makes "refuses both sides" true.
    base = _closes([100.0 + 0.1 * i for i in range(40)])
    assert compute_trend_health(base)["adx"] is None


# ======================================================================
# The panel's TREND line -- REMOVED at the redesign's stage 5,
# 15 November 2026
# ======================================================================
#
# One test stood here: it stripped trend_direction and momentum_mode from the
# golden decision and asserted the TREND line read "UNKNOWN / UNKNOWN" rather
# than F9's fabricated "NEUTRAL / HEALTHY". The line is gone, with the three
# readings it printed. That the panel prints no TREND line -- and no
# VALIDATION, CONFIDENCE or TRADE QUALITY line either -- is held in
# test_panel_prints_only_what_was_computed.py, beside the lines it does
# print, which is where a reader comparing the panel against the record will
# look.
