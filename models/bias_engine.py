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
    df,
    trend_sequence,
    trend_health,
    trend_failure,
    trend_exhaustion,
    reversal_direction,
    reversal_strength,
    continuation_strength,
    structure_regime="NEUTRAL STRUCTURE",
    volume_sentiment="NEUTRAL VOLUME",
    supertrend_direction=0.0,
    macro_bias="NEUTRAL",
):
    """
    Returns:
        raw_bias (str)
        bias_score (float, -100..100)
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
    trend_failure = bool(trend_failure)
    trend_exhaustion = bool(trend_exhaustion)
    reversal_strength = safe_float(reversal_strength, 0.0)
    continuation_strength = safe_float(continuation_strength, 0.0)
    supertrend_direction = safe_float(supertrend_direction, 0.0)
    reversal_direction = reversal_direction if reversal_direction in ("BULLISH", "BEARISH") else "NONE"
    structure_regime = str(structure_regime) if structure_regime else "NEUTRAL STRUCTURE"
    volume_sentiment = str(volume_sentiment) if volume_sentiment else "NEUTRAL VOLUME"
    macro_bias = str(macro_bias).upper() if macro_bias else "NEUTRAL"
    trend_sequence = str(trend_sequence) if trend_sequence else "NONE"

    # Validate DataFrame inputs
    if df is not None and not df.empty:
        # Check for critical indicators and clean them if needed
        critical_cols = ["close", "EMA_20", "EMA_50", "RSI"]
        for col in critical_cols:
            if col in df.columns and df[col].isna().any():
                if col == "close":
                    # Forward fill close prices
                    df[col] = df[col].ffill().bfill()
                else:
                    # For indicators, use close price as fallback
                    df[col] = df[col].fillna(df["close"])

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

    # trend_failure isn't one of the six weighted factors -- it's a
    # structural warning sign (recent lower-high/lower-low), so it
    # discounts the WHOLE blend rather than getting its own weight slot.
    # A CHOCH against the current direction gets the same treatment --
    # both are "the structure just contradicted this bias" signals, so
    # they share one discount rather than compounding into a double
    # penalty when they fire together.
    if trend_failure or choch_against_trend:
        bias_score *= 0.5

    bias_score = float(np.clip(bias_score, -100, 100))

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