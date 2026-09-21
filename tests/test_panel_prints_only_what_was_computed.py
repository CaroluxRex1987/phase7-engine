"""
The panel prints a score only when one was computed, and names the asset it
was run on.

FOUND 21 SEPTEMBER 2026, by reading the code during the pre-backtest review
(docs/PHASE7_NEXT.md, "Review findings", items 1-3). Not seen on a live panel.

Three things the panel could print that nothing had computed:

  1. "AERO" in two sentences of the BTC section, whatever the symbol. On
     BTCUSDT the BTC context is always skipped, so every BTCUSDT run said
     "AERO analysis above is unaffected." Sequence item 12 had fixed the same
     string in decision_model.py.

  2. "nan". The router sends NaN for a value it could not measure, and the
     TREND and VALIDATION lines formatted it with ":.2f" -- "Score: nan/100".
     Decision Reasoning's "trend strength nan/100" was the same defect in
     decision_model.py.

  3. "0.00/100" for an entry, confidence, trade-quality or BTC-adjusted score
     that was absent -- a score of zero that nobody computed.

WHY THE SWEEP TEST AND NOT ONE TEST PER LINE

test_no_number_on_the_panel_prints_as_nan renders the panel with every numeric
field missing or NaN, and asserts the word "nan" appears nowhere. A test per
line would pass for every line it names and say nothing about the next line
somebody adds; this one fails for that line too. The per-line tests below it
pin the exact wording, and the negative controls pin that a real value still
prints.

Fixture-free, per run_tests.py.
"""

import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

NAN = float("nan")


def _render(decision):
    from core.panel_render import render_panel

    panel = render_panel(decision)
    assert isinstance(panel, str), "render_panel returned no panel"
    return panel


def _no_nan(panel):
    return re.search(r"\bnan\b", panel, flags=re.IGNORECASE) is None


def _line(panel, prefix):
    for line in panel.splitlines():
        if line.strip().startswith(prefix):
            return line
    raise AssertionError(f"no line starting {prefix!r} in:\n{panel}")


# --- 2 and 3: scores -------------------------------------------------------

def _everything_unmeasured(symbol="TESTUSDT"):
    return {
        "symbol": symbol,
        "timeframe": "4h",
        "bias": {"raw": "NEUTRAL", "score": NAN},
        "trend": {"trend_health": NAN},
        "structure": {"hvn": NAN, "lvn": NAN, "swing_struct": NAN},
        "entry": {"score": NAN, "zone_lower": NAN, "zone_upper": NAN,
                  "distance_from_zone": NAN},
        "risk": {"validation_score": NAN, "confidence_score": NAN,
                 "trade_quality_proposed": NAN, "atr_stop": NAN,
                 "targets": (NAN, NAN, NAN)},
        "exit": {"action": "WAIT", "current_price": NAN},
        "btc_context": {"available": True, "n_observations": 0,
                        "correlation": None, "beta": None,
                        "btc_adjusted_confidence": NAN},
    }


def test_no_number_on_the_panel_prints_as_nan():
    panel = _render(_everything_unmeasured())
    assert _no_nan(panel), (
        "the panel printed the literal text 'nan' for a value that was not "
        "measured:\n" + "\n".join(l for l in panel.splitlines()
                                   if re.search(r"\bnan\b", l, re.I)))


def test_absent_scores_print_as_absent_not_as_zero():
    panel = _render({"symbol": "TESTUSDT", "timeframe": "4h"})

    for prefix in ("TREND", "VALIDATION", "CONFIDENCE (decision)",
                   "|-- Proposed Entry", "ENTRY QUALITY"):
        line = _line(panel, prefix)
        assert "not computed" in line, line
        assert "0.00/100" not in line, line
    assert _no_nan(panel)


def test_the_btc_adjusted_score_prints_as_absent_not_as_zero():
    panel = _render(_everything_unmeasured())
    line = _line(panel, "BTC-ADJUSTED CONFIDENCE")
    assert line.startswith("BTC-ADJUSTED CONFIDENCE: not computed (vs not computed"), line


def test_a_computed_score_still_prints_with_its_scale():
    """
    Negative control. A guard that printed "not computed" for everything would
    pass every test above.
    """
    panel = _render({
        "symbol": "TESTUSDT", "timeframe": "4h",
        "trend": {"trend_health": 62.5},
        "entry": {"score": 71.25, "score_ceiling": 100.0},
        "risk": {"validation_score": 35.0, "confidence_score": 42.5,
                 "trade_quality_proposed": 58.0},
    })
    assert "(Score: 62.50/100)" in _line(panel, "TREND")
    assert "(Score: 35.00/100)" in _line(panel, "VALIDATION")
    assert _line(panel, "CONFIDENCE (decision)").endswith("42.50/100")
    assert _line(panel, "|-- Proposed Entry").endswith("58.00/100")
    assert _line(panel, "ENTRY QUALITY").endswith("71.25/100")


def test_a_real_zero_is_still_printed_as_zero():
    """
    Negative control for the other direction: 0.0 is a score, and must not be
    swallowed as though it were missing.
    """
    panel = _render({"symbol": "TESTUSDT", "timeframe": "4h",
                     "risk": {"confidence_score": 0.0}})
    assert _line(panel, "CONFIDENCE (decision)").endswith("0.00/100")


def test_decision_reasoning_says_trend_strength_was_not_computed():
    from models.decision_model import DecisionModel

    def reasons_for(trend_health):
        reasons = []
        action = DecisionModel()._determine_final_action(
            bias={"raw": "NEUTRAL", "score": 5.0},
            trend={"trend_health": trend_health, "trend_direction_sign": 1},
            entry={"score": 40.0, "entry_status": "AWAY FROM ZONE"},
            risk={"risk_valid": True, "risk_regime": "NORMAL RISK",
                  "validation_state": "NEUTRAL"},
            macro_bias="NEUTRAL",
            reasons=reasons,
        )
        assert action == "WAIT", action
        return " ".join(reasons)

    unmeasured = reasons_for(NAN)
    assert "trend strength not computed (up)" in unmeasured, unmeasured
    assert not re.search(r"\bnan\b", unmeasured, re.I), unmeasured

    # Negative control: a measured value is still printed as a number.
    measured = reasons_for(62.0)
    assert "trend strength 62/100 (up)" in measured, measured


# --- 1: the asset's name ---------------------------------------------------

def test_the_btc_section_names_the_asset_the_run_was_made_on():
    unavailable = _render({"symbol": "SOLUSDT", "timeframe": "4h"})
    assert "SOL analysis above is unaffected" in unavailable
    assert "AERO" not in unavailable

    unmeasured = _render(_everything_unmeasured("SOLUSDT"))
    assert "SOL and BTC could not be paired" in unmeasured
    assert "AERO" not in unmeasured


def test_a_btcusdt_run_does_not_mention_aero():
    """The path every BTCUSDT run takes: engine_core skips the BTC context."""
    panel = _render({"symbol": "BTCUSDT", "timeframe": "4h"})
    assert "BTC analysis above is unaffected" in panel
    assert "AERO" not in panel


def test_an_aero_run_still_says_aero():
    """Negative control: the fix names the run's asset, it does not drop it."""
    panel = _render({"symbol": "AEROUSDT", "timeframe": "4h"})
    assert "AERO analysis above is unaffected" in panel


def test_asset_name_strips_the_quote_currency_longest_first():
    from models.decision_model import asset_name

    assert asset_name("AEROUSDT") == "AERO"
    assert asset_name("solusdc") == "SOL"
    assert asset_name("BTCUSD") == "BTC"
    # The inline version tried "USD" before "BUSD", so this read "ETHB".
    assert asset_name("ETHBUSD") == "ETH"
    # Nothing left to call an asset: returned whole rather than as "".
    assert asset_name("USDT") == "USDT"
    assert asset_name("UNKNOWN") == "UNKNOWN"


def test_the_panel_and_the_reasoning_use_one_function():
    """
    Two copies of the suffix list is how the panel came to say AERO after the
    reasoning stopped. Read from the parse tree, not the source text (rule 16).
    """
    import ast

    import core.panel_render as panel_render
    import models.decision_model as decision_model

    def calls_asset_name(module):
        tree = ast.parse(open(module.__file__, "rb").read().decode("utf-8"))
        return any(isinstance(n, ast.Call)
                   and getattr(n.func, "id", None) == "asset_name"
                   for n in ast.walk(tree))

    def spells_the_suffixes(module):
        tree = ast.parse(open(module.__file__, "rb").read().decode("utf-8"))
        return [n.lineno for n in ast.walk(tree)
                if isinstance(n, ast.Tuple)
                and any(isinstance(e, ast.Constant) and e.value == "USDT"
                        for e in n.elts)]

    assert calls_asset_name(panel_render)
    assert calls_asset_name(decision_model)
    assert spells_the_suffixes(panel_render) == [], (
        "panel_render carries its own quote-currency list again")
    assert len(spells_the_suffixes(decision_model)) == 1
