"""
The forward measurement's count: what the scheduled task's runs decided, per
pair and per version, and which candles no run read.

Written 7 November 2026, before the reading of 14 November, from DECISIONS,
"Decision, 17 October 2026 -- how the forward measurement is counted" (its
rules 1 to 4), under "Ruling, 17 October 2026 -- the forward measurement ...",
point 5 ("Claude counts"). The reading of 31 October was counted by a script
that was never filed; this one is, so that the reading of 14 November can be
re-run and checked. Its check against data is that, given the logs and the
window of 31 October, it gives that reading's figures (PHASE7_NEXT.md, Open
items, the forward measurement, "The reading of 31 October"). Tested on
synthetic records only (tests/test_count_forward_measurement.py).

WHAT IT READS. The live decision logs (`phase7_decision_log_<pair>.jsonl` in
the folder given) and the process log (`phase7_engine.log` in the same folder
unless --process-log names another). It writes nothing unless --json is given.

THE RECORDS (rules 1 and 2) are measure_draft_gaps.py's population, imported
from it so that the two readings count the same records: live, 4h, at one
`code_hash`, of candles that opened from 08:00 UTC on 17 October to the last
open given, one per pair per candle, the task's -- logged within five minutes
of its first start at or after the candle's close (minute 05 of 02, 06, 10,
14, 18 and 22 o'clock, Swedish time). Here the degraded records are counted
with the rest, as the reading of 31 October counted them, and also apart.

FAILURES (rules 3 and 4) are read from the process log's "Engine returned
error for <pair>" lines only, never from ERROR lines. One whose reason holds
"not yet final" is a refusal; any other is a failure. A candle with no counted
record is missed, whatever was refused or failed on it.

READINGS -- where the decision leaves a choice, this is the one made:

 1. The window's end is given (--last-open, the open time in UTC of the last
    candle counted); nothing here guesses it from the time the logs were
    staged. Its start is rule 1's candle unless --first-open gives another.
 2. One version at a time. If the window holds live 4h task-shaped records at
    more than one `code_hash`, the script stops and names them; each version's
    count starts from zero, so its window is the caller's to give
    (--code-hash and --first-open).
 3. A record the population would count but whose degradation verdict is
    neither true nor false stops the script: the decision counts it, and this
    script cannot place it. No such record is on the engine's path.
 4. A candle with no counted record, but with a live 4h record of the same
    version and pair logged by some other run, is missed, and also listed as
    "read only by a run that is not the task's". With no task record in the
    window, there is no version to match, and a record of any version is
    listed.
 5. The process log's times are Swedish local time with no zone. They are
    read by the EU rule, as measure_draft_gaps.py reads Swedish time. In the
    hour the clocks go back, a time has two readings; if both fall on the
    same candle, that candle is used; if not, the line is counted as
    ambiguous and placed on no candle. A time in the hour the clocks skip is
    counted the same way.
 6. A process-log attempt belongs to the candle it would read: the last that
    closed at or before its time, in UTC. A refusal names its candle's close
    in its own text ("the last candle closed at ... (UTC)"), and that is used.
    Attempts are counted when their candle is in the window.
 7. A run is a group of attempts in the process log, one "Starting Phase-7
    engine for" line each; a new run starts when a pair repeats inside the
    current one or more than 120 seconds pass since its last line. A run is
    "at the task's minute" when it starts within the five minutes from a
    scheduled start, by the same rule as the records.
 8. LONG is AGGRESSIVE LONG, LONG and CONSERVATIVE LONG; SHORT likewise.
    NO-TRADE is any action that begins "NO-TRADE". Anything else is counted
    as "other", by name.
 9. LONGs on the same candle are counted per candle, across pairs; a run of
    candles in a row that each hold a LONG is printed as one group. They are
    actions, not trades: one pair's LONG on consecutive candles is one setup
    read again.
10. When missed candles fall is read per candle (all pairs read it, some, or
    none) by the hour of its close in UTC -- 00, 04, 08, 12, 16 or 20 --
    which is one Swedish hour in summer time and another in winter time;
    both are printed beside each slot.

What none of this answers: why a candle was missed. The log does not say.

    python docs/build/count_forward_measurement.py logs --last-open "2026-11-14 04:00"
    python docs/build/count_forward_measurement.py logs --last-open "2026-11-14 04:00" --json count.json

Documentation tooling, under docs/, which the code fingerprint does not read.
"""

import argparse
import collections
import datetime as dt
import importlib.util
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
if REPO not in sys.path:
    sys.path.insert(0, REPO)


def _population_module():
    spec = importlib.util.spec_from_file_location(
        "phase7_measure_draft_gaps", os.path.join(HERE, "measure_draft_gaps.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


gaps = _population_module()

from core.decision_log import is_live_record  # noqa: E402

UTC = dt.timezone.utc
BAR = gaps.BAR
FIRST_OPEN = gaps.FIRST_OPEN
TASK_WINDOW = gaps.TASK_WINDOW
PAIRS = ("AEROUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "BNBUSDT",
         "DOGEUSDT", "ADAUSDT", "LINKUSDT", "AVAXUSDT", "SUIUSDT")   # the ruling's order
RUN_GAP = dt.timedelta(seconds=120)                                  # READINGS, 7
SLOTS = (0, 4, 8, 12, 16, 20)                                        # UTC close hours

LINE = re.compile(r"^(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d),(\d{3}) - ([A-Z]+) - (.*)$")
STARTING = re.compile(r"^Starting Phase-7 engine for (\S+) on (\S+)")
COMPLETED = re.compile(r"^Phase-7 engine completed successfully for (\S+)")
RETURNED_ERROR = re.compile(r"^Engine returned error for ([^:\s]+): (.*)$")
REFUSED_CLOSE = re.compile(r"the last candle closed at (\d{4}-\d\d-\d\d \d\d:\d\d:\d\d) \(UTC\)")


# ---------------------------------------------------------------- time

def floor_open(t):
    """The open of the 4h candle that holds `t` (UTC)."""
    t = t.astimezone(UTC)
    return t.replace(hour=t.hour - t.hour % 4, minute=0, second=0, microsecond=0)


def candle_read_at(t):
    """READINGS, 6: the open of the last candle closed at or before `t`."""
    return floor_open(t) - BAR


def local_to_utc(naive):
    """
    READINGS, 5: the UTC readings of a Swedish wall-clock time. A list of one
    time normally, two in the hour the clocks go back, none in the hour they
    skip.
    """
    out = []
    for hours in (2, 1):
        offset = dt.timedelta(hours=hours)
        t = (naive - offset).replace(tzinfo=UTC)
        if gaps.stockholm_offset(t) == offset:
            out.append(t)
    return out


def stockholm(t):
    return t + gaps.stockholm_offset(t)


def fmt(t):
    return t.strftime("%Y-%m-%d %H:%M UTC")


def fmt_span(td):
    s = int(round(td.total_seconds()))
    return f"{s // 60} min {s % 60} s"


def is_task_start(t):
    """READINGS, 7: inside the five minutes from a scheduled start."""
    start = gaps.task_start(floor_open(t))
    if start > t:
        start = gaps.task_start(floor_open(t) - BAR)
    return start <= t < start + TASK_WINDOW


# ---------------------------------------------------------------- records

def window(first_open, last_open):
    out, t = [], first_open
    while t <= last_open:
        out.append(t)
        t += BAR
    return out


def _record_view(rec):
    """(decision, candle open, logged) of a live 4h record, or None."""
    d = rec.get("decision") if isinstance(rec, dict) else None
    if not isinstance(d, dict) or not is_live_record(d) or d.get("timeframe") != "4h":
        return None
    pv = d.get("provenance") or {}
    opened = gaps.parse_time(((pv.get("decision_candles") or {}).get("struct") or {}).get("open_time"))
    logged = gaps.parse_time(rec.get("logged_at"))
    if opened is None or logged is None:
        return None
    return d, opened, logged


def versions_in_window(logs, first_open, last_open):
    """READINGS, 2: every code_hash of a live 4h record of a candle in the window."""
    found = collections.Counter()
    for pair, rows in logs.items():
        for _, rec in rows:
            view = _record_view(rec)
            if view is None:
                continue
            d, opened, logged = view
            start = gaps.task_start(opened + BAR)
            if first_open <= opened <= last_open and start <= logged < start + TASK_WINDOW:
                found[(d.get("provenance") or {}).get("code_hash")] += 1
    return found


def other_runs(logs, code_hash, first_open, last_open, counted):
    """READINGS, 4: (pair, open) read by a live 4h record that is not counted."""
    out = set()
    for pair, rows in logs.items():
        for _, rec in rows:
            view = _record_view(rec)
            if view is None:
                continue
            d, opened, _ = view
            if (first_open <= opened <= last_open
                    and (code_hash is None
                         or (d.get("provenance") or {}).get("code_hash") == code_hash)
                    and str(d.get("symbol", "")).upper() == pair
                    and (pair, opened) not in counted):
                out.add((pair, opened))
    return out


def group(action):
    """READINGS, 8."""
    if not isinstance(action, str):
        return "other"
    if action in gaps.TRADE_ACTIONS:
        return gaps.side_of(action)
    if action == "WAIT":
        return "WAIT"
    if action.startswith("NO-TRADE"):
        return "NO-TRADE"
    return "other"


# ---------------------------------------------------------------- process log

def read_process_log(path):
    """
    Every attempt the process log records: dicts with pair, local (the naive
    Swedish time of its "Starting" line), outcome ("success", "refused",
    "failed" or None when no outcome line follows), reason and refused_close.
    Also the run summary lines ("N of M pairs failed"), as they stand.
    """
    attempts, summaries, open_by_pair = [], [], {}
    if not path or not os.path.exists(path):
        return {"attempts": attempts, "summaries": summaries, "read": False}
    with open(path, encoding="utf-8", errors="replace") as f:
        for raw in f:
            m = LINE.match(raw.rstrip("\r\n"))
            if not m:
                continue
            local = dt.datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S").replace(
                microsecond=int(m.group(2)) * 1000)
            text = m.group(4)
            s = STARTING.match(text)
            if s:
                a = {"pair": s.group(1).upper(), "timeframe": s.group(2), "local": local,
                     "last": local, "outcome": None, "reason": None, "refused_close": None}
                attempts.append(a)
                open_by_pair[a["pair"]] = a
                continue
            c = COMPLETED.match(text)
            e = RETURNED_ERROR.match(text)
            pair = (c or e).group(1).upper() if (c or e) else None
            a = open_by_pair.get(pair) if pair else None
            if pair and (a is None or a["outcome"] is not None):
                # an outcome line with no "Starting" line of its own is still
                # counted (rule 4 counts from these lines), as its own attempt
                a = {"pair": pair, "timeframe": None, "local": local, "last": local,
                     "outcome": None, "reason": None, "refused_close": None,
                     "no_start_line": True}
                attempts.append(a)
                open_by_pair[pair] = a
            if a is not None:
                a["last"] = local
                if c:
                    a["outcome"] = "success"
                else:
                    reason = e.group(2)
                    a["reason"] = reason
                    if "not yet final" in reason:
                        a["outcome"] = "refused"
                        r = REFUSED_CLOSE.search(reason)
                        if r:
                            a["refused_close"] = dt.datetime.strptime(
                                r.group(1), "%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC)
                    else:
                        a["outcome"] = "failed"
                continue
            if "pairs failed" in text and m.group(3) == "ERROR":
                summaries.append((local, text))
            for a in attempts[-1:]:
                if a["outcome"] is None:
                    a["last"] = local
    return {"attempts": attempts, "summaries": summaries, "read": True}


def place(attempt):
    """READINGS, 5 and 6: (candle open, utc) or (None, None) when ambiguous."""
    if attempt["refused_close"] is not None:
        utcs = local_to_utc(attempt["local"])
        return attempt["refused_close"] - BAR, (utcs[0] if utcs else None)
    utcs = local_to_utc(attempt["local"])
    candles = {candle_read_at(t) for t in utcs}
    if len(candles) != 1:
        return None, None
    return candles.pop(), utcs[0]


def runs(attempts):
    """READINGS, 7."""
    out, cur = [], None
    for a in attempts:
        if (cur is None or a["pair"] in cur["pairs"]
                or a["local"] - cur["last"] > RUN_GAP):
            cur = {"local": a["local"], "last": a["last"], "pairs": [], "attempts": []}
            out.append(cur)
        cur["pairs"].append(a["pair"])
        cur["attempts"].append(a)
        cur["last"] = max(cur["last"], a["last"])
    return out


# ---------------------------------------------------------------- count

def count(logs, process, last_open, first_open=FIRST_OPEN, code_hash=None, pairs=PAIRS):
    """The whole count, as a dict of plain values (times as datetimes)."""
    candles = window(first_open, last_open)
    found = versions_in_window(logs, first_open, last_open)
    if code_hash is None:
        if len(found) > 1:
            raise SystemExit("the window holds records of more than one version; give "
                             "--code-hash and --first-open for each: "
                             + ", ".join(f"{h} ({n})" for h, n in sorted(found.items(), key=str)))
        code_hash = next(iter(found), None)
    elif len(code_hash) < 64:
        code_hash = gaps.resolve_code_hash(logs, code_hash)

    pop = gaps.select_population(logs, code_hash, first_open=first_open, last_open=last_open)
    if pop["excluded"].get("no degradation verdict"):
        raise SystemExit(f"{pop['excluded']['no degradation verdict']} task record(s) carry no "
                         "degradation verdict; the decision counts them and this script "
                         "cannot place them (READINGS, 3)")
    rows = sorted(pop["n"] + pop["degraded"], key=lambda r: (r["pair"], r["open"]))
    rows = [r for r in rows if r["pair"] in pairs]
    counted = {(r["pair"], r["open"]): r for r in rows}
    elsewhere = other_runs(logs, code_hash, first_open, last_open, counted)

    # records, per pair
    actions = collections.Counter()
    labels = collections.Counter()
    per_pair = {p: collections.Counter() for p in pairs}
    for r in rows:
        a = (r["decision"].get("exit") or {}).get("action")
        g = group(a)
        actions[g] += 1
        labels[a if isinstance(a, str) else repr(a)] += 1
        per_pair[r["pair"]][g] += 1
    other_labels = sorted(k for k in labels if group(k) == "other")

    # offsets from the close, by clock
    offsets = {}
    for r in rows:
        close = r["open"] + BAR
        clock = "summer" if gaps.stockholm_offset(close) == dt.timedelta(hours=2) else "winter"
        o = offsets.setdefault(clock, {"n": 0, "min": None, "max": None})
        d = r["logged"] - close
        o["n"] += 1
        o["min"] = d if o["min"] is None else min(o["min"], d)
        o["max"] = d if o["max"] is None else max(o["max"], d)

    # provenance
    def struct(r):
        return (((r["decision"].get("provenance") or {}).get("decision_candles") or {})
                .get("struct") or {})
    rows_seen = collections.Counter((r["decision"].get("provenance") or {}).get("row_count")
                                    for r in rows)
    dropped = collections.Counter(struct(r).get("forming_candles_dropped") for r in rows)
    close_ok = sum(1 for r in rows
                   if gaps.parse_time(struct(r).get("exchange_close_time")) == r["open"] + BAR)

    # missed
    missed = {p: [c for c in candles if (p, c) not in counted] for p in pairs}
    by_candle = {c: [p for p in pairs if (p, c) in counted] for c in candles}

    # process log
    placed = collections.Counter()
    attempts = []
    for a in process["attempts"]:
        c, t = place(a)
        if c is None:
            if any(first_open <= candle_read_at(u) <= last_open
                   for u in local_to_utc(a["local"])) or not local_to_utc(a["local"]):
                placed["ambiguous"] += 1
            continue
        if not (first_open <= c <= last_open):
            continue
        a = dict(a, candle=c, utc=t)
        attempts.append(a)
    run_list = runs(attempts)
    outcomes = collections.Counter(a["outcome"] or "no outcome line" for a in attempts)
    no_start = sum(1 for a in attempts if a.get("no_start_line"))
    refusals = [a for a in attempts if a["outcome"] == "refused"]
    failures = [a for a in attempts if a["outcome"] == "failed"]
    refused_then = collections.Counter(
        "read later" if (a["pair"], a["candle"]) in counted else "missed" for a in refusals)

    # degraded
    degraded = [{"pair": r["pair"], "open": r["open"],
                 "action": (r["decision"].get("exit") or {}).get("action"),
                 "missing": list((r["decision"].get("degradation") or {}).get("missing_inputs") or [])}
                for r in pop["degraded"] if r["pair"] in pairs]

    # LONGs on the same candle
    longs = {c: [p for p in pairs
                 if (p, c) in counted
                 and group((counted[(p, c)]["decision"].get("exit") or {}).get("action")) == "LONG"]
             for c in candles}
    with_long = [c for c in candles if longs[c]]
    streaks, cur = [], []
    for c in candles:
        if longs[c]:
            cur.append(c)
        elif cur:
            streaks.append(cur)
            cur = []
    if cur:
        streaks.append(cur)

    # when candles were read, by slot
    slots = {}
    for c in candles:
        close = c + BAR
        clock = "summer" if gaps.stockholm_offset(close) == dt.timedelta(hours=2) else "winter"
        s = slots.setdefault(close.hour, {"candles": 0, "all": 0, "some": 0, "none": 0,
                                          "summer": [0, 0], "winter": [0, 0]})
        n = len(by_candle[c])
        s["candles"] += 1
        s["all" if n == len(pairs) else ("none" if n == 0 else "some")] += 1
        s[clock][1] += 1
        if n == len(pairs):
            s[clock][0] += 1

    return {
        "code_hash": code_hash, "versions_in_window": dict(found),
        "first_open": first_open, "last_open": last_open, "candles": len(candles),
        "pairs": list(pairs), "records": len(rows),
        "records_per_pair": {p: sum(1 for r in rows if r["pair"] == p) for p in pairs},
        "excluded": pop["excluded"], "offsets": offsets,
        "row_count": dict(rows_seen), "forming_candles_dropped": dict(dropped),
        "exchange_close_is_open_plus_bar": close_ok,
        "actions": dict(actions), "labels": dict(labels), "other_labels": other_labels,
        "per_pair": {p: dict(per_pair[p]) for p in pairs},
        "missed_per_pair": {p: len(missed[p]) for p in pairs},
        "missed": sum(len(v) for v in missed.values()),
        "missed_read_elsewhere": sorted(elsewhere),
        "candles_read_by_all": sum(1 for c in candles if len(by_candle[c]) == len(pairs)),
        "candles_read_by_some": sum(1 for c in candles if 0 < len(by_candle[c]) < len(pairs)),
        "candles_read_by_none": sum(1 for c in candles if not by_candle[c]),
        "process_log_read": process["read"],
        "attempts": len(attempts), "outcomes": dict(outcomes),
        "attempts_ambiguous": placed["ambiguous"], "attempts_no_start_line": no_start,
        "refused": len(refusals), "refused_then": dict(refused_then),
        "refusals": [(a["pair"], a["local"], a["candle"]) for a in refusals],
        "failed": len(failures),
        "failed_per_pair": dict(collections.Counter(a["pair"] for a in failures)),
        "failures": [(a["pair"], a["local"], a["candle"], a["reason"]) for a in failures],
        "runs": len(run_list),
        "runs_at_task_minute": sum(1 for r in run_list
                                   if r["attempts"][0]["utc"] is not None
                                   and is_task_start(r["attempts"][0]["utc"])),
        "run_sizes": dict(collections.Counter(len(r["pairs"]) for r in run_list)),
        "runs_all_success": sum(1 for r in run_list
                                if all(a["outcome"] == "success" for a in r["attempts"])),
        "degraded": degraded,
        "longs": sum(len(v) for v in longs.values()),
        "candles_with_long": len(with_long),
        "long_streaks": [[(c, len(longs[c])) for c in s] for s in streaks],
        "slots": slots,
    }


# ---------------------------------------------------------------- report

def report(res):
    out = []
    w = out.append
    w("The forward measurement's count (DECISIONS, Decision, 17 October 2026).")
    w(f"Version: code_hash {res['code_hash']}")
    w(f"Window: the {res['candles']} candles that opened from {fmt(res['first_open'])} "
      f"to {fmt(res['last_open'])}.")
    pp = res["records_per_pair"]
    w(f"Read: {res['records']} records; per pair " + ", ".join(f"{p} {pp[p]}" for p in res["pairs"]))
    for clock in ("summer", "winter"):
        o = res["offsets"].get(clock)
        if o:
            w(f"  logged {fmt_span(o['min'])} to {fmt_span(o['max'])} after the close, "
              f"{o['n']} records ({clock} time)")
    ex = {k: v for k, v in res["excluded"].items() if v}
    w("  not counted: " + (", ".join(f"{k} {v}" for k, v in ex.items()) if ex else "none"))
    w(f"  row_count {res['row_count']}; forming_candles_dropped {res['forming_candles_dropped']}; "
      f"exchange close = open + 4h on {res['exchange_close_is_open_plus_bar']}")
    w(f"Candles read by all {len(res['pairs'])} pairs: {res['candles_read_by_all']}, "
      f"by some: {res['candles_read_by_some']}, by none: {res['candles_read_by_none']}.")
    mp = res["missed_per_pair"]
    share = res["missed"] / (res["candles"] * len(res["pairs"])) if res["candles"] else 0.0
    w(f"Missed: {res['missed']} ({share:.0%} of the window); per pair "
      + ", ".join(f"{p} {mp[p]}" for p in res["pairs"]))
    if res["missed_read_elsewhere"]:
        w("  of them read only by a run that is not the task's: "
          + ", ".join(f"{p} {fmt(c)}" for p, c in res["missed_read_elsewhere"]))
    if not res["process_log_read"]:
        w("Process log: not found; refusals and failures not counted.")
    else:
        w(f"Process log: {res['attempts']} attempts on candles in the window, in "
          f"{res['runs']} runs ({res['runs_at_task_minute']} at the task's minute; "
          f"sizes {res['run_sizes']}; {res['runs_all_success']} with every pair a success); "
          f"outcomes {res['outcomes']}; placed on no candle {res['attempts_ambiguous']}; "
          f"outcome lines with no starting line {res['attempts_no_start_line']}.")
        w(f"Refused: {res['refused']} {res['refused_then']}"
          + "".join(f"\n  {p} at {t:%Y-%m-%d %H:%M:%S} local, the candle of {fmt(c)}"
                    for p, t, c in res["refusals"]))
        w(f"Failed: {res['failed']}"
          + "".join(f"\n  {p} at {t:%Y-%m-%d %H:%M:%S} local, the candle of {fmt(c)}: {why}"
                    for p, t, c, why in res["failures"]))
    a = res["actions"]
    w(f"Actions, of {res['records']}: LONG {a.get('LONG', 0)}, SHORT {a.get('SHORT', 0)}, "
      f"WAIT {a.get('WAIT', 0)}, NO-TRADE {a.get('NO-TRADE', 0)}, other {a.get('other', 0)}")
    for label, n in sorted(res["labels"].items()):
        w(f"  {label}: {n}")
    w("Per pair, LONG / SHORT / WAIT / NO-TRADE (other):")
    for p in res["pairs"]:
        c = res["per_pair"][p]
        w(f"  {p} {c.get('LONG', 0)} / {c.get('SHORT', 0)} / {c.get('WAIT', 0)} / "
          f"{c.get('NO-TRADE', 0)} ({c.get('other', 0)})")
    w(f"Degraded: {len(res['degraded'])}"
      + "".join(f"\n  {d['pair']} {fmt(d['open'])} {d['action']} {d['missing']}"
                for d in res["degraded"]))
    w(f"LONGs on the same candle: {res['longs']} on {res['candles_with_long']} candles; "
      "candles in a row, pairs LONG on each:")
    for s in res["long_streaks"]:
        w(f"  from {fmt(s[0][0])}: " + ", ".join(str(n) for _, n in s))
    w("When the candles were read, by the close's hour (all pairs read it / of the slot's candles):")
    for h in sorted(res["slots"]):
        s = res["slots"][h]
        su = stockholm(dt.datetime(2026, 7, 1, h, tzinfo=UTC)).hour
        wi = stockholm(dt.datetime(2026, 1, 1, h, tzinfo=UTC)).hour
        w(f"  {h:02d}:00 UTC ({wi:02d}:00 winter / {su:02d}:00 summer): {s['all']} of "
          f"{s['candles']} (winter {s['winter'][0]} of {s['winter'][1]}, summer "
          f"{s['summer'][0]} of {s['summer'][1]}); some {s['some']}, none {s['none']}")
    w("Actions, not trades. Why a candle was missed, the log does not say.")
    return "\n".join(out)


def _plain(obj):
    if isinstance(obj, dt.datetime):
        return obj.isoformat()
    if isinstance(obj, dt.timedelta):
        return obj.total_seconds()
    if isinstance(obj, dict):
        return {str(k): _plain(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [_plain(v) for v in obj]
    return obj


def _utc_arg(text):
    t = gaps.parse_time(text)
    if t is None:
        raise argparse.ArgumentTypeError(f"not a time: {text!r}")
    return t


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("log_dir")
    ap.add_argument("--last-open", required=True, type=_utc_arg,
                    help="open time (UTC) of the last candle counted, e.g. '2026-11-14 04:00'")
    ap.add_argument("--first-open", type=_utc_arg, default=FIRST_OPEN)
    ap.add_argument("--code-hash", default=None, help="a full hash or a prefix naming one")
    ap.add_argument("--process-log", default=None,
                    help="default: phase7_engine.log in the log folder")
    ap.add_argument("--json", default=None)
    args = ap.parse_args(argv)
    for name in ("first_open", "last_open"):
        t = getattr(args, name)
        if t != floor_open(t):
            ap.error(f"--{name.replace('_', '-')} is not a 4h open: {t}")
    logs = gaps.read_logs(args.log_dir)
    process = read_process_log(args.process_log or os.path.join(args.log_dir, "phase7_engine.log"))
    res = count(logs, process, args.last_open, first_open=args.first_open,
                code_hash=args.code_hash)
    print(report(res))
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(_plain(res), f, indent=1, sort_keys=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
