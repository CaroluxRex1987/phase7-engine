import math
import numbers
from decimal import Decimal, ROUND_FLOOR

from typing import Dict, Any, List, Optional, Tuple

from core.threshold_text import compared_value_text

# THE REDESIGN'S STAGE 4, 15 November 2026. Entry quality is D + H
# (docs/redesign_entry53_draft.md, section 3.1; the design was approved as a
# whole on 12 November, the tier lines ruled on 11 November, and the
# structure multiplier ruled out on 7 November).
#
# WHAT STOOD HERE UNTIL THIS STAGE, AND WHY NONE OF IT IS LEFT.
#
#     ZONE_POINTS_NOT_MEASURED = 15.0   of 30
#     ATR_POINTS_NOT_MEASURED  = 15.0   of 25
#
# were this file's own policy, established by Finding 3 on 1 September: a
# missing input left its component at the midpoint of its range and did not
# lower the score by itself, because carrying the absence was the degraded
# flag's job. The redesign does not score an absence at all. A part whose
# input is missing is NOT MEASURED, entry quality is not computed, and the
# run is degraded (section 3.1, "it is not given a neutral value"). So both
# constants go, and so do the VWMA 15.0, RSI 10.0 and structure 6.0 defaults
# that were written inline beside them -- the same fabrication shape without
# a name.
#
#     EMA_ZONE_MAX_POINTS = 30.0   ATR_DISTANCE_MAX_POINTS = 25.0
#     VWMA_MAX_POINTS     = 20.0   RSI_MAX_POINTS          = 15.0
#     STRUCTURE_MAX_POINTS = 12.0  COMPONENT_MAX_POINTS    = 102.0
#
# were the five parts' maxima and their sum. Four of the five parts leave
# with the design (section 3.2): VWMA, RSI and the HVN's percent bands are
# not the hypothesis the redesign tests, and the EMA-zone part's own band
# widths of 1, 2 and 3.5 were set by no ruling. Distance survives, as D,
# measured in ATRs instead of in band widths.
#
#     SCORE_CEILING = 100.0
#     CONFLUENCE_BOOST_MULT = 1.05   CONFLUENCE_PENALTY_MULT = 0.90
#
# were the clip and the two values the three confluence multipliers took.
# Viktor ruled the structure multiplier out on 7 November (DECISIONS,
# "Ruling, 7 November 2026 -- the redesign's entry quality has no structure
# multiplier"); macro's and trend's went with the factors they counted a
# second time (section 3.3). D + H reaches 100 exactly, so there is nothing
# left to clip.
#
# THE FOUR THAT REPLACE THEM. D is the close's distance from the midpoint of
# the EMA band, counted in ATRs; H is its distance from the HVN, in the same
# unit, so the two parts read in ONE unit (section 3.1). Both are straight
# lines rather than the old exp(-0.5 x ratio) decay, so every point on the
# panel can be checked by hand and the line reaches zero at a stated
# distance instead of never.
#
#     D = DISTANCE_MAX_POINTS x max(0, 1 - d / DISTANCE_ZERO_ATR)
#     H = HVN_MAX_POINTS      x max(0, 1 - h / HVN_ZERO_ATR)
#
# 80 and 20, not an even split: the hypothesis is a pullback to the average
# (ruling 1), so the distance is the question and the HVN is supporting
# evidence that a level is there. Keeping the HVN part at 20 also limits what
# H5 can move (section 8).
#
# Each of the four is registered in core/decision_log.py's
# FINGERPRINTED_MODULES, like every other constant that decides which runs
# may trade: each moves entry quality, and entry quality is the only input to
# the tier (ruling 4).
DISTANCE_MAX_POINTS = 80.0
DISTANCE_ZERO_ATR = 3.0
HVN_MAX_POINTS = 20.0
HVN_ZERO_ATR = 2.0


def _finite(value: Any) -> Optional[float]:
    """
    `value` as a float when it is a real, finite number, and None when there
    is no reading in it: a bool, anything that is not a number, NaN or an
    infinity. Zero is a reading, and so is a negative number -- the callers
    that need a positive one say so themselves.

    _measured_amount below is the same idea for a volume or a turnover,
    where a negative amount is not a reading either; the two are kept apart
    so neither has to carry the other's rule.
    """
    if isinstance(value, bool) or not isinstance(value, numbers.Real):
        return None
    number = float(value)
    return number if math.isfinite(number) else None


def _reading(df: Any, column: str) -> Optional[float]:
    """
    The decision candle's value in `column` -- the frame's last row, which
    the fetcher has already reduced to the latest CLOSED candle (finding 16)
    -- or None when there is no reading there.
    """
    try:
        if column not in df.columns or df[column].empty:
            return None
        return _finite(df[column].iloc[-1])
    except (AttributeError, IndexError, KeyError, TypeError, ValueError):
        return None

def calculate_entry_quality(
    df: Optional[Any],
    zone_lower: float,
    zone_upper: float,
) -> Dict[str, Any]:
    """
    Entry quality: D + H, from 0 to 100, with no multiplier and no clip.

    D, the distance part, is the close's distance from the midpoint of the
    EMA band, counted in ATRs:

        d = |close - band_mid| / ATR
        D = DISTANCE_MAX_POINTS x max(0, 1 - d / DISTANCE_ZERO_ATR)

    H, the HVN part, is its distance from the high-volume node, in the same
    unit:

        h = |close - HVN| / ATR
        H = HVN_MAX_POINTS x max(0, 1 - h / HVN_ZERO_ATR)

    Full points at the band's middle, nothing at DISTANCE_ZERO_ATR and
    beyond, and the same shape for H. The design, and why 80 and 20 rather
    than an even split, are above the four constants and in
    docs/redesign_entry53_draft.md, section 3.1.

    NOT MEASURED, AND WHY IT IS NOT A ZERO. If the close, the band, the ATR
    or the HVN cannot be read, the part that needed it is NOT MEASURED and
    entry quality is not computed: `score` is None, and so is each part that
    could not be read. `not_measured` names what was missing, and
    core/engine_core.py appends it to the run's degradation; gate 9 reads an
    absent score as a WAIT with a sentence of its own
    (models/decision_model.py, _apply_quality_gate), never as a quality of
    zero. Until this stage a missing input took the midpoint of its
    component's range -- 15 of 30 for the band, 15 of 25 for the ATR
    distance, 15 of 20 for VWMA, 10 of 15 for RSI, 6 of 12 for the HVN -- on
    the policy of 1 September that the degraded flag and not the score
    carries the absence. The redesign's rule of 29 August is the other way
    round: a number nobody measured is not reported as a number.

    The band's own absence is NOT named here. core/engine_core.py computes
    the band from EMA_20 and EMA_50 and can say which of the two was
    missing, so it names it there; naming it twice would put one missing
    input in the record under two descriptions.

    STATUS IS A POSITION, NOT A DISTANCE. The close is INSIDE THE BAND when
    it lies between EMA_20 and EMA_50 with the ends included, and ABOVE or
    BELOW it otherwise. `close_inside_band` is that same fact as a
    true-or-false field, and it is what the AGGRESSIVE tier reads
    (models/decision_model.py), so a change to a panel word cannot change an
    action and the word on the panel cannot disagree with the tier (section
    3.1, proposal 1, under Viktor's ruling of 7 November 2026 that the
    redesign's AGGRESSIVE reads the close inside the band). The words NEAR
    ZONE, APPROACHING ZONE, AWAY FROM ZONE and ZONE HAS NO WIDTH go with the
    band widths of 1, 2 and 3.5 that set them, which no ruling did; ZONE NOT
    AVAILABLE and NO DATA stay. Two coincident averages are still a band a
    close has a position against, which is why ZONE HAS NO WIDTH is not
    needed: the close is inside it, above it or below it as before.

    `distance_from_zone` keeps its key and its definition -- the same
    distance as a percentage of the close (round 8, F5) -- and
    `distance_atr` is that distance in ATRs. One measurement under two
    names, each name saying its unit (F8), and neither decides anything on
    its own.
    """
    not_measured: List[str] = []

    def unmeasured(status: str) -> Dict[str, Any]:
        return {
            "score": None,
            "distance_atr": None,
            "distance_pts": None,
            "hvn_distance_atr": None,
            "hvn_pts": None,
            "entry_status": str(status),
            "close_inside_band": None,
            # AUDIT FINDING (4), 5 September 2026: this was 0.0, which the
            # panel printed as "0.00% away from zone" -- price sitting
            # exactly on a zone that does not exist, on a run that had no
            # data at all. NaN is how this engine spells "not located" for
            # this field and panel_render prints it as such; the key, the
            # definition and the spelling are unchanged by this stage.
            "distance_from_zone": float("nan"),
            "not_measured": not_measured,
        }

    if df is None or getattr(df, "empty", True):
        not_measured.append("the decision frame (it has no rows to read)")
        return unmeasured("NO DATA")

    # AUDIT FINDING (4), 5 September 2026: the close fell back to 1.0, and
    # every distance, ratio and percentage below was measured against it.
    close = _reading(df, "close")
    if close is None or close <= 0.0:
        not_measured.append("close (the decision candle's close price)")
        return unmeasured("NO DATA")

    lower = _finite(zone_lower)
    upper = _finite(zone_upper)
    band_available = lower is not None and upper is not None
    if band_available and lower > upper:
        # Kept as a guard even though engine_core orders them before
        # calling: this function is public and takes the two bounds as
        # separate arguments, so it cannot assume its caller did.
        lower, upper = upper, lower

    if band_available:
        band_mid = (lower + upper) / 2.0
        dist_to_mid = abs(close - band_mid)
        distance_from_zone = float((dist_to_mid / close) * 100.0)
        inside = bool(lower <= close <= upper)
        if inside:
            entry_status = "INSIDE THE BAND"
        elif close > upper:
            entry_status = "ABOVE THE BAND"
        else:
            entry_status = "BELOW THE BAND"
    else:
        dist_to_mid = None
        distance_from_zone = float("nan")
        inside = None
        entry_status = "ZONE NOT AVAILABLE"

    atr = _reading(df, "ATR")
    if atr is not None and atr <= 0.0:
        # A zero or negative ATR is not a unit to count a distance in.
        atr = None
    if atr is None:
        not_measured.append(
            "ATR (entry quality counts both of its distances in ATRs)")

    hvn = _reading(df, "HVN")
    if hvn is None:
        not_measured.append(
            "HVN (the high-volume node the HVN part measures against)")

    if dist_to_mid is None or atr is None:
        distance_atr = None
        distance_pts = None
    else:
        distance_atr = float(dist_to_mid / atr)
        distance_pts = float(DISTANCE_MAX_POINTS
                             * max(0.0, 1.0 - distance_atr / DISTANCE_ZERO_ATR))

    if hvn is None or atr is None:
        hvn_distance_atr = None
        hvn_pts = None
    else:
        hvn_distance_atr = float(abs(close - hvn) / atr)
        hvn_pts = float(HVN_MAX_POINTS
                        * max(0.0, 1.0 - hvn_distance_atr / HVN_ZERO_ATR))

    score = (None if distance_pts is None or hvn_pts is None
             else float(distance_pts + hvn_pts))

    return {
        "score": score,
        "distance_atr": distance_atr,
        "distance_pts": distance_pts,
        "hvn_distance_atr": hvn_distance_atr,
        "hvn_pts": hvn_pts,
        "entry_status": entry_status,
        "close_inside_band": inside,
        "distance_from_zone": distance_from_zone,
        "not_measured": not_measured,
    }


# WORK ORDER F, 21 September 2026 -- the confirmation gate.
#
# Finding 11 of the 21 September pre-backtest review: long_signal and
# short_signal were computed on every run, carried into the decision object,
# the decision log and the simulated order -- and read by nothing that
# decides. The record could show `long_signal: False` beside an AGGRESSIVE
# LONG. They had been left in `entry` on 2 September "for a future ruling on
# whether they should CONFIRM a direction bias has already chosen" (see
# decision_model.py). That ruling is now made.
#
# VIKTOR'S RULING, 21 September 2026: the signal CONFIRMS. A trade the
# decision ladder chooses is taken only if the signal for its side holds;
# otherwise the action is NO-TRADE (SIGNAL UNCONFIRMED). He wrote the rule
# first; Claude critiqued it; he then delegated the remaining adjustments
# ("Make the adjustments you want and do what is best for the engine and the
# project"). What each old condition became, and whose call it was:
#
#   macro_bias not opposed      REMOVED -- Viktor. Macro is already a 10%
#                               factor inside bias_score; a veto lets the same
#                               evidence vote twice.
#   detailed_bias == CONFIRMED  REMOVED -- Viktor. decision_model chooses on
#                               raw_bias; a second, stricter bias threshold
#                               here was a conflict between two modules. The
#                               consequence, recorded: the bias state
#                               machine's persistence requirement no longer
#                               gates a trade anywhere.
#                               CORRECTED 27 September 2026 (finding 18):
#                               there was no persistence requirement. The
#                               state machine never read its previous state,
#                               so CONFIRMED only ever meant |bias_score| >
#                               30 -- and the ladder already needs >= 30
#                               (MIN_ACTION_BIAS) to act. What stopped gating
#                               here was that threshold, which differs from
#                               the ladder's only at exactly 30.0. The class
#                               is now bias_label (models/bias_engine.py).
#   trend_health >= 50          REMOVED -- Claude, under the delegation. It
#                               decided nothing: every trading branch of the
#                               ladder already requires trend_health >= 50
#                               (CONSERVATIVE_TREND_HEALTH_MIN) or >= 75.
#   reversal_strength > 0       REPLACED BY ITS PARTS -- Viktor. The number
#                               is a sum of named components (trend_health.py,
#                               section 7), so a cut-off would silently decide
#                               which combinations block. HVN proximity alone
#                               no longer blocks: it was a second HVN veto
#                               beside the stop pulled to the 75-day HVN.
#                               DEPENDENCY, recorded: if finding 6 is later
#                               ruled to stop pulling the stop to the HVN,
#                               nothing checks HVN proximity at all.
#                               IN FORCE since 27 September 2026: finding 6
#                               was so ruled, and no gate checks HVN
#                               proximity. It still weighs -- the entry
#                               score's structure points and trend_health's
#                               reversal reading read it -- but vetoes
#                               nothing. On the list for after the audit
#                               (Viktor, point 3 of the finding 6 ruling).
#   trend exhaustion            KEPT -- Viktor. Structure must match the side,
#                               so every confirmed trade runs with the trend,
#                               and exhaustion is always against it.
#                               REPLACED 5 October 2026 (fix 2, below): ADX
#                               under MIN_TREND_ADX blocks both sides in its
#                               place, and the flag no longer reaches the gate.
#   momentum divergence         BLOCKS ONLY WHEN IT POINTS AGAINST THE TRADE --
#                               Viktor. decision_model's own direction-blind
#                               divergence check on the upper tiers is removed
#                               in the same change so the engine has ONE
#                               divergence rule, not two that disagree --
#                               Claude, under the delegation.
#   structure regime matches    KEPT -- Viktor.
#
# Stated for the auditor: all three surviving conditions (structure regime,
# exhaustion via reversal/continuation, divergence) also reach bias_score
# as weighted factors. The gate is a hard AND on top of that blend -- a veto,
# which can refuse a trade but never adds confidence to one. That is a design
# choice. It has not been backtested; no evidence yet says it improves
# decisions.
# SINCE FIX 2 (5 October 2026) the three are structure regime, ADX and
# divergence. ADX reaches bias_score as well: it is up to 40 of trend
# health's 100 points (indicators/trend_health.py, adx_strength), and trend
# health is 30% of bias_score. The gate still only vetoes.
#
# Checked against the live decision log before writing (21 September, 29
# records): no past action would change. One SHORT was taken in that log
# (code 38458f20...); its reversal reading of 4.0 was HVN proximity alone,
# so it passes under this rule where the old signal refused it.

# FIX 2, 5 October 2026 -- no trend, no trade. Point 4 of round 8's triage
# (docs/PHASE7_DECISIONS.md, "Ruling, 5 October 2026 -- round 8 triaged
# ..."; the review's B3), Viktor's ruling by agreeing to Claude's suggestion:
# the exhaustion flag leaves this gate, and ADX under 20 blocks both sides,
# with the reason printed. It implements point 9 of the ruling of
# 28 September, "trends only, for now".
#
# Why the flag goes: it was (this bar's range > the last bar's AND ADX < 20)
# OR (trend health < 35 AND ADX < 15) (indicators/trend_health.py, section
# 4). Trend health is almost never under 35, so in practice it asked whether
# the last candle was wider than the one before it, in a low-ADX market --
# on the review's count of real 4h bars (not re-derived here) it fired on
# about half of the bars with ADX under 20 and on none above. Both of its
# clauses need ADX under 20, so every setup it blocked is still blocked.
#
# An ADX with no valid reading -- None (trend_readings.py could not read it),
# NaN, an infinity, a bool, anything that is not a number, or a number
# outside ADX's own 0-100 range -- blocks both sides too, with its own
# reason. The ruling left this to the patch, failing safe: a reading that
# does not exist cannot show a trend, so it cannot confirm one. The run
# still completes and is recorded. In this engine such a run is already
# degraded (trend_readings.py names the missing ADX), and the gate runs before
# the degradation override, so when the ladder chose a side the label is
# NO-TRADE (SIGNAL UNCONFIRMED) with the degradation notes appended to it --
# the precedence work order F set -- where it was NO-TRADE (DEGRADED INPUT).
#
# The flag itself is unchanged and still read everywhere else it was: trend
# health's reversal reading, the trend-regime label, Exit Watch and the
# record (trend.exhaustion). Only this gate stops reading it.
#
# 20 is the level the risk regime read as chop (models/risk_model.py's
# REGIME_CHOP_ADX, until fix 3): chosen, not derived, and not backtested. It
# is its own constant here, fingerprinted in core/decision_log.py, because the
# regime's two ADX tests were to be removed (point 3 of the same triage);
# fix 3 removed them on 6 October 2026.
#
# Checked against the live decision log (5 October, 48 records; records
# 1-10 are test records). ADX was under 20 on one live run, record 47
# (18.43, a WAIT: the ladder chose no side, so the gate decided nothing),
# and the exhaustion flag fired on no record. Replayed through
# DecisionModel.evaluate() with every other input held at its recorded
# value, no record's action differs before and after this fix. The blockers
# change on two records: 47 gains the ADX reason on both sides, and test
# record 4, which has no ADX at all, gains the no-reading reason on both.
# The confirmation sentence changes on the seven records whose replay
# confirms a side (19, 20, 21, 42, 43, 44 and 48).
MIN_TREND_ADX = 20.0


def _measured_adx(adx: Any) -> Optional[float]:
    """
    The ADX as a float, or None when there is no valid reading.

    A bool is a number to Python and not a reading; NaN and the infinities
    are not readings either; and ADX is bounded to 0-100 by its definition,
    so a value outside that range is a defect upstream, not a market. Every
    one of these returns None, which the gate treats as no trend shown.
    """
    if isinstance(adx, bool) or not isinstance(adx, numbers.Real):
        return None
    value = float(adx)
    if not math.isfinite(value) or value < 0.0 or value > 100.0:
        return None
    return value


def _adx_text(adx: float) -> str:
    """
    A valid ADX under MIN_TREND_ADX, as its blocker prints it: one decimal,
    rounded DOWN, so 19.96 reads "19.9" and never "20.0, under the 20".
    Decimal(repr(...)) floors the float's shortest decimal form exactly,
    which multiplying the float by ten and flooring cannot promise.
    """
    return str(Decimal(repr(float(adx))).quantize(Decimal("0.1"),
                                                  rounding=ROUND_FLOOR))


# THE REDESIGN'S STAGE 3, 15 November 2026: gates 6 and 7 of the draft's
# ladder (docs/redesign_entry53_draft.md, section 4) join this list, so that
# one place still names every reason a side is refused.
#
# GATE 6, Viktor's ruling of 25 October 2026, point 3: no LONG while the
# daily trend is bearish. A NEUTRAL daily trend passes; SHORT is not gated by
# macro. It is written in one vocabulary, side LONG against macro BEARISH,
# because entry 14's defect was a comparison of macro's words with the
# trade's. A macro value outside BULLISH, BEARISH and NEUTRAL is not a
# reading: it is neither passed nor called bearish (below).
#
# GATE 7, his ruling of 31 October 2026: the liquidity floor. The decision
# candle's turnover in USDT, MEXC's quote_volume, must be at least
# LIQUIDITY_FLOOR_USDT. 10,000 is his ruling of 11 November 2026, a starting
# value on the tunable list; it is the largest value of 1, 2, 5, 10, 20, 50 ...
# at which no pair had more than 5% of its records under it in the reading of
# 11 November. It applies to both sides.
#
# WHICH LABEL A REFUSED SIDE GETS. The draft's ladder takes the first gate,
# in order, that fails: gates 3 to 5 are NO-TRADE (SIGNAL UNCONFIRMED), as
# before; then gate 6, NO-TRADE (MACRO AGAINST); then gate 7, NO-TRADE (THIN
# MARKET). The blocker list still carries every reason. A gate 6 or 7 that
# could NOT BE MEASURED blocks the side too -- an absent confirmation is not
# a confirmation -- and takes the label SIGNAL UNCONFIRMED, never MACRO
# AGAINST or THIN MARKET: a market nobody measured is not given the label of
# a thin one (the draft's section 5, version 1). In the engine such a run is
# also degraded, named by core/engine_core.py.
LIQUIDITY_FLOOR_USDT = 10000.0

SIGNAL_UNCONFIRMED = "NO-TRADE (SIGNAL UNCONFIRMED)"
MACRO_AGAINST = "NO-TRADE (MACRO AGAINST)"
THIN_MARKET = "NO-TRADE (THIN MARKET)"
REFUSAL_LABELS = (SIGNAL_UNCONFIRMED, MACRO_AGAINST, THIN_MARKET)

MACRO_READINGS = ("BULLISH", "BEARISH", "NEUTRAL")


def _measured_amount(value: Any) -> Optional[float]:
    """
    A volume or a turnover as a float, or None when there is no valid
    reading: a bool, anything that is not a number, NaN, an infinity or a
    negative amount. Zero is a reading.
    """
    if isinstance(value, bool) or not isinstance(value, numbers.Real):
        return None
    amount = float(value)
    if not math.isfinite(amount) or amount < 0.0:
        return None
    return amount


def exact_text(value: float) -> str:
    """A number as recorded: its shortest decimal form, with no rounding."""
    return f"{Decimal(repr(float(value))):f}"


def _signal_refusals(
    direction: str,
    structure_regime: str,
    momentum_divergence: bool,
    divergence_direction: str,
    *,
    adx: Any,
    macro_bias: Any,
    quote_volume: Any,
) -> List[Tuple[str, str]]:
    """
    Every reason the setup does not confirm `direction`, in gate order, each
    with the label that gate gives a refused trade. signal_blockers() is the
    reasons; generate_entry_signals() also records the first one's label.
    """
    if direction not in ("LONG", "SHORT"):
        raise ValueError(f"direction must be LONG or SHORT, got {direction!r}")

    refusals = [(SIGNAL_UNCONFIRMED, reason) for reason in _confirmation_blockers(
        direction, structure_regime, momentum_divergence, divergence_direction,
        adx=adx)]

    # Gate 6.
    if direction == "LONG":
        if not isinstance(macro_bias, str) or macro_bias not in MACRO_READINGS:
            refusals.append((
                SIGNAL_UNCONFIRMED,
                f"the daily trend was recorded as {macro_bias!r}, which is "
                "not BULLISH, BEARISH or NEUTRAL, so it cannot be shown not "
                "to be bearish"))
        elif macro_bias == "BEARISH":
            refusals.append((
                MACRO_AGAINST,
                "the daily trend is BEARISH, and no long is taken while the "
                "daily trend is bearish"))

    # Gate 7.
    turnover = _measured_amount(quote_volume)
    if turnover is None:
        refusals.append((
            SIGNAL_UNCONFIRMED,
            "the decision candle's turnover in USDT has no valid reading on "
            "this run, so the market cannot be shown to be liquid enough"))
    elif turnover < LIQUIDITY_FLOOR_USDT:
        refusals.append((
            THIN_MARKET,
            f"the decision candle's turnover was "
            f"{compared_value_text(turnover, LIQUIDITY_FLOOR_USDT)} USDT, "
            f"under the {LIQUIDITY_FLOOR_USDT:g} USDT the engine requires "
            f"to treat the market as liquid enough"))

    return refusals


def signal_blockers(
    direction: str,
    structure_regime: str,
    momentum_divergence: bool,
    divergence_direction: str,
    *,
    adx: Any,
    macro_bias: Any,
    quote_volume: Any,
) -> List[str]:
    """
    Every reason the setup does NOT confirm a trade in `direction` ("LONG" or
    "SHORT"). An empty list is a confirmation; the signal is exactly that.

    `adx` is keyword-only and has no default (fix 2): a call in the shape
    before fix 2 -- the exhaustion flag third, five positional arguments --
    raises TypeError instead of binding the flag to another parameter.
    `macro_bias` and `quote_volume` (stage 3 of the redesign, gates 6 and 7)
    are keyword-only with no default for the same reason: a call that does
    not give them is refused, not read as a market that passed both.
    """
    return [reason for _, reason in _signal_refusals(
        direction, structure_regime, momentum_divergence, divergence_direction,
        adx=adx, macro_bias=macro_bias, quote_volume=quote_volume)]


def _confirmation_blockers(
    direction: str,
    structure_regime: str,
    momentum_divergence: bool,
    divergence_direction: str,
    *,
    adx: Any,
) -> List[str]:
    """Gates 3 to 5: structure, ADX and the price/RSI disagreement."""
    wanted_structure = "BULLISH TREND" if direction == "LONG" else "BEARISH TREND"
    opposing = "BEARISH" if direction == "LONG" else "BULLISH"
    blockers: List[str] = []

    if structure_regime != wanted_structure:
        blockers.append(f"structure is {structure_regime}, not {wanted_structure}")

    measured = _measured_adx(adx)
    if measured is None:
        blockers.append(
            "ADX has no valid reading on this run, so the market cannot be "
            "shown to be trending")
    elif measured < MIN_TREND_ADX:
        blockers.append(
            f"ADX is {_adx_text(measured)}, under the {MIN_TREND_ADX:g} the "
            f"engine requires to treat the market as trending")

    # B4's LABELS, 14 October 2026: these sentences said "momentum
    # divergence", which reads as highs against highs. What
    # indicators/trend_readings.py compares is this candle's close and RSI
    # with the close and RSI four candles back, so that is what they say.
    # The rule is unchanged (whether it should veto is Viktor's, not ruled).
    if momentum_divergence:
        if divergence_direction == opposing:
            blockers.append(
                f"a {opposing.lower()} price/RSI disagreement over four "
                f"candles points against the trade")
        elif divergence_direction not in ("BULLISH", "BEARISH"):
            # A divergence whose direction was not recorded cannot be shown
            # NOT to point against the trade, so it is not a confirmation.
            blockers.append(
                "price and RSI disagree over four candles, but the direction "
                f"was recorded as {divergence_direction!r}, so it cannot be "
                "shown not to point against the trade")

    return blockers


def generate_entry_signals(
    structure_regime: str,
    momentum_divergence: bool,
    divergence_direction: str,
    *,
    adx: Any,
    macro_bias: Any,
    quote_volume: Any,
) -> Dict[str, Any]:
    """
    Both sides' confirmation signals and the reasons behind each.

    Returns long_signal / short_signal (True exactly when that side's blocker
    list is empty), long_signal_blockers / short_signal_blockers, and, since
    stage 3 of the redesign, long_signal_refusal / short_signal_refusal: the
    NO-TRADE label of the first gate that side does not pass, None when it
    passes them all. Both sides are recorded so the decision log shows why
    each was or was not confirmed, not only the side that was traded.
    """
    out: Dict[str, Any] = {}
    for key, direction in (("long", "LONG"), ("short", "SHORT")):
        refusals = _signal_refusals(
            direction, structure_regime, momentum_divergence,
            divergence_direction, adx=adx, macro_bias=macro_bias,
            quote_volume=quote_volume)
        out[f"{key}_signal"] = not refusals
        out[f"{key}_signal_blockers"] = [reason for _, reason in refusals]
        out[f"{key}_signal_refusal"] = refusals[0][0] if refusals else None
    return out


# THE REDESIGN'S STAGE 3, 15 November 2026: gate 8, the trigger and its
# volume (the draft's section 5).
#
# THE TRIGGER, Viktor's ruling of 11 November 2026: for a LONG, the decision
# candle -- the last closed one -- closes above its open AND above the
# previous candle's close; a SHORT is the mirror. A pullback that has not
# turned yet is a WAIT.
#
# ITS VOLUME, his ruling of 31 October 2026: that candle's volume must be
# strictly above the median of the TRIGGER_VOLUME_LOOKBACK candles before it.
# The margin starts at zero. Twenty is a length, not a cutoff. Base-asset
# volume, because it is compared with itself on one pair.
#
# NOT MEASURED IS NOT A READING (the draft's section 3.2, entry 19's lesson
# carried forward): an absent or non-finite volume on the decision candle, or
# fewer than twenty readable candles before it, leaves the median None and is
# named in `not_measured`; it is never compared as though it were the median.
# The same for a price that is not a finite number. core/engine_core.py
# degrades the run on any name in that list.
#
# With no side -- a NEUTRAL direction -- there is no trigger to read, and
# `trigger` is None with nothing named: the ladder has already returned WAIT
# at gate 2. The two volumes are still recorded; they have no side.
TRIGGER_VOLUME_LOOKBACK = 20


def read_trigger(
    side: Optional[str],
    *,
    open_price: Any,
    close_price: Any,
    previous_close: Any,
    volume: Any,
    previous_volumes: Any,
) -> Dict[str, Any]:
    """
    Gate 8's readings on the decision candle.

    `side` is "LONG", "SHORT" or None (no side). `previous_volumes` is the
    volume of the candles before the decision candle, oldest first; the last
    TRIGGER_VOLUME_LOOKBACK of them are read.

    Returns `trigger` (True, False, or None when there is no side or a price
    was not measured), `trigger_volume`, `trigger_volume_median` (each None
    when not measured) and `not_measured`, the names of what could not be
    read.
    """
    if side not in ("LONG", "SHORT", None):
        raise ValueError(f"side must be LONG, SHORT or None, got {side!r}")

    not_measured: List[str] = []

    def price(value: Any, name: str) -> Optional[float]:
        if (isinstance(value, bool) or not isinstance(value, numbers.Real)
                or not math.isfinite(float(value))):
            not_measured.append(name)
            return None
        return float(value)

    opened = price(open_price, "the decision candle's open")
    closed = price(close_price, "the decision candle's close")
    before = price(previous_close, "the previous candle's close")

    trigger: Optional[bool] = None
    if side is not None and None not in (opened, closed, before):
        if side == "LONG":
            trigger = closed > opened and closed > before
        else:
            trigger = closed < opened and closed < before

    trigger_volume = _measured_amount(volume)
    if trigger_volume is None:
        not_measured.append("the decision candle's volume")

    try:
        earlier = list(previous_volumes)
    except TypeError:
        earlier = []
    window = [_measured_amount(v) for v in earlier[-TRIGGER_VOLUME_LOOKBACK:]]
    median: Optional[float] = None
    if len(window) == TRIGGER_VOLUME_LOOKBACK and None not in window:
        ordered = sorted(window)
        middle = TRIGGER_VOLUME_LOOKBACK // 2
        if TRIGGER_VOLUME_LOOKBACK % 2:
            median = ordered[middle]
        else:
            median = (ordered[middle - 1] + ordered[middle]) / 2.0
    else:
        not_measured.append(
            f"the volume of the {TRIGGER_VOLUME_LOOKBACK} candles before "
            f"the decision candle")

    return {
        "trigger": trigger,
        "trigger_volume": trigger_volume,
        "trigger_volume_median": median,
        "not_measured": not_measured,
    }
