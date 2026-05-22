from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from typing import Any, Optional

from .memory_guard import canonical_guard_text, query_requests_history
from .models import MemoryRecallHit

_LATEST_MARKERS = (
    'latest',
    'most recent',
    'recent',
    'recently',
    'newest',
    'current',
    'now',
    'today',
)

_PREVIOUS_MARKERS = (
    'previous',
    'before',
    'prior',
    'earlier',
    'last one',
)

_NOTE_MARKERS = (
    'note',
    'notes',
    'archive',
    'message',
    'email',
    'meeting note',
)


def build_temporal_query_profile(query: str) -> dict[str, bool]:
    lowered = canonical_guard_text(query)
    history_intent = query_requests_history(lowered)
    latest_intent = any(marker in lowered for marker in _LATEST_MARKERS)
    previous_intent = any(marker in lowered for marker in _PREVIOUS_MARKERS)
    note_focused = any(marker in lowered for marker in _NOTE_MARKERS)
    return {
        'history_intent': history_intent,
        'latest_intent': latest_intent,
        'previous_intent': previous_intent,
        'current_intent': latest_intent and not history_intent,
        'note_focused': note_focused,
    }


def _parse_datetime(value: Any) -> Optional[datetime]:
    text = str(value or '').strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace('Z', '+00:00'))
    except ValueError:
        return None


def _datetime_score(value: Any) -> float:
    parsed = _parse_datetime(value)
    if parsed is None:
        return 0.0
    return parsed.timestamp()


def _freshness_bucket(hit: MemoryRecallHit) -> str:
    metadata = dict(hit.metadata or {})
    status = str(metadata.get('status', '') or '').strip().lower()
    if status in {'active', 'current'}:
        return 'fresh'
    if status in {'inactive', 'expired', 'closed', 'archived'}:
        return 'stale'
    if metadata.get('valid_to'):
        return 'stale'
    if metadata.get('updated_at') or metadata.get('created_at'):
        return 'warm'
    if hit.layer in {'core', 'working'}:
        return 'warm'
    return 'cool'


def _freshness_rank(hit: MemoryRecallHit, *, profile: dict[str, bool]) -> tuple[float, float, float]:
    metadata = dict(hit.metadata or {})
    bucket = _freshness_bucket(hit)
    bucket_weight = {'fresh': 4.0, 'warm': 2.5, 'cool': 1.0, 'stale': -2.0}.get(bucket, 0.0)
    time_score = max(
        _datetime_score(metadata.get('updated_at')),
        _datetime_score(metadata.get('created_at')),
        _datetime_score(metadata.get('valid_from')),
        _datetime_score(metadata.get('valid_to')),
    )
    layer_bonus = 0.0
    if profile.get('latest_intent') and hit.layer in {'temporal', 'working'}:
        layer_bonus += 1.5
    if profile.get('previous_intent') and hit.layer in {'archive', 'episodic'}:
        layer_bonus += 1.0
    if profile.get('note_focused') and hit.layer in {'archive', 'episodic'}:
        layer_bonus += 1.0
    return (bucket_weight + layer_bonus, time_score, float(hit.score))


def rerank_memory_freshness(hits: list[MemoryRecallHit], *, query: str) -> tuple[list[MemoryRecallHit], dict[str, Any]]:
    profile = build_temporal_query_profile(query)
    adjusted: list[MemoryRecallHit] = []
    for hit in hits:
        metadata = dict(hit.metadata or {})
        bucket = _freshness_bucket(hit)
        metadata['freshness_bucket'] = bucket
        rank = _freshness_rank(hit, profile=profile)
        metadata['freshness_rank'] = list(rank)
        score = float(hit.score)
        if bucket == 'fresh':
            score += 1.25
        elif bucket == 'warm':
            score += 0.50
        elif bucket == 'stale' and not profile.get('history_intent'):
            score -= 1.50
        if profile.get('latest_intent') and bucket == 'fresh':
            score += 1.0
        if profile.get('previous_intent') and bucket == 'stale':
            score += 0.75
        adjusted.append(replace(hit, score=round(score, 4), metadata=metadata))
    adjusted.sort(key=lambda item: _freshness_rank(item, profile=profile), reverse=True)
    return adjusted, summarize_fresh_hits(adjusted, profile=profile)


def summarize_fresh_hits(hits: list[MemoryRecallHit], *, profile: Optional[dict[str, bool]] = None, limit: int = 3) -> dict[str, Any]:
    rows = hits[:max(0, int(limit))]
    buckets: dict[str, int] = {}
    for hit in hits:
        bucket = str((hit.metadata or {}).get('freshness_bucket', '') or _freshness_bucket(hit))
        buckets[bucket] = buckets.get(bucket, 0) + 1
    return {
        'profile': dict(profile or {}),
        'top_keys': [hit.key for hit in rows],
        'top_buckets': [str((hit.metadata or {}).get('freshness_bucket', '') or _freshness_bucket(hit)) for hit in rows],
        'bucket_counts': buckets,
        'hit_count': len(hits),
    }
