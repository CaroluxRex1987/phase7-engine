"""
The suite must not touch the engine's real record.

WHY THIS FILE EXISTS

On 6 September 2026 the suite was run against a clean clone with the
filesystem watched. Twenty-eight tests across eleven files were writing real
decision records into `logs/phase7_decision_log_aerousdt.jsonl` -- the
permanent record Item 5 (Reproducibility) and Item 6 (Traceability) are about
-- because they ran the engine against the real `config.LOG_DIR`. Nine
records per run, plus an archive, a chart and the cross-run state file.

Worse: `test_lineage.py`'s archive-path spelling test wrote into the relative
literal `"logs/"` and then called `shutil.rmtree("logs")` in a `finally`.
Running the suite DELETED the engine's log directory outright. A live run's
record and three earlier records were lost that way, and `logs/` is
gitignored, so no copy existed anywhere.

Neither of the two independent reviewers found this, and neither could have.
It is invisible in the source: every individual line is unremarkable, and the
damage only appears when the suite is executed and the filesystem is watched
before and after. Rule 25 -- reading finds what is written, running finds
what happens.

AND THE FIRST VERSION OF THIS FILE WAS NOT ENOUGH

It watched `logs` and passed in a Linux sandbox. On Viktor's machine it
failed immediately: `test_frame_ownership.py` wrote two PNGs to
`REPO_ROOT/Logs/Charts/`, the capitalised spelling `config` does not use.
That is a stray folder on Linux and the engine's live chart directory on
Windows, because Windows does not distinguish the two names.

So the guard now scans by lowercased directory name (`conftest.LOG_DIR_NAMES`)
and a Linux run sees what a Windows run would. A guard whose result depends on
which platform it ran on is not a guard, and this one was, for one delivery.

WHAT THESE TESTS DO

`tests/conftest.py` points `config.LOG_DIR` and `config.CHART_DIR` at a
temporary directory at import time, for both pytest and `run_tests.py`. These
tests check that the redirection is in force, that it did not change what a
real run does, and that the real directory came through the suite unaltered.

The last of those is order-dependent and says so: it can only see damage done
by tests that ran before it. It is not the guarantee -- the guarantee is the
redirection in conftest. This is the alarm that says the redirection stopped
working, or that something found a route around it, which is exactly what it
did on its first run.
"""

import os

import conftest
from conftest import (
    REAL_LOG_DIR,
    REAL_LOG_DIR_AT_START,
    SHIPPED_LOG_DIR,
    SUITE_LOG_DIR,
)


def _inside(path, root):
    """True when `path` is `root` or sits underneath it."""
    path = os.path.realpath(path)
    root = os.path.realpath(root)
    return path == root or path.startswith(root + os.sep)


# ============================================================
# The redirection is in force
# ============================================================

def test_the_log_directory_the_suite_writes_to_is_not_in_the_repository():
    """
    The engine writes wherever `config.LOG_DIR` points. If that resolves
    inside the repository while the suite is running, every test that runs
    the engine is appending to the record the audit is about.

    Order-independent: it reads the live value of the setting rather than
    the consequences of somebody having used it.
    """
    from core import config

    assert not _inside(config.LOG_DIR, conftest.REPO_ROOT), (
        f"config.LOG_DIR is {config.LOG_DIR!r}, which resolves inside the "
        f"repository at {conftest.REPO_ROOT!r}. A test that runs the engine "
        f"will write a real decision record into the engine's own log."
    )
    assert _inside(config.LOG_DIR, SUITE_LOG_DIR), (
        f"config.LOG_DIR is {config.LOG_DIR!r}, which is outside the "
        f"repository but is not the suite's temporary directory either. "
        f"Something repointed it and did not put it back."
    )


def test_the_chart_directory_is_redirected_too():
    """
    Charts are written on the same runs and were landing in `logs/charts/`
    beside the decision log. The rmtree took them with it.
    """
    from core import config

    assert not _inside(config.CHART_DIR, conftest.REPO_ROOT), (
        f"config.CHART_DIR is {config.CHART_DIR!r}, inside the repository."
    )


# ============================================================
# The redirection did not change what a real run does
# ============================================================

def test_the_shipped_default_still_points_at_the_repositorys_own_logs():
    """
    A guard that made the engine stop logging where it is supposed to log
    would be worse than the defect. `conftest` overrides the value for the
    test session only; the value `core/config.py` declares must be unchanged.

    This is the negative half of the fix: proof it is a redirection and not
    an edit to production behaviour.
    """
    assert SHIPPED_LOG_DIR, "config declares no LOG_DIR at all"
    assert not os.path.isabs(SHIPPED_LOG_DIR) or _inside(
        SHIPPED_LOG_DIR, conftest.REPO_ROOT), (
        f"the shipped LOG_DIR is {SHIPPED_LOG_DIR!r}, which no longer points "
        f"at the repository's own log directory. A real run would write "
        f"somewhere else."
    )
    assert "log" in SHIPPED_LOG_DIR.lower(), (
        f"the shipped LOG_DIR is {SHIPPED_LOG_DIR!r}"
    )


# ============================================================
# The real directory came through the suite unaltered
# ============================================================

def test_the_real_log_directory_was_not_written_to_or_deleted():
    """
    Compares every `logs`-named directory in the repository root against the
    snapshot conftest took before any test ran: each file and its size, so an
    appended record is caught as well as a deleted one, and every casing of
    the name is covered so the result does not depend on the platform.

    ORDER-DEPENDENT, deliberately and with its limits stated. It can only
    observe damage done by tests that ran before it, and it cannot see a test
    that deletes a directory and rebuilds it byte for byte. The guarantee is
    conftest's redirection; this is the alarm for when something finds a way
    around it.

    `None` on both sides means no such directory existed before the suite and
    none exists now, which is the normal state on a fresh clone.
    """
    now = conftest._snapshot_log_dirs()

    if REAL_LOG_DIR_AT_START is None and now is None:
        return

    assert REAL_LOG_DIR_AT_START is not None, (
        f"no log directory existed under {conftest.REPO_ROOT} when the suite "
        f"started and one exists now: {now}. A test created the engine's real "
        f"log directory."
    )
    assert now is not None, (
        f"{REAL_LOG_DIR} existed when the suite started and is gone now. A "
        f"test deleted the engine's permanent record -- the decision log, "
        f"the archives, the charts and the cross-run state file."
    )

    before, after = dict(REAL_LOG_DIR_AT_START), dict(now)
    created = sorted(set(after) - set(before))
    removed = sorted(set(before) - set(after))
    changed = sorted(k for k in set(before) & set(after)
                     if before[k] != after[k])

    assert not (created or removed or changed), (
        f"the suite modified a log directory under {conftest.REPO_ROOT}.\n"
        f"  created: {created}\n"
        f"  removed: {removed}\n"
        f"  changed size: {changed}\n"
        f"A test reached the engine's real record. Find it and give it a "
        f"temporary directory. Note that a `Logs/...` path is the same file "
        f"as `logs/...` on Windows."
    )


def test_the_snapshot_comparison_can_actually_fail():
    """
    Negative control for the test above.

    A guard that compares two structures is worthless if the comparison
    cannot report a difference -- and this one returns early when both sides
    are None, which is the common case on a clean clone. So the comparison is
    exercised here against a directory built for the purpose.

    Sizes are measured rather than asserted as literals. The first version of
    this test asserted 4 bytes for "one\\n" and failed on Windows, where text
    mode writes 5 -- a hardcoded byte count that ignored line endings, in a
    repository that has now been bitten by exactly that three times.
    """
    import shutil
    import tempfile

    work = tempfile.mkdtemp(prefix="phase7_guard_")
    try:
        logs = os.path.join(work, "logs")
        os.makedirs(logs)
        record = os.path.join(logs, "record.jsonl")

        with open(record, "w") as fh:
            fh.write("one\n")
        first = conftest._snapshot_log_dirs(work)
        assert first is not None and len(first) == 1, first
        name, size = first[0]
        assert name == "logs/record.jsonl", first
        assert size == os.path.getsize(record), first

        with open(record, "a") as fh:
            fh.write("two\n")
        appended = conftest._snapshot_log_dirs(work)
        assert appended != first, (
            "appending to a file did not change the snapshot, so the guard "
            "above cannot see a suite run adding decision records"
        )

        os.remove(record)
        emptied = conftest._snapshot_log_dirs(work)
        assert emptied == [], emptied
        assert emptied != appended

        shutil.rmtree(logs)
        assert conftest._snapshot_log_dirs(work) is None, (
            "a deleted directory did not snapshot as None, so the guard "
            "above cannot see the rmtree that caused this file to exist"
        )
    finally:
        shutil.rmtree(work, ignore_errors=True)


def test_the_snapshot_sees_a_capitalised_logs_directory_too():
    """
    The case that broke the first version of this guard.

    `Logs/Charts/x.png` is a second directory on Linux and the engine's own
    chart directory on Windows. A snapshot that matches the name exactly
    reports nothing on Linux and the guard passes -- on the platform where
    the patch is written, and not on the one where it runs.
    """
    import shutil
    import tempfile

    work = tempfile.mkdtemp(prefix="phase7_guard_case_")
    try:
        charts = os.path.join(work, "Logs", "Charts")
        os.makedirs(charts)
        with open(os.path.join(charts, "_x.png"), "w") as fh:
            fh.write("x")

        snap = conftest._snapshot_log_dirs(work)
        assert snap is not None, (
            "a capitalised Logs/ directory snapshotted as None, so the guard "
            "cannot see files written through that spelling"
        )
        assert [n for n, _ in snap] == ["Logs/Charts/_x.png"], snap
    finally:
        shutil.rmtree(work, ignore_errors=True)
