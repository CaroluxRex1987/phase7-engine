"""
The cheapest test in the suite, and the one that would have prevented the
most damage.

The engine's runtime log records seven separate occasions where a change was
accepted and then discovered broken only when someone ran the engine by hand:

    2026-08-24 17:06:05  name 'Optional' is not defined
    2026-08-24 17:14:01  name 'Any' is not defined
    2026-08-24 17:15:08  name 'Any' is not defined
    2026-08-24 17:16:14  name 'Any' is not defined
    2026-08-25 00:07:38  unterminated f-string (volume_profile.py, line 105)
    2026-08-25 00:10:49  expected 'except' or 'finally' block (volume_profile.py, line 208)
    2026-08-25 00:52:28  invalid syntax (indicators.py, line 121)
    2026-08-25 00:53:37  unindent does not match any outer indentation level
    2026-08-25 01:13:30  cannot import name 'config' from 'models'

Every one of those is caught by compiling and importing the modules. None of
them required running the engine, fetching data, or knowing anything about
markets. They are exactly what an automated check is for.

Constitution: Tier 3, items 3 (automated tests) and 4 (regression tests),
both currently Non-compliant.
"""

import importlib
import os
import py_compile
import sys

from conftest import ENGINE_MODULES, REPO_ROOT, all_python_files


def test_every_file_compiles():
    """
    Catches syntax errors, unterminated strings, bad indentation, and missing
    except/finally blocks — five of the nine logged failures — without
    executing anything.
    """
    import tempfile
    failures = []
    with tempfile.TemporaryDirectory() as tmp:
        for rel in all_python_files():
            path = os.path.join(REPO_ROOT, rel)
            out = os.path.join(tmp, rel.replace(os.sep, "_") + "c")
            try:
                py_compile.compile(path, doraise=True, cfile=out)
            except py_compile.PyCompileError as e:
                failures.append(f"{rel}: {e.msg.strip().splitlines()[-1]}")
    assert not failures, "files failed to compile:\n  " + "\n  ".join(failures)


def test_every_module_imports():
    """
    Catches undefined names at module scope, bad import paths, and anything
    that raises while a module is being loaded — the remaining four logged
    failures.

    This is the check that fails today on a clean checkout. See
    test_clean_checkout.py for why, and for the isolated case.
    """
    failures = []
    for mod in ENGINE_MODULES:
        for cached in [m for m in sys.modules if m == mod or m.startswith(mod + ".")]:
            del sys.modules[cached]
        try:
            importlib.import_module(mod)
        except Exception as e:
            failures.append(f"{mod}: {type(e).__name__}: {e}")
    assert not failures, "modules failed to import:\n  " + "\n  ".join(failures)


def test_declared_dependencies_cover_actual_imports():
    """
    Constitution Tier 2, item 6 (controlled dependencies) — Non-compliant.

    requirements.txt names pandas, numpy, matplotlib, ccxt and pandas_ta.
    The code also imports requests and colorama, neither declared; and
    nothing anywhere imports ccxt, which is declared.

    A fresh `pip install -r requirements.txt` therefore produces an
    environment in which the engine cannot start.
    """
    req_path = os.path.join(REPO_ROOT, "requirements.txt")
    declared = set()
    with open(req_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                name = line.split("==")[0].split(">=")[0].split("[")[0].strip()
                declared.add(name.lower().replace("-", "_"))

    third_party = set()
    stdlib = set(sys.stdlib_module_names)
    local = {"core", "data", "indicators", "models", "structure", "utils",
             "main", "live_trading", "conftest"}
    import ast
    for rel in all_python_files():
        with open(os.path.join(REPO_ROOT, rel), encoding="utf-8") as f:
            try:
                tree = ast.parse(f.read())
            except SyntaxError:
                continue                      # reported by the compile test
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    third_party.add(a.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                third_party.add(node.module.split(".")[0])
    third_party = {m.lower() for m in third_party if m not in stdlib and m not in local}

    missing = sorted(m for m in third_party if m not in declared)
    unused = sorted(d for d in declared if d not in third_party)

    msg = []
    if missing:
        msg.append(f"imported but not declared: {', '.join(missing)}")
    if unused:
        msg.append(f"declared but never imported: {', '.join(unused)}")
    assert not msg, "requirements.txt does not match the code:\n  " + "\n  ".join(msg)
