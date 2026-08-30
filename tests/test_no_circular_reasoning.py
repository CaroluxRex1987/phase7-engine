"""
Sequence item 11 — Item 11, No Circular Reasoning. The third Critical.

THE DEFECT

`trend_health` reached the confidence score by three separate routes, and the
panel printed it three times:

  direct       confidence = ... + trend_health * 0.3
  via bias     trend_health * 0.30 -> bias_score -> bias_strength * 0.5 -> conf
  via          val_score = trend_health  (engine_core), then +-5/+10/-15
  validation   -> validation_state -> validation_adj -> confidence

  rendering    TREND: 95.35 / MOMENTUM: STRONG (95.35) / Current Market: 95.35

One measurement, presented as several agreeing signals. The validation path is
the sharpest: a validation score seeded with the thing it validates is not
evidence, it is a restatement.

THE TEST STEP 5 ASKED FOR

"perturb trend_health, assert confidence moves exactly once."

That is what the first two tests below do, and the pair matters. Asserting the
direct term is gone would also pass on a formula that ignored every input, so
the control asserts confidence still responds to the one path that is allowed
to carry trend health — bias strength.
"""

import ast
import os

from conftest import REPO_ROOT


def _confidence(trend_health, bias_score=60.0):
    """
    One confidence score, with everything but trend_health held fixed.

    Called directly rather than through the engine on purpose: at engine level
    trend_health legitimately moves bias_score, so a whole-pipeline test could
    not distinguish "removed the direct term" from "removed nothing".
    """
    from models.decision_model import DecisionModel

    return DecisionModel()._compute_confidence(
        bias={"score": bias_score, "raw": "BULLISH"},
        trend={"trend_health": trend_health},
        structure={"regime": "BULLISH TREND"},
        risk={"validation_state": "NEUTRAL"},
        final_action="LONG",
        reasons=[],
    )


def test_confidence_does_not_read_trend_health_directly():
    """
    With bias held fixed, trend health must not move confidence at all.

    Before this item, spanning 0 to 100 moved it by 30 points — on top of
    whatever the same measurement had already contributed through bias_score.
    """
    scores = {th: _confidence(th) for th in (0.0, 25.0, 50.0, 75.0, 100.0)}
    distinct = sorted(set(round(v, 9) for v in scores.values()))

    assert len(distinct) == 1, (
        "confidence changed when only trend_health changed:\n  "
        + "\n  ".join(f"trend_health={k:>5} -> confidence={v:.4f}"
                      for k, v in scores.items())
        + "\n\nTrend health reaches confidence through bias_score, at weight "
          "0.30 inside bias_engine. Any additional term counts one measurement "
          "twice and reports a number agreeing with itself as corroboration."
    )


def test_confidence_still_moves_with_bias_strength():
    """
    The control, and the reason the test above is not vacuous.

    A _compute_confidence that returned a constant would satisfy the previous
    assertion perfectly. This one fails if the single permitted path has been
    severed along with the duplicate.
    """
    weak = _confidence(50.0, bias_score=10.0)
    strong = _confidence(50.0, bias_score=90.0)

    assert strong > weak, (
        f"confidence did not increase with bias strength "
        f"({weak:.2f} at score 10, {strong:.2f} at score 90).\n"
        "Trend health is supposed to reach confidence through exactly one "
        "route. Zero routes is not the fix."
    )


def test_confidence_can_still_reach_the_top_of_its_range():
    """
    Removing a 30-point term without rescaling would cap confidence at 70.

    That matters beyond tidiness: _compute_ev consumes confidence as a rough
    win rate. A percentage that cannot reach its own maximum understates every
    expected value computed from it, which is a quiet way to be wrong.
    """
    best = _confidence(50.0, bias_score=100.0)
    from models.decision_model import DecisionModel

    ceiling = DecisionModel()._compute_confidence(
        bias={"score": 100.0, "raw": "BULLISH"},
        trend={"trend_health": 50.0},
        structure={"regime": "BULLISH TREND"},
        risk={"validation_state": "STRONG"},
        final_action="LONG",
        reasons=[],
    )

    assert ceiling >= 99.0, (
        f"the best possible case scores {ceiling:.1f}/100 — maximum bias "
        f"strength, structure agreeing, validation strong. If the top of the "
        f"scale is unreachable the number is not a percentage."
    )
    assert best > 0.0


def test_validation_is_not_seeded_with_trend_health():
    """
    The third path, and the one that most deserved the word "circular".

    `val_score = trend_health` meant the validation score WAS trend health,
    nudged. It then re-entered confidence as an independent-looking term, and
    the panel showed it on its own VALIDATION line.

    Checked on the AST rather than by running the engine: the assignment's
    right-hand side must be a literal, not a name borrowed from elsewhere.
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
        f"validates is a restatement, not evidence — and it reaches confidence "
        f"a second time through validation_adj."
    )


def test_the_panel_prints_trend_health_once():
    """
    Item 10(a), merged into this item because it is the same defect rendered.

    TREND, MOMENTUM's number and Current Market were all the same value. A
    reader seeing three numbers agree reasonably concludes three things agree.
    """
    with open(os.path.join(REPO_ROOT, "core", "panel_render.py"), encoding="utf-8") as f:
        source = f.read()

    code_only = "\n".join(line.split("#", 1)[0] for line in source.splitlines())
    renders = code_only.count("trend_health_score")

    # One extraction, one render.
    assert renders <= 2, (
        f"trend_health_score appears {renders} times in panel_render code.\n"
        "It should be extracted once and printed once, on the TREND line. "
        "MOMENTUM's label (STRONG / BUILDING / EXTENDED) is momentum_mode and "
        "is a genuinely separate reading; its number was not."
    )

    assert "Current Market" not in code_only, (
        "the Current Market line is back. It rendered trade_quality_current, "
        "which was trend_health verbatim under a third name."
    )


def test_the_reasoning_no_longer_claims_trend_health_as_a_confidence_input():
    """
    Step 5's coupling rule: "the reason strings change in the same commit —
    prose describing the old formula is an Item 8 regression the moment the
    number changes."

    The sentence used to read "Confidence is X/100 — bias strength is Y/100,
    trend health is Z/100, ...", naming as an input the exact term this item
    removed.
    """
    from models.decision_model import DecisionModel

    reasons = []
    DecisionModel()._compute_confidence(
        bias={"score": 60.0, "raw": "BULLISH"},
        trend={"trend_health": 95.0},
        structure={"regime": "BULLISH TREND"},
        risk={"validation_state": "NEUTRAL"},
        final_action="LONG",
        reasons=reasons,
    )

    text = " ".join(reasons)
    assert "95" not in text, (
        f"the confidence explanation still quotes the trend health value:\n"
        f"  {text}\n"
        "It is not an input to this score. Prose describing a calculation that "
        "no longer runs is the Item 8 regression the coupling rule exists to "
        "prevent."
    )
