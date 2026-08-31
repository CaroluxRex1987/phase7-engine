"""
Sequence item 5b — removing compute_exit and engine_core's render path.

WHY THIS IS A SEPARATE FILE FROM test_no_dead_columns.py

5a deleted indicator columns and inherited a single output-invariance proof for
all of them. 5b is a different kind of change: it removes a function that was
called on every run, and it removes a parameter from a public method signature.
Both turn out to be output-invariant too, but that had to be established rather
than assumed, and the reasoning is per-item rather than blanket.

A CORRECTION, RECORDED HERE BECAUSE IT IS ALREADY IN A PUSHED COMMIT

The 5a commit message and the docstring of test_no_dead_columns.py both said
compute_exit "is called at engine_core.py:889 and its output feeds at least
eight sites across four files — current_price is read in five places and action
in three, including live_trading's simulated order."

The line number was 529, not 889. More importantly, the second half traced
names rather than data. Eight references to a variable called `exit_data` do
exist, but seven of them are not reading compute_exit's output.
signal_router.py:265 builds a fresh dict:

    "exit": {
        "action": final_action,                     # <- DecisionModel's
        "current_price": float(exit_data.get("current_price", 0.0)),
    }

`final_action` there is dm_result["final_action"] from decision_model.py.
compute_exit also returned a key called `final_action`, and the two were
conflated. The `action` reads in panel_render and live_trading were always
reading DecisionModel.

The conclusion — handle it separately from 5a — was still right, because a
refactor should not ride inside a cleanup on borrowed proof. The stated reason
for it was wrong.

WHAT COMPUTE_EXIT ACTUALLY CONTRIBUTED

Six returned keys. Five (final_action, exit_reason, stop_loss, target_hit,
exit_status) were computed on every run and discarded one call later. The panel
does print a stop loss, but reads risk["atr_stop"].

The sixth, current_price, was float(price_data["close"].iloc[-1]) where
price_data=df_struct — the identical expression engine_core had already
evaluated at the top of its section 8, on the same frame. df_struct is assigned
once and never reassigned, so the values were equal by construction. It is now
passed through directly.

THE RENDER PATH

engine_core.run() took render: bool = True, and the only caller passed
render=False. So the panel engine_core could print was unreachable from every
entry point. Removing compute_exit made it worse than unused: the panel reads
its DECISION line from exit["action"], which only the router supplies, so the
raw object would have fallen through to the literal default and printed "WAIT"
on every run regardless of analysis. Before 5b it fell through to compute_exit
and printed an exit verdict under a decision heading.

Either way it is the panel asserting a decision nothing computed — the Item 6
family. Deleted under Item 16. Ruled by Viktor, 30 August 2026.
"""

import ast
import inspect
import os
import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PINNED_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "fixtures", "pinned")


def _engine_available():
    try:
        import pandas_ta  # noqa: F401
        return True
    except Exception:
        return False


def _source(rel):
    with open(os.path.join(REPO_ROOT, rel), encoding="utf-8") as f:
        return f.read()


def test_compute_exit_is_gone():
    """
    The regression guard. Restoring it means restoring five outputs nothing
    reads plus a duplicate of a value the engine already has.
    """
    import models.exit_model as exit_model

    assert not hasattr(exit_model, "compute_exit"), (
        "compute_exit is back in models/exit_model.py. Five of its six return "
        "values were discarded by signal_router before anything downstream saw "
        "them, and the sixth duplicated engine_core's own current_price. If "
        "the engine now needs exit management, that is a real feature and "
        "belongs in its own commit with its own justification — not restored "
        "as a side effect."
    )


def test_build_exit_watch_survives():
    """
    The other half. build_exit_watch is the advisory-flag function, it is
    consumed, and it lives in the same file compute_exit was deleted from —
    exactly the shape of a cleanup that takes one thing too many.
    """
    import models.exit_model as exit_model

    assert hasattr(exit_model, "build_exit_watch"), (
        "build_exit_watch has gone missing from models/exit_model.py. It is "
        "consumed: engine_core calls it and its output is the panel's Exit "
        "Watch section."
    )


def test_engine_core_has_no_render_parameter():
    """
    Signature-level, so it fails at import rather than at some later run.
    """
    from core.engine_core import Phase7Engine

    params = inspect.signature(Phase7Engine.run).parameters
    assert "render" not in params, (
        "Phase7Engine.run has a `render` parameter again. Rendering belongs to "
        "SignalRouter, which owns the only complete decision object. A panel "
        "built from engine_core's raw output has no DECISION to show and will "
        "print the fallback literal instead."
    )


def test_engine_core_does_not_render():
    """
    Stronger than the signature check: the import and the calls must both be
    gone, or a later change can quietly reintroduce rendering without a
    parameter to notice.
    """
    src = _source(os.path.join("core", "engine_core.py"))
    tree = ast.parse(src)

    imported = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            for a in node.names:
                if a.name == "render_panel":
                    imported.append(node.module)

    called = [
        n for n in ast.walk(tree)
        if isinstance(n, ast.Call)
        and isinstance(n.func, ast.Name)
        and n.func.id == "render_panel"
    ]

    assert not imported and not called, (
        "core/engine_core.py renders again "
        f"(imports from: {imported or 'none'}; call sites: {len(called)}).\n"
        "engine_core returns a decision object; the router assembles the "
        "complete one and renders it. Two renderers means two panels that can "
        "disagree, and the engine's would be the one with no DECISION."
    )


def test_the_dead_hit_literals_are_gone_from_the_panel():
    """
    Item 16, and a small honesty point.

    panel_render coloured "TARGET 1/2/3 HIT" green and "STOP LOSS HIT" red.
    Those four strings could only come from compute_exit, which the router
    discarded, so the comparisons never matched. A reader of that file would
    reasonably conclude the panel can report a target being hit.
    """
    src = _source(os.path.join("core", "panel_render.py"))

    # Strip comments — the removal is documented in prose in that file, and the
    # explanation necessarily names the strings it is explaining.
    code_only = "\n".join(
        line.split("#", 1)[0] for line in src.splitlines()
    )

    resurrected = [s for s in ("TARGET 1 HIT", "TARGET 2 HIT", "TARGET 3 HIT",
                               "STOP LOSS HIT") if s in code_only]

    assert not resurrected, (
        "dead action literals are back in core/panel_render.py: "
        + ", ".join(resurrected) +
        "\nNothing produces these. DecisionModel emits WAIT, NO-TRADE (RISK "
        "TOO HIGH), LONG/SHORT and the AGGRESSIVE/CONSERVATIVE variants."
    )


def test_current_price_survives_the_removal():
    """
    The invariance check that matters, done live rather than by inspection.

    compute_exit's one consumed output was the last close of the structure
    frame. engine_core now supplies it directly. If those ever differ, every
    R:R ratio on the panel is computed against the wrong price — panel_render
    derives its risk distance from this value.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    from data.data_fetcher import DataFetcher, data_fetcher
    from models.signal_router import SignalRouter

    data_fetcher.base_url = "http://127.0.0.1:1"   # nothing may reach the network
    try:
        DataFetcher.set_pinned_source(PINNED_DIR)
        decision = SignalRouter().route(symbol="AEROUSDT", timeframe="4h")
    finally:
        DataFetcher.clear_pinned_source()

    assert "error" not in decision, decision.get("error")

    reported = float(decision["exit"]["current_price"])

    import pandas as pd
    pinned = pd.read_csv(os.path.join(PINNED_DIR, "AEROUSDT_4h.csv"))
    expected = float(pinned["close"].iloc[-1])

    assert reported == expected, (
        f"decision['exit']['current_price'] is {reported}, but the last close "
        f"in the pinned series is {expected}.\n"
        "These were the same value before 5b because compute_exit recomputed "
        "the same expression on the same frame. If they have diverged, "
        "engine_core is sourcing current_price from somewhere else."
    )
