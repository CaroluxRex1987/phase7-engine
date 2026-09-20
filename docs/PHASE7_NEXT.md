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

The three mechanical items before the independent audit are done (`b68de08`, `9a35f1c`,
`077d120`), and the `docs/Phase7_Audit_Findings_Complete.pdf` item is closed (`4629002`;
HISTORY, "20 September 2026 — correction: the round-1 audit outputs were lost"). This
session only brought the record current: `4629002`'s Windows result and hook result
recorded below, and the Engineering Notes regenerated through it.
**What comes next is planning the independent audit, and that is Viktor's call** —
which model, which package, and whether the auditor sees the findings scrapped on
20 September (DECISIONS, "Ruling, 20 September 2026 — the open-items list scrapped;
an independent audit next").

## Ruled this session

Nothing.

## Where things stand, right now

- **Tip:** current as of `3a899b5`; the actual tip is the commit that wrote this file
  (a commit cannot name its own hash). **Tag:** `portfolio-v1` at `99e022e`.
  **Release gate:** open, declared 15 September 2026.
- **code_hash:** `bb47ab537314953e16b2db2fcf24003ead64eb5538a30221a6578d518bb7d34d` —
  unchanged since `f24a6e9`. Recomputed on `3a899b5`'s tree and on this commit's applied
  tree; not assumed.
- **Golden snapshot:** last changed at `f24a6e9`; no engine code has changed since.
- **Test suite**, unchanged since `b68de08`: 486 passed / 0 failed with pandas_ta;
  355 passed / 120 skipped without it; `run_tests.py` 415 / 0 / 32. Linux sandbox,
  autocrlf clone, on `3a899b5` and on this commit's applied tree. Windows at `4629002`
  and at `3a899b5`: **confirmation by proceeding** (Viktor went past the
  stop-on-difference steps). Windows at this commit: to be confirmed the same way.
- **Engineering Notes:** through Entry #141 (v1.33), which covers `4629002`. **Two
  commits behind** — `3a899b5`, which regenerated them, and this one — by the
  batching rule. A commit that regenerates the Notes cannot cover itself, so one
  behind is the lowest the gap can go; regenerating again for `3a899b5` alone would
  only move the gap forward one commit.
- **Portfolio Document and AI-Attribution Statement:** current. Rebuilt from `4629002`,
  their extracted text is identical to the committed PDFs, because no commit since
  `c745a67` has changed either script; so they were not regenerated. The previous
  version of this file said they were one commit behind; that was wrong.
- **Handover check / pre-push hook:** `3a899b5` is on GitHub — fetched into the sandbox
  on 20 September, confirmed as the tip, and its four changed files compared byte for
  byte with the tree verified before delivery. The pre-push hook reported
  `SUMMARY: clean` on the pushes of `4629002` and `3a899b5` (Viktor's report).

## Resolved this session

- **The record brought current at `4629002`.** The two landing facts above, Entry #141
  and the v1.33 Document History row in the Engineering Notes, and the correction about
  the two portfolio PDFs.
- **`3a899b5`'s landing facts recorded** (the Windows and hook results above), in a
  NEXT-only commit. Viktor chose this over leaving them for the next docs commit or
  regenerating the Notes for `3a899b5`.

## Open items

Items marked **Viktor's call** are his to decide; he writes his position first and
Claude critiques it.

- **Viktor's call — planning the independent audit:** which model, the package (the
  standing default for a fresh Tier-1 audit is the full package), and whether the
  auditor sees the scrapped findings. Not started.
- **Found, not checked: README.md's "Every raw report from every round is in
  `docs/audit_reports/`".** Round 2's folder holds a reasoning trace that ends before
  any report, and the provider export records Qwen's round-2 output as never saved.
  Whether the sentence overstates this was not examined (recorded at `4629002`).
- **Viktor, outside the repository:** delete "To do list Claude Phase 7 Engine.pdf".
  It was seen back in `D:\Phase_7_Engine_Random_Files` on 20 September, after an
  earlier listing the same day had not shown it.
- **Not investigated:** a connection attempt to `api.mexc.com` during `run_tests.py`,
  refused by the sandbox's egress proxy. Seen once on the tree before `b68de08`, and
  once on a pristine `16d3c1f` tree on 20 September. Which test, if any, makes it is
  unknown.
- **Found, not fixed: DECISIONS' "The rules, earned" has no rule 18.** The list goes
  17 → 19 since `108cc9f`. Not renumbered, because rule numbers are cited by number
  throughout and renumbering would make every later citation wrong. Rule-number
  citations in live code were checked by title and match; those in dated records were
  not checked.
- **The pre-push hook is installed per clone, not per repository.** After any re-clone
  (including after a machine wipe), run `git config core.hooksPath githooks`;
  `session_handover_check.py` section 6 flags a clone without it.
- **Unrelated, not urgent:** confirm which YH programme permits AI-assisted
  examensarbete work.
