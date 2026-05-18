from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

from .brain import BrainAdapter, BrainPlan
from .cli import cli_entrypoint as legacy_cli_entrypoint
from .memory import MemoryStore


ASK_USAGE = """usage: forge-agent ask [--json] [--no-memory] [--memory-limit N] <request>

Turn a plain-language request into a local Forge plan.

Examples:
  forge-agent ask "organize my invoices by month" --json
  forge-agent --workspace .forge-agent ask "make a project status deck" --json
  forge-agent ask --no-memory "organize my invoices" --json
  forge-agent ask --memory-limit 2 "organize my invoices" --json
"""


@dataclass
class EntrypointOptions:
    workspace: str
    command_argv: list[str]


@dataclass
class AskOptions:
    wants_json: bool
    memory_enabled: bool
    memory_limit: int
    goal_parts: list[str]


def cli_entrypoint() -> int:
    """Console entrypoint wrapper for v1.9 planning and user-friendly errors.

    Existing commands continue to use the mature CLI module. The new `ask`
    command is handled here to keep the v1.9 change small and low-risk.
    """

    try:
        argv = sys.argv[1:]
        options = _parse_supported_global_options(argv)
        if options.command_argv and options.command_argv[0] == "ask":
            return _handle_ask(options.command_argv[1:], workspace=options.workspace)
        return legacy_cli_entrypoint()
    except OSError as exc:
        print(f"Forge Agent file error: {exc}", file=sys.stderr)
        return 2


def _parse_supported_global_options(argv: list[str]) -> EntrypointOptions:
    """Return wrapper-supported global options and remaining command args.

    The mature argparse CLI owns full option parsing. This helper only handles
    the global options needed before the wrapper-owned `ask` command.
    """

    workspace = ".forge-agent"
    remaining = list(argv)
    while remaining:
        if remaining[0] == "--workspace" and len(remaining) >= 2:
            workspace = remaining[1]
            remaining = remaining[2:]
            continue
        if remaining[0].startswith("--workspace="):
            workspace = remaining[0].split("=", 1)[1]
            remaining = remaining[1:]
            continue
        break
    return EntrypointOptions(workspace=workspace, command_argv=remaining)


def _strip_supported_global_options(argv: list[str]) -> list[str]:
    """Backward-compatible helper used by older tests."""

    return _parse_supported_global_options(argv).command_argv


def _handle_ask(argv: list[str], *, workspace: str = ".forge-agent") -> int:
    if any(item in {"-h", "--help"} for item in argv):
        print(ASK_USAGE)
        return 0

    options = _parse_ask_options(argv)
    if options.memory_limit < 0:
        return _print_ask_error(
            "invalid_memory_limit",
            "--memory-limit must be zero or greater.",
            wants_json=options.wants_json,
        )

    goal = " ".join(options.goal_parts).strip()
    if not goal:
        return _print_ask_error(
            "missing_request",
            "Provide a request after `forge-agent ask`; please provide a request.",
            wants_json=options.wants_json,
        )

    plan = BrainAdapter().plan(goal)
    _attach_memory_recall(
        plan,
        workspace=workspace,
        enabled=options.memory_enabled,
        limit=options.memory_limit,
    )
    data = plan.to_dict()
    if options.wants_json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0
    print("Forge Agent brain plan")
    print(f"Goal: {plan.goal}")
    print(f"Intent: {plan.intent}")
    print(f"Next step: {plan.next_step}")
    print(f"Needs approval now: {plan.needs_user_approval}")
    print(f"Confidence: {plan.confidence:.2f}")
    for note in plan.notes:
        print(f"- {note}")
    memory_used = plan.metadata.get("memory_used", [])
    if memory_used:
        print("Memory used:")
        for memory in memory_used:
            print(f"- {memory['id']} score={memory['score']} {memory['scope']}/{memory['wing']}")
    return 0


def _parse_ask_options(argv: list[str]) -> AskOptions:
    wants_json = False
    memory_enabled = True
    memory_limit = 5
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
        if item == "--memory-limit":
            if index + 1 >= len(argv):
                memory_limit = -1
                index += 1
                continue
            try:
                memory_limit = int(argv[index + 1])
            except ValueError:
                memory_limit = -1
            index += 2
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
        goal_parts=goal_parts,
    )


def _print_ask_error(error: str, message: str, *, wants_json: bool) -> int:
    payload = {
        "error": error,
        "message": message,
        "usage": "forge-agent ask \"organize my invoices by month\" --json",
    }
    if wants_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2), file=sys.stderr)
    else:
        print(f"Forge Agent ask error: {message}", file=sys.stderr)
        print("Example: forge-agent ask \"organize my invoices by month\" --json", file=sys.stderr)
    return 2


def _attach_memory_recall(plan: BrainPlan, *, workspace: str, enabled: bool = True, limit: int = 5) -> None:
    """Attach bounded memory recall metadata to a plan.

    Memory can inform planning metadata, but it does not execute actions,
    approve actions, or bypass dry-run/rollback behavior.
    """

    normalized_limit = max(0, limit)
    plan.metadata["memory_policy"] = {
        "enabled": enabled,
        "bounded": True,
        "limit": normalized_limit,
        "include_sensitive": False,
        "sensitive_requires_explicit_recall": True,
    }
    if not enabled or normalized_limit == 0:
        plan.metadata["memory_used"] = []
        return
    store = MemoryStore(Path(workspace))
    matches = store.recall(plan.goal, limit=normalized_limit, include_sensitive=False)
    plan.metadata["memory_used"] = [
        {
            "id": match.memory.id,
            "scope": match.memory.scope,
            "wing": match.memory.wing,
            "room": match.memory.room,
            "score": match.score,
            "reasons": match.reasons,
        }
        for match in matches
    ]
