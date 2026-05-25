from __future__ import annotations

import argparse
import json
from pathlib import Path

from forge_agent.user_flow_demo import run_user_flow_demo


_REQUIRED_FILES = [
    "README.md",
    "LICENSE",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "docs/ARCHITECTURE_OVERVIEW.md",
    "docs/OPEN_SOURCE_RELEASE_CHECKLIST.md",
    "docs/CAPABILITIES.md",
]


def add_readiness_parser(subparsers):
    command = subparsers.add_parser("readiness", help="check basic local project readiness")
    command.add_argument("--json", action="store_true", help="print JSON instead of human text")
    command.add_argument("--run-demo", action="store_true", help="also run local demo checks")


def handle_readiness(args: argparse.Namespace) -> int:
    root = Path.cwd()
    checks = []
    for relative in _REQUIRED_FILES:
        checks.append({"name": relative, "ok": (root / relative).exists()})
    demo = None
    if args.run_demo:
        demo_result = run_user_flow_demo(root / ".forge-agent-readiness-demo")
        demo = {"passed": demo_result.passed, "checks": demo_result.checks, "final_files": demo_result.final_files}
        checks.append({"name": "user-flow-demo", "ok": demo_result.passed})
    passed = all(item["ok"] for item in checks)
    payload = {"ready": passed, "checks": checks, "demo": demo}
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"Forge Agent readiness: {'ready' if passed else 'needs attention'}")
        for item in checks:
            marker = "ok" if item["ok"] else "missing"
            print(f"- {marker}: {item['name']}")
        if demo is not None:
            print(f"Demo: {'ok' if demo['passed'] else 'failed'}")
    return 0 if passed else 1
