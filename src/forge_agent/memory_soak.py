from __future__ import annotations

import hashlib
import json
from typing import Any, Optional


def _stable_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def _recall_path(recall_hits: Any) -> str:
    rows = list(recall_hits or []) if isinstance(recall_hits, list) else []
    for row in rows:
        if not isinstance(row, dict):
            continue
        metadata = dict(row.get('metadata') or {})
        path = str(metadata.get('path', '') or '').strip()
        if path:
            return path
    return ''


def build_memory_soak_snapshot(
    *,
    memory_engine: Optional[dict[str, Any]] = None,
    memory_continuity: Optional[dict[str, Any]] = None,
    recall_hits: Optional[list[dict[str, Any]]] = None,
) -> dict[str, Any]:
    engine = dict(memory_engine or {})
    continuity = dict(memory_continuity or {})
    freshness = dict(engine.get('freshness') or {})
    resolution = dict(engine.get('resolution') or {})
    focus_paths = [str(item).strip() for item in (engine.get('focus_paths') or []) if str(item).strip()]
    continuity_focus_path = str(engine.get('continuity_focus_path', '') or continuity.get('focus_path', '') or '').strip()
    top_slot = str(engine.get('top_slot', '') or '').strip()
    top_bucket = str(engine.get('top_bucket', '') or '').strip()
    top_path = _recall_path(recall_hits)
    contaminated_top_hits = int(engine.get('contaminated_top_hits', 0) or 0)
    suppressed_conflicts = int(engine.get('suppressed_conflicts', 0) or 0)
    stale_top_hits = int(freshness.get('stale_top_hits', 0) or 0)
    conflict_top_hits = int(resolution.get('conflict_top_hits', 0) or 0)
    current_intent = bool(engine.get('current_intent', False) or (engine.get('profile') or {}).get('current_intent', False))
    history_intent = bool(engine.get('history_intent', False) or (engine.get('profile') or {}).get('history_intent', False))

    continuity_drift = False
    if continuity_focus_path and top_path and current_intent:
        related_archive = False
        if continuity_focus_path.startswith('relationships/customers/') and top_path.startswith('archive/sessions/'):
            focus_entity = continuity_focus_path.rsplit('/', 1)[-1]
            related_archive = focus_entity and focus_entity in top_path
        continuity_drift = not related_archive and not (
            top_path == continuity_focus_path
            or top_path.startswith(continuity_focus_path + '/')
            or continuity_focus_path.startswith(top_path + '/')
        )

    contamination_score = contaminated_top_hits + suppressed_conflicts + conflict_top_hits
    if current_intent and (top_bucket == 'stale' or stale_top_hits > 1):
        contamination_score += max(1, stale_top_hits)
    if continuity_drift:
        contamination_score += 2

    if contamination_score >= 5:
        risk_level = 'high'
    elif contamination_score >= 2:
        risk_level = 'medium'
    else:
        risk_level = 'low'

    snapshot_payload = {
        'focus_paths': focus_paths[:4],
        'continuity_focus_path': continuity_focus_path,
        'top_slot': top_slot,
        'top_bucket': top_bucket,
        'top_path': top_path,
        'risk_level': risk_level,
        'contamination_score': contamination_score,
        'current_intent': current_intent,
        'history_intent': history_intent,
    }
    digest = hashlib.sha1(_stable_json(snapshot_payload).encode('utf-8')).hexdigest()[:16]
    return {
        **snapshot_payload,
        'digest': digest,
        'contaminated_top_hits': contaminated_top_hits,
        'suppressed_conflicts': suppressed_conflicts,
        'stale_top_hits': stale_top_hits,
        'conflict_top_hits': conflict_top_hits,
        'continuity_drift': continuity_drift,
        'soak_ready': risk_level == 'low' and bool(digest),
    }


def update_memory_soak_window(
    previous_window: Optional[dict[str, Any]],
    snapshot: Optional[dict[str, Any]],
    *,
    max_history: int = 12,
) -> dict[str, Any]:
    prev = dict(previous_window or {})
    current = dict(snapshot or {})
    digest = str(current.get('digest', '') or '').strip()
    previous_digest = str(prev.get('last_digest', '') or '').strip()
    stable_digest_runs = int(prev.get('stable_digest_runs', 0) or 0) + 1 if digest and digest == previous_digest else (1 if digest else 0)
    risk_level = str(current.get('risk_level', '') or 'low')
    previous_low_risk = int(prev.get('low_risk_streak', 0) or 0)
    low_risk_streak = previous_low_risk + 1 if risk_level == 'low' else 0
    contamination_spike_count = int(prev.get('contamination_spike_count', 0) or 0) + (1 if risk_level == 'high' else 0)
    drift_count = int(prev.get('drift_count', 0) or 0) + (1 if bool(current.get('continuity_drift', False)) else 0)
    history = [row for row in list(prev.get('history') or []) if isinstance(row, dict)]
    history.append({
        'digest': digest,
        'risk_level': risk_level,
        'focus_path': str(current.get('continuity_focus_path', '') or ''),
        'top_slot': str(current.get('top_slot', '') or ''),
        'contamination_score': int(current.get('contamination_score', 0) or 0),
    })
    history = history[-max(1, int(max_history)):]
    return {
        'last_digest': digest,
        'stable_digest_runs': stable_digest_runs,
        'low_risk_streak': low_risk_streak,
        'contamination_spike_count': contamination_spike_count,
        'drift_count': drift_count,
        'soak_ready': bool(stable_digest_runs >= 3 and low_risk_streak >= 3 and contamination_spike_count == 0),
        'current_risk_level': risk_level,
        'current_focus_path': str(current.get('continuity_focus_path', '') or ''),
        'current_top_slot': str(current.get('top_slot', '') or ''),
        'history': history,
    }


def summarize_memory_soak_window(window: Optional[dict[str, Any]]) -> dict[str, Any]:
    payload = dict(window or {})
    history = [row for row in list(payload.get('history') or []) if isinstance(row, dict)]
    return {
        'stable_digest_runs': int(payload.get('stable_digest_runs', 0) or 0),
        'low_risk_streak': int(payload.get('low_risk_streak', 0) or 0),
        'contamination_spike_count': int(payload.get('contamination_spike_count', 0) or 0),
        'drift_count': int(payload.get('drift_count', 0) or 0),
        'soak_ready': bool(payload.get('soak_ready', False)),
        'current_risk_level': str(payload.get('current_risk_level', '') or ''),
        'history_size': len(history),
    }
