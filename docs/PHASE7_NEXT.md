# Next step — read this first

*Updated 2 September 2026, after Findings 6 and 7 — the last Critical. **Every Critical
the Luna Pro audit raised now has a fix that has landed.** The release gate is still shut,
because "unresolved" means no fix has landed **and been re-audited**, and the re-audit has
not run. That re-audit is now the single thing standing between this engine and its own
trading prohibition. Suite: 170 passing, 0 failed, and 99 passed / 71 skipped / 0 errors on
a machine without `pandas_ta`.*

> **The engine is under its own trading prohibition right now.** The Constitution's release
> gate, adopted 27 August: *"No output of this engine may be relied on for a real trading
> decision while any Critical Tier 1 finding stands unresolved"* — and unresolved means
> *"no fix has landed **and been re-audited**."* Running it to look at is fine. Acting on
> it is not. See "What the document set says" below.

> **Read the audit report, not this file, when you want to know what is outstanding.**
> From 31 August to 1 September this file said remediation of the five Criticals was
> complete. It was not. Finding 3 — a whole Critical — had never been entered into any
> roadmap, so it was never scheduled, never ruled on, and never noticed missing. It was
> found by reading `docs/audit_package/luna_pro_audit_report.md` end to end. This file is
> a plan derived from that report; the report is the record.

## Where things stand

```
0–15 ✅  all sixteen items' code work complete
16   ✅  Step 8 independent re-audit — RUN, by GPT-5.6 Luna Pro
     ✅  Batches 1–2: real skips + five unambiguous fixes — dba1b63
     ✅  Items 3, 11, 14: rulings made and implemented — c4dfcc7
     ✅  Item 8/13 macro degradation — 5d2cbbe
     ✅  Finding 15: dependency versions pinned — a26c545
     ✅  Finding 3: decision-bar integrity — the Critical nobody scheduled
─────────────────────────────────────────────────────────
     ←   Findings 6, 7, 9, 11, 12 + the 13/14 remainders  NEXT
         and Part 6 observations 1, 3, 4
         then: an independent re-audit, with git history supplied
```

**"The owed document batch"** has been carried in this diagram since before the audit and
appears nowhere else — not in the audit report, not in any commit. Nobody now knows what
it referred to. Treat it as stale unless Viktor recognises it.

`claude/phase7-item16-triage.md`, which this file used to say to read first, does not
exist and never did — flagged rather than blocked on when batches 1–2 shipped. This file
and `docs/audit_package/luna_pro_audit_report.md` (the full report) have carried that
weight instead; nothing has needed the missing file since.

## The short version

The engine passed 119 self-authored tests and failed an independent audit on five
Criticals, three of which were in code already fixed and certified. The auditor's summary
of the suite is worth keeping even though the defect it describes is fixed: it "tests that
selected implementation details have not changed more strongly than it tests whether the
engine is correct" — a warning about what a green suite can hide, not only about this one
mechanism.

**The 119 figure was not what it appeared, and this is now fixed.** `if not
_engine_available(): return` was a PASS under pytest, not a skip. Batch 1 converted all 46
occurrences to real `pytest.skip()` calls; on a machine without `pandas_ta` the suite now
reports 46 SKIPPED rather than 46 false PASSes, which is how the four tests that import
`core.engine_core` directly (bypassing the guard) were found to fail outright in that
scenario — reported for record, not fixed, since importing directly rather than going
through an `_engine_available()` guard is a defect in those four tests, not one Item 16
named. The suite is 136 items now (10 net new, from the Item 3 and Item 14 test files
below) and — with `pandas_ta` installed, which is the normal case on Viktor's machine — all
136 pass.

## Three rulings — made, 31 August 2026

Viktor delegated all three ("decide items 3, 11, 14 myself") rather than ruling on each
individually. What follows is the ruling and where it lives; full reasoning is in commit
`c4dfcc7` and in the code itself, everywhere tagged `ITEM <N> RE-AUDIT`.

1. **Item 3 — abnormal volume.** All-zero volume is rejected outright, at
   `data/validation.py` — there is no genuine measurement to build VWMA or any
   volume-weighted read from. An isolated extreme spike is still **accepted** at that layer
   — the original "deliberately not implemented" reasoning held: a spike is real data, and
   rejecting a run over a busy market would make the engine least available exactly when it
   matters. What changed is that a spike no longer reaches every downstream score
   unflagged — `indicators/indicators.py` now detects one (>10x the recent rolling median)
   and records it as a degradation, capping confidence rather than fabricating a
   substitute value. Ruled: reject / **degrade** / accept, per case.
2. **Item 11 — independent confirmation.** The prior "sequence item 11" pass fixed one
   instance (a direct `trend_health * 0.3` term in confidence) and left three siblings of
   the same pattern standing — structure regime and macro/volume agreement, each counted
   once inside `bias_score` and again as a confidence bonus, plus trend health leaking into
   bias_engine's own "reversal/continuation" factor a second time. All three removed rather
   than reweighted: `bias_score` is now the one place all six factors are combined, and
   `confidence` is exactly its magnitude — see `models/decision_model.py`'s
   `_compute_confidence` and `models/bias_engine.py`'s dependency-graph comment.
3. **Item 14 — AGGRESSIVE / CONSERVATIVE labels.** They survive, but AGGRESSIVE now
   requires an independent risk-regime check on top of directional conviction and entry
   quality. `risk_model.classify_risk_regime()` already computed a four-tier regime; only
   the EXTREME-RISK-or-not boolean reached `risk_valid`. It's now threaded through as its
   own field, and `decision_model.py` won't return AGGRESSIVE when the regime is HIGH
   VOLATILITY RISK or worse — the setup still trades, just as the plain LONG/SHORT it
   earned on trend health and entry quality alone.

## Finding 3 — the Critical that was never on the list

Found 2 September 2026, by reading the audit report itself rather than this file.

**What it was.** Every indicator guard in `indicators/indicators.py` asked one question:
`.isna().all()` — "did the calculation return nothing at all". That catches total failure.
It does not catch a series with 299 good values and no value at the bar the decision is
made on. And it could not: `clean_series(method="forward_fill")` had already filled that
gap with the previous bar's number before the guard ran, so `.isna().all()` was False no
matter what happened at the decision bar. A stale reading sat in the decision row,
indistinguishable from a measurement.

**How wide.** The audit named ATR and SuperTrend direction. Injecting a trailing NaN into
each indicator in turn found ATR, RSI, ADX, SuperTrend *and* both EMAs — every one, no
failure recorded, decision row equal to the previous bar. It was a property of the guard,
so the guard is now one function (`indicators.unusable_reason`) that every caller asks.
Two had no guard at all to fix: the SuperTrend *level* (only its direction was checked)
and the EMAs. The same trailing fill was also running on the raw OHLCV columns, turning a
truncated final candle into a synthetic bar repeating the previous close — defence in
depth only, since `validation.py` rejects that frame first, which is now pinned by a test.

**And the consumers.** Item 9a removed the invented constants from the producer and left
them in the readers, where two of them awarded the *maximum* score for a measurement never
taken: a missing RSI fell back to `50.0`, inside the "not extended" band, scoring 15 of
15; a missing HVN fell back to `close`, making the distance exactly zero, scoring 12 of 12.
The HVN one is byte-for-byte the defect item 3 fixed for VWMA, sitting forty lines below
that fix. `risk_model.calculate_stop_targets` accepted a NaN ATR outright — every
comparison against NaN is False — and with a structural level present returned a
completely normal-looking plan in which ATR contributed nothing.

**Ruled:** a value that was not measured at the decision bar is absent, and absent means
that indicator failed — which hands it to the degradation machinery that already caps
confidence and refuses to authorize a trade. No new policy was invented; the existing one
was applied one row over.

Fixed in `indicators/indicators.py`, `models/entry_model.py`, `models/risk_model.py`,
`core/panel_render.py`, with `tests/test_decision_bar_integrity.py` (18 tests, 14 of which
fail against the pre-fix code — the other four are controls that must pass both sides).

## Every remaining finding, checked against the code — 2 September 2026

Built by opening each location the audit quoted and looking at what is there now, not by
re-reading the report's verdicts. Three findings turned out to be already closed by work
that never named them, which is the mirror image of Finding 3 and the reason this table
exists at all. **Claude told Viktor "nine Major and Moderate findings still open" on 1
September; that number came from the report rather than the code and was wrong.**

### Major

| # | Rule | Status | Evidence |
|---|---|---|---|
| 6 | Item 5 — provenance | **OPEN** | `provenance` carries engine_version, last_candle, row_count, source. No input hash, no dataset manifest version, no fetch parameters (`limit`), no prior state, no full decision-affecting config. |
| 7 | Item 6 — lineage | **OPEN** | `decision_log.py`'s record is still `{logged_at, engine_version, config, decision}`. No walkable chain back to raw candles. |
| 8 | Item 8 — inaccurate claims | ✅ **CLOSED** | All three paths. `panel_render.py` now prints `(Lookback {config.STRUCT_LOOKBACK})`; "full size" appears nowhere in the engine; the failed-macro path degrades as of `5d2cbbe`. Batches 1–2 fixed the first two without recording that they closed a numbered finding. |
| 9 | Item 10 — `confidence_score` means two things | **OPEN** | `engine_core.py:664` still emits `"confidence_score": trend["trend_health"]` in the raw object while `signal_router.py:300` emits `float(confidence)`. Same field name, different meaning depending on which entry point you call. |
| 10 | Item 16 — unconsumed `trade_quality_current` | ✅ **CLOSED** | The field is gone from `engine_core.py` and `signal_router.py`; the only surviving mention is a comment in a test explaining its removal. |

### Moderate

| # | Rule | Status | Evidence |
|---|---|---|---|
| 11 | T2-3 — nested contracts | **OPEN** | `_validate_engine_output` still checks only that five top-level keys exist. `{"bias": {}, "trend": {}, ...}` still passes and is turned into a normal-looking decision from defaults. |
| 12 | T2-4 — explicit configuration | **OPEN** | The six `WEIGHT_*` bias weights are module constants in `bias_engine.py`; the stop/target multipliers in `risk_model.py`; `STALE_AFTER_BARS` in `validation.py`; `RAW_BIAS_THRESHOLD` alongside them. None are in `config.py` and none are in `FINGERPRINTED_CONFIG`, so two runs that differ in any of them log as the same configuration. |
| 13 | T3-3 — tests that pass without running | **MOSTLY CLOSED** | Return-based skips (batch 1), the vacuous `trade_quality_current` assertion (batch 2) and the four unguarded `engine_core` imports (`3d0b410`) are all fixed. **Remainder:** the plotting test still asserts only the absence of ERROR records, so a chart that silently omitted candles would pass. |
| 14 | T3-4 — regression surface | **PARTLY OPEN** | The macro half was rewritten with `5d2cbbe`. **Remainder:** the independently-required shape in `test_golden_path.py` still omits `provenance`, `degradation` and the decision-log path, so a re-baseline that dropped any of them would be accepted. |
| 15 | T3-8 — dependency versions | ✅ **CLOSED** | `a26c545`. |

### Part 6 — observations outside the Constitution

| # | Observation | Status |
|---|---|---|
| 1 | `PHASE7_PINNED_DATA` set but not a directory returns `None`, so a run intended as pinned silently uses the live API | **OPEN** |
| 2 | `main.py` creates a hardcoded `Logs` directory | ✅ **CLOSED** — both call sites use `config.LOG_DIR` |
| 3 | `requests.get(url, params=params)` has no timeout, so a network failure can hang indefinitely | **OPEN** |
| 4 | `_save_state` writes directly to the final path; an interrupted write leaves a truncated file that reads as "no prior run" | **OPEN** |
| 5 | `panel_render`'s `safe_float` printed `nan`/`inf` verbatim | ✅ **CLOSED** — `108cc9f` |
| 6 | Source comments contain claims about prior audits | Informational; the auditor already discounted them |

### The "Not verifiable" verdicts are cheaper than they look

Twelve rules were graded **Not verifiable** — not failed, *unassessable* — and the report
says why in each case. Several are unassessable only because the auditor was handed source
snapshots with commit messages and history deliberately withheld: version control,
controlled changes, known-good checkpoints, rollback capability, and documentation of
significant decisions. This repository has all of that. **Supplying the git history to the
next re-audit would likely move five verdicts without a line of code changing**, which
makes it the cheapest work on this page. Item 17 (backtesting isolation) and Item 15
(empirical evidence supersedes theory) genuinely need artifacts that do not exist yet.

## What the document set says — read end to end, 2 September 2026

Nine documents, read in full for the first time by this thread: the Constitution, the
Documentation & Change-Log Standard, the Engineering Notes, the Tier 0 Companion, the
Roadmap, the Remediation Plan, the Audit Execution Instructions, the Credential Security
Protocol, and both copies of the item-16 review instruction. Everything below is a
citation, not a recollection.

### The two gates, and what they actually block

**The release gate** (Constitution, adopted 27 August, after the freeze lifted): *"No
output of this engine may be relied on for a real trading decision while any Critical Tier
1 finding stands unresolved."* Unresolved is defined as *"no fix has landed and been
re-audited."* Both halves matter — everything fixed this week has landed and none of it has
been re-audited.

**The backtest gate**, same section: *"Backtesting architecture is not built until Items 2,
3, 6 and 18 are all Compliant."*

**Four Criticals block them, not three.** Viktor's ruling of 29 August raised Item 6
(Traceability) from Major to Critical — *"severity reflects consequence, not implementation
effort"* — because the panel asserts a safety action that did not occur, on every run. Item
6 is Luna Pro's Finding 7. **It is the last Critical standing and it is tomorrow's work.**

### The Constitution does not need amending, and the project already ruled so

The scope freeze lifted on 27 August, when the last Tier 1 item received a finding. That
permits amendments; it is not licence to make them. Engineering Notes #26, written the hour
it lifted: *"None of them should be adopted today. The freeze was never about whether
changes were good ideas — it was about not letting the document be revised by the same
enthusiasm that wrote it, before anything had tested it. Something has now tested it, and
the useful next act is fixing the ten Non-compliances rather than reopening the rulebook
that found them."* The Constitution says it in its own voice too: *"Lifting the freeze
permits proposing amendments. It is not a statement that the engine is sound."*

**Amendment control, in force since 27 August, for whenever that day comes:**

1. Tier 1 and Tier 2 amendments require review by a party that is **not Claude**.
2. Every amendment must state explicitly what it **weakens, broadens, removes or newly
   excepts** — not what it improves.
3. There is no "wording only" category that bypasses either of the above.

### Two amendments are owed. Neither is urgent, and one is smaller than it looks.

**Item 20 — the crash-reporter channel.** Item 20 enumerates the channels a credential must
never reach (hardcoding, version control, logs, error messages, screenshots) and does not
name process-environment capture by a crash reporter or telemetry agent. Recorded and
deliberately left unfixed because closing it means amending a Tier 1 invariant, which now
requires the non-Claude review above. The Roadmap names the practical blocker: Gemini and
Copilot both refused to ingest the Constitution PDF — a content-classification false
positive.

**But the protection already exists.** `Phase7_Credential_Security_Protocol.pdf` §6.2,
"Diagnostics Cannot Carry a Credential Out": *"Any telemetry, crash reporting, error
aggregation, or usage analytics the engine ever gains must be incapable of including
credential material — verified by inspecting what is actually transmitted, not by trusting
the library's defaults."* Tagged **"Enforces: Tier 1, Items 20 and 21."** Written the same
day as the invariant it serves. So this amendment tidies the register to match a practice
that is already written down; it does not close a live hole. The engine also holds no
credentials at all. **Unblocking it is small:** amendment control asks only for an
uninvolved model, given the current text and the proposed change, asked whether the change
weakens anything. A plain-text extract of Item 20 plus the proposed clause sidesteps the
PDF classifier that stopped Gemini and Copilot.

**The Minimum Viable Audit gate wording.** The DEFECT row records the Constitution
contradicting itself: Next Steps defines the gate as four items (2, 3, 6, 18) and the
conflict-of-interest safeguards written in the same revision describe it as three (2, 3, 6),
omitting Item 18. The audit resolved it in favour of the four-item gate — Run A was
actually executed against all four, per the Audit Execution Instructions §6 — and the
Constitution records that the correction *"is now permissible but has not been made, and
needs its own proposal and its own row."* Practice has settled it; only the text is stale.

### Correction: the adjudications were ruled on 29 August

`Phase7_Roadmap.pdf` Revision 4 is titled "All five adjudications ruled" and records every
one closed. This thread said on 2 September that four remained open, having read the
Engineering Notes and the Constitution — both of which stop before that ruling — and not
the Roadmap. The rulings:

| Question | Ruling |
|---|---|
| Item 6 severity | **CRITICAL** — severity reflects consequence, not implementation effort |
| Position sizing | **REMOVE FROM THE ENGINE** — no Constitution amendment needed |
| Item 13, halt or degrade | **DEGRADE** — record the failure, cut confidence, authorize no trade |
| Item 2 strength | **COMPLIANT, rationale amended** — sequence item 15 becomes mandatory for the backtest gate |
| Items 4 and 12 | **DISSOLVED BY REMEDIATION** — the caches were deleted at sequence item 6 |
| Item 20 amendment | **STILL OPEN** — the only one |

### The independence ledger, and a cost already paid

Engineering Notes #31 tracks which models have seen what, on the principle that
*"independence is tracked at the lab, not the checkpoint."* Nine have now seen the
Constitution. The Remediation Plan of 29 August names the families **still clean on both
lists for the Step 8 re-audit: Meta, Mistral, Qwen, Cohere, Amazon, MiniMax** — and records
in the same paragraph that **Luna Pro was considered and rejected for Step 5 "because it had
already seen the Constitution during the hostile review."**

Step 8 was then run by Luna Pro.

Its findings were real — every one was checked against source before any of it was fixed,
and Finding 3 in particular was verified by running the engine, not by trusting the report.
Nothing here argues for discarding them. What it costs is precisely what the ledger exists
to buy: **the next re-audit cannot treat agreement with this one as independent
confirmation.** Use one of the six clean families for it, and do not let a second Luna Pro
result read as corroboration of the first.

### One thing to verify that this thread could not

The item-16 instruction to Luna Pro says: *"You will be given the file
`..._RATIFIED_AUDITCOPY.pdf`. Audit against that copy and no other. If you are given, or
find, a different version of the Constitution, stop and say so — the live version has been
annotated since ratification with the outcomes of a previous audit, and grading against it
would let you read the answers before sitting the exam."*

`docs/audit_package/Phase7_Constitution_v1.0_RATIFIED_AUDITCOPY.pdf` is 69,656 bytes; the
live document is 112,290 bytes and 38 pages. The smaller size is consistent with a frozen
pre-annotation copy and gives no reason for alarm. It is worth one check anyway — open it
and confirm it has no AUDITED, AMENDED or DEFECT row — because it is a one-minute check on
the question of whether the re-audit graded the exam or the answer key, and nobody has run
it. (An earlier draft of this section compared that figure against the 101,831 bytes in the
Audit Execution Instructions and called it a mismatch. That was wrong: those instructions
describe the **Step 3** package for Kimi K3, a different audit with a different material
set. Recorded rather than deleted, per this project's practice.)

### The documentation is a week in arrears

This is the real answer to "does anything need upgrading."

- **Engineering Notes stop at entry #33, 29 August.** The rebuild, the Step 8 re-audit,
  nine commits and Finding 3 are all unrecorded in the project's standing log. Draft
  entries #34–#42 exist and are awaiting the build script.
- **Change Impact Records: none.** The Documentation & Change-Log Standard has been "in
  effect immediately" since 25 August, and its own trigger is *"anything that could
  plausibly affect what the engine outputs."* Every commit this week qualifies. The commit
  messages do the job informally; what does not exist is the *"one running, referenceable
  log"* the standard says it was written to create.
- **The Constitution's Version History has no row for Step 8 having run.** The AUDITED row
  records the Kimi K3 audit of 27 August. The re-audit that followed the whole remediation
  has no row at all.
- **Stale pointers.** The Tier 0 Companion and the Credential Security Protocol both name
  `Phase7_Engineering_Constitution_v1.0_Rev6.pdf` as their companion; the live document is
  RATIFIED, Rev 8 content.
- **The Roadmap's Revision 4 predates everything since 29 August** and still presents the
  sixteen-item sequence as pending.

### A convergence worth noticing

Roadmap section D parks machine learning with five written conditions. Condition 2 is *"a
working decision **and outcome** log with real accumulated history,"* and Engineering Notes
#32 explains why it does not exist: *"`engine_core.py:466` overwrites its state file each
run rather than accumulating. Decisions without outcomes are unlabelled examples."*

That is the same gap as Findings 6 and 7. It is also the same gap the database question of
1 September was circling. Tomorrow's work is load-bearing for three separate threads: the
release gate, the backtest gate, and whether ML ever comes off ice.

## Tomorrow — the Major and Moderate work

Agreed with Viktor, 2 September. Order is mine; the pairings are the audit's own.

1. ✅ **Findings 6 and 7 — done. The last Critical.** See the section below.
2. **Finding 9**, the `confidence_score` collision. Small and self-contained: either rename
   the raw field or make both entry points mean the same thing, then update `EngineOutput`
   and `DecisionObject` to say which.
3. **Finding 11**, nested contract validation at the router boundary. The `TypedDict`
   declarations already describe the shape; nothing enforces them at the seam.
4. **Finding 12**, centralising the weights and multipliers, then adding them to
   `FINGERPRINTED_CONFIG`. Mechanical, but it moves numbers that decide trades into a file
   whose changes are recorded — and it will want a check that the fingerprint list and the
   config actually agree, or it decays the way rule 11 warns.
5. **The 13 and 14 remainders.** Plotting-content assertions, and adding `provenance` /
   `degradation` / the log path to the independently-required shape.
6. **Part 6 observations 1, 3 and 4.** A refusal instead of a silent live fallback, a
   request timeout, and an atomic state write. Three small, unrelated, cheap.

Also owed, and cheap, once the code work lands:

7. **The documentation arrears** — Engineering Notes #34-#42 (drafted), the Constitution
   Version History row for Step 8, Change Impact Records, and the two stale Rev 6 pointers.
8. **The two amendments**, in the order their blockers clear: the MVA gate wording (settled
   in practice, needs a proposal and a row) and Item 20 (needs one uninvolved model, given a
   text extract rather than the PDF).

Not scheduled: the independent re-audit itself. It is the point of all of this, it is not
something the engine's own author can grade, and it should go to one of the six model
families still clean on both independence lists — Meta, Mistral, Qwen, Cohere, Amazon,
MiniMax — not to Luna Pro a second time.

## Found by running the engine, 2 September — a Critical the audit did not have

Viktor ran `python main.py` against live MEXC data the evening Findings 6 and 7 landed.
AEROUSDT 4h came back bearish on every measure the engine has — bearish bias, bearish
regime, bearish structure, an LH-LL sequence, strong bearish distribution, SuperTrend
freshly flipped bearish — with one dissenting reading, `MACRO TREND: BULLISH`.

It printed:

```
DECISION      : CONSERVATIVE LONG
CURRENT PRICE : $0.4725
STOP LOSS     : $0.4889      <- above price
TARGET 1      : $0.4561
TARGET 2      : $0.4397
TARGET 3      : $0.4233      <- all below price, descending
```

**A long label on a short plan.** Every number in that plan was correctly computed; the
word attached to them was not. An operator following the DECISION line would have bought
an instrument the engine had just analysed, in detail and correctly, as a short. That is
the audit's own definition of Critical.

It also printed *"Bias is bullish and the broader macro trend agrees"* four lines above its
own Validation Note saying *"The higher timeframe disagrees with this bias"* — two
contradictory claims in one panel, the first of them false.

**Two causes.** `decision_model.py` opened a direction from any of three independent
sources — `raw_bias or long_signal or macro_bias` — so the macro clause alone was enough,
and `trend_health >= 50` then passed because trend health is an *unsigned magnitude*: a
strong bearish trend scores 69. No bearish evidence anywhere in the run could block it, and
the bearish block below never ran because the bullish one returned first. Meanwhile
`risk_model.py:84` builds stop and targets from `detailed_bias` alone. Two direction
sources, never reconciled.

**Viktor's ruling, 2 September: bias is the sole direction source.** Macro keeps its
existing 10% vote inside `bias_score` and gets no second, overriding one — letting it
override the blend counts one piece of evidence twice, which is Item 11 in the module that
picks the side. `long_signal` / `short_signal` go with it for the same reason: an
entry-zone reading that can pick a side against the engine's own bias is the identical
defect under another name. They stay available in `entry` for a future ruling on whether
they should *confirm* a direction bias has already chosen; they may no longer choose one.

Two more instances surfaced while testing, neither of which anyone had seen: the mirror
case (bullish bias, bearish macro) returned `CONSERVATIVE SHORT`, and a **neutral** bias
with a long entry signal returned `AGGRESSIVE LONG` — the most confident label the engine
has, from no directional view at all.

**And a guard, because narrowing the source is not the same as checking.** The fix stops
these two modules disagreeing for the reason they disagreed that day; it cannot stop them
disagreeing for a reason nobody has thought of. `_refuse_incoherent_plan` reads direction
off the targets themselves — ascending from the stop is a long, descending is a short — and
refuses any action whose label contradicts its own levels. Deliberately a refusal and not a
relabelling: one of the two sources is wrong and nothing inside that function can tell
which, so `NO-TRADE` is the only answer available that is certainly not the wrong one.

Thirteen tests. Five fail against the committed code on behavioural assertions, six on
`AttributeError` because the guard is new, and two are controls that must pass on both
sides — a genuine bullish run still reaches a LONG, a genuine bearish one still reaches a
SHORT. A fix that stopped the engine ever taking a side would pass every other test in that
file and be worthless.

**What this says about the audit.** Luna Pro read the source and the tests and did not find
this, and neither did four earlier passes across three models. It needs bias and macro to
disagree on live data, which no pinned fixture does. Reading finds what is written;
running finds what happens. New earned rule 25.

## Findings 6 and 7 — the last Critical, and what Viktor ruled

**Viktor's ruling, 2 September 2026: hash *and* archive, pruned at ninety days.** The
Constitution says under Item 5 that the retention decision is one "the audit should force
explicitly rather than leave implicit," and this is that decision made rather than assumed.

The two halves do different jobs, and the difference is the whole design.

- **The hash detects.** It costs nothing, it lives in the decision log, and the log is
  never pruned. A decision from two years ago can still be checked against data fetched
  today, and the answer — same or different — is exactly as trustworthy as it was on the
  day.
- **The archive reconstructs.** It is the actual candles, and the only thing that can
  rebuild a run whose source has since changed. It is also the only part with a cost, which
  is why it is the only part with a limit: about 31 KB a run, so roughly 2.8 MB steady-state
  at the ninety-day cap.

Past the window a run does not become unverifiable — it becomes **verifiable but not
rebuildable**, and the record says which by whether the archive file is still there.

**What the gap actually was.** Sequence item 12 built a decision log: what the engine
concluded, plus a five-field fingerprint of what it saw. The fingerprint was a last-candle
timestamp and a row count, and two different frames can share both. Nothing stored told them
apart, so "reconstructable" was a word in the Constitution rather than a property of the
engine.

**How it is proven.** The central test does not inspect fields — a test asserting
`"lineage" in decision` would pass just as happily over a lineage section full of nulls, and
that is precisely the shape Luna Pro's assessment of this suite warned about. Instead it
takes the archive the engine wrote, rebuilds the candles from it, runs the engine again
against the rebuilt data *and nothing else*, and requires the identical decision. An archive
missing a column, truncating history, or losing a float's precision fails it.

Fifteen tests. Three fail against pre-fix code on real behavioural assertions (no lineage
section, the router dropping it, the log not carrying it); nine fail on `ImportError`
because `core/lineage.py` is new, which proves the module did not exist rather than
anything about the old engine; one is a control that passes on both sides. Worth stating
plainly rather than counting all twelve as behavioural evidence.

The golden snapshot moved exactly as predicted before the run: `lineage` added,
`provenance` gained seven keys, **and not one existing value changed**. This commit adds a
record and alters no output.

### Found while doing it, then ruled: an unwritable log directory no longer halts a run

Writing the halt-safety test surfaced a defect predating all of this. If `LOG_DIR` could
not be created — a path under a regular file, a read-only volume — the whole run died with
`Router execution failed: [Errno 20] Not a directory` and the operator got no analysis at
all. Verified against the pre-change code, so this work did not introduce it. It was left
unfixed in that commit on purpose, because fixing it there would have let the halt-safety
test pass for a reason unrelated to what it was written to prove.

**The cause was smaller than "the engine cannot log."** `route()` opened with two unguarded
`os.makedirs` calls that wrote nothing — every writer in this engine already creates its own
directory on demand inside its own error handling (`decision_log.write` returns `None`,
`_save_state` warns, `plot_engine_chart` warns, `lineage.write_archive` returns `None`).
The two calls duplicated all four and added a failure mode at the worst point in the run:
the top of `route()`, before anything had been computed, so four independently recoverable
conditions collapsed into one total failure and took the analysis with them. Same class as
sequence item 14's own `REQUIRED_DIRS` finding, which removed the list and left these two
calls standing.

**Viktor's ruling, 2 September: a run whose decision log cannot be written still authorizes
a trade.** It warns, the panel makes no claim that anything was logged, and the operator
decides. His 29 August degrade-not-halt ruling applied literally — a disk problem must
neither destroy an analysis that was computed correctly nor veto one.

**Claude recommended the opposite and was overruled**, on the grounds that Item 6 is
Critical and a trade taken on a decision that left no trace is unauditable by construction —
and that this differs from a failed *archive*, where the hash still lands in the log and
the run stays verifiable. Recorded because the difference matters to whoever audits this
next: it was decided, with the trade-off on the table, not defaulted into. The tests in
`tests/test_unwritable_log_dir.py` pin the ruling and say so in their docstrings, so a
later reader who thinks the assertion looks wrong will find the reasoning rather than
guess at it.

**The cost, stated plainly.** The one decision an operator acts on without a record is the
one an auditor would ask about first. That is the price of the ruling, and it is the
reason it is written down here rather than left to be discovered.

## Suggested order — status

1. ✅ `pytest.skip()` across the suite — batch 1, `dba1b63`.
2. ✅ The cheap and unambiguous fixes — batch 2, `dba1b63`.
3. ✅ Item 3 volume policy — `c4dfcc7`.
4. ✅ Item 11 circularity — `c4dfcc7`.
5. ✅ Item 14 — `c4dfcc7`.
6. ✅ Item 8/13 macro degradation — `5d2cbbe`. A failed macro-timeframe fetch used to
   leave `macro_bias` at its initialised `"NEUTRAL"` with nothing added to `degradation`,
   so a failed higher-timeframe read and a genuinely neutral macro trend rendered
   identically. `test_the_macro_series_is_actually_read` had documented this in its own
   docstring as "recorded rather than fixed"; that assertion was rewritten with the fix.
7. ✅ Audit Finding 15 — dependency versions pinned, `a26c545`.
8. ✅ Audit Finding 3 — decision-bar integrity. Never appeared in steps 1–6 at all; see
   the section above for why that is the most important thing on this page.
9. ✅ Audit Findings 6 and 7 — reproducibility and traceability, the last Critical. Input
   hashing, a raw-candle archive pruned at ninety days per Viktor's ruling, and the full
   Item 6 lineage chain persisted to the decision log.
10. ✅ The direction-source Critical — not from the audit, found by running the engine on
    live data. Bias is now the sole source of direction, and a plan that contradicts its
    own label is refused. See the section above.

## Not on the roadmap, worth revisiting

- **A database for decision history.** Raised by Viktor, 1 September 2026. Every run's
  reasoning currently lands in flat files — `logs/phase7_decision_log_*.jsonl` and
  `phase7_state_*.json` — which is simple and fine for a single-user, single-machine
  tool that never executes trades. That stops being enough once someone wants to query
  *across* runs — win rate by risk regime, how often the AGGRESSIVE gate in item 14
  actually fires, that kind of cross-run analytics — at which point scanning a folder
  of JSONL gets slow. No such need has come up yet, so nothing is planned; if it does,
  the natural fit is a lightweight embedded database (SQLite, not a server) as a query
  layer alongside the existing logs, not a replacement for them.

## The machine was rebuilt

Windows was reinstalled on 30 August 2026, all drives wiped. Everything of value is on
GitHub at `375334a`; nothing lived only on disk except gitignored `logs/`.

**`docs/audit_package/environment_before_reinstall.txt`** records the exact library
versions and **Python 3.12.0** that produced the original golden baseline.
`requirements.txt` and `requirements-dev.txt` now pin exact versions — audit **Finding 15,
closed 1 September 2026** — so a fresh install can no longer silently resolve a different
pandas / numpy / pandas_ta and shift indicator output. Pinned to the versions verified
identical across both environments that ran the full suite that day (sandbox, Python 3.12.3;
Viktor's machine, Python 3.12.10): `pandas==3.0.5`, `numpy==2.2.6`, `matplotlib==3.11.1`,
`pandas_ta==0.4.71b0`, `requests==2.32.5`, `colorama==0.4.6`, `pytest==9.1.1`. The baseline
has since moved twice more, deliberately, at `dba1b63` and `c4dfcc7` — each time because a
real fix changed what the engine computes, verified by predicting the diff before
re-baselining (see Working practice below). **If the golden snapshot moves and neither
commit explains it, check this file's environment note before assuming the engine broke.**

After reinstalling: Python 3.12.0 (Viktor's machine is now on 3.12.10; both have verified
identical, correct results), git, `pip install -r requirements.txt -r requirements-dev.txt`,
and re-link the Claude desktop app to `D:\phase7_engine`.

## Working practice

- **Deliver as a `.patch`, never a zip.** `git apply --check <file>.patch` first, then
  `git apply`. Write the patch and message file into the repo over the device bridge,
  stage them out with explicit paths, then delete them.
- **Restore CRLF before diffing.** The repo is CRLF; Python text-mode writes produce LF.
- **`git diff --cached` beats hand-built `diff -ruN` + sed.** Batches 1–2 built patches by
  running `diff -ruN` on two directories and rewriting the headers into `diff --git` form
  by hand. Items 3/11/14 did it by staging the changed files into a throwaway git repo
  seeded from the pre-change state and running `git diff --cached` — correct `diff --git`
  headers for free, no header rewriting to get wrong.
- **Run the suite plain BEFORE re-baselining**, and **predict the diff in advance**. Items
  13, 14 and 15 each predicted exactly what would move — nine fields, one field, nothing —
  and each was right. Items 3/11/14 did the same: bias.score down slightly (the
  health-derived term removed from continuation_strength), confidence moving independently
  (no longer penalised/bonused by the removed structure/validation terms), everything
  downstream of confidence moving with it, nothing else. That is exactly what the diff
  showed.
- **Never `device_stage_files` back into the sandbox working copy**; it overwrites edits.

## The rules, earned

1. Search exhaustively before asserting a thing is not there.
2. A grep for a key name is not a data-flow trace — follow the value to its reader.
3. A defect found once is usually a class.
4. A passing test can be hiding the finding.
5. An argument that a difference would not matter is not evidence the difference exists.
6. A declaration permitting the one illegal shape is worse than none.
7. Inject failures at a point confirmed to be on the path; after deleting a block, scan the
   function for names it defined.
8. A record of a run must not contain machine-specific paths.
9. A guard that iterates a list is silent when the list empties.
10. **Count what you claim.** Two commit messages said "ten tests" where there were nine.
11. **A list of names is a claim about the code, and it decays.**
12. **Fix the helper, not just the branch.** Item 9a cleaned every `except` block and left
    `clean_series`, which the success path ran through, still turning an all-NaN indicator
    into zeros — silencing the guards 9a had just written.
13. **Injecting one kind of failure tests one kind of failure.** Ask what else the
    dependency can do wrong.
14. **Grade a finding at its real severity, including downwards.**
15. **A test that returns is a test that passed.** Skipping must be visible in the result,
    or the suite reports green for work it never did.
16. **A guard written from a list of examples inherits the gaps in that list.** The
    hardcoded-path test searched five spellings; the surviving bug used a sixth. Match on
    structure — the parse tree, the actual value — not on enumerated text.
17. **Verification by sampling is not verification.** Claude declared the Constitution PDF
    free of audit outcomes after searching three guessed phrases and reading six of
    eighteen hits on a fourth. The outcomes were in a table using words never searched, and
    the auditor found them in its first act.
19. **The plan is not the source. Work from the audit, not from the summary of it.**
    Four of the five Criticals were remediated, verified and signed off while the fifth
    sat unread in the report the whole time. It was absent from this file, so every check
    that consulted this file agreed the work was done — including three separate passes
    that re-read *this page* looking for what was left. Nobody re-opened the report until
    2 September. A derived document cannot tell you what it never contained.
20. **A finding list is a snapshot with a date on it, and it decays in both directions.**
    Rule 19 is the plan missing what the report had. This is the other direction: on 2
    September, three of the ten Major/Moderate findings turned out to be already fixed —
    Finding 8's three broken claims, Finding 10's unconsumed field, Finding 15's version
    pins — closed by batches 1–2 and by work that never mentioned a finding number. Claude
    told Viktor "nine still open" straight from the report the day before, and that was
    wrong by three. Neither document knows the current state of the code. Only the code
    does, so the status table above cites a file and a line for every verdict in it.
21. **An independence ledger only works if it is read before the room opens.** The
    Remediation Plan of 29 August names six model families still clean for the Step 8
    re-audit and records, in the same paragraph, that Luna Pro had been rejected for Step 5
    because it had already read the Constitution during the hostile review. Step 8 was then
    run by Luna Pro. Its findings were real and were each verified against source, so this
    is not an argument for discarding them — it is a record of what was spent. The ledger
    buys exactly one thing, the ability to treat a second opinion as independent, and that
    is the thing no longer available for this round.
22. **Fixing the instance you found does not close the item; the re-audit checks the
    pattern.** Sequence item 11 removed one duplicated-evidence term (trend_health, counted
    directly and via bias_score) and the item was marked done. The independent audit found
    the same pattern — a measurement counted once as a weighted factor and again as a bonus
    layered on top of the result those factors produced — in three more places nobody had
    re-checked once the first one was fixed.
23. **A test that fails with `ImportError` proves the module is new, not that the defect
    was real.** Findings 6 and 7 shipped with twelve of thirteen tests failing against the
    pre-fix code, which reads like strong evidence and mostly is not: nine of those failures
    were `cannot import name 'lineage'`. Only three were assertions about what the old
    engine actually did. The number to quote is the behavioural one, because a reader who
    later discovers the difference will discount everything else in the same commit message.
24. **Do not fix a second defect inside the test that found it.** The halt-safety test for
    the archive step first failed because an unwritable log directory already killed the
    whole run — a real defect, and not this one. Widening the fix to cover it would have
    made the test pass for a reason unrelated to what it was written to prove, and the
    commit would have claimed a ruling nobody made. Narrow the test to the claim you can
    actually support, and record the other defect where the next reader will find it.
25. **Reading finds what is written; running finds what happens.** The direction-source
    Critical — a CONSERVATIVE LONG printed over a stop above price and three descending
    targets — survived an independent 44-rule audit and four earlier passes across three
    models, all of which read the source and the tests. It surfaced on the first live run,
    because it needs bias and macro to actually disagree and no pinned fixture makes them.
    A suite built from fixtures cannot reach a state its fixtures never enter, so running
    the thing is a distinct form of verification and not a slower version of reading it.
