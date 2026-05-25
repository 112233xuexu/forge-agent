from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .plugin_registry import PluginCapability, PluginRegistry, default_plugin_registry


@dataclass(slots=True)
class PlaybookStep:
    title: str
    capability: str
    plain_language: str
    requires_confirmation: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "PlaybookStep":
        data = dict(payload or {})
        return cls(
            title=str(data["title"]),
            capability=str(data["capability"]),
            plain_language=str(data.get("plain_language", "") or ""),
            requires_confirmation=bool(data.get("requires_confirmation", False)),
        )


@dataclass(slots=True)
class Playbook:
    name: str
    description: str
    triggers: list[str]
    steps: list[PlaybookStep]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "triggers": list(self.triggers),
            "steps": [step.to_dict() for step in self.steps],
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Playbook":
        data = dict(payload or {})
        return cls(
            name=str(data["name"]),
            description=str(data.get("description", "") or ""),
            triggers=[str(item) for item in data.get("triggers", []) or []],
            steps=[PlaybookStep.from_dict(item) for item in data.get("steps", []) or []],
            metadata=dict(data.get("metadata", {}) or {}),
        )


@dataclass(slots=True)
class PlaybookMatch:
    playbook: Playbook
    score: int
    capabilities: list[PluginCapability]

    def to_dict(self) -> dict[str, Any]:
        return {
            "playbook": self.playbook.to_dict(),
            "score": self.score,
            "capabilities": [capability.to_dict() for capability in self.capabilities],
        }


class PlaybookLibrary:
    def __init__(self, playbooks: list[Playbook] | None = None) -> None:
        self.playbooks = list(playbooks or [])

    def add(self, playbook: Playbook) -> Playbook:
        self.playbooks.append(playbook)
        return playbook

    def list(self) -> list[Playbook]:
        return sorted(self.playbooks, key=lambda item: item.name)

    def match(self, goal: str, *, registry: PluginRegistry | None = None, limit: int = 3) -> list[PlaybookMatch]:
        registry = registry or default_plugin_registry()
        tokens = _tokens(goal)
        matches: list[PlaybookMatch] = []
        for playbook in self.playbooks:
            haystack = " ".join([playbook.name, playbook.description, " ".join(playbook.triggers)]).lower()
            score = sum(1 for token in tokens if token in haystack)
            if not score:
                continue
            capabilities = [registry.get(step.capability) for step in playbook.steps]
            matches.append(PlaybookMatch(playbook, score, [item for item in capabilities if item is not None]))
        matches.sort(key=lambda item: (item.score, item.playbook.name), reverse=True)
        return matches[: max(0, limit)]

    def to_dict(self) -> dict[str, Any]:
        return {"playbooks": [playbook.to_dict() for playbook in self.list()]}

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "PlaybookLibrary":
        return cls([Playbook.from_dict(item) for item in payload.get("playbooks", []) or []])


def default_playbooks() -> PlaybookLibrary:
    library = PlaybookLibrary()
    library.add(
        Playbook(
            name="meeting-notes-summary",
            description="Turn notes into a short summary and next steps.",
            triggers=["summarize notes", "meeting notes", "action items"],
            steps=[PlaybookStep("Summarize the notes", "summarize-notes", "I will turn the notes into bullets and next steps.")],
        )
    )
    library.add(
        Playbook(
            name="rewrite-message",
            description="Rewrite text in a clearer or warmer style.",
            triggers=["rewrite", "warmer tone", "make concise", "professional"],
            steps=[PlaybookStep("Rewrite the text", "rewrite-text", "I will rewrite the text in the requested style.")],
        )
    )
    library.add(
        Playbook(
            name="follow-up-draft",
            description="Draft a short follow-up from action items.",
            triggers=["follow up", "next steps", "draft message"],
            steps=[PlaybookStep("Draft the follow-up", "draft-follow-up", "I will draft a short follow-up message.")],
        )
    )
    return library


def explain_playbook_match(match: PlaybookMatch) -> str:
    steps = "; ".join(step.plain_language for step in match.playbook.steps)
    return f"I found a playbook: {match.playbook.name}. {steps}"


def _tokens(text: str) -> set[str]:
    return {part.lower() for part in str(text or "").replace("-", " ").split() if part.strip()}
