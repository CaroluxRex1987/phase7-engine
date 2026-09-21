"""
An archive answers to the decision log, not only to itself; it is JSON a
strict reader accepts; and the overwrite its name allows is the one documented.

FOUND 21 SEPTEMBER 2026, in the deferred read of core/lineage.py
(docs/PHASE7_NEXT.md, "Review findings", 23, 24, and 19's archive half).

24. verify_archive() compares each stored frame with the digest stored beside
    it in the same file, so an edit that rewrites both passes. The check
    against the decision log's input_hashes existed only in the tests. Now
    lineage.verify_against_record() does it.

19. write_archive() called json.dumps with its default allow_nan=True, so a
    non-finite float in the payload would be written as the bare token NaN.
    Latent -- only `meta` can carry a float, and no fingerprinted constant is
    non-finite today -- but the same shape the decision log had.

23. The archive's name is run_hash, which excludes code_hash, so a rerun on
    identical input and settings under different code rewrites the file and
    the earlier run's meta.code with it. A documentation correction; the test
    below pins the behaviour the docstring now states, so the two cannot drift.

"Strict" means json.loads with a parse_constant that refuses NaN, Infinity
and -Infinity. Fixture-free, per run_tests.py: temporary directories are made
and removed inside each test.
"""

import gzip
import json
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

RUN_ID = "ab" * 32


def _frames():
    import pandas as pd

    idx = pd.date_range("2026-01-01", periods=12, freq="4h", tz="UTC")
    struct = pd.DataFrame({"close": [float(i) for i in range(12)],
                           "volume": [10.0 + i for i in range(12)]}, index=idx)
    macro = pd.DataFrame({"close": [100.0 + i for i in range(12)]}, index=idx)
    return {"struct": struct, "macro": macro}


def _record(frames, run_id=RUN_ID, wrap=True, btc_hash=None):
    """A decision-log line shaped as decision_log.write() writes it."""
    from core import lineage

    hashes = {name: lineage.frame_hash(df) for name, df in frames.items()}
    hashes["btc"] = btc_hash
    decision = {"provenance": {"run_hash": run_id, "input_hashes": hashes}}
    return {"logged_at": "x", "decision": decision} if wrap else decision


def _rewrite(path, payload):
    with open(path, "wb") as fh:
        with gzip.GzipFile(fileobj=fh, mode="wb", mtime=0) as gz:
            gz.write(json.dumps(payload, sort_keys=True).encode("utf-8"))


def _strict_loads(text):
    def refuse(token):
        raise ValueError(f"non-JSON token {token!r}")
    return json.loads(text, parse_constant=refuse)


# ============================================================
# 24 -- the archive against its record
# ============================================================

def test_an_archive_matches_the_record_of_the_run_that_wrote_it():
    from core import lineage

    work = tempfile.mkdtemp(prefix="phase7_vrec_")
    try:
        frames = _frames()
        path = lineage.write_archive(frames, work, "AEROUSDT", "4h", RUN_ID)
        assert path
        assert lineage.verify_against_record(path, _record(frames)) == {
            "run_hash": True, "frames": {"macro": True, "struct": True}}
    finally:
        shutil.rmtree(work, ignore_errors=True)


def test_an_edit_that_rewrites_the_frame_and_its_digest_is_caught_by_the_record():
    """
    The finding itself. verify_archive() passes this edit; the record does not.
    """
    import hashlib
    from core import lineage

    work = tempfile.mkdtemp(prefix="phase7_vrec_")
    try:
        frames = _frames()
        path = lineage.write_archive(frames, work, "AEROUSDT", "4h", RUN_ID)
        payload = lineage.read_archive(path)
        edited = payload["frames"]["struct"]["canonical"].replace("5.0", "7.0", 1)
        assert edited != payload["frames"]["struct"]["canonical"]
        payload["frames"]["struct"]["canonical"] = edited
        payload["frames"]["struct"]["sha256"] = \
            hashlib.sha256(edited.encode("utf-8")).hexdigest()
        _rewrite(path, payload)

        assert lineage.verify_archive(path) == {"struct": True, "macro": True}, (
            "the self-check was expected to pass a consistent edit -- that is "
            "the limit finding 24 names. If it now fails, this test's premise "
            "has changed and should be re-read."
        )
        assert lineage.verify_against_record(path, _record(frames)) == {
            "run_hash": True, "frames": {"macro": True, "struct": False}}, (
            "an archive edited together with its own digest still matches the "
            "decision log's hash. The record is then not being consulted."
        )
    finally:
        shutil.rmtree(work, ignore_errors=True)


def test_the_stored_digest_is_not_what_gets_compared():
    """
    An edit to the digest alone, with the frame intact, must still match the
    record: the frame is re-hashed, not the digest beside it trusted.
    """
    from core import lineage

    work = tempfile.mkdtemp(prefix="phase7_vrec_")
    try:
        frames = _frames()
        path = lineage.write_archive(frames, work, "AEROUSDT", "4h", RUN_ID)
        payload = lineage.read_archive(path)
        payload["frames"]["struct"]["sha256"] = "0" * 64
        _rewrite(path, payload)

        assert lineage.verify_archive(path)["struct"] is False
        assert lineage.verify_against_record(path, _record(frames))["frames"] == {
            "macro": True, "struct": True}
    finally:
        shutil.rmtree(work, ignore_errors=True)


def test_a_different_run_hash_is_reported():
    from core import lineage

    work = tempfile.mkdtemp(prefix="phase7_vrec_")
    try:
        frames = _frames()
        path = lineage.write_archive(frames, work, "AEROUSDT", "4h", RUN_ID)
        result = lineage.verify_against_record(path, _record(frames, run_id="cd" * 32))
        assert result["run_hash"] is False
        assert result["frames"] == {"macro": True, "struct": True}
    finally:
        shutil.rmtree(work, ignore_errors=True)


def test_a_frame_on_one_side_only_does_not_match():
    from core import lineage

    work = tempfile.mkdtemp(prefix="phase7_vrec_")
    try:
        frames = _frames()
        # The record hashed a btc frame the archive does not hold.
        path = lineage.write_archive(frames, work, "AEROUSDT", "4h", RUN_ID)
        result = lineage.verify_against_record(
            path, _record(frames, btc_hash="e" * 64))
        assert result["frames"] == {"btc": False, "macro": True, "struct": True}

        # The archive holds a frame the record did not hash.
        record = _record({"struct": frames["struct"]})
        assert lineage.verify_against_record(path, record)["frames"] == {
            "macro": False, "struct": True}
    finally:
        shutil.rmtree(work, ignore_errors=True)


def test_nothing_to_compare_returns_empty():
    from core import lineage

    work = tempfile.mkdtemp(prefix="phase7_vrec_")
    try:
        frames = _frames()
        path = lineage.write_archive(frames, work, "AEROUSDT", "4h", RUN_ID)
        # A record written before the lineage fields existed.
        assert lineage.verify_against_record(path, {"decision": {"provenance": {}}}) == {}
        assert lineage.verify_against_record(path, {"decision": {}}) == {}
        # Every recorded hash null.
        assert lineage.verify_against_record(path, {"decision": {"provenance": {
            "run_hash": RUN_ID, "input_hashes": {"struct": None}}}}) == {}
        assert lineage.verify_against_record(path, None) == {}
        # No archive there.
        missing = os.path.join(work, "archive", "absent.json.gz")
        assert lineage.verify_against_record(missing, _record(frames)) == {}
    finally:
        shutil.rmtree(work, ignore_errors=True)


def test_the_decision_object_is_accepted_as_well_as_the_log_line():
    from core import lineage

    work = tempfile.mkdtemp(prefix="phase7_vrec_")
    try:
        frames = _frames()
        path = lineage.write_archive(frames, work, "AEROUSDT", "4h", RUN_ID)
        assert lineage.verify_against_record(path, _record(frames, wrap=False)) == \
            lineage.verify_against_record(path, _record(frames, wrap=True))
    finally:
        shutil.rmtree(work, ignore_errors=True)


# ============================================================
# 19 -- the archive's JSON
# ============================================================

def _archive_text(meta):
    from core import lineage

    work = tempfile.mkdtemp(prefix="phase7_arcjson_")
    try:
        path = lineage.write_archive(
            _frames(), work, "AEROUSDT", "4h", RUN_ID, meta=meta)
        assert path, "write_archive returned None"
        with gzip.open(path, "rb") as gz:
            return gz.read().decode("utf-8")
    finally:
        shutil.rmtree(work, ignore_errors=True)


def test_a_non_finite_value_in_the_archive_is_written_as_null():
    text = _archive_text({"config": {"A": float("nan"), "B": [float("inf"), -float("inf")]}})
    payload = _strict_loads(text)
    assert payload["meta"]["config"] == {"A": None, "B": [None, None]}


def test_finite_values_in_the_archive_are_unchanged():
    meta = {"engine_version": "v", "config": {"A": 1.5, "B": [2, 0.1], "C": True, "D": None}}
    payload = _strict_loads(_archive_text(meta))
    assert payload["meta"] == meta


def test_the_callers_meta_is_not_modified():
    meta = {"config": {"A": float("nan")}}
    _archive_text(meta)
    assert meta["config"]["A"] != meta["config"]["A"], "the caller's NaN was replaced"


# ============================================================
# 23 -- the overwrite the docstring now states
# ============================================================

def test_a_rerun_under_different_code_rewrites_the_archive_and_its_meta_code():
    """
    Pins the behaviour write_archive()'s docstring documents. If a later change
    names archives so that this no longer happens, this test fails and the
    docstring has to be updated with it.
    """
    from core import lineage

    work = tempfile.mkdtemp(prefix="phase7_rerun_")
    try:
        frames = _frames()
        first = lineage.write_archive(frames, work, "AEROUSDT", "4h", RUN_ID,
                                      meta={"code": {"code_hash": "1" * 64}})
        second = lineage.write_archive(frames, work, "AEROUSDT", "4h", RUN_ID,
                                       meta={"code": {"code_hash": "2" * 64}})
        assert first == second
        assert len(os.listdir(os.path.join(work, "archive"))) == 1
        assert lineage.read_archive(second)["meta"]["code"]["code_hash"] == "2" * 64
        assert "FINDING 23" in lineage.write_archive.__doc__
        assert "code_hash" in lineage.write_archive.__doc__
    finally:
        shutil.rmtree(work, ignore_errors=True)
