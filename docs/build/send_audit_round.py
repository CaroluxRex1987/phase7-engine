#!/usr/bin/env python3
"""Send a built audit package to a named reviewer model through the OpenRouter API.

Written for round 4 (Kimi K3), repointed for round 5 (GPT-6 Astra) on 12 September
2026 after Viktor's OpenRouter billing-export check cleared OpenAI: GPT-5.6 Luna
Pro's hostile-Constitution-review and Step-8 sessions both show variant=standard
with no training routing, so under the project's own rule -- session exposure ends
with the session, training and lineage exposure never does -- that lab-level
exposure does not carry to Astra. Repointed again for round 6 (Meta Muse Spark
1.3) on 13 September 2026. Viktor's original ruling that day named
meta/muse-spark-1.2; checking OpenRouter's live models API before building this
round -- not done before that ruling -- found 1.2 no longer listed as an
invokable endpoint, only meta/muse-spark-1.3, meta/muse-spark-1.3-contributor,
and meta/muse-spark-1.2-contributor. Both -contributor tiers are excluded on
sight, regardless of price: their own pages state prompts and outputs may be
used to improve Meta's products, and this project's source is not going to a
tier with that policy. 1.3 is the live, same-price, same-context successor,
and it is also the first reviewer in this project's history from a lab with no
prior exposure to any part of it -- no billing-export check was needed the way
one was for Astra, because there is nothing on the ledger for Meta to clear.

Repointed for round 7 (Laguna S 2.1, pinned to Poolside) on 29 September 2026 --
PHASE7_DECISIONS.md, "Ruling, 29 September 2026 -- the independent audit: now, by
Laguna S 2.1, the full package in one session" -- and changed from one request to
two, per "what the auditor sees, and no planted bugs" the same day: Parts 1-6 are
graded on the first message alone, and the Part 7 material goes in a second
request.

Six failures in this project's audit history are what this script exists to
make impossible (until 29 September this line said three and listed four; it
said five until 30 September):

  * a run that went to whatever the Auto Router picked (round 3, GLM 5.3 Flash) --
    here the model AND the serving provider are pinned, with fallbacks off, so a
    substitution is an error rather than a silently different reviewer;
  * a run that died at a 16,384-token output ceiling with finish_reason=length,
    burning the full input charge -- here MAX_OUTPUT_TOKENS is explicit, is
    asserted to exceed the largest response this project has ever received,
    and the finish reason is recorded;
  * a run whose output existed only in a chat window -- here every token is
    streamed to disk as it arrives, under docs/audit_reports/, which is tracked;
  * a report silently corrupted by a wrong text-encoding assumption (round 6,
    Meta Muse Spark 1.3) -- requests falls back to Latin-1 for a response whose
    Content-Type carries no charset, so every non-ASCII character streamed back
    got decoded wrong and re-written to disk as mangled UTF-8; caught after the
    fact and repaired byte-for-byte (see
    docs/audit_reports/round6_muse-spark-1.3_2026-09-13/ENCODING_CORRECTION.md).
    Here resp.encoding is forced to "utf-8" immediately after the request
    returns, before anything reads resp.text or iterates the stream;
  * a Part 7 file the reviewer could read before writing Parts 1-6 (rounds 5
    and 6) -- commit_messages_PART7_ONLY.md travelled in the same single message
    as Parts 1-6, held back only by a request in its own header. Checked on
    29 September 2026: both rounds' requests, rebuilt from the package files
    with this script as it stood at each send (`4d99cdb`, `84e5e8f`), hash to
    the payload_sha256 in their run_metadata.json, and each is one message
    with that file inside it. Here the Part 7 material is a second request,
    and --send-part7 refuses to make it until the first reply finished
    normally, came from the pinned provider, and is committed in git -- so
    what Parts 1-6 said before Part 7 existed is on record, not asserted;
  * a run whose request never asked for reasoning (round 7, run 1, Laguna S
    2.1, 30 September 2026) -- 0 reasoning tokens in Poolside's own record,
    52 seconds on 455,360 prompt tokens, every rule rated Compliant and none
    of the four test bugs found. Here every request asks for reasoning, and
    --send refuses the real send until a one-line probe has shown that the
    endpoint reasons when asked (ROUND 7'S SECOND RUN, below).

And one check that is not a past failure but was ruled before the send
(PHASE7_DECISIONS.md, "Ruling, 26 September 2026 -- the pre-send token check
is audit preparation, not an engine item"): each send is measured first with
the auditor's own tokenizer (package_token_check.py, pinned by SHA-256) and
refused before any network call when it does not fit. The first send is
measured against the whole conversation it starts, with the first reply
counted at the full reserve, so a run is not paid for whose Part 7 could not
follow. The second is measured exactly, with the first reply as written.

TWO COMMANDS, AND A COMMIT BETWEEN THEM

Nothing is sent without --send or --send-part7. Without either the script
assembles both messages, hashes them, runs the token check when given the
tokenizer folder, prints the sizes, the cost and the runs on record, and
stops. The probe is part of --send, not of the dry run.

    --send        sends the first message (the instruction and Parts 1-6's
                  material) and writes the reply as turn1_* under
                  docs/audit_reports/round7_laguna-s-2.1_<date>/ for run 1,
                  and round7_laguna-s-2.1_run<N>_<date>/ for run N after it.
                  Refused once the round has had MAX_RUNS runs, when the
                  first message is not the bytes every earlier run sent, and
                  when the reasoning probe shows no reasoning.
    --send-part7  sends the second request: the first message again, the
                  first reply as written, and the Part 7 material. Refused
                  unless turn1_report.md, turn1_reasoning.txt and
                  turn1_run_metadata.json are committed and unchanged, the
                  reply finished with finish_reason=stop, the provider
                  reported was the pinned one, the report is not empty, the
                  first message rebuilds to the same bytes it was sent as,
                  and the run is not closed (CLOSED_RUNS). The reply is
                  written as turn2_*.

The commit between them is Claude's design under Viktor's delegation of
21 September (items 3 and 4 of the preparation list); Viktor did not object
when it was put to him on 29 September. It makes "Parts 1-6 are saved" a
fact git records with a time, which is what "nothing found after Part 7
counts" (the test-bug scoring rule, ruling of 29 September on six questions
before the send) needs to be checkable.

THE FIRST REPLY'S REASONING GOES BACK WITH IT

Ruled 29 September 2026, by agreeing to Claude's suggestion. Laguna's chat
template at e80da38 shows an earlier reply's reasoning in full when the
request carries it and an empty <think></think> when it does not; OpenRouter
accepts it back as a `reasoning` string on the assistant message (its
reasoning-tokens guide, read 29 September). Whether Poolside's endpoint passes
it through to the template was not checked before the send. The token check
counts the second request both ways and records both, and the provider's own
count afterwards (native_tokens_prompt) says which one it saw.

ROUND 7'S SECOND RUN

Ruled 30 September 2026, by agreeing to Claude's suggestion
(PHASE7_DECISIONS.md, "Ruling, 30 September 2026 -- what follows round 7's
first reply"). Run 1's reply had no reasoning -- 0 reasoning tokens in the
provider's own record -- and found none of the four test bugs; its request
had not asked for reasoning. The ruling: no Part 7 to run 1; run 2 with
reasoning requested and nothing else changed; run 1 counts as a run; two
runs in all. The design below is Claude's under the delegation of
21 September, put to Viktor before it was built:

  * every request asks for reasoning (REASONING), and --send first sends a
    one-line probe with the same pins (build_probe_body) and refuses the
    real send unless the probe's usage reports reasoning tokens above zero.
    The probe carries nothing from the package;
  * a round has at most MAX_RUNS runs. A run is any send that left a reply
    on record -- a folder holding turn1_run_metadata.json or a non-empty
    turn1_report.md -- whatever its finish reason, a reply cut off at the
    output ceiling included (Viktor's answer, the same day). A send that
    failed before any reply came back is not a run;
  * every run sends the same first message: --send refuses unless the
    payload hashes to the payload_sha256 each earlier run recorded;
  * each run writes to a folder of its own, and --send never writes into a
    folder that holds a reply. --force and --out-dir are refused with
    --send; both remain for --send-part7;
  * run 1 is closed (CLOSED_RUNS): --send-part7 never continues it. Run 2
    was closed the same day, once it had scored 0 of 4 and Viktor had
    checked the score: with two runs under half, round 7 ended, and Part 7
    goes to neither run (the same ruling, point 4);
  * the generation lookup waits about five minutes in all
    (GENERATION_LOOKUP_WAITS), not about 44 seconds: run 1's lookup ran out
    of tries, which is why its turn1_run_metadata.json names no provider.
    Why the record was late was not found.

Usage (from the repository root):

    set OPENROUTER_API_KEY=sk-or-...
    python docs/build/send_audit_round.py --tokenizer-dir <folder>
    python docs/build/send_audit_round.py --tokenizer-dir <folder> --send
    python docs/build/send_audit_round.py --tokenizer-dir <folder> --send-part7
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import time
from pathlib import Path

API_URL = "https://openrouter.ai/api/v1/chat/completions"
GENERATION_URL = "https://openrouter.ai/api/v1/generation"

MODEL = "poolside/laguna-s-2.1"
PROVIDER_SLUG = "poolside"
PROVIDER_DISPLAY_NAME = "Poolside"
# The entry in package_token_check.MODELS that is this model: its tokenizer,
# its chat template, its context and its maximum output.
TOKEN_CHECK_MODEL = "laguna-s-2.1"

# Read by Claude on 29 September 2026 from OpenRouter's endpoints API for
# poolside/laguna-s-2.1 (fetched with a web tool, not by this script): one
# endpoint, provider "Poolside", tag poolside/fp4 (fp4 quantization), context
# 1,048,576, max completion 131,072, $0.09 / $0.18 per million input / output
# tokens, supported parameters reasoning, include_reasoning, tools,
# tool_choice, temperature, max_tokens. The same figures as the model page
# read the same day (PHASE7_DECISIONS.md, "six questions before the send").
# The live query at the send is still owed (preparation list, item 1).
#
# Poolside's provider page on OpenRouter, read the same day, says inputs and
# outputs from FREE use of Laguna S 2.1 may be used for training, and says
# nothing about paid use. data_collection stays "deny" below; if OpenRouter
# classes the endpoint as one that may train, the send is refused with a 404
# (see send()). That is a decision to make then, not a flag to flip.
#
# MAX_OUTPUT_TOKENS is the endpoint's whole ceiling, and it is the token
# check's reserve for every reply. Round 6 set 100,000 under a 943,718 ceiling;
# here the ceiling is the model's own 131,072, and the check measured on
# 29 September that a trial package fits with both replies at this size
# (PHASE7_NEXT.md, the twenty-fourth session). Reasoning counts against it on
# most providers (OpenRouter's reasoning-tokens guide), so it bounds a reply's
# thinking and its answer together; that is not confirmed for Poolside. Run 1
# (30 September) asked for no reasoning and got none, so it says nothing either
# way. If a reply's reasoning and answer together exceed the reserve, the
# second request is still measured exactly before it is sent
# (check_part7_send) and refused if it does not fit.
MAX_OUTPUT_TOKENS = 131_072
# Kimi K3, round 4, 5 September 2026: 41,861 completion tokens, finish_reason
# stop (docs/audit_reports/round4_kimi-k3_2026-09-05/run_metadata.json).
# Until 29 September this said 36,085 (Kimi K3's run of 2 September), which
# round 4 had already exceeded; the assertion held either way.
LARGEST_PRIOR_RESPONSE = 41_861

# USD per token, from the same endpoints query. The endpoint also carries
# "discount": 0.1, whose meaning was not checked; the estimate ignores it.
PRICE_IN = 0.09 / 1_000_000
PRICE_OUT = 0.18 / 1_000_000

# The first message: the instruction first, then the files it goes with. The
# set is asserted exactly: an extra or missing file aborts the run, because
# several rounds' directories carry the same filenames.
#
# rev8 is round 7's instruction (preparation list, item 9 -- not yet written
# when this was repointed; the build refuses until it exists). Revs 1-7 stay in
# docs/audit_package/ unedited, per the document's own preservation rule.
INSTRUCTION_FILE = "item16_review_instruction_rev8.md"
MESSAGE1_ATTACHMENTS = [
    "Phase7_Constitution_v1.0_RATIFIED_AUDITCOPY.txt",
    "phase7_engine_source.md",
    "phase7_test_suite.md",
    "MANIFEST.md",
    "version_control_history.md",
    "execution_transcripts.md",
]
MESSAGE1_FILES = [INSTRUCTION_FILE] + MESSAGE1_ATTACHMENTS

# The second message: the Part 7 material (ruling of 29 September, "what the
# auditor sees"). part7_material_PART7_ONLY.md is written by hand -- the
# bias_score findings, the list for after the audit, and the points of the
# 15 September PDF still live -- and commit_messages_PART7_ONLY.md is built,
# cut to the commits since e65a0f7.
MESSAGE2_FILES = [
    "part7_material_PART7_ONLY.md",
    "commit_messages_PART7_ONLY.md",
]

DELIVERY_NOTE_1 = (
    "The review instruction follows in full, and after it the {n} files that go "
    "with it, each delimited by a BEGIN FILE / END FILE marker carrying the "
    "file's name. The files are supplied as text in a single message because "
    "this is an API call and not a chat interface; their bytes are unmodified.\n"
)
DELIVERY_NOTE_2 = (
    "Your previous reply -- Parts 1-6 of your report -- has been saved and "
    "committed, and will not be changed. The {n} files below are the material "
    "for Part 7, as your instruction describes it, each delimited by a BEGIN "
    "FILE / END FILE marker carrying the file's name. Their bytes are "
    "unmodified.\n"
)

RUN_DIR_PREFIX = "round7_laguna-s-2.1_"
TURN1 = "turn1_"
TURN2 = "turn2_"

# ROUND 7'S SECOND RUN (the docstring). Two runs in all, run 1 included.
MAX_RUNS = 2
# Run folders --send-part7 never continues, each with the reason it gives.
CLOSED_RUNS = {
    "round7_laguna-s-2.1_2026-09-30": (
        "run 1 (30 September 2026) is closed: Part 7 does not go to it "
        "(PHASE7_DECISIONS.md, \"Ruling, 30 September 2026 -- what follows round "
        "7's first reply\", point 1)"),
    "round7_laguna-s-2.1_run2_2026-09-30": (
        "run 2 (30 September 2026) is closed: it found 0 of the 4 test bugs, so "
        "round 7 has ended and Part 7 does not go to it (PHASE7_DECISIONS.md, "
        "\"Round 7 ended, 30 September 2026 -- run 2 found 0 of 4\")"),
}
# OpenRouter's unified reasoning parameter. `enabled` asks for the model's own
# default; no effort level is named, because nothing read says how Poolside's
# endpoint maps one.
REASONING = {"enabled": True}
# The probe: a question with nothing from the package in it, and a small
# ceiling. At $0.18 per million output tokens, 4,096 cost under a tenth of a
# cent. A reply cut off at the ceiling still shows whether reasoning happened.
PROBE_PROMPT = "What is 17 multiplied by 24? Reply with the number only."
PROBE_MAX_TOKENS = 4_096
# Seconds to wait before each try of the generation lookup: about five
# minutes in all. Until 30 September it was eight tries after 2-9 seconds
# each, about 44 seconds, and run 1's lookup ran out inside it.
GENERATION_LOOKUP_WAITS = (5,) * 6 + (15,) * 6 + (30,) * 6


def _load_token_check():
    path = Path(__file__).with_name("package_token_check.py")
    spec = importlib.util.spec_from_file_location("phase7_send_token_check", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


token_check = _load_token_check()


def _utc_now() -> _dt.datetime:
    return _dt.datetime.now(_dt.timezone.utc)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read_set(directory: Path, expected: list[str], what: str) -> tuple[list[dict], dict]:
    if not directory.is_dir():
        raise SystemExit(f"{what} directory not found: {directory}")
    found = sorted(p.name for p in directory.iterdir() if p.is_file())
    if found != sorted(expected):
        missing = [n for n in expected if n not in found]
        extra = [n for n in found if n not in expected]
        raise SystemExit(
            f"{what} contents do not match what this script sends.\n"
            f"  directory: {directory}\n"
            f"  missing:   {missing or 'none'}\n"
            f"  unexpected:{extra or 'none'}\n"
            "Refusing to send a package that is not the one this script describes."
        )
    records: list[dict] = []
    texts: dict[str, str] = {}
    for name in expected:
        raw = (directory / name).read_bytes()
        try:
            texts[name] = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise SystemExit(f"{name} is not valid UTF-8: {exc}")
        records.append({"name": name, "bytes": len(raw), "sha256": _sha256(raw)})
    return records, texts


def read_package(package_dir: Path) -> tuple[list[dict], dict]:
    """The first message's files, verified. Returns (file records, {name: text})."""
    return _read_set(package_dir, MESSAGE1_FILES, "first message")


def read_part7(part7_dir: Path) -> tuple[list[dict], dict]:
    """The second message's files, verified the same way."""
    return _read_set(part7_dir, MESSAGE2_FILES, "second message (Part 7)")


def _attach(parts: list[str], texts: dict, names: list[str]) -> None:
    for name in names:
        parts.append(f"\n===== BEGIN FILE: {name} =====\n")
        parts.append(texts[name])
        parts.append(f"\n===== END FILE: {name} =====\n")


def build_payload(texts: dict[str, str]) -> str:
    parts = [DELIVERY_NOTE_1.format(n=len(MESSAGE1_ATTACHMENTS)), "\n",
             texts[INSTRUCTION_FILE], "\n"]
    _attach(parts, texts, MESSAGE1_ATTACHMENTS)
    return "".join(parts)


def build_part7_payload(texts: dict[str, str]) -> str:
    parts = [DELIVERY_NOTE_2.format(n=len(MESSAGE2_FILES))]
    _attach(parts, texts, MESSAGE2_FILES)
    return "".join(parts)


def _request(messages: list[dict], allow_data_collection: bool) -> dict:
    return {
        "model": MODEL,
        "messages": messages,
        "max_tokens": MAX_OUTPUT_TOKENS,
        "stream": True,
        "stream_options": {"include_usage": True},
        # OpenRouter cuts the middle out of a prompt too long for the model
        # when context compression is on. It is on by default only for
        # endpoints of 8,192 tokens or less, so not for this one; it is pinned
        # off anyway, so that a prompt that does not fit is refused rather than
        # quietly shortened (OpenRouter's context-compression page, read
        # 29 September 2026; the older name for this was `transforms`).
        "plugins": [{"id": "context-compression", "enabled": False}],
        # Ruled 30 September 2026: run 1 did not ask for reasoning and got none
        # (0 reasoning tokens in Poolside's own record). OpenRouter's endpoint
        # listing for Laguna S 2.1 names `reasoning` among its supported
        # parameters (read 29 September, and again on 30 September through a
        # web tool). Whether the endpoint acts on it is what the probe checks.
        "reasoning": dict(REASONING),
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


def build_request_body(payload: str, allow_data_collection: bool) -> dict:
    """The first request: the first message alone."""
    return _request([{"role": "user", "content": payload}], allow_data_collection)


def build_part7_request_body(payload: str, reply_reasoning: str, reply_answer: str,
                             part7_payload: str, allow_data_collection: bool) -> dict:
    """The second request: the first message again, the first reply as it was
    written -- its answer and its reasoning -- and the Part 7 material."""
    return _request(
        [
            {"role": "user", "content": payload},
            {"role": "assistant", "content": reply_answer, "reasoning": reply_reasoning},
            {"role": "user", "content": part7_payload},
        ],
        allow_data_collection,
    )


def build_probe_body(allow_data_collection: bool) -> dict:
    """The reasoning probe: one short question, with the same model, pins and
    reasoning request as a real send, and a small output ceiling."""
    body = _request([{"role": "user", "content": PROBE_PROMPT}], allow_data_collection)
    body["max_tokens"] = PROBE_MAX_TOKENS
    return body


# --- the token check ---------------------------------------------------------


def _token_spec(models):
    spec = (models or token_check.MODELS)[TOKEN_CHECK_MODEL]
    if MAX_OUTPUT_TOKENS > spec.max_output_tokens:
        raise SystemExit(
            f"MAX_OUTPUT_TOKENS ({MAX_OUTPUT_TOKENS:,}) is above {spec.name}'s maximum "
            f"output ({spec.max_output_tokens:,}); the reserve the check keeps would "
            "not bound the reply.")
    return spec


def check_first_send(tokenizer_dir, payload, part7_payload, models=None,
                     counter_factory=None) -> dict:
    """The whole conversation the first send starts, worst case: the first
    request, and the second with the first reply at the full reserve. Raises
    SystemExit unless both fit; returns the counts for the record."""
    spec = _token_spec(models)
    factory = counter_factory or token_check.load_counter
    try:
        token_check.verify_tokenizer_dir(spec, tokenizer_dir)
        count = factory(spec, tokenizer_dir)
        texts = [payload, part7_payload]
        rendered = [count(spec.render(texts[:1])), count(spec.render(texts))]
        result = token_check.check_fit(rendered, MAX_OUTPUT_TOKENS, spec.context_tokens)
        token_check.report(spec, ["first message", "second message"], texts,
                           [count(t) for t in texts], result, out=sys.stdout)
    except token_check.CheckError as exc:
        raise SystemExit(f"CHECK NOT MADE: {exc}\nNothing was sent.")
    if not result.fits:
        raise SystemExit("The conversation does not fit. Nothing was sent.")
    return {
        "model": spec.name,
        "hf_revision": spec.hf_revision,
        "context": spec.context_tokens,
        "reserve": MAX_OUTPUT_TOKENS,
        "request1_prompt_tokens": result.turns[0].prompt_tokens,
        "request2_prompt_tokens_worst_case": result.turns[1].prompt_tokens,
        "worst_case_margin": result.margin,
    }


def check_part7_send(tokenizer_dir, payload, reply_reasoning, reply_answer,
                     part7_payload, models=None, counter_factory=None) -> dict:
    """The second request, counted exactly with the first reply as written.
    Counted both with its reasoning (what is sent) and without (for comparison
    with the provider's own count afterwards). Raises SystemExit unless the
    request as sent fits."""
    spec = _token_spec(models)
    factory = counter_factory or token_check.load_counter
    texts = [payload, part7_payload]
    try:
        token_check.verify_tokenizer_dir(spec, tokenizer_dir)
        count = factory(spec, tokenizer_dir)
        with_reasoning = count(spec.render(texts, replies=[(reply_reasoning, reply_answer)]))
        answer_only = count(spec.render(texts, replies=[("", reply_answer)]))
        result = token_check.check_known(with_reasoning, 2, MAX_OUTPUT_TOKENS,
                                         spec.context_tokens)
    except token_check.CheckError as exc:
        raise SystemExit(f"CHECK NOT MADE: {exc}\nNothing was sent.")
    turn = result.turns[0]
    print(f"model          {spec.name}  ({spec.hf_repo} @ {spec.hf_revision[:7]})")
    print(f"request 2      {with_reasoning:>11,} tokens with the first reply's reasoning "
          f"(sent); {answer_only:,} with its answer only")
    print(f"               {turn.prompt_tokens:>11,} prompt + reserve = "
          f"{turn.needed_tokens:,} of {result.context:,}")
    if not result.fits:
        raise SystemExit(f"VERDICT        DOES NOT FIT -- {-result.margin:,} tokens over. "
                         "Nothing was sent.")
    print(f"VERDICT        FITS -- {result.margin:,} tokens to spare "
          f"({result.margin / result.context:.1%} of the context)")
    return {
        "model": spec.name,
        "hf_revision": spec.hf_revision,
        "context": spec.context_tokens,
        "reserve": MAX_OUTPUT_TOKENS,
        "request2_prompt_tokens_with_reasoning": with_reasoning,
        "request2_prompt_tokens_answer_only": answer_only,
        "margin": result.margin,
    }


# --- the first reply, before Part 7 -------------------------------------------


def _git(repo_root: Path, *args) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo_root), *args], capture_output=True,
                          text=True, encoding="utf-8", errors="replace")


def _uncommitted(repo_root: Path, paths: list[Path]) -> list[str]:
    """Each path that git does not hold, committed and unchanged."""
    problems = []
    for path in paths:
        try:
            rel = path.resolve().relative_to(repo_root.resolve()).as_posix()
        except ValueError:
            problems.append(f"{path} is outside the repository")
            continue
        try:
            tracked = _git(repo_root, "ls-files", "--error-unmatch", "--", rel)
            status = _git(repo_root, "status", "--porcelain", "--", rel)
        except OSError as exc:
            problems.append(f"{rel}: git could not be run ({exc})")
            continue
        state = status.stdout.strip()
        if tracked.returncode != 0:
            problems.append(f"{rel} is not committed")
        elif state.startswith("A"):
            problems.append(f"{rel} is added but not committed")
        elif state:
            problems.append(f"{rel} has changed since it was committed")
    return problems


def verify_first_reply(run_dir: Path, repo_root: Path, payload_sha256: str) -> tuple[str, str, dict]:
    """Everything that must hold before Part 7 may be sent. Returns (reasoning,
    answer, turn-1 metadata); raises SystemExit, sending nothing, otherwise."""
    meta_path = run_dir / f"{TURN1}run_metadata.json"
    report_path = run_dir / f"{TURN1}report.md"
    reasoning_path = run_dir / f"{TURN1}reasoning.txt"
    if not meta_path.is_file():
        raise SystemExit(f"no first reply recorded in {run_dir} ({meta_path.name} is "
                         "missing). Send the first message with --send.")
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    problems = []
    if meta.get("model") != MODEL or meta.get("provider_pinned") != PROVIDER_SLUG:
        problems.append(f"the first reply was requested from {meta.get('model')!r} via "
                        f"{meta.get('provider_pinned')!r}, not {MODEL!r} via "
                        f"{PROVIDER_SLUG!r}")
    if meta.get("finish_reason") != "stop":
        problems.append(
            f"the first reply did not finish normally (finish_reason="
            f"{meta.get('finish_reason')!r}), so Parts 1-6 may be cut off. The ruled "
            "answer is a rerun in a fresh session, not Part 7 on an incomplete report")
    if meta.get("provider_reported") != PROVIDER_DISPLAY_NAME:
        problems.append(f"the provider reported for the first reply was "
                        f"{meta.get('provider_reported') or 'unavailable'!r}, not "
                        f"{PROVIDER_DISPLAY_NAME!r}")
    if not meta.get("report_chars"):
        problems.append("the first reply has no report content")
    if meta.get("payload_sha256") != payload_sha256:
        problems.append("the first message does not rebuild to the bytes it was sent "
                        "as: the package changed after the first send")
    texts = {}
    for path, key in ((report_path, "report_sha256"), (reasoning_path, "reasoning_sha256")):
        if not path.is_file():
            problems.append(f"{path.name} is missing")
            continue
        raw = path.read_bytes()
        if _sha256(raw) != meta.get(key):
            problems.append(f"{path.name} is not the file the first send wrote "
                            "(its SHA-256 differs from the one recorded)")
        texts[path] = raw.decode("utf-8")
    problems += _uncommitted(repo_root, [report_path, reasoning_path, meta_path])
    if problems:
        raise SystemExit("Refusing to send Part 7. Nothing was sent.\n  "
                         + "\n  ".join(problems))
    return texts[reasoning_path], texts[report_path], meta


def _holds_a_run(run_dir: Path) -> bool:
    """Whether a folder holds a reply on record: turn1_run_metadata.json, or a
    turn1_report.md that is not empty (a stream that broke off after the reply
    had started)."""
    report = run_dir / f"{TURN1}report.md"
    return ((run_dir / f"{TURN1}run_metadata.json").is_file()
            or (report.is_file() and report.stat().st_size > 0))


def recorded_runs(repo_root: Path) -> list[Path]:
    """Every run of this round on record, whatever its finish reason. A send
    that failed before any reply came back left no reply, and is not a run."""
    base = repo_root / "docs" / "audit_reports"
    if not base.is_dir():
        return []
    return sorted(d for d in base.glob(RUN_DIR_PREFIX + "*")
                  if d.is_dir() and _holds_a_run(d))


def check_another_run(repo_root: Path, payload_sha256: str) -> list[Path]:
    """Refuses, sending nothing, when the round has had its runs, or when the
    first message is not the bytes every earlier run sent. Returns the runs on
    record."""
    runs = recorded_runs(repo_root)
    if len(runs) >= MAX_RUNS:
        raise SystemExit(
            f"Round 7 has had its {MAX_RUNS} runs:"
            + "".join(f"\n  {d.name}" for d in runs)
            + "\nThe next step is another auditor, not another run (PHASE7_DECISIONS.md, "
            "\"Ruling, 30 September 2026 -- what follows round 7's first reply\", "
            "point 4). Nothing was sent.")
    problems = []
    for run in runs:
        meta_path = run / f"{TURN1}run_metadata.json"
        try:
            recorded = json.loads(meta_path.read_text(encoding="utf-8")).get("payload_sha256")
        except (OSError, ValueError):
            recorded = None
        if recorded is None:
            problems.append(f"{run.name}: no payload_sha256 on record to compare with")
        elif recorded != payload_sha256:
            problems.append(f"{run.name} sent {recorded}; this first message is "
                            f"{payload_sha256}")
    if problems:
        raise SystemExit("Refusing to send: every run sends the same first message.\n  "
                         + "\n  ".join(problems) + "\nNothing was sent.")
    return runs


def _find_waiting_run(repo_root: Path) -> Path:
    """The one run directory whose first reply has no Part 7 yet. Closed runs
    (CLOSED_RUNS) are never waiting."""
    base = repo_root / "docs" / "audit_reports"
    waiting = sorted(
        d for d in base.glob(RUN_DIR_PREFIX + "*")
        if d.name not in CLOSED_RUNS
        and (d / f"{TURN1}run_metadata.json").is_file()
        and not ((d / f"{TURN2}report.md").is_file()
                 and (d / f"{TURN2}report.md").stat().st_size > 0)
    ) if base.is_dir() else []
    if len(waiting) != 1:
        raise SystemExit(
            f"found {len(waiting)} run directories waiting for Part 7 under {base}"
            + ("".join(f"\n  {d}" for d in waiting))
            + "\nPass --out-dir to name the one to continue.")
    return waiting[0]


def _next_run_dir(repo_root: Path) -> Path:
    """The folder for the next run: round7_laguna-s-2.1_<date> for run 1,
    round7_laguna-s-2.1_run<N>_<date> for run N after it. Refused if it
    already holds a reply: a run on record is never written over. Not
    created here: main() creates it once the probe has passed."""
    number = len(recorded_runs(repo_root)) + 1
    stamp = _utc_now().strftime("%Y-%m-%d")
    name = f"{RUN_DIR_PREFIX}{stamp}" if number == 1 else f"{RUN_DIR_PREFIX}run{number}_{stamp}"
    run_dir = repo_root / "docs" / "audit_reports" / name
    if _holds_a_run(run_dir):
        raise SystemExit(f"{run_dir} already holds a reply. A run on record is never "
                         "written over. Nothing was sent.")
    return run_dir


# --- the network -----------------------------------------------------------------


def _fetch_generation(session, api_key: str, gen_id: str, sleep=time.sleep) -> dict | None:
    """The billing row for the call: provider actually used, native token counts,
    cost. One try after each wait in GENERATION_LOOKUP_WAITS."""
    for attempt, wait in enumerate(GENERATION_LOOKUP_WAITS, 1):
        sleep(wait)
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
        print(f"  generation record not available yet (try {attempt} of "
              f"{len(GENERATION_LOOKUP_WAITS)})", flush=True)
    return None


def reasoning_tokens(usage) -> int | None:
    """The reasoning-token count a usage block reports, or None when it reports none."""
    details = (usage or {}).get("completion_tokens_details") or {}
    value = details.get("reasoning_tokens")
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def read_stream(lines) -> dict:
    """What a streamed reply carried, from its server-sent-event lines: the
    generation id, the finish reason, the usage block, and the answer and the
    reasoning as text. Used by the probe; send() keeps its own loop, which
    writes to disk as it reads."""
    got = {"generation_id": None, "finish_reason": None, "usage": None,
           "content": "", "reasoning": ""}
    for raw_line in lines:
        if not raw_line or not raw_line.startswith("data: "):
            continue  # blank lines and OPENROUTER PROCESSING keep-alives
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


def probe_reasoning(body: dict, api_key: str) -> dict:
    """Sends the probe and reports what came back, for the record. Decides
    nothing: main() refuses the real send unless reasoning_tokens is above 0."""
    import requests  # pinned at 2.32.5 in requirements.txt

    print(f"POST {API_URL}  probe  model={MODEL}  provider={PROVIDER_SLUG}  "
          f"max_tokens={body['max_tokens']}  reasoning={body.get('reasoning')}", flush=True)
    resp = requests.post(
        API_URL,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json=body,
        stream=True,
        timeout=(30, 300),
    )
    resp.encoding = "utf-8"  # as in send(): the header names no charset
    if resp.status_code != 200:
        return {"http_status": resp.status_code, "error": resp.text[:2000],
                "reasoning_tokens": None}
    got = read_stream(resp.iter_lines(decode_unicode=True))
    return {
        "http_status": 200,
        "generation_id": got["generation_id"],
        "finish_reason": got["finish_reason"],
        "usage": got["usage"],
        "answer": got["content"][:200],
        "reasoning_chars": len(got["reasoning"]),
        "reasoning_tokens": reasoning_tokens(got["usage"]),
    }


def send(body: dict, api_key: str, run_dir: Path, metadata: dict, prefix: str) -> int:
    import requests  # pinned at 2.32.5 in requirements.txt

    report_path = run_dir / f"{prefix}report.md"
    reasoning_path = run_dir / f"{prefix}reasoning.txt"

    session = requests.Session()
    started = _utc_now()
    print(f"POST {API_URL}  model={MODEL}  provider={PROVIDER_SLUG}  "
          f"max_tokens={MAX_OUTPUT_TOKENS}  messages={len(body['messages'])}", flush=True)

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

    # OpenRouter's response carries no explicit charset, so `requests` would
    # otherwise fall back to Latin-1 (the old HTTP default) for resp.text and
    # for iter_lines(decode_unicode=True) below -- silently mis-decoding every
    # non-ASCII character. This is what corrupted round 6's report.md; force
    # the encoding the API actually uses instead of trusting the header.
    resp.encoding = "utf-8"

    if resp.status_code != 200:
        detail = resp.text[:8000]
        (run_dir / f"{prefix}http_error.txt").write_text(
            f"HTTP {resp.status_code}\n\n{detail}\n", encoding="utf-8"
        )
        print(f"\nHTTP {resp.status_code}. Body saved to "
              f"{run_dir / (prefix + 'http_error.txt')}", file=sys.stderr)
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
            # The bytes on disk, which --send-part7 checks before it sends
            # them back.
            "report_sha256": _sha256(report_path.read_bytes()),
            "reasoning_sha256": _sha256(reasoning_path.read_bytes()),
        }
    )

    generation = _fetch_generation(session, api_key, gen_id) if gen_id else None
    if generation:
        (run_dir / f"{prefix}generation.json").write_text(
            json.dumps(generation, indent=2), encoding="utf-8"
        )
        row = generation.get("data", generation)
        metadata["provider_reported"] = row.get("provider_name")
        metadata["native_tokens_prompt"] = row.get("native_tokens_prompt")
        metadata["native_tokens_completion"] = row.get("native_tokens_completion")
        metadata["total_cost_usd"] = row.get("total_cost")

    (run_dir / f"{prefix}run_metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )

    print()
    print(f"finish_reason        {finish_reason}")
    if usage:
        print(f"tokens in / out      {usage.get('prompt_tokens')} / "
              f"{usage.get('completion_tokens')}")
    provider_reported = metadata.get("provider_reported")
    print(f"provider reported    {provider_reported or 'unavailable'}")
    counted = metadata.get("token_check") or {}
    checked = [f"{counted[k]:,}" for k in ("request1_prompt_tokens",
                                             "request2_prompt_tokens_with_reasoning",
                                             "request2_prompt_tokens_answer_only")
               if k in counted]
    print(f"prompt tokens        provider {metadata.get('native_tokens_prompt', 'unavailable')}"
          f"; token check {' / '.join(checked) or 'not made'}")
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
    if body.get("reasoning") and not (reasoning_tokens(usage) or reasoning_chars):
        problems.append(
            "reasoning was requested and the reply carries none (no reasoning tokens, "
            "no reasoning text). The probe had shown reasoning; this reply did not. "
            "It is still a run (ruling of 30 September): score it as it stands."
        )
    for problem in problems:
        print(f"\nWARNING: {problem}", file=sys.stderr)
    if prefix == TURN1 and not problems:
        print("\nNext: read the report, commit the turn1_* files, then run --send-part7.")
    return 1 if problems else 0


def main(argv: list[str] | None = None, repo_root: Path | None = None, models=None,
         counter_factory=None, send_fn=None, probe_fn=None) -> int:
    repo_root = repo_root or Path(__file__).resolve().parents[2]
    round_dir = repo_root / "docs" / "audit_package" / "round7"
    send_fn = send_fn or send
    probe_fn = probe_fn or probe_reasoning

    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--package-dir", type=Path, default=round_dir / "MESSAGE1_PARTS1-6",
                        help="the first message's files")
    parser.add_argument("--part7-dir", type=Path, default=round_dir / "MESSAGE2_PART7",
                        help="the second message's files")
    parser.add_argument("--tokenizer-dir", type=Path, default=None,
                        help="the auditor's pinned tokenizer files (package_token_check.py); "
                             "required to send")
    parser.add_argument("--out-dir", type=Path, default=None,
                        help="with --send-part7 only: the run folder to continue (default: "
                             "the one run waiting for Part 7)")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--send", action="store_true",
                      help="send the first message; without --send or --send-part7 this is a dry run")
    mode.add_argument("--send-part7", action="store_true",
                      help="send the Part 7 material, once the first reply is committed")
    parser.add_argument("--force", action="store_true",
                        help="with --send-part7 only: overwrite an existing Part 7 reply")
    parser.add_argument("--allow-data-collection", action="store_true",
                        help="permit providers that may train on the prompt (default: deny)")
    args = parser.parse_args(argv)

    if MAX_OUTPUT_TOKENS <= LARGEST_PRIOR_RESPONSE:
        raise SystemExit("MAX_OUTPUT_TOKENS is not above the largest prior response.")

    records, texts = read_package(args.package_dir)
    part7_records, part7_texts = read_part7(args.part7_dir)
    payload = build_payload(texts)
    part7_payload = build_part7_payload(part7_texts)
    payload_sha256 = _sha256(payload.encode("utf-8"))

    for label, directory, recs, text in (
            ("first message", args.package_dir, records, payload),
            ("second message", args.part7_dir, part7_records, part7_payload)):
        print(f"{label:<15}{directory}")
        for record in recs:
            print(f"  {record['bytes']:>9,}  {record['sha256'][:16]}  {record['name']}")
        raw = text.encode("utf-8")
        print(f"  payload {len(raw):,} bytes, {len(text):,} chars, sha256 {_sha256(raw)}")
    print(f"model          {MODEL}")
    print(f"provider       {PROVIDER_SLUG} only, fallbacks off, context compression off, "
          f"data_collection {'allow' if args.allow_data_collection else 'deny'}")
    print(f"max output     {MAX_OUTPUT_TOKENS:,} tokens per reply "
          f"(largest prior response {LARGEST_PRIOR_RESPONSE:,})")

    metadata = {
        "model": MODEL,
        "provider_pinned": PROVIDER_SLUG,
        "max_output_tokens": MAX_OUTPUT_TOKENS,
        "package_dir": str(args.package_dir),
        "files": records,
        "payload_sha256": payload_sha256,
        "payload_bytes": len(payload.encode("utf-8")),
        "data_collection": "allow" if args.allow_data_collection else "deny",
        "reasoning_requested": dict(REASONING),
    }

    if args.send_part7:
        if args.tokenizer_dir is None:
            raise SystemExit("--send-part7 needs --tokenizer-dir: the second request is "
                             "measured before it is sent. Nothing was sent.")
        run_dir = args.out_dir or _find_waiting_run(repo_root)
        if Path(run_dir).name in CLOSED_RUNS:
            raise SystemExit(f"Refusing to send Part 7: {CLOSED_RUNS[Path(run_dir).name]}. "
                             "Nothing was sent.")
        report2 = run_dir / f"{TURN2}report.md"
        if report2.exists() and report2.stat().st_size > 0 and not args.force:
            raise SystemExit(f"{report2} already holds a response. Refusing to overwrite "
                             "a paid run. Nothing was sent.")
        reasoning1, answer1, meta1 = verify_first_reply(run_dir, repo_root, payload_sha256)
        counted = check_part7_send(args.tokenizer_dir, payload, reasoning1, answer1,
                                   part7_payload, models, counter_factory)
        commit = _git(repo_root, "log", "-1", "--format=%H", "--",
                      (run_dir / f"{TURN1}report.md").resolve()
                      .relative_to(repo_root.resolve()).as_posix()).stdout.strip()
        metadata.update({
            "turn": 2,
            "part7_dir": str(args.part7_dir),
            "part7_files": part7_records,
            "part7_payload_sha256": _sha256(part7_payload.encode("utf-8")),
            "turn1_report_sha256": meta1["report_sha256"],
            "turn1_reasoning_sha256": meta1["reasoning_sha256"],
            "turn1_committed_in": commit,
            "reasoning_carried": True,
            "token_check": counted,
        })
        body = build_part7_request_body(payload, reasoning1, answer1, part7_payload,
                                        args.allow_data_collection)
        prefix = TURN2
    else:
        counted = None
        if args.tokenizer_dir is not None:
            counted = check_first_send(args.tokenizer_dir, payload, part7_payload,
                                       models, counter_factory)
            upper = ((counted["request1_prompt_tokens"]
                      + counted["request2_prompt_tokens_worst_case"]) * PRICE_IN
                     + 2 * MAX_OUTPUT_TOKENS * PRICE_OUT)
            print(f"cost, at most  ${upper:.2f} for both requests, both replies at the "
                  f"full {MAX_OUTPUT_TOKENS:,} (${PRICE_IN * 1e6:.2f} / "
                  f"${PRICE_OUT * 1e6:.2f} per million)")
        else:
            print("token check    not made: pass --tokenizer-dir. --send and "
                  "--send-part7 refuse without it.")
        runs = recorded_runs(repo_root)
        print(f"runs on record {len(runs)} of {MAX_RUNS}"
              + "".join(f"\n  {d.name}" + ("  (closed)" if d.name in CLOSED_RUNS else "")
                        for d in runs))
        if not args.send:
            print("\nDry run. Nothing was sent. Re-run with --send to send the first message.")
            return 0
        if args.out_dir is not None or args.force:
            raise SystemExit("--out-dir and --force are for --send-part7 only: --send writes "
                             "each run to a folder of its own and never over a run on "
                             "record. Nothing was sent.")
        if counted is None:
            raise SystemExit("--send needs --tokenizer-dir: the conversation is measured "
                             "before anything is sent. Nothing was sent.")
        check_another_run(repo_root, payload_sha256)
        metadata.update({"turn": 1, "token_check": counted})
        body = build_request_body(payload, args.allow_data_collection)
        prefix = TURN1

    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        raise SystemExit(
            "OPENROUTER_API_KEY is not set in this shell.\n"
            "    set OPENROUTER_API_KEY=sk-or-...\n"
            "then run this command again in the same window."
        )

    if prefix == TURN1:
        run_dir = _next_run_dir(repo_root)
        probe = probe_fn(build_probe_body(args.allow_data_collection), api_key)
        metadata["reasoning_probe"] = probe
        shown = probe.get("reasoning_tokens")
        print(f"reasoning probe {shown if shown is not None else 'none reported'} reasoning "
              f"tokens (HTTP {probe.get('http_status')})")
        if not (shown or 0) > 0:
            raise SystemExit(
                "Refusing to send: the reasoning probe shows no reasoning. The audit was "
                "not sent; only the probe was. The ruling of 30 September sends run 2 "
                "with reasoning requested -- why it did not come back is to be found out "
                "first.")
    run_dir.mkdir(parents=True, exist_ok=True)
    return send_fn(body, api_key, run_dir, metadata, prefix)


if __name__ == "__main__":
    sys.exit(main())
