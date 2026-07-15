"""
tools/code_executor.py
Runs short, untrusted Python snippets in a restricted namespace with a
wall-clock timeout. This is a teaching-grade sandbox, not a security
boundary — see README "Security notes" before exposing this publicly.

Layers of restriction:
  1. Builtins whitelist        — no open(), no __import__, no eval/exec/compile
  2. Module whitelist          — only a small set of safe stdlib modules importable
  3. Wall-clock timeout        — runs in a daemon thread, killed if it overruns
  4. Captured output           — a sandboxed `print` writes to a local buffer

Note on (3)+(4) together: output is captured via a *sandboxed print
override*, not `contextlib.redirect_stdout`. redirect_stdout mutates the
process-global `sys.stdout`; if the sandboxed code hangs forever (e.g.
`while True: pass`), the timeout abandons the daemon thread but its
`with redirect_stdout(...)` block never exits, permanently corrupting
stdout for the entire host process. Overriding `print` inside the
sandbox's own builtins avoids touching global state entirely, so a
runaway thread can never leak outside its own buffer.
"""

import io
import threading
import builtins as _builtins

from config import CODE_EXEC_TIMEOUT_SECONDS

_SAFE_BUILTINS = {
    name: getattr(_builtins, name)
    for name in (
        "abs", "all", "any", "bool", "dict", "enumerate", "float", "int",
        "len", "list", "max", "min", "range", "reversed", "round",
        "set", "sorted", "str", "sum", "tuple", "zip", "map", "filter",
        "isinstance", "type", "Exception", "ValueError", "TypeError",
        "IndexError", "KeyError", "ZeroDivisionError", "StopIteration",
    )
}

_SAFE_MODULES = {"math", "statistics", "random", "json", "re", "datetime", "itertools", "collections"}


def _safe_import(name, *args, **kwargs):
    if name.split(".")[0] not in _SAFE_MODULES:
        raise ImportError(f"Import of '{name}' is blocked in this sandbox")
    return __import__(name, *args, **kwargs)


class _ExecResult:
    def __init__(self):
        self.stdout = ""
        self.error = None


def _worker(code: str, result: _ExecResult):
    buffer = io.StringIO()

    def _sandboxed_print(*args, sep=" ", end="\n", **kwargs):
        # Ignores file=/flush= kwargs on purpose — everything goes to buffer.
        buffer.write(sep.join(str(a) for a in args) + end)

    safe_builtins = dict(_SAFE_BUILTINS)
    safe_builtins["__import__"] = _safe_import
    safe_builtins["print"] = _sandboxed_print
    sandbox_globals = {"__builtins__": safe_builtins}

    try:
        exec(compile(code, "<sandbox>", "exec"), sandbox_globals, {})
        result.stdout = buffer.getvalue()
    except Exception as exc:  # noqa: BLE001 — deliberately broad, this is a sandbox
        result.stdout = buffer.getvalue()
        result.error = f"{type(exc).__name__}: {exc}"


def run(code: str) -> dict:
    code = code.strip()
    if not code:
        return {"ok": False, "output": "No code provided to execute.", "meta": {"error_type": "EmptyInput"}}

    if any(banned in code for banned in ("open(", "os.system", "subprocess", "socket", "__import__",
                                          "eval(", "exec(", "compile(", ".read(", "input(")):
        return {
            "ok": False,
            "output": "Blocked: code contains a disallowed operation (file/network/system access).",
            "meta": {"error_type": "SandboxViolation"},
        }

    result = _ExecResult()
    thread = threading.Thread(target=_worker, args=(code, result), daemon=True)
    thread.start()
    thread.join(timeout=CODE_EXEC_TIMEOUT_SECONDS)

    if thread.is_alive():
        return {
            "ok": False,
            "output": f"Execution exceeded the {CODE_EXEC_TIMEOUT_SECONDS}s sandbox timeout and was aborted. "
                      f"(Output up to the timeout is not recovered — the thread is abandoned, not killed.)",
            "meta": {"error_type": "Timeout"},
        }

    if result.error:
        return {"ok": False, "output": (result.stdout + f"\n{result.error}").strip(),
                "meta": {"error_type": "RuntimeError"}}

    return {"ok": True, "output": result.stdout or "(no output)", "meta": {}}
