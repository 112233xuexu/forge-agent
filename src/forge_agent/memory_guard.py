from __future__ import annotations

import re
from typing import Any


def canonical_guard_text(text: str | None) -> str:
    value = str(text or "").strip().lower()
    value = re.sub(r"\s+", " ", value)
    return value


def guard_value_in_text(value: str, text: str) -> bool:
    expected = canonical_guard_text(value)
    actual = canonical_guard_text(text)
    return bool(expected and expected in actual)


def parse_preference_content(content: str) -> dict[str, str]:
    text = str(content or "")
    lowered = canonical_guard_text(text)
    result: dict[str, str] = {"raw": text, "canonical": lowered}
    for marker in ["prefer", "preference", "like", "use", "default"]:
        if marker in lowered:
            result["kind"] = marker
            break
    if ":" in text:
        key, value = text.split(":", 1)
        result["key"] = canonical_guard_text(key)
        result["value"] = value.strip()
    return result


def query_requests_history(query: str) -> bool:
    text = canonical_guard_text(query)
    return any(token in text for token in ["history", "previous", "before", "last time", "remember", "过去", "之前", "上次", "记得"])


def summarize_guard_rules(rules: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "count": len(rules),
        "active": sum(1 for rule in rules if rule.get("active", True)),
        "keys": sorted(str(rule.get("key", "")) for rule in rules if rule.get("key")),
    }
