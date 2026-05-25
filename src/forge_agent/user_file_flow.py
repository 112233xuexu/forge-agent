from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any
import re

from .organizer import FileOrganizer, OrganizeResult


@dataclass(slots=True)
class UserFileFlowResult:
    goal: str
    status: str
    text: str
    mode: str
    source: str | None = None
    operation: str = "organize_by_month"
    organize_result: OrganizeResult | None = None
    missing_inputs: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "goal": self.goal,
            "status": self.status,
            "text": self.text,
            "mode": self.mode,
            "source": self.source,
            "operation": self.operation,
            "organize_result": self.organize_result.to_dict() if self.organize_result else None,
            "missing_inputs": list(self.missing_inputs),
        }


def maybe_run_file_goal(goal: str, *, workspace: str | Path, mode: str) -> UserFileFlowResult | None:
    if not _looks_like_file_organize(goal):
        return None
    source = _extract_source(goal)
    if not source:
        return UserFileFlowResult(
            goal=goal,
            status="input_required",
            text="I need a folder path before I can organize files.",
            mode=mode,
            missing_inputs=["source_folder"],
        )
    organizer = FileOrganizer(workspace)
    if mode == "explain":
        return UserFileFlowResult(
            goal=goal,
            status="explained",
            text="I will scan the folder, find invoice or receipt files, group them by month, and show the plan before moving anything.",
            mode=mode,
            source=source,
        )
    result = organizer.organize_by_month(source, approve=mode == "execute")
    status = "completed" if mode == "execute" else "planned"
    text = "I moved the planned files." if mode == "execute" else "I prepared a file organization preview. No files were moved."
    return UserFileFlowResult(goal=goal, status=status, text=text, mode=mode, source=source, organize_result=result)


def format_file_flow_human(result: UserFileFlowResult) -> str:
    lines = ["Forge Agent", f"Status: {result.status}", f"Goal: {result.goal}"]
    if result.source:
        lines.append(f"Folder: {result.source}")
    if result.text:
        lines.append(f"Summary: {result.text}")
    if result.missing_inputs:
        lines.append("Needed: " + ", ".join(result.missing_inputs))
    if result.organize_result is not None:
        lines.append(f"Planned moves: {len(result.organize_result.planned_moves)}")
        if result.organize_result.moved_files:
            lines.append(f"Moved files: {len(result.organize_result.moved_files)}")
        if result.organize_result.operation_id:
            lines.append(f"Operation: {result.organize_result.operation_id}")
        for message in result.organize_result.messages[:3]:
            lines.append(f"- {message}")
    return "\n".join(lines)


def _looks_like_file_organize(goal: str) -> bool:
    lowered = goal.lower()
    return ("organize" in lowered or "sort" in lowered) and any(term in lowered for term in ("folder", "files", "invoices", "receipts", "directory"))


def _extract_source(goal: str) -> str:
    quoted = re.search(r"['\"]([^'\"]+)['\"]", goal)
    if quoted:
        return quoted.group(1).strip()
    match = re.search(r"(?:folder|directory|dir|from|in)\s+([^\s]+)", goal, flags=re.IGNORECASE)
    if match:
        return match.group(1).strip()
    path_like = re.search(r"(\.?\.?/[A-Za-z0-9_./-]+|[A-Za-z]:\\[^\s]+)", goal)
    return path_like.group(1).strip() if path_like else ""
