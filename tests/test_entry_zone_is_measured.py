"""
Audit finding (4) — the entry zone was fabricated when the EMAs were missing.

WHAT WAS WRONG, IN TWO FILES

core/engine_core.py:

    entry_zone_lower = float(EMA_20) if present else close * 0.99
    entry_zone_upper = float(EMA_50) if present else close * 1.01

models/entry_model.py:

    close      = safe_float(..., 1.0)
    zone_lower = safe_float(zone_lower, close * 0.99)
    zone_upper = safe_float(zone_upper, close * 1.01)
    if zone_width <= 1e-8: zone_width = close * 0.01

Five fabricated constants between them. A missing EMA pair became a band one
percent either side of the last price — a number with no relationship to this
instrument or to anything measured — and that band then scored the 30-point
EMA position component AND the 25-point ATR distance component, which measures
distance to this zone. 55 of 100 derived from a constant, printed as an entry
quality score.

The worst of the five is the close-price fallback: a price that could not be
read became $1.00, and every distance, ratio and percentage in the function is
measured against it.

THE ONE THAT WAS NOT ON THE LIST

engine_core put EMA_20 in `lower` and EMA_50 in `upper` unconditionally. In an
uptrend the fast EMA is above the slow one, so the panel printed

    ENTRY ZONE    : $0.4981 - $0.4918

with the lower bound above the upper — seen on the live run at fa68197.
entry_model swaps them before scoring, so the arithmetic was right the whole
time and only the display was wrong. That is why no test caught it and why
reading the panel did.

WHAT REPLACED IT

No zone means NaN, the run records the missing input, and the two components
that depend on the zone fall to their neutral value — this file's own policy
since Finding 3, on the grounds that lowering conviction is the degraded-run
flag's job. Scoring the absence as well would make a degraded run look like a
bad setup rather than an unmeasured one.
"""

import math
import os

import numpy as np
import pandas as pd
import pytest

from conftest import REPO_ROOT

PINNED_DIR = os.path.join(REPO_ROOT, "tests", "fixtures", "pinned")
UNREACHABLE = "http://127.0.0.1:9"


def _frame(close=1.2345, ema20=None, ema50=None, atr=0.01, rows=60, **cols):
    data = {"close": [close] * rows}
    if ema20 is not None:
        data["EMA_20"] = [ema20] * rows
    if ema50 is not None:
        data["EMA_50"] = [ema50] * rows
    if atr is not None:
        data["ATR"] = [atr] * rows
    data.update({k: [v] * rows for k, v in cols.items()})
    return pd.DataFrame(data)


# ============================================================
# No zone means no zone
# ============================================================

def test_an_absent_zone_is_not_invented_from_the_price():
    """
    The finding itself. NaN bounds must not become close*0.99 / close*1.01.
    """
    import models.entry_model as em
    from models.entry_model import calculate_entry_quality

    # getattr with the documented default, so this test fails on the
    # BEHAVIOUR against pre-fix code rather than on an ImportError for a
    # constant that did not exist yet. test_the_not_measured_policy_is_named
    # below is what guards the constant itself.
    neutral = getattr(em, "ZONE_POINTS_NOT_MEASURED", 15.0)

    close = 1.2345
    out = calculate_entry_quality(_frame(close=close),
                                  float("nan"), float("nan"))

    assert out["entry_status"] == "ZONE NOT AVAILABLE", (
        f"status is {out['entry_status']!r}. The old code fabricated a band "
        f"one percent either side of {close} and then reported which part of "
        f"it price was in."
    )
    assert out["ema_pos_pts"] == int(neutral), (
        f"scored {out['ema_pos_pts']} of 30 for a zone that was never "
        f"located. The fabricated band scored 5, 10, 20 or 30 depending on "
        f"where price happened to sit inside a constant."
    )
    assert math.isnan(out["distance_from_zone"]), (
        f"reported a distance of {out['distance_from_zone']} from a zone that "
        f"does not exist"
    )


def test_an_absent_zone_also_stops_the_atr_distance_being_scored():
    """
    The consequence that is easy to miss: the ATR component divides the
    distance TO THE ZONE by ATR. No zone, no distance, nothing to divide.
    """
    import models.entry_model as em
    from models.entry_model import calculate_entry_quality

    neutral = getattr(em, "ATR_POINTS_NOT_MEASURED", 15.0)

    out = calculate_entry_quality(_frame(atr=0.01), float("nan"), float("nan"))

    assert out["atr_dist_pts"] == int(round(neutral)), (
        f"atr_dist_pts is {out['atr_dist_pts']} on a run with no zone. ATR "
        f"was present, but the distance it scales is a distance to the zone."
    )


def test_only_one_bound_is_still_no_zone():
    from models.entry_model import calculate_entry_quality

    for lower, upper in ((1.0, float("nan")), (float("nan"), 1.0)):
        out = calculate_entry_quality(_frame(), lower, upper)
        assert out["entry_status"] == "ZONE NOT AVAILABLE", (
            f"bounds ({lower}, {upper}) produced {out['entry_status']!r}. "
            f"Half a zone is not a zone."
        )


def test_a_price_that_could_not_be_read_is_not_one_dollar():
    """
    The fabrication underneath all the others.
    """
    from models.entry_model import calculate_entry_quality

    df = pd.DataFrame({"close": [float("nan")] * 60, "ATR": [0.01] * 60})
    out = calculate_entry_quality(df, 0.99, 1.01)

    assert out["entry_status"] == "NO DATA", (
        f"status is {out['entry_status']!r}. close fell back to 1.0, so a "
        f"zone of 0.99-1.01 read as ACTIVE ENTRY ZONE — a perfect entry, "
        f"scored against a price nobody read."
    )
    assert out["score"] == 0.0
    assert math.isnan(out["distance_from_zone"])


def test_a_zone_with_no_width_is_not_given_one():
    """
    zone_width = close * 0.01 silently re-scaled all three bands, which are
    multiples of that width.
    """
    import models.entry_model as em
    from models.entry_model import calculate_entry_quality

    neutral = getattr(em, "ZONE_POINTS_NOT_MEASURED", 15.0)

    out = calculate_entry_quality(_frame(close=1.2345), 1.2345, 1.2345)

    assert out["entry_status"] == "ZONE HAS NO WIDTH", (
        f"status is {out['entry_status']!r} for two coincident EMAs"
    )
    assert out["ema_pos_pts"] == int(neutral)
    assert math.isfinite(out["distance_from_zone"]), (
        "distance_from_zone is a real measurement even when the zone has no "
        "width — it should still be reported"
    )


def test_the_not_measured_policy_is_named():
    """
    The two constants exist and are the midpoints they claim to be.

    Separated from the behavioural tests above deliberately: this one CAN
    only fail with an ImportError against pre-fix code, which proves a name
    is new and nothing about whether the defect was real. Keeping it apart
    stops it inflating the negative-control count.
    """
    from models.entry_model import (ATR_POINTS_NOT_MEASURED,
                                    ZONE_POINTS_NOT_MEASURED)

    assert ZONE_POINTS_NOT_MEASURED == 15.0    # of 30
    assert ATR_POINTS_NOT_MEASURED == 15.0     # of 25


# ============================================================
# The measured case is untouched
# ============================================================

@pytest.mark.parametrize("close,expected_status,expected_pts", [
    (1.10, "ACTIVE ENTRY ZONE", 30),      # dist 0.10 <= width 0.20
    (1.30, "NEAR ZONE", 20),              # dist 0.30 <= 2.0 x width = 0.40
    (1.60, "APPROACHING ZONE", 10),       # dist 0.60 <= 3.5 x width = 0.70
    (2.00, "AWAY FROM ZONE", 5),          # dist 1.00 >  0.70
])
def test_a_real_zone_still_scores_exactly_as_before(close, expected_status, expected_pts):
    """
    Negative control. The NOT-MEASURED branches must not swallow real
    readings, and the bands must not have moved.

    Zone 0.9 - 1.1: mid 1.0, width 0.2, so the band edges sit at a distance
    of 0.2, 0.4 and 0.7 from the mid. The first draft of this test put 1.13
    in the NEAR band -- 0.13 from the mid, which is ACTIVE. The test was
    wrong and reported the code as wrong.
    """
    from models.entry_model import calculate_entry_quality

    out = calculate_entry_quality(_frame(close=close), 0.9, 1.1)

    assert out["entry_status"] == expected_status
    assert out["ema_pos_pts"] == expected_pts
    assert out["distance_from_zone"] == pytest.approx(
        abs(close - 1.0) / close * 100.0)


def test_bounds_given_the_wrong_way_round_are_still_swapped():
    """
    engine_core now orders them, but this function is public and takes two
    separate arguments, so it cannot assume its caller did.
    """
    from models.entry_model import calculate_entry_quality

    forwards = calculate_entry_quality(_frame(close=1.0), 0.9, 1.1)
    backwards = calculate_entry_quality(_frame(close=1.0), 1.1, 0.9)

    assert forwards == backwards


# ============================================================
# engine_core's half
# ============================================================

def _run_pinned():
    """
    Through SignalRouter, not Phase7Engine.run(), because the assembled
    `degradation` BLOCK (degraded / missing_inputs / trading_authorized) is
    the router's. The engine returns the raw list, and the first draft of
    this file called .get() on it.
    """
    from data.data_fetcher import DataFetcher, data_fetcher
    from models.signal_router import SignalRouter

    original = data_fetcher.base_url
    try:
        data_fetcher.base_url = UNREACHABLE
        DataFetcher.set_pinned_source(PINNED_DIR)
        return SignalRouter().route(symbol="AEROUSDT", timeframe="4h")
    finally:
        DataFetcher.clear_pinned_source()
        data_fetcher.base_url = original


def _entry_lines(panel):
    """
    Only the two lines under test.

    The first draft asserted `"$0.0000" not in panel` and
    `"not located" not in panel` against the WHOLE panel, and both matched
    other lines -- a zeroed price elsewhere in a minimal fixture, and SWING
    STRUCT's own "not located this run". Rule 30: a substring assertion
    cannot see the shape of what it matched.
    """
    return "\n".join(
        line for line in panel.splitlines()
        if line.lstrip().startswith(("ENTRY ZONE", "ZONE DISTANCE"))
    )


def test_the_lower_bound_is_the_lower_of_the_two():
    """
    The defect the live panel showed. On this fixture the trend is up, so
    EMA_20 > EMA_50 and the old code printed them in that order under labels
    saying the opposite.
    """
    pytest.importorskip("pandas_ta")

    decision = _run_pinned()
    entry = decision.get("entry", {})

    assert entry, f"no entry block: {sorted(decision)[:12]}"
    lower = float(entry["zone_lower"])
    upper = float(entry["zone_upper"])

    assert lower <= upper, (
        f"zone_lower {lower:.8f} is above zone_upper {upper:.8f}. The panel "
        f"prints these in that order under those labels."
    )

    bar = decision["lineage"]["indicators_at_decision_bar"]
    ema_fast, ema_slow = float(bar["EMA_20"]), float(bar["EMA_50"])
    assert {round(lower, 8), round(upper, 8)} == {round(min(ema_fast, ema_slow), 8),
                                                 round(max(ema_fast, ema_slow), 8)}, (
        f"the bounds ({lower}, {upper}) are not the two EMAs "
        f"({ema_fast}, {ema_slow}) — ordering them must not change which "
        f"numbers they are"
    )


def test_a_missing_ema_pair_degrades_the_run_instead_of_inventing_a_band():
    """
    End to end, with the EMAs actually gone. The absence has to reach the
    degradation block, because that — not the sub-score — is what stops the
    run authorising a trade.
    """
    pytest.importorskip("pandas_ta")

    import indicators.indicators as ind

    original = ind.add_technical_indicators

    def without_emas(df, inplace=False):
        frame, failures = original(df, inplace=inplace)
        return frame.drop(columns=[c for c in ("EMA_20", "EMA_50")
                                   if c in frame.columns]), failures

    import core.engine_core as ec
    ec_original = ec.add_technical_indicators
    try:
        ec.add_technical_indicators = without_emas
        decision = _run_pinned()
    finally:
        ec.add_technical_indicators = ec_original

    assert "error" not in decision, (
        f"removing the EMAs ended the run: {decision.get('error')}. Viktor "
        f"ruled degrade, not halt."
    )

    entry = decision["entry"]
    assert math.isnan(float(entry["zone_lower"])), (
        f"zone_lower is {entry['zone_lower']!r} with no EMA_20 in the frame"
    )
    assert math.isnan(float(entry["zone_upper"]))
    assert entry["entry_status"] == "ZONE NOT AVAILABLE"

    block = decision.get("degradation", {})
    assert block.get("degraded") is True, (
        f"the EMAs were missing and the run does not report itself degraded: "
        f"{block}"
    )
    assert any("entry zone" in m.lower() for m in block.get("missing_inputs", [])), (
        f"the degradation block does not name the entry zone: "
        f"{block.get('missing_inputs')}"
    )


def test_a_normal_run_is_not_degraded_by_this():
    """Negative control for the test above."""
    pytest.importorskip("pandas_ta")

    decision = _run_pinned()
    block = decision.get("degradation", {})

    assert block.get("degraded") is False, (
        f"a clean pinned run reports itself degraded: {block}"
    )
    assert not any("entry zone" in m.lower()
                   for m in block.get("missing_inputs", []))


# ============================================================
# The panel
# ============================================================

def _panel(entry):
    from core.panel_render import render_panel
    return render_panel({"symbol": "TESTUSDT", "timeframe": "4h", "entry": entry})


def test_the_panel_does_not_print_a_zone_it_does_not_have():
    panel = _panel({
        "zone_lower": float("nan"), "zone_upper": float("nan"),
        "distance_from_zone": float("nan"),
        "entry_status": "ZONE NOT AVAILABLE", "score": 45.0,
    })

    lines = _entry_lines(panel)

    assert "not located" in lines, (
        f"the panel does not say the zone is missing: {lines!r}"
    )
    assert "$0.0000" not in lines, (
        f"the panel still prints $0.0000 - $0.0000 for an absent zone. Zero "
        f"is a price. Lines: {lines!r}"
    )
    assert "0.00% away from zone" not in lines, (
        f"the panel still prints 0.00% away — price sitting exactly on a "
        f"zone that was never found, which is the strongest claim this line "
        f"can make. Lines: {lines!r}"
    )
    assert "not measured" in lines


def test_the_panel_still_prints_a_zone_it_does_have():
    """Negative control."""
    panel = _panel({
        "zone_lower": 0.4918, "zone_upper": 0.4981,
        "distance_from_zone": 5.44,
        "entry_status": "AWAY FROM ZONE", "score": 36.66,
    })

    lines = _entry_lines(panel)

    assert "$0.4918 - $0.4981" in lines, lines
    assert "5.44% away from zone" in lines, lines
    assert "not located" not in lines, lines
