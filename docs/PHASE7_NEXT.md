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

The three mechanical items Viktor ruled should come before the independent audit are
all done: the manifest test (`b68de08`), the stale citations (`9a35f1c`) and README's
omissions (`077d120`). The Engineering Notes and the two portfolio PDFs are current as of
this commit. **What comes next is planning the independent audit, and that is Viktor's
call** — which model, which package, and whether the auditor sees the findings scrapped
on 20 September (DECISIONS, "Ruling, 20 September 2026 — the open-items list scrapped;
an independent audit next").

## Ruled this session

- **Dated records are not edited to follow a move** (item 9). Viktor ruled that item 9
  covers every stale pointer a repository-wide search found, not just the ten files
  recorded, and — after first wanting the dated records edited too, "the aim was to
  keep a real record", and Claude arguing against — accepted a forward note instead:
  the sentence at the top of this file, plus the ruling in DECISIONS, "Ruling,
  20 September 2026 — dated records are not edited to follow a move". Claude read his
  reply ("we can ignore it this time if you want") as that ruling and said so before
  building.

## Where things stand, right now

- **Tip:** current as of `077d120`; the actual tip is the regeneration commit that wrote
  this file (a commit cannot name its own hash). **Tag:** `portfolio-v1` at `99e022e`.
  **Release gate:** open, declared 15 September 2026.
- **code_hash:** `bb47ab537314953e16b2db2fcf24003ead64eb5538a30221a6578d518bb7d34d` —
  unchanged since `f24a6e9`. Recomputed on the trees of all six commits since `c7ced36`
  (`e431714`, `e115272`, `b68de08`, `16d3c1f`, `9a35f1c`, `077d120`) for the Notes'
  v1.32, and on this commit's applied tree; not assumed.
- **Golden snapshot:** last changed at `f24a6e9`; no engine code has changed since.
- **Test suite**, unchanged since `b68de08`: 486 passed / 0 failed with pandas_ta;
  355 passed / 120 skipped without it; `run_tests.py` 415 / 0 / 32, the same 32 by name.
  Linux sandbox, autocrlf clone, applied tree, for each of this session's three commits.
  Windows at `9a35f1c` and `077d120`: **confirmation by proceeding** (Viktor went past
  the stop-on-difference steps and pasted `git status`). Windows at this commit: to be
  confirmed the same way.
- **Engineering Notes:** through Entry #140 (v1.32), regenerated in this commit; no gap.
  **Phase7_Portfolio_Document.pdf** and **Phase7_AI_Attribution.pdf** regenerated in the
  same commit; their text differs from the previous build only by `9a35f1c`'s pointer
  changes, compared word by word. The Notes script, run unchanged before the new entries
  were added, reproduced the committed PDF's text exactly.
- **Handover check / pre-push hook:** `SUMMARY: clean` on the pushes of `9a35f1c` and
  `077d120`. After each push GitHub's tip was fetched into the sandbox and every changed
  file compared byte for byte with what was verified.

## Resolved this session

- **Item 9 — stale citations of `docs/PHASE7_NEXT.md`, `9a35f1c`.** The recorded list
  of ten files was incomplete; the fix covers twenty-four. Live pointers now name the
  section of DECISIONS or HISTORY that holds the content; still-correct citations were
  left; dated records were not edited (ruling above). Two citations were wrong from the
  day they were written: "rule 18" in `entry_model.py` and
  `test_decision_bar_integrity.py` — `108cc9f` renumbered that rule in the same commit
  (now 22). `code_hash` unmoved, all 33 per-file fingerprints equal, with a negative
  control. Full account in its commit message and Notes Entry #139.
- **Item 10 — README.md brought current, `077d120`.** The three recorded omissions
  closed, plus four stale statements found by reading the whole file: test counts,
  `Logs/` for `logs/`, the module lists and "sixteen files" (twenty-two now), and the
  "nothing but a Python interpreter" claim `run_tests.py`'s docstring had withdrawn.
  Notes Entry #140.
- **Engineering Notes regenerated, v1.32, Entries #136–#140**, with the two portfolio
  PDFs. This file's previous version (`16d3c1f`) moved to HISTORY verbatim, proven by
  un-demoting the block and comparing byte for byte, with a one-character negative
  control; the old HISTORY is an exact prefix of the new one.

## Open items

Items marked **Viktor's call** are his to decide; he writes his position first and
Claude critiques it.

- **Viktor's call — planning the independent audit:** which model, the package (the
  standing default for a fresh Tier-1 audit is the full package), and whether the
  auditor sees the scrapped findings. Not started.
- **Viktor's call, open since 6 September — `docs/Phase7_Audit_Findings_Complete.pdf`.**
  README.md and `docs/build/README.md` cite it; it does not exist in the repository, and
  its build script's source material has never been here. Remove the reference, or
  restore the source material. Not in the list scrapped on 20 September.
- **Viktor, outside the repository:** delete "To do list Claude Phase 7 Engine.pdf".
  Carried from `16d3c1f`; whether it has been done is not known.
- **Not investigated:** a connection attempt to `api.mexc.com` during `run_tests.py`,
  refused by the sandbox's egress proxy. Seen once on the tree before `b68de08`, and
  once on a pristine `16d3c1f` tree on 20 September, before any of this session's
  changes; not in the other runs. Which test, if any, makes it is unknown.
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
