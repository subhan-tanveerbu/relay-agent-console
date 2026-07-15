# RELAY — Agent Ops Console

A multi-tool AI agent presented as a mission-control dashboard, not a chatbot.
Built for the **Multi-Tool Agent Beginner** assignment (Tool Chaining, Tool
Selection Logic, Error Handling, Sandboxed Code Execution).

![mode](https://img.shields.io/badge/UI-Operations_Console-7C5CFF)
![python](https://img.shields.io/badge/Python-3.10+-29D3C6)
![license](https://img.shields.io/badge/license-MIT-3DDC97)

---

## Why it doesn't look like a chatbot

Most beginner agent projects are a sidebar + a scrolling message list. RELAY
treats the agent as a **system you operate**, not a person you talk to:

- No sidebar, no chat bubbles, no blue-on-white ChatGPT palette.
- A **dashboard grid** — Active Tools, AI Workspace, Execution Monitor,
  Results Panel, Activity History — each with a distinct job.
- The **signature element** is the Execution Monitor rail: every tool call
  becomes a node on a connected trace (like a metro line / circuit path),
  pulsing amber while running and settling into mint or coral when it
  finishes — a visual metaphor for *tool chaining*, not a log dump.

### Design tokens

| Role            | Value                          |
|------------------|--------------------------------|
| Background (ink) | `#0A0D12`                      |
| Panel glass       | `#12161F` → `#171C27` gradient |
| Primary signal    | `#7C5CFF` violet               |
| Secondary signal  | `#29D3C6` teal                 |
| Success           | `#3DDC97` mint                 |
| Error             | `#FF5D5D` coral                |
| Warning / running | `#FFB454` amber                |
| Display type      | Space Grotesk                  |
| Body type         | IBM Plex Sans                  |
| Data / code type  | IBM Plex Mono                  |

All tokens live in one place, `config.py`, and are compiled into CSS by
`components/theme.py` — re-skinning the whole app means editing one dataclass.

---

## Architecture

```
relay-agent-console/
├── app.py                    # Streamlit entry point — layout + wiring only
├── api.py                    # FastAPI service exposing the same orchestrator
├── config.py                 # Design tokens, settings, tool registry metadata
├── requirements.txt
├── agents/
│   └── agent_orchestrator.py # Tool selection + chaining (LLM mode & heuristic mode)
├── tools/
│   ├── calculator.py         # AST-based safe expression evaluator
│   ├── code_executor.py      # Restricted, timed Python sandbox
│   ├── file_reader.py        # txt / csv / pdf / docx ingestion
│   └── web_search.py         # DuckDuckGo (+ optional SerpAPI) lookup
├── components/                # Presentation layer — one responsibility each
│   ├── theme.py               # Design-token → CSS compiler, hides Streamlit chrome
│   ├── header.py               # Brand bar, live status pill, clock
│   ├── tool_panel.py           # Active Tools cards + enable/disable toggles
│   ├── execution_monitor.py    # The signature animated rail
│   ├── results_panel.py        # Final output + source badges
│   ├── activity_history.py     # Scrollable run history filmstrip
│   └── status_badge.py         # Reusable badge factory
└── utils/
    ├── session_state.py       # Typed session_state accessors
    ├── helpers.py              # Intent-detection heuristics, formatting
    └── callbacks.py             # LangChain callback → timeline step adapter
```

Every tool follows the same contract — `run(...) -> {ok, output, meta}` — so
the orchestrator and UI never branch on which tool ran; they branch on the
result shape instead. This is what makes chaining and error handling
uniform across four otherwise-unrelated tools.

---

## Two execution modes

RELAY runs **with or without** an OpenAI key so it's demoable out of the box:

- **Live mode** (`OPENAI_API_KEY` set) — a real LangChain tool-calling agent
  on `gpt-4o` performs tool selection and multi-step chaining itself. A
  `TimelineCallbackHandler` records every `on_tool_start/end/error` event for
  the Execution Monitor.
- **Heuristic mode** (no key) — a deterministic router (`utils/helpers.py`)
  applies the same intent rules an LLM would: code fence → Code Executor,
  arithmetic pattern → Calculator, "search/latest/current" → Web Search,
  file present → File Reader first, then chains into the primary tool. This
  keeps grading/demo frictionless and costs nothing to run.

Set the mode via environment variable:

```bash
export OPENAI_API_KEY=sk-...        # enables live LLM tool-calling
export OPENAI_MODEL=gpt-4o          # optional, this is the default
export SERPAPI_API_KEY=...          # optional, improves web search quality
```

---

## Sandboxed code execution — how it works, and its limits

`tools/code_executor.py` is a **teaching-grade** sandbox:

1. A whitelist of ~25 safe builtins (no `open`, `eval`, `exec`, `__import__`
   passthrough) is injected instead of the real `builtins` module.
2. A custom `__import__` only allows `math`, `statistics`, `random`, `json`,
   `re`, `datetime`, `itertools`, `collections`.
3. A string-pattern pre-check blocks obvious escape attempts (`os.system`,
   `subprocess`, `socket`, `.read(`, etc.) before execution even starts.
4. Code runs in a **daemon thread** with a hard wall-clock timeout
   (`CODE_EXEC_TIMEOUT_SECONDS`, default 5s); if it overruns, the thread is
   abandoned and an error is returned.
5. `stdout` is captured via `contextlib.redirect_stdout`, never the real
   terminal.

**This is not a security boundary** — a sufficiently creative Python
program can still exhaust memory, throw the interpreter into a busy-loop
past the join timeout (thread isn't force-killed), or find gaps in the
string-based pre-check. For a production system, swap this module for a
real isolate: a `subprocess` under `resource.setrlimit` + a container
(gVisor/Firecracker) or a hosted sandbox (Modal, E2B, Daytona). The module
boundary (`tools/code_executor.py:run`) is designed so that swap doesn't
touch any other file.

---

## Error handling, end to end

Every tool returns `{"ok": False, "output": "<human explanation>", "meta":
{"error_type": ...}}` instead of raising — the orchestrator never needs a
bare `except Exception` around tool calls to stay alive, and the UI renders
failures as a coral node + error badge in the same rail as successes,
instead of crashing the run. Failure modes explicitly handled:

- Missing / unsupported / oversized files (`file_reader`)
- Malformed expressions, division by zero, disallowed functions (`calculator`)
- Syntax errors, runtime exceptions, timeouts, blocked operations (`code_executor`)
- Network failures, empty queries, empty result sets (`web_search`)
- Empty task input, LLM/agent invocation failures (`agent_orchestrator`)

---

## Running it

```bash
pip install -r requirements.txt
streamlit run app.py
```

Optional FastAPI layer (reuses the same `agents/` and `tools/` code):

```bash
uvicorn api:app --reload --port 8000
curl -X POST http://localhost:8000/execute -H "Content-Type: application/json" \
     -d '{"query": "sqrt(196) + 12 * 3"}'
```

---

## Extending

- **New tool** → add `tools/<name>.py` with a `run(...)` returning the
  standard contract, register it in `config.TOOL_META`, add it to
  `_TOOL_FUNCS` in `agent_orchestrator.py`, and wire a `StructuredTool` in
  `_build_langchain_tools` for live mode.
- **New panel** → add `components/<name>.py` exposing a `render(...)`
  function; import and call it from `app.py`. Nothing else needs to change.
- **Re-skin** → edit `config.Palette` / `config.Type`; every component reads
  from CSS variables compiled by `components/theme.py`.
