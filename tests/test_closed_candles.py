"""
Finding 16 -- decisions are made on closed candles.

Ruled by Viktor, 26 September 2026 (docs/PHASE7_DECISIONS.md, "Ruling, 26
September 2026 -- decisions are made on closed candles (finding 16)"):

  1. Decisions are made on closed candles only, on every series the engine
     fetches.
  2. Nothing that decides reads the forming candle. The panel shows the live
     price on one line, labelled as information only, with its distance from
     the decision candle's close.
  3. Staleness is measured from the decision candle's close time. A series
     fails unless its decision candle is the latest one that should have
     closed, allowing a short grace for exchange delay; inside the grace the
     run fails rather than deciding on the previous candle (the reading
     Viktor confirmed on 26 September 2026).
  4. The decision log records, for each series, the decision candle's open
     time and whether a forming candle was dropped.

Before the fix, data/data_fetcher.py read MEXC's close_time, threw it away and
kept every row, so the close, the volume and every indicator at the decision
bar came from the candle still forming.

Fixture-free on purpose: run_tests.py calls every test_* with no arguments, so
requests.get is replaced by hand and restored in a finally block, and every
fetch passes its own `now`. Nothing touches the network or logs/.
"""

import json
import os

import pandas as pd

import data.data_fetcher as fetcher_module
from data import validation
from data.data_fetcher import DataFetcher

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
PINNED_DIR = os.path.join(TESTS_DIR, "fixtures", "pinned")
GOLDEN = os.path.join(TESTS_DIR, "fixtures", "golden_decision.json")

STEP_MS = 4 * 60 * 60 * 1000
# A 4h boundary: 2026-09-26 16:00:00 UTC.
BOUNDARY = pd.Timestamp("2026-09-26 16:00:00")
BOUNDARY_MS = int(BOUNDARY.value // 1_000_000)

CLOSED_CLOSE = "1.05"
FORMING_CLOSE = "1.20"


class _Reply:
    def __init__(self, payload):
        self._payload = payload
        self.status_code = 200
        self.text = ""

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


def _rows(last_open_ms, n=30, close_offset_ms=0, forming_open_ms=None):
    """
    n regular 4h candles, the last opening at last_open_ms, each with MEXC's
    close_time = open + one bar + close_offset_ms. MEXC's own convention was
    not read from its documentation; both 0 and -1 ms are exercised below.
    Every candle closes at CLOSED_CLOSE, except the one opening at
    forming_open_ms, which closes at FORMING_CLOSE -- so a test can tell which
    candle a price came from.
    """
    out = []
    for i in range(n):
        open_ms = last_open_ms - (n - 1 - i) * STEP_MS
        close = FORMING_CLOSE if open_ms == forming_open_ms else CLOSED_CLOSE
        out.append([open_ms, "1.00", "1.30", "0.90", close, "100",
                    open_ms + STEP_MS + close_offset_ms, "105"])
    return out


def _fetch(rows, now, timeframe="4h"):
    original = fetcher_module.requests.get
    fetcher_module.requests.get = lambda *a, **k: _Reply(rows)
    try:
        return DataFetcher().fetch_ohlc("TESTUSDT", timeframe, limit=len(rows), now=now)
    finally:
        fetcher_module.requests.get = original


# --- 1. the forming candle leaves the frame ----------------------------------

def test_the_forming_candle_is_dropped_and_its_close_is_not_the_decision_close():
    now = BOUNDARY + pd.Timedelta(hours=1)
    rows = _rows(BOUNDARY_MS, forming_open_ms=BOUNDARY_MS)
    out = _fetch(rows, now)
    assert not isinstance(out, dict), out
    assert len(out) == 29, len(out)
    assert out.index[-1] == BOUNDARY - pd.Timedelta(hours=4), out.index[-1]
    assert out["close"].iloc[-1] == float(CLOSED_CLOSE), (
        "the decision close is the forming candle's close -- finding 16"
    )
    candles = out.attrs["candles"]
    assert candles["basis"] == "live"
    assert candles["forming_candles_dropped"] == 1
    assert candles["live_price"] == float(FORMING_CLOSE)
    assert list(out.columns) == ["open", "high", "low", "close", "volume"], (
        "close_time must not leave the fetcher"
    )


def test_no_candle_is_dropped_when_the_exchange_has_not_opened_one():
    now = BOUNDARY + pd.Timedelta(minutes=5)
    rows = _rows(BOUNDARY_MS - STEP_MS)          # ends with the candle closing at BOUNDARY
    out = _fetch(rows, now)
    assert not isinstance(out, dict), out
    assert len(out) == 30
    assert out.attrs["candles"]["forming_candles_dropped"] == 0
    assert out.attrs["candles"]["live_price"] is None


def test_two_candles_are_dropped_when_this_clock_is_a_little_behind():
    """
    Three seconds before the boundary by this machine's clock, the exchange has
    already opened the next candle: the candle closing at the boundary and the
    one opening at it are both still forming here.
    """
    now = BOUNDARY - pd.Timedelta(seconds=3)
    rows = _rows(BOUNDARY_MS, forming_open_ms=BOUNDARY_MS)
    out = _fetch(rows, now)
    assert not isinstance(out, dict), out
    assert out.attrs["candles"]["forming_candles_dropped"] == 2
    assert out.index[-1] == BOUNDARY - pd.Timedelta(hours=8)
    assert out.attrs["candles"]["live_price"] == float(FORMING_CLOSE)


def test_a_future_dated_candle_is_not_dropped_out_of_sight():
    """
    Finding 25 must survive the drop: a candle opening more than one bar after
    now is a timestamp or clock defect, not a forming candle, and dropping it
    would hide the defect.
    """
    now = BOUNDARY
    rows = _rows(BOUNDARY_MS + 2 * STEP_MS)
    out = _fetch(rows, now)
    assert isinstance(out, dict) and "future-dated data" in out["error"], out


# --- 3. staleness from the close, with the grace -----------------------------

def test_a_run_inside_the_grace_fails_rather_than_deciding_on_the_previous_candle():
    now = BOUNDARY + pd.Timedelta(seconds=30)
    rows = _rows(BOUNDARY_MS, forming_open_ms=BOUNDARY_MS)
    out = _fetch(rows, now)
    assert isinstance(out, dict) and "not yet final" in out["error"], out


def test_a_run_just_after_the_grace_decides_on_the_candle_that_closed():
    now = BOUNDARY + pd.Timedelta(seconds=validation.FINALITY_GRACE_SECONDS + 1)
    rows = _rows(BOUNDARY_MS, forming_open_ms=BOUNDARY_MS)
    out = _fetch(rows, now)
    assert not isinstance(out, dict), out
    assert out.index[-1] == BOUNDARY - pd.Timedelta(hours=4)


def test_a_missing_latest_candle_is_stale():
    """The candle closing at BOUNDARY should be there five minutes later."""
    now = BOUNDARY + pd.Timedelta(minutes=5)
    rows = _rows(BOUNDARY_MS - 2 * STEP_MS)      # ends with the candle closing at BOUNDARY - 4h
    out = _fetch(rows, now)
    assert isinstance(out, dict) and "stale data" in out["error"], out


def test_the_grace_is_sixty_seconds():
    assert validation.FINALITY_GRACE_SECONDS == 60
    assert not hasattr(validation, "STALE_AFTER_BARS"), (
        "the three-bars-from-the-open allowance is replaced, not kept beside"
    )


# --- the exchange's close_time -----------------------------------------------

def test_both_close_time_conventions_are_accepted():
    now = BOUNDARY + pd.Timedelta(hours=1)
    for offset in (0, -1):
        rows = _rows(BOUNDARY_MS, close_offset_ms=offset, forming_open_ms=BOUNDARY_MS)
        out = _fetch(rows, now)
        assert not isinstance(out, dict), (offset, out)
        expected = BOUNDARY + pd.Timedelta(milliseconds=offset)
        assert out.attrs["candles"]["exchange_close_time"] == str(expected), (
            offset, out.attrs["candles"])


def test_an_exchange_close_time_that_disagrees_is_a_malformed_reply():
    now = BOUNDARY + pd.Timedelta(hours=1)
    rows = _rows(BOUNDARY_MS, close_offset_ms=5 * 60 * 1000, forming_open_ms=BOUNDARY_MS)
    out = _fetch(rows, now)
    assert isinstance(out, dict) and "close_time" in out["error"], out


def test_an_unlisted_timeframe_is_split_by_the_exchange_close_time():
    """MEXC's month has no fixed length; its own close_time decides."""
    opens = pd.date_range("2024-01-01", periods=24, freq="MS")
    rows = []
    for i, o in enumerate(opens):
        end = opens[i + 1] if i + 1 < len(opens) else o + pd.DateOffset(months=1)
        close = FORMING_CLOSE if i == len(opens) - 1 else CLOSED_CLOSE
        rows.append([int(o.value // 1_000_000), "1.00", "1.30", "0.90", close, "100",
                     int(pd.Timestamp(end).value // 1_000_000), "105"])
    now = opens[-1] + pd.Timedelta(days=3)
    out = _fetch(rows, now, timeframe="1M")
    assert not isinstance(out, dict), out
    assert len(out) == 23
    assert out.attrs["candles"]["forming_candles_dropped"] == 1


# --- pinned data --------------------------------------------------------------

def test_pinned_data_records_that_the_question_cannot_be_asked():
    DataFetcher.set_pinned_source(PINNED_DIR)
    try:
        df = DataFetcher().get_tf("AEROUSDT", "4h", limit=450)
    finally:
        DataFetcher.clear_pinned_source()
    assert "fetch_error" not in df.attrs, df.attrs
    candles = df.attrs["candles"]
    assert candles["basis"] == "pinned"
    assert candles["forming_candles_dropped"] is None, (
        "a pinned file carries no fetch time: 'dropped none' would be a claim"
    )
    assert candles["live_price"] is None
    assert len(df) == 450


# --- 4. the record ------------------------------------------------------------

def test_the_decision_candle_is_read_from_the_frame_the_fetcher_returned():
    # core.engine_core imports the indicators, which import pandas_ta at
    # module scope. Skipped without it, as the golden tests are.
    import pytest
    pytest.importorskip("pandas_ta")
    from core.engine_core import Phase7Engine

    now = BOUNDARY + pd.Timedelta(hours=1)
    df = _fetch(_rows(BOUNDARY_MS, forming_open_ms=BOUNDARY_MS), now)
    rec = Phase7Engine._decision_candle(df, "4h")
    assert rec == {
        "open_time": str(BOUNDARY - pd.Timedelta(hours=4)),
        "close_time": str(BOUNDARY),
        "exchange_close_time": str(BOUNDARY),
        "forming_candles_dropped": 1,
        "live_price": float(FORMING_CLOSE),
        "basis": "live",
    }, rec
    assert Phase7Engine._decision_candle(None, "4h") is None


def test_the_golden_record_carries_a_decision_candle_for_every_series():
    with open(GOLDEN) as f:
        golden = json.load(f)
    candles = golden["provenance"]["decision_candles"]
    assert sorted(candles) == ["btc", "macro", "struct"], candles
    for name, rec in candles.items():
        assert rec["basis"] == "pinned", (name, rec)
        assert rec["forming_candles_dropped"] is None, (name, rec)
        assert rec["open_time"] == golden["lineage"]["inputs"][name]["last_candle"], (
            name, rec)


# --- 2. the panel -------------------------------------------------------------

def _panel(provenance, current_price=0.80):
    from core.panel_render import render_panel
    return render_panel({
        "symbol": "TESTUSDT", "timeframe": "4h",
        "bias": {"raw": "NEUTRAL"}, "trend": {}, "structure": {}, "entry": {},
        "risk": {}, "exit": {"current_price": current_price},
        "provenance": provenance,
    })


def _line(panel, prefix):
    lines = [ln for ln in panel.splitlines() if ln.lstrip().startswith(prefix)]
    assert len(lines) == 1, (prefix, lines)
    return lines[0]


def test_the_panel_shows_the_live_price_as_information_only():
    panel = _panel({"decision_candles": {"struct": {
        "open_time": "2026-09-26 12:00:00", "live_price": 0.84, "basis": "live"}}})
    decision = _line(panel, "DECISION CLOSE")
    live = _line(panel, "LIVE PRICE")
    assert "$0.8000" in decision and "2026-09-26 12:00:00" in decision, decision
    assert "$0.8400" not in decision, "the live price leaked into the decision line"
    assert "$0.8400" in live and "information only" in live, live
    assert "+5.00% from the decision close" in live, live


def test_the_panel_says_why_there_is_no_live_price():
    pinned = _line(_panel({"decision_candles": {"struct": {
        "open_time": "2025-03-16 20:00:00", "live_price": None, "basis": "pinned"}}}),
        "LIVE PRICE")
    assert "pinned" in pinned and "$" not in pinned, pinned
    none_sent = _line(_panel({"decision_candles": {"struct": {
        "open_time": "2026-09-26 12:00:00", "live_price": None, "basis": "live"}}}),
        "LIVE PRICE")
    assert "no forming candle" in none_sent and "$" not in none_sent, none_sent
    absent = _line(_panel({}), "LIVE PRICE")
    assert "not available" in absent and "$" not in absent, absent
