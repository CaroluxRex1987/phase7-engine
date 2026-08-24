import pandas as pd

# ============================================================
# DYNAMIC BIAS ENGINE
# ============================================================

def calculate_dynamic_bias(
    df,
    trend_sequence,
    trend_health,
    trend_failure,
    trend_exhaustion,
    reversal_direction,
    reversal_strength,
    continuation_strength,
):
    """
    Returns:
        raw_bias (str)
        bias_score (float)
    """

    # Normalize None values to safe defaults
    trend_health = trend_health if trend_health is not None else 0.0
    trend_failure = trend_failure if trend_failure is not None else 0.0
    trend_exhaustion = trend_exhaustion if trend_exhaustion is not None else 0.0
    reversal_strength = reversal_strength if reversal_strength is not None else 0.0
    continuation_strength = continuation_strength if continuation_strength is not None else 0.0

    # Basic bias logic
    if trend_health > 0.6 and continuation_strength > 0:
        raw_bias = "BULLISH"
    elif trend_health < -0.6 and continuation_strength < 0:
        raw_bias = "BEARISH"
    else:
        raw_bias = "NEUTRAL"

    # Score calculation with normalization and bounds checking
    # Fix: Ensure all inputs are finite and normalize to prevent scale issues
    trend_component = np.clip(trend_health, -100, 100) * 0.5
    continuation_component = np.clip(continuation_strength, -50, 50) * 0.3
    failure_component = np.clip(trend_failure, 0, 10) * -0.2
    reversal_component = np.clip(reversal_strength, -20, 20) * 0.1
    
    bias_score = float(
        trend_component +
        continuation_component +
        failure_component +
        reversal_component
    )
    
    # Final bounds check to prevent extreme values
    bias_score = np.clip(bias_score, -100, 100)

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

    # Volatility detection
    if "ATR" in df.columns:
        atr = df["ATR"].iloc[-1]
        price = df["close"].iloc[-1]

        vol_ratio = atr / price if price != 0 else 0

        if vol_ratio > 0.02:
            volatility_mode = "HIGH VOLATILITY"
        elif vol_ratio > 0.01:
            volatility_mode = "MEDIUM VOLATILITY"
        else:
            volatility_mode = "LOW VOLATILITY"
    else:
        volatility_mode = "UNKNOWN"

    # Regime detection
    if "STRUCTURE_REGIME" in df.columns:
        dynamic_regime = df["STRUCTURE_REGIME"].iloc[-1]
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

        if raw_bias == "BULLISH" and bias_score > 0.3:
            self.state = "BULLISH CONFIRMED"
        elif raw_bias == "BEARISH" and bias_score < -0.3:
            self.state = "BEARISH CONFIRMED"
        elif abs(bias_score) < 0.2:
            self.state = "NEUTRAL"
        else:
            self.state = raw_bias

        return self.state
