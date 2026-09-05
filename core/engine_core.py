import math
import pandas as pd
from typing import Dict, Any, Optional, List
import json
import os
import logging
import traceback

from . import config
from data.data_fetcher import data_fetcher
from indicators.indicators import add_technical_indicators
from structure.structure import calculate_structure
from indicators.trend_health import compute_trend_health
from models.bias_engine import (
    calculate_dynamic_bias,
    calculate_dynamic_regime,
    BiasStateMachine,
)
from models.risk_model import RiskModel
from models.entry_model import generate_entry_signals, calculate_entry_quality
from models.exit_model import build_exit_watch
from core import lineage
from core import decision_log
from models.btc_context import compute_correlation_beta, classify_correlation, classify_stress
from utils.plotting import plot_engine_chart

logger = logging.getLogger(__name__)


# AUDIT FINDING (2 September 2026), found by running the engine.
#
# The panel printed, four lines apart:
#
#     MACRO TREND: BULLISH
#     ...
#     Validation Notes:
#      - The higher timeframe is neutral.
#
# Two claims about the same thing, in one panel, and the second one false.
# The block that produced it had three branches -- agrees, disagrees, and an
# else that said "The higher timeframe is neutral." That else was covering
# TWO different situations:
#
#     the macro really is neutral            -> the sentence is true
#     the macro has a direction, the BIAS    -> the sentence is false. It
#     is neutral                                describes the bias and
#                                               attributes it to the macro.
#
# On a neutral-bias run -- which is what the engine reports whenever its six
# factors cancel, a common state -- the panel therefore contradicted its own
# MACRO TREND line every time.
#
# This is the same shape as the contradiction that exposed the direction
# Critical on 2 September: the decision claimed "the broader macro trend
# agrees" while Validation Notes said it disagreed. Item 8, in the section
# that exists to tell the operator what was checked.
#
# Extracted to a function so the four cases can be tested directly. Inline,
# the only way to reach the false branch was to find market data that
# produced a neutral bias under a directional macro.
# AUDIT FINDING (5 September 2026), found by running the engine.
#
# The panel printed VOLUME : STRONG BEARISH DISTRIBUTION and, in the same
# run, under Validation Notes: "Volume sentiment is supportive of current
# momentum." The bias was BULLISH CONFIRMED.
#
# The test was `if "STRONG" in volume_sentiment.upper()`. It matched the word
# and ignored the direction, so strongly BEARISH volume scored +15 towards a
# BULLISH validation and printed as support. On the run that exposed it, that
# +15 is what made VALIDATION read STRONG at exactly 75.00 -- 50 baseline,
# +10 macro agreeing, +15 volume "supporting".
#
# Third instance of one class: a direction-blind test producing a directional
# claim. The macro note was the first (macro_agreement below, 3 September),
# and bias_engine signing trend_health from the sign of a magnitude was the
# second (4 September).
#
# models/bias_engine.py already had this right. _VOLUME_SENTIMENT_SCORES maps
# STRONG BEARISH DISTRIBUTION to -100. One quantity computed correctly in one
# module and wrongly in another -- exactly what check 7.6 of the auditor
# instruction asks a reviewer to look for.
#
# No weight is invented. +15 for volume supporting the bias, as before; -25
# for volume against it, which is the weight this same block already used for
# its disconfirming branch. Strong volume against the bias is disconfirming.
def volume_agreement(volume_sentiment, raw_bias):
    """
    How the volume reading stands relative to this run's bias.

    Returns (score_delta, note). Extracted so every case can be tested
    directly; inline, the false branch needed market data that happened to
    pair strong counter-trend volume with an opposing bias.
    """
    v = str(volume_sentiment).upper()
    vol_up = "BULLISH" in v
    vol_down = "BEARISH" in v
    bias_up = raw_bias == "BULLISH"
    bias_down = raw_bias == "BEARISH"

    if "DIVERGENCE" in v or "WEAK" in v or "EXHAUSTION" in v:
        return -25.0, "Volume divergence or weakness detected."

    if not (vol_up or vol_down):
        return 0.0, "Volume sentiment is neutral."

    if (vol_up and bias_up) or (vol_down and bias_down):
        return 15.0, "Volume sentiment supports this bias."

    if (vol_up and bias_down) or (vol_down and bias_up):
        return -25.0, (
            f"Volume sentiment ({volume_sentiment}) runs AGAINST this bias."
        )

    # Volume has a direction and the bias does not. Naming the reading lets
    # the operator check this line against the VOLUME line above it.
    return 0.0, (
        f"The bias is neutral, so volume sentiment ({volume_sentiment}) "
        f"neither supports nor opposes it."
    )


def macro_agreement(macro_bias, raw_bias):
    """
    How the higher timeframe stands relative to this run's bias.

    Returns (score_delta, note). The deltas are unchanged from the inline
    version: +10 agreeing, -20 disagreeing, 0 when there is no comparison to
    make. Only the sentence for that last case is new, and only in the half
    of it that was previously described wrongly.
    """
    macro = str(macro_bias).upper()
    macro_up = "BULLISH" in macro
    macro_down = "BEARISH" in macro
    bias_up = raw_bias == "BULLISH"
    bias_down = raw_bias == "BEARISH"

    if (macro_up and bias_up) or (macro_down and bias_down):
        return 10.0, "The higher timeframe agrees with this bias."

    if (macro_up and bias_down) or (macro_down and bias_up):
        return -20.0, "The higher timeframe disagrees with this bias."

    if not (macro_up or macro_down):
        return 0.0, "The higher timeframe is neutral."

    # The macro has a direction and the bias does not. Naming the macro read
    # here matters: the operator can see MACRO TREND on the panel above and
    # check this sentence against it.
    return 0.0, (
        f"The bias is neutral, so there is nothing for the higher timeframe "
        f"({macro}) to agree or disagree with."
    )

class Phase7Engine:
    """
    Phase‑7 Structural Quant Engine
    Main orchestrator for:
        - Data & Macro Confluence (MTF)
        - Indicators & Caching
        - Structure & Volume Sentiment
        - Trend Health & Bias
        - Entry Quality, Risk & Exit
        - Charting
        - BTC Market Context (informational only)

    SEQUENCE ITEM 5b: this class no longer renders. It returns a decision
    object; SignalRouter assembles the final one and renders it. That was
    already the intent — signal_router.py:83 says so in a comment, and it was
    the only caller — but engine_core kept a render path that no entry point
    reached. See the run() docstring for why leaving it in place became
    actively wrong once compute_exit was removed.
    """

    def __init__(self) -> None:
        self.bias_state_machine = BiasStateMachine()
        # Separate state machine for BTC's own bias -- BTC's detailed bias
        # is tracked independently of AERO's, since they're different assets
        # with their own history of confirmations.
        self.btc_bias_state_machine = BiasStateMachine()
        self.risk_model = RiskModel()
        # SEQUENCE ITEM 6: _indicator_cache, _structure_cache and
        # _max_cache_size lived here. See the run() docstring for why they went.

    def _validate_dataframe(self, df: Optional[pd.DataFrame], required_columns: List[str], context: str = "") -> bool:
        """
        Validate DataFrame has required columns and sufficient data length.
        """
        if df is None or df.empty:
            logger.error(f"DataFrame validation failed - empty or None DataFrame in {context}")
            return False

        if len(df) < 20:
            logger.error(f"DataFrame validation failed - insufficient data ({len(df)} rows) in {context}")
            return False

        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            logger.error(f"DataFrame validation failed - missing columns {missing_cols} in {context}")
            return False

        return True

    # SEQUENCE ITEM 6: _manage_cache (FIFO eviction at 15 entries) was here.
    # It was correct code serving two caches that never returned a hit in any
    # production path.

    # ============================================================
    # C3 BUILD: cross-run state persistence
    # ============================================================
    #
    # Two of the Exit Watch flags (SuperTrend flip, bias flip) are only
    # meaningful as a COMPARISON against the previous run. This tool is
    # normally invoked as a fresh command each time rather than left running
    # continuously, so in-memory instance state (like self.bias_state_machine
    # above) doesn't survive between runs -- it has to be a small file on
    # disk instead. Defensive by design: a missing or corrupt state file
    # just means "nothing to compare against yet," never a crash.

    def _state_path(self, symbol: str, timeframe: str) -> str:
        # SEQUENCE ITEM 14: was getattr(config, "LOG_DIR", "Logs/"). A
        # fallback for a name config always defines is a second, undeclared
        # setting that only takes effect when the first goes missing — so a
        # deleted or misspelled config entry relocates the engine's output
        # silently instead of failing where it can be seen.
        log_dir = config.LOG_DIR
        return os.path.join(log_dir, f"phase7_state_{symbol}_{timeframe}.json")

    # ============================================================
    # AUDIT FINDINGS 6 AND 7 -- Items 5 (Reproducibility) and 6
    # (Traceability), the last Critical.
    #
    # Item 6 was raised from Major to Critical by Viktor's ruling of 29
    # August 2026, which is what makes it the finding holding the release
    # gate shut: "no output of this engine may be relied on for a real
    # trading decision while any Critical Tier 1 finding stands unresolved."
    #
    # What sequence item 12 built was a decision log: what the engine
    # concluded, plus a five-field fingerprint of what it saw. What the
    # re-audit asked for is the chain underneath the conclusion --
    #
    #   decision <- decision components <- normalized signals <- raw signals
    #            <- indicators <- validated market data <- raw source data
    #
    # -- and enough of the input to rebuild the run rather than merely
    # describe it. The three methods below collect the middle links; the
    # ends are the input hash (core/lineage.py) and the archive.
    #
    # Every one of them is read-only over frames the analysis already
    # produced. Nothing here can change a decision, which is deliberate:
    # an audit trail that can alter the thing it records is not one.
    # ============================================================

    @staticmethod
    def _decision_bar_row(df) -> Dict[str, Any]:
        """
        Every column's value at the decision bar -- the last row, the one the
        analysis is actually made on.

        Read off the frame rather than re-listed by name, so an indicator
        added later is recorded without anyone remembering to add it here. A
        hand-maintained list of what to record is a list that goes stale, and
        this project has already fixed that defect twice: seven config
        constants that were fingerprinted but read by nothing (sequence item
        14), and a guard list that named two indicators when the defect had
        five (Finding 3).
        """
        out: Dict[str, Any] = {}
        if df is None or len(df) == 0:
            return out
        try:
            row = df.iloc[-1]
        except Exception:
            return out
        for name in df.columns:
            try:
                value = row[name]
            except Exception:
                continue
            try:
                as_float = float(value)
            except (TypeError, ValueError):
                out[str(name)] = str(value)
                continue
            # A non-finite value is recorded as None rather than as the string
            # "nan": this record is read back as JSON, and "nan" in a numeric
            # field is the exact defect Observation 5 named in the panel.
            out[str(name)] = as_float if math.isfinite(as_float) else None
        return out

    @staticmethod
    def _frame_summary(df, digest) -> Dict[str, Any]:
        """One input frame, identified rather than described."""
        if df is None:
            return {"sha256": None, "rows": 0, "first_candle": None, "last_candle": None}
        return {
            "sha256": digest,
            "rows": int(len(df)),
            "columns": sorted(str(c) for c in df.columns),
            "first_candle": str(df.index[0]) if len(df) else None,
            "last_candle": str(df.index[-1]) if len(df) else None,
        }

    def _load_state(self, symbol: str, timeframe: str) -> Dict[str, Any]:
        try:
            path = self._state_path(symbol, timeframe)
            if not os.path.exists(path):
                return {}
            with open(path, "r") as f:
                loaded = json.load(f)
            return loaded if isinstance(loaded, dict) else {}
        except Exception as e:
            logger.warning(f"Could not load prior engine state (first run, or file is corrupt): {e}")
            return {}

    def _save_state(self, symbol: str, timeframe: str, state: Dict[str, Any]) -> None:
        try:
            log_dir = config.LOG_DIR
            os.makedirs(log_dir, exist_ok=True)
            path = self._state_path(symbol, timeframe)
            with open(path, "w") as f:
                json.dump(state, f)
        except Exception as e:
            logger.warning(f"Could not persist engine state for next run's Exit Watch comparison: {e}")

    def run(
        self,
        symbol: Optional[str] = None,
        timeframe: Optional[str] = None,
        limit: int = 450,
        save_chart: bool = True,
    ) -> Dict[str, Any]:
        """
        Execute full engine pipeline with Multi-Timeframe Confluence and safe
        error containment. Returns a decision object; rendering is the router's.

        SEQUENCE ITEM 5b removed the `render` parameter and the five
        `render_panel` calls it guarded.

        The parameter defaulted to True, but the only caller in the codebase —
        signal_router.py:87 — passed render=False, so no entry point ever
        printed this panel. It was reachable only by calling run() by hand.

        Removing compute_exit turned that from unused into misleading. The
        panel reads its DECISION line from decision["exit"]["action"], which is
        assembled by the router from DecisionModel. The raw object this method
        returns has never carried that key — before 5b the panel fell through
        to compute_exit's "final_action" and printed an exit verdict ("HOLD",
        "TARGET 1 HIT") in the slot labelled DECISION; after 5b it would have
        fallen through again to the literal default and printed "WAIT" on every
        run regardless of analysis.

        Either way it is the panel asserting a decision nothing computed, which
        is the Item 6 defect family. Deleting the path is Item 16 (unconsumed
        complexity) and closes the Item 6 exposure in one move. Ruled by Viktor,
        30 August 2026.

        SEQUENCE ITEM 6 removed the indicator and structure caches.

        They never returned a hit in any production path. main.py builds one
        SignalRouter, calls route once and exits; live_trading.run_once does the
        same. Each process began with both caches empty and ended without a
        single hit. The key embedded the last close, so even a long-running
        process would miss on every new bar.

        They were not merely useless. On the one reachable hit path they were a
        corruption hazard: the miss path stored a copy (df.copy()), but the hit
        path returned the cached object itself, and calculate_structure was
        called with copy_df=False and wrote STRUCTURE, HVN and LVN into it plus
        an ffill/bfill/fillna(0.0) across the OHLCV columns. The two caches
        shared a key and normally moved together, which hid this — but if
        structure analysis raised after the indicator cache had been written,
        the next run with that key took a hit on one and a miss on the other,
        and mutated the cached frame.

        Deletion rather than repair of the key: recomputation at 450 bars is
        trivial, and this removes the stale-serving hazard rather than
        rescheduling it. This is what dissolves the Items 4/12 dispute — both
        readings become true once the cache is gone.
        """
        symbol = symbol or config.SYMBOL
        timeframe = timeframe or config.TIMEFRAME
        macro_tf = config.MACRO_TIMEFRAME
        required_base_cols = ["open", "high", "low", "close", "volume"]

        # C3: load whatever was persisted from the last run (for the
        # SuperTrend-flip / bias-flip Exit Watch comparisons below).
        prior_state = self._load_state(symbol, timeframe)

        # SEQUENCE ITEM 9a: every input this run could not compute, in the
        # operator's words. Empty means the analysis below used everything it
        # claims to. Anything in it blocks the run from authorizing a trade —
        # see models/decision_model.py.
        degradation = []

        try:
            # 1. FETCH EXECUTION DATA
            df = data_fetcher.get_tf(symbol, timeframe, limit=limit)

            if not self._validate_dataframe(df, required_base_cols, "base market data"):
                # A13 FIX: distinguish a genuine data-fetch/API failure from an
                # ordinary "insufficient data" condition, instead of both
                # collapsing into the same generic message (which looked
                # identical to a normal no-signal HOLD in the panel).
                fetch_error = df.attrs.get("fetch_error") if df is not None else None
                error_message = (
                    f"Data fetch failed: {fetch_error}"
                    if fetch_error
                    else "Invalid or insufficient market data"
                )
                decision_object = {
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "error": error_message,
                }
                return decision_object

            # AUDIT FINDING 6: the input, as validated and before a single
            # derived column exists.
            #
            # Taken HERE and not later, for a reason that decides whether the
            # hash means anything. The frame the decision is assembled from
            # carries every indicator column, and those are this engine's own
            # arithmetic. Hashing them would fingerprint the code together
            # with the market data, so changing an indicator length would
            # present as the exchange having changed its candles -- and the
            # one question this hash exists to answer, "was the input the
            # same?", would stop having an answer.
            #
            # A copy, because add_technical_indicators() returns a frame that
            # may share storage with this one. The whole point is a record of
            # what arrived, and a record that later mutates into what the
            # engine made of it is not a record.
            raw_struct = df.copy()

            # 1b. FETCH MACRO DATA (Multi-Timeframe Confluence)
            # None means "not archived because it was never usable", which is
            # a different fact from "archived and empty". The record keeps
            # them different.
            raw_macro = None
            raw_btc = None
            # AUDIT FINDING 6 requires the fetch parameters actually used to
            # be recoverable. Bound to a name and then both passed and
            # recorded, so the call and the record cannot disagree -- a
            # literal here and a literal in the provenance block would be two
            # declarations of one number, which is how they drift.
            macro_limit = 100
            df_macro = data_fetcher.get_tf(symbol, macro_tf, limit=macro_limit)
            macro_bias = "NEUTRAL"

            if self._validate_dataframe(df_macro, required_base_cols, "macro timeframe data"):
                raw_macro = df_macro.copy()  # AUDIT FINDING 6 -- see raw_struct above
                try:
                    # SEQUENCE ITEM 9a: macro failures are recorded like any
                    # other. A macro read computed without ADX is still a macro
                    # read the operator should know about.
                    df_macro, macro_failures = add_technical_indicators(df_macro)
                    degradation.extend(f"macro {f}" for f in map(str, macro_failures))
                    if "EMA_50" in df_macro.columns:
                        macro_close = float(df_macro["close"].iloc[-1])
                        macro_ema50 = float(df_macro["EMA_50"].iloc[-1])

                        if macro_close > macro_ema50:
                            macro_bias = "BULLISH"
                        elif macro_close < macro_ema50:
                            macro_bias = "BEARISH"
                except Exception as e:
                    # ITEM 8/13 RE-AUDIT: this used to only log.warning and
                    # leave macro_bias at "NEUTRAL" -- indistinguishable from a
                    # genuinely flat higher timeframe. Same fabricated-fallback
                    # shape item 9 named for indicator failures (a failure
                    # rendered as a real reading), so it gets the same fix:
                    # recorded as a degradation instead of only logged.
                    logger.warning(f"Failed to process macro timeframe data: {e}")
                    degradation.append(
                        f"macro timeframe data failed to process ({e}) -- "
                        f"macro_bias reported as NEUTRAL by default, not "
                        f"because the higher timeframe is genuinely flat"
                    )
                    macro_bias = "NEUTRAL"
            else:
                # ITEM 8/13 RE-AUDIT (roadmap "Item 8/13 macro degradation"):
                # a macro fetch failure or an insufficient/malformed macro
                # frame used to leave macro_bias at its initialised "NEUTRAL"
                # with nothing added to `degradation` -- a failed higher-
                # timeframe read and a genuinely neutral macro trend rendered
                # identically, both on the panel and to every downstream
                # consumer of macro_bias (bias_engine's macro factor,
                # signal_router's macro/volume agreement check, the
                # AGGRESSIVE-gate macro checks in decision_model).
                # tests/test_golden_path.py::test_the_macro_series_is_actually_read
                # documented this in its own docstring as "recorded rather
                # than fixed... a rider on sequence item 9's degrade ruling."
                #
                # Ruled: report the failure like any other degraded input,
                # per Viktor's item 9 "degrade, don't fabricate" ruling.
                # macro_bias still can't invent a direction from missing
                # data, so it stays NEUTRAL -- but the run is now marked
                # degraded instead of silently trusted.
                macro_fetch_error = df_macro.attrs.get("fetch_error") if df_macro is not None else None
                degradation.append(
                    f"macro timeframe fetch failed: {macro_fetch_error}"
                    if macro_fetch_error
                    else "macro timeframe data is invalid or insufficient"
                )

            # 2. INDICATORS
            try:
                df, indicator_failures = add_technical_indicators(df)
                degradation.extend(str(f) for f in indicator_failures)

                # SEQUENCE ITEM 9a: this used to require all five indicators
                # and raise if any were missing — which, now that a failed
                # indicator drops its column instead of inventing a value,
                # would turn every indicator failure into a halt.
                #
                # Viktor ruled degrade, not halt. So a missing indicator is
                # recorded above and the run continues without it.
                #
                # ATR is the one exception, and it is not a change of policy.
                # Without ATR there is no stop distance and no targets, so
                # there is no risk plan to degrade — the object the engine
                # would return has no risk section at all. That is the
                # difference between an analysis missing a component and an
                # analysis that does not exist.
                if "ATR" not in df.columns:
                    raise ValueError(
                        "ATR is unavailable, so no stop or targets can be "
                        "computed. There is no degraded form of a risk plan "
                        "with no levels in it."
                    )

            except Exception as e:
                logger.error(f"Failed to add technical indicators: {e}")
                decision_object = {
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "error": f"Technical indicator calculation failed: {str(e)}",
                }
                return decision_object

            # 3. STRUCTURE ENGINE
            try:
                structure_obj = calculate_structure(
                    df, lookback=config.STRUCT_LOOKBACK,
                    volume_profile_bins=config.VOLUME_PROFILE_BINS
                )
                if not isinstance(structure_obj, dict):
                    raise ValueError("Structure engine returned invalid format")

                df_struct = structure_obj.get("df", df)

                # SEQUENCE ITEM 9a: was `required_indicators`, a list defined
                # inside section 2's try block. That definition went with the
                # block when the all-five requirement was removed, and this
                # line kept referring to it — every run died here with a
                # NameError that the outer handler reported as "Structure
                # analysis failed", naming the wrong stage.
                #
                # required_base_cols is what this check actually needs, and is
                # more correct than what it replaced: structure.py raises on
                # missing OHLCV, and section 2 already guarantees ATR. Under
                # the degrade ruling the other indicators may legitimately be
                # absent, so requiring all five here would have re-imposed the
                # halt this item exists to remove — one stage further down.
                if not self._validate_dataframe(df_struct, required_base_cols, "structure analysis"):
                    raise ValueError("Structure analysis produced invalid DataFrame")

                # 2 SEPTEMBER 2026: these four .get defaults were
                # "NEUTRAL STRUCTURE", "NONE", "NEUTRAL VOLUME" and 0.0 -- a
                # second layer of the same invention structure.py's handlers
                # were making, ready to fire if a key ever went missing. An
                # absent reading is UNKNOWN, and an absent price level is NaN.
                structure_regime = structure_obj.get("regime", "UNKNOWN STRUCTURE")
                trend_sequence = structure_obj.get("sequence", "UNKNOWN")
                volume_sentiment = structure_obj.get("volume_sentiment", "UNKNOWN VOLUME")
                # A6-adjacent FIX: swing_struct was computed by structure.py but never
                # extracted here, so it never made it into the decision object / panel.
                swing_struct = structure_obj.get("swing_struct", float("nan"))

                # Sub-routine failures inside StructureEngine.analyze() reach
                # the run's degradation list here, the same way trend_health's
                # do further down. Until 2 September there was nothing to
                # extend: analyze() swallowed its five sub-routine exceptions
                # and reported nothing, so a run with a crashed detector was
                # indistinguishable from a clean one and still authorised a
                # trade.
                degradation.extend(structure_obj.get("degraded_inputs", []))

            except Exception as e:
                logger.error(f"Structure analysis failed: {e}")
                decision_object = {
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "error": f"Structure analysis failed: {str(e)}",
                }
                return decision_object

            # 4. TREND HEALTH ENGINE
            #
            # AUDIT FINDING 6 (the surviving fabrication constants), 5 September
            # 2026. This stage used to wrap the call in a try whose handler
            # substituted {"trend_health": 50.0, ...}. Three things were wrong
            # with that, and they compound:
            #
            #   1. 50.0 is the exact centre of the scale. It is the value
            #      sequence item 9a deleted from trend_health.py's OWN default,
            #      for the reason recorded there — it is a reading a real
            #      market can produce, so nothing downstream can tell it from a
            #      measurement. Deleting it in the module and leaving a copy in
            #      the caller left the fabrication one stage further out.
            #   2. It could not run. compute_trend_health is total: every path
            #      through it returns a dict containing "trend_health",
            #      including its own `except`, which returns 0.0 and names the
            #      failure in degraded_inputs. There is nothing that function
            #      can do that reaches a handler here.
            #   3. If it ever HAD run, it would not have degraded the run — it
            #      would have killed it. The substitute dict has no
            #      "trend_direction_sign", and the bias engine call below reads
            #      that key by subscript OUTSIDE the try. The run would die of
            #      a KeyError at the next stage, reported as neither a trend
            #      failure nor a bias failure.
            #
            # A module breaking its own return contract is a defect in this
            # program, not a condition of the market, so "degrade, don't halt"
            # does not apply: there is no partial trend health to carry
            # forward, and no honest number to carry it with. It is reported as
            # the failure it is, in the same shape sections 2 and 3 already use.
            trend = compute_trend_health(df_struct)
            if not isinstance(trend, dict) or "trend_health" not in trend:
                logger.error("Trend health engine returned an invalid format")
                decision_object = {
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "error": (
                        "Trend health analysis failed: compute_trend_health "
                        "returned an invalid format. That is a contract "
                        "violation in indicators/trend_health.py, not a market "
                        "condition, so no substitute score is invented for it."
                    ),
                }
                return decision_object

            # SEQUENCE ITEM 9a: trend_health names the inputs it scored
            # without. Those are degradations of this run, not of that
            # module, so they join the same list.
            degradation.extend(trend.get("degraded_inputs", []))

            # 5. BIAS ENGINE
            # Roadmap Layer 2: bias_engine.py's weighted blend now uses three
            # more factors that were already available here but never passed
            # through -- structure_regime, volume_sentiment, and macro_bias
            # (all computed above), plus SuperTrend direction (extracted here).
            supertrend_direction = float(df_struct["ST_Direction"].iloc[-1]) if "ST_Direction" in df_struct.columns else 0.0

            # SEQUENCE ITEM 6: the df=df_struct argument is gone. See
            # bias_engine.calculate_dynamic_bias — it never read the frame.
            # AUDIT FINDING 7: the blend fills this in as it runs, so what is
            # recorded is the arithmetic that produced bias_score rather than
            # a second computation of it. See bias_engine.calculate_dynamic_bias.
            bias_components: Dict[str, Any] = {}
            raw_bias, bias_score = calculate_dynamic_bias(
                trend_sequence=trend_sequence,
                trend_health=trend["trend_health"],
                trend_exhaustion=trend["trend_exhaustion"],
                reversal_direction=trend.get("reversal_direction"),
                reversal_strength=trend.get("reversal_strength", 0),
                continuation_strength=trend.get("continuation_strength"),
                # 4 SEPTEMBER 2026: the trend direction now travels explicitly
                # rather than being inferred from continuation_strength's sign
                # inside bias_engine. Read with [] rather than .get(): a missing
                # key here means trend_health did not run, and defaulting it to
                # 0 would zero a 30% weight -- the exact defect this closes.
                trend_direction_sign=trend["trend_direction_sign"],
                structure_regime=structure_regime,
                volume_sentiment=volume_sentiment,
                supertrend_direction=supertrend_direction,
                macro_bias=macro_bias,
                components=bias_components,
            )

            dynamic_regime, volatility_mode = calculate_dynamic_regime(df_struct)
            detailed_bias = self.bias_state_machine.transition(raw_bias, bias_score)

            bias = {
                "raw": raw_bias,
                "detailed": detailed_bias,
                "score": bias_score,
                "regime": dynamic_regime,
                "volatility": volatility_mode,
            }

            # 6. STRUCTURE SUMMARY
            # 2 SEPTEMBER 2026: both fallbacks were 0.0. A structural level of
            # zero is finite, so risk_model would have accepted it and placed
            # a long's stop at $0.0000. NaN is what "not located" means here.
            hvn = float(df_struct["HVN"].iloc[-1]) if "HVN" in df_struct.columns else float(structure_obj.get("hvn", float("nan")))
            lvn = float(df_struct["LVN"].iloc[-1]) if "LVN" in df_struct.columns else float(structure_obj.get("lvn", float("nan")))

            structure = {
                "regime": structure_regime,
                "sequence": trend_sequence,
                "hvn": hvn,
                "lvn": lvn,
                "volume_sentiment": volume_sentiment,
                # A6-adjacent FIX: now propagated through to the decision object
                # instead of being dropped, so panel_render.py's SWING STRUCT line
                # reflects the real value from structure.py (still current_price
                # today per the A7 stub, but wired correctly for when B2 lands).
                "swing_struct": swing_struct,
            }

            # 6b. BTC MARKET CONTEXT (new feature, informational only).
            #
            # This NEVER changes BIAS, DECISION, entry, risk, or targets
            # above -- per the explicit requirement this was built to: BTC
            # context is additive, never a replacement or distortion of the
            # AERO-only analysis. It reuses the exact same, already-tested
            # indicators/structure/trend_health/bias_engine functions above,
            # just run a second time on BTC's own data, plus a correlation +
            # beta reading between AERO and BTC. Wrapped end-to-end so any
            # failure here (bad fetch, bad data) can never break or alter
            # the AERO panel -- it just falls back to "unavailable."
            btc_context = {"available": False}
            try:
                if symbol.upper() != "BTCUSDT":
                    df_btc = data_fetcher.get_tf("BTCUSDT", timeframe, limit=limit)
                    if self._validate_dataframe(df_btc, required_base_cols, "BTC context data"):
                        raw_btc = df_btc.copy()  # AUDIT FINDING 6 -- see raw_struct above
                        # BTC failures are recorded but do not degrade the run:
                        # BTC context is informational and already has its own
                        # available/unavailable flag. Naming them still beats
                        # silence when the BTC panel looks wrong.
                        df_btc, btc_failures = add_technical_indicators(df_btc)
                        for f in btc_failures:
                            logger.warning(f"BTC context indicator failure: {f}")
                        btc_structure_obj = calculate_structure(
                            df_btc, lookback=config.STRUCT_LOOKBACK,
                            volume_profile_bins=config.VOLUME_PROFILE_BINS
                        )
                        df_btc_struct = btc_structure_obj.get("df", df_btc)
                        btc_trend = compute_trend_health(df_btc_struct)

                        btc_supertrend_direction = (
                            float(df_btc_struct["ST_Direction"].iloc[-1])
                            if "ST_Direction" in df_btc_struct.columns else 0.0
                        )
                        btc_raw_bias, btc_bias_score = calculate_dynamic_bias(
                            trend_sequence=btc_structure_obj.get("sequence", "NONE"),
                            trend_health=btc_trend["trend_health"],
                            trend_exhaustion=btc_trend["trend_exhaustion"],
                            reversal_direction=btc_trend.get("reversal_direction"),
                            reversal_strength=btc_trend.get("reversal_strength", 0),
                            continuation_strength=btc_trend.get("continuation_strength"),
                            trend_direction_sign=btc_trend["trend_direction_sign"],
                            structure_regime=btc_structure_obj.get("regime", "NEUTRAL STRUCTURE"),
                            volume_sentiment=btc_structure_obj.get("volume_sentiment", "NEUTRAL VOLUME"),
                            supertrend_direction=btc_supertrend_direction,
                            # V1: BTC's own macro-timeframe confluence isn't fetched
                            # separately yet (a third API call for diminishing
                            # returns at this stage) -- straightforward to add later.
                            macro_bias="NEUTRAL",
                        )
                        btc_dynamic_regime, btc_volatility_mode = calculate_dynamic_regime(df_btc_struct)
                        btc_detailed_bias = self.btc_bias_state_machine.transition(btc_raw_bias, btc_bias_score)

                        correlation, beta, n_obs = compute_correlation_beta(
                            df_struct["close"], df_btc_struct["close"], window=30
                        )

                        btc_context = {
                            "available": True,
                            "raw": btc_raw_bias,
                            "detailed": btc_detailed_bias,
                            "score": float(btc_bias_score),
                            "regime": btc_dynamic_regime,
                            "volatility": btc_volatility_mode,
                            "trend_health": float(btc_trend["trend_health"]),
                            # AUDIT FINDING (a), 5 September 2026. NaN means
                            # "not measured" inside btc_context; None is how
                            # this file already spells it in the record (see
                            # risk_inputs' atr and structural_level below), and
                            # it is what serialises to JSON null. n_observations
                            # is the flag the panel and decision model gate on.
                            "correlation": (
                                float(correlation)
                                if math.isfinite(correlation) else None),
                            "correlation_label": classify_correlation(correlation),
                            "beta": float(beta) if math.isfinite(beta) else None,
                            "broad_market_stress": classify_stress(btc_volatility_mode),
                            "n_observations": n_obs,
                        }
            except Exception as e:
                logger.warning(f"BTC context analysis failed (AERO analysis above is unaffected): {e}")
                btc_context = {"available": False}

            # 7. ENTRY MODEL & ENTRY QUALITY ENGINE
            long_signal, short_signal = generate_entry_signals(
                detailed_bias=detailed_bias,
                structure_regime=structure_regime,
                trend_health=trend["trend_health"],
                trend_exhaustion=trend["trend_exhaustion"],
                reversal_strength=trend.get("reversal_strength", 0),
                macro_bias=macro_bias,
            )

            # AUDIT FINDING (4), 5 September 2026. These two lines were:
            #
            #   entry_zone_lower = float(EMA_20) if present else close * 0.99
            #   entry_zone_upper = float(EMA_50) if present else close * 1.01
            #
            # TWO defects, and only one of them was on the list.
            #
            # The listed one: a missing EMA produced a band one percent either
            # side of the last price. That is not a measurement of anything --
            # not of this instrument, not of its moving averages -- and it fed
            # the 30-point EMA position score, the 25-point ATR distance score
            # (which measures distance to this zone), the entry status and the
            # ZONE DISTANCE percentage. entry_model.py held the mirror image
            # of the same constants, which is why the fix takes two files.
            #
            # The unlisted one, seen on the live run at fa68197 and recorded
            # in PHASE7_NEXT: EMA_20 went to `lower` and EMA_50 to `upper`
            # unconditionally. In an uptrend the fast EMA is ABOVE the slow
            # one, so the panel printed
            #
            #     ENTRY ZONE    : $0.4981 - $0.4918
            #
            # with the lower bound above the upper. entry_model swaps them
            # before scoring, so the arithmetic was right the whole time and
            # only the display was wrong -- which is why no test caught it and
            # why reading the panel did. The bound named "lower" is now the
            # lower of the two.
            if ("EMA_20" in df_struct.columns and "EMA_50" in df_struct.columns):
                ema_fast = float(df_struct["EMA_20"].iloc[-1])
                ema_slow = float(df_struct["EMA_50"].iloc[-1])
                if math.isfinite(ema_fast) and math.isfinite(ema_slow):
                    entry_zone_lower = min(ema_fast, ema_slow)
                    entry_zone_upper = max(ema_fast, ema_slow)
                else:
                    entry_zone_lower = float("nan")
                    entry_zone_upper = float("nan")
                    degradation.append(
                        "entry zone (EMA_20/EMA_50 present but not finite)")
            else:
                # NaN, not a fabricated band. entry_model scores the position
                # component neutrally and reports ZONE NOT AVAILABLE, and the
                # absence is named here so the run reports itself degraded --
                # which is what stops it authorising a trade.
                entry_zone_lower = float("nan")
                entry_zone_upper = float("nan")
                missing = [c for c in ("EMA_20", "EMA_50")
                           if c not in df_struct.columns]
                degradation.append(
                    f"entry zone ({'/'.join(missing)} unavailable)")

            # A6-adjacent FIX: calculate_entry_quality() accepts macro_bias and
            # trade_direction to apply its macro-confluence multiplier, but neither
            # was ever passed, so that multiplier silently defaulted to neutral/LONG
            # every call. Now derives trade_direction from whichever signal (if any)
            # is active and passes the real macro_bias through.
            #
            # Roadmap Layer 5: also passes trend_direction (trend_health.py) and
            # structure_sequence (structure.py's B2 sequence, already computed
            # above as trend_sequence) through, so entry quality's own multipliers
            # can factor in whether the granular trend/structure context actually
            # supports this specific trade direction.
            eq_trade_direction = "SHORT" if short_signal else "LONG"
            eq_metrics = calculate_entry_quality(
                df_struct,
                entry_zone_lower,
                entry_zone_upper,
                macro_bias=macro_bias,
                trade_direction=eq_trade_direction,
                trend_direction=trend.get("trend_direction", "NEUTRAL"),
                structure_sequence=trend_sequence,
            )

            entry = {
                "zone_lower": entry_zone_lower,
                "zone_upper": entry_zone_upper,
                "long_signal": long_signal,
                "short_signal": short_signal,
                "score": eq_metrics["score"],
                "ema_pos_pts": eq_metrics["ema_pos_pts"],
                "atr_dist_pts": eq_metrics["atr_dist_pts"],
                "vwma_pts": eq_metrics["vwma_pts"],
                "rsi_pts": eq_metrics["rsi_pts"],
                "struct_pts": eq_metrics["struct_pts"],
                "entry_status": eq_metrics["entry_status"],
                "distance_from_zone": eq_metrics["distance_from_zone"],

                # 5 September 2026: the reconciliation between the five
                # sub-scores and the printed total. Every one of these was a
                # local variable inside calculate_entry_quality that vanished
                # when it returned, so neither the panel nor the decision log
                # could explain why 10+5+10+10+4 was printed under 45.18.
                "base_score": eq_metrics["base_score"],
                "component_max_points": eq_metrics["component_max_points"],
                "macro_multiplier": eq_metrics["macro_multiplier"],
                "trend_multiplier": eq_metrics["trend_multiplier"],
                "structure_multiplier": eq_metrics["structure_multiplier"],
                "combined_multiplier": eq_metrics["combined_multiplier"],
                "scaled_score": eq_metrics["scaled_score"],
                "score_ceiling": eq_metrics["score_ceiling"],
                "score_clipped": eq_metrics["score_clipped"],
            }

            # 8. RISK MODEL & VALIDATION ENGINE
            current_price = float(df_struct["close"].iloc[-1])
            # AUDIT FINDING 6, 5 September 2026. This line ended in
            #     ... else (current_price * 0.02)
            # — the same flat 2%-of-price constant sequence item 9a removed
            # from indicators.py and Finding 3 removed from entry_model.py,
            # still alive in the third consumer of the ATR column. On this
            # repo's pinned fixture the real ATR is 0.010554 and that
            # substitute is 0.016035: a 52% overstatement of how far this
            # instrument moves, and it sets the stop distance and all three
            # targets.
            #
            # It was also unreachable, which is how it survived two passes that
            # deleted its siblings. Section 2 above returns an error object
            # when ATR is absent from `df`, and structure.py's
            # calculate_structure works on a .copy() of that frame, so ATR is
            # present in df_struct on every path that reaches this line.
            #
            # Unreachable is not the same as safe: it is one edit to either of
            # those two facts away from being the live path. The invariant is
            # asserted rather than silently substituted.
            if "ATR" not in df_struct.columns:
                raise ValueError(
                    "ATR is absent from the structure frame. Section 2 "
                    "guarantees it on df and structure.py returns a copy of "
                    "that frame, so reaching this means one of those two "
                    "invariants has broken. No stop distance is invented in "
                    "its place — see section 2 for why a risk plan has no "
                    "degraded form."
                )
            atr_val = float(df_struct["ATR"].iloc[-1])

            atr_stop, t1, t2, t3 = self.risk_model.calculate_stop_targets(
                detailed_bias=detailed_bias,
                trend_health=trend["trend_health"],
                current_price=current_price,
                atr_val=atr_val,
                structural_level=hvn,
                bias_score=bias_score,
            )

            # A6 FIX: previously called with a bogus reference_price=current_price
            # kwarg (silently absorbed by **kwargs, doing nothing) and never passed
            # volatility_state/trend_health, so risk validation always ran against
            # the function's hardcoded defaults ("NORMAL", 50.0) regardless of
            # actual market conditions. Now passes the real, current values.
            # ITEM 14 RE-AUDIT (Finding 5): now returns risk_regime as a
            # third value -- see models/risk_model.py. Carried into the risk
            # dict below so decision_model.py can gate the AGGRESSIVE label
            # on it, independently of trend health and entry quality.
            risk_valid, risk_reason, risk_regime = self.risk_model.validate_risk_parameters(
                current_price=current_price,
                atr_stop=atr_stop,
                volatility_state=volatility_mode,
                trend_health=trend["trend_health"],
            )

            # SEQUENCE ITEM 13 — position sizing removed.
            #
            # This block computed position_size, position_value and risk_amount
            # from config.DEFAULT_ACCOUNT_BALANCE and DEFAULT_RISK_PERCENT.
            # Viktor ruled on 29 August 2026 that the engine must not do this:
            # monetary sizing belongs in the portfolio/execution layer, which is
            # the only layer that knows the real balance and the real exposure.
            #
            # The two config constants are gone with it, so nothing can quietly
            # start reading a placeholder balance again. See
            # models/risk_model.py for the full note.

            # ============================================================
            # VALIDATION — SEQUENCE ITEM 11 (Item 11, No Circular Reasoning)
            # ============================================================
            #
            # This block used to open with `val_score = trend_health` and then
            # nudge it by ±5 and +10/−15. Validation was therefore trend health
            # wearing a second name, and it reached confidence a third time
            # through validation_adj — after arriving directly and again inside
            # bias_score.
            #
            # A validation signal must be INDEPENDENT of the thing it
            # validates, or it is a restatement. It now starts neutral and
            # moves only on evidence trend health does not already contain:
            # volume behaviour, and whether the higher timeframe agrees.
            #
            # The macro test also used to be direction-blind: `-= 5` for any
            # bearish macro, even when the engine's own bias was bearish and
            # macro therefore AGREED. Validation measures agreement, not
            # direction.
            #
            # Weights are a judgment, and stated as one: disconfirming evidence
            # weighs more than confirming, and STRONG requires BOTH signals
            # (50+15+10=75) rather than either alone (65 or 60, both NEUTRAL).
            # A gate that opens on one input is not a gate.
            val_score = 50.0
            val_notes = []

            macro_delta, macro_note = macro_agreement(macro_bias, raw_bias)
            val_score += macro_delta
            val_notes.append(macro_note)

            volume_delta, volume_note = volume_agreement(volume_sentiment, raw_bias)
            val_score += volume_delta
            val_notes.append(volume_note)

            # The three "Trend health is robust / moderate / degrading" notes
            # that used to live here are gone with the rest: they restated the
            # TREND line verbatim in a section headed Validation Notes.

            val_score = max(0.0, min(100.0, val_score))

            if val_score >= 70:
                validation_state = "STRONG"
            elif val_score >= 45:
                validation_state = "NEUTRAL"
            else:
                validation_state = "WEAK"

            validation_note = " | ".join(val_notes)

            risk = {
                "atr_stop": atr_stop,
                "targets": (t1, t2, t3),
                "risk_valid": risk_valid,
                "risk_reason": risk_reason,
                "risk_regime": risk_regime,
                # SEQUENCE ITEM 13 — risk_score and signal_strength removed.
                # Both were assigned bias_score verbatim, making three names for
                # one number in a single object, and the third — bias.score — is
                # the one that says what it holds. Neither alias was read by any
                # consumer: panel_render.py bound risk_score to a local and then
                # printed validation_score and confidence_score instead. An
                # unread field with a misleading name is worse than no field,
                # because the next reader believes it.
                "confidence_score": trend["trend_health"],
                "trade_quality_proposed": eq_metrics["score"],
                "validation_state": validation_state,
                "validation_score": val_score,
                "validation_note": validation_note,
            }

            # 9. EXIT MODEL
            #
            # SEQUENCE ITEM 5b: compute_exit was called here and its six-key
            # result placed at decision_object["exit"]. Five of those keys —
            # final_action, exit_reason, stop_loss, target_hit, exit_status —
            # were computed on every run and discarded: signal_router.py:265
            # builds its own two-key "exit" dict from DecisionModel's action
            # and this current_price, and nothing downstream ever saw the rest.
            # The panel prints a stop loss, but reads risk["atr_stop"], not the
            # one compute_exit returned.
            #
            # The sixth key, current_price, was float(df_struct["close"]
            # .iloc[-1]) — the identical expression already evaluated above at
            # the top of section 8, on the same frame. df_struct is assigned
            # once, in section 3, and never reassigned, so the two values were
            # equal by construction rather than by coincidence.
            #
            # exit_model.build_exit_watch stays. It is the advisory-flag
            # function, it is consumed, and it is unrelated.

            # C3 BUILD: Exit Watch -- advisory-only flags (see exit_model.py's
            # build_exit_watch docstring). Uses prior_state (loaded at the top
            # of this run) for the two flags that need a run-over-run
            # comparison (SuperTrend flip, bias flip).
            exit_watch = build_exit_watch(
                trend=trend,
                structure=structure,
                bias=bias,
                current_price=current_price,
                supertrend_direction=supertrend_direction,
                target_t1=t1,
                prior_state=prior_state,
            )

            # Persist this run's state so the NEXT run can detect a
            # SuperTrend flip / bias flip against it.
            self._save_state(
                symbol, timeframe,
                {"supertrend_direction": supertrend_direction, "detailed_bias": detailed_bias},
            )

            # 10. CHARTING
            chart_path = None
            if save_chart:
                chart_path = plot_engine_chart(
                    df=df_struct,
                    entry_data={
                        "entry_zone_lower": entry_zone_lower,
                        "entry_zone_upper": entry_zone_upper,
                    },
                    risk_data={
                        "atr_stop": atr_stop,
                        "targets": (t1, t2, t3),
                    },
                    # SEQUENCE ITEM 14: was an f-string joining CHART_DIR —
                    # which already ends in a separator — with "/", producing
                    # "logs/charts//chart_...". Harmless to the filesystem and
                    # wrong in every path this engine reported.
                    save_path=os.path.join(
                        config.CHART_DIR, f"chart_{symbol}_{timeframe}.png"),
                )

            # ============================================================
            # 10b. LINEAGE -- AUDIT FINDINGS 6 AND 7
            # ============================================================
            #
            # Assembled here, after everything it describes has been computed
            # and before anything is returned, so it cannot describe a state
            # the run never reached.
            input_hashes = {
                "struct": lineage.frame_hash(raw_struct),
                "macro": lineage.frame_hash(raw_macro),
                "btc": lineage.frame_hash(raw_btc),
            }
            config_fingerprint = decision_log.config_snapshot(config)
            module_fingerprint = decision_log.module_snapshot()

            # The run's identity: the data AND the settings that decide what
            # is computed from it. Neither alone identifies a run -- the same
            # candles under different indicator lengths are a different
            # analysis, and so are different candles under the same settings.
            run_id = lineage.run_hash(
                input_hashes,
                {"config": config_fingerprint, "modules": module_fingerprint},
            )

            # Wrapped, on top of the swallowing those two functions already do
            # internally. Viktor's ruling of 29 August is degrade, not halt,
            # and this is the one place in a run where a purely audit-side
            # concern touches the disk. An analysis that was computed
            # correctly must reach the operator even when the archive cannot
            # be written: a traceability feature able to destroy the analysis
            # it documents would be a worse defect than the gap it closes.
            #
            # Belt and braces deliberately. write_archive() returning None
            # covers the failures it anticipates; this covers the ones it does
            # not.
            archive_path = None
            pruned = []
            try:
                archive_path = lineage.write_archive(
                    {"struct": raw_struct, "macro": raw_macro, "btc": raw_btc},
                    config.LOG_DIR, symbol, timeframe, run_id,
                    meta={
                        "engine_version": config.engine_version,
                        "config": config_fingerprint,
                        "modules": module_fingerprint,
                    },
                )
                # Retention is Viktor's ruling of 2 September 2026: ninety days
                # of rebuildable history, an unlimited life for the hash that
                # verifies. The run just written is passed as `keep` so it can
                # never be removed by its own prune, whatever the clock on this
                # machine says.
                pruned = lineage.prune(
                    config.LOG_DIR, lineage.RETENTION_DAYS, keep=[archive_path])
            except Exception as exc:
                # Deliberately NOT appended to `degradation`. That list blocks
                # the run from authorizing a trade and is about inputs the
                # ANALYSIS was computed without. The analysis here is complete;
                # what failed is the filing of it. Conflating the two would
                # refuse trades over a full disk.
                logger.warning(
                    f"Raw-input archive could not be written ({exc}). The "
                    f"analysis is unaffected and its input hashes are still "
                    f"recorded, so this run stays verifiable -- it is simply "
                    f"not rebuildable from this machine."
                )
                archive_path = None
            if pruned:
                logger.info(
                    f"Pruned {len(pruned)} raw-input archive(s) older than "
                    f"{lineage.RETENTION_DAYS} days. Their hashes remain in the "
                    f"decision log, so those runs stay verifiable against data "
                    f"fetched later -- they are no longer rebuildable from here."
                )

            # Item 6's chain, walkable end to end:
            #
            #   decision            -> the object returned below
            #   decision components -> bias_components, risk_inputs
            #   normalized signals  -> each factor's `signed` value
            #   raw signals         -> each factor's `input` value
            #   indicators          -> indicators_at_decision_bar
            #   validated data      -> inputs[*].sha256
            #   raw source data     -> archive
            #
            # Each link names the one below it, which is the property that
            # makes it a chain rather than a pile of fields.
            lineage_record = {
                "format": lineage.CANONICAL_FORMAT,
                "run_hash": run_id,
                "inputs": {
                    "struct": self._frame_summary(raw_struct, input_hashes["struct"]),
                    "macro": self._frame_summary(raw_macro, input_hashes["macro"]),
                    "btc": self._frame_summary(raw_btc, input_hashes["btc"]),
                },
                "indicators_at_decision_bar": self._decision_bar_row(df_struct),
                "bias_components": bias_components,
                "risk_inputs": {
                    "current_price": current_price,
                    "atr": atr_val if math.isfinite(atr_val) else None,
                    "structural_level": (
                        float(hvn) if (hvn is not None and math.isfinite(hvn)) else None),
                    "bias_score": bias_score,
                    "detailed_bias": detailed_bias,
                    "trend_health": trend["trend_health"],
                    "volatility_state": volatility_mode,
                    "risk_regime": risk_regime,
                },
                "archive": {
                    # The path this run's inputs were written to, or null. Null
                    # is recorded rather than the path that would have been
                    # used, because a record naming a file nothing wrote is the
                    # defect sequence item 12 exists to have closed.
                    "path": archive_path,
                    "pruned_this_run": len(pruned),
                    "retention_days": lineage.RETENTION_DAYS,
                },
            }

            # 11. UNIFIED RETURN OBJECT
            decision_object = {
                "symbol": symbol,
                "timeframe": timeframe,
                "macro_bias": macro_bias,
                "bias": bias,
                "trend": trend,
                "structure": structure,
                "entry": entry,
                "risk": risk,
                # SEQUENCE ITEM 5b: was compute_exit's six-key dict; the router
                # consumed exactly this one value out of it.
                "exit": {"current_price": current_price},
                # SEQUENCE ITEM 9a: every input this analysis was computed
                # without. Empty is the normal case.
                "degradation": list(degradation),

                # SEQUENCE ITEM 12 (Item 5, Reproducibility): what this run
                # actually saw. A stored decision without these cannot be
                # checked against anything — it is a receipt, not an audit
                # trail. engine_version has been defined in config since the
                # engine was built and written nowhere until now.
                "provenance": {
                    "engine_version": config.engine_version,
                    "last_candle": str(df_struct.index[-1]) if len(df_struct) else None,
                    "row_count": int(len(df_struct)),
                    # "pinned" rather than the directory: a pinned path is
                    # machine-specific and, in tests, a fresh temp directory
                    # per run — recording it made provenance differ between two
                    # runs on identical data, which is the opposite of what
                    # this block is for. WHAT the data was is fingerprinted by
                    # last_candle and row_count above; WHERE it sat is not part
                    # of the identity.
                    "source": "pinned" if data_fetcher.pinned_source() else str(data_fetcher.base_url),

                    # AUDIT FINDING 6. The five fields above identify a run
                    # only as far as a timestamp and a length can, which is not
                    # far: two different frames can share both, and nothing
                    # stored told them apart. These do.
                    "run_hash": run_id,
                    "input_hashes": input_hashes,
                    "canonical_format": lineage.CANONICAL_FORMAT,
                    "fetch": {
                        # Requested and effective, separately. They differ
                        # whenever the source holds less history than was asked
                        # for, and a record that stores only one of them cannot
                        # say which happened.
                        "requested_limit": limit,
                        "macro_requested_limit": macro_limit,
                        "effective_rows": {
                            "struct": int(len(raw_struct)) if raw_struct is not None else 0,
                            "macro": int(len(raw_macro)) if raw_macro is not None else 0,
                            "btc": int(len(raw_btc)) if raw_btc is not None else 0,
                        },
                        "pinned": bool(data_fetcher.pinned_source()),
                    },
                    # The state carried in from the previous run. Two runs on
                    # identical candles produce different Exit Watch flags when
                    # this differs, so a reconstruction without it is not a
                    # reconstruction.
                    "prior_state": prior_state,
                    "module_constants": module_fingerprint,
                    "archive_path": archive_path,
                },
                "exit_watch": exit_watch,
                # AUDIT FINDING 7 (Item 6, Traceability): the chain from this
                # decision back to the raw candles it was made from.
                "lineage": lineage_record,
                "btc_context": btc_context,
                "chart_path": chart_path,
            }

            return decision_object

        except Exception as e:
            logger.error(f"Critical error in Phase7Engine pipeline: {e}")
            traceback.print_exc()
            decision_object = {
                "symbol": symbol,
                "timeframe": timeframe,
                "error": str(e),
            }
            return decision_object