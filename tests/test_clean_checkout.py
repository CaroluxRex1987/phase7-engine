"""
Does the published repository actually run when someone clones it?

This test exists because the answer is currently no, and because that fact is
invisible from Viktor's machine — D:\\phase7_engine has a Logs/ directory that
has been there since the first run, so the failure never appears locally. It
appears for anyone starting from a fresh clone of the public repository.

main.py, at module scope:

    logging.basicConfig(
        handlers=[logging.FileHandler('Logs/phase7_engine.log'), ...]
    )                                                    # line 16

and then, inside main():

    os.makedirs('Logs', exist_ok=True)                   # line 41

logging.FileHandler opens its file eagerly. With no Logs/ directory it raises
FileNotFoundError while the module is still being imported — before main() is
entered, and therefore before the try/except inside main() can catch it, and
before the makedirs call that would have prevented it.

Run 1's blind review found this ordering and described it as a soft failure:
"the logging machinery catches it and prints to stderr, so early log lines
silently miss the file." That is wrong. It is a hard crash on import. The
finding was real and its severity was understated.

Constitution: Tier 3, items 3 and 4.
"""

import os
import shutil
import subprocess
import sys
import tempfile

from conftest import REPO_ROOT


def _copy_repo_without_logs(dest):
    def ignore(directory, names):
        return [n for n in names
                if n in {".git", "__pycache__", "Logs", "logs", "tests",
                         "aider-env", ".venv", "venv"}]
    shutil.copytree(REPO_ROOT, dest, ignore=ignore, dirs_exist_ok=True)


def test_main_imports_without_a_logs_directory():
    """
    Import main.py in a copy of the repository that has no Logs/ directory,
    which is the state of a fresh clone.

    Runs in a subprocess because logging.basicConfig mutates global state and
    a failed handler would contaminate the rest of the suite.
    """
    with tempfile.TemporaryDirectory() as tmp:
        repo = os.path.join(tmp, "engine")
        _copy_repo_without_logs(repo)
        assert not os.path.exists(os.path.join(repo, "Logs"))

        proc = subprocess.run(
            [sys.executable, "-c", "import main"],
            cwd=repo, capture_output=True, text=True, timeout=120,
        )

    if proc.returncode != 0 and "FileNotFoundError" in proc.stderr:
        raise AssertionError(
            "main.py cannot be imported from a fresh clone.\n"
            "logging.FileHandler('Logs/phase7_engine.log') runs at module scope, "
            "before os.makedirs('Logs') inside main().\n"
            "Fix: create the directory before basicConfig, or pass delay=True "
            "to the handler.\n\n"
            + proc.stderr.strip().splitlines()[-1]
        )
    if proc.returncode != 0:
        raise AssertionError(
            "main.py failed to import from a fresh clone for a different "
            "reason:\n" + proc.stderr.strip()
        )


def test_main_runs_without_a_logs_directory():
    """
    The same thing one level up: does `python main.py` get far enough to
    return its own exit code, rather than dying during import?

    A non-zero exit code is acceptable here — with no network the engine
    should fail its data fetch and return 1 through its own error handling.
    What is not acceptable is a traceback, which means it never reached that
    handling at all.
    """
    with tempfile.TemporaryDirectory() as tmp:
        repo = os.path.join(tmp, "engine")
        _copy_repo_without_logs(repo)

        proc = subprocess.run(
            [sys.executable, "main.py"],
            cwd=repo, capture_output=True, text=True, timeout=300,
        )

    assert "Traceback" not in proc.stderr, (
        "main.py raised instead of returning an exit code:\n" + proc.stderr.strip()
    )
