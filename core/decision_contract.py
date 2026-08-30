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

KNOWN DEFECTS THIS DECLARATION RECORDS RATHER THAN FIXES

Declaring a shape honestly means declaring the parts of it that are wrong.

  trend.health          duplicates trend.trend_health
  trend.momentum        duplicates trend.momentum_mode

Two names for one value, twice, with nothing saying which is canonical. Same
shape as the risk_score / signal_strength aliasing already scheduled for
sequence item 13. CANONICAL_ALIASES below names the survivor of each pair so
that new code has an answer; removing the duplicates is a field change and
belongs with item 13's, under item 13's verification.

  risk.position_size, position_value, risk_amount,
  account_balance, risk_percent

Viktor ruled on 29 August that the engine must not compute monetary position
sizing at all. These five are declared because they are currently produced, and
they are scheduled for removal at sequence item 13. When that lands, they come
out of here in the same commit — that is the contract doing its job.
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
    health: float                 # duplicate of trend_health — see module docstring
    trend_health: float
    failure: bool
    exhaustion: bool
    momentum: str                 # duplicate of momentum_mode
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
    risk_score: float
    confidence_score: float
    signal_strength: float
    trade_quality_current: float
    trade_quality_proposed: float
    validation_state: str
    validation_score: float
    validation_note: str
    # Scheduled for removal at sequence item 13 — see module docstring.
    position_size: float
    position_value: float
    risk_amount: float
    account_balance: float
    risk_percent: float
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
# New code reads the canonical name; the duplicate is removed at sequence
# item 13, when a field change is in scope and has verification attached.

CANONICAL_ALIASES = {
    ("trend", "health"): "trend_health",
    ("trend", "momentum"): "momentum_mode",
}


# ============================================================
# Fields whose removal is already scheduled
# ============================================================
#
# Declared because they are produced today. Listed here so that when sequence
# item 13 removes them, the contract test fails until this file is updated in
# the same commit — which is the whole point of having a contract.

SCHEDULED_FOR_REMOVAL = {
    ("risk", "position_size"): "sequence item 13 — Viktor's position-sizing ruling",
    ("risk", "position_value"): "sequence item 13 — Viktor's position-sizing ruling",
    ("risk", "risk_amount"): "sequence item 13 — Viktor's position-sizing ruling",
    ("risk", "account_balance"): "sequence item 13 — Viktor's position-sizing ruling",
    ("risk", "risk_percent"): "sequence item 13 — Viktor's position-sizing ruling",
}
