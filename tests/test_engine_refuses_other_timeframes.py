"""
B5's guard: the engine decides on 4h candles only -- 26 November 2026.

DECISIONS, "Ruling, 20 October 2026 -- B5: 4h only for now, and a guard
refuses any other timeframe". The thresholds (the volatility bands, the stop
limits, the structure threshold, the VWMA and HVN bands) are percentages of
price set for 4h candles; on AERO's daily candles every bar read EXTREME
VOLATILITY. Point 2 of the ruling asks for the refusal to be the code's, "so
that the safe choice is the only one available rather than a rule to
remember". Until this file, a search of the engine's .py files found no
refusal of another timeframe: main.py refused only a missing or empty one,
and data/validation.py's bar table accepts every timeframe it lists.

The guard is Phase7Engine.run's, the one place every route to a decision
passes: main.py's run_pair and live_trading.run_once through the router, and
a direct call. These tests check that every other timeframe is refused
before anything is fetched, read or written; that a config.TIMEFRAME changed
to another is refused the same way, including through main.py; and that 4h,
the default, still passes -- without which the guard would refuse every run.

No fixtures, so run_tests.py runs every test here and its watched error count
does not move. The engine needs pandas_ta; without it the three behavioural
tests skip, and the source test still runs.
"""

import ast
import io
import os
import shutil
import tempfile

import pytest

from conftest import REPO_ROOT

ENGINE_CORE = os.path.join(REPO_ROOT, "core", "engine_core.py")
CONFIG = os.path.join(REPO_ROOT, "core", "config.py")

SYMBOL = "TESTUSDT"

# Each a timeframe the bar table knows or a near miss of 4h. Exact match is
# the rule: finding 26 made the bar table case-sensitive ("1M" is a month,
# "1m" a minute), so "4H" is not 4h to this engine either.
REFUSED = ["1h", "1d", "15m", "1w", "1M", "4H", " 4h", "4h ", "240m"]


def _engine_available():
    try:
        import pandas_ta  # noqa: F401
        return True
    except Exception:
        return False


class _Fetcher:
    """Stands in for data_fetcher: records every attribute asked of it."""

    def __init__(self):
        self.asked = []

    def __getattr__(self, name):
        self.asked.append(name)

        def call(*args, **kwargs):
            self.asked.append((name, args))
            return None

        return call


class _Isolated:
    """
    The engine's data_fetcher replaced, and config.LOG_DIR and CHART_DIR
    pointed at an empty directory of their own, for the length of a block.
    Restored on the way out, however the block ends.
    """

    def __init__(self, timeframe_setting=None):
        self.timeframe_setting = timeframe_setting

    def __enter__(self):
        import core.engine_core as ec
        from core import config

        self.ec, self.config = ec, config
        self.fetcher = _Fetcher()
        self.saved = (ec.data_fetcher, config.LOG_DIR, config.CHART_DIR,
                      config.TIMEFRAME, config.SYMBOL)
        self.directory = tempfile.mkdtemp(prefix="phase7_b5_guard_")
        ec.data_fetcher = self.fetcher
        config.LOG_DIR = self.directory
        config.CHART_DIR = os.path.join(self.directory, "charts")
        if self.timeframe_setting is not None:
            config.TIMEFRAME = self.timeframe_setting
        return self

    def written(self):
        found = []
        for root, dirs, files in os.walk(self.directory):
            found.extend(os.path.join(root, name) for name in dirs + files)
        return found

    def __exit__(self, *exc):
        (self.ec.data_fetcher, self.config.LOG_DIR, self.config.CHART_DIR,
         self.config.TIMEFRAME, self.config.SYMBOL) = self.saved
        shutil.rmtree(self.directory, ignore_errors=True)
        return False


def test_the_engine_refuses_every_timeframe_but_4h():
    """Asked for another timeframe, the run ends at once, naming it."""
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    for timeframe in REFUSED:
        with _Isolated() as box:
            result = box.ec.Phase7Engine().run(
                symbol=SYMBOL, timeframe=timeframe, save_chart=False)
            written = box.written()
            asked = list(box.fetcher.asked)

        assert isinstance(result, dict) and "error" in result, (
            f"timeframe {timeframe!r} was not refused: {sorted(result)[:12]}"
        )
        assert result["error"].startswith("Refused: timeframe"), (
            f"timeframe {timeframe!r} ended with another error: "
            f"{result['error']!r}"
        )
        assert repr(timeframe) in result["error"], (
            f"the refusal does not name the timeframe asked for: "
            f"{result['error']!r}"
        )
        assert "4h" in result["error"], (
            f"the refusal does not say which timeframe is decided on: "
            f"{result['error']!r}"
        )
        assert sorted(result) == ["error", "symbol", "timeframe"], (
            f"the refusal carries more than a failed fetch's error object "
            f"does: {sorted(result)}"
        )
        assert asked == [], (
            f"timeframe {timeframe!r}: the data fetcher was used before the "
            f"refusal: {asked}"
        )
        assert written == [], (
            f"timeframe {timeframe!r}: the refused run wrote {written}"
        )


def test_a_configured_timeframe_other_than_4h_is_refused_through_main():
    """
    The case the guard exists for: config.TIMEFRAME edited to another value.
    A run given no timeframe takes the setting, and is refused -- directly,
    and through main.py's run_pair, which counts the pair as failed.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    import main

    with _Isolated(timeframe_setting="1h") as box:
        direct = box.ec.Phase7Engine().run(symbol=SYMBOL, save_chart=False)
        through_main = main.run_pair(SYMBOL)
        written = box.written()
        asked = list(box.fetcher.asked)

    assert "error" in direct and direct["error"].startswith(
        "Refused: timeframe '1h'"), (
        f"a config.TIMEFRAME of '1h' was not refused: {direct!r}"
    )
    assert direct["timeframe"] == "1h", direct
    assert through_main is False, (
        "main.run_pair reported success for a refused timeframe"
    )
    assert asked == [], f"the data fetcher was used: {asked}"
    assert written == [], f"the refused runs wrote {written}"


def test_4h_passes_the_guard():
    """
    The control: 4h, given or taken from the default setting, goes past the
    guard to the fetch. The stand-in fetcher returns nothing, so the run ends
    there with the fetch's own error, not the refusal.
    """
    if not _engine_available():
        pytest.skip("pandas_ta not installed")

    for given in ("4h", None):
        with _Isolated() as box:
            assert box.config.TIMEFRAME == "4h"
            result = box.ec.Phase7Engine().run(
                symbol=SYMBOL, timeframe=given, save_chart=False)
            asked = list(box.fetcher.asked)

        assert "error" in result, result
        assert not result["error"].startswith("Refused"), (
            f"4h (given as {given!r}) was refused: {result['error']!r}"
        )
        assert result["error"] == "Invalid or insufficient market data", (
            f"4h (given as {given!r}) did not end at the fetch: "
            f"{result['error']!r}"
        )
        assert ("get_tf", (SYMBOL, "4h")) in asked, (
            f"4h (given as {given!r}) never asked for its candles: {asked}"
        )


def _module_string(path, name):
    with io.open(path, encoding="utf-8") as handle:
        tree = ast.parse(handle.read())
    values = [
        node.value.value
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == name for t in node.targets)
        and isinstance(node.value, ast.Constant)
    ]
    assert len(values) == 1, f"{name} is assigned {len(values)} times in {path}"
    return values[0]


def test_the_timeframe_decided_on_is_the_ruled_one():
    """
    Read from the source, so it runs without pandas_ta. DECISION_TIMEFRAME is
    4h, as ruled, and config.TIMEFRAME is the same: a default the guard
    refused would refuse every run. Allowing another timeframe means changing
    this test, which names the ruling, as well as the constant.
    """
    allowed = _module_string(ENGINE_CORE, "DECISION_TIMEFRAME")
    assert allowed == "4h", (
        f"DECISION_TIMEFRAME is {allowed!r}; the ruling of 20 October 2026 "
        f"(B5) allows 4h only until another timeframe has its own thresholds"
    )
    configured = _module_string(CONFIG, "TIMEFRAME")
    assert configured == allowed, (
        f"config.TIMEFRAME is {configured!r} and the engine decides on "
        f"{allowed!r} only, so every run would be refused"
    )
