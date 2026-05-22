import json

from forge_agent.desktop_adapter import DesktopAdapter, DesktopRequest
from forge_agent.runtime_compat import CompatRuntime
from forge_agent.tool_registry import ToolRegistry


def make_runtime(tmp_path):
    tools = ToolRegistry()
    tools.register("summarize_notes", lambda notes: {"summary": notes})
    return CompatRuntime(tmp_path / "state.db", tools)


def test_desktop_adapter_health(tmp_path):
    runtime = make_runtime(tmp_path)
    adapter = DesktopAdapter(runtime)

    response = adapter.handle(DesktopRequest.new(action="health"))

    assert response.status == "ok"
    assert response.payload["action"] == "health"
    runtime.close()


def test_desktop_adapter_plans_local_request(tmp_path):
    runtime = make_runtime(tmp_path)
    adapter = DesktopAdapter(runtime)

    response = adapter.handle({"action": "plan", "text": "Summarize these notes", "inputs": {"notes": "hello"}})

    assert response.status == "planned"
    assert response.payload["payload"]["route"]["plan"]["steps"][0]["tool_name"] == "summarize_notes"
    runtime.close()


def test_desktop_adapter_executes_when_requested(tmp_path):
    runtime = make_runtime(tmp_path)
    adapter = DesktopAdapter(runtime)

    response = adapter.handle({"action": "execute", "text": "Summarize these notes", "inputs": {"notes": "hello"}})

    assert response.status == "completed"
    assert response.payload["payload"]["execution"]["status"] == "completed"
    runtime.close()


def test_desktop_adapter_json_roundtrip(tmp_path):
    runtime = make_runtime(tmp_path)
    adapter = DesktopAdapter(runtime)

    content = json.dumps({"action": "ping"})
    response = json.loads(adapter.handle_json(content))

    assert response["status"] == "ok"
    runtime.close()
