# Next step — read this first

*Updated 30 August, after sequence item 14. Suite: 108 passing, 0 failing, 0 errors.*

Per-item detail lives in the commit messages. This doc carries only what a session needs
before touching anything.

## Order

```
0–10 ✅   adjudications, apparatus, contract
8  ✅  Item 3  Data Integrity        CRITICAL ✔
9  ✅  Item 13 Fail Safely           CRITICAL ✔   (9a, 9b, 9c)
11 ✅  Item 11 No Circular Reasoning CRITICAL ✔
12 ✅  Items 5+6 reproducibility     CRITICAL ✔
13 ✅  Item 14 risk is not conviction            (10c, 14a close with it)
14 ✅  T2-4 explicit configuration
─────────────────────────────────────────────────
15 ←   Item 2's caveat — bfill quarantine        NEXT, last code item
16     Step 8 independent re-audit
```

**ALL FOUR CRITICALS RESOLVED** (Items 3, 6, 11, 13). The release gate's condition is met.
That is not the same as the engine being trustworthy — **Step 8's re-audit at item 16 is
what decides whether any of it held.**

## Item 15 — the groundwork, already done

`bfill` fills a gap from the FUTURE. In a series indexed by time, a missing bar filled
backwards carries information the engine could not have had at that bar. Every site below
was mapped on 30 August; the next session does not need to re-grep.

```
indicators/indicators.py:54    clean_series, method="forward_fill" — ffill().bfill()
indicators/indicators.py:172   the OHLCV cleaning loop, all five columns
indicators/indicators.py:194   EMA repair when pandas_ta leaves NaNs
indicators/indicators.py:374   VWMA, then .fillna(close_prices)
indicators/indicators.py:409   slope, then .fillna(0.0)
indicators/volume_profile.py:62  OHLCV, then .fillna(0)
structure/structure.py:434     OHLCV, then .fillna(0.0)
models/bias_engine.py:74       OHLCV
utils/plotting.py:95           display only — the chart, not a decision
```

Three things to settle before editing:

1. **`clean_series(method="forward_fill")` is misnamed** — it forward-fills AND
   back-fills. Every caller that asked for forward_fill got lookahead it did not request.
2. **Only the leading edge is lookahead in practice.** `ffill` handles every gap after the
   first valid value; `bfill` only ever fires on NaNs BEFORE the first one — the warm-up
   rows. So the question is what a warm-up row should be, not what a gap should be.
3. **plotting.py is display, not decision.** It can keep bfill; say so explicitly rather
   than leaving it looking like an oversight.

Item 2's caveat is the reason this is a separate item — check its wording in the rulings
record before deciding the rule, not after.

## Riders

- **Item 9 leftovers:** `volume_profile` substitutes **zero for a missing high or low**
  (line 62 above — same edit surface as item 15); a failed macro fetch leaves `macro_bias`
  at `"NEUTRAL"`, so a missing timeframe and a directionless market share one word.
- **From item 13:** `risk.trade_quality_current` and `risk.confidence_score` are both
  `trend["trend_health"]` at the engine_core seam; the router overwrites `confidence_score`
  with DecisionModel's real value, so it is not an alias in the output. The engine-side
  dict says otherwise and is worth a look.

## Open decisions

- **The ATR halt** (9a) and **"abnormal volume" not implemented** (item 8) — both Claude's
  calls, both flagged as overrulable.
- **Item 20 amendment** — needs a reviewer who is not Claude. Gemini and Copilot refuse the
  Constitution PDF (content classification). Untested and cheap: try the Roadmap PDF.

## Owed document work

README, Roadmap PDF, Engineering Notes. The state and rulings records are current to
**item 11** and owe entries for **12, 13 and 14**.

## Item 16 — the re-audit

`docs/item16_review_instruction.md` is the brief to hand the reviewer. Give it that, the
`..._RATIFIED_AUDITCOPY.pdf` and the source tree — **not** the commit messages, which
contain the previous auditor's reasoning about the same code.

Use a lab that has seen neither the Constitution nor the source. GLM 5.3 and Kimi K3 have
spent their independence and are the right choice for an informal plan-versus-execution
check, if one is wanted first.

## Working practice

- **Deliver as a `.patch`, never a zip.** `git apply --check <file>.patch` first — a dry
  run that reports problems and changes nothing — then `git apply`. Item 13 went as a zip
  and required dragging folders over the working tree in Explorer, the one step in the
  process with no undo of its own. Stage the patch and message file out of the commit with
  explicit paths (`git add core models tests ...`), then delete them.
- **Restore CRLF before diffing.** The repo is CRLF; Python text-mode writes produce LF and
  every touched file then shows as wholly rewritten.
- **Run the suite plain BEFORE re-baselining.** Re-baselining first bakes whatever the
  engine currently produces into the snapshot and the second run passes against it
  vacuously. The failing diff is the evidence.
- **Predict the diff in advance.** Items 13 and 14 each predicted exactly which fields
  would move, and nothing else did. That is what turns a re-baseline from an admission
  into a proof.
- **Re-baselining:** `set PHASE7_UPDATE_SNAPSHOT=1`, run, `set PHASE7_UPDATE_SNAPSHOT=`
  with **no trailing space**.
- **Windows:** always `git commit -F <file>` for multi-line messages, and keep the message
  file out of the commit.
- `python run_tests.py` discards passing tests' stdout. Paste only the summary line and
  the Failures block.

## The rules, earned

1. Search exhaustively before asserting a thing is not there.
2. A grep for a key name is not a data-flow trace — follow the value to its reader.
3. A defect found once is usually a class.
4. A passing test can be hiding the finding.
5. An argument that a difference would not matter is not evidence the difference exists.
6. A declaration permitting the one illegal shape is worse than none.
7. Inject failures at a point confirmed to be on the path; after deleting a block, scan the
   function for names it defined.
8. **A record of a run must not contain machine-specific paths.** What the data WAS is
   fingerprinted by `last_candle` and `row_count`; where it sat is not part of the identity.
9. **A guard that iterates a list is silent when the list empties.** Both contract tests
   watching `SCHEDULED_FOR_REMOVAL` and `CANONICAL_ALIASES` would have kept passing after
   item 13 emptied them. Empty is now an explicit early return.
10. **Count what you claim.** Both the item 13 and item 14 commit messages said "ten tests"
    where there were nine, and the suite total caught it both times — the second after the
    rule had already been written. A number stated from memory in a document that will be
    audited is a finding waiting to happen. Run the count.
11. **A list of names is a claim about the code, and it decays.** `FINGERPRINTED_CONFIG`
    named seven settings nothing read, in the file item 12 added to stop the engine
    asserting untrue things. Any declaration naming code elsewhere needs a test that
    re-checks the claim against a live run.
