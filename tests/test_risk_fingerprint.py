"""
The run record must identify the settings that produced the plan.

WHAT WAS WRONG

core/decision_log.py has carried this sentence since the Finding 6 fix was
written:

    "The audit's required action asks for 'all decision-affecting
     configuration, including risk-model multipliers and bias weights.'"

Fifteen lines below it, FINGERPRINTED_MODULES named one module: the bias
engine. The weights were fingerprinted. The risk-model multipliers were not.

Changing ATR_STOP_MULT from 1.2 to 1.5 moves the stop and all three targets
on every run this engine makes. Before this change, two such runs were
byte-identical across run_hash, config_snapshot, module_snapshot and
provenance -- the same recorded identity for two different trading plans on
the same candles. Item 6 is Traceability, raised to Critical on 29 August,
and that is the rule this broke, inside the fix written to satisfy it.

It was not a name missing from a list. models/risk_model.py set those four
multipliers on the RiskModel INSTANCE, and module_snapshot() reads MODULE
attributes -- it cannot see instance state. There was nothing for the list
to name. Nor was risk_model.py alone: it held no module-level constants at
all, so every threshold in it had the same problem.

Found on 2 September by an audit run that never completed, and verified
against source before being believed.

WHY THE CONSTANTS MOVED RATHER THAN THE MECHANISM

Two fixes were available: move the numbers to module level, or extend
module_snapshot() to instantiate classes and read their attributes. Viktor
chose the first on 2 September, on the grounds that it is the smaller change
and that models/bias_engine.py -- the one module already complying -- is
shaped that way. The mechanism stays simple and the two risk-bearing modules
come to it.

WHAT THESE TESTS HOLD

Four things, because a fingerprint can fail in four different directions:
a name that does not exist, a name that exists and is read by nothing, a
constant the arithmetic ignores, and a multiplier that creeps back onto the
instance where the snapshot cannot see it. The third is the one that matters
most and the one a declaration-only test would miss: sequence item 14 found
SEVEN config constants that were fingerprinted and read by nothing, so the
log recorded seven settings as "the knobs that change the numbers" when
changing any of them changed nothing.
"""

import io
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.decision_log import FINGERPRINTED_MODULES, module_snapshot
from models import risk_model
from models.risk_model import RiskModel

MODULE_KEY = "models.risk_model"
SOURCE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "models", "risk_model.py",
)


def _source():
    with io.open(SOURCE_PATH, encoding="utf-8") as fh:
        return fh.read()


def _names():
    return FINGERPRINTED_MODULES[MODULE_KEY]


def test_the_risk_model_is_fingerprinted_at_all():
    """
    The entry itself. Stated separately from the checks below because its
    absence is the original defect, not a degraded form of it.
    """
    assert MODULE_KEY in FINGERPRINTED_MODULES, (
        "models.risk_model is not fingerprinted. Every stop and every target "
        "this engine produces is computed from constants in that module, and "
        "without this entry two runs with different multipliers record the "
        "same run_hash."
    )


def test_every_fingerprinted_name_exists_and_is_a_number():
    missing = [n for n in _names() if not hasattr(risk_model, n)]
    assert not missing, (
        "FINGERPRINTED_MODULES names constants risk_model.py does not "
        "define: " + ", ".join(missing)
    )

    not_numeric = [
        n for n in _names()
        if not isinstance(getattr(risk_model, n), (int, float))
    ]
    assert not not_numeric, (
        "these fingerprinted names are not numbers, so the snapshot is "
        "recording something other than a setting: " + ", ".join(not_numeric)
    )


def test_no_fingerprinted_constant_is_dead():
    """
    Sequence item 14's finding, applied to this module before it can repeat.

    A constant that is declared and never read makes the record claim a knob
    exists that changes nothing. Each name must appear in the source at least
    twice: its definition, and at least one place that reads it.
    """
    source = _source()
    dead = [n for n in _names() if source.count(n) < 2]
    assert not dead, (
        "these constants are fingerprinted but read by nothing in "
        "risk_model.py, so the record names settings that do not affect a "
        "decision: " + ", ".join(dead)
    )


def test_the_multipliers_have_not_returned_to_the_instance():
    """
    The defect was instance state the snapshot could not see. A future
    __init__ that copies these onto self would restore it silently: the
    snapshot would report the module value while the arithmetic used the
    instance one, and the record would be wrong in exactly the way that is
    hardest to notice.
    """
    source = _source()
    for attr in ("self.atr_stop_mult", "self.target1_mult",
                 "self.target2_mult", "self.target3_mult"):
        assert attr not in source, (
            f"{attr} is back on the instance. module_snapshot() reads module "
            f"attributes and cannot see it, so the fingerprint would no "
            f"longer describe the arithmetic that produced the plan."
        )

    assert not hasattr(RiskModel, "__init__") or \
        RiskModel.__init__ is object.__init__, (
        "RiskModel has regained an __init__. If it sets decision-affecting "
        "state, that state is invisible to the run record."
    )


def test_module_snapshot_actually_carries_the_risk_constants():
    snapshot = module_snapshot()
    assert MODULE_KEY in snapshot, "module_snapshot() did not record risk_model"

    recorded = snapshot[MODULE_KEY]
    for name in _names():
        assert name in recorded, f"{name} is missing from the snapshot"
        assert recorded[name] == getattr(risk_model, name), (
            f"the snapshot records {name} as {recorded[name]!r} while the "
            f"module holds {getattr(risk_model, name)!r}"
        )


# ======================================================================
# The behavioural half. A declaration test proves the name exists; only
# these prove the number is the one the arithmetic uses.
# ======================================================================

def _plan(**overrides):
    kwargs = dict(
        detailed_bias="BULLISH CONFIRMED",
        trend_health=50.0,
        current_price=100.0,
        atr_val=2.0,
        structural_level=None,
        bias_score=40.0,
        volatility_state="NORMAL",
    )
    kwargs.update(overrides)
    return RiskModel().calculate_stop_targets(**kwargs)


def test_the_stop_is_computed_from_the_fingerprinted_multiplier(monkeypatch):
    stop_before, _, _, _ = _plan()

    monkeypatch.setattr(risk_model, "ATR_STOP_MULT",
                        risk_model.ATR_STOP_MULT * 2.0)
    stop_after, _, _, _ = _plan()

    assert stop_after != stop_before, (
        "doubling ATR_STOP_MULT did not move the stop. The constant is "
        "fingerprinted but the arithmetic reads something else, which is the "
        "item 14 defect in a new place: the record would name a setting that "
        "changes nothing."
    )
    assert stop_after < stop_before, (
        "doubling the stop multiplier should widen a long's stop, not tighten it"
    )


def test_each_target_is_computed_from_its_own_fingerprinted_multiplier(monkeypatch):
    _, t1_before, t2_before, t3_before = _plan()

    monkeypatch.setattr(risk_model, "TARGET2_MULT",
                        risk_model.TARGET2_MULT + 1.0)
    _, t1_after, t2_after, t3_after = _plan()

    assert t2_after != t2_before, "TARGET2_MULT is not read by the target maths"
    assert t1_after == t1_before, "changing TARGET2_MULT moved target 1"
    assert t3_after == t3_before, "changing TARGET2_MULT moved target 3"


def test_the_volatility_multipliers_are_read(monkeypatch):
    stop_before, _, _, _ = _plan(volatility_state="HIGH VOLATILITY")

    monkeypatch.setattr(risk_model, "VOL_MULT_HIGH",
                        risk_model.VOL_MULT_HIGH * 2.0)
    stop_after, _, _, _ = _plan(volatility_state="HIGH VOLATILITY")

    assert stop_after != stop_before, (
        "VOL_MULT_HIGH is fingerprinted but the high-volatility branch does "
        "not read it"
    )


def test_the_regime_boundaries_are_read(monkeypatch):
    model = RiskModel()

    assert model.classify_risk_regime("NORMAL", 9.0, 80.0) == "EXTREME RISK"
    monkeypatch.setattr(risk_model, "REGIME_EXTREME_STOP_PCT", 20.0)
    assert model.classify_risk_regime("NORMAL", 9.0, 80.0) != "EXTREME RISK", (
        "REGIME_EXTREME_STOP_PCT is fingerprinted but classify_risk_regime "
        "does not read it"
    )


def test_the_stop_distance_limits_are_read(monkeypatch):
    model = RiskModel()

    # A stop 20% away fails on the maximum.
    valid, reason, _ = model.validate_risk_parameters(100.0, 80.0)
    assert valid is False
    assert "maximum" in reason.lower()

    # Raising the ceiling past 20% must retire THAT rejection. The trade is
    # still refused -- a 20% stop is EXTREME RISK by the regime boundary a
    # few lines further down -- so the check is that the REASON changed, not
    # that the plan passed. Asserting valid is True here would be asserting
    # something the engine should not do.
    monkeypatch.setattr(risk_model, "MAX_STOP_DISTANCE_PCT", 25.0)
    valid_after, reason_after, _ = model.validate_risk_parameters(100.0, 80.0)
    assert "maximum" not in reason_after.lower(), (
        "MAX_STOP_DISTANCE_PCT is fingerprinted but validate_risk_parameters "
        "does not read it -- raising the ceiling to 25% left a 20% stop still "
        "rejected for exceeding the maximum"
    )
    assert valid_after is False and "EXTREME" in reason_after, (
        "a 20% stop should now be refused by the risk regime rather than by "
        "the distance ceiling"
    )


def test_the_rejection_message_quotes_the_constant_it_enforces():
    """
    The message used to read "(15%)" as a literal beside a literal 15.0.
    Two declarations of one number drift the moment either is edited -- the
    defect this project has recorded at item 14, at Finding 3 and at 2be405f.
    """
    model = RiskModel()
    _, reason, _ = model.validate_risk_parameters(100.0, 80.0)
    assert f"{risk_model.MAX_STOP_DISTANCE_PCT:.0f}%" in reason, (
        "the rejection message no longer quotes MAX_STOP_DISTANCE_PCT, so "
        "the text and the threshold can now disagree"
    )
