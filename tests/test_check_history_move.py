"""
docs/build/check_history_move.py -- every line a rewrite of PHASE7_NEXT.md
removes is in HISTORY's new entry, word for word and in order, and nothing else.

Written 4 November 2026 with the script, from DECISIONS, "Ruling, 4 November
2026 -- HISTORY keeps what each rewrite of PHASE7_NEXT.md removes, not the
whole file". The entries below are written out by hand, not rendered by the
script, so a fault in the script's own idea of a block cannot make its check
agree with it. Each failing case is a single change to the passing one.

No fixtures: run_tests.py calls every test with no arguments. The git test
makes its repository in a temporary folder and writes nothing in this one.
"""

import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
TOOL_PATH = os.path.join(REPO, "docs", "build", "check_history_move.py")
D = "–"


def _tool():
    spec = importlib.util.spec_from_file_location("phase7_check_history_move", TOOL_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


OLD_NEXT = [
    "# Next step",           # 1
    "",                      # 2
    "Tip: `aaaaaaa`.",       # 3  replaced
    "Session of 1 May.",     # 4  deleted
    "Its account.",          # 5  deleted
    "",                      # 6
    "## Open items",         # 7
    "- one",                 # 8
    "- two, old wording",    # 9  replaced
    "- three",               # 10
]
NEW_NEXT = [
    "# Next step",
    "",
    "Tip: `bbbbbbb`.",
    "",
    "## Open items",
    "- one",
    "- two, new wording",
    "- three",
    "- four, added",
]
OLD_HISTORY = ["# History", "", "## An earlier entry", "", "Its text."]


def _entry(commit="abc1234"):
    return [
        "",
        "## 4 November 2026 " + "—" + " the lines the rewrite removed from its version at `%s`" % commit,
        "",
        "*The whole version: `git show %s:docs/PHASE7_NEXT.md`.*" % commit,
        "",
        "---",
        "",
        "Lines 3" + D + "5 of the version at `%s`:" % commit,
        "",
        "~~~~~",
        "Tip: `aaaaaaa`.",
        "Session of 1 May.",
        "Its account.",
        "~~~~~",
        "",
        "Line 9 of the version at `%s`:" % commit,
        "",
        "~~~~~",
        "- two, old wording",
        "~~~~~",
    ]


def _check(new_history, old_next=OLD_NEXT, new_next=NEW_NEXT, old_history=OLD_HISTORY, base=None):
    return _tool().check(old_next, new_next, old_history, new_history, base=base)


def test_the_runs_removed_are_the_deleted_and_replaced_lines():
    runs = _tool().removed_runs(OLD_NEXT, NEW_NEXT)
    assert runs == [
        (3, 5, ["Tip: `aaaaaaa`.", "Session of 1 May.", "Its account."]),
        (9, 9, ["- two, old wording"]),
    ]


def test_a_correct_entry_passes():
    assert _check(OLD_HISTORY + _entry()) == []


def test_a_dropped_line_fails():
    entry = _entry()
    entry.remove("Its account.")
    assert _check(OLD_HISTORY + entry)


def test_a_changed_character_fails():
    entry = [line.replace("1 May", "1 Mai") for line in _entry()]
    problems = _check(OLD_HISTORY + entry)
    assert any("differs" in p for p in problems), problems


def test_an_added_line_in_a_block_fails():
    entry = _entry()
    entry.insert(entry.index("Its account.") + 1, "A line NEXT never had.")
    assert _check(OLD_HISTORY + entry)


def test_a_missing_block_fails():
    entry = _entry()[:15]
    problems = _check(OLD_HISTORY + entry)
    assert any("blocks" in p for p in problems), problems


def test_a_wrong_line_number_fails():
    entry = [line.replace("Line 9 ", "Line 8 ") for line in _entry()]
    problems = _check(OLD_HISTORY + entry)
    assert any("labelled" in p for p in problems), problems


def test_blocks_out_of_order_fail():
    entry = _entry()
    head, first, second = entry[:7], entry[7:15], entry[15:]
    assert _check(OLD_HISTORY + head + second + [""] + first)


def test_text_outside_the_blocks_fails():
    entry = _entry() + ["", "A sentence after the blocks."]
    problems = _check(OLD_HISTORY + entry)
    assert any("neither blank" in p for p in problems), problems


def test_the_header_must_point_to_git():
    entry = [line for line in _entry() if "git show" not in line]
    problems = _check(OLD_HISTORY + entry)
    assert any("git show" in p for p in problems), problems


def test_an_edit_to_the_old_history_fails():
    edited = list(OLD_HISTORY)
    edited[4] = "Its text, edited."
    problems = _check(edited + _entry())
    assert any("append-only" in p for p in problems), problems


def test_a_removal_with_nothing_appended_fails():
    assert _check(list(OLD_HISTORY))


def test_no_removal_and_nothing_appended_passes():
    grown = OLD_NEXT + ["- an added line"]
    assert _check(OLD_HISTORY + ["", ""], new_next=grown) == []


def test_no_removal_but_text_appended_fails():
    grown = OLD_NEXT + ["- an added line"]
    assert _check(OLD_HISTORY + _entry(), new_next=grown)


def test_the_labels_must_name_the_base():
    assert _check(OLD_HISTORY + _entry(), base="abc1234" + "0" * 33) == []
    problems = _check(OLD_HISTORY + _entry(), base="def5678" + "0" * 33)
    assert any("not the base" in p for p in problems), problems


def test_a_removed_line_that_begins_with_the_fence_is_refused():
    old = OLD_NEXT[:4] + ["~~~~~ a line like a fence"] + OLD_NEXT[5:]
    entry = [line.replace("Its account.", "~~~~~ a line like a fence") for line in _entry()]
    problems = _check(OLD_HISTORY + entry, old_next=old)
    assert problems == [
        "line 5 of the base's NEXT begins with the fence '~~~~~' and could not be read back "
        "from a block"
    ], problems


def test_line_endings_are_not_compared():
    tool = _tool()
    crlf = ("\r\n".join(OLD_HISTORY + _entry()) + "\r\n").encode("utf-8")
    lf = ("\n".join(OLD_HISTORY) + "\n").encode("utf-8")
    assert tool.split_lines(crlf)[: len(OLD_HISTORY)] == tool.split_lines(lf)
    assert tool.check(OLD_NEXT, NEW_NEXT, tool.split_lines(lf), tool.split_lines(crlf)) == []


def _write(path, lines, ending):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as handle:
        handle.write((ending.join(lines) + ending).encode("utf-8"))


def _git(repo, *args):
    return subprocess.run(
        ["git", "-C", repo, "-c", "user.name=t", "-c", "user.email=t@example.invalid",
         "-c", "commit.gpgsign=false", "-c", "core.hooksPath=" + os.devnull] + list(args),
        capture_output=True, check=True,
    ).stdout.decode("ascii").strip()


def test_the_command_reads_the_base_from_git_and_the_files_from_disk():
    """End to end: an LF base committed, a CRLF working tree, exit 0, then 1."""
    work = tempfile.mkdtemp(prefix="phase7_history_move_")
    try:
        nxt = os.path.join(work, "docs", "PHASE7_NEXT.md")
        hist = os.path.join(work, "docs", "PHASE7_HISTORY.md")
        _write(nxt, OLD_NEXT, "\n")
        _write(hist, OLD_HISTORY, "\n")
        _git(work, "init", "-q")
        _git(work, "add", "docs/PHASE7_NEXT.md")
        _git(work, "add", "docs/PHASE7_HISTORY.md")
        _git(work, "commit", "-q", "-m", "base")
        short = _git(work, "rev-parse", "--short=7", "HEAD")
        _write(nxt, NEW_NEXT, "\r\n")
        _write(hist, OLD_HISTORY + _entry(short), "\r\n")

        def run():
            return subprocess.run(
                [sys.executable, TOOL_PATH, "--repo", work],
                capture_output=True, check=False,
            )

        passed = run()
        assert passed.returncode == 0, passed.stdout + passed.stderr
        assert b"the 4 lines the rewrite removed" in passed.stdout

        _write(hist, OLD_HISTORY + [l for l in _entry(short) if l != "Its account."], "\r\n")
        failed = run()
        assert failed.returncode == 1, failed.stdout + failed.stderr
    finally:
        shutil.rmtree(work, ignore_errors=True)
