# Run A — Kimi K3, Minimum Viable Audit gate findings

OpenRouter, 2026-08-27. Max Tokens 64,000, reasoning effort Max.
Auditor's verbatim output. Recovered from the session transcript.

---

## Finding 1 — Item 2 (No Future Information / Look-Ahead Bias)
- **Principle:** Tier 1, Item 2 — No Future Information / Look-Ahead Bias
- **Status:** Compliant (live path), with a standing caveat that must survive into Step 9
- **Severity:** Minor (the caveat below; the invariant itself holds for the live pipeline)
- **Effort:** Small to eliminate the latent pattern
- **Evidence:** Independently verified by reading the full source, not the audit package's claims:
  - All decision inputs are taken from the last completed bar only: `df_struct["EMA_20"].iloc[-1]`, `df["ST_Direction"].iloc[-1]`, `df["ATR"].iloc[-1]` (core/engine_core.py); `.iat[-1]`, `.iat[-4]`, `.iat[-5]` (indicators/trend_health.py); `.tail(window)` (models/btc_context.py).
  - Structure pivot detection is causality-safe by construction: `structure/structure.py::_find_confirmed_swings` requires `i - lookback >= 0` and `i + lookback <= n-1` before accepting a pivot, and its own comment states confirmation waits "until `lookback` bars of price action have passed after it." For a run at time "now," those confirmation bars are in the past. BOS/CHOCH are then compared against the last close. This is correct.
  - Indicator computation is via pandas_ta rolling/ewm operations (causal).
  - **Caveat:** the codebase makes pervasive use of backward fill — `clean_series()` forward-fill branch does `.ffill().bfill()` (indicators/indicators.py); input cleaning `.ffill().bfill()` (indicators.py, indicators/volume_profile.py); the structure wrapper `df_clean[required_cols].ffill().bfill().fillna(0.0)` (structure/structure.py); plotting `.fillna(method='ffill').fillna(method='bfill')` (utils/plotting.py). `bfill` routes later values into earlier rows. It cannot affect the decision because the decision reads row `-1`, and row `-1` has no later row to fill from. If this same code is ever evaluated at historical decision points (i.e., any backtest), the pattern becomes a genuine look-ahead leak. The engine is compliant *only because* its decision timestamp is always the last bar.
- **Impact if this stands:** None for live output. If unaddressed, the backtesting architecture (Step 9) inherits a latent mechanism for future-information leakage at historical decision points — the exact failure class Item 2's rationale names as most dangerous.
- **Required action:** None for this gate. Before backtesting work begins (Step 9), remove or quarantine `bfill` in all analysis paths, or restrict it to documented, decision-non-reachable uses.
- **Verification:** grep each analysis module for `bfill` / `fillna(method=...)` / `interpolate`; at backtest build time, run a point-in-time harness that re-computes each historical decision using a truncated dataframe and asserts no NaN-filled warm-up leak.
- **Re-audit:** Yes — mandatory when the backtesting architecture is built, per the Constitution's own guidance that Item 2 gets the most explicit checking at that step.
- **Correlation disclosure:** This "Compliant" is a static-review judgment over the same source Claude wrote, and my reading pattern (look for centered windows, `.iloc[-1]` usage) is a standard one that Claude would also apply — that is a shared-methodology blind spot, not independence. It is partially mitigated because every module's indexing was walked individually, but an execution-level point-in-time test (not possible from these artefacts alone) would be stronger evidence than my reading.
---
## Finding 2 — Item 3 (Data Integrity)
- **Principle:** Tier 1, Item 3 — Data Integrity
- **Status:** Non-compliant
- **Severity:** Critical (unvalidated and fabricated inputs flow into live decisions every run)
- **Effort:** Medium (one central validation module plus call-site wiring)
- **Evidence:**
  - `data/data_fetcher.py::fetch_ohlc` validates only that the response is a non-empty list. There are **no checks for missing candles (gaps), duplicated candles, impossible prices, timestamp ordering/consistency, stale data, or abnormal volume** — explicit sub-items named in the invariant text. The only applicable checks are empty-response and `engine_core._validate_dataframe`'s empty / len<20 / required-columns check (the log's `[ERROR] Insufficient data` entries show only this weak check firing on the 1h/1w scans).
  - `indicators/indicators.py::add_technical_indicators` and `structure/structure.py::calculate_structure` **silently fabricate** input values via `ffill().bfill().fillna(0)` instead of detecting defects — the invariant demands detection *before* analysis, not synthesis during it.
  - `indicators/volume_profile.py::compute_volume_profile` does contain genuine per-candle checks (non-finite, `high < low`, negative volume → skip and count; the log's "processed 450 candles, skipped 0" shows the counter running) — but in `engine_core.run()`, structure/volume profile executes *after* indicators have already consumed the raw frame, so the one real detection point sits downstream of analysis.
  - One inference, marked as such: exchange kline endpoints typically return the currently-forming candle as the last element. `fetch_ohlc` does not check last-candle completeness; the engine decides on a possibly incomplete 4h candle. I cannot verify MEXC's exact behavior from these artefacts, so this sub-point is flagged as unverified rather than established.
  - Macro pipeline: on validation failure, `macro_bias` is set to `"NEUTRAL"` and the pipeline continues (core/engine_core.py, "1b. FETCH MACRO DATA" block; corroborated by the log line `2026-08-24 02:36:18 WARNING Failed to process macro timeframe data:`). A data defect becomes a *neutral input to analysis* — precisely the quiet conversion the invariant forbids.
- **Impact if this stands:** Garbage data becomes good-looking output without announcement. Fabricated close prices flow into EMA/RSI/ATR, then into bias, entry quality, risk validation, and the final decision; a fetch outage in the macro timeframe is silently reinterpreted as "NEUTRAL." The engine cannot currently distinguish "no defect found" from "defect fabricated away."
- **Required action:** Add a validation gate in `DataFetcher.get_tf` (or a dedicated validator called first in `engine_core.run`) covering: gap detection, duplicate timestamps, timestamp ordering, impossible prices (negative, `high < low`), staleness (last candle age vs. timeframe), volume sanity (negative/zero-spike), and last-candle completeness (drop or flag the forming candle). Fabrication paths in indicators/structure must be replaced by explicit reject-or-flag semantics. Macro-timeframe failure should halt or mark `macro_bias` as "UNAVAILABLE," never "NEUTRAL."
- **Verification:** Fixture tests with deliberately corrupted pulls (duplicated rows, a gap, a `high<low` row, a stale last timestamp, negative volume) must be rejected before indicator computation; a clean pull must pass. Re-run the engine against a synthetic corrupted CSV via `DataFetcher.load_csv`.
- **Re-audit:** Yes — re-check after the validation module lands, before Step 5 prioritization is considered closed.
---
## Finding 3 — Item 6 (Traceability)
- **Principle:** Tier 1, Item 6 — Traceability
- **Status:** Non-compliant
- **Severity:** Major — borderline Critical, because one element is an *actively false* claim rendered to the operator every run
- **Effort:** Small-to-Medium
- **Evidence:**
  - `core/panel_render.py` closes every successful panel with `Trade logged to Logs/phase7_trade_log_{symbol.lower()}.csv`. **No file in the 19-file source writes that CSV.** The only writes present anywhere are: `Logs/phase7_engine.log` (main.py logging handler), chart PNGs (utils/plotting.py), LiveSim JSON (live_trading.py), and the two-field state JSON `{"supertrend_direction","detailed_bias"}` (engine_core._save_state — confirmed by the evidence file's exact content). The rendered claim of a persisted trade record is fiction.
  - Partial mitigation present in code: `models/decision_model.py` builds `explanation.reasons` and entry-quality sub-points (`ema_pos_pts`, `atr_dist_pts`, `vwma_pts`, `rsi_pts`, `struct_pts`), and `models/signal_router.py` retains section dicts — so an in-memory chain `decision ← components ← signals` exists during the run.
  - Missing links in the chain: the unified decision object carries **no raw-data fingerprint** — no last-candle timestamp, no row count, no source identifier; only `symbol`/`timeframe`. `engine_version` exists in core/config.py but is never embedded in any output. Once the process exits, the walk `panel → components → indicators → validated data → raw source` cannot be reconstructed from anything the engine persists.
- **Impact if this stands:** "Why did the engine produce this decision?" is answerable only while the process is alive. Worse, every panel asserts a log artifact that does not exist — a false auditability signal delivered to the operator, which undermines trust in every other rendered line (and is the exact failure the gate items exist to catch).
- **Required action:** Either implement the claimed trade log (structured append of the full decision object, plus data fingerprint: last candle timestamp, candle count, source endpoint, engine version, config snapshot) or remove/replace the claim in panel_render.py. The raw-data reference must be embedded in the decision object at build time in `engine_core.run`.
- **Verification:** After a run, the CSV/decision-log file exists on disk, contains the full section dicts plus the fingerprint fields above, and a third party can reconstruct decision → components → indicator values → (last-candle timestamp, row count) without touching process memory.
- **Re-audit:** Yes — re-check once persistence lands.
---
## Finding 4 — Item 18 (Read-Only Market Access)
- **Principle:** Tier 1, Item 18 — Read-Only Market Access
- **Status:** Compliant (code-level), with one explicitly bounded Unknown on deployment environment
- **Severity:** N/A / none
- **Effort:** Small for the optional hardening below
- **Evidence (verified directly against the provided source — the audit package's search claims were re-tested, not trusted):**
  - credentials: `core/config.py` contains `API_KEY = ""` and `API_SECRET = ""` with the comment "not required for public OHLC endpoints" — the package's listed matches are confirmed; no other credential-bearing field exists in any of the 19 files.
  - execution surface: across all 19 files there is no `place_order` / `create_order` / `createOrder` / `.buy(` / `.sell(` / `execute_trade` / `submit_order` / `new_order`, and no HTTP verb other than GET. The sole network call is `requests.get(f"{base}/api/v3/klines")` (data/data_fetcher.py), a public endpoint; the engine therefore never presents a credential at all, so it cannot present one carrying trade-execution permissions.
  - `requirements.txt` lists `ccxt` (an execution-capable library), but no file imports it; imports across the package are pandas/numpy/matplotlib/requests/pandas_ta + stdlib (+optional colorama).
  - Item 18's own rationale is satisfied a fortiori: with zero credential material, the guarantee does not even need to move into the exchange's permission model — there is no permission to misuse.
- **Impact if this stands:** None at code level. Residual risk is environmental only.
- **Required action:** None for compliance. Optional hardening: state the zero-credential design explicitly in the README, and add a CI-style grep guard so a future contributor adding ccxt import or a credential field fails the build.
- **Verification:** Re-run the pattern scan on future revisions; confirm imports remain GET-only and credential-free. Note the boundary: I cannot verify from these artefacts that no real key exists on Viktor's machine (environment variables, local ignore files) — that deployment aspect is Unknown and remains so for whoever operates the engine; it is not part of code compliance here.
- **Re-audit:** Lightweight re-scan at each future audit pass; treat as Critical-level recheck if multi-user/operator features or any credential-handling code is ever introduced (interacts with Items 19–21 in the later sweep).
- **Correlation disclosure:** My verification method (fixed pattern list + import scan) duplicates the audit package's own stated methodology, so it is not an independent technique — the supplement I added (walking every import and confirming the only network call is a GET to a public endpoint with no auth headers anywhere) still comes from reading the same source Claude wrote. A genuinely independent confirmation would be a runtime check (e.g., intercepting outbound requests in a sandbox); that execution-level check was not available from the artefacts.
---
## Finding 5 — DEFECT row resolution (Minimum Viable Audit gate composition)
- **Principle:** Constitution, Version History "DEFECT" row (Aug 27) — internal contradiction between the Next Steps definition of the gate (Items 2, 3, 6, 18) and the conflict-of-interest safeguards passage ("gate items (Items 2, 3 and 6)")
- **Status:** Resolved — the Next Steps four-item definition stands; the safeguards enumeration is defective shorthand
- **Severity:** Moderate (a documented process gap, not itself an engine invariant violation) — but the affected invariant is the most consequential one in the gate, hence not Minor
- **Effort:** Small (a wording correction, deferrable until the freeze lifts since interpretation is now settled)
- **Evidence:** Next Steps "New — the audit's starting gate (Minimum Viable Audit)" enumerates Items 2, 3, 6, 18 and gives Item 18's reason for inclusion ("if the running process holds a credential with trade permissions, then Item 1 is aspirational no matter what the code currently does"). The later "New — audit independence safeguards" bullet says "the Minimum Viable Audit gate items (Items 2, 3, 6)." The DEFECT row's own pending instruction: "Pending that finding, the stricter reading governs: Item 18 is a gate item and does receive the independent second check. The audit must record a formal finding resolving which passage stands."
- **Impact if this stood unresolved:** Item 18 — the one invariant that converts Item 1 from behavioral promise to structural property — would be the only gate item exempt from the second-check-by-non-author safeguard.
- **Required action (resolution):** Adopt the Next Steps enumeration as the controlling definition (it is the passage that defines the gate and contains the joined reasoning for Item 18); read "(Items 2, 3 and 6)" as errant shorthand inherited from the pre-Item-18 revision and without effect. Consequence: all four gate items, including Item 18, require the independent second check. No rule text need change under the freeze; the wording fix is a documented amendment candidate for after the freeze lifts, per Version History's own amendment note.
- **Verification:** Any future audit procedure/test run's checklist includes Items 2, 3, 6, and 18 for the second check; this present run already subjects Item 18 to the same audit as the other three, consistent with the resolution.
- **Re-audit:** No — one-time interpretive resolution; note for the post-freeze wording cleanup.
---
## Section 5 open questions — tested, not confirmed (per instructions)
**5.1 — "BTC-Adjusted AERO Prediction" (Prediction V1).**
- Additivity claim: **verified at code level.** In `models/decision_model.py::evaluate`, `final_action` is computed from bias/trend/entry/risk/macro only; `confidence` and `ev` likewise use only the unadjusted inputs. `_compute_btc_adjusted` returns a separate dict, merged only into `btc_context` by `models/signal_router.py::_merge_btc_context`, and rendered in its own section labeled "informational only — does not change BIAS or DECISION" in `core/panel_render.py`. The AERO-only decision path is not touched.
- Empirical status: **Unknown and honestly labeled.** No backtesting output exists in the artefacts (the package itself says the backtesting folder was removed), so the public "computationally validated, empirically unvalidated" framing is the epistemically correct one. This remains an Item 7/8 matter for the full sweep, not graded here.
**5.2 — Roadmap Layers 2 and 5.**
- Layer 2 (multi-factor bias weighting): **implemented** — `models/bias_engine.py` computes a six-factor weighted blend with named weights summing to 1.00.
- Layer 5 (entry multipliers): **implemented** — `models/entry_model.py::calculate_entry_quality`, section 6, applies macro/trend-direction/structure-sequence multipliers, explicitly commented "Roadmap Layer 5." The audit package's hedge ("Layer 5 does not appear anywhere in this package's 19 files under that name") is **false**; I verified this directly against entry_model.py's docstring.
- Residual issue: `models/decision_model.py`'s docstring still describes Layers 2 and 5 as future work ("will feed richer inputs into this later"). Stale documentation — minor; flagged for the later sweep, no gate-level consequence.
**Independence check on the open questions:** the Constitution warns that an audit confirming exactly the two flagged questions and nothing else is a warning sign. This run did not do that: it produced two Non-compliant gate findings (Items 3 and 6), one latent-risk caveat (Item 2), one verified-search falsehood in the package (Layer 5 "not appearing under that name"), and resolved the DEFECT row — in addition to testing both open questions.
---
## Unverifiable package claims (recorded, per disclosure instruction)
- The package's file sizes, staging timestamps, the public GitHub repository's existence/contents, and the provenance of the evidence bundle **cannot be verified from the artefacts provided** and were not relied upon. All findings rest on the source text, logs, state file, and simulated trade record provided inline in this review.
- The MEXC endpoint's inclusion of a forming last candle (used in Finding 2) is asserted from general exchange behavior, not verified from the artefacts; the rest of Finding 2 stands independently of that sub-point.
