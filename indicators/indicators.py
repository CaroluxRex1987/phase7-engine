import pandas as pd
import pandas_ta as ta

def pct_slope(series: pd.Series) -> pd.Series:
    """Return the normalized percentage slope of a series."""
    return (series.diff() / series.shift(1)) * 100


def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add all core technical indicators required by the Phase‑7 engine.
    """

    df = df.copy()

    # ============================================================
    # CORE INDICATORS
    # ============================================================

    df["EMA_20"] = ta.ema(df["close"], length=20)
    df["EMA_50"] = ta.ema(df["close"], length=50)
    df["RSI"] = ta.rsi(df["close"], length=14)

    # Bollinger Bands
    bb = ta.bbands(df["close"], length=20, std=2.0)
    df["BB_lower"] = bb.iloc[:, 0]
    df["BB_middle"] = bb.iloc[:, 1]
    df["BB_upper"] = bb.iloc[:, 2]

    # ADX / DI
    adx_df = ta.adx(df["high"], df["low"], df["close"], length=14)
    df["ADX"] = adx_df.iloc[:, 0]
    df["DIP"] = adx_df.iloc[:, 1]
    df["DIM"] = adx_df.iloc[:, 2]

    # SuperTrend
    st_df = ta.supertrend(df["high"], df["low"], df["close"], length=10, multiplier=3.0)
    df["SuperTrend"] = st_df.iloc[:, 0]
    df["ST_Direction"] = st_df.iloc[:, 1]

    # Typical Price
    df["Typical_Price"] = (df["high"] + df["low"] + df["close"]) / 3.0

    # ============================================================
    # SECONDARY INDICATORS
    # ============================================================

    df["ATR"] = ta.atr(df["high"], df["low"], df["close"], length=14)
    df["KAMA"] = ta.kama(df["close"], length=10)

    # VWMA (Volume‑Weighted Moving Average)
    df["VWMA"] = (
        (df["close"] * df["volume"]).rolling(window=20).sum()
        / df["volume"].rolling(window=20).sum()
    )

    # ============================================================
    # SLOPES
    # ============================================================

    df["EMA20_Slope"] = pct_slope(df["EMA_20"])
    df["EMA50_Slope"] = pct_slope(df["EMA_50"])
    df["VWMA_Slope"] = pct_slope(df["VWMA"])
    df["KAMA_Slope"] = pct_slope(df["KAMA"])

    return df
