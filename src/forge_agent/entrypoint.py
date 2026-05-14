from __future__ import annotations

import json
import sys

from .brain import BrainAdapter
from .cli import cli_entrypoint as legacy_cli_entrypoint


def cli_entrypoint() -> int:
    """Console entrypoint wrapper for v1.9 planning and user-friendly errors.

    Existing commands continue to use the mature CLI module. The new `ask`
    command is handled here to keep the v1.9 change small and low-risk.
    """

    try:
        argv = sys.argv[1:]
        if argv and argv[0] == "ask":
            return _handle_ask(argv[1:])
        return legacy_cli_entrypoint()
    except OSError as exc:
        print(f"Forge Agent file error: {exc}", file=sys.stderr)
        return 2


def _handle_ask(argv: list[str]) -> int:
    wants_json = False
    cleaned: list[str] = []
    for item in argv:
        if item == "--json":
            wants_json = True
        else:
            cleaned.append(item)
    plan = BrainAdapter().plan(" ".join(cleaned))
    data = plan.to_dict()
    if wants_json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0
    print("Forge Agent brain plan")
    print(f"Goal: {plan.goal}")
    print(f"Intent: {plan.intent}")
    print(f"Next step: {plan.next_step}")
    print(f"Needs approval now: {plan.needs_user_approval}")
    print(f"Confidence: {plan.confidence:.2f}")
    for note in plan.notes:
        print(f"- {note}")
    return 0
