from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from forge_agent.memory_models import MemoryItem


@dataclass(frozen=True)
class MemorySafetyDecision:
    action: str
    reasons: list[str]
    safe_to_recall: bool

    def to_dict(self) -> dict[str, Any]:
        return {"action": self.action, "reasons": list(self.reasons), "safe_to_recall": self.safe_to_recall}


def decide_memory_safety(memory: MemoryItem, *, include_sensitive: bool = False) -> MemorySafetyDecision:
    reasons: list[str] = []
    if memory.status == "forgotten":
        return MemorySafetyDecision("exclude", ["memory was forgotten"], False)
    if memory.status == "quarantined":
        return MemorySafetyDecision("quarantine", ["memory is quarantined"], False)
    if memory.safety == "sensitive" and not include_sensitive:
        return MemorySafetyDecision("require_explicit_recall", ["sensitive memory needs explicit recall"], False)
    if memory.confidence < 0.25:
        reasons.append("low confidence")
        return MemorySafetyDecision("review", reasons, False)
    return MemorySafetyDecision("allow", reasons or ["active memory"], True)


def summarize_safety(decisions: list[MemorySafetyDecision]) -> dict[str, int]:
    totals: dict[str, int] = {}
    for decision in decisions:
        totals[decision.action] = totals.get(decision.action, 0) + 1
    return totals
