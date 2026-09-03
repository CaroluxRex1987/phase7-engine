"""
A structure sub-routine that fails must say so, and must not invent a level.

WHAT WAS WRONG

StructureEngine.analyze() wrapped each of its five sub-routines in its own
try/except and substituted a value on failure. None of the five recorded
anything, and analyze() had no channel to record through. A crashed detector
therefore produced a complete, ordinary-looking structure reading, the run
was not marked degraded, and a trade could be authorised on it.

Viktor's ruling of 29 August is degrade, not halt: a failed input is
RECORDED, confidence is capped, and no trade is authorised. The first of
those three was missing, and the other two depend on it.

The volume-node handler was the sharpest case:

    except Exception:
        hvn, lvn = float(current_price), float(current_price)

models/entry_model.py scores structure proximity as abs(close - hvn) / close.
With hvn equal to close that is exactly zero, which lands in the < 0.015 band
and awards the FULL 12 of 12 structure points for a high-volume node that was
never located.

That is the defect Finding 3 fixed on 1 September. Its comment is still in
entry_model.py, describing this exact arithmetic. The fix changed the
CONSUMER's fallback from `close` to NaN and left this producer handing down a
finite number equal to the price -- so the guarded path was safe and the
unguarded one still paid full marks. Closed the door, left the window.

Found on 2 September by an audit run that never produced a report, and
verified against source before any of it was believed.

WHAT THESE TESTS HOLD

That each of the five failures is recorded; that no failure produces a price
level a consumer will accept as a measurement; that the 12-of-12 payout is
gone at the producer as well as the consumer; and that the panel says a level
was not located rather than drawing one.
"""

import math
import os
import sys

import pandas as pd
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from structure.structure import StructureEngine, calculate_structure


def _frame(rows=60, price=100.0):
    return pd.DataFrame({
        "open": [price] * rows,
        "high": [price * 1.01] * rows,
        "low": [price * 0.99] * rows,
        "close": [price] * rows,
        "volume": [1000.0] * rows,
    })


def _boom(*args, **kwargs):
    raise RuntimeError("detector exploded")


# ======================================================================
# Each handler records, and none of them invents
# ======================================================================

@pytest.mark.parametrize("method,key", [
    ("_detect_regime", "structure regime"),
    ("_detect_sequence", "structure sequence"),
    ("_detect_hvn_lvn", "volume node"),
    ("_detect_swing_structure", "swing structure"),
    ("_volume_sentiment_simple", "volume sentiment"),
])
def test_every_failed_sub_routine_is_recorded(monkeypatch, method, key):
    engine = StructureEngine()
    monkeypatch.setattr(engine, method, _boom)

    out = engine.analyze(_frame(), current_price=100.0)

    recorded = out.get("degraded_inputs", [])
    assert any(key in entry for entry in recorded), (
        f"{method} raised and nothing was recorded. degraded_inputs={recorded!r}. "
        f"An unrecorded failure leaves the run undegraded, and an undegraded "
        f"run authorises a trade."
    )


def test_a_failed_volume_node_is_not_the_current_price():
    """
    The 12-of-12 payout, at the producer.

    hvn == close makes abs(close - hvn) / close exactly zero, which
    entry_model scores as full structure points. NaN does not.
    """
    engine = StructureEngine()
    engine._detect_hvn_lvn = _boom

    out = engine.analyze(_frame(price=100.0), current_price=100.0)

    for level in ("hvn", "lvn"):
        value = out[level]
        assert not math.isfinite(value), (
            f"{level} came back as {value!r} after the detector failed. Any "
            f"finite value here is a located level to every consumer."
        )
        assert value != 100.0, f"{level} is the current price wearing a level's name"


def test_a_failed_swing_detector_is_not_the_current_price():
    engine = StructureEngine()
    engine._detect_swing_structure = _boom

    out = engine.analyze(_frame(price=100.0), current_price=100.0)

    assert not math.isfinite(out["swing_struct"]), (
        "swing_struct came back finite after the detector failed"
    )


def test_failed_labels_say_unknown_rather_than_neutral():
    """
    NEUTRAL is a reading of the market. UNKNOWN is the absence of one. The
    macro NEUTRAL fabrication was removed at sequence item 9 for this reason;
    these two were the same shape and survived it.
    """
    engine = StructureEngine()
    engine._detect_regime = _boom
    engine._volume_sentiment_simple = _boom

    out = engine.analyze(_frame(), current_price=100.0)

    assert "UNKNOWN" in out["regime"], out["regime"]
    assert "UNKNOWN" in out["volume_sentiment"], out["volume_sentiment"]
    assert out["regime"] != "NEUTRAL STRUCTURE"
    assert out["volume_sentiment"] != "NEUTRAL VOLUME"


def test_a_clean_run_records_no_degradation():
    """
    The other direction. A degradation channel that reports something on a
    healthy run is worse than none: it trains the reader to ignore it.
    """
    out = StructureEngine().analyze(_frame(), current_price=100.0)
    assert out.get("degraded_inputs") == [], out.get("degraded_inputs")


def test_an_empty_frame_reports_levels_as_absent_not_as_zero():
    """
    calculate_structure's early return used 0.0 for all three levels. Zero is
    finite, so risk_model would accept it as a structural level and place a
    long's stop at $0.0000.
    """
    out = calculate_structure(pd.DataFrame())

    for level in ("hvn", "lvn", "swing_struct"):
        assert not math.isfinite(out[level]), (
            f"{level} is {out[level]!r} for an empty frame -- a finite number "
            f"a consumer will treat as a measurement"
        )
    assert out.get("degraded_inputs"), "an empty frame was not recorded as degraded"


# ======================================================================
# The consumer end: a NaN node must not pay full marks
# ======================================================================

def test_a_missing_volume_node_scores_no_structure_points():
    from models.entry_model import calculate_entry_quality

    df = _frame(price=100.0)
    df["ATR"] = 2.0
    df["VWMA"] = 100.0
    df["RSI"] = 50.0
    df["EMA_20"] = 99.0
    df["EMA_50"] = 98.0

    df["HVN"] = 100.0                     # a node sitting exactly at price
    located = calculate_entry_quality(df, zone_lower=99.0, zone_upper=98.0)

    df["HVN"] = float("nan")              # the same node, not located
    absent = calculate_entry_quality(df, zone_lower=99.0, zone_upper=98.0)

    assert located["struct_pts"] == 12.0, (
        "a node at the price no longer scores 12/12 -- this test's premise "
        "has moved and the assertion below no longer means what it says"
    )
    assert absent["struct_pts"] != 12.0, (
        "a volume node that was never located still scores the full 12 of 12. "
        "This is Finding 3's arithmetic, reached through the producer instead "
        "of the consumer."
    )


# ======================================================================
# The panel
# ======================================================================

def test_the_panel_does_not_draw_a_level_it_does_not_have():
    import json
    from core.panel_render import render_panel

    fixture = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "fixtures", "golden_decision.json")
    if not os.path.exists(fixture):
        pytest.skip("golden fixture not present")

    with open(fixture, encoding="utf-8") as fh:
        decision = json.load(fh)

    decision["structure"]["swing_struct"] = float("nan")
    panel = render_panel(decision)

    assert "SWING STRUCT  : not located this run" in panel, (
        "the panel printed a swing level for a run that did not find one"
    )
    assert "SWING STRUCT  : $0.0000" not in panel, (
        "safe_float's 0.0 default turned an absent level into a price again"
    )


def test_the_swing_line_occupies_a_line_of_its_own():
    """
    Shape, not substring.

    The first version of the fix above replaced a template line that ended in
    a newline with a computed one that did not, and every substring assertion
    in this file still passed: "SWING STRUCT  : $0.4700 (Lookback 8)" is
    present whether or not the line ends. The panel printed

        SWING STRUCT  : $0.4700 (Lookback 8)STOP LOSS     : $0.4636

    on a live run, and a person reading the output caught it. Nothing in this
    suite renders the panel and looks at its structure, so nothing could.

    Checked with the level present AND absent, because the two branches build
    the line separately and only one of them was ever exercised by a test.
    """
    import json
    from core.panel_render import render_panel

    fixture = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "fixtures", "golden_decision.json")
    if not os.path.exists(fixture):
        pytest.skip("golden fixture not present")

    with open(fixture, encoding="utf-8") as fh:
        base = json.load(fh)

    for label, value in (("located", 0.47), ("absent", float("nan"))):
        decision = json.loads(json.dumps(base))
        decision["structure"]["swing_struct"] = value
        panel = render_panel(decision)

        lines = panel.split("\n")
        swing = [ln for ln in lines if "SWING STRUCT" in ln]
        assert len(swing) == 1, (
            f"[{label}] expected one SWING STRUCT line, found {len(swing)}"
        )
        assert "STOP LOSS" not in swing[0], (
            f"[{label}] the swing line does not terminate -- STOP LOSS is "
            f"printed on the end of it: {swing[0]!r}"
        )
        assert any(ln.lstrip().startswith("STOP LOSS") for ln in lines), (
            f"[{label}] STOP LOSS no longer starts a line of its own"
        )
