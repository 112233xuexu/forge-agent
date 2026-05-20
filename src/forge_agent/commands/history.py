from __future__ import annotations

import argparse
import json
from pathlib import Path

from forge_agent.cli_common import print_cli_error, print_subcommand_help
from forge_agent.history import OperationHistory


def add_history_parser(subparsers):
    history_cmd = subparsers.add_parser("history", help="show local operation history")
    history_sub = history_cmd.add_subparsers(dest="history_command")
    history_list = history_sub.add_parser("list", help="list operations")
    history_list.add_argument("--limit", type=int, default=20)
    history_list.add_argument("--json", action="store_true")
    history_show = history_sub.add_parser("show", help="show one operation manifest")
    history_show.add_argument("operation_id")
    history_show.add_argument("--json", action="store_true")


def handle_history(args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
    store = OperationHistory(Path(args.workspace))
    command = getattr(args, "history_command", None)
    if command in {None, "list"}:
        items = store.list(limit=getattr(args, "limit", 20))
        if getattr(args, "json", False):
            print(json.dumps([item.to_dict() for item in items], ensure_ascii=False, indent=2))
            return 0
        if not items:
            print("No operations yet.")
            return 0
        for item in items:
            print(f"{item.created_at} {item.status:<11} {item.kind:<10} {item.operation_id} {item.summary}")
        return 0
    if command == "show":
        try:
            data = store.show(args.operation_id)
        except FileNotFoundError as exc:
            return print_cli_error(str(exc), error="file_not_found", json_output=args.json)
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0
    print_subcommand_help(parser, "history")
    return 0
