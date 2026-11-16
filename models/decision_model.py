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
from core.threshold_text import compared_value_text

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


# 5 SEPTEMBER 2026 -- VIKTOR'S RULING: a lean is not a case. A directional
# action must require more than a label that leans.
#
# From that day until 14 November 2026 the mechanism was a constant here,
# MIN_ACTION_BIAS = 30: bias.raw came from the weighted sum past +/-20
# (bias_engine's RAW_BIAS_THRESHOLD), and a side was acted on only at a sum
# of 30 or more. Its comment, and the reasons for two thresholds, are in git
# at 6038283.
#
# THE REDESIGN'S STAGE 2, 14 November 2026. The direction is no longer a sum
# (Viktor's ruling of 7 November 2026): it is BULLISH or BEARISH only when
# EMA50's slope and the order of EMA_20 and EMA_50 agree, and NEUTRAL
# otherwise (models/bias_engine.py, direction_from_emas). That agreement is
# the floor. So the constant is gone, with its line in
# core/decision_log.py's FINGERPRINTED_MODULES, and the lean is the NEUTRAL
# direction: _determine_final_action answers WAIT for it with a sentence of
# its own, where the constant's sentence stood.


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

    THE REDESIGN'S STAGE 5, 15 November 2026. This class produced four
    things until this stage: the action, a confidence score, a trade
    quality and an illustrative EV. Three of them are gone, and so are the
    three constants behind them --

        AVG_REWARD_R                = 2.0
        EV_BREAKEVEN_BAND_R         = 0.3
        DEGRADED_CONFIDENCE_CEILING = 50.0

    -- which leaves the run-hash payload (core/decision_log.py), moving
    run_hash and the archive's file name. evaluate() returns the action and
    the explanation, and nothing else. See the records at _compute_confidence
    and _apply_degradation below for what each part was and why it went.
    """

    def evaluate(
        self,
        bias: Dict[str, Any],
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
        # THE REDESIGN'S STAGE 5, 15 November 2026: `trend` was the second
        # positional parameter and is gone. Stage 4 took the trend block out
        # of _determine_final_action with trend health's tiers, which left
        # _compute_trade_quality as its one reader here; that method goes in
        # this stage, so nothing in this class reads a trend reading at all.
        # A caller still passing it in second place now gives four
        # positional arguments to three slots and fails with a TypeError
        # rather than having the trend block land silently in `entry` --
        # the same protection work order G relied on when macro_bias left.
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
        final_action = self._determine_final_action(bias, entry, risk, reasons=reasons)
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

        # THE REDESIGN'S STAGE 3, 15 November 2026: gate 8, the trigger and
        # its volume. After gates 3 to 7 (the signal gate above), so that a
        # refusal there stays the label: the draft's ladder takes the first
        # gate, in order, that fails.
        action_before_trigger = final_action
        before = len(reasons)
        final_action = self._apply_trigger_gate(final_action, entry, reasons)
        if final_action != action_before_trigger and len(reasons) > before:
            action_reason_index = len(reasons) - 1

        # THE REDESIGN'S STAGE 4, 15 November 2026: gate 9, entry quality,
        # and the tier it decides. Last of the gates, after gate 8, because
        # the draft's ladder takes the label of the first gate in its order
        # that fails and the tier is derived only once all of them pass.
        # _apply_quality_gate writes the sentence that names the tier, and
        # it is the only place a tier is chosen.
        before = len(reasons)
        final_action = self._apply_quality_gate(final_action, entry, risk, reasons)
        # Gate 9 is the ONLY stage that chooses a tier, so whenever it runs
        # it is the stage that set the action -- including when the tier it
        # chooses is the bare side it was handed and the string does not
        # change. The "did the action change?" test the gates above use
        # would miss precisely that case, and the summary of every plain
        # LONG or SHORT would name the direction sentence instead of the
        # sentence saying why this is a LONG and not a CONSERVATIVE LONG or
        # a WAIT. Found by running the second pinned decision before this
        # stage's commit: it is a LONG, and its summary named gate 2.
        if len(reasons) > before:
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
        # THE REDESIGN'S STAGE 5, 15 November 2026: _compute_confidence and
        # _compute_trade_quality were called here, and _compute_ev after the
        # degradation below. All three are gone; the records are at
        # _compute_confidence's old position.

        if degradation:
            action_before_degradation = final_action
            before = len(reasons)
            final_action = self._apply_degradation(
                degradation, final_action, reasons
            )
            # Degradation appends its notes whether or not it changes the
            # action. Only a changed action moves the summary.
            if final_action != action_before_degradation and len(reasons) > before:
                action_reason_index = len(reasons) - 1

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
            "explanation": explanation,
        }

    SIGNAL_UNCONFIRMED = "NO-TRADE (SIGNAL UNCONFIRMED)"

    @classmethod
    def _read_refusal(cls, entry: Any, side: str) -> str:
        """
        The label a refused side takes: the one models/entry_model.py
        recorded for the first gate that side did not pass (stage 3 of the
        redesign: SIGNAL UNCONFIRMED, MACRO AGAINST or THIN MARKET).

        Fails safe to SIGNAL UNCONFIRMED: a label that is absent, or is not
        one of the three, is not believed. Called only for a side
        _read_signal did not confirm.
        """
        entry = entry if isinstance(entry, dict) else {}
        label = entry.get(f"{side}_signal_refusal")
        if isinstance(label, str) and label in entry_model.REFUSAL_LABELS:
            return label
        return cls.SIGNAL_UNCONFIRMED

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
                # B4's labels, 14 October 2026: "no momentum divergence"
                # became what is compared (indicators/trend_health.py,
                # section 5).
                reasons.append(
                    f"Structural confirmation holds for the {side}: structure "
                    f"agrees with the direction, ADX is "
                    f"{entry_model.MIN_TREND_ADX:g} or "
                    f"more, and no price/RSI disagreement over four candles "
                    f"points against it."
                )
                return final_action
            leaning = "bullish" if side == "long" else "bearish"
            # Stage 3 of the redesign, 15 November 2026: the label is the
            # first gate's that the side did not pass. Gates 3 to 5 keep
            # their sentence and their label; a side they pass and gate 6 or
            # 7 refuses is not said to lack structural confirmation.
            # Stage 4, 15 November 2026: both sentences read "This would
            # have been {final_action}" -- a tier the old ladder had already
            # chosen from trend health. The tier is now derived after gate 9
            # (_apply_quality_gate), so at this point there is no tier, and
            # final_action is the bare side. The wording follows gate 8's,
            # which stage 3 wrote for the same reason.
            label = self._read_refusal(entry, side)
            if label == self.SIGNAL_UNCONFIRMED:
                reasons.append(
                    f"No earlier gate refused the {side}, but the {leaning} "
                    f"bias lacks structural confirmation "
                    f"({'; '.join(blockers)}), so no trade is taken."
                )
            else:
                reasons.append(
                    f"No earlier gate refused the {side}, but "
                    f"{'; '.join(blockers)}, so no trade is taken."
                )
            return label

        if final_action == "NO-TRADE (RISK TOO HIGH)":
            raw_bias = str(bias.get("raw", "NEUTRAL")) if isinstance(bias, dict) else "NEUTRAL"
            if raw_bias in ("BULLISH", "BEARISH"):
                side = "long" if raw_bias == "BULLISH" else "short"
                confirmed, blockers = self._read_signal(entry, side)
                if not confirmed:
                    if self._read_refusal(entry, side) == self.SIGNAL_UNCONFIRMED:
                        reasons.append(
                            f"Separately, the {raw_bias.lower()} bias also lacked "
                            f"structural confirmation ({'; '.join(blockers)}). The "
                            f"risk refusal is the label; this is recorded so the "
                            f"log shows both failures."
                        )
                    else:
                        reasons.append(
                            f"Separately, the {side} would also have been "
                            f"refused ({'; '.join(blockers)}). The risk "
                            f"refusal is the label; this is recorded so the "
                            f"log shows both failures."
                        )
        return final_action

    def _apply_trigger_gate(self, final_action: str, entry: Any,
                            reasons: List[str]) -> str:
        """
        GATE 8 of the redesign (stage 3, 15 November 2026): a trade that
        passed every earlier gate is taken only on a resumption candle with
        volume behind it. The rule is documented above read_trigger in
        models/entry_model.py; this reads what that function recorded in
        `entry` and does not compute it again.

        Fails safe: a trigger that is absent or not True/False, or a volume
        or median that is not a number, is not a trigger. That is a WAIT with
        its own sentence, and never the sentence of a candle that was read
        and did not resume. On the engine's path such a run is degraded too.
        """
        if not any(side in final_action for side in ("LONG", "SHORT")):
            return final_action
        side = "long" if "LONG" in final_action else "short"
        entry = entry if isinstance(entry, dict) else {}

        trigger = entry.get("trigger")
        volume = entry_model._measured_amount(entry.get("trigger_volume"))
        median = entry_model._measured_amount(entry.get("trigger_volume_median"))
        lookback = entry_model.TRIGGER_VOLUME_LOOKBACK

        if not isinstance(trigger, bool) or volume is None or median is None:
            reasons.append(
                f"No earlier gate refused the {side}, but the trigger was "
                f"not measured on this run (the decision candle against its "
                f"open and the previous close, and its volume against the "
                f"median of the {lookback} candles before it), and a trigger "
                f"that was not measured is not a trigger — WAIT."
            )
            return "WAIT"

        beyond = "above" if side == "long" else "below"
        failures: List[str] = []
        if not trigger:
            failures.append(
                f"the last closed candle did not close {beyond} both its "
                f"open and the previous candle's close")
        if not volume > median:
            # Entry 58's rule: the volume is printed on its own side of the
            # median, which is printed exactly as computed.
            printed = (entry_model.exact_text(volume) if volume == median
                       else compared_value_text(volume, median))
            failures.append(
                f"its volume, {printed}, is not above the median of the "
                f"{lookback} candles before it, "
                f"{entry_model.exact_text(median)}")
        if not failures:
            reasons.append(
                f"The last closed candle is a resumption candle for the "
                f"{side}: it closed {beyond} both its open and the previous "
                f"candle's close, on volume above the median of the "
                f"{lookback} candles before it."
            )
            return final_action

        reasons.append(
            f"No earlier gate refused the {side}, but there is no "
            f"resumption candle yet: {', and '.join(failures)} — WAIT."
        )
        return "WAIT"

    def _apply_quality_gate(self, final_action: str, entry: Any,
                            risk: Any, reasons: List[str]) -> str:
        """
        GATE 9 of the redesign (stage 4, 15 November 2026), and the tier it
        decides. The last gate: a side that has passed gates 0 to 8 is taken
        only if the close is at a pullback to the average, which entry
        quality measures (ruling 4, 25 October 2026, point 4).

            quality >= UPPER_TIER_ENTRY_QUALITY_MIN   LONG / SHORT, and
                AGGRESSIVE when the close is inside the EMA band and the
                risk regime is NORMAL or LOW
            quality >= CONSERVATIVE_ENTRY_QUALITY_MIN CONSERVATIVE LONG/SHORT
            under that                               WAIT -- not a pullback

        Last, not first. The draft's ladder runs 0, 1, 2, 3-5, 6, 7, 8, 9
        and takes the label of the FIRST gate that fails, and the reading of
        11 November counted with that order
        (docs/build/measure_draft_gaps.py, `ladder`). So a low quality beside
        a failed ADX is the ADX's refusal, not this one, and the tier is
        derived only once every earlier gate has passed -- which is why
        _determine_final_action returns the bare side and no sentence before
        this one names a tier.

        What AGGRESSIVE reads is `entry.close_inside_band`, a true-or-false
        field, and not the STATUS word (Viktor's ruling of 7 November 2026
        that the redesign's AGGRESSIVE reads the close inside the band; the
        draft's section 3.1, proposal 1). Until this stage it read
        `"ACTIVE" in entry_status.upper()`, so a change to a panel word
        could change an action. The risk regime is the same intensity gate
        as before (item 14 re-audit, finding 5): conviction never overrides
        risk, and a regime outside NORMAL and LOW leaves a high-quality
        setup at the plain side.

        Fails safe: a quality that is absent or is not a finite number is
        not a quality, and that is a WAIT with a sentence of its own, never
        a quality of zero and never the sentence of a close that was
        measured and found too far out. On the engine's path such a run is
        degraded too, with the missing input named
        (models/entry_model.py, calculate_entry_quality). `close_inside_band`
        anything but True is read as not inside, so a record that does not
        carry the field cannot reach AGGRESSIVE.
        """
        if not any(side in final_action for side in ("LONG", "SHORT")):
            return final_action
        side = "LONG" if "LONG" in final_action else "SHORT"
        leaning = "bullish" if side == "LONG" else "bearish"
        entry = entry if isinstance(entry, dict) else {}
        risk = risk if isinstance(risk, dict) else {}

        upper = self.UPPER_TIER_ENTRY_QUALITY_MIN
        conservative = self.CONSERVATIVE_ENTRY_QUALITY_MIN

        quality = entry_model._finite(entry.get("score"))
        if quality is None:
            reasons.append(
                f"No earlier gate refused the {side.lower()}, but entry "
                f"quality was not measured on this run (the close's "
                f"distance from the EMA band's midpoint and from the HVN, "
                f"both counted in ATRs), and a quality that was not "
                f"measured is not a quality — WAIT."
            )
            return "WAIT"

        # Entry 58's rule: the quality is printed on its own side of every
        # line the sentence names, so it can never print AS a line it is
        # only near (core/threshold_text.py).
        printed = compared_value_text(quality, (conservative, upper))

        if quality < conservative:
            reasons.append(
                f"No earlier gate refused the {side.lower()}, but entry "
                f"quality is {printed} of 100, under the {conservative:g} a "
                f"trade needs: the close is not at a pullback to the "
                f"average — WAIT."
            )
            return "WAIT"

        if quality < upper:
            reasons.append(
                f"The {leaning} bias passed every gate with entry quality "
                f"{printed} of 100 — at or above the {conservative:g} a "
                f"CONSERVATIVE trade needs, and under the {upper:g} the "
                f"upper tiers need — CONSERVATIVE {side}."
            )
            return f"CONSERVATIVE {side}"

        inside = entry.get("close_inside_band") is True
        regime = str(risk.get("risk_regime", "UNKNOWN RISK"))
        aggressive_allowed = regime in ("NORMAL RISK", "LOW RISK")

        if inside and aggressive_allowed:
            reasons.append(
                f"The {leaning} bias passed every gate with entry quality "
                f"{printed} of 100, at or above the {upper:g} the upper "
                f"tiers need, the close inside the EMA band, and a "
                f"{regime.lower()} — AGGRESSIVE {side}."
            )
            return f"AGGRESSIVE {side}"

        if inside:
            reasons.append(
                f"The {leaning} bias passed every gate with entry quality "
                f"{printed} of 100 and the close inside the EMA band, which "
                f"would otherwise qualify as AGGRESSIVE, but the risk "
                f"regime is {regime} — directional conviction does not "
                f"override risk, so this stays {side}."
            )
            return side

        where = {"ABOVE THE BAND": "above", "BELOW THE BAND": "below"}.get(
            str(entry.get("entry_status", "")), "outside")
        reasons.append(
            f"The {leaning} bias passed every gate with entry quality "
            f"{printed} of 100, at or above the {upper:g} the upper tiers "
            f"need, but the close is {where} the EMA band rather than "
            f"inside it, which AGGRESSIVE requires — {side}."
        )
        return side

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

    def _apply_degradation(self, degradation, final_action, reasons):
        """
        Enforce the degrade ruling on a decision already computed.

        Viktor's ruling of 29 August 2026, verbatim: "When an indicator
        fails, the engine continues in an explicitly degraded state. It must
        not fabricate replacement values. The failure must be recorded in the
        decision output, and confidence and trade quality must be reduced
        accordingly. A degraded result does not by itself authorize trading."

        1. It must not fabricate replacement values. Held where each value is
           produced: a missing indicator is None or NaN and is named, never
           substituted (sequence item 9a; entry quality's own not-measured
           rule, stage 4).

        2. The failure is recorded in the decision output. Listed here in the
           reasoning the operator reads, as well as in `degradation`.

        3. A degraded result does not by itself authorize trading. Any action
           naming a side becomes NO-TRADE, and degradation.trading_authorized
           is false.

        THE CAP IS GONE, AND SO IS THE CLAUSE IT SERVED -- the redesign's
        stage 5, 15 November 2026, Claude's reading of this ruling, VIKTOR'S
        TO REVERSE. The second sentence of point 2 of the ruling named two
        quantities, confidence and trade quality, and this method capped both
        at DEGRADED_CONFIDENCE_CEILING (50.0). Both leave the record in this
        stage, so there is nothing left for the cap to reduce.

        The one surviving score is entry quality, and capping THAT was
        considered and refused: entry.score is printed on the panel beside
        the D, the H and the two ATR distances it is computed from
        (80 x max(0, 1 - d/3) + 20 x max(0, 1 - h/2)), so a capped score
        would contradict its own stated arithmetic on the same screen -- two
        places computing one number, the defect shape this engine keeps
        finding. It is also not needed for safety: point 3 above already
        refuses the trade outright, which is a stronger constraint than any
        ceiling on a reported number.

        WHAT THAT WEAKENS: a degraded run's entry quality is now reported
        uncapped. It is reported beside a NO-TRADE (DEGRADED INPUT) and a
        named missing input, so it cannot be read as a green light, but the
        number itself is no longer held down.

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

        if any(side in final_action for side in ("LONG", "SHORT")):
            reasons.append(
                f"The action would have been {final_action}; a degraded run "
                f"cannot authorize a trade, so it is NO-TRADE."
            )
            final_action = "NO-TRADE (DEGRADED INPUT)"

        return final_action

    # ============================================================
    # FINAL ACTION (moved here verbatim from signal_router.py's
    # _determine_final_action -- same tested logic, just relocated to the
    # architecturally correct place, per the roadmap's own diagnosis)
    # ============================================================

    # THE REDESIGN'S STAGE 4, 15 November 2026: the tiers come from entry
    # quality alone (ruling 4, 25 October 2026), and the two lines are 70
    # and 50 (DECISIONS, "Ruling, 11 November 2026 -- the redesign's tier
    # lines are 70 and 50 ...", where Viktor also kept all three labels).
    #
    #   quality >= UPPER_TIER_ENTRY_QUALITY_MIN   LONG / SHORT, and
    #                                            AGGRESSIVE when the close
    #                                            is inside the EMA band and
    #                                            the risk regime is NORMAL
    #                                            or LOW
    #   quality >= CONSERVATIVE_ENTRY_QUALITY_MIN CONSERVATIVE LONG / SHORT
    #   under that                               WAIT -- not a pullback
    #
    # WHAT THESE TWO NAMES REPLACE.
    #
    #     AGGRESSIVE_TREND_HEALTH_MIN   = 75.0
    #     AGGRESSIVE_ENTRY_SCORE_MIN    = 70.0
    #     CONSERVATIVE_TREND_HEALTH_MIN = 50.0
    #
    # were promoted from bare literals inside _determine_final_action on
    # 13 September 2026 (round 6's F1 follow-up). The pair (trend health >=
    # 75, entry score >= 70) was the line between AGGRESSIVE-eligible and
    # plain LONG/SHORT, and the single 50 -- trend health's -- was the line
    # between CONSERVATIVE and WAIT. Trend health leaves the tier here and
    # the module in stage 5, so both of its lines go; the 70 is the same
    # number under a name that says what it now measures, which is the one
    # line the upper tiers share; and the 50 is a new name, because the old
    # 50 was a trend-health line and this one is entry quality's.
    #
    # Both are fingerprinted, like every other decision-affecting number in
    # this class (AVG_REWARD_R, DEGRADED_CONFIDENCE_CEILING above) -- see
    # core/decision_log.py's FINGERPRINTED_MODULES entry for this class.
    # Renaming a fingerprinted constant without updating that list drops it
    # out of the run-hash payload silently, which is the decay rule 11 warns
    # about; it is updated in this commit.
    #
    # (Dated: MIN_ACTION_BIAS left this file at the redesign's stage 2,
    # 14 November 2026, and RAW_BIAS_THRESHOLD leaves models/bias_engine.py
    # with the weighted sum in stage 5. Both were named beside these three
    # in the same audit finding; neither needed F1's fix.)
    UPPER_TIER_ENTRY_QUALITY_MIN = 70.0
    CONSERVATIVE_ENTRY_QUALITY_MIN = 50.0

    # THE REDESIGN'S STAGE 4, 15 November 2026: _conservative_reason stood
    # here. It named what kept a setup below the upper tier -- trend health
    # under 75, entry quality under 70, or both -- and was written on
    # 21 September because the sentence had blamed the wrong one of the two.
    # With the tiers coming from entry quality alone there is one line to
    # name and no attribution to get wrong, so the sentence is written where
    # the tier is decided (_apply_quality_gate below).

    def _determine_final_action(
        self,
        bias: Dict[str, Any],
        entry: Dict[str, Any],
        risk: Dict[str, Any],
        *,
        reasons: List[str],
    ) -> str:
        """
        GATES 0 TO 2 of the redesign's ladder, and nothing else: whether the
        inputs are well formed, whether risk was assessed and passed, and
        whether there is a direction to act on. What it returns is the SIDE,
        naming no tier:

        - LONG / SHORT
        - WAIT
        - NO-TRADE (RISK NOT ASSESSED)
        - NO-TRADE (RISK TOO HIGH)

        THE REDESIGN'S STAGE 4, 15 November 2026. Until this stage this
        function also chose the tier, from trend health and entry quality,
        and so returned CONSERVATIVE LONG, AGGRESSIVE SHORT and the rest.
        The tier now comes from entry quality alone (ruling 4, 25 October
        2026) and is derived AFTER gate 9, which is after gates 3 to 8 --
        the draft's order, and the order the reading of 11 November counted
        with (docs/build/measure_draft_gaps.py, `ladder`: 0, 1, 2, 3-5, 6,
        7, 8, 9, and the tier only once every one of them passes). So the
        tier cannot be chosen here: a gate between this function and gate 9
        may refuse the side, and a tier named before gate 9 would be a claim
        about a trade that does not exist. See _apply_quality_gate.

        `trend` was the second parameter and is gone: with trend health out
        of the tier, nothing in this function reads it. The number stays in
        the record and on the panel until stage 5.
        """
        try:
            if not all(isinstance(d, dict) for d in [bias, entry, risk]):
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

            # ITEM 14 RE-AUDIT (Finding 5): risk_regime gates action
            # INTENSITY -- whether "AGGRESSIVE" may be used -- and never
            # direction, and never whether a trade is allowed at all, which
            # risk_valid above has already decided. It still does, and it is
            # now read where AGGRESSIVE is decided: gate 9
            # (_apply_quality_gate). Entry quality and the close's position
            # against the band moved there with it.
            #
            # Gone from this function with the tier: SEQUENCE ITEM 13's
            # trend_health read, 5 September's trend_direction_sign, the
            # trend_note the two built, and work order B's "not computed"
            # text for a trend health that was never measured. The tier no
            # longer reads trend health (ruling 4, 25 October 2026 -- the
            # tiers come from entry quality alone), and the number itself
            # stays in the record and on the panel until stage 5.
            #
            # H1 IS GONE. It was
            #
            #     if validation_state == "WEAK" and trend_health < 40:
            #         return "WAIT"
            #
            # the held-back defect H1 (Decision, 25 October 2026, point 2).
            # The redesign's ladder has no such gate -- the draft's section
            # 4, "H1 goes" -- and both of its inputs leave in stage 5, so
            # leaving the branch here for one stage would let a run WAIT for
            # a reason no gate in the design names, and before gate 2 at
            # that. Removed with the ladder rather than with its inputs, so
            # that the ladder this stage leaves behind IS the design's.
            # validation_score, validation_state and validation_note stay in
            # the record and on the panel until stage 5; nothing in the
            # decision reads any of them now. H1's replacement is proposed
            # in stage 6, with H2's and H5's (agreed 11 November 2026).

            raw_bias = str(bias.get("raw", "NEUTRAL"))

            # 5 SEPTEMBER 2026: the magnitude was read here, not only the
            # label (bias_strength, |bias.score|), for the floor below.
            # Stage 2 of the redesign, 14 November 2026: the floor reads the
            # label alone again, because the label now carries it.

            # VIKTOR'S RULING, 2 September 2026: bias is the sole direction
            # source. This block used to read
            #
            #     if raw_bias == "BULLISH" or long_signal or macro_bias == "BULLISH":
            #
            # and the bearish block below it mirrored that. Three
            # independent sources could each open a direction, the first
            # block to match returned, and nothing ever compared the answer
            # against the risk plan -- which risk_model builds from the side
            # alone. Found by running the engine on live data, 2 September:
            # AEROUSDT 4h came back bearish on every measure the engine has,
            # with a BULLISH macro read, and the engine printed CONSERVATIVE
            # LONG above a stop ABOVE price and three targets BELOW it. A
            # long label on a short plan. Why bias rather than macro: macro
            # has had its vote. long_signal / short_signal went for the same
            # reason, and were RULED to confirm on 21 September (work order
            # F) -- see _apply_signal_gate.

            # VIKTOR'S RULING, 5 September 2026: a lean is not a case.
            #
            # THE REDESIGN'S STAGE 2, 14 November 2026 (the draft's gate 2).
            # This compared |bias.score| with MIN_ACTION_BIAS and sent a
            # BULLISH or BEARISH label under 30 to WAIT. The lean is now the
            # NEUTRAL direction itself, so the floor is the label. The
            # sentence says what BULLISH and BEARISH require and that this
            # candle is neither, so that it is also true of a direction that
            # could not be measured, which arrives here as NEUTRAL beside a
            # degradation that names what was missing.
            if raw_bias not in ("BULLISH", "BEARISH"):
                reasons.append(
                    "The direction is NEUTRAL: it is bullish only when EMA50 "
                    "is rising and EMA20 is above it, and bearish only when "
                    "EMA50 is falling and EMA20 is below it. This candle is "
                    "neither, so there is no side to act on — WAIT."
                )
                return "WAIT"

            # THE SIDE, AND NO TIER. Gates 3 to 7 are the confirmation
            # signal's blockers (_apply_signal_gate), gate 8 is the trigger
            # (_apply_trigger_gate) and gate 9 is entry quality and the tier
            # (_apply_quality_gate). Each runs after this function, in the
            # draft's order, so every sentence they write about this action
            # names no tier either: until gate 9 passes there is no tier to
            # claim. Until this stage a refusal by gate 6, 7 or 8 read "This
            # would have been CONSERVATIVE LONG" -- a tier the old ladder
            # chose from trend health, which stage 3 filed as a claim stage
            # 4 had to remove (DECISIONS, "Decision, 15 November 2026 --
            # stage 3 of the redesign's build ...", reading 8).
            side = "LONG" if raw_bias == "BULLISH" else "SHORT"
            rule = ("EMA50 is rising and EMA20 is above it" if side == "LONG"
                    else "EMA50 is falling and EMA20 is below it")
            reasons.append(
                f"The direction is {raw_bias}: {rule}, so the "
                f"{side.lower()} is the side the remaining gates are read "
                f"for."
            )
            return side

        except Exception as e:
            logger.error(f"Decision engine evaluation failed: {e}")
            reasons.append("The decision engine hit an unexpected error, so it defaulted to WAIT as a safe fallback.")
            return "WAIT"

    # ============================================================
    # CONFIDENCE (new, real multi-factor score -- previously just a
    # trend_health passthrough)
    # ============================================================

    # ============================================================
    # CONFIDENCE, TRADE QUALITY AND EV -- REMOVED at the redesign's
    # stage 5, 15 November 2026
    # ============================================================
    #
    # _compute_confidence, _compute_trade_quality and _compute_ev stood
    # here, in that order, with AVG_REWARD_R, EV_BREAKEVEN_BAND_R and
    # DEGRADED_CONFIDENCE_CEILING above them. Ruling 6 of 25 October 2026
    # (DECISIONS, "Ruling, 25 October 2026 -- the indicator document's eight
    # questions"): confidence and the EV line are dropped.
    #
    # WHAT EACH WAS.
    #
    #   _compute_confidence   abs(bias.score) clipped to 100 -- the weighted
    #                         sum's own magnitude and nothing else, after the
    #                         Item 11 re-audit removed structure_alignment
    #                         and validation_adj from it. It wrote the
    #                         sentence naming the sum's six factors, and
    #                         risk.confidence_score. The sum goes in this
    #                         stage (models/bias_engine.py), so there is no
    #                         score to take a magnitude of.
    #   _compute_trade_quality  entry.score under a second name, as
    #                         risk.trade_quality_proposed, plus the sentence
    #                         "Entry quality is X/100 -- a weak entry.
    #                         Compare it against the TREND line ...". Both
    #                         go: the number is entry.score, which gate 9
    #                         reads and the panel prints with the D and H it
    #                         is made of, and the sentence compared it
    #                         against the TREND line, which is trend
    #                         health's and leaves here too. One name for one
    #                         meaning (round 8, F8).
    #   _compute_ev           (win_rate x AVG_REWARD_R) - (loss_rate x 1)
    #                         with confidence/100 as the win rate: a linear
    #                         rescaling of confidence that could not
    #                         disagree with it, as its own comment said, and
    #                         risk.ev_r, risk.assumed_win_rate and
    #                         risk.avg_reward_r with it.
    #
    # So eight leaves leave the record -- risk.confidence_score,
    # risk.trade_quality_proposed, risk.ev_r, risk.assumed_win_rate,
    # risk.avg_reward_r and, from engine_core's validation block,
    # risk.validation_state, risk.validation_score and
    # risk.validation_note -- and three sentences leave
    # explanation.reasons, which moves again as stage 3's reading 1 said it
    # would. Each leaf moves once, to its final value: gone.
    #
    # WHAT NO LONGER HAPPENS, STATED PLAINLY. A run used to print a
    # confidence and an expected value beside its action. It does not. The
    # action is the engine's answer, and the nine gates behind it are each
    # a yes or a no an operator can read in Decision Reasoning. There is no
    # single number saying how sure the engine is, because every number
    # that said so was the weighted sum restated -- which is the finding
    # the redesign was built to answer, not a gap it leaves.

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
