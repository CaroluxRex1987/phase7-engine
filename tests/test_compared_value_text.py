"""
No printed value crosses the line it is set against.

ENTRY 58, found 1 November 2026 (docs/PHASE7_NEXT.md, "Found after
22 September"): "trend strength is 75/100, below the 75 the SHORT tier needs"
on a trend health of 74.52. The rule and this test's values are the redesign
draft's section 6. core/threshold_text.py's compared_value_text is the one
helper every sentence that quotes a line will print through; stage 1 of the
redesign adds it and nothing calls it yet, which the last test here holds so
that the stage that first uses it moves that test on purpose.

For every line the engine or the redesign compares against, the values
t - 1e-9, t - 0.005, t - 0.5, t, t + 0.005 and t + 0.5 are printed, and each
printed value is on the same side of t as its true value.

Fixture-free, per run_tests.py. Standard library only.
"""

import os
import sys
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.threshold_text import compared_value_text

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Lines compared today or in the approved draft: ADX 20, bias strength 30,
# trend health 40 and 75, the tier lines 50 and 70, entry quality's 80, the
# liquidity floor 10,000, and zero for a signed reading.
LINES = [0.0, 20.0, 30.0, 40.0, 50.0, 70.0, 75.0, 80.0, 10_000.0]
OFFSETS = [-1e-9, -0.005, -0.5, 0.0, 0.005, 0.5]


def _side(value, line):
    return (value > line) - (value < line)


def test_every_printed_value_is_on_its_own_side_of_the_line():
    wrong = []
    for line in LINES:
        for offset in OFFSETS:
            value = line + offset
            text = compared_value_text(value, line)
            printed = Decimal(text)
            if _side(printed, Decimal(repr(line))) != _side(value, line):
                wrong.append((value, line, text))
    assert not wrong, wrong


def test_the_value_entry_58_found_prints_under_its_line():
    assert compared_value_text(74.52, 75.0) == "74.5"
    assert compared_value_text(74.52, 75) == "74.5"


def test_a_value_clear_of_the_line_prints_as_a_whole_number():
    assert compared_value_text(92.0, 70.0) == "92"
    assert compared_value_text(45.18175716, 70.0) == "45"
    assert compared_value_text(0.0, 50.0) == "0"


def test_a_value_on_the_line_prints_as_the_line():
    for line in LINES:
        assert Decimal(compared_value_text(line, line)) == Decimal(repr(line))
    assert compared_value_text(70.0, 70.0) == "70"


def test_decimals_are_added_only_until_the_side_is_right():
    assert compared_value_text(69.5, 70.0) == "69.5"
    assert compared_value_text(69.96, 70.0) == "69.96"
    assert compared_value_text(70.4, 70.0) == "70.4"


def test_past_two_decimals_a_value_is_rounded_away_from_the_line():
    assert compared_value_text(69.999, 70.0) == "69.99"
    assert compared_value_text(70.0 - 1e-9, 70.0) == "69.99"
    assert compared_value_text(70.004, 70.0) == "70.01"
    assert compared_value_text(70.0 + 1e-9, 70.0) == "70.01"


def test_it_agrees_with_the_adx_blockers_own_rounding_where_both_apply():
    """_adx_text floors 19.96 to 19.9; this prints 19.96. Both are under 20."""
    for adx in (19.96, 19.999, 19.5, 0.0, 12.34):
        assert Decimal(compared_value_text(adx, 20.0)) < 20


def test_a_reading_that_does_not_exist_has_no_text():
    for bad in (None, float("nan"), float("inf"), float("-inf"), True, "70"):
        for args in ((bad, 70.0), (70.0, bad)):
            try:
                text = compared_value_text(*args)
            except ValueError:
                continue
            raise AssertionError(f"{args!r} printed as {text!r}")


def test_no_engine_module_calls_the_helper_yet():
    """
    Stage 1 adds the helper unused, so no sentence and no action changes. The
    stage that rewrites the first sentence through it removes this test.
    """
    users = []
    for folder in ("core", "data", "indicators", "models", "structure", "utils"):
        for name in sorted(os.listdir(os.path.join(REPO_ROOT, folder))):
            if not name.endswith(".py") or (folder, name) == ("core", "threshold_text.py"):
                continue
            with open(os.path.join(REPO_ROOT, folder, name), encoding="utf-8") as f:
                if "threshold_text" in f.read():
                    users.append(f"{folder}/{name}")
    for name in ("main.py", "live_trading.py"):
        with open(os.path.join(REPO_ROOT, name), encoding="utf-8") as f:
            if "threshold_text" in f.read():
                users.append(name)
    assert users == [], users
