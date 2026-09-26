# Round 1 — the original ratification audit, 27 August 2026

Run 1 (DeepSeek V4 Pro, blind review) and Runs A, B and C (Kimi K3), all run on
27 August 2026 through the OpenRouter chat room. Recorded as lost on 20 September 2026
(docs/PHASE7_HISTORY.md, "20 September 2026 — correction: the round-1 audit outputs were
lost"). Found by Viktor on 23 September 2026 in `D:\USB Backup\Phase7_Engine documents\`,
a backup that ends 30 August, and filed here on 26 September. The full account is in
docs/PHASE7_HISTORY.md, "26 September 2026 — correction: the round-1 audit outputs were
recovered".

## The files

| File | What it is | Bytes | SHA256 |
|---|---|---|---|
| `Run1_DeepSeek_blind_review.md` | Run 1: source only, no Constitution, ten ranked findings | 15,923 | `078dcf7c5794881244624eb957ae6ff60420f7fcd9cb8b26ec63f7d784d2e839` |
| `RunA_KimiK3_MVA_gate_findings.md` | Run A: Items 2, 3, 6 and 18 | 18,366 | `1718afcac29698eab0628d34de3bda3474692bebffe1b62f81c856fa9a064fd3` |
| `RunA_KimiK3_room_export.json` | Run A: the OpenRouter room export (prompt, reasoning, output) | 544,271 | `0ca783a2247283f82769d98b692a5ee95c02c16c9bda2d591bc54e0a2752f553` |
| `RunA_KimiK3_truncated_reasoning_trace.md` | Run A's first attempt: cut off at 16,384 output tokens, no findings | 73,925 | `26ab14bb446b4966b655f46d3a03f6b5c2914146409fa2c7785333246e451e26` |
| `RunB_KimiK3_tier1_findings.md` | Run B: the other 17 Tier 1 items | 24,682 | `d8280b4cea95ed60124a575d8817ef281e14f89c4949493bf1bb7c893110f21e` |
| `RunC_KimiK3_tiers234_findings.md` | Run C: Tiers 2, 3 and 4 | 32,019 | `991dd7ba866429a503e43cec44b22df02a943fd3c7b69000444533eb0f420f89` |

The hashes are the ones Viktor took with `certutil -hashfile … SHA256` on 23 September,
before any file was copied or opened. Every file here is byte-identical to them.
`.gitattributes` switches line-ending normalisation off for `docs/audit_reports/**`, so
git stores and checks out these bytes unchanged.

## What the hashes prove, and what they do not

They prove the content has not changed since 23 September. They do not prove these are
the files as made on 27 August. That evidence is weaker: the backup's modification dates
(27 August, 06:12 to 09:43), and one cross-check against a primary source, below.

## How far each file is verbatim

The five `.md` files are not raw provider output. Each opens with a short header, above a
`---` rule, written when the file was made; who wrote it is not recorded. The headers of
Runs A, B and C say "Auditor's verbatim output". Run A's and the trace's say the text was
recovered from the session transcript; Run 1's and the trace's say that happened after the
OpenRouter room was deleted.

**Run A's findings were checked against the room export** on 26 September. The body below
the header matches the export's final assistant message character for character, except
for 21 newline characters present in the export and absent from the `.md` file. With all
whitespace removed, the two are identical (15,494 characters). The export's assistant
message is dated 27 August 03:39 UTC (05:39 local); the request log read on 20 September
lists a Kimi K3 generation at 05:39 local.

**Not checked:** Run 1, Run B and Run C have no primary source in this folder, so their
bodies rest on their headers. The truncated trace is from an earlier attempt than the
export records, and does not match the export's reasoning.
