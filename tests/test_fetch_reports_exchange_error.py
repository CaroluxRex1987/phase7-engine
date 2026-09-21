"""
Finding 27 (docs/PHASE7_NEXT.md, "Review findings", deferred read of
21 September 2026) -- data/data_fetcher.py's fetch_ohlc discarded the
exchange's own error text, and imported `time` without using it.

Fixture-free on purpose: run_tests.py calls every test_* with no arguments,
so requests.get is replaced by hand and restored in a finally block. Nothing
touches the network or logs/.
"""

import ast
import io
import os

import requests

import data.data_fetcher as fetcher_module

FETCHER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "data", "data_fetcher.py")

MEXC_ERROR = {"code": -1121, "msg": "Invalid symbol."}


class _Reply:
    """A stand-in for requests.Response: a status, a JSON body or a text body."""

    def __init__(self, status=200, payload=None, text=None):
        self.status_code = status
        self._payload = payload
        self.text = text if text is not None else ""

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.exceptions.HTTPError(
                f"{self.status_code} Client Error: Bad Request for url: "
                f"https://api.mexc.com/api/v3/klines", response=self)

    def json(self):
        if self._payload is None:
            raise ValueError("no JSON body")
        return self._payload


def _fetch_with(reply):
    original = fetcher_module.requests.get
    fetcher_module.requests.get = lambda *a, **k: reply
    try:
        return fetcher_module.DataFetcher().fetch_ohlc("NOPEUSDT", "4h", limit=5)
    finally:
        fetcher_module.requests.get = original


def test_a_code_and_msg_in_a_200_reply_reach_the_error():
    out = _fetch_with(_Reply(200, payload=MEXC_ERROR))
    assert isinstance(out, dict) and "error" in out, out
    assert "-1121" in out["error"] and "Invalid symbol." in out["error"], out["error"]


def test_a_code_and_msg_in_a_4xx_reply_reach_the_error():
    """MEXC documents 4XX for a malformed request: the usual case."""
    out = _fetch_with(_Reply(400, payload=MEXC_ERROR))
    assert isinstance(out, dict) and "error" in out, out
    assert out["error"].startswith("API request failed: 400"), out["error"]
    assert "-1121" in out["error"] and "Invalid symbol." in out["error"], out["error"]


def test_a_plain_text_4xx_body_reaches_the_error():
    out = _fetch_with(_Reply(403, text="Access denied by WAF rule 17"))
    assert "Access denied by WAF rule 17" in out["error"], out["error"]


def test_a_4xx_with_no_body_still_reports_the_status():
    out = _fetch_with(_Reply(429, text=""))
    assert out["error"].startswith("API request failed: 429"), out["error"]
    assert "The exchange said" not in out["error"], out["error"]


def test_a_long_reply_is_truncated():
    out = _fetch_with(_Reply(200, payload={"page": "x" * 5000}))
    err = out["error"]
    assert "characters)" in err, err[:400]
    assert len(err) < fetcher_module.EXCHANGE_TEXT_LIMIT + 200, len(err)


def test_an_empty_list_is_reported_as_no_candles():
    out = _fetch_with(_Reply(200, payload=[]))
    assert "empty list" in out["error"], out["error"]


def test_a_list_of_candles_is_not_an_error():
    """The control: a well-formed reply still becomes a frame."""
    base, step = 1700000000000, 4 * 60 * 60 * 1000
    rows = [[base + i * step, "1.00", "1.10", "0.90", "1.05", "100",
             base + (i + 1) * step - 1, "105"] for i in range(30)]
    original_validate = fetcher_module.validate_ohlcv
    fetcher_module.validate_ohlcv = lambda *a, **k: None   # fixed past candles
    try:
        out = _fetch_with(_Reply(200, payload=rows))
    finally:
        fetcher_module.validate_ohlcv = original_validate
    assert not isinstance(out, dict), out
    assert len(out) == 30


def test_every_import_in_the_fetcher_is_used():
    """`import time` sat unused; this fails on the next unused import too."""
    with io.open(FETCHER, encoding="utf-8") as f:
        tree = ast.parse(f.read())
    imported = {}
    for node in tree.body:
        if isinstance(node, ast.Import):
            for a in node.names:
                imported[(a.asname or a.name).split(".")[0]] = node.lineno
        elif isinstance(node, ast.ImportFrom):
            for a in node.names:
                imported[a.asname or a.name] = node.lineno
    used = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    unused = sorted(name for name in imported if name not in used)
    assert not unused, f"imported and never used in data_fetcher.py: {unused}"
