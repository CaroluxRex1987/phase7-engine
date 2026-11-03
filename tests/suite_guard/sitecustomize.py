"""
The suite's watch on the engine's real log directory -- one process at a time.

ENTRY 59, 3 November 2026 (found 2 November, landing `1b82ed0`)

Until this file, the guard in tests/test_real_log_directory_untouched.py
compared the real `logs/` folder with a snapshot taken when the suite started,
and failed on any file created, removed or changed in size. Since 17 October
the scheduled task runs the engine into that same folder every four hours, at
minute 05. A suite run spanning one of its runs failed the guard on the task's
own records -- `1b82ed0`'s `run_tests.py` step, 862 / 1 / 31 -- and said a
test had reached the engine's record when none had. A folder cannot say who
wrote to it.

So the guard no longer asks the folder. It asks the processes. Python raises
an audit event (PEP 578) before every file open, delete, rename, mkdir and
rmtree, in the process doing it; a hook installed here sees each one with its
path, and records those that would change something inside a real log
directory. The suite's process and every Python process it starts carry the
hook; the scheduled task does not, because it is not started by the suite.
What the task writes is therefore never recorded, and what a test writes is
recorded whenever it happens -- including while the task is running.

It also sees what the snapshot could not: a file rewritten to the same size,
and a directory deleted and rebuilt byte for byte (the old guard's docstring
named both as limits).

HOW IT REACHES THE SUITE'S CHILD PROCESSES

This file is named `sitecustomize` so that Python imports it at startup in any
process whose path holds this folder. tests/conftest.py puts the folder on
PYTHONPATH in its own environment, which every child the suite starts
inherits, and names the watched roots and the report file in two variables.
In the suite's process conftest loads this file under another name and calls
`install` itself. A process started without those variables -- the scheduled
task, a hand run -- does nothing here at all.

WHAT IT CANNOT SEE, stated:

  - a process that is not Python (git, sh): none the suite starts writes to a
    log directory, and those started with the repository as their folder run
    read-only git commands (checked 3 November 2026 by reading every
    subprocess call in tests/);
  - a Python child started with -I, -E or -S, or with an environment built
    without PYTHONPATH: no test does either (same check);
  - an operation given relative to an open directory (`dir_fd`): rmtree's
    inner deletions are, but rmtree raises its own event with the full path
    first, which is caught;
  - anything written before conftest is imported, which is before any test.

The guard test reads the report when it runs, so, like the snapshot before
it, it sees what was done before it ran and nothing after: order-dependent,
and still not the guarantee, which is conftest's redirection.

No fixtures, no third-party imports: this runs inside every child at startup.
"""

import json
import os
import sys

ENV_ROOTS = "PHASE7_SUITE_GUARD_ROOTS"
ENV_REPORT = "PHASE7_SUITE_GUARD_REPORT"

# A directory directly under a watched root whose name lowercases to this is a
# real log directory. Lowercased, so a Linux run sees what a Windows run would:
# `Logs/` and `logs/` are one folder there (6 September 2026, conftest).
LOG_DIR_NAMES = frozenset({"logs"})

# Event -> the positions of its path arguments, and of its dir_fd if it takes
# one. `open` is handled separately: it changes nothing unless its flags write.
_PATH_EVENTS = {
    "os.remove": ((0,), 1),
    "os.rmdir": ((0,), 1),
    "os.mkdir": ((0,), 2),
    "os.rename": ((0, 1), 2),     # os.replace raises this one too
    "os.truncate": ((0,), None),
    "os.utime": ((0,), 3),
    "os.link": ((1,), 3),
    "os.symlink": ((1,), 2),
    "shutil.rmtree": ((0,), 1),
}

_WRITE_FLAGS = 0
for _name in ("O_WRONLY", "O_RDWR", "O_APPEND", "O_CREAT", "O_TRUNC", "O_EXCL"):
    _WRITE_FLAGS |= getattr(os, _name, 0)

_state = {"roots": [], "report": None, "busy": False, "installed": False}


def _norm(path):
    return os.path.normcase(os.path.realpath(path))


def guarded(path, roots, cwd=None):
    """
    The watched root and the path relative to it when `path` lies in a real
    log directory under one of `roots` (or is one), else None.

    A relative path is taken against `cwd`, the process's folder by default,
    which is what the operation itself does. The relative path is reported
    as `os.path.normcase` gives it: lowercased on Windows, which does not
    tell `Logs` from `logs`, and unchanged on Linux.
    """
    if isinstance(path, int) or path is None:
        return None
    try:
        path = os.fsdecode(os.fspath(path))
    except TypeError:
        return None
    if not os.path.isabs(path):
        path = os.path.join(cwd if cwd is not None else os.getcwd(), path)
    target = _norm(path)
    for root in roots:
        base = _norm(root)
        try:
            rel = os.path.relpath(target, base)
        except ValueError:          # another drive, on Windows
            continue
        first = rel.split(os.sep, 1)[0]
        if first.lower() in LOG_DIR_NAMES:
            return root, rel.replace(os.sep, "/")
    return None


def writes(event, args):
    """The paths an audit event would change, or an empty list."""
    if event == "open":
        path, _mode, flags = args
        if isinstance(flags, int) and flags & _WRITE_FLAGS:
            return [path]
        return []
    spec = _PATH_EVENTS.get(event)
    if spec is None:
        return []
    positions, dir_fd_at = spec
    if dir_fd_at is not None and len(args) > dir_fd_at:
        dir_fd = args[dir_fd_at]
        if dir_fd is not None and dir_fd != -1:
            return []
    return [args[i] for i in positions if i < len(args)]


def _hook(event, args):
    if event != "open" and event not in _PATH_EVENTS:
        return
    if _state["busy"] or not _state["roots"]:
        return
    _state["busy"] = True
    try:
        for path in writes(event, args):
            hit = guarded(path, _state["roots"])
            if hit is None:
                continue
            if event == "os.mkdir" and os.path.isdir(path):
                continue            # exist_ok on a folder that is there
            root, rel = hit
            entry = {
                "pid": os.getpid(),
                "event": event,
                "root": root,
                "path": rel,
                "test": os.environ.get("PYTEST_CURRENT_TEST"),
            }
            report = _state["report"]
            if report:
                with open(report, "a", encoding="utf-8") as fh:
                    fh.write(json.dumps(entry) + "\n")
    except Exception:
        # An audit hook that raises aborts the operation it was told of. The
        # guard must never be the reason a test's file operation fails.
        pass
    finally:
        _state["busy"] = False


def install(roots, report):
    """Watch `roots`, reporting to `report`. One hook per process, ever."""
    _state["roots"] = list(roots)
    _state["report"] = report
    if not _state["installed"]:
        sys.addaudithook(_hook)
        _state["installed"] = True


def watch(root):
    """Add a root for the length of a negative control; returns a remover."""
    _state["roots"].append(root)

    def stop():
        if root in _state["roots"]:
            _state["roots"].remove(root)
    return stop


def read_report(report, root=None):
    """Every entry in `report`, or those under `root`."""
    if not report or not os.path.exists(report):
        return []
    with open(report, encoding="utf-8") as fh:
        entries = [json.loads(line) for line in fh if line.strip()]
    if root is None:
        return entries
    return [e for e in entries if _norm(e["root"]) == _norm(root)]


def _install_from_environment():
    roots = [r for r in os.environ.get(ENV_ROOTS, "").split(os.pathsep) if r]
    report = os.environ.get(ENV_REPORT)
    if roots and report:
        install(roots, report)


def _chain_other_sitecustomize():
    """Run the sitecustomize this file shadows, if the interpreter has one."""
    import importlib.machinery
    import importlib.util

    here = _norm(os.path.dirname(os.path.abspath(__file__)))
    rest = [p for p in sys.path if _norm(p or os.curdir) != here]
    spec = importlib.machinery.PathFinder.find_spec("sitecustomize", rest)
    if spec is None or spec.loader is None:
        return
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)


if __name__ == "sitecustomize":
    _install_from_environment()
    _chain_other_sitecustomize()
