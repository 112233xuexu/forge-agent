from __future__ import annotations

import argparse
import json


def print_cli_error(message: str, *, error: str, json_output: bool) -> int:
    if json_output:
        print(json.dumps({"ok": False, "error": error, "message": message}, ensure_ascii=False, indent=2))
    else:
        print(message)
    return 2


def print_json_success(payload: dict[str, object]) -> None:
    print(json.dumps({"ok": True, **payload}, ensure_ascii=False, indent=2))


def print_subcommand_help(parser: argparse.ArgumentParser, command: str) -> None:
    subparsers_action = next(action for action in parser._subparsers._actions if getattr(action, "dest", None) == "command")
    subparsers_action.choices[command].print_help()
