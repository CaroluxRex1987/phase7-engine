"""
Sequence item 14 — T2-4, explicit configuration.

THE PRINCIPLE

A constant in config.py is a promise that changing it changes the engine. Every
one that nothing reads breaks that promise, and breaks it silently: the reader
edits the number, runs the engine, and gets the same answer with no error and
no sign of why.

WHAT WAS FOUND

Sixteen of the twenty-eight constants in config.py were read by nothing.

    EMA_FAST, EMA_SLOW           indicators.py hardcoded 20 and 50
    RSI_LENGTH, ADX_LENGTH,      hardcoded 14, on both the primary and
    ATR_LENGTH                   the fallback path
    VWMA_LENGTH                  hardcoded 20
    VOLUME_PROFILE_BINS          StructureEngine() took its own default of 50
    CHART_WIDTH, CHART_HEIGHT,   plotting.py hardcoded (14, 8), 200 and
    CHART_DPI, CHART_STYLE       "dark_background"
    BB_LENGTH, BB_STD,           indicators deleted at sequence item 5a
    KAMA_LENGTH
    API_KEY, API_SECRET          no code path can use a credential
    TRADE_LOG_DIR, REQUIRED_DIRS read only by each other

Every value matched what the code hardcoded, with two exceptions:
CHART_HEIGHT said 10 where the renderer used 8, and CHART_DPI said 150 where it
used 200. Those two were corrected in config rather than in the renderer —
every chart produced so far came out at 14x8 and 200 dpi, and quietly resizing
them is a visible change nobody asked for.

THE ONE THAT MATTERED

core/decision_log.py's FINGERPRINTED_CONFIG named seven of the unread constants
as "the knobs that change the numbers", and the decision log recorded them on
every run as part of a run's identity. Changing any of them changed nothing.

That is the item 12 defect — an audit record asserting something untrue — sitting
inside the file item 12 added to fix it. It is closed the same way item 12 was:
by making the claim true rather than by deleting it.

WHY MOST OF THIS TEST READS SOURCE

The engine cannot tell you that a constant is unread; it produces the same
number either way. That is the whole failure mode, so the check has to be
static. The behavioural tests below cover the part that can be observed: change
a setting, and the engine must change with it.
"""

import ast
import os
import pytest
import re

from conftest import REPO_ROOT

CONFIG_PATH = os.path.join(REPO_ROOT, "core", "config.py")

# Read by the test suite rather than the engine. Declared here so the "is it
# read" scan can say so out loud instead of the exception living silently in a
# skip list.
TEST_ONLY = set()

# Values whose only job is to be recorded, not to steer a calculation.
NOT_A_KNOB = {"engine_version"}


def _engine_available():
    try:
        import pandas_ta  # noqa: F401
        return True
    except Exception:
        return False


def _config_constants():
    """Every module-level name config.py binds, in declaration order."""
    with open(CONFIG_PATH, encoding="utf-8") as f:
        tree = ast.parse(f.read())
    names = []
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    names.append(t.id)
    return names


def _engine_sources():
    """Every .py file in the engine except config.py itself and the tests."""
    from conftest import all_python_files
    out = []
    for rel in all_python_files(include_doc_tooling=False):
        if rel.replace("\\", "/") == "core/config.py":
            continue
        with open(os.path.join(REPO_ROOT, rel), encoding="utf-8") as f:
            # Comments stripped: this file and several others NAME the removed
            # constants in explanatory comments, and a scan that counts those
            # as reads would pass on an engine that reads none of them.
            code = "\n".join(l.split("#", 1)[0] for l in f.read().splitlines())
        out.append((rel, code))
    return out


# ============================================================
# Every setting is a setting
# ============================================================

def test_every_config_constant_is_read_by_the_engine():
    sources = _engine_sources()
    unread = []

    for name in _config_constants():
        if name in TEST_ONLY:
            continue
        if not any(re.search(r"\b" + re.escape(name) + r"\b", code)
                   for _, code in sources):
            unread.append(name)

    assert not unread, (
        "config.py declares constants no engine module reads: "
        + ", ".join(unread)
        + "\n\nA constant nothing reads is a promise that editing it changes "
          "the engine, and it does not. Either wire it to the calculation it "
          "names, or delete it — sixteen of these were found at sequence item "
          "14 and seven of them were being recorded in the decision log as "
          "part of a run's identity."
    )


def test_no_module_supplies_a_fallback_for_a_config_value():
    """
    `getattr(config, "LOG_DIR", "Logs/")` is a second setting: undeclared,
    invisible in config.py, and it takes effect exactly when the real one goes
    missing — so a deleted or misspelled entry relocates the engine's output
    silently instead of failing where someone would see it.

    Note the default that survives: decision_log.config_snapshot uses a
    three-argument getattr on purpose, to RECORD a missing name rather than
    omit it. It is excluded by name below, not by shape, so a new shadow
    default cannot hide behind the exemption.
    """
    offenders = []

    for rel, code in _engine_sources():
        try:
            tree = ast.parse(code)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Name)
                    and node.func.id == "getattr"
                    and len(node.args) == 3
                    and isinstance(node.args[0], ast.Name)
                    and node.args[0].id in ("config", "cfg")):
                if isinstance(node.args[1], ast.Constant):
                    label = f"{rel}: getattr(config, {node.args[1].value!r}, ...)"
                else:
                    label = f"{rel}: getattr(config, <computed>, ...)"
                offenders.append(label)

    allowed = {"core/decision_log.py: getattr(config, <computed>, ...)"}
    offenders = [o for o in offenders if o.replace("\\", "/") not in allowed]

    assert not offenders, (
        "modules supply their own default for a config value:\n  "
        + "\n  ".join(offenders)
        + "\n\nRead config.<NAME> directly. A missing setting should stop the "
          "engine at the line that needed it, not quietly substitute a value "
          "that appears in no configuration file."
    )


# ============================================================
# The decision log's claim about itself
# ============================================================

def test_every_fingerprinted_name_exists_and_is_read():
    """
    FINGERPRINTED_CONFIG calls itself "the knobs that change what the engine
    computes", and the decision log records it as part of a run's identity.

    At sequence item 12 seven of the thirteen names were read by nothing. A
    reader diffing two records would have concluded the runs used different
    settings when the settings could not reach the calculation at all.
    """
    from core.decision_log import FINGERPRINTED_CONFIG
    from core import config

    declared = set(_config_constants())
    sources = _engine_sources()

    missing = [n for n in FINGERPRINTED_CONFIG if not hasattr(config, n)]
    assert not missing, (
        "FINGERPRINTED_CONFIG names constants config.py does not define: "
        + ", ".join(missing)
    )

    not_in_config_py = [n for n in FINGERPRINTED_CONFIG if n not in declared]
    assert not not_in_config_py, (
        "FINGERPRINTED_CONFIG names values that are not module-level constants "
        "of config.py: " + ", ".join(not_in_config_py)
    )

    unread = [n for n in FINGERPRINTED_CONFIG
              if n not in NOT_A_KNOB
              and not any(re.search(r"\b" + re.escape(n) + r"\b", code)
                          for _, code in sources)]

    assert not unread, (
        "the decision log fingerprints settings nothing reads: "
        + ", ".join(unread)
        + "\n\nThe record would say these determined the run. Changing them "
          "determines nothing. That is an audit trail asserting something "
          "untrue, which is the defect sequence item 12 exists to close."
    )


def test_a_missing_fingerprinted_name_is_recorded_not_dropped():
    """
    The snapshot used to skip names config did not define. A record that
    silently omits a knob looks complete and is not: nothing distinguishes a
    setting that was missing from one that was never fingerprinted.
    """
    from core import config, decision_log

    class Stub:
        pass

    stub = Stub()
    for name in decision_log.FINGERPRINTED_CONFIG[:-1]:
        setattr(stub, name, getattr(config, name))
    absent = decision_log.FINGERPRINTED_CONFIG[-1]

    snapshot = decision_log.config_snapshot(stub)

    assert absent in snapshot, (
        f"{absent} is missing from config and the snapshot dropped it rather "
        f"than recording that it was absent"
    )
    assert snapshot[absent] == decision_log.MISSING


# ============================================================
# Paths
# ============================================================

def test_the_log_directories_are_the_ones_git_ignores():
    """
    .gitignore ignores `logs/`. config declared `Logs/`.

    On Windows those are one directory and the mismatch is invisible, which is
    why it survived. On Linux they are two, and only one of them is ignored —
    so a clone that runs the engine finds its own run artifacts staged for
    commit.
    """
    from core import config

    with open(os.path.join(REPO_ROOT, ".gitignore"), encoding="utf-8") as f:
        ignored = {l.strip().rstrip("/") for l in f if l.strip()
                   and not l.startswith("#")}

    for name in ("LOG_DIR", "CHART_DIR"):
        value = getattr(config, name).replace("\\", "/").strip("/")
        root = value.split("/")[0]
        assert root in ignored, (
            f"config.{name} is {getattr(config, name)!r}, whose top-level "
            f"directory {root!r} is not in .gitignore. Engine output would be "
            f"offered for commit. .gitignore ignores: {sorted(ignored)[:8]}..."
        )


def _docstrings(tree):
    """Every docstring node in a module, by identity."""
    out = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef,
                             ast.FunctionDef, ast.AsyncFunctionDef)):
            body = getattr(node, "body", None)
            if (body and isinstance(body[0], ast.Expr)
                    and isinstance(body[0].value, ast.Constant)
                    and isinstance(body[0].value.value, str)):
                out.add(id(body[0].value))
    return out


def test_no_module_hardcodes_a_path_config_declares():
    """
    Five sites carried one. signal_router.py had
    f"Logs/Charts/chart_{symbol}_{timeframe}.png" as a `.get` default and
    created "Logs/Charts" directly; main.py opened 'Logs/phase7_engine.log';
    live_trading.py defaulted to "Logs/LiveSim/". Each is a copy of a path
    config declares, in the case config does not use — so on Linux half the
    engine wrote to a directory the other half never read and git did not
    ignore.

    Docstrings are exempt and comments are already stripped. Both quote the
    defective strings deliberately — core/decision_log.py's opening docstring
    reproduces the trade-log line sequence item 12 was written to remove — and
    a scan that cannot tell a quotation from an instruction would force the
    history out of the record to stay green.
    """
    needles = ("Logs/", "Logs\\\\", "Logs/Charts", "logs/charts", "logs/livesim")
    offenders = []

    for rel, code in _engine_sources():
        try:
            tree = ast.parse(code)
        except SyntaxError:
            continue
        skip = _docstrings(tree)
        for node in ast.walk(tree):
            if (isinstance(node, ast.Constant)
                    and isinstance(node.value, str)
                    and id(node) not in skip):
                for needle in needles:
                    if needle in node.value:
                        offenders.append(f"{rel}: {node.value!r}")
                        break

    assert not offenders, (
        "modules contain a hardcoded log or chart path:\n  "
        + "\n  ".join(sorted(set(offenders)))
        + "\n\nUse config.LOG_DIR / config.CHART_DIR. A duplicated path is a "
          "setting that only half the engine obeys."
    )


def test_the_chart_path_has_no_doubled_separator():
    """
    CHART_DIR ends in a separator and the save path was built with an f-string
    that added another, so every chart path the engine reported read
    "logs/charts//chart_...". Harmless to the filesystem, wrong in the record.
    """
    from core import config

    joined = os.path.join(config.CHART_DIR, "chart_TESTUSDT_4h.png")
    normalised = joined.replace("\\", "/")

    assert "//" not in normalised, (
        f"the chart path doubles a separator: {joined!r}"
    )


# ============================================================
# The settings actually steer the engine
# ============================================================

def test_changing_an_indicator_length_changes_the_indicator():
    """
    The behavioural half. The static scan proves config is MENTIONED at the
    calculation; this proves the value reaches it.

    RSI is used because it has a fallback path that recomputes the same
    quantity by hand — so a length wired only into the primary path would pass
    a source scan and fail here the moment the primary path was unavailable.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    import pandas as pd
    from core import config
    from indicators import indicators

    df = pd.read_csv(os.path.join(REPO_ROOT, "tests", "fixtures",
                                  "ohlcv_clean_4h.csv"))

    original = config.RSI_LENGTH
    try:
        config.RSI_LENGTH = 14
        out_a, _ = indicators.add_technical_indicators(df, inplace=False)
        config.RSI_LENGTH = 30
        out_b, _ = indicators.add_technical_indicators(df, inplace=False)
    finally:
        config.RSI_LENGTH = original

    a = float(out_a["RSI"].iloc[-1])
    b = float(out_b["RSI"].iloc[-1])

    assert a != b, (
        f"RSI is {a} at length 14 and {b} at length 30 — config.RSI_LENGTH "
        f"does not reach the calculation. It was hardcoded to 14 on both the "
        f"primary and the manual fallback path until sequence item 14."
    )


def test_the_chart_settings_reach_matplotlib():
    """
    Source-level. Rendering a chart to check the figure size would need
    matplotlib, a display-free backend and a temp file, to assert something a
    two-line scan states exactly: the numbers come from config, not from the
    renderer.
    """
    with open(os.path.join(REPO_ROOT, "utils", "plotting.py"),
              encoding="utf-8") as f:
        code = "\n".join(l.split("#", 1)[0] for l in f.read().splitlines())

    assert "figsize=(config.CHART_WIDTH, config.CHART_HEIGHT)" in code, (
        "plotting.py does not take its figure size from config"
    )
    assert "dpi=config.CHART_DPI" in code, (
        "plotting.py does not take its dpi from config"
    )
    assert "plt.style.use(config.CHART_STYLE)" in code, (
        "plotting.py does not take its style from config"
    )
    assert "figsize=(14, 8)" not in code and "dpi=200" not in code, (
        "the hardcoded chart dimensions are back alongside the config reads"
    )
