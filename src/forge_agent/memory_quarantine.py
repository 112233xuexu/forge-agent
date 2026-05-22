from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from typing import Any, Optional

from .models import MemoryRecallHit


def _stable_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def _path_related(path: str, focus_path: str) -> bool:
    normalized_path = str(path or '').strip()
    normalized_focus = str(focus_path or '').strip()
    if not normalized_path or not normalized_focus:
        return False
    return (
        normalized_path == normalized_focus
        or normalized_path.startswith(normalized_focus + '/')
        or normalized_focus.startswith(normalized_path + '/')
    )


def build_memory_quarantine_snapshot(
    hits: list[MemoryRecallHit],
    *,
    memory_engine: Optional[dict[str, Any]] = None,
    memory_soak: Optional[dict[str, Any]] = None,
    memory_recovery: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    engine = dict(memory_engine or {})
    soak = dict(memory_soak or {})
    recovery = dict(memory_recovery or {})
    profile = dict(engine.get('profile') or {})
    current_intent = bool(engine.get('current_intent', False) or profile.get('current_intent', False))
    history_intent = bool(engine.get('history_intent', False) or profile.get('history_intent', False))
    latest_intent = bool(profile.get('latest_intent', False))
    note_focused = bool(profile.get('note_focused', False))
    continuity_focus_path = str(
        engine.get('continuity_focus_path', '')
        or recovery.get('target_focus_path', '')
        or recovery.get('continuity_focus_path', '')
        or ''
    ).strip()
    soak_risk = str(soak.get('risk_level', '') or 'low')
    contamination_score = int(soak.get('contamination_score', 0) or 0)
    recovery_mode = str(recovery.get('mode', '') or '')

    quarantine_entries: list[dict[str, Any]] = []
    for hit in hits:
        metadata = dict(hit.metadata or {})
        reasons: list[str] = []
        path = str(metadata.get('path', '') or '').strip()
        slot = str(metadata.get('resolution_slot', '') or '').strip()
        if metadata.get('guard_stale_keys'):
            reasons.append('guard_stale')
        if bool(metadata.get('resolution_conflict', False)):
            reasons.append('resolution_conflict')
        if str(metadata.get('freshness_bucket', '') or '') == 'stale' and not (latest_intent and note_focused):
            reasons.append('stale_bucket')
        preference_self_path = path.startswith('self/preferences/')
        if current_intent and not history_intent and continuity_focus_path and path and not preference_self_path and not _path_related(path, continuity_focus_path):
            reasons.append('off_focus_path')
        if current_intent and not history_intent and hit.layer in {'archive', 'episodic'} and not (latest_intent and note_focused):
            reasons.append('trace_under_current')
        if not reasons:
            continue
        quarantine_entries.append({
            'source_id': str(hit.source_id or ''),
            'layer': hit.layer,
            'key': str(hit.key or ''),
            'path': path,
            'slot': slot,
            'reasons': reasons,
        })

    risk_triggered = bool(
        soak_risk in {'medium', 'high'}
        or contamination_score >= 2
        or recovery_mode in {'guarded_reanchor', 'reanchored'}
    )
    active = bool(
        quarantine_entries
        and current_intent
        and not history_intent
        and not (latest_intent and note_focused)
        and (risk_triggered or any('off_focus_path' in row.get('reasons', []) for row in quarantine_entries))
    )
    if active:
        severity = 'high' if soak_risk == 'high' or contamination_score >= 5 else 'medium'
    elif quarantine_entries:
        severity = 'low'
    else:
        severity = 'none'
    payload = {
        'active': active,
        'severity': severity,
        'continuity_focus_path': continuity_focus_path,
        'current_intent': current_intent,
        'history_intent': history_intent,
        'latest_note_query': bool(latest_intent and note_focused),
        'quarantined_source_ids': [row['source_id'] for row in quarantine_entries if row['source_id']],
        'quarantined_paths': [row['path'] for row in quarantine_entries if row['path']],
        'quarantined_slots': [row['slot'] for row in quarantine_entries if row['slot']],
        'quarantined_count': len(quarantine_entries),
        'soak_risk_level': soak_risk,
        'recovery_mode': recovery_mode,
    }
    digest = hashlib.sha1(_stable_json(payload).encode('utf-8')).hexdigest()[:16] if quarantine_entries else ''
    return {
        **payload,
        'digest': digest,
        'entries': quarantine_entries[:12],
    }


def apply_memory_quarantine(
    hits: list[MemoryRecallHit],
    quarantine: Optional[dict[str, Any]],
) -> tuple[list[MemoryRecallHit], dict[str, Any]]:
    state = dict(quarantine or {})
    if not bool(state.get('active', False)):
        return hits, state
    quarantined_ids = {str(item).strip() for item in list(state.get('quarantined_source_ids') or []) if str(item).strip()}
    if not quarantined_ids:
        return hits, state

    filtered: list[MemoryRecallHit] = []
    filtered_count = 0
    for hit in hits:
        source_id = str(hit.source_id or '').strip()
        metadata = dict(hit.metadata or {})
        metadata['memory_quarantine_active'] = True
        metadata['memory_quarantine_digest'] = str(state.get('digest', '') or '')
        if source_id and source_id in quarantined_ids:
            filtered_count += 1
            continue
        filtered.append(replace(hit, metadata=metadata))
    if not filtered:
        return hits, {**state, 'filtered_count': 0}
    return filtered, {**state, 'filtered_count': filtered_count}


def summarize_memory_quarantine(hits: list[MemoryRecallHit], quarantine: Optional[dict[str, Any]]) -> dict[str, Any]:
    state = dict(quarantine or {})
    return {
        'active': bool(state.get('active', False)),
        'severity': str(state.get('severity', '') or 'none'),
        'digest': str(state.get('digest', '') or ''),
        'continuity_focus_path': str(state.get('continuity_focus_path', '') or ''),
        'quarantined_count': int(state.get('quarantined_count', 0) or 0),
        'filtered_count': int(state.get('filtered_count', 0) or 0),
        'soak_risk_level': str(state.get('soak_risk_level', '') or ''),
        'recovery_mode': str(state.get('recovery_mode', '') or ''),
        'top_hit_count': len(hits[:3]),
        'top_layers': [item.layer for item in hits[:3]],
    }


def update_memory_quarantine_window(
    previous_window: Optional[dict[str, Any]],
    quarantine: Optional[dict[str, Any]],
    *,
    max_history: int = 12,
) -> dict[str, Any]:
    prev = dict(previous_window or {})
    current = dict(quarantine or {})
    active = bool(current.get('active', False))
    active_runs = int(prev.get('active_runs', 0) or 0) + (1 if active else 0)
    clear_runs = int(prev.get('clear_runs', 0) or 0) + (0 if active else 1)
    total_filtered = int(prev.get('total_filtered', 0) or 0) + int(current.get('filtered_count', 0) or 0)
    severity = str(current.get('severity', '') or 'none')
    severity_peak = prev.get('severity_peak', 'none') or 'none'
    rank = {'none': 0, 'low': 1, 'medium': 2, 'high': 3}
    if rank.get(severity, 0) > rank.get(str(severity_peak), 0):
        severity_peak = severity
    history = [row for row in list(prev.get('history') or []) if isinstance(row, dict)]
    history.append({
        'active': active,
        'severity': severity,
        'filtered_count': int(current.get('filtered_count', 0) or 0),
        'digest': str(current.get('digest', '') or ''),
    })
    history = history[-max(1, int(max_history)):]
    return {
        'active_runs': active_runs,
        'clear_runs': clear_runs,
        'total_filtered': total_filtered,
        'severity_peak': severity_peak,
        'last_digest': str(current.get('digest', '') or ''),
        'history': history,
    }


def summarize_memory_quarantine_window(window: Optional[dict[str, Any]]) -> dict[str, Any]:
    payload = dict(window or {})
    history = [row for row in list(payload.get('history') or []) if isinstance(row, dict)]
    return {
        'active_runs': int(payload.get('active_runs', 0) or 0),
        'clear_runs': int(payload.get('clear_runs', 0) or 0),
        'total_filtered': int(payload.get('total_filtered', 0) or 0),
        'severity_peak': str(payload.get('severity_peak', '') or 'none'),
        'history_size': len(history),
    }
