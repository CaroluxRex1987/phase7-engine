# Independent Re-Audit Report

I audited the supplied 29-page Constitution text, engine source bundle, and test-suite bundle. I did not receive commit messages, the remediation roadmap, engineering notes, or previous findings. Comments in the source that refer to prior audits were treated as claims by the project, not as evidence.

The audit does not raise execution concerns such as fees, slippage, routing, latency, or order fills. The supplied code contains no real order-execution path.

## Part 1 — Verdict table

The `T2-*`, `T3-*`, and `T4-*` labels below are document-order labels for the unnumbered rules in Tiers 2–4. They are not remediation sequence items.

### Tier 1 — Fundamental invariants

| Rule | Short name | Verdict |
|---:|---|---|
| Item 1 | Tool, Not Autonomous Actor | **Compliant** |
| Item 2 | No Future Information / Look-Ahead Bias | **Compliant** |
| Item 3 | Data Integrity | **Partially compliant** |
| Item 4 | Determinism | **Compliant** |
| Item 5 | Reproducibility | **Partially compliant** |
| Item 6 | Traceability | **Non-compliant** |
| Item 7 | No Unsupported Predictive Claims | **Compliant** |
| Item 8 | Epistemic Honesty | **Partially compliant** |
| Item 9 | Precise Definitions | **Compliant** |
| Item 10 | Consistent Semantics | **Partially compliant** |
| Item 11 | No Circular Reasoning | **Non-compliant** |
| Item 12 | No Hidden Decision-Affecting State | **Compliant** |
| Item 13 | Fail Safely | **Partially compliant** |
| Item 14 | Risk Is Not Conviction | **Non-compliant** |
| Item 15 | Empirical Evidence Supersedes Theory | **Not verifiable** |
| Item 16 | Complexity Must Provide Demonstrated Value | **Partially compliant** |
| Item 17 | Backtesting Isolated From Core Engine | **Not verifiable** |
| Item 18 | Read-Only Market Access | **Compliant** |
| Item 19 | Withdrawal Permissions Never Enabled | **Compliant** |
| Item 20 | Credentials Never Exposed | **Compliant** |
| Item 21 | Operator Credentials Stay With Operator | **Compliant** |

### Tier 2 — Architectural principles

| Rule | Short name | Verdict |
|---:|---|---|
| T2-1 | Separation of responsibilities | **Compliant** |
| T2-2 | Observation → interpretation → decision → risk/action | **Compliant** |
| T2-3 | Explicit interfaces/contracts | **Partially compliant** |
| T2-4 | Explicit configuration | **Partially compliant** |
| T2-5 | Modular design | **Compliant** |
| T2-6 | Controlled dependencies | **Compliant** |
| T2-7 | Explicit, evaluated changes to interfaces or behavior | **Not verifiable** |

### Tier 3 — Engineering process

| Rule | Short name | Verdict |
|---:|---|---|
| T3-1 | Hypothesis-driven development | **Not verifiable** |
| T3-2 | Controlled changes | **Not verifiable** |
| T3-3 | Automated tests | **Partially compliant** |
| T3-4 | Regression tests | **Partially compliant** |
| T3-5 | Fixed evaluation datasets | **Not verifiable** |
| T3-6 | Version control | **Not verifiable** |
| T3-7 | Known-good checkpoints | **Not verifiable** |
| T3-8 | Reproducible experiments | **Partially compliant** |
| T3-9 | Rollback capability | **Not verifiable** |
| T3-10 | Documentation of significant decisions | **Not verifiable** |

### Tier 4 — Engineering preferences

| Rule | Short name | Verdict |
|---:|---|---|
| T4-1 | Robustness over optimization | **Compliant** |
| T4-2 | Generalization over historical fit | **Compliant** |
| T4-3 | Explainability over unnecessary opacity | **Compliant** |
| T4-4 | Stability over flashy outputs | **Compliant** |
| T4-5 | Useful information over more information | **Not verifiable** |
| T4-6 | Prefer simpler designs when invariants are equally satisfied | **Not verifiable** |

---

## Part 2 — Findings

Findings are ordered by severity.

---

### Finding 1 — Item 3: abnormal volume is accepted as valid input

**Status:** Partially compliant  
**Severity:** **Critical**

#### Location

`data/validation.py`:

```python
if (volume < 0).any():
    return f"negative volume; lowest is {float(volume.min())}"
```

The validator checks that volume is finite and non-negative, but has no upper-bound, spike, distribution, or all-zero-volume check.

`structure/structure.py` subsequently uses volume in decision-relevant calculations:

```python
volume_expansion = recent_vol_mean > (1.2 * vma_baseline)
```

and:

```python
vwma_recent = np.average(c_recent, weights=v_recent)
```

`indicators/indicators.py` also uses volume to calculate VWMA:

```python
valid_mask = (volume_sum > 0) & np.isfinite(volume_sum) & np.isfinite(price_volume_sum)
df["VWMA"] = np.where(valid_mask, price_volume_sum / volume_sum, close_prices)
```

#### What the code does

It rejects negative volume but accepts any finite non-negative volume, including an isolated corrupted spike or an all-zero volume series.

The source comment explicitly acknowledges this:

```python
**Abnormal volume.** The invariant lists it, and this module checks only that
volume is finite and non-negative.
```

That is a project claim that the code does not satisfy the Constitution.

#### Broken clause

Item 3 requires:

> “Missing candles, duplicated candles, impossible prices, timestamp inconsistencies, NaN/Inf values, stale data, malformed API responses, and abnormal volume must be detected before they become analysis.”

#### Concrete scenario

A single candle contains:

```text
volume = 10^12
```

while its OHLC values and timestamp are otherwise valid. The validator accepts it. The volume spike can then:

- trigger `volume_expansion`;
- alter `volume_sentiment`;
- alter the bias score;
- alter VWMA and entry quality;
- reach the final decision and panel.

An all-zero volume series is also accepted. In that case, VWMA can fall back to the closing price through:

```python
df["VWMA"] = np.where(valid_mask, price_volume_sum / volume_sum, close_prices)
```

which can award a zero-distance VWMA score despite there being no usable volume measurement.

#### Impact

A corrupted volume input can change the directional bias, entry score, confidence-related calculations, and recommended action while being presented as a clean analysis.

#### Required action

Define and implement an explicit abnormal-volume policy. At minimum, distinguish:

- negative volume;
- all-zero or unusable volume;
- isolated extreme spikes;
- malformed or non-finite volume.

The policy should either reject the data or mark the analysis degraded before volume reaches indicators, structure, or decisions.

#### Verification

Add tests for:

- an isolated extreme volume spike;
- all-zero volume;
- a volume series with one non-finite value;
- a clean control series that remains accepted.

#### Re-audit

Re-audit Item 3 and the dependent Item 13 degradation path.

---

### Finding 2 — Item 8 and Item 13: a failed macro input becomes an ordinary neutral reading

**Item 8 status:** Partially compliant  
**Item 13 status:** Partially compliant  
**Severity:** **Critical**

#### Location

`core/engine_core.py`:

```python
df_macro = data_fetcher.get_tf(symbol, macro_tf, limit=100)
macro_bias = "NEUTRAL"

if self._validate_dataframe(df_macro, required_base_cols, "macro timeframe data"):
    try:
        df_macro, macro_failures = add_technical_indicators(df_macro)
        ...
    except Exception as e:
        logger.warning(f"Failed to process macro timeframe data: {e}")
        macro_bias = "NEUTRAL"
```

There is no corresponding:

```python
degradation.append(...)
```

for a missing, invalid, or failed macro series.

#### What the code does

If the macro fetch fails, the macro timeframe is invalid, or macro indicator processing raises, the engine continues with:

```python
macro_bias = "NEUTRAL"
```

The final decision is not marked degraded, confidence is not capped, and the panel prints:

```text
MACRO TREND: NEUTRAL
```

as if neutrality had been measured.

The supplied test suite documents this behavior rather than rejecting it. In `tests/test_golden_path.py`:

```python
assert without_macro == "NEUTRAL", (
    f"a missing macro series produced macro_bias={without_macro!r}, "
    f"expected 'NEUTRAL'."
)
```

#### Broken clauses

Item 8 requires the engine to distinguish:

> “what is directly observed, what is mathematically derived, what is interpreted, what is hypothesized, what has been empirically validated, and what remains unknown.”

Item 13 requires:

> “When data is missing, invalid, stale, or contradictory, the engine must become less confident or halt output — never invent a confident-looking answer.”

#### Concrete scenario

The pinned source contains:

```text
AEROUSDT_4h.csv
BTCUSDT_4h.csv
```

but not:

```text
AEROUSDT_1d.csv
```

`get_tf()` returns an empty frame with a `fetch_error`. `_validate_dataframe()` returns false. The engine silently retains `macro_bias = "NEUTRAL"` and produces a normal decision object with no degraded flag.

That neutral fallback influences:

- `calculate_dynamic_bias`;
- entry-quality multipliers;
- validation score;
- final action selection.

The same visible output is used for both:

1. a genuinely measured neutral macro trend; and
2. no macro data at all.

#### Impact

The engine can make a different decision because a required contextual input was absent, while the panel gives no indication that the input was unavailable.

#### Required action

Treat macro failure as an explicit degradation:

```python
degradation.append("macro timeframe unavailable")
```

or halt the analysis if macro context is mandatory. Do not encode “unknown” as `"NEUTRAL"`.

The panel should distinguish at least:

```text
MACRO TREND: UNAVAILABLE
```

from:

```text
MACRO TREND: NEUTRAL
```

#### Verification

Remove or corrupt the macro file and assert that:

- the decision is degraded or halted;
- `macro_bias` is not represented as a measured neutral;
- confidence/trade quality are reduced or no trade is authorized;
- the reasoning identifies the missing macro input.

#### Re-audit

Re-audit Items 3, 8, and 13 together.

---

### Finding 3 — Item 13: partially invalid indicator columns can pass without degradation

**Status:** Partially compliant  
**Severity:** **Critical**

#### Location

`indicators/indicators.py`:

```python
atr = clean_series(
    ta.atr(df["high"], df["low"], df["close"], length=config.ATR_LENGTH),
    method="forward_fill")
if atr is None or atr.isna().all():
    raise ValueError("pandas_ta returned no usable ATR")
df["ATR"] = atr
```

The guard detects only an entirely NaN series. A series with a valid prefix and a NaN at the decision bar is accepted.

`core/engine_core.py` then checks only column presence:

```python
if "ATR" not in df.columns:
    raise ValueError(
        "ATR is unavailable, so no stop or targets can be "
        "computed."
    )
```

and reads:

```python
atr_val = float(df_struct["ATR"].iloc[-1]) if "ATR" in df_struct.columns else (current_price * 0.02)
```

`models/risk_model.py` validates the numeric inputs inadequately:

```python
if current_price <= 0 or atr_val <= 0:
    ...
```

Comparisons involving `NaN` are false. The later checks likewise do not reject NaN:

```python
if stop_dist_pct > 15.0:
    ...
if stop_dist_pct < 0.2:
    ...
```

#### What the code does

A trailing NaN in ATR, SuperTrend, or another indicator can remain in the DataFrame because only all-NaN columns are removed. The value then travels into risk or bias calculations without being recorded as a failure.

#### Concrete scenario

`ta.atr()` returns valid values for the first 299 rows and `NaN` at row 300, the decision row.

`clean_series(...).ffill()` does not fill a trailing NaN. Because the column is not entirely NaN, it is retained. The engine reads:

```python
atr_val = nan
```

Risk calculation can then produce NaN levels or rely on incidental `min()`/`max()` behavior involving a structural level. Risk validation may still return:

```python
True, "OK"
```

because NaN comparisons do not enter either rejection branch.

A similar failure occurs for SuperTrend direction: only this is checked:

```python
if direction.isna().all():
    raise ValueError(...)
```

A partially invalid direction column is accepted, and `calculate_dynamic_bias()` converts its NaN to the default `0.0` through `safe_float()` without recording degradation.

#### Broken clause

Item 13 requires invalid or missing data to reduce confidence or halt output, never to become a normal-looking answer.

#### Impact

The engine can produce normal risk output from an invalid decision-bar indicator. Depending on the structural-level values, this can result in:

- NaN stop/target output;
- structurally derived levels that silently replace the missing ATR calculation;
- a risk check reported as `"OK"`;
- no degraded state.

#### Required action

Validate every decision-relevant indicator for:

- finite values;
- usable value at the decision row;
- required warm-up completion.

Do not test only `.isna().all()`. Reject or degrade if the final value is missing or non-finite.

Also make risk validation explicitly reject non-finite inputs with `np.isfinite()`.

#### Verification

Inject:

- trailing NaN ATR;
- trailing NaN SuperTrend direction;
- trailing infinity;
- valid-prefix/all-invalid controls.

Assert that the output is degraded or an error and never reports a normal risk plan.

#### Re-audit

Re-audit Item 13 and the risk-output portions of Items 8 and 10.

---

### Finding 4 — Item 11: bias and confidence reuse derived evidence as if it were independent

**Status:** Non-compliant  
**Severity:** **Critical**

#### Location

`indicators/trend_health.py`:

```python
health_component = (trend_health / 100.0) * 40.0
```

`models/bias_engine.py` separately includes both:

```python
signed_trend_health * WEIGHT_TREND_HEALTH
```

and:

```python
reversal_continuation_score * WEIGHT_REVERSAL_CONTINUATION
```

where `reversal_continuation_score` is based on `continuation_strength`, which already contains `health_component`, ADX, RSI, and acceleration.

The same bias score is then used by `models/decision_model.py`:

```python
bias_strength = min(100.0, abs(_safe_float(bias.get("score"), 0.0)))
```

while confidence adds structure and validation adjustments:

```python
if raw_bias == "BULLISH" and structure_regime == "BULLISH TREND":
    structure_alignment = 10.0
```

and:

```python
validation_adj = {"STRONG": 10.0, "NEUTRAL": 0.0, "WEAK": -15.0}.get(validation_state, 0.0)
```

The validation score itself is built from macro and volume:

`core/engine_core.py`:

```python
if (macro_up and bias_up) or (macro_down and bias_down):
    val_score += 10
```

and:

```python
if "STRONG" in volume_sentiment.upper() or "EXPANSION" in volume_sentiment.upper():
    val_score += 15
```

Those same macro and volume values are already direct factors in `calculate_dynamic_bias()`.

#### What the code does

The system treats the following as separate confirming evidence even though they are derived from overlapping inputs:

- trend health;
- continuation strength;
- ADX and RSI inside both of those;
- structure regime inside both bias and confidence;
- macro bias inside both bias and validation;
- volume sentiment inside both bias and validation.

#### Broken clause

Item 11 requires:

> “A signal must not be allowed to reinforce itself through multiple derived layers and then be presented as independent confirmation.”

#### Concrete scenario

With:

```text
structure_regime = BULLISH TREND
macro_bias = BULLISH
volume_sentiment = STRONG BULLISH ACCUMULATION
raw_bias = BULLISH
```

the structure, macro, and volume inputs first increase `bias_score`. They then increase `validation_score`, which becomes `validation_state = STRONG`, and confidence adds another +10. Structure also adds another +10 directly to confidence.

The final confidence explanation says:

```text
structure agrees with the bullish bias, and validation is strong
```

but those are not independent confirmations of the bias; they are restatements of factors already used to create it.

#### Impact

The displayed confidence and illustrative EV can be inflated by counting the same evidence more than once. Confidence is visible to the operator and is used by `_compute_ev()` as a rough win-rate proxy.

#### Required action

Define an explicit dependency graph for decision inputs. Either:

- remove duplicated factors from confidence/validation;
- or ensure each downstream score consumes only genuinely independent inputs;
- and document which values are derived from which upstream measurements.

Add perturbation tests that vary structure, macro, volume, continuation, and trend health independently.

#### Verification

For each base measurement, perturb it while holding all independent inputs fixed. Confirm that one underlying measurement does not increase multiple supposedly independent confidence components.

#### Re-audit

Re-audit Item 11 after the dependency graph and tests are added.

#### Layer 5 open question

The specific flagged Layer 5 question is narrower: `macro_bias`, `trend_direction`, and `structure_sequence` are computed separately in the supplied code. I found no direct assignment where one is derived from either of the other two. That specific Layer 5 relationship is therefore not itself shown to be circular. The broader bias/validation/confidence path above is circular and is sufficient for Item 11 to be Non-compliant.

---

### Finding 5 — Item 14: “AGGRESSIVE” action is selected from conviction and entry quality without an independent risk decision

**Status:** Non-compliant  
**Severity:** **Critical**

#### Location

`models/decision_model.py`:

```python
if trend_health >= 75 and entry_score >= 70 and not divergence:
    if entry_active:
        ...
        return "AGGRESSIVE LONG"
```

The short side has the equivalent branch:

```python
return "AGGRESSIVE SHORT"
```

The conservative explanation says:

```python
"the entry quality ({entry_score:.0f}/100) isn't strong "
"enough for full size — CONSERVATIVE LONG."
```

The decision logic checks only:

```python
risk_valid = bool(risk.get("risk_valid", True))
if not risk_valid:
    ...
    return "NO-TRADE (RISK TOO HIGH)"
```

It does not use the risk regime to distinguish normal risk from high risk once `risk_valid` is true.

#### What the code does

High trend health and high entry score directly produce an `"AGGRESSIVE LONG"` or `"AGGRESSIVE SHORT"` action. The code describes the alternative as not being suitable for “full size,” even though position sizing has been removed.

#### Broken clause

Item 14 requires:

> “Directional conviction must never be treated as equivalent to risk. Being highly confident an asset is bullish does not automatically justify taking on high risk.”

#### Concrete scenario

Inputs include:

```text
trend_health = 80
entry_score = 75
raw_bias = BULLISH
entry_status = ACTIVE ENTRY ZONE
momentum_divergence = False
risk_valid = True
volatility_state = HIGH VOLATILITY
```

The risk model can classify the setup as:

```text
HIGH VOLATILITY RISK
```

while still returning `risk_valid = True`. The decision model nevertheless returns:

```text
AGGRESSIVE LONG
```

because directional strength and entry quality meet the thresholds.

#### Impact

The operator receives an action whose wording implies increased risk-taking, selected from directional conviction and entry quality rather than from an independent risk policy. The “full size” explanation is especially problematic because no full-size operation occurs and no position sizing exists.

#### Required action

Separate:

1. directional recommendation;
2. risk regime;
3. action intensity.

Either eliminate “AGGRESSIVE/CONSERVATIVE” action labels or define an independent, explicit risk policy that can cap them. Do not describe an absent position size.

#### Verification

Test high-conviction inputs across:

- low volatility;
- high volatility;
- extreme volatility;
- wide and tight stops.

Assert that conviction alone cannot select the highest-risk action.

#### Re-audit

Re-audit Item 14 and the action semantics under Item 9.

---

### Finding 6 — Item 5: provenance is present but does not make every run reconstructable

**Status:** Partially compliant  
**Severity:** **Major**

#### Location

`core/engine_core.py`:

```python
"provenance": {
    "engine_version": config.engine_version,
    "last_candle": str(df_struct.index[-1]) if len(df_struct) else None,
    "row_count": int(len(df_struct)),
    "source": "pinned" if data_fetcher.pinned_source() else str(data_fetcher.base_url),
}
```

`core/decision_log.py` records:

```python
record = {
    "logged_at": datetime.now(timezone.utc).isoformat(),
    "engine_version": config.engine_version,
    "config": config_snapshot(config),
    "decision": decision,
}
```

#### What the code does correctly

It records:

- engine version;
- latest candle timestamp;
- row count;
- a source category or URL;
- selected configuration values;
- the decision object.

#### What remains missing

The record does not include:

- a raw-data archive or content hash;
- a pinned dataset manifest/version;
- the actual pinned source identity beyond `"pinned"`;
- all run parameters, such as `limit`;
- the prior state used by `Exit Watch`;
- all decision-affecting module configuration, including risk-model multipliers and bias weights.

`FINGERPRINTED_CONFIG` contains selected values such as:

```python
"STRUCT_LOOKBACK", "VOLUME_PROFILE_BINS",
"EMA_FAST", "EMA_SLOW",
"RSI_LENGTH", "ADX_LENGTH", "ATR_LENGTH",
"VWMA_LENGTH", "SUPERTREND_LENGTH", "SUPERTREND_MULT",
```

but not every parameter that can affect output.

#### Broken clause

Item 5 requires:

> “Every analysis must be reconstructable later — its data timestamp, data source and version, engine version, configuration, and parameters must all be recoverable.”

#### Concrete scenario

The exchange later revises or removes historical candles. The log contains the endpoint URL and latest timestamp, but not the exact candles used or a content hash. A later analyst cannot establish that the reconstructed input is byte-for-byte the input that produced the decision.

Likewise, two runs with different prior state files can produce different `exit_watch` output, but the prior state is not recorded in provenance.

#### Impact

The log is a useful receipt, but it is not a complete reconstruction record.

#### Required action

Record:

- exact input-data hash and dataset/manifest version;
- requested and effective fetch parameters;
- all decision-affecting configuration;
- prior state or a state hash;
- preferably the raw input or a durable archive reference.

#### Verification

Delete or alter the source data after a run and demonstrate that the analysis can still be reproduced from the recorded artifact.

#### Re-audit

Re-audit Item 5 and the traceability relationship with Item 6.

---

### Finding 7 — Item 6: the decision log records the result but not the required lineage

**Status:** Non-compliant  
**Severity:** **Major**

#### Location

`core/decision_log.py`:

```python
record = {
    "logged_at": datetime.now(timezone.utc).isoformat(),
    "engine_version": config.engine_version,
    "config": config_snapshot(config),
    "decision": decision,
}
```

The final decision object contains derived sections such as:

```python
"bias": {...},
"trend": {...},
"structure": {...},
"entry": {...},
"risk": {...},
"exit": {...},
```

but no raw candles, raw indicators, normalized signal records, or lineage identifiers.

#### What the code does

The engine stores the final decision and limited provenance. It does not preserve a walkable chain from:

```text
decision
→ decision components
→ normalized signals
→ raw signals
→ indicators
→ validated market data
→ raw source data
```

#### Broken clause

Item 6 requires:

> “Every major output must have an explainable lineage: decision ← decision components ← normalized signals ← raw signals ← indicators ← validated market data ← raw source data.”

#### Concrete scenario

An operator sees:

```text
TARGET 1: $...
CONFIDENCE: .../100
DECISION: ...
```

Six months later, the raw API data has changed. The log contains the target and some configuration, but not the ATR value, source candles, indicator inputs, or the exact intermediate components that produced the target. The operator cannot walk backward to the raw source data.

#### Impact

The output can be inspected descriptively, but not independently reconstructed or traced to exact raw candles. This defeats the Constitution’s stated requirement that a reasonable-looking output remain auditable.

#### Required action

Attach lineage metadata or artifacts to each major output. At minimum, persist:

- exact raw input reference/hash;
- validated-data reference;
- indicator values used at the decision bar;
- normalized signal values;
- decision-component contributions;
- final decision calculation inputs.

#### Verification

Given only a stored decision and its associated audit artifact, a reviewer should be able to reproduce each major displayed number.

#### Re-audit

Re-audit Item 6 after lineage artifacts exist.

---

### Finding 8 — Item 8: user-facing claims remain inaccurate in several paths

**Status:** Partially compliant  
**Severity:** **Major**

#### Positive evidence

The BTC section does state:

```python
f"   (computationally validated, empirically unvalidated — no backtest supports this adjustment)\n"
```

and degraded runs add explicit reasoning such as:

```python
"This run is DEGRADED: ..."
```

Those are compliant paths.

#### Broken path A — hardcoded lookback claim

`core/panel_render.py`:

```python
f"SWING STRUCT  : ${safe_float(structure.get('swing_struct', current_price)):.4f} (Lookback 8)\n"
```

But `core/engine_core.py` calls:

```python
calculate_structure(
    df, lookback=config.STRUCT_LOOKBACK,
    volume_profile_bins=config.VOLUME_PROFILE_BINS
)
```

If `config.STRUCT_LOOKBACK` is changed from 8 to 20, the calculation changes but the panel still says `Lookback 8`.

#### Broken path B — “full size” claim

`models/decision_model.py` says:

```python
"the entry quality ({entry_score:.0f}/100) isn't strong "
"enough for full size — CONSERVATIVE LONG."
```

The engine no longer computes position size and has no full-size operation.

#### Broken path C — failed macro represented as neutral

As described in Finding 2, a failed macro input is rendered as:

```text
MACRO TREND: NEUTRAL
```

without saying that the macro reading was unavailable.

#### Broken clause

Item 8 requires the engine to distinguish observed, derived, interpreted, hypothesized, validated, and unknown information.

#### Impact

An operator can be told:

- that an 8-bar lookback was used when another lookback was used;
- that an entry is not suitable for “full size” when no size exists;
- that macro conditions are neutral when they were never measured.

#### Required action

Make every user-facing claim derive from the same value used in the calculation. Replace unavailable values with explicit `UNAVAILABLE`/`UNKNOWN` states and remove references to nonexistent position sizing.

#### Verification

Run with:

- a non-default `STRUCT_LOOKBACK`;
- missing macro data;
- conservative action conditions.

Compare every panel assertion with the actual calculation path.

#### Re-audit

Re-audit Item 8 and all panel text.

---

### Finding 9 — Item 10: `risk.confidence_score` has different meanings in the raw and routed objects

**Status:** Partially compliant  
**Severity:** **Major**

#### Location

`core/engine_core.py` creates the raw engine output:

```python
"confidence_score": trend["trend_health"],
"trade_quality_current": trend["trend_health"],
"trade_quality_proposed": eq_metrics["score"],
```

`models/signal_router.py` creates the final decision object:

```python
"confidence_score": float(confidence),
"trade_quality_proposed": float(trade_quality["proposed_entry"]),
```

where `confidence` comes from `DecisionModel._compute_confidence()` and is not necessarily trend health.

#### What the code does

A caller of `Phase7Engine.run()` receives `risk["confidence_score"]` meaning trend health. A caller of `SignalRouter.route()` receives `risk["confidence_score"]` meaning the DecisionModel’s multi-factor confidence.

The production panel uses the routed object, so the main path currently displays the latter. The raw engine method remains callable and returns the former.

#### Broken clause

Item 10 requires:

> “The same term, score, or scale must mean the same thing in every module that uses it.”

#### Concrete scenario

For identical market data, a direct consumer of:

```python
Phase7Engine().run(...)
```

reads a confidence score equal to trend health, while the production router returns a different confidence score based on bias strength, structure alignment, and validation.

A future consumer that bypasses the router receives a number with the same name but a different meaning.

#### Impact

The same field name can produce materially different interpretations depending on the entry point.

#### Required action

Use distinct names for raw and routed values, or make the raw engine output and final decision object use a single documented semantic. Update `EngineOutput` and `DecisionObject` contracts accordingly.

#### Verification

Run both entry points on the same input and assert that identically named fields have the same documented meaning and, where intended, the same value.

#### Re-audit

Re-audit Item 10 and the decision contract.

---

### Finding 10 — Item 16: an unconsumed risk field remains in the live pipeline

**Status:** Partially compliant  
**Severity:** **Major**

#### Location

`core/engine_core.py`:

```python
"trade_quality_current": trend["trend_health"],
```

`models/signal_router.py` does not include `trade_quality_current` in the final `risk` block. `core/panel_render.py` no longer displays it.

The final `RiskBlock` in `core/decision_contract.py` does not declare it either.

#### What the code does

Every normal engine run computes and carries `trade_quality_current`, but the routed decision drops it and no production consumer reads it.

The test suite’s apparent check is also ineffective:

`tests/test_degraded_state.py`:

```python
assert risk.get("trade_quality_current", 0.0) <= ceiling
```

Because the field is absent, this reads the default `0.0`.

#### Broken clause

Item 16 requires:

> “New indicators, models, calculations, or layers must exist because they solve a demonstrated problem or provide measurable value — not merely because they can be added.”

#### Concrete scenario

Every run computes a second name for trend health in the raw risk object. It never reaches the final panel or decision contract. It cannot provide user value, yet remains part of the live pipeline and is tested as though present.

#### Impact

The field increases interface ambiguity and preserves the same duplicated-semantic risk that the cleanup was intended to remove.

#### Required action

Delete the field and its stale test expectation, or promote it to an intentionally defined, consumed field with a distinct semantic and contract entry.

#### Verification

Static-scan every consumer and validate the final object against the contract. No unconsumed risk field should remain.

#### Re-audit

Re-audit Item 16 and the decision contract.

---

### Finding 11 — Tier 2, Explicit interfaces/contracts: top-level presence is checked, but malformed sections are accepted

**Status:** Partially compliant  
**Severity:** **Moderate**

#### Location

`models/signal_router.py`:

```python
required_sections = ["bias", "trend", "structure", "entry", "risk"]
missing_sections = [section for section in required_sections if section not in raw_output]
```

The router validates only that the five top-level names exist. It then accepts loosely typed dictionaries:

```python
def _build_decision_object(
    ...
    bias: Dict[str, Any],
    trend: Dict[str, Any],
    structure: Dict[str, Any],
    entry: Dict[str, Any],
    risk: Dict[str, Any],
```

and supplies defaults throughout:

```python
"score": float(bias.get("score", 0.0)),
```

#### What the code does

An engine output such as:

```python
{
    "bias": {},
    "trend": {},
    "structure": {},
    "entry": {},
    "risk": {},
}
```

passes `_validate_engine_output()` and is transformed into a normal-looking decision with default zeros, neutral labels, and default risk validity.

The `TypedDict` declarations document the desired shape but are not used to enforce it at this seam.

#### Broken principle

Tier 2 requires:

> “What a module accepts and returns should be a stated contract, not something the next module has to reverse-engineer by reading the source.”

#### Impact

A producer can silently omit decision-critical fields and the router fabricates a structurally valid object from defaults rather than rejecting the interface violation.

#### Required action

Validate nested contracts at the router boundary, reject missing required fields, and distinguish an error object from a partially populated normal decision.

#### Verification

Pass malformed engine outputs with:

- missing nested fields;
- wrong types;
- NaN values;
- unknown fields.

Assert that the router returns a clear error instead of a normal decision.

#### Re-audit

Re-audit T2-3 and Item 13.

---

### Finding 12 — Tier 2, Explicit configuration: important behavior remains outside the recorded configuration

**Status:** Partially compliant  
**Severity:** **Moderate**

#### Positive evidence

Indicator and chart settings are centralized and wired, for example:

```python
RSI_LENGTH = 14
```

and:

```python
ta.rsi(..., length=config.RSI_LENGTH)
```

#### Location of the remaining issue

`models/bias_engine.py`:

```python
WEIGHT_TREND_HEALTH = 0.30
WEIGHT_STRUCTURE_REGIME = 0.20
WEIGHT_VOLUME_SENTIMENT = 0.15
WEIGHT_SUPERTREND_DIRECTION = 0.15
WEIGHT_MACRO_BIAS = 0.10
WEIGHT_REVERSAL_CONTINUATION = 0.10
```

`models/risk_model.py`:

```python
self.atr_stop_mult: float = 1.2
self.target1_mult: float = 1.0
self.target2_mult: float = 2.0
self.target3_mult: float = 3.0
```

`data/validation.py`:

```python
STALE_AFTER_BARS = 3
```

Other decision behavior is embedded in thresholds such as:

```python
RAW_BIAS_THRESHOLD = 20.0
```

and local structural thresholds in `structure/structure.py`.

These values are not part of `core/config.py` and are not included in `FINGERPRINTED_CONFIG`.

#### Broken principle

Tier 2 requires:

> “Important behavior ... comes from named, visible configuration — not mystery constants buried in the logic that touches them.”

#### Concrete scenario

Two runs use the same `core/config.py` snapshot but differ in:

- bias weights;
- risk stop multipliers;
- target multipliers;
- stale-data threshold.

The decision log represents them as the same configuration even though those values can change the output.

#### Impact

The system is partially configurable but the recorded configuration does not identify all behavior that controls decisions.

#### Required action

Centralize or explicitly classify all decision-affecting settings, then include them in the provenance/config snapshot.

#### Verification

Change each setting independently and assert:

1. the intended output changes;
2. the changed value appears in the run record.

#### Re-audit

Re-audit T2-4 and Item 5.

---

### Finding 13 — Tier 3, Automated tests: critical tests can pass without running

**Status:** Partially compliant  
**Severity:** **Moderate**

#### Location

This pattern appears repeatedly, for example in `tests/test_degraded_state.py`:

```python
if not _engine_available():
    print("SKIP: pandas_ta not installed")
    return
```

The same pattern appears in smoke, golden-path, contract, degraded-state, frame-ownership, and other modules.

#### What the code does

Under pytest, returning from a test is a pass, not a skip. Therefore, on a machine without `pandas_ta`, many tests report success without testing the engine pipeline.

The suite should use:

```python
pytest.skip(...)
```

or an explicit unavailable-dependency result that causes the runner to fail closed.

#### Broken principle

Tier 3 requires:

> “Every meaningful modification gets tested before it's accepted, not after.”

#### Concrete scenario

A clean checkout lacks `pandas_ta`. The tests for:

- end-to-end routing;
- degraded indicator behavior;
- golden output;
- contract production;
- frame ownership;

print a message and return. A CI job can report a passing suite despite never executing those checks.

#### Additional weak checks

`tests/test_degraded_state.py` contains:

```python
assert risk.get("trade_quality_current", 0.0) <= ceiling
```

but the final decision object does not contain `trade_quality_current`; this assertion always passes with `0.0`.

`tests/test_frame_ownership.py` only checks that the plotting function emits no ERROR logs. A plotting implementation that silently omits candles but returns a chart path could pass.

#### Required action

- Replace return-based skips with real skips that are visible in test results.
- Make the critical engine tests fail if their required dependency is unavailable.
- Assert presence and behavior of fields before checking their values.
- Test chart content or plotting calls, not just absence of errors.

#### Verification

Run the suite with `pandas_ta` absent and confirm the result is not a false green build.

#### Re-audit

Re-audit T3-3 and the release test command.

---

### Finding 14 — Tier 3, Regression tests: the suite protects selected outputs, but not the full regression surface

**Status:** Partially compliant  
**Severity:** **Moderate**

#### Positive evidence

`tests/test_golden_path.py` runs the routed production path against pinned data and compares a stored decision snapshot. `tests/test_smoke.py` also runs the pipeline end to end.

#### Remaining gaps

The golden snapshot excludes:

```python
VOLATILE = {"chart_path", "timestamp", "generated_at"}
```

and independently asserts only a limited top-level shape:

```python
required = {
    "symbol", "timeframe", "macro_bias",
    "bias", "trend", "structure", "entry", "risk",
    "exit", "exit_watch", "btc_context", "explanation",
}
```

It does not independently require fields such as:

- provenance;
- degradation;
- decision log path.

Also, the golden-path test explicitly accepts the known macro failure behavior as `"NEUTRAL"` rather than requiring a degraded state.

#### Broken principle

Tier 3 requires:

> “A new improvement must not silently destroy previously working behavior. Existing tests and fixed datasets exist specifically to catch this.”

#### Concrete scenario

A future re-baseline removes `provenance` or `degradation`. The snapshot comparison can accept the new baseline, and the independent expected-shape assertion does not require either field.

Similarly, a future change can preserve the golden decision while removing a failure signal, because the snapshot is primarily an output lock rather than a semantic invariant test.

#### Required action

Separate:

1. immutable golden outputs;
2. independent contract invariants;
3. failure-mode expectations.

Do not let re-baselining weaken required-shape assertions.

#### Verification

Delete one required field, re-run the suite, and confirm an independent test fails even if the snapshot is regenerated.

#### Re-audit

Re-audit T3-4 after expanding the regression assertions.

---

### Finding 15 — Tier 3, Reproducible experiments: pinned data exists, but dependency versions are unconstrained

**Status:** Partially compliant  
**Severity:** **Moderate**

#### Positive evidence

The supplied code has a pinned-data path and golden tests that set:

```python
data_fetcher.base_url = "http://127.0.0.1:1"
DataFetcher.set_pinned_source(...)
```

The test suite also controls the cross-run state file.

#### Location

`requirements.txt`:

```text
pandas
numpy
matplotlib
pandas_ta
requests
colorama
```

No versions are pinned.

#### Broken principle

Tier 3 requires:

> “Someone else — or future-you — should be able to rerun a validation test and get the same measured result.”

#### Concrete scenario

A future installation resolves a different version of pandas, pandas-ta, or NumPy. EMA, RSI, ADX, SuperTrend, NaN handling, or rendering behavior can change while the source and pinned CSVs remain unchanged.

The golden test may then fail for environmental reasons, or worse, be re-baselined against changed library behavior.

#### Required action

Record a reproducible dependency environment, such as:

- pinned package versions;
- a lockfile;
- Python version;
- relevant platform/runtime assumptions.

#### Verification

Recreate the environment independently and compare the golden output and indicator values.

#### Re-audit

Re-audit T3-8 and the fixed-dataset process together.

---

## Part 3 — Not verifiable

### Item 15 — Empirical Evidence Supersedes Theoretical Expectation

The source contains formulas and comments but no measured live/backtest comparison showing a disagreement between theory and observed behavior, nor evidence of how such a disagreement would be adjudicated.

Needed: empirical evaluation results, comparison methodology, and a record showing measured behavior wins when it conflicts with mathematical expectation.

### Item 17 — Backtesting Isolated From the Core Engine

No backtesting implementation was supplied. The absence of a backtester means there is no demonstrated failure path, isolation boundary, checkpoint mechanism, or rollback artifact to inspect.

Needed: the backtesting/validation tooling, its import and data boundaries, failure tests, known-good checkpoints, and recovery procedure.

### Tier 2 — Explicit, evaluated changes to interfaces or behavior

The final source and tests show some contract and golden-snapshot machinery, but they do not prove that interface or behavior changes were evaluated before acceptance.

Needed: versioned diffs, change records, downstream impact analysis, and acceptance evidence.

### Tier 3 — Hypothesis-driven development

The source contains comments describing hypotheses and planned work, but not independent evidence that changes followed the required problem → hypothesis → implementation → test → measurement → evaluation process.

Needed: dated hypotheses, experiment results, and acceptance/rejection records.

### Tier 3 — Controlled changes

The supplied material does not contain the change sequence or commit history needed to determine whether changes were kept narrow and declared before work began.

Needed: commit history or equivalent dated change records.

### Tier 3 — Fixed evaluation datasets

The tests refer to pinned CSVs and `MANIFEST.json`, but the actual fixture files and manifest were not included in the supplied text. I could not independently check their contents, hashes, origin, or stability.

Needed: the actual fixture files, manifest, origin metadata, and a reproducible dataset-generation procedure.

### Tier 3 — Version control

No repository history was supplied, and commit messages were explicitly withheld.

Needed: version-control history demonstrating real tracked changes rather than only source snapshots.

### Tier 3 — Known-good checkpoints

No tags, checkpoints, release artifacts, or repository history were supplied.

Needed: preserved known-good versions and evidence that they can be restored.

### Tier 3 — Rollback capability

No rollback mechanism or recovery exercise was supplied.

Needed: a documented rollback procedure and a test or exercise demonstrating restoration to a known-good engine state.

### Tier 3 — Documentation of significant decisions

The source contains extensive explanatory comments, including dated claims, but those comments alone do not establish a durable decision-record process or show that the records existed before each change.

Needed: dated architectural decision records or equivalent versioned decision artifacts.

### Tier 4 — Useful information over more information

Whether BTC context, Exit Watch, EV text, and the remaining panel fields provide useful information rather than unnecessary information cannot be established from source alone.

Needed: user/operator evidence, measured usage, or an explicit comparison of alternative panel designs.

### Tier 4 — Prefer simpler designs when invariants are equally satisfied

No alternative designs were supplied, so it is not possible to determine whether a simpler design would satisfy the same rules equally well.

Needed: competing designs and the documented tie-break decision.

---

## Part 4 — Test-suite assessment

### Specific Section 7.3 results

#### Tests that can pass without proving the engine works

The most important issue is the repeated pattern:

```python
if not _engine_available():
    print("SKIP: pandas_ta not installed")
    return
```

This is not a pytest skip. It is a passing test body. A dependency-missing environment can therefore report success while skipping many of the tests that matter most.

Other weak or vacuous checks include:

1. **Absent field checked through a default**

   `tests/test_degraded_state.py`:

   ```python
   assert risk.get("trade_quality_current", 0.0) <= ceiling
   ```

   The field is not in the final decision object. The assertion passes because the default is `0.0`, not because the degraded trade quality was actually capped.

2. **Empty collection exits without checking**

   `tests/test_decision_contract.py`:

   ```python
   if not SCHEDULED_FOR_REMOVAL:
       return
   ```

   and:

   ```python
   if not CANONICAL_ALIASES:
       return
   ```

   An empty state is currently intended, so these are not automatically defects. They nevertheless do not prove that the scheduling or alias mechanism remains meaningful if its contents are accidentally removed.

3. **Plotting test checks only absence of error logs**

   `tests/test_frame_ownership.py` collects only records with `levelno >= logging.ERROR`. A plotting path that omitted candles while emitting warnings—or no error at all—could pass without proving that candles were rendered.

4. **Golden snapshot can be re-baselined**

   `test_decision_object_matches_snapshot()` writes a new baseline when `PHASE7_UPDATE_SNAPSHOT` is set. That is useful operationally, but the test does not enforce independent review of the changed expected result.

5. **Known bad macro behavior is encoded as expected**

   `test_the_macro_series_is_actually_read()` expects missing macro data to produce `"NEUTRAL"`. That proves the missing file is read, but it also protects the silent-neutral fallback rather than requiring an honest degraded state.

6. **Static scans can test text rather than behavior**

   Several tests inspect source strings and absence of names. These are useful guards against specific regressions, but they can pass while the replacement behavior is absent or wrong.

### Failure injection

Some failure injection is well targeted:

- `ta.adx` and `ta.supertrend` are patched on the module actually imported by `indicators.indicators`;
- the risk calculation is patched at the class method used by the engine;
- the pinned source is used through the production fetch path;
- the state file is deliberately controlled in golden-path tests.

That is positive evidence.

I did not find a major instance in the supplied current tests where a deliberately injected failure is plainly at a code path the production engine cannot reach. However, the test suite contains enough absence-only and default-based assertions that a passing result is not equivalent to proof of correctness.

### Overall judgment

The suite does test the engine in some meaningful ways, especially:

- pinned end-to-end runs;
- selected indicator failures;
- data-integrity fixtures;
- contract shape;
- deterministic golden output;
- state-file comparisons.

But overall it tests **that selected implementation details have not changed** more strongly than it tests whether the engine is correct.

It is primarily a regression-lock suite consisting of:

- a single golden scenario;
- source scans;
- absence tests;
- authored failure tests;
- many tests that return successfully when dependencies are unavailable.

It does not adequately test:

- abnormal volume;
- failed macro degradation;
- partially invalid decision-bar indicators;
- full lineage;
- raw-vs-routed confidence semantics;
- risk/convection separation;
- all recorded configuration;
- actual chart content;
- complete malformed nested contracts.

The supplied description says a runner was included, but no `run_tests.py` file marker was present in the material provided here. I therefore could not independently assess the fallback runner’s actual behavior.

---

## Part 5 — Release gate

**Release gate: Not met.**

The Constitution requires that no unresolved Critical Tier 1 finding stand.

Critical findings remain for:

- Item 3 — abnormal volume can reach analysis;
- Item 8 / Item 13 — failed macro input is represented as neutral;
- Item 13 — partially invalid indicators can pass without degradation;
- Item 11 — overlapping evidence is counted as independent confirmation;
- Item 14 — conviction and entry quality select an aggressive action without an independent risk decision.

The engine should not pass the stated release gate until those findings are fixed and independently re-audited.

---

## Part 6 — Observations outside the Constitution

These are not additional graded findings.

1. **The pinned-source environment variable can silently fall back to live data.**

   `data/data_fetcher.py` returns `None` from `pinned_source()` when `PHASE7_PINNED_DATA` is set but points to a non-directory. The fetcher then uses the live API. A user who intended a pinned run can therefore receive live data without an explicit configuration error.

2. **`main.py` still creates a hardcoded `Logs` directory.**

   It correctly creates `config.LOG_DIR`, but later also executes:

   ```python
   os.makedirs('Logs', exist_ok=True)
   ```

   This can recreate the case-sensitive path split the rest of the remediation removed.

3. **The live API request has no timeout.**

   `data/data_fetcher.py` uses:

   ```python
   response = requests.get(url, params=params)
   ```

   without a timeout. This can leave a command hanging indefinitely during a network failure. This is an availability concern, not an execution concern.

4. **State persistence is not atomic.**

   `_save_state()` writes directly to the final JSON path. An interrupted write can leave a truncated file; `_load_state()` then silently treats it as no prior state. The current design documents that behavior, but an atomic replace would preserve the distinction between “first run” and “state write was damaged.”

5. **Panel numeric conversion does not reject non-finite values.**

   `core/panel_render.py`’s `safe_float()` converts `NaN` and infinity without checking finiteness:

   ```python
   return float(value) if value is not None else default
   ```

   This can produce visible `nan` or `inf` values rather than an explicit invalid-analysis message.

6. **The source comments contain claims about prior findings and remediation outcomes.**

   I treated those as project-authored claims and did not use them as evidence. No withheld audit materials were supplied to me, so I did not treat the audit as contaminated by those comments.