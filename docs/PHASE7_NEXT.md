# Next step — read this first

*4 October 2026. Rewritten by `d27743f`, which records round 8's first run, scores it
0 of 4 and closes it to Part 7 — item 5 of round 8's preparation list; the version it
replaced — as it stood at `217ede6` — is in HISTORY verbatim. Brought current, in the
same session, by the commit that records round 8's second run (2 of 4, a pass).
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

**One exception, since 4 October: the independent audit.** Viktor delegated it to
Claude outright and asked for no more questions or decisions on it (DECISIONS,
"Delegation, 4 October 2026 — the next independent audit is Claude's to run"). Work on
the audit — round 8's preparation list in Open items — goes ahead without asking what
he wants first; he runs the commands. Everything else still follows the rule above.

## Where the project is

**The closed list is done** — work order G and findings 4, 5, 6, 7, 16 and 18, each
ruled with any code it called for landed; the last, G, at `7d0024e`. **Round 7 of the
independent audit is over, with no report that counts.** Laguna S 2.1 (Poolside) was
sent the full package on 30 September, built from the tag `round7-sent-2026-09-30`
(`e186423`), twice: run 1 without reasoning requested and run 2 with it. Both runs
found 0 of the 4 test bugs, and Viktor checked both scores (DECISIONS, "Round 7 ended,
30 September 2026 — run 2 found 0 of 4"). How the round was prepared and sent — the
preparation list, items 1 to 13 — is in HISTORY, in this file's versions from
`d5ced0c` to `1523e0c`. **On 4 October Viktor delegated the next audit to Claude
outright** (DECISIONS, "Delegation, 4 October 2026 — the next independent audit is
Claude's to run"); accepting or rejecting its result stays his, and he runs the
commands. **Claude's decisions under it**, each in DECISIONS with what it weakens:
round 8 goes to Xiaomi's MiMo-V2.6-Pro, the full package in one session, if it passes
four checks before the send; the package is the tag's, with only rev 9 of the
instruction and a corrected Part 7 document; the freeze holds, with a second exception
for the token check's tests; and if MiMo fails, scoped packages go to Upstage, NVIDIA,
Cohere and AI21. **All four checks passed** — the last, reasoning, by the probe at the
send. How the tooling builds and sends round 8 is Claude's, in DECISIONS ("Decision,
4 October 2026 — round 8's tooling"); what rev 9 and the Part 7 correction say,
likewise ("Decision, 4 October 2026 — rev 9 and the Part 7 correction"). **Round 8's
first run was sent on 4 October, from `217ede6` (tagged `round8-sent-2026-10-04`), and
found 0 of the 4 test bugs** — Claude's score, which Viktor checks; it reasoned at
length (40,434 reasoning tokens) and named itself Claude, though the provider's record
is Xiaomi's (DECISIONS, "Decision, 4 October 2026 — round 8's first run: 0 of 4, no
Part 7 to it, run 2 next"). Part 7 does not go to it. **Run 2 found 2 of the 4 — a
pass** (DECISIONS, "Decision, 4 October 2026 — round 8's second run: 2 of 4, a pass;
Part 7 to it"), so its ratings count. **Next:** Part 7 to run 2 (Open items).
Anything found meanwhile goes on the list for after the audit (below), not onto the
closed list.

**Since 28–29 September the project has a finish line** — DECISIONS, "Ruling,
28 September 2026 — what "finished" means, and how the engine is judged". In short: a
trade's goal is T1 before the stop, with T1 netting at least 3% after fees; spot only,
no leverage, and on spot SHORT means sell to USDT; "finished" is at least 100 closed
trades from one engine version, at least 60% reaching T1 first, profit after fees, and
a better result than random longs with the same stop and T1; trends only for now;
paper trading in ten equal slices. Goal B's verdict is kept exactly as pre-registered,
with two lines added to its methodology (spot only; how a trade ends) and the finish
criteria reported beside it. The portfolio is now secondary; goal A stands as
achieved. It changes no code. Two new trading rules go on the list for after the audit
(below): the 3% floor and a range-trading mode.

**Nothing Claude does under the delegation decides the engine's trading rules.**
Findings 4–7, 16 and 18 were questions about what the engine should do, and were
Viktor's. G changed which trades are taken and was Claude's under the delegation: it was
scoped in full, the live log was replayed first, and the live run came before the
commit. What it weakens is in DECISIONS, "Work order G, 27 September 2026 — macro no
longer decides the CONSERVATIVE tier (finding 17)", for Viktor to reverse if he
disagrees.

**The independent audit was paused until the closed list was done** — DECISIONS,
"Ruling, 21 September 2026 — the independent audit paused" and "Ruling, 22 September
2026 — when the audit resumes". **With G landed at `7d0024e`, that condition is met.** **The
Constitution's step 8 binds:** "Re-audit the items that changed —
independent auditor again, not a self-check by whoever made the fix. 9) Only then …
build the backtesting architecture." No engine change since the last independent round
(round 6 fix-verification, 14 September) has been independently re-audited, so **no
backtesting before an independent re-audit.** What opens it is now ruled (DECISIONS,
"Ruling, 29 September 2026 — what opens backtesting"): building needs Items 2, 3, 6 and
18 rated Compliant or fixed and confirmed, no Critical or Major finding open, every fix
confirmed by the same auditor, and Viktor's declaration; running needs Goal B's harness
built and tested and a known-good checkpoint. Claude's second point of 21 September —
the rule exists only as text — is answered inside it: the entry-point guard is built
with the first backtest code.

**The twenty-second to thirty-first sessions (29–30 September)** prepared round 7, sent
it and closed it. Their accounts are in HISTORY, in this file's earlier versions; the
last, as it stood at `1523e0c`, was moved there by `ff12e17`.

**After the thirty-first session, no commit until this one.** What follows is filed
from Claude's memory notes of those sessions, not from their chats, which this session
could not read. Those notes do not number the sessions, so they are named by date.
Nothing in them was ruled except the delegation.

- **30 September to 1 October — the next auditor.** Viktor's positions, none ruled: he
  first chose Amazon's Nova 2 Pro, then found he could not get it; he would prefer an
  auditor reachable through OpenRouter; the freeze stays; he raised Upstage and, if
  forced, reusing an auditor already used — "if the constitution blocks us from doing
  what is needed, it needs to be changed". Whether the same package or a new build was
  left for Claude's suggestion. He set up an AWS account to reach Amazon's models; a
  check of whether Nova 2 Pro is reachable through Amazon Bedrock was left unfinished on
  1 October.
- **1 October — ten questions to ask of the engine**, and hostile reviews of the
  Constitution (Open items). Both came from a ChatGPT conversation Viktor shared;
  OpenAI is spent already. What to do with them is not chosen.
- **4 October — the delegation, and Claude's four decisions under it** (above). Viktor
  confirmed he has never used a Xiaomi or MiMo model anywhere, and granted the session
  `G:\Phase_7_Engine_Random_Files`.

**The session of 4 October that filed the delegation** (`ff12e17`), under Claude Opus
5.5, opened on "Continue Phase 7" and went straight to the work the delegation names
(PACE FIRST, the exception). Claude read GitHub's tip (a clone) and `master` and
`origin/master` off Viktor's disk: all `1523e0c`. It made the checks of the round-8 decision as far as
they can be made from here: MiMo-V2.6-Pro's four endpoints on OpenRouter, its model
cards and its Hugging Face file listings — all read through a web tool that summarises
the page — and Viktor's OpenRouter activity export, read directly: no Xiaomi or MiMo
row. The sandbox's proxy refuses Hugging Face by policy, so the count with MiMo's own
tokenizer waited for Viktor to download the files. Its commit, `ff12e17`, was docs
only: the delegation, the four decisions with the checks as they stood, and the record
since the thirty-first session. Between it and this session Viktor downloaded MiMo's
tokenizer files into `G:\Phase_7_Engine_Random_Files\Docs\04_Data\MiMo-V2.6-Pro-MOPD_tokenizer_adea8e2\`.

**The session of 4 October that landed the tooling** (`4a4c6ce`, the third that day),
under Claude Opus 5.5, opened on "Continue Phase 7" and went to item 3 of round 8's list
(PACE FIRST, the exception).
Claude read GitHub's tip (a clone) and `master` off Viktor's disk: both `ff12e17`. It
staged MiMo's tokenizer files and checked them against Hugging Face's listings, checked
the renderer against the template, staged round 7's built package off Viktor's disk —
every first-message file hashes to what round 7's runs recorded — and made check 4 on a
trial build: it fits (DECISIONS, "Decision, 4 October 2026 — round 8's tooling"). The
commit (`4a4c6ce`) was tooling and tests only, no engine code: MiMo in
`docs/build/package_token_check.py`, `docs/build/send_audit_round.py` repointed to round
8 with the provider order, the new `docs/build/build_round8_package.py`,
`docs/build/build_audit_package.py` refusing to rebuild round 7, and the two test files
the freeze allows.

**The session of 4 October that wrote rev 9** (`217ede6`, the fourth that day), under
Claude Opus 5.5, opened on "Continue Phase 7" and went to item 4 of round 8's list
(PACE FIRST, the exception).
Claude read GitHub's tip (a clone) and `master` and `origin/master` off Viktor's disk:
all `4a4c6ce`. It staged round 7's built package off his disk — every first-message file
hashes to what both of round 7's runs recorded — and wrote rev 9 and the Part 7
correction. **Re-running rev 8's counted disclosure on the package as built found it
short by six rules** (twenty-one, not fifteen): Items 4 and 12, three Tier 2 principles
and one Tier 3 item, cited in the code by table position ("T2-1", "T2-3", "T3-5",
"Tier 2, item 6") or under a dispute with no verdict word, all of them in rev 8's
package. Its other counts held, and Section 4a's list of changed files held exactly.
MiMo's knowledge cutoff: one statement found, a sample system prompt in the API example
code on Xiaomi's model page ("December 2024"). Its commit was docs only: rev 9, the
Part 7 document corrected, a DECISIONS entry, this file and HISTORY.

**This session (4 October, the fifth that day)**, under Claude Opus 5.5, opened on
"Continue Phase 7" and went to item 5 of round 8's list, the send (PACE FIRST, the
exception). Claude read GitHub's tip (a clone) and `master` off Viktor's disk: both
`217ede6`. Viktor built round 8's package, which matched the sandbox's build file for
file; ran the two freeze checks and the dry run, which printed what was predicted; and
fetched OpenRouter's endpoint list for MiMo as raw JSON with curl, since the sandbox's
proxy refuses openrouter.ai by policy. He tagged `217ede6` and sent run 1: the probe
showed reasoning, Xiaomi's endpoint answered in ten minutes, and Claude scored the
reply 0 of 4. `d27743f` recorded the run and closed it in the send script, so Part 7
cannot go to it (DECISIONS, "Decision, 4 October 2026 — round 8's first run: 0 of 4, no
Part 7 to it, run 2 next"); Viktor pushed it with the tag, and GitHub's tip matched the
tree verified in the sandbox. He then sent run 2: Xiaomi's endpoint again, nineteen
minutes, 68,464 reasoning tokens, and Claude scored it 2 of 4 — S2 and S4 found. The
commit that writes this line records it; it is docs and the run's files only.

## Ruled — in force

- **New, 4 October — Claude's, under the delegation: round 8's second run** (DECISIONS,
  "Decision, 4 October 2026 — round 8's second run: 2 of 4, a pass; Part 7 to it").
  Scored 2 of 4 (S2, S4), a pass, so its ratings count; Part 7 goes to it. **Filed at
  the commit that writes this line**, with the run's four files.
- **New, 4 October — Claude's, under the delegation: round 8's first run** (DECISIONS,
  "Decision, 4 October 2026 — round 8's first run: 0 of 4, no Part 7 to it, run 2
  next"). Scored 0 of 4; no Part 7 to it, closed in the send script; run 2 unchanged.
  Its self-naming as Claude is recorded for Viktor to weigh. **Landed at `d27743f`**,
  with the run's four files.
- **New, 4 October — Claude's, under the delegation: rev 9 and the Part 7 correction**
  (DECISIONS, "Decision, 4 October 2026 — rev 9 and the Part 7 correction"). Rev 9 is
  rev 8 readdressed to round 8, with round 7's outcome stated without its ratings and
  Section 2's counts corrected to twenty-one rules; the Part 7 document is corrected
  where it named round 7 as its own and where the ruling of 30 September made its
  threshold sentence untrue. MiMo's Qwen2-class tokenizer and its team lead's time at
  DeepSeek are left out of rev 9, so the auditor names itself. **Landed at
  `217ede6`.**
- **New, 4 October — Claude's, under the delegation: round 8's tooling** (DECISIONS,
  "Decision, 4 October 2026 — round 8's tooling: round 7's files reused by hash, the
  provider order run by hand, and check 4"). Round 7's built files are reused, each
  checked against the hash both runs recorded, rather than rebuilt from the tag; the
  provider order is run by hand with `--provider`, and Part 7 goes to whichever
  provider answered; check 4 passed on a trial build. **Its code landed at
  `4a4c6ce`.**
- **New, 4 October — the next independent audit is delegated to Claude** (DECISIONS,
  "Delegation, 4 October 2026 — the next independent audit is Claude's to run"). Viktor
  keeps accepting or rejecting the result, running the commands, and everything the
  delegation does not name: rulings on the engine, triage, Constitution amendments, the
  declaration that opens backtesting. No code.
- **New, 4 October — Claude's, under the delegation:** round 8 to Xiaomi
  MiMo-V2.6-Pro, the full package in one session, if four checks pass, pinned to
  Xiaomi with GMICloud, DeepInfra and Novita after it, two runs in all; the package
  from the tag with only rev 9 and the Part 7 document corrected; the freeze holds,
  `tests/test_package_token_check.py` joining the exception; scoped packages to
  Upstage, NVIDIA, Cohere and AI21 as the fallback (DECISIONS, the three entries
  "Decision, 4 October 2026 — …"). No code yet.
- **New, 30 September — what follows round 7's first reply** (DECISIONS, same title).
  Points 1–4 by agreeing to Claude's suggestion; point 5 is Viktor's choice of two
  options (he chose the one Claude recommended). (1) Part 7 does not go to run 1.
  (2) Run 2 asks for reasoning and changes nothing else, and the send is refused unless
  a probe shows reasoning; `tests/test_send_audit_round.py` is the one exception to the
  freeze. (3) Run 1 counts as a run. (4) Two runs in all: if run 2 also finds fewer
  than two of the four, the next step is another auditor. (5) A run is any reply on
  record, including one cut off at the ceiling; an HTTP error before any reply is not.
  Viktor checked Claude's scoring of run 1, 0 of 4. **Its code landed at `3e8191a`.**
  Run 2 found 0 of 4 the same day, Viktor checking: **round 7 has ended** (DECISIONS,
  "Round 7 ended, 30 September 2026 — run 2 found 0 of 4").
- **New, 29 September — the test bugs: four usable, and four is enough** (DECISIONS,
  same title). The classification is Claude's (Claude scores, Viktor checks), checked
  by Viktor; "four is enough" is his choice from three options Claude put to him, with
  no recommendation. Usable: the risk gate's order, `trend_health` missing from
  `lineage.risk_inputs`, the entry score under a NEUTRAL bias, and the
  weak-validation WAIT. None or one found means a rerun; two or more, a pass. No code.
- **New, 29 September — six questions before the send** (DECISIONS, same title).
  Points 1, 2, 4 and 5 by agreeing to Claude's suggestion; 3 and 6 Viktor's own
  answers. (1) The package's commit is tagged and engine code and tests are frozen
  until the report is triaged. (2) The instruction carries the ruled behaviour as plain
  requirements and the files changed since `e65a0f7`, without reasons, and asks where a
  requirement itself looks wrong. (3) The second pass is Laguna again, as often as
  needed, each run a fresh session scored on its own. (4) How the test bugs are scored:
  defects only, usable only if nothing shipped gives them away, found only with the same
  place and the same fault in Parts 1–6, locked by a commit before the send. (5) The
  instruction does not say the ratings open backtesting. (6) No fallback decided in
  advance for a package that does not fit. No code.
- **New, 29 September — the independent audit: now, by Laguna S 2.1, the full package
  in one session** (DECISIONS, same title). Both points by agreeing to Claude's
  suggestion. Not split; NVIDIA is kept for a smaller, scoped round later. Claude's
  earlier first choice, Nemotron 3 Super, was withdrawn: OpenRouter serves it at 262K.
  The fit is confirmed by the pre-send token check. No code.
- **New, 29 September — what the auditor sees, and no planted bugs** (DECISIONS, same
  title). By agreeing to Claude's suggestion. Two messages: Parts 1–6 first; Part 7
  only after they are saved — the `bias_score` findings, the list for after the audit,
  any 15 September PDF point still live, and the commit messages since `e65a0f7`. The
  rest of the 20 September list is not shown. Nothing is planted: the list for after
  the audit is the test. No code yet; the send script changes before the send.
- **New, 29 September — what opens backtesting** (DECISIONS, same title). Viktor's
  position first, refined by Claude's critique. Built once Items 2, 3, 6 and 18 are
  rated Compliant (or each gap fixed and confirmed by the same auditor), no Critical or
  Major finding is open and every other finding is ruled, every fix is confirmed by the
  same auditor, and Viktor declares it in DECISIONS. Run only once Goal B's harness —
  with the entry-point guard, built with the first backtest code — is built and tested
  and the engine passes a known-good checkpoint. Under half the usable test bugs found:
  the auditor runs a second time first. The list for after the audit is not a
  condition. No code.
- **New, 29 September — Fable 5.1 works on the list for after the audit, not before
  it** (DECISIONS, "Ruling, 29 September 2026 — Fable 5.1 works on the list for after
  the audit, not before it"). Option A of three, by agreeing to Claude's suggestion.
  No code.
- **New, 28 September — what "finished" means, and how the engine is judged**
  (DECISIONS, "Ruling, 28 September 2026 — what "finished" means, and how the engine is
  judged"). Points 1–6 by Viktor's position first; 7–11, and A–E (reconciling it with
  Goal B, 29 September), by agreeing to Claude's suggestion. No code. Two items go on
  the list for after the audit.
- **The order of work is delegated to Claude** (Viktor, 21 September: "Organize a to do
  list and we start working, It is up to you."). It covers ordering and the items marked
  Claude's below; it does not cover the items marked Viktor's.
- **The audit is paused**, and **work order F is ruled** — both in DECISIONS, 21
  September.
- **When the audit resumes** (DECISIONS, 22 September): once work order G and findings
  4, 5, 6, 7, 16 and 18 are done. A finding is done when Viktor has ruled it and any code
  his ruling calls for has landed; a ruling to leave it as it is counts. The list is
  closed. **Met at `7d0024e`.**
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
  his position first. **Its code landed at `d76ddfd`.**
- **New, 27 September — work order G: macro no longer decides the CONSERVATIVE tier
  (finding 17)** (DECISIONS, "Work order G, 27 September 2026 — macro no longer decides
  the CONSERVATIVE tier (finding 17)"). Claude's call under the delegation: the macro
  condition is gone from both CONSERVATIVE branches, and `macro_bias` from
  `DecisionModel.evaluate()` and the ladder; the router still records it. Inside it,
  Viktor's ruling, by agreeing to Claude's suggestion: the CONSERVATIVE sentence names
  what fell short instead of always blaming entry quality. **Its code landed at
  `7d0024e`.**
- **`bias_score`'s weighting waits for after the audit, and the auditor sees it**
  (DECISIONS, 22 September; filed at `75682ee`) — in Part 7 (ruling of 29 September).
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
  round 8's second run and its record: docs only. Before it: `d27743f` (this session's
  first commit: round 8's first run and its record, the send script and one test),
  `217ede6` (the session of 4 October that wrote rev 9:
  docs only), `4a4c6ce` (the session of
  4 October that landed round 8's tooling: tooling and tests), `ff12e17` (the
  session of 4 October that filed the delegation: docs only), `1523e0c` (the thirty-first
  session's second commit: round 7's second run, run 2 closed in the send script, and
  the end of round 7), `3e8191a` (the thirty-first session's first commit: the send
  script and its test for round 7's second run, and the ruling of 30 September on what
  follows the first reply), `86f30f1` (the thirtieth session's second
  commit: round 7's first reply and its record), `e186423` (the thirtieth session's
  first commit: item 8 and two deviations; round 7's package was built from it),
  `8b6fd00` (the twenty-eighth session's commit: the Part 7 document, item 13),
  `01f2892` (the twenty-seventh session's commit:
  rev 8 of the instruction, item 9), `12b483e` (the twenty-sixth session's commit: items 3, 4 and 5 —
  the send in two requests), `f256937` (the twenty-fifth session's commit: items 7 and 6,
  and four test bugs are enough), `59b747a` (the twenty-fourth session's commit: the
  pre-send token check), `d5ced0c`
  (the twenty-third session's second commit: six rulings before the send), `e7a94d1`
  (the twenty-third session's first commit: the rulings of 29 September on the audit
  and on what opens backtesting), `ec4e5fd` (the twenty-first
  session's commit: the Engineering Notes regenerated at v1.36), `68c6191` (the
  twentieth session's commit: the ruling on Fable 5.1 and the corrected list of Aider
  models), `22cb39b` (the nineteenth session's commit: the ruling of 28 September),
  `7d0024e` (the seventeenth
  session's commit: work order G), `d76ddfd` (the sixteenth session's commit: finding
  18's code), `8b9ac1e` (the fifteenth session's commit:
  finding 5's code), `76c8cde` (the fourteenth session's commit: finding 6's code),
  `b0efe23` (the thirteenth session's commit: finding 4's code), `57f0521` (the twelfth
  session's commit: finding 7's code), `add8540` (the eleventh session's first commit:
  finding 16's code), `bf2e802` (the tenth session's first commit: finding 16 ruled),
  `7d103d7` (the ninth session's first commit: the move to E:), `eba6a2a` (the eighth
  session's third commit), `1861208` (the stop-distance ruling), `2582994` (the eighth
  session's first commit: two rulings), `75682ee` (the seventh session's owed filing and
  the round-1 audit outputs), `bc48f59` (the Engineering Notes regenerated at v1.35),
  `c5dc4cd`, `e804b64`, `5e55eb8`, `3bfa6b7` (`data/data_fetcher.py`: finding 27). F
  itself is `3f263c2`. **Tags:** `portfolio-v1` at `99e022e`; `round7-sent-2026-09-30`
  at `e186423`, the commit round 7's package was built from, made on Viktor's machine
  before the send and pushed after `86f30f1`; `round8-sent-2026-10-04` at `217ede6`, the
  commit round 8 was sent from, made on Viktor's machine before run 1 and pushed after
  `d27743f`. **Release gate:**
  open, declared 15 September 2026.
- **Frozen until round 8's report is triaged** (DECISIONS, "Decision, 4 October 2026 —
  round 8's package: the tag's, with only the instruction and the Part 7 document
  corrected; the freeze holds"): no commit touches engine code or tests. Docs-only
  commits are allowed. **Two exceptions**, both tests of tooling that is not the engine:
  `tests/test_send_audit_round.py` (ruled 30 September) and
  `tests/test_package_token_check.py` (decided 4 October). `tests/` on `master` differs
  from the tag's in both, the first since `3e8191a` (and again at `d27743f`), the second since `4a4c6ce`; `docs/audit_package/round7/MANIFEST.md` keeps its hash as sent.
  Round 8's package is round 7's files, checked by hash, so neither exception reaches
  the auditor. `docs/build/build_round8_package.py`, new, is tooling, not engine code.
- **Where the project lives, from 26 September:** `E:\phase7_engine` on Viktor's machine;
  the files kept outside the repository in `G:\Phase_7_Engine_Random_Files`. Copied with
  robocopy, verified — git's own checks on Windows for the tracked files, SHA-256 for the
  91 ignored data files and the 25 Random Files — and only then the originals renamed.
  The evidence is in HISTORY, "26 September 2026 (ninth session) — the repository moved
  to `E:\phase7_engine`". Run the engine and every command from `E:\phase7_engine` (in
  cmd, changing drive needs `cd /d`). A dated record that names the D: paths means the
  same folders before the move; dated records are not edited.
- **The pushes of `217ede6` and `d27743f`** happened. At the start of this session
  GitHub's tip (a clone) and `master` on Viktor's disk were both `217ede6`; after his
  push of `d27743f` and the tag, GitHub's tip was `d27743f`, every file in it the same
  as the tree verified in the sandbox, and the tag at `217ede6`. Viktor reported no
  deviation from either command sequence, so `d27743f`'s Windows test counts (728, 657 /
  0 / 32) are his confirmation by proceeding, and **nothing is owed** for either (ruling
  on proposal (b)). The same holds for the push of
  the commit that writes this line unless it deviates. Earlier pushes and deviations
  are recorded in this file's previous versions, in HISTORY.
- **Before this commit**, the files it changes were taken from GitHub at `d27743f`,
  which matched what was delivered to Viktor's disk; run 2's four files were staged off
  his disk and hash to what their metadata records.
- **code_hash:** `c6a44d4d7ab1c8d36f2a07f6f2c78a1967ecfc135259cbe828b3daa275e571c9`,
  unmoved by the commit that writes this line, which changes no `.py` file, and by
  `d27743f`, whose `.py` files are all under `docs/` and `tests/`, which the
  fingerprint excludes by directory. Computed on the tree before
  and after it, under Python 3.12.3.
  It last moved at `7d0024e` (from `f4b23f94…`), in
  `models/decision_model.py` and `models/signal_router.py`, confirmed on Windows by
  Viktor's live run before that commit.
- **code_hash is only comparable within one Python minor version.** It hashes `ast.dump`
  output, a CPython implementation detail (`core/code_fingerprint.py`, "WHAT IT DOES NOT
  SURVIVE"). **Every `code_hash` claim about this project is computed under Python 3.12**
  (Viktor runs 3.12.10).
- **Golden snapshot:** unmoved by the commit that writes this line. Last re-baselined
  at `7d0024e`, 2 fields (`explanation.reasons[0]` and `explanation.summary`, the
  CONSERVATIVE sentence), with `run_hash` unmoved; before that at `76c8cde`, 11 fields.
- **Test suite** — **728 passed / 0 failed, no warnings line** with `pandas_ta`;
  **583 passed / 134 skipped** without it; `run_tests.py` **657 passed / 0 failed /
  32 errors**, all 32 fixture-collection `TypeError`s; unchanged by the commit that
  writes this line, which changes no test (re-run with run 2's files in place: the same
  counts). `d27743f` added one test to `tests/test_send_audit_round.py`, with no fixture and not needing
  `pandas_ta`; before it, 727, 582 / 134 and 656 / 0 / 32, confirmed on Windows at
  `4a4c6ce` by Viktor proceeding. Linux sandbox, autocrlf clone, Python 3.12.3, pinned
  requirements, run on the applied tree with run 1's files in place. One new test,
  `test_the_commit_messages_up_to_the_tag_are_round_7s_to_the_byte`, runs `git log` up
  to the tag `round7-sent-2026-09-30`: it needs the tag, which a full clone has.
- **Engineering Notes:** through Entry #183 (v1.36), which covers `68c6191`. **Seventeen
  commits behind** — `ec4e5fd`, the floor (a commit that regenerates the Notes cannot
  cover itself, Entry #144), `e7a94d1`, `d5ced0c`, `59b747a`, `f256937`, `12b483e`,
  `01f2892`, `8b6fd00`, `e186423`, `86f30f1`, `3e8191a`, `1523e0c`, `ff12e17`,
  `4a4c6ce`, `217ede6`, `d27743f` and the commit that writes this line. Every later commit adds one until the next regeneration. Batched, by the
  15 September rule; no time pressure. v1.36 records the round-1 recovery, the rulings of 22
  (filed 26), 26, 27, 28 and 29 September, the move to E:, the code for findings 16, 7,
  4, 6, 5 and 18, work order G and the Aider correction. Its PDF's extracted text
  differs from v1.35's only by the seventeen entries, the new Document History row and
  fourteen footer page numbers (127 pages to 143), compared word by word.
- **Portfolio Document and AI-Attribution Statement:** both current with their scripts —
  each rebuilt from `68c6191` in the sandbox (reportlab 5.0.1), its extracted text
  identical to the committed PDF. Neither changes in the commit that writes this line;
  the Attribution Statement's script last changed at `68c6191`, the Portfolio
  Document's at `6e1baba`.
- **README.md:** its test counts are current (728, 583 and 657), changed at `d27743f`,
  so the hook's section 5 will report 1 commit since it was touched — the commit that
  writes this line, which changes no count. Two of its status rows are stale and not changed here (Open items).
- **The round-1 audit outputs are in the repository**, in
  `docs/audit_reports/round1_deepseek-v4-pro_kimi-k3_2026-08-27/`, byte-identical to the
  hashes Viktor took on 23 September. The account is in HISTORY, "26 September 2026 —
  correction: the round-1 audit outputs were recovered".

## Carried lesson — the live run comes BEFORE the commit

At F the live run asked for in the command sequence did not happen before the commit:
at the push the log still held 29 records, the newest on the old `code_hash`. Claude
caught it by reading the log, not from a paste. **On every change that moves
`code_hash` — and always on one that touches the decision path (G was one) — the live
run and the panel read happen before `git commit`, and Claude checks the decision-log
record for the new `code_hash` before the commit step, not after the push.** Never
predict live numbers; check the record. Followed at `2c7a7d1`, `4e2b1c8`, `486f1a5`,
`3bfa6b7`, `add8540`, `57f0521`, `b0efe23`, `76c8cde`, `8b9ac1e`, `d76ddfd` and `7d0024e`: the command
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
- **27 September, work order G:** a replay of the decision log is evidence only once it
  reproduces the logged actions. The first replay passed the degradation block in the
  wrong shape and reproduced 40 of 43; that check caught it. And once a parameter lives
  only at the router, a test that supplies it has to go through the router, whose error
  record has no `exit`: index it (`out["exit"]["action"]`), never `.get` it, so a
  negative assertion cannot pass on a failed build.

- **29 September:** `git ls-remote <url> refs/heads/master` reads GitHub's tip without
  a clone — enough to confirm a push.
- **29 September (twenty-third session):** rulings made in a session that landed no
  commit can be filed only from what that session wrote down — here, the roadmap
  document's Phase 4 list. Claude's notes between sessions lagged that list on one
  ruling (what the auditor sees, noted as open, was ruled). File from the written
  record, and say which record.
- **29 September (twenty-fourth session):** the sandbox cannot reach `huggingface.co`
  or `openrouter.ai` either (the proxy refuses both), so the tokenizer files came off
  Viktor's disk, staged from G:, and the live models API query stays with him. The
  token check runs in a third virtualenv — Python 3.12 with `tokenizers==0.23.2`, which
  pulls in `huggingface_hub` — kept apart from the two test virtualenvs, whose counts
  assume the pinned requirements only. Laguna's chat template uses a `{% generation %}`
  tag that plain `jinja2` cannot parse; to render it in the sandbox, register a small
  extension that parses the tag as a pass-through.
- **4 October (the session of `4a4c6ce`):** the sandbox's proxy still refuses `huggingface.co`, but
  the web-fetch tool reached Hugging Face's API (`/api/models/<repo>/tree/<rev>`) and
  OpenRouter's endpoints API. It summarises what it reads, so a hash read through it is
  evidence only once recomputed from bytes staged off Viktor's disk — here every one
  matched. A file kept in LFS (`tokenizer.json`) is listed with the git id of its
  pointer, not of its bytes; its LFS id is its SHA-256. MiMo's chat template needs no
  extension: plain `jinja2` renders it.
- **4 October (the session of `4a4c6ce`):** round 7's built package — `docs/audit_package/round7/`,
  ignored by git — exists only on Viktor's disk; stage it from E: when it is needed.
  Its first-message files hash to what both of round 7's runs recorded, and its
  commit-messages file is regenerated byte for byte from an autocrlf clone on Linux.
- **4 October (this session):** a counted disclosure is only as good as the search
  behind it. Rev 8's looked for a rule's number beside a verdict word and missed six
  rules the code cites by table position ("T2-1", "T3-5", "Tier 2, item 6") or under
  a dispute with no verdict word. Search for every way the code names a rule — "Item
  N", "Items N/M", "TN-M", "Tier N, item M", and the rule's own name — then read each
  hit.

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
   **Ruled 27 September, option A; done at `b0efe23`**
   (DECISIONS, "Ruling, 27 September 2026 — the plan is measured from the decision close
   (finding 4)"). The panel now names the decision close as the plan's entry and labels
   the band EMA BAND; a backtest fills at the next candle's open. Entering at the band
   is on the list for after the audit (below). **Code landed at `b0efe23`.** Done.
5. **A NEUTRAL bias still prints a full plan.** The plan's direction comes from
   `bias_score >= 0` (`models/risk_model.py`, since C), so a score between −20 and +20
   prints a long- or short-shaped stop and targets under a NEUTRAL bias with no
   direction box; exactly 0 prints a long.
   **Ruled 27 September: panel only; done at `8b9ac1e`**
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
   **Ruled 27 September: the stop comes from ATR alone; done at `76c8cde`** (DECISIONS, "Ruling, 27 September 2026 — the stop comes from ATR
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
    done at `d76ddfd`** (DECISIONS, "Ruling, 27 September
    2026 — the bias label is a function of the score (finding 18)"). `bias_label` in
    `models/bias_engine.py`; tests in `tests/test_bias_label.py`. Done.

**Claude's, done**

17. **Macro still counts twice in the CONSERVATIVE branches.** `decision_model`'s
    CONSERVATIVE LONG requires `macro_bias == "BULLISH"`, CONSERVATIVE SHORT
    `"BEARISH"` — a hard requirement on evidence already weighted into `bias_score`,
    the double count Viktor removed from the signal at F. Left out of F so that each
    change to which trades are taken lands in its own commit. → G.
    **Done at `7d0024e`** (DECISIONS, "Work order G,
    27 September 2026 — macro no longer decides the CONSERVATIVE tier (finding 17)"):
    the condition is gone, and `macro_bias` with it from the decision model; tests in
    `tests/test_macro_counts_once.py`. The three other places macro is read are
    unchanged and wait for after the audit.

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
`models/decision_model.py:551–553` at `7d0024e`, before the
ladder); and passing the risk check is not
a trade — the ladder and the confirmation gate still decide. **What to watch for now:**
the decision log will show how often runs refused only on the HVN stop become trades
under ATR alone. The two newest records (27 September, 12:31 and 13:08 UTC, on finding
5's and finding 18's code) are LONG at HIGH VOLATILITY RISK — the first trades the log
holds since the SHORT of 16 September. The one before them (04:04 UTC) was refused as
EXTREME RISK, which is refused whatever the stop. Read from the log staged on
27 September (43 records); two runs are not a rate.

## Found after 22 September — for after the next audit

The 22 September ruling closed the list above. A finding made from now on is recorded
here, with its evidence, and waits until after the independent audit; it does not move
the audit. **Ruled 29 September:** the auditor sees this list only in Part 7, after it
has saved Parts 1–6, and the list is the test of the auditor (DECISIONS, "what the
auditor sees, and no planted bugs"). Before the send, each item is checked against the
code comments, docstrings and test names that ship, by the rule in "six questions
before the send", point 4 (Open items). **Classified 29 September** (DECISIONS,
"Ruling, 29 September 2026 — the test bugs: four usable, and four is enough"): usable —
the risk gate's order, `lineage.risk_inputs`, the entry score under a NEUTRAL bias and
the weak-validation WAIT; every other entry is a new trading rule, not a defect, or
given away by a shipped line that entry names. **The Part 7 document (30 September)
classifies every entry**, including the two added on 30 September; neither is scored.

- **The risk gate runs before the bias checks.** The risk verdict returns at
  `models/decision_model.py:551–553`, before the weak-validation and lean checks at
  `:656–668` (at `7d0024e`; written as `:500–502` and `:605–617`
  on 26 September, correct until `d76ddfd` moved them six lines, then G further), so a
  run the ladder would have answered WAIT is reported as NO-TRADE (RISK
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
- **The weak-validation WAIT decides nothing.** The ladder returns WAIT when validation
  is WEAK and trend health is under 40 (`models/decision_model.py:656–660` at
  `7d0024e`), but trend health under 40 already fails both the
  CONSERVATIVE line (50) and the upper tier (75), so the answer would be WAIT anyway;
  the branch only chooses which sentence is printed. Macro reaches it through the
  validation score, so it is one of the three places macro is still read, and it
  changes no trade. Found by Claude reading the code while scoping G, 27 September; on
  this list by the 22 September ruling, not separately ruled.
- **A floor on T1: at least 3% after fees.** Point 2 of "Ruling, 28 September 2026 —
  what "finished" means, and how the engine is judged": the engine should issue no LONG
  whose T1 nets under 3% after fees. Today T1 equals the stop distance, anywhere from
  0.2% to 8% (`models/risk_model.py`, read at `7d0024e`), so this is a filter on the
  stop distance and a new trading rule. How many trades it would remove has not been
  measured; only records since `76c8cde` carry ATR-only stops. **Ruled for after the
  audit** (Viktor, 28 September).
- **A range-trading mode.** Buying at support and selling at resistance, on levels,
  with stops at the levels — Viktor's own style, and a second strategy with its own log
  and its own verdict (point 9 of the same ruling, which describes its first test case,
  his BLESSUSDT chart). **Ruled for after the audit** (Viktor, 28 September, by
  agreeing to Claude's suggestion).
- **Confidence is read as a win rate (point 1 of the 15 September PDF).**
  `models/decision_model.py:910` (at `ec4e5fd`), in `_compute_ev`, sets
  `win_rate = confidence / 100` (clipped to 0–1), and the EV figure in R that the
  explanation prints is computed from it. The confidence score is not a measured win
  rate. Its docstring and a 20 September comment already say the figure is a
  restatement of confidence and not a backtested number; it decides nothing. Scrapped
  with the rest of the 20 September list, found still live on 29 September (read from
  the code), and **moved back onto this list by the ruling of 29 September** on what
  the auditor sees. Not usable as a test bug: its docstring names the problem (point 4
  of "six questions before the send"). Points 3 and 4 of the PDF are the next two
  entries; point 5 is not live (DECISIONS, "the test bugs", item 7).
- **The BTC adjustment has no baseline (point 3 of the 15 September PDF).**
  `DecisionModel._compute_btc_adjusted` (`models/decision_model.py`) moves a second
  confidence figure by up to ±20 points on BTC's bias and the pair's correlation with
  BTC, and by −15 under broad market stress; nothing has tested whether that predicts
  anything. It decides nothing: only the record and the panel read it. Unchanged since
  the PDF, traced from the code on 29 September and **moved onto this list by the
  ruling of 29 September** on what the auditor sees. Not usable as a test bug: the
  panel's own line says "empirically unvalidated — no backtest supports this
  adjustment" (`core/panel_render.py:676`).
- **Is ×0.90 enough against the macro trend? (point 4 of the 15 September PDF).**
  `models/entry_model.py:384–385` multiplies the entry score by
  `CONFLUENCE_PENALTY_MULT` (0.90) when macro opposes the trade. Since work order G it
  is one of three things left that act against a trade opposing macro, with the
  validation score's −20 and macro's 10% in `bias_score`, which G read, unconfirmed
  with Viktor, as the 22 September ruling's "three penalties" item. Traced on
  29 September and **moved onto this list by the same ruling**. Not a test bug: it
  asks how large a weight should be, and `models/decision_model.py:692` names it
  anyway.
- **"ROUND 6" in seven test comments means round 5's requested-run 6.** Six comments
  read `ROUND 6 MUTANT ESCAPE (GPT-6 Astra), 12 September 2026` (`run_tests.py:150`,
  `tests/test_frame_ownership.py:219` and `:300`, `tests/test_smoke.py:130`,
  `tests/test_timeframe_disagreement.py:353`, `tests/test_trend_direction_source.py:223`)
  and one docstring says "round 6 (GPT-6 Astra)"
  (`tests/test_run_tests_filter_matching.py:2`). GPT-6 Astra graded round 5; these came
  from its requested-run 6, a day before round 6 (Muse Spark 1.3) was sent. The project's
  own records used the same name ("the five round-6 mutant-escape findings"). Found by
  Claude on 30 September while counting the parties rev 8 names; not changed, so that
  the code the auditor reads is not edited for it. Not usable as a test bug: the shipped
  line is itself the defect.
- **A comparison between two vocabularies in `calculate_entry_quality`.**
  `models/entry_model.py:384` (at `01f2892`) tests `macro_bias != trade_direction`.
  `macro_bias` is BULLISH, BEARISH or NEUTRAL and `trade_direction` is LONG or SHORT, so
  the test is always true. The two branches above it catch agreement, and
  `core/engine_core.py` passes only BULLISH, BEARISH or NEUTRAL, so the result is right
  for every value any caller passes; any other macro value would be penalised as
  opposing. Found by Claude on 30 September while checking point 4 of the 15 September
  PDF for the Part 7 document; on this list by the 22 September ruling, not separately
  ruled. Not scored: it changes nothing observable.
- **Fable 5.1 works on this list after the audit** (DECISIONS, "Ruling, 29 September
  2026 — Fable 5.1 works on the list for after the audit, not before it"). Not a
  finding; recorded here so the list says who works on it after the audit.

## Work order — Claude's, under Viktor's delegation

Each code commit is its own commit and updates this file for its own landing.

- **A–F landed:** A `ebb4e5c`, B `a530006`, C `e3f3d51` (D folded in), E `afd8460`,
  F `3f263c2`. Each one's Windows confirmation, negative controls and wrong predictions
  are recorded in HISTORY's entry for this file at `aafded0`, and in the Notes.
- **The six commits for findings 19–28 and the direction-box tests** — `9c4917c`,
  `05a12c7`, `2c7a7d1`, `4e2b1c8`, `486f1a5`, `3bfa6b7`. Done.
- **G — macro in the CONSERVATIVE branches (17). Done at `7d0024e`.** Scoped in full before any diff; the live log replayed through the router
  before and after (2 of 43 runs change, both 15 September, both then refused by the
  gate because the records predate F); the live run before the commit. The work order
  list is finished.

## Resolved this session

- **Item 5 of round 8's preparation list, run 1** — built, checked, tagged and sent;
  scored 0 of 4; closed to Part 7 (`d27743f`; DECISIONS, "Decision, 4 October 2026 —
  round 8's first run: 0 of 4, no Part 7 to it, run 2 next").
- **Run 2** — sent, scored 2 of 4, a pass (the commit that writes this line; DECISIONS,
  "Decision, 4 October 2026 — round 8's second run: 2 of 4, a pass; Part 7 to it").
- **The pushes of `217ede6` and `d27743f`** — filed above, once; no deviation reported.
- **The once-per-session rewrite of this file.** The previous version, as at `217ede6`,
  is in HISTORY verbatim, headings demoted one level, proven by un-demotion with a
  negative control (this commit's message has the result).

## Open items

Items marked **Viktor's call** are his to decide; he writes his position first and
Claude critiques it.

- **Owed to the next commit:** nothing, unless this commit's push deviates from its
  prediction (ruling on proposal (b), 27 September).
- **The independent audit, round 8 — the preparation list.** Claude's, under the
  delegation of 4 October; Viktor runs the commands. In this order:
  1. **Done, 4 October:** checks 1–3 of the round-8 decision, as far as they can be made
     before the send (DECISIONS, "Decision, 4 October 2026 — round 8: Xiaomi
     MiMo-V2.6-Pro, the full package in one session").
  2. **Done, 4 October:** Viktor downloaded MiMo's tokenizer files into
     `G:\Phase_7_Engine_Random_Files\Docs\04_Data\MiMo-V2.6-Pro-MOPD_tokenizer_adea8e2\`;
     Claude checked them against both repositories' listings and read the template
     (DECISIONS, "Decision, 4 October 2026 — round 8's tooling").
  3. **Done, 4 October, at `4a4c6ce`:** the tooling commit —
     MiMo in `package_token_check.py`, the send repointed to round 8 with the provider
     order run by `--provider`, and `build_round8_package.py`, which makes round 8's
     folders from round 7's built files checked by hash (a refinement of "built from the
     tag": DECISIONS, the same entry). **Check 4 passed on a trial build**: 209,763
     tokens to spare.
  4. **Done, 4 October, at `217ede6`:** rev 9 of the
     instruction (`docs/audit_package/item16_review_instruction_rev9.md`, new) and the
     Part 7 document corrected in place (DECISIONS, "Decision, 4 October 2026 — rev 9
     and the Part 7 correction"). Rev 9 says why the manifest reads `Round: round7`;
     its Section 2 counts were re-run on the package as built (twenty-one rules, not
     fifteen) and its Section 4a list held; MiMo's knowledge cutoff is stated with its
     one source. On a trial build in the sandbox (Linux; round 7's files staged from
     E:, rev 9 and the Part 7 document with CRLF as on a Windows checkout) the first
     message is 430,813 tokens by MiMo's tokenizer and the whole conversation fits with
     208,193 to spare (19.9%), at most $0.72.
  5. **Run 1 — done, 4 October; 0 of 4.** The send, as round 7's item 10 did (HISTORY, this file as it stood at
     `1523e0c`): Viktor runs `python docs/build/build_round8_package.py` and Claude
     compares his build with the sandbox's (rev 9's SHA-256 on a Windows checkout:
     `579db7a12d12858d…`, the Part 7 document's `487b42b99e7e564e…`, payload
     `b6950de5809bc68a…`); the endpoints are re-read by the send's own query;
     `git diff --stat 01f2892 round7-sent-2026-09-30 -- "*.py" ":!docs"` prints
     nothing; `git diff --stat round7-sent-2026-09-30 HEAD -- "*.py" ":!docs"` names
     only `tests/test_package_token_check.py` and `tests/test_send_audit_round.py`
     (rev 9 says so to the auditor); the commit the send is made from is tagged; the probe, then `--send`
     (Xiaomi first; if its endpoint refuses, `--provider` names the next in the order);
     the first reply committed the same day, with `docs/audit_package/round8/MANIFEST.md`,
     which git tracks; then `--send-part7`, to the provider that answered. The auditor
     goes into the independence ledger at the time of use. Every check came out as
     predicted; run 1 went to Xiaomi's endpoint and scored 0 of 4, so it gets no Part 7
     and is closed in the send script (DECISIONS, "Decision, 4 October 2026 — round 8's
     first run: 0 of 4, no Part 7 to it, run 2 next"). **Viktor checks the score.**
  5a. **Run 2 — done, 4 October; 2 of 4, a pass.** The same first message, Xiaomi's
     endpoint, the probe first; its reply committed the same day by the commit that
     writes this line (DECISIONS, "Decision, 4 October 2026 — round 8's second run").
  5b. **Next — Part 7 to run 2**, after the commit that writes this line is pushed:
     `--send-part7`, with no `--provider` (it goes to Xiaomi's endpoint, which answered).
     Counted in the sandbox at 658,197 tokens with the first reply's reasoning: fits,
     259,307 to spare. Its reply (`turn2_*`) is committed the same day.
  6. **Scoring:** Claude scores against the four "Found means" sentences of the Part 7
     document and Viktor checks. Run 1: 0 of 4. Run 2: 2 of 4 (S2, S4), a pass. Two runs in all; fewer than two of the
     four found in both runs means the fallback (DECISIONS, "Decision, 4 October 2026 — the fallback:
     scoped packages").
  7. **The result is Viktor's to accept or reject**; then triage (his), and the same
     auditor verifies the fixes (the 14 September precedent).
- **The ledger entry for round 7**, which the roster-and-ledger document asks for at the
  send, from the provider's record: Poolside, `poolside/laguna-s-2.1` (OpenRouter's
  permaslug `poolside/laguna-s-2.1-20260720`), 30 September 2026 at 09:58 UTC, through
  the API with Viktor's key, one request, 455,360 prompt tokens; shown the first message
  — rev 8, the Constitution's audit copy, the source and test bundles, the manifest, the
  history without messages and the execution transcripts; role: independent auditor,
  round 7, Parts 1–6 — run 1, which counts as a run and does not get Part 7 (ruling of
  30 September). Recorded here; the document outside the repository is to be reissued
  with it once the round's runs are done, so one reissue carries every run's entry —
  Claude's choice, Viktor's to change. **Run 2's entry**, from the provider's record:
  Poolside, `poolside/laguna-s-2.1` (permaslug `poolside/laguna-s-2.1-20260720`),
  30 September 2026 at 11:43 UTC, through the API with Viktor's key; a probe request
  (59 prompt tokens, nothing from the package) and one request, 455,360 prompt tokens,
  with reasoning requested; shown the same first message; role: independent auditor,
  round 7, run 2, Parts 1–6; 0 of 4, no Part 7. Round 7's runs are done, so the reissue
  is now due. **Claude's, under the delegation of 4 October:** reissued once, after round
  8's runs, so it carries round 7's two entries, round 8's, and Xiaomi added to the
  roster with the facts checked on 4 October. **Round 8's run 1 entry**, from the
  provider's record: Xiaomi, `xiaomi/mimo-v2.6-pro` (permaslug
  `xiaomi/mimo-v2.6-pro-20260921`), 4 October 2026, 15:51:46 to 16:02:09 UTC, through
  the API with Viktor's key; a probe (24 prompt tokens, nothing from the package) and one
  request, 430,820 prompt tokens, reasoning requested (40,434 reasoning tokens); shown
  the first message — rev 9, the Constitution's audit copy, the source and test bundles,
  the manifest, the history without messages and the execution transcripts; role:
  independent auditor, round 8, run 1, Parts 1–6; 0 of 4, no Part 7. It named itself
  Claude (DECISIONS, the same entry). **Round 8's run 2 entry**, from the provider's
  record: Xiaomi, `xiaomi/mimo-v2.6-pro` (permaslug `xiaomi/mimo-v2.6-pro-20260921`),
  4 October 2026, 16:45:32 to 17:04:29 UTC, through the API with Viktor's key; a probe
  (nothing from the package) and one request, 430,820 prompt tokens (430,720 from the
  provider's prompt cache), reasoning requested (68,464 reasoning tokens); shown the
  same first message; role: independent auditor, round 8, run 2, Parts 1–6; 2 of 4.
  Part 7 to follow; its entry is added when it is sent.
- **Viktor, outside the repository:** delete `D:\phase7_engine_MOVED_TO_E` and
  `D:\Phase_7_Engine_Random_Files_MOVED_TO_G` once satisfied with the copies on E: and
  G: (HISTORY, 26 September, ninth session). Not urgent.
- **Round 7's preparation list (items 1–13)** is closed: every item done, or ended
  with the round. Its full text, with item 10's checks at the send, is in HISTORY, in
  this file as it stood at `1523e0c`; round 8's list (above) points to it.
- **The model roster and the independence ledger are one document since
  30 September:** `Docs\Phase7_Model_Roster_and_Ledger_2026-09-30.pdf` in
  `G:\Phase_7_Engine_Random_Files` (5 pages, SHA-256
  `edb506c258c1bd711dc7b36263500b62c6f7e96ffcb1a29f469ce798eb39a656`), made at Viktor's
  request from five documents, each kept as it was: the roster of 30 September (item 8
  above), the ledger and the roster of 29 September, and the two of 22 September. Where
  they disagree the later record wins; its section 9 lists what it carried over and what
  it left out. Clean for a full round — Poolside (chosen for this round) and Amazon
  (Nova 2 Pro, a preview release); scoped rounds only — Upstage, NVIDIA, Cohere, AI21.
  NVIDIA moved there because OpenRouter serves Nemotron 3 Super at 262K on both its
  endpoints (checked 30 September), not the 1M the earlier rosters gave. Once this round
  spends Poolside, Amazon is the only full-round lab left on the list. Mistral is spent
  (HISTORY, 2 September; reaffirmed 29 September). Viktor stated on 29 September that he
  has never used an NVIDIA or Poolside model anywhere. NVIDIA is kept for a scoped
  round; whether its part in Mistral NeMo counts against it is moot for this round.
  Model facts other than Laguna S 2.1's and Nemotron 3 Super's served context and output
  cap were checked on 22 September and not since. **Xiaomi is not on it:** MiMo-V2.6
  was released on 21–22 September, after the last check. Round 8's decision
  (DECISIONS, 4 October) records Xiaomi's facts as read on 4 October; the reissue
  (above) adds it.
- **The independence ledger is outside the repository, reconciled 29 September**
  against OpenRouter's activity export — 727 requests, 22 August to 14 September 2026,
  kept as `Docs\04_Data\OpenRouter_Activity_Export_2026-09-29.csv` in
  `G:\Phase_7_Engine_Random_Files` (SHA256 `d0edf17e0c42b35e3879a206e8a2c1d0`
  `6c9c8cfdb8bb6945615ea25baef336b8`) — and reissued as
  `Docs\Phase7_Spent_Models_Ledger_2026-09-29.pdf`; the 22 September version is kept as
  it was. **Since 30 September it is section 3 of the roster-and-ledger document above**,
  where the export was re-read: its hash matches, and every count agrees with the
  29 September ledger. Newly noted there: one of the 727 rows records no model, provider
  or tokens — the only request ID starting `gen-tool-`, which the document reads, without
  OpenRouter's confirmation, as a Chatroom tool step rather than a model request.
  Every lab in the export was already spent except Mistral (above). The export
  covers OpenRouter only: Gemini, ChatGPT, Copilot, Grok and the second Claude instance
  were used elsewhere and stand on the repository's record. **Grok's entry**, owed since
  26 September, is in the reissued ledger from Grok's own account of what it read: the
  Constitution and the Assistant Instruction in full; README and this file at about
  `c5dc4cd`; production code in `main.py`, `live_trading.py`, `data/`, `core/`,
  `models/`, `indicators/` and `structure/`; the full `tests/` tree and fixtures; one
  live panel Viktor pasted. It is Grok's account, not a provider export, saved as
  `Docs\02_Reviews_and_Feedback\Grok_Inventory_of_What_It_Read_2026-09-26.txt` in
  `G:\Phase_7_Engine_Random_Files` (SHA256 `0d923a095bc112bda5ad11e6be39a98f0d5a48ad`
  `139938ed119d18ebd96a71ed`).
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
- **Viktor's call — repointing `docs/build/build_findings_bundle.py`** at the round-1
  folder, so `Phase7_Audit_Findings_Complete.pdf` could be rebuilt. A tooling change;
  not done.
- **Claude's — README.md's "Independent audit" and "Backtesting" rows are stale**
  (seen 29 September; not changed since — `59b747a`, `12b483e`, `3e8191a` and `1523e0c`
  touched only README's test counts). The first still says the next round is paused until work
  order G and the six findings are done, which happened at `7d0024e`; the second
  predates the ruling of 29 September on what opens backtesting. Both are written in
  Viktor's voice, so the new wording goes to him before it lands.
- **Claude's — the running change list for the audit:** `docs/audit_change_list.md`,
  from the baseline `e65a0f7` (the tree round 6's fix-verification was sent). **Every
  later commit that changes engine code, tests or tooling adds its line there in the
  same commit.** `22cb39b` added the ruling of 28 September to its rulings section
  and named `7d0024e` where G's commit wrote "the commit that adds this line". The
  rulings of 29 September are not added: none changes what the engine must do, or any
  code.
- **The pre-push hook is installed per clone, not per repository.** After any re-clone
  (including after a machine wipe), run `git config core.hooksPath githooks`;
  `session_handover_check.py` section 6 flags a clone without it.
- **Unrelated, not urgent:** confirm which YH programme permits AI-assisted
  examensarbete work.
- **Viktor's call — the paper-trading setup.** Specified by the ruling of 28 September
  (points 3, 5 and 7–11); nothing is built: unattended runs every 4h per pair
  (question 14 below), the paper account in ten slices, the scoring. It is not an
  engine change. When, and on which pairs, is Viktor's.
- **Viktor, outside the repository:** the BLESSUSDT screenshot of 28 September is not
  in the repository — it shows his browser, and the repository is public. DECISIONS
  describes its marks in text. Keeping the image, for example in
  `G:\Phase_7_Engine_Random_Files`, is his choice.
- **The questions of 28 September.** Claude's sixteen, asked before the ruling. Viktor
  answered 1, 2, 15 and 16 (what the engine claims, what ends development, whether a
  year of paper trading is enough, what weight the portfolio carries) — that is the
  ruling. The rest are open; Claude can answer 3–13 from the code and the log, and 14
  is shared.
  3. Where did each number come from — the six bias weights, the 30/70/±20 thresholds,
     the 8% and 15% limits? Which were derived, and which chosen?
  4. How many independent pieces of evidence does a decision rest on? Found so far:
     macro counted twice (fixed at G), RSI reaching `bias_score` twice, the four-factor
     overlap.
  5. How often does the engine say "trade" now, and is the rate plausible? The live log
     holds only hand-started runs, so this needs runs over past candles — close to the
     backtest pause, and Viktor's call.
  6. Does the panel always show exactly what the engine decided?
  7. Can every logged decision be rebuilt from its record, and for how long?
  8. Would the tests catch a change that is wrong but consistent?
  9. Who has checked the work since 14 September? So far Claude alone.
  10. Are there still paths a healthy run never takes?
  11. Do the documents describe the code, or each other?
  12. Does the engine work live on a pair other than AEROUSDT?
  13. How often does it run degraded on live data, and would anyone notice?
  14. Can it run unattended for a year and keep a clean log?
- **Viktor's, not chosen — ten questions to ask of the engine (1 October).** He asked
  for them to be kept: What does it take in? What does it produce? What assumptions
  does it make? What mathematical or technical principle is it based on? What can make
  it fail? How do we know it is working correctly? What tests would expose a false
  result? Which parts are deterministic and which stochastic? Which parts are
  empirically validated and which theoretically justified? What would convince us that
  the entire thing is wrong? What to do with them — Claude answers from the code, his
  answers first, given to the auditor, or made standing questions — is not chosen. With
  them, from the same ChatGPT conversation, hostile reviews of the Constitution (for
  example, "construct a compliant implementation that is nevertheless obviously
  wrong"); he agreed to take that up when the questions are, starting with whether each
  of round 7's four test bugs breaks a specific Constitution rule. Neither is part of
  the delegated audit, and neither goes to round 8's auditor unless he says so.
