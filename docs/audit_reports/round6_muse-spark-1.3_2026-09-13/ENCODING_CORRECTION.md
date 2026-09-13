# Encoding correction — round 6 report.md

Filed 13 September 2026, the same day the round-6 report was received. Ruled by Viktor:
correct the file and patch the tool.

## What was wrong

Every non-ASCII character in `report.md` as originally written (em dashes, `±`, `→`) was
mojibake. Line 1 read:

    I am Meta Muse Spark 1.3 â\x80\x94 first reviewer in this project...

instead of:

    I am Meta Muse Spark 1.3 — first reviewer in this project...

All-ASCII content — every verdict, every code excerpt, the release-gate finding — was
unaffected throughout. This was a defect in how the response was written to disk, not in
what the model said, and not in the substance of anything already reported to Viktor.

## Root cause

`docs/build/send_audit_round.py` read the streamed response with
`resp.iter_lines(decode_unicode=True)` without first setting `resp.encoding`. OpenRouter's
SSE response carries no explicit charset in its `Content-Type` header, and `requests` falls
back to ISO-8859-1 (Latin-1) — the old HTTP default — whenever a text response doesn't name
one. The API's actual body is UTF-8, so every multi-byte UTF-8 character was decoded as two
or three wrong Latin-1 codepoints, then written back out as UTF-8 — a real but fully
reversible corruption.

## Why the fix is trustworthy

The corruption is a deterministic, bijective transform (UTF-8 bytes read as Latin-1
codepoints, one codepoint per byte, then re-encoded as UTF-8), so it can be undone exactly:

    corrected_text = original_file_bytes.decode("utf-8").encode("latin-1").decode("utf-8")

Applied to the file as received, this round-trips cleanly with no decode errors, and the
only non-ASCII characters remaining afterward are legitimate typography (`±`, `–`, `—`,
`→`) — no `Â`/`Ã`/`â` mojibake markers are left anywhere in the result. This is a mechanical
decode fix, not a content edit: the corrected file states exactly what the model said,
nothing added or removed.

## What changed, byte-for-byte

| file | bytes | chars | SHA-256 |
|---|---|---|---|
| `report.md`, as originally written (corrupted) | 17,353 | 17,072 | `aae7ac9d6eb8f803b20e4174772252ffd887b99d2098582861b4903b05e7ab87` |
| `report.md`, corrected | 17,072 | 16,885 | `ae9a6fd8eb0a3b3a0e65465e8897c99bb7b12ffb0d4326736200bf861cf692cc` |

`reasoning.txt` (825 bytes) contains no non-ASCII characters and is unaffected; its content
and hash are unchanged.

`run_metadata.json` is left exactly as written at send time — it is the contemporaneous
record of the API call itself (cost `$0.63386125`, `470,488`/`10,765` native tokens,
`finish_reason: stop`, timing, generation id), and none of that is wrong. Its
`"report_chars": 17072` field is a downstream count taken from the corrupted stream as it
was received; it is now stale by exactly the cause recorded here (the corrected file is
16,885 characters) and is left unedited rather than silently rewritten, per this project's
own practice of recording an error rather than erasing it.

## Fix going forward

`docs/build/send_audit_round.py` now sets `resp.encoding = "utf-8"` immediately after the
POST returns, before anything reads `resp.text` or iterates the stream — see the code
comment and the docstring's list of failure modes this script exists to make impossible,
which now names this one as its fourth entry. Round 7 onward is not exposed to this defect.
