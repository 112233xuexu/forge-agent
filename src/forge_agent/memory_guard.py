from __future__ import annotations

import re
from typing import Any, Optional

_HISTORY_MARKERS = (
    'before',
    'previous',
    'previously',
    'used to',
    'old value',
    'history',
    'historical',
    'earlier',
    'formerly',
    'what was',
)


def canonical_guard_text(value: Any) -> str:
    text = str(value or '').strip().lower()
    return re.sub(r'\s+', ' ', text)


def guard_value_in_text(content: Any, value: Any) -> bool:
    haystack = canonical_guard_text(content)
    needle = canonical_guard_text(value)
    if not haystack or not needle:
        return False
    if len(needle) <= 2:
        return False
    if ' ' in needle or any(ch in needle for ch in '=:/-_'):
        return needle in haystack
    return re.search(r'(?<!\w)' + re.escape(needle) + r'(?!\w)', haystack) is not None


def parse_preference_content(content: str) -> tuple[Optional[str], Optional[str]]:
    raw = str(content or '')
    if '=' not in raw:
        return None, None
    key, value = raw.split('=', 1)
    key = key.strip() or None
    value = value.strip() or None
    return key, value


def query_requests_history(query: str) -> bool:
    lowered = canonical_guard_text(query)
    if not lowered:
        return False
    return any(marker in lowered for marker in _HISTORY_MARKERS)


def summarize_guard_rules(rules_by_scope: dict[str, dict[str, dict[str, Any]]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for scope, rules in rules_by_scope.items():
        for key, rule in rules.items():
            stale_values = sorted({canonical_guard_text(item): item for item in rule.get('stale_values', []) if str(item or '').strip()}.values())
            canonical_content = str(rule.get('canonical_content') or '').strip()
            rows.append({
                'scope': scope,
                'key': key,
                'canonical_content': canonical_content,
                'stale_values': stale_values,
                'stale_count': len(stale_values),
                'sources': sorted(set(rule.get('sources', []))),
            })
    rows.sort(key=lambda item: (0 if str(item['scope']).startswith('session:') else 1, item['key']))
    return rows
