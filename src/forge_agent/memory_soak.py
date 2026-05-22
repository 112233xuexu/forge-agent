from __future__ import annotations

import hashlib
import json
from typing import Any, Optional


def _stable_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def build_memory_soak_snapshot(
    *,
    continuity_resume: Optional[dict[str, Any]] = None,
    active_context: Optional[dict[str, Any]] = None,
    hits: Optional[list[Any]] = None,
    max_hits: int = 8,
) -> dict[str, Any]:
    resume = dict(continuity_resume or {})
    context = dict(active_context or {})
    recall_hits = list(hits or context.get('recall_hits') or [])
    changed_sections = list(resume.get('changed_sections') or [])
    changed_defaults = list(resume.get('changed_default_keys') or [])
    changed_guard = list(resume.get('changed_guard_keys') or [])
    continuity_drift = bool(changed_sections)
    contamination_score = 0
    if 'focus_path' in changed_sections:
        contamination_score += 3
    contamination_score += min(4, len(changed_defaults))
    contamination_score += min(3, len(changed_guard))

    hit_rows: list[dict[str, Any]] = []
    off_path_hits = 0
    stale_hits = 0
    focus_path = str(resume.get('current_focus_path', '') or context.get('palace_path', '') or '').strip()
    for hit in recall_hits[:max(1, int(max_hits))]:
        metadata = dict(getattr(hit, 'metadata', {}) or (hit.get('metadata') if isinstance(hit, dict) else {}) or {})
        layer = str(getattr(hit, 'layer', '') or (hit.get('layer') if isinstance(hit, dict) else '') or '')
        key = str(getattr(hit, 'key', '') or (hit.get('key') if isinstance(hit, dict) else '') or '')
        path = str(metadata.get('path', '') or '')
        freshness_bucket = str(metadata.get('freshness_bucket', '') or '')
        if freshness_bucket == 'stale':
            stale_hits += 1
        if focus_path and path and not (path == focus_path or path.startswith(focus_path + '/') or focus_path.startswith(path + '/')):
            off_path_hits += 1
        hit_rows.append({'layer': layer, 'key': key, 'path': path, 'freshness_bucket': freshness_bucket})
    contamination_score += min(4, off_path_hits)
    contamination_score += min(3, stale_hits)
    if contamination_score >= 7:
        risk_level = 'high'
    elif contamination_score >= 3:
        risk_level = 'medium'
    elif contamination_score > 0:
        risk_level = 'low'
    else:
        risk_level = 'none'
    payload = {
        'continuity_drift': continuity_drift,
        'changed_sections': changed_sections,
        'changed_default_keys': changed_defaults,
        'changed_guard_keys': changed_guard,
        'focus_path': focus_path,
        'off_path_hits': off_path_hits,
        'stale_hits': stale_hits,
        'contamination_score': contamination_score,
        'risk_level': risk_level,
        'sample_hits': hit_rows,
    }
    payload['digest'] = hashlib.sha1(_stable_json(payload).encode('utf-8')).hexdigest()[:16]
    return payload


def compare_memory_soak(previous: Optional[dict[str, Any]], current: Optional[dict[str, Any]]) -> dict[str, Any]:
    prev = dict(previous or {})
    curr = dict(current or {})
    prev_score = int(prev.get('contamination_score', 0) or 0)
    curr_score = int(curr.get('contamination_score', 0) or 0)
    delta = curr_score - prev_score
    if delta > 0:
        trend = 'worse'
    elif delta < 0:
        trend = 'better'
    else:
        trend = 'stable'
    return {
        'previous_risk_level': str(prev.get('risk_level', '') or 'none'),
        'current_risk_level': str(curr.get('risk_level', '') or 'none'),
        'score_delta': delta,
        'trend': trend,
        'digest_changed': str(prev.get('digest', '') or '') != str(curr.get('digest', '') or ''),
    }


def should_pause_memory_use(soak: Optional[dict[str, Any]]) -> bool:
    state = dict(soak or {})
    return str(state.get('risk_level', '') or '') == 'high' or int(state.get('contamination_score', 0) or 0) >= 7


def update_memory_soak_window(previous_window: Optional[dict[str, Any]], soak: Optional[dict[str, Any]], *, max_history: int = 12) -> dict[str, Any]:
    prev = dict(previous_window or {})
    current = dict(soak or {})
    risk = str(current.get('risk_level', '') or 'none')
    score = int(current.get('contamination_score', 0) or 0)
    total_score = int(prev.get('total_score', 0) or 0) + score
    runs = int(prev.get('runs', 0) or 0) + 1
    high_runs = int(prev.get('high_runs', 0) or 0) + (1 if risk == 'high' else 0)
    medium_runs = int(prev.get('medium_runs', 0) or 0) + (1 if risk == 'medium' else 0)
    history = [row for row in list(prev.get('history') or []) if isinstance(row, dict)]
    history.append({'risk_level': risk, 'contamination_score': score, 'digest': str(current.get('digest', '') or '')})
    history = history[-max(1, int(max_history)):]
    return {
        'runs': runs,
        'total_score': total_score,
        'average_score': round(total_score / max(1, runs), 4),
        'high_runs': high_runs,
        'medium_runs': medium_runs,
        'last_risk_level': risk,
        'last_score': score,
        'history': history,
    }


def summarize_memory_soak_window(window: Optional[dict[str, Any]]) -> dict[str, Any]:
    payload = dict(window or {})
    history = [row for row in list(payload.get('history') or []) if isinstance(row, dict)]
    return {
        'runs': int(payload.get('runs', 0) or 0),
        'average_score': float(payload.get('average_score', 0.0) or 0.0),
        'high_runs': int(payload.get('high_runs', 0) or 0),
        'medium_runs': int(payload.get('medium_runs', 0) or 0),
        'last_risk_level': str(payload.get('last_risk_level', '') or 'none'),
        'history_size': len(history),
    }
