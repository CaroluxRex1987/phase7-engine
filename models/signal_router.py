import os
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class SignalRouter:
    """
    Routes raw engine data into unified decision objects and handles panel rendering.
    """

    def __init__(self, engine_core=None) -> None:
        if engine_core is None:
            from core.engine_core import Phase7Engine
            self.engine_core = Phase7Engine()
        else:
            self.engine_core = engine_core

    def _validate_engine_output(self, raw_output: Dict[str, Any]) -> bool:
        """
        Validate that engine output contains required sections.
        
        Args:
            raw_output: Raw engine output dictionary
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not isinstance(raw_output, dict):
            logger.error("Engine output is not a dictionary")
            return False
            
        if "error" in raw_output:
            return True  # Error states are valid
            
        required_sections = ["bias", "trend", "structure", "entry", "risk"]
        missing_sections = [section for section in required_sections if section not in raw_output]
        
        if missing_sections:
            logger.error(f"Engine output missing required sections: {missing_sections}")
            return False
            
        return True

    def route_and_execute(self, symbol: str, timeframe: str) -> Dict[str, Any]:
        """
        Executes the engine core workflow, builds the decision object, 
        and renders the output panel.
        
        Args:
            symbol: Trading symbol
            timeframe: Analysis timeframe
            
        Returns:
            Dict containing unified decision object
        """
        try:
            # Validate inputs
            if not symbol or not isinstance(symbol, str):
                return {"error": "Invalid symbol parameter"}
            if not timeframe or not isinstance(timeframe, str):
                return {"error": "Invalid timeframe parameter"}
                
            os.makedirs("Logs/Charts", exist_ok=True)
            os.makedirs("Logs", exist_ok=True)

            # Run the core engine calculations
            raw_output = self.engine_core.run(symbol, timeframe)

            # Validate engine output
            if not self._validate_engine_output(raw_output):
                return {"error": "Engine produced invalid output format"}

            if "error" in raw_output:
                return raw_output

            # Build unified decision dictionary with dynamic decision logic
            try:
                decision = self._build_decision_object(
                    symbol=symbol,
                    timeframe=timeframe,
                    bias=raw_output.get("bias", {}),
                    trend=raw_output.get("trend", {}),
                    structure=raw_output.get("structure", {}),
                    entry=raw_output.get("entry", {}),
                    risk=raw_output.get("risk", {}),
                    exit_data=raw_output.get("exit", {}),
                    macro_bias=raw_output.get("macro_bias", "NEUTRAL"),
                    chart_path=raw_output.get("chart_path", f"Logs/Charts/chart_{symbol}_{timeframe}.png")
                )
                
                return decision
                
            except Exception as e:
                logger.error(f"Failed to build decision object: {e}")
                return {"error": f"Decision object construction failed: {str(e)}"}
                
        except Exception as e:
            logger.error(f"Router execution failed: {e}")
            return {"error": f"Router execution failed: {str(e)}"}

    def route(self, symbol: str, timeframe: str) -> Dict[str, Any]:
        """
        Alias for route_and_execute to match main.py calls.
        
        Args:
            symbol: Trading symbol
            timeframe: Analysis timeframe
            
        Returns:
            Dict containing unified decision object
        """
        return self.route_and_execute(symbol, timeframe)

    def _determine_final_action(
        self, 
        bias: Dict[str, Any], 
        trend: Dict[str, Any], 
        entry: Dict[str, Any], 
        risk: Dict[str, Any], 
        macro_bias: str
    ) -> str:
        """
        Multi-factor decision engine mapping quantitative states to final trade actions:
        - LONG / CONSERVATIVE LONG / AGGRESSIVE LONG
        - SHORT / CONSERVATIVE SHORT / AGGRESSIVE SHORT
        - WAIT
        - NO-TRADE (RISK TOO HIGH)
        
        Args:
            bias: Bias analysis results
            trend: Trend analysis results
            entry: Entry analysis results
            risk: Risk analysis results
            macro_bias: Macro timeframe bias
            
        Returns:
            str: Final trading action
        """
        try:
            # Validate input dictionaries
            if not all(isinstance(d, dict) for d in [bias, trend, entry, risk]):
                logger.warning("Invalid input types for decision engine, defaulting to WAIT")
                return "WAIT"
                
            risk_valid = risk.get("risk_valid", True)
            if not risk_valid:
                return "NO-TRADE (RISK TOO HIGH)"

            validation_state = risk.get("validation_state", "NEUTRAL")
            trend_health = float(trend.get("health", trend.get("trend_health", 50.0)))
            entry_score = float(entry.get("score", 0.0))
            entry_status = str(entry.get("entry_status", ""))
            divergence = bool(trend.get("momentum_divergence", False))

            long_signal = bool(entry.get("long_signal", False))
            short_signal = bool(entry.get("short_signal", False))
            raw_bias = str(bias.get("raw", "NEUTRAL"))

            # If risk or validation state is extremely weak, hold or wait
            if validation_state == "WEAK" and trend_health < 40:
                return "WAIT"

            # Bullish Evaluation Branch
            if raw_bias == "BULLISH" or long_signal or macro_bias == "BULLISH":
                if trend_health >= 75 and entry_score >= 70 and not divergence:
                    if "ACTIVE" in entry_status.upper():
                        return "AGGRESSIVE LONG"
                    return "LONG"
                elif trend_health >= 50 and macro_bias == "BULLISH":
                    return "CONSERVATIVE LONG"

            # Bearish Evaluation Branch
            if raw_bias == "BEARISH" or short_signal or macro_bias == "BEARISH":
                if trend_health >= 75 and entry_score >= 70 and not divergence:
                    if "ACTIVE" in entry_status.upper():
                        return "AGGRESSIVE SHORT"
                    return "SHORT"
                elif trend_health >= 50 and macro_bias == "BEARISH":
                    return "CONSERVATIVE SHORT"

            # Default fallback
            return "WAIT"
            
        except Exception as e:
            logger.error(f"Decision engine failed: {e}")
            return "WAIT"

    def _build_decision_object(
        self,
        symbol: str,
        timeframe: str,
        bias: Dict[str, Any],
        trend: Dict[str, Any],
        structure: Dict[str, Any],
        entry: Dict[str, Any],
        risk: Dict[str, Any],
        exit_data: Dict[str, Any],
        macro_bias: str,
        chart_path: str
    ) -> Dict[str, Any]:
        """
        Convert engine output into a unified trade decision object.
        
        Args:
            symbol: Trading symbol
            timeframe: Analysis timeframe
            bias: Bias analysis results
            trend: Trend analysis results
            structure: Structure analysis results
            entry: Entry analysis results
            risk: Risk analysis results
            exit_data: Exit analysis results
            macro_bias: Macro timeframe bias
            chart_path: Path to generated chart
            
        Returns:
            Dict containing unified decision object
        """
        try:
            final_action = self._determine_final_action(bias, trend, entry, risk, macro_bias)

            return {
                "symbol": symbol,
                "timeframe": timeframe,
                "macro_bias": macro_bias,

                # -------------------------
                # Bias & Trend
                # -------------------------
                "bias": {
                    "raw": bias.get("raw", "NEUTRAL"),
                    "detailed": bias.get("detailed", "NEUTRAL"),
                    "score": bias.get("score", 0),
                    "regime": bias.get("regime", "NEUTRAL STRUCTURE"),
                    "volatility": bias.get("volatility", "NORMAL")
                },

                "trend": {
                    "health": trend.get("trend_health", 0),
                    "failure": trend.get("trend_failure", 0),
                    "exhaustion": trend.get("trend_exhaustion", 0),
                    "momentum": trend.get("momentum_mode", "HEALTHY"),
                    "momentum_mode": trend.get("momentum_mode", "HEALTHY"),
                    "momentum_divergence": trend.get("momentum_divergence", False)
                },

                # -------------------------
                # Structure
                # -------------------------
                "structure": {
                    "regime": structure.get("regime", "NEUTRAL"),
                    "sequence": structure.get("sequence", "NONE"),
                    "hvn": structure.get("hvn", 0.0),
                    "lvn": structure.get("lvn", 0.0),
                    "swing_struct": structure.get("swing_struct", exit_data.get("current_price", 0.0))
                },

                # -------------------------
                # Entry
                # -------------------------
                "entry": {
                    "zone_lower": entry.get("zone_lower", 0.0),
                    "zone_upper": entry.get("zone_upper", 0.0),
                    "long_signal": entry.get("long_signal", False),
                    "short_signal": entry.get("short_signal", False),
                    "score": entry.get("score", 0),
                    "distance_from_zone": entry.get("distance_from_zone", 0.0),
                    "entry_status": entry.get("entry_status", "ACTIVE ENTRY ZONE"),
                    "ema_pos_pts": entry.get("ema_pos_pts", 0),
                    "atr_dist_pts": entry.get("atr_dist_pts", 0),
                    "vwma_pts": entry.get("vwma_pts", 0),
                    "rsi_pts": entry.get("rsi_pts", 0),
                    "struct_pts": entry.get("struct_pts", 0)
                },

                # -------------------------
                # Risk
                # -------------------------
                "risk": {
                    "atr_stop": risk.get("atr_stop", 0.0),
                    "targets": risk.get("targets", (0.0, 0.0, 0.0)),
                    "risk_valid": risk.get("risk_valid", True),
                    "risk_reason": risk.get("risk_reason", "OK"),
                    "risk_score": risk.get("risk_score", 0),
                    "confidence_score": risk.get("confidence_score", bias.get("score", 0)),
                    "signal_strength": risk.get("signal_strength", bias.get("score", 0)),
                    "trade_quality_current": risk.get("trade_quality_current", 0),
                    "trade_quality_proposed": risk.get("trade_quality_proposed", 0),
                    "validation_state": risk.get("validation_state", "NEUTRAL"),
                    "validation_score": risk.get("validation_score", 50.0),
                    "validation_note": risk.get("validation_note", "Standard validation review.")
                },

                # -------------------------
                # Exit & Decision Action
                # -------------------------
                "exit": {
                    "action": final_action,
                    "current_price": exit_data.get("current_price", 0.0)
                },

                # -------------------------
                # Chart
                # -------------------------
                "chart_path": chart_path
            }
            
        except Exception as e:
            logger.error(f"Failed to build decision object: {e}")
            return {
                "symbol": symbol,
                "timeframe": timeframe,
                "error": f"Decision object construction failed: {str(e)}"
            }
