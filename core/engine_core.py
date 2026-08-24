import pandas as pd
from typing import Dict, Any, Optional
import logging

from . import config
from data.data_fetcher import data_fetcher
from indicators.indicators import add_technical_indicators
from structure.structure import calculate_structure
from indicators.trend_health import compute_trend_health
from models.bias_engine import (
    calculate_dynamic_bias,
    calculate_dynamic_regime,
    BiasStateMachine,
)
from models.risk_model import RiskModel
from models.entry_model import generate_entry_signals, calculate_entry_quality
from models.exit_model import compute_exit
from utils.plotting import plot_engine_chart
from core.panel_render import render_panel

logger = logging.getLogger(__name__)


class Phase7Engine:
    """
    Phase‑7 Structural Quant Engine
    Main orchestrator for:
        - Data
        - Indicators
        - Structure
        - Trend health
        - Bias
        - Entry
        - Risk
        - Exit
        - Charting
        - Multi-Timeframe Confluence (MTF)
    """

    def __init__(self) -> None:
        self.bias_state_machine = BiasStateMachine()
        self.risk_model = RiskModel()

    def _validate_dataframe(self, df: pd.DataFrame, required_columns: list, context: str = "") -> bool:
        """
        Validate DataFrame has required columns and sufficient data.
        
        Args:
            df: DataFrame to validate
            required_columns: List of required column names
            context: Context string for error messages
            
        Returns:
            bool: True if valid, False otherwise
        """
        if df is None or df.empty:
            logger.error(f"DataFrame validation failed - empty or None DataFrame in {context}")
            return False
            
        if len(df) < 20:
            logger.error(f"DataFrame validation failed - insufficient data ({len(df)} rows) in {context}")
            return False
            
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            logger.error(f"DataFrame validation failed - missing columns {missing_cols} in {context}")
            return False
            
        return True

    def run(
        self, 
        symbol: Optional[str] = None, 
        timeframe: Optional[str] = None, 
        limit: int = 450, 
        save_chart: bool = True, 
        render: bool = True
    ) -> Dict[str, Any]:
        """
        Execute full engine pipeline with Multi-Timeframe Confluence.
        
        Args:
            symbol: Trading symbol (defaults to config.SYMBOL)
            timeframe: Timeframe for analysis (defaults to config.TIMEFRAME)
            limit: Number of candles to fetch
            save_chart: Whether to save chart output
            render: Whether to render panel output
            
        Returns:
            Dict containing decision object with analysis results or error information
        """

        symbol = symbol or config.SYMBOL
        timeframe = timeframe or config.TIMEFRAME
        macro_tf = getattr(config, "MACRO_TIMEFRAME", "1d")

        try:
            # 1. FETCH EXECUTION DATA
            df = data_fetcher.get_tf(symbol, timeframe, limit=limit)

            # Enhanced DataFrame validation
            required_base_cols = ["open", "high", "low", "close", "volume"]
            if not self._validate_dataframe(df, required_base_cols, "base market data"):
                decision_object = {
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "error": "Invalid or insufficient market data",
                }
                if render:
                    render_panel(decision_object)
                return decision_object

            # 1b. FETCH MACRO DATA (Multi-Timeframe Confluence)
            df_macro = data_fetcher.get_tf(symbol, macro_tf, limit=100)
            macro_bias = "NEUTRAL"
            
            if self._validate_dataframe(df_macro, required_base_cols, "macro timeframe data"):
                try:
                    df_macro = add_technical_indicators(df_macro)
                    if "EMA_50" in df_macro.columns:
                        macro_close = df_macro["close"].iloc[-1]
                        macro_ema50 = df_macro["EMA_50"].iloc[-1]
                        
                        if macro_close > macro_ema50:
                            macro_bias = "BULLISH"
                        elif macro_close < macro_ema50:
                            macro_bias = "BEARISH"
                except Exception as e:
                    logger.warning(f"Failed to process macro timeframe data: {e}")
                    macro_bias = "NEUTRAL"

            # 2. INDICATORS
            try:
                df = add_technical_indicators(df)
                
                # Validate required indicators were added
                required_indicators = ["EMA_20", "EMA_50", "RSI", "ATR", "ADX"]
                if not self._validate_dataframe(df, required_indicators, "technical indicators"):
                    raise ValueError("Failed to generate required technical indicators")
                    
            except Exception as e:
                logger.error(f"Failed to add technical indicators: {e}")
                decision_object = {
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "error": f"Technical indicator calculation failed: {str(e)}",
                }
                if render:
                    render_panel(decision_object)
                return decision_object

            # 3. STRUCTURE ENGINE
            try:
                structure_obj = calculate_structure(df)
                if not isinstance(structure_obj, dict):
                    raise ValueError("Structure engine returned invalid format")
                    
                df_struct = structure_obj.get("df", df)
                
                # Validate structure output
                if not self._validate_dataframe(df_struct, required_indicators, "structure analysis"):
                    raise ValueError("Structure analysis produced invalid DataFrame")

                structure_regime = structure_obj.get("regime", "NEUTRAL STRUCTURE")
                trend_sequence = structure_obj.get("sequence", "NONE")
                volume_sentiment = structure_obj.get("volume_sentiment", "NEUTRAL VOLUME")
                
            except Exception as e:
                logger.error(f"Structure analysis failed: {e}")
                decision_object = {
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "error": f"Structure analysis failed: {str(e)}",
                }
                if render:
                    render_panel(decision_object)
                return decision_object

            # 4. TREND HEALTH ENGINE
            try:
                trend = compute_trend_health(df_struct)
                if not isinstance(trend, dict) or "trend_health" not in trend:
                    raise ValueError("Trend health engine returned invalid format")
            except Exception as e:
                logger.error(f"Trend health analysis failed: {e}")
                # Use safe defaults
                trend = {
                    "trend_health": 50.0,
                    "trend_failure": False,
                    "trend_exhaustion": False,
                    "momentum_mode": "NEUTRAL",
                    "momentum_divergence": False
                }

            # 5. BIAS ENGINE
            raw_bias, bias_score = calculate_dynamic_bias(
                df=df_struct,
                trend_sequence=trend_sequence,
                trend_health=trend["trend_health"],
                trend_failure=trend["trend_failure"],
                trend_exhaustion=trend["trend_exhaustion"],
                reversal_direction=trend.get("reversal_direction"),
                reversal_strength=trend.get("reversal_strength", 0),
                continuation_strength=trend.get("continuation_strength"),
            )

            dynamic_regime, volatility_mode = calculate_dynamic_regime(df_struct)

            detailed_bias = self.bias_state_machine.transition(raw_bias, bias_score)

            bias = {
                "raw": raw_bias,
                "detailed": detailed_bias,
                "score": bias_score,
                "regime": dynamic_regime,
                "volatility": volatility_mode,
            }

            # 6. STRUCTURE SUMMARY
            hvn = df_struct["HVN"].iloc[-1] if "HVN" in df_struct.columns else structure_obj.get("hvn", 0.0)
            lvn = df_struct["LVN"].iloc[-1] if "LVN" in df_struct.columns else structure_obj.get("lvn", 0.0)

            structure = {
                "regime": structure_regime,
                "sequence": trend_sequence,
                "hvn": hvn,
                "lvn": lvn,
                "volume_sentiment": volume_sentiment,
            }

            # 7. ENTRY MODEL & ENTRY QUALITY ENGINE (STEP 3 UPGRADE)
            long_signal, short_signal = generate_entry_signals(
                detailed_bias=detailed_bias,
                structure_regime=structure_regime,
                trend_health=trend["trend_health"],
                trend_failure=trend["trend_failure"],
                trend_exhaustion=trend["trend_exhaustion"],
                reversal_strength=trend.get("reversal_strength", 0),
                macro_bias=macro_bias,
            )

            entry_zone_lower = df_struct["EMA_20"].iloc[-1] if "EMA_20" in df_struct.columns else df_struct["close"].iloc[-1] * 0.99
            entry_zone_upper = df_struct["EMA_50"].iloc[-1] if "EMA_50" in df_struct.columns else df_struct["close"].iloc[-1] * 1.01

            # Compute real quantitative entry scores via calculate_entry_quality
            eq_metrics = calculate_entry_quality(df_struct, entry_zone_lower, entry_zone_upper)

            entry = {
                "zone_lower": entry_zone_lower,
                "zone_upper": entry_zone_upper,
                "long_signal": long_signal,
                "short_signal": short_signal,
                "score": eq_metrics["score"],
                "ema_pos_pts": eq_metrics["ema_pos_pts"],
                "atr_dist_pts": eq_metrics["atr_dist_pts"],
                "vwma_pts": eq_metrics["vwma_pts"],
                "rsi_pts": eq_metrics["rsi_pts"],
                "struct_pts": eq_metrics["struct_pts"],
                "entry_status": eq_metrics["entry_status"],
                "distance_from_zone": eq_metrics["distance_from_zone"],
            }

            # 8. RISK MODEL & VALIDATION ENGINE UPGRADE (STEP 2)
            current_price = df_struct["close"].iloc[-1]
            atr_val = df_struct["ATR"].iloc[-1] if "ATR" in df_struct.columns else (current_price * 0.02)

            atr_stop, t1, t2, t3 = self.risk_model.calculate_stop_targets(
                detailed_bias=detailed_bias,
                trend_health=trend["trend_health"],
                current_price=current_price,
                atr_val=atr_val,
                structural_level=hvn,
                bias_score=bias_score,
            )

            risk_valid, risk_reason = self.risk_model.validate_risk_parameters(
                current_price=current_price,
                atr_stop=atr_stop,
                reference_price=current_price,
            )

            # --- Dynamic Validation Engine Computation ---
            trend_health = trend.get("trend_health", 50.0)
            val_score = trend_health
            val_notes = []
            
            if "BULLISH" in macro_bias.upper():
                val_score += 5
            elif "BEARISH" in macro_bias.upper():
                val_score -= 5
                
            if "STRONG" in volume_sentiment.upper() or "EXPANSION" in volume_sentiment.upper():
                val_score += 10
                val_notes.append("Volume sentiment is supportive of current momentum.")
            elif "DIVERGENCE" in volume_sentiment.upper() or "WEAK" in volume_sentiment.upper():
                val_score -= 15
                val_notes.append("Volume divergence or weakness detected.")
            else:
                val_notes.append("Volume sentiment is neutral.")
                
            if trend_health >= 75:
                val_notes.append("Trend health is robust.")
            elif trend_health < 50:
                val_notes.append("Trend health is degrading.")
            else:
                val_notes.append("Trend health is moderate.")
                
            val_score = max(0.0, min(100.0, val_score))
            
            if val_score >= 70:
                validation_state = "STRONG"
            elif val_score >= 45:
                validation_state = "NEUTRAL"
            else:
                validation_state = "WEAK"
                
            validation_note = " | ".join(val_notes)

            risk = {
                "atr_stop": atr_stop,
                "targets": (t1, t2, t3),
                "risk_valid": risk_valid,
                "risk_reason": risk_reason,
                "risk_score": bias_score,
                "confidence_score": trend["trend_health"],
                "signal_strength": bias_score,
                "trade_quality_current": trend["trend_health"],
                "trade_quality_proposed": eq_metrics["score"],
                "validation_state": validation_state,
                "validation_score": val_score,
                "validation_note": validation_note,
            }

            # 9. EXIT MODEL
            exit_data = compute_exit(
                price_data=df_struct,
                entry_data=entry,
                risk_data=risk,
            )

            # 10. CHARTING
            chart_path = None
            if save_chart:
                chart_path = plot_engine_chart(
                    df=df_struct,
                    entry_data={
                        "entry_zone_lower": entry_zone_lower,
                        "entry_zone_upper": entry_zone_upper,
                    },
                    risk_data={
                        "atr_stop": atr_stop,
                        "targets": (t1, t2, t3),
                    },
                    save_path=f"{config.CHART_DIR}/chart_{symbol}_{timeframe}.png",
                )

            # 11. UNIFIED RETURN OBJECT
            decision_object = {
                "symbol": symbol,
                "timeframe": timeframe,
                "macro_bias": macro_bias,
                "bias": bias,
                "trend": trend,
                "structure": structure,
                "entry": entry,
                "risk": risk,
                "exit": exit_data,
                "chart_path": chart_path,
            }

            # 12. RENDER PANEL (Only if render is True)
            if render:
                render_panel(decision_object)

            return decision_object

        except Exception as e:
            import traceback
            traceback.print_exc()
            decision_object = {
                "symbol": symbol,
                "timeframe": timeframe,
                "error": str(e),
            }
            if render:
                render_panel(decision_object)
            return decision_object
