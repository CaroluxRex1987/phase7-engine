#!/usr/bin/env python3
"""
Round 6 fix-verification: ask the model that raised F1-F5 whether they are fixed.

WHAT THIS IS, AND WHY IT IS NOT send_audit_round.py

Viktor's ruling, 14 September 2026: closing F1-F5 does not require a fresh,
independent model. Meta Muse Spark 1.3 (round 6's auditor) is asked to verify
its own findings were actually fixed -- not to re-grade the Constitution from
scratch. Finding something new along the way would be a bonus, not the goal.
Deliberately not called "Round 7": that name is reserved for whenever a
genuinely independent model is next asked to look, which the project is
saving for a point where independence actually matters (the stated example
is before backtesting).

This is a separate script from send_audit_round.py, not a mode flag on it,
because the two have different lifecycles. send_audit_round.py gets
repointed at a new reviewer every round -- three repoints already, Kimi K3
to GPT-6 Astra to Meta Muse Spark 1.3. Verifying round 6's own findings only
makes sense asked of the model that made them, permanently, regardless of
whatever model a future round 7 uses. Importing send_audit_round.py's MODEL
constant would couple this script's identity to that module's mutable state:
a future repoint for round 7 would silently redirect this call too, sending
someone else's follow-up to a model that never made the finding it is being
asked to check. That is the same "one edit upstream" failure shape Muse
Spark 1.3's own F3 named for a fabricated-zero default three call frames
away from where it fires. So MODEL, PROVIDER_SLUG and pricing are pinned
here independently, even though it costs a small duplication of
send_audit_round.py's transport logic below.

WHAT IS SENT, AND WHY FULL FILES RATHER THAN DIFFS

This is a single-turn API call (`messages: [{"role": "user", ...}]`, same as
send_audit_round.py) -- Muse Spark 1.3 carries no memory of round 6 between
calls, so whatever it needs to judge a finding must be in this payload.
Round 6's own report.md is attached verbatim (the model's own words, not a
paraphrase of them -- Engineering Notes #24 records what a hand-described
package cost this project once already). Bare diff hunks were considered and
rejected: a three-line unified-diff context cannot show whether a promoted
constant is used consistently elsewhere in the same file, or whether a
dropped duplicate key was relied on somewhere else in that module. The full
current content of the eight files the five fixing commits touched is sent
instead -- real per-finding context, without resending the ~470,000-token
package a fresh full audit would cost.

Usage (from the repository root):

    set OPENROUTER_API_KEY=sk-or-...
    python docs/build/send_fix_verification.py
    python docs/build/send_fix_verification.py --send
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import sys
import time
from pathlib import Path

API_URL = "https://openrouter.ai/api/v1/chat/completions"
GENERATION_URL = "https://openrouter.ai/api/v1/generation"

# Pinned independently of send_audit_round.py -- see the module docstring's
# "WHAT THIS IS, AND WHY IT IS NOT send_audit_round.py" for why this is
# deliberate duplication, not an oversight.
MODEL = "meta/muse-spark-1.3"
PROVIDER_SLUG = "meta"
PROVIDER_DISPLAY_NAME = "Meta"

# Unchanged from round 6: never the limiting factor there, and this payload
# is far smaller.
MAX_OUTPUT_TOKENS = 100_000
LARGEST_PRIOR_RESPONSE = 36_085  # Kimi K3, 2 September 2026, no report produced

# meta/muse-spark-1.3 pricing at round-6 time, USD per token (verified against
# OpenRouter's live models API on 13 September 2026, not the marketing page --
# see send_audit_round.py's module docstring for what that page got wrong
# about 1.2). Re-verify before sending if this is run long after 14 September
# 2026; pricing is not re-checked by this script at run time.
PRICE_IN = 1.25 / 1_000_000
PRICE_OUT = 4.25 / 1_000_000

REPORT_PATH_REL = "docs/audit_reports/round6_muse-spark-1.3_2026-09-13/report.md"

# The eight files the five landed fixing commits touched
# (447966b F1, 3c7e9ae F2, 9b34163 F3, 154e534 F4, ac0a211 F5). Full current
# content, not diffs -- see the module docstring.
TOUCHED_FILES = [
    "models/entry_model.py",
    "indicators/indicators.py",
    "models/btc_context.py",
    "structure/structure.py",
    "core/engine_core.py",
    "models/signal_router.py",
    "core/panel_render.py",
    "models/decision_model.py",
]

REVIEW_NOTE = """You are Meta Muse Spark 1.3. Attached is your own report from round 6 of this
project's audit history (13 September 2026), delimited as report.md below.

This is a narrow follow-up, not a new round of the same audit. You are being
asked whether the three findings in your Part 2 (F1, F2, F3) are now fixed,
plus two items that trace directly to your own report but were not given
separate numbers there -- described below. You are not being asked to
re-grade the verdict table, reassess Part 3-6, or review anything outside
these five items. If you notice something else materially wrong while doing
this, say so -- that is a bonus, not the goal, and should not change your
verdicts on the five items below.

The five items:

F1 (your Part 2, T2-4 Explicit configuration, Moderate). Your Location
section named bare literals across five files, including two locations in
models/decision_model.py: the trend-health/entry-score bands
(">=75"/">=70"/">=50") and the MIN_ACTION_BIAS/RAW_BIAS_THRESHOLD naming
split. The first fix pass deliberately scoped out both of those two
decision_model.py locations, fixing only the other four files. Check the
four files it did fix (models/entry_model.py, indicators/indicators.py,
models/btc_context.py, structure/structure.py) against what your Location
section named.

F2 (your Part 2, Item 10 Consistent Semantics, Minor). Check
core/engine_core.py's "confidence_score" key against models/signal_router.py's.

F3 (your Part 2, Item 13/Item 8, Minor). Check models/signal_router.py's
_build_decision_object for the six 0.0 fallbacks you found.

F4 (not separately numbered in your report -- a downstream instance of the
same pattern your F3 described). Your F3 recommended "replace 0.0 defaults
with NaN-passthrough (_finite_or_nan-style) consistent with structure.hvn/lvn
handling". core/panel_render.py independently defaulted atr_stop, targets,
and current_price to a finite 0.0 one layer further downstream of the six
fields your F3 named. Check whether that is now NaN-safe.

F5 (not separately numbered in your report -- the two decision_model.py
locations your own F1 Location section named but the first fix pass scoped
out, described above). Check models/decision_model.py directly.

For each of the five, answer: Fixed / Not fixed / Partially fixed, with one
line citing the specific code that supports the verdict. Then, separately
and only if you have one: anything else you noticed, unprompted.
"""


def _utc_now() -> _dt.datetime:
    return _dt.datetime.now(_dt.timezone.utc)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_payload(repo_root: Path) -> tuple[str, list[dict]]:
    """Returns (payload text, [{name, bytes, sha256}] for the dry-run summary)."""
    records: list[dict] = []
    parts = [REVIEW_NOTE]

    report_bytes = (repo_root / REPORT_PATH_REL).read_bytes()
    report_text = report_bytes.decode("utf-8")
    records.append({"name": REPORT_PATH_REL, "bytes": len(report_bytes),
                     "sha256": _sha256(report_bytes)})
    parts.append(f"\n===== BEGIN FILE: report.md (your own round-6 report) =====\n")
    parts.append(report_text)
    parts.append("\n===== END FILE: report.md =====\n")

    for rel in TOUCHED_FILES:
        raw = (repo_root / rel).read_bytes()
        text = raw.decode("utf-8")
        records.append({"name": rel, "bytes": len(raw), "sha256": _sha256(raw)})
        parts.append(f"\n===== BEGIN FILE: {rel} =====\n")
        parts.append(text)
        parts.append(f"\n===== END FILE: {rel} =====\n")

    return "".join(parts), records


def build_request_body(payload: str, allow_data_collection: bool) -> dict:
    return {
        "model": MODEL,
        "messages": [{"role": "user", "content": payload}],
        "max_tokens": MAX_OUTPUT_TOKENS,
        "stream": True,
        "stream_options": {"include_usage": True},
        "provider": {
            "only": [PROVIDER_SLUG],
            "allow_fallbacks": False,
            "require_parameters": True,
            "data_collection": "allow" if allow_data_collection else "deny",
        },
    }


def _open_run_dir(repo_root: Path, force: bool) -> Path:
    stamp = _utc_now().strftime("%Y-%m-%d")
    run_dir = repo_root / "docs" / "audit_reports" / f"round6_fix-verification_{stamp}"
    report = run_dir / "report.md"
    if report.exists() and report.stat().st_size > 0 and not force:
        raise SystemExit(
            f"{report} already holds a response. Refusing to overwrite a paid run.\n"
            "Move it aside, or pass --force if you are sure."
        )
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def _fetch_generation(session, api_key: str, gen_id: str) -> dict | None:
    """The billing row for the call: provider actually used, native token counts, cost."""
    for attempt in range(8):
        time.sleep(2 + attempt)
        try:
            resp = session.get(
                GENERATION_URL,
                params={"id": gen_id},
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=30,
            )
            if resp.status_code == 200:
                return resp.json()
        except Exception:  # noqa: BLE001 - metadata is best effort, the report is not
            pass
    return None


def send(body: dict, api_key: str, run_dir: Path, metadata: dict) -> int:
    import requests  # pinned at 2.32.5 in requirements.txt

    report_path = run_dir / "report.md"
    reasoning_path = run_dir / "reasoning.txt"

    session = requests.Session()
    started = _utc_now()
    print(f"POST {API_URL}  model={MODEL}  provider={PROVIDER_SLUG}  "
          f"max_tokens={MAX_OUTPUT_TOKENS}", flush=True)

    resp = session.post(
        API_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json=body,
        stream=True,
        timeout=(30, 900),
    )

    # Same fix as send_audit_round.py, for the same reason: OpenRouter's
    # response carries no explicit charset, so `requests` would otherwise
    # fall back to Latin-1 for resp.text / iter_lines(decode_unicode=True),
    # silently mis-decoding every non-ASCII character. That is what
    # corrupted round 6's report.md.
    resp.encoding = "utf-8"

    if resp.status_code != 200:
        detail = resp.text[:8000]
        (run_dir / "http_error.txt").write_text(
            f"HTTP {resp.status_code}\n\n{detail}\n", encoding="utf-8"
        )
        print(f"\nHTTP {resp.status_code}. Body saved to {run_dir / 'http_error.txt'}",
              file=sys.stderr)
        return 2

    gen_id = None
    finish_reason = None
    usage = None
    content_chars = 0
    reasoning_chars = 0
    last_report = time.time()

    with open(report_path, "w", encoding="utf-8", newline="") as report_f, \
         open(reasoning_path, "w", encoding="utf-8", newline="") as reasoning_f:
        for raw_line in resp.iter_lines(decode_unicode=True):
            if not raw_line:
                continue
            if raw_line.startswith(":"):  # OPENROUTER PROCESSING keep-alive
                continue
            if not raw_line.startswith("data: "):
                continue
            data = raw_line[6:].strip()
            if data == "[DONE]":
                break
            try:
                event = json.loads(data)
            except json.JSONDecodeError:
                continue

            gen_id = event.get("id") or gen_id
            if event.get("usage"):
                usage = event["usage"]
            for choice in event.get("choices") or []:
                delta = choice.get("delta") or {}
                text = delta.get("content")
                if text:
                    report_f.write(text)
                    report_f.flush()
                    content_chars += len(text)
                thought = delta.get("reasoning")
                if thought:
                    reasoning_f.write(thought)
                    reasoning_f.flush()
                    reasoning_chars += len(thought)
                if choice.get("finish_reason"):
                    finish_reason = choice["finish_reason"]

            if time.time() - last_report >= 30:
                elapsed = int((_utc_now() - started).total_seconds())
                print(f"  {elapsed:>5}s  reasoning {reasoning_chars:>9,} chars  "
                      f"report {content_chars:>9,} chars", flush=True)
                last_report = time.time()

    finished = _utc_now()
    metadata.update(
        {
            "started_utc": started.isoformat(),
            "finished_utc": finished.isoformat(),
            "elapsed_seconds": round((finished - started).total_seconds(), 1),
            "generation_id": gen_id,
            "finish_reason": finish_reason,
            "usage": usage,
            "report_chars": content_chars,
            "reasoning_chars": reasoning_chars,
        }
    )

    generation = _fetch_generation(session, api_key, gen_id) if gen_id else None
    if generation:
        (run_dir / "generation.json").write_text(
            json.dumps(generation, indent=2), encoding="utf-8"
        )
        row = generation.get("data", generation)
        metadata["provider_reported"] = row.get("provider_name")
        metadata["native_tokens_prompt"] = row.get("native_tokens_prompt")
        metadata["native_tokens_completion"] = row.get("native_tokens_completion")
        metadata["total_cost_usd"] = row.get("total_cost")

    (run_dir / "run_metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )

    print()
    print(f"finish_reason        {finish_reason}")
    if usage:
        print(f"tokens in / out      {usage.get('prompt_tokens')} / "
              f"{usage.get('completion_tokens')}")
    provider_reported = metadata.get("provider_reported")
    print(f"provider reported    {provider_reported or 'unavailable'}")
    print(f"cost                 {metadata.get('total_cost_usd', 'unavailable')}")
    print(f"report               {report_path}  ({content_chars:,} chars)")
    print(f"reasoning            {reasoning_path}  ({reasoning_chars:,} chars)")

    problems = []
    if finish_reason == "length":
        problems.append(
            "finish_reason=length -- the response hit the output ceiling and is "
            "TRUNCATED. Do not treat the report as complete."
        )
    if provider_reported and provider_reported != PROVIDER_DISPLAY_NAME:
        problems.append(
            f"the response was served by {provider_reported!r}, not "
            f"{PROVIDER_DISPLAY_NAME!r}. The reviewer is not the one that was ruled."
        )
    if content_chars == 0:
        problems.append(
            "no report content was returned -- only reasoning, if anything."
        )
    for problem in problems:
        print(f"\nWARNING: {problem}", file=sys.stderr)
    return 1 if problems else 0


def main(argv: list[str] | None = None) -> int:
    repo_root = Path(__file__).resolve().parents[2]

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=None,
                        help="where the response is written (default: under docs/audit_reports/)")
    parser.add_argument("--send", action="store_true",
                        help="actually make the call; without it this is a dry run")
    parser.add_argument("--force", action="store_true",
                        help="overwrite an existing response in the output directory")
    parser.add_argument("--allow-data-collection", action="store_true",
                        help="permit providers that may train on the prompt (default: deny)")
    args = parser.parse_args(argv)

    if MAX_OUTPUT_TOKENS <= LARGEST_PRIOR_RESPONSE:
        raise SystemExit("MAX_OUTPUT_TOKENS is not above the largest prior response.")

    payload, records = build_payload(repo_root)
    payload_bytes = payload.encode("utf-8")
    estimated_prompt_tokens = round(len(payload) / 4)

    print("files")
    for record in records:
        print(f"  {record['bytes']:>9,}  {record['sha256'][:16]}  {record['name']}")
    print(f"payload        {len(payload_bytes):,} bytes, {len(payload):,} chars, "
          f"sha256 {_sha256(payload_bytes)}")
    print(f"estimated in   ~{estimated_prompt_tokens:,} tokens "
          f"(round 6's full audit package was ~470,000 -- this is a fix-"
          f"verification pass, not a fresh audit, so it carries the report "
          f"plus eight touched files, not the codebase)")
    print(f"model          {MODEL}")
    print(f"provider       {PROVIDER_SLUG} only, fallbacks off, data_collection "
          f"{'allow' if args.allow_data_collection else 'deny'}")
    print(f"max output     {MAX_OUTPUT_TOKENS:,} tokens "
          f"(largest prior response {LARGEST_PRIOR_RESPONSE:,})")
    low = estimated_prompt_tokens * PRICE_IN + 5_000 * PRICE_OUT
    high = estimated_prompt_tokens * PRICE_IN + 20_000 * PRICE_OUT
    print(f"cost estimate  ${low:.2f} - ${high:.2f} "
          f"(input plus 5k-20k output at $1.25/$4.25 per M -- five short "
          f"verdicts plus citations should need far less output than a full "
          f"audit report)")

    metadata = {
        "model": MODEL,
        "provider_pinned": PROVIDER_SLUG,
        "max_output_tokens": MAX_OUTPUT_TOKENS,
        "purpose": "round6_fix_verification",
        "files": records,
        "payload_sha256": _sha256(payload_bytes),
        "payload_bytes": len(payload_bytes),
        "estimated_prompt_tokens": estimated_prompt_tokens,
        "data_collection": "allow" if args.allow_data_collection else "deny",
    }

    if not args.send:
        print("\nDry run. Nothing was sent. Re-run with --send to make the call.")
        return 0

    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        raise SystemExit(
            "OPENROUTER_API_KEY is not set in this shell.\n"
            "    set OPENROUTER_API_KEY=sk-or-...\n"
            "then run this command again in the same window."
        )

    run_dir = args.out_dir or _open_run_dir(repo_root, args.force)
    run_dir.mkdir(parents=True, exist_ok=True)
    body = build_request_body(payload, args.allow_data_collection)
    return send(body, api_key, run_dir, metadata)


if __name__ == "__main__":
    sys.exit(main())
