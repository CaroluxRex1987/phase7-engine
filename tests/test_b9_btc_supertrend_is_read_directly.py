"""
B9 -- a failed BTC SuperTrend is not read as a neutral one.

THE DEFECT

Claude's self-review of 5 October 2026 (B9; the review is kept outside the
repository) named four defaults left in engine_core.py's BTC block. Three of
them -- NEUTRAL STRUCTURE, NEUTRAL VOLUME and NONE -- went with the fallback
sweep of 13 October (`797bdc9`), which did not say it was doing B9's work.
The fourth was the SuperTrend: when BTC's ST_Direction column was missing,
the block read 0.0.

The column is missing exactly when BTC's SuperTrend calculation failed:
indicators.py records the failure and leaves no column. For BTC that record
reached only a log line ("BTC context indicator failure"), never the decision
object, and bias_engine scores a direction of 0.0 as a neutral SuperTrend. So
the panel's BTC BIAS line printed a reading one of its factors short, as if
it were complete.

THE RULING, 15 OCTOBER 2026

By agreeing to Claude's suggestion (docs/PHASE7_DECISIONS.md, "Ruling,
15 October 2026 -- B9: ..."): BTC's SuperTrend is read directly, the
13 October shape. A missing column raises inside the BTC block, and the
block's handler reports BTC unavailable for the run, as it does for any BTC
failure. The asset's own SuperTrend read keeps its 0.0: there a failure is a
recorded degradation, so no trade can follow from it, and it is on the list
for after the audit.

WHAT THESE TESTS HOLD

1. With BTC's SuperTrend failing, the routed decision reports BTC
   unavailable. Fails against the pre-fix code, where the block stayed
   available with a bias computed from 0.0.
2. The panel then says BTC is unavailable and prints no BTC BIAS line.
   Fails against the pre-fix code.
3. The asset's own analysis does not move when only BTC's SuperTrend fails.
   A control: passes on both sides.
4. A healthy run keeps the BTC section and its BTC BIAS line. A control:
   passes on both sides.
5. The asset's own SuperTrend failing still degrades the run rather than
   ending it, and authorizes no trade. The 0.0 there was left by the ruling;
   a fix that read it directly too would turn a failed indicator into a
   failed run, against the 29 August ruling (degrade, don't halt). A control:
   passes on both sides.

The failure is made the way it happens: pandas_ta's supertrend raises, and
indicators.py's own handler records it and leaves no column. It raises only
for one series, told apart by price: the pinned BTCUSDT candles close above
50,000, the pinned AEROUSDT candles below 1.

All fixture-free, so run_tests.py runs them too.
"""

import json
import os

import pytest

# Importing conftest points config.LOG_DIR at the suite's own temporary
# directory, under run_tests.py as well as pytest, so these runs write no
# record where the engine keeps its real one.
from conftest import REPO_ROOT

PINNED_DIR = os.path.join(REPO_ROOT, "tests", "fixtures", "pinned")
UNREACHABLE = "http://127.0.0.1:9"

# Between the two pinned series: BTCUSDT_4h closes 53,584.77 to 62,338.69,
# AEROUSDT_4h 0.49 to 0.81 and AEROUSDT_1d 0.43 to 0.97.
BTC_PRICE_FLOOR = 1000.0

# Sections of the decision object that describe the asset's own analysis.
# exit_watch is left out on purpose: it compares against the state file the
# previous run wrote, so two runs in a row can differ there for reasons that
# have nothing to do with BTC. provenance and lineage are left out because
# they carry run times.
ASSET_SECTIONS = ("bias", "degradation", "entry", "exit", "macro_bias",
                  "risk", "structure", "trend")


def _engine_available():
    try:
        import pandas_ta  # noqa: F401
        return True
    except Exception:
        return False


def _route(fail_supertrend_for=None):
    """
    Route the pinned AEROUSDT set, with one series' SuperTrend raising.

    fail_supertrend_for is None, "btc" or "asset". The patch sits on the ta
    module indicators.py imports, as in tests/test_degraded_state.py, and is
    restored in a finally.
    """
    import indicators.indicators as ind
    from data.data_fetcher import DataFetcher, data_fetcher
    from models.signal_router import SignalRouter

    real_supertrend = ind.ta.supertrend

    def supertrend(high, low, close, *args, **kwargs):
        is_btc = float(close.iloc[-1]) > BTC_PRICE_FLOOR
        if ((fail_supertrend_for == "btc" and is_btc)
                or (fail_supertrend_for == "asset" and not is_btc)):
            raise RuntimeError(f"simulated {fail_supertrend_for} SuperTrend failure")
        return real_supertrend(high, low, close, *args, **kwargs)

    original_url = data_fetcher.base_url
    try:
        ind.ta.supertrend = supertrend
        data_fetcher.base_url = UNREACHABLE
        DataFetcher.set_pinned_source(PINNED_DIR)
        return SignalRouter().route(symbol="AEROUSDT", timeframe="4h")
    finally:
        ind.ta.supertrend = real_supertrend
        DataFetcher.clear_pinned_source()
        data_fetcher.base_url = original_url


def _canonical(section):
    """A section as comparable text: NaN compares unequal to itself."""
    return json.dumps(section, sort_keys=True, default=str)


def test_a_failed_btc_supertrend_leaves_the_btc_section_unavailable():
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    decision = _route(fail_supertrend_for="btc")
    assert "error" not in decision, decision.get("error")

    assert decision["btc_context"]["available"] is False, (
        "BTC's SuperTrend failed, and the BTC section is still reported "
        f"available: {decision['btc_context']!r}. Its bias was computed from "
        "a direction of 0.0, which bias_engine scores as a neutral SuperTrend "
        "-- a reading one factor short, recorded as if complete. B9, ruled "
        "15 October 2026: the direction is read directly, so the block is "
        "unavailable for the run."
    )


def test_the_panel_says_btc_is_unavailable_and_prints_no_btc_bias():
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    from core.panel_render import render_panel

    decision = _route(fail_supertrend_for="btc")
    panel = render_panel(decision)

    assert "BTC BIAS" not in panel, (
        "the panel printed a BTC BIAS for a run in which BTC's SuperTrend "
        "failed, with nothing to say a factor was missing"
    )
    assert "unavailable this run" in panel, (
        "the panel does not say the BTC section is unavailable"
    )


def test_control_the_assets_own_analysis_does_not_move():
    """
    BTC is reference only (Viktor's ruling, 5 October 2026, point 7), so a
    BTC-only failure must leave everything the asset's own analysis produced
    exactly as a healthy run leaves it.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    control = _route()
    failed = _route(fail_supertrend_for="btc")
    assert "error" not in control, control.get("error")
    assert "error" not in failed, failed.get("error")

    moved = [key for key in ASSET_SECTIONS
             if _canonical(control[key]) != _canonical(failed[key])]
    assert not moved, (
        f"a BTC-only SuperTrend failure moved the asset's own {moved}"
    )


def test_control_a_healthy_btc_supertrend_keeps_the_section():
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    from core.panel_render import render_panel

    decision = _route()
    assert "error" not in decision, decision.get("error")
    assert decision["btc_context"]["available"] is True, decision["btc_context"]
    assert "BTC BIAS" in render_panel(decision)


def test_control_the_assets_own_supertrend_failure_still_degrades_the_run():
    """
    The other half of the ruling. The asset's own read keeps its 0.0: a
    failed SuperTrend there is named in the degradation block, which
    authorizes no trade. Reading it directly as well would end the run with
    an error instead, which the 29 August ruling forbids.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    decision = _route(fail_supertrend_for="asset")
    assert "error" not in decision, (
        f"the asset's SuperTrend failed and the run ended in an error: "
        f"{decision.get('error')!r}. Viktor ruled degrade, not halt."
    )

    block = decision["degradation"]
    assert block["degraded"] is True, block
    assert any("SuperTrend" in m for m in block["missing_inputs"]), block
    action = decision["exit"]["action"]
    assert not any(side in action for side in ("LONG", "SHORT")), (
        f"a degraded run authorized {action}"
    )
    assert decision["btc_context"]["available"] is True, (
        "the asset's own failure took the BTC section with it"
    )
