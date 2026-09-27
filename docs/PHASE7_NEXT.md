# Next step — read this first

*27 September 2026. Rewritten by the commit that lands finding 18's ruling and code,
which also files the push of `8b9ac1e`; the version it replaces — as it stood at
`8b9ac1e` — is in HISTORY verbatim.
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

## PACE FIRST — read this before the rest of this file

Viktor judged, on his own, that 226 commits across 22 days had become hasty, and
ruled to slow down considerably (15 September 2026). **Do not open a session by
proposing work from "Open items" below, and do not treat it as a queue to clear.**
Ask what he wants to do first.

## Where the project is

**What remains before the independent audit is a closed list:** work order G (Claude's,
finding 17) and findings 4, 5, 6, 7, 16 and 18 (Viktor's). When each is done, the audit
is next. Anything found in the meantime goes on the list for after the audit (below),
not onto this one. **Phase 3 started on 26 September (tenth session), in the order 16,
7, 4, 6, 5, 18, then G.** **Finding 16 is done** (ruled in the tenth session, code at
`add8540`). **Finding 7 is done** (ruled 27 September, code at `57f0521`). **Finding 4
is done** (ruled 27 September, option A, code at `b0efe23`). **Finding 6 is done**
(ruled 27 September, the stop comes from ATR alone, code at `76c8cde`). **Finding 5 is
done** (ruled 27 September, panel only, code at `8b9ac1e`). **Finding 18 is done**:
ruled on 27 September (the bias label is a function of the score; no new rule), and its
code lands with the commit that writes this line, after the live run and the
decision-log record were read (the commit message has what the record showed). **All
six of Viktor's findings are done. Work order G is the last item on the closed list**,
and after it the independent audit.

**Nothing Claude does under the delegation decides the engine's trading rules.**
Findings 4–7, 16 and 18 are questions about what the engine should do. They are
Viktor's, and none of Claude's commits touches them. G changes which trades are taken.
It is Claude's under the delegation, and it gets full scope, the live log checked first,
and the live run before the commit.

**The independent audit is paused, and has an end** — DECISIONS, "Ruling, 21 September
2026 — the independent audit paused" and "Ruling, 22 September 2026 — when the audit
resumes". **The Constitution's step 8 binds:** "Re-audit the items that changed —
independent auditor again, not a self-check by whoever made the fix. 9) Only then …
build the backtesting architecture." No engine change since the last independent round
(round 6 fix-verification, 14 September) has been independently re-audited, so **no
backtesting before an independent re-audit.** Claude's second point in the 21 September
ruling is still open: the no-backtest rule exists only as text.

**This session (27 September, the sixteenth, the one after `8b9ac1e`)**, under Claude
Opus 5.5, opened on "Continue Phase 7". **A wrong turn, recorded:** Claude opened by
saying finding 5 was ruled but not yet built, from its own notes between sessions, and
Viktor asked for it to be built. Before any work Claude cloned GitHub and read `master`
and `origin/master` off his disk: all three were `8b9ac1e`, finding 5's code, committed
and pushed by the fifteenth session minutes earlier. Nothing was rebuilt; the notes had
been written before that commit. The start-of-session read of the refs is what caught
it, which is why it is kept (DECISIONS, the ruling on proposal (b)).

Then finding 18. Before Viktor wrote anything, Claude read the code and found the
finding's premise false: the "state machine" never read its previous state, so there
was no persistence requirement to gate anything — CONFIRMED only ever meant
|`bias_score`| > 30. Claude set out four options (label only; real persistence; the
same labels from a plain function; a CONFIRMED gate), Viktor asked for Claude's
suggestion and ruled by agreeing to it (DECISIONS, "Ruling, 27 September 2026 — the
bias label is a function of the score (finding 18)"). **A second wrong claim, caught
before the build:** Claude told Viktor `tests/test_plan_direction_and_side.py` uses the
class; it only names it in its docstring, and no test exercised the class at all. The
change moves `code_hash` and no decision, so the live run and the read of its log
record come before the commit step.

## Ruled — in force

- **The order of work is delegated to Claude** (Viktor, 21 September: "Organize a to do
  list and we start working, It is up to you."). It covers ordering and the items marked
  Claude's below; it does not cover the items marked Viktor's.
- **The audit is paused**, and **work order F is ruled** — both in DECISIONS, 21
  September.
- **When the audit resumes** (DECISIONS, 22 September): once work order G and findings
  4, 5, 6, 7, 16 and 18 are done. A finding is done when Viktor has ruled it and any code
  his ruling calls for has landed; a ruling to leave it as it is counts. The list is
  closed.
- **New, 27 September — the plan is measured from the decision close (finding 4)**
  (DECISIONS, "Ruling, 27 September 2026 — the plan is measured from the decision close
  (finding 4)"). Option A: the decision close is the plan's single entry; the band is
  labelled EMA BAND; a backtest fills at the next candle's open and records the gap
  (added to Goal B's methodology); entering at the band goes on the list for after the
  audit. **Its code landed at `b0efe23`.**
- **New, 27 September — the stop comes from ATR alone (finding 6)** (DECISIONS,
  "Ruling, 27 September 2026 — the stop comes from ATR alone (finding 6)"). The HVN no
  longer pulls the stop and stays as information only; the 8% and 15% limits are
  unchanged; nothing checks HVN proximity, which goes on the list for after the audit;
  a swing-structure anchor was not chosen and not measured. Ruled by agreeing to
  Claude's suggestion, not by writing his position first. **Its code landed at
  `76c8cde`.** **Confirmed 27 September (the next session):** Claude's reading of
  "information only" stands — only the stop stopped using the HVN; the entry score's,
  the reversal reading's and the Exit Watch's uses stay, and revisiting them belongs
  with the `bias_score` weighting review after the audit. Also by agreeing to Claude's
  suggestion (DECISIONS, under the finding 6 ruling).
- **New, 27 September — a NEUTRAL bias prints no plan (finding 5)** (DECISIONS,
  "Ruling, 27 September 2026 — a NEUTRAL bias prints no plan (finding 5)"). Panel only:
  no stop, targets or R:R, and one PLAN line naming the NEUTRAL bias and its score
  inside ±20. The engine still computes and logs the plan; the risk check needs a stop.
  Ruled by agreeing to Claude's suggestion, not by writing his position first. **Its
  code landed at `8b9ac1e`.**
- **New, 27 September — a push that goes as predicted leaves nothing owed** (DECISIONS,
  "Ruling, 27 September 2026 — a push that goes as predicted leaves nothing owed").
  Claude's proposal (b) of 26 September, adopted by agreeing to Claude's suggestion. A
  push is recorded once, in the next commit's account; only a deviation becomes an owed
  item. The floor-of-one chain of owed hook results ends.
- **New, 27 September — the bias label is a function of the score (finding 18)**
  (DECISIONS, "Ruling, 27 September 2026 — the bias label is a function of the score
  (finding 18)"). The behaviour stays exactly as it was: `BiasStateMachine`, which never
  read its previous state, becomes `bias_label(raw_bias, bias_score)` in
  `models/bias_engine.py`, the same labels word for word; no new trading rule and no
  CONFIRMED gate. "A side must hold for N closed candles" and renaming CONFIRMED go on
  the list for after the audit. Ruled by agreeing to Claude's suggestion, not by writing
  his position first. **Its code lands with the commit that writes this line.**
- **`bias_score`'s weighting waits for after the audit, and the auditor sees it**
  (DECISIONS, 22 September; filed at `75682ee`).
- **New, 26 September — any model may build or review; doing so costs it audit
  eligibility** (DECISIONS, "Ruling, 26 September 2026 — any model may build or review;
  doing so costs it audit eligibility"). No model other than Claude is in use now.
- **New, 26 September — the pre-send token check is audit preparation, not an engine
  item** (DECISIONS, "Ruling, 26 September 2026 — the pre-send token check is audit
  preparation, not an engine item"). It does not add to or reopen the closed list.
- **New, 26 September — the stop-distance finding is evidence for findings 4 and 6**
  (DECISIONS, "Ruling, 26 September 2026 — the stop-distance finding is evidence for
  findings 4 and 6"). Not part of G; the closed list is unchanged. The 8% ceiling is part
  of finding 6; the risk gate's position goes on the list for after the audit.
- **New, 26 September (ninth session) — where the project lives, Viktor's choice.** The
  repository is `E:\phase7_engine`; the files kept outside it are in
  `G:\Phase_7_Engine_Random_Files`. `D:\USB Backup\Phase7_Engine documents` stays where it
  is. The originals on D: are renamed `phase7_engine_MOVED_TO_E` and
  `Phase_7_Engine_Random_Files_MOVED_TO_G`; deleting them is Viktor's. He chose Claude's
  recommended option on all three (HISTORY, "26 September 2026 (ninth session) — the
  repository moved to `E:\phase7_engine`").
- **New, 26 September (tenth session) — the phase-3 order: 16, 7, 4, 6, 5, 18, then G
  last.** Proposed by Claude under the 21 September delegation of the order of work;
  Viktor agreed it on 26 September. One finding at a time, at his pace.
- **New, 26 September (tenth session) — finding 16: decisions are made on closed
  candles** (DECISIONS, "Ruling, 26 September 2026 — decisions are made on closed
  candles (finding 16)"). All three series; the live price shown as information only;
  staleness measured from the close time, requiring the latest closed candle; the log
  records each series' decision candle. **Its code landed at `add8540`.** How point 3
  reads (a run inside the grace fails), the 60-second grace
  with its evidence, the pinned-data treatment and the panel's labels are recorded under
  the ruling, "Recorded when its code landed" (eleventh session).
- **New, 27 September — finding 7: indicator values are no longer replaced beyond
  5 sigma** (DECISIONS, "Ruling, 27 September 2026 — indicator values are no longer
  replaced beyond 5 sigma (finding 7)"). The replacement is removed from
  `clean_series`; the inf-to-NaN step stays; checking the candles for bad data goes on
  the list for after the audit. **Its code landed at `57f0521`.**

## Where things stand, right now

- **Tip:** the commit that writes this line (a commit cannot name its own hash) —
  finding 18's ruling and code; it changes no decision and no label. Before it:
  `8b9ac1e` (the fifteenth session's commit: finding 5's code), `76c8cde` (the
  fourteenth session's commit: finding 6's code), `b0efe23` (the thirteenth session's
  commit: finding 4's code), `57f0521` (the twelfth session's commit: finding
  7's code), `add8540` (the eleventh session's first commit: finding 16's code),
  `bf2e802` (the tenth session's first commit: finding 16 ruled), `7d103d7` (the ninth
  session's first commit: the move to E:), `eba6a2a` (the eighth session's third
  commit), `1861208` (the stop-distance ruling), `2582994` (the eighth session's first
  commit: two rulings), `75682ee` (the seventh session's owed filing and the round-1
  audit outputs), `bc48f59` (the Engineering Notes regenerated at v1.35), `c5dc4cd`,
  `e804b64`, `5e55eb8`, `3bfa6b7` (`data/data_fetcher.py`: finding 27). F itself is
  `3f263c2`. **Tag:** `portfolio-v1` at `99e022e`. **Release gate:** open, declared
  15 September 2026.
- **Where the project lives, from 26 September:** `E:\phase7_engine` on Viktor's machine;
  the files kept outside the repository in `G:\Phase_7_Engine_Random_Files`. Copied with
  robocopy, verified — git's own checks on Windows for the tracked files, SHA-256 for the
  91 ignored data files and the 25 Random Files — and only then the originals renamed.
  The evidence is in HISTORY, "26 September 2026 (ninth session) — the repository moved
  to `E:\phase7_engine`". Run the engine and every command from `E:\phase7_engine` (in
  cmd, changing drive needs `cd /d`). A dated record that names the D: paths means the
  same folders before the move; dated records are not edited.
- **The push of `8b9ac1e`** happened: this session read `master` and
  `origin/master` off Viktor's disk (`.git/refs/heads/master` and
  `.git/refs/remotes/origin/master`, staged; written 14:34:16 and 14:34:29 local) and
  GitHub's tip from a fresh clone, all three `8b9ac1e`. Viktor reported no deviation
  from that push's prediction, so it is recorded here once, as predicted, and **nothing
  is owed** (ruling on proposal (b)). The same holds for the push of the commit that
  writes this line unless it deviates.
- **Before this commit**, every file it changes matched Viktor's disk on E: byte for
  byte (staged off his disk and compared with the clone at `8b9ac1e`).
- **code_hash:** `f4b23f94ca9b0562c5c68a756fbd45222f6e11f9ecb78efaa75fcb4817142183`,
  moved by the commit that writes this line (from `c636157…`, which held from
  `8b9ac1e`): `models/bias_engine.py` and `core/engine_core.py`, the only two per-file
  fingerprints that changed (checked against every file; the comment and docstring
  changes in `models/entry_model.py`, `models/decision_model.py` and
  `models/risk_model.py` move none, as predicted). Computed on the working tree and on
  the applied tree under Python 3.12.3. Confirmed on Windows before the commit by
  Viktor's live run, whose decision-log record Claude read — the commit message has it.
- **code_hash is only comparable within one Python minor version.** It hashes `ast.dump`
  output, a CPython implementation detail (`core/code_fingerprint.py`, "WHAT IT DOES NOT
  SURVIVE"). **Every `code_hash` claim about this project is computed under Python 3.12**
  (Viktor runs 3.12.10).
- **Golden snapshot:** unmoved by the commit that writes this line, as predicted: it
  pins `bias.detailed` (BULLISH CONFIRMED) and `btc_context.detailed` (BEARISH
  CONFIRMED), and `bias_label` gives the same labels; no fingerprinted constant changed,
  so `run_hash` is unmoved too. Unmoved at `8b9ac1e` as well. Last re-baselined at
  `76c8cde`, 11 fields, as predicted before that run: `exit.action` (NO-TRADE (RISK TOO
  HIGH) → CONSERVATIVE LONG), `explanation.reasons`, `explanation.summary`,
  `exit_watch` (the Target 1 price), `risk.atr_stop`, `risk.targets`,
  `risk.risk_valid`, `risk.risk_reason`, `risk.risk_regime`,
  `lineage.risk_inputs.risk_regime` (UNKNOWN → NORMAL RISK) and
  `lineage.risk_inputs.structural_level` (removed). Before that, last re-baselined at
  `add8540`.
- **Test suite** — moved by the commit that writes this line: **652 passed / 0 failed,
  no warnings line** with `pandas_ta`; **507 passed / 134 skipped** without it;
  `run_tests.py` **581 passed / 0 failed / 32 errors**, all 32 fixture-collection
  `TypeError`s (unchanged: the new tests take no fixtures). Linux sandbox, autocrlf
  clone, Python 3.12.3, pinned requirements, applied tree. +7 in
  `tests/test_bias_label.py`, none of which needs `pandas_ta`. **On Windows**, the
  counts Viktor was told to stop on in this commit's command sequence; he proceeded,
  which is his confirmation. Before that, 645 at `8b9ac1e`.
- **Engineering Notes:** through Entry #166 (v1.35), which covers `c5dc4cd`. **Thirteen
  commits behind** — `bc48f59`, the floor (a commit that regenerates the Notes cannot
  cover itself, Entry #144), `75682ee`, `2582994`, `1861208`, `eba6a2a`, `7d103d7`,
  `bf2e802`, `add8540`, `57f0521`, `b0efe23`, `76c8cde`, `8b9ac1e`, and the commit that
  writes this line. Every later commit adds one until the next regeneration, which also
  records the round-1 recovery, the rulings of 26 and 27 September, the phase-3 order,
  the move to E: and the code for findings 16, 7, 4, 6, 5 and 18. No time pressure
  (Viktor, 26 September).
- **Portfolio Document and AI-Attribution Statement:** both current with their scripts,
  which last changed at `6e1baba`.
- **README.md:** changed by the commit that writes this line — its two test-count
  passages only (652 / 507 + 134 skipped / 581). So the hook's section 5 will report 0
  commits since README.md was touched (expected).
- **The round-1 audit outputs are in the repository**, in
  `docs/audit_reports/round1_deepseek-v4-pro_kimi-k3_2026-08-27/`, byte-identical to the
  hashes Viktor took on 23 September. The account is in HISTORY, "26 September 2026 —
  correction: the round-1 audit outputs were recovered".

## Carried lesson — the live run comes BEFORE the commit

At F the live run asked for in the command sequence did not happen before the commit:
at the push the log still held 29 records, the newest on the old `code_hash`. Claude
caught it by reading the log, not from a paste. **On every change that moves
`code_hash` — and always on one that touches the decision path (G is one) — the live
run and the panel read happen before `git commit`, and Claude checks the decision-log
record for the new `code_hash` before the commit step, not after the push.** Never
predict live numbers; check the record. Followed at `2c7a7d1`, `4e2b1c8`, `486f1a5`,
`3bfa6b7`, `add8540`, `57f0521`, `b0efe23`, `76c8cde`, `8b9ac1e` and the commit that writes this line: the command
list stopped at the live run, Claude read the record, and only then gave the commit steps. **Since finding 16, a
live run in the first 60 seconds after a 4h close (00:00, 04:00, 08:00, 12:00, 16:00,
20:00 UTC) fails by design** ("not yet final"); run again a minute later.

## Sandbox practice

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
- **Seventh session:** `docs/audit_reports/**` is `-text`, so its files are committed and
  checked out byte for byte, LF or CRLF as they came; compare them by hash, never after a
  line-ending conversion. The session's hashes of the round-1 files are in HISTORY
  (26 September).
- **Sixth session:** `reportlab` 5.0.1 (not pinned; `docs/build/README.md` has the
  install line) rebuilt the committed Notes PDF from `5e55eb8` with identical extracted
  text, so it is a sound baseline for the Notes. The PDF embeds a build timestamp, so
  its bytes differ on every run.
- **Eighth session:** a `git status --short` prediction built from the clone cannot see
  untracked files on Viktor's disk (the push of `75682ee`; its account is in HISTORY).
  Before predicting it, list his repository over the device bridge and compare it with
  the clone's tracked and ignored files.
- **Ninth session:** the repository is at `E:\phase7_engine` on Viktor's machine (moved
  26 September), so the device bridge needs that folder granted, and every device path
  in a delivery names E:. `D:\phase7_engine` no longer exists under that name.
- **Tenth session:** the session had no shell on Viktor's machine, only file staging, so
  his tip was read from `.git/refs` staged off his disk, not from `git log`.
- **Eleventh session:** the same (file staging only). The scope stated before the diff
  missed two consequences the suite then caught: `core/decision_contract.py` must
  declare every provenance field (`test_decision_contract.py`), and a panel label that
  starts with `DECISION` is found by `test_setup_direction_box.py`'s "starts with
  DECISION" search before the DECISION line itself. Both are in the commit message. A
  new panel label should be checked against every `startswith` search over the panel.
- **27 September:** file staging only again. Before removing a rule, instrument it (a
  line that logs when it fires, run on the golden test and the fixture frames, then
  restore the file and `cmp` it) — that is how the golden prediction for finding 7 was
  made from evidence rather than from reading.
- **27 September, finding 6:** re-derive a ruling's evidence before filing it. The
  figures handed over with the ruling said 29 of 39 pass and 7 are refused, which does
  not add up to 39; recomputed from the staged log, 32 pass (29 of them newly). Also:
  `core/code_fingerprint.py` strips docstrings and the AST has no comments, so a
  docstring- or comment-only change moves no per-file fingerprint — checked per file,
  not assumed. And when a parameter is removed, check every call that passed it for a
  test that would now pass for the wrong reason: the `detailed_bias` test still passed
  `structural_level=None`, which would have raised the TypeError on its own.
- **27 September, finding 5:** a negative control can fail to fail because a second
  guard also holds. Breaking the NEUTRAL check in `decision_model` alone left the grid
  green: a NEUTRAL score is inside ±20, and `MIN_ACTION_BIAS` (30) sends any
  lean under 30 to WAIT, so a NEUTRAL bias misread as BULLISH still never trades. The
  control that fails breaks the path past both. And a `sed` meant to break one line
  matched two (`if plan_withheld:`); controls are now edited by an exact, counted
  replacement.
- **27 September, finding 18:** a name is a claim, not evidence. "State machine",
  `state` and `transition()` read as memory, and the record built a finding on it; the
  method body never read `self.state`. Read what a unit does before reasoning from what
  it is called. Also: Claude's notes between sessions can be behind the repository —
  read `master` and `origin/master` off Viktor's disk before proposing any build
  (this session's first finding). And a new UPPER_CASE numeric constant in a
  fingerprinted module is caught by `test_fingerprint_names_every_constant.py` and has
  to enter `FINGERPRINTED_MODULES`, which moves `run_hash` and the golden snapshot —
  weigh that before naming a number.

## Review findings, 21 September 2026

Read at `635a94e` from Viktor's disk and from an autocrlf clone. **Every finding comes
from reading the code; none was reproduced by running the engine** unless it says so.
Line numbers are as read at the commit each entry names. Since finding 6's commit,
`current_price` is at `core/engine_core.py:1063` and the stop-and-targets call at
`:1111–1117` (this line said `:1060` and `:1101–1108`, set at finding 16; finding 4's
comments had already moved them by three).
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
   T1–T3 and all three R:R values come from `current_price` (`engine_core.py:1005`); the
   zone is EMA20–EMA50. LONG is authorised without price in the zone (entry score ≥ 70 is
   reachable at NEAR ZONE), and CONSERVATIVE LONG has no zone condition at all. The
   printed R:R holds only for an entry at the current price. There is no single entry
   price on the panel. A backtest must fill somewhere, so this needs ruling first.
   **Ruled 27 September, option A; done with the commit that writes this line**
   (DECISIONS, "Ruling, 27 September 2026 — the plan is measured from the decision close
   (finding 4)"). The panel now names the decision close as the plan's entry and labels
   the band EMA BAND; a backtest fills at the next candle's open. Entering at the band
   is on the list for after the audit (below). **Code landed at `b0efe23`.** Done.
5. **A NEUTRAL bias still prints a full plan.** The plan's direction comes from
   `bias_score >= 0` (`models/risk_model.py`, since C), so a score between −20 and +20
   prints a long- or short-shaped stop and targets under a NEUTRAL bias with no
   direction box; exactly 0 prints a long.
   **Ruled 27 September: panel only; done with the commit that writes this line**
   (DECISIONS, "Ruling, 27 September 2026 — a NEUTRAL bias prints no plan (finding
   5)"). Under a NEUTRAL bias the panel prints no stop, targets or R:R, and one PLAN
   line; the engine still computes and logs the plan. Tests in
   `tests/test_neutral_bias_prints_no_plan.py`. Done.
6. **The stop is pulled to the 75-day volume point of control, with no distance limit.**
   `structural_level=hvn` (`engine_core.py:1050`); for a long the stop is
   min(HVN, ATR stop). The HVN is the single highest-volume bin of the whole 450-candle
   frame (`indicators/volume_profile.py`, 50 bins) — about 75 days on 4h. A trend that
   has moved away from its point of control therefore gets its stop there, and past 8%
   the risk check fails: NO-TRADE (RISK TOO HIGH). Between 8% and 15% the setup is
   classified EXTREME RISK (`models/risk_model.py:439`, `:524–526`); past 15% the
   distance limit refuses it first and RISK REGIME reads UNKNOWN (`:516–520`). This text
   said "past 15%" until 26 September, when the code was read. Seen on Viktor's
   live runs of 21 September at 05:28, 05:51 and 06:18 and on the pinned golden fixture,
   each checked against the record (details in HISTORY); the 19:24 run's action was again
   RISK TOO HIGH on the HVN stop. How often this vetoes a setup across many runs was not
   measured. **Dependency added at F:** the confirmation gate no longer blocks on HVN
   proximity, on the reasoning that this stop already acts on that area. If this finding
   is ruled to stop pulling the stop to the HVN, nothing checks HVN proximity.
   **Ruled 26 September:** the 8% ceiling is part of this finding, and the count under
   "Evidence for findings 4 and 6" below is its measurement.
   **Ruled 27 September: the stop comes from ATR alone; done with the commit that
   writes this line** (DECISIONS, "Ruling, 27 September 2026 — the stop comes from ATR
   alone (finding 6)"). `calculate_stop_targets` no longer takes a structural level,
   `engine_core` passes no HVN, and `lineage.risk_inputs` no longer lists one; the 8%
   and 15% limits are unchanged. Tests in `tests/test_stop_is_atr_only.py`. The
   dependency above is now in force: nothing gates on HVN proximity (list for after the
   audit, below). **Code landed at `76c8cde`.** Done.
7. **Indicator values beyond 5σ are silently replaced by the previous bar's.**
   `indicators/indicators.py:105–110`, inside `clean_series`, which EMA, RSI, ADX,
   SuperTrend and ATR all pass through. Nothing records the replacement — unlike volume
   spikes (`:746`), which are kept and flagged. At the decision bar the replaced value
   becomes a reported indicator *failure*. The mean and standard deviation span the
   whole frame, so a backtest that computes indicators once over its history would leak
   future bars into past decisions. Reachability on live data: not measured.
   **Ruled 27 September: the replacement is removed, the inf step kept** — DECISIONS,
   "Ruling, 27 September 2026 — indicator values are no longer replaced beyond 5 sigma
   (finding 7)". **Code landed at `57f0521`**; tests in
   `tests/test_no_outlier_replacement.py`. Done.
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
    **Ruled 26 September (tenth session): decisions are made on closed candles** —
    DECISIONS, "Ruling, 26 September 2026 — decisions are made on closed candles
    (finding 16)". Re-read on 26 September: `fetch_ohlc` names `close_time` and drops it
    (`data/data_fetcher.py:346–358`); three series are fetched (`core/engine_core.py:422`,
    `:472`, `:755`); `current_price` is the last row's close (`:1005`). **Code landed
    at `add8540`**:
    `fetch_ohlc` drops the forming candle before validation and records it; the
    staleness check measures from the decision candle's close with a 60-second grace;
    `provenance.decision_candles` records each series; the panel prints DECISION CLOSE
    and a LIVE PRICE line. Done.
18. **The bias state machine gates no trade since F.** Viktor dropped the CONFIRMED
    requirement so the signal follows `raw_bias`, as `decision_model` does.
    `detailed_bias` still feeds `exit_model`'s "bias state changed" flag and the
    persisted state; nothing that decides reads it. Recorded, nothing removed. Whether
    its persistence requirement should gate anything is Viktor's call.
    **Corrected 27 September, from the code:** there was no persistence requirement.
    `BiasStateMachine.transition()` never read its previous state, and an instance
    lived one run; CONFIRMED only ever meant |`bias_score`| > 30, and the ladder already
    needs ≥ 30 to act. On Viktor's log all 42 recorded AERO labels are what the current
    score gives. **Ruled 27 September: the same labels from a function with no state;
    done with the commit that writes this line** (DECISIONS, "Ruling, 27 September
    2026 — the bias label is a function of the score (finding 18)"). `bias_label` in
    `models/bias_engine.py`; tests in `tests/test_bias_label.py`. Done.

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

## Evidence for findings 4 and 6 — the stop-distance count

**Both findings are done** (4 at `b0efe23`, 6 at `76c8cde`), so
this section is now a pointer. The count of 26 September (37 records: 33 NO-TRADE (RISK
TOO HIGH), 29 of them on the distance limit; the ladder replay) is in HISTORY, in this
file's version at `b0efe23`, "Evidence for findings 4 and 6". The ATR-only recount of
27 September that finding 6 was ruled on, with its correction, is in DECISIONS, "Ruling,
27 September 2026 — the stop comes from ATR alone (finding 6)". **Two things from it
still stand:** G cannot change a refusal made by the risk gate (the verdict returns at
`models/decision_model.py:500–502`, before the ladder); and passing the risk check is not
a trade — the ladder and the confirmation gate still decide. **What to watch for now:**
the decision log will show how often runs refused only on the HVN stop become trades
under ATR alone. On the newest records (26 and 27 September) volatility was EXTREME, and
EXTREME VOLATILITY is refused as EXTREME RISK whatever the stop.

## Found after 22 September — for after the next audit

The 22 September ruling closed the list above. A finding made from now on is recorded
here, with its evidence, and waits until after the independent audit; it does not move
the audit. Whether the auditor is shown this section is part of the package question,
Viktor's when the audit is planned.

- **The risk gate runs before the bias checks.** The risk verdict returns at
  `models/decision_model.py:500–502`, before the weak-validation and lean checks at
  `:605–617`, so a run the ladder would have answered WAIT is reported as NO-TRADE (RISK
  TOO HIGH). In the log counted on 26 September this was 2 of the 33 refused runs. It
  changes what the panel says, not which trades are taken. Found by Claude reading the
  code, 26 September; **ruled for after the audit** (Viktor, 26 September).
- **Checking the candles for bad data.** On price, `data/validation.py` rejects NaN,
  inf, non-positive values and impossible candles, nothing else, so an extreme but
  internally consistent print reaches the indicators; since finding 7 nothing erases
  it downstream either. **Ruled for after the audit** (Viktor, 27 September, point 3 of
  the finding 7 ruling).
- **Entering at the EMA band (option B of finding 4).** The plan becomes a limit order
  at the band's edge, with stop, targets and R:R measured from there, and an expiry if
  price does not reach it. It changes which trades are taken. Claude noted, unmeasured,
  that an entry at the band on a pullback sits nearer the stop and might meet fewer
  distance refusals — the gate behind most NO-TRADEs; the decision log can measure it.
  **Ruled for after the audit** (Viktor, 27 September, point 4 of the finding 4 ruling).
- **Nothing gates on HVN proximity.** Work order F removed HVN proximity from the
  confirmation gate because the HVN stop acted on that area; finding 6 removed the HVN
  stop. The HVN still weighs — the entry score's structure points and trend_health's
  reversal reading — but vetoes nothing, so a long can be authorised directly under a
  high-volume node. **Ruled for after the audit** (Viktor, 27 September, point 3 of the
  finding 6 ruling).
- **`lineage.risk_inputs` leaves out an input to the stop.** `calculate_stop_targets`
  scales the ATR by `trend_factor`, which reads `trend_health`
  (`models/risk_model.py`, the line `trend_factor = 1.0 + …`), so trend health sets the
  stop distance, and through it the 8% and 15% checks. `risk_inputs` does not record
  it, and its comment in `core/engine_core.py` (ITEM 14, 11 September) says trend_health
  "no longer" feeds the risk decision — true of the regime classification, not of the
  stop. The value is still in the record, at `trend.trend_health`: the recount of
  27 September needed it to reproduce the logged stops. Found by Claude reading the code
  while building finding 6, 27 September; on this list by the 22 September ruling, not
  separately ruled. A lineage change would move the golden snapshot.
- **Under a NEUTRAL bias the entry score is measured for a side nothing chose.**
  `core/engine_core.py` scores entry quality for `eq_trade_direction`, which under a
  NEUTRAL bias is the sign of `bias_score` (the line `eq_trade_direction = "LONG" if
  bias_score >= 0 else "SHORT"`) — the same rule finding 5 found in the plan. The panel
  still prints ENTRY QUALITY and TRADE QUALITY for it; finding 5's ruling covers the
  stop, targets and R:R only. It decides nothing: a NEUTRAL bias never reaches a side.
  Found by Claude reading a rendered NEUTRAL panel while building finding 5,
  27 September; on this list by the 22 September ruling, not separately ruled.
- **A side that must hold for N closed candles before a trade.** What finding 18's
  text assumed the state machine did; it never did. A new trading rule, so not built
  now. If built: compute it from the closed candles in the run's own input, which the
  input hash pins, not from a state file. **Ruled for after the audit** (Viktor,
  27 September, point 3 of the finding 18 ruling).
- **The word CONFIRMED on the panel.** It reads as a lean that has held for a while; it
  means |`bias_score`| > 30. Renaming it moves a panel label and the golden snapshot.
  **Ruled for after the audit** (Viktor, 27 September, point 4 of the finding 18
  ruling). Recorded with it, not ruled: at exactly 30.0 the ladder can take a side
  (`MIN_ACTION_BIAS`, ≥ 30) while the label reads BULLISH or BEARISH (> 30 needed) —
  noted beside `MIN_ACTION_BIAS` in `models/decision_model.py`.

## Work order — Claude's, under Viktor's delegation

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
  The live run happens before the commit (above). **The last item on the closed list,
  and next.** Not started.

## Resolved this session

- **Finding 18** — its premise corrected from the code (no persistence existed), ruled
  by agreeing to Claude's suggestion (the same labels from a function with no state),
  and its code landed by the commit that writes this line; finding 18 is done. All six
  of Viktor's findings on the closed list are done.
- **The push of `8b9ac1e`** — filed above, once, as predicted.
- **Claude's stale opening claim** (finding 5 "not yet built") — caught by reading the
  refs off Viktor's disk before any work; recorded above.
- **The once-per-session rewrite of this file.** The previous version, as at `8b9ac1e`,
  is in HISTORY verbatim, headings demoted one level, proven by un-demotion with a
  negative control (the commit message has the result).

## Open items

Items marked **Viktor's call** are his to decide; he writes his position first and
Claude critiques it.

- **Owed to the next commit:** nothing, unless this commit's push deviates from its
  prediction (ruling on proposal (b), 27 September).
- **Viktor, outside the repository:** delete `D:\phase7_engine_MOVED_TO_E` and
  `D:\Phase_7_Engine_Random_Files_MOVED_TO_G` once satisfied with the copies on E: and
  G: (HISTORY, 26 September, ninth session). Not urgent.
- **Claude's — work order G (finding 17).** The last item on the closed list before
  the audit, and **next**. Changes which trades are taken: full scope first, the live
  log checked for which recorded actions it would change, and the live run before the
  commit. Whether to start it is Viktor's to say (PACE FIRST).
- **Claude's — the pre-send token check** (audit preparation, ruled 26 September). It
  cannot be finished until the auditor is pinned, because it needs that model's
  tokenizer; until then it can be built with the model as a parameter. It goes under
  `docs/`, which `core/code_fingerprint.py` excludes by directory, so it cannot move
  `code_hash`; it takes a line in `docs/audit_change_list.md`. Not started.
- **Viktor's call — the next independent auditor.** Claude recommends Nemotron 3 Super or
  Poolside Laguna S 2.1 (both 1M context, open weights, pinnable, labs not in the
  project's record). Mistral Large 3 is out for a full round (256K context). The ranking
  is in "Phase-7 — Model Roster" (22 September, outside the repository, filed as
  `The_clean_slate_model_list.pdf`; it supersedes the clean-slate list). Not decided.
- **The independent audit — paused until the closed list is done** (DECISIONS, 21 and
  22 September). When it is planned, still Viktor's: which model, the package (the
  standing default for a fresh Tier-1 audit is the full package), whether the auditor
  sees the rest of the 20 September scrapped findings and the list for after the audit,
  and the instruction for the selected model. The auditor is shown the `bias_score`
  weighting findings (ruled). No backtesting before the audit.
- **The independence ledger is outside the repository and not yet reconciled** —
  `Phase7_Spent_Models_Ledger_2026-09-22.pdf`, built from README.md and the
  AI-Attribution Statement, not from provider exports. **Owed to it: Grok's entry.** The
  ledger shows Grok as not having seen engine source. Grok's own account of what it read,
  given on 26 September: the Constitution and the Assistant Instruction in full; README
  and this file at about `c5dc4cd`; production code in `main.py`, `live_trading.py`,
  `data/`, `core/`, `models/`, `indicators/` and `structure/`; the full `tests/` tree and
  fixtures; one live panel Viktor pasted. It is Grok's account, not a provider export.
  Saved unchanged, at Viktor's request, as
  `Docs\02_Reviews_and_Feedback\Grok_Inventory_of_What_It_Read_2026-09-26.txt` in
  `G:\Phase_7_Engine_Random_Files` (SHA256 `0d923a095bc112bda5ad11e6be39a98f0d5a48ad`
  `139938ed119d18ebd96a71ed`, as written by Claude; unchanged after the move from D:
  on 26 September).
  Grok is ineligible to audit the engine (DECISIONS, 26 September). Its review
  (`ASSISTING_MODEL_REVIEW_2026-09-23.md`, outside the repository) is received, not
  triaged; by its own text it is not an audit, and anything accepted from it goes on the
  list for after the audit.
- **Viktor has stopped using Grok.** Its test run reported 458 passed, 126 skipped and
  2 failed — together the recorded 460 without `pandas_ta` — and it put the two failures
  down to repository checks without resolving them. Claude's reading, not reproduced:
  one is likely `tests/test_session_handover_check_ignored_filter.py`, which needs a
  `git` executable; the other was not in the five test files read. No model other than
  Claude is in use.
- **Viktor's call, not ruled — Claude's point (2) of 21 September:** the rule "no
  backtesting before re-audit" exists only as text; a structural form would be a
  backtest entry point that refuses to run without a recorded re-audit.
- **Viktor's call — repointing `docs/build/build_findings_bundle.py`** at the round-1
  folder, so `Phase7_Audit_Findings_Complete.pdf` could be rebuilt. A tooling change;
  not done.
- **Claude's — the running change list for the audit:** `docs/audit_change_list.md`,
  from the baseline `e65a0f7` (the tree round 6's fix-verification was sent). **Every
  later commit that changes engine code, tests or tooling adds its line there in the
  same commit.** Finding 18's commit adds its line, and names `8b9ac1e` in the line that
  finding 5's commit wrote as "the commit that adds this line".
- **The pre-push hook is installed per clone, not per repository.** After any re-clone
  (including after a machine wipe), run `git config core.hooksPath githooks`;
  `session_handover_check.py` section 6 flags a clone without it.
- **Unrelated, not urgent:** confirm which YH programme permits AI-assisted
  examensarbete work.
