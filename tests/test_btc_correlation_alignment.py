"""
Audit finding (a) — the BTC relationship was measured on unpaired bars.

WHAT WAS WRONG

models/btc_context.py:

    aero_series = pd.Series(aero_closes).reset_index(drop=True)
    btc_series  = pd.Series(btc_closes).reset_index(drop=True)

Both series arrive indexed by timestamp — data_fetcher sets that index — and
both lines threw it away. The two tails were then paired by POSITION, so bar
i of AERO was correlated against bar i of BTC whatever four hours those two
bars actually belonged to.

WHY IT SURVIVED

In the ordinary case both fetches return the same 450 candles and the
positional pairing happens to BE the timestamp pairing. On this repo's pinned
fixtures the two indexes share all 450 timestamps, and the old code and the
new code agree to the last decimal. There was nothing to see until the two
series differed by one bar — a candle closing between the two API calls, an
exchange gap, a stale feed.

Measured on the pinned fixtures, dropping one BTC bar from inside the
30-candle window, across all 31 positions: the printed correlation moved by a
median of 0.105 (max 0.165), beta by a median of 0.135, and the printed label
changed in 4 of the 31. `n_observations` read 30 either way.

THE SECOND HALF

Every failure in that module returned `0.0, 0.0, 0`. Zero is a correlation a
real pair of independent assets produces, so a failure was indistinguishable
from a measurement, and the panel printed

    CORRELATION   : WEAK / NO CLEAR RELATIONSHIP (+0.00) over last 0 candles
    BTC SENSITIVITY (beta): 0.00x

— a finding about two assets, from nothing. Same defect as trend_health's
50.0 and RSI's 50.0, in the third module to carry it.
"""

import json
import math
import os

import numpy as np
import pandas as pd
import pytest

from conftest import REPO_ROOT

PINNED_DIR = os.path.join(REPO_ROOT, "tests", "fixtures", "pinned")
UNREACHABLE = "http://127.0.0.1:9"

BAR = pd.Timedelta("4h")
START = pd.Timestamp("2026-01-01 00:00:00")


def _series(values, start=START, step=BAR):
    idx = pd.DatetimeIndex([start + i * step for i in range(len(values))])
    return pd.Series([float(v) for v in values], index=idx)


def _walk(n, seed, drift=0.0):
    rng = np.random.default_rng(seed)
    steps = rng.normal(drift, 0.02, size=n)
    return list(100.0 * np.exp(np.cumsum(steps)))


def _reference(aero, btc, window=30):
    """Correlation and beta computed the obvious correct way, independently
    of the module under test, so this is a check and not a restatement."""
    joined = pd.concat({"a": aero, "b": btc}, axis=1, join="inner").dropna()
    joined = joined.sort_index().tail(window + 1)
    ar = joined["a"].pct_change()
    br = joined["b"].pct_change()
    keep = ar.notna() & br.notna()
    ar, br = ar[keep], br[keep]
    if len(ar) < 3:
        return None
    return float(ar.corr(br)), float(np.cov(ar, br)[0, 1] / br.var()), len(ar)


# ============================================================
# The pairing
# ============================================================

def test_a_missing_bar_no_longer_shifts_every_pairing():
    """
    The defect itself. BTC is missing one bar from inside the window, which
    is what a candle closing between the two API calls looks like.
    """
    from models.btc_context import compute_correlation_beta

    aero = _series(_walk(60, seed=1))
    btc = _series(_walk(60, seed=2))
    btc_gapped = btc.drop(btc.index[-8])

    got = compute_correlation_beta(aero, btc_gapped, window=30)
    want = _reference(aero, btc_gapped, window=30)

    assert want is not None
    assert got[2] == want[2], (
        f"paired {got[2]} observations, the timestamp join gives {want[2]}"
    )
    assert got[0] == pytest.approx(want[0], abs=1e-12), (
        f"correlation {got[0]:+.6f} against the timestamp-aligned "
        f"{want[0]:+.6f}. A gap in one series must not shift the other's "
        f"bars against it."
    )
    assert got[1] == pytest.approx(want[1], abs=1e-12)


def test_the_positional_answer_and_the_aligned_answer_actually_differ_here():
    """
    Negative control for the test above. If these two agreed on this data,
    the test would pass on code that still pairs by position and would be
    proving nothing.
    """
    aero = _series(_walk(60, seed=1))
    btc = _series(_walk(60, seed=2))
    btc_gapped = btc.drop(btc.index[-8])

    positional = _reference(
        aero.reset_index(drop=True),
        btc_gapped.reset_index(drop=True).set_axis(
            pd.RangeIndex(len(btc_gapped))),
        window=30,
    )
    aligned = _reference(aero, btc_gapped, window=30)

    assert positional is not None and aligned is not None
    assert abs(positional[0] - aligned[0]) > 1e-3, (
        "the fixture chosen for this test does not actually distinguish "
        "positional pairing from timestamp pairing, so the test above is "
        "vacuous. Pick data where it does."
    )


def test_two_series_that_share_no_timestamps_measure_nothing():
    """
    Not 'they are uncorrelated'. Nothing was compared.
    """
    from models.btc_context import compute_correlation_beta

    aero = _series(_walk(60, seed=3), start=START)
    btc = _series(_walk(60, seed=4), start=START + pd.Timedelta("2h"))

    correlation, beta, n = compute_correlation_beta(aero, btc, window=30)

    assert n == 0, f"reported {n} paired observations from a disjoint index"
    assert math.isnan(correlation), (
        f"returned correlation {correlation!r} for two series with no shared "
        f"timestamps. A number here is a finding nobody measured."
    )
    assert math.isnan(beta)


def test_series_without_a_time_index_are_refused_not_approximated():
    from models.btc_context import compute_correlation_beta

    aero = pd.Series(_walk(60, seed=5))
    btc = pd.Series(_walk(60, seed=6))

    correlation, beta, n = compute_correlation_beta(aero, btc, window=30)

    assert n == 0 and math.isnan(correlation) and math.isnan(beta), (
        f"got {(correlation, beta, n)!r}. Without a shared time index there "
        f"is no fact about which bar belongs beside which, so pairing them "
        f"by position invents one."
    )


def test_perfectly_aligned_series_are_unchanged_by_the_fix():
    """
    The equivalence check. The normal case is the case this must not move,
    and it is why the golden snapshot does not move either.
    """
    from models.btc_context import compute_correlation_beta

    aero = _series(_walk(60, seed=7))
    btc = _series(_walk(60, seed=8))

    got = compute_correlation_beta(aero, btc, window=30)
    want = _reference(aero, btc, window=30)

    assert got[2] == want[2] == 30
    assert got[0] == pytest.approx(want[0], abs=1e-12)
    assert got[1] == pytest.approx(want[1], abs=1e-12)


def test_the_pinned_fixtures_are_fully_paired():
    """
    States the fact the golden snapshot rests on, so it fails loudly if a
    fixture is ever replaced with one that does not share every timestamp.
    """
    aero = pd.read_csv(os.path.join(PINNED_DIR, "AEROUSDT_4h.csv"))
    btc = pd.read_csv(os.path.join(PINNED_DIR, "BTCUSDT_4h.csv"))
    aero.columns = [c.lower() for c in aero.columns]
    btc.columns = [c.lower() for c in btc.columns]

    shared = set(aero["timestamp"]) & set(btc["timestamp"])

    assert len(shared) == len(aero) == len(btc), (
        f"the pinned AERO and BTC fixtures share {len(shared)} of "
        f"{len(aero)}/{len(btc)} timestamps. The golden snapshot was "
        f"baselined on the assumption that they are fully paired, which is "
        f"why timestamp alignment did not move it."
    )


# ============================================================
# Nothing measured is reported as nothing measured
# ============================================================

@pytest.mark.parametrize("value", [None, float("nan"), float("inf"), "banana", object()])
def test_an_unusable_correlation_is_labelled_not_measured(value):
    from models.btc_context import classify_correlation

    assert classify_correlation(value) == "NOT MEASURED", (
        f"classify_correlation({value!r}) claimed a relationship. It used to "
        f"coerce anything unusable to 0.0 and return 'WEAK / NO CLEAR "
        f"RELATIONSHIP', which is a finding rather than the absence of one."
    )


@pytest.mark.parametrize("r,expected", [
    (0.85, "STRONG POSITIVE"),
    (-0.85, "STRONG NEGATIVE"),
    (0.45, "MODERATE POSITIVE"),
    (0.10, "WEAK / NO CLEAR RELATIONSHIP"),
])
def test_a_real_coefficient_is_still_labelled_normally(r, expected):
    """Negative control: the NOT MEASURED branch must not swallow real
    readings."""
    from models.btc_context import classify_correlation

    assert classify_correlation(r) == expected


def test_the_panel_does_not_print_a_correlation_it_does_not_have():
    from core.panel_render import render_panel

    decision = {
        "symbol": "TESTUSDT", "timeframe": "4h",
        "btc_context": {
            "available": True, "detailed": "NEUTRAL", "regime": "NEUTRAL STRUCTURE",
            "volatility": "NORMAL", "correlation": None,
            "correlation_label": "NOT MEASURED", "beta": None,
            "broad_market_stress": False, "n_observations": 0,
            "btc_adjusted_confidence": 50.0, "reasons": [],
        },
    }

    panel = render_panel(decision)

    assert "NOT MEASURED" in panel, "the panel does not say the pairing failed"
    assert "over last 0 candles" not in panel, (
        "the panel still prints 'over last 0 candles' — a sentence that has "
        "already asserted a relationship by the time it admits there was no "
        "data"
    )
    assert "(+0.00)" not in panel, (
        "the panel still prints a correlation of +0.00 for a run that "
        "measured none. Zero is a value a real pair of assets produces."
    )
    assert "0.00x" not in panel, (
        "the panel still prints a beta of 0.00x — 'AERO does not respond to "
        "BTC', asserted from nothing"
    )


def test_the_panel_still_prints_a_correlation_it_does_have():
    """Negative control for the test above."""
    from core.panel_render import render_panel

    decision = {
        "symbol": "TESTUSDT", "timeframe": "4h",
        "btc_context": {
            "available": True, "detailed": "BULLISH CONFIRMED",
            "regime": "BULLISH TREND", "volatility": "NORMAL",
            "correlation": 0.57, "correlation_label": "MODERATE POSITIVE",
            "beta": 0.98, "broad_market_stress": False, "n_observations": 30,
            "btc_adjusted_confidence": 78.33, "reasons": [],
        },
    }

    panel = render_panel(decision)

    assert "MODERATE POSITIVE" in panel
    assert "(+0.57)" in panel
    assert "over last 30 candles" in panel
    assert "0.98x" in panel
    assert "NOT MEASURED" not in panel


# ============================================================
# The decision model
# ============================================================

def _btc_ctx(**over):
    base = {
        "available": True, "score": 60.0, "detailed": "BULLISH CONFIRMED",
        "correlation": 0.80, "correlation_label": "STRONG POSITIVE",
        "beta": 1.0, "broad_market_stress": False, "n_observations": 30,
    }
    base.update(over)
    return base


def test_an_unmeasured_correlation_moves_the_confidence_by_nothing():
    from models.decision_model import DecisionModel

    model = DecisionModel()
    bias = {"score": 60.0, "raw": "BULLISH"}

    out = model._compute_btc_adjusted(
        70.0, bias,
        _btc_ctx(correlation=None, correlation_label="NOT MEASURED",
                 beta=None, n_observations=0),
        symbol="TESTUSDT")

    assert out["available"] is True
    assert math.isfinite(out["btc_adjusted_confidence"]), (
        f"btc_adjusted_confidence is {out['btc_adjusted_confidence']!r} — a "
        f"NaN correlation propagated into the number the panel prints"
    )
    assert out["adjustment"] == pytest.approx(0.0), (
        f"adjusted by {out['adjustment']} on a relationship that was never "
        f"measured"
    )
    assert out["btc_adjusted_confidence"] == pytest.approx(70.0)


def test_a_measured_correlation_still_adjusts():
    """Negative control: gating on 'measured' must not disable the feature."""
    from models.decision_model import DecisionModel

    model = DecisionModel()
    out = model._compute_btc_adjusted(
        70.0, {"score": 60.0, "raw": "BULLISH"}, _btc_ctx(), symbol="TESTUSDT")

    assert out["adjustment"] > 0.0, (
        "a strong positive correlation with an agreeing BTC produced no "
        "adjustment — the gate is swallowing real readings"
    )


def test_the_reason_string_does_not_claim_a_relationship_it_lacks():
    from models.decision_model import DecisionModel

    model = DecisionModel()
    out = model._compute_btc_adjusted(
        70.0, {"score": 60.0, "raw": "BULLISH"},
        _btc_ctx(correlation=None, correlation_label="NOT MEASURED",
                 beta=None, n_observations=0),
        symbol="TESTUSDT")

    reason = " ".join(out["reasons"]).lower()

    assert "could not be measured" in reason, (
        f"the reason does not say the pairing failed: {reason!r}"
    )
    assert "+0.00" not in reason and "over the last 0 candles" not in reason, (
        f"the reason still quotes a coefficient measured on nothing: {reason!r}"
    )
    assert "relationship relationship" not in reason


# ============================================================
# What reaches the record
# ============================================================

def test_the_btc_block_is_strict_json(monkeypatch):
    """
    NaN is the honest in-memory value and invalid JSON. engine_core converts
    it to None at the boundary, the way it already does for atr and
    structural_level. json.dumps(allow_nan=False) is what would catch a
    regression: Python emits a bare NaN token by default, which every strict
    reader rejects.
    """
    pytest.importorskip("pandas_ta")

    import core.engine_core as ec
    from data.data_fetcher import DataFetcher, data_fetcher

    original_url = data_fetcher.base_url
    try:
        data_fetcher.base_url = UNREACHABLE
        DataFetcher.set_pinned_source(PINNED_DIR)
        decision = ec.Phase7Engine().run(symbol="AEROUSDT", timeframe="4h",
                                         save_chart=False)
    finally:
        DataFetcher.clear_pinned_source()
        data_fetcher.base_url = original_url

    btc = decision.get("btc_context", {})
    assert btc, f"no btc_context in the decision object: {sorted(decision)[:12]}"

    try:
        json.dumps(btc, allow_nan=False, default=str)
    except ValueError as e:
        pytest.fail(
            f"the btc_context block is not strict JSON: {e}. A NaN reached "
            f"the decision object instead of being converted to None."
        )
