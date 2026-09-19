# Next step — read this first

*19 September 2026. This file is the project's current-state entry point: it states only
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

- **Tip:** current as of `2f5fdaa`; the actual tip is the docs commit that wrote this
  file (a commit cannot name its own hash). **Tag:** `portfolio-v1` at `99e022e`.
  **Release gate:** open, declared 15 September 2026 — see docs/PHASE7_DECISIONS.md,
  "Two goals, and the order they finish in."
- **code_hash:** `bb47ab537314953e16b2db2fcf24003ead64eb5538a30221a6578d518bb7d34d` —
  unmoved by `2f5fdaa`. Recomputed on the pre- and post-patch trees, not assumed:
  `core/code_fingerprint.py` walks `.py` files only, and the patch added no engine file.
- **Golden snapshot:** untouched by `2f5fdaa` (no engine code in the diff;
  `test_golden_path` passed).
- **Test suite, at `2f5fdaa`:**
  - Windows (Viktor's machine, pandas_ta): expected 485 passed / 0 failed. He was told to
    stop at that step on any other count and proceeded; the output itself was not pasted
    into the session, so this is his confirmation by proceeding, not a count Claude read.
  - Linux sandbox, clone made with `core.autocrlf=true` (the patch-delivery skill's
    setup, so the CSVs check out CRLF as on Windows): 485 passed / 0 failed with
    pandas_ta; 354 passed / 120 skipped without it; `run_tests.py` 414 passed / 0 failed
    / 32 errors — the same 32 by name as the standing baseline, diffed programmatically.
  - **Standing platform difference:** on a default LF Linux or macOS checkout,
    `tests/test_pinned_source.py::test_manifest_hashes_match_the_files` fails, because
    `.gitattributes`'s `* text=auto` changes the pinned CSVs' bytes per platform while
    `MANIFEST.json` pins raw-byte hashes. Measured at `742b514` on a fresh default clone:
    475 passed / 1 failed. At `2f5fdaa` the prediction is 484 / 1 — **not measured**,
    because that patch is built against the CRLF tree and does not apply to an LF
    checkout. Every sandbox figure is reported with this failure included, never quietly
    subtracted. The fix is still an open item below.
- **Handover check:** ran for real on Viktor's Windows machine as the pre-push hook's
  first run, on the push of `2f5fdaa` — every section clean, `SUMMARY: clean`, 30
  ignored routine-noise entries filtered, section 6 "installed". That is also the first
  Windows evidence that the hook runs at all. This session had file access to his
  machine but no shell, so no other run of the script on his machine was possible.

## Resolved this session

- **The pre-push hook, built and landed at `2f5fdaa`.** Proposed in the 18 September
  session, never built, and missing from the previous Open items — Viktor raised it at
  the start of this session as the one concrete follow-up outstanding.
  `githooks/pre-push` runs `docs/build/session_handover_check.py` on every `git push`;
  a finding stops the push. Viktor's ruling (option A of three): stop, consult with
  Claude, and override with `git push --no-verify` if the answer is push. He first asked
  for "only warn"; Claude pointed out a warning cannot also let him decide "push or not",
  because the push would already have gone. Fails closed if the check cannot run.
  Ruling and reasoning: docs/PHASE7_DECISIONS.md, handover checklist item 9 and the
  ruling beneath it. Full verification, wrong turns and predictions: `2f5fdaa`'s commit
  message.
- **Two things verification found, both recorded in that commit message:** a single
  `git apply` of a patch that adds a `.gitattributes` rule and a new file together
  writes the new file under the *old* attributes (the hook came out CRLF on an
  autocrlf clone), so the delivery applied `.gitattributes` first as its own step; and
  on Linux git 2.43 a hook that cannot be executed at all makes `git push` hang rather
  than fail, so the push tests carry a timeout.
- **Previous version of this file moved to HISTORY verbatim.** The 18 September
  session's account existed only here — HISTORY had not been appended to since the
  split — so it was moved whole before this rewrite, not summarised.

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

- **The weight magnitudes themselves — 0.30/0.20/0.15/0.15/0.10/0.10 — remain
  unreviewed hand-picked judgment calls.** `Phase7_Roadmap.pdf` says so in its own
  words; nothing in the repository gives a reason for the specific split. Explicitly
  out of scope for the 18 September fix, by Viktor's choice, not an oversight. Writing
  down the market thesis the engine review's own scope conditions ask for is still
  undone too.
- **The four unchecked factors have now been traced, and the finding is open for
  Viktor's decision.** Four of the six factors — trend health (0.30), structure
  regime (0.20), SuperTrend direction (0.15), macro bias (0.10), three quarters of
  the blend — are four different transforms of one measurement: the recent direction
  of `close`. They will disagree at turning points but agree by construction in any
  sustained trend, and `bias_score` presents that agreement as four independent
  confirmations. Recorded rather than fixed, because acting on it means reweighting
  or dropping factors, which is a trading judgment this project cannot evaluate until
  backtesting is unblocked. Full reasoning: docs/PHASE7_DECISIONS.md, "Second
  engine-review finding, recorded not fixed."
- **The earlier claim that structure_regime had been checked was based on a false
  description and is withdrawn.** `models/bias_engine.py` described it as
  "structure.py's swing-based regime label"; it is actually a 5-bar vs 15-bar
  close-mean gap, and `swing_struct` reaches nothing but the panel. The check was run
  against a mechanism the factor does not use. The description is corrected and the
  real behaviour is now pinned by a test.
- **RSI still reaches `bias_score` through two factors,** and the written exemption
  for it is narrower than its prose claims — measured r = 0.83 in uptrends against
  r = 0.37 in downtrends. Worth at most 1.5 points of `bias_score`. Recorded, not
  fixed, for the same reason as above.
- **`test_pinned_source.py::test_manifest_hashes_match_the_files` is not portable
  and needs a decision.** It hashes the raw bytes of CSVs that `* text=auto` causes
  git to check out differently per platform, so it passes only on the OS that
  generated `MANIFEST.json`. The clean fix is to hash line-ending-normalised content
  in both `docs/build/make_pinned.py` and the test, then regenerate the manifest —
  three files, no engine change, works on Windows immediately. Not taken on 18 September
  (to keep that patch to one subject) nor on 19 September (not requested).
- **The pre-push hook is installed per clone, not per repository.**
  `git config core.hooksPath githooks` lives in `.git/config`, which a fresh clone does
  not carry. `session_handover_check.py` section 6 now flags a clone without it, so a
  missing hook is visible at every hand-run of the check — but nothing can make it
  impossible. After any re-clone (including after a machine wipe), run that one command.
- **The engine review itself still has no completion boundary and is still not
  formally scoped** — unchanged since 15 September; see "The course correction"
  above.
- **The untracked handover PDF is gone from disk; what happened to it is unrecorded.**
  `Claude outputs/Phase7_Session_Handover_2026-09-15.pdf` was never committed (checked:
  `git log --all` on that path is empty) and was no longer in `Claude outputs/` on
  Viktor's disk on 19 September (checked by directory listing over the device bridge).
  Whether he deleted it deliberately or moved it elsewhere is not known to Claude — one
  line from him closes this item.
- **The Constitution's backtest-start condition** (Items 2, 3, 6, 18) has never been
  formally declared met the way the release gate was. Unchanged. Deferred behind the
  course correction above.
- **The seven test files that cite `docs/PHASE7_NEXT.md` by name** in a docstring or
  comment (`test_frame_ownership.py`, `test_imports.py`, `test_lineage.py`,
  `test_risk_regime_independence.py`, `test_router_no_fabricated_zero_defaults.py`,
  `test_decision_bar_integrity.py`, `test_exit_model_removal.py`), and the same
  citation inside `docs/build/build_engineering_notes.py`, `build_portfolio_document.py`
  and `build_ai_attribution.py` — still stale, still not fixed (the 18 September scope
  was the independence finding, and 19 September's was the pre-push hook — neither a
  repository-wide citation sweep).
- **Engineering Notes are ten commits stale** at `2f5fdaa` — `bd44b98`, `f9e5127`,
  `dff7d00`, `4a97c32`, `5be5d82`, `f24a6e9`, `2fee78f`, `e2c6637`, `742b514`,
  `2f5fdaa` — last regenerated through Entry #127 (v1.30), and this docs commit makes
  eleven. Known and deliberate per the batching rule (docs/PHASE7_DECISIONS.md,
  "Working practice"); stated explicitly rather than left implicit. The batching rule's
  own trigger ("once several commits have landed") has arguably been met for a while —
  whether to regenerate now is Viktor's call.
- **Unrelated, not urgent:** confirm which YH programme permits AI-assisted
  examensarbete work.
