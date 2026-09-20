# Next step — read this first

*20 September 2026 (late evening). This file is the project's current-state entry point:
it states only what is true right now and what to do next, and is rewritten each session,
not appended to. Standing rules, ratified specifications and rulings in force live in
docs/PHASE7_DECISIONS.md. The dated record — including this file's previous version,
moved there verbatim this session — lives in docs/PHASE7_HISTORY.md. A citation of this
file written before the 18 September 2026 split — in the Engineering Notes, audit
reports, handovers or any other dated record — refers to content now in one of those
two files; dated records are not edited to say so (DECISIONS, "Ruling, 20 September
2026 — dated records are not edited to follow a move").*

*Amended 21 September 2026, one commit after it was written. `119c8a3` landed after
`b869a30` wrote this file, in the same session, and left five statements below false
and six more incomplete or unrecorded.
This amendment corrects them in place. It is **not** the once-per-session rewrite, and
no HISTORY move is owed by it — `b869a30` made that move.*

## PACE FIRST — read this before the rest of this file

Viktor judged, on his own, that 226 commits across 22 days had become hasty, and
ruled to slow down considerably (15 September 2026). **Do not open a session by
proposing work from "Open items" below, and do not treat it as a queue to clear.**
Ask what he wants to do first.

## Where the project is

This session opened fresh after `6e1baba`, with this file two commits stale — `a9d4b1f`
and `6e1baba` had both landed since it was written at `65a0aef`, by Viktor's own ruling
that the rewrite happens in a new chat (`6e1baba`'s commit message records it, because
the file itself could not). Asked what he wanted to do first, he chose the rewrite and
the TREND-line fix, in that order, as two separate commits — the rewrite being this one.

**What comes next is still planning the independent audit, and that is Viktor's
call** — which model, which package, whether the auditor sees the findings scrapped on
20 September, and the instruction for the selected model (DECISIONS, "Ruling, 20
September 2026 — the open-items list scrapped; an independent audit next"). He writes
his position first; Claude critiques it. He said this session that he is considering
putting that audit on pause, "since we fixed all the issues now." **That is a position,
not a ruling, and nothing here acts on it.** Claude's stated objection, for him to
answer when he does rule: the audit's purpose on this project has never been to close
known findings — it is to find the ones nobody has found yet, and the project's own
record says the recurring defect shape is the one that survives audits, on paths a
healthy run never takes. An empty open-items list is what an audit is for, not a reason
to skip one. The TREND-line defect fixed at `119c8a3` is a small instance of the same
argument: it was found by Viktor reading a live panel two hours after a patch that fixed
its identical twin, not by any review.

## Ruled this session

- **The NEXT rewrite lands first, as its own commit; the TREND-line fix follows as a
  second, separate commit.** Viktor's choice from three offered options. The fix is a
  code change and moves `code_hash`, so it is not mixed into a documentation commit —
  the same separation `6e1baba` made. Both landed, in that order: `b869a30`, then
  `119c8a3`.

## Where things stand, right now

- **Tip:** current as of `119c8a3`; the actual tip is the commit that amended this file
  (a commit cannot name its own hash). `119c8a3` was confirmed as GitHub's tip by a fresh
  sandbox clone on 21 September, which found `PHASE7_NEXT.md`, `PHASE7_HISTORY.md` and
  `core/panel_render.py` byte-identical to the verified tree and the new test file
  identical modulo CRLF.
  **Tag:** `portfolio-v1` at `99e022e`. **Release gate:** open, declared 15 September
  2026.
- **code_hash:** `35718f6b8c7c021f52ae566c266ab7fc8295c7e1bff89121bba8a20272168b3c` —
  moved at `119c8a3`, the TREND-line fix, from `b02137660111…`, which had itself moved at
  `a9d4b1f` from `bb47ab53…`, where it stood since `f24a6e9`. Unmoved by `6e1baba`, by
  `b869a30` and by this amendment — none of the three touches a `.py` file outside
  `docs/`, which `core/code_fingerprint.py` excludes by directory. Recomputed under
  Python 3.12 on `119c8a3`'s tree and on this amendment's applied tree; not assumed.
- **code_hash is only comparable within one Python minor version, and that bit this
  session.** `core/code_fingerprint.py` hashes `ast.dump` output, which is a CPython
  implementation detail; the file says so under "WHAT IT DOES NOT SURVIVE". The sandbox
  used this session had `python3` = 3.11.15 by default and reported
  `938720cd…` on an unmodified `6e1baba` tree. Nothing had moved: Python 3.12.3 on the
  same tree gives `b0213766…`, matching Viktor's Windows decision-log record, and
  Python 3.13.13 gives a third value again. **Every `code_hash` claim about this
  project must be computed under Python 3.12** (Viktor runs 3.12.10; the pinned
  requirements record 3.12.10 and 3.12.3). A hash that "moved" is a question about the
  interpreter before it is a question about the code.
- **Golden snapshot:** re-baselined at `a9d4b1f`, two fields only. Unchanged by
  `6e1baba`, by `b869a30`, by `119c8a3` and by this amendment, and no re-baseline has
  been run since `a9d4b1f`. `119c8a3` changed a panel-rendering string only; nothing on
  the decision path has moved since `a9d4b1f`.
- **Test suite**, moved at `119c8a3`, which added a fixture-free file of 4 tests:
  **504 passed / 0 failed** with `pandas_ta`; **372 passed / 121 skipped** without it;
  `run_tests.py` **433 passed / 0 failed / 32 errors**. The 32 are fixture-collection
  errors and have not moved since long before this session — the new tests take no
  fixture, which is why the error count stayed flat while the passed count rose by four,
  and no behavioural failure is hidden in them. Reported at `119c8a3` from a Linux
  sandbox and from Viktor's Windows machine, agreeing on all three; the sandbox clone
  type for that run is not recorded here. This amendment is documentation only and does
  not move them.
- **`a9d4b1f` is confirmed on Windows from Viktor's own live run**, not predicted from
  Linux: the panel printed `VALIDATION : … 35.00/100` and the arithmetic matched (50,
  +10 macro, −25 volume divergence); the EV line printed the new wording at +0.14R with
  confidence 38; the decision log's last record carries a summary naming the risk
  reason with no EV sentence; and that record carries
  `code_hash b02137660111…`. The prediction made on Linux held on his machine.
- **`119c8a3` is confirmed on Windows from Viktor's own live run**, not predicted from
  Linux: AEROUSDT 4h at 00:02 on 21 September 2026, decision NO-TRADE (RISK TOO HIGH).
  The panel printed `TREND : BULLISH / STRONG (Score: 100.00/100)` with
  `VALIDATION : WEAK (Score: 35.00/100)` on the line below — the denominator the fix
  added, on the line that had been missing it, beside the one `a9d4b1f` had already
  fixed. `RISK REGIME: UNKNOWN` on that run was checked against `models/risk_model.py`
  and is the documented behaviour of the stop-distance branch, not a defect.
- **Engineering Notes:** through Entry #141 (v1.33), which covers `4629002`. **Ten
  commits behind** — `3a899b5`, `92775ea`, `53394ff`, `982e70f`, `65a0aef`, `a9d4b1f`,
  `6e1baba`, `b869a30`, `119c8a3` and this one — by Viktor's choice, under the standing
  batching rule. (Nine through `119c8a3`; the tenth is this amendment, counted the same
  way the previous version counted itself.) If the independent audit's package includes
  the Notes, regenerate them before building it.
- **Portfolio Document and AI-Attribution Statement:** both current with their scripts.
  `build_portfolio_document.py` was corrected at `6e1baba` and its PDF regenerated in
  that same commit; `build_ai_attribution.py` has not changed since `9a35f1c`, whose
  PDF was regenerated at `c745a67`.
- **Handover check / pre-push hook:** the hook reported `SUMMARY: clean` on the pushes
  of `4629002`, `3a899b5`, `92775ea`, `53394ff` and `982e70f` (Viktor's report), and
  again on the push that carried this session's work — a first attempt had failed on
  DNS, which is not a hook result. **Whether that push carried both `b869a30` and
  `119c8a3` or only the latter was not established**, so nothing here claims a
  per-commit result for either. **Its result on the pushes of `65a0aef`, `a9d4b1f` and
  `6e1baba` was not reported** either, so nothing here claims it was clean on them.

## Resolved this session

- **The once-per-session rewrite of this file**, deferred by `6e1baba` to this session.
  The previous version is in HISTORY verbatim, headings demoted one level.
- **`a9d4b1f`'s and `6e1baba`'s landing facts** folded in above — Windows counts,
  Viktor's live-run confirmation, the new `code_hash`, the re-baselined snapshot.
- **The TREND line's missing denominator, fixed at `119c8a3`** — the second of the two
  commits ruled above, and the one that ruling predicted. A new fixture-free test file of
  4 tests with three negative controls; the denominator is held from the parse tree and
  from running the indicator, each proven load-bearing separately. The whole panel was
  swept afterwards: no other score printed by it is missing its scale.
- **Closed at `6e1baba`, and no longer open items here:** the Portfolio Document's
  "four independent runs … no prior involvement in the build" claim, and README's
  "every raw report from every round is in `docs/audit_reports/`".

## Open items

Items marked **Viktor's call** are his to decide; he writes his position first and
Claude critiques it.

- **Viktor's call — planning the independent audit, or pausing it:** which model, the
  package (the standing default for a fresh Tier-1 audit is the full package), whether
  the auditor sees the scrapped findings, and the instruction for the selected model —
  or whether the round is paused at all, which he raised this session and has not
  ruled. Not started.
- **Found, not checked:** HISTORY's 5 September "The record corrected from the bill"
  says the eleven round-2 observations came from a Qwen run; the
  `round2_kimi_k3_20260902/README.md`, filed later, says they are Kimi's. Which is the
  later word, and whether the earlier one is marked superseded, was not examined.
- **The pre-push hook is installed per clone, not per repository.** After any re-clone
  (including after a machine wipe), run `git config core.hooksPath githooks`;
  `session_handover_check.py` section 6 flags a clone without it.
- **Unrelated, not urgent:** confirm which YH programme permits AI-assisted
  examensarbete work.
