from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


DEFAULT_WINGS = ["user", "project", "skills", "operations", "sessions"]
VALID_SCOPES = {"user", "project", "session", "skill", "operation"}
VALID_SAFETY = {"normal", "sensitive"}
VALID_STATUS = {"active", "forgotten", "quarantined"}


@dataclass
class MemoryItem:
    """A visible, forgettable memory item in the local Forge memory palace."""

    id: str
    scope: str
    wing: str
    room: str
    closet: str
    drawer: str
    content: str
    source: str = "manual"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_used_at: str | None = None
    confidence: float = 1.0
    safety: str = "normal"
    status: str = "active"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MemoryItem":
        return cls(
            id=str(data["id"]),
            scope=str(data.get("scope", "project")),
            wing=str(data.get("wing", data.get("scope", "project"))),
            room=str(data.get("room", "general")),
            closet=str(data.get("closet", "default")),
            drawer=str(data.get("drawer", "inbox")),
            content=str(data.get("content", "")),
            source=str(data.get("source", "manual")),
            created_at=str(data.get("created_at", "")),
            last_used_at=data.get("last_used_at"),
            confidence=float(data.get("confidence", 1.0)),
            safety=str(data.get("safety", "normal")),
            status=str(data.get("status", "active")),
            metadata=dict(data.get("metadata", {})),
        )


@dataclass
class MemoryRecall:
    """A bounded, explainable memory retrieval result."""

    memory: MemoryItem
    score: float
    reasons: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "memory": self.memory.to_dict(),
            "score": self.score,
            "reasons": self.reasons,
        }
