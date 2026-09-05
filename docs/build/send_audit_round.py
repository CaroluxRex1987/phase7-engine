#!/usr/bin/env python3
"""Send a built audit package to a named reviewer model through the OpenRouter API.

Written for round 4 (Kimi K3). Three failures in this project's audit history are
what this script exists to make impossible:

  * a run that went to whatever the Auto Router picked (round 3, GLM 5.3 Flash) --
    here the model AND the serving provider are pinned, with fallbacks off, so a
    substitution is an error rather than a silently different reviewer;
  * a run that died at a 16,384-token output ceiling with finish_reason=length,
    burning the full input charge -- here MAX_OUTPUT_TOKENS is explicit, is
    asserted to exceed the largest response this project has ever received
    (36,085 tokens), and the finish reason is recorded;
  * a run whose output existed only in a chat window -- here every token is
    streamed to disk as it arrives, under docs/audit_reports/, which is tracked.

Nothing is sent unless --send is passed. Without it the script assembles the
payload, hashes it, prints the size and the cost estimate, and stops.

Usage (from the repository root):

    set OPENROUTER_API_KEY=sk-or-...
    python docs/build/send_audit_round.py
    python docs/build/send_audit_round.py --send
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

MODEL = "moonshotai/kimi-k3"
PROVIDER_SLUG = "moonshotai"
PROVIDER_DISPLAY_NAME = "Moonshot AI"

# Verified against openrouter.ai/api/v1/models/moonshotai/kimi-k3/endpoints on
# 5 September 2026: the Moonshot AI endpoint serves 1,048,576 context and
# 943,718 max completion tokens. Other endpoints of the same model do NOT --
# DeepInfra caps completions at 16,384, which is the exact ceiling that killed
# the 27 August run, and Chutes at 65,535. That is why the provider is pinned.
MAX_OUTPUT_TOKENS = 200_000
LARGEST_PRIOR_RESPONSE = 36_085  # Kimi K3, 2 September 2026, no report produced

# Moonshot AI endpoint pricing at the time of writing, USD per token.
PRICE_IN = 3.0 / 1_000_000
PRICE_OUT = 15.0 / 1_000_000

# The order the reviewer instruction itself uses in section 4, "What you will be
# given". The instruction is item 1 and goes first; the rest follow as it lists
# them. The set is asserted exactly: an extra or missing file aborts the run,
# because several rounds' directories carry the same filenames.
INSTRUCTION_FILE = "item16_review_instruction_rev5.md"
ATTACHMENT_FILES = [
    "Phase7_Constitution_v1.0_RATIFIED_AUDITCOPY.txt",
    "phase7_engine_source.md",
    "phase7_test_suite.md",
    "MANIFEST.md",
    "version_control_history.md",
    "execution_transcripts.md",
]
EXPECTED_FILES = [INSTRUCTION_FILE] + ATTACHMENT_FILES

DELIVERY_NOTE = (
    "The review instruction follows in full, and after it the six files it lists "
    "in section 4, each delimited by a BEGIN FILE / END FILE marker carrying the "
    "file's name. The files are supplied as text in a single message because this "
    "is an API call and not a chat interface; their bytes are unmodified.\n"
)


def _utc_now() -> _dt.datetime:
    return _dt.datetime.now(_dt.timezone.utc)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_package(package_dir: Path) -> tuple[list[dict], dict]:
    """Read and verify the package. Returns (file records, {name: text})."""
    if not package_dir.is_dir():
        raise SystemExit(f"package directory not found: {package_dir}")

    found = sorted(p.name for p in package_dir.iterdir() if p.is_file())
    expected = sorted(EXPECTED_FILES)
    if found != expected:
        missing = [n for n in expected if n not in found]
        extra = [n for n in found if n not in expected]
        raise SystemExit(
            "package contents do not match what this script sends.\n"
            f"  directory: {package_dir}\n"
            f"  missing:   {missing or 'none'}\n"
            f"  unexpected:{extra or 'none'}\n"
            "Refusing to send a package that is not the one this script describes."
        )

    records: list[dict] = []
    texts: dict[str, str] = {}
    for name in EXPECTED_FILES:
        raw = (package_dir / name).read_bytes()
        try:
            texts[name] = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise SystemExit(f"{name} is not valid UTF-8: {exc}")
        records.append({"name": name, "bytes": len(raw), "sha256": _sha256(raw)})
    return records, texts


def build_payload(texts: dict[str, str]) -> str:
    parts = [DELIVERY_NOTE, "\n", texts[INSTRUCTION_FILE], "\n"]
    for name in ATTACHMENT_FILES:
        parts.append(f"\n===== BEGIN FILE: {name} =====\n")
        parts.append(texts[name])
        parts.append(f"\n===== END FILE: {name} =====\n")
    return "".join(parts)


def build_request_body(payload: str, allow_data_collection: bool) -> dict:
    return {
        "model": MODEL,
        "messages": [{"role": "user", "content": payload}],
        "max_tokens": MAX_OUTPUT_TOKENS,
        "stream": True,
        "stream_options": {"include_usage": True},
        "provider": {
            # "only" is the exclusive whitelist; allow_fallbacks is belt and
            # braces. If the pinned provider cannot serve the request the call
            # fails loudly instead of quietly becoming a different reviewer.
            "only": [PROVIDER_SLUG],
            "allow_fallbacks": False,
            "require_parameters": True,
            "data_collection": "allow" if allow_data_collection else "deny",
        },
    }


def _open_run_dir(repo_root: Path, force: bool) -> Path:
    stamp = _utc_now().strftime("%Y-%m-%d")
    run_dir = repo_root / "docs" / "audit_reports" / f"round4_kimi-k3_{stamp}"
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

    if resp.status_code != 200:
        detail = resp.text[:8000]
        (run_dir / "http_error.txt").write_text(
            f"HTTP {resp.status_code}\n\n{detail}\n", encoding="utf-8"
        )
        print(f"\nHTTP {resp.status_code}. Body saved to {run_dir / 'http_error.txt'}",
              file=sys.stderr)
        if resp.status_code == 404:
            print(
                "A 404 with no endpoints means the pinned provider cannot serve this\n"
                "request under the constraints set here -- most likely the data_collection\n"
                '"deny" policy, or max_tokens above that endpoint\'s ceiling. That is a\n'
                "decision to make deliberately, not a flag to flip. Do not switch to Auto\n"
                "Router.",
                file=sys.stderr,
            )
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
            "TRUNCATED. This is the failure mode of 27 August. Do not treat the "
            "report as complete."
        )
    if provider_reported and provider_reported != PROVIDER_DISPLAY_NAME:
        problems.append(
            f"the response was served by {provider_reported!r}, not "
            f"{PROVIDER_DISPLAY_NAME!r}. The reviewer is not the one that was ruled."
        )
    if content_chars == 0:
        problems.append(
            "no report content was returned -- only reasoning, if anything. This is "
            "what happened on 2 September: 36,085 tokens of reasoning and no report."
        )
    for problem in problems:
        print(f"\nWARNING: {problem}", file=sys.stderr)
    return 1 if problems else 0


def main(argv: list[str] | None = None) -> int:
    repo_root = Path(__file__).resolve().parents[2]
    default_package = repo_root / "docs" / "audit_package" / "round4" / "UPLOAD_THESE"

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-dir", type=Path, default=default_package)
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

    records, texts = read_package(args.package_dir)
    payload = build_payload(texts)
    payload_bytes = payload.encode("utf-8")
    estimated_prompt_tokens = round(len(payload) / 4)

    print(f"package        {args.package_dir}")
    for record in records:
        print(f"  {record['bytes']:>9,}  {record['sha256'][:16]}  {record['name']}")
    print(f"payload        {len(payload_bytes):,} bytes, {len(payload):,} chars, "
          f"sha256 {_sha256(payload_bytes)}")
    print(f"estimated in   ~{estimated_prompt_tokens:,} tokens "
          f"(round 3's same package billed 251,148)")
    print(f"model          {MODEL}")
    print(f"provider       {PROVIDER_SLUG} only, fallbacks off, data_collection "
          f"{'allow' if args.allow_data_collection else 'deny'}")
    print(f"max output     {MAX_OUTPUT_TOKENS:,} tokens "
          f"(largest prior response {LARGEST_PRIOR_RESPONSE:,})")
    low = estimated_prompt_tokens * PRICE_IN + 40_000 * PRICE_OUT
    high = estimated_prompt_tokens * PRICE_IN + 120_000 * PRICE_OUT
    print(f"cost estimate  ${low:.2f} - ${high:.2f} "
          f"(input plus 40k-120k output at $3/$15 per M)")

    metadata = {
        "model": MODEL,
        "provider_pinned": PROVIDER_SLUG,
        "max_output_tokens": MAX_OUTPUT_TOKENS,
        "package_dir": str(args.package_dir),
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
