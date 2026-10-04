# Independent Re-Audit, Round 8 — Parts 1–6

**Model identity: Claude (Anthropic).** I state this in accordance with Section 5. The disclosure that "Claude wrote the fixes you are grading, and wrote the tests that check them" applies directly to me. I have not previously seen this project in any session. I do not recognise this code from training data — the repository's stated first commit (24 August 2026) postdates my knowledge cutoff. Where I found myself relying on a comment rather than the code, I say so in Part 6.

**Package check (Section 5):** The Constitution file contains the 44-rule register across four tiers (21/7/10/6), the finding schema, severity rubric, Minimum Viable Audit definition, and Next Steps. The Version History ends at LICENSED with no audit outcomes. The content matches the description in Section 2. This document is Revision 9 per the revision history. All six first-message files are present. No outcome language found in the Constitution.

---

## Part 1 — Verdict table

### Tier 1 — Invariants

| # | Name | Verdict |
|---|------|---------|
| 1 | Tool, Not Autonomous Actor | Compliant |
| 2 | No Future Information / Look-Ahead Bias | Compliant |
| 3 | Data Integrity | Compliant |
| 4 | Determinism | Compliant |
| 5 | Reproducibility | **Partially compliant** |
| 6 | Traceability | Compliant |
| 7 | No Unsupported Predictive Claims | Compliant |
| 8 | Epistemic Honesty | Compliant |
| 9 | Every Measurement Has a Precise Definition | Compliant |
| 10 | Consistent Semantics | **Partially compliant** |
| 11 | No Circular Reasoning | **Partially compliant** |
| 12 | No Hidden Decision-Affecting State | Compliant |
| 13 | Fail Safely | Compliant |
| 14 | Risk Is Not Conviction | Compliant |
| 15 | Empirical Evidence Supersedes Theoretical Expectation | Compliant |
| 16 | Complexity Must Provide Demonstrated Value | **Partially compliant** |
| 17 | Backtesting Must Be Isolated From the Core Engine | Compliant (vacuously — no backtesting exists) |
| 18 | Read-Only Market Access | Compliant |
| 19 | Withdrawal Permissions Are Never Enabled | Compliant |
| 20 | Credentials Are Never Exposed | Compliant |
| 21 | Operator Credentials Stay With the Operator | Compliant |

### Tier 2 — Architecture

| # | Name | Verdict |
|---|------|---------|
| T2-1 | Separation of responsibilities | Compliant |
| T2-2 | Observation → interpretation → decision → risk/action | Compliant |
| T2-3 | Explicit interfaces/contracts | Compliant |
| T2-4 | Explicit configuration | **Partially compliant** |
| T2-5 | Modular design | Compliant |
| T2-6 | Controlled dependencies | Compliant |
| T2-7 | Explicit, evaluated changes to interfaces or behavior | Compliant |

### Tier 3 — Engineering Process

| # | Name | Verdict |
|---|------|---------|
| T3-1 | Hypothesis-driven development | **Not verifiable** |
| T3-2 | Controlled changes | Compliant |
| T3-3 | Automated tests | Compliant |
| T3-4 | Regression tests | Compliant |
| T3-5 | Fixed evaluation datasets | Compliant |
| T3-6 | Version control | Compliant |
| T3-7 | Known-good checkpoints | Compliant |
| T3-8 | Reproducible experiments | Compliant |
| T3-9 | Rollback capability | Compliant |
| T3-10 | Documentation of significant decisions | Compliant |

### Tier 4 — Preferences

| # | Name | Verdict |
|---|------|---------|
| T4-1 | Robustness over optimization | Compliant |
| T4-2 | Generalization over historical fit | Compliant |
| T4-3 | Explainability over unnecessary opacity | Compliant |
| T4-4 | Stability over flashy outputs | Compliant |
| T4-5 | Useful information over more information | Compliant |
| T4-6 | Prefer the simpler design (tie-breaker) | **Not verifiable** |

**Summary: 37 Compliant, 5 Partially compliant, 2 Not verifiable, 0 Non-compliant.**

---

## Part 2 — Findings

### Finding 1 — Item 11 (No Circular Reasoning) — Major

**Location:** `models/bias_engine.py`, the weighted blend and `components` output; `indicators/trend_health.py` (`compute_trend_health`); `structure/structure.py` (`_detect_regime`); `core/engine_core.py` (macro_bias derivation).

**What the code does:** Six factors are blended as independent weighted inputs to `bias_score`:

```
WEIGHT_TREND_HEALTH = 0.30        ← EMA slope magnitude, signed by slope direction
WEIGHT_STRUCTURE_REGIME = 0.20    ← mean(close[-5:]) vs mean(close[-15:]) gap
WEIGHT_VOLUME_SENTIMENT = 0.15    ← volume/price divergence
WEIGHT_SUPERTREND_DIRECTION = 0.15 ← ATR-banded price flip
WEIGHT_MACRO_BIAS = 0.10          ← close vs daily EMA_50
WEIGHT_REVERSAL_CONTINUATION = 0.10 ← RSI-momentum + slope acceleration
```

The `components` output records each factor's `"input"`, `"signed"`, `"weight"`, and `"contribution"` as though they were independent confirmations. Four of the six — trend health (0.30), structure regime (0.20), SuperTrend direction (0.15), and macro bias (0.10), totaling 0.75 of the blend — are different transformations of the same underlying measurement: the recent direction of close price. The code's own "INDEPENDENCE REVIEW, SECOND PASS" comment states this plainly and records the decision not to fix it.

**Which clause it breaks:** *"A signal must not be allowed to reinforce itself through multiple derived layers and then be presented as independent confirmation."*

**What goes wrong in practice:** On a sustained uptrend (450-bar AEROUSDT 4h with prices rising), all four price-direction factors agree by construction: EMA slopes are positive → trend_health contribution positive; 5-bar mean exceeds 15-bar mean → structure_regime is "BULLISH TREND" → structure_score +100; SuperTrend direction is +1 → supertrend_score +100; close exceeds daily EMA_50 → macro_score +100. The weighted blend sums these as four independent votes: 0.30×(up to 100) + 0.20×100 + 0.15×100 + 0.10×100 = up to 75 points from what is one directional observation counted four times. Add volume sentiment and reversal/continuation and `bias_score` reaches +100, the clip limit. The panel prints `CONFIDENCE (decision): 100.00/100` and `BIAS: BULLISH CONFIRMED`. The `lineage.bias_components` shows six "factors" with individual "contributions" that sum to the score. An operator reading this sees multi-factor consensus where there is a single measurement echoed through four formulas.

A secondary aspect of the same rule (check 7.4): `macro_bias` is weighted at 10% inside `bias_score` AND applied as a ±5% confluence multiplier on `entry_quality` (`macro_multiplier` in `models/entry_model.py`). The same measurement moves two scores that both feed the decision ladder: bias_score determines direction and minimum strength (MIN_ACTION_BIAS=30), entry_quality determines tier (AGGRESSIVE requires ≥ 70). On a borderline setup (bias_score=28, entry_score=68), a bullish macro on a bullish bias pushes bias_score to ~38 and entry_score to ~71.4, turning WAIT into AGGRESSIVE LONG on one piece of evidence counted twice.

**Severity: Major.** Violates a Tier 1 invariant. The resulting numbers are arithmetically correct from their inputs — the defect is the claimed independence of those inputs, not the computation. The effect reaches every decision the engine makes. I considered Critical under the Constitution's rubric ("violates a Tier 1 invariant in a way that could reach a live decision") but the instructions reserve Critical for "a wrong or fabricated number the operator would reasonably act on." The confidence number is not wrong or fabricated; it is misleadingly presented.

---

### Finding 2 — Item 5 (Reproducibility) / T2-4 (Explicit configuration) — Minor

**Location:** `models/bias_engine.py` (`calculate_dynamic_regime`, thresholds `0.04`, `0.02`, `0.01`); `indicators/trend_health.py` (momentum bands `40.0`, `55.0`, `70.0`, `80.0`; RSI strength bands `25.0`–`85.0`; trend regime boundaries `75.0`, `50.0`, `25.0`, `20.0`); `models/entry_model.py` (EMA zone multipliers `2.0`, `3.5`; ATR decay `0.5` and floor `5.0`; VWMA bands `0.01`, `0.025`, `0.05` and point tiers `15.0`, `10.0`, `5.0`; RSI bands `40.0`, `60.0`, `30.0`, `70.0`; structure bands `0.015`, `0.03` and point tiers `8.0`, `4.0`).

**What the code does:** Decision-affecting scoring and classification thresholds are bare literals inside comparison expressions. For example, in `calculate_dynamic_regime`:

```python
elif vol_ratio > 0.04:
    volatility_mode = "EXTREME VOLATILITY"
elif vol_ratio > 0.02:
    volatility_mode = "HIGH VOLATILITY"
elif vol_ratio > 0.01:
    volatility_mode = "MEDIUM VOLATILITY"
```

These three values determine the volatility mode, which feeds `calculate_stop_targets` (stop multiplier selection) and `classify_risk_regime` (risk tier). They are not named constants and therefore cannot appear in `FINGERPRINTED_MODULES`. The `test_fingerprint_names_every_constant` test scans only for UPPER_CASE named numeric constants and does not see bare literals. The `code_hash` (parse-tree hash) captures all of them, so two runs on different thresholds ARE distinguishable — but only through a hash comparison, not through the human-readable record.

**Which clause it breaks:** Item 5: *"Every analysis must be reconstructable later — its data timestamp, data source and version, engine version, configuration, and parameters must all be recoverable."* T2-4: *"Important behavior (RSI period, EMA windows, confidence caps) comes from named, visible configuration — not mystery constants buried in the logic that touches them."*

**What goes wrong in practice:** A run made with the VWMA distance band at 0.02 and a run made with 0.025 produce different `entry_quality` scores (different `vwma_pts` at a VWMA distance of 0.022). Both record identical `module_snapshot` values in the decision log. A reader comparing two decision records cannot tell which threshold each run used without cross-referencing `code_hash` against a source archive — and past the 90-day archive window, that source may no longer be available.

**Severity: Minor.** The `code_hash` does distinguish the runs (the analysis IS reconstructable), but the human-readable parameter record does not. T2-4 is design debt (the principle says "named, visible configuration"), and many important settings ARE in named configuration; these are the ones that are not.

---

### Finding 3 — Item 10 (Consistent Semantics) — Minor

**Location:** `core/engine_core.py` (`macro_agreement`, substring matching); `models/bias_engine.py` (Factor 5, exact matching); `models/decision_model.py` (`_determine_final_action`, `"ACTIVE" in entry_status.upper()`); `models/entry_model.py` (produces exact status strings).

**What the code does:** The direction of `macro_bias` is determined using substring matching in one module and exact matching in another:

```python
# engine_core.py — macro_agreement
macro_up = "BULLISH" in macro

# bias_engine.py — Factor 5
if macro_bias == "BULLISH":
    macro_score = 100.0
```

Similarly, `entry_status` is produced as one of seven exact strings ("ACTIVE ENTRY ZONE", "NEAR ZONE", etc.) but checked via substring matching in `decision_model`:

```python
entry_active = "ACTIVE" in entry_status.upper()
```

**Which clause it breaks:** *"The same term, score, or scale must mean the same thing in every module that uses it."*

**What goes wrong in practice:** If `macro_bias` were set to `"BULLISH CONFIRMED"` (which the current producer — `engine_core`'s three-way branch — cannot do), `macro_agreement` would score +10 to `validation_score` for agreeing with a bullish bias while `bias_engine` would score 0.0 for the macro factor (since `"BULLISH CONFIRMED" != "BULLISH"`). The two modules would disagree about the same input: one says the macro agrees, the other says it has no opinion. If `entry_status` were extended with `"REACTIVATED ZONE"`, `decision_model` would treat it as active (substring `"ACTIVE"` matches). The codebase has already had three direction-blind bugs of this exact class (the macro note of 3 September, the bias_engine sign-of-magnitude of 4 September, the volume_agreement of 5 September). This is the same pattern surviving in two comparison sites.

**Severity: Minor.** Cannot manifest with current input sets. But the inconsistency in matching strategy is the class of latent defect that produced three prior findings in this codebase.

---

### Finding 4 — Item 16 (Complexity Must Provide Demonstrated Value) / Item 2 (No Future Information) — Minor

**Location:** `indicators/indicators.py`, `clean_series`, the `method="interpolate"` branch.

**What the code does:**

```python
elif method == "interpolate":
    series = series.interpolate(method='linear', limit_direction='forward')
```

`pandas.Series.interpolate(method='linear')` fills interior NaN values by linear interpolation between the nearest valid values on BOTH sides — i.e., using future data. The `limit_direction='forward'` parameter affects only the handling of edge NaN values when a `limit` is set; without a `limit`, it has no effect on the interpolation method itself.

**Which clause it breaks:** Item 16: *"New indicators, models, calculations, or layers must exist because they solve a demonstrated problem or provide measurable value — not merely because they can be added."* Item 2: *"Information unavailable at the exact decision timestamp must never influence that decision, whether directly or through a derived signal."*

**What goes wrong in practice:** The `interpolate` method is dead code — no call site in the engine or the test suite uses `method="interpolate"`. But it is one edit from being live (changing `"forward_fill"` to `"interpolate"` at any call site). If that happened, interior gaps would be filled from future bars — a look-ahead leak. The `test_only_the_chart_may_fill_backwards` scan catches `bfill`, `limit_direction='both'`, and `method='bfill'` but not `interpolate(method='linear')`. The leak would be undetected by the suite.

**Severity: Minor.** Dead code with latent risk. The Item 2 invariant holds today (nothing calls it), but the guard has a gap. For Item 16, it is unconsumed complexity.

---

### Finding 5 — Item 11 (No Circular Reasoning), secondary — Minor

**Location:** `models/entry_model.py` (`calculate_entry_quality`, `macro_multiplier`), `models/bias_engine.py` (Factor 5, `macro_score`).

**What the code does:** `macro_bias` is weighted at 10% inside `bias_score` (as `macro_score`, one of six blended factors) AND applied as a ±5% confluence multiplier on `entry_quality` (as `macro_multiplier`, one of three multipliers). The same measurement moves two separate scores that both feed the decision ladder.

```python
# bias_engine.py — Factor 5
if macro_bias == "BULLISH":
    macro_score = 100.0
# ... blended at WEIGHT_MACRO_BIAS = 0.10

# entry_model.py — Confluence
if macro_bias == "BULLISH" and trade_direction == "LONG":
    macro_multiplier = CONFLUENCE_BOOST_MULT  # 1.05
```

**Which clause it breaks:** *"A signal must not be allowed to reinforce itself through multiple derived layers and then be presented as independent confirmation."* (Check 7.4: *"a factor already weighted inside a composite is then applied a second time on top of it."*)

**What goes wrong in practice:** A bullish macro on a bullish bias increases `bias_score` by up to +10 (one-sixth of the weight, pushing toward MIN_ACTION_BIAS=30) AND increases `entry_quality` by 5% (pushing toward AGGRESSIVE_ENTRY_SCORE_MIN=70). One piece of evidence opens two gates. The code's own record says "none of them adds the same number twice to one score" — true within each score — but the same measurement reaches the decision through two separate scores.

Note: the `trend_multiplier` and `structure_multiplier` use `trend_direction` (slope sign) and `structure_sequence` (swing analysis) respectively, which are related to but distinct from the `trend_health` and `structure_regime` factors in `bias_score`. Those are weaker instances of the same pattern. The `macro_multiplier` is the cleanest instance because it reuses the exact same input.

**Severity: Minor.** Impact bounded to ±5% on entry_quality. The code documents the multi-score reach of macro but treats it as a weighting question rather than a double-count.

---

## Part 3 — Not verifiable

**T3-1 (Hypothesis-driven development):** I can see evidence of focused, incremental commits in the version control history and extensive design rationale in code comments, but cannot determine whether every change followed the "problem → hypothesis → implementation → test → measurement → evaluation → accept/reject" sequence. I would need the commit messages and the development session records.

**T4-6 (Prefer the simpler design):** This is a tie-breaker applied when multiple designs satisfy every invariant equally. I cannot assess it without seeing the alternative designs that were considered. I would need design comparison records or alternative implementations.

---

## Part 4 — Test suite assessment

### Section 7.3 results

**Tests that can pass without proving what they claim:**

1. **`test_the_panel_never_prints_a_non_finite_number`** (in `tests/test_decision_bar_integrity.py`): Checks only that `math.isfinite` or `np.isfinite` appears somewhere in `panel_render`'s source. Would pass if one isfinite call existed anywhere in the file, even if every price field's `safe_float` were broken. This proves the source contains the string "isfinite", not that any particular guard works.

2. **`test_macro_and_volume_agreement_do_not_move_confidence_a_second_time`** (in `tests/test_no_circular_reasoning.py`): Calls `_compute_confidence` twice with IDENTICAL arguments (`bias={"score": 60.0, "raw": "BULLISH"}`) and asserts the results are equal. The test name claims to verify that macro and volume can't move confidence, but neither input is varied. This proves determinism of identical calls, not independence from macro/volume.

3. **`test_structure_regime_does_not_move_confidence_a_second_time`** (in `tests/test_no_circular_reasoning.py`): Defines a wrapper `confidence_with(structure_regime, raw_bias)` that accepts `structure_regime` but never passes it to `_compute_confidence`. The three calls with different `structure_regime` values inevitably return the same result because the parameter is discarded. This proves that a function that ignores its parameter returns the same value regardless of that parameter.

*(Note: the companion test `test_compute_confidence_signature_has_no_room_for_the_duplicated_inputs` does verify the function signature, which combined with these behavioral checks provides reasonable coverage. But the behavioral checks alone are vacuous for their stated claims.)*

4. **`test_the_snapshot_covers_every_top_level_field`** (in `tests/test_golden_path.py`): When no snapshot file exists, prints "SKIP: no baseline yet" and `return`s — the test PASSES rather than skipping or failing. Under `run_tests.py`, `pytest.skip()` becomes an error (to preserve the watched error count), so `return` is the established pattern. But it means the test silently passes when the baseline is missing, which is the state where it is most needed.

**Tests that inject a failure at a point the code path never reaches:** None found. The test suite is notably careful about this — `test_degraded_state.py`'s docstring explicitly records a first attempt that patched `classify_risk_regime` (which `calculate_stop_targets` never calls) and documents the correction.

**Tests asserting only absence:** `test_deleted_columns_stay_deleted` asserts columns are absent. Its companion `test_consumed_columns_are_still_produced` asserts the kept columns are present. Together they are robust against a feature vanishing entirely.

**Tests whose setup contradicts what they claim to test:** Items 2 and 3 above fall here — the setup does not vary the input the test claims to be checking.

**Tests that return instead of skipping:** Item 4 above.

**Tests whose fixture can no longer produce the condition:** `test_timeframe_disagreement.py` includes explicit precondition checks (`test_the_fixture_really_does_split_the_two_timeframes`) that fail loudly if the fixture no longer produces the target condition. `test_no_outlier_replacement.py` includes `_five_sigma_outliers` precondition assertions. The suite is generally disciplined about this.

**Other Section 7.3 observations:**
- The suite has strong negative controls throughout (many explicitly labeled "MUST PASS BOTH BEFORE AND AFTER THE FIX").
- The source-level guards parse ASTs rather than matching text, avoiding false positives from comments that quote removed code. This is well done.
- The mutation-resistance notes (labeled "ROUND 6 MUTANT ESCAPE") show the suite has been hardened against no-op mutants. The file-on-disk checks added to `test_frame_ownership.py` are good examples.

### Overall judgement

**The suite tests both that the engine is correct and that it has not changed.** The golden path test is a regression test (hasn't changed). The other ~74 files predominantly test specific behaviors, edge cases, failure modes, and invariants. The balance is approximately 70/30 in favor of correctness testing.

The suite is strong by conventional standards: it has negative controls, precondition checks, AST-level source guards, and end-to-end tests through the production path. The main structural weakness is that the fixes and the tests share an author (Claude), creating a risk that the tests confirm the fixes' shape rather than independently challenging the behavior. The handful of vacuous tests identified above is consistent with that risk — they look like they test independence properties but actually test determinism of identical calls.

The suite does NOT adequately guard against the `interpolate` look-ahead pattern (Finding 4). The `test_only_the_chart_may_fill_backwards` scan covers `bfill`-family patterns but not forward-looking interpolation.

---

## Part 5 — Release gate

The gate condition is: **no Critical Tier 1 finding stands unresolved.**

I have zero Critical findings. My most severe finding is Major (Item 11, correlated bias factors presented as independent). The instructions reserve Critical for "a defect that produces a wrong or fabricated number the operator would reasonably act on, or an assertion by the engine that something happened when it did not." The Item 11 finding produces a misleading number (overstated confidence due to correlated inputs) but not a wrong or fabricated one — the arithmetic is correct from its inputs.

**The gate condition is met, on my findings alone.**

I note for the record that the distinction between Major and Critical here rests on whether an overstated confidence score — arithmetically correct but derived from correlated inputs — constitutes "a wrong number." I chose Major because the number faithfully represents its inputs; the defect is in the claim of independence, not in the computation. A different reviewer might reasonably rate this Critical.

---

## Part 6 — Observations outside the Constitution

### A. The BTC-Adjusted Prediction feature (flagged open question)

The feature is declared "correctness-validated, empirically unvalidated." The code implements the arithmetic correctly (correlation-scaled, bounded adjustment) and the panel carries the required label: *"computationally validated, empirically unvalidated — no backtest supports this adjustment."* This satisfies Item 7's requirement that the status be stated honestly.

However, the number is presented to two decimal places (`BTC-ADJUSTED CONFIDENCE: 79.81/100`), which conveys a precision that implies empirical grounding. The honest label sits below it. The fundamental tension the Constitution names remains: a number formatted like a measurement is presented alongside its own disclaimer that it is not one. This is not a rule violation — the Constitution requires the disclosure, and the disclosure is present — but it is a design choice that works against the spirit of Item 8.

### B. Layer 5 / Entry Quality's Multipliers (flagged open question — Item 11 "Unknown")

The Constitution says this has "not actually been checked against the real code yet." I checked. The three inputs to the confluence multipliers are:

1. **`macro_bias`** — the SAME input as bias_engine's Factor 5 (weight 0.10). Directly reused.
2. **`trend_direction`** — from EMA slope sign in `trend_health.py`. Shares its raw input (EMA slopes) with `trend_health` (weight 0.30), which is computed from the same slopes plus ADX and RSI. Related through shared raw data.
3. **`structure_sequence`** — from swing analysis in `structure.py._detect_sequence`. Uses confirmed swing highs/lows. `structure_regime` (weight 0.20) uses `_detect_regime`, which reads mean(close[-5:]) vs mean(close[-15:]). These are genuinely different mechanisms reading the same price series.

**Answer to the open question:** The three inputs are NOT fully independent of the bias_score inputs. `macro_bias` is directly reused (Finding 5). `trend_direction` shares raw data with `trend_health`. `structure_sequence` uses a different mechanism and is the most independent of the three. The Item 11 "Unknown" status can now be resolved as: partly circular (macro directly, trend through shared raw data, structure approximately independent).

### C. Hysteresis in `_detect_regime` is per-call, not cross-run

`StructureEngine._detect_regime` implements "state persistence to reduce whipsaws" through `self._last_regime`. But `calculate_structure` creates a fresh `StructureEngine` per call, so `_last_regime` always starts at `"NEUTRAL STRUCTURE"`. The hysteresis only affects borderline cases within a single analysis (where the starting state determines whether a marginal gap resolves to BULLISH, BEARISH, or stays NEUTRAL). It does NOT smooth across candles as the name "hysteresis" traditionally implies. The code's claim of "preventing whipsaws during choppy consolidation phases by introducing state persistence" overstates what the mechanism does. This is not a rule violation — the state is explicit, documented, and deterministic — but the design description is inaccurate.

### D. The `test_the_snapshot_covers_every_top_level_field` required-key list is incomplete

The test checks for a specific set of required keys: `{"symbol", "timeframe", "macro_bias", "bias", "trend", "structure", "entry", "risk", "exit", "exit_watch", "btc_context", "explanation"}`. This list omits `"degradation"`, `"provenance"`, `"lineage"`, `"decision_log_path"`, and `"chart_path"` — all of which are in the decision contract and produced by the router. If a future re-baseline dropped one of these sections, this test would not catch it. The companion `test_the_decision_object_matches_the_contract` does validate the full contract against a live run, so the gap is partially covered.

### E. Claimed fixes I could not confirm

I verified the following claimed fixes against source and found them accurate:
- RSI/ATR fallbacks now use Wilder's RMA (ewm with alpha=1/length, adjust=False) ✓
- Entry zone fabrication removed (NaN when EMAs missing) ✓
- `volume_agreement` direction-aware ✓
- `risk_valid` default removed (uses `read_risk_verdict`) ✓
- Stop computed from ATR alone (no `structural_level` parameter) ✓
- `bias_label` is stateless ✓
- `trend_direction_sign` passed explicitly, validated to (-1, 0, 1) ✓
- Macro no longer overrides direction in `_determine_final_action` ✓

I could NOT confirm:
1. The exact numeric equivalence of the RSI/ATR fallbacks to `pandas_ta` at the decision bar (requires running both implementations on the same data). The code's measurement claims (e.g., "reads 69.140344 against pandas_ta's 69.140344") are consistent with the implementation but unverified.
2. The golden snapshot matching current output (requires running the engine).
3. The `code_hash` changing when specific constants change (requires executing `code_fingerprint`).

### F. Places where I noticed myself relying on a comment rather than the code

1. **`bias_engine.py`'s dependency graph comment** — I initially used it to understand which raw inputs feed each factor. When I then traced `structure_regime` to `_detect_regime`, I found the comment's earlier description ("swing-based regime label") was wrong and had been corrected in a later paragraph. I should have verified each factor's source independently before reading the summary. (The comment caught its own error, which is to its credit, but I relied on it first.)

2. **`decision_model.py`'s `_compute_confidence` docstring** — I relied on the claim that "structure_alignment and validation_adj were removed" and then verified against the function body. The claim was accurate, but I started from trust rather than verification.

3. **`risk_model.py`'s constants block comment** — I relied on the statement that ADX "now reaches bias_score through exactly one of its six factors" and verified against `trend_health.py`. Accurate, but again trust-first.

4. **`indicators.py`'s `clean_series` docstring** — I relied on it to identify the `interpolate` method as the third cleaning option and then verified it was uncalled. The docstring was accurate.

In each case the comment turned out to be accurate. But the pattern — reading the narrative before checking the code — is exactly the failure mode Section 4a warns about. For behavior-affecting checks (the actual fix verification in E above), I traced code, not comments.

### G. Observations outside the Constitution

1. **The EV sentence's "worth taking on average" phrasing.** The expected-value calculation treats confidence (bias magnitude) as a win-rate probability. The output labels this "illustrative, not backtested" and says "it is arithmetic on confidence alone, so it can never disagree with it." But the sentence concludes "positive -- worth taking on average if that win rate holds up," which is a conditional recommendation derived from a circular input. An operator skimming the panel might read "worth taking" and miss the conditionality. This is not a rule violation — the labeling is present and explicit — but the phrasing works against the labeling.

2. **The whitelist pattern in `signal_router._build_decision_object`.** Every field the router assembles is named explicitly. A field added to the engine's output but not named in the router's rebuild is silently dropped before reaching the panel or the log. The code documents this and the entry block's reconciliation fields were lost exactly this way on first attempt. The `test_decision_contract.py` tests catch drops at the contract level, but only for fields that are in the TypedDicts. A field added to engine_core without a corresponding contract update would be lost silently.

3. **`decision_log_backup.py` is tooling that lives in `utils/` alongside engine code.** It imports `core.config` and writes to disk. It is not called by the engine. This is the kind of non-engine code that makes `code_fingerprint`'s over-inclusive walk slightly noisy (every edit to it moves `code_hash`). The fingerprint module documents this trade-off explicitly and I agree with the choice, but it is worth noting.

---

**End of Parts 1–6.**