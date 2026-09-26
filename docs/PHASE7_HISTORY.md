# Phase-7 — dated history

*Created 18 September 2026, by mechanical split of docs/PHASE7_NEXT.md (see that
file's own head block and this patch's commit message for the reconciliation proof).
Everything in this file is verbatim content moved from docs/PHASE7_NEXT.md, in its
original relative order, with no line added, removed or reordered. Two sub-orderings
are both preserved exactly as they existed in the source: the head-block archive
immediately below runs newest-first (each patch was prepended above the last), and
everything after it runs oldest-first (each dated section was appended below the
last). This file is append-only going forward — new entries are added at the end,
oldest-to-newest, matching the second convention. Read this file when a question
calls back to a specific date, patch or audit round; it is not meant as routine
orientation. docs/PHASE7_NEXT.md is the entry point for current state;
docs/PHASE7_DECISIONS.md holds the standing rules and ratified specifications that
remain in force.*

---

# Next step — read this first

*15 September 2026 (twenty-fourth patch, docs only) — **Goal B is specified and ratified
before any backtesting code exists.** New permanent section, "Goal B — the backtesting
phase, specified before it starts," below under "Two goals, and the order they finish in."
Read that section; this entry is a pointer and a record of how it was decided, not a
repeat of it.

- **How it was decided.** Same shape as the portfolio-ready declaration: Viktor wrote his
  own position on each governance question first, Claude critiqued it, corrections were
  folded in, and Viktor ratified. Four rounds — the checkpoint/rollback/isolation rules,
  the fixed evaluation dataset, the pre-registered verdict thresholds, and the completion
  boundary. The final call on the remaining open points was explicitly delegated to Claude
  ("make the changes you want and are content with... it is your call"), and the reasoning
  for each is recorded in the section rather than only in chat.
- **What it closes.** The two questions carried forward unanswered since the
  twenty-first-patch entry below — what "known-good checkpoint" and "fixed evaluation
  dataset" concretely mean for this project — are both now answered, along with three
  things that were never on the list: the pre-registered verdict procedure, the completion
  boundary that ends the phase, and the re-run clause that stops a negative verdict being
  quietly re-litigated.
- **Three findings from reading the code, not the documents.** `PHASE7_PINNED_DATA`
  silently falls back to the live API when the environment variable is set but does not
  resolve to a directory (`data/data_fetcher.py::pinned_source()` returns `None`, and
  `None` means live) — still open, now a named precondition of goal B. The eval dataset is
  three series per run, not one file, so the multi-timeframe alignment rule (truncate by
  candle open time, never close time) is the highest-risk line in the whole phase. And
  `_load_pinned` already tails to `limit`, so the harness is a time cursor on the existing
  pinned path rather than a new data pipeline — a much smaller build than first scoped.
- **Two of Claude's own errors are recorded in the section itself**, both the same shape:
  asserting from this file's narrative instead of from the code. The lookahead sweep Claude
  said had never happened (`793e863`, 30 August, with `tests/test_no_lookahead.py` already
  pinning it), and `fc35a2f` described as a reusable precedent without reading it. Standing
  mitigation adopted for goal B: every claim about the codebase's state states whether it
  came from reading code or from a document.
- **Not started, and deliberately so.** No goal B code exists yet. The precondition order
  in the new section begins with a 100-decision-point timing benchmark, because whether a
  backtest takes minutes or hours decides whether walk-forward is affordable at all, and it
  costs almost nothing to find out first.
- **`code_hash` unaffected** — this patch touches only `docs/PHASE7_NEXT.md`, under
  `docs/`, which `core/code_fingerprint.py` excludes from its file walk by directory name.
  Confirmed on both trees, not assumed. No engine module or test touched, so the golden
  snapshot does not apply.

---
*Prior head block (15 September, twenty-third patch) kept below for history.*


*15 September 2026 (twenty-third patch, docs only) — **Engineering Notes regenerated
through Entry #127 (v1.30), landed `bd44b98`.** Batched regeneration Viktor chose himself
at this session's start, over two other open items (writing his own position on the two
Goal B definitional questions; the unrelated YH-programme question) — both of those
remain untouched and still open.

- **What changed.** Nine new entries (#119 through #127) appended to
  `docs/build/build_engineering_notes.py`, one per logical unit of work in the ten commits
  landed between `293f310` (v1.29) and `a441023` — the Portfolio Document, the
  AI-Attribution Statement, this file's own currency fix for both, the five token-saving
  rules' in-repo copy, the mutant-escape-findings correction, the release-gate/
  portfolio-ready/`portfolio-v1` declaration, the session-handover script, the README.md
  fix plus the stray-file finding and backtesting-scoping carry-forward, and the
  README-currency check (item 8). One new Document History row (v1.30) summarizing the
  batch, matching every prior version row's own style and per-entry citation pattern.
- **Verified, not assumed, on both platforms.** `code_hash` confirmed unmoved —
  `38458f20779d2709ed6402c69407339f797c69089ace3b18922ca5c8bb289fbb` — on the pristine
  tip, the edited tree, and a fresh independent clone with the patch applied, all three
  identical; `docs/` is excluded from `core/code_fingerprint.py`'s file walk by directory
  name and neither changed file sits outside it. Golden snapshot not applicable — no
  engine module touched. Full three-configuration suite run twice in the Linux sandbox
  (466 passed / 338 passed, 117 skipped / 395 passed, 0 failed, 32 pre-existing errors,
  diffed by name against baseline, not just counted) and confirmed a third time on
  Viktor's own machine before he committed — first Windows confirmation of this
  particular build script's output since it was created.
- **This document's own currency gap, closed by this entry.** The Engineering Notes had
  carried a ten-commit gap since `293f310` (v1.29), named explicitly in the
  twenty-first-patch entry below and left untouched through the twenty-second. That gap
  is now closed; the next one starts accumulating from here.
- **`code_hash` unaffected by this entry either** — this patch touches only
  `docs/PHASE7_NEXT.md`, under `docs/`, excluded from the fingerprint walk by directory
  name. No engine module or test touched, so the golden snapshot does not apply.

---
*Prior head block (15 September, twenty-second patch) kept below for history.*


*15 September 2026 (twenty-second patch) — **The handover script gets a README.md
currency check (item 8); the "ignored-file sweep every time" half of the same open
question closes with no code change.** Viktor named the split himself — the checkpoint/
dataset questions are his to write, this one is Claude's engineering call — then said
"Yes. Fix this."

- **What changed, in `docs/build/session_handover_check.py`.** One new function,
  `check_readme_currency`, printed as `## 5.` in the script's output: README.md's
  last-touched commit (hash, date, subject), HEAD's own, and the commit count between
  them. Informational only — it does not feed the script's exit code, the same way the
  four "still manual" reminders don't, because whether README.md's *content* still
  matches what this file's head block declares is a judgment call, not a git fact. What
  the script now removes is the reason that judgment call went unmade for sixteen days
  (README.md last touched 30 August, fixed at `ebb0a46` on 15 September): nobody ran
  `git log` on README.md to see how old it was.
- **The other half of the open question needed no code change.** Whether the
  ignored-file sweep should run "every time" was already answered by the script's own
  existence: `## 2.` (`check_ignored_files`) runs on every invocation, unconditionally,
  since the twentieth patch created it. The stray `*_commit_message.txt` file the
  twenty-first-patch entry found slipped through because the script itself didn't run
  that session (no shell access to Viktor's machine), not because its sweep logic was
  incomplete. Stated plainly rather than silently adding a redundant check to look
  responsive.
- **This file's own "Working practice" checklist gets item 8** (below), matching the
  script: README.md currency, printed automatically, judged manually, the same as items
  1, 2, 4 and 6.
- **Verified, not assumed.** Three scenarios run against a throwaway git repo: a clean
  tree with README.md one commit behind HEAD; a stray commit-message file plus an
  ignored file plus a staged index together, to confirm the new check doesn't disturb
  the existing flagged/clean logic; and a repo where README.md has no commit history at
  all, to confirm the new check degrades gracefully instead of raising. All three
  produced the expected output and exit code. The patch itself was verified the same way
  every patch in this file is: `git apply --check` then `git apply` against a pristine
  copy of the file re-staged off Viktor's disk immediately before building the diff (md5
  confirmed identical to the disk copy before patching, and to the intended new version
  after), CRLF preserved (240/240 lines, no LF-only lines, before and after), and
  `python -m py_compile` confirmed on the applied result.
- **`code_hash` unaffected** — `docs/build/session_handover_check.py` sits under `docs/`,
  which `core/code_fingerprint.py` excludes from its file walk by directory name, checked
  directly in that file's own `EXCLUDED_DIR_NAMES` rather than assumed from precedent. No
  file outside `docs/` touched.
- **Test suite: not re-run, and that's a scoping call, not a skip.** This script has no
  pytest coverage — `tests/` has no `test_session_handover_check.py`, checked by listing
  the directory — and nothing under test imports it; it's invoked by hand, not by the
  suite. Nothing in `tests/`, `core/`, `indicators/`, `utils/`, `models/`, `structure/` or
  `data/` was touched, so there is nothing under test this patch could have moved; the
  usual three-configuration run was skipped as inapplicable, not disproportionate.
- **Platform.** Built and verified in the Linux sandbox only, same as the script's
  original twentieth-patch delivery. No shell access to Viktor's machine this session
  either, so this stays Linux evidence for `git apply` / `py_compile` / the three
  throwaway-repo runs. Nothing added is OS-conditional (no path handling, no
  platform branches), so there's no specific reason to expect a difference on his
  machine, but that expectation is unconfirmed until it runs there once applied.

---
*Prior head block (15 September, twenty-first patch) kept below for history.*


*15 September 2026 (twenty-first patch, docs only) — **Session close: the README fix
logged here for the first time, a stray leftover delivery file found, and today's
backtesting-scoping findings carried forward so they survive into the next session
rather than living only in chat.** Run at Viktor's request, starting a new chat.

- **README.md fix, landed `ebb0a46`, never logged in this file.** Found while starting
  to scope backtesting: `README.md` had not been touched since 30 August (`881df1d`) and
  still said the release gate was shut, contradicting the 15 September declaration.
  Fixed in its own patch, verified `code_hash`-neutral (README.md sits outside
  `core/code_fingerprint.py`'s file walk entirely) and against the full suite (466
  passed, unchanged). Viktor's own correction, recorded plainly rather than smoothed
  over: this was not a case of him failing to ask for document checks — the standing
  handover check has never covered `README.md`, only this file, the Engineering Notes,
  and `git status`. That checklist gap is not fixed by this patch; see below.
- **A stray delivery leftover, found by hand-checking what the new handover script
  checks.** No shell access to Viktor's machine this session, so the check ran as a
  direct directory listing instead of a live script run. It found
  `phase7_mutant_escape_correction_commit_message.txt` sitting at the repo root,
  gitignored (`*_commit_message.txt`) and therefore invisible to `git status --short`.
  Its mtime (14:41) sits two minutes before the `f7f2e51` object was written, so it is
  very likely that patch's own commit-message file, never deleted per step 11 of its
  numbered delivery sequence. This is a second, live instance of the exact blind spot
  this file's own lessons already name (reviewer responses once sat unnoticed the same
  way) — confirmation the class recurs, not a new lesson. Not deleted by Claude; Viktor
  should `del` it himself, same as any other delivery artifact. Everything else in the
  tree checked out clean: no other loose `.patch`/`*_commit_message.txt` files anywhere,
  nothing else with an out-of-place recent timestamp.
- **The handover checklist's own scope is now a named, undecided question.** It covers
  `PHASE7_NEXT.md`, the Engineering Notes, and git state — never `README.md`, and (per
  the finding above) its git-based checks can still miss a gitignored straggler unless
  someone runs the `--ignored` check specifically. Whether to add `README.md`, and
  whether the routine should include an explicit ignored-file sweep every time rather
  than only when Claude happens to do one by hand, are open — not decided this session,
  named here so they are not lost.
- **Backtesting-scoping findings from today, carried forward, nothing acted on.**
  Viktor chose to start scoping Goal B this session; here is what the scoping so far
  found, for whichever session picks it up next:
  1. The Constitution's backtest-start condition — Items 2, 3, 6 and 18 all Compliant —
     is a separate clause from the release gate and has not been formally re-checked or
     declared the way the release gate was on 15 September. Evidence points to it
     already being satisfied (all four items independently resolved), but nobody has
     said so the way Viktor said "the gate is open" for the release gate.
  2. Item 17 (Backtesting Must Be Isolated) is the actual design constraint for whatever
     gets built: not an unbreakable backtester, a blast radius — a failure must never
     corrupt, destabilize or redefine the live engine, and when it fails it must be
     possible to isolate what broke and return to a known-good state without ambiguity.
  3. A real precedent for exactly what Item 17 guards against: a 6 September finding
     (GLM, F-1) in the old `indicators.py::pct_slope` — `.bfill()`-contaminated rows,
     harmless only because the decision path always reads the newest bar, and "a
     backtest harness walking the decision timestamp backwards would reach it with no
     code change" (the report's own words). Already fixed (`4d56f2a`, `pct_slope`
     removed entirely, confirmed gone from current code) — but proof the defect shape
     exists in this codebase, and nothing has ever swept for other instances of it on
     purpose.
  4. Two questions put to Viktor, per his own standing preference to write a governance
     position himself before Claude critiques it, not yet answered: what "known-good
     checkpoint" and "fixed evaluation dataset" concretely mean for this project.
- **Engineering Notes gap, stated rather than closed on reflex.** Last regenerated at
  `293f310` (v1.29, 14 September). Five docs-only commits have landed since (the
  sixteenth through this, the twenty-first, patch) without a fresh regeneration, per the
  batching rule adopted 15 September — this is that rule working as intended, not
  neglect, but the gap should say so rather than go unmentioned.
- **`code_hash` unaffected** — docs-only, confirmed against a fresh clone, not assumed.
  No engine module touched by anything this entry records; the golden snapshot does not
  apply.

---
*Prior head block (15 September, twentieth patch) kept below for history.*


*15 September 2026 (twentieth patch) — **A manual session-handover check script,
`docs/build/session_handover_check.py`; a proposed auto-pruning mechanism for the Lessons
list, declined.** Viktor read an unrelated agent-harness project (ECC) and asked for
critical feedback on two of its own components he thought worth adopting, then delegated
the final call: "It is your call, do what is best for the engine and the project."

- **Adopted, in modified form.** The handover checklist below has been an instruction ("run
  these seven checks") rather than a structural fact of the repo — Viktor's own standing
  preference is a structural fix over a reminder to be careful. `docs/build/session_handover_check.py`
  now runs four of the seven checks by command rather than by memory: untracked/modified
  files, ignored files (filtered for routine build/cache noise, so a real signal like the
  reviewer-response incident this file already documents isn't buried under `__pycache__`
  entries), loose `.patch`/`*_commit_message.txt` files, and a staged-but-uncommitted index.
  The other three — is this session's state written into this file, are today's rulings
  recorded, are the Engineering Notes current or the gap stated, is anything still only in
  chat — ask whether specific prose is accurate, which needs judgment, not a git command;
  the script prints them as a reminder rather than pretending to answer them.
- **Not automatic, and said so rather than overclaimed.** ECC wires this kind of check to
  Claude Code lifecycle hooks that fire inside a persistent session. This project's actual
  workflow is single commands run one at a time in `cmd.exe` with no such session to hook
  into, so the script is invoked by hand at session close — same cadence as before, computed
  instead of recollected, not the automatic version ECC gets.
- **Declined: an "instinct"-style confidence-scored auto-prune for "Lessons carried
  forward."** Two reasons, not one. It conflicts directly with this project's own standing
  rule that wrong turns are recorded rather than quietly corrected — pruning is quiet
  removal. And recurrence count is not a proxy for importance: the `git add -A` trap
  stopped recurring specifically because it was fixed structurally (`214c5d8`'s `.gitignore`
  rule), so a recurrence-based prune would delete exactly the lessons that worked, first.
  No change made to that list.
- **The other four ECC components Viktor's own proposal had already declined** —
  verification-loop/eval-harness, the `rules/` folder, multi-agent orchestration, the broad
  skill catalog — are confirmed correct and left as-is; nothing to add there.
- **Verified before delivery, not assumed.** All four detectors in the script were run
  against deliberately introduced test conditions (a stray `.patch`/commit-message pair, a
  staged file) and confirmed to actually fire, then the test scaffolding was removed and the
  tree confirmed clean again.
- **`code_hash` unaffected** — the new file lives under `docs/build/`, excluded from
  `core/code_fingerprint.py`'s file walk by directory name; computed on the pristine and
  patched trees and confirmed identical, not assumed. No engine module touched, so the
  golden snapshot does not apply to this patch.
- **Test counts (Linux sandbox, Python 3.12.3), re-run before this change and confirmed
  unchanged after it, since none of it touches engine or test code.** pytest with
  `pandas_ta` 466 passed; pytest without it 338 passed / 117 skipped; `run_tests.py` 395
  passed / 0 failed / 32 errors (32 pre-existing, unrelated to this patch).
- **Platform.** Built and verified in the Linux sandbox only. `pathlib`/`subprocess`/`git`
  behave the same on Windows for what this script does, so there is no specific reason to
  expect it to fail there, but that expectation is not yet confirmed — run it once applied
  and paste the output back, both to confirm it works on your machine and to get its first
  real reading.

---
*Prior head block (15 September, nineteenth patch) kept below for history.*


*15 September 2026 (nineteenth patch, docs only) — **The release gate is declared open
and the project portfolio-ready.** Viktor's ruling, recorded in full under "Declared —
15 September 2026" (below, under "Two goals, and the order they finish in"). Read that
section for the reasoning; this entry is a pointer, not a repeat of it.

- **What this does and does not do.** Closes the one item the sixteenth through
  eighteenth patches all left open: whether criterion 1 counts as met, whether to declare
  portfolio-ready, and whether to tag. The first two are now yes, recorded above with
  reasoning. The tag (`portfolio-v1`) is a separate, following commit — this patch does
  not create it, so the tag should point at a commit at or after this one, never before.
- **code_hash unaffected** — docs-only, confirmed against a fresh clone, not assumed.
- **Verification scope, stated plainly.** Pure prose recording a ruling already made in
  chat; no code or test file touched. Full suite re-run skipped as disproportionate,
  matching the eighteenth patch's own precedent for a documentation-only change.

---
*Prior head block (15 September, eighteenth patch) kept below for history.*


*15 September 2026 (eighteenth patch, docs only) — **The five round-6 mutant-escape
findings (requested-run 6, GPT-6 Astra) were already closed at `044b055` (12 September)
and this file never said so.** Found while scoping a request to fix them: they turned
out to already be fixed, verified, and folded into round 6's audit batch. This entry
corrects the record rather than re-doing work already done.

- **What `044b055` actually did, never spelled out in this file before now.** All five
  mutant-escape findings from requested-run 6 closed in one commit: `compute_trend_health`'s
  always-neutral escape (`tests/test_trend_direction_source.py`), `_determine_final_action`'s
  always-WAIT escape (`tests/test_timeframe_disagreement.py`), `plot_engine_chart`'s no-op
  escape on both affected tests (`tests/test_frame_ownership.py`), `SignalRouter.route`'s
  canned-error escape (`tests/test_smoke.py`), and `run_tests.py`'s zero-match-exits-0 bug
  (fixed in `run_tests.py` itself, with a new `tests/test_run_tests_filter_matching.py`).
  Each mutant reproduced in-process, confirmed to escape the old test, confirmed caught by
  the new one, confirmed the new test still passes on real code. `code_hash` moved by
  exactly the predicted file (`run_tests.py`); golden snapshot confirmed unmoved. Test
  counts at landing: 440 passed (with pandas_ta) / 317 passed + 112 skipped (without) /
  369 passed, 0 failed, 32 errors (`run_tests.py`) — all recorded in the commit itself.
- **Already independently reviewed.** `044b055` was one of the "three post-round-5 fix
  commits" (`2387717`, `88e47e9`, `044b055`) this file already cites by hash as folded
  into round 6's audit package (thirteenth-patch entry, below) — round 6 found no Critical
  Tier-1 defect in that batch. This file just never said what `044b055` was.
- **Why this matters for the record, not for the decision.** This doesn't decide whether
  the release gate is open or the project is portfolio-ready — that's still Viktor's call,
  unchanged. It does mean one specific thread that looked open (five Major-severity
  findings "for Viktor to rule on") was already closed three days before anyone asked
  whether it needed ruling on.
- **Lesson, named plainly.** Claude reported these five as still open in chat, from
  reading this file's own narrative rather than checking git. This file cited `044b055`
  by hash without ever saying what it fixed — rule 19's failure shape below ("work from
  the audit, not from the summary of it"): a derived document didn't contain what the
  actual commit did, and the gap went unnoticed until someone asked to act on it.
- **Verification scope for this patch, stated plainly.** Pure prose, citing an
  already-landed, already-tested commit's own message — no code or test file touched, so
  the full three-configuration suite re-run was skipped as disproportionate to what
  changed. `code_hash` confirmed unmoved (computed on both trees) since that check is
  cheap regardless of patch size and catches any accidental non-docs change.

---
*Prior head block (15 September, seventeenth patch) kept below for history.*


*15 September 2026 (seventeenth patch, docs only) — **The five token-saving workflow rules
from the same-day chat discussion recorded in this file's own Working practice section**,
not just in the patch-delivery skill and memory. Viktor asked for an in-repo copy after the
skill/memory version landed.

- **What changed.** One new bullet under "Working practice" (below): scoped-files
  review-package default reserved for genuine fresh Tier-1 audits (not decided per-round),
  batched Engineering Notes / Portfolio Document regeneration instead of after every small
  patch, no routine staging or re-reading of `docs/audit_package/`'s
  `qwen_reasoning_*.txt` files or superseded round folders, chat-reply discipline
  restated as holding regardless of patch size, and the fresh-session-at-closure preference
  restated. Same five rules already implemented into the patch-delivery skill and recorded
  in memory earlier the same day (15 September) — this entry is the in-repo copy Viktor
  asked for, not a new ruling.
- **Not decided here.** The portfolio-ready declaration and the `portfolio-v1` tag are
  still open and still Viktor's call — see the sixteenth patch entry below, unchanged by
  this one.
- **`code_hash` unaffected** — this entry and the Working practice addition touch only
  `docs/PHASE7_NEXT.md`, which `core/code_fingerprint.py` excludes from its file walk by
  directory name; confirmed against a fresh clone of `origin/master`, not assumed.

---
*Prior head block (14 September, sixteenth patch) kept below for history.*


*14 September 2026 (sixteenth patch, docs only) — **Items 4 and 5 of six landed
(`69f1972`, `eee218e`); this file itself was the one thing not yet updated to say so.**
Session handover check, per Viktor's standing end-of-session practice: the three commits
below existed in git and in chat, but nowhere in this file, which is supposed to be the
project's own entry point.

- **What landed this session, in order.** `293f310` — Engineering Notes regenerated
  through Entry #118 (v1.29), closing the seven-commit documentation gap since before
  round 6. `69f1972` — `docs/build/build_portfolio_document.py`, generating the
  fourteen-section portfolio document (item 4). `eee218e` —
  `docs/build/build_ai_attribution.py`, generating the AI-attribution statement (item 5),
  including a corrected, AST-verified 118-entry tag count (an eyeballed regex first
  produced 111) and a corrected Results-section attribution (the sixteen-item remediation
  sequence is GLM 5.3's, not Luna Pro's — caught in proofreading before either document
  reached Viktor). Full detail in each commit's own message.
- **All six portfolio-ready criteria now have their supporting material on record**, not
  just five. (1) Release gate — round 6 (13 September) re-audited round 5's three
  Criticals and found no Critical Tier-1 defect, which is the Constitution's own bar
  ("every Critical fixed *and* re-audited") — but Viktor has never written the words
  "the release gate is open"; this file has stated the gate's technical condition, not
  declared it met. (2) Remaining findings — round 6's own F1/F2/F3 fixed and
  self-verified (fourteenth patch), the bonus duplicate-`@staticmethod` fixed (`a70fc1b`,
  fifteenth patch); nothing is on record as open and unruled. (3) Engineering Notes —
  current as of `293f310`. (4) Portfolio document — exists (`69f1972`). (5)
  AI-attribution — exists (`eee218e`). (6) Suite and golden snapshot — current, confirmed
  by every one of this session's three commits the same way as every prior patch (466
  passed / 338 passed, 117 skipped / 395 passed, 0 failed, 32 pre-existing errors).
- **Not decided here, and not this file's place to decide:** whether criterion 1 counts
  as met on today's record, whether to declare the project portfolio-ready, and whether
  to tag `portfolio-v1`. Viktor was given a plain breakdown of the above in chat and
  asked to write his own reasoned position first, per his standing preference on
  governance calls, before Claude critiques it — recorded here so the question survives
  into whatever session picks it up next, rather than living only in that chat.
- **Housekeeping.** `code_hash` unaffected — all three commits, and this entry, touch
  only files under `docs/`, which `core/code_fingerprint.py` excludes from its file walk
  by directory name; confirmed against a fresh clone of `origin/master`
  (`eee218e`), not assumed. Each delivery's own command sequence asked Viktor to delete
  the loose `.patch`/commit-message files after a successful push; not independently
  re-checked this session.

---
*Prior head block (14 September, fifteenth patch) kept below for history.*


*14 September 2026 (fifteenth patch) — **Round-6's bonus finding fixed: the duplicate
`@staticmethod` above `_finite_or_nan` in `models/signal_router.py`, landed at `a70fc1b`.**
The fourteenth patch left this for whenever it was convenient; Viktor asked for it the
same day.

- **What changed.** One of the two stacked `@staticmethod` lines removed (lines 546-547
  before the fix). `_finite_or_nan` keeps its single decorator, same body, same six call
  sites in `_build_decision_object` — no behavior change.
- **`code_hash` moved, predicted correctly.** `core/code_fingerprint.py` hashes the
  docstring-stripped parse tree, and a duplicate decorator is a second entry in the
  function's `decorator_list` — confirmed directly before the patch shipped, not assumed:
  `13908bba...20505d3851` → `3867ba49...05d3851`.
- **Golden snapshot unmoved.** `tests/fixtures/golden_decision.json` untouched —
  `tests/test_golden_path.py` (in the 466 below) confirms the decision path produces the
  identical output, since applying `@staticmethod` twice was always a no-op.
- **Verified in the Linux sandbox** against a fresh clone of `a70fc1b`: pytest with
  `pandas_ta`, 466 passed, 2 warnings; pytest without it, 338 passed, 117 skipped;
  `run_tests.py`, 395 passed / 0 failed / 32 errors (same 32 pre-existing
  missing-fixture-argument errors, unrelated to this file). Matched exactly on Viktor's
  own machine (Windows) before he committed.
- **Not decided here: whether this makes the project portfolio-ready.** F1-F5 plus this
  cleanup closes every item round-6 raised, but declaring portfolio-ready and tagging the
  commit (per the two-goals ordering, 3 September) is still Viktor's own call.

---
*Prior head block (14 September, fourteenth patch) kept below for history.*


*14 September 2026 (fourteenth patch, docs-only) — **Round-6 fix-verification sent and
graded: F1-F5 all Fixed, independently checked against code by Claude.** Closes the open
item raised at the ninth patch's own orientation (13 September) — whether closing F1
through F5 needs a round-7 re-audit before portfolio-ready — per Viktor's 14 September
ruling: the round-6 auditor verifies its own findings rather than a fresh model
re-grading everything.

- **Sent.** `python docs/build/send_fix_verification.py --send`, 14 September. Provider
  confirmed `Meta` (matches the pin, no substitution), `finish_reason=stop` (not
  truncated), `72,542` / `2,008` native prompt/completion tokens, cost `$0.0992115` —
  below the estimated $0.12-$0.19 range because the response was more terse (five short
  verdicts, no full report) than the 5k-20k output tokens the estimate budgeted for.
  Response saved to `docs/audit_reports/round6_fix-verification_2026-09-14/`.
- **All five verdicts: Fixed.** F1 (four locations named and fingerprinted), F2
  (`confidence_score` dropped from `core/engine_core.py`, sole meaning left in
  `models/signal_router.py`), F3 (all six fields NaN-passthrough via `_finite_or_nan`),
  F4 (`core/panel_render.py`'s downstream defaults NaN-safe), F5
  (`models/decision_model.py`'s bands and threshold split named/fingerprinted).
- **Independently checked against the code, not just relayed.** Every citation in the
  model's report was grepped against the actual landed code at `59de938` and matches:
  `CONFLUENCE_BOOST_MULT`/`CONFLUENCE_PENALTY_MULT`/`SPIKE_RATIO`/`CORRELATION_WINDOW`/
  `REGIME_HYSTERESIS_THRESHOLD` (F1); `confidence_score` present only in
  `signal_router.py`, not `engine_core.py` (F2); all six `signal_router.py` fields
  through `_finite_or_nan` (F3); `panel_render.py`'s `safe_float(..., float("nan"))` and
  `math.isfinite()` guards (F4); `AGGRESSIVE_TREND_HEALTH_MIN`/`AGGRESSIVE_ENTRY_SCORE_MIN`/
  `CONSERVATIVE_TREND_HEALTH_MIN`/`MIN_ACTION_BIAS`/`RAW_BIAS_THRESHOLD` (F5).
- **Bonus finding, unprompted by the review note, confirmed real — found, not fixed.**
  `models/signal_router.py` lines 546-547: `@staticmethod` appears twice, stacked, above
  `_finite_or_nan`. Harmless (a duplicate decorator, not a behavior change) but a real
  defect, not noise — verified present in the actual file. No ruling made on it this
  patch; left for whenever it is convenient to fix.
- **Not decided here: whether this makes the project portfolio-ready.** F1-F5 closing
  with verification satisfies the fix-everything-then-verify cadence, but declaring
  portfolio-ready and tagging the commit (per the two-goals ordering, 3 September) is
  Viktor's own call to make, not something this patch assumes on his behalf.

---
*Prior head block (14 September, thirteenth patch) kept below for history.*


*14 September 2026 (thirteenth patch, docs-only) — **docs/build/send_fix_verification.py
added, landed at `2fc578b`.** Viktor's ruling, same day: closing F1-F5 does not need a
fresh independent model. The round-6 auditor (meta/muse-spark-1.3) is asked to verify its
own findings were actually fixed, not to re-grade the Constitution from scratch —
finding something new would be a bonus, not the goal. Deliberately not called "Round 7";
that name is reserved for the next genuinely independent audit, saved for when
independence actually matters (before backtesting, per the existing two-goals ordering).

- New script, not a mode on `send_audit_round.py`: that script gets repointed at a new
  reviewer every round (three repoints already — Kimi K3, GPT-6 Astra, Meta Muse Spark
  1.3), so importing its `MODEL` constant would let a future repoint silently redirect
  this call too — the "one edit upstream" shape muse-spark-1.3's own F3 named for a
  fabricated-zero default three call frames from where it fires. `MODEL`/`PROVIDER_SLUG`/
  pricing are pinned independently here instead, duplicating that script's transport
  logic rather than sharing it.
- Sends a single-turn API call (no memory persists between calls, so muse-spark-1.3 has
  no memory of round 6 unless restated): round 6's own `report.md` verbatim, a review
  note pointing at each of the five items, and the full current content of the eight
  files the five fixing commits touched — not bare diffs (too thin: a few lines of
  context cannot show whether a promoted constant is used consistently elsewhere in the
  same file) and not the full codebase (would cost close to round 6's ~470,000-token
  package for a task meant to be narrow). F4 and F5 are not separately numbered in
  muse-spark-1.3's own report, so the review note explains both: F4 is a downstream
  instance of the pattern F3 described, one layer further in `core/panel_render.py`; F5
  is the two `models/decision_model.py` locations F1's own Location section already
  named but the first fix pass deliberately scoped out.
- Docs-only, no engine module touched: `code_hash` and golden snapshot confirmed
  unmoved, all three test configs unchanged (466 passed; 338 passed/117 skipped; 395
  passed/0 failed/32 errors). Dry-run estimate: ~80,346 tokens, $0.12-$0.19 — well under
  round 6's $0.63 and round 5's $12.22, consistent with a narrow follow-up rather than a
  fresh audit.
- **Not yet sent.** `OPENROUTER_API_KEY` stays on Viktor's machine and was never
  requested for or supplied to this session; he runs `python
  docs/build/send_fix_verification.py --send` himself when ready, same as every other
  audit-round send in this project.

---
*Prior head block (14 September, twelfth patch) kept below for history.*


*14 September 2026 (twelfth patch, docs-only) — **Head block brought current: the
Engineering Notes reconstruction's closure recorded at the top of the file, and the
`3e93fff` delivery defect plus its `214c5d8` structural fix named plainly.** This
session did not start new engine or docs work; it picked up the 13 September
handover's own next task (finish the Engineering Notes reconstruction) and closed it,
then found and fixed a delivery mistake made while closing it out.

- **Engineering Notes reconstruction** — `6900564`. Entries #94-#103 reconstructed
  from the v1.25/v1.26 Document History rows' own text (a document-integrity gap:
  those rows claimed the entries existed as numbered log entries and they did not);
  entries #104-#111 added for 13 September's own work (Round 6 send/grade, F1/F2/F3,
  the docs and handover-file commits, F4, F5). A three-digit entry-number rendering
  defect found while rebuilding the PDF (numbers wrapped inside `entry_box()`'s number
  column, first appearing at #100) fixed in the same commit: column widened
  `0.42in` → `0.56in`, title column narrowed to match, `entry_box()` and
  `highlighted_entry_box()` both updated. PDF grew 74 → 79 pages. Landed clean, no
  issues; byte-identical on the landed tree; `code_hash` and golden snapshot unmoved;
  all three test configs unchanged. (The prior head block below already records this
  landing correctly as of its own writing — this entry exists so the closure is
  visible at the top of the file without scrolling past it.)
- **Delivery defect at `3e93fff`, caused by Claude, not Viktor.** That commit (the
  prior head-block update, below) landed carrying its own two delivery files
  (`phase7_next_headblock.patch`, `phase7_next_headblock_commit_message.txt`)
  committed into the tracked repo alongside the real change. Root cause: the patch
  was rebuilt and redelivered to fill in the real `6900564` commit hash in place of a
  "pending" placeholder, and that redelivery used a shortened command sequence that
  dropped the `git reset <patch> <patch>_commit_message.txt` steps rule 38 exists for
  — the same `git add -A` trap rule 38 already documents, recurring because a
  numbered sequence omitted the steps rule 38 requires, not because Viktor did
  anything wrong. Viktor pasted back `git status --short` showing the two files
  staged, and Claude told him that was "exactly the expected status" without having
  actually checked it — an unverified claim stated with full confidence, the same
  failure shape Viktor's own standing rule on stating things flags as recurring and
  unacceptable. Caught by Claude itself during routine post-landing verification
  (`git show --name-status 3e93fff`), not by Viktor.
- **Structural fix** — `214c5d8`, delivered as `phase7_gitignore_cleanup.patch`.
  Removes both stray files from tracking and adds `*.patch` / `*_commit_message.txt`
  to `.gitignore` — a structural fix (Viktor's own standing preference: change the
  setup so the safe action is the only one available, rather than documenting which
  of several options is correct) so `git add -A` can no longer stage either file
  regardless of which numbered sequence is followed or whether its reset steps
  survive editing, rather than a fifth restatement of rule 38. First version of this
  fix failed to apply (tried to diff the two stray files against their pre-image, but
  Viktor had already `del`eted them from disk per the original delivery sequence);
  the corrected version touches only `.gitignore` and relies on `git add -A` picking
  up the already-missing files as a plain deletion. Confirmed landed and
  byte-identical via fresh clone: `.gitignore` is the only content change, `git
  ls-files` returns no `.patch`/`commit_message` matches anywhere in the repo,
  `code_hash` and golden snapshot unmoved, pytest 466 passed on the landed tree.

**A correction to the 14 September session handover note**
(`Claude outputs/phase7_handover_2026-09-14.md`), found while scoping this patch, not
by Viktor. That note describes this head block as still saying the Engineering Notes
reconstruction is "pending Viktor's apply" and listing it as an open item. Checked
against the actual landed file (this document, as `3e93fff` left it) rather than
assumed: that is not what it says — the document-integrity-gap paragraph below
already reads "Landed at `6900564`" with no open item, because `3e93fff`'s own final
delivery filled in the real hash before landing. The head block's real, narrower
staleness was only that it could not describe its own delivery defect or the fix for
it, since neither existed yet when `3e93fff` was written — that is what this entry
closes.

**Test counts at tip (Linux sandbox, Python 3.12.3), re-run before this docs-only
change and confirmed unchanged after it.** pytest with `pandas_ta` 466 passed; pytest
without `pandas_ta` 338 passed / 117 skipped; `run_tests.py` 395 passed / 0 failed /
32 errors (32 pre-existing, unrelated to this patch). `code_hash` confirmed unchanged
at `13908bba2ebe9a279d29acfa97876fd91a4c251b28e851631ecb8e20505d3851` on the pristine,
working, and patch-applied trees alike — computed, not assumed, since `docs/` is
excluded from the fingerprint walk by directory name and this change is docs-only.
Golden snapshot confirmed unchanged, `b027ac17f379255085b26bd1920a54d1`.

**Platform.** Built and verified in the Linux sandbox. Docs-only change with no
platform-sensitive content (no paths, no byte counts, no OS-dependent behaviour), so
there is no reason to expect Windows evidence to differ, but that expectation has not
itself been confirmed on Viktor's machine.

**Open, not yet ruled** (carried forward unchanged, not re-raised): whether closing F1
through F5 needs a round-7 re-audit before this project counts as portfolio-ready, or
whether non-Critical findings can be accepted/fixed without re-auditing — raised at
the tenth patch's own orientation, never re-raised since. This is Viktor's call; per
the 14 September handover's own instruction, waiting for him to bring it up rather
than re-raising it here.

---
*Prior head block (14 September, eleventh patch and its fix) kept below for history.*


*13 September 2026 (eleventh patch, four commits) — **F4 and F5 fixed, closing every
item the tenth patch's F1-F3 left open; the stray handover file and this document's own
head block both resolved.** Viktor's ruling on "what is next" from the tenth patch: fix
all four raised items.

- **Docs** — `1f1c935`. The (now-prior) head block below rewritten for F1/F2/F3; rule 38
  added — always `git reset` the delivery files before `git commit`, after the
  `git add -A` trap recurred three times during the tenth patch's own delivery.
- **Handover file** — `da2e231`. `Claude outputs/phase7_handover_2026-09-12.md`
  committed as-is: a complete, never-committed 12 September session handover note, found
  stray and uncommitted, confirmed by diff not to be a Viktor edit. Closes the tenth
  patch's open item (2).
- **F4** — `154e534`. `core/panel_render.py`'s `atr_stop`/`targets`/`current_price` no
  longer default to `0.0` — the same `_finite_or_nan`-style treatment F3 gave the other
  three, one layer downstream. Closes the tenth patch's found-not-fixed item and open item
  (3). A real `UnboundLocalError` bug (color variables referenced before definition) was
  found and fixed while building this, caught by running the suite, not by review —
  named honestly in the commit message. `code_hash` `36420c9f…` → `3c4ad5ca…`.
- **F5** — `ac0a211`. `models/decision_model.py`'s AGGRESSIVE/CONSERVATIVE
  trend-health/entry-score bands (`75`/`70`/`50`) promoted to named, fingerprinted class
  constants (`AGGRESSIVE_TREND_HEALTH_MIN`, `AGGRESSIVE_ENTRY_SCORE_MIN`,
  `CONSERVATIVE_TREND_HEALTH_MIN`), values unchanged. Investigated and found NOT a defect:
  the same finding's `MIN_ACTION_BIAS` naming split against `RAW_BIAS_THRESHOLD` — both
  already named, already fingerprinted, deliberately two different thresholds; nothing
  changed there. Closes the tenth patch's other not-fixed item. `code_hash`
  `3c4ad5ca…` → `13908bba…`. Golden snapshot moved (7 record-completeness fields,
  zero decision fields) — predicted this time from the F1 precedent rather than
  discovered by surprise.

**Test counts at tip (Linux sandbox, Python 3.12.3).** pytest with `pandas_ta` 466 passed;
pytest without `pandas_ta` 338 passed / 117 skipped; `run_tests.py` 395 passed / 0 failed /
32 errors (32 pre-existing fixture-collection errors, unrelated to anything this batch
touched). All four commits confirmed landed and byte-identical via fresh clone + md5 at
the time.

**Platform.** Built and verified in the Linux sandbox. Not yet independently re-run on
Viktor's Windows machine for this specific batch, unlike the tenth patch's three commits,
which were.

**A document-integrity gap found the same session, its fix delivered separately.**
`docs/build/build_engineering_notes.py`'s own Document History table (`v1.25`, `v1.26`
rows) claimed Entries #94 through #103 were added, with full narrative and commit hashes
for each, but no `entry_box(94)` through `entry_box(103)` existed anywhere in the file —
ten entries' worth of already-recorded work existed only as history-table prose, never as
the numbered entries those rows claimed exist. Viktor ruled: reconstruct #94-#103 from the
history table's own text, then add new entries from #104 covering this batch's own work.
Landed at `6900564` — Entries #94-#111, two new Document History rows (`v1.27`,
`v1.28`), plus a three-digit entry-number column-width rendering defect found and fixed
while rebuilding the PDF. Confirmed landed and byte-identical via fresh clone + md5;
docs-only, `code_hash` and the golden snapshot confirmed unmoved on the pristine,
working, patch-applied, and landed trees alike (`13908bba…`, matching tip).

**Open, not yet ruled.** Whether closing F1 through F5 needs a round-7 re-audit before
this project counts as portfolio-ready, or whether non-Critical findings can be
accepted/fixed without re-auditing — raised at the tenth patch's own orientation, never
re-raised, still not answered.

---
*Prior head block (13 September, tenth patch) kept below for history.*


*13 September 2026 (tenth patch, three commits) — **Round 6's F1/F2/F3 fixed,
verified per-fix and combined, and landed.** Viktor ruled: "Let us fix F1 to F3." Each
landed as its own commit, independently verified before and after combining, per the
project's established one-fix-per-commit pattern.

- **F1** — `447966b`. T2-4 Explicit Configuration. Six bare literals/function-locals
  promoted to named constants at their existing location, value unchanged:
  `models/entry_model.py`'s `CONFLUENCE_BOOST_MULT`/`CONFLUENCE_PENALTY_MULT`
  (module-level), `indicators/indicators.py`'s `SPIKE_RATIO` (function-local promoted to
  module scope), `models/btc_context.py`'s `CORRELATION_WINDOW` (now
  `compute_correlation_beta`'s own default), `structure/structure.py`'s
  `StructureEngine.REGIME_HYSTERESIS_THRESHOLD` (class attribute, matching
  `DecisionModel`'s existing pattern). All four registered in `decision_log.py`'s
  `FINGERPRINTED_MODULES`. Scope stated explicitly, narrower than the report's own F1
  Location section: `decision_model.py`'s trend-health bands (`>=75`/`>=70`/`>=50`) and
  the `MIN_ACTION_BIAS`/`RAW_BIAS_THRESHOLD` naming split are not touched — left open,
  see below.
- **F2** — `3c7e9ae`. Item 10 Consistent Semantics. `engine_core.py`'s raw `risk` dict no
  longer carries a duplicate `confidence_score` (unsigned trend magnitude) under the same
  dotted name `signal_router.py` gives a different meaning (bias magnitude) in the final
  decision object. Dropped rather than renamed — the value survives intact at
  `trend.trend_health`, a few lines below in the same return object.
- **F3** — `9b34163`. Item 13 Fail Safely / Item 8 Epistemic Honesty, unreachable on the
  live path today. `signal_router.py`'s `_build_decision_object` no longer substitutes a
  finite `0.0` for six absent measurements (`zone_lower`, `zone_upper`,
  `distance_from_zone`, `atr_stop`, `targets`, `current_price`) — all six now go through
  `_finite_or_nan`, the same treatment `structure.hvn`/`lvn`/`swing_struct` already get.
  Found, not fixed: three of these six reach `panel_render.py` through a still-not-NaN-
  aware `safe_float()` call distinct from the one already fixed for the other three —
  flagged for a separate, narrowly-scoped patch, not folded into this one (touching
  `current_price`'s downstream arithmetic risks repeating the project's own prior "$nan"
  print regression).

**Test counts, split by kind, isolated per fix and combined (Linux sandbox, then
reproduced on Viktor's own Windows machine while landing each commit — this is now
Windows evidence, not just Linux):**

    pytest with pandas_ta:     440 -> 443 (F1) -> 446 (F2) -> 455 (F3) passed, 0 failed
                                throughout
    pytest without pandas_ta:  317p/112s -> 318p/114s (F1) -> 318p/117s (F2) ->
                                327p/117s (F3)
    run_tests.py:              369p/0f/32e -> 372 (F1) -> 375 (F2) -> 384 (F3) passed,
                                0 failed / 32 errors unchanged throughout

**Golden snapshot** — F1 moved (predicted wrong the first pass, corrected by running the
suite): `lineage.run_hash` folds the FULL `module_snapshot()` output into its hash, so
registering 4 new fingerprinted names moved `run_hash` and the derived `archive_path`
even though no decision value changed — 6 record-completeness fields moved,
re-baselined and confirmed against the diff, zero decision fields moved. F2 and F3 both
predicted and confirmed unmoved (byte-identical, md5 `43534cb6c506728c5869a627a24fe711`
throughout both).

**`code_hash` moved, predicted and confirmed, isolated per fix:**

| tree | code_hash |
|---|---|
| `4e0110b` (base) | `4d6f81965109e5a206ad5ac093ba1986f6a5d455243f395408d914b82327d127` |
| F1 alone | `2f2d03408625e34b994a064c88e81b4e508d07f036ef7e3b4c2b9f73ee9f74d5` |
| F1+F2 | `fab0c772162cd12f386bf814d5a4a899434f8981d6d89e684b3e6b72810e6977` |
| F1+F2+F3 | `36420c9fe3dbe6ddecacf3954224475332f0ad39f1f47f7c1989554591ba9567` |

Each step confirmed to move exactly one file's own entry in the fingerprint table
(`engine_core.py` for F1->F2, `signal_router.py` for F2->F3), not assumed from the
top-level hash alone.

**A CRLF wrinkle found while re-baselining F1's golden snapshot on Linux**, out of scope
for this patch: `test_golden_path.py`'s `PHASE7_UPDATE_SNAPSHOT` path writes with a plain
`open(path, "w")`, no explicit `newline=`, so it inherits the sandbox's LF rather than
this repo's CRLF. Converted back by hand (byte-level `\n`->`\r\n`, safe because
`json.dump` escapes embedded newlines as two characters, never a raw byte) and
re-verified. Worth knowing if this file is ever re-baselined from a Linux sandbox again
— `test_golden_path.py` itself is unpatched.

**Platform.** Built and verified in the Linux sandbox first — three configurations, each
fix isolated then combined. All three commits were then applied and both test
configurations re-run by Viktor on his own Windows machine as part of landing them; the
counts above are confirmed on both platforms, not Linux alone.

**A delivery-mechanics lesson, not a code defect.** All six files (three patches, three
commit messages) were delivered to the repo root together rather than one patch at a
time. Every one of the three `git add -A` steps therefore swept in the not-yet-applied
patch/message files for the *next* fix, plus a pre-existing, unrelated, already-modified
`Claude outputs/phase7_handover_2026-09-12.md` that predates this session and was never
touched by any of these three patches. Caught each time by reading `git status --short`
before committing rather than trusting the numbered sequence blindly, and corrected with
`git reset` before each commit — nothing wrong landed in any of the three commits,
confirmed by the staged file list matching the predicted set exactly at every commit.
Added as rule 38 below. The handover file's own stray modification is still unresolved
— open item, see below.

**Not fixed, deliberately.** `decision_model.py`'s trend-health bands and the
`MIN_ACTION_BIAS`/`RAW_BIAS_THRESHOLD` naming split (F1's report raised these, the
narrower scope Viktor ruled on did not include them). `panel_render.py`'s
`atr_stop`/`targets`/`current_price` `safe_float()` calls (F3's found-not-fixed item,
above).

**Open, not yet ruled.** (1) Whether closing F1/F2/F3 needs a round-7 re-audit before this
project counts as portfolio-ready, or whether non-Critical findings can be
accepted/fixed without re-auditing — raised at the end of the F1/F2/F3 orientation, not
yet answered. (2) `Claude outputs/phase7_handover_2026-09-12.md` sits modified and
uncommitted, predating this session, unrelated to F1/F2/F3 — Viktor confirmed he made no
edits himself; origin and disposition undetermined. (3) `panel_render.py`'s
NaN-consistency gap found during F3. (4) `Phase7_Engineering_Notes.pdf` still reflects
the eighth patch — regenerating it remains deferred, not forgotten.

---
*Prior head block (13 September, ninth patch) kept below for history.*


*13 September 2026 (ninth patch, docs only) — **Round 6 sent and graded; release gate holds
(Met, no Critical Tier-1 finding).** First `--send` attempt failed HTTP 403 (OpenRouter's
account-level 18+ age-attestation gate, not a package or provider problem — resolved by
Viktor at openrouter.ai/settings/preferences, no charge incurred); the second attempt
completed cleanly. `finish_reason=stop`, provider `Meta` (matches the pin), 470,488 prompt
tokens / 10,765 completion tokens (6,570 of them reasoning), cost **$0.63386125** — confirmed
in `generation.json`/`run_metadata.json`.

Meta Muse Spark 1.3's report (`docs/audit_reports/round6_muse-spark-1.3_2026-09-13/report.md`,
172 lines, self-identifies correctly as "first reviewer in this project from a lab with no
prior exposure to it," ends cleanly on Section 11's closing line, not truncated) found no
Critical Tier-1 defect:

- **F1** — T2-4 Explicit configuration, Moderate. Confluence multipliers
  (`macro_multiplier`/`trend_multiplier`/`structure_multiplier` in `entry_model.py`),
  `SPIKE_RATIO`, the correlation window, and `structure.py`'s `threshold = 0.0015` are bare
  literals or function locals, not named configuration — none is readable from
  `core/config.py`, and several have no module-scope name at all, so
  `decision_log.module_snapshot()` cannot record them.
- **F2** — Item 10 Consistent Semantics, Minor. `confidence_score` means unsigned trend
  magnitude in `engine_core.py` but bias magnitude in `signal_router.py` — same dotted key,
  two derivations; the router's overwrite means today's operator sees one value, but the
  duplicate meaning is still live at the engine layer.
- **F3** — Item 13/Item 8, Minor, unreachable on the live path today. `signal_router.py`'s
  `_build_decision_object` substitutes `0.0` for a missing zone/price/target key instead of
  NaN — the same fabrication shape as the `close*0.99` and `swing_struct=current_price`
  defects already removed, one upstream edit away from firing.

Item 15 (Empirical Evidence Supersedes Theory) stays **Not verifiable** — no backtest exists
yet to disagree with anything, consistent with every prior round. All three batched
post-round-5 fix commits (`2387717`, `88e47e9`, `044b055`) were reviewed from code as shipped
and confirmed real; the pinned golden decision is unchanged except the disclosed
`degraded_inputs: []` schema addition.

**Encoding defect found and fixed the same day.** Verifying the report before acting on it
found every non-ASCII character in `report.md` as originally written — every em dash, `±`,
`→` — was mojibake (`â\x80\x94` for an em dash, etc.); all-ASCII content, including every
verdict and finding above, was unaffected throughout. Root cause:
`docs/build/send_audit_round.py` read the streamed response with
`resp.iter_lines(decode_unicode=True)` without setting `resp.encoding` first, so `requests`
fell back to Latin-1 (OpenRouter's response carries no explicit charset) instead of the
API's actual UTF-8. The corruption is a deterministic, reversible byte transform; round-
tripping the file as received (`.decode("utf-8").encode("latin-1").decode("utf-8")`)
restores the model's exact original text with no residual mojibake — full detail, both
files' hashes, and why `run_metadata.json` is left untouched, in
`docs/audit_reports/round6_muse-spark-1.3_2026-09-13/ENCODING_CORRECTION.md`.

**RULED, 13 September 2026 — both.** (1) `report.md` replaced with the corrected decode —
same model output, not a content edit, original corrupted bytes hashed for the record in
ENCODING_CORRECTION.md rather than silently discarded. (2) `send_audit_round.py` patched to
set `resp.encoding = "utf-8"` immediately after the POST returns, before anything reads
`resp.text` or the stream, and its docstring's list of failure modes this script exists to
make impossible now names this as the fourth. Round 7 onward is not exposed to it.

**Platform.** Docs only; no production module touched, `code_hash` unaffected.

**Open, not yet ruled.** Whether to fix or accept each of F1/F2/F3 as a limitation, and
whether closing them needs a round-7 re-audit before this project can be called
portfolio-ready per the two-goals ordering -- unlike round 5's Criticals, none of round
6's findings blocks the release gate on its own, so the answer is not forced the way it
was last round. Both are Viktor's call, raised at the end of this session, not yet
answered. Separately: Phase7_Engineering_Notes.pdf still reflects the eighth patch, not
round 6 or this correction -- regenerating it is deferred, not forgotten.

---
*Prior head block (13 September, eighth patch) kept below for history.*


*12 September 2026 (eighth patch, one commit) — **All five of requested-run 6's
mutant-escape findings fixed, verified, and landed at `044b055`.** Viktor: "we go with
number 1" (fix these five ahead of round 6's re-audit of F1/F2/F3). Touches five test files
and `run_tests.py` only; no production module in `core/`, `models/`, `indicators/`,
`structure/`, `data/` or `utils/` changed — each fix strengthens an existing test's own
assertions to check what its docstring already claimed to check.

- **Fix 1 — `test_trend_direction_source.py`.** Added the `assert sign == expect` its own
  loop header had computed and never read, closing the always-neutral
  `compute_trend_health` escape. Verifying it surfaced a second, pre-existing defect in the
  same test: the fixture handed raw OHLCV straight to `compute_trend_health`, which needs
  `EMA20_Slope`/`EMA50_Slope`/`ADX`/`RSI` — columns only `add_technical_indicators()`
  computes — so the original fixture returned NEUTRAL/0/0.0 on real, unmutated code for
  both slope directions. Fixed by routing the fixture through
  `add_technical_indicators()` -> `calculate_structure()`, the same order
  `core/engine_core.py` uses, before calling `compute_trend_health`.
- **Fix 2 — `test_timeframe_disagreement.py`.** Added an assertion on
  `decision["exit"]["action"]` (substring `"LONG"`), closing the always-WAIT
  `_determine_final_action` escape the test's own docstring already claimed to guard
  against but never checked.
- **Fix 3 — `test_frame_ownership.py`.** Both tests now assert the rendered chart file
  exists and exceeds 1024 bytes, closing the no-op `plot_engine_chart` escape (previously
  checked only frame-ownership and log-level side effects, both trivially satisfied by a
  function that draws nothing).
- **Fix 4 — `test_smoke.py`.** Added `assert "error" not in first` plus a check that
  `first["exit"]["action"]` is truthy, closing the canned-identical-error-dict
  `SignalRouter.route` escape (previously checked only that two calls agreed with each
  other, not that either reached a real decision).
- **Fix 5 — `run_tests.py` + new `tests/test_run_tests_filter_matching.py`.** Section 7.3's
  finding: a filter matching zero test files exited 0 — a green exit code for a run that
  tested nothing. `main()` now checks, before the run loop, whether a given filter matched
  no files, and exits 2 if so. Three new subprocess-based tests, including a negative
  control using a throwaway always-passing file (an existing test file was tried first and
  rejected — `test_imports.py`'s `pytest.skip()` becomes an "error" under `run_tests.py`,
  which would have made the control's assumptions environment-dependent).

All five verified non-vacuously: named mutant reproduced in-process, old test confirmed to
pass against it (matching requested-run 6), new test confirmed to FAIL against the same
mutant naming the actual defect, then confirmed to PASS against real code.

**Test counts, split by kind, combined with both prior fixes this session (`2387717`,
`88e47e9`) already included:**

    pytest with pandas_ta:     437 -> 440 passed, 0 failed
    pytest without pandas_ta:  315p/111s -> 317p/112s (net +2 passed/+1 skipped, not +3/+0:
                                fix 1's new pandas_ta guard flips one previously-passing
                                test to skip under this configuration)
    run_tests.py:               366 -> 369 passed, 0 failed, 32 errors unchanged

**Golden snapshot** — predicted unmoved, confirmed: none of the five fixes touch the
decision-object shape, `engine_core.py`, `signal_router.py`, or any indicator;
`test_golden_path.py` (8 tests) passes unchanged.

**`code_hash` moved, predicted (one file, `run_tests.py`; `tests/` excluded by directory)
and confirmed:** `099f84ae...c57` -> `4d6f8196...127` (built on `b087875`).

**Not fixed by this patch.** Round 6's re-audit of F1/F2/F3 is still unrun. **Batching,
ruled 13 September:** all three post-round-5 fix commits (`2387717`, `88e47e9`, `044b055`) —
none of which has had any independent review — are folded into round 6's package alongside
the F1/F2/F3 re-audit, rather than a separate later pass. **Round 6's model, ruled 13
September, corrected same day:** `meta/muse-spark-1.3` on OpenRouter. Originally ruled as
`meta/muse-spark-1.2` — ChatGPT and Gemini ruled out as future channels (12 September),
pick delegated to Claude, chosen over `x-ai/grok-4.6` for context-window headroom (1.05M vs
500K against a package that was already 435,612 prompt tokens at round 5, before batching in
three more commits) and single-provider safety (no auto-router substitution risk, the
round-3 failure mode). Before building round 6, checking OpenRouter's live models API (not
done before the original ruling) found `meta/muse-spark-1.2` no longer listed as an
invokable endpoint -- only `meta/muse-spark-1.3`, `meta/muse-spark-1.3-contributor`, and
`meta/muse-spark-1.2-contributor` exist now. The `-contributor` tiers were ruled out
regardless of price: their own pages state prompts and outputs may be used to improve
Meta's products, which would leak Phase-7's source rather than just cost more. `1.3` is the
live, same-tier, same-price ($1.25/$4.25 per M) successor with the same 1.05M context and no
data-sharing notice, released 2 September 2026 -- the original reasoning applies to it
unchanged. Viktor ruled the correction same day. Round 6 itself is still unbuilt and
unsent.

**Platform.** Built and verified in the Linux sandbox — evidence about Linux, not yet
Windows. No production module changed, so no live-data run is being recommended before this
lands (unlike the BTC-decoupling and RSI-fallback fixes in the block below).

---
*Prior head block (12 September, seventh patch) kept below for history.*


*12 September 2026 (seventh patch, two commits) — **Both requested-run 4 and 5 findings
fixed, verified, and landed. Requested-run 6's five mutant-escape findings remain unfixed;
release gate stays shut.** Viktor ruled on both new findings the sixth patch (below) recorded,
each landed as its own commit per the established one-fix-per-commit pattern, each
independently verified before and after combining, exactly as F1/F2/F3 were.

- **BTC-degradation decoupling**, landed at `2387717`. Viktor ruled: "BTC only indicator fail
  should not degrade AERO's independent current actual confidence/trading-authorization. The
  information about the BTC price movement is just there as a bonus and something to
  consider." `engine_core.py`'s BTC-context block now captures `btc_trend`'s
  `degraded_inputs` into a local variable instead of appending them to the shared
  `degradation` list `DecisionModel.evaluate()` reads to cap confidence and gate
  `trading_authorized` — SWEEP ITEM 11's motivation (don't silently drop a BTC indicator
  failure) is preserved by recording it in `btc_context["degraded_inputs"]` instead, a new
  optional field on `decision_contract.py`'s `BtcContextBlock`, carried through
  `signal_router.py`'s `_merge_btc_context`. Reaches the decision log for an auditor; never
  reaches the `degradation` list, `DecisionModel`, or the live panel — confirmed
  `panel_render.py`'s BTC section needs no change, resolving Viktor's separate concern that
  new panel text (e.g. "BTC ADX unavailable") could read to a new user as something wrong
  with the engine itself, rather than an absent bonus number. Three new tests in
  `tests/test_btc_degradation_stays_informational.py`, confirmed to fail against pre-fix code.
- **RSI-fallback zero-average-loss fix**, landed at `88e47e9`. Viktor ruled: "We need to fix
  the RSI-Fallback" — the sixth patch's finding that a purely monotonic price series drives
  the manual RSI fallback's average loss to zero for the whole series, which
  `loss.replace(0, np.nan)` turned into an all-NaN column and an outright fallback failure
  rather than the mathematically correct RSI 100. `indicators.py`'s fallback now special-cases
  `loss == 0`: RSI 100 when gain is positive (pandas_ta's own answer), RSI 50 when gain is
  also zero (a flat price, the same neutral centre-of-scale value this file already uses
  elsewhere). Two new parametrized tests in `tests/test_no_fabricated_fallbacks.py`
  (`monotonic`→100, `flat`→50), confirmed to fail against pre-fix code.

**Golden snapshot** — predicted to move only for the BTC fix (a schema addition, since the
pinned fixtures never fail a BTC indicator or hold a zero Wilder average loss), confirmed:
re-baselined, diffed field-by-field against the prior snapshot, exactly one key added
(`btc_context.degraded_inputs: []`) — every other field, and every field the RSI fix could
have touched, byte-identical. All 8 `test_golden_path.py` tests pass.

**`code_hash` moved, predicted and confirmed**, isolated per fix and combined:

| tree | code_hash |
|---|---|
| `d69235d` (base) | `00c8d4ea4858bb2b8f5dfabcfbeac8ceeda23a4513c11adcb5c8ce1f1025854b` |
| BTC fix alone | `7398e96d74fd749209d998f4fd13f7765f7567a2098da45c02cf386fd9376702` |
| RSI fix alone | `07e0da8cd751514928857681e25b68f8f8a1f1289dde0c5a964c7cee0a7a6c53` |
| both combined | `099f84aefff87ef8742484601039e959bbd905bc8170ad8832db7a5b1c417c57` |

**Test counts, split by kind, base → BTC-alone / RSI-alone → combined:**

    pytest with pandas_ta:     432 → 435 / 434 → 437 passed, 0 failed throughout
    pytest without pandas_ta:  315p/106s → 315p/109s / 315p/108s → 315p/111s, 0 failed
    run_tests.py:              365p/0f/29e → 366p/0f/31e / 365p/0f/30e → 366p/0f/32e

The `run_tests.py` error-count increases are the runner's own known limitation (calling
parametrized/fixture-taking tests with no arguments) picking up the new tests — same shape as
every pre-existing entry in that list, not a new kind of problem; diffed to confirm no
pre-existing entry's identity changed.

**Not fixed by this patch.** Requested-run 6's five mutant-escape findings (`compute_trend_health`,
`_determine_final_action`, `plot_engine_chart`, `SignalRouter.route`, and the empty-filter
`run_tests.py` result) remain exactly as the sixth patch recorded them — GPT-6 Astra's own
report already names the required action (real preconditions, assert the actual outcome,
perturb through real consumers) and nothing here has started that work. **Release gate stays
shut** on that basis, and round 6's re-audit of F1/F2/F3 is still unrun.

**Platform.** Built and verified in the Linux sandbox, same as F1/F2/F3 and the sixth patch —
evidence about Linux. Applied and committed by Viktor on his own Windows machine via the
device bridge (no shell there this session); both commits landed cleanly (`2387717`, `88e47e9`)
on top of `d69235d`. Not yet evidence that the suite passes on Windows — recommend running the
engine once on live data before trusting a decision from it, same as recommended for F3.

---
*Prior head block (12 September, sixth patch) kept below for history.*

*12 September 2026 (sixth patch, docs only) — **Requested-runs 4-6 from GPT-6 Astra's
round-5 report executed and reported. No code touched. Two new candidate defects found;
neither fixed. Release gate stays shut.** Per Viktor's instruction this session: run
requested-runs 4-6 (BTC-only failures, fallback equivalence, test effectiveness/isolation —
all Major, not Critical, in the round-5 report) rather than commissioning round 6 yet. All
three run against the live tip (`83f9d2d`) in the Linux sandbox; not yet evidence about
Windows. Scripts used are not part of this patch (throwaway, run from outside the tree).

**Run 4 — BTC-only failures.** Independently failed BTC's own ADX, SuperTrend, ATR and
structure (AERO's and the macro frame's own indicator calls left real, via call-count-based
mocks, plus one genuine-data scenario: BTC's final candle NaN'd on `high`/`low`/`close`).
AERO's own action and `confidence_score` stayed byte-identical to the healthy control for
BTC SuperTrend failure, BTC ATR failure (primary raised; the manual fallback recovered it,
so ATR alone could not be forced to fail outright this way), BTC structure failure (whole
`btc_context` correctly falls to `{"available": false}`, panel correctly prints "unavailable
this run"), and the genuine BTC-feed-corruption scenario (`_validate_dataframe` rejects it
before it reaches indicators; `btc_context` again `{"available": false}`).

**BTC ADX failure did not stay isolated.** With only the 3rd `ta.adx` call (BTC's) mocked to
raise — AERO's own `trend_health` unaffected at 95.35, matching the control — AERO's own
`confidence_score` dropped from 78.70 to exactly 50.0 (`DecisionModel.DEGRADED_CONFIDENCE_CEILING`)
and `degradation.trading_authorized` flipped `true`→`false`, with `missing_inputs` reading
`["BTC ADX (column absent)"]` — nothing AERO-side. This is the opposite of what
`engine_core.py`'s own comment at the BTC context block promises: *"This NEVER changes BIAS,
DECISION, entry, risk, or targets above... BTC context is additive, never a replacement or
distortion of the AERO-only analysis."* Traced to `SWEEP ITEM 11` (8 Sep 2026, `c3b0d43`,
GLM F-6): that fix made BTC's own `compute_trend_health` `degraded_inputs` (previously
silently discarded) get appended, as `f"BTC {d}"`, into the *same* `degradation` list
`DecisionModel.evaluate()` reads to cap AERO's confidence and gate `trading_authorized` —
so a fix aimed at "these BTC degradations were being silently dropped" landed by routing
them into the one list that is not supposed to hear from BTC at all. RSI shares the same
`compute_trend_health` degraded_inputs channel and was not tested here (outside run 4's
named scope of ADX/SuperTrend/ATR/structure) but is presumably the same shape. **Not fixed.
Whether the comment or the code is wrong is Viktor's call** — GLM F-6/item 11 was ruled
7-8 September as a real fix for a real problem (BTC degradations going unreported), and
undoing it un-fixes that; the alternative is a second, BTC-only degradation channel that
DecisionModel never reads. Full reproduction in the session transcript.

**Run 5 — fallback equivalence.** Forced `ta.ema`/`ta.rsi`/`ta.atr` to raise (manual
pandas fallback takes over) and compared the final-bar value against the real pandas_ta
computation, at frame lengths 20/50/75/100/300/450, on a random walk, a monotonic series,
and an early-large-move series, plus altered indicator lengths (EMA 9/21, RSI 7, ATR 21).
Confirms the round-5 report's suspicion that `tests/test_no_fabricated_fallbacks.py`'s
single 300-bar/default-length check does not represent the general case:

| n   | worst \|rel diff\| seen (random walk, default lengths) |
|-----|----------------------------------------------------|
| 20  | RSI 12.78%, ATR 16.06%, EMA_20 0.06%                |
| 50  | EMA_50 1.20%, RSI 2.11%, ATR 0.47%                  |
| 75  | EMA_50 0.18%                                        |
| 100 | all under 0.13%                                     |
| 300–450 | all under 1e-4% (matches the existing 300-bar/default-length test) |

Altered lengths (n=50, EMA 9/21 RSI 7 ATR 21) reproduced the same shape: ATR 9.74% off,
consistent with shorter effective histories amplifying the two algorithms' different
warm-up seeding (documented in the fallback's own comments) rather than any new mechanism.

**New: the manual RSI fallback fails outright, not just divergently, on a purely monotonic
price series.** A strictly-increasing 100-bar close series has zero down-bars, so the
fallback's `loss.replace(0, np.nan)` — written to dodge division by zero — turns the
*entire* loss series to NaN, `rs = gain / NaN` is NaN throughout, `unusable_reason` correctly
sees an all-NaN series and raises, and RSI is recorded as failed for the whole run. pandas_ta,
on the identical input, correctly returns 100.0 (the mathematically right answer: all gains,
no losses). So a real, sustained monotonic move — exactly the condition where an overbought
RSI reading matters most — is precisely where the fallback goes silently missing instead of
reading the extreme value, if pandas_ta is ever unavailable (a configuration this project
ships and tests: the 315+106-skip suite). **Not fixed** — the fallback needs a `loss == 0`
special case (RSI 100, or 50 if gain is also 0) rather than the blanket NaN-out. Also
confirmed, as the report asked: a successful fallback is never recorded anywhere in the
returned failures/degradation object — a run using the manual EMA/RSI/ATR path is
indistinguishable, in every field but the indicator's own number, from one that used
pandas_ta.

**Run 6 — test effectiveness and isolation.** Built and ran all four mutants named in F11's
"Verification" line, in-process, against their named tests. **All four escaped detection,
exactly as GPT-6 Astra predicted:**

- always-neutral `compute_trend_health` (returns NEUTRAL/0 unconditionally) —
  `test_trend_direction_source.py::test_trend_health_reports_a_sign_that_matches_its_own_label`
  — **passed**.
- always-WAIT `DecisionModel._determine_final_action` — `test_timeframe_disagreement.py::
  test_the_engine_still_reaches_a_side_when_the_timeframes_agree` — **passed** (that test
  never asserts the action itself, only `bias.raw`/`macro_bias`, exactly as F11 item 3 says).
- no-op `plot_engine_chart` (returns the save path, draws nothing, logs nothing) — both
  `test_frame_ownership.py::test_plot_engine_chart_does_not_touch_the_callers_frame` and
  `::test_plotting_does_not_swallow_a_broken_repair_path` — **passed**.
- `SignalRouter.route` always returning the identical canned error dict —
  `test_smoke.py::test_the_smoke_run_is_reproducible` — **passed**.

Also checked, as requested: a filtered `run_tests.py` invocation whose filter matches zero
files exits 0 with "0 passed 0 failed 0 errors" — a silently green result for a run that
tested nothing, confirming that Section 7.3 claim directly. And, a genuinely reassuring
negative result: a sentinel file placed in a real `logs/` directory at the repo root
survived byte-for-byte across a fresh-process, non-empty-filter `run_tests.py` invocation —
`conftest.py`'s import-time `LOG_DIR` redirect (the fix for the 6 September decision-log
incident) holds under the dependency-free runner too, not just under pytest. **None of the
five mutant/isolation findings were fixed this session** — run 6 was a measurement, and
GPT-6 Astra's own report already carries the required action (real preconditions, assert
the actual outcome, perturb through real consumers).

**`code_hash` confirmed unmoved by this patch**, independently computed before and after
touching only this file: `00c8d4ea4858bb2b8f5dfabcfbeac8ceeda23a4513c11adcb5c8ce1f1025854b`
— matches the value on record at `83f9d2d` exactly. (One false alarm on the way: the
sandbox's own throwaway verification scripts, written at the repo root rather than outside
the tree, transiently changed the computed hash by being picked up as source files — caught
by recomputing after moving them out, not by assuming the invariant held.)

**Release gate stays shut.** Nothing in this patch fixes anything. Two new candidate defects
(the BTC-degradation cross-contamination above, and the monotonic-series RSI-fallback
failure) and the confirmed F11 mutant-escape findings are recorded here for **Viktor to
rule on** — whether each is worth its own fix, and if so at what priority against round 6's
re-audit. Requested-runs 1-3 (volatility propagation, entry-scoring direction, trailing
zero-volume window) were the ones behind F1/F2/F3, already fixed and landed; 4-6 are now
done. Round 6's re-audit of the F1/F2/F3 fixes is still unrun and is not this session's job.

---
*Prior head block (12 September, fifth patch) kept below for history.*


*12 September 2026 (fifth patch) — **All three round-5 Criticals fixed, verified, and
landed. Docs pass batched as promised.** Each fix was its own patch, per Viktor's
instruction, delivered and verified individually per the patch-delivery skill before the
next was started.

- **F1** landed at `83e334d`: `calculate_stop_targets()`'s production call now passes
  `volatility_state=volatility_mode`, matching what the sibling `validate_risk_parameters`
  call already received three lines below.
- **F2** landed at `3f92230`: `eq_trade_direction` is now derived from `raw_bias` directly
  (BULLISH→LONG, BEARISH→SHORT, NEUTRAL→the `bias_score` sign), not from `short_signal` —
  the same signal `decision_model.py`'s own `decide()` already uses, and the same "bias is
  the sole direction source" shape Viktor ruled for that function on 2 September.
- **F3** landed at `7fcf646`, two parts in `indicators.py`: VWMA's own forward-fill now
  stops at the trailing edge (interior gaps still fill; nothing follows the last row if that
  row's own window had no usable volume), and `"VWMA"` was added to `critical_indicators` so
  a genuine decision-bar miss gets the same `failed()`/degraded-inputs treatment every other
  indicator failure gets. Three new regression tests added to
  `tests/test_decision_bar_integrity.py`, confirmed to actually fail against pre-fix code
  (not vacuous), mirroring the file's existing ADX test for the same class of finding.

Each fix independently reproduced against live code before and after, on both a build tree
and a separately-applied pristine-clone tree; golden snapshot predicted unmoved and
confirmed by running it each time (none of the three exercised the pinned TESTUSDT
fixture's specific values); `code_hash` predicted moved and confirmed on two independently
built trees each time; all three suite configurations unmoved except F3's own three added
tests (432/315+106-skip/365, 29 `run_tests.py` errors — same identity as before, diffed
character-for-character). All evidence from the Linux sandbox; not yet evidence about
Windows until Viktor applies and runs each patch there.

**Observed, not fixed, out of round 5's scope:** `risk_model.py`'s own
`calculate_stop_targets()` has a structurally similar-looking `effective_bias` fallback, but
`detailed_bias` never holds `"LONG"`/`"SHORT"` literally (only `BiasStateMachine`'s own
`"BULLISH CONFIRMED"`/`"BEARISH CONFIRMED"`/`"NEUTRAL"` alphabet), so the branch always falls
through to the `bias_score`-sign tie-break regardless. Recorded because it surfaced while
scoping F2; not part of round 5's report or ruling, and no ruling was asked for it.

**Engineering Notes gap closed.** `docs/build/build_engineering_notes.py`'s Document History
table gains a `v1.26` row, entries #98 through #103, covering `4d99cdb`, `de7d135`,
`a12640a`, and the three fixes above (`83e334d`, `3f92230`, `7fcf646`) — following the same
#94–97 precedent of a compact table row rather than individual `entry_box()` calls. Two
drafts of this row failed before landing: one on a straight-quote/curly-quote mismatch
against this file's own quoting convention (`SyntaxError`), one on being nearly double the
longest existing row and exceeding ReportLab's page-height limit (`LayoutError` on page 75).
The row that landed is ~2,537 characters, under the ~2,413-character precedent set by
v1.20. Rebuilt the PDF in the sandbox afterward — 75 pages, exits clean, no `LayoutError`,
and the new row's text confirmed present on page 75 by extracting the PDF's own text, not
just by the exit code. **Regenerating `docs/Phase7_Engineering_Notes.pdf` from this updated
script on your machine is still your own manual step** (`python docs\build\build_engineering_notes.py`)
— this patch only changes the script, per the project's existing precedent that PDF
regeneration stays a deliberate step rather than an automatic one.

This patch touches only `docs/PHASE7_NEXT.md` (this file) and
`docs/build/build_engineering_notes.py` — both under `docs/`, excluded from
`core/code_fingerprint.py`'s hash by directory. `code_hash` confirmed unmoved
(`00c8d4ea4858bb2b8f5dfabcfbeac8ceeda23a4513c11adcb5c8ce1f1025854b`, matching F3's own
landed value exactly) on the tree before this patch and the tree after, computed
separately rather than assumed from the directory-exclusion rule alone. All three suite
configurations re-run on the patched tree and confirmed at F3's exact post-fix counts
(432 / 315+106-skip / 365+29-errors) — no drift from a docs-only change.

**Release gate stays shut.** The Constitution's bar is "landed *and* been re-audited" —
all three of round 5's Criticals have landed but none has been re-audited yet; that is
round 6's job, not this session's. Requested-runs 4–6 from GPT-6 Astra's report (BTC-only
failures, fallback equivalence, test-effectiveness — all Major, not Critical) remain unrun.

**Recommend running the engine on live data and reading the panel before your next commit.**
A run whose decision-bar VWMA rolling window has no usable volume will now come back
DEGRADED, naming VWMA in `missing_inputs`, confidence capped at 50/100, trading not
authorized — where it previously showed a clean analysis with a stale VWMA distance score.
That is F3 working as intended, not a new defect. The same applies more generally: any run
where `raw_bias` disagrees with what `long_signal`/`short_signal` alone would have implied
can now score entry quality differently than before (F2), and any run under elevated or
reduced volatility can now get wider or narrower stops/targets than before (F1).

---
*Prior head block (12 September, fourth patch) kept below for history.*


*12 September 2026 (fourth patch) — **Round 5 sent and graded; release gate stays shut on
three newly confirmed Criticals; all three RULED to fix.** Docs only, no code touched.
`python docs\build\send_audit_round.py --send` ran twice: a first attempt failed with HTTP
401 ("User not found" — an API-key problem, not a package or provider problem) before ever
opening `report.md`; the second attempt completed cleanly. `finish_reason=stop`, provider
`OpenAI` (matches the pin), 435,612 prompt tokens / 17,681 completion tokens (5,696 of them
reasoning), cost **$12.21636** — confirmed twice over, in `generation.json`/`run_metadata.json`
and independently in Viktor's own OpenRouter dashboard (transaction
`gen-1789201256-vlxCpCbrWwF2bnTxMClf`). The cost is real, not a sign of a broken run: it is
roughly 2.5x the script's $10/$50-per-M estimate because the 435,612-token prompt crosses
GPT-6 Astra's long-context pricing threshold (reported elsewhere at 272,000 tokens) and
`cache_write_tokens` shows the near-entire prompt paid a cache-write premium on top —
`send_audit_round.py`'s cost estimator accounts for neither and should before round 6.

GPT-6 Astra's report (`docs/audit_reports/round5_gpt-6-astra_2026-09-12/report.md`, 1,106
lines, ends cleanly on a "Bottom line" paragraph, not truncated) found three Critical Tier-1
defects, none previously on record:

- **F1** — measured volatility never reaches `calculate_stop_targets()`. The production call
  (`engine_core.py:950`) omits `volatility_state`, so stop/target geometry always uses the
  NORMAL multiplier regardless of actual conditions. The sibling call three lines below
  (`validate_risk_parameters`) does receive it.
- **F2** — entry quality can be scored for LONG while the actual plan and action are SHORT.
  `eq_trade_direction` is set from `short_signal`, which `generate_entry_signals()` zeroes for
  reasons that have nothing to do with direction (a reversal warning, macro disagreement, a
  gate miss) — so a fully bearish-confirmed setup can still get scored as a long entry, and
  `decision_model.py`'s BEARISH branch uses that score without ever checking `short_signal`
  itself.
- **F3** — an unavailable current-bar VWMA silently becomes the prior bar's reading.
  `indicators.py` correctly marks a zero-volume rolling window as NaN, then forward-fills it
  before anything downstream sees the absence; `validate_ohlcv` only rejects a series that is
  zero for its *entire* length, not a trailing zero-volume window, so nothing upstream catches
  it either.

**All three independently reproduced against live code this session, not just re-read from
the report.** Cloned `HEAD de7d1357b5e8425067c627915f1d9b5a90264642` (matches `MANIFEST.md`
exactly — also spot-checked 4 individual file hashes against the manifest, all matched), built
a Python 3.12 sandbox, and ran the actual functions:

- F1: the production call shape reproduces the report's own numbers exactly —
  `(95.968, 104.032, 108.064, 112.096)` vs `(94.5568, 105.4432, 110.8864, 116.3296)` if
  volatility were passed.
- F2: `generate_entry_signals()` really does return `(False, False)` on a fully
  `BEARISH CONFIRMED` setup carrying a small positive reversal warning; the same market state
  scores `82.62` through the actual (wrong) LONG path versus `100.00` through a direct SHORT
  calculation.
- F3: fed a 300-bar series with the last 20 volumes zeroed — `validate_ohlcv` accepted it,
  `add_technical_indicators` reported zero failures, and the decision-bar VWMA was genuinely
  NaN pre-fill, then silently carried forward. Also found: the code's own comment above the
  fill (`indicators.py`, around lines 766-771) claims this is "an honest absence already
  handled at the reader, not a silent one" — that claim is false about the code beside it,
  since the fill happens before the reader ever sees NaN. Same shape as the
  `decision_contract.py` comment this project has already caught being wrong once.

**RULED, 12 September 2026 — fix all three.** No decision to accept any as a limitation; all
three are confirmed, release-gate-blocking, and have a clear required action.

- F1: pass `volatility_state=volatility_mode` into `calculate_stop_targets()`, matching what
  the sibling call already receives.
- F2: **RULED** — derive `eq_trade_direction` from `raw_bias`/`detailed_bias` directly (the
  same signal `decision_model.py` already uses to pick the final action), not from
  `short_signal`.
- F3: **RULED** — route a decision-bar VWMA miss through the existing `failed(...)`/
  degraded-inputs path, the same treatment every other indicator failure gets. Accepted
  consequence, stated explicitly rather than discovered in a diff: a run that currently comes
  back clean can start showing DEGRADED and lose AGGRESSIVE eligibility once this lands.

Not yet done: any of the three fixes themselves. This patch is docs only — `code_hash` and the
golden snapshot are unmoved, and all three suite configurations are unmoved, since nothing
under `core/`, `models/`, `indicators/`, `data/`, `structure/`, or `utils/` was touched.

**Engineering Notes gap widens further.** Already owed entries for `4d99cdb` (GPT-6 Astra
ruling + round-5 prep) and `de7d135` (Luna Pro independence check made exhaustive); now also
owes one for round 5's actual send, its independent verification, and today's fix ruling.
Batch all of it into one entry pass once the three fixes land, rather than writing four
separate ones.

Requested-runs 4-6 from GPT-6 Astra's report (BTC-only failures, fallback equivalence,
test-effectiveness — all Major, not Critical) have not been run.*

---
*Prior head block (12 September, third patch) kept below for history.*


*12 September 2026 (third patch) — **The GPT-6 Astra ruling's evidence upgraded from two
named sessions to all nine, and a 2 September hedge closed for good.** Docs only, no code
touched. The round-5 ruling (below) rested on Viktor checking that Luna Pro's hostile
Constitution review and Step 8 both show `variant=standard` with no training routing. Doing
that check together surfaced something the ruling had glossed over: those two sessions were
never actually pinned to specific rows in the OpenRouter log — "Open, and not chased" already
said as much about all nine Luna Pro calls in that window. Rather than guess which two rows
were which, Viktor confirmed every Luna Pro call this project has made went through
OpenRouter (no consumer interface, so the "unknowable retention" branch of the 2 September
ruling is never reached) and then checked every one of the nine generations in the log
himself. All nine: `openai/gpt-5.6-luna-pro`, no `/flex` or `/fast` suffix, "No data
training." Which two of the nine carry the hostile-review and Step-8 names is still
unmapped and this does not map it — it no longer needs to be, for independence purposes.
Closes the 2 September hedge in "Independence — what kind of exposure, and what clears it"
("probably clean, not provably" → provably) and strengthens the round-5 ruling's own
paragraph with the same evidence. See both, further down this file, for the closures in
full.*

---
*Prior head block (12 September, second patch) kept below for history.*



*12 September 2026 (second patch) — **GPT-6 Astra RULED and selected as round 5's auditor;
round-5 audit-package prep delivered, nothing sent.** Viktor ran the OpenRouter
billing-export check the "position, not yet a ruling" note below was waiting on: both of
GPT-5.6 Luna Pro's exposed sessions (the hostile Constitution review and Step 8 itself) show
`variant=standard` with no training routing. By the existing rule — session exposure ends
with the session, training and lineage exposure never does — that limits OpenAI's exposure
to those two sessions rather than tainting the lab as a whole, so GPT-6 Astra is not
disqualified by them. **RULED: GPT-6 Astra selected.**

`docs/build/send_audit_round.py` repointed at `openai/gpt-6-astra` / provider slug `openai`
(the bare slug pins the standard tier and excludes the flex/fast variants, which need
explicit opt-in — verified by web search on 12 September since Astra postdates training
data, not assumed): `$10/$50` per million tokens, `MAX_OUTPUT_TOKENS` at 100,000 against
Astra's own 128,000 ceiling (the historical cross-round floor, 36,085, is unchanged).
`docs/build/build_audit_package.py` moved to `ROUND = "round5"` and, per **ruling 3, 11
September** ("fold Part 7 into round 5 rather than resending it"), folds
`commit_messages_PART7_ONLY.md` into the single upload set for the first time — the
two-folder `UPLOAD_THESE`/`PART7_LATER` split rounds 3 and 4 used is gone, since the file
was never actually attached by `send_audit_round.py` under either round and the split was
withholding nothing real. **Closes "Open — decisions" item 5.** Dry-run verified in the
sandbox: `build_audit_package.py` produces exactly 8 files in one folder (no `PART7_LATER`);
`send_audit_round.py`'s dry run shows the correct model, provider, pricing and a
$6.53–$9.03 cost estimate (up from round 3/4's package — the commit-messages file roughly
doubles it) and refuses to run further without `--send`.

New `docs/audit_package/item16_review_instruction_rev6.md`: lists the commit-messages file
as item 8, actually supplied (Section 4); fixes a dangling reference to the removed Section
13 inside Section 4a (found while reading the document for this revision, not previously
caught); corrects a stale claim in Section 5 that no attempt at this round had produced a
graded report — two later attempts, after Rev 5 was actually issued, returned complete
Parts 1-6 reports (GLM 5.3 Flash under Rev 4 / round3, Kimi K3 under Rev 5 / round4), and
the correction is explicit that neither report's content is disclosed to round 5's reviewer;
and adds a fifth disclosure naming GPT-6 Astra's lab relationship to Luna Pro (Rev 1's
compromised auditor) and how the billing-export check above resolves it, including what
that check can and cannot show. **This disclosure rewrite is audit-integrity prose, not
mechanics — Viktor may want to read Section 5 himself before it goes out.**

**Nothing was sent to OpenRouter.** `--send` was not passed and `OPENROUTER_API_KEY` was
not touched anywhere in this session; sending is Viktor's own action, on his machine, same
as every round before this one. All three suite configurations unmoved (429 / 315+103
skipped / 362-0-29) and `code_hash` unmoved (`e774b93d2b42bc41…`) — every file this patch
touches is under `docs/`, excluded by directory. Decision-log integrity checked directly: no
`logs/` directory was created by the suite runs used to verify this patch.

`docs/audit_package/round5/MANIFEST.md` is not shipped in this patch — like every prior
round's manifest, it is a build artifact with a build timestamp in it, produced by actually
running `python docs/build/build_audit_package.py`, which the command list below has Viktor
do himself before committing.

---
*Prior head block (12 September, first patch) kept below for history.*



*12 September 2026 — **Engineering Notes gap discharged, decision-log backup mechanism
built, handover check gained its 7th question.** Three no-decision items from “Open —
work” and ruling 5, delivered as one patch. Entries #94 through #97 (`bb6d222`, `4705d03`,
`e75f7be`, `0c7dec5`) added to `build_engineering_notes.py`'s Document History — run
`python docs/build/build_engineering_notes.py` to regenerate the PDF, still a deliberate
step rather than an automatic one. `decision_log_backups/` is new and tracked: the
6 September backup moved there from `Claude outputs/` (renamed, byte-identical, md5
confirmed), and `utils/decision_log_backup.py` takes a dated snapshot of every live
`logs/phase7_decision_log_*.jsonl` on command, refusing to silently overwrite one already
taken — a command Viktor runs, not a scheduled job, since nothing reachable from here can
register one on his machine. Eight new fixture-free tests
(`tests/test_decision_log_backup.py`) pin its behaviour. The handover check gained a
seventh question (ruling 5, first bullet, now CLOSED): does `git status --short` show
anything in the INDEX column. **`code_hash` moved, predicted and confirmed:
`2741062fae070f61…` → `e774b93d2b42bc41…`** — one new file, `utils/decision_log_backup.py`,
in a directory `code_fingerprint.py` does not exclude; nothing else in this batch touches a
non-excluded `.py` file. Suite 421→429 passed under pytest, 354→362 passed / 0 failed /
**29 errors** unmoved under `run_tests.py`, 307→315 / 103 skipped without `pandas_ta` — the
eight new tests, and nothing else, account for every moved count. Golden snapshot unmoved:
nothing on the decision path was touched.*

*__Still open, not decided this session:__ the `.gitignore` half of ruling 5 / decision 8
— should `Claude outputs/` get a `.gitignore` entry — flagged for Viktor rather than
defaulted, on the same ground he already ruled once for `round3/README.md`. Also still
open: tagging the ten suite-written records inside the live decision log itself (ruling 2's
other half). That file is gitignored and lives only on Viktor's machine, so it needs its
own approach rather than a git patch, and is not attempted here.*

*Decision 2's OpenRouter billing-export check (GPT-6 Astra) is next, and it is Viktor's to
run.*

---
*Prior head block (11 September) kept below for history.*



*11 September 2026 — **Item 14 / decision 2 is RULED and CLOSED at `0c7dec5`.** The risk
regime now classifies itself from ADX instead of from `trend_health`, so the "independent"
risk gate no longer reads the same number that is 0.30 of `bias_score`. Viktor ruled:
replace the coupling rather than delete the heuristic. `REGIME_LOW_TREND_HEALTH`/
`REGIME_HIGH_TREND_HEALTH` became `REGIME_CHOP_ADX = 20.0` / `REGIME_STRONG_ADX = 25.0`,
both thresholds already load-bearing in `indicators/trend_health.py` for the same two
market states. **`code_hash` moved, predicted and confirmed on three trees:
`47bc557119bb0350…` → `2741062fae070f61…`.** Suite on Viktor's own machine: 421 passed /
0 failed under pytest, 354 passed / 0 failed / **29 errors** under `run_tests.py` — the
watched error count unmoved. Golden re-baselined at six sites, all enumerated in
`0c7dec5`'s commit message; no decision field moved. Full reasoning, the incomplete
prediction and two wrong turns are in that commit message rather than repeated here.*

*__The live run did NOT reach the new code, and that is recorded rather than counted as
validation.__ AEROUSDT 4h, 11 September 22:50: stop distance 17.6% exceeded the 15%
maximum, so `validate_risk_parameters` returned early with `UNKNOWN` and never called
`classify_risk_regime`; volatility was EXTREME, which would have short-circuited it
anyway. The ADX branches are still unobserved on live data. The next run that lands in
them should be read with that in mind.*

*__Found by reading that panel, not fixed:__ the panel prints `RISK REGIME` but never
prints ADX — the number that now decides it is invisible to the operator, where
`trend_health` used to be visible on the TREND line. Still fully in the record
(`lineage.risk_inputs.adx`). Panel-only transparency regression, same class as GLM F-5.
Viktor's call whether the panel gains a line.*

*__Also landed 11 September, housekeeping:__ `bb6d222` moved the four `qwen_reasoning_*.txt`
into `docs/`; `4705d03` reconciled this file's body with `76380ec` after the Grok session
updated only the head block; `e75f7be` committed
`docs/Phase7_Sweep_Session_Commands.pdf`, which had been sitting untracked.*

***Five rulings were made on 11 September and only one of them is in a commit message.***
*They are written out under "Rulings, 11 September 2026" near the end of this file. The
release gate is still shut and nothing landed since round 4 has been re-audited.*

*__Engineering Notes stop at #93__ and do not cover `bb6d222`, `4705d03`, `e75f7be` or
`0c7dec5`. Up to four entries owed, two or three if grouped. Third session running that
this gap has reopened; the builder fix made publishing one command, not automatic.*

*9 September 2026 — **Kimi Finding 2 / decision 3 closed at `5e2e9f3`.** BTC agreement uses RAW_BIAS_THRESHOLD (label band) and signed correlation; golden re-baselined (btc_context only). Suite 345/0/29. Viktor ruled fix.*

*Updated 7–8 September 2026 (Grok session). **Sweep items 1–5 (Invented defaults and
fabricated readings) are done and committed at `22afea2`.** Five files:
`models/signal_router.py`, `models/decision_model.py`, `models/bias_engine.py`,
`structure/structure.py`, `core/panel_render.py`. **code_hash on Viktor's machine after
commit: `a64b48e468d35c8648e9f740aef5bdc9b886aec827a5931cd3693de52848957a`.** Suite:
345 passed / 0 failed / 29 errors. Golden: 8/8, snapshot unchanged (blast radius limited
to absent-key / failure paths). Wrong turn recorded: Part B insert omitted
@staticmethod on _optional_number; fixed before commit. Full chronological record:
`Claude outputs/Grok_session_2026-09-07_sweep_1-5_log.md` (if present) / session log.
Items 6–8 closed at `4d56f2a` (dead code, exit_watch NaN, test_live). Fourteen-item sweep **COMPLETE** at `c3b0d43` (items 9–14). No sweep engineering work remains.. **Independence: Grok has written code against the
Constitution; it is no longer a clean independent reviewer of this code.***

***Nothing ruled this session.*** *All eight items in "Open — decisions" remain Viktor's.
Release gate still shut.*

***Where the next session starts.*** *Sweep items 1–5 closed at `22afea2`. Next is items
6–14 (dead code, then false statements + structural), or cleanup of fingerprint
pollution from `Claude outputs/backup_pre_sweep_1_5/` (.py files not excluded).*

---
*Prior head block (6 September) kept below for history.*


*Updated 6 September 2026, sixth session. **All three of Claude's recommended pieces of
work are done, and so are the three findings the semantic audit turned up.** Engineering
Notes entries #83-90 published (`cdf9025`); the semantic half of the document audit done,
all eight PDFs read against tip `0f8e04a` (`0f8e04a`, `fc4b8fc`); its three new findings —
a stale procedure in the Audit Execution Instructions (partially closed: a correction
notice added, the rewrite itself still owed and only matters before a round 5), a stale
register count in the Documentation Standard (closed), and a crash bug in `run_tests.py`
under a genuine no-pytest environment (closed) — all fixed and landed `8051f5f`. See "Open
— work" below, item 3, and the three dated sections near the end of this file for each
piece. **`code_hash` moved with the `run_tests.py` fix, predicted and confirmed:
`6c4ef720baf991a020284fc7dfd81486ed2814fa6daafdbf84fbe2981a20a338`** — `run_tests.py` is
deliberately fingerprinted (its own test pins that). Suite confirmed unmoved on Viktor's
own machine: 412 passed/0 failed with `pandas_ta`, `run_tests.py` 345 passed/0
failed/29 errors, both checked before and after the `run_tests.py` patch. **Caught by the
end-of-session handover check: the Engineering Notes gap is open again** — four entries
owed (the audit and its three fixes), stopped at #90. See "Open — work" item 3.*

***Nothing has been ruled this session.*** *All eight items in "Open — decisions" are still
open and still Viktor's, decision 3 and decision 7 included. The release gate is still shut,
and nothing that has landed since round 4 has been re-audited by anyone.*

***Where the next session starts.*** *Everything from Claude's recommended order and the
semantic audit's findings is done. What's left is the fourteen-item sweep, assembled in
"The sweep of latent and Minor items" — the only piece of open work that touches the
decision path: three patches, three golden predictions, live runs owed. Not a ruling —
still Claude's own recommendation, and still Viktor's call whether or when.*

*__If the goal is opening the release gate, the sweep doesn't move it either.__ That runs
through decision 3 (Kimi Finding 2) and a re-audit, both of which are Viktor's.*

*__Environment note, 6 September:__ `reportlab` is installed on Viktor's machine and has now
rebuilt `Phase7_Engineering_Notes.pdf` there successfully. It is deliberately not in
`requirements.txt` — `docs/build/README.md` carries its own install line — so a fresh clone
still needs `pip install reportlab` before any document can be rebuilt.*

*The block below was written in the fifth session and is kept as written; it says "fourth
session", which is one of the small counting slips this project records rather than tidies.
Where it says 400 or 406 passing, those figures are historical.*

*Updated 6 September 2026, fourth session. **Rounds 3 and 4 are both in. Two reports,
sixteen distinct items between them, two real overlaps.** Round 3 was GLM 5.3 Flash (by
accident, and it stands as round 3 on the record rather than discarded); round 4 was Kimi
K3 through the API, the first complete report in four attempts. Kimi's Section 11
confirmation run was made on 6 September against unmodified code and **confirmed Finding 1
end to end**, and the fix for it has landed. **GLM F-7 as extended landed at `26a05dc`** —
and it turned out to be reachable rather than latent, which the 5 September note did not
know. **Kimi Finding 5 item 6 landed at `4678f45`**, and it too was reachable: the swing
detector needs 21 rows and the engine admits 20, so a 20-row frame got its own price back
as a structural level. **Kimi Finding 3, the largest of the Majors, landed at `1045748`** —
the record now carries a hash of the source itself, because six of the seven settings that
finding named cannot be held by a list of constant names at all. Suite: **400 passing,
0 failed**. Everything pushed.*

***Two live runs are on the record**, both AEROUSDT 4h on 6 September. 10:04 discharged the
run owed for F-7. 10:51 was made on the tree carrying the Finding 3 fix, before that commit,
and it found something neither reviewer did: the BTC block raised confidence and explained
it with a sentence its own label contradicts — by a mechanism that is **not** the one Kimi
Finding 2 describes. Nothing on the decision path is sitting unrun. See "Kimi Finding 3" at
the end of this file; the new observation is input to decision 3 and is not itself ruled.*

***The test suite was destroying the engine's decision record, and had already done it.**
Found on 6 September by running the suite against a clean clone and watching the
filesystem. Twenty-eight tests wrote real decision records into the live log; one deleted
`logs/` outright. The 10:04 run's raw record and the three synthetic Section 11 records
were lost that way before anyone noticed. A pristine checkout of `717ea30`, seeded with
marker files, came out of a **400-passing** suite run with every marker gone. **Fixed and
landed at `fc35a2f`**, after the first attempt failed on Windows for a reason worth
reading — see "The suite was destroying the decision record" near the end of this file.
**Decision 7 has been restated as a consequence and still needs your ruling.***

***The document set was audited end to end on 6 September**, and the mechanical half is
clean where it matters: all three audit-package manifests verify byte-for-byte against
their recorded build commits, so what each reviewer graded is provable. Two structural
problems came out of it — no build script can write into the repository, which is why the
Engineering Notes gap has grown at every handover; and this file carried false statements
about the decision log. The semantic half, reading the eight PDFs against the current
state, has NOT been done. See "The document audit" below.*

*The release gate is **still shut**. "Unresolved" means no fix has landed **and been
re-audited**, and nothing landed since round 4 has been re-audited by anyone. One Major
from round 4 plus most of round 3's eleven stand unfixed. Eight decisions are open and all
eight are Viktor's — see "Open — decisions" near the end of this file, which is the section
to read first, together with "The round-3 versus round-4 comparison" above it.*

*The earlier state of this block — "what is left to fix is empty", suite 319, one thing
standing between here and sending the package — was true on the evening of 5 September. It
is kept in the history rather than in this paragraph.*

*Eleven defects found by an audit run that never produced a report, all verified against
source, four fixed. Two more found by running the engine and reading the panel — including
one introduced by a patch the same day, which every test in the suite passed because they
matched substrings and not shape.*

> **This project now has two goals with two different endings.** It is the technical
> portfolio project in Viktor's 2026–2028 career plan and the intended *examensarbete*,
> AND it is an engine he intends to finish. Those complete at very different times, and
> the first must be banked and tagged before the second begins. See "Two goals, and the
> order they finish in" immediately below — read it before planning any work.

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

**What this ruling is not.** It is not a compromise, and it did not weigh a model's
capability against its contamination. The argument is about mechanism: if nothing carries
between sessions, nothing carries. Had a mechanism been found, Kimi K3 would stay out
regardless of its rank — and if Kimi were ranked fortieth rather than fourth, the ruling
would be word for word identical.

The distinction matters well beyond this decision. A rule reading "an exception was made
because the model was valuable" is one anyone can invoke later to justify anything. A rule
reading "session exposure has no mechanism of harm under these conditions" can be
attacked, tested and overturned on its merits.

**Consequences.**

- Viktor's "relatively OK" grade on the Luna Pro Step 8 stands, and for the right reason.
  The only thing short of fully fine is that the hostile review may have run somewhere that
  retains conversations, which is now unknowable. Probably clean, not provably.

  **CLOSED 12 September 2026 — provably, not just probably.** Viktor confirmed every Luna
  Pro call the project has made ran through OpenRouter, not a consumer interface, so the
  "somewhere unknowable" case above does not apply and the ruling's own default (unknowable
  retention, treat as permanent) is never reached. He then checked every Luna Pro generation
  in the OpenRouter log himself — not only Step 8's, all of them, since which exact call was
  the hostile review was never pinned down (see "Open, and not chased" below) and no longer
  needs to be: each one shows `openai/gpt-5.6-luna-pro` with no `/flex` or `/fast` suffix and
  a data policy of "No data training." Checked directly this time, three of them read from
  the log together in a working session (Sep 3, 06:37 AM / 05:20 AM / 05:00 AM — Model ID
  and data policy confirmed identical on all three), the rest checked by Viktor and reported
  clean. This is the check the round-5 head block's GPT-6 Astra ruling already rested on;
  this closure makes its evidence exhaustive rather than assumed.
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
| ~~two dead constants (#6)~~ | done | patch L, 5 Sept |
| ~~HTTP timeout, `DataFrame` inside the `try` (#c)~~ | done | patch M, 5 Sept |
| ~~directory created at import (#d)~~ | done | patch M, 5 Sept |
| ~~RSI/ATR smoothing (#5)~~ | done | patch L, 5 Sept — smoothing matched |
| ~~entry sub-scores vs printed total~~ | done | patch Q, 5 Sept |
| ~~entry-zone fabrication (#4)~~ | done | patch P, 5 Sept — plus the inverted display |
| ~~correlation alignment (#a)~~ | done | patch O, 5 Sept |
| ~~continuation floor (#b)~~ | done | ruling 3, patch I, 4 Sept |

**The table is empty.** Five patches closed the seven rows in one day, three of them
moving printed numbers and two of those requiring a golden re-baseline. Every one shipped
with its prediction stated before the run and checked afterwards.

Two counting notes, kept because they are the kind of error that hides work: this table
once said "four or five patches" above seven rows, and on 5 September a session summary
said "six queued fixes" against the same seven. The rows are the thing to trust, never
the sentence above them.

### Before the audit can be sent — do not skip these

Status as of the end of 5 September is in the section at the foot of this file.

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
6. **Search the built package before sending it.** Added 5 September, after a
   grep of round 3 found the instruction's own stop condition firing on the
   bundles it ships with. Not a reading task — a mechanical search for outcome
   language, prior auditor names, and severity words.

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
15. ✅ Patches I, J, K — rulings 1, 2 and 3, 4–5 September. See that section.
16. ✅ Patches L, M, O, P, Q — the whole of "What is left to fix", 5 September. See
    "Patches O, P and Q" at the end of this file, and "Patches L and M" above it.
17. ◐ **The pre-audit checklist**, in "Before the audit can be sent" above. Items 2, 3,
    4, 5 and 6 are closed; item 1 is one command away and waits only on the package
    being rebuilt against the corrected rev 4. See the section at the foot of this file.
18. ⬜ The re-audit itself. Which model runs it is still Viktor's to rule.


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

## Rulings 1, 2 and 3 — built and landed, 4–5 September 2026

The three rulings left open on 3 September were all built. Suite 226 → **251 passing**.

### Ruling 3 — the silent continuation zeroing (patch I)

`bias_engine` never knew which way the trend pointed. It inferred direction from the
sign of `continuation_strength`, which meant that whenever continuation was zero the
engine silently read the trend as flat — regardless of what the trend actually was.

`indicators/trend_health.py` had computed the direction all along and thrown it away.
Patch I exposes it (`trend_direction`, `trend_direction_sign`) and makes
`trend_direction_sign` a **required** parameter of the bias engine, validated to
`(-1, 0, 1)`, rather than an inferred one:

```python
trend_direction = int(trend_direction_sign)
if trend_direction not in (-1, 0, 1):
    raise ValueError(...)
```

The ruling was made **after** the behaviour was measured across 9,800 live bars, not
before. That order is the point — see rule 36.

### Ruling 1 — a direction-blind number was being offered as directional support (patch K)

Reason strings said `"with strong trend health ({trend_health:.0f}/100)"`. Trend health
is a magnitude; it says nothing about which way. Offered as a reason for a BULLISH or
BEARISH call, it read as directional evidence that it was not. Replaced with:

```python
trend_note = f"trend strength {trend_health:.0f}/100 ({_dir_word})"
```

where `_dir_word` comes from `trend_direction_sign` — which only exists because of
patch I. A correction to the record: Claude had claimed the panel's `TREND` line carried
the same defect. It does not. It prints two true facts side by side and asserts no
relationship between them. Only the reason strings made the claim.

### Ruling 2 — a hard minimum bias strength (patch K)

An ACTION could be issued off a bias that leaned barely at all. `MIN_ACTION_BIAS = 30.0`
in `models/decision_model.py`, added to `FINGERPRINTED_MODULES`:

```python
if raw_bias in ("BULLISH", "BEARISH") and bias_strength < MIN_ACTION_BIAS:
    reasons.append(...)
    return "WAIT"
```

Claude first argued for collapsing this into the existing `RAW_BIAS_THRESHOLD` and
reversed that while building it. They answer different questions: `RAW_BIAS_THRESHOLD`
asks *does the blend lean far enough to call a side*; `MIN_ACTION_BIAS` asks *is that
lean strong enough to act on*. One number cannot be tuned for both without one of the
two answers becoming an accident of the other.

Seven existing fixtures in `test_no_risk_free_conviction.py` built `bias={"raw": ...}`
with no score at all. They were **completed**, not worked around — the alternative was
relaxing a floor to accommodate incomplete test data, which is how a floor stops meaning
anything.

### Patch J — `volume_agreement` extracted

Same treatment as `macro_agreement` in patch D: a four-branch module-level function in
`core/engine_core.py`, so agreement logic is testable in isolation rather than only
observable through a full run. Eight tests.

### What went wrong while building these

- **Three stale-base rebuilds.** Patch J was generated against `engine_core.py` staged
  before patch I landed (39 failures). Patch K was rebuilt twice against a
  `decision_log.py` missing the `models.risk_model` anchor. See rule 35.
- **A too-crude substring assertion in Claude's own volume test** — asserting on
  `"support"` in a note that quotes a label reading `BULLISH VOLUME SUPPORT`. Rule 30 was
  written three days earlier, about exactly this, and was still violated in a test written
  to guard its cousin. Knowing a rule and applying it are different acts.

### The golden diff, patch K

Predicted five fields and produced exactly five: `run_hash` ×2, `archive_path` ×2 (it
derives from `run_hash[:16]` — rule 33), and `module_constants` gaining
`models.decision_model.MIN_ACTION_BIAS = 30.0`. Nothing else moved. Re-baselined; live
run confirmed the new wording and a `bias_score` of 56.72 clearing the floor.

### Usage discipline, adopted 5 September

Chat context is charged in full on every turn, so a long thread pays for its own history
repeatedly. Two changes, decided by Claude and accepted by Viktor:

1. **When a patch ships with a commit message, the chat reply is only the predictions to
   check and the commands to run.** The reasoning belongs in this file, where it is
   cheaper and where it survives.
2. **Start a fresh session when a thread has served its purpose.** "Continue Phase 7" is
   sufficient to resume — provided the handover check has run, which is what makes this
   safe rather than reckless.

This must not become a reason to explain less. It is a reason to explain in the right
place.

## Patches L and M — built and landed, 5 September 2026

Four of the seven rows in "What is left to fix" closed in two commits. Suite 251 → **270**.
Neither patch moved the golden snapshot, and both said so before running.

`fa68197` — patch L, findings 5 and 6
`0603dff` — patch M, findings (c) and (d)

The reasoning is in the two commit messages, in full. What belongs here is the part that
outlives them.

### Unreachable is not the same as safe (finding 6)

Two fabrication constants survived in `engine_core.py` after item 9a removed their
siblings from `indicators.py` and Finding 3 removed them from `entry_model.py`:
`{"trend_health": 50.0, ...}` and `atr_val = ... else current_price * 0.02`.

Both were unreachable, which is *why* they survived two passes. `compute_trend_health` is
total — every path through it returns a dict — so nothing could reach the first handler.
Section 2 halts when ATR is absent and `structure.py` returns a copy of that frame, so
nothing could reach the second.

The trend one was worse than a fabrication, and the negative control is what showed it: its
substitute dict has no `trend_direction_sign`, which the next stage reads by subscript
*outside* the try. Run against pre-fix code, a broken trend contract does not degrade the
run — it dies with `KeyError: 'trend_direction_sign'`, reported as neither a trend failure
nor a bias failure. That was found by running the test, not by reading the code.

### A fallback claimed to be an equivalence and was not (finding 5)

The RSI and ATR fallbacks smoothed with a simple moving average. `pandas_ta` smooths both
with Wilder's RMA. So "recomputes the same quantity by another route" — the claim in
`add_technical_indicators`' own docstring, and the stated grounds on which
`test_degraded_state` asserts these paths are **not** degradations — was false.

On the pinned fixture, final bar: RSI 84.45 against `pandas_ta`'s 69.14, and an ATR 1.80%
low. That test had been passing on a false premise for as long as it existed.

The choice the table flagged — match the smoothing, or record which path ran — was Claude's
to make (Viktor: *"None needs a ruling from me"*) and was made by reading the repo rather
than by preference: `test_degraded_state` already asserts this fallback costs nothing.
Recording the path would leave that assertion false and add a flag to explain why.
Matching makes it true.

### Two defects found by the verification step itself

Neither was on the list. Both were found because the process ran, not because anyone
looked.

- **The `pandas_ta`-free run could not run at all.** `test_macro_agreement` and
  `test_volume_agreement` import a pure function whose module chain reaches `pandas_ta`,
  so both **errored at collection** and pytest reported "2 errors" and ran *nothing*. The
  result for the other 251 tests was unobtainable, silently, since those files were
  written. `pytest.importorskip` now makes it the skip it should have been: 0 errors,
  159 passed, 88 skipped.
- **The module-level simulator defeated a deliberate lazy import.**
  `SignalRouter.__init__` imports `engine_core` inside the function, which is what lets
  `live_trading` be imported without `pandas_ta`. `live_trading_simulator =
  LiveTradingSimulator()` at module scope called that `__init__` at import time and undid
  it. Verified both directions rather than argued: pre-fix `import live_trading` raises
  `ModuleNotFoundError`; post-fix it succeeds.

### Found by running the engine, and not yet fixed

`main.py` on `fa68197` printed:

```
ENTRY ZONE    : $0.4981 - $0.4918
```

The lower bound is above the upper. `engine_core` assigns `EMA_20` to `zone_lower` and
`EMA_50` to `zone_upper` unconditionally, so in an uptrend they come out inverted.
`entry_model` swaps them before scoring, so the arithmetic is right and **the display is
wrong**. It belongs with finding (4), which touches those exact two lines. Not yet checked:
whether any other reader of the zone is missing the same swap.

### What is left

Three rows, all of which change printed numbers:

1. entry sub-scores vs printed total — panel only
2. entry-zone fabrication (#4) — plus the inverted display above
3. correlation alignment by timestamp (#a)

Each needs its own patch, a golden re-baseline, and a live run before it commits.

## Patches O, P and Q — the table is empty, 5 September 2026

The last three rows, in three commits. Suite 270 → **319**.

`2bbb40e` — patch O, finding (a), the BTC correlation
`95b1002` — patch P, finding (4), the entry zone
`127d947` — patch Q, the entry sub-scores

Full reasoning is in the three commit messages. What belongs here is what outlives them.

### Two of the three were latent, and that is the pattern of this whole batch

Finding (a): correlation and beta were computed by pairing AERO and BTC **by position**
after both series' timestamp indexes were discarded. In the ordinary case both fetches
return the same 450 candles, so positional pairing IS timestamp pairing and the code is
correct by accident. On the pinned fixtures the two indexes share all 450 timestamps and
old and new agree to the last decimal — which is why the golden snapshot did not move.

It stops being harmless the moment the series differ by one bar: a candle closing between
two sequential API calls, an exchange gap, a stale feed. Measured on the fixtures by
dropping one BTC bar from inside the window, all 31 positions: the printed correlation
moved by a median of 0.105, beta by 0.135, and **the printed label changed in 4 of 31**.
`n_observations` read 30 either way, so the panel's own evidence line gave no tell.

Finding (4): the same shape. `close * 0.99 / close * 1.01` for a missing EMA pair is only
ever reached when an EMA is missing, which does not happen on a healthy run. Five
fabricated constants across two files, and the worst was not on the list — a close price
that could not be read became `$1.00`, so a run with no data at all reported ACTIVE ENTRY
ZONE, 30 of 30, against a price nobody read.

**The lesson to carry, and it is now four for four:** the fabrications that survive
audits are the unreachable ones. Item 9a, Finding 3, Finding 6 and Finding 4 all removed
constants from paths that no healthy run takes. Unreachable is not safe — it is one edit
to an invariant elsewhere from being the live path, and nothing tests it in the meantime.

### The one that was neither latent nor listed

Patch P also fixed a display defect found by **reading the panel**, not the code:
`ENTRY ZONE : $0.4981 - $0.4918`, the lower bound above the upper, because `engine_core`
put EMA_20 in `lower` and EMA_50 in `upper` unconditionally. `entry_model` swaps them
before scoring, so the arithmetic was right the whole time and only the display was
wrong. No test could have caught it; every test asserted on the numbers.

Three of this project's defects have now been found by running the engine and looking at
the output. That remains the cheapest detector it has.

### What patch Q was actually about

    ENTRY QUALITY : 45.18/100
        |-- ... five components summing to 39

Recorded on 2 September as "not wrong, unexplained". For a number an operator is meant to
act on, unexplained is its own defect: they either work out the gap themselves or stop
trusting the number.

Three causes, none of them visible anywhere — sub-scores rounded for display while the
total was not, three confluence multipliers applied after the sum, and a clip at 100. And
a fourth thing the clip was hiding: **the five components add to 102, not 100**, while the
docstring said 100 directly above the list. With full confluence a perfect setup reaches
118.08 and loses the difference silently.

The panel now prints the subtotal out of 102, the multiplier broken into its three
factors, and a Clipped line when the clip actually fires. The column adds up.

### A structural problem this exposed, recorded not fixed

`signal_router.py` rebuilds the entry block **field by field**. Anything the engine adds
that its list does not name is dropped before the panel or the decision log sees it —
silently, with no error and no failing test. Patch Q's nine new fields vanished exactly
that way on the first attempt; the reconciliation lines simply did not appear.

The entry block's shape is now declared in four places: `entry_model`'s return,
`engine_core`'s dict, `signal_router`'s rebuild, and `decision_contract`'s TypedDict.
Four copies of one fact, and this is the defect class the project has recorded most
often. Restructuring it is larger than any one finding warranted, so it is written down
here instead of done quietly.

### Mistakes made building these three

- **A verify tree built on a stale base.** Patch O was first verified against a copy taken
  before patch M landed and reported 279 tests instead of 291. The patch itself was fine
  — M touches none of O's files — but the verification was not. Caught by the arithmetic,
  not by remembering rule 35.
- **Rule 30, twice more.** A panel assertion matched `SWING STRUCT`'s own "not located
  this run", and another matched the panel *title* because it contains the words "ENTRY
  QUALITY". Both were substring checks that could not see the shape of what they matched.
  The rule was written on 3 September and has now been violated on 4, 5 and 5 September.
  It is a candidate for a mechanical check, per rule 37.
- **A test that passed against pre-fix code.** Patch Q's denominator check looked for
  `"/30` — the literal preceded by a quote — which the old code never contained, because
  the denominators sat inside f-strings. It was caught only because the negative control
  came back eleven red and one green, and the green one was wrong. This is the vacuous
  assertion from 3 September, and the negative control is the only reason it did not ship.

### One more thing, observed and not chased

During a full-suite run the sandbox's egress proxy logged two rejected CONNECTs to
`api.mexc.com:443`. Every test that routes or fetches sets `base_url` to a dead local port
first, and each was checked; the source was not identified. Recorded because a suite that
can reach the internet is a suite whose result depends on the network.

### What comes next

Not the gate. The pre-audit checklist in "Before the audit can be sent", above — five
items, and the first two are the ones skipped last time: rebuild the package against
current code, and commit everything before building it. The Engineering Notes are still
in arrears and now stop twelve patches back.

## The pre-audit checklist — all six closed, 5 September 2026

`ab531d7` — the Engineering Notes brought current, entries #57–#70
`1489b43` — rev 4 of the reviewer instruction, and the builder pointed at round 3
`5c0d42d` — Section 2 scoped to the Constitution file, entries #71–#72
`2674d7c` — the regenerated round 3 manifest committed
`c4d6969` — rev 4's own disclosure corrected, after item 6 was run against the package
`1083dc5` — the manifest rebuilt at `c4d6969`, all 71 hashes unchanged

Suite 319 throughout; none of this touches engine code.

### What closed

**Item 5, the Notes.** They stopped at Entry #56 on 3 September while three rulings and
eight patches landed. Entries #57–#70 cover 4–5 September; #71 and #72 cover this
afternoon. 47 pages to 58.

**Item 3, rev 4.** New file; revs 1–3 preserved. It carries the fix-first-then-compare
ruling in Section 4a, an honest account of the failed attempts in Section 5, the
unreachable-branch instruction in 7.1, a paired-series example in 7.6, and a new
Section 13.

**Item 4, the holdout.** `_prior_observations()` concatenates the four
`qwen_reasoning_*.txt` verbatim into `PART7_LATER/prior_observations_PART8_ONLY.md`.
The reviewer is asked for a **Part 8** reconciling its own findings against those
eleven, including where its method did not reach one, and is told plainly that the
comparison measures the review process rather than marking it.

**Item 2, commit first.** Both commits landed on a clean tree, so the manifest records a
HEAD that actually contains what it packaged.

**Item 6, search the package.** New. Run for the first time against
`round3/UPLOAD_THESE/`, and it found three errors in rev 4's own disclosure — see below.
It is now a standing pre-send step rather than a one-off.

### The builder now writes round 3

`ROUND = "round3"`. `round2/` is the only record of what the previous attempts were
given, and it is the baseline a new report gets compared against; rebuilding over it
would have destroyed that while contradicting the script's own docstring. A missing
input now refuses the build **before anything is written** — the first version of that
check refused from inside the copy loop, after five files had reached `UPLOAD_THESE/`,
which is the exact populated-but-incomplete state the folder layout exists to prevent.
Found by the negative control, not by reading it.

### The finding that stopped the send

Section 2 told the reviewer to stop if the **code bundles** contained a named prior
auditor, a count of Compliant and Non-compliant items, or a list of Critical findings.
They contain all three: verdicts for Items 3, 6, 16, 18, Tier 3 items 3 and 4, and Tier
4 item 2; the phrases "five Criticals", "four Criticals" and "the third Critical"; and
Luna Pro and GLM by name. A reviewer following the instruction would have refused — a
fourth attempt ended by the package, the third in a row.

Ruled: scope the condition to the Constitution file, count and disclose what the bundles
hold, ask for the reviewer's own verdict on all forty-four with a Part 6 note on whether
a comment moved it. The comments stay, on Section 4's argument. The structural fix is
above, under "worth revisiting", and is deliberately after the re-audit.

**The part worth carrying:** a reviewer that stops tells you loudly. The failure one step
over is silent — a reviewer that reads "Item 18, kept Compliant" and grades Item 18
Compliant produces a report that looks entirely ordinary. Rule 28's test, applied to the
audit process rather than to the code.

### Item 6, first run — what the search found

The package is clean where it matters, and this was checked rather than assumed:

- The Constitution audit copy is 29 pages with 29 form feeds and no Version History row
  recording an outcome. Every Compliant / Non-compliant / Unknown in it is rubric text
  defining the schema. The 38-to-29-page truncation holds.
- `MANIFEST.md` against the two bundles: 71 files in both, path lists identical, and all
  71 SHA-256 values recomputed from the bundle bytes and matching. The manifest is not a
  claim taken on trust.
- The seven-rules-with-a-prior-verdict count is correct as stated.
- `execution_transcripts.md` carries no reviewer name, no verdict, no count.

Rev 4's counted disclosure was wrong in three places, all fixed in `c4d6969`:

1. **Five** distinct Critical-count phrases in the bundles, not three. "the first
   Critical" and "the last Critical" were missed.
2. **Three** named AI parties, not two. Claude is named in both bundles, twice as having
   been overruled by Viktor — the implementing party rather than a reviewer, which is why
   the sentence did not cover it, and the same class of exposure regardless.
3. The disclosure covered only the two code bundles. `version_control_history.md` is a
   third file in the package and names `luna_pro_audit_report.md` and the four
   `qwen_reasoning_*.txt` by filename. Neither's contents reach the reviewer before
   grading, and a filename in a diff-stat does not trip the stop condition — but leaving
   it undisclosed, after three attempts died on the package, was not a risk worth taking.

**Found by grepping the artifact, not by re-reading the instruction**, which could not
have found it: the prose was internally consistent and the error was in the counting.
That is the second time in two days the artifact caught what reading did not, and it is
the argument for item 6 being standing rather than a one-off.

### Found by the search, and deliberately not fixed

Two code comments cite `claude/phase7-rulings.md` as where a ruling is recorded — once in
the source bundle, once in a test docstring. There is no `claude/` directory in the
repository. It is a traceability claim pointing at nothing, and it goes to the auditor as
it stands: the ruling of 5 September defers moving the audit narrative out of code
comments until after the re-audit, on the grounds that editing the codebase now hands the
auditor an artifact groomed for its grader. Correcting this would be exactly that.

Separately, from the generated history and **not verified by running git**:
`version_control_history.md` reports 117 commits authored "Your Name" on 58 and "unknown"
on 59. No commit on the branch carries a configured identity. The builder prints `%an`
verbatim, so this is a fact about the repository rather than a defect in the package.
Left alone — rewriting authorship across 117 commits to look better for an audit is worse
than the finding.

### Ruled 5 September: round3/README.md gets no .gitignore exception

Claude's call, delegated. `MANIFEST.md` is excepted from `round*/*` because it is the
provenance record — it names the commit the bundle was built from and hashes every file
in it. `README.md` carries no provenance the manifest does not: its build timestamp and
commit hash are the manifest's first two lines, and every sentence of its prose is
already tracked, in `docs/build/build_audit_package.py` lines 550–562, where it is
generated. So the "which folder to upload" note does reach the repo — as the builder
source that writes it. Committing the README would store the same content a third time
and add a must-not-be-hand-edited file to a repository whose tracked files exist to be
edited.

The safeguard against uploading the wrong folder was never that note in any case. It is
the `UPLOAD_THESE/` and `PART7_LATER/` split, which puts the safe action in the directory
name, and the builder emptying both folders on every build so a stale file cannot survive
into a package.

### A prediction that did not hold

The rev 4 commit predicted the commit count would go 117 to 118. It went to 119. `2674d7c`
had landed at 12:37, between the 10:29 build and the patch — the manifest commit, the
checklist item that was owed and had already been done. The 117 came from the
`version_control_history.md` built at 10:29 and was stale by the time it was used.

A number read off a generated artifact and treated as current. The same shape as Entry
#71's withdrawn claim about file modification times, and as the finding that the record
of the audit attempts had to be corrected from the provider's bill. Recorded because it
is the third instance, not the first.

### The record corrected from the bill

Rule 29 a second time. The provider log for 2 September reads Qwen 10:53, Qwen 15:38,
Qwen 15:42, Kimi K3 15:58. Entry #50 has the last two the wrong way round, so the eleven
observations came from a Qwen run **before** Kimi. `UPLOAD_THESE/` was written at
16:47:56, after all four calls: no attempt at round 2 has ever received it, which is now
proved rather than inferred. Entry #22 names DeepSeek V4 **Pro**; the bill says **Flash
0731**.

Claude's own error, withdrawn in Entry #71: file modification times were offered as
evidence of when a model ran. They record when a transcript was saved.

Open, and not chased: nine Luna Pro calls between 27 August and 3 September, more than
the record accounts for, three of them on 3 September mapping to nothing; and Kimi K3's
2 September call returning 36,085 output tokens, which is not the truncated stub the
record describes when leaving its spent status undecided.

**The independence half of the Luna Pro gap no longer needs chasing — see "Independence —
what kind of exposure, and what clears it," Consequences, CLOSED 12 September 2026.** Which
specific call was the hostile review and which was Step 8 is still not mapped, and this
does not map it. What changed is that the mapping stopped mattering for independence: every
one of the nine calls was checked and every one shows no training routing, so it is moot
which of them carries which name. The mapping itself — if anyone ever wants it, for a
reason other than independence — is exactly as unchased as this paragraph already said.

### Ruled 5 September: Kimi K3 runs round 3 — WITHDRAWN THE SAME DAY

**This ruling was withdrawn on the afternoon of 5 September. Its central reason was
built on a misattribution and inverted once the record was corrected. It is kept in
full below, unedited, because the reasoning is what went wrong and deleting it would
hide that. See "The transcripts were Kimi's all along" further down.**

Viktor's call, delegated to Claude on the evening of 5 September — he had reserved the
model choice for himself, then handed it over and set the confound aside. Recorded here
because it is his to reverse.

**The ruling. Kimi K3 audits round 3.** The model choice and the Part 8 confound are one
decision, not two: choosing a non-Qwen auditor is what dissolves the confound, and
choosing Qwen is what would have required handling it.

**Why.**

1. **Part 8 becomes informative.** The eleven prior observations in
   `prior_observations_PART8_ONLY.md` came from the Qwen run at 15:42 on 2 September —
   established from the provider's bill, not from recollection. Part 8 asks the auditor
   whether a prior observation moved its grade. Asked of Qwen, agreement cannot be
   distinguished from family consistency and disagreement cannot be distinguished from
   drift, so the answer carries no information in either direction. Cross-family,
   agreement is evidence.
2. **Round 3 is a first look.** Qwen has now read an earlier build of this source and
   produced eleven findings on it. A fourth Qwen pass is a re-read. Kimi has never
   completed a pass on this codebase.
3. **Rank.** Kimi K3 sits fourth on the coding leaderboards, above Qwen3.8-Max — as the
   2 September record holds it. Not re-verified here; the leaderboard may have moved in
   three days.
4. **Independence is not the discriminator, and does not block Kimi.** Every request in
   the provider history is `variant=standard` with training routing off, so Kimi's
   27 August truncation and its 2 September stop are both session exposure, which the
   2 September ruling clears with a fresh call. The same rule is what keeps Qwen
   eligible. This is the removal of an objection to Kimi, not an argument for it.

**The strongest case against this ruling, which is the case for Qwen.** The step has
failed three times. The package was built for Qwen and the instruction was written with
it in mind. Changing the model changes a fourth variable on a step that has never once
completed, and the discipline this project runs on is to change one thing at a time. The
answer is that all three failures were the PDF, the PDF is fixed, and the model was never
the variable under test — but the objection is real, and it is recorded rather than
dismissed.

**What could reverse reason 2.** The provider log shows Kimi's 2 September call returning
36,085 output tokens. The attempts table describes that attempt as receiving an unreadable
PDF, saying so, and stopping — which is not 36,000-token behaviour. Either the table is
wrong about what Kimi did that day, or that row is something else. It was not resolved. If
Kimi did in fact grade the round-2 bundle, it has read an earlier build of the source and
round 3 is not a first look for it either. That does not change eligibility, because
session exposure still clears, and it does not change the ruling, because reasons 1 and 3
stand without it. It is recorded because the reasoning above is weaker than it reads if
that row is what it might be.

**Two conditions on the run, both from this project's own record.**

- **Set the max-output ceiling before the call.** Kimi is the model that burned a full
  input charge at `finish=length`, 16,384 tokens, on 27 August. Check it, every run.
- **Through the API, not a chat interface.** Session exposure demonstrably clears only
  where the training opt-out is a matter of record.

## The transcripts were Kimi's all along — 5 September 2026, afternoon

The largest correction this project has had to make. It began as a request to read
the old Kimi chat room before spending a call on it, and ended with a withdrawn
ruling, a downgraded auditor and two evidence sets that were never going to reach
version control.

### What the room contained

Six documents, saved from the Kimi K3 room of 2 September. They are **not** Parts 1-6
of a report. They are one continuous reasoning trace, split at the chat interface's
own message boundaries, ending mid-sentence at "**A13 path". Kimi produced 36,085
tokens of reasoning and no report. That closes the open question about the
36,085-token bill row.

### The finding

The four files in the repository root named `qwen_reasoning_1.txt` through
`qwen_reasoning_4.txt` are that same Kimi transcript.

Verified rather than inferred: with all whitespace stripped, the two are identical for
**57,631 characters from the first byte**, both opening "Let me start by carefully
reviewing the instructions and the materials provided." Two different models do not
coincide on 57,000 characters.

`prior_observations_PART8_ONLY.md` is a header plus those four files. **So the eleven
prior observations are Kimi's work, not Qwen's.**

### Why nobody caught it

The repository copy is lossy — about 60,000 characters shorter than the room copy,
with material missing from the middle. One of the passages in the gap is the model
identifying itself:

> the instruction says I'm "Qwen3.8-Max" — I'm not; I'm Kimi (Moonshot AI) ... If the
> ledger records "Qwen3.8-Max" but the actual reviewer is Kimi, the ledger is wrong —
> that's material to the audit's integrity.

It said so explicitly, in the section of the instruction written to make it say so,
and the sentence never reached the repository. Every document downstream inherited the
filename instead: Entry #50, the attempts table, the Part 8 document, the 5 September
correction from the bill, and the morning's ruling.

The 5 September correction is the instructive one. It reasoned from call timestamps —
Qwen 15:42 before Kimi 15:58 — to conclude the eleven came from Qwen. The inference
was sound and the conclusion was wrong, because the bill records **what was called**,
not **which output was saved under which name**. Rule 29 says prefer the system that
recorded it as a side effect of its own job. The transcript is that system, and it was
sitting in the repository under the wrong name the whole time.

### What it cost

The morning's ruling put the confound on Qwen and sent the package to Kimi. It is
Kimi-audits-Kimi that makes Part 8 uninformative. The ruling was exactly inverted.

## The GLM 5.3 Flash run — an accident that produced a report

The Chatroom tab was left on **Auto Router** rather than a named model. The router
chose GLM 5.3 Flash, and the round-3 package went to it.

| field | value |
|---|---|
| date | 5 September 2026, 13:39 (11:39 UTC) |
| model | `z-ai/glm-5.3-flash-20260826` via Auto Router |
| serving provider | BaseTen |
| input / output | 251,148 / 11,475 tokens |
| cost | $0.0434, 102.7 s |
| package | `round3/UPLOAD_THESE/` at `c4d6969`, instruction rev 4 |

It read the package: Part 1 names all 44 rules, six checked against the Constitution
text and all six trace. Its model-identity check fired correctly — the first line
states it is not Qwen3.8-Max.

**Verdict returned:** 26 Compliant, 13 Partially compliant, 1 Not verifiable, 0
Non-compliant. Eleven findings, all Minor. Gate reported met on its findings alone,
with its own caveat that it is not claiming no Major or Critical defect exists.

### Verified against source, three of eleven

- **F-2, `pct_slope` unconsumed** — CONFIRMED, and stronger than filed: the name
  occurs exactly once in the source bundle, its own `def`. No call sites.
- **F-4, `_merge_btc_context` fabricated defaults** — CONFIRMED, `signal_router.py`.
- **F-7, `risk.get("risk_valid", True)`** — CONFIRMED, and **under-scoped by the
  report**. GLM filed it against `live_trading.py` and justified Minor on the grounds
  that the module only writes a simulated-order log. The same permissive default sits
  in `decision_model._determine_final_action` — the trade-authorization gate — and in
  `signal_router._build_decision_object`. A risk block that is a dict but missing that
  key means risk was never assessed and the decision engine reads it as passed. GLM's
  severity argument does not cover either.

That miss is what the depth-of-read difference looks like in practice: 11,475 output
tokens against 251,148 of input, no reasoning spend, 102 seconds. Kimi burned 36,085
tokens of reasoning on a smaller package and never reached a report.

The best thing in it is Part 6b: three named places where a comment led its reasoning
before the code confirmed it, in descending order, unprompted beyond the instruction
asking.

## The independence ledger, rebuilt from the full provider export

723 rows, every model, every route. **All 723 are `variant=standard`.** No free
endpoint, ever. The no-training conclusion holds unchanged.

### Z.ai is not clean, and this is the second family the ledger had wrong

`z-ai/glm-5.3` ran on **28 August at 22:53** through the Chatroom: 104,394 in, 55,179
out, 48,167 reasoning, finish=stop. A full substantive session on this project, eleven
days before GLM 5.3 Flash audited it. Under the lab-not-checkpoint rule, **GLM 5.3
Flash was not an independent reviewer.** Its findings stand on their own evidence; the
comparison it feeds is one exposed reviewer against one clean one, and that caveat
travels with it permanently.

### Kimi clears, on the check that mattered most

Every Aider call in the history carries the key `Nexus-Key` and the app `Aider` — 681
of them, across Claude Sonnet 4 (194), DeepSeek v3 (315), DeepSeek R1 (96), Mistral
Nemo (71) and Claude 3 Haiku (4). Exactly the five the corrected record names.

**All 14 Kimi K3 calls are `OpenRouter: Chatroom`.** Kimi never worked on the
codebase. Session exposure only, which the 2 September ruling clears.

But its exposure is far larger than the record said: eight substantive reads on 27
August of 93K-110K input each, producing roughly 100,000 tokens of output about this
engine, plus 36,085 on 2 September. "A Step 3 attempt that truncated" describes one
row of thirteen.

### Outputs that were produced and never saved

- Four of the 27 August Kimi calls finished `stop`: 16,361, 15,971, 18,386 and 9,819
  tokens. None is in the repository.
- Qwen's 2 September call at 13:42 UTC returned **11,964 tokens**. No Qwen transcript
  exists in the repository under any name — the files bearing that name are Kimi's.
  What Qwen actually said is lost.
- Luna Pro's three 3 September calls returned 165,887, 162,555 and 65,221 tokens.
- One row, 2 September 08:59:19, has no model recorded at all.

## The .gitignore blind spot

Both evidence sets were first saved under `docs/audit_package/round*/`, which
`.gitignore` ignores except for `MANIFEST.md`. That rule is correct for generated
package bytes and wrong for reviewer responses, which are primary evidence and cannot
be regenerated.

Worse, **ignored files do not appear in `git status --short`**, so the standing
handover check could not have caught it. A check that looks for untracked files that
matter is blind to files the repository has been told to ignore.

**Structural fix, not an instruction to be careful:** reviewer responses now live in
`docs/audit_reports/<round>_<model>_<date>/`, which is tracked by default. No
exception list to maintain, and the safe location is the only one on offer. `round*/`
stays ignored for generated packages, which is what the rule was written for.

Filed there: `round2_kimi_k3_20260902/` (the complete transcript, six files, with a
README recording what it establishes) and `round3_glm_5.3_flash_20260905/` (the
report, three files, with its ledger row and verification status).

## Rulings, 5 September afternoon

- **The GLM report is round 3.** Not discarded, not acted on. No finding in it is
  fixed before the next round. It exists to be compared against round 4's report on
  the same unmodified code.
- **Kimi K3 runs round 4**, on that same unmodified code. Ruled on two grounds, with a
  third rejected. First, it has graded **none of the forty-four rules**: its earlier
  attempt could not read the standard, refused to grade, and returned Section 7 check
  results instead — so on the question this round actually asks, it is blind. "Self-review"
  overstates what it is. Second, it is the last high-ranked model clean on both
  independence lists, so a round that does not spend it spends a worse reviewer or none.

  **Rejected as a ground: that Kimi is an important model to use.** That is the exact shape
  the 2 September independence ruling warned against — a rule reading "an exception was
  made because the model was valuable" is one anyone can invoke later to justify anything,
  where a rule about mechanism can be attacked and overturned on its merits. Scarcity of
  clean reviewers is a fact about the ledger. Model quality is a preference, and it is
  doing no work in this decision.

  **Disclosed and accepted:** eleven of Kimi's own observations are already fixed in this
  code, with comments describing them. The exposure is not that it repeats a verdict — it
  has none — but that it may accept a fix to its own diagnosis more readily than a stranger
  would. Small, real, and not removable without spending a different reviewer. Accepted
  rather than argued away, and recorded here so a later reader can weigh it against
  whatever the report turns out to say.
- **Part 8 is dropped from the Kimi run entirely.** Its comparison set is Kimi's own
  reasoning. Parts 1-6, Part 7 optional. Viktor does the GLM-versus-Kimi comparison
  himself from the two reports, which keeps both fully independent and puts the
  comparison in the hands of the only party who can make it honestly.
- **Rev 5 changes exactly two things** — Section 5's false statement about the
  reviewer's identity and clean-list status, and the removal of Part 8 — and nothing
  that changes what is graded, how, or what is handed over. GLM ran against rev 4; the
  revision history will name the delta so the comparison carries its own caveat.

## What comes next

Rev 5 landed as `c82f5b3`; the builder was pointed at round 4 in `417cadf` and the package
rebuilt from it. `round4/UPLOAD_THESE/` holds seven files with rev 5 in place of rev 4,
`PART7_LATER/` holds one, `round3/` is untouched, and the round-3 and round-4 manifests
differ in three lines — Built, HEAD, Round — so all 71 file hashes are unchanged.

### Round 4 — sent, and what came back

Sent 5 September 2026 at 16:24 UTC through the OpenRouter API by
`docs/build/send_audit_round.py`, not through a chat interface: model
`moonshotai/kimi-k3`, provider pinned to Moonshot AI (`only`, fallbacks off,
`data_collection: deny`), max output 200,000 tokens. The payload was the seven files of
`round4/UPLOAD_THESE` as built at `417cadf`, in the order Section 4 lists them —
1,085,418 bytes, sha256 `dd3d21d19b0a4115878c7b9156c80a2706c62882a549f72e497102fe2d1e4a8e`.
Provider pinning is what makes round 3's accident impossible rather than unlikely: the
same model on DeepInfra caps completions at 16,384 tokens, the exact ceiling that killed
27 August, and on Chutes at 65,535.

| | |
|---|---|
| finish_reason | `stop` |
| provider reported | Moonshot AI |
| tokens in / out | 251,485 / 41,861 — 33,931 reasoning, 7,930 report |
| cost | $1.38 |
| elapsed | 1,047 s |
| filed at | `docs/audit_reports/round4_kimi-k3_2026-09-05/` |

Structure, checked and deliberately not graded: all 44 rules carry a verdict — 38
Compliant, one of them marked vacuous because no backtester exists; 6 Partially
compliant; no Non-compliant; no Not verifiable. Seven findings, three Major and four
Minor. Part 7 was not begun and `PART7_LATER/` was never sent. The reviewer stated its
identity unprompted, as Section 5 of rev 5 asks: Kimi, made by Moonshot AI — adding that
it cannot name its own checkpoint from the inside, so it cannot say whether it is the
same Kimi K3 that made the 2 September attempt, and that a reader should weigh the report
accordingly.

**The 36,085 question is still open, and Claude twice said otherwise while the run was
streaming.** Watching the progress lines, Claude converted characters to tokens at 3.3
chars/token — a ratio taken from the lossy repository copy of the 2 September transcript
— and announced that the run had passed the point where that attempt died, so the ceiling
had been the cause. The billing row gives the real ratio as 4.31. This run's reasoning
ended at **33,931 tokens, below 36,085**, and stopped of its own accord before the report
began; only the total completion exceeded it, at 41,861. What the run establishes is
therefore narrower than what was claimed: the same model, on the same material, spends
about 34,000 tokens reasoning and can then write a complete report. Whether 36,085 was a
ceiling is if anything less likely than before — ceilings are round numbers and that one
is not — but that is inference, not evidence. The entry stays open.

**Wrong turns, recorded.** The first `--send` returned HTTP 401 `Missing Authentication
header`: the placeholder `sk-or-...` from Claude's own command block had been set as the
key, literally. Nothing was charged, and `http_error.txt` is kept in the run directory
rather than deleted. Separately, the live API key was visible in a screenshot pasted into
the session; it was deleted and replaced after the run. If a later reader is reconciling
the ledger, the rows to look at are those between the exposure and the deletion.

**The `.gitignore` blind spot, second instance.** `*.json` and `*.csv` are ignored
repository-wide, so `run_metadata.json` and `generation.json` would have been written into
a tracked directory and never seen — the same shape as the reviewer responses that sat
unnoticed under `round*/`, and invisible to `git status --short` for the same reason.
Exceptions were added for `docs/audit_reports/**`. Adding them also revealed that
`provider_activity_export/openrouter_activity_20260905.csv` — filed the same day as the
ledger's source of truth — had never actually been committed.

**The rename hold is discharged.** The four `qwen_reasoning_*.txt` in the repository root
may now be renamed: the package has been sent, and Section 5 did its work with nothing in
front of it. The comment in `build_audit_package.py` where `PRIOR_OBSERVATIONS` used to be
should go with the rename.

### The round-3 versus round-4 comparison, 5 September

The comparison was reserved for Viktor by design, on the reasoning that he is the only party
who can make it honestly. On the evening of 5 September he handed it over — *"I am not
reading those reports. You read them and suggest updates/upgrades. If there is something i
need to decide on. You tell me."* — so what follows was written by Claude, the party that
wrote the code both reviewers graded. Sections below that state what the reports say, and
what the source says, can be checked.

The fuller write-up, including Claude's comparative judgement of the two reviewers' quality,
is in this repository at `Claude outputs/round3_vs_round4_comparison.md` and its PDF.
**It got there by accident and was then ratified, and the distinction matters.** The
intention had been to keep it out — it is Claude ranking the reviewers who graded Claude,
and it was unruled — but `git add -A` swept the folder into commit `bd79800`, which was
pushed to a public repository before anyone noticed. Viktor's ruling on being told: keep it.
The reasoning he accepted is that the code is already public so describing a defect in it
adds nothing; the engine holds no credentials and cannot trade; the document discloses its
own conflict in its first paragraph; and removing it from the tip would not remove it from
history at `bd79800` in any case.

Claude's earlier reasoning for keeping it out — *"the same reasoning as
`Feedback_Phase7_Engine.pdf`"* — was too broad, and is withdrawn. That document is candid
criticism of Viktor himself and stays outside version control. This one assesses two model
reports. The two are not the same kind of document and should not have been given the same
rule.

| | Round 3 — GLM 5.3 Flash | Round 4 — Kimi K3 |
|---|---|---|
| Compliant | 26 | 38 |
| Partially compliant | 13 | 6 |
| Not verifiable | 1 (Item 17) | 0 |
| Non-compliant | 0 | 0 |
| Findings | 11, all Minor | 7 — three Major, four Minor |
| Release gate, on own findings | met | met |
| Output tokens | 11,475, no reasoning spend | 41,861 (33,931 reasoning) |

The tallies and the findings point in opposite directions. GLM marks more rules imperfect and
rates every defect Minor; Kimi marks fewer imperfect and raises three Majors. They are not
the same audit at two strictness settings — they looked at different things.

**The one place they read the same three lines.** `models/signal_router.py`,
`_merge_btc_context`, lines 478-481. GLM filed it as F-4, Minor: the merge invents defaults
for fields that may be absent, but "engine_core currently always populates these keys when
available is True, so the defaults never fire." Kimi filed the same lines as Finding 1,
Major, because the failure mode is not a missing key: `core/engine_core.py` line 771 builds
the block with `"available": True` and line 784 writes `"correlation": None` when the
correlation is not finite. The key is present with the value `None`, so `.get(key, 0.0)`
returns `None`, `float(None)` raises `TypeError`, `_build_decision_object`'s broad `try`
converts a complete analysis into an error dict, and that is what reaches the decision log
and the panel.

Verified at source on 5 September, all four sites read: the producer's `"available": True`
with a `None` correlation (`engine_core.py` 771-788), the consumer's `float(...get(...))`
(`signal_router.py` 478-481), and `decision_model._compute_btc_adjusted` handling the same
state correctly via `correlation_raw is not None` (line 693). The asymmetry is real — the
5 September fix taught `decision_model` and `panel_render` about `None` and did not teach
`signal_router`. Not verified: the end-to-end run, which is what Kimi's Section 11 requests.

**Found by Kimi only.** Finding 2, Major — `_compute_btc_adjusted` derives `agreement` from
the signs of the two bias scores and multiplies by `abs(correlation)`, discarding the
correlation's sign, so on a negative correlation "BTC bearish" scores as confirming "AERO
bearish"; verified at source (lines 700-717) and exhibited in the project's own shipped
transcript at −0.90 with confidence raised 52.64 → 64.58 and the sentence "agreeing".
Finding 3, Major — Item 5: `engine_version` is a static string unchanged across every commit,
and `FINGERPRINTED_MODULES` omits decision-affecting constants (`DEGRADED_CONFIDENCE_CEILING`,
`BTC_ADJUSTMENT_CAP`, the entry multipliers, the trend bands, `SPIKE_RATIO`, `window=30`,
`0.0015`), so two runs on different code record identical hashes. Finding 4, Minor —
`classify_risk_regime` takes `trend_health` as an input, and `decision_contract.py` carries a
comment claiming that gate is independent of trend health. Finding 5 item 6, Minor and
reachable — `_detect_swing_structure` returns the current price as a structural level on
frames shorter than 21 rows, and the engine's minimum is 20. Finding 6, Minor — the panel
prints "Connecting to MEXC API…" on offline pinned runs, and the banner says Phase-7.3 while
`engine_version` says v1.0.

**Found by GLM only.** F-3 — `calculate_structure` writes STRUCTURE/HVN/LVN both onto its
returned frame and into its dict, and `engine_core` reads both routes. F-6 — BTC-side
`compute_trend_health` degradations are not propagated into the AERO run's degradation list.
F-7 — the permissive `risk_valid` default, which Claude found on 5 September to be
under-scoped: the same default sits on the trade-authorization path in
`decision_model._determine_final_action`, which GLM's severity argument does not cover.
F-8 and F-9 — two tests whose stated method and actual method diverge. F-11 — `exit_model`'s
`or 0.0` on hvn/lvn is dead code that is safe only because `NaN > 0` is False.

**Two more, added 6 September, and the omission is the point.** The paragraph above named
six GLM-only findings. GLM filed eleven (F-1 to F-11; F-12 is a summary, not a finding),
with two real overlaps — F-4 against Kimi Finding 1, and F-2's `pct_slope` against Kimi
Finding 7 — so nine should be listed here and six were. F-5 turns up under "Agreed by
both" below. **F-1 and F-10 appeared nowhere in this comparison at all**, which means the
sweep assembled from the sections this file names would have silently dropped them:

- **F-1** — two `.bfill()` calls survive in `indicators/indicators.py::pct_slope`. GLM
  verified it is not a live leak: the analysis happens at the last bar of a 450-row frame
  and the contaminated rows sit ~400 bars behind every window the decision reads. It is an
  Item 2 residual on a path a backtest harness walking the decision timestamp backwards
  would reach with no code change. It dies with `pct_slope` if F-2 is fixed by deletion.
- **F-10** — `module_snapshot()` swallows import failures and records
  `{"<import failed>": str(exc)}` **inside the run-hash payload**, and nothing documents
  that. Two runs on identical data, one where `models.decision_model` fails to import,
  produce different `run_hash` values with no field-level signal distinguishing an
  environment failure from a deliberate setting change. Item 5: recoverable, yes;
  distinguishable, no. Not fixed by the `code_hash` work, which answers a different
  question.

This is the same defect class the comparison itself describes one paragraph down — a
reviewer reasoning from a list another source proves incomplete — occurring in the
comparison. Rule 11: a list of names decays, including this one.

**Agreed by both.** `pct_slope` is unconsumed dead code; the confidence and entry-quality
labels overlap more than the panel admits; the suite tests behaviour rather than merely
pinning it, reversing the earlier auditor's judgement; and neither found a Critical.

**The structural observation, and it is a fact about the two reports rather than an opinion
about the two models.** Nine of GLM's eleven findings do not appear in Kimi's report and five
of Kimi's seven do not appear in GLM's. The union is roughly sixteen distinct items with two
real overlaps — nearly twice either report. Both reviewers concluded the release gate is met
*on their own findings*, and each was reasoning from a list the other proves incomplete. The
gate language ("no Critical Tier 1 finding stands unresolved") is in practice evaluated
against whatever one reviewer happened to reach.

**Suggested fix order** (engineering, Claude's unless overruled): ~~Kimi Finding 1 first,
and the real fix is the missing test at the router seam rather than the merge line~~ —
**DONE 6 September, see "Finding 1 fixed" below**; then ~~GLM F-7 as extended, because wrong
polarity on an authorization gate outranks what follows~~ — **DONE 6 September at `26a05dc`,
see "GLM F-7 as extended" below**; then Kimi Finding 2 (blocked on decision 3); ~~then Kimi
Finding 5 item 6~~ — **DONE 6 September at `4678f45`, see "Kimi Finding 5 item 6" below**;
~~then Kimi Finding 3~~ — **DONE 6 September at `1045748`, see "Kimi Finding 3" below**;
**then the latent and Minor items as one sweep, which is now the next piece of work** and
needs no decision first; then GLM F-8/F-9 for test hygiene. **Kimi Finding 2 is the only
item in this order blocked on a ruling, and it is the only round-4 Major left.** The
10:51 live run added a second, independent mechanism to it — see decision 3.

### Open — decisions

These are Viktor's, and none was made on 5 September.

1. **Does the release gate open?** Both reviewers say met on their own findings. The standing
   ruling is that unresolved means fixed *and* re-audited, and three Majors stand unfixed.
2. **Item 14.** Kimi says feeding `trend_health` into `classify_risk_regime` makes conviction
   an input to risk and breaks Item 14; GLM graded Item 14 Compliant. This is a reading of
   the Constitution, not a code question. Either way, `decision_contract.py`'s comment
   claiming independence from trend health is false about the code beside it.

   **RULED AND CLOSED 11 September 2026, at `0c7dec5`.** Viktor ruled that the risk regime
   determines itself, which dissolves the reading rather than settling it: with
   `trend_health` no longer an input, the question of whether that coupling breaks Item 14
   stops being live. Asked whether to drop the "weak trend is itself a risk factor"
   heuristic or replace it, he ruled replace — so `classify_risk_regime` reads ADX, which
   `trend_health` is computed FROM rather than derived from. Note this turned out NOT to be
   "a reading of the Constitution, not a code question": the ruling made it a code change,
   and the sentence above was wrong about that. The `decision_contract.py` comment was
   already corrected by sweep item 10; the code underneath it is now true as well.

   Honest limit, carried over from the commit message: ADX still reaches `bias_score`
   indirectly through `continuation_strength`'s `adx_component`. What it is no longer is
   the same value read twice. Whether ADX is the *correct* risk proxy is empirical and
   cannot be settled before backtesting, which sits behind the release gate.
3. **Kimi Finding 2 — fix or accept as a recorded limitation?** Display-only, labelled
   unvalidated, cannot reach a gate. Claude recommends fixing: it is a wrong number an
   operator reads, and "contained" is the argument that has failed twice here.
   **Strengthened on 6 September by the 10:51 live run, and the new part is a second
   mechanism rather than a second example.** Kimi's finding is that `abs(correlation)`
   discards the correlation's sign, and its exhibit is a −0.90 pairing. At 10:51 the
   correlation was **+0.51** — the sign was never in question — and the panel still printed
   *"BTC is also neutral, agreeing with AERO's own bias"* over a BULLISH CONFIRMED AERO,
   while raising confidence 73.86 → 75.80. Cause, verified at `decision_model.py` 704-768:
   `agreement` is decided by the SIGN of `btc_score` and the words come from
   `btc_detailed`, the LABEL. Those disagree for any score that is non-zero but below the
   labelling threshold. So the function produces false sentences by two independent routes,
   one of which is reachable on exactly the positive correlations the suite already covers —
   and Kimi's own note that the tests cannot see the inverted case is true of this one too,
   for a different reason: nothing asserts the sentence against the label. Full write-up
   under "Kimi Finding 3" below, including what was inferred rather than checked.

   **The inference is now VERIFIED, and the band is wider than the write-up assumed.**
   `calculate_dynamic_bias` and `calculate_dynamic_regime` were read on 6 September, which
   is what closed this. BTC's label does come from `RAW_BIAS_THRESHOLD = 20.0`:
   `engine_core.py` line 748 computes BTC's bias through `calculate_dynamic_bias`, and
   `bias_engine.py` 355-360 requires `bias_score > 20.0` strictly to call a side.
   `engine_core.py` 765 then passes that through `BiasStateMachine.transition`, which
   requires `abs(score) < 20` for NEUTRAL — so both gates agree at the ~19 the panel
   arithmetic implied. `decision_model.py` 708 reads `btc_context["score"]`, the same
   blend score, and takes its SIGN.

   So the false-sentence band is **0 < |btc_score| ≤ 20**, not a narrow neighbourhood of
   19. Every score in it has a non-zero sign and a NEUTRAL label. The 10:51 run did not
   land in an unlucky corner; it landed in a twenty-point-wide dead zone that the suite's
   own positive correlations reach routinely. That strengthens the case for fixing rather
   than accepting, and it is the last input this decision was waiting on.

   **CLOSED 9 September 2026 — Viktor ruled fix.** Landed at `5e2e9f3` (docs `179f4f9`).
   `agreement` now reads BTC's own label band (`RAW_BIAS_THRESHOLD`) rather than the raw
   score's sign alone, and the sentence is built from the signed correlation instead of
   `abs(correlation)`. Golden re-baselined on `btc_context` only — adjusted confidence
   78.14 → 79.26 on pinned TESTUSDT, no other field moved. Suite 345/0/29, unmoved. This
   was Grok's patch, in the same session as the sweep; Grok is not independent for any
   re-audit of it.
4. **Does the divergence change the independence policy?** If a two-reviewer union is twice
   either report, one clean reviewer per round is under-powered — which makes the ledger's
   scarcity problem worse rather than better. Viktor has said he wants to write his own
   position on this one before hearing Claude's.
5. **Part 7.** `commit_messages_PART7_ONLY.md` was never sent; both reviewers confirmed they
   finalised without it. Over the API it means resending the package plus the report to a
   fresh instance, about $1.40, and it is not the same thing as a conversation continuing.

   **CLOSED 11 September 2026 — see "Rulings, 11 September 2026" item 3.** Not resent to
   rounds 3 or 4; folded into round 5's package from the start instead. **BUILT 12 September
   2026**: `docs/build/build_audit_package.py` now includes `commit_messages_PART7_ONLY.md`
   in the single upload set, and `docs/build/send_audit_round.py`'s `ATTACHMENT_FILES`
   carries it — the first round for which that file is actually reachable by an API call,
   rather than described as available and never attached.
6. **Disclosure.** The round-3 run was not disclosed to Kimi, deliberately and on the record.
   If any of this comparison reaches the portfolio document, the non-disclosure and its
   reason travel with it.
7. **What the live decision log is for, now that most of it is test output.**
   **RESTATED 6 September 2026 — the previous wording is preserved below because it is a
   decision that could not have been ruled on as written.**

   It used to read: "the three synthetic records in the live decision log — records 10, 11
   and 12 of `logs/phase7_decision_log_aerousdt.jsonl`, written by the first version of the
   Section 11 harness before it was repointed at a temporary directory. Prune or keep?"

   Those three records no longer exist, and neither does the file they were in. Acting on
   that wording against the log as it now stands would have deleted **record 11, the 10:51
   live run**, and found no record 12. A decision that names rows by position in an append
   log is a decision with an expiry date nobody wrote down.

   What the file actually holds: eleven records, all stamped 08:51 UTC on 6 September
   inside a single minute. Records 1-10 are a **test suite run** — identical
   `run_hash 3a68572a83`, identical bias score 78.6973, one error record carrying no
   `code_hash`. Record 11 is the 10:51 AEROUSDT run at 73.859. Reproduced exactly in a
   sandbox: one full suite run writes those same ten records. So **one of eleven records
   in the engine's permanent record is a decision anybody made.**

   The suite no longer writes there (see "The suite was destroying the decision record"),
   so the file is stable from here. The question that remains is Viktor's and it is
   larger than pruning:

   - Do the ten suite records get pruned, leaving one real run, or does the log keep them
     as the evidence of what was happening to it? The standing practice of recording wrong
     turns rather than tidying them argues for keeping — but that practice was written for
     wrong turns somebody took, not for output a green test suite deposited.
   - Does a log that has been rebuilt from test output serve as the Item 5 / Item 6 record
     the release gate leans on, or does that record start again from the next live run?
   - `logs/` is gitignored, so the record still has no second copy anywhere. Whether that
     changes is part of the same ruling.

   Nothing here is urgent in the sense of blocking work, and nothing should be deleted
   before it is ruled on. It is his record either way.
8. **Two holes in the delivery and handover mechanism, found on 6 September.** Both are
   process rather than code, both have a structural fix available, and neither is ruled.
   See "What the handover found, and could not have found" below for the evidence.
   - *The handover check has no question that would catch a staged-but-uncommitted commit.*
     Its six questions ask about untracked files and loose patch files. The 6 September doc
     rewrite was neither: a fully staged index with its message file beside it, prepared and
     never committed, which survived a handover check and a whole session. A seventh
     question — does `git status --short` show anything in the INDEX column — would have
     caught it.
   - *The delivery filenames are generic and keep coming back.* `COMMIT_MSG.txt` was swept
     into `77d822f` by `git add -A`, deleted again in `76150d0`, and re-armed a third time
     on 6 September. A `.gitignore` entry would close it; Viktor ruled on 5 September that
     `round3/README.md` gets no `.gitignore` exception, and there is a recorded `.gitignore`
     blind spot above, so this is a ruling and not a tidy-up. The interim mitigation is
     already in the working practice below: a delivered file gets a name unique to its
     version, which is the only reason the 6 September delivery files could be reset by name.

     **First bullet CLOSED, 12 September 2026.** Accepted in principle at ruling 5 (11
     September); the seventh question is now in the “Working practice” handover check below,
     docs-only and code_hash-neutral by directory exclusion.

     **Second bullet — still open, still a ruling and not a tidy-up.** Not decided this
     session either, on the same ground Viktor already ruled once: ask him directly rather
     than default it. The interim mitigation (versioned delivery filenames) remains in force
     and was followed for everything delivered 12 September.
   - *A third instance, found the same day and not a new decision — evidence for these two.*
     The Finding 5 item 6 delivery was issued as a numbered command list, then reissued with
     the same steps renumbered when the live run was inserted. One `git add` was lost between
     the two numberings and the commit went in without its test file, caught only by reading
     `2 files changed` in the commit output. Amended before pushing. The candidate structural
     fix is one numbered list per delivery, issued once and never renumbered; it is recorded
     here rather than adopted, because it is the same kind of process ruling as the two above.

### Open — work

1. ~~Section 11: the confirmation run for Finding 1.~~ **DONE, 6 September 2026 — Finding 1
   confirmed end to end, on unmodified code, before any fix.** See "The Section 11
   confirmation run" below, which also records what the run found beyond the finding and two
   wrong turns made getting there.
2. ~~The fixes, in the order above.~~ **Kimi Finding 1, GLM F-7 as extended, Kimi Finding 5
   item 6 and Kimi Finding 3 are all fixed and pushed (6 September, `76150d0`, `26a05dc`,
   `4678f45` and `1045748`). The sweep of latent and Minor items is the next one, and it
   needs no decision from Viktor first.** The rest of the order stands; Kimi Finding 2 is
   blocked on decision 3 above and is the last round-4 Major.

   **The sweep is now assembled — fourteen items, in "The sweep of latent and Minor items"
   near the end of this file.** It was spread across six sources and no section held it,
   and two of its items (GLM F-1 and F-10) were missing from the comparison that was
   supposed to list them. **One thing jumped ahead of it on 6 September**: the test suite
   was destroying the decision record, which outranks fourteen latent items and is fixed.

   **CLOSED 7–8 September 2026 (Grok session).** All fourteen items landed, split by class
   exactly as suggested: items 1–5 (invented defaults) at `22afea2`, items 6–8 (dead code)
   at `4d56f2a`, items 9–14 (false statements plus the F-3 structural fix) at `c3b0d43` —
   docs commits `029c510`, `e528475`, `c56f969`. Suite 345/0/29 after each code commit;
   golden 8/8, unmoved, because the sweep only touched absent-key and failure paths. A
   separate fix, `ef00765`, excludes `Claude outputs/` from the `code_hash` walk after
   Grok's own backup files were found polluting it. Recorded at Engineering Notes #91–#93
   (v1.24). Grok wrote all of this code and is therefore not independent for any future
   re-audit of it — see the per-item checklist below, now updated to match.
3. The Engineering Notes are current through Entry #82 and do not cover the round-4 run,
   the round-3 versus round-4 comparison, the Section 11 confirmation run, the Finding 1
   fix, the F-7 fix, the Finding 5 item 6 fix, or the Finding 3 fix. **Seven entries owed**
   — it was five before item 6 landed and six before Finding 3, and the gap grows by one
   with every fix that ships. This is the item that has grown at every handover for three
   sessions; it is a candidate for the structural treatment rule 28 describes rather than
   for being carried forward an eighth time.

   **The structural cause was found on 6 September, and it is not discipline.** Nine of
   the ten PDF builders under `docs/build/` hardcoded their output to `/tmp/outputs/` — an
   absolute Linux path that does not exist on Viktor's machine and is nowhere in this
   repository. **No build script could write into the repository.** Every PDF in `docs/`
   was produced in a sandbox and carried across by hand. So "regenerate the Notes" was not
   one command; it was run in a sandbox, find the file in `/tmp`, move it over the device
   bridge, commit — which is exactly the shape of task that does not get done at the end of
   a session. **Eight entries owed** counting 6 September's document audit.

   **The builder half is FIXED — see "The build scripts can write into the repository" at
   the end of this file.** `docs/build/_output.py` resolves the path from `__file__` and
   the nine import it. The tenth, `build_audit_package.py`, never had the defect: it
   already resolved repo-relative, which is why its manifests verify byte-for-byte. **The
   eight entries are still owed.** They are content inside `build_engineering_notes.py`;
   the fix makes publishing them one command, not writing them.

   Two of the nine are worse and cannot be fixed by repointing alone:
   `build_findings_bundle.py` and `build_remediation_plan.py` also READ source material
   that is not in this repository. Neither document can be regenerated by anyone, from
   here, at all. They now say exactly that and exit 2 before doing any work, instead of
   failing with a bare `FileNotFoundError` naming a directory in `/tmp`. That is an honest
   failure, not a fixed script.

   **CLOSED 6 September 2026 — the eight entries are published.** Entries #83-90 landed at
   commit `cdf9025`, covering the round-4 run, the round-3/round-4 comparison, the Section
   11 confirmation run, and the Finding 1, F-7, Finding 5 item 6, Finding 3 and
   decision-record-destruction fixes, plus the build-scripts fix itself — all eight, so the
   count does not carry a ninth item forward. `code_hash` confirmed unchanged on three
   separate trees (pristine, hand-verified, independently cloned-and-patched); suite
   unmoved in all three configurations. Not verified: this exact content rendering through
   reportlab on Windows specifically — every prior entry in this builder has rendered there,
   and nothing new uses an unproven construct, but that is a structural argument, not a
   Windows observation. See "6 September 2026 — Engineering Notes entries #83-90 published"
   near the end of this file.

   **REOPENED the same session, end-of-session handover check, 6 September 2026.** The
   Notes stop at Entry #90 and do not cover what landed after: the semantic half of the
   document audit, or its three findings' fixes (the Documentation Standard correction, the
   Audit Execution Instructions correction notice, the `run_tests.py` crash fix — commits
   `0f8e04a`, `fc4b8fc`, `8051f5f`, `6f219ef`). **Four entries owed.** Flagged here rather
   than left to be found next session, per the standing handover check — this is the same
   growing-gap pattern rule 28 and the structural fix above were about; it is back after one
   session's use because publishing the Notes is still a deliberate step, not an automatic
   one, even now that it is a single command.
4. The four `qwen_reasoning_*.txt` may now be renamed; the hold is discharged.
5. Observed in the live run of 6 September and NOT investigated: the panel printed
   `BTC BIAS : BULLISH` directly above `BTC REGIME : BEARISH TREND`. Those come from two
   different functions on the same BTC frame (`calculate_dynamic_bias` and
   `calculate_dynamic_regime`), so it may be a legitimate state — a bullish bias inside a
   bearish structural regime — and the downstream reason string reads only the bias half.
   Neither function has been read. Recorded as an observation, not as a finding.
   **It did not reproduce in the 10:04 run of the same day**, which read `BTC BIAS :
   BULLISH CONFIRMED` over `BTC REGIME : NEUTRAL STRUCTURE`. That is consistent with a
   legitimate state and is not evidence of one — two runs is not a sample, and the two
   functions are still unread.
   **Third observation, 10:51 the same day: `BTC BIAS : NEUTRAL` over `BTC REGIME :
   BEARISH TREND`.** Two of three runs show the two fields disagreeing. Still not a
   finding and still not investigated — but the 10:51 run gives a partial and UNVERIFIED
   explanation for the bias half: the BTC bias score at 10:51 was just under 19 (inferred
   from the panel arithmetic, not observed), which is below the threshold that would have
   labelled it BULLISH, so a positive score printed as NEUTRAL. Whether BTC's label comes
   from `RAW_BIAS_THRESHOLD = 20.0` has NOT been checked — `calculate_dynamic_bias` is
   still unread. If it does, the divergence is a labelling band and not a disagreement,
   and this item closes cheaply. Reading those two functions is now the obvious next move
   on it, and it is the same reading that decision 3 needs.

   **CLOSED 6 September 2026 — not a finding, and verified rather than inferred.** Both
   functions were read. They do not measure the same thing and were never expected to
   agree. `calculate_dynamic_regime` (`bias_engine.py` 369-416) returns
   `df["STRUCTURE"].iloc[-1]` verbatim — the raw structural label, nothing else.
   `calculate_dynamic_bias` is a six-factor weighted blend in which that same label enters
   as `structure_regime` at weight **0.20** (`bias_engine.py` 51, 216-218), alongside
   trend health 0.30, volume sentiment 0.15, SuperTrend 0.15, macro 0.10 and
   reversal/continuation 0.10. The result is thresholded at ±20 and then passed through
   `BiasStateMachine`, which needs ±30 to say CONFIRMED. The panel's BTC BIAS line is that
   state machine's output (`engine_core.py` 765), not the raw label at all.

   A `BEARISH TREND` structure carrying a fifth of the weight can be outvoted by the other
   four fifths. `BTC BIAS : NEUTRAL` over `BTC REGIME : BEARISH TREND` is a legitimate
   state, and two of three runs showing the two fields disagreeing is the expected shape
   rather than a symptom. Three runs was never a sample; it did not need to be.

   What it leaves, and it is presentation rather than correctness: the panel prints the two
   adjacently with nothing saying they are different quantities measured at different
   scales. Same class as GLM F-5 — a label that overlaps another more than the panel
   admits. Recorded there, not reopened here.
6. This file's own head block was stale for most of 5 September and was rewritten on the
   6th. Worth re-reading it against reality at the end of each session rather than only at
   the end of each phase.

   **It happened again, in a new shape, and was fixed on 11 September.** The 7-9 September
   Grok session updated the head block and the Engineering Notes but not this file's body,
   so "Open — decisions" #3 and "Open — work" #2 still described the sweep and Kimi
   Finding 2 as open work after both had landed. Reconciled at `4705d03`. The lesson is
   narrower than "re-read the head block": a session that closes an item has to close it
   in the tracking sections too, because those are what the next session acts on.
7. **Engineering Notes stop at Entry #93 (v1.24, 9 September).** Not covered: the qwen
   rename (`bb6d222`), this file's body reconciliation (`4705d03`), the sweep-commands PDF
   (`e75f7be`), and Item 14 (`0c7dec5`). Up to four entries owed, two or three if grouped
   sensibly. Publishing them is one command since the builder fix, but it is still a
   deliberate step rather than an automatic one, which is why this keeps reopening.

   **CLOSED 12 September 2026 — entries #94-#97 written into `build_engineering_notes.py`
   (v1.25).** Docs-only, code_hash-neutral by directory exclusion. The PDF itself is not
   regenerated by this patch; run `python docs/build/build_engineering_notes.py` (one
   command, per the 6 September builder fix) after applying to publish it.
8. **The decision-log backup practice is ruled but not built** — see "Rulings, 11 September
   2026" item 2. First concrete step is committing
   `Claude outputs/phase7_decision_log_aerousdt_20260906_backup.jsonl`, currently the only
   second copy of the 6 September record, into a committed location outside any ignored
   directory.

   **CLOSED 12 September 2026 — `decision_log_backups/` is a new tracked directory, outside
   `logs/` and outside `Claude outputs/` (so it does not depend on ruling 5's still-open
   `.gitignore` question). The 6 September file moved there, renamed to
   `phase7_decision_log_aerousdt_20260906.jsonl`, md5-confirmed byte-identical.
   `utils/decision_log_backup.py` takes a new dated snapshot of every live
   `logs/phase7_decision_log_*.jsonl` on command (`python utils/decision_log_backup.py`),
   refusing to overwrite a differing same-day snapshot without `--force`. Eight fixture-free
   tests in `tests/test_decision_log_backup.py`. Not a scheduled job — nothing reachable from
   this bridge can register one on Viktor's machine — so it is a command for him to run, not
   an automatic one; session end is the natural point. Ruling 2's other half — tagging the ten
   suite-written records already inside the live log — is NOT done here: that file is
   gitignored and machine-local, outside what a git patch can touch, and needs its own
   approach.**
9. **Should the panel print ADX?** Since `0c7dec5` the panel shows `RISK REGIME` without
   showing the quantity that decides it, where `trend_health` used to be visible on the
   TREND line. The record is unaffected. Panel-only change if taken, no decision-path
   effect, and it is Viktor's call rather than a defect to repair.
10. **The ADX branches have never been observed deciding a live run.** The 11 September
    22:50 run exited on the 15% max-stop check before reaching them. Worth watching the
    first run that produces a sub-15% stop in non-extreme volatility: ADX below 20 should
    read HIGH VOLATILITY RISK even when volatility looks calm, and LOW RISK should appear
    only with low volatility and ADX at 25 or above.
11. **Round 5 is built, not sent.** `docs/build/send_audit_round.py` and
    `docs/build/build_audit_package.py` point at GPT-6 Astra / `round5`, and
    `item16_review_instruction_rev6.md` is written and dry-run-verified end to end (see the
    head block above). What is left, and it is entirely Viktor's: run
    `python docs/build/build_audit_package.py` to produce `UPLOAD_THESE/` and commit the new
    `round5/MANIFEST.md`, sanity-check `python docs/build/send_audit_round.py`'s dry-run
    output on his own machine, set `OPENROUTER_API_KEY`, and re-run with `--send` when he is
    ready to spend the roughly $6.50-$9 this round now costs.

## 6 September 2026 — the Section 11 confirmation run

Kimi's round-4 report asked for exactly one run, and this is it. It was made **before any
fix**, on unmodified code, so that Finding 1 is observed rather than argued. The harness and
its outputs are at
`docs/audit_reports/round4_kimi-k3_2026-09-05/section11_confirmation/`.

Three runs, all offline (`requests.get`/`.post`/`Session.request` replaced with functions
that raise), all served from the committed pinned fixtures:

| | variant | result |
|---|---|---|
| A | fixtures exactly as committed — negative control | completed, `correlation +0.2326`, `n_observations 30` |
| B | `BTCUSDT_4h` with every timestamp shifted +2h — zero shared timestamps | `Decision object construction failed: float() argument must be a string or a real number, not 'NoneType'` |
| C | BTC's last 60 candles flat — the optional zero-variance variant | same message (secondary; a flat series also moves BTC-side ATR and volatility, so it has more than one possible cause) |

**Finding 1 is confirmed end to end.** B produced the exact string Kimi named as the
distinguishing output, and A completing on the same harness is what makes B's failure mean
something. The chain had already been verified by reading all four sites — `engine_core`
771-788 writing `"available": True` beside `"correlation": None`, `signal_router`
478-481 doing `float(...get("correlation", 0.0))`, the broad `except` at 451, and
`compute_correlation_beta` returning `(NaN, NaN, 0)` on an empty inner join. What was
missing was the observation, and it is no longer missing.

### What the run found that the report does not contain

The decision log record written when the merge fails is
`{"error": ..., "symbol": ..., "timeframe": ..., "decision_log_path": ...}` and nothing
else. The healthy record beside it carries `lineage` and `provenance`, with `input_hashes`,
`run_hash` and the flag saying the run was pinned. The error record carries none of them.

That is wider than Finding 1 as written. The broad `except` does not only discard a healthy
analysis — it discards the run's lineage, and `decision_log.write` then stores a record that
Item 6 cannot trace to any input. Item 6 is the Critical that keeps the release gate shut,
so a defect that manufactures untraceable records inside it is not a display concern. It is
reproducible from tracked bytes: `isolated_phase7_decision_log_aerousdt.jsonl` in the
evidence directory holds all three records, one healthy and two error.

Whether this is folded into the Finding 1 fix or raised as its own item is Viktor's call.
Claude's position is fold it in: the discarded analysis and the discarded lineage are the
same broad `except` at `signal_router.py` 446-452, so two items would mean two patches
touching one block, and the second would be reviewed against a codebase the first had
already changed underneath it. The argument for splitting is that they fail different
rules — Finding 1 is availability, the lineage loss is Item 6 — and that a Critical-item
defect found by a confirmation run deserves its own entry rather than a paragraph inside
someone else's finding.

### Two wrong turns, recorded rather than cleaned up

**The first version of the harness wrote into the engine's permanent record.** It ran with
`config.LOG_DIR` untouched, so its three runs appended three records to
`logs/phase7_decision_log_aerousdt.jsonl` — records 10, 11 and 12 of 12, two of them error
records — and overwrote `logs/phase7_state_AEROUSDT_4h.json`, leaving the persisted bias
state machine holding `BULLISH CONFIRMED` derived from a fixture. A diagnostic wrote into
the record the audit is about. Claude's prediction for that run named the decision-log
writes for the completing runs only, and did not name the error-path write or the state file
at all.

The fix is structural rather than a warning: the harness now repoints `config.LOG_DIR` at a
temporary directory for the duration, so it cannot reach the real log, and copies the record
its own runs produced into the evidence directory afterwards. That copy is where the
untraceable-record evidence above comes from. Verified after the second run: the real log
is unchanged at 90,277 bytes and its modification time did not move.

The three synthetic records still sit in the live decision log. Left for Viktor to rule on;
the standing practice of recording wrong turns rather than tidying them argues for keeping
them, but it is his record.

**CORRECTION, 6 September 2026 — the paragraph above is now false about the file, and is
kept because it was true when written and the correction is the point.** The three
synthetic records are gone, and so is the twelve-record, 90,277-byte file they were in.
`test_lineage.py`'s archive-path spelling test deleted `logs/` outright on a later suite
run, and the suite then rebuilt the log out of its own test output. See "The suite was
destroying the decision record" below, and decision 7, which has been restated because it
named those records by position.

The harness fix described above was correct and remains correct. It repointed **one**
caller while the same defect sat in twenty-eight tests and one `rmtree`, and nobody asked
whether the class was larger. Rule 3, and this is where the two halves of it meet.

**The delivery mechanism shipped the wrong version silently.** The corrected harness was
staged for the device bridge under the same filename as the version it replaced, and the
commit wrote the *older* bytes. It failed with `ModuleNotFoundError: No module named 'core'`,
which is v1's path logic running from a directory v1 was never meant to run from. Nothing
reported an error. The `py_compile` check passed and was worthless as a guard, because both
versions compile — it tested syntax when the question was identity.

Two rules taken from it: a delivered file gets a staged name unique to its version, and a
delivery is verified by reading the file back off the device and diffing it against the
intended bytes, not by compiling the copy that was sent.

### A prediction that was close and not exact

The error object's keys were predicted as `['error', 'symbol', 'timeframe']`. They are
`['decision_log_path', 'error', 'symbol', 'timeframe']` — `route_and_execute` adds
`decision_log_path` after the write, to the error dict as readily as to a healthy one. The
substance held; the enumeration did not.

## 6 September 2026 — Finding 1 fixed, and the seam it was hiding in

Landed as a patch against unmodified code, after the Section 11 confirmation run above had
already reproduced the defect. Suite 319 → **331 passing, 0 failed**. Golden snapshot did
not move, which was predicted before the run and is the same claim as the negative-control
test: on the pinned fixtures the correlation is measured (+0.2326 over 30 observations), so
every value the snapshot records goes through the unchanged path.

### What changed

`models/signal_router.py`, two things:

1. A new `_optional_number()` helper, and the two call sites that read
   `float(btc_context.get(key, 0.0))` now pass through what the producer wrote. None stays
   None; a non-finite number becomes None; a measured number is unchanged. **None rather
   than 0.0 deliberately** — a correlation of 0.00 is a measurement, the one a real pair of
   independent assets produces, so substituting it would report a finding the engine does
   not have. That is the defect already removed from `btc_context.py`'s `(0.0, 0.0, 0)`,
   from `trend_health`'s 50.0 and from RSI's 50.0. `panel_render` and `decision_model`
   already read None as "not measured"; this is the third module agreeing with them instead
   of crashing on them.

2. The record written when the assembly fails now carries the run's `lineage` and
   `provenance`. That is the Item 6 defect the confirmation run found and neither reviewer
   filed.

`tests/test_router_btc_seam.py`, new: twelve tests written **at the seam** rather than as
one more assertion about either side of it. That is the actual lesson — the producer was
tested, the decision model was tested, the panel was tested, and the place where one
module's output becomes another's input was not. The pinned fixtures share all 450
timestamps, so nothing in the suite had ever made the producer emit its not-measured shape
and handed it to this consumer.

### Evidence against pre-fix code

Run against the unmodified engine: **8 failed, 2 passed, 2 skipped**, and all eight
failures are behavioural — `TypeError` raised from `signal_router.py`'s own `float()` line,
and `KeyError: 'lineage'` on the failed record. No `ImportError`, no collection error:
nothing failed merely because the module is new. The split matters, because a new module
that fails to import proves only that it is new.

The two that pass pre-fix are there on purpose.
`test_a_measured_relationship_passes_through_unchanged` is the negative control and must
pass both before and after; `test_the_lineage_survives_into_the_written_record` exercises
`decision_log`, which the patch does not touch.

### Where the verification stopped

The patch was built and verified in a Linux sandbox on the pinned dependency versions —
applies clean to a pristine checkout, both changed files md5-match what was built, suite
from the applied tree 222 passed / 98 skipped / 0 failed against a 212 / 96 / 0 pre-patch
baseline on the same tree. But `pandas_ta` cannot be installed there, so that was the
`pandas_ta`-free run only: the two end-to-end tests in the new file and the golden snapshot
were unverified until the Windows run. Stated at delivery rather than after the fact.

### Not fixed, and why

- The other fields in the same merge still carry invented defaults — `"NEUTRAL"`,
  `"NORMAL"`, `0.0` for `trend_health`. Not covered, because they are not optional
  measurements. That is the same "the producer always sets it" argument that was made about
  the correlation line and was wrong, so it is recorded in the helper's docstring as an
  open question rather than as a guarantee.
- **A failure inside the merge still cannot degrade rather than halt.** The 29 August
  ruling says a failed input caps confidence instead of stopping the run, but
  `decision_model.evaluate()` is called *before* the merge is assembled, so a degradation
  discovered at merge time cannot reach the model that reads the degradation list. Making
  it reachable means computing the BTC block before `evaluate()`. That is a restructure,
  it is a real gap in a standing ruling, and it is written down here rather than left in a
  patch comment.

## 6 September 2026 — GLM F-7 as extended, and it was reachable

Landed at `26a05dc`, pushed. Suite 331 → **363 passing, 0 failed**. Golden snapshot did not
move, predicted before the run and confirmed by `git diff` on
`tests/fixtures/golden_decision.json` rather than only by the test passing.

### The finding got worse on being read

The 5 September note called this a permissive default sitting in three places, and rated the
extension over GLM's Minor on the strength of one of them being the authorization gate. That
was right and it was incomplete. **The defect was reachable, not latent.**

`signal_router._validate_engine_output` checked that the key `"risk"` was PRESENT as a
section and never once looked at what was under it. So an engine output whose risk block was
`{}` passed validation, satisfied `_determine_final_action`'s `isinstance(risk, dict)` guard,
and reached a gate whose `.get("risk_valid", True)` supplied the authorization the engine had
never computed. `_refuse_incoherent_plan` does not catch that case either — an empty block
has no targets, `_plan_direction` returns None, and the action passes through untouched.

Measured against pre-fix code, on the conviction fixture from
`tests/test_no_risk_free_conviction.py`:

```
risk = {}                      ->  AGGRESSIVE LONG
risk = {"risk_valid": "OK"}    ->  AGGRESSIVE LONG
risk = {"risk_valid": None}    ->  NO-TRADE (RISK TOO HIGH),
                                   reasoning "Risk check failed (OK)"
```

The first two are the maximum-intensity authorization this engine can issue, on a run where
risk was never assessed. The third is the right refusal for the wrong reason, printing a
sentence about a check that never ran.

**A validator that checks presence plus a consumer that defaults permissively is the
composition, and neither half looks wrong on its own.** That is the transferable part. Both
lines read as ordinary defensive code; the hole is in the space between them, which is the
same place Kimi Finding 1 lived — the producer was tested, the consumer was tested, and the
seam was not.

### What changed

`models/risk_model.py` — new `read_risk_verdict(risk)`. Returns the verdict, or None when
there is not one. Absent, present-as-None and present-as-not-a-boolean are one state — risk
was not assessed — and none of them is a pass. One function rather than three corrected call
sites, on rule 3: a defect found once is usually a class, and three correct copies are three
things to keep correct. Deliberately strict about the type, so an unrecognised verdict shape
fails closed. `validate_risk_parameters()` is the only producer and all six of its return
paths hand back a Python `bool` literal — verified by running the engine on the pinned
fixtures and reading the type off the result, not from the source alone.

`models/decision_model.py` — the gate refuses instead of assuming, with its own action
string, **`NO-TRADE (RISK NOT ASSESSED)`**. Not reusing `NO-TRADE (RISK TOO HIGH)`: a check
that ran and failed has a reason and gives it; an absent check does not and must not borrow
one. A bare flip of the default to `False` would have printed "Risk check failed (OK)",
because `risk_reason` defaults to `"OK"` — the same fabrication wearing the opposite sign.

`models/signal_router.py` — `_validate_engine_output` now rejects an engine output whose
risk block carries no verdict, which is what closes the reachable route;
`_build_decision_object` records the verdict that was read rather than an invented `True`.

`live_trading.py` — GLM's own site, reading through the same function. Records None rather
than False when there is no verdict: the order log is a record of what the engine said, and
"no verdict" is what it said.

`tests/test_risk_verdict_is_read_not_assumed.py` — new, 32 tests.

**The contract kept `risk_valid: bool` rather than becoming `Optional[bool]`, and that is a
decision worth having on the record.** Optional looked like the honest declaration and is the
weaker fix: `tests/test_decision_contract.py`'s `_type_ok` returns True for any Union, so the
field would have stopped being type-checked at all. Rejecting the no-verdict shape at the
validator instead makes `bool` a guarantee rather than a hope. Noted as a live hole in that
test regardless — *every* Optional field the contract declares is currently unchecked.

### Evidence against pre-fix code

**14 failed, 18 passed**, and the split is the point:

- **11 behavioural** — the gate authorizing on an unassessed block, the validator accepting
  one, the router turning one into a decision, the recorded verdict, the simulated order.
- **3 source-text** — the guard that keeps the default from coming back.
- **0 ImportError, 0 collection errors.**

That last figure needed a harness and it is stated rather than glossed. The new tests import
`read_risk_verdict`, so run plainly against pre-fix code the whole file collapses into one
collection error — which would prove only that the file is new, the exact trap the Finding 1
write-up names. The pre-fix run was made with `read_risk_verdict` grafted into
`risk_model.py` **alone**, a pure function nothing calls, with all three defective call sites
and the permissive validator left exactly as they were.

7 of the 18 pre-fix passes are negative controls, named as such in the file. The one that
matters most is `test_negative_control_an_assessed_pass_still_authorizes`: a gate made to
refuse unconditionally would satisfy every refusal test in that file.

### Verification, and where it went further than last time

`pandas_ta` 0.4.71b0 **does** install in a Linux sandbox on Python 3.12 — the Finding 1
write-up recorded it as impossible, and that was a fact about a Python 3.11 interpreter
rather than about the package. So unlike Finding 1, the end-to-end tests and the golden
snapshot were verified before delivery instead of deferred to the Windows run.

Both ways: **363 passed / 0 failed** with `pandas_ta`; **252 passed / 100 skipped / 0
errors** without it, against a 222 / 98 / 0 pre-patch baseline on the same tree. Patch
applies clean to a pristine checkout seeded from Viktor's own byte-exact CRLF files; all five
changed files md5-match what was built; suite figures are from the applied tree.

Not verified at the time: a live run against the MEXC API, and the panel rendering of the
new action string. **That run has since been made — 6 September 10:04, AEROUSDT 4h**, on
the tree carrying this fix and the Finding 5 item 6 fix together, and it is written up in
"Kimi Finding 5 item 6" below. The gate refused with `NO-TRADE (RISK TOO HIGH)` and the
reason "Risk regime classified as EXTREME RISK", so `validate_risk_parameters` returned a
genuine `bool` on live data and the gate read it. The `NO-TRADE (RISK NOT ASSESSED)` string
this fix introduced has still never been rendered on live data, and should not be: it
exists for a state that must not occur.

### Not fixed, and why

- `_compute_confidence` appends "the risk check above is what's blocking the trade" to any
  action starting with `NO-TRADE`, including `PLAN CONTRADICTS ACTION` and `DEGRADED INPUT`,
  where the risk check is not what blocked it. Pre-existing, not introduced here.
- `tests/test_pinned_source.py::test_manifest_hashes_match_the_files` hashes the raw bytes of
  the pinned CSVs, and the manifest holds their CRLF form. It therefore **fails on any LF
  checkout** — every Linux or macOS clone of this repository — and passes only on a Windows
  working tree. It failed on the clone this patch was built from and was worked around
  locally. A clean-checkout test that passes on one platform is a guard with a blind spot.
- The other invented defaults in the same two assemblies still stand: `"NORMAL RISK"`,
  `"NEUTRAL"`, `50.0`, `"OK"`. None is an authorization, which is why they were left; the
  same "the producer always sets it" reasoning has now been wrong twice in two days.

### What the handover found, and could not have found

Two process holes, both recorded as decision 8 above rather than fixed on Claude's own
initiative.

**The 6 September doc rewrite was never committed.** The head block, the Section 11 section
and the Finding 1 section existed only in Viktor's working tree through an entire session,
staged, with their message file `COMMIT_MSG.txt` sitting beside them — a complete prepared
commit that was never run. The head block asserted *"Everything pushed."* That sentence was
false about the document containing it. It landed as `038bbfa`, immediately before the F-7
commit, on its own prepared message.

The handover check ran at the end of the session that prepared it and did not catch it. That
is not the check being ignored; it is the check having no question that would fire. Items 3
and 5 ask about *untracked* files and *loose patch* files, and this was neither.

**`COMMIT_MSG.txt` has been swept into a commit once already.** `git add -A` put it into
`77d822f`; `76150d0` deleted it; a third copy was armed on 6 September and caught only
because the `git status --short` step exists and Viktor pasted it. The generic filename is
the mechanism.

## 6 September 2026 — Kimi Finding 5 item 6, and the live run that was owed

Landed at `4678f45`, pushed. Suite 363 → **377 passing, 0 failed**. Golden snapshot did not
move, predicted before the run with a checkable reason and confirmed by the fixture's
absence from `git status` rather than only by the test passing.

### The margin was one row

`_detect_swing_structure` returned `current_price` on both of its not-located paths — the
price the engine is being asked about, handed back as the structural level it had failed to
find. On the panel that reads `SWING STRUCT : $<price>`: a located level sitting exactly on
the current price, which is the strongest statement that field can make, made on precisely
the runs that located nothing.

`2 * lookback + 5` is 21 at `config.STRUCT_LOOKBACK = 8`.
`engine_core._validate_dataframe` rejects frames below 20 rows. **The two minimums disagree
by one, and on the wrong side** — so a 20-row frame passed validation, ran the whole
pipeline, and got its own price back as structure. Kimi graded it Minor and reachable, and
reachable was right.

The second return is not about length: a frame of any size in which no pivot can be
confirmed takes the same path. A clean monotonic run does it.

### Third time on the same field

`signal_router._build_decision_object` built the field as
`float(structure.get("swing_struct", exit_data.get("current_price", 0.0)))`, so a structure
block carrying no swing level got the current price written in as one — into the panel and
into the permanent decision-log record. Reachable by the composition GLM F-7 named two
commits earlier: `_validate_engine_output` checks that `"structure"` is PRESENT and never
what is under it, so `{}` passes validation and arrives there.

Both halves fixed together, under rule 3. `entry_model`'s fallback for this class was fixed
on 1 September and `panel_render`'s identical `.get('swing_struct', current_price)` on
2 September, and the producer went on inventing through both. **Closing the door and leaving
the window, twice on one field, is what made this the third fix rather than the first.**

### What changed

`structure/structure.py` — both not-located returns are `float("nan")`. `current_price`
stays a parameter; it is still what the nearest-of-high-or-low comparison measures against.

`models/signal_router.py` — the assembly default is `float("nan")`, matching the default
`engine_core` already uses when it reads the field out of the structure object.

`tests/test_swing_structure_is_not_invented.py` — new, 14 tests.

**No `degraded_inputs` entry, and that is a decision rather than an oversight.** Held by a
named test so a later change to it is visible. Not-enough-data is an ordinary return in that
module (`_detect_regime` under 15 rows, `_detect_sequence` under `6 * lookback + 10`), and
`degraded_inputs` feeds the run's degradation list, which drives the confidence ceiling and
can reach the final action. `swing_struct` is read by nothing but the panel and the record —
not by entry scoring, not by `risk_model`'s stop, not by any gate. A display-only field that
can move an authorization is a worse defect than the one being fixed, even in the safe
direction.

### Evidence against pre-fix code

**9 failed, 5 passed.** 7 behavioural, 2 source-text, **0 ImportError and 0 collection
errors — with no harness this time**, which is worth the sentence because the F-7 patch
needed one: these tests import no new name, so they run against pre-fix code exactly as
written. Nothing was grafted.

3 of the 5 pre-fix passes are negative controls, named as such in the file. A producer
rewritten to return NaN unconditionally would satisfy every "does not invent" test in that
file and destroy the field.

Both source guards match on the **parse tree** rather than on text, per rule 16: the
explanatory comments in both files quote the old expressions verbatim, so a substring search
would read the comments as the defect.

Figures both ways, from the applied tree rather than the working copy: **377 / 0** with
`pandas_ta`; **266 passed / 100 skipped / 0 errors** without it, from a 252 / 100 baseline —
all 14 new tests run in both configurations and none skips. `run_tests.py`, the runner that
works without pytest: 296 → **310 passed, 0 failed, 29 errors, the error count unchanged**.
That last figure is why the two router tests take no `monkeypatch` fixture — every
`render_panel` call in `signal_router.py` is inside `route_and_execute`, so a direct
`_build_decision_object` call needs nothing silenced, and a fixture-taking test is an error
under that runner. There are 29 of those already; this added none.

### The live run — AEROUSDT 4h, 6 September 10:04

Made on the tree carrying this fix, after the patch was applied and before the commit, and
it **discharges the run owed for F-7** as well.

```
CURRENT PRICE : $0.5437
SWING STRUCT  : $0.5063 (Lookback 8)
DECISION      : NO-TRADE (RISK TOO HIGH)
Risk check failed (Risk regime classified as EXTREME RISK.)
```

A located level that is not the current price — the unchanged branch behaving as before.
And the F-7 half: the refusal names a real reason rather than `NO-TRADE (RISK NOT ASSESSED)`
or the `Risk check failed (OK)` fabrication, so `validate_risk_parameters` returned a genuine
`bool` on live data and the gate read it instead of assuming it.

**What the run did not exercise, and structurally cannot.** A 300-bar live frame locates a
swing, so neither changed branch was reached. The NaN paths are covered by the suite only.
Reaching them on live data would need a symbol or timeframe with fewer than 21 candles of
history. This is stated because "ran it live" is otherwise read as covering the change,
and here it covers the absence of a regression rather than the fix itself.

### Not fixed, and why

- **The other invented defaults in the same router assembly still stand:** `hvn` and `lvn`
  default to `0.0`, `regime` to `"NEUTRAL"`, `sequence` to `"NONE"`, `volume_sentiment` to
  `"NEUTRAL VOLUME"`. Same class — zero is a price and NEUTRAL is a reading — and latent by
  the same argument that turned out to be wrong for `swing_struct`: an empty structure block
  reaches all six lines, not just the one. None is an authorization. They belong to the
  sweep of latent and Minor items in the fix order, and are named here so the sweep has them.
- `float(structure.get("swing_struct", ...))` still raises `TypeError` if the key is present
  with the value `None` — the exact shape of Kimi Finding 1 on a different field. Latent:
  `engine_core` never writes `None` there. Named because **"the producer always sets it" has
  now been the wrong argument three times in three days.**
- `tests/test_pinned_source.py::test_manifest_hashes_match_the_files` still fails on any LF
  checkout, as recorded with F-7. Worked around locally; nothing in this patch touches the
  fixtures.

### What went wrong delivering it

The command list was issued once, then reissued with the same steps renumbered when the live
run was inserted between the suite and the commit. **One `git add` was lost between the two
numberings** and the commit went in without its test file — two files instead of three,
caught by reading `2 files changed` in the commit output rather than by any check. Amended
before pushing, so the pushed history is clean and no force push was needed.

Recorded as a third instance under decision 8 rather than fixed on Claude's own initiative.
The candidate structural fix is one numbered list per delivery, issued once and never
renumbered.

Second, smaller: the commit message delivered as `_v1` said "Not verified: a live run" and
was already false by the time the amend happened, because the run had been made in between.
Replaced by `_v2` carrying the panel. **A commit message is written before the last thing
happens, and it is the thing that has to be re-read before it is used**, which the amend
made cheap and would not have been after a push.

## 6 September 2026 — Kimi Finding 3, and a sentence the live run found

Landed at `1045748`, pushed. Suite 377 → **400 passing, 0 failed**. The golden snapshot DID
move, was predicted to move in exactly five fields before the run, and moved in exactly
those five.

### The list could not be fixed by extending the list

That is the whole finding, and the obvious remedy is the wrong one. Kimi names seven
decision-affecting settings missing from `FINGERPRINTED_MODULES`, and `module_snapshot()`
reads a name with `getattr(module, name)`:

| setting | what it actually is |
|---|---|
| `DEGRADED_CONFIDENCE_CEILING` | a class attribute of `DecisionModel` |
| `BTC_ADJUSTMENT_CAP` | a class attribute of `DecisionModel` |
| `SPIKE_RATIO` | a local variable inside a function |
| the entry multipliers | bare literals in an if/elif ladder |
| the trend bands | bare literals in comparisons |
| `window=30` | a keyword literal at a call site |
| `0.0015` | a bare literal assigned to a local |

`getattr` on a module reaches none of the last five. **Six of the seven are not omissions
from a list. They are things a list of that shape cannot hold.**

And the finding is narrower than the defect. An enumeration of constants cannot see a
changed comparison operator, a reordered branch, or a new term in a formula — all of which
change what the engine decides, and all of which left the record byte-identical. Rule 11
(a list of names decays), rule 16 (a guard built from examples inherits their gaps) and
rule 28 (change the structure, do not write an instruction to be careful) all point the
same way: adding seven names satisfies the finding's letter and leaves the mechanism that
produced it intact, ready to be short by seven more.

### What changed

`core/code_fingerprint.py` — new. For every `.py` file under the repository root that is not
in an excluded **directory**: read bytes → `ast.parse` → strip docstrings → `ast.dump` →
SHA-256, and `code_hash` is a SHA-256 over the sorted (path, digest) pairs. 32 files, about
100 ms per run. No list of constants and no list of modules, so a constant written tomorrow
is covered the moment it exists.

The parse tree rather than the text, deliberately: this repository rewrites its explanatory
comments in nearly every commit, and a fingerprint that always differs carries exactly as
much information as one that never does — which is the defect being fixed.

`core/engine_core.py` — takes the fingerprint in the lineage block, writes `code_hash` into
provenance and the whole fingerprint including per-file digests into the archive meta. The
decision log gets one line per run forever; the archive is gzipped and written once per
distinct run, which is where thirty-two digests belong. Wrapped in `try/except` on the same
argument as the archive block beside it.

`core/decision_log.py` — `module_snapshot()` resolves dotted names through classes, so the
two `DecisionModel` constants are in the readable record for the first time.
`models.entry_model` gains an entry: its point budget decides every entry score the engine
prints and was never fingerprinted at all.

`core/decision_contract.py` declares `code_hash`. `tests/test_golden_path.py` adds it to
`VOLATILE`. `tests/test_code_fingerprint.py` — new, 23 tests.

### What it deliberately does not do, and this one is reversible

`code_hash` is **not** folded into `run_hash`. Folding it in would move `run_hash` on every
commit touching any engine file — and `run_hash` is pinned by the golden snapshot and is the
archive's filename, so every commit would fail the golden test and need a re-baseline.
**Re-baselining is the step where a real change gets waved through alongside the expected
one.** That check has caught more defects here than any other, and spending it to buy a
property the record already carries in a separate field is a bad trade.

So `run_hash` keeps its documented meaning — which inputs, under which settings — and
`code_hash` sits beside it saying which code. Held by a named test that asserts on the
**parse tree** of the `run_hash` call site rather than on its text, because the comment
beside that call discusses `code_id` at length and a substring search would read the
explanation as the thing it warns against (rule 16, and rule 37 — knowing a rule is not
applying it). The test's own failure message says what to do if the trade should go the
other way.

This was Claude's call under the delegation, not Viktor's, and it is one line to reverse.

### Evidence against pre-fix code

23 tests against an unmodified checkout of `eeb351d`: **21 failed, 2 passed.**

**The honest number is 7** — the behavioural failures, from the half of the file that
imports nothing this patch adds and therefore runs against the old engine exactly as
written: provenance carries no code identity; the stored log record carries none; the
archive meta carries no per-file digests; `ProvenanceBlock` does not declare the field; the
degraded-confidence ceiling is not in the record; the BTC adjustment cap is not in the
record; `models.entry_model` is not fingerprinted at all.

The other **14 fail with `ModuleNotFoundError`** and prove the module is new, not that the
defect was real. Rule 23, and the file says so where those tests begin. The 2 that pass
pre-fix are named for what they are: a regression guard, and the decision guard above.

Three negative controls, named in the file: a comment does not move the hash, a docstring
does not move it, and the same source as CRLF and as LF hashes identically. The third earns
its place here specifically — `test_pinned_source.py` already fails on any LF checkout
because a hash was taken over bytes that carry line endings.

The positive side edits the finding's own constants at their own lines in throwaway copies
of the real files — `0.0015`, `SPIKE_RATIO`, `DEGRADED_CONFIDENCE_CEILING`, `window=30` —
plus `>=` becoming `>` on a trend band, which is not one of the seven and is the reason the
fix is a source hash rather than a longer list.

### The golden re-baseline, predicted before it was run

Adding constants to `FINGERPRINTED_MODULES` changes `module_snapshot`, which is inside
`run_hash`, which is inside the archive filename. Predicted as five fields across two
top-level keys, and that is what the diff showed:

- `provenance.module_constants` — gains `DecisionModel.BTC_ADJUSTMENT_CAP`,
  `DecisionModel.DEGRADED_CONFIDENCE_CEILING`, and the `models.entry_model` block (9 names)
- `provenance.run_hash` — `a655ec56…` → `c8e207a1…`
- `lineage.run_hash` — the same value
- `provenance.archive_path` — `testusdt_4h_a655ec562938e176.json.gz` →
  `testusdt_4h_c8e207a1d852aac4.json.gz`
- `lineage.archive.path` — the same path

The archive filename is the mechanical consequence rule 33 was written about: it is built
from `run_hash[:16]` and moves with it. **Nothing else moved.** Every decision field is
byte-identical — bias components, indicators at the decision bar, risk inputs, entry, risk,
exit watch. `code_hash` does not appear in the snapshot at all, which is `VOLATILE` doing
its job.

### Figures, from the applied tree rather than the working copy

| | before | after |
|---|---|---|
| pytest, `pandas_ta` installed | 377 / 0 | **400 passed, 0 failed** |
| pytest, `pandas_ta` absent | 266 / 100 | **286 passed, 103 skipped, 0 errors** |
| `run_tests.py` (no pytest) | 310 / 0 / 29 | **333 passed, 0 failed, 29 errors** |

The error count under `run_tests.py` is **unchanged**: none of the 23 new tests takes a
pytest fixture. 20 of the 23 run without `pandas_ta`; the 3 that skip are the ones that run
the engine end to end.

### The live run — AEROUSDT 4h, 6 September 10:51

Made on the tree carrying this fix, after the patch was applied and before the commit.

```
CURRENT PRICE : $0.5451
SWING STRUCT  : $0.5063 (Lookback 8)
CONFIDENCE (decision): 73.86/100
DECISION      : NO-TRADE (RISK TOO HIGH)
Risk check failed (Risk regime classified as EXTREME RISK.)
```

The panel is unchanged in shape — no new line, no missing line — and no
`Source fingerprint could not be taken` warning appeared, so the new `try/except` was not
exercised and the fingerprint was taken on live data.

**The hash matched the sandbox bit for bit.** `44e085cfa1fa0b5bb48ccd7a917b3f8db578619dc39d1386d333dcd3d9c49994`
on Viktor's Windows machine under Python 3.12.10 against a CRLF checkout, and the identical
value in a Linux sandbox under Python 3.12.3 against an LF checkout. The prediction made
before the run was weaker than this — it claimed only that the file set matched, having
enumerated the 31 `.py` files over the device bridge. Platform-independence, line-ending
independence and 3.12-minor-version independence of `ast.dump` all fell out together and
are now observed rather than assumed. **Not** observed: any interpreter outside 3.12.

### What the run found that neither report contains

The BTC block raised confidence 73.86 → 75.80 and explained it:

```
BTC BIAS      : NEUTRAL
CORRELATION   : MODERATE POSITIVE (+0.51) over last 30 candles
BTC-ADJUSTED CONFIDENCE: 75.80/100 (vs 73.86/100 unadjusted)
 - BTC is also neutral, agreeing with AERO's own bias.
```

AERO reads `BULLISH CONFIRMED`. A neutral BTC cannot be "also" what a bullish AERO is, and
it cannot be agreeing.

**Verified**, `decision_model.py` 704-768: `agreement` is decided by the SIGN of `btc_score`,
and the words in `agree_phrase` come from `btc_detailed`, the LABEL. Those disagree whenever
the score is non-zero but below the labelling threshold. The arithmetic is sound —
73.86 + 1.94 = 75.80 requires `agreement = +1` at the printed +0.51, which puts `btc_score`
just under 19. **The number is behaving as designed; the sentence is false.**

**Not verified**: that BTC's label threshold is `RAW_BIAS_THRESHOLD = 20.0`. The ~19 is
inferred from the panel arithmetic, not observed, and `calculate_dynamic_bias` is unread.

**Why it is not simply Kimi Finding 2.** Finding 2's title says "*and the reason string
asserts agreement the data contradicts*", so this falls inside its title. But Finding 2's
body and its exhibit are entirely about `abs(correlation)` discarding the correlation's
sign, at −0.90. Here the correlation is **positive** and the sign was never in question, so
that mechanism did not fire. This is a second, independent route to the same class of false
sentence, reachable on exactly the positive correlations the suite already covers — and
Kimi's note that the tests cannot see the inverted case is true of this one too, for a
different reason: **nothing asserts the sentence against the label.**

Rule 3: a defect found once is usually a class. Filed as input to decision 3 rather than
fixed, because whether Finding 2 is fixed or accepted as a recorded limitation is Viktor's
ruling and this changes what he is ruling on.

Rule 25 again — reading finds what is written, running finds what happens. This survived two
independent reviewers and every pass over that function, and surfaced on the first live run
that happened to land in the band.

### Not fixed, and why

- **`engine_version` is still the static string.** It is a release label maintained by hand
  and is now documented as one, in the contract and at the site that writes it. Making it
  move automatically would put a second computed value beside `code_hash` carrying the same
  information, and the banner/version mismatch it is tangled up with is Kimi Finding 6.
- **`code_hash` depends on the interpreter.** `ast.dump` gains node fields between CPython
  versions. Recorded rather than worked around: `python` is carried beside the hash in the
  archive meta, and a test asserts it is there. Observed identical across 3.12.3 and
  3.12.10; untested outside 3.12.
- **The entry multipliers, the trend bands, `SPIKE_RATIO`, `window=30` and `0.0015` are
  still unnamed literals.** Covered by the source hash, absent from the readable snapshot.
  Naming them means moving them to module level, which is a change to the decision path;
  this patch changed the record. Worth doing as its own item with its own golden diff.
- **A rerun on identical inputs after a code change still overwrites the earlier archive.**
  The archive is content-addressed by `run_hash`, which does not move on a code change. The
  frames are byte-identical so nothing about the inputs is lost; what is lost is the earlier
  run's `meta.code`. It follows directly from the `run_hash` decision and belongs beside it.
- **The other invented defaults in the router assembly** named at `4678f45` still stand.

### What went right delivering it, for once

The candidate structural fix recorded under decision 8 on 6 September — **one numbered
command list per delivery, issued once and never renumbered** — was used here for the first
time. Nineteen steps, with the live run at step 7 and an explicit instruction to stop there,
paste the panel, and resume at step 8 under the same numbers. Nothing was lost between the
two halves; `git status --short` showed seven entries in the INDEX column before the commit
and the commit reported seven files changed, both predicted in advance.

That is one delivery, not evidence. But it is the first delivery since the rule was written
where a run had to be inserted mid-list, which is the exact shape that lost a `git add` at
`4678f45`. Decision 8 remains unruled.

## 6 September 2026 — the suite was destroying the decision record

Landed at `fc35a2f`, pushed. Suite 400 → **406 passing, 0 failed**. No engine
source file touched, so no live run was owed and `code_hash` did not move.

### How it was found, and why neither reviewer could have

Not by reading. By running the suite against a clean clone and listing `logs/` before and
after. Every individual line involved is unremarkable; the damage exists only at runtime.
Rule 25, and this is the sharpest example the project has produced: two independent
reviewers read these files, one of them filed a finding about the very test that does the
worst of it, and the mechanism survived both.

### Four routes into the engine's own record, and the fourth surfaced after the first fix shipped

**1. Twenty-eight tests, across ELEVEN files, ran the engine against the real
`config.LOG_DIR`.** Nothing repointed it. A full suite run appended nine real decision
records to `logs/phase7_decision_log_aerousdt.jsonl`, plus one error record, and wrote an
archive, a chart and the cross-run state file. The writers include `test_traceability.py`
and `test_code_fingerprint.py` — the two files whose entire subject is what the permanent
record contains. `test_the_code_hash_survives_into_the_permanent_log_not_just_the_return`
asserts against a log it wrote itself moments earlier.

**2. A twelfth file deleted the directory.** `test_lineage.py`'s archive-path spelling
test passed the relative literal `"logs/"` to `lineage.write_archive` and then called
`shutil.rmtree("logs", ignore_errors=True)` in a `finally`. Resolved against the
repository root, that is the engine's real log directory: decision log, every archive, the
charts, the state file.

**3. A thirteenth created it as a side effect.** `test_imports.py` purges and re-imports
every engine module, which re-executes `core/config.py` and undoes any redirection;
`main.py` then opens a `logging.FileHandler` in `config.LOG_DIR` at module scope. The test
whose subject is whether modules import was creating the engine's log directory.

**4. A fourteenth wrote into it through the CAPITALISED spelling.**
`test_frame_ownership.py` saved two PNGs to `REPO_ROOT/Logs/Charts/`. On Linux that is a
stray second directory; on Windows, where the filesystem does not distinguish the two
names, it is the engine's live chart directory, beside the chart of the last real run.
This is exactly the defect `test_no_module_hardcodes_a_path_config_declares` was written
about — in a file that test does not scan, because it checks modules and these two lines
are in a test.

### The first patch was wrong, and the way it was wrong is the lesson

v1 was built, verified in a Linux sandbox, delivered, applied — and **failed on Viktor's
machine at the first test run**, with two failures.

The guard watched the directory named exactly `logs`. Route 4 writes to `Logs`. On Linux
those are two directories, so the guard reported clean and the sandbox verification said
405 passing. On Windows they are one directory and the guard fired immediately. **A guard
whose result depends on which platform it ran on is not a guard**, and the platform it was
verified on was not the platform it runs on.

The second failure was a negative control asserting that writing `"one\n"` produces a
4-byte file. Text mode on Windows produces 5. A hardcoded byte count that ignored line
endings — the third time this repository has been bitten by that exact thing, after
`test_pinned_source.py`'s manifest and the audit package's normalisation.

Both are recorded here rather than quietly fixed because the first one changes how
verification should be read from now on: **a result from the Linux sandbox is evidence
about Linux until something makes it evidence about Windows.** The guard now scans by
lowercased directory name so a Linux run sees what a Windows run would, and that
behaviour has its own test. Confirmed by reverting only the route-4 fix: the guard then
fails on Linux, where v1's passed.

v1 also said "twenty-eight tests across twelve files". Twenty-eight is right; eleven files
write and the twelfth deletes. Caught by recounting the evidence, not by review.

So the suite did not merely pollute the record. It destroyed it and partially rebuilt it
out of test output, and `logs/` is gitignored, so nothing anywhere held a second copy.

### It had already happened, and this is what was lost

The live log holds eleven records. Ten are a suite run at 08:51 UTC — one `run_hash`,
`3a68572a83`, one bias score, 78.6973, and one error record with no `code_hash`. The
eleventh is the 10:51 AEROUSDT run at 73.859. Reproduced in a sandbox: a single full suite
run writes exactly those ten, error record included, plus
`logs/archive/aerousdt_4h_3a68572a835705c5.json.gz` and
`logs/charts/chart_AEROUSDT_4h.png`.

**Gone:** the 10:04 run's raw record and its archive, and the three synthetic Section 11
records this file spent a section describing. The 10:04 run now survives only as the panel
pasted into this document. The statement above that both runs' raw records "are only on my
disk" was true when written and is no longer true of 10:04.

The append-only writer (`decision_log.py:294`, `open(path, "a")`) means records cannot
vanish by writing. The `rmtree` is how they vanished. What cannot be recovered from here
is the contents; if a second `phase7_decision_log_aerousdt.jsonl` exists elsewhere on
disk, they are in it.

### Evidence against pre-fix code

A pristine checkout of `717ea30`, seeded with three marker records, a marker archive, a
marker chart and a marker state file, then run:

**400 passed — and every marker was gone.** Three records replaced by ten test records.
`aerousdt_4h_deadbeefdeadbeef.json.gz` deleted. Chart and state file overwritten.

A green suite destroyed the evidence. That is the defect executed rather than argued.

The same experiment on the patched tree, through all three configurations: **406 / 292 /
339 passing**, and
`logs/phase7_decision_log_aerousdt.jsonl` came through with sha256
`c6000cb40613a8f0fafb7b45826f069f2d627f40c52eeaf5b81d842ebf1e9ec3` unchanged, all four
seeded files intact, through all three test configurations.

### What changed

`tests/conftest.py` points `config.LOG_DIR` and `config.CHART_DIR` at a temporary
directory **at import time** — not as a pytest fixture, because `run_tests.py` never calls
a fixture but does import this module. One place, both runners. The shipped values are
kept so a guard can prove this is a redirection rather than a change to what a real run
does.

`tests/test_lineage.py` runs the archive-path test in a working directory of its own. The
argument stays the relative literal `"logs/"` deliberately: the defect it pins is a
separator inside a path built from that argument, so normalising the argument would test
something else.

`tests/test_golden_path.py` gets its own workspace and keeps the relative log spellings,
so `provenance.archive_path`, `lineage.archive.path` and `decision_log_path` still record
as `logs/...`. **The golden snapshot did not move and was not re-baselined.** Adding those
three fields to `VOLATILE` was the easy fix and was rejected — it would have retired the
cross-platform path-spelling coverage that caught a real defect on Viktor's machine.
`_state_path()` now resolves against that workspace rather than `REPO_ROOT`.

`tests/test_imports.py` gets a working directory too. Purging and re-importing every
module re-executes `core/config.py`, undoing the redirection, and `main.py` opens a
`FileHandler` in `config.LOG_DIR` at module scope — so the test whose subject is whether
modules import was creating the real `logs/` as a side effect. Redirecting config again
after the purge would be a race against import order; moving the working directory is not.

`tests/test_explicit_configuration.py`'s `.gitignore` check reads the shipped values, since
the live ones are now a temp directory during a run. The question it asks is about what a
real run does on a clone.

`tests/test_frame_ownership.py`'s two plotting tests write their PNG to a temporary
directory instead of `REPO_ROOT/Logs/Charts/`. Neither test cares where the file lands;
both care what happens to the frame and to the log while it is written.

`tests/test_real_log_directory_untouched.py` — new, 6 tests. Two earn their place
specifically: a negative control proving the snapshot comparison can report a difference at
all, since it returns early when nothing exists on either side; and one pinning the
case-insensitive scan, which is the thing v1 got wrong.

### Where the verification stopped

The third guard — that the real `logs/` came through unaltered — is **order-dependent**,
and its docstring says so. It sees only damage done by tests that ran before it, and it
cannot see a test that deletes the directory and rebuilds it byte for byte. The guarantee
is the redirection; that test is the alarm for when the redirection stops working.
Confirmed non-vacuous: with the two redirection lines commented out, both config guards
fail.

### Figures

| | before | after |
|---|---|---|
| pytest, `pandas_ta` installed | 400 / 0 | **406 passed, 0 failed** |
| pytest, `pandas_ta` absent | 286 / 103 | **292 passed, 103 skipped** |
| `run_tests.py` (no pytest) | 333 / 0 / 29 | **339 passed, 0 failed, 29 errors** |

Error count unchanged at 29: none of the six new tests takes a pytest fixture, and all six
run without `pandas_ta`. `code_hash` unchanged at `44e085cfa1fa…`, computed on both
trees rather than assumed — `core/code_fingerprint.py` excludes `tests` by name.

### Rule 3, for the third time in four days

The Section 11 harness was fixed for this exact defect four commits earlier, by repointing
`config.LOG_DIR` for the duration. That fix was applied to one caller and nobody asked
whether anything else did the same thing. `test_code_fingerprint.py`, added at `1045748`
the day before this was found, shipped a new instance of it — and the predictions written
for that patch did not name the write.

GLM F-8 saw the visible edge of this and read it as test hygiene: `test_golden_path.py`
controlling the C3 state file by deleting it. It is still open, and it is now deleting a
file in a temporary directory.

### Not fixed, and why

- **Where the lost records went is not recoverable from here.** Nothing in the repository
  can rebuild them.
- **`logs/` is still gitignored**, so the record still has no second copy and the next
  accident still costs everything in it. That is part of decision 7.
- **The suite still writes decision records**; they land somewhere harmless now. Nothing
  asserts that a test which runs the engine meant to write one.
- **`test_no_module_hardcodes_a_path_config_declares` still scans modules only.** Extending
  it to `tests/` would have caught route 4 by reading rather than by running, and is the
  structural answer to that route specifically. Left out deliberately: it is a source-text
  check, this repository has been burned by those before, and the behavioural guard added
  here covers the same class on both platforms. Recorded as a candidate, not adopted.
- **`test_golden_path.py::_clear_state()` still controls the C3 state file by deleting it**
  — GLM F-8, still open. It now deletes a file in a temporary directory, which removes the
  blast radius but not the finding.

## 6 September 2026 — the document audit

Prompted by nothing in particular, which is the point: the last time this document set was
read end to end, on 2 September, it found a whole Critical that had never been entered
into any roadmap.

### The audit-package record is intact, and this is the good news

All three manifests verify **byte-for-byte** against their recorded build commits:
round 2 60/60 at `390a7945`, round 3 71/71 at `c4d6969c`, round 4 71/71 at `417cadf7`.
Zero missing, zero mismatched. What each reviewer actually graded is provable, which is
the property `build_audit_package.py` was written to give and it holds.

They verify against an **LF** checkout, and the reason is worth recording:
`build_audit_package.py` reads text-mode (line 159) and writes `newline="\n"` (481, 503),
so the bundle is normalised. `tests/test_pinned_source.py` hashes raw bytes and does not.
**Two hashing schemes over the same repository with opposite line-ending behaviour** — and
the non-normalising one is the one that fails on every non-Windows checkout and has been
worked around locally twice. That argues for fixing it by normalising rather than by
working around it a third time. It belongs with GLM F-8/F-9 in the test-hygiene pass.

### One suspicion, checked and wrong

`docs/audit_package/phase7_engine_source.md` and `phase7_test_suite.md` are dated
30 August, and `item16_review_instruction_rev5.md` cites both by name as "every module the
engine runs, complete." That reads like a stale-bundle trap. It is not:
`build_audit_package.py` documents them as the round-1 record kept deliberately and copies
fresh bundles into `round*/UPLOAD_THESE`. Recorded because a checked-and-wrong suspicion
is worth exactly as much as a confirmed one, and costs the next reader the same hour if it
is not written down.

### No build script can write into this repository

Covered under "Open — work" item 3 above, because it is the answer to why the Engineering
Notes gap grows. Repeated here for the reader who arrives at the document audit first:
nine of the ten `docs/build/build_*.py` scripts hardcoded `/tmp/outputs/`, and two of them
also read source material from `/tmp/outputs/audit_raw/` that is not in the repository at
all. **This audit said "all ten" and the count was nine** — `build_audit_package.py`
already resolved repo-relative. Corrected and fixed the same day; see the last dated
section of this file.

### A dangling reference in the front door

`README.md` and `docs/build/README.md` both cite `docs/Phase7_Audit_Findings_Complete.pdf`.
It does not exist anywhere in the repository. `build_findings_bundle.py` builds it — to
`/tmp/outputs/`, from a source directory that is also not here.

Every other dangling reference found is benign: gitignored build outputs
(`commit_messages_PART7_ONLY.md`, `execution_transcripts.md`,
`version_control_history.md`, `prior_observations_PART8_ONLY.md`), or already recorded as
dangling in this file (`claude/phase7-*`, `Phase7_Engineering_Constitution_v1.0_Rev6.pdf`).

### What this audit did NOT do

The eight PDFs — Constitution, Roadmap, Engineering Notes, Remediation Plan, Documentation
and Change Log Standard, Tier 0 Companion, Credential Security Protocol, Audit Execution
Instructions — were **not opened** at the time this section was written. **They have since
been — see "The semantic half of the document audit" below, done the same day.**

## 6 September 2026 — the semantic half of the document audit

Read each of the eight PDFs against the current repository (tip `0f8e04a`) — the pass the
mechanical half above said would be where a second Finding 3 turns up, if one is there. It
found one candidate for that class, plus two smaller, genuinely new discrepancies —
everything else it turned up was already tracked, now with exact code citations.

### New: the Audit Execution Instructions describe a procedure nobody follows anymore

`Phase7_Audit_Execution_Instructions.pdf`, frozen since 29 August, is the one document in
this set explicitly meant to survive being put down and picked up again — it is what a
future round 5 would be run from. It still describes a manual, browser-based OpenRouter
chat procedure: open a chat, pick the model from a dropdown, set Max Tokens 64,000, upload
four files (Constitution PDF, source `.txt`/`.zip`, an audit-package PDF, an evidence
`.zip`).

Nothing about that is how round 3 or round 4 actually ran. Round 4 ran through
`docs/build/send_audit_round.py`, a script that pins model *and* provider explicitly
(`"only": [PROVIDER_SLUG], "allow_fallbacks": False`) — because round 3 went to GLM 5.3
Flash by accident when a chat UI's Auto Router silently substituted it, the exact failure
this document's own "Contamination Rules" section does not name. The script sets
`MAX_OUTPUT_TOKENS = 200_000`, not 64,000 — and its own comment records that even 64,000
had already failed once (`LARGEST_PRIOR_RESPONSE = 36_085  # Kimi K3, 2 September 2026, no
report produced`). It sends seven plain-text files including `item16_review_instruction_rev5.md`,
not the doc's "four files" of PDF/zip. And the materials-count table
(`docs/build/build_audit_instructions.py:260-261`) hardcodes "19 source files, 207,625
bytes"; the repository has 23 `.py` files outside `tests/` and `docs/` today.

Not fixed here — rewriting it is real work, not a one-line correction, and it only matters
before a round 5 is actually run. Recorded as a finding rather than scheduled, severity
Major as a process document: following it as written would misconfigure a future round
without warning about the one failure mode that has already cost one.

**PARTIALLY CLOSED 6 September 2026.** Not rewritten — that is still owed, and only
matters once a round 5 is imminent — but a prominent correction notice now sits at the top
of the document, before "1. Materials", naming all four divergences above with citations to
`send_audit_round.py`. A person picking this document up to run round 5 now sees the
correction before the stale procedure rather than following it blind. Landed `8051f5f`.

### New: the Documentation and Change Log Standard states the wrong register size

`Phase7_Documentation_and_Change_Log_Standard.pdf` says twice, including in its own
scope-freeze sentence, that the Constitution is frozen at 17 Tier 1 / 7 Tier 2 / 10 Tier 3
/ 6 Tier 4 invariants — 40 total. That was true on the document's own 25 August dateline and
became false the next day: the Constitution ratified 26 August at
Revision 6 added four Tier 1 items (18-21), making the register 21/7/10/6 = 44 — the count
this file itself has used everywhere else since. The Roadmap and the Audit Execution
Instructions both correctly say 21/7/10/6. A document about documentation discipline
misstating the size of the register it sits beside, uncorrected for at least twelve days,
is Moderate and mildly ironic rather than dangerous. Not fixed here.

**CLOSED 6 September 2026.** Both mentions corrected to 21/7/10/6, a correction paragraph
added rather than a silent edit, and a Version History row (v1.1) — the document's first
revision since v1.0. Landed `8051f5f`.

### New: `run_tests.py`'s "works without pytest" claim doesn't hold under a genuine no-pytest environment

Engineering Notes entries #86-87 (and `run_tests.py`'s own framing) describe it as the
runner that works without pytest installed. Reproduced two ways with pytest actually
absent: with pytest fully uninstalled, 33 of roughly 66 test files fail to import at all
(most use `pytest.mark.parametrize`, `pytest.skip`, `pytest.approx` at module scope), giving
55 passed / 1 failed / 33 errors — not the 29-errors figure the Notes report anywhere. With
pytest installed but `pandas_ta` absent (a real combination, since `pandas_ta==0.4.71b0`
needs Python ≥3.12 and nothing stops an older clone from having pytest without it),
`run_tests.py` crashes outright: `pytest.skip()` raises `Skipped`, which subclasses
`BaseException` rather than `Exception`, so the runner's own `except Exception` in
`_run_one()` does not catch it — first hit is
`tests/test_code_fingerprint.py::test_the_archive_meta_says_which_file_changed_not_only_that_one_did`,
added by commit `1045748`. The 29-errors figure the Notes cite is real, but only in the one
environment the project actually runs (pytest **and** pandas_ta both installed) — the
document never states that precondition. Severity Minor/Moderate: does not touch the
decision path, and Viktor's own Windows/3.12.10 machine always has both, but it is a live
bug in the project's own test tooling on exactly the axis (dependency/interpreter variance)
this project is otherwise careful about. Not fixed here.

**CLOSED 6 September 2026.** Both call sites (`_run_one()` and `main()`'s `load()` call)
now catch `BaseException` rather than `Exception`, re-raising `KeyboardInterrupt` and
`SystemExit`. Reproduced fixed in both problem environments: pytest-without-pandas_ta no
longer crashes (240 passed / 1 failed / 122 errors, a real if different count rather than
no count at all); the module-level `importorskip` crash is fixed too, a second call site
the original report did not separately name. The docstring's "no pytest, no plugins" claim
is corrected to what was actually verified. `code_hash` moves, predicted and confirmed:
`44e085cfa1fa…` → `6c4ef720baf9…` — `run_tests.py` is deliberately fingerprinted (its own
test says so). In the project's real environment (pytest + `pandas_ta`), before and after
are byte-identical, run twice: 344 passed / 1 failed (the known LF-clone artifact,
unrelated) / 29 errors — confirming the fix is inert where it needs to be. Landed `8051f5f`.
**Head-block `code_hash` below is now the new value.**

### Confirmed, not new — restated with exact current-code citations

Everything else the eight documents were checked against was either accurate today or was
already tracked in this file. Worth having on record with citations rather than only as a
restated claim:

- **Item 10 (Consistent Semantics) is still violated, still contained.** `engine_core.py`
  1042 emits `confidence_score` as `trend["trend_health"]` (an unsigned magnitude);
  `signal_router.py` 423 emits the same field name for the real computed confidence.
  Confirmed unreachable: `SignalRouter` reads `dm_result["confidence"]`, never the
  mismatched field, so the panel is not affected. This is the already-tracked Finding 9.
- **The `decision_contract.py` "independently of trend health" comment is confirmed false,
  with the exact mechanism**: `risk_model.py:323`'s `classify_risk_regime` takes
  `trend_health` as a direct parameter and branches on it at lines 329 and 331. Already
  open decision 2; no change to its characterization.
- **The Roadmap (Revision 4, 29 August) still presents a sixteen-item sequence as pending
  that is now mostly done** — items 5, 8, 10, 12 and 13 of that sequence all verified
  present in current code (`indicators.py`'s deletions, `data/validation.py`,
  `decision_contract.py`, `decision_log.py`, the position-sizing removal). Its compliance
  table (21/17/6 of 44, from the single 27 August audit) predates three further rounds.
  Already known; now quantified against code rather than only asserted stale.
- **Tier 0 Companion and Credential Security Protocol both still point at
  `Phase7_Engineering_Constitution_v1.0_Rev6.pdf`**, which does not exist. Already recorded
  as a dangling reference in this file; confirmed still unfixed at tip, source is
  `build_tier0_companion.py:170` and `build_credential_protocol.py:168`.
- **The audit-package manifests still verify byte-for-byte** (round 2 60/60, round 3
  71/71, round 4 71/71) and the Remediation Plan, correctly self-labelled a frozen 29
  August snapshot, asserts nothing about today's repo that is false.

### What this pass could not check

Whether OpenRouter's pricing and procedure claims still hold (external, not this repo);
the "Item 20 amendment... blocked on Gemini and Copilot refusing to ingest the Constitution
PDF" sub-thread in the Roadmap (not traced to ground truth, not asserted either way);
whether Credential Security Protocol's operational practices (key rotation, IP
allowlisting) are followed — none of these are checkable from a static read. The
Constitution's own Items 15 and 17 (backtesting isolation, empirical-over-theoretical) stay
correctly "Unknown" — there is no backtesting code in the tree to check against.

**All three new findings are now fixed, 6 September 2026, landed `8051f5f`.** Two
docs-only (register count, the audit-instructions correction notice); one real code
change (`run_tests.py`), which moved `code_hash` — predicted, confirmed, and recorded in
the head block. None of this touched the decision path, and nothing here was a ruling —
the fourteen-item sweep is the only piece of open work left that touches it.

## The sweep of latent and Minor items — assembled 6 September 2026

The next piece of engineering work, and it needs no ruling first. **No single section of
this file contained it**: it is assembled from the "Not fixed, and why" subsection of each
of the four 6 September fix write-ups, plus the GLM-only and Kimi-only lists in the
round-3 versus round-4 comparison — and, as recorded there, that comparison was itself
short by two, so F-1 and F-10 come from the round-3 report directly.

Fourteen items. Duplicates across sources are merged and noted.

**Invented defaults and fabricated readings — one class, and the largest part**

~~1. `_merge_btc_context` remaining defaults~~ **DONE 7–8 Sep 2026 (Grok), `22afea2`.**
~~2.~~ **DONE 7–8 Sep 2026 (Grok), `22afea2`.** The router's structure assembly: `hvn`/`lvn` → `0.0`, `regime` → `"NEUTRAL"`,
   `sequence` → `"NONE"`, `volume_sentiment` → `"NEUTRAL VOLUME"`. *(Finding 5 item 6,
   was not fixed at 6 September — named there specifically so this sweep would have them)*
~~3.~~ **DONE 7–8 Sep 2026 (Grok), `22afea2`.** The same two assemblies: `"NORMAL RISK"`, `"NEUTRAL"`, `50.0`, `"OK"`. *(F-7,
   was not fixed at 6 September. Overlapped items 5.3 and 5.4 below on `"NORMAL RISK"` and `50.0`.)*
~~4.~~ **DONE 7–8 Sep 2026 (Grok), `22afea2`.** `float(structure.get("swing_struct", …))` raised `TypeError` when the key was present
   with the value `None` — Kimi Finding 1's exact shape on a different field. Latent only
   because `engine_core` never writes `None` there, and "the producer always sets it" had
   been the wrong argument three times before this fix. *(Finding 5 item 6)*
~~5.~~ **DONE 7–8 Sep 2026 (Grok), `22afea2`.** Kimi Finding 5's remaining items, 1-5 and 7 — item 6 was fixed 6 September:
   `calculate_dynamic_regime`'s `vol_ratio = 0.01` default printing an invented
   `MEDIUM VOLATILITY`; the same function's `"NEUTRAL STRUCTURE"` when the STRUCTURE
   column is absent; `decision_model`'s `trend.get("trend_health", 50.0)` midpoint
   fabrication; its `risk.get("risk_regime", "NORMAL RISK")`; `panel_render`'s
   `risk.get("validation_score", 0)`; and `_detect_hvn_lvn` returning adaptive-window
   price extremes **as** HVN/LVN with nothing appended to `degraded_inputs`.

**Dead code, and one stale contract**

~~6.~~ **DONE 7–8 Sep 2026 (Grok), `4d56f2a`.** GLM F-2 and Kimi Finding 7 together: `pct_slope` was unconsumed; `data/validation.py`'s
   `is_valid` was unconsumed; `StructureAnalysisResult` was declared as the formal return contract,
   never used as an annotation, and **stale** — it lacked the `degraded_inputs` key
   `analyze()` now returns, so the one formal contract in the file described a shape the
   function no longer produced; `test_live.py` at the repository root imported a name that
   had been deleted and died on import.
~~7.~~ **DONE 7–8 Sep 2026 (Grok), `4d56f2a`.** GLM F-11: `exit_model.build_exit_watch`'s `or 0.0` treated `0.0` and `NaN` identically,
   safe only because `NaN > 0` is False.
~~8.~~ **DONE 7–8 Sep 2026 (Grok), `4d56f2a`.** GLM F-1: the second `clean_series` call inside `pct_slope` — removed with item 6.

**Statements the code does not support**

~~9.~~ **DONE 7–8 Sep 2026 (Grok), `c3b0d43`.** Kimi Finding 6: the banner asserted "Connecting to MEXC API…" on offline pinned runs, and
   said Phase-7.3 while `engine_version` said v1.0.
~~10.~~ **DONE 7–8 Sep 2026 (Grok), `c3b0d43`.** Kimi Finding 4, the separable half: `decision_contract.py`'s comment claiming the risk
    gate is independent of trend health was false about the code beside it — comment corrected.
    **Whether the coupling itself breaks Item 14 is still decision 2** and was not
    touched here.
~~11.~~ **DONE 7–8 Sep 2026 (Grok), `c3b0d43`.** GLM F-6: BTC-side `compute_trend_health` degradations were not propagated into the AERO
    run's degradation list.
~~12.~~ **DONE 7–8 Sep 2026 (Grok), `c3b0d43`.** GLM F-10: `module_snapshot` recorded `{"<import failed>": str(exc)}` into the run-hash
    payload, undocumented — now documented.
~~13.~~ **DONE 7–8 Sep 2026 (Grok), `c3b0d43`.** `_compute_confidence` appended "the risk check above is what's blocking the trade" to
    every `NO-TRADE` action, including `PLAN CONTRADICTS ACTION` and `DEGRADED INPUT`,
    where the risk check was not what blocked it.

**Structural**

~~14.~~ **DONE 7–8 Sep 2026 (Grok), `c3b0d43`.** GLM F-3: `calculate_structure` wrote STRUCTURE/HVN/LVN both onto its returned frame
    and into its dict, and `engine_core` read both routes — now one route.

**Deliberately NOT in the sweep, and why**

- Kimi Finding 2 and the second mechanism the 10:51 run found — decision 3.
- The Item 14 coupling — decision 2. The false comment above is separable and is in.
- The merge-time degradation gap: `decision_model.evaluate()` is called before the BTC
  block is assembled, so a degradation discovered at merge time cannot reach the model
  that reads the degradation list. That is a restructure and a real hole in the 29 August
  ruling, not a sweep item.
- The unnamed literals — entry multipliers, trend bands, `SPIKE_RATIO`, `window=30`,
  `0.0015`. Already ruled to get their own item and their own golden diff, because naming
  them means moving them to module level, which is a change to the decision path.
- `engine_version` as a static string — tangled with Kimi Finding 6; do them together.
- `code_hash`'s interpreter dependence, and the archive overwrite on a rerun after a code
  change. Both accepted and recorded.
- `test_pinned_source.py`'s LF-checkout failure, and GLM F-8/F-9. Test hygiene, which is
  the pass after this one — now with the line-ending argument from the document audit
  attached to it.

**Suggested split, Claude's call unless overruled:** three patches by class — the invented
defaults, the dead code, the false statements plus F-3 — because they need three different
golden predictions and only the first touches what the record contains.

**Followed, 7–8 September 2026 (Grok).** Three commits, exactly this split: `22afea2`,
`4d56f2a`, `c3b0d43`. Fourteen-item sweep complete; docs recorded at `029c510`, `e528475`,
`c56f969`.

## 6 September 2026 — the build scripts can write into the repository

Suite 406 → **412 passing, 0 failed**. No engine source file touched: `code_hash`
unchanged at `44e085cfa1fa…`, computed on both trees rather than assumed, and the golden
snapshot did not move. No live run owed.

### The count was wrong, and the model was already in the directory

The document audit said all ten `docs/build/build_*.py` hardcoded `/tmp/outputs/`. It was
**nine**. `build_audit_package.py` resolves its output from `__file__` at line 47 — and it
is the one whose three manifests verify byte-for-byte against their recorded build
commits, while every PDF beside them was carried across by hand. The fix did not need
designing; it needed extracting from the script that already had it.

Same shape as v1 of the suite-log patch saying "twelve files" when eleven wrote and the
twelfth deleted. Both were caught by recounting the evidence, neither by review.

### What changed

`docs/build/_output.py` — new. `REPO_ROOT` from `__file__`, `output_path(filename)`
returning a path inside `docs/`, `source_path(*parts)` for build inputs, and
`require_source(path, document, why)` which exits 2 with a message. `output_path` rejects
anything that is not a bare filename: absolute, containing a separator, or carrying a
drive letter. A build script no longer has a path of its own to get wrong, which is rule
28 rather than an instruction to be careful.

The nine import it. Seven now write their PDF into `docs/`.
`build_findings_bundle.py` and `build_remediation_plan.py` also point their source at the
repository and call `require_source`, so they stop before doing any work and say the
material has never been here — instead of a bare `FileNotFoundError` from inside reportlab
setup naming a directory in `/tmp` on a machine where nothing is wrong.

`docs/build/README.md` no longer says "change it to wherever you want the PDF". That
sentence was the instruction rule 28 exists to replace.

`tests/test_docs_build_writes_into_the_repository.py` — new, 6 tests.

### Evidence against pre-fix code

The new test file, run against a pristine `90225a4`: **5 failed, 1 passed**, and the split
matters.

Two are behavioural and are the defect executed: the scan finds **eleven absolute
assignments across nine files**, and **none of the nine** takes its output from a shared
resolver. Three fail because `docs/build/_output.py` does not exist on that tree — that
proves the module is new and nothing else, and is not evidence about anything. The sixth
is the negative control, which passes on both trees by design: it feeds the scanner the
pre-fix line as a string and requires it to report it.

### Verified rather than asserted

- All nine run from the repository root, and one also from inside `docs/build/`: seven
  exit 0 having written into `docs/`, two exit 2. **The same output path from either
  working directory** — which is the reason the resolver reads `__file__` and not
  `os.getcwd()`.
- The rebuilt Engineering Notes and Roadmap **extract text identical** to the committed
  PDFs — 63 and 15 pages, same SHA-256 over the extracted text. Repointing is faithful; a
  rebuild is the same document, not a new one.
- The rebuilt PDFs are deliberately **not in this commit**. Their content is unchanged and
  only the creation timestamp inside the file would move.

### Figures

| | before | after |
|---|---|---|
| pytest, `pandas_ta` installed | 406 / 0 | **412 passed, 0 failed** |
| pytest, `pandas_ta` absent | 292 / 103 skipped | **298 passed, 103 skipped** |
| `run_tests.py` (no pytest) | 339 / 0 / 29 | **345 passed, 0 failed, 29 errors** |

Error count unchanged at 29: all six new tests take no fixtures, deliberately, and none
needs `pandas_ta`.

### Which platform this is evidence about

**Linux.** The seven-of-nine build result is a Linux result and nothing here makes it a
Windows one.

What is platform-neutral by construction rather than by luck: the filename check reads the
string itself instead of asking `os.path.isabs` alone, so `C:\outputs\x.pdf` is rejected
identically on both platforms — `isabs` answers False for it on Linux and True on Windows,
which is exactly how the log-directory guard came out green in a sandbox and failed on
Viktor's machine. The `__file__` resolution and the AST scan cannot come out differently
either.

Not verified on Windows: that reportlab renders these documents there. reportlab was
installed on Viktor's machine on 6 September; the first Windows evidence will be the first
Notes rebuild.

### The guard that should have caught this excludes the directory it happened in

`test_explicit_configuration.py`'s `test_no_module_hardcodes_a_path_config_declares` scans
with `all_python_files(include_doc_tooling=False)`, so `docs/` is outside it by
construction. The stated reason for that flag (`tests/conftest.py`) is the dependency
manifest: counting reportlab as an engine dependency would make a fresh
`pip install -r requirements.txt` pull a PDF library the engine never uses, which is the
defect that test exists to catch pointed the other way. The reason is sound and it is
about imports. One flag answers two questions and answers the path-literal one wrongly.

Not changed here — narrowing it touches a test whose subject is the engine's dependency
manifest, and the new file asks the path question about `docs/build/` directly. Recorded
as a candidate, alongside the same-shaped candidate from the suite-log fix.

### Not fixed, and why

- **The eight Engineering Notes entries are still owed.** They are content inside
  `build_engineering_notes.py`. This patch makes publishing them one command; writing them
  is writing.
- **The two documents that cannot be built still cannot be built.** Their source material
  has never been in this repository. They now fail early and say so.
- **`README.md` and `docs/build/README.md` still cite `docs/Phase7_Audit_Findings_Complete.pdf`**,
  which does not exist and cannot be produced from here. Whether the reference goes or the
  source material is restored is a decision this patch does not take.
- **reportlab stays out of `requirements.txt`**, deliberately. `docs/build/README.md`
  carries its own install line and that is the intended arrangement.
- **The nine scripts still execute at module scope with no `main()`.** Untouched; it is
  not what was wrong with them.

## 6 September 2026 — Engineering Notes entries #83-90 published

**What changed.** `docs/build/build_engineering_notes.py` gains eight entries, #83-90, and
a new Document History row (v1.23). This is the item "Open — work" 3 above tracked as
growing at every handover for three sessions; it is now closed rather than carried
forward. Each entry is drawn only from the corresponding write-up already in this file —
the Section 11 confirmation run, the Finding 1 fix, GLM F-7 as extended, Kimi Finding 5
item 6, Kimi Finding 3, the fix for the suite destroying the decision record, the document
audit, and the build-scripts-can-write-into-the-repository fix itself — matched to the
builder's existing entries for format, tag vocabulary, and tone. No fact in the new
entries was invented; commit hashes, suite figures, line numbers, and panel output are
copied from the record above, not re-derived. Landed at commit `cdf9025`, pushed the same
session.

**Verified rather than asserted.** The diff is purely additive: 330 insertions, 0
deletions, one file. Confirmed by diffing the text of pages 1-57 of a PDF built from the
pre-change script against the same pages from the post-change script — byte-identical, the
first difference exactly at page 58, where Entry #83 begins. `code_hash` was computed, not
assumed, on three separate trees — the pristine pre-change tree, the hand-verified applied
tree, and a third, independently cloned-and-patched tree — all three
`44e085cfa1fa0b5bb48ccd7a917b3f8db578619dc39d1386d333dcd3d9c49994`, matching the value the
head block already carried, because `core/code_fingerprint.py` excludes `docs/` by
directory. The golden snapshot was not touched — no test or engine file is in this diff.
The suite was checked on the independently patched clone, not only the working copy: 412
passed / 0 failed with `pandas_ta`; 298 passed / 103 skipped without it; `run_tests.py` 345
passed / 0 failed / 29 errors, the error count unmoved.

**Which platform this is evidence about.** Linux — the sandbox where the patch was built
and verified. The built PDF grows from 63 to 72 pages; that page count and the diff above
are both Linux results. Windows evidence followed separately: Viktor rebuilt the PDF on
his own machine after applying the patch, and it rendered — the first confirmation that
reportlab handles this builder's full output, old and new entries together, outside the
sandbox. Nothing about the new entries uses a construct absent from the older ones (no
Unicode sub/superscripts, no new fonts, no table shape beyond the existing history table),
which was the structural argument made before the Windows run; it is now also an
observation, not only an argument.

**Not fixed, or not owed by this patch.** None of the eight open decisions is touched. The
semantic half of the document audit (the eight PDFs read against current state) and the
fourteen-item sweep are both still open — this was Claude's own recommended first of the
three pieces of work, and Viktor's instruction was "you decide," not a ruling on the order
itself. No engine or decision-path file was touched, so no live run is owed for this patch.

## 18 September 2026 — PHASE7_NEXT.md as it stood at `742b514`

*Moved here verbatim on 19 September 2026, when PHASE7_NEXT.md was rewritten for that
session. Every line below the rule is the file's content at `742b514`, unchanged —
including its own "this session" wording, which refers to 18 September. Its headings are
demoted one level (`#` → `##`, `##` → `###`) so they nest under this entry; no other
character is changed.*

---

## Next step — read this first

*18 September 2026 — this file rewritten as the project's current-state entry point,
replacing its previous role as a single chronological file. Standing rules, ratified
specifications and rulings that remain in force now live in
docs/PHASE7_DECISIONS.md. The dated narrative record of how the project got here —
the head-block archive and every dated session's own account of what it found and
did — now lives in docs/PHASE7_HISTORY.md. This file states only what is true right
now and what to do next; it is rewritten each session, not appended to. If you are
looking for what happened on a specific date, in a specific audit round, or why a
past patch did what it did, that is in HISTORY, not here.*

### PACE FIRST — read this before the rest of this file

Viktor judged, on his own, that 226 commits across 22 days had become hasty, and
ruled to slow down considerably (15 September 2026). **Do not open a session by
proposing work from "Open items" below, and do not treat it as a queue to clear.**
Ask what he wants to do first.

### Where things stand, right now

- **Tip:** `e2c6637`. **Tag:** `portfolio-v1` at `99e022e`. **Release gate:** open,
  declared 15 September 2026 — see docs/PHASE7_DECISIONS.md, "Two goals, and the
  order they finish in."
- **code_hash:** `bb47ab537314953e16b2db2fcf24003ead64eb5538a30221a6578d518bb7d34d`
  — moved from `5080ccf0490502ad72dadaf6c3c525d19792139ea52d7fb15ee28a923ab5d189`
  (unmoved since 18 September) by this session's patch (`f24a6e9`), which touched
  one engine file's fingerprint, `indicators/trend_health.py`. `models/bias_engine.py`
  and `models/risk_model.py` were also edited but comment-only — confirmed
  programmatically that neither file's per-file fingerprint moved, since
  `core/code_fingerprint.py` hashes the docstring-stripped parse tree and plain `#`
  comments were never part of what it dumps. The session's second patch
  (`e2c6637`) did not move it again and was not expected to: its only code edit
  was another comment block in `models/bias_engine.py`, and `tests/` is outside
  the fingerprint entirely. Confirmed by recomputation on the built tree, not
  assumed from the rule.
- **Test suite, at `e2c6637`:** 476 passed (pandas_ta, Viktor's Windows run) /
  344 passed, 120 skipped (without pandas_ta, sandbox) / 404 passed, 32
  pre-existing errors (`run_tests.py`, sandbox — the same 32 by name as the
  standing baseline, diffed programmatically rather than counted). The two tests
  added by `e2c6637` account for the rise from 474. Sandbox figures carry one
  extra failure that Windows does not — see the correction immediately below,
  which is now a standing platform difference rather than a one-off.
- **CORRECTION, made later the same day.** The line above previously read
  "Confirmed on BOTH the Linux sandbox and Viktor's own Windows machine — he ran
  all three configurations himself before committing and every count matched."
  That was false and it was Claude's error. The counts do not match: on a Linux
  checkout `tests/test_pinned_source.py::test_manifest_hashes_match_the_files`
  fails, so the sandbox figure is 473 passed / 1 failed where Windows reports 474
  passed / 0 failed. Verified by running the full suite on an untouched clone of
  `2fee78f`, not inferred. The cause is not a defect in the engine: the pinned
  CSVs are covered by `.gitattributes`'s `* text=auto`, so git stores them LF and
  checks them out CRLF on Windows, while `MANIFEST.json` holds sha256 hashes of
  the raw bytes — which therefore only match on the platform the manifest was
  generated on. The test is green for Viktor and red for every Linux or macOS
  checkout, including any future CI. See "Open items" for the fix, which has not
  been taken. Every sandbox figure in this document is reported with that one
  failure included rather than quietly subtracted.
- **Golden snapshot:** applicable this session — the patch touched engine code
  reachable on the golden fixture's path (ADX 31.96 at the decision bar fed
  `continuation_strength`'s now-removed component). Moved in exactly 16 leaf
  fields, all causally downstream of `bias.score` — diffed old vs new
  programmatically at leaf granularity. Full field list: `f24a6e9`'s commit
  message. `e2c6637` did not touch it: that patch changed one comment block, one
  test file and two documents, so `tests/fixtures/golden_decision.json` is not in
  its diff at all and `test_golden_path` passed unchanged.
- **Handover check:** not run as a script this session — this session has no shell
  access to Viktor's machine, only the device-file bridge, so it was approximated
  from `git status --short`, read twice around the commit rather than run as
  `session_handover_check.py`. One open item came out of that reading — see "Open
  items" below — everything else was clean: no other untracked or modified files,
  no loose delivery files (the patch and commit-message files are gitignored and
  were deleted after commit regardless), nothing staged uncommitted.

### The course correction — Goal B is on the slow burner

Decided 15 September 2026. Full reasoning: docs/PHASE7_DECISIONS.md, under "Goal B —
the backtesting phase, specified before it starts," in the subsection "Course
correction — the engine review, before any Goal B work." In short: before any Goal B
implementation, the engine gets reviewed for logical soundness — is the decision
logic coherent, are the constants justified, are the signals actually independent, is
the thesis written down anywhere. Goal B's full specification stands, ratified and
unchanged; it is deferred, not cancelled.

One finding from that eventual review was pulled forward and fixed this session,
narrowly, ahead of the review being scoped — see "Resolved this session" below. The
review itself, its completion boundary, and everything else it would cover remain
exactly as unscoped as before this session's fix.

### Resolved this session

- **Bias-weight independence — one finding, fixed narrowly by Viktor's own choice.**
  Asked directly whether the six bias weights are defensible, and to write a
  position on it first rather than have it handed back for scoping. Found that
  `trend_health` (weight 0.30) and `reversal_continuation` (weight 0.10) — 40% of
  `bias_score`'s blend — both read the same raw `adx_val` and score it on two
  different monotonic curves: not Item 11's defect (a reused *computed value*), a
  reused raw *input*, which is why it passed Item 11's audit and six subsequent
  rounds. Given a three-way choice — fix independence only, write a reasoned
  rationale for the weight magnitudes, or both — Viktor chose independence only.
  `indicators/trend_health.py`'s `continuation_strength` no longer has an ADX
  component; its ceiling honestly drops from 60 to 35, not rescaled back up, the
  same standard the original Item 11 fix used. `models/risk_model.py`'s own,
  separate read of raw ADX for the risk-regime gate was already independent of
  `bias_score` and needed no code change, only a comment correction. Full
  reasoning, what was deliberately left out of scope, and full verification detail:
  docs/PHASE7_DECISIONS.md, "First engine-review finding, fixed — bias-weight
  independence," and `f24a6e9`'s commit message.
- **The patch-delivery process itself changed.** Delivering that patch, `git add -A`
  swept an untracked file (`Claude outputs/Phase7_Session_Handover_2026-09-15.pdf`)
  toward staging — caught only by reading `git status --short` before committing,
  which is a carefulness step, not a structural one. The patch-delivery skill was
  updated (proposed to Viktor for review, not yet confirmed saved) to add files by
  name instead of `git add -A` on his real repo going forward, so an unrelated
  untracked file cannot be staged regardless of what else is sitting in the repo at
  commit time.

- **The independence review's second pass — the finding that closes the
  question Viktor actually asked.** The first pass fixed one shared raw input and
  left four of the six factors untraced. Tracing them found that trend health
  (0.30), structure regime (0.20), SuperTrend direction (0.15) and macro bias
  (0.10) — three quarters of the blend — are four different transforms of one
  measurement, the recent direction of `close`. Not the ADX defect repeated; the
  four genuinely disagree at turning points. But they agree by construction in any
  sustained trend, and `bias_score` presents that agreement as four independent
  confirmations. Recorded, deliberately not fixed: acting on it means reweighting
  or dropping factors, which is a trading judgment nothing here can evaluate until
  backtesting is unblocked. Two errors in the project's own record were corrected
  in the same patch — `bias_engine.py`'s false "swing-based" description of
  structure regime, and Claude's false claim that this session's Linux and Windows
  test counts matched. Full reasoning: docs/PHASE7_DECISIONS.md, "Second
  engine-review finding, recorded not fixed," and `e2c6637`'s commit message.

### Open items

- **The weight magnitudes themselves — 0.30/0.20/0.15/0.15/0.10/0.10 — remain
  unreviewed hand-picked judgment calls.** `Phase7_Roadmap.pdf` says so in its own
  words; nothing in the repository gives a reason for the specific split. Explicitly
  out of scope for this session's fix, by Viktor's choice, not an oversight. Writing
  down the market thesis the engine review's own scope conditions ask for is still
  undone too.
- **The four unchecked factors have now been traced, and the finding is open for
  Viktor's decision.** Four of the six factors — trend health (0.30), structure
  regime (0.20), SuperTrend direction (0.15), macro bias (0.10), three quarters of
  the blend — are four different transforms of one measurement: the recent direction
  of `close`. They will disagree at turning points but agree by construction in any
  sustained trend, and `bias_score` presents that agreement as four independent
  confirmations. Recorded rather than fixed, because acting on it means reweighting
  or dropping factors, which is a trading judgment this project cannot evaluate until
  backtesting is unblocked. Full reasoning: docs/PHASE7_DECISIONS.md, "Second
  engine-review finding, recorded not fixed."
- **The earlier claim that structure_regime had been checked was based on a false
  description and is withdrawn.** `models/bias_engine.py` described it as
  "structure.py's swing-based regime label"; it is actually a 5-bar vs 15-bar
  close-mean gap, and `swing_struct` reaches nothing but the panel. The check was run
  against a mechanism the factor does not use. The description is corrected and the
  real behaviour is now pinned by a test.
- **RSI still reaches `bias_score` through two factors,** and the written exemption
  for it is narrower than its prose claims — measured r = 0.83 in uptrends against
  r = 0.37 in downtrends. Worth at most 1.5 points of `bias_score`. Recorded, not
  fixed, for the same reason as above.
- **`test_pinned_source.py::test_manifest_hashes_match_the_files` is not portable
  and needs a decision.** It hashes the raw bytes of CSVs that `* text=auto` causes
  git to check out differently per platform, so it passes only on the OS that
  generated `MANIFEST.json`. The clean fix is to hash line-ending-normalised content
  in both `docs/build/make_pinned.py` and the test, then regenerate the manifest —
  three files, no engine change, works on Windows immediately. Not taken here to keep
  this patch to one subject.
- **The engine review itself still has no completion boundary and is still not
  formally scoped** — unchanged from before this session; see "The course
  correction" above.
- **An untracked file needs a decision.**
  `Claude outputs/Phase7_Session_Handover_2026-09-15.pdf` was sitting untracked in
  the repo when this session's patch was delivered, got caught mid-`git add -A`
  before it could ride into the commit, and was left exactly where it was —
  neither committed, deleted, nor explained. Whether it belongs in git (like the
  other dated handover documents already tracked in `Claude outputs/`) or was never
  meant to be there is Viktor's call, not made this session.
- **The Constitution's backtest-start condition** (Items 2, 3, 6, 18) has never been
  formally declared met the way the release gate was. Unchanged from before this
  session. Deferred behind the course correction above.
- **The seven test files that cite `docs/PHASE7_NEXT.md` by name** in a docstring or
  comment (`test_frame_ownership.py`, `test_imports.py`, `test_lineage.py`,
  `test_risk_regime_independence.py`, `test_router_no_fabricated_zero_defaults.py`,
  `test_decision_bar_integrity.py`, `test_exit_model_removal.py`), and the same
  citation inside `docs/build/build_engineering_notes.py`, `build_portfolio_document.py`
  and `build_ai_attribution.py` — unchanged from before this session, still stale,
  still not fixed (scope was this session's independence finding, not a
  repository-wide citation sweep).
- **Engineering Notes are eight commits stale** — `bd44b98`, `f9e5127`,
  `dff7d00`, `4a97c32`, `5be5d82`, `f24a6e9`, `2fee78f`, `e2c6637` — last
  regenerated through Entry #127 (v1.30).
  Known and deliberate per the batching rule (docs/PHASE7_DECISIONS.md, "Working
  practice"); stated explicitly rather than left implicit.
- **Unrelated, not urgent:** confirm which YH programme permits AI-assisted
  examensarbete work.

## 19 September 2026 — PHASE7_NEXT.md as it stood at `5c73e24`

*Moved here verbatim on 20 September 2026, when PHASE7_NEXT.md was rewritten for that
session. Every line below the rule is the file's content at `5c73e24` (unchanged at
`c7ced36`), unchanged — including its own "this session" wording, which refers to
19 September. Its headings are demoted one level (`#` → `##`, `##` → `###`) so they
nest under this entry; no other character is changed.*

---

## Next step — read this first

*19 September 2026. This file is the project's current-state entry point: it states only
what is true right now and what to do next, and is rewritten each session, not appended
to. Standing rules, ratified specifications and rulings in force live in
docs/PHASE7_DECISIONS.md. The dated record — including this file's previous version,
moved there verbatim this session — lives in docs/PHASE7_HISTORY.md.*

### PACE FIRST — read this before the rest of this file

Viktor judged, on his own, that 226 commits across 22 days had become hasty, and
ruled to slow down considerably (15 September 2026). **Do not open a session by
proposing work from "Open items" below, and do not treat it as a queue to clear.**
Ask what he wants to do first.

### Where things stand, right now

- **Tip:** current as of `2f5fdaa`; the actual tip is the docs commit that wrote this
  file (a commit cannot name its own hash). **Tag:** `portfolio-v1` at `99e022e`.
  **Release gate:** open, declared 15 September 2026 — see docs/PHASE7_DECISIONS.md,
  "Two goals, and the order they finish in."
- **code_hash:** `bb47ab537314953e16b2db2fcf24003ead64eb5538a30221a6578d518bb7d34d` —
  unmoved by `2f5fdaa`. Recomputed on the pre- and post-patch trees, not assumed:
  `core/code_fingerprint.py` walks `.py` files only, and the patch added no engine file.
- **Golden snapshot:** untouched by `2f5fdaa` (no engine code in the diff;
  `test_golden_path` passed).
- **Test suite, at `2f5fdaa`:**
  - Windows (Viktor's machine, pandas_ta): expected 485 passed / 0 failed. He was told to
    stop at that step on any other count and proceeded; the output itself was not pasted
    into the session, so this is his confirmation by proceeding, not a count Claude read.
  - Linux sandbox, clone made with `core.autocrlf=true` (the patch-delivery skill's
    setup, so the CSVs check out CRLF as on Windows): 485 passed / 0 failed with
    pandas_ta; 354 passed / 120 skipped without it; `run_tests.py` 414 passed / 0 failed
    / 32 errors — the same 32 by name as the standing baseline, diffed programmatically.
  - **Standing platform difference:** on a default LF Linux or macOS checkout,
    `tests/test_pinned_source.py::test_manifest_hashes_match_the_files` fails, because
    `.gitattributes`'s `* text=auto` changes the pinned CSVs' bytes per platform while
    `MANIFEST.json` pins raw-byte hashes. Measured at `742b514` on a fresh default clone:
    475 passed / 1 failed. At `2f5fdaa` the prediction is 484 / 1 — **not measured**,
    because that patch is built against the CRLF tree and does not apply to an LF
    checkout. Every sandbox figure is reported with this failure included, never quietly
    subtracted. The fix is still an open item below.
- **Handover check:** ran for real on Viktor's Windows machine as the pre-push hook's
  first run, on the push of `2f5fdaa` — every section clean, `SUMMARY: clean`, 30
  ignored routine-noise entries filtered, section 6 "installed". That is also the first
  Windows evidence that the hook runs at all. This session had file access to his
  machine but no shell, so no other run of the script on his machine was possible.

### Resolved this session

- **The pre-push hook, built and landed at `2f5fdaa`.** Proposed in the 18 September
  session, never built, and missing from the previous Open items — Viktor raised it at
  the start of this session as the one concrete follow-up outstanding.
  `githooks/pre-push` runs `docs/build/session_handover_check.py` on every `git push`;
  a finding stops the push. Viktor's ruling (option A of three): stop, consult with
  Claude, and override with `git push --no-verify` if the answer is push. He first asked
  for "only warn"; Claude pointed out a warning cannot also let him decide "push or not",
  because the push would already have gone. Fails closed if the check cannot run.
  Ruling and reasoning: docs/PHASE7_DECISIONS.md, handover checklist item 9 and the
  ruling beneath it. Full verification, wrong turns and predictions: `2f5fdaa`'s commit
  message.
- **Two things verification found, both recorded in that commit message:** a single
  `git apply` of a patch that adds a `.gitattributes` rule and a new file together
  writes the new file under the *old* attributes (the hook came out CRLF on an
  autocrlf clone), so the delivery applied `.gitattributes` first as its own step; and
  on Linux git 2.43 a hook that cannot be executed at all makes `git push` hang rather
  than fail, so the push tests carry a timeout.
- **Previous version of this file moved to HISTORY verbatim.** The 18 September
  session's account existed only here — HISTORY had not been appended to since the
  split — so it was moved whole before this rewrite, not summarised.

### The course correction — Goal B is on the slow burner

Decided 15 September 2026. Full reasoning: docs/PHASE7_DECISIONS.md, under "Goal B —
the backtesting phase, specified before it starts," in the subsection "Course
correction — the engine review, before any Goal B work." In short: before any Goal B
implementation, the engine gets reviewed for logical soundness — is the decision
logic coherent, are the constants justified, are the signals actually independent, is
the thesis written down anywhere. Goal B's full specification stands, ratified and
unchanged; it is deferred, not cancelled.

One finding from that eventual review was pulled forward and fixed on 18 September,
narrowly, ahead of the review being scoped, and a second was recorded but not fixed —
see docs/PHASE7_HISTORY.md, "18 September 2026 — PHASE7_NEXT.md as it stood at
`742b514`." The review itself, its completion boundary, and everything else it would
cover remain exactly as unscoped as before.

### Open items

- **The weight magnitudes themselves — 0.30/0.20/0.15/0.15/0.10/0.10 — remain
  unreviewed hand-picked judgment calls.** `Phase7_Roadmap.pdf` says so in its own
  words; nothing in the repository gives a reason for the specific split. Explicitly
  out of scope for the 18 September fix, by Viktor's choice, not an oversight. Writing
  down the market thesis the engine review's own scope conditions ask for is still
  undone too.
- **The four unchecked factors have now been traced, and the finding is open for
  Viktor's decision.** Four of the six factors — trend health (0.30), structure
  regime (0.20), SuperTrend direction (0.15), macro bias (0.10), three quarters of
  the blend — are four different transforms of one measurement: the recent direction
  of `close`. They will disagree at turning points but agree by construction in any
  sustained trend, and `bias_score` presents that agreement as four independent
  confirmations. Recorded rather than fixed, because acting on it means reweighting
  or dropping factors, which is a trading judgment this project cannot evaluate until
  backtesting is unblocked. Full reasoning: docs/PHASE7_DECISIONS.md, "Second
  engine-review finding, recorded not fixed."
- **The earlier claim that structure_regime had been checked was based on a false
  description and is withdrawn.** `models/bias_engine.py` described it as
  "structure.py's swing-based regime label"; it is actually a 5-bar vs 15-bar
  close-mean gap, and `swing_struct` reaches nothing but the panel. The check was run
  against a mechanism the factor does not use. The description is corrected and the
  real behaviour is now pinned by a test.
- **RSI still reaches `bias_score` through two factors,** and the written exemption
  for it is narrower than its prose claims — measured r = 0.83 in uptrends against
  r = 0.37 in downtrends. Worth at most 1.5 points of `bias_score`. Recorded, not
  fixed, for the same reason as above.
- **`test_pinned_source.py::test_manifest_hashes_match_the_files` is not portable
  and needs a decision.** It hashes the raw bytes of CSVs that `* text=auto` causes
  git to check out differently per platform, so it passes only on the OS that
  generated `MANIFEST.json`. The clean fix is to hash line-ending-normalised content
  in both `docs/build/make_pinned.py` and the test, then regenerate the manifest —
  three files, no engine change, works on Windows immediately. Not taken on 18 September
  (to keep that patch to one subject) nor on 19 September (not requested).
- **The pre-push hook is installed per clone, not per repository.**
  `git config core.hooksPath githooks` lives in `.git/config`, which a fresh clone does
  not carry. `session_handover_check.py` section 6 now flags a clone without it, so a
  missing hook is visible at every hand-run of the check — but nothing can make it
  impossible. After any re-clone (including after a machine wipe), run that one command.
- **The engine review itself still has no completion boundary and is still not
  formally scoped** — unchanged since 15 September; see "The course correction"
  above.
- **The untracked handover PDF is gone from disk; what happened to it is unrecorded.**
  `Claude outputs/Phase7_Session_Handover_2026-09-15.pdf` was never committed (checked:
  `git log --all` on that path is empty) and was no longer in `Claude outputs/` on
  Viktor's disk on 19 September (checked by directory listing over the device bridge).
  Whether he deleted it deliberately or moved it elsewhere is not known to Claude — one
  line from him closes this item.
- **The Constitution's backtest-start condition** (Items 2, 3, 6, 18) has never been
  formally declared met the way the release gate was. Unchanged. Deferred behind the
  course correction above.
- **The seven test files that cite `docs/PHASE7_NEXT.md` by name** in a docstring or
  comment (`test_frame_ownership.py`, `test_imports.py`, `test_lineage.py`,
  `test_risk_regime_independence.py`, `test_router_no_fabricated_zero_defaults.py`,
  `test_decision_bar_integrity.py`, `test_exit_model_removal.py`), and the same
  citation inside `docs/build/build_engineering_notes.py`, `build_portfolio_document.py`
  and `build_ai_attribution.py` — still stale, still not fixed (the 18 September scope
  was the independence finding, and 19 September's was the pre-push hook — neither a
  repository-wide citation sweep).
- **Engineering Notes are ten commits stale** at `2f5fdaa` — `bd44b98`, `f9e5127`,
  `dff7d00`, `4a97c32`, `5be5d82`, `f24a6e9`, `2fee78f`, `e2c6637`, `742b514`,
  `2f5fdaa` — last regenerated through Entry #127 (v1.30), and this docs commit makes
  eleven. Known and deliberate per the batching rule (docs/PHASE7_DECISIONS.md,
  "Working practice"); stated explicitly rather than left implicit. The batching rule's
  own trigger ("once several commits have landed") has arguably been met for a while —
  whether to regenerate now is Viktor's call.
- **Unrelated, not urgent:** confirm which YH programme permits AI-assisted
  examensarbete work.


## 19 September 2026 (evening) — PHASE7_NEXT.md as it stood at `e115272`

*Moved here verbatim on 20 September 2026, when PHASE7_NEXT.md was rewritten for that
session. Every line below the rule is the file's content at `e115272` (first written at
`e431714`), unchanged — including its own "this session" wording. Its headings are
demoted one level (`#` → `##`, `##` → `###`) so they nest under this entry; no other
character is changed.*

*Its dating, corrected here rather than in the text below: the file is headed
"20 September 2026", and the entry above this one says it was moved "on 20 September
2026". Both are a day ahead. `e431714` and `e115272`, the commits that wrote them, are
dated 19 September 2026 (18:30 and 20:41 +0200, from `git log`); that was the second
session on 19 September, after the one that wrote `5c73e24` at 04:34. The text is left
as it was, because this file is append-only.*

---

## Next step — read this first

*20 September 2026. This file is the project's current-state entry point: it states only
what is true right now and what to do next, and is rewritten each session, not appended
to. Standing rules, ratified specifications and rulings in force live in
docs/PHASE7_DECISIONS.md. The dated record — including this file's previous version,
moved there verbatim this session — lives in docs/PHASE7_HISTORY.md.*

### PACE FIRST — read this before the rest of this file

Viktor judged, on his own, that 226 commits across 22 days had become hasty, and
ruled to slow down considerably (15 September 2026). **Do not open a session by
proposing work from "Open items" below, and do not treat it as a queue to clear.**
Ask what he wants to do first.

### Where things stand, right now

- **Tip:** current as of `e431714`; the actual tip is the docs commit that wrote this
  file (a commit cannot name its own hash). **Tag:** `portfolio-v1` at `99e022e`.
  **Release gate:** open, declared 15 September 2026 — see docs/PHASE7_DECISIONS.md,
  "Two goals, and the order they finish in."
- **code_hash:** `bb47ab537314953e16b2db2fcf24003ead64eb5538a30221a6578d518bb7d34d` —
  unmoved by `5c73e24`, `c7ced36`, `e431714` and this commit (all docs-only). For
  `e431714` and this commit it was recomputed on the pre- and post-patch trees, not
  assumed.
- **Golden snapshot:** last changed at `f24a6e9` (checked with `git log` on the
  snapshot file); `code_hash` has been `bb47ab53…` since that commit, so no engine
  file has changed since either.
- **Test suite — engine code identical since `5c73e24`:**
  - Windows (Viktor's machine, pandas_ta): **485 passed / 0 failed at `5c73e24`, read
    from his pasted output.** At `c7ced36` and `e431714`, 485 / 0 is his confirmation by
    proceeding (told to stop on any other count; output not pasted).
  - Linux sandbox, clone made with `core.autocrlf=true` (CSVs check out CRLF, as on
    Windows): 485 passed / 0 failed with pandas_ta; 354 passed / 120 skipped without
    it; `run_tests.py` 414 passed / 0 failed / 32 errors — the same 32 by name as the
    standing baseline.
  - **Standing platform difference:** a default LF Linux or macOS checkout gives
    484 / 1 — `tests/test_pinned_source.py::test_manifest_hashes_match_the_files`,
    because `.gitattributes`'s `* text=auto` changes the pinned CSVs' bytes per platform
    while `MANIFEST.json` pins raw-byte hashes. Always reported, never quietly
    subtracted. The fix is an open item below.
- **Engineering Notes:** current. Regenerated at `c7ced36` through Entry #135 (v1.31) —
  eight entries, #128–#135, covering all eleven commits `bd44b98`..`5c73e24`.
  `c7ced36`, `e431714` and this commit are not yet covered; all three are docs-only.
- **Handover check / pre-push hook:** ran on the pushes of `c7ced36` and `e431714`,
  `SUMMARY: clean` both times.

### Resolved since the previous version of this file

- **`c7ced36` — Engineering Notes regenerated through Entry #135 (v1.31), docs-only.**
  Viktor's three rulings: regenerate now rather than batch later; give the course
  correction (#129) and the `git add -A` incident (#133) entries of their own rather
  than folding them into neighbours; and record the Windows 485 in the repo's own
  wording, "confirmation by proceeding." The `code_hash` chain was recomputed per
  commit for those entries, not assumed: `38458f20…` from `portfolio-v1` through
  `4a97c32`, `5080ccf0…` at `5be5d82`, `bb47ab53…` at `f24a6e9` and every commit since.
- **Engineering Notes staleness — closed** by `c7ced36`.
- **The untracked handover PDF — closed.** Viktor moved
  `Phase7_Session_Handover_2026-09-15.pdf` out of `Claude outputs/` to his project
  folder outside the repository (`D:\Phase_7_Engine_Random_Files`), where it now exists
  as two copies. That they are byte-identical was checked on 19 September; on
  20 September only their names and equal sizes (17,189 bytes) were re-checked, by
  directory listing over the device bridge.
- **The seven test files that cite `docs/PHASE7_NEXT.md` do not read it.** Checked by
  static search only: none of them opens the file; the citations are in docstrings and
  comments. A dynamically built path would not show up in that search. The citations
  themselves are still stale — see Open items.
- **README.md checked against this file, at `e431714`.** Fifteen commits behind before
  it (last touched at `ebb0a46`, 15 September). Two things were actually stale and are
  fixed: both test-count statements (466 / 338 + 117 skipped / `run_tests.py` 395 → the
  current 485 / 354 + 120 skipped / 414), and the repository-layout tree, which lacked
  `githooks/` (added at `2f5fdaa`). Found and deliberately **not** changed, because they
  predate the fifteen commits and are omissions rather than staleness: the layout tree
  also omits `Claude outputs/` and `decision_log_backups/`, and README does not point a
  reader at `docs/PHASE7_NEXT.md` / `PHASE7_DECISIONS.md` / `PHASE7_HISTORY.md` at all.
- **One wrong prediction in `e431714`'s delivery, recorded here because it happened
  after that commit's message was written.** Claude told Viktor that `git status
  --short` would list the two delivery files (`.patch`, `_commit_message.txt`) as
  `??`. They did not appear at all: `.gitignore` lines 106–107 ignore `*.patch` and
  `*_commit_message.txt`, and `--short` does not list ignored files. The prediction
  was made from memory, not checked; the patch-delivery skill's own wording
  ("confirm the delivery files are absent") was right. No harm — the files were
  ignored, not missing — but it is the unchecked-claim shape of the 3 September
  lesson, and an incomplete prediction weakens the stop-on-unpredicted-output rule.

### The course correction — Goal B is on the slow burner

Decided 15 September 2026. Full reasoning: docs/PHASE7_DECISIONS.md, under "Goal B —
the backtesting phase, specified before it starts," in the subsection "Course
correction — the engine review, before any Goal B work." In short: before any Goal B
implementation, the engine gets reviewed for logical soundness — is the decision
logic coherent, are the constants justified, are the signals actually independent, is
the thesis written down anywhere. Goal B's full specification stands, ratified and
unchanged; it is deferred, not cancelled.

One finding from that eventual review was pulled forward and fixed on 18 September,
narrowly, ahead of the review being scoped, and a second was recorded but not fixed —
see docs/PHASE7_HISTORY.md, "18 September 2026 — PHASE7_NEXT.md as it stood at
`742b514`." The review itself, its completion boundary, and everything else it would
cover remain exactly as unscoped as before.

### Open items

Items marked **Viktor's call** are his to decide; he writes his position first and
Claude critiques it.

- **Viktor's call — the six bias-weight magnitudes and the engine's written thesis.**
  0.30/0.20/0.15/0.15/0.10/0.10 remain unreviewed hand-picked judgment calls;
  `Phase7_Roadmap.pdf` says so in its own words, and nothing in the repository gives a
  reason for the specific split. The market thesis the engine review's own scope
  conditions ask for is still unwritten.
- **Viktor's call — five points from the 15 September PDF, "A input and raised
  questions on the current output of the engine"** (kept outside the repository), none
  found in PHASE7_NEXT, DECISIONS or HISTORY by keyword search (not a full read):
  1. the +0.69R expected value treats the confidence score as if it were a win rate;
  2. volume may be counted three times;
  3. the +10.55 BTC confidence boost;
  4. whether macro ×0.90 is enough against the macro trend;
  5. what the "5.00" validation score is out of.
  The PDF's sixth point, the /102 denominator, is documented in code as deliberate.
  Whether these five go into the engine review's scope is his decision.
- **Viktor's call — retiring "To do list Claude Phase 7 Engine.pdf"** (outside the
  repository). It is stale: every "Immediate" item on it landed at `5be5d82` and
  `4a97c32`.
- **The four unchecked factors have been traced, and the finding is open for Viktor's
  decision.** Four of the six factors — trend health (0.30), structure regime (0.20),
  SuperTrend direction (0.15), macro bias (0.10), three quarters of the blend — are
  four different transforms of one measurement: the recent direction of `close`. They
  will disagree at turning points but agree by construction in any sustained trend,
  and `bias_score` presents that agreement as four independent confirmations. Recorded
  rather than fixed, because acting on it means reweighting or dropping factors, which
  is a trading judgment this project cannot evaluate until backtesting is unblocked.
  Full reasoning: docs/PHASE7_DECISIONS.md, "Second engine-review finding, recorded not
  fixed."
- **The earlier claim that structure_regime had been checked was based on a false
  description and is withdrawn** (18 September). `models/bias_engine.py` described it
  as "structure.py's swing-based regime label"; it is actually a 5-bar vs 15-bar
  close-mean gap, and `swing_struct` reaches nothing but the panel. The description is
  corrected and the real behaviour is pinned by a test.
- **RSI still reaches `bias_score` through two factors,** and the written exemption for
  it is narrower than its prose claims — measured r = 0.83 in uptrends against r = 0.37
  in downtrends. Worth at most 1.5 points of `bias_score`. Recorded, not fixed, for the
  same reason as the four-factor finding.
- **`test_pinned_source.py::test_manifest_hashes_match_the_files` is not portable and
  needs a decision.** It hashes the raw bytes of CSVs that `* text=auto` checks out
  differently per platform, so it passes only on the OS that generated `MANIFEST.json`.
  The clean fix is to hash line-ending-normalised content in both
  `docs/build/make_pinned.py` and the test, then regenerate the manifest — three files,
  no engine change. Not taken on 18, 19 or 20 September (not requested).
- **The pre-push hook is installed per clone, not per repository.**
  `git config core.hooksPath githooks` lives in `.git/config`, which a fresh clone does
  not carry. `session_handover_check.py` section 6 flags a clone without it. After any
  re-clone (including after a machine wipe), run that one command.
- **The engine review itself still has no completion boundary and is still not
  formally scoped** — unchanged since 15 September; see "The course correction" above.
- **The Constitution's backtest-start condition** (Items 2, 3, 6, 18) has never been
  formally declared met the way the release gate was. Unchanged. Deferred behind the
  course correction above.
- **Stale citations of `docs/PHASE7_NEXT.md`** in seven test files'
  docstrings/comments (`test_frame_ownership.py`, `test_imports.py`, `test_lineage.py`,
  `test_risk_regime_independence.py`, `test_router_no_fabricated_zero_defaults.py`,
  `test_decision_bar_integrity.py`, `test_exit_model_removal.py`) and inside
  `docs/build/build_engineering_notes.py`, `build_portfolio_document.py` and
  `build_ai_attribution.py`. They point at content that moved to DECISIONS or HISTORY
  in the 18 September split. Harmless to test behaviour (see Resolved above), not fixed.
- **README.md's pre-existing omissions** — `Claude outputs/` and
  `decision_log_backups/` absent from the layout tree; no pointer to the three
  PHASE7_* documents. Found on 20 September, left for a decision rather than widened
  into `e431714`.
- **Unrelated, not urgent:** confirm which YH programme permits AI-assisted
  examensarbete work.


## 20 September 2026 — PHASE7_NEXT.md as it stood at `16d3c1f`

*Moved here verbatim on 20 September 2026, when PHASE7_NEXT.md was rewritten at the close
of the next session. Every line below the rule is the file's content at `16d3c1f`,
unchanged — including its own "this session" wording. Its headings are demoted one level
(`#` → `##`, `##` → `###`) so they nest under this entry; no other character is changed.
That next session edited the file in place twice before this rewrite, at `9a35f1c` (item
9) and `077d120` (item 10); those two versions are in git, and what they added is carried
into the rewritten file.*

---

## Next step — read this first

*20 September 2026. This file is the project's current-state entry point: it states only
what is true right now and what to do next, and is rewritten each session, not appended
to. Standing rules, ratified specifications and rulings in force live in
docs/PHASE7_DECISIONS.md. The dated record — including this file's previous version,
moved there verbatim this session — lives in docs/PHASE7_HISTORY.md.*

### PACE FIRST — read this before the rest of this file

Viktor judged, on his own, that 226 commits across 22 days had become hasty, and
ruled to slow down considerably (15 September 2026). **Do not open a session by
proposing work from "Open items" below, and do not treat it as a queue to clear.**
Ask what he wants to do first.

### Ruled this session — the old list is scrapped; an independent audit is next

Viktor scrapped the seven judgment and review items that were open at `e115272` — the
bias-weight magnitudes and thesis, the five points from the 15 September PDF, the To-do
PDF, the four-factor finding, the RSI double path, the engine review's missing scope,
and the backtest-start declaration. Next is **a new audit by an independent model**;
before it, three mechanical items: the manifest test (done, `b68de08`), the stale
citations, and README's omissions. Full ruling, what it does and does not change, and
what is still undecided about the audit: docs/PHASE7_DECISIONS.md, "Ruling,
20 September 2026."

### Where things stand, right now

- **Tip:** current as of `b68de08`; the actual tip is the docs commit that wrote this
  file (a commit cannot name its own hash). **Tag:** `portfolio-v1` at `99e022e`.
  **Release gate:** open, declared 15 September 2026.
- **code_hash:** `bb47ab537314953e16b2db2fcf24003ead64eb5538a30221a6578d518bb7d34d` —
  unmoved by `b68de08` (recomputed on the pre-patch tree and on applied autocrlf and LF
  trees) and by this commit (docs-only; recomputed, not assumed). Unchanged since
  `f24a6e9`.
- **Golden snapshot:** last changed at `f24a6e9`; no engine file has changed since.
- **Test suite at `b68de08`** (engine code unchanged since `5c73e24`):
  - Windows (Viktor's machine, pandas_ta): 486 passed / 0 failed and `run_tests.py`
    415 / 0 / 32 — **confirmation by proceeding** (told to stop on any other count;
    output not pasted).
  - Linux sandbox, autocrlf clone: 486 / 0 with pandas_ta; 355 passed / 120 skipped
    without it; `run_tests.py` 415 passed / 0 failed / 32 errors, the same 32 by name as
    before.
  - Linux sandbox, **default LF clone: 486 / 0.** The standing platform difference
    (484 / 1 on LF checkouts) is closed by `b68de08`.
- **Engineering Notes:** through Entry #135 (v1.31), regenerated at `c7ced36`. Not yet
  covering `e431714`, `e115272` (both docs-only), `b68de08` (tests and tooling — the
  first non-docs commit since the last regeneration) or this commit. Batched per the
  standing rule; regeneration is due at the latest when 9 and 10 have landed.
- **Handover check / pre-push hook:** ran on the push of `b68de08`, `SUMMARY: clean`.
  GitHub's tip was then fetched into the sandbox: `b68de08`, the three files
  byte-identical to what was verified.

### Resolved since the previous version of this file

- **`b68de08` — the pinned-data manifest check is portable.** Manifest hashes are now
  over CRLF-normalised content, in both `make_pinned.py` and the test; the manifest was
  regenerated by the script itself (CSVs byte-identical); one new test,
  `test_manifest_hash_ignores_line_endings`, makes a revert to raw bytes fail on every
  platform. Full account in its commit message.
- **Where the six bias weights came from — traced in `git log`.** Unchanged in value
  since `83a9425` (26 August), which brought them in wholesale, replacing the first
  commits' four-term blend. No commit ever changed a weight value without a record;
  the original choice predates the repository, which is why no reason for it exists.
  Recorded in DECISIONS with the ruling above.
- **GitHub's tip checked by clone, not by assertion**, at the start of this session
  (`e115272`) and after the push (`b68de08`).
- **The previous version of this file was misdated.** It was headed "20 September";
  the commits that wrote it (`e431714`, `e115272`) are dated 19 September. Corrected
  in the note heading its HISTORY entry, not in the moved text, since HISTORY is
  append-only. This file's date (20 September) is from the session clock and matches
  `b68de08`'s commit date.

### Open items

Items marked **Viktor's call** are his to decide; he writes his position first and
Claude critiques it.

- **Stale citations of `docs/PHASE7_NEXT.md`** (next, Claude's work) in seven test
  files' docstrings/comments (`test_frame_ownership.py`, `test_imports.py`,
  `test_lineage.py`, `test_risk_regime_independence.py`,
  `test_router_no_fabricated_zero_defaults.py`, `test_decision_bar_integrity.py`,
  `test_exit_model_removal.py`) and in `docs/build/build_engineering_notes.py`,
  `build_portfolio_document.py` and `build_ai_attribution.py`. They point at content
  that moved to DECISIONS or HISTORY in the 18 September split. None of them opens the
  file (static search only).
- **README.md's pre-existing omissions** (after that, Claude's work) — `Claude outputs/`
  and `decision_log_backups/` absent from the layout tree; no pointer to the three
  PHASE7_* documents.
- **Viktor's call — planning the independent audit:** which model, the package (the
  standing default for a fresh Tier-1 audit is the full package), and whether the
  auditor sees the scrapped findings. Not started.
- **Viktor, outside the repository:** delete "To do list Claude Phase 7 Engine.pdf".
- **Not investigated:** in one `run_tests.py` run on the pre-patch tree, the sandbox's
  egress proxy reported one connection attempt to `api.mexc.com` (refused there). An
  earlier run of the same command on the same tree showed no such report, so it is not
  reliably reproduced; not caused by `b68de08`, whose tree was not yet built. Which
  test, if any, makes it is unknown. `b68de08`'s commit message says it was "present on
  the pre-patch tree too"; more exactly, it was seen once, only on the pre-patch tree,
  and not in the post-patch runs.
- **The pre-push hook is installed per clone, not per repository.** After any re-clone
  (including after a machine wipe), run `git config core.hooksPath githooks`;
  `session_handover_check.py` section 6 flags a clone without it.
- **Unrelated, not urgent:** confirm which YH programme permits AI-assisted
  examensarbete work.


## 20 September 2026 (later) — PHASE7_NEXT.md as it stood at `c745a67`

*Moved here verbatim on 20 September 2026, when PHASE7_NEXT.md was rewritten at the close
of the next session. Every line below the rule is the file's content at `c745a67`,
unchanged — including its own "this session" wording. Its headings are demoted one level
(`#` → `##`, `##` → `###`) so they nest under this entry; no other character is changed.*

---

## Next step — read this first

*20 September 2026. This file is the project's current-state entry point: it states only
what is true right now and what to do next, and is rewritten each session, not appended
to. Standing rules, ratified specifications and rulings in force live in
docs/PHASE7_DECISIONS.md. The dated record — including this file's previous version,
moved there verbatim this session — lives in docs/PHASE7_HISTORY.md. A citation of this
file written before the 18 September 2026 split — in the Engineering Notes, audit
reports, handovers or any other dated record — refers to content now in one of those
two files; dated records are not edited to say so (DECISIONS, "Ruling, 20 September
2026 — dated records are not edited to follow a move").*

### PACE FIRST — read this before the rest of this file

Viktor judged, on his own, that 226 commits across 22 days had become hasty, and
ruled to slow down considerably (15 September 2026). **Do not open a session by
proposing work from "Open items" below, and do not treat it as a queue to clear.**
Ask what he wants to do first.

### Where the project is

The three mechanical items Viktor ruled should come before the independent audit are
all done: the manifest test (`b68de08`), the stale citations (`9a35f1c`) and README's
omissions (`077d120`). The Engineering Notes and the two portfolio PDFs are current as of
this commit. **What comes next is planning the independent audit, and that is Viktor's
call** — which model, which package, and whether the auditor sees the findings scrapped
on 20 September (DECISIONS, "Ruling, 20 September 2026 — the open-items list scrapped;
an independent audit next").

### Ruled this session

- **Dated records are not edited to follow a move** (item 9). Viktor ruled that item 9
  covers every stale pointer a repository-wide search found, not just the ten files
  recorded, and — after first wanting the dated records edited too, "the aim was to
  keep a real record", and Claude arguing against — accepted a forward note instead:
  the sentence at the top of this file, plus the ruling in DECISIONS, "Ruling,
  20 September 2026 — dated records are not edited to follow a move". Claude read his
  reply ("we can ignore it this time if you want") as that ruling and said so before
  building.

### Where things stand, right now

- **Tip:** current as of `077d120`; the actual tip is the regeneration commit that wrote
  this file (a commit cannot name its own hash). **Tag:** `portfolio-v1` at `99e022e`.
  **Release gate:** open, declared 15 September 2026.
- **code_hash:** `bb47ab537314953e16b2db2fcf24003ead64eb5538a30221a6578d518bb7d34d` —
  unchanged since `f24a6e9`. Recomputed on the trees of all six commits since `c7ced36`
  (`e431714`, `e115272`, `b68de08`, `16d3c1f`, `9a35f1c`, `077d120`) for the Notes'
  v1.32, and on this commit's applied tree; not assumed.
- **Golden snapshot:** last changed at `f24a6e9`; no engine code has changed since.
- **Test suite**, unchanged since `b68de08`: 486 passed / 0 failed with pandas_ta;
  355 passed / 120 skipped without it; `run_tests.py` 415 / 0 / 32, the same 32 by name.
  Linux sandbox, autocrlf clone, applied tree, for each of this session's three commits.
  Windows at `9a35f1c` and `077d120`: **confirmation by proceeding** (Viktor went past
  the stop-on-difference steps and pasted `git status`). Windows at this commit: to be
  confirmed the same way.
- **Engineering Notes:** through Entry #140 (v1.32), regenerated in this commit; no gap.
  **Phase7_Portfolio_Document.pdf** and **Phase7_AI_Attribution.pdf** regenerated in the
  same commit; their text differs from the previous build only by `9a35f1c`'s pointer
  changes, compared word by word. The Notes script, run unchanged before the new entries
  were added, reproduced the committed PDF's text exactly.
- **Handover check / pre-push hook:** `SUMMARY: clean` on the pushes of `9a35f1c` and
  `077d120`. After each push GitHub's tip was fetched into the sandbox and every changed
  file compared byte for byte with what was verified.

### Resolved this session

- **Item 9 — stale citations of `docs/PHASE7_NEXT.md`, `9a35f1c`.** The recorded list
  of ten files was incomplete; the fix covers twenty-four. Live pointers now name the
  section of DECISIONS or HISTORY that holds the content; still-correct citations were
  left; dated records were not edited (ruling above). Two citations were wrong from the
  day they were written: "rule 18" in `entry_model.py` and
  `test_decision_bar_integrity.py` — `108cc9f` renumbered that rule in the same commit
  (now 22). `code_hash` unmoved, all 33 per-file fingerprints equal, with a negative
  control. Full account in its commit message and Notes Entry #139.
- **Item 10 — README.md brought current, `077d120`.** The three recorded omissions
  closed, plus four stale statements found by reading the whole file: test counts,
  `Logs/` for `logs/`, the module lists and "sixteen files" (twenty-two now), and the
  "nothing but a Python interpreter" claim `run_tests.py`'s docstring had withdrawn.
  Notes Entry #140.
- **Engineering Notes regenerated, v1.32, Entries #136–#140**, with the two portfolio
  PDFs. This file's previous version (`16d3c1f`) moved to HISTORY verbatim, proven by
  un-demoting the block and comparing byte for byte, with a one-character negative
  control; the old HISTORY is an exact prefix of the new one.

### Open items

Items marked **Viktor's call** are his to decide; he writes his position first and
Claude critiques it.

- **Viktor's call — planning the independent audit:** which model, the package (the
  standing default for a fresh Tier-1 audit is the full package), and whether the
  auditor sees the scrapped findings. Not started.
- **Viktor's call, open since 6 September — `docs/Phase7_Audit_Findings_Complete.pdf`.**
  README.md and `docs/build/README.md` cite it; it does not exist in the repository, and
  its build script's source material has never been here. Remove the reference, or
  restore the source material. Not in the list scrapped on 20 September.
- **Viktor, outside the repository:** delete "To do list Claude Phase 7 Engine.pdf".
  Carried from `16d3c1f`; whether it has been done is not known.
- **Not investigated:** a connection attempt to `api.mexc.com` during `run_tests.py`,
  refused by the sandbox's egress proxy. Seen once on the tree before `b68de08`, and
  once on a pristine `16d3c1f` tree on 20 September, before any of this session's
  changes; not in the other runs. Which test, if any, makes it is unknown.
- **Found, not fixed: DECISIONS' "The rules, earned" has no rule 18.** The list goes
  17 → 19 since `108cc9f`. Not renumbered, because rule numbers are cited by number
  throughout and renumbering would make every later citation wrong. Rule-number
  citations in live code were checked by title and match; those in dated records were
  not checked.
- **The pre-push hook is installed per clone, not per repository.** After any re-clone
  (including after a machine wipe), run `git config core.hooksPath githooks`;
  `session_handover_check.py` section 6 flags a clone without it.
- **Unrelated, not urgent:** confirm which YH programme permits AI-assisted
  examensarbete work.


## 20 September 2026 — correction: the round-1 audit outputs were lost

*A new dated entry, not an edit: under the ruling "dated records are not edited to follow
a move" (DECISIONS, 20 September 2026), the 30 August entry "The machine was rebuilt"
stands as written, and this entry corrects it.*

**What the 30 August entry got wrong.** It says: "Everything of value is on GitHub at
`375334a`; nothing lived only on disk except gitignored `logs/`." The four verbatim
round-1 auditor outputs — Run 1 (DeepSeek V4 Pro, blind review) and Runs A, B and C
(Kimi K3), all run on 27 August through the OpenRouter chat room — were not on GitHub.
No commit on any branch has ever contained `docs/audit_raw/`, any of the four filenames
`build_findings_bundle.py` expects, or `docs/Phase7_Audit_Findings_Complete.pdf` (checked
20 September with `git log --all` on a fresh clone at `c745a67`). No copy outside the
repository has been found either (below). The pre-reinstall check looked at what the
repository tracked and ignored; it had no way to see what had never entered it.

**How it surfaced.** README.md said "All raw auditor output is published verbatim in
`docs/Phase7_Audit_Findings_Complete.pdf`", and that the later rounds' reports were in
`docs/audit_reports/` "the same as the original four". The PDF had been recorded as
missing since 6 September and left as Viktor's call. Deciding it on 20 September meant
first establishing whether the source could be restored.

**What was searched, 20 September, and what each found:**

- `D:\phase7_engine`, every folder under `docs\`, on disk: nothing. The one candidate,
  `docs/audit_package/luna_pro_audit_report.md`, is a different audit (GPT-5.6 Luna Pro).
- `D:\Phase_7_Engine_Random_Files`: nothing. `Feedback_Phase7_Engine.pdf` names the
  auditors but is Claude's critique of Viktor's role, not their output.
- Git history, all branches: never committed (above).
- OpenRouter chat room: empty. Its history is kept only in the browser, not on
  OpenRouter's servers (OpenRouter's own help article).
- OpenRouter request logs: the 27 August generations are listed — DeepSeek V4 Pro at
  03:58 and Kimi K3 at 04:56, 05:26, 05:39, 06:40 and 07:18 (local time) — but each
  shows "I/O logging is not enabled". Token counts and costs only, no text. Claude first
  guessed that an icon on some rows meant the text was stored; opening one showed it
  does not. Recorded because it was stated before it was checked.
- A Claude data export for 26–31 August: `conversations.json` is an empty list. One
  project from those dates (created 27 August, unnamed) lists seven documents from 29–30
  August, every one with an empty filename and empty content in the export. Whether
  Cowork sessions are included in that export at all was not checked.

**Not searched**, when Viktor ended the search: his Downloads folder; the Cowork task list
in the desktop app for 27–29 August sessions; the unnamed project opened in the app
rather than read from the export. "Lost" in this entry's title means not found after the
search above, not proven absent everywhere.

**Rulings, Viktor, 20 September 2026** (Claude recommended all three; Viktor approved them
as proposed):

1. README.md states that the round-1 outputs were never committed and cannot be
   recovered, says what survives (`Phase7_Remediation_Plan.pdf`, GLM 5.3's unedited
   prioritisation of those findings, not the findings themselves), and drops "the same
   as the original four".
2. The 30 August entry's error is recorded here, as a new dated entry.
3. `docs/build/build_findings_bundle.py` is kept. It exits 2 with a message rather than
   failing part-way, and it is the record of how the PDF was built.

**What the original four were, so the record keeps at least that:** Run 1, DeepSeek V4
Pro — blind review, source only, no Constitution, no register. Run A, Kimi K3 — the
Minimum Viable Audit gate, Items 2, 3, 6 and 18, plus the DEFECT resolution. Run B,
Kimi K3 — the remaining Tier 1 invariants, Items 1, 4, 5, 7–17 and 19–21. Run C,
Kimi K3 — Tiers 2, 3 and 4. (From `build_findings_bundle.py`'s own file table and
README.md's audit table.)


## 20 September 2026 (morning) — PHASE7_NEXT.md as it stood at `4629002`

*Moved here verbatim on 20 September 2026, when PHASE7_NEXT.md was rewritten in the next
session. Every line below the rule is the file's content at `4629002`, unchanged —
including its own "this session" wording. Its headings are demoted one level (`#` → `##`,
`##` → `###`) so they nest under this entry; no other character is changed.*

---

## Next step — read this first

*20 September 2026. This file is the project's current-state entry point: it states only
what is true right now and what to do next, and is rewritten each session, not appended
to. Standing rules, ratified specifications and rulings in force live in
docs/PHASE7_DECISIONS.md. The dated record — including this file's previous version,
moved there verbatim this session — lives in docs/PHASE7_HISTORY.md. A citation of this
file written before the 18 September 2026 split — in the Engineering Notes, audit
reports, handovers or any other dated record — refers to content now in one of those
two files; dated records are not edited to say so (DECISIONS, "Ruling, 20 September
2026 — dated records are not edited to follow a move").*

### PACE FIRST — read this before the rest of this file

Viktor judged, on his own, that 226 commits across 22 days had become hasty, and
ruled to slow down considerably (15 September 2026). **Do not open a session by
proposing work from "Open items" below, and do not treat it as a queue to clear.**
Ask what he wants to do first.

### Where the project is

The three mechanical items before the independent audit are done (`b68de08`, `9a35f1c`,
`077d120`), and the open question about `docs/Phase7_Audit_Findings_Complete.pdf` is now
closed: its source, the four round-1 auditor outputs, could not be found, and README.md
says so
(HISTORY, "20 September 2026 — correction: the round-1 audit outputs were lost").
**What comes next is planning the independent audit, and that is Viktor's call** —
which model, which package, and whether the auditor sees the findings scrapped on
20 September (DECISIONS, "Ruling, 20 September 2026 — the open-items list scrapped;
an independent audit next").

### Ruled this session

- **The round-1 outputs are recorded as lost, not restored** (the Findings_Complete
  item). Viktor chose to find the source first; the search covered the repository on
  disk, git history, `D:\Phase_7_Engine_Random_Files`, the OpenRouter chat room and
  request logs, and a Claude data export, and found no copy. He then called off the
  search and approved Claude's three recommendations as proposed: README.md states the
  loss and what survives; the 30 August "nothing lived only on disk" error is recorded
  as a new dated HISTORY entry; `build_findings_bundle.py` is kept. Full account in
  HISTORY, "20 September 2026 — correction: the round-1 audit outputs were lost".

### Where things stand, right now

- **Tip:** current as of `c745a67`; the actual tip is the commit that wrote this file
  (a commit cannot name its own hash). **Tag:** `portfolio-v1` at `99e022e`.
  **Release gate:** open, declared 15 September 2026.
- **code_hash:** `bb47ab537314953e16b2db2fcf24003ead64eb5538a30221a6578d518bb7d34d` —
  unchanged since `f24a6e9`. Recomputed on `c745a67`'s tree and on this commit's applied
  tree; not assumed.
- **Golden snapshot:** last changed at `f24a6e9`; no engine code has changed since.
- **Test suite**, unchanged since `b68de08`: 486 passed / 0 failed with pandas_ta;
  355 passed / 120 skipped without it; `run_tests.py` 415 / 0 / 32. Linux sandbox,
  autocrlf clone, on `c745a67` and on this commit's applied tree. Windows at `c745a67`:
  **confirmation by proceeding** (Viktor went past the stop-on-difference steps and
  pasted `git status`). Windows at this commit: to be confirmed the same way.
- **Engineering Notes:** through Entry #140 (v1.32), at `c745a67`. **One commit behind**
  — this one — by the batching rule; the Portfolio and AI-Attribution PDFs likewise.
- **Handover check / pre-push hook:** `c745a67` is on GitHub — fetched into the sandbox
  on 20 September and confirmed as the tip. The hook's output for that push was not
  pasted, so it is not recorded here.

### Resolved this session

- **`docs/Phase7_Audit_Findings_Complete.pdf`, open since 6 September.** README.md no
  longer claims the round-1 output is published; it says the output was never committed,
  cannot be recovered, and names what survives. The same passage's "the same as the
  original four" is gone — the round-1 reports were never in `docs/audit_reports/`.
  `docs/build/README.md` points to the HISTORY entry. The error in HISTORY's 30 August
  entry is corrected by a new entry, not an edit.

### Open items

Items marked **Viktor's call** are his to decide; he writes his position first and
Claude critiques it.

- **Viktor's call — planning the independent audit:** which model, the package (the
  standing default for a fresh Tier-1 audit is the full package), and whether the
  auditor sees the scrapped findings. Not started.
- **Found, not checked: README.md's "Every raw report from every round is in
  `docs/audit_reports/`".** Round 2's folder holds a reasoning trace that ends before
  any report, and the provider export records Qwen's round-2 output as never saved.
  Whether the sentence overstates this was not examined — it was outside the
  Findings_Complete item.
- **Viktor, outside the repository:** delete "To do list Claude Phase 7 Engine.pdf".
  It was seen back in `D:\Phase_7_Engine_Random_Files` on 20 September, after an
  earlier listing the same day had not shown it.
- **Not investigated:** a connection attempt to `api.mexc.com` during `run_tests.py`,
  refused by the sandbox's egress proxy. Seen once on the tree before `b68de08`, and
  once on a pristine `16d3c1f` tree on 20 September. Which test, if any, makes it is
  unknown.
- **Found, not fixed: DECISIONS' "The rules, earned" has no rule 18.** The list goes
  17 → 19 since `108cc9f`. Not renumbered, because rule numbers are cited by number
  throughout and renumbering would make every later citation wrong. Rule-number
  citations in live code were checked by title and match; those in dated records were
  not checked.
- **The pre-push hook is installed per clone, not per repository.** After any re-clone
  (including after a machine wipe), run `git config core.hooksPath githooks`;
  `session_handover_check.py` section 6 flags a clone without it.
- **Unrelated, not urgent:** confirm which YH programme permits AI-assisted
  examensarbete work.


## 20 September 2026 (evening) — PHASE7_NEXT.md as it stood at `92775ea`

*Moved here verbatim on 20 September 2026, when PHASE7_NEXT.md was rewritten in the next
session. Every line below the rule is the file's content at `92775ea`, unchanged — including
its own "this session" and "this commit" wording, which refers to `3a899b5` and `92775ea`.
Its headings are demoted one level (`#` → `##`, `##` → `###`) so they nest under this entry;
no other character is changed.*

---

## Next step — read this first

*20 September 2026. This file is the project's current-state entry point: it states only
what is true right now and what to do next, and is rewritten each session, not appended
to. Standing rules, ratified specifications and rulings in force live in
docs/PHASE7_DECISIONS.md. The dated record — including this file's previous version,
moved there verbatim this session — lives in docs/PHASE7_HISTORY.md. A citation of this
file written before the 18 September 2026 split — in the Engineering Notes, audit
reports, handovers or any other dated record — refers to content now in one of those
two files; dated records are not edited to say so (DECISIONS, "Ruling, 20 September
2026 — dated records are not edited to follow a move").*

### PACE FIRST — read this before the rest of this file

Viktor judged, on his own, that 226 commits across 22 days had become hasty, and
ruled to slow down considerably (15 September 2026). **Do not open a session by
proposing work from "Open items" below, and do not treat it as a queue to clear.**
Ask what he wants to do first.

### Where the project is

The three mechanical items before the independent audit are done (`b68de08`, `9a35f1c`,
`077d120`), and the `docs/Phase7_Audit_Findings_Complete.pdf` item is closed (`4629002`;
HISTORY, "20 September 2026 — correction: the round-1 audit outputs were lost"). This
session only brought the record current: `4629002`'s Windows result and hook result
recorded below, and the Engineering Notes regenerated through it.
**What comes next is planning the independent audit, and that is Viktor's call** —
which model, which package, and whether the auditor sees the findings scrapped on
20 September (DECISIONS, "Ruling, 20 September 2026 — the open-items list scrapped;
an independent audit next").

### Ruled this session

Nothing.

### Where things stand, right now

- **Tip:** current as of `3a899b5`; the actual tip is the commit that wrote this file
  (a commit cannot name its own hash). **Tag:** `portfolio-v1` at `99e022e`.
  **Release gate:** open, declared 15 September 2026.
- **code_hash:** `bb47ab537314953e16b2db2fcf24003ead64eb5538a30221a6578d518bb7d34d` —
  unchanged since `f24a6e9`. Recomputed on `3a899b5`'s tree and on this commit's applied
  tree; not assumed.
- **Golden snapshot:** last changed at `f24a6e9`; no engine code has changed since.
- **Test suite**, unchanged since `b68de08`: 486 passed / 0 failed with pandas_ta;
  355 passed / 120 skipped without it; `run_tests.py` 415 / 0 / 32. Linux sandbox,
  autocrlf clone, on `3a899b5` and on this commit's applied tree. Windows at `4629002`
  and at `3a899b5`: **confirmation by proceeding** (Viktor went past the
  stop-on-difference steps). Windows at this commit: to be confirmed the same way.
- **Engineering Notes:** through Entry #141 (v1.33), which covers `4629002`. **Two
  commits behind** — `3a899b5`, which regenerated them, and this one — by the
  batching rule. A commit that regenerates the Notes cannot cover itself, so one
  behind is the lowest the gap can go; regenerating again for `3a899b5` alone would
  only move the gap forward one commit.
- **Portfolio Document and AI-Attribution Statement:** current. Rebuilt from `4629002`,
  their extracted text is identical to the committed PDFs, because no commit since
  `c745a67` has changed either script; so they were not regenerated. The previous
  version of this file said they were one commit behind; that was wrong.
- **Handover check / pre-push hook:** `3a899b5` is on GitHub — fetched into the sandbox
  on 20 September, confirmed as the tip, and its four changed files compared byte for
  byte with the tree verified before delivery. The pre-push hook reported
  `SUMMARY: clean` on the pushes of `4629002` and `3a899b5` (Viktor's report).

### Resolved this session

- **The record brought current at `4629002`.** The two landing facts above, Entry #141
  and the v1.33 Document History row in the Engineering Notes, and the correction about
  the two portfolio PDFs.
- **`3a899b5`'s landing facts recorded** (the Windows and hook results above), in a
  NEXT-only commit. Viktor chose this over leaving them for the next docs commit or
  regenerating the Notes for `3a899b5`.

### Open items

Items marked **Viktor's call** are his to decide; he writes his position first and
Claude critiques it.

- **Viktor's call — planning the independent audit:** which model, the package (the
  standing default for a fresh Tier-1 audit is the full package), and whether the
  auditor sees the scrapped findings. Not started.
- **Found, not checked: README.md's "Every raw report from every round is in
  `docs/audit_reports/`".** Round 2's folder holds a reasoning trace that ends before
  any report, and the provider export records Qwen's round-2 output as never saved.
  Whether the sentence overstates this was not examined (recorded at `4629002`).
- **Viktor, outside the repository:** delete "To do list Claude Phase 7 Engine.pdf".
  It was seen back in `D:\Phase_7_Engine_Random_Files` on 20 September, after an
  earlier listing the same day had not shown it.
- **Not investigated:** a connection attempt to `api.mexc.com` during `run_tests.py`,
  refused by the sandbox's egress proxy. Seen once on the tree before `b68de08`, and
  once on a pristine `16d3c1f` tree on 20 September. Which test, if any, makes it is
  unknown.
- **Found, not fixed: DECISIONS' "The rules, earned" has no rule 18.** The list goes
  17 → 19 since `108cc9f`. Not renumbered, because rule numbers are cited by number
  throughout and renumbering would make every later citation wrong. Rule-number
  citations in live code were checked by title and match; those in dated records were
  not checked.
- **The pre-push hook is installed per clone, not per repository.** After any re-clone
  (including after a machine wipe), run `git config core.hooksPath githooks`;
  `session_handover_check.py` section 6 flags a clone without it.
- **Unrelated, not urgent:** confirm which YH programme permits AI-assisted
  examensarbete work.


## 20 September 2026 — PHASE7_NEXT.md as it stood at `982e70f`

*Moved here verbatim on 20 September 2026, when PHASE7_NEXT.md was rewritten in the next
session. Every line below the rule is the file's content at `982e70f`, unchanged —
including its own wording: "this session" refers to the session that wrote `53394ff`;
"this commit" refers to `982e70f`, which edited the file in place and added the section
"Recorded later on 20 September, in a new session". Its "20 September, evening" is as
written; `53394ff` is timestamped 09:11 (+0200). Its headings are demoted one level
(`#` → `##`, `##` → `###`) so they nest under this entry; no other character is changed.*

---

## Next step — read this first

*20 September 2026. This file is the project's current-state entry point: it states only
what is true right now and what to do next, and is rewritten each session, not appended
to. Standing rules, ratified specifications and rulings in force live in
docs/PHASE7_DECISIONS.md. The dated record — including this file's previous version,
moved there verbatim this session — lives in docs/PHASE7_HISTORY.md. A citation of this
file written before the 18 September 2026 split — in the Engineering Notes, audit
reports, handovers or any other dated record — refers to content now in one of those
two files; dated records are not edited to say so (DECISIONS, "Ruling, 20 September
2026 — dated records are not edited to follow a move").*

### PACE FIRST — read this before the rest of this file

Viktor judged, on his own, that 226 commits across 22 days had become hasty, and
ruled to slow down considerably (15 September 2026). **Do not open a session by
proposing work from "Open items" below, and do not treat it as a queue to clear.**
Ask what he wants to do first.

### Where the project is

This session (20 September, evening) took four loose ends from the Open items, at
Viktor's choice: README.md's claim about the audit reports, the `api.mexc.com`
connection seen during the tests, rule-number citations around DECISIONS' missing
rule 18, and folding `92775ea`'s landing facts into this file. All four are closed —
see "Resolved this session". Checking the README claim turned up a contradiction in
the record about round 3's independence, which Viktor ruled on.
**What comes next is still planning the independent audit, and that is Viktor's
call** — which model, which package, and whether the auditor sees the findings
scrapped on 20 September (DECISIONS, "Ruling, 20 September 2026 — the open-items list
scrapped; an independent audit next").

### Ruled this session

- **Round 3 is not counted as independent.** DECISIONS, "Ruling, 20 September 2026 —
  round 3 is not counted as independent": the reason that holds is authorship (GLM 5.3
  wrote the Remediation Plan; GLM 5.3 Flash then reviewed work done under it), not
  exposure, which the 2 September ruling would clear. Viktor first proposed counting it
  as independent, from memory of the 28 August run as minor; the record showed
  otherwise, and he ruled.
- **`test_main_runs_without_a_logs_directory` is left as it is (option A)** — it keeps
  doing one live engine run against MEXC whenever the suite runs with `pandas_ta`.
  Claude recommended option B (point the subprocess at `tests/fixtures/pinned/`, which
  ran to exit 0 with no network in the sandbox) and was overruled.
- **README wording delegated to Claude:** the round-2 sentence ("do what is best for
  the project") and the round-3 wording ("fix the GLM wording as it should be done").
- **A note at the rule-18 gap in DECISIONS: yes.**

### Where things stand, right now

- **Tip:** current as of `53394ff`; the actual tip is the commit that wrote this file
  (a commit cannot name its own hash). `53394ff` was confirmed as GitHub's tip by a
  fresh clone (Viktor's, and again by the sandbox clone of the later 20 September
  session). **Tag:** `portfolio-v1` at `99e022e`.
  **Release gate:** open, declared 15 September 2026.
- **code_hash:** `bb47ab537314953e16b2db2fcf24003ead64eb5538a30221a6578d518bb7d34d` —
  unchanged since `f24a6e9`. Recomputed on `53394ff`'s tree and on this commit's applied
  tree; not assumed.
- **Golden snapshot:** last changed at `f24a6e9`; no engine code has changed since.
- **Test suite**, unchanged since `b68de08`: 486 passed / 0 failed with pandas_ta;
  355 passed / 120 skipped without it; `run_tests.py` 415 / 0 / 32. Linux sandbox,
  autocrlf clone, on `53394ff` and on this commit's applied tree. Windows at `4629002`,
  `3a899b5`, `92775ea` and `53394ff`: **confirmation by proceeding** (Viktor went past
  the stop-on-difference steps). Windows at this commit: to be confirmed the same way.
- **Engineering Notes:** through Entry #141 (v1.33), which covers `4629002`. **Four
  commits behind** — `3a899b5`, `92775ea`, `53394ff` and this one — by the batching
  rule. Not regenerated in this commit. If the independent audit's package includes the
  Notes, regenerate them before building it.
- **Portfolio Document and AI-Attribution Statement:** current with their scripts; no
  commit since `c745a67` has changed either script. One claim in the Portfolio Document
  is now known to be wrong — see Open items.
- **Handover check / pre-push hook:** the pre-push hook reported `SUMMARY: clean` on
  the pushes of `4629002`, `3a899b5`, `92775ea` and `53394ff` (Viktor's report).

### Resolved this session

- **README.md's "Every raw report from every round is in `docs/audit_reports/`".**
  Narrowly overstated: round 2 never produced a report (every attempt stopped before
  writing one; the folder holds Kimi K3's reasoning trace, and a Qwen response from
  that day was never saved), yet the paragraph counted it among rounds that had run and
  pointed to their reports. Now stated. The same paragraph said every round ran "on a
  model reporting no prior exposure"; corrected per the round-3 ruling, with the status
  table and the release-gate paragraph brought in line ("five further rounds", three
  both independent and complete).
- **The `api.mexc.com` connection.** Made by
  `tests/test_clean_checkout.py::test_main_runs_without_a_logs_directory`, which runs
  `python main.py` in a temporary copy of the repository and so fetches live data. Found
  by tracing every outbound connection in the sandbox (Linux, autocrlf clone, `92775ea`):
  it is the suite's only one, under both pytest and `run_tests.py`; with `pandas_ta`
  absent no connection was made (whether because that test is skipped was not checked).
  It writes only inside its temporary directory, so the live decision log is not
  touched. Left as is, by ruling.
- **Rule-number citations around the missing rule 18.** The rules list was rebuilt at
  all 98 commits that touched it. Only one rule ever changed number — "Fixing the
  instance you found does not close the item": 18 → 20 at `108cc9f`, → 21 at
  `710cb5e`, → 22 at `e70b835`, all 1–2 September. Every citation of rules 18–21 in
  tracked `.md`/`.py`/`.txt` files (excluding `docs/audit_package/` and
  `docs/audit_reports/`) and in every commit message was checked against the list as it
  stood when written: all correct, except "rule 18" meaning today's rule 22, already
  recorded at `9a35f1c` (Entry #139). PDFs were not searched.
- **A note at the gap, and a rendering defect it also fixes.** DECISIONS now has an
  item 18 saying the number is empty and where the rule went. Found while adding it:
  Markdown numbers an ordered list by position, so the rendered list had shown every
  rule from 19 on one lower than its cited number — a reader following "rule 22" on
  GitHub landed on rule 23. Checked with a CommonMark renderer (markdown-it-py), not on
  GitHub itself: before, source and rendered numbers diverged from 19 on; after, all 38
  match.
- **`92775ea`'s landing facts** (Windows by proceeding, hook clean) folded in above.

### Recorded later on 20 September, in a new session

- **`53394ff`'s landing facts** (Windows by proceeding, hook clean) folded in above.
- **Claude's `git status --short` prediction was wrong, a second time** (Viktor's
  report). It listed `??` lines for the two delivery files. They are gitignored
  (`.gitignore` lines 106–107: `*.patch`, `*_commit_message.txt`), so they never appear
  there; the correct prediction is that they are absent.
- **"To do list Claude Phase 7 Engine.pdf" is deleted** from
  `D:\Phase_7_Engine_Random_Files` (Viktor's report). Its Open item is closed.

### Open items

Items marked **Viktor's call** are his to decide; he writes his position first and
Claude critiques it.

- **Viktor's call — planning the independent audit:** which model, the package (the
  standing default for a fresh Tier-1 audit is the full package), and whether the
  auditor sees the scrapped findings. Not started.
- **Found, not fixed: the Portfolio Document says the four original audit runs were on
  "models with no prior involvement in the build".** README.md says DeepSeek worked on
  the build through Aider, and Run 1 was DeepSeek. Fixing it means editing
  `build_portfolio_document.py` and regenerating the PDF.
- **Found, not checked:** HISTORY's 5 September "The record corrected from the bill"
  says the eleven round-2 observations came from a Qwen run; the
  `round2_kimi_k3_20260902/README.md`, filed later, says they are Kimi's. Which is the
  later word, and whether the earlier one is marked superseded, was not examined.
- **The pre-push hook is installed per clone, not per repository.** After any re-clone
  (including after a machine wipe), run `git config core.hooksPath githooks`;
  `session_handover_check.py` section 6 flags a clone without it.
- **Unrelated, not urgent:** confirm which YH programme permits AI-assisted
  examensarbete work.


## 20 September 2026 (late evening) — PHASE7_NEXT.md as it stood at `65a0aef`

*Moved here verbatim on 20 September 2026, when PHASE7_NEXT.md was rewritten in the
next session. Every line below the rule is the file's content at `65a0aef`, the commit
that wrote it, unchanged — including its own wording: "this session" is the session
that wrote `65a0aef`, and "this commit" is `65a0aef` itself. It does not know about
`a9d4b1f` or `6e1baba`, which landed after it and before this move; `6e1baba`'s commit
message records why, since the file could not. Its headings are demoted one level
(`#` → `##`, `##` → `###`) so they nest under this entry; no other character is
changed.*

---

## Next step — read this first

*20 September 2026. This file is the project's current-state entry point: it states only
what is true right now and what to do next, and is rewritten each session, not appended
to. Standing rules, ratified specifications and rulings in force live in
docs/PHASE7_DECISIONS.md. The dated record — including this file's previous version,
moved there verbatim this session — lives in docs/PHASE7_HISTORY.md. A citation of this
file written before the 18 September 2026 split — in the Engineering Notes, audit
reports, handovers or any other dated record — refers to content now in one of those
two files; dated records are not edited to say so (DECISIONS, "Ruling, 20 September
2026 — dated records are not edited to follow a move").*

### PACE FIRST — read this before the rest of this file

Viktor judged, on his own, that 226 commits across 22 days had become hasty, and
ruled to slow down considerably (15 September 2026). **Do not open a session by
proposing work from "Open items" below, and do not treat it as a queue to clear.**
Ask what he wants to do first.

### Where the project is

This session (20 September, from about 10:00) opened on the independent audit, and
Viktor chose to land the session's routine record first, as its own commit: this
rewrite of the file, with its previous version moved verbatim to HISTORY, and
`982e70f`'s two landing facts. The previous session's account — the round-3 ruling,
README's audit-round corrections, the `api.mexc.com` trace, the rule-18 note, and the
in-place record of `53394ff`'s landing — is now in HISTORY, "20 September 2026 —
PHASE7_NEXT.md as it stood at `982e70f`".
**What comes next is still planning the independent audit, and that is Viktor's
call** — which model, which package, whether the auditor sees the findings scrapped
on 20 September, and the instruction for the selected model (DECISIONS, "Ruling, 20
September 2026 — the open-items list scrapped; an independent audit next"). He writes
his position first; Claude critiques it.

### Ruled this session

- **The NEXT rewrite and `982e70f`'s landing facts land first, as their own commit**,
  rather than being folded into the audit-planning commit as planned at the end of the
  previous session. Viktor's choice.
- **The Engineering Notes are not regenerated in this commit.** Claude recommended
  waiting: a regeneration now would cover `3a899b5` to `982e70f` but not the
  audit-planning commit that follows, so it would have to be done again before building
  a package that includes the Notes. Viktor agreed. They are regenerated once, after
  the audit rulings, and only if the package includes them.

### Where things stand, right now

- **Tip:** current as of `982e70f`; the actual tip is the commit that wrote this file
  (a commit cannot name its own hash). `982e70f` was confirmed as GitHub's tip by a
  sandbox fetch (Viktor's report), and again by this session's sandbox clone.
  **Tag:** `portfolio-v1` at `99e022e`. **Release gate:** open, declared 15 September
  2026.
- **code_hash:** `bb47ab537314953e16b2db2fcf24003ead64eb5538a30221a6578d518bb7d34d` —
  unchanged since `f24a6e9`. Recomputed on `982e70f`'s tree and on this commit's applied
  tree; not assumed.
- **Golden snapshot:** last changed at `f24a6e9`; no engine code has changed since.
- **Test suite**, unchanged since `b68de08`: 486 passed / 0 failed with pandas_ta;
  355 passed / 120 skipped without it; `run_tests.py` 415 / 0 / 32. Linux sandbox,
  autocrlf clone, on `982e70f` and on this commit's applied tree. Windows at `4629002`,
  `3a899b5`, `92775ea`, `53394ff` and `982e70f`: **confirmation by proceeding** (Viktor
  went past the stop-on-difference steps). Windows at this commit: to be confirmed the
  same way.
- **Engineering Notes:** through Entry #141 (v1.33), which covers `4629002`. **Five
  commits behind** — `3a899b5`, `92775ea`, `53394ff`, `982e70f` and this one — by
  Viktor's choice this session (see "Ruled this session"). If the independent audit's
  package includes the Notes, regenerate them after the audit-planning commit and
  before building it.
- **Portfolio Document and AI-Attribution Statement:** current with their scripts; no
  commit since `c745a67` has changed either script. One claim in the Portfolio Document
  is now known to be wrong — see Open items.
- **Handover check / pre-push hook:** the pre-push hook reported `SUMMARY: clean` on
  the pushes of `4629002`, `3a899b5`, `92775ea`, `53394ff` and `982e70f` (Viktor's
  report).

### Resolved this session

- **`982e70f`'s landing facts** (Windows by proceeding, hook clean) folded in above.
- **The once-per-session rewrite of this file**, deferred by `982e70f` to this
  session. The previous version is in HISTORY verbatim, headings demoted one level.

### Open items

Items marked **Viktor's call** are his to decide; he writes his position first and
Claude critiques it.

- **Viktor's call — planning the independent audit:** which model, the package (the
  standing default for a fresh Tier-1 audit is the full package), whether the auditor
  sees the scrapped findings, and the instruction for the selected model. Not started.
  If the package includes the Engineering Notes, regenerate them first (see above).
- **Found, not fixed: the Portfolio Document says the four original audit runs were on
  "models with no prior involvement in the build".** README.md says DeepSeek worked on
  the build through Aider, and Run 1 was DeepSeek. Fixing it means editing
  `build_portfolio_document.py` and regenerating the PDF.
- **Found, not checked:** HISTORY's 5 September "The record corrected from the bill"
  says the eleven round-2 observations came from a Qwen run; the
  `round2_kimi_k3_20260902/README.md`, filed later, says they are Kimi's. Which is the
  later word, and whether the earlier one is marked superseded, was not examined.
- **The pre-push hook is installed per clone, not per repository.** After any re-clone
  (including after a machine wipe), run `git config core.hooksPath githooks`;
  `session_handover_check.py` section 6 flags a clone without it.
- **Unrelated, not urgent:** confirm which YH programme permits AI-assisted
  examensarbete work.


## 21 September 2026 — PHASE7_NEXT.md as it stood at `635a94e`

*Moved here verbatim on 21 September 2026, when PHASE7_NEXT.md was rewritten in the
next session. Every line below the rule is the file's content at `635a94e` — written at
`b869a30` and amended in place at `635a94e` — unchanged, including its own wording:
"this session" is the 20 September session that wrote `b869a30`, `119c8a3` and
`635a94e`, and "this amendment" is `635a94e`. Its headings are demoted one level
(`#` → `##`, `##` → `###`) so they nest under this entry; no other character is
changed.*

---

## Next step — read this first

*20 September 2026 (late evening). This file is the project's current-state entry point:
it states only what is true right now and what to do next, and is rewritten each session,
not appended to. Standing rules, ratified specifications and rulings in force live in
docs/PHASE7_DECISIONS.md. The dated record — including this file's previous version,
moved there verbatim this session — lives in docs/PHASE7_HISTORY.md. A citation of this
file written before the 18 September 2026 split — in the Engineering Notes, audit
reports, handovers or any other dated record — refers to content now in one of those
two files; dated records are not edited to say so (DECISIONS, "Ruling, 20 September
2026 — dated records are not edited to follow a move").*

*Amended 21 September 2026, one commit after it was written. `119c8a3` landed after
`b869a30` wrote this file, in the same session, and left five statements below false
and six more incomplete or unrecorded.
This amendment corrects them in place. It is **not** the once-per-session rewrite, and
no HISTORY move is owed by it — `b869a30` made that move.*

### PACE FIRST — read this before the rest of this file

Viktor judged, on his own, that 226 commits across 22 days had become hasty, and
ruled to slow down considerably (15 September 2026). **Do not open a session by
proposing work from "Open items" below, and do not treat it as a queue to clear.**
Ask what he wants to do first.

### Where the project is

This session opened fresh after `6e1baba`, with this file two commits stale — `a9d4b1f`
and `6e1baba` had both landed since it was written at `65a0aef`, by Viktor's own ruling
that the rewrite happens in a new chat (`6e1baba`'s commit message records it, because
the file itself could not). Asked what he wanted to do first, he chose the rewrite and
the TREND-line fix, in that order, as two separate commits — the rewrite being this one.

**What comes next is still planning the independent audit, and that is Viktor's
call** — which model, which package, whether the auditor sees the findings scrapped on
20 September, and the instruction for the selected model (DECISIONS, "Ruling, 20
September 2026 — the open-items list scrapped; an independent audit next"). He writes
his position first; Claude critiques it. He said this session that he is considering
putting that audit on pause, "since we fixed all the issues now." **That is a position,
not a ruling, and nothing here acts on it.** Claude's stated objection, for him to
answer when he does rule: the audit's purpose on this project has never been to close
known findings — it is to find the ones nobody has found yet, and the project's own
record says the recurring defect shape is the one that survives audits, on paths a
healthy run never takes. An empty open-items list is what an audit is for, not a reason
to skip one. The TREND-line defect fixed at `119c8a3` is a small instance of the same
argument: it was found by Viktor reading a live panel two hours after a patch that fixed
its identical twin, not by any review.

### Ruled this session

- **The NEXT rewrite lands first, as its own commit; the TREND-line fix follows as a
  second, separate commit.** Viktor's choice from three offered options. The fix is a
  code change and moves `code_hash`, so it is not mixed into a documentation commit —
  the same separation `6e1baba` made. Both landed, in that order: `b869a30`, then
  `119c8a3`.

### Where things stand, right now

- **Tip:** current as of `119c8a3`; the actual tip is the commit that amended this file
  (a commit cannot name its own hash). `119c8a3` was confirmed as GitHub's tip by a fresh
  sandbox clone on 21 September, which found `PHASE7_NEXT.md`, `PHASE7_HISTORY.md` and
  `core/panel_render.py` byte-identical to the verified tree and the new test file
  identical modulo CRLF.
  **Tag:** `portfolio-v1` at `99e022e`. **Release gate:** open, declared 15 September
  2026.
- **code_hash:** `35718f6b8c7c021f52ae566c266ab7fc8295c7e1bff89121bba8a20272168b3c` —
  moved at `119c8a3`, the TREND-line fix, from `b02137660111…`, which had itself moved at
  `a9d4b1f` from `bb47ab53…`, where it stood since `f24a6e9`. Unmoved by `6e1baba`, by
  `b869a30` and by this amendment — none of the three touches a `.py` file outside
  `docs/`, which `core/code_fingerprint.py` excludes by directory. Recomputed under
  Python 3.12 on `119c8a3`'s tree and on this amendment's applied tree; not assumed.
- **code_hash is only comparable within one Python minor version, and that bit this
  session.** `core/code_fingerprint.py` hashes `ast.dump` output, which is a CPython
  implementation detail; the file says so under "WHAT IT DOES NOT SURVIVE". The sandbox
  used this session had `python3` = 3.11.15 by default and reported
  `938720cd…` on an unmodified `6e1baba` tree. Nothing had moved: Python 3.12.3 on the
  same tree gives `b0213766…`, matching Viktor's Windows decision-log record, and
  Python 3.13.13 gives a third value again. **Every `code_hash` claim about this
  project must be computed under Python 3.12** (Viktor runs 3.12.10; the pinned
  requirements record 3.12.10 and 3.12.3). A hash that "moved" is a question about the
  interpreter before it is a question about the code.
- **Golden snapshot:** re-baselined at `a9d4b1f`, two fields only. Unchanged by
  `6e1baba`, by `b869a30`, by `119c8a3` and by this amendment, and no re-baseline has
  been run since `a9d4b1f`. `119c8a3` changed a panel-rendering string only; nothing on
  the decision path has moved since `a9d4b1f`.
- **Test suite**, moved at `119c8a3`, which added a fixture-free file of 4 tests:
  **504 passed / 0 failed** with `pandas_ta`; **372 passed / 121 skipped** without it;
  `run_tests.py` **433 passed / 0 failed / 32 errors**. The 32 are fixture-collection
  errors and have not moved since long before this session — the new tests take no
  fixture, which is why the error count stayed flat while the passed count rose by four,
  and no behavioural failure is hidden in them. Reported at `119c8a3` from a Linux
  sandbox and from Viktor's Windows machine, agreeing on all three; the sandbox clone
  type for that run is not recorded here. This amendment is documentation only and does
  not move them.
- **`a9d4b1f` is confirmed on Windows from Viktor's own live run**, not predicted from
  Linux: the panel printed `VALIDATION : … 35.00/100` and the arithmetic matched (50,
  +10 macro, −25 volume divergence); the EV line printed the new wording at +0.14R with
  confidence 38; the decision log's last record carries a summary naming the risk
  reason with no EV sentence; and that record carries
  `code_hash b02137660111…`. The prediction made on Linux held on his machine.
- **`119c8a3` is confirmed on Windows from Viktor's own live run**, not predicted from
  Linux: AEROUSDT 4h at 00:02 on 21 September 2026, decision NO-TRADE (RISK TOO HIGH).
  The panel printed `TREND : BULLISH / STRONG (Score: 100.00/100)` with
  `VALIDATION : WEAK (Score: 35.00/100)` on the line below — the denominator the fix
  added, on the line that had been missing it, beside the one `a9d4b1f` had already
  fixed. `RISK REGIME: UNKNOWN` on that run was checked against `models/risk_model.py`
  and is the documented behaviour of the stop-distance branch, not a defect.
- **Engineering Notes:** through Entry #141 (v1.33), which covers `4629002`. **Ten
  commits behind** — `3a899b5`, `92775ea`, `53394ff`, `982e70f`, `65a0aef`, `a9d4b1f`,
  `6e1baba`, `b869a30`, `119c8a3` and this one — by Viktor's choice, under the standing
  batching rule. (Nine through `119c8a3`; the tenth is this amendment, counted the same
  way the previous version counted itself.) If the independent audit's package includes
  the Notes, regenerate them before building it.
- **Portfolio Document and AI-Attribution Statement:** both current with their scripts.
  `build_portfolio_document.py` was corrected at `6e1baba` and its PDF regenerated in
  that same commit; `build_ai_attribution.py` has not changed since `9a35f1c`, whose
  PDF was regenerated at `c745a67`.
- **Handover check / pre-push hook:** the hook reported `SUMMARY: clean` on the pushes
  of `4629002`, `3a899b5`, `92775ea`, `53394ff` and `982e70f` (Viktor's report), and
  again on the push that carried this session's work — a first attempt had failed on
  DNS, which is not a hook result. **Whether that push carried both `b869a30` and
  `119c8a3` or only the latter was not established**, so nothing here claims a
  per-commit result for either. **Its result on the pushes of `65a0aef`, `a9d4b1f` and
  `6e1baba` was not reported** either, so nothing here claims it was clean on them.

### Resolved this session

- **The once-per-session rewrite of this file**, deferred by `6e1baba` to this session.
  The previous version is in HISTORY verbatim, headings demoted one level.
- **`a9d4b1f`'s and `6e1baba`'s landing facts** folded in above — Windows counts,
  Viktor's live-run confirmation, the new `code_hash`, the re-baselined snapshot.
- **The TREND line's missing denominator, fixed at `119c8a3`** — the second of the two
  commits ruled above, and the one that ruling predicted. A new fixture-free test file of
  4 tests with three negative controls; the denominator is held from the parse tree and
  from running the indicator, each proven load-bearing separately. The whole panel was
  swept afterwards: no other score printed by it is missing its scale.
- **Closed at `6e1baba`, and no longer open items here:** the Portfolio Document's
  "four independent runs … no prior involvement in the build" claim, and README's
  "every raw report from every round is in `docs/audit_reports/`".

### Open items

Items marked **Viktor's call** are his to decide; he writes his position first and
Claude critiques it.

- **Viktor's call — planning the independent audit, or pausing it:** which model, the
  package (the standing default for a fresh Tier-1 audit is the full package), whether
  the auditor sees the scrapped findings, and the instruction for the selected model —
  or whether the round is paused at all, which he raised this session and has not
  ruled. Not started.
- **Found, not checked:** HISTORY's 5 September "The record corrected from the bill"
  says the eleven round-2 observations came from a Qwen run; the
  `round2_kimi_k3_20260902/README.md`, filed later, says they are Kimi's. Which is the
  later word, and whether the earlier one is marked superseded, was not examined.
- **The pre-push hook is installed per clone, not per repository.** After any re-clone
  (including after a machine wipe), run `git config core.hooksPath githooks`;
  `session_handover_check.py` section 6 flags a clone without it.
- **Unrelated, not urgent:** confirm which YH programme permits AI-assisted
  examensarbete work.


## 21 September 2026 (third session) — PHASE7_NEXT.md as it stood at `aafded0`

*Moved here verbatim on 21 September 2026, when PHASE7_NEXT.md was rewritten at the
opening of that day's third session. Every line below the rule is the file's content at
`aafded0` — rewritten at `ebb4e5c` and amended in place at `a530006`, `e3f3d51`,
`afd8460`, `49de810`, `3f263c2` and `aafded0` — unchanged, including its own wording:
"this session" is the first 21 September session (from `635a94e`) together with the
second (from `49de810`), whose work was amended into it in place, and "the commit that
writes this line" and "the documentation commit after it" name `aafded0` or the commit
that made each amendment. Its headings are demoted one level (`#` → `##`, `##` → `###`)
so they nest under this entry; no other character is changed.*

---

## Next step — read this first

*21 September 2026. This file is the project's current-state entry point: it states only
what is true right now and what to do next, and is rewritten each session, not appended
to. Standing rules, ratified specifications and rulings in force live in
docs/PHASE7_DECISIONS.md. The dated record — including this file's previous version,
moved there verbatim this session — lives in docs/PHASE7_HISTORY.md. A citation of this
file written before the 18 September 2026 split — in the Engineering Notes, audit
reports, handovers or any other dated record — refers to content now in one of those
two files; dated records are not edited to say so (DECISIONS, "Ruling, 20 September
2026 — dated records are not edited to follow a move").*

*Kept current commit by commit this session. Each of the code commits planned below
updates this file's own lines for its own landing, in the same commit, so the file does
not fall behind the tip the way it did on 20 September, when `119c8a3` landed after
`b869a30` had written it.*

*A second session opened on 21 September at `49de810`. Its work is amended into this
file in place, commit by commit; the once-per-session rewrite, with the previous
version moved to HISTORY, is owed — deferred to the next session's opening, agreed with
Viktor when his weekly usage stood at 25% remaining.*

### PACE FIRST — read this before the rest of this file

Viktor judged, on his own, that 226 commits across 22 days had become hasty, and
ruled to slow down considerably (15 September 2026). **Do not open a session by
proposing work from "Open items" below, and do not treat it as a queue to clear.**
Ask what he wants to do first.

### Where the project is

This session opened fresh at `635a94e`. Asked what he wanted to do first, Viktor asked
what questions he should put to the engine before backtesting starts: whether its logic
and reasoning are correct, whether it displays the correct information, and whether it
carries dead code or modules that do not work as they should. Claude read the decision
path and most of the input side and reported the findings recorded below. Viktor then
asked Claude to organise the work and start it — "It is up to you" — so the order under
"Work order" is Claude's, under that delegation.

**Nothing here decides the engine's trading rules.** Five findings (4–7, and 16, found
later the same morning) are questions about what the engine should do rather than
defects in what it does; they are listed under
"Viktor's call, before backtesting" and none of the planned commits touches them.

**The independent audit is paused — ruled by Viktor, 21 September, second session:**
"We pause the audit. We work on the engine another four weeks." The four weeks are
fixes and preparing the audit, and none of our own checks is written up as
verification (DECISIONS, "Ruling, 21 September 2026 — the independent audit paused").
The Constitution's step 8 still binds: no backtesting before an independent re-audit.
Claude's two points not adopted, recorded there: no end condition (Claude suggested
deciding again around 19 October), and the no-backtest rule exists only as text.

**Viktor's plan, stated 21 September — a plan, not a ruling:** about four more weeks of
this kind of work — our own review, fixes and improvements — before the next audit,
with no time pressure ("i dont mind working 4 more weeks fixing and improving what we
can for the next audition, there is no time press"). It sits alongside the unruled audit
question above, not in place of it.

**Checked against the Constitution, 21 September, at Viktor's request.** Claude read the
ratified PDF's rules and its "Next Steps" sequence (not its version history or
glossary) against this session's work. Nothing done this session breaks it: each
change was stated before the work, tested, negative-controlled and version-controlled;
Fail Safely (13), Epistemic Honesty (8) and Traceability (6) were strengthened, not
weakened; no rule was touched. **One condition it does impose, and it bears on the
audit question:** its sequence reads "8) Re-audit the items that changed — independent
auditor again, not a self-check by whoever made the fix. 9) Only then … build the
backtesting architecture." None of this session's fixes has been independently
re-audited. Pausing the audit is consistent with the Constitution; pausing it and then
starting backtesting is not. Where it is thinnest: two riders were found mid-work
rather than stated before it (the BUSD suffix in B, `utcnow` in E); items 14 and 15
below were first written as "found sound", which reads as the builder certifying its
own compliance and is reworded; finding 16 may be an existing Item 3 / Item 8 gap,
Unknown until ruled on. Viktor's reading: "we are reviewing everything ourselves and
make adjustments and fixes, i think it is good and important work."

### Ruled this session

- **The order of work is delegated to Claude** (Viktor, 21 September: "Organize a to do
  list and we start working, It is up to you."). The delegation covers ordering and the
  items marked Claude's below; it does not cover the five marked Viktor's.
- **Second session, 21 September:** the audit paused (above); work order F ruled — the
  entry signals CONFIRM the side the ladder chooses (DECISIONS, "Ruling, 21 September
  2026 — the entry signals confirm"). Viktor wrote the conditions; the remaining
  adjustments were delegated to Claude ("Make the adjustments you want and do what is
  best for the engine and the project").
- **The rest of the read waits** (Viktor, 21 September: "we check it after"):
  `data/data_fetcher.py`, `data/validation.py`, `core/decision_log.py` and
  `core/lineage.py` are read after the work list, not before it.

### Where things stand, right now

- **Tip:** the documentation commit filing F's Windows confirmation (a commit cannot
  name its own hash); the one before it is `3f263c2`, work order F. **Tag:** `portfolio-v1` at `99e022e`.
  **Release gate:** open, declared 15 September 2026.
- **Working tree at `635a94e`:** clean — `git status --short` printed nothing
  (Viktor's paste, 21 September, before this session's work began).
- **code_hash:** `44f7296bb9c1a927712797df132eff4114f2782cdebb290d93d0dc86f8e44f78`,
  moved at work order F (`models/entry_model.py`, `models/decision_model.py`,
  `core/engine_core.py`, `core/decision_contract.py`, `models/signal_router.py`,
  `indicators/trend_health.py` — the six files it edits, and no others) from
  `3e76c1c5…`, computed under Python 3.12.3 on the pristine and the applied tree.
  **Confirmed on Windows, AFTER the commit, not before it:** the record of Viktor's live
  run of 21 September 19:24 (AEROUSDT 4h, 30th record in the log) carries
  `44f7296b…`, read by Claude from his disk. The run before committing, asked for in
  the command sequence, did not happen: at the push the log still held 29 records, the
  newest on `3e76c1c5…`. Claude caught it by reading the log, not from a paste. The
  record also shows F's fields as designed — `long_signal` True with an empty blocker
  list, `short_signal` False with "structure is BULLISH TREND, not BEARISH TREND",
  `divergence_direction` "NONE" — and, correctly, no "Separately" reason: the action was
  RISK TOO HIGH (the HVN stop again, finding 6) with the long confirmed. `3e76c1c5…` was
  unmoved by `49de810` — moved at work order E (`live_trading.py`, `structure/structure.py`,
  `indicators/volume_profile.py`) from `ac02a155…`, which `e3f3d51` (C) had moved from
  `ec88cf24…`, which `a530006` (B) had moved from `35718f6b…`. Computed under Python
  3.12.3 on the pristine and the applied tree, not assumed. **All three are confirmed on
  Viktor's Windows machine:** the decision-log records his live runs wrote before
  committing `a530006`, `e3f3d51` and `afd8460` carry `ec88cf24…`, `ac02a155…` and
  `3e76c1c5…`.
- **code_hash is only comparable within one Python minor version.** It hashes `ast.dump`
  output, a CPython implementation detail (`core/code_fingerprint.py`, "WHAT IT DOES NOT
  SURVIVE"). On 20 September a sandbox whose default `python3` was 3.11.15 reported a
  different value on an unmodified tree. **Every `code_hash` claim about this project is
  computed under Python 3.12** (Viktor runs 3.12.10).
- **Golden snapshot:** re-baselined at work order F, three fields ADDED and nothing
  changed, as predicted: `entry.long_signal_blockers` (`[]`),
  `entry.short_signal_blockers` (`["structure is BULLISH TREND, not BEARISH TREND"]`)
  and `trend.divergence_direction` (`"NONE"`). The action, every reason and `run_hash`
  did not move; the fixture's long signal was already True and stays True. Unmoved by
  work order E. Re-baselined before that at `e3f3d51` (C), one field, as predicted:
  `lineage.risk_inputs.detailed_bias` removed, because it never fed the stop or targets.
  No decision field moved and `run_hash` did not move. Previously re-baselined at
  `a9d4b1f`; unmoved by `a530006`, whose pinned-run panel was byte-identical before and
  after.
- **Test suite, moved at work order F** by one new fixture-free file of 21 tests
  (`tests/test_signal_confirms.py`), none of which skips: **549 passed / 0 failed, no
  warnings line** with `pandas_ta`; **414 passed / 124 skipped** without it;
  `run_tests.py` **478 passed / 0 failed / 32 errors**, the 32 unmoved. Linux sandbox,
  `core.autocrlf=true` clone, Python 3.12.3, pinned requirements. **On Windows**, 549 and
  478 / 0 / 32 are confirmed by Viktor proceeding past the steps whose stop conditions
  they were.
  At work order E, by one new fixture-free file of 6 tests, three of
  which skip without `pandas_ta`: **528 passed / 0 failed, and no warnings** with
  `pandas_ta` — the suite's two DeprecationWarnings were the `utcnow()` call E removes;
  **393 passed / 124 skipped** without it; `run_tests.py` **457 passed / 0 failed / 32
  errors**, all 32 fixture-collection `TypeError`s, unmoved. (`e3f3d51` stood at
  522 / 390 / 451, `a530006` at 515 / 383 / 444.)
  Verified in a Linux sandbox on a `core.autocrlf=true` clone under Python 3.12.3,
  pinned requirements. **On Windows:** Viktor's pytest printed 528 passed and no
  warnings line (his paste); `run_tests.py`'s 457 / 0 / 32 is confirmed by his
  proceeding past the step whose stop condition it was.
- **Engineering Notes:** through Entry #141 (v1.33), which covers `4629002`. **Seventeen
  commits behind** — `3a899b5`, `92775ea`, `53394ff`, `982e70f`, `65a0aef`, `a9d4b1f`,
  `6e1baba`, `b869a30`, `119c8a3`, `635a94e`, `ebb4e5c`, `a530006`, `e3f3d51`,
  `afd8460`, `49de810`, `3f263c2` and the documentation commit after it — by Viktor's choice, under the
  standing batching rule. **This count includes the commit that writes it, so every
  later commit adds one until the Notes are regenerated;** it is the line most likely to
  go stale in this file. If the independent audit's package includes the Notes,
  regenerate them before building it.
- **Portfolio Document and AI-Attribution Statement:** both current with their scripts.
- **Pre-push hook:** reported `SUMMARY: clean` on the pushes of `635a94e`, `ebb4e5c`,
  `a530006`, `e3f3d51`, `afd8460` and `49de810` — Viktor pasted all six outputs, so those are
  confirmed, not reported. On `3f263c2` the output was not pasted; the push landed (the
  sandbox fetched it), and the hook stops a push on any finding, so clean is inferred,
  not seen. Earlier record, carried unchanged:
  clean on the pushes of `4629002`, `3a899b5`, `92775ea`, `53394ff` and `982e70f`
  (Viktor's report) and on the push that carried `119c8a3`; whether that push also
  carried `b869a30` was not established; the result on the pushes of `65a0aef`,
  `a9d4b1f` and `6e1baba` was not reported.
- **Windows live-run confirmations of `a9d4b1f` and `119c8a3`:** recorded in full in the
  previous version of this file, now HISTORY's 21 September entry.

### Resolved this session

- **Four notes that existed only in the 20 September chat, filed here:** the hook's clean
  result on `635a94e` (above); the Engineering Notes line counting itself (above); the
  obligation to rewrite this file if this session did substantive work, which `ebb4e5c`
  did; and the autocrlf observation, which stays open (below).
- **The once-per-session rewrite of this file.** The previous version — written at
  `b869a30`, amended at `635a94e` — is in HISTORY verbatim, headings demoted one level,
  proven by un-demotion.

### Review findings, 21 September 2026

Read at `635a94e` from Viktor's disk and from an autocrlf clone, byte-identical for every
file compared. **Every finding below comes from reading the code. None has been
reproduced by running the engine**, and each says how far its reachability was checked.

**The panel prints something that was not computed**

1. **Two panel lines name AERO whatever the symbol** — `core/panel_render.py:553` and
   `:599`. On BTCUSDT the BTC context is always skipped (`core/engine_core.py:754`), so
   every BTCUSDT run prints "AERO analysis above is unaffected." Sequence item 12 fixed
   the same string in `models/decision_model.py` and missed these two. **Fixed at work
   order B:** both sentences name the run's asset through `asset_name()`, now the one
   function the panel and the reasoning share.
2. **TREND and VALIDATION can print `Score: nan/100`** — `panel_render.py:696`, `:703`.
   The router sends NaN for a missing value on purpose (`models/signal_router.py:326`,
   `:444`); the price lines got a guard at Round 6 F3, these two did not, including in
   `119c8a3` and `a9d4b1f`, which edited exactly these lines. Same shape in
   Decision Reasoning's "trend strength nan/100" (`decision_model.py`,
   `_determine_final_action`). How often the value is missing on a live run: not
   checked. **Fixed at work order B:** every score line goes through one helper,
   `_score_text()`, which prints "not computed" for a value that is not finite; the
   reasoning sentence says "trend strength not computed".
3. **Entry, confidence and trade-quality scores print `0.00` when absent** —
   `panel_render.py:201–203`, and the BTC-adjusted confidence the same way. Latent: the
   router always sets all three (`signal_router.py:369`, `:441`, `:442`). **Fixed at
   work order B:** absent is NaN and prints "not computed".

**Viktor's call, before backtesting** — he writes his position first; Claude critiques.

4. **The panel gives an entry ZONE but measures everything from the last close.** Stop,
   T1–T3 and all three R:R values come from `current_price` (`engine_core.py:999`); the
   zone is EMA20–EMA50. LONG is authorised without price in the zone (entry score ≥ 70 is
   reachable at NEAR ZONE), and CONSERVATIVE LONG has no zone condition at all. The
   printed R:R holds only for an entry at the current price. There is no single entry
   price on the panel. A backtest must fill somewhere, so this needs ruling first.
5. **A NEUTRAL bias still prints a full plan.** The plan's direction comes from
   `bias_score >= 0` (see 8), so a score between −20 and +20 prints a long- or
   short-shaped stop and targets under a NEUTRAL bias with no direction box; exactly 0
   prints a long.
6. **The stop is pulled to the 75-day volume point of control, with no distance limit.**
   `structural_level=hvn` (`engine_core.py:1040`); for a long the stop is
   min(HVN, ATR stop). The HVN is the single highest-volume bin of the whole 450-candle
   frame (`indicators/volume_profile.py`, 50 bins) — about 75 days on 4h. A trend that
   has moved away from its point of control therefore gets its stop there, and past 15%
   the risk check fails: NO-TRADE (RISK TOO HIGH), RISK REGIME UNKNOWN.
   **Seen on three live runs and the pinned fixture since, each checked against the
   record, not inferred.** The 05:51 and 06:18 runs (the second on the new candle that
   opened 04:00 UTC) both carry a stop equal to the HVN, 0.549596 — at 06:18, 17.6%
   below a price of 0.6666, NO-TRADE again. The first of them in detail: Viktor's live
   run of 21 September 05:28 (AEROUSDT 4h, before committing `a530006`): the stop,
   0.549596, is the HVN exactly, 18.2% below a price of 0.6719, so NO-TRADE. The ATR stop
   it replaced works out at about 0.6301, 6.2% below price — computed by Claude from that
   record's ATR (0.022209), bias score (65.08), trend health (97) and HIGH VOLATILITY;
   the engine does not print it. By the decision rules — read, not run — that run would
   otherwise have been CONSERVATIVE LONG. And the pinned golden fixture is the same case:
   stop = HVN = 0.6421571, 19.9% below 0.80173175, NO-TRADE (RISK TOO HIGH). How often
   this vetoes a setup across many runs was not measured.
   **Dependency added at work order F:** the confirmation gate no longer blocks on HVN
   proximity, on the reasoning that this stop already acts on that area. If this
   finding is ruled to stop pulling the stop to the HVN, nothing checks HVN proximity.
7. **Indicator values beyond 5σ are silently replaced by the previous bar's.**
   `indicators/indicators.py:105–110`, inside `clean_series`, which EMA, RSI, ADX,
   SuperTrend and ATR all pass through.
   Nothing records the replacement — unlike volume spikes (`:746`), which are kept and
   flagged. At the decision bar the replaced value becomes a reported indicator
   *failure*. The mean and standard deviation span the whole frame, so a backtest that
   computes indicators once over its history would leak future bars into past
   decisions. Reachability on live data: not measured.

**Finding 16, added the same morning — the decision is made on the candle still
forming.** Numbered 16 because 14 and 15 were already used below. Found from the record,
then confirmed in the code: Viktor's live runs at 05:28 and 05:51 (21 September) carry
the same last candle, `2026-09-21 00:00` UTC — the 4h candle that closes at 04:00 UTC,
06:00 his time — with a different input hash and a different price (0.6719, then
0.6714). `data/data_fetcher.py` requests MEXC klines, reads and discards `close_time`,
and keeps every row, the live one included. So on a live run the close, the volume, and
every indicator at the decision bar come from a partial candle, and the panel can
change within the same candle. A backtest run on closed candles would be testing a
different engine from the one run live — the volume-based readings most of all. Which
candle counts is a rule, not a defect to patch, so it sits here with 4–7.

**Code that cannot run, or runs and decides nothing** — Claude's

8. **A direction check that can never match** — `models/risk_model.py:240` compares
   `detailed_bias` to "LONG"/"SHORT"; its only caller passes "BULLISH CONFIRMED" /
   "BEARISH CONFIRMED" / "NEUTRAL" (`engine_core.py:707`). The A1/A2 shape, surviving in
   a second file. Not a wrong answer today: raw bias comes from the same score, so an
   authorised action and its plan cannot point opposite ways.
9. **An unreachable fallback that would be wrong if reached** — `risk_model.py:278–282`,
   `:296–297`. `bias_score` is clipped to ±100 (`models/bias_engine.py:448`), so the ATR
   stop is always on the correct side. If the branch ever ran it would leave the stop on
   the wrong side while the targets used a different distance. **Fixed at work order
   C**, with 8: the parameter is removed, the direction is stated as the sign of
   `bias_score`, a non-finite score is refused, and the fallback raises. Shown on the
   pre-fix code: `bias_score` 400 returned a long with its stop at 101.04 above a price
   of 100, and `validate_risk_parameters` passed it (True, "OK", NORMAL RISK).
10. **Nothing at runtime checks that the stop sits on the correct side.** The panel's
    R:R uses `abs()` (`panel_render.py:171`, `:177–179`); `_refuse_incoherent_plan`
    reads target order only; `core/decision_contract.py` runs in tests and checks shape,
    not values. **Closed at work order C** by putting the check at the only producer —
    see D under "Work order".
11. **`long_signal` / `short_signal` are recorded and decide nothing.** Computed every run
    (`generate_entry_signals`), carried into the decision object, the log and the
    simulated order; no decision reads them. They are False whenever
    `reversal_strength > 0` — e.g. within 3% of the HVN — so the record can show
    `long_signal: False` beside an AGGRESSIVE LONG. → F.
    **Ruled and fixed at work order F:** the signals now CONFIRM the side the ladder
    chooses; an unconfirmed trade is `NO-TRADE (SIGNAL UNCONFIRMED)`. Conditions:
    structure matches the side, the trend is not exhausted, no momentum divergence
    points against the trade. Macro, CONFIRMED, trend health and HVN proximity no
    longer take part. `decision_model`'s own direction-blind divergence veto on the
    upper tiers is removed, so there is one divergence rule. Each side's reasons are
    recorded (`long_signal_blockers` / `short_signal_blockers`), and the trend block
    now carries `divergence_direction`. Full account: DECISIONS, "Ruling, 21 September
    2026 — the entry signals confirm".

**Fabricated defaults still standing** — Claude's

12. **`live_trading.py`, `_build_simulated_order`:** zone 0.0, stop 0.0, targets
    (0, 0, 0), current price 0.0, `risk_reason` "OK". The class Round 6 F3 fixed in the
    router and the panel. Reachable only through `test_live.py`, a manual script.
    **Fixed at work order E:** absent is None (JSON null). Also fixed there, found while
    scoping: its timestamp called `utcnow()`, deprecated since Python 3.12 and the
    source of the suite's two DeprecationWarnings.
13. **`structure/structure.py:544–546`:** `.get("hvn", 0.0)`, `.get("lvn", 0.0)`,
    `.get("regime", "NEUTRAL STRUCTURE")`. Latent — the keys are always present.
    **Fixed at work order E:** indexed directly, so a missing key raises. Also corrected
    there: `indicators/volume_profile.py`'s docstring still said "NOT FIXED HERE" about
    a fill that sequence item 15 had fixed.

**Claude's claims, open to the independent auditor** — first written as "Checked and
found sound", reworded 21 September: the Constitution does not let the builder certify
its own compliance, so these are claims with their evidence named, not findings.

14. Every engine module is reachable from `main.py` except `core/decision_contract.py`
    (test-side by design) and `utils/decision_log_backup.py` (a standalone tool with its
    own `__main__`). No orphaned module.
15. `_refuse_incoherent_plan` cannot fire today (see 8) — correctly so: it is a tripwire
    against a future change, which is what its docstring says it is. Claude's reading
    (the argument is in 8), not a finding.

**Found at work order F, 21 September, second session**

17. **Macro still counts twice in the CONSERVATIVE branches.** `decision_model`'s
    CONSERVATIVE LONG requires `macro_bias == "BULLISH"`, CONSERVATIVE SHORT
    `"BEARISH"` — a hard requirement on evidence already weighted into `bias_score`,
    the double count Viktor removed from the signal at F. Not changed at F, so that
    each change to which trades are taken lands in its own commit. → G.
18. **The bias state machine now gates no trade.** A consequence of F (Viktor dropped the
    CONFIRMED requirement so the signal follows `raw_bias`, as `decision_model` does).
    `detailed_bias` still feeds `exit_model`'s "bias state changed" flag and the
    persisted state; nothing that decides reads it. Recorded, nothing removed. Whether
    its persistence requirement should gate anything is Viktor's call; not started.

### Work order — Claude's, under Viktor's delegation

Each code commit is its own commit and updates this file for its own landing.

- **A — landed at `ebb4e5c`.** The findings above into the repo; the HISTORY move.
- **B — landed at `a530006`.** Panel display (1, 2, 3). Also found while scoping it:
  `asset_name`'s suffix list tried "USD" before "BUSD", so a BUSD pair lost only "USD";
  fixed in the same function. **Confirmed on Windows** by Viktor's live run before the
  commit (AEROUSDT 4h, 21 September 05:28): every score line printed a number with its
  "/100", no "nan" and no "not computed" anywhere, and the BTC section named AERO.
- **C — landed at `e3f3d51`.** `risk_model` dead paths (8, 9). Output-invariant on
  every decision field; the one golden change is the lineage record above. **Confirmed
  on Windows** by the record of Viktor's live run before the commit (05:51): it carries
  `code_hash ac02a155…` and a `risk_inputs` block without `detailed_bias`. **A wrong
  prediction, recorded:** Claude told him that run would print exactly the 05:28
  numbers, because it was before 06:00 and "the same candle". It printed a different
  price and targets. The patch was not the cause — the stop was unchanged and each
  target sat exactly 1R, 2R and 3R from the new price — the prediction was: it assumed
  the engine reads closed candles without checking. That is how finding 16 was found.
- **D — folded into C, not a separate commit.** Finding 10 asked for one check every plan
  passes. `calculate_stop_targets` is the only producer of a stop and targets, and since
  C it refuses a stop on the wrong side of price; the targets are then measured from a
  positive distance, so they cannot be on the wrong side either. The check now sits at
  the source, which is the structural form of the fix. The `abs()` in the panel's R:R
  and in `validate_risk_parameters` stays — harmless once no wrong-side stop can reach
  them. Claude's call under the delegation.
- **E — landed at `afd8460`.** Remaining fabricated defaults (12, 13). No decision field
  moves; golden snapshot unmoved; `live_trading.py` is not on the engine's path.
  **Confirmed on Windows** by the record of Viktor's 06:18 run before the commit:
  `code_hash 3e76c1c5…`. That run's REGIME, STRUCTURE, VOLUME and VALIDATION lines
  differed from 05:51 because a new candle had opened at 04:00 UTC — not because of E,
  whose pinned-run panel was byte-identical before and after in the sandbox.
- **Filed after E, documentation only:** the evidence above that existed only in chat —
  E's Windows confirmation, the hook result on `afd8460`, the third HVN-vetoed run,
  Viktor's four-week plan, and the Constitution check.
- **F — landed in the commit that writes this line.** The signals confirm (11): Viktor's
  ruling and conditions, Claude's delegated adjustments, all in DECISIONS. The golden
  snapshot gained three fields and changed none; no action in the 29 live-log records
  would change. Negative controls, each restored and confirmed with `cmp`: restoring
  the ladder's divergence veto, making the gate a no-op, making divergence
  direction-blind, dropping the appended risk-and-signal reason, letting a missing
  signal pass, re-adding `macro_bias`, and ignoring a self-contradicting record — each
  failed the tests guarding it. Existing tests changed: two fixtures now carry complete
  signal records (without them the "cannot open a direction" tests would pass
  vacuously, refused by the gate for missing data) and one fingerprint test retargeted
  at the comparison without `and not divergence`. **Landed at `3f263c2`; confirmed on
  Windows after the commit** (see code_hash above). **A wrong prediction, recorded:**
  Claude's expected `git status --short` listed `tests/test_signal_confirms.py` last;
  git sorts by path, so it prints before `test_summary_…`. Same files, same states.
- **G — macro in the CONSERVATIVE branches (17).** Claude's, under the delegation. Changes
  which trades are taken; scoped before any diff; the live log checked first, as for F.
- **Then:** the deferred read (`data_fetcher`, `validation`, `decision_log`, `lineage` —
  `data_fetcher`'s live fetch path was read for finding 16, nothing else of it), and
  Viktor's rulings on 4–7 and 16 before any backtest is designed.

### Open items

Items marked **Viktor's call** are his to decide; he writes his position first and
Claude critiques it.

- **Viktor's call — findings 4, 5, 6, 7 and 16 above**, before backtesting. Not
  started.
- **The independent audit — paused, ruled 21 September.** When it is planned, still
  Viktor's: which model, the package (the standing default for a fresh Tier-1 audit is
  the full package), whether the auditor sees the scrapped findings, and the
  instruction for the selected model. No backtesting before it.
- **Claude's — the running change list for the audit.** Every change since the last
  audit, one line per commit: what changed, which finding it closes, which tests
  guard it. Becomes the auditor's scope. Not started.
- **Viktor's call — finding 18** (whether the bias state machine should gate anything).
  Not started.
- **Found, not resolved — which clone produced the Linux counts at `119c8a3`.** An
  autocrlf clone passes `tests/test_pinned_source.py` and gives 504 / 0 (confirmed again
  this session). The earlier text described the `119c8a3` Linux counts as coming from a
  default LF clone, which by the standing note should fail that test. The previous
  version of this file said the clone type was not recorded rather than restate it.
- **Found, not checked:** HISTORY's 5 September "The record corrected from the bill"
  says the eleven round-2 observations came from a Qwen run; the
  `round2_kimi_k3_20260902/README.md`, filed later, says they are Kimi's. Which is the
  later word, and whether the earlier one is marked superseded, was not examined.
- **The pre-push hook is installed per clone, not per repository.** After any re-clone
  (including after a machine wipe), run `git config core.hooksPath githooks`;
  `session_handover_check.py` section 6 flags a clone without it.
- **Unrelated, not urgent:** confirm which YH programme permits AI-assisted
  examensarbete work.


## 21 September 2026 (fifth session) — PHASE7_NEXT.md as it stood at `4e2b1c8`

*Moved here verbatim on 21 September 2026, when PHASE7_NEXT.md was rewritten at the
opening of that day's fifth session — the rewrite owed at the fourth session's close.
Every line below the rule is the file's content at `4e2b1c8` — rewritten at `cb659f1`
and amended in place at `1cc2142`, `9c4917c`, `05a12c7`, `2c7a7d1`, `5d3a4b4` and
`4e2b1c8` — unchanged, including its own wording: "this session" is the third
21 September session (from `aafded0`) together with the fourth, whose work was amended
into it in place, and "the commit that writes this line" names `4e2b1c8` or the commit
that made each amendment. Its headings are demoted one level (`#` → `##`, `##` → `###`)
so they nest under this entry; no other character is changed.*

---

## Next step — read this first

*21 September 2026, third session; amended in place in the fourth by commit 4 of the
six (the rewrite this file owes each session is owed at the fourth session's close). This file is the project's current-state entry point:
it states only what is true right now and what to do next, and is rewritten each
session, not appended to. Standing rules, ratified specifications and rulings in force
live in docs/PHASE7_DECISIONS.md. The dated record — including this file's previous
version, moved there verbatim this session — lives in docs/PHASE7_HISTORY.md. A citation
of this file written before the 18 September 2026 split — in the Engineering Notes,
audit reports, handovers or any other dated record — refers to content now in one of
those two files; dated records are not edited to say so (DECISIONS, "Ruling, 20
September 2026 — dated records are not edited to follow a move").*

*Each code commit updates this file's own lines for its own landing, in the same
commit, so the file does not fall behind the tip.*

### PACE FIRST — read this before the rest of this file

Viktor judged, on his own, that 226 commits across 22 days had become hasty, and
ruled to slow down considerably (15 September 2026). **Do not open a session by
proposing work from "Open items" below, and do not treat it as a queue to clear.**
Ask what he wants to do first.

### Where the project is

On 21 September Viktor asked what to put to the engine before backtesting starts:
whether its logic is correct, whether it displays the correct information, and whether
it carries dead code. Claude read the decision path and most of the input side; the
findings are below. Viktor delegated the order of the work to Claude. Work orders A–F
have landed (below). In the third session Viktor chose four items ahead of G: the
deferred read, the running change list for the audit, two record questions and the
sandbox lessons into the patch-delivery skill — all done (below). G is next in
Claude's order. In the fourth session Viktor chose commits 4–6 of the six ahead of G;
commit 4 is the commit that writes this line.

**Nothing Claude does under that delegation decides the engine's trading rules.**
Findings 4–7, 16 and 18 are questions about what the engine should do; they are
Viktor's, and none of the planned commits touches them. F changed which trades are
taken, and Viktor ruled it (DECISIONS, "Ruling, 21 September 2026 — the entry signals
confirm").

**The independent audit is paused** — ruled by Viktor, 21 September: "We pause the
audit. We work on the engine another four weeks." The four weeks are fixes and
preparing the audit, with no time pressure, and none of our own checks is written up as
verification (DECISIONS, "Ruling, 21 September 2026 — the independent audit paused").
**The Constitution's step 8 binds:** "Re-audit the items that changed — independent
auditor again, not a self-check by whoever made the fix. 9) Only then … build the
backtesting architecture." No engine change since the last independent round (round 6
fix-verification, 14 September) has been independently re-audited, so **no backtesting
before an independent re-audit.** Claude's two points not adopted, recorded in that
ruling: no end condition (Claude suggested deciding again around 19 October), and the
no-backtest rule exists only as text.

### Ruled — in force

- **The order of work is delegated to Claude** (Viktor, 21 September: "Organize a to do
  list and we start working, It is up to you."). It covers ordering and the items marked
  Claude's below; it does not cover the items marked Viktor's.
- **The audit is paused**, and **work order F is ruled** — both above, both in DECISIONS.
- **The rest of the read waits** (Viktor, 21 September: "we check it after"):
  `data/data_fetcher.py`, `data/validation.py`, `core/decision_log.py` and
  `core/lineage.py` are read after the work list, not before it.

### Where things stand, right now

- **Tip:** the commit that writes this line (a commit cannot name its own hash) —
  commit 4 of the six, `core/lineage.py`: findings 23 and 24 and the archive's half of
  19. Before it: `5d3a4b4` (the third session's documentation close), `2c7a7d1` (finding 22), `05a12c7` (findings 19–21), `9c4917c` (the
  direction-box tests), `1cc2142` (the deferred read and the audit change list). F
  itself is `3f263c2`. **Tag:** `portfolio-v1` at `99e022e`. **Release gate:** open, declared
  15 September 2026.
- **Working tree at `2c7a7d1`:** clean — the pre-push hook's section 1, which is
  `git status --short`, printed "none" on that push (Viktor's paste, third session of
  21 September). The same at `1cc2142` and `cb659f1`. On the push of `5d3a4b4` the
  hook printed `SUMMARY: clean` (Viktor's message opening the fourth session).
- **code_hash:** `4fe5084e47157289326776ffca85671548608fc409b614c7e11c2fc687c71d66`,
  moved by the commit that writes this line (`core/lineage.py`) from `82c14ef9…`;
  computed under Python 3.12.3 on the pristine and the applied tree. **Windows
  confirmation owed** to the live run in that commit's command sequence, before its
  `git commit`; filed by the next commit. `82c14ef9…` was moved at `2c7a7d1` (`core/decision_log.py`, finding 22) from `f691c4d8…`, which
  `05a12c7` had moved from `44f7296b…`; both computed under Python 3.12.3 on the
  pristine and the applied tree. Unmoved by the commit that writes this line
  (documentation only), `5d3a4b4`. **Confirmed on Windows, before the commit:** Viktor's live run
  of 21 September 22:09 on `2c7a7d1`'s applied tree (AEROUSDT 4h, NO-TRADE (RISK TOO
  HIGH), the 31st record) carries `82c14ef9…`. Claude read it from his disk before the
  commit step: the 30 records before it byte-identical to the copy taken at `1cc2142`;
  the new record strict JSON (no NaN or Infinity token); `module_constants` holding
  `BTC_STRESS_PENALTY` 15.0, `AVG_REWARD_R` 2.0 and `EV_BREAKEVEN_BAND_R` 0.3; the panel
  printed "Decision logged to" and the SETUP DIRECTION box read LONG on a NO-TRADE run.
  **Not exercised on Windows:** the run had no non-finite value, so the record holds no
  `null` at all — finding 19's conversion is evidenced on Linux only, by
  `tests/test_decision_log_record_format.py`. `f691c4d8…` (`05a12c7`) was never run on
  its own; the 22:09 run carries all of its code. `44f7296b…` was moved at F (`3f263c2`)
  from `3e76c1c5…`, Python 3.12. **Confirmed on Windows** by the
  decision-log record of Viktor's live run of 21 September 19:24 (AEROUSDT 4h, the 30th
  record), read by Claude from his disk; unmoved by `aafded0`, `cb659f1`, `1cc2142` and
  the direction-box tests commit.
- **code_hash is only comparable within one Python minor version.** It hashes `ast.dump`
  output, a CPython implementation detail (`core/code_fingerprint.py`, "WHAT IT DOES NOT
  SURVIVE"). **Every `code_hash` claim about this project is computed under Python 3.12**
  (Viktor runs 3.12.10).
- **Golden snapshot:** unmoved by the commit that writes this line, as predicted: the
  archive's bytes are unchanged for a payload with no non-finite float (checked on all
  22 archives in Viktor's `logs/archive`, re-serialised under both codes, Linux).
  Re-baselined at `2c7a7d1`, finding 22,
  seven leaves and nothing else: `lineage.run_hash` and `provenance.run_hash`
  (`c210b69e…` → `51c8f3df…`), `lineage.archive.path` and `provenance.archive_path`
  (the archive is named by `run_hash`), and three added under
  `provenance.module_constants.models.decision_model` — `DecisionModel.AVG_REWARD_R`
  2.0, `DecisionModel.BTC_STRESS_PENALTY` 15.0, `DecisionModel.EV_BREAKEVEN_BAND_R`
  0.3. No decision field moved. **An incomplete prediction, recorded:** Claude named
  `run_hash`, `archive.path` and `archive_path` beforehand and missed the three
  `module_constants` leaves — the change itself — and that `run_hash` sits in two
  places. Before this, re-baselined at F (three fields added).
- **Test suite at the commit that writes this line** — moved by 12 fixture-free tests:
  11 in the new `tests/test_lineage_against_record.py` and 1 appended to
  `tests/test_lineage.py`, which skips without `pandas_ta`: **578 passed / 0 failed, no
  warnings line** with `pandas_ta`; **441 passed / 126 skipped** without it;
  `run_tests.py` **507 passed / 0 failed / 32 errors**, all 32 fixture-collection
  `TypeError`s, unmoved. Linux sandbox, autocrlf clone, Python 3.12.3, pinned
  requirements, applied tree; on Windows, the stop conditions of its command sequence.
  At `2c7a7d1`: 566 / 430 with 125 skipped / 495. Before that: 555 / 420 / 484 at `9c4917c`,
  563 / 428 / 492 at `05a12c7`. Linux sandbox, `core.autocrlf=true` clone, Python
  3.12.3, pinned requirements. **On Windows**, the pytest and `run_tests.py` counts of
  all three commits (555 and 484 / 0 / 32; 563 and 492 / 0 / 32; 566 and 495 / 0 / 32)
  are confirmed by Viktor proceeding past the steps whose stop conditions they were. At
  `3f263c2` it stood at 549 / 414 / 478.
- **Engineering Notes:** through Entry #141 (v1.33), which covers `4629002`. **Twenty-four
  commits behind** — `3a899b5`, `92775ea`, `53394ff`, `982e70f`, `65a0aef`, `a9d4b1f`,
  `6e1baba`, `b869a30`, `119c8a3`, `635a94e`, `ebb4e5c`, `a530006`, `e3f3d51`,
  `afd8460`, `49de810`, `3f263c2`, `aafded0`, `cb659f1`, `1cc2142`, `9c4917c`,
  `05a12c7`, `2c7a7d1`, `5d3a4b4` and the commit that writes this line — by
  Viktor's choice, under the standing batching rule. **This count includes the commit
  that writes it, so every later commit adds one until the Notes are regenerated.** If
  the independent audit's package includes the Notes, regenerate them before building
  it.
- **Portfolio Document and AI-Attribution Statement:** both current with their scripts.
- **README.md:** brought current at `cb659f1` — the paused audit, and what backtesting
  now waits on — and its two test-count lines again in the commit that writes this line
  (566 / 430 with 125 skipped / 495, the counts at `2c7a7d1`). The hook reported it four
  commits behind on the push of `2c7a7d1`; the counts were the stale part. Its two
  test-count lines again in the commit that writes this line (578 / 441 with 126
  skipped / 507).
- **Pre-push hook:** `SUMMARY: clean` on the pushes of `2c7a7d1` (which carried
  `9c4917c` and `05a12c7`), `1cc2142`, `cb659f1` and `aafded0` — Viktor pasted all four
  in the third session of 21 September, so confirmed, not reported. On `cb659f1` its section 5 showed README.md touched at the tip, 0 commits since, as
  predicted. Clean, and pasted, on `635a94e`, `ebb4e5c`, `a530006`, `e3f3d51`,
  `afd8460` and `49de810`. On `3f263c2` the output was not pasted; the push landed and
  the hook stops a push on any finding, so clean is inferred, not seen. The earlier record is in HISTORY.

### Carried lesson — the live run comes BEFORE the commit

At F the live run asked for in the command sequence did not happen before the commit:
at the push the log still held 29 records, the newest on the old `code_hash`. Claude
caught it by reading the log, not from a paste. Viktor's 19:24 run came after the
commit. **On the next change that touches the decision path (G is one), the live run
and the panel read happen before `git commit`, and Claude checks the decision-log
record for the new `code_hash` before the commit step, not after the push.** Never
predict live numbers; check the record. **Followed at `2c7a7d1`** (not a decision-path
change, but it changes what the log records): the command list stopped at the live
run, Claude read the record, and only then gave the commit steps; nothing was pushed
before the check.

### Sandbox practice — learned 21 September, second session

- Set `git config core.autocrlf true` in the clone and re-check out; a `-c` flag on
  `git clone` does not persist.
- Run negative controls with `PYTHONDONTWRITEBYTECODE=1`.
- The golden updater writes LF with no final-newline handling of its own; restore CRLF
  and the original ending by hand before diffing.
- A file re-written to the outputs folder under the same name once reached Viktor's
  disk as the OLD version. Use a new file name for each version, and always read
  deliveries back.
- `git status --short` sorts by path; predict the order that way.

### Review findings, 21 September 2026

Read at `635a94e` from Viktor's disk and from an autocrlf clone. **Every finding comes
from reading the code; none was reproduced by running the engine** unless it says so.
The full text of each fixed finding, with its evidence, is in HISTORY's entry for this
file as it stood at `aafded0`.

**Fixed** — one line each

1. Two panel lines named AERO whatever the symbol — fixed at B (`a530006`).
2. TREND and VALIDATION could print `Score: nan/100` — fixed at B.
3. Absent entry, confidence and trade-quality scores printed `0.00` — fixed at B.
8. `risk_model`'s direction check could never match — fixed at C (`e3f3d51`).
9. An unreachable fallback that would put the stop on the wrong side — fixed at C.
10. Nothing at runtime checked the stop's side — closed at C, at the only producer (D).
11. `long_signal` / `short_signal` decided nothing — ruled and fixed at F (`3f263c2`):
    they now CONFIRM the side the ladder chooses; unconfirmed is `NO-TRADE (SIGNAL
    UNCONFIRMED)`.
12. `live_trading.py`'s simulated order fabricated zeros and "OK" — fixed at E
    (`afd8460`), with its `utcnow()` call.
13. `structure/structure.py`'s `.get(…, default)` on always-present keys — fixed at E.

**Viktor's call, before backtesting** — he writes his position first; Claude critiques.

4. **The panel gives an entry ZONE but measures everything from the last close.** Stop,
   T1–T3 and all three R:R values come from `current_price` (`engine_core.py:999`); the
   zone is EMA20–EMA50. LONG is authorised without price in the zone (entry score ≥ 70 is
   reachable at NEAR ZONE), and CONSERVATIVE LONG has no zone condition at all. The
   printed R:R holds only for an entry at the current price. There is no single entry
   price on the panel. A backtest must fill somewhere, so this needs ruling first.
5. **A NEUTRAL bias still prints a full plan.** The plan's direction comes from
   `bias_score >= 0` (`models/risk_model.py`, since C), so a score between −20 and +20
   prints a long- or short-shaped stop and targets under a NEUTRAL bias with no
   direction box; exactly 0 prints a long.
6. **The stop is pulled to the 75-day volume point of control, with no distance limit.**
   `structural_level=hvn` (`engine_core.py:1040`); for a long the stop is
   min(HVN, ATR stop). The HVN is the single highest-volume bin of the whole 450-candle
   frame (`indicators/volume_profile.py`, 50 bins) — about 75 days on 4h. A trend that
   has moved away from its point of control therefore gets its stop there, and past 15%
   the risk check fails: NO-TRADE (RISK TOO HIGH), RISK REGIME UNKNOWN. Seen on Viktor's
   live runs of 21 September at 05:28, 05:51 and 06:18 and on the pinned golden fixture,
   each checked against the record (details in HISTORY); the 19:24 run's action was again
   RISK TOO HIGH on the HVN stop. How often this vetoes a setup across many runs was not
   measured. **Dependency added at F:** the confirmation gate no longer blocks on HVN
   proximity, on the reasoning that this stop already acts on that area. If this finding
   is ruled to stop pulling the stop to the HVN, nothing checks HVN proximity.
7. **Indicator values beyond 5σ are silently replaced by the previous bar's.**
   `indicators/indicators.py:105–110`, inside `clean_series`, which EMA, RSI, ADX,
   SuperTrend and ATR all pass through. Nothing records the replacement — unlike volume
   spikes (`:746`), which are kept and flagged. At the decision bar the replaced value
   becomes a reported indicator *failure*. The mean and standard deviation span the
   whole frame, so a backtest that computes indicators once over its history would leak
   future bars into past decisions. Reachability on live data: not measured.
16. **The decision is made on the candle still forming.** Found from the record, then
    confirmed in the code: Viktor's live runs at 05:28 and 05:51 (21 September) carry
    the same last candle, `2026-09-21 00:00` UTC, with a different input hash and price.
    `data/data_fetcher.py` requests MEXC klines, reads and discards `close_time`, and
    keeps every row, the live one included. So on a live run the close, the volume and
    every indicator at the decision bar come from a partial candle, and the panel can
    change within the same candle. A backtest on closed candles would test a different
    engine from the one run live. Which candle counts is a rule, not a defect to patch.
18. **The bias state machine gates no trade since F.** Viktor dropped the CONFIRMED
    requirement so the signal follows `raw_bias`, as `decision_model` does.
    `detailed_bias` still feeds `exit_model`'s "bias state changed" flag and the
    persisted state; nothing that decides reads it. Recorded, nothing removed. Whether
    its persistence requirement should gate anything is Viktor's call.

**Claude's, open**

17. **Macro still counts twice in the CONSERVATIVE branches.** `decision_model`'s
    CONSERVATIVE LONG requires `macro_bias == "BULLISH"`, CONSERVATIVE SHORT
    `"BEARISH"` — a hard requirement on evidence already weighted into `bias_score`,
    the double count Viktor removed from the signal at F. Left out of F so that each
    change to which trades are taken lands in its own commit. → G.

**Found in the deferred read, 21 September, third session** — Claude's

`data/data_fetcher.py`, `data/validation.py`, `core/decision_log.py` and
`core/lineage.py`, read at `cb659f1` in full, with their call sites in
`core/engine_core.py`. From reading the code, except where a line says it was checked
against the live log. None changes a decision. 19–24 fixed since (below); 25–27 open.

19. **The decision log writes bare `NaN`, which is not JSON.** `decision_log.write()`
    calls `json.dumps` with its default `allow_nan=True`, so a NaN in the decision object
    is written as the token `NaN`. Python reads it back; a strict JSON reader (`jq`,
    JavaScript's `JSON.parse`) rejects the whole line. The module docstring claims the
    format is "readable by anything". **Checked against Viktor's live log:** 1 of its 30
    records (6 September) carries `"swing_struct": NaN`. Reachable today — the router
    emits NaN for a value not located, on purpose (`models/signal_router.py`,
    `_finite_or_nan`). The archive's JSON (`lineage.write_archive`) has the same shape.
    **Fixed for the decision log at `05a12c7`:** every
    non-finite float is written as `null`, and `allow_nan=False` keeps a bare NaN out.
    Records already in the log keep their NaN; `read()` still accepts them. **The
    archive's half fixed by the commit that writes this line**, with the same
    sanitiser (`decision_log._json_safe`). Latent there: only `meta` can hold a float,
    and no fingerprinted constant is non-finite today.
20. **`decision_log.read()` drops any line it cannot parse, silently.** Its comment
    says the case is "a torn final line"; the code skips a damaged line anywhere in the
    file and counts nothing, so a corrupted middle record vanishes from the history it
    returns. **Fixed in the same commit as 19:** `read_with_report()` returns the
    skipped line numbers; `read()` still skips and now logs them.
21. **`decision_log`'s module docstring says the record's source is "the pinned
    directory".** Since the provenance change the engine records the literal
    `"pinned"`, on purpose (`core/engine_core.py`, the `provenance` block). Stale
    docstring. **Corrected in the same commit as 19.**
22. **The readable half of the fingerprint misses three named constants.**
    `FINGERPRINTED_MODULES` lists `DecisionModel.BTC_ADJUSTMENT_CAP` but not its
    sibling `DecisionModel.BTC_STRESS_PENALTY`, nor `AVG_REWARD_R` and
    `EV_BREAKEVEN_BAND_R`, which set the illustrative EV sentence. All three are inside
    `code_hash`, so a change to them is still detected; the record just cannot say which
    value a run used. **Adding them moves `run_hash`**, which the golden snapshot pins,
    so the fix is a predicted re-baseline, not a free edit. **Fixed at `2c7a7d1`:** the
    three are listed, and
    `tests/test_fingerprint_names_every_constant.py` scans every fingerprinted module
    for UPPER_CASE finite numeric constants, so the next one missed fails the day it is
    written rather than waiting for a read.
23. **The raw-input archive is overwritten by a rerun on different code.** Its file
    name is `run_hash`, which excludes `code_hash` by design; a rerun on identical
    candles and config under changed code rewrites the file, and the earlier run's
    per-file code digests (`meta.code`) with it. The decision record keeps its own
    `code_hash`, so the decision's code identity survives. Reachable on pinned-fixture
    runs across commits; live runs rarely repeat their input (finding 16).
    **Documented by the commit that writes this line** (`write_archive`'s docstring),
    not renamed, and pinned by a test of the overwrite it describes.
24. **`lineage.verify_archive()` checks an archive only against itself.** It compares
    each stored frame with the digest stored beside it in the same file, so an edit
    that rewrites both passes. The check that means something — the archive against the
    decision log's `input_hashes` — exists only in the tests; nothing in the repository
    lets an operator check a logged decision against its archive or against re-fetched
    data. The docstring's "a file that has been edited since it was written says so"
    overstates it. **Fixed by the commit that writes this line:**
    `lineage.verify_against_record(path, record)` re-hashes each archived frame and
    compares it with the record's `input_hashes`, and the archive's `run_hash` with the
    record's; `verify_archive`'s docstring now says what it checks. Run on Viktor's live
    log (read on Linux from his disk, 31 records): 30 match in every frame and in
    `run_hash`; 1 (6 September) carries no input hashes and returns `{}`. **Not built:**
    a command-line wrapper (the function is called from Python), and a re-fetch
    comparison (`frame_hash` of a re-fetched frame against the same record hash).
25. **The staleness check accepts a last candle in the future.** `validate_ohlcv`
    rejects age above three bars and accepts any negative age. A timestamp
    inconsistency, one of Item 3's named classes. Reachability on MEXC: not measured.
26. **`validation`'s timeframe table lower-cases what it is given.** MEXC's month
    interval `1M` would be read as one minute, and MEXC's `60m` is not listed, which
    silently switches off the spacing and staleness checks. Latent: the engine uses
    only `4h` and `1d` (`core/config.py`), and `main.py` takes no other.
27. **`data_fetcher.fetch_ohlc` discards the exchange's own error text** when the
    response is not a list (e.g. MEXC's `{"code": …, "msg": …}`): the error reads
    "Empty or invalid API response." Also: `import time` is unused.

**Confirmed again by the read, not new:** finding 16 — `fetch_ohlc` drops
`close_time` and keeps the forming candle, and the staleness check measures from the
candle's open time, so a forming candle is never stale.

**Claude's claims, open to the independent auditor** — claims with their evidence
named, not findings: the Constitution does not let the builder certify its own
compliance.

14. Every engine module is reachable from `main.py` except `core/decision_contract.py`
    (test-side by design) and `utils/decision_log_backup.py` (a standalone tool with its
    own `__main__`). No orphaned module.
15. `_refuse_incoherent_plan` cannot fire today (see 8) — correctly so: it is a tripwire
    against a future change, which is what its docstring says it is.

### Work order — Claude's, under Viktor's delegation

Each code commit is its own commit and updates this file for its own landing.

- **A–F landed:** A `ebb4e5c` (the review into the repo), B `a530006` (panel display),
  C `e3f3d51` (risk-model dead paths; D folded in), E `afd8460` (fabricated defaults),
  F `3f263c2` (the signals confirm). Each one's Windows confirmation, negative controls
  and wrong predictions are recorded in HISTORY's entry for this file at `aafded0`.
- **Done in the third session, ahead of G, at Viktor's choice:** the deferred read
  (findings 19–27 above); the running change list, now `docs/audit_change_list.md`; the
  two record questions (Resolved, below); the sandbox lessons, proposed to Viktor as an
  update to the patch-delivery skill (a skill is saved by him from a review card, not
  from the repository).
- **G — macro in the CONSERVATIVE branches (17). Next in Claude's order.** Changes which
  trades are taken, so it is scoped in full before any diff: `decision_model`'s ladder,
  every caller, the golden fields it could move, and the live decision log checked
  first for which recorded actions it would change, as for F. The live run happens
  before the commit (above).
- **Findings 19–27 and the direction-box tests — six commits, Claude's.** Viktor chose
  commits 1–3 for the third session, the rest for later:
  1. Tests for the SETUP DIRECTION box and its NEUTRAL branch — `9c4917c`. Tests only;
     `code_hash` unmoved.
  2. `decision_log`: findings 19, 20, 21 — `05a12c7`.
  3. `decision_log`: finding 22 alone — `2c7a7d1`. It moved `run_hash`, so the golden
     snapshot.
  4. `lineage`: 23 (a documentation correction, not a rename: the archive's name is
     pinned in the golden snapshot and the record keeps its own `code_hash`) and 24
     (check an archive against its decision-log record); also the archive's own bare
     NaN, the lineage half of 19 — the commit that writes this line.
  5. `validation`: 25 (reject a last candle more than one bar in the future) and 26
     (case-sensitive timeframe table with MEXC's spellings).
  6. `data_fetcher`: 27.
  Viktor chose 4–6 for the fourth session.

### Resolved this session

- **The once-per-session rewrite of this file.** The previous version — rewritten at
  `ebb4e5c` and amended in place through `aafded0` — is in HISTORY verbatim, headings
  demoted one level, proven by un-demotion.
- **The hook's clean result on `aafded0`**, which existed only in chat, is filed above.
- **Which clone produced the Linux counts at `119c8a3`: an autocrlf clone.**
  `119c8a3`'s own commit message says "LINUX, autocrlf clone, Python 3.12.3" for
  504 / 372 / 433. The "default LF clone" text was `b869a30`'s, about `6e1baba`'s counts,
  and it said the LF counts were the same three numbers. There was no contradiction:
  `b68de08` (20 September) made `tests/test_pinned_source.py` portable across line
  endings, so an LF clone no longer fails it. Checked on 21 September: a fresh default
  clone of `cb659f1` (no CRLF in the tree) passes that file, 11 / 0. The "standing
  note" the item leaned on — the patch-delivery skill's "an LF clone fails that test" —
  was stale since `b68de08`; corrected in the proposed skill update.
- **Round 2's eleven observations are Kimi's.** The later word is HISTORY's own
  "The transcripts were Kimi's all along — 5 September 2026, afternoon", the same day
  as "The record corrected from the bill" and filed after it, backed by
  `docs/audit_reports/round2_kimi_k3_20260902/README.md` (57,631 identical characters;
  the transcript names itself Kimi). That later section names "the 5 September
  correction from the bill" among the records that inherited the misattribution. The
  earlier section is not marked in place; HISTORY is append-only and the correction
  that supersedes it names it, so no edit is owed.
- **The HISTORY move at `cb659f1` now has its negative control.** `cb659f1`'s
  message said the move was proven by un-demotion but ran no negative control, which
  the practice includes (Engineering Notes, `e431714`). Run afterwards against the
  committed blobs: the proof holds, and a one-character change to the moved body is
  detected.
- **README.md checked against this file** — the hook reported it three commits behind.
  Stale: both test-count lines (528 / 393 / 457, the counts at E), and nothing said the
  audit is paused or that backtesting now also waits on an independent re-audit of the
  changes since 14 September. Brought current at `cb659f1`; its test counts again,
  after `2c7a7d1` moved them, in the commit that writes this line.
- **The live-run check for `05a12c7` and `2c7a7d1`**, and the hook's clean result and
  clean working tree at `2c7a7d1`, which existed only in chat, are filed above.

### Open items

Items marked **Viktor's call** are his to decide; he writes his position first and
Claude critiques it.

- **Viktor's call — findings 4, 5, 6, 7, 16 and 18 above**, before backtesting. Not
  started.
- **The independent audit — paused, ruled 21 September.** When it is planned, still
  Viktor's: which model, the package (the standing default for a fresh Tier-1 audit is
  the full package), whether the auditor sees the scrapped findings, and the
  instruction for the selected model. No backtesting before it.
- **Claude's — the running change list for the audit:** `docs/audit_change_list.md`,
  from the baseline `e65a0f7` (the tree round 6's fix-verification was sent). **Every
  later commit that changes engine code, tests or tooling adds its line there in the
  same commit.** The two entries that had no test at all — the SETUP DIRECTION box and
  its CONTRADICTORY line (`66f1479`, `39e0e79`) — are guarded since the commit that adds
  `tests/test_setup_direction_box.py`.
- **The pre-push hook is installed per clone, not per repository.** After any re-clone
  (including after a machine wipe), run `git config core.hooksPath githooks`;
  `session_handover_check.py` section 6 flags a clone without it.
- **Unrelated, not urgent:** confirm which YH programme permits AI-assisted
  examensarbete work.


## 22 September 2026 (sixth session) — PHASE7_NEXT.md as it stood at `5e55eb8`

*Moved here verbatim on 22 September 2026, when PHASE7_NEXT.md was rewritten in the
sixth session — the once-per-session rewrite owed at the fifth session's close. Every
line below the rule is the file's content at `5e55eb8` — rewritten at `486f1a5` and
amended in place at `3bfa6b7` and `5e55eb8` — unchanged, including its own wording:
"this session" is the fifth 21 September session, and "the commit that writes this
line" names `5e55eb8` or the commit that made each amendment. Its line "Viktor will
continue in the same chat on 22 September" is left as written; he opened a new session
on 22 September. Its headings are demoted one level (`#` → `##`, `##` → `###`) so they
nest under this entry; no other character is changed.*

---

## Next step — read this first

*21 September 2026, fifth session. Rewritten at the opening of this session by commit 5
of the six (`486f1a5`); the version it replaces — written at the opening of the third session and
amended in place through the fourth, as it stood at `4e2b1c8` — is in HISTORY verbatim.
This file is the project's current-state entry point: it states only what is true right
now and what to do next, and is rewritten each session, not appended to. Standing
rules, ratified specifications and rulings in force live in docs/PHASE7_DECISIONS.md.
The dated record — including this file's previous version, moved there verbatim this
session — lives in docs/PHASE7_HISTORY.md. A citation of this file written before the
18 September 2026 split — in the Engineering Notes, audit reports, handovers or any
other dated record — refers to content now in one of those two files; dated records are
not edited to say so (DECISIONS, "Ruling, 20 September 2026 — dated records are not
edited to follow a move").*

*Each code commit updates this file's own lines for its own landing, in the same
commit, so the file does not fall behind the tip.*

### PACE FIRST — read this before the rest of this file

Viktor judged, on his own, that 226 commits across 22 days had become hasty, and
ruled to slow down considerably (15 September 2026). **Do not open a session by
proposing work from "Open items" below, and do not treat it as a queue to clear.**
Ask what he wants to do first.

### Where the project is

On 21 September Viktor asked what to put to the engine before backtesting starts:
whether its logic is correct, whether it displays the correct information, and whether
it carries dead code. Claude read the decision path and, in the third session, the
deferred input side; the findings are below. Viktor delegated the order of the work to
Claude. Work orders A–F have landed, and commits 1–4 of the six that fix the deferred
read's findings. In the fifth session Viktor chose commits 5 and 6, then the session's
close: commit 5 is `486f1a5`, commit 6 `3bfa6b7`, and the commit that writes this line
is the session's documentation close. That closes the six. G is next in Claude's order.
Viktor will continue in the same chat on 22 September.

**Nothing Claude does under that delegation decides the engine's trading rules.**
Findings 4–7, 16 and 18 are questions about what the engine should do; they are
Viktor's, and none of the planned commits touches them. F changed which trades are
taken, and Viktor ruled it (DECISIONS, "Ruling, 21 September 2026 — the entry signals
confirm").

**The independent audit is paused** — ruled by Viktor, 21 September: "We pause the
audit. We work on the engine another four weeks." The four weeks are fixes and
preparing the audit, with no time pressure, and none of our own checks is written up as
verification (DECISIONS, "Ruling, 21 September 2026 — the independent audit paused").
**The Constitution's step 8 binds:** "Re-audit the items that changed — independent
auditor again, not a self-check by whoever made the fix. 9) Only then … build the
backtesting architecture." No engine change since the last independent round (round 6
fix-verification, 14 September) has been independently re-audited, so **no backtesting
before an independent re-audit.** Claude's two points not adopted, recorded in that
ruling: no end condition (Claude suggested deciding again around 19 October), and the
no-backtest rule exists only as text.

### Ruled — in force

- **The order of work is delegated to Claude** (Viktor, 21 September: "Organize a to do
  list and we start working, It is up to you."). It covers ordering and the items marked
  Claude's below; it does not cover the items marked Viktor's.
- **The audit is paused**, and **work order F is ruled** — both above, both in DECISIONS.
- **No ruling was made in the fifth session.** Viktor chose the work (commits 5 and 6,
  then the close); 28 and the widening of 27 are Claude's, under the delegation.

### Where things stand, right now

- **Tip:** the commit that writes this line (a commit cannot name its own hash) — the
  fifth session's documentation close; documentation only. Before it: `3bfa6b7`
  (commit 6 of the six, `data/data_fetcher.py`: finding 27), `486f1a5`
  (commit 5, `data/validation.py`: findings 25, 26 and 28, and this file's session
  rewrite), `4e2b1c8` (commit 4, `core/lineage.py`: findings 23, 24 and the archive's half of 19),
  `5d3a4b4` (the third session's documentation close), `2c7a7d1` (22), `05a12c7`
  (19–21), `9c4917c` (the direction-box tests), `1cc2142` (the deferred read and the
  audit change list). F itself is `3f263c2`. **Tag:** `portfolio-v1` at `99e022e`.
  **Release gate:** open, declared 15 September 2026.
- **Working tree and hook at `3bfa6b7`:** the push `486f1a5..3bfa6b7` printed
  `SUMMARY: clean`, section 1 (`git status --short`) "none", section 6 "installed" —
  Viktor's paste, fifth session. The tip was fetched into the sandbox afterwards and
  its five files matched the verified build byte for byte. The same at `486f1a5` (push
  `4e2b1c8..486f1a5`, pasted; six files matched). **Owed to the next session:** the
  hook's result on the push of the commit that writes this line, which will exist
  only in chat until filed. At `4e2b1c8`: the push
  `5d3a4b4..4e2b1c8` printed `SUMMARY: clean`, section 1 "none" (Viktor's message
  opening the fifth session); the tip, fetched after that push, matched the verified
  files (fourth session), and recomputes to `4fe5084e…` on a fresh clone (Linux, Python
  3.12.3). The earlier record of the hook is in HISTORY.
- **code_hash:** `b3c2308f8f3e05981af25ee82468c071f7bf0b9d49519b6e75bd78c37b5fb365`,
  moved at `3bfa6b7` (`data/data_fetcher.py`) from `2c8ebe32…`, computed under Python
  3.12.3 on the pristine and the applied tree; unmoved by the commit that writes this
  line (documentation only). **Confirmed on Windows before its commit:** Viktor's live
  run of 21 September 23:29, AEROUSDT 4h, NO-TRADE (RISK TOO HIGH), the 34th record,
  read by Claude from his disk before the commit step. The 33 earlier records were
  byte-identical to the copy taken before the run; the new record was strict JSON and
  carried `b3c2308f…`. Its archive, `aerousdt_4h_5242945daebc435b.json.gz`, was strict
  JSON with the same `meta.code.code_hash`. `verify_against_record` returned `run_hash`
  True and `btc`, `macro` and `struct` all True; `verify_archive` returned all True. The
  five applied files on disk matched the build (the new test file CRLF on disk). The
  run fetched successfully, so 27's new error text was not exercised on Windows — it
  is evidenced on Linux only, by `tests/test_fetch_reports_exchange_error.py`.
  **`2c8ebe3264c2543369d534512f0e1a6b3751f0e61811ecb291dfa5a9a331f391` (`486f1a5`),
  confirmed on Windows before its commit:** Viktor's live run of 21 September 23:17,
  AEROUSDT 4h, NO-TRADE (RISK TOO HIGH), the 33rd record, read by Claude from his disk
  before the commit step. No fetch error — so the forming candle passed finding 25's
  check, as predicted. The 32 earlier records were byte-identical to the copy taken
  before the run; the new record was strict JSON (no NaN or Infinity token) and
  carried `2c8ebe32…`. Its archive, `aerousdt_4h_f0113fc2ee2caee6.json.gz`, was strict
  JSON with the same `meta.code.code_hash`. `verify_against_record` returned `run_hash`
  True and `btc`, `macro` and `struct` all True; `verify_archive` returned all True. The
  six applied files on disk matched the build (the new test file CRLF on disk).
  **`4fe5084e47157289326776ffca85671548608fc409b614c7e11c2fc687c71d66` (`4e2b1c8`),
  confirmed on Windows before its commit:** Viktor's live run of 21 September 22:54,
  AEROUSDT 4h, NO-TRADE (RISK TOO HIGH), the 32nd record, read by Claude from his disk
  before the commit step (fourth session). The 31 earlier records were byte-identical
  to the copy taken at `5d3a4b4`; the new record was strict JSON and carried
  `4fe5084e…`. Its archive, `aerousdt_4h_87f1792d8b504b89.json.gz`, was strict JSON and
  its `meta.code.code_hash` was the same. `verify_against_record` returned `run_hash`
  True and `btc`, `macro` and `struct` all True; `verify_archive` returned all True. The
  six applied files on disk matched the build (the new test file CRLF on disk). The
  earlier hashes and their confirmations are in HISTORY (this file as it stood at
  `4e2b1c8`).
- **code_hash is only comparable within one Python minor version.** It hashes `ast.dump`
  output, a CPython implementation detail (`core/code_fingerprint.py`, "WHAT IT DOES NOT
  SURVIVE"). **Every `code_hash` claim about this project is computed under Python 3.12**
  (Viktor runs 3.12.10).
- **Golden snapshot:** unmoved by the commit that writes this line (documentation
  only). Unmoved at `3bfa6b7`, as predicted: `data/data_fetcher.py` is not fingerprinted, and its change acts only on a live reply
  that is an error; the pinned path does not call `fetch_ohlc`. Unmoved at `486f1a5`
  too: `data/validation.py` is not in `FINGERPRINTED_MODULES`, the pinned path passes
  no `now`, and `4h` and `1d` keep their table entries. Last re-baselined at `2c7a7d1` (finding 22: `run_hash` in two places, the archive
  name in two, three `module_constants` leaves; no decision field).
- **Test suite** — unmoved by the commit that writes this line (documentation only).
  At `3bfa6b7`, moved by 8 fixture-free tests
  in the new `tests/test_fetch_reports_exchange_error.py`, none needing `pandas_ta`:
  **597 passed / 0 failed, no warnings line** with `pandas_ta`; **460 passed / 126
  skipped** without it; `run_tests.py` **526 passed / 0 failed / 32 errors**, all 32
  fixture-collection `TypeError`s, unmoved. Linux sandbox, autocrlf clone, Python
  3.12.3, pinned requirements, applied tree; on Windows, the stop conditions of its
  command sequence (Viktor proceeded past them). At `486f1a5`: 589 / 452 with 126 skipped / 518 (Linux); on
  Windows, confirmed by Viktor proceeding past the steps whose stop conditions they
  were. At `4e2b1c8`: 578 / 441 with 126 skipped / 507.
- **Engineering Notes:** through Entry #141 (v1.33), which covers `4629002`.
  **Twenty-seven commits behind** — `3a899b5`, `92775ea`, `53394ff`, `982e70f`,
  `65a0aef`, `a9d4b1f`, `6e1baba`, `b869a30`, `119c8a3`, `635a94e`, `ebb4e5c`,
  `a530006`, `e3f3d51`, `afd8460`, `49de810`, `3f263c2`, `aafded0`, `cb659f1`,
  `1cc2142`, `9c4917c`, `05a12c7`, `2c7a7d1`, `5d3a4b4`, `4e2b1c8`, `486f1a5`, `3bfa6b7`
  and the commit that writes this line — by Viktor's choice, under the standing batching rule. **This count
  includes the commit that writes it, so every later commit adds one until the Notes
  are regenerated.** If the independent audit's package includes the Notes, regenerate
  them before building it.
- **Portfolio Document and AI-Attribution Statement:** both current with their scripts.
- **README.md:** its two test-count lines current at `3bfa6b7` (597 / 460 with 126
  skipped / 526); untouched by the commit that writes this line, which changes no count,
  so the hook's section 5 will report it one commit behind — expected. Otherwise
  current since `cb659f1`.

### Carried lesson — the live run comes BEFORE the commit

At F the live run asked for in the command sequence did not happen before the commit:
at the push the log still held 29 records, the newest on the old `code_hash`. Claude
caught it by reading the log, not from a paste. **On every change that moves
`code_hash` — and always on one that touches the decision path (G is one) — the live
run and the panel read happen before `git commit`, and Claude checks the decision-log
record for the new `code_hash` before the commit step, not after the push.** Never
predict live numbers; check the record. Followed at `2c7a7d1`, `4e2b1c8`, `486f1a5` and `3bfa6b7`: the
command list stopped at the live run, Claude read the record, and only then gave the
commit steps.

### Sandbox practice

- Set `git config core.autocrlf true` in the clone and re-check out; a `-c` flag on
  `git clone` does not persist.
- Run negative controls with `PYTHONDONTWRITEBYTECODE=1`.
- The golden updater writes LF with no final-newline handling of its own; restore CRLF
  and the original ending by hand before diffing.
- A file re-written to the outputs folder under the same name once reached Viktor's
  disk as the OLD version. Use a new file name for each version, and always read
  deliveries back.
- `git status --short` sorts by path; predict the order that way.
- **Fifth session:** the sandbox's default `python3` was 3.11; build both virtualenvs
  from `/usr/bin/python3.12` explicitly. The sandbox cannot reach `api.mexc.com` (the
  proxy refuses it), so anything about MEXC's live behaviour is either read from its
  documentation or from Viktor's own runs — say which.

### Review findings, 21 September 2026

Read at `635a94e` from Viktor's disk and from an autocrlf clone. **Every finding comes
from reading the code; none was reproduced by running the engine** unless it says so.
The full text of each fixed finding, with its evidence, is in HISTORY: 1–13 in the
entry for this file at `aafded0`, 19–24 in the entry at `4e2b1c8`.

**Fixed** — one line each

1. Two panel lines named AERO whatever the symbol — fixed at B (`a530006`).
2. TREND and VALIDATION could print `Score: nan/100` — fixed at B.
3. Absent entry, confidence and trade-quality scores printed `0.00` — fixed at B.
8. `risk_model`'s direction check could never match — fixed at C (`e3f3d51`).
9. An unreachable fallback that would put the stop on the wrong side — fixed at C.
10. Nothing at runtime checked the stop's side — closed at C, at the only producer (D).
11. `long_signal` / `short_signal` decided nothing — ruled and fixed at F (`3f263c2`):
    they now CONFIRM the side the ladder chooses; unconfirmed is `NO-TRADE (SIGNAL
    UNCONFIRMED)`.
12. `live_trading.py`'s simulated order fabricated zeros and "OK" — fixed at E
    (`afd8460`), with its `utcnow()` call.
13. `structure/structure.py`'s `.get(…, default)` on always-present keys — fixed at E.
19. The decision log wrote bare `NaN`, which is not JSON — fixed at `05a12c7`; the
    archive's half at `4e2b1c8`.
20. `decision_log.read()` dropped damaged lines silently — fixed at `05a12c7`.
21. `decision_log`'s docstring named the wrong recorded source — fixed at `05a12c7`.
22. The readable fingerprint missed three constants — fixed at `2c7a7d1`, with a scan
    that fails on the next one.
23. A rerun on changed code overwrites the archive — documented and pinned by a test at
    `4e2b1c8`, not renamed.
24. `verify_archive()` checked an archive only against itself — `verify_against_record()`
    added at `4e2b1c8`. Not built: a command-line wrapper, and a re-fetch comparison.
25. **The staleness check accepted a last candle in the future.** Fixed at `486f1a5`:
    a last candle more than one bar
    (`FUTURE_TOLERANCE_BARS = 1`) after `now` is rejected as future-dated. One bar, not
    zero, because the exchange's clock and Viktor's are two clocks. Reachability on
    MEXC: not measured.
26. **`validation`'s timeframe table lower-cased what it was given.** Fixed at
    `486f1a5`: exact match, case included; MEXC's `60m` and `1W`
    listed; the month `1M` deliberately unlisted (not a fixed number of minutes), so it
    skips the spacing check instead of being read as one minute. Consequence, stated: an
    upper-case spelling the table does not list (`4H`) is now unknown and skips the
    spacing and staleness checks, where before it was lower-cased and checked; nothing
    in the engine uses one. MEXC's spellings: `60m` is on its documentation page (read
    this session through a fetch tool that summarised the page, so weak); `1W` and `1M`
    come from the third session's read and were not re-checked.
27. **`data_fetcher.fetch_ohlc` discarded the exchange's own error text.** Fixed at
    `3bfa6b7`. A reply that is not a list is quoted in the error
    (MEXC's `{"code": …, "msg": …}` as that pair, anything else as its repr), and an
    empty list is reported apart from it; they used to share "Empty or invalid API
    response." **Widened past the finding as written:** a 4XX reply's body is quoted
    too — MEXC documents 4XX for a malformed request, so that is where its code/msg
    usually arrives, and `requests`' `HTTPError` text holds only the status line and
    the URL. Quoted text is cut at `EXCHANGE_TEXT_LIMIT` (300) characters. The unused
    `import time` is removed, and a test now fails on any unused import in the module.
    The exchange's text reaches the panel's "Data fetch failed" line only: a failed
    fetch writes no decision-log record. What MEXC actually returns for a bad symbol
    was not observed — the sandbox cannot reach it.
28. **An aware `now` was relabelled as UTC, not converted.** Found while fixing 25, in
    the same lines: `tz_localize(None)` keeps the wall-clock reading, so a Stockholm
    `now` was read two hours late. Fixed at `486f1a5` with `tz_convert("UTC")` first. The engine's own caller passes naive UTC and never
    reached it; after 25, a `now` west of UTC would have made a current series look
    future-dated, so the two land together.

**Viktor's call, before backtesting** — he writes his position first; Claude critiques.

4. **The panel gives an entry ZONE but measures everything from the last close.** Stop,
   T1–T3 and all three R:R values come from `current_price` (`engine_core.py:999`); the
   zone is EMA20–EMA50. LONG is authorised without price in the zone (entry score ≥ 70 is
   reachable at NEAR ZONE), and CONSERVATIVE LONG has no zone condition at all. The
   printed R:R holds only for an entry at the current price. There is no single entry
   price on the panel. A backtest must fill somewhere, so this needs ruling first.
5. **A NEUTRAL bias still prints a full plan.** The plan's direction comes from
   `bias_score >= 0` (`models/risk_model.py`, since C), so a score between −20 and +20
   prints a long- or short-shaped stop and targets under a NEUTRAL bias with no
   direction box; exactly 0 prints a long.
6. **The stop is pulled to the 75-day volume point of control, with no distance limit.**
   `structural_level=hvn` (`engine_core.py:1040`); for a long the stop is
   min(HVN, ATR stop). The HVN is the single highest-volume bin of the whole 450-candle
   frame (`indicators/volume_profile.py`, 50 bins) — about 75 days on 4h. A trend that
   has moved away from its point of control therefore gets its stop there, and past 15%
   the risk check fails: NO-TRADE (RISK TOO HIGH), RISK REGIME UNKNOWN. Seen on Viktor's
   live runs of 21 September at 05:28, 05:51 and 06:18 and on the pinned golden fixture,
   each checked against the record (details in HISTORY); the 19:24 run's action was again
   RISK TOO HIGH on the HVN stop. How often this vetoes a setup across many runs was not
   measured. **Dependency added at F:** the confirmation gate no longer blocks on HVN
   proximity, on the reasoning that this stop already acts on that area. If this finding
   is ruled to stop pulling the stop to the HVN, nothing checks HVN proximity.
7. **Indicator values beyond 5σ are silently replaced by the previous bar's.**
   `indicators/indicators.py:105–110`, inside `clean_series`, which EMA, RSI, ADX,
   SuperTrend and ATR all pass through. Nothing records the replacement — unlike volume
   spikes (`:746`), which are kept and flagged. At the decision bar the replaced value
   becomes a reported indicator *failure*. The mean and standard deviation span the
   whole frame, so a backtest that computes indicators once over its history would leak
   future bars into past decisions. Reachability on live data: not measured.
16. **The decision is made on the candle still forming.** Found from the record, then
    confirmed in the code: Viktor's live runs at 05:28 and 05:51 (21 September) carry
    the same last candle, `2026-09-21 00:00` UTC, with a different input hash and price.
    `data/data_fetcher.py` requests MEXC klines, reads and discards `close_time`, and
    keeps every row, the live one included. So on a live run the close, the volume and
    every indicator at the decision bar come from a partial candle, and the panel can
    change within the same candle. A backtest on closed candles would test a different
    engine from the one run live. Which candle counts is a rule, not a defect to patch.
    The staleness check measures from the candle's open time, so a forming candle is
    never stale — confirmed again by the deferred read, and untouched by 25.
18. **The bias state machine gates no trade since F.** Viktor dropped the CONFIRMED
    requirement so the signal follows `raw_bias`, as `decision_model` does.
    `detailed_bias` still feeds `exit_model`'s "bias state changed" flag and the
    persisted state; nothing that decides reads it. Recorded, nothing removed. Whether
    its persistence requirement should gate anything is Viktor's call.

**Claude's, open**

17. **Macro still counts twice in the CONSERVATIVE branches.** `decision_model`'s
    CONSERVATIVE LONG requires `macro_bias == "BULLISH"`, CONSERVATIVE SHORT
    `"BEARISH"` — a hard requirement on evidence already weighted into `bias_score`,
    the double count Viktor removed from the signal at F. Left out of F so that each
    change to which trades are taken lands in its own commit. → G.

**Recorded, not changed:** a timeframe the table does not list still skips the spacing
and staleness checks without saying so (`_interval_minutes` returns None). Making it
loud would reject a monthly series outright; nothing in the engine passes one, so it
stays as documented in the module.

**Claude's claims, open to the independent auditor** — claims with their evidence
named, not findings: the Constitution does not let the builder certify its own
compliance.

14. Every engine module is reachable from `main.py` except `core/decision_contract.py`
    (test-side by design) and `utils/decision_log_backup.py` (a standalone tool with its
    own `__main__`). No orphaned module.
15. `_refuse_incoherent_plan` cannot fire today (see 8) — correctly so: it is a tripwire
    against a future change, which is what its docstring says it is.

### Work order — Claude's, under Viktor's delegation

Each code commit is its own commit and updates this file for its own landing.

- **A–F landed:** A `ebb4e5c`, B `a530006`, C `e3f3d51` (D folded in), E `afd8460`,
  F `3f263c2`. Each one's Windows confirmation, negative controls and wrong predictions
  are recorded in HISTORY's entry for this file at `aafded0`.
- **The six commits for findings 19–28 and the direction-box tests:**
  1. The SETUP DIRECTION box tests — `9c4917c`.
  2. `decision_log`: 19, 20, 21 — `05a12c7`.
  3. `decision_log`: 22 — `2c7a7d1`.
  4. `lineage`: 23, 24, 19's archive half — `4e2b1c8`.
  5. `validation`: 25, 26, and 28 found on the way — `486f1a5`.
  6. `data_fetcher`: 27 — `3bfa6b7`. The six are done.
- **G — macro in the CONSERVATIVE branches (17). Next in Claude's order.**
  Changes which trades are taken, so it is scoped in full before any diff:
  `decision_model`'s ladder, every caller, the golden fields it could move, and the
  live decision log checked first for which recorded actions it would change, as for F.
  The live run happens before the commit (above).

### Resolved this session

- **The fourth session's owed filing:** the Windows confirmation of `4e2b1c8` and the
  hook's clean result on its push, which existed only in chat — filed above.
- **Commits 5 and 6 of the six** — `486f1a5` and `3bfa6b7`; both Windows
  confirmations and both hook results, filed above.
- **The session's handover check, run at its close:** the state is in this file; no
  ruling was made (above); the working tree was clean on the push of `3bfa6b7`
  (section 1 "none"); the Engineering Notes gap is stated (27 behind); no loose patch
  file (section 3 "none"); the one piece of evidence still in chat is the hook's
  result on this commit's own push — owed to the next session (above).
- **The once-per-session rewrite of this file**, owed at the fourth session's close.
  The previous version — written at the third session's opening and amended in place
  through `4e2b1c8` — is in HISTORY verbatim, headings demoted one level, proven by
  un-demotion with a negative control (the commit message has the result).

### Open items

Items marked **Viktor's call** are his to decide; he writes his position first and
Claude critiques it.

- **Owed at the next session's opening:** file the hook's result on this commit's
  push; and this file's once-per-session rewrite, with this version moved to HISTORY
  verbatim, proven by un-demotion with a negative control.
- **Viktor's call — findings 4, 5, 6, 7, 16 and 18 above**, before backtesting. Not
  started.
- **The independent audit — paused, ruled 21 September.** When it is planned, still
  Viktor's: which model, the package (the standing default for a fresh Tier-1 audit is
  the full package), whether the auditor sees the scrapped findings, and the
  instruction for the selected model. No backtesting before it.
- **Claude's — the running change list for the audit:** `docs/audit_change_list.md`,
  from the baseline `e65a0f7` (the tree round 6's fix-verification was sent). **Every
  later commit that changes engine code, tests or tooling adds its line there in the
  same commit.**
- **The pre-push hook is installed per clone, not per repository.** After any re-clone
  (including after a machine wipe), run `git config core.hooksPath githooks`;
  `session_handover_check.py` section 6 flags a clone without it.
- **Unrelated, not urgent:** confirm which YH programme permits AI-assisted
  examensarbete work.


## 26 September 2026 (seventh session) — PHASE7_NEXT.md as it stood at `bc48f59`

*Moved here verbatim on 26 September 2026, when PHASE7_NEXT.md was rewritten by the
seventh session's first commit — the once-per-session rewrite. Every line below the rule
is the file's content at `bc48f59` — rewritten at `e804b64` and amended in place at
`c5dc4cd` and `bc48f59` — unchanged, including its own wording: "this session" is the
sixth, 22 September session, and "the commit that writes this line" names `bc48f59` or
the commit that made each amendment. Its headings are demoted one level (`#` → `##`,
`##` → `###`) so they nest under this entry; no other character is changed.*

---

## Next step — read this first

*22 September 2026, sixth session. Rewritten by this session's first commit, `e804b64`,
the one that regenerates the Engineering Notes at v1.34, and amended in place by its
second and third; the version it replaces — rewritten at
`486f1a5` and amended in place at `3bfa6b7` and `5e55eb8` — is in HISTORY verbatim.
This file is the project's current-state entry point: it states only what is true right
now and what to do next, and is rewritten each session, not appended to. Standing
rules, ratified specifications and rulings in force live in docs/PHASE7_DECISIONS.md.
The dated record — including this file's previous version, moved there verbatim this
session — lives in docs/PHASE7_HISTORY.md. A citation of this file written before the
18 September 2026 split — in the Engineering Notes, audit reports, handovers or any
other dated record — refers to content now in one of those two files; dated records are
not edited to say so (DECISIONS, "Ruling, 20 September 2026 — dated records are not
edited to follow a move").*

*Each code commit updates this file's own lines for its own landing, in the same
commit, so the file does not fall behind the tip.*

### PACE FIRST — read this before the rest of this file

Viktor judged, on his own, that 226 commits across 22 days had become hasty, and
ruled to slow down considerably (15 September 2026). **Do not open a session by
proposing work from "Open items" below, and do not treat it as a queue to clear.**
Ask what he wants to do first.

### Where the project is

Viktor asked, on 21 September, what to put to the engine before backtesting. The
review's findings are below. Work orders A–F have landed, and so have the six commits
for the deferred read's findings (19–28) and the direction-box tests. Asked what to do
first in the sixth session (22 September), Viktor chose two things. The first was to
regenerate the Engineering Notes, 27 commits behind. The second was Claude's open
objection that the audit pause had no end condition. He ruled on the second (below),
and `e804b64` carries both.

**What remains before the independent audit is a closed list:** work order G (Claude's,
finding 17) and findings 4, 5, 6, 7, 16 and 18 (Viktor's). When each is done, the audit
is next. Anything found in the meantime goes on the list for after the audit (below),
not onto this one.

**Nothing Claude does under the delegation decides the engine's trading rules.**
Findings 4–7, 16 and 18 are questions about what the engine should do. They are
Viktor's, and none of Claude's commits touches them. G changes which trades are taken.
It is Claude's under the delegation (Viktor's message opening this session), and it
gets full scope, the live log checked first, and the live run before the commit.

**The independent audit is paused, and now has an end** — DECISIONS, "Ruling, 21
September 2026 — the independent audit paused" and "Ruling, 22 September 2026 — when
the audit resumes". **The Constitution's step 8 binds:** "Re-audit the items that
changed — independent auditor again, not a self-check by whoever made the fix. 9) Only
then … build the backtesting architecture." No engine change since the last independent
round (round 6 fix-verification, 14 September) has been independently re-audited, so
**no backtesting before an independent re-audit.** Claude's second point in the 21
September ruling is still open: the no-backtest rule exists only as text.

### Ruled — in force

- **The order of work is delegated to Claude** (Viktor, 21 September: "Organize a to do
  list and we start working, It is up to you."). It covers ordering and the items marked
  Claude's below; it does not cover the items marked Viktor's.
- **The audit is paused**, and **work order F is ruled** — both in DECISIONS, 21
  September.
- **Ruled this session — when the audit resumes** (DECISIONS, 22 September): once work
  order G and findings 4, 5, 6, 7, 16 and 18 are done. A finding is done when Viktor
  has ruled it and any code his ruling calls for has landed; a ruling to leave it as it
  is counts. The list is closed. The four weeks was his estimate with a buffer, not a
  rule.

### Where things stand, right now

- **Tip:** the commit that writes this line (a commit cannot name its own hash) — the
  Engineering Notes regenerated at v1.35 and `c5dc4cd`'s push filed; documentation
  only. Before it: `c5dc4cd` (`e804b64`'s push filed, README's audit row brought
  current), `e804b64` (the Engineering Notes' v1.34 regeneration, the 22 September
  ruling, and this file's session rewrite), `5e55eb8` (the fifth session's
  documentation close), `3bfa6b7` (commit 6 of the six, `data/data_fetcher.py`:
  finding 27), `486f1a5` (commit 5, `data/validation.py`: 25, 26, 28), `4e2b1c8`
  (commit 4, `core/lineage.py`: 23, 24, 19's archive half), `2c7a7d1` (22), `05a12c7`
  (19–21), `9c4917c` (the direction-box tests). F itself is `3f263c2`. **Tag:**
  `portfolio-v1` at `99e022e`. **Release gate:** open, declared 15 September 2026.
- **Working tree and hook at `c5dc4cd`:** the push `e804b64..c5dc4cd` printed
  `SUMMARY: clean`, section 1 "none", section 6 "installed", and section 5 README.md
  0 commits behind, as predicted — Viktor's paste. The tip was fetched into the sandbox
  afterwards and reverse-applies the verified patch cleanly. **Owed to the next
  commit:** the hook's result on the push of the commit that writes this line.
- **At `e804b64`:** the push `5e55eb8..e804b64` printed `SUMMARY: clean`, section 1
  "none", section 6 "installed", and section 5 README.md two commits behind, as
  predicted — Viktor's paste. The tip was fetched into the sandbox afterwards; its six
  changed files matched the verified build byte for byte.
- **At `5e55eb8`:** the push `3bfa6b7..5e55eb8` printed
  `SUMMARY: clean`, section 1 (`git status --short`) "none", section 6 "installed", and
  section 5 README.md one commit behind (expected: that commit changed no count) —
  Viktor's message opening this session. The fifth session's sandbox fetched the tip
  afterwards, and the verified close patch reverse-applied to it cleanly (same message).
  This session's clone of GitHub's tip was `5e55eb8`. The earlier record of the hook is
  in HISTORY.
- **code_hash:** `b3c2308f8f3e05981af25ee82468c071f7bf0b9d49519b6e75bd78c37b5fb365`,
  moved at `3bfa6b7` (`data/data_fetcher.py`) from `2c8ebe32…`; unmoved at `5e55eb8`, `e804b64`, `c5dc4cd` and
  by the commit that writes this line (documentation only). Computed under Python 3.12.3
  on the tip's tree and on the applied tree. **Confirmed on Windows before its
  commit:** Viktor's live run of 21 September 23:29, AEROUSDT 4h, NO-TRADE (RISK TOO
  HIGH), the 34th record, read by Claude from his disk before the commit step. The 33
  earlier records were byte-identical to the copy taken before the run; the new record
  was strict JSON and carried `b3c2308f…`; its archive,
  `aerousdt_4h_5242945daebc435b.json.gz`, carried the same `meta.code.code_hash`;
  `verify_against_record` and `verify_archive` returned all True. The fetch succeeded,
  so finding 27's new error text is evidenced on Linux only, by its tests. Every
  code_hash from `4629002` to `5e55eb8` was recomputed on its own tree for the v1.34
  regeneration and matched its commit message; the chain is in the Notes' Document
  History, v1.34.
- **code_hash is only comparable within one Python minor version.** It hashes `ast.dump`
  output, a CPython implementation detail (`core/code_fingerprint.py`, "WHAT IT DOES NOT
  SURVIVE"). **Every `code_hash` claim about this project is computed under Python 3.12**
  (Viktor runs 3.12.10).
- **Golden snapshot:** unmoved by the commit that writes this line and at `c5dc4cd`, `e804b64`, `5e55eb8`,
  `3bfa6b7`, `486f1a5` and `4e2b1c8`. Last re-baselined at `2c7a7d1` (finding 22:
  `run_hash` in two places, the archive name in two, three `module_constants` leaves;
  no decision field).
- **Test suite** — unmoved by the commit that writes this line (documentation only):
  **597 passed / 0 failed, no warnings line** with `pandas_ta`; **460 passed / 126
  skipped** without it; `run_tests.py` **526 passed / 0 failed / 32 errors**, all 32
  fixture-collection `TypeError`s. Linux sandbox, autocrlf clone, Python 3.12.3, pinned
  requirements, applied tree. Last moved at `3bfa6b7`; on Windows, confirmed there by
  Viktor proceeding past the stop conditions.
- **Engineering Notes:** through Entry #166 (v1.35), which covers `c5dc4cd` and the
  22 September ruling `e804b64` carried. **One commit behind** — the commit that writes
  this line, which is the floor: a commit that regenerates the Notes cannot cover
  itself (Entry #144). Every later commit adds one until the next regeneration.
- **Portfolio Document and AI-Attribution Statement:** both current with their scripts,
  which last changed at `6e1baba`.
- **README.md:** its two test-count lines current at `3bfa6b7` (597 / 460 with 126
  skipped / 526). Its Independent-audit row, which said the round was paused "for about
  four weeks", now states the 22 September ruling (changed at `c5dc4cd`). Untouched by
  the commit that writes this line, so the hook's section 5 will report README.md one
  commit behind — expected. Otherwise current since `cb659f1`.

### Carried lesson — the live run comes BEFORE the commit

At F the live run asked for in the command sequence did not happen before the commit:
at the push the log still held 29 records, the newest on the old `code_hash`. Claude
caught it by reading the log, not from a paste. **On every change that moves
`code_hash` — and always on one that touches the decision path (G is one) — the live
run and the panel read happen before `git commit`, and Claude checks the decision-log
record for the new `code_hash` before the commit step, not after the push.** Never
predict live numbers; check the record. Followed at `2c7a7d1`, `4e2b1c8`, `486f1a5` and
`3bfa6b7`: the command list stopped at the live run, Claude read the record, and only
then gave the commit steps.

### Sandbox practice

- Set `git config core.autocrlf true` in the clone and re-check out; a `-c` flag on
  `git clone` does not persist.
- Run negative controls with `PYTHONDONTWRITEBYTECODE=1`.
- The golden updater writes LF with no final-newline handling of its own; restore CRLF
  and the original ending by hand before diffing.
- A file re-written to the outputs folder under the same name once reached Viktor's
  disk as the OLD version. Use a new file name for each version, and always read
  deliveries back.
- `git status --short` sorts by path; predict the order that way.
- The sandbox's default `python3` has been 3.11; build both virtualenvs from
  `/usr/bin/python3.12` explicitly. The sandbox cannot reach `api.mexc.com` (the proxy
  refuses it), so anything about MEXC's live behaviour is either read from its
  documentation or from Viktor's own runs — say which.
- **Sixth session:** `reportlab` 5.0.1 (not pinned; `docs/build/README.md` has the
  install line) rebuilt the committed Notes PDF from `5e55eb8` with identical extracted
  text, so it is a sound baseline for the Notes. The PDF embeds a build timestamp, so
  its bytes differ on every run.

### Review findings, 21 September 2026

Read at `635a94e` from Viktor's disk and from an autocrlf clone. **Every finding comes
from reading the code; none was reproduced by running the engine** unless it says so.
The full text of each fixed finding, with its evidence, is in HISTORY: 1–13 in the
entry for this file at `aafded0`, 19–24 in the entry at `4e2b1c8`, 25–28 in the entry
at `5e55eb8`. The Engineering Notes, Entries #150–#164, give each one's landing.

**Fixed** — one line each

1. Two panel lines named AERO whatever the symbol — fixed at B (`a530006`).
2. TREND and VALIDATION could print `Score: nan/100` — fixed at B.
3. Absent entry, confidence and trade-quality scores printed `0.00` — fixed at B.
8. `risk_model`'s direction check could never match — fixed at C (`e3f3d51`).
9. An unreachable fallback that would put the stop on the wrong side — fixed at C.
10. Nothing at runtime checked the stop's side — closed at C, at the only producer (D).
11. `long_signal` / `short_signal` decided nothing — ruled and fixed at F (`3f263c2`):
    they now CONFIRM the side the ladder chooses; unconfirmed is `NO-TRADE (SIGNAL
    UNCONFIRMED)`.
12. `live_trading.py`'s simulated order fabricated zeros and "OK" — fixed at E
    (`afd8460`), with its `utcnow()` call.
13. `structure/structure.py`'s `.get(…, default)` on always-present keys — fixed at E.
19. The decision log wrote bare `NaN`, which is not JSON — fixed at `05a12c7`; the
    archive's half at `4e2b1c8`.
20. `decision_log.read()` dropped damaged lines silently — fixed at `05a12c7`.
21. `decision_log`'s docstring named the wrong recorded source — fixed at `05a12c7`.
22. The readable fingerprint missed three constants — fixed at `2c7a7d1`, with a scan
    that fails on the next one.
23. A rerun on changed code overwrites the archive — documented and pinned by a test at
    `4e2b1c8`, not renamed.
24. `verify_archive()` checked an archive only against itself — `verify_against_record()`
    added at `4e2b1c8`. Not built: a command-line wrapper, and a re-fetch comparison.
25. The staleness check accepted a last candle in the future — fixed at `486f1a5`
    (`FUTURE_TOLERANCE_BARS = 1`). Reachability on MEXC: not measured.
26. `validation`'s timeframe table lower-cased what it was given — fixed at `486f1a5`:
    exact match; `60m` and `1W` listed; `1M` deliberately unlisted. An unlisted
    upper-case spelling (`4H`) now skips the checks; nothing in the engine uses one.
27. `data_fetcher.fetch_ohlc` discarded the exchange's own error text — fixed at
    `3bfa6b7`, widened to a 4XX reply's body. What MEXC returns for a bad symbol was
    not observed.
28. An aware `now` was relabelled as UTC, not converted — found while fixing 25, fixed
    at `486f1a5`.

**Viktor's call, before the audit and before backtesting** — he writes his position
first; Claude critiques. Each is done when ruled and any code the ruling calls for has
landed (DECISIONS, 22 September).

4. **The panel gives an entry ZONE but measures everything from the last close.** Stop,
   T1–T3 and all three R:R values come from `current_price` (`engine_core.py:999`); the
   zone is EMA20–EMA50. LONG is authorised without price in the zone (entry score ≥ 70 is
   reachable at NEAR ZONE), and CONSERVATIVE LONG has no zone condition at all. The
   printed R:R holds only for an entry at the current price. There is no single entry
   price on the panel. A backtest must fill somewhere, so this needs ruling first.
5. **A NEUTRAL bias still prints a full plan.** The plan's direction comes from
   `bias_score >= 0` (`models/risk_model.py`, since C), so a score between −20 and +20
   prints a long- or short-shaped stop and targets under a NEUTRAL bias with no
   direction box; exactly 0 prints a long.
6. **The stop is pulled to the 75-day volume point of control, with no distance limit.**
   `structural_level=hvn` (`engine_core.py:1040`); for a long the stop is
   min(HVN, ATR stop). The HVN is the single highest-volume bin of the whole 450-candle
   frame (`indicators/volume_profile.py`, 50 bins) — about 75 days on 4h. A trend that
   has moved away from its point of control therefore gets its stop there, and past 15%
   the risk check fails: NO-TRADE (RISK TOO HIGH), RISK REGIME UNKNOWN. Seen on Viktor's
   live runs of 21 September at 05:28, 05:51 and 06:18 and on the pinned golden fixture,
   each checked against the record (details in HISTORY); the 19:24 run's action was again
   RISK TOO HIGH on the HVN stop. How often this vetoes a setup across many runs was not
   measured. **Dependency added at F:** the confirmation gate no longer blocks on HVN
   proximity, on the reasoning that this stop already acts on that area. If this finding
   is ruled to stop pulling the stop to the HVN, nothing checks HVN proximity.
7. **Indicator values beyond 5σ are silently replaced by the previous bar's.**
   `indicators/indicators.py:105–110`, inside `clean_series`, which EMA, RSI, ADX,
   SuperTrend and ATR all pass through. Nothing records the replacement — unlike volume
   spikes (`:746`), which are kept and flagged. At the decision bar the replaced value
   becomes a reported indicator *failure*. The mean and standard deviation span the
   whole frame, so a backtest that computes indicators once over its history would leak
   future bars into past decisions. Reachability on live data: not measured.
16. **The decision is made on the candle still forming.** Found from the record, then
    confirmed in the code: Viktor's live runs at 05:28 and 05:51 (21 September) carry
    the same last candle, `2026-09-21 00:00` UTC, with a different input hash and price.
    `data/data_fetcher.py` requests MEXC klines, reads and discards `close_time`, and
    keeps every row, the live one included. So on a live run the close, the volume and
    every indicator at the decision bar come from a partial candle, and the panel can
    change within the same candle. A backtest on closed candles would test a different
    engine from the one run live. Which candle counts is a rule, not a defect to patch.
    The staleness check measures from the candle's open time, so a forming candle is
    never stale — confirmed again by the deferred read, and untouched by 25.
18. **The bias state machine gates no trade since F.** Viktor dropped the CONFIRMED
    requirement so the signal follows `raw_bias`, as `decision_model` does.
    `detailed_bias` still feeds `exit_model`'s "bias state changed" flag and the
    persisted state; nothing that decides reads it. Recorded, nothing removed. Whether
    its persistence requirement should gate anything is Viktor's call.

**Claude's, open**

17. **Macro still counts twice in the CONSERVATIVE branches.** `decision_model`'s
    CONSERVATIVE LONG requires `macro_bias == "BULLISH"`, CONSERVATIVE SHORT
    `"BEARISH"` — a hard requirement on evidence already weighted into `bias_score`,
    the double count Viktor removed from the signal at F. Left out of F so that each
    change to which trades are taken lands in its own commit. → G.

**Recorded, not changed:** a timeframe the table does not list still skips the spacing
and staleness checks without saying so (`_interval_minutes` returns None). Making it
loud would reject a monthly series outright; nothing in the engine passes one, so it
stays as documented in the module.

**Claude's claims, open to the independent auditor** — claims with their evidence
named, not findings: the Constitution does not let the builder certify its own
compliance.

14. Every engine module is reachable from `main.py` except `core/decision_contract.py`
    (test-side by design) and `utils/decision_log_backup.py` (a standalone tool with its
    own `__main__`). No orphaned module.
15. `_refuse_incoherent_plan` cannot fire today (see 8) — correctly so: it is a tripwire
    against a future change, which is what its docstring says it is.

### Found after 22 September — for after the next audit

The 22 September ruling closed the list above. A finding made from now on is recorded
here, with its evidence, and waits until after the independent audit; it does not move
the audit. Whether the auditor is shown this section is part of the package question,
Viktor's when the audit is planned.

- None yet.

### Work order — Claude's, under Viktor's delegation

Each code commit is its own commit and updates this file for its own landing.

- **A–F landed:** A `ebb4e5c`, B `a530006`, C `e3f3d51` (D folded in), E `afd8460`,
  F `3f263c2`. Each one's Windows confirmation, negative controls and wrong predictions
  are recorded in HISTORY's entry for this file at `aafded0`, and in the Notes.
- **The six commits for findings 19–28 and the direction-box tests** — `9c4917c`,
  `05a12c7`, `2c7a7d1`, `4e2b1c8`, `486f1a5`, `3bfa6b7`. Done.
- **G — macro in the CONSERVATIVE branches (17). Claude's, on the list before the
  audit.** Changes which trades are taken, so it is scoped in full before any diff:
  `decision_model`'s ladder, every caller, the golden fields it could move, and the
  live decision log checked first for which recorded actions it would change, as for F.
  The live run happens before the commit (above).

### Resolved this session

- **The fifth session's owed filing** (Viktor's message opening this session): the
  hook's result on the push of `5e55eb8` — filed above.
- **`e804b64`'s push and README's audit row** — the session's second commit, at
  Viktor's request for the finishing touches: the push filed above; README's "about
  four weeks" replaced by the ruling.
- **The Engineering Notes regenerated at v1.35** — the session's third commit, at
  Viktor's call: Entry #165 (the 22 September ruling) and #166 (`c5dc4cd`), with
  `c5dc4cd`'s push filed above. The gap goes from two commits to one, the floor.
- **The once-per-session rewrite of this file.** The previous version, as at `5e55eb8`,
  is in HISTORY verbatim, headings demoted one level, proven by un-demotion with a
  negative control (the commit message has the result).
- **The Engineering Notes regenerated at v1.34**, Entries #142–#164 for the 26 commits
  after `3a899b5` (Viktor's choice this session). One commit behind now: the floor.
- **When the audit resumes — ruled** (above; DECISIONS, 22 September). It answers
  Claude's point (1) in the 21 September ruling.

### Open items

Items marked **Viktor's call** are his to decide; he writes his position first and
Claude critiques it.

- **Owed to the next commit:** file the hook's result on this commit's push.
- **Viktor's call — findings 4, 5, 6, 7, 16 and 18 above.** On the closed list before
  the audit. Not started.
- **Claude's — work order G (finding 17).** On the closed list before the audit.
- **The independent audit — paused until the closed list is done** (DECISIONS, 21 and
  22 September). When it is planned, still Viktor's: which model, the package (the
  standing default for a fresh Tier-1 audit is the full package), whether the auditor
  sees the scrapped findings and the list for after the audit, and the instruction for
  the selected model. No backtesting before it.
- **Viktor's call, not ruled — Claude's point (2) of 21 September:** the rule "no
  backtesting before re-audit" exists only as text; a structural form would be a
  backtest entry point that refuses to run without a recorded re-audit.
- **Claude's — the running change list for the audit:** `docs/audit_change_list.md`,
  from the baseline `e65a0f7` (the tree round 6's fix-verification was sent). **Every
  later commit that changes engine code, tests or tooling adds its line there in the
  same commit.**
- **The pre-push hook is installed per clone, not per repository.** After any re-clone
  (including after a machine wipe), run `git config core.hooksPath githooks`;
  `session_handover_check.py` section 6 flags a clone without it.
- **Unrelated, not urgent:** confirm which YH programme permits AI-assisted
  examensarbete work.


## 26 September 2026 — correction: "To do list Claude Phase 7 Engine.pdf" was not deleted

*A new dated entry, not an edit. The entry above for PHASE7_NEXT.md as it stood at
`982e70f` (20 September) records, under "Recorded later on 20 September, in a new
session", that "To do list Claude Phase 7 Engine.pdf" was deleted from `D:\Phase_7_Engine_Random_Files` (Viktor's report),
and closes its Open item. That entry stands as written; this one corrects it.*

**What happened.** Viktor, in his message opening the seventh session: the PDF was not
deleted. It was still in `D:\Phase_7_Engine_Random_Files` on 22 September, and is now in
`Docs\99_Superseded` there.

**What was checked, 26 September, by Claude from his disk.** `Docs\99_Superseded` holds
one file, `Todo_List_for_Claude_2026-09-18.pdf` (94,441 bytes), not a file of the recorded
name. Its embedded title is "Namnlöst dokument" (a Google Docs export), so the file itself
cannot confirm its earlier name. Its content fits: a two-page to-do list written at tip
`dff7d00`. Its "Immediate" items are the pinned-data fallback, the atomic `_save_state`
write and the handover-check filter; the entry at `e115272` records every "Immediate" item
on that PDF as landed at `5be5d82` and `4a97c32`. So it is identified by content and by Viktor's report, not by
name; when it was renamed is not recorded.

**Status.** The document is retired, not deleted. Nothing in the repository depends on it.


## 26 September 2026 — correction: the round-1 audit outputs were recovered

*A new dated entry, not an edit. The 20 September entry "correction: the round-1 audit
outputs were lost", and every other record of that date saying so, stand as written; this
entry corrects them. The 20 September entry's own caveat held: "lost" meant "not found
after the search above, not proven absent everywhere".*

**What was found.** Viktor, 23 September 2026, in `D:\USB Backup\Phase7_Engine
documents\`, a backup that ends 30 August — before the reinstall. He hashed the six files
with `certutil -hashfile <path> SHA256` before copying, moving or opening any of them, and
recorded the result in `Phase7_Round1_Recovered_Hashes_2026-09-23.txt` (kept outside the
repository):

| File | Bytes | Modified | SHA256 |
|---|---|---|---|
| `Run1_DeepSeek_blind_review.md` | 15,923 | 2026-08-27 06:20 | `078dcf7c5794881244624eb957ae6ff60420f7fcd9cb8b26ec63f7d784d2e839` |
| `RunA_KimiK3_MVA_gate_findings.md` | 18,366 | 2026-08-27 06:20 | `1718afcac29698eab0628d34de3bda3474692bebffe1b62f81c856fa9a064fd3` |
| `RunA_KimiK3_room_export.json` | 544,271 | 2026-08-27 06:12 | `0ca783a2247283f82769d98b692a5ee95c02c16c9bda2d591bc54e0a2752f553` |
| `RunA_KimiK3_truncated_reasoning_trace.md` | 73,925 | 2026-08-27 06:20 | `26ab14bb446b4966b655f46d3a03f6b5c2914146409fa2c7785333246e451e26` |
| `RunB_KimiK3_tier1_findings.md` | 24,682 | 2026-08-27 09:38 | `d8280b4cea95ed60124a575d8817ef281e14f89c4949493bf1bb7c893110f21e` |
| `RunC_KimiK3_tiers234_findings.md` | 32,019 | 2026-08-27 09:43 | `991dd7ba866429a503e43cec44b22df02a943fd3c7b69000444533eb0f420f89` |

His record states what the hashes prove — the content has not changed since 23 September —
and what they do not: that these are the originals. That rests on the 27 August dates.
He checked the rest of the backup on 26 September; it holds nothing else new. The same
record notes that the round-2 Qwen response of 2 September is not in it (the backup ends
30 August).

**What was filed, 26 September.** All six, byte-identical, under
`docs/audit_reports/round1_deepseek-v4-pro_kimi-k3_2026-08-27/`, with a README for the
folder. Checked before the commit:

- **Line endings.** `.gitattributes` has `docs/audit_reports/** -text`, so git neither
  normalises these files at commit nor rewrites them at checkout. The six files are LF with
  no CR byte. The JSON has no final newline, and keeps none.
- **Ignore rules.** `.gitignore` ignores `*.json` but negates it for
  `docs/audit_reports/**/*.json`, so the export is tracked (`git check-ignore -v`).
- **The hashes.** Computed by Claude on the copies staged from Viktor's disk and on the
  files in the patch applied to an autocrlf clone; both matched his table. The command
  sequence stopped after Viktor applied the patch, so that Claude could hash the files on
  his disk before the commit; the commit message records the result.
- **Secrets.** Scanned before filing, since the repository is public: no API key, token,
  e-mail address or local path. The config's empty `API_KEY = ""` / `API_SECRET = ""`
  appear, quoted by the auditors. The export records OpenRouter's routing region as
  `"OSL"`; Claude raised it, and Viktor ruled to commit all six unchanged.
- **Not copied:** `API KEY FROM OPEN CODE.txt`, in the same backup folder. Not opened;
  Claude read only its name and size from the directory listing. Rotating the key, if it
  is still live, is Viktor's.

**One cross-check against a primary source.** Run A's findings file was compared with the
room export's final assistant message. Below the file's header they match character for
character, except for 21 newline characters present in the export and not in the file;
with all whitespace removed they are identical. The export's assistant message is dated
27 August 03:39 UTC (05:39 local), and the 20 September entry lists a Kimi K3 generation
at 05:39 local in the request log. Runs 1, B and C have no primary source in the backup,
and the truncated trace is from an earlier attempt than the export holds.

**What the files are.** Each `.md` file opens with a header written when it was made,
above a `---` rule; who wrote the headers is not recorded. The folder's README gives each
file's scope and what its header claims.

**Forward corrections in the same commit.** README.md's paragraph under "The audit, and
what it found", which said the output "cannot be recovered", now says where it is and that
it used to say otherwise. `docs/build/README.md`'s two paragraphs on the round-1 outputs,
likewise.

**Found and deliberately not fixed.** `docs/build/build_findings_bundle.py` reads the
four findings files, under the same names, from `docs/audit_raw/`, and its exit message
says they are not in the repository. Repointing it at the round-1 folder is a tooling
change and would take a line in `docs/audit_change_list.md`; it is left for Viktor's call.
The Engineering Notes' Entry #141 and the v1.33 history row describe the loss; they are
dated records and are not edited. The next regeneration adds an entry for the recovery.
