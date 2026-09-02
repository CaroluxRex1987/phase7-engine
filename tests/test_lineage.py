"""
Audit Findings 6 and 7 — Items 5 (Reproducibility) and 6 (Traceability).

WHAT THE RE-AUDIT ASKED FOR, AND WHY THE OLD RECORD DID NOT MEET IT

Sequence item 12 built the decision log and closed the Critical half of Item 6:
the panel had claimed a trade log that nothing wrote. What it left is what Luna
Pro's Findings 6 and 7 name, and Viktor's 29 August ruling raised Item 6 to
Critical — which makes this the last Critical, the one holding the release gate
and the backtest gate shut.

The gap in one sentence: the log recorded a last-candle timestamp and a row
count, and two different frames can share both. Nothing stored told them apart,
so "reconstructable" was a word in the Constitution rather than a property of
the engine.

THE STANDARD THIS FILE HOLDS ITSELF TO

Luna Pro's assessment of the previous suite was that "it tests that selected
implementation details have not changed more strongly than it tests whether the
engine is correct." A file that asserted `"lineage" in decision` and stopped
would be exactly that, and would pass just as happily over a lineage section
full of nulls.

So the central test here does not inspect fields. It takes the archive this
engine wrote, rebuilds the candles out of it, runs the engine again on the
rebuilt data, and requires the same decision. That is the claim Item 5 makes,
executed rather than described. Everything else in this file is a property of
the machinery that test depends on.
"""

import copy
import glob
import gzip
import json
import os
import shutil
import tempfile
import time

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PINNED_DIR = os.path.join(REPO, "tests", "fixtures", "pinned")
UNREACHABLE = "http://127.0.0.1:1"


def _engine_available():
    try:
        import pandas_ta  # noqa: F401
        return True
    except Exception:
        return False


# Fields that legitimately differ between two runs on identical input, and so
# cannot be part of a reconstruction comparison. Kept deliberately short: every
# name added here is a field the reconstruction test stops checking, which is
# how a test like this quietly becomes vacuous.
#
#   logged_at / archived_at  wall clock
#   chart_path               written per run, path only
#   decision_log_path        appended per run
#   pruned_this_run          depends on what else is on disk
VOLATILE = {"chart_path", "decision_log_path", "timestamp", "generated_at",
            "logged_at", "archived_at", "pruned_this_run", "archive_path",
            "path", "prior_state"}


def _strip(obj):
    if isinstance(obj, dict):
        return {k: _strip(v) for k, v in obj.items() if k not in VOLATILE}
    if isinstance(obj, (list, tuple)):
        return [_strip(v) for v in obj]
    if isinstance(obj, float):
        return round(obj, 8)
    return obj


def _run(pinned_dir, log_dir):
    """One full routed run against a pinned directory, logging into log_dir."""
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
        DataFetcher.set_pinned_source(pinned_dir)
        return SignalRouter().route(symbol="AEROUSDT", timeframe="4h")
    finally:
        DataFetcher.clear_pinned_source()
        data_fetcher.base_url = original_url
        config.LOG_DIR = original_log
        config.CHART_DIR = original_chart


def _clear_state(log_dir):
    """
    Remove the cross-run state file.

    Exit Watch compares against the previous run, so a second run that can see
    the first one's state is not a repeat of it. Every comparison below starts
    from the same place on purpose.
    """
    for path in glob.glob(os.path.join(log_dir, "phase7_state_*.json")):
        try:
            os.remove(path)
        except OSError:
            pass


# ============================================================
# THE CENTRAL CLAIM — Item 5, executed
# ============================================================

def test_a_run_can_be_rebuilt_from_its_own_archive_and_gives_the_same_decision():
    """
    Item 5: "Every analysis must be reconstructable later."

    This is that sentence as an executable statement. Run the engine, take
    ONLY the archive it wrote, rebuild the candles from it, run again against
    the rebuilt candles, and require the same decision.

    Note what the second run is not given: the original fixture files. If the
    archive is missing a column, truncates the history, loses precision in a
    float, or drops the macro series, the rebuilt run either fails outright or
    produces different numbers. There is no way for this test to pass on an
    archive that does not actually contain the input.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    from core import lineage

    work = tempfile.mkdtemp(prefix="phase7_rebuild_")
    try:
        original_logs = os.path.join(work, "logs_original")
        _clear_state(original_logs)
        first = _run(PINNED_DIR, original_logs)

        assert not first.get("error"), f"the first run failed: {first.get('error')}"
        archived = first["lineage"]["archive"]["path"]
        assert archived, (
            "the run recorded no archive path. Without one there is nothing "
            "to reconstruct from, and Item 5 is a claim rather than a property."
        )
        assert os.path.exists(archived), (
            f"the record names an archive at {archived} and nothing is there. "
            f"That is the defect sequence item 12 exists to have closed, in a "
            f"new field."
        )

        # Rebuild the pinned set from the archive alone.
        payload = lineage.read_archive(archived)
        assert payload, "the archive could not be read back"

        rebuilt_dir = os.path.join(work, "rebuilt")
        os.makedirs(rebuilt_dir)
        wanted = {"struct": "AEROUSDT_4h.csv", "macro": "AEROUSDT_1d.csv",
                  "btc": "BTCUSDT_4h.csv"}
        for name, filename in wanted.items():
            frame = payload["frames"].get(name)
            assert frame, f"the archive holds no {name} frame"
            df = lineage.rebuild_frame(frame["canonical"])
            assert df is not None, f"the {name} frame could not be rebuilt"
            assert lineage.frame_hash(df) == frame["sha256"], (
                f"the rebuilt {name} frame does not hash to the digest stored "
                f"beside it. The archive round trip is lossy, which means the "
                f"stored bytes are not the input."
            )
            out = df.copy()
            # Back into the shape the pinned loader reads.
            # Epoch milliseconds, which is what the pinned loader parses.
            # Cast to a millisecond dtype first rather than dividing an int64:
            # pandas 3 indexes are microsecond-resolution and pandas 2's were
            # nanosecond, so a hardcoded divisor silently produced timestamps
            # a thousand times too close together on one of them.
            epoch_ms = out.index.astype("datetime64[ms]").astype("int64")
            out.insert(0, "timestamp", epoch_ms)
            out.to_csv(os.path.join(rebuilt_dir, filename), index=False)

        rebuilt_logs = os.path.join(work, "logs_rebuilt")
        _clear_state(rebuilt_logs)
        second = _run(rebuilt_dir, rebuilt_logs)

        assert not second.get("error"), (
            f"the run against rebuilt data failed: {second.get('error')}"
        )

        a, b = _strip(first), _strip(second)
        differing = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
        assert not differing, (
            "the decision rebuilt from the archive differs from the original "
            "in: " + ", ".join(differing) +
            "\nThe archive does not carry enough to reproduce the run, so "
            "Item 5 is not met however complete the record looks."
        )

        assert first["lineage"]["run_hash"] == second["lineage"]["run_hash"], (
            "the two runs produced different run hashes despite identical "
            "inputs and settings. The hash is then not an identity."
        )
    finally:
        shutil.rmtree(work, ignore_errors=True)


# ============================================================
# Item 6 — the chain, link by link
# ============================================================

def test_the_lineage_chain_has_every_link_the_constitution_names():
    """
    Item 6: "decision <- decision components <- normalized signals <- raw
    signals <- indicators <- validated market data <- raw source data."

    Each link is checked for CONTENT, not presence. An empty dict under the
    right key satisfies a `in` check and satisfies nothing else.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    work = tempfile.mkdtemp(prefix="phase7_chain_")
    try:
        decision = _run(PINNED_DIR, os.path.join(work, "logs"))
        lin = decision.get("lineage")
        assert lin, "the decision carries no lineage section"

        # indicators <- validated market data
        indicators = lin["indicators_at_decision_bar"]
        for name in ("ATR", "RSI", "ADX", "EMA_20", "EMA_50", "SuperTrend",
                     "ST_Direction", "close"):
            assert name in indicators, (
                f"{name} is missing from the decision-bar record. The chain "
                f"stops at the indicator it does not name."
            )
        assert indicators["ATR"] is not None and indicators["ATR"] > 0

        # decision components <- normalized signals <- raw signals
        factors = lin["bias_components"]["factors"]
        assert len(factors) == 6, (
            f"six weighted factors are blended into bias_score; "
            f"{len(factors)} are recorded."
        )
        for name, factor in factors.items():
            for field in ("input", "signed", "weight", "contribution"):
                assert field in factor, f"factor {name} records no {field}"

        # validated market data
        assert lin["inputs"]["struct"]["sha256"], "no hash for the input frame"
        assert lin["inputs"]["struct"]["rows"] > 0

        # raw source data
        assert lin["archive"]["path"], "no archive reference"
    finally:
        shutil.rmtree(work, ignore_errors=True)


def test_the_recorded_contributions_add_up_to_the_score_they_explain():
    """
    The breakdown must be the arithmetic that ran, not a plausible-looking
    account of it.

    This is the check that would have caught a recomputed explanation drifting
    from the real blend — the failure mode that made an out-parameter the
    right shape for this rather than a second function.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    work = tempfile.mkdtemp(prefix="phase7_sum_")
    try:
        decision = _run(PINNED_DIR, os.path.join(work, "logs"))
        components = decision["lineage"]["bias_components"]
        total = sum(f["contribution"] for f in components["factors"].values())
        assert abs(total - components["weighted_sum"]) < 1e-9, (
            f"the six recorded contributions sum to {total}, and the blend "
            f"they claim to explain is {components['weighted_sum']}. A "
            f"breakdown that does not add up to its own total is a second, "
            f"wrong implementation of the score."
        )
        # And the score the decision was made on is reachable from them.
        assert components["bias_score"] == pytest.approx(
            decision["bias"]["score"], abs=1e-9), (
            "the bias score in the lineage record is not the bias score the "
            "decision reports."
        )
    finally:
        shutil.rmtree(work, ignore_errors=True)


# ============================================================
# The hash — what it must and must not react to
# ============================================================

def test_the_hash_changes_when_a_single_candle_changes():
    """
    The auditor's scenario: the exchange revises history. A hash that does not
    move is a hash that cannot detect it.
    """
    from core import lineage
    import pandas as pd

    idx = pd.date_range("2026-01-01", periods=50, freq="4h", tz="UTC")
    df = pd.DataFrame({"open": range(50), "high": range(50), "low": range(50),
                       "close": [float(i) for i in range(50)],
                       "volume": range(50)}, index=idx)
    before = lineage.frame_hash(df)

    revised = df.copy()
    revised.iloc[10, revised.columns.get_loc("close")] += 0.00000001
    assert lineage.frame_hash(revised) != before, (
        "an eight-decimal revision to one candle did not change the hash. "
        "Prices in this engine are quoted to eight decimals."
    )

    # ...and a truncation, which is the other way source data changes.
    assert lineage.frame_hash(df.iloc[:-1]) != before


def test_the_hash_does_not_change_on_column_order_or_a_rebuild():
    """
    The false positive that would make a real one get ignored.

    A hash that moves when nothing about the data moved teaches its reader to
    dismiss it, so column ordering and a round trip through the archive form
    must both leave it alone.
    """
    from core import lineage
    import pandas as pd

    idx = pd.date_range("2026-01-01", periods=20, freq="4h", tz="UTC")
    df = pd.DataFrame({"close": [float(i) / 3 for i in range(20)],
                       "open": [float(i) for i in range(20)],
                       "volume": [float(i) * 10 for i in range(20)]}, index=idx)

    reordered = df[["volume", "close", "open"]]
    assert lineage.frame_hash(df) == lineage.frame_hash(reordered)

    rebuilt = lineage.rebuild_frame(lineage.canonical_text(df))
    assert lineage.frame_hash(rebuilt) == lineage.frame_hash(df)


def test_nan_survives_the_round_trip_as_nan():
    """
    A gap must come back a gap.

    Finding 3 was a missing value at the decision bar being carried through as
    a real number. An archive that restored NaN as 0.0, or as the string
    "nan", would rebuild a run into a different one and reintroduce the same
    class through the back door.
    """
    from core import lineage
    import math
    import pandas as pd

    idx = pd.date_range("2026-01-01", periods=5, freq="4h", tz="UTC")
    df = pd.DataFrame({"close": [1.0, float("nan"), 3.0, 4.0, float("nan")]},
                      index=idx)
    rebuilt = lineage.rebuild_frame(lineage.canonical_text(df))
    values = list(rebuilt["close"])
    assert math.isnan(values[1]) and math.isnan(values[4])
    assert values[0] == 1.0 and values[2] == 3.0
    assert lineage.frame_hash(rebuilt) == lineage.frame_hash(df)


def test_the_run_hash_moves_when_a_bias_weight_moves():
    """
    Finding 6's required action includes "all decision-affecting configuration,
    including risk-model multipliers and bias weights."

    The weights are not in config.py, so before this they were in no record at
    all. Changing 0.30 to 0.35 changes every decision the engine makes while
    leaving the candles, the config and the indicator lengths identical — two
    such runs were previously indistinguishable in the log.
    """
    from core import lineage
    from core import decision_log
    from models import bias_engine

    inputs = {"struct": "a" * 64, "macro": None, "btc": None}
    before = lineage.run_hash(
        inputs, {"config": {"RSI_LENGTH": 14}, "modules": decision_log.module_snapshot()})

    original = bias_engine.WEIGHT_TREND_HEALTH
    try:
        bias_engine.WEIGHT_TREND_HEALTH = 0.35
        after = lineage.run_hash(
            inputs, {"config": {"RSI_LENGTH": 14}, "modules": decision_log.module_snapshot()})
    finally:
        bias_engine.WEIGHT_TREND_HEALTH = original

    assert before != after, (
        "changing the trend-health weight from 0.30 to 0.35 left the run hash "
        "unchanged. Two runs that would reach different decisions carry the "
        "same identity."
    )


# ============================================================
# The archive — evidence, not a copy
# ============================================================

def test_an_edited_archive_reports_itself_as_edited():
    """
    An archive nobody can check is a copy. Verification is what makes it
    evidence.
    """
    from core import lineage
    import pandas as pd

    work = tempfile.mkdtemp(prefix="phase7_tamper_")
    try:
        idx = pd.date_range("2026-01-01", periods=10, freq="4h", tz="UTC")
        df = pd.DataFrame({"close": [float(i) for i in range(10)]}, index=idx)
        path = lineage.write_archive(
            {"struct": df}, work, "AEROUSDT", "4h", "f" * 64)
        assert lineage.verify_archive(path) == {"struct": True}

        payload = lineage.read_archive(path)
        payload["frames"]["struct"]["canonical"] = \
            payload["frames"]["struct"]["canonical"].replace("1.0", "9.0", 1)
        with open(path, "wb") as fh:
            with gzip.GzipFile(fileobj=fh, mode="wb", mtime=0) as gz:
                gz.write(json.dumps(payload, sort_keys=True).encode("utf-8"))

        assert lineage.verify_archive(path) == {"struct": False}, (
            "an archive whose contents were edited after writing still "
            "verifies. It is then a copy of the data, not evidence about it."
        )
    finally:
        shutil.rmtree(work, ignore_errors=True)


def test_pruning_removes_only_old_archives_and_only_archives():
    """
    This is the only code in the engine that deletes anything.

    Viktor's ruling is ninety days of rebuildable history. The risk in
    implementing it is not that it prunes too little.
    """
    from core import lineage

    work = tempfile.mkdtemp(prefix="phase7_prune_")
    try:
        directory = lineage.archive_dir(work)
        os.makedirs(directory)

        old = os.path.join(directory, lineage.archive_name("AERO", "4h", "a" * 16))
        new = os.path.join(directory, lineage.archive_name("AERO", "4h", "b" * 16))
        stranger = os.path.join(directory, "notes_from_viktor.txt")
        for path in (old, new, stranger):
            with open(path, "w") as fh:
                fh.write("x")
        ancient = time.time() - (365 * 86400)
        os.utime(old, (ancient, ancient))
        os.utime(stranger, (ancient, ancient))

        removed = lineage.prune(work, max_age_days=90)

        assert os.path.basename(old) in removed
        assert not os.path.exists(old)
        assert os.path.exists(new), "an archive inside the window was removed"
        assert os.path.exists(stranger), (
            "prune deleted a file that is not an archive. A retention rule "
            "written for one filename format must not age out anything it "
            "was never meant to match."
        )
    finally:
        shutil.rmtree(work, ignore_errors=True)


def test_the_run_just_written_survives_its_own_prune():
    """
    A machine with a wrong clock, or a retention window someone sets to zero
    while testing, must not delete the archive for the decision being made
    right now.
    """
    from core import lineage
    import pandas as pd

    work = tempfile.mkdtemp(prefix="phase7_keep_")
    try:
        idx = pd.date_range("2026-01-01", periods=5, freq="4h", tz="UTC")
        df = pd.DataFrame({"close": [1.0, 2.0, 3.0, 4.0, 5.0]}, index=idx)
        path = lineage.write_archive({"struct": df}, work, "AERO", "4h", "c" * 64)
        ancient = time.time() - (365 * 86400)
        os.utime(path, (ancient, ancient))

        lineage.prune(work, max_age_days=90, keep=[path])
        assert os.path.exists(path), (
            "the archive for the run that just happened was pruned by that "
            "same run."
        )
    finally:
        shutil.rmtree(work, ignore_errors=True)


def test_a_failed_archive_is_recorded_as_absent_rather_than_claimed():
    """
    The defect sequence item 12 was written to close, in the field added to
    close its successor: a record naming a file nothing wrote.
    """
    from core import lineage
    import pandas as pd

    idx = pd.date_range("2026-01-01", periods=3, freq="4h", tz="UTC")
    df = pd.DataFrame({"close": [1.0, 2.0, 3.0]}, index=idx)

    # A path that cannot be created.
    unwritable = os.path.join(os.devnull, "nope")
    assert lineage.write_archive({"struct": df}, unwritable, "A", "4h", "d" * 64) is None


# ============================================================
# The record must reach the log, not just the object
# ============================================================

def test_the_lineage_reaches_the_written_decision_log():
    """
    The router assembles the decision from a whitelist of named fields, so a
    section engine_core produces and the router does not name is dropped
    silently. That is how a record can be correct in memory and absent on
    disk — and the log is the only copy that outlives the process.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    from core import decision_log

    work = tempfile.mkdtemp(prefix="phase7_log_")
    try:
        log_dir = os.path.join(work, "logs")
        decision = _run(PINNED_DIR, log_dir)
        records = decision_log.read(log_dir, "AEROUSDT")
        assert records, "nothing was written to the decision log"

        stored = records[-1]["decision"]
        assert stored.get("lineage"), (
            "the decision object carries a lineage section and the log does "
            "not. The record that survives the process is the one on disk."
        )
        assert stored["lineage"]["run_hash"] == decision["lineage"]["run_hash"]
        assert stored["provenance"]["input_hashes"]["struct"], (
            "the written provenance carries no input hash"
        )
        assert "module_constants" in stored["provenance"], (
            "the written provenance does not record the bias weights"
        )
    finally:
        shutil.rmtree(work, ignore_errors=True)


def test_the_written_record_is_json_and_holds_no_non_finite_numbers():
    """
    The log is JSON Lines. NaN and Infinity are not JSON, and json.dumps emits
    them unquoted by default — producing a file that this engine can read back
    and nothing else can.

    Observation 5 was the same value reaching the panel. This is the same
    value reaching the permanent record.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    work = tempfile.mkdtemp(prefix="phase7_json_")
    try:
        log_dir = os.path.join(work, "logs")
        _run(PINNED_DIR, log_dir)
        path = os.path.join(log_dir, "phase7_decision_log_aerousdt.jsonl")
        with open(path, encoding="utf-8") as fh:
            for number, line in enumerate(fh, 1):
                if not line.strip():
                    continue
                for token in ("NaN", "Infinity", "-Infinity"):
                    assert token not in line, (
                        f"line {number} of the decision log contains the bare "
                        f"token {token}, which is not valid JSON. Every reader "
                        f"except this one rejects the file."
                    )
                json.loads(line)
    finally:
        shutil.rmtree(work, ignore_errors=True)


# ============================================================
# The record must never cost more than it is worth
# ============================================================

def test_an_archive_that_cannot_be_written_does_not_stop_the_analysis(monkeypatch):
    """
    Viktor's ruling of 29 August: degrade, do not halt.

    Archiving is an audit concern touching the disk in the middle of a run.
    An analysis that was computed correctly must still reach the operator when
    the archive fails, and must say the archive is absent rather than claim
    one. A traceability feature able to destroy the analysis it documents
    would be a worse defect than the gap it was added to close.

    The failure is injected at the archive step specifically, rather than by
    breaking the whole log directory. That distinction matters: an unwritable
    log directory already fails a run on this engine and did so before this
    commit -- it is a real defect, recorded in docs/PHASE7_NEXT.md, and it is
    not this one. Testing through it would let this test pass for the wrong
    reason and would claim a fix that was not made.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    from core import lineage

    def explode(*args, **kwargs):
        raise OSError("no space left on device")

    monkeypatch.setattr(lineage, "write_archive", explode)

    work = tempfile.mkdtemp(prefix="phase7_nowrite_")
    try:
        decision = _run(PINNED_DIR, os.path.join(work, "logs"))

        assert not decision.get("error"), (
            f"the run failed because its archive could not be written: "
            f"{decision.get('error')}"
        )
        assert decision["lineage"]["archive"]["path"] is None, (
            "no archive was written and the record names one anyway."
        )
        # The half that costs nothing must survive the half that costs disk.
        assert decision["lineage"]["run_hash"], (
            "the run hash went missing with the archive. The hash is what "
            "keeps an unwritten or pruned run verifiable, so it must not "
            "depend on the write succeeding."
        )
        assert decision["lineage"]["inputs"]["struct"]["sha256"]
        # And the failure must not be laundered into a trading decision.
        assert not decision["degradation"]["missing_inputs"], (
            "a failed archive was recorded as a missing analysis input. That "
            "list blocks trades, and nothing about the analysis was missing -- "
            "only the filing of it failed."
        )
    finally:
        shutil.rmtree(work, ignore_errors=True)


def test_a_run_whose_archive_is_gone_is_still_verifiable_by_its_hash():
    """
    What the ninety-day window actually costs.

    Past the window a decision does not become unverifiable -- it becomes
    verifiable but not rebuildable. This is that distinction as a test: delete
    the archive, and the hash in the log still answers "is the data I can
    fetch today the data this decision was made on?" exactly as well as it did
    on the day.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    from core import decision_log, lineage

    work = tempfile.mkdtemp(prefix="phase7_pruned_")
    try:
        log_dir = os.path.join(work, "logs")
        decision = _run(PINNED_DIR, log_dir)
        archived = decision["lineage"]["archive"]["path"]

        # Age it past the window and prune, as the engine would in ninety days.
        ancient = time.time() - (200 * 86400)
        os.utime(archived, (ancient, ancient))
        removed = lineage.prune(log_dir, max_age_days=90)
        assert os.path.basename(archived) in removed
        assert not os.path.exists(archived)

        # The log is untouched by pruning, and still identifies the input.
        record = decision_log.read(log_dir, "AEROUSDT")[-1]
        stored_hash = record["decision"]["lineage"]["inputs"]["struct"]["sha256"]
        assert stored_hash, "pruning took the hash with the archive"

        # Re-derive the hash from data available today. Same data, same digest.
        from data.data_fetcher import DataFetcher, data_fetcher
        original = data_fetcher.base_url
        try:
            data_fetcher.base_url = UNREACHABLE
            DataFetcher.set_pinned_source(PINNED_DIR)
            today = data_fetcher.get_tf("AEROUSDT", "4h", limit=450)
        finally:
            DataFetcher.clear_pinned_source()
            data_fetcher.base_url = original

        assert lineage.frame_hash(today) == stored_hash, (
            "the hash recorded for a run no longer matches the same data "
            "re-read. Either the hash is not stable or the input changed -- "
            "and telling those apart is the whole job of this field."
        )
    finally:
        shutil.rmtree(work, ignore_errors=True)


def test_the_recorded_archive_path_is_spelled_the_same_on_every_platform():
    """
    A path written into a permanent record must not depend on which machine
    wrote it.

    This defect shipped. `os.path.join` produces a backslash on Windows and a
    forward slash on Linux, so the same run archived on the two platforms
    recorded two different strings for one file -- and the golden snapshot,
    baselined on Linux, could only ever match on Linux. Viktor's machine caught
    it on the first run; every hash and every number matched, and the only
    difference in the whole decision object was one separator.

    Nothing pinned the format, which is why nothing noticed. This pins it.
    """
    from core import lineage
    import pandas as pd

    work = tempfile.mkdtemp(prefix="phase7_path_")
    try:
        idx = pd.date_range("2026-01-01", periods=5, freq="4h", tz="UTC")
        df = pd.DataFrame({"close": [1.0, 2.0, 3.0, 4.0, 5.0]}, index=idx)
        path = lineage.write_archive(
            {"struct": df}, "logs/", "TESTUSDT", "4h", "e" * 64)
        try:
            assert path is not None
            assert "\\" not in path, (
                f"the recorded archive path {path!r} contains a backslash. On "
                f"another platform the same run records a different string for "
                f"the same file."
            )
            assert path.startswith("logs/archive/")
            # And the spelling must still open the file it names.
            assert os.path.exists(path)
            assert lineage.verify_archive(path) == {"struct": True}
        finally:
            shutil.rmtree("logs", ignore_errors=True)
    finally:
        shutil.rmtree(work, ignore_errors=True)
