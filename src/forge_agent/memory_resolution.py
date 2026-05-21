from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from forge_agent.memory_models import MemoryRecall


@dataclass(frozen=True)
class ResolvedMemory:
    winner: MemoryRecall
    conflicts: list[MemoryRecall]
    reasons: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "winner": self.winner.to_dict(),
            "conflicts": [item.to_dict() for item in self.conflicts],
            "reasons": list(self.reasons),
        }


def resolve_memory_conflicts(matches: list[MemoryRecall]) -> list[ResolvedMemory]:
    grouped: dict[str, list[MemoryRecall]] = {}
    for match in matches:
        key = _resolution_key(match)
        grouped.setdefault(key, []).append(match)
    resolved: list[ResolvedMemory] = []
    for group in grouped.values():
        ranked = sorted(group, key=_rank_key, reverse=True)
        winner = ranked[0]
        conflicts = ranked[1:]
        reasons = ["highest score and confidence"]
        if conflicts:
            reasons.append(f"resolved {len(conflicts)} lower ranked memory item(s)")
        resolved.append(ResolvedMemory(winner=winner, conflicts=conflicts, reasons=reasons))
    return sorted(resolved, key=lambda item: item.winner.score, reverse=True)


def summarize_resolved_memories(items: list[ResolvedMemory]) -> dict[str, Any]:
    return {
        "winners": len(items),
        "conflicts": sum(len(item.conflicts) for item in items),
        "memory_ids": [item.winner.memory.id for item in items],
    }


def _resolution_key(match: MemoryRecall) -> str:
    memory = match.memory
    explicit = memory.metadata.get("resolution_key")
    if explicit:
        return str(explicit)
    return f"{memory.scope}:{memory.wing}:{memory.room}:{memory.closet}:{memory.drawer}"


def _rank_key(match: MemoryRecall) -> tuple[float, float, str]:
    return (float(match.score), float(match.memory.confidence), match.memory.created_at)
