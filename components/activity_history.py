"""
components/activity_history.py
Bottom strip: a horizontally scrolling filmstrip of past runs, each a
small ticket-style card with id, truncated query, tool count, and
status badge. Read-only visual log — clicking is not required by the
assignment brief, so cards stay lightweight (no nested Streamlit
widgets) for fast rendering.
"""

import streamlit as st
from utils.helpers import escape, truncate


def render(runs: list) -> None:
    st.markdown('<div class="panel-eyebrow"><span class="dot"></span>Activity History</div>', unsafe_allow_html=True)

    if not runs:
        st.markdown(
            '<div class="rail-empty">Completed runs will appear here as a scrollable history.</div>',
            unsafe_allow_html=True,
        )
        return

    cards = []
    for run in runs:
        status = "success" if run.get("ok") else "error"
        cards.append(f"""
        <div class="history-card">
            <div class="history-id">{run['id']} · {run.get('mode','')}</div>
            <div class="history-query">{escape(truncate(run.get('query',''), 70))}</div>
            <div class="history-meta">
                <span class="badge {status}">{status}</span>
                <span style="font-family:var(--f-mono);font-size:10px;color:var(--text-faint);">
                    {run.get('tool_count', 0)} calls
                </span>
            </div>
        </div>
        """)

    st.markdown(f'<div class="history-scroll">{"".join(cards)}</div>', unsafe_allow_html=True)
