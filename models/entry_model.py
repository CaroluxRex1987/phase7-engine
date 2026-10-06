import math
import numbers
from decimal import Decimal, ROUND_FLOOR

import numpy as np
from typing import Dict, Any, List, Optional

# AUDIT FINDING (4), 5 September 2026. What a sub-score is worth when the
# thing it scores could not be measured.
#
# Named rather than written as a bare 15.0 in four places, because this is a
# policy and it should be possible to find every application of it. The policy
# is this file's own, established by Finding 3 on 1 September: a missing input
# leaves its component at a neutral value and does NOT lower the score by
# itself. Lowering conviction is the degraded-run flag's job -- engine_core
# records the missing input, and a run carrying degraded inputs cannot
# authorise a trade regardless of what it scored. Scoring the absence twice
# would make a degraded run look like a bad setup instead of an unmeasured one.
#
# Both are the midpoint of their component's reachable range, so neither can
# be mistaken for one of the bands below it.
ZONE_POINTS_NOT_MEASURED = 15.0     # of 30
ATR_POINTS_NOT_MEASURED = 15.0      # of 25


# 5 September 2026, the "entry sub-scores do not sum to the printed total"
# observation. The five component maxima, declared once.
#
# They were literals in three places: the band values in this function, the
# "/30 /25 /20 /15 /12" denominators in panel_render.py, and the docstring.
# Three copies of one fact, which is the defect this project has now recorded
# four times. Each constant is used to award its own component's top band, so
# changing one changes the engine rather than only the label.
EMA_ZONE_MAX_POINTS = 30.0
ATR_DISTANCE_MAX_POINTS = 25.0
VWMA_MAX_POINTS = 20.0
RSI_MAX_POINTS = 15.0
STRUCTURE_MAX_POINTS = 12.0

# 102, not 100. The docstring below said "Max points: 100" while listing five
# components that add to 102, and the final clip to 100 hid the discrepancy.
# Summed rather than written out, so it cannot disagree with the five above.
COMPONENT_MAX_POINTS = (EMA_ZONE_MAX_POINTS + ATR_DISTANCE_MAX_POINTS
                        + VWMA_MAX_POINTS + RSI_MAX_POINTS
                        + STRUCTURE_MAX_POINTS)

# The ceiling the final score is clipped to, after the confluence multipliers.
# With all three multipliers at their maximum a perfect setup reaches
# 102 x 1.05^3 = 118.08, so this clip discards real headroom on the best
# setups. That is a deliberate choice -- the score is presented out of 100 --
# but it was invisible, so the result now carries score_clipped and the panel
# says when it fired.
SCORE_CEILING = 100.0

# ROUND 6 (Meta Muse Spark 1.3), F1 -- T2-4 Explicit Configuration, Moderate.
# The confluence ladder below applied bare 1.05 / 0.90 literals six times,
# with no name at module scope -- decision_log.module_snapshot() cannot see a
# constant that was never bound to a name, so a run that used 0.90 and a run
# that used 0.85 were indistinguishable in the record even though every entry
# score, and possibly AGGRESSIVE eligibility, differs between them. RULED,
# 13 September 2026: fix. Two named constants replace all six literals --
# one boost, one penalty, shared by all three ladders (macro, trend,
# structure) exactly as the six unnamed literals were. Registered in
# core/decision_log.py's FINGERPRINTED_MODULES alongside this module's other
# scoring constants. Values unchanged -- this names what was already there,
# it does not change what any run decides.
CONFLUENCE_BOOST_MULT = 1.05
CONFLUENCE_PENALTY_MULT = 0.90

def calculate_entry_quality(
    df: Optional[Any],
    zone_lower: float,
    zone_upper: float,
    macro_bias: str = "NEUTRAL",
    trade_direction: str = "LONG",
    trend_direction: str = "NEUTRAL",
    structure_sequence: str = "NONE",
) -> Dict[str, Any]:
    """
    Calculates real, quantitative sub-scores and total score for entry quality,
    fully integrated with Macro Trend Confluence and comprehensive NaN handling.

    - EMA Zone Position : 30 pts
    - ATR Distance      : 25 pts
    - VWMA Distance     : 20 pts
    - RSI Extension     : 15 pts
    - Structure         : 12 pts
                          ------
    subtotal              102 pts, then x confluence, then clipped to 100

    5 SEPTEMBER 2026. This said "Max points: 100" directly above five
    components that add to 102, and the panel printed a total the five printed
    sub-scores did not add up to. On the pinned fixture: 10 + 5 + 10 + 10 + 4
    = 39 printed under a total of 45.18. Not wrong -- unexplained, which for a
    number an operator is meant to act on is its own defect.

    Three things made up the gap and none of them was on the panel:

      1. The sub-scores were rounded to whole numbers for display while the
         total was computed from the unrounded values. ATR distance was
         5.0297, printed as 5.
      2. Three confluence multipliers (macro, trend, structure) are applied
         AFTER the sum, each 0.90, 1.00 or 1.05. On that run all three were
         1.05, so the subtotal of 39.03 became 45.18.
      3. The result is clipped to 100, and the components plus the maximum
         multipliers reach 118.08, so the clip is not decorative.

    The sub-scores are returned unrounded, so they sum to base_score exactly,
    and base_score, the three multipliers, their product and score_clipped are
    all returned and printed. The arithmetic now reconciles on the panel.
    (Macro alignment, trend direction, and structure sequence each act as a
    small multiplier/adjuster -- see section 6 below. Roadmap Layer 5: this
    was previously just the single macro multiplier; trend_direction and
    structure_sequence are new inputs, using signals that already existed
    elsewhere in the engine (trend_health.py's new trend_direction field,
    structure.py's B2 sequence detection) but weren't yet factored into
    entry quality itself.)
    """
    default_response = {
        "score": 0.0,
        "ema_pos_pts": 0,
        "atr_dist_pts": 0,
        "vwma_pts": 0,
        "rsi_pts": 0,
        "struct_pts": 0,
        "entry_status": "NO DATA",
        "base_score": 0.0,
        "component_max_points": float(COMPONENT_MAX_POINTS),
        "macro_multiplier": 1.0,
        "trend_multiplier": 1.0,
        "structure_multiplier": 1.0,
        "combined_multiplier": 1.0,
        "scaled_score": 0.0,
        "score_ceiling": float(SCORE_CEILING),
        "score_clipped": False,
        # AUDIT FINDING (4), 5 September 2026: this was 0.0, which the panel
        # printed as "0.00% away from zone" -- price sitting exactly on a zone
        # that does not exist, on a run that had no data at all. NaN is how
        # this engine spells "not located"; panel_render prints it as such.
        "distance_from_zone": float("nan")
    }

    if df is None or getattr(df, "empty", True):
        return default_response

    # Validate and clean inputs
    def safe_float(value: Any, fallback: float) -> float:
        """Safely extract float value with fallback."""
        try:
            if value is None or not np.isfinite(value):
                return fallback
            return float(value)
        except (ValueError, TypeError):
            return fallback

    # AUDIT FINDING (4), 5 September 2026. These three lines were:
    #
    #     close      = safe_float(..., 1.0)
    #     zone_lower = safe_float(zone_lower, close * 0.99)
    #     zone_upper = safe_float(zone_upper, close * 1.01)
    #
    # Three fabrications in three lines, and the worst of them is the first: a
    # close price that could not be read became $1.00, and every distance,
    # ratio and percentage below is measured against it.
    #
    # The zone pair is the finding proper. A missing zone became a band one
    # percent either side of the last price -- a number with no relationship
    # to this instrument, to its EMAs, or to anything that was measured. It
    # then scored the 30-point EMA position component AND, through
    # dist_to_mid, the 25-point ATR distance component: 55 of 100 derived from
    # a constant. engine_core supplied the same fabrication from the other
    # side, which is why this took two files to fix.
    close = safe_float(
        df["close"].iloc[-1]
        if "close" in df.columns and not df["close"].empty else None,
        float("nan"))

    if not np.isfinite(close) or close <= 0:
        # No price, no distances, no percentages. This is what
        # default_response exists for, and it was being bypassed by the 1.0.
        return dict(default_response)

    zone_lower = safe_float(zone_lower, float("nan"))
    zone_upper = safe_float(zone_upper, float("nan"))
    zone_available = bool(np.isfinite(zone_lower) and np.isfinite(zone_upper))

    # Ensure zone bounds are logical. Kept as a guard even though engine_core
    # now orders them before calling: this function is public and takes the
    # two bounds as separate arguments, so it cannot assume its caller did.
    if zone_available and zone_lower > zone_upper:
        zone_lower, zone_upper = zone_upper, zone_lower

    # ============================================================
    # 1. EMA ZONE POSITION SCORING (Max 30)
    # ============================================================
    if not zone_available:
        # dist_to_mid is what section 2 measures the ATR distance with, so an
        # absent zone neutralises that component too. Set to NaN here and
        # handled there; a number would be a distance from a zone that was
        # never located.
        dist_to_mid = float("nan")
        ema_pos_pts = ZONE_POINTS_NOT_MEASURED
        entry_status = "ZONE NOT AVAILABLE"
        distance_from_zone = float("nan")
    else:
        zone_mid = (zone_lower + zone_upper) / 2.0
        zone_width = abs(zone_upper - zone_lower)
        dist_to_mid = abs(close - zone_mid)
        distance_from_zone = float((dist_to_mid / close) * 100.0)

        if zone_width <= 1e-8:
            # AUDIT FINDING (4), the third fabrication: this line was
            #     zone_width = close * 0.01   # Default to 1% of current price
            # A zero-width zone is a REAL state -- the two EMAs have crossed
            # and coincide -- and one percent of price is not a measurement of
            # it. Substituting a width also silently re-scaled all three bands
            # below, which are multiples of that width.
            #
            # There is no proportional band to place price in when the zone has
            # no width, so the component is not scored. Whether a coincident
            # pair of EMAs should instead be banded on distance as a
            # PERCENTAGE of price is a design question, not a defect, and is
            # left open rather than decided here. distance_from_zone above is
            # still real and still printed.
            ema_pos_pts = ZONE_POINTS_NOT_MEASURED
            entry_status = "ZONE HAS NO WIDTH"
        elif dist_to_mid <= zone_width:
            ema_pos_pts = EMA_ZONE_MAX_POINTS
            entry_status = "ACTIVE ENTRY ZONE"
        elif dist_to_mid <= zone_width * 2.0:
            ema_pos_pts = 20
            entry_status = "NEAR ZONE"
        elif dist_to_mid <= zone_width * 3.5:
            ema_pos_pts = 10
            entry_status = "APPROACHING ZONE"
        else:
            ema_pos_pts = 5
            entry_status = "AWAY FROM ZONE"

    # ============================================================
    # 2. ATR DISTANCE SCORING (Max 25)
    # ============================================================
    # FINDING 3 RE-AUDIT, 1 September 2026: the fallback here was
    # `close * 0.02` -- the same flat 2%-of-price constant sequence item 9a
    # deleted from indicators.py, still living in the consumer that reads the
    # column. On this repo's own pinned fixture the real ATR is 0.010554 and
    # the fallback is 0.016035: a 52% overstatement of how much this
    # instrument moves, fed straight into the ATR-distance score.
    #
    # A missing ATR now leaves atr_dist_pts at the same neutral default the
    # unusable-ratio branches below already use, rather than scoring a
    # distance measured against a number nobody computed. Same treatment VWMA
    # got at item 3, twenty lines down.
    atr = safe_float(df["ATR"].iloc[-1] if "ATR" in df.columns and not df["ATR"].empty else None,
                     float("nan"))

    # AUDIT FINDING (4): dist_to_mid is NaN when the zone could not be
    # located, and this component measures a distance TO that zone. Without
    # one there is nothing to divide by ATR. Previously unreachable, because
    # the zone was always fabricated into existence above.
    if np.isfinite(atr) and atr > 0 and np.isfinite(dist_to_mid):
        try:
            atr_ratio = dist_to_mid / atr
            if np.isfinite(atr_ratio):
                # Smooth exponential decay instead of hard thresholds
                atr_dist_pts = float(ATR_DISTANCE_MAX_POINTS
                                     * np.exp(-atr_ratio * 0.5))
                atr_dist_pts = max(5.0, min(ATR_DISTANCE_MAX_POINTS,
                                            atr_dist_pts))
            else:
                atr_dist_pts = ATR_POINTS_NOT_MEASURED
        except (ZeroDivisionError, OverflowError):
            atr_dist_pts = ATR_POINTS_NOT_MEASURED
    else:
        atr_dist_pts = ATR_POINTS_NOT_MEASURED

    # ============================================================
    # 3. VWMA DISTANCE SCORING (Max 20)
    # ============================================================
    vwma_pts = 15.0  # Default score
    if "VWMA" in df.columns and not df["VWMA"].empty:
        # ITEM 3 RE-AUDIT (Finding 1): this used
        #     vwma = safe_float(df["VWMA"].iloc[-1], close)
        # -- close as the fallback whenever the last VWMA value was NaN.
        # indicators.py now leaves VWMA as NaN for exactly the windows with no
        # usable volume measurement (all-zero or invalid volume_sum), rather
        # than fabricating a close-price substitute -- see
        # indicators/indicators.py's VWMA block. This was the second half of
        # the same defect: even a genuinely-missing VWMA reached here and was
        # quietly replaced by `close`, making `vwma_diff` exactly zero and
        # awarding the full 20 points for a distance that was never measured.
        # "Fix the helper, not just the branch" -- the source stopped
        # fabricating a value, and this consumer was the branch still reading
        # one.
        #
        # A missing VWMA now leaves vwma_pts at its neutral default above,
        # the same treatment the column-absent case already got two lines up.
        vwma_raw = df["VWMA"].iloc[-1]
        if np.isfinite(vwma_raw) and close > 0:
            vwma = float(vwma_raw)
            try:
                vwma_diff = abs(close - vwma) / close
                if np.isfinite(vwma_diff):
                    if vwma_diff < 0.01:
                        vwma_pts = VWMA_MAX_POINTS
                    elif vwma_diff < 0.025:
                        vwma_pts = 15.0
                    elif vwma_diff < 0.05:
                        vwma_pts = 10.0
                    else:
                        vwma_pts = 5.0
            except (ZeroDivisionError, OverflowError):
                vwma_pts = 15.0

    # ============================================================
    # 4. RSI EXTENSION SCORING (Max 15)
    # ============================================================
    rsi_pts = 10.0  # Default score
    if "RSI" in df.columns and not df["RSI"].empty:
        # FINDING 3 RE-AUDIT, 1 September 2026: the fallback was 50.0 -- the
        # exact "perfectly balanced" constant sequence item 9a removed from
        # indicators.py, and the worst possible choice here. 50 sits inside the
        # 40-60 band, so a missing RSI scored the FULL 15 of 15: top marks for
        # "not extended", awarded for a measurement that was never taken.
        # indicators.py's own failure text for RSI tells the operator this
        # "scores RSI extension at 0 of 15"; the code did the opposite.
        #
        # Now a missing RSI leaves rsi_pts at the neutral default set above,
        # which is also what the column-absent case gets one line up.
        rsi = safe_float(df["RSI"].iloc[-1], float("nan"))

        if not np.isfinite(rsi):
            pass  # neutral default stands; nothing was measured to score
        elif 40.0 <= rsi <= 60.0:
            rsi_pts = RSI_MAX_POINTS
        elif 30.0 <= rsi < 40.0 or 60.0 < rsi <= 70.0:
            rsi_pts = 10.0
        else:
            rsi_pts = 5.0

    # ============================================================
    # 5. STRUCTURE PROXIMITY SCORING (Max 12)
    # ============================================================
    struct_pts = 6.0  # Default score
    if "HVN" in df.columns and not df["HVN"].empty:
        # FINDING 3 RE-AUDIT, 1 September 2026: the fallback was `close` --
        # byte-for-byte the same defect item 3 fixed for VWMA forty lines up,
        # sitting untouched next to it. close as the fallback makes
        # `abs(close - hvn) / close` exactly zero, which lands in the
        # `< 0.015` band and awards the FULL 12 of 12 structure points for a
        # high-volume node that was never located.
        #
        # Item 3 fixed the instance it was looking at and left its twin. That
        # is rule 22 of docs/PHASE7_DECISIONS.md's list ("Fixing the instance
        # you found does not close the item"), applied to the item that wrote
        # it. Cited here as rule 18 until 20 September 2026: the same commit
        # that wrote this comment, 108cc9f, renumbered the list.
        hvn = safe_float(df["HVN"].iloc[-1], float("nan"))

        if np.isfinite(hvn) and close > 0:
            try:
                hvn_dist = abs(close - hvn) / close
                if np.isfinite(hvn_dist):
                    if hvn_dist < 0.015:
                        struct_pts = STRUCTURE_MAX_POINTS
                    elif hvn_dist < 0.03:
                        struct_pts = 8.0
                    else:
                        struct_pts = 4.0
            except (ZeroDivisionError, OverflowError):
                struct_pts = 6.0

    base_score = float(ema_pos_pts + atr_dist_pts + vwma_pts + rsi_pts + struct_pts)

    # ============================================================
    # 6. CONFLUENCE MULTIPLIERS & FINAL BOUNDS (Roadmap Layer 5)
    # ============================================================
    # Each multiplier is independently small (+-5-10%) and only nudges the
    # score -- none of them can gate a trade on their own (generate_entry_signals
    # already handles hard gating). Combined, they let entry quality reflect
    # not just "is price near a good zone" but "does the broader context this
    # trade would be entering into actually support this specific direction."
    macro_multiplier = 1.0
    if macro_bias == "BULLISH" and trade_direction == "LONG":
        macro_multiplier = CONFLUENCE_BOOST_MULT
    elif macro_bias == "BEARISH" and trade_direction == "SHORT":
        macro_multiplier = CONFLUENCE_BOOST_MULT
    elif macro_bias not in ["NEUTRAL", ""] and macro_bias != trade_direction:
        macro_multiplier = CONFLUENCE_PENALTY_MULT

    # Trend direction alignment: trend_health.py's EMA-slope-based direction
    # label agreeing (or disagreeing) with the direction being scored here.
    trend_multiplier = 1.0
    if trade_direction == "LONG":
        if trend_direction == "BULLISH":
            trend_multiplier = CONFLUENCE_BOOST_MULT
        elif trend_direction == "BEARISH":
            trend_multiplier = CONFLUENCE_PENALTY_MULT
    elif trade_direction == "SHORT":
        if trend_direction == "BEARISH":
            trend_multiplier = CONFLUENCE_BOOST_MULT
        elif trend_direction == "BULLISH":
            trend_multiplier = CONFLUENCE_PENALTY_MULT

    # Structure sequence alignment: a BOS (continuation) in this trade's own
    # direction is rewarded; a CHOCH (possible reversal) against this trade's
    # direction is penalized. An established (non-BOS) swing sequence in this
    # trade's direction, or "NONE"/anything else, is left neutral -- BOS is a
    # stronger continuation signal than a plain swing sequence, so only BOS
    # earns the reward tier here.
    structure_multiplier = 1.0
    if trade_direction == "LONG":
        if structure_sequence == "BOS BULLISH (TREND CONTINUATION)":
            structure_multiplier = CONFLUENCE_BOOST_MULT
        elif structure_sequence == "CHOCH BEARISH (POSSIBLE REVERSAL)":
            structure_multiplier = CONFLUENCE_PENALTY_MULT
    elif trade_direction == "SHORT":
        if structure_sequence == "BOS BEARISH (TREND CONTINUATION)":
            structure_multiplier = CONFLUENCE_BOOST_MULT
        elif structure_sequence == "CHOCH BULLISH (POSSIBLE REVERSAL)":
            structure_multiplier = CONFLUENCE_PENALTY_MULT

    combined_multiplier = macro_multiplier * trend_multiplier * structure_multiplier
    scaled_score = base_score * combined_multiplier
    total_score = float(min(SCORE_CEILING, max(0.0, scaled_score)))

    # 5 September 2026: the five sub-scores were returned as int() and
    # int(round()) while total_score was computed from the unrounded values,
    # so the printed components could not add up to the printed total even
    # before the multipliers were applied. ATR distance was the one that
    # showed it -- 5.0297 printed as 5.
    #
    # Returned unrounded. They now sum to base_score exactly, and the panel
    # formats them for display rather than the model rounding on its behalf.
    # (The panel prints two decimals, so the displayed values can still differ
    # from the displayed subtotal in the last digit by ordinary rounding; the
    # exact values are here and in the decision log.)
    return {
        "score": float(total_score),
        "ema_pos_pts": float(ema_pos_pts),
        "atr_dist_pts": float(atr_dist_pts),
        "vwma_pts": float(vwma_pts),
        "rsi_pts": float(rsi_pts),
        "struct_pts": float(struct_pts),
        "entry_status": str(entry_status),
        "distance_from_zone": float(distance_from_zone),

        # The reconciliation, so the panel does not have to reconstruct it and
        # the decision log carries it. Every one of these was previously a
        # local variable that vanished when the function returned.
        "base_score": float(base_score),
        "component_max_points": float(COMPONENT_MAX_POINTS),
        "macro_multiplier": float(macro_multiplier),
        "trend_multiplier": float(trend_multiplier),
        "structure_multiplier": float(structure_multiplier),
        "combined_multiplier": float(combined_multiplier),
        "scaled_score": float(scaled_score),
        "score_ceiling": float(SCORE_CEILING),
        "score_clipped": bool(scaled_score > SCORE_CEILING or scaled_score < 0.0),
    }


# WORK ORDER F, 21 September 2026 -- the confirmation gate.
#
# Finding 11 of the 21 September pre-backtest review: long_signal and
# short_signal were computed on every run, carried into the decision object,
# the decision log and the simulated order -- and read by nothing that
# decides. The record could show `long_signal: False` beside an AGGRESSIVE
# LONG. They had been left in `entry` on 2 September "for a future ruling on
# whether they should CONFIRM a direction bias has already chosen" (see
# decision_model.py). That ruling is now made.
#
# VIKTOR'S RULING, 21 September 2026: the signal CONFIRMS. A trade the
# decision ladder chooses is taken only if the signal for its side holds;
# otherwise the action is NO-TRADE (SIGNAL UNCONFIRMED). He wrote the rule
# first; Claude critiqued it; he then delegated the remaining adjustments
# ("Make the adjustments you want and do what is best for the engine and the
# project"). What each old condition became, and whose call it was:
#
#   macro_bias not opposed      REMOVED -- Viktor. Macro is already a 10%
#                               factor inside bias_score; a veto lets the same
#                               evidence vote twice.
#   detailed_bias == CONFIRMED  REMOVED -- Viktor. decision_model chooses on
#                               raw_bias; a second, stricter bias threshold
#                               here was a conflict between two modules. The
#                               consequence, recorded: the bias state
#                               machine's persistence requirement no longer
#                               gates a trade anywhere.
#                               CORRECTED 27 September 2026 (finding 18):
#                               there was no persistence requirement. The
#                               state machine never read its previous state,
#                               so CONFIRMED only ever meant |bias_score| >
#                               30 -- and the ladder already needs >= 30
#                               (MIN_ACTION_BIAS) to act. What stopped gating
#                               here was that threshold, which differs from
#                               the ladder's only at exactly 30.0. The class
#                               is now bias_label (models/bias_engine.py).
#   trend_health >= 50          REMOVED -- Claude, under the delegation. It
#                               decided nothing: every trading branch of the
#                               ladder already requires trend_health >= 50
#                               (CONSERVATIVE_TREND_HEALTH_MIN) or >= 75.
#   reversal_strength > 0       REPLACED BY ITS PARTS -- Viktor. The number
#                               is a sum of named components (trend_health.py,
#                               section 7), so a cut-off would silently decide
#                               which combinations block. HVN proximity alone
#                               no longer blocks: it was a second HVN veto
#                               beside the stop pulled to the 75-day HVN.
#                               DEPENDENCY, recorded: if finding 6 is later
#                               ruled to stop pulling the stop to the HVN,
#                               nothing checks HVN proximity at all.
#                               IN FORCE since 27 September 2026: finding 6
#                               was so ruled, and no gate checks HVN
#                               proximity. It still weighs -- the entry
#                               score's structure points and trend_health's
#                               reversal reading read it -- but vetoes
#                               nothing. On the list for after the audit
#                               (Viktor, point 3 of the finding 6 ruling).
#   trend exhaustion            KEPT -- Viktor. Structure must match the side,
#                               so every confirmed trade runs with the trend,
#                               and exhaustion is always against it.
#                               REPLACED 5 October 2026 (fix 2, below): ADX
#                               under MIN_TREND_ADX blocks both sides in its
#                               place, and the flag no longer reaches the gate.
#   momentum divergence         BLOCKS ONLY WHEN IT POINTS AGAINST THE TRADE --
#                               Viktor. decision_model's own direction-blind
#                               divergence check on the upper tiers is removed
#                               in the same change so the engine has ONE
#                               divergence rule, not two that disagree --
#                               Claude, under the delegation.
#   structure regime matches    KEPT -- Viktor.
#
# Stated for the auditor: all three surviving conditions (structure regime,
# exhaustion via reversal/continuation, divergence) also reach bias_score
# as weighted factors. The gate is a hard AND on top of that blend -- a veto,
# which can refuse a trade but never adds confidence to one. That is a design
# choice. It has not been backtested; no evidence yet says it improves
# decisions.
# SINCE FIX 2 (5 October 2026) the three are structure regime, ADX and
# divergence. ADX reaches bias_score as well: it is up to 40 of trend
# health's 100 points (indicators/trend_health.py, adx_strength), and trend
# health is 30% of bias_score. The gate still only vetoes.
#
# Checked against the live decision log before writing (21 September, 29
# records): no past action would change. One SHORT was taken in that log
# (code 38458f20...); its reversal reading of 4.0 was HVN proximity alone,
# so it passes under this rule where the old signal refused it.

# FIX 2, 5 October 2026 -- no trend, no trade. Point 4 of round 8's triage
# (docs/PHASE7_DECISIONS.md, "Ruling, 5 October 2026 -- round 8 triaged
# ..."; the review's B3), Viktor's ruling by agreeing to Claude's suggestion:
# the exhaustion flag leaves this gate, and ADX under 20 blocks both sides,
# with the reason printed. It implements point 9 of the ruling of
# 28 September, "trends only, for now".
#
# Why the flag goes: it was (this bar's range > the last bar's AND ADX < 20)
# OR (trend health < 35 AND ADX < 15) (indicators/trend_health.py, section
# 4). Trend health is almost never under 35, so in practice it asked whether
# the last candle was wider than the one before it, in a low-ADX market --
# on the review's count of real 4h bars (not re-derived here) it fired on
# about half of the bars with ADX under 20 and on none above. Both of its
# clauses need ADX under 20, so every setup it blocked is still blocked.
#
# An ADX with no valid reading -- None (trend_health.py could not read it),
# NaN, an infinity, a bool, anything that is not a number, or a number
# outside ADX's own 0-100 range -- blocks both sides too, with its own
# reason. The ruling left this to the patch, failing safe: a reading that
# does not exist cannot show a trend, so it cannot confirm one. The run
# still completes and is recorded. In this engine such a run is already
# degraded (trend_health.py names the missing ADX), and the gate runs before
# the degradation override, so when the ladder chose a side the label is
# NO-TRADE (SIGNAL UNCONFIRMED) with the degradation notes appended to it --
# the precedence work order F set -- where it was NO-TRADE (DEGRADED INPUT).
#
# The flag itself is unchanged and still read everywhere else it was: trend
# health's reversal reading, the trend-regime label, Exit Watch and the
# record (trend.exhaustion). Only this gate stops reading it.
#
# 20 is the level the risk regime reads as chop (models/risk_model.py,
# REGIME_CHOP_ADX): chosen, not derived, and not backtested. It is its own
# constant here, fingerprinted in core/decision_log.py, because the regime's
# two ADX tests are to be removed (point 3 of the same triage).
#
# Checked against the live decision log (5 October, 48 records; records
# 1-10 are test records). ADX was under 20 on one live run, record 47
# (18.43, a WAIT: the ladder chose no side, so the gate decided nothing),
# and the exhaustion flag fired on no record. Replayed through
# DecisionModel.evaluate() with every other input held at its recorded
# value, no record's action differs before and after this fix. The blockers
# change on two records: 47 gains the ADX reason on both sides, and test
# record 4, which has no ADX at all, gains the no-reading reason on both.
# The confirmation sentence changes on the seven records whose replay
# confirms a side (19, 20, 21, 42, 43, 44 and 48).
MIN_TREND_ADX = 20.0


def _measured_adx(adx: Any) -> Optional[float]:
    """
    The ADX as a float, or None when there is no valid reading.

    A bool is a number to Python and not a reading; NaN and the infinities
    are not readings either; and ADX is bounded to 0-100 by its definition,
    so a value outside that range is a defect upstream, not a market. Every
    one of these returns None, which the gate treats as no trend shown.
    """
    if isinstance(adx, bool) or not isinstance(adx, numbers.Real):
        return None
    value = float(adx)
    if not math.isfinite(value) or value < 0.0 or value > 100.0:
        return None
    return value


def _adx_text(adx: float) -> str:
    """
    A valid ADX under MIN_TREND_ADX, as its blocker prints it: one decimal,
    rounded DOWN, so 19.96 reads "19.9" and never "20.0, under the 20".
    Decimal(repr(...)) floors the float's shortest decimal form exactly,
    which multiplying the float by ten and flooring cannot promise.
    """
    return str(Decimal(repr(float(adx))).quantize(Decimal("0.1"),
                                                  rounding=ROUND_FLOOR))


def signal_blockers(
    direction: str,
    structure_regime: str,
    momentum_divergence: bool,
    divergence_direction: str,
    *,
    adx: Any,
) -> List[str]:
    """
    Every reason the setup does NOT confirm a trade in `direction` ("LONG" or
    "SHORT"). An empty list is a confirmation; the signal is exactly that.

    `adx` is keyword-only and has no default (fix 2): a call in the shape
    before fix 2 -- the exhaustion flag third, five positional arguments --
    raises TypeError instead of binding the flag to another parameter.
    """
    if direction not in ("LONG", "SHORT"):
        raise ValueError(f"direction must be LONG or SHORT, got {direction!r}")

    wanted_structure = "BULLISH TREND" if direction == "LONG" else "BEARISH TREND"
    opposing = "BEARISH" if direction == "LONG" else "BULLISH"
    blockers: List[str] = []

    if structure_regime != wanted_structure:
        blockers.append(f"structure is {structure_regime}, not {wanted_structure}")

    measured = _measured_adx(adx)
    if measured is None:
        blockers.append(
            "ADX has no valid reading on this run, so the market cannot be "
            "shown to be trending")
    elif measured < MIN_TREND_ADX:
        blockers.append(
            f"ADX is {_adx_text(measured)}, under the {MIN_TREND_ADX:g} the "
            f"engine requires to treat the market as trending")

    if momentum_divergence:
        if divergence_direction == opposing:
            blockers.append(
                f"{opposing.lower()} momentum divergence points against the trade")
        elif divergence_direction not in ("BULLISH", "BEARISH"):
            # A divergence whose direction was not recorded cannot be shown
            # NOT to point against the trade, so it is not a confirmation.
            blockers.append(
                "momentum divergence is present but its direction is "
                f"{divergence_direction!r}, so it cannot be shown not to point "
                "against the trade")

    return blockers


def generate_entry_signals(
    structure_regime: str,
    momentum_divergence: bool,
    divergence_direction: str,
    *,
    adx: Any,
) -> Dict[str, Any]:
    """
    Both sides' confirmation signals and the reasons behind each.

    Returns long_signal / short_signal (True exactly when that side's blocker
    list is empty) and long_signal_blockers / short_signal_blockers. Both
    sides are recorded so the decision log shows why each was or was not
    confirmed, not only the side that was traded.
    """
    long_blockers = signal_blockers(
        "LONG", structure_regime, momentum_divergence, divergence_direction,
        adx=adx)
    short_blockers = signal_blockers(
        "SHORT", structure_regime, momentum_divergence, divergence_direction,
        adx=adx)
    return {
        "long_signal": not long_blockers,
        "short_signal": not short_blockers,
        "long_signal_blockers": long_blockers,
        "short_signal_blockers": short_blockers,
    }
