#!/usr/bin/env python3
"""
Where a document build script writes, and where it reads from.

WHY THIS FILE EXISTS

Every `build_*.py` script in this directory except one hardcoded its output to
`/tmp/outputs/` -- an absolute Linux path that exists on no machine this
project is developed on and is nowhere in this repository. The consequence was
not untidiness. **No build script could write into the repository.**
Regenerating a document meant running the script in a sandbox, finding the file
in /tmp, carrying it across by hand and committing it, which is exactly the
shape of task that does not get done at the end of a session. The Engineering
Notes fell behind at four consecutive handovers and stood eight entries in
arrears when this was found on 6 September 2026 -- found by auditing the
document set, not by anyone reading these scripts.

Rule 28: where a mistake cannot be undone, change the structure rather than
writing an instruction to be careful. `docs/build/README.md` carried precisely
that instruction -- "change it to wherever you want the PDF" -- and it is
removed with this change. A script that has no path of its own cannot write to
the wrong one.

THE MODEL FOR THIS WAS ALREADY IN THIS DIRECTORY

`build_audit_package.py` resolves its output repo-relative from `__file__`
(line 47), and that is why its three manifests verify byte-for-byte against
their recorded build commits while the PDFs beside them were carried across by
hand. This module is that resolver, extracted so the other nine share one.

WHY `__file__` AND NOT THE WORKING DIRECTORY

The README documents running these from inside `docs/build/`; they have also
been run from the repository root. A path built from `os.getcwd()` would put
the PDF in a different place depending on which of the two the operator did,
which is a second version of the defect this file exists to remove. `__file__`
gives the same answer from either directory, and on either platform.

TWO SCRIPTS CANNOT BE FIXED BY REPOINTING THE OUTPUT

`build_findings_bundle.py` and `build_remediation_plan.py` also READ source
material -- the verbatim round-1 auditor outputs -- which has never been in
this repository. Repointing their output does not make them runnable, and
pretending otherwise would leave two scripts that fail somewhere inside
reportlab setup with a bare `FileNotFoundError` naming a directory in /tmp.
They now call `require_source()` below and exit with a message that says what
is missing and that its absence is the known state, not a broken path.

That is an honest failure rather than a fixed script. It is recorded as such in
docs/PHASE7_HISTORY.md, "No build script can write into this repository" (moved
there from PHASE7_NEXT.md on 18 September 2026), rather than presented as
remediation.
"""

import os
import sys

# docs/build/_output.py -> docs/build -> docs -> the repository root.
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Built documents live in docs/, beside the sources that describe them.
DOCS_DIR = os.path.join(REPO_ROOT, "docs")


def _is_a_path_rather_than_a_filename(name):
    """True when `name` is anything other than a bare filename.

    Deliberately does not lean on `os.path.isabs` alone. `isabs("C:\\x.pdf")`
    is False on Linux and True on Windows, and a check whose verdict depends on
    which platform ran it is not a check -- the log-directory guard of
    6 September was verified green on Linux and failed on Windows for that
    exact reason. Every clause below reads the string, so both platforms agree.
    """
    return (
        os.path.isabs(name)
        or name.startswith("/")
        or name.startswith("\\")
        or "/" in name
        or "\\" in name
        or (len(name) > 1 and name[1] == ":")
    )


def output_path(filename):
    """The absolute path, inside this repository, for a built document.

    `filename` is a bare filename. A path is rejected rather than joined,
    because the point of this module is that a build script does not choose
    where in the filesystem it writes.
    """
    if not filename or _is_a_path_rather_than_a_filename(filename):
        raise ValueError(
            "output_path() takes a bare filename, not a path: %r. "
            "Build scripts write into docs/ and choose nothing else." % (filename,)
        )
    os.makedirs(DOCS_DIR, exist_ok=True)
    return os.path.join(DOCS_DIR, filename)


def source_path(*parts):
    """The absolute path, inside this repository, of build source material.

    Used by the two scripts that read something other than their own source.
    Nothing is created here: a source that is absent is the caller's problem
    and `require_source()` is how it is reported.
    """
    for part in parts:
        if not part or _is_a_path_rather_than_a_filename(part):
            raise ValueError(
                "source_path() takes bare path segments, not a path: %r" % (part,)
            )
    return os.path.join(DOCS_DIR, *parts)


def require_source(path, document, what_is_missing):
    """Exit early, and say why, when source material is not in this repository.

    Returns `path` when it exists, so a caller can assign through it.
    """
    if os.path.exists(path):
        return path

    sys.stderr.write(
        "\n"
        "%s cannot be built from this repository.\n"
        "\n"
        "  missing: %s\n"
        "  %s\n"
        "\n"
        "This is not a mistyped path. The source material has never been in\n"
        "this repository, so this document cannot be regenerated by anyone\n"
        "from here. See docs/PHASE7_HISTORY.md, \"No build script can write\n"
        "into this repository\".\n"
        "\n" % (document, path, what_is_missing)
    )
    raise SystemExit(2)
