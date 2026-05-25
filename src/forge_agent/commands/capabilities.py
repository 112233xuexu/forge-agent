from __future__ import annotations

import argparse
import json

from forge_agent.plugin_registry import default_plugin_registry


def add_capabilities_parser(subparsers):
    command = subparsers.add_parser("capabilities", help="show what Forge can do locally today")
    command.add_argument("--json", action="store_true", help="print JSON instead of human text")


def handle_capabilities(args: argparse.Namespace) -> int:
    registry = default_plugin_registry()
    capabilities = registry.list()
    if args.json:
        print(json.dumps({"capabilities": [item.to_dict() for item in capabilities]}, ensure_ascii=False, indent=2))
        return 0
    print("Forge Agent can currently help with:")
    for capability in capabilities:
        print(f"- {capability.name}: {capability.description}")
        if capability.examples:
            print(f"  Example: {capability.examples[0]}")
    return 0
