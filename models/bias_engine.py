import numpy as np

# ============================================================
# DYNAMIC BIAS ENGINE (Roadmap Layer 2: multi-factor weighted blend)
# ============================================================
#
# Previously bias_score was built from only two real inputs (trend health
# + continuation/reversal from B1). The roadmap specifies six weighted
# factors -- structure regime, volume sentiment, and SuperTrend direction
# were never wired in at all, even though engine_core.py already has all
# of them available at the point it calls this function. Each factor is
# scored on a consistent -100..+100 scale and combined as a straight
# weighted sum (weights below sum to 1.00), so the -100..100 bias_score
# contract everything downstream relies on (DecisionModel, entry_model,
# BiasStateMachine) is unchanged.
#
# ITEM 11 RE-AUDIT (Finding 4), dependency graph, made explicit rather than
# left to be reconstructed. Six factors are combined below, and each is
# meant to be genuinely independent of the other five:
#
#   trend health (0.30)        <- indicators/trend_health.py's slope/ADX/RSI
#                                  blend, unsigned magnitude
#   structure regime (0.20)    <- structure.py's swing-based regime label
#   volume sentiment (0.15)    <- structure.py's volume/price divergence read
#   supertrend direction (0.15)<- indicators.py's SuperTrend column, sign only
#   macro bias (0.10)          <- engine_core.py's higher-timeframe EMA read
#   reversal/continuation(0.10)<- trend_health.py's continuation_strength
#                                  (ADX + RSI-momentum + acceleration only --
#                                  it no longer includes a trend-health-
#                                  derived term; see trend_health.py's
#                                  "ITEM 11 RE-AUDIT" comment for why that
#                                  was itself a duplicate of the first factor)
#
# This is where the auditor's finding 4 example lived: reversal_continuation_
# score used to be built in part from trend_health's own value, so trend
# health reached bias_score through two of the six weights, not one. That is
# fixed at the source (trend_health.py), not here, because continuation_
# strength has exactly one consumer -- this function -- so the source is
# where the independence actually needs to be true.
#
# What this function does NOT try to do: re-derive or cross-check any factor
# against another. structure_regime, macro_bias and volume_sentiment are also
# read downstream by models/decision_model.py's confidence calculation and by
# engine_core.py's validation score -- Item 11's other broken path, fixed
# there by removing the second and third readings rather than by disagreeing
# with this one. bias_score is the one place these six factors are weighed;
# every other consumer reports what bias_score already concluded rather than
# re-weighing the same inputs.

WEIGHT_TREND_HEALTH = 0.30
WEIGHT_STRUCTURE_REGIME = 0.20
WEIGHT_VOLUME_SENTIMENT = 0.15
WEIGHT_SUPERTREND_DIRECTION = 0.15
WEIGHT_MACRO_BIAS = 0.10
WEIGHT_REVERSAL_CONTINUATION = 0.10

# raw_bias is now derived directly from the composite bias_score itself
# (previously raw_bias and bias_score came from partially different
# logic/inputs, which was architecturally inconsistent with a "multi-factor
# blend" -- now both come from the same one computation).
RAW_BIAS_THRESHOLD = 20.0

# Volume sentiment strings (see structure.py's _volume_sentiment_simple)
# mapped to a signed -100..100 scale.
_VOLUME_SENTIMENT_SCORES = {
    "STRONG BULLISH ACCUMULATION": 100.0,
    "BULLISH VOLUME SUPPORT": 50.0,
    "STRONG BEARISH DISTRIBUTION": -100.0,
    "BEARISH VOLUME PRESSURE": -50.0,
    # Divergence/exhaustion are warning states, not directional votes --
    # scored neutral here; they already reduce confidence elsewhere
    # (trend_exhaustion feeds reversal detection in trend_health.py).
    "VOLUME DIVERGENCE": 0.0,
    "VOLUME EXHAUSTION": 0.0,
    "NEUTRAL VOLUME": 0.0,
}


def calculate_dynamic_bias(
    trend_sequence,
    trend_health,
    trend_exhaustion,
    reversal_direction,
    reversal_strength,
    continuation_strength,
    structure_regime="NEUTRAL STRUCTURE",
    volume_sentiment="NEUTRAL VOLUME",
    supertrend_direction=0.0,
    macro_bias="NEUTRAL",
    components=None,
):
    """
    Returns:
        raw_bias (str)
        bias_score (float, -100..100)

    AUDIT FINDING 7 (Item 6, Traceability): `components`, when a dict is
    passed, is filled with each factor's input, score, weight and
    contribution, plus the discount and the clip. It is an out-parameter
    rather than a third return value for one reason and it is not style:
    the alternative was a second function that recomputes the breakdown,
    and a second implementation of a number is exactly the shape this
    engine keeps finding defects in -- two places computing one thing,
    drifting apart quietly. What is recorded here is the arithmetic that
    actually ran, not a reconstruction of it, so it cannot disagree with
    the score it explains.

    Passing nothing changes nothing. Every existing caller is unaffected
    and the function still returns exactly two values.

    SEQUENCE ITEM 6: this function used to take `df` as its first parameter.

    It never read a value out of it. Every factor in the score below comes from
    the scalar arguments — trend health, structure regime, volume sentiment,
    SuperTrend direction, macro bias. The frame's entire role was this, at the
    top of the body:

        critical_cols = ["close", "EMA_20", "EMA_50", "RSI"]
        for col in critical_cols:
            if col in df.columns and df[col].isna().any():
                if col == "close":
                    df[col] = df[col].ffill().bfill()
                else:
                    df[col] = df[col].fillna(df["close"])

    A write-only parameter: it filled NaNs in four columns of the caller's
    frame, three of which this function does not read, and then computed the
    bias from arguments that have nothing to do with any of them. Whatever it
    repaired, it repaired for somebody else, silently, as a side effect of
    being asked an unrelated question. That is the T2-1 violation the Step 5
    plan names by this function's name.

    Because it was write-only, the fix is deletion rather than "operate on a
    copy" — copying would have preserved a computation whose only output was
    the mutation, turning it into a genuine no-op.

    NOT FIXED HERE, AND DELIBERATELY: the fallback above is also a fabrication
    path, and the RSI branch is the worst kind. RSI is a 0-100 oscillator and
    `df["close"]` is a price, so a missing RSI was replaced by whatever the
    asset happened to cost — about 0.80 for AERO, which reads as maximally
    oversold, and five figures for BTC, which is off the scale entirely. It
    could not fire on clean data (add_technical_indicators cleans RSI with a
    fallback of 50.0 before this is reached), so it is latent rather than live.
    Recorded as a rider on sequence item 9, where the fabricated fallbacks are
    given honest semantics. Item 6's job is to stop the writes reaching a frame
    this function does not own; making the fallbacks honest is item 9's.
    """

    # Comprehensive input validation and NaN handling
    def safe_float(value, default=0.0):
        """Safely convert value to float, handling None and NaN."""
        if value is None:
            return default
        try:
            float_val = float(value)
            return float_val if np.isfinite(float_val) else default
        except (ValueError, TypeError):
            return default

    trend_health = safe_float(trend_health, 0.0)
    trend_exhaustion = bool(trend_exhaustion)
    reversal_strength = safe_float(reversal_strength, 0.0)
    continuation_strength = safe_float(continuation_strength, 0.0)
    supertrend_direction = safe_float(supertrend_direction, 0.0)
    reversal_direction = reversal_direction if reversal_direction in ("BULLISH", "BEARISH") else "NONE"
    structure_regime = str(structure_regime) if structure_regime else "NEUTRAL STRUCTURE"
    volume_sentiment = str(volume_sentiment) if volume_sentiment else "NEUTRAL VOLUME"
    macro_bias = str(macro_bias).upper() if macro_bias else "NEUTRAL"
    trend_sequence = str(trend_sequence) if trend_sequence else "NONE"

    # SEQUENCE ITEM 6: the caller-frame cleaning block was here. See the
    # docstring above for what it did and why deleting it was the fix.

    # Trend direction proxy: continuation_strength's sign is B1's dedicated
    # signed-direction signal, so it's used here to sign trend_health (an
    # unsigned magnitude on its own -- see A4's original fix).
    trend_direction = 1 if continuation_strength > 0 else (-1 if continuation_strength < 0 else 0)

    # ============================================================
    # FACTOR 1: TREND HEALTH (30%)
    # ============================================================
    signed_trend_health = trend_direction * np.clip(trend_health, 0, 100)

    # ============================================================
    # FACTOR 2: STRUCTURE REGIME (20%)
    # ============================================================
    if structure_regime == "BULLISH TREND":
        structure_score = 100.0
    elif structure_regime == "BEARISH TREND":
        structure_score = -100.0
    else:
        structure_score = 0.0

    # ============================================================
    # FACTOR 3: VOLUME SENTIMENT (15%)
    # ============================================================
    volume_score = _VOLUME_SENTIMENT_SCORES.get(volume_sentiment.upper(), 0.0)

    # ============================================================
    # FACTOR 4: SUPERTREND DIRECTION (15%)
    # ============================================================
    if supertrend_direction > 0:
        supertrend_score = 100.0
    elif supertrend_direction < 0:
        supertrend_score = -100.0
    else:
        supertrend_score = 0.0

    # ============================================================
    # FACTOR 5: MACRO BIAS (10%)
    # ============================================================
    if macro_bias == "BULLISH":
        macro_score = 100.0
    elif macro_bias == "BEARISH":
        macro_score = -100.0
    else:
        macro_score = 0.0

    # ============================================================
    # FACTOR 6: REVERSAL / CONTINUATION (10%, combined single factor)
    # continuation_strength is the base signal; a reversal signal that
    # actively OPPOSES the current trend direction proportionally
    # discounts it (never fully zeroes it -- floored at 20% of its
    # original value), rather than being a separate 7th factor.
    # ============================================================
    reversal_signed_direction = 1 if reversal_direction == "BULLISH" else (-1 if reversal_direction == "BEARISH" else 0)
    if trend_direction != 0 and reversal_signed_direction != 0 and reversal_signed_direction != trend_direction:
        discount = max(0.2, 1.0 - (np.clip(reversal_strength, 0, 100) / 100.0))
        reversal_continuation_score = continuation_strength * discount
    else:
        reversal_continuation_score = continuation_strength

    # ============================================================
    # WEIGHTED BLEND
    # ============================================================
    bias_score = (
        signed_trend_health * WEIGHT_TREND_HEALTH +
        structure_score * WEIGHT_STRUCTURE_REGIME +
        volume_score * WEIGHT_VOLUME_SENTIMENT +
        supertrend_score * WEIGHT_SUPERTREND_DIRECTION +
        macro_score * WEIGHT_MACRO_BIAS +
        reversal_continuation_score * WEIGHT_REVERSAL_CONTINUATION
    )

    # AUDIT FINDING 7: the six factors as they were actually weighed.
    # Recorded here rather than after the clip below, because these are
    # the inputs to the blend -- what the clip and the discount then do
    # to their sum is recorded separately, so a reader can see both the
    # parts and what happened to the whole.
    if components is not None:
        components["factors"] = {
            "trend_health": {
                "input": float(trend_health), "signed": float(signed_trend_health),
                "weight": WEIGHT_TREND_HEALTH,
                "contribution": float(signed_trend_health * WEIGHT_TREND_HEALTH)},
            "structure_regime": {
                "input": structure_regime, "signed": float(structure_score),
                "weight": WEIGHT_STRUCTURE_REGIME,
                "contribution": float(structure_score * WEIGHT_STRUCTURE_REGIME)},
            "volume_sentiment": {
                "input": volume_sentiment, "signed": float(volume_score),
                "weight": WEIGHT_VOLUME_SENTIMENT,
                "contribution": float(volume_score * WEIGHT_VOLUME_SENTIMENT)},
            "supertrend_direction": {
                "input": float(supertrend_direction), "signed": float(supertrend_score),
                "weight": WEIGHT_SUPERTREND_DIRECTION,
                "contribution": float(supertrend_score * WEIGHT_SUPERTREND_DIRECTION)},
            "macro_bias": {
                "input": macro_bias, "signed": float(macro_score),
                "weight": WEIGHT_MACRO_BIAS,
                "contribution": float(macro_score * WEIGHT_MACRO_BIAS)},
            "reversal_continuation": {
                "input": float(continuation_strength),
                "signed": float(reversal_continuation_score),
                "weight": WEIGHT_REVERSAL_CONTINUATION,
                "contribution": float(
                    reversal_continuation_score * WEIGHT_REVERSAL_CONTINUATION)},
        }
        components["weighted_sum"] = float(bias_score)
        components["trend_direction"] = int(trend_direction)
        components["reversal_direction"] = reversal_direction
        components["reversal_strength"] = float(reversal_strength)

    # B2 FIX: trend_sequence was accepted as a parameter here but never
    # actually used anywhere in this function -- structure.py's
    # _detect_sequence() was a stub that always returned "NONE", so there
    # was nothing real to use yet. Now that B2 has built real BOS/CHOCH
    # detection, a CHOCH ("change of character") AGAINST the current trend
    # direction is a genuine structural warning sign -- price just broke
    # the last confirmed swing extreme against the established sequence,
    # which is the same kind of warning trend_failure already represents.
    # Rather than adding a 7th weighted factor (which would mean
    # re-deriving and re-testing all six existing weights), it's folded
    # into the same discount as trend_failure below.
    choch_against_trend = (
        (trend_direction > 0 and "CHOCH BEARISH" in trend_sequence) or
        (trend_direction < 0 and "CHOCH BULLISH" in trend_sequence)
    )

    # A CHOCH against the current direction is "the structure just
    # contradicted this bias", so it discounts the WHOLE blend rather than
    # getting its own weight slot among the six factors.
    #
    # SEQUENCE ITEM 9c: this condition was `trend_failure or
    # choch_against_trend`, and the comment described them as two signals
    # sharing one discount. There was only ever one. trend_failure could not
    # become True — see the note in trend_health.py — so every discount this
    # line has ever applied came from the CHOCH.
    if choch_against_trend:
        bias_score *= 0.5

    if components is not None:
        components["choch_against_trend"] = bool(choch_against_trend)
        components["trend_sequence"] = trend_sequence
        components["after_discount"] = float(bias_score)

    bias_score = float(np.clip(bias_score, -100, 100))

    if components is not None:
        components["clipped"] = bool(components["after_discount"] != bias_score)
        components["bias_score"] = float(bias_score)
        components["raw_bias_threshold"] = RAW_BIAS_THRESHOLD

    # raw_bias now comes directly from the same composite score, instead
    # of a separate trend_health-only gate -- one computation drives both.
    if bias_score > RAW_BIAS_THRESHOLD:
        raw_bias = "BULLISH"
    elif bias_score < -RAW_BIAS_THRESHOLD:
        raw_bias = "BEARISH"
    else:
        raw_bias = "NEUTRAL"

    return raw_bias, bias_score


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
            vol_ratio = 0.01  # Default to medium volatility

        # BUG FIX (found while cross-checking Option A's "volatility modes
        # are consistent" point): risk_model.py has a real "EXTREME
        # VOLATILITY" tier (widest stops, halved position sizing,
        # automatic EXTREME RISK classification) but this function -- the
        # only place volatility_state is ever produced -- topped out at
        # "HIGH VOLATILITY" and could never emit "EXTREME VOLATILITY".
        # That entire risk tier was dead code. Added the missing tier.
        if vol_ratio > 0.04:
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
        dynamic_regime = "NEUTRAL STRUCTURE"

    return dynamic_regime, volatility_mode


# ============================================================
# BIAS STATE MACHINE
# ============================================================

class BiasStateMachine:
    def __init__(self):
        self.state = "NEUTRAL"

    def transition(self, raw_bias, bias_score):
        """
        Returns a stable bias state.
        """

        # Normalize None values
        bias_score = bias_score if bias_score is not None else 0.0

        # Thresholds match bias_score's real -100..100 scale (A5 fix).
        if raw_bias == "BULLISH" and bias_score > 30:
            self.state = "BULLISH CONFIRMED"
        elif raw_bias == "BEARISH" and bias_score < -30:
            self.state = "BEARISH CONFIRMED"
        elif abs(bias_score) < 20:
            self.state = "NEUTRAL"
        else:
            self.state = raw_bias

        return self.state