# Provider activity export — OpenRouter, pulled 5 September 2026

`openrouter_activity_20260905.csv` — 723 rows, the complete request history for this
account. This is the primary source for every independence claim the project makes.

## Why it is in the repository

Rule 29: where a project keeps a record of what happened, check whether some system
already recorded it as a side effect of its own job, and prefer that source. This is
that source. Twice the project's own ledger, written from recollection, has been wrong
about which model families had seen this codebase, and both times only this export
found it. A claim about independence that cannot be checked against it is not a claim
the project can stand behind.

## What it establishes

- **All 723 rows are `variant=standard`.** No free endpoint, ever, so no Phase-7
  material was sent anywhere that trains on it. Every "session exposure clears" ruling
  rests on this line.
- **The five models that worked on the codebase**, all through Aider, all under the key
  `Nexus-Key`: DeepSeek v3 (315), Claude Sonnet 4 (194), DeepSeek R1 (96), Mistral Nemo
  (71 across two keys), Claude 3 Haiku (4). 681 calls.
- **Z.ai is not clean.** `z-ai/glm-5.3` ran 28 August at 22:53 through the Chatroom,
  104,394 in / 55,179 out / 48,167 reasoning, finish=stop — eleven days before
  `z-ai/glm-5.3-flash` produced the round-3 report. Under the lab-not-checkpoint rule
  the round-3 reviewer was not independent.
- **Kimi K3 clears.** All 14 of its calls are `OpenRouter: Chatroom`; none went through
  Aider. Session exposure only. Its exposure is nonetheless eight substantive reads on
  27 August of 93K-110K input each, plus 36,085 output tokens on 2 September, where the
  project's record described a single truncated attempt.
- **Outputs produced and never saved:** four Kimi completions on 27 August (16,361,
  15,971, 18,386, 9,819 tokens); Qwen's 11,964 tokens on 2 September at 13:42 UTC, which
  means what Qwen actually said in round 2 is lost; three Luna Pro responses on
  3 September of 165,887, 162,555 and 65,221 tokens. One row on 2 September at 08:59:19
  records no model at all.
- **The 27 August token ceiling**, exactly: `kimi-k3`, completion 16,384, reasoning
  18,668, `finish=length`. 2^14. The reason the max-output setting is checked before
  every audit run.

## What it does not contain

The `user` column is empty on all 723 rows. `api_key_name` holds key *labels*
(`Nexus-Key`, `aider-key (disabled)`) and no key material. `generation_id` values are
opaque OpenRouter request identifiers. Costs and token volumes are present, and are
published deliberately: an audit trail that omits what each attempt cost is a weaker
record than one that does not.

## Timestamps

`created_at` is UTC. The project's narrative is written in Europe/Stockholm, UTC+2 on
these dates — so the round-2 attempts recorded as 10:53, 15:38, 15:42 and 15:58 appear
here as 08:53, 13:38, 13:42 and 13:58.
