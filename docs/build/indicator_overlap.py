"""
Indicator overlap and decision impact, measured with the engine's own functions.

Written 24 October 2026, at Viktor's request, from the two scripts behind the
document "Understanding the Phase-7 Engine" (kept outside this repository, in
G:\\Phase_7_Engine_Random_Files\\Docs\\02_Reviews_and_Feedback). It answers two of
that document's three questions and leaves the third alone:

  1. Are the indicators duplicated?        Base rates, agreement corrected for
                                            chance (Cohen's kappa), correlations.
  2. Does that change the engine's          The full decision path per bar, as
     decisions?                             the engine is and with each disputed
                                            factor removed.
  3. Would changing it make the decisions  NOT ANSWERED HERE. That needs what price
     better?                                did afterwards, which is backtesting,
                                            closed by the ruling of 29 September.

WHAT IT READS. Archived runs from logs/archive/ (one per pair is enough: each
holds 449 4h candles and 100 daily candles), and optionally the live decision
logs, to check that its baseline reproduces the actions the engine logged. For
every bar from the 151st to the last it runs the engine's own
add_technical_indicators, calculate_structure, compute_trend_health,
calculate_dynamic_bias, calculate_entry_quality, generate_entry_signals, the
risk model and DecisionModel.evaluate on the candles up to that bar. Nothing
after the bar is read: tests/test_indicator_overlap_tool.py changes every candle
after a bar and checks that the bar's row does not move.

WHAT IT DOES NOT MODEL. Degradation. A degraded run blocks every trade whatever
the factors say, so it is left out rather than counted as a change; the
comparison with the logs skips degraded records for the same reason. And the
BTC context, which decides nothing since N5.

THE INDICATORS ARE COMPUTED ONCE PER PAIR, on the whole archived frame, and the
frame is then cut at each bar. Every indicator the engine uses reads only the
past, so the cut frame equals what the engine computes on candles up to that
bar, except for the first values of each EMA, which start from the frame's
first candle rather than the fetch's. On the last bar the two are identical,
which is what the golden test below checks.

MACRO uses the daily candles that had closed when the 4h bar closed: open plus
one day at or before the bar's open plus four hours. The engine reads the same
candles (it drops the daily candle still forming). The scripts behind version 2
of the document used open plus one day at or before the bar's OPEN, which
leaves out the daily candle that closes with a 20:00 bar. On the archives of 23 October
the engine's rule gives 2,980 bars where the old one gave 2,970, and every
figure moves a little without changing a conclusion: for example, removing the
four disputed bias factors with today's cutoffs cuts trade actions by 35.5%
(1,333 to 860) where version 2 says 37% (1,324 to 841), and the baseline
matches the engine's logged action on 197 of 197 records where it says 196 of
196 (Linux sandbox, 24 October 2026).

4h only (DECISIONS, "Ruling, 20 October 2026 — B5: 4h only for now"): the tool
refuses another timeframe in config rather than guess its bar length.

This is documentation tooling. It lives under docs/, which the code fingerprint
does not read, and it changes nothing the engine decides.

    python docs/build/indicator_overlap.py logs/archive
    python docs/build/indicator_overlap.py logs/archive --logs logs --csv rows.csv
"""

import argparse
import contextlib
import glob
import gzip
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import numpy as np
import pandas as pd

from core import config, lineage
import models.bias_engine as bias_engine

WARMUP = 150
BAR = pd.Timedelta(hours=4)
DAY = pd.Timedelta(days=1)
MIN_DAILY_FOR_MACRO = 50          # the daily EMA 50 needs this many candles

WEIGHTS = ("WEIGHT_TREND_HEALTH", "WEIGHT_STRUCTURE_REGIME", "WEIGHT_VOLUME_SENTIMENT",
           "WEIGHT_SUPERTREND_DIRECTION", "WEIGHT_MACRO_BIAS", "WEIGHT_REVERSAL_CONTINUATION")
FOUR = ("WEIGHT_STRUCTURE_REGIME", "WEIGHT_VOLUME_SENTIMENT",
        "WEIGHT_SUPERTREND_DIRECTION", "WEIGHT_REVERSAL_CONTINUATION")

# name -> (weights set to zero, weights set to a new value, entry mode)
VARIANTS = {
    "baseline": ((), {}, "as is"),
    "no continuation": (("WEIGHT_REVERSAL_CONTINUATION",), {}, "as is"),
    "no SuperTrend": (("WEIGHT_SUPERTREND_DIRECTION",), {}, "as is"),
    "no structure regime (bias only)": (("WEIGHT_STRUCTURE_REGIME",), {}, "as is"),
    "no volume sentiment": (("WEIGHT_VOLUME_SENTIMENT",), {}, "as is"),
    "all four removed, cutoffs unchanged": (FOUR, {}, "as is"),
    "all four removed, rescaled to 100": (FOUR, {"WEIGHT_TREND_HEALTH": 0.75,
                                                  "WEIGHT_MACRO_BIAS": 0.25}, "as is"),
    "entry: no trend multiplier": ((), {}, "no trend multiplier"),
    "entry: no macro multiplier": ((), {}, "no macro multiplier"),
    "entry: EMA zone + ATR + VWMA as one": ((), {}, "one distance"),
}


def current_weights():
    return {name: getattr(bias_engine, name) for name in WEIGHTS}


@contextlib.contextmanager
def bias_weights(zero=(), set_to=None):
    """The bias engine's weights for one variant, restored whatever happens."""
    saved = current_weights()
    try:
        for name in zero:
            setattr(bias_engine, name, 0.0)
        for name, value in (set_to or {}).items():
            setattr(bias_engine, name, value)
        yield
    finally:
        for name, value in saved.items():
            setattr(bias_engine, name, value)


def frames_from_archive(path):
    """(symbol, 4h frame, daily frame) from one archived run."""
    with gzip.open(path, "rb") as f:
        payload = json.load(f)
    frames = payload["frames"]
    return (payload["symbol"],
            lineage.rebuild_frame(frames["struct"]["canonical"]),
            lineage.rebuild_frame(frames["macro"]["canonical"]))


def macro_at(daily_ind, bar_open):
    """The macro reading at a 4h bar, from daily candles closed when it closed,
    or None when fewer than MIN_DAILY_FOR_MACRO had."""
    closed = daily_ind[daily_ind.index + DAY <= bar_open + BAR]
    if len(closed) < MIN_DAILY_FOR_MACRO:
        return None
    close, ema = float(closed["close"].iloc[-1]), float(closed["EMA_50"].iloc[-1])
    if not (math.isfinite(close) and math.isfinite(ema)):
        return None
    return "BULLISH" if close > ema else "BEARISH" if close < ema else "NEUTRAL"


def _entry_score(eq, mode):
    if mode == "no trend multiplier":
        score = eq["base_score"] * eq["macro_multiplier"] * eq["structure_multiplier"]
    elif mode == "no macro multiplier":
        score = eq["base_score"] * eq["trend_multiplier"] * eq["structure_multiplier"]
    elif mode == "one distance":
        # EMA zone (30) carries the 75 points of the three distance parts.
        base = (eq["ema_pos_pts"] * 75.0 / 30.0) + eq["rsi_pts"] + eq["struct_pts"]
        score = base * eq["combined_multiplier"]
    else:
        return eq["score"]
    return float(min(100.0, max(0.0, score)))


def bar_row(frame_ind, daily_ind, t, variants=VARIANTS):
    """
    One bar's readings and, for each variant, the engine's action. frame_ind is
    the 4h frame with indicators added; t is the bar's position. Returns None
    when macro cannot be read at that bar.
    """
    from indicators.trend_health import compute_trend_health
    from structure.structure import calculate_structure
    from models.entry_model import calculate_entry_quality, generate_entry_signals
    from models.risk_model import RiskModel
    from models.decision_model import DecisionModel
    from core.engine_core import macro_agreement, volume_agreement

    df = frame_ind.iloc[: t + 1]
    bar_open = df.index[-1]
    macro = macro_at(daily_ind, bar_open)
    if macro is None:
        return None
    s = calculate_structure(df, lookback=config.STRUCT_LOOKBACK,
                            volume_profile_bins=config.VOLUME_PROFILE_BINS)
    dfs = s["df"]
    tr = compute_trend_health(dfs)
    supertrend = float(dfs["ST_Direction"].iloc[-1])
    kw = dict(trend_sequence=s["sequence"], trend_health=tr["trend_health"],
              trend_exhaustion=tr["trend_exhaustion"], reversal_direction=tr.get("reversal_direction"),
              reversal_strength=tr["reversal_strength"], continuation_strength=tr.get("continuation_strength"),
              trend_direction_sign=tr["trend_direction_sign"], structure_regime=s["regime"],
              volume_sentiment=s["volume_sentiment"], supertrend_direction=supertrend, macro_bias=macro)
    _, volatility = bias_engine.calculate_dynamic_regime(dfs)
    signals = generate_entry_signals(structure_regime=s["regime"], momentum_divergence=tr["momentum_divergence"],
                                     divergence_direction=tr["divergence_direction"], adx=tr["adx"])
    lo, hi = sorted([float(dfs["EMA_20"].iloc[-1]), float(dfs["EMA_50"].iloc[-1])])
    price, atr = float(dfs["close"].iloc[-1]), float(dfs["ATR"].iloc[-1])
    slope = (float(dfs["EMA20_Slope"].iloc[-1]) + float(dfs["EMA50_Slope"].iloc[-1])) / 2.0
    vwma = float(dfs["VWMA"].iloc[-1])
    risk_model, decision_model = RiskModel(), DecisionModel()

    row = {"bar": str(bar_open), "close": price, "macro": macro}
    for name, (zero, set_to, entry_mode) in variants.items():
        components = {}
        with bias_weights(zero, set_to):
            raw, score = bias_engine.calculate_dynamic_bias(components=components, **kw)
        side = "LONG" if raw == "BULLISH" else "SHORT" if raw == "BEARISH" else ("LONG" if score >= 0 else "SHORT")
        eq = calculate_entry_quality(dfs, lo, hi, macro_bias=macro, trade_direction=side,
                                     trend_direction=tr["trend_direction"], structure_sequence=s["sequence"])
        entry_score = _entry_score(eq, entry_mode)
        stop, t1, t2, t3 = risk_model.calculate_stop_targets(current_price=price, atr_val=atr,
                                                            bias_score=score, volatility_state=volatility)
        valid, reason, regime = risk_model.validate_risk_parameters(current_price=price, atr_stop=stop,
                                                                    volatility_state=volatility)
        validation = 50.0 + macro_agreement(macro, raw)[0] + volume_agreement(s["volume_sentiment"], raw)[0]
        validation = max(0.0, min(100.0, validation))
        state = "STRONG" if validation >= 70 else "NEUTRAL" if validation >= 45 else "WEAK"
        out = decision_model.evaluate(
            bias={"raw": raw, "score": score},
            trend={"trend_health": tr["trend_health"], "trend_direction_sign": tr["trend_direction_sign"]},
            entry={"score": entry_score, "entry_status": eq["entry_status"],
                   **{k: signals[k] for k in ("long_signal", "short_signal",
                                              "long_signal_blockers", "short_signal_blockers")}},
            risk={"risk_valid": valid, "risk_reason": reason, "risk_regime": regime,
                  "validation_state": state, "atr_stop": stop, "targets": (t1, t2, t3)},
            degradation=[])
        row[f"action | {name}"] = out["final_action"]
        row[f"bias score | {name}"] = float(score)
        if name == "baseline":
            factors = components["factors"]
            row.update({
                "trend sign": int(tr["trend_direction_sign"]),
                "structure": factors["structure_regime"]["signed"],
                "volume": factors["volume_sentiment"]["signed"],
                "SuperTrend": factors["supertrend_direction"]["signed"],
                "macro sign": factors["macro_bias"]["signed"],
                "continuation": factors["reversal_continuation"]["signed"],
                "trend health": float(tr["trend_health"]), "ADX": float(tr["adx"]) if tr["adx"] is not None else math.nan,
                "slope %": slope, "raw bias": raw, "entry score": float(eq["score"]),
                "EMA zone pts": eq["ema_pos_pts"], "ATR distance pts": eq["atr_dist_pts"],
                "VWMA pts": eq["vwma_pts"], "RSI pts": eq["rsi_pts"], "HVN pts": eq["struct_pts"],
                "band distance %": eq["distance_from_zone"],
                "VWMA distance %": abs(price - vwma) / price * 100.0,
                "multiplier": eq["combined_multiplier"],
            })
    return row


def pair_rows(symbol, frame, daily, warmup=WARMUP, last=None):
    """Every bar's row for one pair, from bar `warmup` to `last` (default: all)."""
    from indicators.indicators import add_technical_indicators
    frame_ind, _ = add_technical_indicators(frame)
    daily_ind, _ = add_technical_indicators(daily)
    end = len(frame_ind) if last is None else min(last, len(frame_ind))
    rows = []
    for t in range(warmup, end):
        row = bar_row(frame_ind, daily_ind, t)
        if row is not None:
            row["pair"] = symbol
            rows.append(row)
    return rows


# --- statistics -------------------------------------------------------------

def kappa(a, b):
    """(observed agreement, chance agreement, Cohen's kappa) of two label series.
    Every distinct value is its own state, flat included; NaN pairs are dropped."""
    a, b = pd.Series(a, dtype=float), pd.Series(b, dtype=float)
    keep = a.notna().to_numpy() & b.notna().to_numpy()
    a, b = a.to_numpy()[keep], b.to_numpy()[keep]
    if len(a) == 0:
        return math.nan, math.nan, math.nan
    observed = float(np.mean(a == b))
    chance = float(sum(np.mean(a == v) * np.mean(b == v) for v in np.union1d(a, b)))
    k = math.nan if chance == 1.0 else (observed - chance) / (1.0 - chance)
    return observed, chance, k


def side(action):
    """LONG or SHORT for an action that takes one, otherwise None."""
    if action.startswith("NO-TRADE"):
        return None
    return "LONG" if "LONG" in action else "SHORT" if "SHORT" in action else None


def impact(rows):
    """{variant: {"changed", "trades", "flipped", "trade to none", "none to trade"}}"""
    base = [r["action | baseline"] for r in rows]
    out = {}
    for name in VARIANTS:
        acts = [r[f"action | {name}"] for r in rows]
        b_sides, v_sides = [side(x) for x in base], [side(x) for x in acts]
        out[name] = {
            "changed": sum(x != y for x, y in zip(base, acts)),
            "trades": sum(s is not None for s in v_sides),
            "flipped": sum(bs is not None and vs is not None and bs != vs for bs, vs in zip(b_sides, v_sides)),
            "trade to none": sum(bs is not None and vs is None for bs, vs in zip(b_sides, v_sides)),
            "none to trade": sum(bs is None and vs is not None for bs, vs in zip(b_sides, v_sides)),
        }
    return out


def compare_with_logs(rows, records, code_hash):
    """
    The baseline against the engine's own logged actions. `records` are decision
    log records (dicts as written). Only live, non-degraded records at
    `code_hash` are compared. Returns (compared, matched, mismatches).
    """
    by_bar = {(r["pair"], r["bar"]): r["action | baseline"] for r in rows}
    compared = matched = 0
    mismatches = []
    for rec in records:
        d = rec.get("decision", {})
        pv = d.get("provenance", {})
        if pv.get("code_hash") != code_hash or pv.get("fetch", {}).get("pinned"):
            continue
        if d.get("degradation", {}).get("degraded"):
            continue
        key = (d.get("symbol"), pv.get("last_candle"))
        if key not in by_bar:
            continue
        compared += 1
        if by_bar[key] == d["exit"]["action"]:
            matched += 1
        else:
            mismatches.append((key, by_bar[key], d["exit"]["action"]))
    return compared, matched, mismatches


def summarise(rows):
    """The report, as text."""
    d = pd.DataFrame(rows)
    lines = [f"bars: {len(d)}   pairs: {d['pair'].nunique()}   from {d['bar'].min()} to {d['bar'].max()}", ""]
    factors = ["trend sign", "structure", "volume", "SuperTrend", "macro sign", "continuation"]
    lines.append("== how often each factor points up / flat / down (%)")
    for f in factors:
        v = np.sign(d[f].astype(float))
        lines.append(f"  {f:14s} {np.mean(v > 0) * 100:5.1f} {np.mean(v == 0) * 100:5.1f} {np.mean(v < 0) * 100:5.1f}")
    lines += ["", "== agreement with flat as its own state: observed, by chance, kappa"]
    for i, a in enumerate(factors):
        for b in factors[i + 1:]:
            o, c, k = kappa(np.sign(d[a].astype(float)), np.sign(d[b].astype(float)))
            lines.append(f"  {a:14s} {b:14s} {o * 100:5.1f}% {c * 100:5.1f}%  {k:+.2f}")
    has_side = d["raw bias"] != "NEUTRAL"
    lines += ["", f"== raw bias's side equals the EMA slope's sign on "
                  f"{np.mean(np.sign(d['bias score | baseline'][has_side]) == np.sign(d['trend sign'][has_side])) * 100:.1f}% "
                  f"of the {int(has_side.sum())} bars where it has a side"]
    lines += ["", "== thresholds: share of bars that pass"]
    for label, mask in (("trend health >= 75", d["trend health"] >= 75), ("trend health >= 50", d["trend health"] >= 50),
                        ("trend health < 40", d["trend health"] < 40), ("ADX >= 20", d["ADX"] >= 20),
                        ("|bias score| >= 30", d["bias score | baseline"].abs() >= 30),
                        ("entry score >= 70", d["entry score"] >= 70)):
        lines.append(f"  {label:22s} {mask.mean() * 100:5.1f}%")
    parts = ["EMA zone pts", "ATR distance pts", "VWMA pts", "RSI pts", "HVN pts"]
    lines += ["", "== entry quality's parts: correlations", d[parts].corr().round(2).to_string()]
    lines += ["", "== decision impact (actions changed; trade actions after; side flipped)"]
    for name, r in impact(rows).items():
        lines.append(f"  {name:38s} {r['changed']:6d}  {r['trades']:6d}  {r['flipped']:4d}")
    return "\n".join(lines)


def _read_records(log_dir):
    records = []
    for path in sorted(glob.glob(os.path.join(log_dir, "phase7_decision_log_*.jsonl"))):
        with open(path, encoding="utf-8") as f:
            for line in f:
                try:
                    records.append(json.loads(line))
                except ValueError:
                    continue
    return records


def main(argv=None):
    import logging
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("archive_dir", help="logs/archive, or any folder of archived runs")
    parser.add_argument("--logs", help="the folder of live decision logs, to check the baseline against them")
    parser.add_argument("--csv", help="also write every bar's row here")
    args = parser.parse_args(argv)
    if config.TIMEFRAME != "4h":
        raise SystemExit(f"4h only; config.TIMEFRAME is {config.TIMEFRAME!r}")
    logging.disable(logging.CRITICAL)

    newest = {}
    for path in glob.glob(os.path.join(args.archive_dir, "*_4h_*.json.gz")):
        pair = os.path.basename(path).split("_")[0]
        if pair not in newest or os.path.getmtime(path) > os.path.getmtime(newest[pair]):
            newest[pair] = path
    if not newest:
        raise SystemExit(f"no archived 4h runs in {args.archive_dir}")
    rows = []
    for pair in sorted(newest):
        symbol, frame, daily = frames_from_archive(newest[pair])
        rows += pair_rows(symbol, frame, daily)
        print(f"  {symbol}: {os.path.basename(newest[pair])}", file=sys.stderr)
    print(summarise(rows))
    if args.logs:
        from core.code_fingerprint import code_fingerprint
        compared, matched, mismatches = compare_with_logs(rows, _read_records(args.logs),
                                                          code_fingerprint()["code_hash"])
        print(f"\n== baseline vs the engine's logged action, live and not degraded, this code_hash: "
              f"{matched} of {compared} the same")
        for key, ours, logged in mismatches[:20]:
            print(f"  {key}: here {ours!r}, logged {logged!r}")
    if args.csv:
        pd.DataFrame(rows).to_csv(args.csv, index=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
