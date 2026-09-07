# `import os` was here. Its only two uses were the eager makedirs removed
# from route() -- see the note there. Left in place it would be a
# declaration nothing reads, which is what sequence item 14 spent its
# time removing from this codebase.
from typing import Dict, Any, Optional, List
import logging
import math

from core import config, decision_log
from core.panel_render import render_panel
from models.decision_model import DecisionModel
# GLM F-7, extended -- 6 September 2026. See models/risk_model.py.
from models.risk_model import read_risk_verdict

logger = logging.getLogger(__name__)

class SignalRouter:
    """
    Routes raw engine data into unified decision objects and handles panel rendering.

    ROADMAP LAYER 1 FIX: this router previously contained its own decision
    logic (_determine_final_action) -- diagnosed in the original roadmap as
    architecturally wrong ("Router contains decision logic (should not)").
    That logic now lives in models/decision_model.py; this router is a pure
    assembler: run the engine, call DecisionModel.evaluate(...), assemble
    the unified decision object, render it.
    """

    def __init__(self, engine_core: Optional[Any] = None, decision_model: Optional[DecisionModel] = None) -> None:
        if engine_core is None:
            from core.engine_core import Phase7Engine
            self.engine_core = Phase7Engine()
        else:
            self.engine_core = engine_core

        self.decision_model = decision_model if decision_model is not None else DecisionModel()

    def _validate_engine_output(self, raw_output: Dict[str, Any]) -> bool:
        """
        Validate that engine output contains required sections.

        Args:
            raw_output: Raw engine output dictionary

        Returns:
            bool: True if valid, False otherwise
        """
        if not isinstance(raw_output, dict):
            logger.error("Engine output is not a dictionary")
            return False

        if "error" in raw_output:
            return True  # Error states are valid data payloads containing failure notices

        required_sections = ["bias", "trend", "structure", "entry", "risk"]
        missing_sections = [section for section in required_sections if section not in raw_output]

        if missing_sections:
            logger.error(f"Engine output missing required sections: {missing_sections}")
            return False

        # GLM F-7 AS EXTENDED, 6 September 2026. This function checked that
        # the key "risk" was PRESENT and never what was under it, so
        # {"bias": ..., "risk": {}} passed here, satisfied
        # _determine_final_action's isinstance(risk, dict) guard, and reached
        # a gate whose default turned an unassessed block into a pass. That
        # composition -- a validator that checks presence, a consumer that
        # defaults permissively -- is what made the defect reachable rather
        # than latent.
        #
        # Rejecting here rather than only refusing downstream, because the
        # engine output IS malformed and this is the function whose job is to
        # say so. The refusal in decision_model.py stays as well: DecisionModel
        # is called directly by tests and is a public class, so a caller that
        # never passes through here must still not be able to buy a pass by
        # omission.
        if read_risk_verdict(raw_output.get("risk")) is None:
            logger.error(
                "Engine output's risk section carries no pass/fail verdict "
                "(risk_valid absent or not a boolean); risk was not assessed"
            )
            return False

        return True

    def route_and_execute(self, symbol: str, timeframe: str) -> Dict[str, Any]:
        """
        Executes the engine core workflow, builds the decision object,
        and renders the output panel.

        Args:
            symbol: Trading symbol
            timeframe: Analysis timeframe

        Returns:
            Dict containing unified decision object
        """
        try:
            # Validate inputs
            if not symbol or not isinstance(symbol, str):
                error_obj = {"error": "Invalid symbol parameter"}
                render_panel(error_obj)
                return error_obj
            if not timeframe or not isinstance(timeframe, str):
                error_obj = {"error": "Invalid timeframe parameter"}
                render_panel(error_obj)
                return error_obj

            # SEQUENCE ITEM 14 corrected these from the literals "Logs/Charts"
            # and "Logs" to the config paths. VIKTOR'S RULING, 2 September
            # 2026, removes them outright.
            #
            # They wrote nothing. Every writer in this engine creates its own
            # directory, on demand, inside its own error handling:
            # decision_log.write (returns None), engine_core._save_state
            # (warns), plotting.plot_engine_chart (warns), and
            # lineage.write_archive (returns None). These two calls duplicated
            # all four.
            #
            # What they added was a failure mode. Unguarded, at the top of
            # route(), BEFORE the analysis runs -- so an unwritable log
            # directory raised here, the broad handler below turned it into
            # "Router execution failed: [Errno 20] Not a directory", and the
            # operator lost not just the log but the entire analysis. Four
            # independently recoverable conditions collapsed into one total
            # failure, at the one point in the run where nothing had been
            # computed yet to lose.
            #
            # Found while writing the halt-safety test for the raw-input
            # archive; verified present before that work, so it long predates
            # it. It is the same class as item 14's own REQUIRED_DIRS finding
            # -- "read by nothing at all -- the directories are created on
            # demand by the code that writes into them" -- which removed the
            # list and left these two calls standing.
            #
            # RULED, and this is the part that is a judgment rather than a bug
            # fix: a run whose decision log cannot be written STILL AUTHORIZES
            # A TRADE. It warns, the panel makes no claim that anything was
            # logged, and the operator decides. Viktor's 29 August
            # degrade-not-halt ruling applied literally: a disk problem must
            # not destroy an analysis that was computed correctly, and must not
            # veto one either.
            #
            # The cost is stated rather than hidden. Item 6 is Critical, and
            # the one decision acted on without a record is the one an auditor
            # would ask about first. Recorded in docs/PHASE7_NEXT.md as a
            # decision with its trade-off, so a re-audit reads a ruling and not
            # an oversight.

            # THIS router owns rendering exclusively (see class docstring / C1
            # fix), using the one complete decision object as the single source
            # of truth for the panel.
            #
            # SEQUENCE ITEM 5b: the call used to pass render=False. That
            # parameter is gone -- engine_core no longer renders at all, so the
            # exclusivity this comment asserts is now enforced by the code
            # rather than by every caller remembering to ask for it.
            raw_output = self.engine_core.run(symbol, timeframe)

            # Validate engine output format
            if not self._validate_engine_output(raw_output):
                error_obj = {"error": "Engine produced invalid output format"}
                render_panel(error_obj)
                return error_obj

            if "error" in raw_output:
                render_panel(raw_output)
                return raw_output

            # Build unified decision dictionary with dynamic decision logic
            try:
                decision = self._build_decision_object(
                    symbol=symbol,
                    timeframe=timeframe,
                    bias=raw_output.get("bias", {}),
                    trend=raw_output.get("trend", {}),
                    structure=raw_output.get("structure", {}),
                    entry=raw_output.get("entry", {}),
                    risk=raw_output.get("risk", {}),
                    exit_data=raw_output.get("exit", {}),
                    degradation=raw_output.get("degradation", []),
                    provenance=raw_output.get("provenance", {}),
                    # AUDIT FINDING 7 (Item 6): the lineage chain, passed
                    # through with provenance. This assembly is a whitelist --
                    # a key engine_core produces and this call does not name is
                    # silently dropped -- so a record that never reaches the
                    # decision log is the default outcome of adding one.
                    lineage_record=raw_output.get("lineage", {}),
                    exit_watch=raw_output.get("exit_watch", []),
                    btc_context=raw_output.get("btc_context", {}),
                    macro_bias=raw_output.get("macro_bias", "NEUTRAL"),
                    # SEQUENCE ITEM 14: the default was a hardcoded
                    # f"Logs/Charts/chart_{symbol}_{timeframe}.png" — a fourth
                    # copy of a path config declares, in a directory whose name
                    # was already the wrong case. engine_core always sets this
                    # key (to None when charting failed), so the default never
                    # fired; it was a literal waiting to be believed.
                    chart_path=raw_output.get("chart_path")
                )

                # SEQUENCE ITEM 12 (Item 6): write the log the panel has
                # claimed since the engine was built, and record whether it
                # actually happened. The panel prints the line only when there
                # is a path — an engine that says "logged" after a failed write
                # is the same defect with a new filename.
                logged_to = decision_log.write(decision, config)
                decision["decision_log_path"] = logged_to or ""
                if not logged_to:
                    logger.warning("decision log could not be written for this run")

                logger.info(f"Signal router successfully processed {symbol} [{timeframe}] -> Action: {decision.get('exit', {}).get('action', 'UNKNOWN')}")
                render_panel(decision)
                return decision

            except Exception as e:
                logger.error(f"Failed to build decision object: {e}")
                error_obj = {"error": f"Decision object construction failed: {str(e)}"}
                render_panel(error_obj)
                return error_obj

        except Exception as e:
            logger.error(f"Router execution failed: {e}")
            error_obj = {"error": f"Router execution failed: {str(e)}"}
            render_panel(error_obj)
            return error_obj

    def route(self, symbol: str, timeframe: str) -> Dict[str, Any]:
        """
        Alias for route_and_execute to match main.py calls.

        Args:
            symbol: Trading symbol
            timeframe: Analysis timeframe

        Returns:
            Dict containing unified decision object
        """
        return self.route_and_execute(symbol, timeframe)

    def _build_decision_object(
        self,
        symbol: str,
        timeframe: str,
        bias: Dict[str, Any],
        trend: Dict[str, Any],
        structure: Dict[str, Any],
        entry: Dict[str, Any],
        risk: Dict[str, Any],
        exit_data: Dict[str, Any],
        macro_bias: str,
        chart_path: str,
        exit_watch: Optional[List[Any]] = None,
        btc_context: Optional[Dict[str, Any]] = None,
        degradation: Optional[List[str]] = None,
        provenance: Optional[Dict[str, Any]] = None,
        lineage_record: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Convert engine output into a unified trade decision object.
        Pure assembly: all decision logic (final_action, confidence,
        trade_quality, ev, btc_adjusted, explanation) comes from
        self.decision_model.evaluate().
        """
        degradation = list(degradation) if isinstance(degradation, list) else []
        provenance = dict(provenance) if isinstance(provenance, dict) else {}
        lineage_record = dict(lineage_record) if isinstance(lineage_record, dict) else {}

        try:
            # SEQUENCE ITEM 9a: degradation is passed INTO the decision model
            # rather than stapled onto the object afterwards. Viktor's ruling
            # says a degraded result does not by itself authorize trading, so
            # the model has to know before it decides — an annotation added
            # after the fact would describe a decision already made.
            # ITEM 11 RE-AUDIT (Finding 4): `structure` is no longer passed
            # to evaluate() -- DecisionModel's confidence calculation stopped
            # reading it (see decision_model.py's _compute_confidence). It is
            # still used below, to build this function's own "structure"
            # block of the decision object.
            dm_result = self.decision_model.evaluate(
                bias, trend, entry, risk, macro_bias, btc_context,
                degradation=degradation,
                symbol=symbol,
            )
            final_action = dm_result["final_action"]
            confidence = dm_result["confidence"]
            trade_quality = dm_result["trade_quality"]
            ev = dm_result["ev"]
            btc_adjusted = dm_result["btc_adjusted"]
            explanation = dm_result["explanation"]

            # Defensive normalization for targets tuple
            targets = risk.get("targets", (0.0, 0.0, 0.0))
            if not isinstance(targets, (list, tuple)) or len(targets) < 3:
                targets = (0.0, 0.0, 0.0)

            return {
                "symbol": symbol,
                "timeframe": timeframe,
                "macro_bias": macro_bias,

                "bias": {
                    "raw": str(bias.get("raw", "UNKNOWN")),
                    "detailed": str(bias.get("detailed", "UNKNOWN")),
                    "score": self._finite_or_nan(bias.get("score")),
                    "regime": str(bias.get("regime", "UNKNOWN STRUCTURE")),
                    "volatility": str(bias.get("volatility", "UNKNOWN"))
                },

                "trend": {
                    # SEQUENCE ITEM 13: "health" and "momentum" were exact
                    # duplicates of "trend_health" and "momentum_mode",
                    # assigned from the same source expression on the adjacent
                    # line. core/decision_contract.py named the survivors at
                    # item 10 and scheduled the removal here. Nothing read the
                    # short names except decision_model.py, which preferred
                    # them, so a change to the canonical field would have gone
                    # unnoticed there.
                    "trend_health": self._finite_or_nan(trend.get("trend_health")),
                    "exhaustion": bool(trend.get("trend_exhaustion", False)),
                    "momentum_mode": str(trend.get("momentum_mode", "UNKNOWN")),
                    "momentum_divergence": bool(trend.get("momentum_divergence", False)),
                    "trend_direction": str(trend.get("trend_direction", "UNKNOWN")),
                },

                "structure": {
                    "regime": str(structure.get("regime", "UNKNOWN STRUCTURE")),
                    "sequence": str(structure.get("sequence", "UNKNOWN")),
                    "hvn": self._finite_or_nan(structure.get("hvn")),
                    "lvn": self._finite_or_nan(structure.get("lvn")),
                    "volume_sentiment": str(structure.get("volume_sentiment", "UNKNOWN VOLUME")),
                    # KIMI FINDING 5 ITEM 6, 6 September 2026. This default was
                    #
                    #     exit_data.get("current_price", 0.0)
                    #
                    # the consumer half of the fabrication fixed in
                    # structure.py this commit, on the same field: a structure
                    # block that carried no swing level got the current price
                    # written in as one, into the panel and into the decision
                    # log. It is reachable by the same composition as GLM F-7 --
                    # _validate_engine_output checks that "structure" is
                    # PRESENT, so an engine output whose structure block is {}
                    # passes validation and arrives here, where the default
                    # fires. An absent price level is NaN, which is what
                    # engine_core's own .get default on this field already
                    # uses and what panel_render prints as "not located".
                    "swing_struct": self._finite_or_nan(structure.get("swing_struct"))
                },

                "entry": {
                    "zone_lower": float(entry.get("zone_lower", 0.0)),
                    "zone_upper": float(entry.get("zone_upper", 0.0)),
                    "long_signal": bool(entry.get("long_signal", False)),
                    "short_signal": bool(entry.get("short_signal", False)),
                    "score": float(entry.get("score", 0.0)),
                    "distance_from_zone": float(entry.get("distance_from_zone", 0.0)),
                    "entry_status": str(entry.get("entry_status", "ACTIVE ENTRY ZONE")),
                    "ema_pos_pts": float(entry.get("ema_pos_pts", 0.0)),
                    "atr_dist_pts": float(entry.get("atr_dist_pts", 0.0)),
                    "vwma_pts": float(entry.get("vwma_pts", 0.0)),
                    "rsi_pts": float(entry.get("rsi_pts", 0.0)),
                    "struct_pts": float(entry.get("struct_pts", 0.0)),

                    # 5 September 2026. This block rebuilds the entry section
                    # field by field, so anything the engine adds and this
                    # list does not name is silently dropped before the panel
                    # or the decision log ever sees it -- which is what
                    # happened to these nine on the first attempt at this fix:
                    # the reconciliation lines simply did not appear, with no
                    # error.
                    #
                    # They are how the five sub-scores above become `score`:
                    # they sum to base_score (out of component_max_points,
                    # which is 102, not 100), that is multiplied by
                    # combined_multiplier, and the result is clipped to
                    # score_ceiling.
                    "base_score": float(entry.get("base_score", 0.0)),
                    "component_max_points": float(entry.get("component_max_points", 0.0)),
                    "macro_multiplier": float(entry.get("macro_multiplier", 1.0)),
                    "trend_multiplier": float(entry.get("trend_multiplier", 1.0)),
                    "structure_multiplier": float(entry.get("structure_multiplier", 1.0)),
                    "combined_multiplier": float(entry.get("combined_multiplier", 1.0)),
                    "scaled_score": float(entry.get("scaled_score", 0.0)),
                    "score_ceiling": float(entry.get("score_ceiling", 100.0)),
                    "score_clipped": bool(entry.get("score_clipped", False)),
                },

                "risk": {
                    "atr_stop": float(risk.get("atr_stop", 0.0)),
                    "targets": (float(targets[0]), float(targets[1]), float(targets[2])),
                    # GLM F-7 AS EXTENDED, 6 September 2026. This read
                    # bool(risk.get("risk_valid", True)) and wrote the
                    # invented True into the decision log and the panel, so
                    # the permanent record of a run on which risk was never
                    # assessed said risk passed.
                    #
                    # The contract still declares this bool rather than
                    # Optional[bool], and that is now a guarantee rather than
                    # a hope: _validate_engine_output above rejects an engine
                    # output whose risk block carries no verdict, so nothing
                    # reaching this assembly can produce None here. Declaring
                    # it Optional would have been the weaker fix --
                    # tests/test_decision_contract.py's _type_ok returns True
                    # for any Union, so the field would have stopped being
                    # type-checked at all.
                    "risk_valid": read_risk_verdict(risk),
                    "risk_reason": str(risk.get("risk_reason", "UNKNOWN")),
                    # ITEM 14 RE-AUDIT (Finding 5): risk_model.py's
                    # classify_risk_regime() always computed this; only its
                    # EXTREME-RISK/not boolean reached risk_valid above.
                    # DecisionModel now reads the regime itself to gate
                    # whether an AGGRESSIVE action label may be used --
                    # directional conviction is no longer the only thing
                    # deciding it.
                    "risk_regime": str(risk.get("risk_regime", "UNKNOWN RISK")),
                    # ROADMAP LAYER 1 FIX: confidence_score and the two
                    # trade_quality_* fields are now DecisionModel's real,
                    # multi-factor outputs (see models/decision_model.py)
                    # instead of engine_core.py's raw trend_health
                    # passthrough. Field names/paths kept identical so
                    # panel_render.py needs no changes to consume them.
                    "confidence_score": float(confidence),
                    "trade_quality_proposed": float(trade_quality["proposed_entry"]),
                    "validation_state": str(risk.get("validation_state", "UNKNOWN")),
                    "validation_score": self._finite_or_nan(risk.get("validation_score")),
                    "validation_note": str(risk.get("validation_note", "No validation note supplied.")),

                    # SEQUENCE ITEM 13: the five position-sizing fields were
                    # removed here under Viktor's ruling of 29 August 2026.
                    # They were fed by engine_core.py from a placeholder
                    # 10,000 balance in config.py; both the computation and
                    # the constants are gone.
                    "ev_r": float(ev.get("ev_r", 0.0)),
                    "assumed_win_rate": float(ev.get("assumed_win_rate", 0.0)),
                    "avg_reward_r": float(ev.get("avg_reward_r", 2.0)),
                },

                "exit": {
                    "action": final_action,
                    "current_price": float(exit_data.get("current_price", 0.0))
                },

                # C3 BUILD: advisory-only Exit Watch flags, passed straight
                # through from engine_core.py -- see exit_model.py's
                # build_exit_watch() for what feeds into this.
                "exit_watch": list(exit_watch) if isinstance(exit_watch, list) else [],

                # SEQUENCE ITEM 9a: what this analysis was computed without,
                # and whether that blocks it from authorizing a trade.
                "degradation": {
                    "degraded": bool(degradation),
                    "missing_inputs": list(degradation),
                    "trading_authorized": not bool(degradation),
                },

                # BTC MARKET CONTEXT (new feature, V1): merges engine_core.py's
                # BTC-side analysis (bias/regime/correlation/beta) with
                # DecisionModel's BTC-adjusted confidence -- informational
                # only, never changes BIAS/DECISION/confidence above.
                "btc_context": self._merge_btc_context(btc_context, btc_adjusted),

                "explanation": explanation,

                # SEQUENCE ITEM 12 (Item 5): what this run saw, passed
                # straight through from engine_core.
                "provenance": provenance,

                # AUDIT FINDING 7 (Item 6, Traceability): the walkable chain
                # from this decision back to the raw candles -- decision
                # components, normalized signals, raw signals, indicator values
                # at the decision bar, the validated-input hashes, and the
                # archive holding the input itself.
                "lineage": lineage_record,

                # Filled in below, after the log is written. Empty string means
                # nothing was logged, and the panel prints no claim.
                "decision_log_path": "",

                # AUDIT FINDING (2 September 2026): this was str(chart_path).
                # plot_engine_chart returns None when it could not write --
                # an unwritable directory, a matplotlib failure -- and
                # str(None) is the four-character string "None", which is
                # TRUTHY. panel_render gates the chart line on
                # `decision.get("chart_path") or ""`, so the gate passed and
                # the panel printed:
                #
                #     Chart saved to None
                #
                # naming a file that does not exist, in the same shape as the
                # trade-log claim sequence item 12 removed for being a claim
                # about a file nothing wrote.
                #
                # The convention was already here, two fields up:
                # decision_log_path uses "" to mean nothing was written and
                # the panel prints no claim. chart_path simply never followed
                # it. It does now.
                "chart_path": str(chart_path) if chart_path else ""
            }

        except Exception as e:
            logger.error(f"Failed to build decision object layout: {e}")
            # AUDIT, Item 6. Found by the Section 11 confirmation run on
            # 6 September 2026, and by neither reviewer: this record used to be
            # {symbol, timeframe, error} and nothing else, while the healthy
            # record beside it in the same log carries `lineage` and
            # `provenance` -- input_hashes, run_hash, and the flag saying
            # whether the run was pinned. decision_log.write() serialises
            # whatever it is handed, so every failed assembly stored a record
            # that cannot be traced to any input, inside the one item this
            # project raised to Critical.
            #
            # A run that failed still has a lineage. Losing the analysis is not
            # a reason to also lose the identity of the inputs that produced
            # it -- that is the difference between a defect and a defect nobody
            # can reconstruct. Both names are already normalised to dicts above
            # the try, so they are defined here however the assembly failed.
            return {
                "symbol": symbol,
                "timeframe": timeframe,
                "error": f"Decision object construction failed: {str(e)}",
                "provenance": provenance,
                "lineage": lineage_record,
            }

    @staticmethod
    @staticmethod
    def _finite_or_nan(value: Any) -> float:
        """Measurement level: None/non-finite -> NaN; real finite kept. Sweep 1-5."""
        if value is None:
            return float("nan")
        try:
            number = float(value)
        except (TypeError, ValueError):
            return float("nan")
        return number if math.isfinite(number) else float("nan")

    @staticmethod
    def _optional_number(value: Any) -> Optional[float]:
        """
        A quantity the producer may legitimately not have, passed through
        rather than replaced.

        KIMI ROUND 4, FINDING 1 (Major), confirmed end to end by the Section 11
        run on 6 September 2026 before this fix was written. The two call sites
        below read

            float(btc_context.get("correlation", 0.0))

        which looks like a default for a missing key and is not one. The key is
        always present: engine_core writes it with the value None when the
        quantity could not be measured (engine_core.py 771-788, the same
        spelling that file already uses for atr and structural_level, and the
        one that serialises to JSON null). So the default never fired,
        float(None) raised TypeError, and _build_decision_object's broad except
        turned a complete and correct AERO analysis into an error dict because
        an OPTIONAL Bitcoin number was unavailable. Two indexes sharing no
        timestamps is enough to reach it: one candle closing between two API
        calls, an exchange gap, a stale feed.

        None is returned rather than 0.0 deliberately. A correlation of 0.00 is
        a measurement -- it is what a real pair of independent assets produces
        -- so substituting it would report a finding the engine does not have.
        That is the defect this codebase already removed from btc_context.py's
        (0.0, 0.0, 0), from trend_health's 50.0 and from RSI's 50.0, and
        reintroducing it at the merge would put it back one layer down.

        panel_render (its _correlation_lines) and decision_model (its
        correlation_measured test) both already read None as "not measured".
        This is the third module agreeing with them instead of crashing on
        them.

        NOT changed, and stated rather than left to be found: the other fields
        in the merge below still carry invented defaults -- "NEUTRAL",
        "NORMAL", 0.0 for trend_health. They are not covered here because they
        are not optional measurements; engine_core computes them
        unconditionally. That is the same "the producer always sets it"
        argument that was made about this line and was wrong, so it is recorded
        as an open question rather than as a guarantee.
        """
        if value is None:
            return None
        try:
            number = float(value)
        except (TypeError, ValueError):
            return None
        return number if math.isfinite(number) else None

    def _merge_btc_context(
        self,
        btc_context: Optional[Dict[str, Any]],
        btc_adjusted: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Combines engine_core.py's BTC-side analysis (bias/regime/volatility/
        correlation/beta) with DecisionModel's BTC-adjusted confidence into
        one dict for panel_render.py -- kept as a single merge point so
        panel_render.py doesn't need to know these came from two different
        places.
        """
        btc_context = btc_context if isinstance(btc_context, dict) else {}
        btc_adjusted = btc_adjusted if isinstance(btc_adjusted, dict) else {}

        if not btc_context.get("available") or not btc_adjusted.get("available"):
            return {"available": False}

        return {
            "available": True,
            "raw": str(btc_context.get("raw", "UNKNOWN")),
            "detailed": str(btc_context.get("detailed", "UNKNOWN")),
            "regime": str(btc_context.get("regime", "UNKNOWN STRUCTURE")),
            "volatility": str(btc_context.get("volatility", "UNKNOWN")),
            "trend_health": self._finite_or_nan(btc_context.get("trend_health")),
            # KIMI ROUND 4, FINDING 1 -- see _optional_number below. These two
            # were float(...get(key, 0.0)) and raised TypeError on the value
            # engine_core actually writes.
            "correlation": self._optional_number(btc_context.get("correlation")),
            "correlation_label": str(btc_context.get("correlation_label", "WEAK / NO CLEAR RELATIONSHIP")),
            "beta": self._optional_number(btc_context.get("beta")),
            "broad_market_stress": bool(btc_context.get("broad_market_stress", False)),
            "n_observations": int(btc_context.get("n_observations", 0) or 0),
            "btc_adjusted_confidence": self._finite_or_nan(btc_adjusted.get("btc_adjusted_confidence")),
            "reasons": list(btc_adjusted.get("reasons", [])),
        }