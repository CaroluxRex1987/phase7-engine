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
| Constitution | Ratified 26 August 2026. Rules frozen at 21 / 7 / 10 / 6 = 44. Scope freeze lifted 27 August. |
| Independent audit | **Complete.** Four runs, all 44 rules graded: 21 Compliant, 17 Non-compliant, 6 Unknown. Three findings rated Critical. |
| Engine code | **Non-compliant on 17 rules, three of them Critical.** Remediation has started: 2 of 16 sequence items done. |
| Tests | 18 tests. **8 pass, 10 fail.** The failures are the Non-compliances written as executable acceptance criteria. |
| Backtesting | Not rebuilt. Blocked by the release gate until Items 2, 3, 6 and 18 are Compliant. |
| Live trading | Read-only market access only. The engine cannot place orders. |

**A release gate is now in force.** No output of this engine may be relied on for a
real trading decision while any Critical Tier 1 finding stands unresolved. Running it
to look at is fine. Acting on it is not.

The three Criticals, stated plainly:

- **Item 3 — Data Integrity.** Nothing detects missing candles, duplicates, impossible
  prices, bad timestamp ordering, stale data or abnormal volume. Defects are silently
  filled in by `ffill`/`bfill` rather than caught.
- **Item 11 — No Circular Reasoning.** One quantity (`trend_health`) is counted at
  least four times and presented on the panel as four agreeing signals.
- **Item 13 — Fail Safely.** When an indicator fails, the engine substitutes
  confident-looking constants with no marker. A failed SuperTrend silently adds a
  permanent bullish vote to the bias score.

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
  the previous build. The goal is not an unbreakable backtester — it is a blast radius.
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
prior involvement in the build:

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

**The most useful finding did not come from any of them.** After the audit closed I
built a test harness and ran the engine. It found three things four audit passes across
three models had all missed — including that, as published, the repository did not
start from a fresh clone. None of the audits ran the code; they read it. A different
*method* beat a different *model*.

The remediation sequence is in [`docs/Phase7_Roadmap.pdf`](docs/), and the reasoning
behind its ordering in [`docs/Phase7_Remediation_Plan.pdf`](docs/).

---

## How this was built

Drafted with Claude (Anthropic) under my direction. The rules, the judgment calls, and
the corrections are mine; most of the prose in the documents is not. I have tried to be
exact about that distinction throughout, because the whole point of the constitution is
that nobody — including me — gets to overstate what they did.

Nine models have now seen the constitution at various stages: Claude, Copilot, Gemini,
ChatGPT, a second Claude instance in a dedicated reviewer role, Grok, Kimi K3, GPT-5.6
Luna Pro, and GLM 5.3. Four have graded the engine source: Claude, Kimi K3, DeepSeek V4
Pro and GLM 5.3.

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
python run_tests.py            # everything
python run_tests.py imports    # one file
python run_tests.py -q         # summary only
```

The dependency-free runner exists because the suite has to work on a clean machine
before `pip install` has succeeded — which is exactly the situation the dependency test
is about.

**Ten failures are expected.** They are acceptance criteria for fixes that have not
landed yet, and each one names a file and a line.

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
modules, and sit outside that count. There is no `backtesting/` in the tree:
an earlier version was removed during development, and per the Status table
above it is deliberately not being rebuilt until the release gate opens.

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
