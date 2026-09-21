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

**Nothing here decides the engine's trading rules.** Four findings are questions about
what the engine should do rather than defects in what it does; they are listed under
"Viktor's call, before backtesting" and none of the planned commits touches them.

**Planning or pausing the independent audit is still Viktor's call, unruled** — which
model, which package, whether the auditor sees the findings scrapped on 20 September, and
the instruction for the selected model (DECISIONS, "Ruling, 20 September 2026 — the
open-items list scrapped; an independent audit next"). On 20 September he said he was
considering pausing it, "since we fixed all the issues now"; that is a position, not a
ruling. Claude's objection, for him to answer when he rules: the audit exists to find
what nobody has found yet, not to close known findings. This session's review is a
small instance of the point — it found thirteen defects and open questions in a
codebase whose open-items list was empty.

## Ruled this session

- **The order of work is delegated to Claude** (Viktor, 21 September: "Organize a to do
  list and we start working, It is up to you."). The delegation covers ordering and the
  items marked Claude's below; it does not cover the four marked Viktor's.
- **The rest of the read waits** (Viktor, 21 September: "we check it after"):
  `data/data_fetcher.py`, `data/validation.py`, `core/decision_log.py` and
  `core/lineage.py` are read after the work list, not before it.

## Where things stand, right now

- **Tip:** the commit that landed work order B (a commit cannot name its own hash); the
  one before it is `ebb4e5c`, which rewrote this file. **Tag:** `portfolio-v1` at
  `99e022e`.
  **Release gate:** open, declared 15 September 2026.
- **Working tree at `635a94e`:** clean — `git status --short` printed nothing
  (Viktor's paste, 21 September, before this session's work began).
- **code_hash:** `ec88cf242fdd6014abe66693ab7c319cbac97cf3d9131e9fe7c27562c1ac06f8` —
  moved at work order B (`core/panel_render.py`, `models/decision_model.py`) from
  `35718f6b…`, where it stood since `119c8a3`; `ebb4e5c` touched `docs/` only and did not
  move it. Both values computed under Python 3.12.3 on the pristine and the applied tree,
  not assumed.
- **code_hash is only comparable within one Python minor version.** It hashes `ast.dump`
  output, a CPython implementation detail (`core/code_fingerprint.py`, "WHAT IT DOES NOT
  SURVIVE"). On 20 September a sandbox whose default `python3` was 3.11.15 reported a
  different value on an unmodified tree. **Every `code_hash` claim about this project is
  computed under Python 3.12** (Viktor runs 3.12.10).
- **Golden snapshot:** last re-baselined at `a9d4b1f`, two fields. Unmoved by work order
  B: the only decision-path change is the wording of one reason on a run whose trend
  health was not measured, and the pinned run measures it. The pinned run's whole panel
  is byte-identical before and after B.
- **Test suite, moved at work order B** by one new fixture-free file of 11 tests:
  **515 passed / 0 failed** with `pandas_ta`; **383 passed / 121 skipped** without it;
  `run_tests.py` **444 passed / 0 failed / 32 errors**, all 32 fixture-collection
  `TypeError`s, unmoved. Verified in a Linux sandbox on a `core.autocrlf=true` clone
  under Python 3.12.3, pinned requirements — evidence about Linux until Viktor's run.
- **Engineering Notes:** through Entry #141 (v1.33), which covers `4629002`. **Twelve
  commits behind** — `3a899b5`, `92775ea`, `53394ff`, `982e70f`, `65a0aef`, `a9d4b1f`,
  `6e1baba`, `b869a30`, `119c8a3`, `635a94e`, `ebb4e5c` and work order B's commit — by
  Viktor's choice, under
  the standing batching rule. **This count includes the commit that writes it, so every
  later commit adds one until the Notes are regenerated;** it is the line most likely to
  go stale in this file. If the independent audit's package includes the Notes,
  regenerate them before building it.
- **Portfolio Document and AI-Attribution Statement:** both current with their scripts.
- **Pre-push hook:** reported `SUMMARY: clean` on the pushes of `635a94e` and `ebb4e5c`
  — Viktor pasted both outputs, so those are confirmed, not reported. Earlier record,
  carried unchanged:
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
   the risk check fails: NO-TRADE (RISK TOO HIGH), RISK REGIME UNKNOWN — the branch the
   21 September AEROUSDT run took. Whether the HVN set that run's stop was not checked,
   and how often this vetoes a setup was not measured.
7. **Indicator values beyond 5σ are silently replaced by the previous bar's.**
   `indicators/indicators.py:105–110`, inside `clean_series`, which EMA, RSI, ADX,
   SuperTrend and ATR all pass through.
   Nothing records the replacement — unlike volume spikes (`:746`), which are kept and
   flagged. At the decision bar the replaced value becomes a reported indicator
   *failure*. The mean and standard deviation span the whole frame, so a backtest that
   computes indicators once over its history would leak future bars into past
   decisions. Reachability on live data: not measured.

**Code that cannot run, or runs and decides nothing** — Claude's

8. **A direction check that can never match** — `models/risk_model.py:240` compares
   `detailed_bias` to "LONG"/"SHORT"; its only caller passes "BULLISH CONFIRMED" /
   "BEARISH CONFIRMED" / "NEUTRAL" (`engine_core.py:707`). The A1/A2 shape, surviving in
   a second file. Not a wrong answer today: raw bias comes from the same score, so an
   authorised action and its plan cannot point opposite ways. → C.
9. **An unreachable fallback that would be wrong if reached** — `risk_model.py:278–282`,
   `:296–297`. `bias_score` is clipped to ±100 (`models/bias_engine.py:448`), so the ATR
   stop is always on the correct side. If the branch ever ran it would leave the stop on
   the wrong side while the targets used a different distance. → C.
10. **Nothing at runtime checks that the stop sits on the correct side.** The panel's
    R:R uses `abs()` (`panel_render.py:171`, `:177–179`); `_refuse_incoherent_plan`
    reads target order only; `core/decision_contract.py` runs in tests and checks shape,
    not values. Unreachable today per 8 and 9. → D.
11. **`long_signal` / `short_signal` are recorded and decide nothing.** Computed every run
    (`generate_entry_signals`), carried into the decision object, the log and the
    simulated order; no decision reads them. They are False whenever
    `reversal_strength > 0` — e.g. within 3% of the HVN — so the record can show
    `long_signal: False` beside an AGGRESSIVE LONG. → F.

**Fabricated defaults still standing** — Claude's

12. **`live_trading.py`, `_build_simulated_order`:** zone 0.0, stop 0.0, targets
    (0, 0, 0), current price 0.0, `risk_reason` "OK". The class Round 6 F3 fixed in the
    router and the panel. Reachable only through `test_live.py`, a manual script. → E.
13. **`structure/structure.py:544–546`:** `.get("hvn", 0.0)`, `.get("lvn", 0.0)`,
    `.get("regime", "NEUTRAL STRUCTURE")`. Latent — the keys are always present. → E.

**Checked and found sound**

14. Every engine module is reachable from `main.py` except `core/decision_contract.py`
    (test-side by design) and `utils/decision_log_backup.py` (a standalone tool with its
    own `__main__`). No orphaned module.
15. `_refuse_incoherent_plan` cannot fire today (see 8) — correctly so: it is a tripwire
    against a future change, which is what its docstring says it is. Not a finding.

## Work order — Claude's, under Viktor's delegation

Each code commit is its own commit and updates this file for its own landing.

- **A — landed at `ebb4e5c`.** The findings above into the repo; the HISTORY move.
- **B — landed.** Panel display (1, 2, 3). Also found while scoping it: `asset_name`'s
  suffix list tried "USD" before "BUSD", so a BUSD pair lost only "USD"; fixed in the
  same function. Viktor's Windows live run before committing: result not yet recorded.
- **C — `risk_model` dead paths (8, 9).** Output-invariant: the code says what it already
  does, and the unreachable fallback fails closed instead of returning a wrong-side stop.
- **D — plan-side guard (10).** One check every plan passes before it can authorise a
  trade; fails closed. Unreachable today, so output-invariant on every current run.
- **E — remaining fabricated defaults (12, 13).**
- **F — `long_signal` / `short_signal` (11).** Touches the decision contract and possibly
  the golden snapshot; scoped fully before any diff.
- **Then:** the deferred read (`data_fetcher`, `validation`, `decision_log`, `lineage`),
  and Viktor's rulings on 4–7 before any backtest is designed.

## Open items

Items marked **Viktor's call** are his to decide; he writes his position first and
Claude critiques it.

- **Viktor's call — findings 4, 5, 6, 7 above**, before backtesting. Not started.
- **Viktor's call — planning the independent audit, or pausing it:** which model, the
  package (the standing default for a fresh Tier-1 audit is the full package), whether
  the auditor sees the scrapped findings, and the instruction for the selected model —
  or whether the round is paused at all, which he raised on 20 September and has not
  ruled. Not started.
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
