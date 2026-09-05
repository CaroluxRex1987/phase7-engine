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


# AUDIT FINDING (a), 5 September 2026. NOT_MEASURED is what this module
# returns when it cannot compute a relationship, and it is NaN rather than 0.0
# for the reason recorded three times elsewhere in this engine: 0.0 is a
# reading a real market can produce. Two assets that genuinely move
# independently correlate at about zero, so a zero returned by a FAILURE is
# indistinguishable from a measurement -- the same defect as trend_health's
# old 50.0 and RSI's old 50.0.
#
# Callers gate on the third return value, `n`, which is 0 only when nothing
# was measured. engine_core converts the NaN to None at the boundary before it
# reaches the decision object, matching what it already does for hvn and atr.
NOT_MEASURED = float("nan")


def compute_correlation_beta(aero_closes: pd.Series, btc_closes: pd.Series, window: int = 30) -> Tuple[float, float, int]:
    """
    Correlation + beta between AERO and BTC returns over the most recent
    `window` candles that BOTH series actually have.

    AUDIT FINDING (a): this used to do

        aero_series = pd.Series(aero_closes).reset_index(drop=True)
        btc_series = pd.Series(btc_closes).reset_index(drop=True)

    and then pair the two tails by POSITION. Both series arrive indexed by
    timestamp -- data_fetcher sets that index -- and both lines threw it away.
    Bar i of AERO was correlated against bar i of BTC whatever times those
    two bars belonged to.

    In the ordinary case the two fetches return the same 450 candles and the
    positional pairing happens to be the timestamp pairing, which is why this
    survived: on this repo's pinned fixtures the two indexes share all 450
    timestamps and the old code and the new code agree exactly.

    It stops being harmless the moment the two series differ by one bar --
    a new candle closing between the two API calls, an exchange gap in one
    symbol, a stale feed. Then every AERO return is paired with a BTC return
    from a different four hours. Measured on the pinned fixtures, dropping a
    single BTC bar from inside the 30-candle window: the printed correlation
    moved by a median of 0.105 (max 0.165), beta by a median of 0.135, and
    the printed LABEL changed in 4 of the 31 positions tested. n_observations
    read 30 either way, so the panel gave the reader no hint.

    Both series are now joined on their shared timestamps and the window is
    taken from the joined result.

    KNOWN LIMITATION, stated rather than fixed: after an inner join across a
    gap, one return spans two candle intervals instead of one. Both sides span
    the SAME two, so the pair is still contemporaneous -- which is what
    correlation needs -- but the observation is not the same length as its
    neighbours. Dropping gap-spanning pairs would need this function to know
    the timeframe, which it is not told. Recorded as open.

    Returns:
        correlation (float, -1..1; NaN if it could not be computed)
        beta (float; AERO's sensitivity to BTC moves -- 1.0 means AERO
              tends to move 1:1 with BTC; NaN if it could not be computed)
        n (int; how many paired return observations were actually used.
           0 means nothing was measured, and is the flag callers gate on)
    """
    try:
        if aero_closes is None or btc_closes is None:
            return NOT_MEASURED, NOT_MEASURED, 0

        aero_series = pd.Series(aero_closes)
        btc_series = pd.Series(btc_closes)

        if len(aero_series) < 3 or len(btc_series) < 3:
            return NOT_MEASURED, NOT_MEASURED, 0

        # AUDIT FINDING (a). Without a shared time index there is no fact
        # about which bar of one series belongs beside which bar of the
        # other, and a correlation computed without that fact is not a
        # measurement of anything. Refused rather than approximated.
        if not (isinstance(aero_series.index, pd.DatetimeIndex)
                and isinstance(btc_series.index, pd.DatetimeIndex)):
            return NOT_MEASURED, NOT_MEASURED, 0

        paired = pd.concat(
            {"aero": aero_series, "btc": btc_series}, axis=1, join="inner"
        ).dropna()

        if len(paired) < 3:
            return NOT_MEASURED, NOT_MEASURED, 0

        paired = paired.sort_index().tail(window + 1)

        aero_returns = paired["aero"].pct_change().replace([np.inf, -np.inf], np.nan)
        btc_returns = paired["btc"].pct_change().replace([np.inf, -np.inf], np.nan)

        valid = aero_returns.notna() & btc_returns.notna()
        aero_returns = aero_returns[valid].reset_index(drop=True)
        btc_returns = btc_returns[valid].reset_index(drop=True)

        if len(aero_returns) < 3:
            return NOT_MEASURED, NOT_MEASURED, 0

        btc_var = btc_returns.var()
        if not np.isfinite(btc_var) or btc_var == 0:
            # BTC did not move across the window, so its sensitivity is
            # undefined rather than zero -- dividing by that variance is the
            # thing being refused. n is still reported, because the pairing
            # itself succeeded and the reader should see how much data this
            # verdict was reached on.
            return NOT_MEASURED, NOT_MEASURED, int(len(aero_returns))

        covariance = float(np.cov(aero_returns, btc_returns)[0, 1])
        beta = covariance / float(btc_var)

        correlation = float(aero_returns.corr(btc_returns))
        if not np.isfinite(correlation) or not np.isfinite(beta):
            # 5 September 2026: these were two separate `= 0.0` assignments.
            # A non-finite correlation became "the two are unrelated" and a
            # non-finite beta became "AERO does not respond to BTC", both of
            # which are claims. Neither was measured.
            return NOT_MEASURED, NOT_MEASURED, int(len(aero_returns))

        correlation = max(-1.0, min(1.0, correlation))

        return correlation, beta, int(len(aero_returns))

    except Exception:
        return NOT_MEASURED, NOT_MEASURED, 0


NOT_MEASURED_LABEL = "NOT MEASURED"


def classify_correlation(r: float) -> str:
    """
    Plain-language label for a -1..1 correlation coefficient.

    AUDIT FINDING (a): an unusable input used to become r = 0.0 here, which
    then printed "WEAK / NO CLEAR RELATIONSHIP" -- a finding, from no data.
    None, NaN and anything unparseable now say so instead.
    """
    if r is None:
        return NOT_MEASURED_LABEL
    try:
        r = float(r)
    except (TypeError, ValueError):
        return NOT_MEASURED_LABEL
    if not np.isfinite(r):
        return NOT_MEASURED_LABEL

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