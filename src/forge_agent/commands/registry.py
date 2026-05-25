from __future__ import annotations

import argparse

from forge_agent.commands.approvals import add_approvals_parser, handle_approvals
from forge_agent.commands.capabilities import add_capabilities_parser, handle_capabilities
from forge_agent.commands.core import add_core_parsers, handle_do, handle_doctor, handle_init
from forge_agent.commands.demo import add_demo_parser, handle_demo
from forge_agent.commands.history import add_history_parser, handle_history
from forge_agent.commands.make import add_make_parser, handle_make
from forge_agent.commands.memory import add_memory_parser, handle_memory
from forge_agent.commands.organize import add_organize_parsers, handle_organize, handle_rollback
from forge_agent.commands.readiness import add_readiness_parser, handle_readiness
from forge_agent.commands.schedule import add_schedule_parser, handle_schedule
from forge_agent.commands.skills import add_skills_parser, handle_skills
from forge_agent.commands.smoke import add_smoke_parser, handle_smoke
from forge_agent.commands.tasks import add_tasks_parser, handle_tasks
from forge_agent.runtime import ForgeRuntime


def add_all_command_parsers(subparsers):
    add_core_parsers(subparsers)
    add_capabilities_parser(subparsers)
    add_readiness_parser(subparsers)
    add_smoke_parser(subparsers)
    add_organize_parsers(subparsers)
    add_memory_parser(subparsers)
    add_history_parser(subparsers)
    add_schedule_parser(subparsers)
    add_make_parser(subparsers)
    add_tasks_parser(subparsers)
    add_skills_parser(subparsers)
    add_approvals_parser(subparsers)
    add_demo_parser(subparsers)


def route_command(args: argparse.Namespace, parser: argparse.ArgumentParser, runtime: ForgeRuntime) -> int:
    command = getattr(args, "command", None)
    if command == "init":
        return handle_init(args, runtime)
    if command == "do":
        return handle_do(args, runtime)
    if command == "doctor":
        return handle_doctor(args, runtime)
    if command == "capabilities":
        return handle_capabilities(args)
    if command == "readiness":
        return handle_readiness(args)
    if command == "smoke":
        return handle_smoke(args)
    if command == "organize":
        return handle_organize(args)
    if command == "organize-rollback":
        return handle_rollback(args)
    if command == "memory":
        return handle_memory(args, parser)
    if command == "history":
        return handle_history(args, parser)
    if command == "schedule":
        return handle_schedule(args, parser)
    if command == "make":
        return handle_make(args, parser)
    if command == "tasks":
        return handle_tasks(args, runtime)
    if command == "skills":
        return handle_skills(args, parser)
    if command == "approvals":
        return handle_approvals(args, parser)
    if command == "demo":
        return handle_demo(args)
    parser.print_help()
    return 0