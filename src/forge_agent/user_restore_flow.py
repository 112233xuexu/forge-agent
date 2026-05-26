from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .organizer import FileOrganizer, RollbackResult


_CN_RESTORE_TERMS = ("\u64a4\u9500", "\u6062\u590d", "\u56de\u6eda", "\u8fd8\u539f")
_CN_TARGET_TERMS = ("\u6574\u7406", "\u6587\u4ef6\u5939", "\u76ee\u5f55", "\u6587\u4ef6")


@dataclass(slots=True)
class UserRestoreFlowResult:
    goal: str
    status: str
    text: str
    mode: str
    operation: str = "restore_last_organize"
    rollback_result: RollbackResult | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "goal": self.goal,
            "status": self.status,
            "text": self.text,
            "mode": self.mode,
            "operation": self.operation,
            "rollback_result": self.rollback_result.to_dict() if self.rollback_result else None,
        }


def maybe_run_restore_goal(goal: str, *, workspace: str | Path, mode: str) -> UserRestoreFlowResult | None:
    if not _looks_like_restore(goal):
        return None
    if mode in {"preview", "explain"}:
        status = "planned" if mode == "preview" else "explained"
        return UserRestoreFlowResult(
            goal=goal,
            status=status,
            text="I will restore the latest approved file organization operation. Preview mode does not move files back.",
            mode=mode,
        )
    result = FileOrganizer(workspace).rollback_last()
    return UserRestoreFlowResult(
        goal=goal,
        status="completed",
        text="I restored files from the latest file organization operation.",
        mode=mode,
        rollback_result=result,
    )


def format_restore_flow_human(result: UserRestoreFlowResult) -> str:
    lines = ["Forge Agent", f"Status: {result.status}", f"Goal: {result.goal}", f"Summary: {result.text}"]
    if result.rollback_result is not None:
        lines.append(f"Restored files: {len(result.rollback_result.restored_files)}")
        if result.rollback_result.skipped_files:
            lines.append(f"Skipped files: {len(result.rollback_result.skipped_files)}")
        for message in result.rollback_result.messages[:3]:
            lines.append(f"- {message}")
    return "\n".join(lines)


def _looks_like_restore(goal: str) -> bool:
    lowered = goal.lower()
    restore_terms = ("undo", "restore", "rollback", "roll back", *_CN_RESTORE_TERMS)
    target_terms = ("organize", "organization", "folder", "files", *_CN_TARGET_TERMS)
    return any(term in lowered for term in restore_terms) and any(term in lowered for term in target_terms)
