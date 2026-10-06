"""
B6 -- a run on pinned candles keeps its own decision log, archive and Exit
Watch state.

Viktor's ruling of 5 October 2026, point 6 (docs/PHASE7_DECISIONS.md, "Ruling,
5 October 2026 -- round 8 triaged ..."): "Runs on pinned data write to their
own decision log, archive and Exit Watch state, chosen by the code from the
run's source rather than by a setting someone has to remember." Found by
Claude's self-review of 5 October (B6), on Viktor's real log.

WHAT WAS WRONG

Every run wrote its decision record, its raw-input archive and its Exit Watch
state into config.LOG_DIR, whatever its candles were: the state file and the
log were keyed by symbol and timeframe only. On Viktor's machine the live log,
logs/phase7_decision_log_aerousdt.jsonl, holds nine runs on the synthetic
fixture (6 September 2026, provenance.source "pinned") and one hand-built
record among its live runs; logs/archive holds the synthetic run's archive;
and the first live run that day read its Exit Watch prior_state from the
pinned run 27 seconds earlier, so its "SuperTrend flipped" and "bias changed"
flags compared live AERO with a synthetic series. The twelve-month
paper-trading verdict will be read from the live log, so a reader who did not
filter would have counted synthetic runs as trades.

WHAT THE FIX DOES

The run's source decides, once per run (Phase7Engine._is_live_run), where its
records go: a live run keeps config.LOG_DIR exactly as before, and any other
run gets its pinned/ subdirectory (decision_log.records_dir). The decision log
follows the record's own provenance (decision_log.is_live_record): only a
record that says fetch.pinned is False goes in the live log. The records
already in the live log stay there; the ruling names them.

No pytest fixtures anywhere in this file: run_tests.py calls every test_*
function with no arguments, so a fixture parameter would become an error
there and move its watched count.
"""

import json
import os
import shutil
import tempfile
import types

import pytest


PINNED_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "fixtures", "pinned")
# A port nothing listens on: a fetch that escapes the pinned source, or the
# test double below, fails at the socket instead of reaching an exchange.
UNREACHABLE = "http://127.0.0.1:1"
SYMBOL = "AEROUSDT"
TIMEFRAME = "4h"
STATE_FILE = f"phase7_state_{SYMBOL}_{TIMEFRAME}.json"


def _engine_available():
    try:
        import pandas_ta  # noqa: F401
        return True
    except Exception:
        return False


def _config(log_dir):
    return types.SimpleNamespace(LOG_DIR=log_dir, engine_version="test")


def _record(pinned):
    """A decision whose provenance states its source, as the engine writes it."""
    return {
        "symbol": "TESTUSDT",
        "timeframe": "4h",
        "provenance": {
            "source": "pinned" if pinned else "https://api.mexc.com",
            "fetch": {"pinned": pinned},
        },
    }


def _route(log_dir, chart_dir, live):
    """
    One routed run on the committed fixture, logging under log_dir.

    live=False: through the pinned source, as every engine test does.

    live=True: no pinned source is set, so the run is live by the engine's own
    test, and the singleton's fetch_ohlc -- the one network call -- is replaced
    by a test double that serves the same fixture. The double replaces only
    the exchange; everything from get_tf() on is the production path. Its
    candles are labelled as a test double rather than as live or pinned.
    """
    from core import config
    from data.data_fetcher import DataFetcher, data_fetcher
    from models.signal_router import SignalRouter

    original_url = data_fetcher.base_url
    original_log, original_chart = config.LOG_DIR, config.CHART_DIR
    try:
        data_fetcher.base_url = UNREACHABLE
        config.LOG_DIR = log_dir
        config.CHART_DIR = chart_dir
        if live:
            def from_the_fixture(symbol, timeframe, limit=300, now=None):
                out = data_fetcher._load_pinned(PINNED_DIR, symbol, timeframe, limit)
                if hasattr(out, "attrs"):
                    out.attrs["candles"] = {"basis": "test double for a live fetch"}
                return out
            data_fetcher.fetch_ohlc = from_the_fixture
        else:
            DataFetcher.set_pinned_source(PINNED_DIR)
        return SignalRouter().route(symbol=SYMBOL, timeframe=TIMEFRAME)
    finally:
        DataFetcher.clear_pinned_source()
        data_fetcher.__dict__.pop("fetch_ohlc", None)
        data_fetcher.base_url = original_url
        config.LOG_DIR, config.CHART_DIR = original_log, original_chart


# ============================================================
# Where a record goes -- no engine needed
# ============================================================

def test_a_live_run_s_records_directory_is_the_log_directory_unchanged():
    from core import decision_log

    native = os.path.join(tempfile.gettempdir(), "phase7_b6") + os.sep
    for log_dir in ("logs/", "logs", native):
        assert decision_log.records_dir(log_dir, True) == log_dir, log_dir


def test_every_other_run_goes_to_pinned_spelled_the_same_on_every_platform():
    """
    Paths under this directory are written into the record and pinned by the
    golden snapshot, so it must be one string on Windows and Linux.
    """
    from core import decision_log

    assert decision_log.records_dir("logs/", False) == "logs/pinned/"
    assert decision_log.records_dir("logs", False) == "logs/pinned/"
    assert decision_log.records_dir("", False) == "pinned/"
    assert (decision_log.log_path(decision_log.records_dir("logs/", False), "TESTUSDT")
            == "logs/pinned/phase7_decision_log_testusdt.jsonl")

    # Windows spellings, as strings: built by string operations, so the same
    # answer on every platform, and this checks the Windows case on Linux too.
    assert decision_log.records_dir("C:\\phase7\\logs\\", False) == "C:/phase7/logs/pinned/"
    assert decision_log.records_dir("C:\\phase7\\logs", False) == "C:/phase7/logs/pinned/"

    # The form tests/conftest.py gives config.LOG_DIR: an absolute path ending
    # in os.sep, which has backslashes on Windows. The answer must not.
    native = os.path.join(tempfile.gettempdir(), "phase7_b6") + os.sep
    out = decision_log.records_dir(native, False)
    assert "\\" not in out, out
    assert out.endswith("/pinned/"), out


def test_only_a_record_that_says_it_was_fetched_live_is_live():
    """Both of provenance's statements of its source must say live."""
    from core import decision_log

    assert decision_log.is_live_record(_record(pinned=False)) is True

    # Each shape below is a live record with one thing wrong, so each guard
    # is tested on its own and none can be passed for another's reason.
    live = "https://api.mexc.com"
    not_live = [
        _record(pinned=True),
        {"symbol": "TESTUSDT"},                                     # no provenance at all
        {"provenance": None},
        None,
        "not a decision",
        {"provenance": {"source": live}},                          # no fetch block
        {"provenance": {"source": live, "fetch": None}},
        {"provenance": {"source": live, "fetch": {}}},
        {"provenance": {"source": live, "fetch": {"pinned": None}}},
        {"provenance": {"source": live, "fetch": {"pinned": 0}}},  # falsy is not False
        {"provenance": {"source": live, "fetch": {"pinned": "false"}}},
        {"provenance": {"fetch": {"pinned": False}}},              # no source
        {"provenance": {"source": None, "fetch": {"pinned": False}}},
        {"provenance": {"source": "pinned", "fetch": {"pinned": False}}},  # contradicts itself
    ]
    for decision in not_live:
        assert decision_log.is_live_record(decision) is False, decision


def test_write_files_a_record_by_what_it_says_about_its_source():
    from core import decision_log

    work = tempfile.mkdtemp(prefix="phase7_b6_write_")
    try:
        log_dir = os.path.join(work, "logs") + os.sep
        pinned_dir = decision_log.records_dir(log_dir, False)

        live_path = decision_log.write(_record(pinned=False), _config(log_dir))
        pinned_path = decision_log.write(_record(pinned=True), _config(log_dir))
        bare_path = decision_log.write({"symbol": "TESTUSDT"}, _config(log_dir))
        # Naming the directory does not override the choice: no caller can put
        # a pinned record in a live log.
        explicit_path = decision_log.write(_record(pinned=True), _config("unused/"),
                                           log_dir=log_dir)

        assert live_path == decision_log.log_path(log_dir, "TESTUSDT")
        expected = decision_log.log_path(pinned_dir, "TESTUSDT")
        assert pinned_path == bare_path == explicit_path == expected

        live = decision_log.read(log_dir, "TESTUSDT")
        assert [r["decision"]["provenance"]["fetch"]["pinned"] for r in live] == [False], (
            "the live log holds something other than the one live record"
        )
        assert len(decision_log.read(pinned_dir, "TESTUSDT")) == 3
    finally:
        shutil.rmtree(work, ignore_errors=True)


# ============================================================
# The engine, end to end
# ============================================================

def test_a_pinned_run_files_its_log_archive_and_state_under_pinned_only():
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    from core import decision_log

    work = tempfile.mkdtemp(prefix="phase7_b6_pinned_")
    try:
        log_dir = os.path.join(work, "logs") + os.sep
        decision = _route(log_dir, os.path.join(work, "charts"), live=False)
        assert not decision.get("error"), decision.get("error")
        assert decision["provenance"]["fetch"]["pinned"] is True

        pinned = decision_log.records_dir(log_dir, False)
        assert decision["decision_log_path"] == decision_log.log_path(pinned, SYMBOL)
        assert os.path.isfile(decision["decision_log_path"])
        archive = decision["lineage"]["archive"]["path"]
        assert archive and archive.startswith(pinned + "archive/"), archive
        assert os.path.isfile(archive)
        assert os.path.isfile(os.path.join(pinned, STATE_FILE))

        assert sorted(os.listdir(log_dir)) == ["pinned"], (
            "a pinned run left something where live runs keep their records: "
            f"{sorted(os.listdir(log_dir))}"
        )
    finally:
        shutil.rmtree(work, ignore_errors=True)


def test_a_live_run_files_its_log_archive_and_state_where_they_always_were():
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    from core import decision_log, lineage
    from data.data_fetcher import DataFetcher

    work = tempfile.mkdtemp(prefix="phase7_b6_live_")
    try:
        assert DataFetcher.pinned_source() is None, (
            "a pinned source is set in this process, so this run cannot be live"
        )
        log_dir = os.path.join(work, "logs") + os.sep
        decision = _route(log_dir, os.path.join(work, "charts"), live=True)
        assert not decision.get("error"), decision.get("error")
        assert decision["provenance"]["fetch"]["pinned"] is False
        assert decision["provenance"]["source"] == UNREACHABLE

        assert decision["decision_log_path"] == decision_log.log_path(log_dir, SYMBOL)
        assert os.path.isfile(decision["decision_log_path"])
        archive = decision["lineage"]["archive"]["path"]
        assert archive and archive.startswith(lineage.archive_dir(log_dir) + "/"), archive
        assert os.path.isfile(archive)
        assert os.path.isfile(os.path.join(log_dir, STATE_FILE))

        assert not os.path.exists(decision_log.records_dir(log_dir, False)), (
            "a live run wrote under pinned/"
        )
    finally:
        shutil.rmtree(work, ignore_errors=True)


def test_exit_watch_compares_a_run_only_with_the_last_run_from_its_own_source():
    """
    The 6 September defect: a live run read its prior state from a pinned
    run. Each source's state file is seeded with a different prior run, and
    each run must report the one from its own source -- and a pinned run must
    leave the live state as it found it.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    from core import decision_log

    work = tempfile.mkdtemp(prefix="phase7_b6_state_")
    try:
        log_dir = os.path.join(work, "logs") + os.sep
        charts = os.path.join(work, "charts")
        pinned = decision_log.records_dir(log_dir, False)
        live_prior = {"supertrend_direction": -1.0, "detailed_bias": "BEARISH CONFIRMED"}
        pinned_prior = {"supertrend_direction": 1.0, "detailed_bias": "NEUTRAL"}
        os.makedirs(pinned)
        with open(os.path.join(log_dir, STATE_FILE), "w") as fh:
            json.dump(live_prior, fh)
        with open(os.path.join(pinned, STATE_FILE), "w") as fh:
            json.dump(pinned_prior, fh)

        pinned_run = _route(log_dir, charts, live=False)
        assert not pinned_run.get("error"), pinned_run.get("error")
        assert pinned_run["provenance"]["prior_state"] == pinned_prior

        with open(os.path.join(log_dir, STATE_FILE)) as fh:
            assert json.load(fh) == live_prior, "a pinned run rewrote the live state"

        live_run = _route(log_dir, charts, live=True)
        assert not live_run.get("error"), live_run.get("error")
        assert live_run["provenance"]["prior_state"] == live_prior
    finally:
        shutil.rmtree(work, ignore_errors=True)


def test_each_source_prunes_only_its_own_archives():
    """
    The ninety-day prune runs at the end of every run. Each source's runs
    prune their own archive directory: a live run ages out an expired live
    archive and leaves an expired pinned one, and a pinned run the other way
    round.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    import time

    from core import decision_log, lineage

    work = tempfile.mkdtemp(prefix="phase7_b6_prune_")
    ancient = time.time() - (200 * 86400)

    def expired_archive(directory, digit):
        archive_dir = lineage.archive_dir(directory)
        os.makedirs(archive_dir, exist_ok=True)
        path = os.path.join(archive_dir, f"aerousdt_4h_{digit * 16}.json.gz")
        with open(path, "wb") as fh:
            fh.write(b"expired")
        os.utime(path, (ancient, ancient))
        return path

    try:
        log_dir = os.path.join(work, "logs") + os.sep
        charts = os.path.join(work, "charts")
        pinned = decision_log.records_dir(log_dir, False)

        live_first = expired_archive(log_dir, "a")
        pinned_old = expired_archive(pinned, "b")
        live_run = _route(log_dir, charts, live=True)
        assert not live_run.get("error"), live_run.get("error")
        assert live_run["lineage"]["archive"]["pruned_this_run"] == 1
        assert not os.path.exists(live_first)
        assert os.path.exists(pinned_old), "a live run pruned a pinned archive"

        live_second = expired_archive(log_dir, "c")
        pinned_run = _route(log_dir, charts, live=False)
        assert not pinned_run.get("error"), pinned_run.get("error")
        assert pinned_run["lineage"]["archive"]["pruned_this_run"] == 1
        assert not os.path.exists(pinned_old)
        assert os.path.exists(live_second), "a pinned run pruned a live archive"
    finally:
        shutil.rmtree(work, ignore_errors=True)


def test_a_broken_pinned_request_is_not_a_live_run():
    """
    PHASE7_PINNED_DATA naming something that is not a directory makes
    pinned_source() raise. The run fails at its fetch, as it did before B6;
    until then it must not count as live, and nothing is written anywhere.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    from core import config
    from core.engine_core import Phase7Engine
    from data.data_fetcher import PINNED_ENV_VAR, DataFetcher, data_fetcher
    from models.signal_router import SignalRouter

    work = tempfile.mkdtemp(prefix="phase7_b6_broken_")
    previous = os.environ.get(PINNED_ENV_VAR)
    original_url = data_fetcher.base_url
    original_log, original_chart = config.LOG_DIR, config.CHART_DIR
    try:
        not_a_directory = os.path.join(work, "not_a_directory")
        with open(not_a_directory, "w") as fh:
            fh.write("x")
        os.environ[PINNED_ENV_VAR] = not_a_directory
        with pytest.raises(ValueError):
            DataFetcher.pinned_source()

        assert Phase7Engine._is_live_run() is False

        log_dir = os.path.join(work, "logs") + os.sep
        data_fetcher.base_url = UNREACHABLE
        config.LOG_DIR = log_dir
        config.CHART_DIR = os.path.join(work, "charts")
        decision = SignalRouter().route(symbol=SYMBOL, timeframe=TIMEFRAME)

        assert PINNED_ENV_VAR in (decision.get("error") or ""), decision.get("error")
        assert not os.path.exists(log_dir), os.listdir(log_dir)
    finally:
        if previous is None:
            os.environ.pop(PINNED_ENV_VAR, None)
        else:
            os.environ[PINNED_ENV_VAR] = previous
        data_fetcher.base_url = original_url
        config.LOG_DIR, config.CHART_DIR = original_log, original_chart
        shutil.rmtree(work, ignore_errors=True)


# ============================================================
# A consequence outside the engine: the audit package's transcripts
# ============================================================

def test_the_audit_package_redacts_the_temp_directory_in_both_spellings():
    """
    docs/build/build_audit_package.py captures two pinned runs into the audit
    package and replaces their temp directory, which on Windows holds the
    machine's username, with <TEMP>. Since B6 a pinned run's "Decision logged
    to" line names that directory with forward slashes, which the native,
    backslashed spelling does not match. Checked on strings, so it holds on
    Linux for the Windows case.
    """
    import importlib.util

    from conftest import REPO_ROOT
    from core import decision_log

    spec = importlib.util.spec_from_file_location(
        "phase7_build_audit_package_b6",
        os.path.join(REPO_ROOT, "docs", "build", "build_audit_package.py"))
    bap = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bap)

    work = "C:\\Users\\someone\\AppData\\Local\\Temp\\phase7_transcripts_x"
    logged = decision_log.log_path(
        decision_log.records_dir(work + "\\logs", False), SYMBOL)
    line = f"Decision logged to {logged}"
    for actual, placeholder in bap._temp_redaction(work).items():
        line = line.replace(actual, placeholder)

    assert "someone" not in line, line
    assert line == "Decision logged to <TEMP>/logs/pinned/phase7_decision_log_aerousdt.jsonl", line
