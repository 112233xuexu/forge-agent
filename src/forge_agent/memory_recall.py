from __future__ import annotations

from .memory_models import MemoryItem, MemoryRecall


def recall_memories(
    items: list[MemoryItem],
    query: str,
    *,
    limit: int = 5,
    include_sensitive: bool = False,
    scopes: set[str] | None = None,
    wings: set[str] | None = None,
) -> list[MemoryRecall]:
    """Return deterministic, bounded, explainable memory matches.

    This helper is intentionally behavior-preserving. It mirrors the previous
    MemoryStore.recall scoring and filtering logic while making the recall
    implementation independently testable.
    """

    tokens = tokens_for(query)
    normalized_scopes = normalize_filter(scopes)
    normalized_wings = normalize_filter(wings)
    if not tokens or limit <= 0:
        return []

    candidates: list[MemoryRecall] = []
    for item in items:
        if normalized_scopes and item.scope not in normalized_scopes:
            continue
        if normalized_wings and item.wing not in normalized_wings:
            continue
        if item.safety == "sensitive" and not include_sensitive:
            continue
        score, reasons = score_item(item, tokens)
        if score > 0:
            candidates.append(MemoryRecall(memory=item, score=score, reasons=reasons))
    candidates.sort(key=lambda match: (-match.score, match.memory.created_at, match.memory.id))
    return candidates[:limit]


def score_item(item: MemoryItem, query_tokens: set[str]) -> tuple[float, list[str]]:
    reasons: list[str] = []
    score = 0.0
    content_tokens = tokens_for(item.content)
    path_tokens = tokens_for(" ".join([item.scope, item.wing, item.room, item.closet, item.drawer]))
    content_overlap = query_tokens & content_tokens
    path_overlap = query_tokens & path_tokens
    if content_overlap:
        score += len(content_overlap) * 2.0
        reasons.append("content token match: " + ", ".join(sorted(content_overlap)))
    if path_overlap:
        score += len(path_overlap) * 1.0
        reasons.append("palace path match: " + ", ".join(sorted(path_overlap)))
    if item.confidence != 1.0 and score > 0:
        score *= max(0.0, min(item.confidence, 1.0))
        reasons.append(f"confidence adjusted: {item.confidence}")
    return round(score, 3), reasons


def tokens_for(text: str) -> set[str]:
    normalized = "".join(ch.lower() if ch.isalnum() else " " for ch in text)
    return {token for token in normalized.split() if len(token) >= 2}


def normalize_filter(values: set[str] | None) -> set[str]:
    if not values:
        return set()
    return {value.strip() for value in values if value.strip()}
