"""
GATE 9, the tiers, and the two lines -- the redesign's stage 4.

WHAT IS RULED, AND BY WHOM

Ruling 4 (DECISIONS, "Decision, 25 October 2026 ...", point 4; Viktor's):
the tiers come from entry quality alone. Trend health decided them until
this stage, and both of its lines are gone.

Viktor's ruling of 11 November 2026 ("the redesign's tier lines are 70 and
50 ..."): the lines stay 70 and 50, and all three labels are kept. The
measured distribution he ruled on is in docs/redesign_entry53_draft.md,
section 4: of 539 records with a side, 92 at 70 and over, 163 between the
lines and 284 under 50.

Viktor's ruling of 7 November 2026 ("the redesign's AGGRESSIVE reads the
close inside the band"): AGGRESSIVE needs the close between EMA_20 and
EMA_50 with the ends included. It reads entry.close_inside_band, a
true-or-false field, not the STATUS word -- so a change to a panel word
cannot change an action.

Item 14's finding 5, unchanged: the risk regime gates action INTENSITY and
nothing else. tests/test_no_risk_free_conviction.py holds that half.

WHERE GATE 9 SITS, AND WHY IT MATTERS

Last. The draft's ladder runs 0, 1, 2, 3-5, 6, 7, 8, 9 and takes the label
of the FIRST gate that fails, and the reading of 11 November counted with
that order (docs/build/measure_draft_gaps.py, `ladder`). A low quality
beside a failed ADX is therefore the ADX's refusal, not gate 9's, and the
tier is derived only once every earlier gate has passed. That is why
_determine_final_action returns the bare side and no sentence written
before gate 9 names a tier.

ENTRY 58'S RULE AT THESE TWO LINES

No sentence rounds a compared value across its line. Gate 9's sentences
print the quality through core/threshold_text.py, against BOTH lines where
both are named, because 69.999 printed against 50 alone comes out "70" and
the same sentence then says it is under the 70.

The edge stage 3 filed -- a value EQUAL to a line that needs more than two
decimals prints above it -- cannot fire here: 70 and 50 have no decimals.
That is held below rather than assumed, and the edge itself is still open.

No fixtures and no pytest import outside the skips: run_tests.py calls each
test with no arguments.
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.threshold_text import compared_value_text
from models.decision_model import DecisionModel

UPPER = DecisionModel.UPPER_TIER_ENTRY_QUALITY_MIN
CONSERVATIVE = DecisionModel.CONSERVATIVE_ENTRY_QUALITY_MIN

TRIGGERED = {"trigger": True, "trigger_volume": 2.0, "trigger_volume_median": 1.0}


def _signals(side="long"):
    """A confirmed signal for `side`, as the engine computes one."""
    from models.entry_model import generate_entry_signals
    return generate_entry_signals(
        structure_regime="BULLISH TREND" if side == "long" else "BEARISH TREND",
        momentum_divergence=False, divergence_direction="NONE", adx=30.0,
        macro_bias="NEUTRAL", quote_volume=50_000.0)


def _gate9(quality, inside=False, regime="NORMAL RISK", side="LONG",
           action=None, status=None):
    """Gate 9 alone, on a side that reached it."""
    reasons = []
    if status is None:
        status = "INSIDE THE BAND" if inside else "ABOVE THE BAND"
    entry = {"score": quality, "close_inside_band": inside,
             "entry_status": status}
    out = DecisionModel()._apply_quality_gate(
        action or side, entry, {"risk_regime": regime}, reasons)
    return out, reasons


def _evaluate(quality, inside=False, regime="NORMAL RISK", raw="BULLISH",
              trigger=None, signals=None):
    """The whole of evaluate(), so the gate order is the engine's."""
    long_side = raw != "BEARISH"
    if signals is None:
        signals = _signals("long" if long_side else "short")
    entry = {"score": quality, "close_inside_band": inside,
             "entry_status": "INSIDE THE BAND" if inside else "ABOVE THE BAND",
             **signals, **(TRIGGERED if trigger is None else trigger)}
    return DecisionModel().evaluate(
        # The redesign's stage 5, 15 November 2026: `trend` was the second
        # positional parameter and is gone -- _compute_trade_quality was
        # its last reader in the decision model. The `score` this bias
        # dict carried and the `validation_state` in the risk dict are
        # gone with it: neither is a field the engine writes now.
        bias={"raw": raw},
        entry=entry,
        risk={"risk_valid": True, "risk_reason": "OK", "risk_regime": regime,
              "targets": [1.1, 1.2, 1.3] if long_side else [0.9, 0.8, 0.7]},
        degradation=None,
    )


# ============================================================
# 1. The two lines are the ruled values, and in the run hash
# ============================================================

def test_the_lines_are_70_and_50_and_both_are_fingerprinted():
    from core.decision_log import FINGERPRINTED_MODULES, module_snapshot

    assert UPPER == 70.0
    assert CONSERVATIVE == 50.0

    listed = FINGERPRINTED_MODULES["models.decision_model"]
    snap = module_snapshot()["models.decision_model"]
    for name, value in (("UPPER_TIER_ENTRY_QUALITY_MIN", 70.0),
                        ("CONSERVATIVE_ENTRY_QUALITY_MIN", 50.0)):
        key = f"DecisionModel.{name}"
        assert key in listed, (
            f"{name} decides which runs may trade and is not in the "
            f"run-hash payload")
        assert snap[key] == value


def test_nothing_else_in_the_decision_reads_a_bare_70_or_50():
    """
    The three-copies-of-one-fact defect, which this project has recorded
    more than once. _compute_trade_quality compared a bare 70 and a bare 50
    -- the same two lines, written a second time -- and now reads the
    constants. Read from the parse tree, so a comment mentioning the
    numbers is not counted.
    """
    import ast

    source = os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "models", "decision_model.py")
    with open(source, encoding="utf-8") as fh:
        tree = ast.parse(fh.read())

    offenders = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Compare):
            continue
        for operand in [node.left] + list(node.comparators):
            if (isinstance(operand, ast.Constant)
                    and operand.value in (70, 70.0, 50, 50.0)):
                offenders.append(ast.dump(node)[:120])
    assert offenders == [], (
        "a comparison in the decision model is against a bare 70 or 50. "
        "Both are tier lines with names; a second copy can move without "
        "the first:\n  " + "\n  ".join(offenders))


# ============================================================
# 2. The three tiers, at the lines and either side of them
# ============================================================

def test_the_tier_at_every_boundary_and_between_them():
    """
    The lines are inclusive at the bottom: "at or above" 70 is an upper
    tier, "at or above" 50 is CONSERVATIVE. Both ends of each band, and a
    value just under each line.
    """
    cases = [
        (0.0, "WAIT"),
        (49.99, "WAIT"),
        (CONSERVATIVE, "CONSERVATIVE LONG"),
        (50.01, "CONSERVATIVE LONG"),
        (69.99, "CONSERVATIVE LONG"),
        (UPPER, "LONG"),
        (70.01, "LONG"),
        (100.0, "LONG"),
    ]
    for quality, expected in cases:
        action, _ = _gate9(quality)
        assert action == expected, (quality, action)
        short, _ = _gate9(quality, side="SHORT")
        assert short == expected.replace("LONG", "SHORT"), (quality, short)


def test_aggressive_needs_the_quality_the_band_and_the_regime():
    """
    All three, and each one alone is not enough. The regime half is item
    14's finding 5, which tests/test_no_risk_free_conviction.py holds in
    full; it is here so that the three conditions are read together.
    """
    assert _gate9(80.0, inside=True, regime="NORMAL RISK")[0] == "AGGRESSIVE LONG"
    assert _gate9(80.0, inside=True, regime="LOW RISK")[0] == "AGGRESSIVE LONG"
    # The band alone, with the quality under the line.
    assert _gate9(60.0, inside=True)[0] == "CONSERVATIVE LONG"
    assert _gate9(40.0, inside=True)[0] == "WAIT"
    # The quality alone, with the close outside the band.
    assert _gate9(80.0, inside=False)[0] == "LONG"
    # Quality and band, in a regime that refuses the intensity.
    for regime in ("HIGH VOLATILITY RISK", "EXTREME RISK", "UNKNOWN RISK"):
        assert _gate9(80.0, inside=True, regime=regime)[0] == "LONG", regime


def test_close_inside_band_anything_but_true_is_not_inside():
    """
    Fails safe on the tier that risks the most. A record that does not
    carry the field -- one written before this stage -- cannot reach
    AGGRESSIVE on it, and nor can a truthy value of another type.
    """
    absent = object()   # the field not present at all, which is its own case
    for forged in (None, "INSIDE THE BAND", 1, "yes", [], absent):
        reasons = []
        entry = {"score": 80.0, "entry_status": "INSIDE THE BAND"}
        if forged is not absent:
            entry["close_inside_band"] = forged
        action = DecisionModel()._apply_quality_gate(
            "LONG", entry, {"risk_regime": "NORMAL RISK"}, reasons)
        assert action == "LONG", (forged, action)
        # It is the plain side, not a WAIT: the quality passed its line, so
        # the trade stands; only the intensity is withheld.
        assert reasons and reasons[0].endswith("— LONG."), (forged, reasons)

    # The control: True, and only True, reaches AGGRESSIVE.
    assert _gate9(80.0, inside=True)[0] == "AGGRESSIVE LONG"


def test_a_quality_that_was_not_measured_is_a_wait_of_its_own():
    """
    Never a quality of zero, and never the sentence of a close that was
    measured and found too far out. Zero is a real reading -- the golden
    run's is exactly that -- so the two cases must not share a sentence.
    """
    for absent in (None, float("nan"), float("inf"), "80", True, [80.0]):
        action, reasons = _gate9(absent)
        assert action == "WAIT", (absent, action)
        assert any("was not measured on this run" in r for r in reasons), absent
        assert not any("pullback to the average" in r for r in reasons), absent

    # And the control: a real zero gets the pullback sentence, not this one.
    action, reasons = _gate9(0.0)
    assert action == "WAIT"
    assert any("not at a pullback to the average" in r for r in reasons), reasons
    assert not any("was not measured" in r for r in reasons), reasons


def test_gate_9_is_silent_on_an_action_that_names_no_side():
    """
    It runs after gates 3 to 8, so most of what reaches it has already been
    refused. A refusal must not collect a tier sentence on the way out.
    """
    for action in ("WAIT", "NO-TRADE (RISK TOO HIGH)",
                   "NO-TRADE (RISK NOT ASSESSED)", "NO-TRADE (MACRO AGAINST)",
                   "NO-TRADE (THIN MARKET)", "NO-TRADE (SIGNAL UNCONFIRMED)",
                   "NO-TRADE (DEGRADED INPUT)"):
        out, reasons = _gate9(80.0, inside=True, action=action)
        assert out == action, action
        assert reasons == [], (action, reasons)


# ============================================================
# 3. The order: gate 9 is last
# ============================================================

def test_an_earlier_gate_keeps_the_label_when_the_quality_would_also_fail():
    """
    The draft's ladder takes the first gate, in order, that fails. A
    quality of 10 beside a structure that disagrees is the signal's
    refusal, not gate 9's -- which is the whole reason gate 9 runs after
    gates 3 to 8 rather than inside the ladder.
    """
    from models.entry_model import (MACRO_AGAINST, SIGNAL_UNCONFIRMED,
                                    THIN_MARKET, generate_entry_signals)

    def signals(**kw):
        base = dict(structure_regime="BULLISH TREND", momentum_divergence=False,
                    divergence_direction="NONE", adx=30.0,
                    macro_bias="NEUTRAL", quote_volume=50_000.0)
        base.update(kw)
        return generate_entry_signals(**base)

    # Gates 3 to 5, 6 and 7, each with a quality that would fail gate 9.
    for kwargs, label in (
            ({"adx": 15.0}, SIGNAL_UNCONFIRMED),
            ({"structure_regime": "BEARISH TREND"}, SIGNAL_UNCONFIRMED),
            ({"macro_bias": "BEARISH"}, MACRO_AGAINST),
            ({"quote_volume": 5.0}, THIN_MARKET)):
        out = _evaluate(10.0, signals=signals(**kwargs))
        assert out["final_action"] == label, (kwargs, out["explanation"])
        assert not any("pullback to the average" in r
                       for r in out["explanation"]["reasons"]), kwargs

    # Gate 8, likewise: no resumption candle, and a quality under the line.
    out = _evaluate(10.0, trigger={"trigger": False, "trigger_volume": 1.0,
                                   "trigger_volume_median": 2.0})
    assert out["final_action"] == "WAIT"
    assert "no resumption candle yet" in out["explanation"]["summary"]
    assert not any("pullback to the average" in r
                   for r in out["explanation"]["reasons"])

    # And the control: with every earlier gate passing, gate 9 is what
    # refuses, and its sentence is the summary.
    out = _evaluate(10.0)
    assert out["final_action"] == "WAIT"
    assert "not at a pullback to the average" in out["explanation"]["summary"]


def test_no_sentence_before_gate_9_names_a_tier():
    """
    Until this stage a refusal by gate 6, 7 or 8 read "This would have been
    CONSERVATIVE LONG" -- a tier the old ladder had chosen from trend
    health, which stage 3 filed as a claim stage 4 had to remove. The tier
    is derived after gate 9 now, so before it there is no tier to claim.
    """
    from models.entry_model import generate_entry_signals

    refused = (
        _evaluate(80.0, inside=True, signals=generate_entry_signals(
            structure_regime="BULLISH TREND", momentum_divergence=False,
            divergence_direction="NONE", adx=30.0, macro_bias="BEARISH",
            quote_volume=50_000.0)),
        _evaluate(80.0, inside=True, signals=generate_entry_signals(
            structure_regime="BULLISH TREND", momentum_divergence=False,
            divergence_direction="NONE", adx=15.0, macro_bias="NEUTRAL",
            quote_volume=50_000.0)),
        _evaluate(80.0, inside=True,
                  trigger={"trigger": False, "trigger_volume": 1.0,
                           "trigger_volume_median": 2.0}),
    )
    for out in refused:
        for reason in out["explanation"]["reasons"]:
            if reason.startswith("Entry quality is"):
                continue  # trade quality's own sentence, not a tier claim
            assert "CONSERVATIVE" not in reason and "AGGRESSIVE" not in reason, (
                out["final_action"], reason)


def test_the_tier_is_chosen_in_one_place():
    """
    Read from the parse tree: only _apply_quality_gate returns a tier. A
    second place that could return one is a second rule, which is what the
    ladder's two duplicated branches were.
    """
    import ast

    source = os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "models", "decision_model.py")
    with open(source, encoding="utf-8") as fh:
        tree = ast.parse(fh.read())

    writers = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for inner in ast.walk(node):
            if not isinstance(inner, ast.Return) or inner.value is None:
                continue
            text = ast.dump(inner.value)
            if "AGGRESSIVE" in text or "CONSERVATIVE" in text:
                writers.add(node.name)
    assert writers == {"_apply_quality_gate"}, sorted(writers)


# ============================================================
# 4. Entry 58's rule at these two lines
# ============================================================

def test_the_quality_is_printed_on_its_own_side_of_both_lines():
    """
    The reason the helper takes both lines: 69.999 printed against 50 alone
    comes out "70", beside a sentence saying it is under the 70.
    """
    from decimal import Decimal

    for quality in (49.996, 49.999, 50.0, 50.001, 50.004, 69.9, 69.99,
                    69.996, 69.999, 70.0, 70.001, 70.004, 0.0, 100.0):
        text = compared_value_text(quality, (CONSERVATIVE, UPPER))
        printed = Decimal(text)
        for line in (Decimal(repr(CONSERVATIVE)), Decimal(repr(UPPER))):
            exact = Decimal(repr(quality))
            side = (exact > line) - (exact < line)
            shown = (printed > line) - (printed < line)
            assert shown == side, (quality, text, line)


def test_the_sentence_a_reader_sees_never_contradicts_itself():
    """
    The same thing through the gate rather than the helper: the number in
    the sentence must agree with the words around it.
    """
    for quality in (49.999, 50.0, 50.001, 69.999, 70.0, 70.001):
        action, reasons = _gate9(quality)
        sentence = reasons[0]
        if action == "WAIT":
            assert f"under the {CONSERVATIVE:g} a trade needs" in sentence
            assert "50 of 100, under the 50" not in sentence, sentence
        elif action == "CONSERVATIVE LONG":
            assert f"at or above the {CONSERVATIVE:g}" in sentence
            assert f"under the {UPPER:g}" in sentence
            assert "70 of 100 —" not in sentence, (
                f"a CONSERVATIVE quality printed as the line it is under: "
                f"{sentence}")
        else:
            assert f"at or above the {UPPER:g}" in sentence


def test_a_quality_exactly_on_a_line_prints_as_that_line():
    """
    The other half of entry 58's rule: only a value that IS the line prints
    as the line. 70 and 50 have no decimals, so the edge stage 3 filed -- a
    value equal to a line needing more than two decimals prints ABOVE it --
    cannot fire at either of them. Held rather than assumed; the edge
    itself is still open, and no constant line in the engine has decimals.
    """
    assert compared_value_text(70.0, (CONSERVATIVE, UPPER)) == "70"
    assert compared_value_text(50.0, (CONSERVATIVE, UPPER)) == "50"
    assert compared_value_text(70.0, UPPER) == "70"
    assert compared_value_text(50.0, CONSERVATIVE) == "50"

    # The edge, at a line that does need more than two decimals: 100.123456
    # against itself still prints above it. This is the filed behaviour, not
    # a wish -- it is held here so that fixing it is a change this test
    # reports rather than one nothing notices.
    assert compared_value_text(100.123456, 100.123456) == "100.13"


# ============================================================
# 5. On the engine's path
# ============================================================

def test_on_the_engine_path_an_unreadable_hvn_degrades_the_run_and_waits():
    """
    The rule of 29 August, through the whole engine: a part of entry
    quality whose input cannot be read is NOT MEASURED, the run is degraded
    with the input named, and gate 9 answers WAIT rather than scoring the
    absence. Until this stage a missing HVN scored 6 of 12 -- the midpoint
    of its component -- and the run traded on the rest.
    """
    import pytest

    pytest.importorskip("pandas_ta")

    import core.engine_core as ec
    from data.data_fetcher import DataFetcher, data_fetcher
    from models.signal_router import SignalRouter

    pinned = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "fixtures", "pinned")
    original_structure = ec.calculate_structure

    def without_the_hvn(df, **kwargs):
        out = original_structure(df, **kwargs)
        frame = out.get("df")
        if frame is not None and "HVN" in frame.columns:
            out = dict(out, df=frame.drop(columns=["HVN"]))
        return out

    original_url = data_fetcher.base_url
    try:
        ec.calculate_structure = without_the_hvn
        data_fetcher.base_url = "http://127.0.0.1:1"
        DataFetcher.set_pinned_source(pinned)
        decision = SignalRouter().route(symbol="AEROUSDT", timeframe="4h")
    finally:
        ec.calculate_structure = original_structure
        DataFetcher.clear_pinned_source()
        data_fetcher.base_url = original_url

    assert "error" not in decision, decision.get("error")
    entry = decision["entry"]
    assert entry["hvn_pts"] is None, entry
    assert entry["score"] is None, (
        "entry quality was computed with one of its two parts unmeasured")
    # Stage 5, 15 November 2026: this read risk.trade_quality_proposed,
    # which was entry.score under a second name and None exactly when entry
    # quality was not measured. The field is gone -- one name for one
    # meaning -- so entry.score above is the whole of the assertion, and
    # that the duplicate has not come back is asserted here.
    assert "trade_quality_proposed" not in decision["risk"], decision["risk"]

    block = decision["degradation"]
    assert block["degraded"] is True, block
    assert any("HVN" in m for m in block["missing_inputs"]), block["missing_inputs"]
    assert block["trading_authorized"] is False

    # The distance part needs no HVN, so it is still measured: an absence is
    # confined to the part that needed the missing input.
    assert entry["distance_pts"] is not None
    assert entry["distance_atr"] is not None
    assert isinstance(entry["close_inside_band"], bool)
    assert entry["entry_status"] in ("INSIDE THE BAND", "ABOVE THE BAND",
                                    "BELOW THE BAND")

    # And the action is a WAIT or a NO-TRADE, never a side: the run cannot
    # trade on a quality nobody measured, and a degraded run cannot trade
    # at all.
    action = decision["exit"]["action"]
    assert action == "WAIT" or action.startswith("NO-TRADE"), action
