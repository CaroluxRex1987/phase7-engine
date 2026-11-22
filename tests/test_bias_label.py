"""
The bias label is a function of the score, with no memory.

FINDING 18 (review of 21 September 2026, docs/PHASE7_NEXT.md). The record said
the bias state machine had a "persistence requirement" that stopped gating
trades at work order F. Read on 27 September: BiasStateMachine.transition()
never read its previous state -- every branch assigned self.state from the
current raw_bias and bias_score -- and engine_core built a fresh instance each
run. CONFIRMED only ever meant |bias_score| > 30.

Viktor's ruling, 27 September 2026, by agreeing to Claude's suggestion
(docs/PHASE7_DECISIONS.md, "Ruling, 27 September 2026 -- the bias label is a
function of the score (finding 18)"): keep the behaviour, word for word, and
make the code say what it does. The class became models.bias_engine.bias_label.

What these tests hold:

  - the labels at every boundary, on the inputs the engine produces (raw_bias
    derived from the score, as calculate_dynamic_bias does);
  - the labels on inputs the engine never produces, exactly as the class gave
    them -- pinned so that "no label changed" is checked, not asserted;
  - no memory: a label does not depend on what was asked before. A side that
    must hold for N candles was not chosen (on the list for after the audit);
    adding memory here is a new trading-adjacent rule and should fail this
    file, so that it is done on purpose;
  - core/engine_core.py labels both AERO and BTC through bias_label and holds
    no state machine (read from its source, so no pandas_ta is needed).

The golden test covers the engine path: its fixture records BULLISH CONFIRMED
for AERO and BEARISH CONFIRMED for BTC.

Before this commit, sandbox only: the old class and bias_label gave the same
label on 126,120 inputs (six raw_bias values, including None and a lower-case
one, crossed with scores from -105 to +105 in 0.01 steps, None, NaN, +-inf and
the boundaries), with one class instance reused across the whole grid.

Fixture-free, per run_tests.py. None of these needs pandas_ta.

THE REDESIGN'S STAGE 2, 14 November 2026. bias_label is gone. The direction
is EMA50's slope and the EMAs' order (Viktor's ruling of 7 November 2026),
with no score behind it, so there is nothing for CONFIRMED to mean: the
label is the direction, for the asset and for BTC. Everything above is the
dated account of the function this file held. Four of its seven tests went
with the function (the boundaries, a score not computed, the inputs the
engine never produces, no memory), one is rewritten (how engine_core gets
the two labels), and two stand: no state machine in engine_core or in
bias_engine. The golden fixture records BULLISH for both now. The rule
itself is held in tests/test_direction_is_the_slow_trends_side.py.
"""

import ast
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


def _engine_core_tree():
    path = os.path.join(ROOT, "core", "engine_core.py")
    with open(path, encoding="utf-8") as f:
        return ast.parse(f.read())


def test_engine_core_takes_both_labels_from_the_direction():
    """
    Until stage 2: detailed_bias = bias_label(raw_bias, bias_score), and the
    same for BTC. Now each is assigned from the raw label by name, with
    nothing in between that could add a word to it.
    """
    tree = _engine_core_tree()
    assigned = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name) and target.id in (
                    "detailed_bias", "btc_detailed_bias"):
                assigned.setdefault(target.id, []).append(
                    node.value.id if isinstance(node.value, ast.Name)
                    else ast.dump(node.value))
    assert assigned.get("detailed_bias") == ["raw_bias"], assigned
    assert assigned.get("btc_detailed_bias") == ["btc_raw_bias"], assigned

    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    imported = {a.name for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)
                for a in n.names}
    assert "bias_label" not in names | imported, (
        "engine_core refers to bias_label again")


def test_engine_core_holds_no_state_machine():
    tree = _engine_core_tree()
    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    attrs = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    imported = {a.name for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)
                for a in n.names}
    found = sorted(x for x in names | attrs | imported
                   if "statemachine" in x.lower().replace("_", "")
                   or x == "transition")
    assert not found, f"engine_core still refers to: {found}"


def test_bias_engine_has_no_state_machine_class_and_no_label_function():
    import models.bias_engine as be
    assert not hasattr(be, "BiasStateMachine")
    # Stage 2: this asserted callable(be.bias_label). A label function that
    # came back would be a second source for a word the direction decides.
    assert not hasattr(be, "bias_label")
    assert callable(be.direction_from_emas)
