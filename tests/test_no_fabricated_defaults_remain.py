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

    assert order["entry_zone"] == {"lower": None, "upper": None}, order
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
    assert order["entry_zone"] == {"lower": 0.61, "upper": 0.64}
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
    """
    offenders = []
    for dirpath, dirnames, filenames in os.walk(REPO):
        dirnames[:] = [d for d in dirnames
                       if d not in {".git", "__pycache__", "tests", "docs",
                                    "logs", "Logs", ".venv", "venv"}]
        for name in filenames:
            if not name.endswith(".py"):
                continue
            rel = os.path.relpath(os.path.join(dirpath, name), REPO)
            for node in ast.walk(_tree(rel)):
                if isinstance(node, ast.Attribute) and node.attr == "utcnow":
                    offenders.append(f"{rel}:{node.lineno}")
    assert offenders == [], offenders


# --- 13: the structure frame ----------------------------------------------

def test_calculate_structure_copies_the_analysis_without_defaults():
    """
    Read from the parse tree: no `result.get(<key>, <default>)` in
    structure.py. A behavioural test cannot see this -- analyze() always
    returns the keys, which is why the defaults were latent.
    """
    defaults = []
    for node in ast.walk(_tree(os.path.join("structure", "structure.py"))):
        if (isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "get"
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "result"
                and len(node.args) >= 2):
            defaults.append(f"line {node.lineno}: {ast.unparse(node)}")
    assert defaults == [], defaults


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
