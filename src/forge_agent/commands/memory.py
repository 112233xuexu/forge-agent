from __future__ import annotations

import argparse
import json
from pathlib import Path

from forge_agent.cli_common import print_cli_error, print_json_success, print_subcommand_help
from forge_agent.memory import MemoryStore


def add_memory_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    memory_cmd = subparsers.add_parser("memory", help="manage the local controlled memory palace")
    memory_sub = memory_cmd.add_subparsers(dest="memory_command")
    memory_add = memory_sub.add_parser("add", help="add a visible memory item")
    memory_add.add_argument("content", nargs="+", help="memory content")
    memory_add.add_argument("--scope", default="project", choices=["user", "project", "session", "skill", "operation"])
    memory_add.add_argument("--wing", help="memory wing; defaults to scope")
    memory_add.add_argument("--room", default="general")
    memory_add.add_argument("--closet", default="default")
    memory_add.add_argument("--drawer", default="inbox")
    memory_add.add_argument("--source", default="manual")
    memory_add.add_argument("--safety", default="normal", choices=["normal", "sensitive"])
    memory_add.add_argument("--json", action="store_true")

    memory_list = memory_sub.add_parser("list", help="list active memory items")
    memory_list.add_argument("--all", action="store_true", help="include forgotten and quarantined memories")
    memory_list.add_argument("--json", action="store_true")

    memory_show = memory_sub.add_parser("show", help="show one memory item")
    memory_show.add_argument("memory_id")
    memory_show.add_argument("--json", action="store_true")

    for name in ["forget", "quarantine", "restore"]:
        memory_action = memory_sub.add_parser(name, help=f"mark one memory item as {name}d")
        memory_action.add_argument("memory_id")
        memory_action.add_argument("--json", action="store_true")

    memory_search = memory_sub.add_parser("search", help="search active memories")
    memory_search.add_argument("query", nargs="+")
    memory_search.add_argument("--limit", type=int, default=10)
    memory_search.add_argument("--json", action="store_true")

    memory_recall = memory_sub.add_parser("recall", help="recall bounded, explainable relevant memories")
    memory_recall.add_argument("query", nargs="+")
    memory_recall.add_argument("--limit", type=int, default=5)
    memory_recall.add_argument("--include-sensitive", action="store_true")
    memory_recall.add_argument("--scope", action="append", default=[], help="only recall memories with this scope; repeatable")
    memory_recall.add_argument("--wing", action="append", default=[], help="only recall memories with this wing; repeatable")
    memory_recall.add_argument("--json", action="store_true")

    memory_palace = memory_sub.add_parser("palace", help="show palace map")
    memory_palace.add_argument("--json", action="store_true")

    memory_audit = memory_sub.add_parser("audit", help="show memory audit log")
    memory_audit.add_argument("--limit", type=int, default=50)
    memory_audit.add_argument("--json", action="store_true")

    memory_export = memory_sub.add_parser("export", help="export memory palace bundle")
    memory_export.add_argument("--active-only", action="store_true", help="exclude forgotten and quarantined memories")
    memory_export.add_argument("--audit-limit", type=int, default=1000)
    memory_export.add_argument("--json", action="store_true")

    memory_doctor = memory_sub.add_parser("doctor", help="show memory store health")
    memory_doctor.add_argument("--json", action="store_true")


def handle_memory(args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
    store = MemoryStore(Path(args.workspace))
    command = getattr(args, "memory_command", None)
    wants_json = getattr(args, "json", False)
    try:
        if command == "add":
            item = store.add(
                " ".join(args.content),
                scope=args.scope,
                wing=args.wing,
                room=args.room,
                closet=args.closet,
                drawer=args.drawer,
                source=args.source,
                safety=args.safety,
            )
            if wants_json:
                print_json_success({"memory": item.to_dict()})
            else:
                print(f"Added memory: {item.id} [{item.scope}/{item.wing}/{item.room}]")
            return 0
        if command in {None, "list"}:
            items = store.list(include_inactive=getattr(args, "all", False))
            if wants_json:
                print_json_success({"memories": [item.to_dict() for item in items]})
            else:
                if not items:
                    print("No memory items yet.")
                for item in items:
                    print(f"{item.id} {item.status:<11} {item.scope}/{item.wing}/{item.room}: {item.content}")
            return 0
        if command == "show":
            item = store.show(args.memory_id)
            if wants_json:
                print_json_success({"memory": item.to_dict()})
            else:
                print(json.dumps(item.to_dict(), ensure_ascii=False, indent=2))
            return 0
        if command == "forget":
            item = store.forget(args.memory_id)
            if wants_json:
                print_json_success({"memory": item.to_dict()})
            else:
                print(f"Forgot memory: {item.id}")
            return 0
        if command == "quarantine":
            item = store.quarantine(args.memory_id)
            if wants_json:
                print_json_success({"memory": item.to_dict()})
            else:
                print(f"Quarantined memory: {item.id}")
            return 0
        if command == "restore":
            item = store.restore(args.memory_id)
            if wants_json:
                print_json_success({"memory": item.to_dict()})
            else:
                print(f"Restored memory: {item.id}")
            return 0
        if command == "search":
            items = store.search(" ".join(args.query), limit=args.limit)
            if wants_json:
                print_json_success({"memories": [item.to_dict() for item in items]})
            else:
                if not items:
                    print("No matching memory items.")
                for item in items:
                    print(f"{item.id} {item.scope}/{item.wing}/{item.room}: {item.content}")
            return 0
        if command == "recall":
            matches = store.recall(
                " ".join(args.query),
                limit=args.limit,
                include_sensitive=args.include_sensitive,
                scopes=set(args.scope or []),
                wings=set(args.wing or []),
            )
            if wants_json:
                print_json_success({"matches": [match.to_dict() for match in matches]})
            else:
                if not matches:
                    print("No recalled memory items.")
                for match in matches:
                    print(f"{match.memory.id} score={match.score} reasons={'; '.join(match.reasons)}")
            return 0
        if command == "palace":
            data = store.palace()
            if wants_json:
                print_json_success({"palace": data})
            else:
                print(json.dumps(data, ensure_ascii=False, indent=2))
            return 0
        if command == "audit":
            rows = store.audit(limit=args.limit)
            if wants_json:
                print_json_success({"audit": rows})
            else:
                for row in rows:
                    print(f"{row.get('created_at')} {row.get('action')} {row.get('memory_id')}")
            return 0
        if command == "export":
            bundle = store.export_bundle(include_inactive=not args.active_only, audit_limit=args.audit_limit)
            if wants_json:
                print_json_success({"export": bundle})
            else:
                print(json.dumps(bundle, ensure_ascii=False, indent=2))
            return 0
        if command == "doctor":
            status = store.doctor()
            if wants_json:
                print_json_success({"doctor": status})
            else:
                print(f"Memory root: {status['root']}\nActive: {status['active']}\nForgotten: {status['forgotten']}\nQuarantined: {status['quarantined']}")
            return 0
    except KeyError as exc:
        return print_cli_error(str(exc), error="not_found", json_output=wants_json)
    except ValueError as exc:
        return print_cli_error(str(exc), error="invalid_input", json_output=wants_json)
    print_subcommand_help(parser, "memory")
    return 0
