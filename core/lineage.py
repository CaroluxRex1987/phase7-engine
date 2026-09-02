"""
Lineage — audit Findings 6 and 7 (Items 5 Reproducibility, 6 Traceability).

WHY THIS FILE EXISTS

Sequence item 12 built the decision log and closed the worst half of Item 6:
the panel had claimed a trade log that nothing wrote. What it left open is the
half the Step 8 re-audit named, and Viktor's 29 August ruling raised to
Critical.

The log records what the engine DECIDED and a five-field fingerprint of what it
SAW. That is a receipt. Item 5 asks for something stronger:

    "Every analysis must be reconstructable later -- its data timestamp, data
     source and version, engine version, configuration, and parameters must all
     be recoverable."

and Item 6 asks for a chain that can be walked:

    decision <- decision components <- normalized signals <- raw signals
             <- indicators <- validated market data <- raw source data

A timestamp and a row count cannot do either. Two different frames can share a
last candle and a length, and no stored field distinguishes them. The auditor's
scenario is the plain one: the exchange revises history, and six months later
nobody can establish that the candles they can fetch today are the candles the
decision was made on.

WHAT "RECONSTRUCTABLE" WAS RULED TO MEAN

Viktor's ruling, 2 September 2026: hash AND archive, pruned at ninety days.

The two halves do different jobs and the difference is the whole design.

    THE HASH detects. It is small, it costs nothing, and it goes in the
    decision log, which is never pruned. A hash outlives the archive on
    purpose: a decision from two years ago can still be checked against data
    fetched today, and the answer -- same or different -- is exactly as
    trustworthy as it was on the day.

    THE ARCHIVE reconstructs. It is the actual candles, and it is the only
    thing that can rebuild a run whose source has since changed. It is also
    the only part with a cost, which is why it is the only part with a limit.

Ninety days is a retention policy, not a claim about how long a decision
matters. Past the window the run does not become unverifiable -- it becomes
verifiable but not rebuildable, and the log says which by whether the archive
file is still there. Nothing silently degrades from one to the other: the
manifest records what was archived, so a missing file reads as pruned rather
than as never written.

WHY THE HASH IS OF THE VALIDATED INPUT, NOT THE FINAL FRAME

The frame the decision is assembled from carries every indicator column, and
those are DERIVED. Hashing them would fingerprint the engine's own arithmetic
along with the market data, so an indicator change would present as a data
change and the hash would stop answering the question it exists to answer:
"was the input the same?" The hash is taken on the OHLCV as validated and
before a single indicator column is added.

WHY A CANONICAL FORM RATHER THAN to_csv

A hash is only useful if the same data hashes the same everywhere. pandas has
changed its default float repr, its NaN spelling and its timestamp formatting
across versions this project has already run on -- numpy moved 1.26 -> 2.2
across the machine rebuild alone (Engineering Notes #34). A hash that depends
on those defaults would report a data change on a library upgrade, which is
the false positive most likely to make a real one get ignored.

So the serialisation here is written out explicitly and depends on no library
default: sorted columns, ISO-8601 UTC index, Python's shortest-round-trip float
repr, a fixed NaN spelling, unit separators, LF line endings, UTF-8.
"""

import gzip
import hashlib
import io
import json
import os
import re
import time
from datetime import datetime, timezone

# Viktor's ruling, 2 September 2026. Archives older than this are removed; the
# hashes that identify them stay in the decision log forever.
RETENTION_DAYS = 90

ARCHIVE_DIRNAME = "archive"

# The only filenames prune() will ever delete. Written as a whole-string match
# so that nothing else that ends up in this directory -- a note, a copy someone
# made, a file from a future format -- can be removed by an age check written
# today. Deleting evidence by accident is a worse failure than keeping too
# much of it.
ARCHIVE_RE = re.compile(r"^[a-z0-9]+_[a-z0-9]+_[0-9a-f]{16}\.json\.gz$")

# Bumped when the canonical form below changes. A stored hash is only
# comparable to a hash computed by the same format version, and a reader that
# cannot tell which format produced a digest cannot tell a data change from a
# format change.
CANONICAL_FORMAT = 1

_SEP = "\x1f"
_NAN = "NaN"


def _scalar(value):
    """One cell, in a form that does not depend on any library's defaults."""
    if value is None:
        return _NAN
    # bool before number: bool is an int subclass and True would serialise
    # as 1.0, which is not what the frame holds.
    if isinstance(value, bool):
        return "true" if value else "false"
    try:
        as_float = float(value)
    except (TypeError, ValueError):
        return str(value)
    if as_float != as_float:          # NaN, without importing numpy
        return _NAN
    if as_float in (float("inf"), float("-inf")):
        return "Infinity" if as_float > 0 else "-Infinity"
    # repr() of a float is the shortest string that round-trips exactly, and
    # has been since Python 3.1. Stable across platforms and pandas versions.
    return repr(as_float)


def _index_label(label):
    iso = getattr(label, "isoformat", None)
    if iso is None:
        return str(label)
    try:
        # tz-aware timestamps are normalised to UTC so that the same instant
        # hashes the same regardless of the reader's timezone; naive ones are
        # left alone rather than being assumed to be UTC, because assuming is
        # how a wrong answer gets a confident hash.
        if getattr(label, "tzinfo", None) is not None:
            label = label.tz_convert("UTC") if hasattr(label, "tz_convert") else label.astimezone(timezone.utc)
    except Exception:
        pass
    return iso() if callable(iso) else str(label)


def canonical_text(df):
    """
    The frame as one deterministic string. This is what gets hashed, and it is
    also what gets archived -- one representation, so a rebuilt frame is
    guaranteed to hash to the value the log recorded rather than merely
    expected to.
    """
    if df is None:
        return ""
    columns = sorted(str(c) for c in df.columns)
    out = io.StringIO()
    out.write(f"phase7-canonical-v{CANONICAL_FORMAT}\n")
    out.write(_SEP.join(["index"] + columns))
    out.write("\n")
    # Column-wise extraction once, then row assembly: .iloc on every cell is
    # O(rows x cols) python-level lookups and this runs on every decision.
    series = {c: list(df[c]) for c in columns}
    labels = list(df.index)
    for row in range(len(labels)):
        cells = [_index_label(labels[row])]
        cells.extend(_scalar(series[c][row]) for c in columns)
        out.write(_SEP.join(cells))
        out.write("\n")
    return out.getvalue()


def rebuild_frame(text):
    """
    The inverse of canonical_text(): the archived form back into a DataFrame.

    This is what separates an archive from a backup. A stored blob nobody can
    turn back into the thing it came from is a claim that the data was kept,
    and this project's characteristic defect is exactly that shape -- a record
    asserting something no code makes true. So the round trip is a property
    the suite checks against every run's real frames:

        frame_hash(rebuild_frame(canonical_text(df))) == frame_hash(df)

    Returns None for text this format does not recognise, rather than a
    partially parsed frame. Half a reconstruction that looks whole is worse
    than none, because the hash comparison it then fails would be blamed on
    the data.
    """
    import pandas as pd

    if not text:
        return None
    lines = text.split("\n")
    if not lines or not lines[0].startswith("phase7-canonical-v"):
        return None
    try:
        version = int(lines[0].rsplit("v", 1)[1])
    except (IndexError, ValueError):
        return None
    if version != CANONICAL_FORMAT:
        return None
    header = lines[1].split(_SEP)
    columns = header[1:]
    labels, rows = [], []
    for line in lines[2:]:
        if not line:
            continue
        cells = line.split(_SEP)
        if len(cells) != len(header):
            return None
        labels.append(cells[0])
        rows.append([_unscalar(c) for c in cells[1:]])
    index = pd.to_datetime(pd.Index(labels), errors="coerce", format="ISO8601")
    if index.isna().any():
        index = pd.Index(labels)
    return pd.DataFrame(rows, columns=columns, index=index)


def _unscalar(cell):
    """One cell, back from its canonical spelling."""
    if cell == _NAN:
        return float("nan")
    if cell == "Infinity":
        return float("inf")
    if cell == "-Infinity":
        return float("-inf")
    if cell == "true":
        return True
    if cell == "false":
        return False
    try:
        return float(cell)
    except ValueError:
        return cell


def frame_hash(df):
    """SHA-256 of the canonical form. None for a frame that does not exist."""
    if df is None:
        return None
    return hashlib.sha256(canonical_text(df).encode("utf-8")).hexdigest()


def run_hash(input_hashes, config_snapshot):
    """
    One identifier for the whole run: the input data AND the settings that
    decide what is computed from it.

    Both halves are needed. Identical candles under different indicator lengths
    are a different analysis, and identical settings over different candles
    obviously are too -- so neither alone identifies a run.
    """
    payload = json.dumps(
        {"inputs": input_hashes, "config": config_snapshot, "format": CANONICAL_FORMAT},
        sort_keys=True, default=str,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _posix(path):
    """A path spelled the same way on every platform. See write_archive()."""
    return str(path).replace("\\", "/")


def archive_dir(log_dir):
    return _posix(os.path.join(log_dir, ARCHIVE_DIRNAME))


def archive_name(symbol, timeframe, run_id):
    safe = lambda s: re.sub(r"[^A-Za-z0-9]", "", str(s)).lower() or "unknown"
    return f"{safe(symbol)}_{safe(timeframe)}_{run_id[:16]}.json.gz"


def write_archive(frames, log_dir, symbol, timeframe, run_id, meta=None):
    """
    Write one run's raw inputs. Returns the path, or None.

    None rather than raising, for the reason decision_log.write() gives: an
    analysis that was computed correctly should still reach the operator when
    the disk is full. What must never happen is the record claiming an archive
    that is not there, which is why the caller stores what this returns rather
    than the path it would have used.

    The filename is the run hash, not a timestamp, so a rerun on identical
    input rewrites one file instead of accumulating copies -- identical input
    is not a second observation.
    """
    try:
        directory = archive_dir(log_dir)
        os.makedirs(directory, exist_ok=True)
        # Forward slashes, on every platform, for both the I/O below and the
        # value returned into the decision log.
        #
        # os.path.join() uses a backslash on Windows, and this path is written
        # into a permanent record that is read on other machines -- so the same
        # run archived on Windows and on Linux produced two different strings
        # for the same file, and the golden snapshot could only ever match the
        # platform it was baselined on. Caught by that snapshot on Viktor's
        # machine after it had been baselined on Linux.
        #
        # decision_log's own log_path() escapes this by luck rather than
        # design: config.LOG_DIR already ends in a separator, so its single
        # join never inserts one. This path joins a directory level deeper,
        # which is where the backslash appeared.
        #
        # Python's file APIs accept forward slashes on Windows, so one
        # normalised string serves both purposes and there is no second
        # spelling of the path to keep in step.
        path = _posix(os.path.join(
            directory, archive_name(symbol, timeframe, run_id)))
        payload = {
            "format": CANONICAL_FORMAT,
            "run_hash": run_id,
            "archived_at": datetime.now(timezone.utc).isoformat(),
            "symbol": str(symbol),
            "timeframe": str(timeframe),
            "meta": meta or {},
            "frames": {
                name: {"sha256": frame_hash(df), "canonical": canonical_text(df)}
                for name, df in (frames or {}).items()
                if df is not None
            },
        }
        # Fixed mtime in the gzip header: the member timestamp would otherwise
        # make two byte-identical archives differ, and this file is content
        # addressed.
        raw = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
        with open(path, "wb") as fh:
            with gzip.GzipFile(fileobj=fh, mode="wb", mtime=0) as gz:
                gz.write(raw)
        return path
    except Exception:
        return None


def read_archive(path):
    """The stored payload, or None if it cannot be read."""
    try:
        with gzip.open(path, "rb") as gz:
            return json.loads(gz.read().decode("utf-8"))
    except Exception:
        return None


def verify_archive(path):
    """
    Re-hash every stored frame and compare against the digest stored beside it.

    Returns {frame_name: bool}. An empty dict means nothing could be read.
    This is what makes the archive evidence rather than a copy: a file that has
    been edited since it was written says so.
    """
    payload = read_archive(path)
    if not payload:
        return {}
    out = {}
    for name, frame in (payload.get("frames") or {}).items():
        text = frame.get("canonical", "")
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        out[name] = (digest == frame.get("sha256"))
    return out


def prune(log_dir, max_age_days=RETENTION_DAYS, now=None, keep=()):
    """
    Remove archives older than the retention window. Returns what was removed.

    Deliberately narrow, because this is the only code in the engine that
    deletes anything. It looks in exactly one directory, does not recurse, and
    removes only files whose whole name matches ARCHIVE_RE -- so a file this
    format does not recognise is left alone rather than aged out on a
    filename it was never meant to match. `keep` is the run just written,
    which must survive its own prune whatever the clock says.
    """
    removed = []
    directory = archive_dir(log_dir)
    if not os.path.isdir(directory) or not max_age_days:
        return removed
    now = time.time() if now is None else now
    cutoff = now - (float(max_age_days) * 86400.0)
    protected = {os.path.abspath(p) for p in (keep or ()) if p}
    try:
        names = os.listdir(directory)
    except OSError:
        return removed
    for name in names:
        if not ARCHIVE_RE.match(name):
            continue
        path = os.path.join(directory, name)
        if os.path.abspath(path) in protected:
            continue
        try:
            if not os.path.isfile(path):
                continue
            if os.path.getmtime(path) >= cutoff:
                continue
            os.remove(path)
            removed.append(name)
        except OSError:
            # A file that cannot be removed is left and reported by absence
            # from the return value. Retention is best-effort; the analysis is
            # not.
            continue
    return removed
