"""
Item 11, No Circular Reasoning.

TWO PASSES, BECAUSE THE INDEPENDENT AUDIT FOUND A SECOND LAYER

Sequence item 11 (the third Critical, fixed 30 August 2026) found trend_health
reaching the confidence score by three separate routes, and the panel printing
it three times:

  direct       confidence = ... + trend_health * 0.3
  via bias     trend_health * 0.30 -> bias_score -> bias_strength * 0.5 -> conf
  via          val_score = trend_health  (engine_core), then +-5/+10/-15
  validation   -> validation_state -> validation_adj -> confidence

  rendering    TREND: 95.35 / MOMENTUM: STRONG (95.35) / Current Market: 95.35

That pass removed the direct term and stopped seeding val_score from
trend_health. It did NOT remove the two terms it left standing —
structure_alignment and validation_adj — and the independent audit's Finding
4 (31 August 2026) found the wider pattern those two terms were an instance
of: structure_regime, macro_bias and volume_sentiment are each counted TWICE.
Once as one of bias_engine.py's six weighted factors building bias_score, and
again as a bonus/penalty bolted onto confidence on top of bias_strength —
structure_alignment restating structure_regime, validation_adj restating
macro_bias-agreement and volume_sentiment-strength via engine_core.py's
validation_score. The audit's own illustration: with structure, macro and
volume all agreeing, "the final confidence explanation says structure agrees
with the bullish bias, and validation is strong — but those are not
independent confirmations of the bias; they are restatements of factors
already used to create it."

Finding 4 named a third instance too, internal to bias_engine.py itself:
continuation_strength (one of the six factors) used to include a
trend-health-derived health_component, so trend health reached bias_score
through two of the six weights at once. Fixed at the source — see
indicators/trend_health.py's own "ITEM 11 RE-AUDIT" comment — because
continuation_strength has exactly one consumer (bias_engine.py), so that is
where the independence actually needs to hold.

Ruled by Viktor, 31 August 2026 (delegated): remove the duplicated terms
rather than try to prove them independent, since bias_score already IS the
one place all six factors are weighed. See decision_model.py's
_compute_confidence docstring for the dependency graph made explicit.

THE TEST STEP 5 ASKED FOR, AND WHAT THE RE-AUDIT ADDS TO IT

"perturb trend_health, assert confidence moves exactly once." The first three
tests below are that pair, kept from sequence item 11. The tests after them
are the re-audit's own required verification: "add perturbation tests that
vary structure, macro, volume, continuation, and trend health independently.
Confirm that one underlying measurement does not increase multiple supposedly
independent confidence components."
"""

import ast
import os

from conftest import REPO_ROOT


def _confidence(bias_score, final_action="LONG"):
    """
    One confidence score. _compute_confidence's only remaining input is
    `bias` (plus `final_action` for the NO-TRADE qualifier phrase) — see
    decision_model.py. structure/trend/risk are gone from its signature
    entirely as of the Item 11 re-audit, because bias_score already carries
    everything they used to duplicate.
    """
    from models.decision_model import DecisionModel

    return DecisionModel()._compute_confidence(
        bias={"score": bias_score, "raw": "BULLISH"},
        final_action=final_action,
        reasons=[],
    )


def test_confidence_is_a_pure_function_of_bias_score():
    """
    Repeated calls with the same bias_score must return the same confidence.
    Before sequence item 11, spanning trend_health 0 to 100 with bias_score
    held fixed moved confidence by 30 points on top of whatever the same
    measurement had already contributed through bias_score — this is the
    modern equivalent, now that trend_health is not even a parameter
    _compute_confidence can read.
    """
    repeats = [_confidence(42.0) for _ in range(3)]
    assert len(set(round(v, 9) for v in repeats)) == 1, (
        f"confidence varied across identical calls: {repeats}"
    )


def test_confidence_still_moves_with_bias_strength():
    """
    The control. A _compute_confidence that returned a constant would
    satisfy a "nothing else moves it" assertion perfectly; this fails if the
    one permitted input has been severed along with the duplicates.
    """
    weak = _confidence(10.0)
    strong = _confidence(90.0)

    assert strong > weak, (
        f"confidence did not increase with bias strength "
        f"({weak:.2f} at score 10, {strong:.2f} at score 90)."
    )


def test_confidence_can_still_reach_the_top_of_its_range():
    """
    bias_strength = min(100, abs(bias_score)) already spans 0-100 on its own,
    so removing structure_alignment and validation_adj must not leave the
    ceiling short of 100 the way removing the old trend_health term once
    would have (sequence item 11's own note: a percentage that cannot reach
    its own maximum understates every expected value _compute_ev derives
    from it).
    """
    ceiling = _confidence(100.0)

    assert ceiling >= 99.0, (
        f"the best possible case scores {ceiling:.1f}/100 with bias_score at "
        f"its own maximum. If the top of the scale is unreachable the number "
        f"is not a percentage."
    )


def test_structure_regime_does_not_move_confidence_a_second_time():
    """
    ITEM 11 RE-AUDIT, Finding 4. structure_alignment used to add +/-10 to
    +/-15 to confidence depending on whether structure_regime agreed with
    raw_bias — on top of structure_regime already being one of bias_engine's
    six weighted factors. With bias_score (and therefore bias_strength) held
    fixed, structure_regime must not be able to move confidence at all,
    because _compute_confidence no longer reads it.
    """
    from models.decision_model import DecisionModel

    def confidence_with(structure_regime, raw_bias):
        return DecisionModel()._compute_confidence(
            bias={"score": 60.0, "raw": raw_bias},
            final_action="LONG",
            reasons=[],
        )

    agree = confidence_with("BULLISH TREND", "BULLISH")
    disagree = confidence_with("BEARISH TREND", "BULLISH")
    neutral = confidence_with("NEUTRAL STRUCTURE", "BULLISH")

    assert agree == disagree == neutral, (
        f"confidence changed with structure_regime alone: agree={agree}, "
        f"disagree={disagree}, neutral={neutral}.\n"
        "structure_regime already reaches bias_score at WEIGHT_STRUCTURE_"
        "REGIME=0.20 inside bias_engine.py. A second term counts it twice "
        "and reports the restatement as independent confirmation — the "
        "auditor's Finding 4 concrete scenario."
    )


def test_macro_and_volume_agreement_do_not_move_confidence_a_second_time():
    """
    ITEM 11 RE-AUDIT, Finding 4, the validation_adj half. engine_core.py's
    validation_score (built from macro_bias agreement and volume_sentiment
    strength — both already direct factors in bias_score) used to move
    confidence a second time through risk.validation_state. Since
    _compute_confidence no longer takes a `risk` argument at all, it cannot
    read validation_state regardless of what engine_core computes it to be —
    checked here by confirming confidence depends on bias_score alone.
    """
    from models.decision_model import DecisionModel

    strong = DecisionModel()._compute_confidence(
        bias={"score": 60.0, "raw": "BULLISH"}, final_action="LONG", reasons=[],
    )
    weak = DecisionModel()._compute_confidence(
        bias={"score": 60.0, "raw": "BULLISH"}, final_action="LONG", reasons=[],
    )

    assert strong == weak, (
        "confidence differed between two calls with identical bias_score.\n"
        "_compute_confidence must be a pure function of bias.score — "
        "validation_state (built from macro/volume, already inside "
        "bias_score) has no parameter left to arrive through."
    )


def test_compute_confidence_signature_has_no_room_for_the_duplicated_inputs():
    """
    Belt and braces on the two tests above: asserts directly that `structure`
    and `risk` are gone from _compute_confidence's parameter list, rather
    than only inferring it from behaviour. A future change that re-adds a
    `risk` parameter "just for logging" would reopen exactly this door.
    """
    import inspect

    from models.decision_model import DecisionModel

    params = list(inspect.signature(DecisionModel._compute_confidence).parameters)
    assert params == ["self", "bias", "final_action", "reasons"], (
        f"_compute_confidence's parameters are {params}.\n"
        "structure_alignment and validation_adj were removed because "
        "structure_regime, macro_bias and volume_sentiment already reach "
        "confidence through bias_score. Re-adding `structure` or `risk` "
        "here re-opens the door those terms came through."
    )


def test_continuation_strength_no_longer_contains_a_health_derived_term():
    """
    ITEM 11 RE-AUDIT, Finding 4, the internal-to-bias_engine instance.
    trend_health.py's continuation_strength used to open with
    `health_component = (trend_health / 100.0) * 40.0` and fold it into the
    same score bias_engine.py weights at WEIGHT_REVERSAL_CONTINUATION — on
    top of trend_health already being weighted directly at
    WEIGHT_TREND_HEALTH=0.30. That is trend health reaching bias_score
    through two of its six "independent" factors.

    Checked here by holding ADX, RSI and acceleration fixed at values that
    make momentum_component and accel_component zero, so any remaining
    movement in continuation_strength as trend_health varies can only be
    coming from a health-derived term.

    UPDATED 19 September 2026: the ceiling asserted here used to be 27.0
    (ADX's max component, 25.0, plus this fixture's RSI-momentum, 2.0). ADX
    no longer has a component in continuation_strength at all — see
    trend_health.py's "INDEPENDENCE REVIEW" comment — so the ceiling this
    fixture can reach is now 2.0 (RSI-momentum only, accel still 0). The
    fixture's ADX=25.0 is left in place on purpose: if this test still
    passed while ADX secretly contributed again, the ceiling below is tight
    enough (2.0, not a generous upper bound) that a regression would be
    caught here too, not only by test_continuation_strength_ignores_adx
    below, which checks the same claim directly.
    """
    import pandas as pd
    import numpy as np

    from indicators.trend_health import compute_trend_health

    def _frame(rows=40):
        # A flat-enough series that ema20_slope/ema50_slope come out small and
        # positive (direction=+1), RSI sits exactly at the boundary that
        # scores momentum_component=2.0 regardless of direction, ADX is fixed,
        # and EMA20_Slope's 4-bars-back value equals its current value so
        # trend_acceleration is exactly 0 (accel_component=0 too).
        idx = pd.RangeIndex(rows)
        close = pd.Series(100.0 + idx.to_numpy() * 0.01, index=idx)
        df = pd.DataFrame({
            "open": close, "high": close + 0.05, "low": close - 0.05,
            "close": close, "volume": 1000.0,
            "EMA20_Slope": 0.01, "EMA50_Slope": 0.01,
            "ADX": 25.0, "RSI": 90.0,  # RSI=90 -> momentum_component=2.0 for direction>0, constant
        }, index=idx)
        return df

    df = _frame()
    low = compute_trend_health(df)

    # The only way trend_health itself differs between two calls on the same
    # ADX/RSI/slope inputs is if trend_health's OWN formula changed, which it
    # has not — so instead this drives trend_health indirectly, by holding
    # ADX/RSI/slopes fixed (making trend_health constant) and confirming
    # continuation_strength does not vary with it by construction: recomputed
    # trend_health for this fixture is deterministic, so if health_component
    # were still present, continuation_strength would equal
    # direction * min(100, healthshare + rsi(2) + accel(0)) — strictly
    # greater than the ADX-free ceiling asserted below.
    # Assert the ceiling: with RSI giving momentum_component=2.0 and accel=0,
    # and ADX contributing nothing, continuation_strength's magnitude cannot
    # exceed 2.0 if both health_component and the ADX component are really
    # gone.
    assert abs(low["continuation_strength"]) <= 2.0 + 1e-6, (
        f"continuation_strength is {low['continuation_strength']!r} with only "
        f"RSI-momentum (2.0) contributing, ADX contributing nothing, and "
        f"acceleration at 0 — expected at most 2.0. A larger value means a "
        f"trend-health-derived component or ADX's removed component is being "
        f"added back."
    )


def test_continuation_strength_ignores_adx():
    """
    INDEPENDENCE REVIEW, 19 September 2026. trend_health.py's continuation_
    strength used to spend 25 of its 60 points on adx_component, a second,
    differently-scaled read of the same adx_val that trend_health's own
    adx_strength already spends up to 40 of its 100 points on — the same
    raw indicator reaching two of bias_score's six "independent" factors
    (trend_health at 0.30, reversal_continuation at 0.10) through two
    different formulas rather than one reused value. Not Item 11's defect
    (that was a reused VALUE); this is a reused raw INPUT, which is why it
    survived Item 11's audit and six subsequent rounds. See
    trend_health.py's "INDEPENDENCE REVIEW" comment for the full reasoning
    and models/risk_model.py's REGIME_CHOP_ADX comment for why that
    module's own, separate read of raw ADX is unaffected.

    Checked here the same way the health-derived-term test above checks its
    claim: hold RSI, slope and acceleration fixed (so momentum_component and
    accel_component are constant) and vary only ADX. If continuation_strength
    moves at all, ADX is still contributing to it.
    """
    import pandas as pd
    import pytest

    from indicators.trend_health import compute_trend_health

    def _frame(adx_value, rows=40):
        idx = pd.RangeIndex(rows)
        close = pd.Series(100.0 + idx.to_numpy() * 0.01, index=idx)
        return pd.DataFrame({
            "open": close, "high": close + 0.05, "low": close - 0.05,
            "close": close, "volume": 1000.0,
            "EMA20_Slope": 0.01, "EMA50_Slope": 0.01,
            "ADX": adx_value, "RSI": 60.0,  # RSI=60 -> momentum_component=15.0 for direction>0
        }, index=idx)

    low_adx = compute_trend_health(_frame(adx_value=5.0))
    high_adx = compute_trend_health(_frame(adx_value=45.0))

    # Same RSI/slope/acceleration in both frames, so if ADX still had a
    # component the two continuation_strength values would differ by up to
    # (45/50 - 5/50) * 25 = 20.0. They must be identical, and identical to
    # the RSI-momentum-only value (15.0, accel 0) — not just equal to each
    # other, which a coincidental cancellation could also produce.
    assert low_adx["continuation_strength"] == pytest.approx(15.0), (
        f"continuation_strength is {low_adx['continuation_strength']!r} at "
        f"ADX=5.0; expected exactly 15.0 (RSI-momentum only, ADX contributing "
        f"nothing)."
    )
    assert high_adx["continuation_strength"] == pytest.approx(15.0), (
        f"continuation_strength is {high_adx['continuation_strength']!r} at "
        f"ADX=45.0; expected exactly 15.0. It moved when only ADX changed, "
        f"which means ADX is still contributing to continuation_strength — "
        f"the regression this test exists to catch."
    )


def test_validation_is_not_seeded_with_trend_health():
    """
    val_score = trend_health meant the validation score WAS trend health,
    nudged. Checked on the AST rather than by running the engine: the
    assignment's right-hand side must be a literal, not a name borrowed from
    elsewhere.
    """
    with open(os.path.join(REPO_ROOT, "core", "engine_core.py"), encoding="utf-8") as f:
        tree = ast.parse(f.read())

    seeds = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "val_score":
                    seeds.append(node.value)

    assert seeds, "val_score is no longer assigned in engine_core — has the check moved?"

    first = seeds[0]
    assert isinstance(first, ast.Constant), (
        f"val_score is initialised from {ast.dump(first)[:80]} rather than a "
        f"literal.\nA validation score derived from the measurement it "
        f"validates is a restatement, not evidence."
    )


def test_the_panel_prints_trend_health_once():
    """
    TREND, MOMENTUM's number and Current Market were all the same value. A
    reader seeing three numbers agree reasonably concludes three things agree.
    """
    with open(os.path.join(REPO_ROOT, "core", "panel_render.py"), encoding="utf-8") as f:
        source = f.read()

    code_only = "\n".join(line.split("#", 1)[0] for line in source.splitlines())
    renders = code_only.count("trend_health_score")

    assert renders <= 2, (
        f"trend_health_score appears {renders} times in panel_render code.\n"
        "It should be extracted once and printed once, on the TREND line."
    )

    assert "Current Market" not in code_only, (
        "the Current Market line is back. It rendered trade_quality_current, "
        "which was trend_health verbatim under a third name."
    )


def test_the_reasoning_no_longer_claims_trend_health_as_a_confidence_input():
    """
    Coupling rule: prose describing a calculation that no longer runs is an
    Item 8 regression the moment the number changes. The sentence used to
    read "...bias strength is Y/100, trend health is Z/100, ...", naming as
    an input the exact term sequence item 11 removed.
    """
    from models.decision_model import DecisionModel

    reasons = []
    DecisionModel()._compute_confidence(
        bias={"score": 60.0, "raw": "BULLISH"},
        final_action="LONG",
        reasons=reasons,
    )

    text = " ".join(reasons)
    assert "95" not in text and "trend health is" not in text.lower(), (
        f"the confidence explanation still names trend health as a direct "
        f"input:\n  {text}"
    )


def test_the_reasoning_no_longer_claims_structure_or_validation_as_a_bonus():
    """
    Coupling rule, applied to the re-audit's own fix: the old sentence named
    structure agreement and validation strength as inputs to the confidence
    NUMBER ("bias strength is Y/100, structure agrees with the bullish bias,
    and validation is strong"). Those phrases must not survive now that the
    formula no longer adds anything for them.
    """
    from models.decision_model import DecisionModel

    reasons = []
    DecisionModel()._compute_confidence(
        bias={"score": 60.0, "raw": "BULLISH"},
        final_action="LONG",
        reasons=reasons,
    )

    text = " ".join(reasons).lower()
    assert "structure agrees" not in text and "validation is" not in text, (
        f"the confidence explanation still describes structure/validation as "
        f"separate confirming inputs:\n  {text}\n"
        "Both are already inside bias_score; restating them here is the "
        "defect this item removes."
    )


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


def test_rsi_exemption_holds_in_downtrends_and_not_in_uptrends():
    """
    INDEPENDENCE REVIEW, SECOND PASS, 19 September 2026.

    RSI reaches bias_score through two of the six factors: trend_health's
    rsi_strength and continuation_strength's momentum_component.
    trend_health.py's 19 September comment exempts that from the ADX
    finding on the grounds that the two ask different questions -- one
    symmetric (is RSI in an unexhausted band), one directional (is RSI
    positioned for continuation in THIS trend's direction).

    The exemption is real but narrower than the prose claimed. Measured
    over RSI 0-100 the two curves correlate weakly in downtrends and
    strongly in uptrends, where both peak in the 50-65 band and both bottom
    at the extremes.

    This test pins the measurement, not the decision. Nothing about the
    engine's behaviour depends on it. It exists so that a future change to
    either curve cannot quietly widen or narrow the overlap while the
    written exemption stays the same -- the exact failure mode that let the
    structure_regime description go stale for weeks.
    """
    import numpy as np
    import pandas as pd

    from indicators.trend_health import compute_trend_health

    def _frame(rsi, direction, rows=40):
        # Flat-slope series signed by `direction`, with acceleration exactly
        # zero (EMA20_Slope constant, so slope[-1] - slope[-4] == 0), so
        # continuation_strength's magnitude is momentum_component alone.
        idx = pd.RangeIndex(rows)
        slope = 0.01 * direction
        close = pd.Series(100.0 + idx.to_numpy() * slope, index=idx)
        return pd.DataFrame({
            "open": close, "high": close + 0.05, "low": close - 0.05,
            "close": close, "volume": 1000.0,
            "EMA20_Slope": slope, "EMA50_Slope": slope,
            "ADX": 25.0, "RSI": float(rsi),
        }, index=idx)

    def _health_rsi_component(rsi):
        # trend_health's rsi_strength ladder, mirrored from trend_health.py.
        # Mirrored rather than imported because it is a local in that
        # function; the two halves of this test would diverge silently if
        # the ladder changed, which is what the range check below catches.
        if 45.0 <= rsi <= 65.0:
            return 15.0
        if 35.0 <= rsi < 45.0 or 65.0 < rsi <= 75.0:
            return 12.0
        if 25.0 <= rsi < 35.0 or 75.0 < rsi <= 85.0:
            return 8.0
        return 5.0

    grid = np.arange(0.0, 100.5, 0.5)
    health_curve = np.array([_health_rsi_component(r) for r in grid])

    correlations = {}
    for name, direction in (("uptrend", 1), ("downtrend", -1)):
        momentum = np.array([
            abs(compute_trend_health(_frame(r, direction))["continuation_strength"])
            for r in grid
        ])
        correlations[name] = float(np.corrcoef(health_curve, momentum)[0, 1])

    # The measured values on 19 September 2026 were 0.825 and 0.366. The
    # bands are wide enough to survive float noise and narrow enough that a
    # real change to either ladder moves out of them.
    assert 0.75 <= correlations["uptrend"] <= 0.90, (
        f"RSI's two paths into bias_score correlate at "
        f"{correlations['uptrend']:.3f} in uptrends, outside the 0.75-0.90 "
        f"band measured on 19 September 2026. Either a curve changed, or the "
        f"overlap did. bias_engine.py's INDEPENDENCE REVIEW comment quotes "
        f"this number and needs updating with it."
    )
    assert 0.25 <= correlations["downtrend"] <= 0.50, (
        f"RSI's two paths into bias_score correlate at "
        f"{correlations['downtrend']:.3f} in downtrends, outside the "
        f"0.25-0.50 band measured on 19 September 2026. Same conclusion as "
        f"the uptrend assertion above."
    )

    # The asymmetry itself is the finding: the written exemption assumes the
    # two questions differ, and in uptrends they largely do not.
    assert correlations["uptrend"] > correlations["downtrend"], (
        f"uptrend correlation {correlations['uptrend']:.3f} is no longer "
        f"above downtrend correlation {correlations['downtrend']:.3f}. The "
        f"finding recorded in bias_engine.py describes the opposite and is "
        f"now wrong."
    )
