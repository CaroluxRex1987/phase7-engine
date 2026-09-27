"""
Finding 4 -- the plan is measured from the decision close.

Review of 21 September 2026, finding 4: the panel printed an ENTRY ZONE (the
band between EMA_20 and EMA_50) while the stop, T1-T3 and all three R:R values
were measured from the last close, and no rule requires price to be inside the
band to trade. The panel had no single entry price, and a backtest must fill
somewhere.

Viktor's ruling, 27 September 2026 (DECISIONS, "Ruling, 27 September 2026 --
the plan is measured from the decision close (finding 4)"), option A of three:
the close of the decision candle -- the latest closed candle, since finding 16
-- is the plan's single entry price. The panel says so on the DECISION CLOSE
line, and the band is labelled for what it is. Entering at the band (a limit
order) is on the list for after the audit; the live price was rejected.

WHAT THESE TESTS HOLD
1. On the engine path, exit.current_price (the plan's entry in the log) is
   the close of the decision candle, and the stop and all three targets are
   measured from it.
2. The DECISION CLOSE line names itself the plan's entry, and the R:R on T1
   is computed from it.
3. No panel line is labelled ENTRY ZONE or ZONE DISTANCE any more, and the
   band line says it is not the entry.
4. The band label names the EMA lengths config holds, not a written-in pair.

All fixture-free, so run_tests.py runs them too.
"""

import math
import os

import pandas as pd
import pytest

from conftest import REPO_ROOT
from core import config
from core.panel_render import render_panel

PINNED_DIR = os.path.join(REPO_ROOT, "tests", "fixtures", "pinned")
UNREACHABLE = "http://127.0.0.1:9"


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


def _decision(exit_data=None, risk=None, entry=None):
    return {
        "symbol": "TESTUSDT", "timeframe": "4h",
        "entry": entry if entry is not None else {
            "score": 45.0, "entry_status": "AWAY FROM ZONE",
            "zone_lower": 0.4918, "zone_upper": 0.4981,
            "distance_from_zone": 5.44,
        },
        "risk": risk if risk is not None else {
            "atr_stop": 0.72, "targets": (0.85, 0.90, 0.95)},
        "exit": exit_data if exit_data is not None else {"current_price": 0.80},
    }


def _lines(panel, prefix):
    return [ln for ln in panel.splitlines() if ln.lstrip().startswith(prefix)]


# ============================================================
# 1. The engine path
# ============================================================

def test_the_plan_is_measured_from_the_decision_candles_close():
    pytest.importorskip("pandas_ta")

    decision = _run_pinned()

    struct = decision["provenance"]["decision_candles"]["struct"]
    frame = pd.read_csv(os.path.join(PINNED_DIR, "AEROUSDT_4h.csv"))
    opened = pd.to_datetime(frame["timestamp"], unit="ms").dt.strftime(
        "%Y-%m-%d %H:%M:%S")
    rows = frame[opened == struct["open_time"]]
    assert len(rows) == 1, f"decision candle {struct['open_time']!r} not in the fixture"
    decision_close = float(rows["close"].iloc[0])

    entry = float(decision["exit"]["current_price"])
    assert entry == decision_close, (
        f"the plan's entry {entry} is not the decision candle's close "
        f"{decision_close}"
    )

    stop = float(decision["risk"]["atr_stop"])
    targets = [float(t) for t in decision["risk"]["targets"]]
    assert math.isfinite(stop) and all(math.isfinite(t) for t in targets), (
        stop, targets)
    distance = abs(entry - stop)
    assert distance > 0, (entry, stop)
    side = 1.0 if stop < entry else -1.0
    from models.risk_model import TARGET1_MULT, TARGET2_MULT, TARGET3_MULT
    for target, mult in zip(targets, (TARGET1_MULT, TARGET2_MULT, TARGET3_MULT)):
        assert math.isclose(target, entry + side * distance * mult,
                            rel_tol=0, abs_tol=1e-12), (
            f"target {target} is not {mult}x the stop distance from the "
            f"decision close {entry}"
        )


# ============================================================
# 2. The DECISION CLOSE line
# ============================================================

def test_the_decision_close_line_names_itself_the_plans_entry():
    panel = render_panel(_decision())
    assert panel is not None

    lines = _lines(panel, "DECISION CLOSE")
    assert len(lines) == 1, lines
    assert "$0.8000" in lines[0], lines[0]
    assert "the plan's entry" in lines[0], lines[0]
    assert "measured from it" in lines[0], lines[0]

    # The claim on that line, checked against the number beside it:
    # stop distance |0.80 - 0.72| = 0.08, T1 R:R |0.85 - 0.80| / 0.08 = 0.625.
    t1 = _lines(panel, "TARGET 1")
    assert len(t1) == 1, t1
    assert ("R:R 1 : 0.62" in t1[0]) or ("R:R 1 : 0.63" in t1[0]), t1[0]


def test_a_missing_decision_close_claims_no_entry():
    panel = render_panel(_decision(exit_data={}))
    assert panel is not None
    lines = _lines(panel, "DECISION CLOSE")
    assert len(lines) == 1, lines
    assert "not available" in lines[0], lines[0]
    assert "the plan's entry" not in lines[0], lines[0]


# ============================================================
# 3. The band is not labelled an entry
# ============================================================

def test_no_line_calls_the_band_an_entry_zone():
    panel = render_panel(_decision())
    assert panel is not None

    assert _lines(panel, "ENTRY ZONE") == []
    assert _lines(panel, "ZONE DISTANCE") == []

    band = _lines(panel, "EMA BAND")
    assert len(band) == 1, band
    assert "$0.4918 - $0.4981" in band[0], band[0]
    assert "not the entry" in band[0], band[0]
    distance = _lines(panel, "BAND DISTANCE")
    assert len(distance) == 1, distance
    assert "5.44% away from the band" in distance[0], distance[0]


# ============================================================
# 4. The label reads the lengths from config
# ============================================================

def test_the_band_label_names_the_configured_lengths():
    fast, slow = config.EMA_FAST, config.EMA_SLOW
    try:
        config.EMA_FAST, config.EMA_SLOW = 13, 34
        located = render_panel(_decision())
        missing = render_panel(_decision(entry={
            "score": 45.0, "entry_status": "ZONE NOT AVAILABLE",
            "zone_lower": float("nan"), "zone_upper": float("nan"),
            "distance_from_zone": float("nan")}))
    finally:
        config.EMA_FAST, config.EMA_SLOW = fast, slow

    for panel in (located, missing):
        assert panel is not None
        band = _lines(panel, "EMA BAND")
        assert len(band) == 1, band
        assert "(EMA 13 and EMA 34)" in band[0], band[0]
        assert "20" not in band[0] and "50" not in band[0], band[0]
    assert "not located" in _lines(missing, "EMA BAND")[0]
