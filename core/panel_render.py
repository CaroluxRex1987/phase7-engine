import logging
import textwrap

from . import config

logger = logging.getLogger(__name__)

# Viktor's terminal window can't comfortably show a line longer than this,
# and long lines were also triggering a display bug when he resized the
# window (that section of the panel disappearing). Every bulleted panel
# section (Decision Reasoning, Exit Watch, etc.) is wrapped to this width
# instead of ever printing one long line.
MAX_LINE_WIDTH = 125


def _wrap_bullets(items, empty_message):
    """
    Turns a list of strings into ' - ...' bulleted panel lines, wrapping
    any line that would exceed MAX_LINE_WIDTH onto multiple lines (indented
    so the wrapped text still reads as one bullet, not a new one).
    """
    if not items:
        items = [empty_message]

    out_lines = []
    for item in items:
        wrapped = textwrap.wrap(
            str(item),
            width=MAX_LINE_WIDTH,
            initial_indent=" - ",
            subsequent_indent="   ",
            break_long_words=False,
            break_on_hyphens=False,
        )
        out_lines.extend(wrapped if wrapped else [" - "])

    return "\n".join(out_lines) + "\n"

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
            return None

        # Handle error state
        if "error" in decision:
            error_msg = decision['error']
            if COLORAMA_AVAILABLE:
                print(f"\n{Fore.RED}[ERROR] {error_msg}{Style.RESET_ALL}")
            else:
                print(f"\n[ERROR] {error_msg}")
            return None

    except Exception as e:
        logger.error(f"Failed to validate decision object: {e}")
        print(f"\n[ERROR] Failed to process decision object: {e}")
        return None

    try:
        # Basic metadata with safe extraction
        # SEQUENCE ITEM 12: the fallback was "AEROUSDT", so a decision object
        # with no symbol rendered as a confident AERO panel rather than as the
        # error it is.
        symbol = str(decision.get("symbol") or "UNKNOWN")
        timeframe = str(decision.get("timeframe", "4h"))
        macro_bias = str(decision.get("macro_bias", "NEUTRAL"))

        # Extract sections with safe defaults
        bias = decision.get("bias", {}) if isinstance(decision.get("bias"), dict) else {}
        trend = decision.get("trend", {}) if isinstance(decision.get("trend"), dict) else {}
        structure = decision.get("structure", {}) if isinstance(decision.get("structure"), dict) else {}
        entry = decision.get("entry", {}) if isinstance(decision.get("entry"), dict) else {}
        risk = decision.get("risk", {}) if isinstance(decision.get("risk"), dict) else {}
        exit_data = decision.get("exit", {}) if isinstance(decision.get("exit"), dict) else {}

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

        # SEQUENCE ITEM 13: this was called `risk_amount`, which is what
        # engine_core.py called a sum of money — an account balance times a
        # risk percentage. Here it is a price distance, and it is the
        # denominator of all three R:R ratios. One name, two unrelated
        # quantities, in an object that carried both.
        #
        # The money is gone under Viktor's ruling, so the collision is gone
        # with it; the name is corrected anyway, because the removal of one
        # side of a collision is the moment the other side gets renamed or
        # never does. Zero denominator still guarded.
        stop_distance = abs(current_price - stop_loss) if stop_loss and current_price else 0.0

        if stop_distance > 0:
            rr_t1 = abs(t1 - current_price) / stop_distance
            rr_t2 = abs(t2 - current_price) / stop_distance
            rr_t3 = abs(t3 - current_price) / stop_distance
        else:
            rr_t1 = rr_t2 = rr_t3 = 0.0

        # Formatted scores with safe conversion
        #
        # BUG FIX (found during the A3/A4/A5 pass): the VALIDATION line below
        # displayed risk_score — which engine_core.py set to bias_score — next
        # to the validation_state label, instead of the validation_score that
        # the STRONG/NEUTRAL/WEAK label was derived from. The label was always
        # right; only the number beside it was wrong. Before B1 existed
        # bias_score sat close to validation_score by coincidence, which is why
        # it went unnoticed.
        #
        # SEQUENCE ITEM 13: the `risk_score = ...` line that survived that fix
        # is gone too. After the fix nothing printed it, so the panel bound a
        # local and dropped it — and the comment claimed it was still used for
        # CONFIDENCE, which reads confidence_score. The field itself is removed
        # from the decision object; bias.score is where that number lives.
        validation_score = safe_float(risk.get('validation_score', 0))
        entry_score = safe_float(entry.get('score', 0))
        confidence_score = safe_float(risk.get('confidence_score', 0))
        tq_proposed = safe_float(risk.get('trade_quality_proposed', 0))
        trend_health_score = safe_float(trend.get('trend_health', 0))

        # C4 BUILD: position size and the standalone EV line were both
        # dropped from the panel per Viktor's request -- the underlying
        # numbers (including EV, which still appears inside Decision
        # Reasoning below) are still computed upstream in
        # engine_core.py/decision_model.py in case they're useful again
        # later, just no longer read/shown here as their own line.

    except Exception as e:
        logger.error(f"Failed to extract panel data: {e}")
        print(f"\n[ERROR] Failed to extract panel data: {e}")
        return None

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

        # ============================================================
        # SEQUENCE ITEM 12 — Items 5 and 6, the footer
        # ============================================================
        #
        # These two lines used to be unconditional:
        #
        #   f"Trade logged to Logs/phase7_trade_log_{symbol.lower()}.csv"
        #   f"AI Risk chart saved to {decision.get('chart_path', '...')}"
        #
        # The first named a file no code wrote — Item 6, rated Critical: the
        # engine asserting an audit action that did not occur, on every run.
        #
        # The second had a subtler version of the same fault. `.get` with a
        # default returns the DEFAULT only when the key is ABSENT; the router
        # always sets chart_path, and sets it to None when charting failed. So
        # a failed chart printed "AI Risk chart saved to None" — still a claim
        # that something was saved.
        #
        # Both now print only when the thing they describe actually happened,
        # and say so plainly when it did not.
        logged_to = decision.get("decision_log_path") or ""
        log_line = (
            f"Decision logged to {logged_to}\n" if logged_to
            else "Decision NOT logged — this run has no audit record.\n"
        )

        saved_chart = decision.get("chart_path") or ""
        chart_line = (
            f"Chart saved to {saved_chart}\n" if saved_chart
            else "No chart was produced for this run.\n"
        )

        # SEQUENCE ITEM 5b: this read used to be
        #     exit_data.get('action', exit_data.get('final_action', 'WAIT'))
        # The 'final_action' fallback existed for the raw engine object, whose
        # "exit" block was compute_exit's. engine_core no longer renders and
        # compute_exit is gone, so the only caller is signal_router, which
        # always supplies 'action'. A fallback that cannot fire is worse than
        # none: it implies the DECISION line has a second source when it has
        # one, and the one it named printed an exit verdict under a decision
        # heading.
        action_val = str(exit_data.get('action', 'WAIT'))

        # C1: Decision Reasoning trail. Built from decision["explanation"]["reasons"],
        # which comes from the exact same evaluation path signal_router.py used to
        # produce the DECISION shown above -- so this can never disagree with it.
        # Wrapped to MAX_LINE_WIDTH (see _wrap_bullets) so a long reason never
        # produces one unbroken line too wide for the terminal.
        explanation = decision.get("explanation", {}) if isinstance(decision.get("explanation"), dict) else {}
        explanation_reasons = explanation.get("reasons", [])
        reasoning_lines = _wrap_bullets(
            explanation_reasons if isinstance(explanation_reasons, list) else [],
            "No explanation available for this decision.",
        )

        # C3: Exit Watch advisory flags. Passed straight through from
        # signal_router.py / exit_model.py's build_exit_watch() -- see
        # that function's docstring for what feeds into this list. Same
        # line-wrapping treatment as Decision Reasoning above.
        exit_watch = decision.get("exit_watch", [])
        exit_watch_lines = _wrap_bullets(
            exit_watch if isinstance(exit_watch, list) else [],
            "No exit-watch flags are active right now.",
        )

        # BTC MARKET CONTEXT (new feature, V1): informational only, never
        # changes BIAS/DECISION/CONFIDENCE above. Falls back to a plain
        # one-line note if unavailable (e.g. BTC fetch failed this run, or
        # this run WAS analyzing BTCUSDT itself) -- that never affects the
        # rest of the panel.
        btc = decision.get("btc_context", {}) if isinstance(decision.get("btc_context"), dict) else {}
        btc_available = bool(btc.get("available", False))

        if COLORAMA_AVAILABLE:
            # SEQUENCE ITEM 5b: the green list also held "TARGET 1 HIT",
            # "TARGET 2 HIT" and "TARGET 3 HIT", and the red list held
            # "STOP LOSS HIT". Those four strings were only ever produced by
            # compute_exit, which the router discarded before the panel saw it,
            # so the comparisons could not match. action_val comes from
            # DecisionModel, whose full output is WAIT, NO-TRADE (RISK TOO
            # HIGH), LONG, AGGRESSIVE LONG, CONSERVATIVE LONG and the three
            # short equivalents.
            #
            # Note that bare "LONG" and "SHORT" are live — DecisionModel does
            # emit them (decision_model.py:150 and :172), alongside the
            # AGGRESSIVE/CONSERVATIVE variants which fall through to yellow.
            # Only the four HIT literals were dead; the conditions stay.
            if action_val in ["LONG"]:
                colored_action = f"{Fore.GREEN}{action_val}{Style.RESET_ALL}"
            elif action_val in ["SHORT"]:
                colored_action = f"{Fore.RED}{action_val}{Style.RESET_ALL}"
            else:
                colored_action = f"{Fore.YELLOW}{action_val}{Style.RESET_ALL}"
            # ANSI code for Orange text
            ORANGE = "\033[38;5;214m"
            c_cyan = Fore.CYAN
            c_magenta = Fore.MAGENTA
            c_green = Fore.GREEN
            c_red = Fore.RED
            dim = Style.DIM
            reset = Style.RESET_ALL
        else:
            colored_action = action_val
            ORANGE = ""
            c_cyan = ""
            c_magenta = ""
            c_green = ""
            c_red = ""
            dim = ""
            reset = ""

        # Constructing layout strings cleanly
        header_banner = f"\n{c_cyan}Connecting to MEXC API for {symbol} ({timeframe}) - Phase-7.3 Structural Quant Engine...{reset}\n\n" if COLORAMA_AVAILABLE else f"\nConnecting to MEXC API for {symbol} ({timeframe}) - Phase-7.3 Structural Quant Engine...\n\n"

        box_top = f"{c_magenta}=========================================================================\n" if COLORAMA_AVAILABLE else "=========================================================================\n"
        title_line = f"    PHASE-7 STRUCTURAL DYNAMIC ENTRY QUALITY ENGINE\n"
        box_mid = f"========================================================================={reset}\n\n" if COLORAMA_AVAILABLE else "=========================================================================\n\n"
        divider = f"{dim}-------------------------------------------------------------------------{reset}\n" if COLORAMA_AVAILABLE else "-------------------------------------------------------------------------\n"

        # BTC MARKET CONTEXT (new feature, V1) -- built as its own block
        # here so the conditional (available vs. not) stays readable,
        # rather than trying to branch inside the big f-string below.
        # Informational only: never changes BIAS/DECISION/CONFIDENCE above.
        if btc_available:
            btc_reasoning_lines = _wrap_bullets(
                btc.get("reasons", []) if isinstance(btc.get("reasons"), list) else [],
                "No additional notes.",
            )
            btc_section = (
                f"{divider}"
                f"BTC Market Context (informational only -- does not change BIAS or DECISION above):\n"
                f"BTC BIAS      : {colorize_val(btc.get('detailed', 'NEUTRAL'))}\n"
                f"BTC REGIME    : {colorize_val(btc.get('regime', 'NEUTRAL STRUCTURE'))} | "
                f"Vol: {colorize_val(btc.get('volatility', 'NORMAL'))}\n"
                f"CORRELATION   : {colorize_val(btc.get('correlation_label', 'WEAK / NO CLEAR RELATIONSHIP'))} "
                f"({safe_float(btc.get('correlation', 0.0)):+.2f}) over last {int(btc.get('n_observations', 0))} candles\n"
                f"BTC SENSITIVITY (beta): {safe_float(btc.get('beta', 0.0)):.2f}x\n"
                f"BROAD MARKET STRESS: {colorize_val('YES' if btc.get('broad_market_stress') else 'No')}\n"
                f"BTC-ADJUSTED CONFIDENCE: {safe_float(btc.get('btc_adjusted_confidence', 0.0)):.2f}/100 "
                f"(vs {confidence_score:.2f}/100 unadjusted)\n"
                # SEQUENCE ITEM 12, Item 7: this number is correctness-validated
                # — it computes what it was designed to compute — and
                # empirically unvalidated: nothing has tested whether adjusting
                # confidence by BTC correlation predicts anything. Item 7
                # requires that status be stated rather than implied away, and
                # a number on a panel implies it away by default.
                f"   (computationally validated, empirically unvalidated — no backtest supports this adjustment)\n"
                f"{btc_reasoning_lines}\n"
            )
        else:
            btc_section = (
                f"{divider}"
                f"BTC Market Context (informational only): unavailable this run -- AERO analysis above is unaffected.\n\n"
            )

        panel = (
            f"{header_banner}"
            f"{box_top}{title_line}{box_mid}"
            f"BIAS       : {colorize_val(bias.get('detailed', bias.get('raw', 'NEUTRAL')))}\n"
            f"REGIME     : {colorize_val(bias.get('regime', 'NEUTRAL STRUCTURE'))}\n"
            f"STRUCTURE  : {colorize_val(structure.get('regime', 'NEUTRAL'))} | Vol: {colorize_val(bias.get('volatility', 'NORMAL'))}\n"
            f"SEQUENCE   : {colorize_val(structure.get('sequence', 'NONE'))}\n"
            f"TREND      : {colorize_val(trend.get('trend_direction', 'NEUTRAL'))} / {colorize_val(trend.get('momentum_mode', 'HEALTHY'))} (Score: {trend_health_score:.2f})\n"
            # SEQUENCE ITEM 11: the number after the label was
            # trend_health_score — the same value the TREND line above already
            # shows. The LABEL (STRONG / BUILDING / EXTENDED) is momentum_mode,
            # a genuinely separate reading, so it stays.
            f"MOMENTUM   : {colorize_val(trend.get('momentum_mode', 'HEALTHY'))}\n"
            f"VOLUME     : {colorize_val(structure.get('volume_sentiment', 'WEAK OR CONTRARY VOLUME'))}\n"
            f"VALIDATION : {colorize_val(risk.get('validation_state', 'WEAK'))} (Score: {validation_score:.2f})\n"
            f"VOLATILITY : {colorize_val(bias.get('volatility', 'LOW'))}\n"
            f"MACRO TREND: {colorize_val(macro_bias)}\n\n"
            f"{divider}"
            f"CURRENT PRICE : {ORANGE}${current_price:.4f}{reset}\n"
            f"ENTRY ZONE    : {c_cyan}${safe_float(entry.get('zone_lower', 0)):.4f} - ${safe_float(entry.get('zone_upper', 0)):.4f}{reset}\n"
            f"ZONE DISTANCE : {safe_float(entry.get('distance_from_zone', 0.0)):.2f}% away from zone\n"
            f"STATUS        : {colorize_val(entry.get('entry_status', 'ACTIVE ENTRY ZONE'))}\n"
            f"SWING STRUCT  : ${safe_float(structure.get('swing_struct', current_price)):.4f} (Lookback {config.STRUCT_LOOKBACK})\n"
            f"STOP LOSS     : {c_red}${stop_loss:.4f}{reset}\n"
            f"TARGET 1 (Cons): {c_green}${t1:.4f}{reset} | R:R 1 : {rr_t1:.2f}\n"
            f"TARGET 2 (Norm): {c_green}${t2:.4f}{reset} | R:R 1 : {rr_t2:.2f}\n"
            f"TARGET 3 (Aggr): {c_green}${t3:.4f}{reset} | R:R 1 : {rr_t3:.2f}\n\n"
            f"{divider}"
            f"ENTRY QUALITY : {entry_score:.2f}/100\n"
            f"    |-- EMA Zone Position : {safe_float(entry.get('ema_pos_pts', 22)):.0f}/30\n"
            f"    |-- ATR Distance      : {safe_float(entry.get('atr_dist_pts', 10)):.0f}/25\n"
            f"    |-- VWMA Distance     : {safe_float(entry.get('vwma_pts', 20)):.0f}/20\n"
            f"    |-- RSI Extension     : {safe_float(entry.get('rsi_pts', 15)):.0f}/15\n"
            f"    |-- Structure         : {safe_float(entry.get('struct_pts', 2)):.0f}/12\n\n"
            f"{divider}"
            f"CONFIDENCE (decision): {confidence_score:.2f}/100\n"
            f"TRADE QUALITY :\n"

            f"    |-- Proposed Entry    : {tq_proposed:.2f}/100\n\n"
            f"{box_top}"
            f"DECISION      : {colored_action}\n\n"
            f"{divider}"
            f"Decision Reasoning:\n"
            f"{reasoning_lines}\n"
            f"{divider}"
            f"Exit Watch (advisory only -- not automatic):\n"
            f"{exit_watch_lines}\n"
            f"{divider}"
            f"Validation Notes:\n"
            f" - {risk.get('validation_note', 'VWMA volume trend is pointing down.')}\n"
            f"{btc_section}"
            f"{box_top}\n"
            f"{log_line}"
            f"{chart_line}"
        )

        print(panel)
        return panel

    except Exception as e:
        logger.error(f"Failed to build or print panel: {e}")
        try:
            print(f"\n[ERROR] Panel rendering failed: {e}")
        except Exception:
            print("\n[ERROR] Critical panel rendering failure")
        return None