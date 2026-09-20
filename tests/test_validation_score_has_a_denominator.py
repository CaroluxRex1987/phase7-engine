"""
The validation score on the panel says what it is out of.

FOUND 20 SEPTEMBER 2026. The panel printed

    VALIDATION : WEAK (Score: 5.00)

and Viktor had to ask what 5.00 was out of. It is out of 100: engine_core.py
starts the score at 50 and moves it only on evidence trend health does not
already contain -- macro agreement (+10 / -20) and volume agreement
(+15 / -25) -- then clamps to 0..100. A 5.00 is the floor case: 50, macro
disagreeing, volume against.

Every other score on the panel carries its denominator. This one did not, so
a reader could not tell 5.00/100 (very weak) from 5.00/10 (middling) without
opening the source. Item 8, Epistemic Honesty: a number an operator is meant
to act on has to say what it means.

Fixture-free, per run_tests.py.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _engine_available():
    """
    core.engine_core imports pandas_ta at module level. The established
    pattern in this suite (tests/test_code_fingerprint.py) is to skip rather
    than to assert something weaker, so the check is never vacuous.
    """
    try:
        import pandas_ta  # noqa: F401
    except ImportError:
        return False
    return True


def _panel(validation_score, validation_state="WEAK"):
    from core.panel_render import render_panel

    return render_panel({
        "symbol": "TESTUSDT",
        "timeframe": "4h",
        "risk": {
            "validation_state": validation_state,
            "validation_score": validation_score,
            "validation_note": "Volume sentiment is neutral.",
        },
    })


def test_the_validation_score_carries_its_denominator():
    panel = _panel(5.0)

    assert "5.00/100" in panel, (
        "the VALIDATION line prints a bare number again; a reader cannot tell "
        "5.00/100 from 5.00/10"
    )


def test_the_floor_and_the_ceiling_both_print_it():
    assert "0.00/100" in _panel(0.0)
    assert "100.00/100" in _panel(100.0, validation_state="STRONG")


def test_the_state_is_still_printed_beside_the_score():
    """
    Negative control: the denominator must not have replaced the label.
    """
    panel = _panel(75.0, validation_state="STRONG")
    assert "STRONG" in panel and "75.00/100" in panel, panel


def test_the_score_bounds_the_engine_can_produce_are_the_ones_claimed():
    """
    The docstring above says 0..100 with a 50 baseline. Held against
    engine_core rather than asserted in prose: the two agreement functions are
    the only movers, so the reachable range is 50-45 .. 50+25 before clamping.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    from core.engine_core import macro_agreement, volume_agreement

    macro_deltas = [
        macro_agreement("BULLISH", "BULLISH")[0],
        macro_agreement("BEARISH", "BULLISH")[0],
        macro_agreement("NEUTRAL", "BULLISH")[0],
    ]
    volume_deltas = [
        volume_agreement("BULLISH VOLUME SUPPORT", "BULLISH")[0],
        volume_agreement("BEARISH VOLUME PRESSURE", "BULLISH")[0],
        volume_agreement("NEUTRAL VOLUME", "BULLISH")[0],
    ]

    assert max(macro_deltas) == 10.0 and min(macro_deltas) == -20.0, macro_deltas
    assert max(volume_deltas) == 15.0 and min(volume_deltas) == -25.0, volume_deltas
    assert 50.0 + min(macro_deltas) + min(volume_deltas) == 5.0, (
        "the 5.00 the panel showed is no longer the floor case this test "
        "documents"
    )
