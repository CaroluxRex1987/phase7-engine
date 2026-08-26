import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def compute_volume_profile(df: pd.DataFrame, num_bins: int = 50):
    """
    Compute a true binned price-volume profile using proportional
    candle overlap distribution with comprehensive error handling.

    Returns:
        profile (pd.Series): Volume per price bin
        hvn (float): High Volume Node (bin midpoint)
        lvn (float): Low Volume Node (bin midpoint)
    """

    try:
        if df is None:
            logger.error("DataFrame is None")
            return pd.Series(dtype=float, name="volume"), None, None

        if not isinstance(df, pd.DataFrame):
            logger.error("Input is not a pandas DataFrame")
            return pd.Series(dtype=float, name="volume"), None, None

        if df.empty:
            logger.warning("DataFrame is empty")
            return pd.Series(dtype=float, name="volume"), None, None

        required = {"low", "high", "volume"}
        missing = required - set(df.columns)
        if missing:
            logger.error(f"Missing required columns: {sorted(missing)}")
            return pd.Series(dtype=float, name="volume"), None, None

        if num_bins < 1:
            logger.error("num_bins must be at least 1")
            num_bins = 50

        try:
            for col in ["low", "high", "volume"]:
                if df[col].isna().any():
                    logger.warning(f"NaN values found in {col}, cleaning data")
                    df[col] = df[col].ffill().bfill().fillna(0)
                df[col] = df[col].replace([np.inf, -np.inf], np.nan).fillna(0)
        except Exception as e:
            logger.error(f"Failed to clean input data: {e}")
            return pd.Series(dtype=float, name="volume"), None, None

    except Exception as e:
        logger.error(f"Input validation failed: {e}")
        return pd.Series(dtype=float, name="volume"), None, None

    try:
        try:
            price_min = float(df["low"].min())
            price_max = float(df["high"].max())
        except Exception as e:
            logger.error(f"Failed to calculate price range: {e}")
            return pd.Series(dtype=float, name="volume"), None, None

        if not np.isfinite(price_min) or not np.isfinite(price_max):
            logger.error("Price range contains non-finite values")
            return pd.Series(dtype=float, name="volume"), None, None

        if price_max <= price_min:
            logger.error(f"Invalid price range: max ({price_max}) <= min ({price_min})")
            price_mid = (price_max + price_min) / 2 if price_max == price_min else price_min
            price_min = price_mid * 0.999
            price_max = price_mid * 1.001

        try:
            edges = np.linspace(price_min, price_max, num_bins + 1)
            bins = pd.IntervalIndex.from_breaks(edges, closed="right")
        except Exception as e:
            logger.error(f"Failed to create price bins: {e}")
            return pd.Series(dtype=float, name="volume"), None, None

        try:
            profile = pd.Series(0.0, index=bins, name="volume")
        except Exception as e:
            logger.error(f"Failed to initialize volume profile: {e}")
            return pd.Series(dtype=float, name="volume"), None, None

    except Exception as e:
        logger.error(f"Price range and bin construction failed: {e}")
        return pd.Series(dtype=float, name="volume"), None, None

    try:
        processed_candles = 0
        skipped_candles = 0

        try:
            candle_data = df[["low", "high", "volume"]].itertuples(index=False, name=None)
        except Exception as e:
            logger.error(f"Failed to iterate over candle data: {e}")
            return pd.Series(dtype=float, name="volume"), None, None

        for candle in candle_data:
            try:
                low, high, volume = candle
                if not np.isfinite(low) or not np.isfinite(high) or not np.isfinite(volume):
                    skipped_candles += 1
                    continue
                if high < low or volume < 0:
                    skipped_candles += 1
                    continue

                candle_range = high - low
                min_range = (high + low) * 0.5 * 1e-6

                if candle_range <= min_range:
                    try:
                        mid_price = (high + low) * 0.5
                        closest_bin = None
                        min_distance = float('inf')
                        for interval in bins:
                            try:
                                distance = min(abs(mid_price - interval.left), abs(mid_price - interval.right))
                                if distance < min_distance:
                                    min_distance = distance
                                    closest_bin = interval
                            except Exception:
                                continue
                        if closest_bin is not None:
                            profile.loc[closest_bin] += volume
                            processed_candles += 1
                    except Exception as e:
                        logger.warning(f"Failed to process doji candle: {e}")
                        skipped_candles += 1
                    continue

                try:
                    for interval in bins:
                        try:
                            overlap_low = max(low, interval.left)
                            overlap_high = min(high, interval.right)
                            if overlap_high > overlap_low:
                                overlap = overlap_high - overlap_low
                                proportion = overlap / candle_range
                                profile.loc[interval] += volume * proportion
                        except Exception as e:
                            logger.warning(f"Failed to process bin overlap: {e}")
                            continue
                    processed_candles += 1
                except Exception as e:
                    logger.warning(f"Failed to distribute volume for candle: {e}")
                    skipped_candles += 1

            except Exception as e:
                logger.warning(f"Failed to process candle: {e}")
                skipped_candles += 1
                continue

        logger.info(f"Volume profile: processed {processed_candles} candles, skipped {skipped_candles}")

    except Exception as e:
        logger.error(f"Volume distribution failed: {e}")
        return pd.Series(dtype=float, name="volume"), None, None

    try:
        if profile.sum() == 0:
            logger.warning("Volume profile is empty (zero total volume)")
            return profile, None, None

        try:
            centers = pd.Series([interval.mid for interval in bins], index=bins)
        except Exception as e:
            logger.error(f"Failed to calculate bin centers: {e}")
            return profile, None, None

        try:
            hvn_idx = profile.idxmax()
            lvn_idx = profile.idxmin()
            hvn = float(centers.loc[hvn_idx])
            lvn = float(centers.loc[lvn_idx])
            if not np.isfinite(hvn) or not np.isfinite(lvn):
                logger.warning("HVN or LVN values are not finite")
                hvn = None if not np.isfinite(hvn) else hvn
                lvn = None if not np.isfinite(lvn) else lvn
        except Exception as e:
            logger.error(f"Failed to extract HVN/LVN: {e}")
            hvn, lvn = None, None

        return profile, hvn, lvn

    except Exception as e:
        logger.error(f"HVN/LVN extraction failed: {e}")
        return pd.Series(dtype=float, name="volume"), None, None
