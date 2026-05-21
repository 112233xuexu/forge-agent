from __future__ import annotations

import hashlib
import json
from typing import Any, Optional


def _stable_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def _canonical_defaults(defaults: Any) -> dict[str, str]:
    payload = dict(defaults or {}) if isinstance(defaults, dict) else {}
    rows: dict[str, str] = {}
    for key, value in payload.items():
        normalized_key = str(key or '').strip()
        if not normalized_key:
            continue
        normalized_value = str(value or '').strip()
        if not normalized_value:
            continue
        rows[normalized_key] = normalized_value
    return dict(sorted(rows.items()))


def _canonical_guard(memory_guard: Any) -> list[dict[str, Any]]:
    rules = list((memory_guard or {}).get('rules') or []) if isinstance(memory_guard, dict) else []
    rows: list[dict[str, Any]] = []
    for rule in rules:
        key = str(rule.get('key', '') or '').strip()
        canonical_content = str(rule.get('canonical_content', '') or '').strip()
        stale_values = [str(item).strip() for item in (rule.get('stale_values') or []) if str(item).strip()]
        if not key or not canonical_content:
            continue
        rows.append({
            'key': key,
            'canonical_content': canonical_content,
            'stale_values': sorted(stale_values),
        })
    rows.sort(key=lambda item: item['key'])
    return rows


def _recall_anchors(active_context: Any, *, limit: int = 6) -> list[dict[str, str]]:
    recall_hits = list((active_context or {}).get('recall_hits') or []) if isinstance(active_context, dict) else []
    anchors: list[dict[str, str]] = []
    for hit in recall_hits:
        layer = str(hit.get('layer', '') or '').strip()
        key = str(hit.get('key', '') or '').strip()
        content = str(hit.get('content', '') or '').strip()
        if not layer or not key or not content:
            continue
        anchors.append({'layer': layer, 'key': key, 'content': content})
        if len(anchors) >= limit:
            break
    return anchors


def build_memory_continuity(memory_runtime: Optional[dict[str, Any]]) -> dict[str, Any]:
    payload = dict(memory_runtime or {})
    active_context = dict(payload.get('active_context') or {})
    wakeup = dict(payload.get('wakeup') or {})
    l3_items = (((wakeup.get('layers') or {}).get('L3') or {}).get('items') or [])
    focus_path = str(payload.get('palace_path', '') or wakeup.get('palace_path', '') or active_context.get('palace_path', '') or '').strip()
    defaults = _canonical_defaults(active_context.get('defaults') or {})
    guard = _canonical_guard(active_context.get('memory_guard') or {})
    pack_names = sorted({str(item.get('name', '') or '').strip() for item in (active_context.get('context_packs') or []) if isinstance(item, dict) and str(item.get('name', '') or '').strip()})
    anchor_payload = {
        'focus_path': focus_path,
        'active_defaults': defaults,
        'guard': guard,
        'active_pack_names': pack_names,
        'wakeup_top_path': str(l3_items[0].get('graph_path', '') if l3_items else ''),
        'recall_anchors': _recall_anchors(active_context),
    }
    digest = hashlib.sha1(_stable_json(anchor_payload).encode('utf-8')).hexdigest()[:16]
    return {
        **anchor_payload,
        'digest': digest,
        'anchor_count': len(anchor_payload['recall_anchors']),
        'guard_count': len(guard),
    }


def compare_memory_continuity(previous: Optional[dict[str, Any]], current: Optional[dict[str, Any]]) -> dict[str, Any]:
    prev = dict(previous or {})
    curr = dict(current or {})
    prev_focus = str(prev.get('focus_path', '') or '').strip()
    curr_focus = str(curr.get('focus_path', '') or '').strip()
    prev_defaults = _canonical_defaults(prev.get('active_defaults') or {})
    curr_defaults = _canonical_defaults(curr.get('active_defaults') or {})
    prev_guard = {str(item.get('key', '') or ''): str(item.get('canonical_content', '') or '') for item in (prev.get('guard') or []) if str(item.get('key', '') or '')}
    curr_guard = {str(item.get('key', '') or ''): str(item.get('canonical_content', '') or '') for item in (curr.get('guard') or []) if str(item.get('key', '') or '')}

    matching_default_keys = sorted([key for key, value in prev_defaults.items() if curr_defaults.get(key) == value])
    changed_default_keys = sorted([key for key in set(prev_defaults) | set(curr_defaults) if prev_defaults.get(key) != curr_defaults.get(key)])
    matching_guard_keys = sorted([key for key, value in prev_guard.items() if curr_guard.get(key) == value])
    changed_guard_keys = sorted([key for key in set(prev_guard) | set(curr_guard) if prev_guard.get(key) != curr_guard.get(key)])

    changed_sections: list[str] = []
    if prev_focus != curr_focus:
        changed_sections.append('focus_path')
    if changed_default_keys:
        changed_sections.append('active_defaults')
    if changed_guard_keys:
        changed_sections.append('guard')
    if str(prev.get('digest', '') or '') != str(curr.get('digest', '') or ''):
        changed_sections.append('digest')

    alignment_score = 0.0
    if prev_focus and curr_focus and prev_focus == curr_focus:
        alignment_score += 4.0
    alignment_score += float(len(matching_default_keys))
    alignment_score += 0.5 * float(len(matching_guard_keys))
    if prev_focus and str(curr.get('wakeup_top_path', '') or '').strip() == prev_focus:
        alignment_score += 1.0

    return {
        'status': 'stable' if not changed_sections else ('drifted' if 'focus_path' in changed_sections or len(changed_default_keys) >= 2 else 'changed'),
        'previous_focus_path': prev_focus,
        'current_focus_path': curr_focus,
        'changed_sections': changed_sections,
        'matching_default_keys': matching_default_keys,
        'changed_default_keys': changed_default_keys,
        'matching_guard_keys': matching_guard_keys,
        'changed_guard_keys': changed_guard_keys,
        'alignment_score': round(alignment_score, 4),
        'digest_changed': str(prev.get('digest', '') or '') != str(curr.get('digest', '') or ''),
    }


def continuity_focus_path(continuity_state: Optional[dict[str, Any]]) -> str:
    return str((continuity_state or {}).get('focus_path', '') or '').strip()
