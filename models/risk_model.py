from typing import Tuple, Union, Optional
import logging
import numpy as np

logger = logging.getLogger(__name__)

class RiskModel:
    """
    Core institutional risk engine for Phase-7.
    Provides:
        - Volatility-adjusted ATR stop calculation
        - Tiered target generation
        - Position sizing & leverage adjustment
        - Risk regime classification & advanced validation
    """

    def __init__(self) -> None:
        # Tunable multipliers
        self.atr_stop_mult: float = 1.2        # Base ATR multiplier for stop
        self.target1_mult: float = 1.0         # Conservative target (x stop distance)
        self.target2_mult: float = 2.0         # Normal target (x stop distance)
        self.target3_mult: float = 3.0         # Aggressive target (x stop distance)

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
            if current_price <= 0 or atr_val <= 0:
                logger.error(f"Invalid price inputs: price={current_price}, atr={atr_val}")
                raise ValueError("Invalid price or ATR values")

            effective_bias = detailed_bias
            if effective_bias not in ["LONG", "SHORT"]:
                effective_bias = "LONG" if bias_score >= 0 else "SHORT"

            # Volatility-adjusted modifier
            vol_multiplier = 1.0
            if volatility_state == "HIGH VOLATILITY":
                vol_multiplier = 1.35  # Widen stops in high vol to avoid whipsaws
            elif volatility_state == "LOW VOLATILITY":
                vol_multiplier = 0.85  # Tighter stops in calm markets
            elif volatility_state == "EXTREME VOLATILITY":
                vol_multiplier = 1.60

            # Structural influence: strong trend pushes stop further
            trend_factor = 1.0 + (max(0.0, min(100.0, trend_health)) / 200.0)
            bias_factor = 1.0 - (abs(bias_score) / 300.0)

            stop_mult = self.atr_stop_mult * trend_factor * bias_factor * vol_multiplier

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
                    stop_distance = atr_val * self.atr_stop_mult

                target_t1 = current_price + (stop_distance * self.target1_mult)
                target_t2 = current_price + (stop_distance * self.target2_mult)
                target_t3 = current_price + (stop_distance * self.target3_mult)
            else:  # SHORT
                calculated_stop = current_price + (atr_val * stop_mult)
                atr_stop = (
                    max(structural_level, calculated_stop)
                    if valid_structural
                    else calculated_stop
                )

                stop_distance = atr_stop - current_price
                if not np.isfinite(stop_distance) or stop_distance <= 0:
                    stop_distance = atr_val * self.atr_stop_mult

                target_t1 = current_price - (stop_distance * self.target1_mult)
                target_t2 = current_price - (stop_distance * self.target2_mult)
                target_t3 = current_price - (stop_distance * self.target3_mult)

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
    # POSITION SIZING & LEVERAGE ADJUSTMENT
    # ============================================================

    def calculate_position_size(
        self,
        account_balance: float,
        risk_percent: float,
        current_price: float,
        atr_stop: float,
        volatility_state: str = "NORMAL"
    ) -> float:
        """
        Calculates exact position size based on account risk percentage, stop distance,
        and volatility-adjusted leverage constraints.
        """
        if account_balance <= 0 or risk_percent <= 0 or current_price <= 0:
            return 0.0

        risk_amount = account_balance * (risk_percent / 100.0)
        stop_distance = abs(current_price - atr_stop)

        # Critical protection: Prevent division by zero and micro stops
        min_stop_distance = current_price * 0.001  # 0.1% minimum stop distance
        if stop_distance < min_stop_distance:
            return 0.0

        position_size = risk_amount / stop_distance

        # Cap maximum position size to prevent extreme leverage overexposure
        max_position_value = account_balance * 10.0  # 10x max structural leverage limit
        max_position_size = max_position_value / current_price
        position_size = min(position_size, max_position_size)

        # Apply volatility scaling haircuts
        if volatility_state == "EXTREME VOLATILITY":
            position_size *= 0.5  # Cut position sizing in half during market stress
        elif volatility_state == "HIGH VOLATILITY":
            position_size *= 0.8

        return float(position_size)

    # ============================================================
    # RISK REGIME CLASSIFICATION & VALIDATION
    # ============================================================

    def classify_risk_regime(self, volatility_state: str, stop_distance_pct: float, trend_health: float) -> str:
        """
        Classifies current setup into a distinct risk regime profile.
        """
        if volatility_state == "EXTREME VOLATILITY" or stop_distance_pct > 8.0:
            return "EXTREME RISK"
        elif volatility_state == "HIGH VOLATILITY" or trend_health < 40.0:
            return "HIGH VOLATILITY RISK"
        elif volatility_state == "LOW VOLATILITY" and trend_health >= 70.0:
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
    ) -> Tuple[bool, str]:
        """
        Validates whether risk parameters are within safe operational thresholds.
        """
        try:
            if current_price <= 0 or atr_stop <= 0:
                return False, "Invalid price or stop levels."

            stop_dist_pct = (abs(current_price - atr_stop) / current_price) * 100.0

            if stop_dist_pct > 15.0:
                return False, "Stop distance exceeds maximum allowable threshold (15%)."
            if stop_dist_pct < 0.2:
                return False, "Stop distance too tight (risk of market noise liquidation)."

            risk_regime = self.classify_risk_regime(volatility_state, stop_dist_pct, trend_health)
            if risk_regime == "EXTREME RISK":
                return False, "Risk regime classified as EXTREME RISK."

            return True, "OK"

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
            return False, f"Risk validation error: {str(e)}"