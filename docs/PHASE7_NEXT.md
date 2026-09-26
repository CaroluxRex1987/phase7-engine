# Next step — read this first

*26 September 2026, ninth session. Rewritten by this session's first commit, the one
that records the move of the repository to `E:\phase7_engine` and files what the push of
`eba6a2a` owed; the version it replaces — as it stood at `eba6a2a` — is in HISTORY
verbatim.
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
not onto this one. None of the closed list has started.

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

**The ninth session (26 September)** is a new chat on the same day as the eighth, under
Claude Opus 5.5. It opened on Viktor's message: phase 3 of the roadmap to the audit ("Phase
7 roadmap to the independent audit", a Claude Docs document outside the repository) —
his findings 4, 5, 6, 7, 16 and 18 and Claude's work order G, one finding at a time, his
position first — and one item owed by the push of `eba6a2a`. Before phase 3 started,
Viktor moved the project to two new drives on his machine (below, "Where things stand",
and HISTORY). Phase 3 has not started; Viktor names the finding it starts with.

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

## Where things stand, right now

- **Tip:** the commit that writes this line (a commit cannot name its own hash) — the
  ninth session's first commit; documentation only. Before it: `eba6a2a` (the eighth
  session's third commit), `1861208` (the stop-distance ruling), `2582994` (the eighth
  session's first commit: two rulings), `75682ee` (the seventh session's owed filing and
  the round-1 audit outputs), `bc48f59` (the Engineering Notes regenerated at v1.35),
  `c5dc4cd`, `e804b64`, `5e55eb8`, `3bfa6b7` (the last code commit,
  `data/data_fetcher.py`: finding 27). F itself is `3f263c2`. **Tag:** `portfolio-v1` at
  `99e022e`. **Release gate:** open, declared 15 September 2026.
- **Where the project lives, from 26 September:** `E:\phase7_engine` on Viktor's machine;
  the files kept outside the repository in `G:\Phase_7_Engine_Random_Files`. Copied with
  robocopy, verified — git's own checks on Windows for the tracked files, SHA-256 for the
  91 ignored data files and the 25 Random Files — and only then the originals renamed.
  The evidence is in HISTORY, "26 September 2026 (ninth session) — the repository moved
  to `E:\phase7_engine`". Run the engine and every command from `E:\phase7_engine` (in
  cmd, changing drive needs `cd /d`). A dated record that names the D: paths means the
  same folders before the move; dated records are not edited.
- **The push of `eba6a2a`** printed `SUMMARY: clean`, section 1 "none", section 6
  "installed" and section 5 README.md 3 commits behind — as predicted (Viktor's message
  opening this session). Claude had fetched GitHub's tip after that push and found the
  documents it changed matched what was built (the eighth session). **Owed to the next
  commit:** the hook's result on the push of the commit that writes this line. Filing a
  push's result always leaves the filing commit's own push owed — a floor of one, like
  the Notes'. The earlier record of the hook is in HISTORY.
- **Before this commit**, the two documents it changes matched Viktor's disk on E: byte
  for byte.
- **code_hash:** `b3c2308f8f3e05981af25ee82468c071f7bf0b9d49519b6e75bd78c37b5fb365`,
  moved at `3bfa6b7` (`data/data_fetcher.py`); unmoved since, and by the commit that
  writes this line — computed on the tip's tree and on the applied tree under Python
  3.12.3. The move to E: cannot enter it: the walk records paths relative to the
  repository root (`core/code_fingerprint.py`). Confirmed on Windows before `3bfa6b7`'s
  commit by Viktor's live run of 21 September 23:29 (details in HISTORY, the entry for
  this file at `bc48f59`).
- **code_hash is only comparable within one Python minor version.** It hashes `ast.dump`
  output, a CPython implementation detail (`core/code_fingerprint.py`, "WHAT IT DOES NOT
  SURVIVE"). **Every `code_hash` claim about this project is computed under Python 3.12**
  (Viktor runs 3.12.10).
- **Golden snapshot:** unmoved by the commit that writes this line. Last re-baselined at
  `2c7a7d1` (finding 22; no decision field).
- **Test suite** — unmoved by the commit that writes this line (documentation only; no
  test reads this file or HISTORY): **597 passed / 0 failed, no warnings line** with
  `pandas_ta`; **460 passed / 126 skipped** without it; `run_tests.py` **526 passed / 0
  failed / 32 errors**, all 32 fixture-collection `TypeError`s. Linux sandbox, autocrlf
  clone, Python 3.12.3, pinned requirements, applied tree. Last moved at `3bfa6b7`. **On
  Windows**, Viktor's `python -m pytest -q` in `E:\phase7_engine` at `eba6a2a`, right
  after the move: 597 passed (26 September).
- **Engineering Notes:** through Entry #166 (v1.35), which covers `c5dc4cd`. **Six
  commits behind** — `bc48f59`, the floor (a commit that regenerates the Notes cannot
  cover itself, Entry #144), `75682ee`, `2582994`, `1861208`, `eba6a2a`, and the commit
  that writes this line.
  Every later commit adds one until the next regeneration, which also records the round-1
  recovery, the three rulings of 26 September and the move to E:. No time pressure
  (Viktor, 26 September).
- **Portfolio Document and AI-Attribution Statement:** both current with their scripts,
  which last changed at `6e1baba`.
- **README.md:** not changed by the commit that writes this line; last changed at
  `75682ee`. So the hook's section 5 will report README.md 4 commits behind (expected).
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
predict live numbers; check the record. Followed at `2c7a7d1`, `4e2b1c8`, `486f1a5` and
`3bfa6b7`: the command list stopped at the live run, Claude read the record, and only
then gave the commit steps.

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

## Review findings, 21 September 2026

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
   T1–T3 and all three R:R values come from `current_price` (`engine_core.py:1005`); the
   zone is EMA20–EMA50. LONG is authorised without price in the zone (entry score ≥ 70 is
   reachable at NEAR ZONE), and CONSERVATIVE LONG has no zone condition at all. The
   printed R:R holds only for an entry at the current price. There is no single entry
   price on the panel. A backtest must fill somewhere, so this needs ruling first.
5. **A NEUTRAL bias still prints a full plan.** The plan's direction comes from
   `bias_score >= 0` (`models/risk_model.py`, since C), so a score between −20 and +20
   prints a long- or short-shaped stop and targets under a NEUTRAL bias with no
   direction box; exactly 0 prints a long.
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

## Evidence for findings 4 and 6 — the stop-distance count (26 September)

**The engine almost never trades, and one gate decides nearly all of it.** Viktor,
22 September, in chat. **Ruled 26 September: evidence for findings 4 and 6, not a new
item and not part of G** (DECISIONS, "Ruling, 26 September 2026 — the stop-distance
finding is evidence for findings 4 and 6"). What the code shows — read from staged
copies of Viktor's disk, which matched `75682ee`; the engine was not run:

- **G cannot change it.** `_determine_final_action` returns NO-TRADE (RISK TOO HIGH) on
  a failed risk verdict at `models/decision_model.py:500–502`, before the direction
  ladder whose CONSERVATIVE branches G would change (from `:619`). No refusal in the
  log is within G's reach.
- **Finding 6, confirmed.** For a long the stop is `min(hvn, calculated_stop)`, for a
  short `max(…)` (`models/risk_model.py:328–349`): the point of control can only widen
  the stop, never tighten it.
- **Finding 4, confirmed.** Stop and targets are measured from `current_price`, the
  last close (`core/engine_core.py:1005`, the call at `:1046–1053`).
- **RISK REGIME: UNKNOWN, confirmed.** Both distance refusals return before the regime
  is classified (`models/risk_model.py:516–522`); the inference of 22 September holds.
- **The ceiling is 8%, not 15%.** A stop 8–15% away is classified EXTREME RISK and
  refused (`risk_model.py:439`, `:524–526`); the 15% limit only decides which message
  prints. Finding 6's text above is corrected accordingly; ruled part of finding 6.
- **Count, 26 September**, of Viktor's `logs/phase7_decision_log_aerousdt.jsonl`, staged
  off his disk (last written 23 September, 00:01 UTC): 37 records, 6–23 September, all
  AEROUSDT 4h, test runs included — 33 NO-TRADE (RISK TOO HIGH), 3 WAIT, 1 SHORT
  (16 September), 0 LONG. Of the 33, 29 were refused on the distance limit (UNKNOWN)
  and 4 as EXTREME RISK (8.4–15.0%). The records cover 18 distinct last candles (one
  record lacks the field); on 16 of them every run was refused. Macro agreed with the
  raw bias in 31 of the 33.
- **What the refused runs would otherwise have been.** Replaying the ladder on the 33
  with the risk gate ignored gives 25 CONSERVATIVE, 6 at the LONG/SHORT tier and 2
  WAIT. This is Claude's re-implementation from reading, not engine output, and it
  leaves out the confirmation gate that runs after the ladder, so some of the 31 could
  still be refused there. It is the measurement finding 6 says "was not measured", on
  one symbol over one mostly rising period.
- The count of 22 September (35 runs, 31 NO-TRADE, 27 on the distance limit) was of an
  earlier copy; the two records added since are both distance refusals.

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
  The live run happens before the commit (above). Not started.

## Resolved this session

- **The move to E: and G:** — above ("Where things stand") and in HISTORY, with the
  evidence.
- **The push of `eba6a2a`** — filed above.
- **The once-per-session rewrite of this file.** The previous version, as at `eba6a2a`,
  is in HISTORY verbatim, headings demoted one level, proven by un-demotion with a
  negative control (the commit message has the result).

## Open items

Items marked **Viktor's call** are his to decide; he writes his position first and
Claude critiques it.

- **Owed to the next commit:** file the hook's result on this commit's push.
- **Viktor, outside the repository:** delete `D:\phase7_engine_MOVED_TO_E` and
  `D:\Phase_7_Engine_Random_Files_MOVED_TO_G` once satisfied with the copies on E: and
  G: (HISTORY, 26 September, ninth session). Not urgent.
- **Viktor's call — findings 4, 5, 6, 7, 16 and 18 above.** On the closed list before
  the audit. Not started.
- **Claude's — work order G (finding 17).** On the closed list before the audit.
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
  same commit.** This session's first commit is documentation only and adds none.
- **Viktor, outside the repository:** rotate the plaintext API key in `D:\USB
  Backup\Phase7_Engine documents\API KEY FROM OPEN CODE.txt` if it is still live. The
  file was not copied or opened.
- **The pre-push hook is installed per clone, not per repository.** After any re-clone
  (including after a machine wipe), run `git config core.hooksPath githooks`;
  `session_handover_check.py` section 6 flags a clone without it.
- **Unrelated, not urgent:** confirm which YH programme permits AI-assisted
  examensarbete work.
