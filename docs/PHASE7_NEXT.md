# Next step — read this first

*Updated 30 August 2026, after item 16. **The independent re-audit has run and the release
gate is NOT met.** Suite: 119 passing — but see the caveat below, it means less than it says.*

## Where things stand

```
0–15 ✅  all sixteen items' code work complete
16   ✅  Step 8 independent re-audit — RUN, by GPT-5.6 Luna Pro
─────────────────────────────────────────────────────────
     ←   REMEDIATION of the audit's findings         NEXT
         then: the owed document batch
```

**Read `claude/phase7-item16-triage.md` before anything else.** It carries the auditor's
five Criticals, Claude's verdict on each (four hold, one does not), three further confirmed
defects, and a suggested order of work. The full report is
`docs/audit_package/luna_pro_audit_report.md`.

## The short version

The engine passed 119 self-authored tests and failed an independent audit on five
Criticals, three of which are in code Claude fixed and certified. The auditor's summary of
the suite is worth quoting: it "tests that selected implementation details have not changed
more strongly than it tests whether the engine is correct."

**The 119 figure is not what it appears.** `if not _engine_available(): return` is a PASS
under pytest, not a skip, and it appears across the suite. On a machine without
`pandas_ta` the engine tests report success without running. Until that is fixed, nobody
knows which tests have been running — including in every verification Claude reported
during items 8–15.

## Three rulings needed from Viktor before code

1. **Item 3 — what counts as abnormal volume?** All-zero is unambiguous and must be
   rejected (it makes VWMA equal close, awarding a perfect 20/20 entry score). The
   isolated-spike case is where Claude's original "deliberately not implemented" objection
   still has some force. Reject, degrade, or accept?
2. **Item 11 — what counts as independent confirmation?** Macro, volume and structure each
   reach confidence twice. Removing the duplication is easy; deciding which path survives
   is a trading judgment.
3. **Item 14 — do the AGGRESSIVE / CONSERVATIVE labels survive at all?** They no longer
   describe a size; sequence item 13 removed sizing.

## Suggested order

1. `pytest.skip()` across the suite, then re-run and see what actually fails. **First,
   before any behavioural fix.**
2. The cheap and unambiguous: the "full size" text, `main.py`'s bare `'Logs'`,
   `trade_quality_current` and its vacuous assertion, "Lookback 8", `np.isfinite` in risk
   validation.
3. Item 3 volume policy (needs ruling 1).
4. Item 8/13 macro degradation — includes rewriting the golden-path test that currently
   asserts the defect as expected behaviour.
5. Item 11 circularity (needs ruling 2). Largest.
6. Item 14 (needs ruling 3).

## The machine was rebuilt

Windows was reinstalled on 30 August 2026, all drives wiped. Everything of value is on
GitHub at `375334a`; nothing lived only on disk except gitignored `logs/`.

**`docs/audit_package/environment_before_reinstall.txt`** records the exact library
versions and **Python 3.12.0** that produced the current golden baseline.
`requirements.txt` pins no versions — that is audit Finding 15 — so a fresh install can
resolve different pandas / numpy / pandas_ta and shift indicator output. **If the golden
snapshot moves after the rebuild, check that file before assuming the engine broke.**

After reinstalling: Python 3.12.0, git, `pip install -r requirements.txt`, and re-link the
Claude desktop app to `D:\phase7_engine`.

## Working practice

- **Deliver as a `.patch`, never a zip.** `git apply --check <file>.patch` first, then
  `git apply`. Write the patch and message file into the repo over the device bridge,
  stage them out with explicit paths, then delete them.
- **Restore CRLF before diffing.** The repo is CRLF; Python text-mode writes produce LF.
- **Run the suite plain BEFORE re-baselining**, and **predict the diff in advance**. Items
  13, 14 and 15 each predicted exactly what would move — nine fields, one field, nothing —
  and each was right.
- **Never `device_stage_files` back into the sandbox working copy**; it overwrites edits.

## The rules, earned

1. Search exhaustively before asserting a thing is not there.
2. A grep for a key name is not a data-flow trace — follow the value to its reader.
3. A defect found once is usually a class.
4. A passing test can be hiding the finding.
5. An argument that a difference would not matter is not evidence the difference exists.
6. A declaration permitting the one illegal shape is worse than none.
7. Inject failures at a point confirmed to be on the path; after deleting a block, scan the
   function for names it defined.
8. A record of a run must not contain machine-specific paths.
9. A guard that iterates a list is silent when the list empties.
10. **Count what you claim.** Two commit messages said "ten tests" where there were nine.
11. **A list of names is a claim about the code, and it decays.**
12. **Fix the helper, not just the branch.** Item 9a cleaned every `except` block and left
    `clean_series`, which the success path ran through, still turning an all-NaN indicator
    into zeros — silencing the guards 9a had just written.
13. **Injecting one kind of failure tests one kind of failure.** Ask what else the
    dependency can do wrong.
14. **Grade a finding at its real severity, including downwards.**
15. **A test that returns is a test that passed.** Skipping must be visible in the result,
    or the suite reports green for work it never did.
16. **A guard written from a list of examples inherits the gaps in that list.** The
    hardcoded-path test searched five spellings; the surviving bug used a sixth. Match on
    structure — the parse tree, the actual value — not on enumerated text.
17. **Verification by sampling is not verification.** Claude declared the Constitution PDF
    free of audit outcomes after searching three guessed phrases and reading six of
    eighteen hits on a fourth. The outcomes were in a table using words never searched, and
    the auditor found them in its first act.
