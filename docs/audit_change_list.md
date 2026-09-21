# Changes since the last independent audit

*A running list, kept by Claude under Viktor's delegation (PHASE7_NEXT.md, Open items).
It becomes the next independent auditor's scope. Whether the auditor is shown this file,
and in what form, is Viktor's call when the audit is planned. Nothing in it is
verification: every "guarded by" names the tests Claude wrote or pointed at. Whether
those tests guard what they claim to is exactly what the auditor is asked to check.*

## The baseline

The last independent round was the round-6 fix-verification (Meta Muse Spark 1.3,
14 September 2026; `docs/audit_reports/round6_fix-verification_2026-09-14/`). It was
sent a scoped package of nine files. **All nine match the tree at `e65a0f7` and every
commit back to `ac0a211`** (checked on 21 September by sha256 against each commit's
blobs, allowing for either line ending). No engine file changed between `ac0a211` and
`e65a0f7`, so `e65a0f7` is the baseline. The round did not see the whole engine, only
those nine files. `code_hash` at `e65a0f7` and at `ac0a211` is the same, `13908bba…`
(Python 3.12). Which commit the full round 6 of 13 September read was not checked
here.

Everything below landed after `e65a0f7`. Add one line per commit as each lands.

## Engine code — one line per commit, oldest first

Each line gives what changed, which finding it closes, and which tests guard it.
"Output" says whether a decision field or the golden snapshot moved.

| Commit | Date | What changed | Closes | Guarded by | Output |
|---|---|---|---|---|---|
| `a70fc1b` | 14 Sep | `models/signal_router.py`: a duplicate `@staticmethod` on `_finite_or_nan` removed | round-6 fix-verification's unprompted note | none specific; existing router tests exercise the function | none; `code_hash` moved |
| `66f1479` | 14 Sep | `core/panel_render.py`: a SETUP DIRECTION box states LONG or SHORT from `bias.raw`; prints CONTRADICTORY when bias and the plan disagree | Viktor's request (a SHORT setup had no word "SHORT" on the panel) | none when it landed; `test_setup_direction_box.py` since 21 Sep (below), including the CONTRADICTORY line | panel only |
| `39e0e79` | 14 Sep | `core/panel_render.py`: a NEUTRAL bias prints no direction box | Viktor's ruling on 66f1479's NEUTRAL line | none when it landed; `test_setup_direction_box.py` since 21 Sep (below) | panel only |
| `5be5d82` | 18 Sep | `data/data_fetcher.py`: `PHASE7_PINNED_DATA` set to a path that is not a directory now raises instead of silently going live. `core/engine_core.py`: `_save_state` writes atomically | Tier 1 of the 18 September session | `test_pinned_source.py` (added cases), `test_engine_state_atomic_write.py` | none |
| `f24a6e9` | 19 Sep | `indicators/trend_health.py`, `models/bias_engine.py`, `models/risk_model.py`: ADX's second read removed from `continuation_strength` | Item 11 (shared raw input reaching `bias_score` twice) | `test_no_circular_reasoning.py` (extended) | **golden re-baselined** (16 fields, all downstream of `bias_score`, 78.70 → 77.10 on the fixture; action unchanged). Moves `bias_score` on every run, so it **can change which trades are taken** near a threshold |
| `e2c6637` | 19 Sep | `models/bias_engine.py`: comment only. Records that four of six bias factors read the direction of close | recorded, not fixed — Viktor's call | `test_no_circular_reasoning.py` (documents the finding) | none |
| `9a35f1c` | 20 Sep | comments and docstrings in five engine modules and `utils/decision_log_backup.py`: stale citations of `PHASE7_NEXT.md` | item 9 of 20 September | none needed (comments) | none; `code_hash` unmoved (docstrings stripped; comments are not in the AST) |
| `a9d4b1f` | 20 Sep | `models/decision_model.py`: the run summary names the action's own reason, not the EV line. `core/panel_render.py`: VALIDATION prints "/100". `models/bias_engine.py`: comment | a refusal summarised as "worth taking" | `test_summary_names_the_action_reason.py`, `test_validation_score_has_a_denominator.py` | **golden re-baselined** (2 fields) |
| `119c8a3` | 21 Sep | `core/panel_render.py`: the TREND line prints "/100" | display | `test_trend_score_has_a_denominator.py` | panel only |
| `a530006` | 21 Sep | `core/panel_render.py`, `models/decision_model.py`: AERO named whatever the symbol; `nan/100` and `0.00` for absent scores; BUSD suffix order | review findings 1–3 | `test_panel_prints_only_what_was_computed.py` | panel and reasoning text |
| `e3f3d51` | 21 Sep | `models/risk_model.py`, `core/engine_core.py`: a direction parameter that decided nothing removed; a wrong-side stop now raises | review findings 8–10 | `test_plan_direction_and_side.py` | **golden re-baselined** (1 lineage field removed) |
| `afd8460` | 21 Sep | `live_trading.py`, `structure/structure.py`, `indicators/volume_profile.py`: fabricated zeros and "OK" in the simulated order; `.get(…, default)` on always-present keys; `utcnow()` | review findings 12–13 | `test_no_fabricated_defaults_remain.py` | none |
| `3f263c2` | 21 Sep | `models/entry_model.py`, `models/decision_model.py`, `core/engine_core.py`, `core/decision_contract.py`, `models/signal_router.py`, `indicators/trend_health.py`: the entry signals confirm the side the ladder chooses; unconfirmed is `NO-TRADE (SIGNAL UNCONFIRMED)` | review finding 11; **changes which trades are taken** — Viktor's ruling (DECISIONS, "the entry signals confirm") | `test_signal_confirms.py`; `test_code_fingerprint.py`, `test_direction_source.py`, `test_summary_names_the_action_reason.py` amended | **golden re-baselined** (3 fields added) |
| `05a12c7` | 21 Sep | `core/decision_log.py`: non-finite floats written as `null` with `allow_nan=False` (19); `read_with_report()`, and `read()` logs what it skips (20); the module docstring names the recorded source, `"pinned"` (21) | deferred-read findings 19–21 | `test_decision_log_record_format.py` | none on the decision; the log's spelling of "no value" is `null` from this commit on |
| `2c7a7d1` | 21 Sep | `core/decision_log.py`: `DecisionModel.BTC_STRESS_PENALTY`, `AVG_REWARD_R`, `EV_BREAKEVEN_BAND_R` added to `FINGERPRINTED_MODULES` | deferred-read finding 22 | `test_fingerprint_names_every_constant.py` (scans every fingerprinted module, so a future omission fails too) | **golden re-baselined**: `run_hash` (2 places) and the archive name (2 places) move; 3 leaves added under `module_constants`; no decision field |
| commit 4 of the six (the commit that adds this line) | 21 Sep | `core/lineage.py`: `verify_against_record()` checks an archive against its decision-log record (24); `verify_archive`'s docstring says it checks the archive against itself (24); the archive's JSON writes non-finite floats as `null` with `allow_nan=False` (19, archive half; latent); `write_archive`'s docstring states the overwrite under changed code (23) | deferred-read findings 23, 24, 19's archive half | `test_lineage_against_record.py` (11); `test_lineage.py` (1 added: a real run's archive matches its record) | none; the archive's bytes are unchanged for a payload with no non-finite float |

## Tests and tooling only

| Commit | Date | What changed | Guarded by |
|---|---|---|---|
| `5be5d82` | 18 Sep | the handover check's routine-noise filter (`docs/build/session_handover_check.py`) | `test_session_handover_check_ignored_filter.py` |
| `2f5fdaa` | 19 Sep | `githooks/pre-push` runs the handover check and stops a push on a finding; `.gitattributes` pins it `eol=lf` | `test_pre_push_hook.py` |
| `b68de08` | 20 Sep | `tests/test_pinned_source.py` and the pinned MANIFEST: the hash check portable across line endings | itself |
| `9c4917c` | 21 Sep | `tests/test_setup_direction_box.py`: 6 tests for `66f1479` and `39e0e79` — LONG, SHORT, NEUTRAL prints nothing, CONTRADICTORY takes neither side for either bias, the box follows bias on a run that takes no trade, and its place under DECISION | itself; four negative controls on `core/panel_render.py`, each failing it |

## Rulings since the baseline that change what the engine must do

- **Goal B — the backtesting phase, specified before it starts** (DECISIONS,
  15 September).
- **The entry signals confirm (work order F)** (DECISIONS, 21 September) — the change
  on this list made in order to change which trades are taken. `f24a6e9` can change
  them too, as a consequence: it moves `bias_score`.
- **The independent audit paused** (DECISIONS, 21 September). No backtesting before an
  independent re-audit of everything above (Constitution step 8).

## Found, open, and not yet a change

Recorded in `docs/PHASE7_NEXT.md` ("Review findings"): Viktor's calls 4–7, 16 and 18;
Claude's 17 (work order G) and 25–27 from the deferred read (19–24 have landed, above).
Each gets a line above when it lands.
