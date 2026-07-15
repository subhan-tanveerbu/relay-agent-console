"""
components/header.py
Top bar: brand mark, system status pill, live mode indicator, clock.
"""

import time
import streamlit as st

from config import APP_NAME, APP_TAGLINE, APP_ICON, LIVE_MODE


def render(active_tool_count: int) -> None:
    mode_label = "LIVE · GPT-4o" if LIVE_MODE else "HEURISTIC ROUTER"
    st.markdown(
        f"""
        <div class="relay-header">
            <div class="relay-brand">
                <div class="relay-mark">{APP_ICON}</div>
                <div>
                    <div class="relay-title">{APP_NAME}</div>
                    <div class="relay-sub">{APP_TAGLINE}</div>
                </div>
            </div>
            <div class="relay-status">
                <div class="status-pill"><span class="pulse"></span>{mode_label}</div>
                <div class="status-pill" style="background: rgba(124,92,255,0.08); border-color: var(--violet-soft);">
                    <span style="width:7px;height:7px;border-radius:50%;background:var(--violet);"></span>
                    {active_tool_count} tools active
                </div>
                <div class="relay-clock">{time.strftime("%H:%M:%S")}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
