from typing import Tuple, Union
import logging

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
        self.atr_stop_mult = 1.2        # Base ATR multiplier for stop
        self.target1_mult = 1.0         # Conservative target
        self.target2_mult = 2.0         # Normal target
        self.target3_mult = 3.0         # Aggressive target

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

        # Structural influence: strong trend pushes stop further
        trend_factor = 1.0 + (trend_health / 200.0)
        bias_factor = 1.0 - (abs(bias_score) / 300.0)

        stop_mult = self.atr_stop_mult * trend_factor * bias_factor * vol_multiplier

        if effective_bias == "LONG":
            atr_stop = (
                min(structural_level, current_price - (atr_val * stop_mult))
                if structural_level
                else current_price - (atr_val * stop_mult)
            )
            target_t1 = current_price + (atr_val * self.target1_mult)
            target_t2 = current_price + (atr_val * self.target2_mult)
            target_t3 = current_price + (atr_val * self.target3_mult)
        else:  # SHORT
            atr_stop = (
                max(structural_level, current_price + (atr_val * stop_mult))
                if structural_level
                else current_price + (atr_val * stop_mult)
            )
            target_t1 = current_price - (atr_val * self.target1_mult)
            target_t2 = current_price - (atr_val * self.target2_mult)
            target_t3 = current_price - (atr_val * self.target3_mult)

        return atr_stop, target_t1, target_t2, target_t3

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
    ):
        """
        Calculates exact position size based on account risk percentage, stop distance,
        and volatility-adjusted leverage constraints.
        """
        if account_balance <= 0 or risk_percent <= 0:
            return 0.0

        risk_amount = account_balance * (risk_percent / 100.0)
        stop_distance = abs(current_price - atr_stop)

        # Critical fix: Prevent division by zero and extremely small stops
        min_stop_distance = current_price * 0.001  # 0.1% minimum stop distance
        if stop_distance < min_stop_distance:
            return 0.0

        position_size = risk_amount / stop_distance
        
        # Critical fix: Cap maximum position size to prevent excessive leverage
        max_position_value = account_balance * 10.0  # 10x max leverage
        max_position_size = max_position_value / current_price
        position_size = min(position_size, max_position_size)
        
        # Apply volatility adjustment scale to size if necessary
        if volatility_state == "EXTREME VOLATILITY":
            position_size *= 0.5  # Cut size in half during extreme risk events

        return float(position_size)

    # ============================================================
    # RISK REGIME CLASSIFICATION & VALIDATION
    # ============================================================

    def classify_risk_regime(self, volatility_state, stop_distance_pct, trend_health):
        """
        Classifies current setup into a distinct risk regime.
        """
        if volatility_state == "EXTREME VOLATILITY" or stop_distance_pct > 8.0:
            return "EXTREME RISK"
        elif volatility_state == "HIGH VOLATILITY" or trend_health < 40:
            return "HIGH VOLATILITY RISK"
        elif volatility_state == "LOW VOLATILITY" and trend_health >= 70:
            return "LOW RISK"
        else:
            return "NORMAL RISK"

    def validate_risk_parameters(
        self, 
        current_price: float, 
        atr_stop: float, 
        volatility_state: str = "NORMAL", 
        **kwargs
    ) -> Tuple[bool, str]:
        """
        Validates whether risk parameters are within safe trading thresholds,
        accepting any extra keyword arguments (like reference_price) from engine_core.
        
        Args:
            current_price: Current market price
            atr_stop: Calculated ATR stop level
            volatility_state: Current volatility regime
            **kwargs: Additional parameters (for compatibility)
            
        Returns:
            Tuple of (is_valid, reason_message)
        """
        try:
            if current_price <= 0 or atr_stop <= 0:
                return False, "Invalid price or stop levels."

            stop_dist_pct = (abs(current_price - atr_stop) / current_price) * 100.0

            if stop_dist_pct > 15.0:
                return False, "Stop distance exceeds maximum allowable threshold (15%)."
            if stop_dist_pct < 0.2:
                return False, "Stop distance too tight (risk of noise execution)."

            risk_regime = self.classify_risk_regime(volatility_state, stop_dist_pct, trend_health=50.0)
            if risk_regime == "EXTREME RISK":
                return False, "Risk regime classified as EXTREME RISK."

            return True, "OK"
            
        except Exception as e:
            logger.error(f"Risk validation failed: {e}")
            return False, f"Risk validation error: {str(e)}"
