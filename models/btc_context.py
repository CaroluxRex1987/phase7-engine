import numpy as np
import pandas as pd
from typing import Tuple

# ============================================================
# BTC/AERO RELATIONSHIP ENGINE (new feature, V1)
# ============================================================
#
# Supports the "BTC-Adjusted AERO Prediction" feature: a SEPARATE, additive
# reading that sits alongside the original AERO-only analysis and never
# replaces or distorts it. This module only computes the relationship
# metrics (correlation, beta, and a volatility-based stress classifier);
# BTC's own bias/trend/regime reuses the exact same, already-tested
# bias_engine.py / trend_health.py / structure.py functions engine_core.py
# already runs for AERO -- just called a second time on BTC's own data.


def compute_correlation_beta(aero_closes: pd.Series, btc_closes: pd.Series, window: int = 30) -> Tuple[float, float, int]:
    """
    Rolling correlation + beta between AERO and BTC returns over the most
    recent `window` candles (or however much history is actually available,
    whichever is smaller).

    Returns:
        correlation (float, -1..1; 0.0 if it can't be computed)
        beta (float; AERO's sensitivity to BTC moves -- 1.0 means AERO
              tends to move 1:1 with BTC; 0.0 if it can't be computed)
        n (int; how many paired return observations were actually used)
    """
    try:
        if aero_closes is None or btc_closes is None:
            return 0.0, 0.0, 0

        aero_series = pd.Series(aero_closes).reset_index(drop=True)
        btc_series = pd.Series(btc_closes).reset_index(drop=True)

        if len(aero_series) < 3 or len(btc_series) < 3:
            return 0.0, 0.0, 0

        n = min(len(aero_series), len(btc_series), window + 1)
        aero_tail = aero_series.tail(n).reset_index(drop=True)
        btc_tail = btc_series.tail(n).reset_index(drop=True)

        aero_returns = aero_tail.pct_change().replace([np.inf, -np.inf], np.nan)
        btc_returns = btc_tail.pct_change().replace([np.inf, -np.inf], np.nan)

        valid = aero_returns.notna() & btc_returns.notna()
        aero_returns = aero_returns[valid].reset_index(drop=True)
        btc_returns = btc_returns[valid].reset_index(drop=True)

        if len(aero_returns) < 3:
            return 0.0, 0.0, 0

        btc_var = btc_returns.var()
        if not np.isfinite(btc_var) or btc_var == 0:
            return 0.0, 0.0, int(len(aero_returns))

        covariance = float(np.cov(aero_returns, btc_returns)[0, 1])
        beta = covariance / float(btc_var)

        correlation = float(aero_returns.corr(btc_returns))
        if not np.isfinite(correlation):
            correlation = 0.0
        if not np.isfinite(beta):
            beta = 0.0

        correlation = max(-1.0, min(1.0, correlation))

        return correlation, beta, int(len(aero_returns))

    except Exception:
        return 0.0, 0.0, 0


def classify_correlation(r: float) -> str:
    """Plain-language label for a -1..1 correlation coefficient."""
    try:
        r = float(r)
    except (TypeError, ValueError):
        r = 0.0

    r_abs = abs(r)
    if r_abs >= 0.7:
        strength = "STRONG"
    elif r_abs >= 0.3:
        strength = "MODERATE"
    else:
        return "WEAK / NO CLEAR RELATIONSHIP"

    direction = "POSITIVE" if r >= 0 else "NEGATIVE"
    return f"{strength} {direction}"


def classify_stress(btc_volatility_mode: str) -> bool:
    """
    V1 broad-market-stress proxy: BTC itself sitting in an elevated
    volatility regime. Simple and reuses an already-tested classifier
    (calculate_dynamic_regime in bias_engine.py) rather than inventing a
    new stress metric for this first version.
    """
    return str(btc_volatility_mode).upper() in ("EXTREME VOLATILITY", "HIGH VOLATILITY")