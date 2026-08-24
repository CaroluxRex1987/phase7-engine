import pandas as pd

def supertrend(df, length=10, multiplier=3.0):
    """
    Custom SuperTrend implementation.
    Returns:
        - SuperTrend line
        - Direction (1 = bullish, -1 = bearish)
    """

    df = df.copy()

    # ============================================================
    # ATR CALCULATION
    # ============================================================

    high = df["high"]
    low = df["low"]
    close = df["close"]

    # True Range
    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()

    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    # ATR (RMA)
    atr = tr.ewm(alpha=1/length, adjust=False).mean()

    # ============================================================
    # BASIC BANDS
    # ============================================================

    hl2 = (high + low) / 2

    upper_band = hl2 + multiplier * atr
    lower_band = hl2 - multiplier * atr

    # ============================================================
    # FINAL BANDS
    # ============================================================

    final_upper = upper_band.copy()
    final_lower = lower_band.copy()

    for i in range(1, len(df)):
        # Final upper band
        if (upper_band.iloc[i] < final_upper.iloc[i - 1]) or (close.iloc[i - 1] > final_upper.iloc[i - 1]):
            final_upper.iloc[i] = upper_band.iloc[i]
        else:
            final_upper.iloc[i] = final_upper.iloc[i - 1]

        # Final lower band
        if (lower_band.iloc[i] > final_lower.iloc[i - 1]) or (close.iloc[i - 1] < final_lower.iloc[i - 1]):
            final_lower.iloc[i] = lower_band.iloc[i]
        else:
            final_lower.iloc[i] = final_lower.iloc[i - 1]

    # ============================================================
    # SUPERTREND LINE
    # ============================================================

    supertrend = pd.Series(index=df.index, dtype=float)
    direction = pd.Series(index=df.index, dtype=int)

    for i in range(len(df)):
        if i == 0:
            supertrend.iloc[i] = final_lower.iloc[i]
            direction.iloc[i] = 1
            continue

        if close.iloc[i] > final_upper.iloc[i - 1]:
            direction.iloc[i] = 1
        elif close.iloc[i] < final_lower.iloc[i - 1]:
            direction.iloc[i] = -1
        else:
            direction.iloc[i] = direction.iloc[i - 1]

        # Choose band based on direction
        if direction.iloc[i] == 1:
            supertrend.iloc[i] = final_lower.iloc[i]
        else:
            supertrend.iloc[i] = final_upper.iloc[i]

    # ============================================================
    # RETURN STRUCTURE
    # ============================================================

    df["SuperTrend"] = supertrend
    df["ST_Direction"] = direction

    return df
