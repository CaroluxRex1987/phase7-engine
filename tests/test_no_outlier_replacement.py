"""
Finding 7 -- indicator values beyond 5 sigma were silently replaced.

Ruled by Viktor on 27 September 2026 (docs/PHASE7_DECISIONS.md, "Ruling,
27 September 2026 -- indicator values are no longer replaced beyond 5 sigma
(finding 7)"): the replacement is removed from clean_series; the inf-to-NaN
step stays.

WHAT THE RULE DID

clean_series set every value more than five standard deviations from the
series' mean to NaN, once the series had more than 10 values. The forward fill
then replaced an interior NaN with the previous bar's value, and the
trailing-edge rule left a NaN at the decision bar, which unusable_reason()
reports as an indicator FAILURE. EMA_20, EMA_50, RSI, ADX, the SuperTrend
level and direction and ATR all passed through it, on their primary paths and
on the EMA, RSI and ATR fallbacks.

WHY NOTHING CAUGHT IT

The rule needed more than 10 values. The longest series any test passed to
clean_series directly had 10, and on the fixture frames the engine tests use
the rule fired on no value at all (measured 27 September by instrumenting
it). So every test that exists passed with the rule and passes without it.

WHAT THESE TESTS PIN

1. A value beyond 5 sigma survives, at the decision bar and inside the frame
   (pure clean_series; runs without pandas_ta).
2. Early values do not depend on later bars: cleaning a series and then
   slicing it gives what cleaning the slice gives (pure; Item 2).
3. The inf-to-NaN step the ruling keeps.
4. On the engine path, with synthetic or modified frames: a fresh SuperTrend
   flip survives; an ATR spike of about 2.2x survives on the primary and the
   backup path; a 10% decision-bar move in a flat market survives in every
   indicator in scope, primary and fallback; and a value planted beyond
   5 sigma in each pandas_ta output is written unchanged.

Every test here is fixture-free, so run_tests.py runs it. Each was run
against a broken version and failed -- the eight finding-7 tests with the rule
restored, the inf test with the inf step removed (negative controls, recorded
in the commit that added this file).
"""

import os

import numpy as np
import pandas as pd
import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PINNED_4H = os.path.join(REPO_ROOT, "tests", "fixtures", "pinned",
                         "AEROUSDT_4h.csv")


def _clean_series():
    """
    clean_series, imported without dragging pandas_ta in -- the same approach
    as tests/test_no_lookahead.py, so the pure tests run on a machine without
    it.
    """
    src = open(os.path.join(REPO_ROOT, "indicators", "indicators.py"),
               encoding="utf-8").read()
    start = src.index("def clean_series")
    end = src.index("def unusable_reason")
    ns = {"pd": pd, "np": np}
    exec(src[start:end], ns)
    return ns["clean_series"]


def _engine_available():
    try:
        import pandas_ta  # noqa: F401
        return True
    except Exception:
        return False


def _quiet_series(n=450, seed=11):
    """Values near 1.0 with small noise: anything a few units away is >5 sigma."""
    rng = np.random.default_rng(seed)
    return pd.Series(1.0 + rng.normal(0.0, 0.01, n))


def _five_sigma_outliers(series):
    """Which entries the removed rule would have erased. Used to prove each
    test's input really does carry a value the rule would have touched."""
    mean, std = series.mean(), series.std()
    return (series - mean).abs() > 5 * std


# ============================================================
# 1-3. clean_series itself -- no pandas_ta needed
# ============================================================

def test_a_value_beyond_five_sigma_at_the_decision_bar_is_kept():
    clean_series = _clean_series()
    s = _quiet_series()
    s.iloc[-1] = 5.0
    assert _five_sigma_outliers(s).iloc[-1], "precondition: the value is >5 sigma"

    out = clean_series(s.copy(), method="forward_fill")

    assert out.iloc[-1] == 5.0, (
        f"the decision bar's value 5.0 came back as {out.iloc[-1]!r}. A value "
        f"beyond 5 sigma is being erased again, and at the decision bar that "
        f"is a reported indicator failure (finding 7)."
    )


def test_an_interior_value_beyond_five_sigma_is_kept_not_replaced_by_the_previous_bar():
    clean_series = _clean_series()
    s = _quiet_series()
    s.iloc[200] = -3.0
    assert _five_sigma_outliers(s).iloc[200], "precondition: the value is >5 sigma"

    out = clean_series(s.copy(), method="forward_fill")

    assert out.iloc[200] == -3.0, (
        f"bar 200 held -3.0 and came back as {out.iloc[200]!r} (bar 199 is "
        f"{out.iloc[199]!r}). It is being replaced by the previous bar's "
        f"value again, and nothing records it (finding 7)."
    )
    assert out.equals(s), "clean_series changed a series that has no NaN or inf"


def test_early_values_do_not_depend_on_later_bars():
    """
    Item 2. The removed rule measured the mean and standard deviation over the
    WHOLE series, so whether bar 5 survived depended on bars after it. Here
    bar 5 is unremarkable among the first 20 bars and beyond 5 sigma once 430
    quiet bars follow -- the old rule kept it in the short series and erased
    it in the long one.
    """
    clean_series = _clean_series()
    head = pd.Series([1.0] * 20)
    head.iloc[5] = 3.0
    full = pd.concat([head, pd.Series([1.0] * 430)], ignore_index=True)
    assert not _five_sigma_outliers(head).iloc[5], "precondition"
    assert _five_sigma_outliers(full).iloc[5], "precondition"

    out_head = clean_series(head.copy(), method="forward_fill")
    out_full = clean_series(full.copy(), method="forward_fill")

    assert out_full.iloc[:20].tolist() == out_head.tolist() == head.tolist(), (
        f"bar 5 reads {out_head.iloc[5]!r} when the series ends at bar 19 and "
        f"{out_full.iloc[5]!r} when 430 later bars follow. A value at bar 5 "
        f"depends on bars after it: a look-ahead leak (Item 2, finding 7)."
    )

    # And across a real-looking series, at many cut points: cleaning then
    # slicing equals slicing then cleaning.
    rng = np.random.default_rng(5)
    walk = pd.Series(np.cumsum(rng.standard_t(2, 450)) + 100.0)
    out_walk = clean_series(walk.copy(), method="forward_fill")
    for k in range(11, 451, 13):
        prefix = clean_series(walk.iloc[:k].copy(), method="forward_fill")
        assert out_walk.iloc[:k].equals(prefix), (
            f"the first {k} bars clean differently depending on what follows"
        )


def test_inf_is_still_turned_into_nan():
    """The step the ruling keeps. An inf is not a measurement."""
    clean_series = _clean_series()
    s = pd.Series([1.0, 2.0, np.inf, 4.0, -np.inf])

    out = clean_series(s, method="forward_fill")

    assert not np.isinf(out).any(), f"an inf survived: {out.tolist()}"
    # Interior: filled forward like any gap. Decision bar: left NaN, so the
    # caller's guard reports it.
    assert out.iloc[2] == 2.0, out.tolist()
    assert pd.isna(out.iloc[-1]), out.tolist()


# ============================================================
# 4. The engine path -- pandas_ta needed
# ============================================================

def _frame(close, spread=0.01, seed=0):
    rng = np.random.default_rng(seed)
    close = np.asarray(close, dtype=float)
    n = len(close)
    opens = np.r_[close[0], close[:-1]]
    high = np.maximum(opens, close) + spread
    low = np.minimum(opens, close) - spread
    ts = pd.date_range("2026-01-01", periods=n, freq="4h")
    return pd.DataFrame({"timestamp": ts, "open": opens, "high": high,
                         "low": low, "close": close,
                         "volume": 1000.0 + rng.random(n) * 100.0})


def _steady_uptrend_then_drop(drop_bars=6, n=450):
    """
    A long, smooth uptrend (SuperTrend long throughout), then a sharp drop over
    the last `drop_bars` bars -- a fresh flip to short at the decision bar.
    Synthetic, built so the direction series is one-sided before the flip,
    which is the case the removed rule erased.
    """
    rng = np.random.default_rng(7)
    t = np.arange(n)
    close = 10 + 0.02 * t + 0.05 * np.sin(t / 3.0) + rng.normal(0, 0.02, n)
    close[-drop_bars:] = close[-drop_bars - 1] - np.linspace(0.6, 1.2, drop_bars)
    return _frame(close, spread=0.045, seed=7)


def _flat_then_jump(jump=1.0, n=450):
    """A flat market near 10.0, then a 10% move on the decision bar."""
    rng = np.random.default_rng(3)
    close = 10 + rng.normal(0, 0.02, n)
    close[-1] = close[-2] + jump
    return _frame(close, spread=0.01, seed=3)


def _atr_spike(multiple=15.0):
    """
    The pinned AEROUSDT 4h fixture with the last bar's range widened
    `multiple` times: ATR at the decision bar about 2.2x its recent median.
    """
    df = pd.read_csv(PINNED_4H)
    last = df.index[-1]
    c = df.at[last, "close"]
    r = df.at[last, "high"] - df.at[last, "low"]
    df.at[last, "high"] = c + r * multiple / 2
    df.at[last, "low"] = c - r * multiple / 2
    return df


def _without(ind, names):
    """Make the named pandas_ta calls raise, so the fallbacks run. Returns a
    restore function; no fixture, so run_tests.py can run the caller."""
    saved = {name: getattr(ind.ta, name) for name in names}

    def boom(*a, **k):
        raise RuntimeError("primary disabled by the test")

    for name in names:
        setattr(ind.ta, name, boom)

    def restore():
        for name, fn in saved.items():
            setattr(ind.ta, name, fn)
    return restore


def test_a_fresh_supertrend_flip_at_the_decision_bar_survives():
    if not _engine_available():
        pytest.skip("pandas_ta not installed")
    import indicators.indicators as ind
    from core import config

    df = _steady_uptrend_then_drop(drop_bars=6)
    raw = ind.ta.supertrend(df["high"], df["low"], df["close"],
                            length=config.SUPERTREND_LENGTH,
                            multiplier=config.SUPERTREND_MULT)
    raw_dir = raw.iloc[:, 1]
    assert raw_dir.iloc[-1] == -1.0 and int((raw_dir < 0).sum()) == 6, (
        "precondition: the frame flips short for exactly its last 6 bars")
    assert _five_sigma_outliers(raw_dir.dropna()).iloc[-1], (
        "precondition: the flip is beyond 5 sigma of the direction series")

    out, failures = ind.add_technical_indicators(df)

    failed = [f.indicator for f in failures]
    assert "SuperTrend" not in failed, (
        f"a fresh 6-bar SuperTrend flip was reported as a failure: {failures}. "
        f"The flip is being erased as an outlier again (finding 7)."
    )
    assert out["ST_Direction"].iloc[-1] == -1.0
    assert out["SuperTrend"].iloc[-1] == raw.iloc[-1, 0]
    # The same drop took RSI and ATR past 5 sigma too.
    assert "RSI" not in failed and "ATR" not in failed, failures
    raw_rsi = ind.ta.rsi(df["close"], length=config.RSI_LENGTH)
    assert out["RSI"].iloc[-1] == raw_rsi.iloc[-1]


def test_an_atr_spike_at_the_decision_bar_survives():
    if not _engine_available():
        pytest.skip("pandas_ta not installed")
    import indicators.indicators as ind
    from core import config

    df = _atr_spike()
    raw = ind.ta.atr(df["high"], df["low"], df["close"],
                     length=config.ATR_LENGTH)
    ratio = raw.iloc[-1] / raw.iloc[-51:-1].median()
    assert 2.0 < ratio < 2.5, f"precondition: ATR spike is {ratio:.2f}x"
    assert _five_sigma_outliers(raw.dropna()).iloc[-1], "precondition"

    out, failures = ind.add_technical_indicators(df)

    assert "ATR" not in [f.indicator for f in failures], (
        f"an ATR of {ratio:.2f}x its recent median was reported as a failure: "
        f"{failures}. ATR sets the stop and all three targets; erasing it "
        f"removes the whole risk plan (finding 7)."
    )
    assert out["ATR"].iloc[-1] == raw.iloc[-1]


def test_the_backup_atr_keeps_the_spike_too():
    if not _engine_available():
        pytest.skip("pandas_ta not installed")
    import indicators.indicators as ind
    from core import config

    df = _atr_spike()
    tr = pd.concat([df["high"] - df["low"],
                    (df["high"] - df["close"].shift(1)).abs(),
                    (df["low"] - df["close"].shift(1)).abs()],
                   axis=1).max(axis=1, skipna=True)
    expected = tr.ewm(alpha=1.0 / float(config.ATR_LENGTH),
                      adjust=False).mean()
    assert _five_sigma_outliers(expected).iloc[-1], "precondition"

    restore = _without(ind, ["atr"])
    try:
        out, failures = ind.add_technical_indicators(df)
    finally:
        restore()

    assert "ATR" not in [f.indicator for f in failures], failures
    assert out["ATR"].iloc[-1] == expected.iloc[-1]


def test_a_decision_bar_move_in_a_flat_market_survives_in_every_indicator():
    """
    A 10% move on the decision bar after a flat market. The removed rule
    erased EMA_20, EMA_50, the SuperTrend and ATR on the primary paths, and
    RSI as well on the fallbacks.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")
    import indicators.indicators as ind

    df = _flat_then_jump()

    out, failures = ind.add_technical_indicators(df)
    assert failures == [], (
        f"a 10% decision-bar move after a flat market was reported as "
        f"failures: {[f.indicator for f in failures]} (finding 7)")
    for col in ("EMA_20", "EMA_50", "RSI", "ADX", "SuperTrend",
                "ST_Direction", "ATR"):
        assert np.isfinite(out[col].iloc[-1]), col

    restore = _without(ind, ["ema", "rsi", "atr"])
    try:
        out_fb, failures_fb = ind.add_technical_indicators(df)
    finally:
        restore()
    assert failures_fb == [], (
        f"the fallback paths reported failures on the same frame: "
        f"{[f.indicator for f in failures_fb]} (finding 7)")
    close = df["close"]
    for length, col in ((20, "EMA_20"), (50, "EMA_50")):
        expected = close.ewm(span=length, adjust=False).mean().iloc[-1]
        assert out_fb[col].iloc[-1] == expected, col
    for col in ("RSI", "ATR"):
        assert out_fb[col].iloc[-1] != out_fb[col].iloc[-2], (
            f"the {col} fallback's decision bar equals the previous bar")


def test_a_value_planted_beyond_five_sigma_is_written_unchanged():
    """
    Each pandas_ta output in scope gets a value beyond 5 sigma planted at an
    interior bar and at the decision bar; the frame must carry both unchanged.
    Covers ADX, which no realistic frame above takes past 5 sigma, and the
    SuperTrend level. The direction is +/-1 and cannot be planted this way;
    the flip test covers it.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")
    import indicators.indicators as ind

    from core import config

    df = pd.read_csv(PINNED_4H)
    interior = len(df) - 100
    planted_values = {}

    def planted(real, fn_name, column=None):
        def wrapped(*a, **k):
            out = real(*a, **k).copy()
            s = out if column is None else out.iloc[:, column]
            far = float(s.mean() + 20 * s.std())
            planted_values[(fn_name, k.get("length"))] = far
            if column is None:
                out.iloc[interior] = far
                out.iloc[-1] = far
            else:
                out.iloc[interior, column] = far
                out.iloc[-1, column] = far
            return out
        return wrapped

    # (pandas_ta call, output column planted, frame column, the call's length)
    cases = (("ema", None, "EMA_20", config.EMA_FAST),
             ("ema", None, "EMA_50", config.EMA_SLOW),
             ("rsi", None, "RSI", config.RSI_LENGTH),
             ("adx", 0, "ADX", config.ADX_LENGTH),
             ("supertrend", 0, "SuperTrend", config.SUPERTREND_LENGTH),
             ("atr", None, "ATR", config.ATR_LENGTH))
    for fn_name, column, col, length in cases:
        real = getattr(ind.ta, fn_name)
        planted_values.clear()
        setattr(ind.ta, fn_name, planted(real, fn_name, column))
        try:
            out, failures = ind.add_technical_indicators(df.copy())
        finally:
            setattr(ind.ta, fn_name, real)
        far = planted_values[(fn_name, length)]
        # Exact equality, not merely "present": if the primary's value were
        # erased, the EMA, RSI and ATR fallbacks would recompute an ordinary
        # value and no failure would show -- the planted value is the proof
        # the primary's own output was written.
        assert col not in [f.indicator for f in failures], (
            f"{col}: a planted value beyond 5 sigma at the decision bar was "
            f"reported as a failure: {failures} (finding 7)")
        assert out[col].iloc[-1] == far, (
            f"{col}: the decision bar holds {out[col].iloc[-1]!r}, not the "
            f"value pandas_ta returned ({far!r}) (finding 7)")
        assert out[col].iloc[interior] == far, (
            f"{col}: bar {interior} holds {out[col].iloc[interior]!r}, not the "
            f"value pandas_ta returned ({far!r}); bar {interior - 1} is "
            f"{out[col].iloc[interior - 1]!r} (finding 7)")
