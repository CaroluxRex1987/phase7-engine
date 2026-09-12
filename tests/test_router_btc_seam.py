"""
The router seam — what engine_core produces, what signal_router accepts.

KIMI ROUND 4, FINDING 1 (Major), and the Item 6 defect the confirmation run
found underneath it.

WHAT WAS WRONG

`core/engine_core.py` (771-788) builds the BTC block as

    {"available": True, ..., "correlation": None, "beta": None}

when the AERO/BTC relationship could not be measured. None is that file's own
spelling for "not measured" — the same one it uses for atr and
structural_level — and it is what serialises to JSON null.

`models/signal_router.py::_merge_btc_context` (478-481) read it as

    "correlation": float(btc_context.get("correlation", 0.0))

The 0.0 is not a default for a missing key. The key is present, so the default
never fired; float(None) raised TypeError, and _build_decision_object's broad
except turned a complete and correct AERO analysis into

    Decision object construction failed: float() argument must be a string or
    a real number, not 'NoneType'

An optional Bitcoin number being unavailable destroyed the analysis it was
optional to. Two indexes sharing no timestamps is enough to get there: one
candle closing between two API calls, an exchange gap, a stale feed.

WHY IT SURVIVED THREE READINGS OF THESE LINES

The round-3 reviewer read the same three lines and filed them as Minor,
reasoning that "engine_core currently always populates these keys when
available is True, so the defaults never fire". That is true and it is the
wrong half of the sentence: the key is populated, with None. The pinned
fixtures share all 450 timestamps, so no test in this suite had ever made the
producer emit its not-measured shape and handed it to this consumer. The
producer was tested (test_btc_correlation_alignment.py), the decision model was
tested, the panel was tested. The seam between them was not.

That is what this file is for. The tests below are written at the seam
deliberately, rather than as one more assertion about either side of it.

THE SECOND DEFECT, FOUND BY THE CONFIRMATION RUN

The record written when the assembly fails was {symbol, timeframe, error} and
nothing else, while the healthy record beside it in the same log carries
`lineage` and `provenance` — input_hashes, run_hash, and whether the run was
pinned. decision_log.write() serialises whatever it is handed, so every failed
assembly stored a record that cannot be traced to any input. Item 6 is the item
this project raised to Critical.
"""

import os
import shutil

import pandas as pd
import pytest

from conftest import REPO_ROOT

PINNED_DIR = os.path.join(REPO_ROOT, "tests", "fixtures", "pinned")
UNREACHABLE = "http://127.0.0.1:9"

TWO_HOURS_MS = 2 * 60 * 60 * 1000


def _router():
    """A router with no engine attached — these tests drive the assembler."""
    from models.signal_router import SignalRouter
    return SignalRouter(engine_core=object())


def _producer_shape(**over):
    """
    The BTC block as core/engine_core.py actually writes it, not as a test
    would like it to look. Keep this in step with engine_core 771-788; the
    end-to-end test at the bottom is what catches it drifting.
    """
    base = {
        "available": True,
        "raw": "BULLISH",
        "detailed": "BULLISH CONFIRMED",
        "score": 60.0,
        "regime": "TRENDING",
        "volatility": "NORMAL",
        "trend_health": 71.0,
        "correlation": None,
        "correlation_label": "NOT MEASURED",
        "beta": None,
        "broad_market_stress": False,
        "n_observations": 0,
        "degraded_inputs": [],
    }
    base.update(over)
    return base


# ============================================================
# The merge accepts what the producer emits
# ============================================================

def test_the_merge_accepts_the_producers_not_measured_shape():
    merged = _router()._merge_btc_context(
        _producer_shape(),
        {"available": True, "btc_adjusted_confidence": 52.0, "reasons": []},
    )
    assert merged["available"] is True
    assert merged["correlation"] is None
    assert merged["beta"] is None


def test_an_unmeasured_correlation_does_not_arrive_as_a_measurement():
    """
    The point of returning None rather than 0.0. A correlation of 0.00 is what
    a real pair of independent assets produces, so substituting it reports a
    finding the engine does not have — the defect already removed from
    btc_context.py's (0.0, 0.0, 0), trend_health's 50.0 and RSI's 50.0.
    """
    merged = _router()._merge_btc_context(
        _producer_shape(),
        {"available": True, "btc_adjusted_confidence": 52.0, "reasons": []},
    )
    assert merged["correlation"] != 0.0
    assert merged["beta"] != 0.0
    assert merged["n_observations"] == 0


def test_a_measured_relationship_passes_through_unchanged():
    """
    The negative control. If the fix altered a measured value the panel would
    start printing a different number for the same inputs.
    """
    merged = _router()._merge_btc_context(
        _producer_shape(correlation=-0.9012, beta=1.37, n_observations=30,
                        correlation_label="STRONG NEGATIVE"),
        {"available": True, "btc_adjusted_confidence": 64.5, "reasons": ["x"]},
    )
    assert merged["correlation"] == pytest.approx(-0.9012)
    assert merged["beta"] == pytest.approx(1.37)
    assert merged["n_observations"] == 30
    assert merged["correlation_label"] == "STRONG NEGATIVE"


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf"), "n/a", object()])
def test_a_value_that_is_not_a_finite_number_is_not_measured(bad):
    """
    NaN is the in-memory spelling btc_context returns; engine_core converts it
    to None at its own boundary. If a future producer stops converting, the
    merge must still not crash and must still not invent a number.
    """
    merged = _router()._merge_btc_context(
        _producer_shape(correlation=bad),
        {"available": True, "btc_adjusted_confidence": 52.0, "reasons": []},
    )
    assert merged["correlation"] is None


# ============================================================
# A failed assembly still says what it ran on
# ============================================================

def test_a_failed_assembly_still_carries_the_runs_lineage():
    class _Fails:
        def evaluate(self, *args, **kwargs):
            raise RuntimeError("forced, to reach the except")

    from models.signal_router import SignalRouter

    lineage = {"input_hashes": {"AEROUSDT_4h": "abc123"}, "run_hash": "def456",
               "pinned": True}
    provenance = {"source": "pinned"}

    out = SignalRouter(engine_core=object(), decision_model=_Fails())._build_decision_object(
        symbol="AEROUSDT", timeframe="4h",
        bias={}, trend={}, structure={}, entry={}, risk={}, exit_data={},
        macro_bias="NEUTRAL", chart_path="",
        provenance=provenance, lineage_record=lineage,
    )

    assert "error" in out
    assert out["lineage"] == lineage, (
        "the failed record lost its lineage — Item 6 cannot trace it to any "
        "input, which is the state the Section 11 run found in the live log"
    )
    assert out["provenance"] == provenance


def test_the_lineage_survives_into_the_written_record(tmp_path):
    """
    The claim is about the log, not about a dict in memory, so the assertion is
    made on bytes read back off disk.
    """
    from core import config, decision_log

    record = {"symbol": "AEROUSDT", "timeframe": "4h",
              "error": "Decision object construction failed: forced",
              "provenance": {"source": "pinned"},
              "lineage": {"run_hash": "def456"}}

    written = decision_log.write(record, config, log_dir=str(tmp_path))
    assert written, "the log was not written, so this test proves nothing"

    back = decision_log.read(str(tmp_path), "AEROUSDT")
    assert len(back) == 1
    assert back[0]["decision"]["lineage"] == {"run_hash": "def456"}


# ============================================================
# End to end, on the producer's own output
# ============================================================

def test_the_router_completes_when_the_correlation_cannot_be_measured(tmp_path, monkeypatch):
    """
    The test that would have caught this, and the one that catches the next one:
    the real engine, on real fixtures, made to produce its not-measured shape,
    handed to the real router.

    The BTC series is the committed fixture with every timestamp shifted by two
    hours, so the two indexes share nothing and compute_correlation_beta returns
    (NaN, NaN, 0). This is the case Kimi's Section 11 asked for. Before the fix
    it returned an error object; a complete decision is the assertion.
    """
    pytest.importorskip("pandas_ta")

    from core import config
    from data.data_fetcher import DataFetcher, data_fetcher
    from models.signal_router import SignalRouter

    pinned = tmp_path / "pinned"
    pinned.mkdir()
    for name in ("AEROUSDT_4h.csv", "AEROUSDT_1d.csv"):
        shutil.copy2(os.path.join(PINNED_DIR, name), pinned / name)
    btc = pd.read_csv(os.path.join(PINNED_DIR, "BTCUSDT_4h.csv"))
    btc["timestamp"] = btc["timestamp"].astype("int64") + TWO_HOURS_MS
    btc.to_csv(pinned / "BTCUSDT_4h.csv", index=False)

    # Nothing here touches the engine's real log directory.
    monkeypatch.setattr(config, "LOG_DIR", str(tmp_path / "logs") + os.sep)

    original_url = data_fetcher.base_url
    try:
        data_fetcher.base_url = UNREACHABLE
        DataFetcher.set_pinned_source(str(pinned))
        decision = SignalRouter().route("AEROUSDT", "4h")
    finally:
        DataFetcher.clear_pinned_source()
        data_fetcher.base_url = original_url

    assert "error" not in decision, (
        f"the analysis was destroyed by an unmeasurable optional input: "
        f"{decision.get('error')}"
    )

    btc_block = decision.get("btc_context", {})
    assert btc_block.get("available") is True
    assert btc_block.get("correlation") is None
    assert btc_block.get("n_observations") == 0
    assert decision.get("lineage"), "a completed run with no lineage"


def test_the_control_case_still_works(tmp_path, monkeypatch):
    """
    The negative control for the test above. On the fixtures as committed the
    two indexes share all 450 timestamps, the correlation is measured, and the
    run must still complete with a number — otherwise the test above would pass
    on a harness that cannot produce a working run at all.
    """
    pytest.importorskip("pandas_ta")

    from core import config
    from data.data_fetcher import DataFetcher, data_fetcher
    from models.signal_router import SignalRouter

    monkeypatch.setattr(config, "LOG_DIR", str(tmp_path / "logs") + os.sep)

    original_url = data_fetcher.base_url
    try:
        data_fetcher.base_url = UNREACHABLE
        DataFetcher.set_pinned_source(PINNED_DIR)
        decision = SignalRouter().route("AEROUSDT", "4h")
    finally:
        DataFetcher.clear_pinned_source()
        data_fetcher.base_url = original_url

    assert "error" not in decision
    btc_block = decision.get("btc_context", {})
    assert isinstance(btc_block.get("correlation"), float)
    assert btc_block.get("n_observations") == 30
