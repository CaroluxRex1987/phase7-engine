"""
docs/build/count_forward_measurement.py -- the forward measurement's count.

Written 7 November 2026 with the script, from DECISIONS, "Decision, 17 October
2026 -- how the forward measurement is counted", before the reading of
14 November. Synthetic records and process logs only, built here in a
temporary folder; no test reads the live logs. Expected values are worked by
hand from the decision's rules and the script's READINGS, not taken from its
output.

No fixtures: run_tests.py calls every test with no arguments.
"""

import datetime as dt
import importlib.util
import io
import json
import os
import shutil
import sys
import tempfile
from contextlib import redirect_stdout

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
TOOL_PATH = os.path.join(REPO, "docs", "build", "count_forward_measurement.py")
UTC = dt.timezone.utc
HASH = "816d4951" + "0" * 56
OTHER = "aaaaaaaa" + "1" * 56
PAIRS = ("AEROUSDT", "ETHUSDT")


def _tool():
    if REPO not in sys.path:
        sys.path.insert(0, REPO)
    spec = importlib.util.spec_from_file_location("phase7_count_forward", TOOL_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _t(text):
    return dt.datetime.fromisoformat(text).replace(tzinfo=UTC)


def _record(pair, opened, action="WAIT", after=dt.timedelta(minutes=5, seconds=10),
            logged=None, code_hash=HASH, degraded=False, pinned=False, rows=449):
    """A live 4h decision record whose struct candle opened at `opened` (UTC text)."""
    o = _t(opened)
    close = o + dt.timedelta(hours=4)
    when = logged if logged is not None else close + after
    fmt = "%Y-%m-%d %H:%M:%S"
    return {
        "logged_at": when.isoformat(),
        "decision": {
            "symbol": pair, "timeframe": "4h",
            "exit": {"action": action},
            "degradation": {"degraded": degraded,
                            "missing_inputs": ["volume: synthetic"] if degraded else []},
            "provenance": {
                "source": "pinned" if pinned else "https://api.mexc.com",
                "fetch": {"pinned": pinned},
                "code_hash": code_hash, "row_count": rows,
                "decision_candles": {"struct": {
                    "open_time": o.strftime(fmt), "close_time": close.strftime(fmt),
                    "exchange_close_time": close.strftime(fmt),
                    "forming_candles_dropped": 1}},
            },
        },
    }


class _Logs:
    """A temporary log folder: decision logs per pair, and a process log."""

    def __init__(self):
        self.dir = tempfile.mkdtemp(prefix="phase7_count_forward_")

    def write(self, records, process_lines=()):
        by_pair = {}
        for r in records:
            by_pair.setdefault(r["decision"]["symbol"].lower(), []).append(r)
        for pair, rows in by_pair.items():
            with open(os.path.join(self.dir, f"phase7_decision_log_{pair}.jsonl"), "w",
                      encoding="utf-8") as f:
                for r in rows:
                    f.write(json.dumps(r) + "\n")
        with open(os.path.join(self.dir, "phase7_engine.log"), "w", encoding="utf-8") as f:
            for line in process_lines:
                f.write(line + "\n")
        return self.dir

    def close(self):
        shutil.rmtree(self.dir, ignore_errors=True)


def _count(records, process_lines=(), last_open="2026-10-17 16:00:00",
           first_open="2026-10-17 08:00:00", pairs=PAIRS, code_hash=None):
    tool = _tool()
    logs = _Logs()
    try:
        d = logs.write(records, process_lines)
        res = tool.count(tool.gaps.read_logs(d),
                         tool.read_process_log(os.path.join(d, "phase7_engine.log")),
                         _t(last_open), first_open=_t(first_open), code_hash=code_hash,
                         pairs=pairs)
    finally:
        logs.close()
    return res


def _run_lines(local_start, pairs, outcome="ok", reason=None):
    """Process-log lines of one run, a pair every two seconds from `local_start`."""
    t = dt.datetime.fromisoformat(local_start)
    out = []
    for p in pairs:
        stamp = t.strftime("%Y-%m-%d %H:%M:%S") + ",100"
        out.append(f"{stamp} - INFO - Starting Phase-7 engine for {p} on 4h")
        out.append(f"{stamp} - INFO - Volume profile: processed 449 candles, skipped 0")
        if outcome == "ok":
            out.append(f"{stamp} - INFO - Phase-7 engine completed successfully for {p}")
        else:
            out.append(f"{stamp} - ERROR - DataFrame validation failed - empty or None "
                       "DataFrame in base market data")
            out.append(f"{stamp} - ERROR - Engine returned error for {p}: {reason}")
        t += dt.timedelta(seconds=2)
    return out


NOT_FINAL = ("Data fetch failed: API data for X 4h failed validation: not yet final: the "
             "last candle closed at 2026-10-17 12:00:00 (UTC), 0 days 00:00:02.3 before "
             "the reference time -- inside the 60-second grace for exchange delay")


# ---------------------------------------------------------------- time

def test_swedish_wall_clock_times_read_as_utc_by_the_eu_rule():
    tool = _tool()
    naive = dt.datetime
    assert tool.local_to_utc(naive(2026, 10, 17, 14, 5)) == [_t("2026-10-17 12:05:00")]
    assert tool.local_to_utc(naive(2026, 11, 6, 22, 5)) == [_t("2026-11-06 21:05:00")]
    # the hour the clocks go back on 25 October has two readings
    assert tool.local_to_utc(naive(2026, 10, 25, 2, 5)) == [_t("2026-10-25 00:05:00"),
                                                           _t("2026-10-25 01:05:00")]
    # the hour the clocks skip on 29 March has none
    assert tool.local_to_utc(naive(2026, 3, 29, 2, 30)) == []


def test_an_attempt_reads_the_last_candle_closed_before_it():
    tool = _tool()
    assert tool.candle_read_at(_t("2026-10-17 12:05:00")) == _t("2026-10-17 08:00:00")
    assert tool.candle_read_at(_t("2026-10-17 12:00:00")) == _t("2026-10-17 08:00:00")
    assert tool.candle_read_at(_t("2026-10-17 11:59:59")) == _t("2026-10-17 04:00:00")


def test_the_fold_hour_places_an_attempt_when_both_readings_agree():
    tool = _tool()
    a = {"local": dt.datetime(2026, 10, 25, 2, 5), "refused_close": None}
    # 00:05 and 01:05 UTC both read the candle that closed at 00:00 UTC
    assert tool.place(a)[0] == _t("2026-10-24 20:00:00")
    b = {"local": dt.datetime(2026, 3, 29, 2, 30), "refused_close": None}
    assert tool.place(b) == (None, None)


def test_the_task_minute_follows_the_clock_change():
    tool = _tool()
    assert tool.is_task_start(_t("2026-10-17 12:05:30"))       # 14:05 summer
    assert not tool.is_task_start(_t("2026-10-17 12:00:30"))   # 14:00, by hand
    assert tool.is_task_start(_t("2026-11-06 21:05:30"))       # 22:05 winter
    assert not tool.is_task_start(_t("2026-11-06 20:05:30"))   # 21:05 winter


# ---------------------------------------------------------------- records

def test_task_records_are_counted_and_the_rest_of_the_window_is_missed():
    recs = [_record("AEROUSDT", "2026-10-17 08:00:00", "LONG"),
            _record("ETHUSDT", "2026-10-17 08:00:00", "SHORT"),
            _record("AEROUSDT", "2026-10-17 12:00:00", "WAIT")]
    res = _count(recs)
    assert res["candles"] == 3
    assert res["records"] == 3
    assert res["records_per_pair"] == {"AEROUSDT": 2, "ETHUSDT": 1}
    assert res["missed_per_pair"] == {"AEROUSDT": 1, "ETHUSDT": 2}
    assert res["missed"] == 3
    assert (res["candles_read_by_all"], res["candles_read_by_some"],
            res["candles_read_by_none"]) == (1, 1, 1)


def test_a_run_that_is_not_the_tasks_is_not_counted_and_its_candle_is_missed():
    by_hand = _t("2026-10-17 13:29:00")    # 15:29 local, not minute 05
    recs = [_record("AEROUSDT", "2026-10-17 08:00:00", "LONG", logged=by_hand),
            _record("ETHUSDT", "2026-10-17 08:00:00", "WAIT")]
    res = _count(recs, last_open="2026-10-17 08:00:00")
    assert res["records"] == 1
    assert res["missed_per_pair"] == {"AEROUSDT": 1, "ETHUSDT": 0}
    assert res["missed_read_elsewhere"] == [("AEROUSDT", _t("2026-10-17 08:00:00"))]
    assert res["excluded"]["not the task's run"] == 1
    # with no task record in the window there is no version to match (READINGS, 4)
    alone = _count(recs[:1], last_open="2026-10-17 08:00:00")
    assert alone["records"] == 0 and alone["code_hash"] is None
    assert alone["missed_read_elsewhere"] == [("AEROUSDT", _t("2026-10-17 08:00:00"))]


def test_pinned_records_and_candles_outside_the_window_are_not_counted():
    recs = [_record("AEROUSDT", "2026-10-17 08:00:00", pinned=True),
            _record("AEROUSDT", "2026-10-17 04:00:00"),
            _record("AEROUSDT", "2026-10-17 20:00:00"),
            _record("ETHUSDT", "2026-10-17 12:00:00")]
    res = _count(recs)
    assert res["records"] == 1
    assert res["excluded"]["not live"] == 1
    assert res["excluded"]["before the window"] == 1
    assert res["excluded"]["after the window"] == 1


def test_two_versions_in_the_window_stop_the_count():
    recs = [_record("AEROUSDT", "2026-10-17 08:00:00"),
            _record("ETHUSDT", "2026-10-17 12:00:00", code_hash=OTHER)]
    with pytest.raises(SystemExit) as e:
        _count(recs)
    assert HASH in str(e.value) and OTHER in str(e.value)
    # given one version, it counts that one alone
    res = _count(recs, code_hash=OTHER)
    assert res["records"] == 1 and res["records_per_pair"]["ETHUSDT"] == 1


def test_a_hand_run_of_another_version_does_not_stop_the_count():
    recs = [_record("AEROUSDT", "2026-10-17 08:00:00"),
            _record("ETHUSDT", "2026-10-17 08:00:00", code_hash=OTHER,
                    logged=_t("2026-10-17 13:29:00"))]
    res = _count(recs)
    assert res["code_hash"] == HASH and res["records"] == 1


def test_a_record_with_no_degradation_verdict_stops_the_count():
    rec = _record("AEROUSDT", "2026-10-17 08:00:00")
    rec["decision"]["degradation"] = {}
    with pytest.raises(SystemExit) as e:
        _count([rec])
    assert "degradation verdict" in str(e.value)


def test_actions_are_grouped_by_side_and_counted_per_pair():
    recs = [_record("AEROUSDT", "2026-10-17 08:00:00", "AGGRESSIVE LONG"),
            _record("AEROUSDT", "2026-10-17 12:00:00", "CONSERVATIVE SHORT"),
            _record("AEROUSDT", "2026-10-17 16:00:00", "NO-TRADE (RISK TOO HIGH)"),
            _record("ETHUSDT", "2026-10-17 08:00:00", "WAIT"),
            _record("ETHUSDT", "2026-10-17 12:00:00", "SOMETHING NEW")]
    res = _count(recs)
    assert res["actions"] == {"LONG": 1, "SHORT": 1, "NO-TRADE": 1, "WAIT": 1, "other": 1}
    assert res["per_pair"]["AEROUSDT"] == {"LONG": 1, "SHORT": 1, "NO-TRADE": 1}
    assert res["per_pair"]["ETHUSDT"] == {"WAIT": 1, "other": 1}
    assert res["other_labels"] == ["SOMETHING NEW"]
    assert res["labels"]["AGGRESSIVE LONG"] == 1


def test_degraded_records_are_counted_with_the_rest_and_listed_apart():
    recs = [_record("AEROUSDT", "2026-10-17 08:00:00", "NO-TRADE (DEGRADED INPUT)",
                    degraded=True),
            _record("AEROUSDT", "2026-10-17 12:00:00", "LONG")]
    res = _count(recs)
    assert res["records"] == 2
    assert res["actions"] == {"NO-TRADE": 1, "LONG": 1}
    assert [(d["pair"], d["open"]) for d in res["degraded"]] == [
        ("AEROUSDT", _t("2026-10-17 08:00:00"))]


def test_longs_on_the_same_candle_and_candles_in_a_row():
    recs = [_record("AEROUSDT", "2026-10-17 08:00:00", "LONG"),
            _record("ETHUSDT", "2026-10-17 08:00:00", "CONSERVATIVE LONG"),
            _record("AEROUSDT", "2026-10-17 12:00:00", "AGGRESSIVE LONG"),
            _record("ETHUSDT", "2026-10-17 12:00:00", "SHORT"),
            _record("AEROUSDT", "2026-10-17 16:00:00", "WAIT"),
            _record("ETHUSDT", "2026-10-17 20:00:00", "LONG")]
    res = _count(recs, last_open="2026-10-17 20:00:00")
    assert res["longs"] == 4
    assert res["candles_with_long"] == 3
    assert res["long_streaks"] == [[(_t("2026-10-17 08:00:00"), 2), (_t("2026-10-17 12:00:00"), 1)],
                                   [(_t("2026-10-17 20:00:00"), 1)]]


def test_offsets_are_split_by_the_clock_of_the_close():
    recs = [_record("AEROUSDT", "2026-10-24 16:00:00", after=dt.timedelta(minutes=5, seconds=4)),
            _record("AEROUSDT", "2026-10-25 16:00:00", after=dt.timedelta(minutes=65, seconds=5))]
    res = _count(recs, first_open="2026-10-24 16:00:00", last_open="2026-10-25 16:00:00")
    assert res["records"] == 2
    assert res["offsets"]["summer"]["min"] == dt.timedelta(minutes=5, seconds=4)
    assert res["offsets"]["winter"]["max"] == dt.timedelta(minutes=65, seconds=5)


def test_slots_name_the_close_hour_and_its_clock():
    recs = [_record("AEROUSDT", "2026-10-24 20:00:00", after=dt.timedelta(minutes=5)),
            _record("ETHUSDT", "2026-10-24 20:00:00", after=dt.timedelta(minutes=5))]
    # the candles closing 00:00 UTC on 25 (summer, 02:00 local) and 26 October
    # (winter, 01:00 local); the first read by both pairs, the second by none
    res = _count(recs, first_open="2026-10-24 20:00:00", last_open="2026-10-25 20:00:00")
    s = res["slots"][0]
    assert s["candles"] == 2 and s["all"] == 1 and s["none"] == 1
    assert s["summer"] == [1, 1] and s["winter"] == [0, 1]


# ---------------------------------------------------------------- process log

def test_a_not_yet_final_refusal_is_a_refusal_and_its_candle_read_later_is_not_missed():
    recs = [_record(p, "2026-10-17 08:00:00") for p in PAIRS]
    lines = (_run_lines("2026-10-17 14:00:00", PAIRS, outcome="error", reason=NOT_FINAL)
             + ["2026-10-17 14:00:07,215 - ERROR - 2 of 2 pairs failed: AEROUSDT, ETHUSDT"]
             + _run_lines("2026-10-17 14:05:00", PAIRS))
    res = _count(recs, lines, last_open="2026-10-17 08:00:00")
    assert res["refused"] == 2 and res["failed"] == 0
    assert res["refused_then"] == {"read later": 2}
    assert res["missed"] == 0
    assert res["runs"] == 2 and res["runs_at_task_minute"] == 1
    assert res["runs_all_success"] == 1
    assert res["outcomes"] == {"refused": 2, "success": 2}


def test_a_refusal_whose_candle_no_run_read_leaves_it_missed():
    lines = _run_lines("2026-10-17 14:00:00", PAIRS, outcome="error", reason=NOT_FINAL)
    res = _count([], lines, last_open="2026-10-17 08:00:00")
    assert res["refused_then"] == {"missed": 2}
    assert res["missed"] == 2


def test_failures_are_counted_from_mains_line_only_never_from_error_lines():
    lines = _run_lines("2026-10-17 18:05:00", ["AEROUSDT"], outcome="error",
                       reason="Data fetch failed: connection reset")
    res = _count([], lines)
    # two ERROR lines for the pair, one failure
    assert sum(1 for x in lines if " - ERROR - " in x) == 2
    assert res["failed"] == 1 and res["failed_per_pair"] == {"AEROUSDT": 1}
    assert res["failures"][0][2] == _t("2026-10-17 12:00:00")
    assert res["refused"] == 0


def test_an_error_line_with_no_starting_line_is_still_counted():
    lines = ["2026-10-17 18:05:01,000 - ERROR - Engine returned error for ETHUSDT: boom"]
    res = _count([], lines)
    assert res["failed"] == 1 and res["attempts_no_start_line"] == 1


def test_runs_split_when_a_pair_repeats_or_two_minutes_pass():
    tool = _tool()
    lines = (_run_lines("2026-10-17 14:05:00", ["AEROUSDT", "ETHUSDT"])
             + _run_lines("2026-10-17 14:05:10", ["AEROUSDT"])
             + _run_lines("2026-10-17 14:09:00", ["ETHUSDT"]))
    logs = _Logs()
    try:
        d = logs.write([], lines)
        attempts = tool.read_process_log(os.path.join(d, "phase7_engine.log"))["attempts"]
    finally:
        logs.close()
    assert [r["pairs"] for r in tool.runs(attempts)] == [["AEROUSDT", "ETHUSDT"],
                                                         ["AEROUSDT"], ["ETHUSDT"]]


def test_attempts_on_candles_outside_the_window_are_not_counted():
    lines = (_run_lines("2026-10-17 10:05:00", ["AEROUSDT"])     # reads the 04:00 candle
             + _run_lines("2026-10-18 02:05:00", ["AEROUSDT"]))  # reads 20:00, after it
    res = _count([], lines)
    assert res["attempts"] == 0 and res["runs"] == 0


def test_a_missing_process_log_is_said_not_counted_as_nothing_failed():
    tool = _tool()
    res = tool.count({}, tool.read_process_log(None), _t("2026-10-17 08:00:00"))
    assert res["process_log_read"] is False
    assert "Process log: not found" in tool.report(res)


# ---------------------------------------------------------------- the command

def test_the_command_prints_the_report_writes_json_and_changes_no_log():
    tool = _tool()
    recs = [_record(p, "2026-10-17 08:00:00", "LONG") for p in tool.PAIRS]
    logs = _Logs()
    try:
        d = logs.write(recs, _run_lines("2026-10-17 14:05:00", tool.PAIRS))
        before = {n: open(os.path.join(d, n), "rb").read() for n in os.listdir(d)}
        out_json = os.path.join(tempfile.mkdtemp(prefix="phase7_count_json_"), "c.json")
        buf = io.StringIO()
        with redirect_stdout(buf):
            assert tool.main([d, "--last-open", "2026-10-17 08:00", "--json", out_json]) == 0
        after = {n: open(os.path.join(d, n), "rb").read() for n in os.listdir(d)}
        with open(out_json, encoding="utf-8") as f:
            data = json.load(f)
        shutil.rmtree(os.path.dirname(out_json), ignore_errors=True)
    finally:
        logs.close()
    text = buf.getvalue()
    assert before == after
    assert "Read: 10 records" in text and "Missed: 0 (0% of the window)" in text
    assert "LONGs on the same candle: 10 on 1 candles" in text
    assert data["records"] == 10 and data["actions"] == {"LONG": 10}


def test_the_command_refuses_a_window_edge_that_is_not_a_4h_open():
    tool = _tool()
    logs = _Logs()
    try:
        d = logs.write([])
        with redirect_stdout(io.StringIO()):
            try:
                import contextlib
                with contextlib.redirect_stderr(io.StringIO()):
                    tool.main([d, "--last-open", "2026-10-17 09:00"])
            except SystemExit as e:
                assert e.code == 2
            else:
                raise AssertionError("a window edge off the 4h grid was accepted")
    finally:
        logs.close()
