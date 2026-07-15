"""
app.py
RELAY — Agent Ops Console
Entry point. Lays out the dashboard grid (Active Tools / AI Workspace +
Execution Monitor / Results Panel, plus a bottom Activity History strip)
and wires user actions to agents.agent_orchestrator.run_task.

Run with:  streamlit run app.py
"""

import streamlit as st

from config import APP_NAME, APP_TAGLINE, TOOL_META
from components import theme, header, tool_panel, execution_monitor, results_panel, activity_history
from agents.agent_orchestrator import run_task
from utils.session_state import init_state, new_run_id


st.set_page_config(
    page_title=f"{APP_NAME} · {APP_TAGLINE}",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

init_state()
theme.inject()

active_count = sum(1 for v in st.session_state.enabled_tools.values() if v)
header.render(active_count)

col_tools, col_workspace, col_results = st.columns([1.05, 2.35, 1.55], gap="medium")

# ---------------------------------------------------------------- Active Tools
with col_tools:
    with st.container(border=True):
        tool_panel.render()

# ---------------------------------------------------------------- AI Workspace
with col_workspace:
    with st.container(border=True):
        st.markdown('<div class="panel-eyebrow"><span class="dot"></span>AI Workspace</div>', unsafe_allow_html=True)

        query = st.text_area(
            "task",
            placeholder="Describe the task — e.g. \"Summarize the uploaded report and calculate the average of column C\"",
            height=100,
            label_visibility="collapsed",
        )

        upload_col, run_col = st.columns([3, 1])
        with upload_col:
            uploaded = st.file_uploader(
                "attach",
                type=["txt", "md", "csv", "pdf", "docx"],
                label_visibility="collapsed",
            )
            st.session_state.uploaded_file = uploaded
        with run_col:
            st.write("")
            run_clicked = st.button("▶  Run task", use_container_width=True)

        if run_clicked:
            with st.spinner("Routing task through tool chain…"):
                result = run_task(
                    query=query,
                    uploaded_file=st.session_state.uploaded_file,
                    enabled_tools=st.session_state.enabled_tools,
                )
            st.session_state.current_steps = result["steps"]
            st.session_state.current_result = result

            push_record = {
                "id": new_run_id(),
                "query": query,
                "ok": result["ok"],
                "mode": result["mode"],
                "tool_count": len(result["steps"]),
            }
            st.session_state.runs.insert(0, push_record)
            st.session_state.runs = st.session_state.runs[:25]

        st.markdown('<hr class="relay-rule"/>', unsafe_allow_html=True)
        execution_monitor.render(st.session_state.current_steps)

# ---------------------------------------------------------------- Results Panel
with col_results:
    with st.container(border=True):
        results_panel.render(st.session_state.current_result, st.session_state.current_steps)

# ---------------------------------------------------------------- Activity History
st.markdown('<div style="height:18px"></div>', unsafe_allow_html=True)
with st.container(border=True):
    activity_history.render(st.session_state.runs)
