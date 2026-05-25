from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from forge_agent.plugin_registry import default_plugin_registry
from forge_agent.user_flow_demo import run_user_flow_demo


def add_smoke_parser(subparsers):
    command = subparsers.add_parser("smoke", help="run a short local product smoke check")
    command.add_argument("--json", action="store_true", help="print JSON instead of human text")


def handle_smoke(args: argparse.Namespace) -> int:
    root = Path(args.workspace)
    capabilities = default_plugin_registry().list()
    demo = run_user_flow_demo(root / "smoke-user-flow")
    checks: dict[str, bool] = {
        "capabilities_available": len(capabilities) >= 8,
        "user_flow_demo_passed": demo.passed,
    }
    payload: dict[str, Any] = {
        "passed": all(checks.values()),
        "checks": checks,
        "capability_count": len(capabilities),
        "demo": demo.to_dict(),
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print("Forge Agent smoke check")
        print(f"Passed: {payload['passed']}")
        print(f"Capabilities: {len(capabilities)}")
        for name, ok in checks.items():
            print(f"- {'ok' if ok else 'failed'}: {name}")
    return 0 if payload["passed"] else 1
