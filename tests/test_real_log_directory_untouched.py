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

AND THEN IT RANG FOR SOMETHING THAT WAS NOT A TEST (entry 59)

Until 3 November 2026 the alarm compared the real folder with a snapshot taken
when the suite started. Since 17 October the scheduled task runs the engine
into that folder every four hours, at minute 05; on 2 November `1b82ed0`'s
`run_tests.py` step ran across the 18:05 run and failed here on five decision
logs, saying a test had reached the record. None had: each log had gained one
record, the task's. An alarm that rings on a normal event teaches its reader
to dismiss it.

A folder cannot say who wrote to it, so the alarm now asks the processes:
tests/suite_guard/sitecustomize.py records every write a process of the suite
makes inside a real log directory, as it happens, through Python's audit
hooks. The scheduled task is not a process of the suite. The controls below
hold both sides: a write by this process, by its child, through either
spelling of the folder, is recorded; the same write by a process the suite did
not start is not.
"""

import os
import shutil
import subprocess
import sys
import tempfile

import conftest
from conftest import (
    REAL_LOG_DIR,
    SHIPPED_LOG_DIR,
    SUITE_GUARD,
    SUITE_GUARD_REPORT,
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
    Every write, delete, rename, mkdir or rmtree that a process of the suite
    made inside a `logs`-named directory of the repository root, in any
    casing, as tests/suite_guard/sitecustomize.py recorded it when it
    happened. There must be none.

    ORDER-DEPENDENT, deliberately and with its limits stated: it reads what
    was recorded before it ran. The guarantee is conftest's redirection; this
    is the alarm for when something finds a way around it. What the hook
    cannot see is listed in its module's docstring.

    The scheduled task's writes are never here: it is not a process of the
    suite (entry 59).
    """
    found = SUITE_GUARD.read_report(SUITE_GUARD_REPORT, conftest.REPO_ROOT)

    assert not found, (
        f"a process of the suite changed a log directory under "
        f"{conftest.REPO_ROOT}:\n"
        + "".join(f"  {e['event']} {e['path']}  (pid {e['pid']}, "
                  f"test {e['test']})\n" for e in found)
        + f"A test reached the engine's real record ({REAL_LOG_DIR}). Find it "
        f"and give it a temporary directory. Note that a `Logs/...` path is "
        f"the same file as `logs/...` on Windows."
    )


# ============================================================
# Negative controls -- each side of the line the alarm draws
# ============================================================
#
# Each builds a stand-in repository root in a temporary folder and watches it
# for the length of the control, so the real one is never touched. The report
# is the suite's own; the alarm above reads only the real root's entries.

def _stand_in_root(prefix, with_logs=False):
    """A temporary root, watched from now; its `logs/` made first if asked,
    so that making it is not among what the control records."""
    root = tempfile.mkdtemp(prefix=prefix)
    if with_logs:
        os.makedirs(os.path.join(root, "logs"))
    return root, SUITE_GUARD.watch(root)


def _events(root):
    return [(e["event"], e["path"])
            for e in SUITE_GUARD.read_report(SUITE_GUARD_REPORT, root)]


def _as_reported(path):
    """
    A path as the hook reports it: what `os.path.normcase` makes of it, with
    forward slashes. On Windows that lowercases it -- Windows does not tell
    `Logs` from `logs` -- and on Linux it changes nothing.

    Found 3 November 2026 on Viktor's machine, the first run of these
    controls there: the capitalised control expected `Logs/...` and the hook,
    having caught the folder, reported `logs/...`. The sandbox could not
    show it.
    """
    return os.path.normcase(path.replace("/", os.sep)).replace(os.sep, "/")


def test_every_kind_of_write_by_this_process_is_recorded():
    """
    The suite's own side, operation by operation, including the two the
    snapshot before 3 November could not see: a file rewritten to the same
    size, and a directory deleted and rebuilt as it was. A read is not a
    write, and a folder beside `logs` is not a log directory.
    """
    root, stop = _stand_in_root("phase7_guard_self_")
    try:
        logs = os.path.join(root, "logs")
        record = os.path.join(logs, "record.jsonl")
        os.makedirs(logs)
        with open(record, "w") as fh:
            fh.write("one\n")
        with open(record, "a") as fh:
            fh.write("two\n")
        with open(record) as fh:
            fh.read()
        with open(record, "w") as fh:             # the same size again
            fh.write("one\ntwo\n")
        os.replace(record, record + ".moved")
        os.remove(record + ".moved")
        shutil.rmtree(logs)
        os.makedirs(logs)                         # rebuilt as it was
        os.makedirs(logs, exist_ok=True)          # there already: no change
        os.makedirs(os.path.join(root, "notes"))
        with open(os.path.join(root, "notes", "x.txt"), "w") as fh:
            fh.write("x")

        assert _events(root) == [
            ("os.mkdir", "logs"),
            ("open", "logs/record.jsonl"),
            ("open", "logs/record.jsonl"),
            ("open", "logs/record.jsonl"),
            ("os.rename", "logs/record.jsonl"),
            ("os.rename", "logs/record.jsonl.moved"),
            ("os.remove", "logs/record.jsonl.moved"),
            ("shutil.rmtree", "logs"),
            ("os.rmdir", "logs"),
            ("os.mkdir", "logs"),
        ], _events(root)
        assert all(e["pid"] == os.getpid()
                   for e in SUITE_GUARD.read_report(SUITE_GUARD_REPORT, root))
    finally:
        stop()
        shutil.rmtree(root, ignore_errors=True)


def test_a_capitalised_logs_directory_is_watched_too():
    """
    The case that broke the first version of this guard (6 September 2026):
    `Logs/Charts/x.png` is a second directory on Linux and the engine's own
    chart directory on Windows. Matched by name exactly, the alarm would stay
    silent on the platform where the patch is written and not on the one
    where it runs.
    """
    root, stop = _stand_in_root("phase7_guard_case_")
    try:
        charts = os.path.join(root, "Logs", "Charts")
        os.makedirs(charts)
        with open(os.path.join(charts, "_x.png"), "w") as fh:
            fh.write("x")

        assert _events(root) == [
            ("os.mkdir", _as_reported("Logs")),
            ("os.mkdir", _as_reported("Logs/Charts")),
            ("open", _as_reported("Logs/Charts/_x.png")),
        ], _events(root)
    finally:
        stop()
        shutil.rmtree(root, ignore_errors=True)


_APPEND_A_RECORD = (
    "import sys\n"
    "with open(sys.argv[1], 'a') as fh:\n"
    "    fh.write('{\"record\": 1}\\n')\n"
)


def _append_from_a_child(root, env):
    record = os.path.join(root, "logs", "phase7_decision_log_testusdt.jsonl")
    before = os.path.getsize(record) if os.path.exists(record) else 0
    proc = subprocess.run([sys.executable, "-c", _APPEND_A_RECORD, record],
                          env=env, capture_output=True, text=True, timeout=60)
    assert proc.returncode == 0, proc.stderr
    assert os.path.getsize(record) > before, (
        "the child did not append, so this control shows nothing")
    return record


def test_a_child_the_suite_starts_is_watched_too():
    """
    The suite's other side: a Python process a test starts inherits the
    hook through the environment conftest set, and its write is recorded
    under its own pid. tests/test_main_takes_pairs.py runs main.py this way.
    """
    root, stop = _stand_in_root("phase7_guard_child_", with_logs=True)
    try:
        env = dict(os.environ)
        env[SUITE_GUARD.ENV_ROOTS] = os.pathsep.join([root, conftest.REPO_ROOT])
        _append_from_a_child(root, env)

        entries = SUITE_GUARD.read_report(SUITE_GUARD_REPORT, root)
        opened = [e for e in entries
                  if e["path"] == "logs/phase7_decision_log_testusdt.jsonl"]
        assert opened, (
            f"a child of the suite appended to a log directory and nothing "
            f"was recorded: {entries}")
        assert all(e["pid"] != os.getpid() for e in opened), opened
    finally:
        stop()
        shutil.rmtree(root, ignore_errors=True)


def test_a_process_the_suite_did_not_start_is_not_recorded():
    """
    The scheduled task's side, which is what entry 59 is about: the same
    append as the control above, from a process started with the environment
    the suite inherited rather than the one it set -- no PYTHONPATH entry, no
    watched roots, no report -- while this process watches the same root. The
    file grows and nothing is recorded, as on 2 November when the 18:05 run
    appended to five decision logs during `run_tests.py`.
    """
    root, stop = _stand_in_root("phase7_guard_other_", with_logs=True)
    try:
        env = dict(os.environ)
        env.pop(SUITE_GUARD.ENV_ROOTS, None)
        env.pop(SUITE_GUARD.ENV_REPORT, None)
        rest = [p for p in env.get("PYTHONPATH", "").split(os.pathsep)
                if p and p != conftest.SUITE_GUARD_DIR]
        if rest:
            env["PYTHONPATH"] = os.pathsep.join(rest)
        else:
            env.pop("PYTHONPATH", None)
        _append_from_a_child(root, env)

        assert _events(root) == [], _events(root)
    finally:
        stop()
        shutil.rmtree(root, ignore_errors=True)
