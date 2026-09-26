# Run C — Kimi K3, Tiers 2, 3 and 4

OpenRouter, 2026-08-27. Max Tokens 64,000, reasoning effort Max.
7 architectural principles, 10 process disciplines, 6 stated preferences.
All 21 Tier 1 invariants audited in Runs A and B, out of scope here.
Note: this run had web access and fetched the public repository; Runs 1, A and B did not.
Auditor's verbatim output.

---

I'll verify one externally-checkable claim in the Step 2a package before finalizing the process-tier findings: the claimed public GitHub repository (the package's only offered evidence for version control, checkpoints, and rollback capability).

**Audit scope:** Tier 2 (7 items), Tier 3 (10 items), Tier 4 (6 items) only. All claims from the Step 2a package and the Constitution were treated as unverified until checked against the supplied source and evidence files directly. One package claim was verifiable externally: the public repository `github.com/CaroluxRex1987/phase7-engine` does exist (created 2026-08-26, MIT licence, master branch, README matches the described layout). That claim is corroborated. Nothing else in this audit rests on web sources; all other evidence is from the artefacts supplied.

Correlation note that applies throughout: I am an AI auditor reasoning about artefacts largely written by another AI. Where a finding below grades "Compliant" based on comments/docstrings (which are author-written claims), I say so explicitly and do not treat them as independent confirmation. Where I lacked corroboration, the status is Unknown rather than Compliant.

---

# TIER 2 — ARCHITECTURAL PRINCIPLES

---

**Principle:** T2-1, Separation of responsibilities
**Status:** Non-compliant
**Severity:** Moderate (Tier 2 gap; the violating capability is latent, see Impact)
**Effort:** Small
**Evidence:** `models/bias_engine.py`, function `calculate_dynamic_bias`, "Validate DataFrame inputs" block: on detecting NaN it rewrites `df["close"]` via `ffill().bfill()` and rewrites `EMA_20/EMA_50/RSI` via `fillna(df["close"])` **in place on the caller's DataFrame**, silently. `core/engine_core.py` passes `df_struct` into this function and continues using it afterward for entry/risk/exit computation. The principle's third clause — "the decision layer doesn't silently redefine raw signals it receives" — is violated in design even though upstream NaN-cleaning in `indicators/indicators.add_technical_indicators` makes the path unlikely to fire in practice. The data-acquisition and indicator clauses check out: `data/data_fetcher.py` contains no decision logic; `indicators/*` contain no risk logic.
**Impact:** A module in the decision chain can silently rewrite its inputs and propagate mutated values to downstream modules, defeating the boundary the audit is supposed to be able to rely on. Latent today; real the moment upstream cleaning misses a NaN.
**Required action:** Replace in-place mutation with a local copy inside `calculate_dynamic_bias`, or remove the cleaning block and treat dirty input as an error passed back up the chain.
**Verification:** Pass a DataFrame containing a NaN in `EMA_20` into `calculate_dynamic_bias` and confirm the caller's DataFrame is bitwise unchanged afterward.
**Re-audit:** Yes, after the change.

---

**Principle:** T2-2, Observation → interpretation → decision → risk/action
**Status:** Compliant
**Severity:** —
**Effort:** None
**Evidence:** `core/engine_core.py`, `Phase7Engine.run`, numbered pipeline sections: §2 indicators (`indicators/indicators.py`, raw values — observation), §4 trend health (`indicators/trend_health.py`, returns `trend_health`/`trend_direction` — interpretation), §5 bias (`models/bias_engine.py`), §7 entry, §8 risk (`models/risk_model.py` — risk), with final decision isolated in `models/decision_model.py` → `DecisionModel.evaluate` (called only from `models/signal_router.py`). No single function spans all four stages. This is checkable from the call graph alone without trusting any comment.
**Impact:** None standing.
**Required action:** None.
**Verification:** Re-trace the call graph on any future refactor; the stage boundaries must remain separate functions.
**Re-audit:** No, unless architecture changes.

---

**Principle:** T2-3, Explicit interfaces/contracts
**Status:** Non-compliant
**Severity:** Moderate
**Effort:** Medium
**Evidence:** The only formal contract in the engine is `structure/structure.py`'s `StructureAnalysisResult(TypedDict)`. The cross-module decision object — consumed by `core/panel_render.py`, assembled in `models/signal_router._build_decision_object`, and read by `live_trading.py` — is an implicit shape defined only in assembler code and `.get()` calls with defaults. The failure history confirms this has already broken once: `live_trading.py`'s own docstring records reading `entry_zone_lower/upper` and `exit.final_action` after the shape had drifted to `zone_lower/upper` and `exit.action` (would raise KeyErrors, per that docstring). A fix comment is claim; the drift itself is the evidence.
**Impact:** Any consumer written against the decision object (panel, simulator, future backtester) can break silently on rename, and there is no schema to diff against.
**Required action:** Define a single schema for the decision object (TypedDict/dataclass) in one module; have `signal_router` build it and `panel_render`/`live_trading` consume only declared fields.
**Verification:** Static check (e.g. mypy) passes on all three consumers against the declared type; add a test that instantiates the object and asserts field presence.
**Re-audit:** Yes.

---

**Principle:** T2-4, Explicit configuration
**Status:** Non-compliant
**Severity:** Moderate
**Effort:** Small
**Evidence:** `core/config.py` defines `EMA_FAST=20`, `EMA_SLOW=50`, `RSI_LENGTH=14`, `ADX_LENGTH=14`, `ATR_LENGTH=14`, `BB_LENGTH=20`, `BB_STD=2.0`, `VWMA_LENGTH=20`, `KAMA_LENGTH=10`. `indicators/indicators.add_technical_indicators` references **none of them**: it hardcodes `ta.ema(close_prices, length=20)`, `ta.rsi(df["close"], length=14)`, `ta.bbands(..., length=20, std=2.0)`, `ta.adx(..., length=14)`, `ta.atr(..., length=14)`, `ta.kama(..., length=10)`, and VWMA `rolling(window=20)`. Only SuperTrend reads config (`config.SUPERTREND_LENGTH/MULT`, per the A9 comment). Additionally, decision-critical thresholds are buried in logic: `models/decision_model._determine_final_action` hardcodes `trend_health >= 75`, `entry_score >= 70`; `models/bias_engine.BiasStateMachine` hardcodes ±30/±20. These are the principle's own "mystery constants."
**Impact:** Editing `config.RSI_LENGTH` changes nothing; the file advertises central control the code does not honour. Any user trusting config is silently running different parameters than they set.
**Required action:** Wire all indicator lengths/periods through `config`; move decision thresholds to named constants in config or module-level named constants with a single reading point.
**Verification:** Change one value (e.g. `RSI_LENGTH=21`), rerun, confirm the RSI column differs from the length-14 baseline.
**Re-audit:** Yes.

---

**Principle:** T2-5, Modular design
**Status:** Compliant, with two Minor observations
**Severity:** Minor (observations only)
**Effort:** Small
**Evidence:** Module map in source: `data_fetcher` (fetch), `indicators` (values), `trend_health` (trend scoring), `volume_profile` (profile), `structure` (structure/volume sentiment), `bias_engine` (bias/state machine), `risk_model` (stop/targets/sizing), `entry_model` (signals/quality), `decision_model` (final action/confidence/EV/explanation), `panel_render` (display), `plotting` (charts), `signal_router` (assembly). Two blemishes, both checkable: (1) `core/engine_core.py` step 8 computes the validation score/state/note **inline in the orchestrator** rather than in a module; (2) `models/signal_router._build_decision_object` overwrites `exit.action` with `DecisionModel`'s `final_action`, so `models/exit_model.compute_exit`'s own `exit_signal` computation is executed and then discarded (only `current_price` survives) — dead-ish work crossing a module boundary.
**Impact:** (1) Validation logic lives where it can't be unit-tested in isolation. (2) Wasted computation and a misleading contract: callers can read `exit_model` output and believe it drove the displayed action.
**Required action:** Extract validation scoring into its own module or into `risk_model`; either consume `exit_model`'s signal or stop computing it.
**Verification:** Neither observation survives a source diff after the change.
**Re-audit:** For the two observations, yes.

---

**Principle:** T2-6, Controlled dependencies
**Status:** Non-compliant
**Severity:** Moderate
**Effort:** Small
**Evidence:** `requirements.txt` lists `pandas, numpy, matplotlib, ccxt, pandas_ta`. Against the 19 supplied files: (a) `data/data_fetcher.py` imports `requests` — **not declared**; (b) `core/panel_render.py` imports `colorama` — **not declared** (soft-fallback exists, but it is still an undeclared optional dependency); (c) `ccxt` is declared but no file imports it — the Step 2a claim of non-use is confirmed against the supplied source. Dependency drift discovered by breakage is also on record in `phase7_engine.log` at 2026-08-25 01:13:30: `ERROR - Failed to import required modules: cannot import name 'config' from 'models' (D:\phase7_engine\models\__init__.py)`.
**Impact:** A clean-environment install fails at `import requests` before the engine starts; the unused `ccxt` stays on the manifest, widening supply-chain surface for an order-execution-capable library.
**Required action:** Regenerate the manifest from actual imports (add `requests`, decide on `colorama`, drop or gate `ccxt`); guard against import drift with a smoke import test.
**Verification:** Fresh venv, install only from `requirements.txt`, run `test_live.py` to completion.
**Re-audit:** Yes.

---

**Principle:** T2-7, Explicit, evaluated changes to interfaces or behavior
**Status:** Compliant — graded primarily on authored fix-comments; see the correlation caveat
**Severity:** —
**Effort:** None
**Evidence:** The codebase carries labeled, located, downstream-evaluated change records: `models/risk_model.py` "A12 FIX" (targets now multiples of actual stop distance), `core/panel_render.py` "BUG FIX (found during A3/A4/A5 pass)" (validation-score display), `data/data_fetcher.py` "A13 FIX" (fetch-error surfacing), `models/bias_engine.py` EXTREME-VOLATILITY tier restoration, `structure/structure.py` "A11 FIX" (real HVN/LVN source), `indicators/indicators.py` "A9 FIX" (single canonical SuperTrend). Independent-ish corroboration exists for one of them: the supplied simulated trade record (`Logs/LiveSim/sim_trade_...json`, timestamp 2026-08-25T02:45) shows stop 0.4774, price 0.568, targets 0.6586/0.7491/0.8397, i.e. risk-multiples ≈ 1.00/2.00/3.00 — exactly what the A12 comment claims; the older `scan_summary_report.txt` (2026-08-24) shows R:R ≈ 0.68/1.35/2.03, consistent with the pre-fix behaviour. Correlation caveat: most of this finding rests on author-written comments, and my habit of accepting a well-formed "FIX" comment as evidence is plausibly shared with the model that wrote them; the numeric corroboration is the only part that is not author-voice evidence.
**Impact:** None standing.
**Required action:** None for the current state; the habit should move to commit messages/ADR files rather than living only in source comments.
**Verification:** The A12-style numeric check above is repeatable against any new simulated trade record.
**Re-audit:** Yes, at next interface change.

---

# TIER 3 — ENGINEERING PROCESS

Tier 3 is process. Per the audit rules, I do not infer that a process existed because the code looks like its product. Most items here are Unknown, and that is a result, not a gap in effort.

---

**Principle:** T3-1, Hypothesis-driven development
**Status:** Unknown
**Severity:** Moderate if the gap is real (suspected, not established)
**Effort:** Medium to remedy by practice, None to establish alone
**Evidence:** No artefact supplied demonstrates the problem→hypothesis→implementation→test→measurement→evaluation cycle for any change. The source carries labels resembling a plan (A1–A13, B1/B2, C1–C4, "Roadmap Layer 2/5") — e.g. `models/decision_model.py` docstring, `models/entry_model.py` comment — and the fetched README references an "engineering log" in `docs/`, but neither the log nor any hypothesis/test/measurement record was supplied to this audit. Correlation caveat: the labels look like a disciplined process *to me* partly because I and the builder share habits; that resemblance is exactly what "Unknown" exists to withhold.
**Impact:** If changes were not hypothesis-driven, the engine accumulates features whose acceptance was never falsifiable (relevant to Tier 1 Item 7's empirically-unvalidated prediction feature, found out of scope here).
**Required action:** Produce the engineering log/hypothesis records for the labeled changes (A1–A13, B/C series) showing pre-stated problem and acceptance test.
**Verification:** Each labeled change maps to a dated hypothesis entry with test and measurement recorded.
**Re-audit:** Yes, once the engineering log is in the evidence bundle.

---

**Principle:** T3-2, Controlled changes
**Status:** Unknown
**Severity:** Moderate if the gap is real
**Effort:** Medium
**Evidence:** `phase7_engine.log` shows a sequence of single-failure-run-fix cycles (e.g. 2026-08-24 02:36 `fillna() ... 'method'` failure, later runs clean; 2026-08-25 00:07 `unterminated f-string` in `volume_profile.py`, 00:21 clean run). That is *consistent with* narrow, isolated changes — and also consistent with uncontrolled changes discovered one at a time. The artefacts cannot distinguish the two, and per the audit rules I do not grade resemblance as compliance.
**Impact:** If changes are not narrow, failures cannot be attributed (the Constitution's Duhem-Quine rationale), which in practice converts every debugging session into archaeology.
**Required action:** Commit-per-change practice with the stated scope in the message; the (now verified) git history should show it.
**Verification:** Review commit history: each commit's diff confined to one labeled change (A-n, B-n, C-n series), with the stated scope in the message.
**Re-audit:** Yes, against the git history (now possible, since the repo's existence is verified).

---

**Principle:** T3-3, Automated tests
**Status:** Non-compliant
**Severity:** Moderate
**Effort:** Medium
**Evidence:** No test framework exists among the 19 files: `requirements.txt` (44 B) contains no test library; the only test artefact is `test_live.py`, a one-shot smoke script printing a log path. The dependence on manual run-and-observe testing is directly evidenced by runtime-caught syntax/type errors in `phase7_engine.log`: 2026-08-24 17:06:05 `name 'Optional' is not defined`; 17:14/17:15/17:16 `name 'Any' is not defined`; 2026-08-25 00:07:38 `unterminated f-string ... (volume_profile.py, line 105)`; 00:10:49 `expected 'except' or 'finally' block (volume_profile.py, line 208)`; 00:52:28 `invalid syntax (indicators.py, line 121)`; 00:53:37 `unindent does not match any outer indentation level (indicators.py, line 102)`; 01:13:30 `cannot import name 'config' from 'models'`. Any automated import/compile check would have caught every one of these before a run.
**Impact:** Modifications are accepted and only then discovered broken at runtime — repeatedly, per the log — and the same class of breakage will recur on the next change and in the future backtesting build.
**Required action:** Introduce pytest with at least import/compile checks and golden-path engine tests; run on every change (CI or pre-commit).
**Verification:** A test command exits nonzero on each of the logged failure classes (bad import, syntax error, typing-name error).
**Re-audit:** Yes.

---

**Principle:** T3-4, Regression tests
**Status:** Non-compliant
**Severity:** Moderate
**Effort:** Medium
**Evidence:** No regression infrastructure exists in the supplied artefacts (same basis as T3-3: no framework, no suite). `phase7_engine.log` records behaviour that broke, was fixed, then broke again in sequence — e.g. the 2026-08-24 02:36 indicator failure cleared, then 2026-08-25 01:13:30 an import regression appeared (`cannot import name 'config' from 'models'`), then cleared by 01:18. There is also no fixed golden output to regress against (see T3-5).
**Impact:** Fixes carry no guard; each modification can silently re-break a previously working module — and has, per the log's own sequence.
**Required action:** Golden-output snapshot tests for the engine pipeline plus import checks; run before acceptance of any change.
**Verification:** Reintroduce a known-fixed bug (e.g. the `models.config` import name) and confirm the suite fails.
**Re-audit:** Yes.

---

**Principle:** T3-5, Fixed evaluation datasets
**Status:** Unknown
**Severity:** Moderate if the dataset does not exist
**Effort:** Medium
**Evidence:** A mechanism for fixed files exists — `data/data_fetcher.load_csv` — but no dataset artefact is present in the package, and every logged run (`phase7_engine.log`, `scan_summary_report.txt`) fetched live MEXC data. Absence in a Claude-assembled bundle is weak evidence of absence generally, but the packager's own statement that "no other evidence exists to bundle" makes a fixed dataset's existence genuinely uncertain rather than established.
**Impact:** Without a pinned dataset, "better/worse" per change is unmeasurable; T3-4 regression testing cannot be built; the backtesting build the Constitution sequences next would begin without its own stated prerequisite.
**Required action:** Commit at least one frozen OHLC dataset; run evaluations against it and record the dataset identity with results.
**Verification:** Two runs against the dataset produce identical outputs; the dataset hash is recorded alongside results.
**Re-audit:** Yes.

---

**Principle:** T3-6, Version control
**Status:** Compliant (with a caveat worth recording)
**Severity:** —
**Effort:** None
**Evidence:** Externally verified: `github.com/CaroluxRex1987/phase7-engine` resolves (fetched during this audit): git repository, master branch, MIT licence, README layout matching the 19 supplied files, created **2026-08-26 21:57 UTC**. Caveat: `phase7_engine.log` shows active development running 2026-08-24 through 2026-08-26, so most of the development history shown in the evidence predates the repository. Version control exists now; it did not exist for most of the logged work.
**Impact:** None for current state; the caveat means history before 2026-08-26 is effectively one flattened snapshot.
**Required action:** None beyond continuing in-repo development.
**Verification:** The URL resolves; commits continue to accrue against ongoing changes.
**Re-audit:** Yes, on the history-depth caveat at next audit.

---

**Principle:** T3-7, Known-good checkpoints
**Status:** Unknown
**Severity:** Moderate if checkpointing is not practised
**Effort:** Small once in VCS
**Evidence:** The repository exists (verified, see T3-6) but the supplied artefacts contain no tags, releases, or named checkpoint references, and the README fetch did not establish any. Existence of git ≠ practice of checkpointing; nothing further is checkable.
**Impact:** Without preserved known-good states, a bad change to the engine — which this engine's own history (`phase7_engine.log`, multiple failure runs) shows is routine — has no defined return point, precisely the failure the Constitution's Item 17 narrative fears for the next build.
**Required action:** Tag a known-good state now; tag before each future significant modification.
**Verification:** Tags exist in the repository and any tag can be checked out and run.
**Re-audit:** Yes.

---

**Principle:** T3-8, Reproducible experiments
**Status:** Unknown
**Severity:** Moderate
**Effort:** Medium
**Evidence:** No experiment record exists in the supplied artefacts. The engine fetches live data per run (config-driven, `data/data_fetcher.get_tf`), maintains a cross-run state file (`Logs/phase7_state_AEROUSDT_4h.json`, supplied: `{"supertrend_direction": 1.0, "detailed_bias": "BULLISH CONFIRMED"}`), and has no pinned dataset (see T3-5). Whether any validation result could be rerun to the same measured value is not determinable from these artefacts.
**Impact:** Validation claims cannot be independently rerun; "it worked when I ran it" cannot be distinguished from "it reproducibly works" — the distinction the Constitution's own Item 4/5 (out of scope) also depends on.
**Required action:** Pin dataset + config + version for at least one recorded experiment and record its output hash.
**Verification:** A third party reruns and reproduces the recorded result.
**Re-audit:** Yes.

---

**Principle:** T3-9, Rollback capability
**Status:** Compliant for capability; Unknown for depth
**Severity:** — for capability; Moderate if depth turns out to be absent
**Effort:** None/Small
**Evidence:** The mechanism (git with remote) is verified present (see T3-6). Depth — whether any meaningful earlier state exists to roll back *to* — cannot be established, since the repository was created after most logged development and the commit history was not part of the evidence bundle. I report one status on the rule as worded ("capability"), and flag the depth question rather than silently folding it into a clean Compliant. Hmm — correction: the status must be one value. Status: Compliant for the mechanism as the rule states, with depth **flagged** as an unverified sub-question.

**Impact:** Capability is now present; if history is a single squashed snapshot, rollback can only reach as far back as the initial commit — no earlier working state may exist to return to.
**Required action:** Confirm commit history depth; if flattened, accept a tagged known-good baseline as the rollback floor (ties to T3-7).
**Verification:** `git log` shows more than one meaningful checkpoint; a `git checkout <earlier-good>` run succeeds.
**Re-audit:** Yes, once (to close the depth question).

---

**Principle:** T3-10, Documentation of significant decisions
**Status:** Compliant
**Severity:** —
**Effort:** None
**Evidence:** Decision documentation exists in directly checkable form inside the supplied source: each significant change carries an explanation of *why*, located at the change — e.g. `models/risk_model.py` A12 (R:R construction), `core/panel_render.py` validation-display mix-up including *why it went unnoticed* (coincidental proximity of two scores), `live_trading.py` docstring recording both the broken import and the architectural reason for rewiring through `SignalRouter`. External corroboration: the fetched README (github.com/CaroluxRex1987/phase7-engine) references an "engineering log" in `docs/` recording decisions including mistakes. Caveat: this grades *documentation of decisions*, not their quality; and part of the pattern (well-written "FIX" rationale) is exactly the kind of artefact that reads convincingly to models sharing the builder's training habits — noted rather than treated as independent proof.
**Impact:** None standing.
**Required action:** Move records to durable form (ADR files / commit history) so they survive code edits.
**Verification:** For any labeled change, the *why* is retrievable without reading source (ADR or log entry).
**Re-audit:** No, provided the practice continues.

---

# TIER 4 — ENGINEERING PREFERENCES

Graded as preferences. Departures are noted with deliberateness where inferable; none are inflated into defects.

---

**Principle:** T4-1, Robustness over optimization
**Status:** Compliant (preference honoured)
**Severity:** —
**Effort:** None
**Evidence:** `indicators/indicators.py` carries hand-computed fallback paths for RSI, Bollinger, ADX, ATR, KAMA, SuperTrend when `pandas_ta` fails; `indicators.indicators.clean_series` provides layered NaN/inf cleaning with fallbacks; `core/engine_core.py` bounds caches (`_max_cache_size = 15`, FIFO eviction); `structure/structure.py` StructureEngine wraps each sub-routine with a fallback. Robustness choices are visibly preferred over tuned precision throughout.
**Impact:** —
**Required action:** None.
**Verification:** n/a.
**Re-audit:** No.

---

**Principle:** T4-2, Generalization over historical fit
**Status:** Compliant (preference honoured)
**Severity:** —
**Effort:** None
**Evidence:** `scan_summary_report.txt` (supplied) runs the engine across BTCUSDT, ETHUSDT, XRPUSDT, ADAUSDT, LINKUSDT, SOLUSDT, AEROUSDT over 1h/4h/1d/1w timeframes — the symbol is a parameter (`core/config.SYMBOL`, `engine_core.run(symbol=...)`), and multi-asset output is directly observable in that evidence file. This counters the "one asset" concern the preference names.
**Impact:** —
**Required action:** None.
**Verification:** n/a.
**Re-audit:** No.

---

**Principle:** T4-3, Explainability over unnecessary opacity
**Status:** Compliant (preference honoured)
**Severity:** —
**Effort:** None
**Evidence:** `models/decision_model.evaluate` builds `explanation.reasons` (plain-language rationale per output); `core/panel_render.py` renders a "Decision Reasoning" section plus advisory "Exit Watch"; `models/exit_model.build_exit_watch` emits sentences, not opaque flags; `scan_summary_report.txt` shows "Validation Notes" in plain text. Correlation caveat: this grades explainability-by-construction from the code path, which is checkable, not the woo claim in comments.
**Impact:** —
**Required action:** None.
**Verification:** n/a.
**Re-audit:** No.

---

**Principle:** T4-4, Stability over flashy outputs
**Status:** Compliant (preference honoured, one Minor cosmetic note)
**Severity:** Minor
**Effort:** Small
**Evidence:** `structure/structure.py` `_detect_regime` uses a hysteresis buffer (`threshold = 0.0015`) to prevent regime whipsaw; `models/bias_engine.BiasStateMachine` gates state flips on score thresholds; defensive defaults are pervasive (`trend_health.py` `default_response`, engine-core fallbacks). Cosmetic note, not a violation: in `scan_summary_report.txt` panels, `TREND` and `MOMENTUM` render the same value (e.g. both `EXTENDED (90.00)`) because the TREND line falls back to `momentum_mode` when `trend_direction` is absent — a duplication the current source has since addressed via `trend_direction` (`indicators/trend_health.py`, `models/signal_router.py`).
**Impact:** Duplicated panel fields waste reader attention marginally; nothing miscomputed.
**Required action:** Ensure panel's TREND field reads `trend_direction` only.
**Verification:** Scan output shows distinct TREND/MOMENTUM values where they genuinely differ.
**Re-audit:** No (cosmetic).

---

**Principle:** T4-5, Useful information over more information
**Status:** Compliant, with one Minor departure flagged — looks inadvertent, not deliberate
**Severity:** Minor
**Effort:** Small
**Evidence:** Honoured: `core/panel_render.py` documents a deliberate removal — position-size and EV line dropped from the panel at Viktor's request, upstream computation retained. Departure: the supplied simulated trade record (`Logs/LiveSim/sim_trade_...json`) contains `"entry_zone": {"lower": 0.496554..., "upper": 0.467111...}` — lower > upper. Cause is visible in source: `core/engine_core.py` sets `entry_zone_lower = EMA_20`, `entry_zone_upper = EMA_50`, which invert whenever EMA20 > EMA50; `models/entry_model.calculate_entry_quality` swaps internally for scoring, but the un-swapped pair is still exported into the decision object and rendered ("ENTRY ZONE: $0.4966 - $0.4671"). This undermines panel *usefulness* (information presented inverted). Judged a departure from the preference, not a defect, and apparently inadvertent — though note it also touches displayed honesty of numbers (Tier 1 territory, out of scope here, worth handing to that audit).
**Impact:** A displayed price interval occasionally reads as nonsense; confidence in displayed numbers erodes each time.
**Required action:** Normalize ordering at the source in `engine_core.py` (present min/max), not only inside the scorer.
**Verification:** Force EMA20>EMA50 input; exported `zone_lower < zone_upper` and panel reads sensibly.
**Re-audit:** Yes (minor, but fix verification is cheap).

---

**Principle:** T4-6, Prefer the simpler design when invariants are equally satisfied (tie-breaker)
**Status:** Unknown
**Severity:** Minor by construction (Tier 4)
**Effort:** —
**Evidence:** A tie-breaking preference cannot be observed in a single snapshot of one codebase: there is no artefact recording alternative designs that cleared the invariants and the choice made between them. The now-deleted duplicate SuperTrend implementation (referenced by the "A9 FIX" comment in `indicators/indicators.py`) is a claim that a simplicity tie-break was once applied; the deletion is not independently verifiable because the deleted file is not in the supplied package.
**Impact:** If the preference is not practised, complexity accretes despite Tier 1 Item 16, raising audit surface per change.
**Required action:** Record rejected alternatives in the engineering log when a tie-break decision occurs.
**Verification:** At least one documented future tie-break with the rejected alternative named.
**Re-audit:** Yes, opportunistically.

---

# SUMMARY TABLE

| # | Item | Status | Severity |
|---|------|--------|----------|
| T2-1 | Separation of responsibilities | Non-compliant | Moderate |
| T2-2 | Observation→interpretation→decision→risk | Compliant | — |
| T2-3 | Explicit interfaces/contracts | Non-compliant | Moderate |
| T2-4 | Explicit configuration | Non-compliant | Moderate |
| T2-5 | Modular design | Compliant (2 Minor observations) | Minor |
| T2-6 | Controlled dependencies | Non-compliant | Moderate |
| T2-7 | Explicit, evaluated changes | Compliant (correlation caveat noted) | — |
| T3-1 | Hypothesis-driven development | Unknown | Moderate (if real) |
| T3-2 | Controlled changes | Unknown | Moderate (if real) |
| T3-3 | Automated tests | Non-compliant | Moderate |
| T3-4 | Regression tests | Non-compliant | Moderate |
| T3-5 | Fixed evaluation datasets | Unknown | Moderate (if absent) |
| T3-6 | Version control | Compliant (repo verified; pre-2026-08-26 history caveat) | — |
| T3-7 | Known-good checkpoints | Unknown | Moderate (if absent) |
| T3-8 | Reproducible experiments | Unknown | Moderate |
| T3-9 | Rollback capability | Compliant for capability; depth unverified | Moderate (if depth absent) |
| T3-10 | Documentation of significant decisions | Compliant | — |
| T4-1 | Robustness over optimization | Compliant | — |
| T4-2 | Generalization over historical fit | Compliant | — |
| T4-3 | Explainability over opacity | Compliant | — |
| T4-4 | Stability over flashy outputs | Compliant (cosmetic note) | Minor |
| T4-5 | Useful information over more information | Compliant (one inadvertent departure: inverted entry zone) | Minor |
| T4-6 | Simpler design tie-breaker | Unknown | Minor |

**Package-claim verification score:** the claim that the public repository exists is confirmed (fetched directly, this audit). Two source-checkable claims from the package also hold against the supplied code: ccxt declared-but-unimported, and the empty `API_KEY`/`API_SECRET` pair in `core/config.py`. I did not treat the package's characterizations of module behaviour as evidence; where they mattered, I read the module.

**Highest-leverage items for the re-audit queue:** T3-3/T3-4 (no automated/regression testing — the runtime log supplies its own counter-evidence), T2-4 (config file disconnected from the logic it appears to govern), and the T3-1/T3-5/T3-7/T3-8 cluster of Unknowns, which become answerable the moment the engineering log and at least one pinned dataset are added to the evidence bundle.
