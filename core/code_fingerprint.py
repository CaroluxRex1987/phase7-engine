"""
The run's CODE identity -- Kimi Finding 3, round 4 (Item 5, Reproducibility).

WHY THIS FILE EXISTS

Two runs made on different code recorded identical hashes.

`config.engine_version` is the string "Phase-7 Structural Quant Engine v1.0"
and has not changed across any commit in this repository's history. The other
half of the record, `decision_log.FINGERPRINTED_MODULES`, is an enumeration of
constant names -- and the finding lists seven decision-affecting settings it
does not contain:

    DEGRADED_CONFIDENCE_CEILING   models/decision_model.py:102
    BTC_ADJUSTMENT_CAP            models/decision_model.py:679
    the entry confluence multipliers (1.05 / 0.90)
                                  models/entry_model.py:362-400
    the trend bands (75 / 50 / 25) indicators/trend_health.py:343-345,
                                  models/decision_model.py:440-491
    SPIKE_RATIO                   indicators/indicators.py:719
    window=30                     core/engine_core.py:767
    0.0015                        structure/structure.py:140

THE LIST CANNOT BE FIXED BY EXTENDING THE LIST

That is the part worth being precise about, because the obvious remedy is to
add seven names to FINGERPRINTED_MODULES and call it closed. It does not work.
`module_snapshot()` reads a name with `getattr(module, name)`, and of the seven:

    DEGRADED_CONFIDENCE_CEILING   a CLASS attribute of DecisionModel
    BTC_ADJUSTMENT_CAP            a CLASS attribute of DecisionModel
    SPIKE_RATIO                   a LOCAL variable inside a function
    the entry multipliers         bare literals in an if/elif ladder
    the trend bands               bare literals in comparisons
    window=30                     a literal at a call site
    0.0015                        a bare literal assigned to a local

Exactly none of the last five can be reached by `getattr` on a module, and the
first two required moving the constants -- which is what
`models/risk_model.py` had to do in September to become fingerprintable at all.
Six of the seven are not omissions from a list. They are things a list of that
shape structurally cannot hold.

And the finding is narrower than the defect. An enumeration of constants cannot
see a changed comparison operator, a reordered branch, a swapped `>=` for `>`,
or a whole new term added to a formula. All of those change what the engine
decides, and all of them left the record byte-identical.

Rule 11 in PHASE7_NEXT.md: *a list of names is a claim about the code, and it
decays.* Rule 16: *a guard written from a list of examples inherits the gaps in
that list.* Rule 28: where a mistake cannot be undone, change the structure
rather than writing an instruction to be careful. Adding seven names would
satisfy the finding's letter and leave the mechanism that produced it intact,
ready to be short by seven more the next time somebody adds a constant.

WHAT THIS DOES INSTEAD

It fingerprints the source itself. For every `.py` file under the repository
root that is not in an excluded directory:

    read the bytes -> ast.parse -> strip docstrings -> ast.dump -> SHA-256

and the run's `code_hash` is a SHA-256 over the sorted (path, digest) pairs.
No list of constants, no list of modules. A constant added tomorrow is covered
the moment it is written, because it is in the file.

WHY THE PARSE TREE AND NOT THE TEXT

Hashing the source text would work and would be wrong in practice. This project
rewrites its explanatory comments in nearly every commit -- this docstring is
sixty lines of it -- so a text hash would move on every commit regardless of
whether anything computable changed. A fingerprint that always differs carries
the same amount of information as one that never differs, which is none.

`ast.parse` discards comments and formatting and keeps every literal, every
operator and every branch. `ast.dump(..., include_attributes=False)` also
discards line and column numbers, so inserting a comment above a function does
not move the digest of that function. Docstrings survive parsing as string
constants and are stripped here explicitly, for the same reason comments are
not wanted.

The test for the boundary is a pair of negative controls in
tests/test_code_fingerprint.py: editing a comment or a docstring must NOT move
the hash, and changing `0.0015` to `0.0016` must.

Matching on the parse tree rather than on text is the same technique rule 16
required of the source guards in the Finding 5 item 6 patch, applied to a
different problem.

WHAT IS DELIBERATELY OVER-INCLUSIVE

The walk excludes DIRECTORIES and never individual files -- `tests/` (a test
cannot change what the engine decides), `docs/` (PDF builders and audit
records), plus caches, virtualenvs and version-control metadata. Everything
else is in, including `run_tests.py`, `test_live.py` and `utils/plotting.py`,
none of which sits on the decision path.

That is a deliberate choice and not an oversight. A per-file exclusion list is
the decaying thing this file exists to replace, and the two errors are not
symmetric: including a file that cannot affect a decision makes the hash move
when nothing important changed, which costs a reader thirty seconds of looking.
Excluding a file that CAN affect a decision reproduces the defect. The question
this field answers is "is this the same source tree", and it is allowed to be
strict about it.

WHAT IT DOES NOT SURVIVE

`ast.dump` is a CPython implementation detail and its output changes when the
AST gains node fields between interpreter versions. Two runs on identical
source under Python 3.12 and 3.13 can therefore record different `code_hash`
values. This is recorded rather than worked around: `python` is carried beside
the hash in the fingerprint dict and written into the archive meta, so a reader
comparing two hashes can see whether the interpreter is the reason. Comparing
hashes across interpreter versions is not meaningful and the record now says so
instead of leaving it to be discovered.

WHAT THIS IS NOT

It is not folded into `run_hash`. See core/engine_core.py at the call site for
that decision and its reasoning, and
tests/test_code_fingerprint.py::test_the_code_hash_is_deliberately_not_in_the_run_hash
which holds it so that a later change to it is visible rather than silent.
"""

import ast
import hashlib
import os
import platform

# The serialisation this file produces. Bumped when anything below changes the
# bytes that go into a digest, so two hashes are never compared across two
# different definitions of what a hash means. Same contract as
# lineage.CANONICAL_FORMAT.
CODE_FORMAT = 1

# The repository root: this file lives in core/, so one level up.
SOURCE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Directories whose contents cannot change what the engine decides. Names, not
# paths, matched at every level of the walk. See "WHAT IS DELIBERATELY
# OVER-INCLUSIVE" above for why this list is of directories and never of files.
EXCLUDED_DIR_NAMES = frozenset({
    "tests",            # a test does not change the engine's output
    "docs",             # PDF builders, audit packages, reviewer responses
    ".git",
    "__pycache__",
    ".pytest_cache",
    "venv", "env", "aider-env", ".venv",
    "Backup",
    "logs", "Logs",
    # 9 September 2026. Session backups and handoff patches under this name
    # carried .py copies into the walk and moved code_hash without any engine
    # change (Grok sweep session). Not engine source.
    "Claude outputs",
})

PARSE_FAILED = "<parse failed: {}>"


def _posix(path):
    """
    A path spelled the same way on every platform.

    The same argument lineage._posix() makes, and the same defect: these
    strings go into the digest and into a permanent record read on other
    machines, so `core\\config.py` on Windows and `core/config.py` on Linux
    must not be two different runs.
    """
    return str(path).replace("\\", "/")


def _strip_docstrings(tree):
    """
    Remove module, class and function docstrings from a parsed tree, in place.

    A docstring is a string expression as the first statement of a body, and it
    is the one piece of prose that survives parsing. Left in, it would put this
    file's own eighty-line header inside the hash and move it on every edit --
    the text-hash problem the parse tree was chosen to avoid, reintroduced
    through the back door.
    """
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if not isinstance(body, list) or not body:
            continue
        if not isinstance(node, (ast.Module, ast.ClassDef,
                                 ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        first = body[0]
        if (isinstance(first, ast.Expr)
                and isinstance(first.value, ast.Constant)
                and isinstance(first.value.value, str)):
            # Replaced rather than deleted. A function whose entire body is a
            # docstring becomes syntactically invalid with an empty body, and
            # `pass` is what the author would have written.
            body[0] = ast.Pass()
    return tree


def file_fingerprint(path):
    """
    SHA-256 of one file's docstring-stripped parse tree.

    A file that cannot be parsed records the reason instead of being skipped,
    for the reason decision_log.config_snapshot() gives about a missing name: a
    record that looks complete and is not leaves the reader unable to tell an
    absent value from one that was never asked for. The reason string is itself
    part of the digest, so a file that starts failing to parse changes the
    run's code hash rather than quietly dropping out of it.
    """
    try:
        with open(path, "rb") as fh:
            source = fh.read()
        # Decoded explicitly rather than opened in text mode: text mode applies
        # universal newlines and a platform default encoding, and this digest
        # must not depend on either. CRLF and LF produce the same parse tree.
        tree = _strip_docstrings(ast.parse(source.decode("utf-8")))
        dumped = ast.dump(tree, annotate_fields=True, include_attributes=False)
    except Exception as exc:
        return PARSE_FAILED.format(exc)
    return hashlib.sha256(dumped.encode("utf-8")).hexdigest()


def iter_source_files(root=None):
    """
    Every `.py` file under `root` that is not in an excluded directory.

    Returns paths relative to `root`, in POSIX spelling, sorted -- so the set
    is ordered by the content of the tree and not by the order the filesystem
    happened to hand it over.
    """
    root = SOURCE_ROOT if root is None else root
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        # Pruned in place, which is what stops os.walk descending into them.
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIR_NAMES]
        for name in filenames:
            if name.endswith(".py"):
                full = os.path.join(dirpath, name)
                found.append(_posix(os.path.relpath(full, root)))
    return sorted(found)


def code_fingerprint(root=None):
    """
    The run's code identity.

        {"format": int, "python": str, "code_hash": str,
         "files": {relative_path: digest}}

    `code_hash` is a SHA-256 over the sorted (path, digest) pairs, so it moves
    when a file's contents change, when a file is added, and when one is
    removed. `files` says WHICH file moved, which a single hash cannot -- the
    difference between knowing two runs are not the same run and being able to
    do anything about it.
    """
    root = SOURCE_ROOT if root is None else root
    files = {rel: file_fingerprint(os.path.join(root, rel))
             for rel in iter_source_files(root)}

    # The digest is over an explicit, unambiguous serialisation rather than
    # over repr() of a dict: a separator that can occur inside a path would let
    # two different trees produce one string, and NUL cannot occur in either a
    # path or a hex digest.
    payload = "\0".join(f"{rel}\0{files[rel]}" for rel in sorted(files))
    payload = f"{CODE_FORMAT}\0{payload}"

    return {
        "format": CODE_FORMAT,
        # Recorded, not hashed. See "WHAT IT DOES NOT SURVIVE" above: this is
        # what lets a reader tell an interpreter change from a code change.
        "python": platform.python_version(),
        "code_hash": hashlib.sha256(payload.encode("utf-8")).hexdigest(),
        "files": files,
    }
