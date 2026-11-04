"""
Checks that a commit's rewrite of docs/PHASE7_NEXT.md moved every line it
removed into docs/PHASE7_HISTORY.md, word for word and in order, and nothing
else.

Written 4 November 2026 from DECISIONS, "Ruling, 4 November 2026 -- HISTORY
keeps what each rewrite of PHASE7_NEXT.md removes, not the whole file". From
19 September to 3 November each rewrite moved the whole previous version of
NEXT into HISTORY, about 440 KB a commit, and HISTORY reached 16.7 MB; a file
over 50 MiB draws a warning from GitHub and one over 100 MiB is refused. Git
already holds every version of NEXT byte for byte, so HISTORY now keeps the
lines a rewrite takes out -- 2 to 6 KB a commit over the eleven before the
ruling -- and points to git for the whole version. This script is the proof
that nothing leaves NEXT without landing in HISTORY, which is what the whole
move was for: on 19 September the 18 September account existed only in NEXT.

THE RULE IT CHECKS, between a base (a commit, HEAD by default) and the files
in the working tree:

 1. HISTORY is append-only: the base's HISTORY, line for line, is the start of
    the working tree's.
 2. If the rewrite removed or changed no line of NEXT, nothing is appended
    (blank lines aside).
 3. Otherwise exactly one entry is appended, and its blocks are the removed
    lines: for each run of the base's lines that the working tree's NEXT
    deletes or replaces, in order, one block carrying that run word for word,
    labelled with the run's line numbers in the base's version. No block is
    missing, none is extra, and no line in a block differs.

The runs are those of difflib.SequenceMatcher (autojunk off) over the two
versions' lines, its "delete" and "replace" opcodes; an inserted line removes
nothing. A replaced line is moved whole, though one character of it changed:
the new wording is in NEXT, the old in HISTORY.

THE ENTRY'S FORM (written by hand; `--emit` prints the blocks to paste):

    ## <date> -- the lines the rewrite of PHASE7_NEXT.md removed from its version at `<commit>`

    *Any prose, which must contain `git show <commit>:docs/PHASE7_NEXT.md`.*

    ---

    Lines 3<en dash>5 of the version at `<commit>`:

    ~~~~~
    <the three lines, as they were>
    ~~~~~

    Line 9 of the version at `<commit>`:

    ~~~~~
    <the line>
    ~~~~~

The entry starts at a line beginning "## ". Everything up to its first line
reading exactly "---" is the header; after it, only blank lines, labels and
fenced blocks. Every label names the same commit; given a base from git, that
commit must be the base (a prefix of its full hash). A removed line that
begins with the fence, "~~~~~", is refused: the block could not be read back.

LINE ENDINGS are not compared. A line is read without its CR LF or LF, so a
CRLF working tree on Windows checks against an LF blob from git, and the same
files give the same answer on Windows and Linux. Whether the final line ended
with a newline is not compared either.

WHAT IT DOES NOT CHECK: that the header's prose is true, that NEXT's new
wording is right, or anything about DECISIONS. It reads; it writes nothing.

Usage, from the repository's root:

    python docs/build/check_history_move.py
    python docs/build/check_history_move.py --base <commit>
    python docs/build/check_history_move.py --emit
    python docs/build/check_history_move.py --files OLD_NEXT NEW_NEXT OLD_HISTORY NEW_HISTORY

Exit 0 when the rule holds, 1 when it does not, 2 on a usage or git error.
"""

import argparse
import difflib
import os
import re
import subprocess
import sys

NEXT_PATH = "docs/PHASE7_NEXT.md"
HISTORY_PATH = "docs/PHASE7_HISTORY.md"
FENCE = "~~~~~"
EN_DASH = "–"
LABEL = re.compile(
    r"^Lines? (\d+)(?:" + EN_DASH + r"(\d+))? of the version at `([0-9a-f]{7,40})`:$"
)
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class EntryError(Exception):
    """The appended text is not an entry in the form above."""


def split_lines(data):
    """A file's bytes as its lines, decoded as UTF-8, without line endings."""
    text = data.decode("utf-8")
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    return [line[:-1] if line.endswith("\r") else line for line in lines]


def removed_runs(old, new):
    """(first, last, lines) for each run of `old` that `new` deletes or replaces.

    first and last are 1-based line numbers in `old`, inclusive.
    """
    matcher = difflib.SequenceMatcher(None, old, new, autojunk=False)
    runs = []
    for tag, i1, i2, _j1, _j2 in matcher.get_opcodes():
        if tag in ("delete", "replace"):
            runs.append((i1 + 1, i2, list(old[i1:i2])))
    return runs


def label(first, last, commit):
    if first == last:
        return "Line %d of the version at `%s`:" % (first, commit)
    return "Lines %d%s%d of the version at `%s`:" % (first, EN_DASH, last, commit)


def render_blocks(runs, commit):
    """The entry's body below its "---", as lines."""
    out = []
    for first, last, lines in runs:
        out.extend(["", label(first, last, commit), "", FENCE])
        out.extend(lines)
        out.append(FENCE)
    return out


def parse_entry(lines):
    """(header lines, [(first, last, commit, lines)]) of one appended entry."""
    i = 0
    while i < len(lines) and lines[i] == "":
        i += 1
    if i == len(lines) or not lines[i].startswith("## "):
        raise EntryError("the appended text does not start with a heading beginning '## '")
    start = i
    while i < len(lines) and lines[i] != "---":
        i += 1
    if i == len(lines):
        raise EntryError("the entry has no line reading exactly '---' after its header")
    header = lines[start:i]
    i += 1
    blocks = []
    while i < len(lines):
        line = lines[i]
        if line == "":
            i += 1
            continue
        match = LABEL.match(line)
        if not match:
            raise EntryError(
                "appended line %d is neither blank, a label nor inside a block: %s"
                % (i + 1, _shown(line))
            )
        first = int(match.group(1))
        last = int(match.group(2)) if match.group(2) else first
        commit = match.group(3)
        if line.startswith("Lines ") != (match.group(2) is not None):
            raise EntryError("appended line %d: 'Line' names one line, 'Lines' a range" % (i + 1))
        i += 1
        while i < len(lines) and lines[i] == "":
            i += 1
        if i == len(lines) or lines[i] != FENCE:
            raise EntryError("the label at appended line %d is not followed by a block" % (i + 1))
        i += 1
        body = []
        while i < len(lines) and lines[i] != FENCE:
            body.append(lines[i])
            i += 1
        if i == len(lines):
            raise EntryError("a block is not closed by '%s'" % FENCE)
        i += 1
        blocks.append((first, last, commit, body))
    return header, blocks


def _shown(line):
    return repr(line.encode("ascii", "backslashreplace").decode("ascii"))


def check(old_next, new_next, old_history, new_history, base=None):
    """The problems found, as sentences; an empty list means the rule holds.

    `base`, when given, is the full hash of the base commit; every label must
    name a prefix of it.
    """
    runs = removed_runs(old_next, new_next)
    for first, _last, lines in runs:
        for offset, line in enumerate(lines):
            if line.startswith(FENCE):
                return [
                    "line %d of the base's NEXT begins with the fence '%s' and could not be "
                    "read back from a block" % (first + offset, FENCE)
                ]

    if new_history[: len(old_history)] != old_history:
        for n, (a, b) in enumerate(zip(old_history, new_history), start=1):
            if a != b:
                return ["HISTORY is not append-only: its line %d differs from the base's" % n]
        return ["HISTORY is not append-only: it is shorter than the base's"]
    appended = new_history[len(old_history):]

    if not runs:
        if any(line != "" for line in appended):
            return ["the rewrite removed no line of NEXT, but HISTORY has text appended"]
        return []

    try:
        header, blocks = parse_entry(appended)
    except EntryError as exc:
        return [str(exc)]

    problems = []
    commits = {commit for _f, _l, commit, _b in blocks}
    if len(commits) > 1:
        problems.append("the labels name more than one commit: %s" % ", ".join(sorted(commits)))
    commit = blocks[0][2] if blocks else None
    if commit is not None:
        if base is not None and not base.startswith(commit):
            problems.append("the labels name `%s`, which is not the base %s" % (commit, base))
        pointer = "git show %s:%s" % (commit, NEXT_PATH)
        if not any(pointer in line for line in header):
            problems.append("the header does not contain `%s`" % pointer)

    if len(blocks) != len(runs):
        problems.append(
            "the entry has %d blocks; the rewrite removed %d runs of lines"
            % (len(blocks), len(runs))
        )
    for n, (run, block) in enumerate(zip(runs, blocks), start=1):
        first, last, lines = run
        b_first, b_last, _commit, body = block
        if (b_first, b_last) != (first, last):
            problems.append(
                "block %d is labelled lines %d-%d; the run removed is lines %d-%d"
                % (n, b_first, b_last, first, last)
            )
        if body != lines:
            for k, (a, b) in enumerate(zip(lines, body)):
                if a != b:
                    problems.append(
                        "block %d, line %d (line %d of the base's NEXT) differs: %s in NEXT, "
                        "%s in HISTORY" % (n, k + 1, first + k, _shown(a), _shown(b))
                    )
                    break
            else:
                problems.append(
                    "block %d has %d lines; the run removed has %d" % (n, len(body), len(lines))
                )
    return problems


def _git(repo, *args):
    result = subprocess.run(
        ["git", "-C", repo] + list(args), capture_output=True, check=False
    )
    if result.returncode != 0:
        raise RuntimeError(
            "git %s failed: %s" % (" ".join(args), result.stderr.decode("utf-8", "replace").strip())
        )
    return result.stdout


def _read(path):
    with open(path, "rb") as handle:
        return handle.read()


def _write(text):
    sys.stdout.buffer.write(text.encode("utf-8"))
    sys.stdout.buffer.flush()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--base", default="HEAD", help="the commit the rewrite starts from")
    parser.add_argument("--repo", default=REPO, help="the repository (this script's, by default)")
    parser.add_argument("--files", nargs=4, metavar=("OLD_NEXT", "NEW_NEXT", "OLD_HISTORY", "NEW_HISTORY"))
    parser.add_argument("--emit", action="store_true", help="print the blocks for the entry, and check nothing")
    args = parser.parse_args(argv)

    try:
        if args.files:
            old_next, new_next, old_history, new_history = [split_lines(_read(p)) for p in args.files]
            base = None
            commit = None
        else:
            base = _git(args.repo, "rev-parse", "--verify", args.base + "^{commit}").decode("ascii").strip()
            commit = base[:7]
            old_next = split_lines(_git(args.repo, "show", "%s:%s" % (base, NEXT_PATH)))
            old_history = split_lines(_git(args.repo, "show", "%s:%s" % (base, HISTORY_PATH)))
            new_next = split_lines(_read(os.path.join(args.repo, *NEXT_PATH.split("/"))))
            new_history = split_lines(_read(os.path.join(args.repo, *HISTORY_PATH.split("/"))))
    except (OSError, RuntimeError, UnicodeDecodeError) as exc:
        _write("check_history_move: %s\n" % exc)
        return 2

    if args.emit:
        runs = removed_runs(old_next, new_next)
        _write("\n".join(render_blocks(runs, commit or "<commit>")) + "\n")
        return 0

    problems = check(old_next, new_next, old_history, new_history, base=base)
    if problems:
        for problem in problems:
            _write("check_history_move: %s\n" % problem)
        return 1
    runs = removed_runs(old_next, new_next)
    if not runs:
        _write("check_history_move: the rewrite removed no line of NEXT, and nothing is appended to HISTORY.\n")
    else:
        count = sum(len(lines) for _f, _l, lines in runs)
        _write(
            "check_history_move: the %d lines the rewrite removed from NEXT, in %d runs, are in "
            "HISTORY's new entry word for word, and nothing else is appended.\n" % (count, len(runs))
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
