# Decision-log backups

This directory holds dated, committed snapshots of the live decision log
(`logs/phase7_decision_log_*.jsonl`), which `.gitignore` excludes from the repo
entirely -- so without this directory the log has no second copy anywhere.

Ruled by Viktor, 11 September 2026 (Rulings, "The live decision log"):
option B, committed dated snapshots, in preference to an ad-hoc manual step.
Placed at the repo root rather than under `Claude outputs/` because that
directory is itself an open question (Rulings, item 5 -- a `.gitignore` entry
for it is on the table) and a backup location has to survive that ruling
either way.

## What is here

`phase7_decision_log_aerousdt_20260906.jsonl` -- the first snapshot, taken
ad hoc on 6 September before this directory existed (it lived under
`Claude outputs/` until this commit). It is the only surviving second copy of
that day's record: ten records the test suite wrote before `fc35a2f` stopped
the suite from writing into the live log at all, and record 11, the 10:51
AEROUSDT live run. Untouched here -- moved, not edited.

## Taking a new snapshot

    python utils/decision_log_backup.py

Copies every `logs/phase7_decision_log_*.jsonl` into this directory as
`<name>_<YYYYMMDD>.jsonl` (UTC date). Refuses to overwrite an existing dated
snapshot unless its content is byte-identical to what is already there (a
same-day re-run is then a no-op) or `--force` is passed -- a snapshot is a
historical record, not a rolling copy, so overwriting one silently would
destroy exactly what this directory exists to keep. `--dry-run` previews
without writing.

This is a command Viktor runs, not a scheduled job: nothing in this project's
toolchain can put something on his machine's task scheduler, so "automation"
here means one command instead of a manual copy-and-rename, not an unattended
cron. Session-end is the natural point to run it, alongside the handover
check.

## Not done by this script

The suite-written records already inside the live log (see Rulings, 11
September: "keep the records ... tag them") are not touched here. Tagging
those ten records as suite output, in place, in a file this bridge can read
but that git does not track, is a separate, un-built piece of the same
ruling and needs its own approach -- flagged, not done, in
docs/PHASE7_NEXT.md.
