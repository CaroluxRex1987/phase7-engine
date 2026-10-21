"""
Item 18 — Read-Only Market Access, kept Compliant by a standing check.

Item 18 says the engine must never hold credentials with trade-execution
permissions, and must never be able to place an order. Run 1's blind review
verified that by hand: it searched all nineteen files for place_order,
create_order, createOrder, .buy(, .sell( and found none, and confirmed
live_trading.py only builds a dict and writes JSON.

That verification was a snapshot. These tests make it continuous.

The distinction matters because Item 18 is the invariant the whole project is
built around — it is what makes "this cannot lose money" true rather than
aspirational. An audit finding says the property held on 27 August. A test says
it holds now, and fails the moment someone adds a dependency or a convenience
method that would break it.

Constitution: Tier 1, Items 18 through 21. Sequence item 4.

A note on precision. The word "order" appears sixteen times in this codebase in
entirely benign contexts — live_trading.py builds a dict it calls an order and
writes it to JSON, which is a simulation, not an execution. A guard that
grepped for the word would fire on all sixteen and would be deleted within a
week for crying wolf. These guards target call syntax and import statements,
which is what an actual execution surface looks like.

EACH SCAN NOW SHOWS IT CAN FIRE (20 October 2026; round 8, run 2, Part 4,
shape 1, which names test_no_order_execution_calls "and its three siblings";
the list for after the audit, entry 37). A scan that reads no file, or whose
matcher matches nothing, passes on any tree. So each matcher is a function
below, the scan calls it, and the controls at the end of this file show that
the source scans read every module in conftest.ENGINE_MODULES, that both
manifests are read, and that each matcher reports the shape it exists for.
The file has four tests beside the first, not three, and all four are
covered. Writing the controls found three shapes the scans could not see:

  - `import json, ccxt`. The import scan matched the first name on a line
    only. Imports are read from the parse tree now, and a name handed to
    importlib.import_module() or __import__() is read too.
  - `python-binance`, `binance-connector` and `alpaca-trade-api`, the names
    a requirements file gives two of the four libraries. The manifest scan
    compared a requirement's name with the import name, which for binance
    and alpaca_trade_api is not that name.
  - `ccxt~=4.0`, `ccxt<5`, `ccxt[pro]`, and a line with a marker. The
    manifest scan cut a line at "==" and ">=" only.
"""

import ast
import os
import re

from conftest import ENGINE_MODULES, REPO_ROOT, all_python_files

# Calls that would place, modify or cancel a real order. Matched as call
# syntax — `place_order(` — not as bare words, so "order" in a variable name
# or a comment does not trip them.
EXECUTION_CALLS = [
    "place_order", "create_order", "createOrder", "submit_order",
    "new_order", "cancel_order", "cancelOrder", "post_order",
    "create_market_buy_order", "create_market_sell_order",
    "create_limit_buy_order", "create_limit_sell_order",
]

# Libraries whose presence means the engine could execute, whatever the code
# currently does with them. ccxt was declared in requirements.txt until
# sequence item 2 removed it, despite nothing importing it.
EXECUTION_LIBRARIES = ["ccxt", "binance", "krakenex", "alpaca_trade_api"]

# A requirements file names a library by the name pip installs it under, which
# is not always the name it is imported by. `binance` is installed as
# python-binance or binance-connector; alpaca_trade_api as alpaca-trade-api,
# which _requirement_name() below reads as the same name. Read from each
# package's wheel on PyPI, 20 October 2026: the wheel's top-level package is
# the import name above.
EXECUTION_DISTRIBUTIONS = ["python-binance", "binance-connector"]

MANIFESTS = ["requirements.txt", "requirements-dev.txt"]

# Endpoint paths that only exist to trade. The engine's read-only endpoint is
# /api/v3/klines; anything under /order or /account is a different animal.
EXECUTION_ENDPOINTS = ["/api/v3/order", "/api/v3/account", "/api/v3/openOrders"]


def _engine_sources():
    """Engine code only — not the documentation build scripts, not the tests."""
    return [rel for rel in all_python_files(include_doc_tooling=False)
            if not rel.replace("\\", "/").startswith("tests/")]


def _read(rel):
    with open(os.path.join(REPO_ROOT, rel), encoding="utf-8", errors="replace") as f:
        return f.read()


# --- the matchers ----------------------------------------------------------
# One function per scan, so that each scan and its control at the end of this
# file run the same code on different text.

def execution_calls_in(source):
    """[(line, text)] for each call to a name in EXECUTION_CALLS, matched as
    call syntax -- `place_order(` -- on a line that is not a comment."""
    hits = []
    for lineno, line in enumerate(source.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue                     # a comment naming one is fine
        for call in EXECUTION_CALLS:
            if re.search(rf"\b{re.escape(call)}\s*\(", line):
                hits.append((lineno, stripped[:90]))
    return hits


def execution_imports_in(source):
    """
    [(line, module)] for each import of a package in EXECUTION_LIBRARIES,
    read from the parse tree: every name of `import a, b`, the module of
    `from x import y` (a relative import names a local module, not the
    library), and a string handed to importlib.import_module() or
    __import__(). A comment or a docstring naming one is not an import.
    """
    found = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            names = [node.module] if node.level == 0 and node.module else []
        elif (isinstance(node, ast.Call)
              and (getattr(node.func, "id", None) or getattr(node.func, "attr", None))
              in ("import_module", "__import__")
              and node.args and isinstance(node.args[0], ast.Constant)
              and isinstance(node.args[0].value, str)):
            names = [node.args[0].value]
        else:
            continue
        found.extend((node.lineno, name) for name in names
                     if name.split(".")[0] in EXECUTION_LIBRARIES)
    return found


def _requirement_name(line):
    """A requirement line's project name as pip compares names -- lowercase,
    with each run of '-', '_' and '.' read as one '-' -- or None for a line
    that names none: a comment, a blank, an option such as -r."""
    match = re.match(r"\s*([A-Za-z0-9][A-Za-z0-9._-]*)", line)
    return re.sub(r"[-_.]+", "-", match.group(1)).lower() if match else None


def declared_execution_libraries(manifest_text):
    """[(line, name)] for each requirement naming an execution library, by its
    import name or by the name pip installs it under, whatever version
    specifier, extras or marker follows the name."""
    wanted = {_requirement_name(name)
              for name in EXECUTION_LIBRARIES + EXECUTION_DISTRIBUTIONS}
    found = []
    for lineno, line in enumerate(manifest_text.splitlines(), 1):
        name = _requirement_name(line)
        if name in wanted:
            found.append((lineno, name))
    return found


def trading_endpoints_in(source):
    """[(line, text)] for each line, not a comment, naming a path in
    EXECUTION_ENDPOINTS."""
    hits = []
    for lineno, line in enumerate(source.splitlines(), 1):
        if line.strip().startswith("#"):
            continue
        for endpoint in EXECUTION_ENDPOINTS:
            if endpoint in line:
                hits.append((lineno, line.strip()[:90]))
    return hits


# api_key = "something long enough to be real"
CREDENTIAL_ASSIGNMENT = re.compile(
    r"""(?ix)
    \b(
        api[_-]?key | api[_-]?secret | secret[_-]?key |
        access[_-]?token | private[_-]?key | passphrase
    )\s*=\s*
    ["']([^"']{16,})["']
    """
)
CREDENTIAL_PLACEHOLDERS = {"your_api_key_here", "changeme", "xxx", "none", "null",
                           "placeholder", "todo", "example", ""}


def credential_literals_in(source):
    """[(line, name, length)] for each key-shaped NAME assigned a literal of 16
    characters or more that is not a placeholder, on a line that is not a
    comment."""
    hits = []
    for lineno, line in enumerate(source.splitlines(), 1):
        if line.strip().startswith("#"):
            continue
        m = CREDENTIAL_ASSIGNMENT.search(line)
        if m and m.group(2).strip().lower() not in CREDENTIAL_PLACEHOLDERS:
            hits.append((lineno, m.group(1), len(m.group(2))))
    return hits


# --- the scans --------------------------------------------------------------

def test_no_order_execution_calls():
    """
    The property Item 18 exists to guarantee.

    If this ever fails, the engine has gained the ability to act rather than
    advise, and the release gate is the least of the problems.
    """
    hits = [f"{rel}:{lineno}  {text}"
            for rel in _engine_sources()
            for lineno, text in execution_calls_in(_read(rel))]

    assert not hits, (
        "order-execution calls found — Item 18 forbids the engine from being "
        "able to place a trade at all:\n  " + "\n  ".join(hits)
    )


def test_no_execution_capable_libraries_are_imported():
    """
    ccxt was declared in requirements.txt for weeks while nothing imported it.
    A declared-but-unused execution library is a loaded gun in a drawer: the
    engine cannot fire it today, and the next person to add a feature finds it
    already installed.

    Read from the parse tree since 20 October 2026 (the module docstring).
    """
    hits = [f"{rel}:{lineno}  import {name}"
            for rel in _engine_sources()
            for lineno, name in execution_imports_in(_read(rel))]

    assert not hits, (
        "execution-capable libraries imported:\n  " + "\n  ".join(hits)
    )


def test_execution_libraries_are_not_declared_as_dependencies():
    """
    The manifest half of the same guard. Nothing should install an execution
    library into an environment this engine runs in.

    By the name pip installs it under, and with any specifier, since
    20 October 2026 (the module docstring).
    """
    declared = []
    for manifest in MANIFESTS:
        path = os.path.join(REPO_ROOT, manifest)
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            declared.extend(f"{manifest}:{lineno}  {name}" for lineno, name
                            in declared_execution_libraries(f.read()))

    assert not declared, (
        "execution-capable libraries declared as dependencies:\n  "
        + "\n  ".join(declared) +
        "\nItem 18 puts the guarantee in the exchange, not the code — but an "
        "installed execution library makes the code the only thing standing "
        "between this engine and an order."
    )


def test_no_trading_endpoints_referenced():
    """
    The engine talks to exactly one endpoint: /api/v3/klines, which is public
    market data and requires no authentication. Anything under /order or
    /account requires a key and does something.
    """
    hits = [f"{rel}:{lineno}  {text}"
            for rel in _engine_sources()
            for lineno, text in trading_endpoints_in(_read(rel))]

    assert not hits, (
        "trading or account endpoints referenced:\n  " + "\n  ".join(hits)
    )


def test_no_credential_literals_in_source():
    """
    Items 19–21. The engine holds no credentials, so none should ever appear
    as a literal.

    Deliberately narrow: it looks for a key-shaped NAME assigned a long
    literal, not for the word "key" or for any long string. Documentation
    about credentials — of which this project has a great deal — must not trip
    it, or the guard gets deleted. The pattern is CREDENTIAL_ASSIGNMENT,
    above.
    """
    hits = [f"{rel}:{lineno}  {name} = <redacted, {length} chars>"
            for rel in _engine_sources()
            for lineno, name, length in credential_literals_in(_read(rel))]

    assert not hits, (
        "credential-shaped literals found in source:\n  " + "\n  ".join(hits) +
        "\nItems 19-21: credentials are read from the environment or an OS "
        "keychain, never committed."
    )


# --- the controls ------------------------------------------------------------
# Each scan above passes on a clean tree, and would pass as well if it read no
# file or its matcher matched nothing (round 8, run 2, Part 4, shape 1). These
# show that it reads what it must and reports what it is for.

def test_the_source_scans_read_every_engine_module():
    """
    The four scans over the source read _engine_sources(). Each module in
    conftest.ENGINE_MODULES, the suite's own list of the engine, must be
    among the files it returns.
    """
    read = {rel.replace("\\", "/") for rel in _engine_sources()}
    expected = {module.replace(".", "/") + ".py" for module in ENGINE_MODULES}
    assert expected, "conftest.ENGINE_MODULES is empty"
    missing = sorted(expected - read)
    assert not missing, f"the source scans do not read: {missing}"


def test_the_manifest_scan_reads_both_manifests():
    """
    The manifest scan passes over a manifest that is not there, so with both
    gone it passes. Both are committed, so each must be there, and each must
    parse as the names it pins.
    """
    names = {}
    for manifest in MANIFESTS:
        path = os.path.join(REPO_ROOT, manifest)
        assert os.path.exists(path), f"{manifest} is not in the repository"
        with open(path, encoding="utf-8") as f:
            names[manifest] = {_requirement_name(line) for line in f.read().splitlines()}
    assert {"pandas", "numpy"} <= names["requirements.txt"], names
    assert "pytest" in names["requirements-dev.txt"], names


def test_the_call_scan_can_report_a_violation():
    """Each name in EXECUTION_CALLS, written as a call, is reported; a comment
    naming one, and "order" as an ordinary name, are not."""
    for call in EXECUTION_CALLS:
        line = f"result = exchange.{call}(symbol, 'buy', 1)"
        assert execution_calls_in(line + "\n") == [(1, line)], call
    assert len(execution_calls_in("client.create_order (symbol)\n")) == 1
    assert execution_calls_in("# exchange.create_order(symbol) is never called\n") == []
    assert execution_calls_in('order = {"side": "buy"}\nwrite_json(order)\n') == []


def test_the_import_scan_can_report_a_violation():
    """Each library in EXECUTION_LIBRARIES, imported in each form, is reported;
    a comment, a docstring, a local module and a longer name are not."""
    for lib in EXECUTION_LIBRARIES:
        assert execution_imports_in(f"import {lib}\n") == [(1, lib)], lib
        assert execution_imports_in(f"import {lib} as client\n") == [(1, lib)], lib
        assert execution_imports_in(f"from {lib} import Client\n") == [(1, lib)], lib
        assert execution_imports_in(f"def connect():\n    import {lib}\n") == [(2, lib)], lib
        # Not seen before 20 October 2026: the line scan matched the first name
        # of an import statement, and nothing that was not one.
        assert execution_imports_in(f"import json, {lib}\n") == [(1, lib)], lib
        assert execution_imports_in(f"importlib.import_module({lib!r})\n") == [(1, lib)], lib
    assert execution_imports_in("import ccxt.pro\n") == [(1, "ccxt.pro")]
    assert execution_imports_in("from binance.client import Client\n") == [
        (1, "binance.client")]
    # Not seen before 20 October 2026 either.
    assert execution_imports_in('client = __import__("ccxt")\n') == [(1, "ccxt")]
    for clean in ("# import ccxt\n", '"""import ccxt"""\n', "from . import ccxt\n",
                  "import ccxt_tools\n", "import json\n", "__import__(name)\n"):
        assert execution_imports_in(clean) == [], clean


def test_the_manifest_scan_can_report_a_violation():
    """Each library is reported by its import name and by the name pip
    installs it under, whatever follows the name; a comment, another
    project and an option are not."""
    for name in EXECUTION_LIBRARIES + EXECUTION_DISTRIBUTIONS:
        assert declared_execution_libraries(f"{name}==1.0.0\n") == [
            (1, _requirement_name(name))], name
    # Not seen before 20 October 2026: two of the four by the name pip
    # installs them under.
    assert declared_execution_libraries("python-binance==1.0.37\n") == [
        (1, "python-binance")]
    assert declared_execution_libraries("alpaca-trade-api==3.2.0\n") == [
        (1, "alpaca-trade-api")]
    # Every specifier, extras and a marker. Before 20 October 2026 a line was
    # cut at "==" and ">=" only, so ~=, <, !=, >, <=, the extras and the
    # marker were not seen.
    for line in ("ccxt", "ccxt>=4.0", "ccxt~=4.0", "ccxt<5", "ccxt!=4.1", "ccxt>4",
                 "ccxt<=4", "ccxt===4.0", "ccxt[pro]==4.0", "CCXT == 4.0",
                 "ccxt ; python_version >= '3.12'", "  ccxt==4.0  # pinned"):
        assert declared_execution_libraries(line + "\n") == [(1, "ccxt")], line
    for clean in ("# ccxt==4.0\n", "pandas==3.0.5\n", "ccxt-tools==1.0\n",
                  "-r requirements.txt\n", "\n"):
        assert declared_execution_libraries(clean) == [], clean


def test_the_endpoint_scan_can_report_a_violation():
    """Each path in EXECUTION_ENDPOINTS is reported; the one the engine reads,
    and a comment naming one, are not."""
    for endpoint in EXECUTION_ENDPOINTS:
        assert len(trading_endpoints_in(f'url = BASE_URL + "{endpoint}"\n')) == 1, endpoint
    assert trading_endpoints_in('url = BASE_URL + "/api/v3/klines"\n') == []
    assert trading_endpoints_in('# never "/api/v3/order"\n') == []


def test_the_credential_scan_can_report_a_violation():
    """A key-shaped name assigned a long literal is reported, in either case;
    a placeholder, a value read from the environment, a short literal and a
    comment are not."""
    assert credential_literals_in('api_key = "a1b2c3d4e5f6g7h8i9j0"\n') == [
        (1, "api_key", 20)]
    assert len(credential_literals_in("API_SECRET='a1b2c3d4e5f6g7h8i9j0k1'\n")) == 1
    for clean in ('api_key = "your_api_key_here"\n',
                  'api_key = os.environ["MEXC_API_KEY"]\n',
                  'api_key = "short"\n',
                  '# api_key = "a1b2c3d4e5f6g7h8i9j0"\n'):
        assert credential_literals_in(clean) == [], clean
