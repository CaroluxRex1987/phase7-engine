"""
Audit finding (4) — the entry zone was fabricated when the EMAs were missing.

WHAT WAS WRONG, IN TWO FILES

core/engine_core.py:

    entry_zone_lower = float(EMA_20) if present else close * 0.99
    entry_zone_upper = float(EMA_50) if present else close * 1.01

models/entry_model.py:

    close      = safe_float(..., 1.0)
    zone_lower = safe_float(zone_lower, close * 0.99)
    zone_upper = safe_float(zone_upper, close * 1.01)
    if zone_width <= 1e-8: zone_width = close * 0.01

Five fabricated constants between them. A missing EMA pair became a band one
percent either side of the last price — a number with no relationship to this
instrument or to anything measured — and that band then scored the 30-point
EMA position component AND the 25-point ATR distance component, which measures
distance to this zone. 55 of 100 derived from a constant, printed as an entry
quality score.

The worst of the five is the close-price fallback: a price that could not be
read became $1.00, and every distance, ratio and percentage in the function is
measured against it.

THE ONE THAT WAS NOT ON THE LIST

engine_core put EMA_20 in `lower` and EMA_50 in `upper` unconditionally. In an
uptrend the fast EMA is above the slow one, so the panel printed

    ENTRY ZONE    : $0.4981 - $0.4918

with the lower bound above the upper — seen on the live run at fa68197.
entry_model swaps them before scoring, so the arithmetic was right the whole
time and only the display was wrong. That is why no test caught it and why
reading the panel did.

WHAT REPLACED IT

No zone means NaN, and the run records the missing input.

THE REDESIGN'S STAGE 4, 15 November 2026

The policy this file held changed, and the finding it was written for did
not. Until this stage a missing zone left its two components -- the 30-point
EMA position and the 25-point ATR distance -- at ZONE_POINTS_NOT_MEASURED
and ATR_POINTS_NOT_MEASURED, 15 of 30 and 15 of 25, on this file's own
reasoning since Finding 3: lowering conviction is the degraded flag's job,
and scoring an absence twice makes a degraded run look like a bad setup.
Entry quality is D + H now, and a part whose input is missing is NOT
MEASURED: entry quality is not computed at all, the score is None, and gate
9 reads that as a WAIT with a sentence of its own. So the two constants go
with the two components, and the assertions that read them read None
instead. The fabrications the finding named are still refused, which is what
this file is for, and the status words have changed with STATUS itself (it
is the close's position against the band now, not its distance in band
widths).
"""

import math
import os

import numpy as np
import pandas as pd
import pytest

from conftest import REPO_ROOT

PINNED_DIR = os.path.join(REPO_ROOT, "tests", "fixtures", "pinned")
UNREACHABLE = "http://127.0.0.1:9"


def _frame(close=1.2345, ema20=None, ema50=None, atr=0.01, hvn=None,
           rows=60, **cols):
    """
    Stage 4: `hvn` is new. Entry quality is D + H, so a frame with no HVN
    column leaves H not measured and the whole score None -- which is right,
    and is not what most of the tests below are about. The ones that want a
    score pass one.
    """
    data = {"close": [close] * rows}
    if ema20 is not None:
        data["EMA_20"] = [ema20] * rows
    if ema50 is not None:
        data["EMA_50"] = [ema50] * rows
    if atr is not None:
        data["ATR"] = [atr] * rows
    if hvn is not None:
        data["HVN"] = [hvn] * rows
    data.update({k: [v] * rows for k, v in cols.items()})
    return pd.DataFrame(data)


# ============================================================
# No zone means no zone
# ============================================================

def test_an_absent_zone_is_not_invented_from_the_price():
    """
    The finding itself. NaN bounds must not become close*0.99 / close*1.01.
    """
    from models.entry_model import calculate_entry_quality

    close = 1.2345
    out = calculate_entry_quality(_frame(close=close, hvn=close),
                                  float("nan"), float("nan"))

    assert out["entry_status"] == "ZONE NOT AVAILABLE", (
        f"status is {out['entry_status']!r}. The old code fabricated a band "
        f"one percent either side of {close} and then reported which part of "
        f"it price was in."
    )
    # Stage 4: this read `ema_pos_pts == 15` -- the midpoint of the
    # 30-point component. There is no such component and no such midpoint:
    # the distance part is NOT MEASURED, and with it the whole quality.
    assert out["distance_pts"] is None, (
        f"scored {out['distance_pts']} of 80 for a band that was never "
        f"located. The fabricated band scored 5, 10, 20 or 30 of 30 "
        f"depending on where price happened to sit inside a constant."
    )
    assert out["distance_atr"] is None
    assert out["score"] is None, (
        f"entry quality is {out['score']} with no band to measure the "
        f"close's distance from")
    assert out["close_inside_band"] is None, (
        "a close has no position against a band nobody located")
    assert math.isnan(out["distance_from_zone"]), (
        f"reported a distance of {out['distance_from_zone']} from a zone that "
        f"does not exist"
    )
    # The band's absence is core/engine_core.py's to name -- it computes the
    # band and can say which EMA was missing -- so this function does not
    # name it a second time.
    assert not any("band" in m.lower() or "zone" in m.lower()
                   for m in out["not_measured"]), out["not_measured"]


def test_an_absent_zone_leaves_the_distance_part_not_measured_even_with_an_atr():
    """
    The consequence that is easy to miss: D divides the distance TO THE BAND
    by ATR. No band, no distance to divide, however good the ATR is.

    Stage 4 renamed this from
    test_an_absent_zone_also_stops_the_atr_distance_being_scored, which held
    the same property of the 25-point ATR-distance component. The draft's
    section 14 classified it G, as going with that component; the property
    it tests is D's own and stays. Recorded as one of section 14's
    misclassifications for this stage.
    """
    from models.entry_model import calculate_entry_quality

    out = calculate_entry_quality(_frame(atr=0.01, hvn=1.2345),
                                  float("nan"), float("nan"))

    assert out["distance_pts"] is None, (
        f"distance_pts is {out['distance_pts']} on a run with no band. ATR "
        f"was present, but the distance it scales is a distance to the band."
    )
    # H is measurable here -- it needs the HVN and the ATR, not the band --
    # and it is still measured. The absence is confined to the part that
    # needed the missing input.
    assert out["hvn_pts"] is not None
    assert out["score"] is None, (
        "one part not measured leaves the quality not computed, not the "
        "other part's points reported as the total")


def test_only_one_bound_is_still_no_zone():
    from models.entry_model import calculate_entry_quality

    for lower, upper in ((1.0, float("nan")), (float("nan"), 1.0)):
        out = calculate_entry_quality(_frame(), lower, upper)
        assert out["entry_status"] == "ZONE NOT AVAILABLE", (
            f"bounds ({lower}, {upper}) produced {out['entry_status']!r}. "
            f"Half a zone is not a zone."
        )


def test_a_price_that_could_not_be_read_is_not_one_dollar():
    """
    The fabrication underneath all the others.
    """
    from models.entry_model import calculate_entry_quality

    df = pd.DataFrame({"close": [float("nan")] * 60, "ATR": [0.01] * 60})
    out = calculate_entry_quality(df, 0.99, 1.01)

    assert out["entry_status"] == "NO DATA", (
        f"status is {out['entry_status']!r}. close fell back to 1.0, so a "
        f"zone of 0.99-1.01 read as ACTIVE ENTRY ZONE — a perfect entry, "
        f"scored against a price nobody read."
    )
    # Stage 4: this read `score == 0.0`, the default_response's value. A
    # quality of zero is a real reading -- the golden run's is exactly that
    # -- so it cannot also mean "no price was read". None does.
    assert out["score"] is None
    assert out["distance_atr"] is None and out["hvn_distance_atr"] is None
    assert out["close_inside_band"] is None
    assert any("close" in m for m in out["not_measured"]), out["not_measured"]
    assert math.isnan(out["distance_from_zone"])


def test_two_coincident_averages_are_still_a_band_with_a_position():
    """
    zone_width = close * 0.01 silently re-scaled all three bands, which were
    multiples of that width. That is the finding, and it is still refused.

    Stage 4 renamed this from test_a_zone_with_no_width_is_not_given_one and
    turned its status assertion round. ZONE HAS NO WIDTH existed because the
    three bands were multiples of the width and there was none to multiply.
    STATUS is a position now, and a close has a position against two
    coincident averages exactly as it has against two separated ones: on
    them, above them or below them. So the word goes, and the position is
    asserted instead. The draft's section 14 classified this G under branch
    (a); the property survives the branch, so it is an R. Recorded as one of
    section 14's misclassifications for this stage.
    """
    from models.entry_model import calculate_entry_quality

    on_it = calculate_entry_quality(_frame(close=1.2345, hvn=1.2345, atr=0.1),
                                    1.2345, 1.2345)
    assert on_it["entry_status"] == "INSIDE THE BAND", on_it["entry_status"]
    assert on_it["close_inside_band"] is True
    # The close is ON the band, so its distance from the midpoint is zero
    # and D is full -- which is the width-independent answer. The old code
    # would have banded it against a fabricated width of close * 0.01.
    assert on_it["distance_atr"] == 0.0
    assert on_it["distance_pts"] == 80.0

    above = calculate_entry_quality(_frame(close=1.3, hvn=1.3, atr=0.1),
                                    1.2, 1.2)
    assert above["entry_status"] == "ABOVE THE BAND", above["entry_status"]
    assert above["close_inside_band"] is False

    below = calculate_entry_quality(_frame(close=1.1, hvn=1.1, atr=0.1),
                                    1.2, 1.2)
    assert below["entry_status"] == "BELOW THE BAND", below["entry_status"]
    assert below["close_inside_band"] is False

    for out in (on_it, above, below):
        assert math.isfinite(out["distance_from_zone"]), (
            "distance_from_zone is a real measurement even when the two "
            "averages coincide — it should still be reported"
        )


# Stage 4, 15 November 2026: test_the_not_measured_policy_is_named stood
# here, holding that ZONE_POINTS_NOT_MEASURED and ATR_POINTS_NOT_MEASURED
# were both 15.0, the midpoints of their components. Both constants are
# gone: a part whose input is missing is not measured rather than given a
# neutral value, so there is no policy number left to name. The policy
# itself is held by the two tests above, which assert None.


# ============================================================
# The measured case is untouched
# ============================================================

# Zone 0.9 - 1.1 with ATR 0.1 and the HVN at the midpoint, so every number
# below is a whole or a half ATR and can be checked by hand -- which is the
# reason D and H are straight lines rather than the old exp(-0.5 x ratio)
# decay (the draft's section 3.1).
#
#   d = |close - 1.0| / 0.1          D = 80 x max(0, 1 - d / 3)
#   h = |close - 1.0| / 0.1          H = 20 x max(0, 1 - h / 2)
@pytest.mark.parametrize("close,status,d,D,h,H", [
    (1.00, "INSIDE THE BAND", 0.0, 80.0, 0.0, 20.0),
    (1.10, "INSIDE THE BAND", 1.0, 80.0 * 2 / 3, 1.0, 10.0),
    (1.15, "ABOVE THE BAND", 1.5, 40.0, 1.5, 5.0),
    (0.85, "BELOW THE BAND", 1.5, 40.0, 1.5, 5.0),
    (1.40, "ABOVE THE BAND", 4.0, 0.0, 4.0, 0.0),
])
def test_a_real_zone_still_scores_and_the_lines_have_not_moved(
        close, status, d, D, h, H):
    """
    Negative control. The NOT-MEASURED branches must not swallow real
    readings, and the two straight lines must not have moved.

    Stage 4 rewrote this from test_a_real_zone_still_scores_exactly_as_before,
    whose four cases were the EMA-position component's bands -- ACTIVE ENTRY
    ZONE at 30 of 30 within one band width of the midpoint, then NEAR at 20,
    APPROACHING at 10 and AWAY at 5 at two and three and a half widths. The
    component, the words and the widths are all gone (no ruling set the 1, 2
    and 3.5), so there is nothing left of the old expectations to keep. The
    cases below are the new lines at their ends and in between, including
    both ends of the band, where the close counts as inside it.
    """
    from models.entry_model import calculate_entry_quality

    out = calculate_entry_quality(
        _frame(close=close, atr=0.1, hvn=1.0), 0.9, 1.1)

    assert out["entry_status"] == status
    assert out["close_inside_band"] is (status == "INSIDE THE BAND")
    assert out["distance_atr"] == pytest.approx(d)
    assert out["distance_pts"] == pytest.approx(D)
    assert out["hvn_distance_atr"] == pytest.approx(h)
    assert out["hvn_pts"] == pytest.approx(H)
    assert out["score"] == pytest.approx(D + H)
    assert out["not_measured"] == []
    # Unchanged by this stage: the same distance as a percentage of the
    # close, under the same key and the same definition (round 8, F5).
    assert out["distance_from_zone"] == pytest.approx(
        abs(close - 1.0) / close * 100.0)


def test_neither_part_goes_negative_past_the_end_of_its_line():
    """
    max(0, ...) in both parts, held at a distance far past where each line
    reaches zero. Without this, a straight line would keep falling and a
    close far from everything would score below nothing.
    """
    from models.entry_model import calculate_entry_quality

    out = calculate_entry_quality(
        _frame(close=10.0, atr=0.1, hvn=1.0), 0.9, 1.1)

    assert out["distance_atr"] == pytest.approx(90.0)
    assert out["distance_pts"] == 0.0
    assert out["hvn_pts"] == 0.0
    assert out["score"] == 0.0


def test_bounds_given_the_wrong_way_round_are_still_swapped():
    """
    engine_core now orders them, but this function is public and takes two
    separate arguments, so it cannot assume its caller did.
    """
    from models.entry_model import calculate_entry_quality

    forwards = calculate_entry_quality(_frame(close=1.0), 0.9, 1.1)
    backwards = calculate_entry_quality(_frame(close=1.0), 1.1, 0.9)

    assert forwards == backwards


# ============================================================
# engine_core's half
# ============================================================

def _run_pinned():
    """
    Through SignalRouter, not Phase7Engine.run(), because the assembled
    `degradation` BLOCK (degraded / missing_inputs / trading_authorized) is
    the router's. The engine returns the raw list, and the first draft of
    this file called .get() on it.
    """
    from data.data_fetcher import DataFetcher, data_fetcher
    from models.signal_router import SignalRouter

    original = data_fetcher.base_url
    try:
        data_fetcher.base_url = UNREACHABLE
        DataFetcher.set_pinned_source(PINNED_DIR)
        return SignalRouter().route(symbol="AEROUSDT", timeframe="4h")
    finally:
        DataFetcher.clear_pinned_source()
        data_fetcher.base_url = original


def _entry_lines(panel):
    """
    Only the two lines under test.

    The first draft asserted `"$0.0000" not in panel` and
    `"not located" not in panel` against the WHOLE panel, and both matched
    other lines -- a zeroed price elsewhere in a minimal fixture, and SWING
    STRUCT's own "not located this run". Rule 30: a substring assertion
    cannot see the shape of what it matched.

    FINDING 4, 27 September 2026: the lines are labelled EMA BAND and BAND
    DISTANCE now (Viktor's ruling). Exactly two lines must match, so a
    future relabel fails here instead of leaving every assertion below to
    search an empty string.
    """
    lines = [
        line for line in panel.splitlines()
        if line.lstrip().startswith(("EMA BAND", "BAND DISTANCE"))
    ]
    assert len(lines) == 2, f"expected the band line and its distance: {lines!r}"
    return "\n".join(lines)


def test_the_lower_bound_is_the_lower_of_the_two():
    """
    The defect the live panel showed. On this fixture the trend is up, so
    EMA_20 > EMA_50 and the old code printed them in that order under labels
    saying the opposite.
    """
    pytest.importorskip("pandas_ta")

    decision = _run_pinned()
    entry = decision.get("entry", {})

    assert entry, f"no entry block: {sorted(decision)[:12]}"
    lower = float(entry["zone_lower"])
    upper = float(entry["zone_upper"])

    assert lower <= upper, (
        f"zone_lower {lower:.8f} is above zone_upper {upper:.8f}. The panel "
        f"prints these in that order under those labels."
    )

    bar = decision["lineage"]["indicators_at_decision_bar"]
    ema_fast, ema_slow = float(bar["EMA_20"]), float(bar["EMA_50"])
    assert {round(lower, 8), round(upper, 8)} == {round(min(ema_fast, ema_slow), 8),
                                                 round(max(ema_fast, ema_slow), 8)}, (
        f"the bounds ({lower}, {upper}) are not the two EMAs "
        f"({ema_fast}, {ema_slow}) — ordering them must not change which "
        f"numbers they are"
    )


def test_a_missing_ema_pair_degrades_the_run_instead_of_inventing_a_band():
    """
    End to end, with the EMAs actually gone. The absence has to reach the
    degradation block, because that — not the sub-score — is what stops the
    run authorising a trade.
    """
    pytest.importorskip("pandas_ta")

    import indicators.indicators as ind

    original = ind.add_technical_indicators

    def without_emas(df, inplace=False):
        frame, failures = original(df, inplace=inplace)
        return frame.drop(columns=[c for c in ("EMA_20", "EMA_50")
                                   if c in frame.columns]), failures

    import core.engine_core as ec
    ec_original = ec.add_technical_indicators
    try:
        ec.add_technical_indicators = without_emas
        decision = _run_pinned()
    finally:
        ec.add_technical_indicators = ec_original

    assert "error" not in decision, (
        f"removing the EMAs ended the run: {decision.get('error')}. Viktor "
        f"ruled degrade, not halt."
    )

    entry = decision["entry"]
    assert math.isnan(float(entry["zone_lower"])), (
        f"zone_lower is {entry['zone_lower']!r} with no EMA_20 in the frame"
    )
    assert math.isnan(float(entry["zone_upper"]))
    assert entry["entry_status"] == "ZONE NOT AVAILABLE"

    block = decision.get("degradation", {})
    assert block.get("degraded") is True, (
        f"the EMAs were missing and the run does not report itself degraded: "
        f"{block}"
    )
    assert any("entry zone" in m.lower() for m in block.get("missing_inputs", [])), (
        f"the degradation block does not name the entry zone: "
        f"{block.get('missing_inputs')}"
    )


def test_a_normal_run_is_not_degraded_by_this():
    """Negative control for the test above."""
    pytest.importorskip("pandas_ta")

    decision = _run_pinned()
    block = decision.get("degradation", {})

    assert block.get("degraded") is False, (
        f"a clean pinned run reports itself degraded: {block}"
    )
    assert not any("entry zone" in m.lower()
                   for m in block.get("missing_inputs", []))


# ============================================================
# The panel
# ============================================================

def _panel(entry):
    from core.panel_render import render_panel
    return render_panel({"symbol": "TESTUSDT", "timeframe": "4h", "entry": entry})


def test_the_panel_does_not_print_a_zone_it_does_not_have():
    panel = _panel({
        "zone_lower": float("nan"), "zone_upper": float("nan"),
        "distance_from_zone": float("nan"),
        "entry_status": "ZONE NOT AVAILABLE", "score": 45.0,
    })

    lines = _entry_lines(panel)

    assert "not located" in lines, (
        f"the panel does not say the zone is missing: {lines!r}"
    )
    assert "$0.0000" not in lines, (
        f"the panel still prints $0.0000 - $0.0000 for an absent zone. Zero "
        f"is a price. Lines: {lines!r}"
    )
    # "0.00%", not the whole old phrase: round 8's F5 relabelled the line
    # (10 October 2026), and a phrase the panel no longer prints would make
    # this assertion pass whatever the panel printed.
    assert "0.00%" not in lines, (
        f"the panel still prints 0.00% away — price sitting exactly on a "
        f"zone that was never found, which is the strongest claim this line "
        f"can make. Lines: {lines!r}"
    )
    assert "not measured" in lines


def test_the_panel_still_prints_a_zone_it_does_have():
    """Negative control."""
    panel = _panel({
        "zone_lower": 0.4918, "zone_upper": 0.4981,
        "distance_from_zone": 5.44,
        "entry_status": "AWAY FROM ZONE", "score": 36.66,
    })

    lines = _entry_lines(panel)

    assert "$0.4918 - $0.4981" in lines, lines
    assert "5.44% from the band's midpoint" in lines, lines
    assert "not located" not in lines, lines
