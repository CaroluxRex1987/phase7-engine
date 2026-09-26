# Run B — Kimi K3, Tier 1 invariants outside the MVA gate

OpenRouter, 2026-08-27. Max Tokens 64,000, reasoning effort Max.
Items 1, 4, 5, 7-17, 19-21. Items 2, 3, 6 and 18 audited separately in Run A.
Auditor's verbatim output.

---

## AUDIT FINDINGS — TIER 1 INVARIANTS (Items 1, 4, 5, 7–17, 19–21)

Out of scope per instruction: Items 2, 3, 6, 18. Tiers 2–4 not touched.

All evidence was checked directly against the supplied source bundle and the four evidence files (`phase7_engine.log`, `scan_summary_report.txt`, `phase7_state_AEROUSDT_4h.json`, `sim_trade_*.json`). Where the Step 2a package made a claim I could not verify from the artefacts, that is stated.

---

**Principle — Item 1: Tool, Not Autonomous Actor**
**Status — Compliant**
**Severity — Minor**
**Effort — None**
**Evidence** — I scanned the full supplied source myself rather than trusting the package's Section 2 search results: the only network call in any file is `requests.get(url, params=params)` in `data/data_fetcher.py` (public MEXC klines endpoint, GET only). No POST/PUT/DELETE, no order-placement call (`create_order`, `place_order`, `.buy`, `.sell`, etc.) anywhere in the 19 files. `live_trading.py` builds a dict and writes JSON to `Logs/LiveSim/` — no exchange interaction. `requirements.txt` lists ccxt, but no file imports it (verified by reading every import block in the bundle).
**Impact** — None currently; the engine cannot act externally.
**Required action** — None.
**Verification** — Re-run the same pattern scan on any future revision; the absence result must hold.
**Re-audit** — Yes, whenever a new dependency or module is added.

---

**Principle — Item 4: Determinism**
**Status — Compliant (via a documented, pre-audit exception)**
**Severity — Minor**
**Effort — None**
**Evidence** — `core/engine_core.py` contains a comment block headed "C3 BUILD: cross-run state persistence" describing the disk state file used for SuperTrend-flip/bias-flip Exit Watch comparisons. That documentation ships inside the audited source, so it predates this audit and is admissible under Item 4's own audit guidance. The nondeterminism affects only advisory `exit_watch` flags; `final_action` in `models/decision_model.py` does not consume `exit_watch`. `BiasStateMachine.transition` computes its new state purely from `(raw_bias, bias_score)`; `self.state` is only a container, so instance reuse does not create history dependence. `live_trading.py`'s `datetime.utcnow()` touches log timestamps only.
**Impact** — Exit Watch flip flags can differ for identical market input depending on prior run — by design, and documented.
**Required action** — None, provided the C3 comment remains; any further cross-run state must be documented before the next audit.
**Verification** — Run twice on frozen data with the state file removed vs. present: decision fields identical, only flip flags differ, as designed. Confirmed consistent with `Logs/phase7_state_AEROUSDT_4h.json` content matching `_save_state`'s schema exactly.
**Re-audit** — Yes, on any new statefulness.

---

**Principle — Item 5: Reproducibility**
**Status — Non-compliant**
**Severity — Major**
**Effort — Small-to-Medium**
**Evidence** — (a) `core/panel_render.py` prints, on every successful panel, the hardcoded line `Trade logged to Logs/phase7_trade_log_{symbol}.csv` — no file in the supplied 19-file bundle writes any such CSV (the only write paths are `engine_core._save_state` JSON, `plotting.py` PNG, `live_trading.py` JSON). The claimed record location does not exist. (b) `core/config.py` defines `engine_version = "Phase‑7 Structural Quant Engine v1.0"`, but that string is never written into the decision object, the logs, or the simulated-trade JSON (`Logs/LiveSim/sim_trade_….json` contains timestamp/symbol/decision/risk only — no version, no config snapshot, no data-source tag).
**Impact** — "Why did the engine produce this decision" is not reconstructable: no engine version, no parameter snapshot, and the one artifact the panel claims exists (the trade CSV) is never written. This also undermines the Constitution's own retention question — it was left implicit rather than forced.
**Required action** — Stamp engine version, config snapshot, and data-source/timestamp into the decision object and into every persisted artifact; either actually write the CSV the panel advertises or remove the claim.
**Verification** — One run must produce a persisted record containing version + parameter snapshot; the panel's log-destination line must name a file that provably exists.
**Re-audit** — Yes, after the fix.

---

**Principle — Item 7: No Unsupported Predictive Claims**
**Status — Non-compliant**
**Severity — Major**
**Effort — Small**
**Evidence** — The "BTC-Adjusted AERO Prediction" renders `BTC-ADJUSTED CONFIDENCE: x/100` on the panel (`core/panel_render.py` BTC section; `models/decision_model.py._compute_btc_adjusted`) with no "empirically unvalidated" label anywhere. The Constitution's resolution for this feature requires a label such as "Prediction V1: computationally validated, empirically unvalidated" wherever the feature is presented. That label exists nowhere in the decision object reasons or the panel. (The package's §5.1 quotes a README carrying the label — that README is not among the supplied artefacts, so I cannot verify it; the code itself lacks the label.) Note the contrast: the EV line does carry an honest tag — "Expected value (illustrative, not backtested)" — so the engine knows how to do this and simply didn't for BTC-adjusted confidence.
**Impact** — A predictive adjustment is presented to the trader with the same visual weight as validated quantities; the exact gap the Constitution pre-flagged.
**Required action** — Add the "computationally validated, empirically unvalidated" label to the BTC-adjusted panel section and to the decision-model reason string.
**Verification** — Panel output for any run shows the label adjacent to `BTC-ADJUSTED CONFIDENCE`.
**Re-audit** — Yes.

Correlation note: Item 7 was pre-flagged in both the Constitution and the audit package, so this finding is confirmation of an already-named open question, not an independent discovery. The finding stands on verifiable code evidence, but its novelty is nil; the items below (10, 11, 13, 14, 16) are independent of the pre-flagged set.

---

**Principle — Item 8: Epistemic Honesty**
**Status — Non-compliant**
**Severity — Major**
**Effort — Medium**
**Evidence** — (a) `indicators/indicators.py`: when `pandas_ta` fails, hardcoded synthetic values are injected silently — `df["RSI"] = 50.0`, `df["ADX"] = 25.0`, `df["ATR"] = df["close"] * 0.02`, `df["SuperTrend"] = df["close"]`, `ST_Direction = 1.0` — and nothing in the decision object records that these are defaults, not measurements. The panel renders them as real numbers. (b) `core/panel_render.py` asserts a trade-log CSV exists (see Item 5) — stating as fact what is not true. (c) `models/decision_model.py` marks the EV line "illustrative, not backtested" and labels BTC context "informational only" — partial compliance that makes the unlabeled fallbacks in (a) stand out rather than excuse them.
**Impact** — A number can be "hypothesized/default" while appearing "measured" — the precise blurring this invariant exists to prevent; it flows into bias and decision.
**Required action** — Propagate a synthetic-data flag from indicator fallbacks into the decision object and render it on the panel; fix the phantom CSV claim (with Item 5).
**Verification** — Force `pandas_ta` to fail in a test; the panel must show a fallback/degraded marker, and confidence must be reduced.
**Re-audit** — Yes.

---

**Principle — Item 9: Every Measurement Has a Precise Definition**
**Status — Compliant (with a remark)**
**Severity — Minor**
**Effort — None**
**Evidence** — The numeric terms do have explicit mathematical definitions in code: `trend_health` (`indicators/trend_health.py`, slope+ADX+RSI components), `bias_score` (`models/bias_engine.py`, named weights summing to 1.00), entry quality sub-scores (`models/entry_model.py`, capped point tables), `validation_score` (`core/engine_core.py`, threshold rules), `confidence` (`models/decision_model.py._compute_confidence`, stated formula), risk thresholds (`models/risk_model.py`, 0.2%–15% stop band).
**Impact** — Definitions exist, but they live scattered in code; there is no consolidated registry, so a term's definition can be changed without noticing dependents. Remark: `confidence` rendered to two decimals invites a probability reading the Constitution's working rule forbids unless calibrated — flagged, not violation.
**Required action** — Optionally consolidate definitions in one registry document.
**Verification** — Each named term has a code-or-document anchor; currently true.
**Re-audit** — Yes, if a term-registry amendment (Engineering Notes Entry #6) lands.

---

**Principle — Item 10: Consistent Semantics**
**Status — Non-compliant**
**Severity — Major**
**Effort — Small**
**Evidence** — (a) One quantity under three labels on the same panel: `models/decision_model.py._compute_trade_quality` sets `current_market = trend_health`; `core/engine_core.py` sets `trade_quality_current = trend["trend_health"]`; `core/panel_render.py` renders `TREND … (Score)`, `MOMENTUM … (same score)`, and `TRADE QUALITY / Current Market` — all equal. Visible in `Logs/scan_summary_report.txt`, e.g. the BTCUSDT 4h block: "TREND : EXTENDED (Score: 90.00)" / "MOMENTUM : EXTENDED (90.00)" / "Current Market : 90.00/100". (b) Field inversion: in `Logs/LiveSim/sim_trade_….json`, `entry_zone.lower = 0.49655…` and `upper = 0.46711…` — "lower" holds the higher value, because `core/engine_core.py` assigns `zone_lower = EMA_20`, `zone_upper = EMA_50` unconditionally (EMA20 > EMA50 in a downtrend); the internal swap in `entry_model.py` does not propagate back to the exported object. (c) The historical `confidence`/rename drift documented in `models/signal_router.py`'s docstring confirms this class recurs.
**Impact** — The trader reads one number as three different things, and downstream consumers (`live_trading.py`) export inverted "lower/upper" fields; semantics drift is precisely the bug class that broke fourteen modules in this project's own history.
**Required action** — De-duplicate the trend_health renderings or label them truthfully; enforce lower ≤ upper before export; remove or rename one of `risk_score`/`signal_strength` (both alias `bias_score` in `core/engine_core.py`).
**Verification** — On a known dataset, each label on the panel maps to exactly one definition; a downtrend run exports `lower < upper`.
**Re-audit** — Yes.

---

**Principle — Item 11: No Circular Reasoning**
**Status — Non-compliant**
**Severity — Critical**
**Effort — Medium**
**Evidence** — `trend_health` is recycled as if it were multiple independent confirmations: it is 30% of `bias_score` (`models/bias_engine.py`, `WEIGHT_TREND_HEALTH = 0.30`); it is then added AGAIN into confidence separately (`models/decision_model.py._compute_confidence`: `bias_strength*0.5 + trend_health*0.3 + …`, where `bias_strength = |bias_score|` already contains trend_health); it is the base of `validation_score` (`core/engine_core.py`: `val_score = trend_health`, ±adjustments), whose `validation_state` feeds the decision gate; and it is rendered again as "Current Market" trade quality. One underlying quantity is counted at least four times and presented as separate evidence. On the Constitution's pre-flagged Layer-5 question (`macro_bias` / `trend_direction` / `structure_sequence` in `models/entry_model.py`): I checked upstream provenance — macro uses 1d data, trend_direction uses EMA-slope sign, sequence uses swing pivots — not mutually derived, so that specific suspicion cleared; the trend_health recycling above is a separate, stronger instance found independently of the pre-flagged question.
**Impact** — Confidence and validation are mathematically inflated by double-counting, and both reach the panel and the trader — one signal "talking to itself in five accents" (the Constitution's own phrasing).
**Required action** — Eliminate re-counting: either remove trend_health from the confidence formula (it is already inside bias_score) or normalize bias_score to exclude it before reuse; give `validation_score` a non-trend_health basis or fold it into the same single factor.
**Verification** — Factor-provenance analysis: no input quantity contributes to the same score through two paths; ablated runs show a lower, honest confidence ceiling.
**Re-audit** — Yes.

---

**Principle — Item 12: No Hidden Decision-Affecting State**
**Status — Compliant (with the same documented exception as Item 4)**
**Severity — Minor**
**Effort — None**
**Evidence** — The one persistent state, the disk file written by `engine_core._save_state` (`Logs/phase7_state_AEROUSDT_4h.json`, 67 B, content matches schema exactly), is documented in the shipped source's C3 comment block — pre-audit documentation, admissible under Item 12's guidance — and influences only `exit_watch` advisory flags, not `final_action`. `BiasStateMachine` and `StructureEngine._last_regime` do not carry effective history between decisions (verified in code: the former is a pure function per call; the latter is re-instantiated inside `calculate_structure` every call, so its hysteresis never persists).
**Impact** — As designed; a note: `StructureEngine`'s advertised hysteresis ("State Machine … with Hysteresis") is inoperative because the engine is rebuilt per call — dead design, not hidden state.
**Required action** — None for compliance; consider removing the misleading hysteresis machinery or making it actually persistent + documented.
**Verification** — Two identical runs with the state file cleared vs. warm produce identical decision fields.
**Re-audit** — Yes.

---

**Principle — Item 13: Fail Safely**
**Status — Non-compliant**
**Severity — Critical**
**Effort — Medium**
**Evidence** — `indicators/indicators.py` `except`-fallback blocks inject confident-looking constants with no log and no degradation marker: `RSI = 50.0`, `ADX/DIP/DIM = 25.0`, `ATR = close*0.02`, `SuperTrend = close`, `ST_Direction = 1.0`. These feed `compute_trend_health` → `calculate_dynamic_bias` → `generate_entry_signals` → the decision. Similarly `structure.py._detect_hvn_lvn` silently falls back from real volume-profile nodes to price-extreme heuristics. Counter-evidence handled well elsewhere: the A13 fetch-failure surfacing (`data/data_fetcher.py`) and the risk gate (`models/risk_model.py`) do fail safely — visible in `Logs/LiveSim/sim_trade_….json` where `long_signal: true` was overridden to `NO-TRADE (RISK TOO HIGH)` with `risk_reason` recorded. But a fabricated RSI/ADX reaching the decision pipeline is not a safe failure.
**Impact** — Broken indicator computation can masquerade as a normal, confident panel; a data/tooling fault becomes pseudo-measured input that can move bias and the decision — the exact "confidence manufactured to fill a gap" scenario this invariant bans.
**Required action** — Log every fallback activation, propagate a degraded-data flag into the decision object, and force confidence/NO-TRADE semantics on degradation.
**Verification** — Induce a `pandas_ta` failure in test; engine must emit a degraded, visibly-marked output rather than constants.
**Re-audit** — Yes.

---

**Principle — Item 14: Risk Is Not Conviction**
**Status — Non-compliant**
**Severity — Major**
**Effort — Small**
**Evidence** — (a) `core/engine_core.py` writes `"risk_score": bias_score` (and `signal_strength` likewise) in the risk dict — a conviction magnitude parked under a risk label in the decision object. (b) The `validation_state` gate used by `_determine_final_action` is built from `val_score`, which starts as `trend_health` ± volume-sentiment adjustments (`core/engine_core.py`) — conviction-domain numbers masquerading as risk validation, and that gate does reach the WAIT/NO-TRADE logic. (c) Secondary, rationale-level: `core/engine_core.py` computes `position_size` from hardcoded `DEFAULT_ACCOUNT_BALANCE`/`DEFAULT_RISK_PERCENT` (C4 build) — the Rev-5-corrected rationale of Item 14 says position sizing must remain the trader's alone; "displayed-only" sizing lives in the decision object even after removal from the panel.
**Impact** — Conviction numerically substitutes for risk in object fields and in one decision gate; a strong directional read can launder itself into a "validation" result.
**Required action** — Remove/rename `risk_score`/`signal_strength`; rebase `validation_state` off risk-relevant inputs or stop it gating decisions; decide constitutionally whether displayed position sizing stands given Rev 5.
**Verification** — No risk-labeled field equals a conviction output; disabling trend_health adjusts no risk gate.
**Re-audit** — Yes.

---

**Principle — Item 15: Empirical Evidence Supersedes Theoretical Expectation**
**Status — Unknown**
**Severity — Moderate**
**Effort — N/A (blocked on backtesting/calibration existing)**
**Evidence** — There is no backtesting or calibration artifact in the supplied evidence bundle (confirmed: four evidence files are log, scan, state, one sim-trade JSON). The weighted-factor model (`models/bias_engine.py`) is entirely theoretically weighted; no measured-vs-theory comparison exists to resolve. Per the ratified Constitution, "Unknown … not a placeholder for laziness, a real outcome."
**Impact** — The invariant is untestable today; it will only bite once backtesting exists — which is exactly when it matters most.
**Required action** — When backtesting/calibration exists, test this item against concrete theory/measured conflicts.
**Verification** — A documented case where measured behavior contradicted theory, resolved in favor of measurement (or a justified exception).
**Re-audit** — Mandatory, post-backtesting.

---

**Principle — Item 16: Complexity Must Provide Demonstrated Value**
**Status — Non-compliant**
**Severity — Major**
**Effort — Small**
**Evidence** — I scanned all supplied files for consumers of each computed indicator: `indicators/indicators.py` computes Bollinger Bands (`BB_lower/middle/upper`), KAMA, DIP/DIM, and Typical_Price — no module in the bundle references any of them. Additionally `utils/plotting.py` checks for a `"VWAP"` column that is never produced (the indicators create `VWMA`), so even the chart's VWAP line is unreachable dead code.
**Impact** — Pure dead complexity: paid in code surface, NaN-handling paths, and failure modes, with zero demonstrated value — the exact pattern Item 16 disqualifies.
**Required action** — Delete the unused indicators and the unreachable VWAP plot branch, or wire each one into a documented decision/input role.
**Verification** — After removal, engine runs clean; search confirms no orphan references (or, if wired, a documented consumer exists).
**Re-audit** — Yes.

---

**Principle — Item 17: Backtesting Isolation**
**Status — Compliant (by absence of the subsystem)**
**Severity — Minor**
**Effort — None now**
**Evidence** — No backtesting component exists anywhere in the supplied 19-file source (verified by scanning the bundle — no `backtest` token). The package's claim that a `backtesting/` folder was removed cites a public README Status table that is not part of the artefacts, so that specific claim is unverifiable here; the absence within the audited source is directly verified.
**Impact** — Blast radius is trivially zero while backtesting does not exist. The invariant's purpose is forward-looking; the danger arrives with the rebuild.
**Required action** — None now. Before backtesting is rebuilt, isolation must be demonstrated (see Future Amendment Candidate "Backtesting Environment Isolation Contract").
**Verification** — Re-scan each revision for backtesting imports/hooks in the live path; their absence confirms continued compliance.
**Re-audit** — Mandatory the moment any backtesting module re-enters.

---

**Principle — Item 19: Withdrawal Permissions Are Never Enabled**
**Status — Compliant (vacuously — no credentials are held)**
**Severity — Minor**
**Effort — None**
**Evidence** — `core/config.py` holds `API_KEY = ""` and `API_SECRET = ""`; the engine touches no credential material anywhere (only public GET klines; no auth headers in `data/data_fetcher.py`).
**Impact** — No ability to move funds exists to be misused.
**Required action** — None.
**Verification** — Scan for credential material; confirm none.
**Re-audit** — Mandatory if any credential is ever introduced.

---

**Principle — Item 20: Credentials Are Never Exposed**
**Status — Compliant (on the channels auditable from the supplied artefacts)**
**Severity — Minor**
**Effort — None**
**Evidence** — No credential strings anywhere in source; the runtime log (`Logs/phase7_engine.log`) contains engine status/errors only (pandas kwarg errors, import errors, syntax-error lines during development) — no secrets. Error messages and `traceback.print_exc()` (`core/engine_core.py`) cannot leak what does not exist. Panel and scan report contain none.
**Impact** — None currently. Caveat: git history of the public repository is not among the artefacts, so "never committed to version control" cannot be verified from this package.
**Required action** — None for the audited channels.
**Verification** — Static scan of source + logs (done here); separately, a repo-history audit outside this package's scope (git log / secret-scanning) to close the VCS channel.
**Re-audit** — Yes, and mandatory upon introducing any real credential.

---

**Principle — Item 21: Operator Credentials Stay With the Operator**
**Status — Compliant (vacuously — no outbound channels exist)**
**Severity — Minor**
**Effort — None**
**Evidence** — The engine makes no outbound transmission of any kind beyond public GET klines; no telemetry, no crash reporter, no analytics, no support workflow exists in the supplied source. Multi-user capability does not exist yet — the invariant is pre-emptive, as written.
**Impact** — As designed; risk arrives with any future outbound feature.
**Required action** — None now.
**Verification** — Confirm zero outbound calls other than `requests.get` on the public endpoint (verified in this run).
**Re-audit** — Mandatory when any multi-user, telemetry, or reporting feature is proposed.

---

## Summary and required process notes

- **Compliant (8):** Items 1, 4, 9, 12, 17 (by absence), 19 (vacuous), 20 (auditable channels), 21 (vacuous).
- **Non-compliant (8):** Items 5, 7, 8, 10, 11 (Critical), 13 (Critical), 14, 16.
- **Unknown (1):** Item 15 — no backtesting/calibration artefact exists to test it against; this is the proper status, not a lapse.
- **Pre-flagged confirmation disclaimer:** The Constitution warned that an audit confirming only its two pre-flagged questions should be read as a warning sign. That did not happen here: Items 10, 11, 13, 14, 16, and the Item 5 phantom-CSV finding are new, independently derived findings; Item 7's confirmation rests on direct code evidence.
- **Package-claim verification status:** The Step 2a Section 2 search claims were re-run by me against the supplied source and held. The package's README-based claims (empirically-unvalidated label, removed backtesting folder's README rationale) could not be verified from the artefacts and are recorded as unverified.
- **Correlation disclosure:** Where my conclusions coincide with Claude-written comments in the code (e.g., accepting the A12/A13 fix narratives, judging the C3 state documentation admissible), shared-training-data habits may be inflating agreement; flagged here rather than presented as purely independent. Conversely, the circular-reasoning (Item 11), fail-safe fallbacks (Item 13), semantic-inversion (Item 10), phantom log claim (Item 5), and dead-indicator (Item 16) findings arose from direct scans of the bundle and do not depend on Claude's own self-documentation.

Suggested Step 5 priority: Criticals first (Item 11, Item 13 — both Small-Medium effort), then Major findings ordered by reachability (Items 7, 10, 8, 14, 16 — all Small; Item 5 — Small/Medium), then the Minor confirmations and the re-audit triggers for Items 17, 19, 20, 21.
