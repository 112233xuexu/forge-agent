from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class AppCapability:
    name: str
    description: str = ""
    inputs: list[str] = field(default_factory=list)
    effects: list[str] = field(default_factory=list)
    needs_confirmation: bool = False
    reversible: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "inputs": list(self.inputs),
            "effects": list(self.effects),
            "needs_confirmation": self.needs_confirmation,
            "reversible": self.reversible,
            "metadata": dict(self.metadata),
        }


class AppCapabilityCatalog:
    def __init__(self) -> None:
        self._items: dict[str, AppCapability] = {}

    def add(self, capability: AppCapability) -> None:
        if capability.name in self._items:
            raise ValueError(f"capability already exists: {capability.name}")
        self._items[capability.name] = capability

    def has(self, name: str) -> bool:
        return name in self._items

    def get(self, name: str) -> AppCapability | None:
        return self._items.get(name)

    def names(self) -> list[str]:
        return sorted(self._items)

    def describe(self) -> list[dict[str, Any]]:
        return [self._items[name].to_dict() for name in sorted(self._items)]
