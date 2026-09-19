"""
The pre-push hook (19 September 2026).

WHAT IS BEING PINNED

githooks/pre-push runs docs/build/session_handover_check.py on every
`git push` and stops the push when it exits non-zero. Viktor's ruling
(option A): a finding stops the push, he consults, and overrides with
`git push --no-verify` if the answer is push. The hook fails closed -- if
the check cannot run at all, the push is stopped too.

The tests below push for real, from a throwaway repo to a throwaway bare
remote, so what they check is git's actual behaviour running the hook --
not a reading of the hook's source. Each "stopped" test is paired with a
clean push that goes through, so a hook that stopped everything (or never
ran) cannot pass them.

PLATFORM NOTE

On Windows, git runs the hook with Git for Windows' own sh, and the hook
finds `python` on PATH the same way the test run did. On Linux and macOS,
git also requires the hook's executable bit -- read off the working-tree
file, not the index. The throwaway repos set both: os.chmod on the file,
and `git update-index --chmod=+x` in the index (the command the real
repo's section-6 check tells you to run). Leaving out the os.chmod made
the first draft of these tests fail on Linux: git skipped the hook with a
hint on stderr and every push went through.

The hook itself must stay LF (a CRLF line breaks sh). The first two tests
check that on the real repository: the .gitattributes rule, and the bytes
actually on disk.

No fixtures: run_tests.py calls every test_* with no arguments.
"""

import importlib.util
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from conftest import REPO_ROOT

HOOK_REL = "githooks/pre-push"
CHECK_REL = "docs/build/session_handover_check.py"
HOOK_PATH = os.path.join(REPO_ROOT, "githooks", "pre-push")
CHECK_PATH = os.path.join(REPO_ROOT, "docs", "build", "session_handover_check.py")


def _run(args, cwd):
    # The timeout is load-bearing, not tidiness. Measured on Linux git 2.43:
    # when the hook cannot be executed at all (a CRLF shebang makes the
    # interpreter "/bin/sh\r"), `git push` prints "cannot exec" and then
    # HANGS rather than failing. Without a timeout, a broken hook would stall
    # the whole suite instead of failing a test. Not checked on Git for
    # Windows, which resolves the shebang itself.
    return subprocess.run(
        args, cwd=cwd, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=120,
    )


def _git(cwd, *args):
    result = _run(["git", *args], cwd=cwd)
    assert result.returncode == 0, f"git {' '.join(args)} failed: {result.stderr}"
    return result.stdout.strip()


def _load_check_module():
    spec = importlib.util.spec_from_file_location(
        "phase7_session_handover_check_hooks", CHECK_PATH
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _copy_bytes(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(src, "rb") as f:
        data = f.read()
    with open(dst, "wb") as f:
        f.write(data)


def _repo_with_hook(install=True):
    """A throwaway work repo carrying the real hook and check, plus a bare remote.

    Returns (base_dir, work_dir, remote_dir). The work repo has one commit,
    not yet pushed.
    """
    base = tempfile.mkdtemp(prefix="phase7_pre_push_")
    work = os.path.join(base, "work")
    remote = os.path.join(base, "remote.git")
    os.makedirs(work)
    _git(base, "init", "-q", "--bare", remote)
    _git(work, "init", "-q")
    _git(work, "config", "user.email", "test@example.com")
    _git(work, "config", "user.name", "test")
    _git(work, "config", "core.autocrlf", "false")
    hook_copy = os.path.join(work, "githooks", "pre-push")
    _copy_bytes(HOOK_PATH, hook_copy)
    # Linux/macOS git reads the executable bit off the working-tree file, not
    # the index -- without this it skips the hook with only a hint on stderr,
    # and every push goes through. (No effect on Windows, where git runs the
    # hook regardless.)
    os.chmod(hook_copy, 0o755)
    _copy_bytes(CHECK_PATH, os.path.join(work, "docs", "build", "session_handover_check.py"))
    with open(os.path.join(work, "README.md"), "w") as f:
        f.write("throwaway\n")
    _git(work, "add", "-A")
    _git(work, "update-index", "--chmod=+x", HOOK_REL)
    _git(work, "commit", "-q", "-m", "initial")
    _git(work, "remote", "add", "origin", remote)
    if install:
        _git(work, "config", "core.hooksPath", "githooks")
    return base, work, remote


def _push(work, *extra):
    return _run(["git", "push", *extra, "origin", "HEAD:refs/heads/main"], cwd=work)


def _remote_head(remote):
    result = _run(["git", "rev-parse", "--verify", "-q", "refs/heads/main"], cwd=remote)
    return result.stdout.strip() if result.returncode == 0 else None


# ---------------------------------------------------------------------------
# The real repository's copy of the hook
# ---------------------------------------------------------------------------

def test_gitattributes_pins_the_hook_to_lf():
    out = _git(REPO_ROOT, "check-attr", "eol", "--", HOOK_REL)
    assert out.endswith("eol: lf"), (
        f".gitattributes does not pin {HOOK_REL} to LF: {out!r}. On a Windows "
        f"checkout `* text=auto` would give it CRLF and sh would break on it."
    )


def test_the_hook_on_disk_has_no_carriage_returns():
    with open(HOOK_PATH, "rb") as f:
        data = f.read()
    assert data.startswith(b"#!/bin/sh\n"), "hook does not start with an LF shebang line"
    assert b"\r" not in data, (
        f"{HOOK_REL} contains CR bytes -- sh reads them as part of each command. "
        f"Re-check it out after .gitattributes' eol=lf rule is in place."
    )


# ---------------------------------------------------------------------------
# The hook's behaviour, by pushing for real
# ---------------------------------------------------------------------------

def test_a_clean_tree_pushes_through():
    """THE NEGATIVE CONTROL for every 'stopped' test below."""
    base, work, remote = _repo_with_hook()
    try:
        result = _push(work)
        assert result.returncode == 0, (
            f"a clean push was stopped:\n{result.stdout}\n{result.stderr}"
        )
        assert _remote_head(remote) == _git(work, "rev-parse", "HEAD")
        assert "SUMMARY: clean" in result.stdout + result.stderr, (
            "the push went through but the check's output is absent -- "
            "the hook may not have run at all"
        )
    finally:
        shutil.rmtree(base, ignore_errors=True)


def test_a_flagged_tree_stops_the_push():
    base, work, remote = _repo_with_hook()
    try:
        assert _push(work).returncode == 0
        pushed = _remote_head(remote)

        with open(os.path.join(work, "notes.txt"), "w") as f:
            f.write("second commit\n")
        _git(work, "add", "notes.txt")
        _git(work, "commit", "-q", "-m", "second")
        with open(os.path.join(work, "stray.txt"), "w") as f:
            f.write("untracked -- the check must flag this\n")

        result = _push(work)
        output = result.stdout + result.stderr
        assert result.returncode != 0, f"a flagged push went through:\n{output}"
        assert _remote_head(remote) == pushed, "the remote moved despite the stop"
        assert "stray.txt" in output, "the finding itself was not shown"
        assert "push STOPPED" in output
    finally:
        shutil.rmtree(base, ignore_errors=True)


def test_no_verify_overrides_the_stop():
    """The override the ruling relies on: the decision stays Viktor's."""
    base, work, remote = _repo_with_hook()
    try:
        with open(os.path.join(work, "stray.txt"), "w") as f:
            f.write("untracked\n")
        assert _push(work).returncode != 0
        assert _remote_head(remote) is None

        result = _push(work, "--no-verify")
        assert result.returncode == 0, result.stderr
        assert _remote_head(remote) == _git(work, "rev-parse", "HEAD")
    finally:
        shutil.rmtree(base, ignore_errors=True)


def test_the_push_is_stopped_when_the_check_cannot_run():
    """Fails closed: a missing check script stops the push rather than passing it."""
    base, work, remote = _repo_with_hook()
    try:
        _git(work, "rm", "-q", CHECK_REL)
        _git(work, "commit", "-q", "-m", "remove the check")

        result = _push(work)
        output = result.stdout + result.stderr
        assert result.returncode != 0, f"push went through with no check:\n{output}"
        assert _remote_head(remote) is None
        assert "could not run" in output
    finally:
        shutil.rmtree(base, ignore_errors=True)


# ---------------------------------------------------------------------------
# Section 6 of the check: is the hook installed in this clone?
# ---------------------------------------------------------------------------

def test_hooks_check_is_clean_when_installed():
    """THE NEGATIVE CONTROL for the two section-6 tests below."""
    module = _load_check_module()
    base, work, _ = _repo_with_hook(install=True)
    try:
        assert module.check_hooks_path(Path(work)) == []
    finally:
        shutil.rmtree(base, ignore_errors=True)


def test_hooks_check_flags_a_clone_without_hooks_path():
    module = _load_check_module()
    base, work, _ = _repo_with_hook(install=False)
    try:
        problems = module.check_hooks_path(Path(work))
        assert any("core.hooksPath" in p for p in problems), problems
    finally:
        shutil.rmtree(base, ignore_errors=True)


def test_hooks_check_flags_a_hook_tracked_without_the_executable_bit():
    module = _load_check_module()
    base, work, _ = _repo_with_hook(install=True)
    try:
        _git(work, "update-index", "--chmod=-x", HOOK_REL)
        problems = module.check_hooks_path(Path(work))
        assert any("100644" in p for p in problems), problems
    finally:
        shutil.rmtree(base, ignore_errors=True)
