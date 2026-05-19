from __future__ import annotations

import sys
from dataclasses import dataclass

from .ask_options import ASK_USAGE, parse_ask_options
from .ask_presenter import print_ask_error, print_ask_plan
from .ask_service import build_ask_plan
from .cli import cli_entrypoint as legacy_cli_entrypoint


@dataclass
class EntrypointOptions:
    workspace: str
    command_argv: list[str]


def cli_entrypoint() -> int:
    """Console entrypoint wrapper for ask routing and user-friendly errors."""

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

    options = parse_ask_options(argv)
    if options.memory_limit < 0:
        return print_ask_error(
            "invalid_memory_limit",
            "--memory-limit must be zero or greater.",
            wants_json=options.wants_json,
        )

    goal = " ".join(options.goal_parts).strip()
    if not goal:
        return print_ask_error(
            "missing_request",
            "Provide a request after `forge-agent ask`; please provide a request.",
            wants_json=options.wants_json,
        )

    plan = build_ask_plan(goal, workspace=workspace, options=options)
    print_ask_plan(plan, wants_json=options.wants_json)
    return 0
