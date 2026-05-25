from __future__ import annotations

import argparse
import json
from pathlib import Path

from forge_agent.file_organizer_demo import run_file_organizer_demo
from forge_agent.user_flow_demo import run_user_flow_demo


def add_demo_parser(subparsers):
    parser = subparsers.add_parser("demo", help="run an ordinary-user demo")
    parser.add_argument("--kind", default="file-organizer", choices=["file-organizer", "user-flow"], help="demo kind")
    parser.add_argument("--json", action="store_true", help="print JSON only")


def handle_demo(args: argparse.Namespace) -> int:
    if args.kind == "user-flow":
        result = run_user_flow_demo(Path(args.workspace) / "demo-user-flow")
        if args.json:
            print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
            return 0 if result.passed else 1
        print("Forge Agent ordinary-user demo: user flow")
        print(f"Passed: {result.passed}")
        print(f"Workspace: {result.workspace}")
        print(f"Source: {result.source_dir}")
        print(f"Preview: {result.preview.get('status')}")
        print(f"Execute: {result.execute.get('status')}")
        print(f"Restore: {result.restore.get('status')}")
        print("Checks:")
        for name, ok in result.checks.items():
            print(f"- {'ok' if ok else 'failed'}: {name}")
        print("Final files:")
        for item in result.final_files:
            print(f"- {item}")
        for item in result.audit:
            print(f"- {item}")
        return 0 if result.passed else 1

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
    for moved in result.moved_files:
        print("- " + str(moved.get("source")) + " -> " + str(moved.get("destination")))
    return 0