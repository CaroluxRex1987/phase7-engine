# Next step — read this first

*21 September 2026, third session. This file is the project's current-state entry point:
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
have landed (below); G is next in Claude's order.

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

- **Tip:** the documentation commit that writes this file (a commit cannot name its own
  hash); the one before it is `aafded0`, which filed F's Windows confirmation; F itself
  is `3f263c2`. **Tag:** `portfolio-v1` at `99e022e`. **Release gate:** open, declared
  15 September 2026.
- **Working tree:** last seen clean by `git status --short` at `635a94e` (Viktor's
  paste, 21 September); not pasted since. The hook's clean SUMMARY covers its own
  checks, not every line `git status` would print.
- **code_hash:** `44f7296bb9c1a927712797df132eff4114f2782cdebb290d93d0dc86f8e44f78`,
  moved at F (`3f263c2`) from `3e76c1c5…`, Python 3.12. **Confirmed on Windows** by the
  decision-log record of Viktor's live run of 21 September 19:24 (AEROUSDT 4h, the 30th
  record), read by Claude from his disk. Unmoved by `aafded0` and by the commit that
  writes this file — both touch no `.py` file, and `core/code_fingerprint.py` walks
  `.py` files only.
- **code_hash is only comparable within one Python minor version.** It hashes `ast.dump`
  output, a CPython implementation detail (`core/code_fingerprint.py`, "WHAT IT DOES NOT
  SURVIVE"). **Every `code_hash` claim about this project is computed under Python 3.12**
  (Viktor runs 3.12.10).
- **Golden snapshot:** last re-baselined at F — three fields added
  (`entry.long_signal_blockers`, `entry.short_signal_blockers`,
  `trend.divergence_direction`), nothing changed; the action, every reason and
  `run_hash` did not move.
- **Test suite at `3f263c2`, unmoved since:** **549 passed / 0 failed, no warnings
  line** with `pandas_ta`; **414 passed / 124 skipped** without it; `run_tests.py`
  **478 passed / 0 failed / 32 errors**, all 32 fixture-collection `TypeError`s. Linux
  sandbox, `core.autocrlf=true` clone, Python 3.12.3, pinned requirements. **On
  Windows**, 549 and 478 / 0 / 32 are confirmed by Viktor proceeding past the steps whose
  stop conditions they were.
- **Engineering Notes:** through Entry #141 (v1.33), which covers `4629002`. **Eighteen
  commits behind** — `3a899b5`, `92775ea`, `53394ff`, `982e70f`, `65a0aef`, `a9d4b1f`,
  `6e1baba`, `b869a30`, `119c8a3`, `635a94e`, `ebb4e5c`, `a530006`, `e3f3d51`,
  `afd8460`, `49de810`, `3f263c2`, `aafded0` and the commit that writes this line — by
  Viktor's choice, under the standing batching rule. **This count includes the commit
  that writes it, so every later commit adds one until the Notes are regenerated.** If
  the independent audit's package includes the Notes, regenerate them before building
  it.
- **Portfolio Document and AI-Attribution Statement:** both current with their scripts.
- **README.md:** brought current in the commit that writes this file — test counts,
  the paused audit, and what backtesting now waits on.
- **Pre-push hook:** `SUMMARY: clean` on the push of `aafded0` — Viktor pasted it at the
  opening of the third session of 21 September, so confirmed, not reported. Clean, and
  pasted, on `635a94e`, `ebb4e5c`, `a530006`, `e3f3d51`, `afd8460` and `49de810`. On
  `3f263c2` the output was not pasted; the push landed and the hook stops a push on any
  finding, so clean is inferred, not seen. The earlier record is in HISTORY.

## Carried lesson — the live run comes BEFORE the commit

At F the live run asked for in the command sequence did not happen before the commit:
at the push the log still held 29 records, the newest on the old `code_hash`. Claude
caught it by reading the log, not from a paste. Viktor's 19:24 run came after the
commit. **On the next change that touches the decision path (G is one), the live run
and the panel read happen before `git commit`, and Claude checks the decision-log
record for the new `code_hash` before the commit step, not after the push.** Never
predict live numbers; check the record.

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
- **G — macro in the CONSERVATIVE branches (17). Next in Claude's order.** Changes which
  trades are taken, so it is scoped in full before any diff: `decision_model`'s ladder,
  every caller, the golden fields it could move, and the live decision log checked
  first for which recorded actions it would change, as for F. The live run happens
  before the commit (above).
- **Then:** the deferred read (`data_fetcher`, `validation`, `decision_log`, `lineage` —
  `data_fetcher`'s live fetch path was read for finding 16, nothing else of it).
- **Then:** the running change list for the audit (Open items).

## Resolved this session

- **The once-per-session rewrite of this file.** The previous version — rewritten at
  `ebb4e5c` and amended in place through `aafded0` — is in HISTORY verbatim, headings
  demoted one level, proven by un-demotion.
- **The hook's clean result on `aafded0`**, which existed only in chat, is filed above.
- **README.md checked against this file** — the hook reported it three commits behind.
  Stale: both test-count lines (528 / 393 / 457, the counts at E), and nothing said the
  audit is paused or that backtesting now also waits on an independent re-audit of the
  changes since 14 September. Brought current in the commit that writes this line.

## Open items

Items marked **Viktor's call** are his to decide; he writes his position first and
Claude critiques it.

- **Viktor's call — findings 4, 5, 6, 7, 16 and 18 above**, before backtesting. Not
  started.
- **The independent audit — paused, ruled 21 September.** When it is planned, still
  Viktor's: which model, the package (the standing default for a fresh Tier-1 audit is
  the full package), whether the auditor sees the scrapped findings, and the
  instruction for the selected model. No backtesting before it.
- **Claude's — the running change list for the audit.** Every change since the last
  audit, one line per commit: what changed, which finding it closes, which tests
  guard it. Becomes the auditor's scope. Not started.
- **Found, not resolved — which clone produced the Linux counts at `119c8a3`.** An
  autocrlf clone passes `tests/test_pinned_source.py` and gave 504 / 0 (confirmed again
  on 21 September). The earlier text described the `119c8a3` Linux counts as coming from
  a default LF clone, which by the standing note should fail that test. The clone type
  was not recorded.
- **Found, not checked:** HISTORY's 5 September "The record corrected from the bill"
  says the eleven round-2 observations came from a Qwen run; the
  `round2_kimi_k3_20260902/README.md`, filed later, says they are Kimi's. Which is the
  later word, and whether the earlier one is marked superseded, was not examined.
- **The pre-push hook is installed per clone, not per repository.** After any re-clone
  (including after a machine wipe), run `git config core.hooksPath githooks`;
  `session_handover_check.py` section 6 flags a clone without it.
- **Unrelated, not urgent:** confirm which YH programme permits AI-assisted
  examensarbete work.
