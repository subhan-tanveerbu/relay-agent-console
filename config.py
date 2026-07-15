"""
config.py
Central configuration for RELAY — Agent Ops Console.
Holds runtime settings, environment flags and the design-token system
that components/theme.py compiles into CSS. Keeping tokens here means
the entire visual identity can be re-skinned from one file.
"""

import os
from dataclasses import dataclass, field


# --------------------------------------------------------------------------
# Runtime / environment settings
# --------------------------------------------------------------------------

APP_NAME = "RELAY"
APP_TAGLINE = "Agent Ops Console"
APP_ICON = "◈"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY", "")  # optional, improves web search

LIVE_MODE = bool(OPENAI_API_KEY)  # True -> LangChain LLM agent, False -> heuristic router

CODE_EXEC_TIMEOUT_SECONDS = 5
MAX_FILE_SIZE_MB = 8
MAX_HISTORY_ITEMS = 25


# --------------------------------------------------------------------------
# Design tokens
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Palette:
    ink: str = "#0A0D12"          # base background
    ink_soft: str = "#0F131B"     # secondary background
    panel: str = "#12161F"        # glass panel fill
    panel_hi: str = "#171C27"     # elevated panel fill
    border: str = "rgba(148,163,196,0.12)"
    border_strong: str = "rgba(148,163,196,0.24)"

    text: str = "#E8EAF2"
    text_dim: str = "#9AA1B6"
    text_faint: str = "#5D6478"

    violet: str = "#7C5CFF"       # primary signal / brand
    violet_soft: str = "rgba(124,92,255,0.14)"
    teal: str = "#29D3C6"         # secondary signal / data
    teal_soft: str = "rgba(41,211,198,0.14)"

    mint: str = "#3DDC97"         # success
    mint_soft: str = "rgba(61,220,151,0.14)"
    coral: str = "#FF5D5D"        # error
    coral_soft: str = "rgba(255,93,93,0.14)"
    amber: str = "#FFB454"        # warning / pending
    amber_soft: str = "rgba(255,180,84,0.14)"


@dataclass(frozen=True)
class Type:
    display: str = "'Space Grotesk', sans-serif"
    body: str = "'IBM Plex Sans', sans-serif"
    mono: str = "'IBM Plex Mono', monospace"


@dataclass(frozen=True)
class Tokens:
    palette: Palette = field(default_factory=Palette)
    type: Type = field(default_factory=Type)
    radius_sm: str = "8px"
    radius_md: str = "14px"
    radius_lg: str = "20px"


TOKENS = Tokens()


# --------------------------------------------------------------------------
# Tool registry metadata (icon glyphs + copy live here, not scattered in UI)
# --------------------------------------------------------------------------

TOOL_META = {
    "file_reader": {
        "label": "File Reader",
        "glyph": "▤",
        "blurb": "Reads text, CSV, PDF & DOCX into context",
    },
    "calculator": {
        "label": "Calculator",
        "glyph": "±",
        "blurb": "Evaluates arithmetic & math expressions safely",
    },
    "code_executor": {
        "label": "Code Executor",
        "glyph": "◧",
        "blurb": "Runs Python in a restricted, timed sandbox",
    },
    "web_search": {
        "label": "Web Search",
        "glyph": "◎",
        "blurb": "Looks up current information on the open web",
    },
}
