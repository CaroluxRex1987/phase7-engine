"""
Round 8, F5 -- BAND DISTANCE names the quantity it prints.

Round 8 (MiMo-V2.6-Pro, 4 October 2026), F5: the panel printed
"BAND DISTANCE : x% away from the band", while entry_model's
distance_from_zone is the distance from the band's MIDPOINT as a percentage
of the close. With the close inside the band the line printed a positive
distance "away from the band" under STATUS : ACTIVE ENTRY ZONE. Claude's
review of 5 October reproduced it on a real run: decision candle
30 September 08:00 UTC, close $0.8082, band $0.7795 - $0.8142, printed
"1.40% away from the band" with the close inside the band.

Viktor's ruling (DECISIONS, "Ruling, 5 October 2026 -- round 8 triaged ...",
point 8): the label and record fixes are made now. The repair is Claude's:
the label names the midpoint; the number, the record key and the entry score
are unchanged.

WHAT THESE TESTS HOLD
1. On the real run's numbers the line names the midpoint and prints the
   number it always printed, beside STATUS : ACTIVE ENTRY ZONE.
2. On round 8's own example (close above the band) the line prints the
   midpoint distance, 4.22%, under its own name -- not the edge distance,
   3.26%.
3. The record's number is the midpoint distance, as before (control: passes
   on the pre-fix code too).

No panel line says "away from the band" in any of them. All fixture-free,
so run_tests.py runs them too.
"""

import pandas as pd
import pytest

from core.panel_render import render_panel
from models.entry_model import calculate_entry_quality


def _frame(close, rows=60):
    return pd.DataFrame({"close": [close] * rows, "ATR": [0.01] * rows})


def _entry(close, lower, upper):
    out = calculate_entry_quality(_frame(close), lower, upper)
    return {
        "score": out["score"], "entry_status": out["entry_status"],
        "zone_lower": lower, "zone_upper": upper,
        "distance_from_zone": out["distance_from_zone"],
    }


def _panel(entry):
    panel = render_panel({"symbol": "TESTUSDT", "timeframe": "4h",
                          "entry": entry})
    assert panel is not None
    return panel


def _line(panel, prefix):
    lines = [ln for ln in panel.splitlines() if ln.lstrip().startswith(prefix)]
    assert len(lines) == 1, lines
    return lines[0]


def test_inside_the_band_the_line_names_the_midpoint():
    entry = _entry(0.8082, 0.7795, 0.8142)
    assert entry["entry_status"] == "ACTIVE ENTRY ZONE", entry

    panel = _panel(entry)

    distance = _line(panel, "BAND DISTANCE")
    assert "1.40% from the band's midpoint" in distance, distance
    assert "away from the band" not in panel, distance
    assert "ACTIVE ENTRY ZONE" in _line(panel, "STATUS"), panel


def test_outside_the_band_the_number_is_the_midpoint_distance():
    entry = _entry(0.8017, 0.7602, 0.7756)

    distance = _line(_panel(entry), "BAND DISTANCE")

    assert "4.22% from the band's midpoint" in distance, distance
    assert "3.26%" not in distance, distance
    assert "away from the band" not in distance, distance


def test_the_recorded_number_is_unchanged():
    """Control: the record keeps the midpoint distance the score uses."""
    close, lower, upper = 0.8017, 0.7602, 0.7756
    entry = _entry(close, lower, upper)

    midpoint = (lower + upper) / 2.0
    assert entry["distance_from_zone"] == pytest.approx(
        abs(close - midpoint) / close * 100.0)
