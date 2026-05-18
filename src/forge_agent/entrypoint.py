from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

from .brain import BrainAdapter, BrainPlan
from .cli import cli_entrypoint as legacy_cli_entrypoint
from .memory import MemoryStore


ASK_USAGE = """usage: forge-agent ask [--json] <request>

Turn a plain-language request into a local Forge plan.

Examples:
  forge-agent ask "organize my invoices by month" --json
  forge-agent --workspace .forge-agent ask "make a project status deck" --json
"""


@dataclass
class EntrypointOptions:
    workspace: str
    command_argv: list[str]


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

    wants_json = False
    cleaned: list[str] = []
    for item in argv:
        if item == "--json":
            wants_json = True
        else:
            cleaned.append(item)

    goal = " ".join(cleaned).strip()
    if not goal:
        error = {
            "error": "missing_request",
            "message": "Provide a request after `forge-agent ask`.",
            "usage": "forge-agent ask \"organize my invoices by month\" --json",
        }
        if wants_json:
            print(json.dumps(error, ensure_ascii=False, indent=2), file=sys.stderr)
        else:
            print("Forge Agent ask error: provide a request after `forge-agent ask`.", file=sys.stderr)
            print("Example: forge-agent ask \"organize my invoices by month\" --json", file=sys.stderr)
        return 2

    plan = BrainAdapter().plan(goal)
    _attach_memory_recall(plan, workspace=workspace)
    data = plan.to_dict()
    if wants_json:
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


def _attach_memory_recall(plan: BrainPlan, *, workspace: str) -> None:
    """Attach bounded memory recall metadata to a plan.

    Memory can inform planning metadata, but it does not execute actions,
    approve actions, or bypass dry-run/rollback behavior.
    """

    store = MemoryStore(Path(workspace))
    matches = store.recall(plan.goal, limit=5, include_sensitive=False)
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
    plan.metadata["memory_policy"] = {
        "bounded": True,
        "limit": 5,
        "include_sensitive": False,
        "sensitive_requires_explicit_recall": True,
    }
