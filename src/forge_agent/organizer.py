from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
import json
import re
import shutil

from .approvals import ApprovalLedger
from .skills import SkillStore


@dataclass
class OrganizeMove:
    source: str
    destination: str
    month: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass
class OrganizeResult:
    source_dir: str
    output_dir: str
    mode: str
    approved: bool
    approval_id: str | None
    skill_id: str
    skill_name: str
    created_skill: bool
    planned_moves: list[OrganizeMove] = field(default_factory=list)
    moved_files: list[OrganizeMove] = field(default_factory=list)
    manifest_path: str | None = None
    messages: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["planned_moves"] = [item.to_dict() for item in self.planned_moves]
        data["moved_files"] = [item.to_dict() for item in self.moved_files]
        return data


class FileOrganizer:
    """Real file organizer for ordinary users.

    Defaults to dry-run so Forge Agent never moves real user files silently.
    Passing `approve=True` allows safe invoice/receipt file moves into month
    folders and records the operation in the workspace manifest.
    """

    def __init__(self, workspace: str | Path = ".forge-agent") -> None:
        self.workspace = Path(workspace)
        self.skill_store = SkillStore(self.workspace)
        self.approvals = ApprovalLedger(self.workspace)

    def organize_by_month(
        self,
        source_dir: str | Path,
        *,
        output_dir: str | Path | None = None,
        approve: bool = False,
        include_extensions: Iterable[str] = (".txt", ".pdf", ".md", ".csv"),
    ) -> OrganizeResult:
        source = Path(source_dir).expanduser().resolve()
        if not source.exists() or not source.is_dir():
            raise FileNotFoundError(f"source directory does not exist: {source}")
        output = Path(output_dir).expanduser().resolve() if output_dir else source / "organized"
        goal = f"Organize invoices and receipts in {source} by month"
        skill, created = self.skill_store.get_or_create_for_goal(goal)
        planned = self._plan_moves(source, output, set(include_extensions))
        approval = self.approvals.request(
            action=f"Move {len(planned)} invoice/receipt files from {source} into month folders under {output}.",
            risk="file_move",
            explanation=(
                "Forge Agent detected invoice or receipt-like files and prepared a month-based organization plan. "
                "Dry-run mode only previews the plan. Use --approve to allow the moves."
            ),
            metadata={"source_dir": str(source), "output_dir": str(output), "skill_id": skill.skill_id, "planned_moves": [item.to_dict() for item in planned]},
        )
        if not approve:
            return OrganizeResult(
                source_dir=str(source),
                output_dir=str(output),
                mode="dry-run",
                approved=False,
                approval_id=approval.approval_id,
                skill_id=skill.skill_id,
                skill_name=skill.name,
                created_skill=created,
                planned_moves=planned,
                messages=[
                    "Dry-run only: no files were moved.",
                    "Review the plan, then rerun with --approve to move files.",
                ],
            )

        self.approvals.decide(approval.approval_id, "approved")
        moved: list[OrganizeMove] = []
        for item in planned:
            target = Path(item.destination)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(item.source, item.destination)
            moved.append(item)
        self.skill_store.mark_used(skill.skill_id, success=True)
        manifest_path = self._write_manifest(source, output, skill.skill_id, approval.approval_id, moved)
        return OrganizeResult(
            source_dir=str(source),
            output_dir=str(output),
            mode="approved",
            approved=True,
            approval_id=approval.approval_id,
            skill_id=skill.skill_id,
            skill_name=skill.name,
            created_skill=created,
            planned_moves=planned,
            moved_files=moved,
            manifest_path=str(manifest_path),
            messages=[f"Moved {len(moved)} files.", f"Manifest written to {manifest_path}"],
        )

    def _plan_moves(self, source: Path, output: Path, include_extensions: set[str]) -> list[OrganizeMove]:
        moves: list[OrganizeMove] = []
        for path in sorted(source.iterdir()):
            if not path.is_file() or path.suffix.lower() not in include_extensions:
                continue
            text = _safe_read_text(path)
            if not _is_invoice_like(path.name, text):
                continue
            month = _month_from_text_or_name(path.name, text)
            destination = output / month / path.name
            if destination.resolve() == path.resolve():
                continue
            moves.append(OrganizeMove(source=str(path), destination=str(destination), month=month))
        return moves

    def _write_manifest(self, source: Path, output: Path, skill_id: str, approval_id: str, moved: list[OrganizeMove]) -> Path:
        self.workspace.mkdir(parents=True, exist_ok=True)
        manifest_path = self.workspace / "organize-manifest.json"
        manifest = {
            "source_dir": str(source),
            "output_dir": str(output),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "skill_id": skill_id,
            "approval_id": approval_id,
            "moved_files": [item.to_dict() for item in moved],
        }
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return manifest_path


def _safe_read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")[:4096]
    except OSError:
        return ""


def _is_invoice_like(name: str, text: str) -> bool:
    haystack = f"{name}\n{text}".lower()
    return any(keyword in haystack for keyword in ["invoice", "receipt", "bill", "statement", "发票", "收据", "账单"])


def _month_from_text_or_name(name: str, text: str) -> str:
    match = re.search(r"(20\d{2})[-_/](0[1-9]|1[0-2])", f"{name}\n{text}")
    if match:
        return f"{match.group(1)}-{match.group(2)}"
    return "unknown-month"
