"""
Sequence item 3 — the pinned data path.

Before this existed, get_tf() always went to the live API, so the engine could
not be run twice on the same input. That made most of the audit's Verification
fields unsatisfiable: Items 3, 11 and 13 all prescribe "change something, rerun,
compare", and T2-4's own check is "change a knob, rerun, observe the delta".
None of that is possible when every run sees different data.

These tests cover the mechanism itself. They do not need pandas_ta, a network,
or any knowledge of trading — which is the point.

Constitution: closes T3-5 (fixed evaluation datasets), and unblocks the
Verification clauses of Items 3, 11, 13 and T2-4.

NOTE ON THE GOLDEN-PATH TEST: test_golden_path.py still monkeypatches
DataFetcher.get_tf rather than using this mechanism. That is deliberate and
temporary. Switching it over changes the BTC series it sees — the monkeypatch
fabricates BTC by reversing and scaling the base series — which would move the
stored snapshot. Re-baselining belongs to sequence item 7, which exists to
capture the golden baseline *after* the cleanup in items 5 and 6, so that every
later delta is attributable to exactly one controlled change. Doing it here
would spend that attributability early.
"""

import os
import sys

from conftest import fixture, REPO_ROOT

PINNED_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "fixtures", "pinned")


def _fetcher():
    from data.data_fetcher import DataFetcher
    return DataFetcher


def _unreachable(instance):
    """
    Point an instance at a dead port.

    If any of these tests reach the network the connection is refused
    immediately, so a test that silently fell back to the live API fails loudly
    instead of passing slowly.
    """
    instance.base_url = "http://127.0.0.1:1"
    return instance


def test_pinned_directory_exists_and_is_complete():
    """
    All three series the engine fetches must be present.

    engine_core makes three calls: the base series (line 499), the macro
    timeframe (524), and BTC context (682). Pinning only the base leaves two
    thirds of a run still dependent on the network, and the resulting
    "reproducible" run is not.
    """
    assert os.path.isdir(PINNED_DIR), f"no pinned dataset at {PINNED_DIR}"

    expected = {"AEROUSDT_4h.csv", "AEROUSDT_1d.csv", "BTCUSDT_4h.csv"}
    present = {f for f in os.listdir(PINNED_DIR) if f.endswith(".csv")}
    missing = expected - present
    assert not missing, f"pinned dataset incomplete, missing: {sorted(missing)}"

    assert os.path.exists(os.path.join(PINNED_DIR, "MANIFEST.json")), (
        "the pinned dataset has no MANIFEST.json — sequence item 3 requires "
        "hashes and origin to be recorded, not assumed"
    )


def test_manifest_hashes_match_the_files():
    """
    The manifest records a sha256 per series. If a file is edited without
    regenerating, this catches it — which is the whole reason to record hashes
    rather than trust that the data has not moved.
    """
    import hashlib
    import json

    with open(os.path.join(PINNED_DIR, "MANIFEST.json")) as f:
        manifest = json.load(f)

    mismatches = []
    for series in manifest["series"]:
        path = os.path.join(PINNED_DIR, series["file"])
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        if h.hexdigest() != series["sha256"]:
            mismatches.append(series["file"])

    assert not mismatches, (
        "pinned data does not match its manifest: " + ", ".join(mismatches) +
        "\nEither the files were edited without regenerating, or the manifest "
        "is stale. Regenerate with: python docs/build/make_pinned.py"
    )


def test_pinned_source_serves_all_three_series_without_network():
    DataFetcher = _fetcher()
    fetcher = _unreachable(DataFetcher())
    try:
        DataFetcher.set_pinned_source(PINNED_DIR)
        for symbol, timeframe in [("AEROUSDT", "4h"), ("AEROUSDT", "1d"),
                                  ("BTCUSDT", "4h")]:
            df = fetcher.get_tf(symbol, timeframe, limit=300)
            err = df.attrs.get("fetch_error")
            assert err is None, f"{symbol} {timeframe} failed: {err}"
            assert len(df) > 0, f"{symbol} {timeframe} returned no rows"
            assert list(df.columns) == ["open", "high", "low", "close", "volume"], (
                f"{symbol} {timeframe} has unexpected columns: {list(df.columns)}"
            )
    finally:
        DataFetcher.clear_pinned_source()


def test_two_fetches_return_equal_data():
    """The property that makes every later fix verifiable."""
    DataFetcher = _fetcher()
    fetcher = _unreachable(DataFetcher())
    try:
        DataFetcher.set_pinned_source(PINNED_DIR)
        first = fetcher.get_tf("AEROUSDT", "4h", limit=300)
        second = fetcher.get_tf("AEROUSDT", "4h", limit=300)
        assert first.equals(second), (
            "two fetches of pinned data returned different frames"
        )
    finally:
        DataFetcher.clear_pinned_source()


def test_each_fetch_returns_an_independent_copy():
    """
    When this was written, T2-1 was open: four modules rewrote their caller's
    columns in place. If the pinned source had handed the same object to every
    caller, those writes would have corrupted the dataset mid-run and the second
    and third series would have seen mutated data.

    Sequence item 6 closed T2-1, so this is no longer load-bearing against that
    specific hazard — and it stays anyway, for two reasons. It is the guarantee
    this class makes on its own terms: a caller who receives a frame owns it.
    And it is what stops a future "optimisation" from caching the loaded frame,
    which would make the ownership claim false again without touching any of the
    modules item 6 fixed.
    """
    DataFetcher = _fetcher()
    fetcher = _unreachable(DataFetcher())
    try:
        DataFetcher.set_pinned_source(PINNED_DIR)
        first = fetcher.get_tf("AEROUSDT", "4h", limit=300)
        original_close = float(first["close"].iloc[-1])

        first["close"] = 0.0                      # simulate in-place mutation

        second = fetcher.get_tf("AEROUSDT", "4h", limit=300)
        assert float(second["close"].iloc[-1]) == original_close, (
            "mutating a returned frame corrupted the next fetch — the pinned "
            "source is handing out shared state"
        )
    finally:
        DataFetcher.clear_pinned_source()


def test_missing_series_errors_rather_than_falling_back_to_live():
    """
    The most important test in this file.

    A silent fall-through to the live API would reintroduce exactly the
    nondeterminism the pinned source exists to remove — and would do it
    invisibly, which is worse than not having the mechanism at all.
    """
    DataFetcher = _fetcher()
    fetcher = _unreachable(DataFetcher())
    try:
        DataFetcher.set_pinned_source(PINNED_DIR)
        df = fetcher.get_tf("NOTAREALPAIR", "4h", limit=300)

        assert len(df) == 0, "expected no rows for a series with no pinned file"
        err = df.attrs.get("fetch_error")
        assert err, (
            "a missing pinned series returned no error — it may have fallen "
            "through to the live API"
        )
        assert "pinned source active" in err, (
            f"error does not identify this as a pinned-source failure: {err}"
        )
    finally:
        DataFetcher.clear_pinned_source()


def test_limit_takes_the_most_recent_candles():
    """
    The API returns the most recent `limit` candles. The pinned source must
    match, or indicator warm-up periods land on different data than they would
    live.
    """
    DataFetcher = _fetcher()
    fetcher = _unreachable(DataFetcher())
    try:
        DataFetcher.set_pinned_source(PINNED_DIR)
        full = fetcher.get_tf("AEROUSDT", "4h", limit=100000)
        limited = fetcher.get_tf("AEROUSDT", "4h", limit=50)

        assert len(limited) == 50, f"expected 50 rows, got {len(limited)}"
        assert limited.index[-1] == full.index[-1], (
            "limit took the oldest candles instead of the newest"
        )
    finally:
        DataFetcher.clear_pinned_source()


def test_environment_variable_activates_the_pinned_source():
    """
    So a run can be made reproducible from the command line without editing
    code:  PHASE7_PINNED_DATA=tests/fixtures/pinned python main.py
    """
    DataFetcher = _fetcher()
    from data.data_fetcher import PINNED_ENV_VAR

    previous = os.environ.get(PINNED_ENV_VAR)
    try:
        DataFetcher.clear_pinned_source()
        assert DataFetcher.pinned_source() is None, (
            "a pinned source was active before this test set one — earlier "
            "tests are leaking state"
        )

        os.environ[PINNED_ENV_VAR] = PINNED_DIR
        assert DataFetcher.pinned_source() is not None, (
            f"{PINNED_ENV_VAR} did not activate the pinned source"
        )
    finally:
        if previous is None:
            os.environ.pop(PINNED_ENV_VAR, None)
        else:
            os.environ[PINNED_ENV_VAR] = previous
        DataFetcher.clear_pinned_source()


def test_live_api_is_the_default():
    """
    The mechanism must be opt-in. Nothing about normal operation changes until
    someone asks for pinned data.
    """
    DataFetcher = _fetcher()
    from data.data_fetcher import PINNED_ENV_VAR

    previous = os.environ.get(PINNED_ENV_VAR)
    try:
        DataFetcher.clear_pinned_source()
        os.environ.pop(PINNED_ENV_VAR, None)
        assert DataFetcher.pinned_source() is None, (
            "fetches are pinned by default — they should go live unless asked"
        )
    finally:
        if previous is not None:
            os.environ[PINNED_ENV_VAR] = previous
