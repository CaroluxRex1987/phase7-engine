import os
from typing import Dict, Any, Optional, List
import logging

from core.panel_render import render_panel
from models.decision_model import DecisionModel

logger = logging.getLogger(__name__)

class SignalRouter:
    """
    Routes raw engine data into unified decision objects and handles panel rendering.

    ROADMAP LAYER 1 FIX: this router previously contained its own decision
    logic (_determine_final_action) -- diagnosed in the original roadmap as
    architecturally wrong ("Router contains decision logic (should not)").
    That logic now lives in models/decision_model.py; this router is a pure
    assembler: run the engine, call DecisionModel.evaluate(...), assemble
    the unified decision object, render it.
    """

    def __init__(self, engine_core: Optional[Any] = None, decision_model: Optional[DecisionModel] = None) -> None:
        if engine_core is None:
            from core.engine_core import Phase7Engine
            self.engine_core = Phase7Engine()
        else:
            self.engine_core = engine_core

        self.decision_model = decision_model if decision_model is not None else DecisionModel()

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
            return True  # Error states are valid data payloads containing failure notices

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
                error_obj = {"error": "Invalid symbol parameter"}
                render_panel(error_obj)
                return error_obj
            if not timeframe or not isinstance(timeframe, str):
                error_obj = {"error": "Invalid timeframe parameter"}
                render_panel(error_obj)
                return error_obj

            os.makedirs("Logs/Charts", exist_ok=True)
            os.makedirs("Logs", exist_ok=True)

            # THIS router owns rendering exclusively (see class docstring / C1
            # fix), using the one complete decision object as the single source
            # of truth for the panel.
            #
            # SEQUENCE ITEM 5b: the call used to pass render=False. That
            # parameter is gone -- engine_core no longer renders at all, so the
            # exclusivity this comment asserts is now enforced by the code
            # rather than by every caller remembering to ask for it.
            raw_output = self.engine_core.run(symbol, timeframe)

            # Validate engine output format
            if not self._validate_engine_output(raw_output):
                error_obj = {"error": "Engine produced invalid output format"}
                render_panel(error_obj)
                return error_obj

            if "error" in raw_output:
                render_panel(raw_output)
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
                    exit_watch=raw_output.get("exit_watch", []),
                    btc_context=raw_output.get("btc_context", {}),
                    macro_bias=raw_output.get("macro_bias", "NEUTRAL"),
                    chart_path=raw_output.get("chart_path", f"Logs/Charts/chart_{symbol}_{timeframe}.png")
                )

                logger.info(f"Signal router successfully processed {symbol} [{timeframe}] -> Action: {decision.get('exit', {}).get('action', 'UNKNOWN')}")
                render_panel(decision)
                return decision

            except Exception as e:
                logger.error(f"Failed to build decision object: {e}")
                error_obj = {"error": f"Decision object construction failed: {str(e)}"}
                render_panel(error_obj)
                return error_obj

        except Exception as e:
            logger.error(f"Router execution failed: {e}")
            error_obj = {"error": f"Router execution failed: {str(e)}"}
            render_panel(error_obj)
            return error_obj

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
        chart_path: str,
        exit_watch: Optional[List[Any]] = None,
        btc_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Convert engine output into a unified trade decision object.
        Pure assembly: all decision logic (final_action, confidence,
        trade_quality, ev, btc_adjusted, explanation) comes from
        self.decision_model.evaluate().
        """
        try:
            dm_result = self.decision_model.evaluate(bias, trend, structure, entry, risk, macro_bias, btc_context)
            final_action = dm_result["final_action"]
            confidence = dm_result["confidence"]
            trade_quality = dm_result["trade_quality"]
            ev = dm_result["ev"]
            btc_adjusted = dm_result["btc_adjusted"]
            explanation = dm_result["explanation"]

            # Defensive normalization for targets tuple
            targets = risk.get("targets", (0.0, 0.0, 0.0))
            if not isinstance(targets, (list, tuple)) or len(targets) < 3:
                targets = (0.0, 0.0, 0.0)

            return {
                "symbol": symbol,
                "timeframe": timeframe,
                "macro_bias": macro_bias,

                "bias": {
                    "raw": str(bias.get("raw", "NEUTRAL")),
                    "detailed": str(bias.get("detailed", "NEUTRAL")),
                    "score": float(bias.get("score", 0.0)),
                    "regime": str(bias.get("regime", "NEUTRAL STRUCTURE")),
                    "volatility": str(bias.get("volatility", "NORMAL"))
                },

                "trend": {
                    "health": float(trend.get("trend_health", 0.0)),
                    "trend_health": float(trend.get("trend_health", 0.0)),
                    "failure": bool(trend.get("trend_failure", False)),
                    "exhaustion": bool(trend.get("trend_exhaustion", False)),
                    "momentum": str(trend.get("momentum_mode", "HEALTHY")),
                    "momentum_mode": str(trend.get("momentum_mode", "HEALTHY")),
                    "momentum_divergence": bool(trend.get("momentum_divergence", False)),
                    # New: explicit BULLISH/BEARISH/NEUTRAL direction label
                    # from trend_health.py, passed straight through.
                    "trend_direction": str(trend.get("trend_direction", "NEUTRAL")),
                },

                "structure": {
                    "regime": str(structure.get("regime", "NEUTRAL")),
                    "sequence": str(structure.get("sequence", "NONE")),
                    "hvn": float(structure.get("hvn", 0.0)),
                    "lvn": float(structure.get("lvn", 0.0)),
                    "volume_sentiment": str(structure.get("volume_sentiment", "NEUTRAL VOLUME")),
                    "swing_struct": float(structure.get("swing_struct", exit_data.get("current_price", 0.0)))
                },

                "entry": {
                    "zone_lower": float(entry.get("zone_lower", 0.0)),
                    "zone_upper": float(entry.get("zone_upper", 0.0)),
                    "long_signal": bool(entry.get("long_signal", False)),
                    "short_signal": bool(entry.get("short_signal", False)),
                    "score": float(entry.get("score", 0.0)),
                    "distance_from_zone": float(entry.get("distance_from_zone", 0.0)),
                    "entry_status": str(entry.get("entry_status", "ACTIVE ENTRY ZONE")),
                    "ema_pos_pts": float(entry.get("ema_pos_pts", 0.0)),
                    "atr_dist_pts": float(entry.get("atr_dist_pts", 0.0)),
                    "vwma_pts": float(entry.get("vwma_pts", 0.0)),
                    "rsi_pts": float(entry.get("rsi_pts", 0.0)),
                    "struct_pts": float(entry.get("struct_pts", 0.0))
                },

                "risk": {
                    "atr_stop": float(risk.get("atr_stop", 0.0)),
                    "targets": (float(targets[0]), float(targets[1]), float(targets[2])),
                    "risk_valid": bool(risk.get("risk_valid", True)),
                    "risk_reason": str(risk.get("risk_reason", "OK")),
                    "risk_score": float(risk.get("risk_score", 0.0)),
                    # ROADMAP LAYER 1 FIX: confidence_score and the two
                    # trade_quality_* fields are now DecisionModel's real,
                    # multi-factor outputs (see models/decision_model.py)
                    # instead of engine_core.py's raw trend_health
                    # passthrough. Field names/paths kept identical so
                    # panel_render.py needs no changes to consume them.
                    "confidence_score": float(confidence),
                    "signal_strength": float(risk.get("signal_strength", bias.get("score", 0.0))),
                    "trade_quality_current": float(trade_quality["current_market"]),
                    "trade_quality_proposed": float(trade_quality["proposed_entry"]),
                    "validation_state": str(risk.get("validation_state", "NEUTRAL")),
                    "validation_score": float(risk.get("validation_score", 50.0)),
                    "validation_note": str(risk.get("validation_note", "Standard validation review.")),

                    # C4 BUILD: displayed-only position sizing (from
                    # engine_core.py, using config.py's risk settings) and
                    # an illustrative EV estimate (from DecisionModel,
                    # since it needs the confidence score above). Neither
                    # of these causes the engine to size or place a trade.
                    "position_size": float(risk.get("position_size", 0.0)),
                    "position_value": float(risk.get("position_value", 0.0)),
                    "risk_amount": float(risk.get("risk_amount", 0.0)),
                    "account_balance": float(risk.get("account_balance", 0.0)),
                    "risk_percent": float(risk.get("risk_percent", 0.0)),
                    "ev_r": float(ev.get("ev_r", 0.0)),
                    "assumed_win_rate": float(ev.get("assumed_win_rate", 0.0)),
                    "avg_reward_r": float(ev.get("avg_reward_r", 2.0)),
                },

                "exit": {
                    "action": final_action,
                    "current_price": float(exit_data.get("current_price", 0.0))
                },

                # C3 BUILD: advisory-only Exit Watch flags, passed straight
                # through from engine_core.py -- see exit_model.py's
                # build_exit_watch() for what feeds into this.
                "exit_watch": list(exit_watch) if isinstance(exit_watch, list) else [],

                # BTC MARKET CONTEXT (new feature, V1): merges engine_core.py's
                # BTC-side analysis (bias/regime/correlation/beta) with
                # DecisionModel's BTC-adjusted confidence -- informational
                # only, never changes BIAS/DECISION/confidence above.
                "btc_context": self._merge_btc_context(btc_context, btc_adjusted),

                "explanation": explanation,

                "chart_path": str(chart_path)
            }

        except Exception as e:
            logger.error(f"Failed to build decision object layout: {e}")
            return {
                "symbol": symbol,
                "timeframe": timeframe,
                "error": f"Decision object construction failed: {str(e)}"
            }

    def _merge_btc_context(
        self,
        btc_context: Optional[Dict[str, Any]],
        btc_adjusted: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Combines engine_core.py's BTC-side analysis (bias/regime/volatility/
        correlation/beta) with DecisionModel's BTC-adjusted confidence into
        one dict for panel_render.py -- kept as a single merge point so
        panel_render.py doesn't need to know these came from two different
        places.
        """
        btc_context = btc_context if isinstance(btc_context, dict) else {}
        btc_adjusted = btc_adjusted if isinstance(btc_adjusted, dict) else {}

        if not btc_context.get("available") or not btc_adjusted.get("available"):
            return {"available": False}

        return {
            "available": True,
            "raw": str(btc_context.get("raw", "NEUTRAL")),
            "detailed": str(btc_context.get("detailed", "NEUTRAL")),
            "regime": str(btc_context.get("regime", "NEUTRAL STRUCTURE")),
            "volatility": str(btc_context.get("volatility", "NORMAL")),
            "trend_health": float(btc_context.get("trend_health", 0.0)),
            "correlation": float(btc_context.get("correlation", 0.0)),
            "correlation_label": str(btc_context.get("correlation_label", "WEAK / NO CLEAR RELATIONSHIP")),
            "beta": float(btc_context.get("beta", 0.0)),
            "broad_market_stress": bool(btc_context.get("broad_market_stress", False)),
            "n_observations": int(btc_context.get("n_observations", 0) or 0),
            "btc_adjusted_confidence": float(btc_adjusted.get("btc_adjusted_confidence", 0.0)),
            "reasons": list(btc_adjusted.get("reasons", [])),
        }