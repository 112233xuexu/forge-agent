from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class MemoryRecallHit:
    """A normalized memory recall candidate passed through the memory pipeline."""

    layer: str
    scope: str
    key: str
    content: str
    score: float
    reason: str = ""
    source_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
