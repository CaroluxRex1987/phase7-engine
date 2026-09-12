"""
Takes a dated, committed snapshot of the live decision log.

WHY THIS EXISTS

`logs/` is gitignored (see core/config.py's LOG_DIR and .gitignore), so
`logs/phase7_decision_log_<symbol>.jsonl` -- the record Constitution Item 5
and Item 6 lean on -- has no second copy anywhere by default. That was
discovered the hard way on 6 September, when the test suite was found to be
writing into and once deleting that exact file (fixed at `fc35a2f`); the only
reason that day's record survives at all is an ad-hoc manual copy someone
happened to make first.

Ruled by Viktor, 11 September 2026 ("Rulings, 11 September 2026", item 2):
keep what the suite wrote rather than pruning it, and take committed dated
snapshots (option B) rather than relying on an ad-hoc step each time. This
script is that step, made repeatable. It is not a scheduled job -- nothing
reachable from this project's tooling can register one on Viktor's machine --
so "automation" here means one command in place of a manual copy-and-rename,
run at his discretion (session end is the natural point, alongside the
handover check).

WHERE SNAPSHOTS GO, AND WHY NOT Claude outputs/

decision_log_backups/, a new tracked directory at the repo root. `Claude
outputs/` was the ad-hoc precedent (the 6 September backup lived there) but
is itself an open question -- Rulings item 5 has a `.gitignore` entry for it
on the table -- so a backup location that depended on that directory staying
trackable would be one ruling away from silently losing its own reason to
exist. A dedicated directory has no such dependency.

WHAT IT DOES NOT DO

It does not touch the live log. It does not tag the suite-written records
inside it as suite output -- that is a separate, un-built piece of the same
11 September ruling, on a file this script can copy but that git does not
track, and it needs its own approach. See decision_log_backups/README.md and
docs/PHASE7_NEXT.md.
"""

import argparse
import filecmp
import glob
import os
import shutil
import sys
from datetime import datetime, timezone

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import config

BACKUP_DIR = "decision_log_backups"

# Matches core/decision_log.py's LOG_FILENAME = "phase7_decision_log_{symbol}.jsonl"
# for any symbol, rather than importing that format string and supplying a
# wildcard symbol -- this way a rename of LOG_FILENAME's shape is something a
# reader of this file notices instead of something the glob silently stops
# matching.
LIVE_LOG_GLOB = "phase7_decision_log_*.jsonl"


def _dated_backup_name(source_name, today):
    stem, ext = os.path.splitext(source_name)
    return f"{stem}_{today}{ext}"


def take_snapshot(log_dir=None, backup_dir=None, today=None, force=False, dry_run=False):
    """
    Copy every live decision log into dated snapshots.

    Returns a list of (source_path, dest_path, action) tuples, action one of
    "copied", "skipped (already backed up, identical)", "skipped (dry run)",
    or "REFUSED (dest exists and differs; rerun with --force)".

    Never raises on a missing live log directory or an empty one -- an engine
    that has not been run yet, or has been run somewhere logs/ was cleared,
    has nothing to back up, and that is reported as zero files rather than as
    a failure.
    """
    log_dir = log_dir if log_dir is not None else config.LOG_DIR
    backup_dir = backup_dir if backup_dir is not None else BACKUP_DIR
    today = today if today is not None else datetime.now(timezone.utc).strftime("%Y%m%d")

    results = []
    sources = sorted(glob.glob(os.path.join(log_dir, LIVE_LOG_GLOB)))

    if not sources:
        return results

    if not dry_run:
        os.makedirs(backup_dir, exist_ok=True)

    for source_path in sources:
        dest_name = _dated_backup_name(os.path.basename(source_path), today)
        dest_path = os.path.join(backup_dir, dest_name)

        if os.path.exists(dest_path):
            if filecmp.cmp(source_path, dest_path, shallow=False):
                results.append((source_path, dest_path, "skipped (already backed up, identical)"))
                continue
            if not force:
                results.append((source_path, dest_path, "REFUSED (dest exists and differs; rerun with --force)"))
                continue
            # force=True and the two differ: fall through to overwrite below.

        if dry_run:
            results.append((source_path, dest_path, "skipped (dry run)"))
            continue

        # copy2 preserves mtime -- a snapshot's own file time is itself part
        # of the record of when the underlying log last changed.
        shutil.copy2(source_path, dest_path)
        results.append((source_path, dest_path, "copied"))

    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--force", action="store_true",
                         help="Overwrite an existing dated snapshot that differs from the live log.")
    parser.add_argument("--dry-run", action="store_true",
                         help="Show what would happen without writing anything.")
    args = parser.parse_args()

    results = take_snapshot(force=args.force, dry_run=args.dry_run)

    if not results:
        print(f"No live decision logs found under {config.LOG_DIR!r} -- nothing to back up.")
        return 0

    refused = False
    for source_path, dest_path, action in results:
        print(f"{action}: {source_path} -> {dest_path}")
        if action.startswith("REFUSED"):
            refused = True

    return 1 if refused else 0


if __name__ == "__main__":
    sys.exit(main())
