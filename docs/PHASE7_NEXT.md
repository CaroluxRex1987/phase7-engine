# Next step — read this first

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

## PACE FIRST — read this before the rest of this file

Viktor judged, on his own, that 226 commits across 22 days had become hasty, and
ruled to slow down considerably (15 September 2026). **Do not open a session by
proposing work from "Open items" below, and do not treat it as a queue to clear.**
Ask what he wants to do first.

## Where the project is

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

## Ruled — in force

- **The order of work is delegated to Claude** (Viktor, 21 September: "Organize a to do
  list and we start working, It is up to you."). It covers ordering and the items marked
  Claude's below; it does not cover the items marked Viktor's.
- **The audit is paused**, and **work order F is ruled** — both above, both in DECISIONS.
- **No ruling was made in the fifth session.** Viktor chose the work (commits 5 and 6,
  then the close); 28 and the widening of 27 are Claude's, under the delegation.

## Where things stand, right now

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

## Carried lesson — the live run comes BEFORE the commit

At F the live run asked for in the command sequence did not happen before the commit:
at the push the log still held 29 records, the newest on the old `code_hash`. Claude
caught it by reading the log, not from a paste. **On every change that moves
`code_hash` — and always on one that touches the decision path (G is one) — the live
run and the panel read happen before `git commit`, and Claude checks the decision-log
record for the new `code_hash` before the commit step, not after the push.** Never
predict live numbers; check the record. Followed at `2c7a7d1`, `4e2b1c8`, `486f1a5` and `3bfa6b7`: the
command list stopped at the live run, Claude read the record, and only then gave the
commit steps.

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
- **Fifth session:** the sandbox's default `python3` was 3.11; build both virtualenvs
  from `/usr/bin/python3.12` explicitly. The sandbox cannot reach `api.mexc.com` (the
  proxy refuses it), so anything about MEXC's live behaviour is either read from its
  documentation or from Viktor's own runs — say which.

## Review findings, 21 September 2026

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

## Work order — Claude's, under Viktor's delegation

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

## Resolved this session

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

## Open items

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
