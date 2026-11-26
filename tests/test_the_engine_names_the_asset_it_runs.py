"""
The engine names the asset it runs on, not AERO -- entry 40, 26 November 2026.

PHASE7_NEXT.md, "Found after 22 September", entry 40 ("AERO" in names and one
log line, whatever the pair), found choosing the forward measurement's pairs
on 17 October and read from the code: core/engine_core.py's warning when the
BTC context fails said "AERO analysis above is unaffected" on every pair, and
models/btc_context.py's compute_correlation_beta took `aero_closes`, with
`aero_series` and `aero_returns` inside it. `a530006` fixed two panel lines of
the same kind on 21 September (tests/test_panel_prints_only_what_was_computed.py
holds those).

Two tests:

  - no identifier in the engine's source says AERO -- read from the parse tree
    of every file code_hash reads, so a name carried into a new function fails
    here too, and not only the three this entry renamed;
  - a run on TESTUSDT whose BTC context fails logs "TEST analysis above is
    unaffected", the name asset_name() gives, which is the function the
    panel's sentence for the same failure uses.

String constants are not scanned: test_live.py, a hand-run script, names
AEROUSDT as the pair it runs, which is a choice of pair and not the defect
(entry 40's commit records it as left).

No fixtures, so run_tests.py runs both and its watched error count does not
move. The run needs pandas_ta and skips without it; the scan does not.
"""

import ast
import logging
import os
import shutil
import tempfile

import pytest

from conftest import REPO_ROOT

PINNED_DIR = os.path.join(REPO_ROOT, "tests", "fixtures", "pinned")

# A port nothing listens on, as in tests/test_golden_path.py: a fetch that
# escapes the pinned source dies here instead of reaching a live exchange.
UNREACHABLE = "http://127.0.0.1:1"

FAILURE = "stand-in failure of the BTC context"


def _engine_available():
    try:
        import pandas_ta  # noqa: F401
        return True
    except Exception:
        return False


def _identifiers(tree):
    """Every name the parse tree binds or reads, with its line."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            yield node.lineno, node.id
        elif isinstance(node, ast.arg):
            yield node.lineno, node.arg
        elif isinstance(node, ast.Attribute):
            yield node.lineno, node.attr
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                               ast.ClassDef)):
            yield node.lineno, node.name
        elif isinstance(node, ast.keyword) and node.arg is not None:
            yield node.lineno, node.arg
        elif isinstance(node, ast.alias):
            yield getattr(node, "lineno", 0), node.asname or node.name


def test_no_identifier_in_the_engine_says_aero():
    """Read from the parse tree of every file code_hash reads (rule 16)."""
    from core.code_fingerprint import iter_source_files

    files = iter_source_files(REPO_ROOT)
    assert "models/btc_context.py" in files and "core/engine_core.py" in files, (
        f"the walk did not reach the engine's files: {files[:8]}")

    found = []
    for rel in files:
        with open(os.path.join(REPO_ROOT, rel), "rb") as fh:
            tree = ast.parse(fh.read().decode("utf-8"))
        found.extend(f"{rel}:{line} {name}" for line, name in _identifiers(tree)
                     if "aero" in name.lower())

    assert found == [], (
        "names in the engine's source still say AERO, whatever the pair:\n  "
        + "\n  ".join(found))


class _Capture(logging.Handler):
    def __init__(self):
        super().__init__(level=logging.WARNING)
        self.lines = []

    def emit(self, record):
        self.lines.append(record.getMessage())


def test_a_failed_btc_context_logs_the_asset_the_run_was_made_on():
    """
    TESTUSDT is AEROUSDT's pinned candles under another name, copied into a
    directory of the test's own; compute_correlation_beta is replaced by one
    that raises, which is inside the BTC block's handler. The run must go on
    and log one line naming TEST, not AERO.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    import core.engine_core as ec
    from core import config
    from data.data_fetcher import DataFetcher, data_fetcher

    def raising(*args, **kwargs):
        raise RuntimeError(FAILURE)

    directory = tempfile.mkdtemp(prefix="phase7_entry40_")
    pinned = os.path.join(directory, "pinned")
    os.makedirs(pinned)
    for source, target in (("AEROUSDT_4h.csv", "TESTUSDT_4h.csv"),
                           ("AEROUSDT_1d.csv", "TESTUSDT_1d.csv"),
                           ("BTCUSDT_4h.csv", "BTCUSDT_4h.csv")):
        shutil.copyfile(os.path.join(PINNED_DIR, source),
                        os.path.join(pinned, target))

    # Entry 68 (PHASE7_NEXT.md, "Found after 22 September"): an earlier test
    # file, tests/test_measure_draft_gaps.py, runs docs/build/
    # measure_draft_gaps.py's main() in-process, and main() switches logging
    # off for the whole process with logging.disable(CRITICAL), never lifted.
    # This test passed alone and failed in the full suite on 26 November,
    # its line dropped before any handler saw it. Lifted for this run and
    # put back as it was found, so the test's answer does not depend on
    # which files ran before it.
    switched_off = logging.root.manager.disable
    capture = _Capture()
    saved = (ec.compute_correlation_beta, data_fetcher.base_url,
             config.LOG_DIR, config.CHART_DIR)
    ec.logger.addHandler(capture)
    logging.disable(logging.NOTSET)
    try:
        ec.compute_correlation_beta = raising
        data_fetcher.base_url = UNREACHABLE
        config.LOG_DIR = os.path.join(directory, "logs") + os.sep
        config.CHART_DIR = os.path.join(directory, "charts") + os.sep
        DataFetcher.set_pinned_source(pinned)
        decision = ec.Phase7Engine().run(symbol="TESTUSDT", timeframe="4h",
                                         save_chart=False)
    finally:
        logging.disable(switched_off)
        DataFetcher.clear_pinned_source()
        ec.logger.removeHandler(capture)
        (ec.compute_correlation_beta, data_fetcher.base_url,
         config.LOG_DIR, config.CHART_DIR) = saved
        shutil.rmtree(directory, ignore_errors=True)

    assert isinstance(decision, dict) and "error" not in decision, (
        f"the run did not complete: {decision!r:.300}")
    assert decision.get("btc_context") == {"available": False}, (
        f"the BTC context did not fall back to unavailable: "
        f"{decision.get('btc_context')!r:.300}")

    failed = [line for line in capture.lines
              if line.startswith("BTC context analysis failed")]
    assert failed == [
        f"BTC context analysis failed (TEST analysis above is unaffected): "
        f"{FAILURE}"
    ], f"the BTC failure was logged as {failed!r}"
    assert not any("AERO" in line for line in capture.lines), (
        f"a run on TESTUSDT logged AERO: "
        f"{[line for line in capture.lines if 'AERO' in line]!r}")
