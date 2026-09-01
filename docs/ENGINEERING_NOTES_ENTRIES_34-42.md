# Phase-7 Engineering Notes — draft entries #34 to #42

**Status: draft, not yet built into `Phase7_Engineering_Notes.pdf`.**

The Notes are generated from `docs/build/build_engineering_notes.py`; this file is the
content for the next nine entries plus the Document History row, written to that document's
own conventions so it can be transcribed into the build script without re-deciding anything.

The Notes' rules, applied here: entries are appended in order, never rewritten; each has a
number, a date, a short title, a status tag and a body; where something has changed or been
resolved, that becomes a *new* entry referencing the old one by number rather than an edit
to the original.

Status tags used below are the document's existing ones: `REFERENCE — FILED FOR THE RECORD`,
`OBSERVATION — FILED FOR THE RECORD`, `DECISION — ADOPTED`, `AUDIT STEP 8 — RECORDED`,
`MILESTONE — RECORDED`, `FINDINGS — FROM EXECUTION`. No new tag is introduced.

---

## #34 — The Machine Was Rebuilt, and the Baseline Survived It
**30 August 2026 — REFERENCE — FILED FOR THE RECORD**

Windows was reinstalled and all drives wiped. Everything of value was on GitHub at
`375334a`; nothing lived only on disk except gitignored `logs/`. The reason this is worth an
entry rather than a shrug is Item 5: the golden baseline is a claim about an environment,
and the environment was destroyed and rebuilt.

`docs/audit_package/environment_before_reinstall.txt` records the library versions and
Python 3.12.0 that produced the original baseline. The rebuild resolved different ones —
numpy moved from 1.26.4 to 2.2.6, pandas and pandas-ta unchanged — and the golden snapshot
did not move. That is a real result and it was checked rather than assumed. It is also the
strongest available argument for what became audit Finding 15: nothing in the repository
required those versions, and the fact that the baseline held was luck that nobody had
arranged.

Viktor's machine is now on Python 3.12.10; the remediation sandbox ran 3.12.3. Both produce
identical suite results, verified on every delivery since.

---

## #35 — Step 8: the Independent Re-Audit Runs, and Finds Five Criticals
**30 August 2026 — AUDIT STEP 8 — RECORDED**

Sequence item 16 executed. GPT-5.6 Luna Pro received the engine source, the test suite, the
frozen audit copy of the register and a written instruction
(`docs/audit_package/item16_review_instruction.md`), and returned
`docs/audit_package/luna_pro_audit_report.md` — a full 44-rule verdict table, fifteen
findings, a test-suite assessment and a release-gate determination.

**Release gate: Not met.** Five findings rated Critical:

1. Item 3 — abnormal volume reaches analysis unchecked.
2. Items 8 + 13 — a failed macro input is rendered as an ordinary neutral reading.
3. Item 13 — partially invalid indicator columns pass without degradation.
4. Item 11 — bias and confidence reuse derived evidence as if it were independent.
5. Item 14 — "AGGRESSIVE" is selected from conviction and entry quality with no independent
   risk decision.

Ten further findings at Major or Moderate, and twelve rules graded Not verifiable.

Two things about this run belong in the record rather than in a summary of it. First, its
assessment of the suite — *"it tests that selected implementation details have not changed
more strongly than it tests whether the engine is correct"* — is the sharpest single sentence
any reviewer has produced about this project, and it was aimed at a suite written four days
earlier specifically to be better than that. Second, see Entry #41: the model that produced
this report was not on the clean list the Remediation Plan had drawn up for this step.

---

## #36 — Remediation Batches 1 and 2
**31 August 2026 — MILESTONE — RECORDED** — commit `dba1b63`

Two batches, one commit.

**Batch 1 — the skip mechanism.** The suite contained 46 occurrences of `if not
_engine_available(): return`. Under pytest a return is a pass, so on a machine without
`pandas_ta` the suite reported success for work it had not done — audit Finding 13, and the
defect Entry #29's harness had been built to prevent. All 46 became real `pytest.skip()`
calls. Running the suite without `pandas_ta` then reported 46 SKIPPED instead of 46 false
passes, which is how four tests that import `core.engine_core` directly, bypassing the
guard, were found to fail outright in that environment. Recorded at the time, not fixed —
see Entry #38.

**Batch 2 — five unambiguous fixes.** The "full size" text in `decision_model.py` (Finding
8, path B); `main.py`'s bare `'Logs'` (Part 6 observation 2); `trade_quality_current` and its
vacuous assertion (Findings 10 and 13); the hardcoded `Lookback 8` on the panel, now
interpolated from `config.STRUCT_LOOKBACK` (Finding 8, path A); and `np.isfinite` in risk
validation.

None of these five named the audit finding they closed. Three whole findings were later
discovered to be already closed for exactly this reason — see Entry #40.

---

## #37 — Items 3, 11 and 14: Delegated, Ruled, Implemented
**31 August 2026 — DECISION — ADOPTED** — commit `c4dfcc7`

*"Decide items 3, 11, 14 myself."* — Viktor, delegating all three trading-judgment calls
rather than ruling on each. Recorded as a delegation because Roles & Authority assigns these
to Viktor and this is the second time he has handed a specific class of them over knowingly.

**Item 3 — abnormal volume: reject / degrade / accept, per case.** All-zero volume is
rejected at `data/validation.py` — there is no measurement to build a volume-weighted read
from. An isolated extreme spike is still accepted at that layer, because the original
"deliberately not implemented" reasoning held: a spike is real data, and rejecting a run over
a busy market makes the engine least available exactly when it matters. What changed is that
a spike no longer reaches every downstream score unflagged — `indicators.py` detects one
above 10× the recent rolling median and records it as a degradation, capping confidence
rather than substituting a value.

**Item 11 — remove the duplicated factors rather than argue for their independence.** The
prior sequence-item-11 pass had removed one duplicated term and left three siblings standing.
`bias_score` is now the one place all six weighted factors are combined and `confidence` is
exactly its magnitude; `continuation_strength` no longer carries a trend-health-derived
component; `bias_engine.py` gained an explicit dependency-graph comment, which is what the
audit's required action actually asked for.

**Item 14 — the labels survive, gated.** `classify_risk_regime()` already computed a
four-tier regime and only the EXTREME-or-not boolean escaped `validate_risk_parameters`. The
regime is now threaded through as its own contract field, and AGGRESSIVE is refused when it
is HIGH VOLATILITY RISK or worse. Direction and whether a trade is allowed at all are
untouched; this gates intensity only.

Ten net new tests. The golden snapshot moved, in exactly the four fields predicted before the
run.

---

## #38 — Three Small Items, and the Four Tests From Entry #36
**1–2 September 2026 — MILESTONE — RECORDED** — commits `5d2cbbe`, `a26c545`, `3d0b410`, `2be405f`

**Item 8/13, the macro half (`5d2cbbe`).** A failed macro-timeframe fetch left `macro_bias`
at its initialised `"NEUTRAL"` with nothing added to `degradation`, so a failed
higher-timeframe read and a genuinely flat one rendered identically. Both the
validation-failure path and the processing-exception path now record a degradation.
`test_the_macro_series_is_actually_read` had documented this in its own docstring as
*"recorded rather than fixed… a rider on sequence item 9's degrade ruling"*; that assertion
was rewritten with the fix, which is what its docstring had asked whoever fixed it to do.

**Finding 15, dependency pinning (`a26c545`).** `requirements.txt` and `requirements-dev.txt`
now pin exact versions, verified by building a fresh virtualenv from empty and confirming
`pip freeze` matched before running the suite. Closes the risk Entry #34 records the project
having survived by luck.

**The four unguarded tests (`3d0b410`).** The tests Entry #36 recorded and did not fix. Three
are entirely about `Phase7Engine` and now carry the same `_engine_available()` guard as the
rest of the suite. The fourth, `test_every_module_imports`, got a different fix: it checks all
21 engine modules for import-time defects and only three of them need `pandas_ta`, so a
blanket skip would have stopped checking the other eighteen for an unrelated reason. It now
excuses the exact "pandas_ta is missing" exception and still fails on anything else.

**Stale labels (`2be405f`).** Two golden-path tests still carried *"EXPECTED TO FAIL until
sequence item 12"* in their docstrings; item 12 had fixed both defects before the Luna Pro
audit began and both tests had been passing since. Documentation-only.

---

## #39 — Finding 3: the Critical That Was Never Scheduled
**2 September 2026 — FINDINGS — FROM EXECUTION** — commit `108cc9f`

*"A derived document cannot tell you what it never contained."*

Found by reading `luna_pro_audit_report.md` end to end rather than the roadmap written from
it. Finding 3 — Item 13, partially invalid indicator columns passing without degradation —
is one of the audit's five Criticals and had never been entered into any roadmap, so it was
never scheduled, never ruled on, and never noticed missing. From 31 August to 2 September
`PHASE7_NEXT.md` said remediation of the five Criticals was complete. Four of them were.

**The defect.** Every indicator guard asked one question, `.isna().all()` — "did the
calculation return nothing at all." That cannot catch a series with 299 good values and no
value at the bar the decision is made on, and it could not even in principle:
`clean_series(method="forward_fill")` had already filled that gap with the previous bar's
number before the guard ran.

**The class was wider than the two instances the audit named.** Injecting a trailing NaN into
each indicator in turn, before the fix: ATR, RSI, ADX, SuperTrend and both EMAs — every one
carried a stale prior-bar value into the decision row, and not one recorded a failure. Two had
no guard at all to fix: the SuperTrend *level*, and the EMAs. The same trailing fill ran on
the raw OHLCV columns, turning a truncated final candle into a synthetic bar repeating the
previous close.

**And the consumers were re-fabricating what sequence item 9a had removed.** A missing RSI
fell back to `50.0`, inside the "not extended" band, scoring the full 15 of 15 — while
`indicators.py`'s own failure text told the operator it scored 0 of 15. A missing HVN fell
back to `close`, making the distance exactly zero and scoring 12 of 12. The HVN case is
byte-for-byte the defect item 3 had fixed for VWMA six days earlier, forty lines above it.

**Ruled:** a value not measured at the decision bar is absent, and absent means that
indicator failed — which hands it to the degradation machinery that already exists. No new
policy; the existing one applied one row over.

Verified end to end: before the fix, a trailing-NaN ATR produced `degraded: False`,
`missing_inputs: []`, a full stop and three targets, and moved entry quality from 45.18 to
45.25 — a different answer, reported clean. 18 new tests, 14 of which fail against the
pre-fix code; the other four are controls that must pass on both sides. Golden snapshot did
not move, predicted in advance and for the right reason: real pinned data has zero trailing
NaNs.

**Recorded against Claude:** the first draft of that test file reintroduced the defect fixed
in `3d0b410` the same morning — five of its tests imported `indicators.indicators` with no
`_engine_available()` guard and errored instead of skipping. Caught by running the suite in a
pandas_ta-free virtualenv before packaging. Same class, same day, inside the fix for the
class.

---

## #40 — The Status Sweep, and a Count That Was Wrong by Three
**2 September 2026 — OBSERVATION — FILED FOR THE RECORD**

Claude told Viktor on 1 September that nine Major and Moderate findings remained open. That
number came from the audit report rather than from the code, and it was wrong by three.

Checked by opening each location the audit quoted: **Finding 8** (inaccurate user-facing
claims) was fully closed — `Lookback` interpolated from config and the "full size" text gone,
both in batch 2, with the macro path closed by `5d2cbbe`. **Finding 10** (unconsumed
`trade_quality_current`) was closed in batch 2. **Finding 15** was closed at `a26c545` the
previous day.

None of those three commits mentioned a finding number, which is why nobody knew they had
closed one. Entry #36 records the same omission from the other side.

Genuinely open: Findings 6, 7, 9, 11 and 12 in full, plus the remainders of 13 (the plotting
test still asserts only the absence of ERROR records) and 14 (the required-shape assertion
still omits `provenance`, `degradation` and the log path). Seven, not nine. The status table
now in `PHASE7_NEXT.md` cites a file and a line for every verdict, so the next reader can
re-check it rather than trust it.

This is the mirror image of Entry #39. That one was the plan missing what the report had;
this one is the report not knowing what had been fixed since. Neither document knows the
state of the code.

---

## #41 — The Step 8 Auditor Was Not on the Clean List
**2 September 2026 — OBSERVATION — FILED FOR THE RECORD**

`Phase7_Remediation_Plan.pdf`, 29 August, records: *"Luna Pro was considered and rejected for
this step because it had already seen the Constitution during the hostile review. Still clean
on both lists for the Step 8 re-audit: Meta, Mistral, Qwen, Cohere, Amazon, MiniMax."*

Step 8 was run by Luna Pro the following day.

Entry #31 sets out why the ledger exists: *"independence is tracked at the lab, not the
checkpoint"* — and Entries #18 and #20 record Grok being removed from the auditor plan for
precisely this reason, having read the Constitution in an earlier conversation. The same
disqualifier applied here and the ledger was not consulted.

**What this does not mean.** The findings are sound. Every one was checked against source
before any of it was fixed, and Finding 3 was verified by running the engine rather than by
trusting the report. Nothing here argues for discarding the report or redoing the work it
produced.

**What it costs** is the single thing the ledger buys: the next re-audit cannot treat
agreement with this one as independent corroboration, because it would be the second reading
by a model that had already read the standard. The next re-audit should go to one of the six
families named above, and its agreement with Luna Pro should be read as agreement between two
readings, one of them contaminated — not as confirmation.

Recorded rather than quietly noted, per Entry #21's reasoning: the party that made the error
should not be the party that decides the evidence of it disappears.

---

## #42 — The Document Set Read End to End
**2 September 2026 — REFERENCE — FILED FOR THE RECORD**

Viktor asked whether the Constitution needed upgrading. Answering it honestly required
reading all nine governing documents rather than sampling them — Entry #17's lesson, and rule
17 of `PHASE7_NEXT.md`'s list, which exists because Claude once declared this exact PDF clean
after searching four guessed phrases.

**The answer is no, and the project had already ruled so.** Entry #26, written the hour the
freeze lifted: *"the useful next act is fixing the ten Non-compliances rather than reopening
the rulebook that found them."*

**Four things the read surfaced that were not in any working document:**

1. **The release gate is in force and blocks on Item 6.** Viktor's 29 August ruling raised
   Traceability from Major to Critical; Item 6 is the audit's Finding 7, still open. Until it
   lands and is re-audited, no output may be relied on for a real trading decision, and the
   backtest architecture is not built. Nothing in `PHASE7_NEXT.md` had said so.

2. **The adjudications were ruled on 29 August**, in Roadmap Revision 4. Claude reported four
   still open, having read the Engineering Notes and the Constitution — both of which stop
   before that ruling — and not the Roadmap. Only the Item 20 amendment remains open.

3. **Item 20's gap is already served operationally.** `Phase7_Credential_Security_Protocol.pdf`
   §6.2 covers telemetry, crash reporting, error aggregation and usage analytics, and is
   tagged "Enforces: Tier 1, Items 20 and 21" — written the same day as the invariant whose
   channel list omits it. The pending amendment tidies the register to match a practice that
   exists; it does not close a live hole. Unblocking it needs one uninvolved model given a
   text extract, not the PDF that Gemini and Copilot's classifiers refused.

4. **The documentation is a week in arrears** — this log stopping at #33 being the largest
   part of it, alongside no Change Impact Records since the standard took effect on 25 August,
   no Version History row for Step 8, and two companion documents still pointing at Rev 6.

**One check nobody has run.** The item-16 instruction requires the re-audit to grade against
the frozen audit copy, *"not the live version… annotated since ratification with the outcomes
of a previous audit."* `docs/audit_package/Phase7_Constitution_v1.0_RATIFIED_AUDITCOPY.pdf` is
69,656 bytes against the live document's 112,290; the smaller size is consistent with a frozen
copy and there is no reason for alarm. It is still worth opening once to confirm it carries no
AUDITED, AMENDED or DEFECT row, because it is a one-minute check on whether the re-audit
graded the exam or the answer key.

*(An earlier draft of this entry compared that byte count against the 101,831 recorded in
`Phase7_Audit_Execution_Instructions.pdf` and called it a mismatch. That was wrong — those
instructions describe the Step 3 package for Kimi K3, a different audit with a different
material set. Corrected here rather than deleted.)*

---

## Document History — new row

| Version | Date | Notes |
|---|---|---|
| v1.17 | 2 September 2026 | Entries #34 through #42 added, covering the six days between the audit closing and this entry — a period this log had not recorded at all. #34 the machine rebuild and the baseline surviving it; #35 Step 8, the independent re-audit, five Criticals, release gate not met; #36 remediation batches 1 and 2; #37 items 3, 11 and 14 delegated and ruled; #38 the macro degradation, dependency pinning, the four unguarded tests and the stale labels; #39 Finding 3, a Critical that had never been scheduled, found by reading the audit report rather than the roadmap; #40 the status sweep, three findings already closed and a count wrong by three; #41 the Step 8 auditor not being on the clean list, recorded rather than quietly noted; #42 the full document read, four corrections to the working record. Register unchanged at 21 / 7 / 10 / 6, no longer frozen. Two amendments owed, neither adopted. |

---

## Note on building this

The Notes are generated from `docs/build/build_engineering_notes.py`. This file is content,
not a build. To produce the PDF, the nine entries above need transcribing into that script's
entry structure with their status tags, and the Document History row appending.

Send that script and it can be done directly, with the same patch-and-verify flow as the code
changes: build the PDF, diff the page count and the entry numbering, and check the rendered
output before it replaces the current file.
