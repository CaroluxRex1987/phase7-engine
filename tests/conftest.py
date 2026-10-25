"""
Shared test setup for the Phase-7 engine.

Puts the repository root on sys.path so tests can import engine modules the
same way main.py does, and exposes the pinned fixture directory.

Works under pytest. Also importable by run_tests.py, the dependency-free
fallback runner, so the suite can be executed on a machine with no pytest
installed.
"""

import atexit
import os
import shutil
import sys
import tempfile

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(TESTS_DIR)
FIXTURES = os.path.join(TESTS_DIR, "fixtures")

if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)


# ============================================================
# THE SUITE MUST NOT REACH THE ENGINE'S REAL RECORD
# ============================================================
#
# Found 6 September 2026 by running the suite and watching the filesystem,
# which is the only way it could be found: nothing in the source says it.
#
# Twenty-eight tests, spread across ELEVEN files, ran the engine against the
# real `config.LOG_DIR`, so every suite run appended real decision records to
# `logs/phase7_decision_log_aerousdt.jsonl` -- the permanent record Items 5
# and 6 are about, and the artifact the release gate's evidence rests on.
# Nine records per run, plus an archive, plus a chart, plus the cross-run
# state file.
#
# Three more files reached that directory without writing a record: a twelfth
# deleted it (below), a thirteenth created it as an import side effect
# (test_imports.py), and a fourteenth wrote PNGs into it through the
# capitalised `Logs/Charts` spelling (test_frame_ownership.py), which is one
# directory on Windows and two on Linux.
#
# One test went further. `test_lineage.py`'s archive-path spelling test wrote
# into the literal relative path "logs/" and then called
# `shutil.rmtree("logs")` in its `finally` -- deleting the whole directory:
# the decision log, every archive, the charts and the state file. That is how
# a live run's record and three earlier records were lost. `logs/` is
# gitignored, so nothing anywhere held a second copy.
#
# The Section 11 harness was fixed for this same defect in the same week, by
# repointing `config.LOG_DIR` at a temporary directory for the duration. That
# fix was applied to one caller. This applies it to the process.
#
# Rule 28: change the setup so the safe action is the only one available,
# rather than writing down which of several options is correct. A test that
# wants a log directory now gets a temporary one whether or not its author
# thought about it.
#
# Done at import time rather than as a pytest fixture deliberately.
# `run_tests.py` -- the dependency-free runner this file's docstring promises
# to work under -- never calls a fixture, but it does import this module. One
# place, both runners.

REAL_LOG_DIR = os.path.join(REPO_ROOT, "logs")

# Matched case-INSENSITIVELY, and that is the whole point of this constant.
#
# `Logs/Charts` and `logs/charts` are two directories on Linux and one
# directory on Windows. A test carrying the capitalised spelling therefore
# creates a harmless stray folder in a sandbox and writes into the engine's
# live chart directory on Viktor's machine -- so a guard that watches only
# `logs` passes on the platform where the fix is developed and fails on the
# platform that matters. That happened on 6 September 2026, to this guard, on
# its first run: two PNGs from test_frame_ownership.py.
#
# Scanning by lowercased name means a Linux run catches what a Windows run
# would, which is the only way verification here is worth anything.
LOG_DIR_NAMES = frozenset({"logs"})


def _snapshot_log_dirs(root=None):
    """
    Every directory directly under `root` whose name lowercases to "logs",
    and every file inside it with its size, as sorted (path, size) pairs.

    Paths are prefixed with the directory's real name, so `logs/x.jsonl` and
    `Logs/x.jsonl` are distinguishable on a filesystem that distinguishes
    them. Sizes rather than names alone, because appending a decision record
    does not change the file list.

    Returns None when no such directory exists, which is the normal state of
    a fresh clone.
    """
    root = REPO_ROOT if root is None else root
    try:
        names = sorted(n for n in os.listdir(root)
                       if n.lower() in LOG_DIR_NAMES
                       and os.path.isdir(os.path.join(root, n)))
    except OSError:
        return None
    if not names:
        return None

    out = []
    for name in names:
        base = os.path.join(root, name)
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames.sort()
            for fn in sorted(filenames):
                full = os.path.join(dirpath, fn)
                rel = os.path.relpath(full, base).replace(os.sep, "/")
                try:
                    size = os.path.getsize(full)
                except OSError:
                    size = None
                out.append((f"{name}/{rel}", size))
    return sorted(out)


REAL_LOG_DIR_AT_START = _snapshot_log_dirs()

_SUITE_LOG_DIR = tempfile.mkdtemp(prefix="phase7_suite_logs_")
atexit.register(shutil.rmtree, _SUITE_LOG_DIR, True)

from core import config as _config  # noqa: E402  (needs REPO_ROOT on sys.path)

# The values the engine actually ships with, kept so a guard test can prove
# this override is a test-session redirection and not a change to what a real
# run does.
SHIPPED_LOG_DIR = _config.LOG_DIR
SHIPPED_CHART_DIR = _config.CHART_DIR

SUITE_LOG_DIR = _SUITE_LOG_DIR

_config.LOG_DIR = _SUITE_LOG_DIR + os.sep
_config.CHART_DIR = os.path.join(_SUITE_LOG_DIR, "charts") + os.sep

# Every module in the engine, as a dotted import path. Empty __init__.py
# package markers are excluded deliberately: they contain nothing to break.
#
# HELD TO THE TREE, 24 October 2026 (the list for after the audit, entry 49,
# found on 20 October). This comment said "every module" while the list was
# three short: core.lineage, core.code_fingerprint and
# utils.decision_log_backup were added to the engine on 2, 6 and 12 September
# and never here, so test_every_module_imports never imported them. Rule 11:
# a list of names is a claim about the code, and it decays. So the claim is
# checked now: tests/test_imports.py::test_engine_modules_is_every_module_in_the_tree
# reads every .py file core/code_fingerprint.py reads for code_hash, and fails
# on one that is in neither this list nor NOT_ENGINE_MODULES below. It does
# not fill the list in: a module listed by a walk would be imported by
# test_every_module_imports, and test_live.py shows what importing a script
# can do. Someone decides which list a new file goes in, and until then the
# suite fails.
ENGINE_MODULES = [
    "core.code_fingerprint",
    "core.config",
    "core.decision_contract",
    "core.decision_log",
    "core.engine_core",
    "core.lineage",
    "core.panel_render",
    "data.data_fetcher",
    "data.validation",
    "indicators.indicators",
    "indicators.trend_health",
    "indicators.volume_profile",
    "models.bias_engine",
    "models.btc_context",
    "models.decision_model",
    "models.entry_model",
    "models.exit_model",
    "models.risk_model",
    "models.signal_router",
    "structure.structure",
    "utils.decision_log_backup",
    "utils.plotting",
    "live_trading",
    "main",
]

# The .py files code_hash reads that are not the engine, each with its reason.
# The check named above fails on a file in neither list, and on a name in
# either that is no longer a file, so this one cannot go stale unseen either.
NOT_ENGINE_MODULES = {
    "run_tests": "the suite's fallback runner: test tooling kept at the "
                 "repository root, not engine code",
    "test_live": "a hand-run script whose module body runs the engine once "
                 "through live_trading's simulator, which writes a simulated "
                 "order when the run succeeds: importing it is running it",
}

# The .py files code_hash reads, as paths relative to the root -- and with
# include_doc_tooling, those under docs/ as well. The compile check walks
# these; it does not import them, so it is safe to include modules with side
# effects at import time.
#
# `docs/build/` holds the reportlab scripts that generate the project's PDFs.
# They are real Python and a syntax error in one is a real bug, so the compile
# check should cover them — but they are documentation tooling, not the engine,
# and their imports must not count toward the engine's dependency manifest.
# Adding reportlab to requirements.txt to satisfy a docs script would make a
# fresh `pip install -r requirements.txt` pull a PDF library the engine never
# uses. Hence the flag: include them when checking syntax, exclude them when
# checking declared dependencies.
#
# ONE LIST OF DIRECTORIES, 25 October 2026 (the list for after the audit,
# entry 51, found on 24 October landing entry 49). This walk skipped a set of
# directory names of its own, and core/code_fingerprint.py's
# EXCLUDED_DIR_NAMES -- what code_hash, and so every decision record, counts
# as the engine -- skipped four more: .pytest_cache, env, Backup and
# Claude outputs. Two lists of the same directories, drifted apart (rule 11):
# a .py file under env/, Backup/ or Claude outputs/ would have been read here
# as the engine, by the compile check, the dependency check and every source
# scan, and was not the engine in any record. So the walk takes code_hash's
# list, read when it is called, and gives docs/ back to the compile check
# alone: without the flag it reads exactly what code_hash reads. One list, so
# the two cannot drift (rule 28).
# tests/test_imports.py::test_the_suite_walks_the_files_code_hash_reads holds
# it. `root` is for that test; every other caller walks the repository.
DOC_TOOLING_DIRS = {"docs"}


def all_python_files(include_doc_tooling=True, root=None):
    from core import code_fingerprint

    root = REPO_ROOT if root is None else root
    skip = set(code_fingerprint.EXCLUDED_DIR_NAMES)
    if include_doc_tooling:
        skip -= DOC_TOOLING_DIRS
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in skip]
        for fn in sorted(filenames):
            if fn.endswith(".py"):
                out.append(os.path.relpath(os.path.join(dirpath, fn), root))
    return sorted(out)


def fixture(name):
    return os.path.join(FIXTURES, name)
