"""
Entry 57, 27 November 2026 -- run_tests.py leaves a record that it ran.

THE FINDING (27 October 2026, landing entry 31)

pytest rewrites .pytest_cache/v/cache/nodeids at the end of every run, so a
landing check can read off Viktor's disk that it ran after an apply.
run_tests.py wrote no file, so whether it ran, and what it counted, rested on
his silence. Ruled the same day, by Viktor agreeing to Claude's suggestion:
at the end of each run run_tests.py writes its finish time and its passed,
failed and errors counts to an ignored file, which a landing check reads as
it reads pytest's cache.

WHAT IS PINNED

1. A run writes the record, with the counts it printed and a finish time
   that carries its UTC offset.
2. A filtered run says which filters it had, so a run of one file is never
   read as a run of the suite.
3. A filter that matches nothing tests nothing and writes no record.
4. A record that cannot be written leaves the exit code as it was.
5. The record's folder is ignored by name in .gitignore, and the handover
   check -- which the pre-push hook runs, and which stops the push on any
   ignored file it does not know -- files it as routine.

No fixtures: run_tests.py calls every test with no arguments. Each test
loads its own copy of run_tests.py and points it at a temporary tests folder
and a temporary record path, so no test writes the real record or runs the
real suite. Tests 1 to 4 need only the standard library; test 5 needs git, as
tests/test_session_handover_check_ignored_filter.py does.
"""

import contextlib
import datetime
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from conftest import REPO_ROOT

RUNNER_PATH = os.path.join(REPO_ROOT, "run_tests.py")
HANDOVER_PATH = os.path.join(REPO_ROOT, "docs", "build", "session_handover_check.py")

PROBE_NAME = "test_p7_entry57_runner_probe"

# One test of each outcome run_tests.py counts: a pass, a failing assertion,
# and a test that takes an argument, which the runner calls with none and
# counts as an error.
PROBE_BODY = (
    "def test_passes():\n"
    "    assert True\n"
    "\n"
    "def test_fails():\n"
    "    assert False, 'probe failure'\n"
    "\n"
    "def test_takes_a_fixture(tmp_path):\n"
    "    pass\n"
)

ALL_PASS_BODY = "def test_passes():\n    assert True\n"


def _load(name):
    spec = importlib.util.spec_from_file_location(name, RUNNER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _run_probe(body, argv, record_path=None):
    """
    Run a private copy of run_tests.main on one probe file.

    Returns (exit code, the temporary directory, the record's path, printed
    output). The tests folder lives in that directory, and so does the record
    unless a path is given; the caller removes it. sys.path and sys.modules
    are put back.
    """
    work = tempfile.mkdtemp(prefix="phase7_entry57_")
    tests = os.path.join(work, "tests")
    os.makedirs(tests)
    with open(os.path.join(tests, PROBE_NAME + ".py"), "w", encoding="utf-8") as f:
        f.write(body)

    runner = _load("phase7_run_tests_under_test")
    runner.TESTS = tests
    runner.ROOT = work
    runner.LAST_RUN = record_path or os.path.join(work, ".run_tests_cache", "last_run.json")

    saved_path = list(sys.path)
    out = io.StringIO()
    try:
        with contextlib.redirect_stdout(out):
            code = runner.main(argv)
    finally:
        sys.path[:] = saved_path
        sys.modules.pop(PROBE_NAME, None)
    return code, work, runner.LAST_RUN, out.getvalue()


def _read(path):
    with open(path, encoding="utf-8") as f:
        return json.loads(f.read())


def test_a_run_writes_its_finish_time_and_its_counts():
    before = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)
    code, work, record_path, _ = _run_probe(PROBE_BODY, ["-q"])
    after = datetime.datetime.now(datetime.timezone.utc)
    try:
        assert code == 1, f"a run with a failure and an error returned {code}"
        record = _read(record_path)
        assert sorted(record) == ["errors", "failed", "filters", "finished", "passed"], record
        assert (record["passed"], record["failed"], record["errors"]) == (1, 1, 1), record
        assert record["filters"] == [], record
        finished = datetime.datetime.fromisoformat(record["finished"])
        assert finished.tzinfo is not None, (
            f"the finish time carries no UTC offset: {record['finished']!r}"
        )
        assert before <= finished <= after, (
            f"finish time {finished} is not inside the run ({before} to {after})"
        )
    finally:
        shutil.rmtree(work, ignore_errors=True)


def test_a_filtered_run_records_its_filters():
    code, work, record_path, _ = _run_probe(ALL_PASS_BODY, ["-q", "entry57"])
    try:
        assert code == 0, f"an all-pass run returned {code}"
        record = _read(record_path)
        assert record["filters"] == ["entry57"], record
        assert (record["passed"], record["failed"], record["errors"]) == (1, 0, 0), record
    finally:
        shutil.rmtree(work, ignore_errors=True)


def test_a_filter_matching_nothing_writes_no_record():
    code, work, record_path, _ = _run_probe(ALL_PASS_BODY, ["-q", "no_such_file_name"])
    try:
        assert code == 2, f"a filter matching nothing returned {code}"
        assert not os.path.exists(record_path), (
            "a run that tested nothing wrote a record a landing check would read as a run"
        )
    finally:
        shutil.rmtree(work, ignore_errors=True)


def test_a_record_that_cannot_be_written_leaves_the_exit_code_alone():
    blocker_dir = tempfile.mkdtemp(prefix="phase7_entry57_blocker_")
    blocker = os.path.join(blocker_dir, "a_file_not_a_folder")
    with open(blocker, "w", encoding="utf-8") as f:
        f.write("x")
    record_path = os.path.join(blocker, "last_run.json")
    try:
        code, work, _, output = _run_probe(ALL_PASS_BODY, ["-q"], record_path)
        try:
            assert code == 0, f"an all-pass run whose record failed returned {code}"
            assert "could not write the last-run record" in output, output
            assert not os.path.exists(record_path)
        finally:
            shutil.rmtree(work, ignore_errors=True)
    finally:
        shutil.rmtree(blocker_dir, ignore_errors=True)


def test_gitignore_names_the_record_folder():
    with open(os.path.join(REPO_ROOT, ".gitignore"), encoding="utf-8") as f:
        lines = [line.strip() for line in f.read().splitlines()]
    assert ".run_tests_cache/" in lines, (
        ".gitignore does not name .run_tests_cache/; the record would be ignored "
        "only by the *.json rule, which nothing ties to it"
    )


def test_the_record_is_ignored_and_the_handover_check_files_it_as_routine():
    spec = importlib.util.spec_from_file_location("phase7_handover_entry57", HANDOVER_PATH)
    handover = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(handover)

    work = tempfile.mkdtemp(prefix="phase7_entry57_repo_")
    try:
        def git(*args):
            return subprocess.run(["git", *args], cwd=work, capture_output=True, text=True)

        git("init", "-q")
        git("config", "user.email", "test@example.com")
        git("config", "user.name", "test")
        shutil.copyfile(os.path.join(REPO_ROOT, ".gitignore"), os.path.join(work, ".gitignore"))
        git("add", ".gitignore")
        git("commit", "-q", "-m", "initial")

        os.makedirs(os.path.join(work, ".run_tests_cache"))
        with open(os.path.join(work, ".run_tests_cache", "last_run.json"), "w") as f:
            f.write("{}\n")

        status = git("status", "--ignored", "--short").stdout.splitlines()
        assert "!! .run_tests_cache/" in status, (
            f"the record's folder is not ignored: {status}"
        )
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            flagged = handover.check_ignored_files(Path(work))
        assert flagged == [], (
            f"the handover check flags the record, so the pre-push hook would stop: {flagged}"
        )
    finally:
        shutil.rmtree(work, ignore_errors=True)
