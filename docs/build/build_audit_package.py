#!/usr/bin/env python3
"""
Builds the material an independent auditor receives. Repeatable, from the repo.

WHY THIS SCRIPT EXISTS

The Step 8 package was assembled by hand. Engineering Notes #24 records what
that cost: "a false claim found in Claude's own Step 2a package" -- the party
under audit describing its own evidence, and getting it wrong. A hand-built
bundle can claim a file count it does not contain, omit a module nobody
notices, or describe a manifest that does not match what shipped.

A generated bundle cannot. It walks the repository, emits what it finds, and
the manifest is computed from the bytes it actually wrote rather than from
anyone's memory of them. Every file carries a SHA-256, so the auditor can
verify that what they received is what the repository holds, and a later reader
can establish exactly which artifact was graded.

WHAT IT REFUSES TO INCLUDE, AND WHY THAT IS ENFORCED RATHER THAN INTENDED

docs/ holds the roadmap, the engineering notes, PHASE7_NEXT.md and the previous
auditor's report. All of it is another party's reasoning about this same code,
and reading it before forming a view would make the report a review of someone
else's audit rather than an audit.

Intending to exclude it is not enough. The exclusion is asserted below, and the
build fails loudly rather than shipping a package that quietly contains the
answers. A previous attempt at this audit was correctly refused because the
wrong Constitution file was supplied by mistake; that is the failure mode this
guard exists for.

OUTPUT GOES TO A NEW DIRECTORY, NOT OVER THE OLD ONE

docs/audit_package/ holds what Luna Pro actually graded. Overwriting it would
destroy the record of what the previous audit saw, which is the same
traceability argument Item 6 makes about decisions, applied to the audit
process itself. Each round gets its own directory.
"""

import hashlib
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROUND = "round2"
PACKAGE_DIR = os.path.join(REPO, "docs", "audit_package")
OUT_DIR = os.path.join(PACKAGE_DIR, ROUND)

# The upload set is a DIRECTORY, not a list in a document.
#
# docs/audit_package/ contains last round's bundles under the same filenames as
# this round's. They differ only by size and date, and uploading the stale pair
# would have the auditor grade code that no longer exists -- with nothing in its
# report to reveal that had happened. A warning is not a safeguard when the two
# files are named the same thing.
#
# So the files that go to the auditor are copied into one folder containing
# nothing else, including the instruction and the Constitution, and the
# withheld material goes in a separate folder. "Upload everything in this
# folder" is then literally correct and requires no judgment at the moment
# where a mistake cannot be undone.
UPLOAD_DIR = os.path.join(OUT_DIR, "UPLOAD_THESE")
PART7_DIR = os.path.join(OUT_DIR, "PART7_LATER")

# Copied in from docs/audit_package/ rather than referenced, so the upload
# folder is complete on its own.
# The Constitution ships as TEXT, not as the PDF.
#
# Round 2's second attempt sent the PDF. The model could see the filename and
# could not see the contents; it said so and stopped. A standard the auditor
# cannot read is worse than one they were told about and never received, so the
# format changed rather than the auditor being asked to work around it. The .txt
# is a mechanical `pdftotext -layout` extraction carrying the source PDF's
# SHA-256 in its own header.
#
# The PDF stays in the repository as the canonical artifact and is deliberately
# NOT in this list. Shipping both would put two files in the upload folder each
# claiming to be the standard, which is the same defect check 7.6 asks the
# auditor to look for.
HAND_WRITTEN = [
    "item16_review_instruction_rev3.md",
    "Phase7_Constitution_v1.0_RATIFIED_AUDITCOPY.txt",
]

# Directories that never enter a bundle, for four different reasons:
#   docs      another party's reasoning about this code (see the docstring)
#   logs      run artifacts; not the artifact under audit
#   .git      history is supplied separately and deliberately shaped
#   caches    derived bytes
EXCLUDED_DIRS = {"docs", "logs", ".git", "__pycache__", ".pytest_cache",
                 ".venv", "venv", "node_modules"}

# The test bundle is "every test module and the runner". run_tests.py is the
# no-pytest runner and test_live.py is a root-level smoke check; both are test
# material and belong with the tests rather than with the engine.
TEST_ROOT_FILES = {"run_tests.py", "test_live.py"}

# Not source, but the auditor needs them: Tier 3 asks about controlled changes
# and pinned dependencies, and Item 5 asks about reproducibility. Withholding
# requirements.txt and then grading "are dependencies pinned" is asking a
# question while hiding the answer.
PROJECT_FILES = ["pytest.ini", "requirements.txt", "requirements-dev.txt",
                 ".gitattributes", ".gitignore"]

MARKER = "=== FILE: {path} ==="

# Terminal colour codes, stripped from captured output. See _capture().
ANSI = re.compile(r"\x1b\[[0-9;]*m")


def _walk(kind):
    """Every .py in the repo, split into engine and test material."""
    found = []
    for root, dirs, files in os.walk(REPO):
        dirs[:] = sorted(d for d in dirs if d not in EXCLUDED_DIRS)
        for name in sorted(files):
            if not name.endswith(".py"):
                continue
            full = os.path.join(root, name)
            rel = os.path.relpath(full, REPO).replace(os.sep, "/")
            is_test = rel.startswith("tests/") or rel in TEST_ROOT_FILES
            # This script builds the package; it is not part of the artifact.
            if rel.startswith("docs/"):
                continue
            if (kind == "tests") == bool(is_test):
                found.append(rel)
    return found


def _read(rel):
    with open(os.path.join(REPO, rel), encoding="utf-8") as fh:
        return fh.read()


def _bundle(rel_paths, title, purpose):
    """One markdown bundle, with the delimiter the instruction document names."""
    # The delimiter is DESCRIBED here rather than written out, because a
    # literal copy of it in the header is a phantom entry to anything that
    # splits the file on it -- a document containing a fake instance of its own
    # delimiter, which is a small dishonesty of exactly the kind this project
    # audits for.
    parts = [f"# {title}\n\n{purpose}\n\n"
             f"Each file below begins with a line reading three equals signs, the word "
             f"FILE, a colon, the path, and three equals signs. {len(rel_paths)} files "
             f"follow, in path order. Cite locations by path and by quoting the code: "
             f"line numbers are not included.\n\n"]
    entries = []
    for rel in rel_paths:
        text = _read(rel)
        entries.append((rel, len(text.encode("utf-8")),
                        hashlib.sha256(text.encode("utf-8")).hexdigest()))
        parts.append(MARKER.format(path=rel) + "\n\n```python\n" + text + "\n```\n\n")
    return "".join(parts), entries


def _git(*args):
    try:
        out = subprocess.run(["git", "-C", REPO, *args], capture_output=True,
                             text=True, encoding="utf-8", errors="replace")
        return out.stdout.strip() if out.returncode == 0 else f"<git failed: {out.stderr.strip()}>"
    except Exception as exc:                      # git absent, or not a repo
        return f"<git unavailable: {exc}>"


def _history_metadata():
    """
    The SHAPE of the version-control history, with the reasoning removed.

    Five rules came back "Not verifiable" from the previous audit -- version
    control, controlled changes, known-good checkpoints, rollback, and
    documentation of decisions -- and every one of them was unassessable ONLY
    because history was withheld. Supplying it is the cheapest verdict movement
    available on the whole register.

    But commit MESSAGES are the previous auditor's account and the fixer's own
    reasoning: what was found, what was rated Critical, what was changed and
    why. Handing those over before the reviewer has formed a view would defeat
    the point of asking a second party at all.

    So: hashes, dates, authorship, files touched, insertions and deletions,
    tags and branches -- everything needed to judge whether version control is
    real and disciplined -- and SUBJECT LINES WITHHELD. A subject like "Audit
    Findings 6 and 7: make a run reconstructable and traceable" would leak both
    a finding number and its outcome in eleven words.

    The full messages are written to a separate file for the optional Part 7
    pass, after the reviewer has committed to Parts 1-6.
    """
    lines = [
        "# Version-control history — metadata only",
        "",
        "**Subject lines and commit bodies are deliberately withheld from this file.**",
        "They contain the previous auditor's findings and the fixer's reasoning, and",
        "reading them before you have formed your own view would make your report a",
        "review of someone else's audit. They are supplied separately for the optional",
        "Part 7 pass, after Parts 1-6 are saved.",
        "",
        "What is here is the shape of the history: whether version control exists,",
        "whether changes are made in controlled increments, whether known-good points",
        "are marked, and whether rollback is possible. Judge those on this evidence.",
        "",
        "## Summary",
        "",
        f"- Total commits on the current branch: {_git('rev-list', '--count', 'HEAD')}",
        f"- Current branch: {_git('rev-parse', '--abbrev-ref', 'HEAD')}",
        f"- All branches: {_git('branch', '-a', '--format=%(refname:short)') or '<none>'}",
        f"- Tags: {_git('tag', '--list') or '<no tags>'}",
        f"- First commit date: {_git('log', '--reverse', '--format=%ad', '--date=iso')[:25]}",
        f"- Latest commit date: {_git('log', '-1', '--format=%ad', '--date=iso')}",
        f"- Working tree clean: {'yes' if not _git('status', '--porcelain') else 'NO -- uncommitted changes present'}",
        "",
        "## Commits, newest first",
        "",
        "Each entry: short hash, ISO date, author, then the files changed with",
        "insertions and deletions.",
        "",
    ]
    raw = _git("log", "--format=%x00%h%x00%ad%x00%an", "--date=iso", "--numstat")
    if raw.startswith("<git"):
        lines.append(raw)
        return "\n".join(lines) + "\n"

    current = None
    for line in raw.splitlines():
        if line.startswith("\x00"):
            _, short, date, author = line.split("\x00", 3)
            current = short
            lines.append("")
            lines.append(f"### `{short}` — {date} — {author}")
        elif line.strip() and current:
            cols = line.split("\t")
            if len(cols) == 3:
                added, removed, path = cols
                lines.append(f"- `{path}` +{added} / -{removed}")
        elif not line.strip() and current:
            lines.append("")
    return "\n".join(lines) + "\n"


def _full_messages():
    header = (
        "# Commit messages — FOR PART 7 ONLY\n\n"
        "**Do not read this file until Parts 1 through 6 of your report are written\n"
        "and saved.**\n\n"
        "These are the fixer's own account of what was changed and why, and they name\n"
        "findings from a previous audit along with their severities. Reading them first\n"
        "would replace your independent view with someone else's, and there is no second\n"
        "chance to be independent.\n\n"
        "Once your report is committed, these support Part 7: places where the stated\n"
        "intent and the shipped code differ, and any claim here your own reading does\n"
        "not support.\n\n---\n\n"
    )
    return header + _git("log", "--format=commit %H%nDate: %ad%n%n%B%n---%n", "--date=iso") + "\n"


def _capture(label, why, run):
    """One engine run, with everything it printed, verbatim."""
    import contextlib, io as _io, traceback as _tb

    buffer = _io.StringIO()
    try:
        with contextlib.redirect_stdout(buffer):
            decision = run()
        note = f"Action: {decision.get('explanation', {}).get('summary', '<none>')[:120]}"
        if decision.get("error"):
            note = f"Error: {decision['error']}"
    except Exception:
        note = "This run raised. The traceback is part of the transcript."
        buffer.write("\n" + _tb.format_exc())
    # The panel is colourised for a terminal. Left in, the escape sequences
    # would reach the reviewer as noise and cost tokens to no purpose -- and
    # unlike the code's comments, they carry no claim worth preserving.
    plain = ANSI.sub("", buffer.getvalue()).rstrip()
    return f"## {label}\n\n{why}\n\n**{note}**\n\n```\n{plain}\n```\n\n"


def _transcripts():
    """
    What the engine actually printed, captured rather than described.

    Section 11 of the instruction explains why this is here: the most recent
    Critical in this project was invisible to reading and appeared only when two
    data sources disagreed. A reviewer who cannot execute the program is in the
    position every previous reviewer was in when that defect went through.

    Two runs, both deterministic and offline. The network is pointed at a port
    nothing listens on, so nothing here depends on what an exchange returned on
    the day.

    The disagreement fixture is imported from the test that asserts against it
    rather than rebuilt here. A second implementation of the same series would
    be two things to keep in step, and the transcript would stop being evidence
    about the condition the suite actually tests.
    """
    header = (
        "# Execution transcripts\n\n"
        "Output the engine produced when run. Captured verbatim, including anything\n"
        "it printed to stderr-style log lines.\n\n"
        "**Treat these exactly as you treat comments: as claims by the party under\n"
        "audit.** They were produced and selected by the party being graded. A\n"
        "transcript proves what happened on one run, not what happens generally. If a\n"
        "verdict would be easier with the program's behaviour under some other\n"
        "condition, Section 11 of your instructions explains how to ask for it.\n\n"
        "Both runs below are offline and deterministic: the live endpoint is pointed at\n"
        "a port nothing listens on, and the data comes from files in the repository or\n"
        "from a pure function of them. Neither depends on what an exchange returned on\n"
        "any particular day.\n\n---\n\n"
    )
    sys.path.insert(0, REPO)
    parts = [header]
    unreachable = "http://127.0.0.1:1"

    try:
        from core import config
        from data.data_fetcher import DataFetcher, data_fetcher
        from models.signal_router import SignalRouter
    except Exception as exc:
        return header + (
            f"**The engine could not be imported in this environment, so no runs were\n"
            f"captured.** The reason is recorded here rather than the section being\n"
            f"omitted: `{exc}`\n")

    import tempfile

    original_url = data_fetcher.base_url
    original_log, original_chart = config.LOG_DIR, config.CHART_DIR
    work = tempfile.mkdtemp(prefix="phase7_transcripts_")
    try:
        data_fetcher.base_url = unreachable
        config.LOG_DIR = os.path.join(work, "logs")
        config.CHART_DIR = os.path.join(work, "logs", "charts")

        def pinned_run():
            DataFetcher.set_pinned_source(os.path.join(REPO, "tests", "fixtures", "pinned"))
            try:
                return SignalRouter().route(symbol="AEROUSDT", timeframe="4h")
            finally:
                DataFetcher.clear_pinned_source()

        parts.append(_capture(
            "Run 1 — the committed pinned fixtures",
            "The series the test suite uses as its baseline. This is the engine's "
            "ordinary output shape on data where nothing is missing and nothing "
            "conflicts.", pinned_run))

        def disagreement_run():
            from tests.test_timeframe_disagreement import _write_set
            pinned = os.path.join(work, "disagree")
            os.makedirs(pinned, exist_ok=True)
            _write_set(pinned, rising_first=True)
            DataFetcher.set_pinned_source(pinned)
            try:
                return SignalRouter().route(symbol="AEROUSDT", timeframe="4h")
            finally:
                DataFetcher.clear_pinned_source()

        parts.append(_capture(
            "Run 2 — the two timeframes disagreeing",
            "A long rally followed by a sharp multi-day break, so the daily average "
            "still points up while the shorter timeframe has turned down. Generated by "
            "a pure function; see tests/test_timeframe_disagreement.py for the series "
            "and what the suite asserts about it.", disagreement_run))
    finally:
        data_fetcher.base_url = original_url
        config.LOG_DIR, config.CHART_DIR = original_log, original_chart
        import shutil
        shutil.rmtree(work, ignore_errors=True)

    return "".join(parts)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    source_files = _walk("source")
    test_files = _walk("tests")

    # The guard. Intending to exclude the answers is not the same as excluding
    # them, and this is the one mistake that cannot be recovered from once the
    # package has been sent.
    leaked = [p for p in source_files + test_files
              if p.startswith("docs/") or "audit_package" in p]
    if leaked:
        sys.exit(f"REFUSING TO BUILD: withheld material would ship: {leaked}")
    if not source_files or not test_files:
        sys.exit(f"REFUSING TO BUILD: found {len(source_files)} source and "
                 f"{len(test_files)} test files; expected both to be non-empty.")

    project_present = [p for p in PROJECT_FILES if os.path.exists(os.path.join(REPO, p))]

    source_text, source_entries = _bundle(
        source_files + project_present,
        "Phase-7 Structural Quant Engine — complete source",
        "Every module the engine runs, plus the project files that decide how it is "
        "built and pinned. Nothing has been trimmed, summarised or withheld: if a "
        "module is not here, it does not exist.")
    test_text, test_entries = _bundle(
        test_files,
        "Phase-7 Structural Quant Engine — complete test suite",
        "Every test module and the runner. These were written by the same party that "
        "wrote the fixes they check, which is what Section 7.3 of your instructions "
        "asks you to bear in mind.")

    head = _git("rev-parse", "HEAD")
    manifest = [
        "# Audit package manifest",
        "",
        f"- Built: {datetime.now(timezone.utc).isoformat()}",
        f"- Repository HEAD: `{head}`",
        f"- Round: {ROUND}",
        f"- Source files: {len(source_entries)}",
        f"- Test files: {len(test_entries)}",
        "",
        "Every file's SHA-256 is listed below, computed from the exact bytes placed in",
        "the bundle. If a file in the bundle does not hash to the value here, the",
        "package was altered after it was built and you should say so in your report.",
        "",
    ]
    for label, entries in (("Source", source_entries), ("Tests", test_entries)):
        manifest.append(f"## {label}")
        manifest.append("")
        for rel, size, digest in entries:
            manifest.append(f"- `{rel}` — {size} bytes — `{digest}`")
        manifest.append("")

    import shutil

    # Rebuilt from empty each time. A stale file left behind in the upload
    # folder from a previous build is the same hazard this layout exists to
    # remove, one level down.
    for directory in (UPLOAD_DIR, PART7_DIR):
        shutil.rmtree(directory, ignore_errors=True)
        os.makedirs(directory, exist_ok=True)

    upload = {
        "phase7_engine_source.md": source_text,
        "phase7_test_suite.md": test_text,
        "MANIFEST.md": "\n".join(manifest),
        "version_control_history.md": _history_metadata(),
        "execution_transcripts.md": _transcripts(),
    }
    withheld = {"commit_messages_PART7_ONLY.md": _full_messages()}

    print("\nUPLOAD_THESE/ -- give the auditor everything in this folder:")
    for name, text in upload.items():
        with open(os.path.join(UPLOAD_DIR, name), "w",
                  encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        print(f"  {name:38} {len(text.encode('utf-8')):>9,} bytes")

    copied = 0
    for name in HAND_WRITTEN:
        source = os.path.join(PACKAGE_DIR, name)
        if not os.path.exists(source):
            print(f"  {name:38}   MISSING -- not copied")
            continue
        shutil.copy2(source, os.path.join(UPLOAD_DIR, name))
        copied += 1
        print(f"  {name:38} {os.path.getsize(source):>9,} bytes")

    print("\nPART7_LATER/ -- do NOT upload until Parts 1-6 are written and saved:")
    for name, text in withheld.items():
        with open(os.path.join(PART7_DIR, name), "w",
                  encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        print(f"  {name:38} {len(text.encode('utf-8')):>9,} bytes")

    with open(os.path.join(OUT_DIR, "MANIFEST.md"), "w",
              encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(manifest))

    upload_bytes = sum(len(t.encode("utf-8")) for t in upload.values()) + sum(
        os.path.getsize(os.path.join(PACKAGE_DIR, n))
        for n in HAND_WRITTEN if os.path.exists(os.path.join(PACKAGE_DIR, n)))
    print(f"\n{len(upload) + copied} files to upload, {upload_bytes:,} bytes "
          f"(roughly {upload_bytes // 4:,} tokens -- treat as a floor; code "
          f"tokenizes denser than four bytes per token).")
    print(f"HEAD: {head}")
    if copied != len(HAND_WRITTEN):
        print("\nWARNING: an expected document was missing and the upload folder "
              "is incomplete. Do not send it until that is resolved.")


if __name__ == "__main__":
    main()
