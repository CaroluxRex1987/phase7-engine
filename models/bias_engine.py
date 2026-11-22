import numpy as np

# ============================================================
# THE WEIGHTED SUM -- REMOVED at the redesign's stage 5, 15 November 2026
# ============================================================
#
# calculate_dynamic_bias stood here, with the six weights it blended
#
#     WEIGHT_TREND_HEALTH         = 0.30
#     WEIGHT_STRUCTURE_REGIME     = 0.20
#     WEIGHT_VOLUME_SENTIMENT     = 0.15
#     WEIGHT_SUPERTREND_DIRECTION = 0.15
#     WEIGHT_MACRO_BIAS           = 0.10
#     WEIGHT_REVERSAL_CONTINUATION= 0.10
#
# RAW_BIAS_THRESHOLD (20.0), the _VOLUME_SENTIMENT_SCORES table, the
# CHOCH-against-trend x0.5 discount, the clip to +/-100 and the
# `components` out-parameter that recorded each factor's input, signed
# value, weight and contribution as lineage.bias_components.
#
# It returned (raw_bias, bias_score). Stage 2 of the redesign took the
# direction off it -- bias.raw, bias.detailed and the plan's side come from
# direction_from_emas below (Viktor's ruling of 7 November 2026) -- and
# kept the call for its SCORE alone, because confidence was that score's
# magnitude (models/decision_model.py, _compute_confidence) and confidence
# left in this stage. Stage 5 removes confidence, so the score has no
# reader and the function, its constants and its breakdown go with it:
# bias.score, lineage.bias_components and the seven
# provenance.module_constants entries leave the record, which moves
# run_hash and the archive's file name.
#
# WHAT LEAVES WITH IT, AND WHY THAT IS THE POINT. The blend's own
# independence review (19 September 2026) had recorded that four of the six
# factors -- trend health 0.30, structure regime 0.20, SuperTrend direction
# 0.15 and macro bias 0.10, three quarters of the blend -- were four
# transforms of one measurement, the recent direction of close, and that
# bias_score presented their agreement as four independent confirmations.
# It was recorded and deliberately not fixed, because reweighting is a
# trading judgment this project could not evaluate. The redesign answers it
# by removing the blend rather than reweighting it: one rule reads the
# direction (EMA50's slope and the EMAs' order), and every other factor
# that survives the redesign is a GATE with a yes or no, not a weight in a
# sum. Nothing now blends two readings into one number.
#
# docs/build/indicator_overlap.py, whose variants zeroed these weights one
# at a time to measure that overlap, goes in this stage for the same
# reason: with no weights there is nothing for it to zero.



# ============================================================
# DYNAMIC REGIME ENGINE
# ============================================================

def calculate_dynamic_regime(df):
    """
    Returns:
        dynamic_regime (str)
        volatility_mode (str)
    """

    if df is None or df.empty:
        return "UNKNOWN", "UNKNOWN"

    # Volatility detection with NaN handling
    if "ATR" in df.columns:
        atr = df["ATR"].iloc[-1]
        price = df["close"].iloc[-1]

        # Fix: Handle NaN values and prevent division by zero
        if np.isfinite(atr) and np.isfinite(price) and price > 0:
            vol_ratio = atr / price
        else:
            vol_ratio = None  # unmeasured — do not invent MEDIUM

        # BUG FIX (found while cross-checking Option A's "volatility modes
        # are consistent" point): risk_model.py has a real "EXTREME
        # VOLATILITY" tier (widest stops, halved position sizing,
        # automatic EXTREME RISK classification) but this function -- the
        # only place volatility_state is ever produced -- topped out at
        # "HIGH VOLATILITY" and could never emit "EXTREME VOLATILITY".
        # That entire risk tier was dead code. Added the missing tier.
        if vol_ratio is None:
            volatility_mode = "UNKNOWN"
        elif vol_ratio > 0.04:
            volatility_mode = "EXTREME VOLATILITY"
        elif vol_ratio > 0.02:
            volatility_mode = "HIGH VOLATILITY"
        elif vol_ratio > 0.01:
            volatility_mode = "MEDIUM VOLATILITY"
        else:
            volatility_mode = "LOW VOLATILITY"
    else:
        volatility_mode = "UNKNOWN"

    # Regime detection (column name fixed in the A3/A4/A5 pass -- was
    # checking for "STRUCTURE_REGIME", which never existed; structure.py
    # names the column "STRUCTURE")
    if "STRUCTURE" in df.columns:
        dynamic_regime = df["STRUCTURE"].iloc[-1]
    else:
        dynamic_regime = "UNKNOWN STRUCTURE"

    return dynamic_regime, volatility_mode


# ============================================================
# DIRECTION (the redesign's stage 2, 14 November 2026)
# ============================================================
#
# Viktor's ruling of 7 November 2026 (docs/PHASE7_DECISIONS.md, "Ruling,
# 7 November 2026 -- the redesign's direction is EMA50's slope and the EMAs'
# order ..."), built as stage 2 of the redesign's six (DECISIONS, "Decision,
# 14 November 2026 -- the redesign's code is cut into six stages ..."):
#
#   BULLISH   EMA50_Slope > 0 and EMA_20 > EMA_50
#   BEARISH   EMA50_Slope < 0 and EMA_20 < EMA_50
#   NEUTRAL   anything else: the two disagree, the slope is exactly zero or
#             the averages are equal. A lean, and no side.
#
# EMA20_Slope is not read. No threshold: the agreement of the two is the
# floor that MIN_ACTION_BIAS (30, models/decision_model.py) was until this
# stage, so the rule adds no number to the fingerprint.
#
# WHAT THIS REPLACES, AND WHAT IT DOES NOT YET. Until this stage bias.raw
# was the weighted sum above against RAW_BIAS_THRESHOLD, the plan's side was
# the sum's sign, and bias.detailed was bias_label(raw, score): the same
# label with CONFIRMED past +/-30 (BiasStateMachine until finding 18,
# 27 September 2026). All three come from this function: detailed is the
# raw label, and bias_label is gone.
#
# STAGE 5, 15 November 2026: calculate_dynamic_bias is now gone too, with
# its six weights and RAW_BIAS_THRESHOLD -- see the record above. Stage 2
# kept it for its score because confidence read that score; confidence
# leaves here, so nothing reads it and this function is the only source of
# a direction in the engine.
#
# The same rule is in docs/build/measure_draft_gaps.py, draft_direction,
# which counted it on the reading of 11 November before any of this was
# built; tests/test_direction_is_the_slow_trends_side.py holds the two to
# one answer over a grid.

def _finite_or_none(value):
    """
    A finite float, or None for anything that is not one. True, False and
    text are not numbers here, though float() would take them.
    """
    if value is None or isinstance(value, (bool, str, bytes)):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if np.isfinite(number) else None


def direction_from_emas(ema50_slope, ema_20, ema_50, components=None):
    """
    The direction, from the decision candle's EMA50_Slope, EMA_20 and EMA_50.

    Returns "BULLISH", "BEARISH" or "NEUTRAL", or None when one of the three
    is not a finite number. None is "not measured", which is not NEUTRAL:
    the caller records it as a degradation and does not read it as the
    averages disagreeing.

    `components`, when a dict is passed, is filled with what was compared,
    as calculate_dynamic_bias fills its own (audit finding 7: the record is
    the comparison that ran, not a second computation of it):

        ema50_slope      "RISING", "FALLING" or "FLAT"; None if not measured
        ema20_vs_ema50   "ABOVE", "BELOW" or "EQUAL"; None if not measured
        result           what is returned

    Words and not true-or-false, because a slope that is not rising is
    either falling or flat, and only one of those can be BEARISH. The four
    numbers compared are in lineage.indicators_at_decision_bar and are not
    copied.
    """
    slope = _finite_or_none(ema50_slope)
    fast = _finite_or_none(ema_20)
    slow = _finite_or_none(ema_50)

    if slope is None:
        slope_word = None
    elif slope > 0:
        slope_word = "RISING"
    elif slope < 0:
        slope_word = "FALLING"
    else:
        slope_word = "FLAT"

    if fast is None or slow is None:
        order_word = None
    elif fast > slow:
        order_word = "ABOVE"
    elif fast < slow:
        order_word = "BELOW"
    else:
        order_word = "EQUAL"

    if slope_word is None or order_word is None:
        result = None
    elif slope_word == "RISING" and order_word == "ABOVE":
        result = "BULLISH"
    elif slope_word == "FALLING" and order_word == "BELOW":
        result = "BEARISH"
    else:
        result = "NEUTRAL"

    if components is not None:
        components["ema50_slope"] = slope_word
        components["ema20_vs_ema50"] = order_word
        components["result"] = result

    return result


def plan_side(direction):
    """
    The side the risk plan is drawn on: LONG under BULLISH, SHORT under
    BEARISH, and LONG under anything else.

    The last is a stand-in, not a side. A NEUTRAL run takes no trade and
    the panel prints no plan for it, but the engine still computes one,
    because the risk check needs a stop (Viktor's ruling of 27 September
    2026, finding 5, point 2), and a stop needs a side to be drawn on. The
    check reads only the stop's distance from price, which is the same on
    either side. Until this stage the stand-in was the sign of the weighted
    sum, with zero drawn as a long; the sum no longer says anything about
    direction, so the stand-in is fixed. Claude's choice at stage 2, Viktor's
    to reverse.
    """
    if direction == "BEARISH":
        return "SHORT"
    return "LONG"
