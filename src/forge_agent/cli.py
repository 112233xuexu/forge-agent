from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from . import __version__
from .approvals import ApprovalLedger
from .file_organizer_demo import run_file_organizer_demo
from .organizer import FileOrganizer
from .runtime import ForgeRuntime
from .skills import SkillStore


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="forge-agent", description="Forge Agent CLI")
    parser.add_argument("--version", action="version", version=f"forge-agent {__version__}")
    parser.add_argument("--workspace", default=".forge-agent", help="runtime workspace")
    sub = parser.add_subparsers(dest="command")

    init_cmd = sub.add_parser("init", help="create or repair a local Forge workspace")
    init_cmd.add_argument("--profile", default="local", help="workspace profile name")
    init_cmd.add_argument("--force", action="store_true", help="rewrite workspace config")

    do_cmd = sub.add_parser("do", help="submit a goal to the local runtime")
    do_cmd.add_argument("goal", nargs="+", help="goal text")

    organize_cmd = sub.add_parser("organize", help="organize invoice/receipt files by month; dry-run by default")
    organize_cmd.add_argument("source", help="folder to scan")
    organize_cmd.add_argument("--output", help="output folder; defaults to SOURCE/organized")
    organize_cmd.add_argument("--approve", action="store_true", help="actually move files after previewing the plan")
    organize_cmd.add_argument("--json", action="store_true", help="print JSON instead of human text")

    rollback_cmd = sub.add_parser("organize-rollback", help="rollback the latest or selected approved organize operation")
    rollback_cmd.add_argument("--operation-id", help="operation id to rollback; defaults to latest organize operation")
    rollback_cmd.add_argument("--json", action="store_true", help="print JSON instead of human text")

    tasks_cmd = sub.add_parser("tasks", help="list local task history")
    tasks_cmd.add_argument("--limit", type=int, default=20, help="maximum tasks to show")
    tasks_cmd.add_argument("--json", action="store_true", help="print JSON instead of table text")

    skills_cmd = sub.add_parser("skills", help="list or manage local reusable skills")
    skills_cmd.add_argument("--json", action="store_true", help="print JSON instead of table text")
    skills_sub = skills_cmd.add_subparsers(dest="skills_command")
    skills_list = skills_sub.add_parser("list", help="list skills")
    skills_list.add_argument("--json", action="store_true", help="print JSON instead of table text")
    skills_show = skills_sub.add_parser("show", help="show one skill")
    skills_show.add_argument("skill_id", help="full or prefix skill id")
    for action_name, status in [
        ("test", "tested"),
        ("validate", "validated"),
        ("promote", "promoted"),
        ("deprecate", "deprecated"),
        ("quarantine", "quarantined"),
    ]:
        action_parser = skills_sub.add_parser(action_name, help=f"mark a skill as {status}")
        action_parser.add_argument("skill_id", help="full or prefix skill id")
        action_parser.add_argument("--reason", default=f"manual {action_name}", help="reason to record in lifecycle log")

    approvals_cmd = sub.add_parser("approvals", help="list or decide approval requests")
    approvals_sub = approvals_cmd.add_subparsers(dest="approvals_command")
    approvals_list = approvals_sub.add_parser("list", help="list approval requests")
    approvals_list.add_argument("--json", action="store_true", help="print JSON instead of table text")
    approvals_decide = approvals_sub.add_parser("decide", help="approve or deny a request")
    approvals_decide.add_argument("approval_id", help="approval request id")
    approvals_decide.add_argument("--decision", required=True, choices=["approved", "denied"], help="approval decision")

    demo_cmd = sub.add_parser("demo", help="run an ordinary-user demo")
    demo_cmd.add_argument("--kind", default="file-organizer", choices=["file-organizer"], help="demo kind")
    demo_cmd.add_argument("--json", action="store_true", help="print JSON only")

    doctor_cmd = sub.add_parser("doctor", help="print workspace health")
    doctor_cmd.add_argument("--json", action="store_true", help="print JSON instead of human text")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    runtime = ForgeRuntime(Path(args.workspace))

    if args.command == "init":
        status = runtime.init_workspace(profile=args.profile, force=args.force)
        print(f"Initialized Forge workspace: {status.workspace}")
        for message in status.messages:
            print(f"- {message}")
        return 0

    if args.command == "do":
        result = runtime.do(" ".join(args.goal))
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return 0

    if args.command == "organize":
        organizer = FileOrganizer(Path(args.workspace))
        try:
            result = organizer.organize_by_month(args.source, output_dir=args.output, approve=args.approve)
        except FileNotFoundError as exc:
            print(str(exc))
            return 2
        if args.json:
            print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
            return 0
        print("Forge Agent file organizer")
        print(f"Source: {result.source_dir}")
        print(f"Output: {result.output_dir}")
        print(f"Mode: {result.mode}")
        print(f"Approval: {result.approval_id}")
        print(f"Skill: {result.skill_name} ({result.skill_id})")
        print(f"Planned moves: {len(result.planned_moves)}")
        if result.operation_id:
            print(f"Operation: {result.operation_id}")
        if result.moved_files:
            print(f"Moved files: {len(result.moved_files)}")
        if result.manifest_path:
            print(f"Manifest: {result.manifest_path}")
        for message in result.messages:
            print(f"- {message}")
        for item in result.planned_moves[:20]:
            print(f"  {item.source} -> {item.destination}")
        if len(result.planned_moves) > 20:
            print(f"  ... and {len(result.planned_moves) - 20} more")
        return 0

    if args.command == "organize-rollback":
        organizer = FileOrganizer(Path(args.workspace))
        try:
            result = organizer.rollback_operation(args.operation_id) if args.operation_id else organizer.rollback_last()
        except FileNotFoundError as exc:
            print(str(exc))
            return 2
        if args.json:
            print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
            return 0
        print("Forge Agent organize rollback")
        print(f"Operation: {result.operation_id}")
        print(f"Restored files: {len(result.restored_files)}")
        print(f"Skipped files: {len(result.skipped_files)}")
        if result.manifest_path:
            print(f"Manifest: {result.manifest_path}")
        for message in result.messages:
            print(f"- {message}")
        for item in result.restored_files[:20]:
            print(f"  {item.source} -> {item.destination}")
        return 0

    if args.command == "tasks":
        tasks = runtime.list_tasks(limit=args.limit)
        if args.json:
            print(json.dumps([task.to_dict() for task in tasks], ensure_ascii=False, indent=2))
            return 0
        if not tasks:
            print("No tasks yet. Run `forge-agent do \"your goal\"` to create one.")
            return 0
        for task in tasks:
            skill = task.evidence.get("skill", {}) if isinstance(task.evidence, dict) else {}
            skill_name = skill.get("name", "no skill") if isinstance(skill, dict) else "no skill"
            print(f"{task.created_at}  {task.status:<10}  {task.task_id}  {task.goal}  [skill: {skill_name}]")
        return 0

    if args.command == "skills":
        return _handle_skills(args, parser)

    if args.command == "approvals":
        ledger = ApprovalLedger(Path(args.workspace))
        if args.approvals_command == "list":
            approvals = ledger.list()
            if args.json:
                print(json.dumps([item.to_dict() for item in approvals], ensure_ascii=False, indent=2))
                return 0
            if not approvals:
                print("No approval requests yet.")
                return 0
            for item in approvals:
                print(f"{item.status:<9} {item.approval_id} {item.risk}: {item.action}")
            return 0
        if args.approvals_command == "decide":
            item = ledger.decide(args.approval_id, args.decision)
            print(json.dumps(item.to_dict(), ensure_ascii=False, indent=2))
            return 0
        _print_subcommand_help(parser, "approvals")
        return 0

    if args.command == "demo":
        result = run_file_organizer_demo(Path(args.workspace) / "demo-file-organizer")
        if args.json:
            print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
            return 0
        print("Forge Agent ordinary-user demo: file organizer")
        print(f"Goal: {result.goal}")
        print(f"Workspace: {result.workspace}")
        print(f"Approval: {result.approval_id}")
        print(f"Skill: {result.skill_name} ({result.skill_id})")
        print(f"Created skill: {result.created_skill}")
        print(f"Reuse proven: {result.reuse_proven}")
        print(f"Manifest: {result.manifest_path}")
        print("Moved files:")
        for item in result.moved_files:
            print(f"- {item['source']} -> {item['destination']}")
        return 0

    if args.command == "doctor":
        status = runtime.doctor()
        if args.json:
            print(json.dumps(status.to_dict(), ensure_ascii=False, indent=2))
        else:
            print(f"Workspace: {status.workspace}")
            print(f"Ready: {status.ready}")
            print(f"Tasks: {status.task_count}")
            print(f"Skills: {status.skill_count}")
            for message in status.messages:
                print(f"- {message}")
        return 0 if status.ready else 1

    parser.print_help()
    return 0


def _handle_skills(args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
    store = SkillStore(Path(args.workspace))
    store.init()
    command = getattr(args, "skills_command", None)
    if command in {None, "list"}:
        skills = store.list()
        wants_json = getattr(args, "json", False)
        if wants_json:
            print(json.dumps([skill.to_dict() for skill in skills], ensure_ascii=False, indent=2))
            return 0
        if not skills:
            print("No skills yet. Run `forge-agent do \"your goal\"` or `forge-agent organize ./folder` and Forge Agent will create one if needed.")
            return 0
        for skill in skills:
            print(f"{skill.status:<11} uses={skill.uses:<3} success={skill.success_count:<3} failure={skill.failure_count:<3} {skill.skill_id}  {skill.name}")
        return 0
    if command == "show":
        skill = store.get(args.skill_id)
        if skill is None:
            print(f"Skill not found: {args.skill_id}")
            return 2
        print(json.dumps(skill.to_dict(), ensure_ascii=False, indent=2))
        return 0
    status_map = {
        "test": "tested",
        "validate": "validated",
        "promote": "promoted",
        "deprecate": "deprecated",
        "quarantine": "quarantined",
    }
    if command in status_map:
        try:
            skill = store.set_status(args.skill_id, status_map[command], reason=args.reason)
        except KeyError as exc:
            print(str(exc))
            return 2
        print(json.dumps(skill.to_dict(), ensure_ascii=False, indent=2))
        return 0
    _print_subcommand_help(parser, "skills")
    return 0


def _print_subcommand_help(parser: argparse.ArgumentParser, command: str) -> None:
    subparsers_action = next(action for action in parser._subparsers._actions if getattr(action, "dest", None) == "command")
    subparsers_action.choices[command].print_help()


def cli_entrypoint() -> int:
    return main()
