from __future__ import annotations

from dataclasses import replace
from typing import Any, Iterable, Optional

from .memory_guard import canonical_guard_text, query_requests_history
from .models import MemoryRecallHit

_CURRENT_MARKERS = (
    'current',
    'latest',
    'now',
    'today',
    'usual',
    'normally',
    'default',
    'active',
    'preferred',
)

_CUSTOMER_MARKERS = (
    'customer',
    'client',
    'account',
    'renewal',
    'follow up',
    'followup',
    'contract',
)

_PREFERENCE_MARKERS = (
    'translate',
    'translation',
    'language',
    'style',
    'tone',
    'rewrite',
    'preference',
)

_ARCHIVE_MARKERS = (
    'exact',
    'verbatim',
    'quote',
    'quoted',
    'original',
    'wording',
    'note',
    'notes',
)


def normalize_ranking_path(path: Any) -> str:
    return canonical_guard_text(str(path or '').replace('\\', '/')).strip('/')


def query_requests_current_state(query: str) -> bool:
    lowered = canonical_guard_text(query)
    if not lowered or query_requests_history(lowered):
        return False
    return any(marker in lowered for marker in _CURRENT_MARKERS)


def build_query_focus_profile(query: str) -> dict[str, Any]:
    lowered = canonical_guard_text(query)
    history_intent = query_requests_history(lowered)
    current_intent = query_requests_current_state(lowered)
    customer_focused = any(marker in lowered for marker in _CUSTOMER_MARKERS)
    preference_focused = any(marker in lowered for marker in _PREFERENCE_MARKERS)
    archive_focused = any(marker in lowered for marker in _ARCHIVE_MARKERS)
    return {
        'query': lowered,
        'history_intent': history_intent,
        'current_intent': current_intent,
        'customer_focused': customer_focused,
        'preference_focused': preference_focused,
        'archive_focused': archive_focused,
    }


def _path_family(path: str) -> str:
    normalized = normalize_ranking_path(path)
    if normalized.startswith('relationships/customers/'):
        return 'relationships/customers'
    if normalized.startswith('self/preferences'):
        return 'self/preferences'
    return '/'.join(normalized.split('/')[:2])


def path_focus_alignment(path: Any, focus_paths: Iterable[str]) -> float:
    candidate = normalize_ranking_path(path)
    normalized_focus = [normalize_ranking_path(item) for item in focus_paths if normalize_ranking_path(item)]
    if not candidate or not normalized_focus:
        return 0.0
    positive = 0.0
    negative = 0.0
    for focus in normalized_focus:
        if candidate == focus:
            positive = max(positive, 1.0)
            continue
        if candidate.startswith(focus + '/') or focus.startswith(candidate + '/'):
            positive = max(positive, 0.82)
            continue
        candidate_family = _path_family(candidate)
        focus_family = _path_family(focus)
        if candidate_family and candidate_family == focus_family:
            if candidate_family == 'relationships/customers':
                negative = min(negative, -0.92)
            else:
                positive = max(positive, 0.34)
            continue
        if candidate.startswith('archive/sessions/') and focus.startswith('relationships/customers/'):
            positive = max(positive, 0.22)
            continue
        if focus.startswith('archive/sessions/') and candidate.startswith('relationships/customers/'):
            positive = max(positive, 0.22)
    return round(positive if positive > 0 else negative, 4)


def rerank_memory_hits(
    hits: list[MemoryRecallHit],
    *,
    query: str,
    focus_paths: Optional[list[str]] = None,
    history_intent: Optional[bool] = None,
    current_intent: Optional[bool] = None,
) -> tuple[list[MemoryRecallHit], dict[str, Any]]:
    focus_profile = build_query_focus_profile(query)
    if history_intent is None:
        history_intent = bool(focus_profile['history_intent'])
    if current_intent is None:
        current_intent = bool(focus_profile['current_intent'])
    focus_paths = [normalize_ranking_path(item) for item in list(focus_paths or []) if normalize_ranking_path(item)]
    reranked: list[MemoryRecallHit] = []
    contaminated_top_candidates = 0
    for hit in hits:
        metadata = dict(hit.metadata or {})
        candidate_path = normalize_ranking_path(
            metadata.get('path') or metadata.get('graph_path') or metadata.get('palace_path') or ''
        )
        path_alignment = path_focus_alignment(candidate_path, focus_paths)
        adjustment = 0.0
        reasons: list[str] = []
        status = canonical_guard_text(metadata.get('status', ''))
        guard_canonical_keys = list(metadata.get('guard_canonical_keys') or [])
        guard_stale_keys = list(metadata.get('guard_stale_keys') or [])
        if current_intent:
            if hit.layer in {'core', 'temporal'}:
                if not (focus_profile['archive_focused'] and hit.layer == 'temporal'):
                    adjustment += 0.08
                    reasons.append('current-layer-bias')
                else:
                    adjustment -= 0.08
                    reasons.append('archive-query-temporal-penalty')
            if status in {'contradicted', 'inactive', 'stale', 'superseded'}:
                adjustment -= 0.16
                reasons.append('stale-status-penalty')
            if guard_stale_keys:
                adjustment -= 0.18
                reasons.append('guard-stale-penalty')
            if guard_canonical_keys:
                adjustment += 0.10
                reasons.append('guard-canonical-bonus')
            if path_alignment > 0:
                adjustment += 0.24 * path_alignment
                reasons.append('focus-aligned')
            elif path_alignment < 0:
                adjustment += 0.28 * path_alignment
                reasons.append('focus-mismatch')
            if focus_profile['customer_focused'] and hit.layer in {'archive', 'episodic'} and path_alignment < 0:
                adjustment -= 0.08
                reasons.append('customer-contamination-penalty')
            if hit.layer == 'archive' and guard_stale_keys and float(metadata.get('verbatim_overlap', 0.0) or 0.0) >= 0.25:
                adjustment -= 0.06
                reasons.append('stale-verbatim-penalty')
        elif history_intent:
            if guard_stale_keys:
                adjustment += 0.12
                reasons.append('history-stale-release')
            if hit.layer == 'archive':
                adjustment += 0.06
                reasons.append('history-archive-bonus')
            if status and status != 'active':
                adjustment += 0.05
                reasons.append('history-status-release')
            if path_alignment > 0:
                adjustment += 0.08 * path_alignment
                reasons.append('history-focus-aligned')
        else:
            if path_alignment > 0:
                adjustment += 0.10 * path_alignment
                reasons.append('focus-aligned')
            elif path_alignment < 0:
                adjustment += 0.14 * path_alignment
                reasons.append('focus-mismatch')
            if guard_canonical_keys:
                adjustment += 0.04
                reasons.append('guard-canonical-bonus')

        if focus_profile['archive_focused'] and hit.layer == 'archive':
            adjustment += 0.14
            reasons.append('archive-query-bias')

        if guard_stale_keys and not history_intent and (path_alignment < 0 or hit.layer == 'archive'):
            contaminated_top_candidates += 1

        metadata['ranking_focus_paths'] = focus_paths
        metadata['ranking_path_alignment'] = round(path_alignment, 4)
        metadata['ranking_adjustment'] = round(adjustment, 4)
        metadata['ranking_reasons'] = reasons
        metadata['ranking_current_intent'] = bool(current_intent)
        metadata['ranking_history_intent'] = bool(history_intent)
        reranked.append(replace(hit, score=round(hit.score + adjustment, 4), metadata=metadata))

    priority = {'core': 5, 'temporal': 4, 'semantic': 3, 'episodic': 2, 'archive': 1}
    reranked.sort(key=lambda item: (item.score, priority.get(item.layer, 0)), reverse=True)
    summary = {
        'focus_paths': focus_paths,
        'current_intent': bool(current_intent),
        'history_intent': bool(history_intent),
        'customer_focused': bool(focus_profile['customer_focused']),
        'preference_focused': bool(focus_profile['preference_focused']),
        'archive_focused': bool(focus_profile['archive_focused']),
        'contamination_candidates': contaminated_top_candidates,
        'top_path_alignments': [float((item.metadata or {}).get('ranking_path_alignment', 0.0) or 0.0) for item in reranked[:3]],
    }
    return reranked, summary


def summarize_ranked_hits(hits: list[MemoryRecallHit], *, limit: int = 3) -> dict[str, Any]:
    top_hits = hits[: max(0, int(limit))]
    contaminated_top = sum(1 for item in top_hits if (item.metadata or {}).get('guard_stale_keys'))
    focus_paths: list[str] = []
    for item in top_hits:
        for path in list((item.metadata or {}).get('ranking_focus_paths') or []):
            normalized = normalize_ranking_path(path)
            if normalized and normalized not in focus_paths:
                focus_paths.append(normalized)
    current_intent = bool((top_hits[0].metadata or {}).get('ranking_current_intent')) if top_hits else False
    history_intent = bool((top_hits[0].metadata or {}).get('ranking_history_intent')) if top_hits else False
    return {
        'top_hit_count': len(top_hits),
        'contaminated_top_hits': contaminated_top,
        'focus_paths': focus_paths,
        'current_intent': current_intent,
        'history_intent': history_intent,
    }
