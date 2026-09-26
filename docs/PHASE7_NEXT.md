# Next step — read this first

*26 September 2026, seventh session. Rewritten by this session's first commit, the one
that files what the sixth session owed and the round-1 audit outputs; the version it
replaces — rewritten at `e804b64` and amended in place at `c5dc4cd` and `bc48f59` — is in
HISTORY verbatim.
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

**The seventh session (26 September)** opened on Viktor's message listing four owed items
and four things discussed only in chat since 22 September. Asked what to do first, he
chose the owed filing. Before it, at his request, Claude made a roadmap to the audit — a
Claude Docs document, "Phase 7 roadmap to the independent audit", outside the repository.
It proposes an order and changes no rule. The session switched model partway, from Claude
Sonnet 5 to Claude Opus 5.5 (the commit message has the detail).

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
- **Filed this session — `bias_score`'s weighting waits for after the audit, and the
  auditor sees it** (DECISIONS, "Ruling, 22 September 2026 — bias_score's weighting waits
  for after the audit, and the auditor sees it"). Ruled in chat on 22 September, option 3.

## Where things stand, right now

- **Tip:** the commit that writes this line (a commit cannot name its own hash) — the
  seventh session's owed filing; documentation only. Before it: `bc48f59` (the
  Engineering Notes regenerated at v1.35, `c5dc4cd`'s push filed), `c5dc4cd` (`e804b64`'s
  push filed, README's audit row), `e804b64` (the Notes at v1.34, the 22 September ruling,
  NEXT's sixth-session rewrite), `5e55eb8`, `3bfa6b7` (commit 6 of the six,
  `data/data_fetcher.py`: finding 27). F itself is `3f263c2`. **Tag:** `portfolio-v1` at
  `99e022e`. **Release gate:** open, declared 15 September 2026.
- **Working tree and hook at `bc48f59`:** the push `c5dc4cd..bc48f59` printed
  `SUMMARY: clean`, section 1 "none", section 6 "installed", and section 5 README.md one
  commit behind (expected) — Viktor's message opening this session. He verified the push
  by fetch on 22 September; this session's clone of GitHub's tip was `bc48f59`, and the
  five documents this commit changes matched his disk byte for byte before any edit.
  **Owed to the next commit:** the hook's result on the push of the commit that writes
  this line. The earlier record of the hook is in HISTORY.
- **code_hash:** `b3c2308f8f3e05981af25ee82468c071f7bf0b9d49519b6e75bd78c37b5fb365`,
  moved at `3bfa6b7` (`data/data_fetcher.py`); unmoved since, and by the commit that
  writes this line — computed on the tip's tree and on the applied tree under Python
  3.12.3. Confirmed on Windows before `3bfa6b7`'s commit by Viktor's live run of
  21 September 23:29 (details in HISTORY, the entry for this file at `bc48f59`).
- **code_hash is only comparable within one Python minor version.** It hashes `ast.dump`
  output, a CPython implementation detail (`core/code_fingerprint.py`, "WHAT IT DOES NOT
  SURVIVE"). **Every `code_hash` claim about this project is computed under Python 3.12**
  (Viktor runs 3.12.10).
- **Golden snapshot:** unmoved by the commit that writes this line. Last re-baselined at
  `2c7a7d1` (finding 22; no decision field).
- **Test suite** — unmoved by the commit that writes this line (documentation only):
  **597 passed / 0 failed, no warnings line** with `pandas_ta`; **460 passed / 126
  skipped** without it; `run_tests.py` **526 passed / 0 failed / 32 errors**, all 32
  fixture-collection `TypeError`s. Linux sandbox, autocrlf clone, Python 3.12.3, pinned
  requirements, applied tree. Last moved at `3bfa6b7`.
- **Engineering Notes:** through Entry #166 (v1.35), which covers `c5dc4cd`. **Two
  commits behind** — `bc48f59`, the floor (a commit that regenerates the Notes cannot
  cover itself, Entry #144), and the commit that writes this line. Every later commit
  adds one until the next regeneration, which also records the round-1 recovery.
- **Portfolio Document and AI-Attribution Statement:** both current with their scripts,
  which last changed at `6e1baba`.
- **README.md:** changed by the commit that writes this line — its paragraph on the
  round-1 outputs, under "The audit, and what it found", now says where they are, and that
  it used to say they could not be recovered. So the hook's section 5 will report
  README.md 0 commits behind. Its two test-count lines current at `3bfa6b7`; its
  Independent-audit row current at `c5dc4cd`.
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

## Found after 22 September — for after the next audit

The 22 September ruling closed the list above. A finding made from now on is recorded
here, with its evidence, and waits until after the independent audit; it does not move
the audit. Whether the auditor is shown this section is part of the package question,
Viktor's when the audit is planned.

- **The engine almost never trades, and one gate decides nearly all of it.** Viktor,
  22 September, in chat; recorded here on 26 September. **Where it belongs is open and
  Viktor's: work order G (finding 17), findings 4 and 6 already on the list, or this
  list.** Evidence, from Claude's count on 22 September of a copy of
  `logs/phase7_decision_log_aerousdt.jsonl` (not recounted this session): 35 runs, 6 to
  22 September, all AEROUSDT 4h, about 10 of them test runs — 31 NO-TRADE, 3 WAIT,
  1 SHORT (16 September), 0 LONG. 27 of the 31 refusals are the 15% stop-distance rule,
  and since 19 September every refusal is. The stop has sat at about 0.547–0.550 since
  19 September while price rose. On the 22 September panel the stop was 20.7% from the
  current price and 13.0% from the entry zone's bottom, because stop and targets are
  measured from the current price. Every stop-distance refusal shows RISK REGIME: UNKNOWN;
  that the regime is not computed once the stop check fails is an inference, and the code
  has not been read. **Claude's reading, from this file's text of findings 4, 6 and 17
  and not from the code:** the measuring point is finding 4, and a stop held at the
  volume point of control is finding 6, whose text says how often it vetoes a setup "was
  not measured" — the count above is that measurement. Finding 17 is about macro in the
  CONSERVATIVE branches and does not mention the stop. First step before Viktor rules:
  read finding 17's code and the stop path, and say what the code shows.

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

- **The sixth session's owed filing** (Viktor's message opening this session), in the
  session's first commit:
  - the hook's result on the push of `bc48f59` — filed above;
  - the ruling of 22 September on `bias_score`'s weighting — filed in DECISIONS;
  - a correction: "To do list Claude Phase 7 Engine.pdf" was not deleted, as `982e70f`
    recorded — HISTORY, 26 September. It is in `Docs\99_Superseded` of
    `D:\Phase_7_Engine_Random_Files`, renamed, identified by content;
  - **the round-1 audit outputs, recovered** — filed in `docs/audit_reports/`, a new
    HISTORY entry, and forward corrections in README.md and `docs/build/README.md`. The
    20 September record is not edited.
- **The once-per-session rewrite of this file.** The previous version, as at `bc48f59`,
  is in HISTORY verbatim, headings demoted one level, proven by un-demotion with a
  negative control (the commit message has the result).

## Open items

Items marked **Viktor's call** are his to decide; he writes his position first and
Claude critiques it.

- **Owed to the next commit:** file the hook's result on this commit's push.
- **Viktor's call — findings 4, 5, 6, 7, 16 and 18 above.** On the closed list before
  the audit. Not started.
- **Claude's — work order G (finding 17).** On the closed list before the audit.
- **Viktor's call — where the stop-distance finding belongs** (above, "Found after
  22 September"). Claude reads the code first.
- **Viktor's positions of 22 September, stated in chat, not yet ruled in DECISIONS:**
  1. **Spent models for build and review.** Models already spent (Gemini, ChatGPT, Grok
     and the others on the ledger) may do build and review work, with full transparency:
     the same patch gates, the commit message names the model, and a ledger entry is made
     at the time of use. Any model that writes engine code is disqualified from auditing
     that code. Claude agreed.
  2. **A pre-send token check, built ahead of the audit.** It measures the audit package
     with the chosen model's own tokenizer and refuses the send if package plus output
     reserve does not fit. Claude agreed, on condition that it is ruled explicitly as
     audit preparation, not an engine item, so the closed list stays closed.
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
  AI-Attribution Statement, not from provider exports. **Owed to it:** Grok read the
  production modules for its assisting-model review of 23 September
  (`ASSISTING_MODEL_REVIEW_2026-09-23.md`, outside the repository); the ledger shows Grok
  as not having seen engine source. That review is received, not triaged. By its own text
  it is not an audit, grades nothing, and anything accepted from it goes on the list for
  after the audit.
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
