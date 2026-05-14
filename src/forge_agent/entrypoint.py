from __future__ import annotations

import json
import sys

from .brain import BrainAdapter
from .cli import cli_entrypoint as legacy_cli_entrypoint


ASK_USAGE = """usage: forge-agent ask [--json] <request>

Turn a plain-language request into a local Forge plan.

Examples:
  forge-agent ask "organize my invoices by month" --json
  forge-agent --workspace .forge-agent ask "make a project status deck" --json
"""


def cli_entrypoint() -> int:
    """Console entrypoint wrapper for v1.9 planning and user-friendly errors.

    Existing commands continue to use the mature CLI module. The new `ask`
    command is handled here to keep the v1.9 change small and low-risk.
    """

    try:
        argv = sys.argv[1:]
        command_argv = _strip_supported_global_options(argv)
        if command_argv and command_argv[0] == "ask":
            return _handle_ask(command_argv[1:])
        return legacy_cli_entrypoint()
    except OSError as exc:
        print(f"Forge Agent file error: {exc}", file=sys.stderr)
        return 2


def _strip_supported_global_options(argv: list[str]) -> list[str]:
    """Return command args after wrapper-supported global options.

    The mature argparse CLI owns full option parsing. This helper only handles
    the global options needed before the wrapper-owned `ask` command.
    """

    remaining = list(argv)
    while remaining:
        if remaining[0] == "--workspace" and len(remaining) >= 2:
            remaining = remaining[2:]
            continue
        if remaining[0].startswith("--workspace="):
            remaining = remaining[1:]
            continue
        break
    return remaining


def _handle_ask(argv: list[str]) -> int:
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
    return 0
