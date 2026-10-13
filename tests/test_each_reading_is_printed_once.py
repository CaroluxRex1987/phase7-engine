"""
Each reading printed once -- 13 October 2026.

WHAT WAS WRONG

Viktor's live run for F9 (12 October) showed two readings printed twice:

1. REGIME printed what STRUCTURE printed. The REGIME line printed
   bias['regime'], which engine_core sets from calculate_dynamic_regime --
   a read of the STRUCTURE column that calculate_structure fills with its own
   result['regime']. The STRUCTURE line printed structure['regime'], that same
   result['regime']. One value, two lines; they could differ only when a
   fallback fired.
2. The STRUCTURE line's "| Vol:" field and the VOLATILITY line both printed
   bias['volatility'].

THE RULING

DECISIONS, "Ruling, 13 October 2026 -- the fallback sweep", point 6, by
agreeing to Claude's suggestion: the REGIME line goes (STRUCTURE prints the
value at its source), and the Vol field goes from the STRUCTURE line
(VOLATILITY is the line labelled for it). Patch 2 of the 12 October additions.

WHAT THESE TESTS HOLD

- No line of the panel is headed REGIME, and bias['regime'] is not printed
  anywhere: a sentinel put there does not appear.
- bias['volatility'] is printed exactly once, on the VOLATILITY line, and no
  line of the asset's own readings carries a "Vol:" field.
- The negative control: the Bitcoin section, which prints each of its readings
  once, still carries BTC REGIME and its Vol field -- so the "Vol:" check
  above can find a field when one is there.

The decision object is not changed: bias.regime and bias.volatility stay in it
and in the record (the golden snapshot pins both). Fixture-free, per
run_tests.py; nothing here needs pandas_ta.
"""

import re

ANSI = re.compile(r"\x1b\[[0-9;]*m")

REGIME_SENTINEL = "SENTINEL BIAS REGIME"
VOL_SENTINEL = "SENTINEL VOLATILITY"


def _decision():
    return {
        "symbol": "TESTUSDT", "timeframe": "4h", "macro_bias": "BULLISH",
        "bias": {"raw": "BULLISH", "detailed": "BULLISH CONFIRMED",
                 "regime": REGIME_SENTINEL, "volatility": VOL_SENTINEL},
        "trend": {},
        "structure": {"regime": "BULLISH TREND",
                      "sequence": "BULLISH SWING SEQUENCE (HH-HL)",
                      "volume_sentiment": "BULLISH VOLUME SUPPORT"},
        "entry": {"entry_status": "NEAR ZONE"},
        "risk": {"validation_state": "NEUTRAL", "risk_regime": "HIGH VOLATILITY RISK"},
        "exit": {"action": "WAIT"},
        "exit_watch": [],
        "btc_context": {"available": True, "detailed": "BEARISH",
                        "regime": "BEARISH TREND", "volatility": "LOW VOLATILITY",
                        "broad_market_stress": False},
    }


def _render():
    from core.panel_render import render_panel
    panel = render_panel(_decision())
    assert isinstance(panel, str), "render_panel returned no panel"
    return ANSI.sub("", panel)


def _lines(panel):
    return [ln.strip() for ln in panel.splitlines()]


def _asset_readings(panel):
    """The panel's lines before the Bitcoin section: the asset's own."""
    head = panel.split("BTC Market Context", 1)
    assert len(head) == 2, "the Bitcoin section is missing, so the split proves nothing"
    return _lines(head[0])


def test_no_line_is_headed_regime():
    panel = _render()
    headed = [ln for ln in _lines(panel) if ln.startswith("REGIME")]
    assert headed == [], headed
    assert REGIME_SENTINEL not in panel, [
        ln for ln in _lines(panel) if REGIME_SENTINEL in ln]


def test_structure_prints_the_regime_at_its_source():
    panel = _render()
    structure = [ln for ln in _lines(panel) if ln.startswith("STRUCTURE")]
    assert structure == ["STRUCTURE  : BULLISH TREND"], structure


def test_volatility_is_printed_once_on_its_own_line():
    panel = _render()
    carrying = [ln for ln in _lines(panel) if VOL_SENTINEL in ln]
    assert carrying == [f"VOLATILITY : {VOL_SENTINEL}"], carrying


def test_no_asset_reading_carries_a_vol_field():
    fields = [ln for ln in _asset_readings(_render()) if "Vol:" in ln]
    assert fields == [], fields


def test_negative_control_bitcoin_keeps_its_vol_field():
    panel = _render()
    btc = [ln for ln in _lines(panel) if ln.startswith("BTC REGIME")]
    assert btc == ["BTC REGIME    : BEARISH TREND | Vol: LOW VOLATILITY"], btc
    assert "Vol:" in panel
