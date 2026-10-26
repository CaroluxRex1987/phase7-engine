# Next step — read this first

*26 October 2026, from 18:56. Rewritten by the commit that files Claude's decision on
entry 26 of the list for after the audit — Goal B's truncation rule, under Viktor's
delegation, docs only — and records `3d7e6cb`'s landing; the version it replaced — as
it stood at `3d7e6cb` — is in HISTORY verbatim.
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

**One exception, since 4 October: the independent audit.** Viktor delegated it to Claude
outright and asked for no more questions or decisions on it (DECISIONS, "Delegation, 4
October 2026 — the next independent audit is Claude's to run"). Work on the audit goes
ahead without asking what he wants first; he runs the commands. Round 8 is finished:
triaged on 5 October, its fixes landed, and its fix verification — the last part of it,
Claude's under the delegation as Claude reads it — accepted by Viktor on 17 October
(DECISIONS, "Ruling, 17 October 2026 — round 8's fix verification accepted on the stop's
answer; the release gate reopens"). What is left under the delegation is running the next
audit, on the plan as ruled on 17 October, with its fallback (DECISIONS, "Ruling,
17 October 2026 — Amazon's audit …" and "… — if Amazon fails the check twice …"),
scored on the four held-back defects ruled on 18 October (DECISIONS, "Ruling,
18 October 2026 — the four held-back defects …") — Claude's reading, his to change.
The roster and ledger were
reissued on 17 October (Open
items, "The model roster and the independence ledger"). The
fixes were never under it: they were his triage rulings. Everything else still follows
the rule above.

## Where the project is

**Round 8 is over, and triaged.** Xiaomi's MiMo-V2.6-Pro audited the whole engine on
4 October, from the package built at the tag `round7-sent-2026-09-30` (`e186423`); it was
sent from `217ede6`, tagged `round8-sent-2026-10-04`. Run 1 found 0 of the 4 test bugs,
run 2 found 2 of 4 — a pass — and Part 7 went to run 2. Viktor accepted the result in a
narrow form: the findings go to triage, the ratings do not count toward opening
backtesting, and backtesting stays closed (DECISIONS, "Ruling, 4 October 2026 — round 8's
result …"). **He triaged it on the night of 4 to 5 October**, beside a review Claude
wrote that night at his request, of the engine, the Constitution and round 8 — not
independent, and counting toward no gate. `eb86846` filed the triage (DECISIONS,
"Ruling, 5 October 2026 — round 8 triaged …" and "Correction, 5 October 2026 — two of
rev 9's requirement sentences were wrong"). In short: the stop no
longer depends on conviction or trend health, a break of Item 14 ruled Critical
(confirmed by Viktor on 5 October); the release gate closed until that fix had landed
and round 8's auditor had verified it (it reopened on 17 October); the risk regime comes from volatility alone; no
trade under ADX 20 replaces the exhaustion flag; the trend score waits; test runs get a
log of their own; the BTC-adjusted confidence line goes; the label and record fixes are
made now; F4 stays on the list; and the freeze lifts. **Three fixes have landed: the
stop**, at `c2b07fb`, **the trend gate**, at `1b25f36`, **and the regime**, at
`fcb7823`. **The label and record batch is done:** B6, runs on pinned data keeping
records of their own, at `9e507b1`, N5, Bitcoin reference only, at `6469a67`, F3,
a frame with no readable time axis rejected, at `ae37795`, F5, the band distance
labelled from the band's midpoint, at `9d00d99`, F6, `clean_series` without its
look-ahead method, at `27d3ed5`, F8, one name for one meaning, at `9051ffd`, F9,
four claims the code did not support, at `e5ac20a`, the fallback sweep at
`797bdc9`, the two repeated readings at `69c92d6`, B4's labels at `22a9a35`, B7 at
`d77a8c4`, B9 at `64ad625`, B10 at `9ea1cf3`, and Part 4's three test shapes at
`f00bef6`. **On
12 October the panel's fallback readings and two
repeated readings joined the batch; on 13 October their shape, scope and order were
ruled** (DECISIONS, "Ruling, 13 October 2026 — the fallback sweep: the 12 October
additions' shape, scope and order"): a value only printed or recorded falls back to
the router's own word for an absent one, a value with no such word or one the engine
computes with is read directly, and every default in the panel and the router's
decision-building code is listed in a test; the REGIME line and the STRUCTURE line's
Vol field are gone, so each reading is printed once. **On 14 October B4's labels'
shape was ruled** (DECISIONS, "Ruling, 14 October 2026 — B4's labels: their shape"):
the sentences that print the momentum divergence say what is compared — this candle's
close and RSI against the close and RSI four candles back — and the volume label
VOLUME DIVERGENCE is FADING VOLUME, matched whole; every score is unchanged, and the
keys keep their names. **On 15 October B7's shape was ruled** (DECISIONS, "Ruling,
15 October 2026 — B7: the distance limits record the regime"): the risk regime is
classified before the 15% limit and the 0.2% floor, and both record it where they
recorded UNKNOWN; every verdict and reason is unchanged, and the 15% limit stays.
**On 15 October B9 was ruled** (DECISIONS, "Ruling, 15 October 2026 — B9: Bitcoin's
SuperTrend is read directly"): the fallback sweep had already made all of it but
Bitcoin's SuperTrend, without naming B9; that is read directly, so a failed one makes
the BTC section unavailable for the run, and the asset's own SuperTrend read waits for
after the audit.
**On 15 October B10 was ruled** (DECISIONS, "Ruling, 15 October 2026 — B10: two outputs
agree with finding 4 and the action"): the simulated order records the band as
`ema_band`, its entry stays `current_price`, the decision log's name for it, and the
panel prints the note naming Target 1 only on a run whose action names a side — panel
only, as for finding 5; the three test shapes follow as one patch.
**On 15 October Part 4's three test shapes were ruled** (DECISIONS, "Ruling, 15 October
2026 — Part 4's three test shapes"): the golden coverage test fails when its baseline
is missing, and runs without `pandas_ta`; the non-finite test renders the golden
decision with each of its floats set to +inf, -inf and NaN in turn; the SuperTrend
level test, which Part 4 named beside it, runs the guard and asserts that SuperTrend
fails whole; and the watched error count is written as a number only in this file.
Tests and a docstring only: no decision, `code_hash` or golden field moves.
**On 16 October the fix verification was decided** (DECISIONS, "Decision, 16 October
2026 — round 8's fix verification: what is checked, what is sent, and to whom"),
Claude's under the delegation of 4 October, filed at `36de35d`.
The Critical's fix and round 8's fixed findings are checked against its own words;
every other change to code it read is checked for new defects; what was not fixed is
declared. MiMo-V2.6-Pro is pinned as in round 8, for one run, on a package close to
full size because the fixes touched most of the engine, and the commit sent from is
tagged first.
**On 17 October its tooling landed** (DECISIONS, "Decision, 17 October 2026 — the fix
verification's tooling"), Claude's under the same delegation, at `78ea37d`:
`docs/build/send_round8_fix_verification.py`, its instruction and its tests.
The package is built from git at the tagged commit, measured with MiMo's own tokenizer
at 341,082 tokens, and refused unless the probe is served by round 8's checkpoint. The
diffs start at `e186423`, the code round 8 read, not at `217ede6` as the decision of
16 October words it; the entry says why.
**The same morning it was sent and answered** (DECISIONS, "Fix verification, 17 October
2026 — round 8's auditor: the stop's fix holds, no new Critical; Viktor's to accept"),
filed at `d3188f2`. One run, from `78ea37d`, tagged
`round8-verify-sent-2026-10-17`, served by round 8's checkpoint on Xiaomi's endpoint.
The report: the stop's fix holds; no change adds a Critical; every fixed finding and
Part 4's three test shapes are fixed; no new defect in the nine other changes; none of
the items declared not fixed is worse. Claude checked twenty-three of its claims against
the code and found the code each describes; one quotation merges two passages. The reply is short for
its read — 7,309 reasoning tokens on 341,082, where round 8's run 2 had 68,464 on
430,820 — and it found nothing wrong anywhere. No second run (Claude's).
**Viktor accepted it at 09:37 the same morning** (DECISIONS, "Ruling, 17 October 2026 —
round 8's fix verification accepted on the stop's answer; the release gate reopens"), by
agreeing to Claude's suggestion: on A.1 alone, the stop's answer. A.2 — no new Critical
— is recorded rather than relied on, since the changes it names are eight of the
seventeen; sections B–F are triaged, noted, no action; there is no second run and no
other auditor now; and the next full audit names the stop's fix as its own question.
**The release gate is open again; backtesting is not.** What comes next is Viktor's to
choose (PACE FIRST, above), and what the triage left open is his too (Open items).
**Later the same morning, from 10:34**, asked what he wanted to do, Viktor asked for
Claude's suggestions and took them (DECISIONS, "Ruling, 17 October 2026 — the forward
measurement: ten pairs every four hours, and main.py takes them"). "Finished" needs 100
closed trades from one version, and nothing on record says how often the engine trades,
so it is to run every four hours on ten pairs, logging only, started by Windows Task
Scheduler on his machine. `main.py` takes the pairs and works from its own folder, at
`0491b84`; Viktor created the scheduled task after its push, and its first run, at 14:05,
wrote a record for each of the ten pairs (Open items, the forward measurement).
**In the afternoon, from 14:10**, Viktor asked for Claude's work first, as one docs-only
commit: new wording for README's three stale status rows, his to approve before it
landed, and the forward measurement's first checks, read from the logs on his disk, with
what its first records show of the trend score ("Found after 22 September", the
review's B1). He approved the wording at about 14:30, and `a235783` landed it. Asked
then whether he wanted to write his position on two of the questions of 6 October, he
answered one and asked for Claude's suggestion on the other, and at 16:58 agreed to
Claude's suggestions on both (DECISIONS, "Ruling, 17 October 2026 — Amazon's audit:
scored on four defects held back from the list, and its ratings are the ones that
count"): Amazon's audit is scored on four known minor defects held back from the list
for after the audit, and its ratings are the ones that count toward opening
backtesting, on conditions fixed before the send. At 17:44 he agreed to Claude's
suggestion for what follows if Amazon fails the check twice (DECISIONS, "Ruling,
17 October 2026 — if Amazon fails the check twice …"): a scoped round on Items 2, 3, 6
and 18 by a lab clean for scoped rounds, scored on the same four, and if that fails
too, backtesting stays closed until a lab that has never seen the project is
available.
**In the evening, from 18:43**, Viktor asked for the scheduled task's second run to be
filed, read from `logs/phase7_engine.log` on his disk: nothing ran at 18:00, so he
reads the run at 14:00 as a one-off (Open items, the forward measurement). He asked
next for the four held-back defects, under the rulings of 17 October; Claude proposed
them, with their "found means" sentences, in the message that delivered `fbd7877`'s
patch — Viktor's to accept or swap (Open items, the independent audit).
**On 18 October**, after pushing `fbd7877` at 05:36, Viktor asked at 07:56 for
Claude's suggestions on the four and at 07:58 agreed to them: H1 and H2 accepted, H4
replaced through a search of the files a scoped package would carry, H3 kept unless
the search found something clearly better. The search found H5, a flat candle
credited to the wrong volume bin, and at 09:28 he accepted it in H4's place
(DECISIONS, "Ruling, 18 October 2026 — the four held-back defects: H1, H2, H3 and
H5"). Under the plan of 6 October as changed on 17 October, the list for after the
audit, less the four, comes next — when he chooses to start it.
**On 19 October, from 09:08**, after pushing `8311167` at 08:49, Viktor asked for the
forward measurement's line on the 14:00 close of 18 October to be corrected, in the
session's first commit: his PC was not running at that close — nothing ran between
10:06 on 18 October and 02:05 on 19 October — so the question it was to answer needs
a later one (Open items, the forward measurement).
**On 19 October, from 10:19**, after pushing `d2dddf7` at 09:59, Viktor asked for the
sort of the list for after the audit first. Claude read the list's forty-five entries at
`d2dddf7` and put a table to him — kind, who decides, rough size and suggested order —
with six notes, and at 11:03 he agreed to Claude's suggestion (DECISIONS, "Ruling,
19 October 2026 — the list for after the audit, sorted: kind, who decides, size and
order"). Waves 0 and 1 — the rulings that steer the rest, and the work that moves no
`code_hash` — come first; no commit that moves `code_hash` lands before the forward
measurement's reading of 14 November; entry 1, S1, is worked after the audit, with the
four. Open, his: whether `bias_score`'s weighting joins the work before the audit, and
whether Fable 5.1 or Claude builds the list (Open items).
**On 19 October, from 18:16, going on into 20 October**, Viktor asked for the 14:00
reading first: nothing ran at the 14:00 close of 19 October, with the PC running, so
the run of 14:00:00.9 on 17 October did not come back (Open items, the forward
measurement). Asked on 20 October what was next, he asked for Claude's suggestions and
took them: wave 0 of the sort, entry 12 first. **At 06:47 he ruled F4's third path
Critical** (DECISIONS, "Ruling, 20 October 2026 — F4's third path is Critical …"), by
agreeing to Claude's suggestion, after the facts were put to him without a view:
macro's ×1.05 / ×0.90 on the entry score can move a setup across 70, between LONG and
CONSERVATIVE LONG, which breaks Tier 1 Item 11 and reaches live decisions. **The
release gate is closed again**; backtesting stays closed. The fix lands after the
reading of 14 November and before the send; its shape, and who re-audits it, are his
(Open items). **At 07:04 he ruled entries 38 and 22**, by agreeing to Claude's
suggestions: Claude builds the list, and Fable 5.1 waits until after Amazon's audit,
asked again at entry 10 (DECISIONS, "Ruling, 20 October 2026 — Claude builds the list
…"); and 4h only for now, with a guard that refuses any other timeframe, in wave 2
(DECISIONS, "Ruling, 20 October 2026 — B5: 4h only for now …"). Of wave 0, what is
left is his: whether `bias_score`'s weighting joins the work before the audit. Wave 1
can start when he chooses.
**On 20 October, from 09:18**, after pushing `391c338` at 09:13, Viktor asked for its
landing to be checked against his disk, then for Claude to decide what is next. Claude
split it by who decides. His, position first: whether `bias_score`'s weighting joins
the work before the audit — until he rules, the ruling of 22 September stands, and it
waits until after — and entries 26 and 31, Goal B's two rulings in wave 1. Claude's:
wave 1's five entries of its own, 13, 21 and 28 first as one commit, then 36 and 37, a
patch each. At 10:01 he said go. **Wave 1 has started:** `8360923` landed entries 13,
21 and 28 ("Found after 22 September", below), comments and docstrings only, so
`code_hash` and the golden snapshot held. It found two entries more: 47, BTC
structure's degradations are neither recorded nor logged; and 48, a tooling test that
pins a line of `models/risk_model.py`, found when that patch's first build broke it
(the same section). Claude suggested, in chat and not ruled, entry 48 next, then 36
and 37, a patch each, tests only.
**On 20 October, from 11:13**, after pushing `8360923` at 11:03, Viktor asked for its
landing to be checked against his disk, listed that suggestion, and asked Claude to
decide what is next. Wave 1's test gaps are Claude's under the sort of 19 October, so
Claude decided: entry 48 first. It is the one that fails the suite whenever a change
adds or removes a line above line 400 of `models/risk_model.py`, and the smallest;
entries 36 and 37 touch neither that file nor that test, so the order between them and
48 is Claude's choice, not forced. `ed005a0` landed entry 48 ("Found after
22 September", below), one test only, so `code_hash` and the golden snapshot held.
Entries 36 and 37 follow, a patch each. At 13:19, after `ed005a0`'s push had been read
off his disk, Viktor said go for entry 36. `e88e0dd` landed it (the same section), one
test only, so `code_hash` and the golden snapshot held.
**On 20 October, from 17:49**, after pushing `e88e0dd` at 14:23, Viktor asked for its
landing to be checked against his disk, then for entry 37, which Claude had decided on
in the session from 11:13, under the sort of 19 October: Part 4's other named tests
checked against round 8's Part 4, tests only. `d508b29` landed it (the same
section). Part 4 is right on each test it names as defective; six test files
change, ten controls are added, and `code_hash` and the golden snapshot hold. It found
two entries more: 49, `conftest.ENGINE_MODULES` is not every module in the engine; and
50, `README.md` writes the watched error count (the same section). `d508b29` was
pushed at 08:36 on 21 October.
**On 23 and 24 October, in the same session**, Viktor asked for a document of about 15
pages, for himself, on the most important questions about the engine: why it has the
indicators it has, which of them measure the same thing, where bias or circular
reasoning could still hide, and what to improve. Claude wrote it, measured from the
engine's own functions on the ten pairs' archived candles, and saved it outside the
repository (below). Viktor had ChatGPT and Gemini review version 1; Claude checked
their points against the code and the data, ran the decision-impact test one of them
asked for, and wrote version 2 with the corrections and the results. It is not
independent: Claude built most of the engine. Nothing was ruled; the decisions it
raises are Viktor's (Open items, "The engine's indicators"). `9f2f3d7` filed it, with
`d508b29`'s landing and the forward measurement's runs of 20 and 21 October, docs only,
pushed at 18:54 on 24 October. At 18:50 Viktor asked Claude to start on the tooling, the
second of the three things Claude had offered: `d410bfa` landed
`docs/build/indicator_overlap.py` and `tests/test_indicator_overlap_tool.py` (Open
items, "The engine's indicators"), pushed at 19:40 on 24 October. `34d8e3b` recorded
`d410bfa`'s landing, its test steps run after its commit, and GitHub's tips for
`9f2f3d7` and `d410bfa`: docs only, pushed at 20:14 on 24 October.
**On 24 October, from 20:16**, after pushing `34d8e3b`, Viktor asked for its landing
to be checked against his disk and recorded in the next commit, then which items in
Open items are his and which Claude's, and then for Claude's suggestion: entry 49,
`conftest.ENGINE_MODULES` held to the tree, Claude's under the sort of 19 October and
then the last of wave 1's entries that were Claude's. He agreed at 20:24. `ad34c02`
landed it ("Found after 22 September", below): tests only, so `code_hash` and the
golden snapshot held. It found one entry more: 51, the suite's file walk and
`code_hash`'s exclude different directories (the same section).
**On 25 October, from 15:20**, Viktor asked for `ad34c02`'s landing to be checked
against his disk and GitHub's tip to be fetched if the repository was reachable, both
recorded in the next commit (below). Asked what next, Claude suggested entry 51, or of
his items the questions on the engine's indicators first. He asked for suggestions on
those questions; asked whether to keep his rule of his position first, he kept it, and
Claude set out each question's options and what each would commit the engine to,
without a pick. At 16:30 he asked for Claude's suggestions, and at 16:34 accepted all
eight (DECISIONS, "Ruling, 25 October 2026 — the engine's indicators …"; Ruled — in
force). Filing them, Claude found that four of them reach three of the four held-back
defects, and that the entry score's trend multiplier has the shape of F4's third path;
asked how to file each, Viktor left both to Claude (DECISIONS, the two entries
"Decision, 25 October 2026 — …"). `89d2367` filed the three entries and recorded
`ad34c02`'s landing: docs and `README.md`, no code and no test.
**On 25 October, from 17:56**, after pushing `89d2367` at 17:47, Viktor opened the
session with its landing record, which Claude read off his disk again (below), and
asked for Claude's suggestion: entry 51, Claude's under the sort of 19 October, or of
his items entries 26 and 31, entry 50's shape or entry 47's place. He said go at
18:13. Reading the suite, Claude found a second walk of the engine with a list of
directories of its own, in `tests/test_no_fabricated_defaults_remain.py`, the same
defect, and told him before building that it would be fixed in the same commit, the
call being Claude's. `b387c03` landed entry 51 ("Found after 22 September", below):
tests only, so `code_hash` and the golden snapshot held. It found one entry more: 54,
the audit package's own list of the directories that are not the engine (the same
section).
**On 25 October, from 19:20, going on to 26 October**, after pushing `b387c03` at
19:18, Viktor opened the session with its landing record, as the session before had
written it for him. Claude read it against that session's checks and found two parts
saying more than the checks had shown: the commit message had been compared with its
line endings made the same — delivered CRLF, it is stored LF, as `git commit -F`
stores it — not byte for byte; and the session's first, failed comparison of GitHub's
files with his disk had added a CR to files its own `git archive` had already written
with CRLF, not to files GitHub holds as CRLF: GitHub holds the seven with LF (read
from GitHub that evening). The same overstatement was in this file for `89d2367`'s
commit message, written by `b387c03`: corrected below, Claude's error. On 26 October
at 09:36 Viktor asked for Claude's suggestion. GitHub asked the sandbox for
credentials, as for a repository that is not public, and attaching it failed, GitHub
not being linked to Claude; so the project's state was read off his disk. Claude
suggested entry 54, with the two corrections in the same commit, or of his items
entries 26 and 31, entry 50's shape or entry 47's place. He said go at 10:13.
`9862568` landed entry 54 ("Found after 22 September", below): a build script under
`docs/` and a test, so `code_hash` and the golden snapshot held. It found one entry
more: 55, the engine bundle's header (the same section).
**On 26 October, from 16:51**, after pushing `9862568` at 11:19, Viktor opened the
session with its landing record, as the session before had written it for him. Claude
read it off his disk and GitHub again (below): every part that could be read again
held, and two could not be. At 18:09 Viktor asked for Claude's suggestion: entry 55,
Claude's under the delegation of 4 October, or of his items entries 26 and 31, entry
50's shape or entry 47's place. He said go at 18:09. `3d7e6cb` landed entry 55
("Found after 22 September", below): a build script under `docs/` and a test, so
`code_hash` and the golden snapshot held. It found no entry more.
**On 26 October, from 18:56**, after pushing `3d7e6cb` at 18:44, Viktor opened the
session with its landing record, as the session before had written it for him. Claude
read it off his disk and GitHub again (below): every part that could be read again
held, and two could not be. At 18:59 Viktor asked for Claude's suggestion: entry 26,
his, position first, or stopping there. He said go at 19:00; shown what entry 26 asks,
he asked what leak, was told, and at 19:02 answered, "I don't understand. Just fix it
as you see fit." The commit that writes this line files Claude's decision on entry 26
under that delegation (DECISIONS, "Decision, 26 October 2026 — Goal B keeps a candle
only once it has closed at `t` (entry 26)"), docs only, and records `3d7e6cb`'s
landing. Entry 31 was not delegated and stays his.

**The review and the comparison are outside the repository**, in
`G:\Phase_7_Engine_Random_Files\Docs\02_Reviews_and_Feedback`:
`Phase7_Claude_Self_Review_2026-10-05` (the full review) and
`Phase7_Self_Review_Short_2026-10-05` (the short version), and
`Phase7_Freqtrade_Comparison_2026-10-05`, written later the same night — each as .md and
.pdf. Nothing was ruled on the comparison (Open items). In the same folder since
24 October: `Phase7_Engine_Understanding_2026-10-24` (version 1, 13 pages) and
`Phase7_Engine_Understanding_2026-10-24_v2` (version 2, 18 pages), each as .md and .pdf.

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
disagrees. The fixes of 5 October are Viktor's rulings; Claude builds them, and only
their order is Claude's.

**The independent audit was paused until the closed list was done** — DECISIONS,
"Ruling, 21 September 2026 — the independent audit paused" and "Ruling, 22 September
2026 — when the audit resumes". **With G landed at `7d0024e`, that condition is met.**
**The Constitution's step 8 binds:** "Re-audit the items that changed — independent
auditor again, not a self-check by whoever made the fix. 9) Only then … build the
backtesting architecture." Round 8 read every engine change since the last independent
round (round 6 fix-verification, 14 September) — the whole engine as at `e186423` — but
its ratings do not count toward opening backtesting (DECISIONS, "Ruling, 4 October 2026
— round 8's result …"), and the fixes of 5 October change the engine again, so **no
backtesting yet.** What opens it is now ruled (DECISIONS, "Ruling, 29 September 2026 —
what opens backtesting"): building needs Items 2, 3, 6 and 18 rated Compliant or fixed
and confirmed, no Critical or Major finding open, every fix confirmed by the same
auditor, and Viktor's declaration; running needs Goal B's harness built and tested and a
known-good checkpoint. Claude's second point of 21 September — the rule exists only as
text — is answered inside it: the entry-point guard is built with the first backtest
code.

**The twenty-second to thirty-first sessions (29–30 September)** prepared round 7, sent
it and closed it. Their accounts are in HISTORY, in this file's earlier versions; the
last, as it stood at `1523e0c`, was moved there by `ff12e17`.

**The sessions of 4 October** (`ff12e17`, `4a4c6ce`, `217ede6`, `d27743f` to `040a529`,
and `9e42d30`) filed the delegation, built round 8's tooling, wrote rev 9, sent round 8's
two runs and Part 7, and filed Viktor's ruling on the result. Their accounts are in
HISTORY, in this file's versions from `ff12e17` to `9e42d30`, the last moved there by
`eb86846`; what was filed from Claude's memory notes rather than from a chat is marked
there.

**The session of the night of 4 to 5 October** landed no commit. Viktor asked for a full
read-only review of the engine, the Constitution and round 8's audit, its findings to go
to triage beside round 8's and the report to stay outside the repository. Claude read the
tip `9e42d30` (a clone, checked against `master` and `origin/master` off Viktor's disk),
ran the engine's code on his real AERO candles, rebuilt from the run archives, and wrote
the review; Viktor triaged both the same night, every point by agreeing to Claude's
suggestion. A comparison with Freqtrade followed, read from Viktor's copy on F:. The
record is a resume note, `Docs\01_Handovers_and_Resume_Prompts\Phase7_Resume_2026-10-05.md`
in `G:\Phase_7_Engine_Random_Files`, and the reports beside it (above).

**The session of 5 October that filed the triage** (`eb86846`, docs only) had Viktor
confirm point 1, re-derived the triage's figures from the live log, and named the ten
test records in it. Its account is in HISTORY, in this file's version at `eb86846`,
moved there by `c2b07fb`.

**The session of 5 October, evening** (`c2b07fb`) landed fix 1, the stop, scoped in full
before any diff and with its live run before the commit. Its account is in HISTORY, in
this file's version at `c2b07fb`, moved there by `1b25f36`.

**The session of the night of 5 to 6 October** (`1b25f36`) landed fix 2, the trend
gate, scoped in full before any diff and with its live run before the commit; its two
test steps ran after the live run. Its account is in HISTORY, in this file's version
at `1b25f36`, moved there by `fcb7823`.

**The session of 6 October, early evening** (`fcb7823`) landed fix 3, the regime,
scoped in full before any diff, with the live log replayed through the risk check on
the code before and after, and with its live run before the commit. Its account is in
HISTORY, in this file's version at `fcb7823`, moved there by `9e507b1`.

**The session of 9 October** (`6469a67`) landed N5, the second patch of the label and
record batch, scoped in full before any diff, with the 38 run archives replayed before
and after and its live run before the commit; it also filed the positions of 6 and
7 October in DECISIONS. Its account is in HISTORY, in this file's version at `6469a67`,
moved there by `ae37795`. The accounts of the sessions before it are in the versions
before that.

**The session of 10 October, afternoon** (`ae37795`) landed F3, the third patch of the
batch: the validator refuses a frame with no readable time axis. It ran the auditor's
reproduction before building and found its account of the outcome wrong (Work order,
item 4, F3). Its account is in HISTORY, in this file's version at `ae37795`, moved there
by `9d00d99`.

**The session of 10 October, evening** (`9d00d99`) landed F5, the fourth patch of the
batch: the BAND DISTANCE line names the band's midpoint. Its account is in HISTORY, in
this file's version at `9d00d99`, moved there by `27d3ed5`.

**The session of 11 October, evening** (`27d3ed5`) landed F6, the fifth patch of the
batch: `clean_series` accepts only methods that read no later row. Its account is in
HISTORY, in this file's version at `27d3ed5`, moved there by `9051ffd`.

**The session of 11 October, late evening** (`9051ffd`) landed F8, the sixth patch of
the batch: "VWMA" names only the engine's VWMA, and the momentum label is printed once.
Its account is in HISTORY, in this file's version at `9051ffd`, moved there by
`e5ac20a`.

**The session of 11 October, near midnight, to 12 October, early morning** (`e5ac20a`)
landed F9, the seventh patch of the batch: four claims the code did not support, and
the labels ruled in with them. Its account is in HISTORY, in this file's version at
`e5ac20a`, moved there by `ef65f46`.

**The session of 12 October, morning** (`ef65f46`, docs only) filed Viktor's ruling of
08:24: the panel's eleven fallback readings and the two repeated readings join the
batch. Its account is in HISTORY, in this file's version at `ef65f46`, moved there by
`797bdc9`. Its two test steps were skipped at the time; Viktor
ran both on Windows at 09:06 on 12 October, and both matched (pytest 792;
`run_tests.py` 721 / 0 / 32) — recorded here at his instruction.

**The session of 12 October, evening, to 13 October, night** (`797bdc9`), configured
for Claude Opus 5.5, opened at `ef65f46` — `master` and `origin/master` on Viktor's disk, from
`.git/refs` staged off it — and asked Viktor first, as the pace rule says, between B4's
labels and the shape of the 12 October additions. Claude read the three fallbacks found
filing that ruling and showed that none can fire on the engine's path; a run of the
suite that recorded every `.get` default taken found 15 test files handing the panel
hand-built decisions, and no `engine_core` default taken. Claude's first lean, to
remove the fallbacks, was wrong, and was corrected to UNKNOWN once checked. Viktor
agreed to Claude's suggestions at 01:13 on 13 October and settled two questions the
rule left open by choosing the option Claude recommended (DECISIONS, "Ruling,
13 October 2026 — the fallback sweep …", which records Claude's three errors on the
way). It landed patch 1, the sweep, at `797bdc9`, with its live run before the
commit. Its account is in HISTORY, in this file's version at `797bdc9`, moved there by
`69c92d6`.

**The session of 13 October, night** (`69c92d6`) landed patch 2, the two repeated
readings, with its live run before the commit. Its pytest step ran on Windows before
the live run: the cache staged off Viktor's disk on 14 October was rewritten at 05:41
on 13 October and holds the five new tests' ids; the live record is from 05:50, the
commit from 06:05. Its account is in HISTORY, in this file's version at `69c92d6`,
moved there by `22a9a35`.

**The session that landed B4's labels** (`22a9a35`) ruled their shape at 06:23 on
14 October and landed them with the live run before the commit. Its file dated it "13
October, morning, to 14 October, morning"; from Viktor's disk, the apply was at 22:53
on 14 October, the pytest cache was rewritten at 22:55 and holds the eight new tests'
ids, the live record is from 23:00 on the new `code_hash`, and the commit from 23:09.
Its account is in HISTORY, in this file's version at `22a9a35`, moved there by
`d77a8c4`.

**The session that landed B7** (`d77a8c4`) ruled its shape at 02:12 on 15 October and
landed it with the live run before the commit. Its file dated it "14 October, night,
to 15 October, night"; from Viktor's disk, the apply was at 02:59 on 15 October, the
pytest cache was rewritten at 03:02 and holds the five new tests' ids, the live record
is from 03:49 on the new `code_hash`, and the commit from 03:52. Its account is in
HISTORY, in this file's version at `d77a8c4`, moved there by `64ad625`.

**The session that landed B9** (`64ad625`) ruled its two calls at 07:55 on 15 October
and landed B9 with the live run before the commit. Its file dated it "15 October, from
03:55"; as its commit message records from Viktor's disk, the apply was at 10:01 and
the pytest cache was rewritten at 10:03 and holds the five new tests' ids; the live
record is from 10:18 on the new `code_hash`, and the commit from 10:29. Its account is
in HISTORY, in this file's version at `64ad625`, moved there by `9ea1cf3`.

**The session that landed B10** (`9ea1cf3`) ruled its calls at 11:00 and 11:13 on
15 October and landed B10 with the live run before the commit. As its commit message
records from Viktor's disk, the apply was at 12:10 and the pytest cache was rewritten
at 13:05 and holds the ten new tests' ids; the live record is from 13:14 on the new
`code_hash`, and the commit from 13:30. Its account is in HISTORY, in this file's
version at `9ea1cf3`, moved there by `f00bef6`.

**The session that landed Part 4's three test shapes** (`f00bef6`) ruled their shapes
at 14:28 and 15:51 on 15 October and landed them without a live run, since they move
no `code_hash`. Its file dated it "15 October, from 13:33". From Viktor's disk, staged
on 16 October: the files it changed were written at 16:18:01, the pytest cache was
rewritten at 16:20:45, the commit is from 16:40:36 and `origin/master`'s ref from
16:40:48. Its account is in HISTORY, in this file's version at `f00bef6`, moved there
by `36de35d`.

**The session that decided the fix verification** (`36de35d`) opened on 15 October at
18:47 at `f00bef6`, paused at 18:56 for Viktor's weekly usage on Claude's advice, and
resumed at 04:27 on 16 October; with "Do it." at 04:28 Viktor agreed to splitting the
first stage in two. It filed the decision, docs only, committed at 05:30. Its account is
in HISTORY, in this file's version at `36de35d`, moved there by `78ea37d`.

**The session that sent the fix verification and filed its report** (`78ea37d`,
`d3188f2`) opened on 16 October at 05:44 at `36de35d`, configured for Claude Opus 5.5.
Viktor asked for a budget estimate first; with 13% of his weekly usage left, he paused
at 06:16 on Claude's advice and resumed at 06:17 on 17 October after the reset.
`78ea37d` landed the tooling: the apply was at 07:08, the pytest cache was rewritten 3
minutes later and holds the 25 new tests' ids, and the commit is from 08:39. Viktor's
dry run on Windows printed the sandbox's payload SHA-256 and token count exactly; the
tag was pushed; the send ran from 08:55 to 08:59. `d3188f2` filed the report and the
run's four files, and corrected three passages `78ea37d` left stale. From Viktor's disk,
staged in the session of 17 October from 09:24: the files its patch changed were
written at 09:15:45, the pytest
cache was rewritten at 09:18:24, and the commit is from 09:22:28. Its account is in
HISTORY, in this file's version at `d3188f2`, moved there by `67f6ec1`.

**The session that accepted the fix verification** (`67f6ec1`, docs only) opened on
17 October at 09:24 at `d3188f2`, configured for Claude Opus 5.5. Before Viktor wrote
anything, Claude named what its filed check of the report had missed — A.2's list. He
ruled at 09:37, by agreeing to Claude's suggestion (DECISIONS, "Ruling, 17 October 2026 —
round 8's fix verification accepted …", "How it was made"). `67f6ec1` filed the ruling
and corrected passages left stale. From Viktor's disk, staged in the session of
17 October from 10:34: the files its patch changed were written at 10:08:20, the
pytest cache was rewritten at 10:11:43, and the commit is from 10:19:51. Its account
is in HISTORY, in this file's version at `67f6ec1`, moved there by `0491b84`.

**The session that landed the forward measurement** (`0491b84`) opened on 17 October at
10:34 at `67f6ec1`, configured for Claude Opus 5.5. Asked what he wanted to do, Viktor
asked for Claude's suggestions at 10:50 and took them at 10:56; asked again at 11:42, he
agreed at 11:46 (DECISIONS, "Ruling, 17 October 2026 — the forward measurement …",
"How it was made"). Claude reissued the roster and ledger under the delegation. It
landed `main.py`'s change with its live runs before the commit, one per pair by hand,
recorded in its message. From Viktor's disk, staged in the session from 14:10: the
first patch's files were written at 13:14:04; the pytest cache was rewritten at 13:17:44, as that
session read it, and again at 13:54:08, 3 minutes 2 seconds after the second patch's
files were written at 13:51:06, and holds the nine new tests' ids; the live records
are from 13:27:45 to 13:29:16; the commit is from 13:59:27, and `origin/master`'s ref
from 13:59:43. Its account is in HISTORY, in this file's version at `0491b84`, moved
there by `a235783`.

**The session of 17 October, from 14:10**, configured for Claude Opus 5.5, opened at
`0491b84`, GitHub's tip, cloned; `master` and `origin/master` on Viktor's disk, from
`.git/refs` staged off it, matched it, and so did every file its first commit changes,
byte for byte. Viktor asked for Claude's work first, as one docs-only commit. Claude drafted
README's three rows; Viktor approved them as drafted at about 14:30, with the two
sentences that would have contradicted them, and put the other stale passages Claude
found on the list (Open items). Claude read the forward measurement's first runs and
the trend scores from the logs on his disk and filed them (Open items, the forward
measurement; "Found after 22 September", B1), with his query of the scheduled task,
pasted at 14:28, and set how the measurement is counted before any reading (DECISIONS,
"Decision, 17 October 2026 — how the forward measurement is counted"). The session
paused at 14:44 at Viktor's word, with 3% of his session limit left and the patch and
its message already on his disk, and resumed at 16:26 after the reset. `a235783` landed
them, `README.md` and docs only: from Viktor's disk, the apply was at 16:27:35, the
pytest cache was rewritten at 16:31:18, the commit is from 16:48:25 and
`origin/master`'s ref from 16:48:39, and GitHub's tip matched the verified files byte
for byte. `8d5d64a` filed Viktor's rulings of 16:58 on two of the questions of
6 October, docs only: from his disk, the apply was at 17:08:32, the pytest cache was
rewritten at 17:12:10, the commit is from 17:29:56 and `origin/master`'s ref from
17:30:08, and GitHub's tip matched the verified files byte for byte. `a48d9e5` filed
his ruling of 17:44 on what follows if Amazon fails the check twice, docs only: from
his disk, staged in the session from 18:43, the apply was at 18:12:06, the pytest
cache was rewritten at 18:15:11, the commit is from 18:28:49 and `origin/master`'s ref
from 18:29:01, and GitHub's tip, cloned, matched his disk's two files byte for byte.

**The session of 17 October, from 18:43, going on into 18 October**, configured for
Claude Opus 5.5, opened at
`a48d9e5`, GitHub's tip, cloned; `master` and `origin/master` on Viktor's disk, from
`.git/refs` staged off it, matched it, and so did both files its first commit
changes, byte for byte. Viktor asked for the scheduled task's second run to be filed, read from
`logs/phase7_engine.log` on his disk, and then for the four held-back defects. Claude
read the process log and the ten decision logs, staged off his disk at 18:46 and
19:12 (Open items, the forward measurement). `fbd7877` filed the first, docs only:
from his disk, the apply was at 05:18:51 on 18 October, the pytest cache was rewritten
at 05:22:59, the commit is from 05:36:29 and `origin/master`'s ref from 05:36:43, and
GitHub's tip, fetched, matched the verified files byte for byte. The session went on
on 18 October: Viktor ruled on the four at 07:58 and 09:28, after Claude's search of
the files a scoped package would carry, and `8311167` filed the ruling, docs only:
from his disk, staged in the session of 19 October, the apply was at 08:02:55 on
19 October, the pytest cache was rewritten at 08:05:56, the commit is from 08:48:57
and `origin/master`'s ref from 08:49:11, and GitHub's tip, cloned, matched his disk's
two files byte for byte.

**The session of 19 October, from 09:08**, configured for Claude Opus 5.5, opened at
`8311167`, GitHub's tip, cloned; `master` and `origin/master` on Viktor's disk, from
`.git/refs` staged off it, matched it, and so did both files its commit changes, byte
for byte. Viktor asked for the forward measurement's line on the 14:00 close of
18 October to be corrected, in the session's first commit. Claude read the process
log, staged off his disk at 09:18 (Open items, the forward measurement). `d2dddf7`
made the correction, docs only: from his disk, staged in the session from 10:19, the
apply was at 09:51:49, the pytest cache was rewritten at 09:54:44, the commit is from
09:59:41 and `origin/master`'s ref from 09:59:56, and GitHub's tip, cloned, matched his
disk's two files byte for byte. Four points of that session stayed in chat, and Viktor
listed them at the start of the next: Claude's suggestion to sort the list for after
the audit, docs only, nothing filed until he approved it (ruled at 11:03, above); after
he sorts the Bedrock billing, Claude checks whether Nova 2 Pro can be reached and
whether the full package fits (Open items, the independent audit); his PC is now on day
and night, and the process log is read after 14:05 on 19 October for the 14:00
question (Open items, the forward measurement); and `d2dddf7`'s landing, not yet in
this file, was to be read off his disk. Its account is in HISTORY, in this file's
version at `d2dddf7`, moved there by `aa9e7ac`. (`391c338` left this sentence saying
"the commit that writes this line"; corrected on 20 October.)

**The session of 19 October, from 10:19**, configured for Claude Opus 5.5, opened at
`d2dddf7`, GitHub's tip, cloned; `master` and `origin/master` on Viktor's disk, from
`.git/refs` staged off it, matched it, and so did all three files its commit changes,
byte for byte. Viktor asked for the sort of the list for after the audit first, and
agreed to it at 11:03 (above). `aa9e7ac` filed the ruling and `d2dddf7`'s landing, docs
only: from his disk, staged in the session from 18:16, the apply was at 11:42:43, the
pytest cache was rewritten at 11:45:34, the commit is from 11:55:08 and
`origin/master`'s ref from 11:55:23, and GitHub's tip, cloned, matched his disk's three
files byte for byte. Viktor had read the same times off his disk at 12:06 and left
them in chat, with the 14:00 reading not yet made; he listed both at the start of the
next session. Its account is in HISTORY, in this file's version at `aa9e7ac`, moved
there by `391c338`.

**The session of 19 October, from 18:16, going on into 20 October**, configured for
Claude Opus 5.5, opened at `aa9e7ac`, GitHub's tip, cloned; `master` and
`origin/master` on Viktor's disk, from `.git/refs` staged off it, matched it, and so
did every file its commit changes, byte for byte. Viktor asked for the 14:00 reading
first, read from the process log staged off his disk (Open items, the forward
measurement), and on 20 October for Claude's suggestions, which he took (above).
`391c338` filed the three rulings, the reading and `aa9e7ac`'s landing, with README's
"Engine code" and "Release gate" rows and the paragraph under its table, in wording
he approved, docs and `README.md`: from his disk, staged in the session of 20 October
from 09:18, the apply was at 08:57:41, the pytest cache was rewritten at 09:00:34, the
commit is from 09:13:11 and `origin/master`'s ref from 09:13:25, and GitHub's tip,
cloned, matched his disk's four files byte for byte. Viktor had read the same times off
his disk at 09:17 and left them in chat; he listed them at the start of the next
session. Its account is in HISTORY, in this file's version at `391c338`, moved there by
`8360923`.

**The session of 20 October, from 09:18**, configured for Claude Opus 5.5, opened at
`391c338`, GitHub's tip, cloned; `master` and `origin/master` on Viktor's disk, from
`.git/refs` staged off it, matched it, and so did every file `391c338` changes and
every file `8360923` changes, byte for byte. Viktor asked for `391c338`'s landing
first, then for Claude to decide what is next, and at 10:01 for it to start (above).
`8360923` landed entries 13, 21 and 28 and recorded `391c338`'s landing: comments and
docstrings in `core/engine_core.py`, `models/risk_model.py`, `run_tests.py` and five
test files, and docs: from his disk, staged in the session from 11:13, the apply was at
10:44:24, the pytest cache was rewritten at 10:47:55, the commit is from 11:03:26 and
`origin/master`'s ref from 11:03:39, and GitHub's tip, cloned, is `8360923`. Claude had
read the same times off his disk after the push, in chat only; Viktor listed them, with
Claude's suggestion for what came next, at the start of the next session. Its account is in
HISTORY, in this file's version at `8360923`, moved there by `ed005a0`.

**The session of 20 October, from 11:13**, configured for Claude Opus 5.5, opened at
`8360923`, GitHub's tip, cloned; `master` and `origin/master` on Viktor's disk, from
`.git/refs` staged off it, read `8360923`. Each of the eleven files `8360923` changes is,
on his disk, byte for byte an autocrlf checkout of GitHub's tip — the commit's blob with
every LF as CRLF, which is how git checks a text file out on Windows here (`* text=auto`);
compared with the raw blobs, every one differs by its CRs alone. Viktor asked for
`8360923`'s landing first, then for Claude to decide what is next (above). `ed005a0`
landed entry 48 and recorded `8360923`'s landing: one test in
`tests/test_send_round8_fix_verification.py`, and docs. From his disk, staged in that
session after the push: the apply was at 11:37:58, the pytest cache was rewritten at
11:42:14, the commit is from 11:53:21 and `origin/master`'s ref from 11:53:40; `master`
and `origin/master` read `ed005a0`, GitHub's tip, fetched, is `ed005a0`, and its four
files on his disk and on GitHub are byte for byte the tree that was verified.
`e88e0dd` landed entry 36 and recorded `ed005a0`'s landing: one test in
`tests/test_decision_bar_integrity.py`, and docs: from his disk, staged in that session
after the push, the apply was at 13:59:36, the pytest cache was rewritten at 14:04:12,
the commit is from 14:23:07 and `origin/master`'s ref from 14:23:19, and GitHub's tip,
fetched, is `e88e0dd`. Claude had read those times off his disk after the push, in chat
only, and had decided entry 37 next, in chat; Viktor listed both at the start of the
next session. Its account is in HISTORY, in this file's version at `e88e0dd`, moved
there by `d508b29`.

**The session of 20 October, from 17:49, going on to 24 October**, configured for
Claude Opus 5.5, opened at
`e88e0dd`, GitHub's tip, cloned; `master` and `origin/master` on Viktor's disk, from
`.git/refs` staged off it, read `e88e0dd`. Each of the three files `e88e0dd` changes is,
on his disk, byte for byte an autocrlf checkout of GitHub's tip; compared with the raw
blobs, each differs by its CRs alone. The times above were read off his disk again:
the three files' mtimes, `.pytest_cache/v/cache/nodeids`, the commit date and `HEAD`'s
reflog, and `origin/master`'s reflog line "update by push". Viktor asked for
`e88e0dd`'s landing first, then for entry 37 (above). `d508b29` landed entry 37 and
recorded `e88e0dd`'s landing: six test files, `README.md`'s test counts, and docs. From
his disk, staged in that session after the push: the apply was at 08:29:24 on
21 October, the pytest cache was rewritten at 08:32:13 and holds the new tests' ids, the
commit is from 08:36:45 and `origin/master`'s ref from 08:36:58; `master` and
`origin/master` read `d508b29`, GitHub's tip, fetched, is `d508b29`, and its ten files on
GitHub are byte for byte the tree that was verified. `9f2f3d7` recorded that, the
forward measurement's runs of 20 and 21 October (Open items) and the document of
24 October (above): docs only. From his disk, staged in that session after its push: the
apply was at 18:47:23 on 24 October, the pytest cache was rewritten at 18:50:42, the
commit is from 18:54:34 and `origin/master`'s ref from 18:54:48; `master` and
`origin/master` read `9f2f3d7`, the commit message on his disk is the one delivered, and
`docs/PHASE7_NEXT.md` on his disk is the file built. GitHub could not be reached from
Claude's sandbox at first, because the repository had been made private; Viktor made it
public again that evening, and GitHub's `9f2f3d7`, fetched then, is byte for byte the
tree verified before that delivery (`d410bfa` left this paragraph saying its tip was
not fetched; corrected by `34d8e3b`). `d410bfa` landed the
overlap and decision-impact tool, with its tests and docs. From his disk, staged after
its push: the apply was at 19:39:43 on 24 October, the commit is from 19:40:11 and
`origin/master`'s ref from 19:40:22, its reflog line "update by push"; `master` and
`origin/master` read `d410bfa`, and GitHub's tip, fetched, is `d410bfa`, byte for byte
the tree verified before delivery, with the commit message delivered. Its two test steps
had not run before the commit: it came 28 seconds after the apply, and the pytest
cache on his disk was last written at 18:50:42, by `9f2f3d7`'s run. Claude asked for
them after the push, under their original numbers, to stop only if a count differed:
the cache was rewritten at 19:43:56 and holds the 13 new tests' ids, and Viktor
reported "Done. All good." `34d8e3b` recorded that, docs only. From his disk, staged
after its push in that session and read again in the session from 20:16: the apply
was at 20:06:09 on 24 October, the pytest cache was rewritten at 20:09:00, the commit is
from 20:14:19 and `origin/master`'s ref from 20:14:34, its reflog line "update by push";
`master` and `origin/master` read `34d8e3b`, and GitHub's tip, fetched, is `34d8e3b`,
byte for byte the tree verified before delivery. Claude had read those times off his
disk after the push, in chat only; Viktor listed them at the start of the next session.
Its account is in HISTORY, in this file's version at `34d8e3b`, moved there by
`ad34c02`.

**The session of 24 October, from 20:16**, configured for Claude Opus 5.5, opened at
`34d8e3b`, GitHub's tip, cloned; `master` and `origin/master` on Viktor's disk, from
`.git/refs` staged off it, read `34d8e3b`. Its one file, `docs/PHASE7_NEXT.md`, is on
his disk byte for byte an autocrlf checkout of GitHub's tip, and its mtime is still the
apply's. The times above were read off his disk again: the file's mtime,
`.pytest_cache/v/cache/nodeids`, the commit date and `HEAD`'s reflog, and
`origin/master`'s reflog line "update by push". And the cache's `lastfailed`, not read
before in this project, is `{}`, last written at 13:37:30 on 26 September, so the pytest
run of 20:09:00 recorded no failure: pytest 9.1.1 rewrites that file when a run's
failures differ from it and leaves it alone when they do not (an experiment in the
Linux sandbox, not on Windows). `run_tests.py` leaves no trace, so its count for
`34d8e3b` rests on Viktor's silence. GitHub's `34d8e3b` is the commit his `master`
reads, so its tree is the one his apply produced; the tree verified before that delivery
was in the sandbox of the session before and is not compared again here. Viktor asked
for `34d8e3b`'s landing first, then which Open items are his and which Claude's, then
for Claude's suggestion (above). `ad34c02` landed entry 49 and recorded `34d8e3b`'s
landing: two test files, `README.md`'s test counts, and docs. From his disk, staged in
the next session: the apply was at 21:34:19 on 24 October, the pytest cache was
rewritten at 21:39:04 and holds the new test's id, the commit is from 21:50:48 and
`origin/master`'s ref from 21:51:00, its reflog line "update by push"; `master` and
`origin/master` read `ad34c02`. GitHub's tip was not fetched in that session: the
sandbox was asked for credentials, the repository being private. Claude had read those
times off his disk after the push, in chat only; Viktor listed them at the start of the
next session. Its account is in HISTORY, in this file's version at `ad34c02`, moved
there by `89d2367`.

**The session of 25 October, from 15:20**, configured for Claude Opus 5.5, opened at
`ad34c02`. GitHub could not be read from Claude's sandbox at first: Viktor said at
15:21 that the repository was private, and attaching it to the session failed, GitHub
not being linked to Claude. He made it public again by 16:17; GitHub's tip, read with
`git ls-remote` and no credentials at 16:17:25 and again at his request at 16:20:54, is
`ad34c02`, and the sandbox cloned it. `master` and `origin/master` on his disk, from
`.git/refs` staged off it, read `ad34c02`; `.git/FETCH_HEAD` does not exist, so no
fetch has run in that clone and its `origin/master` is his git's record of the push.
Each of the six files `ad34c02` changes is on his disk byte for byte an autocrlf
checkout of GitHub's tip, CRLF throughout, and their mtimes are still the apply's,
21:34:19.192 to .200. The times above were read off his disk: those mtimes,
`.pytest_cache/v/cache/nodeids`, the commit object's date and `HEAD`'s reflog, and
`origin/master`'s reflog line "update by push". The cache holds
`tests/test_imports.py::test_engine_modules_is_every_module_in_the_tree`, which
`34d8e3b`'s `tests/test_imports.py` does not contain (read from GitHub's clone), so that
run collected the applied tree; its `lastfailed` is still `{}`, last written at
13:37:30 on 26 September, so the run recorded no failure. `run_tests.py` leaves no
trace, so its count for `ad34c02` rests on Viktor's silence. `89d2367` filed the
rulings and decisions above and recorded `ad34c02`'s landing: docs and `README.md`.
From his disk, staged in the next session: the apply was at 17:26:02 on 25 October,
the pytest cache was rewritten at 17:30:51, the commit is from 17:46:51 and
`origin/master`'s ref from 17:47:04, its reflog line "update by push"; `master` and
`origin/master` read `89d2367`. Claude had read those times off his disk after the
push, and found GitHub's tip and its four files byte for byte what was verified before
delivery, and its commit message the one delivered, line endings aside, in chat only;
Viktor listed them at the start of the next session, with the README wording approved
by his proceeding past its stop. (`b387c03` left this sentence saying the commit
message, too, was byte for byte what was verified. It was compared with its line
endings made the same and its ends trimmed: delivered CRLF, it is stored LF, as
`git commit -F` stores it — on git 2.43 in the sandbox, and in `89d2367`'s and
`b387c03`'s commit objects, made on Windows. Claude's error, corrected on
26 October.) Its account is in HISTORY, in this file's version at `89d2367`, moved
there by `b387c03`.

**The session of 25 October, from 17:56**, configured for Claude Opus 5.5, opened at
`89d2367`, GitHub's tip, cloned at 18:10 and read again with `git ls-remote` at 18:54;
`master` and `origin/master` on Viktor's disk, from `.git/refs` staged off it, read
`89d2367`. Each of the four files `89d2367` changes is on his disk byte for byte an
autocrlf checkout of GitHub's tip, and their mtimes are still the apply's, 17:26:02.733
to .744. The times above were read off his disk again: those mtimes,
`.pytest_cache/v/cache/nodeids`, the commit object's date and `HEAD`'s reflog, and
`origin/master`'s reflog line "update by push". The cache's `lastfailed` is still `{}`,
last written at 13:37:30 on 26 September, so the run of 17:30:51 recorded no failure.
`89d2367` changed no test, so the cache's ids cannot show which tree that run
collected; its time, 4 minutes 49 seconds after the apply, shows it ran after it.
`run_tests.py` leaves no trace, so its count for `89d2367` rests on Viktor's silence.
The tree verified before that delivery was in the sandbox of the session before and is
not compared again here. `b387c03` landed entry 51 and recorded `89d2367`'s landing:
three test files, `README.md`'s test counts, and docs. From his disk, staged in the
next session: the apply was at 19:10:28 on 25 October, the pytest cache was rewritten
at 19:13:22 and holds the new test's id, the commit is from 19:18:19 and
`origin/master`'s ref from 19:18:30, its reflog line "update by push"; `master` and
`origin/master` read `b387c03`. Claude had read those times off his disk after the
push, and found GitHub's tip, `b387c03`, and an autocrlf checkout of its seven files
byte for byte the tree verified before delivery and the files on his disk, and its
commit message the one delivered, line endings aside, in chat only. That session's
first comparison of GitHub's files with his disk failed: it added a CR to each line of
files its `git archive` had already written with CRLF, that clone's `core.autocrlf`
being `true`; redone, they matched. The record it wrote for Viktor called the commit
message byte-identical and put that failure down to GitHub's files being CRLF; neither
is what was shown (the session of 25 October, from 19:20, below). Its account is in
HISTORY, in this file's version at `b387c03`, moved there by `9862568`.

**The session of 25 October, from 19:20, going on to 26 October**, configured for
Claude Opus 5.5, opened at `b387c03`. GitHub's tip, read with a bare clone at the
start of the session on 25 October, is `b387c03`, its parent `89d2367`; its seven
files are stored with LF, no line of them ending in CRLF, and the messages of
`b387c03` and `89d2367` hold no CR. On 26 October GitHub asked the sandbox for
credentials, and attaching the repository failed, GitHub not being linked to Claude;
so the sandbox's repository was built from Viktor's own — the three packs and 76 loose
objects of `E:\phase7_engine\.git`, his branch, remote and tag refs, staged off his
disk: 350 commits, `git fsck --connectivity-only` reporting nothing missing, checked
out at `b387c03` with `core.autocrlf` true. `master` and `origin/master` on his disk,
from `.git/refs` staged off it, read `b387c03`. Each of the seven files `b387c03`
changes is on his disk byte for byte that checkout, and their mtimes are still the
apply's, 19:10:28.505 to .521. The times above were read off his disk again on
26 October: those mtimes, `.pytest_cache/v/cache/nodeids`, the commit object's date
and `HEAD`'s reflog, and `origin/master`'s reflog line "update by push". The cache's
`lastfailed` is still `{}`, last written at 13:37:30 on 26 September, so the run of
19:13:22, 2 minutes 54 seconds after the apply, recorded no failure, and it holds
`tests/test_imports.py::test_the_suite_walks_the_files_code_hash_reads`, which only
the applied tree has. `run_tests.py` leaves no trace, so its count for `b387c03` rests
on Viktor's silence. `9862568` landed entry 54 and recorded `b387c03`'s landing: a
build script under `docs/`, one test file, `README.md`'s test counts, and docs. From
his disk, staged in the next session: the apply was at 11:08:47 on 26 October, the
pytest cache was rewritten at 11:12:15 and holds the new test's id, the commit is from
11:18:58 and `origin/master`'s ref from 11:19:48, its reflog line "update by push";
`master` and `origin/master` read `9862568`. Claude had read those times off his disk
after the push, and found GitHub's tip, `9862568` — read at 16:49, the repository
public again — an autocrlf checkout of its six files byte for byte the tree verified
before delivery and the files on his disk, GitHub's six blobs LF, and its commit
message the one delivered with its CRs removed, byte for byte, in chat only; Viktor
listed them at the start of the next session. Its account is in HISTORY, in this
file's version at `9862568`, moved there by `3d7e6cb`.

**The session of 26 October, from 16:51**, configured for Claude Opus 5.5, opened at
`9862568`. GitHub's tip, read with `git ls-remote` at 16:56:03 and again at 16:58:19
with every credential source in the sandbox switched off, is `9862568`, its parent
`b387c03`, and the sandbox cloned it at 16:56; at 18:10 GitHub asked the sandbox for
credentials again. `master` and `origin/master` on his disk, from `.git/refs` staged
off it, read `9862568`. The commit object, staged off his disk, hashes to that name
and is byte for byte GitHub's, with no CR in it. Each of the six files `9862568`
changes is on his disk byte for byte an autocrlf checkout of GitHub's tip, whose six
blobs hold no CR, and their mtimes are still the apply's, 11:08:47.570 to .585. The
times above were read off his disk again: those mtimes,
`.pytest_cache/v/cache/nodeids`, the commit object's date and `HEAD`'s and `master`'s
reflogs, and `origin/master`'s reflog line "update by push". The cache's `lastfailed`
is still `{}`, last written at 13:37:30 on 26 September, so the run of 11:12:15,
3 minutes 28 seconds after the apply, recorded no failure, and it holds
`tests/test_send_audit_round.py::test_the_package_reads_the_engine_code_hash_reads`,
which only the applied tree has. Neither delivery file is left in the repository's
root. `run_tests.py` leaves no trace, so its count for `9862568` rests on Viktor's
silence. The commit message was compared with the one delivered, and the six files
with the tree verified before delivery, by the session before, in its sandbox: the
delivered message was deleted by its step 14 and that sandbox is gone, so neither is
compared again here. `3d7e6cb` landed entry 55 and recorded `9862568`'s landing: a
build script under `docs/`, one test file, `README.md`'s test counts, and docs. From
his disk, staged in the next session: the apply was at 18:25:03 on 26 October, the
pytest cache was rewritten at 18:30:11 and holds the new test's id, the commit is from
18:44:33 and `origin/master`'s ref from 18:44:47, its reflog line "update by push";
`master` and `origin/master` read `3d7e6cb`. Claude had read those times off his disk
after the push, and found GitHub's tip, `3d7e6cb` — read at 18:56, the repository
public again — an autocrlf checkout of its six files byte for byte the tree verified
before delivery and the files on his disk, GitHub's six blobs LF, and its commit
message the one delivered with its CRs removed, byte for byte, in chat only; Viktor
listed them at the start of the next session. Its account is in HISTORY, in this
file's version at `3d7e6cb`, moved there by the commit that writes this line.

**This session (26 October, from 18:56)**, configured for Claude Opus 5.5, opened at
`3d7e6cb`. GitHub's tip, cloned by the sandbox at 18:57 and read with `git ls-remote`
at 18:58:39 with git's credential helper and prompts switched off, is `3d7e6cb`, its
parent `9862568`; whether the sandbox's network proxy adds credentials of its own was
not checked. `master` and `origin/master` on his disk, from `.git/refs` staged off it,
read `3d7e6cb`. The commit object, staged off his disk, hashes to that name and is
byte for byte GitHub's, with no CR in it, and `.git/COMMIT_EDITMSG` is byte for byte
its message. Each of the six files `3d7e6cb` changes is on his disk byte for byte an
autocrlf checkout of GitHub's tip, whose six blobs hold no CR, and their mtimes are
still the apply's, 18:25:03.677 to .687. The times above were read off his disk again:
those mtimes, `.pytest_cache/v/cache/nodeids` (18:30:11.807), the commit object's date
and `HEAD`'s reflog, the `master` ref (18:44:33.425), and `origin/master`'s ref
(18:44:47.758) and its reflog line "update by push". The cache's `lastfailed` is still
`{}`, last written at 13:37:30 on 26 September, so the run of 18:30:11, 5 minutes
8 seconds after the apply, recorded no failure, and it holds
`tests/test_send_audit_round.py::test_each_bundle_says_the_order_its_files_follow_in`,
which `9862568`'s test file does not have. Neither delivery file is left in the
repository's root: it holds no `.patch` file and no commit message file.
`run_tests.py` leaves no trace, so its count for `3d7e6cb` rests on Viktor's silence.
The commit message was compared with the one delivered, and the six files with the
tree verified before delivery, by the session before, in its sandbox: the delivered
message was deleted by its own step and that sandbox is gone, so neither is compared
again here. The commit that writes this line files Claude's decision on entry 26 and
records `3d7e6cb`'s landing.

## Ruled — in force

- **New, 26 October — Claude's, under Viktor's delegation of the same day: Goal B keeps
  a candle only once it has closed** (DECISIONS, "Decision, 26 October 2026 — Goal B
  keeps a candle only once it has closed at `t` (entry 26)"). Entry 26: at `t` a
  candle of any series is kept only when its open time plus one bar of its own
  timeframe is at or before `t` — the live engine's own rule, `_split_forming` — and
  the negative control's noise covers every candle so dropped, the daily candle still
  forming at `t` among them. Precondition 2's text is amended in place. Viktor's to
  reverse; entry 31 stays his.
- **New, 25 October — Viktor's, by agreeing to Claude's suggestions: the engine's
  indicators** (DECISIONS, "Ruling, 25 October 2026 — the engine's indicators: one
  direction source, gates for weights, and one redesign before Amazon's audit"). The
  trend-pullback hypothesis; one direction source, the EMA slope, with ADX, the
  structure regime and divergence as gates; macro a gate on LONG only; trend health
  removed; entry quality as distance from the EMA band in ATRs and HVN nearness;
  confidence and the EV line dropped for now; one redesign, after the reading of
  14 November and before Amazon's audit, with `bias_score`'s weighting and F4's fix in
  it — the multiplier removed, Amazon re-auditing it. Reverses the ruling of
  22 September on the weighting. The redesign is entry 53.
- **New, 25 October — Claude's, under Viktor's delegation of the same day: the
  held-back defects the redesign reaches** (DECISIONS, "Decision, 25 October 2026 — the
  held-back defects the redesign reaches are replaced or judged again, not protected").
  The redesign is designed on its merits; H1 is replaced, H2 kept only if the design
  keeps its parameter for its own reasons, H5 judged again once entry quality's weights
  are set, H3 kept. Replacements are chosen when the design is fixed, before its code is
  built; Claude proposes them and Viktor accepts or rejects.
- **New, 25 October — Claude's, under Viktor's delegation of the same day: the trend
  multiplier is Critical** (DECISIONS, "Decision, 25 October 2026 — the trend multiplier
  is Critical, by F4's precedent"). Entry 52: the same shape as F4's third path. Removed
  by the redesign and re-audited by Amazon. Two Criticals are open; the release gate
  reopens when both fixes have landed and been re-audited.
- **New, 20 October — Viktor's, by agreeing to Claude's suggestion: F4's third path is
  Critical** (DECISIONS, "Ruling, 20 October 2026 — F4's third path is Critical: macro
  moving the tier breaks Item 11, and the release gate closes"). Macro's ×1.05 / ×0.90
  on the entry score can move a setup between LONG and CONSERVATIVE LONG; that breaks
  Tier 1 Item 11 and reaches live decisions. The release gate is closed until its fix
  has landed and been re-audited; goal A stands and `portfolio-v1` stays. The fix lands
  after the reading of 14 November and before the send, with a live run before its
  commit. Its shape and who re-audits it were ruled on 25 October: the multiplier
  removed, in the redesign (entry 53), and Amazon re-audits it within its audit.
- **New, 20 October — Viktor's, by agreeing to Claude's suggestion: Claude builds the
  list for after the audit** (DECISIONS, "Ruling, 20 October 2026 — Claude builds the
  list for after the audit; Fable 5.1 waits until after the audit"). Entry 38. Fable
  5.1 waits until after Amazon's audit; the question is asked again at entry 10, the
  range-trading mode.
- **New, 20 October — Viktor's, by agreeing to Claude's suggestion: B5, 4h only for
  now** (DECISIONS, "Ruling, 20 October 2026 — B5: 4h only for now, and a guard refuses
  any other timeframe"). Entry 22. No timeframe but 4h is used until it has its own
  thresholds, ruled with evidence; a guard that refuses any other lands in wave 2.
- **New, 19 October — Viktor's, by agreeing to Claude's suggestion: the list for after
  the audit, sorted** (DECISIONS, "Ruling, 19 October 2026 — the list for after the
  audit, sorted: kind, who decides, size and order"). Each of the forty open entries
  has a kind, who decides it, a rough size and a place in the order: wave 0, the
  rulings that steer the rest; 1, what moves no `code_hash`; 2, code that changes no
  decision; 3, the renames; 4, the trading rules; 5, the range mode. No commit that
  moves `code_hash` lands before the forward measurement's reading of 14 November.
  Entry 1, S1, is worked after the audit with the four. Claude's reading of his words,
  his to correct, is in the entry.
- **New, 18 October — Viktor's: the four held-back defects are H1, H2, H3 and H5**
  (DECISIONS, "Ruling, 18 October 2026 — the four held-back defects: H1, H2, H3 and
  H5"). H1 and H2 accepted as Claude proposed them; H3 kept, by agreeing to Claude's
  suggestion; H5, found by a search he agreed to, in H4's place. Each has its "found
  means" sentence there. Work on the list leaves them as they are, Claude re-checks
  them at the tag before the send, and they are fixed after the audit. Where the
  redesign of 25 October reaches them, the decision of that day applies (above).
- **New, 17 October — Viktor's, by agreeing to Claude's suggestion: if Amazon fails the
  check twice** (DECISIONS, "Ruling, 17 October 2026 — if Amazon fails the check twice:
  a scoped round on Items 2, 3, 6 and 18, then a wait for a clean lab"). A scoped round
  on Items 2, 3, 6 and 18 by a lab clean for scoped rounds — Upstage, NVIDIA, Cohere or
  AI21 — scored on the same four held-back defects, its ratings counting on the same
  four conditions; if it fails too, backtesting stays closed until a lab that has never
  seen the project is available. The four now also sit in the files that scoped
  package would carry.
- **New, 17 October — Viktor's: Amazon's audit is scored on four defects held back from
  the list, and its ratings are the ones that count** (DECISIONS, "Ruling, 17 October
  2026 — Amazon's audit …"). Question 3 of 6 October by his position first ("Yes"),
  then Claude's critique, whose suggestions he agreed to; question 2 by agreeing to
  Claude's suggestion. Four known minor defects, outside Items 2, 3, 6 and 18 and not
  pointed at by the code's comments, are chosen before work on the list starts, left in
  for the audit and fixed after it; their "found means" sentences are committed before
  the send. Amazon's ratings count toward opening backtesting if the check passes, the
  provider's record shows the pinned model, the run finishes normally and Viktor checks
  the score; round 8's verified fixes do not count through condition 1's second path.
  What follows if it fails the check twice: the entry above.
- **New, 17 October — Claude's, under point 5 of the forward measurement's ruling: how
  it is counted** (DECISIONS, "Decision, 17 October 2026 — how the forward measurement
  is counted"). From the task's first run; the task's record is the one decision per
  pair per candle per version; refusals, failures and missed candles counted apart,
  failures from `main.py`'s line for each pair. Set before any reading; Viktor's to
  change.
- **New, 17 October — Viktor's, by agreeing to Claude's suggestion: the forward
  measurement** (DECISIONS, "Ruling, 17 October 2026 — the forward measurement: ten
  pairs every four hours, and main.py takes them"). The engine runs every four hours on
  ten pairs, logging only, started by one Windows scheduled task on his machine;
  `main.py` takes the pairs and works from its own folder, landed at `0491b84`. Claude
  counts at two and at four weeks. It changes no decision and is not the paper-trading
  year. Missing from this list in the version at `0491b84`, which filed the ruling.
- **New, 17 October — Viktor's, by agreeing to Claude's suggestion: round 8's fix
  verification accepted on the stop's answer; the release gate reopens** (DECISIONS,
  same title). Accepted on A.1 alone — the stop's fix holds — as point 2 of the triage
  asked; A.2 recorded, not relied on, since it names eight of the seventeen changes.
  Sections B–F go to his triage, as the instruction told the auditor, and are triaged:
  noted, no action; B's *fixed* is recorded as confirmed in one run, counting toward
  nothing until he rules what makes a round-8 rating count. No second run, and no other
  auditor now. The next full audit names the stop's fix as its own question and checks
  the seven fixes in B for new defects. Backtesting stays closed.
- **New, 16 October — Claude's, under the delegation of 4 October: round 8's fix
  verification** (DECISIONS, "Decision, 16 October 2026 — round 8's fix verification:
  what is checked, what is sent, and to whom"). MiMo-V2.6-Pro checks the fix of the
  Critical (point 1, the stop) and of its own F1, F2, F3, F5, F6, F8, F9 and Part 4's
  three test shapes, and checks every other change to code it read for new defects.
  F4, F7, F10, Part 4's other named tests and the Part 7 reply's §1(3) and §1(5) are
  declared not fixed. One request and one run (the cap of two in all, 30 September,
  still holds), Xiaomi's endpoint pinned, the commit sent from tagged first. Viktor's
  to reverse.
- **15 October — Viktor's, by agreeing to Claude's suggestions: Part 4's three
  test shapes** (DECISIONS, "Ruling, 15 October 2026 — Part 4's three test shapes").
  With no baseline, the golden coverage test fails, as the snapshot comparison does,
  and it runs without `pandas_ta`. The non-finite test renders the golden decision with
  each float field set to +inf, -inf and NaN, one at a time, after checking that the
  plan prints. The SuperTrend level test runs the guard with the level blanked at the
  decision bar and asserts that SuperTrend fails whole: neither column is written. The
  watched error count is written as a number only in this file; `run_tests.py`
  counting fixture-taking tests apart goes on the list for after the audit. **Landed at
  `f00bef6`.**
- **15 October — Viktor's, by agreeing to Claude's suggestions: B10, two outputs
  agree with finding 4 and the action** (DECISIONS, "Ruling, 15 October 2026 — B10: two
  outputs agree with finding 4 and the action"). The simulated order's `entry_zone` is
  `ema_band`, the panel's label for the band, with the same values; the order's entry
  stays `current_price`, the decision log's name for the decision close, so no field is
  added or copied. The panel prints the Exit Watch note naming Target 1 only on a run
  whose action names a side — not on a WAIT, any NO-TRADE or an absent action; panel
  only, as for finding 5: the decision object and the log keep the note, and under a
  leaning bias the plan still prints. B10 came first, as ordered on 13 October; the
  three test shapes follow as one patch. **Landed at `9ea1cf3`.**
- **15 October — Viktor's, by agreeing to Claude's suggestions: B9, Bitcoin's
  SuperTrend read directly** (DECISIONS, "Ruling, 15 October 2026 — B9: Bitcoin's
  SuperTrend is read directly"). Two calls. Bitcoin's SuperTrend direction is read by
  subscript, the 13 October shape, where a missing column read 0.0: a failed BTC
  SuperTrend makes the BTC section unavailable for the run, where the panel printed a
  BTC BIAS one factor short and the failure reached only the log. The asset's own read
  keeps its 0.0 — there a failure is a recorded degradation and authorizes no trade —
  and waits for after the audit (Found after 22 September). B9's router default and
  three of its BTC defaults had landed with the fallback sweep at `797bdc9`, which did
  not name B9. **Landed at `64ad625`.**
- **15 October — Viktor's, by agreeing to Claude's suggestion: B7, the distance
  limits record the regime** (DECISIONS, "Ruling, 15 October 2026 — B7: the distance
  limits record the regime"). Option A of two: `validate_risk_parameters` classifies
  the regime before the 15% limit and the 0.2% floor, and both return it where they
  returned UNKNOWN; their messages and their precedence are unchanged, so every verdict
  and every reason is what it was. The 15% limit stays, as the ruling of 27 September
  kept it — a check that cannot change a verdict while the 8% is below it, kept as a
  backstop. The 0.2% floor is in scope: Claude found it has the same shape. UNKNOWN is
  returned only where no regime can be computed. **Landed at `d77a8c4`.**
- **14 October — Viktor's, by agreeing to Claude's suggestion: B4's labels, their
  shape** (DECISIONS, "Ruling, 14 October 2026 — B4's labels: their shape"). Option B
  of three: the Exit Watch flag, the confirmation gate's blocker and the confirmation
  reason say "price/RSI disagreement over four candles", which is what
  `indicators/trend_health.py` compares; the volume label VOLUME DIVERGENCE is FADING
  VOLUME; `core/engine_core.py` matches FADING VOLUME and VOLUME EXHAUSTION whole, each
  with a note of its own, where it matched part of a word (and a WEAK no label
  contains). Every score unchanged. The keys `momentum_divergence` and
  `divergence_direction` keep their names; the rename is on the list for after the
  audit. Whether the divergence should veto is still Viktor's, not ruled. The wording
  is Claude's, Viktor's to reverse. **Landed at `22a9a35`.**
- **13 October — Viktor's, by agreeing to Claude's suggestions: the fallback
  sweep — the 12 October additions' shape, scope and order** (DECISIONS, "Ruling,
  13 October 2026 — the fallback sweep: the 12 October additions' shape, scope and
  order"). The three fallbacks found filing the 12 October ruling join, with STATUS's
  twin in the router. A value only printed or recorded falls back to the router's own
  value for an absent one; a value the engine computes with, and a router value whose
  type has no UNKNOWN, is read directly. `reversal_strength` at `engine_core`'s two
  bias calls is in. Patch 1 is the sweep of every default in the panel and the router's
  decision-building code — **landed at `797bdc9`**; patch 2 takes the REGIME line and
  the STRUCTURE line's Vol field out — **landed at `69c92d6`**;
  then B4's labels — **landed at `22a9a35`**. What
  the patch read into the rule (numbers to NaN; the Bitcoin block unavailable rather
  than an error; the exit watch "not computed") is Claude's, Viktor's to reverse.
- **12 October — Viktor's: the panel's fallback readings and two repeated
  readings join the label and record batch** (DECISIONS, "Ruling, 12 October 2026 —
  the panel's fallback readings and two repeated readings join the label and record
  batch"). The eleven fallbacks listed under "Found after 22 September" at `e5ac20a`,
  REGIME printed beside STRUCTURE with the same value, and `bias.volatility` printed
  on both the Vol field and the VOLATILITY line. Filed at `ef65f46`; the shape and
  order were ruled on 13 October (the entry above).
- **12 October — Viktor's, by agreeing to Claude's suggestion: F9's shape and
  scope** (DECISIONS, "Ruling, 12 October 2026 — F9's shape and scope"). F9(1) is
  option C, as for finding 18: the structure regime is a plain function of the frame,
  with the same output on the engine's path; `REGIME_HYSTERESIS_THRESHOLD` keeps its
  name and its comment says it is a dead band — the rename waits for after the audit.
  In scope with F9's four: `trend_direction`'s failure label, and `_detect_regime`'s
  answer to a frame too short to read (UNKNOWN STRUCTURE). The panel's TREND-line
  fallbacks were in scope if they could not fire; they cannot (Work order, item 4,
  F9). Landed at `e5ac20a`.
- **New, 5 October — Viktor's, by agreeing to Claude's suggestion: round 8's triage**
  (DECISIONS, "Ruling, 5 October 2026 — round 8 triaged: three decision-path fixes and
  the label and record fixes now, the release gate closed, the freeze lifted"). Ruled
  on the night of 4 to 5 October; filed from the resume note. (1) The stop is ATR × 1.2
  × the volatility factor: trend health and the bias score no longer scale it — a
  break of Item 14, confirmed by Viktor on 5 October. (2) The release gate is closed
  until (1) has landed and round 8's auditor has verified it. (3) The risk regime
  comes from volatility alone. (4) ADX under 20 blocks both sides, replacing the
  exhaustion flag in the confirmation gate. (5) The trend score's scale waits for
  after the audit, decided before paper trading. (6) Test runs get their own log,
  archive and state; the test records in the live log are named. (7) The
  BTC-adjusted confidence line is removed. (8) The label and record fixes are made
  now. (9) F4 stays on the list. (10) The score check is declined. (11) The freeze
  lifts. Filed at `eb86846`. **(1) landed at `c2b07fb`, (4) at `1b25f36`, (3) at
  `fcb7823`, (6) at `9e507b1`, and (7) at `6469a67`; of (8), F3 at `ae37795`, F5
  at `9d00d99`, F6 at `27d3ed5`, F8 at `9051ffd`, F9 at `e5ac20a`, the fallback
  sweep the 12 October ruling added to it at `797bdc9`, its two repeated readings
  at `69c92d6`, B4's labels at `22a9a35`, B7 at `d77a8c4`, B9 at `64ad625`, B10 at
  `9ea1cf3`, and Part 4's three test shapes at `f00bef6`**; the fix verification
  (Work order, item 5) followed: decided at `36de35d`, its tooling landed at
  `78ea37d`, its report filed at `d3188f2`, and accepted by Viktor on 17 October
  (above). Point 4
  left to the patch how an ADX with no valid reading is treated: it blocks both sides
  too (Work order, item 2). Point 3 left to it how LOW VOLATILITY maps without the
  strong-trend test: LOW RISK, the reading the ruling named as Claude's; and the patch
  makes a volatility state the regime does not know UNKNOWN RISK, where it was NORMAL
  RISK (Work order, item 3). Point 6 left to it where the records go and how a run's
  source is read: `logs/pinned/`, the log chosen from each record's own provenance, a
  record that does not say it is live kept out of the live log, and a broken pinned
  request counted as not live (Work order, item 4). Point 7 left to it whether the
  computation and its record field go with the line: they do, with the two constants
  that bounded it, `evaluate()`'s two parameters that only it read, and the BTC bias
  score engine_core handed over only for it (Work order, item 4). All are Claude's
  proposals, Viktor's to reverse.
- **New, 5 October — two of rev 9's requirement sentences corrected** (DECISIONS,
  "Correction, 5 October 2026 — two of rev 9's requirement sentences were wrong"), by
  point 9. Rev 9 itself is not edited.
- **New, 5 October — Claude's, under the delegation of the order of work: the fixes'
  order** — the stop, the trend gate, then the regime (the triage's entry, "The order
  of the work"). The resume note had the regime before the trend gate; swapped so
  that no commit leaves AGGRESSIVE open in a low-ADX market.
- **New, 4 October — Viktor's, by agreeing to Claude's suggestion: round 8's result**
  (DECISIONS, "Ruling, 4 October 2026 — round 8's result: the findings go to triage,
  the ratings do not count, backtesting stays closed"). Run 2's findings and Part 7
  points go to triage; its ratings do not count toward opening backtesting; backtesting
  stays closed. Ruled without reading the report; the two scores are unchecked by him.
  It narrows the entry below, which said run 2's ratings count. **Filed at
  `9e42d30`.**
- **New, 4 October — Claude's, under the delegation: round 8's second run** (DECISIONS,
  "Decision, 4 October 2026 — round 8's second run: 2 of 4, a pass; Part 7 to it").
  Scored 2 of 4 (S2, S4), a pass, so its ratings count — narrowed by the ruling above:
  not toward opening backtesting; Part 7 goes to it. **Filed at
  `a0276dd`**, with the run's four files. Part 7 was sent and answered; the record is
  DECISIONS, "Round 8, 4 October 2026 — Part 7 answered; the result goes to Viktor",
  filed at `040a529`.
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
- **New, 4 October — Claude's, under the delegation:** round 8 to Xiaomi MiMo-V2.6-Pro,
  the full package in one session, if four checks pass, pinned to Xiaomi with GMICloud,
  DeepInfra and Novita after it, two runs in all; the package from the tag with only rev
  9 and the Part 7 document corrected; the freeze holds (lifted 5 October),
  `tests/test_package_token_check.py` joining the exception; scoped packages to Upstage,
  NVIDIA, Cohere and AI21 as the fallback (DECISIONS, the three entries "Decision, 4
  October 2026 — …"). No code yet.
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
- **Reversed on 25 October — `bias_score`'s weighting waits for after the audit, and
  the auditor sees it** (DECISIONS, 22 September; filed at `75682ee`) — in Part 7
  (ruling of 29 September). It joins the redesign before Amazon's audit (above).
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
  Claude's decision on entry 26 of the list for after the audit filed, docs only, and
  `3d7e6cb`'s landing recorded. Before it: `3d7e6cb` (the session of 26 October, from
  16:51: entry 55 of the list for after the audit, audit tooling and a test, and
  `9862568`'s landing recorded), `9862568` (the session of 25 October, from 19:20, going
  on to 26 October: entry 54 of the list for after the audit, audit tooling and a test,
  and `b387c03`'s landing recorded), `b387c03` (the session of 25 October, from 17:56: entry
  51 of the list for after the audit, tests only, and `89d2367`'s landing recorded),
  `89d2367` (the session of 25 October, from 15:20: Viktor's eight
  rulings of 25 October and Claude's two decisions under his delegation filed, and
  `ad34c02`'s landing recorded: docs and `README.md`), `ad34c02`
  (the session of 24 October, from 20:16: entry 49 of the list for after the audit,
  tests only, and `34d8e3b`'s landing recorded), `34d8e3b` (the session of 20 October,
  from 17:49, going on to
  24 October, its fourth commit: `d410bfa`'s landing and its test steps run after its
  commit recorded, and GitHub's tip for `9f2f3d7`: docs only), `d410bfa` (its third
  commit: the overlap and decision-impact tool, `docs/build/indicator_overlap.py`, with
  its tests and docs), `9f2f3d7` (its second commit: `d508b29`'s landing,
  the forward measurement's runs of 20 and 21 October and the document of 24 October
  recorded: docs only), `d508b29` (its first commit: entry 37 of the list for after the
  audit, tests only, and `e88e0dd`'s
  landing recorded), `e88e0dd` (the session of 20 October, from 11:13, its second
  commit: entry 36, one test only, and `ed005a0`'s landing recorded), `ed005a0` (its
  first commit: entry 48, one test only, and `8360923`'s landing recorded), `8360923`
  (the session of 20 October, from
  09:18: entries 13, 21
  and 28 of the list for after the audit, comments and docstrings only, and `391c338`'s
  landing recorded), `391c338` (the session of 19 October,
  from 18:16, going on into 20 October: Viktor's three rulings of 20 October filed, and
  the 14:00 reading of 19 October and `aa9e7ac`'s landing recorded: docs and
  `README.md`), `aa9e7ac` (the
  session of 19 October, from 10:19: Viktor's ruling on the sort of the list for after
  the audit filed: docs only), `d2dddf7` (the session of 19 October, from
  09:08: the forward measurement's line on the 14:00 close of 18 October corrected:
  docs only), `8311167` (the session of 17 October, from 18:43, going on
  into 18 October, its second commit: Viktor's ruling on the four held-back defects
  filed: docs only), `fbd7877` (its first commit: the scheduled task's second run
  filed; nothing ran at 18:00: docs only), `a48d9e5` (the session of 17 October, from
  14:10, its third commit: Viktor's ruling
  on what follows if Amazon fails the check twice filed: docs only), `8d5d64a` (its
  second commit: Viktor's rulings on two of the
  questions of 6 October filed: docs only), `a235783` (its first commit:
  README's three status rows brought current
  and the forward measurement's first checks filed: docs only), `0491b84` (the session
  of 17 October, from 10:34: the
  forward measurement: `main.py` takes the pairs and works from its own folder: engine
  code, a new test file and docs), `67f6ec1` (the session of 17 October, from 09:24:
  Viktor's ruling on round 8's fix verification report filed: docs only), `d3188f2` (the
  session of 16 October, 05:44, to 17 October: the report filed: the
  run's four files and docs), `78ea37d` (the same session: the fix verification's
  tooling: a new script under `docs/build/`, a new instruction under
  `docs/audit_package/`, a new test file and docs), `36de35d` (the session of 16 October, 04:27: round 8's fix verification decided:
  docs only), `f00bef6` (the session of
  15 October, from 13:33: Part 4's three test shapes: tests, `run_tests.py`'s docstring
  and docs), `9ea1cf3` (the session of 15 October, from 10:32: B10: engine code, two tests, a new
  test file and docs), `64ad625` (the session
  of 15 October, from 03:55: B9: engine code, a new test file and docs), `d77a8c4` (the
  session of 14 October, night, to 15 October, night: B7: engine code, two tests, a new
  test file and docs), `22a9a35` (the session of 14 October: B4's labels: engine code, three
  tests, the golden fixture, a new test file and docs), `69c92d6` (the session of
  13 October, night: the two repeated readings,
  patch 2 of the 12 October additions: the panel, a test, a new test file and docs),
  `797bdc9` (the session of 12 October, evening, to
  13 October, night: the fallback sweep, patch 1: engine code, tests, a new test file
  and docs), `ef65f46` (the session of 12 October, morning: Viktor's
  ruling of 08:24 filed: docs only), `e5ac20a` (the session of 11 October, near midnight, to 12 October,
  early morning: F9, four claims the code beside them did not support: engine code, a
  new test file and docs), `9051ffd` (the session of 11 October, late evening: F8, one name for one
  meaning: engine code, a new test file and docs), `27d3ed5` (the session of
  11 October, evening: F6, `clean_series` accepts only methods that read no later row:
  engine code, a new test file and docs), `9d00d99` (the session of 10 October, evening: F5, the band
  distance labelled from the band's midpoint: engine code, tests and docs), `ae37795` (the session of 10 October,
  afternoon: F3, a frame with no readable time axis rejected: engine code, a new test
  file and docs), `6469a67` (the session of 9 October: N5, Bitcoin reference only: engine code,
  tests, the golden fixture and docs), `9e507b1` (the session of 6 October, later the same evening: B6, runs on pinned data
  keeping records of their own: engine code, tests, the golden fixture, the
  audit-package builder and docs), `fcb7823` (the session of 6 October,
  early evening: fix 3, the regime: engine code, tests, the golden fixture and docs),
  `1b25f36` (the session of the night of 5 to 6 October: fix 2,
  the trend gate: engine code, tests, the golden fixture and docs), `c2b07fb` (the
  session of 5 October, evening: fix 1, the
  stop: engine code, tests, the golden fixture and docs), `eb86846` (the session of
  5 October that filed round 8's triage: docs only), `9e42d30` (the sixth session of
  4 October: Viktor's ruling on round 8's result: docs only), `040a529` (the fifth
  session of 4 October's third commit: round 8's Part 7 reply and its record: docs
  only), `a0276dd` (its second commit: round 8's second run: docs only), `d27743f` (its
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
  `d27743f`; `round8-verify-sent-2026-10-17` at `78ea37d`, the commit round 8's fix
  verification was sent from, made on Viktor's machine and pushed before the send.
  **Release gate: closed since 20 October** (DECISIONS, "Ruling, 20 October 2026 —
  F4's third path is Critical …"), until that Critical's fix and the trend
  multiplier's, rated Critical on 25 October (DECISIONS, "Decision, 25 October 2026 —
  the trend multiplier is Critical …"), have landed and been re-audited. Declared open
  on 15 September; closed from 5 October ("Ruling, 5 October
  2026 — round 8 triaged …", point 2) until Viktor accepted the report of round 8's
  auditor, which verified the fix of the stop that landed at `c2b07fb`, on 17 October
  ("Ruling, 17 October 2026 — round 8's fix verification accepted on the stop's answer;
  the release gate reopens"); open from then to 20 October.
- **The freeze is lifted** (point 11 of the same ruling): round 8's report is triaged, so
  commits may touch engine code and tests again. It held from 29 September (DECISIONS,
  "Ruling, 29 September 2026 — six questions before the send", point 1) to 5 October,
  with two exceptions for the tests of the sending tools. `tests/` on `master` differs from the tag
  `round8-sent-2026-10-04` in `tests/test_send_audit_round.py` (`d27743f`), in the six
  test files and the golden fixture `c2b07fb` changes or adds, in
  `tests/test_signal_confirms.py`, the new `tests/test_no_trend_no_trade.py` and the
  golden fixture again (`1b25f36`), in
  `tests/test_no_circular_reasoning.py`, `tests/test_no_risk_free_conviction.py`,
  `tests/test_risk_fingerprint.py`, `tests/test_risk_regime_independence.py`,
  `tests/test_stop_ignores_conviction.py` and `tests/test_stop_is_atr_only.py`, the new
  `tests/test_regime_from_volatility_alone.py` and the golden fixture again
  (`fcb7823`), in
  `tests/test_code_fingerprint.py`, `tests/test_decision_log_record_format.py`,
  `tests/test_engine_state_atomic_write.py`, `tests/test_golden_path.py`,
  `tests/test_lineage.py`, `tests/test_router_btc_seam.py` and
  `tests/test_traceability.py`, the new `tests/test_pinned_runs_keep_their_own_records.py`
  and the golden fixture again (`9e507b1`), in `tests/test_btc_correlation_alignment.py`,
  `tests/test_btc_degradation_stays_informational.py`, `tests/test_code_fingerprint.py`,
  `tests/test_decision_contract.py`, `tests/test_fingerprint_names_every_constant.py`,
  `tests/test_golden_path.py`, `tests/test_panel_prints_only_what_was_computed.py`,
  `tests/test_router_btc_seam.py` and `tests/test_traceability.py`, the new
  `tests/test_btc_is_reference_only.py` and the golden fixture again (`6469a67`), in
  the new `tests/test_untimed_frame_is_rejected.py` (`ae37795`), in
  `tests/test_entry_zone_is_measured.py`,
  `tests/test_plan_entry_is_the_decision_close.py` and the new
  `tests/test_band_distance_is_from_the_midpoint.py` (`9d00d99`), in the new
  `tests/test_clean_series_methods.py` (`27d3ed5`), in the new
  `tests/test_one_name_one_meaning.py` (`9051ffd`), in the new
  `tests/test_round8_f9_claims_match_the_code.py` (`e5ac20a`), and in
  `tests/test_direction_source.py`, `tests/test_macro_counts_once.py`,
  `tests/test_risk_verdict_is_read_not_assumed.py`,
  `tests/test_router_no_fabricated_zero_defaults.py`, `tests/test_signal_confirms.py`,
  `tests/test_swing_structure_is_not_invented.py` and the new
  `tests/test_an_absent_value_is_not_a_reading.py` (`797bdc9`). The panel's lines are
  read again in the new `tests/test_each_reading_is_printed_once.py` (`69c92d6`).
  `22a9a35` changed `tests/test_no_trend_no_trade.py`, `tests/test_signal_confirms.py`,
  `tests/test_volume_agreement.py` and the golden fixture, and added
  `tests/test_b4_labels_say_what_is_measured.py`. `d77a8c4` changed
  `tests/test_regime_from_volatility_alone.py` and `tests/test_stop_is_atr_only.py`,
  and added `tests/test_b7_distance_limits_record_the_regime.py`. `64ad625` added
  `tests/test_b9_btc_supertrend_is_read_directly.py`. `9ea1cf3` changed
  `tests/test_neutral_bias_prints_no_plan.py` and
  `tests/test_no_fabricated_defaults_remain.py`, and added
  `tests/test_b10_outputs_agree_with_finding_4_and_the_action.py`. `f00bef6`
  changed `tests/test_golden_path.py`,
  `tests/test_decision_bar_integrity.py`,
  `tests/test_docs_build_writes_into_the_repository.py`,
  `tests/test_code_fingerprint.py` and `tests/test_summary_names_the_action_reason.py`,
  and `run_tests.py`'s docstring. `36de35d` changed no test. `78ea37d` added
  `tests/test_send_round8_fix_verification.py` (25 tests, no fixtures) and changed no
  other test. `d3188f2` and `67f6ec1` changed no test. `0491b84` added
  `tests/test_main_takes_pairs.py` (9 tests, no fixtures) and changed no other test.
  `a235783`, `8d5d64a`, `a48d9e5`, `fbd7877`, `8311167`, `d2dddf7`, `aa9e7ac` and
  `391c338` change no test. `8360923` changed comments and docstrings in
  `tests/test_frame_ownership.py`, `tests/test_run_tests_filter_matching.py`,
  `tests/test_smoke.py`, `tests/test_timeframe_disagreement.py` and
  `tests/test_trend_direction_source.py`, and no test's code. `ed005a0` changed one
  test, `test_the_location_check_can_fail` in
  `tests/test_send_round8_fix_verification.py`, and added, removed and renamed none.
  `e88e0dd` changed one test, `test_the_panel_never_prints_a_non_finite_number` in
  `tests/test_decision_bar_integrity.py`, and added, removed and renamed none.
  `d508b29` changed `tests/test_execution_surface.py`,
  `tests/test_no_circular_reasoning.py`, `tests/test_no_fabricated_defaults_remain.py`,
  `tests/test_panel_prints_only_what_was_computed.py`,
  `tests/test_risk_verdict_is_read_not_assumed.py` and
  `tests/test_swing_structure_is_not_invented.py`: it adds ten tests, makes the three
  parametrized cases of one test a single test, and renamed none. `9f2f3d7` changed no
  test. `d410bfa` added `tests/test_indicator_overlap_tool.py` (13 tests, none taking
  a fixture, two needing `pandas_ta`) and changed no other test. `34d8e3b` changed no
  test. `ad34c02` added one test to `tests/test_imports.py`,
  `test_engine_modules_is_every_module_in_the_tree` (no fixture, no `pandas_ta`), and
  changed what `test_every_module_imports` imports, through `tests/conftest.py`'s
  `ENGINE_MODULES`, with a dated paragraph in its docstring and a count taken out of
  one of its comments; it removed and renamed none. `89d2367` changed no test.
  `b387c03` added one test to `tests/test_imports.py`,
  `test_the_suite_walks_the_files_code_hash_reads` (no fixture, no `pandas_ta`); made
  the list of directories `tests/conftest.py`'s `all_python_files` skips `code_hash`'s,
  for every test that walks the tree through it, which read the same files; and
  changed `test_no_engine_module_calls_utcnow` in
  `tests/test_no_fabricated_defaults_remain.py`, which walks the tree through it now,
  with a dated paragraph in its docstring. It removed and renamed none. `9862568`
  added one test to `tests/test_send_audit_round.py`,
  `test_the_package_reads_the_engine_code_hash_reads` (no fixture, no `pandas_ta`),
  with a dated paragraph in that file's docstring, and changed no other test's code:
  `test_every_file_the_build_writes_is_one_the_send_sends` builds with the new walk,
  and the names it checks are the same. It removed and renamed none. `3d7e6cb` added
  one test to `tests/test_send_audit_round.py`,
  `test_each_bundle_says_the_order_its_files_follow_in` (no fixture, no `pandas_ta`),
  with a dated paragraph in that file's docstring, and changed no other test's code:
  `test_every_file_the_build_writes_is_one_the_send_sends` builds with the new header,
  and the names it checks are the same. It removed and renamed none. The commit that
  writes this line changes no test.
- **Where the project lives, from 26 September:** `E:\phase7_engine` on Viktor's machine;
  the files kept outside the repository in `G:\Phase_7_Engine_Random_Files`. Copied with
  robocopy, verified — git's own checks on Windows for the tracked files, SHA-256 for the
  91 ignored data files and the 25 Random Files — and only then the originals renamed.
  The evidence is in HISTORY, "26 September 2026 (ninth session) — the repository moved
  to `E:\phase7_engine`". Run the engine and every command from `E:\phase7_engine` (in
  cmd, changing drive needs `cd /d`). A dated record that names the D: paths means the
  same folders before the move; dated records are not edited.
- **The push of `3d7e6cb`** happened, at 18:44:47 on 26 October: GitHub's tip, read
  at 18:57 and 18:58 in the next session, is `3d7e6cb`, `master` and `origin/master`
  on Viktor's disk read it (their `.git/refs` files, and `origin/master`'s reflog line
  "update by push"), and its six files on his disk are byte for byte an autocrlf
  checkout of it. An autocrlf checkout of GitHub's six files was read byte for byte
  what was verified before delivery, and its commit message the one delivered with its
  CRs removed, byte for byte, after the push, in the session that delivered it. No
  deviation was reported (ruling on proposal (b)). So did `9862568`'s, at 11:19:48 on
  26 October, GitHub's tip read at 16:49 that day and at 16:56 and 16:58, its six files
  on his disk byte for byte an autocrlf checkout of it, and an autocrlf checkout of
  GitHub's six files read byte for byte what was verified before delivery and its
  commit message the one delivered with its CRs removed,
  `b387c03`'s, at 19:18:30 on 25 October, GitHub's tip read that evening, its seven
  files on his disk byte for byte an autocrlf checkout of it, and an autocrlf checkout
  of GitHub's seven files read byte for byte what was verified before delivery and its
  commit message the one delivered, line endings aside, `89d2367`'s, at 17:47:04 on
  25 October, GitHub's tip read at 18:10 and
  18:54 that day, its four files on his disk byte for byte an autocrlf checkout of it,
  and GitHub's four files read byte for byte what was verified before delivery and its
  commit message the one delivered, line endings aside (`b387c03` wrote "byte for
  byte" of the commit message too; corrected on 26 October, "Where the project is"),
  `ad34c02`'s, at 21:51:00 on 24 October,
  GitHub's tip read on 25 October and its six files on his disk byte for byte an
  autocrlf checkout of it, `34d8e3b`'s, at
  20:14:34 on 24 October, GitHub's tip fetched and its tree byte for byte the one
  verified before delivery, `d410bfa`'s, at 19:40:22 on 24 October, GitHub's tip
  fetched and its tree byte for byte the one verified before delivery, `9f2f3d7`'s, at
  18:54:48 on 24 October,
  GitHub's tip fetched later that evening, once the repository was public again, and its
  tree byte-identical to the one verified before delivery, `d508b29`'s, at 08:36:58 on
  21 October,
  GitHub's tip fetched and its ten files byte-identical to the tree verified before
  delivery, `e88e0dd`'s, at 14:23:19
  on 20 October, its three files on his disk byte-identical to an autocrlf checkout of
  GitHub's tip, `ed005a0`'s, at
  11:53:40 on 20 October, its four files on his disk byte-identical to an autocrlf
  checkout of GitHub's tip, `8360923`'s, at
  11:03:39 on 20 October, its eleven files on his disk byte-identical to an autocrlf
  checkout of GitHub's tip, `391c338`'s, at 09:13:25 on 20 October, `aa9e7ac`'s, at 11:55:23 on 19 October,
  `d2dddf7`'s, at 09:59:56 on 19 October,
  `8311167`'s, at 08:49:11 on 19 October,
  `fbd7877`'s, at 05:36:43 on 18 October, `a48d9e5`'s, at 18:29:01 on 17 October,
  `8d5d64a`'s, `a235783`'s and `0491b84`'s.
  The same holds for the push of the
  commit that writes this line unless it deviates. Earlier pushes and deviations are
  recorded in this file's previous versions, in HISTORY.
- **Before this commit**, every file its patch changes was staged off Viktor's disk and
  matched an autocrlf checkout of `3d7e6cb`, GitHub's tip, cloned at 18:57 on
  26 October, byte for byte.
- **code_hash:** `816d4951bb0322763ec4abc4b9ed8161d5b902372823350e5272f2fb7176e380`,
  set by `0491b84` from `bc1b9c2c…` — `main.py` alone — and confirmed on Windows: its
  eleven hand-run records and the ten of each of the first two scheduled runs carry it.
  Unchanged by `a235783`, `8d5d64a`, `a48d9e5`, `fbd7877`, `8311167`, `d2dddf7`,
  `aa9e7ac` and `391c338`, which change no `.py` file, by `8360923`, which changed
  comments and docstrings only — in `core/engine_core.py`, `models/risk_model.py` and
  `run_tests.py`, which the fingerprint reads with both stripped, and in `tests/`, which
  it does not read — by `ed005a0`, `e88e0dd` and `d508b29`, each of which changed
  files under `tests/` and `docs/`, which it does not read, the last also `README.md`,
  which is not a `.py` file, by `9f2f3d7`, which changed one file under `docs/`, by
  `d410bfa`, which added files under `docs/` and `tests/` and changed `README.md`, by
  `34d8e3b`, which changed one file under `docs/`, by `ad34c02`, which changed files
  under `docs/` and `tests/`, which it does not read, and `README.md`, which is not a
  `.py` file, by `89d2367`, which changed files under `docs/` and `README.md`, by
  `b387c03`, which changed files under `tests/` and `docs/` and `README.md`, by
  `9862568` and `3d7e6cb`, each of which changed files under `docs/` and `tests/` and
  `README.md`, and by the commit that writes this line, which changes files under
  `docs/` only: computed on clones of `0491b84`,
  `a235783`, `8d5d64a`, `a48d9e5`, `fbd7877`, `8311167`, `d2dddf7`, `aa9e7ac`,
  `391c338`, `8360923`, `ed005a0` and `e88e0dd` and on the applied trees, under Python
  3.12.3; the trees of `d508b29`, `9f2f3d7`, `d410bfa`, `34d8e3b`, `ad34c02`,
  `89d2367`, `b387c03`, `9862568` and `3d7e6cb` and the applied tree of the commit
  that writes this line give the same. `bc1b9c2c…` was
  set by `9ea1cf3`, confirmed on Windows by its live run, and held through `f00bef6`,
  `36de35d`, `78ea37d`, `d3188f2` and `67f6ec1`, which changed only files under `docs/`
  and `tests/`, `README.md` and `run_tests.py`'s docstring.
- **code_hash is only comparable within one Python minor version.** It hashes `ast.dump`
  output, a CPython implementation detail (`core/code_fingerprint.py`, "WHAT IT DOES NOT
  SURVIVE"). **Every `code_hash` claim about this project is computed under Python 3.12**
  (Viktor runs 3.12.10).
- **Golden snapshot:** unchanged by the commit that writes this line, which changes
  docs and no code or test, by `3d7e6cb`, which changed a build script under `docs/`,
  one test file, `README.md`'s counts and docs, and read no fixture,
  by `9862568`, which changed a build script under `docs/`, one test file,
  `README.md`'s counts and docs, and read no fixture, by `b387c03`, which changed three test files, `README.md`'s counts and
  docs, and read no fixture, by `89d2367`,
  which changed docs and `README.md` and no code or test, by `ad34c02`, which changed
  two test files,
  `README.md`'s counts and docs, and read no fixture, by `34d8e3b`, which
  changed one file under `docs/`, by `d410bfa`, whose new test reads the fixture and the golden
  test's pinned set without writing either, by `9f2f3d7`, which changed one file under
  `docs/`, by `d508b29`, which changed six test
  files, `README.md`'s counts
  and docs, and read no fixture, by `e88e0dd`, which
  changed one test and docs and read the fixture without writing it, by `ed005a0`, which
  changed one
  tooling test and docs, by `8360923`, which changed comments and docstrings only, by
  `391c338`, by `aa9e7ac`, by `d2dddf7`, by
  `8311167`, by `fbd7877`, by `a48d9e5`, by `8d5d64a` and by `a235783`, which change no
  code and no test, and by `0491b84`, as predicted: it changed `main.py`, which the
  golden test does not run (it calls the router directly), and no fingerprinted name or
  value, so `run_hash` (`40dcdc72…`) holds. Unchanged by `67f6ec1`, `d3188f2`, `78ea37d`, `36de35d`, `f00bef6`, `9ea1cf3`,
  `64ad625` and `d77a8c4` too. Last
  re-baselined at
  `22a9a35`, 4 leaves (the confirmation reason, `volume_sentiment` twice and
  `validation_note`'s volume half: VOLUME DIVERGENCE → FADING VOLUME); before that at
  `6469a67`, 8 leaves.
- **Test suite** — **900 passed / 0 failed, no warnings line** with `pandas_ta`;
  **724 passed / 165 skipped** without it; `run_tests.py` **832 passed / 0 failed /
  31 errors**, all 31 fixture-collection `TypeError`s: the 32 of `e88e0dd` less
  `test_no_module_defaults_a_missing_risk_verdict_to_a_pass`. This is meant to be the
  one place the watched error count is written as a number (DECISIONS, "Ruling,
  15 October 2026 — Part 4's three test shapes", point 5); `README.md` writes it too
  (entry 50). The commit that writes this line changes no test, and the three counts
  hold: from the Linux sandbox, Python 3.12.3, pinned requirements, the patch applied
  to an autocrlf clone of `3d7e6cb`. `3d7e6cb` added one test, taking no fixture and
  not needing `pandas_ta`: pytest rose by 1 in both configurations, and `run_tests.py`
  passes 1 more with its error count unchanged: from the Linux sandbox, Python 3.12.3,
  pinned requirements, the patch applied to an autocrlf clone of `9862568`. Its pytest
  step ran on Windows after the apply (the cache on his disk was rewritten at 18:30:11
  on 26 October, 5 minutes 8 seconds after its files were written, at 18:25:03, and
  holds the new test's id, and its `lastfailed` was left as it was, `{}`, so that run
  recorded no failure), and Viktor went on to the commit, which confirms 900 by
  proceeding. `9862568`
  added one test, taking no fixture and not needing `pandas_ta`: pytest rose by 1 in
  both configurations, and `run_tests.py` passes 1 more with its error count unchanged:
  from the Linux sandbox, Python 3.12.3, pinned requirements, the patch applied to an
  autocrlf checkout of `b387c03` made from his repository's objects. Its pytest step
  ran on Windows after the apply (the cache on his disk was rewritten at 11:12:15 on
  26 October, 3 minutes 28 seconds after its files were written, at 11:08:47, and
  holds the new test's id, and its `lastfailed` was left as it was, `{}`, so that run
  recorded no failure), and Viktor went on to the commit, which confirms 899 by
  proceeding. `b387c03` added one test, taking no fixture and not
  needing `pandas_ta`: pytest rose by 1 in both configurations, and `run_tests.py`
  passes 1 more with its error count unchanged: from the Linux sandbox, Python 3.12.3,
  pinned requirements, the patch applied to an autocrlf clone of `89d2367`. Its pytest
  step ran on Windows after the apply (the cache on his disk was rewritten at 19:13:22
  on 25 October, 2 minutes 54 seconds after its files were written, at 19:10:28, and
  holds the new test's id, and its `lastfailed` was left as it was, `{}`, so that run
  recorded no failure), and Viktor went on to the commit, which confirms 898 by
  proceeding. `89d2367` changed no test, and the three counts held: from the Linux
  sandbox, Python 3.12.3,
  pinned requirements, the patch applied to an autocrlf clone of `ad34c02`. Its pytest
  step ran on Windows after the apply (the cache on his disk was rewritten at 17:30:51
  on 25 October, 4 minutes 49 seconds after its files were written, at 17:26:02, and
  its `lastfailed` was left as it was, `{}`, so that run recorded no failure), and
  Viktor went on to the commit, which confirms 897 by proceeding. `ad34c02` added one
  test, taking no fixture and not
  needing `pandas_ta`: pytest rose by 1 in both configurations, and `run_tests.py`
  passes 1 more with its error count unchanged: from the Linux sandbox, Python 3.12.3,
  pinned requirements, the patch applied to an autocrlf clone of `34d8e3b`. Its pytest
  step ran on Windows after the apply (the cache on his disk was rewritten at 21:39:04
  on 24 October, 4 minutes 45 seconds after its files were written, at 21:34:19, and
  holds the new test's id, and its `lastfailed` was left as it was, `{}`, so that run
  recorded no failure), and Viktor went on to the commit, which confirms 897 by
  proceeding. `34d8e3b`
  changed no test; its pytest step ran on Windows after the apply (the cache on his
  disk was rewritten at 20:09:00 on 24 October, 2 minutes 51 seconds after its file was
  written, at 20:06:09, and its `lastfailed` was left as it was, `{}`, so that run
  recorded no failure), and Viktor went on to the commit, which confirms 896 by
  proceeding.
  `d410bfa` added 13 tests, none taking a fixture, two needing `pandas_ta`: pytest rose
  by 13 with it, by 11 passed and 2 skipped without it, and `run_tests.py` passes 13
  more with its error count unchanged: from the Linux sandbox, Python 3.12.3, pinned
  requirements, the patch applied to the tree of `9f2f3d7`. Its two test steps ran on
  Windows only after its commit and push, at Claude's request: the pytest cache on his
  disk was rewritten at 19:43:56 on 24 October and holds the 13 new tests' ids, and
  Viktor reported "Done. All good." to a request to stop only if a count differed, which
  confirms 896 and 828 / 0 / 31. `9f2f3d7` changed no test; its pytest step ran on
  Windows after the
  apply (the cache on his disk was rewritten at 18:50:42 on 24 October, 3 minutes
  19 seconds after its file was written, at 18:47:23), and Viktor went on to the
  commit, which confirms 883 by proceeding. `d508b29` added ten tests, none taking a
  fixture and none needing `pandas_ta`, and
  made that test, parametrized over three files, one test that takes no argument:
  pytest rose by 8 in both configurations (3 ids become 1), `run_tests.py` passes 11
  more — the ten, and the test it had counted as a fixture error and never run — and
  its error count fell by that one: from the Linux sandbox, Python 3.12.3, pinned
  requirements, the patch applied to an autocrlf clone of `e88e0dd`. Its pytest step
  ran on Windows after the apply: the cache on his disk was rewritten at 08:32:13 on
  21 October, 2 minutes 49 seconds after its files were written, at 08:29:24, and holds
  the new tests' ids; Viktor went on to the commit, which confirms 883 by proceeding.
  `e88e0dd` and `ed005a0` each changed the body of one test, which takes no
  fixture; `8360923` changed comments and
  docstrings in five test files and `run_tests.py` and no test's code; `391c338`,
  `aa9e7ac`, `d2dddf7`, `8311167`, `fbd7877`, `a48d9e5`, `8d5d64a` and `a235783`
  changed no test; and the pytest step of each ran on Windows after its apply — the
  cache on his disk was rewritten at 14:04:12 on 20 October, 4 minutes 36 seconds after
  `e88e0dd`'s files were written, at 11:42:14, 4 minutes 16 seconds after
  `ed005a0`'s files were written, at 10:47:55, 3 minutes
  31 seconds after `8360923`'s files were written, at 09:00:34, 2 minutes 53 seconds
  after `391c338`'s files were written, at 11:45:34 on 19 October, 2 minutes
  51 seconds after `aa9e7ac`'s
  files were written, at 09:54:44, 2 minutes 55 seconds after `d2dddf7`'s, at 08:05:56,
  3 minutes 1 second after `8311167`'s, at
  05:22:59 on 18 October, 4 minutes 8 seconds after `fbd7877`'s, at 18:15:11 on
  17 October, 3 minutes 5 seconds after `a48d9e5`'s, at 17:12:10, 3 minutes
  38 seconds after `8d5d64a`'s, and at 16:31:18, 3 minutes 43 seconds after
  `a235783`'s — and Viktor went on to each commit, which confirms 875 by proceeding.
  `0491b84`
  added 9 tests, none taking a fixture and every one needing `pandas_ta` (each runs the
  engine): the first and third counts rose by 9, the skips by 9, and the error count
  held. Its pytest step ran on Windows after each of its two patches: the cache on his
  disk was rewritten at 13:17:44, 3 minutes 40 seconds after the first patch's files
  were written, and again at 13:54:08, and holds the 9 new ids; Viktor reported no
  difference from the predictions. `67f6ec1` changed no test; its pytest
  step ran on Windows after the apply — the cache on his disk was rewritten at
  10:11:43, 3 minutes 23 seconds after the files were written — and Viktor went on to
  the commit, which confirms the predicted 866 by proceeding. `d3188f2` changed no test
  either. Its pytest step ran on Windows after the apply: the
  cache on his disk was rewritten at 09:18:24, 2 minutes 39 seconds after the files
  were written, and Viktor went on to the commit, which confirms the predicted 866 by
  proceeding. `78ea37d` added 25 tests, none taking a fixture and none needing
  `pandas_ta`, so each count rose by 25 and the error count held. `78ea37d`'s pytest
  step ran on Windows after the apply (its cache holds the 25 new ids), and Viktor
  reported no difference from the predicted 866 or 795 / 0 / 32. `36de35d`'s were 841;
  676 / 154; 770 / 0 / 32, the same as `f00bef6`'s; whether its pytest step ran is not
  checked
  (docs only). `f00bef6`
  added no test and changed 3: the golden coverage test, which has run without
  `pandas_ta` since then (hence 675 / 155 to 676 / 154), the non-finite test and the
  SuperTrend level test. Its pytest step ran on Windows after the apply: the cache on
  his disk was rewritten at 16:20:45 on 15 October, 2 minutes 44 seconds after the
  files were written. `run_tests.py` leaves no trace. `9ea1cf3`'s were 841; 675 / 155;
  770 / 0 / 32. `64ad625`'s were 831;
  668 / 152; 760 / 0 / 32. `d77a8c4`'s were 826; 668 / 147; 755 / 0 / 32.
  `22a9a35`'s were 821; 663 / 147; 750 / 0 / 32.
  `69c92d6`'s were 813; 656 / 146; 742 / 0 / 32. `797bdc9`'s
  were 808; 651 / 146; 737 / 0 / 32. `ef65f46`'s test steps were skipped at the time,
  then run on Windows at 09:06 on 12 October: both matched (792; 721 / 0 / 32). One test,
  `test_the_commit_messages_up_to_the_tag_are_round_7s_to_the_byte`, runs `git log` up
  to the tag `round7-sent-2026-09-30`: it needs the tag, which a full clone has.
- **Engineering Notes:** through Entry #183 (v1.36), which covers `68c6191`.
  **Sixty-four commits behind** — `ec4e5fd`, the floor (a commit that regenerates the
  Notes cannot
  cover itself, Entry #144), `e7a94d1`, `d5ced0c`, `59b747a`, `f256937`, `12b483e`,
  `01f2892`, `8b6fd00`, `e186423`, `86f30f1`, `3e8191a`, `1523e0c`, `ff12e17`,
  `4a4c6ce`, `217ede6`, `d27743f`, `a0276dd`, `040a529`, `9e42d30`, `eb86846`,
  `c2b07fb`, `1b25f36`, `fcb7823`, `9e507b1`, `6469a67`, `ae37795`, `9d00d99`,
  `27d3ed5`, `9051ffd`, `e5ac20a`, `ef65f46`, `797bdc9`, `69c92d6`, `22a9a35`,
  `d77a8c4`, `64ad625`, `9ea1cf3`, `f00bef6`, `36de35d`, `78ea37d`, `d3188f2`,
  `67f6ec1`, `0491b84`, `a235783`, `8d5d64a`, `a48d9e5`, `fbd7877`, `8311167`,
  `d2dddf7`, `aa9e7ac`, `391c338`, `8360923`, `ed005a0`, `e88e0dd`, `d508b29`,
  `9f2f3d7`, `d410bfa`, `34d8e3b`, `ad34c02`, `89d2367`, `b387c03`, `9862568`,
  `3d7e6cb` and the commit that writes this line.
  Every later
  commit adds one
  until the
  next regeneration. Batched, by
  the 15 September rule; no time pressure. v1.36 records the round-1 recovery, the
  rulings of 22 (filed 26), 26, 27, 28 and 29 September, the move to E:, the code for
  findings 16, 7, 4, 6, 5 and 18, work order G and the Aider correction. Its PDF's
  extracted text differs from v1.35's only by the seventeen entries, the new Document
  History row and fourteen footer page numbers (127 pages to 143), compared word by
  word.
- **Portfolio Document and AI-Attribution Statement:** both current with their scripts —
  each rebuilt from `68c6191` in the sandbox (reportlab 5.0.1), its extracted text
  identical to the committed PDF. Neither changes in the commit that writes this line;
  the Attribution Statement's script last changed at `68c6191`, the Portfolio
  Document's at `6e1baba`.
- **README.md:** its test counts are current (900, 724 / 165 and 832, and the error
  count, 31), last changed by `3d7e6cb`, which changed only those numbers there, and
  not by the commit that writes this line; that README writes the error count at
  all is entry 50. **Its
  three status rows are
  current** — "Independent audit", "Release
  gate" and "Backtesting" — since `a235783`, in wording Viktor
  approved, with the two sentences that said otherwise: the paragraph under the table
  now names the gate's closing from 5 to 17 October, and Repository layout no longer
  says nothing on record contradicts backtesting's condition — round 8's ratings of
  Items 2, 3 and 6 do. **`391c338`** changed the "Engine code"
  and "Release gate" rows and the paragraph under the table, in wording Viktor approved,
  for the Critical ruled on 20 October; the "Engine code" row now counts the eighth
  Critical too. **`89d2367`** changed those two rows, the paragraph under the table
  and one sentence of the "Independent audit" row, for the Critical rated on
  25 October, in wording Claude wrote under Viktor's delegation and put to him before
  his commit; he approved it by proceeding past its stop. That sentence, "Every
  finding ruled Critical has a
  landed fix verified by an independent auditor", written on 17 October, had been false
  since 20 October: `391c338` changed the two rows beside it and left it. Still stale,
  on the list at his choice (Open items): "The audit, and
  what it found" and "How this was built", which stop at
  13–14 September, and the layout block's `logs/` line, silent on `logs/pinned/` since
  `9e507b1`. Its paragraph on what is empirically validated was rewritten at `6469a67`
  (the BTC-Adjusted Prediction removed) — Viktor's to reword (Open items).
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
`3bfa6b7`, `add8540`, `57f0521`, `b0efe23`, `76c8cde`, `8b9ac1e`, `d76ddfd`, `7d0024e`, `c2b07fb`,
`1b25f36`, `fcb7823`, `9e507b1`, `6469a67`, `ae37795`, `9d00d99`, `27d3ed5`, `9051ffd`, `e5ac20a`, `797bdc9`, `69c92d6`, `22a9a35`, `d77a8c4`, `64ad625` and `9ea1cf3`: the command list stopped at the live run, Claude read the record,
and only then gave the commit steps. **Since finding 16, a
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
  (the first finding of finding 18's session). And a new UPPER_CASE numeric constant in a
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
- **4 October (the session of `217ede6`):** a counted disclosure is only as good as the
  search behind it. Rev 8's looked for a rule's number beside a verdict word and missed
  six rules the code cites by table position ("T2-1", "T3-5", "Tier 2, item 6") or under
  a dispute with no verdict word. Search for every way the code names a rule — "Item N",
  "Items N/M", "TN-M", "Tier N, item M", and the rule's own name — then read each hit.
- **5 October:** listing Viktor's repository before predicting `git status` (the eighth
  session's lesson) found three untracked PDFs in `Claude outputs\` that a prediction
  from the clone could not see. A ruling's figures are re-derived before they are filed
  (the 27 September lesson); the triage's all held. And a count of the decision log by
  `provenance.source` misses a record that has no provenance: the ruling named nine
  test records, and the log holds ten — record 4 has no provenance at all.
- **5 October, fix 1:** `pytest.raises(Exception)` accepts any exception, a `TypeError`
  from a stale keyword included. `test_calculate_stop_targets_rejects_a_non_finite_atr`
  was already vacuous at `eb86846`: with its NaN guard deleted it still passed, because
  the wrong-side refusal raises on the NaN stop that follows. It now names the guard's
  own error, and fails with the guard deleted. Assert the type and the message. And a
  replay of the live log with today's code reproduces 34 of the 37 logged actions; the
  three it does not are records 19–21 (15–16 September), which F's gate and G changed,
  as their own entries predicted — the G lesson's check, passed.
- **The night of 5 to 6 October, fix 2:** importing a fingerprinted constant by name
  into another fingerprinted module (`from models.entry_model import MIN_TREND_ADX` in
  `decision_model`) makes a second, unlisted copy of it, and
  `test_fingerprint_names_every_constant.py` failed on it in the first full run. Import
  the module and read the attribute. And a replay that recomputes the gate from each
  record's own fields, rather than reading its recorded signals, reproduces 46 of the
  48 logged actions on `c2b07fb`'s code; the two it does not are records 19 and 20
  (15 September, WAIT), which predate F's gate and replay as CONSERVATIVE SHORT on both
  codes, where G's replay, reading their absent signals, refused them.
- **The night of 5 to 6 October, the test steps:** "silence means the steps passed" is
  Viktor's rule, and it holds for steps that ran. pytest leaves a trace that settles
  whether a run happened: `.pytest_cache/v/cache/nodeids` on his disk is rewritten at
  the end of every run and lists every test it has collected, so a time after the apply
  and the new tests' names in it show the step ran; `run_tests.py` leaves none. Read it
  off his disk before giving the commit steps. It showed that `c2b07fb`'s pytest count
  never ran on Windows, and that `1b25f36`'s two test steps had been skipped before its
  live run.
- **6 October, fix 3:** a search for the keyword `adx=` at the risk check's call sites
  found fifteen calls and missed the positional ones. Two tests called
  `validate_risk_parameters(100.0, 80.0)` and leaned on the `"NORMAL"` default the patch
  removed; only the full run caught them. To find every caller of a function whose
  parameters change, walk the parse tree for calls of that name, not a keyword. And the
  engine run on pinned data outside the test suite writes its decision log, archive and
  chart into that tree's `logs/` — the suite redirects them, a script does not. A probe
  run in the pristine copy did, and was removed with `git clean -fdx` before anything
  was built from it. Probe in a throwaway copy.
- **6 October, B6:** the golden updater rewrites the fixture as LF every time it runs.
  It was run a second time, to read a warning, after CRLF had been restored, and the
  line-ending check before the diff caught the second rewrite. Check line endings after
  every run of the updater, not only the first. A negative control passed: with
  `is_live_record` taking a falsy `pinned` for False, the test still passed, because
  each of its not-live shapes also lacked a source and the source check refused them
  first — the 27 September lesson again. The shapes now carry one defect each. When a
  recorded path's spelling changes, read every consumer of the printed output, not only
  of the record: the audit-package builder redacted its temp directory in its native
  spelling only, and a pinned run's "Decision logged to" line would have carried it with
  forward slashes, username included, on Windows. And a live run can be tested
  offline: clear the pinned source and replace the singleton's `fetch_ohlc` with one
  that serves the fixture (`tests/test_pinned_runs_keep_their_own_records.py`,
  `_route`); everything from `get_tf()` on is the production path.
- **12 October, F9:** before changing what a function does on a path the engine never
  takes, read the tests around it for a decision someone already recorded about that
  path. The first build made a too-short frame raise, so the run would be marked
  degraded; `tests/test_swing_structure_is_not_invented.py` records that not-enough-data
  in `structure.py` is an ordinary return, on purpose. It would still have passed —
  its frame is 20 rows, over the 15 the regime needs — so the suite could not have
  caught it. And a stateful function whose state never survives is tested by reusing
  one instance: a fresh one per call, as every existing test built it, can never reach
  the branches that state guards.
- **11 October, F8:** a rule about names is checked on the parse tree, not the text.
  The new test reads every function in the engine's code (the walk `code_hash` takes)
  and asks whether one that names something vwma touches the engine's VWMA — its
  column, its window setting, its points cap or `vwma_pts`. Comments that mention the
  old names are not code and are not counted; a third test runs the function as it stood
  before F8 through the same check, so the check is shown able to fail.
- **11 October, F6:** a function's list of accepted options is part of what it
  promises. `tests/test_no_lookahead.py` pinned the forward-fill branch and nothing
  pinned the list, so a look-ahead method sat one keyword argument away and a name the
  function did not know returned the series unfilled, silently. The new test asks the
  function for its accepted methods (from its own refusal, so the list cannot drift from
  a copy in the test) and checks every one; a second test runs the removed
  interpolation through the same check, so the check is shown able to fail.
- **10 October, F5:** when a label changes, read every assertion that names the old
  wording, the negative ones first. `"0.00% away from the band" not in lines` would
  have passed whatever the panel printed once the line no longer says "away from the
  band"; it now looks for "0.00%", and a control printing "0.00%" for an absent zone
  makes it fail.
- **10 October, F3:** run an auditor's reproduction before building on its account of
  the outcome. Round 8's F3 described a panel and a record the code never made; the
  defect it named was real, the consequence was not. A one-file probe on the tip and
  on the package commit settled it in a minute, and the new engine-path test asserts
  what the run now does rather than what the report said it did.
- **9 October, N5:** when a patch removes what a test tests, the test goes with it,
  named where it stood. Kept, it fails, or worse, passes on nothing: with Item 7's
  status line gone from the panel, its source-text test would have passed had the
  wording been left in a comment. A removal can take a test's subject away half-way:
  the asset-name test asserted that the decision model calls `asset_name()`, which only
  the removed sentence did. For a change that should alter no decision, the run
  archives are the replay set: each archive's candles rebuilt into a pinned directory
  and routed through the code before and after, every field compared (38 archives; the
  only differences were the removed fields and what `run_hash` names). And
  `models/decision_model.py` ended without a final newline, so an edit anchored at the
  end of the method had to include that last, unterminated line: the edit's own check
  that nothing followed the method stopped the first try at the removal before it wrote
  anything.

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
   said "past 15%" until 26 September, when the code was read. (Line numbers as of
   26 September. Since B7, at `d77a8c4`, RISK REGIME past 15%
   reads EXTREME RISK; the refusal and its message are the same.) Seen on Viktor's
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
27 September (43 records); two runs are not a rate. **5 October:** a third LONG
followed at 14:22 UTC the same day, on G's code. Point 1 of the triage, landed at
`c2b07fb`, changed the stop again — ATR × 1.2 × the volatility factor — and under it the
three LONGs' stop would have been 6.35%, not 7.15%, and all three still LONG (the replay
through the decision model, in `c2b07fb`'s message). Its live run, record 48, was LONG
as well (ADX 27.6).

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
**Triaged 5 October** (DECISIONS, "Ruling, 5 October 2026 — round 8 triaged …"): round
8's findings and Claude's review of the same night were placed. The fixes the triage
calls for are made now (Work order), not here; what stays here, or joins, is marked
below. Whether the entries that change no trade join the label and record batch is
Viktor's to answer.

**Sorted 19 October** (DECISIONS, "Ruling, 19 October 2026 — the list for after the
audit, sorted …"): every open entry has a kind, who decides it, a rough size and a
place in the order there, numbered by its place below, 1 to 46. That answers the
question above for the entries that change no trade: under the plan they are all in
the work before the audit, entry 1 apart.

- **The risk gate runs before the bias checks.** The risk verdict returns at
  `models/decision_model.py:551–553`, before the weak-validation and lean checks at
  `:656–668` (at `7d0024e`; written as `:500–502` and `:605–617`
  on 26 September, correct until `d76ddfd` moved them six lines, then G further), so a
  run the ladder would have answered WAIT is reported as NO-TRADE (RISK
  TOO HIGH). In the log counted on 26 September this was 2 of the 33 refused runs. It
  changes what the panel says, not which trades are taken. Found by Claude reading the
  code, 26 September; **ruled for after the audit** (Viktor, 26 September). The Part 7
  document's S1, not found by round 8. **18 October:** proposed on 17 October as one of
  the four held-back defects, and replaced (DECISIONS, "Ruling, 18 October 2026 — the
  four held-back defects …"); it stays on this list. **19 October:** worked after the
  audit, with the four (DECISIONS, "Ruling, 19 October 2026 — the list for after the
  audit, sorted …", point 3).
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
- **Under a NEUTRAL bias the entry score is measured for a side nothing chose.**
  `core/engine_core.py` scores entry quality for `eq_trade_direction`, which under a
  NEUTRAL bias is the sign of `bias_score` (the line `eq_trade_direction = "LONG" if
  bias_score >= 0 else "SHORT"`) — the same rule finding 5 found in the plan. The panel
  still prints ENTRY QUALITY and TRADE QUALITY for it; finding 5's ruling covers the
  stop, targets and R:R only. It decides nothing: a NEUTRAL bias never reaches a side.
  Found by Claude reading a rendered NEUTRAL panel while building finding 5,
  27 September; on this list by the 22 September ruling, not separately ruled. The
  Part 7 document's S3, not found by round 8.
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
  this list by the 22 September ruling, not separately ruled. The Part 7 document's
  S4; round 8 found it (F10). **Held back for Amazon's audit as H1** (DECISIONS,
  "Ruling, 18 October 2026 — the four held-back defects …"): left as it is until after
  the audit.
- **A floor on T1: at least 3% after fees.** Point 2 of "Ruling, 28 September 2026 —
  what "finished" means, and how the engine is judged": the engine should issue no LONG
  whose T1 nets under 3% after fees. Today T1 equals the stop distance, anywhere from
  0.2% to 8% (`models/risk_model.py`, read at `7d0024e`), so this is a filter on the
  stop distance and a new trading rule. How many trades it would remove has not been
  measured; only records since `76c8cde` carry ATR-only stops. **Ruled for after the
  audit** (Viktor, 28 September). **5 October:** point 1 of the triage, landed at
  `c2b07fb`, narrows T1 with the stop — on the live runs the median from 6.65% to 5.25%.
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
  of "six questions before the send"). Point 4 of the PDF is the next entry; point 3,
  the BTC adjustment, came off this list when N5 landed, at `6469a67`; point 5 is not live (DECISIONS, "the test bugs", item 7).
  **25 October:** dropped with the EV line until backtesting measures how often T1 is
  reached before the stop (DECISIONS, "Ruling, 25 October 2026 — the engine's
  indicators …", ruling 6), in the redesign, entry 53.
- **Is ×0.90 enough against the macro trend? (point 4 of the 15 September PDF).**
  `models/entry_model.py:384–385` multiplies the entry score by
  `CONFLUENCE_PENALTY_MULT` (0.90) when macro opposes the trade. Since work order G it
  is one of three things left that act against a trade opposing macro, with the
  validation score's −20 and macro's 10% in `bias_score`, which G read, unconfirmed
  with Viktor, as the 22 September ruling's "three penalties" item. Traced on
  29 September and **moved onto this list by the same ruling**. Not a test bug: it
  asks how large a weight should be, and `models/decision_model.py:692` names it
  anyway. **5 October:** round 8's F4, third path, is the same question — macro moving
  a setup between LONG and CONSERVATIVE LONG — and stays here (point 9 of the
  triage). **20 October:** ruled Critical, a break of Tier 1 Item 11 (DECISIONS,
  "Ruling, 20 October 2026 — F4's third path is Critical …"); the release gate is
  closed until its fix has landed and been re-audited. The fix lands after the reading
  of 14 November and before the send. **25 October:** its shape ruled — removed, not
  reweighted, in the redesign (entry 53), and re-audited by Amazon within its audit
  (DECISIONS, "Ruling, 25 October 2026 — the engine's indicators …", ruling 8).
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
  line is itself the defect. **19 October:** an eighth, a docstring this entry leaves
  out: `tests/test_trend_direction_source.py:159`, "ROUND 6 FOLLOW-ON, 12 September
  2026" (read at `d2dddf7`, where `run_tests.py`'s comment is at line 155).
  **20 October: changed**, all eight, by `8360923`, comments and
  docstrings only: the six comments read "REQUESTED-RUN 6 MUTANT ESCAPE (GPT-6 Astra,
  round 5)", the docstring at `:159` "REQUESTED-RUN 6 FOLLOW-ON", and the one at
  `tests/test_run_tests_filter_matching.py:2` "round 5's requested-run 6 (GPT-6
  Astra)". Dated records — the Part 7 file, round 8's reports — keep the old wording.
- **A comparison between two vocabularies in `calculate_entry_quality`.**
  `models/entry_model.py:384` (at `01f2892`) tests `macro_bias != trade_direction`.
  `macro_bias` is BULLISH, BEARISH or NEUTRAL and `trade_direction` is LONG or SHORT, so
  the test is always true. The two branches above it catch agreement, and
  `core/engine_core.py` passes only BULLISH, BEARISH or NEUTRAL, so the result is right
  for every value any caller passes; any other macro value would be penalised as
  opposing. Found by Claude on 30 September while checking point 4 of the 15 September
  PDF for the Part 7 document; on this list by the 22 September ruling, not separately
  ruled. Not scored: it changes nothing observable. **5 October:** round 8's Part 7
  reply would class it a defect (its §3) and corrects one clause: a macro value equal
  to the trade direction ("LONG" for a long) leaves the multiplier at 1.0, not 0.90
  (its §2(3)).
- **The trend score barely varies (the review's B1).**
  `indicators/trend_health.py:122–123` scores the slope as `tanh(|slope| × 100) × 45`,
  which is already at 0.96 of its range at 0.02% per bar. Over 494 real 4h bars the
  review counted trend health at 50 or more on 99.4% and at 75 or more on 82%, and every
  live run printed 82.1 to 100. So the tiers' trend requirements gate almost nothing
  beyond ADX. **Ruled 5 October** (point 5 of the triage): after the audit, decided
  before paper trading starts; Claude may first count how often candidate scales would
  fire. **Seen on ten pairs, 17 October** (Claude, from the records on Viktor's disk;
  Viktor read 84 to 100 on every pair's hand-run panel): trend health 83.72
  (AEROUSDT) to 100.00 (SOLUSDT) on the hand runs before `0491b84`, and 83.71 to 97.00
  on the first scheduled run, at 14:05. On all 21 records the slope term was 44.95 to
  45.00 of its 45 points, for average EMA slopes of 0.037% to 0.237% per bar, so the
  scores differed only through ADX (23.7 to 40 of its 40) and RSI's band (12 or 15 of
  15); on 9 of the 21 the ADX term was at its cap too, and the score read 97.00 or
  100.00. Each
  score was recomputed from its record's own EMA slopes, ADX and RSI with the formula at
  lines 136–160 of `0491b84` (122–123 above are the review's, at `9e42d30`), and every
  one matched. All ten pairs were falling with Bitcoin that day: one market state, not
  21 samples. **25 October:** trend health is removed, and its tiers with it (DECISIONS,
  "Ruling, 25 October 2026 — the engine's indicators …", ruling 4), in the redesign,
  entry 53; its scale is no longer the question.
- **Spike detection watches 20 bars while the volume profile reads 450 (round 8's F7).**
  `indicators/indicators.py:767–771`. Widening the window degrades more runs, so it
  changes trades. Viktor's, not ruled (the triage of 5 October).
- **The divergence veto (the review's B4).** Momentum divergence compares the close and
  RSI now with the same four bars earlier, not highs with highs
  (`indicators/trend_health.py`, section 5), and it vetoes the side it points against;
  the review counted it on 11.9% of real bars. Its labels landed at `22a9a35`: the
  sentences say "price/RSI disagreement over four candles"
  (DECISIONS, "Ruling, 14 October 2026 — B4's labels: their shape"). Whether it should
  veto is a trading rule — Viktor's, not ruled.
- **The keys `momentum_divergence` and `divergence_direction` keep their names** (B4's
  labels, 14 October). Renaming them changes the decision contract, the golden snapshot
  and more than 15 test files for a word, so the sentences that print them were
  corrected and the rename waits for after the audit, as `REGIME_HYSTERESIS_THRESHOLD`'s
  does (DECISIONS, "Ruling, 14 October 2026 — B4's labels: their shape", point 3).
  **19 October:** at `d2dddf7` the two keys are named in thirteen test files and the
  golden fixture (a text search), not in more than 15.
- **`models/bias_engine.py` scores a volume label it does not know as neutral** (found
  filing B4's labels, 14 October). `_VOLUME_SENTIMENT_SCORES.get(…, 0.0)`: UNKNOWN
  VOLUME is not one of its keys, so a failed volume read counts towards the bias exactly
  as NEUTRAL VOLUME does. Whether a failed read should count is a weighting question —
  Viktor's. On this list by the 22 September ruling, not separately ruled.
- **Two words for a regime that was not read** (found filing B7, 15 October).
  `validate_risk_parameters` returns "UNKNOWN" where no regime can be computed (a price
  or stop that is not finite or not positive, and its except branch);
  `classify_risk_regime` returns "UNKNOWN RISK" for a volatility state it does not know,
  and the router, `decision_model` and the panel default an absent regime to "UNKNOWN
  RISK". Each branch that says "UNKNOWN" already fails `risk_valid`, so neither word
  decides anything. One word for one meaning is F8's class; B7's ruling did not reach
  it, so it is not changed. Viktor's whether it joins the batch or waits; not ruled.
- **The BTC section's `degraded_inputs` holds only what BTC's trend health reports**
  (found filing B9, 15 October). The comment above it in `core/engine_core.py`'s BTC
  block says a BTC indicator failure "is recorded below, inside btc_context itself";
  the code records `btc_trend`'s own `degraded_inputs`, so a failed BTC indicator that
  trend health does not read reaches only the log line ("BTC context indicator
  failure"). Since B9 a failed BTC SuperTrend makes the section unavailable, so it is
  not one of them. Reference only; changes no trade. On this list by the 22 September
  ruling, not separately ruled. **20 October: changed** by `8360923`, comment only
  (`ed005a0` left this sentence saying "the commit that writes this line"; corrected
  the same day): it says what is recorded — trend health's own `degraded_inputs`
  and no other BTC failure — with a dated note on what it said. Found doing it: entry
  47, at the end of this list.
- **Thresholds fixed for 4h (the review's B5).** The volatility bands (ATR/price over 1%,
  2% and 4%), the stop limits (0.2%, 8% and 15%), the structure threshold (0.15%) and the
  VWMA and HVN bands are percentages of price whatever the timeframe. On AERO 1d, ATR/price
  was above 4% on every one of 90 daily bars (the review's count), so every bar would be
  EXTREME VOLATILITY and every trade refused. Viktor's, before any timeframe but 4h is
  used. **20 October:** ruled 4h only for now, with a guard that refuses any other
  timeframe, in wave 2 (DECISIONS, "Ruling, 20 October 2026 — B5: 4h only for now …").
  The thresholds for each timeframe wait without a date.
- **The Constitution, read with hostile intent (the review's C1–C7).** It checks how the
  engine reports, not whether it works (C1); Item 7 is satisfied by a label (C2); three of
  the four test bugs break no rule as written (C3); the severity rubric against round 8's
  severities (C4); the builder writes what the auditor checks against (C5); stale or
  self-contradicting text (C6). C7 lists candidate amendments, not proposals. Viktor's; an
  amendment to Tier 1 or Tier 2 needs a reviewer who is not Claude.
- **Two points of round 8's Part 7 reply.** §1(3): `models/entry_model.py`'s and
  `indicators/trend_health.py`'s default responses return finite zeros, which the panel
  prints as `0.00/100` where "not computed" is available. §1(5): a failed run returns
  before `decision_log.write` (`models/signal_router.py:162–169`), so a day the engine
  could not run leaves no line in the log, and twelve months of paper trading will need
  those days (the review's C6, item 4). Both confirmed from the code by the review.
  Whether they join the batch is Viktor's to answer.
  **20 October, checking entry 37:** round 8's Part 4 says the same of §1(3) through
  `test_absent_scores_print_as_absent_not_as_zero`, and it holds. Each default response
  forced through the router on the pinned set (Linux sandbox): trend health's printed
  TREND "(Score: 0.00/100)"; entry_model's printed "0.00/100" on ENTRY QUALITY and
  Proposed Entry, and the run was recorded as not degraded, trading authorized, the
  action CONSERVATIVE LONG: that response names no degraded input. On the engine's path
  trend health reaches its own when both slope columns are
  missing, or on any exception; entry_model reaches its only on an empty frame or a
  close that is not a positive number, which the validation refuses first (read from
  the code, not run). The test Part 4 asked for — the engine's own default responses,
  rendered through the router — would fail today, so it comes with this entry's fix,
  which also brings that test's docstring of 20 October current.
- **A longer daily window for macro** (the Freqtrade comparison, 5 October). The engine
  decides macro on 99 closed daily candles. On 99-candle windows the comparison found
  EMA-50 off by a median of 0.2% against a long history, and the close-above-EMA-50 side —
  which is `macro_bias` — flipped on 5 of 294 AERO windows and 7 of 294 BTC windows, with
  4h candles standing in for daily ones. About 200 daily candles would settle it. It
  changes macro readings, so it is Viktor's.
- **Goal B's precondition 2 would let the day's candle leak in** — an observation on the
  ratified text, made on 5 October from two documents, not from code: nothing of the
  harness exists. The precondition truncates every series by candle open time strictly
  before `t`. A daily candle opened at 00:00 is before a decision at 12:00 the same day,
  so it is kept, and a pinned file treats every row as closed (DECISIONS, finding 16,
  "Pinned data") — so the engine would read the whole day's candle, the leak the
  precondition's own text warns against. Keeping a candle only once its open time plus one
  bar is at or before `t` gives the same rows on 4h and keeps the forming daily candle
  out; Freqtrade does it by shifting a higher-timeframe candle one interval forward (the
  comparison's item 4). Changing a ratified specification is Viktor's.
  **26 October: decided**, by Claude under Viktor's delegation of 19:02 ("I don't
  understand. Just fix it as you see fit."), filed by the commit that writes this line
  (DECISIONS, "Decision, 26 October 2026 — Goal B keeps a candle only once it has
  closed at `t` (entry 26)"): at `t` a candle is kept only when its open time plus
  one bar of its own timeframe is at or before `t`, the live engine's own rule
  (`_split_forming`, read at `3d7e6cb`); `t` is the moment the decision is made; and
  the negative control's noise covers every candle the rule drops, which the ratified
  control — noise on the bars after `t` — did not reach for the daily candle.
  Precondition 2 is amended in place. Docs only; nothing of the harness exists.
  Viktor's to reverse.
- **`calculate_dynamic_bias` takes `trend_exhaustion` and never reads it**
  (`models/bias_engine.py:184` and `:264`, read at `c2b07fb`): the flag is coerced to a
  bool and then unused, so the bias score does not see it, and a caller would think it
  does. Found by Claude scoping fix 2 on the night of 5 to 6 October. It changes no
  trade; on this list by the 22 September ruling, not separately ruled. **Held back for
  Amazon's audit as H2** (the same ruling): left as it is until after the audit.
- **Two counts in `models/risk_model.py`'s docstrings are wrong** (read at `1b25f36`,
  from the parse tree): `read_risk_verdict` says `validate_risk_parameters` has six
  return paths, and it has seven; `validate_risk_parameters` says "the three
  early-return branches", and four return before the regime is classified. Both were
  wrong before fix 3, which leaves them as they were. Found by Claude scoping fix 3 on
  6 October. Labels only; on this list by the 22 September ruling, not separately
  ruled — they fit the label and record batch if Viktor adds them to it. **20 October:**
  the first changed by `8360923`, six to seven, in place, with
  no note in the docstring (a note's four lines broke entry 48's test, below): counted
  from the parse tree at `26a05dc`, where the sentence was written, at
  `fcb7823` and at `391c338`, the function has always had seven returns, each a bool
  literal. The second had already been corrected at `d77a8c4` (B7), by a paragraph
  under the wrong one, which the docstring keeps; this entry was not updated then.
- **`calculate_stop_targets` still defaults `volatility_state` to `"NORMAL"`**, a state
  `calculate_dynamic_regime` never produces, and gives every state it does not name the
  factor 1.0 — so an unknown volatility gets the medium stop. Unreachable on the engine's
  path: the engine's UNKNOWN means the decision bar's ATR or close is not a finite
  positive number, and the same function raises on that first. Fix 3 removed the same
  default from `validate_risk_parameters`, where it fed the regime; the stop was not
  fix 3's to change. Found by Claude on 6 October. It changes no trade.
- **STATUS reads ACTIVE ENTRY ZONE up to half a band-width outside the band**
  (`models/entry_model.py`, `dist_to_mid <= zone_width`, read at `ae37795`). The
  test is the close's distance from the band's midpoint against the band's full width,
  so ACTIVE covers the band and half its width again above and below it. ACTIVE
  scores the zone's full 30 points and is what `decision_model` reads as
  `entry_active`, so it can change which tier a setup reaches. Found in Claude's review
  of 5 October, in F5's row ("Also not in round 8"); not ruled in the triage, which
  made F5 a label fix. Seen again building F5 on 10 October. On this list by the
  22 September ruling, not separately ruled.
- **Whether a gap at the decision bar is refused depends on whether a later bar
  exists** (`clean_series`'s forward-fill branch, read at `9d00d99`; seen building F6,
  11 October). An indicator with no value at the last row stays NaN and the run is
  refused (finding 3's trailing edge); the same gap at an earlier row is filled from the
  row before it. `[1, 2, NaN]` cleans to `[1, 2, NaN]`, `[1, 2, NaN, 4]` to
  `[1, 2, 2, 4]` (run in the sandbox). No value is taken from a later row — F6's test
  holds for it — but a backtest that computes indicators once over its whole history
  would decide on a carried-forward value at a bar where the live engine, deciding at
  that bar, would have reported a failure. Goal B's harness is where it matters; nothing
  on the engine's path today. On this list by the 22 September ruling, not separately
  ruled.
- **`REGIME_HYSTERESIS_THRESHOLD` is a dead band, not hysteresis** (`structure/
  structure.py`; F9, 12 October). Renaming it moves `run_hash` and the golden snapshot,
  so the name was kept and its comment corrected; the rename waits for after the audit,
  with CONFIRMED's (DECISIONS, "Ruling, 12 October 2026 — F9's shape and scope").
- **Found by the fallback sweep, not changed by it** (13 October; line numbers at
  `ef65f46`; DECISIONS, "Ruling, 13 October 2026 — the fallback sweep …", last
  section). `_build_decision_object`'s own parameter coercions: `degradation`,
  `provenance` and `lineage_record` read as `[]` or `{}` when not passed, and an
  `exit_watch` that is not a list recorded as `[]` — they serve direct callers, since
  on the engine's path every value now arrives by subscript. `core/engine_core.py`'s
  three other `degraded_inputs` defaults of `[]` (`:711`, `:770`, `:901`), "nothing
  degraded" when absent — not checked for reachability. The supertrend direction of
  0.0 when the `ST_Direction` column is missing (`:777`, `:905`) — reachable on an
  indicator failure, so a degraded value feeding the bias rather than an unreachable
  fallback; whether its absence is recorded as a degradation was not checked. On
  this list by the 22 September ruling, not separately ruled. **Since B9 (15 October):**
  Bitcoin's (`:905`) was B9's, which the triage of 5 October had put in the batch, so
  filing it here was Claude's error (DECISIONS, "Ruling, 15 October 2026 — B9:
  Bitcoin's SuperTrend is read directly"); it is read directly since `64ad625`. The
  asset's own (`:777`; `:797` at `d77a8c4`) stays here by that
  ruling, now checked: a failed SuperTrend is named in the run's `degradation`, which
  authorizes no trade and caps confidence at 50, and the 0.0 makes the factor score
  zero, as trend health scores its own missing inputs. Two residues, neither changing a
  trade: `lineage.bias_components` records the factor's input as 0.0 where nothing was
  measured, and the 0.0 is saved as the next run's prior state, so that run cannot flag
  a SuperTrend flip either, and does not say so (both run in the sandbox on the pinned
  set).
- **The simulator writes an order on every run, a WAIT or a NO-TRADE included** (found
  filing B10, 15 October; `live_trading.py`, `run_once`, at `64ad625`). Every run that
  does not end in an error builds and writes a `sim_trade_<time>.json`, whatever the
  action, with that run's stop and targets — on a run with no trade, a plan the engine
  did not suggest. Its `decision` field says which, so a reader can tell, and nothing
  reads the files back (Open items, "what B6 left shared"); none has been written on
  Viktor's machine (no `logs\LiveSim` there, 15 October). It matters once paper trading
  reads these files. Changes no trade. On this list by the 22 September ruling, not
  separately ruled. **Held back for Amazon's audit as H3** (the same ruling): left as it
  is until after the audit.
- **`run_tests.py` counts a test that takes a fixture as an error, as it counts a real
  one** (round 8's Part 4, its structural point; ruled for this list on 15 October,
  DECISIONS, "Ruling, 15 October 2026 — Part 4's three test shapes", point 5). A real
  error that arrives in the same change as a fixture-taking test is removed leaves the
  count where it was. Counting the two apart would change the runner's output and move
  `code_hash`, since `run_tests.py` is one of its files. Changes no trade.
- **The non-finite panel test cannot reach LIVE PRICE** (found landing Part 4's three
  test shapes, 15 October). It sweeps the floats the golden decision holds, and the
  golden run is on pinned data, whose live price is null: with that line's finiteness
  guard removed for a present value, the test stays green (Linux sandbox). The line is
  guarded in the code. Changes no trade. On this list by the 22 September ruling.
  **20 October: changed**, by `e88e0dd`: the test puts a finite
  live price into the struct candle before anything renders — after asserting the
  fixture's is null — and its precondition asserts the panel prints one LIVE PRICE line
  with a price, so the sweep sets that price to +inf, -inf and NaN like every other
  float. Of the golden decision's nine null leaves, it is the only one the panel reads
  (`core/panel_render.py` reads `live_price` from the struct candle alone). With the
  line's check made `is not None`, the old test passes and the new one fails on the
  three renders of the live price ("$nan"); with the line not printed, the new one fails
  its precondition (Linux sandbox).
- **Part 4's other named tests are not checked against its description** (round 8,
  run 2, Part 4: the absence scans of its shape 1, and its shape 4,
  `tests/test_panel_prints_only_what_was_computed.py::test_absent_scores_print_as_absent_not_as_zero`).
  The three shapes the triage put in the batch, and the second shape's sibling, landed
  on 15 October; the rest were on no list by name. Changes no trade. On this list by
  the 22 September ruling.
  **20 October: checked and changed**, by `d508b29`. Part 4
  names, beside the four of 15 October: in shape 1, `test_no_order_execution_calls` "and
  its three siblings" — the file has four, all checked — and the scans in
  `tests/test_risk_verdict_is_read_not_assumed.py`,
  `tests/test_swing_structure_is_not_invented.py` and
  `tests/test_no_fabricated_defaults_remain.py`; in shape 3 the same, and
  `test_no_dead_columns.py::test_deleted_columns_stay_deleted` as honestly labelled and
  paired; in shape 4, `test_absent_scores_print_as_absent_not_as_zero` and a milder one
  this entry left out,
  `test_no_circular_reasoning.py::test_the_reasoning_no_longer_claims_trend_health_as_a_confidence_input`;
  in shape 5, `test_decision_contract.py`'s two early returns, as not that shape. Part 4
  is right on each defect, and on the two it calls sound beside them (read from the
  tests). Each scan's matcher is now a function the scan calls and a control feeds. Ten
  tests added: nine fail with the matcher or file list they check made to find nothing,
  the tenth, the manifests' control, with a manifest removed. Writing them found what
  the scans could not see, now read: `import json, ccxt`, and an import by name; in the
  manifests, the names pip installs binance and alpaca_trade_api under, and `~=`, `<`,
  `!=`, `>`, `<=`, extras and a marker; `.get("risk_valid",True)` without the space, a
  default of 1, and every engine module but the three sites — that guard also took the
  file as an argument, so `run_tests.py` never ran it; the current price returned
  through a local; and the analysis's defaults under any name but `result`, in a file
  whose scan had found no `.get` to read since 21 September. The "95" had had nothing to
  catch since `c4dfcc7` (1 September) removed the call's trend input; the test now holds
  that every figure the explanation states is the confidence or its scale. The
  absent-score test's setup cannot come from the router, as Part 4 says, and what the
  engine does send prints 0.00/100: entry 24's to fix, with its test (the entry above);
  this test gains a docstring saying so. Twenty negative controls on the engine, the
  manifests and the suite's own file walk: fourteen leave the old tests green and fail
  the new; six fail both (Linux sandbox). Not checked: the tests Part 4 names as sound
  in shapes 1 and 6 (three controls, four preconditions), and the three its judgement
  names for F1 and F5, both fixed and verified on 17 October.
- **Fable 5.1 works on this list after the audit** (DECISIONS, "Ruling, 29 September
  2026 — Fable 5.1 works on the list for after the audit, not before it"). Not a
  finding; recorded here so the list says who works on it after the audit.
  **20 October:** Claude builds the list, now worked before the audit; Fable 5.1 waits
  until after Amazon's audit, asked again at entry 10 (DECISIONS, "Ruling, 20 October
  2026 — Claude builds the list …").
- **The panel prints prices to four decimals** (found choosing the pairs, 17 October,
  reading `core/panel_render.py`): SWING STRUCT, EMA BAND, DECISION CLOSE, LIVE PRICE,
  STOP LOSS and the TARGET lines use `:.4f`, so on a pair priced under about $0.01 the
  panel cannot show the stop or the targets; the decision record keeps full precision.
  Panel only; nothing decides on it. On this list by the 22 September ruling.
- **"AERO" in names and one log line, whatever the pair** (found the same way):
  `core/engine_core.py`'s warning when the BTC context fails says "AERO analysis above
  is unaffected", and `models/btc_context.py`'s `compute_correlation_beta` takes
  `aero_closes`, its docstrings saying AERO. `a530006` fixed two panel lines of this
  kind (Review findings, 1). The process log and names only.
- **On a degraded run, TRADE QUALITY's Proposed Entry is capped and no sentence says so**
  (found reading DOGEUSDT's first live panel, 17 October; read from the code):
  `models/decision_model.py`'s `_apply_degradation` caps `proposed_entry` at
  `DEGRADED_CONFIDENCE_CEILING` (50) as well as the confidence, as the degrade ruling of
  29 August says, but adds a reason sentence for the confidence cap only. The panel then
  printed ENTRY QUALITY 89.17/100 and, under TRADE QUALITY, Proposed Entry 50.00/100, with
  nothing to say why the two differ. Panel and reasoning only; a degraded run authorizes
  no trade. On this list by the 22 September ruling.
- **A run on another pair that does not go through `main.py` records `config.SYMBOL` as
  AEROUSDT** (found writing the ruling of 17 October): `decision_log.config_snapshot`
  records `config.SYMBOL`, which only `main.py` sets to the run's pair, since
  `0491b84`. `live_trading.py`'s `run_once(symbol)` and the tests pass a
  symbol without setting it, so their records say AEROUSDT. It distinguishes `run_hash`
  more, not less; it misleads a reader. Changes no trade.
- **A flat candle can be credited to the wrong volume bin** (found 18 October, read at
  `fbd7877`, by a search of the files a scoped package on Items 2, 3, 6 and 18 would
  carry, made to find a held-back defect). `indicators/volume_profile.py`,
  `compute_volume_profile`, the branch for a candle whose range is at most one
  millionth of its price, gives the candle to the bin whose nearest edge is closest.
  Neighbouring bins share an edge, so for a candle in the lower half of a bin the two
  distances tie, and the strict `<` gives it to the bin below. In the Linux sandbox,
  with ten bins of width 1: a flat candle at 4.2 landed in (3, 4] and HVN read 3.5; at
  4.7 it landed in (4, 5]. The repository's real candle files — AERO 4h and 1d, BTC 4h
  and the clean fixture — hold no flat candle. HVN can move by one bin when a flat
  candle carries a bin's volume. **Held back for Amazon's audit as H5** (DECISIONS,
  "Ruling, 18 October 2026 — the four held-back defects …"): left as it is until
  after the audit.
- **`_compute_trade_quality` takes `trend` and `final_action` and reads neither**
  (`models/decision_model.py:872`, found by the same search). Its only use of `trend`
  went at sequence item 11, as the comment inside it says; `final_action` is never
  read. Changes no number. On this list by the 22 September ruling.
- **`data/validation.py` imports `math` and never uses it** (line 121, found by the
  same search). Cleanup only. On this list by the 22 September ruling.
- **`plot_engine_chart` binds a loop variable it never reads** (`utils/plotting.py`,
  line 231, read at `d2dddf7`; found 18 October by the same search):
  `for i, (target, label, color) in enumerate(…)` never reads `i`. Cleanup only;
  `code_hash` moves, since the file is fingerprinted. The ruling of 18 October named it
  among the search's results and did not put it on the list; added on 19 October by the
  22 September ruling, with 45 (DECISIONS, "Ruling, 19 October 2026 — the list for
  after the audit, sorted …").
- **BTC structure's degradations are neither recorded nor logged** (found 20 October,
  landing entry 21; read at `391c338`). The BTC block in `core/engine_core.py` calls
  `calculate_structure` on BTC's frame and passes its regime, sequence and volume
  sentiment to BTC's bias, but never reads its `degraded_inputs`, and
  `structure/structure.py` has no logger. So a BTC structure sub-routine that fails
  hands BTC's bias its UNKNOWN reading with nothing recorded and nothing logged. The
  asset's own structure failures are recorded (`degradation.extend` on
  `structure_obj`'s list). Reference only: BTC changes no trade (N5). Not changed.
  Entry 47; not in the sort of 19 October. Claude's suggestion, his to change: record,
  Viktor (shape), S, wave 2, with 33.
- **`test_the_location_check_can_fail` reads `models/risk_model.py` from the working
  tree** (`tests/test_send_round8_fix_verification.py`; found 20 October, landing entry
  28). It needs `stop_mult = ATR_STOP_MULT * vol_multiplier` at line 400, so any change
  that adds or removes a line above it fails the suite — the first build of entry 28's
  change added four docstring lines and failed it (1 failed on all three runs, in the
  sandbox). Its neighbour, the citation check, reads the file from the commit that last
  changed the instruction, and holds. Changes no engine code. Entry 48; not in the sort.
  Claude's suggestion, his to change: test gap, Claude, XS, wave 1 — and before any
  wave 2 change to `models/risk_model.py`. **20 October: changed**, by `ed005a0`: the
  test reads the file through `_instruction_tree()`, the reader its
  neighbour uses, so the two read the same tree — the commit that last changed the
  instruction once it is committed and unchanged, the working tree before. A line added
  above line 400 in the working tree fails the old test and not the new one; with the
  instruction also changed in the working tree, both tests read the working tree and
  both fail (Linux sandbox).
- **`conftest.ENGINE_MODULES` is not every module in the engine** (found 20 October,
  writing entry 37's controls; read at `e88e0dd`). Its comment says "Every module in the
  engine"; its 21 leave out `core.code_fingerprint`, `core.lineage` and
  `utils.decision_log_backup`, added on 6, 2 and 12 September. `test_every_module_imports`
  imports only the list, so an error at module level in those three is caught only where
  something else imports them: `core/engine_core.py` the first two, and each has a test
  file that imports it (a text search). The execution scans read all three, as they
  walk the tree; their new coverage control, anchored on the list, does not require
  them. Changes no engine code. Entry 49; not in the sort. Claude's suggestion, his to
  change: test gap, Claude, XS, wave 1.
  **24 October: changed**, by `ad34c02`, at Viktor's go:
  `ENGINE_MODULES` names the three, so `test_every_module_imports` imports 24 modules
  where it imported 21, and `test_engine_modules_is_every_module_in_the_tree`, new,
  holds the list to the tree: every `.py` file `core/code_fingerprint.py` reads for
  `code_hash` must be a module the list names, a package marker with no statement in it
  but a docstring, or one of the two scripts `conftest.NOT_ENGINE_MODULES` names with its
  reason, `run_tests.py` and `test_live.py`; and every name in either list must be a
  file. Against the list as it was, the new test fails naming exactly the three. With
  an error raised at module level in `utils/decision_log_backup.py`, the import check
  passed at `34d8e3b` and fails now, naming it; with one in `core/code_fingerprint.py`,
  without `pandas_ta`, the same. The two modules the import check excuses without
  `pandas_ta` are still `core.engine_core` and `indicators.indicators` (Linux sandbox).
- **`README.md` writes the watched error count** (found 20 October, landing entry 37).
  Its Tests row and its "All tests currently pass" paragraph give `run_tests.py`'s
  errors as a number, where the ruling of 15 October has them written only in this file
  (point 5, which named `run_tests.py`'s docstring and three test files, not README);
  and the paragraph says the count stays flat "except when a new fixture-using test is
  added on purpose", which a test made fixture-free, as entry 37's was, also moves.
  Entry 37's commit set both numbers to 31 with the other counts. Docs only. Entry 50;
  not in the sort. Claude's suggestion, his to change: docs, Viktor (shape) — point 5
  was his — XS, wave 1.
- **The suite's file walk and `code_hash`'s exclude different directories** (found
  24 October, landing entry 49; read at `34d8e3b`). `conftest.all_python_files` skips
  `.git`, `__pycache__`, `tests`, `Logs`, `logs`, `aider-env`, `.venv` and `venv`, and
  `docs` when asked to; `core/code_fingerprint.py`'s `EXCLUDED_DIR_NAMES` also skips
  `.pytest_cache`, `env`, `Backup` and `Claude outputs`. So a `.py` file under `env/`,
  `Backup/` or `Claude outputs/` is read by every test that walks the tree through the
  first — in `tests/test_imports.py`, `tests/test_execution_surface.py`,
  `tests/test_no_lookahead.py`, `tests/test_explicit_configuration.py` and
  `tests/test_risk_verdict_is_read_not_assumed.py` — and is not the engine by the
  second, the one entry 49's test uses: two lists of the same directories, drifted apart
  (rule 11). In the repository no directory of those four names holds a `.py` file, and
  on Viktor's disk none does outside `docs/` (his folders listed on 24 October); the
  two walks give the same files at `34d8e3b` (Linux sandbox), so nothing is read
  differently today. A virtualenv made as `env/` inside the repository would be walked
  by the suite. Changes no engine code. Entry 51; not in the sort. Claude's suggestion,
  his to change: test gap, Claude, XS, wave 1 — the suite's walk taking `code_hash`'s
  exclusions, with `docs/` added back for the compile check.
  **25 October: changed**, by `b387c03`, at Viktor's go:
  `all_python_files` takes `core.code_fingerprint.EXCLUDED_DIR_NAMES` when it is
  called, and gives `docs/` back to the compile check alone, so without the flag it
  reads exactly the files `code_hash` reads. Building it found a second walk of the
  engine with a list of its own, `test_no_engine_module_calls_utcnow` in
  `tests/test_no_fabricated_defaults_remain.py`, which skipped five fewer directories
  than `code_hash` — `.pytest_cache`, `env`, `aider-env`, `Backup` and
  `Claude outputs` — and it walks the tree through `all_python_files` now: the same
  defect, fixed with it (Claude's call, said before building). The new
  `test_the_suite_walks_the_files_code_hash_reads` builds a tree with a `.py` file in a
  directory of every name `code_hash` excludes, at the top, under `core/` and under
  `docs/`, and holds both of the suite's walks to `code_hash`'s on it and on the
  repository. Against the list as it was, it fails naming exactly the files under
  `.pytest_cache/`, `env/`, `Backup/` and `Claude outputs/`; with a name added to
  `code_hash`'s list it passes, and with that and a copy of today's list in
  `conftest.py` it fails naming the new name. A `.py` file with a syntax error under
  `Claude outputs/`, `Backup/` or `docs/Claude outputs/` failed the compile check and
  does not now; one under `docs/build/` fails it as before (Linux sandbox). Read and
  left: `tests/test_clean_checkout.py`'s copy list, which decides what a fresh clone's
  copy holds, not what the engine is, and `tests/test_main_takes_pairs.py`'s list of
  the engine's packages to copy, whose miss would fail its import. In the repository
  and on Viktor's disk, listed on 25 October, no `.py` file sits in a directory a walk
  now skips that it read before, so every walk reads the files it read: 33 for the
  engine, 55 with `docs/`.
- **The entry score's trend multiplier rewards agreement with itself** (found
  25 October, filing that day's rulings; read at `ad34c02`). `calculate_entry_quality`
  multiplies the score by 1.05 when the trade's direction agrees with trend health's
  EMA-slope direction label and by 0.90 when it opposes it
  (`models/entry_model.py:395–407`); the direction comes from that slope on 99.6% of
  the bars with a side (version 2, measured), and an entry score of 70 is the line
  between LONG and CONSERVATIVE LONG (`models/decision_model.py:485`, `718`, `746`).
  Removing it changed the tier on 61 of 2,970 bars in version 2's decision-impact test,
  never whether the engine traded. Rated Critical, a break of Tier 1 Item 11, by Claude
  under Viktor's delegation (DECISIONS, "Decision, 25 October 2026 — the trend
  multiplier is Critical, by F4's precedent"). Entry 52; fixed within entry 53 (ruling
  5): weighting, ruled, M, wave 4.
- **The redesign of 25 October** (DECISIONS, "Ruling, 25 October 2026 — the engine's
  indicators …"). One change: the EMA slope as the one direction source, with ADX, the
  structure regime and divergence as gates; continuation removed and volume sentiment
  out of the decision; SuperTrend as Exit Watch only; macro a gate on LONG only, out of
  the bias, the entry score and the validation score; trend health and its tiers
  removed, the tier from entry quality; entry quality as distance from the EMA band's
  middle in ATRs and HVN nearness, RSI in the divergence gate only, the trend and macro
  multipliers removed; confidence and the EV line dropped; `bias_score`'s weighting,
  and the HVN uses the confirmation of 27 September put with it, in the same change. It
  settles entries 11, 12 and 15, takes 14 and 19 into its scope (Claude's reading, his
  to change) and fixes entry 52. Its design — the ladder, the gates, the weights, and
  the strength floor the ruling of 5 September ("a lean is not a case") needs once the
  weighted sum is gone — is put to Viktor before it is built, with the tests and golden
  fields each part would move. The held-back defects it reaches: DECISIONS, "Decision,
  25 October 2026 — the held-back defects …". Entry 53: trading rules, Viktor (ruled;
  its design his to rule), L, wave 4, after the reading of 14 November and before the
  send.
- **The audit package's list of what is not the engine is its own** (found
  25 October, landing entry 51; read at `89d2367`). `docs/build/build_audit_package.py`
  walks the tree for the engine and test bundles an auditor reads, skipping its own
  `EXCLUDED_DIRS` — `docs`, `logs`, `.git`, `__pycache__`, `.pytest_cache`, `.venv`,
  `venv` and `node_modules` — where `code_hash` skips `core/code_fingerprint.py`'s
  `EXCLUDED_DIR_NAMES`. So a `.py` file under `Logs/`, `env/`, `aider-env/`, `Backup/`
  or `Claude outputs/` would go into the package as the engine, and is not the engine
  in any decision record; one under `node_modules/` is the engine to `code_hash` and
  would be left out. The same shape as entry 51, outside the suite (rule 11);
  `docs/build/send_round8_fix_verification.py` already reads `EXCLUDED_DIR_NAMES` from
  the module. No such file is in the repository or, listed on 25 October, on Viktor's
  disk, so the package is the same today. Changes no engine code. Entry 54; not in the
  sort. Claude's suggestion, his to change: audit tooling, Claude's under the
  delegation of 4 October, XS, wave 1 — before the package for Amazon is built.
  **26 October: changed**, by `9862568`, at Viktor's go: the
  engine bundle is `code_hash`'s own walk, `iter_source_files`, less `run_tests.py`
  and `test_live.py`, which `code_hash` reads and the package puts with the tests on
  purpose; the test bundle is those two and every `.py` under `tests/` in no directory
  `code_hash` skips, `tests` apart; both are read from the packaged tree's
  `core/code_fingerprint.py`, loaded by its path, when the bundles are made, and
  `EXCLUDED_DIRS` is gone. The new
  `tests/test_send_audit_round.py::test_the_package_reads_the_engine_code_hash_reads`
  builds a tree with a `.py` file in a directory of every name `code_hash` skips, at
  the top, under `core/` and under `tests/`, and holds both bundles to `code_hash`'s
  walk on it and on the repository. Against the script as it was, it fails naming
  exactly the files under `Logs/`, `env/`, `aider-env/`, `Backup/` and
  `Claude outputs/` at the top and under `core/`, and the one under `core/tests/`, in
  the engine bundle; `node_modules/` missing from it; the five under `tests/` in the
  test bundle; and the order. Called directly, the old script put a `.py` file under
  `Claude outputs/`, `env/` or `Backup/` in the engine bundle and one under
  `tests/Backup/` in the test bundle, and left one under `node_modules/` out; the new
  one puts the first four in neither bundle and the last in the engine bundle (Linux
  sandbox). The engine bundle's files are now sorted by path: `live_trading.py` and
  `main.py` move from after `__init__.py` to after `indicators/`. In the repository
  and on Viktor's disk, listed on 26 October, the bundles read the same 31 and 94 files
  they read.
- **The engine bundle's header says its files follow in path order, and its project
  files do not** (found 26 October, landing entry 54; read at `b387c03`).
  `build_audit_package.py`'s `_bundle` writes "N files follow, in path order" above
  each bundle. The engine bundle holds the engine's modules, sorted, and after them the
  five project files — `pytest.ini`, `requirements.txt`, `requirements-dev.txt`,
  `.gitattributes` and `.gitignore`, in that order — so the bundle as a whole is not in
  path order. A small untrue sentence in what an auditor reads about its own material,
  of the kind `_bundle`'s own comment calls "a small dishonesty" when it keeps the
  delimiter out of the header. Changes no engine code. Entry 55; not in the sort.
  Claude's suggestion, his to change: audit tooling, Claude's under the delegation of
  4 October, XS, wave 1 — before the package for Amazon is built.
  **26 October: changed**, by `3d7e6cb`, at Viktor's go:
  `_bundle` takes the files that go first, which it refuses unless they are sorted by
  path, and `then`, files that follow them in the order given, and makes the header's
  sentence about the order from the two: the engine bundle's now reads "N files follow:
  the first K in path order, then `pytest.ini`, `requirements.txt`,
  `requirements-dev.txt`, `.gitattributes` and `.gitignore`, in that order", and the
  test bundle's is unchanged. The files, their order and their hashes in the manifest
  are unchanged; `main()` passes the project files as `then`. The new
  `tests/test_send_audit_round.py::test_each_bundle_says_the_order_its_files_follow_in`
  builds both bundles as `main()` does, from the repository, and reads each header
  against the files that follow it; and the call that wrote the untrue header, the
  modules and the project files as one list, is refused. Against the script as it was,
  it fails on that call, which the old `_bundle` took. Kept, not changed: the order
  itself — the engine's modules first, then the files that build and pin them — and
  the bundles already sent, which are records (Linux sandbox).

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
- **The fixes of 5 October**, in Claude's order (DECISIONS, "Ruling, 5 October 2026 —
  round 8 triaged …", "The order of the work"). Each is its own commit, bringing this
  file and `docs/audit_change_list.md` current in it:
  1. **The stop — done at `c2b07fb`.** ATR × 1.2 × the volatility factor (point 1);
     `trend_health` no longer a parameter; the comment beside `lineage.risk_inputs`
     true, and its contract's docstring corrected (F1). The live run and its record
     came before the commit. It moved `code_hash`, `run_hash` and the golden snapshot,
     as predicted.
  2. **No trend, no trade — done at `1b25f36`.** ADX under 20
     blocks both sides in the confirmation gate, with the reason printed, replacing the
     exhaustion flag (point 4); `MIN_TREND_ADX` (20.0) is fingerprinted. An ADX with no
     valid reading — `None`, NaN, an infinity, not a number, or outside 0–100 — blocks
     both sides too, failing safe: the patch's proposal, which the ruling left to it,
     Viktor's to reverse. On a degraded run whose ladder chose a side, that makes the
     label NO-TRADE (SIGNAL UNCONFIRMED), where it was NO-TRADE (DEGRADED INPUT). The
     flag itself still feeds the reversal reading, the trend-regime label and Exit
     Watch. The live run and its record came before the commit. It moved `code_hash`,
     `run_hash` and the golden snapshot, as predicted.
  3. **The regime from volatility alone — done at `fcb7823`.**
     `classify_risk_regime` reads the volatility state and the stop distance, nothing
     else (point 3; round 8's F2, the review's B8): EXTREME VOLATILITY or a stop over 8%
     is EXTREME RISK, HIGH VOLATILITY is HIGH VOLATILITY RISK, MEDIUM VOLATILITY is
     NORMAL RISK, and LOW VOLATILITY is LOW RISK — the mapping the ruling left to the
     patch, as the ruling named Claude's reading. Any other state is UNKNOWN RISK, where
     it fell through to NORMAL RISK: the patch's proposal, Viktor's to reverse. UNKNOWN
     RISK keeps AGGRESSIVE out, decides nothing else, and is unreachable on the engine's
     path today. `REGIME_CHOP_ADX` and `REGIME_STRONG_ADX` are gone;
     `validate_risk_parameters` takes no `adx`, no `**kwargs` and no default state, so a
     stale or misspelt keyword is refused by Python; `lineage.risk_inputs` no longer
     records ADX. Every risk verdict in the live log replays the same on both codes. The
     live run and its record came before the commit. It moved `code_hash`, `run_hash`
     and the golden snapshot, as predicted. Labels only: since fix 2 no run under ADX 20
     trades.
  4. **The label and record batch** (points 6, 7 and 8), one small patch at a time:
     test runs in a log, archive and state of their own (B6) — **done at `9e507b1`**;
     the BTC-adjusted confidence line (N5) — **done at `6469a67`**; a frame with no
     readable time axis (F3) — **done at `ae37795`**; the band distance (F5) — **done
     at `9d00d99`**; `clean_series`'s look-ahead method (F6) — **done at `27d3ed5`**;
     one name for one meaning (F8) — **done at `9051ffd`**; four claims the code did
     not support (F9) — **done at `e5ac20a`**; the 12 October additions, in the order
     ruled on 13 October: patch 1, the fallback sweep — **done at `797bdc9`** — and
     patch 2, the two repeated readings (the REGIME line and the STRUCTURE line's Vol
     field go) — **done at `69c92d6`**; B4's labels — **done at `22a9a35`**; B7 —
     **done at `d77a8c4`**; B9 — **done at `64ad625`**, all but its Bitcoin SuperTrend
     already at `797bdc9`; B10 — **done at `9ea1cf3`**; and the three test shapes of
     round 8's Part 4, as one patch (ruled 15 October) — **done at `f00bef6`**, with the second shape's sibling, which Part 4 named in the same
     sentence. **The batch is done.**
     **B6:** the run's source is read once per run (`_is_live_run`: live only when no
     pinned source is set), and a live run's state, archive and log stay exactly where
     they were, in `config.LOG_DIR`; any other run's go to its `pinned/` subdirectory
     (`decision_log.records_dir`). The decision log is chosen from the record itself:
     only a record whose provenance says live in both places — `fetch.pinned` False and
     `source` the endpoint — goes in the live log, so a record that does not say, a
     hand-built one included, is kept out (failing safe), and a directory passed to
     `write()` does not override it. A `PHASE7_PINNED_DATA` that names no directory is
     not a live run; the run fails at its fetch as before and writes nothing. Each
     source prunes its own archives. The patch's proposals, Viktor's to reverse. The
     audit-package builder now redacts its temp directory in both spellings, which the
     forward-slash pinned path needs on Windows. Not changed, and not named by the
     ruling: the chart, `phase7_engine.log` and `logs/LiveSim/` (Open items). The ten
     test records stay in the live log, as ruled. The live run and its record came
     before the commit. It moved `code_hash` and the golden snapshot's three paths, as
     predicted; `run_hash` did not move.
     **N5:** the panel's BTC-ADJUSTED CONFIDENCE line goes, and with it, as the patch
     proposes — the reading the ruling named as Claude's — everything that existed only
     for it: `DecisionModel._compute_btc_adjusted` and its constants
     `BTC_ADJUSTMENT_CAP` and `BTC_STRESS_PENALTY`; `evaluate()`'s `btc_context` and
     `symbol` parameters, which only it read (a caller still passing either gets a
     TypeError; the `*` before `degradation` stays); the BTC block's
     `btc_adjusted_confidence` and `reasons`, in the router's merge and the contract;
     the panel's validation-status line under the number and the adjustment's sentence;
     and the BTC bias `score` engine_core put in the block for it alone. The BTC section
     keeps BTC BIAS, BTC REGIME, CORRELATION, BTC SENSITIVITY and BROAD MARKET STRESS.
     The block is now available whenever engine_core measured BTC; it also needed the
     adjustment to have been computed, and an adjustment that raised made the whole
     section unavailable (no such failure in the engine log's lines from 6 September to
     6 October). The patch's proposals, Viktor's to reverse. It changes no decision:
     the number was computed after every decision and nothing that decides read it, and
     the 38 run archives on Viktor's disk, replayed through the code before and after,
     differ only in the removed fields and what `run_hash` names. The live run and its
     record came before the commit. It moved `code_hash`, `run_hash` and the golden
     snapshot, as predicted.
     **F3:** `validate_ohlcv` rejects a frame with neither a DatetimeIndex nor a
     `timestamp` column ("no time axis"), where it returned None and skipped every check
     on time: missing candles, duplicates, order, spacing, future-dated, forming and
     stale data. As the patch proposes — Viktor's to reverse — two neighbours of the
     same defect go with it: a `timestamp` column that cannot be read as epoch
     milliseconds ("unreadable time axis"), also accepted until now, and a missing
     timestamp (NaT), already rejected but named as "not in increasing order" at the
     wrong index. `_load_pinned`'s own column check is left as it is: the validator
     runs before it. **The auditor's reproduction was run, and its account of the
     outcome was wrong.** It said an untimed copy of `AEROUSDT_4h.csv` gives a full
     panel and a decision record whose decision candle is the row number 419. Run on
     `6469a67` and on `e186423` (Linux, Python 3.12.3), the run passes validation and
     the indicators, then crashes in `Phase7Engine._decision_candle` (`int +
     Timedelta`): the pipeline's generic "Critical error", no record written. The gap
     was real; the refusal was an accident one frame further on, with an error naming
     neither the file nor the defect. Now the run stops at the fetch with the
     validator's reason. Not changed: on the pinned path staleness is not checked at
     all, by the ruling of 30 August (a file is historical, not stale), so F3's "data
     five years stale analysed as current" describes that ruling, not this gap; and a
     timeframe the bar-length table does not list still skips spacing and staleness
     (finding 26, deliberate; the engine's 4h and 1d are listed). Changes no decision:
     every frame on the engine's path has a time axis. The live run and its record
     came before the commit. It moved `code_hash`; `run_hash` and the golden snapshot
     did not move, as predicted.
     **F5:** the BAND DISTANCE line reads "x% from the band's midpoint", where it read
     "x% away from the band". `distance_from_zone` is the distance from the band's
     midpoint as a percentage of the close; with the close inside the band the old line
     printed a positive distance "away from the band" under STATUS : ACTIVE ENTRY ZONE
     — 1.40% on the real run of 30 September (the review's reproduction; run again in
     the sandbox on the same numbers). The repair is Claude's, as the review's Part D
     lists it, and Viktor's to reverse: the label is changed, not the number. An edge
     distance (zero inside the band) would change what the record's key means between
     one record and the next, and nothing decides on the printed figure. The definition
     is now written beside the number in `models/entry_model.py` and the field in
     `core/decision_contract.py` (comments). Not changed, and not F5: STATUS reads
     ACTIVE ENTRY ZONE whenever the close is within one band-width of the midpoint,
     which reaches half a band-width outside the band on each side — a decision-path
     question, on the list for after the audit (Found after 22 September). Changes no
     decision. The live run and its record came before the commit. It moved
     `code_hash`; `run_hash` and the golden snapshot did not move, as predicted.
     **F6:** `clean_series` accepts two methods, `forward_fill` and `fill_value`; any
     other name raises ValueError, and so does `fill_value` without a number. Removed:
     `interpolate`, a linear interpolation that filled an interior gap from the next
     valid row — a bar in its future (Item 2) — and carried the last value across the
     trailing edge that the forward-fill branch refuses to fill (finding 3); and `drop`,
     unused (Item 16), which returned a series shorter than the frame. No caller outside
     `tests/` used either. Until now an unknown name, or `fill_value` without a number,
     fell through every branch and returned the series with only inf turned to NaN. The
     raises and the removal of `drop` are the patch's proposals, Viktor's to reverse;
     `fill_value` stays, the substitution item 15 kept on purpose (its test in
     `tests/test_no_lookahead.py`). **The auditor's claim that
     `tests/test_no_lookahead.py` cannot see the branch was checked and is right:** it
     calls only `forward_fill` and `fill_value`. Not changed: whether a gap at the last
     row is refused depends on whether a later row exists — not a value from the future,
     but a difference between a backtest and the live engine (Found after 22 September).
     Changes no decision: every call on the engine's path is `forward_fill`, unchanged.
     The live run and its record came before the commit. It moved `code_hash`;
     `run_hash` and the golden snapshot did not move, as predicted.
     **F8:** "VWMA" means one calculation. `_volume_sentiment_simple`
     (`structure/structure.py`) called its two 5-candle volume-weighted means of the
     close, and their difference, `vwma_recent`, `vwma_prev` and `vwma_slope`; the
     engine's VWMA is `indicators/indicators.py`'s 20-candle rolling ratio, scored by
     `entry_model` as "VWMA Distance". Renamed `vw_mean_recent`, `vw_mean_prev` and
     `vw_mean_slope`, and the docstring says what the slope is and that it is not the
     VWMA. Every value is the same: the parse tree, the names mapped back, equals the old
     one, and on every window of the four fixture CSVs (1,434) the old and new function
     return the same label. No name containing "vwma" was printed or recorded, so no
     record, label or note changes. The panel printed `momentum_mode` twice — after the
     slash on the TREND line and as the whole MOMENTUM line (item 11 had taken the
     line's number off and kept the line for its label, which TREND already printed).
     The MOMENTUM line is removed; TREND keeps both readings. Which line goes is the
     patch's proposal, Viktor's to reverse. Not changed: the word after TREND's slash
     carries no name of its own on the panel. Changes no decision. The live run and its
     record came before the commit. It moved `code_hash`; `run_hash` and the golden
     snapshot did not move, as predicted.
     **F9:** four statements the code beside them did not support (Item 8), and the
     labels of the same kind ruled in with them on 12 October. (1) `StructureEngine`
     kept `_last_regime` "for regime persistence to reduce whipsaws" and persisted
     nothing: `calculate_structure` builds a fresh engine per call, so the regime always
     started from NEUTRAL STRUCTURE and the two hysteresis branches ran only for a reused
     instance, which nothing builds. `_detect_regime` is now a plain function of the
     frame — option C, as for finding 18 — and returns what the engine's path got
     before: 20,436 frames, old against new, no difference.
     `REGIME_HYSTERESIS_THRESHOLD` keeps its name, and its comment says it is a dead
     band. A frame under 15 rows reads UNKNOWN STRUCTURE, where it read the stored
     NEUTRAL STRUCTURE; still an ordinary return, not a degradation. (2)
     `compute_trend_health`'s failure labels `momentum_mode`, `trend_regime` and
     `trend_direction` were NEUTRAL; they are UNAVAILABLE. Reachable when both EMA slope
     columns are missing, which an indicator failure causes. The entry score is
     unchanged: the multiplier is 1.0 for every label but BULLISH and BEARISH, tested.
     (3) `volume_agreement` reported UNKNOWN VOLUME — a failed read — as "Volume
     sentiment is neutral."; it now says the reading could not be taken, with the same
     score, 0.0. (4) The ADX failure note claimed "25 of its 100 points" and "bias cannot
     test trend strength": the component is worth up to 40 (measured by the test, not
     written into it), bias has read no ADX of its own since 19 September, and the note
     left out that no trade is taken without an ADX reading (fix 2). Round 5 reported
     the "25" on 12 September, and it was not fixed then. The panel's TREND line fell
     back to NEUTRAL / HEALTHY for a missing label; it cannot fire on the engine's path
     (the router writes both keys on every decision it builds), and it now falls back to
     UNKNOWN, the router's own word. Two comments in `models/bias_engine.py` that
     described the regime as "with hysteresis" now say dead band. The wording of every
     new label and note is the patch's proposal, Viktor's to reverse. Changes no
     decision. The live run and its record came before the commit. It moved
     `code_hash`; `run_hash` and the golden snapshot did not move, as predicted.
     **The fallback sweep** (patch 1 of the 12 October additions): every default in
     `core/panel_render.py` and in the router's decision-building code is listed in
     `tests/test_an_absent_value_is_not_a_reading.py` with the reason it is allowed, and
     a default added or removed in either file fails it. Those that were readings are
     changed under the ruling of 13 October. The panel: BIAS, REGIME, STRUCTURE, Vol,
     SEQUENCE, VOLUME, VALIDATION, VOLATILITY, RISK REGIME, MACRO TREND, STATUS,
     DECISION, the timeframe and the three BTC lines fall back to UNKNOWN, UNKNOWN
     STRUCTURE, UNKNOWN VOLUME or UNKNOWN RISK, the router's own words; BROAD MARKET
     STRESS prints UNKNOWN for an absent flag, where it printed "No"; an absent exit
     watch says it was not computed, where it said no flags were active. The router:
     every section of the engine's output is read by subscript, macro_bias apart (it
     falls back to UNKNOWN); the two trend booleans, the two signals and
     `score_clipped` are read directly; the entry score, its sub-scores and
     reconciliation, and the three EV fields go through `_finite_or_nan`; STATUS's twin
     falls back to UNKNOWN and the correlation label to NOT MEASURED; a Bitcoin block
     missing a boolean or list is unavailable, not an error for the asset.
     `engine_core`: `trend_direction` into the entry score, `reversal_strength` into
     both bias calls, and the BTC call's sequence, regime and volume sentiment are read
     directly. None of these could fire on the engine's path. The 30 tests in six files
     whose hand-built inputs left a now-direct key out are given exactly the value the
     router used to invent. What the patch read into the rule is Claude's, Viktor's to
     reverse (the ruling's entry). Changes no decision: on the golden fixture the
     decision object and the 86-line panel are identical before and after. The live run
     and its record came before the commit. It moved `code_hash`; `run_hash` and the
     golden snapshot did not move, as predicted.
     **B9:** the self-review's B9 named a router default and four BTC defaults. The
     fallback sweep made the router's (STATUS's twin falls back to UNKNOWN) and three of
     the BTC call's (sequence, regime and volume sentiment, read directly) at `797bdc9`,
     without naming B9 (DECISIONS, "Ruling, 15 October 2026 — B9: Bitcoin's SuperTrend
     is read directly", Claude's errors). The fourth, Bitcoin's SuperTrend direction, is
     read by subscript at `64ad625`: a failed BTC SuperTrend
     leaves no column, and the KeyError ends in the BTC block's own handler, which
     reports BTC unavailable for the run, as for any BTC failure — where 0.0 made BTC's
     bias count a neutral SuperTrend and the panel printed BTC BIAS one factor short. The
     asset's own read keeps its 0.0 (Found after 22 September). Changes no decision:
     Bitcoin is reference only, and the new tests hold the asset's own sections equal to
     a healthy run's. The live run and its record came before the commit. It moved
     `code_hash`; `run_hash` and the golden snapshot did not move, as predicted.
     **B10:** the self-review's B10 named two outputs. The simulated order recorded the
     band between the two EMAs as `entry_zone`, which finding 4 made a reference, not
     the entry: since `9ea1cf3` it is `ema_band`, the panel's label,
     with the same values, and the order's entry stays `current_price`, the decision
     close under the decision log's own name. Exit Watch's note naming Target 1 printed
     on a WAIT or a NO-TRADE under a leaning bias, naming the target of a plan the
     engine did not suggest: the panel now prints it only when the action names a side,
     the test `models/decision_model.py` makes of its own action, so WAIT, every
     NO-TRADE and an absent action withhold it. Panel only, as for finding 5: the
     decision object and the log keep the note, and the plan's stop and targets still
     print under a leaning bias. Rendered from the live log's 62 records on both codes,
     44 panels lose the note line and nothing else (35 live runs, 9 pinned), 33 of them
     then saying no flag is active; the other 18 are identical. Changes no decision.
     The live run and its record came before the commit. It moved `code_hash`;
     `run_hash` and the golden snapshot did not move, as predicted.
     **Part 4's three test shapes:** the golden coverage test printed SKIP and
     returned when its baseline was missing, a pass; it now fails then, as the snapshot
     comparison does, and runs without `pandas_ta`, since it reads only the stored
     file. The non-finite test checked only that `math.isfinite` appeared in the
     panel's source; it now renders the golden decision — a CONSERVATIVE LONG, so the
     plan prints — with each of its 120 float fields set to +inf, -inf and NaN in turn,
     360 renders, and fails if a line prints nan, inf or infinity or a render returns no
     panel. Seven of the panel's guards, each removed alone, fail it; the test it
     replaces passed under all seven. Its sibling checked that "SuperTrend's level"
     appeared in the source; it now runs the guard with the level blanked at the
     decision bar. The final sweep drops the level even without its guard, so what the
     test asserts is that SuperTrend fails whole and its direction is not written. The
     watched error count is no longer written as a number in `run_tests.py`'s docstring
     or the three test files that gave one; each points to "Where things stand, right
     now". Tests and a docstring only: `code_hash`, `run_hash` and the golden snapshot
     did not move, as predicted, so there was no live run.
  5. **The fix verification** by round 8's auditor — Claude's, under the delegation of
     4 October. **Decided at `36de35d`** (DECISIONS, "Decision,
     16 October 2026 — round 8's fix verification: what is checked, what is sent, and
     to whom"): the 14 September precedent's form, with the package close to full size
     because the fixes touched 17 of the 33 engine files. Next, its second patch: the
     send script pinned to MiMo, its tests and the instruction, with the package
     measured by MiMo's own tokenizer. Then the tag and the send, Viktor's commands.
     The release gate reopens only on its report (point 2), once Viktor accepts it.
     **Its tooling landed at `78ea37d`** (DECISIONS, "Decision, 17 October 2026 — the
     fix verification's tooling"): the send script, pinned to MiMo on Xiaomi's
     endpoint, its instruction and 25 tests. Measured with MiMo's tokenizer: 341,082
     prompt tokens, 576,422 to spare. **Sent and answered on 17 October; its report
     filed at `d3188f2`** (DECISIONS, "Fix verification, 17 October 2026 — …"): the
     stop's fix holds, no new Critical, every fix fixed, no new defect. No second run.
     **Accepted by Viktor the same day, by agreeing to Claude's suggestion** (DECISIONS,
     "Ruling, 17 October 2026 — …"): on A.1 alone, B–F triaged, noted, no action. The
     release gate is open again. Done.

## Resolved this session

- **`3d7e6cb`'s landing**, read off Viktor's disk and GitHub again, with the times
  Claude had read off them after the push, in chat ("Where the project is", the session
  of 26 October, from 16:51, and this session). Every part that could be read again
  held; the two that could not are named there.
- **Entry 26** — Goal B keeps a candle only once it has closed at `t`, by the commit
  that writes this line ("Found after 22 September"; DECISIONS, "Decision, 26 October
  2026 — Goal B keeps a candle only once it has closed at `t` (entry 26)"): Claude's
  under Viktor's delegation of 19:02 on 26 October, his to reverse.
- **The once-per-session rewrite of this file**, by the commit that writes this line.
  The previous version, as at `3d7e6cb`, is in HISTORY verbatim, headings demoted one
  level, proven by un-demotion with a negative control (the commit message has the
  result).

## Open items

Items marked **Viktor's call** are his to decide; he writes his position first and
Claude critiques it.

- **Owed to the next commit:** nothing, unless this commit's push deviates from its
  prediction (ruling on proposal (b), 27 September).
- **Wave 1 — what is left.** Its test gaps have landed: entry 48 at `ed005a0`, 36 at
  `e88e0dd`, 37 at `d508b29`, 49, found landing 37, at `ad34c02`, and 51, found
  landing 49, at `b387c03`; entry 54, found landing 51, audit tooling, at `9862568`;
  and entry 55, found landing 54, audit tooling, at `3d7e6cb`. Landing 55 found no
  entry more. Of wave 1, what this file names as Claude's has landed. Entry 26, one of
  Goal B's two rulings, was decided by Claude under Viktor's delegation of 26 October
  (DECISIONS, "Decision, 26 October 2026 — Goal B keeps a candle only once it has
  closed at `t` (entry 26)"), his to reverse.
  **Viktor's, position first:** entry 31, Goal B's other ruling, docs only; entry 50's
  shape (docs, found landing 37); and entry 47's place in the sort, if he changes
  Claude's suggestion.
- **The engine's indicators — the document of 24 October** (outside the repository,
  "Where the project is"). Version 2's section 6 questions were ruled on 25 October
  (Ruled — in force); the redesign is entry 53, the next item. **The tooling landed**
  with `d410bfa`:
  `docs/build/indicator_overlap.py`, run as `python
  docs/build/indicator_overlap.py logs/archive --logs logs`, and
  `tests/test_indicator_overlap_tool.py`, which checks its statistics, that its baseline
  reproduces the golden decision, that it reads no candle after the bar it judges, and
  that it restores the bias weights it changes. Building it found one error in the
  scripts behind version 2: macro read the daily candles closed by the bar's open, not
  its close, so it left out the daily candle that closes with a 20:00 bar. With the
  engine's rule every figure moves a little and no conclusion changes: 2,980 bars where
  version 2 has 2,970, trade actions 1,333 to 860 with the four disputed factors removed
  and today's cutoffs (−35.5%) where it has 1,324 to 841 (−37%), and the baseline
  matching the logged action on 197 of 197 records where it has 196 of 196 (Linux
  sandbox, 24 October). Version 2 is not corrected; the tool's docstring records it.
  What the test found, in short: removing any of the four
  disputed bias factors never flipped the side on any bar; removing all four with
  today's cutoffs cut the trade actions by 35.5% (the tool's figure); its baseline
  matched the engine's own logged action on all 197 non-degraded live records it could
  be compared with.
- **The redesign, entry 53 — owed before it is built**, after the reading of
  14 November (DECISIONS, "Ruling, 25 October 2026 — the engine's indicators …"): its
  design put to Viktor — the decision ladder, the gates, entry quality's weights, and
  the strength floor the ruling of 5 September ("a lean is not a case", as the
  AI-Attribution Statement records it) needs once the weighted sum is gone — with the
  tests and golden fields each part would move; the HVN uses the confirmation of
  27 September put with the weighting, not read on 25 October; and, once the design is
  fixed, H1's replacement, and H2 and H5 judged against it, replacements proposed by
  Claude for Viktor to accept (DECISIONS, "Decision, 25 October 2026 — the held-back
  defects …"). Not covered by the eight: the entry score's structure multiplier
  (BOS ×1.05, CHOCH ×0.90), which stays unless Viktor rules otherwise.
- **The forward measurement — Claude's to count, under the ruling of 17 October.** Ten
  pairs — AEROUSDT, ETHUSDT, SOLUSDT, XRPUSDT, BNBUSDT, DOGEUSDT, ADAUSDT, LINKUSDT,
  AVAXUSDT, SUIUSDT — every four hours, by one Windows scheduled task on Viktor's
  machine running `pythonw.exe E:\phase7_engine\main.py` with the ten pairs. **Readings
  due 31 October and 14 November**, two and four weeks from the task's first run, from
  the decision logs and `logs/phase7_engine.log` staged off his disk: per pair and per
  `code_hash`, the closed 4h candles read, the LONG actions among them (AGGRESSIVE LONG,
  LONG, CONSERVATIVE LONG), the SHORT actions, WAIT and NO-TRADE, degraded runs, failed
  runs, and how many LONGs fell on the same candle across pairs. It answers question 5
  of 28 September as far as running forward can, and bears on 12, 13 and 14. It is
  evidence about the version whose `code_hash` is `816d4951…` until a commit moves it;
  the count of each version starts from zero. Not the paper-trading year (the ruling,
  point 6). The hand runs before `0491b84` — one per pair, and AEROUSDT once more with
  `pythonw.exe` from `C:\` — are in that commit's message.
  - **The task**, created by Viktor after `0491b84`'s push: `Phase7\forward
    measurement` in Windows Task Scheduler. His query of it (`schtasks /query /v`),
    pasted at 14:28 on 17 October: `pythonw.exe` from his Python 3.12 install running
    `E:\phase7_engine\main.py` with the ten pairs in the ruling's order; one schedule,
    from 14:05 on 17 October, every 4 hours, no end; interactive only, so it runs while
    he is logged in; no start on batteries, and a run on battery power stops, so a
    candle that closes while the machine runs on battery is missed, as one it sleeps
    through is; next run 18:05; last run 14:05, result 0.
    `schtasks /delete /tn "Phase7\forward measurement" /f` removes it.
  - **The first runs, checked 17 October** — Claude's, from `logs/phase7_engine.log`
    and the ten decision logs, staged off his disk at 14:20. A run that began at
    14:00:00.9 — as the candle that opened at 08:00 UTC closed — refused all ten pairs:
    "not yet final", the candle having closed 2.3 to 7.2 seconds before each fetch,
    inside the 60-second grace, by design (finding 16, `add8540`). It wrote no decision
    record, as no failed run does; the process log names each pair twice —
    `engine_core`'s "empty or None DataFrame in base market data", then `main.py`'s
    "Engine returned error for" the pair, with the reason — and ends "10 of 10 pairs
    failed". What started it is not in the logs, and Viktor does not know; it was not
    the task's schedule, which starts at 14:05, but it ran the ten pairs in the task's
    order, which `main.py` runs only when given them — with no arguments it runs
    `config.SYMBOL` alone (`parse_pairs`, read at `a48d9e5`). **It did not come back at
    the next close:** the process log goes from the 14:05 run's last line, at
    14:05:30.215, to the 18:05 run's first, at 18:05:01.300, with nothing between
    (staged off his disk at 18:46). Viktor reads the run at 14:00 as a one-off
    (17 October, 18:43). That rules out a trigger at every close; one that fires only
    at 14:00 would have shown at the 14:00 close of 18 October, but nothing ran then:
    Viktor's PC was not running (19 October, 09:08), and the process log goes from the
    10:05 run's last line, at 10:06:01.102 on 18 October, to the 02:05 run's first, at
    02:05:06.530 on 19 October, with nothing between (staged off his disk at 09:18 on
    19 October; neither run's records are read here). So the question needs a later
    14:00 close, one at which the PC is running. Viktor's PC runs day and night from
    19 October (his word, in the session from 09:08). **Read for the 14:00 close of
    19 October: nothing ran.** The process log goes from the 10:05 run's last line, at
    10:05:54.974, to the 14:05 run's first, at 14:05:02.124, with nothing between; all
    five scheduled runs of that day are in it, 02:05 to 18:05, 60 lines each, all INFO,
    every pair completed (staged off his disk after the 18:05 run, its last line at
    18:05:41; no decision record read). The log cannot show that the PC was on at
    14:00:00 itself; that rests on his word and on the 14:05 run. So a trigger that
    fires every day at 14:00 is ruled out, which fits Viktor's reading of the run of
    17 October as a one-off. One that fires weekly is not: 17 October was a Saturday,
    so it would show at 14:00 on 24 October, inside what the reading of 31 October
    reads.
    The first scheduled run, 14:05:00 to 14:05:30, read the candle that run refused and
    wrote ten records, one per pair, each its pair's own (`config.SYMBOL` and the
    decision's symbol): live from MEXC, not pinned, 449 rows, the decision candle opened
    08:00 UTC and closed 12:00 UTC, MEXC's close time 12:00 UTC (open plus one bar), one
    forming candle dropped, `code_hash` `816d4951…`. No LONG; SHORT on ADAUSDT;
    CONSERVATIVE SHORT on XRPUSDT, LINKUSDT and SUIUSDT; WAIT on AEROUSDT and AVAXUSDT;
    NO-TRADE (SIGNAL UNCONFIRMED) on ETHUSDT, SOLUSDT and BNBUSDT, and NO-TRADE
    (DEGRADED INPUT) on DOGEUSDT — the candle of 11.8 times the median volume its hand
    run met, still in the last 20. One degraded run, no failed run. The logs are
    otherwise intact: AEROUSDT's is 66 whole lines, the 63 from before 17 October (the
    last from 15 October at 11:14:51 UTC), the two hand runs and the 14:05 record; each
    other pair's is two, its hand run and its 14:05 record.
  - **The second scheduled run, checked 17 October** — Claude's, from the process log
    and the ten decision logs, staged off his disk at 18:46 and 19:12. 18:05:01.300 to
    18:05:39.445, 60 lines, all INFO: each pair started and completed, in the same
    order. Ten records, one per pair, each its pair's own: live, 449 rows, the decision
    candle opened 12:00 UTC and closed 16:00 UTC, MEXC's close time 16:00 UTC, one
    forming candle dropped, `code_hash` `816d4951…`. No LONG; SHORT on SOLUSDT and
    BNBUSDT; CONSERVATIVE SHORT on XRPUSDT, ADAUSDT, LINKUSDT, AVAXUSDT and SUIUSDT;
    WAIT on AEROUSDT; NO-TRADE (SIGNAL UNCONFIRMED) on ETHUSDT, and NO-TRADE (DEGRADED
    INPUT) on DOGEUSDT — the same 11.8-times-median volume candle, still in the last
    20. One degraded run, no failed run. AEROUSDT's log is now 67 whole lines and each
    other pair's three, the last of each from 16:05 UTC and the one before it from
    12:05 UTC.
  - **20 and 21 October** — Claude's, from `logs/phase7_engine.log`, staged off his
    disk; no decision record read. Viktor's laptop stays on with its lid closed: it
    answered over the bridge at 19:39 on 20 October, lid closed, and the 18:05 run of
    that day had written its files for all ten pairs between 18:05:03 and 18:05:29. The
    process log has a complete run, all ten pairs "successfully processed", at 22:05 on
    20 October and at 02:05, 06:05 and 10:05 on 21 October, the last ending at 10:06:10,
    and no error line on 21 October. Then nothing: the log's last write was at 10:06:10
    when it was staged at 22:54 on 21 October. **The closes of 14:00, 18:00 and 22:00 on
    21 October were missed** — his PC was off (his word, 22:54 on 21 October). The
    readings count them as missed candles, under the decision of 17 October. Whether a
    trigger fires weekly at 14:00 (above) is for the reading of 31 October.
  - **How the count is made** — Claude's under the ruling, set before any reading,
    Viktor's to change (DECISIONS, "Decision, 17 October 2026 — how the forward
    measurement is counted"): from the task's first run, the candle that opened at
    08:00 UTC on 17 October; the task's record is the one decision per pair per candle
    per version; refusals, failures and missed candles are counted apart, failures from
    `main.py`'s line for each pair.
- **Viktor's, only if he wants it — an engine output with a section missing leaves no
  record.** The router now reads every section of the engine's output by subscript
  (the fallback sweep), so a missing one fails in `route_and_execute`'s own handler,
  which renders an error and has never written a decision-log record or carried the
  run's lineage — unlike a failure inside `_build_decision_object`, whose error record
  keeps both and is logged. Unreachable: the engine writes every section on every
  result that is not an error. Claude's question of 13 October said the lineage was
  kept in both cases; it is not (DECISIONS, the sweep's ruling, "Claude's errors").
  Whether that handler should log, with lineage, is his; nothing is owed.
- **Viktor's, not ruled — what is left of the positions of 6 and 7 October** (DECISIONS,
  "Position, 6 October 2026 — all the work and the list for after the audit first, then
  one full audit by Amazon; not ruled"). Its questions 2 and 3 were ruled on 17 October
  (DECISIONS, "Ruling, 17 October 2026 — Amazon's audit …"), and question 4 was moot
  from then; what follows if Amazon fails the check twice was ruled the same day
  (DECISIONS, "Ruling, 17 October 2026 — if Amazon fails the check twice …"). Open:
  which few settings may be tuned after the paper-trading year, named before it
  starts; and the Bedrock billing, after
  which the check of reach and fit is Claude's. How a candle that touches both the stop
  and T1 is counted is the Freqtrade item below. For all but the billing he writes his
  position first.
- **The independent audit — round 8 is done, triaged, and its fix verification accepted
  (17 October).** Claude's, under the delegation of 4 October; Viktor runs the commands.
  Round 8's preparation list — items 1 to 8, all done — is in HISTORY, in this file as
  it stood at `9e42d30`. **For the next full audit** (DECISIONS, the ruling of 17
  October, point 6): its instruction names the stop's fix as a question of its own, and
  the seven fixes the verification checked only as fixes — `fcb7823`, `ae37795`,
  `9d00d99`, `27d3ed5`, `9051ffd`, `e5ac20a` and `f00bef6` — are checked for new
  defects. **Ruled 17 October** (DECISIONS, "Ruling, 17 October 2026 — Amazon's audit
  …"): Amazon's audit is scored on four known defects held back from the list for after
  the audit, and its ratings are the ones that count toward opening backtesting, on four
  conditions fixed before the send; round 8's verified fixes do not count toward
  condition 1 through its second path. If Amazon fails the check twice: a scoped round
  on Items 2, 3, 6 and 18 by a lab clean for scoped rounds, scored on the same four,
  then a wait for a clean lab (DECISIONS, "Ruling, 17 October 2026 — if Amazon fails
  the check twice …"). **Ruled 18 October** (DECISIONS, "Ruling, 18 October 2026 —
  the four held-back defects: H1, H2, H3 and H5"): the weak-validation WAIT (H1),
  `calculate_dynamic_bias`'s unread `trend_exhaustion` (H2), the simulator's order on
  every run (H3) and the flat candle credited to the wrong volume bin (H5), each with
  its "found means" sentence in that entry. Work on the list leaves them as they are;
  Claude re-checks each at the tag before the send. **Next, under the plan:** the list
  for after the audit, less the four, in the order ruled on 19 October (DECISIONS,
  "Ruling, 19 October 2026 — the list for after the audit, sorted …"), each piece
  Viktor's to start; the Bedrock billing, his; then the check of reach and fit,
  Claude's.
- **Viktor's, not ruled — what the triage left open** (DECISIONS, "Ruling, 5 October
  2026 — round 8 triaged …", "Not ruled"): F7; B4's divergence veto; C1–C7; the ten
  questions of 1 October; the severity of F2. B5 and the severity of F4's third path
  were ruled on 20 October (DECISIONS, "Ruling, 20 October 2026 — B5 …" and "… — F4's
  third path is Critical …"). F7, the veto and C1–C7 are on the list for after the
  audit, above; the ten
  questions are an item of their own, below. Whether S1, S3, N1–N4, O1–O3 and the Part 7 reply's §1(3) and §1(5)
  join the label and record batch is settled by that sort: all are in the work before
  the audit, S1 after it with the four (S4 is held back as H1 since 18 October).
- **Viktor's, from the Freqtrade comparison (5 October), nothing ruled.** The comparison
  is outside the repository (`Docs\02_Reviews_and_Feedback\Phase7_Freqtrade_Comparison_2026-10-05`
  in `G:\Phase_7_Engine_Random_Files`).
  1. **How a candle that touches both the stop and T1 is counted** — to be ruled before
     any backtest result exists, since pre-registration works only once. Goal B's
     verdict calls T1 before the stop a win, and a 4h candle does not show which came
     first. On the real AERO 4h candles 9 of 594 (1.5%) had a range of 10% or more, about
     the gap between a 5% stop and a 5% T1 (the comparison's run). Its suggestion: count
     such a candle as a stop, report how many trades it affected, and settle it on
     smaller candles where they exist.
  2. **A longer daily window for macro** — on the list for after the audit, above.
  3. **Protections, and Freqtrade's dry-run as the paper-trading ledger** — later; the
     comparison's view is not now.

  **Not added to Goal B.** The comparison named four things for Goal B's harness:
  Freqtrade's look-ahead check (Goal B's precondition 2 already asks for one), a
  warm-up check with each backtest decision given exactly the live windows (449 × 4h and
  99 × 1d), the higher-timeframe rule (above, "Goal B's precondition 2 would let the day's
  candle leak in" — decided on 26 October by Claude under Viktor's delegation, entry
  26), and report figures printed beside the verdict, never instead of it.
  It called adding them Claude's. Goal B is a ratified specification, and its harness is
  a condition of the ruling of 29 September on what lets backtests run, so adding to
  either is Viktor's; they are listed here until he decides. **The licence is GPL-3**,
  confirmed by Viktor's `findstr` on `F:\LICENSE`. Claude's general reading, not legal
  advice: no Freqtrade code goes into this repository, which is public and MIT-licensed —
  ideas only, written our own way.
- **The ledger's entries for rounds 7 and 8 and the fix verification**, owed since
  5 October, are in the reissue of 17 October (below), section 3c, from the provider's
  generation records in `docs/audit_reports/`: round 7's runs 1 and 2 (Poolside,
  `poolside/laguna-s-2.1-20260720`, 30 September), round 8's runs 1 and 2 and Part 7
  (Xiaomi, `xiaomi/mimo-v2.6-pro-20260921`, 4 October) and the fix verification (the
  same, 17 October), with the four probes. **Viktor's statement, 17 October, 13:30**, asked for
  the reissue: "No Amazon model have been sent anything from the project." The reissue
  records it (section 3b), beside the Bedrock check of 1 October.
- **Viktor, outside the repository:** delete `D:\phase7_engine_MOVED_TO_E` and
  `D:\Phase_7_Engine_Random_Files_MOVED_TO_G` once satisfied with the copies on E: and
  G: (HISTORY, 26 September, ninth session). Not urgent.
- **Round 7's preparation list (items 1–13)** is closed: every item done, or ended
  with the round. Its full text, with item 10's checks at the send, is in HISTORY, in
  this file as it stood at `1523e0c`; round 8's list (above) points to it.
- **The model roster and the independence ledger are one document**, reissued on
  17 October as `Docs\Phase7_Model_Roster_and_Ledger_2026-10-17.pdf` (6 pages) and
  `.md` in `G:\Phase_7_Engine_Random_Files`; their SHA-256 are in `0491b84`'s
  message. It carries the 30 September document forward — kept as
  it was, `Docs\Phase7_Model_Roster_and_Ledger_2026-09-30.pdf` (5 pages, SHA-256
  `edb506c258c1bd711dc7b36263500b62c6f7e96ffcb1a29f469ce798eb39a656`), itself made from
  five earlier records — and where they disagree the later wins; its section 9 lists
  what changed. **Spent:** thirteen labs, Poolside (round 7) and Xiaomi (round 8 and the
  fix verification) added. **Clean for a full round:** Amazon alone (Nova 2 Pro, a
  preview release on 22 September). **Scoped rounds only:** Upstage, NVIDIA, Cohere,
  AI21. Mistral is spent (HISTORY, 2 September; reaffirmed 29 September). Viktor stated
  on 29 September that he has never used an NVIDIA or Poolside model anywhere, and on
  4 October a Xiaomi or MiMo model; on 17 October, that no Amazon model has been sent
  anything from the project. Model facts: Xiaomi's from the endpoints file saved
  on 4 October; Laguna S 2.1's and Nemotron 3 Super's served context and output cap of
  30 September; the rest of 22 September, none re-checked for the reissue.
- **The independence ledger is outside the repository, reconciled 29 September**
  against OpenRouter's activity export — 727 requests, 22 August to 14 September 2026,
  kept as `Docs\04_Data\OpenRouter_Activity_Export_2026-09-29.csv` in
  `G:\Phase_7_Engine_Random_Files` (SHA256 `d0edf17e0c42b35e3879a206e8a2c1d0`
  `6c9c8cfdb8bb6945615ea25baef336b8`) — and reissued as
  `Docs\Phase7_Spent_Models_Ledger_2026-09-29.pdf`; the 22 September version is kept as
  it was. **Since 30 September it is section 3 of the roster-and-ledger document above**,
  where the export was re-read: its hash matches, and every count agrees with the
  29 September ledger. The reissue of 17 October carries it as section 3a; the export's
  hash, and that of Grok's account below, were computed again that day, and match. Newly noted in the 30 September document:
  one of the 727 rows records no model, provider
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
  list for after the audit. **5 October:** the review of the night of 4 to 5
  October ran on Claude; Fable 5.1 was not used, so it has seen nothing of this
  project.
- **Viktor has stopped using Grok.** Its test run reported 458 passed, 126 skipped and
  2 failed — together the recorded 460 without `pandas_ta` — and it put the two failures
  down to repository checks without resolving them. Claude's reading, not reproduced:
  one is likely `tests/test_session_handover_check_ignored_filter.py`, which needs a
  `git` executable; the other was not in the five test files read. No model other than
  Claude is in use.
- **Viktor's call — repointing `docs/build/build_findings_bundle.py`** at the round-1
  folder, so `Phase7_Audit_Findings_Complete.pdf` could be rebuilt. A tooling change;
  not done.
- **Claude's to draft, Viktor's to approve — README.md's other stale passages**, found
  drafting the three status rows on 17 October and put here at his choice (the "Engine
  code" row, "the original four, plus three more", was brought current on 20 October
  with the Critical ruled that day):
  "The audit, and what it found" ("Five more rounds have run since")
  and "How this was built" ("Eleven models have now seen the constitution … Seven have
  graded the engine source"), which stop at 13–14 September: rounds 7 and 8, and the two
  models that ran them, which read the Constitution and rated all 44 rules, are missing —
  whether anything else is missing was not checked; and the layout block's `logs/` line,
  true but silent on `logs/pinned/` since `9e507b1` (B6). README is in Viktor's voice, so
  new wording goes to him before it lands. **And the paragraph `6469a67` rewrote** — the
  BTC-Adjusted Prediction gone, no part of the engine empirically validated — is his to
  reword or reverse.
- **Claude's — the running change list for the audit:** `docs/audit_change_list.md`,
  from the baseline `e65a0f7` (the tree round 6's fix-verification was sent). **Every
  later commit that changes engine code, tests or tooling adds its line there in the
  same commit.** `22cb39b` added the ruling of 28 September to its rulings section
  and named `7d0024e` where G's commit wrote "the commit that adds this line". The
  rulings of 29 September are not added: none changes what the engine must do, or any
  code. The triage of 5 October was added to its rulings section by `eb86846`, which
  also named `d27743f` where that commit's own line said "the commit that adds this
  line". `c2b07fb` added fix 1's line under the same wording, `1b25f36` named it there
  and added fix 2's line, and `fcb7823` named that and added fix 3's line (this
  sentence, as `fcb7823` left it, still described `1b25f36`'s step); `9e507b1` named
  `fcb7823` there and added B6's line; `6469a67` named `9e507b1` there and added
  N5's line; `ae37795` named `6469a67` there and added F3's line; `9d00d99` named
  `ae37795` there and added F5's line; `27d3ed5` named `9d00d99` there and added F6's
  line; `9051ffd` named `27d3ed5` there and added F8's line; `e5ac20a` named `9051ffd`
  there and added F9's line; `797bdc9` named `e5ac20a` there and added the fallback
  sweep's line; `69c92d6` named `797bdc9` there and added the repeated readings'
  line; `22a9a35` named `69c92d6` there and added B4's labels' line; `d77a8c4` named
  `22a9a35` there and added B7's line; `64ad625` named `d77a8c4` there and added B9's
  line; `9ea1cf3` named `64ad625` there and added B10's line; `f00bef6` named
  `9ea1cf3` there and added its own line to the tests-and-tooling table, under the
  same wording, for a later commit to name; `78ea37d` named `f00bef6` there and added
  its own line, and `d3188f2` named `78ea37d` there. `67f6ec1` named `f00bef6` in the
  rulings section's sentence that still said "the commit that adds its line above",
  brought the last paragraph current, and added the note for the next full audit
  (DECISIONS, the ruling of 17 October on round 8's fix verification, point 6).
  `0491b84` added its own line and a paragraph to the rulings section, each naming it
  "the commit that adds" its line; this file at `0491b84` still credited `67f6ec1`'s
  three changes to "the commit that writes this line", as `67f6ec1` had written it.
  `a235783` named `0491b84` in both places. (`ef65f46` and
  `36de35d`, docs only, changed no line there.) `8360923` added its own line under the
  same wording; `ed005a0` named it there and added its own, and so did `e88e0dd`,
  `d508b29` and `d410bfa`, each naming the one before; `ad34c02` named `d410bfa` there
  and added its own, `b387c03` named `ad34c02` there and added its own, `9862568` named
  `b387c03` there and added its own, and `3d7e6cb` named `9862568` there and added its
  own. The docs-only commits between them, the commit that writes this line among
  them, changed no line there. (This paragraph stopped at `a235783` until `ad34c02`
  brought it current, and
  at `ad34c02` until `9862568` did.)
- **The pre-push hook is installed per clone, not per repository.** After any re-clone
  (including after a machine wipe), run `git config core.hooksPath githooks`;
  `session_handover_check.py` section 6 flags a clone without it.
- **Unrelated, not urgent:** confirm which YH programme permits AI-assisted
  examensarbete work.
- **Viktor's call — the paper-trading setup.** Specified by the ruling of 28 September
  (points 3, 5 and 7–11). Unattended runs every 4h start with the forward measurement
  (above; ruling of 17 October), as a measurement and not the paper-trading year; the
  paper account in ten slices and the scoring are not built. It is not an engine change.
  When the year starts, and on which pairs, is Viktor's. Point 6 of the triage — test runs in a log of
  their own — landed before it, at `9e507b1` (B6).
- **Viktor's, only if he wants it — what B6 left shared between live and pinned runs.**
  The ruling named the decision log, the archive and the Exit Watch state, and those
  are separated. Three things are not, and B6 did not change them: the chart
  (`logs/charts/chart_<symbol>_<timeframe>.png`, overwritten by every run, a picture
  rather than a record), `logs/phase7_engine.log` (the process log `main.py` opens, so
  a pinned run started through `main.py` writes its lines there), and `logs/LiveSim/`
  (`live_trading.py`'s simulated orders, written whatever the run's source). No code
  reads any of them back (read from the code). Whether any should follow the run's
  source is his call; nothing is owed.
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
     backtest pause, and Viktor's call. **Being measured forward from 17 October**
     (above, the forward measurement).
  6. Does the panel always show exactly what the engine decided?
  7. Can every logged decision be rebuilt from its record, and for how long?
  8. Would the tests catch a change that is wrong but consistent?
  9. Who has checked the work since 14 September? So far Claude alone.
  10. Are there still paths a healthy run never takes?
  11. Do the documents describe the code, or each other?
  12. Does the engine work live on a pair other than AEROUSDT? (First runs on nine
      others by hand before `0491b84`, whose message says what they showed; the
      forward measurement's runs continue it.)
  13. How often does it run degraded on live data, and would anyone notice?
  14. Can it run unattended for a year and keep a clean log?
- **Viktor's, not chosen — ten questions to ask of the engine (1 October).** He asked
  for them to be kept: What does it take in? What does it produce? What assumptions does
  it make? What mathematical or technical principle is it based on? What can make it
  fail? How do we know it is working correctly? What tests would expose a false result?
  Which parts are deterministic and which stochastic? Which parts are empirically
  validated and which theoretically justified? What would convince us that the entire
  thing is wrong? What to do with them — Claude answers from the code, his answers
  first, given to the auditor, or made standing questions — is not chosen. With them,
  from the same ChatGPT conversation, hostile reviews of the Constitution (for example,
  "construct a compliant implementation that is nevertheless obviously wrong"); he
  agreed to take that up when the questions are, starting with whether each of round 7's
  four test bugs breaks a specific Constitution rule. Neither is part of the delegated
  audit, and neither goes to round 8's auditor unless he says so. The review of 5
  October answered one part of the hostile-review request — whether each of the four
  test bugs breaks a specific rule (its C3: three of the four break none as written) —
  and left the ten questions unanswered, so that Viktor's answers can come first.
