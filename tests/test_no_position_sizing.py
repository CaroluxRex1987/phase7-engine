"""
Sequence item 13 — position sizing removed, and the four duplicate fields with
it.

THE RULING

Viktor, 29 August 2026: the engine must not compute `position_size`,
`position_value` or `risk_amount` from an account balance and a risk
percentage. Monetary position sizing belongs outside the Structural Quant
Engine, in the portfolio/execution layer.

WHY A TEST AND NOT JUST A DELETION

A deletion is a fact about today. The engine produced a POSITION SIZE from a
placeholder 10,000 balance for its whole life, and the way that comes back is
not by someone re-adding `calculate_position_size` — it is by a field
reappearing in the decision object because it seemed useful, one name at a
time. So the assertions below are about the output, not about the source: no
block of the decision object may carry a sizing field under any of its names.

The source-level checks that follow are narrower, and one of them exists for a
specific reason: `risk_amount` named two unrelated things in this codebase. In
engine_core it was money — balance times risk percent. In panel_render it was a
price distance,

    risk_amount = abs(current_price - stop_loss)

and it is the denominator of all three R:R ratios. A find-and-replace on the
name would have silently zeroed the panel's R:R display while the rest of the
panel still looked right. The money is gone under the ruling, so the panel's
local is renamed to `stop_distance` in the same commit — the removal of one
side of a name collision is the moment the other side gets fixed, or it never
does. The test asserts the denominator survived the rename and that the old
name does not come back.

THE FOUR DUPLICATES

Item 10 declared them and scheduled them here:

    trend.health          == trend.trend_health
    trend.momentum        == trend.momentum_mode
    risk.risk_score       == bias.score
    risk.signal_strength  == bias.score

The trend pair mattered more than it looks: decision_model.py read
`trend["health"]` FIRST and fell back to `trend["trend_health"]`, so the
canonical field could have been changed with no effect on the decision.
"""

import ast
import os
import pytest

PINNED_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "fixtures", "pinned")
UNREACHABLE = "http://127.0.0.1:1"

# Every name the removed sizing numbers travelled under, in the decision
# object. Checked against every block, not just "risk" — a field moved to
# another block is not a field removed.
SIZING_FIELDS = [
    "position_size",
    "position_value",
    "risk_amount",
    "account_balance",
    "risk_percent",
]

DUPLICATE_FIELDS = {
    "trend": ["health", "momentum"],
    "risk": ["risk_score", "signal_strength"],
}


def _engine_available():
    try:
        import pandas_ta  # noqa: F401
        return True
    except Exception:
        return False


def _run(symbol="AEROUSDT"):
    from data.data_fetcher import DataFetcher, data_fetcher
    from models.signal_router import SignalRouter

    original = data_fetcher.base_url
    try:
        data_fetcher.base_url = UNREACHABLE
        DataFetcher.set_pinned_source(PINNED_DIR)
        return SignalRouter().route(symbol=symbol, timeframe="4h")
    finally:
        DataFetcher.clear_pinned_source()
        data_fetcher.base_url = original


# ============================================================
# The ruling, checked at the output
# ============================================================

def test_no_block_of_the_decision_object_carries_a_sizing_field():
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    decision = _run()
    assert "error" not in decision, decision.get("error")

    found = []
    for block, contents in decision.items():
        if not isinstance(contents, dict):
            continue
        for field in SIZING_FIELDS:
            if field in contents:
                found.append(f"{block}.{field} = {contents[field]!r}")

    assert not found, (
        "the decision object carries monetary position sizing again:\n  "
        + "\n  ".join(found)
        + "\n\nViktor's ruling of 29 August 2026: sizing belongs in the "
          "portfolio/execution layer, which is the only layer that knows the "
          "real balance and the real exposure. A number computed here from a "
          "placeholder balance is an instruction to risk a specific amount."
    )


def test_the_risk_model_has_no_position_sizing_function():
    from models.risk_model import RiskModel

    assert not hasattr(RiskModel, "calculate_position_size"), (
        "RiskModel.calculate_position_size is back. Besides the sizing itself "
        "it carried portfolio policy — a 10x notional cap and 0.5x / 0.8x "
        "volatility haircuts — decided inside an engine that cannot see a "
        "portfolio."
    )


def test_the_placeholder_balance_is_not_in_config():
    from core import config

    for name in ("DEFAULT_ACCOUNT_BALANCE", "DEFAULT_RISK_PERCENT"):
        assert not hasattr(config, name), (
            f"config.{name} is defined again. It was read by exactly one "
            f"caller, the sizing block that is now gone; a placeholder balance "
            f"left in config is an invitation to wire it back up."
        )


def test_the_decision_log_does_not_fingerprint_a_balance():
    """
    The log records the config that can change a decision. A balance can no
    longer change one, and recording it would tell a future reader it still
    could.
    """
    from core.decision_log import FINGERPRINTED_CONFIG

    for name in ("DEFAULT_ACCOUNT_BALANCE", "DEFAULT_RISK_PERCENT"):
        assert name not in FINGERPRINTED_CONFIG, (
            f"{name} is fingerprinted in the decision log but nothing reads it"
        )


# ============================================================
# The duplicates
# ============================================================

def test_the_duplicate_fields_are_gone():
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    decision = _run()
    assert "error" not in decision, decision.get("error")

    found = []
    for block, fields in DUPLICATE_FIELDS.items():
        contents = decision.get(block, {})
        for field in fields:
            if field in contents:
                found.append(f"{block}.{field}")

    assert not found, (
        "duplicate fields are back in the decision object: " + ", ".join(found)
        + "\n\ntrend.health and trend.momentum restated the two fields beside "
          "them; risk.risk_score and risk.signal_strength were both bias.score. "
          "Two names for one number means a change to one of them is invisible "
          "in the other."
    )


def test_the_survivors_are_still_there():
    """
    The removal must not have taken the canonical fields with it. Stated
    separately because a test that only asserts absence passes just as happily
    on an engine that produces nothing at all.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    decision = _run()
    assert "error" not in decision, decision.get("error")

    assert "trend_health" in decision.get("trend", {}), "trend.trend_health is gone"
    assert "momentum_mode" in decision.get("trend", {}), "trend.momentum_mode is gone"
    assert "score" in decision.get("bias", {}), (
        "bias.score is gone — that is the field risk_score and signal_strength "
        "were duplicating, and removing them was only safe because it stays."
    )


def test_the_decision_model_reads_the_canonical_trend_field():
    """
    decision_model.py read `trend["health"]` first, falling back to
    trend_health. With the duplicate gone the fallback would carry it silently
    — but the default is 50.0, so a future rename of trend_health would give
    every decision a fixed mid-range trend reading and raise nothing.

    Asserted at the source, because the value is identical either way and a
    behavioural test cannot see the difference.
    """
    from conftest import REPO_ROOT

    path = os.path.join(REPO_ROOT, "models", "decision_model.py")
    with open(path, encoding="utf-8") as f:
        code = "\n".join(line.split("#", 1)[0] for line in f.read().splitlines())

    assert 'trend.get("health"' not in code and "trend.get('health'" not in code, (
        "decision_model.py reads trend['health'] again. It no longer exists, "
        "so this silently falls through to a default of 50.0 — a fixed "
        "mid-range trend reading on every decision, raising nothing."
    )


# ============================================================
# The name collision — the one hazard in this item
# ============================================================

def test_the_panel_still_computes_its_own_stop_distance():
    """
    `risk_amount` named two unrelated things. In engine_core it was money —
    balance times risk percent — and it is gone. In panel_render it was a price
    distance and it is the denominator of all three R:R ratios. A
    find-and-replace on the name would have silently zeroed the panel's R:R
    display while everything else still looked right.

    The money is gone, so the local is renamed to stop_distance: the removal of
    one side of a name collision is the moment the other side gets fixed, or it
    never does. This asserts the denominator survived the rename.
    """
    from conftest import REPO_ROOT

    path = os.path.join(REPO_ROOT, "core", "panel_render.py")
    with open(path, encoding="utf-8") as f:
        source = f.read()
    tree = ast.parse(source)

    assigned_from_a_subtraction = False
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        names = [t.id for t in node.targets if isinstance(t, ast.Name)]
        if "stop_distance" not in names:
            continue
        for inner in ast.walk(node.value):
            if isinstance(inner, ast.BinOp) and isinstance(inner.op, ast.Sub):
                assigned_from_a_subtraction = True

    assert assigned_from_a_subtraction, (
        "panel_render.py no longer computes stop_distance as a price distance. "
        "It is the denominator of R:R 1, 2 and 3, and without it all three "
        "print 0.00 while the panel otherwise looks correct."
    )

    code = "\n".join(l.split("#", 1)[0] for l in source.splitlines())
    assert "risk_amount" not in code, (
        "risk_amount is back as a name in panel_render.py. It meant a sum of "
        "money everywhere else in this codebase; here it meant a price "
        "distance. That collision is what made a rename dangerous."
    )


def test_the_panel_does_not_read_a_sizing_field_from_the_decision():
    from conftest import REPO_ROOT

    path = os.path.join(REPO_ROOT, "core", "panel_render.py")
    with open(path, encoding="utf-8") as f:
        tree = ast.parse(f.read())

    read = set()
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "get"
                and node.args
                and isinstance(node.args[0], ast.Constant)
                and node.args[0].value in SIZING_FIELDS):
            read.add(node.args[0].value)
        elif (isinstance(node, ast.Subscript)
                and isinstance(node.slice, ast.Constant)
                and node.slice.value in SIZING_FIELDS):
            read.add(node.slice.value)

    assert not read, (
        "panel_render.py reads " + ", ".join(sorted(read)) + " off a decision "
        "object that no longer produces it. `.get` would hand it a default and "
        "the panel would print a confident zero."
    )
