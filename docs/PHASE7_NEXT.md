# Next step — read this first

*20 September 2026. This file is the project's current-state entry point: it states only
what is true right now and what to do next, and is rewritten each session, not appended
to. Standing rules, ratified specifications and rulings in force live in
docs/PHASE7_DECISIONS.md. The dated record — including this file's previous version,
moved there verbatim this session — lives in docs/PHASE7_HISTORY.md. A citation of this
file written before the 18 September 2026 split — in the Engineering Notes, audit
reports, handovers or any other dated record — refers to content now in one of those
two files; dated records are not edited to say so (DECISIONS, "Ruling, 20 September
2026 — dated records are not edited to follow a move").*

## PACE FIRST — read this before the rest of this file

Viktor judged, on his own, that 226 commits across 22 days had become hasty, and
ruled to slow down considerably (15 September 2026). **Do not open a session by
proposing work from "Open items" below, and do not treat it as a queue to clear.**
Ask what he wants to do first.

## Where the project is

This session (20 September, evening) took four loose ends from the Open items, at
Viktor's choice: README.md's claim about the audit reports, the `api.mexc.com`
connection seen during the tests, rule-number citations around DECISIONS' missing
rule 18, and folding `92775ea`'s landing facts into this file. All four are closed —
see "Resolved this session". Checking the README claim turned up a contradiction in
the record about round 3's independence, which Viktor ruled on.
**What comes next is still planning the independent audit, and that is Viktor's
call** — which model, which package, and whether the auditor sees the findings
scrapped on 20 September (DECISIONS, "Ruling, 20 September 2026 — the open-items list
scrapped; an independent audit next").

## Ruled this session

- **Round 3 is not counted as independent.** DECISIONS, "Ruling, 20 September 2026 —
  round 3 is not counted as independent": the reason that holds is authorship (GLM 5.3
  wrote the Remediation Plan; GLM 5.3 Flash then reviewed work done under it), not
  exposure, which the 2 September ruling would clear. Viktor first proposed counting it
  as independent, from memory of the 28 August run as minor; the record showed
  otherwise, and he ruled.
- **`test_main_runs_without_a_logs_directory` is left as it is (option A)** — it keeps
  doing one live engine run against MEXC whenever the suite runs with `pandas_ta`.
  Claude recommended option B (point the subprocess at `tests/fixtures/pinned/`, which
  ran to exit 0 with no network in the sandbox) and was overruled.
- **README wording delegated to Claude:** the round-2 sentence ("do what is best for
  the project") and the round-3 wording ("fix the GLM wording as it should be done").
- **A note at the rule-18 gap in DECISIONS: yes.**

## Where things stand, right now

- **Tip:** current as of `92775ea`; the actual tip is the commit that wrote this file
  (a commit cannot name its own hash). `92775ea` was confirmed as GitHub's tip by a
  fresh clone at the start of this session. **Tag:** `portfolio-v1` at `99e022e`.
  **Release gate:** open, declared 15 September 2026.
- **code_hash:** `bb47ab537314953e16b2db2fcf24003ead64eb5538a30221a6578d518bb7d34d` —
  unchanged since `f24a6e9`. Recomputed on `92775ea`'s tree and on this commit's applied
  tree; not assumed.
- **Golden snapshot:** last changed at `f24a6e9`; no engine code has changed since.
- **Test suite**, unchanged since `b68de08`: 486 passed / 0 failed with pandas_ta;
  355 passed / 120 skipped without it; `run_tests.py` 415 / 0 / 32. Linux sandbox,
  autocrlf clone, on `92775ea` and on this commit's applied tree. Windows at `4629002`,
  `3a899b5` and `92775ea`: **confirmation by proceeding** (Viktor went past the
  stop-on-difference steps). Windows at this commit: to be confirmed the same way.
- **Engineering Notes:** through Entry #141 (v1.33), which covers `4629002`. **Three
  commits behind** — `3a899b5`, `92775ea` and this one — by the batching rule. Not
  regenerated in this commit.
- **Portfolio Document and AI-Attribution Statement:** current with their scripts; no
  commit since `c745a67` has changed either script. One claim in the Portfolio Document
  is now known to be wrong — see Open items.
- **Handover check / pre-push hook:** the pre-push hook reported `SUMMARY: clean` on
  the pushes of `4629002`, `3a899b5` and `92775ea` (Viktor's report).

## Resolved this session

- **README.md's "Every raw report from every round is in `docs/audit_reports/`".**
  Narrowly overstated: round 2 never produced a report (every attempt stopped before
  writing one; the folder holds Kimi K3's reasoning trace, and a Qwen response from
  that day was never saved), yet the paragraph counted it among rounds that had run and
  pointed to their reports. Now stated. The same paragraph said every round ran "on a
  model reporting no prior exposure"; corrected per the round-3 ruling, with the status
  table and the release-gate paragraph brought in line ("five further rounds", three
  both independent and complete).
- **The `api.mexc.com` connection.** Made by
  `tests/test_clean_checkout.py::test_main_runs_without_a_logs_directory`, which runs
  `python main.py` in a temporary copy of the repository and so fetches live data. Found
  by tracing every outbound connection in the sandbox (Linux, autocrlf clone, `92775ea`):
  it is the suite's only one, under both pytest and `run_tests.py`; with `pandas_ta`
  absent no connection was made (whether because that test is skipped was not checked).
  It writes only inside its temporary directory, so the live decision log is not
  touched. Left as is, by ruling.
- **Rule-number citations around the missing rule 18.** The rules list was rebuilt at
  all 98 commits that touched it. Only one rule ever changed number — "Fixing the
  instance you found does not close the item": 18 → 20 at `108cc9f`, → 21 at
  `710cb5e`, → 22 at `e70b835`, all 1–2 September. Every citation of rules 18–21 in
  tracked `.md`/`.py`/`.txt` files (excluding `docs/audit_package/` and
  `docs/audit_reports/`) and in every commit message was checked against the list as it
  stood when written: all correct, except "rule 18" meaning today's rule 22, already
  recorded at `9a35f1c` (Entry #139). PDFs were not searched.
- **A note at the gap, and a rendering defect it also fixes.** DECISIONS now has an
  item 18 saying the number is empty and where the rule went. Found while adding it:
  Markdown numbers an ordered list by position, so the rendered list had shown every
  rule from 19 on one lower than its cited number — a reader following "rule 22" on
  GitHub landed on rule 23. Checked with a CommonMark renderer (markdown-it-py), not on
  GitHub itself: before, source and rendered numbers diverged from 19 on; after, all 38
  match.
- **`92775ea`'s landing facts** (Windows by proceeding, hook clean) folded in above.

## Open items

Items marked **Viktor's call** are his to decide; he writes his position first and
Claude critiques it.

- **Viktor's call — planning the independent audit:** which model, the package (the
  standing default for a fresh Tier-1 audit is the full package), and whether the
  auditor sees the scrapped findings. Not started.
- **Found, not fixed: the Portfolio Document says the four original audit runs were on
  "models with no prior involvement in the build".** README.md says DeepSeek worked on
  the build through Aider, and Run 1 was DeepSeek. Fixing it means editing
  `build_portfolio_document.py` and regenerating the PDF.
- **Found, not checked:** HISTORY's 5 September "The record corrected from the bill"
  says the eleven round-2 observations came from a Qwen run; the
  `round2_kimi_k3_20260902/README.md`, filed later, says they are Kimi's. Which is the
  later word, and whether the earlier one is marked superseded, was not examined.
- **Viktor, outside the repository:** delete "To do list Claude Phase 7 Engine.pdf" from
  `D:\Phase_7_Engine_Random_Files` (last seen there on 20 September; not rechecked this
  session).
- **The pre-push hook is installed per clone, not per repository.** After any re-clone
  (including after a machine wipe), run `git config core.hooksPath githooks`;
  `session_handover_check.py` section 6 flags a clone without it.
- **Unrelated, not urgent:** confirm which YH programme permits AI-assisted
  examensarbete work.
