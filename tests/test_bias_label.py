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
"""

import ast
import itertools
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from models.bias_engine import bias_label, RAW_BIAS_THRESHOLD  # noqa: E402


def _raw(score):
    """raw_bias as calculate_dynamic_bias derives it from the score."""
    if score > RAW_BIAS_THRESHOLD:
        return "BULLISH"
    if score < -RAW_BIAS_THRESHOLD:
        return "BEARISH"
    return "NEUTRAL"


# (score, label) on the inputs the engine produces.
_ENGINE_CASES = [
    (100.0, "BULLISH CONFIRMED"),
    (30.0001, "BULLISH CONFIRMED"),
    (30.0, "BULLISH"),            # > 30 needed; the ladder acts at >= 30
    (25.0, "BULLISH"),
    (20.0001, "BULLISH"),
    (20.0, "NEUTRAL"),            # raw_bias is NEUTRAL at exactly 20
    (19.9999, "NEUTRAL"),
    (0.0, "NEUTRAL"),
    (-0.0, "NEUTRAL"),
    (-19.9999, "NEUTRAL"),
    (-20.0, "NEUTRAL"),
    (-20.0001, "BEARISH"),
    (-25.0, "BEARISH"),
    (-30.0, "BEARISH"),
    (-30.0001, "BEARISH CONFIRMED"),
    (-100.0, "BEARISH CONFIRMED"),
]


def test_the_label_at_every_boundary():
    wrong = [(score, bias_label(_raw(score), score), label)
             for score, label in _ENGINE_CASES
             if bias_label(_raw(score), score) != label]
    assert not wrong, f"(score, got, expected): {wrong}"


def test_a_score_not_computed_is_neutral():
    # calculate_dynamic_bias gives NEUTRAL for a NaN score (every comparison
    # is False); None is read as 0.0, as the class did.
    assert bias_label("NEUTRAL", float("nan")) == "NEUTRAL"
    assert bias_label("NEUTRAL", None) == "NEUTRAL"


def test_inputs_the_engine_never_produces_are_labelled_as_before():
    # (raw_bias, score, what BiasStateMachine.transition() returned)
    cases = [
        ("BULLISH", 5.0, "NEUTRAL"),        # raw disagrees with a small score
        ("BEARISH", 50.0, "BEARISH"),       # raw disagrees with a large score
        ("BULLISH", -50.0, "BULLISH"),
        ("NEUTRAL", 50.0, "NEUTRAL"),
        ("UNKNOWN", 25.0, "UNKNOWN"),
        ("UNKNOWN", 5.0, "NEUTRAL"),
        (None, 25.0, None),
        ("bullish", 50.0, "bullish"),       # case matters, as it did
        ("BULLISH", float("nan"), "BULLISH"),
        ("BULLISH", None, "NEUTRAL"),
        ("BULLISH", float("inf"), "BULLISH CONFIRMED"),
        ("BEARISH", float("-inf"), "BEARISH CONFIRMED"),
    ]
    wrong = [(r, s, bias_label(r, s), want) for r, s, want in cases
             if bias_label(r, s) != want]
    assert not wrong, f"(raw, score, got, expected): {wrong}"


def test_the_label_has_no_memory():
    # Every ordered pair of a grid: the second label must be what the second
    # input gives on its own, whatever was asked first.
    grid = [(_raw(s), s) for s in
            (-100.0, -30.0001, -30.0, -25.0, -20.0, 0.0, 20.0, 25.0, 30.0,
             30.0001, 100.0)]
    alone = {i: bias_label(*inp) for i, inp in enumerate(grid)}
    changed = []
    for (i, first), (j, second) in itertools.product(enumerate(grid), repeat=2):
        bias_label(*first)
        if bias_label(*second) != alone[j]:
            changed.append((first, second))
    assert not changed, f"a label depended on the one before it: {changed[:5]}"


def _engine_core_tree():
    path = os.path.join(ROOT, "core", "engine_core.py")
    with open(path, encoding="utf-8") as f:
        return ast.parse(f.read())


def test_engine_core_labels_both_series_through_bias_label():
    tree = _engine_core_tree()
    targets = {}
    for node in ast.walk(tree):
        if (isinstance(node, ast.Assign) and isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Name)
                and node.value.func.id == "bias_label"):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    targets[t.id] = [a.id for a in node.value.args
                                     if isinstance(a, ast.Name)]
    assert targets.get("detailed_bias") == ["raw_bias", "bias_score"], targets
    assert targets.get("btc_detailed_bias") == ["btc_raw_bias", "btc_bias_score"], targets


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


def test_bias_engine_has_no_state_machine_class():
    import models.bias_engine as be
    assert not hasattr(be, "BiasStateMachine")
    assert callable(be.bias_label)
