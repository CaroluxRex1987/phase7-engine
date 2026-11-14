"""
quote_volume, the candle's turnover in USDT, reaches the frame, the record and
the pinned fixtures -- and nothing decides on it yet.

STAGE 1 OF THE REDESIGN, 14 November 2026 (docs/redesign_entry53_draft.md,
section 5). MEXC sends the turnover as the eighth kline field.
data/data_fetcher.py read it and dropped it, so the liquidity floor ruled on
31 October had nothing to measure. This stage carries the column from the
fetch to the record:

  - fetch_ohlc keeps it, as a float, on closed candles only;
  - the pinned loader keeps it when the file has it and does not compute it
    when the file does not;
  - validate_ohlcv checks it as it checks volume, when the frame carries it;
  - the input hash and the candle archive hold it, because canonical_text
    writes every column;
  - the record's decision-bar row holds it, because that row is read off the
    frame;
  - the committed pinned set's AEROUSDT_4h.csv carries it, as volume x close.

What an ABSENT quote_volume means for a run is the liquidity gate's to say,
in stage 3. Until then a five-column frame is a frame, as it was: the test
below holds that, so stage 3 moves it on purpose.

Fixture-free, per run_tests.py. In Claude's sandbox all of this is Linux
evidence.
"""

import csv
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

import data.data_fetcher as fetcher_module
from core import lineage
from data.data_fetcher import DataFetcher
from data.validation import validate_ohlcv

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
PINNED_DIR = os.path.join(TESTS_DIR, "fixtures", "pinned")
CLEAN = os.path.join(TESTS_DIR, "fixtures", "ohlcv_clean_4h.csv")

FIVE = ["open", "high", "low", "close", "volume"]
SIX = FIVE + ["quote_volume"]

STEP_MS = 4 * 60 * 60 * 1000
BOUNDARY = pd.Timestamp("2026-09-26 16:00:00")
BOUNDARY_MS = int(BOUNDARY.value // 1_000_000)


class _Reply:
    def __init__(self, payload):
        self._payload = payload
        self.status_code = 200
        self.text = ""

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


def _rows(n=30, quote=None):
    """
    n closed 4h candles and one forming, the forming one opening at BOUNDARY.
    Candle i's quote_volume is 1000 + i, as MEXC sends it: a string. `quote`
    replaces the cell of the candle whose position it names.
    """
    out = []
    for i in range(n + 1):
        open_ms = BOUNDARY_MS - (n - i) * STEP_MS
        out.append([open_ms, "1.00", "1.30", "0.90", "1.05", "100",
                    open_ms + STEP_MS, str(1000 + i)])
    for position, cell in (quote or {}).items():
        out[position][7] = cell
    return out


def _fetch(rows):
    original = fetcher_module.requests.get
    fetcher_module.requests.get = lambda *a, **k: _Reply(rows)
    try:
        return DataFetcher().fetch_ohlc(
            "TESTUSDT", "4h", limit=len(rows),
            now=BOUNDARY + pd.Timedelta(hours=1))
    finally:
        fetcher_module.requests.get = original


def _clean_frame():
    df = pd.read_csv(CLEAN)
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df.set_index("timestamp")


def _with_quote_volume(df):
    out = df.copy()
    out["quote_volume"] = out["volume"] * out["close"]
    return out


# --- 1. the live fetch --------------------------------------------------------

def test_the_live_fetch_keeps_quote_volume_as_the_exchange_sent_it():
    out = _fetch(_rows())
    assert not isinstance(out, dict), out
    assert list(out.columns) == SIX, list(out.columns)
    assert out["quote_volume"].dtype.kind == "f", out["quote_volume"].dtype
    # Each closed candle keeps its own cell: 1000 + its position.
    assert list(out["quote_volume"]) == [float(1000 + i) for i in range(30)]


def test_the_forming_candles_quote_volume_does_not_reach_the_frame():
    out = _fetch(_rows())
    assert not isinstance(out, dict), out
    assert len(out) == 30
    assert 1030.0 not in set(out["quote_volume"]), (
        "the forming candle's turnover is in the frame -- finding 16's drop "
        "has to cover the new column too"
    )


def test_a_quote_volume_that_is_not_a_number_is_reported_not_raised():
    for cell in (None, "abc"):
        out = _fetch(_rows(quote={5: cell}))
        assert isinstance(out, dict) and "error" in out, (
            f"quote_volume {cell!r} became a frame: {out!r}"
        )
        assert "malformed" in out["error"] or "validation" in out["error"], out


def test_a_negative_quote_volume_fails_the_live_fetch():
    out = _fetch(_rows(quote={5: "-1"}))
    assert isinstance(out, dict) and "error" in out, out
    assert "negative quote_volume" in out["error"], out["error"]


# --- 2. validation -------------------------------------------------------------

def test_a_frame_with_a_sound_quote_volume_passes_validation():
    assert validate_ohlcv(_with_quote_volume(_clean_frame()), timeframe="4h") is None


def test_validation_checks_quote_volume_as_it_checks_volume():
    base = _with_quote_volume(_clean_frame())

    nan = base.copy()
    nan.loc[nan.index[77], "quote_volume"] = float("nan")
    problem = validate_ohlcv(nan, timeframe="4h")
    assert problem and "'quote_volume'" in problem and "NaN" in problem, problem

    inf = base.copy()
    inf.loc[inf.index[77], "quote_volume"] = float("inf")
    problem = validate_ohlcv(inf, timeframe="4h")
    assert problem and "infinite" in problem and "'quote_volume'" in problem, problem

    negative = base.copy()
    negative.loc[negative.index[77], "quote_volume"] = -5000.0
    problem = validate_ohlcv(negative, timeframe="4h")
    assert problem and "negative quote_volume" in problem, problem

    zero = base.copy()
    zero["quote_volume"] = 0.0
    problem = validate_ohlcv(zero, timeframe="4h")
    assert problem and "all quote_volume values are zero" in problem, problem


def test_one_zero_quote_volume_candle_is_a_measurement_not_a_defect():
    """As with volume: zero on every candle is an absence, zero on one is not."""
    df = _with_quote_volume(_clean_frame())
    df.loc[df.index[77], "quote_volume"] = 0.0
    assert validate_ohlcv(df, timeframe="4h") is None


def test_a_frame_without_quote_volume_is_still_a_frame_until_stage_3():
    """
    Stage 1 changes no action, so a five-column frame validates as it did.
    Stage 3 gives the absence its meaning (a missing input: the run is
    degraded and gate 7 records "not measured") and moves this test.
    """
    assert validate_ohlcv(_clean_frame(), timeframe="4h") is None


# --- 3. the pinned loader ------------------------------------------------------

def _pinned_frame(header, row_cells):
    with tempfile.TemporaryDirectory() as tmp:
        with open(os.path.join(tmp, "TESTUSDT_4h.csv"), "w", newline="") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(header)
            for i in range(40):
                w.writerow([BOUNDARY_MS + i * STEP_MS] + row_cells(i))
        try:
            DataFetcher.set_pinned_source(tmp)
            return DataFetcher().get_tf("TESTUSDT", "4h", limit=300)
        finally:
            DataFetcher.clear_pinned_source()


def test_the_pinned_loader_keeps_quote_volume_when_the_file_has_it():
    df = _pinned_frame(["timestamp"] + SIX,
                       lambda i: [1.0, 1.3, 0.9, 1.05, 100, 2000 + i])
    assert df.attrs.get("fetch_error") is None, df.attrs.get("fetch_error")
    assert list(df.columns) == SIX, list(df.columns)
    assert list(df["quote_volume"]) == [float(2000 + i) for i in range(40)]


def test_the_pinned_loader_does_not_invent_quote_volume():
    df = _pinned_frame(["timestamp"] + FIVE,
                       lambda i: [1.0, 1.3, 0.9, 1.05, 100])
    assert df.attrs.get("fetch_error") is None, df.attrs.get("fetch_error")
    assert list(df.columns) == FIVE, (
        f"a pinned file with no quote_volume came back with {list(df.columns)}: "
        "the column was computed, and a stand-in is not the exchange's number"
    )


def test_a_pinned_file_with_a_bad_quote_volume_is_refused():
    df = _pinned_frame(["timestamp"] + SIX,
                       lambda i: [1.0, 1.3, 0.9, 1.05, 100, -1 if i == 7 else 50])
    error = df.attrs.get("fetch_error")
    assert error and "negative quote_volume" in error, error


# --- 4. the committed pinned set ------------------------------------------------

def _csv_rows(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def test_the_pinned_struct_series_carries_quote_volume_and_the_others_do_not():
    assert list(_csv_rows(os.path.join(PINNED_DIR, "AEROUSDT_4h.csv"))[0]) == \
        ["timestamp"] + SIX
    for name in ("AEROUSDT_1d.csv", "BTCUSDT_4h.csv"):
        assert list(_csv_rows(os.path.join(PINNED_DIR, name))[0]) == \
            ["timestamp"] + FIVE, name


def test_the_pinned_struct_series_is_the_clean_fixture_plus_volume_times_close():
    """
    The five columns the file had are the clean fixture's, cell for cell as
    text, and the sixth is volume x close to four decimals: the rule in
    docs/build/make_pinned.py, restated here because that script writes files
    when imported.
    """
    clean = _csv_rows(CLEAN)
    pinned = _csv_rows(os.path.join(PINNED_DIR, "AEROUSDT_4h.csv"))
    assert len(clean) == len(pinned) == 450
    for before, after in zip(clean, pinned):
        assert {k: after[k] for k in before} == before, before["timestamp"]
        expected = repr(round(float(before["volume"]) * float(before["close"]), 4))
        assert after["quote_volume"] == expected, (
            before["timestamp"], after["quote_volume"], expected)


# --- 5. the record --------------------------------------------------------------

def test_the_input_hash_and_the_archive_text_hold_the_column():
    five = _clean_frame()
    six = _with_quote_volume(five)
    text = lineage.canonical_text(six)
    header = text.splitlines()[1]
    assert "quote_volume" in header, header
    assert lineage.frame_hash(six) != lineage.frame_hash(five)

    # The hash follows the column's values, not only its presence.
    moved = six.copy()
    moved.loc[moved.index[77], "quote_volume"] += 0.0001
    assert lineage.frame_hash(moved) != lineage.frame_hash(six)

    rebuilt = lineage.rebuild_frame(text)
    assert lineage.frame_hash(rebuilt) == lineage.frame_hash(six)
    assert lineage.CANONICAL_FORMAT == 1, (
        "a new column is data in format 1; the format number moved"
    )


def test_the_golden_record_holds_the_decision_candles_quote_volume():
    """
    Read from the committed snapshot, so it needs no engine: the struct
    input's columns, and the decision bar's own value, which is the clean
    fixture's last volume x close.
    """
    import json
    with open(os.path.join(TESTS_DIR, "fixtures", "golden_decision.json")) as f:
        golden = json.load(f)
    inputs = golden["lineage"]["inputs"]
    assert inputs["struct"]["columns"] == sorted(SIX), inputs["struct"]["columns"]
    assert inputs["macro"]["columns"] == sorted(FIVE), inputs["macro"]["columns"]
    assert inputs["btc"]["columns"] == sorted(FIVE), inputs["btc"]["columns"]

    last = _csv_rows(CLEAN)[-1]
    expected = round(float(last["volume"]) * float(last["close"]), 4)
    recorded = golden["lineage"]["indicators_at_decision_bar"]["quote_volume"]
    assert recorded == expected, (recorded, expected)
