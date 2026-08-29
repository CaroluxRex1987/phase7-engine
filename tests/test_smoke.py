"""
The smoke run: the whole engine, end to end, on pinned data.

Sequence item 4 asks for "a smoke run on pinned data". It became possible only
when item 3 landed, and it is the test that proves the pinned source works
*through the engine* rather than only through DataFetcher — which is a
different claim. test_pinned_source.py shows the fetcher serves files
correctly; this shows the engine actually runs on them, start to finish,
without touching the network.

It does not compare a snapshot. Asserting exact output belongs to
test_golden_path.py, and re-baselining that against the pinned source is
sequence item 7's job, deliberately after the cleanup in items 5 and 6 so that
every later delta traces to exactly one controlled change. This test asks only:
does it complete, and is the result shaped like a decision?

That is a lower bar and a useful one. Five of the nine crashes in the runtime
log were failures to complete at all.

Constitution: Tier 3, item 3 (automated tests). Sequence item 4.
"""

import os

from conftest import REPO_ROOT

PINNED_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "fixtures", "pinned")

# The pinned dataset was built to match the engine's own defaults, so a smoke
# run needs no special configuration: config.SYMBOL is AEROUSDT, TIMEFRAME is
# 4h, MACRO_TIMEFRAME is 1d, and BTC context is always BTCUSDT.
SYMBOL = "AEROUSDT"
TIMEFRAME = "4h"

# Top-level keys signal_router builds into every successful decision object.
EXPECTED_KEYS = [
    "symbol", "timeframe", "bias", "trend", "structure",
    "entry", "risk", "exit", "btc_context", "explanation",
]


def _engine_available():
    try:
        import pandas_ta  # noqa: F401
        return True
    except Exception:
        return False


def test_engine_runs_end_to_end_on_pinned_data():
    """
    The whole pipeline on disk-backed input, with the network unreachable.

    base_url is pointed at a dead port on purpose. If any part of the engine
    reaches the API, the connection is refused and this fails — so a silent
    fall-through to live data cannot masquerade as a passing smoke test.
    """
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return

    from data.data_fetcher import DataFetcher, data_fetcher
    from models.signal_router import SignalRouter

    original_url = data_fetcher.base_url
    try:
        data_fetcher.base_url = "http://127.0.0.1:1"
        DataFetcher.set_pinned_source(PINNED_DIR)

        decision = SignalRouter().route(symbol=SYMBOL, timeframe=TIMEFRAME)

        assert isinstance(decision, dict), (
            f"route() returned {type(decision).__name__}, not a dict"
        )
        assert "error" not in decision, (
            f"the engine reported an error on clean pinned data: "
            f"{decision.get('error')}"
        )

        missing = [k for k in EXPECTED_KEYS if k not in decision]
        assert not missing, (
            f"decision object is missing expected keys: {', '.join(missing)}"
        )

        assert decision.get("symbol") == SYMBOL, (
            f"decision reports symbol {decision.get('symbol')!r}, "
            f"expected {SYMBOL!r}"
        )
    finally:
        DataFetcher.clear_pinned_source()
        data_fetcher.base_url = original_url


def test_the_smoke_run_is_reproducible():
    """
    Two full engine runs on pinned data must agree.

    This is the property the whole apparatus phase exists to establish, tested
    at the top level rather than at the fetcher. It is weaker than the golden
    snapshot — it compares two live runs to each other rather than to a stored
    baseline — but it needs no baseline, so it keeps working across the
    re-baselining at sequence item 7.
    """
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return

    from data.data_fetcher import DataFetcher, data_fetcher
    from models.signal_router import SignalRouter

    volatile = {"chart_path", "timestamp", "generated_at"}

    def stable(obj):
        if isinstance(obj, dict):
            return {k: stable(v) for k, v in obj.items() if k not in volatile}
        if isinstance(obj, (list, tuple)):
            return [stable(v) for v in obj]
        if isinstance(obj, float):
            return round(obj, 8)
        return obj

    original_url = data_fetcher.base_url
    try:
        data_fetcher.base_url = "http://127.0.0.1:1"
        DataFetcher.set_pinned_source(PINNED_DIR)

        first = stable(SignalRouter().route(symbol=SYMBOL, timeframe=TIMEFRAME))
        second = stable(SignalRouter().route(symbol=SYMBOL, timeframe=TIMEFRAME))

        if first != second:
            differing = sorted(
                k for k in set(first) | set(second)
                if first.get(k) != second.get(k)
            )
            raise AssertionError(
                "two full engine runs on identical pinned data disagreed.\n"
                f"fields that differ: {', '.join(differing)}"
            )
    finally:
        DataFetcher.clear_pinned_source()
        data_fetcher.base_url = original_url


def test_a_missing_pinned_series_surfaces_as_an_engine_error():
    """
    The failure path, end to end.

    A pinned source with no file for the requested symbol must produce a
    reported error rather than a confident-looking panel built on nothing.
    This is Item 13's territory reached from the data side — and it is what
    proves the "never fall back to live" rule holds through the engine, not
    just inside DataFetcher.
    """
    if not _engine_available():
        print("SKIP: pandas_ta not installed")
        return

    from data.data_fetcher import DataFetcher, data_fetcher
    from models.signal_router import SignalRouter

    original_url = data_fetcher.base_url
    try:
        data_fetcher.base_url = "http://127.0.0.1:1"
        DataFetcher.set_pinned_source(PINNED_DIR)

        decision = SignalRouter().route(symbol="NOTAREALPAIR", timeframe="4h")

        assert isinstance(decision, dict), "route() did not return a dict"
        assert "error" in decision, (
            "the engine produced a decision for a symbol with no data. It "
            "should report an error — a panel built on no input is exactly "
            "the failure Item 13 is about."
        )
    finally:
        DataFetcher.clear_pinned_source()
        data_fetcher.base_url = original_url
