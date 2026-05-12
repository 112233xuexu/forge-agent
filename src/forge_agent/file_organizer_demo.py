from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json
import re
import shutil

from .approvals import ApprovalLedger
from .skills import SkillStore


@dataclass
class FileOrganizerDemoResult:
    """Public ordinary-user demo result."""

    goal: str
    workspace: str
    inbox: str
    organized: str
    manifest_path: str
    approval_id: str
    skill_id: str
    skill_name: str
    created_skill: bool
    reuse_proven: bool
    moved_files: list[dict[str, str]] = field(default_factory=list)
    audit: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


_SAMPLE_FILES: dict[str, str] = {
    "invoice-2026-01-alpha.txt": "Invoice Date: 2026-01-05\nVendor: Alpha Supplies\nAmount: 42.00\n",
    "receipt-2026-01-coffee.txt": "Receipt Date: 2026-01-18\nVendor: Coffee Shop\nAmount: 8.50\n",
    "invoice-2026-02-beta.txt": "Invoice Date: 2026-02-03\nVendor: Beta Services\nAmount: 120.00\n",
    "note-random.txt": "This is a personal note and should remain in the inbox.\n",
}

_SECOND_BATCH: dict[str, str] = {
    "invoice-2026-02-gamma.txt": "Invoice Date: 2026-02-21\nVendor: Gamma Studio\nAmount: 75.00\n",
    "receipt-2026-03-travel.txt": "Receipt Date: 2026-03-02\nVendor: Train\nAmount: 16.20\n",
}


def run_file_organizer_demo(workspace: str | Path = ".forge-agent-demo") -> FileOrganizerDemoResult:
    """Run a deterministic safe demo for the zero-config skill autopilot promise.

    The demo creates sample invoice/receipt files inside a sandbox, asks for a
    plain-language approval, records that approval, organizes files by month,
    writes a manifest, then runs a second similar batch to prove skill reuse.
    """

    workspace_path = Path(workspace)
    if workspace_path.exists():
        shutil.rmtree(workspace_path)
    workspace_path.mkdir(parents=True, exist_ok=True)
    inbox = workspace_path / "inbox"
    organized = workspace_path / "organized"
    inbox.mkdir(parents=True, exist_ok=True)
    organized.mkdir(parents=True, exist_ok=True)

    for name, content in _SAMPLE_FILES.items():
        (inbox / name).write_text(content, encoding="utf-8")

    goal = "帮我整理这个文件夹，找出发票和收据，按月份归类，并给我一份清单"
    skill_store = SkillStore(workspace_path)
    skill_store.init()
    skill, created = skill_store.get_or_create_for_goal(goal)

    approvals = ApprovalLedger(workspace_path)
    approval = approvals.request(
        action="Move invoice and receipt files into month folders inside the demo sandbox.",
        risk="file_move",
        explanation=(
            "Forge Agent will only move files in the generated demo sandbox. "
            "It will not touch your real folders. This demonstrates plain-language approval before risky file operations."
        ),
        metadata={"goal": goal, "skill_id": skill.skill_id},
    )
    approvals.decide(approval.approval_id, "approved")

    moved_first = _organize_invoice_like_files(inbox, organized)
    skill_store.mark_used(skill.skill_id, success=True)

    for name, content in _SECOND_BATCH.items():
        (inbox / name).write_text(content, encoding="utf-8")
    reused_skill, created_second = skill_store.get_or_create_for_goal(
        "请继续整理新来的发票和收据，找出发票和收据，按月份归类"
    )
    moved_second = _organize_invoice_like_files(inbox, organized)
    skill_store.mark_used(reused_skill.skill_id, success=True)

    moved_files = moved_first + moved_second
    manifest_path = workspace_path / "manifest.json"
    manifest = {
        "goal": goal,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "approval_id": approval.approval_id,
        "skill_id": skill.skill_id,
        "skill_name": skill.name,
        "created_skill": created,
        "reuse_proven": reused_skill.skill_id == skill.skill_id and not created_second,
        "moved_files": moved_files,
        "remaining_inbox": sorted(path.name for path in inbox.iterdir()),
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return FileOrganizerDemoResult(
        goal=goal,
        workspace=str(workspace_path),
        inbox=str(inbox),
        organized=str(organized),
        manifest_path=str(manifest_path),
        approval_id=approval.approval_id,
        skill_id=skill.skill_id,
        skill_name=skill.name,
        created_skill=created,
        reuse_proven=manifest["reuse_proven"],
        moved_files=moved_files,
        audit=[
            "created sandbox files",
            "created or selected local skill",
            "requested approval before moving files",
            "recorded approval decision",
            "organized invoice and receipt files by month",
            "ran a second batch to prove skill reuse",
            "wrote manifest.json",
        ],
    )


def _organize_invoice_like_files(inbox: Path, organized: Path) -> list[dict[str, str]]:
    moved: list[dict[str, str]] = []
    for path in sorted(inbox.iterdir()):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if not _is_invoice_like(path.name, text):
            continue
        month = _month_from_text_or_name(path.name, text)
        target_dir = organized / month
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / path.name
        shutil.move(str(path), str(target))
        moved.append({"source": str(path), "destination": str(target), "month": month})
    return moved


def _is_invoice_like(name: str, text: str) -> bool:
    haystack = f"{name}\n{text}".lower()
    return any(keyword in haystack for keyword in ["invoice", "receipt", "发票", "收据"])


def _month_from_text_or_name(name: str, text: str) -> str:
    match = re.search(r"(20\d{2})[-_/](0[1-9]|1[0-2])", f"{name}\n{text}")
    if match:
        return f"{match.group(1)}-{match.group(2)}"
    return "unknown-month"
