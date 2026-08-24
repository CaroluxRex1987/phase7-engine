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
        # Default fallback values or basic percentile estimations if empty
        if df is not None and not df.empty:
            hvn = float(df['high'].max())
            lvn = float(df['low'].min())
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
        """

        if df is None or len(df) < 20:
            return "NEUTRAL VOLUME"

        closes = df["close"].values
        volumes = df["volume"].values

        # VWMA slope (compare last 5 bars)
        vwma_recent = np.average(closes[-5:], weights=volumes[-5:])
        vwma_prev = np.average(closes[-10:-5], weights=volumes[-10:-5])

        vwma_slope = vwma_recent - vwma_prev

        # Price trend (last 5 bars)
        price_slope = closes[-1] - closes[-5]

        # Volume trend (last 5 bars)
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

def calculate_structure(df, lookback=8):
    """
    Compatibility wrapper function expected by engine_core.py.
    Provides structural analysis and injects required DataFrame columns
    (including 'STRUCTURE', 'HVN', and 'LVN') to support downstream modules.
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

    current_price = float(df['close'].iloc[-1])
    engine = StructureEngine()
    result = engine.analyze(df, current_price)
    
    # Create a copy of the DataFrame to prevent SettingWithCopy warnings
    df_copy = df.copy()
    
    # Inject columns required by engine_core and trend_health modules
    df_copy["STRUCTURE"] = result.get("regime", "NEUTRAL STRUCTURE")
    df_copy["HVN"] = result.get("hvn", 0.0)
    df_copy["LVN"] = result.get("lvn", 0.0)
    
    result["df"] = df_copy
        
    return result
