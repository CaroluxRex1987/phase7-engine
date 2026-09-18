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

- **Tip:** `dff7d00`. **Tag:** `portfolio-v1` at `99e022e`. **Release gate:** open,
  declared 15 September 2026 — see docs/PHASE7_DECISIONS.md, "Two goals, and the
  order they finish in."
- **code_hash:** `38458f20779d2709ed6402c69407339f797c69089ace3b18922ca5c8bb289fbb`
  — unmoved since `39e0e79` (14 September). No engine module touched by this patch
  either; confirmed on both the pristine and edited trees, not assumed.
- **Test suite, confirmed this session, Linux sandbox, Python 3.12.3, before any
  change was made:** 466 passed (pandas_ta) / 338 passed, 117 skipped (without
  pandas_ta) / 395 passed, 0 failed, 32 pre-existing errors (`run_tests.py`). Matches
  the baseline this project has carried since 14 September. Re-run after this
  patch's changes, all three configurations unchanged (docs-only patch) — see the
  commit message for the confirming run.
- **Handover check:** see the commit message for this session's actual
  `session_handover_check.py` output; not restated here since it is a git fact, not
  a standing one.

## The course correction — Goal B is on the slow burner

Decided 15 September 2026, written into the repository for the first time by this
patch (previously recorded only in a session-handover document kept outside git).
Full reasoning: docs/PHASE7_DECISIONS.md, under "Goal B — the backtesting phase,
specified before it starts," in the new subsection "Course correction — the engine
review, before any Goal B work." In short: before any Goal B implementation, the
engine gets reviewed for logical soundness — is the decision logic coherent, are the
constants justified, are the signals actually independent, is the thesis written
down anywhere. Goal B's full specification stands, ratified and unchanged; it is
deferred, not cancelled. The engine review itself has not yet been scoped — see the
scope conditions recorded alongside the course correction.

## Resolved this session

- **`FINGERPRINTED_CONFIG` and the bias weights — resolved, not an open gap.** The
  six bias weights (`WEIGHT_TREND_HEALTH` and siblings, `models/bias_engine.py`) are
  NOT in the `FINGERPRINTED_CONFIG` list in `core/decision_log.py` — that list holds
  `config.py`-level names only. They ARE fingerprinted, through the separate
  `FINGERPRINTED_MODULES` / `module_snapshot()` mechanism built for exactly this
  class of module-level constant, and both feed `run_hash`
  (`core/engine_core.py`, lines 1255-1257). Confirmed by reading the code and by a
  passing, purpose-built test:
  `tests/test_lineage.py::test_the_run_hash_moves_when_a_bias_weight_moves` asserts
  the run hash changes when `WEIGHT_TREND_HEALTH` moves from 0.30 to 0.35. Two runs
  with different weights do not log as identical configuration. Last session's grep
  that raised this as unverified was malformed, not wrong to have asked.
- **This file split into three.** docs/PHASE7_NEXT.md (this file, current-state
  only), docs/PHASE7_DECISIONS.md (standing governing material), and
  docs/PHASE7_HISTORY.md (the dated narrative and head-block archive). Reconciliation
  proof: the extracted content covering docs/PHASE7_DECISIONS.md and
  docs/PHASE7_HISTORY.md, reassembled in original document order, is byte-for-byte
  identical to the pre-split file — confirmed programmatically, not eyeballed. See
  the commit message for the exact line-range mapping. This file's own content is
  new, replacing what was previously this filename's role as the project's single
  entry point; it is not extracted from anywhere and is not part of that proof.
- **`session_handover_check.py` reworded** to stop referring to a "head block" this
  file no longer has, and to point at all three files where relevant. See the diff.

## Open items

- **`PHASE7_PINNED_DATA`'s silent live-API fallback — highest practical severity,
  urgent regardless of the course correction above.** Confirmed by reading
  `data/data_fetcher.py::pinned_source()` (lines 106-113): when the environment
  variable is set but does not resolve to a real directory, the function falls
  through to `return None`, and `get_tf()` (line 345-349) treats `None` as "go to
  the live API." A set-but-unresolvable path silently makes a run irreproducible
  without saying so. Not fixed this session; scoped as Tier 1, next.
- **`_save_state`'s non-atomic write, `core/engine_core.py` line 321.** Opens the
  state file with `open(path, "w")`, which truncates immediately, then
  `json.dump()`s into it. An interrupted write between those two steps leaves a
  truncated file that reads as "no prior run" on the next one. Fix: write to a temp
  file, then `os.replace`. Not fixed this session; scoped as Tier 1, next.
- **Engineering Notes are three commits stale** — `bd44b98`, `f9e5127`, `dff7d00` —
  last regenerated through Entry #127 (v1.30). Known and deliberate per the batching
  rule (docs/PHASE7_DECISIONS.md, "Working practice"); stated explicitly here rather
  than left implicit, per this project's own standing rule against silent gaps.
- **The Constitution's backtest-start condition** (Items 2, 3, 6, 18) has never been
  formally declared met the way the release gate was. Evidence points to it already
  being satisfied; nobody has said so the way Viktor said "the gate is open" for the
  release gate. Deferred behind the course correction above.
- **`session_handover_check.py`'s ignored-file filter** still does not cover
  `audit_package/` and `logs/`.
- **The seven test files that cite `docs/PHASE7_NEXT.md` by name in a docstring or
  comment** (`test_frame_ownership.py`, `test_imports.py`, `test_lineage.py`,
  `test_risk_regime_independence.py`, `test_router_no_fabricated_zero_defaults.py`,
  `test_decision_bar_integrity.py`, `test_exit_model_removal.py`) now cite the wrong
  file for facts that moved to docs/PHASE7_HISTORY.md — confirmed none of them
  functionally read or parse the file (checked directly; no `open()`/`Path()` call
  on it anywhere in the codebase), so nothing breaks, but the citations are stale.
  Same is true of prose inside `docs/build/build_engineering_notes.py`,
  `build_portfolio_document.py` and `build_ai_attribution.py` that cites the
  filename. Deliberately not fixed this session — scope was this file's own split,
  not a repository-wide citation sweep; named here so it is not lost.
- **Unrelated, not urgent:** confirm which YH programme permits AI-assisted
  examensarbete work.
