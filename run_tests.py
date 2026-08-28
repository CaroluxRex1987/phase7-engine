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
"""

import importlib.util
import os
import sys
import traceback

ROOT = os.path.dirname(os.path.abspath(__file__))
TESTS = os.path.join(ROOT, "tests")

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


def main(argv):
    quiet = "-q" in argv
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
            errors.append((rel, f"could not load: {type(e).__name__}: {e}"))
            print(f"{RED}ERROR{RESET}  {rel}  (could not load: {e})")
            continue

        fns = [(n, getattr(mod, n)) for n in sorted(dir(mod))
               if n.startswith("test_") and callable(getattr(mod, n))]
        if not quiet:
            print(f"\n{BOLD}{rel}{RESET}  {GREY}({len(fns)} tests){RESET}")

        for name, fn in fns:
            try:
                fn()
                passed += 1
                if not quiet:
                    print(f"  {GREEN}PASS{RESET}  {name}")
            except AssertionError as e:
                failed.append((rel, name, str(e)))
                if not quiet:
                    print(f"  {RED}FAIL{RESET}  {name}")
            except Exception as e:
                errors.append((rel, f"{name}: {type(e).__name__}: {e}"))
                if not quiet:
                    print(f"  {YELLOW}ERROR{RESET} {name}  ({type(e).__name__}: {e})")
                    if os.environ.get("VERBOSE"):
                        traceback.print_exc()

    print(f"\n{BOLD}{'=' * 68}{RESET}")
    print(f"{GREEN}{passed} passed{RESET}   {RED}{len(failed)} failed{RESET}   "
          f"{YELLOW}{len(errors)} errors{RESET}")

    if failed:
        print(f"\n{BOLD}Failures{RESET}")
        for rel, name, msg in failed:
            first = msg.strip().splitlines()[0] if msg.strip() else "(no message)"
            print(f"\n  {RED}{rel}::{name}{RESET}")
            for line in msg.strip().splitlines():
                print(f"    {line}")

    if errors:
        print(f"\n{BOLD}Errors{RESET}")
        for rel, msg in errors:
            print(f"  {YELLOW}{rel}{RESET}  {msg}")

    return 1 if (failed or errors) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
