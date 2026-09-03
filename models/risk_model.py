from typing import Tuple, Union, Optional
import logging
import numpy as np

logger = logging.getLogger(__name__)

# ==================================================================
# DECISION-AFFECTING CONSTANTS
#
# These are module-level, not instance attributes, because
# core/decision_log.py's module_snapshot() fingerprints MODULE
# attributes and cannot see instance state.
#
# AUDIT FINDING 6 (Item 5) asked for "all decision-affecting
# configuration, including risk-model multipliers and bias weights."
# The bias weights were fingerprinted at that item. These were not,
# and they could not have been: they lived on the instance, where
# the mechanism cannot reach them. Two runs whose stops and every
# target differed by 25% hashed identically, and the record that
# claims to identify a run could not tell them apart.
#
# They are read DIRECTLY by the methods below. They are deliberately
# not copied onto self in __init__, because a copy restores exactly
# the gap this closes -- the snapshot would report the module value
# while the arithmetic used the instance one, and nothing would say
# which produced the plan. There is no instance state here to drift.
#
# tests/test_risk_fingerprint.py holds all of this true: that every
# name below is fingerprinted, that none of them is dead, and that
# the multipliers have not crept back onto the instance.
# ==================================================================

# Stop and target geometry.
ATR_STOP_MULT = 1.2            # base ATR multiplier for the stop
TARGET1_MULT = 1.0             # conservative target, x stop distance
TARGET2_MULT = 2.0             # normal target, x stop distance
TARGET3_MULT = 3.0             # aggressive target, x stop distance

# Volatility adjustment applied to the stop multiplier.
VOL_MULT_HIGH = 1.35           # widen stops in high vol to avoid whipsaws
VOL_MULT_LOW = 0.85            # tighter stops in calm markets
VOL_MULT_EXTREME = 1.60

# Structural influence on the stop. A strong trend pushes the stop
# further out; a strong bias pulls it back in.
TREND_FACTOR_DIVISOR = 200.0
BIAS_FACTOR_DIVISOR = 300.0

# Risk regime boundaries.
REGIME_EXTREME_STOP_PCT = 8.0
REGIME_LOW_TREND_HEALTH = 40.0
REGIME_HIGH_TREND_HEALTH = 70.0

# Hard validity limits on the stop distance.
MAX_STOP_DISTANCE_PCT = 15.0   # wider than this is not a stop, it is a hope
MIN_STOP_DISTANCE_PCT = 0.2    # tighter than this sits inside market noise


class RiskModel:
    """
    Core institutional risk engine for Phase-7.
    Provides:
        - Volatility-adjusted ATR stop calculation
        - Tiered target generation
        - Position sizing & leverage adjustment
        - Risk regime classification & advanced validation
    """

    # __init__ removed. It set four multipliers onto the instance:
    # atr_stop_mult, target1_mult, target2_mult and target3_mult. They
    # are module-level constants above now -- see the block there for
    # why. Nothing outside this file ever read the attributes, and
    # nothing assigned to them, so removing them changes no behaviour
    # and removes the only place the recorded settings and the settings
    # actually used could diverge.

    # ============================================================
    # STOP & TARGETS (WITH VOLATILITY ADJUSTMENT)
    # ============================================================

    def calculate_stop_targets(
        self,
        detailed_bias: str,
        trend_health: float,
        current_price: float,
        atr_val: float,
        structural_level: Union[float, None],
        bias_score: float,
        volatility_state: str = "NORMAL"
    ) -> Tuple[float, float, float, float]:
        """
        Compute volatility-adjusted ATR stop + tiered targets, forcing directional fallback
        if bias is neutral so targets never collapse to current price.

        Args:
            detailed_bias: Trading bias direction
            trend_health: Trend health score (0-100)
            current_price: Current market price
            atr_val: Average True Range value
            structural_level: Key structural price level
            bias_score: Bias strength score
            volatility_state: Current volatility regime

        Returns:
            Tuple of (atr_stop, target1, target2, target3)
        """
        try:
            # Input validation
            #
            # FINDING 3 RE-AUDIT, 1 September 2026: this was
            #     if current_price <= 0 or atr_val <= 0
            # and NaN fails both comparisons, because every comparison against
            # NaN is False. So a NaN ATR walked straight past the guard. With
            # no structural level it produced (nan, nan, nan, nan) -- printed
            # verbatim by the panel, whose safe_float did not check finiteness
            # either. WITH a structural level it was worse: the levels came out
            # of the structural branch and looked completely normal
            # -- (98.0, 102.0, 104.0, 106.0) in the audit's own scenario --
            # while the ATR that is supposed to set stop distance contributed
            # nothing and nothing anywhere was flagged.
            #
            # validate_risk_parameters, twenty lines below in this same file,
            # has checked np.isfinite since sequence item 2. The two methods
            # disagreed about whether NaN was acceptable input; they no longer
            # do.
            if not (np.isfinite(current_price) and np.isfinite(atr_val)):
                logger.error(f"Non-finite price inputs: price={current_price}, atr={atr_val}")
                raise ValueError(
                    f"Non-finite price or ATR (price={current_price}, "
                    f"atr={atr_val}) -- no stop or targets can be computed from "
                    f"a value that is not a number."
                )
            if current_price <= 0 or atr_val <= 0:
                logger.error(f"Invalid price inputs: price={current_price}, atr={atr_val}")
                raise ValueError("Invalid price or ATR values")

            effective_bias = detailed_bias
            if effective_bias not in ["LONG", "SHORT"]:
                effective_bias = "LONG" if bias_score >= 0 else "SHORT"

            # Volatility-adjusted modifier
            vol_multiplier = 1.0
            if volatility_state == "HIGH VOLATILITY":
                vol_multiplier = VOL_MULT_HIGH
            elif volatility_state == "LOW VOLATILITY":
                vol_multiplier = VOL_MULT_LOW
            elif volatility_state == "EXTREME VOLATILITY":
                vol_multiplier = VOL_MULT_EXTREME

            # Structural influence: strong trend pushes stop further
            trend_factor = 1.0 + (max(0.0, min(100.0, trend_health)) / TREND_FACTOR_DIVISOR)
            bias_factor = 1.0 - (abs(bias_score) / BIAS_FACTOR_DIVISOR)

            stop_mult = ATR_STOP_MULT * trend_factor * bias_factor * vol_multiplier

            # Ensure structural level is a valid finite float if provided
            valid_structural = structural_level is not None and np.isfinite(structural_level)

            # A12 FIX: targets are now computed as multiples of the ACTUAL stop
            # distance (i.e. real risk), not fixed ATR multiples independent of
            # it. Previously, since the stop can be pulled further out by
            # trend/volatility factors or a structural level (via the min/max
            # below), the realized stop distance could exceed 1x-2x raw ATR,
            # making "conservative" T1 mathematically the worst R:R target
            # (often below 1:1) by construction. Now T1/T2/T3 R:R come out at
            # exactly 1:1 / 2:1 / 3:1 relative to what's actually being risked.
            if effective_bias == "LONG":
                calculated_stop = current_price - (atr_val * stop_mult)
                atr_stop = (
                    min(structural_level, calculated_stop)
                    if valid_structural
                    else calculated_stop
                )

                stop_distance = current_price - atr_stop
                if not np.isfinite(stop_distance) or stop_distance <= 0:
                    # Degenerate case (e.g. structural level sits above price) —
                    # fall back to the raw ATR-based distance so targets never
                    # collapse to current_price.
                    stop_distance = atr_val * ATR_STOP_MULT

                target_t1 = current_price + (stop_distance * TARGET1_MULT)
                target_t2 = current_price + (stop_distance * TARGET2_MULT)
                target_t3 = current_price + (stop_distance * TARGET3_MULT)
            else:  # SHORT
                calculated_stop = current_price + (atr_val * stop_mult)
                atr_stop = (
                    max(structural_level, calculated_stop)
                    if valid_structural
                    else calculated_stop
                )

                stop_distance = atr_stop - current_price
                if not np.isfinite(stop_distance) or stop_distance <= 0:
                    stop_distance = atr_val * ATR_STOP_MULT

                target_t1 = current_price - (stop_distance * TARGET1_MULT)
                target_t2 = current_price - (stop_distance * TARGET2_MULT)
                target_t3 = current_price - (stop_distance * TARGET3_MULT)

            return float(atr_stop), float(target_t1), float(target_t2), float(target_t3)

        except Exception as e:
            # SEQUENCE ITEM 9b: this used to return "safe default fallback
            # bounds" — a stop at price × 0.99 and targets at 1.01, 1.02, 1.03.
            #
            # DIRECTION-BLIND. Those numbers put the stop 1% BELOW price and the
            # targets ABOVE it, whatever `detailed_bias` said. On a short they
            # are inverted: the stop sits where the trade would be winning and
            # every target sits where it would be losing. The panel printed
            # them as STOP LOSS and TARGET 1/2/3 with R:R ratios computed off
            # them, indistinguishable from a real plan.
            #
            # Nor were they "safe". A 1% stop on an instrument whose ATR is 4%
            # is not conservative, it is a stop inside the noise — and the
            # 1/2/3% targets encode a 1:1, 2:1, 3:1 reward that has nothing to
            # do with this market.
            #
            # It is the last of the fabrications item 9 set out to remove, and
            # the only one that produced a tradeable-looking artefact rather
            # than a wrong indicator reading.
            #
            # It raises now. This is the same line drawn at 9a for a missing
            # ATR: without a stop and targets there is no risk plan to degrade
            # to, so there is nothing to continue with. engine_core's existing
            # error path reports it, and the reason travels with it.
            logger.error(f"Stop targets calculation failed: {e}")
            raise ValueError(
                f"Stop and target calculation failed ({type(e).__name__}: {e}). "
                f"No risk plan can be produced, and substituting default levels "
                f"would put a stop and three targets on the panel that were "
                f"never computed from this market."
            ) from e

    # ============================================================
    # POSITION SIZING — REMOVED AT SEQUENCE ITEM 13
    # ============================================================
    #
    # calculate_position_size() lived here. It took an account balance and a
    # risk percentage from config, divided a risk budget by the stop distance,
    # capped the result at 10x notional and then applied 0.5x / 0.8x haircuts
    # in stressed volatility.
    #
    # Viktor ruled on 29 August 2026 that the engine must not compute monetary
    # position sizing at all: sizing belongs to the portfolio/execution layer,
    # which is the only place that knows the real balance, the open exposure,
    # the correlation across positions and the venue's constraints. This engine
    # knows none of those and is never permitted to place a trade.
    #
    # The removal is not a tidy-up. A number labelled POSITION SIZE, produced
    # from a fixed 10,000 placeholder balance, is a specific instruction to risk
    # a specific amount — and the 10x cap and the volatility haircuts are
    # portfolio policy, decided here by whoever wrote the constants, invisible
    # to whoever reads the output. The engine's job ends at the structural
    # verdict, the stop and the targets. Converting those into a quantity is a
    # decision made with information that only exists downstream.

    # ============================================================
    # RISK REGIME CLASSIFICATION & VALIDATION
    # ============================================================

    def classify_risk_regime(self, volatility_state: str, stop_distance_pct: float, trend_health: float) -> str:
        """
        Classifies current setup into a distinct risk regime profile.
        """
        if volatility_state == "EXTREME VOLATILITY" or stop_distance_pct > REGIME_EXTREME_STOP_PCT:
            return "EXTREME RISK"
        elif volatility_state == "HIGH VOLATILITY" or trend_health < REGIME_LOW_TREND_HEALTH:
            return "HIGH VOLATILITY RISK"
        elif volatility_state == "LOW VOLATILITY" and trend_health >= REGIME_HIGH_TREND_HEALTH:
            return "LOW RISK"
        else:
            return "NORMAL RISK"

    def validate_risk_parameters(
        self,
        current_price: float,
        atr_stop: float,
        volatility_state: str = "NORMAL",
        trend_health: float = 50.0,
        **kwargs
    ) -> Tuple[bool, str, str]:
        """
        Validates whether risk parameters are within safe operational thresholds.

        ITEM 14 RE-AUDIT (Finding 5): now returns the risk regime alongside
        the pass/fail, rather than computing it and discarding everything but
        one comparison against "EXTREME RISK". decision_model.py needs the
        regime itself: risk_valid already gates whether a trade is allowed at
        all, and Item 14 is a second, independent question -- given that a
        trade IS allowed, how much risk is actually being taken, which
        risk_valid alone cannot answer (HIGH VOLATILITY RISK and NORMAL RISK
        both return risk_valid=True, and previously looked identical to
        every caller past this function).

        "UNKNOWN" in the three early-return branches: classify_risk_regime()
        was never reached, so there is nothing to report — those branches
        already fail risk_valid, so decision_model.py never reaches the
        AGGRESSIVE-gating logic for them regardless of this string.
        """
        try:
            if not (np.isfinite(current_price) and np.isfinite(atr_stop)):
                return False, "Price or stop level is not a finite number.", "UNKNOWN"
            if current_price <= 0 or atr_stop <= 0:
                return False, "Invalid price or stop levels.", "UNKNOWN"

            stop_dist_pct = (abs(current_price - atr_stop) / current_price) * 100.0

            if stop_dist_pct > MAX_STOP_DISTANCE_PCT:
                return False, (
                    f"Stop distance exceeds maximum allowable threshold "
                    f"({MAX_STOP_DISTANCE_PCT:.0f}%)."
                ), "UNKNOWN"
            if stop_dist_pct < MIN_STOP_DISTANCE_PCT:
                return False, "Stop distance too tight (risk of market noise liquidation).", "UNKNOWN"

            risk_regime = self.classify_risk_regime(volatility_state, stop_dist_pct, trend_health)
            if risk_regime == "EXTREME RISK":
                return False, "Risk regime classified as EXTREME RISK.", risk_regime

            return True, "OK", risk_regime

        except Exception as e:
            # SEQUENCE ITEM 9b: examined and deliberately left alone.
            #
            # Step 5 listed "risk_model's direction-blind except-return" among
            # the fabrications. That is the one in calculate_stop_targets above.
            # This one is different in kind: it returns False — the trade is
            # NOT valid — and names the reason. It fails closed, and a caller
            # cannot mistake it for a passed check.
            #
            # Recorded rather than silently skipped so the re-audit at item 16
            # sees that both except-returns in this file were considered.
            logger.error(f"Risk validation failed: {e}")
            return False, f"Risk validation error: {str(e)}", "UNKNOWN"