"""
B10 -- two outputs agree with finding 4 and the action.

The self-review of 5 October 2026 (outside the repository; B10, Minor) named
two outputs that contradicted finding 4 or the action:

1. The simulated order (live_trading.py) recorded the band between the two
   EMAs as "entry_zone" and had no field called the entry. Finding 4
   (27 September) ruled that the plan's single entry is the close of the
   decision candle and the band a reference; the panel labels it EMA BAND,
   "a reference, not the entry".
2. On a WAIT run, Exit Watch still advised "If you're already in this
   trade ... moving your stop to breakeven once price reaches Target 1",
   naming the target of a plan the engine did not suggest.

Viktor's ruling, 15 October 2026, by agreeing to Claude's suggestions
(DECISIONS, "Ruling, 15 October 2026 -- B10: two outputs agree with finding 4
and the action"):

1. The order's key is "ema_band", the panel's label; its values are the same.
   The order's entry stays "current_price", the name the decision log gives
   the decision close (exit.current_price) -- not renamed, and not copied
   under a second name.
2. The panel prints the note only on a run whose action names a side (LONG
   or SHORT), the test decision_model makes of its own action. WAIT, every
   NO-TRADE and an absent action withhold it. Panel only, as for finding 5:
   the decision object and the log keep the note, and under a leaning bias
   the plan's stop and targets still print.

WHAT THESE TESTS HOLD
1. Every action models/decision_model.py writes is a side, WAIT or a
   NO-TRADE, and no WAIT or NO-TRADE names a side -- the premise the panel's
   rule rests on.
2. No action that names no side prints the note, under either leaning bias;
   the other Exit Watch flags still print, and with the note alone the
   section says no flag is active.
3. An absent action (the DECISION line reads UNKNOWN) prints no note.
4. On the golden decision object the real note prints as built (CONSERVATIVE
   LONG) and is withheld when its action is WAIT, while the object keeps it.
5. Negative controls: every action that names a side prints the note under
   its side's bias; a WAIT under a leaning bias still prints the plan's stop,
   its three targets and the decision close as the plan's entry; rendering
   leaves the decision object as it was.
6. The order records the band as "ema_band", and no key in it is called an
   entry; built from the golden decision object, it carries that decision's
   band and decision close.
7. Negative control: the order's current_price is the decision close.

Fixture-free, per run_tests.py. The order tests need pandas_ta (live_trading
imports the router, which imports the engine) and skip without it; the panel
tests do not.
"""

import ast
import copy
import json
import os
import re

import pytest

from core.panel_render import render_panel
from models.exit_model import TARGET1_NOTE_PREFIX

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GOLDEN = os.path.join(REPO, "tests", "fixtures", "golden_decision.json")

HVN_NOTE = ("Price is close to a high-volume node ($0.8010) -- a level where "
            "price has often reacted before.")

SIDES = {"LONG", "SHORT", "AGGRESSIVE LONG", "AGGRESSIVE SHORT",
         "CONSERVATIVE LONG", "CONSERVATIVE SHORT"}
ACTION_SHAPE = re.compile(
    r"^(WAIT|NO-TRADE( \([A-Z ]+\))?|((AGGRESSIVE|CONSERVATIVE) )?(LONG|SHORT))$")


def _actions_decision_model_writes():
    """Every string literal in models/decision_model.py shaped like an action."""
    with open(os.path.join(REPO, "models", "decision_model.py"),
              encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    return {node.value for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
            and ACTION_SHAPE.match(node.value)}


def _t1_note(t1):
    return (f"{TARGET1_NOTE_PREFIX}, a common approach is moving your stop to "
            f"breakeven once price reaches Target 1 (${t1:.4f}).")


def _decision(raw="BULLISH", action="WAIT", exit_watch=None):
    """A decision shaped as the router builds it, with a plan for its side."""
    if raw == "BEARISH":
        score, stop, targets = -55.0, 0.88, (0.75, 0.70, 0.65)
    else:
        score, stop, targets = 55.0, 0.72, (0.85, 0.90, 0.95)
    exit_data = {"current_price": 0.80}
    if action is not None:
        exit_data["action"] = action
    if exit_watch is None:
        exit_watch = [HVN_NOTE, _t1_note(targets[0])]
    return {
        "symbol": "TESTUSDT", "timeframe": "4h",
        "bias": {"raw": raw, "detailed": raw, "score": score},
        "risk": {"atr_stop": stop, "targets": targets},
        "exit": exit_data,
        "exit_watch": list(exit_watch),
    }


def _lines(panel, prefix):
    return [ln for ln in panel.splitlines() if ln.lstrip().startswith(prefix)]


def _exit_watch_section(panel):
    start = panel.index("Exit Watch (advisory only")
    end = panel.index("Validation Notes:")
    return panel[start:end]


def _golden():
    with open(GOLDEN, encoding="utf-8") as fh:
        return json.load(fh)


# ============================================================
# 1. The premise
# ============================================================

def test_every_action_the_decision_model_writes_is_a_side_wait_or_a_no_trade():
    """
    The panel tells a trade by whether the action names a side. That is
    right only while no action that is not a trade names one. Read from the
    parse tree of models/decision_model.py, the one source of the action (the
    router records final_action as it gets it). An action of some other shape
    would not be seen here; the set is written out so that a new action of
    any of these shapes fails until someone has looked at it.
    """
    actions = _actions_decision_model_writes()
    no_side = sorted(a for a in actions if a not in SIDES)

    assert SIDES <= actions, sorted(SIDES - actions)
    assert all(a == "WAIT" or a.startswith("NO-TRADE") for a in no_side), no_side
    assert [a for a in no_side if "LONG" in a or "SHORT" in a] == [], no_side
    assert actions == SIDES | {
        "WAIT", "NO-TRADE",
        "NO-TRADE (DEGRADED INPUT)", "NO-TRADE (PLAN CONTRADICTS ACTION)",
        "NO-TRADE (RISK NOT ASSESSED)", "NO-TRADE (RISK TOO HIGH)",
        "NO-TRADE (SIGNAL UNCONFIRMED)",
    }, sorted(actions)


# ============================================================
# 2-4. No trade, no note
# ============================================================

def test_no_action_that_names_no_side_prints_the_target_1_note():
    no_side = sorted(a for a in _actions_decision_model_writes() if a not in SIDES)
    assert "WAIT" in no_side and len(no_side) == 7, no_side

    for raw in ("BULLISH", "BEARISH"):
        for action in no_side:
            section = _exit_watch_section(render_panel(_decision(raw, action)))
            assert TARGET1_NOTE_PREFIX not in section, (raw, action, section)
            assert "Target 1" not in section, (raw, action, section)
            assert "high-volume node" in section, (raw, action, section)

    alone = _decision("BULLISH", "WAIT", exit_watch=[_t1_note(0.85)])
    section = _exit_watch_section(render_panel(alone))
    assert "No exit-watch flags are active right now." in section, section


def test_an_absent_action_prints_no_target_1_note():
    panel = render_panel(_decision("BULLISH", action=None))
    decision_line = _lines(panel, "DECISION      :")
    assert len(decision_line) == 1 and "UNKNOWN" in decision_line[0], decision_line
    section = _exit_watch_section(panel)
    assert TARGET1_NOTE_PREFIX not in section, section
    assert "high-volume node" in section, section


def test_on_the_golden_decision_the_note_prints_on_its_trade_and_not_on_a_wait():
    decision = _golden()
    assert decision["exit"]["action"] == "CONSERVATIVE LONG", decision["exit"]
    notes = [f for f in decision["exit_watch"] if f.startswith(TARGET1_NOTE_PREFIX)]
    assert len(notes) == 1, decision["exit_watch"]

    as_built = _exit_watch_section(render_panel(copy.deepcopy(decision)))
    assert TARGET1_NOTE_PREFIX in as_built, as_built

    waiting = copy.deepcopy(decision)
    waiting["exit"]["action"] = "WAIT"
    section = _exit_watch_section(render_panel(waiting))
    assert TARGET1_NOTE_PREFIX not in section, section
    assert waiting["exit_watch"] == decision["exit_watch"], waiting["exit_watch"]


# ============================================================
# 5. Negative controls
# ============================================================

def test_negative_control_every_action_that_names_a_side_prints_the_note():
    for action in sorted(SIDES):
        raw = "BULLISH" if "LONG" in action else "BEARISH"
        section = _exit_watch_section(render_panel(_decision(raw, action)))
        assert TARGET1_NOTE_PREFIX in section, (action, section)
        assert "high-volume node" in section, (action, section)


def test_negative_control_a_wait_under_a_leaning_bias_still_prints_the_plan():
    for raw, stop in (("BULLISH", "$0.7200"), ("BEARISH", "$0.8800")):
        panel = render_panel(_decision(raw, "WAIT"))
        assert _lines(panel, "PLAN") == [], (raw, _lines(panel, "PLAN"))
        stop_line = _lines(panel, "STOP LOSS")
        assert len(stop_line) == 1 and stop in stop_line[0], (raw, stop_line)
        assert len(_lines(panel, "TARGET")) == 3, (raw, _lines(panel, "TARGET"))
        assert "the plan's entry" in _lines(panel, "DECISION CLOSE")[0], raw


def test_negative_control_rendering_leaves_the_decision_object_as_it_was():
    decision = _decision("BULLISH", "WAIT")
    before = copy.deepcopy(decision)
    render_panel(decision)
    assert decision == before, "rendering changed the decision object"
    assert decision["exit_watch"][1].startswith(TARGET1_NOTE_PREFIX)


# ============================================================
# 6-7. The simulated order
# ============================================================

def _build_order(result):
    pytest.importorskip("pandas_ta")
    from live_trading import LiveTradingSimulator

    # _build_simulated_order reads nothing from self; called unbound so the
    # test does not construct a SignalRouter it does not need.
    return LiveTradingSimulator._build_simulated_order(None, result)


def _keys(obj):
    if isinstance(obj, dict):
        for key, value in obj.items():
            yield key
            yield from _keys(value)


def test_the_order_records_the_band_as_the_ema_band_and_calls_nothing_the_entry():
    order = _build_order({
        "symbol": "TESTUSDT", "timeframe": "4h",
        "entry": {"zone_lower": 0.61, "zone_upper": 0.64},
        "exit": {"action": "LONG", "current_price": 0.67},
    })
    assert "entry_zone" not in order, order
    assert order["ema_band"] == {"lower": 0.61, "upper": 0.64}, order
    called_entry = [k for k in _keys(order) if "entry" in str(k).lower()]
    assert called_entry == [], (
        "a key in the simulated order calls something the entry; the plan's "
        "entry is current_price, the decision close (finding 4)", called_entry)


def test_built_from_the_golden_decision_the_order_carries_its_band_and_close():
    decision = _golden()
    order = _build_order(decision)
    assert order["ema_band"] == {"lower": decision["entry"]["zone_lower"],
                                 "upper": decision["entry"]["zone_upper"]}, order
    assert order["current_price"] == decision["exit"]["current_price"], order
    assert order["decision"] == "CONSERVATIVE LONG", order
    json.dumps(order)   # still writable as the file it is


def test_negative_control_the_orders_entry_is_the_decision_close():
    order = _build_order({"symbol": "TESTUSDT", "timeframe": "4h",
                          "exit": {"action": "WAIT", "current_price": 0.67}})
    assert order["current_price"] == 0.67, order
    assert order["decision"] == "WAIT", order
