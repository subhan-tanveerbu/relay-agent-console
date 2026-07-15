"""
components/execution_monitor.py
The signature visual of RELAY: a vertical execution rail where every
tool invocation is a node connected by a stem line, mirroring a
metro/circuit trace rather than a chat log. Running nodes pulse amber,
finished ones settle into mint (success) or coral (error), and each
node's detail is tucked into a collapsible mono-font log via <details>.
"""

import html
import streamlit as st

from config import TOOL_META
from utils.helpers import escape

_GLYPH = {k: v["glyph"] for k, v in TOOL_META.items()}
_STATUS_SYMBOL = {"success": "✓", "error": "!", "running": "•", "pending": "…"}


def render(steps: list) -> None:
    st.markdown('<div class="panel-eyebrow"><span class="dot"></span>Execution Monitor</div>', unsafe_allow_html=True)

    if not steps:
        st.markdown(
            '<div class="rail-empty">No tool calls yet — run a task to populate the trace.</div>',
            unsafe_allow_html=True,
        )
        return

    items_html = []
    for step in steps:
        tool_key = step["tool"]
        glyph = _GLYPH.get(tool_key, "◇")
        label = TOOL_META.get(tool_key, {}).get("label", tool_key)
        status = step["status"]
        symbol = _STATUS_SYMBOL.get(status, "•")
        duration = f'{step["duration_ms"]} ms' if step.get("duration_ms") else ""
        detail = escape(step.get("detail", ""))

        items_html.append(f"""
        <div class="rail-item">
            <div class="stem"></div>
            <div class="rail-node {status}">{symbol}</div>
            <div class="rail-body">
                <div class="rail-top">
                    <span style="opacity:.7">{glyph}</span>
                    <span class="rail-tool">{label}</span>
                    <span class="badge {status}">{status}</span>
                    <span class="rail-time">{step.get('ts','')} · {duration}</span>
                </div>
                <details class="log-expand">
                    <summary>view log ▾</summary>
                    <div class="rail-detail">{detail}</div>
                </details>
            </div>
        </div>
        """)

    st.markdown(f'<div class="rail">{"".join(items_html)}</div>', unsafe_allow_html=True)
