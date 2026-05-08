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
    sub = parser.add_subparsers(dest="command")

    do_cmd = sub.add_parser("do", help="submit a goal to the local runtime")
    do_cmd.add_argument("goal", nargs="+", help="goal text")
    do_cmd.add_argument("--workspace", default=".forge-agent", help="runtime workspace")

    sub.add_parser("doctor", help="print repository status and next steps")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "do":
        runtime = ForgeRuntime(Path(args.workspace))
        result = runtime.do(" ".join(args.goal))
        print(json.dumps(result.__dict__, ensure_ascii=False, indent=2))
        return 0

    if args.command == "doctor":
        print("Forge Agent RC10 public repository is initialized.")
        print("Full prepared source archive is stored in source-archive/ parts.")
        print("Use Codex/maintainer work to unpack and normalize the full tree into regular files.")
        return 0

    parser.print_help()
    return 0


def cli_entrypoint() -> int:
    return main()
