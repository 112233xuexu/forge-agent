from __future__ import annotations

from typing import Any, Optional

from .memory_continuity import continuity_focus_path
from .memory_freshness import rerank_memory_freshness, summarize_fresh_hits
from .memory_guard import canonical_guard_text
from .memory_ranking import build_query_focus_profile, rerank_memory_hits, summarize_ranked_hits
from .memory_resolution import build_resolution_profile, resolve_memory_hits, summarize_resolved_hits
from .models import MemoryRecallHit


def build_memory_engine_profile(
    query: str,
    *,
    focus_paths: Optional[list[str]] = None,
    continuity_state: Optional[dict[str, Any]] = None,
    guard_state: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    ranking = build_query_focus_profile(query)
    resolution = build_resolution_profile(query)
    continuity_state = dict(continuity_state or {})
    guard_rules = list((guard_state or {}).get('rules') or []) if isinstance(guard_state, dict) else []
    continuity_path = continuity_focus_path(continuity_state)
    normalized_focus = [str(item).strip() for item in (focus_paths or []) if str(item).strip()]
    if continuity_path and continuity_path not in normalized_focus:
        normalized_focus.append(continuity_path)
    if not continuity_path and normalized_focus:
        continuity_path = normalized_focus[0]
    guarded_keys = [str(rule.get('key', '') or '').strip() for rule in guard_rules if str(rule.get('key', '') or '').strip()]
    return {
        'query': canonical_guard_text(query),
        'current_intent': bool(ranking.get('current_intent')),
        'history_intent': bool(ranking.get('history_intent')),
        'latest_intent': bool(resolution.get('latest_intent')),
        'previous_intent': bool(resolution.get('previous_intent')),
        'note_focused': bool(resolution.get('note_focused')),
        'customer_focused': bool(ranking.get('customer_focused')),
        'preference_focused': bool(ranking.get('preference_focused')),
        'archive_focused': bool(ranking.get('archive_focused')),
        'conflict_sensitive': bool(resolution.get('conflict_sensitive')),
        'focus_paths': normalized_focus,
        'continuity_focus_path': continuity_path,
        'guard_rule_count': len(guard_rules),
        'guarded_keys': guarded_keys[:6],
    }


def run_memory_engine(
    hits: list[MemoryRecallHit],
    *,
    query: str,
    focus_paths: Optional[list[str]] = None,
    continuity_state: Optional[dict[str, Any]] = None,
    guard_state: Optional[dict[str, Any]] = None,
) -> tuple[list[MemoryRecallHit], dict[str, Any]]:
    profile = build_memory_engine_profile(
        query,
        focus_paths=focus_paths,
        continuity_state=continuity_state,
        guard_state=guard_state,
    )
    ranking_hits, ranking_summary = rerank_memory_hits(
        hits,
        query=query,
        focus_paths=list(profile.get('focus_paths') or []),
        history_intent=bool(profile.get('history_intent')),
        current_intent=bool(profile.get('current_intent')),
    )
    freshness_hits, freshness_summary = rerank_memory_freshness(ranking_hits, query=query)
    resolved_hits, resolution_summary = resolve_memory_hits(freshness_hits, query=query)

    engine_summary = {
        'profile': profile,
        'focus_paths': list(profile.get('focus_paths') or []),
        'continuity_focus_path': str(profile.get('continuity_focus_path', '') or ''),
        'guard_rule_count': int(profile.get('guard_rule_count', 0) or 0),
        'guarded_keys': list(profile.get('guarded_keys') or []),
        'ranking': ranking_summary,
        'freshness': freshness_summary,
        'resolution': resolution_summary,
        'top_slot': str((resolved_hits[0].metadata or {}).get('resolution_slot', '')) if resolved_hits else '',
        'top_bucket': str((resolved_hits[0].metadata or {}).get('freshness_bucket', '')) if resolved_hits else '',
        'contaminated_top_hits': int(ranking_summary.get('contaminated_top_hits', 0) or 0),
        'suppressed_conflicts': int(resolution_summary.get('suppressed_conflicts', 0) or 0),
        'pipeline': ['ranking', 'freshness', 'resolution'],
    }

    for index, hit in enumerate(resolved_hits[:12]):
        metadata = dict(hit.metadata or {})
        metadata['memory_engine_position'] = index + 1
        if index == 0:
            metadata['memory_engine_summary'] = {
                'focus_paths': list(engine_summary['focus_paths']),
                'top_slot': engine_summary['top_slot'],
                'top_bucket': engine_summary['top_bucket'],
                'suppressed_conflicts': engine_summary['suppressed_conflicts'],
                'guard_rule_count': engine_summary['guard_rule_count'],
                'continuity_focus_path': engine_summary['continuity_focus_path'],
            }
        hit.metadata.clear()
        hit.metadata.update(metadata)

    return resolved_hits, engine_summary


def summarize_memory_engine(
    hits: list[MemoryRecallHit],
    engine_summary: Optional[dict[str, Any]],
    *,
    limit: int = 3,
) -> dict[str, Any]:
    summary = dict(engine_summary or {})
    top_hits = hits[: max(0, int(limit))]
    ranking = summarize_ranked_hits(top_hits, limit=limit)
    freshness = summarize_fresh_hits(top_hits, limit=limit)
    resolution = summarize_resolved_hits(top_hits, limit=limit)
    return {
        'focus_paths': list(summary.get('focus_paths') or ranking.get('focus_paths') or []),
        'continuity_focus_path': str(summary.get('continuity_focus_path', '') or ''),
        'guard_rule_count': int(summary.get('guard_rule_count', 0) or 0),
        'guarded_keys': list(summary.get('guarded_keys') or []),
        'current_intent': bool((summary.get('profile') or {}).get('current_intent', False)),
        'history_intent': bool((summary.get('profile') or {}).get('history_intent', False)),
        'latest_intent': bool((summary.get('profile') or {}).get('latest_intent', False)),
        'previous_intent': bool((summary.get('profile') or {}).get('previous_intent', False)),
        'top_slot': str(summary.get('top_slot', '') or ''),
        'top_bucket': str(summary.get('top_bucket', '') or ''),
        'contaminated_top_hits': int(summary.get('contaminated_top_hits', 0) or ranking.get('contaminated_top_hits', 0) or 0),
        'suppressed_conflicts': int(summary.get('suppressed_conflicts', 0) or 0),
        'ranking': ranking,
        'freshness': freshness,
        'resolution': resolution,
        'pipeline': list(summary.get('pipeline') or ['ranking', 'freshness', 'resolution']),
    }
