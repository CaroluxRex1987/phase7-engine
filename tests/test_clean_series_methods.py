"""
clean_series accepts only methods that read no later row (round 8's F6).

Round 8's F6 (Minor, Item 2; also Item 16), made in the label and record batch
by point 8 of the triage of 5 October 2026: `clean_series` kept a method,
'interpolate', that filled an interior gap by linear interpolation -- from the
values on both sides of the gap, so every filled row read the next valid row,
a bar in its future. No caller outside tests/ used it, nor 'drop'. Both are
removed, and a name the function does not know now raises instead of falling
through every branch and returning the series unfilled.

tests/test_no_lookahead.py pins the forward_fill branch only; nothing pinned
the method list, so a look-ahead method could sit one keyword argument away.
The first test here closes that: it asks the function which methods it
accepts (from its own error message, so the list cannot drift from a copy
here) and checks each one against later rows. The second proves the check
can fail. Everything here runs without pandas_ta and without fixtures (so
run_tests.py's error count does not move).
"""

import os
import re

import numpy as np
import pandas as pd
import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _clean_series():
    """clean_series, imported without dragging pandas_ta in -- the same
    approach as tests/test_no_lookahead.py."""
    src = open(os.path.join(REPO_ROOT, "indicators", "indicators.py"),
               encoding="utf-8").read()
    start = src.index("def clean_series")
    end = src.index("def add_technical_indicators")
    ns = {"pd": pd, "np": np}
    exec(src[start:end], ns)
    return ns["clean_series"]


def _accepted_methods(clean_series):
    """The names clean_series accepts, read from its own refusal."""
    with pytest.raises(ValueError) as exc:
        clean_series(pd.Series([1.0]), method="no-such-method")
    m = re.search(r"accepted: (.+)$", str(exc.value))
    assert m, f"the refusal does not list the accepted methods: {exc.value}"
    names = [n.strip() for n in m.group(1).split(",")]
    assert names, "the refusal lists no accepted method"
    return names


# Gaps inside, a warm-up at the start, a gap at the end, and an inf.
_SERIES = pd.Series([np.nan, np.nan, 3.0, np.nan, np.nan, 6.0, 7.0, np.nan,
                     9.0, np.inf, 11.0, 12.0, np.nan, np.nan])


def _later_rows_read(clean):
    """
    The rows whose cleaned value changes when only LATER values change.

    For each cut k, every value after k is replaced by a different value --
    the NaN and inf positions are kept, so the change is in the numbers, not
    in which rows exist. A cleaned value at a row <= k that is not NaN must
    not move: it was made from rows <= k. (Whether a gap at the very end is
    left NaN may depend on whether a later value exists -- the trailing-edge
    rule of finding 3 -- which is why NaN outputs are not compared.)
    """
    base = clean(_SERIES.copy())
    finite = np.isfinite(_SERIES.to_numpy())
    leaked = []
    for k in range(len(_SERIES) - 1):
        changed = _SERIES.copy()
        later = np.arange(len(_SERIES)) > k
        changed[later & finite] = changed[later & finite] * 10.0 + 1000.0
        out = clean(changed)
        for i in range(k + 1):
            a, b = base.iloc[i], out.iloc[i]
            if pd.isna(a) and pd.isna(b):
                continue
            if pd.isna(a) or pd.isna(b) or a != b:
                leaked.append((k, i, a, b))
    return leaked


def test_no_accepted_method_reads_a_later_row():
    """Item 2, for every method clean_series accepts, not only forward_fill."""
    clean_series = _clean_series()
    for method in _accepted_methods(clean_series):
        kwargs = {"fallback_value": -1.0} if method == "fill_value" else {}
        leaked = _later_rows_read(
            lambda s, m=method, kw=kwargs: clean_series(s, method=m, **kw))
        assert not leaked, (
            f"method {method!r} gives rows that change when only later rows "
            f"change (cut, row, before, after): {leaked[:5]}. A value made "
            f"from a bar in its future is Item 2's look-ahead."
        )


def test_the_check_catches_a_linear_interpolation():
    """
    The check above is not vacuous: the removed branch, run through it, is
    caught. This is the code F6 named, verbatim.
    """
    def interpolate(s):
        s = s.replace([np.inf, -np.inf], np.nan)
        return s.interpolate(method="linear", limit_direction="forward")

    assert _later_rows_read(interpolate), (
        "the check passed a linear interpolation, so it cannot see a fill "
        "from a later row and the test above proves nothing"
    )


def test_the_removed_methods_are_refused_by_name():
    clean_series = _clean_series()
    for method in ("interpolate", "drop"):
        with pytest.raises(ValueError, match=f"unknown method '{method}'"):
            clean_series(pd.Series([1.0, np.nan, 3.0]), method=method)


def test_fill_value_without_a_number_is_refused():
    """It used to return the series unfilled, silently."""
    clean_series = _clean_series()
    with pytest.raises(ValueError, match="needs a fallback_value"):
        clean_series(pd.Series([1.0, np.nan, 3.0]), method="fill_value")
