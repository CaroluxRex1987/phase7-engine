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
- **Fill price** *(added 27 September 2026)*: a backtest fills at the open of the candle
  after the decision candle and records the gap from the decision close — "Ruling,
  27 September 2026 — the plan is measured from the decision close (finding 4)", which
  states what it weakens.
- **Spot only** *(added 29 September 2026)*: SHORT is not traded. It closes an open
  long, and the backtest then holds USDT until the next long. Each SHORT is still
  scored for whether it was right, as information. "Ruling, 28 September 2026 — what
  "finished" means, and how the engine is judged", point B, states what it weakens.
- **How a trade ends** *(added 29 September 2026)*: T1 before the stop is a win, the
  stop first a loss. At T1 half is sold and the stop moves to the entry; the rest runs
  to T2 or T3, back to the entry, or to a SHORT signal. The same rules as paper
  trading — the same ruling, points 8 and C; C states what it weakens.

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

*(Added 29 September 2026.)* Beside the verdict, the same OOS trades are scored
against the finish criteria of "Ruling, 28 September 2026 — what "finished" means,
and how the engine is judged", point 7: the share reaching T1 before the stop, the
average profit per trade after fees, and the comparison with random longs. They are
reported, not graded; the verdict above is unchanged (point A of that ruling).

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

*Point (1) was answered on 22 September 2026: "Ruling, 22 September 2026 — when the
audit resumes", below.*

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

## Ruling, 22 September 2026 — when the audit resumes

*New in this file on 22 September 2026, with the Engineering Notes' v1.34 regeneration.
It answers point (1) of Claude's two in the 21 September ruling above; point (2) is
not touched.*

**What was ruled.** Viktor: "We do the audit after we have done G and my findings."
The independent audit resumes when a fixed list of work is done:

- **work order G** (finding 17, macro inside the CONSERVATIVE branches) has landed; and
- **findings 4, 5, 6, 7, 16 and 18** are each done.

**What "done" means.** A finding is done when Viktor has ruled it and any code his ruling
calls for has landed. A ruling to leave something as it is counts as done. Proposed by
Claude; Viktor: "Yes the short term work is 'done' when we have fixed G and the finding,
that's all."

**The list is closed.** Viktor: "anything else we might find gets put on a list for after
the next audit." A finding made after this ruling does not join the list and does not
move the audit. It goes on a separate list, kept in PHASE7_NEXT.md, for after the audit.
His reasoning: "We do the work we said we would do. There is no difference in stopping
now and have the audit, or stopping after the point we decided."

**The four weeks.** An estimate, not a rule. Viktor: the four weeks was his "estimation
... to do the work we decided to do before the audit and also add a buffert for unseen
things. That is all." No date is attached to the trigger.

**How it was reached.** Viktor wrote his position first and Claude critiqued it. The
critique named three gaps. (1) An open list could grow without end: each new finding
would push the audit back, which is the "no end condition" point again by another
route. (2) "Done" was undefined. (3) Whether the trigger replaced the four weeks.
Viktor's answers closed all three. His argument on (1) is that a fixed list is itself
the end condition. Claude agreed and withdrew the objection. On (2) he answered first
about the whole project — "years in the making, constantly improving, constantly fine
tuning, constantly auditing" — and Claude pointed out that the definition was needed
for six findings, not for the project. He accepted the definition above.

**A tension Claude named, not ruled on.** Viktor described the project as running until
"we have built an version of this engine that actually generates profit". Goal B as
ratified (above, 15 September) makes the first out-of-sample evaluation the verdict of
record, accepts a negative verdict as completion, and makes each later re-run a new
phase with its own pre-registration. Working toward a profitable engine is consistent
with that one phase at a time; re-running until a result passes is not. Recorded so it
does not come as a surprise when backtesting starts.

**What it weakens.** A defect found during this work waits for the list after the audit,
whatever its severity, because the ruling makes no exception. The Constitution's order
is unchanged: audit before backtesting (step 8 before step 9).

## Ruling, 22 September 2026 — bias_score's weighting waits for after the audit, and the auditor sees it

*New in this file on 26 September 2026. Ruled in chat on 22 September; filed with the
seventh session's first commit, as owed.*

**What was ruled.** Viktor chose option 3. The weighting of `bias_score` stays off the
closed list (the 22 September ruling above) and waits until after the independent audit.
The independent auditor is shown these findings. "The weighting" means four things:

- the six weights, 0.30 / 0.20 / 0.15 / 0.15 / 0.10 / 0.10, which have never been
  reviewed or given a written reason;
- the four-factor overlap ("Second engine-review finding", above);
- RSI reaching `bias_score` twice (the same section, "Also recorded, also not fixed");
- one volume/macro disagreement adding up to three penalties.

The last of the four is recorded here in Viktor's words from the 22 September message. A
keyword search of this file and HISTORY did not find it as a finding; the nearest is point
2 of the 15 September PDF in HISTORY, "volume may be counted three times". This session
did not see options 1 and 2, so they are not recorded.

**What it answers, and what it leaves open.** The 20 September ruling left open whether the
auditor is shown the scrapped findings. This answers it for items (4) and (5) of that
list and for the weights half of item (1); the thesis half is not covered. Whether the auditor sees the rest of the 20 September scrapped
findings is still Viktor's call. Claude's note of 20 September still applies to the part
now decided: an auditor that has already seen a finding is less independent on that point.

**What it weakens.** An unreviewed weighting sits at the centre of every decision the
engine makes, and the audit runs without it being ruled. The audit can show the weighting
is implemented as written; it cannot say the weights are right.

## Ruling, 26 September 2026 — any model may build or review; doing so costs it audit eligibility

*New in this file on 26 September 2026, filed with the eighth session's first commit.
Viktor stated the position in chat on 22 September and ruled it on 26 September. Claude
drafted the wording and showed it to him in chat before this commit.*

**What was ruled.** Viktor: "a model can be used to review and build but not for audit".
No model is barred from build or review work on the engine. A model that has done that
work may not audit the engine: authorship disqualifies it permanently, and having read
engine source disqualifies it for independence.

**How it was reached.** The 22 September position was worded as "spent models for build
and review" — models already spent as auditors may do build and review work. Viktor asked
why any model would be deemed spent for building and reviewing. Claude agreed the wording
was wrong: "spent" is a fact about the audit role only, and says nothing against building
or reviewing. The rule was restated the other way round — build and review work is open
to any model, and what it costs is audit eligibility — and Viktor confirmed it.

**What goes with it,** carried from the 22 September position and Claude's draft:

- each use is entered in the independence ledger at the time of use;
- work from any model reaches the repository as a patch under the normal gates, with the
  model named in the commit message;
- a family still clean for auditing is not used for build or review work, because that
  work spends it as an auditor. Build and review work goes to models already ineligible
  to audit, Claude among them.

**Where it stands in practice.** No model other than Claude is in use. Viktor stopped
using Grok, the only other one, after its test run reported 2 failures on a suite that
passes on his machine and in Claude's sandbox — failures Grok put down to repository
checks and did not resolve (PHASE7_NEXT.md, Open items, 26 September).

**What it weakens.** Every model used for build or review is one fewer candidate auditor,
and the families not yet in the project's record are few. The rule does not stop a clean
family being used for build work; it makes the cost explicit and puts it on record.

## Ruling, 26 September 2026 — the pre-send token check is audit preparation, not an engine item

*New in this file on 26 September 2026, filed with the eighth session's first commit.
Viktor stated the position in chat on 22 September and ruled it on 26 September. Claude
drafted the wording and showed it to him in chat before this commit.*

**What was ruled.** Viktor: "The pre-send token check is a preparation not an engine
item". The check measures the audit package with the chosen auditor's own tokenizer and
refuses the send if the package plus an output reserve does not fit the model's context.
It is built ahead of the audit. It is not on the closed list (22 September) and does not
add to or reopen it.

**Why it exists.** An auditor must be able to read the whole package without running out
of context: package size is a hard gate on which model can audit (Viktor, 22–23
September; the ranking is in "Phase-7 — Model Roster", outside the repository).

**Conditions,** Claude's of 22 September, which the ruling answers:

- it is built outside the fingerprinted modules, so it cannot move `code_hash`. `docs/`
  is excluded by directory (`core/code_fingerprint.py`, `EXCLUDED_DIR_NAMES`), so
  `docs/build/` qualifies;
- it goes through the normal patch gates, and takes a line in `docs/audit_change_list.md`,
  which covers tooling as well as engine code;
- it cannot be finished until the auditor is pinned, because it needs that model's
  tokenizer. Until then it can be built with the model as a parameter.

**What it weakens.** It puts a tool on the audit's path that no independent party has
reviewed. If it counts wrong, it can pass a send that truncates or refuse one that fits.

## Ruling, 26 September 2026 — the stop-distance finding is evidence for findings 4 and 6

*New in this file on 26 September 2026, filed with the eighth session's second commit.*

**What was ruled.** Viktor agreed with Claude's recommendation: the finding that the
engine almost never trades, because nearly every run is refused on the stop's distance
(Viktor, 22 September; the evidence is in PHASE7_NEXT.md, "Evidence for findings 4 and
6"), is evidence for findings 4 and 6. It is not a new item and not part of work order G,
and the closed list (22 September) is unchanged. Two parts of Claude's code reading were
ruled separately:

- **The 8% ceiling is part of finding 6.** Viktor: "Ok". A stop 8–15% from the price is
  refused as EXTREME RISK (`models/risk_model.py:439`, `:524–526`), so the working limit
  is 8%, not the 15% that finding 6's text stated until 26 September. Ruling finding 6
  decides how far a stop may sit, and these limits are part of that question.
- **The risk gate's position goes on the list for after the audit.** Viktor: "We can put
  it on the after audit list". The risk verdict is checked before the weak-validation and
  lean checks (`models/decision_model.py:500–502`, `:605–617`), so a run the ladder would
  have answered WAIT is reported as NO-TRADE (RISK TOO HIGH) — 2 of the 33 refused runs
  in the log counted on 26 September. It changes what the panel says, not which trades
  are taken, and it was found after 22 September.

**Why not G.** The risk verdict returns before the direction ladder whose CONSERVATIVE
branches G changes. No refusal in the log is within G's reach.

**How it was reached.** Viktor adopted Claude's recommendation rather than writing a
position first. Claude said at the time that the only critique of the recommendation was
its own, which is weaker than his testing it, and that this was acceptable here: the
question is where a finding is filed, and nothing the engine does turns on it.

**What it weakens.** Findings 4 and 6 now carry the measurement of how often the stop
vetoes a setup, which makes them heavier to rule. Until after the audit the panel keeps
reporting some runs that would have been WAIT as RISK TOO HIGH.

## Ruling, 26 September 2026 — decisions are made on closed candles (finding 16)

*New in this file on 26 September 2026, phase 3 of the roadmap to the audit.*

**The question.** Finding 16: the engine decides on the candle that is still forming.
`data/data_fetcher.py` reads MEXC's `close_time`, throws it away and keeps every row. So
on a live run, the close, the volume and every indicator at the decision bar come from a
partial candle, and two runs inside one candle can decide differently. The staleness
check measures from the last candle's open time, so a forming candle is never stale.
Claude asked four questions: which candle decides, what the panel shows of the forming
candle, how staleness is measured, and whether the log records which candle was used.

**What Viktor ruled.**

1. Decisions are made on closed candles only, on every series the engine fetches: the
   symbol's execution timeframe, the macro timeframe and BTCUSDT (today 4h, 1d and 4h).
2. Nothing that decides reads the forming candle. The panel shows the live price on one
   line, labelled as information only, with its distance from the decision candle's
   close. Whether stop and targets should be measured from the live price instead is
   finding 4's question.
3. Staleness is measured from the decision candle's close time. A series fails the check
   unless its decision candle is the latest one that should have closed, allowing a
   short grace for exchange delay. A failure is handled as a stale series is handled
   today.
4. The decision log records, for each series, the decision candle's open time and
   whether a forming candle was dropped.

Points 1 and 4 are Viktor's own position. Points 2 and 3 were Claude's suggestions, which
he adopted.

**Accepted with it.** A decision can be up to one candle old: four hours on 4h, a day for
macro. A price move inside the forming candle is invisible until that candle closes.
`current_price` (`core/engine_core.py:1005`) becomes the decision candle's close, so stop
and targets are measured from that close until finding 4 is ruled. A run in the first
minutes after a close may fail the staleness check instead of deciding on the previous
candle.

**Left to the implementation, and recorded when it lands.** The grace value, with the
evidence for it. How pinned data is treated, since it carries no close time, and whether
the golden snapshot moves.

**Done when** the code lands, with the live run done and the decision-log record read
before its commit.

**Recorded when its code landed** *(added 26 September 2026, eleventh session, by the
commit that lands the code; the ruling above is unchanged)*.

- **Point 3, how it reads.** Before building, Claude asked which of two readings Viktor
  meant: a candle that closed less than the grace ago is not yet final, so a run inside
  the grace fails; or the grace lets the previous candle stand, so a run never fails.
  Claude recommended the first, since it is the only one the "Accepted with it" sentence
  above fits. Viktor agreed by sending the clock measurement Claude had asked for as the
  go-ahead. So: a series fails once a newer candle than its decision candle has closed
  ("stale data"), and fails inside the grace after its decision candle's close ("not
  yet final"). Both are handled as a stale series is handled today.
- **The grace: 60 seconds** (`FINALITY_GRACE_SECONDS`, `data/validation.py`). The
  evidence: Viktor's clock against time.windows.com, 26 September 2026, five samples by
  `w32tm /stripchart`: +0.198 s to +0.200 s, steady. MEXC's own delay in finalising a
  candle was not measured, since the sandbox cannot reach api.mexc.com. Sixty seconds is
  a margin chosen against the one number that was measured. The cost is a failed run in
  the first minute after each close: six minutes a day on 4h.
- **Pinned data.** Every row of a pinned file is treated as closed, and nothing is
  dropped. The record's `forming_candles_dropped` is `null`, not 0, because a pinned
  file carries no fetch time and the question cannot be asked. The live price is `null`.
- **The golden snapshot moved by one added field only**, `provenance.decision_candles`.
  No decision field moved, and `run_hash` is unmoved.
- **The panel.** The price line was labelled CURRENT PRICE; it is the decision close
  now and is labelled DECISION CLOSE, with the decision candle's open time. The live
  price follows as `LIVE PRICE`, marked information only, with its distance from the
  decision close. Claude proposed the label; Viktor agreed with the reading above.

## Ruling, 27 September 2026 — indicator values are no longer replaced beyond 5 sigma (finding 7)

*New in this file on 27 September 2026, phase 3 of the roadmap to the audit. Ruled in a
session on 27 September that made no commit; recorded, with the code, by the next one.*

**The question.** Finding 7: `clean_series` (`indicators/indicators.py:105–110` at
`add8540`) set every indicator value more than five standard deviations from its
series' mean to NaN, once the series had more than 10 values. Inside the frame the
forward fill then replaced it with the previous bar's value; at the decision bar it
stayed NaN and was reported as an indicator failure. Nothing recorded either. The mean
and standard deviation spanned the whole series.

**What Viktor ruled.**

1. Remove the 5-sigma replacement from `clean_series`.
2. Keep the step that turns inf into NaN.
3. Checking the candles for bad data goes on the list for after the audit.

**The evidence it was ruled on** — from the ruling session, sandbox and synthetic
frames, not live data, as Viktor stated it:

- A fresh SuperTrend flip of 17 or fewer bars in 450 is erased and becomes a failure.
- An ATR spike of about 2.2x its usual level at the decision bar is erased.
- No test in the 65 test files pins the behaviour: the rule needs more than 10 values,
  and the longest series a test passes is 10.

**Scope.** Everything that passes through `clean_series`: EMA_20 and EMA_50, RSI, ADX,
the SuperTrend level and direction, and ATR, on the primary paths and on the EMA, RSI
and ATR fallbacks.

**Accepted with it.** An indicator value is written as computed, however far it lies
from the rest of its series. On price, `data/validation.py` rejects NaN, inf,
non-positive values and impossible candles (a high below the low, the open or the
close; a low above the open or the close), and nothing else — read at `add8540`; its
31 August ruling on isolated spikes is about volume. So a bad price print that is
internally consistent now reaches every indicator unaltered. Before, it was erased
only where it pushed an indicator past 5 sigma, and at the decision bar that erasure
was itself a failure. Checking candles for bad data is point 3.

**Done when** the code lands, with the live run done and the decision-log record read
before its commit.

**Recorded when its code landed** *(added 27 September 2026 by the commit that lands
the code; the ruling above is unchanged)*.

- **Re-measured while building, sandbox and synthetic.** The flip threshold is a
  count below n/26, where n is the number of values the direction series has. On a
  450-bar frame SuperTrend's warm-up leaves 440, so a flip of 16 bars or fewer was
  erased and 17 survived; the ruling session's "17 or fewer in 450" is the same bound
  on 450 values. The ATR case reproduced on the pinned AEROUSDT 4h fixture with the
  last bar's range widened 15 times: ATR 2.19x its median over the previous 50 bars,
  erased. A 10% decision-bar move after a flat market erased EMA_20, EMA_50, the
  SuperTrend and ATR, and RSI as well with the fallbacks forced. The test-file count is
  64 `test_*.py` files; 65 counts `tests/conftest.py`.
- **On the fixtures the rule never fired.** Instrumented at `add8540`, it touched no
  value on the golden run or on any of the four fixture frames, which is why no test
  noticed it and why the golden snapshot does not move.

## Ruling, 27 September 2026 — the plan is measured from the decision close (finding 4)

*New in this file on 27 September 2026, phase 3 of the roadmap to the audit. Ruled and
recorded, with its code, in the same session.*

**The question.** Finding 4: the panel printed an ENTRY ZONE — the band between EMA_20
and EMA_50 — while the stop, T1–T3 and all three R:R values are measured from
`current_price`, the close of the decision candle (`core/engine_core.py`, the line after
the finding 16 comment; the call into the risk model below it). No rule requires price
to be inside the band to trade: LONG is reachable at NEAR ZONE, and CONSERVATIVE LONG has
no band condition. The panel printed no single entry price, and a backtest has to fill
somewhere.

**How it was ruled.** Not in the usual order. Viktor asked for Claude's suggestions
first, and Claude set out three options: (A) the decision close, made explicit; (B) the
band — the plan becomes a limit order at the band's edge, with an expiry; (C) the live
price at run time. Claude recommended A, advised against C (it undoes finding 16, is not
reproducible under Item 2, and two runs inside one candle would print different plans),
and said B changes which trades are taken, which only backtest evidence can judge.
Viktor asked for Claude's single suggestion and chose A.

**What Viktor ruled — option A.**

1. The close of the decision candle — the latest closed candle, since finding 16 — is
   the plan's single entry price. Stop, targets and R:R are measured from it, as they
   already were. The panel says so, and the log records it.
2. The band is labelled for what it is on the panel, the band between the two EMAs, so
   the panel stops implying an entry there.
3. A backtest fills at the open of the candle after the decision candle, and records the
   gap between that open and the decision close.
4. Option B — entering at the band — goes on the list for after the audit.

**The risk accepted, not measured.** B may be part of the answer to "the engine almost
never trades": an entry at the band on a pullback sits nearer the stop, so fewer runs
would exceed the distance limit that refuses most of them (the count of 26 September:
29 of 33 refusals on the distance limit). Nobody measured it before the ruling. Claude
offered to measure it from the decision log; the ruling was made without it.

**What point 3 weakens**, stated per this project's amendment rule, since it adds to
Goal B's methodology (a pointer is added there):

- The printed R:R holds only for an entry at the decision close. A backtest fill at the
  next open realises a different R:R whenever the two differ. The gap is recorded, not
  corrected for.
- A fill at the next candle's open is optimistic about timing. The decision cannot
  exist until the decision candle is final — at least 60 seconds after the close, since
  finding 16 — so the open itself is not an achievable price. Spread, fees and slippage
  are not part of this ruling; they are Goal B's methodology.
- How large the close-to-next-open gap is on the exchanges the engine reads has not
  been measured.

**Accepted with it.** No rule is added that price must be in the band to trade: which
trades are taken does not change. `entry_status`'s values ("ACTIVE ENTRY ZONE", "NEAR
ZONE", …) and the STATUS line that prints them are unchanged, because `decision_model`
reads the value (`"ACTIVE" in entry_status`); renaming them is a decision-path change
the ruling did not ask for. The data keys (`zone_lower`, `zone_upper`,
`distance_from_zone`) and the degradation block's wording for a missing band ("entry
zone") are unchanged for the same reason: they are recorded in the decision log, and a
rename there is a change to the record, not to the panel. The entry-quality score is
unchanged: it scores an entry at the decision close against the band, which is what
point 1 says the entry is.

**Done when** the code lands, with the live run done and its decision-log record read
before the commit (the change moves `code_hash`).

**Recorded when its code landed** *(added 27 September 2026 by the commit that lands
the code; the ruling above is unchanged)*.

- **Point 1.** The panel's DECISION CLOSE line now ends "the plan's entry; stop,
  targets and R:R are measured from it". The log already recorded the price, as
  `exit.current_price`; no field is added, so the decision object and the golden
  snapshot do not change. `core/decision_contract.py` says what the field is, in a
  comment.
- **Point 2.** ENTRY ZONE and ZONE DISTANCE are now EMA BAND and BAND DISTANCE. The band
  line names the EMA lengths from `config.EMA_FAST` and `config.EMA_SLOW`, not written-in
  numbers, and says it is "a reference, not the entry". The chart's legend reads "EMA
  band".
- **Point 3** is recorded here and pointed to from Goal B's methodology. No backtest
  code exists; none is written.
- **Point 4** is on the list for after the audit in PHASE7_NEXT.md.

## Ruling, 27 September 2026 — the stop comes from ATR alone (finding 6)

*New in this file on 27 September 2026, phase 3 of the roadmap to the audit. Ruled on
27 September, after `b0efe23` landed; recorded, with the code, by the next commit.*

**The question.** Finding 6: the stop was pulled to the HVN — the single highest-volume
bin of the whole 450-candle frame (`indicators/volume_profile.py`, 50 bins), about 75 days
on 4h. `core/engine_core.py` passed `structural_level=hvn` to
`RiskModel.calculate_stop_targets`, which set a long's stop at min(HVN, ATR stop) and a
short's at max(…). The HVN could only widen the stop, and nothing limited how far: a trend
that had moved away from its point of control got its stop there, and past 8% the risk
check refused the setup (EXTREME RISK; past 15% the distance limit, RISK REGIME UNKNOWN).
The 8% ceiling was ruled part of this finding on 26 September.

**How it was ruled.** Not in the usual order: Viktor ruled by agreeing to Claude's
suggestion, not by writing his position first. Recorded that way at his instruction.

**What Viktor ruled.**

1. The stop comes from ATR alone. It is no longer pulled to the HVN. The HVN stays as
   information only.
2. The 8% (EXTREME RISK) and 15% (distance refusal) limits are unchanged.
3. Since work order F nothing checks HVN proximity: the confirmation gate stopped
   checking it because the HVN stop covered it. That goes on the list for after the
   audit.
4. Using the swing-structure level as the stop anchor was not chosen and not measured.

**The evidence it was ruled on** — Claude, 27 September, from Viktor's
`logs/phase7_decision_log_aerousdt.jsonl` staged off his disk: 40 records, 6–27
September, AEROUSDT 4h, test runs included, 39 usable.

- The HVN pull set the stop in 35 of 39 runs. Median stop distance with the pull: 19.4%.
  Only 3 runs passed the risk check.
- ATR-only: median 5.8%, widest 10.1%. 29 of 39 would pass the risk check; 7 would
  still be refused (6 on EXTREME VOLATILITY, 1 over 8%).
- These figures are Claude's recomputation of the stop formula from the logged inputs,
  not engine output. It matched the logged stop exactly on the 4 runs where the HVN did
  not take over.
- Passing the risk check is not a trade: the direction rules and the confirmation gate
  still apply. The 26 September replay suggested most such runs become CONSERVATIVE and
  a few reach the LONG/SHORT tier.

**Correction to that evidence, found when the code landed** *(Claude, 27 September,
recomputed from the same 40 records, re-staged off Viktor's disk and byte-identical to
the log the ruling was made on)*. "29 of 39 would pass" and "7 would still be refused"
do not add up to 39. Under ATR alone **32 of 39 pass**: the 29 counted are the runs that
newly pass, and the 3 that passed with the pull pass too (29 + 3 + 7 = 39). The 7
refused, the medians and the 35 of 39 hold as stated. The ruling was made on the figure
as worded; the correction makes the evidence stronger, not weaker. Recorded rather than
quietly fixed.

**What it weakens**, stated per this project's amendment practice:

- The HVN no longer vetoes anything. A stop may now sit inside or short of a
  high-volume area — a level where price has often reacted — and be taken out there.
  How often that happens has not been measured; only a backtest can.
- No gate checks HVN proximity (point 3). A long can be authorised directly under a
  high-volume node.
- It changes which trades are taken. Runs refused on the distance limit alone now reach
  the direction ladder and the confirmation gate. On the pinned golden fixture the
  action moves from NO-TRADE (RISK TOO HIGH) to CONSERVATIVE LONG.
- The stop distance now depends only on ATR and the multipliers in
  `models/risk_model.py` (trend health, bias score, volatility state), none of which has
  been backtested.

**How "information only" is read** — Claude's reading, Viktor's to correct. The stop
stops reading the HVN, and nothing else changes: the HVN is still computed and recorded
(`structure.hvn`, `indicators_at_decision_bar.HVN`), and its other existing uses stay —
the entry score's structure points (`models/entry_model.py`, up to 12 of 102), the
reversal reading in `indicators/trend_health.py` (which reaches `bias_score` as part of
the 10% reversal/continuation factor), and the Exit Watch "close to a high-volume node"
note. They weigh; none of them gates. Whether they should stay is not part of this
ruling.

**Done when** the code lands, with the live run done and its decision-log record read
before the commit (the change moves `code_hash` and the decision path).

**Recorded when its code landed** *(added 27 September 2026 by the commit that lands
the code; the ruling above is unchanged)*.

- **Point 1.** `calculate_stop_targets` no longer takes `structural_level`: passing it
  raises TypeError, as `detailed_bias` does since work order C. The stop is
  `price ∓ ATR × stop multiplier`, and nothing else moves it. `engine_core` passes no
  HVN, and `lineage.risk_inputs` no longer lists `structural_level` — it records what fed
  the stop, and the HVN no longer does; the HVN stays under `structure.hvn`.
- **Point 2.** `REGIME_EXTREME_STOP_PCT` (8.0) and `MAX_STOP_DISTANCE_PCT` (15.0) are
  unchanged and pinned by `tests/test_stop_is_atr_only.py`; no fingerprinted constant
  changed, so `run_hash` did not move.
- **Point 3** is on the list for after the audit in PHASE7_NEXT.md. The dependency
  comment in `models/entry_model.py` now says it is in force.
- **Point 4** is recorded here only. Nothing was built or measured.

**Confirmed, 27 September 2026 (the next session)** *(added by the commit that lands
finding 5's code; the ruling above is unchanged)*. Viktor confirmed the "information
only" reading above: only the stop stopped using the HVN. Its uses in the entry score,
the reversal reading and the Exit Watch stay, and revisiting them belongs with the
`bias_score` weighting review after the audit (DECISIONS, 22 September). Confirmed by
agreeing to Claude's suggestion, not by writing his position first; recorded that way
at his instruction.

## Ruling, 27 September 2026 — a NEUTRAL bias prints no plan (finding 5)

*New in this file on 27 September 2026, phase 3 of the roadmap to the audit. Ruled on
27 September, after `76c8cde` landed; recorded, with the code, by the next commit.*

**The question.** Finding 5 (review of 21 September): the plan's direction is the sign
of `bias_score` (`models/risk_model.py`, `calculate_stop_targets`, since work order C),
so a score inside ±20 — a NEUTRAL bias, which prints no direction box — still printed a
long- or short-shaped stop, three targets and their R:R, and a score of exactly 0
printed a long.

**How it was ruled.** By agreeing to Claude's suggestion, not by writing his position
first. Recorded that way at his instruction.

**What Viktor ruled.**

1. Panel only. Under a NEUTRAL bias the panel prints no stop, targets or R:R, and
   instead one line saying there is no plan because the bias is NEUTRAL (score X,
   inside ±20), so there is no direction to measure a stop from.
2. The engine still computes and logs the plan, because the risk check needs a stop.
3. Before any diff: check where the panel prints the plan lines, and that a NEUTRAL
   bias never reaches LONG or SHORT.

**The checks point 3 asked for** — Claude, 27 September, at `76c8cde`, before the diff.

- *Where the plan is printed* (read in `core/panel_render.py` and
  `models/exit_model.py`): the DECISION CLOSE line's ending ("the plan's entry; stop,
  targets and R:R are measured from it", since finding 4), STOP LOSS, and TARGET 1–3
  with their R:R. One more line names a plan price: the Exit Watch's always-on note
  "…once price reaches Target 1 ($x)" (`build_exit_watch`). Nothing else prints the
  plan. Decision Reasoning's expected-value sentence names the fixed 2:1 average reward,
  not the plan's R:R; a risk refusal's reason can cite a stop distance in percent, and
  that distance does not depend on the side (ATR × a multiplier built from
  |`bias_score`|), so it stays true under NEUTRAL.
- *A NEUTRAL bias never reaches LONG or SHORT.* From the code:
  `_determine_final_action` (`models/decision_model.py`) returns a side only inside its
  `raw_bias == "BULLISH"` and `raw_bias == "BEARISH"` branches; a NEUTRAL bias falls
  through to WAIT, or returns earlier with a NO-TRADE or a WAIT. The later stages — the
  confirmation gate, `_refuse_incoherent_plan` and degradation — only turn a side into
  a NO-TRADE, never create one, and `models/signal_router.py` takes the action from
  `evaluate` alone. A second, independent guard holds as well: a NEUTRAL score is inside
  ±20 (`RAW_BIAS_THRESHOLD`), and `MIN_ACTION_BIAS` (30) sends any lean below 30 to
  WAIT, so even a NEUTRAL bias misread as a direction would not trade. From the record:
  Viktor's `logs/phase7_decision_log_aerousdt.jsonl`, staged off his disk (41 records,
  6–27 September), holds 2 NEUTRAL runs, one WAIT and one NO-TRADE (RISK TOO HIGH). As
  a test: `tests/test_neutral_bias_prints_no_plan.py` runs the full `evaluate` over a
  grid of 48,384 NEUTRAL inputs and gets only WAIT and NO-TRADE (RISK TOO HIGH), with a
  negative control showing the same grid reaches a side under BULLISH and BEARISH.

**What it weakens**, stated per this project's amendment practice:

- Under a NEUTRAL bias the panel no longer shows the stop the risk check measured. A
  NEUTRAL run refused as NO-TRADE (RISK TOO HIGH) cites a stop distance whose stop is
  not printed; the stop is in the log (`risk.atr_stop`).
- The panel and the log now differ under a NEUTRAL bias: the log carries a plan the
  panel does not show. Anyone reading the log — a backtest included — must know that a
  NEUTRAL record's stop and targets are not a plan the engine offered.
- A reader who used the NEUTRAL panel to see where a stop would sit if the market
  broke one way loses that. It was only ever the side the score's sign picked.
- ENTRY QUALITY and TRADE QUALITY still print under a NEUTRAL bias, scored for the side
  the score's sign picks. This ruling does not cover them; found while building it, and
  on the list for after the audit (PHASE7_NEXT.md).

**Claude's readings, Viktor's to correct** — three places where the ruling's words had
to be applied to lines it did not name:

- *DECISION CLOSE.* Under a NEUTRAL bias the close and its candle still print, without
  "the plan's entry; stop, targets and R:R are measured from it", which would otherwise
  sit directly above a line saying there is no plan.
- *The Exit Watch note naming Target 1* is a target, so under a NEUTRAL bias the panel
  does not print it. The decision object and the log still carry it. The panel
  recognises it by its opening words, named once as `TARGET1_NOTE_PREFIX` in
  `models/exit_model.py`; the note's text is unchanged.
- *Only NEUTRAL withholds the plan.* A raw bias the engine never emits (absent, shown
  as UNKNOWN) prints the plan as before: the ruling names NEUTRAL, and an absent reading
  is not a reading of no lean.

**Done when** the code lands, with the live run done and its decision-log record read
before the commit (the change moves `code_hash`, though no decision).

**Recorded when its code landed** *(added 27 September 2026 by the commit that lands
the code; the ruling above is unchanged)*.

- **Point 1.** The line reads, for example, `PLAN          : none -- the bias is NEUTRAL
  (score +12.4, inside ±20), so there is no direction to measure a stop from`. The
  threshold is read from `RAW_BIAS_THRESHOLD`, not written in; a score that was not
  computed prints "score not computed", never "nan". It replaces STOP LOSS and the three
  TARGET lines in the same place on the panel.
- **Point 2.** Nothing in the engine, the decision object or the log changed: the
  golden snapshot did not move. `code_hash` moved, for `core/panel_render.py` and
  `models/exit_model.py` only.
- **Point 3** is above, and pinned by the grid test.

## Ruling, 27 September 2026 — a push that goes as predicted leaves nothing owed

*New in this file on 27 September 2026. Ruled on 27 September; recorded by the commit
that lands finding 5's code.*

**The question.** Since the pre-push hook (19 September), each push's hook result was
filed by the next commit, which left that commit's own push owed — a floor of one owed
item that never cleared. Claude proposed on 26 September (proposal (b)) that a push
whose result Viktor does not paste back be recorded once as "as predicted", and only a
deviation be filed as an owed item.

**How it was ruled.** By agreeing to Claude's suggestion, not by writing his position
first. Recorded that way at his instruction.

**What Viktor ruled.** Proposal (b) is adopted. A push that goes as predicted is
recorded once, in the next commit's account, and leaves nothing owed. Only a deviation
becomes an owed item.

**What it weakens.** A push that went wrong and was not reported would now leave no
trace of being unconfirmed; before, the owed item kept asking. It rests on Viktor's
standing practice of reporting only what differs from a prediction (20 September), and
on Claude reading `master` and `origin/master` off his disk at the start of the next
session, which is kept.

## Ruling, 27 September 2026 — the bias label is a function of the score (finding 18)

*New in this file on 27 September 2026, phase 3 of the roadmap to the audit. Ruled on
27 September, after `8b9ac1e` landed; recorded, with the code, by the same commit.*

**The question.** Finding 18 (review of 21 September): since work order F dropped the
CONFIRMED requirement from the confirmation gate, the bias state machine gates no
trade; `detailed_bias` still feeds the panel, `exit_model`'s "bias state changed" flag
and the persisted state. The finding asked whether "its persistence requirement" should
gate anything.

**What Claude found before the ruling, from the code** (`models/bias_engine.py`,
`BiasStateMachine.transition`, at `8b9ac1e`). **There was no persistence
requirement.** `transition()` never read its previous state: every branch assigned
`self.state` from the current `raw_bias` and `bias_score` alone. `core/engine_core.py`
built a fresh instance per process, which on this engine is one run, so it started at
NEUTRAL every time in any case. CONFIRMED only ever meant |`bias_score`| > 30. The
decision ladder already needs |`bias_score`| ≥ 30 (`MIN_ACTION_BIAS`) to act, so
gating a trade on CONFIRMED would change the outcome at exactly 30.0 and nowhere else.
Nothing that decides reads the label: it is read by the panel (BIAS, BTC BIAS), by the
wording of the BTC sentence in `decision_model`, and by `exit_model`'s flag, which
compares against the label the previous run persisted in `engine_core`'s state file —
the only cross-run memory involved. From the record: Viktor's
`logs/phase7_decision_log_aerousdt.jsonl`, staged off his disk (42 records), holds
`bias.detailed` exactly as the current score gives it in all 42 (BULLISH CONFIRMED 36,
BEARISH CONFIRMED 3, NEUTRAL 2, BULLISH 1). BTC's score is not in the record, so BTC's
labels were not checked this way. The finding's own text ("its persistence
requirement") and the comment written at F in `models/entry_model.py` described
something the code never did.

**The options Claude set out.** A: leave it as a label, correct the wording, no code.
B: give it real persistence (a side must hold for N closed candles before a trade) — a
new trading rule. C: replace the class with a plain labelling function giving the same
labels. D: gate trades on CONFIRMED — it would block only a score of exactly 30.0.

**How it was ruled.** By agreeing to Claude's suggestion, not by writing his position
first. Recorded that way, as for findings 5 and 6.

**What Viktor ruled.**

1. The behaviour stays exactly as it is: the same labels, word for word, and no
   decision changes. No new trading rule now (not B), and no CONFIRMED gate (not D).
2. The code says what it does (C): `BiasStateMachine` is replaced by a plain function,
   `bias_label(raw_bias, bias_score)`, with no state; `engine_core` labels AERO and BTC
   through it; the wrong "persistence" wording is corrected where it stands.
3. "A side must hold for N closed candles before a trade" goes on the list for after
   the audit, with Claude's note: if it is ever built, compute it from the closed
   candles in the run's own input, which the input hash pins, not from a state file,
   which would be an input the record cannot reproduce.
4. "CONFIRMED" stays on the panel for now. Whether to rename it (it reads as
   confirmation over time, which it never was) is a wording question for after the
   audit; renaming it moves a panel label and the golden snapshot.

**What it weakens**, stated per this project's amendment practice:

- The panel keeps a word, CONFIRMED, that suggests a lean has held for a while. It has
  never meant that, and point 4 leaves it in place until after the audit.
- `EngineCore` no longer has `bias_state_machine` or `btc_bias_state_machine`. Any
  script outside the repository that reached for them breaks; inside it, nothing did
  (every `.py` file searched).
- `tests/test_bias_label.py` pins "no memory". Adding persistence later now fails a
  test, so it has to be done on purpose — which is the intent, and also a cost.

**Claude's readings, Viktor's to correct.**

- *The 20 is read, the 30 is written in.* The NEUTRAL band reads
  `RAW_BIAS_THRESHOLD` (it was a literal 20, the same value, so no label changes; a
  change to the constant now moves the band with the raw bias it describes). The 30
  stays a literal: naming it would put it in `FINGERPRINTED_MODULES`
  (`tests/test_fingerprint_names_every_constant.py`), which moves `run_hash` and the
  golden snapshot for a number that decides nothing; `code_hash` covers it. It is
  `MIN_ACTION_BIAS`'s value, which `bias_engine` cannot import (`decision_model`
  imports `bias_engine`).
- *The edge at exactly 30.0, recorded, not changed.* The label needs > 30 and the
  ladder acts at ≥ 30, so a run at exactly 30.0 can take a side while the panel's BIAS
  line reads BULLISH or BEARISH, not CONFIRMED. Recorded beside `MIN_ACTION_BIAS` in
  `models/decision_model.py`.
- *Corrections, not rewrites.* The wrong "persistence requirement" in
  `models/entry_model.py`'s comment is kept and followed by a dated correction. So is
  the label list in `models/risk_model.py`'s docstring and in
  `tests/test_plan_direction_and_side.py`'s, which named only BULLISH CONFIRMED,
  BEARISH CONFIRMED and NEUTRAL; the function also returns plain BULLISH and BEARISH.
  Their conclusion (never "LONG" or "SHORT") stands.

**Done when** the code lands, with the live run done and its decision-log record read
before the commit (the change moves `code_hash`, though no decision). Ruling and code
land in the same commit; the commit message has the evidence.

## Work order G, 27 September 2026 — macro no longer decides the CONSERVATIVE tier (finding 17)

*New in this file on 27 September 2026, the last item on the closed list before the
independent audit. Claude's work order under Viktor's delegation, with one ruling of
his inside it; recorded, with the code, by the same commit.*

**The question.** Finding 17 (review of 21 September): both CONSERVATIVE branches of
`decision_model`'s ladder required `macro_bias` to agree with the side
(`and macro_bias == "BULLISH"`, and `"BEARISH"` on the short side). Macro is already a
10% factor inside `bias_score`, so the requirement counted the same evidence twice —
the double count Viktor removed from direction on 2 September and from the entry
signal at work order F. Left out of F so that each change to which trades are taken
lands in its own commit.

**What Claude found before building, from the code and the log.**

- The two upper tiers never had the condition; only the tier with the weakest case
  did.
- Macro reaches the decision in four places: `bias_score` (10%), the entry score's
  confluence multiplier (×1.05 / ×0.90), the validation score (+10 / −20), and this
  clause. G touches only the clause. Claude's reading, from the wording and not
  confirmed with Viktor: the first three are the "one volume/macro disagreement adding
  up to three penalties" item in the 22 September ruling above, which waits for after
  the audit.
- From reading, no test pinned the clause.
- Viktor's `logs/phase7_decision_log_aerousdt.jsonl`, staged off his disk (43 records,
  6–27 September, AEROUSDT 4h), replayed through the router before and after the
  change: the pre-change code reproduces 42 of the 43 logged actions (the miss is a
  16 September SHORT from before F's gate). G changes 2 runs, both on 15 September,
  bearish bias with bullish macro: WAIT on the ladder becomes CONSERVATIVE SHORT. Both
  are then refused as NO-TRADE (SIGNAL UNCONFIRMED), because those records predate F
  and carry no short signal — so whether either would have traded cannot be read from
  the log. Macro agreed with the bias in every other directional run. The log barely
  exercises G.

**Claude's calls under the delegation, each reversible by Viktor.**

1. The macro condition is removed from both CONSERVATIVE branches. The tier is now: a
   side at `MIN_ACTION_BIAS` or more, trend health at
   `CONSERVATIVE_TREND_HEALTH_MIN` or more, below the upper tier — then the
   confirmation gate, as for every tier.
2. `macro_bias` is removed from `DecisionModel.evaluate()` and
   `_determine_final_action()`, since nothing there read it once the clause was gone.
   Keeping an unread parameter would be the item-14 shape (a declared input nothing
   reads), and removing it means macro cannot come back into the ladder without a
   signature change a test catches. The router still takes `macro_bias` and records
   it in the decision object.
3. Everything after `risk` in `evaluate()` is keyword-only, and `reasons` in
   `_determine_final_action()`, so a caller still passing macro in the old fifth
   place fails with a TypeError instead of the string landing in `btc_context`.

**Viktor's ruling inside G — by agreeing to Claude's suggestion, not by writing his
position first.** The CONSERVATIVE sentence read "...but the entry quality (N/100)
isn't strong enough" in every case. The tier is also reached with a strong entry and
trend strength between 50 and 75, and then the sentence blamed a number that had
passed. G rewrites that sentence anyway, so Claude asked whether to fix the false
clause inside G or put it on the list for after the audit; Viktor chose to fix it
inside G. The sentence now names what fell short — trend strength, entry quality, or
both — from the same constants the ladder compares against, through one helper for
both sides. It no longer mentions macro.

**What it weakens**, stated per this project's amendment practice:

- **The CONSERVATIVE tier admits setups whose higher timeframe disagrees or is flat.**
  The requirement was a double count, but it was also the only place the higher
  timeframe could veto that tier outright. A weak-entry trade against the daily trend
  can now be authorised if the bias is at 30 or more and the confirmation gate passes.
  Neither the old filter nor its removal has been measured on data where macro
  disagrees; this log does not contain enough of it.
- `DecisionModel.evaluate()` no longer accepts `macro_bias`, and its later arguments
  must be passed by name. A script outside the repository that called it either way
  breaks; inside it, the router and eight test files were changed (every `.py` file
  searched).
- `tests/test_direction_source.py`'s helper, and one test in
  `tests/test_signal_confirms.py`, now go through the router instead of
  `evaluate()` directly, because the router is where a macro reading still enters.
  They exercise more code per test, so a failure there is less precisely located.

**Stated for the auditor.** Whether a higher-timeframe veto belongs on the weakest
tier is a design question this change answers "not as a second count"; it has not been
backtested either way. The other three places macro reaches the decision are
unchanged and wait for after the audit.

**Done when** the code lands, with the live run done and its decision-log record read
before the commit (the change moves `code_hash`; on live data it changes a decision
only at CONSERVATIVE strength with a macro that disagrees or is neutral). Ruling and code land
in the same commit; the commit message has the evidence. With it, the closed list is
done and the independent audit is next.

## Ruling, 28 September 2026 — what "finished" means, and how the engine is judged

**Why this exists.** Until now the project had no stated claim a test could check, and
no finish line except Goal B's verdict on a backtest. On 28 September, before choosing
any work, Viktor asked which questions the project should ask itself about its logic,
integrity and functionality. Claude listed sixteen (docs/PHASE7_NEXT.md, Open items,
"The questions of 28 September"). Viktor answered the four that were his — what the
engine claims, what result ends development, whether a year of paper trading is enough,
and what weight the portfolio carries — and the rest of this entry follows from those
answers.

How each point was ruled is marked. **Viktor's position first** means he wrote his
position, Claude critiqued it, and he settled it. **By agreeing to Claude's
suggestion** means he asked for Claude's suggestion and agreed to it. Points A–E were
ruled on 29 September, the next morning of the same session.

### Viktor's position first

1. **The claim.** A LONG the engine issues should at least reach T1 before its stop.
   T2 and T3 are a bonus. There is no time limit on a trade: Viktor holds positions for
   months when needed. At a reading, a trade still open is reported separately and is
   neither won nor lost.
2. **T1 must net at least 3% after fees.** Viktor said 3–10%. Read from the code at
   `7d0024e`: T1 is exactly one stop distance from the entry (`TARGET1_MULT = 1.0`,
   `models/risk_model.py`), and a stop more than 8% away is classified EXTREME RISK
   (`REGIME_EXTREME_STOP_PCT = 8.0`), which is NO-TRADE (RISK TOO HIGH). So T1 cannot
   pay more than 8% while that limit stands. Today the engine issues trades with a stop
   anywhere from 0.2% (`MIN_STOP_DISTANCE_PCT`) to 8%, so the floor needs a filter in
   the engine — a new trading rule, on the list for after the audit by the 22 September
   ruling. Every loss is then also at least 3% plus costs.
3. **Spot only; no leverage and no futures.** On spot, SHORT means sell to USDT and wait
   for the next long setup; when nothing is held it means stay in USDT. If futures are
   ever used, SHORT means a 1× short and never more.
4. **No weekly trade target and no cap.** The engine trades whenever a valid setup is
   there and not otherwise; ten trades one week and none the next is fine. The count is
   never raised by loosening a threshold. More trades come from more pairs.
5. **Results are read at 3, 6, 9 and 12 months, and a reading changes nothing.** No
   tuning between readings. A change to the engine is a new version, and its count
   starts again from zero; the `code_hash` in every decision record separates the
   versions.
6. **The portfolio is secondary.** It is not important that this project serves as an
   exam project; Viktor can make another project for that. Confirmed as a ruling by
   point E below.

### By agreeing to Claude's suggestion

7. **Finished** means one engine version and at least 100 closed trades on data it was
   not tuned on, with all of:
   - at least 60% reach T1 before the stop;
   - average profit per trade after fees above zero;
   - it beats random longs that use the same stop and T1 over the same period.

   Fewer than 100 closed trades is "not enough evidence yet", neither pass nor fail, and
   the test runs on. Why 60 and 100: over 100 trades an engine with no edge (a coin flip
   at 1:1) reaches 60% about 3% of the time; 55% needs about 400 trades to say the
   same, and at 55% costs eat most of the edge — as an illustration, not measured fees,
   with a 3.2% stop and 0.2% costs a trade averages +0.12% at 55% and +0.44% at 60%.
   The fee check stays separate because the entry gap on crypto has not been measured.
   The benchmark is there because in a rising market random longs also reach T1 first
   more often than not. Viktor first proposed 51% as the minimum; Claude showed that at
   1:1 it leaves +0.02 of the stop distance per trade before costs, which fees can
   exceed, and that telling 51% from luck takes about 10,000 trades.
8. **Scoring.** The win is decided at T1: T1 before the stop is a win, the stop first
   is a loss, and the win rate counts only those two. A long closed by a SHORT signal
   before either is scored by its net result after fees, reported as its own group
   ("closed by signal") together with its share of all trades. At T1 half is sold and
   the stop moves to the entry; the rest runs to T2 or T3, back to the entry, or to a
   SHORT signal. That changes only the profit total, never the win count. Every trade
   counts in the profit total.
9. **Trends only, for now.** Range trading — buying at support and selling at
   resistance on levels drawn by hand, which is Viktor's own style — is a second
   strategy: new entry logic, stops at levels, new code, its own log and its own
   verdict. Two strategies judged in one verdict could not be told apart. It goes on the
   list for after the audit. **Its first test case** is the chart Viktor marked on
   28 September: BLESSUSDT, 2h, MEXC, roughly 10–26 September 2026 — six buys, about
   11, 17, 20, 22, 24 and 25 September, at roughly 0.0078–0.0093, and six sells, about
   16, 19, 21, 23, 24 and 25 September, at roughly 0.0094–0.0105, read by eye from his
   screenshot. The screenshot is not in the repository; it shows his browser, and the
   repository is public. **The cost, stated:** trends only means the engine will not
   trade the way Viktor does. On that chart Claude expects it would mostly have waited —
   an expectation, not a run.
10. **Capital, for paper trading.** The paper account is split into 10 equal slices of
    10%, with one open position per pair. With the 8% stop limit, one trade can lose at
    most 0.8% of the account. When all ten slices are in use, a new valid setup is
    logged as "missed: no cash" and still scored as if taken, so the engine is judged
    on every setup it finds and the account shows what the money could actually do.
11. **Reports show how many trades were opened together.** Most pairs move with BTC,
    and ten longs opened on one day are closer to one bet made ten times than to ten
    bets.

### Reconciled with Goal B — ruled 29 September 2026, by agreeing to Claude's suggestion

Claude read Goal B (above, 15 September) against points 1–11 before anything was
written, and found five places where they meet.

- **A. Two finish lines, in stages.** Goal B's verdict stays exactly as pre-registered
  (Sharpe ratio against buy-and-hold; INCONCLUSIVE under 30 OOS trades) and judges the
  backtest. The criteria of point 7 are also reported on the backtest's OOS trades,
  beside the verdict, without changing it. "Finished" is declared only when paper
  trading meets them. This weakens nothing in Goal B; it adds a bar.
- **B. Spot only applies to Goal B** — added to its methodology. **What it weakens:**
  the backtest no longer measures the engine's SHORT calls as trades; they are scored
  as information only.
- **C. Goal B uses point 8's exit rules** — added to its methodology, so the backtest
  and paper trading measure one strategy. **What it weakens:** Goal B had no exit rule,
  and this fixes one before any result exists, so the verdict of record measures that
  policy only. Another exit policy (all out at T1, or hold for T3) is a new phase under
  the re-run clause.
- **D. Goal B's dataset is unchanged** — AEROUSDT 4h, AEROUSDT 1d and BTCUSDT 4h,
  pinned. Several pairs are for paper trading only. Goal B's scope-honesty sentence
  stands: one pair is not evidence that the engine generalises.
- **E. The project's purpose from now on is an engine that is profitable by points
  1–11.** Goal A stands as achieved (declared and tagged `portfolio-v1` on
  15 September), and its text is not edited: "It does not have to make money" was true
  of goal A and still is. Goal B's "What goal B is actually for" also stands — a
  trustworthy verdict, not a favourable number.

### What this ruling does not do

- It changes no code, so `code_hash` and the golden snapshot do not move.
- It does not amend the Constitution. Tier 0 asks for "reliable, testable, interpretable
  information and decisions under real-world conditions"; point 7 is how "reliable under
  real-world conditions" is now measured.
- It does not move the audit or reopen the closed list. The 3% floor (point 2) and the
  range mode (point 9) wait for after the audit.
- It does not lift "no backtesting before an independent re-audit" (Constitution
  step 8).
- Nothing of the paper-trading setup exists yet: unattended runs every 4h per pair, the
  paper account with its ten slices, the scoring of points 7–11. Building it is not an
  engine change. When it is built is Viktor's call.

### Claude's errors on the way, recorded

- Claude first said a trade needed a time limit because "almost any LONG reaches T1
  eventually if you wait long enough or ignore the stop". With the stop in place,
  "T1 before the stop" is well defined with no time limit, and Claude said so when
  Viktor answered that he holds positions for months.
- Claude first read Viktor's "10% profit" as 10% on the account over a year and
  proposed measuring in R (units of risk). He meant 10% on the position, per trade;
  without leverage that needs no sizing rule, and his unit was adopted.

The binomial figures above were computed in the sandbox; the code facts were read at
`7d0024e` from an autocrlf clone.

## Ruling, 29 September 2026 — Fable 5.1 works on the list for after the audit, not before it

*New in this file on 29 September 2026, filed with the twentieth session's commit.
Ruled in chat the same day, by agreeing to Claude's suggestion — not by Viktor writing
his position first.*

**The question.** Viktor has 100 USD of Claude credit for Fable 5.1, an Anthropic model,
and asked whether it should review the engine and suggest improvements before the
independent audit.

**What was ruled.** Option A of three: the independent audit comes first; after it,
Fable 5.1 works on the list for after the audit. Not taken: (B) Fable reviews now and
everything it finds goes straight onto the list for after the audit, the audit plan
unchanged; (C) the closed list is reopened for what Fable finds.

**Claude's reasons, given before the ruling.**

- The closed list already sends anything found before the audit to the list for after
  it (DECISIONS, "Ruling, 22 September 2026 — when the audit resumes"). Fable's
  suggestions could not be built before the audit without reopening that list, and the
  auditor would then be checking new code nobody had reviewed.
- Suggestions and improvements are what the list for after the audit holds: the
  `bias_score` weighting, indicator changes, the range mode, the 3% floor.
- Fable is an Anthropic model, as Claude is. Claude's expectation — not tested — is that
  it shares many of Claude's blind spots, which makes it a weak second opinion on
  Claude's work; the independent audit, by another lab, is the real check. Using it costs
  no audit candidate: Anthropic is spent already.
- The best case for B was an early warning of a serious defect. The 2 September
  precedent (fix known defects before an audit rather than leave them for the auditor)
  would then have made reopening the list a deliberate decision, not a routine one.
- Cost was not the constraint. Fable 5.1 is priced at 10 USD per million input tokens
  and 50 USD per million output tokens, with no long-context surcharge (Anthropic's
  pricing page, read 29 September 2026). Claude's estimate for one pass over the ~400K
  full package was 5–7 USD. Its context window was not confirmed.

**What goes with it.** Fable is entered in the independence ledger at the time of use
(DECISIONS, 26 September); it reads the Constitution and the Assistant Instruction
first; its work reaches the repository as a patch under the normal gates, named in the
commit message.

**What it weakens.** The early warning is given up: a serious defect Fable might have
found before the audit is left for the auditor, or for Fable afterwards.

## Ruling, 29 September 2026 — the independent audit: now, by Laguna S 2.1, the full package in one session

*New in this file on 29 September 2026, filed with the twenty-third session's commit.
Ruled in chat in the twenty-second session, the same day, which landed no commit. This
entry and the two after it are filed from the record that session kept as it ruled —
the Phase 4 list of Viktor's roadmap document ("Phase 7 roadmap to the independent
audit", Claude Docs, outside the repository) — not from the chat, which the filing
session could not read. That record paraphrases Viktor, so nothing here quotes him.*

**What was ruled.** Two points, both by agreeing to Claude's suggestion — not by Viktor
writing his position first.

1. **Audit now.** The preparation starts now, and the package is sent when the
   preparation list is done (PHASE7_NEXT.md, Open items), at Viktor's pace. Claude's
   reasons, written in PHASE7_NEXT.md before the ruling: waiting does not save a lab;
   later re-audits of what changed can be scoped and go to the scoped-only labs; and
   fix-verification by the same auditor spends none (ruling of 14 September).
2. **The auditor is Laguna S 2.1, pinned to Poolside, and it is sent the full package
   in one session.** The package is not split. NVIDIA is kept for a smaller, scoped
   round later. Viktor had raised splitting the package in two so that an NVIDIA model
   could take it; he chose this after Claude's critique of the split. The critique's
   reasons are not in the record this entry is filed from, and are not reconstructed
   here.

**Nemotron 3 Super withdrawn — a correction.** Claude had recommended Nemotron 3 Super
(NVIDIA) first and Laguna S 2.1 second (PHASE7_NEXT.md at `ec4e5fd`, Open items), on the
model roster's figure of a 1M context. In the twenty-second session it was found that
OpenRouter serves Nemotron 3 Super at 262K, which cannot hold the package, and the
recommendation was withdrawn. The roster's model facts had not been checked since
22 September. The roster, outside the repository, is to be reissued with the correction
(PHASE7_NEXT.md, Open items). Whether NVIDIA's part in Mistral NeMo counts against
NVIDIA is moot for this round.

**What it rests on.** The package, with room for the answer, has to fit Laguna S 2.1's
context in one session. Measured on 29 September at `ec4e5fd` by character count, at
about four characters a token — not with Laguna's tokenizer — the full package is about
700K tokens: engine source ~150K, tests ~205K, the full commit messages ~300K, the
Constitution, the instruction and the history ~50K. That is not the ~400K+ this project
has used as the package's size until now. With the commit messages cut to those since
`e65a0f7` (the next ruling), the same estimate gives about 515K. Laguna S 2.1's 1M
context is the roster's figure, checked on 22 September and not since. The pre-send
token check (ruling of 26 September) is what confirms the fit before the send. No
fallback has been ruled for a package that does not fit.

**What it weakens.** It spends Poolside. After this round the roster's labs still clean
for a full round are NVIDIA, whose 262K cannot take the full package in one session, and
Amazon (Nova 2 Pro, a preview release).

## Ruling, 29 September 2026 — what the auditor sees, and no planted bugs

*Filed with the same commit, from the same record, as the entry above.*

**What was ruled.** Two points, both by agreeing to Claude's suggestion.

1. **The package goes in two messages.** The first carries Parts 1–6: the code, the
   tests, the Constitution, the instruction, the manifest, the version-control history
   as metadata only (no commit messages), and the execution transcripts. The second
   carries the Part 7 material, and is sent only after the auditor has saved Parts 1–6:
   the `bias_score` findings, the list for after the audit, any point of the
   15 September PDF still live in the code (moved back onto that list), and the commit
   messages since `e65a0f7` only — 82 commits, about 110K tokens instead of about 300K.
   The rest of the 20 September list is not shown.
2. **Nothing is planted.** The list for after the audit, held back until Part 7, is the
   test of the auditor: the real, dated defects Claude found and put on it, which the
   auditor is not told of while it writes Parts 1–6.

**The precedent.** It is the method ruled on 3 September (HISTORY, "Round 2, attempt
three — and what an unfinished audit found, 3 September 2026", "Rulings made
3 September 2026"): the auditor grades blind, saves Parts 1–6, and only then sees what
it is measured against. The alternative put to Viktor — bugs planted in a copy — would
measure whether the auditor finds a shape he chooses, at three costs: the package would
no longer be the repository's tree its SHA-256 manifest claims; the instruction would
have to say planted bugs may exist; and with about five seeds the result is rough
(three found of five fits anything from about 15% to 95%, the exact binomial interval).

**What it answers.** The question open since 20 September — whether the auditor is
shown the scrapped findings — is closed. The `bias_score` findings, which the ruling of
22 September said the auditor is shown, come in Part 7, so the auditor grades the
engine before it sees them. The rest of the 20 September list is not shown, including
the thesis half of its item (1), which the 22 September ruling left open.

**Moved back onto the list for after the audit by this ruling:** point 1 of the
15 September PDF. `models/decision_model.py:910` (at `ec4e5fd`) still turns the
confidence score into an assumed win rate, and the EV figure in R is computed from it.
Read from the code on 29 September. Points 3–5 are not yet traced (PHASE7_NEXT.md, Open
items).

**What still has to be done for it** (Claude's, before the send; PHASE7_NEXT.md, Open
items). `docs/build/send_audit_round.py` sends one message today, so it must be changed
to send two. Each item on the list for after the audit is checked against the code
comments and commit messages that ship with the package; an item they give away is
dropped; the usable set and the rule for scoring it are committed before the send.

**What it weakens.** The test is rough. The list holds about seven such defects, and
some are named in commit messages or code comments that ship with the package, so fewer
will be usable once the check above is done. Point 1 is one: its own docstring and a
20 September comment say what the figure is. And the Part 7 pass that compares plan
with execution sees 82 commit messages, not all of them.

## Ruling, 29 September 2026 — what opens backtesting

*Filed with the same commit, from the same record, as the two entries above. Ruled by
Viktor's position first: he wrote it, Claude critiqued it, and he agreed to the merged
version.*

**His position**, as the record gives it: backtesting can start when the engine is
functional, the fixes and patches after the audit are done, and a safety harness
exists, so that backtesting cannot break the engine.

**What was ruled — the merged version.**

*Backtesting may be built* once all four hold:

1. Items 2, 3, 6 and 18 of the Constitution are rated Compliant by the independent
   auditor, or each gap is fixed and the fix confirmed by the same auditor;
2. no Critical or Major finding is open, and every other finding is ruled;
3. every fix is confirmed by the same auditor;
4. Viktor declares it in this file.

*A backtest may be run* only once Goal B's harness — the write guard, the look-ahead
check, `cut_checkpoint.py` and the entry-point guard — is built and tested, and the
engine passes a known-good checkpoint.

*If the auditor finds fewer than half of the usable test bugs* (the ruling above), it
runs a second time before its Compliant ratings are trusted.

*The list for after the audit is not a condition.*

**The structural no-backtest guard.** Claude's point (2) of 21 September — the rule "no
backtesting before re-audit" exists only as text — is answered inside this ruling: the
entry-point guard is built with the first backtest code, as part of Goal B's harness,
not now.

**How the critique changed it** (compared by Claude at filing, from the two texts
above). "Functional" became four named Constitution items, rated by the auditor. "The
fixes done" became no Critical or Major finding open, every other finding ruled, and
every fix confirmed by the auditor. "A safety harness" became four named parts and a
known-good checkpoint, all already in Goal B (above, 15 September) except the
entry-point guard. Added: building and running are separate gates; Viktor declares the
first in this file; the auditor's ratings count only if it found at least half the test
bugs; and the list for after the audit is named as not a condition.

**What it settles.** The Constitution's backtest-start condition (Items 2, 3, 6, 18),
which "still stands as written" and was never declared met (ruling of 20 September), now
has a stated way to be met.

**Not settled by the record** (named at filing, not ruled): which model and package the
second run uses, if one is needed; and what counts as "usable" and as "found" — the
scoring rule is committed before the send (the ruling above).

**Claude's reading, not ruled.** Goal B's other preconditions — the 100-decision timing
benchmark, the fix to `PHASE7_PINNED_DATA`'s silent live fallback, the time cursor with
its negative control, the dataset build — stand as ratified on 15 September. This
ruling adds gates and removes none.

**What it weakens** (stated by Claude at filing; not in the record it is filed from).
The list for after the audit holds rules that change which trades are taken: the 3%
floor on T1, entering at the EMA band, a side that must hold for N closed candles.
Since the list is not a condition, the backtest may run before any of them is decided.
Under Goal B's re-run clause, the first out-of-sample evaluation is then the verdict of
record for the engine without them, and adopting one afterwards is a new phase with its
own pre-registration.

## Ruling, 29 September 2026 — six questions before the send

*New in this file on 29 September 2026, filed with the twenty-third session's second
commit. Ruled in chat the same session, the same evening. Points 1, 2, 4 and 5, and the
details added to point 3, by agreeing to Claude's suggestion: Viktor asked for Claude's
suggestion on each and agreed to all of them. Point 2 had been marked for his position
first; he chose to ask for the suggestion instead. Points 3 and 6 are his own answers.*

**How it came about.** Viktor asked whether every question needed before the audit had
been answered, and whether everything had been done to make the audit as useful as
possible. Claude's answer: the large questions were ruled earlier the same day (the
three rulings above); six smaller ones were not; and none of the twelve items on the
preparation list (PHASE7_NEXT.md, Open items) had started.

1. **The code is frozen at a tag.** The commit the package is built from is tagged,
   with a name that gives the round and the date of the send (for example
   `round7-sent-<date>`). Until the report is in and triaged, no commit touches engine
   code or tests; docs-only commits, such as recording the send or saving the report,
   are allowed. Before the send, Claude confirms that the package's file hashes match
   the tagged commit. Why: every line number and rating in the report then points at
   one exact tree, and each fix afterwards is checked against the tag.
2. **The auditor is given the intended behaviour, not the reasoning.** The instruction
   for this round carries, in Parts 1–6, a short list of what the engine is required to
   do — one plain line for each ruled behaviour, with no reasons and no history (for
   example "decide on the last closed candle", "a NEUTRAL bias prints no plan", "the
   stop comes from ATR alone") — and the list of files changed since `e65a0f7`, without
   the reasons. DECISIONS and the reasoning stay out. The instruction also asks the
   auditor to say where a requirement itself looks wrong, not only whether the code
   meets it. Nothing from the list for after the audit enters the requirements, because
   that list is the test. Why: the auditor can catch code that departs from a ruling,
   and will not report ruled behaviour as a defect, without reading the arguments for
   it. **What it weakens:** knowing the intent, the auditor may check the code against
   it instead of questioning it; the last instruction line is there against that.
   **How it fits the earlier rulings:** "what the auditor sees, and no planted bugs"
   (above) put the instruction in Parts 1–6; this says what the instruction carries and
   changes nothing else in that ruling. It meets the aim of the 21 September ruling —
   the change list as the auditor's scope, and the engine judged against stated
   intent — which the package as ruled earlier the same day did not carry. The code
   comments already carry part of the intent.
3. **The second pass is Laguna S 2.1 again, as many times as needed.** Viktor: "We run
   it twice as you said, or three times for that matter, doesn't matter to me." Added
   by agreeing to Claude's suggestion: each rerun is a fresh session that has not seen
   Part 7; each run is scored on its own, and Compliant ratings count only from a run
   that finds at least half the usable test bugs; if run after run stays under half,
   the fault is the model's, and the next step is another auditor, not another run.
4. **How the test bugs are scored.**
   - *Which count:* only the defects on the list for after the audit. The new trading
     rules on it — the 3% floor on T1, the range mode, entering at the EMA band, a side
     holding for N closed candles, renaming CONFIRMED — are design choices, not bugs.
   - *Usable:* still in the code as sent, and nothing in the package gives it away — a
     code comment, docstring or test name that names the problem. Each one ruled out is
     recorded with the line that gives it away. Two are out already, read from the code
     at `e7a94d1`: the 30.0 boundary (a comment at `models/decision_model.py:72`) and
     point 1 of the 15 September PDF (the docstring of `_compute_ev` says confidence
     stands in for the win rate).
   - *Found:* the auditor's saved Parts 1–6 name the same place (file and function) and
     the same thing going wrong. The right file with the wrong problem does not count,
     and nothing found after Part 7 counts.
   - *Rerun:* a run that finds fewer than half the usable test bugs is run again (with
     5 usable, 2 found means a rerun and 3 a pass).
   - *Locked before the send:* the list, each item's classification and this rule are
     committed before the send, so nothing can be adjusted after the report is read.
     Claude scores; Viktor checks.

   **What it weakens:** Claude wrote most of the code, chose the test bugs and scores
   them. The commit before the send is what stops the scoring from moving afterwards;
   Viktor's check is the rest.
5. **The instruction does not say that the ratings open backtesting.** The auditor
   should rate Items 2, 3, 6 and 18 the same way whatever follows from them. Knowing the
   consequence adds pressure one way or the other and gives it nothing it needs. The
   instruction says nothing untrue; it leaves the consequence out.
6. **No fallback is decided in advance for a package that does not fit.** Viktor: "I
   think it will run fine, if it doesn't we figure something out." If the token check
   fails, the next step is decided then.

**What it settles.** Both points the backtesting ruling (above) named as not settled by
its record: which model runs the second time (point 3), and what counts as usable and
as found (point 4). And the proposal to tag and freeze, open on the preparation list
(point 1).

**Checked the same day, for points 3 and 6** (read by Claude on 29 September).
OpenRouter's model page lists Laguna S 2.1 with 1,048,576 tokens of context, Poolside as
the only provider, up to 131,072 output tokens, and $0.09 / $0.18 per million input /
output tokens — well under 1 USD for one send, so reruns cost nothing that matters. That
is the page, not the live models API query round 6's send script used; the API query is
still to do at the send. Poolside's release post (21 July 2026) says, in one of its case
studies, that the model's knowledge cutoff is November 2025 — before this repository's
first commit (24 August 2026), so it cannot have trained on it. The model is small: 118B
parameters, 8B active per token. Poolside's long-context claims are about agentic coding
runs, not about reading ~500K tokens of someone else's code, which is why the test-bug
rule matters.

## Ruling, 29 September 2026 — the test bugs: four usable, and four is enough

*New in this file on 29 September 2026, filed with the twenty-fifth session's commit.
The classification below is Claude's, by point 4 of "six questions before the send"
(Claude scores, Viktor checks); Viktor checked it in chat ("I agree"). That four is
enough is Viktor's ruling: Claude put three options to him — four is enough; reopen
"plant nothing"; leave it open until the send — with no recommendation, and he chose
the first. He gave no written reasoning.*

**How it came about.** Items 7 and 6 of the preparation list (PHASE7_NEXT.md, Open
items), done in that order. Claude suggested them before the send scripts (items 3–5)
because they were the only items left whose result could reopen a ruling: "no planted
bugs" rests on the list for after the audit being the test. 7 came first because it
can add entries that 6 classifies. The order is Claude's under the delegation of
21 September; Viktor agreed ("Go.").

**Item 7 — points 3–5 of the 15 September PDF, traced.** Read from the PDF itself
(`Docs\02_Reviews_and_Feedback\Questions_on_Engine_Output_2026-09-15.pdf` in
`G:\Phase_7_Engine_Random_Files`, staged on 29 September) and from the code at
`59b747a`.

- *Point 3: "Boosting confidence by +10.55 points purely based on BTC correlation adds
  a major layer of complexity that has no baseline justification."* **Live.**
  `DecisionModel._compute_btc_adjusted` (`models/decision_model.py`) still moves a
  second confidence figure by up to ±20 points (`BTC_ADJUSTMENT_CAP`) and by −15 under
  broad market stress (`BTC_STRESS_PENALTY`); nothing in it has changed since the PDF.
  It decides nothing: `btc_adjusted_confidence` is read only by the router's merge
  into the record (`models/signal_router.py`, `_merge_btc_context`), the decision
  contract and the panel. Moved onto the list for after the audit.
- *Point 4: "The confluence multiplier applies a penalty (macro x0.90), but is a 10%
  reduction sufficient when trading directly against the macro trend?"* **Live.**
  `models/entry_model.py:384–385` still multiplies the entry score by
  `CONFLUENCE_PENALTY_MULT` (0.90) when macro opposes the trade, and no ruling has said
  whether that is enough. Since work order G macro no longer vetoes the CONSERVATIVE
  tier, so a trade against macro meets only this multiplier, the validation score's
  −20 and macro's 10% inside `bias_score` — the three places Work order G (above) read,
  unconfirmed with Viktor, as the 22 September ruling's "three penalties" item. Moved
  onto the list for after the audit.
- *Point 5: "VALIDATION : WEAK (Score: 5.00). What is this score out of?"* **Not
  live.** The panel has printed "/100" since `a9d4b1f` (20 September), through the one
  function every score line uses since work order B (`a530006`, 21 September). The
  PDF's second clause, a weak validation beside an 88.32 trend strength as "an internal
  conflict", is the design: since `101bb05` (30 August, sequence item 11) validation
  starts at 50 and moves only on macro and volume, never on trend health
  (`core/engine_core.py`, the VALIDATION block). The 5.00 was 50 − 20 (macro
  disagreeing) − 25 (volume divergence), which is the PDF's own panel.

**Item 6 — each entry checked against what ships.** What ships in Parts 1–6 is taken
from round 6's builder (`docs/build/build_audit_package.py` at `59b747a`): every `.py`
file outside `docs/`, five project files, the instruction, the Constitution's text,
the manifest, the history without commit messages, and the execution transcripts.
The shipped `.py` files were searched for each entry and for the phrases that mark a
deferred issue ("after the audit", "not fixed", "recorded, not changed", "open
question"); every line cited below was read at `59b747a`.

- *Not counted — new trading rules* (point 4's own list): entering at the EMA band; a
  side holding for N closed candles; renaming CONFIRMED; the 3% floor on T1; the range
  mode.
- *Not counted — not a defect:* point 4 of the PDF, which asks how large a weight
  should be — the class of question the 22 September ruling put after the audit. It
  would be out anyway: `models/decision_model.py:692` names the confluence multiplier
  among "the weighting questions ruled for after the independent audit".
- *Out — given away by a shipped line:*
  - checking the candles for bad data — `indicators/indicators.py:126`, "Checking the
    CANDLES for bad data is a different question and is on the list for after the
    audit";
  - nothing gates on HVN proximity — `models/entry_model.py:507–513` ("no gate checks
    HVN proximity … vetoes nothing. On the list for after the audit") and
    `tests/test_stop_is_atr_only.py:16`;
  - the 30.0 boundary — `models/decision_model.py:72` (out since `e7a94d1`);
  - point 1 of the PDF, confidence read as a win rate — `models/decision_model.py:899`,
    `_compute_ev`'s docstring (out since `e7a94d1`);
  - point 3 of the PDF, the BTC adjustment — `core/panel_render.py:676`, which prints
    "computationally validated, empirically unvalidated — no backtest supports this
    adjustment" under every BTC-adjusted confidence.
- *Usable — four:*
  1. **The risk gate runs before the bias checks** (`models/decision_model.py:551–553`,
     before `:656–668`). No shipped line names it.
     `tests/test_neutral_bias_prints_no_plan.py:272` asserts that a NEUTRAL grid gives
     exactly WAIT and NO-TRADE (RISK TOO HIGH), without calling it a problem; an
     auditor may read the behaviour as intended.
  2. **`lineage.risk_inputs` leaves out `trend_health`**, which sets the stop through
     `trend_factor` (`models/risk_model.py:335`). No shipped line names it; the ITEM 14
     comment inside the `risk_inputs` literal (`core/engine_core.py`) and
     `LineageBlock`'s docstring (`core/decision_contract.py:328–330`) say the
     opposite. It bears on Item 6, Traceability.
  3. **Under a NEUTRAL bias the entry score is measured for a side nothing chose**
     (`core/engine_core.py:1009`). No shipped line names it. Borderline: the same fault
     in the plan is described at `core/panel_render.py:357–370` (finding 5) — a
     pointer, not a naming, under point 4's rule.
  4. **The weak-validation WAIT decides nothing** (`models/decision_model.py:656–660`).
     No shipped line names it.

**What it means.** With four usable, a run that finds none or one is run again; two
or more is a pass (point 4: fewer than half means a rerun).

**What it weakens.** Three of the four change no trade — the risk gate's order changes
what the panel says, and the entry score and the WAIT decide nothing — so a careful
auditor may leave them out as cosmetic, and a miss is weak evidence that it cannot
see. The fourth is a gap in the record, on one of the four items that open
backtesting. Viktor accepted that by choosing "four is enough"; "no planted bugs"
stands.

**What it answers.** "Points 3–5 are not yet traced", in "what the auditor sees, and
no planted bugs" (above).

**Still to do before the send** (Claude's). The classification is checked again
against the package as actually built (item 3 moves the builder to this round) and
against rev 8 of the instruction (item 9). No requirement line in rev 8 may name any
of the four; "a NEUTRAL bias prints no plan" points the auditor at NEUTRAL panels,
where the third is. Any change is committed before the send, with the line that
causes it.

## Ruling, 29 September 2026 — the second request carries the first reply's reasoning

*New in this file on 29 September 2026, filed with the twenty-sixth session's commit,
which builds items 3, 4 and 5 of the preparation list. Ruled in chat the same session,
by agreeing to Claude's suggestion: Claude put the two questions to Viktor, he asked
"What is your suggestion?", and answered "Go." to it.*

**What was ruled.**

1. **The second request carries the first reply's reasoning**, not only its answer.
   Claude's reasons: Laguna S 2.1's chat template at `e80da38` shows every earlier
   reply's reasoning in full when a request carries it, and an empty `<think></think>`
   when it does not, so a request with it is the conversation the model is built for
   (read from the template); Part 7 compares the commit messages with the code the
   auditor read, and its reasoning is its notes from that reading; it is the auditor's
   own reasoning, so it costs no independence; and only the committed Parts 1–6 are
   scored, so it cannot move the score.
2. **Item 5 — the commit messages cut to those since `e65a0f7` — lands in the same
   commit as items 3 and 4.** The cut is one line in the function that commit already
   rewrites for the second message (`_full_messages()` in
   `docs/build/build_audit_package.py`); separately, that function would change twice
   in two commits.

**Claude's design under the delegation, put to Viktor before the build.** He did not
object to it. `--send` sends the first message alone; `--send-part7` refuses unless the
first reply finished with `finish_reason=stop`, was reported as served by Poolside, has
report content, is committed in git and unchanged since, and the first message rebuilds
to the bytes it was sent as. That puts a commit of the first reply between the two
requests — a docs-only commit, which the freeze allows ("six questions before the
send", point 1). It makes "Parts 1–6 are saved" a fact git records with a time, which
the scoring rule's "nothing found after Part 7 counts" (the same ruling, point 4) needs
in order to be checked.

**What was checked for it** (read by Claude on 29 September). OpenRouter accepts the
reasoning back as a `reasoning` string on the assistant message (its reasoning-tokens
guide). **Not checked:** whether Poolside's endpoint passes it on to the template. The
send's token check counts the second request with the reasoning and without it, and
records both; the provider's count afterwards (`native_tokens_prompt`) shows which one
the model was given.

**What it weakens.** The second request is longer by the reasoning, up to the 131,072
reserve; the check counts it exactly before the send. If Poolside drops the field
without saying so, the second request is answer-only, and that is found only
afterwards, from the counts. The reasoning may hold doubts the auditor set aside while
writing Parts 1–6, which it may take up again in Part 7: that cannot move the score,
since Part 7 is not scored for test bugs, but it can change what Part 7 says. And the
commit between the two requests is one more step in the send.

**Also recorded.** The correction owed with item 4 — rounds 5 and 6 sent the Part 7
commit messages in the same message as Parts 1–6 — is confirmed, from those rounds'
saved requests: HISTORY, "29 September 2026 — checked: rounds 5 and 6 sent the Part 7
file in the same message as Parts 1–6".

## Ruling, 30 September 2026 — rev 8 says nothing about this round's test

*New in this file on 30 September 2026, filed with the twenty-seventh session's commit,
which adds rev 8 of the instruction (item 9 of the preparation list). Ruled in chat the
same session, by agreeing to Claude's suggestion: Claude put three options to Viktor as
his call, he asked "What do you suggest?", and answered "Good, because i was looking at
B too. Agreed."*

**The question.** Rev 7 told the auditor twice that nothing was held back to test it —
"The fixes went in first" (Section 4a, about the eleven observations of 5 September) and
"none were held back to test you" (Section 9, about round 5's ten). For round 7 that is
no longer true: the list for after the audit is held back, and it is the test ("what the
auditor sees, and no planted bugs", 29 September). And the instruction says nothing
untrue ("six questions before the send", point 5).

**The options.** A — say it plainly, without content: some defects the project already
knows of are not fixed, they come in the second message, and Parts 1–6 are measured partly
on whether they found them. B — say nothing about this round's test, and narrow the two
old sentences so each speaks only of the round it describes. C — something else.

**What was ruled: B**, with one addition Claude proposed: Section 12 describes the second
message truthfully but neutrally — the commit messages, and "a document the project wrote
for the Part 7 pass" — without saying that its entries are unfixed or that they are a
test. The Part 7 document says so when it arrives.

**Claude's reasons.** (1) It is the principle of point 5: say nothing untrue, and leave
out what would only add pressure; knowing it is measured against a hidden list changes how
an auditor reads, which is the cost counted against planted bugs. (2) The auditor's task
does not change: Section 9 already tells it to expect defects. (3) Nothing stays hidden:
the second message says all of it, once Parts 1–6 are committed — the same sequencing as
the commit messages.

**What it weakens.** The auditor writes Parts 1–6 without knowing it is being measured,
and a reader could call that withholding. The answer on record: nothing untrue is said,
and it is disclosed in the same conversation, one message later.

**How rev 8 carries it** (Claude's drafting, which Viktor then read and approved).
Section 4a's paragraph on the eleven observations speaks only of that round; it had also
said the report would be compared with them, which is not planned for round 7, and that
is gone. The sentence "That is the situation, stated plainly, so that nothing in your
report has to be a guess about it" is gone, since the situation is no longer stated in
full. Section 9 says round 5's ten were "fixed and landed before round 6". And the Part 7
document is named `part7_material_PART7_ONLY.md` rather than `part7_findings_…`: its name
reaches the auditor in the first message, through the version-control history, once it is
committed (Claude's call under the delegation, in the same commit).

**Approved the same session.** Viktor read the draft of rev 8 and approved it: "I read it,
sounds great. I approve." That includes the scope of its requirement lines, which Claude
had put to him as his: the rulings since `e65a0f7`, plus three older ones the code
carries — direction from the bias score alone; degrade, don't halt; each run's input
hashed and its candles archived — so that the auditor does not report ruled behaviour as
a defect.

## Ruling, 30 September 2026 — the Part 7 document approved

*New in this file on 30 September 2026, filed with the twenty-eighth session's commit,
which adds the Part 7 document (item 13 of the preparation list). Claude drafted it;
Viktor read the draft and approved it: "I approve if you are satisfied also."*

**What was approved.** `docs/audit_package/part7_material_PART7_ONLY.md`, the document
the second message carries beside the commit messages. It holds what the ruling of
29 September on what the auditor sees requires — the `bias_score` findings, the list for
after the audit, and the points of the 15 September PDF, here all six, each with where
it stands — and opens as the first ruling of 30 September requires: what it is, and that
its entries were known to the project and held back until Part 7 on purpose. It tells
the auditor the whole scoring rule, the threshold and the rerun, who scores (Claude,
which wrote the code and chose the entries) and every entry's classification, since
Parts 1–6 are committed before it is sent; and it asks the auditor to challenge any
classification it disagrees with.

**What it adds to the scoring rule** ("six questions before the send", point 4; "the
test bugs", above). Claude's under point 4, Viktor checking; put to him as the part to
check most closely.

1. **What "found" means, for each of the four test bugs:** the place (file and function)
   and the fault, one sentence each. It narrows the 29 September wording, "the same
   place and the same thing going wrong". Two allow more than one name for the place:
   the second (the `risk_inputs` block in `Phase7Engine.run`, or the same lineage as
   `LineageBlock` describes it) and the third (the entry-quality direction in
   `Phase7Engine.run`, or `calculate_entry_quality` as called from it).
2. **Two entries added on 30 September, classified:** "ROUND 6" in seven test comments —
   not scored, since the shipped line is itself the defect; and the always-true
   comparison below — not scored, since it changes nothing observable. Four usable
   stays four.

**Found while writing it.**

- **An always-true comparison.** `calculate_entry_quality` (`models/entry_model.py:384`,
  at `01f2892`) tests `macro_bias != trade_direction`, two vocabularies that never
  match. The branches above it catch agreement and the engine passes only BULLISH,
  BEARISH or NEUTRAL, so the result is right for every value a caller passes. On the
  list for after the audit (PHASE7_NEXT.md).
- **Point 2 of the 15 September PDF had never been traced by the preparation list.**
  Item 7 traced points 3–5 ("the test bugs", above) and point 1 was read on
  29 September; point 2, "triple volume accounting", was not taken up. The code had
  answered it on 20 September, in the comment at `models/bias_engine.py:62–89` (from
  `a9d4b1f`). Read again from the code on 30 September: the panel's "Vol:" field is
  volatility (ATR over price, `calculate_dynamic_regime`), not volume; volume sentiment
  reaches `bias_score` and the validation score, and volume reaches the entry score
  through the VWMA distance. What is left open is that comment's own question, "whether
  three separate penalties for one disagreement is the right total weight". **Claude's
  reading, from the matching words, Viktor's to correct:** that comment is the source of
  the 22 September ruling's item "one volume/macro disagreement adding up to three
  penalties", which this file recorded on 26 September as not found as a finding, and
  which Work order G read, unconfirmed, as macro's three places. The comment names both
  volume and macro; G's reading is its macro half. The Part 7 document gives the auditor
  both halves (its Section 4, item 4).
- **Items 3, 4 and 5 of PHASE7_NEXT.md's preparation list** still said "the commit that
  writes this line" at `01f2892`, carried unchanged from `12b483e`, where they landed.
  Corrected in the new version; the version moved into HISTORY is left as it was, with a
  note in its header.

**Corrected after the approval.** Re-reading the approved draft before building the
patch, Claude found three statements that were not accurate and corrected them. Viktor
sees the corrected document before he applies it.

1. The opening said the first message "did not point you to any of them" and that four
   entries are not named in the code. The first message does name some of them, in the
   code comments Section 3.2 cites, and more than four are unnamed: the always-true
   comparison is too. It now says that some are named in comments, and that four of the
   others are what Parts 1–6 are measured against.
2. Section 1 said every entry was found between 26 and 30 September and deferred under
   the 22 September ruling. Three — the three points of the 15 September PDF on the list
   — come from 15 September, were set aside with the open items on 20 September, and
   were moved onto the list on 29 September. It now says so.
3. "for the reason above" became "for the reasons above".

**What it weakens.** The four "found" sentences are Claude's, written by the party that
scores; a sentence drawn too narrowly would make a real find not count. Viktor's check
is what stands against that, and the auditor is invited to say so in Part 7 — after
Parts 1–6 are fixed, so it cannot move the score. The citations are line numbers at
`01f2892`: the document tells the auditor the engine code and tests have not changed
since, which item 10 must confirm at the tag.

## Ruling, 30 September 2026 — what follows round 7's first reply

*New in this file on 30 September 2026, filed with the thirty-first session's commit,
which changes the send script this ruling calls for. Points 1–4 by agreeing to Claude's
suggestion: Viktor asked for Claude's suggestion on the three questions PHASE7_NEXT.md
left open after round 7's first reply, and answered "Agreed." to all of them and to a
fourth that Claude raised. He did not write his position first. Point 5 is his own
choice between two options Claude put to him, one of them marked as Claude's
recommendation, which he chose. He also confirmed he had checked Claude's scoring
(below).*

**How it came about.** Round 7's first message went to Laguna S 2.1 on 30 September
(PHASE7_NEXT.md, the thirtieth session). The reply rated all 44 rules Compliant, found
nothing, and named none of the four test bugs. Poolside's own generation record shows
0 reasoning tokens: 3,626 completion tokens in 52 seconds, on 455,360 prompt tokens.
The request had not asked for reasoning. Three questions were left open for Viktor:
whether Part 7 goes to this run, whether the rerun goes unchanged or with reasoning
requested, and whether a run with no reasoning counts under point 3 of "six questions
before the send" (above).

**The scoring, checked.** Claude re-scored the reply on 30 September from the committed
`turn1_report.md`, against the four "Found means" sentences of the Part 7 document
(Section 3.1). Part 2 of the reply has no finding, so nothing in it names both the place
and the fault of a test bug. Two near misses both fail the rule. Line 84 names
`_determine_final_action`, the function where S1 and S4 are, only to call its direction
source correct. Line 92 (Item 14) is in S2's area, but it repeats the claim of the ITEM 14
comment that S2 says is misleading, and never mentions `risk_inputs` or `trend_factor`.
"NEUTRAL" and "entry quality" (S3) appear nowhere. **0 of 4.** Viktor checked it (asked
in chat: "Yes, I checked it"). Under point 3 of "six questions before the send", run 1's
Compliant ratings do not count.

**What was ruled.**

1. **Part 7 does not go to run 1.** The score comes from Parts 1–6 alone, so Part 7
   cannot change it. The run's Compliant ratings already do not count, so there is no
   audit for Part 7 to finish. What Part 7 would add is the run's view of the list for
   after the audit, from a run that spent 52 seconds and no reasoning on 455K tokens.
   `turn1_run_metadata.json` stays as the send wrote it, with no provider in it;
   `turn1_generation.json`, fetched afterwards, is the provider record.
   **What it weakens:** a cheap look at how Laguna reads Part 7, and which test bugs it
   would claim, is not taken.
2. **Run 2 asks for reasoning, and nothing else changes.** The same first message,
   checked by its hash against run 1's `1b8b8095…`; the same instruction; the same
   pins. Unchanged, it would most likely repeat run 1, since the request is the only
   thing the project controls. OpenRouter's endpoint listing names `reasoning` among
   Laguna S 2.1's supported parameters (read on 29 September and again on 30 September,
   the second time through a web tool; the sandbox's direct call was refused by its
   proxy). Whether Poolside's endpoint acts on it was not checked, so a one-line probe
   goes first, and the real send is refused unless the probe's reply shows reasoning
   tokens above zero. The generation lookup is lengthened in the same change, since the
   failure that left run 1 with no provider on record would block Part 7 after a
   passing run 2 as well. **The freeze has one exception:** `tests/test_send_audit_round.py`
   may change while engine code and tests are frozen (point 1 of "six questions before
   the send"). It tests a script that is not part of the engine and is not in the
   package, and run 2 sends the first message by its hash from the tag, so the report
   still points at one exact tree. The other option, the script changed and its test
   owed until after triage, would cut verification. **What it weakens:** the freeze
   gets its first exception, and `tests/` on `master` differs from the tag's in that
   one file until the report is triaged. `docs/audit_package/round7/MANIFEST.md` keeps
   the file's hash as it was sent.
3. **Run 1 counts as a run.** It was the ruled package, sent to the ruled model and
   scored by the rule committed before the send. Leaving it out now that it scored 0 of
   4 is the adjustment after the fact that committing the rule first exists to prevent.
   It is recorded as run 1: no reasoning requested, 0 of 4.
4. **Two runs in all.** Point 3 of "six questions before the send" said "if run after
   run stays under half, the fault is the model's", with no number. Each further run of
   the same model raises the chance that a shallow run passes by luck, and a passing
   run's Compliant ratings are then trusted. As an illustration only: a run that passes
   by luck one time in five passes at least once in three tries about half the time
   (1 − 0.8³ ≈ 0.49). So if run 2 also finds fewer than two of the four, the next step
   is another auditor, not a third run. **What it weakens:** Laguna gets one run with
   reasoning requested; a model that might have passed on a third try is dropped.
5. **What counts as a run** (Viktor's choice of two options; Claude recommended this
   one). Any send that left a reply on record counts, a reply cut off at the output
   ceiling included: the ceiling is the model's own maximum, 131,072, so a cut-off is
   the model's limit, not the setup's. A send that fails before any reply comes back,
   such as an HTTP error, does not count. The other option counted only replies that
   finished normally, which would let a model gain tries by running out of room.

**How the script carries it** (Claude's design under the delegation of 21 September,
put to Viktor before it was built; he did not object). `docs/build/send_audit_round.py`:
every request asks for reasoning (`reasoning: {"enabled": true}`); `--send` sends a
probe first and refuses unless it shows reasoning tokens; `--send` refuses a third run,
counting any folder that holds `turn1_run_metadata.json` or a non-empty
`turn1_report.md`; it refuses a first message whose hash differs from any earlier
run's; run 2 goes to `round7_laguna-s-2.1_run2_<date>/`, and a folder holding a reply is
never written over; `--out-dir` and `--force` are refused with `--send`; run 1's folder
is closed, so `--send-part7` never continues it, even when it is named; and the
generation lookup waits about five minutes instead of about 44 seconds. The commit
message has the tests and their negative controls.

**What it does not settle.** Which auditor comes next if run 2 also fails. Point 6 of
"six questions before the send" leaves the like question to be decided when it comes
up, and so does this one. Why run 1's generation lookup failed was not found.

## Round 7 ended, 30 September 2026 — run 2 found 0 of 4

*New in this file on 30 September 2026, filed with the thirty-first session's second
commit, which commits run 2's reply. Nothing new is ruled: this applies point 4 of
"Ruling, 30 September 2026 — what follows round 7's first reply" (above). Claude scored
run 2 and Viktor checked the score (asked in chat: "Yes, checked").*

**Run 2.** Viktor sent it on 30 September at 11:43 UTC, from the same package, with the
send script as changed at `3e8191a`. The probe's reply showed 1,102 reasoning tokens and
the answer 408. The reply itself came from Poolside and finished normally after 45
seconds: 4,415 completion tokens, 2,166 of them reasoning, and 455,360 prompt tokens. Of
those, 455,328 were served from the provider's cache of the identical first message,
which run 1 had sent less than two hours earlier. That cache holds the prompt; run 1's
reply was never part of this prompt. Cost: $0.0049. The generation lookup found the
record within its tries. The files are in
`docs/audit_reports/round7_laguna-s-2.1_run2_2026-09-30/`.

**What it said.** 42 rules Compliant; Item 11 Partially compliant (Major), because four
of the six bias factors read the direction of close; T3-1 Not verifiable; the release
gate met. It named itself "Poolside's Meta-Muse Spark 1.3". Its reasoning says that, for
a package this size, it would "focus on the most critical parts".

**The score: 0 of 4.** Scored from the committed `turn1_report.md`, against the Part 7
document's four "Found means" sentences.

- S1 and S4: `_determine_final_action` is not named.
- S2: `risk_inputs` and `trend_factor` are not named. Its one mention of trend_health
  (Part 6, point 1) repeats the claim of the ITEM 14 comment, which S2 says is
  misleading.
- S3: "NEUTRAL" and "entry quality" are not in the report. The reasoning file holds one
  near miss: "since the code allows for a NEUTRAL bias to still reach a side". It is
  written about Item 11, names no file or function, and is not about the entry score.
  The reasoning is not Parts 1–6 in any case.

The Item 11 finding is not a test bug. The shipped comment in `models/bias_engine.py`
names the overlap (it has since `e2c6637`), the reply itself says so, and it is one of
the `bias_score` findings the Part 7 document carries.

**What follows, as ruled.** Two runs, both under half: round 7 has ended. Neither run's
Compliant ratings count, and neither does either run's verdict on the release gate. Part
7 was sent to neither run. The next step is another auditor, not a third run (point 4).
Run 2 is closed in `send_audit_round.py` like run 1, because the script cannot know a
score; `--send` already refuses a third run.

**Open, Viktor's.** Named here, not ruled:

- the next auditor;
- whether it is sent the same package, built from the tag `round7-sent-2026-09-30`, or a
  new build;
- with that, whether the freeze of point 1 of "six questions before the send" holds
  until that auditor's report is triaged. As written, the freeze lasts "until the
  report is in and triaged", and round 7 produced no report that counts.

**What the result does not show.** The measure has not yet been tried on an auditor that
does the work. Two runs of one small model (8B active parameters per token) found none
of the four. That says this model did not do the work; it does not yet show that the
four test bugs can be found by a model that does.

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
