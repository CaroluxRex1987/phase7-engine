"""
Exit-side logic for the Phase-7 engine.

SEQUENCE ITEM 5b removed `compute_exit` from this file. What it was, why it
went, and what replaced it:

It took the price frame, the entry signals and the risk block, and returned six
keys — final_action, exit_reason, stop_loss, target_hit, exit_status and
current_price. It read as the engine's exit-management brain: stop-loss
evaluated before targets, three target tiers, PARTIAL EXIT versus EXITED
status.

Five of those six keys reached nothing. signal_router.py:265 assembles the
decision object's "exit" entry itself, as {"action": <DecisionModel's
final_action>, "current_price": ...}, so everything else was dropped one call
later. The panel does print a stop loss, but reads risk["atr_stop"]. The panel
does print a DECISION, but that is DecisionModel's verdict, not this one — the
key names collided, which is how this survived earlier reads of the file
including mine.

The sixth key, current_price, was float(price_data["close"].iloc[-1]) computed
from the same frame on which engine_core had already evaluated exactly that
expression. It is now passed straight through from there.

So the deletion is output-invariant, and what looked like an exit-management
system was a stop/target ladder whose verdicts were computed every run and
thrown away. Nothing in the engine ever acted on "STOP LOSS HIT". Nothing
could — Item 18 forbids execution, and the engine holds no positions to exit.

The real exit-side feature is build_exit_watch below, which is advisory by
design and is consumed. It stays.
"""

# SEQUENCE ITEM 5b: pandas and numpy were imported for compute_exit's frame
# access and its isfinite check. build_exit_watch uses neither, so both imports
# go with it.
from typing import Dict, Any, Optional, List

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