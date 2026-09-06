"""
The document build scripts must write into this repository, not into /tmp.

WHAT THIS IS ABOUT

Nine of the ten `docs/build/build_*.py` scripts hardcoded their output to
`/tmp/outputs/` -- an absolute Linux path nowhere in this repository. No build
script could write into the repository, so every PDF in `docs/` was built in a
sandbox and carried across by hand, and the Engineering Notes fell eight
entries behind across four handovers. Found 6 September 2026 by the document
audit; fixed by `docs/build/_output.py`, which resolves paths from `__file__`.

WHY A TEST AND NOT ONLY THE MODULE

The module makes the safe action the available one for a script that uses it.
It cannot stop the next script from being written with a path of its own, and
the guard that exists for exactly this class -- `test_explicit_configuration`'s
`test_no_module_hardcodes_a_path_config_declares` -- scans with
`all_python_files(include_doc_tooling=False)`, so `docs/` is outside it by
construction. That exclusion has a stated reason, and the reason is about the
dependency manifest: counting reportlab as an engine dependency would break a
fresh install. One flag answers two questions and answers this one wrongly.
This file asks the path-literal question about the directory that flag excludes.

WHY THE PARSE TREE AND NOT THE TEXT

`docs/build/_output.py`'s own docstring contains the string `/tmp/outputs/`,
and so does this file. A text scan would fail on the documentation of the fix.
The scan below reads module-level assignments out of the AST, which is the same
technique `core/code_fingerprint.py` uses and for the same reason: a check
built from text matches things that are not code.
"""

import ast
import contextlib
import importlib.util
import io
import os
import shutil
import tempfile

import pytest

from conftest import REPO_ROOT

BUILD_DIR = os.path.join(REPO_ROOT, "docs", "build")

# The nine that hardcoded an output path. `build_audit_package.py` is the tenth
# `build_*.py` and was never one of them -- it already resolved repo-relative
# from `__file__` (line 47), which is why its manifests verify byte-for-byte
# and is the model `_output.py` was extracted from.
PDF_BUILDERS = [
    "build_audit_instructions.py",
    "build_change_log_standard.py",
    "build_constitution_rev1.py",
    "build_credential_protocol.py",
    "build_engineering_notes.py",
    "build_findings_bundle.py",
    "build_remediation_plan.py",
    "build_roadmap.py",
    "build_tier0_companion.py",
]


def _load_output_module():
    path = os.path.join(BUILD_DIR, "_output.py")
    spec = importlib.util.spec_from_file_location("phase7_docs_build_output", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _looks_absolute(value):
    """A string that names a place in the filesystem rather than a filename.

    Every clause reads the string itself. `os.path.isabs` alone would answer
    differently on Linux and Windows for `C:\\x.pdf`, and a guard whose verdict
    depends on the platform that ran it is not a guard -- the log-directory
    guard of 6 September was green in a Linux sandbox and failed on Windows for
    exactly that reason.
    """
    return (
        value.startswith("/")
        or value.startswith("\\")
        or (len(value) > 1 and value[1] == ":")
    )


def absolute_string_assignments(source):
    """[(line, name, value)] for module-level `NAME = "<absolute path>"`."""
    found = []
    for node in ast.parse(source).body:
        if not isinstance(node, ast.Assign):
            continue
        value = node.value
        if not (isinstance(value, ast.Constant) and isinstance(value.value, str)):
            continue
        if not _looks_absolute(value.value):
            continue
        for target in node.targets:
            name = getattr(target, "id", "?")
            found.append((node.lineno, name, value.value))
    return found


def _source_of(filename):
    with open(os.path.join(BUILD_DIR, filename), encoding="utf-8") as handle:
        return handle.read()


def test_no_docs_build_script_assigns_an_absolute_path():
    """The defect itself: eleven such assignments across nine files."""
    offenders = []
    for filename in sorted(os.listdir(BUILD_DIR)):
        if not filename.endswith(".py"):
            continue
        for line, name, value in absolute_string_assignments(_source_of(filename)):
            offenders.append("%s:%d %s = %r" % (filename, line, name, value))

    assert not offenders, (
        "A build script names an absolute path. It cannot then write into this "
        "repository, which is how the Engineering Notes fell eight entries "
        "behind. Use docs/build/_output.py.\n  " + "\n  ".join(offenders)
    )


def test_the_absolute_path_scan_can_report_a_violation():
    """Negative control.

    The scan above passes on a clean tree, and would also pass if it had been
    written to find nothing at all. This feeds it the pre-fix shape.
    """
    pre_fix = 'OUT = "/tmp/outputs/Phase7_Audit_Findings_Complete.pdf"\n'
    assert absolute_string_assignments(pre_fix) == [
        (1, "OUT", "/tmp/outputs/Phase7_Audit_Findings_Complete.pdf")
    ]

    windows_shape = 'OUTPUT_PATH = "C:\\\\outputs\\\\x.pdf"\n'
    assert len(absolute_string_assignments(windows_shape)) == 1

    assert absolute_string_assignments('OUT = _output.output_path("x.pdf")\n') == []


def test_every_pdf_builder_takes_its_output_from_the_shared_resolver():
    """Not writing to /tmp is not the same as writing to the right place.

    A script could satisfy the scan above with a bare relative filename and
    land its PDF in whatever directory the operator happened to be in -- which
    is the same defect with a different symptom, since the README documents
    running these from two different directories.
    """
    missing = []
    for filename in PDF_BUILDERS:
        tree = ast.parse(_source_of(filename))
        calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "output_path"
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "_output"
        ]
        if not calls:
            missing.append(filename)

    assert not missing, (
        "these builders do not take their output from _output.output_path(): "
        + ", ".join(missing)
    )


def test_output_path_lands_in_the_docs_directory_of_this_repository():
    output = _load_output_module()
    built = output.output_path("Phase7_Engineering_Notes.pdf")

    assert os.path.isabs(built)
    assert os.path.dirname(built) == os.path.join(REPO_ROOT, "docs")
    assert os.path.basename(built) == "Phase7_Engineering_Notes.pdf"


def test_output_path_rejects_a_path_rather_than_a_filename():
    """Including the two shapes that a single-platform check gets wrong."""
    output = _load_output_module()

    for rejected in [
        "/tmp/outputs/x.pdf",
        "C:\\outputs\\x.pdf",
        "sub/x.pdf",
        "..\\x.pdf",
        "",
    ]:
        with pytest.raises(ValueError):
            output.output_path(rejected)


def test_require_source_exits_and_names_what_is_missing():
    """The two scripts whose source material is not in this repository.

    Repointing their output does not make them runnable. What this replaces is
    a bare FileNotFoundError raised somewhere below, naming a /tmp directory,
    on a machine where nothing is wrong.

    Takes no fixtures deliberately: `run_tests.py` calls test functions with no
    arguments, and a test that needs one is counted as an error there. The
    error count is 29 and is watched.
    """
    output = _load_output_module()
    workspace = tempfile.mkdtemp(prefix="phase7_require_source_")
    try:
        absent = os.path.join(workspace, "audit_raw")
        captured = io.StringIO()

        with contextlib.redirect_stderr(captured):
            with pytest.raises(SystemExit) as exit_info:
                output.require_source(
                    absent, "Phase7_Remediation_Plan.pdf", "the reason"
                )

        assert exit_info.value.code == 2
        message = captured.getvalue()
        assert absent in message
        assert "Phase7_Remediation_Plan.pdf" in message
        assert "the reason" in message

        present = os.path.join(workspace, "present.md")
        with open(present, "w", encoding="utf-8") as handle:
            handle.write("x")
        assert output.require_source(present, "doc", "why") == present
    finally:
        shutil.rmtree(workspace, ignore_errors=True)
