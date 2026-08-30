"""
Sequence item 15 — Item 2 (No Future Information / Look-Ahead Bias), and the
half of item 9a that was hiding one layer down.

THE INVARIANT

    "Information unavailable at the exact decision timestamp must never
     influence that decision, whether directly or through a derived signal."

And the Constitution's own note on it:

    Item 2 "deserves the most explicit, deliberate checking of any invariant in
    this document once [backtesting] starts, since a backtest with a hidden
    look-ahead leak is the single most common way a system convinces itself it
    works when it doesn't."

That note is why this is a sequence item of its own rather than a line in
item 9. The plan files it under "backtest on-ramp".

WHAT WAS ACTUALLY THERE — AND AN HONEST GRADING OF IT

Nine `.bfill()` calls fed decisions. None of them was a LIVE leak, and the
report should say so plainly rather than borrow severity it has not earned:
the engine makes exactly one decision, at the last bar of a 450-row frame.
Nothing exists after that bar to leak backwards from, and `bfill` only ever
fires on the leading edge — `ffill` covers every later gap. The contaminated
rows sit four hundred bars behind every window the decision reads.

The leak is latent. It becomes live on the day a backtest walks the decision
timestamp backwards, with no code change to blame it on. That is the whole
argument for clearing it now, while the cost is nine lines.

THE PART THAT WAS NOT LATENT

`clean_series` ended with

    if series.isna().any():
        median_val = series.median()
        series = series.fillna(median_val if isfinite(median_val) else 0.0)

so an indicator that came back entirely NaN left that function as a column of
ZEROS. The callers' guards read

    rsi = clean_series(ta.rsi(...))
    if rsi is None or rsi.isna().all():        # already false
        raise ValueError("pandas_ta returned no usable RSI")

`isna().all()` could not be true, because the NaNs were gone before the check
ran. A completely failed RSI became 0 on every bar — maximum oversold. A
completely failed ATR became 0, which is a stop distance of zero.

Item 9a removed the fabricated constants from the `except` branches and did not
look inside the helper the success path ran through. Its tests injected failures
by RAISING, so the returns-nothing-usable path was never exercised and the
guards were never watched to see whether they could fire. Test 4 below is the
one that would have caught it.

Two more of the same shape, found by reading every fill rather than every
`bfill`:

  indicators.py  VWMA  `.fillna(close_prices)` — the identical substitution
                       item 9a removed from the except branch eight lines
                       below, where the surviving comment explains that it
                       "invented the most favourable number available": a zero
                       VWMA distance and a perfect 20 of 20 entry points.
  volume_profile       `.fillna(0)` on low/high — item 9's recorded leftover.
                       The profile bins between price_min and price_max, so one
                       zeroed low drags the range to the origin and the HVN
                       that comes out is a structural level at a price that
                       never traded. engine_core hands that to
                       calculate_stop_targets.

WHAT IS DELIBERATELY UNCHANGED

utils/plotting.py still backfills. It draws a picture and feeds no decision.
Test 7 pins that as a decision rather than an oversight — it fails if the
exemption spreads to a module that does feed a decision.
"""

import ast
import os

import numpy as np
import pandas as pd

from conftest import REPO_ROOT, fixture

# The one module allowed to fill from a later row, and why.
BACKFILL_EXEMPT = {"utils/plotting.py"}

PINNED_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "fixtures", "pinned")
UNREACHABLE = "http://127.0.0.1:1"


def _engine_available():
    try:
        import pandas_ta  # noqa: F401
        return True
    except Exception:
        return False


def _clean_series():
    """
    clean_series, imported without dragging pandas_ta in.

    indicators.py imports pandas_ta at module scope, so the tests that only
    exercise this one pure function would otherwise skip on a machine without
    it — and those are the tests that pin the defect most precisely.
    """
    src = open(os.path.join(REPO_ROOT, "indicators", "indicators.py"),
               encoding="utf-8").read()
    start = src.index("def clean_series")
    end = src.index("def pct_slope")
    ns = {"pd": pd, "np": np}
    exec(src[start:end], ns)
    return ns["clean_series"]


def _ohlcv():
    return pd.read_csv(fixture("ohlcv_clean_4h.csv"))


# ============================================================
# 1–3. The helper itself
# ============================================================

def test_a_gap_is_never_filled_from_a_later_row():
    """
    The direct statement of Item 2 at the smallest scale there is.

    Position 0 has no past. Whatever comes out of it must not be the value that
    first appears at position 5.
    """
    clean_series = _clean_series()

    series = pd.Series([np.nan] * 5 + [10.0, 11.0, 12.0, 13.0, 14.0])
    out = clean_series(series, method="forward_fill")

    leading = out.iloc[:5]
    assert leading.isna().all(), (
        f"the first five values have no past to be filled from and came back "
        f"as {list(leading)}. 10.0 is the value at position 5 — a bar in their "
        f"future. This is Item 2 at its smallest scale."
    )
    assert list(out.iloc[5:]) == [10.0, 11.0, 12.0, 13.0, 14.0], (
        "the forward half of the fill was damaged"
    )


def test_an_interior_gap_is_still_filled_forward():
    """
    The other half, and the reason this is a change rather than a deletion.

    Carrying the last known value forward uses only the past. Removing that as
    well would have made the fix look thorough and left the engine unable to
    tolerate a single missing bar.
    """
    clean_series = _clean_series()

    out = clean_series(pd.Series([1.0, 2.0, np.nan, np.nan, 5.0]),
                       method="forward_fill")

    assert list(out) == [1.0, 2.0, 2.0, 2.0, 5.0], (
        f"an interior gap should carry 2.0 forward; got {list(out)}"
    )


def test_an_all_nan_series_comes_back_all_nan():
    """
    The one that matters most, and the one item 9a needed.

    This returned a column of ZEROS. Every caller's `isna().all()` guard was
    therefore reading a series with no NaNs in it and could not fire.
    """
    clean_series = _clean_series()

    out = clean_series(pd.Series([np.nan] * 20), method="forward_fill")

    assert out.isna().all(), (
        f"an all-NaN series came back as {out.unique()}. Callers guard on "
        f"`isna().all()` and that guard is now false, so a completely failed "
        f"indicator passes as a real reading of zero — maximum oversold for "
        f"RSI, no trend at all for ADX, and for ATR a stop distance of zero."
    )


def test_an_explicit_substitution_still_works_when_asked_for_by_name():
    """
    `fill_value` survives. The objection was never to substitution — it was to
    substitution nobody requested. Here the caller names the method and supplies
    the number.
    """
    clean_series = _clean_series()

    out = clean_series(pd.Series([np.nan, 1.0, np.nan]),
                       method="fill_value", fallback_value=7.0)
    assert list(out) == [7.0, 1.0, 7.0]


# ============================================================
# 4. The guard that could not fire
# ============================================================

def test_an_indicator_that_returns_nothing_usable_is_reported_as_a_failure():
    """
    THE LOAD-BEARING TEST.

    Item 9a's tests injected failures by making pandas_ta RAISE. This injects
    the other failure: the call succeeds and returns a frame with no usable
    values in it. That path ran through clean_series, came out as zeros, and
    reported nothing.

    ADX is used because it is the one indicator with no recomputation fallback,
    so the failure is observable rather than absorbed — and because ADX 0 reads
    as "no trend whatsoever", the opposite end of the scale from the 25.0 item
    9a removed, which is the more misleading of the two.
    """
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return

    import pandas_ta as ta
    from indicators import indicators

    df = _ohlcv()
    original = ta.adx

    def all_nan_adx(*args, **kwargs):
        idx = args[0].index if args else df.index
        return pd.DataFrame({0: [np.nan] * len(idx),
                             1: [np.nan] * len(idx),
                             2: [np.nan] * len(idx)}, index=idx)

    try:
        ta.adx = all_nan_adx
        indicators.ta.adx = all_nan_adx
        out, failures = indicators.add_technical_indicators(df, inplace=False)
    finally:
        ta.adx = original
        indicators.ta.adx = original

    names = [f.indicator for f in failures]
    assert "ADX" in names, (
        f"ta.adx returned a frame with no usable values and the run reported "
        f"failures {names or '[]'}. Before sequence item 15 this produced an "
        f"ADX column of zeros and no failure at all, because clean_series had "
        f"replaced every NaN before the guard looked."
    )

    if "ADX" in out.columns:
        assert not (out["ADX"] == 0).all(), (
            "the ADX column is entirely zero — the fabrication is back"
        )


# ============================================================
# 5–6. Real indicator output
# ============================================================

def test_an_indicators_warmup_rows_stay_empty():
    """
    A 14-period RSI has no value at bar 3. It used to hold the value RSI first
    took at bar 14.
    """
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return

    from core import config
    from indicators.indicators import add_technical_indicators

    out, _ = add_technical_indicators(_ohlcv(), inplace=False)

    warmup = out["RSI"].iloc[:config.RSI_LENGTH - 1]
    assert warmup.isna().any(), (
        "no RSI warm-up row is empty. Either the fill is back, or RSI is being "
        "computed with a window that needs no warm-up — check which before "
        "changing this test."
    )


def test_the_decision_bar_is_unaffected():
    """
    The counterweight. Removing fills must not have emptied the values the
    engine actually reads.

    This is why the item is safe: everything the decision touches is at the
    last bar of a 450-row frame, and every fill that was removed acted on the
    leading edge.
    """
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return

    from indicators.indicators import add_technical_indicators

    out, failures = add_technical_indicators(_ohlcv(), inplace=False)
    assert not failures, f"clean data produced failures: {failures}"

    for col in ("EMA_20", "EMA_50", "RSI", "ADX", "ATR", "VWMA",
                "EMA20_Slope", "EMA50_Slope"):
        assert col in out.columns, f"{col} is missing from the frame"
        assert not pd.isna(out[col].iloc[-1]), (
            f"{col} is NaN at the last bar — the bar every decision reads. "
            f"Removing the leading-edge fills should not have reached it."
        )


# ============================================================
# 7. The rule, held in place
# ============================================================

def _backward_fills(rel):
    """
    Every backward fill in one module, found in the SYNTAX rather than the text.

    A text scan cannot tell an instruction from a quotation, and this codebase
    quotes the calls it removed at length — clean_series's own docstring
    reproduces `.ffill().bfill()`, and bias_engine's explains a block that was
    deleted two items ago. Matching on the parse tree means prose is free to be
    as explicit as it likes.
    """
    with open(os.path.join(REPO_ROOT, *rel.split("/")), encoding="utf-8") as f:
        tree = ast.parse(f.read())

    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr == "bfill":
            found.append(".bfill()")
        elif isinstance(node, ast.Call):
            for kw in node.keywords:
                if (kw.arg == "limit_direction"
                        and isinstance(kw.value, ast.Constant)
                        and kw.value.value == "both"):
                    found.append("limit_direction='both'")
                elif (kw.arg == "method"
                        and isinstance(kw.value, ast.Constant)
                        and kw.value.value == "bfill"):
                    found.append("method='bfill'")
    return found


def test_only_the_chart_may_fill_backwards():
    """
    Source-level, and scoped by module rather than by line, so moving a fill
    somewhere else does not escape it.

    plotting.py is exempt because it draws a picture and feeds no decision. The
    exemption is a list of one, declared at the top of this file, so widening it
    is a visible edit rather than a silent drift.
    """
    from conftest import all_python_files

    offenders = []
    for rel in all_python_files(include_doc_tooling=False):
        norm = rel.replace("\\", "/")
        if norm in BACKFILL_EXEMPT or norm.startswith("tests/"):
            continue
        for hit in _backward_fills(norm):
            offenders.append(f"{norm}: {hit}")

    assert not offenders, (
        "a decision path fills from a later row:\n  " + "\n  ".join(offenders)
        + "\n\nItem 2: information unavailable at the decision timestamp must "
          "never influence that decision. In the engine as it stands the "
          "analysis is made at the last bar and this cannot reach it — but a "
          "backtest moves the decision timestamp backwards, and then it can, "
          "with no code change to blame."
    )


def test_the_chart_exemption_still_applies_to_something():
    """
    An exemption list nobody is on is a list that will be widened without
    anyone noticing it was empty. If plotting stops backfilling, delete the
    entry rather than leaving it standing.
    """
    for rel in BACKFILL_EXEMPT:
        path = os.path.join(REPO_ROOT, *rel.split("/"))
        assert os.path.exists(path), f"{rel} is exempt and does not exist"
        assert _backward_fills(rel), (
            f"{rel} is on the backfill exemption list and no longer backfills. "
            f"Remove it from BACKFILL_EXEMPT — an exemption for nothing is how "
            f"the list grows back."
        )


# ============================================================
# 8–9. The two substitutions found alongside
# ============================================================

def test_the_volume_profile_refuses_rather_than_pricing_a_bar_at_zero():
    """
    `.fillna(0)` on low/high was item 9's recorded leftover. The profile bins
    between price_min and price_max, so a single zeroed low drags the range to
    the origin and empties every bin above it. What comes out is an HVN at a
    price that never traded, which engine_core passes to calculate_stop_targets
    as a structural level.

    A gap a forward fill cannot close is the leading edge, so this builds one.
    """
    from indicators.volume_profile import compute_volume_profile

    df = _ohlcv().copy()
    df.loc[df.index[0], "low"] = np.nan

    profile, hvn, lvn = compute_volume_profile(df, num_bins=10)

    assert hvn is None and lvn is None, (
        f"a frame with an unfillable low produced hvn={hvn}, lvn={lvn}. If the "
        f"gap was zero-filled, those levels come from a bar priced at nothing."
    )


def test_the_structure_engine_refuses_a_frame_it_cannot_forward_fill():
    """
    structure.py filled OHLCV with zero and then read close.iloc[-1] as the
    current price on the very next line.
    """
    from structure.structure import calculate_structure

    df = _ohlcv().copy()
    df.loc[df.index[0], "close"] = np.nan

    try:
        calculate_structure(df)
    except ValueError as e:
        assert "forward fill" in str(e).lower() or "gap" in str(e).lower(), (
            f"it refused, but for an unexpected reason: {e}"
        )
        return

    raise AssertionError(
        "calculate_structure accepted a frame with a gap a forward fill cannot "
        "close. It used to substitute 0.0 and then read a price from it."
    )
