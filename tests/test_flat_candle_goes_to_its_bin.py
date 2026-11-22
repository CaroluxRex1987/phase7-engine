"""
A flat candle's volume goes to the bin that holds its price.

HELD-BACK DEFECT H5, found 18 October 2026 (docs/PHASE7_NEXT.md, "Found after
22 September"); fixed in stage 1 of the redesign, 14 November 2026
(docs/redesign_entry53_draft.md, section 8). compute_volume_profile spreads a
candle with a range over the bins it overlaps. A flat candle -- one whose
range is at most a millionth of its price -- took another branch, which gave
its whole volume to the bin whose nearest edge was closest to its price.
Neighbouring bins share an edge, so for a price in the lower half of a bin the
two distances tied and the strict `<` gave the volume to the bin BELOW the one
the price was in. The HVN and the LVN are bin midpoints, so one misplaced
candle could move either by a bin.

The fix: the bin is the interval (left, right] the price lies in, and the
first bin for a price on the range's lowest edge.

The frames below have ten bins of width 1 from 0 to 10: two wide candles with
no volume set the range, and one flat candle carries all the volume, so the
HVN is the midpoint of the bin it went to.

Fixture-free, per run_tests.py. numpy and pandas only: no engine import.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd

from indicators.volume_profile import compute_volume_profile


def _frame(flat_price):
    """Range 0 to 10 from two volume-less candles; one flat candle with volume."""
    return pd.DataFrame({
        "low":    [0.0, 5.0, flat_price],
        "high":   [5.0, 10.0, flat_price],
        "volume": [0.0, 0.0, 100.0],
    })


def _bin_of_flat_candle(flat_price):
    profile, hvn, _ = compute_volume_profile(_frame(flat_price), num_bins=10)
    filled = [i for i, v in enumerate(profile.to_numpy()) if v > 0]
    assert filled and profile.sum() == 100.0, profile
    assert len(filled) == 1, f"the flat candle's volume is in bins {filled}"
    interval = profile.index[filled[0]]
    assert hvn == interval.mid, (hvn, interval)
    return interval.left, interval.right


def _near(a, b):
    return abs(a - b) < 1e-9


def test_a_flat_candle_in_the_lower_half_of_a_bin_stays_in_that_bin():
    """The behavioural test: before the fix 4.2 went to (3, 4]."""
    left, right = _bin_of_flat_candle(4.2)
    assert _near(left, 4.0) and _near(right, 5.0), (left, right)


def test_a_flat_candle_in_the_upper_half_of_a_bin_stays_in_that_bin():
    left, right = _bin_of_flat_candle(4.7)
    assert _near(left, 4.0) and _near(right, 5.0), (left, right)


def test_a_flat_candle_on_an_edge_goes_to_the_bin_closed_on_that_edge():
    """Bins are (left, right], so 4.0 belongs to (3, 4]."""
    left, right = _bin_of_flat_candle(4.0)
    assert _near(left, 3.0) and _near(right, 4.0), (left, right)


def test_a_flat_candle_on_the_lowest_edge_goes_to_the_first_bin():
    """No right-closed bin holds the range's lowest price; the first bin takes it."""
    left, right = _bin_of_flat_candle(0.0)
    assert _near(left, 0.0) and _near(right, 1.0), (left, right)


def test_a_flat_candle_on_the_highest_edge_goes_to_the_last_bin():
    left, right = _bin_of_flat_candle(10.0)
    assert _near(left, 9.0) and _near(right, 10.0), (left, right)


def test_the_flat_branch_agrees_with_the_proportional_branch_where_they_meet():
    """
    A candle just wide enough to take the proportional branch, around a price
    inside a bin, puts its volume where a flat candle at that price does.
    """
    for price in (4.2, 4.7, 0.3, 9.9):
        flat = _bin_of_flat_candle(price)
        frame = _frame(price)
        frame.loc[2, "low"] = price - 1e-4
        frame.loc[2, "high"] = price + 1e-4
        profile, _, _ = compute_volume_profile(frame, num_bins=10)
        filled = [i for i, v in enumerate(profile.to_numpy()) if v > 1e-9]
        assert len(filled) == 1, (price, filled)
        interval = profile.index[filled[0]]
        assert (interval.left, interval.right) == flat, (price, interval, flat)


def test_no_volume_is_lost_or_added_by_the_flat_branch():
    rng = np.random.default_rng(58)
    prices = rng.uniform(0.0, 10.0, size=200)
    frame = pd.DataFrame({
        "low": np.concatenate([[0.0, 5.0], prices]),
        "high": np.concatenate([[5.0, 10.0], prices]),
        "volume": np.concatenate([[0.0, 0.0], np.full(200, 3.0)]),
    })
    profile, _, _ = compute_volume_profile(frame, num_bins=10)
    assert abs(profile.sum() - 600.0) < 1e-9, profile.sum()
    # Each flat candle is in the bin that holds its price.
    expected = np.zeros(10)
    for p in prices:
        expected[min(max(int(np.ceil(p)) - 1, 0), 9)] += 3.0
    assert np.allclose(profile.to_numpy(), expected), (profile.to_numpy(), expected)


def test_no_committed_candle_fixture_holds_a_flat_candle():
    """
    Why this fix moves no golden leaf: the flat branch is never taken on the
    committed candles. Counted by the function's own test of flatness.
    """
    fixtures = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")
    for rel in ("ohlcv_clean_4h.csv",
                os.path.join("pinned", "AEROUSDT_4h.csv"),
                os.path.join("pinned", "AEROUSDT_1d.csv"),
                os.path.join("pinned", "BTCUSDT_4h.csv")):
        df = pd.read_csv(os.path.join(fixtures, rel))
        flat = (df["high"] - df["low"]) <= (df["high"] + df["low"]) * 0.5 * 1e-6
        assert int(flat.sum()) == 0, f"{rel}: {int(flat.sum())} flat candle(s)"
