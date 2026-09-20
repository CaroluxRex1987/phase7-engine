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
`077d120`), and the open question about `docs/Phase7_Audit_Findings_Complete.pdf` is now
closed: its source, the four round-1 auditor outputs, could not be found, and README.md
says so
(HISTORY, "20 September 2026 — correction: the round-1 audit outputs were lost").
**What comes next is planning the independent audit, and that is Viktor's call** —
which model, which package, and whether the auditor sees the findings scrapped on
20 September (DECISIONS, "Ruling, 20 September 2026 — the open-items list scrapped;
an independent audit next").

## Ruled this session

- **The round-1 outputs are recorded as lost, not restored** (the Findings_Complete
  item). Viktor chose to find the source first; the search covered the repository on
  disk, git history, `D:\Phase_7_Engine_Random_Files`, the OpenRouter chat room and
  request logs, and a Claude data export, and found no copy. He then called off the
  search and approved Claude's three recommendations as proposed: README.md states the
  loss and what survives; the 30 August "nothing lived only on disk" error is recorded
  as a new dated HISTORY entry; `build_findings_bundle.py` is kept. Full account in
  HISTORY, "20 September 2026 — correction: the round-1 audit outputs were lost".

## Where things stand, right now

- **Tip:** current as of `c745a67`; the actual tip is the commit that wrote this file
  (a commit cannot name its own hash). **Tag:** `portfolio-v1` at `99e022e`.
  **Release gate:** open, declared 15 September 2026.
- **code_hash:** `bb47ab537314953e16b2db2fcf24003ead64eb5538a30221a6578d518bb7d34d` —
  unchanged since `f24a6e9`. Recomputed on `c745a67`'s tree and on this commit's applied
  tree; not assumed.
- **Golden snapshot:** last changed at `f24a6e9`; no engine code has changed since.
- **Test suite**, unchanged since `b68de08`: 486 passed / 0 failed with pandas_ta;
  355 passed / 120 skipped without it; `run_tests.py` 415 / 0 / 32. Linux sandbox,
  autocrlf clone, on `c745a67` and on this commit's applied tree. Windows at `c745a67`:
  **confirmation by proceeding** (Viktor went past the stop-on-difference steps and
  pasted `git status`). Windows at this commit: to be confirmed the same way.
- **Engineering Notes:** through Entry #140 (v1.32), at `c745a67`. **One commit behind**
  — this one — by the batching rule; the Portfolio and AI-Attribution PDFs likewise.
- **Handover check / pre-push hook:** `c745a67` is on GitHub — fetched into the sandbox
  on 20 September and confirmed as the tip. The hook's output for that push was not
  pasted, so it is not recorded here.

## Resolved this session

- **`docs/Phase7_Audit_Findings_Complete.pdf`, open since 6 September.** README.md no
  longer claims the round-1 output is published; it says the output was never committed,
  cannot be recovered, and names what survives. The same passage's "the same as the
  original four" is gone — the round-1 reports were never in `docs/audit_reports/`.
  `docs/build/README.md` points to the HISTORY entry. The error in HISTORY's 30 August
  entry is corrected by a new entry, not an edit.

## Open items

Items marked **Viktor's call** are his to decide; he writes his position first and
Claude critiques it.

- **Viktor's call — planning the independent audit:** which model, the package (the
  standing default for a fresh Tier-1 audit is the full package), and whether the
  auditor sees the scrapped findings. Not started.
- **Found, not checked: README.md's "Every raw report from every round is in
  `docs/audit_reports/`".** Round 2's folder holds a reasoning trace that ends before
  any report, and the provider export records Qwen's round-2 output as never saved.
  Whether the sentence overstates this was not examined — it was outside the
  Findings_Complete item.
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
