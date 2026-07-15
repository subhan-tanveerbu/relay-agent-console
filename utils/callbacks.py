"""
utils/callbacks.py
A LangChain BaseCallbackHandler that records tool start/end/error
events into a plain list of step dicts — the same shape the heuristic
router produces — so components/execution_monitor.py can render both
execution modes identically.
"""

import time

try:
    from langchain_core.callbacks import BaseCallbackHandler
except ImportError:  # LangChain not installed — handler simply won't be used
    BaseCallbackHandler = object


class TimelineCallbackHandler(BaseCallbackHandler):
    def __init__(self):
        self.steps = []
        self._starts = {}

    def on_tool_start(self, serialized, input_str, run_id=None, **kwargs):
        tool_name = serialized.get("name", "tool")
        self._starts[str(run_id)] = time.time()
        self.steps.append({
            "id": str(run_id)[:8] if run_id else str(len(self.steps)),
            "tool": tool_name,
            "status": "running",
            "detail": str(input_str)[:200],
            "duration_ms": 0,
            "ts": time.strftime("%H:%M:%S"),
        })

    def on_tool_end(self, output, run_id=None, **kwargs):
        self._close(run_id, "success", str(output)[:400])

    def on_tool_error(self, error, run_id=None, **kwargs):
        self._close(run_id, "error", str(error)[:400])

    def _close(self, run_id, status, detail):
        started = self._starts.get(str(run_id), time.time())
        duration_ms = int((time.time() - started) * 1000)
        for step in reversed(self.steps):
            if step["id"] == (str(run_id)[:8] if run_id else str(len(self.steps) - 1)) and step["status"] == "running":
                step["status"] = status
                step["detail"] = detail
                step["duration_ms"] = duration_ms
                break
