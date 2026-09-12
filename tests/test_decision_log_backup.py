"""
utils/decision_log_backup.py -- pins the behaviour Rulings, 11 September
2026 ("The live decision log") actually asked for: committed dated
snapshots, never a silent overwrite of one already taken.

No pytest fixtures (monkeypatch, tmp_path) are used anywhere in this file.
run_tests.py is a fixture-free runner -- it calls every test_* function with
no arguments -- so a fixture parameter here would not fail loudly, it would
become a collection-time TypeError there and move the watched error count.
tempfile.TemporaryDirectory() gives the same isolation without one, matching
the existing pattern in test_unwritable_log_dir.py.
"""

import os
import tempfile

from utils.decision_log_backup import take_snapshot


def _write(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def test_a_live_log_is_copied_to_a_dated_snapshot():
    with tempfile.TemporaryDirectory() as log_dir, tempfile.TemporaryDirectory() as backup_dir:
        source = os.path.join(log_dir, "phase7_decision_log_aerousdt.jsonl")
        _write(source, '{"a": 1}\n')

        results = take_snapshot(log_dir=log_dir, backup_dir=backup_dir, today="20260906")

        assert len(results) == 1
        _, dest, action = results[0]
        assert action == "copied"
        assert os.path.basename(dest) == "phase7_decision_log_aerousdt_20260906.jsonl"
        with open(dest, encoding="utf-8") as f:
            assert f.read() == '{"a": 1}\n'


def test_multiple_symbols_each_get_their_own_dated_snapshot():
    with tempfile.TemporaryDirectory() as log_dir, tempfile.TemporaryDirectory() as backup_dir:
        _write(os.path.join(log_dir, "phase7_decision_log_aerousdt.jsonl"), "aero\n")
        _write(os.path.join(log_dir, "phase7_decision_log_testusdt.jsonl"), "test\n")

        results = take_snapshot(log_dir=log_dir, backup_dir=backup_dir, today="20260906")

        dest_names = sorted(os.path.basename(dest) for _, dest, _ in results)
        assert dest_names == [
            "phase7_decision_log_aerousdt_20260906.jsonl",
            "phase7_decision_log_testusdt_20260906.jsonl",
        ]
        assert all(action == "copied" for _, _, action in results)


def test_a_same_day_rerun_with_identical_content_is_a_no_op():
    with tempfile.TemporaryDirectory() as log_dir, tempfile.TemporaryDirectory() as backup_dir:
        source = os.path.join(log_dir, "phase7_decision_log_aerousdt.jsonl")
        _write(source, '{"a": 1}\n')

        take_snapshot(log_dir=log_dir, backup_dir=backup_dir, today="20260906")
        results = take_snapshot(log_dir=log_dir, backup_dir=backup_dir, today="20260906")

        assert len(results) == 1
        assert results[0][2] == "skipped (already backed up, identical)"


def test_a_same_day_rerun_with_new_content_is_refused_without_force():
    """
    A snapshot is a historical record, not a rolling copy. If the live log
    grew since the day's first snapshot, overwriting that snapshot silently
    would destroy the point-in-time record this whole mechanism exists to
    keep -- so the default is to refuse, not to clobber.
    """
    with tempfile.TemporaryDirectory() as log_dir, tempfile.TemporaryDirectory() as backup_dir:
        source = os.path.join(log_dir, "phase7_decision_log_aerousdt.jsonl")
        _write(source, '{"a": 1}\n')
        take_snapshot(log_dir=log_dir, backup_dir=backup_dir, today="20260906")

        _write(source, '{"a": 1}\n{"a": 2}\n')
        results = take_snapshot(log_dir=log_dir, backup_dir=backup_dir, today="20260906")

        assert len(results) == 1
        _, dest, action = results[0]
        assert action.startswith("REFUSED")
        # The refusal must not have touched the existing snapshot.
        with open(dest, encoding="utf-8") as f:
            assert f.read() == '{"a": 1}\n'


def test_force_overwrites_a_changed_same_day_snapshot():
    with tempfile.TemporaryDirectory() as log_dir, tempfile.TemporaryDirectory() as backup_dir:
        source = os.path.join(log_dir, "phase7_decision_log_aerousdt.jsonl")
        _write(source, '{"a": 1}\n')
        take_snapshot(log_dir=log_dir, backup_dir=backup_dir, today="20260906")

        _write(source, '{"a": 1}\n{"a": 2}\n')
        results = take_snapshot(log_dir=log_dir, backup_dir=backup_dir, today="20260906", force=True)

        assert results[0][2] == "copied"
        with open(results[0][1], encoding="utf-8") as f:
            assert f.read() == '{"a": 1}\n{"a": 2}\n'


def test_dry_run_reports_without_writing_anything():
    with tempfile.TemporaryDirectory() as log_dir, tempfile.TemporaryDirectory() as backup_dir:
        _write(os.path.join(log_dir, "phase7_decision_log_aerousdt.jsonl"), '{"a": 1}\n')

        results = take_snapshot(log_dir=log_dir, backup_dir=backup_dir, today="20260906", dry_run=True)

        assert results[0][2] == "skipped (dry run)"
        assert os.listdir(backup_dir) == []


def test_no_live_logs_is_reported_as_nothing_to_back_up_not_an_error():
    with tempfile.TemporaryDirectory() as log_dir, tempfile.TemporaryDirectory() as backup_dir:
        results = take_snapshot(log_dir=log_dir, backup_dir=backup_dir, today="20260906")
        assert results == []


def test_a_missing_log_directory_is_the_same_as_an_empty_one():
    with tempfile.TemporaryDirectory() as backup_dir:
        results = take_snapshot(
            log_dir=os.path.join(backup_dir, "does_not_exist"),
            backup_dir=backup_dir,
            today="20260906",
        )
        assert results == []
