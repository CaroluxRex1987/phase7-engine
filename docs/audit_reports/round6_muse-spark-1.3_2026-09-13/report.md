I am Meta Muse Spark 1.3 — first reviewer in this project from a lab with no prior exposure to it. I recognise none of this code, Constitution, or documents from training; I am reading them here.

Package checks before grading: I opened the file named as the Constitution and confirmed it is the Constitution — 21 Tier-1 invariants (1–21), 7 Tier-2 principles, 10 Tier-3 items, 6 Tier-4 preferences, 44 rules, Version History ending at LICENSED 26 August 2026, no AUDITED/AMENDED/DEFECT rows, no verdict table, no Critical list. This document is Rev 7. I did not open `commit_messages_PART7_ONLY.md` for Parts 1–6. Comments, docstrings, transcripts and version history were treated as claims, never facts. On the seven rules with a prior verdict stated in comments/docstrings I graded from code; Part 6 says where a comment moved me.

# Part 1 — Verdict table

Tier 1 — Invariants:
- Item 1 Tool, Not Autonomous Actor — Compliant
- Item 2 No Future Information — Compliant
- Item 3 Data Integrity — Compliant
- Item 4 Determinism — Compliant
- Item 5 Reproducibility — Compliant
- Item 6 Traceability — Compliant
- Item 7 No Unsupported Predictive Claims — Compliant
- Item 8 Epistemic Honesty — Compliant
- Item 9 Every Measurement Has Precise Definition — Compliant
- Item 10 Consistent Semantics — Partially compliant
- Item 11 No Circular Reasoning — Compliant
- Item 12 No Hidden Decision-Affecting State — Compliant
- Item 13 Fail Safely — Compliant
- Item 14 Risk Is Not Conviction — Compliant
- Item 15 Empirical Evidence Supersedes Theory — Not verifiable
- Item 16 Complexity Must Provide Demonstrated Value — Compliant
- Item 17 Backtesting Isolated — Compliant
- Item 18 Read-Only Market Access — Compliant
- Item 19 Withdrawal Never Enabled — Compliant
- Item 20 Credentials Never Exposed — Compliant
- Item 21 Operator Credentials Stay With Operator — Compliant

Tier 2 — Architecture:
- T2-1 Separation of responsibilities — Compliant
- T2-2 Observation→interpretation→decision→risk — Compliant
- T2-3 Explicit interfaces/contracts — Compliant
- T2-4 Explicit configuration — Partially compliant
- T2-5 Modular design — Compliant
- T2-6 Controlled dependencies — Compliant
- T2-7 Explicit, evaluated changes — Compliant

Tier 3 — Process:
- T3-1 Hypothesis-driven development — Compliant
- T3-2 Controlled changes — Compliant
- T3-3 Automated tests — Compliant
- T3-4 Regression tests — Compliant
- T3-5 Fixed evaluation datasets — Compliant
- T3-6 Version control — Compliant
- T3-7 Known-good checkpoints — Compliant
- T3-8 Reproducible experiments — Compliant
- T3-9 Rollback capability — Compliant
- T3-10 Documentation of decisions — Compliant

Tier 4 — Preferences:
- T4-1 Robustness over optimization — Compliant
- T4-2 Generalization over historical fit — Compliant
- T4-3 Explainability over opacity — Compliant
- T4-4 Stability over flashy outputs — Compliant
- T4-5 Useful information over more information — Compliant
- T4-6 Prefer simpler — Compliant

# Part 2 — Findings, most severe first

## F1 — T2-4 Explicit configuration: decision-affecting numbers live as bare literals and locals, not configuration — Partially compliant — Moderate

**Location.** `models/entry_model.py` confluence ladder:
```
macro_multiplier = 1.0 ... macro_multiplier = 1.05 ... macro_multiplier = 0.90
trend_multiplier ... 1.05 ... 0.90
structure_multiplier ... 1.05 ... 0.90
```
`models/decision_model.py` bands: `if trend_health >= 75 and entry_score >= 70`, `elif trend_health >= 50`, `if raw_bias in (...) and bias_strength < MIN_ACTION_BIAS`, `MIN_ACTION_BIAS = 30.0` (fingerprinted, good) vs `RAW_BIAS_THRESHOLD = 20.0` in another module; `indicators/indicators.py`: `SPIKE_RATIO = 10.0` as a function local; `core/engine_core.py`: `compute_correlation_beta(... window=30)`; `structure/structure.py`: `threshold = 0.0015`.

**What the code does.** These decide entry scores (±5–10% each, product to 1.1576 or 0.9450 on transcripts), AGGRESSIVE vs LONG, spike degradation, correlation window, regime hysteresis. None is readable from `core/config.py`; several have no name at module scope at all, so `decision_log.module_snapshot()` structurally cannot hold them — the code's own `code_fingerprint.py` header says so explicitly.

**Clause broken.** T2-4: "Important behavior (RSI period, EMA windows, confidence caps) comes from named, visible configuration — not mystery constants buried in the logic."

**Concrete scenario.** Operator asks "what confluence penalty did this run use?" Record says nothing; changing `0.90` to `0.85` changes every entry score and possibly AGGRESSIVE eligibility while `run_hash`'s config half is byte-identical. Only `code_hash` moves, which answers "code differs" not "which knob". Same for `0.0015` → `0.0016`: structure regime flips on some bars, no readable record.

**Severity Moderate.** Tier-2 gap by rubric; does not by itself print a wrong number the operator acts on, but weakens explicit-configuration and makes the run record unreadable for exactly the numbers that move decisions. The project mitigates with the parse-tree hash; that mitigates detectability, not configurability.

I checked the obvious counter: wiring them all into config would itself be a decision-path change. I am not asking for that here; I am grading that today they are not explicit configuration.

## F2 — Item 10 Consistent Semantics: `confidence_score` means two different quantities in two layers — Partially compliant — Minor

**Location.** `core/engine_core.py`:
```
"confidence_score": trend["trend_health"],
```
`models/signal_router.py`:
```
"confidence_score": float(confidence),
```
where `confidence` is `DecisionModel._compute_confidence` = `abs(bias.score)`.

**What the code does.** Engine output's `risk.confidence_score` is unsigned trend magnitude; decision object's `risk.confidence_score` is bias magnitude. Same dotted name, different derivations, in the object the contract calls one shape at two layers.

**Clause broken.** Item 10: "The same term, score, or scale must mean the same thing in every module that uses it."

**Concrete scenario.** A reader tracing `confidence_score` from engine_core into the panel concludes confidence is trend health (95.35 on Run 1's TREND line). The panel actually prints 78.70, DecisionModel's number. Today the router overwrites unconditionally so the operator sees one value; a future consumer reading the engine layer directly (as `live_trading.py` once read raw engine output) gets the other meaning under the same name.

**Severity Minor.** Contained — final panel/log use the router's meaning — but the duplicate is live, not historical. Rename the engine-layer key or drop it; do not keep two meanings.

The comment did not move me: no comment claims these are the same; the code shows they are not.

## F3 — Item 13 / Item 8: router assembly still invents zeros on paths a healthy run never takes — Partially compliant (Item 13 Compliant on live path, non-compliant on unreachable branches) — Minor

**Location.** `models/signal_router.py`, `_build_decision_object`:
```
"zone_lower": float(entry.get("zone_lower", 0.0)),
"zone_upper": float(entry.get("zone_upper", 0.0)),
"distance_from_zone": float(entry.get("distance_from_zone", 0.0)),
"atr_stop": float(risk.get("atr_stop", 0.0)),
"targets": (float(targets[0]), ...) with (0.0,0.0,0.0) fallback,
"current_price": float(exit_data.get("current_price", 0.0))
```

**What the code does.** If a key is absent, a price/distance of `0.0` is substituted — a finite price this instrument never traded, and `0.00% away` is the strongest zone claim this line can make. On the production path the keys are always present (engine_core always sets them; NaN passes through `float()` unchanged), so this never fires today. That is why it survived: I searched unreachable branches first per 7.1.

**Clause broken.** Item 13: "never invent a confident-looking answer"; Item 8: a `0.0` price presented as a level blurs absent into measured.

**Concrete scenario.** One edit upstream — engine_core stops setting `zone_lower` on some new failure — and the panel prints `ENTRY ZONE $0.0000 - $0.0000 / 0.00% away` instead of `not located / not measured`, with no degradation, because the absence was filled here before any guard saw it. Identical shape to the `close*0.99` and `swing_struct=current_price` fabrications already removed.

**Severity Minor.** Unreachable today; one edit from live; nothing tests it in the meantime. Replace `0.0` defaults with NaN-passthrough (`_finite_or_nan`-style) consistent with `structure.hvn/lvn` handling two lines above.

I reached this by reading the assembly, not by any comment; the surrounding comments correctly describe other fields and say nothing about these defaults, which is part of why they survive.

# Part 3 — Not verifiable

- **Item 15 Empirical Evidence Supersedes Theory — Not verifiable.** What I would need: a backtest or live-measurement comparison where an elegant derivation and observed behaviour disagreed, and evidence of which won. No backtest exists yet (Item 17, correctly absent), no calibration log exists, and the two empirically-unvalidated features are honestly labelled as such. I found no violation — nothing keeps a disproven formula — but absence of a disagreement is not proof the rule is met.

No other rule needed this verdict; process rules blamed on withheld history in Rev 1 are now gradeable from `version_control_history.md` (188 commits, branches, tag `audited-2026-08-27`, per-file diffstats) plus pinned fixtures, golden snapshot and lineage.

# Part 4 — Test suite assessment

**Overall: it tests whether the engine is correct, with source-text guards that are justified regression guards rather than change-detectors.**

I ran Section 7.3's six shapes deliberately:

- *Iterate-and-assert-nothing on empty:* none found. Collection loops (`critical_indicators`, `slope_columns`) assert absence/presence per element; `test_every_declared_field_is_actually_produced` fails if nothing produced.
- *Inject failure where path never reaches:* none found. `test_degraded_state` documents the RSI-vs-ADX recoverable distinction it got wrong on first draft; `test_a_macro_processing_exception...` breaks only the first `add_technical_indicators` call (macro frame) so base processing is untouched; VWMA tests wrap `get_tf` because VWMA is inline, not via `ta.*` — the docstrings state why.
- *Assert only absence (passes if feature vanished):* checked. Every absence test I sampled has a paired presence control: deleted columns + kept columns; `compute_exit` gone + `build_exit_watch` survives; trend_failure gone + genuine exhaustion/divergence still flag; `code_hash` volatile + presence/well-formedness elsewhere.
- *Setup contradicts claim:* checked. `test_timeframe_disagreement.py` asserts the fixture really splits bias vs macro both polarities before asserting behaviour, plus an agreeing-control that must still reach LONG. `test_btc_correlation_alignment` asserts positional vs aligned answers actually differ (negative control) and that pinned fixtures are fully paired. `test_trend_direction_source` now runs the frame through `add_technical_indicators→calculate_structure` and asserts no degradation, after its own docstring admits the prior raw-OHLCV fixture could never leave NEUTRAL.
- *Return instead of skip:* the `if not _engine_available(): return` class was converted to `pytest.skip`; `run_tests.py`'s lack of skip concept is documented, and the new filter-matching tests plus `run_tests.py`'s exit-2 on zero-match close the "0 passed, exit 0" hole.
- *Fixture can no longer produce condition:* checked. RSI zero-loss synthetic frames exist precisely because the pinned fixture never holds average loss at zero; monotonic/flat expectations (100.0/50.0) match `pandas_ta`; VWMA trailing-zero-volume synthetic windows match the report's scenario.

The suite's characteristic strength is negative controls and pre-fix reproduction (counts split behavioural vs ImportError vs controls, per-file). Its characteristic risk — ~dozens of AST/text scans that pin implementation details — is mitigated because each scan pins a defended invariant (no `bfill` in decision path, no `risk_valid", True` default, denominators from constants) and exempts the deliberate exception (`utils/plotting.py` backfill, with a test that fails if the exemption becomes vacant).

Remaining weakness: the suite cannot reach states its fixtures never enter except by generation, and generation is used in only two places (timeframe disagreement, synthetic RSI/VWMA). Live-data-only states (e.g. ADX branches behind a >15% stop or EXTREME volatility, noted in history as never observed live) are covered by unit tests, not by an end-to-end run. That is honest, not a defect, but it is the boundary of what this suite proves.

Prior-reviewer's line that the suite "tests implementation details have not changed more strongly than correctness" is no longer fair on current evidence: the central lineage test rebuilds candles from the archive alone and requires the identical decision; the golden test requires identical decisions on identical inputs; perturbation tests vary one measurement at a time.

# Part 5 — Release gate

The Constitution's gate: no Critical Tier-1 finding stands unresolved, on my findings alone.

**Met.** I return no Critical Tier-1 finding. F1 is Tier-2 Moderate; F2–F3 are Minor. Run 1 (`NO-TRADE (RISK TOO HIGH)` on 15% stop) and Run 2 (`WAIT` on disagreeing timeframes, LONG label never above descending targets) are the safe behaviours Items 13–14 require.

# Part 6 — Observations outside the Constitution (my opinion, not grades)

1. **Three post-round-5 commits, reviewed from code as now stands.** A BTC-only trend failure is captured to `btc_context["degraded_inputs"]`, never appended to shared `degradation`, never read by `panel_render`; AERO confidence/gate cannot move on it while the record keeps it. The RSI fallback resolves `loss==0` to 100.0 (gain>0) / 50.0 (gain==0) after avoiding divide-by-zero, with Wilder smoothing otherwise untouched. The five test-hardening changes add the missing assertions (expected sign vs label-sign agreement; LONG in `exit.action` on agreeing rally; chart file exists and >1KB in both plotting tests; genuine-decision checks in smoke reproducibility; exit-2 on zero-match filter). On code as shipped, each claimed fix is real and none changes the pinned golden decision except the disclosed `degraded_inputs: []` schema addition.

2. **Panel shows RISK REGIME but not the ADX that now decides it.** `lineage.risk_inputs.adx` and `indicators_at_decision_bar.ADX` carry it; the operator surface does not. Same class as prior label-without-quantity observations. Consider one ADX line; no grade, Tier-4 taste.

3. **Residual coupling, honestly disclosed, not graded.** ADX reaches `bias_score` indirectly via `continuation_strength.adx_component` while also deciding the risk regime. Not the same value read twice (the Item-14 defect), but not full independence either. The constants block states this; I agree with that limit and do not ask for more before backtesting.

4. **Dead branch worth deleting.** `risk_model.calculate_stop_targets`: `effective_bias = detailed_bias; if effective_bias not in ["LONG","SHORT"]` — `detailed_bias` is only ever `BULLISH CONFIRMED/BEARISH CONFIRMED/NEUTRAL`, so the first arm never fires and the tie-break always runs. Harmless today, misleading to the next reader about what chooses direction. Tier-4 simplicity.

5. **Where I noticed relying on a comment.** Two places: the VWMA "deliberately NOT in sweep" note (false about the fill beside it — I checked the fill, not the note) and the `decision_contract` "independently of trend health" note (false until the ADX change — I checked `classify_risk_regime` signature and call sites). In both cases the comment was the map to the defect, not evidence. Claimed fixes I could not confirm from code alone: none — every fix comment I sampled has a beside-it implementation and a test that fails pre-fix.

6. **Constitution disagreement, recorded not graded.** Item 15 is the only rule I could not verify without a backtest, yet the freeze lifts only after Tier-1 findings exist. A calibration-log or kill-condition candidate would make Item 15 auditable; as written it is aspirational until backtesting exists. Future-amendment material, not a failure.

## Requested runs (Section 11)

None requested. The verdicts above rest on code paths exercised by committed tests and both transcripts; the live-unobserved ADX-branch concern is covered by unit-level behavioural tests that fail pre-fix. If the project wants one cheap run, re-run the engine on a live frame whose stop is <15% in non-extreme volatility and confirm `RISK REGIME` reacts to ADX while `bias.raw` does not — but I do not withhold any verdict for it.
