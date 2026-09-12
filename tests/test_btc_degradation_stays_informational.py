"""
BTC context must stay informational -- Viktor's ruling, 12 September 2026.

WHAT WAS WRONG

SWEEP ITEM 11 (8 September 2026, c3b0d43, GLM F-6) fixed "BTC-side trend
degradations were computed and discarded" by appending them, as `f"BTC {d}"`,
into the SAME `degradation` list `DecisionModel.evaluate()` reads to cap
`confidence_score` at `DEGRADED_CONFIDENCE_CEILING` (50.0) and gate
`trading_authorized`. Requested-run 4 (GPT-6 Astra's round-5 report) found
this empirically on 12 September: mocking BTC's own `ta.adx` call to fail --
AERO's own indicators, structure and trend left completely real -- dropped
AERO's `confidence_score` from 78.70 to exactly 50.0 and flipped
`trading_authorized` from true to false, with `missing_inputs` reading only
`["BTC ADX (column absent)"]`. Nothing about AERO's own analysis was
incomplete; the BTC-only context block did that on its own.

That is the opposite of `engine_core.py`'s own comment at the BTC context
assembly: "This NEVER changes BIAS, DECISION, entry, risk, or targets above
... BTC context is additive, never a replacement or distortion of the
AERO-only analysis." Viktor ruled: BTC context is informational, a bonus to
consider, and must never gate AERO's own confidence or trading
authorization -- the same relationship `btc_adjusted_confidence` already has
with the main `confidence_score` (a separate, clearly-labelled number, never
a gate).

Item 11's own motivation was real, though: a BTC indicator failure should not
be silently dropped with nothing but a log line. So the fix keeps it
recorded -- inside `btc_context["degraded_inputs"]`, which reaches the
decision log -- and stops it from reaching the shared `degradation` list or
the live panel (panel_render.py does not read this field).

This file is the regression guard for both halves: AERO's confidence and
trading_authorized must not move when only BTC's own indicators are
incomplete (the gate removed), and the BTC failure must still be visible
somewhere in the returned decision object (the record item 11 was protecting
kept).
"""

import os
import shutil
import tempfile

import pytest

from conftest import fixture, REPO_ROOT

SYMBOL = "TESTUSDT"
TIMEFRAME = "4h"
MACRO_TIMEFRAME = "1d"


def _engine_available():
    try:
        import pandas_ta  # noqa: F401
        return True
    except Exception:
        return False


def _write_pinned_set(directory):
    import pandas as pd

    base = pd.read_csv(fixture("ohlcv_clean_4h.csv"))
    base.to_csv(os.path.join(directory, f"{SYMBOL}_{TIMEFRAME}.csv"), index=False)

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

    btc = base.copy()
    for col in ("open", "high", "low", "close"):
        btc[col] = btc[col].to_numpy()[::-1] * 137_000.0
    btc["volume"] = btc["volume"].to_numpy()[::-1] * 3.0
    btc.to_csv(os.path.join(directory, f"BTCUSDT_{TIMEFRAME}.csv"), index=False)


def _run():
    from data.data_fetcher import DataFetcher, data_fetcher
    from models.signal_router import SignalRouter

    tmp = tempfile.mkdtemp(prefix="phase7_btc_isolation_")
    original_url = data_fetcher.base_url
    try:
        _write_pinned_set(tmp)
        data_fetcher.base_url = "http://127.0.0.1:9"
        DataFetcher.set_pinned_source(tmp)
        return SignalRouter().route(symbol=SYMBOL, timeframe=TIMEFRAME)
    finally:
        DataFetcher.clear_pinned_source()
        data_fetcher.base_url = original_url
        shutil.rmtree(tmp, ignore_errors=True)


def _fail_only_the_btc_call(real_fn):
    """
    engine_core.py calls compute_trend_health twice per run: once for AERO's
    own df_struct, once for BTC's df_btc_struct. This returns the real value
    for the first call and a degraded value for the second (BTC's) -- so
    AERO's own trend_health is completely real and only BTC's is missing
    ADX, the same shape requested-run 4 used.
    """
    state = {"n": 0}

    def _inner(df):
        state["n"] += 1
        if state["n"] >= 2:
            real = real_fn(df)
            degraded = dict(real)
            degraded["degraded_inputs"] = list(real.get("degraded_inputs") or []) + ["ADX (column absent)"]
            return degraded
        return real_fn(df)
    return _inner


def test_a_btc_only_indicator_failure_does_not_move_aeros_confidence_or_gate(monkeypatch):
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    import indicators.trend_health as th

    control = _run()
    assert "error" not in control, control.get("error")

    real_compute_trend_health = th.compute_trend_health
    monkeypatch.setattr(
        "core.engine_core.compute_trend_health",
        _fail_only_the_btc_call(real_compute_trend_health),
    )
    degraded_run = _run()
    assert "error" not in degraded_run, degraded_run.get("error")

    assert degraded_run["risk"]["confidence_score"] == control["risk"]["confidence_score"], (
        "a BTC-only indicator failure changed AERO's own confidence_score. "
        "BTC context is informational and must never gate it -- Viktor's ruling, "
        "12 September 2026."
    )
    assert degraded_run["exit"]["action"] == control["exit"]["action"], (
        "a BTC-only indicator failure changed AERO's own action."
    )
    assert degraded_run["degradation"] == control["degradation"], (
        "a BTC-only indicator failure leaked into AERO's own degradation block: "
        f"{degraded_run['degradation']!r} vs control {control['degradation']!r}. "
        "It must not appear in the shared `degradation` list or move "
        "`trading_authorized`."
    )


def test_the_btc_only_failure_is_still_visible_in_the_record(monkeypatch):
    """
    The other half of the ruling: not gating AERO must not mean going back to
    fully silent (the problem SWEEP ITEM 11 existed to fix). It has to show
    up somewhere in the returned decision object, even though nowhere that
    gates AERO or reaches the live panel.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    import indicators.trend_health as th

    real_compute_trend_health = th.compute_trend_health
    monkeypatch.setattr(
        "core.engine_core.compute_trend_health",
        _fail_only_the_btc_call(real_compute_trend_health),
    )
    degraded_run = _run()
    assert "error" not in degraded_run, degraded_run.get("error")

    btc = degraded_run["btc_context"]
    assert btc["available"] is True
    assert "ADX (column absent)" in btc["degraded_inputs"], (
        "the BTC indicator failure was not recorded anywhere -- silently "
        "dropped again, the exact problem SWEEP ITEM 11 was meant to fix."
    )


def test_the_negative_control_has_no_degraded_inputs():
    """
    A healthy BTC run must report an empty degraded_inputs list, not a
    missing key -- so a consumer can rely on the field always being present
    when btc_context is available.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    control = _run()
    assert "error" not in control, control.get("error")
    assert control["btc_context"]["degraded_inputs"] == []
