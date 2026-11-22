"""
The redesign's stage 3, 15 November 2026 -- gates 6 to 8 of the draft's
ladder (docs/redesign_entry53_draft.md, sections 4 and 5).

    6  LONG only: the daily trend is not BEARISH     NO-TRADE (MACRO AGAINST)
    7  the liquidity floor, 10,000 USDT a candle     NO-TRADE (THIN MARKET)
    8  the trigger, and its volume                   WAIT

THE RULINGS, Viktor's. Gate 6: 25 October 2026, point 3 -- no LONG while the
daily trend is bearish. Gate 7 and the trigger's volume: 31 October 2026.
The trigger itself -- the decision candle closes beyond its open and beyond
the previous candle's close -- and F = 10,000 USDT: 11 November 2026.

WHERE THEY SIT. Gates 6 and 7 are blockers on the confirmation signal's
list (models/entry_model.py), so one place still names every reason a side
is refused; the label is the first gate's, in order, that the side does not
pass. Gate 8 follows the signal in DecisionModel.evaluate() and reads what
models/entry_model.py's read_trigger recorded.

WHAT IS NOT MEASURED IS NOT A READING. A daily trend that is not one of its
three words, a turnover that is not a number, a volume or a median that
could not be read: each blocks -- an absent confirmation is not a
confirmation -- and none is given the label of a market that was measured
and failed. In the engine each is also a degraded run.

Fixture-free, per run_tests.py. The engine-path tests skip without
pandas_ta.
"""

import io
import contextlib
import math
import os
import sys
import tempfile
from decimal import Decimal

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from conftest import REPO_ROOT, fixture
from core.decision_log import FINGERPRINTED_MODULES, module_snapshot
from models import entry_model
from models.decision_model import DecisionModel
from models.entry_model import (LIQUIDITY_FLOOR_USDT, TRIGGER_VOLUME_LOOKBACK,
                                generate_entry_signals, read_trigger,
                                signal_blockers)

UNCONFIRMED = "NO-TRADE (SIGNAL UNCONFIRMED)"
MACRO_AGAINST = "NO-TRADE (MACRO AGAINST)"
THIN_MARKET = "NO-TRADE (THIN MARKET)"

MACRO_REASON = ("the daily trend is BEARISH, and no long is taken while the "
                "daily trend is bearish")
NO_TURNOVER = ("the decision candle's turnover in USDT has no valid reading "
               "on this run, so the market cannot be shown to be liquid enough")
UNDER_FLOOR = ("USDT, under the 10000 USDT the engine requires to treat the "
               "market as liquid enough")

PINNED_DIR = os.path.join(REPO_ROOT, "tests", "fixtures", "pinned")
UNREACHABLE = "http://127.0.0.1:9"

SIDES = (("LONG", "long", "BULLISH TREND"), ("SHORT", "short", "BEARISH TREND"))
NOT_AMOUNTS = (None, float("nan"), float("inf"), float("-inf"), -1.0, True,
               False, "50000", [50000.0])


def _blockers(direction, structure, macro="NEUTRAL", quote_volume=50_000.0, adx=30.0):
    return signal_blockers(direction, structure, False, "NONE", adx=adx,
                           macro_bias=macro, quote_volume=quote_volume)


def _signals(structure="BULLISH TREND", macro="NEUTRAL", quote_volume=50_000.0,
             adx=30.0):
    return generate_entry_signals(
        structure_regime=structure, momentum_divergence=False,
        divergence_direction="NONE", adx=adx, macro_bias=macro,
        quote_volume=quote_volume)


TRIGGERED = {"trigger": True, "trigger_volume": 2.0, "trigger_volume_median": 1.0}


def _evaluate(raw="BULLISH", signals=None, trigger=TRIGGERED, risk_valid=True,
              degradation=None, health=90.0, entry_score=80.0):
    """The ladder, the signal gate and gate 8: an AGGRESSIVE trade unless a gate says otherwise."""
    long_plan = raw != "BEARISH"
    if signals is None:
        signals = _signals("BULLISH TREND" if long_plan else "BEARISH TREND")
    # Stage 4, 15 November 2026: AGGRESSIVE reads entry.close_inside_band,
    # not the STATUS word (Viktor's ruling of 7 November). This record said
    # "ACTIVE ENTRY ZONE", which is how the tier used to be reached; the
    # field is what reaches it now, and the word beside it is the one the
    # field prints as. entry_score of 80 is over the upper tiers' line of
    # 70, so every run below is an AGGRESSIVE trade unless a gate says
    # otherwise -- which is what this helper is for.
    entry = {"score": entry_score, "close_inside_band": True,
             "entry_status": "INSIDE THE BAND",
             **signals, **(trigger or {})}
    return DecisionModel().evaluate(
        # The redesign's stage 5, 15 November 2026: `trend` was the second
        # positional parameter and is gone -- _compute_trade_quality was
        # its last reader in the decision model. The `score` this bias
        # dict carried and the `validation_state` in the risk dict are
        # gone with it: neither is a field the engine writes now.
        bias={"raw": raw},
        entry=entry,
        risk={"risk_valid": risk_valid, "risk_reason": "the stop is too far",
              "risk_regime": "NORMAL RISK",
              "targets": [1.1, 1.2, 1.3] if long_plan else [0.9, 0.8, 0.7]},
        degradation=degradation,
    )


# ============================================================
# 1. The constants
# ============================================================

def test_the_floor_and_the_lookback_are_the_ruled_values_and_in_the_run_hash():
    assert LIQUIDITY_FLOOR_USDT == 10000.0
    assert TRIGGER_VOLUME_LOOKBACK == 20
    snapshot = module_snapshot()["models.entry_model"]
    for name, value in (("LIQUIDITY_FLOOR_USDT", 10000.0),
                        ("TRIGGER_VOLUME_LOOKBACK", 20)):
        assert name in FINGERPRINTED_MODULES["models.entry_model"], (
            f"{name} decides which runs may trade and must be in the "
            f"run-hash payload")
        assert snapshot[name] == value, (name, snapshot[name])


# ============================================================
# 2. Gate 6 -- no LONG while the daily trend is bearish
# ============================================================

def test_gate_6_over_every_macro_value_against_both_sides():
    """
    Entry 14's test (the draft's section 3.2): the three words, and values
    that are none of them, against LONG and SHORT. Entry 14's defect was a
    macro value falling silently into one branch.
    """
    # LONG: the three readings.
    assert _blockers("LONG", "BULLISH TREND", macro="BULLISH") == []
    assert _blockers("LONG", "BULLISH TREND", macro="NEUTRAL") == []
    assert _blockers("LONG", "BULLISH TREND", macro="BEARISH") == [MACRO_REASON]
    assert _signals(macro="BEARISH")["long_signal_refusal"] == MACRO_AGAINST

    # LONG: a value that is not a reading is neither passed nor called bearish.
    for not_a_reading in ("", "LONG", "SHORT", "bearish", "UNKNOWN", None, 0, True):
        blockers = _blockers("LONG", "BULLISH TREND", macro=not_a_reading)
        assert blockers == [
            f"the daily trend was recorded as {not_a_reading!r}, which is not "
            "BULLISH, BEARISH or NEUTRAL, so it cannot be shown not to be "
            "bearish"], (not_a_reading, blockers)
        out = _signals(macro=not_a_reading)
        assert out["long_signal"] is False
        assert out["long_signal_refusal"] == UNCONFIRMED, (
            f"a daily trend recorded as {not_a_reading!r} was given the label "
            f"{out['long_signal_refusal']}; nobody measured it as bearish")

    # SHORT is not gated by macro, whatever the value.
    for macro in ("BULLISH", "BEARISH", "NEUTRAL", "", "LONG", None):
        assert _blockers("SHORT", "BEARISH TREND", macro=macro) == [], macro
        out = _signals(structure="BEARISH TREND", macro=macro)
        assert out["short_signal"] is True and out["short_signal_refusal"] is None, macro


def test_gate_6_is_written_in_one_vocabulary():
    """The side's word is never compared with macro's: a LONG under macro "LONG" is not passed."""
    assert _blockers("LONG", "BULLISH TREND", macro="LONG") != []
    assert _blockers("LONG", "BULLISH TREND", macro="SHORT") != []


# ============================================================
# 3. Gate 7 -- the liquidity floor
# ============================================================

def test_the_floor_passes_at_f_and_blocks_both_sides_under_it():
    for direction, key, structure in SIDES:
        assert _blockers(direction, structure, quote_volume=LIQUIDITY_FLOOR_USDT) == []
        assert _blockers(direction, structure, quote_volume=1e12) == []
        for under in (LIQUIDITY_FLOOR_USDT - 1e-9, 9999.5, 7431.0, 0.0):
            blockers = _blockers(direction, structure, quote_volume=under)
            assert len(blockers) == 1 and blockers[0].endswith(UNDER_FLOOR), (
                direction, under, blockers)
            out = _signals(structure=structure, quote_volume=under)
            assert out[f"{key}_signal"] is False
            assert out[f"{key}_signal_refusal"] == THIN_MARKET, (direction, under, out)


def test_the_printed_turnover_never_reads_as_the_floor():
    """
    Entry 58's rule, at this line: a turnover under F is printed under F.
    9999.999999999 must not read "10000 USDT, under the 10000".
    """
    prefix = "the decision candle's turnover was "
    for under in (LIQUIDITY_FLOOR_USDT - 1e-9, LIQUIDITY_FLOOR_USDT - 0.005,
                  LIQUIDITY_FLOOR_USDT - 0.5, 9999.994, 9999.4, 7431.0, 0.0):
        (blocker,) = _blockers("LONG", "BULLISH TREND", quote_volume=under)
        assert blocker.startswith(prefix), blocker
        printed = blocker[len(prefix):].split(" USDT")[0]
        assert Decimal(printed) < Decimal("10000"), (under, printed)
    (blocker,) = _blockers("LONG", "BULLISH TREND", quote_volume=7431.0)
    assert blocker == f"{prefix}7431 {UNDER_FLOOR}", blocker


def test_a_turnover_that_was_not_measured_blocks_and_is_not_called_thin():
    """
    The draft's section 5, version 1: an absent quote_volume is a missing
    input, not a thin market. It is not computed from volume x close either.
    """
    for direction, key, structure in SIDES:
        for not_measured in NOT_AMOUNTS:
            blockers = _blockers(direction, structure, quote_volume=not_measured)
            assert blockers == [NO_TURNOVER], (direction, not_measured, blockers)
            out = _signals(structure=structure, quote_volume=not_measured)
            assert out[f"{key}_signal"] is False
            assert out[f"{key}_signal_refusal"] == UNCONFIRMED, (
                f"a turnover of {not_measured!r} was labelled "
                f"{out[f'{key}_signal_refusal']}")


def test_a_call_without_gate_6_or_gate_7_s_input_is_refused():
    """No default: a call that leaves one out is not read as a market that passed."""
    with pytest.raises(TypeError):
        signal_blockers("LONG", "BULLISH TREND", False, "NONE", adx=30.0,
                        quote_volume=50_000.0)
    with pytest.raises(TypeError):
        signal_blockers("LONG", "BULLISH TREND", False, "NONE", adx=30.0,
                        macro_bias="NEUTRAL")
    with pytest.raises(TypeError):
        generate_entry_signals(structure_regime="BULLISH TREND",
                               momentum_divergence=False,
                               divergence_direction="NONE", adx=30.0)
    # The control: with both, the call is accepted.
    assert _blockers("LONG", "BULLISH TREND") == []


# ============================================================
# 4. The label is the first gate's, and the list has every reason
# ============================================================

def test_the_label_is_the_first_gate_that_fails_and_every_reason_is_listed():
    structure_reason = "structure is BEARISH TREND, not BULLISH TREND"

    all_three = _signals(structure="BEARISH TREND", macro="BEARISH", quote_volume=5.0)
    assert all_three["long_signal_refusal"] == UNCONFIRMED
    assert all_three["long_signal_blockers"][:2] == [structure_reason, MACRO_REASON]
    assert all_three["long_signal_blockers"][2].endswith(UNDER_FLOOR)
    assert len(all_three["long_signal_blockers"]) == 3

    macro_and_thin = _signals(macro="BEARISH", quote_volume=5.0)
    assert macro_and_thin["long_signal_refusal"] == MACRO_AGAINST
    assert len(macro_and_thin["long_signal_blockers"]) == 2

    thin_only = _signals(quote_volume=5.0)
    assert thin_only["long_signal_refusal"] == THIN_MARKET
    assert len(thin_only["long_signal_blockers"]) == 1

    low_adx_and_thin = _signals(adx=15.0, quote_volume=5.0)
    assert low_adx_and_thin["long_signal_refusal"] == UNCONFIRMED

    # A gate that was not measured comes before a later one that failed.
    unread_macro_and_thin = _signals(macro=None, quote_volume=5.0)
    assert unread_macro_and_thin["long_signal_refusal"] == UNCONFIRMED


def test_each_side_s_signal_is_an_empty_list_and_no_label():
    for kwargs in ({}, {"macro": "BEARISH"}, {"macro": "BULLISH"}, {"macro": None},
                   {"quote_volume": 5.0}, {"quote_volume": None},
                   {"structure": "BEARISH TREND"}, {"adx": 15.0},
                   {"structure": "BEARISH TREND", "macro": "BEARISH", "quote_volume": 5.0}):
        out = _signals(**kwargs)
        for side in ("long", "short"):
            empty = out[f"{side}_signal_blockers"] == []
            assert out[f"{side}_signal"] is empty, (kwargs, side)
            assert (out[f"{side}_signal_refusal"] is None) is empty, (kwargs, side)
            if not empty:
                assert out[f"{side}_signal_refusal"] in entry_model.REFUSAL_LABELS


# ============================================================
# 5. The signal gate in DecisionModel.evaluate()
# ============================================================

def test_the_control_every_gate_passing_is_a_trade_on_both_sides():
    """Without it, every refusal below would pass on a model that refused everything."""
    long_out = _evaluate()
    assert long_out["final_action"] == "AGGRESSIVE LONG", long_out["explanation"]
    short_out = _evaluate(raw="BEARISH")
    assert short_out["final_action"] == "AGGRESSIVE SHORT", short_out["explanation"]
    for out, side, beyond in ((long_out, "long", "above"), (short_out, "short", "below")):
        assert (f"The last closed candle is a resumption candle for the {side}: "
                f"it closed {beyond} both its open and the previous candle's "
                f"close, on volume above the median of the 20 candles before "
                f"it.") in out["explanation"]["reasons"], out["explanation"]


def test_a_long_under_a_bearish_daily_trend_is_macro_against_and_says_why():
    out = _evaluate(signals=_signals(macro="BEARISH"))
    assert out["final_action"] == MACRO_AGAINST
    # Stage 4: it read "This would have been AGGRESSIVE LONG, but ...".
    # The tier is derived at gate 9, after this gate, so there is no tier
    # here to name -- the wording follows gate 8's, which stage 3 wrote for
    # the same reason.
    reason = (f"No earlier gate refused the long, but {MACRO_REASON}, so no "
              f"trade is taken.")
    assert reason in out["explanation"]["reasons"]
    assert out["explanation"]["summary"] == f"{MACRO_AGAINST} — {reason}"
    assert not any("structural confirmation" in r
                   for r in out["explanation"]["reasons"]), (
        "structure, ADX and divergence all passed; the sentence must not "
        "say the bias lacked structural confirmation")


def test_a_short_under_any_daily_trend_is_not_gated_by_it():
    for macro in ("BULLISH", "BEARISH", "NEUTRAL"):
        out = _evaluate(raw="BEARISH",
                        signals=_signals(structure="BEARISH TREND", macro=macro))
        assert out["final_action"] == "AGGRESSIVE SHORT", (macro, out["explanation"])


def test_a_thin_market_refuses_both_sides_and_says_why():
    for raw, structure, side in (("BULLISH", "BULLISH TREND", "long"),
                                 ("BEARISH", "BEARISH TREND", "short")):
        out = _evaluate(raw=raw, signals=_signals(structure=structure, quote_volume=7431.0))
        assert out["final_action"] == THIN_MARKET, (raw, out["explanation"])
        # Stage 4: the sentence named the tier the old ladder had chosen.
        reason = (f"No earlier gate refused the {side}, but the decision "
                  f"candle's turnover was 7431 {UNDER_FLOOR}, so no trade "
                  f"is taken.")
        assert out["explanation"]["summary"] == f"{THIN_MARKET} — {reason}"


def test_structure_failing_too_keeps_the_signal_label_and_lists_gate_6_and_7():
    out = _evaluate(signals=_signals(structure="BEARISH TREND", macro="BEARISH",
                                     quote_volume=7431.0))
    assert out["final_action"] == UNCONFIRMED
    summary = out["explanation"]["summary"]
    assert summary.startswith(
        f"{UNCONFIRMED} — No earlier gate refused the long, but the bullish "
        f"bias lacks structural confirmation (structure is BEARISH TREND, "
        f"not BULLISH TREND; "), summary
    assert MACRO_REASON in summary and UNDER_FLOOR in summary, summary


def test_a_label_the_model_does_not_know_is_not_believed():
    """
    Fails safe to SIGNAL UNCONFIRMED: an absent label (a record written
    before this stage), a label that names a side, or one invented.
    """
    for forged in ("AGGRESSIVE LONG", "LONG", "WAIT", "NO-TRADE (SOMETHING ELSE)",
                   None, 7, ["NO-TRADE (THIN MARKET)"]):
        signals = _signals(quote_volume=5.0)
        signals["long_signal_refusal"] = forged
        out = _evaluate(signals=signals)
        assert out["final_action"] == UNCONFIRMED, (forged, out["final_action"])
    signals = _signals(quote_volume=5.0)
    del signals["long_signal_refusal"]
    assert _evaluate(signals=signals)["final_action"] == UNCONFIRMED


def test_a_label_cannot_confirm_a_side_its_blockers_refuse_or_refuse_one_they_pass():
    """The label is read only for a side the signal did not confirm."""
    confirmed = _signals()
    confirmed["long_signal_refusal"] = THIN_MARKET
    assert _evaluate(signals=confirmed)["final_action"] == "AGGRESSIVE LONG"


def test_a_risk_refusal_keeps_its_label_and_records_gate_6_beside_it():
    """Viktor's priority ruling of 21 September (work order F): risk first, both in the log."""
    out = _evaluate(risk_valid=False, signals=_signals(macro="BEARISH"))
    assert out["final_action"] == "NO-TRADE (RISK TOO HIGH)"
    reasons = out["explanation"]["reasons"]
    assert reasons[0].startswith("Risk check failed")
    assert reasons[1] == (
        f"Separately, the long would also have been refused ({MACRO_REASON}). "
        f"The risk refusal is the label; this is recorded so the log shows "
        f"both failures.")
    assert out["explanation"]["summary"].startswith(
        "NO-TRADE (RISK TOO HIGH) — Risk check failed")


def test_a_degraded_run_keeps_gate_6_s_refusal_as_its_label():
    out = _evaluate(signals=_signals(macro="BEARISH"), degradation=["RSI unavailable"])
    assert out["final_action"] == MACRO_AGAINST
    assert any("DEGRADED" in r for r in out["explanation"]["reasons"])


# ============================================================
# 6. Gate 8 -- read_trigger
# ============================================================

def _volumes(n=TRIGGER_VOLUME_LOOKBACK, value=100.0):
    return [value] * n


_TWENTY = object()


def _trigger(side="LONG", open_price=1.00, close_price=1.02, previous_close=1.01,
             volume=150.0, previous_volumes=_TWENTY):
    return read_trigger(
        side, open_price=open_price, close_price=close_price,
        previous_close=previous_close, volume=volume,
        previous_volumes=_volumes() if previous_volumes is _TWENTY else previous_volumes)


def test_the_trigger_is_a_close_beyond_the_open_and_the_previous_close():
    # LONG: above both, strictly.
    assert _trigger("LONG", 1.00, 1.02, 1.01)["trigger"] is True
    assert _trigger("LONG", 1.00, 1.02, 1.03)["trigger"] is False   # above the open only
    assert _trigger("LONG", 1.03, 1.02, 1.01)["trigger"] is False   # above the previous close only
    assert _trigger("LONG", 1.02, 1.02, 1.01)["trigger"] is False   # equal to the open
    assert _trigger("LONG", 1.00, 1.02, 1.02)["trigger"] is False   # equal to the previous close
    assert _trigger("LONG", 1.03, 1.02, 1.04)["trigger"] is False
    # SHORT: the mirror.
    assert _trigger("SHORT", 1.03, 1.01, 1.02)["trigger"] is True
    assert _trigger("SHORT", 1.03, 1.01, 1.00)["trigger"] is False
    assert _trigger("SHORT", 1.00, 1.01, 1.02)["trigger"] is False
    assert _trigger("SHORT", 1.01, 1.01, 1.02)["trigger"] is False
    assert _trigger("SHORT", 1.03, 1.01, 1.01)["trigger"] is False
    # One candle cannot be a trigger for both sides.
    for prices in ((1.00, 1.02, 1.01), (1.03, 1.01, 1.02), (1.0, 1.0, 1.0)):
        both = [_trigger(side, *prices)["trigger"] for side in ("LONG", "SHORT")]
        assert both.count(True) <= 1, (prices, both)


def test_with_no_side_there_is_no_trigger_and_nothing_is_missing():
    out = _trigger(None)
    assert out["trigger"] is None
    assert out["not_measured"] == []
    assert out["trigger_volume"] == 150.0 and out["trigger_volume_median"] == 100.0


def test_a_side_that_is_not_a_side_is_refused():
    for bad in ("BULLISH", "long", "", "NEUTRAL", 1):
        with pytest.raises(ValueError):
            _trigger(bad)


def test_the_median_is_of_the_twenty_candles_before_and_no_others():
    # Twenty values: the median is the mean of the tenth and eleventh.
    earlier = [float(v) for v in range(1, 21)]
    assert _trigger(previous_volumes=earlier)["trigger_volume_median"] == 10.5
    # Order does not matter, and only the last twenty are read.
    shuffled = earlier[::2] + earlier[1::2]
    assert _trigger(previous_volumes=shuffled)["trigger_volume_median"] == 10.5
    longer = [1e9] * 30 + earlier
    assert _trigger(previous_volumes=longer)["trigger_volume_median"] == 10.5
    # The decision candle's own volume is not in its own median.
    assert _trigger(volume=1e9, previous_volumes=earlier)["trigger_volume_median"] == 10.5


def test_the_golden_run_s_figures_from_the_golden_test_s_own_series():
    """
    The draft's section 13.1, gate 8, recomputed from the golden test's own
    4h series (tests/test_golden_path.py, _write_pinned_set) and not from
    tests/fixtures/pinned: the decision candle closed at 0.80173175, under
    its open and the previous close, both 0.80634644, on a volume of
    84,693.7281 against a median of 179,247.8923; its turnover is
    67,901.6508 USDT and the series' smallest 10,650.0211. This time the
    draft's figures are the golden run's.
    """
    pd = pytest.importorskip("pandas")
    from test_golden_path import SYMBOL, TIMEFRAME, _write_pinned_set

    with tempfile.TemporaryDirectory() as tmp:
        _write_pinned_set(tmp)
        series = pd.read_csv(os.path.join(tmp, f"{SYMBOL}_{TIMEFRAME}.csv"))

    last, previous = series.iloc[-1], series.iloc[-2]
    assert (float(last["open"]), float(last["close"]), float(previous["close"])) == (
        0.80634644, 0.80173175, 0.80634644)
    out = read_trigger(
        "LONG", open_price=float(last["open"]), close_price=float(last["close"]),
        previous_close=float(previous["close"]), volume=float(last["volume"]),
        previous_volumes=[float(v) for v in series["volume"].iloc[:-1]])
    assert out == {"trigger": False, "trigger_volume": 84693.7281,
                   "trigger_volume_median": 179247.8923, "not_measured": []}
    assert float(last["quote_volume"]) == 67901.6508
    assert float(series["quote_volume"].min()) == 10650.0211
    assert float(series["quote_volume"].min()) >= LIQUIDITY_FLOOR_USDT


def test_a_volume_that_was_not_measured_is_named_and_never_compared():
    """
    Entry 19's lesson carried forward (the draft's section 3.2): an absent or
    non-finite volume, or fewer than twenty readable candles before it, is
    not measured. It is never compared as though it were the median.
    """
    for bad in NOT_AMOUNTS:
        out = _trigger(volume=bad)
        assert out["trigger_volume"] is None, bad
        assert out["not_measured"] == ["the decision candle's volume"], (bad, out)

    window = "the volume of the 20 candles before the decision candle"
    for earlier in ([], _volumes(19), [100.0] * 19 + [float("nan")],
                    [None] + [100.0] * 19, [100.0] * 10 + [-1.0] + [100.0] * 9,
                    None, 7):
        out = _trigger(previous_volumes=earlier)
        assert out["trigger_volume_median"] is None, earlier
        assert out["not_measured"] == [window], (earlier, out)

    # A zero is a reading; nineteen readable candles and an unreadable one
    # further back than twenty is a full window.
    assert _trigger(volume=0.0)["trigger_volume"] == 0.0
    assert _trigger(previous_volumes=[float("nan")] + _volumes())["not_measured"] == []


def test_a_price_that_was_not_measured_is_named_and_gives_no_trigger():
    names = {"open_price": "the decision candle's open",
             "close_price": "the decision candle's close",
             "previous_close": "the previous candle's close"}
    for parameter, name in names.items():
        for bad in (None, float("nan"), float("inf"), True, "1.0"):
            for side in ("LONG", "SHORT", None):
                out = _trigger(side, **{parameter: bad})
                assert out["trigger"] is None, (parameter, bad, side)
                assert out["not_measured"] == [name], (parameter, bad, side, out)


# ============================================================
# 7. Gate 8 in DecisionModel.evaluate()
# ============================================================

def _trig(trigger=True, volume=150.0, median=100.0):
    return {"trigger": trigger, "trigger_volume": volume,
            "trigger_volume_median": median}


def test_no_resumption_candle_is_a_wait_and_the_sentence_names_what_failed():
    head = "No earlier gate refused the long, but there is no resumption candle yet: "
    price = ("the last closed candle did not close above both its open and "
             "the previous candle's close")
    volume = "its volume, 84694, is not above the median of the 20 candles before it, 179247.8923"

    cases = ((_trig(False, 150.0, 100.0), f"{head}{price} — WAIT."),
             (_trig(True, 84693.7281, 179247.8923), f"{head}{volume} — WAIT."),
             (_trig(False, 84693.7281, 179247.8923), f"{head}{price}, and {volume} — WAIT."))
    for trigger, sentence in cases:
        out = _evaluate(trigger=trigger)
        assert out["final_action"] == "WAIT", (trigger, out["explanation"])
        assert out["explanation"]["summary"] == f"WAIT — {sentence}", out["explanation"]

    short = _evaluate(raw="BEARISH", trigger=_trig(False))
    assert short["final_action"] == "WAIT"
    assert ("No earlier gate refused the short, but there is no resumption "
            "candle yet: the last closed candle did not close below both its "
            "open and the previous candle's close — WAIT.") in short["explanation"]["reasons"]


def test_the_trigger_s_volume_must_be_strictly_above_the_median():
    assert _evaluate(trigger=_trig(True, 100.0, 100.0))["final_action"] == "WAIT"
    assert _evaluate(trigger=_trig(True, 99.999, 100.0))["final_action"] == "WAIT"
    assert _evaluate(trigger=_trig(True, 100.001, 100.0))["final_action"] == "AGGRESSIVE LONG"
    assert _evaluate(trigger=_trig(True, 0.0, 0.0))["final_action"] == "WAIT"


def test_the_printed_volume_is_on_its_own_side_of_the_median():
    """
    Entry 58's rule, where the line is data: the median is printed exactly,
    and the volume under it never prints as it or over it.
    """
    for volume, median in ((100.0035, 100.004), (179247.89, 179247.8923),
                           (99.5, 100.0), (99.9999, 100.0), (0.0, 0.5),
                           (123456.789, 123456.7891)):
        out = _evaluate(trigger=_trig(True, volume, median))
        (sentence,) = [r for r in out["explanation"]["reasons"]
                       if "no resumption candle yet" in r]
        printed = sentence.split("its volume, ")[1].split(",")[0]
        printed_median = sentence.split("candles before it, ")[1].split(" — WAIT.")[0]
        assert Decimal(printed_median) == Decimal(repr(median)), (median, printed_median)
        assert Decimal(printed) < Decimal(printed_median), (volume, median, sentence)
    # Equal: both print exactly, as the same number.
    out = _evaluate(trigger=_trig(True, 100.123456, 100.123456))
    assert ("its volume, 100.123456, is not above the median of the 20 "
            "candles before it, 100.123456") in out["explanation"]["summary"]


def test_a_trigger_that_was_not_measured_is_not_a_trigger():
    """
    Fails safe, with its own sentence: never a trade, and never the sentence
    of a candle that was read and did not resume.
    """
    not_measured = ("No earlier gate refused the long, but the trigger was not "
                    "measured on this run")
    cases = [None, {}, _trig(None), _trig("yes"), _trig(1), _trig(0),
             _trig(True, None, 100.0), _trig(True, 150.0, None),
             _trig(True, float("nan"), 100.0), _trig(True, 150.0, float("inf")),
             _trig(True, True, 100.0), _trig(True, "150", 100.0),
             _trig(True, -1.0, 100.0),
             {"trigger": True}, {"trigger_volume": 150.0, "trigger_volume_median": 100.0}]
    for trigger in cases:
        out = _evaluate(trigger=trigger)
        assert out["final_action"] == "WAIT", (trigger, out["final_action"])
        assert out["explanation"]["summary"].startswith(f"WAIT — {not_measured}"), (
            trigger, out["explanation"]["summary"])
        assert not any("no resumption candle yet" in r
                       for r in out["explanation"]["reasons"]), trigger


def test_an_earlier_gate_s_refusal_stays_the_label():
    """Gate 8 comes after gates 1 to 7: it does not turn their NO-TRADE into a WAIT."""
    no_trigger = _trig(False, 1.0, 2.0)
    assert _evaluate(signals=_signals(structure="BEARISH TREND"),
                     trigger=no_trigger)["final_action"] == UNCONFIRMED
    assert _evaluate(signals=_signals(macro="BEARISH"),
                     trigger=no_trigger)["final_action"] == MACRO_AGAINST
    assert _evaluate(signals=_signals(quote_volume=5.0),
                     trigger=no_trigger)["final_action"] == THIN_MARKET
    risk = _evaluate(risk_valid=False, trigger=no_trigger)
    assert risk["final_action"] == "NO-TRADE (RISK TOO HIGH)"
    for out in (risk, _evaluate(signals=_signals(quote_volume=5.0), trigger=no_trigger)):
        assert not any("resumption candle" in r for r in out["explanation"]["reasons"])


def test_gate_8_is_silent_when_no_side_reached_it():
    neutral = _evaluate(raw="NEUTRAL", trigger=_trig(None, 150.0, 100.0))
    assert neutral["final_action"] == "WAIT"
    assert neutral["explanation"]["summary"].startswith("WAIT — The direction is NEUTRAL")
    assert not any("trigger" in r or "resumption" in r
                   for r in neutral["explanation"]["reasons"])
    # Stage 4: the ladder's other WAIT -- trend strength under the
    # CONSERVATIVE line -- is gone, because the tier no longer reads trend
    # health at all. Gate 2's is the only WAIT before gate 8 now. A low
    # entry quality waits at gate 9, which runs AFTER gate 8, so there gate
    # 8 does run and does say it passed; what must not happen is the
    # quality's WAIT being attributed to the trigger.
    weak = _evaluate(entry_score=45.0)
    assert weak["final_action"] == "WAIT"
    assert "not at a pullback to the average" in weak["explanation"]["summary"], (
        weak["explanation"]["summary"])
    assert not any("no resumption candle yet" in r
                   for r in weak["explanation"]["reasons"])


def test_a_degraded_run_with_no_resumption_candle_stays_a_wait():
    out = _evaluate(trigger=_trig(False), degradation=["RSI unavailable"])
    assert out["final_action"] == "WAIT"
    assert "no resumption candle yet" in out["explanation"]["summary"]
    assert any("DEGRADED" in r for r in out["explanation"]["reasons"])
    # And one whose trigger held is refused by the degradation, as before.
    held = _evaluate(degradation=["RSI unavailable"])
    assert held["final_action"] == "NO-TRADE (DEGRADED INPUT)"


def test_the_decision_model_reads_the_trigger_and_does_not_compute_it():
    """It takes no candle: the readings are models/entry_model.py's, recorded in `entry`."""
    import inspect
    parameters = set(inspect.signature(DecisionModel._apply_trigger_gate).parameters)
    assert parameters == {"self", "final_action", "entry", "reasons"}, parameters


# ============================================================
# 8. The panel
# ============================================================

def _panel(entry_extra, raw="BULLISH"):
    from core.panel_render import render_panel
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import json
    with open(os.path.join(REPO_ROOT, "tests", "fixtures", "golden_decision.json"),
              encoding="utf-8") as f:
        decision = json.load(f)
    decision["entry"].update(entry_extra)
    decision["bias"]["raw"] = raw
    with contextlib.redirect_stdout(io.StringIO()):
        panel = render_panel(decision)
    assert isinstance(panel, str), "render_panel returned no panel"
    return [line for line in panel.splitlines()
            if line.startswith(("TURNOVER", "TRIGGER"))]


def test_the_panel_prints_what_gates_7_and_8_read():
    assert _panel({"quote_volume": 67901.6508, "liquidity_floor": 10000.0,
                   "trigger": False, "trigger_volume": 84693.7281,
                   "trigger_volume_median": 179247.8923}) == [
        "TURNOVER      : 67902 USDT on the decision candle (floor 10000)",
        "TRIGGER       : NO -- the candle did not close beyond its open and the previous close",
        "TRIGGER VOLUME: 84694 against a median of 179247.8923 before it -- not above it",
    ]
    assert _panel({"quote_volume": 9999.999, "liquidity_floor": 10000.0,
                   "trigger": True, "trigger_volume": 200.0,
                   "trigger_volume_median": 100.5}) == [
        "TURNOVER      : 9999.99 USDT on the decision candle (floor 10000) -- UNDER THE FLOOR",
        "TRIGGER       : YES -- the candle closed beyond its open and the previous close",
        "TRIGGER VOLUME: 200 against a median of 100.5 before it -- above it",
    ]


def test_the_panel_says_not_measured_and_no_side_and_never_a_number():
    absent = {"quote_volume": None, "liquidity_floor": 10000.0, "trigger": None,
              "trigger_volume": None, "trigger_volume_median": None}
    assert _panel(absent) == [
        "TURNOVER      : not measured",
        "TRIGGER       : not measured",
        "TRIGGER VOLUME: not measured",
    ]
    assert _panel(dict(absent, trigger_volume=150.0, trigger_volume_median=100.0),
                  raw="NEUTRAL") == [
        "TURNOVER      : not measured",
        "TRIGGER       : not read -- no side to read it for",
        "TRIGGER VOLUME: 150 against a median of 100.0 before it -- above it",
    ]


# ============================================================
# 9. The engine path
# ============================================================

def _route_pinned(directory, symbol="AEROUSDT"):
    from core import config
    from data.data_fetcher import DataFetcher, data_fetcher
    from models.signal_router import SignalRouter

    work = tempfile.mkdtemp(prefix="phase7_gates_")
    original_url = data_fetcher.base_url
    original_log, original_chart = config.LOG_DIR, config.CHART_DIR
    try:
        config.LOG_DIR = os.path.join(work, "logs")
        config.CHART_DIR = os.path.join(work, "logs", "charts")
        data_fetcher.base_url = UNREACHABLE
        DataFetcher.set_pinned_source(directory)
        with contextlib.redirect_stdout(io.StringIO()):
            return SignalRouter().route(symbol=symbol, timeframe="4h")
    finally:
        DataFetcher.clear_pinned_source()
        data_fetcher.base_url = original_url
        config.LOG_DIR, config.CHART_DIR = original_log, original_chart
        import shutil
        shutil.rmtree(work, ignore_errors=True)


def _pinned_copy(change):
    """The committed pinned set, with `change` applied to the pair's 4h frame."""
    import pandas as pd
    import shutil

    tmp = tempfile.mkdtemp(prefix="phase7_gates_set_")
    for name in os.listdir(PINNED_DIR):
        if name.endswith(".csv"):
            shutil.copy(os.path.join(PINNED_DIR, name), os.path.join(tmp, name))
    path = os.path.join(tmp, "AEROUSDT_4h.csv")
    frame = change(pd.read_csv(path))
    frame.to_csv(path, index=False)
    return tmp


def test_on_the_engine_path_the_pinned_run_waits_at_gate_8():
    pytest.importorskip("pandas_ta")
    decision = _route_pinned(PINNED_DIR)
    assert not decision.get("error"), decision.get("error")
    assert decision["degradation"]["degraded"] is False, decision["degradation"]

    entry = decision["entry"]
    assert entry["quote_volume"] == 67901.6508
    assert entry["liquidity_floor"] == LIQUIDITY_FLOOR_USDT
    assert entry["trigger"] is False
    assert entry["trigger_volume"] == 84693.7281
    assert entry["trigger_volume_median"] == pytest.approx(179247.8923, abs=1e-9)
    assert entry["long_signal"] is True and entry["long_signal_refusal"] is None
    assert entry["short_signal_refusal"] == UNCONFIRMED
    assert decision["macro_bias"] == "BULLISH"

    assert decision["exit"]["action"] == "WAIT"
    assert decision["explanation"]["summary"] == (
        "WAIT — No earlier gate refused the long, but there is no resumption "
        "candle yet: the last closed candle did not close above both its open "
        "and the previous candle's close, and its volume, 84694, is not above "
        "the median of the 20 candles before it, 179247.8923 — WAIT.")


def test_on_the_engine_path_a_frame_without_quote_volume_degrades_the_run():
    """
    Stage 1's second reading, moved on purpose: until stage 3 an absent
    quote_volume meant nothing. Now it is a missing input -- the run is
    degraded and names it, the turnover is None and not volume x close, and
    gate 7 blocks both sides without calling the market thin.
    """
    pytest.importorskip("pandas_ta")
    import shutil
    tmp = _pinned_copy(lambda frame: frame.drop(columns="quote_volume"))
    try:
        decision = _route_pinned(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    assert not decision.get("error"), decision.get("error")
    assert decision["degradation"]["degraded"] is True
    assert decision["degradation"]["trading_authorized"] is False
    assert [m for m in decision["degradation"]["missing_inputs"]
            if m.startswith("quote_volume ")], decision["degradation"]
    entry = decision["entry"]
    assert entry["quote_volume"] is None
    for side in ("long", "short"):
        assert NO_TURNOVER in entry[f"{side}_signal_blockers"], (side, entry)
        assert entry[f"{side}_signal"] is False
        assert entry[f"{side}_signal_refusal"] == UNCONFIRMED
    action = decision["exit"]["action"]
    assert not any(side in action for side in ("LONG", "SHORT")), action
    assert action != THIN_MARKET
    assert "quote_volume" not in decision["lineage"]["indicators_at_decision_bar"]


def test_on_the_engine_path_a_thin_candle_is_refused_as_a_thin_market():
    """
    The pinned run with its decision candle's turnover set under F. The
    ladder chooses the long, gates 3 to 6 pass, and gate 7 refuses it --
    before gate 8, which would have made it a WAIT.
    """
    pytest.importorskip("pandas_ta")
    import shutil

    def thin(frame):
        frame.loc[frame.index[-1], "quote_volume"] = 7431.0
        return frame

    tmp = _pinned_copy(thin)
    try:
        decision = _route_pinned(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    assert not decision.get("error"), decision.get("error")
    assert decision["degradation"]["degraded"] is False, decision["degradation"]
    assert decision["entry"]["quote_volume"] == 7431.0
    assert decision["entry"]["long_signal_refusal"] == THIN_MARKET
    assert decision["exit"]["action"] == THIN_MARKET, decision["explanation"]
    assert decision["explanation"]["summary"].endswith(
        f"but the decision candle's turnover was 7431 {UNDER_FLOOR}, so no "
        f"trade is taken.")
    assert not any("resumption" in r for r in decision["explanation"]["reasons"])


def test_on_the_engine_path_a_long_under_a_bearish_daily_trend_is_macro_against():
    """
    tests/test_timeframe_disagreement.py's mirror series: a long decline,
    then a sharp rally. The 4h direction is BULLISH and the daily close is
    still under its EMA 50. Until this stage nothing stopped that long but
    its other gates; now gate 6 does, by name.
    """
    pytest.importorskip("pandas_ta")
    import test_timeframe_disagreement as disagreement

    with contextlib.redirect_stdout(io.StringIO()):
        decision = disagreement._run(rising_first=False)
    assert not decision.get("error"), decision.get("error")
    assert decision["degradation"]["degraded"] is False, decision["degradation"]
    assert decision["bias"]["raw"] == "BULLISH" and decision["macro_bias"] == "BEARISH"
    assert MACRO_REASON in decision["entry"]["long_signal_blockers"]
    assert decision["entry"]["long_signal_refusal"] == MACRO_AGAINST
    assert decision["exit"]["action"] == MACRO_AGAINST, decision["explanation"]
    # The mirror: a bearish 4h under a bullish daily trend is not gated by it.
    with contextlib.redirect_stdout(io.StringIO()):
        short_side = disagreement._run(rising_first=True)
    assert short_side["bias"]["raw"] == "BEARISH" and short_side["macro_bias"] == "BULLISH"
    assert not any("daily trend" in b
                   for b in short_side["entry"]["short_signal_blockers"]), short_side["entry"]


def test_engine_core_reads_the_trigger_for_the_direction_s_side_and_no_stand_in():
    """
    Under NEUTRAL the plan is drawn for a stand-in side (stage 2's second
    reading). The trigger is not read for it: engine_core's call takes its
    side from the direction's own two words, and gives None for anything
    else. Read from the parse tree, not asked of a run.
    """
    import ast
    with open(os.path.join(REPO_ROOT, "core", "engine_core.py"), encoding="utf-8") as f:
        tree = ast.parse(f.read())
    assigned = [node for node in ast.walk(tree)
                if isinstance(node, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == "trigger_side"
                        for t in node.targets)]
    assert len(assigned) == 1, "trigger_side is assigned once"
    assert ast.unparse(assigned[0].value) == (
        "{'BULLISH': 'LONG', 'BEARISH': 'SHORT'}.get(raw_bias)")
    calls = [node for node in ast.walk(tree)
             if isinstance(node, ast.Call)
             and ast.unparse(node.func) == "entry_model.read_trigger"]
    assert len(calls) == 1, "one call to read_trigger"
    assert ast.unparse(calls[0].args[0]) == "trigger_side"
