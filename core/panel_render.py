import logging
import math
import textwrap
from decimal import Decimal

from . import config
from .threshold_text import compared_value_text

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


def _score_text(value, denominator=100.0):
    """
    A score and its scale, or "not computed".

    21 SEPTEMBER 2026, work order B. Every score line on this panel formatted
    its number with ":.2f" directly. The router sends NaN for a value it could
    not measure (signal_router._finite_or_nan), and Python prints that as the
    literal text "nan" -- "VALIDATION : WEAK (Score: nan/100)". The price lines
    were guarded against exactly this at Round 6 F3; the score lines were not,
    including the two that a9d4b1f and 119c8a3 edited to add their "/100".
    Three more scores defaulted an absent value to 0 and printed "0.00/100",
    a score nobody computed.

    One function for every score line, so the next one added cannot forget.
    """
    if isinstance(value, (int, float)) and math.isfinite(value):
        return f"{value:.2f}/{denominator:.0f}"
    return "not computed"


def _stress_text(value):
    """
    BROAD MARKET STRESS, as YES or No when it was classified, UNKNOWN when
    it was not.

    13 OCTOBER 2026, the fallback sweep. The line read
    'YES' if btc.get('broad_market_stress') else 'No', so an absent flag
    printed "No" -- a market nobody classified, reported calm.
    """
    if isinstance(value, bool):
        return "YES" if value else "No"
    return "UNKNOWN"

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
        # 21 SEPTEMBER 2026, work order B: the asset's name for the BTC
        # section's sentences, from the same function decision_model.py's
        # reasoning uses -- see asset_name() there.
        from models.decision_model import asset_name
        asset = asset_name(symbol)
        # 13 OCTOBER 2026, the fallback sweep (DECISIONS, "Ruling, 13 October
        # 2026 -- the fallback sweep"): these were "4h" and "NEUTRAL", a
        # timeframe and a macro reading nobody stated. The router writes both
        # keys on every decision it builds, so neither could fire on the
        # engine's path; absent, they now read UNKNOWN, as symbol already did.
        timeframe = str(decision.get("timeframe", "UNKNOWN"))
        macro_bias = str(decision.get("macro_bias", "UNKNOWN"))

        # Extract sections with safe defaults
        bias = decision.get("bias", {}) if isinstance(decision.get("bias"), dict) else {}
        trend = decision.get("trend", {}) if isinstance(decision.get("trend"), dict) else {}
        structure = decision.get("structure", {}) if isinstance(decision.get("structure"), dict) else {}
        entry = decision.get("entry", {}) if isinstance(decision.get("entry"), dict) else {}
        risk = decision.get("risk", {}) if isinstance(decision.get("risk"), dict) else {}
        exit_data = decision.get("exit", {}) if isinstance(decision.get("exit"), dict) else {}

        # Safe numeric extraction with error handling
        def safe_float(value, default=0.0):
            # FINDING 3 RE-AUDIT, 1 September 2026 (the audit's Observation 5):
            # this converted NaN and infinity without checking, so a non-finite
            # value reached the panel and printed as the literal text "nan" in
            # a price field -- "STOP LOSS : $nan" from calculate_stop_targets'
            # NaN path, which that function now rejects at its own input. The
            # three other safe_float implementations in the engine
            # (entry_model, bias_engine, decision_model) all check finiteness;
            # this one did not.
            #
            # math.isfinite rather than numpy: this module imports neither, and
            # one stdlib import beats a numpy dependency for one predicate.
            try:
                if value is None:
                    return default
                out = float(value)
                return out if math.isfinite(out) else default
            except (ValueError, TypeError):
                return default

        # Targets with safe extraction
        #
        # ROUND 6 F3 FOLLOW-UP, 13 September 2026: this block, current_price
        # and stop_loss below all used to default an absent value to a
        # finite 0.0 -- a (0, 0, 0) fallback for targets, safe_float(..., 0.0)
        # for the other two -- the exact fabrication shape signal_router.py's
        # own targets/atr_stop/current_price defaults were fixed to stop
        # doing (Round 6 F3, commit 9b34163). Unreachable today for the same
        # reason F3's fix was unreachable there -- engine_core always sets
        # these three keys -- but nowhere else on this page makes that
        # assumption (see swing_struct_line, _entry_zone_lines,
        # _correlation_lines below), so this should not either. NaN now,
        # matching every other "not located" field on this panel; every
        # print site for these three is guarded below so a NaN never reaches
        # an f-string price format directly -- that is exactly the "$nan"
        # defect this file's own safe_float() docstring, above, already
        # describes fixing once.
        targets = risk.get("targets")
        if isinstance(targets, (list, tuple)) and len(targets) >= 3:
            t1 = safe_float(targets[0], float("nan"))
            t2 = safe_float(targets[1], float("nan"))
            t3 = safe_float(targets[2], float("nan"))
        else:
            t1 = t2 = t3 = float("nan")

        current_price = safe_float(exit_data.get("current_price"), float("nan"))
        stop_loss = safe_float(risk.get("atr_stop"), float("nan"))

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
        #
        # ROUND 6 F3 FOLLOW-UP: the guard used to be `if stop_loss and
        # current_price` -- truthiness, not a finiteness check. NaN is
        # truthy (any nonzero float is), so that guard alone would not have
        # stopped a NaN input from reaching the subtraction below; explicit
        # math.isfinite() on both inputs instead. A real, measured
        # stop_distance of exactly 0.0 (current_price == stop_loss) still
        # reaches the `else: rr_t* = 0.0` branch beneath it unchanged -- that
        # is a genuine zero-distance stop, not an unknown one, the same
        # distinction _finite_or_nan makes at the router.
        if math.isfinite(current_price) and math.isfinite(stop_loss):
            stop_distance = abs(current_price - stop_loss)
        else:
            stop_distance = float("nan")

        if math.isfinite(stop_distance):
            if stop_distance > 0:
                rr_t1 = abs(t1 - current_price) / stop_distance
                rr_t2 = abs(t2 - current_price) / stop_distance
                rr_t3 = abs(t3 - current_price) / stop_distance
            else:
                rr_t1 = rr_t2 = rr_t3 = 0.0
        else:
            rr_t1 = rr_t2 = rr_t3 = float("nan")

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
        # CONFIDENCE, which reads confidence_score.
        #
        # THE REDESIGN'S STAGE 5, 15 November 2026: four of these locals are
        # gone with the four lines that printed them -- validation_score
        # (VALIDATION), confidence_score (CONFIDENCE (decision)), tq_proposed
        # (TRADE QUALITY / Proposed Entry) and trend_health_score (the TREND
        # line's score). The fields themselves have left the decision object.
        # 21 SEPTEMBER 2026, work order B: this and the three above defaulted
        # an absent value to 0, printed as "0.00/100". NaN now, printed by
        # _score_text as "not computed". The router always sets it today, so
        # the default was latent -- the same reasoning Round 6 F3 applied to
        # the price lines above.
        entry_score = safe_float(entry.get('score'), float('nan'))

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

        # 2 SEPTEMBER 2026: this line read
        #
        #     safe_float(structure.get('swing_struct', current_price))
        #
        # Two fabrications in one expression. The .get default handed back the
        # CURRENT PRICE as a structural level, and safe_float's own 0.0 default
        # turned a NaN -- which is now what structure.py reports when the swing
        # detector fails -- into "$0.0000". Both print as a located level in a
        # price field. A level that was not found is said, not drawn.
        swing_value = safe_float(structure.get("swing_struct"), None)
        swing_struct_line = (
            f"SWING STRUCT  : ${swing_value:.4f} (Lookback {config.STRUCT_LOOKBACK})"
            if swing_value is not None
            else "SWING STRUCT  : not located this run "
                 f"(Lookback {config.STRUCT_LOOKBACK})"
        )

        # AUDIT FINDING (2 September 2026): this line read
        #
        #     risk.get('validation_note', 'VWMA volume trend is pointing down.')
        #
        # A .get default that asserts a specific market fact. If the key were
        # ever missing the panel would state, under a heading called
        # Validation Notes, that volume was pointing down -- a reading of this
        # market that nothing computed. The router always supplies the key, so
        # the default never fired; that makes it latent, not harmless. It is
        # the same shape as the hardcoded trade-log path and the chart
        # default, both removed for the same reason.
        #
        # The replacement says only that nothing was produced, which is the
        # one thing that is true when the key is absent.
        #
        # THE REDESIGN'S STAGE 5, 15 November 2026: this read
        # risk.validation_note, the macro and volume notes joined. The
        # validation block is gone and the macro note alone survives, as the
        # top-level macro_note, printed on its own line under MACRO TREND
        # rather than in a "Validation Notes" section at the foot of the
        # panel.
        macro_note = (
            decision.get("macro_note")
            or "No macro note was produced for this run."
        )
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
        # 13 OCTOBER 2026, the fallback sweep: the 'WAIT' that comment left
        # behind was the same kind of fallback -- an action nobody decided.
        # Absent, the DECISION line now reads UNKNOWN, the router's own word
        # for it (its log line, route_and_execute).
        action_val = str(exit_data.get('action', 'UNKNOWN'))

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

        # FINDING 5, 27 September 2026 -- Viktor's ruling, panel only
        # (docs/PHASE7_DECISIONS.md, "Ruling, 27 September 2026 -- a NEUTRAL
        # bias prints no plan (finding 5)"). The plan's direction is the sign
        # of bias_score (models/risk_model.py, calculate_stop_targets), so
        # under a NEUTRAL bias -- a score inside +/-RAW_BIAS_THRESHOLD, until
        # the redesign's stage 2 made the side the direction's and stage 5
        # removed the score -- the
        # panel printed a long- or short-shaped stop and targets for a
        # direction the engine had not chosen; exactly 0 printed a long. The
        # panel now prints no stop, no targets and no R:R under a NEUTRAL bias,
        # and one PLAN line saying why. The engine still computes the plan and
        # the decision object still carries it: the risk check needs a stop,
        # and the log records it. Nothing here changes a decision -- the
        # ladder never returns LONG or SHORT under a NEUTRAL bias
        # (models/decision_model.py, _determine_final_action), which
        # tests/test_neutral_bias_prints_no_plan.py checks over a grid.
        #
        # Keyed on bias.raw, the field the direction box below and
        # decision_model both read. Only NEUTRAL withholds the plan: a raw
        # bias the engine never emits (absent, UNKNOWN) prints it as before.
        raw_bias_val = str(bias.get("raw", "UNKNOWN")).upper()
        plan_withheld = raw_bias_val == "NEUTRAL"

        # C3: Exit Watch advisory flags. Passed straight through from
        # signal_router.py / exit_model.py's build_exit_watch() -- see
        # that function's docstring for what feeds into this list. Same
        # line-wrapping treatment as Decision Reasoning above.
        #
        # FINDING 5: the always-on note naming Target 1 is a target, so it is
        # not printed under a NEUTRAL bias. It is still in the decision
        # object and the log; only this rendering skips it.
        # 13 OCTOBER 2026, the fallback sweep: an absent exit_watch was read
        # as [], and printed "No exit-watch flags are active right now" -- a
        # reading of a list nobody built. The router writes the key on every
        # decision, so this could not fire on the engine's path; absent, it
        # now says it was not computed.
        # 15 OCTOBER 2026, B10 (DECISIONS, "Ruling, 15 October 2026 -- B10:
        # two outputs agree with finding 4 and the action"): nor on a run
        # that suggests no trade. The note begins "If you're already in this
        # trade" and names this run's Target 1; on a WAIT or a NO-TRADE the
        # engine suggested no trade, so the target is that of a plan it did
        # not suggest. A trade is an action that names a side, the test
        # decision_model makes of its own action (_refuse_incoherent_plan,
        # _apply_degradation): WAIT, every NO-TRADE and an absent action
        # (UNKNOWN) withhold the note. Panel only, as for finding 5: under a
        # leaning bias the plan's stop and targets still print, and the
        # decision object and the log keep the note.
        exit_watch = decision.get("exit_watch")
        exit_watch_computed = isinstance(exit_watch, list)
        exit_watch = exit_watch if exit_watch_computed else []
        names_a_side = any(side in action_val for side in ("LONG", "SHORT"))
        if plan_withheld or not names_a_side:
            from models.exit_model import TARGET1_NOTE_PREFIX
            exit_watch = [flag for flag in exit_watch
                          if not str(flag).startswith(TARGET1_NOTE_PREFIX)]
        exit_watch_lines = _wrap_bullets(
            exit_watch,
            "No exit-watch flags are active right now." if exit_watch_computed
            else "Exit watch was not computed for this run.",
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
        # SWEEP ITEM 9, 8 September 2026. Previous banner claimed "Connecting
        # to MEXC API" on every run including offline pinned, and said
        # Phase-7.3 while config.engine_version is v1.0.
        from core import config as _cfg
        _ver = getattr(_cfg, "engine_version", "Phase-7 Structural Quant Engine")
        header_banner = (
            f"\n{c_cyan}{_ver} — {symbol} ({timeframe}){reset}\n\n"
            if COLORAMA_AVAILABLE
            else f"\n{_ver} — {symbol} ({timeframe})\n\n"
        )

        box_top = f"{c_magenta}=========================================================================\n" if COLORAMA_AVAILABLE else "=========================================================================\n"
        title_line = f"    PHASE-7 STRUCTURAL DYNAMIC ENTRY QUALITY ENGINE\n"
        box_mid = f"========================================================================={reset}\n\n" if COLORAMA_AVAILABLE else "=========================================================================\n\n"
        divider = f"{dim}-------------------------------------------------------------------------{reset}\n" if COLORAMA_AVAILABLE else "-------------------------------------------------------------------------\n"

        def _entry_quality_lines(entry, entry_score):
            """
            THE REDESIGN'S STAGE 4, 15 November 2026. Entry quality is
            D + H, so the panel prints the total and its two parts, each
            beside the distance it was computed from:

                ENTRY QUALITY : 0.00/100
                    |-- Distance (D)      : 0.00/80 at 3.2070 ATR from the band's midpoint
                    |-- HVN nearness (H)  : 0.00/20 at 15.1202 ATR from the HVN
                    |-- Lines             : 70 for LONG/SHORT and AGGRESSIVE, 50 for CONSERVATIVE

            What stood here was the reconciliation of 5 September 2026: five
            sub-scores, their subtotal out of 102, the combined confluence
            multiplier with its three factors, and the clip when it fired.
            It was written because the panel printed five numbers and a
            total they did not add up to -- 10 + 5 + 10 + 10 + 4 under 45.18
            on the pinned fixture. D + H needs no reconciliation: the two
            parts and the total are the whole of the arithmetic, and the
            distances are printed so each part can be checked by hand
            against the straight line it comes from, which was the reason
            for straight lines (the draft's section 3.1).

            The two tier lines are printed because Decision Reasoning names
            them, and a line the operator is told a number is under should
            be visible on the panel beside the number -- the same reason
            stage 3 added TURNOVER, TRIGGER and TRIGGER VOLUME. They come
            from models/decision_model.py's constants rather than being
            written here again.

            A part that was not measured prints as that, not as 0.00/80: the
            denominators are the maxima and a zero is a real score. The
            total prints through _score_text, which already says "not
            computed" for a value the engine did not measure.
            """
            from models.decision_model import DecisionModel
            from models.entry_model import (DISTANCE_MAX_POINTS,
                                            HVN_MAX_POINTS)

            def part(label, points_key, distance_key, maximum, against):
                points = entry.get(points_key)
                distance = entry.get(distance_key)
                shown = _score_text(safe_float(points, float("nan")), maximum)
                if shown == "not computed":
                    return f"    |-- {label:<18}: not measured\n"
                at = safe_float(distance, float("nan"))
                where = (f" at {at:.4f} ATR from {against}"
                         if math.isfinite(at) else "")
                return f"    |-- {label:<18}: {shown}{where}\n"

            lines = (
                f"ENTRY QUALITY : {_score_text(entry_score)}\n"
                + part("Distance (D)", "distance_pts", "distance_atr",
                       DISTANCE_MAX_POINTS, "the band's midpoint")
                + part("HVN nearness (H)", "hvn_pts", "hvn_distance_atr",
                       HVN_MAX_POINTS, "the HVN")
                + (f"    |-- {'Lines':<18}: "
                   f"{DecisionModel.UPPER_TIER_ENTRY_QUALITY_MIN:g} for "
                   f"LONG/SHORT and AGGRESSIVE, "
                   f"{DecisionModel.CONSERVATIVE_ENTRY_QUALITY_MIN:g} for "
                   f"CONSERVATIVE\n")
            )

            return lines + "\n"

        def _entry_zone_lines(entry, c_cyan, reset):
            """
            AUDIT FINDING (4), 5 September 2026. These two lines were:

                ENTRY ZONE    : ${zone_lower:.4f} - ${zone_upper:.4f}
                ZONE DISTANCE : {distance_from_zone:.2f}% away from zone

            with every value passed through safe_float(..., 0.0). A run that
            could not locate the zone printed "$0.0000 - $0.0000" and
            "0.00% away from zone" -- price sitting exactly on a zone that was
            never found. Zero is a price, and 0.00% is the strongest possible
            statement this line can make.

            entry_model now returns NaN for both when there is no zone, which
            is how this engine already spells "not located" (structure.py's
            hvn, lvn and swing_struct). Printed as such.

            FINDING 4, 27 September 2026 -- Viktor's ruling (DECISIONS,
            "Ruling, 27 September 2026 -- the plan is measured from the
            decision close (finding 4)"). The lines were labelled ENTRY ZONE
            and ZONE DISTANCE, while stop, targets and every R:R are measured
            from the decision close and no rule requires price to be inside
            the zone to trade. The panel implied an entry it does not plan.
            They are labelled for what they are now: the band between the two
            EMAs, a reference that the entry-quality score measures the close
            against. The lengths are read from config rather than written
            here, so the label cannot name EMAs the engine did not compute.
            The data keys (zone_lower, zone_upper, distance_from_zone) and
            entry_status's values are unchanged: entry_status is read by
            decision_model (`"ACTIVE" in entry_status`), and renaming it is a
            decision-path change the ruling did not ask for.

            ROUND 8, F5, 10 October 2026 -- the label and record batch
            (DECISIONS, "Ruling, 5 October 2026 -- round 8 triaged ...",
            point 8). The distance line read "x% away from the band", while
            distance_from_zone is the distance from the band's MIDPOINT as a
            percentage of the close (entry_model). With the close inside the
            band it printed a positive distance "away from the band" under
            STATUS : ACTIVE ENTRY ZONE -- on the real run of 30 September,
            1.40%. The line now names what was measured; the number, the key
            and the entry score are unchanged.
            """
            band = f"(EMA {config.EMA_FAST} and EMA {config.EMA_SLOW})"
            lower = safe_float(entry.get("zone_lower"), float("nan"))
            upper = safe_float(entry.get("zone_upper"), float("nan"))
            distance = safe_float(entry.get("distance_from_zone"), float("nan"))

            if math.isfinite(lower) and math.isfinite(upper):
                zone_line = (
                    f"EMA BAND      : {c_cyan}${lower:.4f} - ${upper:.4f}{reset} "
                    f"{band} -- a reference, not the entry\n"
                )
            else:
                zone_line = (
                    f"EMA BAND      : not located "
                    f"{band} unavailable this run\n"
                )

            if math.isfinite(distance):
                distance_line = (
                    f"BAND DISTANCE : {distance:.2f}% from the band's midpoint\n"
                )
            else:
                distance_line = "BAND DISTANCE : not measured\n"

            return zone_line + distance_line

        def _gate_lines(entry, bias):
            """
            THE REDESIGN'S STAGE 3, 15 November 2026: what gates 7 and 8
            read, so that a refusal named in Decision Reasoning points at
            something visible on the panel, and a gate that passed is
            visible too.

                TURNOVER      : 67902 USDT on the decision candle (floor 10000)
                TRIGGER       : NO -- the candle did not close beyond its open and the previous close
                TRIGGER VOLUME: 84694 against a median of 179247.8923 before it -- not above it

            Entry 58's rule holds here as in the sentences: a value set
            against a line is printed on its own side of it
            (core/threshold_text.py), and the median, which is a line the
            data gives, is printed exactly as computed (how many candles it
            is over is models/entry_model.py's TRIGGER_VOLUME_LOOKBACK, and
            Decision Reasoning says it). A value that was not
            measured prints as that; under a NEUTRAL direction there is no
            side to read a trigger for, and the line says so.
            """
            def amount(value):
                if isinstance(value, bool) or not isinstance(value, (int, float)):
                    return None
                number = float(value)
                if not math.isfinite(number) or number < 0.0:
                    return None
                return number

            turnover = amount(entry.get("quote_volume"))
            floor = amount(entry.get("liquidity_floor"))
            if turnover is None or floor is None:
                turnover_line = "TURNOVER      : not measured\n"
            else:
                verdict = "" if turnover >= floor else " -- UNDER THE FLOOR"
                turnover_line = (
                    f"TURNOVER      : {compared_value_text(turnover, floor)} "
                    f"USDT on the decision candle (floor {floor:g}){verdict}\n"
                )

            trigger = entry.get("trigger")
            raw = bias.get("raw")
            if trigger is True:
                trigger_line = ("TRIGGER       : YES -- the candle closed "
                                "beyond its open and the previous close\n")
            elif trigger is False:
                trigger_line = ("TRIGGER       : NO -- the candle did not "
                                "close beyond its open and the previous close\n")
            elif raw == "BULLISH" or raw == "BEARISH":
                trigger_line = "TRIGGER       : not measured\n"
            else:
                trigger_line = "TRIGGER       : not read -- no side to read it for\n"

            volume = amount(entry.get("trigger_volume"))
            median = amount(entry.get("trigger_volume_median"))
            if volume is None or median is None:
                volume_line = "TRIGGER VOLUME: not measured\n"
            else:
                exact_median = f"{Decimal(repr(median)):f}"
                if volume == median:
                    printed = exact_median
                else:
                    printed = compared_value_text(volume, median)
                verdict = "above it" if volume > median else "not above it"
                volume_line = (
                    f"TRIGGER VOLUME: {printed} against a median of "
                    f"{exact_median} before it -- {verdict}\n"
                )

            return turnover_line + trigger_line + volume_line

        def _correlation_lines(btc, colorize_val):
            """
            AUDIT FINDING (a), 5 September 2026. These two lines were:

                CORRELATION   : {label} ({correlation:+.2f}) over last {n} candles
                BTC SENSITIVITY (beta): {beta:.2f}x

            with both numbers passed through safe_float(..., 0.0). When the
            relationship could not be measured, that printed

                CORRELATION   : WEAK / NO CLEAR RELATIONSHIP (+0.00) over last 0 candles
                BTC SENSITIVITY (beta): 0.00x

            -- a stated finding about two assets, a coefficient, and a
            sensitivity, from nothing. "over last 0 candles" was the only tell,
            and it sits at the end of a sentence that has already made the
            claim.

            btc_context now returns NaN for an unmeasured relationship and
            engine_core stores it as None, with n_observations at 0. Either is
            enough to take this branch.
            """
            n_obs = int(btc.get("n_observations", 0) or 0)
            correlation = btc.get("correlation")
            beta = btc.get("beta")

            unmeasured = (
                n_obs <= 0
                or correlation is None
                or not math.isfinite(safe_float(correlation, float("nan")))
            )

            if unmeasured:
                # 21 SEPTEMBER 2026, work order B: this said "AERO" whatever
                # the symbol. Sequence item 12 fixed the same string in
                # decision_model.py and missed this one and the one below.
                return (
                    f"CORRELATION   : {colorize_val('NOT MEASURED')} "
                    f"— {asset} and BTC could not be paired by timestamp this run\n"
                    f"BTC SENSITIVITY (beta): not measured\n"
                )

            beta_text = (
                f"{safe_float(beta, 0.0):.2f}x"
                if (beta is not None and math.isfinite(safe_float(beta, float("nan"))))
                else "not measured"
            )
            return (
                f"CORRELATION   : {colorize_val(btc.get('correlation_label', 'NOT MEASURED'))} "
                f"({safe_float(correlation, 0.0):+.2f}) over last {n_obs} candles\n"
                f"BTC SENSITIVITY (beta): {beta_text}\n"
            )

        # BTC MARKET CONTEXT -- built as its own block here so the
        # conditional (available vs. not) stays readable, rather than trying
        # to branch inside the big f-string below. Reference only: never
        # changes BIAS/DECISION/CONFIDENCE above.
        #
        # N5, 9 October 2026 (Viktor's ruling of 5 October, point 7: Bitcoin
        # is reference only). Three things stood after BROAD MARKET STRESS:
        # the BTC-ADJUSTED CONFIDENCE line, a line stating that number's
        # validation status under Item 7, and the adjustment's own sentence as
        # a bullet. All three went with the adjustment; the section prints
        # what engine_core measured, and nothing else.
        if btc_available:
            btc_section = (
                f"{divider}"
                f"BTC Market Context (informational only -- does not change BIAS or DECISION above):\n"
                # 13 OCTOBER 2026, the fallback sweep: the three fallbacks
                # here were NEUTRAL, NEUTRAL STRUCTURE and NORMAL, and an
                # absent stress flag printed "No". The router writes every
                # key of an available block, so none could fire on the
                # engine's path; absent, each now reads UNKNOWN, as the
                # router's own fallback for the same key does.
                f"BTC BIAS      : {colorize_val(btc.get('detailed', 'UNKNOWN'))}\n"
                f"BTC REGIME    : {colorize_val(btc.get('regime', 'UNKNOWN STRUCTURE'))} | "
                f"Vol: {colorize_val(btc.get('volatility', 'UNKNOWN'))}\n"
                f"{_correlation_lines(btc, colorize_val)}"
                f"BROAD MARKET STRESS: {colorize_val(_stress_text(btc.get('broad_market_stress')))}\n\n"
            )
        else:
            btc_section = (
                f"{divider}"
                f"BTC Market Context (informational only): unavailable this run -- {asset} analysis above is unaffected.\n\n"
            )

        # ROUND 6 F3 FOLLOW-UP: CURRENT PRICE, STOP LOSS and the three
        # TARGET lines (with their R:R ratios) now guard against the NaN
        # these fields can carry per the extraction above, printing "not
        # available" / "not computed" / "not located" instead of letting
        # Python's own float formatting spell a missing value as the literal
        # text "nan" in a price field. Built here, after ORANGE/c_red/
        # c_green/reset are assigned above, not up by swing_struct_line.
        #
        # FINDING 16, 26 September 2026. The engine decides on the latest
        # CLOSED candle, so the price the stop and targets are measured from
        # is that candle's close, and the line says so: it was labelled
        # CURRENT PRICE, which it no longer is. The live price -- the close of
        # the candle still forming, which the fetcher removed -- follows on a
        # line of its own, labelled as information only, with its distance
        # from the decision close (Viktor's ruling, point 2). Nothing that
        # decides reads it; it comes from provenance, not from the analysis.
        #
        # FINDING 4, 27 September 2026 (Viktor's ruling, option A): the
        # decision close IS the plan's entry -- stop, targets and all three
        # R:R values are measured from it -- and the line now says so, since
        # the panel printed no single entry price anywhere.
        provenance = decision.get("provenance")
        provenance = provenance if isinstance(provenance, dict) else {}
        candles = provenance.get("decision_candles")
        candles = candles if isinstance(candles, dict) else {}
        struct_candle = candles.get("struct")
        struct_candle = struct_candle if isinstance(struct_candle, dict) else {}

        candle_note = (
            f" ({timeframe} candle opened {struct_candle['open_time']} UTC)"
            if struct_candle.get("open_time") else ""
        )
        #
        # FINDING 5: under a NEUTRAL bias there is no plan, so the close is
        # printed without calling itself the plan's entry.
        if not math.isfinite(current_price):
            current_price_line = "DECISION CLOSE: not available this run\n"
        elif plan_withheld:
            current_price_line = (
                f"DECISION CLOSE: {ORANGE}${current_price:.4f}{reset}{candle_note}\n"
            )
        else:
            current_price_line = (
                f"DECISION CLOSE: {ORANGE}${current_price:.4f}{reset}{candle_note}"
                f" -- the plan's entry; stop, targets and R:R are measured from it\n"
            )

        live_price = safe_float(struct_candle.get("live_price"), float("nan"))
        if math.isfinite(live_price):
            if math.isfinite(current_price) and current_price != 0:
                distance = (live_price - current_price) / current_price * 100.0
                distance_text = f"{distance:+.2f}% from the decision close"
            else:
                distance_text = "distance from the decision close not computed"
            live_price_line = (
                f"LIVE PRICE    : ${live_price:.4f} -- information only, used by "
                f"no decision; {distance_text}\n"
            )
        elif struct_candle.get("basis") == "pinned":
            live_price_line = "LIVE PRICE    : not available -- pinned data has no live candle\n"
        elif struct_candle.get("basis") == "live":
            live_price_line = (
                "LIVE PRICE    : not available -- the exchange sent no forming "
                "candle this run\n"
            )
        else:
            live_price_line = "LIVE PRICE    : not available this run\n"

        stop_loss_line = (
            f"STOP LOSS     : {c_red}${stop_loss:.4f}{reset}\n"
            if math.isfinite(stop_loss)
            else "STOP LOSS     : not computed this run\n"
        )

        def _target_line(label, price, rr):
            if not math.isfinite(price):
                return f"TARGET {label}: not located this run\n"
            rr_text = f"{rr:.2f}" if math.isfinite(rr) else "not computed"
            return f"TARGET {label}: {c_green}${price:.4f}{reset} | R:R 1 : {rr_text}\n"

        target_lines = (
            _target_line("1 (Cons)", t1, rr_t1)
            + _target_line("2 (Norm)", t2, rr_t2)
            + _target_line("3 (Aggr)", t3, rr_t3)
        )

        # FINDING 5: under a NEUTRAL bias one PLAN line replaces the stop,
        # the three targets and their R:R.
        #
        # THE REDESIGN'S STAGE 2, 14 November 2026. The line read "the bias
        # is NEUTRAL (score X, inside +/-20)", the wording Viktor ruled on
        # 27 September, with the score and the threshold read from the
        # weighted sum. NEUTRAL no longer comes from that sum (his ruling of
        # 7 November: EMA50's slope and the EMAs' order), so printing the
        # sum beside it would give a reason that is not the reason. The
        # line keeps the ruling's sentence and drops the parenthesis; the
        # reason is in Decision Reasoning, in decision_model's own sentence.
        if plan_withheld:
            plan_lines = (
                "PLAN          : none -- the bias is NEUTRAL, "
                "so there is no direction to measure a stop from\n"
            )
        else:
            plan_lines = f"{stop_loss_line}{target_lines}"

        # VIKTOR'S REQUEST, 14 September 2026: a run he read a few days
        # earlier put a genuine SHORT setup in front of him (bearish bias,
        # descending targets) under a NO-TRADE decision -- correct, but
        # nothing on the panel said "SHORT" in words; he had to read the
        # target ordering to know which side the analysis leaned. This
        # prints that reading as its own solid box, directly under the
        # DECISION line, on every run rather than only ones that authorize
        # a trade.
        #
        # Source is bias.raw, not action_val or the risk plan's targets.
        # decision_model.py's _determine_final_action reads this exact
        # field for direction (Viktor's 2 September ruling: bias is the
        # sole direction source), so whenever a trade IS authorized this
        # box already agrees with the LONG/SHORT the DECISION line prints
        # -- it cannot show one side while the DECISION line shows the
        # other for any run that reaches _determine_final_action normally.
        #
        # One case that ruling does not cover: _refuse_incoherent_plan
        # firing ("NO-TRADE (PLAN CONTRADICTS ACTION)") means bias and the
        # risk plan's own targets pointed different ways this run -- see
        # tests/test_direction_source.py, the 2 September defect ("a long
        # label on a short plan") this box exists to never bring back
        # through a new line. Printing the bias direction there would be
        # that identical defect, so that case gets its own honest label
        # instead of a directional claim either side would dispute.
        #
        # RULED, 14 September 2026: a NEUTRAL bias prints nothing here,
        # not a "no lean" line. The first version of this patch printed one,
        # for consistency with swing_struct/entry-zone/correlation's "not
        # located"/"not measured" lines elsewhere on this panel -- but those
        # are measurements that failed. NEUTRAL is not a failed reading; it
        # is bias reporting no lean, which is exactly what an absent box
        # already says. Viktor: only show this box when there is an actual
        # LONG or SHORT to report.
        #
        # raw_bias_val is read once, above the Exit Watch block (finding 5).

        if "PLAN CONTRADICTS ACTION" in action_val.upper():
            direction_box = (
                "SETUP DIRECTION: CONTRADICTORY -- bias and the risk plan "
                "disagree this run; see Decision Reasoning below.\n\n"
            )
        elif raw_bias_val == "BULLISH":
            direction_box = (
                f"{c_green}=========================================================================\n"
                f"    THIS ANALYSIS IS FOR A LONG\n"
                f"========================================================================={reset}\n\n"
            )
        elif raw_bias_val == "BEARISH":
            direction_box = (
                f"{c_red}=========================================================================\n"
                f"    THIS ANALYSIS IS FOR A SHORT\n"
                f"========================================================================={reset}\n\n"
            )
        else:
            direction_box = ""

        panel = (
            f"{header_banner}"
            f"{box_top}{title_line}{box_mid}"
            # 13 OCTOBER 2026, the fallback sweep (DECISIONS, "Ruling, 13
            # October 2026 -- the fallback sweep"): BIAS, REGIME, STRUCTURE,
            # Vol, SEQUENCE, VOLUME, VALIDATION, VOLATILITY, RISK REGIME and
            # STATUS below fell back to readings -- NEUTRAL, NEUTRAL
            # STRUCTURE, NORMAL, NONE, WEAK OR CONTRARY VOLUME, WEAK, LOW,
            # NORMAL RISK, ACTIVE ENTRY ZONE. The router writes every one of
            # these keys on every decision it builds, so none could fire on
            # the engine's path. Absent, each now reads the router's own
            # fallback for the same key, as TREND's did from F9.
            f"BIAS       : {colorize_val(bias.get('detailed', bias.get('raw', 'UNKNOWN')))}\n"
            # ROUND 8, patch 2 of the 12 October additions, 13 October 2026
            # (DECISIONS, "Ruling, 13 October 2026 -- the fallback sweep",
            # point 6): two readings were printed twice. A REGIME line stood
            # here, printing bias['regime'] -- calculate_dynamic_regime's read
            # of the STRUCTURE column, which calculate_structure fills with the
            # same result['regime'] this line prints as structure['regime'].
            # It is gone: STRUCTURE prints the value at its source. This line
            # also carried "| Vol:" with bias['volatility'], the reading the
            # VOLATILITY line below prints; the field is gone, and VOLATILITY
            # prints it alone. The decision object keeps bias.regime and
            # bias.volatility; only the panel prints each reading once.
            f"STRUCTURE  : {colorize_val(structure.get('regime', 'UNKNOWN STRUCTURE'))}\n"
            f"SEQUENCE   : {colorize_val(structure.get('sequence', 'UNKNOWN'))}\n"
            # THE REDESIGN'S STAGE 5, 15 November 2026. Two lines stood here
            # and are gone with the readings they printed:
            #
            #     TREND      : <trend_direction> / <momentum_mode> (Score: <trend_health>)
            #     VALIDATION : <validation_state> (Score: <validation_score>)
            #
            # All five readings have left the decision object. The direction
            # the engine acts on is the BIAS line above, which has been the
            # EMAs' since stage 2; what the macro says about it is the MACRO
            # NOTE line below, and the gates are in Decision Reasoning.
            f"VOLUME     : {colorize_val(structure.get('volume_sentiment', 'UNKNOWN VOLUME'))}\n"
            f"VOLATILITY : {colorize_val(bias.get('volatility', 'UNKNOWN'))}\n"
            # ITEM 14 RE-AUDIT (Finding 5): the independent risk classification
            # that now caps the AGGRESSIVE action label -- see
            # decision_model.py's _determine_final_action. Shown so the
            # reasoning in Decision Reasoning below ("the risk regime is HIGH
            # VOLATILITY RISK") points at something visible on the panel.
            f"RISK REGIME: {colorize_val(risk.get('risk_regime', 'UNKNOWN RISK'))}\n"
            f"MACRO TREND: {colorize_val(macro_bias)}\n"
            # Stage 5, 15 November 2026: the macro note, beside the reading it
            # is about, where the draft's section 4 puts it. It is what
            # survives the Validation Notes section at the foot of the panel.
            f"MACRO NOTE : {macro_note}\n\n"
            f"{divider}"
            f"{current_price_line}"
            f"{live_price_line}"
            f"{_entry_zone_lines(entry, c_cyan, reset)}"
            # Stage 4, 15 November 2026: STATUS is the close's POSITION
            # against the EMA band -- INSIDE THE BAND, ABOVE THE BAND,
            # BELOW THE BAND -- and no longer a distance in band widths
            # (ACTIVE ENTRY ZONE, NEAR ZONE, APPROACHING ZONE, AWAY FROM
            # ZONE, ZONE HAS NO WIDTH, whose 1, 2 and 3.5 no ruling set).
            # It is printed FROM entry.close_inside_band, the same field
            # the AGGRESSIVE tier reads, so the word here cannot disagree
            # with the tier (models/entry_model.py; Viktor's ruling of
            # 7 November 2026). ZONE NOT AVAILABLE and NO DATA stay.
            f"STATUS        : {colorize_val(entry.get('entry_status', 'UNKNOWN'))}\n"
            f"{_gate_lines(entry, bias)}"
            f"{swing_struct_line}\n"
            f"{plan_lines}\n"
            f"{divider}"
            f"{_entry_quality_lines(entry, entry_score)}"
            # THE REDESIGN'S STAGE 5, 15 November 2026: a divider, then
            #
            #     CONFIDENCE (decision): <confidence_score>
            #     TRADE QUALITY :
            #         |-- Proposed Entry    : <trade_quality_proposed>
            #
            # stood here. Both numbers have left the decision object: the
            # first was the weighted sum's magnitude, the second was entry
            # quality under a second name, and ENTRY QUALITY with the D, the
            # H and their two ATR distances is printed just above.
            f"{box_top}"
            f"DECISION      : {colored_action}\n\n"
            f"{direction_box}"
            f"{divider}"
            f"Decision Reasoning:\n"
            f"{reasoning_lines}\n"
            f"{divider}"
            f"Exit Watch (advisory only -- not automatic):\n"
            f"{exit_watch_lines}\n"
            # Stage 5, 15 November 2026: a divider and
            #
            #     Validation Notes:
            #      - <validation_note>
            #
            # stood here, printing the macro and volume notes joined. The
            # volume note is gone with volume_agreement and the macro note is
            # on the MACRO NOTE line above.
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