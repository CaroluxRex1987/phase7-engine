"""
The trend health score on the panel says what it is out of.

FOUND 20 SEPTEMBER 2026, in Viktor's own live run, about two hours after
a9d4b1f landed the identical fix one line below. The panel printed

    TREND      : BULLISH / HEALTHY (Score: 100.00)
    VALIDATION : WEAK (Score: 35.00/100)

-- one line with its denominator and the line above it without. a9d4b1f's
commit message had recorded the VALIDATION line as the instance found; rule 22
in PHASE7_DECISIONS.md says fixing the instance you found does not close the
item, and this is what that rule is about.

WHY 100 IS THE RIGHT DENOMINATOR, AND NOT A GUESS

indicators/trend_health.py's compute_trend_health() builds the score from three
terms with fixed ceilings -- a slope term capped at 45, an ADX term capped at
40, and an RSI band term worth at most 15 -- and then clamps the sum to
0.0 .. 100.0. The section is headed "TREND HEALTH SCORE (0-100)". A 100.00 is
the top of the scale, not an unbounded total that happened to reach three
figures.

test_the_scale_the_panel_claims_is_the_one_the_indicator_produces holds both
halves of that: the clamp bounds are read out of the module's parse tree, so a
rescale to 0..10 fails here instead of quietly making the panel lie, and the
function is also run on real frames to confirm it stays inside them.

THE REST OF THE PANEL WAS SWEPT, NOT SAMPLED

Every other number the panel prints already carries its scale -- /100, /<max>,
a percentage or an x multiplier. This was the last bare one. Recorded here so
the sweep does not have to be repeated from scratch next time.

Fixture-free, per run_tests.py.
"""

import ast
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _panel(trend_health, trend_direction="BULLISH", momentum_mode="HEALTHY"):
    from core.panel_render import render_panel

    return render_panel({
        "symbol": "TESTUSDT",
        "timeframe": "4h",
        "trend": {
            "trend_health": trend_health,
            "trend_direction": trend_direction,
            "momentum_mode": momentum_mode,
        },
    })


def test_the_trend_score_carries_its_denominator():
    panel = _panel(100.0)

    assert "100.00/100" in panel, (
        "the TREND line prints a bare number again; a reader cannot tell "
        "100.00/100 from an unbounded running total"
    )


def test_the_floor_and_the_ceiling_both_print_it():
    assert "0.00/100" in _panel(0.0)
    assert "100.00/100" in _panel(100.0)


def test_the_labels_are_still_printed_beside_the_score():
    """
    Negative control: the denominator must not have replaced or displaced the
    two labels the line exists to carry.
    """
    panel = _panel(62.5, trend_direction="BEARISH", momentum_mode="EXTENDED")
    assert "BEARISH" in panel and "EXTENDED" in panel and "62.50/100" in panel, panel


def test_the_scale_the_panel_claims_is_the_one_the_indicator_produces():
    """
    Two independent halves, because either alone can pass vacuously.

    The parse-tree half reads the clamp bounds out of compute_trend_health
    rather than matching source text, the technique rule 16 requires: a
    rescaled indicator fails here even though the panel would still render.
    The behavioural half runs the function, so a clamp that is present in the
    source and unreachable in practice does not satisfy the test either.
    """
    import numpy as np
    import pandas as pd

    from indicators import trend_health as th

    # --- the bounds the module actually applies -------------------------
    source = open(th.__file__, "rb").read().decode("utf-8")
    tree = ast.parse(source)

    clamp_bounds = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Assign) and len(node.targets) == 1):
            continue
        target = node.targets[0]
        if not (isinstance(target, ast.Name) and target.id == "trend_health"):
            continue
        # max(LOW, min(HIGH, value))
        call = node.value
        if not (isinstance(call, ast.Call) and getattr(call.func, "id", None) == "max"):
            continue
        low = call.args[0]
        inner = call.args[1]
        if not (isinstance(inner, ast.Call) and getattr(inner.func, "id", None) == "min"):
            continue
        high = inner.args[0]
        if isinstance(low, ast.Constant) and isinstance(high, ast.Constant):
            clamp_bounds.append((low.value, high.value))

    assert clamp_bounds == [(0.0, 100.0)], (
        "compute_trend_health no longer clamps trend_health to 0..100, so the "
        "/100 the panel prints is no longer true: found %r" % (clamp_bounds,)
    )

    # --- and what the function returns when it is run -------------------
    def frame(closes):
        df = pd.DataFrame({
            "open": closes,
            "high": [c * 1.01 for c in closes],
            "low": [c * 0.99 for c in closes],
            "close": closes,
            "volume": [1000.0] * len(closes),
        })
        df["EMA20"] = df["close"].ewm(span=20, adjust=False).mean()
        df["EMA50"] = df["close"].ewm(span=50, adjust=False).mean()
        df["EMA20_Slope"] = df["EMA20"].pct_change()
        df["EMA50_Slope"] = df["EMA50"].pct_change()
        df["ADX"] = 55.0
        df["RSI"] = 55.0
        return df

    n = 120
    cases = {
        "steep uptrend": [100.0 * (1.05 ** i) for i in range(n)],
        "steep downtrend": [100.0 * (0.95 ** i) for i in range(n)],
        "flat": [100.0] * n,
        "noisy": list(100.0 + np.sin(np.arange(n)) * 5.0),
    }

    for name, closes in cases.items():
        result = th.compute_trend_health(frame(closes))
        score = result["trend_health"]
        assert 0.0 <= score <= 100.0, (
            "%s produced trend_health %r, outside the 0..100 the panel "
            "prints as the denominator" % (name, score)
        )

    # The degraded path returns the floor of the scale, not its middle -- the
    # SEQUENCE ITEM 9a decision, held here because the panel now prints that
    # value with "/100" beside it.
    assert th.compute_trend_health(None)["trend_health"] == 0.0
