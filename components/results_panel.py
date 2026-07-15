"""
components/results_panel.py
Renders the final agent output plus source badges (which tools
contributed) and success/error notification banner.
"""

import streamlit as st
from config import TOOL_META
from utils.helpers import escape


def render(result: dict, steps: list) -> None:
    st.markdown('<div class="panel-eyebrow"><span class="dot"></span>Results Panel</div>', unsafe_allow_html=True)

    if result is None:
        st.markdown('<div class="result-empty">Results will appear here after a run.</div>', unsafe_allow_html=True)
        return

    ok = result.get("ok", True)
    banner_class = "success" if ok else "error"
    banner_text = "Run completed successfully" if ok else "Run finished with an error"
    st.markdown(f'<span class="badge {banner_class}">{banner_text}</span>', unsafe_allow_html=True)

    used_tools = sorted({s["tool"] for s in steps}) if steps else []
    if used_tools:
        badges = "".join(
            f'<span class="source-badge">◈ {TOOL_META.get(t, {}).get("label", t)}</span>' for t in used_tools
        )
        st.markdown(f'<div style="margin:10px 0 4px 0;">{badges}</div>', unsafe_allow_html=True)

    output = escape(result.get("final_output", ""))
    st.markdown(f'<div class="result-card">{output}</div>', unsafe_allow_html=True)

    st.download_button(
        "Export result (.txt)",
        data=result.get("final_output", ""),
        file_name="relay_result.txt",
        use_container_width=True,
    )
