# Phase-7 test harness

Phase A of the roadmap. Written August 28, 2026, before Step 5 formally ran,
on the grounds that every plausible ordering needs it first.

Closes Tier 3 items 3 (automated tests), 4 (regression tests) and 5 (fixed
evaluation datasets) — all three currently Non-compliant.

## Running it

```
pip install -r requirements.txt -r requirements-dev.txt
pytest
```

Or with no dependencies at all beyond Python itself:

```
python run_tests.py            # everything
python run_tests.py imports    # one file
python run_tests.py -q         # summary only
```

The fallback runner exists because the suite has to work on a clean machine
before `pip install` has succeeded — which is exactly the situation the
dependency test is about.

## Current state: see the runner, not this heading

Sequence item 3 added nine tests (`test_pinned_source.py`), all passing — the pinned
data path, the mechanism that lets the engine be run twice on the same input.

Sequence item 4 added eight more: five Item 18 guards (`test_execution_surface.py`)
and three smoke tests (`test_smoke.py`) that run the whole engine on pinned data with
the network unreachable.

**Counts in this file have been wrong twice.** Run `python run_tests.py` and read the
last line rather than trusting a number written here.

**The failures are correct.** They are Non-compliances written as executable
acceptance criteria. Each goes green as its fix lands, and stays green afterwards.

| Test | Status | Why |
|---|---|---|
| `test_every_file_compiles` | pass | no syntax errors today |
| `test_every_module_imports` | pass | green since the clone fix |
| `test_declared_dependencies_cover_actual_imports` | pass | fixed 29 Aug — sequence item 2 |
| `test_main_imports_without_a_logs_directory` | pass | fixed 29 Aug — sequence item 2 |
| `test_main_runs_without_a_logs_directory` | pass | same fix |
| `test_decision_object_matches_snapshot` | pass | live since `pandas_ta` became available |
| `test_engine_is_deterministic_on_identical_input` | pass | two runs on pinned data agree exactly |
| `test_accepts_clean_data` | pass | control — a validator that rejects everything is not a validator |
| the nine `test_pinned_source.py` tests | pass | added by sequence item 3, 29 Aug |
| the five `test_execution_surface.py` guards | pass | Item 18 kept Compliant continuously, not by snapshot |
| the three `test_smoke.py` tests | pass | whole engine on pinned data, network unreachable |
| the eight `test_rejects_*` | **fail** | Item 3, Critical — nothing validates input yet |
| `test_explanation_does_not_name_a_hardcoded_symbol` | **fail** | `AERO` hardcoded in user-facing text |
| `test_correlation_phrase_is_not_doubled` | **fail** | "relationship relationship" |

**Revision history for this file, because the counts matter.** First written claiming
4 pass / 12 fail — a prediction, not an observation, and wrong: the first real run gave
5 / 13. Updated 29 August to 8 / 10 after sequence item 2 landed. Counts in this file
should be observed output, never expected output.

## What the import check is for

The runtime log records nine occasions where a change was accepted and then
found broken by running the engine by hand:

```
2026-08-24 17:06  name 'Optional' is not defined
2026-08-24 17:14  name 'Any' is not defined            (and 17:15, 17:16)
2026-08-25 00:07  unterminated f-string                (volume_profile.py:105)
2026-08-25 00:10  expected 'except' or 'finally' block (volume_profile.py:208)
2026-08-25 00:52  invalid syntax                       (indicators.py:121)
2026-08-25 00:53  unindent does not match outer indentation
2026-08-25 01:13  cannot import name 'config' from 'models'
```

All seven classes were reintroduced deliberately, one at a time, and the
suite caught every one. None of them needed market data, a network, or any
knowledge of trading — which is the argument for running this on every change
rather than at intervals.

## The clean-checkout failure — FIXED 29 August, sequence item 2

*Kept here because the reasoning is the useful part, and because the two tests below
are now the regression guard against it coming back.*

`main.py` built its log handler at module scope:

```python
logging.basicConfig(handlers=[logging.FileHandler('Logs/phase7_engine.log'), ...])   # line 16
```

and creates the directory inside `main()`:

```python
os.makedirs('Logs', exist_ok=True)                                                    # line 41
```

`FileHandler` opens its file immediately. With no `Logs/` directory it raises
`FileNotFoundError` during import — before `main()` runs, so the `try/except`
inside `main()` cannot catch it.

This never appeared on the machine the engine was built on, because `Logs/`
has existed there since the first run. It appeared for anyone cloning the
public repository. **As published, the repository did not start.**

Run 1's blind review found the ordering but described it as soft: "the
logging machinery catches it and prints to stderr, so early log lines
silently miss the file." That is not what happens. The finding was real and
its severity was understated by one full category.

**The fix**, in commit `cc7f8ff`: `os.makedirs('Logs', exist_ok=True)` placed at import
scope — above the model imports, not merely above `basicConfig`. The tighter placement
would have worked today and been fragile tomorrow: `live_trading.py` instantiates its
simulator at module scope and that constructor also touches the filesystem, so
filesystem work can happen anywhere in the import chain.

Both tests above now pass, and they are what stops this returning.

## The pinned dataset

`fixtures/ohlcv_clean_4h.csv` — 450 four-hour candles, generated
deterministically from a fixed seed. No network, no exchange, no vendor, no
expiry. Regenerating it produces the identical file forever.

Synthetic rather than real market data on purpose: a regression test needs
input that cannot change underneath it, and any real snapshot eventually
raises the question of whether it is still representative. This one only ever
has to be *stable*.

The eight corrupted variants are built from it in memory, one defect each, so
a failure names a single cause.

## The golden path was wrong on its first run

Worth recording rather than quietly fixing.

`test_golden_path.py` was written blind — `pandas_ta` could not be installed
in the authoring environment, so it had never executed. It was shipped marked
unverified, with a note saying that if it failed, the test was probably wrong
before the engine was.

It failed. The test was wrong.

It called `Phase7Engine.run()` directly, which is not how the engine is used.
`main.py` goes through `SignalRouter.route()`, and the router is what invokes
`DecisionModel`. Bypassing it meant the entire decision layer never ran: the
panel printed `DECISION: HOLD` — which is `exit_model`'s value, not
`DecisionModel`'s — along with `No explanation available` and
`BTC-ADJUSTED CONFIDENCE: 0.00`. None of that is engine behaviour. It was the
test asking the wrong question.

It also returned the same dataframe for every symbol, so the engine correlated
the asset with itself and reported `+1.00` correlation and `1.00x` beta.

Both fixed: routes through `SignalRouter`, and BTC gets a distinct series.

Everything else in this directory was run before delivery, and the failures
listed above are observed rather than predicted.

## First real run also confirmed three findings live

From the panel the engine printed on the pinned dataset:

```
TREND      : BULLISH / STRONG (Score: 95.35)
MOMENTUM   : STRONG (95.35)
    |-- Current Market    : 95.35/100
VALIDATION : STRONG (Score: 85.35)
```

Item 11. One quantity in three places, and validation is that same number
plus 5 for bullish macro, minus 15 for volume divergence — 85.35 exactly.

```
ENTRY ZONE    : $0.7756 - $0.7602
Trade logged to Logs/phase7_trade_log_testusdt.csv
AI Risk chart saved to None
```

Entry zone inverted; a CSV announced that nothing writes; and the chart path
printing `None` because the key exists with a null value, so `.get()`'s
default never applies. All three were audit findings. All three are now
visible in one run.
