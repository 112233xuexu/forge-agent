from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from forge_agent.memory_models import MemoryItem


@dataclass(frozen=True)
class MemoryQuality:
    bucket: str
    score: float
    reasons: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {"bucket": self.bucket, "score": self.score, "reasons": list(self.reasons)}


def score_memory_quality(memory: MemoryItem, *, now: datetime | None = None) -> MemoryQuality:
    current = now or datetime.now(timezone.utc)
    reasons: list[str] = []
    score = max(0.0, min(1.0, float(memory.confidence)))

    if memory.status != "active":
        return MemoryQuality(bucket="inactive", score=0.0, reasons=[f"status is {memory.status}"])
    if memory.safety == "sensitive":
        score -= 0.10
        reasons.append("sensitive memory needs explicit use")
    age_days = _age_days(memory.created_at, current)
    if age_days is None:
        score -= 0.10
        reasons.append("created time unavailable")
    elif age_days <= 30:
        score += 0.10
        reasons.append("recent memory")
    elif age_days <= 180:
        reasons.append("established memory")
    else:
        score -= 0.20
        reasons.append("older memory")
    if memory.last_used_at:
        score += 0.10
        reasons.append("used before")
    score = max(0.0, min(1.0, round(score, 3)))
    if score >= 0.80:
        bucket = "strong"
    elif score >= 0.50:
        bucket = "usable"
    else:
        bucket = "weak"
    return MemoryQuality(bucket=bucket, score=score, reasons=reasons or ["default quality"])


def _age_days(value: str, now: datetime) -> int | None:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return max(0, (now - parsed).days)
