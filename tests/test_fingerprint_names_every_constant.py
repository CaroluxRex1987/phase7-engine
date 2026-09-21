"""
Every named numeric constant in a fingerprinted module is in the readable
fingerprint.

FOUND 21 SEPTEMBER 2026, in the deferred read of core/decision_log.py
(docs/PHASE7_NEXT.md, "Review findings", 22). FINGERPRINTED_MODULES listed
DecisionModel.BTC_ADJUSTMENT_CAP and not its sibling
DecisionModel.BTC_STRESS_PENALTY -- the two together bound the BTC-adjusted
confidence -- nor DecisionModel.AVG_REWARD_R and
DecisionModel.EV_BREAKEVEN_BAND_R, which set the illustrative EV sentence.
All three were inside code_hash, so a change to them was detected; the record
could not say which value a run used.

This list has fallen behind the code before, and each time the fix added the
missing names (sequence item 14's seven dead config constants, Kimi Finding 3,
round 6 F1). Adding names does not stop the next one being missed. So the test
below does not name the three: it reads every module the dict covers, finds
every module-level and class-level constant that is UPPER_CASE, numeric and
finite, and fails on any the dict does not list. A constant added tomorrow
fails it the day it is written.

What it deliberately does not count, each for a stated reason:

  - bool, str and other non-numeric constants (SIGNAL_UNCONFIRMED is a label,
    not a knob);
  - non-finite numbers (btc_context.NOT_MEASURED is NaN, a sentinel meaning
    "no value", not a setting);
  - constants of classes imported into a module rather than defined in it.

Without pandas_ta the scan is skipped, not narrowed -- see the test.

Fixture-free, per run_tests.py.
"""

import importlib
import inspect
import math
import numbers
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_UPPER = re.compile(r"^[A-Z][A-Z0-9_]*$")


def _is_knob(value):
    return (isinstance(value, numbers.Real) and not isinstance(value, bool)
            and math.isfinite(float(value)))


def _named_constants(module):
    found = set()
    for name, value in vars(module).items():
        if _UPPER.match(name) and _is_knob(value):
            found.add(name)
        if inspect.isclass(value) and value.__module__ == module.__name__:
            for attr, inner in vars(value).items():
                if _UPPER.match(attr) and _is_knob(inner):
                    found.add(f"{name}.{attr}")
    return found


def test_every_numeric_constant_in_a_fingerprinted_module_is_listed():
    # indicators.indicators imports pandas_ta at module scope, so without it
    # one of the modules cannot be read at all. Skipped whole rather than
    # checking the modules that do import: a pass that silently left one out
    # would look like full coverage.
    import pytest
    pytest.importorskip("pandas_ta")
    from core import decision_log

    missing = {}
    for module_name, listed in decision_log.FINGERPRINTED_MODULES.items():
        module = importlib.import_module(module_name)
        gap = sorted(_named_constants(module) - set(listed))
        if gap:
            missing[module_name] = gap
    assert not missing, (
        "named constants that decide numbers but are not in "
        "FINGERPRINTED_MODULES, so the record cannot say which value a run "
        f"used: {missing}"
    )


def test_the_three_found_on_21_september_are_recorded_with_their_values():
    from core import decision_log

    snap = decision_log.module_snapshot()["models.decision_model"]
    assert snap["DecisionModel.BTC_STRESS_PENALTY"] == 15.0
    assert snap["DecisionModel.AVG_REWARD_R"] == 2.0
    assert snap["DecisionModel.EV_BREAKEVEN_BAND_R"] == 0.3


def test_the_scan_sees_class_constants_and_skips_sentinels():
    """
    Negative control for the scanner itself: a scan that found nothing would
    pass the first test on any list.
    """
    from models import btc_context, decision_model

    found = _named_constants(decision_model)
    assert "MIN_ACTION_BIAS" in found
    assert "DecisionModel.BTC_ADJUSTMENT_CAP" in found
    assert "DecisionModel.SIGNAL_UNCONFIRMED" not in found   # a label
    assert "NOT_MEASURED" not in _named_constants(btc_context)  # NaN sentinel
    assert "CORRELATION_WINDOW" in _named_constants(btc_context)
