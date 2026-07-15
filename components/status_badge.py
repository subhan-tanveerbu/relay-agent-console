"""
components/status_badge.py
Tiny reusable badge factory so status colors/labels stay consistent
anywhere they're used (execution monitor, results panel, history).
"""

_LABELS = {
    "success": "success",
    "error": "error",
    "running": "running",
    "pending": "pending",
}


def badge_html(status: str, label: str = None) -> str:
    status = status if status in _LABELS else "pending"
    text = label or _LABELS[status]
    return f'<span class="badge {status}">{text}</span>'
