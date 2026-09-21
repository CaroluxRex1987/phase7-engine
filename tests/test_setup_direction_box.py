"""
The SETUP DIRECTION box states the side bias leans, and never takes a side
when bias and the plan disagree.

WHY THIS FILE EXISTS

The box was added at 66f1479 (14 September 2026) at Viktor's request -- a
SHORT setup had no word "SHORT" anywhere on the panel -- and its NEUTRAL
branch was changed at 39e0e79 the same day, by his ruling, to print nothing.
Neither commit added a test. docs/audit_change_list.md, written 21 September
2026, found them the only engine changes since the last independent audit with
no test at all.

The case that matters most is not the plain LONG or SHORT. It is the
CONTRADICTORY line: when decision_model refuses a trade as
"NO-TRADE (PLAN CONTRADICTS ACTION)", bias and the risk plan pointed opposite
ways, and a box that printed the bias side there would be the 2 September
defect ("a long label on a short plan", tests/test_direction_source.py)
coming back through a new line. Nothing guarded that until now.

What each test pins, all read from core/panel_render.py's direction box:

  - BULLISH prints "THIS ANALYSIS IS FOR A LONG", and only that.
  - BEARISH prints "THIS ANALYSIS IS FOR A SHORT", and only that.
  - NEUTRAL prints no box and no SETUP DIRECTION line (Viktor's ruling of
    14 September: an absent box already says "no lean").
  - PLAN CONTRADICTS ACTION prints CONTRADICTORY and neither side, whatever
    bias says -- checked for both biases, so a guard that only covered one of
    them fails.
  - The box follows bias, not the action: a WAIT or NO-TRADE run still says
    which side the analysis leaned. That was the purpose of adding it.
  - The box sits directly under the DECISION line.

Fixture-free, per run_tests.py.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

LONG = "THIS ANALYSIS IS FOR A LONG"
SHORT = "THIS ANALYSIS IS FOR A SHORT"
CONTRADICTORY = "SETUP DIRECTION: CONTRADICTORY"


def _render(raw_bias, action="WAIT"):
    from core.panel_render import render_panel

    panel = render_panel({
        "symbol": "TESTUSDT",
        "timeframe": "4h",
        "bias": {"raw": raw_bias},
        "exit": {"action": action},
    })
    assert isinstance(panel, str), "render_panel returned no panel"
    return panel


def test_a_bullish_bias_prints_the_long_box_and_nothing_else():
    panel = _render("BULLISH")
    assert LONG in panel
    assert SHORT not in panel
    assert CONTRADICTORY not in panel


def test_a_bearish_bias_prints_the_short_box_and_nothing_else():
    panel = _render("BEARISH")
    assert SHORT in panel
    assert LONG not in panel
    assert CONTRADICTORY not in panel


def test_a_neutral_bias_prints_no_direction_at_all():
    panel = _render("NEUTRAL")
    assert LONG not in panel
    assert SHORT not in panel
    assert "SETUP DIRECTION" not in panel
    assert "THIS ANALYSIS IS FOR" not in panel


def test_a_contradicted_plan_takes_neither_side_whatever_bias_says():
    for raw in ("BULLISH", "BEARISH"):
        panel = _render(raw, action="NO-TRADE (PLAN CONTRADICTS ACTION)")
        assert CONTRADICTORY in panel, raw
        assert LONG not in panel, raw
        assert SHORT not in panel, raw


def test_the_box_follows_bias_on_a_run_that_takes_no_trade():
    """
    The reason the box exists: on 14 September a WAIT / NO-TRADE run on a
    bearish market printed no side in words. A box shown only when a trade is
    authorized would pass the tests above and miss the point.
    """
    assert LONG in _render("BULLISH", action="NO-TRADE (RISK TOO HIGH)")
    assert SHORT in _render("BEARISH", action="WAIT")


def test_the_box_sits_directly_under_the_decision_line():
    lines = _render("BEARISH").splitlines()
    decision = next(i for i, l in enumerate(lines) if l.startswith("DECISION"))
    box = next(i for i, l in enumerate(lines) if SHORT in l)
    between = [l for l in lines[decision + 1:box] if l.strip()]
    # Only the box's own top border may stand between the two.
    assert all(set(l.strip()) <= set("=") or "\x1b[" in l for l in between), between
    assert box - decision <= 3, (decision, box)
