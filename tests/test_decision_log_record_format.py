"""
The decision log is JSON a strict reader accepts, and its reader says what it
skipped.

FOUND 21 SEPTEMBER 2026, in the deferred read of core/decision_log.py
(docs/PHASE7_NEXT.md, "Review findings", 19-21).

19. write() called json.dumps with its default allow_nan=True, so a NaN in the
    decision object -- the router's deliberate "not measured" -- was written as
    the bare token NaN. That is not JSON. Python reads it back; jq and
    JavaScript's JSON.parse reject the whole line. One record in Viktor's live
    log (6 September, swing_struct) carried it. Now every non-finite float is
    written as null, and allow_nan=False stops a bare NaN reaching the file.

20. read() skipped any line it could not parse, anywhere in the file, and said
    nothing. A corrupted record in the middle of the history vanished from
    what it returned. It still skips -- one damaged line must not make the
    history unreadable -- but read_with_report() returns the skipped line
    numbers and read() logs them.

21. The module docstring said the record's source is "the pinned directory";
    the engine records the literal "pinned".

"Strict" in these tests means json.loads with a parse_constant that refuses
NaN, Infinity and -Infinity -- the three tokens Python accepts and the JSON
standard does not.

Fixture-free, per run_tests.py: temporary directories are made and removed
inside each test.
"""

import json
import logging
import math
import os
import shutil
import sys
import tempfile
import types

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

NAN = float("nan")
INF = float("inf")


def _strict_loads(line):
    def refuse(token):
        raise ValueError(f"non-JSON token {token!r}")
    return json.loads(line, parse_constant=refuse)


def _config():
    return types.SimpleNamespace(LOG_DIR="unused/", engine_version="test")


def _write_and_read_raw(decision):
    from core import decision_log

    tmp = tempfile.mkdtemp(prefix="phase7_logfmt_")
    try:
        path = decision_log.write(decision, _config(), log_dir=tmp)
        assert path, "write() returned None -- the record was not written"
        with open(path, encoding="utf-8") as f:
            lines = [l for l in f.read().splitlines() if l]
        assert len(lines) == 1, lines
        return lines[0]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _decision_with_non_finite_values():
    return {
        "symbol": "TESTUSDT",
        "timeframe": "4h",
        "structure": {"swing_struct": NAN, "hvn": 1.25},
        "risk": {"targets": (NAN, 2.0, INF), "atr_stop": -INF},
        "entry": {"components": [{"score": NAN}, {"score": 3.0}]},
    }


# --- 19 ----------------------------------------------------------------------

def test_a_record_with_nan_is_strict_json():
    line = _write_and_read_raw(_decision_with_non_finite_values())
    record = _strict_loads(line)          # raises on NaN / Infinity
    d = record["decision"]
    assert d["structure"]["swing_struct"] is None
    assert d["structure"]["hvn"] == 1.25
    assert d["risk"]["targets"] == [None, 2.0, None]
    assert d["risk"]["atr_stop"] is None
    assert d["entry"]["components"] == [{"score": None}, {"score": 3.0}]


def test_numpy_nan_is_written_as_null_too():
    import numpy as np

    line = _write_and_read_raw({"symbol": "TESTUSDT",
                                "structure": {"swing_struct": np.float64("nan")}})
    assert _strict_loads(line)["decision"]["structure"]["swing_struct"] is None


def test_writing_does_not_change_the_callers_decision_object():
    decision = _decision_with_non_finite_values()
    _write_and_read_raw(decision)
    assert math.isnan(decision["structure"]["swing_struct"])
    assert isinstance(decision["risk"]["targets"], tuple)
    assert math.isinf(decision["risk"]["targets"][2])


def test_finite_values_are_written_exactly_as_before():
    """
    Negative control: a guard that nulled every float would pass the tests
    above.
    """
    line = _write_and_read_raw({"symbol": "TESTUSDT",
                                "risk": {"confidence_score": 0.0,
                                         "targets": (1.5, 2.5, 3.5)},
                                "flag": True, "count": 3})
    d = _strict_loads(line)["decision"]
    assert d["risk"] == {"confidence_score": 0.0, "targets": [1.5, 2.5, 3.5]}
    assert d["flag"] is True and d["count"] == 3


# --- 20 ----------------------------------------------------------------------

def _log_with_damage(tmp):
    from core import decision_log

    path = decision_log.log_path(tmp, "TESTUSDT")
    with open(path, "w", encoding="utf-8") as f:
        f.write('{"n": 1}\n')
        f.write('{"n": 2, "torn in the mid\n')     # line 2: damaged, not last
        f.write('{"n": 3}\n')
        f.write('{"n": 4, "torn at the e')         # line 4: torn final line
    return path


def test_read_with_report_names_every_skipped_line():
    from core import decision_log

    tmp = tempfile.mkdtemp(prefix="phase7_logread_")
    try:
        _log_with_damage(tmp)
        records, skipped = decision_log.read_with_report(tmp, "TESTUSDT")
        assert [r["n"] for r in records] == [1, 3]
        assert skipped == [2, 4]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_read_still_returns_the_good_records_and_warns_about_the_rest():
    from core import decision_log

    seen = []

    class Catch(logging.Handler):
        def emit(self, record):
            seen.append(record.getMessage())

    handler = Catch(level=logging.WARNING)
    log = logging.getLogger(decision_log.__name__)
    log.addHandler(handler)
    tmp = tempfile.mkdtemp(prefix="phase7_logread_")
    try:
        _log_with_damage(tmp)
        records = decision_log.read(tmp, "TESTUSDT")
        assert [r["n"] for r in records] == [1, 3]
        assert any("[2, 4]" in m for m in seen), seen
    finally:
        log.removeHandler(handler)
        shutil.rmtree(tmp, ignore_errors=True)


def test_a_clean_log_reports_nothing_skipped():
    from core import decision_log

    tmp = tempfile.mkdtemp(prefix="phase7_logread_")
    try:
        with open(decision_log.log_path(tmp, "TESTUSDT"), "w", encoding="utf-8") as f:
            f.write('{"n": 1}\n{"n": 2}\n')
        records, skipped = decision_log.read_with_report(tmp, "TESTUSDT")
        assert [r["n"] for r in records] == [1, 2] and skipped == []
        assert decision_log.read_with_report(tmp, "NOSUCHSYMBOL") == ([], [])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# --- 21 ----------------------------------------------------------------------

def test_the_docstring_names_the_source_the_engine_records():
    from core import decision_log

    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(here, "core", "engine_core.py"), encoding="utf-8") as f:
        engine = f.read()
    assert '"source": "pinned" if data_fetcher.pinned_source()' in engine
    assert 'the literal "pinned"' in decision_log.__doc__
    assert "source          the pinned directory" not in decision_log.__doc__
