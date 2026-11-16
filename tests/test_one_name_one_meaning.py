"""
F8, round 8 (Minor, T1 Item 10 -- Consistent Semantics), 11 October 2026.

Item 10: "The same term, score, or scale must mean the same thing in every
module that uses it." Round 8 found two breaks of it:

1. "VWMA" named two calculations. indicators/indicators.py's VWMA column is a
   20-candle rolling ratio of sum(close x volume) to sum(volume), which
   entry_model scores as "VWMA Distance". structure.py's
   _volume_sentiment_simple called its own reading vwma_recent / vwma_prev /
   vwma_slope: two 5-candle volume-weighted means of the close, a different
   window and a different formula, feeding the volume sentiment and through
   it the bias score. The two can point opposite ways in the same run.
   Fixed by renaming structure.py's three names; every value is the same.

2. The panel printed momentum_mode twice: after the slash on the TREND line,
   and again as the whole of the MOMENTUM line. Fixed by removing the
   MOMENTUM line.

No fixtures, so run_tests.py runs every test here; none needs pandas_ta.
"""

import ast
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# --- 1. the name VWMA ------------------------------------------------------

# What ties a function to the engine's VWMA: the column it is stored in, the
# setting that sets its window, and the entry-score part it is scored into.
# THE REDESIGN'S STAGE 4, 15 November 2026: "VWMA_MAX_POINTS" and
# "vwma_pts" stood in this set. Both were entry quality's -- the 20-point
# VWMA component's maximum and its sub-score -- and the component left with
# the design (the draft's section 3.2). An anchor that no longer exists
# cannot anchor anything, and leaving it here would let a future function
# that assigns a vwma-named local pass the check by naming a dead constant.
# test_every_anchor_still_exists_in_the_engine below holds that.
VWMA_ANCHORS = frozenset({"VWMA", "VWMA_LENGTH"})


def _vwma_names_without_an_anchor(tree):
    """
    (function name, [vwma-named locals]) for every function that assigns a
    name containing "vwma" without touching the engine's VWMA anywhere in
    its body -- no "VWMA" column, no VWMA_LENGTH, no VWMA_MAX_POINTS, no
    "vwma_pts". Read from the parse tree, not the source text, so comments
    and docstrings that mention the old names are not counted.
    """
    found = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        assigned = sorted({
            n.id for n in ast.walk(node)
            if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store)
            and "vwma" in n.id.lower()
        })
        if not assigned:
            continue
        anchored = any(
            (isinstance(n, ast.Constant) and n.value in VWMA_ANCHORS)
            or (isinstance(n, ast.Name) and n.id in VWMA_ANCHORS)
            or (isinstance(n, ast.Attribute) and n.attr in VWMA_ANCHORS)
            for n in ast.walk(node)
        )
        if not anchored:
            found.append((node.name, assigned))
    return found


def _engine_trees():
    from core.code_fingerprint import iter_source_files

    for path in iter_source_files():
        with open(path, "rb") as fh:
            yield path, ast.parse(fh.read().decode("utf-8"))


def test_a_name_that_says_vwma_reads_the_engines_vwma():
    """
    The same walk code_hash takes (tests/ and docs/ excluded by directory):
    every function that names something vwma reads the engine's VWMA.
    """
    offenders = []
    for path, tree in _engine_trees():
        for func, names in _vwma_names_without_an_anchor(tree):
            offenders.append(f"{path}: {func} assigns {names}")
    assert not offenders, (
        "a name says VWMA but the function never reads the engine's VWMA "
        "(Item 10):\n  " + "\n  ".join(offenders)
    )


def test_no_engine_function_assigns_a_vwma_name_at_all_now():
    """
    THE REDESIGN'S STAGE 4, 15 November 2026. This was
    test_the_check_sees_the_vwma_that_is_there, and its anchor was
    entry_model's VWMA scoring: the one function that assigned vwma-named
    locals AND read the engine's VWMA, so the walk above was not passing on
    an empty search. The VWMA component left entry quality with the design
    (section 3.2), and no function in the engine assigns such a local now --
    indicators/indicators.py writes the VWMA column without one.

    So the walk above passes with nothing to find. That is recorded here
    rather than left to be rediscovered, and the count is asserted, so the
    next function that does assign one is looked at. What proves the check
    can still FAIL is test_the_check_catches_the_name_round_8_found below,
    which runs it against the pre-F8 function -- a control on the check
    itself, which does not depend on the engine having an offender or an
    anchor.
    """
    assigning = []
    for path, tree in _engine_trees():
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if any(isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store)
                   and "vwma" in n.id.lower() for n in ast.walk(node)):
                assigning.append(f"{os.path.basename(path)}: {node.name}")
    assert assigning == [], (
        "a function assigns a vwma-named local again. Whether that is a "
        "defect is the walk above's question; this test records that there "
        "were none at stage 4, so the first new one is read:\n  "
        + "\n  ".join(assigning))


def test_every_anchor_still_exists_in_the_engine():
    """
    An anchor is what lets a vwma-named function pass the walk above. One
    that no longer exists in the engine cannot be read by any function, so
    it is dead weight that a future offender could name to pass the check.
    Both of entry quality's anchors became dead at stage 4 and were removed
    from the set; this holds the set against the code so the next one is
    noticed.
    """
    sources = "\n".join(open(path, encoding="utf-8").read()
                         for path, _ in _engine_trees())
    for anchor in sorted(VWMA_ANCHORS):
        assert anchor in sources, (
            f"{anchor!r} is an anchor the engine no longer contains. Remove "
            f"it from VWMA_ANCHORS, or the walk above can be passed by "
            f"naming something that does not exist.")


# The function as it stood before F8, trimmed to what the check reads.
_BEFORE_F8 = '''
def _volume_sentiment_simple(self, df):
    closes = df["close"].values
    volumes = df["volume"].values
    c_recent, c_prev = closes[-5:], closes[-10:-5]
    v_recent, v_prev = volumes[-5:], volumes[-10:-5]
    vwma_recent = np.average(c_recent, weights=v_recent)
    vwma_prev = np.average(c_prev, weights=v_prev)
    vwma_slope = vwma_recent - vwma_prev
    return vwma_slope
'''


def test_the_check_catches_the_name_round_8_found():
    """The control that the check can fail: the pre-F8 names are caught."""
    found = _vwma_names_without_an_anchor(ast.parse(_BEFORE_F8))
    assert found == [("_volume_sentiment_simple",
                      ["vwma_prev", "vwma_recent", "vwma_slope"])], found


# --- 2. the momentum label -------------------------------------------------

def _panel(momentum_mode):
    from core.panel_render import render_panel

    return render_panel({
        "symbol": "TESTUSDT",
        "timeframe": "4h",
        "trend": {
            "trend_health": 62.5,
            "trend_direction": "BEARISH",
            "momentum_mode": momentum_mode,
        },
    })


# THE REDESIGN'S STAGE 5, 15 November 2026:
# test_the_momentum_label_is_printed_once_on_the_trend_line stood here. F8
# (round 8, Item 10, 11 October 2026) found momentum_mode printed twice --
# once as the MOMENTUM line's label and again after the slash on the TREND
# line -- and removed the MOMENTUM line, leaving the TREND line carrying
# both. Both lines are gone now, with trend health, momentum_mode and
# trend_direction (indicators/trend_health.py), so the label is printed
# ZERO times and a test asserting "exactly one" would pass on nothing at
# all. The test below keeps the half that can still fail: no line is headed
# MOMENTUM, which is what F8's fix actually removed, and it is checked on a
# panel built from a stale trend block carrying the label, so the line
# cannot come back unnoticed.


def test_no_line_is_headed_momentum():
    panel = _panel("STRONG")
    headed = [ln for ln in panel.splitlines()
              if ln.strip().startswith("MOMENTUM")]
    assert not headed, headed
    # Stage 5: and no line prints the label at all, from either heading.
    assert "STRONG" not in panel, [ln for ln in panel.splitlines()
                                   if "STRONG" in ln]
