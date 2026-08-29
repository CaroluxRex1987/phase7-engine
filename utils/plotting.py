import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import logging
import os
import numpy as np

logger = logging.getLogger(__name__)

def plot_engine_chart(df, entry_data, risk_data, save_path="chart_output.png"):
    """
    Modular Phase‑7 chart renderer with comprehensive error handling.
    Draws:
        - Candles
        - EMA20 / EMA50
        - Entry zone shading
        - ATR stop
        - Targets T1 / T2 / T3
    
    Returns:
        str: Path to saved chart or None if failed
    """
    
    try:
        # Validate inputs
        if df is None or df.empty:
            logger.error("Cannot plot chart: DataFrame is None or empty")
            return None
            
        if not isinstance(entry_data, dict) or not isinstance(risk_data, dict):
            logger.error("Cannot plot chart: entry_data or risk_data is not a dictionary")
            return None
            
        required_cols = ["open", "high", "low", "close"]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            logger.error(f"Cannot plot chart: missing required columns {missing_cols}")
            return None
            
        # Ensure save directory exists
        save_dir = os.path.dirname(save_path)
        if save_dir:
            os.makedirs(save_dir, exist_ok=True)

        # Set matplotlib style with fallback
        try:
            plt.style.use("dark_background")
        except Exception:
            logger.warning("Could not set dark_background style, using default")
            
        fig, ax = plt.subplots(figsize=(14, 8))
    except Exception as e:
        logger.error(f"Failed to initialize matplotlib figure: {e}")
        return None

    try:
        # ============================================================
        # CANDLE PLOTTING WITH ERROR HANDLING
        # ============================================================

        # Validate price data
        price_cols = ["open", "high", "low", "close"]
        for col in price_cols:
            if df[col].isna().any():
                logger.warning(f"NaN values found in {col}, filling with forward fill")
                df[col] = df[col].fillna(method='ffill').fillna(method='bfill')

        up = df[df["close"] >= df["open"]]
        down = df[df["close"] < df["open"]]

        # Candle wicks with error handling
        if not up.empty:
            try:
                ax.vlines(up.index, up["low"], up["high"], color="#22c55e", linewidth=1)
            except Exception as e:
                logger.warning(f"Failed to plot up candle wicks: {e}")
                
        if not down.empty:
            try:
                ax.vlines(down.index, down["low"], down["high"], color="#ef4444", linewidth=1)
            except Exception as e:
                logger.warning(f"Failed to plot down candle wicks: {e}")

        # Candle bodies with error handling
        if not up.empty:
            try:
                ax.bar(
                    up.index,
                    up["close"] - up["open"],
                    bottom=up["open"],
                    width=0.0008,
                    color="#22c55e"
                )
            except Exception as e:
                logger.warning(f"Failed to plot up candle bodies: {e}")

        if not down.empty:
            try:
                ax.bar(
                    down.index,
                    down["open"] - down["close"],
                    bottom=down["close"],
                    width=0.0008,
                    color="#ef4444"
                )
            except Exception as e:
                logger.warning(f"Failed to plot down candle bodies: {e}")
                
    except Exception as e:
        logger.error(f"Failed to plot candlesticks: {e}")
        # Continue with other chart elements

    try:
        # ============================================================
        # EMA OVERLAYS WITH ERROR HANDLING
        # ============================================================
        #
        # SEQUENCE ITEM 5a: the VWAP branch that used to sit below was
        # unreachable. Nothing in the engine ever assigns df["VWAP"] —
        # verified by searching every module for an assignment — so
        # `if "VWAP" in df.columns` was always False and the plot call inside
        # it had never executed. It read as a feature and was a no-op.
        #
        # This is the same shape as the dead gates recorded elsewhere in the
        # project: a guard testing for something no producer emits. Worth
        # noticing that a reader of this file would reasonably have believed
        # the chart could show VWAP.

        if "EMA_20" in df.columns and not df["EMA_20"].isna().all():
            try:
                ax.plot(df.index, df["EMA_20"], label="EMA20", color="#f59e0b", linewidth=1.4)
            except Exception as e:
                logger.warning(f"Failed to plot EMA_20: {e}")
                
        if "EMA_50" in df.columns and not df["EMA_50"].isna().all():
            try:
                ax.plot(df.index, df["EMA_50"], label="EMA50", color="#a855f7", linewidth=1.4)
            except Exception as e:
                logger.warning(f"Failed to plot EMA_50: {e}")

    except Exception as e:
        logger.error(f"Failed to plot indicators: {e}")

    try:
        # ============================================================
        # ENTRY ZONE SHADING WITH ERROR HANDLING
        # ============================================================

        entry_zone_lower = entry_data.get("entry_zone_lower")
        entry_zone_upper = entry_data.get("entry_zone_upper")

        if entry_zone_lower is not None and entry_zone_upper is not None:
            if np.isfinite(entry_zone_lower) and np.isfinite(entry_zone_upper):
                try:
                    ax.axhspan(
                        entry_zone_lower,
                        entry_zone_upper,
                        color="yellow",
                        alpha=0.12,
                        label="Entry Zone"
                    )
                except Exception as e:
                    logger.warning(f"Failed to plot entry zone: {e}")
            else:
                logger.warning("Entry zone values are not finite, skipping entry zone plot")
        else:
            logger.warning("Entry zone data missing, skipping entry zone plot")

    except Exception as e:
        logger.error(f"Failed to process entry zone: {e}")

    try:
        # ============================================================
        # ATR STOP & TARGETS WITH ERROR HANDLING
        # ============================================================

        atr_stop = risk_data.get("atr_stop")
        targets = risk_data.get("targets", (None, None, None))
        
        if len(targets) >= 3:
            t1, t2, t3 = targets[:3]
        else:
            t1, t2, t3 = None, None, None

        if atr_stop is not None and np.isfinite(atr_stop):
            try:
                ax.axhline(atr_stop, color="red", linestyle="--", linewidth=1.2, label="ATR Stop")
            except Exception as e:
                logger.warning(f"Failed to plot ATR stop: {e}")
        else:
            logger.warning("ATR stop value invalid, skipping ATR stop plot")

        for i, (target, label, color) in enumerate([(t1, "T1", "green"), (t2, "T2", "lime"), (t3, "T3", "darkgreen")]):
            if target is not None and np.isfinite(target):
                try:
                    ax.axhline(target, color=color, linestyle="--", linewidth=1.2, label=label)
                except Exception as e:
                    logger.warning(f"Failed to plot target {label}: {e}")
            else:
                logger.warning(f"Target {label} value invalid, skipping")

    except Exception as e:
        logger.error(f"Failed to process risk levels: {e}")

    try:
        # ============================================================
        # CHART FORMATTING WITH ERROR HANDLING
        # ============================================================

        try:
            ax.set_title("Phase‑7 Structural Quant Engine — Market Structure & Signals", fontsize=14)
        except Exception as e:
            logger.warning(f"Failed to set chart title: {e}")
            
        try:
            ax.grid(True, alpha=0.25)
        except Exception as e:
            logger.warning(f"Failed to set grid: {e}")
            
        try:
            ax.legend(loc="upper left")
        except Exception as e:
            logger.warning(f"Failed to set legend: {e}")

        # Date formatting with error handling
        try:
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
            fig.autofmt_xdate()
        except Exception as e:
            logger.warning(f"Failed to format dates: {e}")

        try:
            plt.tight_layout()
        except Exception as e:
            logger.warning(f"Failed to apply tight layout: {e}")
            
        try:
            plt.savefig(save_path, dpi=200, bbox_inches='tight')
            logger.info(f"Chart successfully saved to {save_path}")
        except Exception as e:
            logger.error(f"Failed to save chart to {save_path}: {e}")
            return None
        finally:
            try:
                plt.close()
            except Exception as e:
                logger.warning(f"Failed to close matplotlib figure: {e}")

        return save_path
        
    except Exception as e:
        logger.error(f"Failed to format and save chart: {e}")
        try:
            plt.close()
        except Exception:
            pass
        return None
