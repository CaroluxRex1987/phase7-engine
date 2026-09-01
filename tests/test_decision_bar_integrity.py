"""
Finding 3 — Item 13: partially invalid indicator columns can pass without
degradation.

THE FINDING, AND WHY IT SURVIVED FOUR MONTHS OF REMEDIATION

This was one of the independent audit's five Criticals and the only one never
worked on. It is not in PHASE7_NEXT.md's sequence, it has no ruling recorded
against it, and the roadmap's claim that "remediation of the audit's five
Criticals is complete" was wrong from 31 August until 1 September 2026. It was
found by reading the audit report itself rather than the roadmap written from
it.

WHAT THE AUDIT QUOTED

    atr = clean_series(ta.atr(...), method="forward_fill")
    if atr is None or atr.isna().all():
        raise ValueError("pandas_ta returned no usable ATR")

"The guard detects only an entirely NaN series. A series with a valid prefix
and a NaN at the decision bar is accepted."

WHAT MADE IT INVISIBLE

`clean_series(method="forward_fill")` runs `.ffill()`, which fills every gap
after the first valid value — including a gap at the last row. So the guard
could not fire even in principle for the case that matters: by the time it
ran, the missing decision-bar value had already been replaced by the previous
bar's number. `.isna().all()` on a series with 299 good values is False no
matter what happened at row 300.

The engine then read `.iloc[-1]` and got a real number, computed from a real
bar — the wrong bar. No failure recorded, no degradation, no cap on
confidence, a full risk plan printed.

THE CLASS, WHICH IS LARGER THAN THE TWO INSTANCES THE AUDIT NAMED

The audit named ATR and SuperTrend direction. Injecting a trailing NaN into
each indicator in turn, before the fix:

    indicator    failure recorded?    decision row == prior bar
    atr          []                   YES (stale)
    rsi          []                   YES (stale)
    adx          []                   YES (stale)
    supertrend   []                   YES (stale)
    ema          []                   YES (stale)

Every one. It was a property of the guard, not of any indicator, so the guard
is now one function — indicators.unusable_reason — and every caller asks it.
Two indicators had no guard at all to fix: the SuperTrend LEVEL (only its
direction was checked) and both EMAs.

The same trailing fill was also running on the raw OHLCV columns, one layer
further up, turning a truncated final candle into a synthetic bar that
repeated the previous close. data/validation.py rejects NaN OHLCV before the
production path reaches that loop — verified, see
test_a_missing_final_candle_is_not_forward_filled — so that half was defence
in depth rather than a live hole.

AND THE CONSUMERS, WHICH WERE FABRICATING WHAT ITEM 9a REMOVED

Item 9a deleted the invented constants from the producer and left them in the
readers. Two of them awarded the MAXIMUM score for a measurement never taken:

    entry_model.py  rsi = safe_float(df["RSI"].iloc[-1], 50.0)
                    50 is inside the 40-60 band -> 15 of 15, top marks
    entry_model.py  hvn = safe_float(df["HVN"].iloc[-1], close)
                    close makes |close-hvn|/close exactly 0 -> 12 of 12

The second is byte-for-byte the defect item 3 fixed for VWMA, sitting
untouched forty lines below the fix. Rule 18 of PHASE7_NEXT.md's own list,
applied to the item that wrote rule 18.
"""

import os
import numpy as np
import pandas as pd
import pytest

PINNED_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "fixtures", "pinned")
UNREACHABLE = "http://127.0.0.1:1"


def _engine_available():
    try:
        import pandas_ta  # noqa: F401
        return True
    except Exception:
        return False


def _pinned_frame():
    from data.data_fetcher import DataFetcher, data_fetcher
    original = data_fetcher.base_url
    try:
        data_fetcher.base_url = UNREACHABLE
        DataFetcher.set_pinned_source(PINNED_DIR)
        return data_fetcher.get_tf("AEROUSDT", "4h", limit=300)
    finally:
        DataFetcher.clear_pinned_source()
        data_fetcher.base_url = original


def _trailing_nan(real):
    """Wrap a pandas_ta function so its output has no value at the last bar."""
    def wrapped(*a, **k):
        out = real(*a, **k)
        if out is None:
            return out
        out = out.copy()
        if hasattr(out, "columns"):
            out.iloc[-1, :] = np.nan
        else:
            out.iloc[-1] = np.nan
        return out
    return wrapped


# ============================================================
# clean_series: the trailing edge
# ============================================================

def test_clean_series_no_longer_fills_the_decision_bar():
    """
    The mechanism the whole finding rests on.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    from indicators.indicators import clean_series

    s = pd.Series([1.0] * 10 + [np.nan])
    out = clean_series(s, method="forward_fill")

    assert pd.isna(out.iloc[-1]), (
        f"a trailing NaN was filled with {out.iloc[-1]!r}.\n"
        "That value is the previous bar's, standing in for the bar the "
        "decision is made on, and every guard downstream tests isna().all(), "
        "which such a series can never satisfy."
    )


def test_clean_series_still_fills_interior_gaps():
    """
    The control, and the limit of the change.

    An interior gap filled forward is the last real observation carried across
    it, and a real value follows. Nothing follows the trailing edge — that is
    the whole distinction.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    from indicators.indicators import clean_series

    s = pd.Series([1.0, np.nan, np.nan, 4.0, 5.0])
    out = clean_series(s, method="forward_fill")

    assert out.tolist() == [1.0, 1.0, 1.0, 4.0, 5.0], out.tolist()


def test_clean_series_still_leaves_leading_warmup_alone():
    """Sequence item 15's rule, unchanged by this one."""
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    from indicators.indicators import clean_series

    s = pd.Series([np.nan, np.nan, 3.0, 4.0])
    out = clean_series(s, method="forward_fill")

    assert pd.isna(out.iloc[0]) and pd.isna(out.iloc[1]), out.tolist()
    assert out.iloc[2] == 3.0 and out.iloc[3] == 4.0, out.tolist()


# ============================================================
# The shared guard
# ============================================================

def test_unusable_reason_names_each_way_a_series_fails():
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    from indicators.indicators import unusable_reason

    assert unusable_reason(None, "X") is not None
    assert unusable_reason(pd.Series(dtype=float), "X") is not None
    assert unusable_reason(pd.Series([np.nan, np.nan]), "X") is not None

    trailing = unusable_reason(pd.Series([1.0, 2.0, np.nan]), "X")
    assert trailing is not None, (
        "a series with a valid prefix and no value at the decision bar was "
        "reported usable — this is the finding itself"
    )
    assert "decision bar" in trailing, trailing

    assert unusable_reason(pd.Series([1.0, 2.0, 3.0]), "X") is None


def test_unusable_reason_rejects_a_non_finite_decision_bar():
    """Infinity is not a reading either, and isna() does not catch it."""
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    from indicators.indicators import unusable_reason

    assert unusable_reason(pd.Series([1.0, 2.0, np.inf]), "X") is not None


# ============================================================
# The producers
# ============================================================

def test_an_indicator_with_no_fallback_reports_a_missing_decision_bar():
    """
    ADX and SuperTrend have no second computation route, so a missing value at
    the decision bar is a real loss and must be reported as one.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    import indicators.indicators as ind

    base = _pinned_frame()
    for fn_name, column in (("adx", "ADX"), ("supertrend", "ST_Direction")):
        real = getattr(ind.ta, fn_name)
        setattr(ind.ta, fn_name, _trailing_nan(real))
        try:
            out, failures = ind.add_technical_indicators(base.copy())
        finally:
            setattr(ind.ta, fn_name, real)

        assert failures, (
            f"{fn_name} had no value at the decision bar and nothing was "
            f"recorded. Before this fix the column kept the previous bar's "
            f"number and the run reported itself clean."
        )
        assert column not in out.columns, (
            f"{column} survived with no usable value at the decision bar; a "
            f"consumer reading .iloc[-1] would get a stale number"
        )


def test_a_recoverable_indicator_still_recovers_rather_than_degrading():
    """
    The control that keeps this fix honest, and the distinction item 9a rests
    on: a fallback that recomputes the same quantity by another route is not a
    fabrication.

    ATR, RSI and the EMAs each have a real second path. Breaking the pandas_ta
    call must still produce a genuine recomputed value at the decision bar —
    not a stale one, and not a degradation.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    import indicators.indicators as ind

    base = _pinned_frame()
    for fn_name, column in (("atr", "ATR"), ("rsi", "RSI"), ("ema", "EMA_50")):
        real = getattr(ind.ta, fn_name)
        setattr(ind.ta, fn_name, _trailing_nan(real))
        try:
            out, failures = ind.add_technical_indicators(base.copy())
        finally:
            setattr(ind.ta, fn_name, real)

        assert column in out.columns, (
            f"{column} was dropped even though its fallback path can compute "
            f"the same quantity. Failures: {[f.indicator for f in failures]}"
        )
        value = float(out[column].iloc[-1])
        prior = float(out[column].iloc[-2])
        assert np.isfinite(value), f"{column} recovered to a non-finite value"
        assert value != prior, (
            f"{column} at the decision bar equals the previous bar exactly "
            f"({value}); that is the stale-carry-forward this fix removes, not "
            f"a recomputation"
        )


def test_when_every_path_fails_the_indicator_is_reported():
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    import indicators.indicators as ind

    base = _pinned_frame()
    real_adx = ind.ta.adx

    def explode(*a, **k):
        raise RuntimeError("simulated total ADX failure")

    ind.ta.adx = explode
    try:
        out, failures = ind.add_technical_indicators(base.copy())
    finally:
        ind.ta.adx = real_adx

    assert any(f.indicator == "ADX" for f in failures), failures
    assert "ADX" not in out.columns


def test_the_supertrend_level_is_guarded_and_not_only_its_direction():
    """
    Before this fix only ST_Direction was checked, and only for all-NaN. The
    level is written to the frame and drawn on the chart.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    import indicators.indicators as ind
    import inspect

    src = inspect.getsource(ind.add_technical_indicators)
    assert "SuperTrend's level" in src, (
        "the SuperTrend level no longer has its own guard; a level with no "
        "value at the decision bar would be written to the frame again"
    )


def test_a_missing_final_candle_is_not_forward_filled():
    """
    The same trailing fill was running on the raw prices, so a truncated final
    candle became a synthetic bar repeating the previous close.

    Also pins the boundary: validation.py rejects this before the production
    path ever reaches the indicator layer, so the loop below is defence in
    depth. If validation ever stops rejecting it, the second assertion here is
    what still stands between a missing candle and a fabricated one.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    import indicators.indicators as ind
    from data.validation import validate_ohlcv

    base = _pinned_frame()
    truncated = base.copy()
    truncated.loc[truncated.index[-1], ["high", "low", "close"]] = np.nan

    assert validate_ohlcv(truncated) is not None, (
        "validation no longer rejects a frame whose final candle is missing"
    )

    out, _failures = ind.add_technical_indicators(truncated)
    assert pd.isna(out["close"].iloc[-1]), (
        f"the missing final close was filled with {out['close'].iloc[-1]!r}, "
        "which is the previous candle's price presented as this one's"
    )


# ============================================================
# The consumers
# ============================================================

def test_a_missing_rsi_no_longer_scores_full_marks():
    """
    The sharpest instance. 50.0 sits inside the 40-60 "not extended" band, so
    the fallback awarded 15 of 15 — the maximum — for a reading that does not
    exist. indicators.py's own failure text told the operator it scored 0.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    import indicators.indicators as ind
    from models.entry_model import calculate_entry_quality

    frame, _ = ind.add_technical_indicators(_pinned_frame())
    close = float(frame["close"].iloc[-1])
    zone = (close * 0.97, close * 0.99)

    missing = frame.copy()
    missing["RSI"] = np.nan
    result = calculate_entry_quality(missing, zone[0], zone[1], "BULLISH")

    assert result["rsi_pts"] < 15, (
        f"a missing RSI scored {result['rsi_pts']} of 15 — the maximum, for a "
        f"measurement never taken"
    )


def test_a_missing_hvn_no_longer_scores_full_marks():
    """
    `close` as the fallback makes the distance exactly zero, which is the
    tightest band. Identical in shape to the VWMA defect item 3 fixed, and it
    was sitting forty lines below that fix.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    import indicators.indicators as ind
    from models.entry_model import calculate_entry_quality

    frame, _ = ind.add_technical_indicators(_pinned_frame())
    close = float(frame["close"].iloc[-1])
    zone = (close * 0.97, close * 0.99)

    missing = frame.copy()
    missing["HVN"] = np.nan
    result = calculate_entry_quality(missing, zone[0], zone[1], "BULLISH")

    assert result["struct_pts"] < 12, (
        f"a missing HVN scored {result['struct_pts']} of 12 — the maximum, "
        f"awarded for a high-volume node that was never located"
    )


def test_a_missing_atr_is_not_scored_against_a_fabricated_two_percent():
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    import indicators.indicators as ind
    from models.entry_model import calculate_entry_quality

    frame, _ = ind.add_technical_indicators(_pinned_frame())
    close = float(frame["close"].iloc[-1])
    zone = (close * 0.90, close * 0.92)   # far from the zone, so the ratio bites

    missing = frame.copy()
    missing["ATR"] = np.nan
    got = calculate_entry_quality(missing, zone[0], zone[1], "BULLISH")

    fabricated = frame.copy()
    fabricated["ATR"] = close * 0.02      # what the old fallback substituted
    old = calculate_entry_quality(fabricated, zone[0], zone[1], "BULLISH")

    assert got["atr_dist_pts"] != old["atr_dist_pts"], (
        "a missing ATR still scores exactly as though close * 0.02 had been "
        "measured, which is the constant item 9a removed from indicators.py"
    )


# ============================================================
# The risk model
# ============================================================

def test_calculate_stop_targets_rejects_a_non_finite_atr():
    """
    NaN fails every comparison, so `atr_val <= 0` never fired.
    """
    from models.risk_model import RiskModel

    model = RiskModel()
    with pytest.raises(Exception):
        model.calculate_stop_targets("BULLISH CONFIRMED", 80.0, 100.0,
                                     float("nan"), None, 60.0)


def test_a_structural_level_no_longer_masks_a_missing_atr():
    """
    The dangerous half of the audit's scenario. With a structural level present
    the levels came out of the structural branch and looked entirely normal —
    (98.0, 102.0, 104.0, 106.0) — while the ATR that is supposed to set stop
    distance contributed nothing and nothing was flagged anywhere.
    """
    from models.risk_model import RiskModel

    model = RiskModel()
    with pytest.raises(Exception):
        model.calculate_stop_targets("BULLISH CONFIRMED", 80.0, 100.0,
                                     float("nan"), 98.0, 60.0)


def test_valid_inputs_still_produce_levels():
    """The control. A guard that rejects everything is not a guard."""
    from models.risk_model import RiskModel

    stop, t1, t2, t3 = RiskModel().calculate_stop_targets(
        "BULLISH CONFIRMED", 80.0, 100.0, 2.0, None, 60.0)

    for value in (stop, t1, t2, t3):
        assert np.isfinite(value), (stop, t1, t2, t3)
    assert stop < 100.0 < t1 < t2 < t3, (stop, t1, t2, t3)


# ============================================================
# The panel
# ============================================================

def test_the_panel_never_prints_a_non_finite_number():
    """
    The audit's Observation 5. panel_render's safe_float converted NaN and
    infinity without checking, so "STOP LOSS : $nan" was reachable. The engine's
    three other safe_float implementations all check finiteness.
    """
    import inspect
    from core import panel_render

    src = inspect.getsource(panel_render)
    assert "math.isfinite" in src or "np.isfinite" in src, (
        "panel_render's safe_float no longer checks finiteness; a NaN price "
        "would print as the literal text 'nan' in a dollar field"
    )


# ============================================================
# End to end
# ============================================================

def test_a_stale_decision_bar_now_degrades_the_routed_run():
    """
    The finding, end to end, through the production path.

    Before: degraded False, missing_inputs [], full risk plan, entry quality
    moved from 45.18 to 45.25 — a different answer, produced from the previous
    bar's ADX, reported as a clean analysis.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    import indicators.indicators as ind
    from data.data_fetcher import DataFetcher, data_fetcher
    from models.signal_router import SignalRouter

    real_adx = ind.ta.adx
    original_url = data_fetcher.base_url
    try:
        ind.ta.adx = _trailing_nan(real_adx)
        data_fetcher.base_url = UNREACHABLE
        DataFetcher.set_pinned_source(PINNED_DIR)
        decision = SignalRouter().route(symbol="AEROUSDT", timeframe="4h")
    finally:
        ind.ta.adx = real_adx
        DataFetcher.clear_pinned_source()
        data_fetcher.base_url = original_url

    block = decision.get("degradation", {})
    assert block.get("degraded") is True, (
        f"ADX had no value at the decision bar and the run reports itself "
        f"clean: {block}"
    )
    assert any("ADX" in m for m in block.get("missing_inputs", [])), (
        f"the degradation block does not name ADX: {block.get('missing_inputs')}"
    )
    assert block.get("trading_authorized") is False, (
        "a run whose indicator had no value at the decision bar still "
        "authorizes trading"
    )
