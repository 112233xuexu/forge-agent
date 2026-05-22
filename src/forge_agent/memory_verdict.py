from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from .models import MemoryRecallHit


@dataclass
class MemoryVerdict:
    """Final explainable memory context for a planning step."""

    adopted: list[MemoryRecallHit]
    rejected: list[MemoryRecallHit] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def used_memory(self) -> bool:
        return bool(self.adopted)

    def to_metadata(self) -> dict[str, object]:
        return {
            "used_memory": self.used_memory,
            "adopted": [hit.to_dict() for hit in self.adopted],
            "rejected": [hit.to_dict() for hit in self.rejected],
            "warnings": list(self.warnings),
        }


def build_memory_verdict(
    selected: Iterable[MemoryRecallHit],
    *,
    suppressed: Iterable[MemoryRecallHit] = (),
    min_score: float = 0.05,
    max_adopted: int = 5,
) -> MemoryVerdict:
    """Convert ranked/resolved memories into a safe planning verdict."""

    adopted: list[MemoryRecallHit] = []
    rejected: list[MemoryRecallHit] = list(suppressed)
    warnings: list[str] = []

    for hit in selected:
        if hit.score < min_score:
            rejected.append(_reject(hit, "below memory adoption threshold"))
            continue
        if len(adopted) >= max_adopted:
            rejected.append(_reject(hit, "outside memory adoption limit"))
            continue
        adopted.append(hit)

    if rejected:
        warnings.append(f"{len(rejected)} memory candidate(s) were not adopted")
    return MemoryVerdict(adopted=adopted, rejected=rejected, warnings=warnings)


def should_adopt_verdict_reanchor(verdict: MemoryVerdict, *, current_quarantine: dict[str, object] | None = None) -> bool:
    """Return whether the verdict is strong enough to re-anchor planning state."""

    if not verdict.adopted:
        return False
    quarantine = dict(current_quarantine or {})
    if quarantine.get("blocked") is True:
        return False
    best = max(hit.score for hit in verdict.adopted)
    return best >= 0.25


def _reject(hit: MemoryRecallHit, reason: str) -> MemoryRecallHit:
    metadata = dict(hit.metadata)
    metadata["rejected"] = True
    metadata["reject_reason"] = reason
    return MemoryRecallHit(
        layer=hit.layer,
        scope=hit.scope,
        key=hit.key,
        content=hit.content,
        score=hit.score,
        reason=(hit.reason + f"; {reason}").strip("; "),
        source_id=hit.source_id,
        metadata=metadata,
    )
