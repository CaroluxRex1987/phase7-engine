import numpy as np
import pandas as pd

def compute_volume_profile(df: pd.DataFrame, num_bins: int = 50):
    """
    Compute a true binned price–volume profile using proportional
    candle overlap distribution.

    Returns:
        profile (pd.Series): Volume per price bin
        hvn (float): High Volume Node (bin midpoint)
        lvn (float): Low Volume Node (bin midpoint)
    """

    # ============================================================
    # VALIDATION
    # ============================================================

    required = {"low", "high", "volume"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    if df.empty:
        return pd.Series(dtype=float, name="volume"), None, None

    if num_bins < 1:
        raise ValueError("num_bins must be at least 1")

    # ============================================================
    # PRICE RANGE
    # ============================================================

    price_min = float(df["low"].min())
    price_max = float(df["high"].max())

    if not np.isfinite(price_min) or not np.isfinite(price_max) or price_max < price_min:
        raise ValueError("Invalid price range in low/high columns")

    # ============================================================
    # BIN CONSTRUCTION
    # ============================================================

    edges = np.linspace(price_min, price_max, num_bins + 1)
    bins = pd.IntervalIndex.from_breaks(edges, closed="right")

    # Initialize profile
    profile = pd.Series(0.0, index=bins, name="volume")

    # ============================================================
    # PROPORTIONAL VOLUME DISTRIBUTION
    # ============================================================

    for low, high, volume in df[["low", "high", "volume"]].itertuples(index=False, name=None):

        # Skip invalid candles
        if not np.isfinite(low) or not np.isfinite(high) or high < low:
            continue

        # Candle range with minimum threshold to prevent division issues
        candle_range = high - low
        min_range = (high + low) * 0.5 * 1e-6  # Minimum range as fraction of price
        if candle_range <= min_range:
            # For doji/near-doji candles, distribute volume to closest bin
            mid_price = (high + low) * 0.5
            closest_bin = None
            min_distance = float('inf')
            for interval in bins:
                distance = min(abs(mid_price - interval.left), abs(mid_price - interval.right))
                if distance < min_distance:
                    min_distance = distance
                    closest_bin = interval
            if closest_bin is not None:
                profile.loc[closest_bin] += volume
            continue

        # For each bin, compute overlap proportion
        for interval in bins:
            overlap_low = max(low, interval.left)
            overlap_high = min(high, interval.right)

            if overlap_high > overlap_low:
                overlap = overlap_high - overlap_low
                proportion = overlap / candle_range
                profile.loc[interval] += volume * proportion

    # ============================================================
    # HVN / LVN EXTRACTION
    # ============================================================

    if profile.sum() == 0:
        return profile, None, None

    centers = pd.Series([interval.mid for interval in bins], index=bins)

    hvn = float(centers.loc[profile.idxmax()])
    lvn = float(centers.loc[profile.idxmin()])

    # ============================================================
    # RETURN STRUCTURE
    # ============================================================

    return profile, hvn, lvn
