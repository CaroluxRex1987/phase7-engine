"""
Sequence item 5a — proving the deletions were safe, and keeping them deleted.

Item 16 forbids unconsumed complexity. The audit found the engine computing
indicator columns that nothing read: Bollinger Bands, the ADX directional
indicators, Typical_Price, KAMA and two of the four slope columns. All written
every run, all read nowhere.

Deleting unconsumed code has an unusually strong verification available:
**output-invariance**. If the engine's decision object is identical before and
after, nothing consumed what was removed. That is a proof, not an argument —
and it is why item 5 was sequenced after items 3 and 4, which built the pinned
data path and the smoke run that make it possible.

The invariance proof itself was performed once, at the time of deletion, by
capturing the decision object on pinned data before and after and comparing.
It cannot be re-run now, because the "before" no longer exists. What these
tests do instead is the durable half: assert the columns stay gone, and assert
the ones that survived are still produced.

WHAT WAS NOT DONE HERE. Step 5's item 5 also listed `compute_exit` for
deletion. It was excluded and handled as 5b, so that a refactor could not ride
inside a cleanup on borrowed proof.

CORRECTION, 30 August 2026. This docstring originally justified that exclusion
by saying compute_exit "is called at engine_core.py:889 and its output feeds at
least eight sites across four files — current_price is read in five places and
action in three, including live_trading's simulated order." The line was 529,
and the rest traced names rather than data: signal_router.py:265 builds its own
"exit" dict, so the `action` those sites read is DecisionModel's, not
compute_exit's. Two dicts shared a key name and I conflated them. The decision
to split was still right; the reason given for it was not. See
test_exit_model_removal.py for the corrected trace.
"""

import os
import pytest

from conftest import fixture

PINNED_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "fixtures", "pinned")

# Removed at sequence item 5a. Each was written on every run and read by
# nothing — verified by scanning every module for a read before deletion.
DELETED_COLUMNS = [
    "BB_lower", "BB_middle", "BB_upper",   # Bollinger trio
    "DIP", "DIM",                          # ADX directional indicators
    "Typical_Price",                       # (H+L+C)/3, input to VWAP and CCI
    "KAMA",                                # only consumer was its own slope
    "KAMA_Slope", "VWMA_Slope",            # produced, never read
    # Removed at the redesign's stage 7, 21 November 2026, by Viktor's ruling
    # of 17 November -- produced and read by nothing since stages 4 and 5
    # (the comment above KEPT_COLUMNS says how each lost its reader):
    "EMA20_Slope",
    "VWMA",
]

# Kept and still produced. Most are load-bearing: if a cleanup takes one, the
# engine breaks quietly rather than loudly.
#
# THE REDESIGN'S STAGE 5, 15 November 2026 -- TWO OF THESE ARE NOW PRODUCED
# AND READ BY NOTHING, which is the question the draft's section 2 left for
# the code to answer, and said this file would answer (stage 5's text, kept;
# stage 7 answered it, below):
#
#   EMA20_Slope  trend_health read it twice, for the mean slope and the
#                acceleration. Both went with the score. The ruled direction
#                reads EMA50's slope only (Viktor's ruling of 7 November).
#   VWMA         entry_model scored the close's distance from it until stage 4
#                made entry quality D + H, with no VWMA part.
#
# Each is still computed every run and still recorded in
# lineage.indicators_at_decision_bar, which is where the draft leaves them
# ("the record keeps it in indicators_at_decision_bar while the column is
# produced"). THAT IS AN ITEM 16 QUESTION -- no unconsumed complexity -- and
# it is recorded rather than answered here: removing a column moves the struct
# input hash, run_hash and the nineteen indicators_at_decision_bar leaves the
# plan for this stage says do not move, so it belongs to stage 6's
# reconciliation, with Viktor told that it is open. This list therefore
# asserts what it has always asserted, that each column is still produced;
# the comments say which of them anything reads.
#
# THE REDESIGN'S STAGE 7, 21 November 2026: both are removed, by Viktor's
# ruling of 17 November, and are in DELETED_COLUMNS above. Stage 6 corrected
# what stage 5 said removing them would move: two leaves of
# indicators_at_decision_bar on each golden run and code_hash, and neither
# the struct input hash nor run_hash -- measured by stage 7 (DECISIONS, its
# entry). Every column left here has a reader.
KEPT_COLUMNS = [
    "EMA_20", "EMA_50",
    "EMA50_Slope",    # bias_engine.direction_from_emas: the ruled direction
    "ADX",            # indicators/trend_readings.py, for the confirmation gate
    "RSI", "ATR", "SuperTrend", "ST_Direction",
]


def _engine_available():
    try:
        import pandas_ta  # noqa: F401
        return True
    except Exception:
        return False


def _indicator_frame():
    """Run the indicator pipeline over the pinned base series."""
    from data.data_fetcher import DataFetcher
    from indicators.indicators import add_technical_indicators

    fetcher = DataFetcher()
    fetcher.base_url = "http://127.0.0.1:1"      # nothing should reach the network
    try:
        DataFetcher.set_pinned_source(PINNED_DIR)
        df = fetcher.get_tf("AEROUSDT", "4h", limit=300)
        assert df.attrs.get("fetch_error") is None, df.attrs.get("fetch_error")
        # SEQUENCE ITEM 9a: add_technical_indicators now returns
        # (frame, failures). Failures are asserted on separately in
        # test_degraded_state.py; this file is about columns.
        frame, _failures = add_technical_indicators(df)
        return frame
    finally:
        DataFetcher.clear_pinned_source()


def test_deleted_columns_stay_deleted():
    """
    The regression guard for item 5a.

    Without this, someone restoring "the Bollinger Bands we used to have"
    reintroduces three columns nothing reads, and Item 16 quietly goes
    Non-compliant again with nothing to notice it.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    df = _indicator_frame()
    resurrected = [c for c in DELETED_COLUMNS if c in df.columns]

    assert not resurrected, (
        "columns removed at sequence item 5a have come back: "
        + ", ".join(resurrected) +
        "\nThey were deleted because nothing read them. If something reads "
        "one now, that is a real change and belongs in its own commit with "
        "its own justification — not restored as a side effect."
    )


def test_consumed_columns_are_still_produced():
    """
    The other half, and the more important one.

    A deletion pass that removes something load-bearing does not necessarily
    crash: trend_health guarded its slope reads with `if "EMA20_Slope" in
    df.columns else 0.0`, so removing that column would have silently zeroed
    the slope contribution to trend health rather than raising (stage 7: the
    score and that guard went at stage 5, and EMA20_Slope at stage 7). The
    engine would keep producing confident-looking numbers computed from less
    than it claims.

    That is exactly the failure class this project keeps finding, so it gets a
    test rather than a comment.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    df = _indicator_frame()
    missing = [c for c in KEPT_COLUMNS if c not in df.columns]

    assert not missing, (
        "indicator columns the engine actually consumes are missing: "
        + ", ".join(missing) +
        "\nA reader that guards its read with a default degrades silently "
        "instead of raising, which is why this is a test and not a comment."
    )


def test_slope_columns_are_not_all_zero():
    """
    Presence is not production.

    `EMA50_Slope` surviving as a column of zeros would pass the test above and
    still mean the direction is computed from nothing. Pinned data has real
    price movement, so a real slope calculation cannot be flat. (Stage 7:
    this named EMA20_Slope and trend health; both are gone.)
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    df = _indicator_frame()
    for col in ["EMA50_Slope"]:
        assert (df[col] != 0.0).any(), (
            f"{col} is entirely zero on pinned data that has real price "
            f"movement — the slope loop is present but not computing."
        )
