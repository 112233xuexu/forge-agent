from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .memory_ranking import MemoryQueryProfile, RankedMemory, rank_memories
from .memory_resolution import MemoryResolution, resolve_memory_conflicts
from .memory_verdict import MemoryVerdict, build_memory_verdict
from .models import MemoryRecallHit


@dataclass
class MemoryEngineResult:
    """Complete memory pipeline output for callers that need auditability."""

    profile: MemoryQueryProfile
    ranked: list[RankedMemory]
    resolution: MemoryResolution
    verdict: MemoryVerdict

    def to_metadata(self) -> dict[str, object]:
        return {
            "profile": {
                "query": self.profile.query,
                "preferred_scopes": list(self.profile.preferred_scopes),
                "preferred_layers": list(self.profile.preferred_layers),
                "min_anchor_score": self.profile.min_anchor_score,
                "metadata": dict(self.profile.metadata),
            },
            "ranked": [item.to_dict() for item in self.ranked],
            "resolution_notes": list(self.resolution.notes),
            "verdict": self.verdict.to_metadata(),
        }


def run_memory_engine(
    query: str,
    hits: Iterable[MemoryRecallHit],
    *,
    preferred_scopes: tuple[str, ...] = (),
    preferred_layers: tuple[str, ...] = (),
    max_adopted: int = 5,
    reference_time: str | None = None,
) -> MemoryEngineResult:
    """Run anchoring, ranking, freshness, conflict resolution, and verdict steps."""

    profile = MemoryQueryProfile(
        query=query,
        preferred_scopes=preferred_scopes,
        preferred_layers=preferred_layers,
        min_anchor_score=0.0,
        metadata={"reference_time": reference_time} if reference_time else {},
    )
    ranked = rank_memories(hits, profile)
    resolution = resolve_memory_conflicts([item.hit for item in ranked])
    verdict = build_memory_verdict(resolution.selected, suppressed=resolution.suppressed, max_adopted=max_adopted)
    return MemoryEngineResult(profile=profile, ranked=ranked, resolution=resolution, verdict=verdict)


def select_memory_context(query: str, hits: Iterable[MemoryRecallHit], *, limit: int = 5) -> list[MemoryRecallHit]:
    """Small convenience API for callers that only need adopted memory hits."""

    return run_memory_engine(query, hits, max_adopted=limit).verdict.adopted
