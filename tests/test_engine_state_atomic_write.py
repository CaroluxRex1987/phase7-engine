"""
Tier 1, Task 11 (18 September 2026) -- _save_state's non-atomic write.

THE FINDING

core/engine_core.py's _save_state opened the state file with open(path, "w")
and then called json.dump(state, f). open(..., "w") truncates the file to
zero length *before* a single byte of the new state is written. If the
process is interrupted between that truncation and a complete json.dump --
killed, the disk fills, the box loses power -- the file left on disk is
empty or a partial JSON fragment: not the old state and not the new one.

_load_state's own except clause swallows that outcome as "first run, or file
is corrupt" and returns {} -- so Exit Watch silently loses its comparison
baseline instead of being told a write was interrupted. Same class of
problem the 29 August degrade-not-halt ruling exists to prevent: a
mechanical failure destroying more than the specific thing that failed.

THE FIX

Write the new state to a temp file inside the same directory (so the
replace is on one filesystem, not two) and os.replace() it over the real
path. os.replace() is documented as atomic on POSIX, and on Windows when the
destination exists, on the same filesystem -- so _load_state can only ever
see the complete old file or the complete new file, never a partial one.

These tests exercise _save_state and _load_state directly -- no pandas_ta
pipeline run, no network -- since the atomicity property lives entirely in
these two methods' own I/O. The pandas_ta guard below is only because
importing core.engine_core at all pulls in indicators.indicators, which
imports pandas_ta at module level.
"""

import json
import os
import tempfile

import pytest


def _engine_available():
    try:
        import pandas_ta  # noqa: F401
        return True
    except Exception:
        return False


def _engine():
    import core.engine_core as ec
    return ec.Phase7Engine()


def test_state_round_trips_through_save_and_load():
    """Control: the ordinary path must still work."""
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    from core import config

    engine = _engine()
    work = tempfile.mkdtemp(prefix="phase7_state_roundtrip_")
    original_log = config.LOG_DIR
    try:
        config.LOG_DIR = work
        state = {"flip": True, "price": 123.45}
        engine._save_state("AEROUSDT", "4h", state)
        loaded = engine._load_state("AEROUSDT", "4h")
        assert loaded == state, f"round trip changed the state: {loaded!r}"
    finally:
        config.LOG_DIR = original_log


def test_no_temp_file_is_left_behind_after_a_successful_save():
    """
    The atomic-write mechanism's own litter must not survive it -- a stray
    .tmp file sitting next to the real state file would be exactly the kind
    of "ignored file that turns out to matter" this project has been bitten
    by before (docs/audit_package/round*/, before the .gitignore fix).
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    from core import config

    engine = _engine()
    work = tempfile.mkdtemp(prefix="phase7_state_notemp_")
    original_log = config.LOG_DIR
    try:
        config.LOG_DIR = work
        engine._save_state("AEROUSDT", "4h", {"flip": False})
        leftovers = [
            f for f in os.listdir(work)
            if f != "phase7_state_AEROUSDT_4h.json"
        ]
        assert not leftovers, f"unexpected files left in the log dir: {leftovers}"
    finally:
        config.LOG_DIR = original_log


def test_a_dump_failure_midway_leaves_the_prior_state_untouched():
    """
    THE DEFECT ITSELF, reproduced directly.

    Simulates the crash this fix protects against: json.dump raises after
    writing part of the new state. Before the fix (open(path, "w") first),
    the real file would already have been truncated to zero bytes by that
    point -- the prior state gone, with no way back to it. After the fix,
    the truncation happens only to a temp file that a failed dump never gets
    promoted from, so the real path still holds the old, complete state.

    Restores json.dump by hand (rather than via pytest's monkeypatch
    fixture) so this test takes no fixture arguments -- run_tests.py's own
    runner does not do pytest-style fixture injection, and a test that
    declared one would join the existing, unrelated pile of "missing
    required positional argument" entries that mismatch is already known
    to produce (see the 32-error baseline this project's suite has carried
    since before this patch), rather than reporting a real result there.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    from core import config
    import core.engine_core as ec

    engine = _engine()
    work = tempfile.mkdtemp(prefix="phase7_state_crash_")
    original_log = config.LOG_DIR
    real_dump = ec.json.dump
    try:
        config.LOG_DIR = work
        old_state = {"flip": True, "price": 100.0}
        engine._save_state("AEROUSDT", "4h", old_state)

        def _dump_then_crash(obj, fp):
            fp.write('{"flip": tr')  # a real partial write, then die
            raise OSError("simulated crash mid-write")

        ec.json.dump = _dump_then_crash
        try:
            engine._save_state("AEROUSDT", "4h", {"flip": False, "price": 200.0})
        finally:
            ec.json.dump = real_dump

        recovered = engine._load_state("AEROUSDT", "4h")
        assert recovered == old_state, (
            f"a crash mid-write corrupted the prior state: {recovered!r} -- "
            f"expected the untouched old state {old_state!r}"
        )

        path = engine._state_path("AEROUSDT", "4h")
        with open(path) as f:
            on_disk = json.load(f)
        assert on_disk == old_state, (
            "the file on disk is not valid, complete JSON of the old state"
        )

        leftovers = [
            f for f in os.listdir(work) if f != os.path.basename(path)
        ]
        assert not leftovers, (
            f"the failed write's temp file was not cleaned up: {leftovers}"
        )
    finally:
        config.LOG_DIR = original_log
