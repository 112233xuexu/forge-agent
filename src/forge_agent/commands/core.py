from __future__ import annotations

import argparse
import json

from forge_agent.default_tools import default_user_tools
from forge_agent.runtime import ForgeRuntime
from forge_agent.user_goal import UserGoalRunner
from forge_agent.user_goal_store import UserGoalStore


def add_core_parsers(subparsers):
    init_cmd = subparsers.add_parser("init", help="create or repair a local Forge workspace")
    init_cmd.add_argument("--profile", default="local", help="workspace profile name")
    init_cmd.add_argument("--force", action="store_true", help="rewrite workspace config")

    do_cmd = subparsers.add_parser("do", help="submit a goal to the local runtime")
    do_cmd.add_argument("goal", nargs="+", help="goal text")
    do_cmd.add_argument("--preview", action="store_true", help="preview a zero-config plan instead of only recording the goal")
    do_cmd.add_argument("--explain", action="store_true", help="explain the plan in ordinary language")
    do_cmd.add_argument("--execute", action="store_true", help="execute the plan through local registered tools when safe")

    doctor_cmd = subparsers.add_parser("doctor", help="print workspace health")
    doctor_cmd.add_argument("--json", action="store_true", help="print JSON instead of human text")


def handle_init(args: argparse.Namespace, runtime: ForgeRuntime) -> int:
    status = runtime.init_workspace(profile=args.profile, force=args.force)
    print(f"Initialized Forge workspace: {status.workspace}")
    for message in status.messages:
        print(f"- {message}")
    return 0


def handle_do(args: argparse.Namespace, runtime: ForgeRuntime) -> int:
    goal = " ".join(args.goal)
    if args.preview or args.explain or args.execute:
        mode = "execute" if args.execute else "explain" if args.explain else "preview"
        runtime.init_workspace()
        store = UserGoalStore(runtime.workspace / "state.db")
        try:
            result = UserGoalRunner(default_user_tools(), store=store).run(goal, mode=mode)
        finally:
            store.close()
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return 0
    result = runtime.do(goal)
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    return 0


def handle_doctor(args: argparse.Namespace, runtime: ForgeRuntime) -> int:
    status = runtime.doctor()
    if args.json:
        print(json.dumps(status.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(f"Workspace: {status.workspace}\nReady: {status.ready}\nTasks: {status.task_count}\nSkills: {status.skill_count}")
        for message in status.messages:
            print(f"- {message}")
    return 0 if status.ready else 1
