import pandas as pd
import numpy as np

def compute_trend_health(df: pd.DataFrame):
    """
    Compute advanced trend health, slope, acceleration, failure, 
    exhaustion, momentum divergence, and trend regime classification.
    """
    if df is None or df.empty or len(df) < 20:
        return {
            "trend_health": 50.0,
            "trend_failure": False,
            "trend_exhaustion": False,
            "momentum_mode": "NEUTRAL",
            "trend_slope": 0.0,
            "trend_acceleration": 0.0,
            "momentum_divergence": False,
            "trend_regime": "NEUTRAL"
        }

    # Extract required values safely
        # Extract required values safely
    ema20_slope = df["EMA20_Slope"].iloc[-1] if "EMA20_Slope" in df.columns else 0.0
    ema50_slope = df["EMA50_Slope"].iloc[-1] if "EMA50_Slope" in df.columns else 0.0
    adx_val = df["ADX"].iloc[-1] if "ADX" in df.columns else 25.0
    rsi_val = df["RSI"].iloc[-1] if "RSI" in df.columns else 50.0

    # ============================================================
    # 1. TREND SLOPE & ACCELERATION
    # ============================================================
    trend_slope = float((ema20_slope + ema50_slope) / 2.0)
    
    # Calculate acceleration (change in slope over the last 3 periods)
    if "EMA20_Slope" in df.columns and len(df) >= 4:
        prev_slope = df["EMA20_Slope"].iloc[-4]
        trend_acceleration = float(ema20_slope - prev_slope)
    else:
        trend_acceleration = 0.0

    # ============================================================
    # 2. TREND HEALTH SCORE (0–100)
    # ============================================================
    slope_strength = min(abs(trend_slope) * 400, 45)
    adx_strength = min(adx_val * 1.2, 40)
    
    if 50 <= rsi_val <= 70:
        rsi_strength = 15
    elif 30 <= rsi_val <= 50:
        rsi_strength = 10
    else:
        rsi_strength = 5

    trend_health = float(slope_strength + adx_strength + rsi_strength)
    trend_health = max(0.0, min(100.0, trend_health))

    # ============================================================
    # 3. TREND FAILURE
    # ============================================================
    trend_failure = False
    if "STRUCTURE" in df.columns:
        recent_struct = df["STRUCTURE"].iloc[-5:]
        trend_failure = (
            (recent_struct == "LH").sum() > 0 or
            (recent_struct == "LL").sum() > 0
        )

    # ============================================================
    # 4. TREND EXHAUSTION
    # ============================================================
    range_val = df["high"].iloc[-1] - df["low"].iloc[-1]
    range_prev = df["high"].iloc[-2] - df["low"].iloc[-2]
    range_expanding = range_val > range_prev
    weak_adx = adx_val < 20

    trend_exhaustion = bool(range_expanding and weak_adx or (trend_health < 35 and adx_val < 15))

    # ============================================================
    # 5. MOMENTUM DIVERGENCE DETECTION
    # ============================================================
    momentum_divergence = False
    if len(df) >= 10 and "RSI" in df.columns:
        price_higher_high = df["close"].iloc[-1] > df["close"].iloc[-5]
        rsi_lower_high = df["RSI"].iloc[-1] < df["RSI"].iloc[-5]
        
        price_lower_low = df["close"].iloc[-1] < df["close"].iloc[-5]
        rsi_higher_low = df["RSI"].iloc[-1] > df["RSI"].iloc[-5]
        
        if (price_higher_high and rsi_lower_high) or (price_lower_low and rsi_higher_low):
            momentum_divergence = True

    # ============================================================
    # 6. MOMENTUM MODE & REGIME CLASSIFICATION
    # ============================================================
    if rsi_val < 40:
        momentum_mode = "BUILDING"
    elif rsi_val < 55:
        momentum_mode = "HEALTHY"
    elif rsi_val < 70:
        momentum_mode = "STRONG"
    elif rsi_val < 80:
        momentum_mode = "EXTENDED"
    else:
        momentum_mode = "EXTREME"

    if trend_health >= 75 and adx_val >= 25:
        trend_regime = "STRONG TREND"
    elif trend_acceleration > 0 and trend_health >= 50:
        trend_regime = "ACCELERATING"
    elif momentum_divergence or trend_exhaustion:
        trend_regime = "EXHAUSTING / DIVERGENT"
    elif adx_val < 20:
        trend_regime = "MEAN REVERTING / CHOP"
    else:
        trend_regime = "MODERATE TREND"

    # ============================================================
    # RETURN STRUCTURE
    # ============================================================
    return {
        "trend_health": trend_health,
        "trend_failure": trend_failure,
        "trend_exhaustion": trend_exhaustion,
        "momentum_mode": momentum_mode,
        "trend_slope": trend_slope,
        "trend_acceleration": trend_acceleration,
        "momentum_divergence": momentum_divergence,
        "trend_regime": trend_regime
    }