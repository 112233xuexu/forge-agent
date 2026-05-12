from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json
import shutil
import uuid


@dataclass
class UndoOperation:
    source: str
    destination: str
    operation: str = "move"

    def to_dict(self) -> dict[str, str]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "UndoOperation":
        return cls(
            source=str(data["source"]),
            destination=str(data["destination"]),
            operation=str(data.get("operation", "move")),
        )


@dataclass
class UndoRecord:
    undo_id: str
    action: str
    status: str
    created_at: str
    updated_at: str
    operations: list[UndoOperation] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["operations"] = [item.to_dict() for item in self.operations]
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "UndoRecord":
        return cls(
            undo_id=str(data["undo_id"]),
            action=str(data.get("action", "unknown")),
            status=str(data.get("status", "available")),
            created_at=str(data.get("created_at", "")),
            updated_at=str(data.get("updated_at", data.get("created_at", ""))),
            operations=[UndoOperation.from_dict(item) for item in data.get("operations", [])],
            metadata=dict(data.get("metadata", {})),
        )


@dataclass
class UndoResult:
    undo_id: str
    status: str
    restored: list[UndoOperation] = field(default_factory=list)
    skipped: list[dict[str, str]] = field(default_factory=list)
    messages: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "undo_id": self.undo_id,
            "status": self.status,
            "restored": [item.to_dict() for item in self.restored],
            "skipped": self.skipped,
            "messages": self.messages,
        }


class UndoLedger:
    """Local undo ledger for reversible user-facing actions."""

    def __init__(self, workspace: str | Path) -> None:
        self.workspace = Path(workspace)
        self.path = self.workspace / "undo.jsonl"

    def init(self) -> None:
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.path.touch(exist_ok=True)

    def create(self, *, action: str, operations: list[UndoOperation], metadata: dict[str, Any] | None = None) -> UndoRecord:
        self.init()
        now = datetime.now(timezone.utc).isoformat()
        record = UndoRecord(
            undo_id=str(uuid.uuid4()),
            action=action,
            status="available",
            created_at=now,
            updated_at=now,
            operations=operations,
            metadata=metadata or {},
        )
        self._append(record)
        return record

    def list(self) -> list[UndoRecord]:
        if not self.path.exists():
            return []
        records: list[UndoRecord] = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                records.append(UndoRecord.from_dict(json.loads(line)))
            except (json.JSONDecodeError, KeyError, TypeError, ValueError):
                continue
        return records

    def latest_available(self) -> UndoRecord | None:
        for record in reversed(self.list()):
            if record.status == "available":
                return record
        return None

    def apply(self, undo_id: str | None = None, *, dry_run: bool = False) -> UndoResult:
        records = self.list()
        target = None
        for record in reversed(records):
            if undo_id is None and record.status == "available":
                target = record
                break
            if undo_id is not None and (record.undo_id == undo_id or record.undo_id.startswith(undo_id)):
                target = record
                break
        if target is None:
            return UndoResult(undo_id=undo_id or "latest", status="not_found", messages=["No matching undo record found."])
        if target.status != "available":
            return UndoResult(undo_id=target.undo_id, status=target.status, messages=[f"Undo record is not available: {target.status}"])

        restored: list[UndoOperation] = []
        skipped: list[dict[str, str]] = []
        for operation in reversed(target.operations):
            if operation.operation != "move":
                skipped.append({"source": operation.source, "destination": operation.destination, "reason": "unsupported operation"})
                continue
            current = Path(operation.destination)
            original = Path(operation.source)
            if not current.exists():
                skipped.append({"source": operation.source, "destination": operation.destination, "reason": "destination missing"})
                continue
            if original.exists():
                skipped.append({"source": operation.source, "destination": operation.destination, "reason": "original path already exists"})
                continue
            restored.append(operation)
            if not dry_run:
                original.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(current), str(original))
        if dry_run:
            return UndoResult(
                undo_id=target.undo_id,
                status="dry-run",
                restored=restored,
                skipped=skipped,
                messages=["Dry-run only: no files were restored."],
            )

        target.status = "applied" if not skipped else "partial"
        target.updated_at = datetime.now(timezone.utc).isoformat()
        target.metadata["restored_count"] = len(restored)
        target.metadata["skipped_count"] = len(skipped)
        self._rewrite(records)
        return UndoResult(
            undo_id=target.undo_id,
            status=target.status,
            restored=restored,
            skipped=skipped,
            messages=[f"Restored {len(restored)} operation(s).", f"Skipped {len(skipped)} operation(s)."],
        )

    def _append(self, record: UndoRecord) -> None:
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record.to_dict(), ensure_ascii=False) + "\n")

    def _rewrite(self, records: list[UndoRecord]) -> None:
        self.init()
        with self.path.open("w", encoding="utf-8") as fh:
            for record in records:
                fh.write(json.dumps(record.to_dict(), ensure_ascii=False) + "\n")
