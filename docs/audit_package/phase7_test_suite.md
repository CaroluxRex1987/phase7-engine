# Phase-7 Structural Quant Engine — Complete Test Suite

Every test module, plus the runner. Section 7.3 of the audit brief asks you to
assess these specifically: most were written by the same author as the fixes
they certify.

Each file below is delimited by a `=== FILE: <path> ===` marker. Line
numbers are not included; cite locations by quoting the code itself.

---


=== FILE: tests/conftest.py ===

```python
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
    "core.decision_log",
    "core.engine_core",
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

```


=== FILE: tests/test_data_integrity.py ===

```python
"""
Item 3 — Data Integrity. Rated Critical. Fixed at sequence item 8.

The invariant names the defect classes by hand: "Missing candles, duplicated
candles, impossible prices, timestamp inconsistencies, NaN/Inf values, stale
data, malformed API responses, and abnormal volume must be detected before
they become analysis."

Nothing detected any of the first six. What existed instead was ffill/bfill,
which fills the defect in and carries on, so the engine could not distinguish
"no defect found" from "defect fabricated away."

THESE TESTS WERE WRITTEN TO FAIL, ON PURPOSE, AND NOW PASS. They were the
acceptance criteria for the fix; they are the regression guard after it. What
changed on 30 August is `_validate` below and nothing else — the corruption
each test introduces, and the assertion each makes, are as originally written.

Each corrupted fixture is a copy of the clean pinned dataset with exactly one
defect introduced, so a failure names one cause rather than a combination.
"""

import os
import tempfile

import pandas as pd

from conftest import fixture

CLEAN = "ohlcv_clean_4h.csv"

# The fixture is a 4h series. Passing this is what enables the interval and
# staleness checks; without it validate_ohlcv skips both rather than guessing
# the bar size.
TIMEFRAME = "4h"


def _load(name=CLEAN):
    return pd.read_csv(fixture(name))


def _write(df, tmpdir, name="corrupt.csv"):
    path = os.path.join(tmpdir, name)
    df.to_csv(path, index=False)
    return path


def _validate(path, now=None):
    """
    Ask the engine to accept or reject a CSV.

    v1 of this helper called the loader and reported what came back, because
    there was no validation entry point. Its docstring said: "When Item 3 is
    fixed, point this at the real validator; the tests themselves should not
    need changing."

    That is what happened. load_csv now records any Item 3 defect at
    .attrs["validation_error"], and this reads it. The bodies of the eight
    tests below are untouched.

    `now` is passed through. See test_rejects_stale_data for why staleness is
    the one check that needs it.
    """
    from data.data_fetcher import DataFetcher
    df = DataFetcher().load_csv(path, timeframe=TIMEFRAME, now=now)
    if isinstance(df, dict) and "error" in df:
        return False, df["error"]
    if hasattr(df, "attrs") and df.attrs.get("validation_error"):
        return False, df.attrs["validation_error"]
    return True, None


def _assert_rejected(path, defect, now=None):
    accepted, reason = _validate(path, now=now)
    assert not accepted, (
        f"{defect} was accepted without complaint.\n"
        "Item 3 requires this to be detected before it becomes analysis. "
        "Nothing currently detects it, so the corrupted values flow into "
        "EMA/RSI/ATR, then bias, entry quality, risk validation and the "
        "final decision."
    )


def test_rejects_a_missing_candle():
    """A four-hour gap in an otherwise continuous series."""
    df = _load()
    df = df.drop(index=200).reset_index(drop=True)
    with tempfile.TemporaryDirectory() as tmp:
        _assert_rejected(_write(df, tmp), "a missing candle (gap in the timestamp series)")


def test_rejects_a_duplicated_candle():
    """The same timestamp appearing twice."""
    df = _load()
    dup = df.iloc[[150]].copy()
    df = pd.concat([df.iloc[:151], dup, df.iloc[151:]]).reset_index(drop=True)
    with tempfile.TemporaryDirectory() as tmp:
        _assert_rejected(_write(df, tmp), "a duplicated candle")


def test_rejects_impossible_prices():
    """A candle whose high is below its low."""
    df = _load()
    df.loc[300, "high"] = df.loc[300, "low"] * 0.5
    with tempfile.TemporaryDirectory() as tmp:
        _assert_rejected(_write(df, tmp), "an impossible price (high below low)")


def test_rejects_negative_price():
    df = _load()
    df.loc[120, "close"] = -1.0
    with tempfile.TemporaryDirectory() as tmp:
        _assert_rejected(_write(df, tmp), "a negative close price")


def test_rejects_out_of_order_timestamps():
    """Two adjacent candles swapped, so the index is no longer monotonic."""
    df = _load()
    a, b = df.loc[100].copy(), df.loc[101].copy()
    df.loc[100], df.loc[101] = b, a
    with tempfile.TemporaryDirectory() as tmp:
        _assert_rejected(_write(df, tmp), "out-of-order timestamps")


def test_rejects_negative_volume():
    df = _load()
    df.loc[77, "volume"] = -5000.0
    with tempfile.TemporaryDirectory() as tmp:
        _assert_rejected(_write(df, tmp), "negative volume")


def test_rejects_stale_data():
    """
    Every candle is real and well formed, but the series ends two years ago.

    STALENESS IS THE ONE CHECK THAT NEEDS A REFERENCE TIME, and this test is
    where that shows.

    The clean fixture spans 2025-01-01 to 2025-03-16. As of 30 August 2026 its
    last candle is 531 days old; this test's corruption shifts it back another
    730, to 1261. A wall-clock threshold separating "clean" from "stale" would
    have to sit between those two numbers — and the clean fixture's age grows
    by one every day, so any constant chosen there expires.

    So validate_ohlcv takes `now` as a parameter and skips the check when it is
    omitted. A CSV on disk is not stale; it is historical. What would be stale
    is treating it as current, and only a caller knows whether it is doing
    that. fetch_ohlc passes the wall clock, because a live feed claiming to be
    current must be. This test passes a `now` anchored to the CLEAN fixture's
    own end, which makes the assertion durable: the clean data is current
    relative to that instant and the shifted data is two years behind it,
    forever, regardless of when the suite is run.

    Ruled by Viktor, 30 August 2026.
    """
    clean = _load()
    reference = pd.to_datetime(clean["timestamp"].iloc[-1], unit="ms")

    df = _load()
    df["timestamp"] = df["timestamp"] - (730 * 24 * 60 * 60 * 1000)
    with tempfile.TemporaryDirectory() as tmp:
        _assert_rejected(_write(df, tmp),
                         "stale data (last candle two years old)",
                         now=reference)


def test_clean_data_is_current_against_its_own_end():
    """
    The other half of the staleness rule, and the guard against the cheap way
    to pass the test above.

    A staleness check that rejected everything would satisfy
    test_rejects_stale_data perfectly. This is what stops that: the same clean
    fixture, measured against the same instant its own last candle sits at,
    must be accepted.

    Together the two pin the rule rather than one direction of it.
    """
    clean = _load()
    reference = pd.to_datetime(clean["timestamp"].iloc[-1], unit="ms")

    accepted, reason = _validate(fixture(CLEAN), now=reference)
    assert accepted, (
        f"the clean fixture was rejected when measured against its own last "
        f"candle: {reason}\n"
        "The staleness rule allows the most recent bar to be up to "
        "STALE_AFTER_BARS old. Data whose newest candle IS the reference "
        "instant is as current as data can be."
    )


def test_rejects_nan_in_close():
    """
    A NaN close price. This one is arguably worse than the others because
    the engine does not ignore it — indicators.py fills it in from a
    neighbouring bar and the fabricated value is then indistinguishable
    from a measurement.
    """
    df = _load()
    df.loc[250, "close"] = float("nan")
    with tempfile.TemporaryDirectory() as tmp:
        _assert_rejected(_write(df, tmp), "a NaN close price")


def test_accepts_clean_data():
    """
    The control. A validator that rejects everything is not a validator, so
    this must pass both before and after the fix.
    """
    accepted, reason = _validate(fixture(CLEAN))
    assert accepted, f"the clean pinned dataset was rejected: {reason}"


def test_each_defect_is_reported_by_its_own_name():
    """
    Detection is not enough; Item 3 says defects must be DETECTED, and a
    detector that reports every defect as "invalid data" has detected that
    something is wrong, not what.

    This matters for the same reason the A13 fix mattered: an engine that
    cannot distinguish a data outage from a quiet market will present both
    identically. A validator that cannot distinguish a duplicated candle from
    a negative price sends whoever is debugging it to read all 450 rows.

    Each corruption must produce a message naming its own defect class.
    """
    df = _load()
    cases = []

    d = df.copy(); d = d.drop(index=200).reset_index(drop=True)
    cases.append((d, ("interval", "gap"), "missing candle"))

    d = df.copy(); dup = d.iloc[[150]].copy()
    d = pd.concat([d.iloc[:151], dup, d.iloc[151:]]).reset_index(drop=True)
    cases.append((d, ("duplicat",), "duplicated candle"))

    d = df.copy(); d.loc[300, "high"] = d.loc[300, "low"] * 0.5
    cases.append((d, ("impossible",), "impossible candle"))

    d = df.copy(); d.loc[120, "close"] = -1.0
    cases.append((d, ("non-positive",), "negative price"))

    d = df.copy(); d.loc[77, "volume"] = -5000.0
    cases.append((d, ("negative volume",), "negative volume"))

    d = df.copy(); d.loc[250, "close"] = float("nan")
    cases.append((d, ("nan",), "NaN"))

    d = df.copy(); a, b = d.loc[100].copy(), d.loc[101].copy()
    d.loc[100], d.loc[101] = b, a
    cases.append((d, ("increasing order", "not in increasing"), "out-of-order timestamps"))

    vague = []
    with tempfile.TemporaryDirectory() as tmp:
        for i, (frame, needles, label) in enumerate(cases):
            _, reason = _validate(_write(frame, tmp, f"c{i}.csv"))
            text = (reason or "").lower()
            if not any(n.lower() in text for n in needles):
                vague.append(f"{label}: reported as {reason!r}")

    assert not vague, (
        "defects were detected but not named:\n  " + "\n  ".join(vague)
        + "\n\nA message that says only 'invalid data' tells whoever is "
          "debugging it to go and read 450 rows."
    )

```


=== FILE: tests/test_decision_contract.py ===

```python
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
        print("SKIP: pandas_ta not installed")
        return

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
        print("SKIP: pandas_ta not installed")
        return

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
        print("SKIP: pandas_ta not installed")
        return

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
        print("SKIP: pandas_ta not installed")
        return

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
        print("SKIP: pandas_ta not installed")
        return

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

```


=== FILE: tests/test_degraded_state.py ===

```python
"""
Sequence item 9a — Items 13 + 8, fail safely and epistemic honesty.

Viktor's ruling of 29 August, verbatim:

    "When an indicator fails, the engine continues in an explicitly degraded
     state. It must not fabricate replacement values. The failure must be
     recorded in the decision output, and confidence and trade quality must be
     reduced accordingly. A degraded result does not by itself authorize
     trading."

That ruling went against GLM's recommendation and against Claude's instinct.
Both preferred halting: it is cheaper, adds no machinery, and satisfies the
invariant's letter. GLM flagged its own preference as a habit shared with the
model family that built this engine, which is what made the choice Viktor's.

These tests are the ruling made checkable. Each of the four clauses gets one.

HOW A FAILURE IS SIMULATED

By making the indicator genuinely fail, not by hand-building a degraded object.
A test that constructs {"degraded": True} and checks the engine formats it
nicely proves the formatter works; it proves nothing about whether a real
pandas_ta exception ever reaches it.

So these patch the pandas_ta function to raise, and run the whole pipeline over
it.

WHICH INDICATOR TO BREAK, AND A TEST THAT WAS WRONG ABOUT IT

The first version of this file broke `ta.rsi` and asserted the run came back
degraded. It did not, and the code was right.

RSI, ATR and the EMAs each have a second computation path — a manual RSI, a
manual true range, pandas' own ewm(). Those are kept deliberately: they compute
the same quantity by another route, which is not the fabrication this item
removes. So breaking `ta.rsi` is recovered from, silently and correctly, and
the run is not degraded because nothing was lost.

ADX and SuperTrend have no second route. They are the ones that degrade.

The distinction is the whole point of item 9a — a fallback that recomputes the
same number is fine, a fallback that invents one is not — and the first draft
of this file did not encode it. test_a_recoverable_failure_does_not_degrade_the_run
now asserts it directly, so the two kinds of fallback cannot be confused again.
"""

import os

PINNED_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "fixtures", "pinned")
UNREACHABLE = "http://127.0.0.1:1"


def _engine_available():
    try:
        import pandas_ta  # noqa: F401
        return True
    except Exception:
        return False


def _pinned_frame():
    from data.data_fetcher import DataFetcher, data_fetcher
    original = data_fetcher.base_url
    try:
        data_fetcher.base_url = UNREACHABLE
        DataFetcher.set_pinned_source(PINNED_DIR)
        return data_fetcher.get_tf("AEROUSDT", "4h", limit=300)
    finally:
        DataFetcher.clear_pinned_source()
        data_fetcher.base_url = original


def _run_with_broken(indicator):
    """
    Run the engine end to end with one pandas_ta function raising.

    Patched on the ta module the indicators import, and restored in a finally.
    The alternative — deleting a column after the fact — would test that
    downstream code tolerates absence, not that the failure is detected and
    reported where it happens.
    """
    import indicators.indicators as ind
    from data.data_fetcher import DataFetcher, data_fetcher
    from models.signal_router import SignalRouter

    def explode(*a, **k):
        raise RuntimeError(f"simulated {indicator} failure")

    original_fn = getattr(ind.ta, indicator)
    original_url = data_fetcher.base_url
    try:
        setattr(ind.ta, indicator, explode)
        data_fetcher.base_url = UNREACHABLE
        DataFetcher.set_pinned_source(PINNED_DIR)
        return SignalRouter().route(symbol="AEROUSDT", timeframe="4h")
    finally:
        setattr(ind.ta, indicator, original_fn)
        DataFetcher.clear_pinned_source()
        data_fetcher.base_url = original_url


# ============================================================
# "It must not fabricate replacement values"
# ============================================================

def test_a_failed_indicator_leaves_no_column_behind():
    """
    The clause the other three rest on.

    Before 9a every failure wrote a constant: RSI 50.0, ADX 25.0, ATR 2% of
    price, SuperTrend = close, ST_Direction = 1.0 (bullish). Nothing downstream
    could tell those from measurements.

    A dropped column can be detected. A plausible number cannot.
    """
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return

    import indicators.indicators as ind

    df = _pinned_frame()
    original = ind.ta.adx
    try:
        ind.ta.adx = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom"))
        frame, failures = ind.add_technical_indicators(df)
    finally:
        ind.ta.adx = original

    assert "ADX" not in frame.columns, (
        "a failed ADX still produced an ADX column. Whatever is in it was not "
        "measured, and nothing downstream can tell."
    )
    assert any(f.indicator == "ADX" for f in failures), (
        f"ADX failed but was not reported. Failures: {[f.indicator for f in failures]}"
    )


def test_the_failure_names_the_indicator_and_the_consequence():
    """
    "Recorded" has to mean legible. An operator reading the panel needs to know
    which reading to distrust, which a traceback does not tell them.
    """
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return

    import indicators.indicators as ind

    df = _pinned_frame()
    original = ind.ta.supertrend
    try:
        ind.ta.supertrend = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom"))
        _frame, failures = ind.add_technical_indicators(df)
    finally:
        ind.ta.supertrend = original

    assert failures, "SuperTrend failed and nothing was recorded"
    text = str(failures[0])
    assert "SuperTrend" in text and "RuntimeError" in text and "—" in text, (
        f"the failure record is not legible: {text!r}\n"
        "It must name the indicator, why it failed, and what the engine loses."
    )


# ============================================================
# "The failure must be recorded in the decision output"
# ============================================================

def test_the_decision_object_reports_the_degradation():
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return

    decision = _run_with_broken("adx")
    assert "error" not in decision, (
        f"the engine halted instead of degrading: {decision.get('error')}\n"
        "Viktor ruled degrade, not halt. A failed ADX must not end the run."
    )

    block = decision.get("degradation", {})
    assert block.get("degraded") is True, (
        f"ADX was broken but the run does not report itself degraded: {block}"
    )
    assert any("ADX" in m for m in block.get("missing_inputs", [])), (
        f"the degradation block does not name ADX: {block.get('missing_inputs')}"
    )


def test_a_recoverable_failure_does_not_degrade_the_run():
    """
    The distinction item 9a rests on, made checkable.

    A fallback that recomputes the same quantity by another route is not a
    fabrication. RSI has a manual calculation, ATR has a manual true range, the
    EMAs have pandas' own ewm(). When pandas_ta fails on one of those, the
    engine computes the real number a different way and nothing is lost — so
    nothing is reported lost.

    ADX and SuperTrend have no second route, which is why the tests around this
    one break those instead.

    Without this test the two kinds of fallback look identical from outside,
    and the first draft of this file confused them: it broke ta.rsi, expected a
    degraded run, and reported the CODE as failing when the test was wrong.
    """
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return

    decision = _run_with_broken("rsi")

    assert "error" not in decision, (
        f"breaking ta.rsi ended the run: {decision.get('error')}\n"
        "The manual RSI calculation should have covered it."
    )

    block = decision.get("degradation", {})
    assert block.get("degraded") is False, (
        f"breaking ta.rsi marked the run degraded: {block}\n"
        "RSI was recomputed by the manual path, so nothing was lost. Marking "
        "this degraded would block trading on a run that measured everything "
        "it claims to — and would make the degraded flag mean 'something "
        "raised somewhere' rather than 'an input is missing'."
    )


def test_a_clean_run_is_not_marked_degraded():
    """
    The control. A flag that is always on is not a flag, and it would make the
    trading block below permanent — which is halting, wearing the degrade
    ruling's clothes.
    """
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return

    from data.data_fetcher import DataFetcher, data_fetcher
    from models.signal_router import SignalRouter

    original = data_fetcher.base_url
    try:
        data_fetcher.base_url = UNREACHABLE
        DataFetcher.set_pinned_source(PINNED_DIR)
        decision = SignalRouter().route(symbol="AEROUSDT", timeframe="4h")
    finally:
        DataFetcher.clear_pinned_source()
        data_fetcher.base_url = original

    block = decision.get("degradation", {})
    assert block.get("degraded") is False, (
        f"a clean run on sound pinned data reports itself degraded: {block}"
    )
    assert block.get("trading_authorized") is True, (
        "a clean run is not authorized to trade, which would make the "
        "degradation gate permanent"
    )


# ============================================================
# "Confidence and trade quality must be reduced accordingly"
# ============================================================

def test_confidence_and_trade_quality_are_capped_when_degraded():
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return

    from models.decision_model import DecisionModel

    ceiling = DecisionModel.DEGRADED_CONFIDENCE_CEILING
    decision = _run_with_broken("adx")
    risk = decision.get("risk", {})

    assert risk.get("confidence_score", 0.0) <= ceiling, (
        f"confidence is {risk.get('confidence_score')} on a degraded run, "
        f"above the {ceiling} ceiling"
    )
    assert risk.get("trade_quality_current", 0.0) <= ceiling, (
        f"trade quality (current market) is {risk.get('trade_quality_current')} "
        f"on a degraded run, above the {ceiling} ceiling"
    )
    assert risk.get("trade_quality_proposed", 0.0) <= ceiling, (
        f"trade quality (proposed entry) is "
        f"{risk.get('trade_quality_proposed')} on a degraded run, above the "
        f"{ceiling} ceiling"
    )


# ============================================================
# "A degraded result does not by itself authorize trading"
# ============================================================

def test_a_degraded_run_cannot_authorize_a_trade():
    """
    The load-bearing sentence of the ruling, and the one that makes degrading
    safe rather than merely more informative than halting.
    """
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return

    decision = _run_with_broken("adx")

    assert decision["degradation"]["trading_authorized"] is False, (
        "a degraded run reports trading as authorized"
    )

    action = decision.get("exit", {}).get("action", "")
    assert not any(side in action for side in ("LONG", "SHORT")), (
        f"a degraded run produced the action {action!r}, which names a side.\n"
        "Viktor's ruling: a degraded result does not by itself authorize "
        "trading. The analysis may still be published; the trade may not."
    )


def test_the_reasoning_says_why_out_loud():
    """
    A structural field a consumer might not read is not the same as telling the
    operator. The reason belongs in the prose they actually see.
    """
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return

    decision = _run_with_broken("adx")
    reasons = " ".join(decision.get("explanation", {}).get("reasons", []))

    assert "DEGRADED" in reasons.upper(), (
        "the decision reasoning does not mention that the run was degraded.\n"
        f"Reasons: {reasons}"
    )
    assert "ADX" in reasons, (
        "the reasoning says the run was degraded but not by what"
    )


# ============================================================
# Sequence item 9b — the last fabrication
# ============================================================

def test_a_failed_risk_calculation_does_not_invent_levels():
    """
    risk_model.calculate_stop_targets' except used to return "safe default
    fallback bounds": a stop at price x 0.99 and targets at 1.01, 1.02, 1.03.

    DIRECTION-BLIND. The stop sits 1% BELOW price and the targets ABOVE it,
    whatever the bias said — so on a short the stop is where the trade would be
    winning and every target is where it would be losing. The panel printed
    them as STOP LOSS and TARGET 1/2/3, with R:R ratios computed off them.

    Nor were they safe: a 1% stop on an instrument whose ATR is 4% is a stop
    inside the noise, and the 1/2/3% targets encode a reward profile that has
    nothing to do with this market.

    This is the only fabrication in the codebase that produced a
    TRADEABLE-LOOKING ARTEFACT rather than a wrong indicator reading, which is
    why it is tested by side rather than merely by presence.
    """
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return

    from models.risk_model import RiskModel

    model = RiskModel()

    # Force the failure from inside the try, by handing it an input the body
    # cannot work with. atr_val=None raises TypeError at the first comparison.
    #
    # The first draft of this test patched classify_risk_regime instead —
    # which calculate_stop_targets never calls; it belongs to
    # validate_risk_parameters. Nothing raised, the function returned real
    # levels, and the assertion below fired correctly on a test that had not
    # broken anything. Second time in item 9 that the test was wrong and the
    # code was right, which is its own small lesson about injecting failures
    # at a point you have actually confirmed is on the path.
    raised = None
    try:
        model.calculate_stop_targets(
            detailed_bias="BEARISH CONFIRMED",   # a SHORT
            trend_health=80.0,
            current_price=100.0,
            atr_val=None,
            structural_level=None,
            bias_score=-70.0,
        )
    except Exception as e:
        raised = e

    assert raised is not None, (
        "a failed stop/target calculation returned levels instead of raising.\n"
        "Whatever came back was not computed from this market, and the panel "
        "cannot tell — it prints a STOP LOSS and three TARGETs either way."
    )
    assert "risk plan" in str(raised).lower(), (
        f"the failure does not say what was lost: {raised}"
    )


def test_the_engine_reports_a_failed_risk_plan_rather_than_inventing_one():
    """
    End to end. The exception must reach the operator as a reported failure,
    not vanish into a handler that supplies levels of its own.
    """
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return

    import models.risk_model as rm
    from data.data_fetcher import DataFetcher, data_fetcher
    from models.signal_router import SignalRouter

    original = rm.RiskModel.calculate_stop_targets
    original_url = data_fetcher.base_url
    try:
        rm.RiskModel.calculate_stop_targets = lambda *a, **k: (
            _ for _ in ()
        ).throw(ValueError("simulated stop/target failure"))
        data_fetcher.base_url = UNREACHABLE
        DataFetcher.set_pinned_source(PINNED_DIR)
        decision = SignalRouter().route(symbol="AEROUSDT", timeframe="4h")
    finally:
        rm.RiskModel.calculate_stop_targets = original
        DataFetcher.clear_pinned_source()
        data_fetcher.base_url = original_url

    assert "error" in decision, (
        "the engine produced a normal decision object despite the stop/target "
        f"calculation failing. Keys: {sorted(decision)}\n"
        "That means something downstream supplied levels the market did not."
    )
    assert "risk" not in decision or not decision.get("risk", {}).get("targets"), (
        "the decision carries targets after the calculation that produces them "
        "failed"
    )


# ============================================================
# Sequence item 9c — the dead trend_failure gate
# ============================================================

def test_the_dead_trend_failure_gate_stays_removed():
    """
    `trend_failure` tested whether the last five values of the STRUCTURE column
    equalled "LH" or "LL". structure.py writes regime labels — "BULLISH TREND",
    "BEARISH TREND", "NEUTRAL STRUCTURE" — and never those two, so the flag was
    False on every run this engine has ever made.

    It was not one dead branch. Four modules acted on it: entry_model blocked
    entries, bias_engine halved the bias score, exit_model raised a watch flag,
    and the router published it as trend.failure. In each case it sat beside a
    live signal, so every block, discount and flag those lines ever produced
    came from something else.

    DELETED RATHER THAN WIRED. The audit found a gate that never fires, not a
    specification for one that should. Choosing when to block a trade is a
    trading decision, and wiring it would produce a behaviour change this
    project cannot yet evaluate — the golden baseline proves a change is
    attributable, never that it is correct, and backtesting sits behind the
    release gate. Recorded in claude/phase7-rulings.md.

    This guard exists because "restore the trend failure check" is an obvious
    thing for someone to do later, and doing it as a restoration rather than as
    a designed feature would bring back the same dead comparison.
    """
    import ast
    import inspect

    import indicators.trend_health as th
    import models.bias_engine as be
    import models.entry_model as em
    import models.exit_model as xm
    from core.decision_contract import TrendBlock

    # The parameter is gone from both consumers that took it.
    for fn in (em.generate_entry_signals, be.calculate_dynamic_bias):
        assert "trend_failure" not in inspect.signature(fn).parameters, (
            f"{fn.__name__} accepts trend_failure again. Nothing produces it."
        )

    # And from the published shape.
    assert "failure" not in TrendBlock.__annotations__, (
        "trend.failure is declared in the contract again. A field the engine "
        "does not compute must not be published as though it does."
    )

    # No module computes or reads it. Checked on the AST so a comment
    # explaining the removal does not count as a reference.
    offenders = []
    for module in (th, be, em, xm):
        src = inspect.getsource(module)
        for node in ast.walk(ast.parse(src)):
            if isinstance(node, ast.Name) and node.id == "trend_failure":
                offenders.append(module.__name__)
                break
            if (isinstance(node, ast.Constant) and node.value == "trend_failure"):
                offenders.append(module.__name__)
                break

    assert not offenders, (
        "trend_failure is back in: " + ", ".join(sorted(set(offenders)))
        + "\nIf structural-failure detection is wanted, it needs a real "
          "producer and its own justification — not the old comparison "
          "against labels structure.py has never written."
    )

```


=== FILE: tests/test_execution_surface.py ===

```python
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

```


=== FILE: tests/test_exit_model_removal.py ===

```python
"""
Sequence item 5b — removing compute_exit and engine_core's render path.

WHY THIS IS A SEPARATE FILE FROM test_no_dead_columns.py

5a deleted indicator columns and inherited a single output-invariance proof for
all of them. 5b is a different kind of change: it removes a function that was
called on every run, and it removes a parameter from a public method signature.
Both turn out to be output-invariant too, but that had to be established rather
than assumed, and the reasoning is per-item rather than blanket.

A CORRECTION, RECORDED HERE BECAUSE IT IS ALREADY IN A PUSHED COMMIT

The 5a commit message and the docstring of test_no_dead_columns.py both said
compute_exit "is called at engine_core.py:889 and its output feeds at least
eight sites across four files — current_price is read in five places and action
in three, including live_trading's simulated order."

The line number was 529, not 889. More importantly, the second half traced
names rather than data. Eight references to a variable called `exit_data` do
exist, but seven of them are not reading compute_exit's output.
signal_router.py:265 builds a fresh dict:

    "exit": {
        "action": final_action,                     # <- DecisionModel's
        "current_price": float(exit_data.get("current_price", 0.0)),
    }

`final_action` there is dm_result["final_action"] from decision_model.py.
compute_exit also returned a key called `final_action`, and the two were
conflated. The `action` reads in panel_render and live_trading were always
reading DecisionModel.

The conclusion — handle it separately from 5a — was still right, because a
refactor should not ride inside a cleanup on borrowed proof. The stated reason
for it was wrong.

WHAT COMPUTE_EXIT ACTUALLY CONTRIBUTED

Six returned keys. Five (final_action, exit_reason, stop_loss, target_hit,
exit_status) were computed on every run and discarded one call later. The panel
does print a stop loss, but reads risk["atr_stop"].

The sixth, current_price, was float(price_data["close"].iloc[-1]) where
price_data=df_struct — the identical expression engine_core had already
evaluated at the top of its section 8, on the same frame. df_struct is assigned
once and never reassigned, so the values were equal by construction. It is now
passed through directly.

THE RENDER PATH

engine_core.run() took render: bool = True, and the only caller passed
render=False. So the panel engine_core could print was unreachable from every
entry point. Removing compute_exit made it worse than unused: the panel reads
its DECISION line from exit["action"], which only the router supplies, so the
raw object would have fallen through to the literal default and printed "WAIT"
on every run regardless of analysis. Before 5b it fell through to compute_exit
and printed an exit verdict under a decision heading.

Either way it is the panel asserting a decision nothing computed — the Item 6
family. Deleted under Item 16. Ruled by Viktor, 30 August 2026.
"""

import ast
import inspect
import os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PINNED_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "fixtures", "pinned")


def _engine_available():
    try:
        import pandas_ta  # noqa: F401
        return True
    except Exception:
        return False


def _source(rel):
    with open(os.path.join(REPO_ROOT, rel), encoding="utf-8") as f:
        return f.read()


def test_compute_exit_is_gone():
    """
    The regression guard. Restoring it means restoring five outputs nothing
    reads plus a duplicate of a value the engine already has.
    """
    import models.exit_model as exit_model

    assert not hasattr(exit_model, "compute_exit"), (
        "compute_exit is back in models/exit_model.py. Five of its six return "
        "values were discarded by signal_router before anything downstream saw "
        "them, and the sixth duplicated engine_core's own current_price. If "
        "the engine now needs exit management, that is a real feature and "
        "belongs in its own commit with its own justification — not restored "
        "as a side effect."
    )


def test_build_exit_watch_survives():
    """
    The other half. build_exit_watch is the advisory-flag function, it is
    consumed, and it lives in the same file compute_exit was deleted from —
    exactly the shape of a cleanup that takes one thing too many.
    """
    import models.exit_model as exit_model

    assert hasattr(exit_model, "build_exit_watch"), (
        "build_exit_watch has gone missing from models/exit_model.py. It is "
        "consumed: engine_core calls it and its output is the panel's Exit "
        "Watch section."
    )


def test_engine_core_has_no_render_parameter():
    """
    Signature-level, so it fails at import rather than at some later run.
    """
    from core.engine_core import Phase7Engine

    params = inspect.signature(Phase7Engine.run).parameters
    assert "render" not in params, (
        "Phase7Engine.run has a `render` parameter again. Rendering belongs to "
        "SignalRouter, which owns the only complete decision object. A panel "
        "built from engine_core's raw output has no DECISION to show and will "
        "print the fallback literal instead."
    )


def test_engine_core_does_not_render():
    """
    Stronger than the signature check: the import and the calls must both be
    gone, or a later change can quietly reintroduce rendering without a
    parameter to notice.
    """
    src = _source(os.path.join("core", "engine_core.py"))
    tree = ast.parse(src)

    imported = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            for a in node.names:
                if a.name == "render_panel":
                    imported.append(node.module)

    called = [
        n for n in ast.walk(tree)
        if isinstance(n, ast.Call)
        and isinstance(n.func, ast.Name)
        and n.func.id == "render_panel"
    ]

    assert not imported and not called, (
        "core/engine_core.py renders again "
        f"(imports from: {imported or 'none'}; call sites: {len(called)}).\n"
        "engine_core returns a decision object; the router assembles the "
        "complete one and renders it. Two renderers means two panels that can "
        "disagree, and the engine's would be the one with no DECISION."
    )


def test_the_dead_hit_literals_are_gone_from_the_panel():
    """
    Item 16, and a small honesty point.

    panel_render coloured "TARGET 1/2/3 HIT" green and "STOP LOSS HIT" red.
    Those four strings could only come from compute_exit, which the router
    discarded, so the comparisons never matched. A reader of that file would
    reasonably conclude the panel can report a target being hit.
    """
    src = _source(os.path.join("core", "panel_render.py"))

    # Strip comments — the removal is documented in prose in that file, and the
    # explanation necessarily names the strings it is explaining.
    code_only = "\n".join(
        line.split("#", 1)[0] for line in src.splitlines()
    )

    resurrected = [s for s in ("TARGET 1 HIT", "TARGET 2 HIT", "TARGET 3 HIT",
                               "STOP LOSS HIT") if s in code_only]

    assert not resurrected, (
        "dead action literals are back in core/panel_render.py: "
        + ", ".join(resurrected) +
        "\nNothing produces these. DecisionModel emits WAIT, NO-TRADE (RISK "
        "TOO HIGH), LONG/SHORT and the AGGRESSIVE/CONSERVATIVE variants."
    )


def test_current_price_survives_the_removal():
    """
    The invariance check that matters, done live rather than by inspection.

    compute_exit's one consumed output was the last close of the structure
    frame. engine_core now supplies it directly. If those ever differ, every
    R:R ratio on the panel is computed against the wrong price — panel_render
    derives its risk distance from this value.
    """
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return

    from data.data_fetcher import DataFetcher, data_fetcher
    from models.signal_router import SignalRouter

    data_fetcher.base_url = "http://127.0.0.1:1"   # nothing may reach the network
    try:
        DataFetcher.set_pinned_source(PINNED_DIR)
        decision = SignalRouter().route(symbol="AEROUSDT", timeframe="4h")
    finally:
        DataFetcher.clear_pinned_source()

    assert "error" not in decision, decision.get("error")

    reported = float(decision["exit"]["current_price"])

    import pandas as pd
    pinned = pd.read_csv(os.path.join(PINNED_DIR, "AEROUSDT_4h.csv"))
    expected = float(pinned["close"].iloc[-1])

    assert reported == expected, (
        f"decision['exit']['current_price'] is {reported}, but the last close "
        f"in the pinned series is {expected}.\n"
        "These were the same value before 5b because compute_exit recomputed "
        "the same expression on the same frame. If they have diverged, "
        "engine_core is sourcing current_price from somewhere else."
    )

```


=== FILE: tests/test_explicit_configuration.py ===

```python
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
        print("SKIP: pandas_ta not installed")
        return

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

```


=== FILE: tests/test_frame_ownership.py ===

```python
"""
Sequence item 6 — T2-1, shared-frame aliasing, and the two caches.

THE PRINCIPLE, STATED AS A TEST

A function that is handed a DataFrame does not own it. If it needs to change
the data, it works on its own copy. The caller's frame is the same afterwards
as it was before.

This is not stylistic. The engine passes one frame through eight stages, and a
module that quietly edits it changes the inputs of every stage after it. The
edits in question were all NaN-fills, so they would not raise — the engine
would keep producing confident numbers computed from data a later stage had
silently rewritten.

WHAT WAS FIXED

  models/bias_engine.py        calculate_dynamic_bias took `df` and never read
                               it. Its only use of the frame was to fill NaNs in
                               four columns, three of which it does not read.
                               A write-only parameter. Deleted, not copied —
                               copying would have left a no-op behind.

  structure/structure.py       calculate_structure had a copy_df flag that
                               defaulted to True; both call sites passed False.
                               The parameter is gone; it always copies now. A
                               knob whose unsafe setting is the one everybody
                               chooses is not a safeguard.

  indicators/volume_profile.py compute_volume_profile cleaned low/high/volume on
                               the caller's frame, and its inf-replacement ran
                               on every call rather than only when something was
                               wrong. Now copies.

  utils/plotting.py            plot_engine_chart filled NaNs in the OHLC columns
                               of the frame it was asked to draw. Now copies.

The last two were not named in the Step 5 plan. They are the same class, found
while fixing the two that were.

  core/engine_core.py          _indicator_cache and _structure_cache deleted.
                               They never returned a hit in any production path,
                               and on the one reachable hit path the cached
                               frame was mutated in place.

WHY THIS IS OUTPUT-INVARIANT

Every one of those writes is conditional on NaN or non-finite values, except
volume_profile's inf-replacement, which is a no-op on finite data. Data that
has been through add_technical_indicators has neither. So on any real run they
did nothing, and the decision-object snapshot proves it.

That is also what made them dangerous rather than merely wrong: they had never
fired, so nothing had ever gone visibly wrong, so there was no pressure to look
at them.

NOT FIXED HERE. Two of those fills are also fabrications:
bias_engine substituted the close price for a missing RSI (a price into a 0-100
oscillator), and volume_profile substitutes zero for a missing high or low.
Item 6 stops them writing into frames they do not own; sequence item 9 is where
the fallbacks are given honest semantics. Recorded as riders there.
"""

import ast
import inspect
import os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PINNED_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "fixtures", "pinned")


def _engine_available():
    try:
        import pandas_ta  # noqa: F401
        return True
    except Exception:
        return False


def _dirty_frame():
    """
    Real pinned data, run through the indicator pipeline, then damaged.

    The damage is the point: a NaN in each column these functions used to
    repair, plus one inf. A function that still wants to write to its input
    will do it here. Clean data would prove nothing, because every one of these
    writes was conditional on exactly the defects being injected.

    Real data rather than a synthetic ramp, because the structure engine has to
    be able to analyse it — otherwise a failure to process would look like a
    failure of ownership.
    """
    import numpy as np

    from data.data_fetcher import DataFetcher
    from indicators.indicators import add_technical_indicators

    fetcher = DataFetcher()
    fetcher.base_url = "http://127.0.0.1:1"
    try:
        DataFetcher.set_pinned_source(PINNED_DIR)
        df = fetcher.get_tf("AEROUSDT", "4h", limit=300)
    finally:
        DataFetcher.clear_pinned_source()

    df, _failures = add_technical_indicators(df)   # (frame, failures) since 9a

    # Damage a handful of interior rows. Not the last row — several callers
    # read .iloc[-1] and the test is about ownership, not about their
    # tolerance for a missing final candle.
    df.loc[df.index[5], "close"] = np.nan
    df.loc[df.index[6], "high"] = np.nan
    df.loc[df.index[7], "low"] = np.nan
    df.loc[df.index[8], "volume"] = np.inf
    df.loc[df.index[9], "EMA_20"] = np.nan
    df.loc[df.index[10], "RSI"] = np.nan
    return df


def _unchanged(before, after):
    """
    pandas' .equals treats NaN in the same position as equal, which is exactly
    the comparison wanted here — the frame must come back with its damage
    intact, not repaired.
    """
    return list(before.columns) == list(after.columns) and before.equals(after)


def test_calculate_structure_does_not_touch_the_callers_frame():
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return

    from structure.structure import calculate_structure

    df = _dirty_frame()
    before = df.copy(deep=True)
    calculate_structure(df, lookback=8)

    assert _unchanged(before, df), (
        "calculate_structure modified the frame it was given.\n"
        "It writes STRUCTURE, HVN and LVN and fills the OHLCV columns. Those "
        "belong on its own copy — the caller's frame is the input to every "
        "later stage of the engine."
    )


def test_compute_volume_profile_does_not_touch_the_callers_frame():
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return

    from indicators.volume_profile import compute_volume_profile

    df = _dirty_frame()
    before = df.copy(deep=True)
    compute_volume_profile(df)

    assert _unchanged(before, df), (
        "compute_volume_profile modified the frame it was given.\n"
        "It is asked for a read-only summary. Its inf-replacement used to run "
        "on every call, so this fired even on clean data."
    )


def test_plot_engine_chart_does_not_touch_the_callers_frame():
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return

    try:
        import matplotlib
        matplotlib.use("Agg")
    except Exception:
        pass                    # the suite already renders charts headless
    from utils.plotting import plot_engine_chart

    df = _dirty_frame()
    before = df.copy(deep=True)
    plot_engine_chart(
        df=df,
        entry_data={"entry_zone_lower": 100.0, "entry_zone_upper": 105.0},
        risk_data={"atr_stop": 95.0, "targets": (110.0, 115.0, 120.0)},
        save_path=os.path.join(REPO_ROOT, "Logs", "Charts", "_ownership_test.png"),
    )

    assert _unchanged(before, df), (
        "plot_engine_chart modified the frame it was given.\n"
        "engine_core passes df_struct to it — the frame the whole analysis was "
        "computed from. A renderer must not edit what it renders."
    )


def test_plotting_does_not_swallow_a_broken_repair_path():
    """
    The companion to the test above, which passed VACUOUSLY on its first run.

    plot_engine_chart's NaN repair called fillna(method='ffill') — an API
    pandas has since removed. It raised TypeError, the function's own
    try/except caught it and logged "Failed to plot candlesticks", and the
    chart rendered with EMAs, entry zone, stop and targets but no price
    candles. The ownership test above still passed, because a frame that was
    never touched is trivially unmodified.

    That is the shape to watch for: a guard satisfied by the failure it exists
    to detect.

    This test watches the log instead of the frame. plot_engine_chart contains
    nine separate try/excepts that downgrade errors to log lines, so a silent
    failure inside it cannot be seen from the return value — it returns the
    save path whether or not the candles were drawn.
    """
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return

    import logging

    try:
        import matplotlib
        matplotlib.use("Agg")
    except Exception:
        pass
    from utils.plotting import plot_engine_chart

    records = []

    class _Collect(logging.Handler):
        def emit(self, record):
            records.append(record)

    plotting_logger = logging.getLogger("utils.plotting")
    handler = _Collect()
    plotting_logger.addHandler(handler)
    try:
        plot_engine_chart(
            df=_dirty_frame(),
            entry_data={"entry_zone_lower": 0.75, "entry_zone_upper": 0.78},
            risk_data={"atr_stop": 0.64, "targets": (0.96, 1.12, 1.28)},
            save_path=os.path.join(REPO_ROOT, "Logs", "Charts", "_repair_test.png"),
        )
    finally:
        plotting_logger.removeHandler(handler)

    problems = [r.getMessage() for r in records if r.levelno >= logging.ERROR]

    assert not problems, (
        "plot_engine_chart logged an error while rendering a frame with NaNs:\n  "
        + "\n  ".join(problems) +
        "\nEvery drawing step in that function is wrapped in a try/except that "
        "downgrades failures to log lines, so the chart is still written and "
        "still returned — just missing whatever failed. A chart with no price "
        "candles looks like a chart."
    )


def test_calculate_dynamic_bias_takes_no_frame():
    """
    Signature-level. The frame parameter was write-only: the function filled
    NaNs in four of the caller's columns and read none of them.

    Restoring it as a copy-taking parameter would be worse than the bug — a
    parameter that is accepted, copied, cleaned and discarded.
    """
    from models.bias_engine import calculate_dynamic_bias

    params = inspect.signature(calculate_dynamic_bias).parameters
    assert "df" not in params, (
        "calculate_dynamic_bias has a `df` parameter again. It computes its "
        "score entirely from scalar arguments; the frame was write-only."
    )


def test_calculate_structure_has_no_copy_opt_out():
    """
    The parameter, not just its value. Leaving copy_df=True as a default would
    have left the unsafe path one keyword away, and it is the path both call
    sites took for as long as it existed.
    """
    from structure.structure import calculate_structure

    params = inspect.signature(calculate_structure).parameters
    assert "copy_df" not in params, (
        "calculate_structure accepts copy_df again. Every call site passed "
        "False the last time this existed."
    )


def test_the_engine_holds_no_caches():
    """
    Item 4/12 dissolved by repair rather than adjudication.

    A reintroduced cache is not automatically wrong, but it would reopen a
    dispute two audit runs disagreed about, so it should not arrive quietly.
    """
    from core.engine_core import Phase7Engine

    engine = Phase7Engine()
    cache_attrs = [a for a in vars(engine) if "cache" in a.lower()]

    assert not cache_attrs, (
        f"Phase7Engine has cache attributes again: {', '.join(cache_attrs)}.\n"
        "The previous two never returned a hit in any production path — one "
        "router, one route, then process exit — and the hit path they did have "
        "mutated the cached frame in place. If a cache is genuinely needed now, "
        "it needs its own justification and a test that proves it is coherent "
        "under mutation."
    )


def test_engine_core_does_not_reference_a_cache():
    """
    Stronger than the attribute check: a cache built as a module-level dict or
    a closure would not show up in vars(engine).
    """
    with open(os.path.join(REPO_ROOT, "core", "engine_core.py"), encoding="utf-8") as f:
        tree = ast.parse(f.read())

    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            names.add(node.id)
        elif isinstance(node, ast.Attribute):
            names.add(node.attr)

    offenders = sorted(n for n in names if "cache" in n.lower())

    assert not offenders, (
        f"core/engine_core.py refers to caching again: {', '.join(offenders)}."
    )

```


=== FILE: tests/test_golden_path.py ===

```python
"""
Golden-path regression test.

Runs the engine end to end against pinned data and compares the decision object
to a stored snapshot. Any change that alters what the engine decides fails this
test and prints the exact fields that moved.

This is the test that makes the remaining fixes safe to attempt. Without it, a
change to bias weighting, the confidence formula or the risk model can silently
alter every decision the engine makes and nothing notices.

Constitution: Tier 3, item 4 (regression tests) and item 5 (fixed evaluation
datasets).

    Re-baseline:  set PHASE7_UPDATE_SNAPSHOT=1
                  python run_tests.py golden
                  (writes the baseline; commit it, and say why in the message)
    Normally:     python run_tests.py golden

Revision history for this file, because it matters:

    v1  Written blind — pandas_ta could not be installed in the authoring
        environment, so it had never run. Marked unverified.
    v2  First real run, 2026-08-28, on Viktor's machine. The test was wrong: it
        called Phase7Engine.run() directly, bypassing SignalRouter and therefore
        DecisionModel. Fixed to route the way main.py does, and to give BTC a
        distinct price series instead of correlating the asset with itself.
    v3  Sequence item 7, 2026-08-30. Three changes, below.


V3, AND WHY EACH PART OF IT
===========================

1. IT NO LONGER MONKEYPATCHES THE CLASS

   v2 did `DataFetcher.get_tf = pinned` — replacing a method on the shared class
   for the duration of the test. That is the same disease sequence item 6 spent
   a commit removing: reaching into something you do not own and changing it for
   everyone. It was guarded by try/finally, so it was contained, but it was also
   the last instance of the pattern in the suite.

   More to the point, it tested the wrong thing. The engine's real data path is
   DataFetcher.set_pinned_source() -> get_tf() -> _load_pinned(), built at
   sequence item 3. A test that replaces get_tf entirely never exercises any of
   it — so the baseline was pinned against a code path production does not use.

   v3 writes three CSVs to a temporary directory and points the real pinned
   source at it. Everything below that is the production path.

2. IT CONTROLS THE C3 STATE FILE

   engine_core persists {supertrend_direction, detailed_bias} to
   Logs/phase7_state_{symbol}_{timeframe}.json after every run, and the next run
   compares against it to produce two of the Exit Watch flags. exit_watch is IN
   the decision object, so the snapshot was a function of run history as well as
   of input.

   In practice it had been stable, for a reason that is luck rather than design:
   both "no state file" and "state file agrees with this run" produce no flags.
   Only a disagreement produces one, and on fixed data nothing disagreed.

   That luck is exactly the shape that breaks on a fresh clone, in CI, or the
   first time someone runs the engine on TESTUSDT by hand. It was visible in the
   29 August smoke output as

       Bias state changed from NEUTRAL to BULLISH CONFIRMED since the last run

   appearing in one run of the suite and not the next.

   v3 deletes the state file before every run, so exit_watch is a function of
   the input alone. GLM's own note on this item asked for exactly this.

3. THE UNREACHABLE-FETCH GUARD PATCHES THE INSTANCE

   From the plan, verbatim: "the data_fetcher singleton binds base_url at import
   — patch the instance, not just config." engine_core imports the module-scope
   singleton, so setting config does nothing to the object doing the fetching.

   Belt and braces: the pinned source already refuses to fall back to the live
   API on a missing series. This makes an unpinned fetch fail at the socket
   rather than at the market.


WHAT THIS BASELINE MUST NOT DO
------------------------------
Two tests in this file are EXPECTED TO FAIL. They document the hardcoded "AERO"
string and the doubled "relationship relationship", both scheduled for sequence
item 12. The snapshot records the engine's current output, defects included —
that is what a baseline is — but the two named defects have their own failing
assertions so that "the snapshot matches" can never be mistaken for "the output
is correct".

A baseline captured while something is quietly broken pins the broken behaviour
as the reference. That happened for real on 30 August: the chart renderer's NaN
repair had been raising and being swallowed for as long as anyone can tell, and
a baseline taken the day before would now be the standard.
"""

import json
import os
import shutil
import tempfile

from conftest import fixture, REPO_ROOT

SNAPSHOT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "fixtures", "golden_decision.json")

# TESTUSDT, not AEROUSDT, on purpose: it is what makes
# test_explanation_does_not_name_a_hardcoded_symbol meaningful. Running the
# golden path on AERO would let the hardcoded string pass unnoticed.
SYMBOL = "TESTUSDT"
TIMEFRAME = "4h"
MACRO_TIMEFRAME = "1d"

# A port nothing listens on. Any fetch that escapes the pinned source dies here
# instead of reaching a live exchange and making the run irreproducible.
UNREACHABLE = "http://127.0.0.1:1"

# Fields excluded from comparison because they legitimately differ between runs
# on identical input. Anything not listed here is expected to be stable.
VOLATILE = {"chart_path", "timestamp", "generated_at"}


def _engine_available():
    try:
        import pandas_ta  # noqa: F401
        return True
    except Exception:
        return False


def _strip(obj):
    if isinstance(obj, dict):
        return {k: _strip(v) for k, v in obj.items() if k not in VOLATILE}
    if isinstance(obj, (list, tuple)):
        return [_strip(v) for v in obj]
    if isinstance(obj, float):
        return round(obj, 8)
    return obj


# ============================================================
# The pinned set
# ============================================================

def _write_pinned_set(directory):
    """
    Derive three series from the one committed fixture and write them where the
    real pinned loader will find them.

    Derived rather than committed so there is a single source of truth: change
    ohlcv_clean_4h.csv and all three move together. The derivations are pure
    functions of it, so the set is byte-identical on every machine.

    TESTUSDT_4h   the fixture verbatim — the series under analysis
    TESTUSDT_1d   a real daily aggregate of it, for the macro-confluence read
    BTCUSDT_4h    a distinct but plausible series, for BTC context
    """
    import pandas as pd

    base = pd.read_csv(fixture("ohlcv_clean_4h.csv"))
    base.to_csv(os.path.join(directory, f"{SYMBOL}_{TIMEFRAME}.csv"), index=False)

    # --- macro: six 4h candles make one day ---
    #
    # v2 returned the SAME 450-row 4h series for the macro timeframe, because
    # its monkeypatch ignored the timeframe argument entirely. So the macro
    # confluence check compared the asset against a 50-period EMA of itself on
    # the wrong timeframe and called the answer a daily trend.
    groups = base.index // 6
    daily = base.groupby(groups).agg(
        timestamp=("timestamp", "first"),
        open=("open", "first"),
        high=("high", "max"),
        low=("low", "min"),
        close=("close", "last"),
        volume=("volume", "sum"),
    ).reset_index(drop=True)
    daily.to_csv(os.path.join(directory, f"{SYMBOL}_{MACRO_TIMEFRAME}.csv"), index=False)

    # --- BTC: same shape, different path ---
    #
    # Reversing the row order gives a genuinely different price path while
    # keeping every candle internally consistent (high >= low still holds,
    # because whole rows move together). Returning the same frame for every
    # symbol would correlate the asset with itself and report beta 1.00x and
    # correlation +1.00, which says nothing about the engine.
    btc = base.copy()
    for col in ("open", "high", "low", "close"):
        btc[col] = btc[col].to_numpy()[::-1] * 137_000.0
    btc["volume"] = btc["volume"].to_numpy()[::-1] * 3.0
    btc.to_csv(os.path.join(directory, f"BTCUSDT_{TIMEFRAME}.csv"), index=False)


# ============================================================
# The C3 state file
# ============================================================

def _state_path(symbol=SYMBOL, timeframe=TIMEFRAME):
    from core import config
    log_dir = config.LOG_DIR
    return os.path.join(REPO_ROOT, log_dir,
                        f"phase7_state_{symbol}_{timeframe}.json")


def _clear_state():
    """No prior run. Both flip flags are skipped, deterministically."""
    try:
        os.remove(_state_path())
    except FileNotFoundError:
        pass
    except OSError:
        pass


def _seed_state(**values):
    """A known prior run, for the tests that exercise the flip flags."""
    path = _state_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(values, f)


def _run(seed=None):
    """
    One engine run through the production path, on pinned data, with the
    network unreachable and the C3 state under the test's control.

    seed=None deletes the state file (no prior run). A dict seeds it.
    """
    from data.data_fetcher import DataFetcher, data_fetcher
    from models.signal_router import SignalRouter

    if seed is None:
        _clear_state()
    else:
        _seed_state(**seed)

    tmp = tempfile.mkdtemp(prefix="phase7_golden_")
    original_url = data_fetcher.base_url
    try:
        _write_pinned_set(tmp)
        data_fetcher.base_url = UNREACHABLE
        DataFetcher.set_pinned_source(tmp)
        return SignalRouter().route(symbol=SYMBOL, timeframe=TIMEFRAME)
    finally:
        DataFetcher.clear_pinned_source()
        data_fetcher.base_url = original_url
        shutil.rmtree(tmp, ignore_errors=True)


# ============================================================
# The baseline
# ============================================================

def test_decision_object_matches_snapshot():
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return

    raw = _run()
    assert "error" not in raw, (
        f"the engine reported an error on pinned data: {raw.get('error')}\n"
        "A baseline cannot be captured from a failed run."
    )
    decision = _strip(raw)

    if os.environ.get("PHASE7_UPDATE_SNAPSHOT"):
        os.makedirs(os.path.dirname(SNAPSHOT), exist_ok=True)
        with open(SNAPSHOT, "w") as f:
            json.dump(decision, f, indent=2, sort_keys=True, default=str)
        print(f"snapshot written: {SNAPSHOT}")
        return

    assert os.path.exists(SNAPSHOT), (
        "no baseline snapshot exists yet. Create one with:\n"
        "    set PHASE7_UPDATE_SNAPSHOT=1\n"
        "    python run_tests.py golden\n"
        "then commit tests/fixtures/golden_decision.json"
    )

    with open(SNAPSHOT) as f:
        expected = json.load(f)

    actual = json.loads(json.dumps(decision, sort_keys=True, default=str))

    if actual != expected:
        diffs = []
        for key in sorted(set(expected) | set(actual)):
            a, b = expected.get(key, "<missing>"), actual.get(key, "<missing>")
            if a != b:
                diffs.append(f"  {key}:\n    was: {a}\n    now: {b}")
        raise AssertionError(
            "the engine's decision changed on identical input:\n"
            + "\n".join(diffs)
            + "\n\nIf the change was intended, re-baseline with "
              "PHASE7_UPDATE_SNAPSHOT=1 and say so in the commit message."
        )


def test_the_snapshot_covers_every_top_level_field():
    """
    A baseline is only as good as its coverage.

    If a future change drops a whole section from the decision object, the
    comparison above catches it — but only while the snapshot still contains
    that section. Re-baselining after an accidental deletion would bake the
    deletion in and this file would go quiet about it.

    So the expected shape is asserted independently of the stored file.
    """
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return
    if not os.path.exists(SNAPSHOT):
        print("SKIP: no baseline yet")
        return

    with open(SNAPSHOT) as f:
        stored = json.load(f)

    required = {
        "symbol", "timeframe", "macro_bias",
        "bias", "trend", "structure", "entry", "risk",
        "exit", "exit_watch", "btc_context", "explanation",
    }
    missing = sorted(required - set(stored))

    assert not missing, (
        "the stored baseline is missing decision-object sections: "
        + ", ".join(missing) +
        "\nEither the engine stopped producing them and the snapshot was "
        "re-baselined without anyone noticing, or this list is out of date. "
        "Check which before updating either."
    )


def _run_without(filename):
    """A run whose pinned set is missing one file. Used to prove it was read."""
    from data.data_fetcher import DataFetcher, data_fetcher
    from models.signal_router import SignalRouter

    _clear_state()
    tmp = tempfile.mkdtemp(prefix="phase7_golden_")
    original_url = data_fetcher.base_url
    try:
        _write_pinned_set(tmp)
        os.remove(os.path.join(tmp, filename))
        data_fetcher.base_url = UNREACHABLE
        DataFetcher.set_pinned_source(tmp)
        return SignalRouter().route(symbol=SYMBOL, timeframe=TIMEFRAME)
    finally:
        DataFetcher.clear_pinned_source()
        data_fetcher.base_url = original_url
        shutil.rmtree(tmp, ignore_errors=True)


def test_the_macro_series_is_actually_read():
    """
    Proof that v3's rewiring is live, rather than an argument that it is.

    v3 moved this file off a class-level monkeypatch and onto the real pinned
    source, and gave the macro timeframe a genuine daily series instead of the
    4h series v2 handed it by accident. The snapshot did not move. That is a
    legitimate outcome — the fixture is a sustained uptrend, so `close > EMA_50`
    is BULLISH on either timeframe, and everything downstream was already
    identical because the 4h series is the same file.

    It is also exactly what a test that had silently stopped reading its input
    would look like. The two are indistinguishable from the snapshot alone, so
    this asserts the difference directly: remove the macro file and the macro
    read must change.

    WHAT THIS EXPOSES, recorded rather than fixed. A macro fetch that fails does
    not raise and does not mark the run degraded — engine_core validates the
    frame, and on failure leaves macro_bias at its initialised "NEUTRAL". So a
    missing timeframe and a genuinely directionless market produce the same
    word, and the panel prints MACRO TREND: NEUTRAL either way.

    That is the fabricated-fallback pattern: a real value and a failure sharing
    a representation. It belongs to sequence item 9 under the degrade ruling —
    a failed input must be reported as a failure, not silently rendered as a
    neutral reading. Rider recorded there.
    """
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return

    with_macro = _run().get("macro_bias")
    without_macro = _run_without(f"{SYMBOL}_{MACRO_TIMEFRAME}.csv").get("macro_bias")
    _clear_state()

    assert with_macro != without_macro, (
        f"deleting {SYMBOL}_{MACRO_TIMEFRAME}.csv from the pinned set did not "
        f"change macro_bias (both {with_macro!r}).\n"
        "The macro timeframe is therefore not being read from the pinned "
        "source, and the golden baseline is pinned against a data path the "
        "engine does not use."
    )
    assert without_macro == "NEUTRAL", (
        f"a missing macro series produced macro_bias={without_macro!r}, "
        f"expected 'NEUTRAL'.\nIf engine_core has learned to report this "
        f"failure honestly, that is sequence item 9 landing and this "
        f"expectation should be updated to match."
    )


def test_engine_is_deterministic_on_identical_input():
    """
    Constitution Tier 1, item 4 (Determinism).

    Two runs on the same pinned data, in the same process.

    This is stronger than it was in v2. The caches it was written to catch are
    gone as of sequence item 6, but the C3 state file is a second channel for
    run history to leak into output, and v2 did not control it — the first run
    wrote state that the second read. It passed because both runs agreed, which
    is the answer you get when the leak is real but benign.
    """
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return

    first = _strip(_run())
    second = _strip(_run())

    if first != second:
        diffs = [k for k in set(first) | set(second) if first.get(k) != second.get(k)]
        raise AssertionError(
            "two runs on identical input produced different results.\n"
            f"fields that differ: {', '.join(sorted(diffs))}"
        )


# ============================================================
# C3 — the cross-run comparison flags
# ============================================================

def test_a_bias_flip_against_prior_state_is_reported():
    """
    The first test of the C3 feature itself.

    Two of the eight Exit Watch flags are comparisons against the previous run,
    read from a state file. Nothing tested that they fire — the golden path
    only ever saw the no-prior-state case, where they are correctly silent.
    Silence is also what a broken comparison produces.
    """
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return

    actual_bias = _run().get("bias", {}).get("detailed", "")
    assert actual_bias, "the run produced no detailed bias to compare against"

    # A prior state that cannot match whatever the run produces.
    prior = "BEARISH CONFIRMED" if "BULL" in actual_bias.upper() else "BULLISH CONFIRMED"
    flags = " ".join(_run(seed={"detailed_bias": prior}).get("exit_watch", []))

    assert prior in flags and "Bias state changed" in flags, (
        f"seeded a prior bias of {prior!r} and ran to {actual_bias!r}, but no "
        f"bias-flip flag was raised.\nExit Watch said: {flags or '(nothing)'}\n"
        "Either the state file is not being read, or the comparison is broken. "
        "Both fail silently in normal use, because 'no flag' is also what "
        "agreement looks like."
    )
    _clear_state()


def test_a_supertrend_flip_against_prior_state_is_reported():
    """
    The other half. SuperTrend direction is ±1, so seeding both signs must
    produce exactly one flag: the run's own direction matches one and opposes
    the other.

    Asserting EXACTLY one is what makes this a test. "At least one" would pass
    if the flag fired unconditionally, which is the opposite defect and just as
    wrong.
    """
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return

    fired = []
    for direction in (1.0, -1.0):
        flags = " ".join(_run(seed={"supertrend_direction": direction}).get("exit_watch", []))
        if "SuperTrend flipped" in flags:
            fired.append(direction)
    _clear_state()

    assert len(fired) == 1, (
        f"seeded both SuperTrend directions; the flip flag fired for {fired} "
        f"— expected exactly one.\n"
        "Zero means the comparison never runs. Two means it fires regardless "
        "of the prior value, which would put a flag on the panel on every run."
    )


# ============================================================
# Known defects, scheduled for sequence item 12
# ============================================================

def test_explanation_does_not_name_a_hardcoded_symbol():
    """
    Constitution Tier 4, item 2 (generalization over historical fit) — rated
    Compliant by the audit on the grounds that "the symbol is a parameter" and
    the scan report covers seven assets.

    That holds for the arithmetic. It does not hold for the prose.

    models/decision_model.py hardcodes "AERO" into user-facing reasoning text at
    lines 411, 413 and 419:

        f"...agreeing with AERO's own bias"
        f"...AERO and BTC have a {correlation_label.lower()} relationship..."

    So running the engine on SOLUSDT produces an explanation that talks about
    AERO. Running it on BTCUSDT produces one claiming to compare AERO against
    BTC while actually comparing BTC to itself.

    core/panel_render.py:83 has the same shape — decision.get("symbol",
    "AEROUSDT") — so a decision object without a symbol renders as AERO rather
    than as an error.

    Found 2026-08-28 by running the engine on TESTUSDT and reading the panel.
    Missed by all four audit runs, because none of them ran it.

    EXPECTED TO FAIL until sequence item 12.
    """
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return

    decision = _run()
    reasons = " ".join(decision.get("explanation", {}).get("reasons", []))
    btc = decision.get("btc_context", {}) or {}
    btc_reasons = " ".join(
        (btc.get("btc_adjusted", {}) or {}).get("reasons", [])
        if isinstance(btc.get("btc_adjusted"), dict) else []
    )
    haystack = (reasons + " " + btc_reasons + " " + str(btc)).upper()

    assert "AERO" not in haystack, (
        "the engine was run on TESTUSDT and its explanation names AERO.\n"
        "Symbol names are hardcoded in models/decision_model.py (lines 411, "
        "413, 419) and core/panel_render.py (line 83).\n"
        "Fix: interpolate the symbol under analysis, or say 'this asset'."
    )


def test_correlation_phrase_is_not_doubled():
    """
    btc_context returns labels that already end in the word "relationship" —
    e.g. "WEAK / NO CLEAR RELATIONSHIP" — and decision_model appends
    " relationship" to them, producing:

        "a weak / no clear relationship relationship"

    Cosmetic, but it appears in output the trader reads, and it is one line to
    fix.

    EXPECTED TO FAIL until sequence item 12.
    """
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return

    decision = _run()
    btc = decision.get("btc_context", {}) or {}
    text = str(btc).lower()

    assert "relationship relationship" not in text, (
        "the BTC reasoning contains a doubled word: 'relationship relationship'.\n"
        "models/decision_model.py:419 appends ' relationship' to a label that "
        "already ends in it."
    )

```


=== FILE: tests/test_imports.py ===

```python
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

```


=== FILE: tests/test_no_circular_reasoning.py ===

```python
"""
Sequence item 11 — Item 11, No Circular Reasoning. The third Critical.

THE DEFECT

`trend_health` reached the confidence score by three separate routes, and the
panel printed it three times:

  direct       confidence = ... + trend_health * 0.3
  via bias     trend_health * 0.30 -> bias_score -> bias_strength * 0.5 -> conf
  via          val_score = trend_health  (engine_core), then +-5/+10/-15
  validation   -> validation_state -> validation_adj -> confidence

  rendering    TREND: 95.35 / MOMENTUM: STRONG (95.35) / Current Market: 95.35

One measurement, presented as several agreeing signals. The validation path is
the sharpest: a validation score seeded with the thing it validates is not
evidence, it is a restatement.

THE TEST STEP 5 ASKED FOR

"perturb trend_health, assert confidence moves exactly once."

That is what the first two tests below do, and the pair matters. Asserting the
direct term is gone would also pass on a formula that ignored every input, so
the control asserts confidence still responds to the one path that is allowed
to carry trend health — bias strength.
"""

import ast
import os

from conftest import REPO_ROOT


def _confidence(trend_health, bias_score=60.0):
    """
    One confidence score, with everything but trend_health held fixed.

    Called directly rather than through the engine on purpose: at engine level
    trend_health legitimately moves bias_score, so a whole-pipeline test could
    not distinguish "removed the direct term" from "removed nothing".
    """
    from models.decision_model import DecisionModel

    return DecisionModel()._compute_confidence(
        bias={"score": bias_score, "raw": "BULLISH"},
        trend={"trend_health": trend_health},
        structure={"regime": "BULLISH TREND"},
        risk={"validation_state": "NEUTRAL"},
        final_action="LONG",
        reasons=[],
    )


def test_confidence_does_not_read_trend_health_directly():
    """
    With bias held fixed, trend health must not move confidence at all.

    Before this item, spanning 0 to 100 moved it by 30 points — on top of
    whatever the same measurement had already contributed through bias_score.
    """
    scores = {th: _confidence(th) for th in (0.0, 25.0, 50.0, 75.0, 100.0)}
    distinct = sorted(set(round(v, 9) for v in scores.values()))

    assert len(distinct) == 1, (
        "confidence changed when only trend_health changed:\n  "
        + "\n  ".join(f"trend_health={k:>5} -> confidence={v:.4f}"
                      for k, v in scores.items())
        + "\n\nTrend health reaches confidence through bias_score, at weight "
          "0.30 inside bias_engine. Any additional term counts one measurement "
          "twice and reports a number agreeing with itself as corroboration."
    )


def test_confidence_still_moves_with_bias_strength():
    """
    The control, and the reason the test above is not vacuous.

    A _compute_confidence that returned a constant would satisfy the previous
    assertion perfectly. This one fails if the single permitted path has been
    severed along with the duplicate.
    """
    weak = _confidence(50.0, bias_score=10.0)
    strong = _confidence(50.0, bias_score=90.0)

    assert strong > weak, (
        f"confidence did not increase with bias strength "
        f"({weak:.2f} at score 10, {strong:.2f} at score 90).\n"
        "Trend health is supposed to reach confidence through exactly one "
        "route. Zero routes is not the fix."
    )


def test_confidence_can_still_reach_the_top_of_its_range():
    """
    Removing a 30-point term without rescaling would cap confidence at 70.

    That matters beyond tidiness: _compute_ev consumes confidence as a rough
    win rate. A percentage that cannot reach its own maximum understates every
    expected value computed from it, which is a quiet way to be wrong.
    """
    best = _confidence(50.0, bias_score=100.0)
    from models.decision_model import DecisionModel

    ceiling = DecisionModel()._compute_confidence(
        bias={"score": 100.0, "raw": "BULLISH"},
        trend={"trend_health": 50.0},
        structure={"regime": "BULLISH TREND"},
        risk={"validation_state": "STRONG"},
        final_action="LONG",
        reasons=[],
    )

    assert ceiling >= 99.0, (
        f"the best possible case scores {ceiling:.1f}/100 — maximum bias "
        f"strength, structure agreeing, validation strong. If the top of the "
        f"scale is unreachable the number is not a percentage."
    )
    assert best > 0.0


def test_validation_is_not_seeded_with_trend_health():
    """
    The third path, and the one that most deserved the word "circular".

    `val_score = trend_health` meant the validation score WAS trend health,
    nudged. It then re-entered confidence as an independent-looking term, and
    the panel showed it on its own VALIDATION line.

    Checked on the AST rather than by running the engine: the assignment's
    right-hand side must be a literal, not a name borrowed from elsewhere.
    """
    with open(os.path.join(REPO_ROOT, "core", "engine_core.py"), encoding="utf-8") as f:
        tree = ast.parse(f.read())

    seeds = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "val_score":
                    seeds.append(node.value)

    assert seeds, "val_score is no longer assigned in engine_core — has the check moved?"

    first = seeds[0]
    assert isinstance(first, ast.Constant), (
        f"val_score is initialised from {ast.dump(first)[:80]} rather than a "
        f"literal.\nA validation score derived from the measurement it "
        f"validates is a restatement, not evidence — and it reaches confidence "
        f"a second time through validation_adj."
    )


def test_the_panel_prints_trend_health_once():
    """
    Item 10(a), merged into this item because it is the same defect rendered.

    TREND, MOMENTUM's number and Current Market were all the same value. A
    reader seeing three numbers agree reasonably concludes three things agree.
    """
    with open(os.path.join(REPO_ROOT, "core", "panel_render.py"), encoding="utf-8") as f:
        source = f.read()

    code_only = "\n".join(line.split("#", 1)[0] for line in source.splitlines())
    renders = code_only.count("trend_health_score")

    # One extraction, one render.
    assert renders <= 2, (
        f"trend_health_score appears {renders} times in panel_render code.\n"
        "It should be extracted once and printed once, on the TREND line. "
        "MOMENTUM's label (STRONG / BUILDING / EXTENDED) is momentum_mode and "
        "is a genuinely separate reading; its number was not."
    )

    assert "Current Market" not in code_only, (
        "the Current Market line is back. It rendered trade_quality_current, "
        "which was trend_health verbatim under a third name."
    )


def test_the_reasoning_no_longer_claims_trend_health_as_a_confidence_input():
    """
    Step 5's coupling rule: "the reason strings change in the same commit —
    prose describing the old formula is an Item 8 regression the moment the
    number changes."

    The sentence used to read "Confidence is X/100 — bias strength is Y/100,
    trend health is Z/100, ...", naming as an input the exact term this item
    removed.
    """
    from models.decision_model import DecisionModel

    reasons = []
    DecisionModel()._compute_confidence(
        bias={"score": 60.0, "raw": "BULLISH"},
        trend={"trend_health": 95.0},
        structure={"regime": "BULLISH TREND"},
        risk={"validation_state": "NEUTRAL"},
        final_action="LONG",
        reasons=reasons,
    )

    text = " ".join(reasons)
    assert "95" not in text, (
        f"the confidence explanation still quotes the trend health value:\n"
        f"  {text}\n"
        "It is not an input to this score. Prose describing a calculation that "
        "no longer runs is the Item 8 regression the coupling rule exists to "
        "prevent."
    )

```


=== FILE: tests/test_no_dead_columns.py ===

```python
"""
Sequence item 5a — proving the deletions were safe, and keeping them deleted.

Item 16 forbids unconsumed complexity. The audit found the engine computing
indicator columns that nothing read: Bollinger Bands, the ADX directional
indicators, Typical_Price, KAMA and two of the four slope columns. All written
every run, all read nowhere.

Deleting unconsumed code has an unusually strong verification available:
**output-invariance**. If the engine's decision object is identical before and
after, nothing consumed what was removed. That is a proof, not an argument —
and it is why item 5 was sequenced after items 3 and 4, which built the pinned
data path and the smoke run that make it possible.

The invariance proof itself was performed once, at the time of deletion, by
capturing the decision object on pinned data before and after and comparing.
It cannot be re-run now, because the "before" no longer exists. What these
tests do instead is the durable half: assert the columns stay gone, and assert
the ones that survived are still produced.

WHAT WAS NOT DONE HERE. Step 5's item 5 also listed `compute_exit` for
deletion. It was excluded and handled as 5b, so that a refactor could not ride
inside a cleanup on borrowed proof.

CORRECTION, 30 August 2026. This docstring originally justified that exclusion
by saying compute_exit "is called at engine_core.py:889 and its output feeds at
least eight sites across four files — current_price is read in five places and
action in three, including live_trading's simulated order." The line was 529,
and the rest traced names rather than data: signal_router.py:265 builds its own
"exit" dict, so the `action` those sites read is DecisionModel's, not
compute_exit's. Two dicts shared a key name and I conflated them. The decision
to split was still right; the reason given for it was not. See
test_exit_model_removal.py for the corrected trace.
"""

import os

from conftest import fixture

PINNED_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "fixtures", "pinned")

# Removed at sequence item 5a. Each was written on every run and read by
# nothing — verified by scanning every module for a read before deletion.
DELETED_COLUMNS = [
    "BB_lower", "BB_middle", "BB_upper",   # Bollinger trio
    "DIP", "DIM",                          # ADX directional indicators
    "Typical_Price",                       # (H+L+C)/3, input to VWAP and CCI
    "KAMA",                                # only consumer was its own slope
    "KAMA_Slope", "VWMA_Slope",            # produced, never read
]

# Kept, and load-bearing. If a future cleanup takes one of these, the engine
# breaks quietly rather than loudly — trend_health falls back to 0.0 slopes
# and entry_model scores VWMA distance against a column that is not there.
KEPT_COLUMNS = [
    "EMA_20", "EMA_50",
    "EMA20_Slope",    # trend_health.py reads it in three places
    "EMA50_Slope",    # trend_health.py:1711
    "VWMA",           # entry_model distance scoring
    "ADX",            # trend_health and bias both read it
    "RSI", "ATR", "SuperTrend", "ST_Direction",
]


def _engine_available():
    try:
        import pandas_ta  # noqa: F401
        return True
    except Exception:
        return False


def _indicator_frame():
    """Run the indicator pipeline over the pinned base series."""
    from data.data_fetcher import DataFetcher
    from indicators.indicators import add_technical_indicators

    fetcher = DataFetcher()
    fetcher.base_url = "http://127.0.0.1:1"      # nothing should reach the network
    try:
        DataFetcher.set_pinned_source(PINNED_DIR)
        df = fetcher.get_tf("AEROUSDT", "4h", limit=300)
        assert df.attrs.get("fetch_error") is None, df.attrs.get("fetch_error")
        # SEQUENCE ITEM 9a: add_technical_indicators now returns
        # (frame, failures). Failures are asserted on separately in
        # test_degraded_state.py; this file is about columns.
        frame, _failures = add_technical_indicators(df)
        return frame
    finally:
        DataFetcher.clear_pinned_source()


def test_deleted_columns_stay_deleted():
    """
    The regression guard for item 5a.

    Without this, someone restoring "the Bollinger Bands we used to have"
    reintroduces three columns nothing reads, and Item 16 quietly goes
    Non-compliant again with nothing to notice it.
    """
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return

    df = _indicator_frame()
    resurrected = [c for c in DELETED_COLUMNS if c in df.columns]

    assert not resurrected, (
        "columns removed at sequence item 5a have come back: "
        + ", ".join(resurrected) +
        "\nThey were deleted because nothing read them. If something reads "
        "one now, that is a real change and belongs in its own commit with "
        "its own justification — not restored as a side effect."
    )


def test_consumed_columns_are_still_produced():
    """
    The other half, and the more important one.

    A deletion pass that removes something load-bearing does not necessarily
    crash: trend_health guards its slope reads with `if "EMA20_Slope" in
    df.columns else 0.0`, so removing that column would silently zero the
    slope contribution to trend health rather than raising. The engine would
    keep producing confident-looking numbers computed from less than it
    claims.

    That is exactly the failure class this project keeps finding, so it gets a
    test rather than a comment.
    """
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return

    df = _indicator_frame()
    missing = [c for c in KEPT_COLUMNS if c not in df.columns]

    assert not missing, (
        "indicator columns the engine actually consumes are missing: "
        + ", ".join(missing) +
        "\nNote that trend_health guards its slope reads with a default of "
        "0.0, so a missing slope column degrades the score silently instead "
        "of raising."
    )


def test_slope_columns_are_not_all_zero():
    """
    Presence is not production.

    `EMA20_Slope` surviving as a column of zeros would pass the test above and
    still mean trend health is computed from nothing. Pinned data has real
    price movement, so a real slope calculation cannot be flat.
    """
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return

    df = _indicator_frame()
    for col in ["EMA20_Slope", "EMA50_Slope"]:
        assert (df[col] != 0.0).any(), (
            f"{col} is entirely zero on pinned data that has real price "
            f"movement — the slope loop is present but not computing."
        )

```


=== FILE: tests/test_no_lookahead.py ===

```python
"""
Sequence item 15 — Item 2 (No Future Information / Look-Ahead Bias), and the
half of item 9a that was hiding one layer down.

THE INVARIANT

    "Information unavailable at the exact decision timestamp must never
     influence that decision, whether directly or through a derived signal."

And the Constitution's own note on it:

    Item 2 "deserves the most explicit, deliberate checking of any invariant in
    this document once [backtesting] starts, since a backtest with a hidden
    look-ahead leak is the single most common way a system convinces itself it
    works when it doesn't."

That note is why this is a sequence item of its own rather than a line in
item 9. The plan files it under "backtest on-ramp".

WHAT WAS ACTUALLY THERE — AND AN HONEST GRADING OF IT

Nine `.bfill()` calls fed decisions. None of them was a LIVE leak, and the
report should say so plainly rather than borrow severity it has not earned:
the engine makes exactly one decision, at the last bar of a 450-row frame.
Nothing exists after that bar to leak backwards from, and `bfill` only ever
fires on the leading edge — `ffill` covers every later gap. The contaminated
rows sit four hundred bars behind every window the decision reads.

The leak is latent. It becomes live on the day a backtest walks the decision
timestamp backwards, with no code change to blame it on. That is the whole
argument for clearing it now, while the cost is nine lines.

THE PART THAT WAS NOT LATENT

`clean_series` ended with

    if series.isna().any():
        median_val = series.median()
        series = series.fillna(median_val if isfinite(median_val) else 0.0)

so an indicator that came back entirely NaN left that function as a column of
ZEROS. The callers' guards read

    rsi = clean_series(ta.rsi(...))
    if rsi is None or rsi.isna().all():        # already false
        raise ValueError("pandas_ta returned no usable RSI")

`isna().all()` could not be true, because the NaNs were gone before the check
ran. A completely failed RSI became 0 on every bar — maximum oversold. A
completely failed ATR became 0, which is a stop distance of zero.

Item 9a removed the fabricated constants from the `except` branches and did not
look inside the helper the success path ran through. Its tests injected failures
by RAISING, so the returns-nothing-usable path was never exercised and the
guards were never watched to see whether they could fire. Test 4 below is the
one that would have caught it.

Two more of the same shape, found by reading every fill rather than every
`bfill`:

  indicators.py  VWMA  `.fillna(close_prices)` — the identical substitution
                       item 9a removed from the except branch eight lines
                       below, where the surviving comment explains that it
                       "invented the most favourable number available": a zero
                       VWMA distance and a perfect 20 of 20 entry points.
  volume_profile       `.fillna(0)` on low/high — item 9's recorded leftover.
                       The profile bins between price_min and price_max, so one
                       zeroed low drags the range to the origin and the HVN
                       that comes out is a structural level at a price that
                       never traded. engine_core hands that to
                       calculate_stop_targets.

WHAT IS DELIBERATELY UNCHANGED

utils/plotting.py still backfills. It draws a picture and feeds no decision.
Test 7 pins that as a decision rather than an oversight — it fails if the
exemption spreads to a module that does feed a decision.
"""

import ast
import os

import numpy as np
import pandas as pd

from conftest import REPO_ROOT, fixture

# The one module allowed to fill from a later row, and why.
BACKFILL_EXEMPT = {"utils/plotting.py"}

PINNED_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "fixtures", "pinned")
UNREACHABLE = "http://127.0.0.1:1"


def _engine_available():
    try:
        import pandas_ta  # noqa: F401
        return True
    except Exception:
        return False


def _clean_series():
    """
    clean_series, imported without dragging pandas_ta in.

    indicators.py imports pandas_ta at module scope, so the tests that only
    exercise this one pure function would otherwise skip on a machine without
    it — and those are the tests that pin the defect most precisely.
    """
    src = open(os.path.join(REPO_ROOT, "indicators", "indicators.py"),
               encoding="utf-8").read()
    start = src.index("def clean_series")
    end = src.index("def pct_slope")
    ns = {"pd": pd, "np": np}
    exec(src[start:end], ns)
    return ns["clean_series"]


def _ohlcv():
    return pd.read_csv(fixture("ohlcv_clean_4h.csv"))


# ============================================================
# 1–3. The helper itself
# ============================================================

def test_a_gap_is_never_filled_from_a_later_row():
    """
    The direct statement of Item 2 at the smallest scale there is.

    Position 0 has no past. Whatever comes out of it must not be the value that
    first appears at position 5.
    """
    clean_series = _clean_series()

    series = pd.Series([np.nan] * 5 + [10.0, 11.0, 12.0, 13.0, 14.0])
    out = clean_series(series, method="forward_fill")

    leading = out.iloc[:5]
    assert leading.isna().all(), (
        f"the first five values have no past to be filled from and came back "
        f"as {list(leading)}. 10.0 is the value at position 5 — a bar in their "
        f"future. This is Item 2 at its smallest scale."
    )
    assert list(out.iloc[5:]) == [10.0, 11.0, 12.0, 13.0, 14.0], (
        "the forward half of the fill was damaged"
    )


def test_an_interior_gap_is_still_filled_forward():
    """
    The other half, and the reason this is a change rather than a deletion.

    Carrying the last known value forward uses only the past. Removing that as
    well would have made the fix look thorough and left the engine unable to
    tolerate a single missing bar.
    """
    clean_series = _clean_series()

    out = clean_series(pd.Series([1.0, 2.0, np.nan, np.nan, 5.0]),
                       method="forward_fill")

    assert list(out) == [1.0, 2.0, 2.0, 2.0, 5.0], (
        f"an interior gap should carry 2.0 forward; got {list(out)}"
    )


def test_an_all_nan_series_comes_back_all_nan():
    """
    The one that matters most, and the one item 9a needed.

    This returned a column of ZEROS. Every caller's `isna().all()` guard was
    therefore reading a series with no NaNs in it and could not fire.
    """
    clean_series = _clean_series()

    out = clean_series(pd.Series([np.nan] * 20), method="forward_fill")

    assert out.isna().all(), (
        f"an all-NaN series came back as {out.unique()}. Callers guard on "
        f"`isna().all()` and that guard is now false, so a completely failed "
        f"indicator passes as a real reading of zero — maximum oversold for "
        f"RSI, no trend at all for ADX, and for ATR a stop distance of zero."
    )


def test_an_explicit_substitution_still_works_when_asked_for_by_name():
    """
    `fill_value` survives. The objection was never to substitution — it was to
    substitution nobody requested. Here the caller names the method and supplies
    the number.
    """
    clean_series = _clean_series()

    out = clean_series(pd.Series([np.nan, 1.0, np.nan]),
                       method="fill_value", fallback_value=7.0)
    assert list(out) == [7.0, 1.0, 7.0]


# ============================================================
# 4. The guard that could not fire
# ============================================================

def test_an_indicator_that_returns_nothing_usable_is_reported_as_a_failure():
    """
    THE LOAD-BEARING TEST.

    Item 9a's tests injected failures by making pandas_ta RAISE. This injects
    the other failure: the call succeeds and returns a frame with no usable
    values in it. That path ran through clean_series, came out as zeros, and
    reported nothing.

    ADX is used because it is the one indicator with no recomputation fallback,
    so the failure is observable rather than absorbed — and because ADX 0 reads
    as "no trend whatsoever", the opposite end of the scale from the 25.0 item
    9a removed, which is the more misleading of the two.
    """
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return

    import pandas_ta as ta
    from indicators import indicators

    df = _ohlcv()
    original = ta.adx

    def all_nan_adx(*args, **kwargs):
        idx = args[0].index if args else df.index
        return pd.DataFrame({0: [np.nan] * len(idx),
                             1: [np.nan] * len(idx),
                             2: [np.nan] * len(idx)}, index=idx)

    try:
        ta.adx = all_nan_adx
        indicators.ta.adx = all_nan_adx
        out, failures = indicators.add_technical_indicators(df, inplace=False)
    finally:
        ta.adx = original
        indicators.ta.adx = original

    names = [f.indicator for f in failures]
    assert "ADX" in names, (
        f"ta.adx returned a frame with no usable values and the run reported "
        f"failures {names or '[]'}. Before sequence item 15 this produced an "
        f"ADX column of zeros and no failure at all, because clean_series had "
        f"replaced every NaN before the guard looked."
    )

    if "ADX" in out.columns:
        assert not (out["ADX"] == 0).all(), (
            "the ADX column is entirely zero — the fabrication is back"
        )


# ============================================================
# 5–6. Real indicator output
# ============================================================

def test_an_indicators_warmup_rows_stay_empty():
    """
    A 14-period RSI has no value at bar 3. It used to hold the value RSI first
    took at bar 14.
    """
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return

    from core import config
    from indicators.indicators import add_technical_indicators

    out, _ = add_technical_indicators(_ohlcv(), inplace=False)

    warmup = out["RSI"].iloc[:config.RSI_LENGTH - 1]
    assert warmup.isna().any(), (
        "no RSI warm-up row is empty. Either the fill is back, or RSI is being "
        "computed with a window that needs no warm-up — check which before "
        "changing this test."
    )


def test_the_decision_bar_is_unaffected():
    """
    The counterweight. Removing fills must not have emptied the values the
    engine actually reads.

    This is why the item is safe: everything the decision touches is at the
    last bar of a 450-row frame, and every fill that was removed acted on the
    leading edge.
    """
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return

    from indicators.indicators import add_technical_indicators

    out, failures = add_technical_indicators(_ohlcv(), inplace=False)
    assert not failures, f"clean data produced failures: {failures}"

    for col in ("EMA_20", "EMA_50", "RSI", "ADX", "ATR", "VWMA",
                "EMA20_Slope", "EMA50_Slope"):
        assert col in out.columns, f"{col} is missing from the frame"
        assert not pd.isna(out[col].iloc[-1]), (
            f"{col} is NaN at the last bar — the bar every decision reads. "
            f"Removing the leading-edge fills should not have reached it."
        )


# ============================================================
# 7. The rule, held in place
# ============================================================

def _backward_fills(rel):
    """
    Every backward fill in one module, found in the SYNTAX rather than the text.

    A text scan cannot tell an instruction from a quotation, and this codebase
    quotes the calls it removed at length — clean_series's own docstring
    reproduces `.ffill().bfill()`, and bias_engine's explains a block that was
    deleted two items ago. Matching on the parse tree means prose is free to be
    as explicit as it likes.
    """
    with open(os.path.join(REPO_ROOT, *rel.split("/")), encoding="utf-8") as f:
        tree = ast.parse(f.read())

    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr == "bfill":
            found.append(".bfill()")
        elif isinstance(node, ast.Call):
            for kw in node.keywords:
                if (kw.arg == "limit_direction"
                        and isinstance(kw.value, ast.Constant)
                        and kw.value.value == "both"):
                    found.append("limit_direction='both'")
                elif (kw.arg == "method"
                        and isinstance(kw.value, ast.Constant)
                        and kw.value.value == "bfill"):
                    found.append("method='bfill'")
    return found


def test_only_the_chart_may_fill_backwards():
    """
    Source-level, and scoped by module rather than by line, so moving a fill
    somewhere else does not escape it.

    plotting.py is exempt because it draws a picture and feeds no decision. The
    exemption is a list of one, declared at the top of this file, so widening it
    is a visible edit rather than a silent drift.
    """
    from conftest import all_python_files

    offenders = []
    for rel in all_python_files(include_doc_tooling=False):
        norm = rel.replace("\\", "/")
        if norm in BACKFILL_EXEMPT or norm.startswith("tests/"):
            continue
        for hit in _backward_fills(norm):
            offenders.append(f"{norm}: {hit}")

    assert not offenders, (
        "a decision path fills from a later row:\n  " + "\n  ".join(offenders)
        + "\n\nItem 2: information unavailable at the decision timestamp must "
          "never influence that decision. In the engine as it stands the "
          "analysis is made at the last bar and this cannot reach it — but a "
          "backtest moves the decision timestamp backwards, and then it can, "
          "with no code change to blame."
    )


def test_the_chart_exemption_still_applies_to_something():
    """
    An exemption list nobody is on is a list that will be widened without
    anyone noticing it was empty. If plotting stops backfilling, delete the
    entry rather than leaving it standing.
    """
    for rel in BACKFILL_EXEMPT:
        path = os.path.join(REPO_ROOT, *rel.split("/"))
        assert os.path.exists(path), f"{rel} is exempt and does not exist"
        assert _backward_fills(rel), (
            f"{rel} is on the backfill exemption list and no longer backfills. "
            f"Remove it from BACKFILL_EXEMPT — an exemption for nothing is how "
            f"the list grows back."
        )


# ============================================================
# 8–9. The two substitutions found alongside
# ============================================================

def test_the_volume_profile_refuses_rather_than_pricing_a_bar_at_zero():
    """
    `.fillna(0)` on low/high was item 9's recorded leftover. The profile bins
    between price_min and price_max, so a single zeroed low drags the range to
    the origin and empties every bin above it. What comes out is an HVN at a
    price that never traded, which engine_core passes to calculate_stop_targets
    as a structural level.

    A gap a forward fill cannot close is the leading edge, so this builds one.
    """
    from indicators.volume_profile import compute_volume_profile

    df = _ohlcv().copy()
    df.loc[df.index[0], "low"] = np.nan

    profile, hvn, lvn = compute_volume_profile(df, num_bins=10)

    assert hvn is None and lvn is None, (
        f"a frame with an unfillable low produced hvn={hvn}, lvn={lvn}. If the "
        f"gap was zero-filled, those levels come from a bar priced at nothing."
    )


def test_the_structure_engine_refuses_a_frame_it_cannot_forward_fill():
    """
    structure.py filled OHLCV with zero and then read close.iloc[-1] as the
    current price on the very next line.
    """
    from structure.structure import calculate_structure

    df = _ohlcv().copy()
    df.loc[df.index[0], "close"] = np.nan

    try:
        calculate_structure(df)
    except ValueError as e:
        assert "forward fill" in str(e).lower() or "gap" in str(e).lower(), (
            f"it refused, but for an unexpected reason: {e}"
        )
        return

    raise AssertionError(
        "calculate_structure accepted a frame with a gap a forward fill cannot "
        "close. It used to substitute 0.0 and then read a price from it."
    )

```


=== FILE: tests/test_no_position_sizing.py ===

```python
"""
Sequence item 13 — position sizing removed, and the four duplicate fields with
it.

THE RULING

Viktor, 29 August 2026: the engine must not compute `position_size`,
`position_value` or `risk_amount` from an account balance and a risk
percentage. Monetary position sizing belongs outside the Structural Quant
Engine, in the portfolio/execution layer.

WHY A TEST AND NOT JUST A DELETION

A deletion is a fact about today. The engine produced a POSITION SIZE from a
placeholder 10,000 balance for its whole life, and the way that comes back is
not by someone re-adding `calculate_position_size` — it is by a field
reappearing in the decision object because it seemed useful, one name at a
time. So the assertions below are about the output, not about the source: no
block of the decision object may carry a sizing field under any of its names.

The source-level checks that follow are narrower, and one of them exists for a
specific reason: `risk_amount` named two unrelated things in this codebase. In
engine_core it was money — balance times risk percent. In panel_render it was a
price distance,

    risk_amount = abs(current_price - stop_loss)

and it is the denominator of all three R:R ratios. A find-and-replace on the
name would have silently zeroed the panel's R:R display while the rest of the
panel still looked right. The money is gone under the ruling, so the panel's
local is renamed to `stop_distance` in the same commit — the removal of one
side of a name collision is the moment the other side gets fixed, or it never
does. The test asserts the denominator survived the rename and that the old
name does not come back.

THE FOUR DUPLICATES

Item 10 declared them and scheduled them here:

    trend.health          == trend.trend_health
    trend.momentum        == trend.momentum_mode
    risk.risk_score       == bias.score
    risk.signal_strength  == bias.score

The trend pair mattered more than it looks: decision_model.py read
`trend["health"]` FIRST and fell back to `trend["trend_health"]`, so the
canonical field could have been changed with no effect on the decision.
"""

import ast
import os

PINNED_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "fixtures", "pinned")
UNREACHABLE = "http://127.0.0.1:1"

# Every name the removed sizing numbers travelled under, in the decision
# object. Checked against every block, not just "risk" — a field moved to
# another block is not a field removed.
SIZING_FIELDS = [
    "position_size",
    "position_value",
    "risk_amount",
    "account_balance",
    "risk_percent",
]

DUPLICATE_FIELDS = {
    "trend": ["health", "momentum"],
    "risk": ["risk_score", "signal_strength"],
}


def _engine_available():
    try:
        import pandas_ta  # noqa: F401
        return True
    except Exception:
        return False


def _run(symbol="AEROUSDT"):
    from data.data_fetcher import DataFetcher, data_fetcher
    from models.signal_router import SignalRouter

    original = data_fetcher.base_url
    try:
        data_fetcher.base_url = UNREACHABLE
        DataFetcher.set_pinned_source(PINNED_DIR)
        return SignalRouter().route(symbol=symbol, timeframe="4h")
    finally:
        DataFetcher.clear_pinned_source()
        data_fetcher.base_url = original


# ============================================================
# The ruling, checked at the output
# ============================================================

def test_no_block_of_the_decision_object_carries_a_sizing_field():
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return

    decision = _run()
    assert "error" not in decision, decision.get("error")

    found = []
    for block, contents in decision.items():
        if not isinstance(contents, dict):
            continue
        for field in SIZING_FIELDS:
            if field in contents:
                found.append(f"{block}.{field} = {contents[field]!r}")

    assert not found, (
        "the decision object carries monetary position sizing again:\n  "
        + "\n  ".join(found)
        + "\n\nViktor's ruling of 29 August 2026: sizing belongs in the "
          "portfolio/execution layer, which is the only layer that knows the "
          "real balance and the real exposure. A number computed here from a "
          "placeholder balance is an instruction to risk a specific amount."
    )


def test_the_risk_model_has_no_position_sizing_function():
    from models.risk_model import RiskModel

    assert not hasattr(RiskModel, "calculate_position_size"), (
        "RiskModel.calculate_position_size is back. Besides the sizing itself "
        "it carried portfolio policy — a 10x notional cap and 0.5x / 0.8x "
        "volatility haircuts — decided inside an engine that cannot see a "
        "portfolio."
    )


def test_the_placeholder_balance_is_not_in_config():
    from core import config

    for name in ("DEFAULT_ACCOUNT_BALANCE", "DEFAULT_RISK_PERCENT"):
        assert not hasattr(config, name), (
            f"config.{name} is defined again. It was read by exactly one "
            f"caller, the sizing block that is now gone; a placeholder balance "
            f"left in config is an invitation to wire it back up."
        )


def test_the_decision_log_does_not_fingerprint_a_balance():
    """
    The log records the config that can change a decision. A balance can no
    longer change one, and recording it would tell a future reader it still
    could.
    """
    from core.decision_log import FINGERPRINTED_CONFIG

    for name in ("DEFAULT_ACCOUNT_BALANCE", "DEFAULT_RISK_PERCENT"):
        assert name not in FINGERPRINTED_CONFIG, (
            f"{name} is fingerprinted in the decision log but nothing reads it"
        )


# ============================================================
# The duplicates
# ============================================================

def test_the_duplicate_fields_are_gone():
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return

    decision = _run()
    assert "error" not in decision, decision.get("error")

    found = []
    for block, fields in DUPLICATE_FIELDS.items():
        contents = decision.get(block, {})
        for field in fields:
            if field in contents:
                found.append(f"{block}.{field}")

    assert not found, (
        "duplicate fields are back in the decision object: " + ", ".join(found)
        + "\n\ntrend.health and trend.momentum restated the two fields beside "
          "them; risk.risk_score and risk.signal_strength were both bias.score. "
          "Two names for one number means a change to one of them is invisible "
          "in the other."
    )


def test_the_survivors_are_still_there():
    """
    The removal must not have taken the canonical fields with it. Stated
    separately because a test that only asserts absence passes just as happily
    on an engine that produces nothing at all.
    """
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return

    decision = _run()
    assert "error" not in decision, decision.get("error")

    assert "trend_health" in decision.get("trend", {}), "trend.trend_health is gone"
    assert "momentum_mode" in decision.get("trend", {}), "trend.momentum_mode is gone"
    assert "score" in decision.get("bias", {}), (
        "bias.score is gone — that is the field risk_score and signal_strength "
        "were duplicating, and removing them was only safe because it stays."
    )


def test_the_decision_model_reads_the_canonical_trend_field():
    """
    decision_model.py read `trend["health"]` first, falling back to
    trend_health. With the duplicate gone the fallback would carry it silently
    — but the default is 50.0, so a future rename of trend_health would give
    every decision a fixed mid-range trend reading and raise nothing.

    Asserted at the source, because the value is identical either way and a
    behavioural test cannot see the difference.
    """
    from conftest import REPO_ROOT

    path = os.path.join(REPO_ROOT, "models", "decision_model.py")
    with open(path, encoding="utf-8") as f:
        code = "\n".join(line.split("#", 1)[0] for line in f.read().splitlines())

    assert 'trend.get("health"' not in code and "trend.get('health'" not in code, (
        "decision_model.py reads trend['health'] again. It no longer exists, "
        "so this silently falls through to a default of 50.0 — a fixed "
        "mid-range trend reading on every decision, raising nothing."
    )


# ============================================================
# The name collision — the one hazard in this item
# ============================================================

def test_the_panel_still_computes_its_own_stop_distance():
    """
    `risk_amount` named two unrelated things. In engine_core it was money —
    balance times risk percent — and it is gone. In panel_render it was a price
    distance and it is the denominator of all three R:R ratios. A
    find-and-replace on the name would have silently zeroed the panel's R:R
    display while everything else still looked right.

    The money is gone, so the local is renamed to stop_distance: the removal of
    one side of a name collision is the moment the other side gets fixed, or it
    never does. This asserts the denominator survived the rename.
    """
    from conftest import REPO_ROOT

    path = os.path.join(REPO_ROOT, "core", "panel_render.py")
    with open(path, encoding="utf-8") as f:
        source = f.read()
    tree = ast.parse(source)

    assigned_from_a_subtraction = False
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        names = [t.id for t in node.targets if isinstance(t, ast.Name)]
        if "stop_distance" not in names:
            continue
        for inner in ast.walk(node.value):
            if isinstance(inner, ast.BinOp) and isinstance(inner.op, ast.Sub):
                assigned_from_a_subtraction = True

    assert assigned_from_a_subtraction, (
        "panel_render.py no longer computes stop_distance as a price distance. "
        "It is the denominator of R:R 1, 2 and 3, and without it all three "
        "print 0.00 while the panel otherwise looks correct."
    )

    code = "\n".join(l.split("#", 1)[0] for l in source.splitlines())
    assert "risk_amount" not in code, (
        "risk_amount is back as a name in panel_render.py. It meant a sum of "
        "money everywhere else in this codebase; here it meant a price "
        "distance. That collision is what made a rename dangerous."
    )


def test_the_panel_does_not_read_a_sizing_field_from_the_decision():
    from conftest import REPO_ROOT

    path = os.path.join(REPO_ROOT, "core", "panel_render.py")
    with open(path, encoding="utf-8") as f:
        tree = ast.parse(f.read())

    read = set()
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "get"
                and node.args
                and isinstance(node.args[0], ast.Constant)
                and node.args[0].value in SIZING_FIELDS):
            read.add(node.args[0].value)
        elif (isinstance(node, ast.Subscript)
                and isinstance(node.slice, ast.Constant)
                and node.slice.value in SIZING_FIELDS):
            read.add(node.slice.value)

    assert not read, (
        "panel_render.py reads " + ", ".join(sorted(read)) + " off a decision "
        "object that no longer produces it. `.get` would hand it a default and "
        "the panel would print a confident zero."
    )

```


=== FILE: tests/test_pinned_source.py ===

```python
"""
Sequence item 3 — the pinned data path.

Before this existed, get_tf() always went to the live API, so the engine could
not be run twice on the same input. That made most of the audit's Verification
fields unsatisfiable: Items 3, 11 and 13 all prescribe "change something, rerun,
compare", and T2-4's own check is "change a knob, rerun, observe the delta".
None of that is possible when every run sees different data.

These tests cover the mechanism itself. They do not need pandas_ta, a network,
or any knowledge of trading — which is the point.

Constitution: closes T3-5 (fixed evaluation datasets), and unblocks the
Verification clauses of Items 3, 11, 13 and T2-4.

NOTE ON THE GOLDEN-PATH TEST: test_golden_path.py still monkeypatches
DataFetcher.get_tf rather than using this mechanism. That is deliberate and
temporary. Switching it over changes the BTC series it sees — the monkeypatch
fabricates BTC by reversing and scaling the base series — which would move the
stored snapshot. Re-baselining belongs to sequence item 7, which exists to
capture the golden baseline *after* the cleanup in items 5 and 6, so that every
later delta is attributable to exactly one controlled change. Doing it here
would spend that attributability early.
"""

import os
import sys

from conftest import fixture, REPO_ROOT

PINNED_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "fixtures", "pinned")


def _fetcher():
    from data.data_fetcher import DataFetcher
    return DataFetcher


def _unreachable(instance):
    """
    Point an instance at a dead port.

    If any of these tests reach the network the connection is refused
    immediately, so a test that silently fell back to the live API fails loudly
    instead of passing slowly.
    """
    instance.base_url = "http://127.0.0.1:1"
    return instance


def test_pinned_directory_exists_and_is_complete():
    """
    All three series the engine fetches must be present.

    engine_core makes three calls: the base series (line 499), the macro
    timeframe (524), and BTC context (682). Pinning only the base leaves two
    thirds of a run still dependent on the network, and the resulting
    "reproducible" run is not.
    """
    assert os.path.isdir(PINNED_DIR), f"no pinned dataset at {PINNED_DIR}"

    expected = {"AEROUSDT_4h.csv", "AEROUSDT_1d.csv", "BTCUSDT_4h.csv"}
    present = {f for f in os.listdir(PINNED_DIR) if f.endswith(".csv")}
    missing = expected - present
    assert not missing, f"pinned dataset incomplete, missing: {sorted(missing)}"

    assert os.path.exists(os.path.join(PINNED_DIR, "MANIFEST.json")), (
        "the pinned dataset has no MANIFEST.json — sequence item 3 requires "
        "hashes and origin to be recorded, not assumed"
    )


def test_manifest_hashes_match_the_files():
    """
    The manifest records a sha256 per series. If a file is edited without
    regenerating, this catches it — which is the whole reason to record hashes
    rather than trust that the data has not moved.
    """
    import hashlib
    import json

    with open(os.path.join(PINNED_DIR, "MANIFEST.json")) as f:
        manifest = json.load(f)

    mismatches = []
    for series in manifest["series"]:
        path = os.path.join(PINNED_DIR, series["file"])
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        if h.hexdigest() != series["sha256"]:
            mismatches.append(series["file"])

    assert not mismatches, (
        "pinned data does not match its manifest: " + ", ".join(mismatches) +
        "\nEither the files were edited without regenerating, or the manifest "
        "is stale. Regenerate with: python docs/build/make_pinned.py"
    )


def test_pinned_source_serves_all_three_series_without_network():
    DataFetcher = _fetcher()
    fetcher = _unreachable(DataFetcher())
    try:
        DataFetcher.set_pinned_source(PINNED_DIR)
        for symbol, timeframe in [("AEROUSDT", "4h"), ("AEROUSDT", "1d"),
                                  ("BTCUSDT", "4h")]:
            df = fetcher.get_tf(symbol, timeframe, limit=300)
            err = df.attrs.get("fetch_error")
            assert err is None, f"{symbol} {timeframe} failed: {err}"
            assert len(df) > 0, f"{symbol} {timeframe} returned no rows"
            assert list(df.columns) == ["open", "high", "low", "close", "volume"], (
                f"{symbol} {timeframe} has unexpected columns: {list(df.columns)}"
            )
    finally:
        DataFetcher.clear_pinned_source()


def test_two_fetches_return_equal_data():
    """The property that makes every later fix verifiable."""
    DataFetcher = _fetcher()
    fetcher = _unreachable(DataFetcher())
    try:
        DataFetcher.set_pinned_source(PINNED_DIR)
        first = fetcher.get_tf("AEROUSDT", "4h", limit=300)
        second = fetcher.get_tf("AEROUSDT", "4h", limit=300)
        assert first.equals(second), (
            "two fetches of pinned data returned different frames"
        )
    finally:
        DataFetcher.clear_pinned_source()


def test_each_fetch_returns_an_independent_copy():
    """
    When this was written, T2-1 was open: four modules rewrote their caller's
    columns in place. If the pinned source had handed the same object to every
    caller, those writes would have corrupted the dataset mid-run and the second
    and third series would have seen mutated data.

    Sequence item 6 closed T2-1, so this is no longer load-bearing against that
    specific hazard — and it stays anyway, for two reasons. It is the guarantee
    this class makes on its own terms: a caller who receives a frame owns it.
    And it is what stops a future "optimisation" from caching the loaded frame,
    which would make the ownership claim false again without touching any of the
    modules item 6 fixed.
    """
    DataFetcher = _fetcher()
    fetcher = _unreachable(DataFetcher())
    try:
        DataFetcher.set_pinned_source(PINNED_DIR)
        first = fetcher.get_tf("AEROUSDT", "4h", limit=300)
        original_close = float(first["close"].iloc[-1])

        first["close"] = 0.0                      # simulate in-place mutation

        second = fetcher.get_tf("AEROUSDT", "4h", limit=300)
        assert float(second["close"].iloc[-1]) == original_close, (
            "mutating a returned frame corrupted the next fetch — the pinned "
            "source is handing out shared state"
        )
    finally:
        DataFetcher.clear_pinned_source()


def test_missing_series_errors_rather_than_falling_back_to_live():
    """
    The most important test in this file.

    A silent fall-through to the live API would reintroduce exactly the
    nondeterminism the pinned source exists to remove — and would do it
    invisibly, which is worse than not having the mechanism at all.
    """
    DataFetcher = _fetcher()
    fetcher = _unreachable(DataFetcher())
    try:
        DataFetcher.set_pinned_source(PINNED_DIR)
        df = fetcher.get_tf("NOTAREALPAIR", "4h", limit=300)

        assert len(df) == 0, "expected no rows for a series with no pinned file"
        err = df.attrs.get("fetch_error")
        assert err, (
            "a missing pinned series returned no error — it may have fallen "
            "through to the live API"
        )
        assert "pinned source active" in err, (
            f"error does not identify this as a pinned-source failure: {err}"
        )
    finally:
        DataFetcher.clear_pinned_source()


def test_limit_takes_the_most_recent_candles():
    """
    The API returns the most recent `limit` candles. The pinned source must
    match, or indicator warm-up periods land on different data than they would
    live.
    """
    DataFetcher = _fetcher()
    fetcher = _unreachable(DataFetcher())
    try:
        DataFetcher.set_pinned_source(PINNED_DIR)
        full = fetcher.get_tf("AEROUSDT", "4h", limit=100000)
        limited = fetcher.get_tf("AEROUSDT", "4h", limit=50)

        assert len(limited) == 50, f"expected 50 rows, got {len(limited)}"
        assert limited.index[-1] == full.index[-1], (
            "limit took the oldest candles instead of the newest"
        )
    finally:
        DataFetcher.clear_pinned_source()


def test_environment_variable_activates_the_pinned_source():
    """
    So a run can be made reproducible from the command line without editing
    code:  PHASE7_PINNED_DATA=tests/fixtures/pinned python main.py
    """
    DataFetcher = _fetcher()
    from data.data_fetcher import PINNED_ENV_VAR

    previous = os.environ.get(PINNED_ENV_VAR)
    try:
        DataFetcher.clear_pinned_source()
        assert DataFetcher.pinned_source() is None, (
            "a pinned source was active before this test set one — earlier "
            "tests are leaking state"
        )

        os.environ[PINNED_ENV_VAR] = PINNED_DIR
        assert DataFetcher.pinned_source() is not None, (
            f"{PINNED_ENV_VAR} did not activate the pinned source"
        )
    finally:
        if previous is None:
            os.environ.pop(PINNED_ENV_VAR, None)
        else:
            os.environ[PINNED_ENV_VAR] = previous
        DataFetcher.clear_pinned_source()


def test_live_api_is_the_default():
    """
    The mechanism must be opt-in. Nothing about normal operation changes until
    someone asks for pinned data.
    """
    DataFetcher = _fetcher()
    from data.data_fetcher import PINNED_ENV_VAR

    previous = os.environ.get(PINNED_ENV_VAR)
    try:
        DataFetcher.clear_pinned_source()
        os.environ.pop(PINNED_ENV_VAR, None)
        assert DataFetcher.pinned_source() is None, (
            "fetches are pinned by default — they should go live unless asked"
        )
    finally:
        if previous is not None:
            os.environ[PINNED_ENV_VAR] = previous

```


=== FILE: tests/test_smoke.py ===

```python
"""
The smoke run: the whole engine, end to end, on pinned data.

Sequence item 4 asks for "a smoke run on pinned data". It became possible only
when item 3 landed, and it is the test that proves the pinned source works
*through the engine* rather than only through DataFetcher — which is a
different claim. test_pinned_source.py shows the fetcher serves files
correctly; this shows the engine actually runs on them, start to finish,
without touching the network.

It does not compare a snapshot. Asserting exact output belongs to
test_golden_path.py, and re-baselining that against the pinned source is
sequence item 7's job, deliberately after the cleanup in items 5 and 6 so that
every later delta traces to exactly one controlled change. This test asks only:
does it complete, and is the result shaped like a decision?

That is a lower bar and a useful one. Five of the nine crashes in the runtime
log were failures to complete at all.

Constitution: Tier 3, item 3 (automated tests). Sequence item 4.
"""

import os

from conftest import REPO_ROOT

PINNED_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "fixtures", "pinned")

# The pinned dataset was built to match the engine's own defaults, so a smoke
# run needs no special configuration: config.SYMBOL is AEROUSDT, TIMEFRAME is
# 4h, MACRO_TIMEFRAME is 1d, and BTC context is always BTCUSDT.
SYMBOL = "AEROUSDT"
TIMEFRAME = "4h"

# Top-level keys signal_router builds into every successful decision object.
EXPECTED_KEYS = [
    "symbol", "timeframe", "bias", "trend", "structure",
    "entry", "risk", "exit", "btc_context", "explanation",
]


def _engine_available():
    try:
        import pandas_ta  # noqa: F401
        return True
    except Exception:
        return False


def test_engine_runs_end_to_end_on_pinned_data():
    """
    The whole pipeline on disk-backed input, with the network unreachable.

    base_url is pointed at a dead port on purpose. If any part of the engine
    reaches the API, the connection is refused and this fails — so a silent
    fall-through to live data cannot masquerade as a passing smoke test.
    """
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return

    from data.data_fetcher import DataFetcher, data_fetcher
    from models.signal_router import SignalRouter

    original_url = data_fetcher.base_url
    try:
        data_fetcher.base_url = "http://127.0.0.1:1"
        DataFetcher.set_pinned_source(PINNED_DIR)

        decision = SignalRouter().route(symbol=SYMBOL, timeframe=TIMEFRAME)

        assert isinstance(decision, dict), (
            f"route() returned {type(decision).__name__}, not a dict"
        )
        assert "error" not in decision, (
            f"the engine reported an error on clean pinned data: "
            f"{decision.get('error')}"
        )

        missing = [k for k in EXPECTED_KEYS if k not in decision]
        assert not missing, (
            f"decision object is missing expected keys: {', '.join(missing)}"
        )

        assert decision.get("symbol") == SYMBOL, (
            f"decision reports symbol {decision.get('symbol')!r}, "
            f"expected {SYMBOL!r}"
        )
    finally:
        DataFetcher.clear_pinned_source()
        data_fetcher.base_url = original_url


def test_the_smoke_run_is_reproducible():
    """
    Two full engine runs on pinned data must agree.

    This is the property the whole apparatus phase exists to establish, tested
    at the top level rather than at the fetcher. It is weaker than the golden
    snapshot — it compares two live runs to each other rather than to a stored
    baseline — but it needs no baseline, so it keeps working across the
    re-baselining at sequence item 7.
    """
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return

    from data.data_fetcher import DataFetcher, data_fetcher
    from models.signal_router import SignalRouter

    volatile = {"chart_path", "timestamp", "generated_at"}

    def stable(obj):
        if isinstance(obj, dict):
            return {k: stable(v) for k, v in obj.items() if k not in volatile}
        if isinstance(obj, (list, tuple)):
            return [stable(v) for v in obj]
        if isinstance(obj, float):
            return round(obj, 8)
        return obj

    original_url = data_fetcher.base_url
    try:
        data_fetcher.base_url = "http://127.0.0.1:1"
        DataFetcher.set_pinned_source(PINNED_DIR)

        first = stable(SignalRouter().route(symbol=SYMBOL, timeframe=TIMEFRAME))
        second = stable(SignalRouter().route(symbol=SYMBOL, timeframe=TIMEFRAME))

        if first != second:
            differing = sorted(
                k for k in set(first) | set(second)
                if first.get(k) != second.get(k)
            )
            raise AssertionError(
                "two full engine runs on identical pinned data disagreed.\n"
                f"fields that differ: {', '.join(differing)}"
            )
    finally:
        DataFetcher.clear_pinned_source()
        data_fetcher.base_url = original_url


def test_a_missing_pinned_series_surfaces_as_an_engine_error():
    """
    The failure path, end to end.

    A pinned source with no file for the requested symbol must produce a
    reported error rather than a confident-looking panel built on nothing.
    This is Item 13's territory reached from the data side — and it is what
    proves the "never fall back to live" rule holds through the engine, not
    just inside DataFetcher.
    """
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return

    from data.data_fetcher import DataFetcher, data_fetcher
    from models.signal_router import SignalRouter

    original_url = data_fetcher.base_url
    try:
        data_fetcher.base_url = "http://127.0.0.1:1"
        DataFetcher.set_pinned_source(PINNED_DIR)

        decision = SignalRouter().route(symbol="NOTAREALPAIR", timeframe="4h")

        assert isinstance(decision, dict), "route() did not return a dict"
        assert "error" in decision, (
            "the engine produced a decision for a symbol with no data. It "
            "should report an error — a panel built on no input is exactly "
            "the failure Item 13 is about."
        )
    finally:
        DataFetcher.clear_pinned_source()
        data_fetcher.base_url = original_url

```


=== FILE: tests/test_traceability.py ===

```python
"""
Sequence item 12 — Items 5 (Reproducibility) and 6 (Traceability), the last
Critical.

THE DEFECT

The panel printed

    Trade logged to Logs/phase7_trade_log_<symbol>.csv

on every run since the engine was written, and no code anywhere wrote that
file. Of the four Criticals it is the only one where the engine was not merely
wrong but claiming a safeguard it did not have.

The chart line had the same fault in a subtler form:

    f"AI Risk chart saved to {decision.get('chart_path', 'Logs/Charts/chart.png')}"

`.get` returns the default only when the key is ABSENT. The router always sets
chart_path, and sets it to None when charting failed — so a failed chart
printed "AI Risk chart saved to None", which is still a claim that something
was saved.

CLOSED BY MAKING IT TRUE, NOT BY DELETING THE CLAIM

The opposite of the call at item 9c, and the difference is worth stating. The
`trend_failure` gate needed someone to decide when a trade should be blocked —
a trading judgment nothing here can validate. This needs nobody to decide
anything: a log file exists or it does not, and Item 5 requires one regardless
of what the panel says.
"""

import json
import os
import shutil
import tempfile

PINNED_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "fixtures", "pinned")
UNREACHABLE = "http://127.0.0.1:1"


def _engine_available():
    try:
        import pandas_ta  # noqa: F401
        return True
    except Exception:
        return False


def _run(symbol="AEROUSDT"):
    from data.data_fetcher import DataFetcher, data_fetcher
    from models.signal_router import SignalRouter

    original = data_fetcher.base_url
    try:
        data_fetcher.base_url = UNREACHABLE
        DataFetcher.set_pinned_source(PINNED_DIR)
        return SignalRouter().route(symbol=symbol, timeframe="4h")
    finally:
        DataFetcher.clear_pinned_source()
        data_fetcher.base_url = original


# ============================================================
# Item 6 — the claim must be true
# ============================================================

def test_the_decision_log_the_panel_claims_actually_exists():
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return

    decision = _run()
    path = decision.get("decision_log_path")

    assert path, (
        "the run reports no decision log path. The panel has claimed one on "
        "every run since the engine was written."
    )
    assert os.path.exists(path), (
        f"the decision object names {path} but no such file exists. That is "
        f"Item 6 exactly: an audit action asserted, not performed."
    )


def test_the_log_records_what_the_run_saw_not_just_what_it_decided():
    """
    Item 5 is Reproducibility, and that is a higher bar than "a record exists".

    A stored decision with no fingerprint of its inputs cannot be checked
    against anything — it is a receipt. These five fields are what make a run
    repeatable.
    """
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return

    from core import config, decision_log

    _run()
    records = decision_log.read(config.LOG_DIR, "AEROUSDT")
    assert records, "the log is empty after a successful run"

    latest = records[-1]
    assert latest.get("engine_version"), "no engine_version in the record"
    assert latest.get("config"), "no config snapshot in the record"

    prov = latest.get("decision", {}).get("provenance", {})
    for field in ("engine_version", "last_candle", "row_count", "source"):
        assert field in prov, f"provenance is missing {field}: {prov}"

    assert prov["row_count"] > 0, "row_count is zero on a successful run"
    assert prov["source"] == "pinned", (
        f"the run used pinned data but records its source as {prov['source']!r}"
    )

    # The source is a KIND, not a path. Recording the pinned directory made
    # provenance differ between two runs on identical data — caught by the
    # determinism test on the first full run of this item.
    assert "/" not in prov["source"] and "\\" not in prov["source"], (
        f"provenance.source looks like a path ({prov['source']!r}). A "
        f"machine-specific location is not part of a run's identity; "
        f"last_candle and row_count are what fingerprint the data."
    )


def test_engine_version_is_written_somewhere_at_last():
    """
    config.engine_version has existed since the engine was built and was
    written nowhere — Step 5's verification pass counted exactly one occurrence
    of it in the whole source tree, its own definition.

    A version string nothing records cannot answer "which build produced this
    number", which is the question a traceability rule exists to answer.
    """
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return

    from core import config

    decision = _run()
    recorded = decision.get("provenance", {}).get("engine_version")
    assert recorded == config.engine_version, (
        f"the run records engine_version {recorded!r}, config says "
        f"{config.engine_version!r}"
    )


def test_a_failed_write_is_reported_as_a_failure():
    """
    The other half of Item 6, and the one that is easy to miss.

    Writing the log fixes the claim only while the write succeeds. An engine
    that prints "logged" after a failed write has the original defect back with
    a new filename.
    """
    from core import config, decision_log

    unwritable = os.path.join(tempfile.gettempdir(), "phase7_not_a_dir")
    try:
        # A file where a directory is expected: makedirs fails, so must write.
        with open(unwritable, "w") as f:
            f.write("x")
        result = decision_log.write({"symbol": "TESTUSDT"}, config, log_dir=unwritable)
    finally:
        try:
            os.remove(unwritable)
        except OSError:
            pass

    assert result is None, (
        f"decision_log.write returned {result!r} when it could not write. "
        f"The caller uses this return value to decide whether the panel may "
        f"claim the run was logged."
    )


# ============================================================
# The panel's claims
# ============================================================

def test_the_panel_makes_no_unconditional_claims_about_files():
    """
    Source-level, because the failing case is hard to reach at runtime and the
    defect is a shape rather than a value: a claim printed without checking.
    """
    from conftest import REPO_ROOT

    with open(os.path.join(REPO_ROOT, "core", "panel_render.py"), encoding="utf-8") as f:
        code = "\n".join(line.split("#", 1)[0] for line in f.read().splitlines())

    assert "Trade logged to Logs/" not in code, (
        "the panel prints a hardcoded trade-log path again. That path named a "
        "file nothing wrote, on every run, for the life of the engine."
    )
    assert "'Logs/Charts/chart.png'" not in code, (
        "the chart line uses a .get default again. The key is always present "
        "and is None when charting failed, so the default never fires and the "
        "panel prints 'saved to None'."
    )


def test_the_explanation_names_the_symbol_under_analysis():
    """
    Item 10(a) rider. "AERO" was hardcoded into the BTC reasoning, so running
    on any other pair produced text about AERO — and running on BTCUSDT claimed
    to compare AERO against BTC while comparing BTC to itself.
    """
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return

    from models.decision_model import DecisionModel

    btc_context = {
        "available": True, "raw": "BEARISH", "detailed": "BEARISH CONFIRMED",
        "correlation": -0.04, "correlation_label": "WEAK / NO CLEAR RELATIONSHIP",
        "beta": -0.05, "broad_market_stress": False, "n_observations": 30,
        "score": -60.0,
    }
    out = DecisionModel()._compute_btc_adjusted(
        confidence=70.0,
        bias={"score": 80.0, "raw": "BULLISH"},
        btc_context=btc_context,
        symbol="SOLUSDT",
    )
    text = " ".join(out.get("reasons", []))

    assert "AERO" not in text.upper(), (
        f"the engine was run on SOLUSDT and its BTC reasoning names AERO:\n  {text}"
    )
    assert "SOL" in text.upper(), (
        f"the reasoning does not name the asset under analysis:\n  {text}"
    )


def test_the_correlation_phrase_is_not_doubled():
    """
    correlation_label already ends in "relationship". The sentence appended
    another, printing "a weak / no clear relationship relationship" on every
    run for as long as the BTC feature has existed.
    """
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return

    from models.decision_model import DecisionModel

    out = DecisionModel()._compute_btc_adjusted(
        confidence=70.0,
        bias={"score": 80.0, "raw": "BULLISH"},
        btc_context={
            "available": True, "raw": "BEARISH", "detailed": "BEARISH CONFIRMED",
            "correlation": -0.04, "correlation_label": "WEAK / NO CLEAR RELATIONSHIP",
            "beta": -0.05, "broad_market_stress": False, "n_observations": 30,
            "score": -60.0,
        },
        symbol="AEROUSDT",
    )
    text = " ".join(out.get("reasons", [])).lower()

    assert "relationship relationship" not in text, (
        f"the doubled word is back:\n  {text}"
    )
    assert "relationship" in text, (
        "the phrase lost the word entirely — the fix should deduplicate, not delete"
    )


def test_the_btc_number_carries_its_validation_status():
    """
    Item 7: a component that is correctness-validated but empirically
    unvalidated must say so rather than let a number imply otherwise.

    Nothing has tested whether adjusting confidence by BTC correlation predicts
    anything. The panel prints it to two decimal places, which implies a great
    deal.
    """
    from conftest import REPO_ROOT

    with open(os.path.join(REPO_ROOT, "core", "panel_render.py"), encoding="utf-8") as f:
        source = f.read()

    assert "empirically unvalidated" in source, (
        "the BTC-adjusted confidence line carries no validation-status label. "
        "Item 7 requires the status to be stated, and a bare number states the "
        "opposite."
    )

```
