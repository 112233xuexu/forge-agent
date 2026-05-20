from __future__ import annotations

import argparse
import json
from pathlib import Path

from forge_agent.cli_common import print_cli_error, print_subcommand_help
from forge_agent.skills import SkillStore


def add_skills_parser(subparsers):
    skills_cmd = subparsers.add_parser("skills", help="list or manage local reusable skills")
    skills_cmd.add_argument("--json", action="store_true", help="print JSON instead of table text")
    skills_sub = skills_cmd.add_subparsers(dest="skills_command")
    skills_list = skills_sub.add_parser("list", help="list skills")
    skills_list.add_argument("--json", action="store_true", help="print JSON instead of table text")
    skills_show = skills_sub.add_parser("show", help="show one skill")
    skills_show.add_argument("skill_id", help="full or prefix skill id")
    for action_name, status in [("test", "tested"), ("validate", "validated"), ("promote", "promoted"), ("deprecate", "deprecated"), ("quarantine", "quarantined")]:
        action_parser = skills_sub.add_parser(action_name, help=f"mark a skill as {status}")
        action_parser.add_argument("skill_id", help="full or prefix skill id")
        action_parser.add_argument("--reason", default=f"manual {action_name}", help="reason to record in lifecycle log")


def handle_skills(args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
    store = SkillStore(Path(args.workspace))
    store.init()
    command = getattr(args, "skills_command", None)
    wants_json = getattr(args, "json", False)
    if command in {None, "list"}:
        skills = store.list()
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
            return print_cli_error(f"Skill not found: {args.skill_id}", error="not_found", json_output=wants_json)
        print(json.dumps(skill.to_dict(), ensure_ascii=False, indent=2))
        return 0
    status_map = {"test": "tested", "validate": "validated", "promote": "promoted", "deprecate": "deprecated", "quarantine": "quarantined"}
    if command in status_map:
        try:
            skill = store.set_status(args.skill_id, status_map[command], reason=args.reason)
        except KeyError as exc:
            return print_cli_error(str(exc), error="not_found", json_output=wants_json)
        print(json.dumps(skill.to_dict(), ensure_ascii=False, indent=2))
        return 0
    print_subcommand_help(parser, "skills")
    return 0
