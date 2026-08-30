"""
The decision log — sequence item 12, Items 5 (Reproducibility) and 6
(Traceability).

WHY THIS FILE EXISTS

The panel has printed

    Trade logged to Logs/phase7_trade_log_<symbol>.csv

on every run since the engine was written, and no code anywhere wrote that
file. That is Item 6, rated Critical: the engine asserting that an audit action
occurred when it did not. Of the four Criticals it is the only one where the
engine was not merely wrong but actively claiming a safeguard it did not have.

Two ways to close it: stop making the claim, or make it true. Step 5 says make
it true, and that is right here in a way it was not for the `trend_failure`
gate at item 9c. That gate would have needed someone to decide when a trade
should be blocked — a trading judgment nobody could validate yet. This needs
nobody to decide anything. A log either exists on disk or it does not, and Item
5 requires one independently of what the panel says.

WHAT A RECORD CONTAINS, AND WHY

Item 5 is Reproducibility. A record that says only what the engine decided is a
receipt; a record that says what it decided AND what it saw is reproducible.
So each line carries a fingerprint of the inputs:

    last_candle     the timestamp of the newest bar the analysis used
    row_count       how much history it had
    source          the pinned directory, or the live endpoint
    engine_version  from config, where it has been defined and written
                    nowhere since the engine was built
    config          the knobs that change the numbers

Given those five, a run can be repeated. Without them a stored decision cannot
be checked against anything — which is the difference between an audit trail
and a diary.

JSONL, one object per line: appendable without parsing what came before,
readable by anything, and it survives a partial write with only the last line
damaged. A CSV cannot hold a nested decision object without flattening it, and
flattening is where fields go missing quietly.

THE LINE THE PANEL PRINTS IS NOW CONDITIONAL

write() returns the path on success and None on failure, and the panel prints
the line only when it gets a path. An engine that says "logged" when the disk
was full would be the same defect wearing a new filename.
"""

import json
import os
from datetime import datetime, timezone

LOG_FILENAME = "phase7_decision_log_{symbol}.jsonl"

# The knobs that change what the engine computes. Not every constant in
# config — CHART_* and the directory paths do not affect a decision, and a
# snapshot that logs them invites the reader to diff noise.
FINGERPRINTED_CONFIG = [
    "SYMBOL", "TIMEFRAME", "MACRO_TIMEFRAME",
    "STRUCT_LOOKBACK", "VOLUME_PROFILE_BINS",
    "EMA_FAST", "EMA_SLOW",
    "RSI_LENGTH", "ADX_LENGTH", "ATR_LENGTH",
    "VWMA_LENGTH", "SUPERTREND_LENGTH", "SUPERTREND_MULT",
    # DEFAULT_ACCOUNT_BALANCE and DEFAULT_RISK_PERCENT were fingerprinted here
    # until sequence item 13 removed position sizing and, with it, both
    # constants. Nothing in a decision depends on an account balance now, so
    # recording one would suggest the number still meant something.
]


def config_snapshot(config):
    """The subset of config that can change a decision."""
    return {name: getattr(config, name) for name in FINGERPRINTED_CONFIG
            if hasattr(config, name)}


def log_path(log_dir, symbol):
    return os.path.join(log_dir, LOG_FILENAME.format(symbol=str(symbol).lower()))


def write(decision, config, log_dir=None):
    """
    Append one decision to the log. Returns the path written, or None.

    None on failure rather than raising: a decision that was computed correctly
    should still reach the operator if the disk is full. What must not happen
    is the panel claiming it was logged anyway — the caller passes this return
    value to the panel, which prints the line only when there is a path.
    """
    try:
        symbol = str(decision.get("symbol", "unknown"))
        log_dir = log_dir if log_dir is not None else getattr(config, "LOG_DIR", "Logs/")
        os.makedirs(log_dir, exist_ok=True)
        path = log_path(log_dir, symbol)

        record = {
            "logged_at": datetime.now(timezone.utc).isoformat(),
            "engine_version": getattr(config, "engine_version", "unknown"),
            "config": config_snapshot(config),
            "decision": decision,
        }

        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, default=str) + "\n")
        return path

    except Exception:
        # Deliberately swallowed and reported as None. Logging is an audit
        # concern; failing to log must not destroy an analysis that succeeded,
        # and the caller's contract is "path or nothing".
        return None


def read(log_dir, symbol):
    """Every record for one symbol, oldest first. For tests and for reading back."""
    path = log_path(log_dir, symbol)
    if not os.path.exists(path):
        return []
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    # A torn final line from an interrupted write. Skipped
                    # rather than raised: one damaged record must not make the
                    # whole history unreadable.
                    continue
    return out
