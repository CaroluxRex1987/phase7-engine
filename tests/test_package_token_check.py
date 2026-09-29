"""
The pre-send token check (docs/build/package_token_check.py).

WHAT IT GUARDS

PHASE7_DECISIONS.md, "Ruling, 26 September 2026 -- the pre-send token check is
audit preparation, not an engine item": measure the package with the auditor's
own tokenizer, and refuse the send if the package plus an output reserve does
not fit the model's context. Item 2 of the preparation list for the audit ruled
on 29 September 2026.

WHAT THESE TESTS DO NOT COVER

They never load a real tokenizer. `tokenizers` is documentation tooling and is
not in requirements.txt, and Poolside's files are kept outside the repository,
so a test that needed either would be skipped on every machine that runs this
suite -- a test that passes by being skipped is the vacuous pass this suite was
hardened against. The counter is injected instead; the arithmetic, the refusals
and the exit codes are what is asserted here. Loading the real tokenizer is
checked by running the tool itself on a known file, on both platforms, with the
count stated in advance (the commit that adds this file).
"""

import hashlib
import importlib.util
import io
import os
import tempfile

import pytest

from conftest import REPO_ROOT

MODULE_PATH = os.path.join(REPO_ROOT, "docs", "build", "package_token_check.py")


def _load():
    spec = importlib.util.spec_from_file_location("phase7_package_token_check", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ptc = _load()


def _words(spec, directory):
    """A stand-in tokenizer: one token per whitespace-separated word."""
    return lambda text: len(text.split())


def _render(messages):
    """A stand-in chat template: two tag words around every message, one word
    for each empty earlier reply, and three words of header."""
    body = " REPLY ".join(f"<u> {m} </u>" for m in messages)
    return "HEADER HEADER HEADER " + body


def _spec_for(directory, context, max_output):
    """A model entry pinned to whatever files are in `directory`."""
    files = {}
    for name in sorted(os.listdir(directory)):
        with open(os.path.join(directory, name), "rb") as fh:
            files[name] = hashlib.sha256(fh.read()).hexdigest()
    return ptc.ModelSpec(name="Test model", hf_repo="test/model", hf_revision="0" * 40,
                         context_tokens=context, max_output_tokens=max_output,
                         render=_render, files=files)


def _write(path, text):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)


# --- the arithmetic -------------------------------------------------------


def test_one_message_needs_the_rendered_request_and_the_reserve():
    result = ptc.check_fit([720], reserve=100, context=820)
    assert result.needed == 820
    assert result.margin == 0
    assert result.fits


def test_one_token_over_the_context_does_not_fit():
    result = ptc.check_fit([721], reserve=100, context=820)
    assert result.needed == 821
    assert result.margin == -1
    assert not result.fits


def test_the_second_turn_carries_the_first_reply_at_the_full_reserve():
    # Turn 2's request renders at 710 tokens with reply 1 empty; reply 1 is then
    # counted at the reserve, and reply 2 needs the reserve too: 710 + 100 + 100.
    result = ptc.check_fit([510, 710], reserve=100, context=10_000)
    assert [t.prompt_tokens for t in result.turns] == [510, 810]
    assert [t.needed_tokens for t in result.turns] == [610, 910]
    assert result.needed == 910


def test_a_second_turn_that_overflows_fails_the_whole_check():
    # Turn 1 fits (610); turn 2 (910) does not fit in 900.
    result = ptc.check_fit([510, 710], reserve=100, context=900)
    assert result.turns[0].fits
    assert not result.turns[1].fits
    assert not result.fits


def test_no_message_and_no_reserve_are_refused_rather_than_passed():
    with pytest.raises(ptc.CheckError):
        ptc.check_fit([], reserve=100, context=1_000)
    with pytest.raises(ptc.CheckError):
        ptc.check_fit([10], reserve=0, context=1_000)


def test_each_turn_is_counted_from_its_whole_rendered_request():
    # Turn 1: 3 header + 2 tags + 3 words = 8. Turn 2: 8 + 1 empty reply + 2 tags
    # + 1 word = 12, then reply 1 at the reserve (40). Counting the tags and the
    # text as one string, as the tokenizer will see them, is the point.
    with tempfile.TemporaryDirectory() as tmp:
        spec = _spec_for(_tok_dir(tmp), context=1_000, max_output=40)
        for i, text in enumerate(["one two three", "four"], 1):
            _write(os.path.join(tmp, f"m{i}.txt"), text)
        result = ptc.run(spec, os.path.join(tmp, "tok"),
                         [os.path.join(tmp, "m1.txt"), os.path.join(tmp, "m2.txt")],
                         reserve=40, counter_factory=_words, out=io.StringIO())
        assert [t.prompt_tokens for t in result.turns] == [8, 12 + 40]
        assert result.needed == 12 + 40 + 40


# --- the pinned tokenizer -------------------------------------------------


def test_every_pinned_file_carries_a_full_sha256():
    hexdigits = set("0123456789abcdef")
    for key, spec in ptc.MODELS.items():
        assert ptc.TOKENIZER_FILE in spec.files, key
        assert len(spec.hf_revision) == 40 and set(spec.hf_revision) <= hexdigits, key
        for name, digest in spec.files.items():
            assert len(digest) == 64 and set(digest) <= hexdigits, (key, name, digest)


def test_lagunas_renderer_writes_the_templates_frame_around_each_message():
    # The frame of chat_template.jinja at e80da38, for user messages only, as
    # rendered by the template itself on 29 September 2026. A change to it is a
    # change to what is counted, and should be deliberate.
    render = ptc.MODELS["laguna-s-2.1"].render
    head = ("\u3008|EOS|\u3009<system>You are a helpful, conversationally-fluent "
            "assistant made by Poolside. You are here to be helpful to users "
            "through natural language conversations.</system>\n")
    assert render(["A\r\nB"]) == head + "<user>A\r\nB</user>\n<assistant><think>"
    assert render(["A", "C"]) == (head + "<user>A</user>\n"
                                  "<assistant><think></think></assistant>\n"
                                  "<user>C</user>\n<assistant><think>")


def test_a_tokenizer_file_that_does_not_match_its_hash_is_refused():
    with tempfile.TemporaryDirectory() as tmp:
        _write(os.path.join(tmp, "tokenizer.json"), "{}")
        spec = _spec_for(tmp, context=1_000, max_output=10)
        ptc.verify_tokenizer_dir(spec, tmp)  # matches as pinned
        _write(os.path.join(tmp, "tokenizer.json"), "{ }")
        with pytest.raises(ptc.CheckError) as info:
            ptc.verify_tokenizer_dir(spec, tmp)
        assert "tokenizer.json: SHA-256" in str(info.value)


def test_a_missing_tokenizer_file_is_refused():
    with tempfile.TemporaryDirectory() as tmp:
        _write(os.path.join(tmp, "tokenizer.json"), "{}")
        _write(os.path.join(tmp, "chat_template.jinja"), "x")
        spec = _spec_for(tmp, context=1_000, max_output=10)
        os.remove(os.path.join(tmp, "chat_template.jinja"))
        with pytest.raises(ptc.CheckError) as info:
            ptc.verify_tokenizer_dir(spec, tmp)
        assert "chat_template.jinja: missing" in str(info.value)


# --- the command line -----------------------------------------------------


def _main(tmp, spec, messages, extra=()):
    paths = []
    for i, text in enumerate(messages, 1):
        path = os.path.join(tmp, f"message{i}.txt")
        _write(path, text)
        paths.append(path)
    argv = ["--model", "test", "--tokenizer-dir", os.path.join(tmp, "tok")]
    for path in paths:
        argv += ["--message", path]
    out = io.StringIO()
    code = ptc.main(argv + list(extra), models={"test": spec},
                    counter_factory=_words, out=out)
    return code, out.getvalue()


def _tok_dir(tmp):
    tok = os.path.join(tmp, "tok")
    os.makedirs(tok)
    _write(os.path.join(tok, "tokenizer.json"), "{}")
    return tok


def test_the_command_exits_0_when_the_package_fits():
    with tempfile.TemporaryDirectory() as tmp:
        spec = _spec_for(_tok_dir(tmp), context=100, max_output=40)
        code, text = _main(tmp, spec, ["one two three"])  # 8 rendered + 40 = 48
        assert code == 0, text
        assert "FITS -- 52 tokens to spare" in text


def test_the_command_exits_1_and_says_refuse_when_the_package_does_not_fit():
    with tempfile.TemporaryDirectory() as tmp:
        spec = _spec_for(_tok_dir(tmp), context=47, max_output=40)
        code, text = _main(tmp, spec, ["one two three"])  # 48 > 47
        assert code == 1, text
        assert "DOES NOT FIT -- 1 tokens over. Refuse the send." in text


def test_the_reserve_defaults_to_the_models_maximum_output():
    with tempfile.TemporaryDirectory() as tmp:
        spec = _spec_for(_tok_dir(tmp), context=48, max_output=40)
        assert _main(tmp, spec, ["one two three"])[0] == 0
        # A smaller reserve given explicitly is used as given.
        spec = _spec_for(os.path.join(tmp, "tok"), context=20, max_output=40)
        assert _main(tmp, spec, ["one two three"], ["--reserve", "12"])[0] == 0
        assert _main(tmp, spec, ["one two three"], ["--reserve", "13"])[0] == 1


def test_the_command_exits_2_and_counts_nothing_with_the_wrong_tokenizer():
    counted = []

    def spy(spec, directory):
        counted.append(directory)
        return _words(spec, directory)

    with tempfile.TemporaryDirectory() as tmp:
        spec = _spec_for(_tok_dir(tmp), context=1_000, max_output=40)
        _write(os.path.join(tmp, "tok", "tokenizer.json"), "{ }")
        _write(os.path.join(tmp, "m.txt"), "one")
        out = io.StringIO()
        code = ptc.main(["--model", "test", "--tokenizer-dir", os.path.join(tmp, "tok"),
                         "--message", os.path.join(tmp, "m.txt")],
                        models={"test": spec}, counter_factory=spy, out=out)
        assert code == 2, out.getvalue()
        assert out.getvalue().startswith("CHECK NOT MADE:")
        assert counted == []


def test_a_message_is_counted_from_its_bytes_newlines_untouched():
    seen = []

    def spy(spec, directory):
        def count(text):
            seen.append(text)
            return 1
        return count

    with tempfile.TemporaryDirectory() as tmp:
        spec = _spec_for(_tok_dir(tmp), context=1_000, max_output=40)
        path = os.path.join(tmp, "m.txt")
        with open(path, "wb") as fh:
            fh.write(b"a\r\nb\n")
        ptc.main(["--model", "test", "--tokenizer-dir", os.path.join(tmp, "tok"),
                  "--message", path], models={"test": spec}, counter_factory=spy,
                 out=io.StringIO())
        # Counted once alone (for the report) and once inside its turn's request.
        assert seen == [_render(["a\r\nb\n"]), "a\r\nb\n"]
