"""
Finding 5 -- a NEUTRAL bias prints no plan.

Review of 21 September 2026, finding 5: the plan's direction is the sign of
bias_score (models/risk_model.py, calculate_stop_targets, since work order C),
so a score inside +/-20 -- a NEUTRAL bias, with no direction box -- still
printed a long- or short-shaped stop, three targets and their R:R, and a score
of exactly 0 printed a long.

Viktor's ruling, 27 September 2026 (DECISIONS, "Ruling, 27 September 2026 --
a NEUTRAL bias prints no plan (finding 5)"), panel only: under a NEUTRAL bias
the panel prints no stop, targets or R:R, and one line saying there is no plan
because the bias is NEUTRAL (the score, inside +/-20), so there is no
direction to measure a stop from. The engine still computes and logs the
plan, because the risk check needs a stop.

WHAT THESE TESTS HOLD
1. Under a NEUTRAL bias: no STOP LOSS line, no TARGET line, no R:R anywhere,
   and exactly one PLAN line naming the bias, its score and the threshold
   (read from bias_engine, not written in).
2. Under a NEUTRAL bias the DECISION CLOSE line still prints the price, and
   does not call itself the plan's entry.
3. Under a NEUTRAL bias the Exit Watch note naming Target 1 is not printed;
   every other Exit Watch flag still is.
4. A NEUTRAL bias whose score was not computed says so, not "nan".
5. Negative controls: BULLISH and BEARISH print the plan exactly as before,
   and so does a raw bias the engine never emits (absent) -- the ruling is
   about NEUTRAL only.
6. The panel withholds; it does not remove. Rendering leaves the decision
   object -- which carries the plan and is what gets logged -- unchanged.
7. The claim the ruling rests on: the decision ladder never returns LONG or
   SHORT under a NEUTRAL bias, checked over a grid of inputs, with a
   negative control showing the same grid does reach a side under BULLISH
   and BEARISH.

All fixture-free, so run_tests.py runs them too.
"""

import copy
import itertools
import math

from core.panel_render import render_panel
from models.bias_engine import RAW_BIAS_THRESHOLD
from models.decision_model import DecisionModel
from models.exit_model import TARGET1_NOTE_PREFIX

NAN = float("nan")

T1_NOTE = (f"{TARGET1_NOTE_PREFIX}, a common approach is moving your stop to "
           f"breakeven once price reaches Target 1 ($0.8500).")
HVN_NOTE = ("Price is close to a high-volume node ($0.8010) -- a level where "
            "price has often reacted before.")


def _decision(raw="NEUTRAL", score=7.25, exit_watch=None, bias=None):
    if bias is None:
        bias = {"raw": raw, "detailed": raw, "score": score}
    return {
        "symbol": "TESTUSDT", "timeframe": "4h",
        "bias": bias,
        "risk": {"atr_stop": 0.72, "targets": (0.85, 0.90, 0.95)},
        "exit": {"action": "WAIT", "current_price": 0.80},
        "exit_watch": list(exit_watch) if exit_watch is not None else [T1_NOTE],
    }


def _lines(panel, prefix):
    return [ln for ln in panel.splitlines() if ln.lstrip().startswith(prefix)]


def _exit_watch_section(panel):
    start = panel.index("Exit Watch (advisory only")
    end = panel.index("Validation Notes:")
    return panel[start:end]


# ============================================================
# 1-4. Under a NEUTRAL bias
# ============================================================

def test_a_neutral_bias_prints_no_stop_no_targets_and_no_rr():
    panel = render_panel(_decision())
    assert panel is not None, "the panel failed to render"
    assert _lines(panel, "STOP LOSS") == [], _lines(panel, "STOP LOSS")
    assert _lines(panel, "TARGET") == [], _lines(panel, "TARGET")
    assert "R:R" not in panel, [ln for ln in panel.splitlines() if "R:R" in ln]
    for price in ("$0.7200", "$0.8500", "$0.9000", "$0.9500"):
        assert price not in panel, f"a plan price {price} was printed"


def test_a_neutral_bias_prints_one_line_saying_why():
    panel = render_panel(_decision(score=7.25))
    plan = _lines(panel, "PLAN")
    assert len(plan) == 1, plan
    line = plan[0]
    assert "the bias is NEUTRAL" in line, line
    assert "score +7.2" in line, line          # 7.25 to one decimal
    assert f"inside ±{RAW_BIAS_THRESHOLD:.0f}" in line, line
    assert "no direction to measure a stop from" in line, line


def test_the_plan_line_prints_a_negative_score_with_its_sign():
    line = _lines(render_panel(_decision(score=-17.8)), "PLAN")[0]
    assert "score -17.8" in line, line


def test_a_score_of_exactly_zero_prints_no_long():
    """The finding's sharpest case: 0 printed a long-shaped plan."""
    panel = render_panel(_decision(score=0.0))
    assert _lines(panel, "STOP LOSS") == []
    assert "score +0.0" in _lines(panel, "PLAN")[0]


def test_the_decision_close_is_printed_but_not_called_the_plans_entry():
    panel = render_panel(_decision())
    close = _lines(panel, "DECISION CLOSE")
    assert len(close) == 1, close
    assert "$0.8000" in close[0], close[0]
    assert "plan's entry" not in close[0], close[0]


def test_the_target_1_note_is_not_printed_but_other_flags_are():
    panel = render_panel(_decision(exit_watch=[HVN_NOTE, T1_NOTE]))
    section = _exit_watch_section(panel)
    assert "Target 1" not in section, section
    assert TARGET1_NOTE_PREFIX not in section, section
    assert "high-volume node" in section, section


def test_with_only_the_target_1_note_exit_watch_says_nothing_is_active():
    section = _exit_watch_section(render_panel(_decision(exit_watch=[T1_NOTE])))
    assert "No exit-watch flags are active right now." in section, section


def test_a_neutral_score_not_computed_says_so():
    line = _lines(render_panel(_decision(score=NAN)), "PLAN")[0]
    assert "score not computed" in line, line
    assert "nan" not in line.lower(), line


def test_on_a_real_decision_object_the_real_target_1_note_is_withheld():
    """
    The golden decision object, as the engine built it, with only its bias
    turned NEUTRAL. Its exit_watch holds the note exit_model really writes,
    so this checks the prefix against the real text, not a copy of it.
    """
    import json
    import os
    fixture = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "fixtures", "golden_decision.json")
    with open(fixture, encoding="utf-8") as fh:
        decision = json.load(fh)
    notes = [f for f in decision["exit_watch"] if "Target 1" in f]
    assert len(notes) == 1 and notes[0].startswith(TARGET1_NOTE_PREFIX), notes

    as_built = render_panel(json.loads(json.dumps(decision)))
    assert "Target 1" in _exit_watch_section(as_built)
    assert len(_lines(as_built, "STOP LOSS")) == 1

    decision["bias"]["raw"] = "NEUTRAL"
    decision["bias"]["score"] = 12.0
    panel = render_panel(decision)
    assert _lines(panel, "STOP LOSS") == [] and _lines(panel, "TARGET") == []
    assert "Target 1" not in _exit_watch_section(panel)
    assert len(_lines(panel, "PLAN")) == 1


# ============================================================
# 5. Negative controls -- a direction prints the plan as before
# ============================================================

def test_bullish_and_bearish_still_print_the_whole_plan():
    for raw in ("BULLISH", "BEARISH"):
        panel = render_panel(_decision(raw=raw, score=55.0))
        assert _lines(panel, "PLAN") == [], (raw, _lines(panel, "PLAN"))
        stop = _lines(panel, "STOP LOSS")
        targets = _lines(panel, "TARGET")
        assert len(stop) == 1 and "$0.7200" in stop[0], (raw, stop)
        assert len(targets) == 3, (raw, targets)
        assert all("R:R 1 : " in t for t in targets), (raw, targets)
        close = _lines(panel, "DECISION CLOSE")[0]
        assert "the plan's entry" in close, (raw, close)
        assert "Target 1 ($0.8500)" in _exit_watch_section(panel), raw


def test_a_raw_bias_the_engine_never_emits_prints_the_plan_as_before():
    """
    Scope, recorded: only NEUTRAL withholds the plan. An absent raw bias
    (the panel reads it as UNKNOWN) is not a reading of no lean, and the
    ruling does not cover it.
    """
    panel = render_panel(_decision(bias={}))
    assert _lines(panel, "PLAN") == []
    assert len(_lines(panel, "STOP LOSS")) == 1
    assert len(_lines(panel, "TARGET")) == 3


# ============================================================
# 6. The panel withholds; it does not remove
# ============================================================

def test_rendering_leaves_the_plan_in_the_decision_object():
    decision = _decision()
    before = copy.deepcopy(decision)
    render_panel(decision)
    assert decision == before, "rendering changed the decision object"
    assert decision["risk"]["atr_stop"] == 0.72
    assert decision["risk"]["targets"] == (0.85, 0.90, 0.95)
    assert decision["exit_watch"] == [T1_NOTE]


# ============================================================
# 7. The ladder never takes a side under a NEUTRAL bias
# ============================================================

def _grid_actions(raw):
    scores = (-RAW_BIAS_THRESHOLD, -19.9, -5.0, 0.0, 5.0, 19.9, RAW_BIAS_THRESHOLD)
    if raw == "BULLISH":
        scores = (21.0, 55.0, 100.0)
    elif raw == "BEARISH":
        scores = (-21.0, -55.0, -100.0)
    # Both plan shapes, so that _refuse_incoherent_plan can never hide a side
    # the ladder chose behind NO-TRADE (PLAN CONTRADICTS ACTION).
    plans = (
        (0.72, (0.85, 0.90, 0.95)),   # long-shaped
        (0.88, (0.75, 0.70, 0.65)),   # short-shaped
    )
    actions = set()
    calls = [0]
    model = DecisionModel()
    # Work order G, 27 September 2026: the grid had a macro dimension
    # ("BULLISH", "BEARISH", "NEUTRAL"), passed as macro_bias. evaluate() no
    # longer takes it, so the dimension is gone and the grid is a third the
    # size; no remaining input is affected.
    for ((stop, targets), score, health, entry_score, status, risk_valid, regime,
         validation, confirmed) in itertools.product(
            plans,
            scores,
            (NAN, 0.0, 49.0, 50.0, 75.0, 100.0),
            (0.0, 69.0, 70.0, 100.0),
            ("ACTIVE ENTRY ZONE", "AWAY FROM ZONE"),
            (True, False),
            ("NORMAL RISK", "HIGH VOLATILITY RISK"),
            ("STRONG", "NEUTRAL", "WEAK"),
            (True, False)):
        blockers = [] if confirmed else ["test blocker"]
        result = model.evaluate(
            bias={"raw": raw, "score": score},
            trend={"trend_health": health, "trend_direction_sign": 1},
            entry={"score": entry_score, "entry_status": status,
                   "long_signal": confirmed, "long_signal_blockers": blockers,
                   "short_signal": confirmed, "short_signal_blockers": list(blockers)},
            risk={"risk_valid": risk_valid, "risk_reason": "test",
                  "risk_regime": regime, "validation_state": validation,
                  "atr_stop": stop, "targets": targets},
        )
        actions.add(result["final_action"])
        calls[0] += 1
    return actions, calls[0]


def test_a_neutral_bias_never_reaches_long_or_short():
    """
    Stronger than "no action names a side": SIGNAL UNCONFIRMED and PLAN
    CONTRADICTS ACTION are only ever produced from an action that named one,
    so under a NEUTRAL bias neither may appear either. What is left is the
    ladder's two answers that choose no side.
    """
    actions, calls = _grid_actions("NEUTRAL")
    assert calls == 2 * 7 * 6 * 4 * 2 * 2 * 2 * 3 * 2, calls
    assert actions == {"WAIT", "NO-TRADE (RISK TOO HIGH)"}, sorted(actions)


def test_negative_control_the_same_grid_reaches_a_side_under_a_direction():
    """Without this, the test above would pass on a grid that cannot trade."""
    bullish, _ = _grid_actions("BULLISH")
    bearish, _ = _grid_actions("BEARISH")
    assert any("LONG" in a for a in bullish), sorted(bullish)
    assert any("SHORT" in a for a in bearish), sorted(bearish)
