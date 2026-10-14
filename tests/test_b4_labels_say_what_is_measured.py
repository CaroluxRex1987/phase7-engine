"""
B4's labels: two readings were named for something they do not measure.

WHAT WAS THERE

The 5 October 2026 self-review (B4, Minor), confirmed on the real candles:

- Momentum divergence. indicators/trend_health.py compares this candle's
  close and RSI with the close and RSI four candles back. Its comments said
  "price making new highs" and "new lows", and the panel said "Momentum
  divergence is active -- price and momentum are disagreeing", both of which
  read as swing highs against swing highs. A close above the close four
  candles back can sit far below the highs in between. It fired on 11.9% of
  the bars counted, and it vetoes the side it points against.
- Volume divergence. structure.py's label fired whenever this candle's volume
  was below the volume four candles back, volume was not expanding, and the
  close had moved at all from four candles back. It was the most common
  volume label (39% of bars), printed as "VOLUME DIVERGENCE", and cost
  validation_score 25 points with the note "Volume divergence or weakness
  detected."

THE RULING

Viktor's, 14 October 2026, by agreeing to Claude's suggestion (option B of
three, and the WEAK clean-up): the printed sentences say what is compared;
the volume label is renamed FADING VOLUME; the decision keys
momentum_divergence and divergence_direction keep their names. Whether the
divergence should veto a side is a trading rule, Viktor's, not ruled -- these
tests check words and leave every score and action as it was.

WHY THE VOCABULARY TEST

core/engine_core.py matched the volume label by part of a word:
`"DIVERGENCE" in v or "WEAK" in v or "EXHAUSTION" in v`. Renaming the label
in structure.py alone would have dropped the 25 points without a test
failing. So the detector is run through every label it can return, and each
must be one bias_engine scores and one volume_agreement answers for itself.

Every test here is fixture-free, so run_tests.py runs them too.
"""

import os
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from indicators.trend_health import compute_trend_health
from models.bias_engine import _VOLUME_SENTIMENT_SCORES
from models.entry_model import signal_blockers
from models.exit_model import build_exit_watch
from structure.structure import StructureEngine


# --- momentum: what trend_health compares -----------------------------------

def _trend_frame(closes, rsis):
    n = len(closes)
    closes = np.asarray(closes, dtype=float)
    return pd.DataFrame({
        "open": closes,
        "high": closes * 1.001,
        "low": closes * 0.999,
        "close": closes,
        "EMA20_Slope": np.full(n, 0.5),
        "EMA50_Slope": np.full(n, 0.3),
        "ADX": np.full(n, 30.0),
        "RSI": np.asarray(rsis, dtype=float),
    })


def test_the_divergence_compares_four_candles_back_not_highs():
    """
    The close four candles back is 1.00; the candles in between rise to
    2.00; this candle closes at 1.10, far below that high. RSI is lower than
    four candles back. No new high was made, and the engine still records a
    BEARISH divergence -- which is why the sentences cannot say "new highs".
    """
    closes = [1.0] * 25 + [1.0, 1.5, 2.0, 1.5, 1.1]
    rsis = [50.0] * 25 + [60.0, 70.0, 75.0, 65.0, 55.0]
    out = compute_trend_health(_trend_frame(closes, rsis))
    assert max(closes[-4:-1]) > closes[-1], "the fixture must not make a new high"
    assert out["momentum_divergence"] is True, out
    assert out["divergence_direction"] == "BEARISH", out

    # And the mirror: no new low, recorded BULLISH.
    closes = [2.0] * 25 + [2.0, 1.5, 1.0, 1.5, 1.9]
    rsis = [50.0] * 25 + [40.0, 30.0, 25.0, 35.0, 45.0]
    out = compute_trend_health(_trend_frame(closes, rsis))
    assert min(closes[-4:-1]) < closes[-1]
    assert out["momentum_divergence"] is True, out
    assert out["divergence_direction"] == "BULLISH", out


def _flag(direction, present=True):
    trend = {"momentum_divergence": True}
    if present:
        trend["divergence_direction"] = direction
    flags = build_exit_watch(trend, {}, {"raw": "BULLISH"}, 1.0, 1.0, 1.1)
    hits = [f for f in flags if f.startswith("Price and RSI disagree")]
    assert len(hits) == 1, flags
    return hits[0]


def test_the_exit_flag_says_what_is_compared_and_which_way():
    bearish = _flag("BEARISH")
    assert bearish == (
        "Price and RSI disagree over the last four candles (bearish): the "
        "close is above the close four candles back, while RSI is below its "
        "value then. An early warning worth watching.")
    bullish = _flag("BULLISH")
    assert bullish == (
        "Price and RSI disagree over the last four candles (bullish): the "
        "close is below the close four candles back, while RSI is above its "
        "value then. An early warning worth watching.")
    for flag in (bearish, bullish):
        assert "divergence" not in flag.lower(), flag


def test_an_unrecorded_direction_is_named_not_guessed():
    for direction, present in (("NONE", True), ("UNKNOWN", True), (None, False)):
        flag = _flag(direction, present)
        assert "which way was not recorded" in flag, flag
        assert "(bearish)" not in flag and "(bullish)" not in flag, flag


def test_no_divergence_no_flag():
    """The control: a flag that always printed would pass the tests above."""
    flags = build_exit_watch({"momentum_divergence": False,
                              "divergence_direction": "BEARISH"},
                             {}, {"raw": "BULLISH"}, 1.0, 1.0, 1.1)
    assert not any(f.startswith("Price and RSI disagree") for f in flags), flags


def test_the_blockers_say_what_is_compared():
    assert signal_blockers("LONG", "BULLISH TREND", True, "BEARISH", adx=30.0) == [
        "a bearish price/RSI disagreement over four candles points against "
        "the trade"]
    assert signal_blockers("SHORT", "BEARISH TREND", True, "BULLISH", adx=30.0) == [
        "a bullish price/RSI disagreement over four candles points against "
        "the trade"]
    for direction in ("NONE", "UNKNOWN", None):
        blockers = signal_blockers("LONG", "BULLISH TREND", True, direction,
                                   adx=30.0)
        assert blockers == [
            "price and RSI disagree over four candles, but the direction was "
            f"recorded as {direction!r}, so it cannot be shown not to point "
            "against the trade"], blockers


# --- volume: the detector's vocabulary --------------------------------------

def _volume_frame(closes, volumes):
    return pd.DataFrame({"close": np.asarray(closes, dtype=float),
                         "volume": np.asarray(volumes, dtype=float)})


RISING = list(np.linspace(1.0, 1.2, 20))
FALLING = list(np.linspace(1.2, 1.0, 20))
FLAT = [1.0] * 20
EXPANDING = [100.0] * 15 + [300.0] * 5      # 5-candle mean 300 > 1.2 x 150
GROWING = list(np.linspace(100.0, 119.0, 20))  # rising, not expanding
SHRINKING = list(np.linspace(119.0, 100.0, 20))
STEADY = [100.0] * 20

# One frame per branch of _volume_sentiment_simple, in its order.
BRANCH_FRAMES = {
    "STRONG BULLISH ACCUMULATION": (RISING, EXPANDING),
    "BULLISH VOLUME SUPPORT": (RISING, GROWING),
    "STRONG BEARISH DISTRIBUTION": (FALLING, EXPANDING),
    "BEARISH VOLUME PRESSURE": (FALLING, GROWING),
    "FADING VOLUME": (RISING, SHRINKING),
    "VOLUME EXHAUSTION": (FLAT, EXPANDING),
    "NEUTRAL VOLUME": (FLAT, STEADY),
}


def _detect(closes, volumes):
    return StructureEngine()._volume_sentiment_simple(_volume_frame(closes, volumes))


def test_fading_volume_is_a_move_on_lower_volume_in_either_direction():
    """
    The label's whole condition: this candle's volume below the volume four
    candles back, no expansion, and the close moved -- up or down. Nothing
    compares a trend in volume with a trend in price.
    """
    assert _detect(RISING, SHRINKING) == "FADING VOLUME"
    assert _detect(FALLING, SHRINKING) == "FADING VOLUME"
    # The control: the same falling-price frame on rising volume is not it.
    assert _detect(FALLING, GROWING) == "BEARISH VOLUME PRESSURE"


def test_every_label_the_detector_returns_is_one_the_engine_scores():
    """
    Each frame reaches the branch it is named for, and the set of labels
    reached is exactly the set bias_engine scores. A label renamed in one
    place and not the other fails here.
    """
    produced = {}
    for expected, (closes, volumes) in BRANCH_FRAMES.items():
        produced[expected] = _detect(closes, volumes)
    assert produced == {k: k for k in BRANCH_FRAMES}, produced
    assert set(produced.values()) == set(_VOLUME_SENTIMENT_SCORES), (
        sorted(set(produced.values()) ^ set(_VOLUME_SENTIMENT_SCORES)))
    assert "VOLUME DIVERGENCE" not in _VOLUME_SENTIMENT_SCORES


def test_no_warning_label_reaches_the_neutral_note():
    """
    Every label without a direction, other than NEUTRAL VOLUME, costs
    validation 25 points under every bias, with a note of its own. This is
    the test that fails if structure.py renames a warning label and
    core/engine_core.py does not follow.
    """
    pytest.importorskip(
        "pandas_ta",
        reason="core.engine_core imports indicators.indicators, which imports "
               "pandas_ta at module level. volume_agreement itself needs neither.")
    from core.engine_core import volume_agreement

    warnings = [label for label in (_detect(c, v) for c, v in BRANCH_FRAMES.values())
                if "BULLISH" not in label and "BEARISH" not in label
                and label != "NEUTRAL VOLUME"]
    assert sorted(warnings) == ["FADING VOLUME", "VOLUME EXHAUSTION"], warnings
    notes = set()
    for label in warnings:
        for bias in ("BULLISH", "BEARISH", "NEUTRAL"):
            delta, note = volume_agreement(label, bias)
            assert delta == -25.0, (label, bias, delta)
            assert note != "Volume sentiment is neutral.", (label, bias)
            assert "divergence" not in note.lower(), note
            notes.add((label, note))
    assert dict(notes) == {
        "FADING VOLUME": ("This candle's volume is below the volume four "
                          "candles back, and volume is not expanding."),
        "VOLUME EXHAUSTION": ("Volume is expanding while the close has moved "
                              "less than 0.1% from four candles back."),
    }
