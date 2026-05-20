from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from . import __version__
from .commands.registry import add_all_command_parsers, route_command
from .runtime import ForgeRuntime


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="forge-agent", description="Forge Agent CLI")
    parser.add_argument("--version", action="version", version=f"forge-agent {__version__}")
    parser.add_argument("--workspace", default=".forge-agent", help="runtime workspace")
    subparsers = parser.add_subparsers(dest="command")
    add_all_command_parsers(subparsers)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    runtime = ForgeRuntime(Path(args.workspace))
    return route_command(args, parser, runtime)


def cli_entrypoint() -> int:
    return main()
