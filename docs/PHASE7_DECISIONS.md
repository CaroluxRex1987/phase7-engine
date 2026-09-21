# Phase-7 — standing decisions and governing material

*Created 18 September 2026, by mechanical split of docs/PHASE7_NEXT.md (see that
file's own head block and this patch's commit message for the reconciliation proof).
Everything in this file is verbatim content moved from docs/PHASE7_NEXT.md, except
one new subsection explicitly marked as new where it appears below. This is where
standing rules, ratified specifications and rulings that remain in force live.
docs/PHASE7_NEXT.md is the entry point for current state; docs/PHASE7_HISTORY.md is
the dated narrative record of how the project got here. Read this file when a rule or
a ruling is actually in question, not as routine orientation.*

---

## Two goals, and the order they finish in — 3 September 2026

This engine now has two purposes, and they end at different times. Recorded here
because treating them as one is the single most likely way this project fails to
finish.

**Goal A — portfolio-ready.** Phase 7 is the major technical portfolio project in
Viktor's 2026–2028 career plan, and the intended *examensarbete* if he takes a YH
programme. What it has to demonstrate is independent technical work, architecture,
testing, debugging, iterative development and structured decision-making. **It does
not have to make money.** The career plan never mentions profitability. A validation
that comes back negative is a result rather than a failure, provided the evidence is
shown.

**Goal B — a finished engine.** Backtesting, a fixed evaluation dataset, known-good
checkpoints, and empirical validation of the features currently declared
correctness-validated and empirically unvalidated. Months of work, and the last of
those is open-ended by nature.

B contains A, so they do not conflict. What conflicts is their **dates**: treated as
one goal, A's completion silently becomes B's. That is the drift the career plan
warns about in its own words — *"Do not keep endlessly redesigning it simply because
another interesting technical rabbit hole appears. The project needs an ending."*

### Portfolio-ready — the milestone and its criteria

Reached when all of these are true:

1. **The release gate is open.** Every Critical fixed *and* re-audited, with a report
   that says so.
2. **The remaining findings are closed or accepted.** Anything not fixed is recorded
   as a limitation with the reason, not left silent.
3. **The Engineering Notes are current**, with no undocumented gap.
4. **The portfolio document exists** — the fourteen sections the career plan
   specifies: objective, problem definition, architecture, data sources, modules,
   decision logic, testing methodology, debugging process, major problems, solutions,
   results, limitations, lessons learned, future development.
5. **The AI-attribution section is written.** What Viktor designed, decided, tested
   and ruled on, versus what Claude produced. The raw material already exists and is
   unusually strong — every ruling in the Engineering Notes is attributed and dated,
   the commit messages record where Claude was overruled, and this file names the
   calls that were his. It has never been assembled into one place.
6. **The suite passes and the golden snapshot is current.**

Then **tag the commit** — suggested name `portfolio-v1`.

### Why the tag matters, and why B waits behind it

Backtesting destroyed the previous build of this engine. That is the recorded reason
the Constitution gates it, and it is not a hypothetical risk. Pursuing goal B before
goal A is banked exposes the thing Viktor intends to submit to the one failure this
project has already suffered once.

With the tag in place, B can break whatever it likes. The submission is a fixed
point.

### Declared — 15 September 2026

**The release gate is open. The project is portfolio-ready.** Viktor's ruling, given
the six criteria's status as of this date, after writing his own position first and
having it checked rather than handed to him:

1. **Release gate.** Round 5 (GPT-6 Astra) found three Criticals (F1/F2/F3), all fixed
   and landed. Round 6 (Meta Muse Spark 1.3 — independent of round 5's model) re-audited
   those three plus the three post-round-5 fix commits (`2387717`, `88e47e9`, `044b055`)
   and found no Critical Tier-1 defect — the Constitution's own bar ("no fix has landed
   and been re-audited"). Named plainly: round 6's scope was the touched files and fix
   commits, not a fresh whole-codebase audit the way round 5 was — the first time this
   project has closed a Critical this way rather than having the fix incidentally survive
   the next full audit round. The Constitution's text doesn't specify scope, so this
   satisfies the letter; it is a new pattern, not a repeat of an old one. The stronger
   reason to trust it isn't "nothing raised a flag" but a checked one: all three fix
   commits' full suite runs (466 passed, golden snapshot and `code_hash` confirmed as
   predicted) came back clean, individually and combined, on a suite that — as of
   `044b055`, confirmed the same day as this ruling — can no longer pass vacuously around
   the functions these commits touch. Against this project's own confidence_score
   precedent (a rename that broke fourteen modules undetected through the suite), that
   distinction is what the ruling actually rests on, not an absence of suspicion.
2. **Remaining findings.** Fully closed. Round 6's own F1-F5 fixed and self-verified
   (fourteenth patch), the bonus duplicate-`@staticmethod` fixed (`a70fc1b`, fifteenth
   patch), and — confirmed only today, correcting an earlier false alarm in this file's
   own chat-side reporting — the five round-6 mutant-escape findings from requested-run 6
   were already closed at `044b055` (twelfth patch). Nothing is on record as open and
   unruled.
3. **Engineering Notes** — current as of `293f310`.
4. **Portfolio document** — exists (`69f1972`), fourteen pages, within any plausible
   exam-paper page limit.
5. **AI-attribution** — exists (`eee218e`).
6. **Suite and golden snapshot** — current, confirmed on every commit since.

Viktor's own words: "the targeted re-audit in Round 6 satisfies the literal
requirement... unless there is a specific technical reason to suspect the fix broke an
unrelated part of the engine, holding this release to a higher standard than every
previous one isn't warranted." No such technical reason was found. All six criteria are
green. Tag `portfolio-v1` follows as its own commit, pointing at this one.

### One consequence for the career plan

Section 10 of the roadmap lists "Finish Phase 7" as a single late-2026 objective,
while its guiding principle says to apply for jobs while learning rather than waiting
for a CV to become complete. Those pull against each other for as long as "finish"
means goal B.

Once portfolio-ready is a named milestone with its own date, job applications start
there — months before B is done, which is what the guiding principle asks for.

## Goal B — the backtesting phase, specified before it starts (15 September 2026)

Written the same way portfolio-ready was: Viktor wrote his own position on each
governance question first, Claude critiqued it, and the corrections were folded in
before anything was locked. Ratified 15 September 2026. Two of Claude's own errors
during that process are recorded at the end of this section rather than quietly
dropped, per this project's own rule.

Backtesting destroyed the previous build. `portfolio-v1` is tagged, so goal B can now
break whatever it likes without endangering what Viktor submits — that is the tag
working as designed. This section is what keeps the breakage recoverable and the
eventual answer trustworthy.

### What goal B is actually for

**Trustworthy truth, not a favourable number.** Every rule below exists to guarantee
Viktor learns what this engine really does. None of it makes the engine better at
predicting anything, and it should not be read as a promise about the result. There is
a substantial chance the honest verdict is that this does not beat buy-and-hold — most
rule-based technical systems do not. That outcome is a result, not a failure, and goal
A's own wording already says so. The value of everything below is that a negative
verdict will be a *trustworthy* negative rather than an ambiguous one.

### Preconditions, in order

The order is deliberate: cheapest information first.

0. **Timing benchmark.** Time 100 decision points against the existing pinned fixtures
   before building anything else. The engine makes one decision per 450-row frame across
   three series; a multi-year 4h backtest is on the order of 5,000–10,000 full runs, each
   recomputing every indicator. Whether that is minutes or hours dictates whether
   walk-forward is affordable and how many variants can realistically be tested. It
   shapes every decision after it and costs almost nothing.
1. **Fix `PHASE7_PINNED_DATA`'s silent live fallback.** `data/data_fetcher.py`'s
   `pinned_source()` returns `None` when the environment variable is set but does not
   resolve to a directory, and `None` means the live API. `set_pinned_source()` raises on
   a bad path; the environment-variable route does not. A mistyped dataset path in a
   backtest would not fail — it would quietly fetch live data from MEXC and produce
   plausible-looking results. This is the open observation already on this file's own
   findings table, and it is a precondition of goal B rather than a nice-to-have.
2. **Time cursor with open-time truncation, and its negative control.** A wrapper on the
   existing `_load_pinned` path rather than a new data pipeline: `_load_pinned` already
   serves `df.iloc[-limit:]`, so a backtest needs "the file truncated at `t`, then the
   existing tail logic" — and the existing loading, validation and error paths then apply
   unchanged, for all three series at once.

   **The truncation rule is the single highest-risk line in goal B.** Each series is
   truncated by candle **open time strictly before `t`**, never by close time. At a 4h
   decision point mid-day the current daily candle has not closed; handing the engine the
   completed daily bar leaks the rest of that day into every decision, invisibly, with
   clean hashes, passing every other check in this section.

   Negative control, because an assertion proves only that the guard did not fire:
   re-run sampled decision points with all bars after `t` replaced by random noise, across
   **at least three different seeds**, asserting byte-identical decisions on every one. A
   single noise draw can coincidentally land on the same side of a threshold.
3. **Item 17 write guard.** Backtest mode requires an explicit flag; writes to live log
   directories, chart directories, or the cross-run state file raise and halt. This shares
   `fc35a2f`'s *intent* but not its mechanism: that commit redirects `config.LOG_DIR` and
   `config.CHART_DIR` via `tests/conftest.py` at import time, keyed to a pytest run, which
   never fires for a user-invoked backtest. The guard is new work — assertions at the
   write points. The cross-run state file is a third artifact class alongside logs and
   charts: a backtest reading live state is contaminated, and writing it corrupts.
4. **`cut_checkpoint.py`.** Runs the checkpoint criteria, refuses to tag on failure,
   writes the manifest.
5. **Dataset build**, with its own provenance record.
6. **Run it, and record the verdict.**

### Known-good checkpoint

**Criteria**

- All three configurations green: pytest with `pandas_ta`, pytest without it, and
  `run_tests.py` at 0 failures with exactly the recorded fixture-error set **matched by
  test name**, not by count. That baseline moves only via a commit that explicitly
  predicts and records the new fixture-taking tests — the same escape hatch the golden
  snapshot already has. Without it, the first legitimate new fixture test during goal B
  would invalidate every checkpoint after it.
- Golden snapshot matches exactly, or carries a documented intentional shift predicted
  before the run. Unintended drift is a hard failure.
- `code_hash` verified, and `session_handover_check.py` clean on items 1, 3 and 4 —
  item 2 once its routine-noise filter is extended to cover the permanent
  `docs/audit_package/round*` and `logs/` entries. Until that filter is extended, item 2
  flags those on every run and the script's own summary never reads clean.
- **Cut only by script.** A ruleset run by remembering to run three commands and compare
  32 error names by eye is an instruction, not a structural fact of the repo — the shape
  this project has already replaced twice (`session_handover_check.py`, and the
  `.gitignore` fix for the `git add -A` trap).

**Tagging and cadence**

- Only tagged commits count as formal checkpoints. Cadence is driven by code change —
  cut a tag whenever backtesting-touching code is committed and all three configurations
  pass — not by session or calendar boundaries.
- The tag records the `data_manifest.json` hash and the result scored against it, so
  "which checkpoint last actually worked" is answerable without cross-referencing
  separate logs by hand. A checkpoint that certifies only code state leaves that question
  open.

**Rollback**

- Primitive: `git read-tree --reset -u <tag>`, then commit. **Not** `git checkout <tag>
  -- .`, which does not delete files added since the tag — verified empirically against a
  throwaway repo, not assumed: the added file survived and the resulting diff against the
  tag was non-empty.
- No `git revert` chains. Reverting a span of commits is not guaranteed to reproduce the
  target tree, and destroying history would violate the decision-log and audit-trail
  invariants anyway. The tree-match commit preserves full history and guarantees identity.
- Valid only if `git diff <checkpoint-tag> HEAD` is empty **and** `code_hash` matches the
  value recorded in the checkpoint manifest. Compute it; do not infer it from the diff.
- Gitignored artifacts — `logs/`, the cross-run state file, `/backtest/` outputs — are
  archived and labelled per recorded protocol during a rollback, never silently orphaned.
  An artifact on disk with no record of which code produced it is an Item 6 problem.

### The fixed evaluation dataset

- **Three series, not one file.** `AEROUSDT_4h` (base), `AEROUSDT_1d` (macro) and
  `BTCUSDT_4h` (context) — the three series `data/data_fetcher.py`'s own docstring records
  the engine fetching every run. Pinned CSVs in the existing `{SYMBOL}_{TIMEFRAME}.csv`
  shape, so the already-tested pinned path is reused rather than extended to a new format.
- Fixed multi-regime historical range — bull, bear, chop — never a rolling relative
  window. **Regime boundaries are set independently of the engine's own indicators**
  (external criteria, not `classify_risk_regime` or its ADX thresholds), and are locked
  into `data_manifest.json` at dataset creation and never adjusted once results exist.
  Boundaries that can move after a result is visible are a knob that sets the verdict.
- Integrity: SHA256 recorded in `data_manifest.json`; any divergence halts execution
  before any simulation runs. Data quality — monotonic timestamps, no duplicates, expected
  bar count, no non-finite or non-positive prices — verified through
  `data/validation.py::validate_ohlcv`, already wired into `load_csv` via
  `.attrs["validation_error"]`, rather than a new mechanism.
- The dataset build itself carries a provenance record: which endpoint, fetched when, what
  range, what was done about gaps. The dataset the engine will be judged on gets the same
  treatment as a live run.
- IS/OOS split is **chronological**, explicitly — never random. In-sample metrics are
  documented for tuning provenance; the verdict comes from out-of-sample only.
- **Scope honesty, to be carried into any document quoting the result:** this evaluates
  one pair with BTC context over these windows. It is not evidence that the engine
  generalises across coins, and nothing downstream may present it as such.

### Lookahead — what already exists, and what does not

The indicator layer is already swept and tested, and this was already true before goal B
was scoped. `793e863` (30 August, "Sequence item 15: Item 2, no look-ahead bias") graded
nine `.bfill()` calls and fixed the same defect shape in VWMA's `.fillna(close_prices)`,
`volume_profile`'s `.fillna(0)`, the EMA slopes and `structure.py`'s OHLCV fill.
`tests/test_no_lookahead.py` (11 tests) pins the result, including one test that the
chart renderer is the only permitted exception and another that the exemption still
means something.

What does not exist is harness-level protection. The existing tests cover indicator
functions operating on the current single-decision architecture — a fixed frame whose
last bar is the decision point. Walking the decision timestamp across history is a new
execution mode with no code today, and the open-time truncation rule plus its negative
control (precondition 2) is what covers it.

### Methodology

- **Primary metric: annualised Sharpe ratio, 0% risk-free rate, out-of-sample only.**
  Chosen in advance rather than left as "Sharpe/Sortino" — a slash permits reporting
  whichever looks better once both are visible, which is not pre-registration. Sortino,
  maximum drawdown, win rate, total return and time-in-market are reported as secondary
  context.
- **Benchmark: buy-and-hold over identical windows, reported in aggregate and per
  regime.** A strategy that trails across the full range but beats the benchmark in the
  bear window is a real result that a single aggregate comparison would flatten.
- **NO-TRADE states and degraded runs count as flat**, never omitted from the statistics.
  Omitting them would report only the runs where the data happened to be clean.
- **Deterministic verification only — no external audit round.** The checks are
  `cut_checkpoint.py`'s suite/snapshot/`code_hash` verification, the `data_manifest.json`
  checksum gate, the open-time truncation assertion with its multi-seed negative control,
  and metrics computed by the pre-registered formulas and emitted alongside the exact
  commit tag and dataset hash.

  **What that decision weakens, stated per this project's own amendment rule:** the
  deterministic checks confirm the data was pinned, the pipeline ran, `code_hash` held,
  and no lookahead was detectable. Nothing outside the project checks whether the
  methodology itself is sound. A script cannot tell you the benchmark was the wrong
  benchmark. This is a deliberate departure from the standing practice of reserving an
  independent reviewer for the moment independence matters most, taken because hashes and
  arithmetic are precisely the class of claim a script checks better than a reviewer does.

### The verdict — pre-registered, before any result exists

Evaluated strictly top to bottom on out-of-sample data. First match wins. The procedure
is exhaustive by construction, so no judgment call is left at the finish line — which is
the one moment in this project where Viktor's own judgment is least independent, having
spent months earning the number he would be grading.

1. **Step 0 — sample size.** OOS trades < 30 → **INCONCLUSIVE.** This gate measures
   whether the strategy acted enough to be judged at all; Sharpe is computed on bar
   returns, so it is not a statistical-power test of the Sharpe estimate.
2. **Step 1 — positive.** Sharpe delta ≥ **+0.30** *and* strategy maximum drawdown ≤
   benchmark maximum drawdown → **POSITIVE.**
3. **Step 2 — negative.** Sharpe delta ≤ **−0.30** *and* strategy maximum drawdown ≥
   benchmark maximum drawdown → **NEGATIVE.**
4. **Step 3 — catch-all.** Everything else → **NEUTRAL.**

Deltas are **absolute differences in Sharpe units**, never relative percentages: a
multiplicative rule inverts when the benchmark Sharpe is negative, which is entirely
plausible in a bear window, and would then require performing *worse* to "exceed by 15%."

The band is symmetric by design. An earlier draft required a large Sharpe gain for
POSITIVE but triggered NEGATIVE on any loss at all, which would have branded a strategy
statistically indistinguishable from the benchmark as negative. The drawdown clauses are
guards against "better returns bought with more risk" and "worse returns with no safety
benefit" respectively — not a second primary metric, which is why POSITIVE requires only
that drawdown is not worse rather than a substantial improvement.

**Every verdict is recorded with absolute OOS total return and time-in-market on the
same line.** Two traps this closes. If both strategy and benchmark lose money, a strategy
that merely lost less grades POSITIVE — correct relative to the benchmark, and
catastrophically misleading if that word reaches the portfolio document without the
absolute figure beside it. And Sharpe structurally favours sitting in cash: a strategy in
the market a tenth of the time can post an attractive ratio on trivial returns. Printing
the numbers solves both without adding a judgment rule.

### Completion boundary

Goal B is complete when the engine executes a fully isolated, lookahead-free backtest
over the pinned dataset, produces a deterministic verification report against the
buy-and-hold benchmark, and records the verdict — POSITIVE, NEUTRAL, NEGATIVE or
INCONCLUSIVE — together with run hashes, OOS metrics, absolute return and time-in-market,
directly into this file as the phase closing log.

The boundary is outcome-shaped rather than effort-shaped, and it accepts a negative
verdict as completion. That is what prevents goal B becoming the forever-project the
career plan's own words warn about: *"Do not keep endlessly redesigning it simply because
another interesting technical rabbit hole appears. The project needs an ending."*

**The re-run clause.** The first out-of-sample evaluation is the verdict of record.
Pre-registration only works once: tuning after seeing the OOS result and re-running
against the same window converts that window into in-sample data and destroys the thing
all of the above was built to protect. Any later re-run after changes is a **new phase**,
with its own pre-registration written before it runs, and the original verdict stays on
the record unaltered — the same append-only discipline the Engineering Notes already use,
where a later entry records the correction and the original stands.

### Two errors made while writing this section

Recorded rather than quietly corrected, per this file's own standing rule, and both the
same shape: a claim asserted from this document's narrative instead of from the code.

- Claude told Viktor no deliberate sweep for lookahead-bias defects had ever been run,
  quoting this file's own words about the 6 September `pct_slope` finding. Checking git
  found `793e863` — a dedicated, thorough sweep from 30 August, with `tests/test_no_lookahead.py`
  already pinning the result. The sweep Claude said was a missing precondition had been
  done six weeks earlier. This is rule 19's failure shape again, and Entry #123 of the
  Engineering Notes — which Claude had helped write earlier the same session — exists to
  warn about exactly it.
- Claude described `fc35a2f` as a reusable precedent that would cover "most of" the Item
  17 guard, without reading it. Reading it found a path redirect performed in
  `tests/conftest.py` at import time and keyed to a pytest run — not a runtime assertion,
  and not reachable from a user-invoked backtest. The guard is new work.

Both were caught only because Viktor asked for a critical review rather than because
Claude noticed. Standing mitigation adopted for goal B: **every claim Claude makes about
the codebase's state says whether it came from reading the code or from a document.**



### Course correction — the engine review, before any Goal B work (18 September 2026, recording a 15 September decision)

Not written into this file until this patch. Decided in conversation at the close of
the 15 September session that specified and ratified this section, above — preserved
by Viktor as a written handover between sessions and recorded here now so the
reasoning survives in the repository rather than only in that conversation, per this
project's own standing rule that a conversation is not a record.

**What changed.** Before any Goal B implementation, the engine itself gets reviewed
for logical soundness — is the decision logic coherent, are the constants justified,
are the signals actually independent, and is the engine's thesis written down
anywhere at all. Everything specified above, and every precondition below, stands
fully ratified. Nothing here is cancelled; it is deferred.

**Why.** Six audit rounds (see docs/PHASE7_HISTORY.md) have checked whether this
engine is honestly built — traceability, fail-safety, explicit configuration,
epistemic honesty, no-lookahead, decision-log integrity. Not one has checked whether
it is analytically sound. Different questions; only one has ever been answered. A
backtest cannot answer the other one either — it grades a decision process against
outcomes, it does not verify that the process's own inputs are non-redundant or that
its constants are more than convenient. Named specifically as things a backtest
structurally cannot surface: whether the thesis is written down anywhere as a claim
("this engine believes X about how these markets behave, therefore it measures Y and
weights it Z"); internal contradictions where two code paths mean different things by
the same concept (this project's own documented history — see "confidence_score" in
docs/PHASE7_HISTORY.md); constants chosen once and never revisited, since
backtesting an arbitrary threshold tests the threshold rather than the idea; dead or
unreachable paths; and signals that look independent but share a hidden common input.

**What is NOT deferred.** Of everything this section's preconditions require, only
the `PHASE7_PINNED_DATA` fix is urgent on its own merits — see "Open items" in
docs/PHASE7_NEXT.md. The Item 17 write guard and `cut_checkpoint.py` both exist to
survive heavy backtest iteration and can wait while backtesting waits.

**Scope conditions for the review itself, agreed the same day, not yet acted on.**
The review needs its own completion boundary, written before it starts — "review the
whole engine" is unbounded by construction, the same reasoning that gave this Goal B
section its own completion boundary above. And a boundary on what kind of claim it
can settle: internal coherence is reviewable rigorously; whether the market thesis is
actually correct is not something a review, or an AI, can establish. Only data can —
which is what this Goal B section is for, once it resumes.

**The pace ruling made alongside this one.** Viktor judged, on his own, that the
project's pace over the prior 22 days (226 commits, active on 20 of them) had become
hasty, and ruled to slow down considerably before doing any of the above. A session
resuming this project does not open by proposing work from docs/PHASE7_NEXT.md's open
items as a queue to clear; it asks what Viktor wants to do first.

### First engine-review finding, fixed — bias-weight independence (19 September 2026)

Ahead of the review above being scoped (still not acted on), Viktor asked Claude directly
whether the six bias weights are defensible and told it to write its own position first,
per the project's working-relationship default (Claude proposes and reasons, Viktor
reviews and decides), rather than treating the question as something to hand back for
scoping.

**The finding.** Two of the six factors bias_engine.py combines share a raw input, not
just a correlated one. `trend_health` (WEIGHT_TREND_HEALTH=0.30) and
`reversal_continuation` (WEIGHT_REVERSAL_CONTINUATION=0.10) both read the same `adx_val`
from `indicators/trend_health.py` and score it on two different monotonic curves — 40% of
the blend leaning on one shared reading dressed as two independent votes. Not Item 11's
defect (a reused computed VALUE); this is a reused raw INPUT reaching bias_score through
two different formulas, which is why it passed Item 11's audit and six subsequent rounds:
those checked for shared values, not shared raw indicators. `models/risk_model.py`'s
Item 14 comment had already named and accepted this exact fact on 11 September ("ADX is
not wholly absent from bias_score — it reaches it through continuation_strength's
adx_component"), under the narrower standard that mattered for Item 14 (not the same
value read twice). RSI is not the same problem: trend_health's rsi_strength asks a
symmetric question (is RSI in a neutral, unexhausted band) and reversal_continuation's
momentum_component asks a directional one — genuinely different information from the same
series, not a duplicate.

**The fix — scoped narrowly, on Viktor's instruction.** Given a choice between fixing the
independence question, writing a reasoned rationale for the weight magnitudes, or both,
Viktor chose independence only. `indicators/trend_health.py`'s `continuation_strength` no
longer has an ADX component; its ceiling drops from 60 to 35 (RSI-momentum 15 +
acceleration 20), honestly, not rescaled back up — the same standard the original Item 11
fix used when `health_component` was removed rather than replaced. ADX now reaches
bias_score through exactly one of the six factors instead of two.
`models/risk_model.py`'s risk-regime gate reads raw ADX directly, never through
bias_score or continuation_strength, so it was already independent of this change and
needed no code change — only its comment, which asserted the now-superseded state,
updated to record what changed and why, with the original text kept for the record rather
than deleted.

**What this does NOT settle.** The weight magnitudes themselves — 0.30 / 0.20 / 0.15 /
0.15 / 0.10 / 0.10 — remain exactly what `Phase7_Roadmap.pdf` already says they are:
"currently judgment calls," chosen by hand, with no written rationale anywhere in the
repository for why trend health outweighs structure regime two to one, or why macro and
reversal/continuation are tied at 10%. Reasoning through those magnitudes, and writing
down the market thesis the review's own scope conditions ask for ("this engine believes X
about how these markets behave, therefore it measures Y and weights it Z"), is
deliberately not part of this patch. `volume_sentiment`'s, `supertrend_direction`'s and
`macro_bias`'s own source computations were also not re-checked for hidden shared inputs
with each other or with trend_health/reversal_continuation — only the pair the review
found was checked and fixed.

**Verification.** Golden snapshot moved in exactly 16 leaf fields, all causally downstream
of `bias.score` (which moved from 78.6972703 to 77.09945429 on the golden fixture, ADX
31.95632018 at the decision bar) — confirmed by a full leaf-level diff of the old and new
snapshot, not just that the test went green again after re-baselining. `code_hash` moved,
and moved in exactly one file's fingerprint, `indicators/trend_health.py` — confirmed
programmatically; the comment-only edits to `bias_engine.py` and `risk_model.py` did not
move their fingerprints, since `code_fingerprint.py` hashes the docstring-stripped parse
tree and plain `#` comments were never part of it. `run_hash` was confirmed unchanged on
the golden run, expected since neither `FINGERPRINTED_CONFIG` nor `FINGERPRINTED_MODULES`
names moved — `trend_health.py` is not itself a fingerprinted module, only the weight
constants and risk multipliers are, and none of those changed value.

### Second engine-review finding, recorded not fixed — the blend asks one question four times (19 September 2026)

The first finding, above, was narrow: two factors read the same raw ADX. Fixing it left
four of the six factors unexamined, and `docs/PHASE7_NEXT.md` said so. This is what
tracing those four found. Claude's work, unprompted, under Viktor's explicit delegation
of the call.

**Two errors in the project's own record, corrected.** `models/bias_engine.py`'s
dependency graph described `structure_regime` (weight 0.20) as "structure.py's
swing-based regime label". It is not, and never was. The label comes from
`_detect_regime()`, which computes the gap between `mean(close[-5:])` and
`mean(close[-15:])` and applies hysteresis. `swing_struct` is computed by the same
module and reaches nothing except the panel — `_detect_swing_structure`'s own docstring
says so. Because that description was wrong, the previous pass recorded `structure_regime`
as checked and independent, on the basis that swing highs and lows share nothing with
ADX or RSI. That conclusion is literally true and beside the point: the check was run
against a mechanism this factor does not use, so the question that mattered was never
asked. Both the graph and the open item have been corrected.

**The finding itself.** Four of the six factors — trend health (0.30), structure regime
(0.20), SuperTrend direction (0.15) and macro bias (0.10), three quarters of the blend
between them — are four different transforms of a single measurement: the recent
direction of `close`. An EMA slope; a short-versus-long mean gap; an ATR-banded flip;
price against its 50-EMA one timeframe up. They use different windows and different
arithmetic, so this is not the ADX defect repeated — that was one reading scored on two
curves, and these four will genuinely disagree at turning points. But all four are
monotonic in the same underlying quantity and enter the blend with the same sign
convention. In a sustained trend they agree because they must, and `bias_score` reports
that agreement to every downstream consumer as four independent confirmations. Only two
factors carry a measurement that is not price direction: volume sentiment (0.15), which
reads `volume`, and continuation's acceleration term, which reads the change in slope and
can oppose the slope itself.

**Why this is recorded rather than fixed.** Acting on it means reweighting or dropping
factors, and that is a trading judgment about what corroboration between correlated trend
reads is actually worth. This project cannot evaluate that yet: the golden baseline proves
a change is attributable, never that it is correct, and backtesting sits behind the release
gate. It is the same reasoning that declined to wire `trend_failure` at sequence item 9c —
an audit that finds a property is not a specification for changing it. The decision is
Viktor's, and it does not have to be made now.

**Also recorded, also not fixed.** RSI reaches `bias_score` through two factors:
`trend_health`'s `rsi_strength` and `continuation_strength`'s `momentum_component`.
`indicators/trend_health.py`'s 19 September comment exempts this from the ADX finding on
the grounds that the two ask different questions — one symmetric (is RSI in an unexhausted
band), one directional (is RSI positioned for continuation in this trend's direction). The
exemption is real but narrower than the prose claimed. Measured across RSI 0–100 in steps
of 0.5, the two curves correlate at r = 0.37 in downtrends and r = 0.83 in uptrends, where
both peak in the 50–65 band and both bottom at the extremes. The duplicated path is worth
at most 1.5 points of `bias_score` against the 2.5 the ADX fix removed, which is why it is
a note and not an alarm.

**What changed in code: nothing.** This patch edits one comment block, adds one
subsection here, and adds two tests. `code_hash` is unmoved — confirmed programmatically,
not assumed — because the `bias_engine.py` edit is comment-only and `tests/` is outside
the fingerprint entirely. The golden snapshot is unmoved for the same reason. The two new
tests pin the facts rather than the judgments: one asserts that `_detect_regime` responds
to `close` and does not respond to ADX, RSI or the EMA slope columns, verified against an
injected ADX dependency to prove it is not passing vacuously; the other pins the two RSI
correlation figures inside bands, so a future change to either curve cannot quietly widen
the overlap while the written exemption stays as it is. That second failure mode is
exactly how the `structure_regime` description went stale and took an audit conclusion
with it.

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


## Not on the roadmap, worth revisiting

- **Move the audit narrative out of code comments.** Ruled 5 September, deferred on
  purpose. The source and test files carry, in comments and docstrings, a stated prior
  verdict for seven of the forty-four rules, three counts of Critical findings, and two
  named prior reviewers. That is why every packaging round has to reason about what the
  artifact discloses, and why one round got it wrong. The narrative belongs in the
  Engineering Notes, beside the rest of the project's history. It is **not** done before
  the re-audit: editing the comments now hands the auditor a codebase altered to look
  better for its grader, which is the objection Section 4 of the reviewer instruction
  makes against stripping them at packaging time. Do it after a report comes back.

- **A database for decision history.** Raised by Viktor, 1 September 2026. Every run's
  reasoning currently lands in flat files — `logs/phase7_decision_log_*.jsonl` and
  `phase7_state_*.json` — which is simple and fine for a single-user, single-machine
  tool that never executes trades. That stops being enough once someone wants to query
  *across* runs — win rate by risk regime, how often the AGGRESSIVE gate in item 14
  actually fires, that kind of cross-run analytics — at which point scanning a folder
  of JSONL gets slow. No such need has come up yet, so nothing is planned; if it does,
  the natural fit is a lightweight embedded database (SQLite, not a server) as a query
  layer alongside the existing logs, not a replacement for them.


## Rulings, 11 September 2026

Five rulings, made in one session. Only the first reached a commit message; the rest are
written here because otherwise they existed only in a chat window.

**1. Item 14 — the risk regime determines itself.** Ruled, built and landed the same day at
`0c7dec5`. Full detail under "Open — decisions" item 2 above and in the commit message.
Claude asked whether to drop the weak-trend heuristic or replace it with something
risk-native; Viktor ruled replace.

**2. The live decision log — keep the records, tag them, and back them up.** Decision 7 is
settled in principle. Viktor's position: what the log holds now is build-and-test-phase
data, and it matters most once the project is finished. So the ten suite-written records
are NOT pruned — they stay as the evidence of what the suite was doing to the log, which is
this project's standing practice of recording rather than tidying, and they get tagged as
suite output rather than deleted. Claude argued for keeping on exactly that ground.

*Not yet built.* Viktor chose committed dated snapshots (option B) over an
ad-hoc manual step, and asked for automation if it is available. The open design question
is where they live: `logs/` is gitignored, so snapshots need their own committed location,
and if `Claude outputs/` is ever gitignored (see ruling 5) that location must sit outside
it. `Claude outputs/phase7_decision_log_aerousdt_20260906_backup.jsonl` already exists as
an ad-hoc precedent and is still untracked — it is currently the only second copy of the
6 September record, and committing it is the first concrete step.

**Snapshot mechanism BUILT, 12 September 2026** — see "Open — work" item 8. Placed at
`decision_log_backups/`, outside `Claude outputs/`, so it does not depend on ruling 5's
still-open `.gitignore` question either way. **The tagging half of this ruling is NOT
built** — the live log is gitignored and machine-local, so it is outside what a git patch
reaches, and it needs its own approach rather than being folded into the snapshot work.

**3. Part 7 — fold it into round 5 rather than resending it.** `commit_messages_PART7_ONLY.md`
was never sent to rounds 3 or 4. Rather than pay ~$1.40 to resend the package to fresh
instances purely to learn whether it would have changed verdicts, round 5's package carries
the full commit messages from the start, and rounds 3 and 4 stand as what they were.
Claude's recommendation, accepted: the only thing separate resending buys is evidentiary
completeness for two reports a new round is about to supersede.

**4. Disclosure of round 3 to Kimi — document it, do not undo it.** Keeping round 4 blind to
round 3 was methodologically right; that is what makes round 4 an independent data point
rather than an anchored one, and it cannot be un-happened now in any case. The obligation is
that when this comparison reaches the portfolio document, the non-disclosure and its reason
are written beside it rather than quietly omitted. Delegated to Claude and ruled on that
basis; decision 6 closes here with no engineering work attached.

**5. The handover and delivery-filename holes — sort them out.** Decision 8 accepted in
principle: the handover check gains a seventh question (does `git status --short` show
anything in the INDEX column, which would catch a staged-but-uncommitted commit), and the
generic-delivery-filename problem gets closed properly. *Not yet built.* The structural
option on the table is a `.gitignore` entry for `Claude outputs/`, which would stop it
reappearing in every listing and remove the `git add -A` hazard permanently — flagged as a
ruling rather than done, because Viktor ruled against a `.gitignore` exception for
`round3/README.md` on 5 September and this is the same shape of question.

**Seventh question BUILT, 12 September 2026** — in the "Working practice" handover check
below. **The `.gitignore` question is still open and still not this session's call to
make** — put to Viktor rather than defaulted, on the same ground he already ruled once.

**And a position, not yet a ruling: GPT-6 Astra for the next audit.** OpenAI released it on
3 September; it is on OpenRouter, which `send_audit_round.py` already pins model and
provider through, at roughly $10/$50 per million tokens standard. Viktor considers it worth
the stretch on the same principle that cleared Kimi. **It is blocked on one check he has not
run yet:** OpenAI is not on the clean list, because Luna Pro (GPT-5.6) ran both the hostile
Constitution review and Step 8. Whether that exposure clears depends on whether those two
sessions appear in the OpenRouter billing export under `variant=standard` with no training
routing — the same check that cleared Kimi and caught Mistral. If they do, the lab clears by
the existing ruling and Astra is the strongest option available. If those sessions ran
outside OpenRouter through a consumer interface, the standing rule is "treat it as
permanent" and Astra is out. The check decides it; the model's capability does not.

**RULED, 12 September 2026 — GPT-6 Astra selected.** The check came back clear: both of
Luna Pro's exposed sessions show `variant=standard` with no training routing. The exposure
is session-level, not lineage-level, so by the existing rule it does not carry to a later,
separate OpenAI model. Round-5 package prep (`send_audit_round.py`, `build_audit_package.py`,
new `item16_review_instruction_rev6.md`) follows in the same patch — see the head block at
the top of this file. Nothing sent; that step is Viktor's, on his machine.

**Strengthened the same day, in a separate follow-up: not just those two sessions.** Viktor
confirmed every Luna Pro call this project has ever made went through OpenRouter — no
consumer interface, so the "unknowable retention" branch above is never reached — and then
checked every one of the nine Luna Pro generations in the log himself, not only the two this
ruling names. All nine show `openai/gpt-5.6-luna-pro` (no `/flex` or `/fast` suffix) and "No
data training." See "Independence — what kind of exposure, and what clears it," Consequences,
CLOSED 12 September 2026, for the full closure — including of a hedge ("probably clean, not
provably") that section had carried since 2 September. This ruling was already sound on the
narrower check; it now rests on the exhaustive one.

## Ruling, 20 September 2026 — the open-items list scrapped; an independent audit next

*New in this file on 20 September 2026 (docs commit after `b68de08`).*

**What was ruled.** Viktor scrapped seven entries of PHASE7_NEXT.md's Open items as they
stood at `e115272`, in his words: "We are gonna scrap that entire list. 1-7." They were,
in the numbering used in the conversation: (1) his written position on the six
bias-weight magnitudes and the engine's thesis; (2) the five points from the
15 September PDF; (3) retiring "To do list Claude Phase 7 Engine.pdf"; (4) the
four-factor finding (the blend asks one question four times); (5) RSI reaching
`bias_score` through two factors; (6) the engine review's missing scope and completion
boundary; (7) the Constitution's backtest-start condition never having been formally
declared met. In their place: "We are going to have a new audit by an independent model
and go from there." Three mechanical items are done first — "We can do step 8., 9., and
10., before the new audit": the non-portable manifest test (done at `b68de08`), the
stale citations of PHASE7_NEXT.md in test files and build scripts, and README.md's
pre-existing omissions. The To-do PDF is to be deleted; it lives outside the repository,
so Viktor deletes it himself.

**How it came about.** Asked what was open, Claude listed the items. On item 1 Viktor
asked whether changes had been made without documenting why. Claude checked `git log`
rather than answering from memory: the six weights have not changed since they entered
the repository in `83a9425` (26 August 2026, "Publish Phase-7 Engineering Constitution,
docs, and current engine state"), which replaced the four-term blend (0.5/0.3/0.2/0.1)
of the first commits of 24 August wholesale. No commit changed a weight value; the
choice itself predates the repository's logging, so its reason was never written down.
Who chose the six values is not recorded anywhere Claude could find. Viktor then ruled
on the items one by one, then scrapped all seven.

**Claude's recommendation, and what it did not change.** Before the full scrap, when
Viktor had ruled to fix (4) and (5) while scrapping (1), Claude pointed out that fixing
either means choosing new weights — item 1 by another name — and suggested either a
short written reason for whatever weights came out, or structural fixes that record
the resulting weights as still unjustified. The full scrap superseded that question
rather than answering it. Claude also suggested that point 1 of the PDF (+0.69R
treating a confidence score as a win rate) might be a plain calculation error rather
than a judgment call — unchecked against the code; it goes with the rest.

**What this does not change.** Nothing here removes the record: the findings behind
(4) and (5) stay in this file ("Second engine-review finding, recorded not fixed",
including its "Also recorded, also not fixed" note on RSI), and the old Open items stay
in PHASE7_HISTORY.md. They are no longer open items. The Constitution's backtest-start
condition (Items 2, 3, 6, 18) still stands as written — scrapping the open item does not
declare it met or waive it. The 15 September course correction ("engine review before
any Goal B work") is not amended by this ruling; how the independent audit relates to
that review has not been ruled.

**Not yet decided** (Viktor's calls, for when the audit is planned): which model; the
package (the standing default for a genuine fresh Tier-1 audit is the full audit
package — see Working practice); and whether the auditor is shown the scrapped
findings. Claude's note on the last: an auditor that has not seen them is more
independent, and anything real in them should surface again on its own.

## Ruling, 20 September 2026 — dated records are not edited to follow a move

*New in this file on 20 September 2026, with the item-9 citation patch (after `16d3c1f`).*

**What was ruled.** Item 9 (stale citations of `docs/PHASE7_NEXT.md`) was recorded as
seven test files and three build scripts. A repository-wide search found more: comments
and docstrings in engine modules, the audit-package and handover scripts,
`requirements.txt` and three READMEs. Claude asked two questions. (A) Should the item
cover every stale pointer the search found? Viktor: yes. (B) Should dated records — the
Engineering Notes entries, `Claude outputs/` handovers, `docs/audit_reports/`,
`docs/constitution_reviews/` — be edited too? Viktor's first position was yes, "the aim
was to keep a real record." Claude argued against: those citations were true when
written (HISTORY and DECISIONS did not exist before 18 September), the Engineering Notes
are declared append-only in the project's own AI-Attribution Statement, and some of the
records are other models' output. Claude proposed a forward note instead. Viktor
accepted it ("we can ignore it this time if you want"); Claude read that as a ruling for
the forward note and said so before building.

**The rule.** A dated record is not edited because a file it cites has since been split
or moved. The forward note is this ruling plus one sentence in PHASE7_NEXT.md's head
block, the file every stale citation leads to: a citation of PHASE7_NEXT.md written
before 18 September 2026 refers to content now in this file (rules, rulings,
specifications) or in PHASE7_HISTORY.md (dated accounts). Live files — code, tests,
build scripts, READMEs — are corrected directly.

**Where the note went, and why it changed.** Claude first proposed a new Engineering
Notes entry and notes in the `Claude outputs/` and `docs/audit_reports/` READMEs. It
chose PHASE7_NEXT.md's head block and this file instead: every stale citation leads to
PHASE7_NEXT.md, so one note there reaches all of them, and this file is not rewritten
each session, so the rule outlasts the sentence in NEXT. The Engineering Notes will
record the patch at their next regeneration in the ordinary way.

## Ruling, 20 September 2026 — round 3 is not counted as independent

*New in this file on 20 September 2026, with the docs commit after `92775ea`.*

**What was ruled.** Round 3 (5 September 2026, GLM 5.3 Flash) is not counted as an
independent audit round. README.md said all five rounds after the original audit ran "on
a model reporting no prior exposure"; it now says round 3 was not independent, and why.

**Why this needed a ruling.** The record contradicted itself. HISTORY's 5 September
entry "Z.ai is not clean" concluded GLM 5.3 Flash "was not an independent reviewer",
reasoning from the lab-level rule: GLM 5.3 had a substantive session on this project on
28 August. But the 2 September ruling (HISTORY, "Independence — what kind of exposure,
and what clears it") holds that exposure from a chat session clears with a fresh
conversation when training is off, and calls applying the lab-level rule to it a
category error. That ruling cleared Kimi K3 on 5 September and OpenAI on 12 September.
GLM 5.3's 28 August session is the same kind: `OpenRouter: Chatroom`,
`variant=standard`, in the provider export. On exposure alone, the 2 September ruling
would clear it.

**The reason that does hold is authorship, not exposure.** That 28 August session
produced the Remediation Plan — `build_remediation_plan.py` records it as "Produced by
GLM 5.3 (z-ai/glm-5.3) on August 29, 2026", from the complete engine source, the
Constitution, all four round-1 audit outputs and the Engineering Notes. Round 3 then
reviewed an engine remediated under that plan. The exposure table has no category for
a lab reviewing work done under its own plan; this ruling is the first case of it.

**How it came about.** Viktor first remembered the 28 August GLM run as "for a minor
thing" and a deliberate compromise — "pretty much the first sidestep" from the rules —
and proposed counting round 3 as independent. Claude checked the record rather than
answering from memory: the run was Step 5, with the full inputs above, 104,394 tokens in
and 55,179 out, and no compromise ruling exists anywhere; the only verdict on file was
the 5 September one. Claude also pointed out that "independent" and "a sidestep" cannot
both be published. Viktor then ruled: "don't count it as independent then."

**Why the round ran at all.** It was never chosen. The round-3 package was meant for
another model; the chat was left on Auto Router, which sent it to GLM 5.3 Flash
(HISTORY, "The GLM 5.3 Flash run — an accident that produced a report"). The
5 September rulings kept its report as round 3 — not acted on, but compared against
round 4's report on the same unmodified code.

**What this does not change.** Round 3's findings stand on their own evidence, and the
fixes built on them stand. No release-gate or portfolio-ready claim rested on round 3's
independence: the gate was declared on round 6's targeted re-audit. What it weakens: the
count of independent rounds after the original audit falls from five, as published, to
three that are both independent and complete (rounds 4, 5 and 6). The authorship
question — whether a lab that planned the fixes may later grade them — is decided here
for this one case only, not as a general rule.

## Ruling, 21 September 2026 — the independent audit paused; four weeks of our own work first

*New in this file on 21 September 2026, with work order F.*

**What was ruled.** Viktor: "We pause the audit. We work on the engine another four
weeks." Asked to write his position first, he set out: "We pause or [our] audit. And
keep working on the engine for another for weeks, reviewing everything, analyzing and
do fixes and patches and try to evaluate our work. Integrity and truth must remain."
After Claude's critique he added: "we should not audit or [our] own work, but we have
fixes to make and prepare a new audit as good as we can."

**What it does not change.** The Constitution's sequence still binds: "8) Re-audit the
items that changed — independent auditor again, not a self-check by whoever made the
fix. 9) Only then … build the backtesting architecture." Pausing the audit is
consistent with it; pausing it and then starting backtesting is not. The open questions
of the 20 September ruling (which model, which package, whether the auditor sees the
scrapped findings) stay open until the audit is planned.

**How the four weeks are recorded.** Agreed with Viktor: nothing done in them is written
up as verification. Our own review, tests and negative controls are recorded as
unaudited work awaiting the auditor — never "found sound", the wording that made items
14 and 15 read as the builder certifying his own compliance. Preparing the audit means
three things: a running list of every change since the last audit (what changed, which
finding it closes, which tests guard it), which becomes the auditor's scope; Viktor's
open rulings answered before the package is sent, so the auditor judges the engine
against stated intent; and the deferred read done first.

**Claude's two points, not adopted.** (1) The pause has no end condition — "about four
weeks" is a plan, not a trigger; Claude suggested a date, about 19 October, on which
Viktor decides again whether to commission the audit or extend the pause. (2) The rule
"no backtesting before re-audit" exists only as text; a structural form would be a
backtest entry point that refuses to run without a recorded re-audit. Neither was
ruled on; both are recorded here so the choice not to adopt them is visible.

## Ruling, 21 September 2026 — the entry signals confirm (work order F)

*New in this file on 21 September 2026, with work order F.*

**The question.** Finding 11: `long_signal` / `short_signal` were computed every run
and decided nothing. On 2 September they had been left in `entry` "for a future ruling
on whether they should CONFIRM a direction bias has already chosen." Claude set out
three options — remove them, make them confirm, or keep and relabel — and named the
second as Viktor's, because it changes which trades are taken.

**What Viktor ruled.** Option 2: a trade the decision ladder chooses is taken only if
that side's signal confirms it; otherwise the action is `NO-TRADE (SIGNAL
UNCONFIRMED)`. His written position, after two rounds of Claude's critique:

1. Macro is removed from the signal completely (it is already inside `bias_score`; a
   veto would count it twice).
2. The reversal check is ruled by its components, not a number: HVN proximity alone
   does not block (the stop pulled to the HVN, finding 6, already acts on that area);
   divergence and exhaustion do.
3. Only a reversal pointing against the trade blocks it.
4. The CONFIRMED requirement is dropped; the signal accepts the direction
   `decision_model` chose from `raw_bias`.
5. When risk and confirmation both fail, `NO-TRADE (RISK TOO HIGH)` stays the label and
   the confirmation failure is appended to the reasons.

He also asked for a check of past decisions first. Claude read the 29 records of the
live decision log: no action would change; the one SHORT in it (code `38458f20…`) had a
reversal reading of 4.0 that was HVN proximity alone, which the old signal refused and
the new one passes. `decision_log_backups/…20260906.jsonl` is a byte-for-byte copy of
the log's first 11 records, not further evidence.

**Delegated to Claude.** Viktor: "Make the adjustments you want and do what is best for
the engine and the project." Claude's calls under that delegation, each reversible by
Viktor:

- **One divergence rule, not two.** `decision_model` vetoed its two upper tiers on any
  divergence whichever way it pointed, while CONSERVATIVE had no divergence check.
  That check is removed; the gate's direction-aware rule applies to every tier.
  Consequences: an upper-tier setup with a divergence against it used to fall to
  CONSERVATIVE or WAIT and is now refused; one with a divergence pointing its own way
  is no longer demoted.
- **The trend-health ≥ 50 condition is dropped from the signal:** every trading branch
  already requires ≥ 50 or ≥ 75, so it decided nothing.
- **Macro inside CONSERVATIVE is NOT changed in this work order.** The CONSERVATIVE
  branches require macro agreement — the same double count Viktor removed from the
  signal. Recorded as finding 17 and scheduled as its own work order (G), so each
  change to which trades are taken is attributable to one commit.
- **The bias state machine now gates no trade** (consequence of rule 4). It still feeds
  `exit_model`'s "bias state changed" flag and the persisted state. Recorded as finding
  18; nothing removed.

**Stated for the auditor.** The three surviving conditions (structure regime,
exhaustion, divergence) also reach `bias_score` as weighted factors. The gate is a hard
AND on top of that blend: it can refuse a trade, never add confidence to one. It is a
design choice and has not been backtested. The HVN reasoning in rule 2 depends on
finding 6, still open: if the stop stops being pulled to the HVN, nothing checks HVN
proximity at all.

## Working practice

- **Deliver as a `.patch`, never a zip.** `git apply --check <file>.patch` first, then
  `git apply`. Write the patch and message file into the repo over the device bridge,
  stage them out with explicit paths, then delete them.
- **When several fixes are landing in the same session, deliver one patch's files at a
  time** — write, apply, commit, delete — rather than placing more than one patch and
  commit-message pair on disk together. `git add -A` sweeps in whatever is still sitting
  there, staged or not (rule 38).
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
- **A delivered file gets a staged name unique to its version.** Reusing one staged
  filename for two versions of the same file shipped the older bytes on 6 September with
  no error reported anywhere.
- **Verify a delivery by reading the file back off the device and diffing it** against the
  intended bytes. Compiling the copy that was sent proves syntax, not identity — both
  versions compiled.
- **Token-saving discipline — adopted 15 September 2026.** Five rules, implemented into
  the patch-delivery skill so a fresh session follows them without being told:
  1. Scoped-files review packages (touched files, direct callers, contract tests) are the
     default for fix-verification sends and narrow patches. The full audit package
     (~400K+ tokens) is reserved for a genuine fresh Tier-1 audit round, not decided
     per-round.
  2. Engineering Notes and Portfolio Document regeneration is batched — at session close,
     or once several commits have landed since the last regeneration — rather than run
     after every small patch. `PHASE7_NEXT.md` itself stays current every time regardless;
     only the two generated PDFs are batched.
  3. `docs/audit_package/`'s `qwen_reasoning_*.txt` files and superseded audit-round
     folders are not staged or re-read as routine workflow, only when a question calls
     back to that specific round by name.
  4. When a patch ships with a commit message, the chat reply stays predictions-and-
     commands only, regardless of how small the patch feels — the discipline compounds
     across a session, a single lapse does not.
  5. Prefer a fresh session over a long one at a real closure point — a finding closed, a
     milestone reached, the docs caught up — over continuing on momentum.
- **Run the handover check before the session ends — Claude initiates it, Viktor does not
  have to remember.** A session does not persist. Whatever was established in it and not
  written down has to be rediscovered, slowly and incompletely, and the parts that came
  out of live runs cannot be rediscovered at all. On 3 September the whole day's state --
  eleven verified findings with line numbers, four patches, three rulings made, three
  owed, sizes for what remained -- existed only in a chat window until Viktor asked
  whether it was safe. It was not. The check runs on any signal the session is ending:

  Run `python docs/build/session_handover_check.py` first — added 15 September 2026,
  twentieth patch, extended with item 8 the same day (twenty-second patch). It answers
  items 3, 5, 7 and 8 below by command (git status, loose delivery files, the staged index,
  README.md's last-touched date) rather than by memory, and prints items 1, 2, 4 and 6 as
  an explicit reminder, since those need someone to read and judge this file's own content,
  which no script can do. Its output is a floor, not a substitute for going through all
  eight:

  1. Is the current state in this file, rather than only in the conversation?
  2. Are today's rulings recorded here, with what they decided and why?
  3. Does `git status --short` show untracked files that matter? Evidence in the repo
     root is the usual casualty -- it survives only if someone commits it.
  4. Are the Engineering Notes current, or is the gap stated explicitly?
  5. Are loose `.patch` files still sitting unapplied?
  6. Is anything still only in a chat window -- a review, a transcript, a reasoning dump?
  7. Does `git status --short` show anything in the INDEX column -- a fully staged commit,
     prepared and never made? Added 11 September 2026, ruling 5: the six questions above ask
     about untracked files and loose patch files, and a staged-but-uncommitted index is
     neither. The 6 September doc rewrite sat that way through a whole session and a
     handover check before anyone noticed.
  8. Does README.md's prose still match what this head block currently declares? Added 15
     September 2026 (twenty-second patch) after README.md went sixteen days stale (last
     touched 30 August, fixed at `ebb0a46`) with nobody noticing. The script prints
     README.md's last-touched date and the commit count since, every run; judging whether
     the content still matches stays manual, the same as items 1, 2, 4 and 6.
  9. Is the pre-push hook installed in this clone? Added 19 September 2026 with
     `githooks/pre-push`, which runs this same script on every `git push`. Git does not
     version `.git/hooks`, so the hook is tracked under `githooks/` and switched on per
     clone with `git config core.hooksPath githooks` — a local setting that a fresh clone
     silently lacks. The script flags it unset, the hook file missing, or the hook tracked
     without its executable bit (Linux/macOS git ignores such a hook; Git for Windows does
     not).

  **Ruled 19 September 2026 — what the pre-push hook does on a finding.** Asked to
  choose between (A) stop the push, consult, override with `git push --no-verify`; (B) a
  y/N prompt at the terminal; (C) warn and let the push through, Viktor first said a
  finding should "only warn, then I consult with you and we push or not." Claude pointed
  out that (C) cannot deliver the second half: the push would have left before the
  consult. Viktor chose (A). The override is deliberate — the decision stays his; the
  hook only guarantees the look happens first. (B) was not rejected on merit but because
  reading the keyboard from a hook under cmd.exe through Git for Windows' sh could not be
  verified from the sandbox. The hook fails closed: if the check cannot run at all, the
  push is stopped too.

  Report what the check finds, not that it ran. If everything is filed, one line.

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
18. *No rule 18.* The rule numbered 18 until `108cc9f` (2 September 2026), "Fixing the
    instance you found does not close the item", is now rule 22. The number is left
    empty rather than closed up, because rules are cited by number throughout the
    project's records and renumbering would make every later citation wrong. This line
    also keeps the rendered list's numbering equal to the numbers written here: Markdown
    numbers an ordered list by position, so without an item 18, every rule from 19 on
    displayed one lower than its cited number. (Recorded 20 September 2026.)
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
34. **A conversation is not a record, and the person doing the work should not be the one
    who has to remember that.** On 3 September a full day of findings, verifications,
    rulings and sizings existed nowhere but a chat window, and would have been lost
    because nothing in the routine said to write it down. It was caught because Viktor
    asked whether it was safe -- which is exactly the save-by-vigilance that rule 28 says
    to replace with a structural fix. The fix is the handover check under Working
    practice, run by Claude at the end of every session rather than requested. The general
    form: where continuity depends on someone remembering to preserve something, move the
    remembering into the process and give it to the party that does not get tired.
35. **Re-stage every base file immediately before generating a diff.** Three patches on
    4–5 September were built against files staged before an earlier patch had landed —
    patch J against a pre-patch-I `engine_core.py` (39 failures), patch K twice against a
    `decision_log.py` missing an anchor added hours earlier. The staged copy is a snapshot,
    not a view, and the moment another patch commits it is silently wrong. A patch built on
    a stale base fails loudly if you are lucky and applies cleanly if you are not.
36. **Measure the behaviour before ruling on it, not after.** Ruling 3 concerned how often
    the engine silently read a real trend as flat. That question has an answer in the data,
    and it was obtained — 9,800 live bars — before the ruling was made rather than used
    afterwards to justify it. A ruling made first and measured second is not a ruling, it
    is a hypothesis with a decision attached to it. Where the cost of measuring is an hour
    and the cost of being wrong is a defect in a release-gated engine, measure.
37. **Knowing a rule is not applying it.** Rule 30 — a substring assertion cannot see the
    shape of what it matched — was written on 3 September after it let a defect through.
    On 5 September Claude wrote a test asserting on `"support"` against a note that quotes
    a label containing the word SUPPORT: the same class of error, in a test written to
    guard the same class of error, two days after writing the rule about it. Rules in this
    file do not fire on their own. The ones that repeat are candidates for a mechanical
    check, not a firmer intention.


38. **Delivering more than one patch's files to the repo root at once reproduces the
    `git add -A` trap on every commit in the batch, not just the first.** The three
    F1/F2/F3 patches and their commit messages were all placed in `D:\phase7_engine`
    together rather than one pair at a time, 13 September 2026. `git add -A` at every one
    of the three commit steps therefore staged not only the intended fix but the next
    fix's still-unapplied `.patch`/`_commit_message.txt` files, and a pre-existing,
    unrelated modification already sitting in the working tree. Nothing wrong actually
    landed — `git status --short`, read before every commit rather than trusted from
    the numbered command sequence, caught it each time, and `git reset` corrected it
    before each commit. The structural fix is to deliver one patch's files at a time, so
    the trap has nothing left on disk to sweep in.
