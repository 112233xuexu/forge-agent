from __future__ import annotations

import re

_STOPWORDS = {
    "a", "an", "and", "are", "be", "for", "from", "i", "in", "into", "is",
    "me", "my", "of", "on", "or", "our", "please", "the", "to", "with", "you",
    "this", "these", "that", "those", "next",
}

_TOKEN_ALIASES = {
    "bullets": "notes",
    "bullet": "notes",
    "transcript": "notes",
    "recap": "summarize",
    "summary": "summarize",
    "summaries": "summarize",
    "write": "draft",
    "compose": "draft",
    "reply": "followup",
    "email": "followup",
    "mail": "followup",
    "actions": "actions",
    "action": "actions",
    "tasks": "actions",
    "todo": "actions",
    "todos": "actions",
    "client": "customer",
    "account": "customer",
    "reword": "paraphrase",
    "rewrite": "paraphrase",
    "paraphrase": "paraphrase",
    "polish": "paraphrase",
    "warmer": "warm",
    "friendlier": "warm",
}


def canonicalize_text(text: str) -> str:
    normalized = text.lower()
    normalized = re.sub(r"follow[\s\-]?up", "followup", normalized)
    normalized = re.sub(r"next\s+steps", "actions", normalized)
    normalized = re.sub(r"action\s+items", "actions", normalized)
    normalized = re.sub(r"meeting\s+(notes|bullets)", "notes", normalized)
    normalized = re.sub(r"call\s+notes", "notes", normalized)
    normalized = re.sub(r"re[-\s]?write", "rewrite", normalized)
    return normalized


def tokenize(text: str) -> list[str]:
    parts = re.findall(r"[a-z0-9_]+", canonicalize_text(text))
    tokens: list[str] = []
    for part in parts:
        aliased = _TOKEN_ALIASES.get(part, part)
        if part not in _STOPWORDS and aliased not in _STOPWORDS:
            tokens.append(aliased)
    return tokens
