# Next step — read this first

*Updated 3 September 2026. **Every Critical the Luna Pro audit raised has a fix that has
landed, and four more patches went in on 3 September** — see "Round 2, attempt three"
below, which is the section to read first. The release gate is still shut, because
"unresolved" means no fix has landed **and been re-audited**, and the re-audit has now
failed three times without ever reaching a verdict. Suite: 226 passing, 0 failed.*

*Eleven defects found by an audit run that never produced a report, all verified against
source, four fixed. Two more found by running the engine and reading the panel — including
one introduced by a patch the same day, which every test in the suite passed because they
matched substrings and not shape.*

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

**And the gap is now closed rather than noted.** Viktor's observation, 2 September: *"I
really should have run the engine more often, but I was too caught up in the workflow."*
The better answer than resolving to be more diligent — which decays — is to make the suite
able to reach the state it could not.

`tests/test_timeframe_disagreement.py` generates a series where the two timeframes
genuinely disagree: a long rally then a sharp multi-day break, so the daily EMA-50 still
sits below the daily close while the 4h structure has decisively turned. An ordinary market
condition, not a contrivance. Deterministic and derived from a pure function — the wobble is
`sin()`, not an RNG — so the series is identical on every machine and every numpy, following
`test_golden_path._write_pinned_set`'s discipline rather than inventing a second one.

Seven tests, running the **whole** engine rather than `DecisionModel` in isolation. Four
fail against the code before `30408c2`, reproducing the live run from generated data:
CONSERVATIVE LONG over descending targets, CONSERVATIVE SHORT in the mirror, and the false
"Bias is bullish" claim. The other three must pass on both sides — two of them assert the
*fixture itself* still produces the disagreement, because if it ever stops, every other test
in the file would go on passing while testing agreement. That is section 7.3's "setup
contradicts what it claims to test", and this file is exactly the shape that fails that way.

The property pinned is deliberately not "the engine returns WAIT here" — that is today's
answer to today's thresholds, and it would fail the next time one legitimately moves. What
must never be true at any threshold is a LONG label above descending targets.

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

## Independence — what kind of exposure, and what clears it

**Ruled 2 September 2026, delegated by Viktor to Claude.** The project held two positions
on this and had not noticed they contradict.

Entry #18 resolved Grok's prior exposure by running Step 3 "in a fresh conversation with no
shared memory of the earlier one." The Remediation Plan, eleven days later, rejected Luna
Pro for Step 5 *because* it had read the Constitution during the hostile review — treating
the same kind of exposure as permanent. Entry #41 then graded Step 8 against the stricter
reading without noticing the looser one existed. Both cannot be right, and which answer you
got depended on which document you happened to open.

**Three different things were being recorded as one:**

| Kind | What it is | What clears it |
|---|---|---|
| **Session** | A model read the document in a chat | A fresh conversation with no shared memory — *provided* that conversation was not fed back into training |
| **Training** | The artifact is in the model's weights | Nothing. Ever. |
| **Lineage** | A sibling model from the same lab worked on the artifact | Nothing — this is training exposure under another name |

Entry #31's rule that "independence is tracked at the lab, not the checkpoint" was written
for the second and third. Applying it to the first is a category error, and it is why the
clean list emptied faster than it had to.

**The ruling.** Session exposure is cleared by a fresh conversation where
training-on-conversations is off. Training and lineage exposure never clear. Where it cannot
be established whether a session fed training — a consumer chat interface, unknown
retention — treat it as permanent, because a wrong guess in that direction cannot be undone.

**Consequences.**

- Viktor's "relatively OK" grade on the Luna Pro Step 8 stands, and for the right reason.
  The only thing short of fully fine is that the hostile review may have run somewhere that
  retains conversations, which is now unknowable. Probably clean, not provably.
- **Kimi K3 is available again.** Its exposure was session-level and its Step 3 attempt
  truncated before completing. It ranks fourth on the current coding leaderboards, above
  Qwen3.8-Max — and its truncated run found two material Item 14 defects that neither
  completed run did. It should be considered for round three.
- Round 2's auditor is **not** being changed. Qwen is chosen, the package is built for it,
  and re-deciding a settled question costs a day for a marginal gain.
- Audits should run **through the API rather than a chat interface**, for independence as
  well as reproducibility: an API call with training opt-out is the case where session
  exposure demonstrably clears.

### Verified against the billing log, 2 September — and the ledger was wrong

The ruling above rests on training-on-conversations being off. Rather than assume it,
Viktor exported the OpenRouter activity log: 713 requests, every model, every route. Three
things came out of it, and only the first was the question being asked.

**One — no free endpoints, ever.** Every request in the entire history shows
`variant=standard`. Combined with paid-endpoint training routing having been off already,
no Phase-7 material was ever sent to an endpoint that trains. **Kimi K3's exposure is
confirmed session-level and it remains available.** The ruling holds unchanged.

**Two — the Step 3 truncation has an exact cause.** Entry #23 records the Kimi K3 attempt
"truncating inside its own reasoning at a default token ceiling." The log names it:

```
2026-08-27 02:56:56  kimi-k3  completion=16,384  reasoning=18,668  finish=length
```

`finish=length`, at exactly 2^14 output tokens. Luna Pro later produced a 133,383-token
completion through the same interface, so the ceiling is raisable and simply was not raised
that day. **Check the max-output setting before every audit run.** It is the cheapest
possible way to waste a full input charge.

**Three — Mistral is not clean, and the Remediation Plan says it is.** Five models ran
through Aider on 22-24 August, while the engine was being built:

| model | requests |
|---|---|
| `deepseek/deepseek-chat-v3` | 315 |
| `anthropic/claude-4-sonnet` | 194 |
| `deepseek/deepseek-r1` | 96 |
| **`mistralai/mistral-nemo`** | **71** |
| `anthropic/claude-3-haiku` | 4 |

Entry #31 names three of them — "Claude Sonnet 4, DeepSeek V3 and DeepSeek R1, through
Aider" — and misses `mistral-nemo` and `claude-3-haiku`. Mistral's lineage worked on this
codebase through exactly the mechanism Entry #31 used to disqualify DeepSeek.

**Mistral comes off the clean list.** What remains: Meta, Qwen, Cohere, Amazon, MiniMax,
and Kimi K3 per the ruling above.

One thing not to over-read: *Amazon Bedrock* appears as the **provider** serving Claude
models, not as Amazon's own models being used. That is a hosting relationship, not lineage.
Amazon stays clean.

The correction matters less than how it was found. Entry #31's independence table was
written from recollection, and it was wrong for a week. **Nobody could have caught it by
thinking harder** — only by reading the billing record, which is the only account of what
actually happened. See earned rule 29.

## The round-2 re-audit — prepared 2 September 2026

**Auditor ruled: Qwen3.8-Max.** It is the highest-ranked model still clean on both
independence lists. Of the five highest-ranked coding models available, three are Claude
(which wrote this engine), one shares a lineage with Luna Pro, and one — Kimi K3 — was
spent on the Step 3 attempt that truncated. Whether Kimi should still count as spent, given
it never completed a review, is left open as an optional future call rather than ruled now.

Cost, at $2/M in and $6/M out: roughly **$0.75–0.80 per pass** on a package of about 181K
tokens. Worth budgeting for two or three attempts — this step has already failed twice, once
on a token ceiling and once on the wrong Constitution file being supplied.

### What changed in the package

`docs/build/build_audit_package.py` **generates** it now. Entry #24 records a false claim
that got into the hand-assembled Step 2a package; a script that walks the repository and
computes the manifest from the bytes it wrote cannot make that class of error. It also
refuses to build if `docs/` would ship, because intending to withhold the answers is not the
same as withholding them.

Three things Luna Pro did not get:

- **Version-control history.** Five Not-verifiable verdicts were unassessable *only* because
  history was withheld — the cheapest verdict movement on the register. Supplied as metadata
  only: hashes, dates, files changed, insertions, tags. **Subject lines are held back**, since
  "Audit Findings 6 and 7: make a run reconstructable and traceable" leaks a finding number
  and its outcome in eleven words. Full messages go in a separate Part 7 file.
- **Project files** — `requirements.txt` and the rest. Grading "are dependencies pinned"
  while withholding the file that pins them is asking a question with the answer hidden.
- **Execution transcripts.** Two deterministic offline runs, including one where the
  timeframes disagree. Labelled as claims by the party under audit, because that is what
  they are. The instruction also invites the auditor to *request* runs, which is the more
  valuable half.

### What this round honestly cannot be

Rev 1 was a blind review. **This one is not, and the instruction says so in its own section.**
The fixes shipped with comments and docstrings that describe the defects in detail —
`test_timeframe_disagreement.py` opens by narrating the CONSERVATIVE LONG run. Those files
are part of the artifact and stripping them would be the party under audit editing its own
evidence, which Rev 1 already ruled against for code comments.

So round 2 buys two things instead: **are the claimed fixes real**, and **what did neither
round find**. That is worth more than a re-discovery of findings already known — but it is a
smaller claim than "an independent audit found the same things", and the report must not be
read as the larger one.

### Pre-flight checklist — run this every time, do not do it from memory

Written after the round-2 run started with **eight tools enabled, including a shell**, which
nobody had chosen and nobody had checked. It probed an empty sandbox, found nothing and
moved on — but the repository is public, and one `git clone` would have handed the auditor
`PHASE7_NEXT.md`, the previous audit report, the Engineering Notes and every commit message.
The entire answer key, in one command.

It was caught by watching a screenshot at the right moment. That is luck, and earned rule 28
says luck is the signal to change the setup rather than to be more careful next time. This
list is that change.

**Tooling — the one that nearly cost this round**

- [ ] **All tools OFF.** Shell, web search, browsing, file access. An auditor needs to read
      what it was given and nothing else. Entry #27 records a previous run fetching the
      public repository; that was noted as a "method difference" after the fact, which is
      the polite name for finding out too late.
- [ ] File parser set to **Native** — not MistralOCR or CloudflareAI. No reason to route
      audit material through a third party, and Mistral is off the clean list.

**Model and routing**

- [ ] Model pinned, provider pinned, **fallbacks off**. A failed request tells you
      something; a silent reroute does not.
- [ ] Training-on-request-data routing **disabled**, paid *and* free. Verify afterwards in
      the billing export rather than trusting the toggle — see rule 29.
- [ ] Confirm no `:free` variant. Free endpoints are usually free because the traffic is
      kept.

**The settings that decide whether you get a report at all**

- [ ] **Max output at the model's ceiling.** Step 3 died at exactly 16,384 tokens with
      `finish=length`. This is the cheapest possible way to waste a full input charge.
- [ ] Streaming **on**. These runs take 5–20 minutes; a non-streamed request that long
      invites a gateway timeout.
- [ ] Reasoning **on**, effort high. And expect a long silence before output — one previous
      run had time-to-first-token equal to its entire generation time. Do not cancel.

**The package**

- [ ] The audit copy carries **no AUDITED, AMENDED or DEFECT row**. Verified two ways:
      extract the text and grep, then look at the Version History pages. A previous attempt
      was correctly refused because the wrong file went out.
- [ ] Upload the **whole `UPLOAD_THESE/` folder** and nothing else. Never hand-pick: two
      rounds' bundles share filenames and differ only by size.
- [ ] `commit_messages_PART7_ONLY.md` stays back until Parts 1–6 are written **and saved**.
- [ ] **No code commits while the audit runs.** The report describes the artifact at the
      commit the package was built from; changing it underneath makes the findings
      unlocatable. Documentation is safe — `docs/` is excluded from the bundle.

### Before sending

One check from Entry #42 that still has not been run: open
`Phase7_Constitution_v1.0_RATIFIED_AUDITCOPY.pdf` and confirm it carries no AUDITED, AMENDED
or DEFECT row. It is a one-minute check on whether the re-audit grades the exam or the
answer key, and a previous attempt was correctly refused for exactly this.

## Round 2, attempt three — and what an unfinished audit found, 3 September 2026

Read this section before doing anything else on this project. It is the current
state, it is written down because the conversation that produced it does not
persist, and every claim in it was verified against source rather than taken
from an auditor's word.

### The re-audit has now failed three times, and never on its own merits

| attempt | model | what happened |
|---|---|---|
| 1 | Qwen3.8-Max | repeated provider-side failures before grading began |
| 2 | Kimi K3 | received the Constitution as a PDF, could see the filename and not the contents, said so and stopped |
| 3 | Qwen3.8-Max | same defect. Its reasoning names it precisely |

Not one of the three was the reviewer's fault, and the third one refusing was
correct behaviour. The common factor across two different providers was the
PDF. The Constitution now ships to auditors as text
(`docs/audit_package/Phase7_Constitution_v1.0_RATIFIED_AUDITCOPY.txt`), a
`pdftotext -layout` extraction carrying the source PDF's SHA-256 in its own
header and verified byte-for-byte against a fresh extraction.

A fourth attempt has not been made. **The model is already chosen** — Viktor
ruled Qwen3.8-Max on 2 September and nothing since has changed it. Its two
failed attempts spent no independence: by his own 2 September ruling, session
exposure ends with the session, and a fresh conversation is clean.

### The unfinished audit did the work anyway, and found eleven real things

Attempt 3 could not read the standard, correctly refused to grade 44 rules it
had not seen, and then ran the instruction's own Section 7 checks — which are
defined in the instruction rather than the Constitution. Its reasoning is
preserved at `qwen_reasoning_1.txt` through `qwen_reasoning_4.txt` in the repo
root.

**Every one of the eleven was treated as a CLAIM and verified against source
before anything was written.** None evaporated; two got worse under checking.

| # | finding | evidence |
|---|---|---|
| 1 | `run_hash` omitted the risk multipliers | `decision_log.py:126` named only `bias_engine`; `risk_model.py:19-22` held them on the instance |
| 2 | `chart_path` printed as the string `"None"` | `signal_router.py:402` + `panel_render.py:228` |
| 3 | structure sub-routines failed silently, inventing levels | `structure.py:42-64`; `hvn = current_price` scores 12/12 at `entry_model.py:200-205` |
| 4 | entry zone fabricated as `close * 0.99 / 1.01` | `engine_core.py:618-619`, `entry_model.py:55-56` |
| 5 | RSI/ATR fallbacks use SMA where `pandas_ta` uses Wilder RMA | `indicators.py:396-397, 557` |
| 6 | two dead fabrication constants survive | `engine_core.py:472` (`50.0`), `:660` (`* 0.02`) |
| 7 | no minimum bias magnitude gates a directional action | `decision_model.py:355` reads the string only |
| a | correlation pairs AERO and BTC by position, not timestamp | `btc_context.py:34-35` discards the index |
| b | the continuation floor silently zeroes a 30% weight | `trend_health.py:232` → `bias_engine.py:177,182` |
| c | no HTTP timeout; `DataFrame` built outside the `try` | `data_fetcher.py:231`, `:245-265` |
| d | a directory is created at import | `live_trading.py:151` + `:42` |

Two more were added by running the engine rather than reading it:

- **The panel called a directional macro neutral.** `MACRO TREND: BULLISH`
  printed four lines above *"The higher timeframe is neutral."* Fixed, patch D.
- **Entry sub-scores do not sum to the printed total.** 30+23+15+15+12 = 95
  under a total of 100.00. The gap is three multipliers applied after the sum
  and then clipped, with nothing on the panel to reconcile them. Not wrong,
  unexplained. Open.

### Four patches landed, 3 September. Suite 196 → 226.

| | patch | what |
|---|---|---|
| A | `patchA_run_identity` | fourteen decision-affecting constants in `risk_model.py` moved to module level and into `FINGERPRINTED_MODULES`. `RiskModel.__init__` is gone, so no instance state can drift from what the record reports. Proven behaviour-preserving across 1,728 stop/target and 192 regime combinations — zero differences |
| B | `patchB_no_false_claims`, commit `23bd476` | `chart_path` follows the `""` convention `decision_log_path` already used; the Validation Notes default that asserted `'VWMA volume trend is pointing down.'` is gone |
| C | `patchC_no_invented_levels` | `analyze()` returns `degraded_inputs` and no handler invents a measurement. Absent levels are NaN, absent labels say UNKNOWN, and `engine_core` extends the run's degradation list with them |
| D | `patchD_macro_note` | `macro_agreement()` extracted with a fourth branch, so a neutral bias no longer produces a false claim about the macro |

**Patch A changed every `run_hash`.** That is the point of it — the identity now
covers settings it did not cover before — but a hash computed after A does not
match one computed before it on identical data. A reader comparing across that
boundary must not read the difference as a change in the market data.

### Rulings made 3 September 2026

- **Fix before auditing, then measure the auditor afterwards.** Leaving known
  defects in place to test whether the auditor finds them was considered and
  rejected — not on honesty grounds, since nothing would have been planted, but
  because the gate requires a fix to have landed *and been re-audited*. Auditing
  first guarantees a third round. The measurement is preserved instead as a
  second Part 7: the auditor grades blind, saves Parts 1–6, and only then sees
  the `qwen_reasoning_*` observations for comparison.
- **The non-Claude review an amendment requires must be of the amendment TEXT,
  not of the problem it fixes.** Gemini's review of the Constitution confirms
  the two pending problems are real, which unblocks drafting. The drafts still
  go to a non-Claude reviewer before adoption.
- **Gemini's recommendation to ban viewing the engine while a Critical is open
  is REJECTED.** Running the engine is how two of this project's defects were
  found, including one the same day. The gate restricts relying on output for a
  real trading decision; a rule that blocks running the program blocks fixing
  it.

### Awaiting a ruling — three, none urgent

1. **Should the decision reason strings keep citing trend health as directional
   support?** `decision_model.py:358` prints *"Bias is bullish with strong trend
   health (90/100)"* — and `trend_health` is an UNSIGNED magnitude, so a strong
   BEARISH trend also scores 90. It can no longer choose a side, so this is not
   the direction Critical returning; it is a question about what the engine
   implies to the operator.
2. **Should a directional action require a minimum bias magnitude?** Three
   thresholds exist — 20 for `raw_bias`, 30 for CONFIRMED, none in the decision
   model. A `bias_score` of 21 with trend health ≥ 75 and entry ≥ 70 prints
   AGGRESSIVE LONG above CONFIDENCE 21/100.
3. **Is the continuation floor intended?** `trend_health.py:232` floors
   `raw_continuation` at zero, which makes `continuation_strength` exactly 0 for
   a decelerating trend, which makes `bias_engine`'s `trend_direction` 0, which
   zeroes `signed_trend_health` — a 30% weight, silently, while the panel still
   prints TREND: BULLISH. **This ruling decides the size of the remaining work.**
   If the zeroing is intended, only a comment is wrong and it is a two-line
   change. If it is not, it alters `bias_score` on every run and is the largest
   item left.

### What is left to fix, with sizes

| | size | note |
|---|---|---|
| two dead constants (#6) | tiny | delete and comment |
| HTTP timeout, `DataFrame` inside the `try` (#c) | tiny | |
| directory created at import (#d) | small | |
| RSI/ATR smoothing (#5) | small | needs a choice: match the smoothing, or record which path ran |
| entry sub-scores vs printed total | small | panel only |
| entry-zone fabrication (#4) | medium | two files; entry scoring must handle an absent zone |
| correlation alignment (#a) | medium | changes a printed number, so the golden snapshot moves |
| continuation floor (#b) | unknown | see ruling 3 above |

Four or five patches. Three change printed numbers, so those need a golden
re-baseline and a live run before they commit.

### Before the audit can be sent — do not skip these

1. **Rebuild the package** with `docs/build/build_audit_package.py`, so the
   auditor grades current code rather than last week's.
2. **Commit everything first.** The working tree was dirty when the round-2
   package was built, which means the packaged files matched no commit.
3. **Rev 4 of the reviewer instruction.** Rev 3 describes the world as of
   2 September. Sections 4a, 5 and 12 need the four patches, the failed
   attempts, and the fix-first-then-compare ruling.
4. **Package the holdout.** The `qwen_reasoning_*` observations become a second
   Part 7 document, opened only after Parts 1–6 are written and saved.
5. **Bring the Engineering Notes current.** They stop before any of this.

**A completed audit is not an open gate.** If the report returns a Critical,
the gate stays shut and the cycle repeats. The milestone is a clean report,
not a finished one.

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
11. ✅ Patch A — the risk multipliers enter the run's identity. Finding 6's required action
    asked for "risk-model multipliers and bias weights"; only the weights were
    fingerprinted, and the multipliers could not have been, because they lived on the
    instance where `module_snapshot()` cannot see them.
12. ✅ Patch B — `chart_path` no longer stringifies `None` into a claim that a file was
    written, and the Validation Notes default that asserted a market fact is gone.
13. ✅ Patch C — the structure engine records its sub-routine failures instead of
    substituting the current price for a level it could not locate.
14. ✅ Patch D — the panel no longer calls a directional macro neutral.
15. ⬜ The remaining eight items, sized in "What is left to fix" above.
16. ⬜ Rev 4, the package rebuild, and the re-audit itself.

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
26. **A ledger that tracks conversations cannot see training data.** This project has
    recorded, for weeks, which models were shown which documents — and never recorded that
    the repository is public on GitHub, which puts the codebase in reach of anything
    trained since. That channel cannot be audited, cannot be cleared, and applies to every
    reviewer including the clean ones. Viktor's ruling, 2 September: state it in the
    reviewer's instruction and ask the reviewer to say so if it finds itself recognising
    the code rather than reading it. On a new project the same fact is a decision rather
    than a disclosure — publish and accept that no future model is provably clean, or stay
    private until the audits are done. Cheaper to choose than to discover.
27. **Name which KIND of exposure you are recording, because they have different
    remedies.** See the ruling below. The register spent models permanently for a reason
    that a fresh conversation removes, and the two rulings that disagreed about it sat in
    two documents for a week without anyone noticing they could not both be true.
28. **Where a mistake cannot be undone, change the structure rather than writing an
    instruction to be careful.** Viktor, 2 September: *"It is important to simplify the
    process as much as is reasonable."* The audit package had two files named
    `phase7_engine_source.md` — last round's and this round's — differing only by size and
    date. Uploading the stale one would have the auditor grade code that no longer exists,
    and nothing in its report would reveal it: a plausible, ordinary-looking audit of the
    wrong artifact. The first fix was a careful paragraph explaining which file to pick.
    The real fix was a folder containing only the correct seven, so "upload everything in
    here" needs no judgment at the moment judgment is most expensive.

    This pattern recurred four times in one day, which is why it is a rule rather than an
    anecdote. The package builder **refuses to build** if `docs/` would ship, instead of
    intending to exclude it. `prune()` matches whole filenames rather than trusting an age
    check not to catch something it was never meant to. The archive path is normalised at
    the point it is written rather than relying on anyone remembering that Windows spells
    separators differently. In each case the earlier version was correct and depended on
    someone staying careful; the later version cannot go wrong.

    The test for whether this rule applies: **if this goes wrong, will anything tell us?**
    A mistake that announces itself can be handled with care. One that produces a
    confident, ordinary-looking wrong answer cannot.
29. **Reconstruct the independence ledger from the billing log, not from memory.** Entry
    #31 listed the models that had worked on this codebase through Aider and named three.
    The OpenRouter activity export shows five: `mistral-nemo` and `claude-3-haiku` were
    missing, and Mistral had therefore sat on the clean list of eligible auditors for a
    week while being disqualified by the project's own rule. The error was not carelessness
    — it was writing a factual record from recollection when an authoritative one existed
    and cost nothing to export.

    Every provider bills per request, and the bill cannot be mistaken about what was called.
    Before naming any model as clean, export the log and check. This generalises past model
    independence: wherever a project keeps a record of what happened, ask whether some
    system already recorded it as a side effect of doing its own job, and prefer that.
30. **A substring assertion cannot see the shape of what it matched.** Patch C replaced a
    panel line that ended in a newline with a computed one that did not, and the panel
    printed `SWING STRUCT : $0.4700 (Lookback 8)STOP LOSS : $0.4636`. Thirteen new tests, a
    negative control, a full-suite run and a golden check all passed, because every
    assertion asked whether a substring was present and it was. Viktor found it by reading
    the output of one live run. Where the layout is part of the claim, assert on the
    structure: split the text and check the line boundaries.
31. **Write the negative control before believing the test.** Every test added on
    3 September was run against the unfixed code first. Eleven of twelve failed as intended
    on patch C; the twelfth passes in both directions on purpose and is recorded as a
    regression guard rather than counted as evidence. Where a fix introduces a function that
    did not exist, pointing the test at the old tree gives an ImportError, which proves
    nothing — reproduce the old logic and run the new assertion against that instead.
32. **Check the project's own record before raising an alarm about it.** Three times on
    3 September Claude flagged a problem that dissolved on inspection: that Gemini's audit
    counts contradicted the record (Entry #29 states exactly those numbers), that having
    Gemini read the Constitution spent independence (Entry #31 already listed it as spent),
    and that the lab-level independence rule might have been introduced without a ruling
    (Entries #18, #20 and #31 record it with precedent). Rule 1 is about not asserting
    absence. This is its mirror: do not assert a discrepancy either, when the document that
    settles it is thirty seconds away.
33. **Predict every consequence of a change, not only the interesting one.** Patch A's
    golden diff was predicted as three changes and produced four — the archive filename is
    built from `run_hash[:16]` and moved with it. Patch B was predicted to add two tests and
    added one, because two of the three new checks were assertions inside an existing test.
    Both were harmless. The point of predicting a diff is that anything unpredicted stops
    the work, and a prediction that only covers the parts worth talking about cannot do
    that.
