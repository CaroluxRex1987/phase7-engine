"""
The panel must not contradict itself about the higher timeframe.

WHAT WAS WRONG

A live run on 3 September printed, four lines apart:

    MACRO TREND: BULLISH
    ...
    Validation Notes:
     - The higher timeframe is neutral.

Two claims about the same thing in one panel, and the second one false.

The block that produced it had three branches: agrees, disagrees, and an
`else` that said "The higher timeframe is neutral." That else covered two
different situations and described both with a sentence that is only true of
one of them:

    macro neutral, bias directional   the macro really is neutral -- true
    macro directional, bias neutral   the sentence describes the BIAS and
                                      attributes it to the MACRO -- false

Whenever the engine's six factors cancel -- a common state, and the state
that run was in, with bias_score at 1.33 -- the panel contradicted its own
MACRO TREND line.

Same shape as the contradiction that exposed the direction Critical the day
before: the decision claimed "the broader macro trend agrees" while
Validation Notes said it disagreed. Item 8, in the section whose whole job is
telling the operator what was checked.

FOUND BY RUNNING IT

Not by the suite, and not by reading. Viktor ran `python main.py` and read
the panel. The inline version could only be reached with market data that
produced a neutral bias under a directional macro, so no unit test could
address it and no fixture happened to hold it. Extracting the logic to
macro_agreement() is what makes the four cases reachable from a test at all;
these are those four cases.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 5 SEPTEMBER 2026, found while running the suite in a pandas_ta-free
# virtualenv — the second half of this project's own verification step, which
# exists because a test that ERRORS at collection looks nothing like a test
# that skips.
#
# This file errored. `macro_agreement` is a pure module-level function that
# needs no market data library at all, but importing it pulls in
# core.engine_core, which imports indicators.indicators, which imports
# pandas_ta at module level. Two files errored this way and took the whole
# collection down with them: `pytest` reported "2 errors" and ran NOTHING,
# so the pandas_ta-free run could not report on any of the other 251 tests.
#
# importorskip turns that into the skip it should always have been. It does
# not make the function importable without pandas_ta — that would mean
# restructuring engine_core's imports, which is a larger change than the
# defect warrants and is recorded here rather than done quietly.
pytest.importorskip(
    "pandas_ta",
    reason="core.engine_core imports indicators.indicators, which imports "
           "pandas_ta at module level. macro_agreement itself needs neither.")

from core.engine_core import macro_agreement


def test_agreement_scores_and_says_so():
    for macro, bias in (("BULLISH", "BULLISH"), ("BEARISH", "BEARISH")):
        delta, note = macro_agreement(macro, bias)
        assert delta == 10.0
        assert note == "The higher timeframe agrees with this bias."


def test_disagreement_scores_and_says_so():
    for macro, bias in (("BULLISH", "BEARISH"), ("BEARISH", "BULLISH")):
        delta, note = macro_agreement(macro, bias)
        assert delta == -20.0
        assert note == "The higher timeframe disagrees with this bias."


def test_a_neutral_macro_is_reported_as_a_neutral_macro():
    for bias in ("BULLISH", "BEARISH", "NEUTRAL"):
        delta, note = macro_agreement("NEUTRAL", bias)
        assert delta == 0.0
        assert note == "The higher timeframe is neutral."


def test_a_directional_macro_is_never_called_neutral():
    """
    The defect itself. This is the case the live run hit.
    """
    for macro in ("BULLISH", "BEARISH"):
        delta, note = macro_agreement(macro, "NEUTRAL")

        assert delta == 0.0, (
            "a neutral bias must not move the validation score -- there is "
            "nothing to agree or disagree with"
        )
        assert "The higher timeframe is neutral." != note, (
            f"the macro is {macro} and the note calls the higher timeframe "
            f"neutral. That is the panel contradicting its own MACRO TREND "
            f"line."
        )
        assert macro in note, (
            f"the note does not name the macro read, so the operator cannot "
            f"check it against the MACRO TREND line above: {note!r}"
        )
        assert "bias is neutral" in note.lower(), (
            f"the note should say which side is neutral: {note!r}"
        )


def test_the_note_never_claims_more_than_it_knows():
    """
    Every branch, swept. No combination may produce a sentence asserting the
    higher timeframe is neutral while the macro read says otherwise.
    """
    for macro in ("BULLISH", "BEARISH", "NEUTRAL", "", "BULLISH CONFIRMED"):
        for bias in ("BULLISH", "BEARISH", "NEUTRAL"):
            _, note = macro_agreement(macro, bias)
            claims_neutral = note == "The higher timeframe is neutral."
            macro_is_directional = ("BULLISH" in macro.upper()
                                    or "BEARISH" in macro.upper())
            assert not (claims_neutral and macro_is_directional), (
                f"macro={macro!r} bias={bias!r} produced {note!r}"
            )
