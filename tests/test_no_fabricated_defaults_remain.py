"""
The last fabricated defaults: the simulated order log and the structure
frame.

FOUND 21 SEPTEMBER 2026, by reading the code during the pre-backtest review
(docs/PHASE7_NEXT.md, "Review findings", items 12 and 13). Work order E.

12. live_trading._build_simulated_order recorded an absent zone, stop, target
    set or current price as 0.0, and an absent risk_reason as "OK". Round 6 F3
    removed the same shape from the router and the panel. Its timestamp also
    used datetime.utcnow(), deprecated since Python 3.12 -- the source of the
    suite's two DeprecationWarnings -- after the same call had been fixed
    sixty lines below it on 5 September.

13. structure.calculate_structure copied the analysis into the frame with
    .get("regime", "NEUTRAL STRUCTURE"), .get("hvn", 0.0) and
    .get("lvn", 0.0). Latent -- analyze() always returns the keys -- and the
    0.0 would have been a structural level at a price of zero, read by
    entry_model and trend_health.

Tests that import live_trading skip without pandas_ta, because live_trading
imports the router and the router imports the engine. The parse-tree tests
read files and run everywhere.

Fixture-free, per run_tests.py.
"""

import ast
import datetime
import json
import os
import sys
import warnings

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)


def _tree(relpath):
    with open(os.path.join(REPO, relpath), "rb") as f:
        return ast.parse(f.read().decode("utf-8"))


def _build_order(result):
    pytest.importorskip("pandas_ta")
    from live_trading import LiveTradingSimulator

    # _build_simulated_order reads nothing from self. Called unbound so the
    # test does not construct a SignalRouter it does not need.
    return LiveTradingSimulator._build_simulated_order(None, result)


def _walk_values(obj):
    if isinstance(obj, dict):
        for v in obj.values():
            yield from _walk_values(v)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            yield from _walk_values(v)
    else:
        yield obj


# --- 12: the simulated order ----------------------------------------------

def test_an_order_built_from_an_empty_result_records_nothing_rather_than_zero():
    order = _build_order({"symbol": "TESTUSDT", "timeframe": "4h"})

    # The band's key is ema_band since B10 (15 October 2026); it was
    # entry_zone (tests/test_b10_outputs_agree_with_finding_4_and_the_action.py).
    assert order["ema_band"] == {"lower": None, "upper": None}, order
    assert order["risk"]["atr_stop"] is None, order
    assert order["risk"]["targets"] is None, order
    assert order["current_price"] is None, order
    assert order["risk"]["risk_reason"] is None, (
        "an order with no risk block records risk_reason 'OK' again")
    assert order["risk"]["risk_valid"] is None
    zeros = [v for v in _walk_values(order) if v == 0.0 and not isinstance(v, bool)]
    assert zeros == [], f"the order still invents a zero: {order}"
    json.dumps(order)   # still writable as the log it is


def test_an_order_built_from_a_real_result_carries_its_values():
    """Negative control: the fix records absence, it does not drop values."""
    order = _build_order({
        "symbol": "TESTUSDT", "timeframe": "4h",
        "entry": {"zone_lower": 0.61, "zone_upper": 0.64},
        "risk": {"atr_stop": 0.55, "targets": (0.79, 0.91, 1.03),
                 "risk_valid": False, "risk_reason": "Stop distance too wide."},
        "exit": {"action": "NO-TRADE (RISK TOO HIGH)", "current_price": 0.67},
    })
    assert order["ema_band"] == {"lower": 0.61, "upper": 0.64}
    assert order["risk"]["atr_stop"] == 0.55
    assert tuple(order["risk"]["targets"]) == (0.79, 0.91, 1.03)
    assert order["risk"]["risk_valid"] is False
    assert order["risk"]["risk_reason"] == "Stop distance too wide."
    assert order["current_price"] == 0.67
    assert order["decision"] == "NO-TRADE (RISK TOO HIGH)"


def test_the_order_timestamp_keeps_its_form_and_raises_no_warning():
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        order = _build_order({"symbol": "TESTUSDT", "timeframe": "4h"})
    stamp = datetime.datetime.fromisoformat(order["timestamp"])
    assert stamp.tzinfo is None, (
        "the order timestamp gained a UTC offset; every earlier order log "
        "entry is a naive ISO string")
    now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    assert abs((now - stamp).total_seconds()) < 60, (stamp, now)


def test_no_engine_module_calls_utcnow():
    """
    The class, not the instance. utcnow() was fixed in data_fetcher.py and in
    _log_simulated_trade and survived in _build_simulated_order; this reads
    every engine module's parse tree, so the next copy fails here too.

    25 October 2026 (the list for after the audit, entry 51): the engine is
    the files conftest.all_python_files reads without the documentation
    tooling, which are the files code_hash reads. This walked the tree with a
    list of directories of its own, which skipped five fewer than code_hash's:
    .pytest_cache, env, aider-env, Backup and Claude outputs.
    """
    from conftest import all_python_files

    offenders = []
    for rel in all_python_files(include_doc_tooling=False):
        for node in ast.walk(_tree(rel)):
            if isinstance(node, ast.Attribute) and node.attr == "utcnow":
                offenders.append(f"{rel}:{node.lineno}")
    assert offenders == [], offenders


# --- 13: the structure frame ----------------------------------------------

def defaults_in(tree):
    """`<x>.get(<key>, <default>)` calls in a parse tree, whatever <x> is."""
    return [f"line {node.lineno}: {ast.unparse(node)}" for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "get"
            and len(node.args) >= 2]


def test_calculate_structure_copies_the_analysis_without_defaults():
    """
    Read from the parse tree: no `<x>.get(<key>, <default>)` in
    structure.py. A behavioural test cannot see this -- analyze() always
    returns the keys, which is why the defaults were latent.

    20 OCTOBER 2026 (round 8, run 2, Part 4, shape 1; the list for after the
    audit, entry 37). This read only calls on a name spelled `result`, so the
    same three defaults on the analysis under any other name passed. And
    structure.py has had no `.get` call at all since 21 September, so the
    scan has found nothing to read either way. It reads every `.get` now, it
    asserts that calculate_structure is in the file it reads, and the control
    below shows that it can fail.
    """
    tree = _tree(os.path.join("structure", "structure.py"))
    functions = {node.name for node in ast.walk(tree)
                 if isinstance(node, ast.FunctionDef)}
    assert "calculate_structure" in functions, (
        "calculate_structure is not in structure/structure.py, the file this reads")
    defaults = defaults_in(tree)
    assert defaults == [], defaults


def test_the_default_scan_can_report_a_violation():
    """
    Negative control. The scan above passes on a clean tree, and would pass as
    well if it matched nothing. Fed the three lines of 21 September as they
    were, it reports all three; fed the same default on another name, it
    reports it; fed the direct reads that replaced them, it reports nothing.
    """
    pre_fix = (
        'df_clean.loc[:, "STRUCTURE"] = result.get("regime", "NEUTRAL STRUCTURE")\n'
        'df_clean.loc[:, "HVN"] = result.get("hvn", 0.0)\n'
        'df_clean.loc[:, "LVN"] = result.get("lvn", 0.0)\n'
    )
    assert len(defaults_in(ast.parse(pre_fix))) == 3
    # Not seen before 20 October 2026.
    assert len(defaults_in(ast.parse('df_clean.loc[:, "HVN"] = analysis.get("hvn", 0.0)\n'))) == 1
    assert len(defaults_in(ast.parse('hvn = engine.analyze(df).get("hvn", 0.0)\n'))) == 1
    # Not a default.
    assert defaults_in(ast.parse('df_clean.loc[:, "HVN"] = result["hvn"]\n')) == []
    assert defaults_in(ast.parse('hvn = result.get("hvn")\n')) == []


def test_the_structure_columns_carry_the_analysis_values():
    """
    Behavioural half, and the control that indexing directly still copies the
    real values into the frame. No pandas_ta needed: structure uses the
    volume profile, not the indicators.
    """
    import numpy as np
    import pandas as pd

    from structure.structure import calculate_structure

    n = 120
    close = 100.0 + np.sin(np.arange(n) / 5.0) * 5.0 + np.arange(n) * 0.1
    df = pd.DataFrame({
        "open": close, "high": close * 1.01, "low": close * 0.99,
        "close": close, "volume": np.full(n, 1000.0),
    })
    result = calculate_structure(df)
    frame = result["df"]

    assert (frame["STRUCTURE"] == result["regime"]).all()
    for col, key in (("HVN", "hvn"), ("LVN", "lvn")):
        value = result[key]
        assert np.isfinite(value) and value > 0, (key, value)
        assert (frame[col] == value).all(), (col, value)
