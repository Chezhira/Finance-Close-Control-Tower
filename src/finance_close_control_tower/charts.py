from __future__ import annotations


def status_colour(status: str) -> str:
    return {"green": "#2e7d32", "amber": "#b26a00", "red": "#b00020"}.get(status.lower(), "#555555")
