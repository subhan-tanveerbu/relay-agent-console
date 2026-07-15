"""
api.py
Optional FastAPI service that exposes the exact same agent orchestrator
used by the Streamlit UI as a REST endpoint. This satisfies the
"FastAPI" technology requirement as a genuine reusable service layer
(agents/tools are framework-agnostic — both app.py and api.py import
the same run_task function) rather than a duplicate implementation.

Run with:  uvicorn api:app --reload --port 8000
Then:      POST http://localhost:8000/execute  {"query": "sqrt(81) + 4"}
"""

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agents.agent_orchestrator import run_task
from config import APP_NAME, TOOL_META

app = FastAPI(title=f"{APP_NAME} API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ExecuteRequest(BaseModel):
    query: str
    enabled_tools: dict | None = None


class ExecuteResponse(BaseModel):
    ok: bool
    mode: str
    final_output: str
    steps: list


@app.get("/health")
def health():
    return {"status": "online", "tools": list(TOOL_META.keys())}


@app.post("/execute", response_model=ExecuteResponse)
def execute(payload: ExecuteRequest):
    """Run a task with no file attachment (JSON-only convenience route)."""
    result = run_task(query=payload.query, uploaded_file=None, enabled_tools=payload.enabled_tools)
    return result


@app.post("/execute-with-file", response_model=ExecuteResponse)
async def execute_with_file(query: str = Form(...), file: UploadFile = File(...)):
    """Run a task with a file attachment, mirroring the Streamlit File Reader flow."""

    class _InMemoryUpload:
        def __init__(self, name: str, content: bytes):
            self.name = name
            self.size = len(content)
            self._content = content

        def getvalue(self):
            return self._content

    content = await file.read()
    upload = _InMemoryUpload(file.filename, content)
    result = run_task(query=query, uploaded_file=upload, enabled_tools=None)
    return result
