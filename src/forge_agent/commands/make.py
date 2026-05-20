from __future__ import annotations

import argparse
import json
from pathlib import Path

from forge_agent.cli_common import print_subcommand_help
from forge_agent.content_packs import ContentPack


def add_make_parser(subparsers):
    make_cmd = subparsers.add_parser("make", help="generate local content artifacts")
    make_sub = make_cmd.add_subparsers(dest="make_command")
    for kind in ["ppt", "report", "news", "storyboard"]:
        item = make_sub.add_parser(kind, help=f"create a {kind} artifact")
        item.add_argument("topic", nargs="+", help="artifact topic")
        item.add_argument("--json", action="store_true")


def handle_make(args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
    pack = ContentPack(Path(args.workspace))
    topic = " ".join(getattr(args, "topic", []) or [])
    if args.make_command == "ppt":
        artifact = pack.make_ppt_outline(topic)
    elif args.make_command == "report":
        artifact = pack.make_report(topic)
    elif args.make_command == "news":
        artifact = pack.make_news_brief(topic)
    elif args.make_command == "storyboard":
        artifact = pack.make_storyboard(topic)
    else:
        print_subcommand_help(parser, "make")
        return 0
    if args.json:
        print(json.dumps(artifact.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(f"Created {artifact.kind}: {artifact.title}\nPath: {artifact.path}")
    return 0
