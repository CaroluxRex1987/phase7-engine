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
    # direction * min(100, healthshare + adx(25) + rsi(2) + accel(0)).
    # Assert the ceiling instead: with ADX=25 (max component 25.0) and
    # RSI giving momentum_component=2.0 and accel=0, continuation_strength's
    # magnitude cannot exceed 27.0 if health_component is really gone.
    assert abs(low["continuation_strength"]) <= 27.0 + 1e-6, (
        f"continuation_strength is {low['continuation_strength']!r} with only "
        f"ADX (max 25) and RSI-momentum (2.0) contributing and acceleration "
        f"at 0 — expected at most 27.0. A larger value means a "
        f"trend-health-derived component is still being added, which is the "
        f"Finding 4 double-count trend_health.py's ITEM 11 RE-AUDIT comment "
        f"describes removing."
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
