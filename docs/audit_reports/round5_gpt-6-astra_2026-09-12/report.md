I am ChatGPT, an OpenAI GPT-family model; my exact model/version is not available to me.

# Phase-7 re-audit â Parts 1â6

## Scope and evidence limitations

This report grades the supplied source against the supplied Constitution, not against earlier reviewersâ conclusions. It covers analytical output only, not trade execution.

**The release gate is not met on my findings.** I found three Critical defects: volatility is omitted from stop construction; entry quality can be scored for the opposite direction from the proposed plan; and an unavailable current VWMA can silently become an older reading.

### Package preflight

- The Constitution file contains the Constitution, including the 21/7/10/6 rule register. Its visible Version History ends at **LICENSED**. I found no previous engine-audit verdict table or outcome row there that triggers Section 2âs stop condition.
- The instruction supplied is **Rev 6**, notwithstanding the older âRound 2â title.
- The source and test bundles contain code corresponding to their names.
- **I did not execute the engine, tests, or cryptographic hashing.** No execution or filesystem tool is available in this call. Manifest hashes therefore remain unverified; I do not claim the package was altered.
- Important supporting artifacts are absent from the bundles and manifest: the pinned CSVs, their `MANIFEST.json`, `ohlcv_clean_4h.csv`, and `golden_decision.json`. Several supplied tests also require absent `docs/build/` modules. This is a **package limitation**, not evidence that those files are absent from the repository.
- The history reports an **unclean working tree**, but supplies neither the changed-path list nor its diff. I cannot establish that the bundled working-tree contents equal the stated HEAD.
- The seven-rule contamination disclosure is stale. For example, `tests/test_risk_regime_independence.py` explicitly states a prior verdict for **Item 14**, beyond the seven listed. I treated those statements as claims, not evidence of present compliance.

**Part 7 is omitted.** Its material was delivered in the same model context, so I cannot certify mechanical isolation from it. I have not used commit-message claims as evidence for the findings or grades below, and I cannot claim that a separate report file was saved before that material became available.

---

# Part 1 â Verdict table

âCompliantâ here means supported within the supplied artifact and the stated scopeânot certification of every possible deployment.

## Tier 1 â Invariants

| Rule | Short name | Verdict |
|---|---|---|
| Item 1 | Tool, not autonomous actor | Compliant |
| Item 2 | No future information | Compliant |
| Item 3 | Data integrity | Partially compliant |
| Item 4 | Determinism | Compliant |
| Item 5 | Reproducibility | Partially compliant |
| Item 6 | Traceability | Partially compliant |
| Item 7 | No unsupported predictive claims | Compliant |
| Item 8 | Epistemic honesty | Partially compliant |
| Item 9 | Precise measurement definitions | Compliant |
| Item 10 | Consistent semantics | Partially compliant |
| Item 11 | No circular reasoning | Partially compliant |
| Item 12 | No hidden decision-affecting state | Compliant |
| Item 13 | Fail safely | Partially compliant |
| Item 14 | Risk is not conviction | Compliant |
| Item 15 | Empirical evidence supersedes theory | Not verifiable |
| Item 16 | Complexity provides demonstrated value | Not verifiable |
| Item 17 | Backtesting isolated from core | Not verifiable |
| Item 18 | Read-only market access | Compliant |
| Item 19 | No withdrawal permissions | Compliant |
| Item 20 | Credentials never exposed | Not verifiable |
| Item 21 | Operator credentials stay local | Compliant |

## Tier 2 â Architecture

| Rule | Short name | Verdict |
|---|---|---|
| T2-1 | Separation of responsibilities | Compliant |
| T2-2 | Observation â interpretation â decision â risk/action | Compliant |
| T2-3 | Explicit interfaces/contracts | Partially compliant |
| T2-4 | Explicit configuration | Partially compliant |
| T2-5 | Modular design | Compliant |
| T2-6 | Controlled dependencies | Compliant |
| T2-7 | Explicit, evaluated interface/behavior changes | Not verifiable |

## Tier 3 â Process

| Rule | Short name | Verdict |
|---|---|---|
| T3-1 | Hypothesis-driven development | Not verifiable |
| T3-2 | Controlled changes | Not verifiable |
| T3-3 | Automated tests before acceptance | Not verifiable |
| T3-4 | Regression tests | Partially compliant |
| T3-5 | Fixed evaluation datasets | Not verifiable |
| T3-6 | Version control | Compliant |
| T3-7 | Known-good checkpoints | Not verifiable |
| T3-8 | Reproducible experiments | Partially compliant |
| T3-9 | Rollback capability | Not verifiable |
| T3-10 | Documentation of significant decisions | Compliant |

## Tier 4 â Preferences

| Rule | Short name | Verdict |
|---|---|---|
| T4-1 | Robustness over optimization | Compliant |
| T4-2 | Generalization over historical fit | Compliant |
| T4-3 | Explainability over unnecessary opacity | Compliant |
| T4-4 | Stability over flashy outputs | Compliant |
| T4-5 | Useful information over more information | Not verifiable |
| T4-6 | Simpler design as tie-breaker | Not verifiable |

### Positive evidence supporting Compliant verdicts

- **Items 1, 18, 19, 21:** The acquisition code makes a public klines request without an authentication header or credential parameter. Configuration has no credential slots. The simulator builds dictionaries and writes local JSON; it contains no order-submission operation or credential-upload path.
- **Item 2:** Confirmed swings explicitly wait for their right-hand confirmation window. The current pipeline decides at the last observed bar. Backfills in plotting operate on a copy and do not feed analysis. Further temporal qualifications appear below.
- **Items 4 and 12:** The numerical pipeline is deterministic given the actual inputs and settings. Cross-run Exit Watch state and pinned-source selection are documented. `BiasStateMachine.transition()` assigns its answer on every branch rather than retaining an undisclosed previous decision.
- **Item 7:** BTC adjustment is expressly labelled empirically unvalidated. EV is explicitly conditional and illustrative, rather than presented as a measured performance statistic. That qualification matters; concerns about its usefulness are in Part 6.
- **Item 9:** Source gives explicit formulas or semantic branches for confidence, trend health, entry quality, volatility, risk classification, and actions. Some names misdescribe those formulas; those are Item 10 findings, not absence of definitions.
- **Item 14:** Actual volatility and stop distance independently constrain risk acceptance, and the action-intensity gate consults risk regime. Sharing ADX with the conviction calculation does not, by itself, prove that directional conviction is being treated as equivalent to risk. Claims of statistical independence are a different matter and fail below.
- **T2-1, T2-2, T2-5:** Acquisition, indicators, structure, bias, entry scoring, risk, decision, and rendering remain identifiable stages. The orchestrator calls these stages rather than hiding them inside acquisition. Copying in structure, profile, and plotting protects caller ownership.
- **T2-6:** Direct third-party imports are declared and version-pinned; the internal dependency structure is inspectable. This is not confirmation that the actual runtime environment matches those pins.
- **T3-6:** The supplied history provides substantial commit-level change records, branches, and a tag.
- **T3-10:** Dated source comments record reasons for significant design decisions, including rejected alternatives. Some descriptions are stale, but the documentation practice itself is positively evidenced.
- **T4-1 through T4-4:** Copying rather than unsafe cache reuse, explicit refusal/degradation paths, parameterized symbols, price-relative calculations, component breakdowns, and qualification of experimental output support these preferences. Defects in implementing a preference do not automatically prove the opposite preference was selected.

---

# Part 2 â Findings

## F1 â Critical: the engine does not pass measured volatility into stop construction

**Rules:** Items 8 and 10; T2-4.

### Location

`core/engine_core.py`, the stop-construction call:

```python
atr_stop, t1, t2, t3 = self.risk_model.calculate_stop_targets(
    detailed_bias=detailed_bias,
    trend_health=trend["trend_health"],
    current_price=current_price,
    atr_val=atr_val,
    structural_level=hvn,
    bias_score=bias_score,
)
```

`models/risk_model.py`:

```python
volatility_state: str = "NORMAL"
```

and:

```python
if volatility_state == "HIGH VOLATILITY":
    vol_multiplier = VOL_MULT_HIGH
elif volatility_state == "LOW VOLATILITY":
    vol_multiplier = VOL_MULT_LOW
elif volatility_state == "EXTREME VOLATILITY":
    vol_multiplier = VOL_MULT_EXTREME
```

### Actual behavior

`volatility_mode` is computed before this call, but omitted from it. Consequently, the production call always uses multiplier **1.0**, regardless of the reported volatility.

The subsequent risk-validation call **does** receive `volatility_mode`. Stop construction and risk classification therefore operate under different volatility inputs on the same run.

### Broken clauses

- Item 8: distinguish âwhat is directly observedâ from what is derived or unknown.
- Item 10: âThe same term, score, or scale must mean the same thing in every module that uses it.â
- T2-4: important behavior must come from ânamed, visible configuration.â

### Concrete consequence

For a long with:

- price = 100;
- ATR = 3;
- trend health = 80;
- bias score = 60;
- structural level = 100;
- measured volatility = `HIGH VOLATILITY`;

the production call calculates:

```text
stop multiplier = 1.2 Ã 1.4 Ã 0.8 = 1.344
stop distance   = 4.032
stop            = 95.968
targets         = 104.032, 108.064, 112.096
```

Passing the measured volatility invokes the declared 1.35 multiplier:

```text
stop distance   = 5.4432
stop            = 94.5568
targets         = 105.4432, 110.8864, 116.3296
```

These are materially different price levels. The high-volatility regime need not reject the trade, so this is not necessarily contained by downstream validation.

**Why Critical:** Wrong stop and target numbers can reach the operator on an otherwise valid analysis.

**Required action:** Pass the measured volatility explicitly, preferably make the parameter required, and test the production call rather than only direct `RiskModel` calls.

**Verification:** A routed high-/low-volatility test must demonstrate that the configured multipliers affect the emitted levels when structure does not dominate the stop.

---

## F2 â Critical: entry quality can be evaluated for LONG while the plan and action are SHORT

**Rules:** Items 8 and 10.

### Location

`core/engine_core.py`:

```python
eq_trade_direction = "SHORT" if short_signal else "LONG"
```

`models/entry_model.py`:

```python
if trend_exhaustion or (reversal_strength is not None and reversal_strength > 0):
    return False, False
```

`models/decision_model.py` chooses direction from:

```python
if raw_bias == "BEARISH":
```

It no longer requires `short_signal`.

### Actual behavior

A false short-entry signal does not mean that the analysis is long. It can mean:

- a reversal warning exists;
- macro opposes the short;
- structure does not meet the entry-signal gate;
- the bias is not confirmed.

Nevertheless, every such case is scored as LONG. The decision model can subsequently issue a short action using that opposite-side score.

The plan/action coherence guard cannot detect this: it compares the action with target ordering, not with the direction used to calculate entry quality.

### Broken clauses

- Item 10: consistent meaning of the same score across modules.
- Item 8: distinguish what the derived number actually represents.

### Concrete consequence

Consider a bearish confirmed bias, bearish trend, bearish macro, bearish BOS, no exhaustion or momentum divergence, and a small positive reversal score. The reversal score makes both entry signals false.

For a base entry score of 70:

```text
Current LONG interpretation:
70 Ã 0.90 Ã 0.90 Ã 1.00 = 56.70

SHORT interpretation:
70 Ã 1.05 Ã 1.05 Ã 1.05 = 81.03375
```

With trend health 80, an active zone, and normal risk, the wrong score can change **AGGRESSIVE SHORT** into **CONSERVATIVE SHORT**.

The supplied second transcript already exposes the direction split: a bearish plan receives a bullish-macro entry multiplier of **1.05** and a bearish-trend multiplier of **0.90**. In that particular combination their product happens to equal the reversed pairâs product; it is evidence of the wrong scoring direction, not by itself evidence of a numerical difference.

**Why Critical:** A materially wrong entry-quality number can directly select the operator-facing action.

**Required action:** Establish one explicit candidate-plan direction and pass it into risk construction and entry scoring. Do not infer it from the absence of an entry signal. Record the scored direction.

**Verification:** Exercise bearish runs where `short_signal` is false for each reason above, including a small reversal warning, and compare the emitted score with a direct SHORT calculation.

---

## F3 â Critical: an unavailable current VWMA silently becomes an older reading

**Rules:** Items 3, 8 and 13.

### Location

`indicators/indicators.py`:

```python
df["VWMA"] = np.where(valid_mask, price_volume_sum / volume_sum, np.nan)

if df["VWMA"].isna().any():
    df["VWMA"] = df["VWMA"].ffill()
```

The final unusable-indicator sweep excludes VWMA.

`data/validation.py` rejects:

```python
if len(volume) and (volume == 0).all():
```

but not a zero-volume trailing window in an otherwise nonzero series.

### Actual behavior

The indicator first correctly marks a zero-volume window as unmeasured, then overwrites that absence with the preceding valid VWMA. No failure is recorded.

This is precisely the trailing-edge problem that `clean_series()` now prevents for other indicators.

### Broken clauses

- Item 3: missing or abnormal inputs must be detected before becoming analysis.
- Item 13: missing or invalid data must reduce confidence or halt output, ânever invent a confident-looking answer.â
- Item 8: an older measurement must not be presented as the current derived quantity without qualification.

### Concrete consequence

Take valid positive-price history with earlier positive volume and its last 20 volumes equal to zero. Validation accepts it because the entire series is not zero.

If the last valid VWMA was 100 and current price is 100, entry scoring awards:

```python
vwma_pts = VWMA_MAX_POINTS
```

That is **20/20 for the current VWMA-distance component**, although the current window has no defined VWMA. The missing VWMA does not itself degrade the run.

### Related surviving volume paths

`structure/structure.py` changes the quantity after zero weights:

```python
except ZeroDivisionError:
    vwma_recent = c_recent.mean()
    vwma_prev = c_prev.mean()
```

It then uses those unweighted means as VWMA inputs to volume-sentiment classification without reporting the substitution.

Also, the spike detector examines only the last `VWMA_LENGTH` bars, while the volume profile consumes the complete frame. An extreme bar immediately outside that detection window can dominate HVN and stop geometry without being flagged.

**Why Critical:** A false current indicator reading changes an entry-quality number used by the decision model.

**Required action:** Preserve unavailable decision-bar VWMA, report its absence, and stop silently relabelling arithmetic means as volume-weighted measurements. Align anomaly-detection coverage with the histories actually consumed.

**Verification:** Use a nonzero prefix followed by 20 zero-volume bars, plus isolated spikes at positions immediately inside and outside the current detection window.

---

## F4 â Major: time-axis validation accepts absent axes and future-dated live data

**Rule:** Item 3.

### Location

`data/validation.py`:

```python
ts = _timestamps(df)
if ts is None:
    return None
```

and:

```python
minutes = _interval_minutes(timeframe)
if minutes is None:
    return None
```

The currency check only rejects:

```python
if age > limit:
```

### Actual behavior

A timestamp-free pinned CSV can be accepted as OHLCV. Unsupported timeframe strings disable both interval and staleness checks. A regularly spaced live response whose final timestamp is in the future has negative age and passes the currency check.

### Broken clause

Item 3 explicitly requires detection of âmissing candlesâ and âtimestamp inconsistencies.â

### Concrete consequence

A pinned file with 450 valid OHLCV rows but no `timestamp` column passes `load_csv()` validation. The engine accepts its positional index and performs analysis even though candle spacing, duplicates in time, and the claimed `4h` timeframe cannot be established.

Separately, shift every timestamp in an otherwise current live response forward by one day. Spacing and monotonicity remain valid; negative age is accepted.

**Why Major:** These are actual validation holes, but I have not executed a fixture demonstrating a resulting wrong market number. Future timestamps are not, by themselves, proof of actual future-information access.

**Required action:** Require a valid time axis on engine data paths, reject unsupported intervals or explicitly mark them unvalidated, and reject future timestamps outside a stated clock tolerance.

**Verification:** Positive control on valid current candles; negative controls for missing timestamps, unsupported intervals, and future-dated responses.

---

## F5 â Major: the claimed independence fix leaves shared ADX/RSI evidence in multiple bias factors

**Rules:** Items 8 and 11.

### Location

`indicators/trend_health.py` builds trend health with:

```python
adx_strength = 0.0 if adx_val is None else min(max(adx_val, 0.0) * 1.2, 40.0)
```

and builds continuation with:

```python
adx_component = (min(max(adx_val, 0.0), 50.0) / 50.0) * 25.0
```

Both also use RSI.

`models/bias_engine.py` combines them:

```python
signed_trend_health * WEIGHT_TREND_HEALTH
...
reversal_continuation_score * WEIGHT_REVERSAL_CONTINUATION
```

Its dependency comment says each factor is meant to be âgenuinely independent of the other five.â The trend-health comment says the remaining continuation inputs have âno other channel into bias_score.â

### Actual behavior

Removing `health_component` removed one direct dependency. It did not remove shared underlying measurements.

### Broken clauses

- Item 11: a signal must not reinforce itself through derived layers and be âpresented as independent confirmation.â
- Item 8: correctly distinguish what has been established.

### Concrete consequence

Hold positive slopes, RSI 60, acceleration zero, reversal zero, and other bias factors fixed. Change ADX from 20 to 30:

- trend health rises by 12, adding **3.6** to bias;
- continuation rises by 5, adding another **0.5**.

One ADX change adds **4.1 bias points through two purportedly independent factors**.

Macro and volume also remain displayed under âValidationâ despite already contributing to bias. Their removal from the confidence bonus is real, but it does not make the displayed validation independent.

**Why Major:** The arithmetic is defined, not fabricated. The defect is duplicated evidence presented with an independence claim. It can influence decisions, but I do not equate every correlated heuristic with a Critical numerical error.

**Required action:** Either remove the duplicate contribution or describe and justify the dependent composite honestly. Do not claim independence merely because a direct reference to `trend_health` disappeared.

**Verification:** Perturb raw ADX and RSI through the complete trend-to-bias calculation, recording every contribution that moves.

---

## F6 â Major: BTC failure handling contradicts the âinformational only, unaffectedâ contract

**Rules:** Items 8 and 13.

### Location

`core/engine_core.py`:

```python
for _d in btc_trend.get("degraded_inputs", []) or []:
    degradation.append(f"BTC {_d}")
```

That list reaches `DecisionModel._apply_degradation()`, which caps confidence and can replace a directional action with NO-TRADE.

Meanwhile:

```python
for f in btc_failures:
    logger.warning(f"BTC context indicator failure: {f}")
```

BTC structure `degraded_inputs` are not propagated or otherwise published as BTC availability information.

`core/panel_render.py` says:

```text
BTC Market Context (informational only -- does not change BIAS or DECISION above)
```

### Actual behavior

BTC failures receive different treatment according to where they surface:

- a BTC trend degradation can change the primary action;
- a BTC SuperTrend failure can leave context available with a missing factor scored as zero;
- a BTC structure failure can leave context available without its degradation being exposed.

### Broken clauses

- Item 8: distinguish observed, derived, and unknown.
- Item 13: missing inputs must not silently produce confident-looking output.

### Concrete consequences

1. Fail only BTC ADX while retaining a healthy base analysis. BTC trend reports ADX absent; the primary run becomes degraded and can lose its directional action, despite the panelâs promise that BTC does not change that decision.
2. Fail only BTC SuperTrend. Its failure is logged, but trend health need not report degradation because it does not read SuperTrend. BTC bias loses its 15% direction factor while `available=True` and the adjusted confidence can still be presented without a missing-input disclosure.

**Why Major:** The optional-context contract is false, and some missing BTC evidence is hidden. This is not simply an unavailable optional panel.

**Required action:** Give BTC context its own completeness/degradation contract. Decide explicitly whether it may veto the primary analysis, then make code, panel, and tests agree.

**Verification:** Inject failures separately into BTC ADX, SuperTrend, ATR, and structure, leaving base and macro calculations untouched.

---

## F7 â Major: reconstruction is not guaranteed, and archive identity can overwrite earlier code metadata

**Rules:** Items 5 and 6.

### Locations

`core/decision_log.py`:

```python
except Exception:
    return None
```

The router still returns the analysis after this failure.

`core/lineage.py`:

```python
RETENTION_DAYS = 90
```

and:

```python
with open(path, "wb") as fh:
```

`core/engine_core.py` deliberately excludes `code_id` from `run_id`, but writes it into archive metadata.

### Actual behavior

The normal path records useful inputs and lineage. However:

- a failed decision-log write can leave no durable decision record;
- a failed archive write can leave no retained raw input;
- pruning removes the only retained input after 90 days;
- the same input/settings hash is reused after code changes that do not change the enumerated settings, overwriting earlier archive metadata.

### Broken clauses

- Item 5: âEvery analysis must be reconstructable later.â
- Item 6: every major output must have an explainable lineage back to raw source data.

### Concrete consequences

- A run completes with an unwritable log directory. The operator receives an analysis, but after process exit its decision, prior state, and configuration need not be recoverable.
- The exchange revises historical candles after the local archive has been pruned. The retained hash can detect a mismatch; it cannot reconstruct the original input.
- Change a bare comparison in decision logic, then rerun identical candles and enumerated settings. The decision log can retain different `code_hash` values, but the shared archive filename now holds only the later `meta.code`, including its interpreter and per-file hashes.

The source fingerprint identifies source currently on disk; it does not archive that source or prove those bytes are the already-imported runtime code.

### A separate canonicalization defect

`core/lineage.py::_index_label()` binds:

```python
iso = getattr(label, "isoformat", None)
```

before replacing `label` with a UTC-converted object, then calls the original bound `iso()`.

Thus equivalent timezone-aware timestamps can hash differently despite the documented UTC-normalization contract.

**Why Major:** These are evidence-retention and reconstruction defects, not fabricated market numbers or false successful-write announcements.

**Required action:** Define an explicit reconstruction period consistent with the governing standard; retain immutable per-analysis metadata; separate deduplicated input storage from per-run code/environment identity; and correct the bound-method timezone bug.

**Verification:** Reconstruct after a code change, after source-data revision, with non-UTC equivalent timestamps, and after failed writes. The existing âdelete archive and compare against the original fixtureâ test does not demonstrate reconstruction.

**Reading chosen:** The Constitution invites an explicit retention decision but does not state that such a decision overrides âevery analysis must be reconstructable.â I grade the unmet guarantee rather than treating a source comment about a ruling as an amendment.

---

## F8 â Major: a boolean risk verdict is accepted without a usable plan; assembly then invents levels

**Rules:** Items 10 and 13; T2-3.

### Location

`models/signal_router.py::_validate_engine_output()` checks section presence and whether `risk_valid` is boolean, but not plan completeness.

`models/decision_model.py`:

```python
plan = self._plan_direction(risk)
if plan is None:
    return final_action
```

Router assembly:

```python
targets = risk.get("targets", (0.0, 0.0, 0.0))
```

```python
"atr_stop": float(risk.get("atr_stop", 0.0))
```

### Actual behavior

A risk block containing `risk_valid=True` can pass without a stop or targets. A directional action survives when plan direction cannot be established. Assembly then supplies zero price levels.

The direction guard also does not inspect the stop, current price, or intermediate target ordering. Despite its description, it checks only first versus last target.

### Broken clauses

- Item 13: contradictory or missing data must not yield a confident-looking answer.
- Item 10: a âpassed riskâ result and a usable risk plan must not silently separate.
- T2-3: module input/output contracts must be explicit and accurate.

### Concrete consequence

A stub engine returns:

```python
bias = {"raw": "BULLISH", "score": 60}
trend = {"trend_health": 80, "trend_direction_sign": 1}
entry = {"score": 80, "entry_status": "ACTIVE ENTRY ZONE"}
risk = {"risk_valid": True, "risk_regime": "NORMAL RISK"}
structure = {}
exit = {"current_price": 100}
```

The validator accepts it; the decision model can produce AGGRESSIVE LONG; the router records a zero stop and three zero targets.

**Reachability qualification:** The supplied healthy producer normally supplies these fields. This is a latent seam defect exposed by malformed output, not evidence that ordinary market input currently makes the producer omit them.

**Why Major:** Contained behind the current producerâs behavior, but the advertised defensive contract fails.

### Additional contract mismatch

`BtcContextBlock` declares:

```python
correlation: float
beta: float
```

Both legitimately become `None`. Making their keys optional does not make their values nullable. The positive-fixture contract test misses this state.

**Required action:** Validate plan shape and geometry; distinguish âno planâ from âcoherent planâ; use nullable types for optional measurements; eliminate price-shaped assembly defaults.

**Verification:** Missing plan, equal targets, a nonfinite middle target, wrong-side stop, and available BTC context with `None` correlation/beta.

---

## F9 â Major: `confidence_score` still names two different quantities

**Rule:** Item 10.

### Location

`core/engine_core.py`:

```python
"confidence_score": trend["trend_health"],
```

`models/signal_router.py`:

```python
"confidence_score": float(confidence),
```

where `confidence` is bias magnitude, possibly capped for degradation.

### Actual behavior

The raw engine output and final decision use the same field name for different calculations. The router ignores the raw field and replaces it.

### Broken clause

Item 10: âThe same term, score, or scale must mean the same thing in every module that uses it.â

### Concrete consequence

On a run with trend health 95.35 and bias magnitude 78.70, a caller of `Phase7Engine.run()` receives approximately 95.35 under `risk.confidence_score`; a routed caller receives approximately 78.70.

Both are declared output forms of the project.

**Why Major:** The normal panel path is protected by replacement, so this is contained rather than a demonstrated wrong panel number.

**Required action:** Remove the unread raw field or rename it to its actual meaning. Prefer not to publish a placeholder for a quantity computed at a later stage.

**Verification:** Contract tests must cover both `EngineOutput` and `DecisionObject`, including semantic identities, not only key presence.

---

## F10 â Major: several operator-facing statements misdescribe the calculation or failure

**Rules:** Items 8 and 10.

### A. âDistance from zoneâ is distance from its midpoint

`models/entry_model.py`:

```python
dist_to_mid = abs(close - zone_mid)
distance_from_zone = float((dist_to_mid / close) * 100.0)
```

The panel prints:

```text
ZONE DISTANCE : ...% away from zone
```

With zone `[0.9, 1.1]` and price `1.05`, price is inside the zone, but the output reports approximately **4.76% away from zone**.

The ACTIVE condition is also:

```python
dist_to_mid <= zone_width
```

rather than half the width. Price `1.15` is therefore ACTIVE for the displayed `[0.9, 1.1]` zone.

This may be an intentional expanded scoring band, but the displayed zone and its semantics do not explain it.

### B. Undefined correlation is falsely attributed to missing timestamp pairs

`models/btc_context.py` can return NaN correlation with positive `n` when BTC variance is zero.

The panel says:

```text
AERO and BTC could not be paired by timestamp this run
```

The decision reasoning says:

```text
the two series share no paired timestamps
```

Thirty-one identical shared timestamps with constant BTC closes contradict both explanations.

### C. Neutral asset bias is misreported as neutral BTC bias

`_compute_btc_adjusted()` sets `agreement=0` when either side is neutral, then says:

```python
agree_phrase = "BTC isn't showing a clear directional bias either way right now"
```

With asset score 0 and BTC score 60, that statement is false about BTC.

### D. Conservative-action reasoning blames entry quality even when another condition failed

The conservative branch says entry quality âisn't strong enough.â With health 60, entry score 90, agreeing macro, and valid risk, it can take this branch because **health** failed the higher gateânot entry quality.

Likewise, momentum divergence can prevent the higher branch while entry quality exceeds 70.

### Broken clauses

- Item 8: distinguish the actual observation, derivation, and unknown.
- Item 10: consistent semantics of âzone,â âdistance,â and directional labels.

**Why Major:** These are misleading explanations or labels for defined calculations, not evidence that a trade was executed or an audit file saved when it was not.

**Required action:** Name midpoint distance explicitly, distinguish the scoring envelope from the displayed zone, and construct reasons from the actual failed condition.

**Verification:** Direct tests for all four cases, asserting the relevant field or complete sentenceânot merely absence of an old phrase.

---

## F11 â Major: regression checks can pass without exercising their claimed property, and experiments retain uncontrolled inputs

**Rules:** T3-4 and T3-8.

### Broken clauses

- T3-4: âA new improvement must not silently destroy previously working behavior.â
- T3-8: another person must be able to rerun a validation test and obtain the same measured result.

### Specific evidence and practical failures

1. **False directional-producer coverage**

   `tests/test_trend_direction_source.py::test_trend_health_reports_a_sign_that_matches_its_own_label`

   The fixture contains OHLCV but no EMA slopes, ADX, or RSI. `compute_trend_health()` takes its missing-slopes default, returning NEUTRAL/0 for both ramps. The variable `expect` is unused.

   A producer permanently returning NEUTRAL/0 satisfies this test.

2. **Purported perturbations do not reach the function**

   `tests/test_no_circular_reasoning.py` defines:

   ```python
   def confidence_with(structure_regime, raw_bias):
   ```

   but does not pass or otherwise use `structure_regime`. Another test calls `_compute_confidence()` twice with identical arguments and calls the results âstrongâ and âweak.â

   These do not test perturbation propagation through the complete pipeline.

3. **The directional end-to-end control never checks an action**

   `tests/test_timeframe_disagreement.py::test_the_engine_still_reaches_a_side_when_the_timeframes_agree`

   It asserts bullish bias and macro, but never asserts LONG. A decision model permanently returning WAIT can satisfy that supposed counterweight.

4. **Smoke reproducibility can compare two failures**

   `tests/test_smoke.py::test_the_smoke_run_is_reproducible`

   It compares two returned dictionaries without requiring either to be a successful analysis. Two identical error objects pass.

   It also does not reset prior state, unlike the golden-path harness, so its inputs need not actually be identical.

5. **A clean-checkout experiment uses uncontrolled network input**

   `tests/test_clean_checkout.py::test_main_runs_without_a_logs_directory`

   It launches `main.py` without pinning data or blocking requests. Network conditions and inherited environment can change its behavior. The sole assertion is absence of `"Traceback"`.

   A `main.py` that immediately exits without running an analysis can satisfy it.

**Why Major:** These weaknesses undermine regression protection and repeatability. They do not establish that every change was accepted without testing; that historical process question remains Not verifiable.

**Required action:** Add successful-run preconditions, assert the supposed control outcome, perturb raw inputs through their real consumers, control prior state and environment, and block network access structurally.

**Verification:** Run focused mutantsâalways-neutral trend output, always-WAIT decisions, empty explanations, and deterministic error returnsâand require the relevant tests to fail.

Further test-specific observations follow in Part 4.

---

## F12 â Minor: current source descriptions remain materially stale

**Rule:** Item 8, contributing to its Partially compliant verdict.

These are not merely old incidents clearly quoted as history; several describe current behavior incorrectly.

| Location | Claim | Supplied code |
|---|---|---|
| `indicators/indicators.py`, ADX failure consequence | ADX contributes â25 of its 100 pointsâ | Trend-health ADX contribution reaches 40 |
| `indicators/trend_health.py`, missing-slopes comment | Slopes are âthe only inputs trend health itself is computed fromâ | ADX and RSI are added directly |
| `models/bias_engine.py`, dependency graph | Structure regime is âswing-basedâ | `_detect_regime()` compares 5- and 15-close means |
| `models/risk_model.py`, class docstring | Provides position sizing and leverage adjustment | That function is removed |
| `structure/structure.py::_detect_hvn_lvn` | Falls back to adaptive-lookback price extremes | It now raises instead |
| `core/engine_core.py`, `risk_inputs` comment | Trend health no longer feeds the risk decision | It still feeds stop geometry through `trend_factor` |
| `requirements-dev.txt` | Suite runs âwith no pytest at allâ | Many modules import pytest; runnerâs own correction acknowledges this |

**Practical consequence:** A maintainer following these descriptions can audit the wrong dependency, misstate the consequences of a failed indicator, or install an environment that cannot run the advertised suite.

**Why Minor:** The listed comments do not themselves change the calculated market result. More consequential false independence and output claims are graded separately above.

**Required action:** Separate historical notes from current contracts, and correct current-tense descriptions against code.

---

# Part 3 â Not verifiable

| Rule | Missing evidence |
|---|---|
| Item 15 | Measurements paired with theoretical expectations and an acceptance/rejection record showing which prevailed. |
| Item 16 | Demonstrated problem/value evidence for retained layers. Being consumed is not proof of measurable value. |
| Item 17 | A concrete isolation and recovery demonstration for validation tooling, including a verified known-good recovery target. Absence of a backtester alone does not establish the full invariant. |
| Item 20 | Current code shows no apparent exchange credentials, but the supplied metadata cannot establish that no secret was ever committed, logged, or exposed through historical artifacts. |
| T2-7 | The actual interface diffs and pre-acceptance downstream evaluation records. Current declarations already show some drift. |
| T3-1 | Dated hypotheses, measurements, evaluations, and accept/reject decisionsânot only explanations written beside completed fixes. |
| T3-2 | Evidence that scope and reasons were stated before work began. Commit size and timestamps alone cannot establish that. |
| T3-3 | Test-execution evidence tied to each meaningful change before acceptance. The package contains engine transcripts, not complete test/acceptance records. |
| T3-5 | The actual pinned datasets, golden snapshot, fixture manifest, and their provenance. Generated synthetic cases are supplied, but the principal baseline cannot be inspected. |
| T3-7 | Tag targets and evidence that preserved checkpoints actually worked before significant modifications. An âauditedâ tag is not by itself a known-good designation. |
| T3-9 | A demonstrated rollback to a working version, including treatment of persistent state and compatibilityânot merely commit history. |
| T4-5 | Evidence that the retained information improves operator decisions or usability compared with a smaller panel. |
| T4-6 | An actual comparison between designs satisfying the invariants equally well. The tie-breakerâs precondition is not established. |

The large number of Not verifiable process verdicts reflects missing **process evidence**, not a claim that the processes did not occur.

---

# Part 4 â Test suite assessment

## Overall judgment

**This suite tests both behavior and implementation stability, but several of its strongest-sounding claims exceed what its assertions establish.**

There is valuable behavioral coverage:

- malformed acquisition responses;
- actual indicator exceptions;
- missing decision-bar values;
- shifted BTC timestamps through the router;
- write failures;
- archive round trips;
- timestamp-paired correlation;
- positive and negative direction controls.

It is substantially more than a snapshot-only suite. Nevertheless, it is not sufficient evidence that the engine is correct. The Critical stop-volatility and entry-direction seams are not covered by the supplied tests.

## Additional Section 7.3 results

### Empty collections and early returns

- **`tests/test_decision_contract.py` â scheduled removals:** returns immediately when `SCHEDULED_FOR_REMOVAL` is empty. That is legitimate conditional coverage, but it performs no current assertion and should not be described as evidence of a checked removal.
- **Same file â aliases:** returns on an empty alias map. When populated, it compares only if both fields exist; a missing alias or canonical field is silently ignored.
- **`tests/test_pinned_source.py::test_manifest_hashes_match_the_files`:** an empty `manifest["series"]` produces no mismatches and passes. The separate completeness test does not require a complete manifest series list.
- **`tests/test_lineage.py::test_the_written_record_is_json_and_holds_no_non_finite_numbers`:** an existing empty log file passes the loop. No record count is required.
- **`tests/test_golden_path.py::test_the_snapshot_covers_every_top_level_field`:** missing snapshot prints `SKIP` and returns, reporting a pass under pytest.
- **Golden update mode:** any nonempty `PHASE7_UPDATE_SNAPSHOT`, including `"0"`, enables rewriting and bypasses comparison. This is an intentional maintenance mode but an uncontrolled inherited variable can disable the regression check.

### Absence-only assertions

- **`tests/test_frame_ownership.py`:** ownership checks pass if the operation simply does nothing.
- Its companion plotting test checks only absence of ERROR logs. A no-op renderer that emits no error still passes; it does not require a chart file or candle artists.
- **`tests/test_no_circular_reasoning.py::test_the_panel_prints_trend_health_once`:** `renders <= 2` also passes if trend health disappears entirely.
- **Same file, reasoning tests:** empty reasons satisfy the negative phrase checks.
- **`tests/test_golden_path.py` hardcoded-symbol and doubled-phrase tests:** empty BTC context or empty explanations can satisfy them.
- **`tests/test_timeframe_disagreement.py` coherence property:** skips a missing plan and makes no directional comparison when the action has no side. Appropriate for a conditional property, insufficient as proof that actionable coherent plans remain possible.
- **`tests/test_degraded_state.py` cap test:** missing risk fields default to zero and satisfy the ceiling assertions. It does not require a successful decision or populated risk block.

### Setup does not prove the stated claim

- The directional trend test and pseudo-perturbation tests are detailed in F11.
- **`tests/test_entry_score_reconciles.py::test_each_component_can_actually_reach_its_stated_maximum`:** checks four components, not ATR distance.
- **`tests/test_risk_fingerprint.py::test_each_target_is_computed_from_its_own_fingerprinted_multiplier`:** changes only `TARGET2_MULT`; the name overstates coverage of all three.
- **Same file, volatility test:** calls `_plan(volatility_state="HIGH VOLATILITY")` directly. It proves the risk method reads the multiplier, not that the engine passes volatility. F1 survives.
- **`tests/test_no_risk_free_conviction.py`:** most action tests use hand-picked regime strings. The separate classifier tests do not establish the entire classifier-to-action integration. The bearish helper also supplies a positive bias score, an inconsistent fixture whose sign is currently hidden by `abs()`.
- **`tests/test_no_fabricated_fallbacks.py`:** fallback equivalence is checked at one final bar of a 300-row fixture, with default lengths. It does not cover the 100-row macro frame, shorter accepted histories, or changed lengths.

### Source scans can pass on prose or skip the relevant module

- **`tests/test_decision_bar_integrity.py`:**
  - SuperTrend-level coverage searches for `"SuperTrend's level"` in source;
  - panel finiteness coverage searches for any `math.isfinite` or `np.isfinite`.
  
  Neither proves the particular output is guarded.
- **`tests/test_explicit_configuration.py`:** âreadâ detection counts names in strings and docstrings, including the fingerprint list itself. Merely recording a setting can satisfy a test meant to prove it steers calculation.
- Its `_engine_sources()` strips everything after `#`, including `#` inside strings. In `utils/plotting.py`, hexadecimal color strings make that transformed source invalid Python. The AST-based callers catch `SyntaxError` and skip the module.
- **`tests/test_risk_fingerprint.py`:** `source.count(name) >= 2` counts explanatory comments as reads.
- **`tests/test_traceability.py`:** existence of `"empirically unvalidated"` anywhere in source does not establish that the label reaches a rendered BTC number.
- **`tests/test_no_lookahead.py`:** the scanner detects particular backfill spellings, not linear interpolation using a later endpoint, centered rolling windows, negative shifts, or full-series statistics.
- **`tests/test_fetch_and_import_hygiene.py`:** the timeout scan passes if all request calls disappear; existence of the settingâs name elsewhere does not prove it is the timeout argument.

### Repeatability and isolation

- **`tests/test_exit_model_removal.py::test_current_price_survives_the_removal`:** changes the shared fetcherâs `base_url` without restoring its original value.
- Many tests clear pinned state rather than restoring the previously active state.
- **`tests/test_pinned_source.py::test_environment_variable_activates_the_pinned_source`:** asserts no pin is active before clearing the inherited environment variable. It can fail in an intentionally pinned test environment.
- The real-log integrity alarm compares file names and sizes, not content. A same-size overwrite escapes it. It also runs before later tests, a limitation its docstring acknowledges.
- **`run_tests.py`** calls each test without fixtures or parameter expansion. Parameterized/fixture-taking tests therefore do not exercise their cases through this runner. It also returns success when a filter selects zero tests.
- The import-check list does not include every current engine utility. Its âevery moduleâ wording is broader than its enumerated coverage.

### Deliberate non-findings

- Returning after an expected exception has been checked is not a vacuous pass.
- Returning when both pre- and post-test log directories are absent is a valid successful comparison.
- Negative security scans are useful even though they assert absence. Their limitation is that a finite list of dangerous spellings is not a complete capability proof.
- A reference correlation calculation resembling the implementation is not automatically worthless. Here the positional-vs-aligned negative control gives it useful discriminatory power, although an additional differently implemented oracle would strengthen it.

## Requested improvement in test strategy

Prioritize **cross-module contract tests** and **mutant-based checks of test effectiveness** over further inventories of forbidden names.

The most valuable immediate cases are:

1. volatility reaches stop construction;
2. entry-scoring direction equals candidate-plan direction;
3. unavailable current VWMA remains unavailable;
4. each optional BTC failure has consistent consequences;
5. a nontrading result cannot satisfy a test intended to prove trading remains possible.

---

# Part 5 â Release gate

**Not met.**

On this report alone, the following Critical Tier 1 defects remain unresolved:

1. **F1:** measured volatility does not reach stop construction;
2. **F2:** entry quality can be calculated for the wrong direction;
3. **F3:** unavailable current VWMA can be replaced by an older reading without degradation.

These conclusions arise from source-level data-flow and arithmetic. They are not claims that I observed a live execution.

The supplied transcripts do not negate them: one rejects on excessive stop distance, and the other waits. Neither demonstrates the relevant successful directional paths.

---

# Part 6 â Observations outside the Constitution

## A. Audit-method DEFECT observations

### Conflicting severity rubrics

The Constitution uses **Critical / Major / Moderate / Minor** and defines Critical broadly by reaching a live decision or customer. Section 6 of the instruction uses three levels and a narrower Critical criterion.

I used the **instructionâs explicit three-level reporting rubric**, while stating practical consequences and reachability. This should be reconciled before comparing severity counts across reports.

### Release-gate attribution

I did not locate the quoted release-gate condition in the supplied 29-page Constitution excerpt. I evaluated the gate as explicitly specified by the review instruction rather than attributing an unseen clause to the standard.

### Truncation description

The excerptâs contents and footnote markers refer to a glossary âat the very end,â but no glossary is supplied. Thus the truncation appears to remove explanatory material as well as later outcome rows. The rule text is readable enough to audit; the description of what was removed should be corrected.

### Pressure to find defects

âA report that finds nothing will be assumed to mean the audit failedâ is not an independence safeguard. It creates an incentive to report defects regardless of evidence. The accompanying instruction not to manufacture findings mitigates but does not remove that pressure.

### Identity and training-exposure evidence

I cannot confirm the named GPT-6 deployment from this context. The actual API model identifier should be retained externally.

The described billing evidence is not supplied here. Even if accurate, a paid/standard routing label alone is not proof of training exclusion; the applicable data policy and routing settings matter. Such evidence cannot exclude public-repository training exposure or certify a later modelâs complete training history.

I have no specific recognition of this project to disclose beyond reading the supplied material. That is not proof that it is absent from training data.

---

## B. Section 7.5 â temporal operations, scoped to the actual engine

I found these relevant operations:

- `clean_series(method="interpolate")` uses linear interpolation. `limit_direction="forward"` does **not** make interpolation causal: an interior gap can still use its later endpoint.
- `clean_series()` uses whole-series mean and standard deviation for outlier removal. Earlier rows can therefore be revised using later rows.
- `calculate_structure()` broadcasts the final regime and volume-node levels across the frame.
- Confirmed swings inspect both sides of a pivot, but only accept pivots far enough behind the current bar to have completed confirmation.
- Plotting retains `.ffill().bfill()` on its own copy.

For the supplied engine, which makes one decision after observing the final frame, these do not establish a current look-ahead violation: the later rows involved are already available at that decision. The interpolation branch also has no production caller in the supplied source.

They would require renewed examination before historical row-by-row decisions. In particular, the existing backfill scanner is not a sufficient temporal-safety test.

---

## C. Claimed fixes I could not fully confirm

- **EMA/RSI/ATR fallback equivalence:** The primary library implementation is not supplied. The tests establish, at most, near-equality on one long fixture. Different initialization and short-history behavior need direct comparison on the pinned library version.
- **Raw-input reconstruction across environments:** The archive round-trip test uses the current source, current environment, explicit fixture-derived symbol/timeframe choices, and reset prior state. It does not demonstrate recovery from the retained artifacts alone in a later environment.
- **Full test isolation:** The central redirection is useful, but filtered fallback-runner invocations need not load `conftest` before engine-running tests. The runner itself does not install that safeguard.
- **Timeout guarantee:** `requests` read timeout is an inactivity timeout, not a total-request deadline. The comment claiming a 30-second worst case is incorrect for a peer that keeps supplying data slowly. This is an availability/documentation concern, not an execution concern.
- **CLI behavior on logging failure:** The router tolerates unwritable logs, but `main.py` still creates a directory and constructs a `FileHandler` at import time, before its `try`. The advertised tolerance does not hold uniformly across entry points.

---

## D. Design observations, not additional graded rules

- The EV text is explicitly hypothetical, which is why I did not fail Item 7 merely for its existence. Nevertheless, converting a heuristic confidence score into a ârough win rateâ and then printing expected R risks lending it empirical authority it has not earned. An independently chosen hypothetical probability would make the conditional nature clearer.
- `AVG_REWARD_R = 2.0` is a second declaration of the average target multiple. Changing the named target multipliers does not update it.
- The `degradation.trading_authorized` field means only ânot blocked by degradation,â not that the final action authorizes a trade. Its name invites consumers to treat it as an overall verdict.
- The simulatorâs second-resolution filenames can overwrite two simulated records written within one second. The primary decision log is separate, so this is not proof that the full engine analysis is lost.
- A volume-profile node does not establish that price âhas often reactedâ there or âhas tended to move throughâ it quickly. Those Exit Watch sentences should be framed as heuristics unless reaction behavior is actually measured.

---

## E. Comment-influence disclosure

For the seven specifically disclosed rules:

| Rule | Disclosure |
|---|---|
| Item 3 | Comments directed attention to particular corruptions. My partial verdict rests on the surviving VWMA and timestamp paths. I cannot exclude anchoring. |
| Item 6 | The extensive history emphasized logging. I independently traced writes, returned paths, retention, and archive replacement. I cannot know how much the framing affected prioritization. |
| Item 18 | The âkept Compliantâ statement was visible. My verdict rests on the public request path, absent credential configuration, and absence of submission codeânot that statement. |
| Item 16 | I did not accept âconsumedâ or âoutput-invariant deletionâ as proof of demonstrated value. The verdict is Not verifiable. |
| T3-3 | A prior Non-compliant label did not establish present process failure. The verdict is Not verifiable because acceptance-time evidence is missing. |
| T3-4 | The prior label and quoted criticism likely influenced where I looked. The partial verdict rests on the specific ineffective assertions documented above. |
| T4-2 | The prior Compliant label was visible. I evaluated the parameterized, mostly price-relative arithmetic; I did not infer empirical cross-asset performance from it. |

The additional Item 14 exposure also matters. I did **not** adopt the premise that any shared ADX input necessarily violates ârisk is not conviction.â I graded the actual risk constraints separately from the false independence claims.

---

## Requested runs â confirmation, not prerequisites for reporting the source defects

Run these in isolated temporary log/chart directories, preserve raw outputs, and report exact dependency versions.

1. **Volatility propagation**
   - Capture the actual arguments passed by `Phase7Engine.run()` to `calculate_stop_targets`.
   - Use a high-volatility case where structure does not dominate.
   - Distinguishing result: the call receives measured volatility and uses its multiplier, versus omitted/default `NORMAL`.

2. **Entry-scoring direction**
   - Produce bearish bias/trend/macro with a small positive reversal score that disables `short_signal`.
   - Record the direction supplied to `calculate_entry_quality`, its multipliers, and final action.
   - Compare with a direct SHORT calculation on the same frame.

3. **Trailing zero-volume window**
   - Valid history, earlier positive volumes, last 20 volumes zero.
   - Record final VWMA before and after filling, failure list, entry points, degradation, and action.
   - Distinguishing result: current VWMA is explicitly unavailable versus an older finite value presented as current.

4. **BTC-only failures**
   - Independently fail BTC ADX, SuperTrend, ATR, and structure.
   - Compare primary action/confidence, BTC availability/completeness, and rendered claims against the healthy control.

5. **Fallback equivalence**
   - Compare primary and forced-fallback EMA/RSI/ATR at frame lengths 20, 50, 75, 100, 300, and 450.
   - Include altered indicator lengths, monotonic prices, and an early large move.
   - Report final-bar differences and whether fallback use is recorded.

6. **Test effectiveness and isolation**
   - Run the named tests against always-neutral trend, always-WAIT decision, no-op plotter, and identical-error-return mutants.
   - Run filtered `run_tests.py` invocations from a fresh process with a sentinel live log directory.
   - Report which mutants pass and any live-directory changes.

**Bottom line:** Several claimed repairs are real. The remaining defects are concentrated at the boundaries between those repairs: a measured value not passed to its consumer, a score calculated for a different direction, and an absence repaired into a plausible number. The current suite does not reliably detect those seams.