from __future__ import annotations

import argparse
import json

from forge_agent.runtime import ForgeRuntime


def add_tasks_parser(subparsers):
    tasks_cmd = subparsers.add_parser("tasks", help="list local task history")
    tasks_cmd.add_argument("--limit", type=int, default=20, help="maximum tasks to show")
    tasks_cmd.add_argument("--json", action="store_true", help="print JSON instead of table text")


def handle_tasks(args: argparse.Namespace, runtime: ForgeRuntime) -> int:
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
