from __future__ import annotations

import argparse
import json
from pathlib import Path

from forge_agent.file_organizer_demo import run_file_organizer_demo


def add_demo_parser(subparsers):
    parser = subparsers.add_parser("demo", help="run an ordinary-user demo")
    parser.add_argument("--kind", default="file-organizer", choices=["file-organizer"], help="demo kind")
    parser.add_argument("--json", action="store_true", help="print JSON only")


def handle_demo(args: argparse.Namespace) -> int:
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
