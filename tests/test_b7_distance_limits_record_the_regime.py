"""
B7 -- the two stop-distance limits record the regime.

Round 8's triage, ruled on the night of 4 to 5 October 2026
(docs/PHASE7_DECISIONS.md, "Ruling, 5 October 2026 -- round 8 triaged ...",
point 8: the label and record batch; the review's B7). Its shape was ruled on
15 October 2026, by Viktor agreeing to Claude's suggestion (DECISIONS,
"Ruling, 15 October 2026 -- B7: the distance limits record the regime").

WHAT WAS WRONG

validate_risk_parameters tested the 15% distance limit and the 0.2% floor
before it classified the regime, and both returned "UNKNOWN" as the regime.
The regime was computable on both: the stop distance was known and the
volatility state is a parameter. And the 15% limit refused nothing on its
own -- any stop over 15% is over REGIME_EXTREME_STOP_PCT (8%), so EXTREME
RISK refuses it anyway. It chose only the message, and made the record say
UNKNOWN for a regime that was EXTREME RISK.

THE FIX

The regime is classified first; both limits then return it. Their messages
are unchanged and keep their precedence. The 15% limit stays, as the ruling
of 27 September kept it, as a backstop should the 8% ever be raised past it.

WHAT THESE TESTS HOLD

1. A stop over 15% is refused with the 15% message and records EXTREME RISK,
   in every volatility state.
2. A stop under 0.2% is refused with the too-tight message and records the
   regime of its volatility state.
3. On every input the verdict and the reason are what they were before B7 --
   checked against an inline copy of the pre-B7 order.
4. "UNKNOWN" is returned only where no regime can be computed.
5. The 15% limit still refuses, with its own message and the regime computed,
   once the 8% is raised past it -- the backstop the ruling keeps it for.

All fixture-free, so run_tests.py runs them too.
"""

import math

from models import risk_model as rm
from models.risk_model import RiskModel


FIFTEEN = "Stop distance exceeds maximum allowable threshold (15%)."
TIGHT = "Stop distance too tight (risk of market noise liquidation)."

REGIME_OF = {
    "LOW VOLATILITY": "LOW RISK",
    "MEDIUM VOLATILITY": "NORMAL RISK",
    "HIGH VOLATILITY": "HIGH VOLATILITY RISK",
    "EXTREME VOLATILITY": "EXTREME RISK",
}
STATES = list(REGIME_OF) + ["UNKNOWN", "NORMAL", None]


def _expected_regime(state, stop_pct):
    if state == "EXTREME VOLATILITY" or stop_pct > rm.REGIME_EXTREME_STOP_PCT:
        return "EXTREME RISK"
    return REGIME_OF.get(state, "UNKNOWN RISK")


def _pre_b7_verdict_and_reason(price, stop, state):
    """The order validate_risk_parameters had until B7, verdict and reason
    only. The regime is left out: that is the one thing B7 changes."""
    if not (math.isfinite(price) and math.isfinite(stop)):
        return False, "Price or stop level is not a finite number."
    if price <= 0 or stop <= 0:
        return False, "Invalid price or stop levels."
    pct = abs(price - stop) / price * 100.0
    if pct > rm.MAX_STOP_DISTANCE_PCT:
        return False, FIFTEEN
    if pct < rm.MIN_STOP_DISTANCE_PCT:
        return False, TIGHT
    if _expected_regime(state, pct) == "EXTREME RISK":
        return False, "Risk regime classified as EXTREME RISK."
    return True, "OK"


def test_a_stop_over_fifteen_percent_records_extreme_risk():
    model = RiskModel()
    for state in STATES:
        for stop in (84.0, 70.0, 1.0):
            got = model.validate_risk_parameters(
                current_price=100.0, atr_stop=stop, volatility_state=state)
            assert got == (False, FIFTEEN, "EXTREME RISK"), (state, stop, got)


def test_a_stop_under_the_floor_records_its_regime():
    model = RiskModel()
    for state in STATES:
        got = model.validate_risk_parameters(
            current_price=100.0, atr_stop=99.9, volatility_state=state)
        assert got == (False, TIGHT, REGIME_OF.get(state, "UNKNOWN RISK")), (state, got)
        assert got[2] != "UNKNOWN", (state, got)


def test_the_verdict_and_reason_are_unchanged_on_every_input():
    model = RiskModel()
    stops = [100.0 - d for d in (0.0, 0.05, 0.1999, 0.2, 0.2001, 1.0, 5.0,
                                 7.9999, 8.0, 8.0001, 12.0, 14.9999, 15.0,
                                 15.0001, 20.0, 99.0)]
    stops += [100.0 + d for d in (0.1, 3.0, 9.0, 16.0)]
    stops += [0.0, -1.0, float("nan"), float("inf")]
    seen = set()
    for state in STATES:
        for stop in stops:
            ok, reason, regime = model.validate_risk_parameters(
                current_price=100.0, atr_stop=stop, volatility_state=state)
            assert (ok, reason) == _pre_b7_verdict_and_reason(100.0, stop, state), (
                state, stop, ok, reason)
            seen.add(reason)
    # Every branch was reached, so the comparison above covered each one.
    assert seen == {
        "OK", FIFTEEN, TIGHT, "Risk regime classified as EXTREME RISK.",
        "Price or stop level is not a finite number.",
        "Invalid price or stop levels.",
    }, seen


def test_unknown_only_where_no_regime_can_be_computed():
    model = RiskModel()
    for price, stop in ((float("nan"), 90.0), (100.0, float("inf")),
                        (0.0, 90.0), (100.0, 0.0), (-5.0, 90.0)):
        ok, _, regime = model.validate_risk_parameters(
            current_price=price, atr_stop=stop, volatility_state="MEDIUM VOLATILITY")
        assert (ok, regime) == (False, "UNKNOWN"), (price, stop, ok, regime)

    for state in STATES:
        for stop in (99.9, 97.0, 91.0, 84.0):
            _, _, regime = model.validate_risk_parameters(
                current_price=100.0, atr_stop=stop, volatility_state=state)
            assert regime != "UNKNOWN", (state, stop, regime)


def test_the_fifteen_percent_backstop_still_refuses_with_the_eight_raised():
    model = RiskModel()
    saved = rm.REGIME_EXTREME_STOP_PCT
    rm.REGIME_EXTREME_STOP_PCT = 20.0
    try:
        got = model.validate_risk_parameters(
            current_price=100.0, atr_stop=83.0, volatility_state="MEDIUM VOLATILITY")
        assert got == (False, FIFTEEN, "NORMAL RISK"), got
        got = model.validate_risk_parameters(
            current_price=100.0, atr_stop=86.0, volatility_state="MEDIUM VOLATILITY")
        assert got == (True, "OK", "NORMAL RISK"), got
    finally:
        rm.REGIME_EXTREME_STOP_PCT = saved
    assert rm.REGIME_EXTREME_STOP_PCT == 8.0
