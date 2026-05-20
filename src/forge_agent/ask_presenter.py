from __future__ import annotations

import json
import sys

from .brain import BrainPlan
from .task_card import TaskCard, TaskCardButton, TaskCardImpact


def print_ask_plan(plan: BrainPlan, *, wants_json: bool) -> None:
    data = plan.to_dict()
    if wants_json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return
    card_data = plan.metadata.get("task_card")
    if isinstance(card_data, dict):
        print(_task_card_from_dict(card_data).human_summary())
        memory_used = plan.metadata.get("memory_used", [])
        if memory_used:
            print("")
            print("What I remembered for this task:")
            for memory in memory_used:
                print(f"- {memory['scope']}/{memory['wing']} ({memory['id']})")
        return
    print("Forge Agent task preview")
    print(f"You asked: {plan.goal}")
    print(f"I will do: {plan.next_step}")
    for note in plan.notes:
        print(f"- {note}")


def _task_card_from_dict(data: dict[str, object]) -> TaskCard:
    impacts = [
        TaskCardImpact(
            summary=str(item.get("summary", "")),
            level=str(item.get("level", "low")),
            reversible=bool(item.get("reversible", False)),
        )
        for item in data.get("impacts", [])
        if isinstance(item, dict)
    ]
    buttons = [
        TaskCardButton(
            label=str(item.get("label", "")),
            kind=str(item.get("kind", "")),
            enabled=bool(item.get("enabled", True)),
        )
        for item in data.get("buttons", [])
        if isinstance(item, dict)
    ]
    return TaskCard(
        title=str(data.get("title", "Task preview")),
        user_request=str(data.get("user_request", "")),
        status=str(data.get("status", "preview")),
        plan=[str(item) for item in data.get("plan", [])],
        impacts=impacts,
        boundaries=[str(item) for item in data.get("boundaries", [])],
        buttons=buttons,
        result_summary=data.get("result_summary") if isinstance(data.get("result_summary"), str) else None,
        record_id=data.get("record_id") if isinstance(data.get("record_id"), str) else None,
        restore_available=bool(data.get("restore_available", False)),
        memory_used=[str(item) for item in data.get("memory_used", [])],
    )


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
