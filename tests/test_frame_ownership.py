"""
Sequence item 6 — T2-1, shared-frame aliasing, and the two caches.

THE PRINCIPLE, STATED AS A TEST

A function that is handed a DataFrame does not own it. If it needs to change
the data, it works on its own copy. The caller's frame is the same afterwards
as it was before.

This is not stylistic. The engine passes one frame through eight stages, and a
module that quietly edits it changes the inputs of every stage after it. The
edits in question were all NaN-fills, so they would not raise — the engine
would keep producing confident numbers computed from data a later stage had
silently rewritten.

WHAT WAS FIXED

  models/bias_engine.py        calculate_dynamic_bias took `df` and never read
                               it. Its only use of the frame was to fill NaNs in
                               four columns, three of which it does not read.
                               A write-only parameter. Deleted, not copied —
                               copying would have left a no-op behind.

  structure/structure.py       calculate_structure had a copy_df flag that
                               defaulted to True; both call sites passed False.
                               The parameter is gone; it always copies now. A
                               knob whose unsafe setting is the one everybody
                               chooses is not a safeguard.

  indicators/volume_profile.py compute_volume_profile cleaned low/high/volume on
                               the caller's frame, and its inf-replacement ran
                               on every call rather than only when something was
                               wrong. Now copies.

  utils/plotting.py            plot_engine_chart filled NaNs in the OHLC columns
                               of the frame it was asked to draw. Now copies.

The last two were not named in the Step 5 plan. They are the same class, found
while fixing the two that were.

  core/engine_core.py          _indicator_cache and _structure_cache deleted.
                               They never returned a hit in any production path,
                               and on the one reachable hit path the cached
                               frame was mutated in place.

WHY THIS IS OUTPUT-INVARIANT

Every one of those writes is conditional on NaN or non-finite values, except
volume_profile's inf-replacement, which is a no-op on finite data. Data that
has been through add_technical_indicators has neither. So on any real run they
did nothing, and the decision-object snapshot proves it.

That is also what made them dangerous rather than merely wrong: they had never
fired, so nothing had ever gone visibly wrong, so there was no pressure to look
at them.

NOT FIXED HERE. Two of those fills are also fabrications:
bias_engine substituted the close price for a missing RSI (a price into a 0-100
oscillator), and volume_profile substitutes zero for a missing high or low.
Item 6 stops them writing into frames they do not own; sequence item 9 is where
the fallbacks are given honest semantics. Recorded as riders there.
"""

import ast
import inspect
import os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PINNED_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "fixtures", "pinned")


def _engine_available():
    try:
        import pandas_ta  # noqa: F401
        return True
    except Exception:
        return False


def _dirty_frame():
    """
    Real pinned data, run through the indicator pipeline, then damaged.

    The damage is the point: a NaN in each column these functions used to
    repair, plus one inf. A function that still wants to write to its input
    will do it here. Clean data would prove nothing, because every one of these
    writes was conditional on exactly the defects being injected.

    Real data rather than a synthetic ramp, because the structure engine has to
    be able to analyse it — otherwise a failure to process would look like a
    failure of ownership.
    """
    import numpy as np

    from data.data_fetcher import DataFetcher
    from indicators.indicators import add_technical_indicators

    fetcher = DataFetcher()
    fetcher.base_url = "http://127.0.0.1:1"
    try:
        DataFetcher.set_pinned_source(PINNED_DIR)
        df = fetcher.get_tf("AEROUSDT", "4h", limit=300)
    finally:
        DataFetcher.clear_pinned_source()

    df = add_technical_indicators(df)

    # Damage a handful of interior rows. Not the last row — several callers
    # read .iloc[-1] and the test is about ownership, not about their
    # tolerance for a missing final candle.
    df.loc[df.index[5], "close"] = np.nan
    df.loc[df.index[6], "high"] = np.nan
    df.loc[df.index[7], "low"] = np.nan
    df.loc[df.index[8], "volume"] = np.inf
    df.loc[df.index[9], "EMA_20"] = np.nan
    df.loc[df.index[10], "RSI"] = np.nan
    return df


def _unchanged(before, after):
    """
    pandas' .equals treats NaN in the same position as equal, which is exactly
    the comparison wanted here — the frame must come back with its damage
    intact, not repaired.
    """
    return list(before.columns) == list(after.columns) and before.equals(after)


def test_calculate_structure_does_not_touch_the_callers_frame():
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return

    from structure.structure import calculate_structure

    df = _dirty_frame()
    before = df.copy(deep=True)
    calculate_structure(df, lookback=8)

    assert _unchanged(before, df), (
        "calculate_structure modified the frame it was given.\n"
        "It writes STRUCTURE, HVN and LVN and fills the OHLCV columns. Those "
        "belong on its own copy — the caller's frame is the input to every "
        "later stage of the engine."
    )


def test_compute_volume_profile_does_not_touch_the_callers_frame():
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return

    from indicators.volume_profile import compute_volume_profile

    df = _dirty_frame()
    before = df.copy(deep=True)
    compute_volume_profile(df)

    assert _unchanged(before, df), (
        "compute_volume_profile modified the frame it was given.\n"
        "It is asked for a read-only summary. Its inf-replacement used to run "
        "on every call, so this fired even on clean data."
    )


def test_plot_engine_chart_does_not_touch_the_callers_frame():
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return

    try:
        import matplotlib
        matplotlib.use("Agg")
    except Exception:
        pass                    # the suite already renders charts headless
    from utils.plotting import plot_engine_chart

    df = _dirty_frame()
    before = df.copy(deep=True)
    plot_engine_chart(
        df=df,
        entry_data={"entry_zone_lower": 100.0, "entry_zone_upper": 105.0},
        risk_data={"atr_stop": 95.0, "targets": (110.0, 115.0, 120.0)},
        save_path=os.path.join(REPO_ROOT, "Logs", "Charts", "_ownership_test.png"),
    )

    assert _unchanged(before, df), (
        "plot_engine_chart modified the frame it was given.\n"
        "engine_core passes df_struct to it — the frame the whole analysis was "
        "computed from. A renderer must not edit what it renders."
    )


def test_calculate_dynamic_bias_takes_no_frame():
    """
    Signature-level. The frame parameter was write-only: the function filled
    NaNs in four of the caller's columns and read none of them.

    Restoring it as a copy-taking parameter would be worse than the bug — a
    parameter that is accepted, copied, cleaned and discarded.
    """
    from models.bias_engine import calculate_dynamic_bias

    params = inspect.signature(calculate_dynamic_bias).parameters
    assert "df" not in params, (
        "calculate_dynamic_bias has a `df` parameter again. It computes its "
        "score entirely from scalar arguments; the frame was write-only."
    )


def test_calculate_structure_has_no_copy_opt_out():
    """
    The parameter, not just its value. Leaving copy_df=True as a default would
    have left the unsafe path one keyword away, and it is the path both call
    sites took for as long as it existed.
    """
    from structure.structure import calculate_structure

    params = inspect.signature(calculate_structure).parameters
    assert "copy_df" not in params, (
        "calculate_structure accepts copy_df again. Every call site passed "
        "False the last time this existed."
    )


def test_the_engine_holds_no_caches():
    """
    Item 4/12 dissolved by repair rather than adjudication.

    A reintroduced cache is not automatically wrong, but it would reopen a
    dispute two audit runs disagreed about, so it should not arrive quietly.
    """
    from core.engine_core import Phase7Engine

    engine = Phase7Engine()
    cache_attrs = [a for a in vars(engine) if "cache" in a.lower()]

    assert not cache_attrs, (
        f"Phase7Engine has cache attributes again: {', '.join(cache_attrs)}.\n"
        "The previous two never returned a hit in any production path — one "
        "router, one route, then process exit — and the hit path they did have "
        "mutated the cached frame in place. If a cache is genuinely needed now, "
        "it needs its own justification and a test that proves it is coherent "
        "under mutation."
    )


def test_engine_core_does_not_reference_a_cache():
    """
    Stronger than the attribute check: a cache built as a module-level dict or
    a closure would not show up in vars(engine).
    """
    with open(os.path.join(REPO_ROOT, "core", "engine_core.py"), encoding="utf-8") as f:
        tree = ast.parse(f.read())

    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            names.add(node.id)
        elif isinstance(node, ast.Attribute):
            names.add(node.attr)

    offenders = sorted(n for n in names if "cache" in n.lower())

    assert not offenders, (
        f"core/engine_core.py refers to caching again: {', '.join(offenders)}."
    )
