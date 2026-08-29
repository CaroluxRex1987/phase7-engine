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
    def _affected():
        return [m for m in list(sys.modules)
                if any(m == e or m.startswith(e + ".") for e in ENGINE_MODULES)]

    # Snapshot the real module objects before disturbing anything.
    #
    # WHY THIS MATTERS — a bug this test caused, 29 August 2026.
    #
    # Deleting modules from sys.modules and re-importing them creates NEW
    # module objects. ENGINE_MODULES lists core.engine_core before
    # data.data_fetcher, so engine_core is re-imported first and binds the
    # data_fetcher singleton that exists at that moment; data.data_fetcher is
    # then deleted and re-imported, producing a *second* singleton.
    #
    # From then on, `from data.data_fetcher import data_fetcher` gives one
    # object and engine_core holds another. Anything that patches module-level
    # state afterwards — a pinned data source, a base_url override, a
    # monkeypatched method — patches the copy the engine is not using, silently.
    #
    # test_smoke.py did exactly that. It set base_url to a dead port and
    # activated the pinned source, and the engine went to the live MEXC API
    # anyway. The tests still passed, for the wrong reasons: one of them was
    # asserting that a bad symbol produces an error, and it got a real 400 from
    # a real server instead of the refusal it was written to check.
    #
    # It only appeared in a full-suite run. Running `run_tests.py smoke` alone
    # worked correctly, because this test had not run first. That is the worst
    # shape of bug — invisible in isolation, wrong in aggregate.
    saved = {m: sys.modules[m] for m in _affected()}

    failures = []
    try:
        for mod in ENGINE_MODULES:
            for cached in [m for m in sys.modules if m == mod or m.startswith(mod + ".")]:
                del sys.modules[cached]
            try:
                importlib.import_module(mod)
            except Exception as e:
                failures.append(f"{mod}: {type(e).__name__}: {e}")
    finally:
        # Put the original module objects back, so every later test sees one
        # consistent set of modules rather than a mixture.
        #
        # Restoring sys.modules alone is NOT enough, and the first attempt at
        # this fix was wrong for exactly that reason. Importing a submodule
        # also sets it as an attribute on its parent package, so after the
        # re-import above `data.data_fetcher` resolves through sys.modules to
        # the restored module but through attribute access on the `data`
        # package to the new one. Both halves have to be put back.
        for m in _affected():
            del sys.modules[m]
        for name, module in saved.items():
            sys.modules[name] = module
            if "." in name:
                parent, child = name.rsplit(".", 1)
                if parent in sys.modules:
                    setattr(sys.modules[parent], child, module)

    assert not failures, "modules failed to import:\n  " + "\n  ".join(failures)


def test_the_engine_and_the_fetcher_module_share_one_singleton():
    """
    The guard against the bug the test above used to cause.

    engine_core imports the module-scope `data_fetcher` singleton. If that ever
    stops being the same object the fetcher module exposes, then patching the
    fetcher — for pinned data, for a dead base_url, for a monkeypatched method
    — silently patches something the engine is not using, and any test relying
    on that patch passes while proving nothing.

    Cheap to check, and it fails loudly the moment the module table is left
    inconsistent by anything.
    """
    import core.engine_core as engine_core
    import data.data_fetcher as fetcher_module

    assert engine_core.data_fetcher is fetcher_module.data_fetcher, (
        "core.engine_core and data.data_fetcher are holding different "
        "DataFetcher singletons.\n"
        "Something has deleted and re-imported modules without restoring "
        "sys.modules. Every test that patches fetcher state after that point "
        "is patching an object the engine does not use."
    )


def test_declared_dependencies_cover_actual_imports():
    """
    Constitution Tier 2, item 6 (controlled dependencies).

    Originally: requirements.txt named pandas, numpy, matplotlib, ccxt and
    pandas_ta. The code also imported requests and colorama, neither declared;
    and nothing anywhere imported ccxt, which was declared. A fresh
    `pip install -r requirements.txt` therefore produced an environment in
    which the engine could not start. Fixed 29 August 2026, sequence item 2.

    Scope note, added the same day: this test walks engine code only. The
    reportlab scripts under docs/build/ generate the project's PDFs and are
    documentation tooling, not engine code. Counting their imports here would
    demand reportlab in requirements.txt, and a fresh install would then pull
    a PDF library the engine never touches — which is the same defect this
    test exists to catch, pointed the other way. docs/build/ has its own
    install line in its README.
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
    for rel in all_python_files(include_doc_tooling=False):
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
