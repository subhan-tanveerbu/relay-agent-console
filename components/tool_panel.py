"""
components/tool_panel.py
Renders the "Active Tools" column: one card per registered tool with
its glyph, blurb and an enable/disable toggle. Toggling here writes
straight into session_state and is respected by the orchestrator on
the next run — this is the tool SELECTION surface the user controls
directly, distinct from the agent's own automatic selection logic.
"""

import streamlit as st
from config import TOOL_META


def render() -> None:
    st.markdown('<div class="panel-eyebrow"><span class="dot"></span>Active Tools</div>', unsafe_allow_html=True)

    for key, meta in TOOL_META.items():
        enabled = st.session_state.enabled_tools.get(key, True)
        card_class = "tool-card" if enabled else "tool-card disabled"
        dot_class = "tool-dot" if enabled else "tool-dot off"
        status_label = "ready" if enabled else "disabled"

        st.markdown(
            f"""
            <div class="{card_class}">
                <div class="tool-glyph">{meta['glyph']}</div>
                <div style="flex:1;">
                    <div class="tool-name">{meta['label']}</div>
                    <div class="tool-blurb">{meta['blurb']}</div>
                    <div class="tool-dot-row">
                        <span class="{dot_class}"></span>
                        <span class="tool-dot-label">{status_label}</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.session_state.enabled_tools[key] = st.toggle(
            f"Enable {meta['label']}", value=enabled, key=f"toggle_{key}", label_visibility="collapsed"
        )
