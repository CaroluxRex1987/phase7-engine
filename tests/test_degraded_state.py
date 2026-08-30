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
        print("SKIP: pandas_ta not installed")
        return

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
        print("SKIP: pandas_ta not installed")
        return

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
        print("SKIP: pandas_ta not installed")
        return

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
        print("SKIP: pandas_ta not installed")
        return

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
        print("SKIP: pandas_ta not installed")
        return

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
        print("SKIP: pandas_ta not installed")
        return

    from models.decision_model import DecisionModel

    ceiling = DecisionModel.DEGRADED_CONFIDENCE_CEILING
    decision = _run_with_broken("adx")
    risk = decision.get("risk", {})

    assert risk.get("confidence_score", 0.0) <= ceiling, (
        f"confidence is {risk.get('confidence_score')} on a degraded run, "
        f"above the {ceiling} ceiling"
    )
    assert risk.get("trade_quality_current", 0.0) <= ceiling, (
        f"trade quality (current market) is {risk.get('trade_quality_current')} "
        f"on a degraded run, above the {ceiling} ceiling"
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
        print("SKIP: pandas_ta not installed")
        return

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
        print("SKIP: pandas_ta not installed")
        return

    decision = _run_with_broken("adx")
    reasons = " ".join(decision.get("explanation", {}).get("reasons", []))

    assert "DEGRADED" in reasons.upper(), (
        "the decision reasoning does not mention that the run was degraded.\n"
        f"Reasons: {reasons}"
    )
    assert "ADX" in reasons, (
        "the reasoning says the run was degraded but not by what"
    )
