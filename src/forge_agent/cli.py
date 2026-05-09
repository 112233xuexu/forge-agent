from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from . import __version__
from .runtime import ForgeRuntime


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

    tasks_cmd = sub.add_parser("tasks", help="list local task history")
    tasks_cmd.add_argument("--limit", type=int, default=20, help="maximum tasks to show")
    tasks_cmd.add_argument("--json", action="store_true", help="print JSON instead of table text")

    skills_cmd = sub.add_parser("skills", help="list local reusable skills")
    skills_cmd.add_argument("--json", action="store_true", help="print JSON instead of table text")

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
        skills = runtime.list_skills()
        if args.json:
            print(json.dumps([skill.to_dict() for skill in skills], ensure_ascii=False, indent=2))
            return 0
        if not skills:
            print("No skills yet. Run `forge-agent do \"your goal\"` and Forge Agent will create one if needed.")
            return 0
        for skill in skills:
            print(f"{skill.status:<10} uses={skill.uses:<3} success={skill.success_count:<3} {skill.skill_id}  {skill.name}")
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


def cli_entrypoint() -> int:
    return main()
