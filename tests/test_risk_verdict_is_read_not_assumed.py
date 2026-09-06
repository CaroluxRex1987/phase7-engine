"""
GLM F-7, as extended — 6 September 2026.

THE FINDING

Round 3 (GLM 5.3 Flash) filed `risk.get("risk_valid", True)` against
`live_trading.py` and argued Minor, on the stated grounds that the module only
writes a simulated-order log. The same permissive default sat in two other
places, and the severity argument does not cover either:

    models/decision_model.py   _determine_final_action   the AUTHORIZATION GATE
    models/signal_router.py    _build_decision_object    the recorded verdict
    live_trading.py            _build_simulated_order    the one GLM filed

A risk block that is a dict but carries no `risk_valid` is a block on which
risk was never assessed. `.get("risk_valid", True)` read that state as
"assessed, and it passed" — the one direction an authorization gate must never
fail in. Nothing in the engine had to be broken for it to happen; the check
merely had to be absent.

WHY IT WAS REACHABLE AND NOT MERELY LATENT

`signal_router._validate_engine_output` checked that the key "risk" was
PRESENT as a section, and never what it contained. So an engine output whose
risk block was `{}` passed validation, satisfied `_determine_final_action`'s
`isinstance(risk, dict)` guard, and could return AGGRESSIVE LONG with no risk
assessment anywhere behind it. `_refuse_incoherent_plan` does not catch that
case either — an empty block has no targets, `_plan_direction` returns None,
and the action passes through untouched.

WHAT THE TESTS BELOW ARE FOR

The negative controls come first and are named as such. A gate that refused
everything would satisfy every refusal test here and be worthless, so the
tests that must pass BOTH before and after the fix carry as much weight as the
ones that must fail before it.
"""

import io
import os

import pytest

from conftest import REPO_ROOT

from models.decision_model import DecisionModel
from models.risk_model import read_risk_verdict


# The conviction fixture from tests/test_no_risk_free_conviction.py: a
# combination that clears every threshold _determine_final_action checks, so
# the only thing under test below is the risk verdict. Without it a refusal
# could be caused by anything and the tests would prove nothing.
HIGH_CONVICTION_TREND_HEALTH = 80.0
HIGH_CONVICTION_ENTRY_SCORE = 75.0
HIGH_CONVICTION_BIAS_SCORE = 60.0

ASSESSED_AND_PASSED = {
    "risk_valid": True,
    "risk_reason": "OK",
    "validation_state": "NEUTRAL",
    "risk_regime": "NORMAL RISK",
    # Ascending targets above the stop: a long plan, so
    # _refuse_incoherent_plan agrees with a long action rather than being the
    # thing that refuses it.
    "targets": (1.10, 1.20, 1.30),
    "atr_stop": 0.90,
}


def _risk(**overrides):
    block = dict(ASSESSED_AND_PASSED)
    block.update(overrides)
    return block


def _final_action(risk):
    reasons = []
    action = DecisionModel()._determine_final_action(
        bias={"raw": "BULLISH", "score": HIGH_CONVICTION_BIAS_SCORE},
        trend={
            "trend_health": HIGH_CONVICTION_TREND_HEALTH,
            "trend_direction_sign": 1,
            "momentum_divergence": False,
        },
        entry={
            "score": HIGH_CONVICTION_ENTRY_SCORE,
            "entry_status": "ACTIVE ENTRY ZONE",
            "long_signal": False,
            "short_signal": False,
        },
        risk=risk,
        macro_bias="NEUTRAL",
        reasons=reasons,
    )
    return action, reasons


# ============================================================
# 1. read_risk_verdict — the one place a verdict is read
# ============================================================

@pytest.mark.parametrize("block, expected", [
    ({"risk_valid": True}, True),
    ({"risk_valid": False}, False),
    ({}, None),
    ({"risk_valid": None}, None),
    ({"risk_valid": "OK"}, None),
    ({"risk_valid": "False"}, None),
    ({"risk_valid": 1}, None),
    ({"risk_valid": 0}, None),
    (None, None),
    ("not a dict", None),
    ([], None),
])
def test_a_verdict_is_returned_only_when_there_is_one(block, expected):
    """
    Absent, present-as-None, and present-as-not-a-boolean are one state: risk
    was not assessed. `1` and `"OK"` are in this table on purpose — both are
    truthy, and both would have opened the gate under the old `bool(...)` read.
    """
    assert read_risk_verdict(block) is expected


# ============================================================
# 2. The authorization gate
# ============================================================

def test_negative_control_an_assessed_pass_still_authorizes():
    """
    MUST PASS BOTH BEFORE AND AFTER THE FIX.

    Everything below asserts a refusal. If the gate had been made to refuse
    unconditionally, every one of those would pass and the engine would be
    broken. This is the test that says the gate still opens when it should.
    """
    action, reasons = _final_action(_risk())
    assert action == "AGGRESSIVE LONG", (
        f"a fully assessed, passing risk block on a high-conviction setup "
        f"should still authorize; got {action!r}.\nReasons: {reasons}"
    )


def test_an_empty_risk_block_is_refused_rather_than_read_as_a_pass():
    """
    The finding itself. Pre-fix this returned AGGRESSIVE LONG: `{}` is a dict,
    so the isinstance guard passed, and `.get("risk_valid", True)` supplied the
    authorization the engine had never computed.
    """
    action, reasons = _final_action({})
    assert action == "NO-TRADE (RISK NOT ASSESSED)", (
        f"an empty risk block means risk was never assessed; the gate must "
        f"refuse rather than default to a pass. Got {action!r}.\n"
        f"Reasons: {reasons}"
    )


def test_a_partial_risk_block_without_the_verdict_is_refused():
    """
    The realistic shape of the defect. A block with stop, targets and regime
    in it looks complete to a reader and to `_refuse_incoherent_plan`, and is
    missing the only field that says whether a trade is allowed.
    """
    partial = _risk()
    del partial["risk_valid"]
    action, reasons = _final_action(partial)
    assert action == "NO-TRADE (RISK NOT ASSESSED)", (
        f"a risk block carrying a plan but no verdict must not be treated as "
        f"a pass; got {action!r}.\nReasons: {reasons}"
    )


def test_a_verdict_present_as_none_is_refused():
    """
    Kimi Finding 1's lesson applied to this field: the dangerous shape is not
    a missing key, it is a key present with the value None. Pre-fix this
    returned NO-TRADE (RISK TOO HIGH) — the right refusal for the wrong
    reason, and it printed "Risk check failed (OK)", which is a sentence about
    a check that never ran.
    """
    action, reasons = _final_action(_risk(risk_valid=None))
    assert action == "NO-TRADE (RISK NOT ASSESSED)", (
        f"a None verdict is not a failed check, it is an absent one; "
        f"got {action!r}.\nReasons: {reasons}"
    )
    assert not any("Risk check failed" in r for r in reasons), (
        "the reasoning claims a risk check failed, on a run where no risk "
        f"check produced a verdict at all.\nReasons: {reasons}"
    )


def test_a_truthy_non_boolean_verdict_is_refused_not_believed():
    """
    The worst of the shapes, because it is silent in both directions: pre-fix
    `bool("OK")` is True, so the string "OK" in that field authorized a trade.
    """
    action, reasons = _final_action(_risk(risk_valid="OK"))
    assert action == "NO-TRADE (RISK NOT ASSESSED)", (
        f"the string 'OK' is not a verdict; got {action!r}.\n"
        f"Reasons: {reasons}"
    )


def test_negative_control_a_real_failed_check_still_says_so():
    """
    MUST PASS BOTH BEFORE AND AFTER THE FIX.

    The two states must stay distinguishable. A check that ran and failed has
    a reason to give and gives it; an absent check does not and must not
    borrow one.
    """
    action, reasons = _final_action(
        _risk(risk_valid=False, risk_reason="Stop distance too tight.")
    )
    assert action == "NO-TRADE (RISK TOO HIGH)", (
        f"an assessed failure must keep its own action string; got {action!r}"
    )
    assert any("Stop distance too tight." in r for r in reasons), (
        f"the failure's own reason must reach the operator.\nReasons: {reasons}"
    )


def test_the_two_no_trade_states_are_not_the_same_string():
    """
    An operator reading the panel has to be able to tell "we checked and it is
    too risky" from "we never checked". Collapsing them into one label would
    pass every other test in this file.
    """
    unassessed, _ = _final_action({})
    failed, _ = _final_action(_risk(risk_valid=False))
    assert unassessed != failed


# ============================================================
# 3. The validator — where malformed engine output is caught
# ============================================================

def _engine_output(risk):
    return {
        "bias": {}, "trend": {}, "structure": {}, "entry": {}, "risk": risk,
    }


def test_negative_control_a_well_formed_engine_output_is_accepted():
    """MUST PASS BOTH BEFORE AND AFTER THE FIX."""
    from models.signal_router import SignalRouter
    assert SignalRouter(engine_core=object())._validate_engine_output(
        _engine_output(_risk())
    ) is True


def test_negative_control_an_error_payload_is_still_a_valid_payload():
    """
    MUST PASS BOTH BEFORE AND AFTER THE FIX.

    The validator returns True early for an error dict — those are failure
    notices the router renders, not analyses. The new check must not sit in
    front of that and start rejecting them.
    """
    from models.signal_router import SignalRouter
    assert SignalRouter(engine_core=object())._validate_engine_output(
        {"error": "something went wrong"}
    ) is True


@pytest.mark.parametrize("risk", [
    {},
    {"atr_stop": 0.9, "targets": (1.1, 1.2, 1.3)},
    {"risk_valid": None},
    {"risk_valid": "OK"},
])
def test_an_engine_output_whose_risk_block_has_no_verdict_is_rejected(risk):
    """
    Pre-fix the validator asked only whether the key "risk" existed. That is
    what made the gate's permissive default reachable from a real run rather
    than only from a direct call.
    """
    from models.signal_router import SignalRouter
    assert SignalRouter(engine_core=object())._validate_engine_output(
        _engine_output(risk)
    ) is False


# ============================================================
# 4. End to end through the router
# ============================================================

class _StubEngine:
    """Stands in for Phase7Engine.run(), returning exactly one output."""

    def __init__(self, output):
        self.output = output

    def run(self, symbol, timeframe):
        return self.output


def _route(monkeypatch, output):
    from models import signal_router as sr
    monkeypatch.setattr(sr, "render_panel", lambda *a, **k: None)
    return sr.SignalRouter(engine_core=_StubEngine(output)).route_and_execute(
        "AEROUSDT", "4h"
    )


def test_a_run_with_no_risk_verdict_produces_an_error_not_a_decision(monkeypatch):
    """
    The whole path, not one function of it. Pre-fix this returned a decision
    object — panel rendered, decision log written — whose risk block said
    `risk_valid: True` on a run where risk was never assessed.
    """
    result = _route(monkeypatch, _engine_output({}))
    assert "error" in result, (
        f"an engine output with no risk verdict must not become a decision; "
        f"got keys {sorted(result)!r}"
    )
    assert "decision_log_path" not in result, (
        "a run refused for having no risk assessment was written to the "
        "decision log anyway"
    )


def test_negative_control_a_stubbed_well_formed_run_still_reaches_a_decision(monkeypatch):
    """
    MUST PASS BOTH BEFORE AND AFTER THE FIX.

    Without this, the test above passes whenever the router errors for any
    reason at all — including a mistake in this file's own stub.
    """
    output = _engine_output(_risk())
    output.update({
        "exit": {"current_price": 1.0},
        "degradation": [],
        "macro_bias": "NEUTRAL",
        "btc_context": {"available": False},
    })
    result = _route(monkeypatch, output)
    assert "error" not in result, (
        f"a well-formed stubbed run should still produce a decision; "
        f"got {result.get('error')!r}"
    )
    assert result["risk"]["risk_valid"] is True


def test_the_recorded_verdict_is_the_one_that_was_read_not_an_invented_pass(monkeypatch):
    """
    `_build_decision_object` called directly, past the validator. It is a
    method on a public class and the record it writes is permanent, so it must
    not invent a pass either — defence in depth rather than one guard doing
    all the work.
    """
    from models import signal_router as sr
    monkeypatch.setattr(sr, "render_panel", lambda *a, **k: None)
    decision = sr.SignalRouter(engine_core=object())._build_decision_object(
        symbol="AEROUSDT", timeframe="4h",
        bias={}, trend={}, structure={}, entry={}, risk={},
        exit_data={"current_price": 1.0},
        degradation=[], provenance={}, lineage_record={}, exit_watch=[],
        btc_context={"available": False}, macro_bias="NEUTRAL",
        chart_path=None,
    )
    assert decision["risk"]["risk_valid"] is None, (
        f"the decision log's permanent record of a run with no risk "
        f"assessment says {decision['risk']['risk_valid']!r}"
    )
    assert decision["exit"]["action"] == "NO-TRADE (RISK NOT ASSESSED)"


# ============================================================
# 5. The simulated order — the site GLM actually filed
# ============================================================

def _simulator(tmp_path):
    """
    Constructing LiveTradingSimulator builds a SignalRouter, whose __init__
    imports core.engine_core, which needs pandas_ta — the same reason
    tests/test_fetch_and_import_hygiene.py guards its own constructor call.
    Importing the module does not.
    """
    pytest.importorskip("pandas_ta",
                        reason="LiveTradingSimulator() constructs a "
                               "SignalRouter, which imports engine_core")
    import live_trading
    return live_trading.LiveTradingSimulator(log_dir=str(tmp_path / "sim"))


def test_the_simulated_order_records_no_verdict_rather_than_a_pass(tmp_path):
    """
    GLM's own finding. `run_once` returns early on an error result, which is
    why this was latent; `_build_simulated_order` is not private and is called
    directly by the suite, so latent is not safe.
    """
    order = _simulator(tmp_path)._build_simulated_order(
        {"symbol": "AEROUSDT", "timeframe": "4h"}
    )
    assert order["risk"]["risk_valid"] is None, (
        f"a simulated order built from a result with no risk block records "
        f"{order['risk']['risk_valid']!r} for the risk check"
    )


def test_negative_control_the_simulated_order_still_carries_a_real_verdict(tmp_path):
    """MUST PASS BOTH BEFORE AND AFTER THE FIX."""
    order = _simulator(tmp_path)._build_simulated_order(
        {"symbol": "AEROUSDT", "timeframe": "4h", "risk": _risk()}
    )
    assert order["risk"]["risk_valid"] is True


# ============================================================
# 6. The default cannot come back
# ============================================================

# Forward slashes deliberately, not os.path.join: these strings become the
# parametrized test ids, and a join would print them with backslashes on
# Viktor's Windows machine and forward slashes in a Linux verification run --
# two different-looking suite outputs for one identical test. Python's file
# APIs take forward slashes on Windows, so os.path.join(REPO_ROOT, relpath)
# below still opens the file either way.
ENGINE_SOURCES = [
    "models/decision_model.py",
    "models/signal_router.py",
    "live_trading.py",
]


def _code(relpath):
    """Source with comment lines stripped — the notes ABOUT the removed
    default necessarily quote it, and a guard that reads its own explanation
    as a violation is useless."""
    with io.open(os.path.join(REPO_ROOT, relpath), encoding="utf-8",
                 newline="") as f:
        src = f.read()
    return "\n".join(line.split("#", 1)[0] for line in src.splitlines())


@pytest.mark.parametrize("relpath", ENGINE_SOURCES)
def test_no_module_defaults_a_missing_risk_verdict_to_a_pass(relpath):
    """
    A source-text guard, deliberately, and for the same reason
    tests/test_no_fabricated_fallbacks.py uses them: with the validator in
    place the behavioural route to two of these three call sites is closed, so
    a behavioural test alone would stop noticing if the default came back.

    Three call sites had the identical line. Rule 3 of this project's earned
    rules — a defect found once is usually a class — says the thing to guard
    is the shape, not the three instances of it.
    """
    code = _code(relpath)
    assert 'risk_valid", True' not in code and "risk_valid', True" not in code, (
        f"{relpath} defaults a missing risk verdict to True again. An absent "
        f"assessment is not a passed one — read it through "
        f"models.risk_model.read_risk_verdict()."
    )
