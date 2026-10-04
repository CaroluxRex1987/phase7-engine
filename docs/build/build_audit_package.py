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

docs/ holds the roadmap, the engineering notes, PHASE7_NEXT.md,
PHASE7_DECISIONS.md, PHASE7_HISTORY.md and the previous auditor's report. All of it is another party's reasoning about this same code,
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
# Each round gets its own directory, and the build never writes into a previous
# one. That is the same traceability argument Item 6 makes about decisions,
# applied to the audit process: round2/ and round3/ are the record of what the
# previous attempts were given, and the only evidence of what an auditor
# actually saw when its report is later compared against a new one. Overwriting
# one would destroy the baseline the comparison is measured against.
#
# round3/ matters more than round2/ did. It is the exact package GLM 5.3 Flash
# graded on 5 September, by accident, and returned a complete Parts 1-6 against
# -- so it is the artifact behind a real report, not a record of an attempt that
# failed. The round-4 comparison is that report against this one.
#
# round4/ is what Kimi K3 actually graded and returned a second complete Parts
# 1-6 report against. round5/ is the first package built after Viktor's ruling
# of 11 September ("fold Part 7 into round 5 rather than resending it"): the
# UPLOAD_DIR/PART7_DIR split that rounds 3 and 4 used is gone, and
# commit_messages_PART7_ONLY.md now ships inside the single upload set --
# because that split had a real defect underneath it. The instruction document
# described the file as available after Parts 1-6 were saved, but the file was
# never in send_audit_round.py's ATTACHMENT_FILES for either round, so no
# reviewer could ever actually reach it. Folding it in fixes that for the first
# time rather than continuing to describe a promise the send step never kept.
#
# round5/ (above) is what GPT-6 Astra actually graded and returned a third
# complete Parts 1-6 report against, finding F1/F2/F3 -- all three now fixed
# and landed. round6/ is this build: it goes to Meta Muse Spark 1.3, not back
# to GPT-6 Astra. Viktor ruled the model 13 September (see
# docs/PHASE7_HISTORY.md), after the originally ruled meta/muse-spark-1.2 turned
# out to no longer be a live OpenRouter endpoint. round6/ also carries three
# commits (2387717, 88e47e9, 044b055) that have never been independently
# reviewed, batched in per Viktor's ruling the same day rather than sent as a
# separate round.
#
# round6/ (above) is what Muse Spark 1.3 graded on 13 September. round7/ is this
# build: it goes to Laguna S 2.1, pinned to Poolside (PHASE7_DECISIONS.md, the
# rulings of 29 September 2026), and it splits the package again -- the first
# build since round 4 to do so -- this time into two folders that are two
# requests, not one folder sent and one kept back. See MESSAGE1_DIR below.
#
# round7/ was sent to Laguna S 2.1 on 30 September 2026, twice, and round 8
# sends its first message again, file for file, with only the instruction
# replaced (PHASE7_DECISIONS.md, "Decision, 4 October 2026 -- round 8's
# package"). Round 8's folders are made by build_round8_package.py, which
# checks each of round7/'s files against the hash both runs recorded before it
# copies one. This script would rebuild round7/ from the working tree -- a
# different test bundle and history since the tag, and a new build time in the
# manifest -- and so destroy the files round 8 is built from. SENT makes it
# refuse. A new round that is built afresh sets ROUND to its own directory
# and SENT to False.
ROUND = "round7"
SENT = True
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
# nothing else, including the instruction and the Constitution. "Upload
# everything in this folder" is then literally correct and requires no
# judgment at the moment where a mistake cannot be undone.
#
# Rounds 3 and 4 also split off a PART7_LATER folder, withheld from the upload
# set, for commit_messages_PART7_ONLY.md. That split is gone as of round 5 (see
# the ROUND comment above): the file was never actually attached by
# send_audit_round.py under either name, so the second folder was not
# withholding anything real -- it was just where a file nobody sent happened to
# sit. One folder now, and the file's own header is what asks the reviewer not
# to open it before Parts 1-6 are saved.
#
# That request was all that held it back in rounds 5 and 6: send_audit_round.py
# sent the one folder as one message, the Part 7 file inside it (checked
# 29 September 2026 by rebuilding both rounds' requests; see that script's
# docstring). From round 7 there are two folders again, and this time each is a
# request: MESSAGE1_DIR is the first message, graded for Parts 1-6 alone, and
# MESSAGE2_DIR is sent by `send_audit_round.py --send-part7`, which refuses until
# the reply to the first is committed (ruling of 29 September, "what the auditor
# sees"). Every file the build writes into a folder is a file the script sends
# in that message, and nothing else: tests/test_send_audit_round.py builds both
# folders and reads them back with the script's own reader.
MESSAGE1_DIR = os.path.join(OUT_DIR, "MESSAGE1_PARTS1-6")
MESSAGE2_DIR = os.path.join(OUT_DIR, "MESSAGE2_PART7")

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
MESSAGE1_HAND_WRITTEN = [
    "item16_review_instruction_rev8.md",
    "Phase7_Constitution_v1.0_RATIFIED_AUDITCOPY.txt",
]

# The Part 7 material written by hand (ruling of 29 September, "what the auditor
# sees"): the bias_score findings, the list for after the audit, and the points
# of the 15 September PDF still live in the code. Not yet written when round 7
# was set up; the build refuses until it exists, as it does for rev8.
#
# Its name says what it is for, not what it holds. The file's contents go only in
# the second message, but its NAME reaches the auditor in the first: once it is
# committed, version_control_history.md lists it. Named part7_findings_* until
# 30 September 2026, when rev 8 was written to describe it to the auditor only as
# "a document the project wrote for the Part 7 pass" (PHASE7_DECISIONS.md, the
# ruling of 30 September on what rev 8 says about this round's test).
MESSAGE2_HAND_WRITTEN = [
    "part7_material_PART7_ONLY.md",
]
HAND_WRITTEN = MESSAGE1_HAND_WRITTEN + MESSAGE2_HAND_WRITTEN

# Part 7 shows the commit messages since this commit only, not the whole
# history (ruling of 29 September, "what the auditor sees": 82 commits at
# ec4e5fd, about 110K tokens instead of about 300K). The range excludes it:
# e65a0f7 is the baseline of docs/audit_change_list.md, the tree the last
# independent round (the round-6 fix-verification of 14 September) was checked
# against.
PART7_COMMITS_SINCE = "e65a0f7"

# Part 8 is gone, so this script no longer reads the four qwen_reasoning_*.txt in
# the repository root. Two things follow and neither is obvious.
#
# Those filenames are WRONG. The transcript is Kimi K3's, not Qwen's; Kimi says so
# in its own reasoning, in a passage the repository copy is missing. Rev 5 removes
# Part 8 for that reason -- the comparison document was the same model's earlier
# reasoning, so the round-4 reviewer would have been grading itself.
#
# They keep the wrong names until round 4 has been sent. A rename is a commit, and
# commits appear in version_control_history.md, which ships in the upload folder --
# so correcting the filename now would put the string "kimi" in front of Kimi
# before it has stated its own identity, which is the one thing Section 5 of Rev 5
# asks it to do unprompted. Rename after the package is out, not before.

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

    The messages since PART7_COMMITS_SINCE are written to a separate file for
    Part 7, sent in a second message after the reviewer has committed to
    Parts 1-6.
    """
    lines = [
        "# Version-control history — metadata only",
        "",
        "**Subject lines and commit bodies are deliberately withheld from this file.**",
        "They contain the previous auditor's findings and the fixer's reasoning, and",
        "reading them before you have formed your own view would make your report a",
        "review of someone else's audit. The messages of the most recent commits are",
        "supplied for Part 7, in a second message, after Parts 1-6 are saved.",
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


def _full_messages(since=PART7_COMMITS_SINCE, until="HEAD"):
    # `until` (4 October 2026): round 8 sends the messages up to the tag its
    # package was built from, not up to the commit it is sent from
    # (build_round8_package.py). With the default, what it writes is unchanged.
    base = _git("rev-parse", "--verify", f"{since}^{{commit}}")
    count = _git("rev-list", "--count", f"{since}..{until}")
    log = _git("log", "--format=commit %H%nDate: %ad%n%n%B%n---%n", "--date=iso",
               f"{since}..{until}")
    failed = [out for out in (base, count, log) if out.startswith("<git")]
    if failed:
        # Previously a failed git call went into the file as its text. This
        # file is what Part 7 is graded on; a package whose commit messages
        # are an error string must not look complete.
        sys.exit(f"REFUSING TO BUILD: the commit messages since {since} could not be "
                 f"read: {failed[0]}")
    header = (
        "# Commit messages — FOR PART 7 ONLY\n\n"
        "**This file comes in a second message, after Parts 1 through 6 of your report\n"
        "were written and saved.**\n\n"
        "These are the fixer's own account of what was changed and why, and they name\n"
        "findings from previous audits along with their severities.\n\n"
        f"They are the messages of the {count} commits made after `{base}`, newest\n"
        "first -- not the whole history, whose shape the metadata-only file in the\n"
        "first message covers.\n\n"
        "They support Part 7: places where the stated intent and the shipped code\n"
        "differ, and any claim here your own reading does not support.\n\n---\n\n"
    )
    return header + log + "\n"


def _capture(label, why, run, redact=None):
    """
    One engine run, with everything it printed, verbatim -- except the one
    thing named in `redact`, which is disclosed rather than silently altered.

    `redact` is an optional {actual_string: placeholder} mapping. The only
    current use (see _transcripts()) replaces the run's own temp directory --
    which on Windows embeds the machine's username, e.g.
    C:\\Users\\<name>\\AppData\\Local\\Temp\\... -- with a stable placeholder.
    That path is an artifact of how this script captures a run, not a claim
    the engine is making about itself, and it has no bearing on anything a
    reviewer is asked to check. Found 13 September 2026 by diffing a Windows
    build of this package against a Linux one; nothing before this indicates
    whether earlier rounds' packages carried the same thing unredacted.
    """
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
    for actual, placeholder in (redact or {}).items():
        plain = plain.replace(actual, placeholder)
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
        "any particular day.\n\n"
        "**One thing is deliberately altered, and this paragraph is here so that is\n"
        "disclosed rather than silent.** Each run logs a decision and saves a chart to a\n"
        "fresh temp directory created solely to capture this transcript; that path is\n"
        "replaced below with the placeholder `<TEMP>`. On the machine that built this\n"
        "package, the real path embeds a Windows username, which is not the engine\n"
        "making a claim about itself and has no bearing on anything you are asked to\n"
        "check. Nothing else in either transcript is touched.\n\n---\n\n"
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
            "conflicts.", pinned_run, redact={work: "<TEMP>"}))

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
            "and what the suite asserts about it.", disagreement_run,
            redact={work: "<TEMP>"}))
    finally:
        data_fetcher.base_url = original_url
        config.LOG_DIR, config.CHART_DIR = original_log, original_chart
        import shutil
        shutil.rmtree(work, ignore_errors=True)

    return "".join(parts)


def main():
    # The round directory is made by the first write into it, not here: a
    # build that refuses below says "Nothing has been written", and until
    # 29 September 2026 it had already made an empty round directory.

    if SENT:
        sys.exit(f"REFUSING TO BUILD: {ROUND} was sent on 30 September 2026, and round 8 "
                 f"is built from its files (build_round8_package.py). Rebuilding "
                 f"{ROUND}/ would overwrite them. Nothing has been written.")

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

    missing = [n for n in HAND_WRITTEN
               if not os.path.exists(os.path.join(PACKAGE_DIR, n))]
    if missing:
        sys.exit(f"REFUSING TO BUILD: these inputs are missing: {missing}. "
                 f"Nothing has been written.")

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

    # Every text is made before anything is removed or written, so a refusal
    # (the commit messages could not be read, say) leaves the last build as it
    # was rather than half-replaced.
    message1 = {
        "phase7_engine_source.md": source_text,
        "phase7_test_suite.md": test_text,
        "MANIFEST.md": "\n".join(manifest),
        "version_control_history.md": _history_metadata(),
        "execution_transcripts.md": _transcripts(),
    }
    message2 = {
        # Ruling 3, 11 September 2026 folded this file into the single upload
        # set from round 5 on, rather than leaving it in a second folder nothing
        # ever sent. From round 7 it is sent -- in the second request, after
        # Parts 1-6 are committed -- and cut to the commits since
        # PART7_COMMITS_SINCE (ruling of 29 September 2026).
        "commit_messages_PART7_ONLY.md": _full_messages(),
    }

    # Rebuilt from empty each time. A stale file left behind in either folder
    # from a previous build is the same hazard this layout exists to remove,
    # one level down.
    for directory in (MESSAGE1_DIR, MESSAGE2_DIR):
        shutil.rmtree(directory, ignore_errors=True)
        os.makedirs(directory, exist_ok=True)

    written = 0
    total_bytes = 0
    for folder, built, hand_written, what in (
            (MESSAGE1_DIR, message1, MESSAGE1_HAND_WRITTEN,
             "the first message: the instruction and Parts 1-6's material"),
            (MESSAGE2_DIR, message2, MESSAGE2_HAND_WRITTEN,
             "the second message, sent only after the reply to the first is committed")):
        print(f"\n{os.path.basename(folder)}/ -- {what}:")
        for name, text in built.items():
            with open(os.path.join(folder, name), "w",
                      encoding="utf-8", newline="\n") as fh:
                fh.write(text)
            size = len(text.encode("utf-8"))
            written += 1
            total_bytes += size
            print(f"  {name:38} {size:>9,} bytes")
        for name in hand_written:
            source = os.path.join(PACKAGE_DIR, name)
            if not os.path.exists(source):
                # Previously a printed warning at the end of a long, otherwise
                # successful run. An incomplete upload folder that announces itself
                # in the last line of output is exactly the hazard this layout exists
                # to remove: the folder still looks complete, and 'upload everything
                # in here' is then wrong. Nothing may be shipped, so nothing is built.
                sys.exit(f"REFUSING TO BUILD: {name} is not in {PACKAGE_DIR}. The "
                         f"folder would be incomplete and would look complete.")
            shutil.copy2(source, os.path.join(folder, name))
            size = os.path.getsize(source)
            written += 1
            total_bytes += size
            print(f"  {name:38} {size:>9,} bytes")

    with open(os.path.join(OUT_DIR, "MANIFEST.md"), "w",
              encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(manifest))

    # A round directory contains its folders and -- in round2, from an older
    # layout, and in round3/round4, which also split off a withheld PART7_LATER
    # folder -- loose copies or a second folder at its root. An earlier attempt
    # at this audit went out carrying a superseded revision of the reviewer
    # instruction, and nothing in its report revealed that. So each round says,
    # in its own directory, what is sent and how.
    with open(os.path.join(OUT_DIR, "README.md"), "w",
              encoding="utf-8", newline="\n") as fh:
        fh.write(
            f"# {ROUND}\n\n"
            f"Built {datetime.now(timezone.utc).isoformat()} from `{head}`.\n\n"
            "**Nothing in here is uploaded by hand.** `docs/build/send_audit_round.py`\n"
            "sends `MESSAGE1_PARTS1-6/` as the first request (`--send`) and\n"
            "`MESSAGE2_PART7/` as the second (`--send-part7`), which it refuses to send\n"
            "until the reply to the first is committed. Each folder must hold exactly\n"
            "the files the script sends in that message; it refuses otherwise. Not the\n"
            "files at this directory's root, and not anything from another round\n"
            "directory: several carry the same filenames and differ only by size and\n"
            "date.\n\n"
            "In rounds 5 and 6 the Part 7 file travelled in the same message as\n"
            "Parts 1-6, held back only by a request in its header. From this round it\n"
            "is a second request (see the `ROUND` comment at the top of\n"
            "`build_audit_package.py`).\n\n"
            "Regenerate with `python docs/build/build_audit_package.py`. Do not edit\n"
            "anything in here by hand: `MANIFEST.md` is computed from the bytes that\n"
            "were written, and a hand edit makes it a false claim.\n")

    print(f"\n{written} files in two folders, {total_bytes:,} bytes (roughly "
          f"{total_bytes // 4:,} tokens at four bytes a token -- a floor, not a "
          f"measurement: send_audit_round.py's dry run with --tokenizer-dir counts "
          f"them with the auditor's own tokenizer).")
    print(f"HEAD: {head}")

if __name__ == "__main__":
    main()
