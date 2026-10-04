Claude (Anthropic) — family: Claude. I cannot read my own exact checkpoint from inside a conversation, and I will not guess one.

**Independence disclosure, before anything else.** Section 5's last paragraph states that Claude wrote the fixes I am grading and wrote the tests that check them. That is me. My review of this code is therefore the case the Constitution itself names — "grading its own homework" — regardless of which lab this round was addressed to. If this round was addressed to a lab with no prior exposure to this project, that lab is not Anthropic. I am not Laguna S 2.1 (Poolside), which is the model named in `tests/test_package_token_check.py` and `tests/test_send_audit_round.py`; those files describe round 7's reviewer. I have no prior-session exposure to this project, and I do not recognise this code from training rather than from reading it — but the public-repository disclosure applies and cannot be checked from my side.

**Package check (Section 5), performed before grading.** The file named as the Constitution contains the Constitution: 29 pages of verbatim extraction, all 44 rules present and legible (21 / 7 / 10 / 6, matching the register the document itself states), the finding schema, severity rubric, MVA and Next Steps intact. No outcome rows in the Version History — it ends at LICENSED, 26 August 2026. **The Section 2 stop condition did not fire.** Layout artefacts ("Determinism6", "Fail Safely14") are present exactly as disclosed and are extraction noise, not damage. The manifest states `Round: round7`, build time 30 September 2026, 36 source files and 75 test files — the file counts match the two bundles exactly (I counted the `=== FILE:` entries: 36 and 75). **I cannot recompute the SHA-256 values**, because I received text rather than bytes; hash verification is therefore not something this report can perform. Nothing in the package contradicts its own name.

---

# Part 1 — Verdict table

**Tier 1 — Invariants**

| Rule | Short name | Verdict |
|---|---|---|
| T1 Item 1 | Tool, Not Autonomous Actor | Compliant |
| T1 Item 2 | No Future Information / Look-Ahead Bias | Partially compliant |
| T1 Item 3 | Data Integrity | Partially compliant |
| T1 Item 4 | Determinism | Compliant |
| T1 Item 5 | Reproducibility | Compliant |
| T1 Item 6 | Traceability | Partially compliant |
| T1 Item 7 | No Unsupported Predictive Claims | Compliant |
| T1 Item 8 | Epistemic Honesty | Partially compliant |
| T1 Item 9 | Every Measurement Has a Precise Definition | Partially compliant |
| T1 Item 10 | Consistent Semantics | Partially compliant |
| T1 Item 11 | No Circular Reasoning | Partially compliant |
| T1 Item 12 | No Hidden Decision-Affecting State | Compliant |
| T1 Item 13 | Fail Safely | Partially compliant |
| T1 Item 14 | Risk Is Not Conviction | Partially compliant |
| T1 Item 15 | Empirical Evidence Supersedes Theoretical Expectation | Not verifiable |
| T1 Item 16 | Complexity Must Provide Demonstrated Value | Partially compliant |
| T1 Item 17 | Backtesting Must Be Isolated From the Core Engine | Compliant |
| T1 Item 18 | Read-Only Market Access | Compliant |
| T1 Item 19 | Withdrawal Permissions Are Never Enabled | Compliant |
| T1 Item 20 | Credentials Are Never Exposed | Compliant |
| T1 Item 21 | Operator Credentials Stay With the Operator | Compliant |

**Tier 2 — Architecture**

| Rule | Short name | Verdict |
|---|---|---|
| T2-1 | Separation of responsibilities | Compliant |
| T2-2 | Observation → interpretation → decision → risk/action | Compliant |
| T2-3 | Explicit interfaces/contracts | Compliant |
| T2-4 | Explicit configuration | Compliant |
| T2-5 | Modular design | Compliant |
| T2-6 | Controlled dependencies | Compliant |
| T2-7 | Explicit, evaluated changes to interfaces or behavior | Compliant |

**Tier 3 — Process**

| Rule | Short name | Verdict |
|---|---|---|
| T3-1 | Hypothesis-driven development | Not verifiable |
| T3-2 | Controlled changes | Partially compliant |
| T3-3 | Automated tests | Partially compliant |
| T3-4 | Regression tests | Compliant |
| T3-5 | Fixed evaluation datasets | Compliant |
| T3-6 | Version control | Compliant |
| T3-7 | Known-good checkpoints | Compliant |
| T3-8 | Reproducible experiments | Compliant |
| T3-9 | Rollback capability | Compliant |
| T3-10 | Documentation of significant decisions | Compliant |

**Tier 4 — Preferences**

| Rule | Short name | Verdict |
|---|---|---|
| T4-1 | Robustness over optimization | Compliant |
| T4-2 | Generalization over historical fit | Compliant |
| T4-3 | Explainability over unnecessary opacity | Compliant |
| T4-4 | Stability over flashy outputs | Compliant |
| T4-5 | Useful information over more information | Partially compliant |
| T4-6 | Prefer the simpler design | Compliant |

---

# Part 2 — Findings

Ordered by severity. Five Major, five Minor. **No Critical findings.**

---

## F1 (Major) — The risk lineage omits an input that moves the stop by up to 50%, and says it does not exist

**Rule:** T1 Item 6 (Traceability). Also Item 8 (Epistemic Honesty) and Item 5 (Reproducibility).

**Location.** `core/engine_core.py`, the `risk_inputs` dict inside `lineage_record`, and its comment:

```
"ITEM 14, 11 September 2026: trend_health stood here and no longer does, because
 this block records what actually fed the risk decision and trend_health no
 longer does."
```

`core/decision_contract.py`, `LineageBlock` docstring: *"the stop and the three targets are computed from price and ATR"*.

**What the code actually does.** `models/risk_model.py`, `calculate_stop_targets`:

```python
trend_factor = 1.0 + (max(0.0, min(100.0, trend_health)) / TREND_FACTOR_DIVISOR)
bias_factor  = 1.0 - (abs(bias_score) / BIAS_FACTOR_DIVISOR)
stop_mult    = ATR_STOP_MULT * trend_factor * bias_factor * vol_multiplier
```

with `TREND_FACTOR_DIVISOR = 200.0`. `trend_health` is passed in by `engine_core` (`trend_health=trend["trend_health"]`) and is used on every run. The project's own test knows this: `tests/test_stop_is_atr_only.py::_expected_stop` writes the expected stop out *with* `trend_health` in the multiplier and asserts the engine matches it. The comment beside the record, and the contract's docstring, say the opposite.

**Clause broken.** Item 6: *"Every major output must have an explainable lineage: decision ← decision components ← … "*. The stop and the three targets are major outputs, and the recorded decision-component branch for them (`risk_inputs`: current_price, atr, bias_score, adx, volatility_state, risk_regime) is missing the fourth factor in their formula. Item 8: the record's own rationale asserts something false about the code beside it.

**What goes wrong in practice.** Two runs, same price 100.0, same ATR 2.0, same `bias_score` 40.0, same volatility — one with `trend_health` 0, one with 100. Stop multiplier 1.04 vs 1.56: the stops are 97.92 and 96.88, and every target moves with them. An auditor reconstructing the plan from `risk_inputs`, which is what that block is for, computes 97.92 both times and cannot find the discrepancy, because the record states that `trend_health` is not a risk input. (It can be recovered by going to `trend.trend_health` or `lineage.bias_components.factors.trend_health.input` in the same record — which is why this is Major and not Critical: the number is computed correctly and the input is recoverable elsewhere in the record. I considered Critical on the "assertion that something happened when it did not" clause and stopped short because the record is incomplete rather than fabricated, and self-correcting if the reader looks outside `risk_inputs`.)

**Severity: Major** — a Tier 1 traceability chain is broken at the branch that produces the numbers the operator acts on, and the break is documented as a property.

---

## F2 (Major) — Item 14's independence is one hop deep: the "independent" risk regime shares its input with 30% of the conviction number

**Rule:** T1 Item 14 (Risk Is Not Conviction). Also Item 11.

**Location.** `models/risk_model.py`, `classify_risk_regime`:

```python
if volatility_state == "HIGH VOLATILITY" or (adx_is_measured and adx < REGIME_CHOP_ADX):
    return "HIGH VOLATILITY RISK"
elif volatility_state == "LOW VOLATILITY" and adx_is_measured and adx >= REGIME_STRONG_ADX:
    return "LOW RISK"
```

against `indicators/trend_health.py`, inside `compute_trend_health`:

```python
adx_strength = 0.0 if adx_val is None else min(max(adx_val, 0.0) * 1.2, 40.0)
...
trend_health = float(slope_strength + adx_strength + rsi_strength)
```

and `models/bias_engine.py`: `WEIGHT_TREND_HEALTH = 0.30` on the signed `trend_health`. `models/decision_model.py` then reads `aggressive_allowed = risk_regime in ("NORMAL RISK", "LOW RISK")`.

**What the code does.** One raw measurement — the ADX column at the decision bar — is read in two places. Up to 40 of `trend_health`'s 100 points come from it, and `trend_health` is the largest single factor (0.30) of `bias_score`, which is confidence. The same reading also decides chop vs. strong-trend in the risk regime, which decides whether AGGRESSIVE is available. The fix of 11 September replaced `trend_health` with ADX inside `classify_risk_regime` because `trend_health` correlated with conviction — but ADX is an *input* to `trend_health`, so the correlation is still there, one hop down. The comment in `risk_model.py` states the module's read "was independent of bias_score before this change and remains so after it"; that is true only in the narrow sense that the value is not routed *through* `bias_score`. By the standard the same comment sets for itself — "an independent check that correlates with the thing it is checking is not a check" — it is not met.

**Clause broken.** Item 14: *"Directional conviction must never be treated as equivalent to risk. Being highly confident an asset is bullish does not automatically justify taking on high risk."* The AGGRESSIVE-intensity decision is partly a second reading of the evidence that produced the conviction.

**What goes wrong in practice.** ADX 18: `adx_strength` 21.6 of trend health, and `adx < REGIME_CHOP_ADX` forces HIGH VOLATILITY RISK — AGGRESSIVE blocked. ADX 30: `adx_strength` 36, and the regime can reach NORMAL/LOW RISK — AGGRESSIVE available. The risk gate therefore opens and closes in the same direction as the conviction it is supposed to counterbalance, on the same input. The genuinely independent refusals (EXTREME VOLATILITY, stop distance > 8%, > 15%) remain and do work; it is the positive half of the gate — the one that *permits* extra intensity — that is correlated.

**Severity: Major** — it weakens a Tier 1 independence guarantee on a live, operator-facing label, without fabricating any number.

---

## F3 (Major) — A frame with no time axis passes data validation with every temporal check silently skipped

**Rule:** T1 Item 3 (Data Integrity). Also Item 8 (the decision-candle record it goes on to make).

**Location.** `data/validation.py`, `validate_ohlcv`:

```python
ts = _timestamps(df)
if ts is None:
    # No time axis at all. Not an error by itself ...
    return None
```

and `data/data_fetcher.py`, `_load_pinned`, whose completeness check is

```python
missing = [c for c in _OHLCV_COLUMNS if c not in df.columns]
```

with `_OHLCV_COLUMNS = ["open", "high", "low", "close", "volume"]` — no timestamp requirement.

**What the code does.** `validate_ohlcv` rejects missing candles, duplicates, out-of-order stamps, irregular intervals, future-dated data, forming candles and stale data — all of them behind the `ts is None` early return. A frame whose index is not a `DatetimeIndex` and which has no `timestamp` column returns `None` (accepted) from the whole temporal half of the validator. The pinned loader never requires a timestamp column, so such a file is served as clean data.

**Clause broken.** Item 3: *"Missing candles, duplicated candles, impossible prices, timestamp inconsistencies, NaN/Inf values, stale data … must be detected before they become analysis."* On this input none of the six temporal classes is detected at all, and the frame becomes analysis. The finding-16 ruling — the engine decides on the last **closed** candle — is entirely a statement about time, and it is void on this path.

**What goes wrong in practice.** Drop the `timestamp` column from a copy of `AEROUSDT_4h.csv` and run: the engine produces a complete panel and a complete decision record. `provenance.last_candle` reads `419` (a row number), and `decision_candles.struct` records an `open_time` of `"419"` with a `close_time` derived from `419 + pd.Timedelta(minutes=240)` — a record asserting a decision candle that does not exist. Data five years stale is analysed as current, because the staleness check never ran. The panel still prints "DECISION CLOSE … the plan's entry; stop, targets and R:R are measured from it" with an operator-actionable plan on it.

**Severity: Major** — it silently voids most of one of the four Minimum Viable Audit items on a supported input path, and produces a false decision-candle record. The Critical argument (the engine asserting a decision candle it did not decide on) is available; I stopped short because reaching it needs a malformed input file and the live MEXC path always supplies timestamps.

---

## F4 (Major) — Evidence is counted twice on its way to the decision, and macro still decides the tier the requirement says it cannot

**Rule:** T1 Item 11 (No Circular Reasoning). Cross-checking Section 4a's stated requirement: *"Macro is one weighted input to that score and has no separate vote."*

**Location.** `models/bias_engine.py` (six weighted factors, and the dependency-graph comment), `models/entry_model.py` (`macro_multiplier` / `trend_multiplier` / `structure_multiplier`), `core/engine_core.py` (`eq_trade_direction` from `raw_bias`; `macro_agreement` / `volume_agreement` feeding `validation_score`), `models/decision_model.py` (the tier ladder reading `entry_score`).

**What the code does.** Three named paths:

1. **Four of the six bias factors are transforms of one measurement.** `bias_engine.py`'s own independence review says it: trend health (EMA slopes), structure regime (close-mean gap), SuperTrend direction (ATR-banded price flip) and macro bias (close vs. EMA-50 one timeframe up) are *"four transforms of one measurement: the recent direction of close … in a sustained trend they agree by construction, and bias_score presents that agreement as four independent confirmations."* 0.75 of the blend's weight is that agreement. The record (`bias_components`) and the confidence sentence present them as six separately weighed factors.
2. **The entry confluence multipliers re-weigh evidence bias_score already weighed.** `trade_direction` is derived from `raw_bias` (i.e. from `bias_score`); `macro_multiplier` is macro agreeing with it; `trend_multiplier` is `trend_direction` — the *sign of the same EMA slopes* that supply `trend_health`'s slope term; `structure_multiplier` is `trend_sequence`, which also drives `bias_score`'s CHOCH discount. So the boost that raises `entry_score` is a boost for the evidence that already chose the direction being scored — and the reasoning then reports "Bias is bullish … with a high-quality entry (80/100)" as two corroborating facts.
3. **Macro has three votes, one of which decides the CONSERVATIVE tier.** Removing work order G's `macro_bias == "BULLISH"` clause did not remove macro from the tier decision: `entry_score = base × macro_mult × trend_mult × struct_mult`, and `entry_score >= AGGRESSIVE_ENTRY_SCORE_MIN (70)` is exactly what separates LONG/AGGRESSIVE from CONSERVATIVE. Base 66 with three boosts = 76.9 → LONG. The identical base with a bearish macro = 65.6 → CONSERVATIVE LONG. Macro also feeds `bias_score` (0.10) and `validation_state` (via `macro_agreement`, −20), which is read in the ladder.

Also still present and disclosed: RSI reaches `bias_score` through `trend_health`'s `rsi_strength` and `continuation_strength`'s `momentum_component`, measured in the code's own comment at r = 0.83 in uptrends.

**Clause broken.** Item 11: *"A signal must not be allowed to reinforce itself through multiple derived layers and then be presented as independent confirmation."* Path 2 is that sentence almost verbatim. The requirement in Section 4a ("Macro … has no separate vote", "Macro does not decide the CONSERVATIVE tier") is contradicted by path 3.

**What goes wrong in practice.** A market that is simply trending produces trend health, structure regime, SuperTrend and macro all agreeing, and `bias_score` reports four independent confirmations of one fact — driving confidence, and through it the EV sentence and the tier, higher than four correlated reads warrant. Separately, a base entry score of 66 lands the operator on LONG or CONSERVATIVE LONG depending only on the daily macro read — the very double-count that work order G was written to remove.

**Severity: Major** — it moves the confidence number and the action tier on every trending run. It is filed as Major rather than higher because no number is fabricated and the project documents paths 1 and 3's sibling (RSI) openly; but path 3 additionally falsifies a stated requirement and a fix claim, which is what makes this more than disclosed design debt.

---

## F5 (Major) — "BAND DISTANCE" reports distance from the band's midpoint and labels it distance from the band

**Rule:** T1 Item 9 (Every Measurement Has a Precise Definition). Also Item 8.

**Location.** `models/entry_model.py`:

```python
zone_mid = (zone_lower + zone_upper) / 2.0
dist_to_mid = abs(close - zone_mid)
distance_from_zone = float((dist_to_mid / close) * 100.0)
```

rendered by `core/panel_render.py`, `_entry_zone_lines`:

```python
distance_line = f"BAND DISTANCE : {distance:.2f}% away from the band\n"
```

**What the code does.** The quantity is the distance from the band's **midpoint**, as a percentage of price. It is printed as the distance from the **band**. The entry score's bands (`dist_to_mid <= zone_width` → ACTIVE, etc.) use the midpoint distance consistently, so the number is internally coherent — the label is not its definition.

**Clause broken.** Item 9: *"Terms such as trend strength, momentum, alignment, confidence, and risk each need an explicit mathematical or semantic definition."* This measurement's stated definition ("away from the band") is not its computed one. Item 8: the panel asserts a distance that is not the distance it names.

**What goes wrong in practice.** Your own Run 1 transcript shows it: band `$0.7602 – $0.7756`, close `$0.8017`, printed **"BAND DISTANCE : 4.22% away from the band"**. The midpoint is 0.7679 → 4.22% (what was computed). The band's near edge is 0.7756 → **3.26%** (what the line claims). The operator is given a figure ~30% large for the stated quantity. Worse, when price is *inside* the band — the case the panel calls `STATUS : ACTIVE ENTRY ZONE` — the line still prints a positive "x% away from the band" directly below it, e.g. band 0.7602–0.7756 and price 0.7700 gives "BAND DISTANCE : 0.27% away from the band" two lines under "STATUS : ACTIVE ENTRY ZONE". Two contradictory claims in one panel — the exact shape as the macro-note and volume-note contradictions this engine has already had twice.

**Severity: Major** — it is a number the operator reads to judge entry timing, printed with a definition it does not have, and it self-contradicts the adjacent STATUS line whenever price is in the zone. I stopped short of Critical because the band bounds are printed on the line above and the quantity itself is well defined and used consistently by the score.

---

## F6 (Minor) — `clean_series` keeps a fill method that reads from later rows

**Rule:** T1 Item 2 (No Future Information). Also Item 16.

**Location.** `indicators/indicators.py`, `clean_series`:

```python
elif method == "interpolate":
    series = series.interpolate(method='linear', limit_direction='forward')
```

**What the code does.** Linear interpolation fills an interior gap from the values on **both** sides of it — including the next valid bar, which is in the future of every row inside the gap. Every current caller passes `method="forward_fill"`, so the live path is clean (forward fill, leading NaN preserved, trailing edge preserved — the item-15 work, checked and correct). `interpolate`, `drop` and `fill_value` are, as far as this package shows, never called.

**Clause broken.** Item 2: *"Information unavailable at the exact decision timestamp must never influence that decision, whether directly or through a derived signal."* A code path that would do exactly that is one keyword argument away, in the same function whose docstring is the project's statement of this rule. Item 16: three unused methods in the same helper.

**What goes wrong in practice.** Any future caller that writes `clean_series(s, method="interpolate")` — plausible, since it is a documented, named option — produces series whose interior values depend on bars after them. The engine today decides at the last bar of a 450-row frame and cannot be affected; a backtest that walks the decision bar backwards turns it into a live leak with no code change, which is the precise scenario the Constitution's own backtesting note warns about for Item 2.

**Severity: Minor** — no reachable effect on any decision the engine makes today.

---

## F7 (Minor) — Volume-spike detection watches 20 bars; the volume profile reads all 450

**Rule:** T1 Item 3 (Data Integrity).

**Location.** `indicators/indicators.py`, the spike block:

```python
window = min(config.VWMA_LENGTH, len(vol))
...
recent = vol.iloc[-window:]
```

against `indicators/volume_profile.py`, `compute_volume_profile`, which distributes **every** candle in the frame across its price bins, and whose HVN/LVN feed `entry_model`'s structure points and `trend_health`'s reversal detection.

**What the code does.** The ruled design (31 August: spikes are real data, never altered, but the run is degraded so confidence is capped) is implemented only for spikes inside the trailing `VWMA_LENGTH` (20) bars. A single candle with volume 10^12, 100 bars back, moves the HVN/LVN — and through them the 12-point structure component and the reversal factor — with no detection and no confidence cap.

**Clause broken.** Item 3: *"… abnormal volume must be detected before they become analysis."* The named consumer that reads the whole window is outside the detector's window.

**What goes wrong in practice.** One exchange glitch bar three weeks back relocates the point of control for the whole 450-bar profile. `struct_pts` and the reversal reading move accordingly; `degradation` stays empty; the run reports itself clean and full-confidence.

**Severity: Minor** — the value reaching the calculation is real market data (which the ruling deliberately permits) and the affected consumers are two of many inputs; the defect is that the safeguard the ruling paired with that permission does not cover the window those consumers read.

---

## F8 (Minor) — "VWMA" means two different calculations in two modules, and MOMENTUM is printed twice

**Rule:** T1 Item 10 (Consistent Semantics).

**Location.** `indicators/indicators.py`: `df["VWMA"] = np.where(valid_mask, price_volume_sum / volume_sum, np.nan)` — a rolling `VWMA_LENGTH` (20) ratio of Σ(close×volume) to Σ(volume), scored by `entry_model`. `structure/structure.py`, `_volume_sentiment_simple`: `vwma_recent = np.average(c_recent, weights=v_recent)` — a 5-bar weighted mean over `closes[-5:]`, and `vwma_prev` over `closes[-10:-5]`, driving the volume-sentiment label that drives `bias_score` (0.15) and the validation note. Also `core/panel_render.py`: the TREND line prints `momentum_mode` and the MOMENTUM line prints the same value again.

**Clause broken.** Item 10: *"The same term, score, or scale must mean the same thing in every module that uses it."* One name, two windows, two formulas, feeding two different outputs.

**What goes wrong in practice.** A reader comparing "VWMA Distance : 10.00/20" on the panel against the volume sentiment's implied VWMA slope is comparing a 20-bar rolling ratio with a 5-bar weighted mean; they can point opposite ways in the same run and nothing in the engine notices. Run 1 of your transcripts shows the duplication too: "TREND : BULLISH / STRONG (Score: 95.35/100)" and "MOMENTUM : STRONG" carry the same reading on two lines.

**Severity: Minor** — no number is wrong; two names collide and one line is redundant.

---

## F9 (Minor) — Four claims in the artifact that the code beside them does not support

**Rule:** T1 Item 8 (Epistemic Honesty). Item 6 cross-reference for the first.

These are the "comment wrong about the code it sits next to" class, and I looked for them specifically.

1. **`structure/structure.py`**, `StructureEngine.__init__`: `self._last_regime` with the comment *"State tracking for regime persistence to reduce whipsaws."* The only caller — `calculate_structure` — constructs `engine = StructureEngine(...)` and calls `analyze()` once per run, so the state carries across nothing at all: `_detect_regime` always enters with `current_state == "NEUTRAL STRUCTURE"`. The claimed whipsaw protection does not operate. This is the same shape as the project's own finding 18 against `BiasStateMachine` ("the record called what it produced a 'persistence requirement'. It had none"), in the module next door. It also matters in the other direction: if anyone ever reuses an instance, output becomes run-history-dependent with no warning (Items 4 and 12).
2. **`indicators/trend_health.py`**, `default_response`: `"momentum_mode": "NEUTRAL"` and `"trend_regime": "NEUTRAL"`. The classifier that runs on success emits `UNAVAILABLE / BUILDING / HEALTHY / STRONG / EXTENDED / EXTREME` and `EXHAUSTING / DIVERGENT / STRONG TREND / ACCELERATING / MEAN REVERTING / CHOP / MODERATE TREND / UNAVAILABLE` — it never emits "NEUTRAL" for either. A total failure therefore prints `MOMENTUM : NEUTRAL`, a label no measurement path can produce, where `UNAVAILABLE` (which the same function uses for a missing RSI) is the honest one.
3. **`core/engine_core.py`**, `volume_agreement`: `if not (vol_up or vol_down): return 0.0, "Volume sentiment is neutral."` This branch is reached for `"UNKNOWN VOLUME"` — the label `structure.py` writes when the sentiment detector *failed*. A failed read is reported to the operator as a neutral reading, under the heading "Validation Notes". That is the identical conflation the macro note was fixed for on 3 September ("The higher timeframe is neutral" for a failed macro read).
4. **`indicators/indicators.py`**, the ADX failure record: `"trend health loses its ADX component (25 of its 100 points)"`. `adx_strength` is `min(adx * 1.2, 40.0)` — the component's ceiling is 40, reached at ADX ≥ 33.3. The user-facing consequence string understates the loss by 37% at the top of its range.

**Clause broken.** Item 8: *"The engine must distinguish, at all times, between what is directly observed, what is … derived, what is interpreted … and what remains unknown."*

**What goes wrong in practice.** (3) is the operator-visible one: a run whose volume detector crashed prints "Volume sentiment is neutral." while the VOLUME line above reads "UNKNOWN VOLUME" — again, two claims about one thing in one panel. (1) misdescribes the mechanism a future maintainer will rely on.

**Severity: Minor** — none of the four changes a computed number; all four put a false statement in front of a reader.

---

## F10 (Minor) — A gate that cannot gate: the validation-WEAK check in the decision ladder never changes the action

**Rule:** T1 Item 16 (Complexity Must Provide Demonstrated Value).

**Location.** `models/decision_model.py`, `_determine_final_action`:

```python
if validation_state == "WEAK" and trend_health < 40:
    reasons.append("Validation is weak and trend health is low ... — waiting for a cleaner setup.")
    return "WAIT"
```

**What the code does.** Nothing that the code below it would not also do. With `trend_health < 40`, neither tier branch can return: the upper branch needs `trend_health >= AGGRESSIVE_TREND_HEALTH_MIN (75)`, the CONSERVATIVE branch needs `>= CONSERVATIVE_TREND_HEALTH_MIN (50)`. Control falls out of the `raw_bias` blocks to the final `return "WAIT"` in every case. The gate therefore can only change the *reason string*, never the action. `validation_state` has no other decision use in the engine (it is displayed on the panel).

**Clause broken.** Item 16: *"New indicators, models, calculations, or layers must exist because they solve a demonstrated problem or provide measurable value."* This is a check presented as a gate that cannot refuse anything the surrounding ladder does not already refuse — the same class as the `trend_failure` gate deleted at sequence item 9c.

**What goes wrong in practice.** Nothing wrong is produced — the harm is that the reasoning reads as though a validation check participated in the decision ("Validation is weak … waiting for a cleaner setup") when validation state is inert here. A future change that lowers the CONSERVATIVE threshold to 40 would silently turn it into a real gate nobody designed.

**Severity: Minor.**

---

# Part 3 — Not verifiable

**T1 Item 15 — Empirical Evidence Supersedes Theoretical Expectation.** The rule adjudicates disputes between measured behaviour and theory. Three instances in the code are consistent with it (the RSI/ATR fallbacks moved to Wilder smoothing after a measured divergence; the 5-sigma replacement was removed after it was measured erasing real flips; `trend_direction_sign` was separated from `continuation_strength` after a 9,800-bar measurement). But in each case the *measurement and the accept/reject decision* exist only as narrative written by the party being graded — the code shows the outcome, not the dispute. *What I would need:* the `PHASE7_DECISIONS.md` entries and commit messages where each measurement and its accept/reject was recorded at the time. The decisions log is not in this package, and the commit messages are withheld until Part 7 — which is not the audit.

**T3-1 — Hypothesis-driven development.** The clause that is checkable from an artifact — that measurements were taken and used — is well supported (see above). The clause that is not checkable is the ordering the rule actually specifies: *"Problem → hypothesis → implementation → test → measurement → evaluation → accept/reject"* and *"with what's changing and why stated before the work starts"*. Everything in this package describes process retrospectively. *What I would need:* the same two sources — decision records and commit messages dated at the time of the change, showing the hypothesis stated before the implementation.

(For the same reason I graded T3-2 only Partially compliant: its granularity half is verifiable from `version_control_history.md` and is mostly good — see below — but its "stated before the work starts" half is not evidenced in this message.)

---

# Part 4 — Test suite assessment

**Section 7.3's six shapes, as I found them.**

1. **Iterating a collection and asserting nothing when it is empty.** The suite's dominant weakness is a family of source/AST absence guards that pass if the scan itself finds nothing: `test_execution_surface.py::test_no_order_execution_calls` (and its three siblings), `test_risk_verdict_is_read_not_assumed.py::test_no_module_defaults_a_missing_risk_verdict_to_a_pass`, `test_swing_structure_is_not_invented.py::test_the_producer_returns_no_expression_built_from_the_current_price`, `test_no_fabricated_defaults_remain.py::test_calculate_structure_copies_the_analysis_without_defaults`, and — the weakest in the suite — `test_decision_bar_integrity.py::test_the_panel_never_prints_a_non_finite_number`, which asserts only that the strings `math.isfinite`/`np.isfinite` occur somewhere in `panel_render.py`, and `test_decision_bar_integrity.py::test_the_supertrend_level_is_guarded_and_not_only_its_direction`, which asserts that a message string ("SuperTrend's level") occurs in the function's source. Neither would fail if the behaviour it names were removed while the text stayed. Many other scans in this suite *do* carry explicit "this scan can fire" controls (`test_the_absolute_path_scan_can_report_a_violation`, `test_the_snapshot_comparison_can_actually_fail`, the code-fingerprint negative controls); the ones above are the ones that do not.
2. **Injecting a failure at a point the code path never reaches.** None found. The two historical instances (patching `ta.rsi`, which is recoverable and so cannot degrade; patching `classify_risk_regime`, which `calculate_stop_targets` never calls) are recorded in the docstrings and were corrected, and the corrections are the reason the file's later tests inject at the right seam.
3. **Asserting only absence.** As (1), with the same names. `test_no_dead_columns.py::test_deleted_columns_stay_deleted` is the same shape but is honestly labelled as a regression guard and paired with `test_consumed_columns_are_still_produced`.
4. **Setup contradicting the claim.** One clear instance: `test_panel_prints_only_what_was_computed.py::test_absent_scores_print_as_absent_not_as_zero` renders `{"symbol": …, "timeframe": …}` — a decision object with **no entry or risk keys at all** — and asserts the panel prints "not computed". But the engine's own unmeasured shape is not an absent key: `entry_model.calculate_entry_quality`'s `default_response` returns `"score": 0.0` and `trend_health`'s returns `"trend_health": 0.0`, both of which the panel prints as `0.00/100` because they are finite. The condition the test builds cannot arise from the engine, and the defect its own docstring names ("0.00/100 … a score of zero that nobody computed") survives one layer down, untested. A second, milder instance: `test_no_circular_reasoning.py::test_the_reasoning_no_longer_claims_trend_health_as_a_confidence_input` asserts `"95" not in text` — a magic substring rather than a claim about meaning.
5. **Returning instead of skipping.** One instance: `test_golden_path.py::test_the_snapshot_covers_every_top_level_field` does `if not os.path.exists(SNAPSHOT): print("SKIP: no baseline yet"); return` — a pass, not a skip. Delete the golden fixture and this test goes green while claiming to protect baseline coverage. (The two `if not SCHEDULED_FOR_REMOVAL: return` / `if not CANONICAL_ALIASES: return` early returns in `test_decision_contract.py` are *not* this shape: an empty dict is a documented valid state and the surrounding tests pin that.)
6. **Fixture can no longer produce the condition.** Generally handled well and unusually self-consciously: `test_timeframe_disagreement.py` asserts its own precondition ("the fixture really does split the two timeframes") before asserting behaviour, and `test_no_outlier_replacement.py`, `test_stop_is_atr_only.py` and `test_entry_score_reconciles.py` all carry precondition assertions. The exception is (4) above.

**Two structural points.**

- The fixtures themselves — `tests/fixtures/pinned/*.csv` and `tests/fixtures/golden_decision.json` — are **not in this package** (Section 4a says so). Every test asserting against a stored expected value or against pinned data can therefore be assessed only for shape, not for whether the expected values are right. That includes the golden baseline and the manifest-of-pins.
- `run_tests.py`, the fallback runner, calls every `test_*` with no arguments and therefore never runs the tests that take a pytest fixture (I count roughly the documented 29). They are reported as errors. So the error count it watches is a mixture of "takes a fixture" and "actually broken", and a new real error can hide inside a stable count. Under that runner, a meaningful slice of the suite — including several of the end-to-end degradation tests — executes at all only under pytest.

**Overall judgement.** This suite does test the engine, and materially so: it runs the full pipeline on pinned data, checks its fallbacks against the reference library to a stated tolerance, executes Item 5's reconstructability claim (rebuild from the archive, re-run, require the same decision), and runs whole-engine scenarios its fixtures deliberately make disagree. The previous auditor's verdict — that it tests "that selected implementation details have not changed more strongly than whether the engine is correct" — is no longer fair as a general description. It is fair in two specific respects. First, there is still a very heavy investment in pinning *current* behaviour (the golden snapshot has been re-baselined in roughly fifteen commits) and in source-text/AST guards. Second, and this is the blind spot that matters: **the suite checks values and shapes, and almost never checks that the name printed beside a number matches what the number is.** Both of my two most serious findings are exactly that class — `risk_inputs` omitting `trend_health` while saying it is not an input (survived `test_stop_is_atr_only.py`, which computes the stop correctly *with* `trend_health` and does not compare that fact against the record), and "BAND DISTANCE" printing midpoint distance (survived `test_entry_zone_is_measured.py` and `test_entry_score_reconciles.py`, which check values and labels separately and never the pairing).

---

# Part 5 — Release gate

**Met, on my findings alone.** The gate is that no Critical Tier 1 finding stands unresolved. I return **zero Critical findings**; five Major and five Minor stand, all against Tier 1 items.

I want to state the caveat the Constitution supplies for me: its own Minimum Viable Audit says that "a failure in any of those four would undermine trust in every other finding" — and two of my five Majors are against Items 3 and 6 (F3 and F1). The gate as written is satisfied. A reader who weights the MVA's own logic rather than the gate's wording should treat that satisfaction as weaker than the single sentence suggests.

---

# Part 6 — Observations outside the Constitution

**A. Two DEFECT observations about the standard itself (Section 10).**

1. **The Constitution contradicts itself about the Minimum Viable Audit.** The "New — the audit's starting gate" paragraph and the Revision 6 history define it as **four** items — 2, 3, 6 **and 18** ("Item 18 … joins Items 2, 3, and 6 in the Minimum Viable Audit gate"). The audit-independence safeguards paragraph still defines it as **three** — "the Minimum Viable Audit gate items (Items 2, 3, 6) get checked a second time by a reviewer who did not write the code" — stale since Revision 6 added Item 18. I graded against the four-item version (the later revision) and note that the second-check requirement is therefore written as covering three of the four. Recommend amending one of the two when the freeze lifts.
2. **Two passages say the document is not ratified, and the document says it is.** The Scope Freeze section: "it starts when it is ratified, and that hasn't happened yet"; Next Steps: "This document isn't ratified yet. Once it is, here's what happens." The status line and the Version History record the RATIFIED act of 26 August 2026. This is stale forward-looking text left unedited per the document's stated practice, but it is not marked as historical, and a reader could conclude the scope freeze is not in force. The register (21/7/10/6) is unambiguous and I graded against it.

**B. Stated requirements that look wrong, or that the code does not honour (Section 4a).**

1. *"Trade direction comes from the bias score alone. Macro is one weighted input to that score and has no separate vote"* — and *"Macro does not decide the CONSERVATIVE tier."* As F4(3) shows, macro still votes through the entry confluence multiplier (which moves `entry_score` across the 70 boundary that *is* the tier) and through `validation_state`. Either the requirement should say macro has three weighted paths and name their intended total weight (the code's own comment records this weighting question as unmade), or the multiplier should go. Right now the requirement and the code disagree, and work order G's claim to have removed macro from the tier decision is not true as stated.
2. *"The stop is measured from ATR. No volume level moves it."* True of volume levels, but incomplete: `trend_health` and `bias_score` scale the ATR multiplier (up to ×1.5 and down to ×0.667). That is defensible design — but see F1: the record built to explain the stop says `trend_health` is not an input to it. If the requirement intends "ATR is the only *anchor*", it should say so.
3. The 90-day archive prune is a sound and disclosed trade-off (verifiable-but-not-rebuildable past the window). One consequence worth naming for the backtest gate: the engine will accumulate a decision log of unbounded age whose early entries can no longer be rebuilt from the engine's own artifacts, only verified against re-fetched data.

**C. Claimed fixes I could not confirm.**

- Work order G's claim that removing the macro clause ended macro's role in the tier decision — **not confirmed**; the entry multiplier still decides LONG vs. CONSERVATIVE.
- The `risk_inputs` comment's claim that `trend_health` no longer feeds the risk decision — **contradicted** by `risk_model.calculate_stop_targets` and by `tests/test_stop_is_atr_only.py`'s own expected-stop formula.
- Work order B's claim that the panel prints a score only when one was computed — **confirmed only for absent keys**. The producers return `0.0` for unmeasured scores (`entry_model`'s `default_response`, `trend_health`'s `default_response`), which are finite and print as `0.00/100`.
- `_entry_quality_lines`'s claim that "absent fields print as 'n/a'" — **not reachable from engine output**, because `signal_router` materialises `float(entry.get("ema_pos_pts", 0.0))` and siblings before the panel sees them.
- `StructureEngine`'s claim of "regime persistence to reduce whipsaws" — **contradicted**; no persistence exists in the deployed call pattern.
- `indicators.py`'s ADX consequence "(25 of its 100 points)" — **contradicted**; the ceiling is 40.
- **Confirmed independently rather than taken on trust:** the claim that the EMA/RSI/ATR fallbacks compute "the same quantity by another route". I checked the mathematics rather than the comment: Wilder's RMA is an EWM with α = 1/length and `adjust=False`, which is what the fallbacks now use, and `ewm(span=n, adjust=False)` is definitionally the same EMA `pandas_ta` computes. The disclosed seeding difference over the first bars is real and bounded, and the decision reads `.iloc[-1]`.

**D. Where I noticed myself relying on a comment rather than the code.**

- The pinned fixtures being "fully paired" and the golden snapshot's contents — asserted by tests and by `MANIFEST.json`, none of which are in this package. I took `test_btc_correlation_alignment.py::test_the_pinned_fixtures_are_fully_paired` at its word because I cannot open the CSVs.
- The one-time output-invariance proof for the sequence item 5a deletions ("captured before and after and compared") cannot be re-run and I did not attempt to.
- The measured numbers in the independence review (the r = 0.83 / 0.37 RSI correlation, the 9,800-bar 0.71% firing rate) are claims; I verified that the code matches them in structure, not that the measurements were taken.

**E. Observations with no rule behind them.**

- Two lines of every panel are information-free. R:R is exactly 1.00 / 2.00 / 3.00 on every run, by construction of A12 (targets are multiples of the realised stop distance), so the column never varies and never informs. EV is a straight-line restatement of confidence (`ev_r = confidence/100 × (R+1) − 1`), which the code itself says "can never disagree with it". Both are labelled honestly, which is why this is T4-5's preference and nothing worse — but the labelling is asymmetric in one respect: the "(this is hypothetical, since no trade is actually being suggested right now)" caveat is added only when **no** trade is suggested. When the engine says `CONSERVATIVE LONG` and appends "worth taking on average", the hypothetical framing is thinnest and the operator is closest to acting.
- `bias_label`'s literal `30` and `MIN_ACTION_BIAS = 30.0` differ by comparator (`>` vs `>=`), so at exactly 30.0 a run can take a side while the panel prints neither CONFIRMED label. Documented and recorded; noting it here only so the disclosure is visible to whoever reads this report.
- `decision_model._determine_final_action`'s first WAIT gate prints `{trend_health:.0f}`; today `trend_health` is finite on every path that reaches it (NaN fails `trend_health < 40`), so the "trend strength nan/100" wording fixed elsewhere cannot appear here — but the guard is by control flow, not by the `math.isfinite` pattern used in the reason string one function up.

**F. Requested runs (Section 11).** Precise conditions and the output that would discriminate:

1. **Untimed pinned input.** Copy `AEROUSDT_4h.csv` with the `timestamp` column removed and run the engine on that directory. *Distinguishes:* if it returns a full panel and a decision record (F3 predicts `provenance.last_candle` reads a row number and `decision_candles.struct.open_time` is not a timestamp), F3 is confirmed as reachable; if it errors, F3 is latent and I will downgrade it.
2. **Price inside the band.** Run on any series where the close sits between `EMA_20` and `EMA_50`, and show the `EMA BAND` / `BAND DISTANCE` / `STATUS` lines. *Distinguishes:* "x% away from the band" printed alongside "STATUS : ACTIVE ENTRY ZONE" confirms F5's self-contradiction directly rather than by arithmetic on Run 1.
3. **The stop's hidden input.** `RiskModel().calculate_stop_targets(trend_health=0.0, current_price=100.0, atr_val=2.0, bias_score=40.0)` and the same call with `trend_health=100.0`, printing both 4-tuples and `provenance.lineage.risk_inputs` for each. *Distinguishes:* two different stops from two records whose `risk_inputs` are identical, which is F1 stated as output.
4. **The inert gate.** `DecisionModel()._determine_final_action` over `trend_health` ∈ {35, 39, 45, 49} × `validation_state` ∈ {WEAK, NEUTRAL, STRONG}, everything else held at a bullish, high-conviction fixture. *Distinguishes:* if the action is `WAIT` in all twelve cells, F10 is confirmed; any non-WAIT at `trend_health < 40` with `validation_state != "WEAK"` disproves it.
5. **Interpolation's direction.** `clean_series(pd.Series([1.0, float("nan"), 3.0]), method="interpolate")`. *Distinguishes:* a filled middle value derived from `3.0` (≈2.0) confirms F6; a NaN would refute it.