from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json
import uuid


@dataclass
class ApprovalRequest:
    """Plain-language approval request for a risky action."""

    approval_id: str
    action: str
    risk: str
    explanation: str
    status: str = "pending"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    decided_at: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ApprovalRequest":
        return cls(
            approval_id=str(data["approval_id"]),
            action=str(data["action"]),
            risk=str(data.get("risk", "unknown")),
            explanation=str(data.get("explanation", "")),
            status=str(data.get("status", "pending")),
            created_at=str(data.get("created_at", "")),
            decided_at=data.get("decided_at"),
            metadata=dict(data.get("metadata", {})),
        )


class ApprovalLedger:
    """Append-only approval ledger stored in the local Forge workspace."""

    def __init__(self, workspace: str | Path) -> None:
        self.workspace = Path(workspace)
        self.path = self.workspace / "approvals.jsonl"

    def init(self) -> None:
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.path.touch(exist_ok=True)

    def request(self, *, action: str, risk: str, explanation: str, metadata: dict[str, Any] | None = None) -> ApprovalRequest:
        self.init()
        item = ApprovalRequest(
            approval_id=str(uuid.uuid4()),
            action=action,
            risk=risk,
            explanation=explanation,
            metadata=metadata or {},
        )
        self._append(item)
        return item

    def list(self) -> list[ApprovalRequest]:
        if not self.path.exists():
            return []
        items: list[ApprovalRequest] = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                items.append(ApprovalRequest.from_dict(json.loads(line)))
            except (json.JSONDecodeError, KeyError, TypeError, ValueError):
                continue
        return items

    def decide(self, approval_id: str, decision: str) -> ApprovalRequest:
        if decision not in {"approved", "denied"}:
            raise ValueError("decision must be 'approved' or 'denied'")
        items = self.list()
        updated: ApprovalRequest | None = None
        for item in items:
            if item.approval_id == approval_id:
                item.status = decision
                item.decided_at = datetime.now(timezone.utc).isoformat()
                updated = item
        if updated is None:
            raise KeyError(f"approval not found: {approval_id}")
        self._rewrite(items)
        return updated

    def _append(self, item: ApprovalRequest) -> None:
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(item.to_dict(), ensure_ascii=False) + "\n")

    def _rewrite(self, items: list[ApprovalRequest]) -> None:
        self.init()
        with self.path.open("w", encoding="utf-8") as fh:
            for item in items:
                fh.write(json.dumps(item.to_dict(), ensure_ascii=False) + "\n")
