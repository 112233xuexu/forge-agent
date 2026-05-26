from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any
import shutil

from .user_file_flow import maybe_run_file_goal
from .user_restore_flow import maybe_run_restore_goal


@dataclass(slots=True)
class UserFlowDemoResult:
    workspace: str
    source_dir: str
    preview: dict[str, Any]
    execute: dict[str, Any]
    restore: dict[str, Any]
    checks: dict[str, bool]
    final_files: list[str]
    audit: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(self.checks.values())

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["passed"] = self.passed
        return data


def run_user_flow_demo(workspace: str | Path = ".forge-agent-user-flow-demo") -> UserFlowDemoResult:
    root = Path(workspace)
    if root.exists():
        shutil.rmtree(root)
    source = root / "invoices"
    source.mkdir(parents=True, exist_ok=True)
    invoice = source / "invoice-2026-05-alpha.txt"
    receipt = source / "receipt-2026-06-beta.txt"
    invoice.write_text("invoice 2026-05 alpha", encoding="utf-8")
    receipt.write_text("receipt 2026-06 beta", encoding="utf-8")

    preview = maybe_run_file_goal(f"organize folder {source}", workspace=root / "state", mode="preview")
    preview_kept_files = invoice.exists() and receipt.exists()

    execute = maybe_run_file_goal(f"organize folder {source}", workspace=root / "state", mode="execute")
    moved_invoice = source / "organized" / "2026-05" / invoice.name
    moved_receipt = source / "organized" / "2026-06" / receipt.name
    execute_moved_files = moved_invoice.exists() and moved_receipt.exists()

    restore = maybe_run_restore_goal("undo last organize", workspace=root / "state", mode="execute")
    restore_returned_files = invoice.exists() and receipt.exists() and not moved_invoice.exists() and not moved_receipt.exists()

    if preview is None or execute is None or restore is None:
        raise RuntimeError("user flow demo could not build the expected flow")

    checks = {
        "preview_did_not_move_files": preview_kept_files,
        "execute_moved_invoice_files": execute_moved_files,
        "restore_returned_files": restore_returned_files,
        "preview_status_planned": preview.status == "planned",
        "execute_status_completed": execute.status == "completed",
        "restore_status_completed": restore.status == "completed",
    }
    final_files = sorted(str(path.relative_to(root)) for path in root.rglob("*") if path.is_file())

    return UserFlowDemoResult(
        workspace=str(root),
        source_dir=str(source),
        preview=preview.to_dict(),
        execute=execute.to_dict(),
        restore=restore.to_dict(),
        checks=checks,
        final_files=final_files,
        audit=[
            "created sample invoice folder",
            "previewed organization through user goal flow",
            "verified preview kept files in place",
            "executed organization through user goal flow",
            "verified invoice files moved into month folders",
            "restored latest organization through user goal flow",
            "verified files returned to the source folder",
        ],
    )
