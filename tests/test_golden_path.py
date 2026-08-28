"""
Golden-path regression test.

Runs the engine end to end against the pinned dataset and compares the
decision object to a stored snapshot. Any change that alters what the engine
decides will fail this test and print the exact fields that moved.

This is the test that makes the other seventeen fixes safe to attempt. Right
now a change to bias weighting, the confidence formula or the risk model can
silently alter every decision the engine makes, and nothing would notice.

Constitution: Tier 3, item 4 (regression tests) and item 5 (fixed evaluation
datasets), both currently Non-compliant.

    First run:   PHASE7_UPDATE_SNAPSHOT=1 pytest tests/test_golden_path.py
                 (writes the baseline; commit it)
    After that:  pytest tests/test_golden_path.py

Revision history for this file, because it matters:

    v1  Written blind — pandas_ta could not be installed in the authoring
        environment, so it had never run. Marked unverified.
    v2  First real run, 2026-08-28, on Viktor's machine. The test was wrong:
        it called Phase7Engine.run() directly, bypassing SignalRouter and
        therefore DecisionModel. Fixed to route the way main.py does, and to
        give BTC a distinct price series instead of correlating the asset
        with itself.
"""

import json
import os

from conftest import fixture, REPO_ROOT

SNAPSHOT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "fixtures", "golden_decision.json")

# Fields excluded from comparison because they legitimately differ between
# runs on identical input. Anything not listed here is expected to be stable.
VOLATILE = {"chart_path", "timestamp", "generated_at"}


def _engine_available():
    try:
        import pandas_ta  # noqa: F401
        return True
    except Exception:
        return False


def _strip(obj):
    if isinstance(obj, dict):
        return {k: _strip(v) for k, v in obj.items() if k not in VOLATILE}
    if isinstance(obj, (list, tuple)):
        return [_strip(v) for v in obj]
    if isinstance(obj, float):
        return round(obj, 8)
    return obj


def _run_on_pinned_data():
    """
    Drive the engine from the pinned CSV rather than the live API, so the
    result depends only on code, never on the market.

    Goes through SignalRouter.route(), which is the path main.py uses. Calling
    Phase7Engine.run() directly skips DecisionModel entirely — no final_action,
    no confidence, no explanation, no BTC adjustment — and snapshots a decision
    object the engine never actually produces. The first version of this test
    did exactly that; the panel it printed said "DECISION: HOLD" (which is
    exit_model's value, not DecisionModel's), "No explanation available", and
    "BTC-ADJUSTED CONFIDENCE: 0.00".

    BTC gets a deliberately different series. Returning the same frame for
    every symbol makes the asset perfectly correlated with itself and reports
    beta 1.00x and correlation +1.00, which says nothing about the engine.
    """
    import pandas as pd
    from data.data_fetcher import DataFetcher
    from models.signal_router import SignalRouter

    base = DataFetcher().load_csv(fixture("ohlcv_clean_4h.csv"))

    # A distinct but plausible BTC series: same shape, different path.
    btc = base.copy()
    for col in ("open", "high", "low", "close"):
        btc[col] = btc[col].to_numpy()[::-1] * 137_000.0
    btc["volume"] = btc["volume"].to_numpy()[::-1] * 3.0

    original = DataFetcher.get_tf

    def pinned(self, symbol, timeframe, limit=300):
        return (btc if str(symbol).upper().startswith("BTC") else base).copy()

    try:
        DataFetcher.get_tf = pinned
        return SignalRouter().route(symbol="TESTUSDT", timeframe="4h")
    finally:
        DataFetcher.get_tf = original


def test_decision_object_matches_snapshot():
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return

    decision = _strip(_run_on_pinned_data())

    if os.environ.get("PHASE7_UPDATE_SNAPSHOT"):
        os.makedirs(os.path.dirname(SNAPSHOT), exist_ok=True)
        with open(SNAPSHOT, "w") as f:
            json.dump(decision, f, indent=2, sort_keys=True, default=str)
        print(f"snapshot written: {SNAPSHOT}")
        return

    assert os.path.exists(SNAPSHOT), (
        "no baseline snapshot exists yet. Create one with:\n"
        "    PHASE7_UPDATE_SNAPSHOT=1 pytest tests/test_golden_path.py\n"
        "then commit tests/fixtures/golden_decision.json"
    )

    with open(SNAPSHOT) as f:
        expected = json.load(f)

    actual = json.loads(json.dumps(decision, sort_keys=True, default=str))

    if actual != expected:
        diffs = []
        for key in sorted(set(expected) | set(actual)):
            a, b = expected.get(key, "<missing>"), actual.get(key, "<missing>")
            if a != b:
                diffs.append(f"  {key}:\n    was: {a}\n    now: {b}")
        raise AssertionError(
            "the engine's decision changed on identical input:\n"
            + "\n".join(diffs)
            + "\n\nIf the change was intended, re-baseline with "
              "PHASE7_UPDATE_SNAPSHOT=1 and say so in the commit message."
        )


def test_engine_is_deterministic_on_identical_input():
    """
    Constitution Tier 1, item 4 (Determinism).

    Two runs on the same pinned data, in the same process. Any difference
    means state is leaking between runs — which is the objection Claude
    raised against the auditor's Compliant rating for Items 4 and 12, over
    the indicator cache keyed on symbol, timeframe, row count and last close
    but not the bar's high, low or volume.
    """
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return

    first = _strip(_run_on_pinned_data())
    second = _strip(_run_on_pinned_data())

    if first != second:
        diffs = [k for k in set(first) | set(second) if first.get(k) != second.get(k)]
        raise AssertionError(
            "two runs on identical input produced different results.\n"
            f"fields that differ: {', '.join(sorted(diffs))}"
        )


def test_explanation_does_not_name_a_hardcoded_symbol():
    """
    Constitution Tier 4, item 2 (generalization over historical fit) — rated
    Compliant by the audit on the grounds that "the symbol is a parameter"
    and the scan report covers seven assets.

    That holds for the arithmetic. It does not hold for the prose.

    models/decision_model.py hardcodes the string "AERO" into user-facing
    reasoning text at lines 411, 413 and 419:

        f"...agreeing with AERO's own bias"
        f"...AERO and BTC have a {correlation_label.lower()} relationship..."

    So running the engine on SOLUSDT produces an explanation that talks about
    AERO. Running it on BTCUSDT produces one claiming to compare AERO against
    BTC while actually comparing BTC to itself.

    core/panel_render.py:83 has the same shape — `decision.get("symbol",
    "AEROUSDT")` — so a decision object without a symbol renders as AERO
    rather than as an error.

    Found on 2026-08-28 by running the engine on TESTUSDT and reading the
    panel. Missed by all four audit runs, because none of them ran it.
    """
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return

    decision = _run_on_pinned_data()
    reasons = " ".join(decision.get("explanation", {}).get("reasons", []))
    btc = decision.get("btc_context", {}) or {}
    btc_reasons = " ".join(
        (btc.get("btc_adjusted", {}) or {}).get("reasons", [])
        if isinstance(btc.get("btc_adjusted"), dict) else []
    )
    haystack = (reasons + " " + btc_reasons + " " + str(btc)).upper()

    assert "AERO" not in haystack, (
        "the engine was run on TESTUSDT and its explanation names AERO.\n"
        "Symbol names are hardcoded in models/decision_model.py (lines 411, "
        "413, 419) and core/panel_render.py (line 83).\n"
        "Fix: interpolate the symbol under analysis, or say 'this asset'."
    )


def test_correlation_phrase_is_not_doubled():
    """
    btc_context returns labels that already end in the word "relationship" —
    e.g. "WEAK / NO CLEAR RELATIONSHIP" — and decision_model appends
    " relationship" to them, producing:

        "a weak / no clear relationship relationship"

    Cosmetic, but it appears in output the trader reads, and it is one line
    to fix.
    """
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return

    decision = _run_on_pinned_data()
    btc = decision.get("btc_context", {}) or {}
    text = str(btc).lower()

    assert "relationship relationship" not in text, (
        "the BTC reasoning contains a doubled word: 'relationship relationship'.\n"
        "models/decision_model.py:419 appends ' relationship' to a label that "
        "already ends in it."
    )
