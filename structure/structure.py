import numpy as np

class StructureEngine:
    """
    Phase‑7 Structure + Volume Sentiment Engine (Simple Mode)
    """

    def __init__(self):
        pass

    # ============================================================
    # MAIN STRUCTURE + VOLUME SENTIMENT ENGINE
    # ============================================================

    def analyze(self, df, current_price):
        """
        Main structure engine entry point.
        Returns structure regime, sequence, HVN/LVN, swing structure,
        and NEW volume sentiment (Simple Mode).
        """

        regime = self._detect_regime(df)
        sequence = self._detect_sequence(df)
        hvn, lvn = self._detect_hvn_lvn(df)
        swing_struct = self._detect_swing_structure(df, current_price)

        # NEW: Volume Sentiment (Simple Mode)
        volume_sentiment = self._volume_sentiment_simple(df)

        return {
            "regime": regime,
            "sequence": sequence,
            "hvn": hvn,
            "lvn": lvn,
            "swing_struct": swing_struct,
            "volume_sentiment": volume_sentiment
        }

    # ============================================================
    # BASIC STRUCTURE DETECTION
    # ============================================================

    def _detect_regime(self, df):
        return "NEUTRAL STRUCTURE"

    def _detect_sequence(self, df):
        return "NONE"

    def _detect_hvn_lvn(self, df):
        # Optimized HVN/LVN detection using numpy for better performance
        if df is not None and not df.empty:
            # Use numpy operations directly on values for speed
            high_values = df['high'].values
            low_values = df['low'].values
            
            # Use numpy functions which are faster than pandas
            hvn = np.max(high_values)
            lvn = np.min(low_values)
            return hvn, lvn
        return 0.0, 0.0

    def _detect_swing_structure(self, df, current_price):
        return current_price

    # ============================================================
    # SIMPLE VOLUME SENTIMENT ENGINE (STYLE A)
    # ============================================================

    def _volume_sentiment_simple(self, df):
        """
        Simple & Clean Volume Sentiment Classification.
        Uses VWMA slope + volume trend vs price trend.
        Optimized for performance with vectorized operations.
        """

        if df is None or len(df) < 20:
            return "NEUTRAL VOLUME"

        # Use numpy arrays directly for better performance
        closes = df["close"].iloc[-10:].values  # Only get what we need
        volumes = df["volume"].iloc[-10:].values

        # Optimized VWMA calculation using numpy
        try:
            vwma_recent = np.average(closes[-5:], weights=volumes[-5:])
            vwma_prev = np.average(closes[-10:-5], weights=volumes[-10:-5])
        except ZeroDivisionError:
            # Handle case where all volumes are zero
            vwma_recent = np.mean(closes[-5:])
            vwma_prev = np.mean(closes[-10:-5])

        vwma_slope = vwma_recent - vwma_prev

        # Vectorized trend calculations
        price_slope = closes[-1] - closes[-5]
        vol_slope = volumes[-1] - volumes[-5]

        # --------------------------------------------------------
        # CLASSIFICATION LOGIC (Simple Mode)
        # --------------------------------------------------------

        # Bullish Volume Support
        if vwma_slope > 0 and vol_slope > 0 and price_slope > 0:
            return "BULLISH VOLUME SUPPORT"

        # Bearish Volume Pressure
        if vwma_slope < 0 and vol_slope > 0 and price_slope < 0:
            return "BEARISH VOLUME PRESSURE"

        # Volume Divergence
        if price_slope > 0 and vol_slope < 0:
            return "VOLUME DIVERGENCE"

        if price_slope < 0 and vol_slope > 0:
            return "VOLUME DIVERGENCE"

        # Volume Exhaustion (volume spike + flat price)
        if vol_slope > 0 and abs(price_slope) < (0.002 * closes[-1]):
            return "VOLUME EXHAUSTION"

        # Default
        return "NEUTRAL VOLUME"


# ============================================================
# ENGINE COMPATIBILITY WRAPPER
# ============================================================

def calculate_structure(df, lookback=8, copy_df=True):
    """
    Compatibility wrapper function expected by engine_core.py.
    Provides structural analysis and injects required DataFrame columns
    (including 'STRUCTURE', 'HVN', and 'LVN') to support downstream modules.
    
    Args:
        df: Input DataFrame
        lookback: Lookback period for structure analysis
        copy_df: Whether to copy DataFrame (set False for performance)
    """
    if df is None or df.empty:
        return {
            "regime": "NEUTRAL STRUCTURE",
            "sequence": "NONE",
            "hvn": 0.0,
            "lvn": 0.0,
            "swing_struct": 0.0,
            "volume_sentiment": "NEUTRAL VOLUME",
            "df": df
        }

    # Performance optimization: avoid DataFrame copy when not needed
    current_price = df['close'].iloc[-1]  # Remove unnecessary float conversion
    engine = StructureEngine()
    result = engine.analyze(df, current_price)
    
    # Conditionally copy DataFrame based on copy_df parameter
    if copy_df:
        df_result = df.copy()
    else:
        df_result = df
    
    # Inject columns required by engine_core and trend_health modules
    # Use vectorized assignment for better performance
    regime_value = result.get("regime", "NEUTRAL STRUCTURE")
    hvn_value = result.get("hvn", 0.0)
    lvn_value = result.get("lvn", 0.0)
    
    df_result["STRUCTURE"] = regime_value
    df_result["HVN"] = hvn_value
    df_result["LVN"] = lvn_value
    
    result["df"] = df_result
        
    return result
