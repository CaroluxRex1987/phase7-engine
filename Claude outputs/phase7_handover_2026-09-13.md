# Phase-7 session handover — 13 September 2026 (end of session)

Read this first, then `docs/PHASE7_NEXT.md`'s head block (which this session did NOT
update — see "Still open" below). Repo: `D:\phase7_engine` on Viktor's machine, GitHub
`CaroluxRex1987/phase7-engine`. Standing constraint: **no shell on Viktor's machine.**
Claude works in its own cloud sandbox, delivers finished files over the device bridge,
verifies byte-for-byte, and Viktor runs `git` himself from Windows `cmd.exe`. Follow the
`anthropic-skills:patch-delivery` skill for sandbox setup, verification, and delivery
mechanics — clone with `-c core.autocrlf=true`, two venvs (with/without
`pandas_ta==0.4.71b0`), three test configs, CRLF discipline, one-patch-at-a-time
delivery, the `git add -A` trap (always `git reset` the delivery files before
committing).

## What landed this session (13 September), tip is `ac0a211`

Round 6 (Meta Muse Spark 1.3) was sent and graded: no Critical Tier-1 finding, release
gate holds. Report at
`docs/audit_reports/round6_muse-spark-1.3_2026-09-13/report.md`. Second send attempt
succeeded after the first hit OpenRouter's account-level 18+ gate (Viktor resolved it,
no charge incurred); `finish_reason=stop`, provider Meta, 470,488 prompt / 10,765
completion tokens, cost $0.63386125.

Findings F1 (T2-4 Explicit Configuration, Moderate), F2 (Item 10 Consistent Semantics,
Minor), F3 (Item 13/8, Minor, unreachable live) — Viktor ruled fix all three, narrower
scope than the report's own F1 Location section (left `decision_model.py`'s bands and
the `panel_render.py` NaN gap open, both closed later this session as F4/F5 below).
Three commits, each independently verified before/after combining:

- `447966b` **F1** — six bare literals/locals promoted to named, fingerprinted
  constants (`CONFLUENCE_BOOST_MULT`/`CONFLUENCE_PENALTY_MULT`, `SPIKE_RATIO`,
  `CORRELATION_WINDOW`, `StructureEngine.REGIME_HYSTERESIS_THRESHOLD`), values
  unchanged.
- `3c7e9ae` **F2** — `engine_core.py`'s raw `risk` dict no longer duplicates
  `confidence_score` under a different meaning than `signal_router.py` gives it;
  dropped, survives at `trend.trend_health`.
- `9b34163` **F3** — `signal_router.py`'s `_build_decision_object` no longer defaults
  six absent measurements to `0.0`; all six now go through `_finite_or_nan`. Found,
  not fixed there: `atr_stop`/`targets`/`current_price` reach `panel_render.py`
  through a separate, still-not-NaN-aware `safe_float()` call — closed as F4, below.

Then, Viktor's ruling on "what is next" (fix all four raised items):

- `1f1c935` docs — `docs/PHASE7_NEXT.md` head block rewritten for F1/F2/F3, rule 38
  added (the `git add -A` trap, discovered three more times this same session even
  after being documented — see "Lesson" below).
- `da2e231` — committed `Claude outputs/phase7_handover_2026-09-12.md` as-is: a
  complete, never-committed 12 September session handover note, found stray and
  uncommitted, confirmed by diff not to be a Viktor edit.
- `154e534` **F4** — `core/panel_render.py`'s `atr_stop`/`targets`/`current_price`
  no longer default to `0.0`; same `_finite_or_nan`-style treatment as F3, one layer
  downstream. A real `UnboundLocalError` bug (color variables referenced before
  definition) was found and fixed while building this, caught by running the suite,
  not by review — named honestly in the commit message. code_hash
  `36420c9f...` → `3c4ad5ca...`.
- `ac0a211` **F5** — `models/decision_model.py`'s AGGRESSIVE/CONSERVATIVE
  trend-health/entry-score bands (`75`/`70`/`50`) promoted to named, fingerprinted
  class constants (`AGGRESSIVE_TREND_HEALTH_MIN`, `AGGRESSIVE_ENTRY_SCORE_MIN`,
  `CONSERVATIVE_TREND_HEALTH_MIN`), values unchanged. Investigated and found NOT a
  defect: the same audit finding's "`MIN_ACTION_BIAS` naming split" against
  `RAW_BIAS_THRESHOLD` — both already named, already fingerprinted, deliberately two
  different thresholds; nothing changed there. code_hash `3c4ad5ca...` →
  `13908bba...`. Golden snapshot moved (7 record-completeness fields, zero decision
  fields) — predicted this time from the F1 precedent rather than discovered by
  surprise.

All commits confirmed landed and byte-identical via fresh clone + md5 at the time.
Test counts at tip (Linux sandbox): pytest+pandas_ta 466 passed; pytest without
pandas_ta 338p/117s; `run_tests.py` 395p/0f/32e (32 pre-existing, unrelated to
anything this session touched — all fixture errors on a fixture-free runner).

**Lesson recorded (rule 38 in `docs/PHASE7_NEXT.md`), and worth restating because it
recurred three times even after being written down**: deliver one patch's files at a
time, and always include `git reset <patch> <patch>_commit_message.txt` before `git
commit` in the numbered sequence — a sequence missing that step is what let `git add
-A` sweep in files it shouldn't have, each time.

## Still open — nothing below has been touched this session

1. **The actual next task, per Viktor's ruling to start a new chat for it:**
   `docs/build/build_engineering_notes.py`'s own Document History table has two rows —
   `v1.25` (September 11) and `v1.26` (September 11-12) — that each claim "Entries #94
   through #97" and "#98 through #103" were "added," with full narrative and commit
   hashes for each. **They were not actually added to the document body.** Grepped the
   whole file: no `entry_box(94` through `entry_box(103` exists anywhere. The numbered
   entries jump from `#93` (September 9) straight to the Document History table — ten
   entries' worth of real, already-recorded work (the qwen file move, the doc
   reconciliation, the risk-regime ADX rename, round 5's three Criticals and their
   fixes) exists only as one-line-per-batch history-table prose, never as the actual
   numbered entries those history rows say exist.

   **Viktor's ruling: reconstruct #94 through #103** from the history table's own
   text — the facts and commit hashes are already there, so this is transcription
   into the `entry_box()` format, not new investigation — **then add new entries
   starting at #104** covering everything in "What landed this session" above (Round
   6 send/grade, F1/F2/F3, the docs and handover-file commits, F4, F5), in the same
   terse style as the existing #91–#93 (2–4 sentences per field, not the older
   long-paragraph style). Add a new Document History row (`v1.27`, or `v1.27`+`v1.28`
   if split into two batches) summarizing the additions the same way `v1.24` did.

   Reference material already in the file for the reconstruction: read the `v1.25` and
   `v1.26` rows themselves (near the end of `docs/build/build_engineering_notes.py`,
   just before the `hist_rows` table closes) — they name every commit hash and the
   substance of each entry. Match `entry_box()`'s signature (`number, date_str, title,
   statement_text, rationale_text, tag_text, accent_color`) and the existing tag/color
   conventions: `"FINDINGS — FIXED"`/GREEN, `"PROCESS — RECORDED"`/STEEL, `"MILESTONE —
   RECORDED"`/GREEN, `"DECISION — ADOPTED"`/GREEN, `"EXTERNAL ASSESSMENT — <NAME>"` for
   a named-model audit send. `docs/build/README.md` has the full house style (colors,
   helpers, page setup) and says to always render with `pdftoppm -png -r 65 out.pdf
   page` and look before shipping.

   After the script is right: rebuild with `python build_engineering_notes.py`
   (needs `reportlab`, deliberately not in `requirements.txt` — see
   `docs/build/README.md`), render and check pages, confirm `code_hash` is unmoved
   (both `tests/` and `docs/` are excluded by directory — verify this on both trees
   rather than assuming, per the skill's own standing rule about directory-exclusion
   checks), confirm the golden snapshot is unmoved (nothing in this file is on the
   decision path), then deliver `docs/build/build_engineering_notes.py` and the
   regenerated `docs/Phase7_Engineering_Notes.pdf` together as one patch, following
   the usual verify-then-deliver sequence.

2. `docs/PHASE7_NEXT.md`'s head block still only covers F1/F2/F3 (the tenth-patch
   entry) — it does not yet record the docs commit, the handover-file commit, F4, or
   F5. Needs its own update once the Engineering Notes work above lands, same as every
   prior round's convention (bring the head block current in the same session the
   fixes are delivered in — this session ran out of turn before reaching it).

3. **Not yet ruled**, raised at the very start of this session and never re-raised:
   whether closing F1/F2/F3 needs a round-7 re-audit before the project counts as
   portfolio-ready, or whether non-Critical findings can be accepted/fixed without
   re-auditing.

4. Run the standing end-of-session handover check again once the Engineering Notes
   work and the `PHASE7_NEXT.md` update both land.
