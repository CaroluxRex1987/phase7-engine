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
     that was absent -- a score of zero that nobody computed. (The
     BTC-adjusted score left the panel with N5, 9 October 2026.)

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
                        "correlation": None, "beta": None},
    }


def test_no_number_on_the_panel_prints_as_nan():
    panel = _render(_everything_unmeasured())
    assert _no_nan(panel), (
        "the panel printed the literal text 'nan' for a value that was not "
        "measured:\n" + "\n".join(l for l in panel.splitlines()
                                   if re.search(r"\bnan\b", l, re.I)))


def test_absent_scores_print_as_absent_not_as_zero():
    """
    The panel's own default for a score its decision does not carry.

    20 OCTOBER 2026 (round 8, run 2, Part 4, shape 4; the list for after the
    audit, entry 37). Part 4 is right that the router never builds this: it
    writes all five keys on every decision, and NaN for a trend health, entry
    or validation score it could not read, which
    test_no_number_on_the_panel_prints_as_nan renders. And the
    engine's two default responses -- trend_health's, which a run without
    both slope columns reaches, and entry_model's -- return a finite 0.0,
    which the panel prints as 0.00/100, since it cannot tell that zero from a
    computed one (test_a_real_zero_is_still_printed_as_zero). Forced through
    the router on the pinned set, in the Linux sandbox, TREND read "(Score:
    0.00/100)", and ENTRY QUALITY and Proposed Entry "0.00/100". That zero is
    to be fixed where it is made, by the list's entry 24 (round 8's Part 7
    reply, section 1(3)), and its test comes with that fix: written now, it
    would fail. What this test holds is the panel's half.
    """
    panel = _render({"symbol": "TESTUSDT", "timeframe": "4h"})

    # THE REDESIGN'S STAGE 5, 15 November 2026: four of the five prefixes
    # are gone with their lines -- TREND, VALIDATION, CONFIDENCE (decision)
    # and |-- Proposed Entry. ENTRY QUALITY is the panel's one remaining
    # score line, and it is the one this rule now rests on. The rule itself
    # is unchanged, and so is where it is enforced: every score line prints
    # through _score_text (core/panel_render.py), which is the single
    # function the 21 September work order introduced so the next line added
    # could not forget its scale.
    line = _line(panel, "ENTRY QUALITY")
    assert "not computed" in line, line
    assert "0.00/100" not in line, line
    assert _no_nan(panel)


# N5, 9 October 2026: test_the_btc_adjusted_score_prints_as_absent_not_as_zero
# stood here. The BTC-ADJUSTED CONFIDENCE line is gone (Viktor's ruling of
# 5 October, point 7: Bitcoin is reference only), so there is no score left
# to print as absent; tests/test_btc_is_reference_only.py checks that the
# line does not come back.


def test_a_computed_score_still_prints_with_its_scale():
    """
    Negative control. A guard that printed "not computed" for everything would
    pass every test above.

    Stage 5, 15 November 2026: four of the five scores asserted here have
    left the decision object, so the control is the one score the panel
    still prints. The second half is this stage's own guard -- the four
    removed LINES must stay removed, which a negative assertion on an absent
    key could never show on its own.
    """
    panel = _render({
        "symbol": "TESTUSDT", "timeframe": "4h",
        "entry": {"score": 71.25},
    })
    assert _line(panel, "ENTRY QUALITY").endswith("71.25/100")


def test_the_lines_stage_5_removed_stay_removed():
    """
    THE REDESIGN'S STAGE 5, 15 November 2026. Four score lines and one
    section left the panel with the readings behind them, and a stale
    decision object carrying those readings -- a record written before this
    stage, or a hand-built one -- must not bring any of them back.

    The MACRO NOTE line is the positive half: one sentence survives the
    Validation Notes section, printed beside the macro reading it is about
    (the draft's section 4).
    """
    stale = {
        "symbol": "TESTUSDT", "timeframe": "4h",
        "macro_bias": "BULLISH",
        "macro_note": "The higher timeframe agrees with this bias.",
        "trend": {"trend_health": 62.5, "momentum_mode": "STRONG",
                  "trend_direction": "BULLISH", "exhaustion": False},
        "entry": {"score": 71.25},
        "risk": {"validation_score": 35.0, "validation_state": "WEAK",
                 "validation_note": "a note from before stage 5",
                 "confidence_score": 42.5, "trade_quality_proposed": 58.0,
                 "ev_r": 1.31, "assumed_win_rate": 42.5, "avg_reward_r": 2.0},
    }
    panel = _render(stale)

    present = [ln.strip() for ln in panel.splitlines()]
    for prefix in ("TREND      :", "VALIDATION :", "CONFIDENCE (decision)",
                   "TRADE QUALITY", "|-- Proposed Entry", "Validation Notes:"):
        assert not any(ln.startswith(prefix) for ln in present), prefix

    for printed in ("62.50", "35.00", "42.50", "58.00", "WEAK",
                    "a note from before stage 5"):
        assert printed not in panel, printed

    note_line = _line(panel, "MACRO NOTE :")
    assert "The higher timeframe agrees with this bias." in note_line, note_line
    assert _line(panel, "ENTRY QUALITY").endswith("71.25/100")


def test_a_real_zero_is_still_printed_as_zero():
    """
    Negative control for the other direction: 0.0 is a score, and must not be
    swallowed as though it were missing.
    """

    # Stage 5, 15 November 2026: this was asserted on CONFIDENCE (decision),
    # whose score is gone. Entry quality is the panel's remaining score, and
    # a zero there is a real reading -- the golden run's own entry quality is
    # exactly 0.0 (D = 0 at 3.2070 ATR, H = 0 at 15.1202 ATR), which is the
    # sharpest case this control can have.
    panel = _render({"symbol": "TESTUSDT", "timeframe": "4h",
                     "entry": {"score": 0.0}})
    assert _line(panel, "ENTRY QUALITY").endswith("0.00/100")


# THE REDESIGN'S STAGE 4, 15 November 2026:
# test_decision_reasoning_says_trend_strength_was_not_computed stood here.
# Work order B wrote it on 21 September because trend_health is NaN when it
# was not measured and ":.0f" printed that as "trend strength nan/100" in
# Decision Reasoning; the fix printed "not computed" instead. The ladder
# does not quote trend strength at all now -- the tier comes from entry
# quality (ruling 4, 25 October 2026), and trend_note went with it -- so
# there is no sentence left for a NaN to reach. The panel's own TREND line
# still prints the number through _score_text, which is what
# test_absent_scores_print_as_absent_not_as_zero below holds, over
# trend_health among the rest.


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

    N5, 9 October 2026: the reasoning half is gone -- the BTC-adjusted
    confidence's sentence was asset_name()'s other caller -- so this no
    longer asserts that decision_model calls it. The one list stays where it
    is, and the panel still calls the function rather than carrying a copy.
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
    assert spells_the_suffixes(panel_render) == [], (
        "panel_render carries its own quote-currency list again")
    assert len(spells_the_suffixes(decision_model)) == 1
