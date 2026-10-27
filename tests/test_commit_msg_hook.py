"""
The commit-msg hook (entry 56, ruled 27 October 2026).

WHAT IS BEING PINNED

githooks/commit-msg refuses a commit whose staged tree is not the tree its
message names on its `Verified-Tree:` line (DECISIONS, "Ruling, 27 October
2026 -- a commit names the tree verified before delivery"). The tree it
checks is `git write-tree` of the index git is committing from, so a file
left out of `git add`, a wrong file or a lost executable bit stops the
commit before it exists. A message that names no tree unambiguously -- two
such lines, or one not written exactly as `Verified-Tree: ` and forty
lowercase hex digits -- is stopped too. So is a message with no such line:
Viktor's ruling of the same day, by agreeing to Claude's suggestion
(DECISIONS, "Ruling, 27 October 2026 -- the commit-msg hook stops a message
with no `Verified-Tree:` line"). The override, as for the pre-push hook, is
`git commit --no-verify`.

The tests below commit for real, in throwaway repos, so what they check is
git's actual behaviour running the hook -- not a reading of its source. Each
"stopped" test is paired with a commit that goes through, so a hook that
stopped everything cannot pass them; and that commit must print the hook's
own line, so a hook that never ran cannot pass it either.

WHAT IS NOT TESTED, AND WHY

The hook also stops a commit when it cannot read the message or when
`git write-tree` fails. Neither could be reached through `git commit`: git
hands the hook the message file itself, and an index whose tree cannot be
built stopped git's own commit before the hook ran (tried on Linux, git
2.43: "Error building trees", the hook not run). Both stay in the hook as
defence in depth, untested.

PLATFORM NOTE

As in tests/test_pre_push_hook.py: on Linux and macOS git runs a hook only
if the working-tree file is executable, so the throwaway repos chmod their
copy; Git for Windows runs it regardless, with its own sh. The hook must
stay LF (a CRLF line breaks sh); the first two tests check that on the real
repository.

The executable bit in the real repository's index is not tested here: the
suite runs before Viktor's `git add` steps, when the hook is not yet
tracked. The bit is part of the tree a commit names, so a commit that
records the hook without it is refused by the hook itself.

No fixtures: run_tests.py calls every test_* with no arguments.
"""

import os
import shutil
import subprocess
import tempfile

from conftest import REPO_ROOT

HOOK_REL = "githooks/commit-msg"
HOOK_PATH = os.path.join(REPO_ROOT, "githooks", "commit-msg")

# What the hook prints when the staged tree is the one the message names.
PASSED_LINE = "the one Verified-Tree names"
STOPPED_LINE = "commit STOPPED"


def _run(args, cwd):
    # A timeout, as in tests/test_pre_push_hook.py: a hook git cannot execute
    # made `git push` hang there (Linux, git 2.43). `git commit` was seen to
    # fail instead ("cannot exec"), but a hang would stall the whole suite.
    return subprocess.run(
        args, cwd=cwd, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=120,
    )


def _git(cwd, *args):
    result = _run(["git", *args], cwd=cwd)
    assert result.returncode == 0, f"git {' '.join(args)} failed: {result.stderr}"
    return result.stdout.strip()


def _write(path, text, newline="\n"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(text.replace("\n", newline).encode("utf-8"))


def _repo_with_hook():
    """A throwaway repo with one commit, the real hook switched on after it.

    Returns (base_dir, work_dir). The hook is copied byte for byte and left
    untracked: git finds it through core.hooksPath, tracked or not.
    """
    base = tempfile.mkdtemp(prefix="phase7_commit_msg_")
    work = os.path.join(base, "work")
    os.makedirs(work)
    _git(work, "init", "-q")
    _git(work, "config", "user.email", "test@example.com")
    _git(work, "config", "user.name", "test")
    _git(work, "config", "core.autocrlf", "false")
    _write(os.path.join(work, "a.txt"), "one\n")
    _git(work, "add", "a.txt")
    _git(work, "commit", "-q", "-m", "initial")
    hook_copy = os.path.join(work, "githooks", "commit-msg")
    os.makedirs(os.path.dirname(hook_copy))
    with open(HOOK_PATH, "rb") as f:
        data = f.read()
    with open(hook_copy, "wb") as f:
        f.write(data)
    # Linux/macOS git reads the executable bit off the working-tree file and
    # skips a hook without it, with only a hint on stderr. (No effect on
    # Windows, where git runs the hook regardless.)
    os.chmod(hook_copy, 0o755)
    _git(work, "config", "core.hooksPath", "githooks")
    return base, work


def _message(tree_line, newline="\r\n"):
    """A commit message shaped like a delivered one.

    CRLF by default, as the delivered message files are on Viktor's disk. The
    body mentions the line in backticks, as delivered messages do; only a line
    that starts with it counts as the line.
    """
    text = (
        "docs: a throwaway commit\n"
        "\n"
        "The body may say `Verified-Tree:` in prose, as delivered messages do.\n"
        "\n"
    )
    if tree_line is not None:
        text += tree_line + "\n"
    text += (
        "Co-Authored-By: Test <test@example.com>\n"
        "Claude-Session: https://example.com/session\n"
    )
    return text.replace("\n", newline)


def _commit(work, message, *extra):
    path = os.path.join(os.path.dirname(work), "message.txt")
    with open(path, "wb") as f:
        f.write(message.encode("utf-8"))
    return _run(["git", "commit", "-q", *extra, "-F", path], cwd=work)


def _head(work):
    return _git(work, "rev-parse", "HEAD")


def _output(result):
    return result.stdout + result.stderr


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
        f"{HOOK_REL} contains CR bytes -- sh reads them as part of each command."
    )


# ---------------------------------------------------------------------------
# The hook's behaviour, by committing for real
# ---------------------------------------------------------------------------

def test_a_commit_naming_its_staged_tree_goes_through():
    """THE NEGATIVE CONTROL for every 'stopped' test below."""
    base, work = _repo_with_hook()
    try:
        _write(os.path.join(work, "b.txt"), "two\n")
        _git(work, "add", "b.txt")
        tree = _git(work, "write-tree")
        result = _commit(work, _message(f"Verified-Tree: {tree}"))
        assert result.returncode == 0, f"a good commit was stopped:\n{_output(result)}"
        assert _git(work, "rev-parse", "HEAD^{tree}") == tree
        assert PASSED_LINE in _output(result), (
            "the commit went through but the hook's line is absent -- "
            "the hook may not have run at all"
        )
        # The delivered file is CRLF; what git commits is not.
        raw = _run(["git", "cat-file", "commit", "HEAD"], cwd=work).stdout
        assert "\r" not in raw
    finally:
        shutil.rmtree(base, ignore_errors=True)


def test_a_file_left_unstaged_stops_the_commit():
    """A missed `git add`: the message names a tree with a file not staged."""
    base, work = _repo_with_hook()
    try:
        _write(os.path.join(work, "b.txt"), "two\n")
        _write(os.path.join(work, "c.txt"), "three\n")
        _git(work, "add", "b.txt", "c.txt")
        verified = _git(work, "write-tree")
        _git(work, "reset", "-q", "c.txt")
        staged = _git(work, "write-tree")
        before = _head(work)

        result = _commit(work, _message(f"Verified-Tree: {verified}"))
        output = _output(result)
        assert result.returncode != 0, f"the commit went through:\n{output}"
        assert _head(work) == before, "a commit was made despite the stop"
        assert verified in output and staged in output, output
        assert STOPPED_LINE in output
    finally:
        shutil.rmtree(base, ignore_errors=True)


def test_a_file_staged_beyond_the_verified_tree_stops_the_commit():
    """A wrong file: one staged that the verified tree does not hold."""
    base, work = _repo_with_hook()
    try:
        _write(os.path.join(work, "b.txt"), "two\n")
        _git(work, "add", "b.txt")
        verified = _git(work, "write-tree")
        _write(os.path.join(work, "stray.txt"), "not verified\n")
        _git(work, "add", "stray.txt")
        before = _head(work)

        result = _commit(work, _message(f"Verified-Tree: {verified}"))
        output = _output(result)
        assert result.returncode != 0, f"the commit went through:\n{output}"
        assert _head(work) == before
        assert STOPPED_LINE in output
    finally:
        shutil.rmtree(base, ignore_errors=True)


def test_a_lost_executable_bit_stops_the_commit():
    """The mode is part of the tree: a hook staged without +x is another tree."""
    base, work = _repo_with_hook()
    try:
        _write(os.path.join(work, "run.sh"), "#!/bin/sh\n")
        _git(work, "add", "run.sh")
        _git(work, "update-index", "--chmod=+x", "run.sh")
        verified = _git(work, "write-tree")
        _git(work, "update-index", "--chmod=-x", "run.sh")
        before = _head(work)

        result = _commit(work, _message(f"Verified-Tree: {verified}"))
        output = _output(result)
        assert result.returncode != 0, f"the commit went through:\n{output}"
        assert _head(work) == before
        assert STOPPED_LINE in output
    finally:
        shutil.rmtree(base, ignore_errors=True)


def test_the_tree_checked_is_the_one_git_commits():
    """`git commit -a` commits from a new index git names in GIT_INDEX_FILE.

    The real .git/index still holds the old tree while the hook runs. A hook
    that read .git/index directly would stop this good commit.
    """
    base, work = _repo_with_hook()
    try:
        _write(os.path.join(work, "a.txt"), "changed\n")
        _git(work, "add", "a.txt")
        verified = _git(work, "write-tree")
        _git(work, "reset", "-q", "a.txt")

        result = _commit(work, _message(f"Verified-Tree: {verified}"), "-a")
        assert result.returncode == 0, f"a good -a commit was stopped:\n{_output(result)}"
        assert _git(work, "rev-parse", "HEAD^{tree}") == verified
        assert PASSED_LINE in _output(result)
    finally:
        shutil.rmtree(base, ignore_errors=True)


def test_two_verified_tree_lines_stop_the_commit():
    """Both name the staged tree, and the commit is still stopped: two lines
    leave open which tree was verified."""
    base, work = _repo_with_hook()
    try:
        _write(os.path.join(work, "b.txt"), "two\n")
        _git(work, "add", "b.txt")
        tree = _git(work, "write-tree")
        before = _head(work)

        line = f"Verified-Tree: {tree}"
        result = _commit(work, _message(f"{line}\n{line}"))
        output = _output(result)
        assert result.returncode != 0, f"the commit went through:\n{output}"
        assert _head(work) == before
        assert STOPPED_LINE in output
    finally:
        shutil.rmtree(base, ignore_errors=True)


def test_a_line_not_in_the_exact_form_stops_the_commit():
    """Each variant would name the staged tree if read loosely."""
    base, work = _repo_with_hook()
    try:
        _write(os.path.join(work, "b.txt"), "two\n")
        _git(work, "add", "b.txt")
        tree = _git(work, "write-tree")
        before = _head(work)

        variants = [
            f"Verified-Tree: {tree[:12]}",          # a short hash
            f"Verified-Tree: {tree.upper()}",       # uppercase hex
            f"verified-tree: {tree}",               # the key's case
            f"Verified-Tree:{tree}",                # no space
            f"Verified-Tree : {tree}",              # space before the colon
            f"  Verified-Tree: {tree}",             # indented
            f"Verified-Tree: {tree} (sandbox)",     # trailing text
        ]
        for variant in variants:
            result = _commit(work, _message(variant))
            output = _output(result)
            assert result.returncode != 0, f"{variant!r} went through:\n{output}"
            assert _head(work) == before, f"{variant!r} made a commit"
            assert STOPPED_LINE in output, variant
    finally:
        shutil.rmtree(base, ignore_errors=True)


def test_no_verify_overrides_the_stop():
    """The override, as for the pre-push hook: the decision stays Viktor's."""
    base, work = _repo_with_hook()
    try:
        _write(os.path.join(work, "b.txt"), "two\n")
        _git(work, "add", "b.txt")
        wrong = "0" * 40
        before = _head(work)
        assert _commit(work, _message(f"Verified-Tree: {wrong}")).returncode != 0
        assert _head(work) == before

        result = _commit(work, _message(f"Verified-Tree: {wrong}"), "--no-verify")
        assert result.returncode == 0, _output(result)
        assert _head(work) != before
    finally:
        shutil.rmtree(base, ignore_errors=True)


def test_a_message_with_no_verified_tree_line_stops_the_commit():
    """Viktor's ruling of 27 October: every commit names its verified tree, so a
    message without the line is stopped like a wrong one, and --no-verify is
    the way past it once consulted."""
    base, work = _repo_with_hook()
    try:
        _write(os.path.join(work, "b.txt"), "two\n")
        _git(work, "add", "b.txt")
        before = _head(work)

        result = _commit(work, _message(None))
        output = _output(result)
        assert result.returncode != 0, f"a message with no line went through:\n{output}"
        assert _head(work) == before
        assert "no Verified-Tree: line" in output, output
        assert STOPPED_LINE in output

        result = _run(["git", "commit", "-q", "-m", "a one-line message"], cwd=work)
        assert result.returncode != 0, "a -m message with no line went through"
        assert _head(work) == before

        result = _commit(work, _message(None), "--no-verify")
        assert result.returncode == 0, _output(result)
        assert _head(work) != before
    finally:
        shutil.rmtree(base, ignore_errors=True)
