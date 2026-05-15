from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
import json
import re
import shutil
import uuid

from .approvals import ApprovalLedger
from .skills import SkillStore


@dataclass
class OrganizeMove:
    source: str
    destination: str
    month: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "OrganizeMove":
        return cls(source=str(data["source"]), destination=str(data["destination"]), month=str(data.get("month", "unknown-month")))


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
    skipped_files: list[dict[str, str]] = field(default_factory=list)
    manifest_path: str | None = None
    operation_id: str | None = None
    messages: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["planned_moves"] = [item.to_dict() for item in self.planned_moves]
        data["moved_files"] = [item.to_dict() for item in self.moved_files]
        return data


@dataclass
class RollbackResult:
    operation_id: str
    restored_files: list[OrganizeMove] = field(default_factory=list)
    skipped_files: list[dict[str, str]] = field(default_factory=list)
    manifest_path: str | None = None
    messages: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["restored_files"] = [item.to_dict() for item in self.restored_files]
        return data


class FileOrganizer:
    """Dry-run-first file organizer with rollback support for ordinary users."""

    def __init__(self, workspace: str | Path = ".forge-agent") -> None:
        self.workspace = Path(workspace)
        self.skill_store = SkillStore(self.workspace)
        self.approvals = ApprovalLedger(self.workspace)
        self.operations_dir = self.workspace / "operations"
        self.latest_operation_path = self.operations_dir / "latest-organize.json"

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
                "Forge Agent prepared a month-based organization plan. Dry-run mode only previews the plan. "
                "Use --approve to allow the moves. Approved moves can be rolled back."
            ),
            metadata={
                "source_dir": str(source),
                "output_dir": str(output),
                "skill_id": skill.skill_id,
                "planned_moves": [item.to_dict() for item in planned],
            },
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
        operation_id = str(uuid.uuid4())
        moved: list[OrganizeMove] = []
        skipped: list[dict[str, str]] = []
        for item in planned:
            target = Path(item.destination)
            if target.exists():
                skipped.append({**item.to_dict(), "reason": "destination already exists"})
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(item.source, item.destination)
            moved.append(item)
        self.skill_store.mark_used(skill.skill_id, success=True)
        manifest_path = self._write_manifest(
            source,
            output,
            skill.skill_id,
            approval.approval_id,
            moved,
            skipped_files=skipped,
            operation_id=operation_id,
        )
        messages = [
            f"Moved {len(moved)} files.",
            f"Manifest written to {manifest_path}",
            "Rollback available with `forge-agent organize-rollback`.",
        ]
        if skipped:
            messages.append(f"Skipped {len(skipped)} files because the destination already exists.")
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
            skipped_files=skipped,
            manifest_path=str(manifest_path),
            operation_id=operation_id,
            messages=messages,
        )

    def rollback_last(self) -> RollbackResult:
        if not self.latest_operation_path.exists():
            raise FileNotFoundError("no previous organize operation found")
        data = json.loads(self.latest_operation_path.read_text(encoding="utf-8"))
        return self.rollback_operation(str(data["operation_id"]))

    def rollback_operation(self, operation_id: str) -> RollbackResult:
        manifest_path = self.operations_dir / f"organize-{operation_id}.json"
        if not manifest_path.exists():
            raise FileNotFoundError(f"organize operation not found: {operation_id}")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        restored: list[OrganizeMove] = []
        skipped: list[dict[str, str]] = []
        for raw in manifest.get("moved_files", []):
            move = OrganizeMove.from_dict(raw)
            current = Path(move.destination)
            original = Path(move.source)
            if not current.exists():
                skipped.append({"source": str(current), "reason": "moved file no longer exists"})
                continue
            if original.exists():
                skipped.append({"source": str(current), "reason": "original path already exists"})
                continue
            original.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(current), str(original))
            restored.append(OrganizeMove(source=str(current), destination=str(original), month=move.month))
        manifest["rolled_back_at"] = datetime.now(timezone.utc).isoformat()
        manifest["restored_files"] = [item.to_dict() for item in restored]
        manifest["rollback_skipped_files"] = skipped
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return RollbackResult(
            operation_id=operation_id,
            restored_files=restored,
            skipped_files=skipped,
            manifest_path=str(manifest_path),
            messages=[f"Restored {len(restored)} files.", f"Skipped {len(skipped)} files."],
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

    def _write_manifest(
        self,
        source: Path,
        output: Path,
        skill_id: str,
        approval_id: str,
        moved: list[OrganizeMove],
        *,
        skipped_files: list[dict[str, str]] | None = None,
        operation_id: str,
    ) -> Path:
        self.operations_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = self.operations_dir / f"organize-{operation_id}.json"
        manifest = {
            "operation_id": operation_id,
            "source_dir": str(source),
            "output_dir": str(output),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "skill_id": skill_id,
            "approval_id": approval_id,
            "moved_files": [item.to_dict() for item in moved],
            "skipped_files": skipped_files or [],
        }
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        self.workspace.mkdir(parents=True, exist_ok=True)
        (self.workspace / "organize-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        self.latest_operation_path.write_text(json.dumps({"operation_id": operation_id, "manifest_path": str(manifest_path)}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
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
