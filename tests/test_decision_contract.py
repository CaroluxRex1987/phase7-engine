"""
Sequence item 10 (T2-3) — the decision-object contract, enforced.

core/decision_contract.py declares the shape. This checks it three ways, and
each one catches something the others do not:

  1. The engine really produces it        run on pinned data, validate
  2. Nothing reads a field that is        static scan of every consumer
     not declared
  3. The declaration is not stale         every declared field is produced

(2) is the one that matters most. It is what would have caught the incident
this item exists to prevent — a rename that broke fourteen modules, in a
codebase where nothing said which modules depended on the old name.

(3) is the guard against the contract quietly becoming fiction. A schema that
describes fields the engine stopped emitting is worse than no schema: it reads
as documentation and it is wrong.

NOTE ON THE STATIC SCAN. It matches attribute access by variable name —
decision.get("x"), result["y"] — which is how every consumer in this codebase
reads these objects. That is a real limit: a consumer that assigned the object
to an undeclared name, or unpacked it, would slip past. It is not a type
system and does not pretend to be. It covers the access pattern actually used,
and the contract test above it covers the shape.
"""

import ast
import os
import pytest

from conftest import REPO_ROOT

PINNED_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "fixtures", "pinned")

# Files that consume one of the two objects, and the local names they bind it
# to. Kept explicit rather than scanning the whole repo: a match on any dict
# named `result` somewhere unrelated would be noise, and noise gets tests
# deleted.
CONSUMERS = {
    "core/panel_render.py": ["decision"],
    "live_trading.py": ["result"],
    "models/signal_router.py": ["raw_output"],
}


def _engine_available():
    try:
        import pandas_ta  # noqa: F401
        return True
    except Exception:
        return False


def _annotations(td):
    """A TypedDict's declared fields. Single source of truth, not a copy."""
    return dict(getattr(td, "__annotations__", {}))


def _required(td):
    req = getattr(td, "__required_keys__", None)
    if req is not None:
        return set(req)
    return set(_annotations(td))          # total=True and no __required_keys__


def _is_typed_dict(ann):
    return hasattr(ann, "__annotations__") and hasattr(ann, "__total__")


def _type_ok(value, ann):
    """
    Runtime check for one field.

    bool is tested before int/float on purpose: bool is a subclass of int in
    Python, so `isinstance(True, float)` chains would let a boolean satisfy a
    numeric field and the contract would say nothing.
    """
    origin = getattr(ann, "__origin__", None)

    if _is_typed_dict(ann):
        return isinstance(value, dict)
    if origin in (list,):
        return isinstance(value, list)
    if origin in (tuple,):
        return isinstance(value, (list, tuple))
    if origin in (dict,):
        return isinstance(value, dict)
    if ann is bool:
        return isinstance(value, bool)
    if ann is int:
        return isinstance(value, int) and not isinstance(value, bool)
    if ann is float:
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if ann is str:
        return isinstance(value, str)
    return True                            # Any, and anything unmodelled


def _validate(obj, td, path, problems):
    """Walk a declared shape against a real object, recording every mismatch."""
    anns = _annotations(td)
    required = _required(td)

    for field in sorted(required):
        if field not in obj:
            problems.append(f"{path}.{field} is declared but missing")

    for field, value in obj.items():
        if field not in anns:
            problems.append(
                f"{path}.{field} is produced but NOT declared in the contract"
            )
            continue
        ann = anns[field]
        if not _type_ok(value, ann):
            problems.append(
                f"{path}.{field} is {type(value).__name__} "
                f"({value!r}), contract says {getattr(ann, '__name__', ann)}"
            )
        elif _is_typed_dict(ann) and isinstance(value, dict):
            _validate(value, ann, f"{path}.{field}", problems)


def _run_engine():
    """One run through the production path on pinned data, network unreachable."""
    from data.data_fetcher import DataFetcher, data_fetcher
    from models.signal_router import SignalRouter

    original_url = data_fetcher.base_url
    try:
        data_fetcher.base_url = "http://127.0.0.1:1"
        DataFetcher.set_pinned_source(PINNED_DIR)
        return SignalRouter().route(symbol="AEROUSDT", timeframe="4h")
    finally:
        DataFetcher.clear_pinned_source()
        data_fetcher.base_url = original_url


# ============================================================
# 1. The engine really produces the declared shape
# ============================================================

def test_the_decision_object_matches_the_contract():
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    from core.decision_contract import DecisionObject, ERROR_KEY

    decision = _run_engine()
    assert ERROR_KEY not in decision, (
        f"the engine errored on pinned data: {decision.get(ERROR_KEY)}"
    )

    problems = []
    _validate(decision, DecisionObject, "decision", problems)

    assert not problems, (
        "the decision object does not match core/decision_contract.py:\n  "
        + "\n  ".join(problems)
        + "\n\nIf the engine changed on purpose, update the contract in the "
          "same commit. That is what it is for."
    )


def test_the_btc_block_is_legal_in_both_of_its_shapes():
    """
    btc_context is the one block with two legal shapes: the full reading, or
    {"available": False} alone. Declared total=False so both validate, which
    means the contract cannot catch a consumer that reads `beta` without
    checking `available` first.

    So that is asserted here instead: the unavailable shape must carry nothing
    but the flag. If it ever gains a partially-populated form, every consumer's
    `available` check becomes insufficient and this fails.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    from models.signal_router import SignalRouter

    unavailable = SignalRouter()._merge_btc_context({}, {})

    assert unavailable == {"available": False}, (
        f"the unavailable BTC shape is {unavailable!r}, expected exactly "
        '{"available": False}.\n'
        "Consumers gate every other field on `available`. A partially "
        "populated unavailable-block would make that check insufficient "
        "without any of them changing."
    )


# ============================================================
# 2. Nothing reads a field the contract does not declare
# ============================================================

def _keys_read(path, varnames):
    """Every string key read off the named variables in one file."""
    with open(os.path.join(REPO_ROOT, path), encoding="utf-8") as f:
        tree = ast.parse(f.read())

    found = set()
    for node in ast.walk(tree):
        # obj.get("key") / obj.get("key", default)
        if (isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "get"
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id in varnames
                and node.args
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)):
            found.add(node.args[0].value)
        # obj["key"]
        elif (isinstance(node, ast.Subscript)
                and isinstance(node.value, ast.Name)
                and node.value.id in varnames
                and isinstance(node.slice, ast.Constant)
                and isinstance(node.slice.value, str)):
            found.add(node.slice.value)
    return found


def test_every_field_a_consumer_reads_is_declared():
    """
    The guard the fourteen-module rename needed.

    A rename lands in the producer, the consumers keep asking for the old name,
    and `.get()` hands each of them a default instead of an error. The panel
    renders zeros, the log records them, and nothing raises. This fails
    instead.
    """
    from core import decision_contract as contract

    declared = set(_annotations(contract.DecisionObject))
    declared |= set(_annotations(contract.EngineOutput))
    declared |= set(_annotations(contract.ErrorObject))

    undeclared = {}
    for path, varnames in CONSUMERS.items():
        extra = sorted(_keys_read(path, varnames) - declared)
        if extra:
            undeclared[path] = extra

    assert not undeclared, (
        "consumers read fields the contract does not declare:\n  "
        + "\n  ".join(f"{p}: {', '.join(k)}" for p, k in undeclared.items())
        + "\n\nEither the field was renamed and this consumer was missed, or "
          "the contract is out of date. Both are the failure T2-3 exists to "
          "prevent — check which before updating either."
    )


# ============================================================
# 3. The declaration has not gone stale
# ============================================================

def test_every_declared_field_is_actually_produced():
    """
    The contract must describe the engine, not the engine's history.

    Without this, a field removed from the producer stays in the contract
    forever and the declaration slowly becomes fiction — which is worse than no
    declaration, because it reads as documentation and is wrong.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    from core.decision_contract import DecisionObject, BtcContextBlock

    decision = _run_engine()
    assert "error" not in decision, decision.get("error")

    missing = []
    for field, ann in _annotations(DecisionObject).items():
        if field not in decision:
            missing.append(field)
            continue
        if _is_typed_dict(ann) and ann is not BtcContextBlock:
            # BtcContextBlock is total=False by design and legitimately
            # partial; every other block declares exactly what it produces.
            absent = sorted(set(_annotations(ann)) - set(decision[field]))
            missing.extend(f"{field}.{a}" for a in absent)

    assert not missing, (
        "the contract declares fields the engine does not produce:\n  "
        + ", ".join(missing)
        + "\n\nIf these were removed on purpose, remove them from "
          "core/decision_contract.py in the same commit."
    )


def test_the_scheduled_removals_are_still_present_and_still_scheduled():
    """
    SCHEDULED_FOR_REMOVAL names fields that exist today and are already agreed
    to be leaving. Each one must still be produced — the moment it is not, the
    contract has been left behind by the change it describes, and the fix is to
    delete it from the TypedDicts and from this dict in the same commit.

    It is empty as of sequence item 13, which removed the five position-sizing
    fields it held. The test is kept for the next entry, and it must not pass
    by having nothing to check while the dict is populated: an empty dict is a
    valid state, a populated dict with nothing produced is not.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    from core.decision_contract import SCHEDULED_FOR_REMOVAL

    if not SCHEDULED_FOR_REMOVAL:
        return                              # nothing scheduled; item 13 landed

    decision = _run_engine()
    assert "error" not in decision, decision.get("error")

    gone = [f"{block}.{field}"
            for (block, field) in SCHEDULED_FOR_REMOVAL
            if field not in decision.get(block, {})]

    assert not gone, (
        "fields listed as scheduled-for-removal are already gone: "
        + ", ".join(gone)
        + "\n\nRemove them from both the TypedDicts and SCHEDULED_FOR_REMOVAL "
          "in core/decision_contract.py — this test is the reminder to do it "
          "in the same commit rather than later."
    )


def test_the_aliases_the_contract_names_really_are_duplicates():
    """
    CANONICAL_ALIASES names the survivor wherever the object carries two names
    for one value. A claim in a docstring is worth nothing: if a declared pair
    ever stops being equal, the contract is telling new code to read a field
    that means something else. So the claim is checked against a real run.

    Empty as of sequence item 13. The two pairs it held — trend.health and
    trend.momentum — were removed rather than disambiguated, and
    tests/test_no_position_sizing.py asserts they stay gone.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    from core.decision_contract import CANONICAL_ALIASES

    if not CANONICAL_ALIASES:
        return

    decision = _run_engine()
    assert "error" not in decision, decision.get("error")

    diverged = []
    for (block, alias), canonical in CANONICAL_ALIASES.items():
        section = decision.get(block, {})
        if alias in section and canonical in section:
            if section[alias] != section[canonical]:
                diverged.append(
                    f"{block}.{alias}={section[alias]!r} but "
                    f"{block}.{canonical}={section[canonical]!r}"
                )

    assert not diverged, (
        "fields the contract calls duplicates now hold different values:\n  "
        + "\n  ".join(diverged)
        + "\n\nEither one of them acquired a real meaning — in which case it "
          "is not an alias and CANONICAL_ALIASES is wrong — or something "
          "assigns them separately. Either way, code told to prefer the "
          "canonical name is now reading the wrong number."
    )
