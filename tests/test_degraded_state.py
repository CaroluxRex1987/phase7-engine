"""
Sequence item 9a — Items 13 + 8, fail safely and epistemic honesty.

Viktor's ruling of 29 August, verbatim:

    "When an indicator fails, the engine continues in an explicitly degraded
     state. It must not fabricate replacement values. The failure must be
     recorded in the decision output, and confidence and trade quality must be
     reduced accordingly. A degraded result does not by itself authorize
     trading."

That ruling went against GLM's recommendation and against Claude's instinct.
Both preferred halting: it is cheaper, adds no machinery, and satisfies the
invariant's letter. GLM flagged its own preference as a habit shared with the
model family that built this engine, which is what made the choice Viktor's.

These tests are the ruling made checkable. Each of the four clauses gets one.

HOW A FAILURE IS SIMULATED

By making the indicator genuinely fail, not by hand-building a degraded object.
A test that constructs {"degraded": True} and checks the engine formats it
nicely proves the formatter works; it proves nothing about whether a real
pandas_ta exception ever reaches it.

So these patch the pandas_ta function to raise, and run the whole pipeline over
it.

WHICH INDICATOR TO BREAK, AND A TEST THAT WAS WRONG ABOUT IT

The first version of this file broke `ta.rsi` and asserted the run came back
degraded. It did not, and the code was right.

RSI, ATR and the EMAs each have a second computation path — a manual RSI, a
manual true range, pandas' own ewm(). Those are kept deliberately: they compute
the same quantity by another route, which is not the fabrication this item
removes. So breaking `ta.rsi` is recovered from, silently and correctly, and
the run is not degraded because nothing was lost.

ADX and SuperTrend have no second route. They are the ones that degrade.

The distinction is the whole point of item 9a — a fallback that recomputes the
same number is fine, a fallback that invents one is not — and the first draft
of this file did not encode it. test_a_recoverable_failure_does_not_degrade_the_run
now asserts it directly, so the two kinds of fallback cannot be confused again.
"""

import os
import pytest

PINNED_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "fixtures", "pinned")
UNREACHABLE = "http://127.0.0.1:1"


def _engine_available():
    try:
        import pandas_ta  # noqa: F401
        return True
    except Exception:
        return False


def _pinned_frame():
    from data.data_fetcher import DataFetcher, data_fetcher
    original = data_fetcher.base_url
    try:
        data_fetcher.base_url = UNREACHABLE
        DataFetcher.set_pinned_source(PINNED_DIR)
        return data_fetcher.get_tf("AEROUSDT", "4h", limit=300)
    finally:
        DataFetcher.clear_pinned_source()
        data_fetcher.base_url = original


def _run_with_broken(indicator):
    """
    Run the engine end to end with one pandas_ta function raising.

    Patched on the ta module the indicators import, and restored in a finally.
    The alternative — deleting a column after the fact — would test that
    downstream code tolerates absence, not that the failure is detected and
    reported where it happens.
    """
    import indicators.indicators as ind
    from data.data_fetcher import DataFetcher, data_fetcher
    from models.signal_router import SignalRouter

    def explode(*a, **k):
        raise RuntimeError(f"simulated {indicator} failure")

    original_fn = getattr(ind.ta, indicator)
    original_url = data_fetcher.base_url
    try:
        setattr(ind.ta, indicator, explode)
        data_fetcher.base_url = UNREACHABLE
        DataFetcher.set_pinned_source(PINNED_DIR)
        return SignalRouter().route(symbol="AEROUSDT", timeframe="4h")
    finally:
        setattr(ind.ta, indicator, original_fn)
        DataFetcher.clear_pinned_source()
        data_fetcher.base_url = original_url


# ============================================================
# "It must not fabricate replacement values"
# ============================================================

def test_a_failed_indicator_leaves_no_column_behind():
    """
    The clause the other three rest on.

    Before 9a every failure wrote a constant: RSI 50.0, ADX 25.0, ATR 2% of
    price, SuperTrend = close, ST_Direction = 1.0 (bullish). Nothing downstream
    could tell those from measurements.

    A dropped column can be detected. A plausible number cannot.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    import indicators.indicators as ind

    df = _pinned_frame()
    original = ind.ta.adx
    try:
        ind.ta.adx = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom"))
        frame, failures = ind.add_technical_indicators(df)
    finally:
        ind.ta.adx = original

    assert "ADX" not in frame.columns, (
        "a failed ADX still produced an ADX column. Whatever is in it was not "
        "measured, and nothing downstream can tell."
    )
    assert any(f.indicator == "ADX" for f in failures), (
        f"ADX failed but was not reported. Failures: {[f.indicator for f in failures]}"
    )


def test_the_failure_names_the_indicator_and_the_consequence():
    """
    "Recorded" has to mean legible. An operator reading the panel needs to know
    which reading to distrust, which a traceback does not tell them.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    import indicators.indicators as ind

    df = _pinned_frame()
    original = ind.ta.supertrend
    try:
        ind.ta.supertrend = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom"))
        _frame, failures = ind.add_technical_indicators(df)
    finally:
        ind.ta.supertrend = original

    assert failures, "SuperTrend failed and nothing was recorded"
    text = str(failures[0])
    assert "SuperTrend" in text and "RuntimeError" in text and "—" in text, (
        f"the failure record is not legible: {text!r}\n"
        "It must name the indicator, why it failed, and what the engine loses."
    )


# ============================================================
# "The failure must be recorded in the decision output"
# ============================================================

def test_the_decision_object_reports_the_degradation():
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    decision = _run_with_broken("adx")
    assert "error" not in decision, (
        f"the engine halted instead of degrading: {decision.get('error')}\n"
        "Viktor ruled degrade, not halt. A failed ADX must not end the run."
    )

    block = decision.get("degradation", {})
    assert block.get("degraded") is True, (
        f"ADX was broken but the run does not report itself degraded: {block}"
    )
    assert any("ADX" in m for m in block.get("missing_inputs", [])), (
        f"the degradation block does not name ADX: {block.get('missing_inputs')}"
    )


def test_a_recoverable_failure_does_not_degrade_the_run():
    """
    The distinction item 9a rests on, made checkable.

    A fallback that recomputes the same quantity by another route is not a
    fabrication. RSI has a manual calculation, ATR has a manual true range, the
    EMAs have pandas' own ewm(). When pandas_ta fails on one of those, the
    engine computes the real number a different way and nothing is lost — so
    nothing is reported lost.

    ADX and SuperTrend have no second route, which is why the tests around this
    one break those instead.

    Without this test the two kinds of fallback look identical from outside,
    and the first draft of this file confused them: it broke ta.rsi, expected a
    degraded run, and reported the CODE as failing when the test was wrong.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    decision = _run_with_broken("rsi")

    assert "error" not in decision, (
        f"breaking ta.rsi ended the run: {decision.get('error')}\n"
        "The manual RSI calculation should have covered it."
    )

    block = decision.get("degradation", {})
    assert block.get("degraded") is False, (
        f"breaking ta.rsi marked the run degraded: {block}\n"
        "RSI was recomputed by the manual path, so nothing was lost. Marking "
        "this degraded would block trading on a run that measured everything "
        "it claims to — and would make the degraded flag mean 'something "
        "raised somewhere' rather than 'an input is missing'."
    )


def test_a_clean_run_is_not_marked_degraded():
    """
    The control. A flag that is always on is not a flag, and it would make the
    trading block below permanent — which is halting, wearing the degrade
    ruling's clothes.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    from data.data_fetcher import DataFetcher, data_fetcher
    from models.signal_router import SignalRouter

    original = data_fetcher.base_url
    try:
        data_fetcher.base_url = UNREACHABLE
        DataFetcher.set_pinned_source(PINNED_DIR)
        decision = SignalRouter().route(symbol="AEROUSDT", timeframe="4h")
    finally:
        DataFetcher.clear_pinned_source()
        data_fetcher.base_url = original

    block = decision.get("degradation", {})
    assert block.get("degraded") is False, (
        f"a clean run on sound pinned data reports itself degraded: {block}"
    )
    assert block.get("trading_authorized") is True, (
        "a clean run is not authorized to trade, which would make the "
        "degradation gate permanent"
    )


# ============================================================
# "Confidence and trade quality must be reduced accordingly"
# ============================================================

def test_confidence_and_trade_quality_are_capped_when_degraded():
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    from models.decision_model import DecisionModel

    ceiling = DecisionModel.DEGRADED_CONFIDENCE_CEILING
    decision = _run_with_broken("adx")
    risk = decision.get("risk", {})

    assert risk.get("confidence_score", 0.0) <= ceiling, (
        f"confidence is {risk.get('confidence_score')} on a degraded run, "
        f"above the {ceiling} ceiling"
    )
    assert risk.get("trade_quality_proposed", 0.0) <= ceiling, (
        f"trade quality (proposed entry) is "
        f"{risk.get('trade_quality_proposed')} on a degraded run, above the "
        f"{ceiling} ceiling"
    )


# ============================================================
# "A degraded result does not by itself authorize trading"
# ============================================================

def test_a_degraded_run_cannot_authorize_a_trade():
    """
    The load-bearing sentence of the ruling, and the one that makes degrading
    safe rather than merely more informative than halting.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    decision = _run_with_broken("adx")

    assert decision["degradation"]["trading_authorized"] is False, (
        "a degraded run reports trading as authorized"
    )

    action = decision.get("exit", {}).get("action", "")
    assert not any(side in action for side in ("LONG", "SHORT")), (
        f"a degraded run produced the action {action!r}, which names a side.\n"
        "Viktor's ruling: a degraded result does not by itself authorize "
        "trading. The analysis may still be published; the trade may not."
    )


def test_the_reasoning_says_why_out_loud():
    """
    A structural field a consumer might not read is not the same as telling the
    operator. The reason belongs in the prose they actually see.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    decision = _run_with_broken("adx")
    reasons = " ".join(decision.get("explanation", {}).get("reasons", []))

    assert "DEGRADED" in reasons.upper(), (
        "the decision reasoning does not mention that the run was degraded.\n"
        f"Reasons: {reasons}"
    )
    assert "ADX" in reasons, (
        "the reasoning says the run was degraded but not by what"
    )


# ============================================================
# Sequence item 9b — the last fabrication
# ============================================================

def test_a_failed_risk_calculation_does_not_invent_levels():
    """
    risk_model.calculate_stop_targets' except used to return "safe default
    fallback bounds": a stop at price x 0.99 and targets at 1.01, 1.02, 1.03.

    DIRECTION-BLIND. The stop sits 1% BELOW price and the targets ABOVE it,
    whatever the bias said — so on a short the stop is where the trade would be
    winning and every target is where it would be losing. The panel printed
    them as STOP LOSS and TARGET 1/2/3, with R:R ratios computed off them.

    Nor were they safe: a 1% stop on an instrument whose ATR is 4% is a stop
    inside the noise, and the 1/2/3% targets encode a reward profile that has
    nothing to do with this market.

    This is the only fabrication in the codebase that produced a
    TRADEABLE-LOOKING ARTEFACT rather than a wrong indicator reading, which is
    why it is tested by side rather than merely by presence.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    from models.risk_model import RiskModel

    model = RiskModel()

    # Force the failure from inside the try, by handing it an input the body
    # cannot work with. atr_val=None raises TypeError at the first comparison.
    #
    # The first draft of this test patched classify_risk_regime instead —
    # which calculate_stop_targets never calls; it belongs to
    # validate_risk_parameters. Nothing raised, the function returned real
    # levels, and the assertion below fired correctly on a test that had not
    # broken anything. Second time in item 9 that the test was wrong and the
    # code was right, which is its own small lesson about injecting failures
    # at a point you have actually confirmed is on the path.
    raised = None
    try:
        model.calculate_stop_targets(
            detailed_bias="BEARISH CONFIRMED",   # a SHORT
            trend_health=80.0,
            current_price=100.0,
            atr_val=None,
            structural_level=None,
            bias_score=-70.0,
        )
    except Exception as e:
        raised = e

    assert raised is not None, (
        "a failed stop/target calculation returned levels instead of raising.\n"
        "Whatever came back was not computed from this market, and the panel "
        "cannot tell — it prints a STOP LOSS and three TARGETs either way."
    )
    assert "risk plan" in str(raised).lower(), (
        f"the failure does not say what was lost: {raised}"
    )


def test_the_engine_reports_a_failed_risk_plan_rather_than_inventing_one():
    """
    End to end. The exception must reach the operator as a reported failure,
    not vanish into a handler that supplies levels of its own.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    import models.risk_model as rm
    from data.data_fetcher import DataFetcher, data_fetcher
    from models.signal_router import SignalRouter

    original = rm.RiskModel.calculate_stop_targets
    original_url = data_fetcher.base_url
    try:
        rm.RiskModel.calculate_stop_targets = lambda *a, **k: (
            _ for _ in ()
        ).throw(ValueError("simulated stop/target failure"))
        data_fetcher.base_url = UNREACHABLE
        DataFetcher.set_pinned_source(PINNED_DIR)
        decision = SignalRouter().route(symbol="AEROUSDT", timeframe="4h")
    finally:
        rm.RiskModel.calculate_stop_targets = original
        DataFetcher.clear_pinned_source()
        data_fetcher.base_url = original_url

    assert "error" in decision, (
        "the engine produced a normal decision object despite the stop/target "
        f"calculation failing. Keys: {sorted(decision)}\n"
        "That means something downstream supplied levels the market did not."
    )
    assert "risk" not in decision or not decision.get("risk", {}).get("targets"), (
        "the decision carries targets after the calculation that produces them "
        "failed"
    )


# ============================================================
# Sequence item 9c — the dead trend_failure gate
# ============================================================

def test_the_dead_trend_failure_gate_stays_removed():
    """
    `trend_failure` tested whether the last five values of the STRUCTURE column
    equalled "LH" or "LL". structure.py writes regime labels — "BULLISH TREND",
    "BEARISH TREND", "NEUTRAL STRUCTURE" — and never those two, so the flag was
    False on every run this engine has ever made.

    It was not one dead branch. Four modules acted on it: entry_model blocked
    entries, bias_engine halved the bias score, exit_model raised a watch flag,
    and the router published it as trend.failure. In each case it sat beside a
    live signal, so every block, discount and flag those lines ever produced
    came from something else.

    DELETED RATHER THAN WIRED. The audit found a gate that never fires, not a
    specification for one that should. Choosing when to block a trade is a
    trading decision, and wiring it would produce a behaviour change this
    project cannot yet evaluate — the golden baseline proves a change is
    attributable, never that it is correct, and backtesting sits behind the
    release gate. Recorded in claude/phase7-rulings.md.

    This guard exists because "restore the trend failure check" is an obvious
    thing for someone to do later, and doing it as a restoration rather than as
    a designed feature would bring back the same dead comparison.
    """
    import ast
    import inspect

    import indicators.trend_health as th
    import models.bias_engine as be
    import models.entry_model as em
    import models.exit_model as xm
    from core.decision_contract import TrendBlock

    # The parameter is gone from both consumers that took it.
    for fn in (em.generate_entry_signals, be.calculate_dynamic_bias):
        assert "trend_failure" not in inspect.signature(fn).parameters, (
            f"{fn.__name__} accepts trend_failure again. Nothing produces it."
        )

    # And from the published shape.
    assert "failure" not in TrendBlock.__annotations__, (
        "trend.failure is declared in the contract again. A field the engine "
        "does not compute must not be published as though it does."
    )

    # No module computes or reads it. Checked on the AST so a comment
    # explaining the removal does not count as a reference.
    offenders = []
    for module in (th, be, em, xm):
        src = inspect.getsource(module)
        for node in ast.walk(ast.parse(src)):
            if isinstance(node, ast.Name) and node.id == "trend_failure":
                offenders.append(module.__name__)
                break
            if (isinstance(node, ast.Constant) and node.value == "trend_failure"):
                offenders.append(module.__name__)
                break

    assert not offenders, (
        "trend_failure is back in: " + ", ".join(sorted(set(offenders)))
        + "\nIf structural-failure detection is wanted, it needs a real "
          "producer and its own justification — not the old comparison "
          "against labels structure.py has never written."
    )


# ============================================================
# Item 8/13 re-audit — the macro read gets the same treatment
# ============================================================
#
# tests/test_golden_path.py::test_the_macro_series_is_actually_read covers
# the case named in the roadmap: the macro timeframe fetch itself failing
# (deleting the pinned macro file, which makes get_tf return an empty frame
# that fails _validate_dataframe). This section covers the other half of the
# same fabricated-fallback shape: the macro frame fetches fine, but something
# raises while it is being processed. Before this fix engine_core.py's
# `except Exception` around that step only logged a warning and left
# macro_bias at "NEUTRAL" -- unreported, same as the fetch-failure case was.

def _run_with_broken_macro_processing():
    """
    Makes add_technical_indicators raise on its FIRST call only, then hands
    every later call through to the real function.

    engine_core.py calls add_technical_indicators on the macro frame (step
    1b) before it calls it on the base frame (step 2), so a first-call-only
    break lands exactly on the macro path and leaves base-data processing
    untouched -- unlike patching a single ta.* function (which would break
    the indicator on both frames, or unlike breaking the whole function
    unconditionally, which would also take down step 2 and turn this into a
    halt-the-run test instead of a degrade-the-macro-read test.
    """
    import core.engine_core as ec
    from data.data_fetcher import DataFetcher, data_fetcher
    from models.signal_router import SignalRouter

    real_fn = ec.add_technical_indicators
    calls = {"n": 0}

    def first_call_explodes(*a, **k):
        calls["n"] += 1
        if calls["n"] == 1:
            raise RuntimeError("simulated macro processing failure")
        return real_fn(*a, **k)

    original_url = data_fetcher.base_url
    try:
        ec.add_technical_indicators = first_call_explodes
        data_fetcher.base_url = UNREACHABLE
        DataFetcher.set_pinned_source(PINNED_DIR)
        return SignalRouter().route(symbol="AEROUSDT", timeframe="4h")
    finally:
        ec.add_technical_indicators = real_fn
        DataFetcher.clear_pinned_source()
        data_fetcher.base_url = original_url


def test_a_macro_processing_exception_degrades_rather_than_fabricates():
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    decision = _run_with_broken_macro_processing()
    assert "error" not in decision, (
        f"the engine halted instead of degrading: {decision.get('error')}\n"
        "A macro-processing exception must not end the run any more than a "
        "failed indicator does."
    )

    assert decision.get("macro_bias") == "NEUTRAL", (
        f"expected macro_bias='NEUTRAL' when macro processing raises "
        f"(the engine cannot invent a direction), got "
        f"{decision.get('macro_bias')!r}"
    )

    block = decision.get("degradation", {})
    assert block.get("degraded") is True, (
        f"macro processing raised but the run does not report itself "
        f"degraded: {block}\n"
        "Before the item 8/13 fix this exception was only logged, so a "
        "failed macro read and a genuinely neutral one looked identical."
    )
    assert any("macro" in m.lower() for m in block.get("missing_inputs", [])), (
        f"the degradation block does not name the macro timeframe: "
        f"{block.get('missing_inputs')}"
    )
