"""
The second pinned decision's base series -- the redesign's stage 4.

WHY IT EXISTS. Stage 3 made the first pinned fixture a WAIT at gate 8, and
stage 4 makes its entry quality 0. The golden snapshot therefore stopped
covering a trade: the tier, the stop, the three targets, the R:R and the
order the panel prints are all fields a refused run does not exercise. The
first fixture stays as the case where the gates refuse, and
tests/fixtures/ohlcv_trade_4h.csv is pinned beside it as the case where
every gate passes (docs/redesign_entry53_draft.md, section 10.1).

WHAT THIS FILE HOLDS, and what holds the rest. The DECISION the series
produces is tests/test_golden_path.py's --
test_the_trade_decision_matches_its_snapshot pins it field by field, and
test_the_second_pinned_decision_actually_reaches_a_trade holds that it is
still a trade, against the engine rather than against its own snapshot.
This file holds the SERIES: that the committed bytes are the ones the
search found, and that the series is clean by the engine's own standards.

WHY THE HASH IS PINNED. The series is written by docs/build/make_pinned.py
from seed 32 through random.Random.gauss, which is not promised to be
stable across Python versions. The committed file is the source of truth
and this hash is what catches a drift -- in the file, or in the
reproduction. It is the hash section 10.1 recorded when the seed was
searched, on 15 November 2026, before any of this stage's code existed.

HOW THIN THE TRADE IS. Its ADX is 21.59, 1.59 over the floor of 20, and its
entry quality 79.83, 9.83 over the line of 70. A change to how ADX is
computed, or an ADX floor tuned above 21.59 (the tunable list, ruled on
12 November 2026), makes it stop being a trade -- and then the seed is
searched again rather than the snapshot re-baselined. The golden test says
so in its own failure message.

No fixtures and no pytest import outside the skip: run_tests.py calls each
test with no arguments.
"""

import csv
import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

FIXTURES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")
TRADE_4H = os.path.join(FIXTURES, "ohlcv_trade_4h.csv")
CLEAN_4H = os.path.join(FIXTURES, "ohlcv_clean_4h.csv")

# docs/redesign_entry53_draft.md, section 10.1, version 13, recorded when the
# seed was searched.
SHA256_LF = "aa85f0ec9ea886ffe510ea37f8d59f2102dea6fa9f8fe9822776744d9b207824"
FOUR_HOURS_MS = 4 * 60 * 60 * 1000
CANDLES = 450


def _rows(path):
    with open(path, newline="") as handle:
        return list(csv.DictReader(handle))


def _sha256_lf(path):
    """
    The content's hash with CRLF normalised to LF, not the raw bytes.

    .gitattributes sets `* text=auto`, so this file is stored with LF and
    checked out with CRLF on Windows: the same committed content has
    different raw bytes per platform. docs/build/make_pinned.py's own
    sha256() hashes the LF form for exactly this reason, and
    tests/test_pinned_source.py carries its own copy of it.
    """
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read().replace(b"\r\n", b"\n")).hexdigest()


def test_the_committed_series_is_the_one_the_seed_search_found():
    assert _sha256_lf(TRADE_4H) == SHA256_LF, (
        "tests/fixtures/ohlcv_trade_4h.csv is not the series seed 32 "
        "produced when it was searched. Either the file changed, or "
        "random.Random.gauss did -- read docs/build/make_pinned.py's block "
        "for the method before deciding which."
    )


def test_the_series_is_clean_by_the_engines_own_standards():
    """
    The constraints docs/build/make_pinned.py's synth enforces, checked on
    the committed file rather than trusted: a fixture that violated one of
    them would make the golden run a degraded run, and the snapshot would
    pin that.
    """
    rows = _rows(TRADE_4H)
    assert len(rows) == CANDLES, len(rows)
    assert list(rows[0]) == ["timestamp", "open", "high", "low", "close",
                             "volume"], list(rows[0])

    previous = None
    for index, row in enumerate(rows):
        timestamp = int(row["timestamp"])
        o, h, l, c = (float(row[k]) for k in ("open", "high", "low", "close"))
        volume = float(row["volume"])
        if previous is not None:
            assert timestamp == previous + FOUR_HOURS_MS, (
                index, timestamp, previous)
        previous = timestamp
        assert h >= max(o, c), index
        assert l <= min(o, c), index
        assert min(o, h, l, c) > 0.0, index
        assert volume > 0.0, index


def test_the_decision_candle_is_a_resumption_candle_over_the_floor():
    """
    What makes this series the second pinned decision, read off the file:
    gates 7 and 8's inputs. The engine's own reading of them is in
    tests/test_golden_path.py; this is the fixture's half, so that a future
    edit to the file that broke one of them says which.
    """
    rows = _rows(TRADE_4H)
    last, before = rows[-1], rows[-2]

    close = float(last["close"])
    assert close > float(last["open"]), "the decision candle does not close up"
    assert close > float(before["close"]), (
        "the decision candle does not close above the previous close")

    volumes = [float(r["volume"]) for r in rows[-21:-1]]
    assert len(volumes) == 20
    ordered = sorted(volumes)
    median = (ordered[9] + ordered[10]) / 2.0
    assert float(last["volume"]) > median, (float(last["volume"]), median)

    # Gate 7 reads volume x close, which is how the golden harness and
    # make_pinned.py both write quote_volume. The series' smallest is well
    # over the floor, so no candle of it is a thin market.
    turnovers = [float(r["volume"]) * float(r["close"]) for r in rows]
    from models.entry_model import LIQUIDITY_FLOOR_USDT
    assert min(turnovers) > LIQUIDITY_FLOOR_USDT, min(turnovers)


def test_it_is_a_second_series_and_not_a_copy_of_the_first():
    """
    The first fixture stays the refused case. If the two files were the same
    content, the second snapshot would pin the first decision again and the
    trade would not be covered at all -- a failure that no assertion about
    the trade's own fields would catch, because they would all be the
    refused run's.
    """
    assert _sha256_lf(TRADE_4H) != _sha256_lf(CLEAN_4H)
    first, second = _rows(CLEAN_4H), _rows(TRADE_4H)
    assert len(first) == len(second), "the two series cover the same window"
    assert first[0]["timestamp"] == second[0]["timestamp"]
    assert first[-1]["timestamp"] == second[-1]["timestamp"]
    assert sum(1 for a, b in zip(first, second)
               if a["close"] != b["close"]) == len(first), (
        "the two series share a close somewhere; they are meant to be two "
        "independent walks over the same grid")


def test_make_pinned_reproduces_it_byte_for_byte_in_content():
    """
    The reproduction path, run rather than described. make_pinned.py writes
    CRLF (csv.writer's default terminator), and git stores this file with LF
    and checks it out per platform, so the comparison is of the content and
    not of the raw bytes -- the same reason the hash above is of the LF
    form.

    The script is not imported: importing it writes files. Its synth and its
    parameters are copied here, and a drift between the copy and the script
    is what test_the_committed_series_is_the_one_the_seed_search_found
    catches on the committed file.
    """
    import random

    def synth(seed, start_ms, step_ms, count, start_price, drift, vol, vol_base):
        rng = random.Random(seed)
        rows, price, ts = [], start_price, start_ms
        for _ in range(count):
            o = price
            move = o * (drift + rng.gauss(0.0, vol))
            c = max(o + move, o * 0.5)
            hi = max(o, c) * (1.0 + abs(rng.gauss(0.0, vol * 0.6)))
            lo = min(o, c) * (1.0 - abs(rng.gauss(0.0, vol * 0.6)))
            v = vol_base * (0.5 + rng.random() * 1.5)
            rows.append({"timestamp": ts, "open": round(o, 8),
                         "high": round(hi, 8), "low": round(lo, 8),
                         "close": round(c, 8), "volume": round(v, 4)})
            price, ts = c, ts + step_ms
        return rows

    rebuilt = synth(32, start_ms=1735689600000, step_ms=FOUR_HOURS_MS,
                    count=CANDLES, start_price=0.5, drift=0.0011, vol=0.0105,
                    vol_base=145_000.0)
    committed = _rows(TRADE_4H)

    assert len(rebuilt) == len(committed)
    for index, (built, stored) in enumerate(zip(rebuilt, committed)):
        for column in ("timestamp", "open", "high", "low", "close", "volume"):
            assert str(built[column]) == stored[column], (index, column)
