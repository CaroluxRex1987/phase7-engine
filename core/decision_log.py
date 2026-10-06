"""
The decision log — sequence item 12, Items 5 (Reproducibility) and 6
(Traceability).

WHY THIS FILE EXISTS

The panel has printed

    Trade logged to Logs/phase7_trade_log_<symbol>.csv

on every run since the engine was written, and no code anywhere wrote that
file. That is Item 6, rated Critical: the engine asserting that an audit action
occurred when it did not. Of the four Criticals it is the only one where the
engine was not merely wrong but actively claiming a safeguard it did not have.

Two ways to close it: stop making the claim, or make it true. Step 5 says make
it true, and that is right here in a way it was not for the `trend_failure`
gate at item 9c. That gate would have needed someone to decide when a trade
should be blocked — a trading judgment nobody could validate yet. This needs
nobody to decide anything. A log either exists on disk or it does not, and Item
5 requires one independently of what the panel says.

WHAT A RECORD CONTAINS, AND WHY

Item 5 is Reproducibility. A record that says only what the engine decided is a
receipt; a record that says what it decided AND what it saw is reproducible.
So each line carries a fingerprint of the inputs:

    last_candle     the timestamp of the newest bar the analysis used
    row_count       how much history it had
    source          the literal "pinned", or the live endpoint. Not the
                    pinned directory: that path is machine-specific and made
                    two runs on identical data record differently (see the
                    provenance block in core/engine_core.py). Corrected
                    21 September 2026, finding 21; this line had said "the
                    pinned directory" since the provenance change.
    engine_version  from config, where it has been defined and written
                    nowhere since the engine was built
    config          the knobs that change the numbers

Given those five, a run can be repeated. Without them a stored decision cannot
be checked against anything — which is the difference between an audit trail
and a diary.

JSONL, one object per line: appendable without parsing what came before,
readable by anything, and it survives a partial write with only the last line
damaged.

"Readable by anything" was not true until 21 September 2026 (finding 19).
json.dumps writes a float NaN as the bare token NaN unless told otherwise, and
NaN is not JSON: Python's json module reads it back, a strict reader (jq,
JavaScript's JSON.parse) rejects the whole line. The engine puts NaN in the
decision object on purpose -- it is how the router says "not measured" -- and
one record in the live log (6 September, swing_struct) carried it. So write()
now spells every non-finite float as null, the one JSON spelling of "no
value", and passes allow_nan=False so that a bare NaN can never be written
again. In the record, null is what NaN, +inf and -inf all mean: not a
number the engine could state. Records written before this change keep their
NaN tokens; read() still accepts them, since Python's parser does. A CSV cannot hold a nested decision object without flattening it, and
flattening is where fields go missing quietly.

THE LINE THE PANEL PRINTS IS NOW CONDITIONAL

write() returns the path on success and None on failure, and the panel prints
the line only when it gets a path. An engine that says "logged" when the disk
was full would be the same defect wearing a new filename.

WHERE A RECORD GOES -- B6, 6 OCTOBER 2026

Viktor's ruling of 5 October 2026, point 6: runs on pinned data write to their
own decision log, archive and Exit Watch state, chosen by the code from the
run's source rather than by a setting someone has to remember. Until then
every run wrote here, so the live log on Viktor's machine holds nine runs on
the synthetic fixture and one hand-built record among its live runs, and the
twelve-month paper-trading count would have had to exclude them by hand. They
stay where they are; the ruling names them in docs/PHASE7_DECISIONS.md.

records_dir() is the one place the directory is chosen. A live run's records
stay in config.LOG_DIR, byte for byte where they were. Every other record --
pinned, or one whose provenance does not say -- goes to its pinned/
subdirectory. write() chooses from the record itself: a record goes in the
live log only when its own provenance says its candles were fetched live
(is_live_record). engine_core makes the same choice once per run for the
state file and the archive, and records it in that same provenance field, so
the record's statement of its source and the place it is filed cannot
disagree.
"""

import json
import logging
import math
import os
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

LOG_FILENAME = "phase7_decision_log_{symbol}.jsonl"

# B6: the subdirectory of the log directory that holds every record not stated
# to be live -- its own decision log, archive/ and Exit Watch state.
PINNED_DIRNAME = "pinned"

# The knobs that change what the engine computes. Not every constant in
# config — CHART_* and the directory paths do not affect a decision, and a
# snapshot that logs them invites the reader to diff noise.
#
# SEQUENCE ITEM 14 owns a correction to this list, and it is the sharpest
# finding of that item. When this file was written at item 12, SEVEN of the
# names below — VOLUME_PROFILE_BINS, EMA_FAST, EMA_SLOW, RSI_LENGTH,
# ADX_LENGTH, ATR_LENGTH, VWMA_LENGTH — were read by nothing. The indicators
# hardcoded their own lengths and config's copies sat unused, so the log
# recorded seven settings as "the knobs that change the numbers" when changing
# any of them changed nothing.
#
# That is the same defect item 12 was written to close, in the record item 12
# created: an audit trail asserting something that is not true. It is fixed by
# making the claim true — item 14 wired every one of these to its calculation —
# rather than by shortening the list, because a run's identity really does
# depend on them. tests/test_explicit_configuration.py holds it true.
FINGERPRINTED_CONFIG = [
    "SYMBOL", "TIMEFRAME", "MACRO_TIMEFRAME",
    # AUDIT FINDING 6 (Item 5): the endpoint decides WHICH candles a
    # run saw, so two runs against different exchanges were previously
    # indistinguishable in the config half of the record. provenance
    # already carried a source string; fingerprinting it here is what
    # puts it inside the run hash, where a change to it changes the
    # run identity instead of merely being noted beside it.
    "API_BASE_URL",
    "STRUCT_LOOKBACK", "VOLUME_PROFILE_BINS",
    "EMA_FAST", "EMA_SLOW",
    "RSI_LENGTH", "ADX_LENGTH", "ATR_LENGTH",
    "VWMA_LENGTH", "SUPERTREND_LENGTH", "SUPERTREND_MULT",
    # DEFAULT_ACCOUNT_BALANCE and DEFAULT_RISK_PERCENT were fingerprinted here
    # until sequence item 13 removed position sizing and, with it, both
    # constants. Nothing in a decision depends on an account balance now, so
    # recording one would suggest the number still meant something.
]


MISSING = "<not defined in config>"


def config_snapshot(config):
    """
    The subset of config that can change a decision.

    A name this list declares but config does not define is RECORDED as absent
    rather than omitted. Skipping it would leave a record that looks complete
    and is not — the reader has no way to tell a knob that was missing from one
    that was never fingerprinted.
    """
    return {name: getattr(config, name, MISSING) for name in FINGERPRINTED_CONFIG}


# AUDIT FINDING 6 (Item 5). The audit's required action asks for "all
# decision-affecting configuration, including risk-model multipliers and bias
# weights." Those are not in config.py -- they are module-level constants in
# the models that use them, which is the right place for them to live and the
# wrong place for them to be invisible.
#
# The weights are the sharpest case. bias_score is a weighted blend of six
# factors, and changing 0.30 to 0.35 changes every decision the engine makes
# while leaving config, the candles and the indicator lengths all identical.
# Before this, two such runs were byte-identical in the record.
#
# Read live from the modules rather than restated here. A copy of the numbers
# in this file would be a second declaration that agrees with the first only
# until someone edits one of them -- the defect this project has now recorded
# three times (seven dead config constants at sequence item 14, a guard list
# short by three indicators at Finding 3, a stale docstring at 2be405f).
#
# KIMI FINDING 3, ROUND 4 -- WHAT THIS DICT IS FOR NOW, AND WHAT IT IS NOT
#
# The finding is that two runs on different code recorded identical hashes,
# and it names seven decision-affecting settings this dict does not contain.
# Six of the seven cannot be added to it at all: SPIKE_RATIO is a function
# local, and the entry multipliers, the trend bands, 0.0015 and window=30 are
# bare literals. `getattr(module, name)` reaches none of those. Extending an
# enumeration was never available as the fix -- and an enumeration cannot see
# a changed operator or a reordered branch in any case, both of which change
# what the engine decides.
#
# core/code_fingerprint.py closes the finding by hashing the parse tree of
# every source file. It needs no list, so it cannot fall behind the code.
#
# This dict is KEPT, and its job has narrowed to the half a hash cannot do:
# saying WHICH knob a run used, in numbers a person can read, without
# reconstructing the tree from an archive. A hash says two runs differ; this
# says the stop multiplier was 1.2. Both are in the record because they answer
# different questions, and neither is a substitute for the other.
#
# 6 September 2026: the two DecisionModel constants below are the only two of
# the seven that are nameable, and naming them needed module_snapshot() to
# learn dotted paths -- see there. models.entry_model was never fingerprinted
# despite its scoring constants deciding entry quality on every run; it is
# added here because those constants are module-level and therefore readable,
# not because the code hash needs the help.
FINGERPRINTED_MODULES = {
    "models.bias_engine": [
        "WEIGHT_TREND_HEALTH", "WEIGHT_STRUCTURE_REGIME",
        "WEIGHT_VOLUME_SENTIMENT", "WEIGHT_SUPERTREND_DIRECTION",
        "WEIGHT_MACRO_BIAS", "WEIGHT_REVERSAL_CONTINUATION",
        "RAW_BIAS_THRESHOLD",
    ],
    # The other half of Finding 6's required action, and it was missing
    # until 2 September. The comment above has quoted "risk-model
    # multipliers and bias weights" since the fix was written, while the
    # dict named only the weights. Changing ATR_STOP_MULT from 1.2 to 1.5
    # moves the stop and all three targets on every run the engine makes,
    # and until now left run_hash, config_snapshot and module_snapshot
    # byte-identical -- an audit trail asserting two different plans were
    # the same run.
    #
    # It was not an omission from this list. models/risk_model.py held
    # these on the RiskModel INSTANCE, where module_snapshot() cannot
    # see them, so there was nothing here to name. The constants moved
    # to module level in the same change that added this entry.
    # 5 September 2026: MIN_ACTION_BIAS decides whether a directional lean is
    # strong enough to act on. Changing it changes which runs authorise a
    # trade, so it belongs inside run_hash by the same argument that put the
    # risk multipliers there.
    #
    # KIMI FINDING 3: the two dotted names are class attributes of
    # DecisionModel, not module-level constants, so they were unreachable by
    # the plain getattr this dict was built around. DEGRADED_CONFIDENCE_CEILING
    # is the ceiling a degraded run's confidence is clipped to and
    # BTC_ADJUSTMENT_CAP bounds how far BTC context can move that confidence --
    # both decide numbers an operator reads and both were invisible in the
    # record. models/risk_model.py answered the same problem in September by
    # moving its constants to module level; these stay where they are and
    # module_snapshot() learned to walk to them instead, because moving a
    # constant is a change to the decision path and this patch is a change to
    # the record.
    # ROUND 6 (Meta Muse Spark 1.3), F1 follow-up, 13 September 2026: three
    # more of the same shape as DEGRADED_CONFIDENCE_CEILING/BTC_ADJUSTMENT_CAP
    # above -- the AGGRESSIVE-eligibility and CONSERVATIVE trend-health bands,
    # promoted from bare literals inside _determine_final_action.
    "models.decision_model": [
        "MIN_ACTION_BIAS",
        "DecisionModel.DEGRADED_CONFIDENCE_CEILING",
        "DecisionModel.BTC_ADJUSTMENT_CAP",
        "DecisionModel.AGGRESSIVE_TREND_HEALTH_MIN",
        "DecisionModel.AGGRESSIVE_ENTRY_SCORE_MIN",
        "DecisionModel.CONSERVATIVE_TREND_HEALTH_MIN",
        # FINDING 22, 21 September 2026. Three class constants that set numbers
        # the operator reads and were missing from this list, found in the
        # deferred read. BTC_STRESS_PENALTY is BTC_ADJUSTMENT_CAP's sibling --
        # the two together bound the BTC-adjusted confidence -- and only the
        # cap was here. AVG_REWARD_R and EV_BREAKEVEN_BAND_R set the
        # illustrative EV sentence and its "worth taking" verdict. All three
        # were already inside code_hash, so a change to them was detected;
        # what the record could not say was which value a run used. Adding
        # them changes run_hash (this dict is part of its payload) and so the
        # archive's file name -- predicted, and the golden snapshot
        # re-baselined in the same commit.
        "DecisionModel.BTC_STRESS_PENALTY",
        "DecisionModel.AVG_REWARD_R",
        "DecisionModel.EV_BREAKEVEN_BAND_R",
    ],
    # KIMI FINDING 3 names "the entry multipliers", which were the bare 1.05
    # and 0.90 literals in generate_entry_signals' confluence ladder and were
    # not nameable here at the time. The rest of this dict's comment still
    # applies to the point budget below -- the entry score is built out of it.
    #
    # ROUND 6 (Meta Muse Spark 1.3), F1, 13 September 2026:
    # CONFLUENCE_BOOST_MULT and CONFLUENCE_PENALTY_MULT are the six literals
    # Kimi's finding could not name, now module-level constants in
    # models/entry_model.py and nameable here like everything else in this
    # list.
    "models.entry_model": [
        "EMA_ZONE_MAX_POINTS", "ATR_DISTANCE_MAX_POINTS",
        "VWMA_MAX_POINTS", "RSI_MAX_POINTS", "STRUCTURE_MAX_POINTS",
        "COMPONENT_MAX_POINTS", "SCORE_CEILING",
        "ZONE_POINTS_NOT_MEASURED", "ATR_POINTS_NOT_MEASURED",
        "CONFLUENCE_BOOST_MULT", "CONFLUENCE_PENALTY_MULT",
        # FIX 2, 5 October 2026: the confirmation gate's ADX threshold -- under
        # it, no side confirms. It decides which runs may trade, so it is in
        # the run-hash payload by the same argument as MIN_ACTION_BIAS above;
        # adding it moves run_hash, and with it the archive's file name.
        "MIN_TREND_ADX",
    ],
    "models.risk_model": [
        "ATR_STOP_MULT", "TARGET1_MULT", "TARGET2_MULT", "TARGET3_MULT",
        "VOL_MULT_HIGH", "VOL_MULT_LOW", "VOL_MULT_EXTREME",
        # FIX 1, 5 October 2026: "TREND_FACTOR_DIVISOR" and
        # "BIAS_FACTOR_DIVISOR" stood here. The stop no longer scales with
        # trend health or the bias score, and both constants are gone from
        # models/risk_model.py, so both names leave the run-hash payload --
        # which moves run_hash, and with it the archive's file name.
        # ITEM 14, 11 September 2026: REGIME_LOW_TREND_HEALTH and
        # REGIME_HIGH_TREND_HEALTH were renamed to REGIME_CHOP_ADX and
        # REGIME_STRONG_ADX when the risk regime stopped reading trend_health.
        # Renaming a fingerprinted constant without updating this list drops
        # it out of the run-hash payload silently, which is the decay rule 11
        # warns about.
        # FIX 3, 6 October 2026: REGIME_CHOP_ADX and REGIME_STRONG_ADX stood
        # after REGIME_EXTREME_STOP_PCT here. The regime no longer reads ADX,
        # and both constants are gone from models/risk_model.py, so both names
        # leave the run-hash payload -- which moves run_hash, and with it the
        # archive's file name.
        "REGIME_EXTREME_STOP_PCT",
        "MAX_STOP_DISTANCE_PCT", "MIN_STOP_DISTANCE_PCT",
    ],
    # ROUND 6 (Meta Muse Spark 1.3), F1, 13 September 2026. Three more of
    # Kimi Finding 3's six unnameable literals, closed the same way as the
    # entry multipliers above: promoted to a named constant at the one place
    # each already lived, value unchanged.
    "indicators.indicators": ["SPIKE_RATIO"],
    "models.btc_context": ["CORRELATION_WINDOW"],
    # The sixth and last: 0.0015 was a bare local inside
    # StructureEngine._detect_regime, not module-level, so it needed the same
    # two-hop ClassName.ATTR resolution _resolve() already does for
    # DecisionModel's two class-attribute constants above.
    "structure.structure": ["StructureEngine.REGIME_HYSTERESIS_THRESHOLD"],
}


def _resolve(module, dotted):
    """
    Walk a dotted name from a module to the value at the end of it.

    KIMI FINDING 3. "MIN_ACTION_BIAS" is one hop and behaves exactly as the
    plain getattr did. "DecisionModel.DEGRADED_CONFIDENCE_CEILING" is two, and
    two hops is what the original could not do -- a constant held on a class
    recorded as MISSING, which is a record saying a knob was not defined when
    it was defined and being read on every run.

    A name that does not resolve returns MISSING, unchanged: the caller's
    contract is that a name it asked for always appears in the output.
    """
    value = module
    for part in dotted.split("."):
        value = getattr(value, part, MISSING)
        if value is MISSING:
            return MISSING
    return value


def module_snapshot():
    """
    The decision-affecting constants that live in modules rather than config.

    A module that cannot be imported records the reason instead of being
    omitted, for the same reason config_snapshot records a missing name: a
    record that looks complete and is not gives the reader no way to tell an
    absent value from one that was never asked for.

    This is the readable half of the code record and no longer the whole of it.
    The complete half is core/code_fingerprint.py, which covers the constants
    no dict of names can hold. See the comment on FINGERPRINTED_MODULES.
    """
    out = {}
    for module_name, names in FINGERPRINTED_MODULES.items():
        try:
            module = __import__(module_name, fromlist=["_"])
        except Exception as exc:
            # SWEEP ITEM 12, 8 September 2026. Documented shape: when a
            # fingerprinted module cannot be imported, the snapshot records
            # a single key "<import failed>" whose value is the exception
            # text, instead of the constant names. Callers must tolerate
            # this key; it is part of the run-hash payload by design.
            out[module_name] = {"<import failed>": str(exc)}
            continue
        out[module_name] = {
            name: _resolve(module, name) for name in names
        }
    return out


def _json_safe(value):
    """
    A copy of `value` in which every non-finite float is None.

    Finding 19, 21 September 2026 -- see the module docstring. Walks dicts,
    lists and tuples, the only containers the decision object uses; anything
    else is returned unchanged for json.dumps' `default=str` to handle, as
    before. numpy.float64 is a float subclass and is covered; a numpy.float32
    is not a float and still goes through `default=str`, which spells NaN as
    the string "nan" -- valid JSON, and the behaviour it had before this
    change. Integers, bools and strings are untouched.

    The decision object passed in is not modified: the record is a copy, and
    the caller's object may still be read after it is logged.
    """
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, dict):
        return {k: _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    return value


def is_live_record(decision):
    """
    B6: True only when the decision says, in both places its provenance
    records its source, that its candles were fetched live:
    `provenance.fetch.pinned` is exactly False, and `provenance.source` is a
    string other than "pinned" (the endpoint).

    Anything else is not a live record: a pinned run, a provenance that is
    missing, malformed or contradicts itself, a decision built by hand (the
    live log's fourth record, 6 September, was one). Failing safe: a record
    this cannot place is kept out of the live log, which is the record the
    paper-trading verdict will be read from, rather than let into it. On the
    engine's path every record carries both fields, set from one answer.
    """
    provenance = decision.get("provenance") if isinstance(decision, dict) else None
    if not isinstance(provenance, dict):
        return False
    fetch = provenance.get("fetch")
    source = provenance.get("source")
    return (isinstance(fetch, dict) and fetch.get("pinned") is False
            and isinstance(source, str) and source != "pinned")


def records_dir(log_dir, live):
    """
    B6: the directory a run's records go to, given the log directory.

    Live: `log_dir` itself, unchanged. Otherwise its pinned/ subdirectory,
    spelled with forward slashes and a trailing one on every platform, so a
    path joined under it -- the log, the archive, the state file -- is the
    same string on Windows and on Linux. Paths under it are written into the
    record, and the golden snapshot pins them (see lineage.write_archive()
    for the backslash this avoids).

    Built by string operations rather than os.path.join, so the answer for a
    given string does not depend on the machine: "C:\\x\\logs" gives
    "C:/x/logs/pinned/" on Linux as on Windows, and the tests can check the
    Windows case on either. An empty log_dir, the working directory, gives
    "pinned/".
    """
    if live:
        return log_dir
    base = str(log_dir).replace("\\", "/")
    if base and not base.endswith("/"):
        base += "/"
    return f"{base}{PINNED_DIRNAME}/"


def log_path(log_dir, symbol):
    return os.path.join(log_dir, LOG_FILENAME.format(symbol=str(symbol).lower()))


def write(decision, config, log_dir=None):
    """
    Append one decision to the log. Returns the path written, or None.

    None on failure rather than raising: a decision that was computed correctly
    should still reach the operator if the disk is full. What must not happen
    is the panel claiming it was logged anyway — the caller passes this return
    value to the panel, which prints the line only when there is a path.

    B6, 6 October 2026: `log_dir` (config.LOG_DIR when not given) is the log
    directory, and the record goes to records_dir(log_dir, is_live_record(
    decision)) -- the log directory itself only for a record that says it is
    live, its pinned/ subdirectory for every other. Passing a directory does
    not override that choice; no caller can put a pinned record in a live log.
    """
    try:
        symbol = str(decision.get("symbol", "unknown"))
        # SEQUENCE ITEM 14: the else branch was
        # getattr(config, "LOG_DIR", "Logs/"). The explicit log_dir argument
        # stays — tests pass an unwritable path through it deliberately — but
        # the config read no longer carries a shadow default.
        log_dir = log_dir if log_dir is not None else config.LOG_DIR
        directory = records_dir(log_dir, is_live_record(decision))
        os.makedirs(directory, exist_ok=True)
        path = log_path(directory, symbol)

        record = {
            "logged_at": datetime.now(timezone.utc).isoformat(),
            "engine_version": config.engine_version,
            "config": config_snapshot(config),
            "decision": decision,
        }

        # Finding 19: non-finite floats become null before serialising, and
        # allow_nan=False makes a bare NaN an error rather than a token no
        # strict JSON reader accepts. _json_safe covers every float the
        # decision object can hold, so the guard is not expected to fire; if
        # a future change ever made it fire, write() returns None and the
        # panel does not claim the run was logged -- the same contract as a
        # full disk.
        line = json.dumps(_json_safe(record), default=str, allow_nan=False)
        with open(path, "a", encoding="utf-8") as f:
            f.write(line + "\n")
        return path

    except Exception:
        # Deliberately swallowed and reported as None. Logging is an audit
        # concern; failing to log must not destroy an analysis that succeeded,
        # and the caller's contract is "path or nothing".
        return None


def read_with_report(log_dir, symbol):
    """
    Every record for one symbol, oldest first, and the line numbers skipped.

    Returns (records, skipped): `skipped` is the list of 1-based line numbers
    that could not be parsed.

    Finding 20, 21 September 2026. read() skipped any line it could not parse
    and said nothing. Its comment named the case it was written for -- a torn
    final line from an interrupted write -- but the code skipped a damaged
    line anywhere, so a corrupted record in the middle of the history vanished
    from what read() returned, with no count and no trace. Skipping is still
    right (one damaged record must not make the whole history unreadable);
    skipping without saying so is not, in the one file this project keeps as
    its audit trail.
    """
    path = log_path(log_dir, symbol)
    if not os.path.exists(path):
        return [], []
    out, skipped = [], []
    with open(path, encoding="utf-8") as f:
        for number, line in enumerate(f, start=1):
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    skipped.append(number)
    return out, skipped


def read(log_dir, symbol):
    """
    Every record for one symbol, oldest first. For tests and for reading back.

    A line that cannot be parsed is skipped, as before, and now reported: a
    warning names the file and every skipped line number. Callers that need
    the numbers themselves use read_with_report().

    B6: reads the one directory it is given. The records of pinned runs are
    read with read(records_dir(log_dir, False), symbol).
    """
    out, skipped = read_with_report(log_dir, symbol)
    if skipped:
        logger.warning(
            f"decision log {log_path(log_dir, symbol)}: {len(skipped)} "
            f"line(s) could not be parsed and were skipped: {skipped}"
        )
    return out
