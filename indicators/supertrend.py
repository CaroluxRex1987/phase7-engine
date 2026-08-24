import pandas as pd

def supertrend(df, length=10, multiplier=3.0):
    """
    Custom SuperTrend implementation with comprehensive NaN handling.
    Returns:
        - SuperTrend line
        - Direction (1 = bullish, -1 = bearish)
    """

    if df is None or df.empty or len(df) < length:
        return df

    df = df.copy()

    # ============================================================
    # INPUT VALIDATION AND CLEANING
    # ============================================================

    required_cols = ["high", "low", "close"]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")
        # Clean input data
        df[col] = df[col].replace([np.inf, -np.inf], np.nan)
        df[col] = df[col].fillna(method='ffill').fillna(method='bfill')

    high = df["high"]
    low = df["low"]
    close = df["close"]

    # ============================================================
    # ATR CALCULATION WITH ENHANCED NaN HANDLING
    # ============================================================

    # True Range with comprehensive NaN handling
    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()

    # Handle NaN values in True Range calculation
    tr_df = pd.concat([tr1, tr2, tr3], axis=1)
    tr = tr_df.max(axis=1, skipna=True)
    
    # Ensure minimum TR to prevent zero ATR and handle edge cases
    typical_price = (high + low + close) / 3
    min_tr = typical_price * 0.0001  # 0.01% of typical price
    min_tr = min_tr.fillna(close * 0.0001)  # Fallback if typical_price has NaN
    
    tr = tr.fillna(min_tr).clip(lower=min_tr)
    
    # Validate TR series
    if tr.isna().any():
        tr = tr.fillna(method='ffill').fillna(method='bfill').fillna(close * 0.01)

    # ATR (RMA) with validation
    try:
        atr = tr.ewm(alpha=1/length, adjust=False).mean()
    except Exception:
        atr = tr.rolling(window=length).mean()
    
    # Cap extreme ATR values and handle NaN
    max_atr = typical_price * 0.1  # Cap ATR at 10% of typical price
    max_atr = max_atr.fillna(close * 0.05)  # Fallback cap
    atr = atr.clip(upper=max_atr)
    
    # Final ATR validation
    if atr.isna().any():
        atr = atr.fillna(method='ffill').fillna(method='bfill').fillna(close * 0.02)

    # ============================================================
    # BASIC BANDS
    # ============================================================

    hl2 = (high + low) / 2

    upper_band = hl2 + multiplier * atr
    lower_band = hl2 - multiplier * atr

    # ============================================================
    # FINAL BANDS WITH NaN PROTECTION
    # ============================================================

    final_upper = upper_band.copy()
    final_lower = lower_band.copy()

    for i in range(1, len(df)):
        try:
            # Validate values before comparison
            curr_upper = upper_band.iloc[i]
            prev_final_upper = final_upper.iloc[i - 1]
            prev_close = close.iloc[i - 1]
            
            if not all(np.isfinite([curr_upper, prev_final_upper, prev_close])):
                final_upper.iloc[i] = prev_final_upper if np.isfinite(prev_final_upper) else curr_upper
            else:
                # Final upper band logic
                if (curr_upper < prev_final_upper) or (prev_close > prev_final_upper):
                    final_upper.iloc[i] = curr_upper
                else:
                    final_upper.iloc[i] = prev_final_upper

            # Similar logic for lower band
            curr_lower = lower_band.iloc[i]
            prev_final_lower = final_lower.iloc[i - 1]
            
            if not all(np.isfinite([curr_lower, prev_final_lower, prev_close])):
                final_lower.iloc[i] = prev_final_lower if np.isfinite(prev_final_lower) else curr_lower
            else:
                # Final lower band logic
                if (curr_lower > prev_final_lower) or (prev_close < prev_final_lower):
                    final_lower.iloc[i] = curr_lower
                else:
                    final_lower.iloc[i] = prev_final_lower
                    
        except Exception:
            # Fallback to previous values
            final_upper.iloc[i] = final_upper.iloc[i - 1] if i > 0 else upper_band.iloc[i]
            final_lower.iloc[i] = final_lower.iloc[i - 1] if i > 0 else lower_band.iloc[i]

    # ============================================================
    # SUPERTREND LINE WITH NaN PROTECTION
    # ============================================================

    supertrend = pd.Series(index=df.index, dtype=float)
    direction = pd.Series(index=df.index, dtype=int)

    for i in range(len(df)):
        try:
            if i == 0:
                supertrend.iloc[i] = final_lower.iloc[i] if np.isfinite(final_lower.iloc[i]) else close.iloc[i]
                direction.iloc[i] = 1
                continue

            curr_close = close.iloc[i]
            prev_final_upper = final_upper.iloc[i - 1]
            prev_final_lower = final_lower.iloc[i - 1]
            prev_direction = direction.iloc[i - 1]

            # Validate values before comparison
            if not all(np.isfinite([curr_close, prev_final_upper, prev_final_lower])):
                direction.iloc[i] = prev_direction
            else:
                # Direction logic
                if curr_close > prev_final_upper:
                    direction.iloc[i] = 1
                elif curr_close < prev_final_lower:
                    direction.iloc[i] = -1
                else:
                    direction.iloc[i] = prev_direction

            # Choose band based on direction
            if direction.iloc[i] == 1:
                supertrend.iloc[i] = final_lower.iloc[i] if np.isfinite(final_lower.iloc[i]) else curr_close
            else:
                supertrend.iloc[i] = final_upper.iloc[i] if np.isfinite(final_upper.iloc[i]) else curr_close
                
        except Exception:
            # Fallback values
            direction.iloc[i] = 1 if i == 0 else direction.iloc[i - 1]
            supertrend.iloc[i] = close.iloc[i]

    # ============================================================
    # RETURN STRUCTURE
    # ============================================================

    df["SuperTrend"] = supertrend
    df["ST_Direction"] = direction

    return df
