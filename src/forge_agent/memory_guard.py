from __future__ import annotations

import re
from collections.abc import Iterable

_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "i", "in", "is", "it", "me", "my", "of", "on", "or", "that", "the", "this", "to", "with", "you", "your",
}
_TOKEN_RE = re.compile(r"[a-z0-9_\-]+", re.IGNORECASE)


def normalize_memory_text(value: str) -> str:
    """Normalize user and memory text for lightweight local matching."""

    return " ".join(_TOKEN_RE.findall(value.lower()))


def tokenize_memory_text(value: str) -> set[str]:
    """Return meaningful normalized tokens, keeping short ids and product names."""

    return {token for token in normalize_memory_text(value).split() if token and token not in _STOPWORDS}


def memory_overlap_score(query: str, candidates: Iterable[str]) -> float:
    """Score how strongly candidate text overlaps the user's current request."""

    query_tokens = tokenize_memory_text(query)
    if not query_tokens:
        return 0.0
    candidate_tokens: set[str] = set()
    for candidate in candidates:
        candidate_tokens.update(tokenize_memory_text(candidate))
    if not candidate_tokens:
        return 0.0
    overlap = query_tokens & candidate_tokens
    return len(overlap) / max(1, len(query_tokens))


def has_memory_anchor(query: str, *candidate_texts: str) -> bool:
    """Return true when a memory candidate is anchored in the current task."""

    return memory_overlap_score(query, candidate_texts) > 0
