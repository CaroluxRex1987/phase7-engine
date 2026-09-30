"""
The audit send in two requests (docs/build/send_audit_round.py) and the build
that feeds it (docs/build/build_audit_package.py).

WHAT IT GUARDS

PHASE7_DECISIONS.md, the ruling of 29 September 2026 on what the auditor sees:
Parts 1-6 are graded on a first message alone; the Part 7 material goes in a
second, sent only after Parts 1-6 are saved. In rounds 5 and 6 the Part 7
file was in the same message as Parts 1-6, held back only by a request in its
own header (checked 29 September 2026 by rebuilding both rounds' requests).
Items 3, 4 and 5 of the preparation list for the audit.

  * the first request is the first message alone, and carries no Part 7 file;
  * the second carries the first message again, the first reply as written --
    its reasoning too (ruled 29 September, by agreeing to Claude's suggestion)
    -- and the Part 7 material;
  * both pin the model and the provider, with fallbacks and OpenRouter's
    context compression off;
  * every file the build writes into a folder is one the send sends in that
    message, and nothing else (rounds 3 and 4 built a Part 7 file no request
    ever carried);
  * the commit messages start after e65a0f7;
  * nothing is sent unless the token check was made and the request fits;
  * Part 7 is refused unless the first reply is committed, unchanged, whole
    and from the pinned provider, and the first message is the one it
    answered.

WHAT THESE TESTS DO NOT COVER

Nothing here touches the network: the function that would POST is replaced by a
spy. The streaming loop, the generation lookup and the provider's answers are
checked only by a real send. As in test_package_token_check.py, no real
tokenizer is loaded: a counter of whitespace-separated words stands in, so the
arithmetic, the refusals and what is sent are what is asserted. No test takes a
fixture, so `run_tests.py` runs every one.
"""

import contextlib
import hashlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from conftest import REPO_ROOT

BUILD_DIR = os.path.join(REPO_ROOT, "docs", "build")


def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, os.path.join(BUILD_DIR, filename))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


sar = _load("phase7_send_audit_round", "send_audit_round.py")
ptc = sar.token_check


# --- stand-ins ------------------------------------------------------------------


def _words(spec, directory):
    """A stand-in tokenizer: one token per whitespace-separated word."""
    return lambda text: len(text.split())


def _render(messages, replies=()):
    """A stand-in chat template: one header word, a tag word either side of
    each message, and each earlier reply as REPLY plus its words."""
    parts = ["HEADER"]
    for i, text in enumerate(messages):
        if i:
            reasoning, answer = replies[i - 1] if i - 1 < len(replies) else ("", "")
            parts.append(f"REPLY {reasoning} {answer}")
        parts.append(f"<u> {text} </u>")
    return " ".join(parts)


def _spec(tok_dir, context):
    files = {}
    for name in sorted(os.listdir(tok_dir)):
        with open(os.path.join(tok_dir, name), "rb") as fh:
            files[name] = hashlib.sha256(fh.read()).hexdigest()
    return ptc.ModelSpec(name="Test model", hf_repo="test/model", hf_revision="0" * 40,
                         context_tokens=context, max_output_tokens=sar.MAX_OUTPUT_TOKENS,
                         render=_render, files=files)


def _write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)


def _git(cwd, *args):
    result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True,
                            encoding="utf-8", errors="replace", timeout=120)
    assert result.returncode == 0, f"git {' '.join(args)} failed: {result.stderr}"
    return result.stdout.strip()


class _Spy:
    """Stands in for send(): records what would have gone out, sends nothing."""

    def __init__(self):
        self.calls = []

    def __call__(self, body, api_key, run_dir, metadata, prefix):
        self.calls.append({"body": body, "run_dir": Path(run_dir),
                           "metadata": metadata, "prefix": prefix})
        return 0


class _Repo:
    """A throwaway git repository holding a round-7 package, a pinned
    stand-in tokenizer folder, and optionally a first reply."""

    def __init__(self):
        self.base = tempfile.mkdtemp(prefix="phase7_send_audit_")
        self.root = Path(self.base) / "repo"
        self.root.mkdir()
        _git(self.root, "init", "-q")
        _git(self.root, "config", "user.email", "test@example.com")
        _git(self.root, "config", "user.name", "test")
        _git(self.root, "config", "core.autocrlf", "false")
        _git(self.root, "config", "commit.gpgsign", "false")
        round_dir = self.root / "docs" / "audit_package" / "round7"
        self.message1 = round_dir / "MESSAGE1_PARTS1-6"
        self.message2 = round_dir / "MESSAGE2_PART7"
        for name in sar.MESSAGE1_FILES:
            _write(str(self.message1 / name), f"first message file {name}\n")
        for name in sar.MESSAGE2_FILES:
            _write(str(self.message2 / name), f"part seven file {name}\n")
        self.tok = self.root.parent / "tok"
        _write(str(self.tok / "tokenizer.json"), "{}")
        _write(str(self.root / "README.md"), "throwaway\n")
        self.commit("initial")
        self.run_dir = self.root / "docs" / "audit_reports" / "round7_laguna-s-2.1_2026-10-01"

    def commit(self, message):
        _git(self.root, "add", "-A")
        _git(self.root, "commit", "-q", "-m", message)
        return _git(self.root, "rev-parse", "HEAD")

    def payload_sha256(self):
        _, texts = sar.read_package(self.message1)
        return hashlib.sha256(sar.build_payload(texts).encode("utf-8")).hexdigest()

    def first_reply(self, answer="## Part 1\r\nA finding.\n", reasoning="I read it.\nAll of it.",
                    **overrides):
        _write(str(self.run_dir / "turn1_report.md"), answer)
        _write(str(self.run_dir / "turn1_reasoning.txt"), reasoning)
        meta = {
            "model": sar.MODEL,
            "provider_pinned": sar.PROVIDER_SLUG,
            "payload_sha256": self.payload_sha256(),
            "finish_reason": "stop",
            "provider_reported": sar.PROVIDER_DISPLAY_NAME,
            "report_chars": len(answer),
            "report_sha256": hashlib.sha256(answer.encode("utf-8")).hexdigest(),
            "reasoning_sha256": hashlib.sha256(reasoning.encode("utf-8")).hexdigest(),
        }
        meta.update(overrides)
        _write(str(self.run_dir / "turn1_run_metadata.json"), json.dumps(meta, indent=2))

    def main(self, argv, context=10_000_000, spy=None):
        spy = spy if spy is not None else _Spy()
        models = {sar.TOKEN_CHECK_MODEL: _spec(str(self.tok), context)}
        saved = os.environ.get("OPENROUTER_API_KEY")
        os.environ["OPENROUTER_API_KEY"] = "sk-or-test"
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                code = sar.main(argv, repo_root=self.root, models=models,
                                counter_factory=_words, send_fn=spy)
        finally:
            if saved is None:
                os.environ.pop("OPENROUTER_API_KEY", None)
            else:
                os.environ["OPENROUTER_API_KEY"] = saved
        return code, spy

    def refused(self, argv, context=10_000_000):
        spy = _Spy()
        with pytest.raises(SystemExit) as info:
            self.main(argv, context=context, spy=spy)
        assert spy.calls == [], "a refusal sent something"
        return str(info.value)

    def close(self):
        shutil.rmtree(self.base, ignore_errors=True)


def _texts(names, prefix):
    return {name: f"{prefix} {name}\n" for name in names}


# --- what each request carries -------------------------------------------------


def test_the_first_request_is_the_first_message_alone():
    payload = sar.build_payload(_texts(sar.MESSAGE1_FILES, "one"))
    body = sar.build_request_body(payload, allow_data_collection=False)
    assert body["messages"] == [{"role": "user", "content": payload}]
    for name in sar.MESSAGE2_FILES:
        assert name not in payload
    for name in sar.MESSAGE1_ATTACHMENTS:
        assert f"BEGIN FILE: {name} =====" in payload


def test_the_second_request_carries_the_first_message_the_reply_and_part7():
    payload = sar.build_payload(_texts(sar.MESSAGE1_FILES, "one"))
    part7 = sar.build_part7_payload(_texts(sar.MESSAGE2_FILES, "seven"))
    body = sar.build_part7_request_body(payload, "my reasoning", "my answer", part7,
                                        allow_data_collection=False)
    first = sar.build_request_body(payload, allow_data_collection=False)
    assert body["messages"][0] == first["messages"][0]
    assert body["messages"][1] == {"role": "assistant", "content": "my answer",
                                   "reasoning": "my reasoning"}
    assert body["messages"][2] == {"role": "user", "content": part7}
    assert len(body["messages"]) == 3
    positions = [part7.index(f"BEGIN FILE: {name} =====") for name in sar.MESSAGE2_FILES]
    assert positions == sorted(positions)


def test_both_requests_pin_the_provider_and_turn_compression_off():
    payload = sar.build_payload(_texts(sar.MESSAGE1_FILES, "one"))
    part7 = sar.build_part7_payload(_texts(sar.MESSAGE2_FILES, "seven"))
    for body in (sar.build_request_body(payload, False),
                 sar.build_part7_request_body(payload, "r", "a", part7, False)):
        assert body["model"] == "poolside/laguna-s-2.1"
        assert body["provider"]["only"] == ["poolside"]
        assert body["provider"]["allow_fallbacks"] is False
        assert body["provider"]["data_collection"] == "deny"
        assert body["plugins"] == [{"id": "context-compression", "enabled": False}]
        assert body["max_tokens"] == sar.MAX_OUTPUT_TOKENS
    assert sar.MAX_OUTPUT_TOKENS > sar.LARGEST_PRIOR_RESPONSE
    assert sar.MAX_OUTPUT_TOKENS <= ptc.MODELS[sar.TOKEN_CHECK_MODEL].max_output_tokens


def test_a_part7_folder_with_a_file_too_many_or_too_few_is_refused():
    repo = _Repo()
    try:
        sar.read_part7(repo.message2)  # as built
        _write(str(repo.message2 / "extra.md"), "x")
        with pytest.raises(SystemExit) as info:
            sar.read_part7(repo.message2)
        assert "extra.md" in str(info.value)
        os.remove(repo.message2 / "extra.md")
        os.remove(repo.message2 / sar.MESSAGE2_FILES[0])
        with pytest.raises(SystemExit) as info:
            sar.read_part7(repo.message2)
        assert sar.MESSAGE2_FILES[0] in str(info.value)
    finally:
        repo.close()


# --- the build and the send agree ------------------------------------------------


def _load_builder(tmp):
    bap = _load("phase7_build_audit_package_for_send", "build_audit_package.py")
    bap.PACKAGE_DIR = tmp
    bap.OUT_DIR = os.path.join(tmp, "round7")
    bap.MESSAGE1_DIR = os.path.join(bap.OUT_DIR, "MESSAGE1_PARTS1-6")
    bap.MESSAGE2_DIR = os.path.join(bap.OUT_DIR, "MESSAGE2_PART7")
    # The engine runs and the git history are slow and are not what this
    # checks: which files land in which folder is.
    bap._transcripts = lambda: "transcripts\n"
    bap._history_metadata = lambda: "history\n"
    bap._full_messages = lambda: "messages\n"
    return bap


def test_every_file_the_build_writes_is_one_the_send_sends():
    tmp = tempfile.mkdtemp(prefix="phase7_build_")
    try:
        bap = _load_builder(tmp)
        for name in bap.HAND_WRITTEN:
            _write(os.path.join(tmp, name), f"hand-written {name}\n")
        with contextlib.redirect_stdout(io.StringIO()):
            bap.main()
        assert sorted(os.listdir(bap.MESSAGE1_DIR)) == sorted(sar.MESSAGE1_FILES)
        assert sorted(os.listdir(bap.MESSAGE2_DIR)) == sorted(sar.MESSAGE2_FILES)
        sar.read_package(Path(bap.MESSAGE1_DIR))
        sar.read_part7(Path(bap.MESSAGE2_DIR))
        assert bap.MESSAGE1_DIR.endswith("MESSAGE1_PARTS1-6")
        assert bap.MESSAGE2_DIR.endswith("MESSAGE2_PART7")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_the_build_refuses_without_the_part7_document_and_writes_nothing():
    tmp = tempfile.mkdtemp(prefix="phase7_build_")
    try:
        bap = _load_builder(tmp)
        for name in bap.MESSAGE1_HAND_WRITTEN:
            _write(os.path.join(tmp, name), f"hand-written {name}\n")
        with pytest.raises(SystemExit) as info:
            with contextlib.redirect_stdout(io.StringIO()):
                bap.main()
        assert bap.MESSAGE2_HAND_WRITTEN[0] in str(info.value)
        assert "Nothing has been written" in str(info.value)
        assert not os.path.exists(bap.OUT_DIR)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_part7_commit_messages_start_after_the_cut():
    base = tempfile.mkdtemp(prefix="phase7_cut_")
    try:
        _git(base, "init", "-q")
        _git(base, "config", "user.email", "test@example.com")
        _git(base, "config", "user.name", "test")
        _git(base, "config", "commit.gpgsign", "false")
        hashes = []
        for word in ("alpha", "bravo", "charlie"):
            _write(os.path.join(base, f"{word}.txt"), word)
            _git(base, "add", "-A")
            _git(base, "commit", "-q", "-m", f"commit {word}")
            hashes.append(_git(base, "rev-parse", "HEAD"))
        bap = _load("phase7_build_audit_package_cut", "build_audit_package.py")
        bap.REPO = base
        text = bap._full_messages(since=hashes[0][:7])
        assert "commit bravo" in text and "commit charlie" in text
        assert "commit alpha" not in text
        assert f"the 2 commits made after `{hashes[0]}`" in text
        assert f"commit {hashes[0]}" not in text
        with pytest.raises(SystemExit) as info:
            bap._full_messages(since="0000000")
        assert "REFUSING TO BUILD" in str(info.value)
    finally:
        shutil.rmtree(base, ignore_errors=True)


def test_the_cut_is_the_ruled_commit():
    assert sar.MESSAGE2_FILES[-1] == "commit_messages_PART7_ONLY.md"
    bap = _load("phase7_build_audit_package_const", "build_audit_package.py")
    assert bap.PART7_COMMITS_SINCE == "e65a0f7"
    assert bap.ROUND == "round7"


# --- the first send: measured, or not sent ----------------------------------------


def test_send_refuses_without_the_tokenizer_folder_and_sends_nothing():
    repo = _Repo()
    try:
        text = repo.refused(["--send"])
        assert "--tokenizer-dir" in text
        # A dry run without it is allowed, and says the check was not made.
        assert repo.main([])[0] == 0
    finally:
        repo.close()


def test_send_refuses_when_the_whole_conversation_does_not_fit():
    repo = _Repo()
    try:
        # Room for the first request and its reply, and for the second
        # request's own words, but not for the first reply held at the full
        # reserve inside the second request as well.
        context = 2 * sar.MAX_OUTPUT_TOKENS + 20
        text = repo.refused(["--tokenizer-dir", str(repo.tok), "--send"], context=context)
        assert "does not fit" in text
    finally:
        repo.close()


def test_send_refuses_with_a_tokenizer_it_was_not_pinned_to():
    repo = _Repo()
    try:
        spy = _Spy()
        models = {sar.TOKEN_CHECK_MODEL: _spec(str(repo.tok), 10_000_000)}
        _write(str(repo.tok / "tokenizer.json"), "{ }")
        with pytest.raises(SystemExit) as info:
            with contextlib.redirect_stdout(io.StringIO()):
                sar.main(["--tokenizer-dir", str(repo.tok), "--send"], repo_root=repo.root,
                         models=models, counter_factory=_words, send_fn=spy)
        assert str(info.value).startswith("CHECK NOT MADE:")
        assert spy.calls == []
    finally:
        repo.close()


def test_send_sends_the_first_message_alone_once_it_is_measured():
    repo = _Repo()
    try:
        code, spy = repo.main(["--tokenizer-dir", str(repo.tok), "--send"])
        assert code == 0
        [call] = spy.calls
        assert call["prefix"] == "turn1_"
        assert len(call["body"]["messages"]) == 1
        counted = call["metadata"]["token_check"]
        assert counted["request1_prompt_tokens"] > 0
        assert (counted["request2_prompt_tokens_worst_case"]
                > counted["request1_prompt_tokens"] + sar.MAX_OUTPUT_TOKENS)
        assert call["metadata"]["payload_sha256"] == repo.payload_sha256()
        assert call["run_dir"].name.startswith("round7_laguna-s-2.1_")
    finally:
        repo.close()


# --- the second send: only after the first reply is committed ---------------------


def _part7_ready(repo):
    repo.first_reply()
    return repo.commit("the first reply")


def test_part7_is_sent_with_the_first_reply_as_written():
    repo = _Repo()
    try:
        commit = _part7_ready(repo)
        code, spy = repo.main(["--tokenizer-dir", str(repo.tok), "--send-part7"])
        assert code == 0
        [call] = spy.calls
        assert call["prefix"] == "turn2_"
        assert call["run_dir"] == repo.run_dir
        user1, reply, user2 = call["body"]["messages"]
        assert reply == {"role": "assistant", "content": "## Part 1\r\nA finding.\n",
                         "reasoning": "I read it.\nAll of it."}
        assert user1["content"].startswith(sar.DELIVERY_NOTE_1.format(
            n=len(sar.MESSAGE1_ATTACHMENTS)))
        for name in sar.MESSAGE2_FILES:
            assert name in user2["content"]
        meta = call["metadata"]
        assert meta["turn1_committed_in"] == commit
        assert meta["reasoning_carried"] is True
        counted = meta["token_check"]
        # "I read it.\nAll of it." is six words: the reasoning is in the count.
        assert (counted["request2_prompt_tokens_with_reasoning"]
                == counted["request2_prompt_tokens_answer_only"] + 6)
    finally:
        repo.close()


def test_part7_is_refused_until_the_first_reply_is_committed():
    repo = _Repo()
    try:
        repo.first_reply()
        text = repo.refused(["--tokenizer-dir", str(repo.tok), "--send-part7"])
        assert "turn1_report.md is not committed" in text
        _git(repo.root, "add", "-A")
        text = repo.refused(["--tokenizer-dir", str(repo.tok), "--send-part7"])
        assert "turn1_report.md is added but not committed" in text
    finally:
        repo.close()


def test_part7_is_refused_when_the_first_reply_was_cut_off():
    repo = _Repo()
    try:
        repo.first_reply(finish_reason="length")
        repo.commit("a cut-off reply")
        text = repo.refused(["--tokenizer-dir", str(repo.tok), "--send-part7"])
        assert "finish_reason='length'" in text
    finally:
        repo.close()


def test_part7_is_refused_when_another_provider_answered():
    repo = _Repo()
    try:
        repo.first_reply(provider_reported="Someone Else")
        repo.commit("a reply from elsewhere")
        text = repo.refused(["--tokenizer-dir", str(repo.tok), "--send-part7"])
        assert "'Someone Else'" in text
    finally:
        repo.close()


def test_part7_is_refused_when_the_report_changed_after_the_send():
    repo = _Repo()
    try:
        _part7_ready(repo)
        # Edited and committed: git is clean, but the bytes are not the ones
        # the send wrote.
        _write(str(repo.run_dir / "turn1_report.md"), "## Part 1\r\nA better finding.\n")
        repo.commit("an edit")
        text = repo.refused(["--tokenizer-dir", str(repo.tok), "--send-part7"])
        assert "turn1_report.md is not the file the first send wrote" in text
        # And edited without a commit: git says so too.
        _write(str(repo.run_dir / "turn1_report.md"), "## Part 1\r\nA finding.\n")
        text = repo.refused(["--tokenizer-dir", str(repo.tok), "--send-part7"])
        assert "has changed since it was committed" in text
    finally:
        repo.close()


def test_part7_is_refused_when_the_first_message_changed_since_it_was_sent():
    repo = _Repo()
    try:
        _part7_ready(repo)
        _write(str(repo.message1 / sar.INSTRUCTION_FILE), "a different instruction\n")
        text = repo.refused(["--tokenizer-dir", str(repo.tok), "--send-part7"])
        assert "the package changed after the first send" in text
    finally:
        repo.close()


def test_part7_is_refused_without_the_tokenizer_folder_or_once_it_has_a_reply():
    repo = _Repo()
    try:
        _part7_ready(repo)
        assert "--tokenizer-dir" in repo.refused(["--send-part7"])
        _write(str(repo.run_dir / "turn2_report.md"), "Part 7.\n")
        text = repo.refused(["--tokenizer-dir", str(repo.tok), "--send-part7",
                             "--out-dir", str(repo.run_dir)])
        assert "already holds a response" in text
    finally:
        repo.close()


def test_part7_is_refused_when_the_second_request_does_not_fit():
    repo = _Repo()
    try:
        _part7_ready(repo)
        # Measured exactly now: the second request's words plus one reserve.
        text = repo.refused(["--tokenizer-dir", str(repo.tok), "--send-part7"],
                            context=sar.MAX_OUTPUT_TOKENS + 10)
        assert "DOES NOT FIT" in text
    finally:
        repo.close()
