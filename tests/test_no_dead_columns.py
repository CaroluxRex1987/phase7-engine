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
deletion. It was excluded: `compute_exit` is called at engine_core.py:889 and
its output feeds at least eight sites across four files — `current_price` is
read in five places and `action` in three, including live_trading's simulated
order. It is not unconsumed code, so removing it is a refactor that changes
behaviour by definition, and it cannot inherit the output-invariance proof that
covers everything in this file. Bundling the two would have let a real
behaviour change hide inside a cleanup that is provably safe. Tracked
separately as 5b.
"""

import os

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
]

# Kept, and load-bearing. If a future cleanup takes one of these, the engine
# breaks quietly rather than loudly — trend_health falls back to 0.0 slopes
# and entry_model scores VWMA distance against a column that is not there.
KEPT_COLUMNS = [
    "EMA_20", "EMA_50",
    "EMA20_Slope",    # trend_health.py reads it in three places
    "EMA50_Slope",    # trend_health.py:1711
    "VWMA",           # entry_model distance scoring
    "ADX",            # trend_health and bias both read it
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
        return add_technical_indicators(df)
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
        print("SKIP: pandas_ta not installed")
        return

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
    crash: trend_health guards its slope reads with `if "EMA20_Slope" in
    df.columns else 0.0`, so removing that column would silently zero the
    slope contribution to trend health rather than raising. The engine would
    keep producing confident-looking numbers computed from less than it
    claims.

    That is exactly the failure class this project keeps finding, so it gets a
    test rather than a comment.
    """
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return

    df = _indicator_frame()
    missing = [c for c in KEPT_COLUMNS if c not in df.columns]

    assert not missing, (
        "indicator columns the engine actually consumes are missing: "
        + ", ".join(missing) +
        "\nNote that trend_health guards its slope reads with a default of "
        "0.0, so a missing slope column degrades the score silently instead "
        "of raising."
    )


def test_slope_columns_are_not_all_zero():
    """
    Presence is not production.

    `EMA20_Slope` surviving as a column of zeros would pass the test above and
    still mean trend health is computed from nothing. Pinned data has real
    price movement, so a real slope calculation cannot be flat.
    """
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return

    df = _indicator_frame()
    for col in ["EMA20_Slope", "EMA50_Slope"]:
        assert (df[col] != 0.0).any(), (
            f"{col} is entirely zero on pinned data that has real price "
            f"movement — the slope loop is present but not computing."
        )
