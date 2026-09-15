"""Session handover check — the mechanical half.

Answers the git-answerable items from PHASE7_NEXT.md's "Working practice"
handover checklist (items 3, 5 and 7) by running the actual commands
rather than relying on anyone remembering to. It does NOT answer items
1, 2, 4 and 6 -- whether this session's state is written into
PHASE7_NEXT.md, whether today's rulings are recorded there, whether the
Engineering Notes gap is current or explicitly stated, and whether any
evidence is still sitting only in a chat window. Those four ask whether
specific prose is accurate and current, which needs something reading
and judging content -- a script cannot do that, so they stay a manual
step every session close and are printed as a reminder at the end.

This exists because the checklist itself was, until now, an instruction
("run these seven checks") rather than a structural fact of the repo --
and Viktor's own standing preference is a structural fix over a
reminder to be careful. It is invoked by hand at session close, the
same as before; nothing in this project's actual workflow (single
commands run one at a time) can trigger it automatically the way an
IDE or a persistent agent session could.

Usage (from anywhere inside the repo, or pass the repo root as $1):
    python docs/build/session_handover_check.py
    python docs/build/session_handover_check.py D:\\phase7_engine

Exit code 0 if nothing was flagged, 1 if something needs a look --
never a claim that everything is fine, only that this script found
nothing. The four manual items still need answering regardless of
which exit code this prints.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def _run(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        args,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def _repo_root(start: Path) -> Path:
    result = _run(["git", "rev-parse", "--show-toplevel"], cwd=start)
    if result.returncode != 0:
        print(f"Not inside a git repository at {start}:", file=sys.stderr)
        print(result.stderr.strip(), file=sys.stderr)
        sys.exit(2)
    return Path(result.stdout.strip())


def check_working_tree(root: Path) -> list[str]:
    """Item 3: untracked or modified files `git status --short` shows directly."""
    result = _run(["git", "status", "--short"], cwd=root)
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    print("## 1. Untracked / modified files  (git status --short)")
    if not lines:
        print("  none")
    else:
        for line in lines:
            print(" ", line)
    return lines


# Pure build/cache noise that carries no information on any run of this
# repo -- filtered so it never has to be recognised and skipped by eye.
# Deliberately short and named explicitly here (not "**/*" catch-alls) so
# it stays legible what is being hidden. Anything not on this exact list
# still prints -- when in doubt, this list stays out, not the file.
_ROUTINE_IGNORED_MARKERS = (
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".DS_Store",
    "Thumbs.db",
    "desktop.ini",
)


def check_ignored_files(root: Path) -> list[str]:
    """Extends item 3: files `git status --short` never shows at all.

    This is the same shape of blind spot named in this file's own
    lessons -- an ignored file does not appear in a plain status check,
    which is exactly how reviewer responses once went unnoticed under
    docs/audit_package/round*/ (since fixed with .gitignore negation
    rules, not by anyone remembering to check). This runs --ignored
    separately and always prints it rather than trusting silence from
    the check above, in case the next surprise isn't covered by an
    existing negation rule.
    """
    result = _run(["git", "status", "--ignored", "--short"], cwd=root)
    all_ignored = [
        line for line in result.stdout.splitlines() if line.startswith("!! ")
    ]
    ignored = [
        line
        for line in all_ignored
        if not any(marker in line for marker in _ROUTINE_IGNORED_MARKERS)
    ]
    print()
    print("## 2. Ignored files present  (git status --ignored) -- review, don't assume harmless")
    if not ignored:
        skipped = len(all_ignored) - len(ignored)
        print(f"  none (routine build/cache noise filtered: {skipped})" if skipped else "  none")
    else:
        for line in ignored:
            print(" ", line)
    return ignored


def check_loose_delivery_files(root: Path) -> list[Path]:
    """Item 5: loose .patch / commit-message files still sitting unapplied.

    Belt-and-suspenders alongside the .gitignore rule added at 214c5d8 --
    that rule stops `git add -A` from staging these, it does not stop
    them existing on disk after a delivery that was never finished.
    """
    print()
    print("## 3. Loose .patch / *_commit_message.txt files anywhere in the tree")
    hits = sorted(
        p
        for pattern in ("*.patch", "*_commit_message.txt")
        for p in root.rglob(pattern)
        if ".git" not in p.parts
    )
    if not hits:
        print("  none")
    else:
        for hit in hits:
            print(" ", hit.relative_to(root))
    return hits


def check_staged_index(root: Path) -> str:
    """Item 7: a fully staged commit, prepared and never made.

    Added 11 September 2026 (ruling 5) after the 6 September doc rewrite
    sat staged-but-uncommitted through a whole session and a handover
    check before anyone noticed -- untracked-file checks don't see it,
    because it isn't untracked.
    """
    result = _run(["git", "diff", "--cached", "--stat"], cwd=root)
    print()
    print("## 4. Staged-but-uncommitted changes  (git diff --cached --stat)")
    if not result.stdout.strip():
        print("  none")
    else:
        print(result.stdout.rstrip())
    return result.stdout.strip()


def main() -> None:
    start = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    root = _repo_root(start)

    modified = check_working_tree(root)
    ignored = check_ignored_files(root)
    loose = check_loose_delivery_files(root)
    staged = check_staged_index(root)

    print()
    print("## Still manual -- this script cannot answer these; read PHASE7_NEXT.md")
    print("## and judge, don't skip them because the checks above came back clean:")
    print("  - Is the current session's state written into PHASE7_NEXT.md, not only in chat?")
    print("  - Are today's rulings recorded there, with what they decided and why?")
    print("  - Are the Engineering Notes current, or is the gap stated explicitly?")
    print("  - Is any evidence -- a review, a transcript, a reasoning dump -- still only in a chat window?")

    flagged = bool(modified or ignored or loose or staged)
    print()
    print("== SUMMARY:", "one or more items above need a look" if flagged else "clean", "==")
    sys.exit(1 if flagged else 0)


if __name__ == "__main__":
    main()
