# Round 8 Fix Verification

## A. The stop

**1. Does the fix hold?**

**Holds.**

The stop multiplier is computed in `models/risk_model.py`, `calculate_stop_targets` (line 400):

```python
stop_mult = ATR_STOP_MULT * vol_multiplier
```

`vol_multiplier` is set from `volatility_state` alone (lines 394–398):
```python
vol_multiplier = 1.0
if volatility_state == "HIGH VOLATILITY":
    vol_multiplier = VOL_MULT_HIGH
elif volatility_state == "LOW VOLATILITY":
    vol_multiplier = VOL_MULT_LOW
elif volatility_state == "EXTREME VOLATILITY":
    vol_multiplier = VOL_MULT_EXTREME
```

`TREND_FACTOR_DIVISOR` and `BIAS_FACTOR_DIVISOR` are gone from the module. `trend_health` is no longer a parameter (keyword-only signature; passing it raises `TypeError`). `bias_score` is used only for the side (`plan_direction = "LONG" if bias_score >= 0 else "SHORT"`, line ~430); its size does not reach the multiplier.

`classify_risk_regime` takes only `volatility_state` and `stop_distance_pct` (line 498). `validate_risk_parameters` takes `current_price`, `atr_stop`, `volatility_state` (all required, no `**kwargs`). The call site in `core/engine_core.py` (line ~1255) passes no `trend_health` and no `adx`.

The lineage comment (`core/engine_core.py`, `risk_inputs` block) and the decision contract's docstring (`core/decision_contract.py`, `LineageBlock`) both state the four inputs: price, atr, volatility_state, and the sign of bias_score. That is what the code reads.

I searched every computation, recording, printing and checking of the stop, its distance or its multiplier. Nothing depends on bias score magnitude, conviction or trend health.

**2. Does any change since my package add a Critical?**

**No.** I checked every change in `engine.diff` for a Tier 1 violation that could reach a live decision under the Constitution's rubric ("how a finding gets recorded"). The changes are: fix 2 (a stricter ADX gate), B6 (record routing), N5 (removal of BTC-adjusted confidence), the fallback sweep (UNKNOWN labels replacing fabricated readings), B4's labels (wording), B7 (regime recorded on refusals), B9 (BTC SuperTrend read directly), B10 (order key rename and note filtering). Each either removes a fabrication, tightens a gate, or corrects a label. None introduces a Tier 1 violation.

---

## B. Your findings

### F1 — Lineage comment and contract docstring corrected

**Fixed.** `core/engine_core.py` (risk_inputs block, lines ~1592–1625): the comment now reads *"Since fix 1 the paragraph is true: the stop and the targets read current_price, atr, volatility_state and the sign of bias_score, all four recorded here."* `core/decision_contract.py` (`LineageBlock` docstring, lines 345–351): *"Since fix 1 the stop is ATR x 1.2 x the volatility factor, on the side the sign of bias_score picks."* Both are accurate against the code.

### F2 — classify_risk_regime reads only volatility and stop distance

**Fixed.** `models/risk_model.py`, `classify_risk_regime` (lines 498–547): signature is `(self, volatility_state: str, stop_distance_pct: float) -> str`. `REGIME_CHOP_ADX` and `REGIME_STRONG_ADX` are gone. The function reads only the volatility state and the stop distance against `REGIME_EXTREME_STOP_PCT`. No ADX, no trend health, no conviction input.

### F3 — A frame with no readable time axis is rejected

**Fixed.** `data/validation.py` (line 352): `if not isinstance(df.index, pd.DatetimeIndex) and "timestamp" not in df.columns:` returns a rejection string naming all six temporal classes. A `timestamp` column that cannot be parsed returns `"unreadable time axis"`. NaT timestamps are named. The pinned loader (`data/data_fetcher.py`, `_load_pinned`) calls `load_csv`, which calls `validate_ohlcv`; the validation error is surfaced as `{"error": ...}`. Confirmed by `tests/test_untimed_frame_is_rejected.py`.

### F5 — "BAND DISTANCE" reads "from the band's midpoint"

**Fixed.** `core/panel_render.py` (line 644): `f"BAND DISTANCE : {distance:.2f}% from the band's midpoint\n"`. The quantity is `distance_from_zone`, computed as `abs(close - zone_mid) / close * 100` in `models/entry_model.py` — distance from the midpoint. The label now matches the definition. Confirmed by `tests/test_band_distance_is_from_the_midpoint.py`.

### F6 — clean_series refuses `interpolate`

**Fixed.** `indicators/indicators.py`, `clean_series` (lines 104–124): `accepted = ("forward_fill", "fill_value")`; any other name raises `ValueError` listing the accepted methods. `'interpolate'` and `'drop'` are gone. `'fill_value'` without a `fallback_value` also raises. Confirmed by `tests/test_clean_series_methods.py`, which checks every accepted method against later rows and proves the check catches linear interpolation.

### F8 — One VWMA name; MOMENTUM line gone

**Fixed.** `structure/structure.py`, `_volume_sentiment_simple`: the locals are `vw_mean_recent`, `vw_mean_prev`, `vw_mean_slope` — no "vwma" in the names. The docstring says *"It is not the engine's VWMA."* `core/panel_render.py` (lines 929–935): the MOMENTUM line is removed; the TREND line carries both `trend_direction` and `momentum_mode`. Confirmed by `tests/test_one_name_one_meaning.py`.

### F9 — Four claims, each separately

**All four fixed.**

1. **StructureEngine state:** `__init__` no longer sets `_last_regime`. `_detect_regime` is a plain function of the frame. A frame under 15 rows returns `"UNKNOWN STRUCTURE"`. The comment says *"It persisted nothing."* Confirmed by `tests/test_round8_f9_claims_match_the_code.py`.

2. **trend_health failure labels:** `default_response` (lines 30–55) has `"momentum_mode": "UNAVAILABLE"`, `"trend_regime": "UNAVAILABLE"`, `"trend_direction": "UNAVAILABLE"`. No measurement path emits "NEUTRAL" for momentum_mode or trend_regime. Confirmed by the same test file.

3. **volume_agreement on UNKNOWN VOLUME:** `core/engine_core.py` (line ~110): `if "UNKNOWN" in v: return 0.0, f"Volume sentiment could not be read ({volume_sentiment}), so volume neither supports nor opposes this bias."` — no longer "neutral." Confirmed by the same test file.

4. **ADX consequence text:** `indicators/indicators.py` (line ~575): `"trend health loses its ADX component (up to 40 of its 100 points), and the confirmation gate refuses both sides, since no trade is taken without an ADX reading."` The "25" is gone. Confirmed by the same test file, which checks the ceiling against `compute_trend_health`'s own output.

### Part 4's three test shapes

**All three fixed.**

1. **Golden coverage test returning instead of skipping:** `tests/test_golden_path.py`, `test_the_snapshot_covers_every_top_level_field` (line ~382): now `assert os.path.exists(SNAPSHOT)` with a failure message. The `print("SKIP: no baseline yet"); return` is gone. The `pandas_ta` skip is also removed (the test reads the stored file). Confirmed by reading the code.

2. **Source-text test beside it:** `tests/test_decision_bar_integrity.py`, `test_the_supertrend_level_is_guarded_and_not_only_its_direction` (line ~309): now replaces `ta.supertrend` with one whose level has no value at the decision bar while its direction keeps one, runs `add_technical_indicators`, and asserts a SuperTrend failure is recorded and neither column is written. Two controls: the pinned frame with nothing replaced computes a level; the replaced call's direction has a value. `test_the_panel_never_prints_a_non_finite_number` (line ~572): now renders the golden decision with each float field set to +inf, -inf and NaN, and asserts no line prints nan/inf/infinity, with a precondition that the plan prints.

3. **Watched error count 29 vs 32:** `run_tests.py` docstring no longer says 29. `tests/test_code_fingerprint.py`, `tests/test_docs_build_writes_into_the_repository.py`, and `tests/test_summary_names_the_action_reason.py` all point to `docs/PHASE7_NEXT.md` instead of naming a number. Confirmed by reading the diffs.

---

## C. Other changes

### Fix 2 — no trade under ADX 20 (`1b25f36`)

**No new defect found.** `MIN_TREND_ADX = 20.0` is fingerprinted. `_measured_adx` rejects bools, non-numbers, non-finite values, and values outside 0–100. `signal_blockers` blocks both sides when ADX is unmeasured or under 20. `_adx_text` rounds down so 19.96 prints as "19.9". The old positional call shape raises `TypeError` (keyword-only `adx`). `engine_core` passes `adx=trend["adx"]`. All confirmed by `tests/test_no_trend_no_trade.py`.

**Ruling claim checked:** "ADX under 20 blocks both sides, and the reason is printed." — Supported. The blocker string is appended and surfaced through `_apply_signal_gate`'s reason.

### B6 — runs on pinned data keep records of their own (`9e507b1`)

**No new defect found.** `is_live_record` requires `fetch.pinned is False` and `source != "pinned"` — both must say live. Missing or contradictory provenance routes to `pinned/`. `records_dir` builds the path with forward slashes, platform-independent. `engine_core._is_live_run()` decides once per run. State, archive and log all follow. Confirmed by `tests/test_pinned_runs_keep_their_own_records.py`, including the "broken pinned request is not a live run" case and the "each source prunes only its own archives" case.

**Ruling claim checked:** "chosen by the code from the run's source rather than by a setting someone has to remember" — Supported.

### N5 — Bitcoin reference only (`6469a67`)

**No new defect found.** `_compute_btc_adjusted`, `BTC_ADJUSTMENT_CAP`, `BTC_STRESS_PENALTY` are gone. `evaluate()` no longer takes `btc_context` or `symbol`. `engine_core` no longer writes BTC's `score` into the BTC block. The panel's BTC section prints what engine_core measured. Confirmed by `tests/test_btc_is_reference_only.py`, which feeds stale keys and checks none are read.

**Ruling claim checked:** "Bitcoin is reference only" — Supported.

### The fallback sweep (`797bdc9`) and the two repeated readings (`69c92d6`)

**No new defect found.** Every panel default is now UNKNOWN (or the router's own value). Every router default for a value computed with is read directly (subscript). The two repeated readings: the REGIME line is gone, and the STRUCTURE line no longer carries a `| Vol:` field. `tests/test_an_absent_value_is_not_a_reading.py` holds an inventory of every default with its reason, with a negative control. `tests/test_each_reading_is_printed_once.py` holds the deduplication.

**Ruling claims checked:**
- "a value that is only printed or recorded falls back to the router's own value for an absent one" — Supported.
- "a value the engine computes with is read directly" — Supported.
- "the REGIME line goes... and the Vol field goes from the STRUCTURE line" — Supported.

### B4's labels (`22a9a35`)

**No new defect found.** `FADING VOLUME` replaces `VOLUME DIVERGENCE` in `structure.py`, `bias_engine._VOLUME_SENTIMENT_SCORES`, and `engine_core.volume_agreement` (exact match). The momentum divergence sentences say "close and RSI against the close and RSI four candles back." The Exit Watch flag names both comparisons and which way. All scores unchanged. Confirmed by `tests/test_b4_labels_say_what_is_measured.py`, which runs the detector through every label and checks the vocabulary.

**Ruling claim checked:** "the two warning labels are matched whole, each with a note saying what it measured" — Supported. `"FADING VOLUME"` and `"VOLUME EXHAUSTION"` are exact matches.

### B7 (`d77a8c4`)

**No new defect found.** The regime is classified before the 15% and 0.2% limits. Both return the computed regime. Messages unchanged. `UNKNOWN` only where no regime can be computed. Confirmed by `tests/test_b7_distance_limits_record_the_regime.py`, which checks every branch and proves the verdict and reason are unchanged against an inline pre-B7 copy.

**Ruling claim checked:** "the 15% limit refuses nothing on its own... It chooses only the message" — Supported. Any stop over 15% is over `REGIME_EXTREME_STOP_PCT` (8%), so `classify_risk_regime` returns EXTREME RISK and the EXTREME RISK check would refuse it anyway.

### B9 (`64ad625`)

**No new defect found.** BTC's `ST_Direction` is read by subscript (line ~937: `btc_supertrend_direction = float(df_btc_struct["ST_Direction"].iloc[-1])`). A missing column raises inside the BTC block's `except`, which sets `btc_context = {"available": False}`. The asset's own read keeps its 0.0. Confirmed by `tests/test_b9_btc_supertrend_is_read_directly.py`.

**Ruling claim checked:** "Bitcoin's SuperTrend direction is read directly" — Supported.

### B10 (`9ea1cf3`)

**No new defect found.** The order key is `"ema_band"` (was `"entry_zone"`). `current_price` stays as the entry. The panel withholds the Target 1 note unless `any(side in action_val for side in ("LONG", "SHORT"))`. Confirmed by `tests/test_b10_outputs_agree_with_finding_4_and_the_action.py`, which checks every action the decision model writes.

**Ruling claim checked:** "the panel prints the Exit Watch note naming Target 1 only on a run whose action names a side" — Supported.

---

## D. Declared not fixed

None of the six was made worse by any change since my package.

- **F4** (`macro_multiplier`): unchanged at `models/entry_model.py` lines 387–389.
- **F7** (spike window): unchanged at `indicators/indicators.py` line 808.
- **F10** (the gate): unchanged at `models/decision_model.py` line 678.
- **Part 4's other named tests** (absence scans of shape 1, and shape 4): not touched.
- **§1(3)** (default responses' `0.0`): unchanged at `models/entry_model.py` line 120 and `indicators/trend_health.py` line 22.
- **§1(5)** (failed run leaves no log record): not changed; the router's error paths still return before `decision_log.write`.

---

## E. Anything else

1. **A claim in the B4 ruling that the code supports but that a reader might misread.** The ruling says "the two warning labels are matched whole, each with a note of its own." The code matches `"FADING VOLUME"` and `"VOLUME EXHAUSTION"` exactly. But `bias_engine._VOLUME_SENTIMENT_SCORES` scores both at 0.0 (neutral), while `volume_agreement` penalises both at −25. The ruling correctly says "each costs validation_score 25 points instead" — but a reader might think the bias score also drops. It does not. This is accurate as written but worth noting.

2. **The `_measured_adx` boundary.** A value of exactly 0.0 is accepted as a valid reading (and blocks, being under 20). A value of exactly 100.0 is accepted and passes. Both are correct per the docstring ("ADX is bounded to 0-100 by its definition"). No defect.

3. **The ADX gate is stricter than the old exhaustion flag in one respect.** The old flag fired only when `range_expanding and weak_adx` (or `trend_health < 35 and adx < 15`). The new gate fires on any setup with ADX under 20, regardless of candle width. This is the ruling's intent ("ADX under 20 blocks both sides"), so it is not a defect, but it means the fix changes trade availability more than the old flag did — which the ruling acknowledges ("About 37% of real 4h bars are blocked outright, where the flag blocked about half of them: fewer setups reach a trade").

---

## F. About this reading

1. **Which model are you?** I do not know my exact checkpoint. I am a large language model. The project's record names both of my round-8 runs as "Claude" while the provider's record named Xiaomi's endpoint. I cannot resolve this from inside a conversation.

2. **Recognition.** I did not recognise any code from training rather than from reading. The public-repository disclosure applies and cannot be checked from my side.

3. **What I read closely, and what I did not.** I read in full: `models/risk_model.py`, `models/entry_model.py`, `models/decision_model.py`, `models/signal_router.py`, `models/bias_engine.py`, `models/btc_context.py`, `models/exit_model.py`, `core/engine_core.py`, `core/decision_log.py`, `core/decision_contract.py`, `core/panel_render.py`, `data/validation.py`, `data/data_fetcher.py`, `indicators/indicators.py`, `indicators/trend_health.py`, `structure/structure.py`, `live_trading.py`, `run_tests.py`, and every test file in the package. I read `engine.diff` and `tests_changed.diff` in full. I searched the rulings excerpt and the Constitution for the specific claims named in each section. I read `core/code_fingerprint.py`, `core/lineage.py`, `core/config.py`, `indicators/volume_profile.py`, `utils/plotting.py`, `main.py`, and `utils/decision_log_backup.py` closely enough to check the specific questions asked. I did not re-run the test suite or execute any code.