"""
A trend that stops accelerating must not stop having a direction.

WHAT WAS WRONG

models/bias_engine.py derived the trend's direction from the sign of
continuation_strength:

    trend_direction = 1 if continuation_strength > 0 else (
        -1 if continuation_strength < 0 else 0)

Those are different quantities. Continuation answers "is this trend still
going?" Direction answers "which way is it pointing?"

indicators/trend_health.py floors continuation at zero by design -- a trend
that is not continuing scores zero continuation, and factor 6 of the bias
blend reflects that correctly. But the INFERRED direction went to zero with
it, and the next line multiplies trend_health by that zero. A 30% weight
disappeared, silently, while the panel kept printing a direction taken from
the very same slope test.

MEASURED BEFORE IT WAS RULED ON

9,800 bars, fifteen pairs, 4h and 1d, fetched live on 4 September 2026:

    floor fired               70 bars, 0.71%
    effect on bias_score      median 21.3 points, max 26.4
    past the +/-20 threshold  52 of 70
    trend_health when fired   up to 88.1
    sign disagreements        ZERO

It concentrated on the daily timeframe -- 1.20% against 0.22% on 4h -- and on
downtrends, better than two to one. The zero sign disagreements matter most:
the floor never corrected a direction, it only deleted a factor.

THE FIX, AND WHAT IT DELIBERATELY DOES NOT DO

The floor stays. It is right about continuation. What changed is that the
direction now travels from trend_health, which computes it from the slope and
always did, instead of being inferred from a magnitude.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.bias_engine import calculate_dynamic_bias, WEIGHT_TREND_HEALTH


def _engine_available():
    try:
        import pandas_ta  # noqa: F401
        return True
    except Exception:
        return False


def _bias(**over):
    kw = dict(
        trend_sequence="NONE",
        trend_health=90.0,
        trend_exhaustion=False,
        reversal_direction="NONE",
        reversal_strength=0.0,
        continuation_strength=40.0,
        trend_direction_sign=1,
        structure_regime="NEUTRAL STRUCTURE",
        volume_sentiment="NEUTRAL VOLUME",
        supertrend_direction=0.0,
        macro_bias="NEUTRAL",
    )
    kw.update(over)
    components = {}
    raw, score = calculate_dynamic_bias(components=components, **kw)
    return raw, score, components


def test_a_decelerating_trend_keeps_its_direction():
    """
    The defect itself. continuation_strength is zero -- the trend has stopped
    continuing -- but the trend is still pointing somewhere and still healthy.
    """
    _, score, comp = _bias(continuation_strength=0.0, trend_direction_sign=1)

    factor = comp["factors"]["trend_health"]
    assert factor["signed"] == pytest.approx(90.0), (
        f"a healthy uptrend with zero continuation contributed "
        f"{factor['signed']} instead of +90. The 30% weight was zeroed by the "
        f"continuation floor, which is the defect this test exists for."
    )
    assert factor["contribution"] == pytest.approx(90.0 * WEIGHT_TREND_HEALTH)
    assert score > 20.0, (
        f"bias_score came back {score:.2f}. With trend health 90 and nothing "
        f"opposing it, the blend should clear the direction threshold."
    )


def test_the_same_holds_for_a_decelerating_downtrend():
    """
    Measured firings were bearish better than two to one, so the bearish case
    is not a mirror-image afterthought.
    """
    _, score, comp = _bias(continuation_strength=0.0, trend_direction_sign=-1)

    assert comp["factors"]["trend_health"]["signed"] == pytest.approx(-90.0)
    assert score < -20.0, f"bias_score came back {score:.2f}"


def test_continuation_still_floors_and_still_counts_for_nothing():
    """
    The floor is correct and stays. Only the direction stopped depending on it.
    """
    _, _, comp = _bias(continuation_strength=0.0, trend_direction_sign=1)
    assert comp["factors"]["reversal_continuation"]["contribution"] == pytest.approx(0.0)


def test_the_direction_is_not_inferred_from_continuation_any_more():
    """
    Source guard. The two values are now independent, so a run where they
    point differently must follow the direction, not the magnitude.
    """
    _, _, comp = _bias(continuation_strength=40.0, trend_direction_sign=-1)
    assert comp["factors"]["trend_health"]["signed"] == pytest.approx(-90.0), (
        "trend health was signed by continuation_strength rather than by "
        "trend_direction_sign -- the inference is back."
    )


def test_a_flat_trend_still_contributes_nothing():
    _, _, comp = _bias(trend_direction_sign=0)
    assert comp["factors"]["trend_health"]["signed"] == pytest.approx(0.0)


def test_the_parameter_is_required_and_validated():
    """
    No default. A default here would be the copy_df pattern sequence item 6
    removed: a safe setting every caller declines to take.
    """
    with pytest.raises(TypeError):
        calculate_dynamic_bias(
            trend_sequence="NONE", trend_health=90.0, trend_exhaustion=False,
            reversal_direction="NONE", reversal_strength=0.0,
            continuation_strength=0.0,
        )

    with pytest.raises(ValueError):
        _bias(trend_direction_sign=2)


def test_trend_health_reports_a_sign_that_matches_its_own_label():
    """
    The producer's end. The number and the label come from one slope test and
    must never disagree -- 9,800 measured bars found zero disagreements, and
    this keeps it that way.

    ROUND 6 FOLLOW-ON, 12 September 2026. Adding the `expect` assertion below
    surfaced a second, pre-existing defect in THIS TEST's own fixture, found
    while verifying the assertion actually catches the named mutant rather
    than a fixture artifact: a raw OHLCV frame handed straight to
    compute_trend_health is missing EMA20_Slope, EMA50_Slope, ADX and RSI --
    columns compute_trend_health reads by name and which only
    add_technical_indicators() computes. Every input showed
    "(column absent)" in degraded_inputs, so the ORIGINAL (weaker) version of
    this test was passing on a frame that could never produce anything but
    NEUTRAL/0 -- it always took the `else` branch, on real code, on both
    slopes, which is exactly how it also passed unchanged under the
    always-neutral mutant. Fixed by running the frame through the same
    add_technical_indicators -> calculate_structure pipeline
    core/engine_core.py uses before it ever calls compute_trend_health,
    rather than calling compute_trend_health directly on raw OHLCV.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    import numpy as np
    import pandas as pd

    from core import config
    from indicators.indicators import add_technical_indicators
    from indicators.trend_health import compute_trend_health
    from structure.structure import calculate_structure

    for slope, expect in ((+1.0, 1), (-1.0, -1)):
        n = 200
        close = 100.0 + slope * np.arange(n) * 0.5
        df = pd.DataFrame({
            "open": close, "high": close * 1.002, "low": close * 0.998,
            "close": close, "volume": np.full(n, 1000.0),
        }, index=pd.date_range("2025-01-01", periods=n, freq="4h"))

        df, failures = add_technical_indicators(df)
        assert not failures, (
            f"add_technical_indicators reported failures on a clean synthetic "
            f"series: {[str(f) for f in failures]} -- this test needs a real "
            f"indicator frame, not a degraded one, to mean anything."
        )
        structure_obj = calculate_structure(
            df, lookback=config.STRUCT_LOOKBACK,
            volume_profile_bins=config.VOLUME_PROFILE_BINS,
        )
        df_struct = structure_obj.get("df", df)

        out = compute_trend_health(df_struct)
        assert not out.get("degraded_inputs"), (
            f"compute_trend_health degraded on a fully-indicatored series: "
            f"{out.get('degraded_inputs')} -- the fixture is still not "
            f"reaching a real reading."
        )
        label = str(out.get("trend_direction", "")).upper()
        sign = out.get("trend_direction_sign")

        assert sign is not None, "trend_direction_sign is missing from the output"
        if "BULL" in label:
            assert sign == 1, f"label {label} but sign {sign}"
        elif "BEAR" in label:
            assert sign == -1, f"label {label} but sign {sign}"
        else:
            assert sign == 0, f"label {label} but sign {sign}"

        # ROUND 6 MUTANT ESCAPE (GPT-6 Astra), 12 September 2026. Everything
        # above only checks that the sign and the label agree WITH EACH
        # OTHER -- an always-neutral compute_trend_health (label "NEUTRAL",
        # sign 0 unconditionally, ignoring the input entirely) satisfies
        # every assertion above for both the rising and falling series, since
        # the neutral branch's own assertion is `sign == 0` and a constant
        # function is internally consistent with itself. `expect` was defined
        # in the loop header for exactly this check and never read. This is
        # the check: the sign must match what the ACTUAL slope of the input
        # demands, not merely agree with whatever label the function chose to
        # attach to it.
        assert sign == expect, (
            f"a {'rising' if slope > 0 else 'falling'} 120-bar series produced "
            f"trend_direction_sign={sign} (label {label!r}); expected {expect}. "
            "If this reads 0 for both directions, compute_trend_health has "
            "stopped reading its input."
        )
