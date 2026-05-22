from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from .models import MemoryRecallHit


@dataclass
class MemoryResolution:
    """Conflict-aware memory selection result."""

    selected: list[MemoryRecallHit]
    suppressed: list[MemoryRecallHit] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


def resolve_memory_conflicts(hits: Iterable[MemoryRecallHit], *, prefer_recent: bool = True) -> MemoryResolution:
    """Keep the best candidate per semantic slot and suppress stale conflicts.

    A slot is intentionally simple: scope + layer + key. Callers can pass a
    finer-grained `metadata["slot"]` when several different keys represent the
    same user preference or project fact.
    """

    selected_by_slot: dict[str, MemoryRecallHit] = {}
    suppressed: list[MemoryRecallHit] = []
    notes: list[str] = []

    for hit in hits:
        slot = str(hit.metadata.get("slot") or f"{hit.scope}:{hit.layer}:{hit.key}")
        current = selected_by_slot.get(slot)
        if current is None:
            selected_by_slot[slot] = hit
            continue
        winner, loser = _choose_winner(current, hit, prefer_recent=prefer_recent)
        selected_by_slot[slot] = winner
        suppressed.append(_mark_suppressed(loser, slot, winner))
        notes.append(f"resolved conflict in {slot}: kept {winner.source_id or winner.key}")

    selected = sorted(selected_by_slot.values(), key=lambda item: item.score, reverse=True)
    return MemoryResolution(selected=selected, suppressed=suppressed, notes=notes)


def _choose_winner(left: MemoryRecallHit, right: MemoryRecallHit, *, prefer_recent: bool) -> tuple[MemoryRecallHit, MemoryRecallHit]:
    if prefer_recent:
        left_freshness = float(left.metadata.get("freshness_weight", 0.0))
        right_freshness = float(right.metadata.get("freshness_weight", 0.0))
        if left_freshness != right_freshness:
            return (left, right) if left_freshness > right_freshness else (right, left)
    if left.score == right.score:
        return left, right
    return (left, right) if left.score > right.score else (right, left)


def _mark_suppressed(hit: MemoryRecallHit, slot: str, winner: MemoryRecallHit) -> MemoryRecallHit:
    metadata = dict(hit.metadata)
    metadata.update({"suppressed": True, "suppressed_slot": slot, "suppressed_by": winner.source_id or winner.key})
    return MemoryRecallHit(
        layer=hit.layer,
        scope=hit.scope,
        key=hit.key,
        content=hit.content,
        score=hit.score,
        reason=(hit.reason + "; suppressed by conflict resolution").strip("; "),
        source_id=hit.source_id,
        metadata=metadata,
    )
