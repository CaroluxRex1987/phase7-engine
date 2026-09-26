# Run 1 — DeepSeek V4 Pro, blind source-only review

OpenRouter, 2026-08-27. Source code only: no Constitution, no audit package,
no indication that a standard existed. Ten ranked findings.
Recovered from the conversation after the OpenRouter room was deleted.

---

Ranked findings
1. `trend_failure` is permanently `False` — a whole risk gate silently never fires
`indicators/trend_health.py :: compute_trend_health` (section 3) and `core/engine_core.py :: run` both treat this as a real signal, but the data it reads can never contain the values it checks.

```python
recent_struct = df["STRUCTURE"].tail(5)
trend_failure = bool(
    (recent_struct == "LH").sum() > 0 or
    (recent_struct == "LL").sum() > 0
)

```

`STRUCTURE` is written by `structure/structure.py :: calculate_structure`:

```python
df_clean.loc[:, "STRUCTURE"] = result.get("regime", "NEUTRAL STRUCTURE")

```

and `_detect_regime` only ever returns `"BULLISH TREND"`, `"BEARISH TREND"`, or `"NEUTRAL STRUCTURE"`. The strings `"LH"`/`"LL"` never appear. So `trend_failure` is `False` on every run, and so are the two fallback dicts in the same file. This is not cosmetic. `trend_failure` feeds three places:

* `models/entry_model.py :: generate_entry_signals` — `if trend_failure or trend_exhaustion or reversal_strength > 0: return False, False`. The failure block is dead.
* `models/bias_engine.py :: calculate_dynamic_bias` — `if trend_failure or choch_against_trend: bias_score *= 0.5`. The failure discount is dead.
* `models/exit_model.py :: build_exit_watch` — "Trend failure is active" flag can never appear. The funny part is that the underlying information the check was trying to use does now exist: `structure/_detect_sequence()` computes real HH/HL/LH/LL swing structure and real BOS/CHOCH. It's just never wired into `trend_failure`. Net effect: the engine reports "trend not failing" as a meaningful analysis even when a genuine lower-high/lower-low sequence has formed. This is exactly the "wrong numbers that look plausible" category, and it's the highest-damage finding because it touches entry gating, bias, and exit advice simultaneously.

2. Indicator failures are replaced with fabricated, directional numbers, with no marker on the panel
`indicators/indicators.py :: add_technical_indicators` has a fallback for every indicator, and the fallbacks are plausible constants or raw-price substitutes, not "missing":

* `ADX = 25.0`, `DIP = 25.0`, `DIM = 25.0` on ADX failure
* `RSI = 50.0` on RSI failure
* `ATR = close * 0.02` on ATR failure
* `SuperTrend = close`, `ST_Direction = 1.0` on SuperTrend failure
* `EMA_20/50 = close` on EMA failure The SuperTrend one is the dangerous one. `core/engine_core.py :: run` extracts `supertrend_direction = float(df_struct["ST_Direction"].iloc[-1])` and passes it into `models/bias_engine.py :: calculate_dynamic_bias`, where a positive direction is scored as `+100.0` at weight `0.15`. So when SuperTrend fails to compute, the engine silently injects a permanent $+15$-point bullish vote into the bias score, regardless of what the market is doing. A failed indicator produces a directional opinion, not a neutral "unknown". `compute_trend_health` has the same pattern: any internal exception returns


```python
"trend_health": 50.0, "trend_failure": False, "trend_exhaustion": False, ...

```

and `engine_core.py` has a second, matching fallback dict. The panel then prints these as if measured (`Score: 50.00`). There is no "degraded/unavailable" state anywhere in the panel for indicators or trend health — only the top-level data-fetch error path (which is handled properly in `data_fetcher.py :: get_tf`) gets one. `risk_model.py :: calculate_stop_targets` has the same disease in its `except`:

```python
return (
    float(current_price * 0.99),
    float(current_price * 1.01),
    float(current_price * 1.02),
    float(current_price * 1.03)
)

```

This fallback is direction-blind: it always puts the stop below price and targets above, so if it ever fires while the engine is in a SHORT context, the displayed stop is on the wrong side of price. It's unlikely to fire (the main guard raises first), but it is a latent silently-wrong path.
3. The exit logic is computed and then thrown away
`core/engine_core.py :: run` step 9 calls:

```python
exit_data = compute_exit(price_data=df_struct, entry_data=entry, risk_data=risk)

```

`models/exit_model.py :: compute_exit` does real work — prioritizing stop-loss, then T3/T2/T1, setting `final_action`, `exit_reason`, `exit_status`. Then `models/signal_router.py :: _build_decision_object` ignores everything except `exit_data.get("current_price")`, and the panel's `DECISION` line comes from `models/decision_model.py :: DecisionModel._determine_final_action`, which never looks at `exit_data` at all. Consequence: the panel can never display `STOP LOSS HIT`, `TARGET 1/2/3 HIT`, or any exit state. On a run where `compute_exit` would say "TARGET 3 HIT", the panel still prints whatever `DecisionModel` says (e.g. `LONG`). The exit model is dead code wearing the costume of a live feature. A reader of the code who sees `compute_exit` and its careful comment about "prioritizing stop loss first" would reasonably expect those outcomes to appear in the output; they do not. This also reveals the program's actual capability boundary: it has no notion of a held position, so "exit" can never be more than a snapshot of the current bar against computed levels. `live_trading.py`'s simulated order likewise reads `exit_data.get("action")`, which is `DecisionModel`'s action, not `compute_exit`'s — so the simulated order's `"decision"` field is "LONG"/"WAIT", never "target hit". That works, but it doesn't reflect the exit model the file is named for.
4. The panel asserts things that are not true
`core/panel_render.py :: render_panel` ends with:

```python
f"Trade logged to Logs/phase7_trade_log_{symbol.lower()}.csv\n"

```

No code anywhere in the repository writes `phase7_trade_log_*.csv`. The only string matches for `phase7_trade_log` are this print. `config.TRADE_LOG_DIR = "Logs/Trades/"` is also never used. Every single run prints "Trade logged" while nothing is logged. That is a false output statement to whoever reads the terminal. Same file:

```python
f"AI Risk chart saved to {decision.get('chart_path', 'Logs/Charts/chart.png')}\n"

```

`engine_core.py` sets `decision_object["chart_path"] = chart_path` where `chart_path` is `None` when `save_chart=False` or `plot_engine_chart` returns `None`. Since the key exists with value `None`, the `.get(..., default)` default never applies; `signal_router.py` then does `str(chart_path)` → `"None"`, and the panel prints:

```
AI Risk chart saved to None

```

5. The configuration file mostly doesn't configure anything; adjacent cases break
`core/config.py` defines `EMA_FAST`, `EMA_SLOW`, `RSI_LENGTH`, `ADX_LENGTH`, `ATR_LENGTH`, `BB_LENGTH`, `BB_STD`, `VWMA_LENGTH`, `KAMA_LENGTH`, `VOLUME_PROFILE_BINS`, `CHART_WIDTH/HEIGHT/DPI/STYLE`. None of them are honored:

* `indicators/indicators.py :: add_technical_indicators` hardcodes 14/14/14, 20/50, 20/2.0, 20, 10.
* `structure/structure.py :: calculate_structure` constructs `StructureEngine()` with the default `50` bins instead of passing `config.VOLUME_PROFILE_BINS`.
* `utils/plotting.py :: plot_engine_chart` hardcodes `figsize=(14, 8)`, `dpi=200`, and `plt.style.use("dark_background")`. So a reader who "changes the settings in config.py" — the obvious thing to do — gets no effect for those knobs, silently. (Only `STRUCT_LOOKBACK`, `SUPERTREND_LENGTH/MULT`, and the account/risk constants are actually wired in.) Adjacent-case breakage, same file: `config.TIMEFRAME = "4h"` works, but MEXC's kline endpoint accepts `60m`, not `1h` (see the ccxt issue `mexc spot interval mapping wrong for 1h`). Change `TIMEFRAME` to `"1h"` and the fetch returns an error silently (it becomes the `get_tf` "data fetch failed" state), rather than working. The code was written for exactly the two configured values. And `requirements.txt` is wrong: it lists `pandas, numpy, matplotlib, ccxt, pandas_ta`, but `data/data_fetcher.py` does `import requests`, which is not listed. A fresh `pip install -r requirements.txt` leaves the engine unable to run (`main.py` will catch the ImportError and return 1, so it degrades to "unusable" rather than crashing, but it's still a broken dependency manifest). `ccxt` is listed and never imported anywhere.

6. State machines that don't keep state
`structure/structure.py :: StructureEngine._detect_regime` is written around a hysteresis `_last_regime` that is supposed to "prevent whipsaws." But `calculate_structure` does `engine = StructureEngine()` on every call, and the pipeline calls `analyze()` once per run. `_last_regime` therefore always starts at `"NEUTRAL STRUCTURE"` and the hysteresis branches are unreachable in practice. Across CLI runs it's also a fresh object, so the claimed persistence never happens. `models/bias_engine.py :: BiasStateMachine.transition` is even more bluntly stateless:

```python
def transition(self, raw_bias, bias_score):
    if raw_bias == "BULLISH" and bias_score > 30:
        self.state = "BULLISH CONFIRMED"
    elif ...

```

It assigns `self.state` but never reads the prior value. It's a pure function wearing a state-machine costume. Not harmful output, but it misleads anyone maintaining the code into thinking there's confirmation logic across runs when there is none.
7. The chart is partially a lie
`utils/plotting.py :: plot_engine_chart`:

```python
if "VWAP" in df.columns and not df["VWAP"].isna().all():
    ax.plot(df.index, df["VWAP"], label="VWAP", ...)

```

But `indicators/indicators.py` creates a column named `VWMA`, never `VWAP`. The VWAP line is silently never drawn, even though the function's docstring says "Draws: ... VWAP." The candle bodies are drawn with `ax.bar(..., width=0.0008)` on a matplotlib date axis, where one unit is one day. For the default `4h` timeframe (0.167 days per bar), `0.0008` days is about 1/200th of a bar width. The rendered chart shows wicks with effectively invisible bodies. It's a visual defect, not a numeric one, but the person reading the chart will be misled about what the candles look like.
8. LVN from the volume profile is essentially a range edge, and HVN is used as a hard stop level
`indicators/volume_profile.py :: compute_volume_profile` bins price and distributes each candle's volume proportionally across overlapped bins. Bins between `price_min` and the first traded price (and above the last traded price) legitimately end at zero volume. Then:

```python
lvn_idx = profile.idxmin()
lvn = float(centers.loc[lvn_idx])

```

`idxmin()` returns the first minimum, which is the first zero-volume bin — i.e. the bottom edge of the entire price range, not a "low volume node" in any useful sense. The LVN printed in `exit_watch` proximity checks (`exit_model.py :: build_exit_watch`) is therefore usually meaningless (bottom of the whole window, where price very rarely sits). Related: in `risk_model.py :: calculate_stop_targets`, `structural_level` (which is the HVN) is used to set the stop via `min(structural_level, calculated_stop)` for longs / `max(...)` for shorts. Using a high-volume node (a level where price clusters) as a stop anchor is a questionable idea in general, but more concretely it means the stop distance — and therefore target levels, R:R, position size, and `risk_valid` — all depend on where the HVN happens to sit relative to price. If the HVN is near price, `validate_risk_parameters` classifies the stop as "too tight" and returns `risk_valid=False`, producing `NO-TRADE (RISK TOO HIGH)` even when nothing about ATR or volatility would suggest that. That coupling is not evident to a reader of the panel.
9. The caching layer is inert and, on the rare hit, mutates its own cache
`core/engine_core.py :: run`:

```python
cache_key = f"{symbol}_{timeframe}_{len(df)}_{df['close'].iloc[-1]}"

```

The key includes the last close price, and this is a fresh process per run, so the cache never actually hits across runs. It's effectively dead code that looks like optimization. And the one way it can hit (calling `run()` twice in the same process with identical data, e.g. the live-trading simulator running twice quickly) triggers a different bug: on a hit, `df = self._indicator_cache[cache_key]`, and then `calculate_structure(df, ..., copy_df=False)` mutates that cached frame in place, adding `STRUCTURE`/`HVN`/`LVN` to the object stored in the cache. Subsequent runs see a frame that has already been structurally annotated. Not fatal, but it's an in-place-mutation hazard that would not be expected from the "bounded cache" comment.
10. Smaller items

* `main.py` configures `logging.FileHandler('Logs/phase7_engine.log')` at import time, but `os.makedirs('Logs', ...)` happens later in `main()` — and the first `logger.info(...)` occurs before the makedirs call. On a first run in a clean checkout, the first file-log write fails (the logging machinery catches it and prints to stderr), so early log lines silently miss the file.
* `live_trading.py :: run_once` calls `route_and_execute`, which calls `render_panel` — so the "simulator" also dumps the full colored panel to stdout as a side effect, which is probably not what a caller invoking `run_once` for a JSON result expects.
* `core/engine_core.py :: run` sets `eq_trade_direction = "SHORT" if short_signal else "LONG"` — when neither signal fires (the common case), the entry-quality multipliers are evaluated as if the trade were a LONG. With `macro_bias == "BEARISH"` that applies a 0.90 penalty to a direction nobody asked about.
* `btc_context` in `engine_core.py` passes `macro_bias="NEUTRAL"` for BTC by design (acknowledged in the comment), but the `models/decision_model.py` BTC-adjustment path treats BTC's `score` as a `-100..100` value and AERO's the same way — that part is fine; the acknowledged limitation is just something a reader should know is stubbed.
* Several long comments are already stale in ways that mislead maintenance: `models/entry_model.py` still says the `generate_entry_signals` gate "won't fire in practice until B1 ... exists, since raw_bias is currently pinned to NEUTRAL" — B1 now exists and `raw_bias` is not pinned. `decision_model.py` says "Layer 2 ... will feed richer inputs later" while Layer 2 is already implemented in `bias_engine.py`. The comments describe a roadmap state that no longer matches the code.

What I can and cannot determine from the source
From the source alone I can state firmly what this program does: it fetches OHLCV from MEXC for the configured symbol (and, unless the symbol is BTCUSDT, for BTCUSDT), computes indicators/structure/bias/risk, prints a terminal panel, writes one PNG (`Logs/Charts/chart_...`), writes one state JSON per symbol/timeframe (`Logs/phase7_state_...json`), and — via `live_trading.py` — can write a simulated-order JSON. Nothing in the code path ever sends an order to any exchange; there is no trading capability in this repository, only the word "trading" in names and a panel line claiming a CSV log that is never written. I cannot determine from the code whether the claimed CSV trade log is supposed to be written by something outside these 19 files; within this codebase it is not, and the panel asserts it is, which is a contradiction I'm flagging as a defect rather than a mystery. One line to close the "what's fine" obligation: the data-fetch error propagation (`data_fetcher.py :: get_tf` → `engine_core.py` distinct "data fetch failed" state) and the normalization of the decision object shape are done correctly, and the MEXC 8-field OHLCV mapping and `4h`/`1d` interval strings check out against the public API — the problems are not there; they are in the signal semantics, the fallbacks, and the unused layers.
