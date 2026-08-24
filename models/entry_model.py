import pandas as pd
import numpy as np

def calculate_entry_quality(df, zone_lower, zone_upper, macro_bias="NEUTRAL", trade_direction="LONG"):
    """
    Calculates real, quantitative sub-scores and total score for entry quality,
    fully integrated with Macro Trend Confluence and comprehensive NaN handling.
    Max points: 100
    - EMA Zone Position : 30 pts
    - ATR Distance      : 25 pts
    - VWMA Distance     : 20 pts
    - RSI Extension     : 15 pts
    - Structure         : 12 pts
    (Macro alignment acts as a multiplier/adjuster)
    """
    if df is None or df.empty:
        return {
            "score": 0.0,
            "ema_pos_pts": 0,
            "atr_dist_pts": 0,
            "vwma_pts": 0,
            "rsi_pts": 0,
            "struct_pts": 0,
            "entry_status": "NO DATA",
            "distance_from_zone": 0.0
        }

    # Validate and clean inputs
    def safe_float(value, fallback):
        """Safely extract float value with fallback."""
        try:
            if value is None or not np.isfinite(value):
                return fallback
            return float(value)
        except (ValueError, TypeError):
            return fallback

    close = safe_float(df["close"].iloc[-1] if "close" in df.columns and not df["close"].empty else None, 1.0)
    zone_lower = safe_float(zone_lower, close * 0.99)
    zone_upper = safe_float(zone_upper, close * 1.01)
    
    # Ensure zone bounds are logical
    if zone_lower > zone_upper:
        zone_lower, zone_upper = zone_upper, zone_lower
    
    # 1. EMA Zone Position Scoring (Max 30)
    zone_mid = (zone_lower + zone_upper) / 2.0
    zone_width = abs(zone_upper - zone_lower)
    
    # Fix: Prevent division by zero in zone width calculations
    if zone_width <= 1e-8 or not np.isfinite(zone_width):
        zone_width = close * 0.01  # Default to 1% of current price
    
    dist_to_mid = abs(close - zone_mid)
    
    if dist_to_mid <= zone_width:
        ema_pos_pts = 30
        entry_status = "ACTIVE ENTRY ZONE"
    elif dist_to_mid <= zone_width * 2.0:
        ema_pos_pts = 20
        entry_status = "NEAR ZONE"
    elif dist_to_mid <= zone_width * 3.5:
        ema_pos_pts = 10
        entry_status = "APPROACHING ZONE"
    else:
        ema_pos_pts = 5
        entry_status = "AWAY FROM ZONE"
        
    distance_from_zone = (dist_to_mid / close) * 100.0

    # 2. ATR Distance Scoring (Max 25) with enhanced NaN handling
    atr = safe_float(df["ATR"].iloc[-1] if "ATR" in df.columns and not df["ATR"].empty else None, close * 0.02)
    
    if atr > 0:
        try:
            atr_ratio = dist_to_mid / atr
            if np.isfinite(atr_ratio):
                # Smooth exponential decay instead of hard thresholds
                atr_dist_pts = 25 * np.exp(-atr_ratio * 0.5)
                atr_dist_pts = max(5, min(25, atr_dist_pts))  # Bounded between 5-25
            else:
                atr_dist_pts = 15
        except (ZeroDivisionError, OverflowError):
            atr_dist_pts = 15
    else:
        atr_dist_pts = 15

    # 3. VWMA Distance Scoring (Max 20) with comprehensive validation
    vwma_pts = 15  # Default score
    if "VWMA" in df.columns and not df["VWMA"].empty:
        vwma = safe_float(df["VWMA"].iloc[-1], close)
        
        if close > 0:
            try:
                vwma_diff = abs(close - vwma) / close
                if np.isfinite(vwma_diff):
                    if vwma_diff < 0.01:
                        vwma_pts = 20
                    elif vwma_diff < 0.025:
                        vwma_pts = 15
                    elif vwma_diff < 0.05:
                        vwma_pts = 10
                    else:
                        vwma_pts = 5
            except (ZeroDivisionError, OverflowError):
                vwma_pts = 15

    # 4. RSI Extension Scoring (Max 15) with validation
    rsi_pts = 10  # Default score
    if "RSI" in df.columns and not df["RSI"].empty:
        rsi = safe_float(df["RSI"].iloc[-1], 50.0)
        
        if 40 <= rsi <= 60:
            rsi_pts = 15
        elif 30 <= rsi < 40 or 60 < rsi <= 70:
            rsi_pts = 10
        else:
            rsi_pts = 5

    # 5. Structure Proximity Scoring (Max 12) with enhanced validation
    struct_pts = 6  # Default score
    if "HVN" in df.columns and not df["HVN"].empty:
        hvn = safe_float(df["HVN"].iloc[-1], close)
        
        if close > 0:
            try:
                hvn_dist = abs(close - hvn) / close
                if np.isfinite(hvn_dist):
                    if hvn_dist < 0.015:
                        struct_pts = 12
                    elif hvn_dist < 0.03:
                        struct_pts = 8
                    else:
                        struct_pts = 4
            except (ZeroDivisionError, OverflowError):
                struct_pts = 6

    base_score = float(ema_pos_pts + atr_dist_pts + vwma_pts + rsi_pts + struct_pts)

    # 6. Macro Confluence Multiplier
    macro_multiplier = 1.0
    if macro_bias == "BULLISH" and trade_direction == "LONG":
        macro_multiplier = 1.05
    elif macro_bias == "BEARISH" and trade_direction == "SHORT":
        macro_multiplier = 1.05
    elif macro_bias != "NEUTRAL" and macro_bias != trade_direction:
        macro_multiplier = 0.90

    total_score = min(100.0, base_score * macro_multiplier)

    return {
        "score": float(total_score),
        "ema_pos_pts": int(ema_pos_pts),
        "atr_dist_pts": int(atr_dist_pts),
        "vwma_pts": int(vwma_pts),
        "rsi_pts": int(rsi_pts),
        "struct_pts": int(struct_pts),
        "entry_status": entry_status,
        "distance_from_zone": float(distance_from_zone)
    }


def generate_entry_signals(
    detailed_bias,
    structure_regime,
    trend_health,
    trend_failure,
    trend_exhaustion,
    reversal_strength,
    macro_bias="NEUTRAL"
):
    """
    Generate long/short entry signals based on structural bias,
    trend health, collapse conditions, and Multi-Timeframe Confluence.
    """
    if trend_failure or trend_exhaustion or (reversal_strength and reversal_strength > 0):
        return False, False

    macro_long_allowed = macro_bias in ["BULLISH", "NEUTRAL"]
    long_signal = (
        macro_long_allowed
        and detailed_bias == "LONG"
        and structure_regime == "BULLISH STRUCTURE"
        and trend_health >= 50
    )

    macro_short_allowed = macro_bias in ["BEARISH", "NEUTRAL"]
    short_signal = (
        macro_short_allowed
        and detailed_bias == "SHORT"
        and structure_regime == "BEARISH STRUCTURE"
        and trend_health >= 50
    )

    return long_signal, short_signal
