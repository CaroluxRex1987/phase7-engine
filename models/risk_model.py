from typing import Tuple, Optional
import logging
import numpy as np

logger = logging.getLogger(__name__)

# ==================================================================
# DECISION-AFFECTING CONSTANTS
#
# These are module-level, not instance attributes, because
# core/decision_log.py's module_snapshot() fingerprints MODULE
# attributes and cannot see instance state.
#
# AUDIT FINDING 6 (Item 5) asked for "all decision-affecting
# configuration, including risk-model multipliers and bias weights."
# The bias weights were fingerprinted at that item. These were not,
# and they could not have been: they lived on the instance, where
# the mechanism cannot reach them. Two runs whose stops and every
# target differed by 25% hashed identically, and the record that
# claims to identify a run could not tell them apart.
#
# They are read DIRECTLY by the methods below. They are deliberately
# not copied onto self in __init__, because a copy restores exactly
# the gap this closes -- the snapshot would report the module value
# while the arithmetic used the instance one, and nothing would say
# which produced the plan. There is no instance state here to drift.
#
# tests/test_risk_fingerprint.py holds all of this true: that every
# name below is fingerprinted, that none of them is dead, and that
# the multipliers have not crept back onto the instance.
# ==================================================================

# Stop and target geometry.
ATR_STOP_MULT = 1.2            # base ATR multiplier for the stop
TARGET1_MULT = 1.0             # conservative target, x stop distance
TARGET2_MULT = 2.0             # normal target, x stop distance
TARGET3_MULT = 3.0             # aggressive target, x stop distance

# Volatility adjustment applied to the stop multiplier.
VOL_MULT_HIGH = 1.35           # widen stops in high vol to avoid whipsaws
VOL_MULT_LOW = 0.85            # tighter stops in calm markets
VOL_MULT_EXTREME = 1.60

# FIX 1, 5 October 2026 (docs/PHASE7_DECISIONS.md, "Ruling, 5 October
# 2026 -- round 8 triaged ...", point 1). Two constants stood here under the
# heading "Structural influence on the stop. A strong trend pushes the stop
# further out; a strong bias pulls it back in.":
#
#     TREND_FACTOR_DIVISOR = 200.0
#     BIAS_FACTOR_DIVISOR = 300.0
#
# They scaled the stop multiplier by 1 + trend_health / 200 (x1.0 to x1.5)
# and by 1 - |bias_score| / 300 (x0.667 at a score of 100). So the same
# market -- the same price, ATR and volatility -- passed or failed the 8%
# risk check below depending on how convinced the engine was, which Viktor
# ruled a break of Item 14: "Directional conviction must never be treated as
# equivalent to risk." The stop is ATR x ATR_STOP_MULT x the volatility
# factor, and nothing else scales it. Both constants are gone, and so are
# their two entries in core/decision_log.py's FINGERPRINTED_MODULES.

# Risk regime boundaries.
#
# ITEM 14, 11 September 2026. REGIME_LOW_TREND_HEALTH (40.0) and
# REGIME_HIGH_TREND_HEALTH (70.0) stood here and were read against
# trend_health. Kimi Finding 4 named the consequence: trend_health is
# WEIGHT_TREND_HEALTH = 0.30 of bias_score, the largest single factor in the
# engine's conviction number, and it was ALSO the number deciding the risk
# regime that Item 14 requires to be an INDEPENDENT check on conviction. One
# reading moved both gates in the same direction at once -- a strong trend
# raised confidence and lowered assessed risk simultaneously -- so the second
# gate could not do the job the Constitution gives it.
#
# Viktor ruled 11 September 2026: the risk regime determines itself. The
# thresholds below read ADX instead, which is an INPUT to trend_health rather
# than something derived from it, and both values are the ones this codebase
# already uses for the same two market states in indicators/trend_health.py:
# ADX < 20 is its "MEAN REVERTING / CHOP" boundary and ADX >= 25 its
# "STRONG TREND" confirmation. Nothing here is a new calibration -- the two
# numbers were already load-bearing one module over.
#
# UPDATE, 19 September 2026: the paragraph below described an accepted
# limit -- ADX reached bias_score a second time, through
# continuation_strength's adx_component, and was kept there on 31 August
# because it was not literally the same VALUE as trend_health's own ADX
# read, just a second, differently-scaled transform of the same raw
# reading. An independence review applied a stricter standard (no shared
# raw INPUT, not just no shared computed value) and removed that second
# transform -- see indicators/trend_health.py's "INDEPENDENCE REVIEW"
# comment. ADX now reaches bias_score through exactly one of its six
# factors (trend_health, 0.30). This module's own read of ADX below was
# never through bias_score or continuation_strength -- it reads adx_val
# directly, so it was independent of bias_score before this change and
# remains so after it; nothing in this file needed to change.
#
# Honest limit, recorded rather than glossed (original text, now historical):
# "ADX is not wholly absent from bias_score -- it reaches it through
# continuation_strength's adx_component. What it is no longer is the same
# value read twice, which is the defect Item 14 names, and that is the same
# standard the Item 11 fix applied when it kept ADX inside
# continuation_strength while removing trend_health." That adx_component no
# longer exists; the sentence is kept for the record rather than deleted, per
# this project's practice of not quietly erasing a superseded rationale.
#
# FIX 3, 6 October 2026 (docs/PHASE7_DECISIONS.md, "Ruling, 5 October 2026
# -- round 8 triaged ...", point 3; round 8's F2 and the review's B8). Two
# more constants stood below REGIME_EXTREME_STOP_PCT: REGIME_CHOP_ADX = 20.0,
# under which the regime was HIGH VOLATILITY RISK, and REGIME_STRONG_ADX =
# 25.0, which LOW VOLATILITY needed to reach LOW RISK. Both are gone, and the
# regime reads no ADX at all.
#
# The UPDATE of 19 September above says this module's read of ADX was
# independent of bias_score. By the standard that same update applied -- no
# shared raw input -- it was not: trend health spends up to 40 of its 100
# points on the same raw ADX (adx_strength, indicators/trend_health.py), and
# trend health is 0.30 of bias_score, so a high ADX still raised conviction
# and lowered the assessed risk together. Round 8 found it as F2. The chop
# test also named the wrong cause: a calm market with no trend printed
# VOLATILITY : LOW VOLATILITY beside RISK REGIME : HIGH VOLATILITY RISK (the
# review's B8).
#
# The regime now comes from volatility alone: the volatility state, and the
# stop distance tested against REGIME_EXTREME_STOP_PCT below, which since
# fix 1 is ATR x ATR_STOP_MULT x the volatility factor -- a measure of
# volatility too. Chop is no longer the regime's to see. Since fix 2 the
# confirmation gate refuses both sides under ADX 20 (models/entry_model.py,
# MIN_TREND_ADX), which is why fix 3 landed after fix 2: in the other order a
# calm market with no trend could have been called AGGRESSIVE between the
# two commits.
REGIME_EXTREME_STOP_PCT = 8.0

# Hard validity limits on the stop distance.
MAX_STOP_DISTANCE_PCT = 15.0   # wider than this is not a stop, it is a hope
MIN_STOP_DISTANCE_PCT = 0.2    # tighter than this sits inside market noise


# ==================================================================
# READING THE VERDICT — GLM F-7, extended. 6 September 2026.
#
# Every consumer of the risk block used to read the pass/fail with
#
#     risk.get("risk_valid", True)
#
# in three places: decision_model._determine_final_action (the trade
# authorization gate), signal_router._build_decision_object (the
# field that reaches the decision log and the panel), and
# live_trading._build_simulated_order. GLM filed only the third and
# argued Minor on the grounds that the module writes a simulated
# order log. The severity argument does not cover the first.
#
# The default is the defect. A risk block that is a dict but carries
# no `risk_valid` is a block on which risk was NEVER ASSESSED, and
# the gate read that state as "assessed, and it passed" -- the one
# direction an authorization gate must never fail in.
#
# It was reachable, not merely latent. signal_router's
# _validate_engine_output checked that the key "risk" was PRESENT as
# a section and never what it contained, so an engine output whose
# risk block was `{}` passed validation, satisfied
# _determine_final_action's isinstance(risk, dict) guard, and could
# return LONG or SHORT with no risk assessment behind it.
# _refuse_incoherent_plan does not catch that case either: an empty
# block has no targets, so _plan_direction returns None and the
# action is passed through untouched.
#
# This function is the one place a verdict is read, for the same
# reason _optional_number is the one place an optional measurement
# is read (signal_router.py, 6 September): a defect found in three
# call sites is a class, and three corrected call sites are three
# things to keep correct.
# ==================================================================

def read_risk_verdict(risk) -> Optional[bool]:
    """
    The risk block's pass/fail verdict, or None when there is no verdict.

    Total by construction. Absent, present as None, and present as
    something that is not a boolean are all one state -- risk was not
    assessed -- and none of them is a pass. The caller decides what to do
    about it; this function will not decide for them by inventing one.

    Deliberately strict about the type. validate_risk_parameters() below
    is the only producer and every one of its six return paths hands back
    a Python bool literal, so nothing legitimate is rejected here. Should
    some future path emit a numpy bool or a truthy string instead, this
    returns None and the callers refuse the trade: an unrecognised verdict
    fails closed, which is the direction this whole function exists to
    protect.
    """
    if not isinstance(risk, dict):
        return None
    value = risk.get("risk_valid")
    if isinstance(value, bool):
        return value
    return None


def _refuse_wrong_side_stop(plan_direction, current_price, atr_stop):
    """
    21 SEPTEMBER 2026, work order C. Replaces a fallback that set

        stop_distance = atr_val * ATR_STOP_MULT

    whenever the stop did not sit on the correct side of price, commented as
    a "degenerate case (e.g. structural level sits above price)".

    UNREACHABLE on the engine's own path. bias_engine clips bias_score to
    +-100, so bias_factor = 1 - |bias_score| / 300 is at least 0.667 and the
    ATR stop always lands on the correct side of price; min() / max() against
    the structural level can only move it further out. The comment's own
    example -- a structural level above price on a long -- is the case min()
    already rules out. (Finding 6, 27 September 2026, removed the structural
    level and the min() / max(); the stop is the ATR stop alone, and the
    argument above holds for it unchanged.) (Fix 1, 5 October 2026, removed
    bias_factor as well -- see the last paragraph.)

    WRONG IF IT WERE REACHED. It replaced the DISTANCE and left the stop where
    it was, on the wrong side of price: a stop above a long's entry, returned
    with three targets measured from a different distance than the stop
    implies. The panel computes R:R with abs(), so it would have printed a
    normal-looking 1:1 / 2:1 / 3:1 beside it, and validate_risk_parameters
    measures the distance with abs() too, so the plan could pass the risk
    check. Reachable by calling calculate_stop_targets with |bias_score| of
    300 or more, which tests/test_plan_direction_and_side.py did until fix 1.

    SINCE FIX 1, 5 October 2026. The stop distance is atr_val x
    ATR_STOP_MULT x a volatility factor, and every one of those is positive,
    so no value of bias_score reaches this branch any more. Two things still
    can. A multiplier constant made zero or negative, which nothing in the
    engine does; tests/test_plan_direction_and_side.py does it for the length
    of one test, to show this raise is still load-bearing. And floating point
    at absurd scales: an ATR under about 1e-16 of price is absorbed when it is
    subtracted, so the distance comes out zero, and an ATR near the largest
    float overflows it to infinity (both checked on 5 October).

    A stop on the wrong side of entry is not a degenerate plan; it is not a
    plan. This raises, and calculate_stop_targets' own except turns that into
    the engine's existing "no risk plan can be produced" error path.
    """
    raise ValueError(
        f"The stop for a {plan_direction} came out at {atr_stop}, on the wrong "
        f"side of the current price {current_price} -- a stop that is not "
        f"below a long's entry or above a short's is not a stop."
    )


class RiskModel:
    """
    Core institutional risk engine for Phase-7.
    Provides:
        - Volatility-adjusted ATR stop calculation
        - Tiered target generation
        - Position sizing & leverage adjustment
        - Risk regime classification & advanced validation
    """

    # __init__ removed. It set four multipliers onto the instance:
    # atr_stop_mult, target1_mult, target2_mult and target3_mult. They
    # are module-level constants above now -- see the block there for
    # why. Nothing outside this file ever read the attributes, and
    # nothing assigned to them, so removing them changes no behaviour
    # and removes the only place the recorded settings and the settings
    # actually used could diverge.

    # ============================================================
    # STOP & TARGETS (WITH VOLATILITY ADJUSTMENT)
    # ============================================================

    def calculate_stop_targets(
        self,
        *,
        current_price: float,
        atr_val: float,
        bias_score: float,
        volatility_state: str = "NORMAL"
    ) -> Tuple[float, float, float, float]:
        """
        Compute volatility-adjusted ATR stop + tiered targets. The plan points
        LONG when bias_score >= 0 and SHORT when it is negative -- on every run,
        including one whose bias is NEUTRAL, so targets never collapse to
        current price.

        21 SEPTEMBER 2026, work order C. The first parameter used to be
        `detailed_bias`, and the direction was chosen by a branch that tested
        it for "LONG" / "SHORT" and otherwise fell back to the sign of
        bias_score. Its only caller passes BiasStateMachine's output, which is
        "BULLISH CONFIRMED", "BEARISH CONFIRMED" or "NEUTRAL" -- never "LONG"
        or "SHORT". So the branch could not be taken, the parameter decided
        nothing, and the direction has always come from the sign of
        bias_score. The same wrong-vocabulary shape as the A1/A2 gates in
        entry_model.py, surviving in a second file. The parameter is removed
        rather than left in place, because a parameter that reads as the
        direction source while being ignored is how the 2 September record
        (tests/test_direction_source.py) came to say this function built its
        plan "from detailed_bias alone". Passing it now raises TypeError.
        CORRECTED 27 September 2026 (finding 18): BiasStateMachine -- now
        models.bias_engine.bias_label -- also returned plain "BULLISH" and
        "BEARISH" (a score past +/-20 up to +/-30), not only the three labels
        listed above. Still never "LONG" or "SHORT", so the conclusion stands.

        FINDING 6, 27 September 2026. The fourth parameter used to be
        `structural_level`, and its only caller passed the HVN -- the single
        highest-volume bin of the whole 450-candle frame, about 75 days on 4h
        (indicators/volume_profile.py). For a long the stop was
        min(HVN, ATR stop), for a short max(...), so the point of control
        could only widen the stop and had no distance limit of its own: a
        trend that had moved away from it got its stop there, and past 8% the
        risk check refused the setup. On Viktor's decision log (39 usable
        runs, 6-27 September, AEROUSDT 4h) the HVN set the stop in 35 of 39.
        Viktor ruled that the stop comes from ATR alone and the HVN stays as
        information only (docs/PHASE7_DECISIONS.md, "Ruling, 27 September
        2026 -- the stop comes from ATR alone (finding 6)"). The parameter is
        removed rather than ignored, for the reason given for detailed_bias
        above: a parameter that reads as a stop anchor while deciding nothing
        is a false statement in the signature. Passing it now raises
        TypeError. The 8% (EXTREME RISK) and 15% (distance refusal) limits in
        validate_risk_parameters are unchanged by the same ruling.

        FIX 1, 5 October 2026 (round 8's triage, point 1). The first
        parameter used to be `trend_health`, and the stop multiplier was
        ATR_STOP_MULT x trend_factor x bias_factor x the volatility factor,
        with trend_factor = 1 + trend_health / 200 and bias_factor =
        1 - |bias_score| / 300. Conviction therefore set the stop, and the
        stop decides the 8% risk verdict: the three LONGs of 27 September
        passed at a 7.15% stop that is 9.53% without the bias factor. Viktor
        ruled it a break of Item 14 and the stop is now ATR_STOP_MULT x the
        volatility factor. That also makes the 27 September ruling, "the stop
        comes from ATR alone", true as worded. `trend_health` is removed
        rather than ignored, for the reason given for detailed_bias above,
        and passing it raises TypeError. bias_score stays: its sign still
        picks the side, and its size no longer reaches the stop. Every
        parameter is keyword-only, because removing the first one would
        otherwise make a call in the old positional order bind trend health
        to current_price without a word.

        Args:
            current_price: Current market price
            atr_val: Average True Range value
            bias_score: Bias score; its sign picks the side (>= 0 is LONG)
            volatility_state: Current volatility regime

        Returns:
            Tuple of (atr_stop, target1, target2, target3)
        """
        try:
            # Input validation
            #
            # FINDING 3 RE-AUDIT, 1 September 2026: this was
            #     if current_price <= 0 or atr_val <= 0
            # and NaN fails both comparisons, because every comparison against
            # NaN is False. So a NaN ATR walked straight past the guard. With
            # no structural level it produced (nan, nan, nan, nan) -- printed
            # verbatim by the panel, whose safe_float did not check finiteness
            # either. WITH a structural level it was worse: the levels came out
            # of the structural branch and looked completely normal
            # -- (98.0, 102.0, 104.0, 106.0) in the audit's own scenario --
            # while the ATR that is supposed to set stop distance contributed
            # nothing and nothing anywhere was flagged. (Finding 6, 27 September
            # 2026, removed the structural branch; the guard stays.)
            #
            # validate_risk_parameters, twenty lines below in this same file,
            # has checked np.isfinite since sequence item 2. The two methods
            # disagreed about whether NaN was acceptable input; they no longer
            # do.
            if not (np.isfinite(current_price) and np.isfinite(atr_val)):
                logger.error(f"Non-finite price inputs: price={current_price}, atr={atr_val}")
                raise ValueError(
                    f"Non-finite price or ATR (price={current_price}, "
                    f"atr={atr_val}) -- no stop or targets can be computed from "
                    f"a value that is not a number."
                )
            # 21 SEPTEMBER 2026, work order C: bias_score picks the plan's
            # direction below, and `NaN >= 0` is False -- a NaN score would
            # have produced a SHORT plan, a direction chosen by a missing
            # number. Unreachable today (bias_engine returns a finite, clipped
            # score); refused here so it stays that way.
            if not np.isfinite(bias_score):
                raise ValueError(
                    f"Non-finite bias_score ({bias_score}) -- the plan's "
                    f"direction is the sign of this number, and a number that "
                    f"is not one has no sign."
                )
            if current_price <= 0 or atr_val <= 0:
                logger.error(f"Invalid price inputs: price={current_price}, atr={atr_val}")
                raise ValueError("Invalid price or ATR values")

            plan_direction = "LONG" if bias_score >= 0 else "SHORT"

            # Volatility-adjusted modifier
            vol_multiplier = 1.0
            if volatility_state == "HIGH VOLATILITY":
                vol_multiplier = VOL_MULT_HIGH
            elif volatility_state == "LOW VOLATILITY":
                vol_multiplier = VOL_MULT_LOW
            elif volatility_state == "EXTREME VOLATILITY":
                vol_multiplier = VOL_MULT_EXTREME

            # FIX 1, 5 October 2026: trend_factor and bias_factor stood here
            # and multiplied into stop_mult -- conviction setting the stop. See
            # the docstring. Nothing but the volatility state scales it now.
            stop_mult = ATR_STOP_MULT * vol_multiplier

            # A12 FIX: targets are now computed as multiples of the ACTUAL stop
            # distance (i.e. real risk), not fixed ATR multiples independent of
            # it. Previously, since the stop can be pulled further out by
            # trend/volatility factors or a structural level (via the min/max
            # below), the realized stop distance could exceed 1x-2x raw ATR,
            # making "conservative" T1 mathematically the worst R:R target
            # (often below 1:1) by construction. Now T1/T2/T3 R:R come out at
            # exactly 1:1 / 2:1 / 3:1 relative to what's actually being risked.
            #
            # FINDING 6, 27 September 2026: the structural level and the
            # min/max named above are gone -- see the docstring. The stop is
            # the ATR stop, and nothing else moves it. (Fix 1, 5 October
            # 2026: the trend factor named above is gone too; the volatility
            # factor is the only one left.)
            if plan_direction == "LONG":
                atr_stop = current_price - (atr_val * stop_mult)

                stop_distance = current_price - atr_stop
                if not np.isfinite(stop_distance) or stop_distance <= 0:
                    _refuse_wrong_side_stop(plan_direction, current_price, atr_stop)

                target_t1 = current_price + (stop_distance * TARGET1_MULT)
                target_t2 = current_price + (stop_distance * TARGET2_MULT)
                target_t3 = current_price + (stop_distance * TARGET3_MULT)
            else:  # SHORT
                atr_stop = current_price + (atr_val * stop_mult)

                stop_distance = atr_stop - current_price
                if not np.isfinite(stop_distance) or stop_distance <= 0:
                    _refuse_wrong_side_stop(plan_direction, current_price, atr_stop)

                target_t1 = current_price - (stop_distance * TARGET1_MULT)
                target_t2 = current_price - (stop_distance * TARGET2_MULT)
                target_t3 = current_price - (stop_distance * TARGET3_MULT)

            return float(atr_stop), float(target_t1), float(target_t2), float(target_t3)

        except Exception as e:
            # SEQUENCE ITEM 9b: this used to return "safe default fallback
            # bounds" — a stop at price × 0.99 and targets at 1.01, 1.02, 1.03.
            #
            # DIRECTION-BLIND. Those numbers put the stop 1% BELOW price and the
            # targets ABOVE it, whatever `detailed_bias` said. On a short they
            # are inverted: the stop sits where the trade would be winning and
            # every target sits where it would be losing. The panel printed
            # them as STOP LOSS and TARGET 1/2/3 with R:R ratios computed off
            # them, indistinguishable from a real plan.
            #
            # Nor were they "safe". A 1% stop on an instrument whose ATR is 4%
            # is not conservative, it is a stop inside the noise — and the
            # 1/2/3% targets encode a 1:1, 2:1, 3:1 reward that has nothing to
            # do with this market.
            #
            # It is the last of the fabrications item 9 set out to remove, and
            # the only one that produced a tradeable-looking artefact rather
            # than a wrong indicator reading.
            #
            # It raises now. This is the same line drawn at 9a for a missing
            # ATR: without a stop and targets there is no risk plan to degrade
            # to, so there is nothing to continue with. engine_core's existing
            # error path reports it, and the reason travels with it.
            logger.error(f"Stop targets calculation failed: {e}")
            raise ValueError(
                f"Stop and target calculation failed ({type(e).__name__}: {e}). "
                f"No risk plan can be produced, and substituting default levels "
                f"would put a stop and three targets on the panel that were "
                f"never computed from this market."
            ) from e

    # ============================================================
    # POSITION SIZING — REMOVED AT SEQUENCE ITEM 13
    # ============================================================
    #
    # calculate_position_size() lived here. It took an account balance and a
    # risk percentage from config, divided a risk budget by the stop distance,
    # capped the result at 10x notional and then applied 0.5x / 0.8x haircuts
    # in stressed volatility.
    #
    # Viktor ruled on 29 August 2026 that the engine must not compute monetary
    # position sizing at all: sizing belongs to the portfolio/execution layer,
    # which is the only place that knows the real balance, the open exposure,
    # the correlation across positions and the venue's constraints. This engine
    # knows none of those and is never permitted to place a trade.
    #
    # The removal is not a tidy-up. A number labelled POSITION SIZE, produced
    # from a fixed 10,000 placeholder balance, is a specific instruction to risk
    # a specific amount — and the 10x cap and the volatility haircuts are
    # portfolio policy, decided here by whoever wrote the constants, invisible
    # to whoever reads the output. The engine's job ends at the structural
    # verdict, the stop and the targets. Converting those into a quantity is a
    # decision made with information that only exists downstream.

    # ============================================================
    # RISK REGIME CLASSIFICATION & VALIDATION
    # ============================================================

    def classify_risk_regime(self, volatility_state: str, stop_distance_pct: float) -> str:
        """
        Classifies current setup into a distinct risk regime profile.

        FIX 3, 6 October 2026: from volatility alone. The third parameter was
        trend_health until 11 September and ADX from then until this fix, and
        is gone. See the constants block at the top of this file for the
        ruling and the reasoning.

            EXTREME VOLATILITY, or a stop distance
            over REGIME_EXTREME_STOP_PCT               EXTREME RISK
            HIGH VOLATILITY                            HIGH VOLATILITY RISK
            MEDIUM VOLATILITY                          NORMAL RISK
            LOW VOLATILITY                             LOW RISK
            any other state                            UNKNOWN RISK

        The four named states are the ones models/bias_engine.py's
        calculate_dynamic_regime() produces from ATR / price. LOW VOLATILITY
        is LOW RISK without the strong-trend test that also stood here: the
        ruling left that mapping to the patch, and named LOW RISK as Claude's
        reading.

        The last line is the patch's own proposal, Viktor's to reverse. Until
        fix 3 every state not named here fell through to NORMAL RISK -- the
        engine's own UNKNOWN, and "NORMAL", which validate_risk_parameters'
        callers got by default. With volatility the only input, NORMAL RISK
        there would be a regime read from no measurement, so the label says
        so instead. UNKNOWN RISK keeps AGGRESSIVE out (decision_model.py
        allows it only at NORMAL RISK or LOW RISK) and decides nothing else:
        whether a trade is allowed at all stays risk_valid's question. On the
        engine's own path it is unreachable today. calculate_dynamic_regime
        says UNKNOWN only when the decision bar's ATR is absent or not
        finite, or its close is not a finite positive number, and on each of
        those the run raises before this is called -- engine_core when the
        ATR column is absent, calculate_stop_targets otherwise.

        Until fix 3 the paragraph here applied "missing means missing" to
        ADX: an unmeasured ADX pushed the regime neither up nor down. The
        same rule, applied to the one input left, is the last line of the
        table.
        """
        if volatility_state == "EXTREME VOLATILITY" or stop_distance_pct > REGIME_EXTREME_STOP_PCT:
            return "EXTREME RISK"
        if volatility_state == "HIGH VOLATILITY":
            return "HIGH VOLATILITY RISK"
        if volatility_state == "MEDIUM VOLATILITY":
            return "NORMAL RISK"
        if volatility_state == "LOW VOLATILITY":
            return "LOW RISK"
        return "UNKNOWN RISK"

    def validate_risk_parameters(
        self,
        current_price: float,
        atr_stop: float,
        volatility_state: str,
    ) -> Tuple[bool, str, str]:
        """
        Validates whether risk parameters are within safe operational thresholds.

        FIX 3, 6 October 2026: three parameters, all required. `adx` is gone
        with the regime's two ADX tests (see classify_risk_regime), and so is
        **kwargs, which is what made the by-name refusal described below
        necessary. A keyword this function does not take -- trend_health,
        adx, or a misspelt volatility_state -- is now refused by Python before
        the body runs, the way fix 1 refused trend_health in
        calculate_stop_targets. That closes the class the A6 comment in
        engine_core.py records, a bogus keyword absorbed and doing nothing,
        rather than adding a second refusal by name. volatility_state lost
        its default of "NORMAL", a state calculate_dynamic_regime never
        produces: the regime's one input is never supplied by a default.

        ITEM 14, 11 September 2026: the trend_health parameter is gone and ADX
        takes its place -- see the constants block at the top of this file.
        (ADX went in its turn at fix 3.)

        Two deliberate details in that swap, as they stood until fix 3:

        * The old default was `trend_health: float = 50.0`. A hardcoded 50.0 is
          the exact fabrication class the 7-8 September sweep removed everywhere
          else, and the A6 comment in engine_core.py records that this default
          was once live for every run. The new default is None, which
          classify_risk_regime() reads as "not measured" rather than as a
          middling market.

        * `trend_health` is REJECTED rather than ignored, below. This function
          takes **kwargs, so a caller left on the old signature would have had
          its trend_health silently swallowed and ADX silently defaulted to
          None -- the run would keep working and quietly stop being able to
          reach LOW RISK. That is precisely the A6 defect (a bogus kwarg
          absorbed by **kwargs, doing nothing) that this same function already
          carries a comment about. A structural fix rather than a note telling
          the next person to be careful. (Since fix 3 there is no **kwargs and
          no refusal in the body: Python refuses trend_health, with
          "unexpected keyword argument 'trend_health'".)

        ITEM 14 RE-AUDIT (Finding 5): now returns the risk regime alongside
        the pass/fail, rather than computing it and discarding everything but
        one comparison against "EXTREME RISK". decision_model.py needs the
        regime itself: risk_valid already gates whether a trade is allowed at
        all, and Item 14 is a second, independent question -- given that a
        trade IS allowed, how much risk is actually being taken, which
        risk_valid alone cannot answer (HIGH VOLATILITY RISK and NORMAL RISK
        both return risk_valid=True, and previously looked identical to
        every caller past this function).

        "UNKNOWN" in the three early-return branches: classify_risk_regime()
        was never reached, so there is nothing to report — those branches
        already fail risk_valid, so decision_model.py never reaches the
        AGGRESSIVE-gating logic for them regardless of this string.
        """
        try:
            if not (np.isfinite(current_price) and np.isfinite(atr_stop)):
                return False, "Price or stop level is not a finite number.", "UNKNOWN"
            if current_price <= 0 or atr_stop <= 0:
                return False, "Invalid price or stop levels.", "UNKNOWN"

            stop_dist_pct = (abs(current_price - atr_stop) / current_price) * 100.0

            if stop_dist_pct > MAX_STOP_DISTANCE_PCT:
                return False, (
                    f"Stop distance exceeds maximum allowable threshold "
                    f"({MAX_STOP_DISTANCE_PCT:.0f}%)."
                ), "UNKNOWN"
            if stop_dist_pct < MIN_STOP_DISTANCE_PCT:
                return False, "Stop distance too tight (risk of market noise liquidation).", "UNKNOWN"

            risk_regime = self.classify_risk_regime(volatility_state, stop_dist_pct)
            if risk_regime == "EXTREME RISK":
                return False, "Risk regime classified as EXTREME RISK.", risk_regime

            return True, "OK", risk_regime

        except Exception as e:
            # SEQUENCE ITEM 9b: examined and deliberately left alone.
            #
            # Step 5 listed "risk_model's direction-blind except-return" among
            # the fabrications. That is the one in calculate_stop_targets above.
            # This one is different in kind: it returns False — the trade is
            # NOT valid — and names the reason. It fails closed, and a caller
            # cannot mistake it for a passed check.
            #
            # Recorded rather than silently skipped so the re-audit at item 16
            # sees that both except-returns in this file were considered.
            logger.error(f"Risk validation failed: {e}")
            return False, f"Risk validation error: {str(e)}", "UNKNOWN"