# Next step — read this first

*18 September 2026 — this file rewritten as the project's current-state entry point,
replacing its previous role as a single chronological file. Standing rules, ratified
specifications and rulings that remain in force now live in
docs/PHASE7_DECISIONS.md. The dated narrative record of how the project got here —
the head-block archive and every dated session's own account of what it found and
did — now lives in docs/PHASE7_HISTORY.md. This file states only what is true right
now and what to do next; it is rewritten each session, not appended to. If you are
looking for what happened on a specific date, in a specific audit round, or why a
past patch did what it did, that is in HISTORY, not here.*

## PACE FIRST — read this before the rest of this file

Viktor judged, on his own, that 226 commits across 22 days had become hasty, and
ruled to slow down considerably (15 September 2026). **Do not open a session by
proposing work from "Open items" below, and do not treat it as a queue to clear.**
Ask what he wants to do first.

## Where things stand, right now

- **Tip:** `f24a6e9`. **Tag:** `portfolio-v1` at `99e022e`. **Release gate:** open,
  declared 15 September 2026 — see docs/PHASE7_DECISIONS.md, "Two goals, and the
  order they finish in."
- **code_hash:** `bb47ab537314953e16b2db2fcf24003ead64eb5538a30221a6578d518bb7d34d`
  — moved from `5080ccf0490502ad72dadaf6c3c525d19792139ea52d7fb15ee28a923ab5d189`
  (unmoved since 18 September) by this session's patch (`f24a6e9`), which touched
  one engine file's fingerprint, `indicators/trend_health.py`. `models/bias_engine.py`
  and `models/risk_model.py` were also edited but comment-only — confirmed
  programmatically that neither file's per-file fingerprint moved, since
  `core/code_fingerprint.py` hashes the docstring-stripped parse tree and plain `#`
  comments were never part of what it dumps.
- **Test suite, this session:** 474 passed (pandas_ta) / 343 passed, 120 skipped
  (without pandas_ta) / 403 passed, 0 failed, 32 pre-existing errors (`run_tests.py`,
  the same 32 by name as the standing baseline — diffed programmatically, not just
  counted). Confirmed on BOTH the Linux sandbox and Viktor's own Windows machine —
  he ran all three configurations himself before committing and every count matched.
- **Golden snapshot:** applicable this session — the patch touched engine code
  reachable on the golden fixture's path (ADX 31.96 at the decision bar fed
  `continuation_strength`'s now-removed component). Moved in exactly 16 leaf
  fields, all causally downstream of `bias.score` — diffed old vs new
  programmatically at leaf granularity. Full field list: `f24a6e9`'s commit
  message.
- **Handover check:** not run as a script this session — this session has no shell
  access to Viktor's machine, only the device-file bridge, so it was approximated
  from `git status --short`, read twice around the commit rather than run as
  `session_handover_check.py`. One open item came out of that reading — see "Open
  items" below — everything else was clean: no other untracked or modified files,
  no loose delivery files (the patch and commit-message files are gitignored and
  were deleted after commit regardless), nothing staged uncommitted.

## The course correction — Goal B is on the slow burner

Decided 15 September 2026. Full reasoning: docs/PHASE7_DECISIONS.md, under "Goal B —
the backtesting phase, specified before it starts," in the subsection "Course
correction — the engine review, before any Goal B work." In short: before any Goal B
implementation, the engine gets reviewed for logical soundness — is the decision
logic coherent, are the constants justified, are the signals actually independent, is
the thesis written down anywhere. Goal B's full specification stands, ratified and
unchanged; it is deferred, not cancelled.

One finding from that eventual review was pulled forward and fixed this session,
narrowly, ahead of the review being scoped — see "Resolved this session" below. The
review itself, its completion boundary, and everything else it would cover remain
exactly as unscoped as before this session's fix.

## Resolved this session

- **Bias-weight independence — one finding, fixed narrowly by Viktor's own choice.**
  Asked directly whether the six bias weights are defensible, and to write a
  position on it first rather than have it handed back for scoping. Found that
  `trend_health` (weight 0.30) and `reversal_continuation` (weight 0.10) — 40% of
  `bias_score`'s blend — both read the same raw `adx_val` and score it on two
  different monotonic curves: not Item 11's defect (a reused *computed value*), a
  reused raw *input*, which is why it passed Item 11's audit and six subsequent
  rounds. Given a three-way choice — fix independence only, write a reasoned
  rationale for the weight magnitudes, or both — Viktor chose independence only.
  `indicators/trend_health.py`'s `continuation_strength` no longer has an ADX
  component; its ceiling honestly drops from 60 to 35, not rescaled back up, the
  same standard the original Item 11 fix used. `models/risk_model.py`'s own,
  separate read of raw ADX for the risk-regime gate was already independent of
  `bias_score` and needed no code change, only a comment correction. Full
  reasoning, what was deliberately left out of scope, and full verification detail:
  docs/PHASE7_DECISIONS.md, "First engine-review finding, fixed — bias-weight
  independence," and `f24a6e9`'s commit message.
- **The patch-delivery process itself changed.** Delivering that patch, `git add -A`
  swept an untracked file (`Claude outputs/Phase7_Session_Handover_2026-09-15.pdf`)
  toward staging — caught only by reading `git status --short` before committing,
  which is a carefulness step, not a structural one. The patch-delivery skill was
  updated (proposed to Viktor for review, not yet confirmed saved) to add files by
  name instead of `git add -A` on his real repo going forward, so an unrelated
  untracked file cannot be staged regardless of what else is sitting in the repo at
  commit time.

## Open items

- **The weight magnitudes themselves — 0.30/0.20/0.15/0.15/0.10/0.10 — remain
  unreviewed hand-picked judgment calls.** `Phase7_Roadmap.pdf` says so in its own
  words; nothing in the repository gives a reason for the specific split. Explicitly
  out of scope for this session's fix, by Viktor's choice, not an oversight. Writing
  down the market thesis the engine review's own scope conditions ask for is still
  undone too.
- **`volume_sentiment`'s, `supertrend_direction`'s and `macro_bias`'s own source
  computations were not re-checked** for hidden shared raw inputs with each other or
  with `trend_health`/`reversal_continuation` — only the one pair this session's
  review found was checked and fixed. structure_regime *was* checked (built from
  swing highs/lows, confirmed to share nothing with ADX/RSI).
- **The engine review itself still has no completion boundary and is still not
  formally scoped** — unchanged from before this session; see "The course
  correction" above.
- **An untracked file needs a decision.**
  `Claude outputs/Phase7_Session_Handover_2026-09-15.pdf` was sitting untracked in
  the repo when this session's patch was delivered, got caught mid-`git add -A`
  before it could ride into the commit, and was left exactly where it was —
  neither committed, deleted, nor explained. Whether it belongs in git (like the
  other dated handover documents already tracked in `Claude outputs/`) or was never
  meant to be there is Viktor's call, not made this session.
- **The Constitution's backtest-start condition** (Items 2, 3, 6, 18) has never been
  formally declared met the way the release gate was. Unchanged from before this
  session. Deferred behind the course correction above.
- **The seven test files that cite `docs/PHASE7_NEXT.md` by name** in a docstring or
  comment (`test_frame_ownership.py`, `test_imports.py`, `test_lineage.py`,
  `test_risk_regime_independence.py`, `test_router_no_fabricated_zero_defaults.py`,
  `test_decision_bar_integrity.py`, `test_exit_model_removal.py`), and the same
  citation inside `docs/build/build_engineering_notes.py`, `build_portfolio_document.py`
  and `build_ai_attribution.py` — unchanged from before this session, still stale,
  still not fixed (scope was this session's independence finding, not a
  repository-wide citation sweep).
- **Engineering Notes are six commits stale** — `bd44b98`, `f9e5127`, `dff7d00`,
  `4a97c32`, `5be5d82`, `f24a6e9` — last regenerated through Entry #127 (v1.30).
  Known and deliberate per the batching rule (docs/PHASE7_DECISIONS.md, "Working
  practice"); stated explicitly rather than left implicit.
- **Unrelated, not urgent:** confirm which YH programme permits AI-assisted
  examensarbete work.
