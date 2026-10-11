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
VWMA_ANCHORS = frozenset({"VWMA", "VWMA_LENGTH", "VWMA_MAX_POINTS", "vwma_pts"})


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


def test_the_check_sees_the_vwma_that_is_there():
    """
    Not vacuous: the walk reaches entry_model's VWMA scoring, which assigns
    vwma-named locals and reads the VWMA column.
    """
    seen = set()
    for path, tree in _engine_trees():
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store) \
                    and "vwma" in node.id.lower():
                seen.add(os.path.basename(path))
    assert "entry_model.py" in seen, sorted(seen)


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


def test_the_momentum_label_is_printed_once_on_the_trend_line():
    word = "EXTENDED"
    panel = _panel(word)
    lines = [ln for ln in panel.splitlines() if word in ln]
    assert len(lines) == 1, (
        f"momentum_mode is printed on {len(lines)} lines:\n" + "\n".join(lines)
    )
    assert lines[0].strip().startswith("TREND"), lines[0]


def test_no_line_is_headed_momentum():
    panel = _panel("STRONG")
    headed = [ln for ln in panel.splitlines()
              if ln.strip().startswith("MOMENTUM")]
    assert not headed, headed
