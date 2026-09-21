# Next step — read this first

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

## PACE FIRST — read this before the rest of this file

Viktor judged, on his own, that 226 commits across 22 days had become hasty, and
ruled to slow down considerably (15 September 2026). **Do not open a session by
proposing work from "Open items" below, and do not treat it as a queue to clear.**
Ask what he wants to do first.

## Where the project is

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

## Ruled this session

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

## Where things stand, right now

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

## Resolved this session

- **Four notes that existed only in the 20 September chat, filed here:** the hook's clean
  result on `635a94e` (above); the Engineering Notes line counting itself (above); the
  obligation to rewrite this file if this session did substantive work, which `ebb4e5c`
  did; and the autocrlf observation, which stays open (below).
- **The once-per-session rewrite of this file.** The previous version — written at
  `b869a30`, amended at `635a94e` — is in HISTORY verbatim, headings demoted one level,
  proven by un-demotion.

## Review findings, 21 September 2026

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

## Work order — Claude's, under Viktor's delegation

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

## Open items

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
