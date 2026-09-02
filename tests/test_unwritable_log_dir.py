"""
An unwritable log directory must not destroy the analysis.

WHAT WAS WRONG

`route()` opened with two unguarded calls:

    os.makedirs(config.CHART_DIR, exist_ok=True)
    os.makedirs(config.LOG_DIR, exist_ok=True)

They wrote nothing. Every writer in this engine already creates its own
directory on demand, inside its own error handling -- decision_log.write
returns None, _save_state warns, plot_engine_chart warns, lineage.write_archive
returns None. These two duplicated all four.

What they added was a failure mode, and they added it at the worst possible
point: the top of route(), before the analysis has run. An unwritable log
directory raised there, the router's broad handler reported "Router execution
failed: [Errno 20] Not a directory", and the operator lost the entire
analysis -- not merely the log of it. Four independently recoverable
conditions collapsed into one total failure.

Found while writing the halt-safety test for the raw-input archive
(test_lineage.py), and verified present before that work rather than
introduced by it. Same class as sequence item 14's REQUIRED_DIRS finding.

VIKTOR'S RULING, 2 September 2026

A run whose decision log cannot be written STILL AUTHORIZES A TRADE. It warns,
the panel makes no claim that anything was logged, and the operator decides.
His 29 August degrade-not-halt ruling applied literally: a disk problem must
not destroy an analysis that was computed correctly, and must not veto one
either.

Claude recommended the opposite -- refusing authorization on the grounds that
Item 6 is Critical and a trade taken on a decision that left no trace is
unauditable by construction. Viktor ruled otherwise. Recorded here because the
tests below pin the ruling, and a later reader should be able to see it was
decided rather than defaulted into.
"""

import os
import shutil
import tempfile

import pytest


PINNED_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "fixtures", "pinned")
UNREACHABLE = "http://127.0.0.1:1"


def _engine_available():
    try:
        import pandas_ta  # noqa: F401
        return True
    except Exception:
        return False


def _run_with_log_dir(log_dir):
    from core import config
    from data.data_fetcher import DataFetcher, data_fetcher
    from models.signal_router import SignalRouter

    original_url = data_fetcher.base_url
    original_log = config.LOG_DIR
    original_chart = config.CHART_DIR
    try:
        data_fetcher.base_url = UNREACHABLE
        config.LOG_DIR = log_dir
        config.CHART_DIR = os.path.join(log_dir, "charts")
        DataFetcher.set_pinned_source(PINNED_DIR)
        return SignalRouter().route(symbol="AEROUSDT", timeframe="4h")
    finally:
        DataFetcher.clear_pinned_source()
        data_fetcher.base_url = original_url
        config.LOG_DIR = original_log
        config.CHART_DIR = original_chart


def _unwritable_dir(work):
    """A log directory that cannot be created: a path underneath a real file."""
    blocker = os.path.join(work, "not_a_directory")
    with open(blocker, "w") as fh:
        fh.write("x")
    return os.path.join(blocker, "logs")


def test_an_unwritable_log_directory_does_not_destroy_the_analysis():
    """
    The defect itself. Before the fix this returned
    {"error": "Router execution failed: [Errno 20] Not a directory: ..."}
    and nothing else -- no bias, no levels, no panel.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    work = tempfile.mkdtemp(prefix="phase7_unwritable_")
    try:
        decision = _run_with_log_dir(_unwritable_dir(work))

        assert not decision.get("error"), (
            f"an unwritable log directory failed the whole run: "
            f"{decision.get('error')}. The analysis is computed before "
            f"anything is written, and a disk problem must not destroy it."
        )
        # The analysis is actually there, not an empty shell that merely
        # lacks an "error" key.
        for section in ("bias", "trend", "structure", "entry", "risk"):
            assert decision.get(section), f"the decision has no {section} block"
        assert decision["bias"].get("detailed"), "no bias was reported"
    finally:
        shutil.rmtree(work, ignore_errors=True)


def test_the_panel_claims_no_log_when_none_was_written():
    """
    Sequence item 12's rule, in the new failure path: the engine must not say
    it logged something it did not. `decision_log_path` is the panel's gate,
    and it must be empty rather than naming a file nothing wrote.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    work = tempfile.mkdtemp(prefix="phase7_noclaim_")
    try:
        decision = _run_with_log_dir(_unwritable_dir(work))
        assert decision.get("decision_log_path") == "", (
            f"the run reports a decision log at "
            f"{decision.get('decision_log_path')!r} and no log was written."
        )
        assert decision["lineage"]["archive"]["path"] is None, (
            "the run names an archive it could not write."
        )
    finally:
        shutil.rmtree(work, ignore_errors=True)


def test_a_run_that_could_not_be_logged_still_authorizes_a_trade():
    """
    VIKTOR'S RULING, 2 September 2026, pinned.

    A failed write is not a missing input. `degradation` blocks trading and is
    about inputs the ANALYSIS was computed without; nothing here was missing
    from the analysis, only from the filing of it. Conflating the two would
    refuse trades over a full disk.

    Claude argued for the opposite and was overruled. If this assertion is
    ever flipped, it should be flipped by a new ruling recorded the same way,
    not by someone deciding the test looks wrong.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    work = tempfile.mkdtemp(prefix="phase7_authorized_")
    try:
        decision = _run_with_log_dir(_unwritable_dir(work))
        degradation = decision.get("degradation", {})

        assert degradation.get("trading_authorized") is True, (
            "a run whose log could not be written was refused authorization. "
            "Viktor ruled on 2 September that a disk problem neither destroys "
            "an analysis nor vetoes one."
        )
        assert not degradation.get("missing_inputs"), (
            f"a failed write was recorded as a missing analysis input: "
            f"{degradation.get('missing_inputs')}. Nothing was missing from "
            f"the analysis."
        )
    finally:
        shutil.rmtree(work, ignore_errors=True)


def test_the_router_creates_no_directories_of_its_own():
    """
    The mechanism, not just the symptom.

    The two makedirs calls are gone from route(). This asserts they have not
    come back -- and, because a name-based check would pass over a differently
    spelled reimplementation, it also asserts the module no longer imports
    `os` at all, which it does not need now.
    """
    import inspect
    import models.signal_router as router_module

    source = inspect.getsource(router_module)
    body = "\n".join(
        line for line in source.splitlines()
        if not line.lstrip().startswith("#")
    )
    assert "makedirs" not in body, (
        "signal_router creates directories again. Every writer in this engine "
        "makes its own, inside its own error handling; doing it here, before "
        "the analysis runs, is what turned a recoverable condition into a "
        "total failure."
    )
    assert not hasattr(router_module, "os"), (
        "signal_router imports os again. Its only uses were the removed "
        "makedirs calls."
    )


def test_a_writable_directory_still_produces_a_log_and_an_archive():
    """
    The control. A router that quietly stopped writing anything would pass
    every test above.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    work = tempfile.mkdtemp(prefix="phase7_writable_")
    try:
        log_dir = os.path.join(work, "logs")
        decision = _run_with_log_dir(log_dir)

        assert decision.get("decision_log_path"), "no decision log was written"
        assert os.path.exists(decision["decision_log_path"])
        archived = decision["lineage"]["archive"]["path"]
        assert archived and os.path.exists(archived), "no archive was written"
    finally:
        shutil.rmtree(work, ignore_errors=True)
