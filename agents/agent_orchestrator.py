"""
agents/agent_orchestrator.py
The brain of RELAY. Exposes a single entry point, `run_task`, which
returns a uniform payload:

    {
        "steps": [ {id, tool, status, detail, duration_ms, ts}, ... ],
        "final_output": str,
        "ok": bool,
        "mode": "live" | "heuristic",
    }

Two execution paths:

  • LIVE mode (OPENAI_API_KEY set) — builds a real LangChain tool-calling
    agent on gpt-4o. The LLM performs tool SELECTION and can CHAIN
    multiple tools across turns; a callback handler records every call.

  • HEURISTIC mode (no key) — a deterministic router applies the same
    tool-selection intent rules an LLM would (see utils/helpers.py) and
    still demonstrates chaining: an uploaded file is always read first,
    then the primary intent tool runs on the combined context. This
    keeps the project fully runnable and demo-able with zero API cost.

Both paths funnel every tool call through _call_tool so error handling
is identical regardless of mode.
"""

import time

from config import LIVE_MODE, OPENAI_MODEL, TOOL_META
from tools import calculator, code_executor, file_reader, web_search
from utils.helpers import looks_like_code, looks_like_math, looks_like_search, looks_like_file, extract_code_block
from utils.callbacks import TimelineCallbackHandler

_TOOL_FUNCS = {
    "calculator": calculator.run,
    "code_executor": code_executor.run,
    "web_search": web_search.run,
    "file_reader": file_reader.run,
}


def _call_tool(tool_key: str, arg, steps: list) -> dict:
    """Execute one tool, appending a step record with real timing + status."""
    start = time.time()
    steps.append({
        "id": f"{tool_key}-{len(steps)}",
        "tool": tool_key,
        "status": "running",
        "detail": str(arg)[:160],
        "duration_ms": 0,
        "ts": time.strftime("%H:%M:%S"),
    })
    try:
        result = _TOOL_FUNCS[tool_key](arg)
    except Exception as exc:  # noqa: BLE001 — tool contract failure is still a result
        result = {"ok": False, "output": f"Unhandled error: {exc}", "meta": {"error_type": type(exc).__name__}}

    duration_ms = int((time.time() - start) * 1000)
    steps[-1]["status"] = "success" if result["ok"] else "error"
    steps[-1]["duration_ms"] = duration_ms
    steps[-1]["detail"] = result["output"][:400]
    return result


# --------------------------------------------------------------------------
# Heuristic router (no LLM required)
# --------------------------------------------------------------------------

def _run_heuristic(query: str, uploaded_file, enabled_tools: dict) -> dict:
    steps = []
    context_chunks = []

    # Tool chaining step 1: always ground on an uploaded file first, if present.
    if uploaded_file is not None and enabled_tools.get("file_reader", True):
        file_result = _call_tool("file_reader", uploaded_file, steps)
        if file_result["ok"]:
            context_chunks.append(file_result["output"])

    # Tool selection logic: priority order mirrors specificity of intent.
    if looks_like_code(query) and enabled_tools.get("code_executor", True):
        result = _call_tool("code_executor", extract_code_block(query), steps)
    elif looks_like_math(query) and enabled_tools.get("calculator", True):
        result = _call_tool("calculator", query, steps)
    elif looks_like_search(query) and enabled_tools.get("web_search", True):
        result = _call_tool("web_search", query, steps)
    elif looks_like_file(query, uploaded_file is not None):
        if context_chunks:
            result = {"ok": True, "output": context_chunks[0], "meta": {}}
        else:
            result = _call_tool("file_reader", uploaded_file, steps)
    else:
        # No confident intent match — fall back to web search as a safe default.
        if enabled_tools.get("web_search", True):
            result = _call_tool("web_search", query, steps)
        else:
            result = {"ok": False, "output": "No enabled tool matched this request.", "meta": {}}

    final_output = result["output"]
    if context_chunks and result is not context_chunks:
        prefix = f"Using {len(context_chunks)} document(s) as context.\n\n"
        final_output = prefix + final_output

    return {
        "steps": steps,
        "final_output": final_output,
        "ok": all(s["status"] != "error" for s in steps) if steps else result["ok"],
        "mode": "heuristic",
    }


# --------------------------------------------------------------------------
# Live LangChain agent (OPENAI_API_KEY set)
# --------------------------------------------------------------------------

def _build_langchain_tools(enabled_tools: dict, uploaded_file):
    from langchain_core.tools import StructuredTool

    tools = []

    if enabled_tools.get("calculator", True):
        tools.append(StructuredTool.from_function(
            func=lambda expression: calculator.run(expression)["output"],
            name="calculator",
            description="Evaluate an arithmetic or math expression, e.g. 'sqrt(144) + 3^2'.",
        ))
    if enabled_tools.get("code_executor", True):
        tools.append(StructuredTool.from_function(
            func=lambda code: code_executor.run(code)["output"],
            name="code_executor",
            description="Execute a short Python snippet in a restricted sandbox and return stdout.",
        ))
    if enabled_tools.get("web_search", True):
        tools.append(StructuredTool.from_function(
            func=lambda query: web_search.run(query)["output"],
            name="web_search",
            description="Search the open web for current information and return top results.",
        ))
    if enabled_tools.get("file_reader", True) and uploaded_file is not None:
        tools.append(StructuredTool.from_function(
            func=lambda _: file_reader.run(uploaded_file)["output"],
            name="file_reader",
            description="Read the single file the user attached to this task and return its text content.",
        ))
    return tools


def _run_live(query: str, uploaded_file, enabled_tools: dict) -> dict:
    from langchain_openai import ChatOpenAI
    from langchain.agents import create_tool_calling_agent, AgentExecutor
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

    tools = _build_langchain_tools(enabled_tools, uploaded_file)
    llm = ChatOpenAI(model=OPENAI_MODEL, temperature=0)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are RELAY, an operations agent with access to tools. "
                   "Select the minimum set of tools needed, chain them if the task "
                   "requires multiple steps (e.g. read a file, then calculate), and "
                   "give a concise final answer."),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)
    handler = TimelineCallbackHandler()
    executor = AgentExecutor(agent=agent, tools=tools, verbose=False, max_iterations=6)

    try:
        response = executor.invoke({"input": query}, config={"callbacks": [handler]})
        final_output = response.get("output", "")
        ok = True
    except Exception as exc:  # noqa: BLE001
        final_output = f"Agent run failed: {exc}"
        ok = False

    # Normalize any lingering "running" steps (e.g. exception mid-tool-call).
    for step in handler.steps:
        if step["status"] == "running":
            step["status"] = "error"
            step["detail"] = "Interrupted before completion."

    return {"steps": handler.steps, "final_output": final_output, "ok": ok, "mode": "live"}


# --------------------------------------------------------------------------
# Public entry point
# --------------------------------------------------------------------------

def run_task(query: str, uploaded_file=None, enabled_tools: dict = None) -> dict:
    enabled_tools = enabled_tools or {k: True for k in TOOL_META}
    query = (query or "").strip()

    if not query:
        return {"steps": [], "final_output": "Enter a task before running the agent.",
                "ok": False, "mode": "idle"}

    if LIVE_MODE:
        try:
            return _run_live(query, uploaded_file, enabled_tools)
        except ImportError:
            pass  # LangChain/OpenAI deps missing — fall through to heuristic mode
    return _run_heuristic(query, uploaded_file, enabled_tools)
