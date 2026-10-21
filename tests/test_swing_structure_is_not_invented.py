"""
Kimi Finding 5, item 6 — 6 September 2026.

THE FINDING

`StructureEngine._detect_swing_structure` returned `current_price` on every
path where it had not located a swing:

    if df is None or len(df) < (2 * lookback + 5):
        return float(current_price)
    ...
    if not swing_highs and not swing_lows:
        return float(current_price)

The price the engine is being asked about, handed back as the structural
level it failed to find. On the panel that is "SWING STRUCT : $<price>" —
a located level sitting exactly on the current price, which is the strongest
statement that field can make, made on the runs that located nothing.

WHY IT IS REACHABLE AND NOT MERELY LATENT

The guard needs `2 * lookback + 5` rows — 21 at the default
`config.STRUCT_LOOKBACK` of 8. `engine_core._validate_dataframe` admits any
frame of 20 rows or more. A 20-row frame therefore passed validation, ran the
whole pipeline, and got its own price back as structure. One row wide, and on
the near side of the engine's own minimum.

THE SECOND HALF, ON THE SAME FIELD

`signal_router._build_decision_object` assembled the same field as

    float(structure.get("swing_struct", exit_data.get("current_price", 0.0)))

so a structure block carrying no swing level got the current price written in
as one — into the panel and into the permanent decision-log record. That is
reachable by the composition GLM F-7 named: `_validate_engine_output` checks
that "structure" is PRESENT and never what is under it, so an engine output
whose structure block is `{}` passes validation and arrives here.

This is the third time this field has been fixed at a consumer while the
producer went on inventing: entry_model on 1 September, panel_render on
2 September, and this module's own header describes the pattern as closing
the door and leaving the window.

WHAT THESE TESTS HOLD

That neither end invents a level; that the run is NOT marked degraded for it,
which is a decision and not an oversight (see the docstring in
`_detect_swing_structure`); and — the negative controls, named as such — that
a swing which CAN be located is still returned, at both ends. A producer that
returned NaN unconditionally would satisfy every "does not invent" test in
this file and destroy the field.
"""

import ast
import json
import math
import os

import pandas as pd
import pytest

from conftest import REPO_ROOT

from core import config
from structure.structure import StructureEngine


LOOKBACK = config.STRUCT_LOOKBACK          # 8
MIN_ROWS_FOR_A_SWING = 2 * LOOKBACK + 5    # 21
ENGINE_MINIMUM_ROWS = 20                   # engine_core._validate_dataframe

CURRENT_PRICE = 100.0


def _flat(rows, price=CURRENT_PRICE):
    """A flat frame. Every bar ties, so pivots ARE confirmable on it."""
    return pd.DataFrame({
        "open": [price] * rows,
        "high": [price * 1.01] * rows,
        "low": [price * 0.99] * rows,
        "close": [price] * rows,
        "volume": [1000.0] * rows,
    })


def _ramp(rows, price=CURRENT_PRICE):
    """
    Strictly increasing. No bar is the extreme of a window that extends to its
    right, so nothing is ever confirmed — the "no swings found" path, on a
    frame long enough to pass the length guard.
    """
    closes = [price + i for i in range(rows)]
    return pd.DataFrame({
        "open": closes,
        "high": [c * 1.01 for c in closes],
        "low": [c * 0.99 for c in closes],
        "close": closes,
        "volume": [1000.0] * rows,
    })


def _peak(rows=61, price=CURRENT_PRICE):
    """Up then down: a real, confirmable swing high in the middle."""
    half = rows // 2
    closes = [price + i for i in range(half)] + [price + half - i for i in range(rows - half)]
    return pd.DataFrame({
        "open": closes,
        "high": [c * 1.01 for c in closes],
        "low": [c * 0.99 for c in closes],
        "close": closes,
        "volume": [1000.0] * rows,
    })


def _swing(df, current_price=CURRENT_PRICE):
    return StructureEngine()._detect_swing_structure(df, current_price, lookback=LOOKBACK)


# ======================================================================
# 1. The producer — an unlocated level is not the current price
# ======================================================================

def test_the_reachable_window_between_the_two_minimums_still_exists():
    """
    The finding is arithmetic before it is behaviour: the detector needs one
    more row than the engine demands. If either number moves this fires, which
    is the point — the tests below choose 20 rows because of these two
    constants and would otherwise be testing an arbitrary length.
    """
    assert MIN_ROWS_FOR_A_SWING > ENGINE_MINIMUM_ROWS, (
        f"the detector needs {MIN_ROWS_FOR_A_SWING} rows and the engine "
        f"admits {ENGINE_MINIMUM_ROWS}; if that gap has closed this test is "
        f"stale and the ones below test nothing in particular"
    )

    source = open(os.path.join(REPO_ROOT, "core", "engine_core.py"),
                  encoding="utf-8").read()
    assert f"if len(df) < {ENGINE_MINIMUM_ROWS}:" in source, (
        "engine_core._validate_dataframe no longer rejects frames below "
        f"{ENGINE_MINIMUM_ROWS} rows in the form this test reads; the gap "
        "above is asserted against a number that is no longer there"
    )


def test_a_twenty_row_frame_does_not_get_its_own_price_back():
    """The reachable case, exactly: one row short of what the detector needs."""
    out = _swing(_flat(ENGINE_MINIMUM_ROWS))

    assert not math.isfinite(out), (
        f"a {ENGINE_MINIMUM_ROWS}-row frame — which the engine accepts — was "
        f"given {out!r} as its structural level; the current price was "
        f"{CURRENT_PRICE!r}"
    )


def test_a_much_shorter_frame_does_not_get_its_own_price_back():
    assert not math.isfinite(_swing(_flat(5)))


def test_a_missing_frame_does_not_get_a_price_back():
    assert not math.isfinite(_swing(None))


def test_a_frame_with_no_confirmable_swings_does_not_get_its_own_price_back():
    """
    The second invented-level path, and it is not about length: this frame is
    60 rows and passes every guard. Nothing in it can be confirmed as a pivot,
    so the answer is still "not located".
    """
    df = _ramp(60)
    out = _swing(df, current_price=float(df["close"].iloc[-1]))

    assert not math.isfinite(out), (
        f"a frame with no confirmable swing got {out!r} as its structural level"
    )


def test_negative_control_a_locatable_swing_is_still_returned():
    """
    MUST PASS BOTH BEFORE AND AFTER THE FIX.

    Without this, a detector rewritten to return NaN unconditionally would
    satisfy every test above and delete the field.
    """
    df = _peak()
    out = _swing(df, current_price=float(df["close"].iloc[-1]))

    assert math.isfinite(out), "a confirmable swing was not returned"
    levels = set(df["high"].tolist()) | set(df["low"].tolist())
    assert out in levels, (
        f"the returned level {out!r} is not a bar high or low in the frame"
    )


# ======================================================================
# 2. Through analyze() — reported, and deliberately not degrading
# ======================================================================

def test_analyze_reports_the_absent_level_rather_than_a_price():
    out = StructureEngine().analyze(_flat(ENGINE_MINIMUM_ROWS),
                                    current_price=CURRENT_PRICE)

    assert not math.isfinite(out["swing_struct"]), (
        f"analyze() handed back {out['swing_struct']!r} as swing_struct on a "
        f"frame too short to locate one"
    )


def test_the_absent_level_does_not_mark_the_run_degraded():
    """
    A DECISION, recorded here so it is visible if someone changes it.

    Not-enough-data is an ordinary return in this module — _detect_regime
    under 15 rows, _detect_sequence under 6*lookback+10 — and degraded_inputs
    feeds engine_core's run degradation list, which drives the confidence
    ceiling and the final action. swing_struct reaches nothing but the panel
    and the decision record, so it must not be able to move an authorization.
    The absence is reported where the field is read, not by degrading the run.
    """
    out = StructureEngine().analyze(_flat(ENGINE_MINIMUM_ROWS),
                                    current_price=CURRENT_PRICE)

    assert out["degraded_inputs"] == [], (
        f"an unlocated swing level degraded the run: {out['degraded_inputs']!r}"
    )


def test_negative_control_analyze_still_locates_a_level_on_a_normal_frame():
    """
    MUST PASS BOTH BEFORE AND AFTER THE FIX. This is the path the golden
    snapshot runs down; if it stopped locating levels the snapshot would move.
    """
    out = StructureEngine().analyze(_flat(60), current_price=CURRENT_PRICE)

    assert math.isfinite(out["swing_struct"]), (
        "a 60-row frame with confirmable pivots reported no swing level"
    )


def test_the_panel_says_not_located_for_a_frame_that_located_nothing():
    """
    Producer to panel, in one test. The panel's own NaN handling is held by
    tests/test_structure_fallbacks.py; what this adds is that the value the
    producer now returns is the value that handling expects.
    """
    from core.panel_render import render_panel

    fixture = os.path.join(REPO_ROOT, "tests", "fixtures", "golden_decision.json")
    if not os.path.exists(fixture):
        pytest.skip("golden fixture not present")

    with open(fixture, encoding="utf-8") as fh:
        decision = json.load(fh)

    produced = StructureEngine().analyze(_flat(ENGINE_MINIMUM_ROWS),
                                         current_price=CURRENT_PRICE)
    decision["structure"]["swing_struct"] = produced["swing_struct"]
    panel = render_panel(decision)

    assert "SWING STRUCT  : not located this run" in panel, (
        "the panel drew a level for a run that located none"
    )
    assert f"${CURRENT_PRICE:.4f}" not in panel.split("SWING STRUCT")[1][:60], (
        "the current price was printed on the swing line"
    )


# ======================================================================
# 3. The router — the same fabrication, one assembly later
# ======================================================================

# 13 OCTOBER 2026, the fallback sweep (DECISIONS, "Ruling, 13 October 2026
# -- the fallback sweep"): the router reads these five directly now, where
# it used to default each to False when absent. They are supplied here with
# exactly those values, so the record these tests read is the one they read
# before. False beside an absent blocker list is still "not computed" to the
# decision model's signal gate, as an absent signal was.
ROUTER_READS_TREND = {"trend_exhaustion": False, "momentum_divergence": False}
ROUTER_READS_ENTRY = {"long_signal": False, "short_signal": False,
                      "score_clipped": False}


def _decision(structure, current_price=1.0):
    from models import signal_router as sr

    return sr.SignalRouter(engine_core=object())._build_decision_object(
        symbol="AEROUSDT", timeframe="4h",
        bias={}, trend=dict(ROUTER_READS_TREND), structure=structure,
        entry=dict(ROUTER_READS_ENTRY),
        risk={"risk_valid": True, "risk_reason": "OK"},
        exit_data={"current_price": current_price},
        degradation=[], provenance={}, lineage_record={}, exit_watch=[],
        btc_context={"available": False}, macro_bias="NEUTRAL",
        chart_path=None,
    )


def test_a_structure_block_with_no_swing_level_does_not_become_the_price():
    """
    Reachable by the F-7 composition: _validate_engine_output checks that
    "structure" is present, not what is under it, so `{}` gets here.

    No monkeypatch fixture, deliberately: every render_panel call in this
    module is inside route_and_execute, so _build_decision_object needs
    nothing silenced -- and run_tests.py, the runner that works without
    pytest, calls test functions with no arguments and reports any that take
    a fixture as an error. Two fewer of those.
    """
    recorded = _decision({}, current_price=1.0)["structure"]["swing_struct"]

    assert not math.isfinite(recorded), (
        f"the decision log's permanent record of a run with no swing level "
        f"says {recorded!r}; the current price was 1.0"
    )


def test_negative_control_a_located_level_still_reaches_the_record():
    """MUST PASS BOTH BEFORE AND AFTER THE FIX."""
    recorded = _decision({"swing_struct": 0.5}, current_price=1.0)["structure"]["swing_struct"]

    assert recorded == 0.5, (
        f"a located swing level was not passed through: {recorded!r}"
    )


# ======================================================================
# 4. Source guards — the defaults must not come back
#
# Matched on the parse tree rather than on text (rule 16): a reintroduction
# spelled differently would slip past a substring search, and the explanatory
# comments in both files quote the old expressions verbatim, which a
# substring search would also read as the defect.
# ======================================================================

def _tree(*parts):
    path = os.path.join(REPO_ROOT, *parts)
    return ast.parse(open(path, encoding="utf-8").read())


def _names_read(node):
    """Every name an expression reads, an attribute's own name included."""
    return ({n.id for n in ast.walk(node) if isinstance(n, ast.Name)}
            | {n.attr for n in ast.walk(node) if isinstance(n, ast.Attribute)})


def _names_bound(target):
    """The local names an assignment target binds: a name, the names in a
    tuple or a list, the container a subscript writes into. An attribute's
    owner is not bound -- `self.level = price` binds no local."""
    if isinstance(target, ast.Name):
        return {target.id}
    if isinstance(target, (ast.Tuple, ast.List)):
        return set().union(*(_names_bound(e) for e in target.elts))
    if isinstance(target, (ast.Starred, ast.Subscript)):
        return _names_bound(target.value)
    return set()


def returns_built_from(fn, name):
    """
    The return expressions in `fn` built from `name`: naming it, or naming a
    local assigned from it at any remove -- `level = current_price` and then
    `return float(level)`. Comparing against it is not building from it:
    _detect_swing_structure reads the price to choose the nearer of two
    located levels, and returns the level.
    """
    bindings = []
    for node in ast.walk(fn):
        if isinstance(node, ast.Assign):
            bindings.append((node.targets, node.value))
        elif isinstance(node, (ast.AugAssign, ast.AnnAssign, ast.NamedExpr)):
            if node.value is not None:
                bindings.append(([node.target], node.value))
        elif isinstance(node, (ast.For, ast.comprehension)):
            bindings.append(([node.target], node.iter))

    built = {name}
    grew = True
    while grew:
        grew = False
        for targets, value in bindings:
            if _names_read(value) & built:
                for target in targets:
                    new = _names_bound(target) - built
                    if new:
                        built |= new
                        grew = True

    return [ast.unparse(n.value) for n in ast.walk(fn)
            if isinstance(n, ast.Return) and n.value is not None
            and _names_read(n.value) & built]


def test_the_producer_returns_no_expression_built_from_the_current_price():
    """
    20 OCTOBER 2026 (round 8, run 2, Part 4, shape 1; the list for after the
    audit, entry 37). This matched "current_price" in the text of each return
    expression, so `level = current_price` followed by `return float(level)`
    -- the defect spelled differently, which the comment above this section
    says the parse tree is read to catch -- passed. Returns built from the
    price through a local are read now, the scan must find a return to read,
    and the control below shows that it can fail.
    """
    tree = _tree("structure", "structure.py")

    fn = [n for n in ast.walk(tree)
          if isinstance(n, ast.FunctionDef) and n.name == "_detect_swing_structure"]
    assert len(fn) == 1, f"expected one _detect_swing_structure, found {len(fn)}"

    returns = [n for n in ast.walk(fn[0])
               if isinstance(n, ast.Return) and n.value is not None]
    assert returns, "_detect_swing_structure has no return for the scan to read"

    offenders = returns_built_from(fn[0], "current_price")

    assert not offenders, (
        f"_detect_swing_structure returns the current price again: {offenders!r}"
    )


def test_negative_control_the_return_scan_can_report_a_violation():
    """
    The scan above passes on a clean tree, and would pass as well if it
    matched nothing. Fed the return of 6 September and the same return through
    a local, it reports both; fed _detect_swing_structure's own use of the
    price, and a NaN, it reports nothing.
    """
    def scan(*body):
        source = "def f(df, current_price):\n" + "".join(f"    {line}\n" for line in body)
        return returns_built_from(ast.parse(source).body[0], "current_price")

    assert scan("return float(current_price)") == ["float(current_price)"]
    assert scan("return float(self.current_price)") == ["float(self.current_price)"]
    # Not seen before 20 October 2026.
    assert scan("level = current_price", "return float(level)") == ["float(level)"]
    assert scan("level = float(current_price)", "out = level", "return out") == ["out"]
    assert scan("level, n = current_price, 0", "return level") == ["level"]
    # Not built from the price.
    assert scan("high, low = 2.0, 1.0",
                "if abs(high - current_price) <= abs(low - current_price):",
                "    return float(high)",
                "return float(low)") == []
    assert scan('return float("nan")') == []


def test_the_router_assembles_the_field_with_no_price_shaped_default():
    tree = _tree("models", "signal_router.py")

    values = [ast.unparse(value)
              for node in ast.walk(tree) if isinstance(node, ast.Dict)
              for key, value in zip(node.keys, node.values)
              if isinstance(key, ast.Constant) and key.value == "swing_struct"]

    assert values, "no swing_struct assembly found in signal_router.py"
    for expr in values:
        assert "current_price" not in expr, (
            f"the swing_struct default is built from the current price again: {expr}"
        )
        assert "0.0" not in expr, (
            f"the swing_struct default is a finite price again: {expr}"
        )
