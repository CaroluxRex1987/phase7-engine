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
"""

import os
import re

from conftest import REPO_ROOT, all_python_files

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


def test_no_order_execution_calls():
    """
    The property Item 18 exists to guarantee.

    If this ever fails, the engine has gained the ability to act rather than
    advise, and the release gate is the least of the problems.
    """
    hits = []
    for rel in _engine_sources():
        text = _read(rel)
        for lineno, line in enumerate(text.splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue                     # a comment naming one is fine
            for call in EXECUTION_CALLS:
                if re.search(rf"\b{re.escape(call)}\s*\(", line):
                    hits.append(f"{rel}:{lineno}  {stripped[:90]}")

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
    """
    hits = []
    for rel in _engine_sources():
        for lineno, line in enumerate(_read(rel).splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            for lib in EXECUTION_LIBRARIES:
                if re.match(rf"^\s*(import|from)\s+{re.escape(lib)}\b", line):
                    hits.append(f"{rel}:{lineno}  {stripped[:90]}")

    assert not hits, (
        "execution-capable libraries imported:\n  " + "\n  ".join(hits)
    )


def test_execution_libraries_are_not_declared_as_dependencies():
    """
    The manifest half of the same guard. Nothing should install an execution
    library into an environment this engine runs in.
    """
    declared = []
    for manifest in ["requirements.txt", "requirements-dev.txt"]:
        path = os.path.join(REPO_ROOT, manifest)
        if not os.path.exists(path):
            continue
        with open(path) as f:
            for lineno, line in enumerate(f, 1):
                name = line.strip().split("==")[0].split(">=")[0].strip().lower()
                if name and not name.startswith("#") and name in EXECUTION_LIBRARIES:
                    declared.append(f"{manifest}:{lineno}  {name}")

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
    hits = []
    for rel in _engine_sources():
        for lineno, line in enumerate(_read(rel).splitlines(), 1):
            if line.strip().startswith("#"):
                continue
            for endpoint in EXECUTION_ENDPOINTS:
                if endpoint in line:
                    hits.append(f"{rel}:{lineno}  {line.strip()[:90]}")

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
    it, or the guard gets deleted.
    """
    # api_key = "something long enough to be real"
    pattern = re.compile(
        r"""(?ix)
        \b(
            api[_-]?key | api[_-]?secret | secret[_-]?key |
            access[_-]?token | private[_-]?key | passphrase
        )\s*=\s*
        ["']([^"']{16,})["']
        """
    )
    placeholders = {"your_api_key_here", "changeme", "xxx", "none", "null",
                    "placeholder", "todo", "example", ""}

    hits = []
    for rel in _engine_sources():
        for lineno, line in enumerate(_read(rel).splitlines(), 1):
            if line.strip().startswith("#"):
                continue
            m = pattern.search(line)
            if m and m.group(2).strip().lower() not in placeholders:
                hits.append(f"{rel}:{lineno}  {m.group(1)} = <redacted, "
                            f"{len(m.group(2))} chars>")

    assert not hits, (
        "credential-shaped literals found in source:\n  " + "\n  ".join(hits) +
        "\nItems 19-21: credentials are read from the environment or an OS "
        "keychain, never committed."
    )
