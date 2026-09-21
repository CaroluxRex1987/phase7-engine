# Next step — read this first

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

## PACE FIRST — read this before the rest of this file

Viktor judged, on his own, that 226 commits across 22 days had become hasty, and
ruled to slow down considerably (15 September 2026). **Do not open a session by
proposing work from "Open items" below, and do not treat it as a queue to clear.**
Ask what he wants to do first.

## Where the project is

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

## Ruled — in force

- **The order of work is delegated to Claude** (Viktor, 21 September: "Organize a to do
  list and we start working, It is up to you."). It covers ordering and the items marked
  Claude's below; it does not cover the items marked Viktor's.
- **The audit is paused**, and **work order F is ruled** — both above, both in DECISIONS.
- **The rest of the read waits** (Viktor, 21 September: "we check it after"):
  `data/data_fetcher.py`, `data/validation.py`, `core/decision_log.py` and
  `core/lineage.py` are read after the work list, not before it.

## Where things stand, right now

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

## Carried lesson — the live run comes BEFORE the commit

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

## Sandbox practice — learned 21 September, second session

- Set `git config core.autocrlf true` in the clone and re-check out; a `-c` flag on
  `git clone` does not persist.
- Run negative controls with `PYTHONDONTWRITEBYTECODE=1`.
- The golden updater writes LF with no final-newline handling of its own; restore CRLF
  and the original ending by hand before diffing.
- A file re-written to the outputs folder under the same name once reached Viktor's
  disk as the OLD version. Use a new file name for each version, and always read
  deliveries back.
- `git status --short` sorts by path; predict the order that way.

## Review findings, 21 September 2026

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

## Work order — Claude's, under Viktor's delegation

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

## Resolved this session

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

## Open items

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
