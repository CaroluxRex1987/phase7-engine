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

## Ruled this session — the old list is scrapped; an independent audit is next

Viktor scrapped the seven judgment and review items that were open at `e115272` — the
bias-weight magnitudes and thesis, the five points from the 15 September PDF, the To-do
PDF, the four-factor finding, the RSI double path, the engine review's missing scope,
and the backtest-start declaration. Next is **a new audit by an independent model**;
before it, three mechanical items: the manifest test (done, `b68de08`), the stale
citations (done, `9a35f1c`), and README's omissions (done, in the commit that wrote
this version of the file). All three are done; planning the audit is next, and is
Viktor's call. Full ruling, what it does and does not change, and
what is still undecided about the audit: docs/PHASE7_DECISIONS.md, "Ruling,
20 September 2026."

## Where things stand, right now

- **Tip:** current as of `9a35f1c`; the actual tip is the item-10 commit that wrote this
  version of the file (a commit cannot name its own hash). **Tag:** `portfolio-v1` at `99e022e`.
  **Release gate:** open, declared 15 September 2026.
- **code_hash:** `bb47ab537314953e16b2db2fcf24003ead64eb5538a30221a6578d518bb7d34d` —
  unmoved by `b68de08`, `16d3c1f`, `9a35f1c` — which edits comments and docstrings in six
  fingerprinted modules; `code_hash` strips both, recomputed on the pre-patch and
  applied trees, not assumed — and the item-10 commit (README.md and this file only;
  recomputed, not assumed). Unchanged since `f24a6e9`.
- **Golden snapshot:** last changed at `f24a6e9`; no engine file has changed since.
- **Test suite at `9a35f1c` and the item-10 commit** (no test or code change in
  either): Linux sandbox, autocrlf clone, applied tree — 486 / 0 with pandas_ta;
  355 passed / 120 skipped without it; `run_tests.py` 415 / 0 / 32, the same 32 by
  name. Windows at `9a35f1c`: 486 / 0 and 415 / 0 / 32 — **confirmation by
  proceeding**. Windows at the item-10 commit: to be confirmed the same way.
- **Test suite at `b68de08`** (engine code unchanged since `5c73e24`):
  - Windows (Viktor's machine, pandas_ta): 486 passed / 0 failed and `run_tests.py`
    415 / 0 / 32 — **confirmation by proceeding** (told to stop on any other count;
    output not pasted).
  - Linux sandbox, autocrlf clone: 486 / 0 with pandas_ta; 355 passed / 120 skipped
    without it; `run_tests.py` 415 passed / 0 failed / 32 errors, the same 32 by name as
    before.
  - Linux sandbox, **default LF clone: 486 / 0.** The standing platform difference
    (484 / 1 on LF checkouts) is closed by `b68de08`.
- **Engineering Notes:** through Entry #135 (v1.31), regenerated at `c7ced36`. Not yet
  covering `e431714`, `e115272` (both docs-only), `b68de08` (tests and tooling — the
  first non-docs commit since the last regeneration), `16d3c1f` (docs-only), `9a35f1c`
  (comments and docstrings) or the item-10 commit (docs-only). Batched per the standing
  rule; **regeneration is now due** — item 10 has landed. `9a35f1c` also changed text
  that
  `build_portfolio_document.py` and `build_ai_attribution.py` render, so their PDFs are
  behind their scripts until those two are regenerated.
- **Handover check / pre-push hook:** ran on the push of `b68de08`, `SUMMARY: clean`.
  GitHub's tip was then fetched into the sandbox: `b68de08`, the three files
  byte-identical to what was verified.

## Resolved since the previous version of this file

- **Item 10 — README.md brought current, in the item-10 commit.** The three recorded
  omissions are closed: `Claude outputs/` and `decision_log_backups/` are in the layout
  tree, and a new paragraph points at the three PHASE7_* files. The same full read of
  README.md found four more stale statements, fixed in the same commit: the test counts
  (485 / 354 / 414 → 486 / 355 / 415, the counts at `b68de08`); `Logs/` in the tree
  (the directory is `logs/`); the module lists and the "sixteen files" count (now
  twenty-two); and the claim that `run_tests.py` needs "nothing but a Python
  interpreter", which the runner's own docstring had withdrawn on 6 September. One
  was left alone because it is not Claude's call — see Open items.

- **Item 9 — stale citations of `docs/PHASE7_NEXT.md`, fixed in the item-9 commit.**
  The recorded list of ten files was incomplete. Every live citation is now either
  pointed at the section of DECISIONS or HISTORY that holds the content, or left alone
  because it is still correct (the handover check reading NEXT, `run_tests.py`'s
  baselines, the audit package's exclusion list). Dated records were not edited — see
  the new DECISIONS ruling. Two citations were wrong from the day they were written:
  "rule 18" in `entry_model.py` and `test_decision_bar_integrity.py` — the same commit
  that wrote them, `108cc9f`, renumbered that rule (now 22). Full account in the commit
  message.

- **`b68de08` — the pinned-data manifest check is portable.** Manifest hashes are now
  over CRLF-normalised content, in both `make_pinned.py` and the test; the manifest was
  regenerated by the script itself (CSVs byte-identical); one new test,
  `test_manifest_hash_ignores_line_endings`, makes a revert to raw bytes fail on every
  platform. Full account in its commit message.
- **Where the six bias weights came from — traced in `git log`.** Unchanged in value
  since `83a9425` (26 August), which brought them in wholesale, replacing the first
  commits' four-term blend. No commit ever changed a weight value without a record;
  the original choice predates the repository, which is why no reason for it exists.
  Recorded in DECISIONS with the ruling above.
- **GitHub's tip checked by clone, not by assertion**, at the start of this session
  (`e115272`) and after the push (`b68de08`).
- **The previous version of this file was misdated.** It was headed "20 September";
  the commits that wrote it (`e431714`, `e115272`) are dated 19 September. Corrected
  in the note heading its HISTORY entry, not in the moved text, since HISTORY is
  append-only. This file's date (20 September) is from the session clock and matches
  `b68de08`'s commit date.

## Open items

Items marked **Viktor's call** are his to decide; he writes his position first and
Claude critiques it.

- **Viktor's call, open since 6 September — `docs/Phase7_Audit_Findings_Complete.pdf`.**
  README.md and `docs/build/README.md` cite it; it does not exist in the repository, and
  its build script's source material has never been here. Recorded on 6 September as
  "a decision this patch does not take": remove the reference, or restore the source
  material. Still undecided; not in the list scrapped on 20 September.
- **Viktor's call — planning the independent audit:** which model, the package (the
  standing default for a fresh Tier-1 audit is the full package), and whether the
  auditor sees the scrapped findings. Not started.
- **Viktor, outside the repository:** delete "To do list Claude Phase 7 Engine.pdf".
- **Not investigated:** in one `run_tests.py` run on the pre-patch tree, the sandbox's
  egress proxy reported one connection attempt to `api.mexc.com` (refused there). An
  earlier run of the same command on the same tree showed no such report, so it is not
  reliably reproduced; not caused by `b68de08`, whose tree was not yet built. Which
  test, if any, makes it is unknown. `b68de08`'s commit message says it was "present on
  the pre-patch tree too"; more exactly, it was seen once, only on the pre-patch tree,
  and not in the post-patch runs. Seen once more on 20 September, in the baseline
  `run_tests.py` run on a pristine `16d3c1f` tree before item 9 was built — so it is
  not caused by item 9 either. Still not investigated.
- **Found, not fixed: DECISIONS' "The rules, earned" has no rule 18.** The list goes
  17 → 19; `108cc9f` (2 September) inserted a rule and moved the old 18 to 20 (now
  22). Not renumbered, because rule numbers are cited by number throughout the
  repository and renumbering would make every later citation wrong. The rule-number
  citations in live code outside item 9's scope were checked by title against the
  list and match; those in dated records were not checked.
- **The pre-push hook is installed per clone, not per repository.** After any re-clone
  (including after a machine wipe), run `git config core.hooksPath githooks`;
  `session_handover_check.py` section 6 flags a clone without it.
- **Unrelated, not urgent:** confirm which YH programme permits AI-assisted
  examensarbete work.
