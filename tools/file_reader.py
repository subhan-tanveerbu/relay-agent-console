"""
tools/file_reader.py
Reads uploaded documents (txt, md, csv, pdf, docx) into a text preview
the agent/LLM can reason over. Isolated try/except per format so one
bad file never crashes the run — each failure mode returns a clear,
structured error instead.
"""

import io
import os

from config import MAX_FILE_SIZE_MB

SUPPORTED_EXTENSIONS = {".txt", ".md", ".csv", ".pdf", ".docx"}


def _read_txt_like(raw: bytes) -> str:
    return raw.decode("utf-8", errors="replace")


def _read_csv(raw: bytes) -> str:
    import csv
    text = raw.decode("utf-8", errors="replace")
    reader = csv.reader(io.StringIO(text))
    rows = list(reader)
    preview_rows = rows[:15]
    lines = [", ".join(r) for r in preview_rows]
    footer = f"\n… {len(rows) - 15} more rows" if len(rows) > 15 else ""
    return f"CSV — {len(rows)} rows x {len(rows[0]) if rows else 0} cols\n" + "\n".join(lines) + footer


def _read_pdf(raw: bytes) -> str:
    try:
        from pypdf import PdfReader
    except ImportError:
        from PyPDF2 import PdfReader  # fallback for older envs
    reader = PdfReader(io.BytesIO(raw))
    pages_text = []
    for i, page in enumerate(reader.pages[:10]):
        pages_text.append(page.extract_text() or "")
    text = "\n".join(pages_text).strip()
    if len(reader.pages) > 10:
        text += f"\n… {len(reader.pages) - 10} more pages not shown"
    return text or "(No extractable text found — this PDF may be scanned/image-based.)"


def _read_docx(raw: bytes) -> str:
    import docx
    document = docx.Document(io.BytesIO(raw))
    paragraphs = [p.text for p in document.paragraphs if p.text.strip()]
    return "\n".join(paragraphs[:200])


_READERS = {
    ".txt": _read_txt_like,
    ".md": _read_txt_like,
    ".csv": _read_csv,
    ".pdf": _read_pdf,
    ".docx": _read_docx,
}


def run(uploaded_file) -> dict:
    """
    uploaded_file: a Streamlit UploadedFile-like object exposing
    .name, .size (bytes) and .getvalue().
    """
    if uploaded_file is None:
        return {"ok": False, "output": "No file was provided to the File Reader.",
                "meta": {"error_type": "MissingFile"}}

    name = getattr(uploaded_file, "name", "unknown")
    ext = os.path.splitext(name)[1].lower()
    size_mb = getattr(uploaded_file, "size", 0) / (1024 * 1024)

    if ext not in SUPPORTED_EXTENSIONS:
        return {
            "ok": False,
            "output": f"Unsupported file type '{ext}'. Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}",
            "meta": {"error_type": "UnsupportedType", "filename": name},
        }

    if size_mb > MAX_FILE_SIZE_MB:
        return {
            "ok": False,
            "output": f"'{name}' is {size_mb:.1f} MB, over the {MAX_FILE_SIZE_MB} MB limit.",
            "meta": {"error_type": "FileTooLarge", "filename": name},
        }

    try:
        raw = uploaded_file.getvalue()
        content = _READERS[ext](raw)
        return {
            "ok": True,
            "output": content[:6000],
            "meta": {"filename": name, "size_kb": round(len(raw) / 1024, 1), "ext": ext},
        }
    except Exception as exc:  # noqa: BLE001 — surfaced to the UI, not swallowed
        return {
            "ok": False,
            "output": f"Failed to parse '{name}': {exc}",
            "meta": {"error_type": type(exc).__name__, "filename": name},
        }
