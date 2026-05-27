from __future__ import annotations

import json
from pathlib import Path

from forge_agent.desktop_adapter import DesktopAdapter
from forge_agent.runtime_compat import CompatRuntime
from forge_agent.tool_registry import ToolRegistry


def main() -> int:
    tools = ToolRegistry()
    tools.register("summarize_notes", lambda notes: {"summary": notes})
    runtime = CompatRuntime(Path(".forge-agent-ui-example") / "state.db", tools)
    adapter = DesktopAdapter(runtime)
    try:
        request = {"action": "plan", "text": "Summarize these notes", "inputs": {"notes": "hello"}}
        plan = adapter.handle(request).to_dict()
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        if plan["needs_confirmation"]:
            request["action"] = "execute"
            print(json.dumps(adapter.handle(request).to_dict(), ensure_ascii=False, indent=2))
    finally:
        runtime.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
