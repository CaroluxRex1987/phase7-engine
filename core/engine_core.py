import pandas as pd
from typing import Dict, Any, Optional, List
import json
import os
import logging
import traceback

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
from models.exit_model import compute_exit, build_exit_watch
from models.btc_context import compute_correlation_beta, classify_correlation, classify_stress
from utils.plotting import plot_engine_chart
from core.panel_render import render_panel

logger = logging.getLogger(__name__)


class Phase7Engine:
    """
    Phase‑7 Structural Quant Engine
    Main orchestrator for:
        - Data & Macro Confluence (MTF)
        - Indicators & Caching
        - Structure & Volume Sentiment
        - Trend Health & Bias
        - Entry Quality, Risk & Exit
        - Charting & Panel Rendering
        - BTC Market Context (informational only)
    """

    def __init__(self) -> None:
        self.bias_state_machine = BiasStateMachine()
        # Separate state machine for BTC's own bias -- BTC's detailed bias
        # is tracked independently of AERO's, since they're different assets
        # with their own history of confirmations.
        self.btc_bias_state_machine = BiasStateMachine()
        self.risk_model = RiskModel()
        # Bounded cache sizes to prevent memory leaks over long sessions
        self._indicator_cache: Dict[str, pd.DataFrame] = {}
        self._structure_cache: Dict[str, Dict[str, Any]] = {}
        self._max_cache_size: int = 15

    def _validate_dataframe(self, df: Optional[pd.DataFrame], required_columns: List[str], context: str = "") -> bool:
        """
        Validate DataFrame has required columns and sufficient data length.
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

    def _manage_cache(self, cache_dict: dict, key: str, value: Any) -> None:
        """Enforces bounded cache size limit using FIFO eviction."""
        if len(cache_dict) >= self._max_cache_size:
            oldest_key = next(iter(cache_dict))
            del cache_dict[oldest_key]
        cache_dict[key] = value

    # ============================================================
    # C3 BUILD: cross-run state persistence
    # ============================================================
    #
    # Two of the Exit Watch flags (SuperTrend flip, bias flip) are only
    # meaningful as a COMPARISON against the previous run. This tool is
    # normally invoked as a fresh command each time rather than left running
    # continuously, so in-memory instance state (like self.bias_state_machine
    # above) doesn't survive between runs -- it has to be a small file on
    # disk instead. Defensive by design: a missing or corrupt state file
    # just means "nothing to compare against yet," never a crash.

    def _state_path(self, symbol: str, timeframe: str) -> str:
        log_dir = getattr(config, "LOG_DIR", "Logs/")
        return os.path.join(log_dir, f"phase7_state_{symbol}_{timeframe}.json")

    def _load_state(self, symbol: str, timeframe: str) -> Dict[str, Any]:
        try:
            path = self._state_path(symbol, timeframe)
            if not os.path.exists(path):
                return {}
            with open(path, "r") as f:
                loaded = json.load(f)
            return loaded if isinstance(loaded, dict) else {}
        except Exception as e:
            logger.warning(f"Could not load prior engine state (first run, or file is corrupt): {e}")
            return {}

    def _save_state(self, symbol: str, timeframe: str, state: Dict[str, Any]) -> None:
        try:
            log_dir = getattr(config, "LOG_DIR", "Logs/")
            os.makedirs(log_dir, exist_ok=True)
            path = self._state_path(symbol, timeframe)
            with open(path, "w") as f:
                json.dump(state, f)
        except Exception as e:
            logger.warning(f"Could not persist engine state for next run's Exit Watch comparison: {e}")

    def run(
        self,
        symbol: Optional[str] = None,
        timeframe: Optional[str] = None,
        limit: int = 450,
        save_chart: bool = True,
        render: bool = True
    ) -> Dict[str, Any]:
        """
        Execute full engine pipeline with Multi-Timeframe Confluence and safe error containment.
        """
        symbol = symbol or config.SYMBOL
        timeframe = timeframe or config.TIMEFRAME
        macro_tf = getattr(config, "MACRO_TIMEFRAME", "1d")
        required_base_cols = ["open", "high", "low", "close", "volume"]

        # C3: load whatever was persisted from the last run (for the
        # SuperTrend-flip / bias-flip Exit Watch comparisons below).
        prior_state = self._load_state(symbol, timeframe)

        try:
            # 1. FETCH EXECUTION DATA
            df = data_fetcher.get_tf(symbol, timeframe, limit=limit)

            if not self._validate_dataframe(df, required_base_cols, "base market data"):
                # A13 FIX: distinguish a genuine data-fetch/API failure from an
                # ordinary "insufficient data" condition, instead of both
                # collapsing into the same generic message (which looked
                # identical to a normal no-signal HOLD in the panel).
                fetch_error = df.attrs.get("fetch_error") if df is not None else None
                error_message = (
                    f"Data fetch failed: {fetch_error}"
                    if fetch_error
                    else "Invalid or insufficient market data"
                )
                decision_object = {
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "error": error_message,
                }
                if render:
                    render_panel(decision_object)
                return decision_object

            cache_key = f"{symbol}_{timeframe}_{len(df)}_{df['close'].iloc[-1]}"

            # 1b. FETCH MACRO DATA (Multi-Timeframe Confluence)
            df_macro = data_fetcher.get_tf(symbol, macro_tf, limit=100)
            macro_bias = "NEUTRAL"

            if self._validate_dataframe(df_macro, required_base_cols, "macro timeframe data"):
                try:
                    df_macro = add_technical_indicators(df_macro)
                    if "EMA_50" in df_macro.columns:
                        macro_close = float(df_macro["close"].iloc[-1])
                        macro_ema50 = float(df_macro["EMA_50"].iloc[-1])

                        if macro_close > macro_ema50:
                            macro_bias = "BULLISH"
                        elif macro_close < macro_ema50:
                            macro_bias = "BEARISH"
                except Exception as e:
                    logger.warning(f"Failed to process macro timeframe data: {e}")
                    macro_bias = "NEUTRAL"

            # 2. INDICATORS (with bounded caching)
            try:
                if cache_key in self._indicator_cache:
                    logger.debug("Using cached indicators")
                    df = self._indicator_cache[cache_key]
                else:
                    df = add_technical_indicators(df)
                    self._manage_cache(self._indicator_cache, cache_key, df.copy())

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

            # 3. STRUCTURE ENGINE (leveraging structure.py optimizations)
            try:
                struct_cache_key = f"struct_{cache_key}"
                if struct_cache_key in self._structure_cache:
                    logger.debug("Using cached structure analysis")
                    structure_obj = self._structure_cache[struct_cache_key]
                else:
                    structure_obj = calculate_structure(
                        df, lookback=getattr(config, "STRUCT_LOOKBACK", 8), copy_df=False
                    )
                    if not isinstance(structure_obj, dict):
                        raise ValueError("Structure engine returned invalid format")
                    self._manage_cache(self._structure_cache, struct_cache_key, structure_obj)

                df_struct = structure_obj.get("df", df)

                if not self._validate_dataframe(df_struct, required_indicators, "structure analysis"):
                    raise ValueError("Structure analysis produced invalid DataFrame")

                structure_regime = structure_obj.get("regime", "NEUTRAL STRUCTURE")
                trend_sequence = structure_obj.get("sequence", "NONE")
                volume_sentiment = structure_obj.get("volume_sentiment", "NEUTRAL VOLUME")
                # A6-adjacent FIX: swing_struct was computed by structure.py but never
                # extracted here, so it never made it into the decision object / panel.
                swing_struct = structure_obj.get("swing_struct", 0.0)

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
                trend = {
                    "trend_health": 50.0,
                    "trend_failure": False,
                    "trend_exhaustion": False,
                    "momentum_mode": "NEUTRAL",
                    "momentum_divergence": False
                }

            # 5. BIAS ENGINE
            # Roadmap Layer 2: bias_engine.py's weighted blend now uses three
            # more factors that were already available here but never passed
            # through -- structure_regime, volume_sentiment, and macro_bias
            # (all computed above), plus SuperTrend direction (extracted here).
            supertrend_direction = float(df_struct["ST_Direction"].iloc[-1]) if "ST_Direction" in df_struct.columns else 0.0

            raw_bias, bias_score = calculate_dynamic_bias(
                df=df_struct,
                trend_sequence=trend_sequence,
                trend_health=trend["trend_health"],
                trend_failure=trend["trend_failure"],
                trend_exhaustion=trend["trend_exhaustion"],
                reversal_direction=trend.get("reversal_direction"),
                reversal_strength=trend.get("reversal_strength", 0),
                continuation_strength=trend.get("continuation_strength"),
                structure_regime=structure_regime,
                volume_sentiment=volume_sentiment,
                supertrend_direction=supertrend_direction,
                macro_bias=macro_bias,
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
            hvn = float(df_struct["HVN"].iloc[-1]) if "HVN" in df_struct.columns else float(structure_obj.get("hvn", 0.0))
            lvn = float(df_struct["LVN"].iloc[-1]) if "LVN" in df_struct.columns else float(structure_obj.get("lvn", 0.0))

            structure = {
                "regime": structure_regime,
                "sequence": trend_sequence,
                "hvn": hvn,
                "lvn": lvn,
                "volume_sentiment": volume_sentiment,
                # A6-adjacent FIX: now propagated through to the decision object
                # instead of being dropped, so panel_render.py's SWING STRUCT line
                # reflects the real value from structure.py (still current_price
                # today per the A7 stub, but wired correctly for when B2 lands).
                "swing_struct": swing_struct,
            }

            # 6b. BTC MARKET CONTEXT (new feature, informational only).
            #
            # This NEVER changes BIAS, DECISION, entry, risk, or targets
            # above -- per the explicit requirement this was built to: BTC
            # context is additive, never a replacement or distortion of the
            # AERO-only analysis. It reuses the exact same, already-tested
            # indicators/structure/trend_health/bias_engine functions above,
            # just run a second time on BTC's own data, plus a correlation +
            # beta reading between AERO and BTC. Wrapped end-to-end so any
            # failure here (bad fetch, bad data) can never break or alter
            # the AERO panel -- it just falls back to "unavailable."
            btc_context = {"available": False}
            try:
                if symbol.upper() != "BTCUSDT":
                    df_btc = data_fetcher.get_tf("BTCUSDT", timeframe, limit=limit)
                    if self._validate_dataframe(df_btc, required_base_cols, "BTC context data"):
                        df_btc = add_technical_indicators(df_btc)
                        btc_structure_obj = calculate_structure(
                            df_btc, lookback=getattr(config, "STRUCT_LOOKBACK", 8), copy_df=False
                        )
                        df_btc_struct = btc_structure_obj.get("df", df_btc)
                        btc_trend = compute_trend_health(df_btc_struct)

                        btc_supertrend_direction = (
                            float(df_btc_struct["ST_Direction"].iloc[-1])
                            if "ST_Direction" in df_btc_struct.columns else 0.0
                        )
                        btc_raw_bias, btc_bias_score = calculate_dynamic_bias(
                            df=df_btc_struct,
                            trend_sequence=btc_structure_obj.get("sequence", "NONE"),
                            trend_health=btc_trend["trend_health"],
                            trend_failure=btc_trend["trend_failure"],
                            trend_exhaustion=btc_trend["trend_exhaustion"],
                            reversal_direction=btc_trend.get("reversal_direction"),
                            reversal_strength=btc_trend.get("reversal_strength", 0),
                            continuation_strength=btc_trend.get("continuation_strength"),
                            structure_regime=btc_structure_obj.get("regime", "NEUTRAL STRUCTURE"),
                            volume_sentiment=btc_structure_obj.get("volume_sentiment", "NEUTRAL VOLUME"),
                            supertrend_direction=btc_supertrend_direction,
                            # V1: BTC's own macro-timeframe confluence isn't fetched
                            # separately yet (a third API call for diminishing
                            # returns at this stage) -- straightforward to add later.
                            macro_bias="NEUTRAL",
                        )
                        btc_dynamic_regime, btc_volatility_mode = calculate_dynamic_regime(df_btc_struct)
                        btc_detailed_bias = self.btc_bias_state_machine.transition(btc_raw_bias, btc_bias_score)

                        correlation, beta, n_obs = compute_correlation_beta(
                            df_struct["close"], df_btc_struct["close"], window=30
                        )

                        btc_context = {
                            "available": True,
                            "raw": btc_raw_bias,
                            "detailed": btc_detailed_bias,
                            "score": float(btc_bias_score),
                            "regime": btc_dynamic_regime,
                            "volatility": btc_volatility_mode,
                            "trend_health": float(btc_trend["trend_health"]),
                            "correlation": correlation,
                            "correlation_label": classify_correlation(correlation),
                            "beta": beta,
                            "broad_market_stress": classify_stress(btc_volatility_mode),
                            "n_observations": n_obs,
                        }
            except Exception as e:
                logger.warning(f"BTC context analysis failed (AERO analysis above is unaffected): {e}")
                btc_context = {"available": False}

            # 7. ENTRY MODEL & ENTRY QUALITY ENGINE
            long_signal, short_signal = generate_entry_signals(
                detailed_bias=detailed_bias,
                structure_regime=structure_regime,
                trend_health=trend["trend_health"],
                trend_failure=trend["trend_failure"],
                trend_exhaustion=trend["trend_exhaustion"],
                reversal_strength=trend.get("reversal_strength", 0),
                macro_bias=macro_bias,
            )

            entry_zone_lower = float(df_struct["EMA_20"].iloc[-1]) if "EMA_20" in df_struct.columns else float(df_struct["close"].iloc[-1] * 0.99)
            entry_zone_upper = float(df_struct["EMA_50"].iloc[-1]) if "EMA_50" in df_struct.columns else float(df_struct["close"].iloc[-1] * 1.01)

            # A6-adjacent FIX: calculate_entry_quality() accepts macro_bias and
            # trade_direction to apply its macro-confluence multiplier, but neither
            # was ever passed, so that multiplier silently defaulted to neutral/LONG
            # every call. Now derives trade_direction from whichever signal (if any)
            # is active and passes the real macro_bias through.
            #
            # Roadmap Layer 5: also passes trend_direction (trend_health.py) and
            # structure_sequence (structure.py's B2 sequence, already computed
            # above as trend_sequence) through, so entry quality's own multipliers
            # can factor in whether the granular trend/structure context actually
            # supports this specific trade direction.
            eq_trade_direction = "SHORT" if short_signal else "LONG"
            eq_metrics = calculate_entry_quality(
                df_struct,
                entry_zone_lower,
                entry_zone_upper,
                macro_bias=macro_bias,
                trade_direction=eq_trade_direction,
                trend_direction=trend.get("trend_direction", "NEUTRAL"),
                structure_sequence=trend_sequence,
            )

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

            # 8. RISK MODEL & VALIDATION ENGINE
            current_price = float(df_struct["close"].iloc[-1])
            atr_val = float(df_struct["ATR"].iloc[-1]) if "ATR" in df_struct.columns else (current_price * 0.02)

            atr_stop, t1, t2, t3 = self.risk_model.calculate_stop_targets(
                detailed_bias=detailed_bias,
                trend_health=trend["trend_health"],
                current_price=current_price,
                atr_val=atr_val,
                structural_level=hvn,
                bias_score=bias_score,
            )

            # A6 FIX: previously called with a bogus reference_price=current_price
            # kwarg (silently absorbed by **kwargs, doing nothing) and never passed
            # volatility_state/trend_health, so risk validation always ran against
            # the function's hardcoded defaults ("NORMAL", 50.0) regardless of
            # actual market conditions. Now passes the real, current values.
            risk_valid, risk_reason = self.risk_model.validate_risk_parameters(
                current_price=current_price,
                atr_stop=atr_stop,
                volatility_state=volatility_mode,
                trend_health=trend["trend_health"],
            )

            # C4 BUILD: position size, displayed for you to read -- the
            # engine never sizes or places a trade itself. Uses the risk
            # settings from config.py (DEFAULT_ACCOUNT_BALANCE /
            # DEFAULT_RISK_PERCENT) so this reflects a fixed, known risk
            # budget rather than any real connected account.
            account_balance = float(getattr(config, "DEFAULT_ACCOUNT_BALANCE", 10_000))
            risk_percent = float(getattr(config, "DEFAULT_RISK_PERCENT", 1.0))
            position_size = self.risk_model.calculate_position_size(
                account_balance=account_balance,
                risk_percent=risk_percent,
                current_price=current_price,
                atr_stop=atr_stop,
                volatility_state=volatility_mode,
            )
            risk_amount = account_balance * (risk_percent / 100.0)
            position_value = position_size * current_price

            # Validation Engine Metrics
            trend_health = float(trend.get("trend_health", 50.0))
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
                # C4 BUILD: displayed only -- the engine doesn't act on these.
                "position_size": position_size,
                "position_value": position_value,
                "risk_amount": risk_amount,
                "account_balance": account_balance,
                "risk_percent": risk_percent,
            }

            # 9. EXIT MODEL
            exit_data = compute_exit(
                price_data=df_struct,
                entry_data=entry,
                risk_data=risk,
            )

            # C3 BUILD: Exit Watch -- advisory-only flags (see exit_model.py's
            # build_exit_watch docstring). Uses prior_state (loaded at the top
            # of this run) for the two flags that need a run-over-run
            # comparison (SuperTrend flip, bias flip).
            exit_watch = build_exit_watch(
                trend=trend,
                structure=structure,
                bias=bias,
                current_price=current_price,
                supertrend_direction=supertrend_direction,
                target_t1=t1,
                prior_state=prior_state,
            )

            # Persist this run's state so the NEXT run can detect a
            # SuperTrend flip / bias flip against it.
            self._save_state(
                symbol, timeframe,
                {"supertrend_direction": supertrend_direction, "detailed_bias": detailed_bias},
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
                "exit_watch": exit_watch,
                "btc_context": btc_context,
                "chart_path": chart_path,
            }

            if render:
                render_panel(decision_object)

            return decision_object

        except Exception as e:
            logger.error(f"Critical error in Phase7Engine pipeline: {e}")
            traceback.print_exc()
            decision_object = {
                "symbol": symbol,
                "timeframe": timeframe,
                "error": str(e),
            }
            if render:
                render_panel(decision_object)
            return decision_object