"""
Tier 1, Task 12 (18 September 2026) -- extending the ignored-file filter.

THE FINDING

check_ignored_files' own docstring explains the blind spot it exists to
close: an ignored file does not show up in a plain `git status --short`. But
until this change, the routine-noise filter (_ROUTINE_IGNORED_MARKERS) did
not cover logs/ (rewritten by the engine on every run -- see the
.gitignore's "LOGS & OUTPUT" section) or the generated content under
docs/audit_package/round*/ (rebuilt from the repository by
docs/build/build_audit_package.py -- see that .gitignore section's own
comment). Both are pure regenerated build output, the same class already
filtered for __pycache__ and .pytest_cache -- so both printed as "review,
don't assume harmless" on every session where an engine run or an audit
package rebuild had happened, which is most of them, burying whatever a
real surprise would have looked like among routine, expected clutter.

WHAT THIS DOES NOT TOUCH

The original incident this check exists for -- reviewer responses under
docs/audit_package/round*/ going unnoticed -- was already fixed by the
.gitignore's own negation rules (MANIFEST.md and docs/audit_reports/**/*.json
are un-ignored, so they are TRACKED and show up in git status normally,
filter or no filter). This change touches only the leftover derived noise
inside round*/ that negation does not cover, not those negation rules.

WHY A THROWAWAY REPO AND NOT THIS ONE

check_ignored_files reads real ignored files off disk via git itself. The
actual repo's logs/ and docs/audit_package/round*/ are usually empty of
generated content between sessions, so asserting against them would mostly
prove nothing. A small, disposable git repo with a matching .gitignore
reproduces the exact shapes git status --ignored --short returns for a
populated logs/ and a populated round*/ directory.
"""

import os
import importlib.util
import shutil
import subprocess
import tempfile
from pathlib import Path

from conftest import REPO_ROOT

MODULE_PATH = os.path.join(REPO_ROOT, "docs", "build", "session_handover_check.py")

GITIGNORE_BODY = (
    "logs/\n"
    "logs/**\n"
    "docs/audit_package/round*/*\n"
    "!docs/audit_package/round*/MANIFEST.md\n"
    "*.secret\n"
)


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "phase7_session_handover_check", MODULE_PATH
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _run(args, cwd):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True)


def _fresh_ignoring_repo():
    """A throwaway git repo with this project's real ignore shapes."""
    work = tempfile.mkdtemp(prefix="phase7_handover_check_")
    _run(["git", "init", "-q"], cwd=work)
    _run(["git", "config", "user.email", "test@example.com"], cwd=work)
    _run(["git", "config", "user.name", "test"], cwd=work)
    with open(os.path.join(work, ".gitignore"), "w") as f:
        f.write(GITIGNORE_BODY)
    _run(["git", "add", ".gitignore"], cwd=work)
    _run(["git", "commit", "-q", "-m", "initial"], cwd=work)
    return work


def test_engine_output_directories_are_filtered_as_routine():
    module = _load_module()
    work = _fresh_ignoring_repo()
    try:
        os.makedirs(os.path.join(work, "logs"))
        with open(os.path.join(work, "logs", "phase7_state_AEROUSDT_4h.json"), "w") as f:
            f.write("{}")

        round_dir = os.path.join(work, "docs", "audit_package", "round7")
        os.makedirs(round_dir)
        with open(os.path.join(round_dir, "MANIFEST.md"), "w") as f:
            f.write("tracked manifest\n")
        with open(os.path.join(round_dir, "phase7_engine_source.md"), "w") as f:
            f.write("generated content\n")

        flagged = module.check_ignored_files(Path(work))
        assert flagged == [], (
            f"routine engine/build output was flagged for review: {flagged}"
        )
    finally:
        shutil.rmtree(work, ignore_errors=True)


def test_an_unrelated_ignored_file_still_surfaces():
    """
    THE NEGATIVE CONTROL.

    Extending the filter must not turn it into a blanket "ignore everything"
    -- something the existing markers do not already cover must still print,
    or this filter has become exactly the blind spot check_ignored_files
    exists to close.
    """
    module = _load_module()
    work = _fresh_ignoring_repo()
    try:
        with open(os.path.join(work, "mystery.secret"), "w") as f:
            f.write("not routine")

        flagged = module.check_ignored_files(Path(work))
        assert any("mystery.secret" in line for line in flagged), (
            f"an unrelated ignored file was filtered out along with the "
            f"routine noise: {flagged}"
        )
    finally:
        shutil.rmtree(work, ignore_errors=True)


def test_the_original_negation_rules_are_unaffected():
    """
    The MANIFEST.md / audit_reports negation rules are what actually fixed
    the original incident this file's docstring describes -- they make those
    files TRACKED, not merely unfiltered here. This pins that a file under
    round*/ that the negation rule covers is untracked-and-visible (git
    considers it a normal new file, not an ignored one) regardless of the
    routine-noise filter added by this change.
    """
    work = _fresh_ignoring_repo()
    try:
        manifest_dir = os.path.join(work, "docs", "audit_package", "round7")
        os.makedirs(manifest_dir)
        manifest_path = os.path.join(manifest_dir, "MANIFEST.md")
        with open(manifest_path, "w") as f:
            f.write("tracked manifest\n")

        status = _run(["git", "status", "--short", manifest_path], cwd=work).stdout
        assert status.strip().startswith("??"), (
            f"MANIFEST.md is not untracked-and-visible as expected: {status!r}"
        )
    finally:
        shutil.rmtree(work, ignore_errors=True)
