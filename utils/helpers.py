"""
utils/helpers.py
Small, dependency-free helpers shared across components and tools.
"""

import html
import re


def escape(text: str) -> str:
    """HTML-escape text before injecting into markdown(unsafe_allow_html=True)."""
    return html.escape(str(text), quote=True)


def truncate(text: str, length: int = 220) -> str:
    text = str(text)
    return text if len(text) <= length else text[:length].rstrip() + "…"


def looks_like_math(query: str) -> bool:
    """Heuristic: string is (mostly) a numeric/arithmetic expression."""
    stripped = query.strip()
    if not stripped:
        return False
    return bool(re.fullmatch(r"[\d\s\.\+\-\*\/\^\%\(\)a-zA-Z,]+", stripped)) and bool(
        re.search(r"[\d]", stripped)
    ) and bool(re.search(r"[\+\-\*\/\^\%]|sqrt|sin|cos|tan|log|pow", stripped))


def looks_like_code(query: str) -> bool:
    if "```" in query:
        return True
    code_signals = ("def ", "import ", "print(", "for ", "while ", "class ", "=")
    return any(sig in query for sig in code_signals) and any(
        kw in query.lower() for kw in ("run", "execute", "code", "script")
    )


def looks_like_search(query: str) -> bool:
    signals = ("search", "look up", "latest", "current", "news", "who is", "what is",
               "when did", "today", "recent", "find information")
    q = query.lower()
    return any(sig in q for sig in signals)


def looks_like_file(query: str, has_upload: bool) -> bool:
    if has_upload:
        return True
    signals = ("file", "document", "read the", "uploaded", "csv", "pdf", "docx")
    q = query.lower()
    return any(sig in q for sig in signals)


def extract_code_block(text: str) -> str:
    match = re.search(r"```(?:python)?\s*(.*?)```", text, re.DOTALL)
    return match.group(1).strip() if match else text.strip()
