from __future__ import annotations

import argparse
import json
from pathlib import Path

from forge_agent.cli_common import print_cli_error
from forge_agent.organizer import FileOrganizer


def add_organize_parsers(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    organize_cmd = subparsers.add_parser("organize", help="organize invoice/receipt files by month; dry-run by default")
    organize_cmd.add_argument("source", help="folder to scan")
    organize_cmd.add_argument("--output", help="output folder; defaults to SOURCE/organized")
    organize_cmd.add_argument("--approve", action="store_true", help="actually move files after previewing the plan")
    organize_cmd.add_argument("--json", action="store_true", help="print JSON instead of human text")

    rollback_cmd = subparsers.add_parser("organize-rollback", help="rollback the latest or selected approved organize operation")
    rollback_cmd.add_argument("--operation-id", help="operation id to rollback; defaults to latest organize operation")
    rollback_cmd.add_argument("--json", action="store_true", help="print JSON instead of human text")


def handle_organize(args: argparse.Namespace) -> int:
    organizer = FileOrganizer(Path(args.workspace))
    try:
        result = organizer.organize_by_month(args.source, output_dir=args.output, approve=args.approve)
    except FileNotFoundError as exc:
        return print_cli_error(str(exc), error="file_not_found", json_output=args.json)
    if args.json:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return 0
    print(f"Forge Agent file organizer\nSource: {result.source_dir}\nOutput: {result.output_dir}\nMode: {result.mode}\nApproval: {result.approval_id}\nSkill: {result.skill_name} ({result.skill_id})")
    print(f"Planned moves: {len(result.planned_moves)}")
    if result.operation_id:
        print(f"Operation: {result.operation_id}")
    if result.moved_files:
        print(f"Moved files: {len(result.moved_files)}")
    if result.skipped_files:
        print(f"Skipped files: {len(result.skipped_files)}")
    if result.manifest_path:
        print(f"Manifest: {result.manifest_path}")
    for message in result.messages:
        print(f"- {message}")
    for item in result.planned_moves[:20]:
        print(f"  {item.source} -> {item.destination}")
    return 0


def handle_rollback(args: argparse.Namespace) -> int:
    organizer = FileOrganizer(Path(args.workspace))
    try:
        result = organizer.rollback_operation(args.operation_id) if args.operation_id else organizer.rollback_last()
    except FileNotFoundError as exc:
        return print_cli_error(str(exc), error="file_not_found", json_output=args.json)
    if args.json:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return 0
    print(f"Forge Agent organize rollback\nOperation: {result.operation_id}\nRestored files: {len(result.restored_files)}\nSkipped files: {len(result.skipped_files)}")
    if result.manifest_path:
        print(f"Manifest: {result.manifest_path}")
    for message in result.messages:
        print(f"- {message}")
    for item in result.restored_files[:20]:
        print(f"  {item.source} -> {item.destination}")
    return 0
