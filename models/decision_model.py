from typing import Dict, Any, List, Tuple, Optional
import logging
import math

logger = logging.getLogger(__name__)


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        f = float(value)
        return f if f == f else default  # NaN check without importing numpy here
    except (ValueError, TypeError):
        return default


class DecisionModel:
    """
    Phase-7 central decision seam (Roadmap Layer 1: "Core Architecture").

    Original roadmap diagnosis: decision logic (_determine_final_action)
    was living inside signal_router.py, which is architecturally wrong --
    "Router contains decision logic (should not)." This module is the fix:
    the single place that turns {bias, trend, entry, risk, macro_bias} into
    {final_action, confidence, trade_quality, explanation}. (`structure` was
    a parameter too until the Item 11 re-audit removed the confidence
    calculation that was its only reader here -- see evaluate()'s comment.)
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
        macro_bias: str,
        btc_context: Optional[Dict[str, Any]] = None,
        degradation: Optional[List[str]] = None,
        symbol: str = "this asset",
    ) -> Dict[str, Any]:
        # ITEM 11 RE-AUDIT (Finding 4): `structure` was a parameter here,
        # threaded into _compute_confidence to compute structure_alignment.
        # It is gone along with that term -- see _compute_confidence's
        # docstring. signal_router.py still reads structure.regime for its
        # own "structure" block; this method simply no longer needs a second
        # copy of it.
        reasons: List[str] = []
        degradation = list(degradation) if degradation else []

        final_action = self._determine_final_action(bias, trend, entry, risk, macro_bias, reasons)

        # The guard that would have caught 2 September's live run.
        #
        # Narrowing the direction source stops the two modules disagreeing for
        # the reason they disagreed that day. It cannot stop them disagreeing
        # for a reason nobody has thought of yet, and the cost of that class of
        # defect is not a wrong number on a panel -- it is an operator taking
        # the opposite side of the analysis. So the relationship is checked
        # rather than trusted.
        final_action = self._refuse_incoherent_plan(final_action, risk, reasons)
        confidence = self._compute_confidence(bias, final_action, reasons)
        trade_quality = self._compute_trade_quality(trend, entry, final_action, reasons)

        if degradation:
            final_action, confidence, trade_quality = self._apply_degradation(
                degradation, final_action, confidence, trade_quality, reasons
            )

        ev = self._compute_ev(confidence, final_action, reasons)

        # BTC-adjusted confidence deliberately builds its OWN, separate
        # reasons list (not appended to `reasons`/explanation above) -- it's
        # shown in its own panel section, not folded into Decision
        # Reasoning, so it never grows that section further.
        btc_adjusted = self._compute_btc_adjusted(confidence, bias, btc_context, symbol)

        explanation = {
            "summary": f"{final_action} — {reasons[-1]}" if reasons else final_action,
            "reasons": reasons,
        }

        return {
            "final_action": final_action,
            "confidence": confidence,
            "trade_quality": trade_quality,
            "ev": ev,
            "btc_adjusted": btc_adjusted,
            "explanation": explanation,
        }

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

    def _determine_final_action(
        self,
        bias: Dict[str, Any],
        trend: Dict[str, Any],
        entry: Dict[str, Any],
        risk: Dict[str, Any],
        macro_bias: str,
        reasons: List[str],
    ) -> str:
        """
        Multi-factor decision engine mapping quantitative states to final trade actions:
        - LONG / CONSERVATIVE LONG / AGGRESSIVE LONG
        - SHORT / CONSERVATIVE SHORT / AGGRESSIVE SHORT
        - WAIT
        - NO-TRADE (RISK TOO HIGH)
        """
        try:
            if not all(isinstance(d, dict) for d in [bias, trend, entry, risk]):
                logger.warning("Invalid input types for decision engine, defaulting to WAIT")
                reasons.append("Some of the engine's inputs came back malformed, so no decision could be made safely — waiting.")
                return "WAIT"

            risk_valid = bool(risk.get("risk_valid", True))
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
            risk_regime = str(risk.get("risk_regime", "NORMAL RISK"))
            aggressive_allowed = risk_regime not in ("HIGH VOLATILITY RISK", "EXTREME RISK")

            validation_state = str(risk.get("validation_state", "NEUTRAL"))
            # SEQUENCE ITEM 13: this read trend["health"] first and fell back
            # to trend["trend_health"]. Both held the same number, but the
            # duplicate was the preferred one, so the canonical field could have
            # been changed here without any effect. "health" is now gone.
            trend_health = _safe_float(trend.get("trend_health", 50.0))
            entry_score = _safe_float(entry.get("score", 0.0))
            entry_status = str(entry.get("entry_status", ""))
            divergence = bool(trend.get("momentum_divergence", False))
            entry_active = "ACTIVE" in entry_status.upper()

            raw_bias = str(bias.get("raw", "NEUTRAL"))

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

            if validation_state == "WEAK" and trend_health < 40:
                reasons.append(
                    f"Validation is weak and trend health is low ({trend_health:.0f}/100) — waiting for a cleaner setup."
                )
                return "WAIT"

            if raw_bias == "BULLISH":
                if trend_health >= 75 and entry_score >= 70 and not divergence:
                    if entry_active and aggressive_allowed:
                        reasons.append(
                            f"Bias is bullish with strong trend health ({trend_health:.0f}/100) and a "
                            f"high-quality, active entry ({entry_score:.0f}/100), with no momentum divergence "
                            f"and a {risk_regime.lower()} — AGGRESSIVE LONG."
                        )
                        return "AGGRESSIVE LONG"
                    if entry_active and not aggressive_allowed:
                        reasons.append(
                            f"Bias is bullish with strong trend health ({trend_health:.0f}/100) and a "
                            f"high-quality, active entry ({entry_score:.0f}/100) would otherwise qualify as "
                            f"AGGRESSIVE, but the risk regime is {risk_regime} — directional conviction does "
                            f"not override risk, so this stays LONG."
                        )
                        return "LONG"
                    reasons.append(
                        f"Bias is bullish with strong trend health ({trend_health:.0f}/100) and a high-quality "
                        f"entry ({entry_score:.0f}/100), with no momentum divergence — LONG."
                    )
                    return "LONG"
                elif trend_health >= 50 and macro_bias == "BULLISH":
                    reasons.append(
                        f"Bias is bullish and the broader macro trend agrees, with decent trend health "
                        f"({trend_health:.0f}/100), but the entry quality ({entry_score:.0f}/100) isn't strong "
                        f"enough — CONSERVATIVE LONG."
                    )
                    return "CONSERVATIVE LONG"

            if raw_bias == "BEARISH":
                if trend_health >= 75 and entry_score >= 70 and not divergence:
                    if entry_active and aggressive_allowed:
                        reasons.append(
                            f"Bias is bearish with strong trend health ({trend_health:.0f}/100) and a "
                            f"high-quality, active entry ({entry_score:.0f}/100), with no momentum divergence "
                            f"and a {risk_regime.lower()} — AGGRESSIVE SHORT."
                        )
                        return "AGGRESSIVE SHORT"
                    if entry_active and not aggressive_allowed:
                        reasons.append(
                            f"Bias is bearish with strong trend health ({trend_health:.0f}/100) and a "
                            f"high-quality, active entry ({entry_score:.0f}/100) would otherwise qualify as "
                            f"AGGRESSIVE, but the risk regime is {risk_regime} — directional conviction does "
                            f"not override risk, so this stays SHORT."
                        )
                        return "SHORT"
                    reasons.append(
                        f"Bias is bearish with strong trend health ({trend_health:.0f}/100) and a high-quality "
                        f"entry ({entry_score:.0f}/100), with no momentum divergence — SHORT."
                    )
                    return "SHORT"
                elif trend_health >= 50 and macro_bias == "BEARISH":
                    reasons.append(
                        f"Bias is bearish and the broader macro trend agrees, with decent trend health "
                        f"({trend_health:.0f}/100), but the entry quality ({entry_score:.0f}/100) isn't strong "
                        f"enough — CONSERVATIVE SHORT."
                    )
                    return "CONSERVATIVE SHORT"

            reasons.append(
                f"No side has a strong enough, well-aligned case right now (trend health {trend_health:.0f}/100, "
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
        qualifier = (
            " This reflects how the picture lines up, not a green light — the risk check above is what's blocking the trade."
            if final_action.startswith("NO-TRADE")
            else ""
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
        fixed 1:1/2:1/3:1 targets) as the reward side. This is a sanity-check
        translation of the confidence score above into "would this be worth
        taking on average if you're right that often" -- not a measured,
        backtested number.
        """
        win_rate = max(0.0, min(1.0, confidence / 100.0))
        ev_r = (win_rate * self.AVG_REWARD_R) - ((1.0 - win_rate) * 1.0)

        if ev_r > 0.3:
            ev_phrase = "positive -- worth taking on average if that win rate holds up"
        elif ev_r < -0.3:
            ev_phrase = "negative -- would lose money on average even at that win rate"
        else:
            ev_phrase = "close to breakeven"

        qualifier = (
            " (this is hypothetical, since no trade is actually being suggested right now)"
            if not any(side in final_action for side in ("LONG", "SHORT"))
            else ""
        )

        reasons.append(
            f"Expected value (illustrative, not backtested): treating the {confidence:.0f}/100 confidence score "
            f"as a rough win rate against the standard {self.AVG_REWARD_R:.0f}:1 average reward, this setup works "
            f"out to about {ev_r:+.2f}R per trade — {ev_phrase}{qualifier}."
        )

        return {
            "ev_r": float(ev_r),
            "assumed_win_rate": float(win_rate * 100.0),
            "avg_reward_r": float(self.AVG_REWARD_R),
        }

    # ============================================================
    # BTC-ADJUSTED CONFIDENCE (new feature, V1)
    # ============================================================

    BTC_ADJUSTMENT_CAP = 20.0
    BTC_STRESS_PENALTY = 15.0

    def _compute_btc_adjusted(
        self,
        confidence: float,
        bias: Dict[str, Any],
        btc_context: Optional[Dict[str, Any]],
        symbol: str = "this asset",
    ) -> Dict[str, Any]:
        """
        A SEPARATE confidence reading that factors in BTC's own bias and how
        closely AERO has been tracking BTC lately -- this NEVER changes
        `confidence` above. Per the explicit requirement this was built to:
        Bitcoin context is additive, shown as its own second number, never
        a replacement for or distortion of the original AERO-only read.

        The adjustment is bounded to +/-20 points, scaled by two things:
        how relevant BTC even is right now (|correlation|) and how
        convicted BTC's own bias is (|btc bias score|/100) -- a BTC bias
        that's both weakly correlated with AERO AND barely committed to a
        direction barely moves this number, by design. A broad
        market-stress flag (BTC itself in an elevated volatility regime)
        subtracts a further 15 points regardless of direction.
        """
        if not isinstance(btc_context, dict) or not btc_context.get("available"):
            return {"available": False}

        try:
            aero_score = _safe_float(bias.get("score"), 0.0)
            btc_score = _safe_float(btc_context.get("score"), 0.0)
            correlation = _safe_float(btc_context.get("correlation"), 0.0)
            correlation_label = str(btc_context.get("correlation_label", "WEAK / NO CLEAR RELATIONSHIP"))
            n_obs = int(btc_context.get("n_observations", 0) or 0)
            stress = bool(btc_context.get("broad_market_stress", False))
            btc_detailed = str(btc_context.get("detailed", "NEUTRAL"))

            aero_dir = 1 if aero_score > 0 else (-1 if aero_score < 0 else 0)
            btc_dir = 1 if btc_score > 0 else (-1 if btc_score < 0 else 0)

            if aero_dir != 0 and btc_dir != 0 and aero_dir == btc_dir:
                agreement = 1
            elif aero_dir != 0 and btc_dir != 0 and aero_dir != btc_dir:
                agreement = -1
            else:
                agreement = 0

            direction_adjustment = agreement * abs(correlation) * (abs(btc_score) / 100.0) * self.BTC_ADJUSTMENT_CAP
            stress_penalty = self.BTC_STRESS_PENALTY if stress else 0.0
            net_adjustment = direction_adjustment - stress_penalty

            btc_adjusted_confidence = max(0.0, min(100.0, confidence + net_adjustment))

            # SEQUENCE ITEM 12: the run's own symbol, not a hardcoded one.
            # Trimmed of the quote currency so the sentence reads "AERO and
            # BTC" rather than "AEROUSDT and BTC".
            asset = str(symbol).upper()
            for suffix in ("USDT", "USDC", "USD", "BUSD"):
                if asset.endswith(suffix) and len(asset) > len(suffix):
                    asset = asset[: -len(suffix)]
                    break

            if agreement > 0:
                agree_phrase = f"BTC is also {btc_detailed.lower()}, agreeing with {asset}'s own bias"
            elif agreement < 0:
                agree_phrase = f"BTC is {btc_detailed.lower()}, disagreeing with {asset}'s own bias"
            else:
                agree_phrase = "BTC isn't showing a clear directional bias either way right now"

            # SEQUENCE ITEM 12. Two fixes in one string.
            #
            # "AERO" was hardcoded, so running on SOLUSDT produced reasoning
            # about AERO — and running on BTCUSDT claimed to compare AERO
            # against BTC while comparing BTC to itself.
            #
            # correlation_label already ENDS in the word "relationship"
            # ("WEAK / NO CLEAR RELATIONSHIP"), and this appended another,
            # printing "a weak / no clear relationship relationship" on every
            # run for as long as the feature has existed.
            label = correlation_label.lower()
            if not label.endswith("relationship"):
                label = f"{label} relationship"

            reason = (
                f"BTC-adjusted confidence: {btc_adjusted_confidence:.0f}/100 (vs {confidence:.0f}/100 unadjusted, "
                f"never replacing it). {asset} and BTC have a {label} (correlation "
                f"{correlation:+.2f} over the last {n_obs} candles), and {agree_phrase}."
            )
            if stress:
                reason += " BTC itself is in an elevated-volatility regime right now, a broad market-stress signal."

            return {
                "available": True,
                "btc_adjusted_confidence": float(btc_adjusted_confidence),
                "adjustment": float(net_adjustment),
                "reasons": [reason],
            }

        except Exception as e:
            logger.warning(f"BTC-adjusted confidence calculation failed: {e}")
            return {"available": False}