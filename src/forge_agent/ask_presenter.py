from __future__ import annotations

import json
import sys

from .brain import BrainPlan


def print_ask_plan(plan: BrainPlan, *, wants_json: bool) -> None:
    data = plan.to_dict()
    if wants_json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return
    print("Forge Agent brain plan")
    print(f"Goal: {plan.goal}")
    print(f"Intent: {plan.intent}")
    print(f"Next step: {plan.next_step}")
    print(f"Needs approval now: {plan.needs_user_approval}")
    print(f"Confidence: {plan.confidence:.2f}")
    for note in plan.notes:
        print(f"- {note}")
    memory_used = plan.metadata.get("memory_used", [])
    if memory_used:
        print("Memory used:")
        for memory in memory_used:
            print(f"- {memory['id']} score={memory['score']} {memory['scope']}/{memory['wing']}")


def print_ask_error(error: str, message: str, *, wants_json: bool) -> int:
    payload = {
        "error": error,
        "message": message,
        "usage": "forge-agent ask \"organize my invoices by month\" --json",
    }
    if wants_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2), file=sys.stderr)
    else:
        print(f"Forge Agent ask error: {message}", file=sys.stderr)
        print("Example: forge-agent ask \"organize my invoices by month\" --json", file=sys.stderr)
    return 2
