from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .tool_registry import ToolRegistry


@dataclass(slots=True)
class PluginCapability:
    name: str
    tool_name: str
    description: str
    inputs: list[str] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)
    risk_level: str = "low"
    local_only: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "PluginCapability":
        data = dict(payload or {})
        return cls(
            name=str(data["name"]),
            tool_name=str(data["tool_name"]),
            description=str(data.get("description", "") or ""),
            inputs=[str(item) for item in data.get("inputs", []) or []],
            examples=[str(item) for item in data.get("examples", []) or []],
            risk_level=str(data.get("risk_level", "low") or "low"),
            local_only=bool(data.get("local_only", True)),
            metadata=dict(data.get("metadata", {}) or {}),
        )


class PluginRegistry:
    """Small public capability registry for local tools.

    This is not a connector system. It only describes and registers local
    deterministic tools so the user-goal runner and docs can explain what Forge
    can do today.
    """

    def __init__(self) -> None:
        self.capabilities: dict[str, PluginCapability] = {}

    def register(self, capability: PluginCapability) -> PluginCapability:
        self.capabilities[capability.name] = capability
        return capability

    def get(self, name: str) -> PluginCapability | None:
        return self.capabilities.get(name)

    def list(self) -> list[PluginCapability]:
        return [self.capabilities[key] for key in sorted(self.capabilities)]

    def find_for_goal(self, goal: str) -> list[PluginCapability]:
        tokens = _tokens(goal)
        matches: list[tuple[int, PluginCapability]] = []
        for capability in self.capabilities.values():
            haystack = " ".join([capability.name, capability.description, " ".join(capability.examples)]).lower()
            score = sum(1 for token in tokens if token in haystack)
            if score:
                matches.append((score, capability))
        matches.sort(key=lambda item: (item[0], item[1].name), reverse=True)
        return [item[1] for item in matches]

    def to_dict(self) -> dict[str, Any]:
        return {"capabilities": [capability.to_dict() for capability in self.list()]}

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "PluginRegistry":
        registry = cls()
        for item in payload.get("capabilities", []) or []:
            registry.register(PluginCapability.from_dict(item))
        return registry


def default_plugin_registry() -> PluginRegistry:
    registry = PluginRegistry()
    registry.register(
        PluginCapability(
            name="summarize-notes",
            tool_name="summarize_notes",
            description="Summarize local notes into bullets and action items.",
            inputs=["notes"],
            examples=["summarize these notes", "turn meeting notes into bullets"],
        )
    )
    registry.register(
        PluginCapability(
            name="rewrite-text",
            tool_name="paraphrase_text",
            description="Rewrite text in a clearer, warmer, shorter, or more professional style.",
            inputs=["text", "style"],
            examples=["rewrite this in a warmer tone", "make this more concise"],
        )
    )
    registry.register(
        PluginCapability(
            name="translate-text",
            tool_name="translate_text",
            description="Create a local placeholder translation output for text.",
            inputs=["text", "target_language"],
            examples=["translate this into Japanese", "translate this to Spanish"],
        )
    )
    registry.register(
        PluginCapability(
            name="draft-follow-up",
            tool_name="draft_followup",
            description="Draft a short follow-up message from a name and action items.",
            inputs=["customer", "action_items"],
            examples=["draft a follow up", "write follow up next steps"],
        )
    )
    return registry


def register_plugin_tools(registry: PluginRegistry, tools: ToolRegistry) -> list[str]:
    missing: list[str] = []
    for capability in registry.list():
        if not tools.has(capability.tool_name):
            missing.append(capability.tool_name)
    return missing


def _tokens(text: str) -> set[str]:
    return {part.lower() for part in str(text or "").replace("-", " ").split() if part.strip()}
