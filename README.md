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
| Constitution | Ratified 26 August 2026. Rules frozen at 21 / 7 / 10 / 6 = 44. |
| Engine code | **Unverified.** No independent audit has been run against it yet. |
| Backtesting | Not rebuilt. Deliberately blocked until the audit has run. |
| Live trading | Read-only market access only. The engine cannot place orders. |

The engine has **not** been shown to predict anything. One component
(BTC-Adjusted AERO Prediction) is correctness-validated — it computes what it was
designed to compute — but empirically unvalidated. Under Tier 1, Item 7 of the
constitution that status has to be stated plainly rather than implied away, so it is
stated here.

Do not use this to trade. It is published as a working record and an engineering
artifact, not as a tool that works.

---

## What's actually interesting here

Probably not the engine. The constitution is the part worth reading.

It is a register of 44 rules across four tiers, written specifically to constrain
AI-assisted development — to stop both the assistant and me from quietly lowering the
bar when a result looked good. A few of the load-bearing ones:

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

## How this was built

Drafted with Claude (Anthropic) under my direction. The rules, the judgment calls, and
the corrections are mine; most of the prose in the documents is not. I have tried to be
exact about that distinction throughout, because the whole point of the constitution is
that nobody — including me — gets to overstate what they did.

Four models were used across the project: Claude, ChatGPT, Copilot and Gemini reviewed
the constitution at different stages. The independent audit of the *code* is intended
for Grok, from xAI — a different model family from the assistant that helped write it,
which is the point. It has not happened yet.

---

## Repository layout

```
phase7_engine/
├── main.py             entry point
├── live_trading.py     read-only live market access (Item 18)
├── test_live.py
├── core/               config, engine_core, panel_render
├── data/               data_fetcher
├── indicators/         indicators, trend_health, volume_profile
├── models/             bias_engine, btc_context, decision_model,
│                       entry_model, exit_model, risk_model, signal_router
├── structure/          structure
├── utils/              plotting
├── logs/               not tracked — see .gitignore
└── docs/               the constitution, engineering log, and companions
```

Sixteen files across `core/`, `data/`, `indicators/`, `models/`, `structure/`
and `utils/` — the module count Step 2a of the constitution refers to.
`main.py`, `live_trading.py` and `test_live.py` are entry points, not
modules, and sit outside that count. There is no `backtesting/` in the tree:
an earlier version was removed during development, and per the Status table
above it is deliberately not being rebuilt until the audit has run.

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
