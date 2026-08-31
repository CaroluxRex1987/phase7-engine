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
    # ITEM 14 RE-AUDIT (Finding 5): risk_model.classify_risk_regime() always
    # computed this; only a boolean comparison against "EXTREME RISK" used to
    # reach risk_valid above. decision_model.py now reads the regime itself
    # to gate the AGGRESSIVE action label independently of trend health and
    # entry quality.
    risk_regime: str
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
