# Phase-7 Structural Quant Engine — Complete Engine Source

Every Python module the engine runs, plus its dependency manifest. The test
suite is in the companion file.

Each file below is delimited by a `=== FILE: <path> ===` marker. Line
numbers are not included; cite locations by quoting the code itself.

---


=== FILE: core/__init__.py ===

```python

```


=== FILE: core/config.py ===

```python
"""
Phase‑7 Structural Quant Engine — Configuration Module
Centralized settings for market, risk, indicators, logging, and charting.
"""


# ============================================================
# ENGINE METADATA
# ============================================================

engine_version = "Phase‑7 Structural Quant Engine v1.0"


# ============================================================
# MARKET SETTINGS
# ============================================================

# Default trading symbol and timeframe
SYMBOL = "AEROUSDT"          # Main trading pair
TIMEFRAME = "4h"            # Execution candle interval
MACRO_TIMEFRAME = "1d"      # Macro Higher Timeframe for MTF Confluence


# ============================================================
# API SETTINGS
# ============================================================

# SEQUENCE ITEM 14: API_KEY and API_SECRET were declared here as empty strings
# and read by nothing. The engine uses only public OHLC endpoints and is never
# permitted to execute a trade, so there is no code path that could need a
# credential. Two empty credential slots sitting in the config of an engine
# that must not trade are an invitation, not a setting.

# Base URL for MEXC REST API
API_BASE_URL = "https://api.mexc.com"


# ============================================================
# LOGGING & STORAGE
# ============================================================

# SEQUENCE ITEM 14: lowercase. .gitignore ignores `logs/`, and these were
# `Logs/`. On Windows that is the same directory and the mismatch is
# invisible; on Linux it is a second directory that git does not ignore, so a
# clone that runs the engine gets its run artifacts staged for commit.
LOG_DIR = "logs/"
CHART_DIR = "logs/charts/"

# SEQUENCE ITEM 14: TRADE_LOG_DIR and REQUIRED_DIRS removed.
#
# TRADE_LOG_DIR was read by nothing but REQUIRED_DIRS, and REQUIRED_DIRS was
# read by nothing at all — the directories are created on demand by the code
# that writes into them (engine_core's state file, decision_log, plotting), so
# the list was a second declaration of a fact already enforced elsewhere.
#
# TRADE_LOG_DIR also named a directory for the trade log that sequence item 12
# established does not exist and never did. Keeping it would leave the last
# trace of that claim in the config.


# ============================================================
# RISK SETTINGS
# ============================================================

# SEQUENCE ITEM 13: DEFAULT_ACCOUNT_BALANCE (10,000) and DEFAULT_RISK_PERCENT
# (1.0) were defined here and read only by the position-sizing block in
# engine_core.py. Viktor ruled on 29 August 2026 that the engine must not
# compute monetary sizing, so both the computation and these constants are
# gone. Leaving them would leave a placeholder balance sitting in config for
# the next reader to wire back up.


# ============================================================
# STRUCTURE SETTINGS
# ============================================================

# Swing lookback for structural highs/lows
STRUCT_LOOKBACK = 8

# Volume profile resolution
VOLUME_PROFILE_BINS = 50


# ============================================================
# INDICATOR SETTINGS
# ============================================================

# EMA settings
EMA_FAST = 20
EMA_SLOW = 50

# Core indicators
RSI_LENGTH = 14
ADX_LENGTH = 14
ATR_LENGTH = 14

# SEQUENCE ITEM 14: BB_LENGTH, BB_STD and KAMA_LENGTH removed. Sequence item
# 5a deleted the Bollinger Bands and KAMA calculations as unconsumed output
# and left these three constants for this item, which is where config hygiene
# belongs. A length for an indicator the engine does not compute is a setting
# that cannot be set.

# Volume-weighted moving average
VWMA_LENGTH = 20

# Supertrend
SUPERTREND_LENGTH = 10
SUPERTREND_MULT = 3.0


# ============================================================
# CHART SETTINGS
# ============================================================

# SEQUENCE ITEM 14: these are now read by utils/plotting.py, which hardcoded
# figsize=(14, 8), dpi=200 and "dark_background" and ignored all four.
#
# Two of them DISAGREED with the code: config said height 10 and dpi 150, the
# renderer used 8 and 200. The declaration is corrected to what the engine has
# actually been drawing rather than the other way round — every chart Viktor
# has looked at came out at 14x8 and 200 dpi, and silently resizing them is a
# visible change nobody asked for. They are settings now, so changing these
# numbers changes the chart.
CHART_WIDTH = 14
CHART_HEIGHT = 8
CHART_DPI = 200
CHART_STYLE = "dark_background"
```


=== FILE: core/decision_contract.py ===

```python
"""
The decision-object contract.

Sequence item 10 (T2-3). This module declares the shape of the two objects the
engine passes around, so that a field change is checked against its consumers
instead of discovered by them.

WHY THIS EXISTS

T2-3's own evidence is an incident recorded in this project's Engineering Notes:
a rename broke fourteen modules at once. Nothing declared what the fields were,
so nothing could say what depended on them. The remediation items still ahead —
9 adds fields for degraded state, 11 renames the overloaded trend_health, 13
removes the position-sizing block — are all field changes on that same object.
Declaring the shape first is the guard those edits need.

TWO OBJECTS, NOT ONE

    ENGINE OUTPUT     what Phase7Engine.run() returns
                      consumed by SignalRouter only

    DECISION OBJECT   what SignalRouter.route() returns, built from the above
                      consumed by panel_render, live_trading, the golden
                      snapshot and the tests

They are different shapes. The router reads ten keys off the engine's output and
emits twelve of its own, some passed through, some replaced. A rename in the
lower layer breaks the router; a rename in the upper layer breaks everything
else. Only the upper one is pinned by the golden snapshot, which is why the
lower one needs declaring too.

WHY TypedDict AND NOT A VALIDATION SCHEMA

The types below are the single source of truth. tests/test_decision_contract.py
introspects them at runtime — it does not carry a second copy of the field list.
Two parallel declarations would drift, and drift between a schema and its
checker is a new failure mode rather than a guard against one.

ON mypy

Step 5's item 10 says "mypy does not exist in the repository (checked); adding
it is apparatus belonging to this item." The check is right; the conclusion is
not, and this is a deliberate departure from the plan, ruled by Viktor on
30 August 2026.

mypy would not have caught the incident this item exists to prevent. Every
consumer reads these objects with decision.get("risk_amount") or
decision["risk"] — string keys on a plain dict. mypy says nothing about either
unless the object is a TypedDict *and* every consumer is annotated to receive
it, which is a much larger refactor than item 10. Adding mypy without that
means configuring it loosely enough to pass on a fully untyped codebase: a
guard that cannot fail, which is the pattern this project has spent a week
removing.

The declarations below are TypedDicts precisely so that nothing is foreclosed.
If mypy and consumer annotations arrive later, the types are already here to
make it worth running.

WHAT ITEM 10 RECORDED AND ITEM 13 REMOVED

This file was written at item 10 to declare the shape honestly, including the
parts of it that were wrong. Four defects were declared rather than fixed,
because a field change needs verification and item 13 was where that lived:

  trend.health          duplicated trend.trend_health
  trend.momentum        duplicated trend.momentum_mode
  risk.risk_score       held bias_score
  risk.signal_strength  held bias_score

  risk.position_size, position_value, risk_amount,
  account_balance, risk_percent

All nine are gone as of sequence item 13. The two trend pairs were exact
duplicates assigned from the same expression; the two risk fields were a third
and fourth name for bias.score, read by nobody; the five sizing fields fell to
Viktor's ruling of 29 August 2026 that the engine must not compute monetary
position sizing.

The mechanism worked as intended and is worth recording. SCHEDULED_FOR_REMOVAL
and CANONICAL_ALIASES below are now empty, and the tests that watched them
fired when item 13 landed — which is what forced this file to be updated in the
same commit rather than left describing an engine that no longer existed.
"""

from typing import Any, Dict, List, Tuple

try:
    from typing import TypedDict
except ImportError:                      # Python < 3.8
    TypedDict = None                     # type: ignore


# ============================================================
# The decision object — SignalRouter.route()
# ============================================================

class BiasBlock(TypedDict):
    raw: str
    detailed: str
    score: float
    regime: str
    volatility: str


class TrendBlock(TypedDict):
    # `health` and `momentum` were declared here as duplicates of the two
    # fields below and removed at sequence item 13.
    trend_health: float
    exhaustion: bool
    momentum_mode: str
    momentum_divergence: bool
    trend_direction: str


class StructureBlock(TypedDict):
    regime: str
    sequence: str
    hvn: float
    lvn: float
    volume_sentiment: str
    swing_struct: float


class EntryBlock(TypedDict):
    zone_lower: float
    zone_upper: float
    long_signal: bool
    short_signal: bool
    score: float
    distance_from_zone: float
    entry_status: str
    ema_pos_pts: float
    atr_dist_pts: float
    vwma_pts: float
    rsi_pts: float
    struct_pts: float


class RiskBlock(TypedDict):
    atr_stop: float
    targets: Tuple[float, float, float]
    risk_valid: bool
    risk_reason: str
    # `risk_score` and `signal_strength` both held bias_score and were removed
    # at sequence item 13. bias.score is that number's one home.
    confidence_score: float
    trade_quality_proposed: float
    validation_state: str
    validation_score: float
    validation_note: str
    # The five position-sizing fields were declared here and removed at
    # sequence item 13 — see module docstring.
    ev_r: float
    assumed_win_rate: float
    avg_reward_r: float


class ExitBlock(TypedDict):
    action: str                   # DecisionModel's verdict, not exit_model's
    current_price: float


class ExplanationBlock(TypedDict):
    summary: str
    reasons: List[str]


class _BtcContextRequired(TypedDict):
    """The half of the BTC block that is always present. See below."""
    available: bool


class BtcContextBlock(_BtcContextRequired, total=False):
    """
    Two legal shapes, and `available` says which one you have.

    When BTC context is unavailable — the run IS BTCUSDT, or the fetch failed —
    _merge_btc_context returns {"available": False} and nothing else. Every
    consumer must check that flag before reading any other key.

    THE SPLIT BASE CLASS IS LOAD-BEARING, not style. A single
    `class BtcContextBlock(TypedDict, total=False)` makes EVERY key optional,
    `available` included, so the contract would permit a BTC block with no
    availability flag at all — the one shape no consumer could handle. That is
    what this declaration originally said, caught on 30 August by printing
    __required_keys__ and finding it empty rather than {"available"}.

    A schema that permits the one illegal shape is worse than none: it reads as
    a guarantee.
    """
    raw: str
    detailed: str
    regime: str
    volatility: str
    trend_health: float
    correlation: float
    correlation_label: str
    beta: float
    broad_market_stress: bool
    n_observations: int
    btc_adjusted_confidence: float
    reasons: List[str]


class DegradationBlock(TypedDict):
    """
    SEQUENCE ITEM 9a. What this analysis was computed without.

    `degraded` is False and `missing_inputs` empty on a normal run.
    `trading_authorized` is the ruling made structural: a degraded result does
    not by itself authorize trading, so it is False whenever `degraded` is True.

    It is a separate field rather than a flag on `risk` because it is a
    statement about the ANALYSIS, not about the trade — it stays true whether
    the action is LONG, WAIT or NO-TRADE, and a consumer asking "can I rely on
    this?" should not have to look inside a risk block to find out.
    """
    degraded: bool
    missing_inputs: List[str]
    trading_authorized: bool


class ProvenanceBlock(TypedDict):
    """
    SEQUENCE ITEM 12 (Item 5, Reproducibility). What the run actually saw.

    A stored decision without these cannot be checked against anything — it is
    a receipt rather than an audit trail. `engine_version` had been defined in
    config since the engine was built and written nowhere until this item.
    """
    engine_version: str
    last_candle: Any              # str, or None on an empty frame
    row_count: int
    source: str                   # the pinned directory, or the live endpoint


class DecisionObject(TypedDict):
    symbol: str
    timeframe: str
    macro_bias: str
    bias: BiasBlock
    trend: TrendBlock
    structure: StructureBlock
    entry: EntryBlock
    risk: RiskBlock
    exit: ExitBlock
    exit_watch: List[str]
    degradation: DegradationBlock          # sequence item 9a
    provenance: ProvenanceBlock            # sequence item 12
    decision_log_path: str                 # sequence item 12; "" if unwritten
    btc_context: BtcContextBlock
    explanation: ExplanationBlock
    chart_path: str


# ============================================================
# The engine output — Phase7Engine.run()
# ============================================================
#
# Deliberately looser than the decision object. engine_core hands the router
# whatever its stages produced; the router is what normalises types and applies
# defaults. Declaring engine_core's blocks field-by-field would duplicate the
# router's own coercion and force both to change together for no gain.
#
# What matters here is the SET OF TOP-LEVEL KEYS, because that is the seam a
# rename breaks: the router reads these ten by name.

class EngineOutput(TypedDict):
    symbol: str
    timeframe: str
    macro_bias: str
    bias: Dict[str, Any]
    trend: Dict[str, Any]
    structure: Dict[str, Any]
    entry: Dict[str, Any]
    risk: Dict[str, Any]
    exit: Dict[str, Any]
    exit_watch: List[str]
    degradation: List[str]                 # sequence item 9a: flat at this layer
    provenance: Dict[str, Any]             # sequence item 12
    btc_context: Dict[str, Any]
    chart_path: Any               # None when save_chart is False


# ============================================================
# The error shape
# ============================================================
#
# Both layers return this instead of their normal object when something fails,
# and every consumer's first act is to check for "error". It is a separate
# shape rather than an optional field on the others, because a decision object
# carrying an error is not a decision object with one key extra — it has none
# of the analysis blocks at all.

class ErrorObject(TypedDict):
    symbol: str
    timeframe: str
    error: str


ERROR_KEY = "error"


# ============================================================
# Alias resolution
# ============================================================
#
# Where the object carries two names for one value, this names the survivor.
#
# Empty as of sequence item 13: the two pairs it held — trend.health /
# trend.trend_health and trend.momentum / trend.momentum_mode — were removed
# rather than merely disambiguated. It is kept, empty, because the next
# unavoidable alias should be declared here rather than left implicit, and
# because tests/test_decision_contract.py checks that whatever it names really
# does hold identical values on a live run.

CANONICAL_ALIASES = {}


# ============================================================
# Fields whose removal is already scheduled
# ============================================================
#
# Fields that exist today and are already agreed to be leaving. Declared here
# so the contract test fails the moment they go, forcing this file to be
# updated in the same commit as the removal.
#
# Empty as of sequence item 13, which removed the five position-sizing fields
# it held. The mechanism did its job: the test fired on the first run of item
# 13 and this file was updated alongside the producers rather than after them.

SCHEDULED_FOR_REMOVAL = {}

```


=== FILE: core/decision_log.py ===

```python
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
    source          the pinned directory, or the live endpoint
    engine_version  from config, where it has been defined and written
                    nowhere since the engine was built
    config          the knobs that change the numbers

Given those five, a run can be repeated. Without them a stored decision cannot
be checked against anything — which is the difference between an audit trail
and a diary.

JSONL, one object per line: appendable without parsing what came before,
readable by anything, and it survives a partial write with only the last line
damaged. A CSV cannot hold a nested decision object without flattening it, and
flattening is where fields go missing quietly.

THE LINE THE PANEL PRINTS IS NOW CONDITIONAL

write() returns the path on success and None on failure, and the panel prints
the line only when it gets a path. An engine that says "logged" when the disk
was full would be the same defect wearing a new filename.
"""

import json
import os
from datetime import datetime, timezone

LOG_FILENAME = "phase7_decision_log_{symbol}.jsonl"

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


def log_path(log_dir, symbol):
    return os.path.join(log_dir, LOG_FILENAME.format(symbol=str(symbol).lower()))


def write(decision, config, log_dir=None):
    """
    Append one decision to the log. Returns the path written, or None.

    None on failure rather than raising: a decision that was computed correctly
    should still reach the operator if the disk is full. What must not happen
    is the panel claiming it was logged anyway — the caller passes this return
    value to the panel, which prints the line only when there is a path.
    """
    try:
        symbol = str(decision.get("symbol", "unknown"))
        # SEQUENCE ITEM 14: the else branch was
        # getattr(config, "LOG_DIR", "Logs/"). The explicit log_dir argument
        # stays — tests pass an unwritable path through it deliberately — but
        # the config read no longer carries a shadow default.
        log_dir = log_dir if log_dir is not None else config.LOG_DIR
        os.makedirs(log_dir, exist_ok=True)
        path = log_path(log_dir, symbol)

        record = {
            "logged_at": datetime.now(timezone.utc).isoformat(),
            "engine_version": config.engine_version,
            "config": config_snapshot(config),
            "decision": decision,
        }

        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, default=str) + "\n")
        return path

    except Exception:
        # Deliberately swallowed and reported as None. Logging is an audit
        # concern; failing to log must not destroy an analysis that succeeded,
        # and the caller's contract is "path or nothing".
        return None


def read(log_dir, symbol):
    """Every record for one symbol, oldest first. For tests and for reading back."""
    path = log_path(log_dir, symbol)
    if not os.path.exists(path):
        return []
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    # A torn final line from an interrupted write. Skipped
                    # rather than raised: one damaged record must not make the
                    # whole history unreadable.
                    continue
    return out

```


=== FILE: core/engine_core.py ===

```python
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
from models.btc_context import compute_correlation_beta, classify_correlation, classify_stress
from utils.plotting import plot_engine_chart

logger = logging.getLogger(__name__)


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

            # 1b. FETCH MACRO DATA (Multi-Timeframe Confluence)
            df_macro = data_fetcher.get_tf(symbol, macro_tf, limit=100)
            macro_bias = "NEUTRAL"

            if self._validate_dataframe(df_macro, required_base_cols, "macro timeframe data"):
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
                    logger.warning(f"Failed to process macro timeframe data: {e}")
                    macro_bias = "NEUTRAL"

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

                structure_regime = structure_obj.get("regime", "NEUTRAL STRUCTURE")
                trend_sequence = structure_obj.get("sequence", "NONE")
                volume_sentiment = structure_obj.get("volume_sentiment", "NEUTRAL VOLUME")
                # A6-adjacent FIX: swing_struct was computed by structure.py but never
                # extracted here, so it never made it into the decision object / panel.
                swing_struct = structure_obj.get("swing_struct", 0.0)

            except Exception as e:
                logger.error(f"Structure analysis failed: {e}")
                decision_object = {
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "error": f"Structure analysis failed: {str(e)}",
                }
                return decision_object

            # 4. TREND HEALTH ENGINE
            try:
                trend = compute_trend_health(df_struct)
                if not isinstance(trend, dict) or "trend_health" not in trend:
                    raise ValueError("Trend health engine returned invalid format")
                # SEQUENCE ITEM 9a: trend_health names the inputs it scored
                # without. Those are degradations of this run, not of that
                # module, so they join the same list.
                degradation.extend(trend.get("degraded_inputs", []))
            except Exception as e:
                logger.error(f"Trend health analysis failed: {e}")
                trend = {
                    "trend_health": 50.0,
                    "trend_exhaustion": False,
                    "momentum_mode": "NEUTRAL",
                    "momentum_divergence": False
                }

            # 5. BIAS ENGINE
            # Roadmap Layer 2: bias_engine.py's weighted blend now uses three
            # more factors that were already available here but never passed
            # through -- structure_regime, volume_sentiment, and macro_bias
            # (all computed above), plus SuperTrend direction (extracted here).
            supertrend_direction = float(df_struct["ST_Direction"].iloc[-1]) if "ST_Direction" in df_struct.columns else 0.0

            # SEQUENCE ITEM 6: the df=df_struct argument is gone. See
            # bias_engine.calculate_dynamic_bias — it never read the frame.
            raw_bias, bias_score = calculate_dynamic_bias(
                trend_sequence=trend_sequence,
                trend_health=trend["trend_health"],
                trend_exhaustion=trend["trend_exhaustion"],
                reversal_direction=trend.get("reversal_direction"),
                reversal_strength=trend.get("reversal_strength", 0),
                continuation_strength=trend.get("continuation_strength"),
                structure_regime=structure_regime,
                volume_sentiment=volume_sentiment,
                supertrend_direction=supertrend_direction,
                macro_bias=macro_bias,
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
            hvn = float(df_struct["HVN"].iloc[-1]) if "HVN" in df_struct.columns else float(structure_obj.get("hvn", 0.0))
            lvn = float(df_struct["LVN"].iloc[-1]) if "LVN" in df_struct.columns else float(structure_obj.get("lvn", 0.0))

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
                            "correlation": correlation,
                            "correlation_label": classify_correlation(correlation),
                            "beta": beta,
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

            entry_zone_lower = float(df_struct["EMA_20"].iloc[-1]) if "EMA_20" in df_struct.columns else float(df_struct["close"].iloc[-1] * 0.99)
            entry_zone_upper = float(df_struct["EMA_50"].iloc[-1]) if "EMA_50" in df_struct.columns else float(df_struct["close"].iloc[-1] * 1.01)

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
            }

            # 8. RISK MODEL & VALIDATION ENGINE
            current_price = float(df_struct["close"].iloc[-1])
            atr_val = float(df_struct["ATR"].iloc[-1]) if "ATR" in df_struct.columns else (current_price * 0.02)

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
            risk_valid, risk_reason = self.risk_model.validate_risk_parameters(
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

            macro_up = "BULLISH" in macro_bias.upper()
            macro_down = "BEARISH" in macro_bias.upper()
            bias_up = raw_bias == "BULLISH"
            bias_down = raw_bias == "BEARISH"

            if (macro_up and bias_up) or (macro_down and bias_down):
                val_score += 10
                val_notes.append("The higher timeframe agrees with this bias.")
            elif (macro_up and bias_down) or (macro_down and bias_up):
                val_score -= 20
                val_notes.append("The higher timeframe disagrees with this bias.")
            else:
                val_notes.append("The higher timeframe is neutral.")

            if "STRONG" in volume_sentiment.upper() or "EXPANSION" in volume_sentiment.upper():
                val_score += 15
                val_notes.append("Volume sentiment is supportive of current momentum.")
            elif "DIVERGENCE" in volume_sentiment.upper() or "WEAK" in volume_sentiment.upper():
                val_score -= 25
                val_notes.append("Volume divergence or weakness detected.")
            else:
                val_notes.append("Volume sentiment is neutral.")

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
                # SEQUENCE ITEM 13 — risk_score and signal_strength removed.
                # Both were assigned bias_score verbatim, making three names for
                # one number in a single object, and the third — bias.score — is
                # the one that says what it holds. Neither alias was read by any
                # consumer: panel_render.py bound risk_score to a local and then
                # printed validation_score and confidence_score instead. An
                # unread field with a misleading name is worse than no field,
                # because the next reader believes it.
                "confidence_score": trend["trend_health"],
                "trade_quality_current": trend["trend_health"],
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
                },
                "exit_watch": exit_watch,
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
```


=== FILE: core/panel_render.py ===

```python
import logging
import textwrap

logger = logging.getLogger(__name__)

# Viktor's terminal window can't comfortably show a line longer than this,
# and long lines were also triggering a display bug when he resized the
# window (that section of the panel disappearing). Every bulleted panel
# section (Decision Reasoning, Exit Watch, etc.) is wrapped to this width
# instead of ever printing one long line.
MAX_LINE_WIDTH = 125


def _wrap_bullets(items, empty_message):
    """
    Turns a list of strings into ' - ...' bulleted panel lines, wrapping
    any line that would exceed MAX_LINE_WIDTH onto multiple lines (indented
    so the wrapped text still reads as one bullet, not a new one).
    """
    if not items:
        items = [empty_message]

    out_lines = []
    for item in items:
        wrapped = textwrap.wrap(
            str(item),
            width=MAX_LINE_WIDTH,
            initial_indent=" - ",
            subsequent_indent="   ",
            break_long_words=False,
            break_on_hyphens=False,
        )
        out_lines.extend(wrapped if wrapped else [" - "])

    return "\n".join(out_lines) + "\n"

# Safe colorama import with fallback
try:
    from colorama import init, Fore, Style
    # Initialize colorama for Windows and cross-platform compatibility
    init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    logger.warning("Colorama not available, using plain text output")
    COLORAMA_AVAILABLE = False
    # Create dummy color classes for fallback
    class DummyColor:
        def __getattr__(self, name):
            return ""
    Fore = DummyColor()
    Style = DummyColor()


def render_panel(decision):
    """
    Renders a Phase7 decision object into an advanced, color-coded
    structured text terminal panel with comprehensive error handling.
    """
    try:
        # Validate input
        if not isinstance(decision, dict):
            error_msg = f"Invalid decision object type: {type(decision)}"
            logger.error(error_msg)
            print(f"\n[ERROR] {error_msg}")
            return None

        # Handle error state
        if "error" in decision:
            error_msg = decision['error']
            if COLORAMA_AVAILABLE:
                print(f"\n{Fore.RED}[ERROR] {error_msg}{Style.RESET_ALL}")
            else:
                print(f"\n[ERROR] {error_msg}")
            return None

    except Exception as e:
        logger.error(f"Failed to validate decision object: {e}")
        print(f"\n[ERROR] Failed to process decision object: {e}")
        return None

    try:
        # Basic metadata with safe extraction
        # SEQUENCE ITEM 12: the fallback was "AEROUSDT", so a decision object
        # with no symbol rendered as a confident AERO panel rather than as the
        # error it is.
        symbol = str(decision.get("symbol") or "UNKNOWN")
        timeframe = str(decision.get("timeframe", "4h"))
        macro_bias = str(decision.get("macro_bias", "NEUTRAL"))

        # Extract sections with safe defaults
        bias = decision.get("bias", {}) if isinstance(decision.get("bias"), dict) else {}
        trend = decision.get("trend", {}) if isinstance(decision.get("trend"), dict) else {}
        structure = decision.get("structure", {}) if isinstance(decision.get("structure"), dict) else {}
        entry = decision.get("entry", {}) if isinstance(decision.get("entry"), dict) else {}
        risk = decision.get("risk", {}) if isinstance(decision.get("risk"), dict) else {}
        exit_data = decision.get("exit", {}) if isinstance(decision.get("exit"), dict) else {}

        # Safe numeric extraction with error handling
        def safe_float(value, default=0.0):
            try:
                return float(value) if value is not None else default
            except (ValueError, TypeError):
                return default

        # Targets with safe extraction
        targets = risk.get("targets", (0, 0, 0))
        if isinstance(targets, (list, tuple)) and len(targets) >= 3:
            t1, t2, t3 = safe_float(targets[0]), safe_float(targets[1]), safe_float(targets[2])
        else:
            t1, t2, t3 = 0.0, 0.0, 0.0

        current_price = safe_float(exit_data.get("current_price", 0.0))
        stop_loss = safe_float(risk.get("atr_stop", 0.0))

        # SEQUENCE ITEM 13: this was called `risk_amount`, which is what
        # engine_core.py called a sum of money — an account balance times a
        # risk percentage. Here it is a price distance, and it is the
        # denominator of all three R:R ratios. One name, two unrelated
        # quantities, in an object that carried both.
        #
        # The money is gone under Viktor's ruling, so the collision is gone
        # with it; the name is corrected anyway, because the removal of one
        # side of a collision is the moment the other side gets renamed or
        # never does. Zero denominator still guarded.
        stop_distance = abs(current_price - stop_loss) if stop_loss and current_price else 0.0

        if stop_distance > 0:
            rr_t1 = abs(t1 - current_price) / stop_distance
            rr_t2 = abs(t2 - current_price) / stop_distance
            rr_t3 = abs(t3 - current_price) / stop_distance
        else:
            rr_t1 = rr_t2 = rr_t3 = 0.0

        # Formatted scores with safe conversion
        #
        # BUG FIX (found during the A3/A4/A5 pass): the VALIDATION line below
        # displayed risk_score — which engine_core.py set to bias_score — next
        # to the validation_state label, instead of the validation_score that
        # the STRONG/NEUTRAL/WEAK label was derived from. The label was always
        # right; only the number beside it was wrong. Before B1 existed
        # bias_score sat close to validation_score by coincidence, which is why
        # it went unnoticed.
        #
        # SEQUENCE ITEM 13: the `risk_score = ...` line that survived that fix
        # is gone too. After the fix nothing printed it, so the panel bound a
        # local and dropped it — and the comment claimed it was still used for
        # CONFIDENCE, which reads confidence_score. The field itself is removed
        # from the decision object; bias.score is where that number lives.
        validation_score = safe_float(risk.get('validation_score', 0))
        entry_score = safe_float(entry.get('score', 0))
        confidence_score = safe_float(risk.get('confidence_score', 0))
        tq_proposed = safe_float(risk.get('trade_quality_proposed', 0))
        trend_health_score = safe_float(trend.get('trend_health', 0))

        # C4 BUILD: position size and the standalone EV line were both
        # dropped from the panel per Viktor's request -- the underlying
        # numbers (including EV, which still appears inside Decision
        # Reasoning below) are still computed upstream in
        # engine_core.py/decision_model.py in case they're useful again
        # later, just no longer read/shown here as their own line.

    except Exception as e:
        logger.error(f"Failed to extract panel data: {e}")
        print(f"\n[ERROR] Failed to extract panel data: {e}")
        return None

    try:
        # Helper for color-coding text values with fallback
        def colorize_val(val):
            try:
                val_str = str(val).upper()
                if not COLORAMA_AVAILABLE:
                    return str(val)

                if "BULLISH" in val_str or "LONG" in val_str or "HEALTHY" in val_str or "STRONG" in val_str:
                    return f"{Fore.GREEN}{val}{Style.RESET_ALL}"
                elif "BEARISH" in val_str or "SHORT" in val_str or "WEAK" in val_str:
                    return f"{Fore.RED}{val}{Style.RESET_ALL}"
                elif "NEUTRAL" in val_str or "WAIT" in val_str or "NORMAL" in val_str:
                    return f"{Fore.YELLOW}{val}{Style.RESET_ALL}"
                return f"{Fore.CYAN}{val}{Style.RESET_ALL}"
            except Exception:
                return str(val)

        # ============================================================
        # SEQUENCE ITEM 12 — Items 5 and 6, the footer
        # ============================================================
        #
        # These two lines used to be unconditional:
        #
        #   f"Trade logged to Logs/phase7_trade_log_{symbol.lower()}.csv"
        #   f"AI Risk chart saved to {decision.get('chart_path', '...')}"
        #
        # The first named a file no code wrote — Item 6, rated Critical: the
        # engine asserting an audit action that did not occur, on every run.
        #
        # The second had a subtler version of the same fault. `.get` with a
        # default returns the DEFAULT only when the key is ABSENT; the router
        # always sets chart_path, and sets it to None when charting failed. So
        # a failed chart printed "AI Risk chart saved to None" — still a claim
        # that something was saved.
        #
        # Both now print only when the thing they describe actually happened,
        # and say so plainly when it did not.
        logged_to = decision.get("decision_log_path") or ""
        log_line = (
            f"Decision logged to {logged_to}\n" if logged_to
            else "Decision NOT logged — this run has no audit record.\n"
        )

        saved_chart = decision.get("chart_path") or ""
        chart_line = (
            f"Chart saved to {saved_chart}\n" if saved_chart
            else "No chart was produced for this run.\n"
        )

        # SEQUENCE ITEM 5b: this read used to be
        #     exit_data.get('action', exit_data.get('final_action', 'WAIT'))
        # The 'final_action' fallback existed for the raw engine object, whose
        # "exit" block was compute_exit's. engine_core no longer renders and
        # compute_exit is gone, so the only caller is signal_router, which
        # always supplies 'action'. A fallback that cannot fire is worse than
        # none: it implies the DECISION line has a second source when it has
        # one, and the one it named printed an exit verdict under a decision
        # heading.
        action_val = str(exit_data.get('action', 'WAIT'))

        # C1: Decision Reasoning trail. Built from decision["explanation"]["reasons"],
        # which comes from the exact same evaluation path signal_router.py used to
        # produce the DECISION shown above -- so this can never disagree with it.
        # Wrapped to MAX_LINE_WIDTH (see _wrap_bullets) so a long reason never
        # produces one unbroken line too wide for the terminal.
        explanation = decision.get("explanation", {}) if isinstance(decision.get("explanation"), dict) else {}
        explanation_reasons = explanation.get("reasons", [])
        reasoning_lines = _wrap_bullets(
            explanation_reasons if isinstance(explanation_reasons, list) else [],
            "No explanation available for this decision.",
        )

        # C3: Exit Watch advisory flags. Passed straight through from
        # signal_router.py / exit_model.py's build_exit_watch() -- see
        # that function's docstring for what feeds into this list. Same
        # line-wrapping treatment as Decision Reasoning above.
        exit_watch = decision.get("exit_watch", [])
        exit_watch_lines = _wrap_bullets(
            exit_watch if isinstance(exit_watch, list) else [],
            "No exit-watch flags are active right now.",
        )

        # BTC MARKET CONTEXT (new feature, V1): informational only, never
        # changes BIAS/DECISION/CONFIDENCE above. Falls back to a plain
        # one-line note if unavailable (e.g. BTC fetch failed this run, or
        # this run WAS analyzing BTCUSDT itself) -- that never affects the
        # rest of the panel.
        btc = decision.get("btc_context", {}) if isinstance(decision.get("btc_context"), dict) else {}
        btc_available = bool(btc.get("available", False))

        if COLORAMA_AVAILABLE:
            # SEQUENCE ITEM 5b: the green list also held "TARGET 1 HIT",
            # "TARGET 2 HIT" and "TARGET 3 HIT", and the red list held
            # "STOP LOSS HIT". Those four strings were only ever produced by
            # compute_exit, which the router discarded before the panel saw it,
            # so the comparisons could not match. action_val comes from
            # DecisionModel, whose full output is WAIT, NO-TRADE (RISK TOO
            # HIGH), LONG, AGGRESSIVE LONG, CONSERVATIVE LONG and the three
            # short equivalents.
            #
            # Note that bare "LONG" and "SHORT" are live — DecisionModel does
            # emit them (decision_model.py:150 and :172), alongside the
            # AGGRESSIVE/CONSERVATIVE variants which fall through to yellow.
            # Only the four HIT literals were dead; the conditions stay.
            if action_val in ["LONG"]:
                colored_action = f"{Fore.GREEN}{action_val}{Style.RESET_ALL}"
            elif action_val in ["SHORT"]:
                colored_action = f"{Fore.RED}{action_val}{Style.RESET_ALL}"
            else:
                colored_action = f"{Fore.YELLOW}{action_val}{Style.RESET_ALL}"
            # ANSI code for Orange text
            ORANGE = "\033[38;5;214m"
            c_cyan = Fore.CYAN
            c_magenta = Fore.MAGENTA
            c_green = Fore.GREEN
            c_red = Fore.RED
            dim = Style.DIM
            reset = Style.RESET_ALL
        else:
            colored_action = action_val
            ORANGE = ""
            c_cyan = ""
            c_magenta = ""
            c_green = ""
            c_red = ""
            dim = ""
            reset = ""

        # Constructing layout strings cleanly
        header_banner = f"\n{c_cyan}Connecting to MEXC API for {symbol} ({timeframe}) - Phase-7.3 Structural Quant Engine...{reset}\n\n" if COLORAMA_AVAILABLE else f"\nConnecting to MEXC API for {symbol} ({timeframe}) - Phase-7.3 Structural Quant Engine...\n\n"

        box_top = f"{c_magenta}=========================================================================\n" if COLORAMA_AVAILABLE else "=========================================================================\n"
        title_line = f"    PHASE-7 STRUCTURAL DYNAMIC ENTRY QUALITY ENGINE\n"
        box_mid = f"========================================================================={reset}\n\n" if COLORAMA_AVAILABLE else "=========================================================================\n\n"
        divider = f"{dim}-------------------------------------------------------------------------{reset}\n" if COLORAMA_AVAILABLE else "-------------------------------------------------------------------------\n"

        # BTC MARKET CONTEXT (new feature, V1) -- built as its own block
        # here so the conditional (available vs. not) stays readable,
        # rather than trying to branch inside the big f-string below.
        # Informational only: never changes BIAS/DECISION/CONFIDENCE above.
        if btc_available:
            btc_reasoning_lines = _wrap_bullets(
                btc.get("reasons", []) if isinstance(btc.get("reasons"), list) else [],
                "No additional notes.",
            )
            btc_section = (
                f"{divider}"
                f"BTC Market Context (informational only -- does not change BIAS or DECISION above):\n"
                f"BTC BIAS      : {colorize_val(btc.get('detailed', 'NEUTRAL'))}\n"
                f"BTC REGIME    : {colorize_val(btc.get('regime', 'NEUTRAL STRUCTURE'))} | "
                f"Vol: {colorize_val(btc.get('volatility', 'NORMAL'))}\n"
                f"CORRELATION   : {colorize_val(btc.get('correlation_label', 'WEAK / NO CLEAR RELATIONSHIP'))} "
                f"({safe_float(btc.get('correlation', 0.0)):+.2f}) over last {int(btc.get('n_observations', 0))} candles\n"
                f"BTC SENSITIVITY (beta): {safe_float(btc.get('beta', 0.0)):.2f}x\n"
                f"BROAD MARKET STRESS: {colorize_val('YES' if btc.get('broad_market_stress') else 'No')}\n"
                f"BTC-ADJUSTED CONFIDENCE: {safe_float(btc.get('btc_adjusted_confidence', 0.0)):.2f}/100 "
                f"(vs {confidence_score:.2f}/100 unadjusted)\n"
                # SEQUENCE ITEM 12, Item 7: this number is correctness-validated
                # — it computes what it was designed to compute — and
                # empirically unvalidated: nothing has tested whether adjusting
                # confidence by BTC correlation predicts anything. Item 7
                # requires that status be stated rather than implied away, and
                # a number on a panel implies it away by default.
                f"   (computationally validated, empirically unvalidated — no backtest supports this adjustment)\n"
                f"{btc_reasoning_lines}\n"
            )
        else:
            btc_section = (
                f"{divider}"
                f"BTC Market Context (informational only): unavailable this run -- AERO analysis above is unaffected.\n\n"
            )

        panel = (
            f"{header_banner}"
            f"{box_top}{title_line}{box_mid}"
            f"BIAS       : {colorize_val(bias.get('detailed', bias.get('raw', 'NEUTRAL')))}\n"
            f"REGIME     : {colorize_val(bias.get('regime', 'NEUTRAL STRUCTURE'))}\n"
            f"STRUCTURE  : {colorize_val(structure.get('regime', 'NEUTRAL'))} | Vol: {colorize_val(bias.get('volatility', 'NORMAL'))}\n"
            f"SEQUENCE   : {colorize_val(structure.get('sequence', 'NONE'))}\n"
            f"TREND      : {colorize_val(trend.get('trend_direction', 'NEUTRAL'))} / {colorize_val(trend.get('momentum_mode', 'HEALTHY'))} (Score: {trend_health_score:.2f})\n"
            # SEQUENCE ITEM 11: the number after the label was
            # trend_health_score — the same value the TREND line above already
            # shows. The LABEL (STRONG / BUILDING / EXTENDED) is momentum_mode,
            # a genuinely separate reading, so it stays.
            f"MOMENTUM   : {colorize_val(trend.get('momentum_mode', 'HEALTHY'))}\n"
            f"VOLUME     : {colorize_val(structure.get('volume_sentiment', 'WEAK OR CONTRARY VOLUME'))}\n"
            f"VALIDATION : {colorize_val(risk.get('validation_state', 'WEAK'))} (Score: {validation_score:.2f})\n"
            f"VOLATILITY : {colorize_val(bias.get('volatility', 'LOW'))}\n"
            f"MACRO TREND: {colorize_val(macro_bias)}\n\n"
            f"{divider}"
            f"CURRENT PRICE : {ORANGE}${current_price:.4f}{reset}\n"
            f"ENTRY ZONE    : {c_cyan}${safe_float(entry.get('zone_lower', 0)):.4f} - ${safe_float(entry.get('zone_upper', 0)):.4f}{reset}\n"
            f"ZONE DISTANCE : {safe_float(entry.get('distance_from_zone', 0.0)):.2f}% away from zone\n"
            f"STATUS        : {colorize_val(entry.get('entry_status', 'ACTIVE ENTRY ZONE'))}\n"
            f"SWING STRUCT  : ${safe_float(structure.get('swing_struct', current_price)):.4f} (Lookback 8)\n"
            f"STOP LOSS     : {c_red}${stop_loss:.4f}{reset}\n"
            f"TARGET 1 (Cons): {c_green}${t1:.4f}{reset} | R:R 1 : {rr_t1:.2f}\n"
            f"TARGET 2 (Norm): {c_green}${t2:.4f}{reset} | R:R 1 : {rr_t2:.2f}\n"
            f"TARGET 3 (Aggr): {c_green}${t3:.4f}{reset} | R:R 1 : {rr_t3:.2f}\n\n"
            f"{divider}"
            f"ENTRY QUALITY : {entry_score:.2f}/100\n"
            f"    |-- EMA Zone Position : {safe_float(entry.get('ema_pos_pts', 22)):.0f}/30\n"
            f"    |-- ATR Distance      : {safe_float(entry.get('atr_dist_pts', 10)):.0f}/25\n"
            f"    |-- VWMA Distance     : {safe_float(entry.get('vwma_pts', 20)):.0f}/20\n"
            f"    |-- RSI Extension     : {safe_float(entry.get('rsi_pts', 15)):.0f}/15\n"
            f"    |-- Structure         : {safe_float(entry.get('struct_pts', 2)):.0f}/12\n\n"
            f"{divider}"
            f"CONFIDENCE (decision): {confidence_score:.2f}/100\n"
            f"TRADE QUALITY :\n"

            f"    |-- Proposed Entry    : {tq_proposed:.2f}/100\n\n"
            f"{box_top}"
            f"DECISION      : {colored_action}\n\n"
            f"{divider}"
            f"Decision Reasoning:\n"
            f"{reasoning_lines}\n"
            f"{divider}"
            f"Exit Watch (advisory only -- not automatic):\n"
            f"{exit_watch_lines}\n"
            f"{divider}"
            f"Validation Notes:\n"
            f" - {risk.get('validation_note', 'VWMA volume trend is pointing down.')}\n"
            f"{btc_section}"
            f"{box_top}\n"
            f"{log_line}"
            f"{chart_line}"
        )

        print(panel)
        return panel

    except Exception as e:
        logger.error(f"Failed to build or print panel: {e}")
        try:
            print(f"\n[ERROR] Panel rendering failed: {e}")
        except Exception:
            print("\n[ERROR] Critical panel rendering failure")
        return None
```


=== FILE: data/__init__.py ===

```python

```


=== FILE: data/data_fetcher.py ===

```python
import os

import pandas as pd
import requests
import time
from core import config
from data.validation import validate_ohlcv

# Environment variable naming a directory of pinned OHLCV CSVs. Checked at call
# time rather than import time, so it can be set after this module is loaded.
PINNED_ENV_VAR = "PHASE7_PINNED_DATA"

# Columns a pinned CSV must provide, in the shape fetch_ohlc() produces.
_OHLCV_COLUMNS = ["open", "high", "low", "close", "volume"]


class DataFetcher:
    """
    Phase‑7 Data Fetcher
    Supports:
        - Local CSV OHLC loading
        - MEXC API OHLC fetching
        - A pinned data source, for reproducible runs (sequence item 3)

    ------------------------------------------------------------------
    THE PINNED SOURCE
    ------------------------------------------------------------------
    Before this existed, get_tf() always went to the live API. That made the
    engine impossible to run twice on the same input, which in turn made most
    of the audit's Verification fields unsatisfiable: "change a knob, rerun,
    compare" cannot be done when every run sees different data.

    Point the fetcher at a directory of CSVs and every fetch is served from
    disk instead:

        set_pinned_source("tests/fixtures/pinned")     # programmatic
        PHASE7_PINNED_DATA=tests/fixtures/pinned       # or by environment

    Files are named {SYMBOL}_{TIMEFRAME}.csv — AEROUSDT_4h.csv,
    AEROUSDT_1d.csv, BTCUSDT_4h.csv. That covers all three series the engine
    fetches (base, macro, BTC context); pinning only the base series would
    leave two thirds of a run still depending on the network.

    TWO DELIBERATE CHOICES, both about failing loudly:

    1. A missing file under an active pinned source is an ERROR, never a
       silent fall-through to the live API. Falling back would reintroduce
       exactly the nondeterminism the pinned source exists to remove, and
       would do it invisibly.

    2. Nothing is cached between calls. Reading a 450-row CSV three times per
       run costs nothing, and handing the same DataFrame object to multiple
       callers was unsafe in this codebase specifically: four modules rewrote
       their caller's columns in place (T2-1). Closed at sequence item 6 —
       calculate_dynamic_bias no longer takes a frame at all, and
       calculate_structure, compute_volume_profile and plot_engine_chart each
       work on their own copy.

       The fresh copy per call stays regardless. It is the guarantee this class
       makes on its own terms rather than a workaround for someone else's bug,
       and it is what test_each_fetch_returns_an_independent_copy asserts.

    Precedence: an explicit set_pinned_source() call beats the environment
    variable, which beats the live API.
    """

    # Class-level, not instance-level, on purpose. engine_core imports the
    # module-scope `data_fetcher` singleton created at the bottom of this file,
    # but tests and callers may construct their own DataFetcher(). A class
    # attribute means every instance agrees on where data comes from.
    _pinned_dir = None

    def __init__(self):
        self.base_url = config.API_BASE_URL

    # ============================================================
    # PINNED SOURCE CONTROL
    # ============================================================

    @classmethod
    def set_pinned_source(cls, path):
        """Serve every subsequent fetch from CSVs in `path`."""
        if path is None:
            cls._pinned_dir = None
            return
        resolved = os.path.abspath(str(path))
        if not os.path.isdir(resolved):
            raise ValueError(
                f"pinned source directory does not exist: {resolved}"
            )
        cls._pinned_dir = resolved

    @classmethod
    def clear_pinned_source(cls):
        """Return to the live API. Does not clear the environment variable."""
        cls._pinned_dir = None

    @classmethod
    def pinned_source(cls):
        """
        The active pinned directory, or None if fetches go to the live API.

        Explicit set_pinned_source() wins; the environment variable is the
        fallback; otherwise live.
        """
        if cls._pinned_dir is not None:
            return cls._pinned_dir
        env = os.environ.get(PINNED_ENV_VAR)
        if env:
            resolved = os.path.abspath(env)
            if os.path.isdir(resolved):
                return resolved
        return None

    @staticmethod
    def pinned_filename(symbol, timeframe):
        """{SYMBOL}_{TIMEFRAME}.csv — symbol upper-cased, timeframe as given."""
        return f"{str(symbol).upper()}_{timeframe}.csv"

    def _load_pinned(self, directory, symbol, timeframe, limit):
        """
        Serve one series from the pinned directory.

        Returns a DataFrame shaped exactly as fetch_ohlc() returns one, or an
        {"error": ...} dict so get_tf()'s existing error path handles it
        unchanged.
        """
        path = os.path.join(directory, self.pinned_filename(symbol, timeframe))
        if not os.path.exists(path):
            return {"error": (
                f"pinned source active ({directory}) but no data for "
                f"{symbol} {timeframe} — expected "
                f"{self.pinned_filename(symbol, timeframe)}. Refusing to fall "
                f"back to the live API, which would make this run "
                f"irreproducible without saying so."
            )}

        try:
            df = self.load_csv(path, timeframe=timeframe)
        except Exception as e:
            return {"error": f"pinned data unreadable ({path}): {e}"}

        # SEQUENCE ITEM 8: checked here, before the reshape below. pandas does
        # not reliably carry .attrs through operations like the column
        # selection and astype that follow, so a later check could silently
        # find nothing wrong with a frame that is.
        #
        # No `now` is passed: a pinned file is historical by definition and
        # asserting it is current would reject the entire fixture set.
        problem = df.attrs.get("validation_error")
        if problem:
            return {"error": f"pinned data {path} failed validation: {problem}"}

        missing = [c for c in _OHLCV_COLUMNS if c not in df.columns]
        if missing:
            return {"error": (
                f"pinned data {path} is missing required columns: "
                f"{', '.join(missing)}"
            )}

        df = df[_OHLCV_COLUMNS].astype(float)

        # The API returns the most recent `limit` candles, so the pinned source
        # takes the tail to match. A pinned file shorter than `limit` is not an
        # error — it is simply all the history there is.
        if limit and len(df) > limit:
            df = df.iloc[-int(limit):]

        # A fresh copy per call. See the class docstring, choice 2.
        return df.copy()

    # ============================================================
    # LOCAL CSV LOADING
    # ============================================================

    def load_csv(self, filepath, timeframe=None, now=None):
        """
        Load OHLCV data from a CSV file.
        CSV must contain: timestamp, open, high, low, close, volume

        SEQUENCE ITEM 8: the loaded frame is validated against Item 3's defect
        classes, and any failure is recorded at `.attrs["validation_error"]`.

        Annotate rather than raise, for two reasons. The frame is still wanted
        by callers that want to look at what is wrong with it — the tests do
        exactly that. And every caller in the engine already has an error
        channel; _load_pinned turns this attribute into an {"error": ...} dict,
        get_tf turns that into .attrs["fetch_error"], and engine_core surfaces
        it. Raising here would mean unwinding all of that for no gain.

        The consequence to be aware of: an attribute is easy to ignore, and
        pandas does not reliably propagate .attrs through operations. Anything
        reading a frame from this method must check the attribute BEFORE
        reshaping it. _load_pinned does, immediately.

        `now` defaults to None, so a plain load makes no claim that the file is
        current and the staleness check does not run. See validation.py.
        """

        df = pd.read_csv(filepath)

        # Convert timestamp → datetime index
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            df.set_index("timestamp", inplace=True)

        problem = validate_ohlcv(df, timeframe=timeframe, now=now)
        if problem:
            df.attrs["validation_error"] = problem

        return df

    # ============================================================
    # MEXC API OHLC FETCHER
    # ============================================================

    def fetch_ohlc(self, symbol, timeframe, limit=300):
        """
        Fetch OHLCV candles from MEXC API.
        MEXC returns **8 fields**, not 12.
        """

        url = f"{self.base_url}/api/v3/klines"
        params = {
            "symbol": symbol,
            "interval": timeframe,
            "limit": limit
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        except Exception as e:
            return {"error": f"API request failed: {e}"}

        if not isinstance(data, list) or len(data) == 0:
            return {"error": "Empty or invalid API response."}

        # ============================================================
        # CORRECT MEXC FORMAT (8 fields)
        # ============================================================

        df = pd.DataFrame(data, columns=[
            "timestamp",        # open time (ms)
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",       # close time (ms)
            "quote_volume"
        ])

        # Keep only OHLCV
        df = df[["timestamp", "open", "high", "low", "close", "volume"]]

        # Convert types
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df["open"] = df["open"].astype(float)
        df["high"] = df["high"].astype(float)
        df["low"] = df["low"].astype(float)
        df["close"] = df["close"].astype(float)
        df["volume"] = df["volume"].astype(float)

        df.set_index("timestamp", inplace=True)

        # SEQUENCE ITEM 8: live data is validated too, and this is the one
        # path that DOES claim to be current — so it is the one that passes a
        # reference time and can therefore fail the staleness check.
        #
        # Item 3 lists "malformed API responses" alongside the data defects.
        # The shape checks above catch a response with the wrong number of
        # fields; this catches one that is correctly shaped and wrong, which is
        # the harder case and the one that reaches analysis.
        # MEXC timestamps are UTC epoch ms, so the reference must be UTC too.
        # Timestamp.now(tz="UTC") rather than the deprecated utcnow().
        problem = validate_ohlcv(df, timeframe=timeframe,
                                 now=pd.Timestamp.now(tz="UTC").tz_localize(None))
        if problem:
            return {"error": f"API data for {symbol} {timeframe} failed validation: {problem}"}

        return df

    # ============================================================
    # UNIFIED FETCH WRAPPER
    # ============================================================

    def get_tf(self, symbol, timeframe, limit=300):
        """
        Unified fetch wrapper used by the engine.

        A13 FIX: previously, any API failure silently returned an empty
        DataFrame with only a logger warning upstream — indistinguishable
        from a genuine "no signal" / insufficient-history condition once it
        reached engine_core.py. A real data outage would look identical to
        a normal HOLD in the panel, with no visibility into what actually
        happened.

        Now the failure reason is attached to the empty DataFrame via
        `.attrs["fetch_error"]` so engine_core.py can surface a distinct
        "data fetch failed" error state instead of the generic
        "insufficient market data" message. The return type is unchanged
        (still always a DataFrame) so nothing else calling get_tf() breaks.

        SEQUENCE ITEM 3: when a pinned source is active, data is served from
        disk instead of the API. The error handling below is shared — a
        missing pinned file surfaces through exactly the same
        `.attrs["fetch_error"]` path as an API failure, so engine_core needs
        no changes to report it.
        """

        pinned_dir = self.pinned_source()
        if pinned_dir:
            df = self._load_pinned(pinned_dir, symbol, timeframe, limit)
        else:
            df = self.fetch_ohlc(symbol, timeframe, limit)

        # If API returned an error dict, surface it as a distinct,
        # identifiable error state rather than falling through as an
        # ordinary empty-data path.
        if isinstance(df, dict) and "error" in df:
            empty_df = pd.DataFrame()
            empty_df.attrs["fetch_error"] = df["error"]
            return empty_df

        return df


# ============================================================
# GLOBAL FETCHER INSTANCE
# ============================================================

data_fetcher = DataFetcher()
```


=== FILE: data/validation.py ===

```python
"""
Item 3 — Data Integrity. Sequence item 8, the first Critical.

The invariant names its defect classes by hand:

    "Missing candles, duplicated candles, impossible prices, timestamp
     inconsistencies, NaN/Inf values, stale data, malformed API responses,
     and abnormal volume must be detected before they become analysis."

Before this module, nothing detected any of the first six. What existed instead
was ffill/bfill, which fills the defect in and carries on — so the engine could
not distinguish "no defect found" from "defect fabricated away". Every one of
the eight test_data_integrity fixtures was accepted without complaint.

REJECT, NOT DEGRADE — AND WHY THAT IS NOT A CONTRADICTION

Viktor's ruling of 29 August says that when an INDICATOR fails, the engine
continues in an explicitly degraded state rather than halting. That ruling
governs sequence item 9 and it is not in tension with this module.

The difference is what is being salvaged. A failed indicator leaves the rest of
the analysis standing: bias, structure and volume are still real measurements,
and a decision built on fewer of them can be reported honestly as such. A
negative price is not a measurement at all. There is no partial analysis of
impossible data to degrade to, and "degrading" would mean deciding which
fabricated number to substitute — the exact behaviour Item 3 exists to stop.

So: defective input is rejected before analysis. Defective analysis, once the
input is sound, is item 9's problem.

STALENESS TAKES AN EXPLICIT REFERENCE TIME

`now` is a parameter, and when it is omitted the staleness check does not run.

A CSV on disk is not stale — it is historical. What would be stale is treating
it as current. So the module refuses to guess: fetch_ohlc passes the wall clock,
because a live feed that claims to be current must be, and a file load asserts
every other invariant while making no currency claim.

This is also the only rule that could be satisfied durably. The clean fixture
this suite validates against spans 2025-01-01 to 2025-03-16 — 531 days old as of
30 August 2026 — and the corrupted "stale" fixture is the same data shifted back
another 730 days. A wall-clock threshold separating them has to sit between 531
and 1261 days, and the clean fixture's age grows by one every day. Any constant
chosen there is a magic number with an expiry date.

Ruled by Viktor, 30 August 2026.

WHAT IS DELIBERATELY NOT CHECKED

**Abnormal volume.** The invariant lists it, and this module checks only that
volume is finite and non-negative. A volume spike is not corruption — it is
frequently the most informative bar in the series, and rejecting runs because
the market got busy would make the engine least available exactly when it
matters. Detecting "abnormal" would require a model of normal, which is analysis
rather than validation, and belongs downstream of this file if it belongs
anywhere. Recorded here so item 16's re-audit sees a decision rather than an
omission.

**Row count.** engine_core._validate_dataframe already requires 20 rows and
reports its own message. Duplicating it here would mean two thresholds to keep
in agreement.
"""

import math

import numpy as np
import pandas as pd

OHLCV = ["open", "high", "low", "close", "volume"]

# How many bars past the last candle before a series claiming to be current is
# not. Three is deliberately loose: an exchange can be a bar behind at a
# boundary, and a validator that cries wolf on a routine lag gets disabled.
STALE_AFTER_BARS = 3

# Minutes per candle, for the interval and staleness checks. Anything not
# listed here is not validated for spacing rather than guessed at — see
# _interval_minutes.
TIMEFRAME_MINUTES = {
    "1m": 1, "3m": 3, "5m": 5, "15m": 15, "30m": 30,
    "1h": 60, "2h": 120, "4h": 240, "6h": 360, "8h": 480, "12h": 720,
    "1d": 1440, "3d": 4320, "1w": 10080,
}


def _interval_minutes(timeframe):
    """None when the timeframe is unknown, which disables spacing checks."""
    if not timeframe:
        return None
    return TIMEFRAME_MINUTES.get(str(timeframe).lower())


def _timestamps(df):
    """
    The series' time axis, whichever form it is in.

    load_csv sets a DatetimeIndex; fetch_ohlc does too; a frame read straight
    from disk has a `timestamp` column of epoch milliseconds. All three reach
    this module, so all three are handled rather than one being assumed.
    """
    if isinstance(df.index, pd.DatetimeIndex):
        return pd.Series(df.index)
    if "timestamp" in df.columns:
        col = df["timestamp"]
        if pd.api.types.is_datetime64_any_dtype(col):
            return pd.Series(col.to_numpy())
        try:
            return pd.Series(pd.to_datetime(col, unit="ms"))
        except Exception:
            return None
    return None


def validate_ohlcv(df, timeframe=None, now=None):
    """
    Return a one-line reason the frame must not become analysis, or None.

    A string rather than an exception: every caller here already has an error
    channel — _load_pinned returns {"error": ...}, get_tf converts that to
    .attrs["fetch_error"], and engine_core surfaces it as a distinct failure
    state. Raising would mean unwinding all of that.

    Args:
        df:         the frame to check
        timeframe:  e.g. "4h". Enables the spacing and staleness checks;
                    without it, both are skipped rather than guessed.
        now:        reference time for staleness. Omitted means the caller
                    makes no claim that this data is current, and the check
                    does not run. See the module docstring.
    """
    if df is None:
        return "no data: the frame is None"
    if not isinstance(df, pd.DataFrame):
        return f"malformed data: expected a DataFrame, got {type(df).__name__}"
    if df.empty:
        return "no data: the frame is empty"

    missing = [c for c in OHLCV if c not in df.columns]
    if missing:
        return f"malformed data: missing required columns {', '.join(missing)}"

    # --- values must be numbers, and real ones ---------------------------
    for col in OHLCV:
        series = pd.to_numeric(df[col], errors="coerce")

        n_nan = int(series.isna().sum())
        if n_nan:
            first = df.index[series.isna().to_numpy().argmax()]
            return (f"{n_nan} NaN or non-numeric value(s) in '{col}', first at "
                    f"{first}. Filling these would make a fabricated value "
                    f"indistinguishable from a measurement.")

        n_inf = int(np.isinf(series.to_numpy()).sum())
        if n_inf:
            return f"{n_inf} infinite value(s) in '{col}'"

    prices = df[["open", "high", "low", "close"]].apply(pd.to_numeric, errors="coerce")
    volume = pd.to_numeric(df["volume"], errors="coerce")

    nonpositive = (prices <= 0).to_numpy().sum()
    if nonpositive:
        col = prices.columns[(prices <= 0).any().to_numpy().argmax()]
        worst = float(prices[col].min())
        return (f"{int(nonpositive)} non-positive price(s); lowest is "
                f"{worst} in '{col}'. A price of zero or less is not a "
                f"measurement error, it is not a price.")

    if (volume < 0).any():
        return f"negative volume; lowest is {float(volume.min())}"

    # --- candles must be internally possible -----------------------------
    #
    # Three ways a candle can be impossible, not one. high < low is the obvious
    # case; a high below the open or close, or a low above them, is the same
    # defect wearing a different shape and would survive a check that only
    # compared high against low.
    body_max = prices[["open", "close"]].max(axis=1)
    body_min = prices[["open", "close"]].min(axis=1)
    impossible = (prices["high"] < prices["low"]) | \
                 (prices["high"] < body_max) | \
                 (prices["low"] > body_min)
    n_bad = int(impossible.sum())
    if n_bad:
        i = int(impossible.to_numpy().argmax())
        row = prices.iloc[i]
        return (f"{n_bad} impossible candle(s); first at index {i}: "
                f"open={row['open']}, high={row['high']}, low={row['low']}, "
                f"close={row['close']}. The high must be the highest of the "
                f"four and the low the lowest.")

    # --- the time axis ---------------------------------------------------
    ts = _timestamps(df)
    if ts is None:
        # No time axis at all. Not an error by itself — some callers hand over
        # a positionally-indexed frame — but nothing below can be checked.
        return None

    n_dupes = int(ts.duplicated().sum())
    if n_dupes:
        first = ts[ts.duplicated(keep=False)].iloc[0]
        return (f"{n_dupes} duplicated timestamp(s), first at {first}. "
                f"A repeated candle double-counts one bar of history in every "
                f"rolling window that crosses it.")

    if not ts.is_monotonic_increasing:
        i = int((ts.diff() < pd.Timedelta(0)).to_numpy().argmax())
        return (f"timestamps are not in increasing order; index {i} "
                f"({ts.iloc[i]}) is earlier than the row before it. Every "
                f"indicator here assumes time runs forwards.")

    minutes = _interval_minutes(timeframe)
    if minutes is None:
        return None                       # spacing and staleness need the bar size

    expected = pd.Timedelta(minutes=minutes)

    if len(ts) > 1:
        gaps = ts.diff().dropna()
        wrong = gaps[gaps != expected]
        if len(wrong):
            i = int(gaps.to_numpy().__ne__(expected.to_timedelta64()).argmax()) + 1
            return (f"{len(wrong)} irregular interval(s) for a {timeframe} "
                    f"series; first at index {i}, gap of {wrong.iloc[0]} where "
                    f"{expected} was expected. A missing candle silently "
                    f"shortens every rolling window that spans it.")

    # --- currency, only if the caller claims it --------------------------
    if now is not None:
        now_ts = pd.Timestamp(now)
        if now_ts.tzinfo is not None:
            now_ts = now_ts.tz_localize(None)
        age = now_ts - ts.iloc[-1]
        limit = expected * STALE_AFTER_BARS
        if age > limit:
            return (f"stale data: the last candle is {ts.iloc[-1]}, which is "
                    f"{age} old against a {timeframe} bar. The engine would "
                    f"analyse it and present the result with no indication "
                    f"that the market has moved since.")

    return None


def is_valid(df, timeframe=None, now=None):
    """Convenience wrapper for callers that want a boolean."""
    return validate_ohlcv(df, timeframe=timeframe, now=now) is None

```


=== FILE: indicators/__init__.py ===

```python

```


=== FILE: indicators/indicators.py ===

```python
from typing import NamedTuple

import pandas as pd
import numpy as np
import pandas_ta as ta

from core import config


class IndicatorFailure(NamedTuple):
    """
    One indicator that could not be computed, and what the engine loses by it.

    SEQUENCE ITEM 9a. `consequence` is written for the person reading the
    panel, not for the person reading the traceback: "trend health is computed
    without ADX" tells an operator what to distrust, where
    "ta.adx returned None" does not.
    """
    indicator: str
    reason: str
    consequence: str

    def __str__(self):
        return f"{self.indicator}: {self.reason} — {self.consequence}"

def clean_series(series: pd.Series, method: str = "forward_fill", fallback_value: float = None) -> pd.Series:
    """
    Clean a series by handling inf and extreme values, and filling gaps FORWARD.

    SEQUENCE ITEM 15 — Item 2 (No Future Information / Look-Ahead Bias) and the
    remainder of item 9a.

    THIS FUNCTION DID TWO THINGS IT DID NOT SAY IT DID

    (1) `method="forward_fill"` ran `.ffill().bfill()`. Every caller asked for a
    forward fill and got a backward one too. `ffill` covers every gap after the
    first valid value, so `bfill` only ever fired on the leading edge — the
    warm-up rows of an indicator, filled with the first value that indicator
    ever produced, which lies in their future.

    In the engine as it stands that cannot reach a decision: the analysis is
    made at the last bar of a 450-row frame and the contaminated rows are four
    hundred bars behind every window. It is a latent leak, not a live one. But
    Item 2 says "information unavailable at the exact decision timestamp must
    never influence that decision", and the Constitution's own note on
    backtesting says Item 2 "deserves the most explicit, deliberate checking of
    any invariant in this document once that work starts, since a backtest with
    a hidden look-ahead leak is the single most common way a system convinces
    itself it works when it doesn't." A backtest walks the decision timestamp
    backwards. On the day that harness is written, every one of these fills
    becomes a live leak, silently, with no code change to blame.

    (2) The final sweep — `fillna(median or 0.0)` — was a fabrication of the
    exact kind item 9a was written to remove, one layer below where item 9a
    looked.

    It mattered more than the backfill. An indicator that came back entirely
    NaN left this function as a column of ZEROS, and the callers' guards read

        rsi = clean_series(ta.rsi(...))
        if rsi is None or rsi.isna().all():   # can never be true
            raise ValueError("pandas_ta returned no usable RSI")

    `isna().all()` was already false, because this function had replaced every
    NaN with 0.0 before the check ran. So a completely failed RSI became RSI=0
    on every bar — maximum oversold — with no failure reported. A completely
    failed ATR became ATR=0, which is a stop distance of zero and three targets
    on top of the entry price. Item 9a's tests injected failures by raising, so
    the returns-nothing path was never exercised and the guards were never
    watched to see whether they could fire.

    WHAT IT DOES NOW

    Forward only, and NaN is a legitimate return value. A series that is all
    NaN comes back all NaN, so the caller's guard means what it says. Leading
    NaNs stay NaN, because a 14-period RSI genuinely has no value at bar 3 and
    inventing one is the leak.

    Args:
        series: Input series to clean
        method: 'forward_fill', 'interpolate', 'drop', or 'fill_value'
        fallback_value: Value to use when method='fill_value' — the one
            explicit substitution left, and the caller has to ask for it by
            name and supply the number itself.

    Returns:
        Cleaned series. May contain NaN. That is the point.
    """
    if series is None or series.empty:
        return series

    # Replace inf values with NaN
    series = series.replace([np.inf, -np.inf], np.nan)

    # Handle extreme outliers (beyond 5 standard deviations)
    if len(series.dropna()) > 10:
        mean_val = series.mean()
        std_val = series.std()
        if np.isfinite(mean_val) and np.isfinite(std_val) and std_val > 0:
            outlier_mask = np.abs(series - mean_val) > (5 * std_val)
            series.loc[outlier_mask] = np.nan

    # Apply cleaning method. SEQUENCE ITEM 15: `.bfill()` removed from the
    # forward_fill branch and limit_direction changed from 'both' to 'forward'.
    # Both filled from later rows; see the docstring.
    if method == "forward_fill":
        series = series.ffill()
    elif method == "interpolate":
        series = series.interpolate(method='linear', limit_direction='forward')
    elif method == "fill_value" and fallback_value is not None:
        series = series.fillna(fallback_value)
    elif method == "drop":
        series = series.dropna()

    # SEQUENCE ITEM 15: the final sweep lived here.
    #
    #     if series.isna().any():
    #         median_val = series.median()
    #         series = series.fillna(median_val if isfinite(median_val) else 0.0)
    #
    # It is gone. A median is a plausible number and that is precisely what
    # makes it dangerous — the reader cannot distinguish it from a measurement.
    # An all-NaN input took the `else 0.0` branch and came back as a column of
    # zeros, which is what silenced three of item 9a's guards.
    return series

def pct_slope(series: pd.Series) -> pd.Series:
    """Return the normalized percentage slope of a series with NaN handling."""
    if series is None or len(series) < 2:
        return pd.Series(dtype=float, index=series.index if series is not None else [])

    # Clean input series first
    series = clean_series(series, method="forward_fill")

    # Calculate slope with zero division protection
    prev_values = series.shift(1)
    slope = (series.diff() / prev_values) * 100

    # Handle division by zero cases
    slope = slope.replace([np.inf, -np.inf], 0.0)

    return clean_series(slope, method="forward_fill")


def add_technical_indicators(df: pd.DataFrame, inplace: bool = False):
    """
    Add the core technical indicators, and report anything that could not be
    computed instead of inventing a value for it.

    Returns:
        (df, failures) — the frame, and a list of IndicatorFailure records.
        An empty list means every indicator was computed from real data.

    SEQUENCE ITEM 9a. Item 13 (Fail Safely) and Item 8 (Epistemic Honesty),
    which the audit reported separately and which are one defect.

    WHAT THIS USED TO DO

    Every indicator here had an `except` that substituted a constant:

        RSI          50.0     the exact centre of the scale — "no opinion",
                              which is a reading, not the absence of one
        ADX          25.0     the conventional trend/no-trend boundary
        ATR          close × 0.02
        SuperTrend   close
        ST_Direction 1.0      bullish
        EMA_20/50    an ewm() fallback, which is a real computation

    Every one of those is a number the engine then treated as a measurement.
    Nothing downstream could tell a fabricated 50.0 from a market that really
    is at RSI 50, and the panel printed both identically.

    ST_Direction = 1.0 is the sharpest case: a failed SuperTrend calculation
    reported *bullish*. Not neutral, not unknown — a direction, chosen by
    whoever wrote the fallback, presented as the market's.

    WHAT IT DOES NOW

    On failure the column is NOT WRITTEN and the failure is recorded. Two
    channels on purpose: the absent column means no fabricated value can be
    read by accident, and the record is the explicit signal the engine acts on.

    An absent column alone would have been quieter but not safer — Item 3's
    lesson is that a defect you cannot name is a defect you cannot report, and
    engine_core needs to tell the operator *which* indicator failed, not merely
    that something did.

    THE EMA FALLBACK IS KEPT, DELIBERATELY

    close.ewm(span=20).mean() is not a fabrication. It is the definition of an
    EMA, computed with pandas instead of pandas_ta, and it produces the same
    number. A fallback that recomputes the same quantity by another route is
    not the defect this item is about — substituting a constant for a
    measurement is. Recorded so the distinction is deliberate rather than an
    oversight.

    RUNS THAT DEGRADE DO NOT HALT

    Viktor ruled on 29 August that a failed indicator degrades rather than
    halts: the engine continues, records what failed, reduces confidence and
    trade quality accordingly, and a degraded result does not by itself
    authorize trading. That ruling went against both GLM's recommendation and
    Claude's instinct, which is why it was Viktor's to make.

    So this returns failures rather than raising. engine_core decides what a
    run missing ADX is still allowed to say.
    """

    if not inplace:
        df = df.copy()

    failures = []

    def failed(indicator, exc, consequence):
        failures.append(IndicatorFailure(
            indicator=indicator,
            reason=f"{type(exc).__name__}: {exc}",
            consequence=consequence,
        ))

    # Validate and clean input data (vectorized operations)
    required_cols = ["open", "high", "low", "close", "volume"]

    # Batch clean all columns at once to reduce overhead
    #
    # SEQUENCE ITEM 15: was `.ffill().bfill()`. Backfilling a price column
    # invents a bar out of the one after it. Forward only now.
    #
    # Worth knowing that this loop is close to unreachable for the NaN case:
    # data/validation.py rejects any NaN in an OHLCV column (validation.py:147)
    # and runs in data_fetcher before the frame gets here. It is kept as a
    # guard for callers that did not come through the fetcher, not deleted,
    # because the cost is one pass and the failure it guards against is a
    # fabricated price.
    for col in required_cols:
        if col in df.columns:
            # Use in-place operations where possible
            df[col] = df[col].replace([np.inf, -np.inf], np.nan)
            df[col] = df[col].ffill()

    # ============================================================
    # CORE INDICATORS WITH NaN PROTECTION (Optimized)
    # ============================================================

    # Pre-extract close prices to avoid repeated column access
    close_prices = df["close"]

    # Calculate EMAs with optimized fallback
    # The ewm() fallbacks below are NOT fabrications and are kept — see the
    # function docstring. They compute the same exponential moving average
    # pandas_ta would, using pandas directly.
    # SEQUENCE ITEM 14: the lengths were 20 and 50 literal, while
    # config.EMA_FAST and config.EMA_SLOW held 20 and 50 and were read by
    # nothing. The column NAMES stay literal on purpose — they are the
    # dataframe's contract with trend_health, entry_model and plotting, and a
    # column named from a config value cannot be looked up by anything that
    # does not also read that value.
    for length, name in ((config.EMA_FAST, "EMA_20"), (config.EMA_SLOW, "EMA_50")):
        try:
            ema = ta.ema(close_prices, length=length)
            # SEQUENCE ITEM 15: was ema.ffill().bfill(). An EMA's leading
            # NaNs are its warm-up and backfilling them stated a value the
            # average did not have yet.
            df[name] = ema.ffill() if ema.isna().any() else ema
        except Exception:
            try:
                df[name] = close_prices.ewm(span=length, adjust=False).mean()
            except Exception as e:
                failed(name, e,
                       "trend health loses its slope component and entry "
                       "quality cannot score EMA zone position")

    # SEQUENCE ITEM 9a: both paths used to end in fallback_value=50.0.
    #
    # The second path is a real RSI calculation, so it stays — like the EMA
    # fallback, it computes the same quantity by another route. What goes is
    # the constant underneath both: 50.0 is the exact centre of the scale, and
    # an oscillator pinned there reads as "perfectly balanced", which is a
    # measurement. A failed RSI is not balanced. It is absent.
    try:
        rsi = clean_series(ta.rsi(df["close"], length=config.RSI_LENGTH),
                           method="forward_fill")
        if rsi is None or rsi.isna().all():
            raise ValueError("pandas_ta returned no usable RSI")
        df["RSI"] = rsi
    except Exception as primary:
        try:
            delta = df["close"].diff()
            gain = delta.where(delta > 0, 0).rolling(window=config.RSI_LENGTH).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=config.RSI_LENGTH).mean()
            rs = gain / loss.replace(0, np.nan)
            rsi = clean_series(100 - (100 / (1 + rs)), method="forward_fill")
            if rsi.isna().all():
                raise ValueError("manual RSI produced no usable values")
            df["RSI"] = rsi
        except Exception as fallback:
            failed("RSI", fallback,
                   "entry quality scores RSI extension at 0 of 15, and trend "
                   f"health loses its momentum component (primary: {primary})")

    # SEQUENCE ITEM 5a: Bollinger Bands removed. BB_lower, BB_middle and
    # BB_upper were written on both the success and fallback paths and read
    # nowhere in the engine — verified by scanning every module for a read.
    # Item 16 (no unconsumed complexity): computing three columns per run that
    # nothing consumes is cost without benefit, and every fallback that writes
    # a fabricated value is one more path Item 13 would otherwise have to give
    # honest semantics to.
    #
    # config.BB_LENGTH and config.BB_STD were left unused by 5a and are
    # removed from config.py at sequence item 14.

    # ADX / DI with error handling
    try:
        adx_df = ta.adx(df["high"], df["low"], df["close"], length=config.ADX_LENGTH)
        if adx_df is not None and not adx_df.empty:
            # SEQUENCE ITEM 5a: DIP and DIM (the directional indicators at
            # columns 1 and 2) were written here and read nowhere. ADX itself
            # is consumed — trend_health and bias both read it — so the call
            # stays and only the two unread columns go.
            #
            # Note for anyone deleting by name: `DIM` is also colorama's
            # dim-text style, used at panel_render.py:1181 as `dim =
            # Style.DIM`. That is unrelated to this dataframe column and
            # removing it breaks the panel's formatting.
            adx = clean_series(adx_df.iloc[:, 0], method="forward_fill")

            # SEQUENCE ITEM 15: ADX had no all-NaN guard, unlike RSI, ATR and
            # SuperTrend. It did not need one while clean_series was quietly
            # turning an all-NaN column into zeros — nothing looked NaN, ever.
            # With that removed, a frame that comes back present but empty of
            # values has to be caught here or it reaches trend_health as a
            # column of NaN with no failure recorded. ADX 0 would have read as
            # "no trend at all", the opposite end of the scale from the 25.0
            # item 9a removed.
            if adx.isna().all():
                raise ValueError("ta.adx returned a frame with no usable values")
            df["ADX"] = adx
        else:
            raise ValueError("ta.adx returned an empty frame")
    except Exception as e:
        # SEQUENCE ITEM 9a: was pd.Series(25.0, index=df.index).
        #
        # 25 is the conventional line between "trending" and "not trending",
        # so a failed ADX did not merely invent a number — it invented the
        # single most ambiguous one, sitting exactly on the boundary that
        # trend_health and bias both test against.
        failed("ADX", e,
               "trend health loses its ADX component (25 of its 100 points) "
               "and bias cannot test trend strength")

    # SuperTrend with error handling
    # A9 FIX: This is now the single, canonical SuperTrend implementation for the
    # engine (pandas_ta-based). The previous standalone custom loop-based
    # implementation in supertrend.py was never imported/called anywhere in the
    # pipeline (main.py, engine_core.py, structure.py, plotting.py, or any other
    # module) — it was dead code that only posed a future collision risk on the
    # same "SuperTrend" / "ST_Direction" column names. It has been deleted.
    # Length/multiplier are pulled from config.py instead of being hardcoded,
    # so config.SUPERTREND_LENGTH / config.SUPERTREND_MULT actually control the
    # calculation. Sequence item 14 did the same for every other length in this
    # file — until then SuperTrend was the only indicator config could reach.
    try:
        st_df = ta.supertrend(
            df["high"], df["low"], df["close"],
            length=config.SUPERTREND_LENGTH,
            multiplier=config.SUPERTREND_MULT,
        )
        if st_df is not None and not st_df.empty:
            df["SuperTrend"] = clean_series(st_df.iloc[:, 0], method="forward_fill")
            direction = clean_series(st_df.iloc[:, 1], method="forward_fill")
            if direction.isna().all():
                raise ValueError("SuperTrend produced no usable direction")
            df["ST_Direction"] = direction
        else:
            raise ValueError("ta.supertrend returned an empty frame")
    except Exception as e:
        # SEQUENCE ITEM 9a: was df["SuperTrend"] = df["close"] and
        # df["ST_Direction"] = pd.Series(1.0, index=df.index).
        #
        # This is the sharpest of the fabrications. ST_Direction = 1.0 is
        # BULLISH. A failed SuperTrend calculation did not report "unknown" or
        # even "neutral" — it reported a direction, chosen by whoever wrote the
        # fallback, and the engine presented it as the market's.
        #
        # bias_engine reads supertrend_direction as one of its factors and
        # build_exit_watch compares it against the previous run to raise a
        # "SuperTrend flipped" flag. Both were being fed a constant.
        failed("SuperTrend", e,
               "bias loses its SuperTrend factor and Exit Watch cannot detect "
               "a SuperTrend flip against the previous run")

    # SEQUENCE ITEM 5a: Typical_Price removed — written once, read nowhere.
    # It is the classic (H+L+C)/3 input to VWAP and CCI, neither of which this
    # engine calculates.

    # ============================================================
    # SECONDARY INDICATORS WITH NaN PROTECTION
    # ============================================================

    # SEQUENCE ITEM 9a: the primary path's fallback_value was
    # df["close"].iloc[-1] * 0.02 — a flat 2% of the last price, asserted as
    # this market's volatility.
    #
    # ATR sets the stop distance and all three targets. A fabricated ATR does
    # not produce a wrong indicator reading; it produces a wrong risk plan,
    # with stop and targets placed by a constant that has nothing to do with
    # how this instrument actually moves.
    #
    # The manual true-range calculation stays: like the EMA and RSI fallbacks
    # it is the same quantity by another route, not a substitute for it.
    try:
        atr = clean_series(
            ta.atr(df["high"], df["low"], df["close"], length=config.ATR_LENGTH),
            method="forward_fill")
        if atr is None or atr.isna().all():
            raise ValueError("pandas_ta returned no usable ATR")
        df["ATR"] = atr
    except Exception as primary:
        try:
            tr1 = df["high"] - df["low"]
            tr2 = (df["high"] - df["close"].shift(1)).abs()
            tr3 = (df["low"] - df["close"].shift(1)).abs()
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1, skipna=True)
            atr = clean_series(tr.rolling(window=config.ATR_LENGTH).mean(),
                               method="forward_fill")
            if atr.isna().all():
                raise ValueError("manual true range produced no usable values")
            df["ATR"] = atr
        except Exception as fallback:
            failed("ATR", fallback,
                   "no stop distance and no targets can be computed — the "
                   f"entire risk plan is unavailable (primary: {primary})")

    # SEQUENCE ITEM 5a: KAMA removed. The column itself was read by exactly
    # one thing — the slope loop below, which produced KAMA_Slope, which
    # nothing read. A dead chain two links long: the only consumer of KAMA
    # existed to feed a consumer that did not exist.
    #
    # config.KAMA_LENGTH was left unused by 5a and is removed from config.py at
    # sequence item 14.

    # VWMA with optimized calculation (avoid intermediate Series creation)
    try:
        volume_col = df["volume"]
        # Use rolling operations directly without creating intermediate cleaned series
        volume_sum = volume_col.rolling(window=config.VWMA_LENGTH).sum()
        price_volume_sum = (close_prices * volume_col).rolling(
            window=config.VWMA_LENGTH).sum()

        # Vectorized calculation with safe division
        valid_mask = (volume_sum > 0) & np.isfinite(volume_sum) & np.isfinite(price_volume_sum)
        df["VWMA"] = np.where(valid_mask, price_volume_sum / volume_sum, close_prices)

        # SEQUENCE ITEM 15: this line was
        #
        #     df["VWMA"] = df["VWMA"].ffill().bfill().fillna(close_prices)
        #
        # and the `.fillna(close_prices)` is the identical fabrication item 9a
        # removed from the except branch eight lines below — where the comment
        # already explains why substituting close for VWMA "invented the most
        # favourable number available", a zero VWMA distance and a perfect 20
        # of 20 entry-quality points. Item 9a fixed the branch that raises and
        # left the one that quietly succeeds.
        #
        # Forward fill only, and no substitution. A VWMA that has no value has
        # no value.
        if df["VWMA"].isna().any():
            df["VWMA"] = df["VWMA"].ffill()
    except Exception as e:
        # SEQUENCE ITEM 9a: was df["VWMA"] = close_prices.
        #
        # entry_model scores how far price sits from VWMA, worth 20 of the 100
        # entry-quality points. Substituting close for VWMA makes that distance
        # exactly zero — a perfect score, awarded because the calculation
        # failed. The fabrication did not merely invent a number, it invented
        # the most favourable one available.
        failed("VWMA", e,
               "entry quality loses its VWMA distance component (20 of 100 "
               "points)")

    # ============================================================
    # SLOPES WITH OPTIMIZED CALCULATION
    # ============================================================

    # Batch calculate slopes to reduce function call overhead
    #
    # SEQUENCE ITEM 5a: was four columns; VWMA_Slope and KAMA_Slope were
    # produced here and read nowhere, and KAMA itself is now gone. The two
    # that remain are genuinely consumed — trend_health.py reads EMA20_Slope
    # at three places and EMA50_Slope at one, so this loop stays.
    #
    # VWMA is NOT removed: entry_model consumes it for distance scoring. Only
    # its slope was dead.
    slope_columns = ["EMA_20", "EMA_50"]
    slope_names = ["EMA20_Slope", "EMA50_Slope"]

    for col, slope_name in zip(slope_columns, slope_names):
        if col in df.columns:
            # Optimized slope calculation without function call overhead
            series = df[col]
            prev_values = series.shift(1)
            slope = ((series - prev_values) / prev_values * 100).replace([np.inf, -np.inf], 0.0)
            # SEQUENCE ITEM 15: was slope.ffill().bfill().fillna(0.0). Zero
            # is not a neutral filler for a slope — it is the specific claim
            # that the moving average is flat, and trend_health reads these at
            # four places to decide whether a trend is strengthening.
            df[slope_name] = slope.ffill()

    # ============================================================
    # FINAL SWEEP
    # ============================================================
    #
    # SEQUENCE ITEM 9a: this block used to be a second fabrication layer.
    # Any critical indicator that came out all-NaN was overwritten with the
    # same constants the except branches used — 50.0, 25.0, close, close × 0.02
    # — so even an indicator that failed *quietly*, without raising, ended up
    # as an invented number.
    #
    # It now drops the column and reports, which is the same treatment a raised
    # exception gets. An indicator that produced nothing but NaN did not
    # compute; how it failed to compute is not the operator's problem.
    critical_indicators = ["EMA_20", "EMA_50", "RSI", "ATR", "ADX"]
    for indicator in critical_indicators:
        if indicator in df.columns and df[indicator].isna().all():
            df.drop(columns=[indicator], inplace=True)
            failed(indicator,
                   ValueError("computed without raising, but every value is NaN"),
                   "silent failure — the calculation returned, and returned nothing")

    return df, failures
```


=== FILE: indicators/trend_health.py ===

```python
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional

def compute_trend_health(df: Optional[pd.DataFrame]) -> Dict[str, Any]:
    """
    Compute advanced trend health, slope, acceleration, failure,
    exhaustion, momentum divergence, continuation/reversal scoring,
    and trend regime classification.
    """
    # SEQUENCE ITEM 9a: trend_health was 50.0 here — the exact middle of the
    # scale, returned whenever this function could not run at all. "Moderately
    # healthy trend" is a reading. The absence of one is not, and 50.0 is the
    # value most likely to be mistaken for a measurement because it is the one
    # a real market can genuinely produce.
    #
    # 0.0 instead, paired with degraded_inputs below. Zero is the floor of the
    # scale rather than a plausible point on it, and the engine now blocks
    # trading on any run carrying degraded inputs — so the number cannot be
    # read as conviction the way 50.0 could.
    default_response = {
        "trend_health": 0.0,
        "degraded_inputs": ["trend health could not be computed at all"],
        "trend_exhaustion": False,
        "momentum_mode": "NEUTRAL",
        "trend_slope": 0.0,
        "trend_acceleration": 0.0,
        "momentum_divergence": False,
        "trend_regime": "NEUTRAL",
        # B1 additions — see sections 2b and 7 below.
        "continuation_strength": 0.0,
        "reversal_direction": "NONE",
        "reversal_strength": 0.0,
        # New: explicit trend direction label — see section 1b below.
        "trend_direction": "NEUTRAL",
    }

    if df is None or not isinstance(df, pd.DataFrame) or df.empty or len(df) < 20:
        return default_response

    try:
        # SEQUENCE ITEM 9a: these four extractions were the engine's second
        # fabrication layer. Where indicators.py substituted a constant when a
        # calculation failed, this substituted one when the column was missing
        # — ADX 25.0 (the trend/no-trend boundary), RSI 50.0 (dead centre),
        # both slopes 0.0 (a flat market).
        #
        # Since indicators.py now DROPS a column it could not compute rather
        # than inventing one, these `else` branches became the live path for
        # every indicator failure. Left alone they would have re-fabricated
        # exactly what item 9a removed, one module downstream.
        #
        # Missing now means missing: the value is None, the component it feeds
        # scores zero, and the input is named in degraded_inputs. Zero rather
        # than a midpoint because an unavailable component must lower
        # conviction, never hold it steady — that is what Viktor's ruling means
        # by "reduced accordingly".
        degraded_inputs = []

        def _read(column, label):
            if column not in df.columns:
                degraded_inputs.append(f"{label} (column absent)")
                return None
            try:
                value = float(df[column].iat[-1])
            except Exception:
                degraded_inputs.append(f"{label} (unreadable)")
                return None
            if not np.isfinite(value):
                degraded_inputs.append(f"{label} (not finite)")
                return None
            return value

        ema20_slope = _read("EMA20_Slope", "EMA20_Slope")
        ema50_slope = _read("EMA50_Slope", "EMA50_Slope")
        adx_val = _read("ADX", "ADX")
        rsi_val = _read("RSI", "RSI")

        # The slopes are the only inputs trend health itself is computed from,
        # so their absence is not a degraded score — it is no score. Reported
        # as such rather than as a flat market.
        if ema20_slope is None and ema50_slope is None:
            out = dict(default_response)
            out["degraded_inputs"] = degraded_inputs
            return out
        ema20_slope = 0.0 if ema20_slope is None else ema20_slope
        ema50_slope = 0.0 if ema50_slope is None else ema50_slope

        # ============================================================
        # 1. TREND SLOPE & ACCELERATION
        # ============================================================
        trend_slope = float((ema20_slope + ema50_slope) / 2.0)

        # Calculate acceleration (change in slope over the last 3 periods)
        trend_acceleration = 0.0
        if "EMA20_Slope" in df.columns and len(df) >= 4:
            prev_slope = float(df["EMA20_Slope"].iat[-4])
            if np.isfinite(prev_slope):
                trend_acceleration = float(ema20_slope - prev_slope)

        # ============================================================
        # 2. TREND HEALTH SCORE (0–100)
        # ============================================================
        normalized_slope = float(np.tanh(abs(trend_slope) * 100) * 45)
        slope_strength = min(normalized_slope, 45.0)

        # SEQUENCE ITEM 9a: the `else` branches here awarded 20.0 of 40 for a
        # missing ADX and 10.0 of 15 for a missing RSI — half marks for an
        # input that was never read. Trend health is the number the panel calls
        # TREND and that bias, confidence and trade quality all build on, so
        # half marks for absent data propagated into every score downstream.
        #
        # Zero now. An input that does not exist contributes nothing.
        adx_strength = 0.0 if adx_val is None else min(max(adx_val, 0.0) * 1.2, 40.0)

        if rsi_val is None:
            rsi_strength = 0.0
        elif 45.0 <= rsi_val <= 65.0:
            rsi_strength = 15.0
        elif 35.0 <= rsi_val < 45.0 or 65.0 < rsi_val <= 75.0:
            rsi_strength = 12.0
        elif 25.0 <= rsi_val < 35.0 or 75.0 < rsi_val <= 85.0:
            rsi_strength = 8.0
        else:
            rsi_strength = 5.0

        trend_health = float(slope_strength + adx_strength + rsi_strength)
        trend_health = max(0.0, min(100.0, trend_health))

        # ============================================================
        # 2b. CONTINUATION STRENGTH (B1)
        # Signed: positive = bullish continuation, negative = bearish
        # continuation, magnitude 0-100. This is what actually unblocks
        # A3 — bias_engine.calculate_dynamic_bias() gates BULLISH/BEARISH
        # on continuation_strength being non-None and > 0 / < 0, which was
        # permanently impossible while this field didn't exist.
        #
        # Direction comes from trend_slope's sign. Magnitude is built from:
        # trend health, ADX strength, whether RSI sits in a healthy
        # continuation zone for that direction (vs. overextended/weak),
        # and whether the trend is accelerating or decelerating in its own
        # direction (deceleration actively subtracts, not just "doesn't help").
        # ============================================================
        if trend_slope > 0:
            direction = 1
        elif trend_slope < 0:
            direction = -1
        else:
            direction = 0

        # ============================================================
        # 1b. TREND DIRECTION (new)
        # A plain BULLISH/BEARISH/NEUTRAL label, so the direction the EMAs
        # are actually sloping is available as its own field instead of
        # only being implied by trend_slope's sign or by momentum_mode
        # (which reflects RSI intensity, not direction -- a strong
        # downtrend and an early uptrend can both show a "BUILDING"
        # momentum_mode, for example). Uses the exact same sign-of-slope
        # test as continuation_strength above, so the two never disagree.
        # Informational only -- doesn't feed into or change trend_health,
        # bias, or any decision logic.
        # ============================================================
        if direction > 0:
            trend_direction = "BULLISH"
        elif direction < 0:
            trend_direction = "BEARISH"
        else:
            trend_direction = "NEUTRAL"

        if direction != 0:
            health_component = (trend_health / 100.0) * 40.0

            # SEQUENCE ITEM 9a: an unavailable input scores zero rather than
            # scoring from a substituted constant. continuation_strength is out
            # of 100; without ADX its ceiling is 75, without RSI 85, and
            # degraded_inputs says which. A lower score for a less complete
            # picture is the intended behaviour, not a side effect.
            if adx_val is None:
                adx_component = 0.0
            else:
                adx_component = (min(max(adx_val, 0.0), 50.0) / 50.0) * 25.0

            if rsi_val is None:
                momentum_component = 0.0
            elif direction > 0:
                if 50.0 <= rsi_val <= 75.0:
                    momentum_component = 15.0
                elif 40.0 <= rsi_val < 50.0 or 75.0 < rsi_val <= 85.0:
                    momentum_component = 8.0
                else:
                    momentum_component = 2.0
            else:
                if 25.0 <= rsi_val <= 50.0:
                    momentum_component = 15.0
                elif 15.0 <= rsi_val < 25.0 or 50.0 < rsi_val <= 60.0:
                    momentum_component = 8.0
                else:
                    momentum_component = 2.0

            accel_aligned = trend_acceleration * direction
            accel_magnitude = float(np.tanh(abs(accel_aligned) * 50.0) * 20.0)
            accel_component = accel_magnitude if accel_aligned >= 0 else -accel_magnitude

            raw_continuation = health_component + adx_component + momentum_component + accel_component
            continuation_strength = float(direction * max(0.0, min(100.0, raw_continuation)))
        else:
            continuation_strength = 0.0

        # ============================================================
        # 3. TREND FAILURE — REMOVED at sequence item 9c
        # ============================================================
        #
        # The block here read the last five values of the STRUCTURE column and
        # set trend_failure if any equalled "LH" or "LL".
        #
        # structure.py never writes those. It writes regime labels — "BULLISH
        # TREND", "BEARISH TREND", "NEUTRAL STRUCTURE" — so the comparison
        # could not match and trend_failure was False on every run this engine
        # has ever made.
        #
        # Four modules acted on it: entry_model blocked entries, bias_engine
        # halved the bias score, exit_model raised a watch flag, and the router
        # published it as trend.failure. All four have been removed with it.
        # In each case it sat beside a live signal (trend_exhaustion, a
        # reversal, a CHOCH against trend), so the deletion is output-invariant
        # — proven by the golden snapshot.
        #
        # WHY DELETED RATHER THAN WIRED. Viktor delegated the call; the
        # reasoning is recorded in claude/phase7-rulings.md and in the commit.
        # In short: the audit found a gate that never fires, not a
        # specification for one that should. Choosing when to block a trade is
        # a trading decision, and wiring it would produce a behaviour change
        # this project cannot yet evaluate — the golden baseline proves a
        # change is attributable, never that it is correct, and backtesting
        # sits behind the release gate.
        #
        # It remains available as a deliberate feature once there is something
        # to validate it against. This deletion does not foreclose it; it
        # declines to smuggle it in as a repair.

        # ============================================================
        # 4. TREND EXHAUSTION
        # ============================================================
        range_val = float(df["high"].iat[-1] - df["low"].iat[-1])
        range_prev = float(df["high"].iat[-2] - df["low"].iat[-2])
        range_expanding = bool(range_val > range_prev)

        # SEQUENCE ITEM 9a: both clauses tested adx_val against a threshold.
        # With ADX unavailable, neither can be evaluated — and asserting
        # "not exhausted" would be a claim, not an absence of one. The flag is
        # left False, which is its default, and ADX's absence is already named
        # in degraded_inputs so the panel can say the check did not run.
        if adx_val is None:
            trend_exhaustion = False
        else:
            weak_adx = bool(adx_val < 20.0)
            trend_exhaustion = bool(
                (range_expanding and weak_adx)
                or (trend_health < 35.0 and adx_val < 15.0)
            )

        # ============================================================
        # 5. MOMENTUM DIVERGENCE DETECTION
        # ============================================================
        momentum_divergence = False
        # B1: track which direction a detected divergence points, not just
        # a yes/no bool — needed by the reversal detection in section 7.
        divergence_direction = "NONE"
        if len(df) >= 10 and "RSI" in df.columns:
            price_higher_high = bool(df["close"].iat[-1] > df["close"].iat[-5])
            rsi_lower_high = bool(df["RSI"].iat[-1] < df["RSI"].iat[-5])

            price_lower_low = bool(df["close"].iat[-1] < df["close"].iat[-5])
            rsi_higher_low = bool(df["RSI"].iat[-1] > df["RSI"].iat[-5])

            if price_higher_high and rsi_lower_high:
                # Price making new highs while momentum weakens -> bearish divergence
                momentum_divergence = True
                divergence_direction = "BEARISH"
            elif price_lower_low and rsi_higher_low:
                # Price making new lows while momentum firms up -> bullish divergence
                momentum_divergence = True
                divergence_direction = "BULLISH"

        # ============================================================
        # 6. MOMENTUM MODE & REGIME CLASSIFICATION
        # ============================================================
        # SEQUENCE ITEM 9a: both classifications are labels the panel prints as
        # statements about the market — MOMENTUM: STRONG, REGIME: MODERATE
        # TREND. With their input missing there is nothing to classify, and any
        # label chosen would be an assertion the engine cannot support. So they
        # say so.
        if rsi_val is None:
            momentum_mode = "UNAVAILABLE"
        elif rsi_val < 40.0:
            momentum_mode = "BUILDING"
        elif rsi_val < 55.0:
            momentum_mode = "HEALTHY"
        elif rsi_val < 70.0:
            momentum_mode = "STRONG"
        elif rsi_val < 80.0:
            momentum_mode = "EXTENDED"
        else:
            momentum_mode = "EXTREME"

        if adx_val is None:
            # Without ADX only the divergence/exhaustion branch is decidable,
            # and "MODERATE TREND" as a default would be the old fabrication
            # wearing a label instead of a number.
            trend_regime = ("EXHAUSTING / DIVERGENT"
                            if (momentum_divergence or trend_exhaustion)
                            else "UNAVAILABLE")
        elif trend_health >= 75.0 and adx_val >= 25.0:
            trend_regime = "STRONG TREND"
        elif trend_acceleration > 0.0 and trend_health >= 50.0:
            trend_regime = "ACCELERATING"
        elif momentum_divergence or trend_exhaustion:
            trend_regime = "EXHAUSTING / DIVERGENT"
        elif adx_val < 20.0:
            trend_regime = "MEAN REVERTING / CHOP"
        else:
            trend_regime = "MODERATE TREND"

        # ============================================================
        # 7. REVERSAL DETECTION (B1)
        # reversal_direction is a label ("BULLISH" / "BEARISH" / "NONE");
        # reversal_strength is a 0-100 magnitude regardless of direction —
        # entry_model.py already treats reversal_strength > 0 as "block
        # entries", independent of which way the reversal points, so this
        # intentionally does NOT sign it.
        #
        # Built from momentum divergence (section 5) plus proximity to the
        # HVN structural level (real since A11 wired in compute_volume_profile
        # — previously this would've been measuring the wrong thing), gated
        # by whether the trend is actually extended/exhausting enough for a
        # reversal signal to mean anything.
        # ============================================================
        structural_direction = "NONE"
        structural_proximity_component = 0.0
        if "HVN" in df.columns:
            hvn_val = float(df["HVN"].iat[-1])
            current_close = float(df["close"].iat[-1])
            if np.isfinite(hvn_val) and current_close > 0:
                hvn_dist_pct = abs(current_close - hvn_val) / current_close * 100.0
                if hvn_dist_pct < 1.5:
                    structural_proximity_component = 20.0
                    structural_direction = "BEARISH" if current_close >= hvn_val else "BULLISH"
                elif hvn_dist_pct < 3.0:
                    structural_proximity_component = 10.0
                    structural_direction = "BEARISH" if current_close >= hvn_val else "BULLISH"

        reversal_direction = "NONE"
        reversal_strength = 0.0

        candidate_direction = divergence_direction if divergence_direction != "NONE" else structural_direction

        if candidate_direction != "NONE":
            divergence_bonus = 25.0 if momentum_divergence else 0.0
            exhaustion_bonus = 20.0 if trend_exhaustion else 0.0
            raw_reversal = divergence_bonus + structural_proximity_component + exhaustion_bonus

            # Reversal signals are only meaningful against an established,
            # extended trend -- scale down sharply if momentum isn't
            # actually extended/exhausted yet.
            if not (momentum_mode in ("EXTENDED", "EXTREME") or trend_exhaustion):
                raw_reversal *= 0.4

            reversal_strength = float(max(0.0, min(100.0, raw_reversal)))
            reversal_direction = candidate_direction if reversal_strength > 0 else "NONE"

        return {
            "trend_health": float(trend_health),
            # SEQUENCE ITEM 9a: names every input this score was computed
            # WITHOUT. Empty means the score used everything it claims to.
            "degraded_inputs": list(degraded_inputs),
            "trend_exhaustion": bool(trend_exhaustion),
            "momentum_mode": str(momentum_mode),
            "trend_slope": float(trend_slope),
            "trend_acceleration": float(trend_acceleration),
            "momentum_divergence": bool(momentum_divergence),
            "trend_regime": str(trend_regime),
            "continuation_strength": float(continuation_strength),
            "reversal_direction": str(reversal_direction),
            "reversal_strength": float(reversal_strength),
            "trend_direction": str(trend_direction),
        }

    except Exception as e:
        # SEQUENCE ITEM 9a: this used to return default_response and swallow
        # `e` entirely — the caller received trend_health 50.0 with no way to
        # know the computation had failed rather than found a middling market.
        # `e` was bound and never used, which is the tell.
        #
        # The payload now carries the reason, and trend_health is 0.0 rather
        # than 50.0, so a failure here reaches the panel as a failure.
        out = dict(default_response)
        out["degraded_inputs"] = [f"trend health raised {type(e).__name__}: {e}"]
        return out
```


=== FILE: indicators/volume_profile.py ===

```python
import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def compute_volume_profile(df: pd.DataFrame, num_bins: int = 50):
    """
    Compute a true binned price-volume profile using proportional
    candle overlap distribution with comprehensive error handling.

    Returns:
        profile (pd.Series): Volume per price bin
        hvn (float): High Volume Node (bin midpoint)
        lvn (float): Low Volume Node (bin midpoint)

    SEQUENCE ITEM 6: this function used to clean `low`, `high` and `volume`
    directly on the caller's frame — and the inf-replacement on the second line
    of that block ran on every call, not only when something was wrong. A
    function asked to compute a read-only summary was writing to its input every
    time it was invoked. It now works on its own copy.

    Not named in the Step 5 plan; found while fixing the two that were. Same
    class: modules mutating frames they don't own.

    NOT FIXED HERE: `fillna(0)` on `low` and `high` substitutes a price of zero
    for a missing one, which would put a fabricated candle at the bottom of the
    volume profile and drag HVN/LVN toward it. Latent — it cannot fire on data
    that has been through add_technical_indicators. Rider on sequence item 9
    with the other fabricated fallbacks.
    """

    try:
        if df is None:
            logger.error("DataFrame is None")
            return pd.Series(dtype=float, name="volume"), None, None

        if not isinstance(df, pd.DataFrame):
            logger.error("Input is not a pandas DataFrame")
            return pd.Series(dtype=float, name="volume"), None, None

        if df.empty:
            logger.warning("DataFrame is empty")
            return pd.Series(dtype=float, name="volume"), None, None

        required = {"low", "high", "volume"}
        missing = required - set(df.columns)
        if missing:
            logger.error(f"Missing required columns: {sorted(missing)}")
            return pd.Series(dtype=float, name="volume"), None, None

        if num_bins < 1:
            logger.error("num_bins must be at least 1")
            num_bins = 50

        try:
            # SEQUENCE ITEM 6: was writing these back into the caller's frame.
            df = df.copy()
            # SEQUENCE ITEM 15. This block was
            #
            #     df[col] = df[col].ffill().bfill().fillna(0)
            #     df[col] = df[col].replace([inf, -inf], nan).fillna(0)
            #
            # and it is the "zero for a missing high or low" that item 9 left
            # on the table. A price of zero is not a neutral placeholder: the
            # profile bins between price_min and price_max, so one zeroed low
            # drags the range to the origin and every bin above it empties.
            # The HVN that comes out is then a structural level derived from a
            # price that never traded, and engine_core passes it to
            # calculate_stop_targets.
            #
            # Forward fill only — no backfill, which would take the value from
            # a later bar, and no zero. If a gap survives, there is no profile
            # to compute and the function's existing empty return says so.
            for col in ["low", "high", "volume"]:
                df[col] = df[col].replace([np.inf, -np.inf], np.nan)
                if df[col].isna().any():
                    logger.warning(f"NaN values found in {col}, forward-filling")
                    df[col] = df[col].ffill()
                if df[col].isna().any():
                    logger.error(
                        f"'{col}' still has gaps after a forward fill — no "
                        f"volume profile can be computed from it. Substituting "
                        f"zero would place structural levels at a price that "
                        f"never traded."
                    )
                    return pd.Series(dtype=float, name="volume"), None, None
        except Exception as e:
            logger.error(f"Failed to clean input data: {e}")
            return pd.Series(dtype=float, name="volume"), None, None

    except Exception as e:
        logger.error(f"Input validation failed: {e}")
        return pd.Series(dtype=float, name="volume"), None, None

    try:
        try:
            price_min = float(df["low"].min())
            price_max = float(df["high"].max())
        except Exception as e:
            logger.error(f"Failed to calculate price range: {e}")
            return pd.Series(dtype=float, name="volume"), None, None

        if not np.isfinite(price_min) or not np.isfinite(price_max):
            logger.error("Price range contains non-finite values")
            return pd.Series(dtype=float, name="volume"), None, None

        if price_max <= price_min:
            logger.error(f"Invalid price range: max ({price_max}) <= min ({price_min})")
            price_mid = (price_max + price_min) / 2 if price_max == price_min else price_min
            price_min = price_mid * 0.999
            price_max = price_mid * 1.001

        try:
            edges = np.linspace(price_min, price_max, num_bins + 1)
            bins = pd.IntervalIndex.from_breaks(edges, closed="right")
        except Exception as e:
            logger.error(f"Failed to create price bins: {e}")
            return pd.Series(dtype=float, name="volume"), None, None

        try:
            profile = pd.Series(0.0, index=bins, name="volume")
        except Exception as e:
            logger.error(f"Failed to initialize volume profile: {e}")
            return pd.Series(dtype=float, name="volume"), None, None

    except Exception as e:
        logger.error(f"Price range and bin construction failed: {e}")
        return pd.Series(dtype=float, name="volume"), None, None

    try:
        processed_candles = 0
        skipped_candles = 0

        try:
            candle_data = df[["low", "high", "volume"]].itertuples(index=False, name=None)
        except Exception as e:
            logger.error(f"Failed to iterate over candle data: {e}")
            return pd.Series(dtype=float, name="volume"), None, None

        for candle in candle_data:
            try:
                low, high, volume = candle
                if not np.isfinite(low) or not np.isfinite(high) or not np.isfinite(volume):
                    skipped_candles += 1
                    continue
                if high < low or volume < 0:
                    skipped_candles += 1
                    continue

                candle_range = high - low
                min_range = (high + low) * 0.5 * 1e-6

                if candle_range <= min_range:
                    try:
                        mid_price = (high + low) * 0.5
                        closest_bin = None
                        min_distance = float('inf')
                        for interval in bins:
                            try:
                                distance = min(abs(mid_price - interval.left), abs(mid_price - interval.right))
                                if distance < min_distance:
                                    min_distance = distance
                                    closest_bin = interval
                            except Exception:
                                continue
                        if closest_bin is not None:
                            profile.loc[closest_bin] += volume
                            processed_candles += 1
                    except Exception as e:
                        logger.warning(f"Failed to process doji candle: {e}")
                        skipped_candles += 1
                    continue

                try:
                    for interval in bins:
                        try:
                            overlap_low = max(low, interval.left)
                            overlap_high = min(high, interval.right)
                            if overlap_high > overlap_low:
                                overlap = overlap_high - overlap_low
                                proportion = overlap / candle_range
                                profile.loc[interval] += volume * proportion
                        except Exception as e:
                            logger.warning(f"Failed to process bin overlap: {e}")
                            continue
                    processed_candles += 1
                except Exception as e:
                    logger.warning(f"Failed to distribute volume for candle: {e}")
                    skipped_candles += 1

            except Exception as e:
                logger.warning(f"Failed to process candle: {e}")
                skipped_candles += 1
                continue

        logger.info(f"Volume profile: processed {processed_candles} candles, skipped {skipped_candles}")

    except Exception as e:
        logger.error(f"Volume distribution failed: {e}")
        return pd.Series(dtype=float, name="volume"), None, None

    try:
        if profile.sum() == 0:
            logger.warning("Volume profile is empty (zero total volume)")
            return profile, None, None

        try:
            centers = pd.Series([interval.mid for interval in bins], index=bins)
        except Exception as e:
            logger.error(f"Failed to calculate bin centers: {e}")
            return profile, None, None

        try:
            hvn_idx = profile.idxmax()
            lvn_idx = profile.idxmin()
            hvn = float(centers.loc[hvn_idx])
            lvn = float(centers.loc[lvn_idx])
            if not np.isfinite(hvn) or not np.isfinite(lvn):
                logger.warning("HVN or LVN values are not finite")
                hvn = None if not np.isfinite(hvn) else hvn
                lvn = None if not np.isfinite(lvn) else lvn
        except Exception as e:
            logger.error(f"Failed to extract HVN/LVN: {e}")
            hvn, lvn = None, None

        return profile, hvn, lvn

    except Exception as e:
        logger.error(f"HVN/LVN extraction failed: {e}")
        return pd.Series(dtype=float, name="volume"), None, None

```


=== FILE: models/__init__.py ===

```python

```


=== FILE: models/bias_engine.py ===

```python
import numpy as np

# ============================================================
# DYNAMIC BIAS ENGINE (Roadmap Layer 2: multi-factor weighted blend)
# ============================================================
#
# Previously bias_score was built from only two real inputs (trend health
# + continuation/reversal from B1). The roadmap specifies six weighted
# factors -- structure regime, volume sentiment, and SuperTrend direction
# were never wired in at all, even though engine_core.py already has all
# of them available at the point it calls this function. Each factor is
# scored on a consistent -100..+100 scale and combined as a straight
# weighted sum (weights below sum to 1.00), so the -100..100 bias_score
# contract everything downstream relies on (DecisionModel, entry_model,
# BiasStateMachine) is unchanged.

WEIGHT_TREND_HEALTH = 0.30
WEIGHT_STRUCTURE_REGIME = 0.20
WEIGHT_VOLUME_SENTIMENT = 0.15
WEIGHT_SUPERTREND_DIRECTION = 0.15
WEIGHT_MACRO_BIAS = 0.10
WEIGHT_REVERSAL_CONTINUATION = 0.10

# raw_bias is now derived directly from the composite bias_score itself
# (previously raw_bias and bias_score came from partially different
# logic/inputs, which was architecturally inconsistent with a "multi-factor
# blend" -- now both come from the same one computation).
RAW_BIAS_THRESHOLD = 20.0

# Volume sentiment strings (see structure.py's _volume_sentiment_simple)
# mapped to a signed -100..100 scale.
_VOLUME_SENTIMENT_SCORES = {
    "STRONG BULLISH ACCUMULATION": 100.0,
    "BULLISH VOLUME SUPPORT": 50.0,
    "STRONG BEARISH DISTRIBUTION": -100.0,
    "BEARISH VOLUME PRESSURE": -50.0,
    # Divergence/exhaustion are warning states, not directional votes --
    # scored neutral here; they already reduce confidence elsewhere
    # (trend_exhaustion feeds reversal detection in trend_health.py).
    "VOLUME DIVERGENCE": 0.0,
    "VOLUME EXHAUSTION": 0.0,
    "NEUTRAL VOLUME": 0.0,
}


def calculate_dynamic_bias(
    trend_sequence,
    trend_health,
    trend_exhaustion,
    reversal_direction,
    reversal_strength,
    continuation_strength,
    structure_regime="NEUTRAL STRUCTURE",
    volume_sentiment="NEUTRAL VOLUME",
    supertrend_direction=0.0,
    macro_bias="NEUTRAL",
):
    """
    Returns:
        raw_bias (str)
        bias_score (float, -100..100)

    SEQUENCE ITEM 6: this function used to take `df` as its first parameter.

    It never read a value out of it. Every factor in the score below comes from
    the scalar arguments — trend health, structure regime, volume sentiment,
    SuperTrend direction, macro bias. The frame's entire role was this, at the
    top of the body:

        critical_cols = ["close", "EMA_20", "EMA_50", "RSI"]
        for col in critical_cols:
            if col in df.columns and df[col].isna().any():
                if col == "close":
                    df[col] = df[col].ffill().bfill()
                else:
                    df[col] = df[col].fillna(df["close"])

    A write-only parameter: it filled NaNs in four columns of the caller's
    frame, three of which this function does not read, and then computed the
    bias from arguments that have nothing to do with any of them. Whatever it
    repaired, it repaired for somebody else, silently, as a side effect of
    being asked an unrelated question. That is the T2-1 violation the Step 5
    plan names by this function's name.

    Because it was write-only, the fix is deletion rather than "operate on a
    copy" — copying would have preserved a computation whose only output was
    the mutation, turning it into a genuine no-op.

    NOT FIXED HERE, AND DELIBERATELY: the fallback above is also a fabrication
    path, and the RSI branch is the worst kind. RSI is a 0-100 oscillator and
    `df["close"]` is a price, so a missing RSI was replaced by whatever the
    asset happened to cost — about 0.80 for AERO, which reads as maximally
    oversold, and five figures for BTC, which is off the scale entirely. It
    could not fire on clean data (add_technical_indicators cleans RSI with a
    fallback of 50.0 before this is reached), so it is latent rather than live.
    Recorded as a rider on sequence item 9, where the fabricated fallbacks are
    given honest semantics. Item 6's job is to stop the writes reaching a frame
    this function does not own; making the fallbacks honest is item 9's.
    """

    # Comprehensive input validation and NaN handling
    def safe_float(value, default=0.0):
        """Safely convert value to float, handling None and NaN."""
        if value is None:
            return default
        try:
            float_val = float(value)
            return float_val if np.isfinite(float_val) else default
        except (ValueError, TypeError):
            return default

    trend_health = safe_float(trend_health, 0.0)
    trend_exhaustion = bool(trend_exhaustion)
    reversal_strength = safe_float(reversal_strength, 0.0)
    continuation_strength = safe_float(continuation_strength, 0.0)
    supertrend_direction = safe_float(supertrend_direction, 0.0)
    reversal_direction = reversal_direction if reversal_direction in ("BULLISH", "BEARISH") else "NONE"
    structure_regime = str(structure_regime) if structure_regime else "NEUTRAL STRUCTURE"
    volume_sentiment = str(volume_sentiment) if volume_sentiment else "NEUTRAL VOLUME"
    macro_bias = str(macro_bias).upper() if macro_bias else "NEUTRAL"
    trend_sequence = str(trend_sequence) if trend_sequence else "NONE"

    # SEQUENCE ITEM 6: the caller-frame cleaning block was here. See the
    # docstring above for what it did and why deleting it was the fix.

    # Trend direction proxy: continuation_strength's sign is B1's dedicated
    # signed-direction signal, so it's used here to sign trend_health (an
    # unsigned magnitude on its own -- see A4's original fix).
    trend_direction = 1 if continuation_strength > 0 else (-1 if continuation_strength < 0 else 0)

    # ============================================================
    # FACTOR 1: TREND HEALTH (30%)
    # ============================================================
    signed_trend_health = trend_direction * np.clip(trend_health, 0, 100)

    # ============================================================
    # FACTOR 2: STRUCTURE REGIME (20%)
    # ============================================================
    if structure_regime == "BULLISH TREND":
        structure_score = 100.0
    elif structure_regime == "BEARISH TREND":
        structure_score = -100.0
    else:
        structure_score = 0.0

    # ============================================================
    # FACTOR 3: VOLUME SENTIMENT (15%)
    # ============================================================
    volume_score = _VOLUME_SENTIMENT_SCORES.get(volume_sentiment.upper(), 0.0)

    # ============================================================
    # FACTOR 4: SUPERTREND DIRECTION (15%)
    # ============================================================
    if supertrend_direction > 0:
        supertrend_score = 100.0
    elif supertrend_direction < 0:
        supertrend_score = -100.0
    else:
        supertrend_score = 0.0

    # ============================================================
    # FACTOR 5: MACRO BIAS (10%)
    # ============================================================
    if macro_bias == "BULLISH":
        macro_score = 100.0
    elif macro_bias == "BEARISH":
        macro_score = -100.0
    else:
        macro_score = 0.0

    # ============================================================
    # FACTOR 6: REVERSAL / CONTINUATION (10%, combined single factor)
    # continuation_strength is the base signal; a reversal signal that
    # actively OPPOSES the current trend direction proportionally
    # discounts it (never fully zeroes it -- floored at 20% of its
    # original value), rather than being a separate 7th factor.
    # ============================================================
    reversal_signed_direction = 1 if reversal_direction == "BULLISH" else (-1 if reversal_direction == "BEARISH" else 0)
    if trend_direction != 0 and reversal_signed_direction != 0 and reversal_signed_direction != trend_direction:
        discount = max(0.2, 1.0 - (np.clip(reversal_strength, 0, 100) / 100.0))
        reversal_continuation_score = continuation_strength * discount
    else:
        reversal_continuation_score = continuation_strength

    # ============================================================
    # WEIGHTED BLEND
    # ============================================================
    bias_score = (
        signed_trend_health * WEIGHT_TREND_HEALTH +
        structure_score * WEIGHT_STRUCTURE_REGIME +
        volume_score * WEIGHT_VOLUME_SENTIMENT +
        supertrend_score * WEIGHT_SUPERTREND_DIRECTION +
        macro_score * WEIGHT_MACRO_BIAS +
        reversal_continuation_score * WEIGHT_REVERSAL_CONTINUATION
    )

    # B2 FIX: trend_sequence was accepted as a parameter here but never
    # actually used anywhere in this function -- structure.py's
    # _detect_sequence() was a stub that always returned "NONE", so there
    # was nothing real to use yet. Now that B2 has built real BOS/CHOCH
    # detection, a CHOCH ("change of character") AGAINST the current trend
    # direction is a genuine structural warning sign -- price just broke
    # the last confirmed swing extreme against the established sequence,
    # which is the same kind of warning trend_failure already represents.
    # Rather than adding a 7th weighted factor (which would mean
    # re-deriving and re-testing all six existing weights), it's folded
    # into the same discount as trend_failure below.
    choch_against_trend = (
        (trend_direction > 0 and "CHOCH BEARISH" in trend_sequence) or
        (trend_direction < 0 and "CHOCH BULLISH" in trend_sequence)
    )

    # A CHOCH against the current direction is "the structure just
    # contradicted this bias", so it discounts the WHOLE blend rather than
    # getting its own weight slot among the six factors.
    #
    # SEQUENCE ITEM 9c: this condition was `trend_failure or
    # choch_against_trend`, and the comment described them as two signals
    # sharing one discount. There was only ever one. trend_failure could not
    # become True — see the note in trend_health.py — so every discount this
    # line has ever applied came from the CHOCH.
    if choch_against_trend:
        bias_score *= 0.5

    bias_score = float(np.clip(bias_score, -100, 100))

    # raw_bias now comes directly from the same composite score, instead
    # of a separate trend_health-only gate -- one computation drives both.
    if bias_score > RAW_BIAS_THRESHOLD:
        raw_bias = "BULLISH"
    elif bias_score < -RAW_BIAS_THRESHOLD:
        raw_bias = "BEARISH"
    else:
        raw_bias = "NEUTRAL"

    return raw_bias, bias_score


# ============================================================
# DYNAMIC REGIME ENGINE
# ============================================================

def calculate_dynamic_regime(df):
    """
    Returns:
        dynamic_regime (str)
        volatility_mode (str)
    """

    if df is None or df.empty:
        return "UNKNOWN", "UNKNOWN"

    # Volatility detection with NaN handling
    if "ATR" in df.columns:
        atr = df["ATR"].iloc[-1]
        price = df["close"].iloc[-1]

        # Fix: Handle NaN values and prevent division by zero
        if np.isfinite(atr) and np.isfinite(price) and price > 0:
            vol_ratio = atr / price
        else:
            vol_ratio = 0.01  # Default to medium volatility

        # BUG FIX (found while cross-checking Option A's "volatility modes
        # are consistent" point): risk_model.py has a real "EXTREME
        # VOLATILITY" tier (widest stops, halved position sizing,
        # automatic EXTREME RISK classification) but this function -- the
        # only place volatility_state is ever produced -- topped out at
        # "HIGH VOLATILITY" and could never emit "EXTREME VOLATILITY".
        # That entire risk tier was dead code. Added the missing tier.
        if vol_ratio > 0.04:
            volatility_mode = "EXTREME VOLATILITY"
        elif vol_ratio > 0.02:
            volatility_mode = "HIGH VOLATILITY"
        elif vol_ratio > 0.01:
            volatility_mode = "MEDIUM VOLATILITY"
        else:
            volatility_mode = "LOW VOLATILITY"
    else:
        volatility_mode = "UNKNOWN"

    # Regime detection (column name fixed in the A3/A4/A5 pass -- was
    # checking for "STRUCTURE_REGIME", which never existed; structure.py
    # names the column "STRUCTURE")
    if "STRUCTURE" in df.columns:
        dynamic_regime = df["STRUCTURE"].iloc[-1]
    else:
        dynamic_regime = "NEUTRAL STRUCTURE"

    return dynamic_regime, volatility_mode


# ============================================================
# BIAS STATE MACHINE
# ============================================================

class BiasStateMachine:
    def __init__(self):
        self.state = "NEUTRAL"

    def transition(self, raw_bias, bias_score):
        """
        Returns a stable bias state.
        """

        # Normalize None values
        bias_score = bias_score if bias_score is not None else 0.0

        # Thresholds match bias_score's real -100..100 scale (A5 fix).
        if raw_bias == "BULLISH" and bias_score > 30:
            self.state = "BULLISH CONFIRMED"
        elif raw_bias == "BEARISH" and bias_score < -30:
            self.state = "BEARISH CONFIRMED"
        elif abs(bias_score) < 20:
            self.state = "NEUTRAL"
        else:
            self.state = raw_bias

        return self.state
```


=== FILE: models/btc_context.py ===

```python
import numpy as np
import pandas as pd
from typing import Tuple

# ============================================================
# BTC/AERO RELATIONSHIP ENGINE (new feature, V1)
# ============================================================
#
# Supports the "BTC-Adjusted AERO Prediction" feature: a SEPARATE, additive
# reading that sits alongside the original AERO-only analysis and never
# replaces or distorts it. This module only computes the relationship
# metrics (correlation, beta, and a volatility-based stress classifier);
# BTC's own bias/trend/regime reuses the exact same, already-tested
# bias_engine.py / trend_health.py / structure.py functions engine_core.py
# already runs for AERO -- just called a second time on BTC's own data.


def compute_correlation_beta(aero_closes: pd.Series, btc_closes: pd.Series, window: int = 30) -> Tuple[float, float, int]:
    """
    Rolling correlation + beta between AERO and BTC returns over the most
    recent `window` candles (or however much history is actually available,
    whichever is smaller).

    Returns:
        correlation (float, -1..1; 0.0 if it can't be computed)
        beta (float; AERO's sensitivity to BTC moves -- 1.0 means AERO
              tends to move 1:1 with BTC; 0.0 if it can't be computed)
        n (int; how many paired return observations were actually used)
    """
    try:
        if aero_closes is None or btc_closes is None:
            return 0.0, 0.0, 0

        aero_series = pd.Series(aero_closes).reset_index(drop=True)
        btc_series = pd.Series(btc_closes).reset_index(drop=True)

        if len(aero_series) < 3 or len(btc_series) < 3:
            return 0.0, 0.0, 0

        n = min(len(aero_series), len(btc_series), window + 1)
        aero_tail = aero_series.tail(n).reset_index(drop=True)
        btc_tail = btc_series.tail(n).reset_index(drop=True)

        aero_returns = aero_tail.pct_change().replace([np.inf, -np.inf], np.nan)
        btc_returns = btc_tail.pct_change().replace([np.inf, -np.inf], np.nan)

        valid = aero_returns.notna() & btc_returns.notna()
        aero_returns = aero_returns[valid].reset_index(drop=True)
        btc_returns = btc_returns[valid].reset_index(drop=True)

        if len(aero_returns) < 3:
            return 0.0, 0.0, 0

        btc_var = btc_returns.var()
        if not np.isfinite(btc_var) or btc_var == 0:
            return 0.0, 0.0, int(len(aero_returns))

        covariance = float(np.cov(aero_returns, btc_returns)[0, 1])
        beta = covariance / float(btc_var)

        correlation = float(aero_returns.corr(btc_returns))
        if not np.isfinite(correlation):
            correlation = 0.0
        if not np.isfinite(beta):
            beta = 0.0

        correlation = max(-1.0, min(1.0, correlation))

        return correlation, beta, int(len(aero_returns))

    except Exception:
        return 0.0, 0.0, 0


def classify_correlation(r: float) -> str:
    """Plain-language label for a -1..1 correlation coefficient."""
    try:
        r = float(r)
    except (TypeError, ValueError):
        r = 0.0

    r_abs = abs(r)
    if r_abs >= 0.7:
        strength = "STRONG"
    elif r_abs >= 0.3:
        strength = "MODERATE"
    else:
        return "WEAK / NO CLEAR RELATIONSHIP"

    direction = "POSITIVE" if r >= 0 else "NEGATIVE"
    return f"{strength} {direction}"


def classify_stress(btc_volatility_mode: str) -> bool:
    """
    V1 broad-market-stress proxy: BTC itself sitting in an elevated
    volatility regime. Simple and reuses an already-tested classifier
    (calculate_dynamic_regime in bias_engine.py) rather than inventing a
    new stress metric for this first version.
    """
    return str(btc_volatility_mode).upper() in ("EXTREME VOLATILITY", "HIGH VOLATILITY")
```


=== FILE: models/decision_model.py ===

```python
from typing import Dict, Any, List, Tuple, Optional
import logging

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
    the single place that turns {bias, trend, structure, entry, risk,
    macro_bias} into {final_action, confidence, trade_quality, explanation}.
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
        structure: Dict[str, Any],
        entry: Dict[str, Any],
        risk: Dict[str, Any],
        macro_bias: str,
        btc_context: Optional[Dict[str, Any]] = None,
        degradation: Optional[List[str]] = None,
        symbol: str = "this asset",
    ) -> Dict[str, Any]:
        reasons: List[str] = []
        degradation = list(degradation) if degradation else []

        final_action = self._determine_final_action(bias, trend, entry, risk, macro_bias, reasons)
        confidence = self._compute_confidence(bias, trend, structure, risk, final_action, reasons)
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

            long_signal = bool(entry.get("long_signal", False))
            short_signal = bool(entry.get("short_signal", False))
            raw_bias = str(bias.get("raw", "NEUTRAL"))

            if validation_state == "WEAK" and trend_health < 40:
                reasons.append(
                    f"Validation is weak and trend health is low ({trend_health:.0f}/100) — waiting for a cleaner setup."
                )
                return "WAIT"

            if raw_bias == "BULLISH" or long_signal or macro_bias == "BULLISH":
                if trend_health >= 75 and entry_score >= 70 and not divergence:
                    if entry_active:
                        reasons.append(
                            f"Bias is bullish with strong trend health ({trend_health:.0f}/100) and a "
                            f"high-quality, active entry ({entry_score:.0f}/100), with no momentum divergence "
                            f"— AGGRESSIVE LONG."
                        )
                        return "AGGRESSIVE LONG"
                    reasons.append(
                        f"Bias is bullish with strong trend health ({trend_health:.0f}/100) and a high-quality "
                        f"entry ({entry_score:.0f}/100), with no momentum divergence — LONG."
                    )
                    return "LONG"
                elif trend_health >= 50 and macro_bias == "BULLISH":
                    reasons.append(
                        f"Bias is bullish and the broader macro trend agrees, with decent trend health "
                        f"({trend_health:.0f}/100), but the entry quality ({entry_score:.0f}/100) isn't strong "
                        f"enough for full size — CONSERVATIVE LONG."
                    )
                    return "CONSERVATIVE LONG"

            if raw_bias == "BEARISH" or short_signal or macro_bias == "BEARISH":
                if trend_health >= 75 and entry_score >= 70 and not divergence:
                    if entry_active:
                        reasons.append(
                            f"Bias is bearish with strong trend health ({trend_health:.0f}/100) and a "
                            f"high-quality, active entry ({entry_score:.0f}/100), with no momentum divergence "
                            f"— AGGRESSIVE SHORT."
                        )
                        return "AGGRESSIVE SHORT"
                    reasons.append(
                        f"Bias is bearish with strong trend health ({trend_health:.0f}/100) and a high-quality "
                        f"entry ({entry_score:.0f}/100), with no momentum divergence — SHORT."
                    )
                    return "SHORT"
                elif trend_health >= 50 and macro_bias == "BEARISH":
                    reasons.append(
                        f"Bias is bearish and the broader macro trend agrees, with decent trend health "
                        f"({trend_health:.0f}/100), but the entry quality ({entry_score:.0f}/100) isn't strong "
                        f"enough for full size — CONSERVATIVE SHORT."
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
        trend: Dict[str, Any],
        structure: Dict[str, Any],
        risk: Dict[str, Any],
        final_action: str,
        reasons: List[str],
    ) -> float:
        """
        Confidence = how much the overall picture agrees with itself, not
        just "how strong is the trend." Built from:
          - bias_strength (0-100): magnitude of bias_score, i.e. how
            decisively the bias engine committed to a direction. Trend health
            is INSIDE this at weight 0.30 and must not be added again --
            see sequence item 11 below.
          - structure_alignment: bonus if structure regime agrees with
            bias direction, penalty if they actively disagree
          - validation_adj: bonus/penalty from risk.validation_state
        This is a V1 -- the roadmap's Layer 2 (multi-factor bias weighting,
        including SuperTrend direction and macro bias strength as their
        own explicit inputs) will feed a richer version of this later.
        """
        bias_strength = min(100.0, abs(_safe_float(bias.get("score"), 0.0)))

        # SEQUENCE ITEM 11: `trend_health * 0.3` was a term here. It is
        # removed. bias_score already carries trend health at WEIGHT_TREND_HEALTH
        # = 0.30 (bias_engine.py), so adding it again counted one measurement
        # twice and presented the agreement of a number with itself as
        # corroboration.
        #
        # bias_strength moves 0.5 -> 0.8 so the score still spans 0-100. Without
        # that the ceiling would be 70, and confidence is consumed by
        # _compute_ev as a rough win rate — a percentage that cannot reach its
        # own maximum understates every expected value computed from it.
        #
        # 80 + 10 (structure) + 10 (validation) = 100 exactly.

        raw_bias = str(bias.get("raw", "NEUTRAL"))
        structure_regime = str(structure.get("regime", "NEUTRAL"))

        if raw_bias == "BULLISH" and structure_regime == "BULLISH TREND":
            structure_alignment = 10.0
            alignment_phrase = "structure agrees with the bullish bias"
        elif raw_bias == "BEARISH" and structure_regime == "BEARISH TREND":
            structure_alignment = 10.0
            alignment_phrase = "structure agrees with the bearish bias"
        elif raw_bias == "BULLISH" and structure_regime == "BEARISH TREND":
            structure_alignment = -15.0
            alignment_phrase = "structure is actually bearish while bias is bullish, a real disagreement"
        elif raw_bias == "BEARISH" and structure_regime == "BULLISH TREND":
            structure_alignment = -15.0
            alignment_phrase = "structure is actually bullish while bias is bearish, a real disagreement"
        else:
            structure_alignment = 0.0
            alignment_phrase = "structure is neutral relative to the bias"

        # Note: this is the volume/structure "validation" check (risk.validation_state),
        # a separate signal from the risk-regime gate that decides risk_valid/risk_reason
        # above. Deliberately NOT called "risk validation" here -- when the risk-regime
        # gate blocks a trade (NO-TRADE) and this validation check happens to read STRONG,
        # the two would otherwise read as contradicting each other.
        validation_state = str(risk.get("validation_state", "NEUTRAL"))
        validation_adj = {"STRONG": 10.0, "NEUTRAL": 0.0, "WEAK": -15.0}.get(validation_state, 0.0)
        if validation_state == "STRONG":
            validation_phrase = "validation is strong"
        elif validation_state == "WEAK":
            validation_phrase = "validation is weak"
        else:
            validation_phrase = "validation is neutral"

        confidence = (bias_strength * 0.8) + structure_alignment + validation_adj
        confidence = max(0.0, min(100.0, confidence))

        # When the risk-regime gate has already blocked the trade, make clear this
        # confidence score describes how the picture lines up, not a green light --
        # otherwise a high number here right after "NO-TRADE" reads as contradictory.
        qualifier = (
            " This reflects how the picture lines up, not a green light — the risk check above is what's blocking the trade."
            if final_action.startswith("NO-TRADE")
            else ""
        )

        # SEQUENCE ITEM 11, coupling rule: this sentence changed in the same
        # commit as the formula. Prose describing a calculation that no longer
        # runs is an Item 8 regression the moment the number moves — and it
        # named trend health as an input, which is exactly what was removed.
        reasons.append(
            f"Confidence is {confidence:.0f}/100 — bias strength is {bias_strength:.0f}/100 "
            f"(which already carries trend health), {alignment_phrase}, and "
            f"{validation_phrase}.{qualifier}"
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
```


=== FILE: models/entry_model.py ===

```python
import numpy as np
from typing import Dict, Any, Tuple, Optional

def calculate_entry_quality(
    df: Optional[Any],
    zone_lower: float,
    zone_upper: float,
    macro_bias: str = "NEUTRAL",
    trade_direction: str = "LONG",
    trend_direction: str = "NEUTRAL",
    structure_sequence: str = "NONE",
) -> Dict[str, Any]:
    """
    Calculates real, quantitative sub-scores and total score for entry quality,
    fully integrated with Macro Trend Confluence and comprehensive NaN handling.
    Max points: 100
    - EMA Zone Position : 30 pts
    - ATR Distance      : 25 pts
    - VWMA Distance     : 20 pts
    - RSI Extension     : 15 pts
    - Structure         : 12 pts
    (Macro alignment, trend direction, and structure sequence each act as a
    small multiplier/adjuster -- see section 6 below. Roadmap Layer 5: this
    was previously just the single macro multiplier; trend_direction and
    structure_sequence are new inputs, using signals that already existed
    elsewhere in the engine (trend_health.py's new trend_direction field,
    structure.py's B2 sequence detection) but weren't yet factored into
    entry quality itself.)
    """
    default_response = {
        "score": 0.0,
        "ema_pos_pts": 0,
        "atr_dist_pts": 0,
        "vwma_pts": 0,
        "rsi_pts": 0,
        "struct_pts": 0,
        "entry_status": "NO DATA",
        "distance_from_zone": 0.0
    }

    if df is None or getattr(df, "empty", True):
        return default_response

    # Validate and clean inputs
    def safe_float(value: Any, fallback: float) -> float:
        """Safely extract float value with fallback."""
        try:
            if value is None or not np.isfinite(value):
                return fallback
            return float(value)
        except (ValueError, TypeError):
            return fallback

    close = safe_float(df["close"].iloc[-1] if "close" in df.columns and not df["close"].empty else None, 1.0)
    zone_lower = safe_float(zone_lower, close * 0.99)
    zone_upper = safe_float(zone_upper, close * 1.01)

    # Ensure zone bounds are logical
    if zone_lower > zone_upper:
        zone_lower, zone_upper = zone_upper, zone_lower

    # ============================================================
    # 1. EMA ZONE POSITION SCORING (Max 30)
    # ============================================================
    zone_mid = (zone_lower + zone_upper) / 2.0
    zone_width = abs(zone_upper - zone_lower)

    if zone_width <= 1e-8 or not np.isfinite(zone_width):
        zone_width = close * 0.01  # Default to 1% of current price

    dist_to_mid = abs(close - zone_mid)

    if dist_to_mid <= zone_width:
        ema_pos_pts = 30
        entry_status = "ACTIVE ENTRY ZONE"
    elif dist_to_mid <= zone_width * 2.0:
        ema_pos_pts = 20
        entry_status = "NEAR ZONE"
    elif dist_to_mid <= zone_width * 3.5:
        ema_pos_pts = 10
        entry_status = "APPROACHING ZONE"
    else:
        ema_pos_pts = 5
        entry_status = "AWAY FROM ZONE"

    distance_from_zone = float((dist_to_mid / close) * 100.0)

    # ============================================================
    # 2. ATR DISTANCE SCORING (Max 25)
    # ============================================================
    atr = safe_float(df["ATR"].iloc[-1] if "ATR" in df.columns and not df["ATR"].empty else None, close * 0.02)

    if atr > 0:
        try:
            atr_ratio = dist_to_mid / atr
            if np.isfinite(atr_ratio):
                # Smooth exponential decay instead of hard thresholds
                atr_dist_pts = float(25 * np.exp(-atr_ratio * 0.5))
                atr_dist_pts = max(5.0, min(25.0, atr_dist_pts))  # Bounded between 5-25
            else:
                atr_dist_pts = 15.0
        except (ZeroDivisionError, OverflowError):
            atr_dist_pts = 15.0
    else:
        atr_dist_pts = 15.0

    # ============================================================
    # 3. VWMA DISTANCE SCORING (Max 20)
    # ============================================================
    vwma_pts = 15.0  # Default score
    if "VWMA" in df.columns and not df["VWMA"].empty:
        vwma = safe_float(df["VWMA"].iloc[-1], close)

        if close > 0:
            try:
                vwma_diff = abs(close - vwma) / close
                if np.isfinite(vwma_diff):
                    if vwma_diff < 0.01:
                        vwma_pts = 20.0
                    elif vwma_diff < 0.025:
                        vwma_pts = 15.0
                    elif vwma_diff < 0.05:
                        vwma_pts = 10.0
                    else:
                        vwma_pts = 5.0
            except (ZeroDivisionError, OverflowError):
                vwma_pts = 15.0

    # ============================================================
    # 4. RSI EXTENSION SCORING (Max 15)
    # ============================================================
    rsi_pts = 10.0  # Default score
    if "RSI" in df.columns and not df["RSI"].empty:
        rsi = safe_float(df["RSI"].iloc[-1], 50.0)

        if 40.0 <= rsi <= 60.0:
            rsi_pts = 15.0
        elif 30.0 <= rsi < 40.0 or 60.0 < rsi <= 70.0:
            rsi_pts = 10.0
        else:
            rsi_pts = 5.0

    # ============================================================
    # 5. STRUCTURE PROXIMITY SCORING (Max 12)
    # ============================================================
    struct_pts = 6.0  # Default score
    if "HVN" in df.columns and not df["HVN"].empty:
        hvn = safe_float(df["HVN"].iloc[-1], close)

        if close > 0:
            try:
                hvn_dist = abs(close - hvn) / close
                if np.isfinite(hvn_dist):
                    if hvn_dist < 0.015:
                        struct_pts = 12.0
                    elif hvn_dist < 0.03:
                        struct_pts = 8.0
                    else:
                        struct_pts = 4.0
            except (ZeroDivisionError, OverflowError):
                struct_pts = 6.0

    base_score = float(ema_pos_pts + atr_dist_pts + vwma_pts + rsi_pts + struct_pts)

    # ============================================================
    # 6. CONFLUENCE MULTIPLIERS & FINAL BOUNDS (Roadmap Layer 5)
    # ============================================================
    # Each multiplier is independently small (+-5-10%) and only nudges the
    # score -- none of them can gate a trade on their own (generate_entry_signals
    # already handles hard gating). Combined, they let entry quality reflect
    # not just "is price near a good zone" but "does the broader context this
    # trade would be entering into actually support this specific direction."
    macro_multiplier = 1.0
    if macro_bias == "BULLISH" and trade_direction == "LONG":
        macro_multiplier = 1.05
    elif macro_bias == "BEARISH" and trade_direction == "SHORT":
        macro_multiplier = 1.05
    elif macro_bias not in ["NEUTRAL", ""] and macro_bias != trade_direction:
        macro_multiplier = 0.90

    # Trend direction alignment: trend_health.py's EMA-slope-based direction
    # label agreeing (or disagreeing) with the direction being scored here.
    trend_multiplier = 1.0
    if trade_direction == "LONG":
        if trend_direction == "BULLISH":
            trend_multiplier = 1.05
        elif trend_direction == "BEARISH":
            trend_multiplier = 0.90
    elif trade_direction == "SHORT":
        if trend_direction == "BEARISH":
            trend_multiplier = 1.05
        elif trend_direction == "BULLISH":
            trend_multiplier = 0.90

    # Structure sequence alignment: a BOS (continuation) in this trade's own
    # direction is rewarded; a CHOCH (possible reversal) against this trade's
    # direction is penalized. An established (non-BOS) swing sequence in this
    # trade's direction, or "NONE"/anything else, is left neutral -- BOS is a
    # stronger continuation signal than a plain swing sequence, so only BOS
    # earns the reward tier here.
    structure_multiplier = 1.0
    if trade_direction == "LONG":
        if structure_sequence == "BOS BULLISH (TREND CONTINUATION)":
            structure_multiplier = 1.05
        elif structure_sequence == "CHOCH BEARISH (POSSIBLE REVERSAL)":
            structure_multiplier = 0.90
    elif trade_direction == "SHORT":
        if structure_sequence == "BOS BEARISH (TREND CONTINUATION)":
            structure_multiplier = 1.05
        elif structure_sequence == "CHOCH BULLISH (POSSIBLE REVERSAL)":
            structure_multiplier = 0.90

    combined_multiplier = macro_multiplier * trend_multiplier * structure_multiplier
    total_score = float(min(100.0, max(0.0, base_score * combined_multiplier)))

    return {
        "score": float(total_score),
        "ema_pos_pts": int(ema_pos_pts),
        "atr_dist_pts": int(round(atr_dist_pts)),
        "vwma_pts": int(vwma_pts),
        "rsi_pts": int(rsi_pts),
        "struct_pts": int(struct_pts),
        "entry_status": str(entry_status),
        "distance_from_zone": float(distance_from_zone)
    }


def generate_entry_signals(
    detailed_bias: str,
    structure_regime: str,
    trend_health: float,
    trend_exhaustion: bool,
    reversal_strength: float,
    macro_bias: str = "NEUTRAL"
) -> Tuple[bool, bool]:
    """
    Generate long/short entry signals based on structural bias,
    trend health, collapse conditions, and Multi-Timeframe Confluence.
    """
    # SEQUENCE ITEM 9c: `trend_failure or` removed from this condition. It
    # was always False — the gate that produced it compared STRUCTURE
    # against labels structure.py never writes. The two remaining
    # disjuncts are live and are what has actually been blocking entries.
    if trend_exhaustion or (reversal_strength is not None and reversal_strength > 0):
        return False, False

    # A1 FIX: structure.py only ever emits "BULLISH TREND" / "BEARISH TREND"
    # (see _detect_regime() in structure.py) — "BULLISH STRUCTURE" /
    # "BEARISH STRUCTURE" were never produced by anything, so these gates
    # could never pass. Corrected to match the real emitted strings.
    #
    # A2 FIX: BiasStateMachine only ever emits "BULLISH CONFIRMED" /
    # "BEARISH CONFIRMED" / "NEUTRAL" (see bias_engine.py) — "LONG" / "SHORT"
    # were never produced either, a second independent dead gate. Corrected
    # to match. Note: this gate still won't fire in practice until B1 (the
    # continuation/reversal engine in trend_health.py) exists, since raw_bias
    # is currently pinned to NEUTRAL upstream — that's expected and by design,
    # not a bug in this file.
    macro_long_allowed = macro_bias in ["BULLISH", "NEUTRAL"]
    long_signal = bool(
        macro_long_allowed
        and detailed_bias == "BULLISH CONFIRMED"
        and structure_regime == "BULLISH TREND"
        and trend_health >= 50.0
    )

    macro_short_allowed = macro_bias in ["BEARISH", "NEUTRAL"]
    short_signal = bool(
        macro_short_allowed
        and detailed_bias == "BEARISH CONFIRMED"
        and structure_regime == "BEARISH TREND"
        and trend_health >= 50.0
    )

    return long_signal, short_signal
```


=== FILE: models/exit_model.py ===

```python
"""
Exit-side logic for the Phase-7 engine.

SEQUENCE ITEM 5b removed `compute_exit` from this file. What it was, why it
went, and what replaced it:

It took the price frame, the entry signals and the risk block, and returned six
keys — final_action, exit_reason, stop_loss, target_hit, exit_status and
current_price. It read as the engine's exit-management brain: stop-loss
evaluated before targets, three target tiers, PARTIAL EXIT versus EXITED
status.

Five of those six keys reached nothing. signal_router.py:265 assembles the
decision object's "exit" entry itself, as {"action": <DecisionModel's
final_action>, "current_price": ...}, so everything else was dropped one call
later. The panel does print a stop loss, but reads risk["atr_stop"]. The panel
does print a DECISION, but that is DecisionModel's verdict, not this one — the
key names collided, which is how this survived earlier reads of the file
including mine.

The sixth key, current_price, was float(price_data["close"].iloc[-1]) computed
from the same frame on which engine_core had already evaluated exactly that
expression. It is now passed straight through from there.

So the deletion is output-invariant, and what looked like an exit-management
system was a stop/target ladder whose verdicts were computed every run and
thrown away. Nothing in the engine ever acted on "STOP LOSS HIT". Nothing
could — Item 18 forbids execution, and the engine holds no positions to exit.

The real exit-side feature is build_exit_watch below, which is advisory by
design and is consumed. It stays.
"""

# SEQUENCE ITEM 5b: pandas and numpy were imported for compute_exit's frame
# access and its isfinite check. build_exit_watch uses neither, so both imports
# go with it.
from typing import Dict, Any, Optional, List

# ============================================================
# C3 BUILD: EXIT WATCH -- advisory-only flags, never automatic actions
# ============================================================
#
# Per the fix plan's C3: the originally-planned exit triggers (trailing
# stop, break-even, trend failure, bias flip, HVN/LVN hit, SuperTrend flip,
# exhaustion, divergence) become flags you read on the panel, not a
# conflict-resolution system the engine acts on. This function collects
# whichever of those are currently true/relevant and returns them as plain
# sentences -- nothing here changes DECISION above; it's a separate,
# advisory "things to keep an eye on" list for a position you're already in
# or considering.
#
# Two of the eight (SuperTrend flip, bias flip) need to compare against the
# PREVIOUS run, since a "flip" is a change, not a snapshot. Since this tool
# is normally run as a fresh command each time (not a long-running process),
# that comparison has to come from state persisted to disk between runs --
# engine_core.py reads/writes that small state file and passes the prior
# values in as `prior_state`. If there's no prior run yet (first-ever run,
# or the state file is missing/corrupt), those two flags are simply skipped
# rather than guessed at.

def build_exit_watch(
    trend: Dict[str, Any],
    structure: Dict[str, Any],
    bias: Dict[str, Any],
    current_price: float,
    supertrend_direction: float,
    target_t1: float,
    prior_state: Optional[Dict[str, Any]] = None,
) -> List[str]:
    """
    Returns a list of plain-language advisory flags. An empty-looking
    result still returns one line saying nothing is active, so the panel
    section is never blank/ambiguous.
    """
    flags: List[str] = []
    prior_state = prior_state if isinstance(prior_state, dict) else {}

    try:
        raw_bias = str(bias.get("raw", "NEUTRAL"))
        detailed_bias = str(bias.get("detailed", "NEUTRAL"))
        sequence = str(structure.get("sequence", "NONE"))
        hvn = float(structure.get("hvn", 0.0) or 0.0)
        lvn = float(structure.get("lvn", 0.0) or 0.0)
        current_price = float(current_price) if current_price else 0.0

        # --- Trend-quality warnings (no prior-run comparison needed) ---
        # SEQUENCE ITEM 9c: a "Trend failure is active" flag lived here. It
        # could not fire — trend_failure was always False — so this advisory
        # has never once appeared on a panel, while reading as though the
        # engine watches for a lower-high/lower-low pattern. It does not.

        if bool(trend.get("trend_exhaustion", False)):
            flags.append(
                "Trend exhaustion is active — momentum looks stretched and may be due for a pause or pullback."
            )

        if bool(trend.get("momentum_divergence", False)):
            flags.append(
                "Momentum divergence is active — price and momentum are disagreeing, an early warning sign worth "
                "watching."
            )

        # --- Reversal signal opposing the current bias (B1) ---
        reversal_direction = trend.get("reversal_direction", "NONE")
        reversal_strength = float(trend.get("reversal_strength", 0.0) or 0.0)
        reversal_opposes = (
            (raw_bias == "BULLISH" and reversal_direction == "BEARISH")
            or (raw_bias == "BEARISH" and reversal_direction == "BULLISH")
        )
        if reversal_opposes and reversal_strength >= 40.0:
            flags.append(
                f"A {reversal_direction} reversal signal is forming against the current {raw_bias} bias "
                f"(strength {reversal_strength:.0f}/100)."
            )

        # --- CHOCH opposing the current bias (B2) ---
        choch_opposes = (
            (raw_bias == "BULLISH" and "CHOCH BEARISH" in sequence)
            or (raw_bias == "BEARISH" and "CHOCH BULLISH" in sequence)
        )
        if choch_opposes:
            flags.append(
                f"Structure just flagged {sequence} — price broke the last swing point against the prevailing "
                f"trend, an early sign of a possible reversal."
            )

        # --- Proximity to a high/low volume node ---
        if current_price > 0 and hvn > 0 and abs(current_price - hvn) / current_price * 100.0 < 1.5:
            flags.append(
                f"Price is close to a high-volume node (${hvn:.4f}) — a level where price has often reacted "
                f"before."
            )
        if current_price > 0 and lvn > 0 and abs(current_price - lvn) / current_price * 100.0 < 1.5:
            flags.append(
                f"Price is close to a low-volume node (${lvn:.4f}) — price has tended to move through these "
                f"quickly rather than react."
            )

        # --- SuperTrend flip since the last run (needs prior_state) ---
        prior_supertrend = prior_state.get("supertrend_direction")
        if prior_supertrend is not None:
            try:
                prior_supertrend = float(prior_supertrend)
                current_sign = 1 if supertrend_direction > 0 else (-1 if supertrend_direction < 0 else 0)
                prior_sign = 1 if prior_supertrend > 0 else (-1 if prior_supertrend < 0 else 0)
                if current_sign != 0 and prior_sign != 0 and current_sign != prior_sign:
                    from_side = "BULLISH" if prior_sign > 0 else "BEARISH"
                    to_side = "BULLISH" if current_sign > 0 else "BEARISH"
                    flags.append(f"SuperTrend flipped from {from_side} to {to_side} since the last run.")
            except (ValueError, TypeError):
                pass

        # --- Bias state flip since the last run (needs prior_state) ---
        prior_bias = prior_state.get("detailed_bias")
        if prior_bias and str(prior_bias) != detailed_bias:
            flags.append(f"Bias state changed from {prior_bias} to {detailed_bias} since the last run.")

        # --- Always-on informational note (not a warning) ---
        if target_t1 and float(target_t1) > 0:
            flags.append(
                f"If you're already in this trade, a common approach is moving your stop to breakeven once price "
                f"reaches Target 1 (${float(target_t1):.4f})."
            )

    except Exception as e:
        flags.append(f"Exit watch could not be fully evaluated this run ({e}).")

    if not flags:
        flags.append("No exit-watch flags are active right now — nothing here suggests changing your position early.")

    return flags
```


=== FILE: models/risk_model.py ===

```python
from typing import Tuple, Union, Optional
import logging
import numpy as np

logger = logging.getLogger(__name__)

class RiskModel:
    """
    Core institutional risk engine for Phase-7.
    Provides:
        - Volatility-adjusted ATR stop calculation
        - Tiered target generation
        - Position sizing & leverage adjustment
        - Risk regime classification & advanced validation
    """

    def __init__(self) -> None:
        # Tunable multipliers
        self.atr_stop_mult: float = 1.2        # Base ATR multiplier for stop
        self.target1_mult: float = 1.0         # Conservative target (x stop distance)
        self.target2_mult: float = 2.0         # Normal target (x stop distance)
        self.target3_mult: float = 3.0         # Aggressive target (x stop distance)

    # ============================================================
    # STOP & TARGETS (WITH VOLATILITY ADJUSTMENT)
    # ============================================================

    def calculate_stop_targets(
        self,
        detailed_bias: str,
        trend_health: float,
        current_price: float,
        atr_val: float,
        structural_level: Union[float, None],
        bias_score: float,
        volatility_state: str = "NORMAL"
    ) -> Tuple[float, float, float, float]:
        """
        Compute volatility-adjusted ATR stop + tiered targets, forcing directional fallback
        if bias is neutral so targets never collapse to current price.

        Args:
            detailed_bias: Trading bias direction
            trend_health: Trend health score (0-100)
            current_price: Current market price
            atr_val: Average True Range value
            structural_level: Key structural price level
            bias_score: Bias strength score
            volatility_state: Current volatility regime

        Returns:
            Tuple of (atr_stop, target1, target2, target3)
        """
        try:
            # Input validation
            if current_price <= 0 or atr_val <= 0:
                logger.error(f"Invalid price inputs: price={current_price}, atr={atr_val}")
                raise ValueError("Invalid price or ATR values")

            effective_bias = detailed_bias
            if effective_bias not in ["LONG", "SHORT"]:
                effective_bias = "LONG" if bias_score >= 0 else "SHORT"

            # Volatility-adjusted modifier
            vol_multiplier = 1.0
            if volatility_state == "HIGH VOLATILITY":
                vol_multiplier = 1.35  # Widen stops in high vol to avoid whipsaws
            elif volatility_state == "LOW VOLATILITY":
                vol_multiplier = 0.85  # Tighter stops in calm markets
            elif volatility_state == "EXTREME VOLATILITY":
                vol_multiplier = 1.60

            # Structural influence: strong trend pushes stop further
            trend_factor = 1.0 + (max(0.0, min(100.0, trend_health)) / 200.0)
            bias_factor = 1.0 - (abs(bias_score) / 300.0)

            stop_mult = self.atr_stop_mult * trend_factor * bias_factor * vol_multiplier

            # Ensure structural level is a valid finite float if provided
            valid_structural = structural_level is not None and np.isfinite(structural_level)

            # A12 FIX: targets are now computed as multiples of the ACTUAL stop
            # distance (i.e. real risk), not fixed ATR multiples independent of
            # it. Previously, since the stop can be pulled further out by
            # trend/volatility factors or a structural level (via the min/max
            # below), the realized stop distance could exceed 1x-2x raw ATR,
            # making "conservative" T1 mathematically the worst R:R target
            # (often below 1:1) by construction. Now T1/T2/T3 R:R come out at
            # exactly 1:1 / 2:1 / 3:1 relative to what's actually being risked.
            if effective_bias == "LONG":
                calculated_stop = current_price - (atr_val * stop_mult)
                atr_stop = (
                    min(structural_level, calculated_stop)
                    if valid_structural
                    else calculated_stop
                )

                stop_distance = current_price - atr_stop
                if not np.isfinite(stop_distance) or stop_distance <= 0:
                    # Degenerate case (e.g. structural level sits above price) —
                    # fall back to the raw ATR-based distance so targets never
                    # collapse to current_price.
                    stop_distance = atr_val * self.atr_stop_mult

                target_t1 = current_price + (stop_distance * self.target1_mult)
                target_t2 = current_price + (stop_distance * self.target2_mult)
                target_t3 = current_price + (stop_distance * self.target3_mult)
            else:  # SHORT
                calculated_stop = current_price + (atr_val * stop_mult)
                atr_stop = (
                    max(structural_level, calculated_stop)
                    if valid_structural
                    else calculated_stop
                )

                stop_distance = atr_stop - current_price
                if not np.isfinite(stop_distance) or stop_distance <= 0:
                    stop_distance = atr_val * self.atr_stop_mult

                target_t1 = current_price - (stop_distance * self.target1_mult)
                target_t2 = current_price - (stop_distance * self.target2_mult)
                target_t3 = current_price - (stop_distance * self.target3_mult)

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

    def classify_risk_regime(self, volatility_state: str, stop_distance_pct: float, trend_health: float) -> str:
        """
        Classifies current setup into a distinct risk regime profile.
        """
        if volatility_state == "EXTREME VOLATILITY" or stop_distance_pct > 8.0:
            return "EXTREME RISK"
        elif volatility_state == "HIGH VOLATILITY" or trend_health < 40.0:
            return "HIGH VOLATILITY RISK"
        elif volatility_state == "LOW VOLATILITY" and trend_health >= 70.0:
            return "LOW RISK"
        else:
            return "NORMAL RISK"

    def validate_risk_parameters(
        self,
        current_price: float,
        atr_stop: float,
        volatility_state: str = "NORMAL",
        trend_health: float = 50.0,
        **kwargs
    ) -> Tuple[bool, str]:
        """
        Validates whether risk parameters are within safe operational thresholds.
        """
        try:
            if current_price <= 0 or atr_stop <= 0:
                return False, "Invalid price or stop levels."

            stop_dist_pct = (abs(current_price - atr_stop) / current_price) * 100.0

            if stop_dist_pct > 15.0:
                return False, "Stop distance exceeds maximum allowable threshold (15%)."
            if stop_dist_pct < 0.2:
                return False, "Stop distance too tight (risk of market noise liquidation)."

            risk_regime = self.classify_risk_regime(volatility_state, stop_dist_pct, trend_health)
            if risk_regime == "EXTREME RISK":
                return False, "Risk regime classified as EXTREME RISK."

            return True, "OK"

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
            return False, f"Risk validation error: {str(e)}"
```


=== FILE: models/signal_router.py ===

```python
import os
from typing import Dict, Any, Optional, List
import logging

from core import config, decision_log
from core.panel_render import render_panel
from models.decision_model import DecisionModel

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

            # SEQUENCE ITEM 14: these were the literals "Logs/Charts" and
            # "Logs". config declares both paths, so the router was creating
            # directories the rest of the engine did not write to on any
            # case-sensitive filesystem.
            os.makedirs(config.CHART_DIR, exist_ok=True)
            os.makedirs(config.LOG_DIR, exist_ok=True)

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
    ) -> Dict[str, Any]:
        """
        Convert engine output into a unified trade decision object.
        Pure assembly: all decision logic (final_action, confidence,
        trade_quality, ev, btc_adjusted, explanation) comes from
        self.decision_model.evaluate().
        """
        degradation = list(degradation) if isinstance(degradation, list) else []
        provenance = dict(provenance) if isinstance(provenance, dict) else {}

        try:
            # SEQUENCE ITEM 9a: degradation is passed INTO the decision model
            # rather than stapled onto the object afterwards. Viktor's ruling
            # says a degraded result does not by itself authorize trading, so
            # the model has to know before it decides — an annotation added
            # after the fact would describe a decision already made.
            dm_result = self.decision_model.evaluate(
                bias, trend, structure, entry, risk, macro_bias, btc_context,
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
                    "raw": str(bias.get("raw", "NEUTRAL")),
                    "detailed": str(bias.get("detailed", "NEUTRAL")),
                    "score": float(bias.get("score", 0.0)),
                    "regime": str(bias.get("regime", "NEUTRAL STRUCTURE")),
                    "volatility": str(bias.get("volatility", "NORMAL"))
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
                    "trend_health": float(trend.get("trend_health", 0.0)),
                    "exhaustion": bool(trend.get("trend_exhaustion", False)),
                    "momentum_mode": str(trend.get("momentum_mode", "HEALTHY")),
                    "momentum_divergence": bool(trend.get("momentum_divergence", False)),
                    # New: explicit BULLISH/BEARISH/NEUTRAL direction label
                    # from trend_health.py, passed straight through.
                    "trend_direction": str(trend.get("trend_direction", "NEUTRAL")),
                },

                "structure": {
                    "regime": str(structure.get("regime", "NEUTRAL")),
                    "sequence": str(structure.get("sequence", "NONE")),
                    "hvn": float(structure.get("hvn", 0.0)),
                    "lvn": float(structure.get("lvn", 0.0)),
                    "volume_sentiment": str(structure.get("volume_sentiment", "NEUTRAL VOLUME")),
                    "swing_struct": float(structure.get("swing_struct", exit_data.get("current_price", 0.0)))
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
                    "struct_pts": float(entry.get("struct_pts", 0.0))
                },

                "risk": {
                    "atr_stop": float(risk.get("atr_stop", 0.0)),
                    "targets": (float(targets[0]), float(targets[1]), float(targets[2])),
                    "risk_valid": bool(risk.get("risk_valid", True)),
                    "risk_reason": str(risk.get("risk_reason", "OK")),
                    # ROADMAP LAYER 1 FIX: confidence_score and the two
                    # trade_quality_* fields are now DecisionModel's real,
                    # multi-factor outputs (see models/decision_model.py)
                    # instead of engine_core.py's raw trend_health
                    # passthrough. Field names/paths kept identical so
                    # panel_render.py needs no changes to consume them.
                    "confidence_score": float(confidence),
                    "trade_quality_proposed": float(trade_quality["proposed_entry"]),
                    "validation_state": str(risk.get("validation_state", "NEUTRAL")),
                    "validation_score": float(risk.get("validation_score", 50.0)),
                    "validation_note": str(risk.get("validation_note", "Standard validation review.")),

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

                # Filled in below, after the log is written. Empty string means
                # nothing was logged, and the panel prints no claim.
                "decision_log_path": "",

                "chart_path": str(chart_path)
            }

        except Exception as e:
            logger.error(f"Failed to build decision object layout: {e}")
            return {
                "symbol": symbol,
                "timeframe": timeframe,
                "error": f"Decision object construction failed: {str(e)}"
            }

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
            "raw": str(btc_context.get("raw", "NEUTRAL")),
            "detailed": str(btc_context.get("detailed", "NEUTRAL")),
            "regime": str(btc_context.get("regime", "NEUTRAL STRUCTURE")),
            "volatility": str(btc_context.get("volatility", "NORMAL")),
            "trend_health": float(btc_context.get("trend_health", 0.0)),
            "correlation": float(btc_context.get("correlation", 0.0)),
            "correlation_label": str(btc_context.get("correlation_label", "WEAK / NO CLEAR RELATIONSHIP")),
            "beta": float(btc_context.get("beta", 0.0)),
            "broad_market_stress": bool(btc_context.get("broad_market_stress", False)),
            "n_observations": int(btc_context.get("n_observations", 0) or 0),
            "btc_adjusted_confidence": float(btc_adjusted.get("btc_adjusted_confidence", 0.0)),
            "reasons": list(btc_adjusted.get("reasons", [])),
        }
```


=== FILE: structure/__init__.py ===

```python

```


=== FILE: structure/structure.py ===

```python
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, Optional, List, TypedDict

from indicators.volume_profile import compute_volume_profile

# Step 8: Formal Return Contract Type Definition for strict static analysis
class StructureAnalysisResult(TypedDict):
    regime: str
    sequence: str
    hvn: float
    lvn: float
    swing_struct: float
    volume_sentiment: str
    df: Optional[pd.DataFrame]


class StructureEngine:
    """
    Phase‑7 Structure + Volume Sentiment Engine
    Fully vectorized with NumPy/Pandas optimizations, input validation,
    localized exception isolation, advanced adaptive lookbacks, hysteresis state machine,
    advanced volume sentiment metrics, and strict typing contracts.
    """

    def __init__(self, volume_profile_bins: int = 50) -> None:
        # State tracking for regime persistence to reduce whipsaws
        self._last_regime: str = "NEUTRAL STRUCTURE"
        self._volume_profile_bins: int = volume_profile_bins

    # ============================================================
    # MAIN STRUCTURE + VOLUME SENTIMENT ENGINE
    # ============================================================

    def analyze(self, df: pd.DataFrame, current_price: float, lookback: int = 8) -> Dict[str, Any]:
        """
        Main structure engine entry point with localized sub-routine error handling.
        Returns structure regime, sequence, HVN/LVN, swing structure, and volume sentiment.
        """
        # Improvement 4: Localized Exception Handling for Sub-Routines
        try:
            regime = self._detect_regime(df)
        except Exception:
            regime = self._last_regime

        try:
            sequence = self._detect_sequence(df, lookback=lookback)
        except Exception:
            sequence = "NONE"

        try:
            hvn, lvn = self._detect_hvn_lvn(df)
        except Exception:
            hvn, lvn = float(current_price), float(current_price)

        try:
            swing_struct = self._detect_swing_structure(df, current_price, lookback=lookback)
        except Exception:
            swing_struct = float(current_price)

        try:
            volume_sentiment = self._volume_sentiment_simple(df)
        except Exception:
            volume_sentiment = "NEUTRAL VOLUME"

        return {
            "regime": regime,
            "sequence": sequence,
            "hvn": hvn,
            "lvn": lvn,
            "swing_struct": swing_struct,
            "volume_sentiment": volume_sentiment
        }

    # ============================================================
    # STRUCTURE DETECTION & STATE MANAGEMENT
    # ============================================================

    def _detect_regime(self, df: pd.DataFrame) -> str:
        """
        Improvement 6: State Machine for Market Regimes with Hysteresis.
        Prevents whipsaws during choppy consolidation phases by introducing state persistence.
        """
        if df is None or len(df) < 15:
            return self._last_regime

        closes = df['close'].values
        ma_short = closes[-5:].mean()
        ma_long = closes[-15:].mean()

        gap_pct = (ma_short - ma_long) / ma_long
        threshold = 0.0015  # 0.15% buffer zone to avoid false triggers

        current_state = self._last_regime

        if current_state == "BULLISH TREND":
            if gap_pct < -threshold:
                new_state = "BEARISH TREND"
            elif gap_pct < 0:
                new_state = "NEUTRAL STRUCTURE"
            else:
                new_state = "BULLISH TREND"
        elif current_state == "BEARISH TREND":
            if gap_pct > threshold:
                new_state = "BULLISH TREND"
            elif gap_pct > 0:
                new_state = "NEUTRAL STRUCTURE"
            else:
                new_state = "BEARISH TREND"
        else:
            if gap_pct > threshold:
                new_state = "BULLISH TREND"
            elif gap_pct < -threshold:
                new_state = "BEARISH TREND"
            else:
                new_state = "NEUTRAL STRUCTURE"

        self._last_regime = new_state
        return new_state

    # ============================================================
    # B2 BUILD: SWING-HIGH/LOW PIVOTS (shared by sequence detection
    # and swing-structure level detection below)
    # ============================================================
    #
    # A confirmed swing high is a bar whose high is the most extreme value
    # within `lookback` bars on BOTH sides of it. Because we only have data
    # up to "now," a pivot can't be confirmed until `lookback` bars of price
    # action have passed after it -- so only bars at least `lookback` back
    # from the most recent bar are eligible. This is standard fractal-pivot
    # detection, matching the "(Lookback 8)" already labeled on the panel's
    # SWING STRUCT line (that label previously described a stub that just
    # returned current_price unchanged -- it's now real).

    def _find_confirmed_swings(
        self,
        highs: np.ndarray,
        lows: np.ndarray,
        lookback: int,
        max_each: int = 2,
        search_limit: int = 200,
    ) -> Tuple[List[Tuple[int, float]], List[Tuple[int, float]]]:
        """
        Scans backward from the most recent confirmable bar and returns up to
        `max_each` confirmed swing highs and swing lows, each as (index, price),
        most recent first. Accepted pivots are required to be at least
        `lookback` bars apart so one flat-topped/bottomed cluster of bars
        doesn't get counted as several separate swing points.
        """
        n = len(highs)
        swing_highs: List[Tuple[int, float]] = []
        swing_lows: List[Tuple[int, float]] = []
        last_high_idx: Optional[int] = None
        last_low_idx: Optional[int] = None

        search_start = n - 1 - lookback
        search_end = max(lookback, search_start - search_limit)

        for i in range(search_start, search_end - 1, -1):
            if i - lookback < 0 or i + lookback >= n:
                continue

            # Minimum spacing between two ACCEPTED pivots is 2x lookback, not
            # just lookback -- two adjacent lookback-windows can otherwise
            # both "win" on the same flat-topped/bottomed cluster of bars
            # (e.g. a multi-bar consolidation at the same level), which would
            # misread one plateau as two separate swings and never let the
            # comparison logic below see a genuinely new extreme.
            if len(swing_highs) < max_each:
                window_high = highs[i - lookback: i + lookback + 1]
                if highs[i] == window_high.max() and (last_high_idx is None or last_high_idx - i >= 2 * lookback):
                    swing_highs.append((i, float(highs[i])))
                    last_high_idx = i

            if len(swing_lows) < max_each:
                window_low = lows[i - lookback: i + lookback + 1]
                if lows[i] == window_low.min() and (last_low_idx is None or last_low_idx - i >= 2 * lookback):
                    swing_lows.append((i, float(lows[i])))
                    last_low_idx = i

            if len(swing_highs) >= max_each and len(swing_lows) >= max_each:
                break

        return swing_highs, swing_lows

    def _detect_sequence(self, df: pd.DataFrame, lookback: int = 8) -> str:
        """
        B2 BUILD (was a stub always returning "NONE"). Real swing-sequence /
        BOS ("break of structure") / CHOCH ("change of character") detection.

        Looks at the two most recent confirmed swing highs and swing lows to
        classify the swing sequence, then checks whether the CURRENT price
        has broken through the most recent confirmed swing extreme:

          BULLISH SWING SEQUENCE (HH-HL) -- higher highs & higher lows, no
                                             break of the last swing high yet
          BEARISH SWING SEQUENCE (LH-LL) -- lower highs & lower lows, no
                                             break of the last swing low yet
          BOS BULLISH / BOS BEARISH      -- price breaks the last swing
                                             extreme IN the direction the
                                             sequence was already going
                                             (trend continuation)
          CHOCH BULLISH / CHOCH BEARISH  -- price breaks the last swing
                                             extreme AGAINST the direction
                                             the sequence was going (the
                                             first sign of a possible
                                             reversal)
          NONE -- not enough confirmed swing points yet, or highs/lows
                  disagree on direction (e.g. higher highs but lower lows)
        """
        if df is None or len(df) < (6 * lookback + 10):
            return "NONE"

        highs = df['high'].values
        lows = df['low'].values
        closes = df['close'].values

        swing_highs, swing_lows = self._find_confirmed_swings(highs, lows, lookback, max_each=2)

        if len(swing_highs) < 2 or len(swing_lows) < 2:
            return "NONE"

        last_high, prev_high = swing_highs[0][1], swing_highs[1][1]
        last_low, prev_low = swing_lows[0][1], swing_lows[1][1]
        current_price = float(closes[-1])

        if last_high > prev_high and last_low > prev_low:
            # Established bullish swing sequence. A break below the last
            # confirmed swing low here would go against that sequence.
            if current_price > last_high:
                return "BOS BULLISH (TREND CONTINUATION)"
            if current_price < last_low:
                return "CHOCH BEARISH (POSSIBLE REVERSAL)"
            return "BULLISH SWING SEQUENCE (HH-HL)"

        if last_high < prev_high and last_low < prev_low:
            # Established bearish swing sequence. A break above the last
            # confirmed swing high here would go against that sequence.
            if current_price < last_low:
                return "BOS BEARISH (TREND CONTINUATION)"
            if current_price > last_high:
                return "CHOCH BULLISH (POSSIBLE REVERSAL)"
            return "BEARISH SWING SEQUENCE (LH-LL)"

        # Mixed (e.g. higher highs but lower lows) -- no clean sequence.
        return "NONE"

    def _detect_hvn_lvn(self, df: pd.DataFrame) -> Tuple[float, float]:
        """
        A11 FIX: Primary HVN/LVN source is now the real binned volume-profile
        engine (compute_volume_profile), which distributes actual traded
        volume proportionally across price bins. This replaces the previous
        approach of using the high/low extremes of an adaptive lookback
        window, which measured price range, not where volume actually traded.

        Falls back to the old adaptive-lookback method only if the volume
        profile can't be computed or returns no usable result, so behavior
        degrades gracefully instead of failing outright.
        """
        if df is None or df.empty:
            return 0.0, 0.0

        try:
            _, hvn, lvn = compute_volume_profile(df, num_bins=self._volume_profile_bins)
            if hvn is not None and lvn is not None and np.isfinite(hvn) and np.isfinite(lvn):
                return float(hvn), float(lvn)
        except Exception:
            pass  # fall through to legacy method below

        # ------------------------------------------------------------
        # LEGACY FALLBACK: adaptive TR-based high/low window
        # ------------------------------------------------------------
        high_values = df['high'].values
        low_values = df['low'].values
        close_values = df['close'].values
        df_len = len(df)

        if df_len > 14:
            prev_closes = np.roll(close_values, 1)
            prev_closes[0] = close_values[0]
            tr = np.maximum(
                high_values - low_values,
                np.maximum(np.abs(high_values - prev_closes), np.abs(low_values - prev_closes))
            )

            recent_tr = np.mean(tr[-14:])
            recent_price = close_values[-1]

            vol_pct = (recent_tr / recent_price) if recent_price > 0 else 0.01
            base_lookback = 20
            vol_factor = vol_pct / 0.01
            adaptive_window = int(base_lookback / max(0.5, min(2.0, vol_factor)))

            lookback = max(5, min(df_len, adaptive_window))
        else:
            lookback = df_len

        hvn = float(high_values[-lookback:].max())
        lvn = float(low_values[-lookback:].min())
        return hvn, lvn

    def _detect_swing_structure(self, df: pd.DataFrame, current_price: float, lookback: int = 8) -> float:
        """
        B2 BUILD (was a stub always returning current_price unchanged).

        Returns the nearest confirmed swing high or swing low to the current
        price -- the closest real structural reference level for manual
        stop/target planning. (structure.py doesn't yet know the intended
        trade direction at this point in engine_core.py's pipeline -- the
        bias engine runs after this -- so this returns whichever confirmed
        swing point is closest, rather than picking "support" vs.
        "resistance" by direction.)
        """
        if df is None or len(df) < (2 * lookback + 5):
            return float(current_price)

        highs = df['high'].values
        lows = df['low'].values

        swing_highs, swing_lows = self._find_confirmed_swings(highs, lows, lookback, max_each=1)

        if not swing_highs and not swing_lows:
            return float(current_price)
        if not swing_highs:
            return float(swing_lows[0][1])
        if not swing_lows:
            return float(swing_highs[0][1])

        nearest_high = swing_highs[0][1]
        nearest_low = swing_lows[0][1]
        if abs(nearest_high - current_price) <= abs(nearest_low - current_price):
            return float(nearest_high)
        return float(nearest_low)

    # ============================================================
    # ADVANCED VOLUME SENTIMENT ENGINE
    # ============================================================

    def _volume_sentiment_simple(self, df: pd.DataFrame) -> str:
        """
        Improvement 2 & 7: Advanced Volume Sentiment Metrics with participation expansion
        and institutional accumulation/distribution detection.
        """
        if df is None or len(df) < 20:
            return "NEUTRAL VOLUME"

        closes = df["close"].values
        volumes = df["volume"].values

        c_recent, c_prev = closes[-5:], closes[-10:-5]
        v_recent, v_prev = volumes[-5:], volumes[-10:-5]

        try:
            vwma_recent = np.average(c_recent, weights=v_recent)
            vwma_prev = np.average(c_prev, weights=v_prev)
        except ZeroDivisionError:
            vwma_recent = c_recent.mean()
            vwma_prev = c_prev.mean()

        vwma_slope = vwma_recent - vwma_prev
        price_slope = closes[-1] - closes[-5]
        vol_slope = volumes[-1] - volumes[-5]

        vma_baseline = volumes[-20:].mean()
        recent_vol_mean = volumes[-5:].mean()
        volume_expansion = recent_vol_mean > (1.2 * vma_baseline)

        if vwma_slope > 0 and volume_expansion and price_slope > 0:
            return "STRONG BULLISH ACCUMULATION"

        if vwma_slope > 0 and vol_slope > 0 and price_slope > 0:
            return "BULLISH VOLUME SUPPORT"

        if vwma_slope < 0 and volume_expansion and price_slope < 0:
            return "STRONG BEARISH DISTRIBUTION"

        if vwma_slope < 0 and vol_slope > 0 and price_slope < 0:
            return "BEARISH VOLUME PRESSURE"

        if (price_slope > 0 and vol_slope < 0 and not volume_expansion) or \
           (price_slope < 0 and vol_slope < 0 and not volume_expansion):
            return "VOLUME DIVERGENCE"

        if volume_expansion and abs(price_slope) < (0.001 * closes[-1]):
            return "VOLUME EXHAUSTION"

        return "NEUTRAL VOLUME"


# ============================================================
# ENGINE COMPATIBILITY WRAPPER
# ============================================================

def calculate_structure(df: Optional[pd.DataFrame], lookback: int = 8,
                        volume_profile_bins: int = 50) -> Dict[str, Any]:
    """
    Compatibility wrapper function with strict input validation, vectorized NaN
    cleaning, and formal typing contracts for engine_core.py.

    SEQUENCE ITEM 6: the `copy_df` parameter is gone. This function always works
    on its own copy now.

    It defaulted to True, and both call sites in engine_core passed False — so
    the safe default was documented and never taken. Under it, `df_clean = df`
    and this function then wrote STRUCTURE, HVN and LVN into the caller's frame
    and ffill/bfill/fillna(0.0)'d its OHLCV columns. The caller's `df` and the
    `df` returned in this dict were one object under two names.

    The parameter is removed rather than merely left at its default, because a
    knob whose unsafe setting is the one everybody chooses is not a safeguard.
    Nothing outside engine_core called this, so there is no compatibility cost.

    Cost of always copying: one 450-row frame per call, twice per run. Measured
    against the class of bug it removes, that is not a trade worth making.
    """
    if df is None or df.empty:
        return {
            "regime": "NEUTRAL STRUCTURE",
            "sequence": "NONE",
            "hvn": 0.0,
            "lvn": 0.0,
            "swing_struct": 0.0,
            "volume_sentiment": "NEUTRAL VOLUME",
            "df": df
        }

    required_cols = ['open', 'high', 'low', 'close', 'volume']
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"StructureEngine requires missing column: '{col}'")

    df_clean = df.copy()

    # SEQUENCE ITEM 15: was .ffill().bfill().fillna(0.0). The backfill took
    # OHLCV values from later bars; the fillna(0.0) put a price of zero on any
    # gap that survived, and the very next line reads close.iloc[-1] as the
    # current price. Forward only, and a gap that a forward fill cannot close
    # is reported rather than papered over — data/validation.py rejects NaN
    # OHLCV upstream, so reaching this means the frame did not come through the
    # fetcher.
    df_clean.loc[:, required_cols] = df_clean[required_cols].ffill()

    still_missing = [c for c in required_cols if df_clean[c].isna().any()]
    if still_missing:
        raise ValueError(
            f"StructureEngine received gaps a forward fill cannot close in: "
            f"{', '.join(still_missing)}. Filling these with zero would make "
            f"the structural analysis and the current price read from bars "
            f"that never traded."
        )

    current_price = float(df_clean['close'].iloc[-1])

    # SEQUENCE ITEM 14: StructureEngine was constructed with no arguments, so
    # its volume_profile_bins defaulted to 50 and config.VOLUME_PROFILE_BINS —
    # also 50 — was read by nothing. Two copies of one number, one of them
    # labelled as the setting and neither of them consulted.
    engine = StructureEngine(volume_profile_bins=volume_profile_bins)
    # B2 FIX: `lookback` was accepted by this wrapper's signature but never
    # actually passed down to the engine -- analyze() didn't even take a
    # lookback parameter, so the "(Lookback 8)" already shown on the panel's
    # SWING STRUCT line was aspirational text next to a stub. Now real.
    result = engine.analyze(df_clean, current_price, lookback=lookback)

    df_clean.loc[:, "STRUCTURE"] = result.get("regime", "NEUTRAL STRUCTURE")
    df_clean.loc[:, "HVN"] = result.get("hvn", 0.0)
    df_clean.loc[:, "LVN"] = result.get("lvn", 0.0)

    result["df"] = df_clean

    return result
```


=== FILE: utils/__init__.py ===

```python

```


=== FILE: utils/plotting.py ===

```python
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import logging
import os
import numpy as np

from core import config

logger = logging.getLogger(__name__)

def plot_engine_chart(df, entry_data, risk_data, save_path="chart_output.png"):
    """
    Modular Phase‑7 chart renderer with comprehensive error handling.
    Draws:
        - Candles
        - EMA20 / EMA50
        - Entry zone shading
        - ATR stop
        - Targets T1 / T2 / T3
    
    Returns:
        str: Path to saved chart or None if failed
    """
    
    try:
        # Validate inputs
        if df is None or df.empty:
            logger.error("Cannot plot chart: DataFrame is None or empty")
            return None
            
        if not isinstance(entry_data, dict) or not isinstance(risk_data, dict):
            logger.error("Cannot plot chart: entry_data or risk_data is not a dictionary")
            return None
            
        required_cols = ["open", "high", "low", "close"]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            logger.error(f"Cannot plot chart: missing required columns {missing_cols}")
            return None
            
        # Ensure save directory exists
        save_dir = os.path.dirname(save_path)
        if save_dir:
            os.makedirs(save_dir, exist_ok=True)

        # SEQUENCE ITEM 14: style, figure size and dpi were hardcoded here
        # while config.py declared CHART_STYLE, CHART_WIDTH, CHART_HEIGHT and
        # CHART_DPI, read by nothing. Two of the four disagreed with what this
        # file actually did (height 10 vs 8, dpi 150 vs 200); config was
        # corrected to the behaviour in use, so this change draws an identical
        # chart and makes those four constants live.
        try:
            plt.style.use(config.CHART_STYLE)
        except Exception:
            logger.warning(f"Could not set {config.CHART_STYLE} style, using default")

        fig, ax = plt.subplots(figsize=(config.CHART_WIDTH, config.CHART_HEIGHT))
    except Exception as e:
        logger.error(f"Failed to initialize matplotlib figure: {e}")
        return None

    try:
        # ============================================================
        # CANDLE PLOTTING WITH ERROR HANDLING
        # ============================================================

        # Validate price data
        #
        # SEQUENCE ITEM 6: this loop used to fill NaNs directly in the caller's
        # frame. engine_core passes df_struct here, so a chart renderer was
        # silently editing the frame the analysis had just been computed from.
        # Harmless in practice only because plotting runs last — which is a
        # statement about the current call order, not about the code.
        df = df.copy()
        price_cols = ["open", "high", "low", "close"]
        for col in price_cols:
            if df[col].isna().any():
                logger.warning(f"NaN values found in {col}, filling with forward fill")
                # Was fillna(method='ffill').fillna(method='bfill'). The
                # `method` keyword was deprecated in pandas 2.1 and removed
                # since; on the installed version this line raised TypeError:
                # "NDFrame.fillna() got an unexpected keyword argument
                # 'method'". The outer try caught it, logged "Failed to plot
                # candlesticks", and the chart rendered with EMAs, entry zone,
                # stop and targets but NO PRICE CANDLES.
                #
                # It had never been observed because the branch only runs when
                # a NaN reaches the plotter, and nothing NaN-shaped survives
                # add_technical_indicators. Found 30 August by the test-runner
                # change, which stopped discarding the output of passing tests.
                #
                # Same class as the dead gates recorded elsewhere in this
                # project: a repair path that has never been exercised and does
                # not work.
                # SEQUENCE ITEM 15 deliberately leaves the backfill here.
                # This module draws a picture; it feeds no decision, and a
                # chart with a hole at the left edge is less readable without
                # being more truthful. Every other .bfill() in the engine was
                # removed under Item 2, and this one is listed as the exception
                # in tests/test_no_lookahead.py so that it stays a decision
                # rather than an oversight.
                df[col] = df[col].ffill().bfill()

        up = df[df["close"] >= df["open"]]
        down = df[df["close"] < df["open"]]

        # Candle wicks with error handling
        if not up.empty:
            try:
                ax.vlines(up.index, up["low"], up["high"], color="#22c55e", linewidth=1)
            except Exception as e:
                logger.warning(f"Failed to plot up candle wicks: {e}")
                
        if not down.empty:
            try:
                ax.vlines(down.index, down["low"], down["high"], color="#ef4444", linewidth=1)
            except Exception as e:
                logger.warning(f"Failed to plot down candle wicks: {e}")

        # Candle bodies with error handling
        if not up.empty:
            try:
                ax.bar(
                    up.index,
                    up["close"] - up["open"],
                    bottom=up["open"],
                    width=0.0008,
                    color="#22c55e"
                )
            except Exception as e:
                logger.warning(f"Failed to plot up candle bodies: {e}")

        if not down.empty:
            try:
                ax.bar(
                    down.index,
                    down["open"] - down["close"],
                    bottom=down["close"],
                    width=0.0008,
                    color="#ef4444"
                )
            except Exception as e:
                logger.warning(f"Failed to plot down candle bodies: {e}")
                
    except Exception as e:
        logger.error(f"Failed to plot candlesticks: {e}")
        # Continue with other chart elements

    try:
        # ============================================================
        # EMA OVERLAYS WITH ERROR HANDLING
        # ============================================================
        #
        # SEQUENCE ITEM 5a: the VWAP branch that used to sit below was
        # unreachable. Nothing in the engine ever assigns df["VWAP"] —
        # verified by searching every module for an assignment — so
        # `if "VWAP" in df.columns` was always False and the plot call inside
        # it had never executed. It read as a feature and was a no-op.
        #
        # This is the same shape as the dead gates recorded elsewhere in the
        # project: a guard testing for something no producer emits. Worth
        # noticing that a reader of this file would reasonably have believed
        # the chart could show VWAP.

        if "EMA_20" in df.columns and not df["EMA_20"].isna().all():
            try:
                ax.plot(df.index, df["EMA_20"], label="EMA20", color="#f59e0b", linewidth=1.4)
            except Exception as e:
                logger.warning(f"Failed to plot EMA_20: {e}")
                
        if "EMA_50" in df.columns and not df["EMA_50"].isna().all():
            try:
                ax.plot(df.index, df["EMA_50"], label="EMA50", color="#a855f7", linewidth=1.4)
            except Exception as e:
                logger.warning(f"Failed to plot EMA_50: {e}")

    except Exception as e:
        logger.error(f"Failed to plot indicators: {e}")

    try:
        # ============================================================
        # ENTRY ZONE SHADING WITH ERROR HANDLING
        # ============================================================

        entry_zone_lower = entry_data.get("entry_zone_lower")
        entry_zone_upper = entry_data.get("entry_zone_upper")

        if entry_zone_lower is not None and entry_zone_upper is not None:
            if np.isfinite(entry_zone_lower) and np.isfinite(entry_zone_upper):
                try:
                    ax.axhspan(
                        entry_zone_lower,
                        entry_zone_upper,
                        color="yellow",
                        alpha=0.12,
                        label="Entry Zone"
                    )
                except Exception as e:
                    logger.warning(f"Failed to plot entry zone: {e}")
            else:
                logger.warning("Entry zone values are not finite, skipping entry zone plot")
        else:
            logger.warning("Entry zone data missing, skipping entry zone plot")

    except Exception as e:
        logger.error(f"Failed to process entry zone: {e}")

    try:
        # ============================================================
        # ATR STOP & TARGETS WITH ERROR HANDLING
        # ============================================================

        atr_stop = risk_data.get("atr_stop")
        targets = risk_data.get("targets", (None, None, None))
        
        if len(targets) >= 3:
            t1, t2, t3 = targets[:3]
        else:
            t1, t2, t3 = None, None, None

        if atr_stop is not None and np.isfinite(atr_stop):
            try:
                ax.axhline(atr_stop, color="red", linestyle="--", linewidth=1.2, label="ATR Stop")
            except Exception as e:
                logger.warning(f"Failed to plot ATR stop: {e}")
        else:
            logger.warning("ATR stop value invalid, skipping ATR stop plot")

        for i, (target, label, color) in enumerate([(t1, "T1", "green"), (t2, "T2", "lime"), (t3, "T3", "darkgreen")]):
            if target is not None and np.isfinite(target):
                try:
                    ax.axhline(target, color=color, linestyle="--", linewidth=1.2, label=label)
                except Exception as e:
                    logger.warning(f"Failed to plot target {label}: {e}")
            else:
                logger.warning(f"Target {label} value invalid, skipping")

    except Exception as e:
        logger.error(f"Failed to process risk levels: {e}")

    try:
        # ============================================================
        # CHART FORMATTING WITH ERROR HANDLING
        # ============================================================

        try:
            ax.set_title("Phase‑7 Structural Quant Engine — Market Structure & Signals", fontsize=14)
        except Exception as e:
            logger.warning(f"Failed to set chart title: {e}")
            
        try:
            ax.grid(True, alpha=0.25)
        except Exception as e:
            logger.warning(f"Failed to set grid: {e}")
            
        try:
            ax.legend(loc="upper left")
        except Exception as e:
            logger.warning(f"Failed to set legend: {e}")

        # Date formatting with error handling
        try:
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
            fig.autofmt_xdate()
        except Exception as e:
            logger.warning(f"Failed to format dates: {e}")

        try:
            plt.tight_layout()
        except Exception as e:
            logger.warning(f"Failed to apply tight layout: {e}")
            
        try:
            plt.savefig(save_path, dpi=config.CHART_DPI, bbox_inches='tight')
            logger.info(f"Chart successfully saved to {save_path}")
        except Exception as e:
            logger.error(f"Failed to save chart to {save_path}: {e}")
            return None
        finally:
            try:
                plt.close()
            except Exception as e:
                logger.warning(f"Failed to close matplotlib figure: {e}")

        return save_path
        
    except Exception as e:
        logger.error(f"Failed to format and save chart: {e}")
        try:
            plt.close()
        except Exception:
            pass
        return None

```


=== FILE: main.py ===

```python
import sys
import os
import logging

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Log directories must exist before anything opens a file inside them.
# logging.FileHandler opens its file at construction, not at first write, so
# the basicConfig call below raises FileNotFoundError during import on any
# machine where the log directory does not already exist — before main() runs,
# and so outside the reach of the try/except inside it. This never appeared on
# the development machine, where it has existed since the first run; it appears
# for anyone cloning the repository.
#
# Placed here rather than immediately above basicConfig because module-scope
# code in the import chain can also touch the filesystem.
#
# SEQUENCE ITEM 14: config is imported first so the directory and the log file
# both come from config.LOG_DIR. They were the literals 'Logs' and
# 'Logs/phase7_engine.log', naming a directory .gitignore does not ignore — so
# on Linux the engine's own log file was offered for commit on any clone.
from core import config

os.makedirs(config.LOG_DIR, exist_ok=True)

from models.signal_router import SignalRouter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(config.LOG_DIR, 'phase7_engine.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def main():
    """
    Main entry point for Phase-7 Structural Quant Engine.
    Returns 0 for success, 1 for failure.
    """
    try:
        # Validate required configuration
        if not hasattr(config, 'SYMBOL') or not config.SYMBOL:
            logger.error("Missing or empty config.SYMBOL")
            return 1
            
        if not hasattr(config, 'TIMEFRAME') or not config.TIMEFRAME:
            logger.error("Missing or empty config.TIMEFRAME")
            return 1
            
        logger.info(f"Starting Phase-7 engine for {config.SYMBOL} on {config.TIMEFRAME}")
        
        # Ensure log directory exists
        os.makedirs('Logs', exist_ok=True)
        
        router = SignalRouter()

        # Run engine using default config values with exception handling
        decision = router.route(
            symbol=config.SYMBOL,
            timeframe=config.TIMEFRAME
        )
        
        # Check for errors in the decision object
        if decision and "error" in decision:
            logger.error(f"Engine returned error: {decision['error']}")
            return 1
            
        logger.info("Phase-7 engine completed successfully")
        return 0
        
    except ImportError as e:
        logger.error(f"Failed to import required modules: {e}")
        return 1
    except AttributeError as e:
        logger.error(f"Configuration error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error in main execution: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

```


=== FILE: live_trading.py ===

```python
import datetime
import os
import json

from models.signal_router import SignalRouter
from core import config


class LiveTradingSimulator:
    """
    SAFE live-trading wrapper for Phase-7.
    This module:
        - Runs the engine (via SignalRouter, the same entry point main.py uses)
        - Generates a simulated order object
        - Logs the intended trade
        - NEVER executes real trades

    FIX (previously broken): this used to `from engine_core import
    phase7_engine` and call that singleton directly -- but no such singleton
    ever existed (only the `Phase7Engine` class does), so this crashed on
    import. Even setting that aside, calling the engine directly like that
    would have bypassed SignalRouter entirely, meaning it would've gotten
    the raw, pre-DecisionModel engine output -- no real confidence score,
    no final_action, no BTC context, none of what the panel actually shows
    you. This is now rewired to go through SignalRouter.route_and_execute(),
    exactly like main.py does, so a simulated order always reflects the
    exact same decision the panel would render for that run.

    Also fixed: a few field names this read no longer matched the current
    decision object's actual shape (entry_zone_lower/upper -> zone_lower/
    upper, exit.final_action -> exit.action) -- these would have raised
    KeyErrors the moment the import itself was fixed.
    """

    # SEQUENCE ITEM 14: the default was the literal "Logs/LiveSim/". It is
    # derived from config.LOG_DIR now, so the simulator writes beside the rest
    # of the engine's output instead of into a directory that differs from it
    # by case on Linux.
    def __init__(self, log_dir=None):
        self.log_dir = log_dir if log_dir is not None else os.path.join(
            config.LOG_DIR, "LiveSim")
        os.makedirs(self.log_dir, exist_ok=True)
        self.router = SignalRouter()

    # ============================================================
    # RUN ENGINE + GENERATE SIMULATED ORDER
    # ============================================================

    def run_once(self, symbol=None, timeframe=None):
        """
        Run the engine once (through SignalRouter, same path main.py uses)
        and generate a simulated trade object -- never a real one.

        Falls back to config.py's SYMBOL/TIMEFRAME if not given, matching
        main.py's behavior. SignalRouter.route_and_execute() itself requires
        both to be given explicitly and does NOT apply config defaults on
        its own, so that fallback has to happen here.
        """
        symbol = symbol or config.SYMBOL
        timeframe = timeframe or config.TIMEFRAME

        result = self.router.route_and_execute(symbol, timeframe)

        # SignalRouter already renders the panel itself -- this just needs
        # to know whether the run succeeded before trying to build an order
        # from it. An error result has no entry/risk/exit sections to read.
        if not isinstance(result, dict) or "error" in result:
            error_message = (
                result.get("error", "Unknown engine error")
                if isinstance(result, dict) else "Engine returned invalid output"
            )
            return {
                "engine_result": result,
                "simulated_order": None,
                "log_path": None,
                "error": error_message,
            }

        # Build simulated order
        order = self._build_simulated_order(result)

        # Log simulated trade
        filepath = self._log_simulated_trade(order)

        return {
            "engine_result": result,
            "simulated_order": order,
            "log_path": filepath
        }

    # ============================================================
    # BUILD SIMULATED ORDER OBJECT
    # ============================================================

    def _build_simulated_order(self, result):
        """
        Convert engine output into a safe simulated order object.
        """

        entry = result.get("entry", {}) if isinstance(result.get("entry"), dict) else {}
        risk = result.get("risk", {}) if isinstance(result.get("risk"), dict) else {}
        exit_data = result.get("exit", {}) if isinstance(result.get("exit"), dict) else {}

        order = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "symbol": result.get("symbol", "UNKNOWN"),
            "timeframe": result.get("timeframe", "UNKNOWN"),
            "decision": exit_data.get("action", "UNKNOWN"),
            "entry_zone": {
                "lower": entry.get("zone_lower", 0.0),
                "upper": entry.get("zone_upper", 0.0)
            },
            "risk": {
                "atr_stop": risk.get("atr_stop", 0.0),
                "targets": risk.get("targets", (0.0, 0.0, 0.0)),
                "risk_valid": risk.get("risk_valid", True),
                "risk_reason": risk.get("risk_reason", "OK")
            },
            "signals": {
                "long_signal": entry.get("long_signal", False),
                "short_signal": entry.get("short_signal", False)
            },
            "current_price": exit_data.get("current_price", 0.0),
            "note": "This is a simulated order. No real trading occurs."
        }

        return order

    # ============================================================
    # LOGGING
    # ============================================================

    def _log_simulated_trade(self, order):
        """
        Save simulated trade to JSON file.
        """

        timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
        filepath = os.path.join(self.log_dir, f"sim_trade_{timestamp}.json")

        with open(filepath, "w") as f:
            json.dump(order, f, indent=4)

        return filepath


# ============================================================
# GLOBAL SAFE LIVE-TRADING SIMULATOR
# ============================================================

live_trading_simulator = LiveTradingSimulator()
```


=== FILE: requirements.txt ===

```
pandas
numpy
matplotlib
pandas_ta
requests
colorama

```
