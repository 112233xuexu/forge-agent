from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class TaskCardButton:
    label: str
    kind: str
    enabled: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {"label": self.label, "kind": self.kind, "enabled": self.enabled}


@dataclass(frozen=True)
class TaskCardImpact:
    summary: str
    level: str = "low"
    reversible: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "level": self.level, "reversible": self.reversible}


@dataclass(frozen=True)
class TaskCard:
    title: str
    user_request: str
    status: str
    plan: list[str]
    impacts: list[TaskCardImpact] = field(default_factory=list)
    boundaries: list[str] = field(default_factory=list)
    buttons: list[TaskCardButton] = field(default_factory=list)
    result_summary: str | None = None
    record_id: str | None = None
    restore_available: bool = False
    memory_used: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "user_request": self.user_request,
            "status": self.status,
            "plan": list(self.plan),
            "impacts": [impact.to_dict() for impact in self.impacts],
            "boundaries": list(self.boundaries),
            "buttons": [button.to_dict() for button in self.buttons],
            "result_summary": self.result_summary,
            "record_id": self.record_id,
            "restore_available": self.restore_available,
            "memory_used": list(self.memory_used),
        }

    def human_summary(self) -> str:
        lines = [self.title, "", f"You asked: {self.user_request}", "", "I will do:"]
        lines.extend(f"- {item}" for item in self.plan)
        if self.impacts:
            lines.append("")
            lines.append("This may affect:")
            lines.extend(f"- {impact.summary}" for impact in self.impacts)
        if self.boundaries:
            lines.append("")
            lines.append("I will not:")
            lines.extend(f"- {item}" for item in self.boundaries)
        if self.result_summary:
            lines.append("")
            lines.append(f"Result: {self.result_summary}")
        if self.restore_available:
            lines.append("")
            lines.append("You can restore this if needed.")
        if self.buttons:
            lines.append("")
            lines.append("Options:")
            lines.extend(f"- {button.label}" for button in self.buttons if button.enabled)
        return "\n".join(lines)


def make_preview_card(
    *,
    title: str,
    user_request: str,
    plan: list[str],
    impacts: list[TaskCardImpact] | None = None,
    boundaries: list[str] | None = None,
    needs_confirmation: bool = True,
) -> TaskCard:
    buttons = []
    if needs_confirmation:
        buttons = [
            TaskCardButton(label="Confirm", kind="confirm"),
            TaskCardButton(label="Edit", kind="edit"),
            TaskCardButton(label="Stop", kind="stop"),
        ]
    return TaskCard(
        title=title,
        user_request=user_request,
        status="needs_confirmation" if needs_confirmation else "preview",
        plan=plan,
        impacts=impacts or [],
        boundaries=boundaries or [],
        buttons=buttons,
    )


def make_done_card(
    *,
    title: str,
    user_request: str,
    plan: list[str],
    result_summary: str,
    record_id: str | None = None,
    restore_available: bool = False,
) -> TaskCard:
    buttons = [TaskCardButton(label="View what I did", kind="view_record")]
    if restore_available:
        buttons.append(TaskCardButton(label="Restore", kind="restore"))
    return TaskCard(
        title=title,
        user_request=user_request,
        status="done",
        plan=plan,
        result_summary=result_summary,
        record_id=record_id,
        restore_available=restore_available,
        buttons=buttons,
    )
