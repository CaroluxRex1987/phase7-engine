"""
Section 11 confirmation run — Kimi K3 round-4 report, Finding 1.

WHAT THIS IS FOR
----------------
The round-4 report (../report.md) asks for exactly one run. Finding 1 says:

    core/engine_core.py writes  {"available": True, ..., "correlation": None}
    when the AERO/BTC correlation could not be measured, and
    models/signal_router.py::_merge_btc_context then does
    float(btc_context.get("correlation", 0.0)) -> float(None) -> TypeError,
    which _build_decision_object's broad except turns into an error dict.
    So a complete, healthy AERO analysis is thrown away because the OPTIONAL
    BTC context could not be measured.

Confirmed at source by reading all four sites. This script confirms it on the
live path, BEFORE any fix, so the defect is observed rather than argued.

WHAT IT DOES
------------
Three runs, all offline, all on the committed pinned fixtures:

  A  CONTROL   fixtures exactly as committed. The two indexes share all 450
               timestamps, so the correlation is measured and the run should
               complete. If A also fails the harness is broken and B proves
               nothing.

  B  THE CASE  AERO series as committed; BTCUSDT_4h with every timestamp
               shifted +2 hours, so the two indexes share zero timestamps.
               compute_correlation_beta's inner join is then empty and it
               returns (NaN, NaN, 0), which engine_core stores as
               "correlation": None alongside "available": True.

  C  SECONDARY the optional variant Kimi mentions: timestamps unchanged, BTC's
               last 60 candles flat, so the returns in the 30-candle window
               have zero variance and the correlation is NaN with
               n_observations > 0. SECONDARY because a flat price series also
               moves BTC-side ATR and volatility, so a failure here can have
               more than one cause.

TWO ISOLATIONS, both deliberate
-------------------------------
1. NETWORK. requests.get / .post / Session.request are replaced with functions
   that raise. If a run reaches the API the traceback says so instead of the
   run quietly succeeding against live data.

2. THE RECORD. config.LOG_DIR is repointed at a temporary directory for the
   duration. The first version of this harness did not do that, and its three
   runs appended three records to the real logs/phase7_decision_log_aerousdt.jsonl
   and overwrote logs/phase7_state_AEROUSDT_4h.json — a diagnostic writing into
   the engine's permanent record. Structural fix rather than a warning: a
   harness that cannot reach the real log cannot contaminate it. The decision
   log the runs DO produce is copied into this directory afterwards, as
   evidence.

Run from anywhere:

    python docs/audit_reports/round4_kimi-k3_2026-09-05/section11_confirmation/section11_confirm.py

Writes only into this directory. The shifted fixtures and the redirected log
live in a temporary directory that is deleted on exit.
"""

import contextlib
import io
import math
import os
import shutil
import sys
import tempfile
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
# section11_confirmation -> round4_... -> audit_reports -> docs -> repo root
ROOT = os.path.abspath(os.path.join(HERE, os.pardir, os.pardir, os.pardir, os.pardir))
sys.path.insert(0, ROOT)

import pandas as pd  # noqa: E402
import requests  # noqa: E402

from core import config  # noqa: E402

FIXTURES = os.path.join(ROOT, "tests", "fixtures", "pinned")
SHIFT_MS = 2 * 60 * 60 * 1000  # +2 hours, in milliseconds

# --- isolation 2: the record ------------------------------------------
# Set before anything is imported that might read it, and before any run.
# engine_core and decision_log both read config.LOG_DIR at call time.
TMP_ROOT = tempfile.mkdtemp(prefix="phase7_section11_")
ISOLATED_LOGS = os.path.join(TMP_ROOT, "logs") + os.sep
os.makedirs(ISOLATED_LOGS, exist_ok=True)
REAL_LOG_DIR = config.LOG_DIR
config.LOG_DIR = ISOLATED_LOGS

import logging  # noqa: E402

logging.basicConfig(
    level=logging.WARNING,
    format="%(levelname)s - %(name)s - %(message)s",
    handlers=[logging.FileHandler(os.path.join(ISOLATED_LOGS, "harness.log"))],
)

from data.data_fetcher import DataFetcher  # noqa: E402
from models.signal_router import SignalRouter  # noqa: E402


# --- isolation 1: the network -----------------------------------------
class NetworkReached(RuntimeError):
    pass


def _no_network(*_args, **_kwargs):
    raise NetworkReached(
        "the run attempted a live HTTP request; this harness is offline by "
        "construction, so a pinned file was missing or the pinned source was "
        "not active"
    )


requests.get = _no_network
requests.post = _no_network
requests.Session.request = _no_network


# ----------------------------------------------------------------------
# Fixture variants
# ----------------------------------------------------------------------
def _build_variant(name, btc_transform):
    """
    One pinned directory. Both AERO series are copied byte for byte; only
    BTCUSDT_4h.csv is rewritten, and only by btc_transform.
    """
    d = os.path.join(TMP_ROOT, name)
    os.makedirs(d, exist_ok=True)
    for f in ("AEROUSDT_4h.csv", "AEROUSDT_1d.csv"):
        shutil.copy2(os.path.join(FIXTURES, f), os.path.join(d, f))

    btc = pd.read_csv(os.path.join(FIXTURES, "BTCUSDT_4h.csv"))
    btc_transform(btc).to_csv(os.path.join(d, "BTCUSDT_4h.csv"), index=False)
    return d


def _unchanged(df):
    return df


def _shift_two_hours(df):
    df = df.copy()
    df["timestamp"] = df["timestamp"].astype("int64") + SHIFT_MS
    return df


def _flatten_tail(df, n=60):
    """Last n candles perfectly flat: open = high = low = close."""
    df = df.copy()
    level = float(df["close"].iloc[-n])
    for col in ("open", "high", "low", "close"):
        df.loc[df.index[-n:], col] = level
    return df


# ----------------------------------------------------------------------
# One run
# ----------------------------------------------------------------------
def run_case(label, pinned_dir, note):
    DataFetcher.set_pinned_source(pinned_dir)

    buf = io.StringIO()
    decision = None
    crashed = None
    try:
        with contextlib.redirect_stdout(buf):
            router = SignalRouter()
            decision = router.route(symbol=config.SYMBOL, timeframe=config.TIMEFRAME)
    except Exception:
        crashed = traceback.format_exc()

    panel = buf.getvalue()

    out_path = os.path.join(HERE, f"run_{label}.txt")
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(f"=== RUN {label} — {note}\n")
        fh.write(f"=== pinned source: {pinned_dir}\n")
        fh.write(f"=== config.LOG_DIR redirected to: {config.LOG_DIR}\n\n")
        fh.write(panel)
        if crashed:
            fh.write("\n=== uncaught traceback ===\n")
            fh.write(crashed)
        fh.write("\n=== returned object ===\n")
        fh.write(repr(decision))
        fh.write("\n")

    print(f"\n--- RUN {label}: {note}")
    if crashed:
        print(f"    UNCAUGHT EXCEPTION: {crashed.strip().splitlines()[-1]}")
        print(f"    full traceback in {out_path}")
        return

    if isinstance(decision, dict) and "error" in decision:
        print(f"    ERROR OBJECT: {decision['error']}")
        print(f"    returned keys: {sorted(decision.keys())}")
    else:
        btc = (decision or {}).get("btc_context", {})
        corr = btc.get("correlation")
        corr_txt = "None" if corr is None else (
            f"{corr:+.4f}" if isinstance(corr, float) and math.isfinite(corr) else repr(corr)
        )
        print("    COMPLETED — no error object")
        print(f"    btc_context.available      = {btc.get('available')}")
        print(f"    btc_context.correlation    = {corr_txt}")
        print(f"    btc_context.n_observations = {btc.get('n_observations')}")

    for line in panel.splitlines():
        if "CORRELATION" in line.upper():
            print(f"    panel: {line.strip()}")
    print(f"    full panel in {out_path}")


def _preserve_isolated_log():
    """
    Copy whatever the three runs wrote into the redirected log directory into
    this directory, as evidence. The traceability question — what a record
    contains when the run failed — is answerable only from these bytes.
    """
    kept = []
    for name in sorted(os.listdir(ISOLATED_LOGS)):
        src = os.path.join(ISOLATED_LOGS, name)
        if not os.path.isfile(src) or name == "harness.log":
            continue
        shutil.copy2(src, os.path.join(HERE, f"isolated_{name}"))
        kept.append(f"isolated_{name}")
    return kept


def main():
    print("Section 11 confirmation run — Kimi round-4 Finding 1")
    print("Code is UNCHANGED; this observes only.")
    print(f"Network: patched to raise.  Real log dir {REAL_LOG_DIR!r} NOT written.")
    print(f"Runs write their record to: {ISOLATED_LOGS}")

    try:
        run_case("A_control", _build_variant("A_control", _unchanged),
                 "fixtures as committed (negative control)")
        run_case("B_shift", _build_variant("B_shift", _shift_two_hours),
                 "BTC timestamps +2h — zero shared timestamps")
        run_case("C_flat", _build_variant("C_flat", _flatten_tail),
                 "BTC last 60 candles flat (SECONDARY, confounded)")

        kept = _preserve_isolated_log()
        print(f"\nRecord produced by these runs, preserved as: {', '.join(kept) or '(none)'}")
    finally:
        DataFetcher.set_pinned_source(None)
        config.LOG_DIR = REAL_LOG_DIR
        shutil.rmtree(TMP_ROOT, ignore_errors=True)

    print("\nHow to read this:")
    print("  A completes and B returns")
    print('  "Decision object construction failed: float() argument ..."')
    print("     -> Finding 1 CONFIRMED end to end.")
    print("  A completes and B completes with CORRELATION: NOT MEASURED")
    print("     -> Finding 1 is WRONG about the live path.")
    print("  A itself fails -> the harness is broken; B proves nothing.")


if __name__ == "__main__":
    main()
