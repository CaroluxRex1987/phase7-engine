"""
Audit findings (c) and (d) — 5 September 2026.

Two defects that share nothing except being invisible until the day they
are not.

FINDING (c) — data/data_fetcher.py

    requests.get(url, params=params)          no timeout at all
    df = pd.DataFrame(data, columns=[...])    outside the try

`requests` defaults its timeout to None, which means wait forever. A server
that accepts the connection and then sends nothing hangs the run with no
error and no log line.

And the try around the network call ended before the frame was built, so a
response that IS a list but is wrong in any other way — a different number of
fields, a null price, a non-numeric string — raised out of fetch_ohlc
uncaught. Every other failure in this class returns {"error": ...}. These
escaped that contract.

FINDING (d) — live_trading.py

    live_trading_simulator = LiveTradingSimulator()   at module scope
    os.makedirs(self.log_dir, exist_ok=True)          in __init__

Importing the module created a directory. tests/test_imports.py imports every
engine module, so running the suite created logs/LiveSim/ on any machine that
ran it. config.py already states the rule: directories are created on demand
by the code that writes into them.
"""

import ast
import io
import os
import sys

import pytest

from conftest import REPO_ROOT

FETCHER = os.path.join(REPO_ROOT, "data", "data_fetcher.py")
LIVE_TRADING = os.path.join(REPO_ROOT, "live_trading.py")


def _tree(path):
    with io.open(path, encoding="utf-8", newline="") as f:
        return ast.parse(f.read())


def _function(tree, name):
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return node
    raise AssertionError(f"{name} not found")


# ============================================================
# (c) the request cannot hang forever
# ============================================================

def test_every_requests_call_passes_a_timeout():
    """
    Source-level, because the behavioural version of this test is a server
    that accepts a connection and never answers — and the assertion is that
    the test does not hang, which a test cannot make.
    """
    tree = _tree(FETCHER)
    offenders = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not (isinstance(func, ast.Attribute)
                and isinstance(func.value, ast.Name)
                and func.value.id == "requests"):
            continue
        if not any(kw.arg == "timeout" for kw in node.keywords):
            offenders.append(f"requests.{func.attr} at line {node.lineno}")

    assert not offenders, (
        "requests call with no timeout in data_fetcher.py: "
        + ", ".join(offenders) + "\n\n"
        "requests defaults to None, which means wait forever. A server that "
        "accepts the connection and then sends nothing hangs the run with no "
        "error and no log line. Pass timeout=config.API_TIMEOUT_SECONDS."
    )


def test_the_timeout_is_a_declared_setting_not_a_literal():
    """
    A hardcoded 15 would be a second setting: invisible in config.py, and in
    force exactly when someone tries to change the real one. Same defect
    test_explicit_configuration guards for LOG_DIR.
    """
    from core import config

    assert isinstance(config.API_TIMEOUT_SECONDS, (int, float)), (
        f"config.API_TIMEOUT_SECONDS is {config.API_TIMEOUT_SECONDS!r}"
    )
    assert config.API_TIMEOUT_SECONDS > 0, (
        "a timeout of zero or less is not a timeout"
    )

    with io.open(FETCHER, encoding="utf-8", newline="") as f:
        code = "\n".join(l.split("#", 1)[0] for l in f.read().splitlines())

    assert "config.API_TIMEOUT_SECONDS" in code, (
        "data_fetcher.py does not read config.API_TIMEOUT_SECONDS, so the "
        "declared setting is not the one in force."
    )


# ============================================================
# (c) a malformed response is reported, not raised
# ============================================================

class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


MALFORMED = {
    "wrong field count": [[1, 2, 3]] * 5,
    "null price": [[1700000000000, "1.0", "2.0", None, "1.5", "10", 1700000000001, "9"]] * 5,
    "price is a word": [[1700000000000, "1.0", "2.0", "0.5", "later", "10", 1700000000001, "9"]] * 5,
    "timestamp out of range": [["not-a-time", "1.0", "2.0", "0.5", "1.5", "10", 1, "9"]] * 5,
    "rows are not lists": [1, 2, 3, 4, 5],
}


@pytest.mark.parametrize("label", sorted(MALFORMED))
def test_a_malformed_response_returns_an_error_rather_than_raising(label, monkeypatch):
    """
    The half of finding (c) that IS behavioural. Each payload is a non-empty
    list, so it survives the shape check, and is wrong in a different way
    underneath it.
    """
    import data.data_fetcher as fetcher_module

    monkeypatch.setattr(fetcher_module.requests, "get",
                        lambda *a, **k: _FakeResponse(MALFORMED[label]))

    try:
        out = fetcher_module.DataFetcher().fetch_ohlc("TESTUSDT", "4h", limit=5)
    except Exception as e:
        pytest.fail(
            f"a {label} response raised out of fetch_ohlc: "
            f"{type(e).__name__}: {e}\n\n"
            "Every other data defect in this method returns {'error': ...}, "
            "which get_tf and the engine know how to report. An exception "
            "here surfaces as whatever stage happened to be running."
        )

    assert isinstance(out, dict) and "error" in out, (
        f"a {label} response returned {type(out).__name__} rather than an "
        f"error dict — it was accepted as market data."
    )


def test_a_well_formed_response_still_becomes_a_frame(monkeypatch):
    """
    The negative control for the test above: wrapping the frame construction
    in a try must not turn a GOOD response into an error dict. Without this,
    `return {"error": ...}` unconditionally would pass every test above.
    """
    import pandas as pd

    import data.data_fetcher as fetcher_module

    base = 1700000000000
    step = 4 * 60 * 60 * 1000
    rows = [[base + i * step, "1.00", "1.10", "0.90", "1.05", "100",
             base + (i + 1) * step - 1, "105"] for i in range(60)]

    monkeypatch.setattr(fetcher_module.requests, "get",
                        lambda *a, **k: _FakeResponse(rows))
    # validate_ohlcv checks staleness against a reference clock, and these
    # candles are fixed in the past. The frame is what this test is about.
    monkeypatch.setattr(fetcher_module, "validate_ohlcv", lambda *a, **k: None)

    out = fetcher_module.DataFetcher().fetch_ohlc("TESTUSDT", "4h", limit=60)

    assert isinstance(out, pd.DataFrame), f"got {type(out).__name__}: {out!r}"
    assert len(out) == 60
    assert list(out.columns) == ["open", "high", "low", "close", "volume"]
    assert out["close"].dtype.kind == "f", (
        f"close is {out['close'].dtype}, not a float — the conversion inside "
        f"the try did not run"
    )


# ============================================================
# (d) importing a module does not touch the disk
# ============================================================

def test_importing_live_trading_creates_no_directory(tmp_path, monkeypatch):
    """
    Imported into a process where LOG_DIR points somewhere empty. Nothing may
    appear there.
    """
    from core import config

    target = tmp_path / "logdir"
    monkeypatch.setattr(config, "LOG_DIR", str(target) + os.sep)

    for name in [m for m in list(sys.modules) if m == "live_trading"]:
        del sys.modules[name]

    import live_trading  # noqa: F401

    assert not target.exists(), (
        f"importing live_trading created {target}. config.py's own rule is "
        f"that directories are created on demand by the code that writes "
        f"into them. The test suite imports every engine module, so an "
        f"import-time makedirs means running pytest writes to disk."
    )


def test_live_trading_has_no_module_level_instance():
    """
    The construction, not just the makedirs. A module-scope instance also
    builds a SignalRouter at import.
    """
    tree = _tree(LIVE_TRADING)

    offenders = []
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        value = node.value
        if isinstance(value, ast.Call) and isinstance(value.func, ast.Name):
            if value.func.id.endswith("Simulator"):
                offenders.append(f"line {node.lineno}: {value.func.id}()")

    assert not offenders, (
        "live_trading.py constructs a simulator at module scope: "
        + ", ".join(offenders) + "\n\n"
        "That runs on import — makedirs, plus a SignalRouter. Use "
        "get_live_trading_simulator(), which pays for it when asked."
    )


def test_the_accessor_returns_one_shared_instance():
    """
    What replaced the singleton still has to behave like one for a caller
    that wants that, or the deletion traded a side effect for a bug.
    """
    # Constructing the simulator builds a SignalRouter, whose __init__
    # imports core.engine_core, which needs pandas_ta. Importing the
    # MODULE does not -- that is the point of the test above.
    pytest.importorskip("pandas_ta",
                        reason="LiveTradingSimulator() constructs a "
                               "SignalRouter, which imports engine_core")
    import live_trading

    live_trading._simulator = None
    try:
        a = live_trading.get_live_trading_simulator()
        b = live_trading.get_live_trading_simulator()
        assert a is b, "the accessor built two simulators"
    finally:
        live_trading._simulator = None


def test_the_simulator_still_creates_its_directory_when_it_writes(tmp_path):
    """
    Moving the makedirs must not mean the write fails on a fresh machine.
    """
    # Constructing the simulator builds a SignalRouter, whose __init__
    # imports core.engine_core, which needs pandas_ta. Importing the
    # MODULE does not -- that is the point of the test above.
    pytest.importorskip("pandas_ta",
                        reason="LiveTradingSimulator() constructs a "
                               "SignalRouter, which imports engine_core")
    import live_trading

    target = tmp_path / "sim" / "nested"
    sim = live_trading.LiveTradingSimulator(log_dir=str(target))

    assert not target.exists(), "constructing the simulator created the directory"

    path = sim._log_simulated_trade({"action": "NO-TRADE", "symbol": "TESTUSDT"})

    assert os.path.isfile(path), f"nothing written at {path}"
    assert target.exists(), "the directory was still not created at write time"
