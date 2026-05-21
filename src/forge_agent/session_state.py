from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class SessionState:
    session_id: str
    goal: str = ""
    status: str = "active"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    context: dict[str, Any] = field(default_factory=dict)
    checkpoints: list[str] = field(default_factory=list)

    def touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "goal": self.goal,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "context": dict(self.context),
            "checkpoints": list(self.checkpoints),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SessionState":
        return cls(
            session_id=str(data["session_id"]),
            goal=str(data.get("goal", "")),
            status=str(data.get("status", "active")),
            created_at=str(data.get("created_at", "")),
            updated_at=str(data.get("updated_at", "")),
            context=dict(data.get("context", {})),
            checkpoints=[str(item) for item in data.get("checkpoints", [])],
        )
