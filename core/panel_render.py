from colorama import init, Fore, Style

# Initialize colorama for Windows and cross-platform compatibility
init(autoreset=True)

def render_panel(decision):
    """
    Renders a Phase7 decision object into an advanced, color-coded
    structured text terminal panel.
    """

    # Handle error state
    if "error" in decision:
        print(f"\n{Fore.RED}[ERROR] {decision['error']}{Style.RESET_ALL}")
        return

    # Basic metadata
    symbol = decision.get("symbol", "AEROUSDT")
    timeframe = decision.get("timeframe", "4h")
    macro_bias = decision.get("macro_bias", "NEUTRAL")

    # Extract sections
    bias = decision.get("bias", {})
    trend = decision.get("trend", {})
    structure = decision.get("structure", {})
    entry = decision.get("entry", {})
    risk = decision.get("risk", {})
    exit_data = decision.get("exit", {})

    # Targets
    targets = risk.get("targets", (0, 0, 0))
    t1, t2, t3 = targets if len(targets) == 3 else (0, 0, 0)

    current_price = exit_data.get("current_price", 0.0)
    stop_loss = risk.get("atr_stop", 0.0)

    # Risk amount for R:R
    risk_amount = abs(current_price - stop_loss) if stop_loss else 0.0

    rr_t1 = abs(t1 - current_price) / risk_amount if risk_amount > 0 else 0.0
    rr_t2 = abs(t2 - current_price) / risk_amount if risk_amount > 0 else 0.0
    rr_t3 = abs(t3 - current_price) / risk_amount if risk_amount > 0 else 0.0

    # Formatted scores
    risk_score = float(risk.get('risk_score', 0))
    entry_score = float(entry.get('score', 0))
    confidence_score = float(risk.get('confidence_score', 0))
    tq_current = float(risk.get('trade_quality_current', 0))
    tq_proposed = float(risk.get('trade_quality_proposed', 0))
    trend_health_score = float(trend.get('trend_health', 0))

    # Helper for color-coding text values
    def colorize_val(val):
        val_str = str(val).upper()
        if "BULLISH" in val_str or "LONG" in val_str or "HEALTHY" in val_str or "STRONG" in val_str:
            return f"{Fore.GREEN}{val}{Style.RESET_ALL}"
        elif "BEARISH" in val_str or "SHORT" in val_str or "WEAK" in val_str:
            return f"{Fore.RED}{val}{Style.RESET_ALL}"
        elif "NEUTRAL" in val_str or "WAIT" in val_str or "NORMAL" in val_str:
            return f"{Fore.YELLOW}{val}{Style.RESET_ALL}"
        return f"{Fore.CYAN}{val}{Style.RESET_ALL}"

    action_val = exit_data.get('action', 'WAIT')
    colored_action = f"{Fore.GREEN}{action_val}{Style.RESET_ALL}" if action_val == "LONG" else (
                     f"{Fore.RED}{action_val}{Style.RESET_ALL}" if action_val == "SHORT" else f"{Fore.YELLOW}{action_val}{Style.RESET_ALL}")

    # ANSI code for Orange text
    ORANGE = "\033[38;5;214m"

    # Build color-accented panel
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
        f"ENTRY ZONE    : {Fore.CYAN}${entry.get('zone_lower', 0):.4f} - ${entry.get('zone_upper', 0):.4f}{Style.RESET_ALL}\n"
        f"ZONE DISTANCE : {entry.get('distance_from_zone', 0.0):.2f}% away from zone\n"
        f"STATUS        : {colorize_val(entry.get('entry_status', 'ACTIVE ENTRY ZONE'))}\n"
        f"SWING STRUCT  : ${structure.get('swing_struct', current_price):.4f} (Lookback 8)\n"
        f"STOP LOSS     : {Fore.RED}${stop_loss:.4f}{Style.RESET_ALL}\n"
        f"TARGET 1 (Cons): {Fore.GREEN}${t1:.4f}{Style.RESET_ALL} | R:R 1 : {rr_t1:.2f}\n"
        f"TARGET 2 (Norm): {Fore.GREEN}${t2:.4f}{Style.RESET_ALL} | R:R 1 : {rr_t2:.2f}\n"
        f"TARGET 3 (Aggr): {Fore.GREEN}${t3:.4f}{Style.RESET_ALL} | R:R 1 : {rr_t3:.2f}\n\n"
        f"{Style.DIM}-------------------------------------------------------------------------{Style.RESET_ALL}\n"
        f"ENTRY QUALITY : {entry_score:.2f}/100\n"
        f"    |-- EMA Zone Position : {entry.get('ema_pos_pts', 22)}/30\n"
        f"    |-- ATR Distance      : {entry.get('atr_dist_pts', 10)}/25\n"
        f"    |-- VWMA Distance     : {entry.get('vwma_pts', 20)}/20\n"
        f"    |-- RSI Extension     : {entry.get('rsi_pts', 15)}/15\n"
        f"    |-- Structure         : {entry.get('struct_pts', 2)}/12\n\n"
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

    print(panel)
    return panel
