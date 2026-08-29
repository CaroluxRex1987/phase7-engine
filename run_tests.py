#!/usr/bin/env python3
"""
Dependency-free test runner.

pytest is the intended way to run this suite:

    pip install -r requirements-dev.txt
    pytest -v

This script exists so the suite also runs on a machine with nothing but a
Python interpreter — no pytest, no plugins, no virtualenv. It discovers
test_*.py files in tests/, calls every test_* function, and reports.

Usage:
    python run_tests.py              # everything
    python run_tests.py imports      # only tests/test_imports.py
    python run_tests.py -q           # one line per file
    python run_tests.py --show-output    # don't suppress test stdout

OUTPUT CAPTURE, added 30 August 2026
------------------------------------
Each test's stdout is captured and discarded if the test passes. A failing or
erroring test gets its output printed underneath it, tail-first.

The engine prints an eighty-line panel on every run, and nine tests run the
engine. A full-suite run was therefore around nine hundred lines, of which
roughly fifty carried information — the rest was the same panel repeated, in
tests that had passed and whose output nobody was going to read.

That is not merely untidy. It made the signal hard to find in the noise on the
one occasion it mattered most: the module-duplication bug of 29 August was
visible in a full-suite run as a `400 Client Error ... api.mexc.com` line
buried inside a passing test's output, and it went unnoticed for a full run
cycle.

Suppressing passing output is the right default; --show-output restores the old
behaviour when a passing test's output is genuinely what you need to look at.

KNOWN LIMIT: logging output is not captured. The logging handlers bind to the
real sys.stderr when they are created, before any redirect is installed, so
`logger.info(...)` lines still appear inline. There are only a handful of them
per run, and they are usually the ones worth seeing.
"""

import contextlib
import importlib.util
import io
import os
import sys
import traceback

ROOT = os.path.dirname(os.path.abspath(__file__))
TESTS = os.path.join(ROOT, "tests")

# How many trailing lines of a failing test's output to show. The interesting
# part of an engine panel is the decision at the bottom, so the tail is the
# useful end.
# Deliberately short. The assertion message is printed in full in the Failures
# section below; this is supplementary context, not the finding.
TAIL_LINES = 12

GREEN, RED, YELLOW, GREY, BOLD, RESET = (
    "\033[32m", "\033[31m", "\033[33m", "\033[90m", "\033[1m", "\033[0m"
)
if not sys.stdout.isatty():
    GREEN = RED = YELLOW = GREY = BOLD = RESET = ""


def load(path):
    name = os.path.splitext(os.path.basename(path))[0]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _run_one(fn, capture):
    """
    Call one test, returning (outcome, message, captured_output).

    outcome is "pass", "fail" or "error". Output is captured only when
    `capture` is true; the buffer is returned either way so callers do not have
    to special-case it.
    """
    buf = io.StringIO()
    redirect = contextlib.redirect_stdout(buf) if capture else contextlib.nullcontext()
    try:
        with redirect:
            fn()
        return "pass", "", buf.getvalue()
    except AssertionError as e:
        return "fail", str(e), buf.getvalue()
    except Exception as e:
        return "error", f"{type(e).__name__}: {e}", buf.getvalue()


def _print_captured(output, indent="      "):
    """Print the tail of a failing test's captured stdout."""
    lines = output.rstrip().splitlines()
    if not lines:
        return
    hidden = len(lines) - TAIL_LINES
    if hidden > 0:
        print(f"{indent}{GREY}... {hidden} earlier lines suppressed "
              f"(--show-output for all){RESET}")
        lines = lines[-TAIL_LINES:]
    for line in lines:
        print(f"{indent}{GREY}|{RESET} {line}")


def main(argv):
    quiet = "-q" in argv
    show_output = "--show-output" in argv
    capture = not show_output
    filters = [a for a in argv if not a.startswith("-")]

    sys.path.insert(0, TESTS)
    sys.path.insert(0, ROOT)

    files = sorted(
        os.path.join(TESTS, f) for f in os.listdir(TESTS)
        if f.startswith("test_") and f.endswith(".py")
    )
    if filters:
        files = [f for f in files if any(k in os.path.basename(f) for k in filters)]

    passed, failed, errors = 0, [], []

    for path in files:
        rel = os.path.relpath(path, ROOT)
        try:
            mod = load(path)
        except Exception as e:
            errors.append((rel, f"could not load: {type(e).__name__}: {e}", ""))
            print(f"{RED}ERROR{RESET}  {rel}  (could not load: {e})")
            continue

        fns = [(n, getattr(mod, n)) for n in sorted(dir(mod))
               if n.startswith("test_") and callable(getattr(mod, n))]
        if not quiet:
            print(f"\n{BOLD}{rel}{RESET}  {GREY}({len(fns)} tests){RESET}")

        for name, fn in fns:
            outcome, msg, output = _run_one(fn, capture)

            if outcome == "pass":
                passed += 1
                if not quiet:
                    print(f"  {GREEN}PASS{RESET}  {name}")
                    if show_output:
                        _print_captured(output)
                continue

            if outcome == "fail":
                failed.append((rel, name, msg, output))
                if not quiet:
                    print(f"  {RED}FAIL{RESET}  {name}")
            else:
                errors.append((rel, f"{name}: {msg}", output))
                if not quiet:
                    print(f"  {YELLOW}ERROR{RESET} {name}  ({msg})")
                    if os.environ.get("VERBOSE"):
                        traceback.print_exc(file=sys.stderr)

            # A failing test's output is the one that is worth reading, so it
            # is printed next to the failure rather than held for the summary.
            if not quiet and output.strip():
                _print_captured(output)

    print(f"\n{BOLD}{'=' * 68}{RESET}")
    print(f"{GREEN}{passed} passed{RESET}   {RED}{len(failed)} failed{RESET}   "
          f"{YELLOW}{len(errors)} errors{RESET}")

    if failed:
        print(f"\n{BOLD}Failures{RESET}")
        for rel, name, msg, _ in failed:
            print(f"\n  {RED}{rel}::{name}{RESET}")
            for line in msg.strip().splitlines():
                print(f"    {line}")

    if errors:
        print(f"\n{BOLD}Errors{RESET}")
        for rel, msg, _ in errors:
            print(f"  {YELLOW}{rel}{RESET}  {msg}")

    return 1 if (failed or errors) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
