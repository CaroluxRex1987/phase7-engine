"""
Kimi Finding 3, round 4 (Item 5, Reproducibility) — two runs on different code
recorded identical hashes.

THE DEFECT, IN THE FINDING'S OWN TERMS

`config.engine_version` is the string "Phase-7 Structural Quant Engine v1.0"
and has not changed across any commit in this repository. The record's other
half, `decision_log.FINGERPRINTED_MODULES`, is an enumeration of constant
names, and the finding lists seven decision-affecting settings missing from it:
DEGRADED_CONFIDENCE_CEILING, BTC_ADJUSTMENT_CAP, the entry multipliers, the
trend bands, SPIKE_RATIO, window=30, and 0.0015.

WHY THE TESTS BELOW ARE SHAPED THE WAY THEY ARE

Six of those seven cannot be added to an enumeration of module attributes at
all — they are a class attribute, a function local, and bare literals in
comparisons and at call sites. `getattr(module, name)` reaches none of them. So
this file does not test that a list got longer. It tests that the record now
distinguishes two runs on different code WHATEVER changed, by fingerprinting
the parse tree of every source file.

The file is in two halves, and the split is rule 23 — a test that fails with
ImportError proves the module is new, not that the defect was real.

    PART ONE asks what the RECORD contains. It imports nothing that this patch
    added, so every test in it runs against pre-fix code exactly as written and
    every failure there is a behavioural failure.

    PART TWO exercises core/code_fingerprint.py directly. Against pre-fix code
    these fail with ImportError and are worth nothing as evidence. They are
    here because the mechanism needs holding, not because they prove anything
    about the old engine.

The negative controls are named as such. A fingerprint that moved on every edit
would pass every "it moved" test in this file and be useless, so two tests
assert that it does NOT move: on a comment, and on a docstring.

NO PYTEST FIXTURES ANYWHERE IN THIS FILE. `run_tests.py` — the runner that
works without pytest — reports a fixture-taking test as an error, and there are
29 of those already. This adds none.
"""

import ast
import gzip
import io
import json
import os
import shutil
import sys
import tempfile

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

PINNED_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "fixtures", "pinned")
UNREACHABLE = "http://127.0.0.1:1"

HEX = set("0123456789abcdef")


def _engine_available():
    try:
        import pandas_ta  # noqa: F401
        return True
    except Exception:
        return False


def _run(symbol="AEROUSDT"):
    """The production path, against pinned data, with the live API unreachable."""
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


def _is_sha256(value):
    return (isinstance(value, str) and len(value) == 64
            and set(value.lower()) <= HEX)


# ============================================================
# PART ONE — what the record contains
#
# Nothing below imports core.code_fingerprint. These run against pre-fix code
# as written, and a failure here is a behavioural failure.
# ============================================================

def test_the_record_says_which_code_the_run_was_made_on():
    """
    The finding, stated as an assertion about the output.

    Pre-fix, provenance had no field that could differ between two runs on
    different code: engine_version is a hand-maintained label and
    module_constants is a list that six of the seven named settings cannot
    appear in.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    decision = _run()
    prov = decision.get("provenance", {})

    assert "code_hash" in prov, (
        "provenance records nothing that identifies the code this run was "
        "made on. engine_version is a static label and module_constants is an "
        "enumeration -- Kimi Finding 3 exactly: two runs on different code "
        "record identical hashes."
    )
    assert _is_sha256(prov["code_hash"]), (
        f"code_hash is not a SHA-256 digest: {prov['code_hash']!r}. None here "
        f"means the fingerprint could not be taken, which is a recorded "
        f"failure and not a passing run."
    )


def test_the_code_hash_survives_into_the_permanent_log_not_just_the_return():
    """
    The decision object is transient; the JSONL line is the record.

    Item 5 is about what can be checked later, so a field that exists only in
    the value returned to the caller closes nothing.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    from core import config, decision_log

    _run()
    records = decision_log.read(config.LOG_DIR, "AEROUSDT")
    assert records, "the log is empty after a successful run"

    prov = records[-1].get("decision", {}).get("provenance", {})
    assert _is_sha256(prov.get("code_hash")), (
        f"the stored record carries no usable code identity: "
        f"{prov.get('code_hash')!r}"
    )


def test_the_archive_meta_says_which_file_changed_not_only_that_one_did():
    """
    A combined hash answers "is this the same code" and stops there. The
    per-file digests answer the question a reader asks next, and they live in
    the gzipped archive rather than in the log line because the log gets one
    line per run forever.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    decision = _run()
    path = decision.get("lineage", {}).get("archive", {}).get("path")
    if not path or not os.path.exists(path):
        pytest.skip(f"no archive was written for this run ({path!r})")

    with gzip.open(path, "rb") as fh:
        payload = json.loads(fh.read().decode("utf-8"))

    code = payload.get("meta", {}).get("code", {})
    files = code.get("files", {})
    assert files, "the archive meta carries no per-file digests"
    assert "core/engine_core.py" in files, (
        "the per-file map does not name core/engine_core.py, so either the "
        "walk missed the decision path or the paths are not in POSIX spelling: "
        + ", ".join(sorted(files)[:5])
    )
    assert all(_is_sha256(v) for v in files.values()), (
        "some per-file entries are not digests: "
        + ", ".join(k for k, v in files.items() if not _is_sha256(v))
    )


def test_the_contract_declares_the_field():
    """
    decision_contract.py is the declared shape of the record. A field written
    but never declared is the kind of drift Item 6 exists to prevent.
    """
    from core.decision_contract import ProvenanceBlock

    assert "code_hash" in getattr(ProvenanceBlock, "__annotations__", {}), (
        "ProvenanceBlock does not declare code_hash, so the record has a "
        "field the contract does not know about"
    )


def test_module_snapshot_reaches_a_constant_held_on_a_class():
    """
    DEGRADED_CONFIDENCE_CEILING, the first of the seven Kimi named.

    It is a class attribute of DecisionModel, and `getattr(module, name)` on
    the module returns nothing for it. Pre-fix it could not be named in
    FINGERPRINTED_MODULES without recording as MISSING -- a record stating a
    knob was not defined when it was defined and read on every degraded run.
    """
    from core.decision_log import MISSING, module_snapshot
    from models.decision_model import DecisionModel

    snap = module_snapshot().get("models.decision_model", {})
    key = "DecisionModel.DEGRADED_CONFIDENCE_CEILING"

    assert key in snap, (
        "the confidence ceiling applied to every degraded run is not in the "
        "record. Kimi Finding 3, first item."
    )
    assert snap[key] is not MISSING, (
        "the ceiling is named but resolves to MISSING, which is a record "
        "asserting the constant is undefined while decision_model reads it"
    )
    assert snap[key] == DecisionModel.DEGRADED_CONFIDENCE_CEILING, (
        f"the record says {snap[key]!r}; the class says "
        f"{DecisionModel.DEGRADED_CONFIDENCE_CEILING!r}"
    )


def test_module_snapshot_reaches_the_btc_adjustment_cap():
    """The second of the seven, and the same shape as the first."""
    from core.decision_log import MISSING, module_snapshot
    from models.decision_model import DecisionModel

    snap = module_snapshot().get("models.decision_model", {})
    key = "DecisionModel.BTC_ADJUSTMENT_CAP"

    assert key in snap and snap[key] is not MISSING, (
        "the cap bounding how far BTC context can move confidence is not in "
        "the record"
    )
    assert snap[key] == DecisionModel.BTC_ADJUSTMENT_CAP


def test_module_snapshot_reaches_spike_ratio():
    """
    ROUND 6 (Meta Muse Spark 1.3), F1, 13 September 2026. SPIKE_RATIO was a
    function local inside add_technical_indicators, unreachable by
    `getattr(module, name)`. Promoted to module scope in
    indicators/indicators.py, value unchanged.

    Skipped without pandas_ta: indicators.indicators imports it at module
    scope, so the module -- and this constant along with it -- cannot be
    imported at all in that configuration. See the regression guard test
    above for the same shape.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed -- indicators.indicators cannot "
                    "be imported")

    from core.decision_log import MISSING, module_snapshot
    from indicators import indicators

    snap = module_snapshot().get("indicators.indicators", {})
    key = "SPIKE_RATIO"

    assert key in snap and snap[key] is not MISSING, (
        "the volume spike ratio degradation threshold is not in the record"
    )
    assert snap[key] == indicators.SPIKE_RATIO


def test_module_snapshot_reaches_the_correlation_window():
    """
    ROUND 6 (Meta Muse Spark 1.3), F1, 13 September 2026. `window=30` was a
    bare keyword argument at engine_core.py's call site into
    compute_correlation_beta, nameable nowhere. Named at the one place it
    now lives: models.btc_context.CORRELATION_WINDOW, the function's own
    default.
    """
    from core.decision_log import MISSING, module_snapshot
    from models import btc_context

    snap = module_snapshot().get("models.btc_context", {})
    key = "CORRELATION_WINDOW"

    assert key in snap and snap[key] is not MISSING, (
        "the BTC correlation window is not in the record"
    )
    assert snap[key] == btc_context.CORRELATION_WINDOW


def test_module_snapshot_reaches_the_structure_hysteresis_threshold():
    """
    ROUND 6 (Meta Muse Spark 1.3), F1, 13 September 2026. The last of the
    six: 0.0015 was a bare local inside StructureEngine._detect_regime.
    Promoted to a class attribute -- the same shape
    DEGRADED_CONFIDENCE_CEILING already has -- so module_snapshot() needs
    the same two-hop ClassName.ATTR resolution to reach it.
    """
    from core.decision_log import MISSING, module_snapshot
    from structure.structure import StructureEngine

    snap = module_snapshot().get("structure.structure", {})
    key = "StructureEngine.REGIME_HYSTERESIS_THRESHOLD"

    assert key in snap and snap[key] is not MISSING, (
        "the structure regime hysteresis buffer is not in the record"
    )
    assert snap[key] == StructureEngine.REGIME_HYSTERESIS_THRESHOLD


def test_the_entry_scoring_constants_are_fingerprinted():
    """
    models.entry_model had no entry at all, while every entry score the engine
    prints is built out of its point budget.

    ROUND 6 (Meta Muse Spark 1.3), F1, 13 September 2026: the 1.05/0.90
    confluence multipliers Kimi named were bare literals in an if/elif
    ladder and were NOT here -- covered only by the source hash. Now named
    (CONFLUENCE_BOOST_MULT, CONFLUENCE_PENALTY_MULT) and included below like
    every other constant in this module; the source hash still covers them
    independently, same as everything else in this file.
    """
    from core.decision_log import MISSING, module_snapshot

    snap = module_snapshot().get("models.entry_model")
    assert snap, "models.entry_model is not fingerprinted at all"

    missing = [k for k, v in snap.items() if v is MISSING]
    assert not missing, (
        "these entry constants are named but do not resolve: "
        + ", ".join(missing)
    )
    not_numeric = [k for k, v in snap.items() if not isinstance(v, (int, float))]
    assert not not_numeric, (
        "these are not numbers, so the snapshot records something other than "
        "a setting: " + ", ".join(not_numeric)
    )


def test_regression_guard_no_fingerprinted_name_resolves_to_missing():
    """
    PASSES BOTH BEFORE AND AFTER, on purpose, and is counted as a regression
    guard rather than as evidence.

    Sequence item 14's finding generalised: a name in the record that resolves
    to nothing makes the record claim a knob exists that the code does not
    have. This holds the whole dict, not one module of it.

    ROUND 6 (Meta Muse Spark 1.3), F1, 13 September 2026: skipped rather than
    held to "passes both before and after" without pandas_ta.
    indicators.indicators (registered here for SPIKE_RATIO) hard-imports
    pandas_ta at module scope -- no module fingerprinted before this patch
    did. Without pandas_ta installed, module_snapshot() correctly records
    "<import failed>" for it, exactly as its own docstring says it should;
    that is not the sequence item 14 finding (a name silently resolving to
    nothing on a fully-installed engine), it is the documented shape for an
    optional dependency the engine itself already degrades around
    elsewhere. See test_module_snapshot_reaches_spike_ratio, which skips the
    same way for the same reason.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed -- indicators.indicators cannot "
                    "be imported, which is the documented <import failed> "
                    "shape, not a name resolving to MISSING")

    from core.decision_log import MISSING, module_snapshot

    bad = []
    for module_name, values in module_snapshot().items():
        if "<import failed>" in values:
            bad.append(f"{module_name}: import failed")
            continue
        bad += [f"{module_name}.{k}" for k, v in values.items() if v is MISSING]

    assert not bad, "fingerprinted names that resolve to nothing: " + ", ".join(bad)


def test_the_code_hash_is_deliberately_not_folded_into_the_run_hash():
    """
    HOLDS A DECISION, so that changing it is visible rather than silent.

    run_hash keeps its documented meaning -- which inputs, under which settings
    -- and code identity is a sibling field. The reason is in the call site's
    comment: run_hash is pinned by the golden snapshot and is the archive's
    filename, so folding code into it would fail the golden test on every
    commit and make re-baselining routine. Re-baselining is where a real change
    to a decision gets waved through.

    Asserted on the PARSE TREE rather than on the text, per rule 16: the
    comment beside that call discusses `code_id` at length, so a substring
    search would read the explanation as the thing it warns against.
    """
    source = io.open(os.path.join(REPO_ROOT, "core", "engine_core.py"),
                     encoding="utf-8").read()
    tree = ast.parse(source)

    calls = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "run_hash"
    ]
    assert calls, "no call to lineage.run_hash found in engine_core.py"

    for call in calls:
        names = {n.id for n in ast.walk(call) if isinstance(n, ast.Name)}
        assert "code_id" not in names, (
            "the source fingerprint has been folded into run_hash. That is a "
            "real option, but it moves run_hash and the archive filename on "
            "every commit, so tests/fixtures/golden_decision.json needs a "
            "re-baseline on every commit too. If that is intended, change this "
            "test and say why in the commit message."
        )


# ============================================================
# PART TWO — the fingerprint mechanism
#
# These import core/code_fingerprint.py, which this patch adds, so against
# pre-fix code they fail with ImportError and are NOT evidence that the defect
# was real. Rule 23.
# ============================================================

# Files copied into a throwaway tree so the mutation tests can edit the exact
# lines the finding names without touching the repository. Paths are relative
# to the repository root and are preserved in the copy, because the fingerprint
# hashes the path alongside the digest.
MUTABLE = [
    os.path.join("structure", "structure.py"),
    os.path.join("indicators", "indicators.py"),
    os.path.join("models", "decision_model.py"),
    os.path.join("core", "engine_core.py"),
    # ROUND 6 (Meta Muse Spark 1.3), F1, 13 September 2026: the correlation
    # window moved here from a bare call-site literal in engine_core.py --
    # see test_a_call_site_literal_moves_the_hash below.
    os.path.join("models", "btc_context.py"),
]


def _sandbox():
    """A temp tree holding real copies of the files the finding names."""
    root = tempfile.mkdtemp(prefix="phase7_fp_")
    for rel in MUTABLE:
        dest = os.path.join(root, rel)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copyfile(os.path.join(REPO_ROOT, rel), dest)
    return root


def _read(root, rel):
    with io.open(os.path.join(root, rel), encoding="utf-8") as fh:
        return fh.read()


def _write(root, rel, text, newline="\n"):
    with io.open(os.path.join(root, rel), "w", encoding="utf-8",
                 newline=newline) as fh:
        fh.write(text)


def _hash(root):
    from core.code_fingerprint import code_fingerprint
    return code_fingerprint(root)["code_hash"]


def _assert_moves(rel, old, new, why):
    """Replace `old` with `new` in one file and assert the hash moves."""
    root = _sandbox()
    try:
        before = _hash(root)
        source = _read(root, rel)
        assert source.count(old) >= 1, (
            f"the construct this test is about is no longer in {rel}: {old!r}. "
            f"The test is stale, not passing."
        )
        _write(root, rel, source.replace(old, new, 1))
        assert _hash(root) != before, why
    finally:
        shutil.rmtree(root, ignore_errors=True)


# --- the negative controls -----------------------------------------------

def test_negative_control_a_comment_does_not_move_the_hash():
    """
    NEGATIVE CONTROL. A fingerprint that moved on every edit would pass every
    "it moved" test below and carry no information at all -- the same amount a
    static string carries, which is what is being fixed.

    This project rewrites its explanatory comments in nearly every commit, so
    this is not a theoretical concern.
    """
    root = _sandbox()
    try:
        before = _hash(root)
        rel = MUTABLE[0]
        _write(root, rel, "# a comment that changes nothing computable\n"
               + _read(root, rel))
        assert _hash(root) == before, (
            "adding a comment moved the code hash. The hash is over the parse "
            "tree precisely so that it does not."
        )
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_negative_control_a_docstring_does_not_move_the_hash():
    """
    NEGATIVE CONTROL, and the reason _strip_docstrings exists. A docstring
    survives ast.parse as a string constant, so without stripping it the parse
    tree would carry every word of the prose this repository is full of.
    """
    root = _sandbox()
    try:
        before = _hash(root)
        rel = MUTABLE[2]
        source = _read(root, rel)
        marker = '"""'
        assert marker in source, "no docstring to edit in " + rel
        _write(root, rel, source.replace(marker, marker + "EDITED. ", 1))
        assert _hash(root) == before, (
            "editing a docstring moved the code hash"
        )
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_negative_control_line_endings_do_not_move_the_hash():
    """
    NEGATIVE CONTROL, and this repository has paid for it before:
    tests/test_pinned_source.py fails on any LF checkout because a hash was
    taken over bytes that carry line endings.

    A run's code identity must not depend on whether it was checked out on
    Windows or Linux, or the field cannot be compared across machines -- which
    is most of what a shared record is for.
    """
    root = _sandbox()
    try:
        before = _hash(root)
        for rel in MUTABLE:
            _write(root, rel, _read(root, rel), newline="\r\n")
        assert _hash(root) == before, (
            "the same source checked out with CRLF hashes differently from "
            "the same source with LF"
        )
    finally:
        shutil.rmtree(root, ignore_errors=True)


# --- the seven settings the finding names ---------------------------------

def test_a_bare_literal_moves_the_hash():
    """
    `0.0015` in structure.py, the seventh of the seven. It was assigned to a
    function local with no name anything outside the function could ask for,
    the clearest case an enumeration could never have covered.

    ROUND 6 (Meta Muse Spark 1.3), F1, 13 September 2026: promoted to
    StructureEngine.REGIME_HYSTERESIS_THRESHOLD, a class attribute, and now
    ALSO nameable in FINGERPRINTED_MODULES via module_snapshot()'s two-hop
    resolution -- the same shape DEGRADED_CONFIDENCE_CEILING already has. It
    stays here, retargeted at the new construct, for the same reason that
    test kept its own name: the source hash covers it independently of
    whether a dict also names it.
    """
    _assert_moves(
        MUTABLE[0], "REGIME_HYSTERESIS_THRESHOLD = 0.0015",
        "REGIME_HYSTERESIS_THRESHOLD = 0.0016",
        "changing the 0.15% structure buffer left the code hash identical",
    )


def test_a_function_local_moves_the_hash():
    """`SPIKE_RATIO`, a local inside a function. Same argument."""
    _assert_moves(
        MUTABLE[1], "SPIKE_RATIO = 10.0", "SPIKE_RATIO = 12.0",
        "changing the volume spike ratio left the code hash identical",
    )


def test_a_class_attribute_moves_the_hash():
    """
    `DEGRADED_CONFIDENCE_CEILING`. It is now ALSO nameable in
    FINGERPRINTED_MODULES, which is why part one has a test for it -- but it
    became nameable only because module_snapshot learned dotted paths, and the
    source hash covers it without needing to be told.
    """
    _assert_moves(
        MUTABLE[2], "DEGRADED_CONFIDENCE_CEILING = 50.0",
        "DEGRADED_CONFIDENCE_CEILING = 60.0",
        "changing the degraded confidence ceiling left the code hash identical",
    )


def test_a_call_site_literal_moves_the_hash():
    """
    `window=30` was a keyword argument at engine_core.py's call site,
    restating compute_correlation_beta's own default and nameable nowhere.

    ROUND 6 (Meta Muse Spark 1.3), F1, 13 September 2026: the call-site
    literal is gone outright rather than renamed -- engine_core.py now
    relies on the function's own default. The number lives exactly once,
    as models.btc_context.CORRELATION_WINDOW, ALSO nameable in
    FINGERPRINTED_MODULES now. Retargeted at that module rather than
    deleted, for the same reason as the test above.
    """
    _assert_moves(
        MUTABLE[4], "CORRELATION_WINDOW = 30", "CORRELATION_WINDOW = 45",
        "changing the BTC correlation window left the code hash identical",
    )


def test_a_changed_comparison_moves_the_hash():
    """
    Not one of the seven, and the reason the fix is a source hash rather than a
    longer list. An enumeration of constants cannot see an operator change, and
    `>=` becoming `>` on a trend band changes which runs authorise a trade
    without changing any constant at all.
    """
    _assert_moves(
        MUTABLE[2], "if trend_health >= 75 and entry_score >= 70",
        "if trend_health > 75 and entry_score >= 70",
        "changing a trend-band comparison left the code hash identical",
    )


# --- the walk and its failure modes ---------------------------------------

def test_adding_a_source_file_moves_the_hash():
    """A new module is new code, and the hash is over the set as well as the contents."""
    root = _sandbox()
    try:
        before = _hash(root)
        _write(root, "new_module.py", "CONSTANT = 1\n")
        assert _hash(root) != before, "adding a source file left the hash identical"
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_removing_a_source_file_moves_the_hash():
    root = _sandbox()
    try:
        before = _hash(root)
        os.remove(os.path.join(root, MUTABLE[0]))
        assert _hash(root) != before, "removing a source file left the hash identical"
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_a_file_that_does_not_parse_is_recorded_rather_than_skipped():
    """
    The same argument config_snapshot makes about a missing name: a record that
    looks complete and is not leaves the reader nothing to notice. A file that
    stops parsing must change the hash, not drop quietly out of it.
    """
    from core.code_fingerprint import PARSE_FAILED, code_fingerprint

    root = _sandbox()
    try:
        before = _hash(root)
        rel = MUTABLE[0]
        _write(root, rel, "def broken(:\n")
        fp = code_fingerprint(root)
        assert fp["code_hash"] != before, (
            "a file that no longer parses left the code hash identical"
        )
        entry = fp["files"][rel.replace(os.sep, "/")]
        assert entry.startswith(PARSE_FAILED[:14]), (
            f"an unparseable file recorded {entry!r} rather than a stated failure"
        )
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_the_hash_is_stable_across_two_calls_on_unchanged_source():
    """
    Determinism, asserted directly. A fingerprint that differs between two
    calls on identical input is worse than none: every comparison it is used
    for reports a difference, so a real one cannot be seen.
    """
    from core.code_fingerprint import code_fingerprint
    first = code_fingerprint()
    second = code_fingerprint()
    assert first["code_hash"] == second["code_hash"]
    assert first["files"] == second["files"]


def test_the_walk_covers_the_engine_and_excludes_the_tests():
    """
    The exclusion is of DIRECTORIES and never of individual files, and this
    pins that choice.

    Tests and PDF builders cannot change what the engine decides, so they are
    out. `run_tests.py` is not on the decision path either and is deliberately
    IN, because a per-file exclusion list is exactly the decaying thing this
    module replaces -- and the two errors are not symmetric. Including a file
    that cannot matter costs a reader a moment; excluding one that can
    reproduces the defect.
    """
    from core.code_fingerprint import iter_source_files

    files = set(iter_source_files())

    for required in ("core/engine_core.py", "core/decision_log.py",
                     "models/decision_model.py", "models/entry_model.py",
                     "indicators/indicators.py", "structure/structure.py",
                     "core/config.py", "run_tests.py"):
        assert required in files, f"{required} is not fingerprinted"

    strayed = sorted(f for f in files
                     if f.startswith("tests/") or f.startswith("docs/"))
    assert not strayed, (
        "the walk descended into an excluded directory: " + ", ".join(strayed)
    )


def test_the_fingerprint_carries_the_interpreter_version():
    """
    ast.dump is a CPython implementation detail and its output changes when the
    AST gains node fields between versions, so two runs on identical source
    under different interpreters can record different hashes.

    That is recorded rather than worked around. Without the version beside the
    hash, a reader comparing two records has no way to tell an interpreter
    change from a code change -- and would reasonably assume the code moved.
    """
    from core.code_fingerprint import code_fingerprint
    fp = code_fingerprint()
    assert fp.get("python"), "the fingerprint does not say which interpreter took it"
    assert fp.get("format"), "the fingerprint does not say which serialisation it is"
