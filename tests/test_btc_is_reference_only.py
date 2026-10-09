"""
Bitcoin is reference only -- N5, Viktor's ruling of 5 October 2026 (point 7
of round 8's triage, by agreeing to Claude's suggestion).

WHAT WAS THERE

DecisionModel._compute_btc_adjusted made a second confidence figure: the
run's confidence, moved by up to 20 points either way -- BTC's bias strength
times the pair's signed correlation, signed by whether BTC's side agreed with
the asset's -- and by 15 down under broad market stress (BTC_ADJUSTMENT_CAP
20.0, BTC_STRESS_PENALTY 15.0). The router merged it into the BTC block as
btc_adjusted_confidence, with its explanatory sentence as reasons, and the
panel printed it as

    BTC-ADJUSTED CONFIDENCE: <x>/100 (vs <y>/100 unadjusted)

with a line under it saying nothing had tested it, and then the sentence. It
ran after the action, confidence, trade quality and EV were set, and nothing
that decides read it. Nothing had tested whether it predicted anything
either: the 15 September PDF's point 3, and the Part 7 document's N5 ("the
BTC adjustment has no baseline").

THE RULING, AND WHAT THE PATCH CHOSE

"Bitcoin is reference only": the panel's line is removed and the BTC section
stays. Whether the computation and its record field went with the line was
left to the patch. They do -- the reading the ruling named as Claude's -- and
so do the two constants, evaluate()'s btc_context and symbol parameters (the
adjustment was their only reader) and the BTC bias score engine_core handed
the router only for it. The BTC block is now available whenever engine_core
measured BTC; until N5 it also needed the adjustment to have been computed.

WHAT THIS FILE HOLDS

That none of it comes back -- in the model, the router's merge, the
contract, the record's readable fingerprint or the panel -- and, as negative
controls, that the BTC section still renders and the block is still
available when engine_core measured BTC. Stale keys are fed in on purpose
where a consumer could pass them through, so a merge or a panel that started
reading them again fails here, not only a producer that started writing them.

Fixture-free, per run_tests.py. The last test runs the engine on the pinned
fixture and is skipped without pandas_ta.
"""

import inspect
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Imported for its side effect as much as for the path: conftest points
# config.LOG_DIR at a temporary directory, so the pinned run below cannot
# write into the engine's real record.
from conftest import REPO_ROOT  # noqa: E402

PINNED_DIR = os.path.join(REPO_ROOT, "tests", "fixtures", "pinned")
UNREACHABLE = "http://127.0.0.1:9"

REMOVED_CONSTANTS = ("BTC_ADJUSTMENT_CAP", "BTC_STRESS_PENALTY")
REMOVED_FIELDS = ("btc_adjusted_confidence", "reasons")

# What the adjustment used to put into the BTC block, and the BTC bias score
# engine_core used to hand over for it -- fed in stale on purpose.
STALE = {
    "score": 60.0,
    "btc_adjusted_confidence": 64.5,
    "reasons": ["BTC-adjusted confidence: 65/100 (vs 50/100 unadjusted, "
                "never replacing it)."],
}


def _producer_block(**over):
    """An available BTC block shaped as core/engine_core.py writes it at N5."""
    block = {
        "available": True,
        "raw": "BULLISH",
        "detailed": "BULLISH CONFIRMED",
        "regime": "BULLISH TREND",
        "volatility": "MEDIUM VOLATILITY",
        "trend_health": 71.0,
        "correlation": 0.57,
        "correlation_label": "MODERATE POSITIVE",
        "beta": 0.98,
        "broad_market_stress": False,
        "n_observations": 30,
        "degraded_inputs": [],
    }
    block.update(over)
    return block


def _declared_btc_keys():
    """Every key core/decision_contract.py declares for the BTC block."""
    from core.decision_contract import BtcContextBlock

    return set(BtcContextBlock.__required_keys__) | set(BtcContextBlock.__optional_keys__)


def _neutral_inputs():
    """bias, trend, entry, risk for a run the ladder answers WAIT."""
    return (
        {"raw": "NEUTRAL", "detailed": "NEUTRAL", "score": 5.0},
        {"trend_health": 60.0, "trend_direction_sign": 1},
        {"score": 40.0, "entry_status": "AWAY FROM ZONE"},
        {"risk_valid": True, "risk_regime": "NORMAL RISK",
         "validation_state": "NEUTRAL", "targets": [1.1, 1.2, 1.3]},
    )


# --- the decision model ------------------------------------------------------

def test_the_decision_model_no_longer_computes_a_btc_figure():
    from models.decision_model import DecisionModel

    assert not hasattr(DecisionModel, "_compute_btc_adjusted"), (
        "DecisionModel computes a BTC-adjusted confidence again")
    for name in REMOVED_CONSTANTS:
        assert not hasattr(DecisionModel, name), f"DecisionModel.{name} is back"

    params = list(inspect.signature(DecisionModel.evaluate).parameters)
    assert "btc_context" not in params and "symbol" not in params, (
        f"evaluate() takes BTC context or a symbol again: {params}")
    # Negative control: the scan reads the real signature.
    assert "risk" in params and "degradation" in params, params


def test_evaluate_returns_no_btc_figure():
    from models.decision_model import DecisionModel

    out = DecisionModel().evaluate(*_neutral_inputs())

    assert out.get("final_action") == "WAIT", out.get("final_action")
    btc_keys = [k for k in out if "btc" in k.lower()]
    assert not btc_keys, f"evaluate() returns BTC output again: {btc_keys}"


def test_a_caller_still_passing_the_old_keywords_fails_loudly():
    """
    A stale caller must fail at the call, not have its BTC context silently
    dropped -- the router's own call is the one this would catch.
    """
    from models.decision_model import DecisionModel

    for kwargs in ({"btc_context": _producer_block()}, {"symbol": "AEROUSDT"}):
        try:
            DecisionModel().evaluate(*_neutral_inputs(), **kwargs)
        except TypeError:
            continue
        raise AssertionError(f"evaluate() accepted {sorted(kwargs)}")

    # Negative control: the keyword that stays is still accepted.
    out = DecisionModel().evaluate(*_neutral_inputs(), degradation=[])
    assert out.get("final_action") == "WAIT", out.get("final_action")


# --- the router's merge, and the contract ------------------------------------

def test_the_btc_block_carries_only_what_engine_core_measured():
    from models.signal_router import SignalRouter

    block = SignalRouter(engine_core=object())._merge_btc_context(
        _producer_block(**STALE))

    assert block.get("available") is True, (
        "engine_core measured BTC and the block says it is unavailable")
    for field in list(REMOVED_FIELDS) + ["score"]:
        assert field not in block, f"the BTC block carries {field!r} again"
    assert set(block) == _declared_btc_keys(), (
        "the BTC block and core/decision_contract.py disagree.\n"
        f"  produced, not declared: {sorted(set(block) - _declared_btc_keys())}\n"
        f"  declared, not produced: {sorted(_declared_btc_keys() - set(block))}\n"
        "test_decision_contract.py skips the second half for this block, "
        "because it is total=False; this is where it is checked.")


def test_the_block_is_available_exactly_when_engine_core_says_so():
    """
    Until N5 the block also needed the adjustment to have been computed;
    an adjustment that raised made the whole section print as unavailable.
    """
    from models.signal_router import SignalRouter

    router = SignalRouter(engine_core=object())
    assert router._merge_btc_context(_producer_block())["available"] is True
    assert router._merge_btc_context({"available": False}) == {"available": False}
    assert router._merge_btc_context(None) == {"available": False}


def test_the_contract_declares_neither_field():
    declared = _declared_btc_keys()
    for field in REMOVED_FIELDS:
        assert field not in declared, (
            f"core/decision_contract.py declares {field!r} for the BTC block "
            f"again, and nothing produces it")
    # Negative control: the declaration is being read.
    assert {"available", "correlation", "degraded_inputs"} <= declared, declared


# --- the record ---------------------------------------------------------------

def test_the_record_names_neither_constant():
    from core import decision_log

    listed = decision_log.FINGERPRINTED_MODULES["models.decision_model"]
    snap = decision_log.module_snapshot()["models.decision_model"]
    for name in REMOVED_CONSTANTS:
        assert f"DecisionModel.{name}" not in listed, (
            f"FINGERPRINTED_MODULES lists DecisionModel.{name} again")
        assert f"DecisionModel.{name}" not in snap
    # Negative control: the snapshot still walks to a class constant.
    assert snap["DecisionModel.DEGRADED_CONFIDENCE_CEILING"] == 50.0


# --- the panel ----------------------------------------------------------------

def test_the_panel_keeps_the_btc_section_and_prints_no_adjusted_line():
    from core.panel_render import render_panel

    panel = render_panel({
        "symbol": "TESTUSDT", "timeframe": "4h",
        "risk": {"confidence_score": 32.0},
        "btc_context": _producer_block(**STALE),
    })
    assert isinstance(panel, str), "render_panel returned no panel"
    lines = [line.strip() for line in panel.splitlines()]

    # Negative control: the section is still there. A panel that dropped it
    # would pass every absence check below.
    for prefix in ("BTC BIAS", "BTC REGIME", "CORRELATION", "BTC SENSITIVITY",
                   "BROAD MARKET STRESS"):
        assert any(line.startswith(prefix) for line in lines), (
            f"no {prefix} line in the BTC section:\n{panel}")

    lowered = panel.lower()
    for text in ("btc-adjusted", "unadjusted", "empirically unvalidated",
                 "never replacing it"):
        assert text not in lowered, f"the panel prints {text!r} again:\n{panel}"

    # The section still ends on a blank line, as it did when the sentence's
    # bullet closed it.
    stress = next(n for n, line in enumerate(lines)
                  if line.startswith("BROAD MARKET STRESS"))
    assert lines[stress + 1] == "", (
        f"BROAD MARKET STRESS is followed by {lines[stress + 1]!r}, not a "
        f"blank line")


# --- end to end ---------------------------------------------------------------

def test_a_pinned_run_records_and_prints_no_btc_figure():
    import pytest

    pytest.importorskip("pandas_ta")

    from core.panel_render import render_panel
    from data.data_fetcher import DataFetcher, data_fetcher
    from models.signal_router import SignalRouter

    original_url = data_fetcher.base_url
    try:
        data_fetcher.base_url = UNREACHABLE
        DataFetcher.set_pinned_source(PINNED_DIR)
        decision = SignalRouter().route(symbol="AEROUSDT", timeframe="4h")
    finally:
        DataFetcher.clear_pinned_source()
        data_fetcher.base_url = original_url

    assert "error" not in decision, decision.get("error")

    btc = decision.get("btc_context", {})
    assert btc.get("available") is True, (
        "the pinned fixture has BTC candles, so the block must be available")
    assert set(btc) == _declared_btc_keys(), sorted(set(btc) ^ _declared_btc_keys())

    constants = decision["provenance"]["module_constants"]["models.decision_model"]
    for name in REMOVED_CONSTANTS:
        assert f"DecisionModel.{name}" not in constants, (
            f"the record names DecisionModel.{name} again")

    panel = render_panel(decision)
    assert "btc-adjusted" not in panel.lower(), "the panel prints the line again"
    assert "BROAD MARKET STRESS" in panel, "the BTC section is gone from the panel"
