from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable
import inspect


@dataclass(slots=True)
class RegisteredTool:
    name: str
    handler: Callable[..., Any]
    description: str
    parameters: list[str]
    max_retries: int = 0
    fallback_tools: list[str] = field(default_factory=list)
    validator: Callable[[Any], None] | None = None
    cacheable: bool = True


class ToolRegistry:
    """Small callable tool registry migrated from the RC10 runtime layer."""

    def __init__(self) -> None:
        self._tools: dict[str, RegisteredTool] = {}

    def register(
        self,
        name: str,
        handler: Callable[..., Any],
        description: str = "",
        *,
        max_retries: int = 0,
        fallback_tools: list[str] | None = None,
        validator: Callable[[Any], None] | None = None,
        cacheable: bool = True,
    ) -> None:
        if name in self._tools:
            raise ValueError(f"tool already registered: {name}")
        signature = inspect.signature(handler)
        parameters = [
            param.name
            for param in signature.parameters.values()
            if param.kind in (inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.KEYWORD_ONLY)
        ]
        self._tools[name] = RegisteredTool(
            name=name,
            handler=handler,
            description=description,
            parameters=parameters,
            max_retries=max(0, int(max_retries)),
            fallback_tools=list(fallback_tools or []),
            validator=validator,
            cacheable=bool(cacheable),
        )

    def run(self, tool_name: str, **kwargs: Any) -> Any:
        registered = self.get(tool_name)
        if registered is None:
            raise KeyError(f"unknown tool: {tool_name}")
        if registered.validator is not None:
            registered.validator(kwargs)
        return registered.handler(**kwargs)

    def has(self, tool_name: str) -> bool:
        return tool_name in self._tools

    def get(self, tool_name: str) -> RegisteredTool | None:
        return self._tools.get(tool_name)

    def list_tools(self) -> list[str]:
        return sorted(self._tools)

    def describe_tools(self) -> list[RegisteredTool]:
        return [self._tools[name] for name in sorted(self._tools)]
