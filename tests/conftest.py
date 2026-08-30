"""
Shared test setup for the Phase-7 engine.

Puts the repository root on sys.path so tests can import engine modules the
same way main.py does, and exposes the pinned fixture directory.

Works under pytest. Also importable by run_tests.py, the dependency-free
fallback runner, so the suite can be executed on a machine with no pytest
installed.
"""

import os
import sys

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(TESTS_DIR)
FIXTURES = os.path.join(TESTS_DIR, "fixtures")

if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# Every module in the engine, as a dotted import path. Empty __init__.py
# package markers are excluded deliberately: they contain nothing to break.
ENGINE_MODULES = [
    "core.config",
    "core.decision_contract",
    "core.engine_core",
    "core.panel_render",
    "data.data_fetcher",
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
    "utils.plotting",
    "live_trading",
    "main",
]

# Every .py file in the repository, as a path relative to the root. The
# compile check walks these; it does not import them, so it is safe to
# include modules with side effects at import time.
#
# `docs/build/` holds the reportlab scripts that generate the project's PDFs.
# They are real Python and a syntax error in one is a real bug, so the compile
# check should cover them — but they are documentation tooling, not the engine,
# and their imports must not count toward the engine's dependency manifest.
# Adding reportlab to requirements.txt to satisfy a docs script would make a
# fresh `pip install -r requirements.txt` pull a PDF library the engine never
# uses. Hence the flag: include them when checking syntax, exclude them when
# checking declared dependencies.
DOC_TOOLING_DIRS = {"docs"}


def all_python_files(include_doc_tooling=True):
    out = []
    skip = {".git", "__pycache__", "tests", "Logs", "logs", "aider-env", ".venv", "venv"}
    if not include_doc_tooling:
        skip = skip | DOC_TOOLING_DIRS
    for dirpath, dirnames, filenames in os.walk(REPO_ROOT):
        dirnames[:] = [d for d in dirnames if d not in skip]
        for fn in sorted(filenames):
            if fn.endswith(".py"):
                out.append(os.path.relpath(os.path.join(dirpath, fn), REPO_ROOT))
    return sorted(out)


def fixture(name):
    return os.path.join(FIXTURES, name)
