# Phase-7 Engine

A structural market-analysis engine for a single crypto asset, built as a personal
project, together with the engineering constitution written to govern it.

This is the third build. The first two broke — the second on backtesting, which took
the live engine down with it. Before starting the third, I wrote a formal 44-rule
engineering specification and had independent AI models review it adversarially rather
than agree with it. That document is in [`docs/`](docs/) and is the main reason this
repository is public.

**All of the work in this repository — three builds and the constitution — was done
by one person, with heavy AI assistance.**

---

## Status: honest version

| | |
|---|---|
| Constitution | Ratified 26 August 2026. Rules frozen at 21 / 7 / 10 / 6 = 44. Scope freeze lifted 27 August; no amendments adopted since. |
| Independent audit | **The original four-run audit, plus five further independent rounds since** (2, 5, 5, 12 and 13 September). Every Critical Tier 1 finding any of them raised has a landed, independently re-audited fix. Full record in [`docs/audit_reports/`](docs/audit_reports/). |
| Engine code | **All Criticals resolved.** The original four, plus three more a later round found — see below. All sixteen remediation-sequence items complete. |
| Tests | 466 pass with `pandas_ta` installed (338 pass, 117 skip without it). The dependency-free runner (`run_tests.py`) reports 395 passed, 0 failed, 32 errors — all from tests written with pytest fixtures that runner deliberately doesn't support, not defects; see its own docstring. |
| Release gate | **Open.** Declared 15 September 2026, tagged `portfolio-v1` in this repository — see below. |
| Backtesting | Not yet rebuilt. The Constitution's own separate condition for starting it — Items 2, 3, 6 and 18 all Compliant — has not been formally re-checked since the release gate opened, though nothing currently on record contradicts it. |
| Live trading | Read-only market access only. The engine cannot place orders — enforced by five guards, each verified by injecting its violation. |

**A release gate is in force, as it always has been:** no output of this engine may be
relied on for a real trading decision while any Critical Tier 1 finding stands
unresolved. As of 15 September 2026 that condition is met — every Critical raised
across the original audit and the five independent rounds since has a landed,
independently re-audited fix — and the project
was declared portfolio-ready and tagged `portfolio-v1` at that commit. **The gate is
open.**

That is a statement about process, not about whether this is a good trading tool. It
still hasn't been shown to predict anything (see below), and running it to look at is
fine — acting on it is not.

The Criticals, stated plainly:

- ✅ **Item 3 — Data Integrity.** *Resolved.* Nothing detected missing candles,
  duplicates, impossible prices, bad timestamp ordering or stale data; defects were
  filled in by `ffill`/`bfill` rather than caught. A validator now rejects each defect
  class before it becomes analysis, and names which one it found.
- ✅ **Item 13 — Fail Safely.** *Resolved.* When an indicator failed, the engine
  substituted confident-looking constants with no marker — `RSI = 50` (dead centre),
  `ADX = 25` (the trend/no-trend boundary), `ST_Direction = 1.0` (**bullish**, a
  direction chosen by whoever wrote the fallback). A failed indicator now drops its
  column and reports what the engine lost by it; the run continues in an explicitly
  degraded state, confidence and trade quality are capped, and **a degraded result
  cannot authorize a trade.**
- ✅ **Item 11 — No Circular Reasoning.** *Resolved.* One quantity (`trend_health`) had
  been counted at least four times and presented on the panel as four agreeing signals.
  Every duplicate counting was removed rather than reweighted; `bias_score` is now the
  one place all factors combine, and confidence is a real, independent multi-factor
  score instead of a renamed copy of one input.
- ✅ **Item 6 — Traceability.** *Resolved.* The panel used to print "Trade logged to
  `Logs/phase7_trade_log_<symbol>.csv`" on every run, and no code anywhere wrote that
  file — the engine reported a safety action that never happened.
  `core/decision_log.py` now actually writes that record, and `core/lineage.py` hashes
  each run's validated input and archives the raw candles (pruned at ninety days), so a
  decision can still be checked against its own evidence even once the archive itself
  has expired.

Three of these four came from the original ratification audit. Item 6 was raised from
Major to Critical afterward, on the principle that severity reflects consequence rather
than how much work a fix takes — the repair was one line, and the consequence was the
tool asserting a safety action that never occurred.

**A later, independent round (GPT-6 Astra, 12 September) found three more Critical
Tier 1 defects** after this remediation had already landed: measured volatility never
reaching the stop/target calculation, entry quality scored for the wrong trade
direction, and a stale indicator value presented as current at the decision bar. Each
was fixed as its own independently verified patch, and a further round (Meta Muse Spark
1.3, 13 September) re-audited all of it and found no Critical Tier 1 defect remaining.
That is the audit history behind the gate opening two days later.

**What the remediation has removed so far**, since the list is more interesting than the
count: two caches that never once returned a hit in any production path; four modules
quietly editing DataFrames they did not own; a function whose only use of its first
parameter was to modify it; an exit model whose five verdicts were computed every run and
discarded; a chart renderer that had been silently drawing charts with **no price
candles** whenever it met a NaN; a risk fallback that returned a stop 1% *below* price and
targets above it **regardless of trade direction**, inverted for a short and printed as a
real plan; and an entry-blocking gate that had never once fired because it compared
against labels nothing writes — while four modules acted on its result.

The engine has **not** been shown to predict anything. One component
(BTC-Adjusted Prediction) is correctness-validated — it computes what it was
designed to compute — but empirically unvalidated. Under Tier 1, Item 7 of the
constitution that status has to be stated plainly rather than implied away, so it is
stated here.

Do not use this to trade. It is published as a working record and an engineering
artifact, not as a tool that works.

---

## What's actually interesting here

Probably not the engine. The constitution is the part worth reading, and the audit
record after it.

The constitution is a register of 44 rules across four tiers, written specifically to
constrain AI-assisted development — to stop both the assistant and me from quietly
lowering the bar when a result looked good. A few of the load-bearing ones:

- **Item 18 — Read-Only Market Access.** The engine must never hold credentials with
  trade-execution permissions. Not as a default setting; as the only permitted state.
  This moves the guarantee out of the code and into the exchange, where a fully
  compromised engine still cannot place a trade.
- **Item 8 — Epistemic Honesty.** The engine must distinguish, at all times, between
  what is observed, derived, interpreted, hypothesised, empirically validated, and
  simply unknown. "Unknown" is a legitimate result.
- **Item 17 — Backtesting Must Be Isolated.** Written because backtesting is what broke
  the previous build. The goal is not an unbreakable backtester — it is a blast radius:
  a backtesting failure must never be able to corrupt, destabilize or redefine the live
  engine, and when it fails, it must be possible to isolate what broke and return to a
  known-good state without ambiguity.
- **The audit is not self-certified.** The party that co-drafted the rules and helped
  build the engine cannot be the party that declares it compliant. An independent model
  produces the findings; I answer each of them adversarially, including every finding
  against my own work; disagreements go to me to adjudicate rather than being resolved
  inside either party's head.

There is also an [engineering log](docs/) recording decisions as they were made,
including the ones I got wrong and corrected. Entries are never rewritten — corrections
are appended as new entries that reference the old ones by number. The mistakes are
still in there on purpose.

---

## The audit, and what it found

Four independent runs through OpenRouter, roughly a dollar each, on models with no
prior involvement in the build, made up the original ratification audit:

| Run | Auditor | Scope |
|---|---|---|
| 1 | DeepSeek V4 Pro | Blind — source only, no constitution, no register |
| A | Kimi K3 | The Minimum Viable Audit gate: Items 2, 3, 6, 18 |
| B | Kimi K3 | The remaining 17 Tier 1 invariants |
| C | Kimi K3 | Tiers 2, 3 and 4 — 23 items |

All raw auditor output is published verbatim in
[`docs/Phase7_Audit_Findings_Complete.pdf`](docs/), unedited — including the places
where an auditor was later shown to be wrong, and the places where one caught me being
wrong.

That was not the last audit. Five more independent rounds have run since — 2 September,
two on 5 September, 12 September (GPT-6 Astra), and 13 September (Meta Muse Spark 1.3,
plus its own fix-verification pass on the 14th) — each on a model reporting no prior
exposure to this codebase or its constitution at the time it ran. Every raw report from
every round is in [`docs/audit_reports/`](docs/audit_reports/), unedited, the same as
the original four. A caveat worth stating rather than skipping: several of these models
cannot confirm their own exact checkpoint from the inside, so "no prior exposure" rests
on the provider's session being genuinely fresh, not on the model itself vouching for
its own identity.

**The most useful finding did not come from any of them.** After the original audit
closed I built a test harness and ran the engine. It found three things four audit
passes across three models had all missed — including that, as published, the
repository did not start from a fresh clone. None of those audits ran the code; they
read it. A different *method* beat a different *model*.

That has kept being true. The harness has since caught defects the audits missed and
defects the remediation itself introduced, usually on the first run after a change — a
chart renderer drawing charts with no price candles, a `NameError` that killed every run,
and a test that contradicted the design it was written to check.

The remediation sequence is in [`docs/Phase7_Roadmap.pdf`](docs/), and the reasoning
behind its ordering in [`docs/Phase7_Remediation_Plan.pdf`](docs/).

---

## How this was built

Drafted with Claude (Anthropic) under my direction. The rules, the judgment calls, and
the corrections are mine; most of the prose in the documents is not. I have tried to be
exact about that distinction throughout, because the whole point of the constitution is
that nobody — including me — gets to overstate what they did.

Eleven models have now seen the constitution at various stages: Claude, Copilot, Gemini,
ChatGPT, a second Claude instance in a dedicated reviewer role, Grok, Kimi K3, GPT-5.6
Luna Pro, GLM 5.3, GPT-6 Astra, and Meta Muse Spark 1.3. Seven have graded the engine
source: Claude, Kimi K3, DeepSeek V4 Pro, GPT-5.6 Luna Pro, GLM 5.3, GPT-6 Astra, and
Meta Muse Spark 1.3 — Luna Pro's own independence for that round is a separate, weaker
claim than the others', for reasons the engineering log states plainly rather than
smoothing over.

One caveat I have to state rather than bury: three models touched this codebase during
the build itself via Aider — Claude Sonnet 4, DeepSeek V3 and DeepSeek R1. That means
DeepSeek's lineage had prior exposure to the code it later reviewed blind, so Run 1's
independence is weaker than it first appears. Independence is tracked at the lab level,
not the model-version level, because treating a version bump as a reset would make the
safeguard ceremonial.

---

## Running the tests

```
pip install -r requirements.txt -r requirements-dev.txt
pytest
```

Or with nothing but a Python interpreter:

```
python run_tests.py               # everything
python run_tests.py imports       # one file
python run_tests.py -q            # summary only
python run_tests.py --show-output # don't suppress passing tests' stdout
```

The dependency-free runner exists because the suite has to work on a clean machine
before `pip install` has succeeded — which is exactly the situation the dependency test
is about.

It discards a passing test's output and prints a failing one's, which is not a cosmetic
choice: two defects were found in output that a *passing* test had been burying, and one
of them was a chart renderer failing silently for as long as anyone can tell.

**All tests currently pass.** 466 with `pandas_ta` installed, 338 (plus 117 skipped)
without it. `run_tests.py` reports 32 errors, not failures — from tests written with
pytest fixtures (`monkeypatch`, `tmp_path`, and similar) that this dependency-free
runner deliberately doesn't support, since supporting them would mean re-implementing
the part of pytest it exists to be independent of. Its own docstring explains the
boundary; the count is watched and expected to stay flat except when a new
fixture-using test is added on purpose.

---

## Repository layout

```
phase7_engine/
├── main.py             entry point
├── live_trading.py     read-only live market access (Item 18)
├── test_live.py
├── run_tests.py        dependency-free test runner
├── core/               config, engine_core, panel_render
├── data/               data_fetcher
├── indicators/         indicators, trend_health, volume_profile
├── models/             bias_engine, btc_context, decision_model,
│                       entry_model, exit_model, risk_model, signal_router
├── structure/          structure
├── utils/              plotting
├── tests/              the suite, plus pinned fixtures
├── Logs/               not tracked — see .gitignore
└── docs/               the constitution, audit record, engineering log
    └── build/          and the reportlab scripts that generate them
```

Sixteen files across `core/`, `data/`, `indicators/`, `models/`, `structure/`
and `utils/` — the module count Step 2a of the constitution refers to.
`main.py`, `live_trading.py` and `test_live.py` are entry points, not
modules, and sit outside that count. There is no `backtesting/` in the tree yet:
an earlier version was removed during development, and it was deliberately left
unbuilt until the Constitution's own condition for starting it — Items 2, 3, 6 and 18
all Compliant — is met, so that rebuilding it could not repeat the exact failure that
broke this engine's second build. That condition has not been formally re-checked
since the release gate opened on 15 September 2026, though nothing currently on record
contradicts it — see the Status table above.

`docs/build/` holds the scripts that generate every PDF in `docs/`. They are committed
so the documents are reproducible from source rather than existing only as rendered
output — the constitution's own reproducibility rule applies to its own documents too.

---

## Licence

Two licences apply, to different things:

- **Source code** (all `.py` files) — MIT. See [`LICENSE`](LICENSE).
- **Documentation** (everything in `docs/`) — CC BY 4.0. See [`docs/LICENSE`](docs/LICENSE).

If you reuse the constitution or any of the documentation, reproduce this notice:

> Phase-7 Engineering Constitution © 2026 by Viktor Ljungberg
> is licensed under CC BY 4.0.
> To view a copy of this license, visit
> https://creativecommons.org/licenses/by/4.0/

Use it, adapt it, strip out what doesn't apply to you. Attribution is the only condition.
