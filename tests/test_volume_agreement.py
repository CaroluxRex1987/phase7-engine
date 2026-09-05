"""
Volume that runs against the bias must not be reported as supporting it.

WHAT WAS WRONG

A live run on 5 September 2026 printed, in one panel:

    VOLUME     : STRONG BEARISH DISTRIBUTION
    BIAS       : BULLISH CONFIRMED
    ...
    Validation Notes:
     - ... | Volume sentiment is supportive of current momentum.

The test was:

    if "STRONG" in volume_sentiment.upper() or "EXPANSION" in ...:
        val_score += 15
        val_notes.append("Volume sentiment is supportive of current momentum.")

It matched the WORD and ignored the DIRECTION. Strongly bearish volume scored
+15 towards a bullish validation and printed as support. On that run the +15
is what produced VALIDATION: STRONG at exactly 75.00 -- 50 baseline, +10 for
the macro agreeing, +15 for volume "supporting".

THE THIRD OF ONE CLASS

A direction-blind test producing a directional claim. The macro note was the
first, fixed 3 September. bias_engine signing trend_health from the sign of a
magnitude was the second, fixed 4 September. This is the third.

models/bias_engine.py had it right the whole time -- _VOLUME_SENTIMENT_SCORES
maps STRONG BEARISH DISTRIBUTION to -100. One quantity, computed correctly in
one module and wrongly in another, which is what check 7.6 of the auditor
instruction asks a reviewer to look for.

WEIGHTS

None is invented. +15 for volume supporting the bias, as before. -25 for
volume against it, which is the weight this same block already used for its
disconfirming branch. Strong volume against the bias is disconfirming.

FOUND BY RUNNING IT

Not by the suite. 233 tests passed on the same tree.
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
# This file errored. `volume_agreement` is a pure module-level function that
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
           "pandas_ta at module level. volume_agreement itself needs neither.")

from core.engine_core import volume_agreement

BULLISH_LABELS = ["STRONG BULLISH ACCUMULATION", "BULLISH VOLUME SUPPORT"]
BEARISH_LABELS = ["STRONG BEARISH DISTRIBUTION", "BEARISH VOLUME PRESSURE"]


def test_the_defect_itself():
    """
    The exact run that exposed it: strongly bearish volume, bullish bias.
    """
    delta, note = volume_agreement("STRONG BEARISH DISTRIBUTION", "BULLISH")

    assert delta < 0, (
        f"strongly bearish volume scored {delta:+.0f} on a bullish bias. "
        f"Anything above zero here is the defect."
    )
    assert "supportive" not in note.lower() and "supports" not in note.lower(), (
        f"the note calls opposing volume supportive: {note!r}"
    )
    assert "AGAINST" in note.upper(), note


def test_agreement_scores_and_says_so():
    for label in BULLISH_LABELS:
        delta, note = volume_agreement(label, "BULLISH")
        assert delta == 15.0, f"{label}: {delta}"
        assert "supports" in note.lower()
    for label in BEARISH_LABELS:
        delta, note = volume_agreement(label, "BEARISH")
        assert delta == 15.0, f"{label}: {delta}"
        assert "supports" in note.lower()


def test_disagreement_is_penalised_both_ways():
    for label in BEARISH_LABELS:
        delta, _ = volume_agreement(label, "BULLISH")
        assert delta == -25.0, f"{label} against BULLISH: {delta}"
    for label in BULLISH_LABELS:
        delta, _ = volume_agreement(label, "BEARISH")
        assert delta == -25.0, f"{label} against BEARISH: {delta}"


def test_divergence_still_penalised_regardless_of_bias():
    """
    Unchanged behaviour. Divergence is a warning state, not a directional
    vote, and it was already handled correctly.
    """
    for bias in ("BULLISH", "BEARISH", "NEUTRAL"):
        delta, note = volume_agreement("VOLUME DIVERGENCE", bias)
        assert delta == -25.0
        assert "divergence" in note.lower()


def test_neutral_volume_scores_nothing():
    for bias in ("BULLISH", "BEARISH", "NEUTRAL"):
        delta, note = volume_agreement("NEUTRAL VOLUME", bias)
        assert delta == 0.0
        assert "neutral" in note.lower()


def test_a_neutral_bias_has_nothing_to_agree_with():
    """
    Same fourth branch the macro note needed. Directional volume under a
    neutral bias is neither support nor opposition, and the note says which
    side is neutral rather than making a claim about the volume.
    """
    for label in BULLISH_LABELS + BEARISH_LABELS:
        delta, note = volume_agreement(label, "NEUTRAL")
        assert delta == 0.0, f"{label} under a neutral bias scored {delta}"
        assert label in note, f"the note does not name the reading: {note!r}"
        assert "bias is neutral" in note.lower(), note


def test_no_label_is_ever_called_supportive_while_opposing():
    """
    Sweep. No combination may produce a supportive note while the volume and
    the bias point opposite ways.
    """
    labels = BULLISH_LABELS + BEARISH_LABELS + [
        "VOLUME DIVERGENCE", "VOLUME EXHAUSTION", "NEUTRAL VOLUME", "",
    ]
    for label in labels:
        for bias in ("BULLISH", "BEARISH", "NEUTRAL"):
            delta, note = volume_agreement(label, bias)
            u = label.upper()
            opposed = (("BULLISH" in u and bias == "BEARISH")
                       or ("BEARISH" in u and bias == "BULLISH"))
            if opposed:
                assert delta <= 0, f"{label} / {bias} scored {delta:+.0f}"
                # The CLAIM, not the word. "BULLISH VOLUME SUPPORT" contains
                # "support" and the note quotes the label back, so a bare
                # substring test fails on correct output -- rule 30, in a test
                # written to catch rule 30's cousin.
                assert "supports this bias" not in note.lower(), f"{label} / {bias}: {note!r}"
                assert "supportive" not in note.lower(), f"{label} / {bias}: {note!r}"


def test_it_agrees_with_the_bias_engine_about_direction():
    """
    The two modules must not disagree about which way a label points. That
    disagreement is the defect, and check 7.6 exists for it.
    """
    from models.bias_engine import _VOLUME_SENTIMENT_SCORES

    for label, score in _VOLUME_SENTIMENT_SCORES.items():
        delta_bull, _ = volume_agreement(label, "BULLISH")
        delta_bear, _ = volume_agreement(label, "BEARISH")
        if score > 0:
            assert delta_bull > 0 and delta_bear < 0, (
                f"bias_engine scores {label} as bullish ({score}), validation "
                f"gives {delta_bull:+.0f} under BULLISH and {delta_bear:+.0f} "
                f"under BEARISH"
            )
        elif score < 0:
            assert delta_bear > 0 and delta_bull < 0, (
                f"bias_engine scores {label} as bearish ({score}), validation "
                f"gives {delta_bear:+.0f} under BEARISH and {delta_bull:+.0f} "
                f"under BULLISH"
            )
