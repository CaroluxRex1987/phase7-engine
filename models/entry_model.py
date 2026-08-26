import numpy as np
from typing import Dict, Any, Tuple, Optional

def calculate_entry_quality(
    df: Optional[Any],
    zone_lower: float,
    zone_upper: float,
    macro_bias: str = "NEUTRAL",
    trade_direction: str = "LONG",
    trend_direction: str = "NEUTRAL",
    structure_sequence: str = "NONE",
) -> Dict[str, Any]:
    """
    Calculates real, quantitative sub-scores and total score for entry quality,
    fully integrated with Macro Trend Confluence and comprehensive NaN handling.
    Max points: 100
    - EMA Zone Position : 30 pts
    - ATR Distance      : 25 pts
    - VWMA Distance     : 20 pts
    - RSI Extension     : 15 pts
    - Structure         : 12 pts
    (Macro alignment, trend direction, and structure sequence each act as a
    small multiplier/adjuster -- see section 6 below. Roadmap Layer 5: this
    was previously just the single macro multiplier; trend_direction and
    structure_sequence are new inputs, using signals that already existed
    elsewhere in the engine (trend_health.py's new trend_direction field,
    structure.py's B2 sequence detection) but weren't yet factored into
    entry quality itself.)
    """
    default_response = {
        "score": 0.0,
        "ema_pos_pts": 0,
        "atr_dist_pts": 0,
        "vwma_pts": 0,
        "rsi_pts": 0,
        "struct_pts": 0,
        "entry_status": "NO DATA",
        "distance_from_zone": 0.0
    }

    if df is None or getattr(df, "empty", True):
        return default_response

    # Validate and clean inputs
    def safe_float(value: Any, fallback: float) -> float:
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

    # ============================================================
    # 1. EMA ZONE POSITION SCORING (Max 30)
    # ============================================================
    zone_mid = (zone_lower + zone_upper) / 2.0
    zone_width = abs(zone_upper - zone_lower)

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

    distance_from_zone = float((dist_to_mid / close) * 100.0)

    # ============================================================
    # 2. ATR DISTANCE SCORING (Max 25)
    # ============================================================
    atr = safe_float(df["ATR"].iloc[-1] if "ATR" in df.columns and not df["ATR"].empty else None, close * 0.02)

    if atr > 0:
        try:
            atr_ratio = dist_to_mid / atr
            if np.isfinite(atr_ratio):
                # Smooth exponential decay instead of hard thresholds
                atr_dist_pts = float(25 * np.exp(-atr_ratio * 0.5))
                atr_dist_pts = max(5.0, min(25.0, atr_dist_pts))  # Bounded between 5-25
            else:
                atr_dist_pts = 15.0
        except (ZeroDivisionError, OverflowError):
            atr_dist_pts = 15.0
    else:
        atr_dist_pts = 15.0

    # ============================================================
    # 3. VWMA DISTANCE SCORING (Max 20)
    # ============================================================
    vwma_pts = 15.0  # Default score
    if "VWMA" in df.columns and not df["VWMA"].empty:
        vwma = safe_float(df["VWMA"].iloc[-1], close)

        if close > 0:
            try:
                vwma_diff = abs(close - vwma) / close
                if np.isfinite(vwma_diff):
                    if vwma_diff < 0.01:
                        vwma_pts = 20.0
                    elif vwma_diff < 0.025:
                        vwma_pts = 15.0
                    elif vwma_diff < 0.05:
                        vwma_pts = 10.0
                    else:
                        vwma_pts = 5.0
            except (ZeroDivisionError, OverflowError):
                vwma_pts = 15.0

    # ============================================================
    # 4. RSI EXTENSION SCORING (Max 15)
    # ============================================================
    rsi_pts = 10.0  # Default score
    if "RSI" in df.columns and not df["RSI"].empty:
        rsi = safe_float(df["RSI"].iloc[-1], 50.0)

        if 40.0 <= rsi <= 60.0:
            rsi_pts = 15.0
        elif 30.0 <= rsi < 40.0 or 60.0 < rsi <= 70.0:
            rsi_pts = 10.0
        else:
            rsi_pts = 5.0

    # ============================================================
    # 5. STRUCTURE PROXIMITY SCORING (Max 12)
    # ============================================================
    struct_pts = 6.0  # Default score
    if "HVN" in df.columns and not df["HVN"].empty:
        hvn = safe_float(df["HVN"].iloc[-1], close)

        if close > 0:
            try:
                hvn_dist = abs(close - hvn) / close
                if np.isfinite(hvn_dist):
                    if hvn_dist < 0.015:
                        struct_pts = 12.0
                    elif hvn_dist < 0.03:
                        struct_pts = 8.0
                    else:
                        struct_pts = 4.0
            except (ZeroDivisionError, OverflowError):
                struct_pts = 6.0

    base_score = float(ema_pos_pts + atr_dist_pts + vwma_pts + rsi_pts + struct_pts)

    # ============================================================
    # 6. CONFLUENCE MULTIPLIERS & FINAL BOUNDS (Roadmap Layer 5)
    # ============================================================
    # Each multiplier is independently small (+-5-10%) and only nudges the
    # score -- none of them can gate a trade on their own (generate_entry_signals
    # already handles hard gating). Combined, they let entry quality reflect
    # not just "is price near a good zone" but "does the broader context this
    # trade would be entering into actually support this specific direction."
    macro_multiplier = 1.0
    if macro_bias == "BULLISH" and trade_direction == "LONG":
        macro_multiplier = 1.05
    elif macro_bias == "BEARISH" and trade_direction == "SHORT":
        macro_multiplier = 1.05
    elif macro_bias not in ["NEUTRAL", ""] and macro_bias != trade_direction:
        macro_multiplier = 0.90

    # Trend direction alignment: trend_health.py's EMA-slope-based direction
    # label agreeing (or disagreeing) with the direction being scored here.
    trend_multiplier = 1.0
    if trade_direction == "LONG":
        if trend_direction == "BULLISH":
            trend_multiplier = 1.05
        elif trend_direction == "BEARISH":
            trend_multiplier = 0.90
    elif trade_direction == "SHORT":
        if trend_direction == "BEARISH":
            trend_multiplier = 1.05
        elif trend_direction == "BULLISH":
            trend_multiplier = 0.90

    # Structure sequence alignment: a BOS (continuation) in this trade's own
    # direction is rewarded; a CHOCH (possible reversal) against this trade's
    # direction is penalized. An established (non-BOS) swing sequence in this
    # trade's direction, or "NONE"/anything else, is left neutral -- BOS is a
    # stronger continuation signal than a plain swing sequence, so only BOS
    # earns the reward tier here.
    structure_multiplier = 1.0
    if trade_direction == "LONG":
        if structure_sequence == "BOS BULLISH (TREND CONTINUATION)":
            structure_multiplier = 1.05
        elif structure_sequence == "CHOCH BEARISH (POSSIBLE REVERSAL)":
            structure_multiplier = 0.90
    elif trade_direction == "SHORT":
        if structure_sequence == "BOS BEARISH (TREND CONTINUATION)":
            structure_multiplier = 1.05
        elif structure_sequence == "CHOCH BULLISH (POSSIBLE REVERSAL)":
            structure_multiplier = 0.90

    combined_multiplier = macro_multiplier * trend_multiplier * structure_multiplier
    total_score = float(min(100.0, max(0.0, base_score * combined_multiplier)))

    return {
        "score": float(total_score),
        "ema_pos_pts": int(ema_pos_pts),
        "atr_dist_pts": int(round(atr_dist_pts)),
        "vwma_pts": int(vwma_pts),
        "rsi_pts": int(rsi_pts),
        "struct_pts": int(struct_pts),
        "entry_status": str(entry_status),
        "distance_from_zone": float(distance_from_zone)
    }


def generate_entry_signals(
    detailed_bias: str,
    structure_regime: str,
    trend_health: float,
    trend_failure: bool,
    trend_exhaustion: bool,
    reversal_strength: float,
    macro_bias: str = "NEUTRAL"
) -> Tuple[bool, bool]:
    """
    Generate long/short entry signals based on structural bias,
    trend health, collapse conditions, and Multi-Timeframe Confluence.
    """
    if trend_failure or trend_exhaustion or (reversal_strength is not None and reversal_strength > 0):
        return False, False

    # A1 FIX: structure.py only ever emits "BULLISH TREND" / "BEARISH TREND"
    # (see _detect_regime() in structure.py) — "BULLISH STRUCTURE" /
    # "BEARISH STRUCTURE" were never produced by anything, so these gates
    # could never pass. Corrected to match the real emitted strings.
    #
    # A2 FIX: BiasStateMachine only ever emits "BULLISH CONFIRMED" /
    # "BEARISH CONFIRMED" / "NEUTRAL" (see bias_engine.py) — "LONG" / "SHORT"
    # were never produced either, a second independent dead gate. Corrected
    # to match. Note: this gate still won't fire in practice until B1 (the
    # continuation/reversal engine in trend_health.py) exists, since raw_bias
    # is currently pinned to NEUTRAL upstream — that's expected and by design,
    # not a bug in this file.
    macro_long_allowed = macro_bias in ["BULLISH", "NEUTRAL"]
    long_signal = bool(
        macro_long_allowed
        and detailed_bias == "BULLISH CONFIRMED"
        and structure_regime == "BULLISH TREND"
        and trend_health >= 50.0
    )

    macro_short_allowed = macro_bias in ["BEARISH", "NEUTRAL"]
    short_signal = bool(
        macro_short_allowed
        and detailed_bias == "BEARISH CONFIRMED"
        and structure_regime == "BEARISH TREND"
        and trend_health >= 50.0
    )

    return long_signal, short_signal