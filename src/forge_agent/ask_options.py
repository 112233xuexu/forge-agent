from __future__ import annotations

from dataclasses import dataclass


ASK_USAGE = """usage: forge-agent ask [--json] [--no-memory] [--memory-limit N] [--include-sensitive-memory] [--memory-scope SCOPE] [--memory-wing WING] <request>

Turn a plain-language request into a local Forge plan.

Examples:
  forge-agent ask "organize my invoices by month" --json
  forge-agent --workspace .forge-agent ask "make a project status deck" --json
  forge-agent ask --no-memory "organize my invoices" --json
  forge-agent ask --memory-limit 2 "organize my invoices" --json
  forge-agent ask --include-sensitive-memory "organize my invoices" --json
  forge-agent ask --memory-scope project "organize my invoices" --json
  forge-agent ask --memory-wing skills "organize my invoices" --json
"""


@dataclass
class AskOptions:
    wants_json: bool
    memory_enabled: bool
    memory_limit: int
    include_sensitive_memory: bool
    memory_scopes: set[str]
    memory_wings: set[str]
    goal_parts: list[str]


def parse_ask_options(argv: list[str]) -> AskOptions:
    wants_json = False
    memory_enabled = True
    memory_limit = 5
    include_sensitive_memory = False
    memory_scopes: set[str] = set()
    memory_wings: set[str] = set()
    goal_parts: list[str] = []
    index = 0
    while index < len(argv):
        item = argv[index]
        if item == "--json":
            wants_json = True
            index += 1
            continue
        if item == "--no-memory":
            memory_enabled = False
            index += 1
            continue
        if item == "--include-sensitive-memory":
            include_sensitive_memory = True
            index += 1
            continue
        if item == "--memory-scope":
            value, index = consume_option_value(argv, index)
            if value:
                memory_scopes.add(value)
            continue
        if item.startswith("--memory-scope="):
            value = item.split("=", 1)[1].strip()
            if value:
                memory_scopes.add(value)
            index += 1
            continue
        if item == "--memory-wing":
            value, index = consume_option_value(argv, index)
            if value:
                memory_wings.add(value)
            continue
        if item.startswith("--memory-wing="):
            value = item.split("=", 1)[1].strip()
            if value:
                memory_wings.add(value)
            index += 1
            continue
        if item == "--memory-limit":
            value, index = consume_option_value(argv, index)
            if value is None:
                memory_limit = -1
                continue
            try:
                memory_limit = int(value)
            except ValueError:
                memory_limit = -1
            continue
        if item.startswith("--memory-limit="):
            try:
                memory_limit = int(item.split("=", 1)[1])
            except ValueError:
                memory_limit = -1
            index += 1
            continue
        goal_parts.append(item)
        index += 1
    return AskOptions(
        wants_json=wants_json,
        memory_enabled=memory_enabled,
        memory_limit=memory_limit,
        include_sensitive_memory=include_sensitive_memory,
        memory_scopes=memory_scopes,
        memory_wings=memory_wings,
        goal_parts=goal_parts,
    )


def consume_option_value(argv: list[str], index: int) -> tuple[str | None, int]:
    if index + 1 >= len(argv):
        return None, index + 1
    value = argv[index + 1].strip()
    if value.startswith("--"):
        return None, index + 1
    return value, index + 2
