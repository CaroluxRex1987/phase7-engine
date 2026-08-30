# Next step — read this first

*Updated 30 August, after sequence item 15. Suite: 119 passing, 0 failing, 0 errors.
No re-baseline was needed. **All sixteen items' code work is complete.***

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
15 ✅  Item 2  No Look-Ahead Bias
─────────────────────────────────────────────────
16 ←   Step 8 independent re-audit               ALL THAT REMAINS
```

**ALL FOUR CRITICALS RESOLVED** (Items 3, 6, 11, 13). The release gate's condition is met.
That is not the same as the engine being trustworthy — **item 16 is what decides whether
any of it held.**

## Item 16 — how to run it

`docs/item16_review_instruction.md` is the brief. Hand the reviewer:

1. that document,
2. `..._RATIFIED_AUDITCOPY.pdf` — never the live Constitution, which now names which
   findings came back Critical,
3. the source tree.

**Not the commit messages.** They contain the previous auditor's reasoning about the same
code, and a reviewer who reads them first is reviewing that audit rather than this engine.
The brief has an optional Part 7 for exactly that comparison, after Parts 1–6 are saved.

Reviewer chosen: **GPT-5.6 Luna Pro**. GLM 5.3 and Kimi K3 have spent their independence.

The brief tells the reviewer that tests written by the author of a fix are not independent
evidence, and asks it specifically to hunt for tests that pass while proving nothing. That
check is aimed at this project's own test suite and is the one most likely to return
something.

## What item 15 found, beyond what was expected

The backfills were **not a live leak** and the record says so: the engine makes one
decision, at the last bar of a 450-row frame, and `bfill` only ever fires on the leading
edge. Latent until a backtest walks the decision timestamp backwards.

The live defect was underneath. `clean_series` ended with `fillna(median or 0.0)`, so an
indicator returning entirely NaN left it as a column of **zeros** — and every caller's
`isna().all()` guard ran *after* that and could never fire. A failed ATR became ATR=0: a
stop distance of zero, three targets on the entry price, no failure reported, no
degradation. Item 9a wrote those guards and tested them by making pandas_ta **raise**,
never by making it return nothing usable.

Also closed: VWMA's `.fillna(close_prices)` on the success path (the same substitution 9a
removed from the except branch), volume_profile's `.fillna(0)` on low/high (item 9's
recorded leftover), the EMA slopes' `.fillna(0.0)`, and structure.py's `.fillna(0.0)`
across OHLCV. An all-NaN guard was added to ADX, which never had one.

`utils/plotting.py` still backfills, deliberately — it draws a picture and feeds no
decision. It is the single entry in `BACKFILL_EXEMPT` and a test fails if that list ever
names a module that has stopped backfilling.

## Riders still open

- **`macro_bias` conflates two states:** a failed macro fetch leaves it at `"NEUTRAL"`, so
  a missing timeframe and a directionless market share one word.
- **`entry_model.py:112`** reads `safe_float(df["VWMA"].iloc[-1], close)` — a default of
  `close`, which is the same "perfect 20 of 20 entry points" substitution item 15 removed
  from indicators.py. Unreachable on validated data (VWMA is never NaN at the last bar of
  a full frame) but it is the same shape and should be looked at.
- **`risk.trade_quality_current` and `risk.confidence_score`** are both
  `trend["trend_health"]` at the engine_core seam; the router overwrites `confidence_score`
  with DecisionModel's real value, so it is not an alias in the output. The engine-side
  dict says otherwise.
- **Item 2's compliance is scoped.** It was verified against a single-decision engine.
  When backtesting is built, Item 2 must be re-checked against the harness, not against
  this. The Constitution says so itself.

## Open decisions

- **The ATR halt** (9a) and **"abnormal volume" not implemented** (item 8) — both Claude's
  calls, both flagged as overrulable.
- **Item 20 amendment** — needs a reviewer who is not Claude. Gemini and Copilot refuse the
  Constitution PDF (content classification). Untested and cheap: try the Roadmap PDF.
  Item 16's reviewer could also serve.

## Owed document work

README, Roadmap PDF, Engineering Notes. The state and rulings records are current to
**item 11** and owe entries for **12, 13, 14 and 15**. Do this after item 16's report is
in, so the records close the loop rather than being rewritten twice.

## Working practice

- **Deliver as a `.patch`, never a zip.** `git apply --check <file>.patch` first — a dry
  run that reports problems and changes nothing — then `git apply`. Item 13 went as a zip
  and required dragging folders over the working tree in Explorer, the one step in the
  process with no undo of its own. Write the patch and the message file straight into
  `D:\phase7_engine` over the device bridge, stage them out of the commit with explicit
  paths (`git add indicators structure ...`), then delete them.
- **Restore CRLF before diffing.** The repo is CRLF; Python text-mode writes produce LF and
  every touched file then shows as wholly rewritten.
- **Run the suite plain BEFORE re-baselining.** Re-baselining first bakes whatever the
  engine currently produces into the snapshot and the second run passes against it
  vacuously. The failing diff is the evidence.
- **Predict the diff in advance.** Items 13, 14 and 15 each predicted exactly what would
  move — nine fields, one field, and nothing at all — and each was right. That is what
  turns a re-baseline from an admission into a proof.
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
9. **A guard that iterates a list is silent when the list empties.** Empty must be an
   explicit early return, or the test stops checking without saying so.
10. **Count what you claim.** Both the item 13 and item 14 commit messages said "ten tests"
    where there were nine — the second after the rule had been written. Run the count.
11. **A list of names is a claim about the code, and it decays.** `FINGERPRINTED_CONFIG`
    named seven settings nothing read, inside the file item 12 added to stop the engine
    asserting untrue things.
12. **Fix the helper, not just the branch.** Item 9a removed fabricated constants from
    every `except` block and left `clean_series`, which the success path ran through, still
    turning an all-NaN indicator into zeros — silencing the very guards 9a had just
    written. A defect removed from the loud path is not removed.
13. **Injecting one kind of failure tests one kind of failure.** 9a's tests made pandas_ta
    RAISE. The path where it returns successfully with nothing usable went unexercised for
    six days. Ask what *else* the dependency can do wrong.
14. **Grade a finding at its real severity, including downwards.** The backfills were
    latent, not live, and saying so cost nothing and made the rest of the report credible.
