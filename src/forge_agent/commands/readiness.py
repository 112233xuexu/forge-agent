from __future__ import annotations

import argparse
import json
from pathlib import Path


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


def handle_readiness(args: argparse.Namespace) -> int:
    root = Path.cwd()
    checks = []
    for relative in _REQUIRED_FILES:
        exists = (root / relative).exists()
        checks.append({"name": relative, "ok": exists})
    passed = all(item["ok"] for item in checks)
    payload = {"ready": passed, "checks": checks}
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"Forge Agent readiness: {'ready' if passed else 'needs attention'}")
        for item in checks:
            marker = "ok" if item["ok"] else "missing"
            print(f"- {marker}: {item['name']}")
    return 0 if passed else 1
