from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from . import __version__
from .commands.approvals import add_approvals_parser, handle_approvals
from .commands.core import add_core_parsers, handle_do, handle_doctor, handle_init
from .commands.history import add_history_parser, handle_history
from .commands.make import add_make_parser, handle_make
from .commands.memory import add_memory_parser, handle_memory
from .commands.organize import add_organize_parsers, handle_organize, handle_rollback
from .commands.schedule import add_schedule_parser, handle_schedule
from .commands.skills import add_skills_parser, handle_skills
from .commands.tasks import add_tasks_parser, handle_tasks
from .file_organizer_demo import run_file_organizer_demo
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

    demo_cmd = sub.add_parser("demo", help="run an ordinary-user demo")
    demo_cmd.add_argument("--kind", default="file-organizer", choices=["file-organizer"], help="demo kind")
    demo_cmd.add_argument("--json", action="store_true", help="print JSON only")
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
        result = run_file_organizer_demo(Path(args.workspace) / "demo-file-organizer")
        if args.json:
            print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
            return 0
        print("Forge Agent ordinary-user demo: file organizer")
        print(f"Goal: {result.goal}\nWorkspace: {result.workspace}\nApproval: {result.approval_id}\nSkill: {result.skill_name} ({result.skill_id})")
        print(f"Created skill: {result.created_skill}\nReuse proven: {result.reuse_proven}\nManifest: {result.manifest_path}")
        print("Moved files:")
        for item in result.moved_files:
            print(f"- {item['source']} -> {item['destination']}")
        return 0
    parser.print_help()
    return 0


def cli_entrypoint() -> int:
    return main()
