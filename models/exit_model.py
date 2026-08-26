import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List

def compute_exit(
    price_data: Optional[pd.DataFrame],
    entry_data: Optional[Dict[str, Any]],
    risk_data: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Phase-7 Exit Logic Wrapper
    Institutional-grade version featuring prioritized stop evaluation,
    safe unpacking, and comprehensive error containment.
    """
    # ============================================================
    # VALIDATION
    # ============================================================
    if price_data is None or not hasattr(price_data, "__getitem__") or getattr(price_data, "empty", True):
        return {"error": "Invalid or empty price_data"}

    if entry_data is None or not isinstance(entry_data, dict):
        return {"error": "Invalid entry_data dictionary"}

    if risk_data is None or not isinstance(risk_data, dict):
        return {"error": "Invalid risk_data dictionary"}

    # ============================================================
    # UNPACK INPUTS SAFELY
    # ============================================================
    try:
        current_price = float(price_data["close"].iloc[-1])
        if not np.isfinite(current_price):
            return {"error": "Current price is non-finite"}
    except Exception:
        return {"error": "Invalid price_data structure or missing close column"}

    try:
        atr_stop = float(risk_data["atr_stop"])
        targets = risk_data.get("targets", [])
        if len(targets) < 3:
            # Fallback unpacking if targets are structured individually or passed differently
            target_t1 = float(risk_data.get("target_t1", current_price * 1.01))
            target_t2 = float(risk_data.get("target_t2", current_price * 1.02))
            target_t3 = float(risk_data.get("target_t3", current_price * 1.03))
        else:
            target_t1, target_t2, target_t3 = float(targets[0]), float(targets[1]), float(targets[2])
    except Exception:
        return {"error": "Invalid risk_data structure or missing targets"}

    try:
        long_signal = bool(entry_data.get("long_signal", False))
        short_signal = bool(entry_data.get("short_signal", False))
    except Exception:
        return {"error": "Invalid entry_data signal structure"}

    # ============================================================
    # EXIT CONDITIONS (PRIORITIZING STOP LOSS FIRST)
    # ============================================================
    exit_signal = "HOLD"
    exit_reason = "No exit conditions met"
    target_hit = None
    exit_status = "ACTIVE"

    if long_signal:
        if current_price <= atr_stop:
            exit_signal = "STOP LOSS HIT"
            exit_reason = "Price reached or breached ATR stop"
            target_hit = None
            exit_status = "EXITED"
        elif current_price >= target_t3:
            exit_signal = "TARGET 3 HIT"
            exit_reason = "Final target reached"
            target_hit = "T3"
            exit_status = "EXITED"
        elif current_price >= target_t2:
            exit_signal = "TARGET 2 HIT"
            exit_reason = "Intermediate target reached"
            target_hit = "T2"
            exit_status = "PARTIAL EXIT"
        elif current_price >= target_t1:
            exit_signal = "TARGET 1 HIT"
            exit_reason = "First target reached"
            target_hit = "T1"
            exit_status = "PARTIAL EXIT"

    elif short_signal:
        if current_price >= atr_stop:
            exit_signal = "STOP LOSS HIT"
            exit_reason = "Price reached or breached ATR stop"
            target_hit = None
            exit_status = "EXITED"
        elif current_price <= target_t3:
            exit_signal = "TARGET 3 HIT"
            exit_reason = "Final target reached"
            target_hit = "T3"
            exit_status = "EXITED"
        elif current_price <= target_t2:
            exit_signal = "TARGET 2 HIT"
            exit_reason = "Intermediate target reached"
            target_hit = "T2"
            exit_status = "PARTIAL EXIT"
        elif current_price <= target_t1:
            exit_signal = "TARGET 1 HIT"
            exit_reason = "First target reached"
            target_hit = "T1"
            exit_status = "PARTIAL EXIT"

    # ============================================================
    # RETURN EXIT DATA TELEMETRY
    # ============================================================
    return {
        "final_action": str(exit_signal),
        "exit_reason": str(exit_reason),
        "stop_loss": float(atr_stop),
        "target_hit": target_hit,
        "exit_status": str(exit_status),
        "current_price": float(current_price),
    }


# ============================================================
# C3 BUILD: EXIT WATCH -- advisory-only flags, never automatic actions
# ============================================================
#
# Per the fix plan's C3: the originally-planned exit triggers (trailing
# stop, break-even, trend failure, bias flip, HVN/LVN hit, SuperTrend flip,
# exhaustion, divergence) become flags you read on the panel, not a
# conflict-resolution system the engine acts on. This function collects
# whichever of those are currently true/relevant and returns them as plain
# sentences -- nothing here changes DECISION above; it's a separate,
# advisory "things to keep an eye on" list for a position you're already in
# or considering.
#
# Two of the eight (SuperTrend flip, bias flip) need to compare against the
# PREVIOUS run, since a "flip" is a change, not a snapshot. Since this tool
# is normally run as a fresh command each time (not a long-running process),
# that comparison has to come from state persisted to disk between runs --
# engine_core.py reads/writes that small state file and passes the prior
# values in as `prior_state`. If there's no prior run yet (first-ever run,
# or the state file is missing/corrupt), those two flags are simply skipped
# rather than guessed at.

def build_exit_watch(
    trend: Dict[str, Any],
    structure: Dict[str, Any],
    bias: Dict[str, Any],
    current_price: float,
    supertrend_direction: float,
    target_t1: float,
    prior_state: Optional[Dict[str, Any]] = None,
) -> List[str]:
    """
    Returns a list of plain-language advisory flags. An empty-looking
    result still returns one line saying nothing is active, so the panel
    section is never blank/ambiguous.
    """
    flags: List[str] = []
    prior_state = prior_state if isinstance(prior_state, dict) else {}

    try:
        raw_bias = str(bias.get("raw", "NEUTRAL"))
        detailed_bias = str(bias.get("detailed", "NEUTRAL"))
        sequence = str(structure.get("sequence", "NONE"))
        hvn = float(structure.get("hvn", 0.0) or 0.0)
        lvn = float(structure.get("lvn", 0.0) or 0.0)
        current_price = float(current_price) if current_price else 0.0

        # --- Trend-quality warnings (no prior-run comparison needed) ---
        if bool(trend.get("trend_failure", False)):
            flags.append(
                "Trend failure is active (a recent lower-high / lower-low pattern) — the current trend may be "
                "losing structure."
            )

        if bool(trend.get("trend_exhaustion", False)):
            flags.append(
                "Trend exhaustion is active — momentum looks stretched and may be due for a pause or pullback."
            )

        if bool(trend.get("momentum_divergence", False)):
            flags.append(
                "Momentum divergence is active — price and momentum are disagreeing, an early warning sign worth "
                "watching."
            )

        # --- Reversal signal opposing the current bias (B1) ---
        reversal_direction = trend.get("reversal_direction", "NONE")
        reversal_strength = float(trend.get("reversal_strength", 0.0) or 0.0)
        reversal_opposes = (
            (raw_bias == "BULLISH" and reversal_direction == "BEARISH")
            or (raw_bias == "BEARISH" and reversal_direction == "BULLISH")
        )
        if reversal_opposes and reversal_strength >= 40.0:
            flags.append(
                f"A {reversal_direction} reversal signal is forming against the current {raw_bias} bias "
                f"(strength {reversal_strength:.0f}/100)."
            )

        # --- CHOCH opposing the current bias (B2) ---
        choch_opposes = (
            (raw_bias == "BULLISH" and "CHOCH BEARISH" in sequence)
            or (raw_bias == "BEARISH" and "CHOCH BULLISH" in sequence)
        )
        if choch_opposes:
            flags.append(
                f"Structure just flagged {sequence} — price broke the last swing point against the prevailing "
                f"trend, an early sign of a possible reversal."
            )

        # --- Proximity to a high/low volume node ---
        if current_price > 0 and hvn > 0 and abs(current_price - hvn) / current_price * 100.0 < 1.5:
            flags.append(
                f"Price is close to a high-volume node (${hvn:.4f}) — a level where price has often reacted "
                f"before."
            )
        if current_price > 0 and lvn > 0 and abs(current_price - lvn) / current_price * 100.0 < 1.5:
            flags.append(
                f"Price is close to a low-volume node (${lvn:.4f}) — price has tended to move through these "
                f"quickly rather than react."
            )

        # --- SuperTrend flip since the last run (needs prior_state) ---
        prior_supertrend = prior_state.get("supertrend_direction")
        if prior_supertrend is not None:
            try:
                prior_supertrend = float(prior_supertrend)
                current_sign = 1 if supertrend_direction > 0 else (-1 if supertrend_direction < 0 else 0)
                prior_sign = 1 if prior_supertrend > 0 else (-1 if prior_supertrend < 0 else 0)
                if current_sign != 0 and prior_sign != 0 and current_sign != prior_sign:
                    from_side = "BULLISH" if prior_sign > 0 else "BEARISH"
                    to_side = "BULLISH" if current_sign > 0 else "BEARISH"
                    flags.append(f"SuperTrend flipped from {from_side} to {to_side} since the last run.")
            except (ValueError, TypeError):
                pass

        # --- Bias state flip since the last run (needs prior_state) ---
        prior_bias = prior_state.get("detailed_bias")
        if prior_bias and str(prior_bias) != detailed_bias:
            flags.append(f"Bias state changed from {prior_bias} to {detailed_bias} since the last run.")

        # --- Always-on informational note (not a warning) ---
        if target_t1 and float(target_t1) > 0:
            flags.append(
                f"If you're already in this trade, a common approach is moving your stop to breakeven once price "
                f"reaches Target 1 (${float(target_t1):.4f})."
            )

    except Exception as e:
        flags.append(f"Exit watch could not be fully evaluated this run ({e}).")

    if not flags:
        flags.append("No exit-watch flags are active right now — nothing here suggests changing your position early.")

    return flags