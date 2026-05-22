from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Iterable

from .memory_freshness import apply_freshness, parse_memory_time
from .memory_guard import has_memory_anchor, memory_overlap_score
from .models import MemoryRecallHit


@dataclass
class MemoryQueryProfile:
    """Signals extracted from the current request for memory ranking."""

    query: str
    preferred_scopes: tuple[str, ...] = ()
    preferred_layers: tuple[str, ...] = ()
    min_anchor_score: float = 0.0
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass
class RankedMemory:
    hit: MemoryRecallHit
    rank: int
    anchor_score: float
    freshness_weight: float

    def to_dict(self) -> dict[str, object]:
        return {
            "rank": self.rank,
            "anchor_score": self.anchor_score,
            "freshness_weight": self.freshness_weight,
            "hit": self.hit.to_dict(),
        }


def rank_memories(hits: Iterable[MemoryRecallHit], profile: MemoryQueryProfile) -> list[RankedMemory]:
    """Rank recall hits with task anchoring, freshness, and scope/layer boosts."""

    ranked: list[RankedMemory] = []
    reference = _profile_reference_time(profile)
    for hit in hits:
        anchor_score = memory_overlap_score(profile.query, (hit.key, hit.content, hit.reason))
        if profile.min_anchor_score and anchor_score < profile.min_anchor_score:
            continue
        if not has_memory_anchor(profile.query, hit.key, hit.content, hit.reason):
            continue
        adjusted = apply_freshness(hit, reference=reference)
        scope_boost = 1.15 if hit.scope in profile.preferred_scopes else 1.0
        layer_boost = 1.10 if hit.layer in profile.preferred_layers else 1.0
        metadata = dict(adjusted.metadata)
        freshness_weight = float(metadata.get("freshness_weight", 1.0))
        metadata.update({"anchor_score": round(anchor_score, 4), "scope_boost": scope_boost, "layer_boost": layer_boost})
        adjusted = MemoryRecallHit(
            layer=adjusted.layer,
            scope=adjusted.scope,
            key=adjusted.key,
            content=adjusted.content,
            score=adjusted.score * (1.0 + anchor_score) * scope_boost * layer_boost,
            reason=(adjusted.reason + "; ranked for current task").strip("; "),
            source_id=adjusted.source_id,
            metadata=metadata,
        )
        ranked.append(RankedMemory(hit=adjusted, rank=0, anchor_score=anchor_score, freshness_weight=freshness_weight))

    ranked.sort(key=lambda item: (item.hit.score, item.anchor_score, _sort_time(item.hit)), reverse=True)
    for index, item in enumerate(ranked, start=1):
        item.rank = index
    return ranked


def top_memories(hits: Iterable[MemoryRecallHit], profile: MemoryQueryProfile, *, limit: int = 5) -> list[MemoryRecallHit]:
    return [item.hit for item in rank_memories(hits, profile)[: max(0, limit)]]


def _profile_reference_time(profile: MemoryQueryProfile) -> datetime | None:
    value = profile.metadata.get("reference_time")
    return parse_memory_time(value)


def _sort_time(hit: MemoryRecallHit) -> datetime:
    parsed = parse_memory_time(hit.metadata.get("last_used_at") or hit.metadata.get("updated_at") or hit.metadata.get("created_at"))
    return parsed or datetime.min
