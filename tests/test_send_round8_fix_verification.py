"""
Round 8's fix verification: the send (docs/build/send_round8_fix_verification.py)
and its instruction (docs/audit_package/round8_fix_verification_instruction.md).

WHAT IT GUARDS

PHASE7_DECISIONS.md, "Decision, 16 October 2026 -- round 8's fix verification:
what is checked, what is sent, and to whom", and the tooling decision of
17 October after it:

  * the package is built from git objects at one commit, the tagged one, and
    never from the working tree; without the tag --send refuses;
  * it carries the instruction, round 8's run-2 reports as recorded, the
    rulings from the triage of 5 October to the end of the decision of
    16 October unbroken, the Constitution's audit copy as round 8 read it,
    the engine's diff and source, and the test diff and added test files --
    this file excepted;
  * the engine round 8 read (e186423) is the engine it was sent from
    (217ede6);
  * the request pins the model, Xiaomi's endpoint, fallbacks and context
    compression off, data collection denied, and asks for reasoning;
  * nothing is sent unless MiMo's token check was made and the request fits;
  * the probe asks for the dated checkpoint first, and the send is refused
    unless the probe reasoned, came from Xiaomi and was served by round 8's
    checkpoint -- or the one --different-checkpoint names;
  * two runs at most; the second needs --second-run, the first run's files
    committed, the same message, and a commit to PHASE7_DECISIONS.md after
    the first run's report;
  * every code location the instruction cites holds the text it quotes.

WHAT THESE TESTS DO NOT COVER

Nothing here reaches the network: the probe and the send are replaced by
stand-ins, and send()'s stream is fed recorded lines through a stand-in for
requests.post. What OpenRouter and Xiaomi's endpoint actually return is
checked only by the real send. No real tokenizer is loaded: a counter of
whitespace-separated words stands in, as in test_send_audit_round.py. No test
takes a fixture, so `run_tests.py` runs every one.
"""

import ast
import contextlib
import hashlib
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from conftest import REPO_ROOT

SCRIPT = os.path.join(REPO_ROOT, "docs", "build", "send_round8_fix_verification.py")
_spec_ = importlib.util.spec_from_file_location("phase7_send_round8_verify", SCRIPT)
svr = importlib.util.module_from_spec(_spec_)
_spec_.loader.exec_module(svr)
ptc = svr.token_check
REPO = Path(REPO_ROOT)


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _git(cwd, *args):
    result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True,
                            encoding="utf-8", errors="replace", timeout=120)
    assert result.returncode == 0, f"git {' '.join(args)} failed: {result.stderr}"
    return result.stdout.strip()


def _write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)


@contextlib.contextmanager
def _patched(**values):
    saved = {name: getattr(svr, name) for name in values}
    for name, value in values.items():
        setattr(svr, name, value)
    try:
        yield
    finally:
        for name, value in saved.items():
            setattr(svr, name, value)


def _instruction_at_head(repo, commit, path):
    """The instruction from the working tree when the commit does not hold it
    yet -- the suite runs before the commit that adds it -- otherwise git's."""
    if path == svr.INSTRUCTION:
        try:
            return svr.blob(repo, commit, path)
        except SystemExit:
            return (repo / path).read_bytes().replace(b"\r\n", b"\n")
    return svr.blob(repo, commit, path)


def _real_package():
    head = svr._git_text(REPO, "rev-parse", "HEAD")
    return svr.build_package(REPO, head, show=_instruction_at_head)


# --- the package, on this repository ------------------------------------------------


def test_the_engine_round_8_read_is_the_engine_it_was_sent_from():
    assert svr.engine_unchanged(REPO, svr.READ_COMMIT, svr.SENT_COMMIT)
    assert _git(REPO, "rev-parse", "round7-sent-2026-09-30^{commit}") == svr.READ_COMMIT
    assert _git(REPO, "rev-parse", "round8-sent-2026-10-04^{commit}") == svr.SENT_COMMIT
    # The check can say no: the engine has changed since.
    assert not svr.engine_unchanged(REPO, svr.READ_COMMIT, "HEAD")


def test_the_package_carries_what_the_decision_names_in_order():
    files = _real_package()
    names = [n for n, _ in files]
    head = svr._git_text(REPO, "rev-parse", "HEAD")
    engine = svr.engine_files(REPO, head)
    read_tests = svr.files_under_tests(REPO, svr.READ_COMMIT)
    added = [p for p in svr.files_under_tests(REPO, head)
             if p not in read_tests and p not in svr.OWN_TESTS]
    assert names == ([svr.INSTRUCTION] + list(svr.ROUND8_REPORTS)
                     + [svr.RULINGS_NAME, svr.CONSTITUTION, svr.ENGINE_DIFF_NAME]
                     + engine + [svr.TESTS_DIFF_NAME] + added)
    assert "tests/test_send_round8_fix_verification.py" not in names
    assert added, "no test file was added since e186423"
    # Every engine file is one the code fingerprint walks.
    walked = set(_fingerprint_files())
    assert set(engine) <= walked
    assert "models/risk_model.py" in engine and "core/config.py" in engine
    assert not [p for p in engine if p.startswith(("tests/", "docs/"))]


def _fingerprint_files():
    spec = importlib.util.spec_from_file_location(
        "phase7_fp_for_verify", os.path.join(REPO_ROOT, "core", "code_fingerprint.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return list(module.iter_source_files(REPO_ROOT))


def test_the_reports_and_the_checkpoint_are_round_8s_as_recorded():
    run2 = REPO / svr.ROUND8_RUN2
    for turn in ("turn1", "turn2"):
        meta = json.loads((run2 / f"{turn}_run_metadata.json").read_text(encoding="utf-8"))
        assert svr.ROUND8_REPORTS[f"{svr.ROUND8_RUN2}/{turn}_report.md"] == meta["report_sha256"]
        assert meta["model"] == svr.MODEL and meta["provider_reported"] == svr.PROVIDER_NAME
    largest = 0
    for run in ("round8_mimo-v2.6-pro_2026-10-04", "round8_mimo-v2.6-pro_run2_2026-10-04"):
        for turn in ("turn1", "turn2"):
            path = REPO / "docs" / "audit_reports" / run / f"{turn}_generation.json"
            if not path.is_file():
                continue
            row = json.loads(path.read_text(encoding="utf-8"))
            row = row.get("data", row)
            assert row["model"] == svr.ROUND8_CHECKPOINT
            largest = max(largest, row["native_tokens_completion"])
    assert largest == svr.LARGEST_PRIOR_RESPONSE < svr.MAX_OUTPUT_TOKENS
    meta = json.loads((run2 / "turn1_run_metadata.json").read_text(encoding="utf-8"))
    [constitution] = [f for f in meta["files"]
                      if f["name"] == os.path.basename(svr.CONSTITUTION)]
    assert constitution["sha256"] == svr.CONSTITUTION_ROUND8_SHA256
    files = dict(_real_package())
    assert _sha(files[svr.CONSTITUTION]) == svr.CONSTITUTION_ROUND8_SHA256
    for path, expected in svr.ROUND8_REPORTS.items():
        assert _sha(files[path]) == expected


def test_the_rulings_are_one_unbroken_excerpt_from_the_triage_to_the_decision():
    decisions = (REPO / svr.DECISIONS).read_bytes().replace(b"\r\n", b"\n").decode("utf-8")
    excerpt = svr.extract_rulings(decisions)
    assert excerpt in decisions
    assert excerpt.startswith(svr.RULINGS_FIRST)
    assert excerpt.count("\n" + svr.RULINGS_LAST) == 1
    end = decisions.index(excerpt) + len(excerpt)
    assert decisions[end:].startswith("## ")
    assert "## Ruling, 4 October 2026" not in excerpt
    assert not re.search(r"(?m)^## Decision, 17 October", excerpt)
    for heading in ("## Ruling, 12 October 2026", "## Ruling, 13 October 2026",
                    "## Ruling, 14 October 2026", "## Ruling, 15 October 2026",
                    "## Correction, 5 October 2026", "## Position, 6 October 2026"):
        assert heading in excerpt


def test_the_rulings_excerpt_is_refused_when_its_bounds_are_not_one_each():
    first, last = svr.RULINGS_FIRST + ": x\n", svr.RULINGS_LAST + ": y\n"
    good = "# D\n\n" + first + "a\n\n" + last + "b\n\n## Next\nc\n"
    assert svr.extract_rulings(good) == first + "a\n\n" + last + "b\n\n"
    for bad in (good + first, good + last, "# D\n\n" + last + "b\n\n" + first + "a\n",
                "# D\n\n" + first + "a\n\n" + last + "b\n", "# D\n\n" + first):
        with pytest.raises(SystemExit):
            svr.extract_rulings(bad)


def test_the_payload_is_the_same_bytes_every_time_and_names_every_file_once():
    files = _real_package()
    payload = svr.build_payload(files)
    assert svr.build_payload(_real_package()) == payload
    assert payload.startswith(svr.DELIVERY_NOTE.format(n=len(files) - 1))
    for name, _ in files[1:]:
        assert payload.count(f"===== BEGIN FILE: {name} =====") == 1
        assert payload.count(f"===== END FILE: {name} =====") == 1
    assert "BEGIN FILE: " + svr.INSTRUCTION not in payload


# --- the instruction cites code that is there -----------------------------------------


_LOCATION = re.compile(r"[(;]\s*`([\w/]+\.py)`,\s+lines?\s+(\d+)(?:\u2013(\d+))?")
_QUOTED = re.compile(r"`([^`\n]+)`|\"([^\"\n]+)\"")


def _citations(text):
    """(quote or None, path, first line, last line) for every location the text
    cites. The quote is the backticked or double-quoted text just before the
    location -- at most 80 characters before it, in the same sentence (no ")",
    new bullet or blank line between), with no other quote between -- unless
    that is itself a file path."""
    found = []
    for loc in _LOCATION.finditer(text):
        window = text[max(0, loc.start() - 120):loc.start()]
        quotes = list(_QUOTED.finditer(window))
        quote = None
        if quotes:
            last = quotes[-1]
            gap = window[last.end():]
            value = last.group(1) or last.group(2)
            if (len(gap) <= 80 and not value.endswith(".py")
                    and not any(mark in gap for mark in (")", "\n-", "\n\n"))):
                quote = value
        first = int(loc.group(2))
        found.append((quote, loc.group(1), first, int(loc.group(3) or first)))
    return found


def _instruction_tree():
    """Where the instruction's line numbers are to hold: the commit that last
    changed it, once it is committed and unchanged; the working tree before."""
    rel = svr.INSTRUCTION
    committed = _git(REPO, "log", "-1", "--format=%H", "--", rel)
    if committed and not _git(REPO, "status", "--porcelain", "--", rel):
        return lambda path: svr.blob(REPO, committed, path).decode("utf-8")
    return lambda path: (REPO / path).read_bytes().decode("utf-8")


def test_every_code_location_the_instruction_cites_holds_what_it_quotes():
    text = (REPO / svr.INSTRUCTION).read_bytes().decode("utf-8").replace("\r\n", "\n")
    read = _instruction_tree()
    cites = _citations(text)
    # Every "`x.py`, line" in the instruction is one of the citations checked.
    assert len(cites) == len(re.findall(r"`[\w/]+\.py`,\s+lines?\s", text)) == 11
    for quote, path, first, last in cites:
        lines = read(path).replace("\r\n", "\n").split("\n")
        assert 1 <= first <= last <= len(lines), f"{path}:{first}-{last} is not in the file"
        if quote:
            assert quote in "\n".join(lines[first - 1:last]), f"{quote!r} is not at {path}:{first}"
    assert sum(1 for c in cites if c[0]) == 7


def test_the_location_check_can_fail():
    text = "is `stop_mult = ATR_STOP_MULT * vol_multiplier` (`models/risk_model.py`, line 401)"
    [(quote, path, first, _)] = _citations(text)
    assert quote == "stop_mult = ATR_STOP_MULT * vol_multiplier"
    lines = (REPO / path).read_bytes().decode("utf-8").replace("\r\n", "\n").split("\n")
    assert quote not in lines[first - 1]
    assert quote in lines[first - 2]


# --- requests -----------------------------------------------------------------------


def test_every_request_pins_the_model_the_provider_and_asks_for_reasoning():
    for model in svr.MODEL_NAMES:
        for body in (svr.build_request_body("payload", model), svr.build_probe_body(model)):
            assert body["model"] == model
            assert body["provider"] == {"only": ["xiaomi"], "allow_fallbacks": False,
                                        "require_parameters": True, "data_collection": "deny"}
            assert body["reasoning"] == {"enabled": True}
            assert body["plugins"] == [{"id": "context-compression", "enabled": False}]
            assert len(body["messages"]) == 1
    assert svr.MODEL_NAMES == ("xiaomi/mimo-v2.6-pro-20260921", "xiaomi/mimo-v2.6-pro")
    assert svr.build_request_body("p", svr.MODEL)["max_tokens"] == svr.MAX_OUTPUT_TOKENS
    probe = svr.build_probe_body(svr.MODEL)
    assert probe["messages"] == [{"role": "user", "content": svr.PROBE_PROMPT}]
    assert probe["max_tokens"] == svr.PROBE_MAX_TOKENS < svr.MAX_OUTPUT_TOKENS
    with pytest.raises(SystemExit):
        svr.build_request_body("p", "xiaomi/mimo-v2.6-flash")


def test_this_script_imports_nothing_from_the_other_send_scripts():
    """Its model and transport are its own (the script's docstring, WHY A SCRIPT
    OF ITS OWN): no import of the other two, and no string naming either -- a
    path built from one would be how a module gets loaded by file."""
    tree = ast.parse(Path(SCRIPT).read_text(encoding="utf-8"))
    docstring = ast.get_docstring(tree, clean=False)
    for node in ast.walk(tree):
        names = []
        if isinstance(node, ast.Import):
            names = [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            names = [node.module or ""]
        elif isinstance(node, ast.Constant) and isinstance(node.value, str) \
                and node.value != docstring:
            names = [node.value]
        for name in names:
            assert "send_audit_round" not in name and "send_fix_verification" not in name


# --- stand-ins -------------------------------------------------------------------------


def _words(spec, directory):
    return lambda text: len(text.split())


def _render(messages, replies=()):
    return "HEADER " + " ".join(f"<u> {m} </u>" for m in messages)


def _models(tok_dir, context):
    files = {n: _sha((Path(tok_dir) / n).read_bytes()) for n in sorted(os.listdir(tok_dir))}
    return {svr.TOKEN_CHECK_MODEL: ptc.ModelSpec(
        name="Test model", hf_repo="test/model", hf_revision="0" * 40,
        context_tokens=context, max_output_tokens=svr.MAX_OUTPUT_TOKENS,
        render=_render, files=files)}


class _Spy:
    def __init__(self):
        self.calls = []

    def __call__(self, body, api_key, run_dir, metadata):
        self.calls.append({"body": body, "run_dir": Path(run_dir), "metadata": metadata})
        return 0


class _Probe:
    """Stands in for probe(): answers each model name as told."""

    def __init__(self, answers=None):
        self.answers = answers or {}
        self.calls = []

    def __call__(self, body, api_key):
        self.calls.append(body)
        result = {"model_requested": body["model"], "http_status": 200,
                  "reasoning_tokens": 9, "model_reported": svr.ROUND8_CHECKPOINT,
                  "provider_reported": "Xiaomi"}
        result.update(self.answers.get(body["model"], {}))
        return result


DECISIONS_TEXT = ("# Decisions\n\n## Ruling, 4 October 2026 — earlier\nold\n\n"
                  + svr.RULINGS_FIRST + ": triage\nfixes\n\n## Position, 6 October\np\n\n"
                  + svr.RULINGS_LAST + ": what is sent\nthe package\n\n## Working practice\nw\n")


class _Repo:
    """A throwaway repository: a commit the auditor read (A), one it was sent
    from (B, the engine unchanged), and one the fixes landed in (C)."""

    def __init__(self):
        self.base = Path(tempfile.mkdtemp(prefix="phase7_verify_"))
        self.root = self.base / "repo"
        self.root.mkdir()
        for args in (("init", "-q"), ("config", "user.email", "t@example.com"),
                     ("config", "user.name", "t"), ("config", "core.autocrlf", "false"),
                     ("config", "commit.gpgsign", "false"), ("config", "tag.gpgsign", "false")):
            _git(self.root, *args)
        shutil.copy(os.path.join(REPO_ROOT, "core", "code_fingerprint.py"),
                    self.root / "_fp.py")
        self.put("core/code_fingerprint.py", (self.root / "_fp.py").read_text(encoding="utf-8"))
        os.remove(self.root / "_fp.py")
        self.put("models/risk_model.py", "stop_mult = 1.2\n")
        self.put("tests/test_old.py", "def test_old():\n    assert True\n")
        self.put("docs/build/tool.py", "x = 1\n")
        self.reports = {}
        for turn in ("turn1", "turn2"):
            path = f"{svr.ROUND8_RUN2}/{turn}_report.md"
            self.put(path, f"# {turn} report\n")
            self.reports[path] = _sha(f"# {turn} report\n".encode())
        self.put(svr.CONSTITUTION, "Tier 1\nItem 14\n")
        self.constitution = _sha(b"Tier 1\r\nItem 14\r\n")
        self.put(svr.DECISIONS, DECISIONS_TEXT)
        self.read = self.commit("read")
        self.put("docs/note.md", "sent\n")
        self.sent = self.commit("sent")
        self.put("models/risk_model.py", "stop_mult = ATR_STOP_MULT * vol_multiplier\n")
        self.put("tests/test_old.py", "def test_old():\n    assert 1\n")
        self.put("tests/test_new.py", "def test_new():\n    assert True\n")
        self.put("tests/test_send_round8_fix_verification.py", "own\n")
        self.put(svr.INSTRUCTION, "# Instruction\n")
        self.fixed = self.commit("fixed")
        self.tok = self.base / "tok"
        _write(str(self.tok / "tokenizer.json"), "{}")

    def put(self, rel, text):
        _write(str(self.root / rel), text)

    def commit(self, message):
        _git(self.root, "add", "-A")
        _git(self.root, "commit", "-q", "-m", message)
        return _git(self.root, "rev-parse", "HEAD")

    def tag(self, name="round8-verify-sent-2026-10-17", commit="HEAD"):
        _git(self.root, "tag", name, commit)

    def patched(self):
        return _patched(READ_COMMIT=self.read, SENT_COMMIT=self.sent,
                        ROUND8_REPORTS=self.reports, CONSTITUTION_ROUND8_SHA256=self.constitution)

    def payload_sha256(self, commit):
        with self.patched():
            return _sha(svr.build_payload(svr.build_package(self.root, commit)).encode("utf-8"))

    def main(self, argv, context=10_000_000, spy=None, probe=None):
        spy = spy if spy is not None else _Spy()
        probe = probe if probe is not None else _Probe()
        saved = os.environ.get("OPENROUTER_API_KEY")
        os.environ["OPENROUTER_API_KEY"] = "sk-or-test"
        try:
            with self.patched(), contextlib.redirect_stdout(io.StringIO()):
                code = svr.main(argv, repo_root=self.root, models=_models(self.tok, context),
                                counter_factory=_words, send_fn=spy, probe_fn=probe)
        finally:
            if saved is None:
                os.environ.pop("OPENROUTER_API_KEY", None)
            else:
                os.environ["OPENROUTER_API_KEY"] = saved
        return code, spy, probe

    def refused(self, argv, probe=None, probes=0, context=10_000_000):
        spy = _Spy()
        probe = probe if probe is not None else _Probe()
        with pytest.raises(SystemExit) as info:
            self.main(argv, context=context, spy=spy, probe=probe)
        assert spy.calls == [], "a refusal sent something"
        assert len(probe.calls) == probes, "the probe went out when it should not"
        return str(info.value)

    def run_on_record(self, name, payload_sha256, commit=True):
        run = self.root / "docs" / "audit_reports" / name
        _write(str(run / "report.md"), "A. Holds.\n")
        _write(str(run / "reasoning.txt"), "read\n")
        _write(str(run / "run_metadata.json"), json.dumps({"payload_sha256": payload_sha256}))
        if commit:
            self.commit(f"run {name}")
        return run

    def close(self):
        shutil.rmtree(self.base, ignore_errors=True)


def _send_args(repo, *extra):
    return ["--tokenizer-dir", str(repo.tok), "--send", *extra]


def _no_run_folder(repo):
    base = repo.root / "docs" / "audit_reports"
    return not list(base.glob(svr.RUN_DIR_PREFIX + "*"))


# --- the package, on a throwaway repository -----------------------------------------------


def test_the_package_is_git_s_bytes_at_the_commit_not_the_working_tree():
    repo = _Repo()
    try:
        repo.put("models/risk_model.py", "changed in the working tree only\n")
        with repo.patched():
            files = dict(svr.build_package(repo.root, repo.fixed))
        assert files["models/risk_model.py"] == b"stop_mult = ATR_STOP_MULT * vol_multiplier\n"
        assert files[svr.CONSTITUTION] == b"Tier 1\r\nItem 14\r\n"
        assert "tests/test_new.py" in files and "tests/test_old.py" not in files
        assert "tests/test_send_round8_fix_verification.py" not in files
        assert "docs/build/tool.py" not in files
        assert b"-stop_mult = 1.2" in files[svr.ENGINE_DIFF_NAME]
        assert b"+    assert 1" in files[svr.TESTS_DIFF_NAME]
        assert b"own" not in files[svr.TESTS_DIFF_NAME]
        assert files[svr.RULINGS_NAME].decode().startswith(svr.RULINGS_FIRST)
        assert b"## Working practice" not in files[svr.RULINGS_NAME]
    finally:
        repo.close()


def test_the_package_is_refused_when_what_it_rests_on_is_not_as_recorded():
    repo = _Repo()
    try:
        cases = (
            {"ROUND8_REPORTS": {f"{svr.ROUND8_RUN2}/turn1_report.md": "0" * 64}},
            {"CONSTITUTION_ROUND8_SHA256": "0" * 64},
            {"SENT_COMMIT": repo.fixed},
        )
        for overrides in cases:
            with repo.patched(), _patched(**overrides):
                with pytest.raises(SystemExit) as info:
                    svr.build_package(repo.root, repo.fixed)
            assert "Nothing was sent" in str(info.value)
        with repo.patched(), pytest.raises(SystemExit):
            svr.build_package(repo.root, repo.read)  # holds no instruction
    finally:
        repo.close()


# --- main --------------------------------------------------------------------------------------


def test_the_dry_run_builds_from_head_until_the_tag_exists_and_sends_nothing():
    repo = _Repo()
    try:
        code, spy, probe = repo.main(["--tokenizer-dir", str(repo.tok)])
        assert code == 0 and spy.calls == [] and probe.calls == []
        text = repo.refused(_send_args(repo))
        assert "no tag round8-verify-sent-<date>" in text
        assert _no_run_folder(repo)
    finally:
        repo.close()


def test_the_send_is_the_tagged_commit_s_package_not_head_s():
    repo = _Repo()
    try:
        repo.tag()
        repo.put("models/risk_model.py", "stop_mult = 9\n")
        head = repo.commit("after the tag")
        code, spy, probe = repo.main(_send_args(repo))
        assert code == 0
        [call] = spy.calls
        meta = call["metadata"]
        assert meta["commit"] == repo.fixed != head
        assert meta["tag"] == "round8-verify-sent-2026-10-17"
        assert meta["payload_sha256"] == repo.payload_sha256(repo.fixed)
        assert call["body"]["messages"][0]["content"].count("stop_mult = 9") == 0
        assert call["body"]["model"] == svr.ROUND8_CHECKPOINT
        assert meta["checkpoint_accepted"] == svr.ROUND8_CHECKPOINT
        assert meta["different_checkpoint"] is False
        assert call["run_dir"].name.startswith(svr.RUN_DIR_PREFIX)
        assert "run2" not in call["run_dir"].name
        assert _no_run_folder(repo), "main() created the run folder; send() does"
        assert [b["model"] for b in probe.calls] == [svr.ROUND8_CHECKPOINT]
    finally:
        repo.close()


def test_the_send_is_refused_with_two_tags_or_a_misnamed_one():
    for tags in (("round8-verify-sent-2026-10-17", "round8-verify-sent-2026-10-18"),
                 ("round8-verify-sent-17-oct",)):
        repo = _Repo()
        try:
            for name in tags:
                repo.tag(name)
            assert "expected one tag" in repo.refused(_send_args(repo))
        finally:
            repo.close()


def test_the_send_is_refused_without_the_token_check_or_when_it_does_not_fit():
    repo = _Repo()
    try:
        repo.tag()
        assert "--send needs --tokenizer-dir" in repo.refused(["--send"])
        assert "does not fit" in repo.refused(_send_args(repo), context=svr.MAX_OUTPUT_TOKENS)
        _write(str(repo.tok / "tokenizer.json"), "{\"changed\": true}")
        models = _models(repo.tok, 10_000_000)
        _write(str(repo.tok / "tokenizer.json"), "{}")
        spy = _Spy()
        with repo.patched(), pytest.raises(SystemExit) as info, \
                contextlib.redirect_stdout(io.StringIO()):
            svr.main(_send_args(repo), repo_root=repo.root, models=models,
                     counter_factory=_words, send_fn=spy, probe_fn=_Probe())
        assert "CHECK NOT MADE" in str(info.value) and spy.calls == []
    finally:
        repo.close()


def test_the_undated_name_is_used_only_when_the_dated_one_is_refused():
    repo = _Repo()
    try:
        repo.tag()
        probe = _Probe({svr.ROUND8_CHECKPOINT: {"http_status": 400}})
        code, spy, _ = repo.main(_send_args(repo), probe=probe)
        assert code == 0
        assert [b["model"] for b in probe.calls] == list(svr.MODEL_NAMES)
        assert spy.calls[0]["body"]["model"] == svr.MODEL
        assert len(spy.calls[0]["metadata"]["reasoning_probes"]) == 2
        both = _Probe({n: {"http_status": 404} for n in svr.MODEL_NAMES})
        assert "accepted neither" in repo.refused(_send_args(repo), probe=both, probes=2)
    finally:
        repo.close()


def test_the_send_is_refused_unless_the_probe_shows_round_8_s_checkpoint():
    repo = _Repo()
    try:
        repo.tag()
        other = "xiaomi/mimo-v2.6-pro-20261101"
        answers = {svr.ROUND8_CHECKPOINT: {"model_reported": other}}
        text = repo.refused(_send_args(repo), probe=_Probe(answers), probes=1)
        assert f"--different-checkpoint {other}" in text
        assert "--different-checkpoint unrecorded" in repo.refused(
            _send_args(repo), probe=_Probe({svr.ROUND8_CHECKPOINT: {"model_reported": None}}),
            probes=1)
        repo.refused(_send_args(repo, "--different-checkpoint", "xiaomi/another"),
                     probe=_Probe(answers), probes=1)
        code, spy, _ = repo.main(_send_args(repo, "--different-checkpoint", other),
                                 probe=_Probe(answers))
        assert code == 0
        meta = spy.calls[0]["metadata"]
        assert meta["checkpoint_accepted"] == other and meta["different_checkpoint"] is True
    finally:
        repo.close()


def test_the_send_is_refused_when_the_probe_did_not_reason_or_came_from_elsewhere():
    repo = _Repo()
    try:
        repo.tag()
        for answer, words in (({"reasoning_tokens": 0}, "no reasoning"),
                              ({"reasoning_tokens": None}, "no reasoning"),
                              ({"provider_reported": "Novita"}, "'Novita'")):
            probe = _Probe({svr.ROUND8_CHECKPOINT: answer})
            assert words in repo.refused(_send_args(repo), probe=probe, probes=1)
        assert _no_run_folder(repo)
    finally:
        repo.close()


def test_a_second_run_needs_its_flag_the_same_message_and_a_filed_decision():
    repo = _Repo()
    try:
        repo.tag()
        sha = repo.payload_sha256(repo.fixed)
        assert "no first run" in repo.refused(_send_args(repo, "--second-run"))
        # A folder holding only an HTTP error is not a run.
        _write(str(repo.root / "docs" / "audit_reports" / (svr.RUN_DIR_PREFIX + "2026-10-17")
                   / "http_error.txt"), "HTTP 404\n")
        assert repo.main(_send_args(repo))[0] == 0
        shutil.rmtree(repo.root / "docs" / "audit_reports" / (svr.RUN_DIR_PREFIX + "2026-10-17"))
        repo.run_on_record(svr.RUN_DIR_PREFIX + "2026-10-17", sha)
        assert "needs --second-run" in repo.refused(_send_args(repo))
        assert "no commit to PHASE7_DECISIONS.md" in repo.refused(_send_args(repo, "--second-run"))
        repo.put(svr.DECISIONS, DECISIONS_TEXT + "\n## Decision — the second run\nsend it\n")
        repo.commit("decide the second run")
        code, spy, _ = repo.main(_send_args(repo, "--second-run"))
        assert code == 0 and "run2_" in spy.calls[0]["run_dir"].name
        assert spy.calls[0]["metadata"]["run"] == 2
        assert spy.calls[0]["metadata"]["payload_sha256"] == sha
        # Run 1's report changed after it was committed: refused.
        repo.put(f"docs/audit_reports/{svr.RUN_DIR_PREFIX}2026-10-17/report.md", "edited\n")
        assert "has changed" in repo.refused(_send_args(repo, "--second-run"))
    finally:
        repo.close()


def test_a_second_run_is_refused_when_its_message_differs_and_a_third_always():
    repo = _Repo()
    try:
        repo.tag()
        repo.run_on_record(svr.RUN_DIR_PREFIX + "2026-10-17", "f" * 64)
        repo.put(svr.DECISIONS, DECISIONS_TEXT + "\n## Decision — the second run\nx\n")
        repo.commit("decide")
        assert "Both runs send the same message" in repo.refused(
            _send_args(repo, "--second-run"))
        repo.run_on_record(svr.RUN_DIR_PREFIX + "run2_2026-10-18", "f" * 64)
        assert "has had its 2 runs" in repo.refused(_send_args(repo, "--second-run"))
    finally:
        repo.close()


# --- send(), fed recorded lines ---------------------------------------------------------------


def _sse(*events):
    lines = [": OPENROUTER PROCESSING", ""]
    for event in events:
        lines += ["data: " + json.dumps(event), ""]
    return lines + ["data: [DONE]", ""]


class _Response:
    def __init__(self, lines, status=200, text=""):
        self.lines, self.status_code, self.text, self.encoding = lines, status, text, None

    def iter_lines(self, decode_unicode=True):
        assert self.encoding == "utf-8", "the stream was read before its encoding was set"
        return iter(self.lines)


def _reply(answer="A. Holds — risk_model.py:400.", reasoning="Read it.", finish="stop"):
    usage = {"prompt_tokens": 10, "completion_tokens": 20,
             "completion_tokens_details": {"reasoning_tokens": 5}}
    return _sse({"id": "gen-1", "choices": [{"delta": {"reasoning": reasoning}}]},
                {"id": "gen-1", "choices": [{"delta": {"content": answer},
                                             "finish_reason": finish}]},
                {"id": "gen-1", "choices": [], "usage": usage})


def _record(**overrides):
    row = {"model": svr.ROUND8_CHECKPOINT, "provider_name": "Xiaomi",
           "native_tokens_prompt": 10, "native_tokens_completion": 20, "total_cost": 0.01}
    row.update(overrides)
    return lambda api_key, gen_id: row


def _metadata():
    return {"checkpoint_accepted": svr.ROUND8_CHECKPOINT, "token_check": {"prompt_tokens": 9}}


def test_send_writes_the_reply_as_it_arrives_and_records_what_served_it():
    base = Path(tempfile.mkdtemp(prefix="phase7_verify_send_"))
    try:
        run_dir = base / "run"
        meta = _metadata()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            code = svr.send({"model": svr.MODEL, "max_tokens": 1}, "k", run_dir, meta,
                            post=lambda *a, **k: _Response(_reply()), fetch=_record())
        assert code == 0
        report = (run_dir / "report.md").read_bytes()
        assert report.decode("utf-8") == "A. Holds — risk_model.py:400."
        assert meta["report_sha256"] == _sha(report)
        assert meta["model_reported"] == svr.ROUND8_CHECKPOINT
        saved = json.loads((run_dir / "run_metadata.json").read_text(encoding="utf-8"))
        assert saved["finish_reason"] == "stop" and saved["provider_reported"] == "Xiaomi"
        assert (run_dir / "generation.json").is_file()
    finally:
        shutil.rmtree(base, ignore_errors=True)


def test_send_warns_when_the_reply_is_cut_off_or_served_by_another_checkpoint():
    cases = (({"finish": "length"}, {}), ({}, {"model": "xiaomi/other"}),
             ({}, {"provider_name": "Novita"}), ({"answer": ""}, {}))
    for reply, record in cases:
        base = Path(tempfile.mkdtemp(prefix="phase7_verify_send_"))
        try:
            err = io.StringIO()
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                code = svr.send({"model": svr.MODEL, "max_tokens": 1}, "k", base / "run",
                                _metadata(), post=lambda *a, **k: _Response(_reply(**reply)),
                                fetch=_record(**record))
            assert code == 1 and "WARNING" in err.getvalue(), (reply, record)
            assert (base / "run" / "run_metadata.json").is_file(), "a reply is always recorded"
        finally:
            shutil.rmtree(base, ignore_errors=True)


def test_an_http_error_is_saved_and_leaves_no_run():
    base = Path(tempfile.mkdtemp(prefix="phase7_verify_send_"))
    try:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            code = svr.send({"model": svr.MODEL, "max_tokens": 1}, "k", base / "run", _metadata(),
                            post=lambda *a, **k: _Response([], status=404, text="no endpoints"),
                            fetch=_record())
        assert code == 2
        assert (base / "run" / "http_error.txt").is_file()
        assert not svr._holds_a_run(base / "run")
    finally:
        shutil.rmtree(base, ignore_errors=True)


def test_the_generation_lookup_waits_about_five_minutes_and_reads_the_row():
    assert 280 <= sum(svr.GENERATION_LOOKUP_WAITS) <= 320
    waits = []

    class _Got:
        status_code = 200

        def json(self):
            return {"data": {"model": svr.ROUND8_CHECKPOINT}}

    tries = iter([Exception("not yet"), _Got()])

    def get(*args, **kwargs):
        item = next(tries)
        if isinstance(item, Exception):
            raise item
        return item

    with contextlib.redirect_stdout(io.StringIO()):
        row = svr.fetch_generation("k", "gen-1", sleep=waits.append, get=get)
    assert row == {"model": svr.ROUND8_CHECKPOINT} and len(waits) == 2
    with contextlib.redirect_stdout(io.StringIO()):
        assert svr.fetch_generation("k", "gen-1", sleep=lambda s: None,
                                    get=lambda *a, **k: (_ for _ in ()).throw(OSError())) is None
