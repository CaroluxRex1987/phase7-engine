"""
run_tests.py's own filter argument, made checkable — round 6 (GPT-6 Astra).

WHAT WAS WRONG (Section 7.3 of the round-5 report, confirmed by requested-run
6, 12 September 2026)

`python run_tests.py <filter>` keeps only the test files whose basename
contains one of the filter strings. Before this fix, a filter matching zero
files fell straight through main()'s loop with passed=0, failed=[], errors=[],
and `return 1 if (failed or errors) else 0` at the bottom returned 0 — a green
exit code for a run that tested nothing. A typo'd filter, or a filter for a
file that had just been renamed or deleted, is indistinguishable from a
run where everything passed, to anything reading the exit code alone (a CI
step, a pre-commit hook, a habit of running the filtered form to save time).

THE FIX

main() now checks, immediately after building the filtered file list and
before the loop that runs anything: if a filter was given and it matched no
files, print which filter matched nothing and return exit code 2. An
unfiltered run (files never empty on a repository with any test_*.py files)
and a filter that matches at least one file are both unaffected — this
guards only the specific silently-green case.

Run as subprocesses, deliberately: this is checking the script's own process
exit code and stdout, not calling its functions in-process (which would not
exercise `if __name__ == "__main__": sys.exit(main(...))` at all, and would
leak main()'s sys.path.insert side effects into this process).
"""

import os
import subprocess
import sys
import tempfile

from conftest import REPO_ROOT

RUN_TESTS = os.path.join(REPO_ROOT, "run_tests.py")


def _run(args, timeout=60):
    return subprocess.run(
        [sys.executable, RUN_TESTS] + args,
        cwd=REPO_ROOT, capture_output=True, text=True, timeout=timeout,
    )


def test_a_filter_matching_nothing_exits_non_zero():
    proc = _run(["-q", "this_matches_no_test_file_anywhere"])

    assert proc.returncode != 0, (
        "a filter matching zero test files exited 0 — the exact defect "
        "Section 7.3 named: a run that tested nothing looks, by exit code "
        "alone, identical to a run where everything passed.\n"
        f"stdout: {proc.stdout!r}"
    )
    assert "0 passed" not in proc.stdout, (
        "expected this to be caught before the summary line ever printed, "
        f"but got: {proc.stdout!r}"
    )


def test_a_filter_matching_something_still_exits_zero_and_runs_it():
    """
    The negative control. Without it, the assertion above could pass because
    every filtered run now fails, not because zero-match specifically does.

    Uses a temporary, self-contained test file rather than an existing one in
    tests/ -- found the hard way, running this file without pandas_ta
    installed: tests/test_imports.py has a test that calls pytest.skip() when
    pandas_ta is absent, and run_tests.py has no notion of "skipped" (see
    _run_one's own comment) -- a skip becomes an "error" there, which made
    THIS test's own exit-code-0 assumption environment-dependent, exactly the
    kind of thing this file exists to not do. A throwaway file with one
    trivial, dependency-free test sidesteps every real test file's own
    situation, whatever it is on whatever machine this runs on.
    """
    fd, path = tempfile.mkstemp(
        prefix="test_zzz_run_tests_control_", suffix=".py", dir=os.path.join(REPO_ROOT, "tests"))
    try:
        with os.fdopen(fd, "w") as f:
            f.write("def test_this_always_passes():\n    assert True\n")
        marker = os.path.splitext(os.path.basename(path))[0]

        proc = _run(["-q", marker])

        assert proc.returncode == 0, (
            f"filtering to a trivial, always-passing test file did not exit "
            f"0.\nstdout: {proc.stdout!r}\nstderr: {proc.stderr!r}"
        )
        assert "1 passed" in proc.stdout, (
            f"the trivial test did not appear to run: {proc.stdout!r}"
        )
    finally:
        os.remove(path)


def test_an_unfiltered_run_is_not_affected_by_the_zero_match_guard():
    """
    The guard only fires when `filters` is non-empty. Confirms the empty-
    filters path (no arguments at all) never hits the new check regardless of
    how many files exist -- checked at the source-text level, not by running
    the whole suite here, which would duplicate the rest of this test run.
    """
    with open(RUN_TESTS, encoding="utf-8") as f:
        src = f.read()

    assert "if not files:" in src and "if filters:" in src, (
        "expected the zero-match guard to be written inside the `if filters:` "
        "block, so an unfiltered invocation (filters == []) never reaches it"
    )
