"""
Audit findings 5 and 6, made checkable — 5 September 2026.

Two separate defects, one shared shape: a failure path that hands back a
number the engine then treats as a measurement.

FINDING 6 — two fabrication constants survived in engine_core.py after
sequence item 9a and Finding 3 removed their siblings from indicators.py and
entry_model.py:

    trend = {"trend_health": 50.0, ...}     the exact centre of the scale
    atr_val = ... else current_price * 0.02 a flat 2% of price

Both were unreachable, which is how they survived. Unreachable is not safe:
each was one edit to an invariant elsewhere away from being the live path, and
the trend one would not even have degraded the run — the dict it substituted
is missing "trend_direction_sign", which the next stage reads by subscript.

FINDING 5 — the RSI and ATR fallbacks smoothed with a simple moving average
where pandas_ta uses Wilder's RMA. tests/test_degraded_state.py asserts those
paths are NOT degradations, on the stated grounds that they recompute "the
same quantity by another route". That test was passing on a false premise.
These tests check the premise it rests on.

The source-text tests here are deliberate. Both constants were deleted before;
a behavioural test cannot see a fabrication on a path nothing can reach, so
the guard that keeps them deleted has to read the source.
"""

import io
import os
import re

import pytest

from conftest import REPO_ROOT

ENGINE_CORE = os.path.join(REPO_ROOT, "core", "engine_core.py")
INDICATORS = os.path.join(REPO_ROOT, "indicators", "indicators.py")
PINNED_DIR = os.path.join(REPO_ROOT, "tests", "fixtures", "pinned")
UNREACHABLE = "http://127.0.0.1:9"


def _code(path):
    """Source with comments and docstrings stripped, so the notes ABOUT a
    deleted fabrication do not read as the fabrication itself."""
    import ast

    with io.open(path, encoding="utf-8", newline="") as f:
        src = f.read()

    tree = ast.parse(src)
    drop = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                             ast.AsyncFunctionDef)):
            body = getattr(node, "body", None)
            if (body and isinstance(body[0], ast.Expr)
                    and isinstance(body[0].value, ast.Constant)
                    and isinstance(body[0].value.value, str)):
                drop.add(id(body[0].value))

    lines = src.splitlines()
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and id(node) in drop:
            for i in range(node.lineno - 1, node.end_lineno):
                lines[i] = ""

    return "\n".join(l.split("#", 1)[0] for l in lines)


def _engine_available():
    try:
        import pandas_ta  # noqa: F401
        return True
    except Exception:
        return False


def _pinned_frame():
    from data.data_fetcher import DataFetcher, data_fetcher
    original = data_fetcher.base_url
    try:
        data_fetcher.base_url = UNREACHABLE
        DataFetcher.set_pinned_source(PINNED_DIR)
        return data_fetcher.get_tf("AEROUSDT", "4h", limit=300)
    finally:
        DataFetcher.clear_pinned_source()
        data_fetcher.base_url = original


# ============================================================
# Finding 6 — the two constants are gone and stay gone
# ============================================================

def test_engine_core_does_not_substitute_a_midpoint_trend_health():
    code = _code(ENGINE_CORE)

    assert not re.search(r'"trend_health"\s*:\s*50(\.0+)?\b', code), (
        'engine_core.py assigns "trend_health": 50.0 again.\n\n'
        "50.0 is the exact centre of the scale — a reading a real market can "
        "produce, so nothing downstream can tell it from a measurement. "
        "trend_health.py's own failure path returns 0.0 and names the reason "
        "in degraded_inputs; a caller that overwrites that with a plausible "
        "number undoes it."
    )


def test_engine_core_does_not_substitute_a_flat_percentage_for_atr():
    code = _code(ENGINE_CORE)

    hits = re.findall(r"current_price\s*\*\s*0\.02|close.{0,20}\*\s*0\.02", code)
    assert not hits, (
        "engine_core.py derives an ATR from a flat percentage of price again: "
        + ", ".join(hits) + "\n\n"
        "On this repo's pinned fixture that constant overstates the real ATR "
        "by 52%, and ATR sets the stop distance and all three targets. "
        "Sequence item 9a removed it from indicators.py and Finding 3 removed "
        "it from entry_model.py; this is the third consumer."
    )


def test_compute_trend_health_is_total_which_is_why_the_handler_could_go():
    """
    The removed handler was justified by this property, so the property is
    now asserted rather than assumed.

    Every one of these inputs is malformed in a different way. None of them
    may raise, and every return must carry the keys engine_core reads by
    subscript — including trend_direction_sign, whose absence from the old
    substitute dict would have turned a degraded run into a KeyError one
    stage later.
    """
    import numpy as np
    import pandas as pd

    from indicators.trend_health import compute_trend_health

    cases = {
        "None": None,
        "not a frame": "not a frame",
        "empty frame": pd.DataFrame(),
        "too few rows": pd.DataFrame({"close": [1.0, 2.0, 3.0]}),
        "no columns at all": pd.DataFrame(index=range(60)),
        "all NaN close": pd.DataFrame({"close": [float("nan")] * 60}),
        "strings in close": pd.DataFrame({"close": ["a"] * 60}),
        "infinities": pd.DataFrame({"close": [np.inf] * 60}),
    }

    required = ("trend_health", "trend_direction_sign", "trend_exhaustion",
                "momentum_mode", "momentum_divergence", "continuation_strength",
                "degraded_inputs")

    for label, value in cases.items():
        try:
            out = compute_trend_health(value)
        except Exception as e:  # pragma: no cover - the failure is the message
            pytest.fail(
                f"compute_trend_health raised on {label}: {type(e).__name__}: {e}\n"
                "engine_core no longer wraps this call, because every path "
                "through it is supposed to return a dict. If that stops being "
                "true, restore a handler that REPORTS the failure — do not "
                "restore one that invents a score."
            )

        assert isinstance(out, dict), f"{label} returned {type(out).__name__}"
        missing = [k for k in required if k not in out]
        assert not missing, (
            f"{label} returned a dict missing {missing}. engine_core reads "
            f"these by subscript, so an absent key is a KeyError at the next "
            f"stage rather than a degraded run."
        )
        assert out["trend_direction_sign"] in (-1, 0, 1), (
            f"{label} returned trend_direction_sign="
            f"{out['trend_direction_sign']!r}; the bias engine validates it "
            f"to (-1, 0, 1) and raises otherwise."
        )


def test_a_broken_trend_contract_is_reported_not_papered_over(monkeypatch):
    """
    The one path that still reaches the check: a trend module that returns
    the wrong shape. It must end the run with a named error, not a score.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    import core.engine_core as ec
    from data.data_fetcher import DataFetcher, data_fetcher

    monkeypatch.setattr(ec, "compute_trend_health", lambda df: {"nonsense": 1})

    original_url = data_fetcher.base_url
    try:
        data_fetcher.base_url = UNREACHABLE
        DataFetcher.set_pinned_source(PINNED_DIR)
        decision = ec.Phase7Engine().run(symbol="AEROUSDT", timeframe="4h",
                                         save_chart=False)
    finally:
        DataFetcher.clear_pinned_source()
        data_fetcher.base_url = original_url

    assert "error" in decision, (
        "a trend module returning the wrong shape produced a decision object "
        f"with no error: {sorted(decision)[:12]}"
    )
    assert "trend health" in decision["error"].lower(), (
        f"the error does not name the stage that failed: {decision['error']!r}"
    )
    assert "trend_health" not in str(decision.get("trend", "")), (
        "a trend block survived a trend-engine contract violation"
    )


# ============================================================
# Finding 5 — the fallbacks compute the same quantity, checked
# ============================================================

def _fallback_frame(indicator):
    """The frame add_technical_indicators produces with one pandas_ta
    function raising, so the manual path is the one that ran."""
    import indicators.indicators as ind

    def explode(*a, **k):
        raise RuntimeError(f"simulated {indicator} failure")

    df = _pinned_frame()
    original = getattr(ind.ta, indicator)
    try:
        setattr(ind.ta, indicator, explode)
        frame, failures = ind.add_technical_indicators(df)
    finally:
        setattr(ind.ta, indicator, original)
    return frame, failures


@pytest.mark.parametrize("indicator,column,tolerance", [
    ("rsi", "RSI", 1e-6),
    ("atr", "ATR", 1e-9),
])
def test_the_fallback_computes_what_pandas_ta_computes(indicator, column, tolerance):
    """
    test_degraded_state asserts these paths are not degradations, because
    they "recompute the same quantity by another route". Until 5 September
    that was false: both smoothed with an SMA where pandas_ta uses Wilder's
    RMA. This is the check that premise never had.

    The decision reads .iloc[-1], so that is the bar the tolerance is on.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    import pandas_ta as ta

    from core import config

    df = _pinned_frame()
    if indicator == "rsi":
        reference = ta.rsi(df["close"], length=config.RSI_LENGTH)
    else:
        reference = ta.atr(df["high"], df["low"], df["close"],
                           length=config.ATR_LENGTH)

    frame, failures = _fallback_frame(indicator)

    assert column in frame.columns, (
        f"{column} is absent — the fallback did not run, so this test "
        f"measured nothing. Failures: {[f.indicator for f in failures]}"
    )

    got = float(frame[column].iloc[-1])
    want = float(reference.iloc[-1])
    delta = abs(got - want)
    scale = max(abs(want), 1e-12)

    assert delta / scale < tolerance, (
        f"the manual {column} fallback reads {got!r} where pandas_ta reads "
        f"{want!r} — a relative difference of {delta / scale:.3e}.\n\n"
        f"A fallback that returns a different number under the same column "
        f"name is a fabrication with extra steps, and test_degraded_state "
        f"asserts this path costs nothing. Match pandas_ta's smoothing "
        f"(Wilder's RMA: ewm(alpha=1/length, adjust=False)) or stop calling "
        f"it the same quantity."
    )


def test_the_fallbacks_do_not_use_a_simple_moving_average():
    """
    The defect in its own words, so a future edit back to `.rolling().mean()`
    fails here with the reason rather than only as a tolerance breach.
    """
    code = _code(INDICATORS)

    offenders = re.findall(
        r"rolling\(window=config\.(RSI_LENGTH|ATR_LENGTH)\)\.mean\(\)", code)
    assert not offenders, (
        "the RSI/ATR fallback smooths with a simple moving average again: "
        + ", ".join(sorted(set(offenders))) + "\n\n"
        "pandas_ta smooths both with Wilder's RMA. On this repo's pinned "
        "fixture the SMA version read RSI 84.45 against pandas_ta's 69.14, "
        "and an ATR 1.80% low — the number that sets the stop and all three "
        "targets."
    )
