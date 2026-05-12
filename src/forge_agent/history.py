from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json


@dataclass
class HistoryEntry:
    operation_id: str
    kind: str
    created_at: str
    summary: str
    manifest_path: str
    status: str = "recorded"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class OperationHistory:
    """Local operation history across Forge Agent skills.

    The first operation source is the organize manifest directory. Future skill
    packs can write manifests under `.forge-agent/operations` and become visible
    through the same history surface.
    """

    def __init__(self, workspace: str | Path = ".forge-agent") -> None:
        self.workspace = Path(workspace)
        self.operations_dir = self.workspace / "operations"

    def list(self, limit: int = 20) -> list[HistoryEntry]:
        entries: list[HistoryEntry] = []
        if not self.operations_dir.exists():
            return []
        for path in sorted(self.operations_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
            if path.name.startswith("latest-"):
                continue
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            operation_id = str(data.get("operation_id", path.stem))
            kind = "organize" if path.name.startswith("organize-") else str(data.get("kind", "operation"))
            created_at = str(data.get("generated_at", data.get("created_at", datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat())))
            moved_count = len(data.get("moved_files", [])) if isinstance(data.get("moved_files", []), list) else 0
            restored_count = len(data.get("restored_files", [])) if isinstance(data.get("restored_files", []), list) else 0
            status = "rolled_back" if data.get("rolled_back_at") else "recorded"
            summary = data.get("summary") or f"{kind} operation with {moved_count} moved files"
            entries.append(
                HistoryEntry(
                    operation_id=operation_id,
                    kind=kind,
                    created_at=created_at,
                    summary=str(summary),
                    manifest_path=str(path),
                    status=status,
                    metadata={"moved_files": moved_count, "restored_files": restored_count},
                )
            )
        return entries[:limit]

    def show(self, operation_id: str) -> dict[str, Any]:
        path = self._find_manifest(operation_id)
        if path is None:
            raise FileNotFoundError(f"operation not found: {operation_id}")
        return json.loads(path.read_text(encoding="utf-8"))

    def _find_manifest(self, operation_id: str) -> Path | None:
        if not self.operations_dir.exists():
            return None
        exact = self.operations_dir / f"organize-{operation_id}.json"
        if exact.exists():
            return exact
        for path in self.operations_dir.glob("*.json"):
            if path.name.startswith("latest-"):
                continue
            if operation_id in path.stem:
                return path
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if str(data.get("operation_id", "")).startswith(operation_id):
                return path
        return None
