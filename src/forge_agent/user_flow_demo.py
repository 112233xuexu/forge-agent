from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any
import shutil

from .user_file_flow import maybe_run_file_goal, UserFileFlowResult
from .user_restore_flow import maybe_run_restore_goal, UserRestoreFlowResult


@dataclass(slots=True)
class UserFlowDemoResult:
    workspace: str
    source_dir: str
    preview: dict[str, Any]
    execute: dict[str, Any]
    restore: dict[str, Any]
    audit: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def run_user_flow_demo(workspace: str | Path = ".forge-agent-user-flow-demo") -> UserFlowDemoResult:
    root = Path(workspace)
    if root.exists():
        shutil.rmtree(root)
    source = root / "invoices"
    source.mkdir(parents=True, exist_ok=True)
    (source / "invoice-2026-05-alpha.txt").write_text("invoice 2026-05 alpha", encoding="utf-8")
    (source / "receipt-2026-06-beta.txt").write_text("receipt 2026-06 beta", encoding="utf-8")
    (source / "personal-note.txt").write_text("not an invoice", encoding="utf-8")

    preview = maybe_run_file_goal(f"organize folder {source}", workspace=root / "state", mode="preview")
    execute = maybe_run_file_goal(f"organize folder {source}", workspace=root / "state", mode="execute")
    restore = maybe_run_restore_goal("undo last organize", workspace=root / "state", mode="execute")

    if preview is None or execute is None or restore is None:
        raise RuntimeError("user flow demo could not build the expected flow")

    return UserFlowDemoResult(
        workspace=str(root),
        source_dir=str(source),
        preview=preview.to_dict(),
        execute=execute.to_dict(),
        restore=restore.to_dict(),
        audit=[
            "created sample invoice folder",
            "previewed organization through user goal flow",
            "executed organization through user goal flow",
            "restored latest organization through user goal flow",
        ],
    )
