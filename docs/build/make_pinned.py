#!/usr/bin/env python3
"""
Generates the pinned dataset for sequence item 3.

Three series, because the engine fetches three and pinning only one leaves two
thirds of a run still dependent on the network:

    AEROUSDT_4h.csv   the base series      (engine_core.py:499)
    AEROUSDT_1d.csv   the macro series     (engine_core.py:524, MACRO_TIMEFRAME)
    BTCUSDT_4h.csv    the BTC context      (engine_core.py:682)

SYNTHETIC, NOT CAPTURED — and that is a decision rather than a shortcut.

A pinned dataset exists to make runs comparable. A real market capture would be
more representative today and would raise, forever after, the question of
whether it still is: markets move, and a snapshot from August 2026 becomes a
snapshot of August 2026. This data only ever has to be *stable*. Regenerating
it from the seeds below produces byte-identical files indefinitely, with no
network, no exchange, no vendor and no expiry.

If a real capture is wanted later, drop it into the same directory under the
same filenames. The mechanism does not care where the numbers came from — which
is why the manifest records origin explicitly rather than assuming.

The base series is the harness's existing ohlcv_clean_4h.csv with one column
added (stage 1 of the redesign, 14 November 2026; draft section 5):
quote_volume, the candle's turnover in USDT, which the liquidity floor reads
from stage 3 on. The pinned candles are synthetic, so the column is too: it is
volume x close, candle by candle, rounded to four decimals as volume is. The
five columns the file had are unchanged. The macro and BTC series do not carry
the column; nothing reads it on them.
"""

import csv
import hashlib
import json
import os
import random
from datetime import datetime, timezone

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "tests", "fixtures", "pinned")
SOURCE_4H = os.path.join(os.path.dirname(OUT), "ohlcv_clean_4h.csv")

FOUR_HOURS_MS = 4 * 60 * 60 * 1000
ONE_DAY_MS = 24 * 60 * 60 * 1000


def read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


COLUMNS = ["timestamp", "open", "high", "low", "close", "volume"]


def write_csv(path, rows, extra=()):
    """`extra` names columns written after the six every series has."""
    columns = COLUMNS + list(extra)
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(columns)
        for r in rows:
            w.writerow([r[c] for c in columns])


def with_quote_volume(rows):
    """
    The rows with quote_volume = volume x close, to four decimals.

    The cells are read as the file wrote them and written back untouched; only
    the new cell is computed. repr() of the rounded float is Python's shortest
    round-trip form, the same on every platform.
    """
    out = []
    for r in rows:
        r = dict(r)
        r["quote_volume"] = repr(round(float(r["volume"]) * float(r["close"]), 4))
        out.append(r)
    return out


def synth(seed, start_ms, step_ms, count, start_price, drift, vol, vol_base):
    """
    A deterministic OHLCV walk. Same seed, same numbers, forever.

    Constraints enforced so the series is clean by the engine's own standards:
    high >= max(open, close), low <= min(open, close), all prices positive,
    volume positive, timestamps strictly increasing on an exact grid, and the
    last candle closed (the caller picks start_ms so it lands in the past).
    """
    rng = random.Random(seed)
    rows = []
    price = start_price
    ts = start_ms
    for _ in range(count):
        o = price
        move = o * (drift + rng.gauss(0.0, vol))
        c = max(o + move, o * 0.5)
        hi = max(o, c) * (1.0 + abs(rng.gauss(0.0, vol * 0.6)))
        lo = min(o, c) * (1.0 - abs(rng.gauss(0.0, vol * 0.6)))
        v = vol_base * (0.5 + rng.random() * 1.5)
        rows.append({
            "timestamp": ts,
            "open": round(o, 8),
            "high": round(hi, 8),
            "low": round(lo, 8),
            "close": round(c, 8),
            "volume": round(v, 4),
        })
        price = c
        ts += step_ms
    return rows


def sha256(path):
    """
    sha256 of the file's content with CRLF line endings normalised to LF.

    Not the raw bytes. .gitattributes sets `* text=auto`, so git stores these
    CSVs with LF and checks them out with CRLF on Windows and LF on Linux and
    macOS: the same committed file has different raw bytes per platform. A
    raw-byte hash therefore matched only the platform that generated the
    manifest, and tests/test_pinned_source.py failed on every other one.
    Hashing the LF form gives one hash per content, on every checkout, and
    still changes the moment a value in the file does.

    tests/test_pinned_source.py carries its own copy of this function (it
    cannot import this module, which writes files when imported). The two must
    stay identical; test_manifest_hash_ignores_line_endings checks the test's
    copy.
    """
    with open(path, "rb") as f:
        data = f.read()
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


os.makedirs(OUT, exist_ok=True)

# --- base series: the harness fixture, with quote_volume added ------------
base = read_csv(SOURCE_4H)
write_csv(os.path.join(OUT, "AEROUSDT_4h.csv"), with_quote_volume(base),
          extra=["quote_volume"])

base_start = int(base[0]["timestamp"])
base_end = int(base[-1]["timestamp"])

# --- macro series: 1d, covering the same window ---------------------------
# 450 four-hour candles is 75 days; 120 daily candles covers it with headroom,
# starting earlier so the macro view has history before the base series opens.
macro_start = base_start - (45 * ONE_DAY_MS)
macro = synth(seed=20260829, start_ms=macro_start, step_ms=ONE_DAY_MS,
              count=120, start_price=0.48, drift=0.0012, vol=0.021,
              vol_base=1_450_000.0)
write_csv(os.path.join(OUT, "AEROUSDT_1d.csv"), macro)

# --- BTC context: 4h, same grid as the base series ------------------------
# Deliberately its own walk rather than a transform of the base series. The
# golden-path test's first version returned the same frame for every symbol,
# which made the asset perfectly correlated with itself and reported beta
# 1.00x — a number that said nothing. An independent series gives the BTC
# context something real to measure.
btc = synth(seed=20260830, start_ms=base_start, step_ms=FOUR_HOURS_MS,
            count=len(base), start_price=61_500.0, drift=-0.0004, vol=0.009,
            vol_base=880.0)
write_csv(os.path.join(OUT, "BTCUSDT_4h.csv"), btc)

# --- manifest: hashes and origin, per sequence item 3 ---------------------
files = sorted(f for f in os.listdir(OUT) if f.endswith(".csv"))
manifest = {
    "dataset": "phase7-pinned-v1",
    "generated_by": "docs/build/make_pinned.py",
    "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "origin": "synthetic — deterministic, generated from fixed seeds",
    "why_synthetic": (
        "A pinned dataset only has to be stable. A real capture would be more "
        "representative on the day it was taken and would afterwards raise the "
        "question of whether it still is. Regenerating from the seeds produces "
        "byte-identical files indefinitely."
    ),
    "reproduce": "python docs/build/make_pinned.py",
    "closed_candles_only": True,
    "sha256_over": "file content with CRLF normalised to LF, not raw bytes",
    "series": [],
}
for name in files:
    path = os.path.join(OUT, name)
    rows = read_csv(path)
    symbol, timeframe = name[:-4].split("_", 1)
    manifest["series"].append({
        "file": name,
        "symbol": symbol,
        "timeframe": timeframe,
        "candles": len(rows),
        "first_timestamp_ms": int(rows[0]["timestamp"]),
        "last_timestamp_ms": int(rows[-1]["timestamp"]),
        "sha256": sha256(path),
        "source": ("tests/fixtures/ohlcv_clean_4h.csv, with quote_volume = "
                   "volume x close added"
                   if name == "AEROUSDT_4h.csv"
                   else "generated by make_pinned.py"),
    })

with open(os.path.join(OUT, "MANIFEST.json"), "w") as f:
    json.dump(manifest, f, indent=2)
    f.write("\n")

print(f"wrote {len(files)} series to {OUT}")
for s in manifest["series"]:
    print(f"  {s['file']:<18} {s['candles']:>4} candles  {s['sha256'][:16]}…")
