# Next step — read this first

*20 September 2026. This file is the project's current-state entry point: it states only
what is true right now and what to do next, and is rewritten each session, not appended
to. Standing rules, ratified specifications and rulings in force live in
docs/PHASE7_DECISIONS.md. The dated record — including this file's previous version,
moved there verbatim this session — lives in docs/PHASE7_HISTORY.md.*

## PACE FIRST — read this before the rest of this file

Viktor judged, on his own, that 226 commits across 22 days had become hasty, and
ruled to slow down considerably (15 September 2026). **Do not open a session by
proposing work from "Open items" below, and do not treat it as a queue to clear.**
Ask what he wants to do first.

## Where things stand, right now

- **Tip:** current as of `c7ced36`; the actual tip is the docs commit that wrote this
  file (a commit cannot name its own hash). **Tag:** `portfolio-v1` at `99e022e`.
  **Release gate:** open, declared 15 September 2026 — see docs/PHASE7_DECISIONS.md,
  "Two goals, and the order they finish in."
- **code_hash:** `bb47ab537314953e16b2db2fcf24003ead64eb5538a30221a6578d518bb7d34d` —
  unmoved by `5c73e24`, `c7ced36` and this commit (all docs-only). For this commit it was
  recomputed on the pre- and post-patch trees, not assumed.
- **Golden snapshot:** last changed at `f24a6e9` (checked with `git log` on the
  snapshot file); `code_hash` has been `bb47ab53…` since that commit, so no engine
  file has changed since either.
- **Test suite — engine code identical since `5c73e24`:**
  - Windows (Viktor's machine, pandas_ta): **485 passed / 0 failed at `5c73e24`, read
    from his pasted output.** At `c7ced36`, 485 / 0 is his confirmation by proceeding
    (told to stop on any other count; output not pasted).
  - Linux sandbox, clone made with `core.autocrlf=true` (CSVs check out CRLF, as on
    Windows): 485 passed / 0 failed with pandas_ta; 354 passed / 120 skipped without
    it; `run_tests.py` 414 passed / 0 failed / 32 errors — the same 32 by name as the
    standing baseline.
  - **Standing platform difference:** a default LF Linux or macOS checkout gives
    484 / 1 — `tests/test_pinned_source.py::test_manifest_hashes_match_the_files`,
    because `.gitattributes`'s `* text=auto` changes the pinned CSVs' bytes per platform
    while `MANIFEST.json` pins raw-byte hashes. Always reported, never quietly
    subtracted. The fix is an open item below.
- **Engineering Notes:** current. Regenerated at `c7ced36` through Entry #135 (v1.31) —
  eight entries, #128–#135, covering all eleven commits `bd44b98`..`5c73e24`.
  `c7ced36` itself and this commit are not yet covered; both are docs-only.
- **Handover check / pre-push hook:** ran on the push of `c7ced36`, `SUMMARY: clean`.

## Resolved since the previous version of this file

- **`c7ced36` — Engineering Notes regenerated through Entry #135 (v1.31), docs-only.**
  Viktor's three rulings: regenerate now rather than batch later; give the course
  correction (#129) and the `git add -A` incident (#133) entries of their own rather
  than folding them into neighbours; and record the Windows 485 in the repo's own
  wording, "confirmation by proceeding." The `code_hash` chain was recomputed per
  commit for those entries, not assumed: `38458f20…` from `portfolio-v1` through
  `4a97c32`, `5080ccf0…` at `5be5d82`, `bb47ab53…` at `f24a6e9` and every commit since.
- **Engineering Notes staleness — closed** by `c7ced36`.
- **The untracked handover PDF — closed.** Viktor moved
  `Phase7_Session_Handover_2026-09-15.pdf` out of `Claude outputs/` to his project
  folder outside the repository (`D:\Phase_7_Engine_Random_Files`), where it now exists
  as two copies. That they are byte-identical was checked on 19 September; on
  20 September only their names and equal sizes (17,189 bytes) were re-checked, by
  directory listing over the device bridge.
- **The seven test files that cite `docs/PHASE7_NEXT.md` do not read it.** Checked by
  static search only: none of them opens the file; the citations are in docstrings and
  comments. A dynamically built path would not show up in that search. The citations
  themselves are still stale — see Open items.
- **README.md checked against this file, in this commit.** Fifteen commits behind before
  it (last touched at `ebb0a46`, 15 September). Two things were actually stale and are
  fixed: both test-count statements (466 / 338 + 117 skipped / `run_tests.py` 395 → the
  current 485 / 354 + 120 skipped / 414), and the repository-layout tree, which lacked
  `githooks/` (added at `2f5fdaa`). Found and deliberately **not** changed, because they
  predate the fifteen commits and are omissions rather than staleness: the layout tree
  also omits `Claude outputs/` and `decision_log_backups/`, and README does not point a
  reader at `docs/PHASE7_NEXT.md` / `PHASE7_DECISIONS.md` / `PHASE7_HISTORY.md` at all.

## The course correction — Goal B is on the slow burner

Decided 15 September 2026. Full reasoning: docs/PHASE7_DECISIONS.md, under "Goal B —
the backtesting phase, specified before it starts," in the subsection "Course
correction — the engine review, before any Goal B work." In short: before any Goal B
implementation, the engine gets reviewed for logical soundness — is the decision
logic coherent, are the constants justified, are the signals actually independent, is
the thesis written down anywhere. Goal B's full specification stands, ratified and
unchanged; it is deferred, not cancelled.

One finding from that eventual review was pulled forward and fixed on 18 September,
narrowly, ahead of the review being scoped, and a second was recorded but not fixed —
see docs/PHASE7_HISTORY.md, "18 September 2026 — PHASE7_NEXT.md as it stood at
`742b514`." The review itself, its completion boundary, and everything else it would
cover remain exactly as unscoped as before.

## Open items

Items marked **Viktor's call** are his to decide; he writes his position first and
Claude critiques it.

- **Viktor's call — the six bias-weight magnitudes and the engine's written thesis.**
  0.30/0.20/0.15/0.15/0.10/0.10 remain unreviewed hand-picked judgment calls;
  `Phase7_Roadmap.pdf` says so in its own words, and nothing in the repository gives a
  reason for the specific split. The market thesis the engine review's own scope
  conditions ask for is still unwritten.
- **Viktor's call — five points from the 15 September PDF, "A input and raised
  questions on the current output of the engine"** (kept outside the repository), none
  found in PHASE7_NEXT, DECISIONS or HISTORY by keyword search (not a full read):
  1. the +0.69R expected value treats the confidence score as if it were a win rate;
  2. volume may be counted three times;
  3. the +10.55 BTC confidence boost;
  4. whether macro ×0.90 is enough against the macro trend;
  5. what the "5.00" validation score is out of.
  The PDF's sixth point, the /102 denominator, is documented in code as deliberate.
  Whether these five go into the engine review's scope is his decision.
- **Viktor's call — retiring "To do list Claude Phase 7 Engine.pdf"** (outside the
  repository). It is stale: every "Immediate" item on it landed at `5be5d82` and
  `4a97c32`.
- **The four unchecked factors have been traced, and the finding is open for Viktor's
  decision.** Four of the six factors — trend health (0.30), structure regime (0.20),
  SuperTrend direction (0.15), macro bias (0.10), three quarters of the blend — are
  four different transforms of one measurement: the recent direction of `close`. They
  will disagree at turning points but agree by construction in any sustained trend,
  and `bias_score` presents that agreement as four independent confirmations. Recorded
  rather than fixed, because acting on it means reweighting or dropping factors, which
  is a trading judgment this project cannot evaluate until backtesting is unblocked.
  Full reasoning: docs/PHASE7_DECISIONS.md, "Second engine-review finding, recorded not
  fixed."
- **The earlier claim that structure_regime had been checked was based on a false
  description and is withdrawn** (18 September). `models/bias_engine.py` described it
  as "structure.py's swing-based regime label"; it is actually a 5-bar vs 15-bar
  close-mean gap, and `swing_struct` reaches nothing but the panel. The description is
  corrected and the real behaviour is pinned by a test.
- **RSI still reaches `bias_score` through two factors,** and the written exemption for
  it is narrower than its prose claims — measured r = 0.83 in uptrends against r = 0.37
  in downtrends. Worth at most 1.5 points of `bias_score`. Recorded, not fixed, for the
  same reason as the four-factor finding.
- **`test_pinned_source.py::test_manifest_hashes_match_the_files` is not portable and
  needs a decision.** It hashes the raw bytes of CSVs that `* text=auto` checks out
  differently per platform, so it passes only on the OS that generated `MANIFEST.json`.
  The clean fix is to hash line-ending-normalised content in both
  `docs/build/make_pinned.py` and the test, then regenerate the manifest — three files,
  no engine change. Not taken on 18, 19 or 20 September (not requested).
- **The pre-push hook is installed per clone, not per repository.**
  `git config core.hooksPath githooks` lives in `.git/config`, which a fresh clone does
  not carry. `session_handover_check.py` section 6 flags a clone without it. After any
  re-clone (including after a machine wipe), run that one command.
- **The engine review itself still has no completion boundary and is still not
  formally scoped** — unchanged since 15 September; see "The course correction" above.
- **The Constitution's backtest-start condition** (Items 2, 3, 6, 18) has never been
  formally declared met the way the release gate was. Unchanged. Deferred behind the
  course correction above.
- **Stale citations of `docs/PHASE7_NEXT.md`** in seven test files'
  docstrings/comments (`test_frame_ownership.py`, `test_imports.py`, `test_lineage.py`,
  `test_risk_regime_independence.py`, `test_router_no_fabricated_zero_defaults.py`,
  `test_decision_bar_integrity.py`, `test_exit_model_removal.py`) and inside
  `docs/build/build_engineering_notes.py`, `build_portfolio_document.py` and
  `build_ai_attribution.py`. They point at content that moved to DECISIONS or HISTORY
  in the 18 September split. Harmless to test behaviour (see Resolved above), not fixed.
- **README.md's pre-existing omissions** — `Claude outputs/` and
  `decision_log_backups/` absent from the layout tree; no pointer to the three
  PHASE7_* documents. Found on 20 September, left for a decision rather than widened
  into this commit.
- **Unrelated, not urgent:** confirm which YH programme permits AI-assisted
  examensarbete work.
