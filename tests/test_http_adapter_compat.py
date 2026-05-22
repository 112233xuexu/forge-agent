import json

from forge_agent.desktop_adapter import DesktopAdapter
from forge_agent.http_adapter import HttpAdapter, HttpRequestEnvelope
from forge_agent.runtime_compat import CompatRuntime
from forge_agent.tool_registry import ToolRegistry


def make_adapter(tmp_path):
    tools = ToolRegistry()
    tools.register("summarize_notes", lambda notes: {"summary": notes})
    runtime = CompatRuntime(tmp_path / "state.db", tools)
    return HttpAdapter(DesktopAdapter(runtime)), runtime


def test_http_adapter_health(tmp_path):
    adapter, runtime = make_adapter(tmp_path)
    response = adapter.handle(HttpRequestEnvelope(method="GET", path="/health"))
    assert response.status_code == 200
    assert response.body["status"] == "ok"
    runtime.close()


def test_http_adapter_run_payload(tmp_path):
    adapter, runtime = make_adapter(tmp_path)
    envelope = HttpRequestEnvelope.from_json(
        method="POST",
        path="/run",
        body=json.dumps({"text": "Summarize these notes", "inputs": {"notes": "hello"}}),
    )
    response = adapter.handle(envelope)
    assert response.status_code == 200
    assert response.body["status"] == "planned"
    runtime.close()
