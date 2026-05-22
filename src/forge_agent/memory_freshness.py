from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .models import MemoryRecallHit


def parse_memory_time(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def memory_last_seen(hit: MemoryRecallHit) -> datetime | None:
    for key in ("last_used_at", "updated_at", "created_at", "timestamp"):
        parsed = parse_memory_time(hit.metadata.get(key))
        if parsed is not None:
            return parsed
    return None


def freshness_weight(hit: MemoryRecallHit, *, reference: datetime | None = None, half_life_days: float = 30.0) -> float:
    """Return a stable 0..1 freshness multiplier for a recall candidate."""

    observed = memory_last_seen(hit)
    if observed is None:
        return 0.75
    reference = reference or datetime.now(timezone.utc)
    if reference.tzinfo is None:
        reference = reference.replace(tzinfo=timezone.utc)
    age_days = max(0.0, (reference - observed).total_seconds() / 86400.0)
    half_life_days = max(1.0, half_life_days)
    return 1.0 / (1.0 + age_days / half_life_days)


def apply_freshness(hit: MemoryRecallHit, *, reference: datetime | None = None) -> MemoryRecallHit:
    weight = freshness_weight(hit, reference=reference)
    metadata = dict(hit.metadata)
    metadata["freshness_weight"] = round(weight, 4)
    return MemoryRecallHit(
        layer=hit.layer,
        scope=hit.scope,
        key=hit.key,
        content=hit.content,
        score=hit.score * weight,
        reason=(hit.reason + "; freshness applied").strip("; "),
        source_id=hit.source_id,
        metadata=metadata,
    )
