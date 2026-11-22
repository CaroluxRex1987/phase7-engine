"""
The panel's price decimals follow the price.

22 November 2026, by Viktor's ruling of 23:48 on 21 November (DECISIONS,
"Ruling, 21 November 2026 -- BLESSUSDT is run by command until the merge and
made the default by one small commit after it ..."). Every price line printed
four decimals; BLESS is about $0.0138, which four decimals show in three
significant figures. core/panel_render.py's _price_decimals takes the decision
close and gives at least four significant figures, never fewer than four
decimals; every price line of one panel uses it.

No fixtures, so run_tests.py runs these too.
"""

def _panel(close, raw="BULLISH"):
    from core.panel_render import render_panel
    return render_panel({
        "symbol": "BLESSUSDT", "timeframe": "4h",
        "bias": {"raw": raw}, "trend": {},
        "structure": {"swing_struct": close * 0.95},
        "entry": {"zone_lower": close * 0.97, "zone_upper": close * 1.01},
        "risk": {"atr_stop": close * 0.96,
                 "targets": [close * 1.03, close * 1.06, close * 1.09]},
        "exit": {"current_price": close},
        "provenance": {"decision_candles": {"struct": {
            "open_time": "2026-11-21 20:00:00", "live_price": close * 1.002,
            "basis": "live"}}},
    })


def _line(panel, prefix):
    lines = [ln for ln in panel.splitlines() if ln.lstrip().startswith(prefix)]
    assert len(lines) == 1, (prefix, lines)
    return lines[0]


def test_the_decimals_for_a_price():
    from core.panel_render import _price_decimals
    cases = {
        0.0138: 5, 0.01: 5, 0.0999: 5, 0.00123: 6, 0.000456: 7,
        0.1: 4, 0.8082: 4, 1.0: 4, 2500.0: 4, 91000.0: 4,
        -0.0138: 5,
    }
    for price, want in cases.items():
        assert _price_decimals(price) == want, (price, _price_decimals(price), want)


def test_an_absent_or_unusable_reference_gives_four():
    from core.panel_render import _price_decimals
    for ref in (None, "x", float("nan"), float("inf"), 0.0, 0):
        assert _price_decimals(ref) == 4, (ref, _price_decimals(ref))


def test_a_bless_sized_panel_prints_every_price_in_five_decimals():
    panel = _panel(0.0138)
    expected = {
        "DECISION CLOSE": ["$0.01380"],
        "LIVE PRICE": ["$0.01383"],
        "STOP LOSS": ["$0.01325"],
        "TARGET 1": ["$0.01421"],
        "TARGET 2": ["$0.01463"],
        "TARGET 3": ["$0.01504"],
        "SWING STRUCT": ["$0.01311"],
        "EMA BAND": ["$0.01339", "$0.01394"],
    }
    for prefix, prices in expected.items():
        line = _line(panel, prefix)
        for text in prices:
            assert text in line, (prefix, text, line)


def test_a_price_of_ten_cents_or_more_prints_four_decimals_as_before():
    panel = _panel(0.8)
    for prefix, text in (("DECISION CLOSE", "$0.8000"), ("STOP LOSS", "$0.7680"),
                         ("TARGET 1", "$0.8240"), ("LIVE PRICE", "$0.8016")):
        line = _line(panel, prefix)
        assert text in line, (prefix, text, line)
    assert "$0.80000" not in panel


def test_without_a_decision_close_the_prices_print_four_decimals():
    from core.panel_render import render_panel
    panel = render_panel({
        "symbol": "BLESSUSDT", "timeframe": "4h",
        "bias": {"raw": "BULLISH"}, "trend": {}, "structure": {}, "entry": {},
        "risk": {"atr_stop": 0.0132}, "exit": {},
        "provenance": {},
    })
    assert "not available this run" in _line(panel, "DECISION CLOSE")
    assert "$0.0132" in _line(panel, "STOP LOSS")
    assert "$0.01320" not in panel
