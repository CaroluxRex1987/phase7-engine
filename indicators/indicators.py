import pandas as pd
import numpy as np
import pandas_ta as ta

from core import config

def clean_series(series: pd.Series, method: str = "forward_fill", fallback_value: float = None) -> pd.Series:
    """
    Clean a pandas Series by handling NaN, inf, and extreme values.

    Args:
        series: Input series to clean
        method: Cleaning method ('forward_fill', 'interpolate', 'drop', 'fill_value')
        fallback_value: Value to use when method='fill_value'

    Returns:
        Cleaned series
    """
    if series is None or series.empty:
        return series

    # Replace inf values with NaN
    series = series.replace([np.inf, -np.inf], np.nan)

    # Handle extreme outliers (beyond 5 standard deviations)
    if len(series.dropna()) > 10:
        mean_val = series.mean()
        std_val = series.std()
        if np.isfinite(mean_val) and np.isfinite(std_val) and std_val > 0:
            outlier_mask = np.abs(series - mean_val) > (5 * std_val)
            series.loc[outlier_mask] = np.nan

    # Apply cleaning method
    if method == "forward_fill":
        series = series.ffill().bfill()
    elif method == "interpolate":
        series = series.interpolate(method='linear', limit_direction='both')
    elif method == "fill_value" and fallback_value is not None:
        series = series.fillna(fallback_value)
    elif method == "drop":
        series = series.dropna()

    # Final fallback: fill remaining NaN with median or zero
    if series.isna().any():
        median_val = series.median()
        fill_val = median_val if np.isfinite(median_val) else 0.0
        series = series.fillna(fill_val)

    return series

def pct_slope(series: pd.Series) -> pd.Series:
    """Return the normalized percentage slope of a series with NaN handling."""
    if series is None or len(series) < 2:
        return pd.Series(dtype=float, index=series.index if series is not None else [])

    # Clean input series first
    series = clean_series(series, method="forward_fill")

    # Calculate slope with zero division protection
    prev_values = series.shift(1)
    slope = (series.diff() / prev_values) * 100

    # Handle division by zero cases
    slope = slope.replace([np.inf, -np.inf], 0.0)

    return clean_series(slope, method="forward_fill")


def add_technical_indicators(df: pd.DataFrame, inplace: bool = False) -> pd.DataFrame:
    """
    Add all core technical indicators required by the Phase‑7 engine with comprehensive NaN handling.
    Optimized for performance with minimal DataFrame copying.
    """

    if not inplace:
        df = df.copy()

    # Validate and clean input data (vectorized operations)
    required_cols = ["open", "high", "low", "close", "volume"]

    # Batch clean all columns at once to reduce overhead
    for col in required_cols:
        if col in df.columns:
            # Use in-place operations where possible
            df[col] = df[col].replace([np.inf, -np.inf], np.nan)
            df[col] = df[col].ffill().bfill()

    # ============================================================
    # CORE INDICATORS WITH NaN PROTECTION (Optimized)
    # ============================================================

    # Pre-extract close prices to avoid repeated column access
    close_prices = df["close"]

    # Calculate EMAs with optimized fallback
    try:
        ema_20 = ta.ema(close_prices, length=20)
        df["EMA_20"] = ema_20.ffill().bfill() if ema_20.isna().any() else ema_20
    except Exception:
        df["EMA_20"] = close_prices.ewm(span=20, adjust=False).mean()

    try:
        ema_50 = ta.ema(close_prices, length=50)
        df["EMA_50"] = ema_50.ffill().bfill() if ema_50.isna().any() else ema_50
    except Exception:
        df["EMA_50"] = close_prices.ewm(span=50, adjust=False).mean()

    try:
        df["RSI"] = clean_series(ta.rsi(df["close"], length=14), method="forward_fill", fallback_value=50.0)
    except Exception:
        # Fallback RSI calculation
        delta = df["close"].diff()
        gain = delta.where(delta > 0, 0).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss.replace(0, np.nan)
        df["RSI"] = clean_series(100 - (100 / (1 + rs)), method="fill_value", fallback_value=50.0)

    # SEQUENCE ITEM 5a: Bollinger Bands removed. BB_lower, BB_middle and
    # BB_upper were written on both the success and fallback paths and read
    # nowhere in the engine — verified by scanning every module for a read.
    # Item 16 (no unconsumed complexity): computing three columns per run that
    # nothing consumes is cost without benefit, and every fallback that writes
    # a fabricated value is one more path Item 13 would otherwise have to give
    # honest semantics to.
    #
    # config.BB_LENGTH and config.BB_STD are now unused. They stay for
    # sequence item 14 (explicit configuration) to remove alongside the other
    # declared-but-unread constants, rather than being deleted here — this
    # step is scoped to code the engine computes, not to config hygiene.

    # ADX / DI with error handling
    try:
        adx_df = ta.adx(df["high"], df["low"], df["close"], length=14)
        if adx_df is not None and not adx_df.empty:
            # SEQUENCE ITEM 5a: DIP and DIM (the directional indicators at
            # columns 1 and 2) were written here and read nowhere. ADX itself
            # is consumed — trend_health and bias both read it — so the call
            # stays and only the two unread columns go.
            #
            # Note for anyone deleting by name: `DIM` is also colorama's
            # dim-text style, used at panel_render.py:1181 as `dim =
            # Style.DIM`. That is unrelated to this dataframe column and
            # removing it breaks the panel's formatting.
            df["ADX"] = clean_series(adx_df.iloc[:, 0], method="forward_fill", fallback_value=25.0)
        else:
            raise ValueError("ADX calculation failed")
    except Exception:
        # Fallback ADX value
        df["ADX"] = pd.Series(25.0, index=df.index)

    # SuperTrend with error handling
    # A9 FIX: This is now the single, canonical SuperTrend implementation for the
    # engine (pandas_ta-based). The previous standalone custom loop-based
    # implementation in supertrend.py was never imported/called anywhere in the
    # pipeline (main.py, engine_core.py, structure.py, plotting.py, or any other
    # module) — it was dead code that only posed a future collision risk on the
    # same "SuperTrend" / "ST_Direction" column names. It has been deleted.
    # Length/multiplier are now pulled from config.py instead of being hardcoded,
    # so config.SUPERTREND_LENGTH / config.SUPERTREND_MULT (previously unused)
    # actually control the calculation.
    try:
        st_df = ta.supertrend(
            df["high"], df["low"], df["close"],
            length=config.SUPERTREND_LENGTH,
            multiplier=config.SUPERTREND_MULT,
        )
        if st_df is not None and not st_df.empty:
            df["SuperTrend"] = clean_series(st_df.iloc[:, 0], method="forward_fill")
            df["ST_Direction"] = clean_series(st_df.iloc[:, 1], method="fill_value", fallback_value=1.0)
        else:
            raise ValueError("SuperTrend calculation failed")
    except Exception:
        # Fallback SuperTrend
        df["SuperTrend"] = df["close"]
        df["ST_Direction"] = pd.Series(1.0, index=df.index)

    # SEQUENCE ITEM 5a: Typical_Price removed — written once, read nowhere.
    # It is the classic (H+L+C)/3 input to VWAP and CCI, neither of which this
    # engine calculates.

    # ============================================================
    # SECONDARY INDICATORS WITH NaN PROTECTION
    # ============================================================

    try:
        df["ATR"] = clean_series(ta.atr(df["high"], df["low"], df["close"], length=14),
                                method="forward_fill", fallback_value=df["close"].iloc[-1] * 0.02)
    except Exception:
        # Fallback ATR calculation
        tr1 = df["high"] - df["low"]
        tr2 = (df["high"] - df["close"].shift(1)).abs()
        tr3 = (df["low"] - df["close"].shift(1)).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1, skipna=True)
        df["ATR"] = clean_series(tr.rolling(window=14).mean(), method="forward_fill")

    # SEQUENCE ITEM 5a: KAMA removed. The column itself was read by exactly
    # one thing — the slope loop below, which produced KAMA_Slope, which
    # nothing read. A dead chain two links long: the only consumer of KAMA
    # existed to feed a consumer that did not exist.
    #
    # config.KAMA_LENGTH is now unused; left for sequence item 14, as above.

    # VWMA with optimized calculation (avoid intermediate Series creation)
    try:
        volume_col = df["volume"]
        # Use rolling operations directly without creating intermediate cleaned series
        volume_sum = volume_col.rolling(window=20).sum()
        price_volume_sum = (close_prices * volume_col).rolling(window=20).sum()

        # Vectorized calculation with safe division
        valid_mask = (volume_sum > 0) & np.isfinite(volume_sum) & np.isfinite(price_volume_sum)
        df["VWMA"] = np.where(valid_mask, price_volume_sum / volume_sum, close_prices)

        # Fill any remaining NaN values
        if df["VWMA"].isna().any():
            df["VWMA"] = df["VWMA"].ffill().bfill().fillna(close_prices)
    except Exception:
        df["VWMA"] = close_prices

    # ============================================================
    # SLOPES WITH OPTIMIZED CALCULATION
    # ============================================================

    # Batch calculate slopes to reduce function call overhead
    #
    # SEQUENCE ITEM 5a: was four columns; VWMA_Slope and KAMA_Slope were
    # produced here and read nowhere, and KAMA itself is now gone. The two
    # that remain are genuinely consumed — trend_health.py reads EMA20_Slope
    # at three places and EMA50_Slope at one, so this loop stays.
    #
    # VWMA is NOT removed: entry_model consumes it for distance scoring. Only
    # its slope was dead.
    slope_columns = ["EMA_20", "EMA_50"]
    slope_names = ["EMA20_Slope", "EMA50_Slope"]

    for col, slope_name in zip(slope_columns, slope_names):
        if col in df.columns:
            # Optimized slope calculation without function call overhead
            series = df[col]
            prev_values = series.shift(1)
            slope = ((series - prev_values) / prev_values * 100).replace([np.inf, -np.inf], 0.0)
            df[slope_name] = slope.ffill().bfill().fillna(0.0)

    # Final validation: ensure no critical indicators have all NaN values
    critical_indicators = ["EMA_20", "EMA_50", "RSI", "ATR", "ADX"]
    for indicator in critical_indicators:
        if indicator in df.columns and df[indicator].isna().all():
            if indicator in ["EMA_20", "EMA_50"]:
                df[indicator] = df["close"]
            elif indicator == "RSI":
                df[indicator] = 50.0
            elif indicator == "ATR":
                df[indicator] = df["close"] * 0.02
            elif indicator == "ADX":
                df[indicator] = 25.0

    return df