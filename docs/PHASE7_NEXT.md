# Next step — read this first

*Updated 2 September 2026, after Finding 3. **All five of the audit's Criticals are now
fixed — but only four of them ever were until today.** Suite: 155 passing, 0 skipped, 0
failed, and 91 passed / 64 skipped on a machine without `pandas_ta`.*

> **Read the audit report, not this file, when you want to know what is outstanding.**
> From 31 August to 1 September this file said remediation of the five Criticals was
> complete. It was not. Finding 3 — a whole Critical — had never been entered into any
> roadmap, so it was never scheduled, never ruled on, and never noticed missing. It was
> found by reading `docs/audit_package/luna_pro_audit_report.md` end to end. This file is
> a plan derived from that report; the report is the record.

## Where things stand

```
0–15 ✅  all sixteen items' code work complete
16   ✅  Step 8 independent re-audit — RUN, by GPT-5.6 Luna Pro
     ✅  Batches 1–2: real skips + five unambiguous fixes — dba1b63
     ✅  Items 3, 11, 14: rulings made and implemented — c4dfcc7
     ✅  Item 8/13 macro degradation — 5d2cbbe
     ✅  Finding 15: dependency versions pinned — a26c545
     ✅  Finding 3: decision-bar integrity — the Critical nobody scheduled
─────────────────────────────────────────────────────────
     ←   nothing outstanding from the audit
         then: the owed document batch (never scoped — see below)
```

**"The owed document batch"** has been carried in this diagram since before the audit and
appears nowhere else — not in the audit report, not in any commit. Nobody now knows what
it referred to. Treat it as stale unless Viktor recognises it.

`claude/phase7-item16-triage.md`, which this file used to say to read first, does not
exist and never did — flagged rather than blocked on when batches 1–2 shipped. This file
and `docs/audit_package/luna_pro_audit_report.md` (the full report) have carried that
weight instead; nothing has needed the missing file since.

## The short version

The engine passed 119 self-authored tests and failed an independent audit on five
Criticals, three of which were in code already fixed and certified. The auditor's summary
of the suite is worth keeping even though the defect it describes is fixed: it "tests that
selected implementation details have not changed more strongly than it tests whether the
engine is correct" — a warning about what a green suite can hide, not only about this one
mechanism.

**The 119 figure was not what it appeared, and this is now fixed.** `if not
_engine_available(): return` was a PASS under pytest, not a skip. Batch 1 converted all 46
occurrences to real `pytest.skip()` calls; on a machine without `pandas_ta` the suite now
reports 46 SKIPPED rather than 46 false PASSes, which is how the four tests that import
`core.engine_core` directly (bypassing the guard) were found to fail outright in that
scenario — reported for record, not fixed, since importing directly rather than going
through an `_engine_available()` guard is a defect in those four tests, not one Item 16
named. The suite is 136 items now (10 net new, from the Item 3 and Item 14 test files
below) and — with `pandas_ta` installed, which is the normal case on Viktor's machine — all
136 pass.

## Three rulings — made, 31 August 2026

Viktor delegated all three ("decide items 3, 11, 14 myself") rather than ruling on each
individually. What follows is the ruling and where it lives; full reasoning is in commit
`c4dfcc7` and in the code itself, everywhere tagged `ITEM <N> RE-AUDIT`.

1. **Item 3 — abnormal volume.** All-zero volume is rejected outright, at
   `data/validation.py` — there is no genuine measurement to build VWMA or any
   volume-weighted read from. An isolated extreme spike is still **accepted** at that layer
   — the original "deliberately not implemented" reasoning held: a spike is real data, and
   rejecting a run over a busy market would make the engine least available exactly when it
   matters. What changed is that a spike no longer reaches every downstream score
   unflagged — `indicators/indicators.py` now detects one (>10x the recent rolling median)
   and records it as a degradation, capping confidence rather than fabricating a
   substitute value. Ruled: reject / **degrade** / accept, per case.
2. **Item 11 — independent confirmation.** The prior "sequence item 11" pass fixed one
   instance (a direct `trend_health * 0.3` term in confidence) and left three siblings of
   the same pattern standing — structure regime and macro/volume agreement, each counted
   once inside `bias_score` and again as a confidence bonus, plus trend health leaking into
   bias_engine's own "reversal/continuation" factor a second time. All three removed rather
   than reweighted: `bias_score` is now the one place all six factors are combined, and
   `confidence` is exactly its magnitude — see `models/decision_model.py`'s
   `_compute_confidence` and `models/bias_engine.py`'s dependency-graph comment.
3. **Item 14 — AGGRESSIVE / CONSERVATIVE labels.** They survive, but AGGRESSIVE now
   requires an independent risk-regime check on top of directional conviction and entry
   quality. `risk_model.classify_risk_regime()` already computed a four-tier regime; only
   the EXTREME-RISK-or-not boolean reached `risk_valid`. It's now threaded through as its
   own field, and `decision_model.py` won't return AGGRESSIVE when the regime is HIGH
   VOLATILITY RISK or worse — the setup still trades, just as the plain LONG/SHORT it
   earned on trend health and entry quality alone.

## Finding 3 — the Critical that was never on the list

Found 2 September 2026, by reading the audit report itself rather than this file.

**What it was.** Every indicator guard in `indicators/indicators.py` asked one question:
`.isna().all()` — "did the calculation return nothing at all". That catches total failure.
It does not catch a series with 299 good values and no value at the bar the decision is
made on. And it could not: `clean_series(method="forward_fill")` had already filled that
gap with the previous bar's number before the guard ran, so `.isna().all()` was False no
matter what happened at the decision bar. A stale reading sat in the decision row,
indistinguishable from a measurement.

**How wide.** The audit named ATR and SuperTrend direction. Injecting a trailing NaN into
each indicator in turn found ATR, RSI, ADX, SuperTrend *and* both EMAs — every one, no
failure recorded, decision row equal to the previous bar. It was a property of the guard,
so the guard is now one function (`indicators.unusable_reason`) that every caller asks.
Two had no guard at all to fix: the SuperTrend *level* (only its direction was checked)
and the EMAs. The same trailing fill was also running on the raw OHLCV columns, turning a
truncated final candle into a synthetic bar repeating the previous close — defence in
depth only, since `validation.py` rejects that frame first, which is now pinned by a test.

**And the consumers.** Item 9a removed the invented constants from the producer and left
them in the readers, where two of them awarded the *maximum* score for a measurement never
taken: a missing RSI fell back to `50.0`, inside the "not extended" band, scoring 15 of
15; a missing HVN fell back to `close`, making the distance exactly zero, scoring 12 of 12.
The HVN one is byte-for-byte the defect item 3 fixed for VWMA, sitting forty lines below
that fix. `risk_model.calculate_stop_targets` accepted a NaN ATR outright — every
comparison against NaN is False — and with a structural level present returned a
completely normal-looking plan in which ATR contributed nothing.

**Ruled:** a value that was not measured at the decision bar is absent, and absent means
that indicator failed — which hands it to the degradation machinery that already caps
confidence and refuses to authorize a trade. No new policy was invented; the existing one
was applied one row over.

Fixed in `indicators/indicators.py`, `models/entry_model.py`, `models/risk_model.py`,
`core/panel_render.py`, with `tests/test_decision_bar_integrity.py` (18 tests, 14 of which
fail against the pre-fix code — the other four are controls that must pass both sides).

## Suggested order — status

1. ✅ `pytest.skip()` across the suite — batch 1, `dba1b63`.
2. ✅ The cheap and unambiguous fixes — batch 2, `dba1b63`.
3. ✅ Item 3 volume policy — `c4dfcc7`.
4. ✅ Item 11 circularity — `c4dfcc7`.
5. ✅ Item 14 — `c4dfcc7`.
6. ✅ Item 8/13 macro degradation — `5d2cbbe`. A failed macro-timeframe fetch used to
   leave `macro_bias` at its initialised `"NEUTRAL"` with nothing added to `degradation`,
   so a failed higher-timeframe read and a genuinely neutral macro trend rendered
   identically. `test_the_macro_series_is_actually_read` had documented this in its own
   docstring as "recorded rather than fixed"; that assertion was rewritten with the fix.
7. ✅ Audit Finding 15 — dependency versions pinned, `a26c545`.
8. ✅ Audit Finding 3 — decision-bar integrity. Never appeared in steps 1–6 at all; see
   the section above for why that is the most important thing on this page.

## Not on the roadmap, worth revisiting

- **A database for decision history.** Raised by Viktor, 1 September 2026. Every run's
  reasoning currently lands in flat files — `logs/phase7_decision_log_*.jsonl` and
  `phase7_state_*.json` — which is simple and fine for a single-user, single-machine
  tool that never executes trades. That stops being enough once someone wants to query
  *across* runs — win rate by risk regime, how often the AGGRESSIVE gate in item 14
  actually fires, that kind of cross-run analytics — at which point scanning a folder
  of JSONL gets slow. No such need has come up yet, so nothing is planned; if it does,
  the natural fit is a lightweight embedded database (SQLite, not a server) as a query
  layer alongside the existing logs, not a replacement for them.

## The machine was rebuilt

Windows was reinstalled on 30 August 2026, all drives wiped. Everything of value is on
GitHub at `375334a`; nothing lived only on disk except gitignored `logs/`.

**`docs/audit_package/environment_before_reinstall.txt`** records the exact library
versions and **Python 3.12.0** that produced the original golden baseline.
`requirements.txt` and `requirements-dev.txt` now pin exact versions — audit **Finding 15,
closed 1 September 2026** — so a fresh install can no longer silently resolve a different
pandas / numpy / pandas_ta and shift indicator output. Pinned to the versions verified
identical across both environments that ran the full suite that day (sandbox, Python 3.12.3;
Viktor's machine, Python 3.12.10): `pandas==3.0.5`, `numpy==2.2.6`, `matplotlib==3.11.1`,
`pandas_ta==0.4.71b0`, `requests==2.32.5`, `colorama==0.4.6`, `pytest==9.1.1`. The baseline
has since moved twice more, deliberately, at `dba1b63` and `c4dfcc7` — each time because a
real fix changed what the engine computes, verified by predicting the diff before
re-baselining (see Working practice below). **If the golden snapshot moves and neither
commit explains it, check this file's environment note before assuming the engine broke.**

After reinstalling: Python 3.12.0 (Viktor's machine is now on 3.12.10; both have verified
identical, correct results), git, `pip install -r requirements.txt -r requirements-dev.txt`,
and re-link the Claude desktop app to `D:\phase7_engine`.

## Working practice

- **Deliver as a `.patch`, never a zip.** `git apply --check <file>.patch` first, then
  `git apply`. Write the patch and message file into the repo over the device bridge,
  stage them out with explicit paths, then delete them.
- **Restore CRLF before diffing.** The repo is CRLF; Python text-mode writes produce LF.
- **`git diff --cached` beats hand-built `diff -ruN` + sed.** Batches 1–2 built patches by
  running `diff -ruN` on two directories and rewriting the headers into `diff --git` form
  by hand. Items 3/11/14 did it by staging the changed files into a throwaway git repo
  seeded from the pre-change state and running `git diff --cached` — correct `diff --git`
  headers for free, no header rewriting to get wrong.
- **Run the suite plain BEFORE re-baselining**, and **predict the diff in advance**. Items
  13, 14 and 15 each predicted exactly what would move — nine fields, one field, nothing —
  and each was right. Items 3/11/14 did the same: bias.score down slightly (the
  health-derived term removed from continuation_strength), confidence moving independently
  (no longer penalised/bonused by the removed structure/validation terms), everything
  downstream of confidence moving with it, nothing else. That is exactly what the diff
  showed.
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
19. **The plan is not the source. Work from the audit, not from the summary of it.**
    Four of the five Criticals were remediated, verified and signed off while the fifth
    sat unread in the report the whole time. It was absent from this file, so every check
    that consulted this file agreed the work was done — including three separate passes
    that re-read *this page* looking for what was left. Nobody re-opened the report until
    2 September. A derived document cannot tell you what it never contained.
20. **Fixing the instance you found does not close the item; the re-audit checks the
    pattern.** Sequence item 11 removed one duplicated-evidence term (trend_health, counted
    directly and via bias_score) and the item was marked done. The independent audit found
    the same pattern — a measurement counted once as a weighted factor and again as a bonus
    layered on top of the result those factors produced — in three more places nobody had
    re-checked once the first one was fixed.
