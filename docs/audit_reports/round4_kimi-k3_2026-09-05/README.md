# Round 4 — Kimi K3, 5 September 2026

The fourth attempt at the Item 16 independent audit, and the first that returned a
complete report.

## What was sent

The seven files of `docs/audit_package/round4/UPLOAD_THESE`, built at `417cadf`, in the
order Section 4 of the reviewer instruction lists them. They were concatenated into a
single user message by `docs/build/send_audit_round.py`; each file is delimited by a
`BEGIN FILE` / `END FILE` marker carrying its name, and the bytes are unmodified. The
assembled payload was 1,085,418 bytes, sha256
`dd3d21d19b0a4115878c7b9156c80a2706c62882a549f72e497102fe2d1e4a8e`. Per-file sizes and
hashes are in `run_metadata.json`.

`PART7_LATER/` was withheld and never sent. There was no system prompt: rev 5 is the whole
instruction, and anything typed into a system-prompt box would have been an instruction to
the reviewer that exists in no file and no commit.

## How it was sent

Through the OpenRouter API, not a chat interface — the condition recorded for this run.

| setting | value |
|---|---|
| model | `moonshotai/kimi-k3` |
| provider | Moonshot AI, pinned (`only`, `allow_fallbacks: false`) |
| data collection | `deny` |
| max output | 200,000 tokens |
| streaming | on, written to disk as it arrived |

The provider is pinned because on this model it decides the output ceiling: DeepInfra
caps completions at 16,384 tokens — the exact ceiling that ended the 27 August run — and
Chutes at 65,535. Auto Router is what turned round 3 into an accident; `only` plus
fallbacks off makes a substitution an error rather than a different reviewer.

## What came back

| | |
|---|---|
| finish_reason | `stop` |
| provider reported | Moonshot AI |
| generation id | `gen-1788625445-Qw2zxNCm031hBTThejce` |
| tokens in / out | 251,485 / 41,861 (33,931 reasoning, 7,930 report) |
| cost | $1.38237 |
| started / finished (UTC) | 16:24:02 / 16:41:29 |

Files here:

- `report.md` — Parts 1-6 as returned, unedited.
- `reasoning.txt` — the model's reasoning trace, 146,394 chars.
- `run_metadata.json` — what was sent, with hashes, and what came back.
- `generation.json` — the provider's own billing row for the call.
- `http_error.txt` — the 401 from the first attempt, kept rather than deleted.

`report.md` and `reasoning.txt` are the raw streams. Nothing in this directory has been
edited after the fact.

## Notes for a later reader

The report was checked for structure only before being filed: all 44 rules carry a
verdict, Parts 1-6 are present, Part 7 was not begun. It was not graded or acted on before
the comparison against the round-3 (GLM 5.3 Flash) report.

That comparison was made later the same evening. It was reserved for Viktor by design; he
handed it to Claude instead, so it was written by the party whose code both reviewers
graded. It is in `docs/PHASE7_NEXT.md` under "The round-3 versus round-4 comparison", with
the reviewer-quality judgement deliberately left outside this repository. No finding from
either report had been acted on at the time of writing.

The reviewer stated its identity unprompted, as Section 5 asks — Kimi, made by Moonshot AI
— and disclosed that it cannot name its own checkpoint from the inside, so it cannot
confirm whether it is the same Kimi K3 that made the incomplete 2 September attempt.

The round-3 run was **not** disclosed to this reviewer. That was a deliberate decision,
made on 5 September and recorded in `PHASE7_NEXT.md`: a graded report already existed on
this same package, with none of its findings acted on, and telling the reviewer so would
have shaped what it looked at.

The first `--send` failed with HTTP 401 because a placeholder key was set literally.
Nothing was charged. The real key was later exposed in a screenshot and was deleted and
replaced after the run; rows in the provider activity export between the exposure and the
deletion should be treated as unverified.
