"""
components/theme.py
Compiles config.TOKENS into a single CSS payload injected once at app
start. This is what turns Streamlit's default look into the RELAY
"AI Operations Console" identity — dark glass panels, a violet/teal
signal palette, Space Grotesk display type, and a signature animated
execution rail. No other module should write raw <style> tags.
"""

import streamlit as st
from config import TOKENS

P = TOKENS.palette
T = TOKENS.type


def _css() -> str:
    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

:root {{
    --ink: {P.ink};
    --ink-soft: {P.ink_soft};
    --panel: {P.panel};
    --panel-hi: {P.panel_hi};
    --border: {P.border};
    --border-strong: {P.border_strong};
    --text: {P.text};
    --text-dim: {P.text_dim};
    --text-faint: {P.text_faint};
    --violet: {P.violet};
    --violet-soft: {P.violet_soft};
    --teal: {P.teal};
    --teal-soft: {P.teal_soft};
    --mint: {P.mint};
    --mint-soft: {P.mint_soft};
    --coral: {P.coral};
    --coral-soft: {P.coral_soft};
    --amber: {P.amber};
    --amber-soft: {P.amber_soft};
    --f-display: {T.display};
    --f-body: {T.body};
    --f-mono: {T.mono};
    --radius-sm: {TOKENS.radius_sm};
    --radius-md: {TOKENS.radius_md};
    --radius-lg: {TOKENS.radius_lg};
}}

/* ---------- reset Streamlit chrome ---------- */
#MainMenu, header[data-testid="stHeader"], footer, div[data-testid="stToolbar"],
div[data-testid="stDecoration"], div[data-testid="stStatusWidget"] {{
    display: none !important;
}}
section[data-testid="stSidebar"] {{ display: none !important; }}

.stApp {{
    background:
        radial-gradient(1100px 520px at 8% -8%, rgba(124,92,255,0.16), transparent 60%),
        radial-gradient(900px 480px at 96% 6%, rgba(41,211,198,0.10), transparent 55%),
        var(--ink);
    font-family: var(--f-body);
    color: var(--text);
}}

.block-container {{
    padding-top: 1.1rem !important;
    padding-bottom: 2.5rem !important;
    max-width: 1400px;
}}

* {{ scrollbar-width: thin; scrollbar-color: var(--border-strong) transparent; }}
*::-webkit-scrollbar {{ width: 6px; height: 6px; }}
*::-webkit-scrollbar-thumb {{ background: var(--border-strong); border-radius: 8px; }}

h1, h2, h3, h4 {{ font-family: var(--f-display); letter-spacing: -0.01em; }}

/* ---------- generic glass panel ---------- */
.glass {{
    background: linear-gradient(180deg, var(--panel-hi), var(--panel));
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 20px 22px;
    backdrop-filter: blur(14px);
    box-shadow: 0 1px 0 rgba(255,255,255,0.03) inset, 0 20px 40px -28px rgba(0,0,0,0.6);
}}

.panel-eyebrow {{
    font-family: var(--f-mono);
    font-size: 11px;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--text-faint);
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 14px;
}}
.panel-eyebrow .dot {{
    width: 6px; height: 6px; border-radius: 50%;
    background: var(--violet);
    box-shadow: 0 0 0 3px var(--violet-soft);
}}

/* ---------- bordered containers used as glass panels ---------- */
div[data-testid="stVerticalBlockBorderWrapper"] > div {{
    background: linear-gradient(180deg, var(--panel-hi), var(--panel)) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-lg) !important;
    backdrop-filter: blur(14px);
}}
div[data-testid="stVerticalBlockBorderWrapper"] {{
    border-radius: var(--radius-lg) !important;
}}

/* ---------- header bar ---------- */
.relay-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 22px;
    margin-bottom: 18px;
    border-radius: var(--radius-lg);
    background: linear-gradient(180deg, var(--panel-hi), var(--panel));
    border: 1px solid var(--border);
}}
.relay-brand {{ display: flex; align-items: center; gap: 12px; }}
.relay-mark {{
    width: 34px; height: 34px; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    background: linear-gradient(135deg, var(--violet), var(--teal));
    color: #05070B; font-family: var(--f-display); font-weight: 700; font-size: 17px;
}}
.relay-title {{ font-family: var(--f-display); font-weight: 700; font-size: 18px; letter-spacing: 0.01em; }}
.relay-sub {{ color: var(--text-faint); font-size: 12px; font-family: var(--f-mono); }}
.relay-status {{ display: flex; align-items: center; gap: 18px; }}
.status-pill {{
    display: flex; align-items: center; gap: 7px;
    font-family: var(--f-mono); font-size: 12px; color: var(--text-dim);
    background: rgba(61,220,151,0.08);
    border: 1px solid var(--mint-soft);
    padding: 6px 12px; border-radius: 999px;
}}
.status-pill .pulse {{
    width: 7px; height: 7px; border-radius: 50%; background: var(--mint);
    box-shadow: 0 0 0 0 var(--mint-soft);
    animation: pulse-ring 1.8s infinite;
}}
@keyframes pulse-ring {{
    0% {{ box-shadow: 0 0 0 0 rgba(61,220,151,0.55); }}
    70% {{ box-shadow: 0 0 0 7px rgba(61,220,151,0); }}
    100% {{ box-shadow: 0 0 0 0 rgba(61,220,151,0); }}
}}
.relay-clock {{ font-family: var(--f-mono); font-size: 12px; color: var(--text-faint); }}

/* ---------- tool cards (Active Tools column) ---------- */
.tool-card {{
    display: flex; gap: 12px; align-items: flex-start;
    padding: 12px 14px; margin-bottom: 10px;
    border-radius: var(--radius-md);
    border: 1px solid var(--border);
    background: var(--ink-soft);
    transition: border-color .18s ease, transform .18s ease, background .18s ease;
}}
.tool-card:hover {{ border-color: var(--border-strong); transform: translateY(-1px); }}
.tool-card.disabled {{ opacity: 0.42; }}
.tool-glyph {{
    width: 30px; height: 30px; flex-shrink: 0; border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 15px; background: var(--violet-soft); color: var(--violet);
    border: 1px solid rgba(124,92,255,0.25);
}}
.tool-name {{ font-weight: 600; font-size: 13.5px; color: var(--text); }}
.tool-blurb {{ font-size: 11.5px; color: var(--text-faint); line-height: 1.35; margin-top: 1px; }}
.tool-dot-row {{ display: flex; align-items: center; gap: 6px; margin-top: 6px; }}
.tool-dot {{ width: 6px; height: 6px; border-radius: 50%; background: var(--mint); }}
.tool-dot.off {{ background: var(--text-faint); }}
.tool-dot-label {{ font-family: var(--f-mono); font-size: 10px; color: var(--text-faint); text-transform: uppercase; letter-spacing: .06em; }}

/* ---------- workspace command console ---------- */
.stTextArea textarea {{
    background: var(--ink-soft) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text) !important;
    font-family: var(--f-mono) !important;
    font-size: 13.5px !important;
    padding: 14px !important;
}}
.stTextArea textarea:focus {{
    border-color: var(--violet) !important;
    box-shadow: 0 0 0 3px var(--violet-soft) !important;
}}
.stTextArea label {{ display: none; }}

div[data-testid="stFileUploaderDropzone"] {{
    background: var(--ink-soft) !important;
    border: 1px dashed var(--border-strong) !important;
    border-radius: var(--radius-md) !important;
}}
[data-testid="stFileUploader"] section {{ background: transparent !important; }}
[data-testid="stFileUploader"] small {{ color: var(--text-faint) !important; }}

.stButton > button {{
    background: linear-gradient(135deg, var(--violet), #9B7CFF) !important;
    color: #0A0D12 !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    font-family: var(--f-display) !important;
    font-weight: 600 !important;
    letter-spacing: 0.02em;
    padding: 0.55rem 1.3rem !important;
    transition: transform .15s ease, box-shadow .15s ease;
    box-shadow: 0 8px 20px -10px rgba(124,92,255,0.65);
}}
.stButton > button:hover {{ transform: translateY(-1px); box-shadow: 0 10px 26px -10px rgba(124,92,255,0.85); }}
.stButton > button:active {{ transform: translateY(0); }}

/* secondary / ghost buttons (via kind="secondary") */
button[kind="secondary"] {{
    background: var(--ink-soft) !important;
    color: var(--text-dim) !important;
    border: 1px solid var(--border) !important;
    box-shadow: none !important;
}}

/* ---------- execution monitor rail ---------- */
.rail {{ position: relative; padding: 6px 2px 4px 2px; }}
.rail-empty {{
    font-family: var(--f-mono); font-size: 12px; color: var(--text-faint);
    padding: 18px 4px; text-align: center; border: 1px dashed var(--border);
    border-radius: var(--radius-md);
}}
.rail-item {{
    display: flex; gap: 12px; position: relative; padding-bottom: 18px;
}}
.rail-item:last-child {{ padding-bottom: 0; }}
.rail-item .stem {{
    position: absolute; left: 11px; top: 26px; bottom: 0; width: 2px;
    background: var(--border);
}}
.rail-item:last-child .stem {{ display: none; }}
.rail-node {{
    width: 24px; height: 24px; border-radius: 50%; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
    font-size: 11px; font-family: var(--f-mono); z-index: 1;
    border: 2px solid var(--border-strong);
    background: var(--ink-soft);
}}
.rail-node.success {{ border-color: var(--mint); color: var(--mint); background: var(--mint-soft); }}
.rail-node.error {{ border-color: var(--coral); color: var(--coral); background: var(--coral-soft); }}
.rail-node.running {{ border-color: var(--amber); color: var(--amber); background: var(--amber-soft); animation: spin-pulse 1.1s linear infinite; }}
@keyframes spin-pulse {{
    0% {{ box-shadow: 0 0 0 0 rgba(255,180,84,0.5); }}
    100% {{ box-shadow: 0 0 0 8px rgba(255,180,84,0); }}
}}
.rail-body {{ flex: 1; padding-top: 1px; }}
.rail-top {{ display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }}
.rail-tool {{ font-weight: 600; font-size: 13px; color: var(--text); font-family: var(--f-display); }}
.rail-time {{ font-family: var(--f-mono); font-size: 10.5px; color: var(--text-faint); margin-left: auto; }}
.rail-detail {{
    margin-top: 5px; font-family: var(--f-mono); font-size: 11.5px; color: var(--text-dim);
    background: var(--ink-soft); border: 1px solid var(--border); border-radius: 8px;
    padding: 8px 10px; white-space: pre-wrap; line-height: 1.5; max-height: 130px; overflow-y: auto;
}}

/* status badges */
.badge {{
    display: inline-flex; align-items: center; gap: 5px;
    font-family: var(--f-mono); font-size: 10.5px; text-transform: uppercase;
    letter-spacing: .05em; padding: 3px 9px; border-radius: 999px; font-weight: 500;
}}
.badge.success {{ background: var(--mint-soft); color: var(--mint); }}
.badge.error {{ background: var(--coral-soft); color: var(--coral); }}
.badge.running {{ background: var(--amber-soft); color: var(--amber); }}
.badge.pending {{ background: rgba(148,163,196,0.12); color: var(--text-faint); }}

/* ---------- results panel ---------- */
.result-card {{
    background: var(--ink-soft);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 16px;
    font-family: var(--f-mono);
    font-size: 12.5px;
    color: var(--text);
    white-space: pre-wrap;
    line-height: 1.6;
    max-height: 360px;
    overflow-y: auto;
}}
.result-empty {{
    color: var(--text-faint); font-size: 12.5px; text-align: center; padding: 30px 10px;
    border: 1px dashed var(--border); border-radius: var(--radius-md); font-family: var(--f-mono);
}}
.source-badge {{
    display: inline-flex; align-items: center; gap: 6px;
    font-family: var(--f-mono); font-size: 10.5px; color: var(--teal);
    background: var(--teal-soft); border: 1px solid rgba(41,211,198,0.28);
    padding: 4px 10px; border-radius: 999px; margin: 3px 6px 0 0;
}}

/* ---------- activity history strip ---------- */
.history-scroll {{ display: flex; gap: 12px; overflow-x: auto; padding: 4px 2px 10px 2px; }}
.history-card {{
    min-width: 190px; max-width: 190px; flex-shrink: 0;
    background: var(--ink-soft); border: 1px solid var(--border);
    border-radius: var(--radius-md); padding: 12px 13px;
    transition: border-color .15s ease, transform .15s ease;
}}
.history-card:hover {{ border-color: var(--border-strong); transform: translateY(-2px); }}
.history-id {{ font-family: var(--f-mono); font-size: 10px; color: var(--text-faint); }}
.history-query {{ font-size: 12px; color: var(--text); margin: 6px 0 8px 0; line-height: 1.35;
    display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }}
.history-meta {{ display: flex; justify-content: space-between; align-items: center; }}

/* section headers */
.section-title {{
    font-family: var(--f-display); font-weight: 600; font-size: 14px;
    color: var(--text); margin-bottom: 2px;
}}

hr.relay-rule {{ border: none; border-top: 1px solid var(--border); margin: 22px 0 18px 0; }}

/* details/expander used for logs */
details.log-expand summary {{
    cursor: pointer; font-family: var(--f-mono); font-size: 11px; color: var(--text-faint);
    list-style: none; padding-top: 6px;
}}
details.log-expand summary::-webkit-details-marker {{ display: none; }}
</style>
"""


def inject() -> None:
    st.markdown(_css(), unsafe_allow_html=True)
