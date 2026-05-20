from __future__ import annotations

import argparse
import json
from pathlib import Path

from forge_agent.cli_common import print_cli_error, print_subcommand_help
from forge_agent.scheduler import ScheduleStore


def add_schedule_parser(subparsers):
    schedule_cmd = subparsers.add_parser("schedule", help="create or manage scheduled automation records")
    schedule_sub = schedule_cmd.add_subparsers(dest="schedule_command")
    schedule_add = schedule_sub.add_parser("add", help="record a scheduled command")
    schedule_add.add_argument("schedule", help="natural-language schedule, e.g. every day 9am")
    schedule_add.add_argument("command", nargs="+", help="command to run later")
    schedule_add.add_argument("--json", action="store_true")
    schedule_list = schedule_sub.add_parser("list", help="list scheduled commands")
    schedule_list.add_argument("--json", action="store_true")
    for action_name, status in [("pause", "paused"), ("resume", "active")]:
        action = schedule_sub.add_parser(action_name, help=f"mark schedule as {status}")
        action.add_argument("task_id")
        action.add_argument("--json", action="store_true")


def handle_schedule(args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
    store = ScheduleStore(Path(args.workspace))
    store.init()
    command = getattr(args, "schedule_command", None)
    if command == "add":
        task = store.add(" ".join(args.command), args.schedule)
        if args.json:
            print(json.dumps(task.to_dict(), ensure_ascii=False, indent=2))
        else:
            print(f"Scheduled: {task.task_id} [{task.status}] {task.schedule} -> {task.command}")
        return 0
    if command in {None, "list"}:
        tasks = store.list()
        if getattr(args, "json", False):
            print(json.dumps([task.to_dict() for task in tasks], ensure_ascii=False, indent=2))
            return 0
        if not tasks:
            print("No schedules yet.")
            return 0
        for task in tasks:
            print(f"{task.status:<7} {task.task_id} {task.schedule} -> {task.command}")
        return 0
    if command in {"pause", "resume"}:
        try:
            task = store.set_status(args.task_id, "paused" if command == "pause" else "active")
        except KeyError as exc:
            return print_cli_error(str(exc), error="not_found", json_output=args.json)
        if args.json:
            print(json.dumps(task.to_dict(), ensure_ascii=False, indent=2))
        else:
            print(f"{task.status}: {task.task_id} {task.schedule} -> {task.command}")
        return 0
    print_subcommand_help(parser, "schedule")
    return 0
