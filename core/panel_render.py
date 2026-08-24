import logging

logger = logging.getLogger(__name__)

# Safe colorama import with fallback
try:
    from colorama import init, Fore, Style
    # Initialize colorama for Windows and cross-platform compatibility
    init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    logger.warning("Colorama not available, using plain text output")
    COLORAMA_AVAILABLE = False
    # Create dummy color classes for fallback
    class DummyColor:
        def __getattr__(self, name):
            return ""
    Fore = DummyColor()
    Style = DummyColor()

def render_panel(decision):
    """
    Renders a Phase7 decision object into an advanced, color-coded
    structured text terminal panel with comprehensive error handling.
    """

    try:
        # Validate input
        if not isinstance(decision, dict):
            error_msg = f"Invalid decision object type: {type(decision)}"
            logger.error(error_msg)
            print(f"\n[ERROR] {error_msg}")
            return

        # Handle error state
        if "error" in decision:
            error_msg = decision['error']
            if COLORAMA_AVAILABLE:
                print(f"\n{Fore.RED}[ERROR] {error_msg}{Style.RESET_ALL}")
            else:
                print(f"\n[ERROR] {error_msg}")
            return

    except Exception as e:
        logger.error(f"Failed to validate decision object: {e}")
        print(f"\n[ERROR] Failed to process decision object: {e}")
        return

    try:
        # Basic metadata with safe extraction
        symbol = str(decision.get("symbol", "AEROUSDT"))
        timeframe = str(decision.get("timeframe", "4h"))
        macro_bias = str(decision.get("macro_bias", "NEUTRAL"))

        # Extract sections with safe defaults
        bias = decision.get("bias", {})
        trend = decision.get("trend", {})
        structure = decision.get("structure", {})
        entry = decision.get("entry", {})
        risk = decision.get("risk", {})
        exit_data = decision.get("exit", {})

        # Ensure all sections are dictionaries
        for section_name, section_data in [("bias", bias), ("trend", trend), ("structure", structure), 
                                         ("entry", entry), ("risk", risk), ("exit", exit_data)]:
            if not isinstance(section_data, dict):
                logger.warning(f"Section '{section_name}' is not a dictionary, using empty dict")
                if section_name == "bias":
                    bias = {}
                elif section_name == "trend":
                    trend = {}
                elif section_name == "structure":
                    structure = {}
                elif section_name == "entry":
                    entry = {}
                elif section_name == "risk":
                    risk = {}
                elif section_name == "exit":
                    exit_data = {}

        # Safe numeric extraction with error handling
        def safe_float(value, default=0.0):
            try:
                return float(value) if value is not None else default
            except (ValueError, TypeError):
                return default

        # Targets with safe extraction
        targets = risk.get("targets", (0, 0, 0))
        if isinstance(targets, (list, tuple)) and len(targets) >= 3:
            t1, t2, t3 = safe_float(targets[0]), safe_float(targets[1]), safe_float(targets[2])
        else:
            t1, t2, t3 = 0.0, 0.0, 0.0

        current_price = safe_float(exit_data.get("current_price", 0.0))
        stop_loss = safe_float(risk.get("atr_stop", 0.0))

        # Risk amount for R:R with division by zero protection
        risk_amount = abs(current_price - stop_loss) if stop_loss and current_price else 0.0

        if risk_amount > 0:
            rr_t1 = abs(t1 - current_price) / risk_amount
            rr_t2 = abs(t2 - current_price) / risk_amount
            rr_t3 = abs(t3 - current_price) / risk_amount
        else:
            rr_t1 = rr_t2 = rr_t3 = 0.0

        # Formatted scores with safe conversion
        risk_score = safe_float(risk.get('risk_score', 0))
        entry_score = safe_float(entry.get('score', 0))
        confidence_score = safe_float(risk.get('confidence_score', 0))
        tq_current = safe_float(risk.get('trade_quality_current', 0))
        tq_proposed = safe_float(risk.get('trade_quality_proposed', 0))
        trend_health_score = safe_float(trend.get('trend_health', 0))

    except Exception as e:
        logger.error(f"Failed to extract panel data: {e}")
        print(f"\n[ERROR] Failed to extract panel data: {e}")
        return

    try:
        # Helper for color-coding text values with fallback
        def colorize_val(val):
            try:
                val_str = str(val).upper()
                if not COLORAMA_AVAILABLE:
                    return str(val)
                    
                if "BULLISH" in val_str or "LONG" in val_str or "HEALTHY" in val_str or "STRONG" in val_str:
                    return f"{Fore.GREEN}{val}{Style.RESET_ALL}"
                elif "BEARISH" in val_str or "SHORT" in val_str or "WEAK" in val_str:
                    return f"{Fore.RED}{val}{Style.RESET_ALL}"
                elif "NEUTRAL" in val_str or "WAIT" in val_str or "NORMAL" in val_str:
                    return f"{Fore.YELLOW}{val}{Style.RESET_ALL}"
                return f"{Fore.CYAN}{val}{Style.RESET_ALL}"
            except Exception:
                return str(val)

        action_val = str(exit_data.get('action', 'WAIT'))
        
        if COLORAMA_AVAILABLE:
            if action_val == "LONG":
                colored_action = f"{Fore.GREEN}{action_val}{Style.RESET_ALL}"
            elif action_val == "SHORT":
                colored_action = f"{Fore.RED}{action_val}{Style.RESET_ALL}"
            else:
                colored_action = f"{Fore.YELLOW}{action_val}{Style.RESET_ALL}"
            # ANSI code for Orange text
            ORANGE = "\033[38;5;214m"
        else:
            colored_action = action_val
            ORANGE = ""

    except Exception as e:
        logger.error(f"Failed to setup color formatting: {e}")
        # Fallback to plain text
        def colorize_val(val):
            return str(val)
        colored_action = str(exit_data.get('action', 'WAIT'))
        ORANGE = ""

    try:
        # Build panel with error handling and color fallback
        if COLORAMA_AVAILABLE:
            panel = (
                f"\n{Fore.CYAN}Connecting to MEXC API for {symbol} ({timeframe}) - Phase-7.3 Structural Quant Engine...{Style.RESET_ALL}\n\n"
                f"{Fore.MAGENTA}=========================================================================\n"
                f"    PHASE-7 STRUCTURAL DYNAMIC ENTRY QUALITY ENGINE\n"
                f"========================================================================={Style.RESET_ALL}\n\n"
                f"BIAS       : {colorize_val(bias.get('detailed', bias.get('raw', 'NEUTRAL')))}\n"
                f"REGIME     : {colorize_val(bias.get('regime', 'NEUTRAL STRUCTURE'))}\n"
                f"STRUCTURE  : {colorize_val(structure.get('regime', 'NEUTRAL'))} | Vol: {colorize_val(bias.get('volatility', 'NORMAL'))}\n"
                f"TREND      : {colorize_val(trend.get('momentum_mode', 'HEALTHY'))} (Score: {trend_health_score:.2f})\n"
                f"MOMENTUM   : {colorize_val(trend.get('momentum_mode', 'HEALTHY'))} ({trend_health_score:.2f})\n"
                f"VOLUME     : {colorize_val(structure.get('volume_sentiment', 'WEAK OR CONTRARY VOLUME'))}\n"
                f"VALIDATION : {colorize_val(risk.get('validation_state', 'WEAK'))} (Score: {risk_score:.2f})\n"
                f"VOLATILITY : {colorize_val(bias.get('volatility', 'LOW'))}\n"
                f"MACRO TREND: {colorize_val(macro_bias)}\n\n"
                f"{Style.DIM}-------------------------------------------------------------------------{Style.RESET_ALL}\n"
                f"CURRENT PRICE : {ORANGE}${current_price:.4f}{Style.RESET_ALL}\n"
                f"ENTRY ZONE    : {Fore.CYAN}${safe_float(entry.get('zone_lower', 0)):.4f} - ${safe_float(entry.get('zone_upper', 0)):.4f}{Style.RESET_ALL}\n"
                f"ZONE DISTANCE : {safe_float(entry.get('distance_from_zone', 0.0)):.2f}% away from zone\n"
                f"STATUS        : {colorize_val(entry.get('entry_status', 'ACTIVE ENTRY ZONE'))}\n"
                f"SWING STRUCT  : ${safe_float(structure.get('swing_struct', current_price)):.4f} (Lookback 8)\n"
                f"STOP LOSS     : {Fore.RED}${stop_loss:.4f}{Style.RESET_ALL}\n"
                f"TARGET 1 (Cons): {Fore.GREEN}${t1:.4f}{Style.RESET_ALL} | R:R 1 : {rr_t1:.2f}\n"
                f"TARGET 2 (Norm): {Fore.GREEN}${t2:.4f}{Style.RESET_ALL} | R:R 1 : {rr_t2:.2f}\n"
                f"TARGET 3 (Aggr): {Fore.GREEN}${t3:.4f}{Style.RESET_ALL} | R:R 1 : {rr_t3:.2f}\n\n"
                f"{Style.DIM}-------------------------------------------------------------------------{Style.RESET_ALL}\n"
                f"ENTRY QUALITY : {entry_score:.2f}/100\n"
                f"    |-- EMA Zone Position : {safe_float(entry.get('ema_pos_pts', 22)):.0f}/30\n"
                f"    |-- ATR Distance      : {safe_float(entry.get('atr_dist_pts', 10)):.0f}/25\n"
                f"    |-- VWMA Distance     : {safe_float(entry.get('vwma_pts', 20)):.0f}/20\n"
                f"    |-- RSI Extension     : {safe_float(entry.get('rsi_pts', 15)):.0f}/15\n"
                f"    |-- Structure         : {safe_float(entry.get('struct_pts', 2)):.0f}/12\n\n"
                f"{Style.DIM}-------------------------------------------------------------------------{Style.RESET_ALL}\n"
                f"CONFIDENCE    : {confidence_score:.2f}/100\n"
                f"TRADE QUALITY :\n"
                f"    |-- Current Market    : {tq_current:.2f}/100\n"
                f"    |-- Proposed Entry    : {tq_proposed:.2f}/100\n\n"
                f"{Fore.MAGENTA}=========================================================================\n"
                f"DECISION      : {colored_action}\n\n"
                f"-------------------------------------------------------------------------\n"
                f"Validation Notes:\n"
                f" - {risk.get('validation_note', 'VWMA volume trend is pointing down.')}\n"
                f"========================================================================={Style.RESET_ALL}\n\n"
                f"Trade logged to Logs/phase7_trade_log_{symbol.lower()}.csv\n"
                f"AI Risk chart saved to {decision.get('chart_path', 'Logs/Charts/chart.png')}\n"
            )
        else:
            # Plain text fallback
            panel = (
                f"\nConnecting to MEXC API for {symbol} ({timeframe}) - Phase-7.3 Structural Quant Engine...\n\n"
                f"=========================================================================\n"
                f"    PHASE-7 STRUCTURAL DYNAMIC ENTRY QUALITY ENGINE\n"
                f"=========================================================================\n\n"
                f"BIAS       : {bias.get('detailed', bias.get('raw', 'NEUTRAL'))}\n"
                f"REGIME     : {bias.get('regime', 'NEUTRAL STRUCTURE')}\n"
                f"STRUCTURE  : {structure.get('regime', 'NEUTRAL')} | Vol: {bias.get('volatility', 'NORMAL')}\n"
                f"TREND      : {trend.get('momentum_mode', 'HEALTHY')} (Score: {trend_health_score:.2f})\n"
                f"MOMENTUM   : {trend.get('momentum_mode', 'HEALTHY')} ({trend_health_score:.2f})\n"
                f"VOLUME     : {structure.get('volume_sentiment', 'WEAK OR CONTRARY VOLUME')}\n"
                f"VALIDATION : {risk.get('validation_state', 'WEAK')} (Score: {risk_score:.2f})\n"
                f"VOLATILITY : {bias.get('volatility', 'LOW')}\n"
                f"MACRO TREND: {macro_bias}\n\n"
                f"-------------------------------------------------------------------------\n"
                f"CURRENT PRICE : ${current_price:.4f}\n"
                f"ENTRY ZONE    : ${safe_float(entry.get('zone_lower', 0)):.4f} - ${safe_float(entry.get('zone_upper', 0)):.4f}\n"
                f"ZONE DISTANCE : {safe_float(entry.get('distance_from_zone', 0.0)):.2f}% away from zone\n"
                f"STATUS        : {entry.get('entry_status', 'ACTIVE ENTRY ZONE')}\n"
                f"SWING STRUCT  : ${safe_float(structure.get('swing_struct', current_price)):.4f} (Lookback 8)\n"
                f"STOP LOSS     : ${stop_loss:.4f}\n"
                f"TARGET 1 (Cons): ${t1:.4f} | R:R 1 : {rr_t1:.2f}\n"
                f"TARGET 2 (Norm): ${t2:.4f} | R:R 1 : {rr_t2:.2f}\n"
                f"TARGET 3 (Aggr): ${t3:.4f} | R:R 1 : {rr_t3:.2f}\n\n"
                f"-------------------------------------------------------------------------\n"
                f"ENTRY QUALITY : {entry_score:.2f}/100\n"
                f"    |-- EMA Zone Position : {safe_float(entry.get('ema_pos_pts', 22)):.0f}/30\n"
                f"    |-- ATR Distance      : {safe_float(entry.get('atr_dist_pts', 10)):.0f}/25\n"
                f"    |-- VWMA Distance     : {safe_float(entry.get('vwma_pts', 20)):.0f}/20\n"
                f"    |-- RSI Extension     : {safe_float(entry.get('rsi_pts', 15)):.0f}/15\n"
                f"    |-- Structure         : {safe_float(entry.get('struct_pts', 2)):.0f}/12\n\n"
                f"-------------------------------------------------------------------------\n"
                f"CONFIDENCE    : {confidence_score:.2f}/100\n"
                f"TRADE QUALITY :\n"
                f"    |-- Current Market    : {tq_current:.2f}/100\n"
                f"    |-- Proposed Entry    : {tq_proposed:.2f}/100\n\n"
                f"=========================================================================\n"
                f"DECISION      : {colored_action}\n\n"
                f"-------------------------------------------------------------------------\n"
                f"Validation Notes:\n"
                f" - {risk.get('validation_note', 'VWMA volume trend is pointing down.')}\n"
                f"=========================================================================\n\n"
                f"Trade logged to Logs/phase7_trade_log_{symbol.lower()}.csv\n"
                f"AI Risk chart saved to {decision.get('chart_path', 'Logs/Charts/chart.png')}\n"
            )

        print(panel)
        return panel
        
    except Exception as e:
        logger.error(f"Failed to build or print panel: {e}")
        # Minimal fallback output
        try:
            print(f"\n[ERROR] Panel rendering failed: {e}")
            print(f"Symbol: {symbol}, Timeframe: {timeframe}")
            print(f"Decision: {exit_data.get('action', 'UNKNOWN')}")
        except Exception:
            print("\n[ERROR] Critical panel rendering failure")
        return None
