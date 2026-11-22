"""
Item 11, No Circular Reasoning.

WHAT THIS FILE HELD, AND WHY ONE TEST IS LEFT

Sequence item 11 (the third Critical, fixed 30 August 2026) found trend health
reaching the confidence score by three routes at once -- directly, through
bias_score's 0.30 weight, and through engine_core's validation score, which
was seeded from trend health -- and the panel printing the same number three
times. The independent audit's Finding 4 (31 August 2026) found the wider
pattern: structure regime, macro bias and volume sentiment were each counted
twice, once as one of bias_engine's six weighted factors and again as a bonus
bolted onto confidence. A third instance was internal to bias_engine, where
continuation_strength carried a trend-health-derived term.

Thirteen tests held those fixes: that confidence was a pure function of
bias_score, that structure regime and the two agreement readings could not
move it a second time, that _compute_confidence's signature had no room for
the duplicated inputs, that continuation_strength contained no health term
and ignored ADX, that validation was not seeded from trend health, that the
panel printed trend health once, that the reasoning claimed none of them as a
confidence input, and that RSI's exemption held in one trend direction and
not the other.

THE REDESIGN'S STAGE 5, 15 November 2026, removes all thirteen -- not because
the item stopped mattering, but because every path they guarded is gone with
the thing at the end of it. There is no confidence score, no expected value,
no trade quality, no validation score and no weighted sum, so there is
nothing for a factor to reach twice: the direction is one rule over
EMA50's slope and the order of the two averages, and every other surviving
factor is a GATE with a yes or a no (DECISIONS, "Ruling, 25 October 2026 --
the indicator document's eight questions", rulings 2, 3 and 6). Item 11's
clause is satisfied by the shape of the design rather than by subtraction
from a blend.

Two of the thirteen are worth naming for how they went, because this project
records that rather than quietly deleting it:

  test_the_panel_prints_trend_health_once counted the string
  "trend_health_score" in panel_render's code and asserted it appeared at
  most twice. After this stage it appears NONE, so the test PASSED
  VACUOUSLY -- a green assertion about a line that no longer exists. That is
  the fifth of the five errors of 3 September 2026 (a test assertion that
  would have passed vacuously), and it is removed rather than left green.

  test_rsi_exemption_holds_in_downtrends_and_not_in_uptrends measured, across
  RSI 0-100, that trend_health's symmetric RSI read and continuation's
  directional one were weakly correlated in downtrends (r = 0.37) and
  strongly in uptrends (r = 0.83) -- the duplicated RSI path bias_engine's
  comment recorded as worth at most 1.5 points of bias_score and
  deliberately did not fix. Both readers are gone, so the measurement has no
  subject. The finding itself is in the dated record, not lost.

WHAT IS STILL CHECKED HERE

One test, on the one factor of the old blend that survives as a gate's input:
structure.py's regime. It must be a read of close and of nothing else, so it
cannot share a raw input with another reading the decision takes. That is the
19 September 2026 independence review's standard -- "shares no raw indicator
with any other factor" -- applied to what the redesign actually reads.

The redesign's own version of this question, whether the direction and entry
quality share a measurement because both read the EMA band, was asked and
answered in the design rather than here: the draft's section 16.1 found that
EMA20_Slope is above zero exactly when the close is above the previous
candle's EMA_20, and Viktor's ruling of 7 November 2026 settled the direction
on EMA50's slope and the EMAs' order instead (section 16.4). The reconciliation
of that section against the built code is stage 6's.

Every test here is fixture-free, so run_tests.py runs it too.
"""

import pandas as pd  # noqa: F401  (used inside the test below)

def test_structure_regime_is_a_function_of_close_alone():
    """
    INDEPENDENCE REVIEW, SECOND PASS, 19 September 2026.

    bias_engine.py's dependency graph described structure_regime (weight
    0.20) as "structure.py's swing-based regime label" for as long as the
    graph has existed. It is not. The label comes from _detect_regime(),
    which reads close and nothing else. swing_struct is computed and
    reaches the panel only.

    That wrong description is why an earlier pass recorded structure_regime
    as checked and independent: the check was run against a mechanism this
    factor does not use.

    Pinned here so the description cannot drift away from the code again
    without a test going red. Two halves: the regime must respond to close,
    and it must not respond to ADX, RSI or the EMA slope columns.
    """
    import pandas as pd
    import numpy as np

    from structure.structure import StructureEngine

    def _frame(rows=40, drift=0.0, adx=25.0, rsi=50.0, slope=0.0):
        idx = pd.RangeIndex(rows)
        close = pd.Series(100.0 + idx.to_numpy() * drift, index=idx)
        return pd.DataFrame({
            "open": close, "high": close + 0.5, "low": close - 0.5,
            "close": close, "volume": 1000.0,
            "ADX": adx, "RSI": rsi,
            "EMA20_Slope": slope, "EMA50_Slope": slope,
        }, index=idx)

    # Half one: close drives it. A rising series and a falling series must
    # not produce the same regime, or the factor is reading nothing.
    up = StructureEngine()._detect_regime(_frame(drift=0.5))
    down = StructureEngine()._detect_regime(_frame(drift=-0.5))
    assert up != down, (
        f"_detect_regime returned {up!r} for a rising close series and "
        f"{down!r} for a falling one. structure_regime is supposed to be a "
        f"read of close; if these agree it is reading something else, or "
        f"nothing."
    )

    # Half two: nothing else drives it. Hold close fixed, move every other
    # indicator column to the far end of its range, and the label must not
    # move. This is the assertion the wrong description defeated.
    base = StructureEngine()._detect_regime(_frame(drift=0.5))
    for label, kwargs in (
        ("ADX", {"adx": 5.0}),
        ("ADX", {"adx": 60.0}),
        ("RSI", {"rsi": 5.0}),
        ("RSI", {"rsi": 95.0}),
        ("EMA slopes", {"slope": -1.0}),
        ("EMA slopes", {"slope": 1.0}),
    ):
        moved = StructureEngine()._detect_regime(_frame(drift=0.5, **kwargs))
        assert moved == base, (
            f"_detect_regime returned {moved!r} instead of {base!r} when only "
            f"{label} changed and close was held identical. structure_regime "
            f"would then share a raw input with trend_health, which is the "
            f"defect class the 19 September independence review exists to "
            f"catch."
        )
