"""
docs/build/indicator_overlap.py -- the overlap and decision-impact tool.

Written 24 October 2026 with the tool. The tool measures how much the engine's
indicators agree, and how many of the engine's actions change when a factor is
removed. A tool like that is only worth its numbers if three things hold, and
these tests hold them:

  - its statistics are right (kappa against hand-worked cases),
  - its baseline IS the engine (the golden decision, reproduced), and
  - it reads no candle after the bar it judges (every later candle changed,
    the bar's row unchanged).

And it must leave the engine as it found it: the bias weights it changes for a
variant are restored, also when the variant fails.

Fixture-free, per run_tests.py. The two tests that run the engine skip without
pandas_ta; the rest need neither pandas_ta nor any file outside the repository.
"""

import importlib.util
import math
import os
import shutil
import sys
import tempfile

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOL_PATH = os.path.join(REPO, "docs", "build", "indicator_overlap.py")


def _tool():
    spec = importlib.util.spec_from_file_location("phase7_indicator_overlap", TOOL_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# --- the statistics ---------------------------------------------------------

def test_kappa_of_identical_series_is_one():
    observed, chance, k = _tool().kappa([1, -1, 1, 1, -1, 0], [1, -1, 1, 1, -1, 0])
    assert observed == 1.0 and k == 1.0


def test_kappa_of_independent_series_is_zero_though_they_agree_68_percent():
    """
    The base-rate point the review of 24 October made: two signals that are each
    up 80% of the time, independently, agree 0.8^2 + 0.2^2 = 68% of the time by
    chance alone. Built exactly: 64 up/up, 16 up/down, 16 down/up, 4 down/down.
    """
    a = [1] * 64 + [1] * 16 + [-1] * 16 + [-1] * 4
    b = [1] * 64 + [-1] * 16 + [1] * 16 + [-1] * 4
    observed, chance, k = _tool().kappa(a, b)
    assert observed == pytest.approx(0.68)
    assert chance == pytest.approx(0.68)
    assert k == pytest.approx(0.0, abs=1e-12)


def test_kappa_counts_flat_as_a_state_of_its_own():
    """A flat reading is not "no opinion" to be dropped: flat against up is a
    disagreement. Hand-worked: observed 3/4, chance (2/4 * 1/4) + (1/4 * 2/4) +
    (1/4 * 1/4) = 5/16, kappa (12/16 - 5/16) / (11/16) = 7/11."""
    observed, chance, k = _tool().kappa([1, 1, 0, -1], [1, 0, 0, -1])
    assert observed == pytest.approx(0.75)
    assert chance == pytest.approx(5 / 16)
    assert k == pytest.approx(7 / 11)


def test_kappa_drops_pairs_with_a_missing_reading():
    observed, _, k = _tool().kappa([1, -1, float("nan")], [1, -1, 1])
    assert observed == 1.0 and k == 1.0


# --- the variants leave the engine as they found it ---------------------------

def test_each_variant_names_weights_the_bias_engine_has():
    tool = _tool()
    import models.bias_engine as be
    for name, (zero, set_to, entry_mode) in tool.VARIANTS.items():
        for weight in list(zero) + list(set_to):
            assert hasattr(be, weight), (name, weight)
        assert entry_mode in ("as is", "no trend multiplier", "no macro multiplier", "one distance"), name
    assert tool.VARIANTS["baseline"] == ((), {}, "as is")


def test_the_weights_are_restored_after_a_variant_and_after_a_failure():
    tool = _tool()
    before = tool.current_weights()
    with tool.bias_weights(tool.FOUR, {"WEIGHT_TREND_HEALTH": 0.75}):
        inside = tool.current_weights()
    assert inside["WEIGHT_TREND_HEALTH"] == 0.75
    assert all(inside[w] == 0.0 for w in tool.FOUR)
    assert tool.current_weights() == before

    with pytest.raises(RuntimeError):
        with tool.bias_weights(("WEIGHT_MACRO_BIAS",)):
            raise RuntimeError("a variant that fails part-way")
    assert tool.current_weights() == before


# --- counting changes ---------------------------------------------------------

def _rows(baseline_and_variant):
    tool = _tool()
    rows = []
    for base, other in baseline_and_variant:
        row = {f"action | {name}": base for name in tool.VARIANTS}
        row["action | no SuperTrend"] = other
        rows.append(row)
    return rows


def test_impact_counts_changes_trades_and_flips():
    tool = _tool()
    result = tool.impact(_rows([
        ("CONSERVATIVE LONG", "CONSERVATIVE LONG"),     # unchanged
        ("CONSERVATIVE LONG", "WAIT"),                  # trade to none
        ("WAIT", "LONG"),                               # none to trade
        ("LONG", "AGGRESSIVE LONG"),                    # tier only
        ("LONG", "SHORT"),                              # side flipped
        ("WAIT", "NO-TRADE (SIGNAL UNCONFIRMED)"),      # label only
    ]))["no SuperTrend"]
    assert result == {"changed": 5, "trades": 4, "flipped": 1,
                      "trade to none": 1, "none to trade": 1}


def test_a_no_trade_label_naming_a_side_is_not_a_trade():
    tool = _tool()
    assert tool.side("NO-TRADE (SIGNAL UNCONFIRMED)") is None
    assert tool.side("NO-TRADE (PLAN CONTRADICTS ACTION)") is None
    assert tool.side("WAIT") is None
    assert tool.side("CONSERVATIVE SHORT") == "SHORT"
    assert tool.side("AGGRESSIVE LONG") == "LONG"


def test_the_log_comparison_reads_only_live_undegraded_records_at_this_code():
    tool = _tool()
    rows = [{"pair": "ETHUSDT", "bar": "2026-10-17 04:00:00", "action | baseline": "WAIT"},
            {"pair": "SOLUSDT", "bar": "2026-10-17 04:00:00", "action | baseline": "LONG"}]

    def record(symbol, action, code="abc", degraded=False, pinned=False, bar="2026-10-17 04:00:00"):
        return {"decision": {"symbol": symbol, "exit": {"action": action},
                             "degradation": {"degraded": degraded},
                             "provenance": {"code_hash": code, "last_candle": bar,
                                            "fetch": {"pinned": pinned}}}}

    records = [record("ETHUSDT", "WAIT"),                         # compared, same
               record("SOLUSDT", "SHORT"),                        # compared, different
               record("ETHUSDT", "LONG", code="other"),           # another version
               record("ETHUSDT", "LONG", degraded=True),          # degraded
               record("ETHUSDT", "LONG", pinned=True),            # a pinned run
               record("ETHUSDT", "LONG", bar="2026-10-18 04:00:00")]  # no row for it
    compared, matched, mismatches = tool.compare_with_logs(rows, records, "abc")
    assert (compared, matched) == (2, 1)
    assert mismatches == [(("SOLUSDT", "2026-10-17 04:00:00"), "LONG", "SHORT")]


def test_the_tool_refuses_a_timeframe_other_than_4h():
    tool = _tool()
    original = tool.config.TIMEFRAME
    try:
        tool.config.TIMEFRAME = "1h"
        with pytest.raises(SystemExit) as stopped:
            tool.main([tempfile.gettempdir()])
        assert "4h only" in str(stopped.value)
    finally:
        tool.config.TIMEFRAME = original


# --- macro: the daily candles closed when the bar closed --------------------------

def test_macro_reads_the_daily_candle_that_closes_with_the_bar():
    """
    The engine decides a bar after it closes, so the daily candle that closes at
    the same moment as a 20:00 bar is already closed and is read. The candle
    still forming at a 16:00 bar's close is not. Built so that the last daily
    candle alone flips macro from BEARISH to BULLISH.
    """
    import pandas as pd
    tool = _tool()
    days = pd.date_range("2026-08-01", periods=60, freq="D")
    daily = pd.DataFrame({"close": [1.0] * 59 + [3.0], "EMA_50": [2.0] * 60}, index=days)
    last_day = days[-1]

    assert tool.macro_at(daily, last_day + pd.Timedelta(hours=20)) == "BULLISH"
    assert tool.macro_at(daily, last_day + pd.Timedelta(hours=16)) == "BEARISH"
    # Fewer than 50 closed daily candles: no reading at all.
    assert tool.macro_at(daily.iloc[:49], days[48] + pd.Timedelta(hours=20)) is None


# --- the baseline is the engine, and it reads no later candle -------------------

def _golden_frames():
    """The golden test's pinned set: the 4h frame and the daily frame the router
    reads, through the engine's own pinned loader."""
    pytest.importorskip("pandas_ta")
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from test_golden_path import SYMBOL, TIMEFRAME, MACRO_TIMEFRAME, _write_pinned_set
    from data.data_fetcher import DataFetcher, data_fetcher

    tmp = tempfile.mkdtemp(prefix="phase7_overlap_tool_")
    original_url = data_fetcher.base_url
    try:
        _write_pinned_set(tmp)
        data_fetcher.base_url = "http://127.0.0.1:1"      # nothing reaches the network
        DataFetcher.set_pinned_source(tmp)
        frame = data_fetcher.get_tf(SYMBOL, TIMEFRAME, limit=450)
        daily = data_fetcher.get_tf(SYMBOL, MACRO_TIMEFRAME, limit=100)
    finally:
        DataFetcher.clear_pinned_source()
        data_fetcher.base_url = original_url
        shutil.rmtree(tmp, ignore_errors=True)
    assert frame.attrs.get("fetch_error") is None and daily.attrs.get("fetch_error") is None
    return frame, daily


def test_the_baseline_reproduces_the_golden_decision():
    """
    On the golden run's own candles, the tool's baseline for the last bar must be
    the decision the router made: its action, its bias score and its macro.
    """
    pytest.importorskip("pandas_ta")
    import json
    tool = _tool()
    from indicators.indicators import add_technical_indicators
    golden_path = os.path.join(REPO, "tests", "fixtures", "golden_decision.json")
    with open(golden_path, encoding="utf-8") as f:
        golden = json.load(f)
    assert golden["degradation"]["degraded"] is False, "the tool does not model degradation"

    frame, daily = _golden_frames()
    frame_ind, _ = add_technical_indicators(frame)
    daily_ind, _ = add_technical_indicators(daily)
    row = tool.bar_row(frame_ind, daily_ind, len(frame_ind) - 1)

    assert row["bar"] == golden["provenance"]["last_candle"]
    assert row["macro"] == golden["macro_bias"]
    assert row["bias score | baseline"] == pytest.approx(golden["bias"]["score"], abs=1e-6)
    assert row["action | baseline"] == golden["exit"]["action"]


def test_no_candle_after_the_bar_is_read():
    """
    Every 4h candle after the judged bar, and every daily candle that closed
    after it, is changed beyond recognition. The bar's row must not move.
    """
    pytest.importorskip("pandas_ta")
    tool = _tool()
    from indicators.indicators import add_technical_indicators
    frame, daily = _golden_frames()
    t = len(frame) - 40
    bar_close = frame.index[t] + tool.BAR

    changed = frame.copy()
    later = changed.index > frame.index[t]
    for col in ("open", "high", "low", "close"):
        changed.loc[later, col] = changed.loc[later, col] * 3.0
    changed.loc[later, "volume"] = changed.loc[later, "volume"] * 10.0
    changed_daily = daily.copy()
    later_daily = changed_daily.index + tool.DAY > bar_close
    assert later.sum() == 39 and later_daily.any(), "the change must reach later candles"
    for col in ("open", "high", "low", "close"):
        changed_daily.loc[later_daily, col] = changed_daily.loc[later_daily, col] * 3.0

    def row_at(f, d, i):
        return tool.bar_row(add_technical_indicators(f)[0], add_technical_indicators(d)[0], i)

    original, after_change = row_at(frame, daily, t), row_at(changed, changed_daily, t)
    assert original is not None
    assert original == after_change

    # Control: the same change is seen by a bar after it, so it is a change the
    # tool can see at all.
    assert row_at(frame, daily, t + 10) != row_at(changed, changed_daily, t + 10)
