from __future__ import annotations

from typing import Any

from .tool_registry import ToolRegistry


def default_user_tools() -> ToolRegistry:
    """Return deterministic local tools for the ordinary-user runner."""

    tools = ToolRegistry()
    tools.register("summarize_notes", summarize_notes)
    tools.register("paraphrase_text", paraphrase_text)
    tools.register("translate_text", translate_text)
    tools.register("draft_followup", draft_followup)
    return tools


def summarize_notes(notes: str) -> dict[str, Any]:
    text = _clean(notes)
    points = _split_points(text)
    if not points and text:
        points = [text]
    return {
        "summary": points[0] if points else "",
        "bullets": points[:5],
        "action_items": points[:3],
    }


def paraphrase_text(text: str, style: str = "clear") -> str:
    cleaned = _clean(text)
    mode = _clean(style).lower()
    if mode in {"warm", "friendly"}:
        return f"Thanks — {cleaned}."
    if mode in {"concise", "brief", "short"}:
        return cleaned.rstrip(".") + "."
    if mode in {"professional", "formal"}:
        return f"Please note: {cleaned}."
    return cleaned


def translate_text(text: str, target_language: str) -> str:
    return f"[{_clean(target_language).lower() or 'target'}] {_clean(text)}"


def draft_followup(customer: str, action_items: list[str] | None = None) -> str:
    name = _clean(customer) or "there"
    items = [str(item).strip() for item in (action_items or []) if str(item).strip()]
    if not items:
        return f"Hi {name}, following up on our notes."
    lines = "\n".join(f"- {item}" for item in items)
    return f"Hi {name},\n\nFollowing up with the next steps:\n{lines}\n"


def _clean(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def _split_points(text: str) -> list[str]:
    pieces = [line.strip(" -\t") for line in text.replace("\r", "\n").split("\n")]
    pieces = [piece for piece in pieces if piece]
    if len(pieces) <= 1:
        pieces = [piece.strip() for piece in text.replace(";", ".").split(".") if piece.strip()]
    return pieces
