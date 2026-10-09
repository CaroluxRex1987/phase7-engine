"""
Sequence item 12 — Items 5 (Reproducibility) and 6 (Traceability), the last
Critical.

THE DEFECT

The panel printed

    Trade logged to Logs/phase7_trade_log_<symbol>.csv

on every run since the engine was written, and no code anywhere wrote that
file. Of the four Criticals it is the only one where the engine was not merely
wrong but claiming a safeguard it did not have.

The chart line had the same fault in a subtler form:

    f"AI Risk chart saved to {decision.get('chart_path', 'Logs/Charts/chart.png')}"

`.get` returns the default only when the key is ABSENT. The router always sets
chart_path, and sets it to None when charting failed — so a failed chart
printed "AI Risk chart saved to None", which is still a claim that something
was saved.

CLOSED BY MAKING IT TRUE, NOT BY DELETING THE CLAIM

The opposite of the call at item 9c, and the difference is worth stating. The
`trend_failure` gate needed someone to decide when a trade should be blocked —
a trading judgment nothing here can validate. This needs nobody to decide
anything: a log file exists or it does not, and Item 5 requires one regardless
of what the panel says.
"""

import json
import os
import pytest
import shutil
import tempfile

PINNED_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "fixtures", "pinned")
UNREACHABLE = "http://127.0.0.1:1"


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
# Item 6 — the claim must be true
# ============================================================

def test_the_decision_log_the_panel_claims_actually_exists():
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    decision = _run()
    path = decision.get("decision_log_path")

    assert path, (
        "the run reports no decision log path. The panel has claimed one on "
        "every run since the engine was written."
    )
    assert os.path.exists(path), (
        f"the decision object names {path} but no such file exists. That is "
        f"Item 6 exactly: an audit action asserted, not performed."
    )


def test_the_log_records_what_the_run_saw_not_just_what_it_decided():
    """
    Item 5 is Reproducibility, and that is a higher bar than "a record exists".

    A stored decision with no fingerprint of its inputs cannot be checked
    against anything — it is a receipt. These five fields are what make a run
    repeatable.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    from core import config, decision_log

    _run()
    # B6, 6 October 2026: _run() is pinned, so its record is in the pinned
    # log, not in config.LOG_DIR's live one.
    records = decision_log.read(decision_log.records_dir(config.LOG_DIR, False), "AEROUSDT")
    assert records, "the log is empty after a successful run"

    latest = records[-1]
    assert latest.get("engine_version"), "no engine_version in the record"
    assert latest.get("config"), "no config snapshot in the record"

    prov = latest.get("decision", {}).get("provenance", {})
    for field in ("engine_version", "last_candle", "row_count", "source"):
        assert field in prov, f"provenance is missing {field}: {prov}"

    assert prov["row_count"] > 0, "row_count is zero on a successful run"
    assert prov["source"] == "pinned", (
        f"the run used pinned data but records its source as {prov['source']!r}"
    )

    # The source is a KIND, not a path. Recording the pinned directory made
    # provenance differ between two runs on identical data — caught by the
    # determinism test on the first full run of this item.
    assert "/" not in prov["source"] and "\\" not in prov["source"], (
        f"provenance.source looks like a path ({prov['source']!r}). A "
        f"machine-specific location is not part of a run's identity; "
        f"last_candle and row_count are what fingerprint the data."
    )


def test_engine_version_is_written_somewhere_at_last():
    """
    config.engine_version has existed since the engine was built and was
    written nowhere — Step 5's verification pass counted exactly one occurrence
    of it in the whole source tree, its own definition.

    A version string nothing records cannot answer "which build produced this
    number", which is the question a traceability rule exists to answer.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    from core import config

    decision = _run()
    recorded = decision.get("provenance", {}).get("engine_version")
    assert recorded == config.engine_version, (
        f"the run records engine_version {recorded!r}, config says "
        f"{config.engine_version!r}"
    )


def test_a_failed_write_is_reported_as_a_failure():
    """
    The other half of Item 6, and the one that is easy to miss.

    Writing the log fixes the claim only while the write succeeds. An engine
    that prints "logged" after a failed write has the original defect back with
    a new filename.
    """
    from core import config, decision_log

    unwritable = os.path.join(tempfile.gettempdir(), "phase7_not_a_dir")
    try:
        # A file where a directory is expected: makedirs fails, so must write.
        with open(unwritable, "w") as f:
            f.write("x")
        result = decision_log.write({"symbol": "TESTUSDT"}, config, log_dir=unwritable)
    finally:
        try:
            os.remove(unwritable)
        except OSError:
            pass

    assert result is None, (
        f"decision_log.write returned {result!r} when it could not write. "
        f"The caller uses this return value to decide whether the panel may "
        f"claim the run was logged."
    )


# ============================================================
# The panel's claims
# ============================================================

def test_the_panel_makes_no_unconditional_claims_about_files():
    """
    Source-level, because the failing case is hard to reach at runtime and the
    defect is a shape rather than a value: a claim printed without checking.
    """
    from conftest import REPO_ROOT

    with open(os.path.join(REPO_ROOT, "core", "panel_render.py"), encoding="utf-8") as f:
        code = "\n".join(line.split("#", 1)[0] for line in f.read().splitlines())

    assert "Trade logged to Logs/" not in code, (
        "the panel prints a hardcoded trade-log path again. That path named a "
        "file nothing wrote, on every run, for the life of the engine."
    )
    assert "'Logs/Charts/chart.png'" not in code, (
        "the chart line uses a .get default again. The key is always present "
        "and is None when charting failed, so the default never fires and the "
        "panel prints 'saved to None'."
    )

    assert "VWMA volume trend is pointing down" not in code, (
        "the Validation Notes line has a .get default that asserts a specific "
        "market fact. A default under that heading states a reading of this "
        "market that nothing computed, and the heading gives it the authority "
        "of something that was."
    )

    # 2 SEPTEMBER 2026. The first assertion above described a live defect and
    # did not catch it. Its message says, correctly, that the key "is None
    # when charting failed" and that the panel "prints 'saved to None'" --
    # and then checked only that the OLD hardcoded default was gone from THIS
    # file. The None arrived from somewhere else: models/signal_router.py
    # built the decision object with str(chart_path), and str(None) is the
    # truthy string "None", which passes the panel's own gate. It printed for
    # the life of the engine.
    #
    # A test whose failure message documents a defect it cannot detect is
    # worse than no test: it reads as coverage to anyone auditing the suite.
    # The claim is made in one file and the value is built in another, so the
    # check has to follow the value.
    with open(os.path.join(REPO_ROOT, "models", "signal_router.py"),
              encoding="utf-8") as f:
        router = f.read()

    assert "str(chart_path) if chart_path" in router, (
        "signal_router stringifies chart_path without a guard again. "
        "str(None) is the truthy string 'None', so the panel prints "
        "'Chart saved to None' -- a claim about a file nothing wrote. The "
        "convention is '' for absent, as decision_log_path already uses two "
        "fields above it."
    )


# N5, 9 October 2026: three tests stood here, and went with what they tested
# (Viktor's ruling of 5 October, point 7: Bitcoin is reference only; the
# BTC-adjusted confidence is gone).
#
#   test_the_explanation_names_the_symbol_under_analysis -- the adjustment's
#     sentence named the run's asset, not "AERO" (Item 10(a) rider). The
#     sentence is gone. The panel's BTC section still names the asset, and
#     tests/test_panel_prints_only_what_was_computed.py holds it to that.
#   test_the_correlation_phrase_is_not_doubled -- the same sentence did not
#     say "relationship relationship". Nothing builds that phrase now.
#   test_the_btc_number_carries_its_validation_status -- core/panel_render.py
#     carried Item 7's status line under the BTC-adjusted confidence. The
#     number and its line are gone. Kept, the test would fail; kept with the
#     wording left in a comment, it would pass while guarding nothing.
#
# tests/test_btc_is_reference_only.py checks that none of it comes back.
