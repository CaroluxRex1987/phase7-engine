#!/usr/bin/env python3
"""Round 8's fix verification: ask round 8's auditor whether its findings were fixed.

WHAT DECIDED IT

PHASE7_DECISIONS.md, "Decision, 16 October 2026 -- round 8's fix verification:
what is checked, what is sent, and to whom" (Claude's, under Viktor's
delegation of 4 October): MiMo-V2.6-Pro, round 8's auditor, is asked whether
the Critical's fix holds, whether its own fixed findings are fixed, and whether
any other change to code it read carries a new defect. One request, a single
turn, on a package close to full size, built from a commit tagged before the
send. How this script does that is Claude's design in the commit that adds it,
filed in PHASE7_DECISIONS.md, "Decision, 17 October 2026 -- the fix
verification's tooling".

WHY A SCRIPT OF ITS OWN

send_fix_verification.py is pinned to round 6's auditor by design, and
send_audit_round.py is repointed every round. Importing either's constants
would let a later repoint redirect this send. So the model, the provider, the
prices and the transport are pinned here, as send_fix_verification.py pinned
its own -- a deliberate duplication of the streaming loop. The token check is
the one module shared: package_token_check.py pins each model's tokenizer by
SHA-256, and its MiMo entry is the one round 8 was measured with.

WHAT IS SENT

One user message, built from git objects at one commit -- never from the
working tree -- so the same commit gives the same bytes on any machine. The
commit is the one the tag round8-verify-sent-<date> points at: --send refuses
without exactly one such tag. Without a tag, the dry run builds from HEAD so
the package can be measured before anything is tagged.

  * the instruction, docs/audit_package/round8_fix_verification_instruction.md;
  * round 8's run-2 reports verbatim (turn1_report.md, turn2_report.md),
    refused unless each hashes to what its run recorded;
  * PHASE7_DECISIONS.md from the triage of 5 October to the end of the
    decision of 16 October, an unbroken excerpt;
  * the Constitution's audit copy, as round 8's package carried it: the same
    bytes, refused unless they hash to what round 8's run 2 recorded. That
    copy had Windows line endings; the blob in git has LF; the CRLF form is
    rebuilt from the blob and checked;
  * engine.diff, from e186423 to the commit sent, over the engine's files;
  * every engine file in full at that commit: the .py files the engine's own
    code fingerprint covers (core/code_fingerprint.py, EXCLUDED_DIR_NAMES);
  * tests_changed.diff over the test files that existed at e186423, and every
    test file added since, in full, except this script's own test file.

The diffs start at e186423, not at 217ede6 as the decision of 16 October
words it. Round 8's package was built from e186423 (the tag
round7-sent-2026-09-30) and sent from 217ede6: the engine's files are the same
at both -- refused here otherwise -- so engine.diff is the same either way.
The test files are not: test_package_token_check.py and
test_send_audit_round.py changed between the two, after the package was
built. From e186423 the test diff shows every change to what the auditor
read.

THE CHECKPOINT

OpenRouter's record of both round-8 runs names the model
xiaomi/mimo-v2.6-pro-20260921 (ROUND8_CHECKPOINT); the model page lists only
xiaomi/mimo-v2.6-pro, with no dated version (read 15 October with a web tool,
not by a call). The probe asks for the dated name first and, if OpenRouter
refuses it, the undated one; the send uses the name the probe was accepted
with. The probe's own generation record is then read, and the send is refused
unless it names ROUND8_CHECKPOINT. --different-checkpoint NAME lets it go to
the checkpoint the probe named instead, recorded as such: the decision of
16 October says a different name makes the result a different checkpoint's,
and the flag makes sending it a choice made before paying for the run rather
than a finding afterwards. The send's own generation record is checked again,
and a different name there is printed and recorded.

RUNS

At most two, the cap of 30 September. A run is any send that left a reply on
record (run_metadata.json, or a report.md that is not empty), cut off or not.
The second needs --second-run, run 1's three files committed, the same first
message by its SHA-256, and a commit to docs/PHASE7_DECISIONS.md after the one
that committed run 1's report: the decision of 16 October says whether to send
a second run is decided after the first reply and filed before the second. The
filing is checked by git, not asserted. No run is ever written over.

Usage (from the repository root):

    python docs/build/send_round8_fix_verification.py --tokenizer-dir <folder>
    git tag round8-verify-sent-<date>
    set OPENROUTER_API_KEY=sk-or-...
    python docs/build/send_round8_fix_verification.py --tokenizer-dir <folder> --send

The tokenizer folder is MiMo's, as for round 8:
G:\\Phase_7_Engine_Random_Files\\Docs\\04_Data\\MiMo-V2.6-Pro-MOPD_tokenizer_adea8e2
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

API_URL = "https://openrouter.ai/api/v1/chat/completions"
GENERATION_URL = "https://openrouter.ai/api/v1/generation"

# Pinned here, not imported: see "WHY A SCRIPT OF ITS OWN".
MODEL = "xiaomi/mimo-v2.6-pro"
ROUND8_CHECKPOINT = "xiaomi/mimo-v2.6-pro-20260921"
# The probe tries these in order; the send uses the first one accepted.
MODEL_NAMES = (ROUND8_CHECKPOINT, MODEL)
PROVIDER_SLUG = "xiaomi"
PROVIDER_NAME = "Xiaomi"
TOKEN_CHECK_MODEL = "mimo-v2.6-pro"

# Xiaomi's endpoint's output ceiling, read 4 October 2026 from OpenRouter's
# endpoints API (send_audit_round.py, where it is recorded). Not re-read here.
MAX_OUTPUT_TOKENS = 131_072
# Round 8's run 2, first reply, 4 October 2026: 80,023 completion tokens,
# 68,464 of them reasoning, finish_reason stop
# (docs/audit_reports/round8_mimo-v2.6-pro_run2_2026-10-04/turn1_run_metadata.json).
LARGEST_PRIOR_RESPONSE = 80_023
# USD per token on Xiaomi's endpoint, read 4 October 2026 (the same record).
# Not re-checked by this script.
PRICE_IN = 0.435 / 1_000_000
PRICE_OUT = 0.87 / 1_000_000

REASONING = {"enabled": True}
PROBE_PROMPT = "What is 17 multiplied by 24? Reply with the number only."
PROBE_MAX_TOKENS = 4_096
GENERATION_LOOKUP_WAITS = (5,) * 6 + (15,) * 6 + (30,) * 6

# What the auditor read in round 8, and where it was sent from.
READ_COMMIT = "e1864234c3f8ebc056d86a71e3b924d58fc5d105"   # round7-sent-2026-09-30
SENT_COMMIT = "217ede65b34165531ae936dc5980106564eb9a37"   # round8-sent-2026-10-04
VERIFY_TAG_PREFIX = "round8-verify-sent-"
VERIFY_TAG_PATTERN = re.compile(r"^round8-verify-sent-\d{4}-\d{2}-\d{2}$")

INSTRUCTION = "docs/audit_package/round8_fix_verification_instruction.md"
ROUND8_RUN2 = "docs/audit_reports/round8_mimo-v2.6-pro_run2_2026-10-04"
# SHA-256 of each report as its run recorded it (report_sha256 in
# turn1_run_metadata.json and turn2_run_metadata.json); checked against git's
# blob at the commit sent.
ROUND8_REPORTS = {
    f"{ROUND8_RUN2}/turn1_report.md":
        "00022d076afd1e3da2d99a07ee4344c06a9ab9235606ed5789ba3b5b2a90b860",
    f"{ROUND8_RUN2}/turn2_report.md":
        "75f0a1224bdb54f4055476bd61284e890925888494e1d0172ca931d02137e3ec",
}
CONSTITUTION = "docs/audit_package/Phase7_Constitution_v1.0_RATIFIED_AUDITCOPY.txt"
# round 8 run 2's turn1_run_metadata.json, files[]: the bytes it was sent.
CONSTITUTION_ROUND8_SHA256 = "08f663a3b591c50e9ac0c62a3512c2a96c00ffb5234a5ed40814c52015aea700"

DECISIONS = "docs/PHASE7_DECISIONS.md"
RULINGS_FIRST = ("## Ruling, 5 October 2026 \u2014 round 8 triaged")
RULINGS_LAST = ("## Decision, 16 October 2026 \u2014 round 8's fix verification")
RULINGS_NAME = (f"{DECISIONS} (excerpt: \"Ruling, 5 October 2026 \u2014 round 8 "
                "triaged\" to the end of \"Decision, 16 October 2026 \u2014 round 8's "
                "fix verification\")")
ENGINE_DIFF_NAME = "engine.diff"
TESTS_DIFF_NAME = "tests_changed.diff"
# Tests of the sending, not of the engine (WHAT IS SENT).
OWN_TESTS = frozenset({"tests/test_send_round8_fix_verification.py"})

DELIVERY_NOTE = (
    "The fix-verification instruction follows in full, and after it {n} files, each "
    "between a BEGIN FILE and an END FILE marker carrying its name. They are supplied "
    "as text in a single message because this is an API call and not a chat "
    "interface; their bytes are unmodified.\n"
)

RUN_DIR_PREFIX = "round8-verify_mimo-v2.6-pro_"
MAX_RUNS = 2

# Pinned so the diffs are the same bytes whatever the machine's git settings.
_DIFF_CONFIG = ("-c", "core.quotepath=off", "-c", "diff.noprefix=false",
                "-c", "diff.mnemonicPrefix=false", "-c", "diff.relative=false",
                "-c", "diff.suppressBlankEmpty=false", "-c", "diff.context=3",
                "-c", "diff.interHunkContext=0")
_DIFF_ARGS = ("diff", "--no-color", "--no-ext-diff", "--no-textconv", "--no-renames",
              "--diff-algorithm=myers", "--indent-heuristic", "-U3",
              "--src-prefix=a/", "--dst-prefix=b/")


def _load_token_check():
    path = Path(__file__).with_name("package_token_check.py")
    spec = importlib.util.spec_from_file_location("phase7_verify_token_check", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


token_check = _load_token_check()


def _utc_now() -> _dt.datetime:
    return _dt.datetime.now(_dt.timezone.utc)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# --- git ---------------------------------------------------------------------------


def _git(repo: Path, *args, check=True) -> subprocess.CompletedProcess:
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True)
    if check and result.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed: "
                         f"{result.stderr.decode('utf-8', 'replace').strip()}")
    return result


def _git_text(repo: Path, *args) -> str:
    return _git(repo, *args).stdout.decode("utf-8").strip()


def blob(repo: Path, commit: str, path: str) -> bytes:
    """A file's bytes as git holds them at `commit`: no line-ending conversion."""
    result = _git(repo, "cat-file", "blob", f"{commit}:{path}", check=False)
    if result.returncode != 0:
        raise SystemExit(f"{path} is not in commit {commit[:7]}. Nothing was sent.")
    return result.stdout


def tracked_files(repo: Path, commit: str) -> list[str]:
    out = _git(repo, "ls-tree", "-r", "-z", "--name-only", commit).stdout.decode("utf-8")
    return sorted(p for p in out.split("\0") if p)


def _excluded_dir_names(repo: Path) -> frozenset:
    path = repo / "core" / "code_fingerprint.py"
    spec = importlib.util.spec_from_file_location("phase7_verify_fingerprint", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return frozenset(module.EXCLUDED_DIR_NAMES)


def engine_files(repo: Path, commit: str, excluded=None) -> list[str]:
    """The .py files the code fingerprint covers, as git holds them at `commit`:
    no part of the path a name in EXCLUDED_DIR_NAMES."""
    excluded = _excluded_dir_names(repo) if excluded is None else excluded
    return [p for p in tracked_files(repo, commit)
            if p.endswith(".py") and not set(p.split("/")[:-1]) & excluded]


def files_under_tests(repo: Path, commit: str) -> list[str]:
    return [p for p in tracked_files(repo, commit) if p.startswith("tests/")]


def diff(repo: Path, a: str, b: str, paths: list[str]) -> str:
    if not paths:
        return ""
    out = _git(repo, *_DIFF_CONFIG, *_DIFF_ARGS, a, b, "--", *paths).stdout
    return out.decode("utf-8")


def find_verify_tag(repo: Path) -> tuple[str, str] | None:
    """(tag, commit) for the one round8-verify-sent-<date> tag, None when there is
    none; refuses when there are several or one is misnamed."""
    tags = [t for t in _git_text(repo, "tag", "--list", VERIFY_TAG_PREFIX + "*").splitlines()
            if t]
    if not tags:
        return None
    bad = [t for t in tags if not VERIFY_TAG_PATTERN.match(t)]
    if bad or len(tags) > 1:
        raise SystemExit(f"expected one tag {VERIFY_TAG_PREFIX}<YYYY-MM-DD>, found: "
                         f"{', '.join(tags)}. Nothing was sent.")
    return tags[0], _git_text(repo, "rev-list", "-n", "1", tags[0])


# --- the package ---------------------------------------------------------------------


def extract_rulings(decisions: str) -> str:
    """The excerpt of PHASE7_DECISIONS.md, unbroken: from the triage of 5 October
    to the line before the next top-level heading after the decision of 16 October."""
    def heading(prefix):
        hits = [m.start() for m in re.finditer(r"(?m)^" + re.escape(prefix), decisions)]
        if len(hits) != 1:
            raise SystemExit(f"PHASE7_DECISIONS.md has {len(hits)} headings starting "
                             f"{prefix!r}, not one. Nothing was sent.")
        return hits[0]
    first, last = heading(RULINGS_FIRST), heading(RULINGS_LAST)
    if last <= first:
        raise SystemExit("the decision of 16 October comes before the triage of "
                         "5 October in PHASE7_DECISIONS.md. Nothing was sent.")
    after = re.search(r"(?m)^## ", decisions[last + 3:])
    if after is None:
        raise SystemExit("nothing follows the decision of 16 October in "
                         "PHASE7_DECISIONS.md; the excerpt has no end. Nothing was sent.")
    return decisions[first:last + 3 + after.start()]


def engine_unchanged(repo: Path, a: str, b: str, excluded=None) -> bool:
    """Whether the engine's files are the same set, with the same bytes, at both."""
    excluded = _excluded_dir_names(repo) if excluded is None else excluded
    files_a = engine_files(repo, a, excluded)
    return files_a == engine_files(repo, b, excluded) and not diff(repo, a, b, files_a)


def build_package(repo: Path, commit: str, excluded=None, show=None) -> list[tuple[str, bytes]]:
    """[(name, bytes)] in the order sent, the instruction first. Every refusal
    comes before anything is sent. `show(repo, commit, path)` reads a file;
    git's blob unless a test stands in for the instruction, which is not
    committed yet when the suite runs before the commit that adds it."""
    excluded = _excluded_dir_names(repo) if excluded is None else excluded
    show = show or blob
    read_engine = engine_files(repo, READ_COMMIT, excluded)
    if not engine_unchanged(repo, READ_COMMIT, SENT_COMMIT, excluded):
        raise SystemExit("the engine's files differ between e186423, which round 8's "
                         "package was built from, and 217ede6, which it was sent from. "
                         "engine.diff would not show what the auditor read. Nothing was sent.")

    files = [(INSTRUCTION, show(repo, commit, INSTRUCTION))]
    for path, expected in ROUND8_REPORTS.items():
        raw = blob(repo, commit, path)
        if _sha256(raw) != expected:
            raise SystemExit(f"{path} at {commit[:7]} is not the report its run "
                             "recorded (SHA-256 differs). Nothing was sent.")
        files.append((path, raw))
    decisions = blob(repo, commit, DECISIONS).decode("utf-8")
    files.append((RULINGS_NAME, extract_rulings(decisions).encode("utf-8")))
    constitution = blob(repo, commit, CONSTITUTION).replace(b"\r\n", b"\n").replace(
        b"\n", b"\r\n")
    if _sha256(constitution) != CONSTITUTION_ROUND8_SHA256:
        raise SystemExit("the Constitution's audit copy is not the one round 8 read "
                         "(SHA-256 differs). Nothing was sent.")
    files.append((CONSTITUTION, constitution))

    now_engine = engine_files(repo, commit, excluded)
    files.append((ENGINE_DIFF_NAME, diff(repo, READ_COMMIT, commit,
                                         sorted(set(read_engine) | set(now_engine)))
                  .encode("utf-8")))
    files += [(p, blob(repo, commit, p)) for p in now_engine]

    read_tests = files_under_tests(repo, READ_COMMIT)
    now_tests = [p for p in files_under_tests(repo, commit) if p not in OWN_TESTS]
    files.append((TESTS_DIFF_NAME, diff(repo, READ_COMMIT, commit, read_tests)
                  .encode("utf-8")))
    files += [(p, blob(repo, commit, p)) for p in now_tests if p not in read_tests]
    for name, raw in files:
        try:
            raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise SystemExit(f"{name} is not valid UTF-8 ({exc}). Nothing was sent.")
    return files


def build_payload(files: list[tuple[str, bytes]]) -> str:
    (_, instruction), rest = files[0], files[1:]
    parts = [DELIVERY_NOTE.format(n=len(rest)), "\n", instruction.decode("utf-8"), "\n"]
    for name, raw in rest:
        parts.append(f"\n===== BEGIN FILE: {name} =====\n")
        parts.append(raw.decode("utf-8"))
        parts.append(f"\n===== END FILE: {name} =====\n")
    return "".join(parts)


def records(files: list[tuple[str, bytes]]) -> list[dict]:
    return [{"name": n, "bytes": len(b), "sha256": _sha256(b)} for n, b in files]


# --- requests ------------------------------------------------------------------------


def build_request_body(payload: str, model: str, allow_data_collection: bool = False,
                       max_tokens: int = MAX_OUTPUT_TOKENS) -> dict:
    if model not in MODEL_NAMES:
        raise SystemExit(f"{model!r} is not one of {MODEL_NAMES}. Nothing was sent.")
    return {
        "model": model,
        "messages": [{"role": "user", "content": payload}],
        "max_tokens": max_tokens,
        "stream": True,
        "stream_options": {"include_usage": True},
        "plugins": [{"id": "context-compression", "enabled": False}],
        "reasoning": dict(REASONING),
        "provider": {
            "only": [PROVIDER_SLUG],
            "allow_fallbacks": False,
            "require_parameters": True,
            "data_collection": "allow" if allow_data_collection else "deny",
        },
    }


def build_probe_body(model: str, allow_data_collection: bool = False) -> dict:
    return build_request_body(PROBE_PROMPT, model, allow_data_collection, PROBE_MAX_TOKENS)


# --- the token check -------------------------------------------------------------------


def check_send(tokenizer_dir, payload, models=None, counter_factory=None) -> dict:
    """The one request, counted with MiMo's own tokenizer and chat template.
    Raises SystemExit unless it fits with the full reserve for the reply."""
    spec = (models or token_check.MODELS)[TOKEN_CHECK_MODEL]
    if MAX_OUTPUT_TOKENS > spec.max_output_tokens:
        raise SystemExit("MAX_OUTPUT_TOKENS is above the model's maximum output.")
    factory = counter_factory or token_check.load_counter
    try:
        token_check.verify_tokenizer_dir(spec, tokenizer_dir)
        count = factory(spec, tokenizer_dir)
        result = token_check.check_fit([count(spec.render([payload]))], MAX_OUTPUT_TOKENS,
                                       spec.context_tokens)
        token_check.report(spec, ["the message"], [payload], [count(payload)], result,
                           out=sys.stdout)
    except token_check.CheckError as exc:
        raise SystemExit(f"CHECK NOT MADE: {exc}\nNothing was sent.")
    if not result.fits:
        raise SystemExit("The request does not fit. Nothing was sent.")
    return {"model": spec.name, "hf_revision": spec.hf_revision,
            "context": spec.context_tokens, "reserve": MAX_OUTPUT_TOKENS,
            "prompt_tokens": result.turns[0].prompt_tokens, "margin": result.margin}


# --- runs ------------------------------------------------------------------------------


def _holds_a_run(run_dir: Path) -> bool:
    report = run_dir / "report.md"
    return ((run_dir / "run_metadata.json").is_file()
            or (report.is_file() and report.stat().st_size > 0))


def recorded_runs(repo: Path) -> list[Path]:
    base = repo / "docs" / "audit_reports"
    if not base.is_dir():
        return []
    return sorted(d for d in base.glob(RUN_DIR_PREFIX + "*") if d.is_dir() and _holds_a_run(d))


def _committed_unchanged(repo: Path, paths: list[Path]) -> list[str]:
    problems = []
    for path in paths:
        rel = path.resolve().relative_to(repo.resolve()).as_posix()
        if _git(repo, "ls-files", "--error-unmatch", "--", rel, check=False).returncode:
            problems.append(f"{rel} is not committed")
        elif _git_text(repo, "status", "--porcelain", "--", rel):
            problems.append(f"{rel} has changed since it was committed, or is only added")
    return problems


def check_runs(repo: Path, payload_sha256: str, second_run: bool) -> list[Path]:
    """Refuses, sending nothing, unless this send may be a run: the first, or a
    second that the project filed a decision for after the first."""
    runs = recorded_runs(repo)
    if len(runs) >= MAX_RUNS:
        raise SystemExit(f"the fix verification has had its {MAX_RUNS} runs:"
                         + "".join(f"\n  {d.name}" for d in runs) + "\nNothing was sent.")
    if not runs:
        if second_run:
            raise SystemExit("--second-run, but no first run is on record. Nothing was sent.")
        return runs
    if not second_run:
        raise SystemExit(f"a run is on record ({runs[0].name}). A second run needs "
                         "--second-run, once the decision to send it is filed in "
                         "PHASE7_DECISIONS.md. Nothing was sent.")
    run1 = runs[0]
    problems = _committed_unchanged(repo, [run1 / "report.md", run1 / "reasoning.txt",
                                           run1 / "run_metadata.json"])
    try:
        recorded = json.loads((run1 / "run_metadata.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        recorded = {}
    if recorded.get("payload_sha256") != payload_sha256:
        problems.append(f"run 1 sent {recorded.get('payload_sha256')}; this message is "
                        f"{payload_sha256}. Both runs send the same message")
    if not problems:
        rel = (run1 / "report.md").resolve().relative_to(repo.resolve()).as_posix()
        first = _git_text(repo, "log", "--format=%H", "--diff-filter=A", "--", rel)
        first = first.splitlines()[-1] if first else ""
        filed = _git_text(repo, "rev-list", f"{first}..HEAD", "--", DECISIONS) if first else ""
        if not filed:
            problems.append("no commit to PHASE7_DECISIONS.md since the one that "
                            "committed run 1's report: the decision to send a second "
                            "run is filed before it is sent")
    if problems:
        raise SystemExit("Refusing the second run. Nothing was sent.\n  "
                         + "\n  ".join(problems))
    return runs


def next_run_dir(repo: Path) -> Path:
    number = len(recorded_runs(repo)) + 1
    stamp = _utc_now().strftime("%Y-%m-%d")
    name = RUN_DIR_PREFIX + (stamp if number == 1 else f"run{number}_{stamp}")
    run_dir = repo / "docs" / "audit_reports" / name
    if _holds_a_run(run_dir):
        raise SystemExit(f"{run_dir} already holds a reply. Nothing was sent.")
    return run_dir


# --- the network -----------------------------------------------------------------------


def reasoning_tokens(usage) -> int | None:
    details = (usage or {}).get("completion_tokens_details") or {}
    value = details.get("reasoning_tokens")
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def read_stream(lines) -> dict:
    got = {"generation_id": None, "finish_reason": None, "usage": None,
           "content": "", "reasoning": ""}
    for raw_line in lines:
        if not raw_line or not raw_line.startswith("data: "):
            continue
        data = raw_line[6:].strip()
        if data == "[DONE]":
            break
        try:
            event = json.loads(data)
        except json.JSONDecodeError:
            continue
        got["generation_id"] = event.get("id") or got["generation_id"]
        if event.get("usage"):
            got["usage"] = event["usage"]
        for choice in event.get("choices") or []:
            delta = choice.get("delta") or {}
            got["content"] += delta.get("content") or ""
            got["reasoning"] += delta.get("reasoning") or ""
            if choice.get("finish_reason"):
                got["finish_reason"] = choice["finish_reason"]
    return got


def fetch_generation(api_key: str, gen_id: str, sleep=time.sleep, get=None) -> dict | None:
    """OpenRouter's record of a call: the model and provider that served it."""
    if get is None:
        import requests  # pinned at 2.32.5 in requirements.txt
        get = requests.get
    for attempt, wait in enumerate(GENERATION_LOOKUP_WAITS, 1):
        sleep(wait)
        try:
            resp = get(GENERATION_URL, params={"id": gen_id},
                       headers={"Authorization": f"Bearer {api_key}"}, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("data", data)
        except Exception:  # noqa: BLE001 - the record is checked, its absence refused
            pass
        print(f"  generation record not available yet (try {attempt} of "
              f"{len(GENERATION_LOOKUP_WAITS)})", flush=True)
    return None


def probe(body: dict, api_key: str) -> dict:
    """Sends the probe and reports what came back, its generation record
    included. Decides nothing: probe_and_choose() does."""
    import requests  # pinned at 2.32.5 in requirements.txt

    print(f"POST {API_URL}  probe  model={body['model']}  provider={PROVIDER_SLUG}", flush=True)
    resp = requests.post(API_URL, headers={"Authorization": f"Bearer {api_key}",
                                           "Content-Type": "application/json"},
                         json=body, stream=True, timeout=(30, 300))
    resp.encoding = "utf-8"
    if resp.status_code != 200:
        return {"model_requested": body["model"], "http_status": resp.status_code,
                "error": resp.text[:2000]}
    got = read_stream(resp.iter_lines(decode_unicode=True))
    record = fetch_generation(api_key, got["generation_id"]) if got["generation_id"] else None
    return {"model_requested": body["model"], "http_status": 200,
            "generation_id": got["generation_id"], "finish_reason": got["finish_reason"],
            "usage": got["usage"], "answer": got["content"][:200],
            "reasoning_tokens": reasoning_tokens(got["usage"]),
            "model_reported": (record or {}).get("model"),
            "provider_reported": (record or {}).get("provider_name")}


def probe_and_choose(api_key: str, probe_fn, allow_data_collection: bool,
                     different_checkpoint: str | None) -> tuple[str, list[dict], str]:
    """Probes the dated name, then the undated one if the dated was refused.
    Returns (the model name to send with, every probe's record, the checkpoint
    the accepted probe was served by). Refuses unless that probe reasoned,
    came from Xiaomi, and was served by ROUND8_CHECKPOINT -- or by the
    checkpoint --different-checkpoint names."""
    probes = []
    for name in MODEL_NAMES:
        result = probe_fn(build_probe_body(name, allow_data_collection), api_key)
        probes.append(result)
        print(f"probe {name}: HTTP {result.get('http_status')}")
        if result.get("http_status") == 200:
            break
    else:
        raise SystemExit("Refusing to send: OpenRouter accepted neither model name for "
                         "the probe. Only the probes were sent.")
    accepted = probes[-1]
    served = accepted.get("model_reported") or "unrecorded"
    problems = []
    if not (accepted.get("reasoning_tokens") or 0) > 0:
        problems.append("the probe shows no reasoning")
    if accepted.get("provider_reported") != PROVIDER_NAME:
        problems.append(f"the probe was served by {accepted.get('provider_reported')!r}, "
                        f"not {PROVIDER_NAME!r}")
    if served != ROUND8_CHECKPOINT and served != different_checkpoint:
        problems.append(f"the probe was served by {served!r}, not round 8's "
                        f"{ROUND8_CHECKPOINT!r}. To send to it anyway, as a different "
                        f"checkpoint's result: --different-checkpoint {served}")
    if problems:
        raise SystemExit("Refusing to send. Only the probe was sent.\n  "
                         + "\n  ".join(problems))
    return accepted["model_requested"], probes, served


def send(body: dict, api_key: str, run_dir: Path, metadata: dict, post=None,
         fetch=None) -> int:
    """Streams the reply to disk as it arrives. `post` and `fetch` stand in for
    requests.post and fetch_generation in the tests; the network is never
    reached there."""
    if post is None:
        import requests  # pinned at 2.32.5 in requirements.txt
        post = requests.post
    fetch = fetch or fetch_generation
    run_dir.mkdir(parents=True, exist_ok=True)
    report_path = run_dir / "report.md"
    reasoning_path = run_dir / "reasoning.txt"
    started = _utc_now()
    print(f"POST {API_URL}  model={body['model']}  provider={PROVIDER_SLUG}  "
          f"max_tokens={body['max_tokens']}", flush=True)
    resp = post(API_URL, headers={"Authorization": f"Bearer {api_key}",
                                  "Content-Type": "application/json"},
                json=body, stream=True, timeout=(30, 900))
    # OpenRouter names no charset; without this, requests decodes as Latin-1,
    # which corrupted round 6's report.
    resp.encoding = "utf-8"
    if resp.status_code != 200:
        (run_dir / "http_error.txt").write_text(f"HTTP {resp.status_code}\n\n"
                                                f"{resp.text[:8000]}\n", encoding="utf-8")
        print(f"\nHTTP {resp.status_code}. Body saved to {run_dir / 'http_error.txt'}. "
              "No reply, so not a run.", file=sys.stderr)
        return 2

    gen_id = finish_reason = usage = None
    content_chars = reasoning_chars = 0
    last_report = time.time()
    with open(report_path, "w", encoding="utf-8", newline="") as report_f, \
         open(reasoning_path, "w", encoding="utf-8", newline="") as reasoning_f:
        for raw_line in resp.iter_lines(decode_unicode=True):
            if not raw_line or not raw_line.startswith("data: "):
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
                if delta.get("content"):
                    report_f.write(delta["content"])
                    report_f.flush()
                    content_chars += len(delta["content"])
                if delta.get("reasoning"):
                    reasoning_f.write(delta["reasoning"])
                    reasoning_f.flush()
                    reasoning_chars += len(delta["reasoning"])
                if choice.get("finish_reason"):
                    finish_reason = choice["finish_reason"]
            if time.time() - last_report >= 30:
                elapsed = int((_utc_now() - started).total_seconds())
                print(f"  {elapsed:>5}s  reasoning {reasoning_chars:>9,} chars  "
                      f"report {content_chars:>9,} chars", flush=True)
                last_report = time.time()

    finished = _utc_now()
    metadata.update({
        "started_utc": started.isoformat(), "finished_utc": finished.isoformat(),
        "elapsed_seconds": round((finished - started).total_seconds(), 1),
        "generation_id": gen_id, "finish_reason": finish_reason, "usage": usage,
        "report_chars": content_chars, "reasoning_chars": reasoning_chars,
        "report_sha256": _sha256(report_path.read_bytes()),
        "reasoning_sha256": _sha256(reasoning_path.read_bytes()),
    })
    record = fetch(api_key, gen_id) if gen_id else None
    if record:
        (run_dir / "generation.json").write_text(json.dumps(record, indent=2),
                                                 encoding="utf-8")
        metadata.update({"provider_reported": record.get("provider_name"),
                         "model_reported": record.get("model"),
                         "native_tokens_prompt": record.get("native_tokens_prompt"),
                         "native_tokens_completion": record.get("native_tokens_completion"),
                         "total_cost_usd": record.get("total_cost")})
    (run_dir / "run_metadata.json").write_text(json.dumps(metadata, indent=2),
                                               encoding="utf-8")

    print(f"\nfinish_reason        {finish_reason}")
    print(f"model reported       {metadata.get('model_reported', 'unavailable')}")
    print(f"provider reported    {metadata.get('provider_reported', 'unavailable')}")
    print(f"prompt tokens        provider {metadata.get('native_tokens_prompt', 'unavailable')}; "
          f"token check {metadata['token_check']['prompt_tokens']:,}")
    print(f"cost                 {metadata.get('total_cost_usd', 'unavailable')}")
    print(f"report               {report_path}  ({content_chars:,} chars)")
    problems = []
    if finish_reason != "stop":
        problems.append(f"finish_reason={finish_reason!r}: the report may be cut off. "
                        "It is still a run.")
    if metadata.get("provider_reported") != PROVIDER_NAME:
        problems.append(f"served by {metadata.get('provider_reported')!r}, not "
                        f"{PROVIDER_NAME!r}.")
    if metadata.get("model_reported") != metadata.get("checkpoint_accepted"):
        problems.append(f"the send was served by {metadata.get('model_reported')!r}; the "
                        f"probe by {metadata.get('checkpoint_accepted')!r}.")
    if content_chars == 0:
        problems.append("no report content was returned.")
    for problem in problems:
        print(f"\nWARNING: {problem}", file=sys.stderr)
    if not problems:
        print("\nNext: read the report, then commit the run's files by name.")
    return 1 if problems else 0


# --- main --------------------------------------------------------------------------------


def main(argv=None, repo_root: Path | None = None, models=None, counter_factory=None,
         send_fn=None, probe_fn=None) -> int:
    repo = repo_root or Path(__file__).resolve().parents[2]
    send_fn = send_fn or send
    probe_fn = probe_fn or probe

    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--tokenizer-dir", type=Path, default=None,
                        help="MiMo's pinned tokenizer files; required to send")
    parser.add_argument("--send", action="store_true",
                        help="send; without it this is a dry run")
    parser.add_argument("--second-run", action="store_true",
                        help="with --send: the second run, once its decision is filed")
    parser.add_argument("--different-checkpoint", default=None, metavar="NAME",
                        help="with --send: send although the probe was served by NAME, "
                             "not round 8's checkpoint")
    parser.add_argument("--allow-data-collection", action="store_true",
                        help="permit providers that may train on the prompt (default: deny)")
    args = parser.parse_args(argv)

    if MAX_OUTPUT_TOKENS <= LARGEST_PRIOR_RESPONSE:
        raise SystemExit("MAX_OUTPUT_TOKENS is not above the largest prior response.")

    tag = find_verify_tag(repo)
    if tag is None:
        if args.send:
            raise SystemExit(f"no tag {VERIFY_TAG_PREFIX}<date>: the commit sent is "
                             "tagged before the send. Nothing was sent.")
        commit = _git_text(repo, "rev-parse", "HEAD")
        print(f"commit         {commit}  (HEAD; not tagged yet, so --send refuses)")
    else:
        commit = tag[1]
        print(f"commit         {commit}  ({tag[0]})")
    files = build_package(repo, commit)
    payload = build_payload(files)
    raw = payload.encode("utf-8")
    payload_sha256 = _sha256(raw)
    print(f"files          {len(files)} (the instruction and {len(files) - 1} after it)")
    print(f"payload        {len(raw):,} bytes, sha256 {payload_sha256}")
    print(f"model          {' or '.join(MODEL_NAMES)}, {PROVIDER_SLUG} only, fallbacks "
          f"off, data_collection {'allow' if args.allow_data_collection else 'deny'}")

    counted = None
    if args.tokenizer_dir is not None:
        counted = check_send(args.tokenizer_dir, payload, models, counter_factory)
        upper = counted["prompt_tokens"] * PRICE_IN + MAX_OUTPUT_TOKENS * PRICE_OUT
        print(f"cost, at most  ${upper:.2f} (prices of 4 October 2026, not re-checked)")
    else:
        print("token check    not made: pass --tokenizer-dir. --send refuses without it.")
    runs = recorded_runs(repo)
    print(f"runs on record {len(runs)} of {MAX_RUNS}" + "".join(f"\n  {d.name}" for d in runs))
    if not args.send:
        if args.second_run or args.different_checkpoint:
            raise SystemExit("--second-run and --different-checkpoint are for --send.")
        print("\nDry run. Nothing was sent.")
        return 0
    if counted is None:
        raise SystemExit("--send needs --tokenizer-dir: the request is measured before "
                         "it is sent. Nothing was sent.")
    check_runs(repo, payload_sha256, args.second_run)
    run_dir = next_run_dir(repo)

    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("OPENROUTER_API_KEY is not set in this shell.\n"
                         "    set OPENROUTER_API_KEY=sk-or-...\n"
                         "then run this command again in the same window.")
    model, probes, served = probe_and_choose(api_key, probe_fn, args.allow_data_collection,
                                             args.different_checkpoint)
    metadata = {
        "model_requested": model, "checkpoint_accepted": served,
        "round8_checkpoint": ROUND8_CHECKPOINT,
        "different_checkpoint": served != ROUND8_CHECKPOINT,
        "provider_pinned": PROVIDER_SLUG, "max_output_tokens": MAX_OUTPUT_TOKENS,
        "commit": commit, "tag": tag[0], "files": records(files),
        "payload_sha256": payload_sha256, "payload_bytes": len(raw),
        "data_collection": "allow" if args.allow_data_collection else "deny",
        "reasoning_requested": dict(REASONING), "reasoning_probes": probes,
        "token_check": counted, "run": len(runs) + 1,
    }
    return send_fn(build_request_body(payload, model, args.allow_data_collection),
                   api_key, run_dir, metadata)


if __name__ == "__main__":
    sys.exit(main())
