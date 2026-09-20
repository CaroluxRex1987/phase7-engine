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

This session (20 September, from about 10:00) opened on the independent audit, and
Viktor chose to land the session's routine record first, as its own commit: this
rewrite of the file, with its previous version moved verbatim to HISTORY, and
`982e70f`'s two landing facts. The previous session's account — the round-3 ruling,
README's audit-round corrections, the `api.mexc.com` trace, the rule-18 note, and the
in-place record of `53394ff`'s landing — is now in HISTORY, "20 September 2026 —
PHASE7_NEXT.md as it stood at `982e70f`".
**What comes next is still planning the independent audit, and that is Viktor's
call** — which model, which package, whether the auditor sees the findings scrapped
on 20 September, and the instruction for the selected model (DECISIONS, "Ruling, 20
September 2026 — the open-items list scrapped; an independent audit next"). He writes
his position first; Claude critiques it.

## Ruled this session

- **The NEXT rewrite and `982e70f`'s landing facts land first, as their own commit**,
  rather than being folded into the audit-planning commit as planned at the end of the
  previous session. Viktor's choice.
- **The Engineering Notes are not regenerated in this commit.** Claude recommended
  waiting: a regeneration now would cover `3a899b5` to `982e70f` but not the
  audit-planning commit that follows, so it would have to be done again before building
  a package that includes the Notes. Viktor agreed. They are regenerated once, after
  the audit rulings, and only if the package includes them.

## Where things stand, right now

- **Tip:** current as of `982e70f`; the actual tip is the commit that wrote this file
  (a commit cannot name its own hash). `982e70f` was confirmed as GitHub's tip by a
  sandbox fetch (Viktor's report), and again by this session's sandbox clone.
  **Tag:** `portfolio-v1` at `99e022e`. **Release gate:** open, declared 15 September
  2026.
- **code_hash:** `bb47ab537314953e16b2db2fcf24003ead64eb5538a30221a6578d518bb7d34d` —
  unchanged since `f24a6e9`. Recomputed on `982e70f`'s tree and on this commit's applied
  tree; not assumed.
- **Golden snapshot:** last changed at `f24a6e9`; no engine code has changed since.
- **Test suite**, unchanged since `b68de08`: 486 passed / 0 failed with pandas_ta;
  355 passed / 120 skipped without it; `run_tests.py` 415 / 0 / 32. Linux sandbox,
  autocrlf clone, on `982e70f` and on this commit's applied tree. Windows at `4629002`,
  `3a899b5`, `92775ea`, `53394ff` and `982e70f`: **confirmation by proceeding** (Viktor
  went past the stop-on-difference steps). Windows at this commit: to be confirmed the
  same way.
- **Engineering Notes:** through Entry #141 (v1.33), which covers `4629002`. **Five
  commits behind** — `3a899b5`, `92775ea`, `53394ff`, `982e70f` and this one — by
  Viktor's choice this session (see "Ruled this session"). If the independent audit's
  package includes the Notes, regenerate them after the audit-planning commit and
  before building it.
- **Portfolio Document and AI-Attribution Statement:** current with their scripts; no
  commit since `c745a67` has changed either script. One claim in the Portfolio Document
  is now known to be wrong — see Open items.
- **Handover check / pre-push hook:** the pre-push hook reported `SUMMARY: clean` on
  the pushes of `4629002`, `3a899b5`, `92775ea`, `53394ff` and `982e70f` (Viktor's
  report).

## Resolved this session

- **`982e70f`'s landing facts** (Windows by proceeding, hook clean) folded in above.
- **The once-per-session rewrite of this file**, deferred by `982e70f` to this
  session. The previous version is in HISTORY verbatim, headings demoted one level.

## Open items

Items marked **Viktor's call** are his to decide; he writes his position first and
Claude critiques it.

- **Viktor's call — planning the independent audit:** which model, the package (the
  standing default for a fresh Tier-1 audit is the full package), whether the auditor
  sees the scrapped findings, and the instruction for the selected model. Not started.
  If the package includes the Engineering Notes, regenerate them first (see above).
- **Found, not fixed: the Portfolio Document says the four original audit runs were on
  "models with no prior involvement in the build".** README.md says DeepSeek worked on
  the build through Aider, and Run 1 was DeepSeek. Fixing it means editing
  `build_portfolio_document.py` and regenerating the PDF.
- **Found, not checked:** HISTORY's 5 September "The record corrected from the bill"
  says the eleven round-2 observations came from a Qwen run; the
  `round2_kimi_k3_20260902/README.md`, filed later, says they are Kimi's. Which is the
  later word, and whether the earlier one is marked superseded, was not examined.
- **The pre-push hook is installed per clone, not per repository.** After any re-clone
  (including after a machine wipe), run `git config core.hooksPath githooks`;
  `session_handover_check.py` section 6 flags a clone without it.
- **Unrelated, not urgent:** confirm which YH programme permits AI-assisted
  examensarbete work.
