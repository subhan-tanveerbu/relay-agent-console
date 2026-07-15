"""
utils/session_state.py
Typed helpers around st.session_state so the rest of the app never
touches raw dict keys. Keeps app.py readable and avoids key-name typos.
"""

import time
import uuid
import streamlit as st

from config import MAX_HISTORY_ITEMS


def init_state() -> None:
    """Populate session_state with defaults on first run."""
    defaults = {
        "runs": [],                 # list of completed run records (Activity History)
        "current_steps": [],        # steps of the run currently rendered (Execution Monitor)
        "current_result": None,     # ResultPayload of the latest run
        "is_running": False,
        "enabled_tools": {
            "file_reader": True,
            "calculator": True,
            "code_executor": True,
            "web_search": True,
        },
        "uploaded_file": None,
        "run_counter": 0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def new_run_id() -> str:
    st.session_state.run_counter += 1
    return f"run-{st.session_state.run_counter:03d}"


def push_run(record: dict) -> None:
    """Store a finished run at the front of history, capped in length."""
    st.session_state.runs.insert(0, record)
    st.session_state.runs = st.session_state.runs[:MAX_HISTORY_ITEMS]


def make_step(tool_key: str, status: str, detail: str = "", duration_ms: int = 0) -> dict:
    return {
        "id": str(uuid.uuid4())[:8],
        "tool": tool_key,
        "status": status,          # pending | running | success | error
        "detail": detail,
        "duration_ms": duration_ms,
        "ts": time.strftime("%H:%M:%S"),
    }
