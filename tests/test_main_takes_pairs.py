"""
main.py takes the pairs to run, and works from its own folder (17 October 2026).

Viktor's ruling of 17 October (docs/PHASE7_DECISIONS.md, "Ruling, 17 October
2026 — the forward measurement ...") runs ten pairs every four hours, started
by Windows Task Scheduler, to measure how often the engine says LONG. Until
then main.py ran only config.SYMBOL, and wrote its logs into whichever folder
it was started from -- for a scheduled task, a folder that is not the
repository.

Each test here reads main.py run as a script in a subprocess, on pinned data,
in a copy of the engine inside a temporary folder, so nothing here can reach
the real logs/. What they hold:

  - every pair named runs, in order, and its record names it twice: as the
    decision's symbol and as its config's SYMBOL;
  - a pair that fails writes no decision record, leaves its error in the
    process log, and does not stop the pairs after it; the exit code is 1;
  - a run started from another folder writes into the engine's folder, and
    leaves the folder it was started from empty;
  - a pair's record is the same whether it runs alone or after other pairs in
    the same process: only logged_at differs;
  - a run with no console -- sys.stdout and sys.stderr None, as under
    pythonw.exe -- still writes its record and exits 0;
  - with no pair named, main.py runs config.SYMBOL as before, and its record is
    the one an explicit AEROUSDT makes;
  - importing main does not change folder, and a malformed pair refuses the
    whole command with exit code 2 before any pair runs.

TESTUSDT is AEROUSDT's pinned candles with every price p made 3 * sqrt(p):
the order of every open, high, low and close is kept, so each candle stays
valid, while every percentage move -- and so every indicator -- differs. A
pair that carried something over from the pair before it would show here;
with identical candles it could not.

In Claude's sandbox all of this is Linux evidence. The Windows half -- the
folder Task Scheduler starts a task in, and pythonw.exe itself -- is checked by
the first scheduled run on Viktor's machine.

No fixtures: run_tests.py calls every test with no arguments. Every test skips
under pytest when pandas_ta is absent, because the engine cannot run.
"""

import atexit
import csv
import json
import os
import shutil
import subprocess
import sys
import tempfile

import pytest

from conftest import REPO_ROOT

ENGINE_DIRS = ("core", "data", "indicators", "models", "structure", "utils")
ENGINE_FILES = ("main.py", "__init__.py")
PINNED = os.path.join(REPO_ROOT, "tests", "fixtures", "pinned")
TIMEOUT = 300

_RUNS = None


def _engine_available():
    try:
        import pandas_ta  # noqa: F401
        return True
    except Exception:
        return False


def _copy_engine(dest):
    os.makedirs(dest)
    for d in ENGINE_DIRS:
        shutil.copytree(os.path.join(REPO_ROOT, d), os.path.join(dest, d),
                        ignore=shutil.ignore_patterns("__pycache__"))
    for f in ENGINE_FILES:
        shutil.copy2(os.path.join(REPO_ROOT, f), dest)
    return dest


def _make_pinned(dest):
    os.makedirs(dest)
    for f in ("AEROUSDT_4h.csv", "AEROUSDT_1d.csv", "BTCUSDT_4h.csv"):
        shutil.copy2(os.path.join(PINNED, f), dest)
    for tf in ("4h", "1d"):
        with open(os.path.join(PINNED, f"AEROUSDT_{tf}.csv"), newline="") as fh:
            rows = list(csv.reader(fh))
        out = [rows[0]]
        for r in rows[1:]:
            prices = [round(3.0 * float(x) ** 0.5, 8) for x in r[1:5]]
            out.append([r[0], *prices, r[5]])
        with open(os.path.join(dest, f"TESTUSDT_{tf}.csv"), "w", newline="") as fh:
            csv.writer(fh, lineterminator="\n").writerows(out)
    return dest


def _env(pinned):
    env = dict(os.environ)
    env["PHASE7_PINNED_DATA"] = pinned
    env.pop("PHASE7_UPDATE_SNAPSHOT", None)
    return env


def _run(args, cwd, env, code=None):
    """`python <args>`, or `python -c <code> <args>` when code is given."""
    cmd = [sys.executable, *(["-c", code] if code is not None else []), *args]
    return subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True,
                          timeout=TIMEOUT)


def _records(engine, symbol):
    path = os.path.join(engine, "logs", "pinned",
                        f"phase7_decision_log_{symbol.lower()}.jsonl")
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def _process_log(engine):
    path = os.path.join(engine, "logs", "phase7_engine.log")
    if not os.path.exists(path):
        return ""
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def _decision_logs_under(root):
    return sorted(os.path.relpath(os.path.join(d, f), root)
                  for d, _, files in os.walk(root) for f in files
                  if f.startswith("phase7_decision_log_"))


# What the import-and-refuse run (D) does, as a script of its own; its
# argument is the engine copy to import main from.
_IMPORT_AND_REFUSE = r"""
import json, os, sys
sys.path.insert(0, sys.argv[1])
before = os.getcwd()
import main
after = os.getcwd()
cases = [
    [], ["ETHUSDT", "SOLUSDT"], ["solusdt"], ["SOLUSD"], ["SOL/USDT"],
    ["USDT"], ["ETHUSDT", "ETHUSDT"],
]
parsed = []
for args in cases:
    try:
        parsed.append(main.parse_pairs(args))
    except ValueError as e:
        parsed.append("ValueError: " + str(e))
exit_code = main.main(["AEROUSDT", "solusdt"])
print(json.dumps({"before": before, "after": after, "parsed": parsed,
                  "exit": exit_code}))
"""

# A run with no console: what pythonw.exe gives a script. Its argument is
# the copy's main.py.
_NO_CONSOLE = r"""
import runpy, sys
sys.stdout = sys.stderr = None
sys.argv = [sys.argv[1], "TESTUSDT"]
runpy.run_path(sys.argv[0], run_name="__main__")
"""


def _runs():
    """Run main.py four ways, once per test process, and keep what came back."""
    global _RUNS
    if _RUNS is not None:
        return _RUNS
    root = tempfile.mkdtemp(prefix="phase7_main_pairs_")
    atexit.register(shutil.rmtree, root, True)
    pinned = _make_pinned(os.path.join(root, "pinned"))
    env = _env(pinned)
    elsewhere = os.path.join(root, "started_here")
    os.makedirs(elsewhere)

    # A: three pairs, the middle one with no data, started from another folder.
    a = _copy_engine(os.path.join(root, "engine_a"))
    run_a = _run([os.path.join(a, "main.py"), "AEROUSDT", "NODATAUSDT", "TESTUSDT"],
                 cwd=elsewhere, env=env)

    # B: TESTUSDT alone, with no console, started from its own folder.
    b = _copy_engine(os.path.join(root, "engine_b"))
    run_b = _run([os.path.join(b, "main.py")], cwd=b, env=env, code=_NO_CONSOLE)

    # C: no pair named, started from its own folder, as Viktor runs it by hand.
    c = _copy_engine(os.path.join(root, "engine_c"))
    run_c = _run(["main.py"], cwd=c, env=env)

    # D: main imported from another folder, then a malformed pair.
    d = _copy_engine(os.path.join(root, "engine_d"))
    elsewhere_d = os.path.join(root, "imported_from_here")
    os.makedirs(elsewhere_d)
    run_d = _run([d], cwd=elsewhere_d, env=env, code=_IMPORT_AND_REFUSE)

    _RUNS = {"root": root, "elsewhere": elsewhere, "elsewhere_d": elsewhere_d,
             "a": a, "b": b, "c": c, "d": d,
             "run_a": run_a, "run_b": run_b, "run_c": run_c, "run_d": run_d}
    return _RUNS


def _need_engine():
    if not _engine_available():
        pytest.skip("pandas_ta not installed")


def _without_logged_at(record):
    return {k: v for k, v in record.items() if k != "logged_at"}


def _starts(log):
    return [line.split("Starting Phase-7 engine for ", 1)[1].split(" on ", 1)[0]
            for line in log.splitlines() if "Starting Phase-7 engine for " in line]


def test_each_pair_named_runs_and_its_record_names_it():
    _need_engine()
    r = _runs()
    assert _starts(_process_log(r["a"])) == ["AEROUSDT", "NODATAUSDT", "TESTUSDT"], (
        "the pairs did not start in the order named:\n" + _process_log(r["a"]))
    for symbol in ("AEROUSDT", "TESTUSDT"):
        records = _records(r["a"], symbol)
        assert len(records) == 1, f"{symbol}: {len(records)} records, expected 1"
        rec = records[0]
        assert rec["decision"]["symbol"] == symbol
        assert rec["config"]["SYMBOL"] == symbol, (
            f"{symbol}'s record says its config's SYMBOL was "
            f"{rec['config']['SYMBOL']!r}: config.SYMBOL was not set for the run")


def test_a_failed_pair_leaves_only_a_log_line_and_the_rest_still_run():
    _need_engine()
    r = _runs()
    assert r["run_a"].returncode == 1, (
        f"exit code {r['run_a'].returncode}, expected 1 for one failed pair\n"
        + r["run_a"].stderr[-2000:])
    assert _records(r["a"], "NODATAUSDT") == [], "the failed pair wrote a decision record"
    log = _process_log(r["a"])
    assert "Engine returned error for NODATAUSDT: " in log
    assert "1 of 3 pairs failed: NODATAUSDT" in log
    assert len(_records(r["a"], "TESTUSDT")) == 1, (
        "the pair after the failed one did not run")


def test_a_run_started_from_another_folder_writes_into_the_engines_folder():
    _need_engine()
    r = _runs()
    left = sorted(os.listdir(r["elsewhere"]))
    assert left == [], f"the folder the run was started from received {left}"
    assert _decision_logs_under(r["a"]) == [
        os.path.join("logs", "pinned", "phase7_decision_log_aerousdt.jsonl"),
        os.path.join("logs", "pinned", "phase7_decision_log_testusdt.jsonl"),
    ]
    assert "Phase-7 engine completed successfully for TESTUSDT" in _process_log(r["a"])


def test_a_pair_reads_the_same_alone_as_after_other_pairs():
    _need_engine()
    r = _runs()
    after_others = _records(r["a"], "TESTUSDT")
    alone = _records(r["b"], "TESTUSDT")
    assert len(after_others) == 1 and len(alone) == 1
    assert _without_logged_at(after_others[0]) == _without_logged_at(alone[0]), (
        "TESTUSDT's record differs when it runs after AEROUSDT and a failed pair "
        "in the same process: something carried over from one run to the next")
    # The comparison means something only if the two pairs' candles differ.
    aero = _records(r["a"], "AEROUSDT")[0]["decision"]
    assert aero["lineage"]["run_hash"] != after_others[0]["decision"]["lineage"]["run_hash"]


def test_a_run_with_no_console_still_writes_its_record():
    _need_engine()
    r = _runs()
    assert r["run_b"].returncode == 0, (
        f"exit code {r['run_b'].returncode} with no console\n" + r["run_b"].stderr[-2000:])
    assert len(_records(r["b"], "TESTUSDT")) == 1
    assert "Phase-7 engine completed successfully for TESTUSDT" in _process_log(r["b"])


def test_no_pair_named_runs_the_configured_pair_as_before():
    _need_engine()
    r = _runs()
    assert r["run_c"].returncode == 0, r["run_c"].stderr[-2000:]
    assert _starts(_process_log(r["c"])) == ["AEROUSDT"]
    default = _records(r["c"], "AEROUSDT")
    named = _records(r["a"], "AEROUSDT")
    assert len(default) == 1 and len(named) == 1
    assert default[0]["config"]["SYMBOL"] == "AEROUSDT"
    assert _without_logged_at(default[0]) == _without_logged_at(named[0]), (
        "the run with no pair named differs from the run that names AEROUSDT")


def _run_d():
    r = _runs()
    assert r["run_d"].returncode == 0, r["run_d"].stderr[-2000:]
    return r, json.loads(r["run_d"].stdout.strip().splitlines()[-1])


def test_importing_main_does_not_change_folder():
    _need_engine()
    r, out = _run_d()
    assert out["before"] == out["after"] == r["elsewhere_d"], (
        f"importing main moved the working folder from {out['before']} to "
        f"{out['after']}; tests/test_imports.py relies on it staying put")


def test_a_malformed_pair_refuses_the_whole_command():
    _need_engine()
    r, out = _run_d()
    assert out["exit"] == 2, f"exit code {out['exit']}, expected 2"
    written = _decision_logs_under(r["d"]) + _decision_logs_under(r["elsewhere_d"])
    assert written == [], f"the refused command wrote decision records: {written}"
    # Imported, not run as a script, so its process log is where it was imported.
    log = _process_log(r["elsewhere_d"])
    assert "Refused, and no pair was run: " in log and "'solusdt'" in log
    assert "Starting Phase-7 engine" not in log


def test_the_pair_rules():
    _need_engine()
    _, out = _run_d()
    parsed = out["parsed"]
    assert parsed[0] == ["AEROUSDT"], "no pair named should mean config.SYMBOL"
    assert parsed[1] == ["ETHUSDT", "SOLUSDT"], "pairs should keep the order named"
    for i, bad in ((2, "solusdt"), (3, "SOLUSD"), (4, "SOL/USDT"), (5, "USDT")):
        assert isinstance(parsed[i], str) and parsed[i].startswith("ValueError: "), (
            f"{bad!r} was accepted: {parsed[i]!r}")
        assert repr(bad) in parsed[i]
    assert parsed[6] == "ValueError: named more than once: ETHUSDT"
