from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from . import __version__
from .commands.approvals import add_approvals_parser, handle_approvals
from .commands.core import add_core_parsers, handle_do, handle_doctor, handle_init
from .commands.demo import add_demo_parser, handle_demo
from .commands.history import add_history_parser, handle_history
from .commands.make import add_make_parser, handle_make
from .commands.memory import add_memory_parser, handle_memory
from .commands.organize import add_organize_parsers, handle_organize, handle_rollback
from .commands.schedule import add_schedule_parser, handle_schedule
from .commands.skills import add_skills_parser, handle_skills
from .commands.tasks import add_tasks_parser, handle_tasks
from .runtime import ForgeRuntime


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="forge-agent", description="Forge Agent CLI")
    parser.add_argument("--version", action="version", version=f"forge-agent {__version__}")
    parser.add_argument("--workspace", default=".forge-agent", help="runtime workspace")
    sub = parser.add_subparsers(dest="command")

    add_core_parsers(sub)
    add_organize_parsers(sub)
    add_memory_parser(sub)
    add_history_parser(sub)
    add_schedule_parser(sub)
    add_make_parser(sub)
    add_tasks_parser(sub)
    add_skills_parser(sub)
    add_approvals_parser(sub)
    add_demo_parser(sub)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    runtime = ForgeRuntime(Path(args.workspace))

    if args.command == "init":
        return handle_init(args, runtime)
    if args.command == "do":
        return handle_do(args, runtime)
    if args.command == "doctor":
        return handle_doctor(args, runtime)
    if args.command == "organize":
        return handle_organize(args)
    if args.command == "organize-rollback":
        return handle_rollback(args)
    if args.command == "memory":
        return handle_memory(args, parser)
    if args.command == "history":
        return handle_history(args, parser)
    if args.command == "schedule":
        return handle_schedule(args, parser)
    if args.command == "make":
        return handle_make(args, parser)
    if args.command == "tasks":
        return handle_tasks(args, runtime)
    if args.command == "skills":
        return handle_skills(args, parser)
    if args.command == "approvals":
        return handle_approvals(args, parser)
    if args.command == "demo":
        return handle_demo(args)
    parser.print_help()
    return 0


def cli_entrypoint() -> int:
    return main()
