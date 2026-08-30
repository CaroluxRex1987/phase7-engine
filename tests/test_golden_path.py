"""
Golden-path regression test.

Runs the engine end to end against pinned data and compares the decision object
to a stored snapshot. Any change that alters what the engine decides fails this
test and prints the exact fields that moved.

This is the test that makes the remaining fixes safe to attempt. Without it, a
change to bias weighting, the confidence formula or the risk model can silently
alter every decision the engine makes and nothing notices.

Constitution: Tier 3, item 4 (regression tests) and item 5 (fixed evaluation
datasets).

    Re-baseline:  set PHASE7_UPDATE_SNAPSHOT=1
                  python run_tests.py golden
                  (writes the baseline; commit it, and say why in the message)
    Normally:     python run_tests.py golden

Revision history for this file, because it matters:

    v1  Written blind — pandas_ta could not be installed in the authoring
        environment, so it had never run. Marked unverified.
    v2  First real run, 2026-08-28, on Viktor's machine. The test was wrong: it
        called Phase7Engine.run() directly, bypassing SignalRouter and therefore
        DecisionModel. Fixed to route the way main.py does, and to give BTC a
        distinct price series instead of correlating the asset with itself.
    v3  Sequence item 7, 2026-08-30. Three changes, below.


V3, AND WHY EACH PART OF IT
===========================

1. IT NO LONGER MONKEYPATCHES THE CLASS

   v2 did `DataFetcher.get_tf = pinned` — replacing a method on the shared class
   for the duration of the test. That is the same disease sequence item 6 spent
   a commit removing: reaching into something you do not own and changing it for
   everyone. It was guarded by try/finally, so it was contained, but it was also
   the last instance of the pattern in the suite.

   More to the point, it tested the wrong thing. The engine's real data path is
   DataFetcher.set_pinned_source() -> get_tf() -> _load_pinned(), built at
   sequence item 3. A test that replaces get_tf entirely never exercises any of
   it — so the baseline was pinned against a code path production does not use.

   v3 writes three CSVs to a temporary directory and points the real pinned
   source at it. Everything below that is the production path.

2. IT CONTROLS THE C3 STATE FILE

   engine_core persists {supertrend_direction, detailed_bias} to
   Logs/phase7_state_{symbol}_{timeframe}.json after every run, and the next run
   compares against it to produce two of the Exit Watch flags. exit_watch is IN
   the decision object, so the snapshot was a function of run history as well as
   of input.

   In practice it had been stable, for a reason that is luck rather than design:
   both "no state file" and "state file agrees with this run" produce no flags.
   Only a disagreement produces one, and on fixed data nothing disagreed.

   That luck is exactly the shape that breaks on a fresh clone, in CI, or the
   first time someone runs the engine on TESTUSDT by hand. It was visible in the
   29 August smoke output as

       Bias state changed from NEUTRAL to BULLISH CONFIRMED since the last run

   appearing in one run of the suite and not the next.

   v3 deletes the state file before every run, so exit_watch is a function of
   the input alone. GLM's own note on this item asked for exactly this.

3. THE UNREACHABLE-FETCH GUARD PATCHES THE INSTANCE

   From the plan, verbatim: "the data_fetcher singleton binds base_url at import
   — patch the instance, not just config." engine_core imports the module-scope
   singleton, so setting config does nothing to the object doing the fetching.

   Belt and braces: the pinned source already refuses to fall back to the live
   API on a missing series. This makes an unpinned fetch fail at the socket
   rather than at the market.


WHAT THIS BASELINE MUST NOT DO
------------------------------
Two tests in this file are EXPECTED TO FAIL. They document the hardcoded "AERO"
string and the doubled "relationship relationship", both scheduled for sequence
item 12. The snapshot records the engine's current output, defects included —
that is what a baseline is — but the two named defects have their own failing
assertions so that "the snapshot matches" can never be mistaken for "the output
is correct".

A baseline captured while something is quietly broken pins the broken behaviour
as the reference. That happened for real on 30 August: the chart renderer's NaN
repair had been raising and being swallowed for as long as anyone can tell, and
a baseline taken the day before would now be the standard.
"""

import json
import os
import shutil
import tempfile

from conftest import fixture, REPO_ROOT

SNAPSHOT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "fixtures", "golden_decision.json")

# TESTUSDT, not AEROUSDT, on purpose: it is what makes
# test_explanation_does_not_name_a_hardcoded_symbol meaningful. Running the
# golden path on AERO would let the hardcoded string pass unnoticed.
SYMBOL = "TESTUSDT"
TIMEFRAME = "4h"
MACRO_TIMEFRAME = "1d"

# A port nothing listens on. Any fetch that escapes the pinned source dies here
# instead of reaching a live exchange and making the run irreproducible.
UNREACHABLE = "http://127.0.0.1:1"

# Fields excluded from comparison because they legitimately differ between runs
# on identical input. Anything not listed here is expected to be stable.
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


# ============================================================
# The pinned set
# ============================================================

def _write_pinned_set(directory):
    """
    Derive three series from the one committed fixture and write them where the
    real pinned loader will find them.

    Derived rather than committed so there is a single source of truth: change
    ohlcv_clean_4h.csv and all three move together. The derivations are pure
    functions of it, so the set is byte-identical on every machine.

    TESTUSDT_4h   the fixture verbatim — the series under analysis
    TESTUSDT_1d   a real daily aggregate of it, for the macro-confluence read
    BTCUSDT_4h    a distinct but plausible series, for BTC context
    """
    import pandas as pd

    base = pd.read_csv(fixture("ohlcv_clean_4h.csv"))
    base.to_csv(os.path.join(directory, f"{SYMBOL}_{TIMEFRAME}.csv"), index=False)

    # --- macro: six 4h candles make one day ---
    #
    # v2 returned the SAME 450-row 4h series for the macro timeframe, because
    # its monkeypatch ignored the timeframe argument entirely. So the macro
    # confluence check compared the asset against a 50-period EMA of itself on
    # the wrong timeframe and called the answer a daily trend.
    groups = base.index // 6
    daily = base.groupby(groups).agg(
        timestamp=("timestamp", "first"),
        open=("open", "first"),
        high=("high", "max"),
        low=("low", "min"),
        close=("close", "last"),
        volume=("volume", "sum"),
    ).reset_index(drop=True)
    daily.to_csv(os.path.join(directory, f"{SYMBOL}_{MACRO_TIMEFRAME}.csv"), index=False)

    # --- BTC: same shape, different path ---
    #
    # Reversing the row order gives a genuinely different price path while
    # keeping every candle internally consistent (high >= low still holds,
    # because whole rows move together). Returning the same frame for every
    # symbol would correlate the asset with itself and report beta 1.00x and
    # correlation +1.00, which says nothing about the engine.
    btc = base.copy()
    for col in ("open", "high", "low", "close"):
        btc[col] = btc[col].to_numpy()[::-1] * 137_000.0
    btc["volume"] = btc["volume"].to_numpy()[::-1] * 3.0
    btc.to_csv(os.path.join(directory, f"BTCUSDT_{TIMEFRAME}.csv"), index=False)


# ============================================================
# The C3 state file
# ============================================================

def _state_path(symbol=SYMBOL, timeframe=TIMEFRAME):
    from core import config
    log_dir = config.LOG_DIR
    return os.path.join(REPO_ROOT, log_dir,
                        f"phase7_state_{symbol}_{timeframe}.json")


def _clear_state():
    """No prior run. Both flip flags are skipped, deterministically."""
    try:
        os.remove(_state_path())
    except FileNotFoundError:
        pass
    except OSError:
        pass


def _seed_state(**values):
    """A known prior run, for the tests that exercise the flip flags."""
    path = _state_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(values, f)


def _run(seed=None):
    """
    One engine run through the production path, on pinned data, with the
    network unreachable and the C3 state under the test's control.

    seed=None deletes the state file (no prior run). A dict seeds it.
    """
    from data.data_fetcher import DataFetcher, data_fetcher
    from models.signal_router import SignalRouter

    if seed is None:
        _clear_state()
    else:
        _seed_state(**seed)

    tmp = tempfile.mkdtemp(prefix="phase7_golden_")
    original_url = data_fetcher.base_url
    try:
        _write_pinned_set(tmp)
        data_fetcher.base_url = UNREACHABLE
        DataFetcher.set_pinned_source(tmp)
        return SignalRouter().route(symbol=SYMBOL, timeframe=TIMEFRAME)
    finally:
        DataFetcher.clear_pinned_source()
        data_fetcher.base_url = original_url
        shutil.rmtree(tmp, ignore_errors=True)


# ============================================================
# The baseline
# ============================================================

def test_decision_object_matches_snapshot():
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return

    raw = _run()
    assert "error" not in raw, (
        f"the engine reported an error on pinned data: {raw.get('error')}\n"
        "A baseline cannot be captured from a failed run."
    )
    decision = _strip(raw)

    if os.environ.get("PHASE7_UPDATE_SNAPSHOT"):
        os.makedirs(os.path.dirname(SNAPSHOT), exist_ok=True)
        with open(SNAPSHOT, "w") as f:
            json.dump(decision, f, indent=2, sort_keys=True, default=str)
        print(f"snapshot written: {SNAPSHOT}")
        return

    assert os.path.exists(SNAPSHOT), (
        "no baseline snapshot exists yet. Create one with:\n"
        "    set PHASE7_UPDATE_SNAPSHOT=1\n"
        "    python run_tests.py golden\n"
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


def test_the_snapshot_covers_every_top_level_field():
    """
    A baseline is only as good as its coverage.

    If a future change drops a whole section from the decision object, the
    comparison above catches it — but only while the snapshot still contains
    that section. Re-baselining after an accidental deletion would bake the
    deletion in and this file would go quiet about it.

    So the expected shape is asserted independently of the stored file.
    """
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return
    if not os.path.exists(SNAPSHOT):
        print("SKIP: no baseline yet")
        return

    with open(SNAPSHOT) as f:
        stored = json.load(f)

    required = {
        "symbol", "timeframe", "macro_bias",
        "bias", "trend", "structure", "entry", "risk",
        "exit", "exit_watch", "btc_context", "explanation",
    }
    missing = sorted(required - set(stored))

    assert not missing, (
        "the stored baseline is missing decision-object sections: "
        + ", ".join(missing) +
        "\nEither the engine stopped producing them and the snapshot was "
        "re-baselined without anyone noticing, or this list is out of date. "
        "Check which before updating either."
    )


def _run_without(filename):
    """A run whose pinned set is missing one file. Used to prove it was read."""
    from data.data_fetcher import DataFetcher, data_fetcher
    from models.signal_router import SignalRouter

    _clear_state()
    tmp = tempfile.mkdtemp(prefix="phase7_golden_")
    original_url = data_fetcher.base_url
    try:
        _write_pinned_set(tmp)
        os.remove(os.path.join(tmp, filename))
        data_fetcher.base_url = UNREACHABLE
        DataFetcher.set_pinned_source(tmp)
        return SignalRouter().route(symbol=SYMBOL, timeframe=TIMEFRAME)
    finally:
        DataFetcher.clear_pinned_source()
        data_fetcher.base_url = original_url
        shutil.rmtree(tmp, ignore_errors=True)


def test_the_macro_series_is_actually_read():
    """
    Proof that v3's rewiring is live, rather than an argument that it is.

    v3 moved this file off a class-level monkeypatch and onto the real pinned
    source, and gave the macro timeframe a genuine daily series instead of the
    4h series v2 handed it by accident. The snapshot did not move. That is a
    legitimate outcome — the fixture is a sustained uptrend, so `close > EMA_50`
    is BULLISH on either timeframe, and everything downstream was already
    identical because the 4h series is the same file.

    It is also exactly what a test that had silently stopped reading its input
    would look like. The two are indistinguishable from the snapshot alone, so
    this asserts the difference directly: remove the macro file and the macro
    read must change.

    WHAT THIS EXPOSES, recorded rather than fixed. A macro fetch that fails does
    not raise and does not mark the run degraded — engine_core validates the
    frame, and on failure leaves macro_bias at its initialised "NEUTRAL". So a
    missing timeframe and a genuinely directionless market produce the same
    word, and the panel prints MACRO TREND: NEUTRAL either way.

    That is the fabricated-fallback pattern: a real value and a failure sharing
    a representation. It belongs to sequence item 9 under the degrade ruling —
    a failed input must be reported as a failure, not silently rendered as a
    neutral reading. Rider recorded there.
    """
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return

    with_macro = _run().get("macro_bias")
    without_macro = _run_without(f"{SYMBOL}_{MACRO_TIMEFRAME}.csv").get("macro_bias")
    _clear_state()

    assert with_macro != without_macro, (
        f"deleting {SYMBOL}_{MACRO_TIMEFRAME}.csv from the pinned set did not "
        f"change macro_bias (both {with_macro!r}).\n"
        "The macro timeframe is therefore not being read from the pinned "
        "source, and the golden baseline is pinned against a data path the "
        "engine does not use."
    )
    assert without_macro == "NEUTRAL", (
        f"a missing macro series produced macro_bias={without_macro!r}, "
        f"expected 'NEUTRAL'.\nIf engine_core has learned to report this "
        f"failure honestly, that is sequence item 9 landing and this "
        f"expectation should be updated to match."
    )


def test_engine_is_deterministic_on_identical_input():
    """
    Constitution Tier 1, item 4 (Determinism).

    Two runs on the same pinned data, in the same process.

    This is stronger than it was in v2. The caches it was written to catch are
    gone as of sequence item 6, but the C3 state file is a second channel for
    run history to leak into output, and v2 did not control it — the first run
    wrote state that the second read. It passed because both runs agreed, which
    is the answer you get when the leak is real but benign.
    """
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return

    first = _strip(_run())
    second = _strip(_run())

    if first != second:
        diffs = [k for k in set(first) | set(second) if first.get(k) != second.get(k)]
        raise AssertionError(
            "two runs on identical input produced different results.\n"
            f"fields that differ: {', '.join(sorted(diffs))}"
        )


# ============================================================
# C3 — the cross-run comparison flags
# ============================================================

def test_a_bias_flip_against_prior_state_is_reported():
    """
    The first test of the C3 feature itself.

    Two of the eight Exit Watch flags are comparisons against the previous run,
    read from a state file. Nothing tested that they fire — the golden path
    only ever saw the no-prior-state case, where they are correctly silent.
    Silence is also what a broken comparison produces.
    """
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return

    actual_bias = _run().get("bias", {}).get("detailed", "")
    assert actual_bias, "the run produced no detailed bias to compare against"

    # A prior state that cannot match whatever the run produces.
    prior = "BEARISH CONFIRMED" if "BULL" in actual_bias.upper() else "BULLISH CONFIRMED"
    flags = " ".join(_run(seed={"detailed_bias": prior}).get("exit_watch", []))

    assert prior in flags and "Bias state changed" in flags, (
        f"seeded a prior bias of {prior!r} and ran to {actual_bias!r}, but no "
        f"bias-flip flag was raised.\nExit Watch said: {flags or '(nothing)'}\n"
        "Either the state file is not being read, or the comparison is broken. "
        "Both fail silently in normal use, because 'no flag' is also what "
        "agreement looks like."
    )
    _clear_state()


def test_a_supertrend_flip_against_prior_state_is_reported():
    """
    The other half. SuperTrend direction is ±1, so seeding both signs must
    produce exactly one flag: the run's own direction matches one and opposes
    the other.

    Asserting EXACTLY one is what makes this a test. "At least one" would pass
    if the flag fired unconditionally, which is the opposite defect and just as
    wrong.
    """
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return

    fired = []
    for direction in (1.0, -1.0):
        flags = " ".join(_run(seed={"supertrend_direction": direction}).get("exit_watch", []))
        if "SuperTrend flipped" in flags:
            fired.append(direction)
    _clear_state()

    assert len(fired) == 1, (
        f"seeded both SuperTrend directions; the flip flag fired for {fired} "
        f"— expected exactly one.\n"
        "Zero means the comparison never runs. Two means it fires regardless "
        "of the prior value, which would put a flag on the panel on every run."
    )


# ============================================================
# Known defects, scheduled for sequence item 12
# ============================================================

def test_explanation_does_not_name_a_hardcoded_symbol():
    """
    Constitution Tier 4, item 2 (generalization over historical fit) — rated
    Compliant by the audit on the grounds that "the symbol is a parameter" and
    the scan report covers seven assets.

    That holds for the arithmetic. It does not hold for the prose.

    models/decision_model.py hardcodes "AERO" into user-facing reasoning text at
    lines 411, 413 and 419:

        f"...agreeing with AERO's own bias"
        f"...AERO and BTC have a {correlation_label.lower()} relationship..."

    So running the engine on SOLUSDT produces an explanation that talks about
    AERO. Running it on BTCUSDT produces one claiming to compare AERO against
    BTC while actually comparing BTC to itself.

    core/panel_render.py:83 has the same shape — decision.get("symbol",
    "AEROUSDT") — so a decision object without a symbol renders as AERO rather
    than as an error.

    Found 2026-08-28 by running the engine on TESTUSDT and reading the panel.
    Missed by all four audit runs, because none of them ran it.

    EXPECTED TO FAIL until sequence item 12.
    """
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return

    decision = _run()
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

    Cosmetic, but it appears in output the trader reads, and it is one line to
    fix.

    EXPECTED TO FAIL until sequence item 12.
    """
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return

    decision = _run()
    btc = decision.get("btc_context", {}) or {}
    text = str(btc).lower()

    assert "relationship relationship" not in text, (
        "the BTC reasoning contains a doubled word: 'relationship relationship'.\n"
        "models/decision_model.py:419 appends ' relationship' to a label that "
        "already ends in it."
    )
