"""
docs/build/measure_draft_gaps.py -- the reading of 14 November's computations.

Written 2 November 2026 with the script, from DECISIONS, "Decision, 2 November
2026 -- how the reading of 14 November measures the redesign draft's gaps ...";
computation 7's two tests added 7 November 2026, from "Amendment, 7 November
2026 -- the reading of 14 November counts the CHOCHs against the side
(computation 7)".
Synthetic records only: every record and archive below is built here, in a
temporary folder, or is the golden decision of the pinned synthetic candles. No
test reads the live logs.

The expected values are worked by hand from the entry's formulas, not taken
from the script's output; the golden test's are the ones the redesign draft
(section 13.1) and the entry (computation 5) computed independently.

No fixtures: run_tests.py calls every test with no arguments.
"""

import copy
import datetime as dt
import importlib.util
import json
import os
import shutil
import sys
import tempfile

import numpy as np
import pandas as pd
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
TOOL_PATH = os.path.join(REPO, "docs", "build", "measure_draft_gaps.py")
UTC = dt.timezone.utc
HASH = "816d4951" + "0" * 56


def _tool():
    if REPO not in sys.path:
        sys.path.insert(0, REPO)
    spec = importlib.util.spec_from_file_location("phase7_measure_draft_gaps", TOOL_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _t(text):
    return dt.datetime.fromisoformat(text).replace(tzinfo=UTC)


def _frame(n=40, last_open="2026-10-20 08:00:00", seed=1):
    """A synthetic 4h frame, rising gently, ending at `last_open`."""
    rng = np.random.default_rng(seed)
    index = pd.date_range(end=pd.Timestamp(last_open), periods=n, freq="4h")
    close = 100.0 + np.cumsum(rng.normal(0.1, 1.0, n))
    open_ = close - rng.normal(0.0, 0.5, n)
    high = np.maximum(open_, close) + 0.5
    low = np.minimum(open_, close) - 0.5
    volume = rng.uniform(1000.0, 2000.0, n)
    return pd.DataFrame({"open": open_, "high": high, "low": low, "close": close,
                         "volume": volume}, index=index)


def _record(pair="AAAUSDT", opened="2026-10-20 08:00:00", logged=None, archive=None,
            frame=None, side="LONG", **over):
    """A live decision record with every field the script reads."""
    o = pd.Timestamp(opened)
    row = frame.loc[o] if frame is not None else {"open": 100.0, "close": 101.0, "volume": 1500.0,
                                                  "high": 101.5, "low": 99.5}
    if logged is None:
        logged = (_t(opened) + dt.timedelta(hours=4, minutes=5, seconds=20))
    ind = {"EMA20_Slope": 0.2, "EMA50_Slope": 0.1, "EMA_20": 100.5, "EMA_50": 100.0,
           "ATR": 2.0, "HVN": 101.0, "close": float(row["close"]), "open": float(row["open"]),
           "volume": float(row["volume"]), "high": float(row["high"]), "low": float(row["low"])}
    targets = [102.0, 104.0, 106.0] if side == "LONG" else [98.0, 96.0, 94.0]
    d = {
        "symbol": pair, "timeframe": "4h", "macro_bias": "NEUTRAL",
        "bias": {"raw": "BULLISH"}, "trend": {},
        "entry": {"long_signal": True, "long_signal_blockers": [],
                  "short_signal": True, "short_signal_blockers": [],
                  "entry_status": "ACTIVE ENTRY ZONE"},
        "risk": {"risk_valid": True, "risk_reason": "OK", "risk_regime": "NORMAL RISK",
                 "targets": targets},
        "exit": {"action": "LONG"},
        "degradation": {"degraded": False},
        "provenance": {"fetch": {"pinned": False}, "source": "mexc", "code_hash": HASH,
                       "decision_candles": {"struct": {"open_time": str(o)}},
                       "archive_path": archive},
        "lineage": {"indicators_at_decision_bar": ind},
    }
    for key, value in over.items():
        target = d
        parts = key.split("__")
        for p in parts[:-1]:
            target = target[p]
        target[parts[-1]] = value
    return {"logged_at": logged.isoformat(), "decision": d}


def _write_logs(folder, records):
    os.makedirs(folder, exist_ok=True)
    by_pair = {}
    for rec in records:
        by_pair.setdefault(rec["decision"]["symbol"], []).append(rec)
    for pair, recs in by_pair.items():
        with open(os.path.join(folder, f"phase7_decision_log_{pair.lower()}.jsonl"), "w",
                  encoding="utf-8") as f:
            for rec in recs:
                f.write(json.dumps(rec) + "\n")


def _archive(tmp, frame, name="aaausdt", run=None):
    from core import lineage
    return lineage.write_archive({"struct": frame}, tmp, name, "4h", run or name + "x" * 16)


# ---------------------------------------------------------------- the defaults

def test_the_defaults_are_the_entrys_population():
    tool = _tool()
    assert tool.FIRST_OPEN == dt.datetime(2026, 10, 17, 8, 0, tzinfo=UTC)
    assert tool.CODE_HASH == "816d4951"
    assert tool.PROFILE_BINS == 50 and tool.CANDLES_A_YEAR == 2190 and tool.PAIRS == 10


# ---------------------------------------------------------------- time

def test_swedish_time_follows_the_eu_rule_at_both_switches():
    tool = _tool()
    two, one = dt.timedelta(hours=2), dt.timedelta(hours=1)
    assert tool.stockholm_offset(_t("2026-10-25 00:59:59")) == two
    assert tool.stockholm_offset(_t("2026-10-25 01:00:00")) == one
    assert tool.stockholm_offset(_t("2026-03-29 00:59:59")) == one
    assert tool.stockholm_offset(_t("2026-03-29 01:00:00")) == two
    assert tool.stockholm_offset(_t("2026-12-31 12:00:00")) == one


def test_the_task_starts_five_minutes_after_a_close_then_sixty_five():
    tool = _tool()
    # 17 October, summer time: the 12:00 UTC close is 14:00 local, read at 14:05.
    assert tool.task_start(_t("2026-10-17 12:00:00")) == _t("2026-10-17 12:05:00")
    # 26 October, winter time: 12:00 UTC is 13:00 local; the next start is 14:05 local.
    assert tool.task_start(_t("2026-10-26 12:00:00")) == _t("2026-10-26 13:05:00")
    # The switch night: 00:00 UTC is 02:00 summer time; 04:00 UTC is 05:00 winter time.
    assert tool.task_start(_t("2026-10-25 00:00:00")) == _t("2026-10-25 00:05:00")
    assert tool.task_start(_t("2026-10-25 04:00:00")) == _t("2026-10-25 05:05:00")


# ---------------------------------------------------------------- the population

def test_only_the_tasks_live_records_in_the_window_are_counted():
    tool = _tool()
    o = "2026-10-20 08:00:00"
    close = _t(o) + dt.timedelta(hours=4)          # 12:00 UTC, 14:00 local; task at 12:05 UTC
    good = _record(opened=o, logged=close + dt.timedelta(minutes=5, seconds=30))
    records = [
        good,
        _record(opened=o, logged=close + dt.timedelta(seconds=40)),                   # a hand run
        _record(opened=o, logged=close + dt.timedelta(minutes=11)),                   # too late
        _record(opened=o, logged=close + dt.timedelta(minutes=6), provenance__fetch={"pinned": True}),
        _record(opened=o, logged=close + dt.timedelta(minutes=6), provenance__code_hash="f" * 64),
        _record(opened="2026-10-17 04:00:00"),                                        # before
        _record(opened=o, logged=close + dt.timedelta(minutes=7)),                    # a second
        _record(opened="2026-10-20 12:00:00", degradation={"degraded": True}),
        _record(opened="2026-10-20 16:00:00", degradation={}),
    ]
    tmp = tempfile.mkdtemp(prefix="phase7_gaps_")
    try:
        _write_logs(tmp, records)
        with open(os.path.join(tmp, "phase7_decision_log_aaausdt.jsonl"), "a") as f:
            f.write("{torn\n")
        pop = tool.select_population(tool.read_logs(tmp), HASH)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    assert [r["record"] for r in pop["n"]] == [good]
    assert len(pop["degraded"]) == 1
    ex = pop["excluded"]
    assert ex["not the task's run"] == 2
    assert ex["not live"] == 1 and ex["other code_hash"] == 1 and ex["before the window"] == 1
    assert ex["second task record of a candle"] == 1 and ex["unreadable line"] == 1
    assert ex["no degradation verdict"] == 1


def test_another_pairs_record_in_a_log_is_not_counted():
    tool = _tool()
    tmp = tempfile.mkdtemp(prefix="phase7_gaps_")
    try:
        rec = _record(pair="BBBUSDT")
        os.makedirs(tmp, exist_ok=True)
        with open(os.path.join(tmp, "phase7_decision_log_aaausdt.jsonl"), "w") as f:
            f.write(json.dumps(rec) + "\n")
        pop = tool.select_population(tool.read_logs(tmp), HASH)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    assert pop["n"] == [] and pop["excluded"]["another pair's record"] == 1


# ---------------------------------------------------------------- 1, 2, 3

def test_direction_is_ema50s_slope_and_the_ema_order():
    """
    Computation 1 as amended on 7 November: EMA50's slope and the EMAs' order.
    EMA20's slope is not read, so a pullback that turns EMA20 down keeps its
    side, and a missing or zero EMA20 slope changes nothing.
    """
    tool = _tool()
    f = tool.draft_direction
    assert f({"EMA20_Slope": 0.1, "EMA50_Slope": 0.1, "EMA_20": 2, "EMA_50": 1}) == "BULLISH"
    assert f({"EMA20_Slope": -0.1, "EMA50_Slope": -0.1, "EMA_20": 1, "EMA_50": 2}) == "BEARISH"
    assert f({"EMA20_Slope": -0.1, "EMA50_Slope": 0.1, "EMA_20": 2, "EMA_50": 1}) == "BULLISH"
    assert f({"EMA20_Slope": 0.1, "EMA50_Slope": -0.1, "EMA_20": 1, "EMA_50": 2}) == "BEARISH"
    assert f({"EMA20_Slope": 0.0, "EMA50_Slope": 0.1, "EMA_20": 2, "EMA_50": 1}) == "BULLISH"
    assert f({"EMA20_Slope": None, "EMA50_Slope": 0.1, "EMA_20": 2, "EMA_50": 1}) == "BULLISH"
    assert f({"EMA20_Slope": 0.1, "EMA50_Slope": 0.1, "EMA_20": 1, "EMA_50": 2}) == "NEUTRAL"
    assert f({"EMA20_Slope": 0.1, "EMA50_Slope": -0.1, "EMA_20": 2, "EMA_50": 1}) == "NEUTRAL"
    assert f({"EMA20_Slope": 0.1, "EMA50_Slope": 0.0, "EMA_20": 2, "EMA_50": 1}) == "NEUTRAL"
    assert f({"EMA20_Slope": 0.1, "EMA50_Slope": 0.1, "EMA_20": 2, "EMA_50": 2}) == "NEUTRAL"
    assert f({"EMA20_Slope": 0.1, "EMA50_Slope": None, "EMA_20": 2, "EMA_50": 1}) is None


def test_quality_is_eighty_for_distance_and_twenty_for_the_hvn():
    tool = _tool()
    # d = |110 - 100| / 10 = 1 -> D = 80 x 2/3; h = |110 - 105| / 10 = 0.5 -> H = 15.
    q, d, h = tool.quality({"close": 110.0, "ATR": 10.0, "EMA_20": 101.0, "EMA_50": 99.0, "HVN": 105.0})
    assert d == pytest.approx(1.0) and h == pytest.approx(0.5)
    assert q == pytest.approx(80.0 * 2.0 / 3.0 + 15.0)
    # Beyond 3 ATRs and 2 ATRs nothing is left.
    q, _, _ = tool.quality({"close": 140.0, "ATR": 10.0, "EMA_20": 100.0, "EMA_50": 100.0, "HVN": 100.0})
    assert q == 0.0
    assert tool.quality({"close": 110.0, "ATR": None, "EMA_20": 1.0, "EMA_50": 1.0, "HVN": 1.0}) is None
    assert tool.quality({"close": 110.0, "ATR": 0.0, "EMA_20": 1.0, "EMA_50": 1.0, "HVN": 1.0}) is None


def test_the_floor_is_the_largest_step_with_no_pair_over_five_percent_under():
    tool = _tool()
    a = np.arange(1, 101, dtype=float)          # under 5: 4% ; under 10: 9%
    b = np.full(100, 1e6)
    assert tool.propose_floor({"A": a, "B": b}) == 5
    assert tool.propose_floor({"B": b}) == 1000000
    assert tool.propose_floor({"A": np.full(10, 0.5)}) is None
    assert list(tool.floor_series(100)) == [1, 2, 5, 10, 20, 50, 100]


def test_the_turnover_and_its_bounds():
    tool = _tool()
    assert tool.turnover({"volume": 10.0, "close": 2.0, "low": 1.5, "high": 3.0}) == (20.0, 15.0, 30.0)
    assert tool.turnover({"volume": None, "close": 2.0, "low": 1.5, "high": 3.0}) is None


# ---------------------------------------------------------------- 4, 5

def _trigger_frame(close, open_, prev_close, volume, before):
    """22 candles: one, the twenty `before` (the last of them closing at
    `prev_close`), and the decision candle."""
    index = pd.date_range(end=pd.Timestamp("2026-10-20 08:00"), periods=22, freq="4h")
    df = pd.DataFrame({"open": 1.0, "high": 2.0, "low": 0.5, "close": 1.0,
                       "volume": [0.0] + list(before) + [volume]}, index=index)
    df.iloc[-2, df.columns.get_loc("close")] = prev_close
    df.iloc[-1, df.columns.get_loc("close")] = close
    df.iloc[-1, df.columns.get_loc("open")] = open_
    return df


def test_the_trigger_closes_beyond_its_open_and_the_previous_close():
    tool = _tool()
    before = list(range(1, 21))                  # the twenty before: median 10.5
    df = _trigger_frame(close=1.2, open_=1.1, prev_close=1.15, volume=11.0, before=before)
    assert tool.trigger(df, len(df) - 1, "LONG") == (True, True)
    assert tool.trigger(df, len(df) - 1, "SHORT")[0] is False
    df = _trigger_frame(close=1.2, open_=1.1, prev_close=1.25, volume=11.0, before=before)
    assert tool.trigger(df, len(df) - 1, "LONG")[0] is False
    df = _trigger_frame(close=1.0, open_=1.1, prev_close=1.05, volume=11.0, before=before)
    assert tool.trigger(df, len(df) - 1, "SHORT")[0] is True


def test_the_triggers_volume_must_be_strictly_above_the_median():
    tool = _tool()
    df = _trigger_frame(close=1.2, open_=1.1, prev_close=1.15, volume=5.0, before=[5.0] * 20)
    assert tool.trigger(df, len(df) - 1, "LONG")[1] is False
    df.iloc[-1, df.columns.get_loc("volume")] = 5.0000001
    assert tool.trigger(df, len(df) - 1, "LONG")[1] is True


def test_h5_reads_the_profiles_hvn_and_the_bin_width_in_atrs():
    tool = _tool()
    from indicators.volume_profile import compute_volume_profile
    frame = _frame()
    _, hvn, _ = compute_volume_profile(frame, num_bins=50)
    width = (frame["high"].max() - frame["low"].min()) / 50
    ratio, ok = tool.h5_reach(frame, {"ATR": 2.0, "HVN": hvn})
    assert ok and ratio == pytest.approx(width / 2.0)
    _, ok = tool.h5_reach(frame, {"ATR": 2.0, "HVN": hvn * (1 + 1e-8)})
    assert not ok


def test_the_archive_must_hold_the_records_candle_and_twenty_one_before():
    tool = _tool()
    tmp = tempfile.mkdtemp(prefix="phase7_gaps_")
    try:
        frame = _frame()
        path = _archive(tmp, frame)
        rec = _record(archive=path, frame=frame)
        row = {"open": _t("2026-10-20 08:00:00"), "decision": rec["decision"]}
        got, why = tool.check_archive(row, tmp, {})
        assert why is None and got[1] == len(frame) - 1

        bad = copy.deepcopy(rec)
        bad["decision"]["lineage"]["indicators_at_decision_bar"]["close"] += 1e-9
        assert tool.check_archive({"open": row["open"], "decision": bad["decision"]}, tmp, {})[1] \
            == "the archive's close is not the record's"

        gap = frame.drop(frame.index[-5])
        path2 = _archive(tmp, gap, name="bbbusdt")
        rec2 = _record(archive=path2, frame=frame)
        assert tool.check_archive({"open": row["open"], "decision": rec2["decision"]}, tmp, {})[1] \
            == "the 21 candles before are not at 4h steps"

        short = frame.iloc[-21:]
        path3 = _archive(tmp, short, name="cccusdt")
        rec3 = _record(archive=path3, frame=frame)
        assert tool.check_archive({"open": row["open"], "decision": rec3["decision"]}, tmp, {})[1] \
            == "fewer than 21 candles before the decision candle"

        rec4 = _record(archive="nowhere/x.json.gz", frame=frame)
        assert tool.check_archive({"open": row["open"], "decision": rec4["decision"]}, tmp, {})[1] \
            == "archive missing or unreadable"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------- 6

def _gates(tool, side="LONG", q=(75.0, 0.0, 0.0), t=(100.0, 90.0, 110.0), floor=50.0,
           trig=(True, True), **over):
    d = _record(side=side, **over)["decision"]
    return tool.ladder(d, side, q, t, floor, trig)[1]


def test_the_ladder_labels_the_first_gate_that_fails():
    tool = _tool()
    inside = {"lineage__indicators_at_decision_bar__close": 100.2}
    # Q 75 and the close (101) outside the band 100 .. 100.5: the plain tier.
    assert _gates(tool) == "LONG"
    assert _gates(tool, **inside) == "AGGRESSIVE LONG"
    assert _gates(tool, risk__risk_regime="HIGH RISK", **inside) == "LONG"
    assert _gates(tool, q=(60.0, 0, 0)) == "CONSERVATIVE LONG"
    assert _gates(tool, q=(49.9, 0, 0)) == "WAIT"
    assert _gates(tool, trig=(False, True)) == "WAIT"
    assert _gates(tool, trig=(True, False)) == "WAIT"
    assert _gates(tool, floor=100.5) == "NO-TRADE (THIN MARKET)"
    assert _gates(tool, macro_bias="BEARISH") == "NO-TRADE (MACRO AGAINST)"
    assert _gates(tool, side="SHORT", macro_bias="BEARISH") == "SHORT"
    assert _gates(tool, entry__long_signal=False,
                  entry__long_signal_blockers=["ADX is under 20"]) == "NO-TRADE (SIGNAL UNCONFIRMED)"
    assert _gates(tool, risk__risk_valid=False) == "NO-TRADE (RISK TOO HIGH)"
    assert _gates(tool, risk={"risk_regime": "NORMAL RISK",
                              "targets": [102.0, 104.0, 106.0]}) == "NO-TRADE (RISK NOT ASSESSED)"
    assert _gates(tool, bias="BULLISH") == "WAIT"                      # gate 0
    d = _record()["decision"]
    assert tool.ladder(d, None, None, (100.0, 90.0, 110.0), 50.0, None)[1] == "WAIT"


def test_a_plan_on_the_other_side_is_counted_apart():
    tool = _tool()
    d = _record(side="SHORT")["decision"]
    assert tool.ladder(d, "LONG", (75.0, 0, 0), (100.0, 0, 0), 50.0, (True, True))[1] == "APART"


def test_a_gate_not_measured_before_a_failure_leaves_no_action():
    tool = _tool()
    assert _gates(tool, trig=None) is None
    assert _gates(tool, floor=None) is None
    assert _gates(tool, q=None, trig=(False, True)) == "WAIT"
    # A failure before the gate that is not measured decides the action.
    assert _gates(tool, trig=None, macro_bias="BEARISH") == "NO-TRADE (MACRO AGAINST)"


def test_an_entry_is_a_trade_whose_previous_record_is_not_the_same_side():
    tool = _tool()
    seq = ["LONG", "AGGRESSIVE LONG", "WAIT", "CONSERVATIVE LONG", "SHORT", None,
           "AGGRESSIVE SHORT", "NO-TRADE (SIGNAL UNCONFIRMED)", "SHORT"]
    rows = [{"pair": "A", "draft": a} for a in seq] + [{"pair": "B", "draft": "LONG"}]
    assert tool.entries(rows, "draft") == {"A": (5, 1), "B": (1, 0)}


# ---------------------------------------------------------------- 7. the CHOCH count

def test_a_choch_against_is_the_whole_sequence_opposite_the_side():
    """
    READINGS 12: the two strings entry_model.py's structure multiplier compares,
    whole; "UNKNOWN", a missing or non-string sequence, or no side, is not
    measured. The golden record's own sequence (BOS BULLISH) reads as a
    sequence that is no CHOCH, on either side -- so the field's path is a real
    record's.
    """
    tool = _tool()
    bear = "CHOCH BEARISH (POSSIBLE REVERSAL)"
    bull = "CHOCH BULLISH (POSSIBLE REVERSAL)"

    def against(seq, side):
        return tool.choch_against({"structure": {"sequence": seq}}, side)

    assert against(bear, "LONG") is True and against(bull, "SHORT") is True
    assert against(bull, "LONG") is False and against(bear, "SHORT") is False
    for seq in ("BOS BULLISH (TREND CONTINUATION)", "BOS BEARISH (TREND CONTINUATION)",
                "BULLISH SWING SEQUENCE (HH-HL)", "BEARISH SWING SEQUENCE (LH-LL)", "NONE",
                "CHOCH BEARISH"):
        assert against(seq, "LONG") is False and against(seq, "SHORT") is False
    assert against("UNKNOWN", "LONG") is None and against(None, "LONG") is None
    assert against(5, "SHORT") is None and against(bear, None) is None
    assert tool.choch_against({}, "LONG") is None
    assert tool.choch_against({"structure": "CHOCH BEARISH"}, "LONG") is None
    with open(os.path.join(HERE, "fixtures", "golden_decision.json"), encoding="utf-8") as f:
        golden = json.load(f)
    assert golden["structure"]["sequence"] == "BOS BULLISH (TREND CONTINUATION)"
    assert tool.choch_against(golden, "LONG") is False
    assert tool.choch_against(golden, "SHORT") is False


def test_the_choch_count_gates_nothing_and_counts_who_passes():
    """
    Six task records on one pair, every one BULLISH but the fifth:
      1 CHOCH BEARISH, passes every gate        -> counted, and passing
      2 CHOCH BEARISH, macro BEARISH            -> counted, fails gate 6
      3 BOS BULLISH                             -> a sequence, no CHOCH
      4 no structure at all                     -> not measured
      5 CHOCH BEARISH, NEUTRAL (no side)        -> not among the sided
      6 UNKNOWN                                 -> not measured
    So: 5 with a side, 2 not measured, CHOCH against 2 of 3, of those 1 passing
    and 1 failing another gate; 1 CHOCH of the 2 records with a sequence that
    pass every gate (1 and 3; 4 and 6 pass too, but their sequence is not
    measured). The CHOCH is no gate: the draft's actions are what they would be
    without it.
    """
    tool = _tool()
    tmp = tempfile.mkdtemp(prefix="phase7_gaps_")
    bear = {"sequence": "CHOCH BEARISH (POSSIBLE REVERSAL)"}
    plan = [dict(structure=bear), dict(structure=bear, macro_bias="BEARISH"),
            dict(structure={"sequence": "BOS BULLISH (TREND CONTINUATION)"}), dict(),
            dict(structure=bear), dict(structure={"sequence": "UNKNOWN"})]
    try:
        frame = _rising_tail(_frame(n=40, last_open="2026-10-20 20:00:00"), k=6)
        records = []
        for i, pos in enumerate(range(len(frame) - 6, len(frame))):
            path = _archive(tmp, frame.iloc[:pos + 1], run=f"run{i}" + "x" * 12)
            c = float(frame["close"].iloc[pos])
            rec = _record(opened=str(frame.index[pos]), archive=path, frame=frame, **plan[i])
            rec["decision"]["lineage"]["indicators_at_decision_bar"].update(
                {"EMA_20": c + 0.001, "EMA_50": c - 0.001, "HVN": c, "ATR": 1.0,
                 "EMA50_Slope": -0.1 if i == 4 else 0.1})
            records.append(rec)
        logs = os.path.join(tmp, "logs")
        _write_logs(logs, records)
        pop = tool.select_population(tool.read_logs(logs), HASH, first_open=_t("2026-10-17 08:00:00"))
        res = tool.measure(pop, tmp, floor=1.0)
        text = tool.report(pop, res)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    seven = res["7 CHOCH"]
    assert res["N"] == 6
    assert seven["records with a side"] == 5
    assert seven["not measured (no sequence)"] == 2
    assert seven["sequences"] == {"BOS BULLISH (TREND CONTINUATION)": 1,
                                  "CHOCH BEARISH (POSSIBLE REVERSAL)": 2, "None": 1, "UNKNOWN": 1}
    assert seven["CHOCH against the side"]["pooled"] == (2, 3)
    assert seven["CHOCH against the side"]["per pair"] == {"AAAUSDT": (2, 3)}
    assert seven["of those, passing every other gate"]["pooled"] == (1, 2)
    assert seven["of those, failing another gate"] == 1
    assert seven["of those, none failing and one not measured"] == 0
    assert seven["of those, apart (the plan's side not the draft's)"] == 0
    assert seven["CHOCH against, of the records passing every gate"]["pooled"] == (1, 2)
    assert seven["their draft actions"] == {"AGGRESSIVE LONG": 1}
    assert seven["against"] is None
    assert [r["draft"] for r in pop["n"]] == ["AGGRESSIVE LONG", "NO-TRADE (MACRO AGAINST)",
                                              "AGGRESSIVE LONG", "AGGRESSIVE LONG", "WAIT",
                                              "AGGRESSIVE LONG"]
    assert "== 7 CHOCH" in text and "CHOCH count reported, not judged" in text


# ---------------------------------------------------------------- end to end

def _rising_tail(frame, k=4):
    frame = frame.copy()
    for pos in range(len(frame) - k, len(frame)):
        prev = float(frame["close"].iloc[pos - 1])
        frame.iloc[pos, frame.columns.get_loc("open")] = prev + 0.1
        frame.iloc[pos, frame.columns.get_loc("close")] = prev + 1.0
        frame.iloc[pos, frame.columns.get_loc("high")] = prev + 1.5
        frame.iloc[pos, frame.columns.get_loc("low")] = prev - 0.4
        frame.iloc[pos, frame.columns.get_loc("volume")] = 1e6
    return frame


def test_the_whole_reading_on_four_synthetic_candles():
    """
    Four task records on one pair: Q 100 inside the band, twice; then NEUTRAL
    (EMA50's slope turned down; EMA20's is not read);
    then Q 100 again. Draft: AGGRESSIVE LONG, AGGRESSIVE LONG, WAIT, AGGRESSIVE
    LONG -- two entries in four measured records, so 2 / 4 x 2,190 x 10 =
    10,950 a year. Today: LONG four times, one entry.
    """
    tool = _tool()
    tmp = tempfile.mkdtemp(prefix="phase7_gaps_")
    try:
        frame = _rising_tail(_frame(n=40, last_open="2026-10-20 20:00:00"))
        records = []
        for i, pos in enumerate(range(len(frame) - 4, len(frame))):
            opened = str(frame.index[pos])
            path = _archive(tmp, frame.iloc[:pos + 1], run=f"run{i}" + "x" * 12)
            c = float(frame["close"].iloc[pos])
            neutral = i == 2
            rec = _record(opened=opened, archive=path, frame=frame)
            rec["decision"]["lineage"]["indicators_at_decision_bar"].update(
                {"EMA_20": c + 0.001, "EMA_50": c - 0.001, "HVN": c, "ATR": 1.0,
                 "EMA50_Slope": -0.1 if neutral else 0.1})
            records.append(rec)
        logs = os.path.join(tmp, "logs")
        _write_logs(logs, records)
        out = os.path.join(tmp, "reading.json")
        assert tool.main([logs, "--root", tmp, "--code-hash", "816d4951", "--floor", "1",
                          "--first-open", "2026-10-17T08:00:00+00:00", "--json", out]) == 0
        with open(out, encoding="utf-8") as f:
            res = json.load(f)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    six = res["6 ladder"]
    assert res["N"] == 4 and res["code_hash"] == HASH
    assert six["draft actions"] == {"AGGRESSIVE LONG": 3, "WAIT": 1}
    assert six["per pair"]["AAAUSDT"]["draft's entries"] == 2
    assert six["per pair"]["AAAUSDT"]["today's entries"] == 1
    assert six["entries a year, projected"] == pytest.approx(10950.0)
    assert six["against"] is False
    assert six["blocks alone"]["2"] == 1
    assert res["1 direction"]["NEUTRAL where today trades"]["pooled"] == [1, 4]
    assert res["2 tiers"]["on the records with a side"]["counts"]["70 and over"] == 3
    assert res["4 trigger"]["trigger passes"]["pooled"] == [3, 3]


def test_the_script_refuses_an_empty_folder_and_an_ambiguous_hash():
    tool = _tool()
    tmp = tempfile.mkdtemp(prefix="phase7_gaps_")
    try:
        with pytest.raises(SystemExit):
            tool.main([tmp])
        _write_logs(tmp, [_record(), _record(opened="2026-10-20 12:00:00",
                                             provenance__code_hash="816d4951" + "1" * 56)])
        with pytest.raises(SystemExit):
            tool.main([tmp])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------- the golden record

def test_the_golden_decision_gives_the_drafts_own_numbers():
    """
    The engine's record of the pinned synthetic candles, made to read as a task
    record, against its archive rebuilt from the same candles. The redesign
    draft (13.1) and the entry (computation 5) computed these apart from this
    script: BULLISH; the trigger and its volume both fail; d 3.2070, h 15.1202,
    quality 0; the profile gives the record's HVN; w / ATR 0.598. So WAIT, at
    gate 8.

    The fixture is the golden SNAPSHOT, every float rounded to 8 decimals
    (test_golden_path.py), so its HVN is the profile's rounded: checked, and
    the unrounded value put back, as the engine's own record holds it.
    """
    from indicators.volume_profile import compute_volume_profile
    tool = _tool()
    sys.path.insert(0, HERE)
    from test_golden_path import SYMBOL, TIMEFRAME, _write_pinned_set
    from data.data_fetcher import DataFetcher, data_fetcher
    from core import lineage

    with open(os.path.join(HERE, "fixtures", "golden_decision.json"), encoding="utf-8") as f:
        golden = json.load(f)
    tmp = tempfile.mkdtemp(prefix="phase7_gaps_")
    original_url = data_fetcher.base_url
    try:
        pinned = os.path.join(tmp, "pinned")
        os.makedirs(pinned)
        _write_pinned_set(pinned)
        data_fetcher.base_url = "http://127.0.0.1:1"      # nothing reaches the network
        DataFetcher.set_pinned_source(pinned)
        try:
            frame = data_fetcher.get_tf(SYMBOL, TIMEFRAME, limit=450)
        finally:
            DataFetcher.clear_pinned_source()
            data_fetcher.base_url = original_url
        assert lineage.frame_hash(frame) == golden["provenance"]["input_hashes"]["struct"]

        d = copy.deepcopy(golden)
        d["provenance"]["fetch"]["pinned"] = False
        d["provenance"]["source"] = "mexc"
        d["provenance"]["code_hash"] = HASH
        d["provenance"]["archive_path"] = _archive(tmp, frame, name="testusdt")
        _, hvn, _ = compute_volume_profile(frame, num_bins=50)
        assert round(hvn, 8) == golden["lineage"]["indicators_at_decision_bar"]["HVN"]
        d["lineage"]["indicators_at_decision_bar"]["HVN"] = hvn
        close = _t(d["provenance"]["decision_candles"]["struct"]["close_time"])
        logged = tool.task_start(close) + dt.timedelta(seconds=30)
        logs = os.path.join(tmp, "logs")
        _write_logs(logs, [{"logged_at": logged.isoformat(), "decision": d}])

        pop = tool.select_population(tool.read_logs(logs), HASH, first_open=_t("2025-01-01 00:00:00"))
        assert len(pop["n"]) == 1
        res = tool.measure(pop, tmp)
        r = pop["n"][0]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    assert r["archive problem"] is None
    assert r["draft dir"] == "BULLISH" and r["today"] == "CONSERVATIVE LONG"
    assert r["trig"] == (False, False)
    q, dd, h = r["q"]
    assert dd == pytest.approx(3.2070, abs=5e-5) and h == pytest.approx(15.1202, abs=5e-5) and q == 0.0
    ratio, ok = tool.h5_reach(r["archive"][0], r["decision"]["lineage"]["indicators_at_decision_bar"])
    assert ok and ratio == pytest.approx(0.598, abs=5e-4)
    assert r["draft"] == "WAIT"
    assert [g for g in (0, 1, 2, "3-5", 6, 7, 8, 9) if r["gates"][g] is False] == [8, 9]
    assert res["5 H5"]["not measured"] == 0
