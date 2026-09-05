"""
The entry sub-scores did not add up to the printed total — 5 September 2026.

    ENTRY QUALITY : 45.18/100
        |-- EMA Zone Position : 10/30
        |-- ATR Distance      : 5/25
        |-- VWMA Distance     : 10/20
        |-- RSI Extension     : 10/15
        |-- Structure         : 4/12

39 printed under a total of 45.18. Found by running the engine, recorded as
"not wrong, unexplained" — which for a number an operator is meant to act on
is its own defect.

Three things made up the gap, and none of them appeared anywhere:

  1. The sub-scores were returned as int() and int(round()) while the total
     was computed from the unrounded values. ATR distance was 5.0297.
  2. Three confluence multipliers (macro, trend, structure) are applied AFTER
     the sum, each 0.90, 1.00 or 1.05.
  3. The result is clipped to 100 — and the five components add to 102 before
     any multiplier, so a strong setup with full confluence reaches
     102 x 1.05^3 = 118.08 and loses the difference silently.

The docstring said "Max points: 100" directly above five components adding to
102, and the panel wrote /30 /25 /20 /15 /12 as literals of its own. Three
copies of one fact.
"""

import math
import os

import pandas as pd
import pytest

from conftest import REPO_ROOT

PINNED_DIR = os.path.join(REPO_ROOT, "tests", "fixtures", "pinned")
UNREACHABLE = "http://127.0.0.1:9"

SUBSCORES = ("ema_pos_pts", "atr_dist_pts", "vwma_pts", "rsi_pts", "struct_pts")


def _executable_source(path):
    """
    Source with comments and docstrings removed.

    The first draft of the denominator check looked for '"/30' — the literal
    preceded by a quote — which the old code never contained, because the
    denominators sat inside f-strings. It passed against pre-fix source and
    proved nothing. Stripping docstrings is what makes a plain substring
    check safe here: the helper's own docstring shows an example panel.
    """
    import ast
    import io

    with io.open(path, encoding="utf-8", newline="") as f:
        source = f.read()

    tree = ast.parse(source)
    docstrings = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                             ast.AsyncFunctionDef)):
            body = getattr(node, "body", None)
            if (body and isinstance(body[0], ast.Expr)
                    and isinstance(body[0].value, ast.Constant)
                    and isinstance(body[0].value.value, str)):
                docstrings.add(id(body[0].value))

    lines = source.splitlines()
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and id(node) in docstrings:
            for i in range(node.lineno - 1, node.end_lineno):
                lines[i] = ""

    return "\n".join(l.split("#", 1)[0] for l in lines)


def _frame(close=1.0, rows=60, **cols):
    data = {"close": [close] * rows}
    data.update({k: [v] * rows for k, v in cols.items()})
    return pd.DataFrame(data)


def _run_pinned():
    from data.data_fetcher import DataFetcher, data_fetcher
    from models.signal_router import SignalRouter

    original = data_fetcher.base_url
    try:
        data_fetcher.base_url = UNREACHABLE
        DataFetcher.set_pinned_source(PINNED_DIR)
        return SignalRouter().route(symbol="AEROUSDT", timeframe="4h")
    finally:
        DataFetcher.clear_pinned_source()
        data_fetcher.base_url = original


# ============================================================
# The scale is 102, and it is declared once
# ============================================================

def test_the_component_maximum_is_the_sum_of_the_components():
    from models.entry_model import (ATR_DISTANCE_MAX_POINTS,
                                    COMPONENT_MAX_POINTS,
                                    EMA_ZONE_MAX_POINTS, RSI_MAX_POINTS,
                                    STRUCTURE_MAX_POINTS, VWMA_MAX_POINTS)

    parts = [EMA_ZONE_MAX_POINTS, ATR_DISTANCE_MAX_POINTS, VWMA_MAX_POINTS,
             RSI_MAX_POINTS, STRUCTURE_MAX_POINTS]

    assert COMPONENT_MAX_POINTS == sum(parts) == 102.0, (
        f"COMPONENT_MAX_POINTS is {COMPONENT_MAX_POINTS} against components "
        f"summing to {sum(parts)}. The docstring said 100 for as long as this "
        f"function has existed."
    )


def test_the_panel_does_not_keep_its_own_copy_of_the_denominators():
    """
    /30 /25 /20 /15 /12 were literals in panel_render. A second declaration
    of a fact agrees with the first only until someone edits one of them.
    """
    code = _executable_source(os.path.join(REPO_ROOT, "core", "panel_render.py"))

    offenders = [d for d in ("/30", "/25", "/20", "/15", "/12") if d in code]

    assert not offenders, (
        "panel_render.py writes the denominators " + ", ".join(offenders)
        + " as literals again. Read them from entry_model's constants, which "
          "are wired to the bands that award the points — otherwise this file "
          "holds a second copy of a fact and agrees with the first only until "
          "someone edits one of them."
    )


def test_each_component_can_actually_reach_its_stated_maximum():
    """
    A denominator is a claim about the numerator's range. Each of the five is
    driven to its top band and checked against the constant the panel prints.
    """
    from models.entry_model import (calculate_entry_quality,
                                    EMA_ZONE_MAX_POINTS, RSI_MAX_POINTS,
                                    STRUCTURE_MAX_POINTS, VWMA_MAX_POINTS)

    out = calculate_entry_quality(
        _frame(close=1.0, VWMA=1.0, RSI=50.0, HVN=1.0, ATR=1000.0),
        0.9, 1.1)

    assert out["ema_pos_pts"] == EMA_ZONE_MAX_POINTS
    assert out["vwma_pts"] == VWMA_MAX_POINTS
    assert out["rsi_pts"] == RSI_MAX_POINTS
    assert out["struct_pts"] == STRUCTURE_MAX_POINTS


# ============================================================
# The arithmetic reconciles
# ============================================================

def test_the_sub_scores_sum_to_the_subtotal_exactly():
    """
    The defect itself. They were rounded for return, so they could not.
    """
    from models.entry_model import calculate_entry_quality

    out = calculate_entry_quality(
        _frame(close=1.05, VWMA=1.02, RSI=44.0, HVN=1.04, ATR=0.03),
        0.9, 1.1)

    total = sum(out[k] for k in SUBSCORES)

    assert total == pytest.approx(out["base_score"], abs=1e-12), (
        f"the five sub-scores sum to {total} against a base_score of "
        f"{out['base_score']}. They were returned as int() and int(round()) "
        f"while base_score was computed from the unrounded values."
    )


def test_the_subtotal_times_the_multiplier_is_the_score():
    from models.entry_model import calculate_entry_quality

    out = calculate_entry_quality(
        _frame(close=1.05, VWMA=1.02, RSI=44.0, HVN=1.04, ATR=0.03),
        0.9, 1.1, macro_bias="BULLISH", trade_direction="LONG",
        trend_direction="BULLISH",
        structure_sequence="BOS BULLISH (TREND CONTINUATION)")

    assert out["combined_multiplier"] == pytest.approx(
        out["macro_multiplier"] * out["trend_multiplier"]
        * out["structure_multiplier"], abs=1e-12)
    assert out["scaled_score"] == pytest.approx(
        out["base_score"] * out["combined_multiplier"], abs=1e-12)
    assert out["score"] == pytest.approx(
        min(out["score_ceiling"], max(0.0, out["scaled_score"])), abs=1e-12)


def test_the_multipliers_reported_are_the_multipliers_applied():
    """
    All three at 1.05 is the case that produced the original 39-under-45.18,
    so it is the case checked.
    """
    from models.entry_model import calculate_entry_quality

    out = calculate_entry_quality(
        _frame(close=1.05, VWMA=1.02, RSI=44.0, HVN=1.04, ATR=0.03),
        0.9, 1.1, macro_bias="BULLISH", trade_direction="LONG",
        trend_direction="BULLISH",
        structure_sequence="BOS BULLISH (TREND CONTINUATION)")

    assert out["macro_multiplier"] == 1.05
    assert out["trend_multiplier"] == 1.05
    assert out["structure_multiplier"] == 1.05
    assert out["combined_multiplier"] == pytest.approx(1.157625)


def test_the_clip_is_declared_when_it_fires():
    """
    102 x 1.05^3 = 118.08. The ceiling is not decorative and was invisible.
    """
    from models.entry_model import calculate_entry_quality

    out = calculate_entry_quality(
        _frame(close=1.0, VWMA=1.0, RSI=50.0, HVN=1.0, ATR=1000.0),
        0.9, 1.1, macro_bias="BULLISH", trade_direction="LONG",
        trend_direction="BULLISH",
        structure_sequence="BOS BULLISH (TREND CONTINUATION)")

    assert out["scaled_score"] > out["score_ceiling"], (
        f"this fixture was meant to exceed the ceiling and scored "
        f"{out['scaled_score']}, so the test below proves nothing"
    )
    assert out["score_clipped"] is True
    assert out["score"] == out["score_ceiling"]


def test_a_score_under_the_ceiling_is_not_reported_as_clipped():
    """Negative control."""
    from models.entry_model import calculate_entry_quality

    out = calculate_entry_quality(
        _frame(close=2.0, VWMA=1.0, RSI=90.0, HVN=1.0, ATR=0.01), 0.9, 1.1)

    assert out["scaled_score"] < out["score_ceiling"]
    assert out["score_clipped"] is False


# ============================================================
# It reaches the panel
# ============================================================

def _quality_lines(panel):
    """
    The ENTRY QUALITY block only.

    The first draft matched any line containing "ENTRY QUALITY", which also
    caught the panel's title, "PHASE-7 STRUCTURAL DYNAMIC ENTRY QUALITY
    ENGINE". Rule 30: a substring assertion cannot see the shape of what it
    matched.
    """
    out, seen = [], False
    for line in panel.splitlines():
        if line.startswith("ENTRY QUALITY :"):
            seen = True
            out.append(line)
            continue
        if not seen:
            continue
        if "Proposed Entry" in line:
            break
        if line.lstrip().startswith("|--"):
            out.append(line)
    return out


def test_the_panel_shows_the_reconciliation():
    from core.panel_render import render_panel

    panel = render_panel({
        "symbol": "TESTUSDT", "timeframe": "4h",
        "entry": {
            "score": 45.18175716, "ema_pos_pts": 10.0,
            "atr_dist_pts": 5.0297006, "vwma_pts": 10.0, "rsi_pts": 10.0,
            "struct_pts": 4.0, "base_score": 39.0297006,
            "component_max_points": 102.0, "macro_multiplier": 1.05,
            "trend_multiplier": 1.05, "structure_multiplier": 1.05,
            "combined_multiplier": 1.157625, "scaled_score": 45.18175716,
            "score_ceiling": 100.0, "score_clipped": False,
            "entry_status": "APPROACHING ZONE", "distance_from_zone": 4.22,
            "zone_lower": 0.76, "zone_upper": 0.78,
        },
    })

    lines = "\n".join(_quality_lines(panel))

    assert "Subtotal" in lines and "39.03/102" in lines, (
        f"the subtotal is missing or wrong:\n{lines}"
    )
    assert "Confluence" in lines and "x1.1576" in lines, (
        f"the confluence multiplier is missing:\n{lines}"
    )
    assert "macro x1.05" in lines and "trend x1.05" in lines and \
           "structure x1.05" in lines, (
        f"the three factors are not broken out:\n{lines}"
    )
    for label, denominator in (("EMA Zone Position", "/30"),
                               ("ATR Distance", "/25"),
                               ("VWMA Distance", "/20"),
                               ("RSI Extension", "/15"),
                               ("Structure", "/12"),
                               ("Subtotal", "/102")):
        row = next((l for l in lines.splitlines()
                    if l.lstrip().startswith(f"|-- {label}")), None)
        assert row is not None, f"no {label} line:\n{lines}"
        assert row.rstrip().endswith(denominator), (
            f"{label} is printed out of the wrong maximum: {row!r}"
        )


def test_the_displayed_components_add_up_to_the_displayed_subtotal():
    """
    The point of the whole change: an operator adding the printed column
    must land on the printed subtotal.
    """
    import re

    from core.panel_render import render_panel

    pytest.importorskip("pandas_ta")

    decision = _run_pinned()
    lines = _quality_lines(render_panel(decision))

    values, subtotal = [], None
    for line in lines:
        match = re.search(r"\|--\s+(.+?)\s*:\s*([0-9.]+)/([0-9]+)", line)
        if not match:
            continue
        label, value = match.group(1).strip(), float(match.group(2))
        if label == "Subtotal":
            subtotal = value
        else:
            values.append(value)

    assert subtotal is not None, f"no Subtotal line:\n{lines}"
    assert len(values) == 5, f"expected five components, got {values}:\n{lines}"
    assert sum(values) == pytest.approx(subtotal, abs=0.011), (
        f"the printed components sum to {sum(values)} under a printed "
        f"subtotal of {subtotal}. This is the defect, one decimal place "
        f"further down."
    )


def test_the_panel_does_not_invent_a_sub_score_it_was_not_given():
    """
    The defaults were 22, 10, 20, 15 and 2 — plausible sub-scores, invented
    by the renderer, for a run that reported none.
    """
    from core.panel_render import render_panel

    panel = render_panel({"symbol": "TESTUSDT", "timeframe": "4h",
                          "entry": {"score": 0.0}})
    lines = "\n".join(_quality_lines(panel))

    assert "22" not in lines, (
        f"the panel still defaults EMA Zone Position to 22 of 30:\n{lines}"
    )
    assert lines.count("n/a") == 5, (
        f"expected all five components to read n/a:\n{lines}"
    )


# ============================================================
# It reaches the record
# ============================================================

def test_the_decision_object_carries_the_reconciliation():
    """
    signal_router rebuilds the entry block field by field, so anything it
    does not name is dropped before the panel or the log sees it. That is
    what happened to these nine on the first attempt at this fix — the lines
    simply did not appear, with no error.
    """
    pytest.importorskip("pandas_ta")

    entry = _run_pinned().get("entry", {})

    for field in ("base_score", "component_max_points", "macro_multiplier",
                  "trend_multiplier", "structure_multiplier",
                  "combined_multiplier", "scaled_score", "score_ceiling",
                  "score_clipped"):
        assert field in entry, (
            f"the decision object's entry block has no {field!r}. "
            f"models/signal_router.py rebuilds this block by name."
        )

    total = sum(float(entry[k]) for k in SUBSCORES)
    assert total == pytest.approx(float(entry["base_score"]), abs=1e-6)
    assert math.isfinite(float(entry["scaled_score"]))
