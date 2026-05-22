from __future__ import annotations

from collections import defaultdict
from dataclasses import replace
from typing import Any

from .memory_freshness import build_temporal_query_profile
from .memory_guard import canonical_guard_text, parse_preference_content, query_requests_history
from .memory_ranking import normalize_ranking_path, query_requests_current_state
from .models import MemoryRecallHit

_CONFLICT_MARKERS = (
    'which',
    'actual',
    'really',
    'right now',
    'correct',
    'current',
    'latest',
    'previous',
    'before',
)


def build_resolution_profile(query: str) -> dict[str, bool]:
    lowered = canonical_guard_text(query)
    temporal = build_temporal_query_profile(query)
    return {
        'history_intent': bool(temporal['history_intent']),
        'current_intent': bool(query_requests_current_state(query) or temporal['current_intent']),
        'latest_intent': bool(temporal['latest_intent']),
        'previous_intent': bool(temporal['previous_intent']),
        'note_focused': bool(temporal['note_focused']),
        'conflict_sensitive': any(marker in lowered for marker in _CONFLICT_MARKERS),
    }


def _slot_key(hit: MemoryRecallHit) -> str:
    metadata = dict(hit.metadata or {})
    path = normalize_ranking_path(metadata.get('path', ''))
    if hit.layer in {'archive', 'episodic'}:
        base_key = str(metadata.get('archive_type', '') or metadata.get('event_type', '') or hit.key or '').strip()
        if base_key:
            return f'{hit.layer}:{base_key}@{path}' if path else f'{hit.layer}:{base_key}'
    guard_keys = [str(item).strip() for item in (metadata.get('guard_canonical_keys') or []) if str(item).strip()]
    if guard_keys:
        return guard_keys[0]
    stale_keys = [str(item).strip() for item in (metadata.get('guard_stale_keys') or []) if str(item).strip()]
    if stale_keys:
        return stale_keys[0]
    subject = str(metadata.get('subject', '') or '').strip()
    predicate = str(metadata.get('predicate', '') or '').strip()
    if subject and predicate:
        return f'{subject}.{predicate}'
    if path.startswith('relationships/customers/'):
        return 'active_customer.current'
    if hit.layer == 'core':
        return str(hit.key or '').strip()
    if hit.layer == 'semantic':
        pref_key, _ = parse_preference_content(hit.content)
        return str(pref_key or hit.key or '').strip()
    return str(hit.key or '').strip() or f'{hit.layer}:{path}'


def _canonical_value(hit: MemoryRecallHit) -> str:
    metadata = dict(hit.metadata or {})
    if hit.layer == 'semantic':
        _, pref_value = parse_preference_content(hit.content)
        if pref_value:
            return canonical_guard_text(pref_value)
    return canonical_guard_text(hit.content)


def _authority(hit: MemoryRecallHit, *, profile: dict[str, bool]) -> float:
    metadata = dict(hit.metadata or {})
    status = canonical_guard_text(metadata.get('status', ''))
    if profile['history_intent']:
        base = {
            'archive': 1.0,
            'episodic': 0.92,
            'temporal': 0.88 if status != 'active' else 0.34,
            'semantic': 0.38,
            'core': 0.28,
        }.get(hit.layer, 0.2)
    elif profile['latest_intent'] and profile['note_focused']:
        base = {
            'archive': 1.06,
            'episodic': 0.84,
            'temporal': 0.52 if status == 'active' else 0.28,
            'semantic': 0.40,
            'core': 0.26,
        }.get(hit.layer, 0.2)
    else:
        base = {
            'temporal': 1.0 if status == 'active' else 0.36,
            'core': 0.88,
            'semantic': 0.72,
            'episodic': 0.42,
            'archive': 0.34,
        }.get(hit.layer, 0.2)
    if metadata.get('guard_canonical_keys'):
        base += 0.08
    if metadata.get('guard_stale_keys') and not profile['history_intent']:
        base -= 0.08
    alignment = float(metadata.get('ranking_path_alignment', 0.0) or 0.0)
    base += max(0.0, alignment) * (0.08 if not profile['history_intent'] else 0.03)
    freshness = float(metadata.get('freshness_score', 0.0) or 0.0)
    base += freshness * (0.05 if profile['history_intent'] else 0.07)
    return round(base, 4)


def resolve_memory_hits(
    hits: list[MemoryRecallHit],
    *,
    query: str,
) -> tuple[list[MemoryRecallHit], dict[str, Any]]:
    profile = build_resolution_profile(query)
    grouped: dict[str, list[MemoryRecallHit]] = defaultdict(list)
    for hit in hits:
        slot = _slot_key(hit)
        if slot:
            grouped[slot].append(hit)

    winners: dict[str, tuple[str, str]] = {}
    conflict_slots = 0
    resolved_slots = 0
    suppressed_conflicts = 0
    current_protected = 0
    history_released = 0
    reranked: list[MemoryRecallHit] = []

    for slot, rows in grouped.items():
        distinct_values = {(_canonical_value(item), item.layer) for item in rows if _canonical_value(item)}
        if len(distinct_values) < 2:
            continue
        conflict_slots += 1
        scored_rows = []
        for item in rows:
            authority = _authority(item, profile=profile)
            scored_rows.append((item.score + authority, authority, item))
        scored_rows.sort(key=lambda row: (row[0], row[1]), reverse=True)
        winner = scored_rows[0][2]
        winners[slot] = (_canonical_value(winner), winner.layer)
        resolved_slots += 1
        if not profile['history_intent']:
            current_protected += 1
        else:
            history_released += 1

    for hit in hits:
        metadata = dict(hit.metadata or {})
        slot = _slot_key(hit)
        authority = _authority(hit, profile=profile)
        adjustment = 0.0
        reasons: list[str] = []
        metadata['resolution_slot'] = slot
        metadata['resolution_authority'] = authority
        if slot in winners:
            winning_value, winning_layer = winners[slot]
            value = _canonical_value(hit)
            conflict = value != winning_value or hit.layer != winning_layer
            metadata['resolution_conflict'] = True
            metadata['resolution_winner_value'] = winning_value
            metadata['resolution_winner_layer'] = winning_layer
            if not conflict:
                adjustment += 0.16 + (0.06 if profile['current_intent'] else 0.03)
                reasons.append('resolution-winner-bonus')
            else:
                suppressed_conflicts += 1
                if profile['history_intent']:
                    adjustment -= 0.05
                    reasons.append('history-conflict-soft-penalty')
                else:
                    adjustment -= 0.18
                    reasons.append('current-conflict-penalty')
                if metadata.get('guard_stale_keys'):
                    adjustment -= 0.08
                    reasons.append('stale-conflict-penalty')
        else:
            metadata['resolution_conflict'] = False

        if profile['previous_intent'] and hit.layer == 'temporal' and canonical_guard_text(metadata.get('status', '')) == 'active':
            adjustment -= 0.14
            reasons.append('previous-active-resolution-penalty')
        if profile['latest_intent'] and profile['note_focused'] and hit.layer == 'archive':
            adjustment += 0.08
            reasons.append('latest-note-resolution-bonus')
        metadata['resolution_adjustment'] = round(adjustment, 4)
        metadata['resolution_reasons'] = reasons
        reranked.append(replace(hit, score=round(hit.score + adjustment, 4), metadata=metadata))

    priority = {'core': 5, 'temporal': 4, 'semantic': 3, 'episodic': 2, 'archive': 1}
    reranked.sort(key=lambda item: (item.score, priority.get(item.layer, 0)), reverse=True)
    summary = {
        'current_intent': bool(profile['current_intent']),
        'history_intent': bool(profile['history_intent']),
        'conflict_slot_count': conflict_slots,
        'resolved_slot_count': resolved_slots,
        'suppressed_conflicts': suppressed_conflicts,
        'current_protected_slots': current_protected,
        'history_released_slots': history_released,
        'top_resolution_slot': str((reranked[0].metadata or {}).get('resolution_slot', '')) if reranked else '',
        'top_resolution_conflict': bool((reranked[0].metadata or {}).get('resolution_conflict', False)) if reranked else False,
        'top_resolution_winner_layer': str((reranked[0].metadata or {}).get('resolution_winner_layer', '')) if reranked else '',
    }
    return reranked, summary


def summarize_resolved_hits(hits: list[MemoryRecallHit], *, limit: int = 3) -> dict[str, Any]:
    top_hits = hits[: max(0, int(limit))]
    slots: list[str] = []
    conflicts = 0
    winners: list[str] = []
    for item in top_hits:
        metadata = dict(item.metadata or {})
        slot = str(metadata.get('resolution_slot', '') or '')
        if slot:
            slots.append(slot)
        if bool(metadata.get('resolution_conflict', False)):
            conflicts += 1
        winner_layer = str(metadata.get('resolution_winner_layer', '') or '')
        if winner_layer:
            winners.append(winner_layer)
    return {
        'top_hit_count': len(top_hits),
        'top_slots': slots,
        'conflict_top_hits': conflicts,
        'winner_layers': winners,
    }
