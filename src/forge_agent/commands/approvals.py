from __future__ import annotations

import argparse
import json
from pathlib import Path

from forge_agent.approvals import ApprovalLedger
from forge_agent.cli_common import print_cli_error, print_subcommand_help


def add_approvals_parser(subparsers):
    approvals_cmd = subparsers.add_parser("approvals", help="list or decide approval requests")
    approvals_sub = approvals_cmd.add_subparsers(dest="approvals_command")
    approvals_list = approvals_sub.add_parser("list", help="list approval requests")
    approvals_list.add_argument("--json", action="store_true")
    approvals_decide = approvals_sub.add_parser("decide", help="approve or deny a request")
    approvals_decide.add_argument("approval_id")
    approvals_decide.add_argument("--decision", required=True, choices=["approved", "denied"])
    approvals_decide.add_argument("--json", action="store_true")


def handle_approvals(args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
    ledger = ApprovalLedger(Path(args.workspace))
    command = getattr(args, "approvals_command", None)
    if command == "list":
        approvals = ledger.list()
        if args.json:
            print(json.dumps([item.to_dict() for item in approvals], ensure_ascii=False, indent=2))
            return 0
        if not approvals:
            print("No approval requests yet.")
            return 0
        for item in approvals:
            print(f"{item.status:<9} {item.approval_id} {item.risk}: {item.action}")
        return 0
    if command == "decide":
        try:
            item = ledger.decide(args.approval_id, args.decision)
        except KeyError as exc:
            return print_cli_error(str(exc), error="not_found", json_output=args.json)
        print(json.dumps(item.to_dict(), ensure_ascii=False, indent=2))
        return 0
    print_subcommand_help(parser, "approvals")
    return 0
