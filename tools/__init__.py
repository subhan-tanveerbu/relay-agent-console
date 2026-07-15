"""
tools package
Each module exposes a `run(...)` function with a uniform contract:

    run(...) -> dict(ok: bool, output: str, meta: dict)

so the orchestrator and UI never need tool-specific branching to read
a result.
"""
