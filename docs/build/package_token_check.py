#!/usr/bin/env python3
"""Pre-send token check: does the audit package fit the auditor's context?

WHAT RULED IT

PHASE7_DECISIONS.md, "Ruling, 26 September 2026 -- the pre-send token check is
audit preparation, not an engine item": the check measures the audit package
with the chosen auditor's own tokenizer and refuses the send if the package plus
an output reserve does not fit the model's context. It is item 2 of the
preparation list for the audit ruled on 29 September 2026 (Laguna S 2.1, pinned
to Poolside, the full package in one session).

WHY A TOKENIZER AND NOT A CHARACTER COUNT

Every size this project has quoted for an audit package so far was a count of
bytes or characters divided by four: "~400K+" until 29 September, then "about
700K" at `ec4e5fd` and "about 515K" with the commit messages cut
(PHASE7_DECISIONS.md, the ruling of 29 September on the auditor). A ratio is an
assumption about the text, and code does not tokenize like prose. It cannot tell
a package that fits from one that will be cut off, which is the one thing this
check is for.

WHY THE TOKENIZER FILES ARE PINNED BY HASH

A check run with the wrong tokenizer prints a confident number about the wrong
model. That is easy to do here: Poolside's Laguna XS 2.1 ships a tokenizer of the
same family under the same file names, and Laguna S 2.1's own tokenizer.json was
changed after release (Poolside's commit 88796b9, "Mark </assistant> (token 24)
as special in tokenizer.json"). So each model entry below names the Hugging Face
revision its files were downloaded at and the SHA-256 of every file, and the
check refuses a folder whose files do not match. The safe action is then the
only one available; nobody has to remember which download is the right one.

The files are kept outside this repository, in the folder of project files that
are not in it, and the path is passed on the command line. They are Poolside's
files, not the project's; the hashes below are what ties them to this check.

WHAT IT COUNTS

The request that has to fit is the LAST one of the conversation. Each turn's
request is rendered the way the model's own chat template renders it -- its
opening token, its default system prompt, the tags around every message, and
the opening of the reply -- and the whole string is counted, so the tags and
the text beside them are counted together, as the tokenizer will see them.
Earlier replies are rendered empty and counted separately, at the full output
reserve each, because a reply's length cannot be known before it is written and
a reasoning model spends part of it thinking. That makes the check the worst
case, not a forecast. With one message it is: template + message + reserve.

A request fits when prompt + reserve <= context, the same comparison a provider
makes when it accepts or refuses `max_tokens`.

The template is not run here: it uses a tag (`{% generation %}`) that only the
`transformers` library understands, and this tool should need nothing but a
tokenizer. Each model entry carries a renderer that writes the same string for
the one case the send uses -- user messages only, no system message, no tools,
the template's defaults otherwise. The template file is pinned by hash with the
rest, so the renderer cannot silently fall out of step with it: a changed
template is a refused check, not a wrong count.

WHAT IT CANNOT KNOW

The provider may count differently: a serving template newer than the pinned
one, a system prompt of its own. OpenRouter reports the provider's own count
after a send (`native_tokens_prompt`, which send_audit_round.py writes to
run_metadata.json). Comparing that with this check's count for the same
payload is how this tool is itself checked.

It sends nothing, opens no network connection and writes nothing.

Usage (from the repository root):

    pip install tokenizers==0.23.2
    python docs/build/package_token_check.py --tokenizer-dir <folder> --message <file>

Repeat --message once per user message, in the order they are sent.
Exit status: 0 fits, 1 does not fit, 2 the check could not be made.
"""

import argparse
import hashlib
import os
import sys
from dataclasses import dataclass, field
from typing import Callable


@dataclass(frozen=True)
class ModelSpec:
    name: str
    hf_repo: str
    hf_revision: str
    context_tokens: int
    max_output_tokens: int
    # (user messages) -> the text of the request for the last of them, as the
    # model's chat template writes it, with every earlier reply left empty.
    render: Callable
    # {file name: SHA-256 of its bytes}. Every file listed must be present and
    # match; the tokenizer is loaded from TOKENIZER_FILE.
    files: dict = field(default_factory=dict)


TOKENIZER_FILE = "tokenizer.json"

# Laguna S 2.1's chat_template.jinja at e80da38, written out for the case the
# send uses. With no system message the template supplies this one; with thinking
# on (its default) a reply opens with <think>. Checked against the template itself
# rendered by jinja2 on 29 September 2026, for one message and for two with an
# empty reply between (the commit that adds this file).
_LAGUNA_SYSTEM = ("You are a helpful, conversationally-fluent assistant made by "
                  "Poolside. You are here to be helpful to users through natural "
                  "language conversations.")


def _render_laguna(user_messages):
    parts = ["〈|EOS|〉", "<system>", _LAGUNA_SYSTEM, "</system>\n"]
    for i, text in enumerate(user_messages):
        if i:
            parts.append("<assistant><think></think></assistant>\n")
        parts.append("<user>" + text + "</user>\n")
    parts.append("<assistant><think>")
    return "".join(parts)


MODELS = {
    "laguna-s-2.1": ModelSpec(
        name="Laguna S 2.1",
        hf_repo="poolside/Laguna-S-2.1",
        hf_revision="e80da38da3ed4c4e56888cc1ba39582946a164ba",
        # 1,048,576 context and 131,072 output: OpenRouter's model page, read
        # 29 September 2026 (PHASE7_DECISIONS.md, the six questions before the
        # send); the context also on Poolside's model card. The live models API
        # query is still owed at the send (preparation list, item 1).
        context_tokens=1_048_576,
        max_output_tokens=131_072,
        render=_render_laguna,
        files={
            "chat_template.jinja":
                "444819b8ad4612870827ac05b9147fe9e3344d3850cae8c2790898fc514099ff",
            "tokenizer.json":
                "809240f7a182cde859a4fc4ebc902e619a173d507e99304c1092aa04e7a6658e",
            "tokenizer_config.json":
                "8103b5dd4baf13b38ee927370fbfeab2b1378457efaa233d1c5f0410c40dc9f9",
        },
    ),
}


class CheckError(Exception):
    """The check could not be made. Never a verdict about the package."""


@dataclass(frozen=True)
class Turn:
    number: int
    prompt_tokens: int
    needed_tokens: int
    fits: bool


@dataclass(frozen=True)
class FitResult:
    reserve: int
    context: int
    turns: tuple

    @property
    def needed(self):
        return self.turns[-1].needed_tokens

    @property
    def margin(self):
        return self.context - self.needed

    @property
    def fits(self):
        return all(turn.fits for turn in self.turns)


def _sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_tokenizer_dir(spec, directory):
    """Refuse unless every pinned file is present and hashes to its pinned value."""
    if not os.path.isdir(directory):
        raise CheckError(f"tokenizer folder not found: {directory}")
    problems = []
    for name, expected in sorted(spec.files.items()):
        path = os.path.join(directory, name)
        if not os.path.isfile(path):
            problems.append(f"{name}: missing")
            continue
        actual = _sha256_file(path)
        if actual != expected:
            problems.append(f"{name}: SHA-256 {actual}, expected {expected}")
    if problems:
        raise CheckError(
            f"the files in {directory} are not {spec.name}'s tokenizer at "
            f"{spec.hf_repo}@{spec.hf_revision[:7]}:\n  " + "\n  ".join(problems)
            + "\nRefusing to count with a tokenizer this check was not pinned to.")


def load_counter(spec, directory):
    """A function text -> token count, from the model's own tokenizer.json.

    Nothing is added to the text: the rendered request already carries the
    template's opening token, so adding special tokens here would count it twice.
    """
    try:
        from tokenizers import Tokenizer
    except ImportError:
        raise CheckError(
            "the `tokenizers` package is not installed. It is documentation "
            "tooling, not an engine dependency, so it is not in requirements.txt:\n"
            "    pip install tokenizers==0.23.2")
    tokenizer = Tokenizer.from_file(os.path.join(directory, TOKENIZER_FILE))

    def count(text):
        return len(tokenizer.encode(text, add_special_tokens=False).ids)

    return count


def check_fit(rendered_tokens, reserve, context):
    """Pure arithmetic. `rendered_tokens[k-1]` is turn k's request as rendered,
    earlier replies empty. Each earlier reply is then counted at the full
    reserve, and the turn fits when that plus room for its own reply is within
    the context."""
    rendered_tokens = tuple(rendered_tokens)
    if not rendered_tokens:
        raise CheckError("no message to check")
    if reserve <= 0:
        raise CheckError(f"the output reserve must be positive, got {reserve}")
    turns = []
    for k, rendered in enumerate(rendered_tokens, 1):
        prompt = rendered + (k - 1) * reserve
        needed = prompt + reserve
        turns.append(Turn(k, prompt, needed, needed <= context))
    return FitResult(reserve, context, tuple(turns))


def _read_text(path):
    # Bytes as the send reads them: UTF-8, newlines untouched. A CRLF file on
    # Windows tokenizes differently from its LF copy on Linux, and what counts
    # is the bytes on the machine that sends.
    with open(path, "rb") as fh:
        raw = fh.read()
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise CheckError(f"{path} is not valid UTF-8: {exc}")


def report(spec, paths, texts, message_tokens, result, out=sys.stdout):
    w = out.write
    w(f"model          {spec.name}  ({spec.hf_repo} @ {spec.hf_revision[:7]})\n")
    w(f"context        {result.context:>11,} tokens\n")
    w(f"reserve        {result.reserve:>11,} tokens for each reply\n")
    for i, (path, text, tokens) in enumerate(zip(paths, texts, message_tokens), 1):
        ratio = len(text) / tokens if tokens else 0.0
        w(f"message {i:<6} {tokens:>11,} tokens  {len(text):>11,} chars  "
          f"{ratio:4.2f} chars/token  {path}\n")
    for turn in result.turns:
        state = "fits" if turn.fits else "DOES NOT FIT"
        w(f"turn {turn.number:<9} {turn.prompt_tokens:>11,} prompt + reserve = "
          f"{turn.needed_tokens:>11,}  {state}\n")
    if result.fits:
        w(f"VERDICT        FITS -- {result.margin:,} tokens to spare "
          f"({result.margin / result.context:.1%} of the context)\n")
    else:
        w(f"VERDICT        DOES NOT FIT -- {-result.margin:,} tokens over. "
          f"Refuse the send.\n")


def run(spec, tokenizer_dir, message_paths, reserve, counter_factory=load_counter,
        out=sys.stdout):
    verify_tokenizer_dir(spec, tokenizer_dir)
    count = counter_factory(spec, tokenizer_dir)
    texts = [_read_text(p) for p in message_paths]
    rendered = [count(spec.render(texts[:k])) for k in range(1, len(texts) + 1)]
    result = check_fit(rendered, reserve, spec.context_tokens)
    report(spec, message_paths, texts, [count(t) for t in texts], result, out=out)
    return result


def main(argv=None, models=None, counter_factory=load_counter, out=sys.stdout):
    models = MODELS if models is None else models
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--model", default="laguna-s-2.1", choices=sorted(models))
    parser.add_argument("--tokenizer-dir", required=True,
                        help="the folder holding the model's pinned tokenizer files")
    parser.add_argument("--message", action="append", required=True,
                        help="a file holding one user message, exactly as sent; "
                             "repeat once per message, in order")
    parser.add_argument("--reserve", type=int, default=None,
                        help="tokens kept free for each reply (default: the "
                             "model's maximum output)")
    args = parser.parse_args(argv)
    spec = models[args.model]
    reserve = spec.max_output_tokens if args.reserve is None else args.reserve
    try:
        result = run(spec, args.tokenizer_dir, args.message, reserve,
                     counter_factory=counter_factory, out=out)
    except CheckError as exc:
        out.write(f"CHECK NOT MADE: {exc}\n")
        return 2
    return 0 if result.fits else 1


if __name__ == "__main__":
    sys.exit(main())
