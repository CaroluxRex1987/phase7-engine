"""
Fix 2 -- no trend, no trade.

Round 8's triage, point 4 (docs/PHASE7_DECISIONS.md, "Ruling, 5 October 2026
-- round 8 triaged ..."; the review's B3), ruled by Viktor on the night of 4 to
5 October by agreeing to Claude's suggestion. It implements point 9 of the
ruling of 28 September, "trends only, for now".

WHAT CHANGED

The confirmation gate (models/entry_model.py, signal_blockers) blocked both
sides on the exhaustion flag, which in practice asked whether the last candle
was wider than the one before it in a low-ADX market. The flag leaves the
gate. In its place, ADX under MIN_TREND_ADX (20) blocks both sides and says
so; an ADX with no valid reading blocks both sides too, failing safe -- the
part the ruling left to the patch. The flag itself is still computed and
still read by trend health's reversal reading, the trend-regime label, Exit
Watch and the record; only the gate stops reading it.

WHAT THESE TESTS HOLD

1. The threshold is 20, and it is in the run-hash payload.
2. 20.0 confirms and anything under it blocks, on both sides.
3. The printed ADX is rounded down, so a value just under 20 never prints as
   "20.0, under the 20".
4. An ADX with no valid reading -- None, NaN, an infinity, a bool, a string,
   a value outside 0-100 -- blocks both sides with its own reason; numpy's
   number types are valid readings.
5. A call in the shape before fix 2 is refused rather than misbound, and adx
   has no default.
6. engine_core hands the gate trend health's ADX and not the flag (read from
   the parse tree, so this runs without pandas_ta).
7. Through DecisionModel.evaluate(): a low ADX refuses a trade the ladder
   chose, with the reason in the reasoning and the summary; a confirmed trade
   says ADX is 20 or more; on a degraded run an unreadable ADX makes the label
   NO-TRADE (SIGNAL UNCONFIRMED), where it was NO-TRADE (DEGRADED INPUT).
8. On the engine path (pandas_ta), with the pinned fixture: the control run
   confirms its long; the same run with trend health's ADX set to 15 refuses
   it and records the ADX reason on both sides; and with ADX's computation
   broken, both sides record the no-reading reason.

All fixture-free, so run_tests.py runs them too.
"""

import ast
import math
import os

import numpy as np
import pytest

from conftest import REPO_ROOT
from core.decision_log import FINGERPRINTED_MODULES, module_snapshot
from models.decision_model import DecisionModel
from models.entry_model import (MIN_TREND_ADX, generate_entry_signals,
                                signal_blockers)

PINNED_DIR = os.path.join(REPO_ROOT, "tests", "fixtures", "pinned")
UNREACHABLE = "http://127.0.0.1:9"

UNCONFIRMED = "NO-TRADE (SIGNAL UNCONFIRMED)"
LOW = ("under the 20 the engine requires to treat the market as trending")
NO_READING = ("ADX has no valid reading on this run, so the market cannot be "
              "shown to be trending")
SIDES = (("LONG", "BULLISH TREND"), ("SHORT", "BEARISH TREND"))


def _blockers(side, structure, adx):
    return signal_blockers(side, structure, False, "NONE", adx=adx)


def _signals(adx, structure="BULLISH TREND"):
    return generate_entry_signals(structure_regime=structure,
                                  momentum_divergence=False,
                                  divergence_direction="NONE", adx=adx)


def _evaluate(signals, degradation=None):
    """An AGGRESSIVE LONG on the ladder; the gate decides the rest."""
    entry = {"score": 80.0, "entry_status": "ACTIVE ENTRY ZONE", **signals}
    return DecisionModel().evaluate(
        bias={"raw": "BULLISH", "score": 78.0},
        trend={"trend_health": 90.0, "trend_direction_sign": 1,
               "momentum_divergence": False},
        entry=entry,
        risk={"risk_valid": True, "risk_reason": "OK",
              "risk_regime": "NORMAL RISK", "validation_state": "NEUTRAL",
              "targets": [1.1, 1.2, 1.3]},
        degradation=degradation,
    )


# ============================================================
# 1. The threshold
# ============================================================

def test_the_threshold_is_20_and_in_the_run_hash():
    assert MIN_TREND_ADX == 20.0
    assert "MIN_TREND_ADX" in FINGERPRINTED_MODULES["models.entry_model"], (
        "the gate's threshold decides which runs may trade and must be in "
        "the run-hash payload")
    assert module_snapshot()["models.entry_model"]["MIN_TREND_ADX"] == 20.0


# ============================================================
# 2. The boundary
# ============================================================

def test_20_confirms_and_anything_under_it_blocks_both_sides():
    for side, structure in SIDES:
        assert _blockers(side, structure, 20.0) == [], side
        assert _blockers(side, structure, 55.0) == [], side
        for low in (19.999, 15.0, 0.0):
            got = _blockers(side, structure, low)
            assert len(got) == 1 and got[0].startswith("ADX is ") and LOW in got[0], (
                side, low, got)


def test_low_adx_blocks_the_side_whose_structure_agrees_and_adds_to_the_other():
    """Both sides: the side against the structure gets both reasons."""
    out = _signals(15.0)
    assert out["long_signal"] is False and out["short_signal"] is False
    assert out["long_signal_blockers"] == [f"ADX is 15.0, {LOW}"]
    assert out["short_signal_blockers"] == [
        "structure is BULLISH TREND, not BEARISH TREND", f"ADX is 15.0, {LOW}"]


# ============================================================
# 3. The printed value
# ============================================================

def test_the_printed_adx_never_reads_as_the_threshold():
    """
    19.96 rounded to one decimal is 20.0, and "ADX is 20.0, under the 20" is
    a sentence that contradicts itself. The value is rounded down instead.
    """
    for value, shown in ((19.96, "19.9"), (19.95, "19.9"), (19.9999999, "19.9"),
                         (18.43, "18.4"), (18.4, "18.4"), (0.0, "0.0")):
        got = _blockers("LONG", "BULLISH TREND", value)
        assert got == [f"ADX is {shown}, {LOW}"], (value, got)


# ============================================================
# 4. No valid reading
# ============================================================

def test_an_adx_with_no_valid_reading_blocks_both_sides():
    for bad in (None, float("nan"), float("inf"), float("-inf"), True, False,
                "25", -0.5, 100.5):
        for side, structure in SIDES:
            assert _blockers(side, structure, bad) == [NO_READING], (side, bad)


def test_numpy_numbers_are_valid_readings():
    """The control for the test above: a refusal of every type is not a rule."""
    for good in (np.float64(30.0), np.float32(30.0), np.int64(30), 30, 100.0):
        for side, structure in SIDES:
            assert _blockers(side, structure, good) == [], (side, good)


# ============================================================
# 5. The old call shape
# ============================================================

def test_a_call_in_the_shape_before_fix_2_is_refused():
    # Before fix 2 the flag was the third positional argument of five.
    with pytest.raises(TypeError):
        signal_blockers("LONG", "BULLISH TREND", False, False, "NONE")
    with pytest.raises(TypeError):
        generate_entry_signals(structure_regime="BULLISH TREND",
                               trend_exhaustion=False,
                               momentum_divergence=False,
                               divergence_direction="NONE")
    # And adx has no default: forgetting it is an error, not a reading.
    with pytest.raises(TypeError):
        signal_blockers("LONG", "BULLISH TREND", False, "NONE")
    with pytest.raises(TypeError):
        generate_entry_signals(structure_regime="BULLISH TREND",
                               momentum_divergence=False,
                               divergence_direction="NONE")


# ============================================================
# 6. engine_core's call
# ============================================================

def test_engine_core_hands_the_gate_adx_and_not_the_flag():
    path = os.path.join(REPO_ROOT, "core", "engine_core.py")
    with open(path, "rb") as fh:
        tree = ast.parse(fh.read().decode("utf-8"))
    calls = [node for node in ast.walk(tree)
             if isinstance(node, ast.Call)
             and isinstance(node.func, ast.Name)
             and node.func.id == "generate_entry_signals"]
    assert len(calls) == 1, f"expected one call to generate_entry_signals, found {len(calls)}"
    call = calls[0]
    assert not call.args, "the call passes arguments by position"
    keywords = {kw.arg: kw.value for kw in call.keywords}
    assert "trend_exhaustion" not in keywords, sorted(keywords)
    adx = keywords.get("adx")
    assert (isinstance(adx, ast.Subscript)
            and isinstance(adx.value, ast.Name) and adx.value.id == "trend"
            and isinstance(adx.slice, ast.Constant) and adx.slice.value == "adx"), (
        "the gate's adx is not trend health's own reading, trend[\"adx\"]")
    strings = {n.value for n in ast.walk(call) if isinstance(n, ast.Constant)}
    assert "trend_exhaustion" not in strings, (
        "the exhaustion flag reaches the confirmation gate again; since fix 2 "
        "ADX does instead")


# ============================================================
# 7. Through the decision model
# ============================================================

def test_a_low_adx_refuses_a_trade_the_ladder_chose_and_says_why():
    out = _evaluate(_signals(15.0))
    assert out["final_action"] == UNCONFIRMED, out["explanation"]
    reason = ("This would have been AGGRESSIVE LONG, but the bullish bias lacked "
              f"structural confirmation (ADX is 15.0, {LOW}), so no trade is taken.")
    assert reason in out["explanation"]["reasons"]
    assert out["explanation"]["summary"] == f"{UNCONFIRMED} — {reason}"


def test_a_confirmed_trade_says_adx_is_20_or_more():
    out = _evaluate(_signals(30.0))
    assert out["final_action"] == "AGGRESSIVE LONG", out["explanation"]
    assert ("Structural confirmation holds for the long: structure agrees with "
            "the direction, ADX is 20 or more, and no momentum divergence "
            "points against it.") in out["explanation"]["reasons"]
    assert not any("exhausted" in r for r in out["explanation"]["reasons"])


def test_an_unreadable_adx_on_a_degraded_run_takes_the_signal_label():
    """
    Predicted in the commit: such a run is degraded, and the gate runs before
    the degradation override, so the label is the gate's, with the
    degradation notes appended. Before fix 2 the gate confirmed it and the
    label was NO-TRADE (DEGRADED INPUT).
    """
    out = _evaluate(_signals(None), degradation=["ADX (column absent)"])
    assert out["final_action"] == UNCONFIRMED, out["explanation"]
    reasons = out["explanation"]["reasons"]
    assert any(NO_READING in r for r in reasons), reasons
    assert any(r.startswith("This run is DEGRADED: ADX (column absent)")
               for r in reasons), reasons


# ============================================================
# 8. The engine path
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


def _run_pinned_with_trend_adx(value):
    """
    The pinned run, with the ADX in the pair's own trend-health result set to
    `value`. engine_core calls compute_trend_health for the pair first and for
    BTC second; only the first call is changed. Restored in a finally.
    """
    import core.engine_core as ec

    real = ec.compute_trend_health
    calls = {"n": 0}

    def first_call_patched(*a, **k):
        calls["n"] += 1
        out = real(*a, **k)
        if calls["n"] == 1:
            out = dict(out, adx=value)
        return out

    try:
        ec.compute_trend_health = first_call_patched
        return _run_pinned()
    finally:
        ec.compute_trend_health = real


def _run_pinned_with_adx_broken():
    import indicators.indicators as ind

    def explode(*a, **k):
        raise RuntimeError("simulated adx failure")

    original = ind.ta.adx
    try:
        ind.ta.adx = explode
        return _run_pinned()
    finally:
        ind.ta.adx = original


def test_on_the_engine_path_a_low_adx_refuses_the_pinned_long():
    pytest.importorskip("pandas_ta")

    control = _run_pinned()
    adx = float(control["lineage"]["indicators_at_decision_bar"]["ADX"])
    assert adx >= MIN_TREND_ADX, (
        f"the pinned fixture's ADX is {adx}; the control needs a trending one")
    assert control["entry"]["long_signal"] is True, control["entry"]
    assert control["exit"]["action"].endswith("LONG"), control["exit"]["action"]

    low = _run_pinned_with_trend_adx(15.0)
    for side in ("long", "short"):
        assert f"ADX is 15.0, {LOW}" in low["entry"][f"{side}_signal_blockers"], (
            side, low["entry"])
    assert low["exit"]["action"] == UNCONFIRMED, low["exit"]["action"]
    assert any(f"ADX is 15.0, {LOW}" in r
               for r in low["explanation"]["reasons"]), low["explanation"]


def test_on_the_engine_path_an_unreadable_adx_blocks_both_sides():
    pytest.importorskip("pandas_ta")

    decision = _run_pinned_with_adx_broken()
    assert decision["degradation"]["degraded"] is True, decision["degradation"]
    for side in ("long", "short"):
        assert NO_READING in decision["entry"][f"{side}_signal_blockers"], (
            side, decision["entry"])
    action = decision["exit"]["action"]
    assert not any(s in action for s in ("LONG", "SHORT")), action
