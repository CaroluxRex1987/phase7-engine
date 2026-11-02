"""
The reading of 14 November's six computations for the redesign's draft.

Written 2 November 2026 from DECISIONS, "Decision, 2 November 2026 -- how the
reading of 14 November measures the redesign draft's gaps, and what result
counts against the draft" (filed at `e939734`), and tested on synthetic records
only (tests/test_measure_draft_gaps.py), before any of the reading's data was
read. That entry is the method. Where this script and the entry differ, the
entry holds and the difference is recorded; the readings this script had to
make where the entry leaves a choice are listed under READINGS below.

WHAT IT READS. The live decision logs (`phase7_decision_log_<pair>.jsonl` in
the folder given) and, for what a record does not hold, that run's own archive
(`provenance.archive_path`, resolved under --root, the repository by default).
It reads nothing else and writes nothing unless --json is given.

THE POPULATION (the entry, "The records", point 1). The decisions the reading
counts under "Decision, 17 October 2026 -- how the forward measurement is
counted": live records, 4h, at one `code_hash`, of candles that opened from
08:00 UTC on 17 October, one per pair per candle, the scheduled task's. The
task's runs start at minute 05 of 02, 06, 10, 14, 18 and 22 o'clock, Swedish
time (Task Scheduler keeps local time, so five minutes after a close before the
clocks went back on 25 October and sixty-five after). A record is the task's
when it was logged in the five minutes from the first such start at or after
its candle closed. Degraded records are counted apart and are in no rate. The
rest is N.

THE SIX COMPUTATIONS, each with what counts against the draft, are the entry's
points 1 to 6; each function below names its point.

READINGS -- where the entry leaves a choice, this is the one made:

 1. Swedish time is computed from the EU rule (summer time from 01:00 UTC on
    the last Sunday of March to 01:00 UTC on the last Sunday of October), not
    from a time-zone database, so the answer is the same on Windows and Linux
    with no `tzdata` installed.
 2. A second record that would also be the task's for the same pair and candle
    is reported, and the first logged is kept.
 3. "Close inside the band" (point 2's AGGRESSIVE) is read literally: the close
    between EMA_20 and EMA_50, ends included. Today's AGGRESSIVE reads "ACTIVE
    ENTRY ZONE", which reaches a whole band width either side of the midpoint;
    that count is printed beside it, for the draft to choose.
 4. A record with a side is one the DRAFT's direction gives a side (point 1).
 5. Gate 0 is today's malformed-input check: bias, trend, entry and risk are
    objects. Gate 1 is `read_risk_verdict` on the record's risk block, and a
    record whose draft side is not the risk plan's side (`_plan_direction`,
    the targets' order), or whose plan has no side, is counted apart and has no
    draft action. Gates 3 to 5 are today's `_read_signal` on the draft side's
    blocker list, so a malformed list fails as it does today. Gate 6 needs a
    `macro_bias` of BULLISH, BEARISH or NEUTRAL; gate 7 is T >= F, with F the
    value point 3 proposes unless --floor gives one.
 6. The draft action is the first gate, in order, that fails; a gate that is
    not measured before any gate fails leaves the action not measured.
 7. "How many records each alone blocks" (point 6) counts records where that
    gate is the only one of gates 0 to 9 that fails, all ten measured. A
    NEUTRAL record has no side for gates 3 to 9 but 7, so gate 2's count is
    the NEUTRAL records on which gates 0, 1 and 7 pass (gate 1 reads
    |price - stop|, the entry says, which has no side); said in the report.
 8. An entry (point 6) is a trade action whose previous counted record on the
    pair does not hold a trade action on the same side; a previous record with
    no draft action is not one, and those entries are counted beside. The
    projection divides entries by the records whose draft action was measured.
    Today's entries are counted the same way, for comparison.
 9. Percentiles are numpy's default (linear between order statistics). "Under
    F" is strictly under. Q's bins are [0, 10), [10, 20) ... [90, 100].
10. F's series is 1, 2, 5, 10, 20, 50 ... USDT, up to 10**15; a pair with no
    measured turnover takes no part in proposing F.
11. Point 3 (b)'s "nine of the ten pairs" is read as at least nine pairs.

What none of this answers is the entry's: whether the draft decides better.

    python docs/build/measure_draft_gaps.py logs
    python docs/build/measure_draft_gaps.py logs --json reading.json

Documentation tooling, under docs/, which the code fingerprint does not read.
"""

import argparse
import datetime as dt
import glob
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import numpy as np

from core import lineage
from core.decision_log import is_live_record
from indicators.volume_profile import compute_volume_profile
from models.decision_model import DecisionModel, read_risk_verdict

UTC = dt.timezone.utc
BAR = dt.timedelta(hours=4)
FIRST_OPEN = dt.datetime(2026, 10, 17, 8, 0, tzinfo=UTC)    # rule 1, 17 October
CODE_HASH = "816d4951"                                       # the entry, point 1
TASK_HOURS = (2, 6, 10, 14, 18, 22)                          # Swedish time, minute 05
TASK_MINUTE = 5
TASK_WINDOW = dt.timedelta(minutes=5)
PROFILE_BINS = 50                                            # config.VOLUME_PROFILE_BINS
HVN_RTOL = 1e-9
CANDLES_A_YEAR = 2190
PAIRS = 10
TRADE_ACTIONS = ("AGGRESSIVE LONG", "LONG", "CONSERVATIVE LONG",
                 "AGGRESSIVE SHORT", "SHORT", "CONSERVATIVE SHORT")
GATE_LABELS = {
    0: "WAIT", 2: "WAIT", 3: "NO-TRADE (SIGNAL UNCONFIRMED)",
    4: "NO-TRADE (SIGNAL UNCONFIRMED)", 5: "NO-TRADE (SIGNAL UNCONFIRMED)",
    6: "NO-TRADE (MACRO AGAINST)", 7: "NO-TRADE (THIN MARKET)", 8: "WAIT", 9: "WAIT",
}
LOG_NAME = re.compile(r"^phase7_decision_log_(.+)\.jsonl$")


# ---------------------------------------------------------------- time

def _last_sunday(year, month):
    day = dt.date(year, month + 1, 1) - dt.timedelta(days=1) if month < 12 else dt.date(year, 12, 31)
    return day - dt.timedelta(days=(day.weekday() + 1) % 7)


def stockholm_offset(t):
    """UTC+2 in summer time, UTC+1 otherwise, by the EU rule (READINGS, 1)."""
    t = t.astimezone(UTC)
    start = dt.datetime.combine(_last_sunday(t.year, 3), dt.time(1, 0), UTC)
    end = dt.datetime.combine(_last_sunday(t.year, 10), dt.time(1, 0), UTC)
    return dt.timedelta(hours=2) if start <= t < end else dt.timedelta(hours=1)


def task_start(close):
    """The first scheduled start at or after a candle's close (UTC)."""
    first = close.replace(minute=TASK_MINUTE, second=0, microsecond=0)
    if first < close:
        first += dt.timedelta(hours=1)
    for j in range(6):
        s = first + dt.timedelta(hours=j)
        local = s + stockholm_offset(s)
        if local.hour in TASK_HOURS and local.minute == TASK_MINUTE:
            return s
    raise ValueError(f"no scheduled start within six hours of {close}")


def parse_time(text):
    """A UTC datetime from an ISO string or a pandas Timestamp's str(); naive is UTC."""
    if not isinstance(text, str) or not text:
        return None
    try:
        t = dt.datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    return t.replace(tzinfo=UTC) if t.tzinfo is None else t.astimezone(UTC)


# ---------------------------------------------------------------- values

def num(value):
    """A finite float, or None. JSON's null (a non-finite value) is None."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    value = float(value)
    return value if math.isfinite(value) else None


def bar_values(decision):
    ind = (decision.get("lineage") or {}).get("indicators_at_decision_bar")
    return ind if isinstance(ind, dict) else {}


def side_of(action):
    if action not in TRADE_ACTIONS:
        return None
    return "LONG" if action.endswith("LONG") else "SHORT"


# ---------------------------------------------------------------- records

def read_logs(log_dir):
    """{pair file name: [(line number, record or None)]} for every live log."""
    out = {}
    for path in sorted(glob.glob(os.path.join(log_dir, "phase7_decision_log_*.jsonl"))):
        m = LOG_NAME.match(os.path.basename(path))
        rows = []
        with open(path, encoding="utf-8") as f:
            for number, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    rows.append((number, json.loads(line)))
                except ValueError:
                    rows.append((number, None))
        out[m.group(1).upper()] = rows
    return out


def resolve_code_hash(logs, prefix):
    """The one full code_hash in the logs that starts with `prefix`."""
    found = set()
    for rows in logs.values():
        for _, rec in rows:
            d = (rec or {}).get("decision") if isinstance(rec, dict) else None
            h = ((d or {}).get("provenance") or {}).get("code_hash") if isinstance(d, dict) else None
            if isinstance(h, str) and h.startswith(prefix):
                found.add(h)
    if len(found) > 1:
        raise SystemExit(f"code_hash prefix {prefix!r} names {len(found)} hashes: {sorted(found)}")
    return found.pop() if found else None


def select_population(logs, code_hash, first_open=FIRST_OPEN, last_open=None):
    """
    The entry's point 1. Returns a dict: `n` (the counted records, each a dict
    with pair, open, record, decision), `degraded`, and `excluded`, a count per
    reason a line is not counted, plus the task offsets seen.
    """
    excluded = {k: 0 for k in ("unreadable line", "not live", "not 4h", "other code_hash",
                               "before the window", "after the window", "no decision candle",
                               "another pair's record", "not the task's run",
                               "second task record of a candle")}
    chosen = {}
    for pair, rows in sorted(logs.items()):
        for number, rec in rows:
            d = rec.get("decision") if isinstance(rec, dict) else None
            if not isinstance(d, dict):
                excluded["unreadable line"] += 1
                continue
            if not is_live_record(d):
                excluded["not live"] += 1
                continue
            if d.get("timeframe") != "4h":
                excluded["not 4h"] += 1
                continue
            pv = d.get("provenance") or {}
            if pv.get("code_hash") != code_hash:
                excluded["other code_hash"] += 1
                continue
            opened = parse_time(((pv.get("decision_candles") or {}).get("struct") or {}).get("open_time"))
            logged = parse_time(rec.get("logged_at"))
            if opened is None or logged is None:
                excluded["no decision candle"] += 1
                continue
            if opened < first_open:
                excluded["before the window"] += 1
                continue
            if last_open is not None and opened > last_open:
                excluded["after the window"] += 1
                continue
            if str(d.get("symbol", "")).upper() != pair:
                excluded["another pair's record"] += 1
                continue
            close = opened + BAR
            start = task_start(close)
            if not (start <= logged < start + TASK_WINDOW):
                excluded["not the task's run"] += 1
                continue
            key = (pair, opened)
            if key in chosen:
                excluded["second task record of a candle"] += 1
                if chosen[key]["logged"] <= logged:
                    continue
            chosen[key] = {"pair": pair, "open": opened, "logged": logged, "line": number,
                           "record": rec, "decision": d}
    rows = sorted(chosen.values(), key=lambda r: (r["pair"], r["open"]))
    offsets = [r["logged"] - (r["open"] + BAR) for r in rows]

    def verdict(r):
        return (r["decision"].get("degradation") or {}).get("degraded")

    excluded["no degradation verdict"] = sum(1 for r in rows if verdict(r) not in (True, False))
    return {"n": [r for r in rows if verdict(r) is False],
            "degraded": [r for r in rows if verdict(r) is True],
            "excluded": excluded,
            "offsets": (min(offsets), max(offsets)) if offsets else None}


# ---------------------------------------------------------------- archive

def load_archive_frame(decision, root, cache):
    """The run's archived struct frame, or None. Cached by path."""
    path = (decision.get("provenance") or {}).get("archive_path")
    if not isinstance(path, str) or not path:
        return None
    full = path if os.path.isabs(path) else os.path.join(root, path)
    if full not in cache:
        payload = lineage.read_archive(full) if os.path.exists(full) else None
        frame = None
        if isinstance(payload, dict):
            text = ((payload.get("frames") or {}).get("struct") or {}).get("canonical")
            frame = lineage.rebuild_frame(text) if text else None
        cache[full] = frame
    return cache[full]


def check_archive(row, root, cache):
    """
    The entry's point 2: the decision candle in the archive, checked against the
    record. Returns (frame, position) or (None, reason).
    """
    d = row["decision"]
    frame = load_archive_frame(d, root, cache)
    if frame is None or len(frame) == 0:
        return None, "archive missing or unreadable"
    index = [parse_time(str(t)) for t in frame.index]
    if row["open"] not in index:
        return None, "decision candle not in the archive"
    pos = index.index(row["open"])
    if pos < 21:
        return None, "fewer than 21 candles before the decision candle"
    for k in range(1, 22):
        if index[pos] - index[pos - k] != k * BAR:
            return None, "the 21 candles before are not at 4h steps"
    vol = frame["volume"].to_numpy(dtype=float)
    if not np.all(np.isfinite(vol[pos - 21:pos])):
        return None, "a volume before the decision candle is not finite"
    ind = bar_values(d)
    for col in ("open", "close", "volume"):
        if num(ind.get(col)) is None or float(frame[col].iloc[pos]) != num(ind.get(col)):
            return None, f"the archive's {col} is not the record's"
    return (frame, pos), None


# ---------------------------------------------------------------- the six

def draft_direction(ind):
    """Point 1: BULLISH, BEARISH, NEUTRAL, or None when an input is missing."""
    s20, s50, e20, e50 = (num(ind.get(k)) for k in ("EMA20_Slope", "EMA50_Slope", "EMA_20", "EMA_50"))
    if None in (s20, s50, e20, e50):
        return None
    if s20 > 0 and s50 > 0 and e20 > e50:
        return "BULLISH"
    if s20 < 0 and s50 < 0 and e20 < e50:
        return "BEARISH"
    return "NEUTRAL"


def quality(ind):
    """Point 2: (Q, d, h), or None when ATR, an EMA, the HVN or the close is missing."""
    close, atr, e20, e50, hvn = (num(ind.get(k)) for k in ("close", "ATR", "EMA_20", "EMA_50", "HVN"))
    if None in (close, atr, e20, e50, hvn) or atr <= 0:
        return None
    d = abs(close - (e20 + e50) / 2.0) / atr
    h = abs(close - hvn) / atr
    return 80.0 * max(0.0, 1.0 - d / 3.0) + 20.0 * max(0.0, 1.0 - h / 2.0), d, h


def inside_band(ind):
    close, e20, e50 = (num(ind.get(k)) for k in ("close", "EMA_20", "EMA_50"))
    return min(e20, e50) <= close <= max(e20, e50)


def turnover(ind):
    """Point 3: (volume x close, volume x low, volume x high), or None."""
    v, c, lo, hi = (num(ind.get(k)) for k in ("volume", "close", "low", "high"))
    if None in (v, c, lo, hi):
        return None
    return v * c, v * lo, v * hi


def floor_series(limit=10 ** 15):
    value = 1
    while value <= limit:
        for m in (1, 2, 5):
            if value * m <= limit:
                yield value * m
        value *= 10


def propose_floor(t_by_pair, share=0.05):
    """Point 3: the largest F in 1, 2, 5, 10 ... with no pair over 5% of its records under F."""
    pairs = {p: np.asarray(v, dtype=float) for p, v in t_by_pair.items() if len(v)}
    if not pairs:
        return None
    best = None
    for f in floor_series():
        if all(np.mean(t < f) <= share for t in pairs.values()):
            best = f
        else:
            break
    return best


def trigger(frame, pos, side):
    """Point 4: (the trigger passes, its volume passes) on the decision candle."""
    o, c = float(frame["open"].iloc[pos]), float(frame["close"].iloc[pos])
    prev = float(frame["close"].iloc[pos - 1])
    passes = (c > o and c > prev) if side == "LONG" else (c < o and c < prev)
    vol = frame["volume"].to_numpy(dtype=float)
    return passes, bool(vol[pos] > float(np.median(vol[pos - 20:pos])))


def h5_reach(frame, ind):
    """Point 5: (w / ATR, the profile gives the record's HVN)."""
    atr, hvn = num(ind.get("ATR")), num(ind.get("HVN"))
    w = (float(frame["high"].max()) - float(frame["low"].min())) / PROFILE_BINS
    _, got, _ = compute_volume_profile(frame, num_bins=PROFILE_BINS)
    ok = (got is not None and hvn is not None and math.isfinite(got)
          and abs(got - hvn) <= HVN_RTOL * abs(hvn))
    return (w / atr if atr else None), ok


def ladder(d, side, q, t, floor, trig):
    """
    Point 6, READINGS 5 and 6: (results, action). `results` maps each gate 0..9
    to True (passes), False (fails) or None (not measured); `action` is the draft
    action, None when not measured, or "APART" when the draft side is not the
    plan's.
    """
    r = {}
    r[0] = all(isinstance(d.get(k), dict) for k in ("bias", "trend", "entry", "risk"))
    risk = d.get("risk") if isinstance(d.get("risk"), dict) else {}
    verdict = read_risk_verdict(risk) if r[0] else None
    r[1] = (verdict is True) if r[0] else None
    r[2] = side is not None
    plan = DecisionModel._plan_direction(risk)
    apart = side is not None and plan != side
    if side is not None and not apart:
        confirmed, _ = DecisionModel._read_signal(d.get("entry"), side.lower())
        r["3-5"] = confirmed
        macro = d.get("macro_bias")
        r[6] = (None if macro not in ("BULLISH", "BEARISH", "NEUTRAL")
                else not (side == "LONG" and macro == "BEARISH"))
        r[8] = None if trig is None else bool(trig[0] and trig[1])
        r[9] = None if q is None else q[0] >= 50.0
    else:
        r["3-5"] = r[6] = r[8] = r[9] = None
    r[7] = None if (t is None or floor is None) else t[0] >= floor
    # gates 3 to 5 are one test on today's list (the entry, point 6)
    order = [0, 1, 2, "3-5", 6, 7, 8, 9]
    if apart:
        return r, "APART"
    action = None
    for g in order:
        if r[g] is None:
            return r, None
        if r[g] is False:
            if g == 1:
                action = ("NO-TRADE (RISK NOT ASSESSED)" if verdict is None
                          else "NO-TRADE (RISK TOO HIGH)")
            else:
                action = GATE_LABELS[3 if g == "3-5" else g]
            return r, action
    tier = side
    if q[0] >= 70.0:
        regime = str(risk.get("risk_regime", ""))
        if inside_band(bar_values(d)) and regime in ("NORMAL RISK", "LOW RISK"):
            tier = f"AGGRESSIVE {side}"
    else:
        tier = f"CONSERVATIVE {side}"
    return r, tier


def entries(rows, key):
    """READINGS 8: (entries, of them after a record with no action) per pair."""
    out = {}
    for pair in sorted({r["pair"] for r in rows}):
        prev, count, after_unknown = "", 0, 0
        for r in (x for x in rows if x["pair"] == pair):
            a = r[key]
            s = side_of(a) if isinstance(a, str) else None
            if s is not None:
                ps = side_of(prev) if isinstance(prev, str) else None
                if ps != s:
                    count += 1
                    if prev is None or prev == "APART":
                        after_unknown += 1
            prev = a
        out[pair] = (count, after_unknown)
    return out


# ---------------------------------------------------------------- run

def measure(population, root, floor=None):
    """Every computation. Returns a dict of results; the report prints it."""
    n = population["n"]
    cache = {}
    res = {"N": len(n), "degraded": len(population["degraded"]),
           "degraded by pair": _by_pair(population["degraded"])}
    pairs = sorted({r["pair"] for r in n})

    for r in n:
        d = r["decision"]
        ind = bar_values(d)
        r["today"] = (d.get("exit") or {}).get("action")
        r["raw"] = (d.get("bias") or {}).get("raw")
        r["draft dir"] = draft_direction(ind)
        r["side"] = {"BULLISH": "LONG", "BEARISH": "SHORT"}.get(r["draft dir"])
        r["q"] = quality(ind) if r["side"] else None
        r["t"] = turnover(ind)
        got, why = check_archive(r, root, cache)
        r["archive"] = got
        r["archive problem"] = why

    # 1. direction
    one = {"not measured": sum(1 for r in n if r["draft dir"] is None)}
    table = {(a, b): 0 for a in ("BULLISH", "BEARISH", "NEUTRAL") for b in ("BULLISH", "BEARISH", "NEUTRAL")}
    other_raw = 0
    for r in n:
        if r["draft dir"] is None:
            continue
        if r["raw"] in ("BULLISH", "BEARISH", "NEUTRAL"):
            table[(r["draft dir"], r["raw"])] += 1
        else:
            other_raw += 1
    both = [r for r in n if r["draft dir"] in ("BULLISH", "BEARISH") and r["raw"] in ("BULLISH", "BEARISH")]
    opposite = [r for r in both if r["draft dir"] != r["raw"]]
    trading = [r for r in n if r["today"] in TRADE_ACTIONS and r["draft dir"] is not None]
    neutral = [r for r in trading if r["draft dir"] == "NEUTRAL"]
    zero = sum(1 for r in n if any(num(bar_values(r["decision"]).get(k)) == 0.0
                                   for k in ("EMA20_Slope", "EMA50_Slope")))
    one.update({"table, draft / today": {f"{a} / {b}": v for (a, b), v in table.items()},
                "raw bias not one of the three": other_raw,
                "opposite": _share(opposite, both, pairs),
                "NEUTRAL where today trades": _share(neutral, trading, pairs),
                "a slope exactly zero": zero})
    one["against (a)"] = _over(len(opposite), len(both), 0.02)
    one["against (b)"] = _over(len(neutral), len(trading), 0.5)
    res["1 direction"] = one

    # 3. F first: gate 7 needs it
    t_by_pair = {p: [r["t"][0] for r in n if r["pair"] == p and r["t"]] for p in pairs}
    proposed = propose_floor(t_by_pair)
    used = floor if floor is not None else proposed
    three = {"not measured": sum(1 for r in n if r["t"] is None), "F proposed": proposed,
             "F used for gate 7": used, "per pair": {}}
    against_a, under_1pct = [], 0
    for p in pairs:
        ts = np.asarray(t_by_pair[p], dtype=float)
        row = {"records": int(ts.size)}
        if ts.size:
            row.update({"min": float(ts.min()), "p1": float(np.percentile(ts, 1)),
                        "p5": float(np.percentile(ts, 5)), "p25": float(np.percentile(ts, 25)),
                        "p50": float(np.percentile(ts, 50))})
            if used is not None:
                trip = [r["t"] for r in n if r["pair"] == p and r["t"]]
                shares = [100.0 * np.mean([x[i] < used for x in trip]) for i in range(3)]
                row["% under F: close, low, high"] = shares
                if max(shares) - min(shares) > 2.0:
                    against_a.append(p)
                if used < 0.01 * row["p50"]:
                    under_1pct += 1
        three["per pair"][p] = row
    three["against (a), pairs"] = against_a
    three["pairs where F is under 1% of the median"] = under_1pct
    three["against (b)"] = used is not None and under_1pct >= 9
    res["3 liquidity floor"] = three

    # 6. the ladder (2 and 4 read its gates)
    for r in n:
        trig = trigger(*r["archive"], r["side"]) if (r["archive"] and r["side"]) else None
        r["trig"] = trig
        r["gates"], r["draft"] = ladder(r["decision"], r["side"], r["q"], r["t"], used, trig)
    measured = [r for r in n if r["draft"] not in (None, "APART")]
    full = [r for r in n if r["draft"] != "APART" and _all_measured(r)]

    def passes_except(r, skip):
        return all(r["gates"][g] is True for g in (0, 1, 2, "3-5", 6, 7, 8, 9) if g != skip)

    # 2. tiers
    sided = [r for r in n if r["side"] and r["q"]]
    two = {"records with a side": len([r for r in n if r["side"]]),
           "not measured": len([r for r in n if r["side"] and not r["q"]])}
    two["bins"] = {f"{10 * i}-{10 * i + 10}": sum(1 for r in sided if min(int(r["q"][0] // 10), 9) == i)
                   for i in range(10)}
    two["on the records with a side"] = _tiers(sided, pairs)
    others = [r for r in sided if r in full and passes_except(r, 9)]
    two["on those passing every other gate"] = _tiers(others, pairs)
    classes = two["on the records with a side"]["counts"]
    two["against"] = bool(sided) and (min(classes.values()) == 0 or max(classes.values()) > 0.9 * len(sided))
    res["2 tiers"] = two

    # 4. the trigger and its volume
    with_side = [r for r in n if r["side"]]
    trig_rows = [r for r in with_side if r["trig"] is not None]
    four = {"records with a side": len(with_side),
            "not measured (archive)": len(with_side) - len(trig_rows),
            "archive problems": _count(r["archive problem"] for r in with_side if r["trig"] is None),
            "trigger passes": _share([r for r in trig_rows if r["trig"][0]], trig_rows, pairs),
            "volume passes": _share([r for r in trig_rows if r["trig"][1]], trig_rows, pairs)}
    pop = [r for r in full if r["side"] and passes_except(r, 8)]
    four["passing every other gate"] = len(pop)
    four["trigger blocks"] = _share([r for r in pop if not r["trig"][0]], pop, pairs)
    four["its volume blocks once the trigger passed"] = _share(
        [r for r in pop if r["trig"][0] and not r["trig"][1]], pop, pairs)
    either = [r for r in pop if not (r["trig"][0] and r["trig"][1])]
    four["either blocks"] = _share(either, pop, pairs)
    four["against"] = bool(pop) and len(either) >= 0.9 * len(pop)
    res["4 trigger"] = four

    # 5. H5
    five = {"per pair": {}, "not measured": 0, "close to a line": []}
    for p in pairs:
        ratios = []
        for r in (x for x in sided if x["pair"] == p):
            if not r["archive"]:
                five["not measured"] += 1
                continue
            ratio, ok = h5_reach(r["archive"][0], bar_values(r["decision"]))
            if not ok or ratio is None:
                five["not measured"] += 1
                continue
            ratios.append(ratio)
            b = 10.0 * ratio
            if abs(r["q"][0] - 50.0) <= b or abs(r["q"][0] - 70.0) <= b:
                five["close to a line"].append((p, str(r["open"]), round(r["q"][0], 4), round(b, 4)))
        five["per pair"][p] = ({"records": len(ratios), "median w/ATR": float(np.median(ratios)),
                                "max w/ATR": float(np.max(ratios))} if ratios else {"records": 0})
    five["against H5 being minor"] = len(five["close to a line"]) > 0
    res["5 H5"] = five

    # 6. reported
    six = {"records with a draft action": len(measured),
           "plan's side not the draft's (apart)": sum(1 for r in n if r["draft"] == "APART"),
           "draft action not measured": sum(1 for r in n if r["draft"] is None),
           "per pair": {}}
    today_e, draft_e = entries(n, "today"), entries(n, "draft")
    for p in pairs:
        rows = [r for r in n if r["pair"] == p]
        six["per pair"][p] = {"today's trade actions": sum(1 for r in rows if r["today"] in TRADE_ACTIONS),
                              "draft's trade actions": sum(1 for r in rows if r["draft"] in TRADE_ACTIONS),
                              "today's entries": today_e[p][0], "draft's entries": draft_e[p][0],
                              "draft's entries after a record with no action": draft_e[p][1]}
    six["draft actions"] = _count(r["draft"] for r in measured)
    six["fully measured (for 'alone')"] = len(full)
    alone = {g: 0 for g in (2, "3-5", 6, 7, 8, 9)}
    for r in full:
        fails = [g for g in (0, 1, 2, "3-5", 6, 7, 8, 9) if r["gates"][g] is False]
        if len(fails) == 1 and fails[0] in alone:
            alone[fails[0]] += 1
    alone[2] = sum(1 for r in n if r["side"] is None and r["draft dir"] is not None
                   and all(r["gates"][g] is True for g in (0, 1, 7)))
    six["blocks alone"] = {str(k): v for k, v in alone.items()}
    total_entries = sum(v[0] for v in draft_e.values())
    six["draft's entries"] = total_entries
    six["entries a year, projected"] = (None if not measured else
                                        total_entries / len(measured) * CANDLES_A_YEAR * PAIRS)
    six["against"] = six["entries a year, projected"] is not None and six["entries a year, projected"] < 100
    six["blocks most alone"] = max(alone, key=lambda g: alone[g]) if any(alone.values()) else None
    six["blocks most alone"] = None if six["blocks most alone"] is None else str(six["blocks most alone"])
    res["6 ladder"] = six
    return res


def _all_measured(r):
    if r["side"] is None:
        return False
    return all(r["gates"][g] is not None for g in (0, 1, 2, "3-5", 6, 7, 8, 9))


def _tiers(rows, pairs):
    counts = {"70 and over": 0, "50 to under 70": 0, "under 50": 0}
    aggressive = active = 0
    for r in rows:
        q = r["q"][0]
        if q >= 70:
            counts["70 and over"] += 1
            ind = bar_values(r["decision"])
            regime_ok = str((r["decision"].get("risk") or {}).get("risk_regime")) in ("NORMAL RISK", "LOW RISK")
            if regime_ok and inside_band(ind):
                aggressive += 1
            status = str((r["decision"].get("entry") or {}).get("entry_status", ""))
            if regime_ok and "ACTIVE" in status.upper():
                active += 1
        elif q >= 50:
            counts["50 to under 70"] += 1
        else:
            counts["under 50"] += 1
    return {"records": len(rows), "counts": counts, "AGGRESSIVE (close inside the band)": aggressive,
            "AGGRESSIVE as today reads it (ACTIVE ENTRY ZONE)": active,
            "per pair": {p: {k: sum(1 for r in rows if r["pair"] == p and _tier_of(r["q"][0]) == k)
                             for k in counts} for p in pairs}}


def _tier_of(q):
    return "70 and over" if q >= 70 else ("50 to under 70" if q >= 50 else "under 50")


def _share(part, whole, pairs):
    pooled = (len(part), len(whole))
    per = {p: (sum(1 for r in part if r["pair"] == p), sum(1 for r in whole if r["pair"] == p))
           for p in pairs}
    return {"pooled": pooled, "per pair": per}


def _over(k, n, limit):
    return n > 0 and k > limit * n


def _count(values):
    out = {}
    for v in values:
        out[str(v)] = out.get(str(v), 0) + 1
    return dict(sorted(out.items()))


def _by_pair(rows):
    return _count(r["pair"] for r in rows)


def _readable(obj):
    """Each (part, whole) share as "k of n (p%)", for the text report only."""
    if isinstance(obj, dict):
        return {k: _readable(v) for k, v in obj.items()}
    if (isinstance(obj, tuple) and len(obj) == 2
            and all(isinstance(x, int) and not isinstance(x, bool) for x in obj)):
        k, n = obj
        return f"{k} of {n}" + (f" ({100.0 * k / n:.1f}%)" if n else "")
    if isinstance(obj, (list, tuple)):
        return [_readable(v) for v in obj]
    return obj


def report(population, res):
    """The results as text: every share with its count, pooled and per pair."""
    lines = []
    add = lines.append
    off = population["offsets"]
    add(f"N = {res['N']} counted records; degraded, apart: {res['degraded']} {res['degraded by pair']}")
    add(f"not counted: {population['excluded']}")
    if off:
        add(f"the task's records were logged {off[0]} to {off[1]} after their candle closed")
    for name in ("1 direction", "2 tiers", "3 liquidity floor", "4 trigger", "5 H5", "6 ladder"):
        add("")
        add(f"== {name}")
        add(json.dumps(_readable(res[name]), indent=1, default=str))
    add("")
    add("gate 2's 'alone' count is the NEUTRAL records on which gates 0, 1 and 7 pass: "
        "a NEUTRAL record has no side for gates 3 to 6, 8 and 9")
    add("counts against: "
        f"direction (a) {res['1 direction']['against (a)']}, (b) {res['1 direction']['against (b)']}; "
        f"tiers {res['2 tiers']['against']}; "
        f"F (a) {bool(res['3 liquidity floor']['against (a), pairs'])}, "
        f"(b) {res['3 liquidity floor']['against (b)']}; "
        f"trigger {res['4 trigger']['against']}; H5 {res['5 H5']['against H5 being minor']}; "
        f"ladder {res['6 ladder']['against']} (blocks most alone: gate {res['6 ladder']['blocks most alone']})")
    return "\n".join(lines)


def main(argv=None):
    import logging
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("log_dir", help="the folder of live decision logs (logs)")
    parser.add_argument("--root", help="where the records' archive paths start; the repository by default")
    parser.add_argument("--code-hash", default=CODE_HASH, help="the version, or a prefix naming one")
    parser.add_argument("--first-open", default=FIRST_OPEN.isoformat(), help="the window's first candle (UTC)")
    parser.add_argument("--last-open", help="the window's last candle (UTC); by default the last read")
    parser.add_argument("--floor", type=float, help="F for gate 7; by default the value point 3 proposes")
    parser.add_argument("--json", help="also write the results here")
    args = parser.parse_args(argv)
    logging.disable(logging.CRITICAL)

    logs = read_logs(args.log_dir)
    if not logs:
        raise SystemExit(f"no decision logs in {args.log_dir}")
    code_hash = resolve_code_hash(logs, args.code_hash)
    if code_hash is None:
        raise SystemExit(f"no record at a code_hash starting {args.code_hash!r}")
    first = parse_time(args.first_open)
    last = parse_time(args.last_open) if args.last_open else None
    population = select_population(logs, code_hash, first, last)
    res = measure(population, args.root or REPO, args.floor)
    res["code_hash"] = code_hash
    print(f"code_hash {code_hash}")
    print(report(population, res))
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
    return 0


if __name__ == "__main__":
    sys.exit(main())
