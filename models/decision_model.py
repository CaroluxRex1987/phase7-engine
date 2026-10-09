from typing import Dict, Any, List, Tuple, Optional
import logging
import math

# GLM F-7, extended -- 6 September 2026. The verdict is read through one
# total function rather than with a permissive default at each call site.
# See models/risk_model.py's read_risk_verdict().
from models.risk_model import read_risk_verdict
# Fix 2, 5 October 2026: the confirmation sentence in _apply_signal_gate names
# the gate's ADX threshold, read from the gate's own constant so the sentence
# cannot drift from the rule it describes. The module is imported, not the
# name: a module-level MIN_TREND_ADX here would be a second, unlisted copy of
# a fingerprinted constant (tests/test_fingerprint_names_every_constant.py).
from models import entry_model

logger = logging.getLogger(__name__)


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        f = float(value)
        return f if f == f else default  # NaN check without importing numpy here
    except (ValueError, TypeError):
        return default


def asset_name(symbol: Any) -> str:
    """
    The traded asset's name for a sentence: "AEROUSDT" -> "AERO".

    21 SEPTEMBER 2026, work order B. Sequence item 12 put this inline in
    _compute_btc_adjusted when it removed a hardcoded "AERO" there; two more
    hardcoded "AERO" strings survived in core/panel_render.py's BTC section.
    One function now serves both, so the panel cannot drift from the reasoning
    text by carrying its own copy.

    N5, 9 OCTOBER 2026: the BTC-adjusted confidence and its sentence are gone
    (Viktor's ruling of 5 October, point 7: Bitcoin is reference only), so
    the panel's BTC section is this function's only caller. It stays in this
    module, where the one quote-currency list has lived since 21 September.

    The suffixes are tried longest first. The inline version tried "USD" before
    "BUSD", so "BUSD" could never match and ETHBUSD read as "ETHB". No pair the
    engine has been run on is affected: every recorded run is a USDT pair.
    """
    asset = str(symbol).upper()
    for suffix in ("USDT", "USDC", "BUSD", "USD"):
        if asset.endswith(suffix) and len(asset) > len(suffix):
            return asset[: -len(suffix)]
    return asset


# 5 SEPTEMBER 2026 -- VIKTOR'S RULING, and the mechanism chosen for it.
#
# HIS RULING: a directional action must require a minimum bias strength.
# _determine_final_action read only the raw_bias STRING, so a bias_score of 21
# -- barely past bias_engine's RAW_BIAS_THRESHOLD of 20 -- could return
# AGGRESSIVE LONG, printed directly above CONFIDENCE 21/100.
#
# THE MECHANISM. A separate constant rather than raising RAW_BIAS_THRESHOLD to
# 30, because the two answer different questions and both are needed:
#
#   RAW_BIAS_THRESHOLD (20)  does the blend lean far enough to CALL a side?
#                            It sets the label, and risk_model builds the plan
#                            shape from the sign either way.
#   MIN_ACTION_BIAS    (30)  is that lean strong enough to ACT on?
#
# Raising the first to 30 would have collapsed both into one number and lost
# the distinction between leaning bullish and being bullish enough to trade.
# The risk of two thresholds is the item-14 defect -- a constant nothing reads
# -- so tests/test_minimum_bias_strength.py holds both to being live, and this
# one is fingerprinted in core/decision_log.py so a change to it changes
# run_hash.
#
# 30 matches bias_engine's CONFIRMED threshold, where the state machine
# already draws the line between a lean and a conviction. Viktor named that
# value; making it a separate constant is Claude's call.
# FINDING 18, 27 September 2026: the state machine is now bias_label
# (models/bias_engine.py), a function of the current score -- it never had
# memory. Its 30 is a literal there, for the reason its comment gives; the
# label needs > 30 and this constant acts at >= 30, so at exactly 30.0 a run
# can take a side while the panel's BIAS line reads BULLISH or BEARISH, not
# CONFIRMED. Recorded, not changed.
MIN_ACTION_BIAS = 30.0


class DecisionModel:
    """
    Phase-7 central decision seam (Roadmap Layer 1: "Core Architecture").

    Original roadmap diagnosis: decision logic (_determine_final_action)
    was living inside signal_router.py, which is architecturally wrong --
    "Router contains decision logic (should not)." This module is the fix:
    the single place that turns {bias, trend, entry, risk} into
    {final_action, confidence, trade_quality, explanation}. (`structure` was
    a parameter too until the Item 11 re-audit removed the confidence
    calculation that was its only reader here -- see evaluate()'s comment.
    `macro_bias` was one until work order G, 27 September 2026, removed the
    CONSERVATIVE clause that was its only reader -- see
    _determine_final_action.)
    signal_router.py now just calls DecisionModel.evaluate(...) and
    assembles/renders the result -- it is a pure assembler, per the
    roadmap's stated architecture.

    confidence and trade_quality are first real, multi-factor outputs here
    -- previously confidence_score was just trend_health renamed. This is a
    V1: the roadmap's Layer 2 (multi-factor bias weighting) and Layer 5
    (entry multipliers) will feed richer inputs into this later without
    requiring another rewrite of this module's shape.

    C4 (advisory EV): risk_model.py's targets are always fixed at exactly
    1:1 / 2:1 / 3:1 reward:risk by construction (see risk_model.py's A12
    fix), averaging to a 2:1 reward multiple. That means an EV estimate
    doesn't need the actual target prices -- it's a fixed function of the
    reward multiple and an assumed win rate. This is explicitly NOT a
    backtested statistic -- it uses this decision's confidence score as a
    stand-in for "win rate," which is a simplifying assumption, not a
    measured fact. Purely a displayed number for you to read (per the
    plan's C4: "recommendations you read, not actions the engine takes").
    """

    AVG_REWARD_R = 2.0

    # The band around zero inside which ev_r is reported as breakeven rather
    # than positive or negative. Was a bare +/-0.3 literal inside _compute_ev;
    # named here so decision_log.module_snapshot() can see it and so the
    # confidence levels the EV sentence quotes are derived from it rather than
    # written out by hand. ROUND 6 F1's rule, applied to this module.
    EV_BREAKEVEN_BAND_R = 0.3

    # SEQUENCE ITEM 9a. Viktor's ruling of 29 August, verbatim: "When an
    # indicator fails, the engine continues in an explicitly degraded state. It
    # must not fabricate replacement values. The failure must be recorded in
    # the decision output, and confidence and trade quality must be reduced
    # accordingly. A degraded result does not by itself authorize trading."
    #
    # A CEILING RATHER THAN A PENALTY, and the choice is worth stating.
    #
    # A subtraction — "minus ten points per missing indicator" — would be a
    # number invented to look precise, and this project has spent a week
    # removing numbers invented to look precise. A ceiling says something the
    # engine can actually defend: however the arithmetic came out, an analysis
    # computed from incomplete inputs is not permitted to claim more than
    # moderate confidence.
    #
    # 50 because it is the midpoint, and the midpoint is the strongest honest
    # claim available when you do not know what you did not measure.
    DEGRADED_CONFIDENCE_CEILING = 50.0

    def evaluate(
        self,
        bias: Dict[str, Any],
        trend: Dict[str, Any],
        entry: Dict[str, Any],
        risk: Dict[str, Any],
        *,
        degradation: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        # WORK ORDER G, 27 September 2026 (finding 17): `macro_bias` was the
        # fifth positional parameter here and is gone -- see
        # _determine_final_action for why. Everything after `risk` is
        # keyword-only so that a caller still passing macro in fifth place
        # fails with a TypeError instead of having the string land silently
        # in btc_context.
        # N5, 9 October 2026: `btc_context` and `symbol` are gone too. Their
        # only reader was the BTC-adjusted confidence, removed by Viktor's
        # ruling of 5 October (point 7: Bitcoin is reference only). The `*`
        # stays, and matters more now: without it the fifth slot would be
        # `degradation`, and a stray "BULLISH" there would be read as seven
        # missing inputs -- list("BULLISH") -- and the run capped as degraded.
        # ITEM 11 RE-AUDIT (Finding 4): `structure` was a parameter here,
        # threaded into _compute_confidence to compute structure_alignment.
        # It is gone along with that term -- see _compute_confidence's
        # docstring. signal_router.py still reads structure.regime for its
        # own "structure" block; this method simply no longer needs a second
        # copy of it.
        reasons: List[str] = []
        degradation = list(degradation) if degradation else []

        # SUMMARY SOURCE, 20 September 2026. `summary` below was built from
        # reasons[-1], and _compute_ev appends to `reasons` last on every
        # path, so the one-line summary of every run was the illustrative EV
        # sentence -- tests/fixtures/golden_decision.json recorded
        # "NO-TRADE (RISK TOO HIGH) -- Expected value ... worth taking on
        # average" for a refused trade. The summary now names the reason
        # belonging to whichever stage last SET final_action. That stage is
        # tracked here rather than inferred from position: reasons[0] would
        # name a superseded action whenever _refuse_incoherent_plan or
        # _apply_degradation overrode the first one, and reasons[-1] is
        # whatever happened to append last.
        action_reason_index: Optional[int] = None

        before = len(reasons)
        final_action = self._determine_final_action(bias, trend, entry, risk, reasons=reasons)
        if len(reasons) > before:
            action_reason_index = len(reasons) - 1

        # WORK ORDER F, 21 September 2026: the confirmation gate. Runs before
        # the plan-coherence check so a vetoed trade never reaches it, and
        # before degradation, which only overrides actions naming a side --
        # so NO-TRADE (SIGNAL UNCONFIRMED) stands on a degraded run, with the
        # degradation notes appended to it.
        action_before_gate = final_action
        before = len(reasons)
        final_action = self._apply_signal_gate(final_action, bias, entry, reasons)
        if final_action != action_before_gate and len(reasons) > before:
            action_reason_index = len(reasons) - 1

        # The guard that would have caught 2 September's live run.
        #
        # Narrowing the direction source stops the two modules disagreeing for
        # the reason they disagreed that day. It cannot stop them disagreeing
        # for a reason nobody has thought of yet, and the cost of that class of
        # defect is not a wrong number on a panel -- it is an operator taking
        # the opposite side of the analysis. So the relationship is checked
        # rather than trusted.
        action_before_refusal = final_action
        before = len(reasons)
        final_action = self._refuse_incoherent_plan(final_action, risk, reasons)
        if final_action != action_before_refusal and len(reasons) > before:
            action_reason_index = len(reasons) - 1
        confidence = self._compute_confidence(bias, final_action, reasons)
        trade_quality = self._compute_trade_quality(trend, entry, final_action, reasons)

        if degradation:
            action_before_degradation = final_action
            before = len(reasons)
            final_action, confidence, trade_quality = self._apply_degradation(
                degradation, final_action, confidence, trade_quality, reasons
            )
            # Degradation appends its notes whether or not it changes the
            # action. Only a changed action moves the summary; a capped
            # confidence on an unchanged action does not.
            if final_action != action_before_degradation and len(reasons) > before:
                action_reason_index = len(reasons) - 1

        ev = self._compute_ev(confidence, final_action, reasons)

        # N5, 9 October 2026: the BTC-adjusted confidence was computed here,
        # after everything above had decided, and nothing that decides read
        # it -- only the record and the panel. Removed by Viktor's ruling of
        # 5 October (point 7: Bitcoin is reference only); the panel's BTC
        # section stays, printing what engine_core measured.

        if reasons:
            summary_index = action_reason_index if action_reason_index is not None else 0
            summary = f"{final_action} — {reasons[summary_index]}"
        else:
            summary = final_action

        explanation = {
            "summary": summary,
            "reasons": reasons,
        }

        return {
            "final_action": final_action,
            "confidence": confidence,
            "trade_quality": trade_quality,
            "ev": ev,
            "explanation": explanation,
        }

    SIGNAL_UNCONFIRMED = "NO-TRADE (SIGNAL UNCONFIRMED)"

    @staticmethod
    def _read_signal(entry: Any, side: str) -> Tuple[bool, List[str]]:
        """
        One side's confirmation ("long" or "short") and its blockers.

        Fails safe: a signal that is absent, malformed or contradicts its own
        blocker list is NOT a confirmation. An absent confirmation read as a
        present one would be the risk_valid=True default of GLM F-7 again.
        """
        entry = entry if isinstance(entry, dict) else {}
        signal = entry.get(f"{side}_signal")
        blockers = entry.get(f"{side}_signal_blockers")
        if not isinstance(signal, bool) or not isinstance(blockers, list):
            return False, ["the confirmation signal was not computed on this run, "
                           "and an absent confirmation is not a confirmation"]
        if signal != (len(blockers) == 0):
            return False, [f"the {side} signal ({signal}) contradicts its own "
                           f"blocker list ({len(blockers)} entries), so it "
                           "cannot be read as a confirmation"]
        return signal, [str(b) for b in blockers]

    def _apply_signal_gate(self, final_action: str, bias: Any, entry: Any,
                           reasons: List[str]) -> str:
        """
        VIKTOR'S RULING, 21 September 2026 (work order F): a trade the ladder
        chooses is taken only if that side's signal confirms it. The rule
        itself is documented above generate_entry_signals in
        models/entry_model.py.

        Priority, also his ruling: a risk refusal stays the label. When risk
        refused AND the bias direction is unconfirmed, the confirmation
        failure is appended to the reasons so the log shows both.
        """
        if any(side in final_action for side in ("LONG", "SHORT")):
            side = "long" if "LONG" in final_action else "short"
            confirmed, blockers = self._read_signal(entry, side)
            if confirmed:
                # Fix 2, 5 October 2026: "the trend is not flagged exhausted"
                # stood where ADX now does -- the flag left the gate.
                reasons.append(
                    f"Structural confirmation holds for the {side}: structure "
                    f"agrees with the direction, ADX is "
                    f"{entry_model.MIN_TREND_ADX:g} or "
                    f"more, and no momentum divergence points against it."
                )
                return final_action
            leaning = "bullish" if side == "long" else "bearish"
            reasons.append(
                f"This would have been {final_action}, but the {leaning} bias "
                f"lacked structural confirmation ({'; '.join(blockers)}), so no "
                f"trade is taken."
            )
            return self.SIGNAL_UNCONFIRMED

        if final_action == "NO-TRADE (RISK TOO HIGH)":
            raw_bias = str(bias.get("raw", "NEUTRAL")) if isinstance(bias, dict) else "NEUTRAL"
            if raw_bias in ("BULLISH", "BEARISH"):
                side = "long" if raw_bias == "BULLISH" else "short"
                confirmed, blockers = self._read_signal(entry, side)
                if not confirmed:
                    reasons.append(
                        f"Separately, the {raw_bias.lower()} bias also lacked "
                        f"structural confirmation ({'; '.join(blockers)}). The "
                        f"risk refusal is the label; this is recorded so the "
                        f"log shows both failures."
                    )
        return final_action

    @staticmethod
    def _plan_direction(risk: Dict[str, Any]) -> Optional[str]:
        """
        Which way the risk plan actually points, read off the plan itself.

        Derived from the targets rather than from any bias field, deliberately:
        a check that asks the same source the action asked cannot detect the
        two disagreeing. Targets ascending from the stop is a long; descending
        is a short. Returns None when there is no plan to read, which is a
        normal state -- a degraded run, or one with no ATR.
        """
        targets = risk.get("targets") if isinstance(risk, dict) else None
        if not isinstance(targets, (list, tuple)) or len(targets) < 2:
            return None
        try:
            first = float(targets[0])
            last = float(targets[-1])
        except (TypeError, ValueError):
            return None
        if not (math.isfinite(first) and math.isfinite(last)):
            return None
        if last > first:
            return "LONG"
        if last < first:
            return "SHORT"
        return None

    def _refuse_incoherent_plan(self, final_action, risk, reasons):
        """
        An action must never ship attached to a plan pointing the other way.

        On 2 September the engine printed CONSERVATIVE LONG with a stop above
        price and three descending targets. Every number in that plan was
        correctly computed; the label on it was not. An operator following the
        DECISION line would have bought an instrument the engine had just
        analysed, in detail and correctly, as a short.

        Refusing rather than relabelling. Picking a side here would mean this
        method deciding a trade direction on a disagreement it cannot
        adjudicate -- and one of the two sources is wrong, with no way to tell
        which from inside this function. NO-TRADE is the only answer available
        that is certainly not the wrong one.
        """
        if not any(side in final_action for side in ("LONG", "SHORT")):
            return final_action

        plan = self._plan_direction(risk)
        if plan is None:
            return final_action

        action_side = "LONG" if "LONG" in final_action else "SHORT"
        if plan == action_side:
            return final_action

        reasons.append(
            f"REFUSED: the decision came out {final_action}, and the risk plan "
            f"beneath it is a {plan.lower()} -- its targets run "
            f"{'up' if plan == 'LONG' else 'down'} from the stop. The action "
            f"and the levels were derived from different readings of "
            f"direction, and one of them is wrong. Which one cannot be "
            f"determined here, so no trade is authorized."
        )
        return "NO-TRADE (PLAN CONTRADICTS ACTION)"

    def _apply_degradation(self, degradation, final_action, confidence,
                           trade_quality, reasons):
        """
        Enforce the degrade ruling on a decision already computed.

        Three effects, in the order the ruling states them.

        1. The failure is recorded in the decision output. It is listed here in
           the reasoning the operator reads, not only in a structural field
           they might not look at.

        2. Confidence and trade quality are reduced. Capped, not penalised —
           see DEGRADED_CONFIDENCE_CEILING.

        3. A degraded result does not by itself authorize trading. Any action
           naming a side becomes NO-TRADE. WAIT and NO-TRADE are already not
           authorizations and are left as they are, with the reason added.

        Applied AFTER the normal computation rather than instead of it, on
        purpose: the engine still does the analysis it can, and the degraded
        state constrains what it is allowed to conclude from it. That is what
        distinguishes degrading from halting — halting would have thrown the
        analysis away.
        """
        missing = "; ".join(degradation)
        reasons.append(
            f"This run is DEGRADED: {missing}. The analysis was computed "
            f"without the input(s) named, so no trade is authorized on it "
            f"regardless of how the remaining scores came out."
        )

        capped_confidence = min(confidence, self.DEGRADED_CONFIDENCE_CEILING)
        capped_quality = {
            "proposed_entry": min(trade_quality.get("proposed_entry", 0.0),
                                  self.DEGRADED_CONFIDENCE_CEILING),
        }

        if capped_confidence < confidence:
            reasons.append(
                f"Confidence is capped at {self.DEGRADED_CONFIDENCE_CEILING:.0f}/100 "
                f"for this run (the uncapped score was {confidence:.0f}/100). "
                f"An analysis missing inputs cannot claim more than moderate "
                f"confidence, whatever the parts that did compute say."
            )

        if any(side in final_action for side in ("LONG", "SHORT")):
            reasons.append(
                f"The action would have been {final_action}; a degraded run "
                f"cannot authorize a trade, so it is NO-TRADE."
            )
            final_action = "NO-TRADE (DEGRADED INPUT)"

        return final_action, capped_confidence, capped_quality

    # ============================================================
    # FINAL ACTION (moved here verbatim from signal_router.py's
    # _determine_final_action -- same tested logic, just relocated to the
    # architecturally correct place, per the roadmap's own diagnosis)
    # ============================================================

    # ROUND 6 (Meta Muse Spark 1.3), F1 follow-up, 13 September 2026:
    # promoted from bare literals inside _determine_final_action below,
    # values unchanged. The pair (trend health >= 75, entry score >= 70)
    # is the line between AGGRESSIVE-eligible and plain LONG/SHORT; the
    # single 50 is the line between CONSERVATIVE and WAIT. (It read "when
    # macro agrees" until work order G, 27 September 2026, removed the
    # macro condition.) Named and fingerprinted like every other decision-affecting
    # number in this file (AVG_REWARD_R, DEGRADED_CONFIDENCE_CEILING
    # above; BTC_ADJUSTMENT_CAP and BTC_STRESS_PENALTY stood below until N5,
    # 9 October 2026) -- see core/decision_log.py's FINGERPRINTED_MODULES
    # entry for this class.
    #
    # RAW_BIAS_THRESHOLD (models/bias_engine.py) and MIN_ACTION_BIAS above
    # were mentioned in the same audit finding, alongside these three, but
    # neither needed this fix: both are already named module-level
    # constants and both are already fingerprinted (see
    # FINGERPRINTED_MODULES/FINGERPRINTED_CONFIG). They are deliberately
    # two different thresholds answering two different questions -- see
    # MIN_ACTION_BIAS's own comment above for why -- not a naming
    # inconsistency to reconcile, and nothing about that pair changes here.
    AGGRESSIVE_TREND_HEALTH_MIN = 75.0
    AGGRESSIVE_ENTRY_SCORE_MIN = 70.0
    CONSERVATIVE_TREND_HEALTH_MIN = 50.0

    def _conservative_reason(self, leaning: str, side: str, trend_note: str,
                             trend_health: float, entry_score: float) -> str:
        """
        The CONSERVATIVE sentence, naming what kept the setup below the
        LONG/SHORT tier.

        WORK ORDER G, 27 September 2026. The sentence read "...but the entry
        quality (N/100) isn't strong enough" in every case. The tier is also
        reached with a strong entry and trend strength between the
        CONSERVATIVE and upper-tier lines, and then the sentence blamed a
        number that had passed. Item 8's class: the engine asserting
        something that is not so, in the line the operator reads first.
        Viktor ruled to fix it inside G, since G rewrites this sentence.

        One helper for both sides, so the two cannot drift apart. The
        thresholds are read from the constants the ladder compares against,
        so the sentence cannot quote a number the ladder does not use.
        """
        trend_short = trend_health < self.AGGRESSIVE_TREND_HEALTH_MIN
        entry_short = entry_score < self.AGGRESSIVE_ENTRY_SCORE_MIN
        trend_min = f"{self.AGGRESSIVE_TREND_HEALTH_MIN:.0f}"
        entry_min = f"{self.AGGRESSIVE_ENTRY_SCORE_MIN:.0f}"
        if trend_short and entry_short:
            detail = (f"below the {trend_min} the {side} tier needs, and the "
                      f"entry quality ({entry_score:.0f}/100) is below its {entry_min}")
        elif trend_short:
            detail = (f"below the {trend_min} the {side} tier needs, with entry "
                      f"quality {entry_score:.0f}/100")
        else:
            # entry_short alone. Neither short cannot reach this helper: the
            # ladder's upper-tier branch returns before the CONSERVATIVE one.
            detail = (f"but the entry quality ({entry_score:.0f}/100) is below "
                      f"the {entry_min} the {side} tier needs")
        return f"Bias is {leaning}, {trend_note}, {detail} — CONSERVATIVE {side}."

    def _determine_final_action(
        self,
        bias: Dict[str, Any],
        trend: Dict[str, Any],
        entry: Dict[str, Any],
        risk: Dict[str, Any],
        *,
        reasons: List[str],
    ) -> str:
        """
        Multi-factor decision engine mapping quantitative states to final trade actions:
        - LONG / CONSERVATIVE LONG / AGGRESSIVE LONG
        - SHORT / CONSERVATIVE SHORT / AGGRESSIVE SHORT
        - WAIT
        - NO-TRADE (RISK NOT ASSESSED)
        - NO-TRADE (RISK TOO HIGH)
        """
        try:
            if not all(isinstance(d, dict) for d in [bias, trend, entry, risk]):
                logger.warning("Invalid input types for decision engine, defaulting to WAIT")
                reasons.append("Some of the engine's inputs came back malformed, so no decision could be made safely — waiting.")
                return "WAIT"

            # GLM F-7 AS EXTENDED, 6 September 2026. This line read
            #
            #     risk_valid = bool(risk.get("risk_valid", True))
            #
            # and this is the authorization gate. A risk block with no
            # verdict in it means risk was never assessed, and the default
            # turned that into a pass -- the engine's own permission to
            # trade, granted by the absence of the check.
            #
            # Two states, two answers, and they are not the same NO-TRADE.
            # "RISK TOO HIGH" says the check ran and failed, and the reason
            # string names what failed. An unassessed block has no such
            # reason to give, and printing "Risk check failed (OK)" -- which
            # is what a bare flip of the default to False would have printed,
            # since risk_reason defaults to "OK" -- would be the same
            # fabrication wearing the opposite sign.
            risk_verdict = read_risk_verdict(risk)
            if risk_verdict is None:
                reasons.append(
                    "REFUSED: the risk block carries no pass/fail verdict, so "
                    "risk was never assessed on this run. An unassessed check "
                    "is not a passed check, and no trade is authorized on one."
                )
                return "NO-TRADE (RISK NOT ASSESSED)"

            risk_valid = risk_verdict
            risk_reason = str(risk.get("risk_reason", "OK"))
            if not risk_valid:
                reasons.append(f"Risk check failed ({risk_reason}), so no trade is allowed right now.")
                return "NO-TRADE (RISK TOO HIGH)"

            # ITEM 14 RE-AUDIT (Finding 5): risk_regime is read here as its
            # own, independent input -- see models/risk_model.py's
            # classify_risk_regime(), which computed this all along but
            # discarded everything except the EXTREME RISK/not-EXTREME
            # boolean already folded into risk_valid above. It gates action
            # INTENSITY only -- whether "AGGRESSIVE" may be used -- never
            # direction and never whether a trade is allowed at all; that is
            # what risk_valid above already decided. Conviction (trend
            # health, entry quality) and risk are now two separate checks
            # instead of one number standing in for both, per the audit's
            # required action: "directional conviction must never be treated
            # as equivalent to risk."
            risk_regime = str(risk.get("risk_regime", "UNKNOWN RISK"))
            aggressive_allowed = risk_regime in ("NORMAL RISK", "LOW RISK")

            validation_state = str(risk.get("validation_state", "NEUTRAL"))
            # SEQUENCE ITEM 13: this read trend["health"] first and fell back
            # to trend["trend_health"]. Both held the same number, but the
            # duplicate was the preferred one, so the canonical field could have
            # been changed here without any effect. "health" is now gone.
            trend_health = _safe_float(trend.get("trend_health", float("nan")), default=float("nan"))
            entry_score = _safe_float(entry.get("score", 0.0))
            entry_status = str(entry.get("entry_status", ""))
            # WORK ORDER F, 21 September 2026: `divergence` was read here
            # and vetoed the two upper tiers whichever way it pointed, while
            # CONSERVATIVE had no divergence check at all. Divergence is now
            # judged in ONE place -- the confirmation gate
            # (_apply_signal_gate, after this function), which blocks every
            # tier on a divergence pointing against the trade and none on one
            # pointing with it. Viktor ruled the direction rule; removing this
            # second, disagreeing rule was Claude's call under his delegation.
            # Consequence, predicted: an upper-tier setup with a divergence
            # against it used to fall through to CONSERVATIVE or WAIT and now
            # reaches the gate and becomes NO-TRADE (SIGNAL UNCONFIRMED); one
            # with a divergence pointing its own way is no longer demoted.
            entry_active = "ACTIVE" in entry_status.upper()

            raw_bias = str(bias.get("raw", "NEUTRAL"))

            # 5 SEPTEMBER 2026: the magnitude, not only the label.
            bias_strength = abs(_safe_float(bias.get("score"), 0.0))

            # 5 SEPTEMBER 2026 -- VIKTOR'S RULING. trend_health is an UNSIGNED
            # magnitude: a strong DOWNtrend also scores 90. The reason strings
            # below read "Bias is bullish with strong trend health (90/100)",
            # offering a direction-blind number as support for a direction --
            # the same 90 would have appeared if the trend ran the other way.
            #
            # trend_direction_sign arrived on 4 September for exactly this
            # reason. Used here, the sentence can no longer imply support the
            # number does not give: it names the direction beside the magnitude
            # and lets the reader see when the two disagree.
            trend_sign = int(_safe_float(trend.get("trend_direction_sign"), 0.0))
            _dir_word = "up" if trend_sign > 0 else ("down" if trend_sign < 0 else "flat")
            # 21 SEPTEMBER 2026, work order B: trend_health is NaN when it
            # was not measured (read above with a NaN default), and ":.0f"
            # printed that as "trend strength nan/100" in Decision Reasoning.
            _strength = (f"{trend_health:.0f}/100" if math.isfinite(trend_health)
                         else "not computed")
            trend_note = f"trend strength {_strength} ({_dir_word})"

            # VIKTOR'S RULING, 2 September 2026: bias is the sole direction
            # source. This block used to read
            #
            #     if raw_bias == "BULLISH" or long_signal or macro_bias == "BULLISH":
            #
            # and the bearish block below it mirrored that. Three independent
            # sources could each open a direction, the first block to match
            # returned, and nothing ever compared the answer against the risk
            # plan -- which risk_model builds from `detailed_bias` alone.
            #
            # Found by running the engine on live data, 2 September. AEROUSDT
            # 4h came back BEARISH CONFIRMED on every measure the engine has --
            # bearish regime, bearish structure, an LH-LL sequence, strong
            # bearish distribution, SuperTrend freshly flipped bearish -- with a
            # BULLISH macro read. The macro clause alone entered the bullish
            # block; `trend_health >= 50` passed because trend health is an
            # UNSIGNED magnitude and a strong bearish trend scores 69; and the
            # engine printed CONSERVATIVE LONG above a stop ABOVE price and
            # three targets BELOW it. A long label on a short plan.
            #
            # It also printed "Bias is bullish and the broader macro trend
            # agrees" while its own Validation Notes said the higher timeframe
            # DISAGREED. Two contradictory claims in one panel, and the first
            # of them false -- Item 8's class, in the module that picks the side.
            #
            # Why bias rather than macro: macro is ALREADY inside bias_score as
            # a 10% weighted factor. Letting it also override the blend counts
            # one piece of evidence twice, which is Item 11 in the module that
            # decides direction. It has had its vote.
            #
            # long_signal / short_signal are gone from here for the same
            # reason, not as tidying: an entry-zone signal that can open a
            # direction against the engine's own bias is the identical defect
            # wearing a different name. They remain available in `entry` for a
            # future ruling on whether they should CONFIRM a direction bias has
            # already chosen; they may no longer choose one.
            #
            # RULED 21 September 2026 (work order F): they confirm. See
            # _apply_signal_gate, which runs after this function returns.

            if validation_state == "WEAK" and trend_health < 40:
                reasons.append(
                    f"Validation is weak and trend health is low ({trend_health:.0f}/100) — waiting for a cleaner setup."
                )
                return "WAIT"

            # VIKTOR'S RULING, 5 September 2026: a lean is not a case.
            if raw_bias in ("BULLISH", "BEARISH") and bias_strength < MIN_ACTION_BIAS:
                reasons.append(
                    f"Bias leans {raw_bias.lower()} but only at {bias_strength:.0f}/100, "
                    f"below the {MIN_ACTION_BIAS:.0f} needed to act on a direction — WAIT."
                )
                return "WAIT"

            # WORK ORDER G, 27 September 2026 (finding 17). Both CONSERVATIVE
            # branches below read
            #
            #     elif trend_health >= ... and macro_bias == "BULLISH":
            #
            # (and "BEARISH" in the short branch): a hard requirement on
            # evidence already weighted into bias_score at 10% -- the double
            # count Viktor removed from the entry signal at work order F, and
            # the one his ruling of 2 September removed from direction. The
            # upper tiers never had it; only the tier with the weakest case
            # did. Claude's call under Viktor's delegation. Removed, and
            # macro_bias removed from this function and from evaluate(), since
            # nothing here read it after that. The router still records it.
            #
            # Predicted consequence, recorded: a directional bias at
            # CONSERVATIVE strength with a disagreeing or neutral macro used
            # to be WAIT and now reaches the confirmation gate as CONSERVATIVE
            # LONG/SHORT. In the live log of 27 September (43 runs) that is 2
            # runs, both on 15 September.
            #
            # What still reads macro, unchanged here: bias_score's 10% factor,
            # the entry score's confluence multiplier, and the validation
            # score. Those are the weighting questions ruled for after the
            # independent audit (DECISIONS, 22 September 2026).
            if raw_bias == "BULLISH":
                if (trend_health >= self.AGGRESSIVE_TREND_HEALTH_MIN
                        and entry_score >= self.AGGRESSIVE_ENTRY_SCORE_MIN):
                    if entry_active and aggressive_allowed:
                        reasons.append(
                            f"Bias is bullish, {trend_note}, with a "
                            f"high-quality, active entry ({entry_score:.0f}/100) "
                            f"and a {risk_regime.lower()} — AGGRESSIVE LONG."
                        )
                        return "AGGRESSIVE LONG"
                    if entry_active and not aggressive_allowed:
                        reasons.append(
                            f"Bias is bullish, {trend_note}, with a "
                            f"high-quality, active entry ({entry_score:.0f}/100) would otherwise qualify as "
                            f"AGGRESSIVE, but the risk regime is {risk_regime} — directional conviction does "
                            f"not override risk, so this stays LONG."
                        )
                        return "LONG"
                    reasons.append(
                        f"Bias is bullish, {trend_note}, with a high-quality "
                        f"entry ({entry_score:.0f}/100) — LONG."
                    )
                    return "LONG"
                elif trend_health >= self.CONSERVATIVE_TREND_HEALTH_MIN:
                    reasons.append(self._conservative_reason(
                        "bullish", "LONG", trend_note, trend_health, entry_score))
                    return "CONSERVATIVE LONG"

            if raw_bias == "BEARISH":
                if (trend_health >= self.AGGRESSIVE_TREND_HEALTH_MIN
                        and entry_score >= self.AGGRESSIVE_ENTRY_SCORE_MIN):
                    if entry_active and aggressive_allowed:
                        reasons.append(
                            f"Bias is bearish, {trend_note}, with a "
                            f"high-quality, active entry ({entry_score:.0f}/100) "
                            f"and a {risk_regime.lower()} — AGGRESSIVE SHORT."
                        )
                        return "AGGRESSIVE SHORT"
                    if entry_active and not aggressive_allowed:
                        reasons.append(
                            f"Bias is bearish, {trend_note}, with a "
                            f"high-quality, active entry ({entry_score:.0f}/100) would otherwise qualify as "
                            f"AGGRESSIVE, but the risk regime is {risk_regime} — directional conviction does "
                            f"not override risk, so this stays SHORT."
                        )
                        return "SHORT"
                    reasons.append(
                        f"Bias is bearish, {trend_note}, with a high-quality "
                        f"entry ({entry_score:.0f}/100) — SHORT."
                    )
                    return "SHORT"
                elif trend_health >= self.CONSERVATIVE_TREND_HEALTH_MIN:
                    reasons.append(self._conservative_reason(
                        "bearish", "SHORT", trend_note, trend_health, entry_score))
                    return "CONSERVATIVE SHORT"

            reasons.append(
                f"No side has a strong enough, well-aligned case right now ({trend_note}, "
                f"entry quality {entry_score:.0f}/100) — waiting for a better setup."
            )
            return "WAIT"

        except Exception as e:
            logger.error(f"Decision engine evaluation failed: {e}")
            reasons.append("The decision engine hit an unexpected error, so it defaulted to WAIT as a safe fallback.")
            return "WAIT"

    # ============================================================
    # CONFIDENCE (new, real multi-factor score -- previously just a
    # trend_health passthrough)
    # ============================================================

    def _compute_confidence(
        self,
        bias: Dict[str, Any],
        final_action: str,
        reasons: List[str],
    ) -> float:
        """
        Confidence is bias_score's own magnitude, and nothing else.

        ITEM 11 RE-AUDIT (Finding 4), the second half. Sequence item 11
        removed a direct `trend_health * 0.3` term because trend health
        already reaches bias_score at WEIGHT_TREND_HEALTH = 0.30 inside
        bias_engine.py. This removes the two terms that survived that pass
        and that the auditor's Finding 4 named specifically:

            structure_alignment   +/-10 to +/-15 if structure_regime agreed
                                   or disagreed with raw_bias
            validation_adj        +/-10 to -15 from risk.validation_state,
                                   which engine_core.py built from macro_bias
                                   agreement and volume_sentiment strength

        structure_regime, macro_bias and volume_sentiment are not new
        evidence at this point in the pipeline -- they are three of the six
        weighted factors bias_engine.calculate_dynamic_bias() already blended
        into bias_score, at 0.20, 0.10 and 0.15 respectively (see that
        module's dependency-graph comment). Adding structure_alignment and
        validation_adj on top counted each of them a second time, and let the
        confidence explanation describe that repetition as independent
        confirmation -- literally the auditor's concrete scenario: "structure
        agrees with the bullish bias, and validation is strong," about a
        bias score those same two facts had already produced.

        The dependency graph, stated rather than left to be reconstructed:
        bias_score already IS the multi-factor consensus (trend health,
        structure regime, volume sentiment, SuperTrend direction, macro bias,
        reversal/continuation). Confidence reports how decisively that
        consensus committed to a direction; it does not re-derive an opinion
        from any of the six factors, because there is no genuinely
        independent input left to check them against. entry_score is the
        nearest candidate, and it already shares macro_bias, trend_direction
        and structure_sequence with bias_score (see engine_core.py's call
        into calculate_entry_quality) -- folding it in here would reproduce
        the same defect through a fourth path rather than fix it.

        Ruled by Viktor, 31 August 2026 (delegated). No rescale needed:
        bias_strength already spans 0-100 on its own (bias_score is clipped
        to +/-100 in bias_engine.py), so removing the two additive terms
        does not shrink confidence's own range the way removing the old
        trend_health term once did.
        """
        confidence = min(100.0, abs(_safe_float(bias.get("score"), 0.0)))

        # When the risk-regime gate has already blocked the trade, make clear this
        # confidence score describes how the picture lines up, not a green light --
        # otherwise a high number here right after "NO-TRADE" reads as contradictory.
        # SWEEP ITEM 13, 8 September 2026. Previous text blamed "the risk
        # check above" on every NO-TRADE, including PLAN CONTRADICTS ACTION
        # and DEGRADED INPUT. Only attach that clause when the action itself
        # names risk.
        qualifier = (
            " This reflects how the picture lines up, not a green light — the risk check above is what's blocking the trade."
            if final_action.startswith("NO-TRADE") and "RISK" in final_action.upper()
            else (
                " This reflects how the picture lines up, not a green light — the trade is blocked for the reason named in the action."
                if final_action.startswith("NO-TRADE")
                else ""
            )
        )

        reasons.append(
            f"Confidence is {confidence:.0f}/100 — the bias engine's own composite "
            f"strength (trend health, structure regime, volume sentiment, SuperTrend "
            f"direction, macro bias, and reversal/continuation, already weighted and "
            f"blended into one score). Restating any of those as a separate bonus here "
            f"would count the same evidence twice.{qualifier}"
        )
        return float(confidence)

    # ============================================================
    # TRADE QUALITY (formalizes what the panel already showed as
    # "Current Market" / "Proposed Entry" -- now owned here instead of
    # being computed ad hoc where the panel happened to read it from)
    # ============================================================

    def _compute_trade_quality(
        self,
        trend: Dict[str, Any],
        entry: Dict[str, Any],
        final_action: str,
        reasons: List[str],
    ) -> Dict[str, float]:
        # SEQUENCE ITEM 11: `current_market` was
        #     _safe_float(trend.get("trend_health", ...))
        # — trend health verbatim, under a third name. The panel printed it as
        # TREND, again as MOMENTUM's number, and again here as Current Market,
        # then this sentence compared the entry against it as though that were
        # an independent yardstick. It is the same measurement three times.
        #
        # Removed rather than replaced with an invented metric: a reader has
        # TREND and ENTRY QUALITY on the panel already and can compare them.
        # Inventing a distinct "market backdrop" score would be new-feature
        # work, and Step 5's own guidance sides with removal.
        proposed_entry = _safe_float(entry.get("score"), 0.0)

        if proposed_entry >= 70:
            quality_phrase = "a high-quality entry on its own terms"
        elif proposed_entry >= 50:
            quality_phrase = "a workable entry"
        else:
            quality_phrase = "a weak entry"

        reasons.append(
            f"Entry quality is {proposed_entry:.0f}/100 — {quality_phrase}. "
            f"Compare it against the TREND line rather than against a restatement "
            f"of it."
        )

        return {
            "proposed_entry": float(proposed_entry),
        }

    # ============================================================
    # EV (C4 build -- new, illustrative-only)
    # ============================================================

    def _compute_ev(
        self,
        confidence: float,
        final_action: str,
        reasons: List[str],
    ) -> Dict[str, float]:
        """
        EV = (win_rate x average reward) - (loss_rate x 1), expressed in "R"
        (multiples of what's being risked). Uses confidence/100 as a stand-in
        for win rate and AVG_REWARD_R (2.0, the average of risk_model.py's
        fixed 1:1/2:1/3:1 targets) as the reward side. Not a measured,
        backtested number.

        It is also not a check on the confidence score. With the reward
        multiple fixed, this is a linear rescaling of confidence -- the two
        move together by construction and cannot disagree -- so it was
        described as a "sanity-check translation" for longer than it should
        have been. The reason string says what it is instead.
        """
        win_rate = max(0.0, min(1.0, confidence / 100.0))
        ev_r = (win_rate * self.AVG_REWARD_R) - ((1.0 - win_rate) * 1.0)

        # WHAT THIS NUMBER IS, 20 September 2026. ev_r is a straight-line
        # restatement of confidence: with a fixed reward multiple R,
        # ev_r = confidence/100 x (R + 1) - 1. It carries no information
        # confidence does not already carry and cannot disagree with it, so
        # it is not a second opinion and the sentence below no longer reads
        # like one. The two confidence levels quoted are derived from
        # AVG_REWARD_R and EV_BREAKEVEN_BAND_R rather than written out, so
        # changing either constant moves the sentence with it.
        breakeven_confidence = 100.0 / (self.AVG_REWARD_R + 1.0)
        positive_confidence = (
            (1.0 + self.EV_BREAKEVEN_BAND_R) * 100.0 / (self.AVG_REWARD_R + 1.0)
        )

        if ev_r > self.EV_BREAKEVEN_BAND_R:
            ev_phrase = "positive -- worth taking on average if that win rate holds up"
        elif ev_r < -self.EV_BREAKEVEN_BAND_R:
            ev_phrase = "negative -- would lose money on average even at that win rate"
        else:
            ev_phrase = "close to breakeven"

        qualifier = (
            " (this is hypothetical, since no trade is actually being suggested right now)"
            if not any(side in final_action for side in ("LONG", "SHORT"))
            else ""
        )

        reasons.append(
            f"Expected value (illustrative, not backtested): the {confidence:.0f}/100 confidence score restated "
            f"against the standard {self.AVG_REWARD_R:.0f}:1 average reward, not a second reading of the setup — "
            f"it is arithmetic on confidence alone, so it can never disagree with it. On that basis about "
            f"{ev_r:+.2f}R per trade — {ev_phrase}{qualifier}. On this reward multiple any confidence above "
            f"{breakeven_confidence:.0f}/100 is breakeven or better, and above {positive_confidence:.0f}/100 reads as positive."
        )

        return {
            "ev_r": float(ev_r),
            "assumed_win_rate": float(win_rate * 100.0),
            "avg_reward_r": float(self.AVG_REWARD_R),
        }

    # ============================================================
    # BTC-ADJUSTED CONFIDENCE -- removed, N5, 9 October 2026
    # ============================================================
    #
    # _compute_btc_adjusted stood here, with BTC_ADJUSTMENT_CAP (20.0) and
    # BTC_STRESS_PENALTY (15.0): a second confidence figure, moved by up to
    # 20 points either way -- BTC's bias strength times the pair's signed
    # correlation, signed by whether BTC's side agreed -- and by 15 down
    # under broad market stress, printed beside the real confidence with a
    # sentence explaining it. It ran after the action, confidence, trade
    # quality and EV were set, and nothing that decides read it: only the
    # record and the panel. Nothing had tested whether it predicted anything
    # (the 15 September PDF's point 3; the Part 7 document's N5).
    #
    # VIKTOR'S RULING, 5 October 2026 (point 7 of round 8's triage, by
    # agreeing to Claude's suggestion): Bitcoin is reference only, "for
    # bearing, not a mandatory thing". The panel's line goes and the BTC
    # section stays. Whether the computation and its record field went with
    # the line was left to the patch; they do, the reading the ruling named
    # as Claude's.
