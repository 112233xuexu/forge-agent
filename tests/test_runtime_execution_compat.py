from forge_agent.runtime_compat import CompatRuntime
from forge_agent.tool_registry import ToolRegistry


def summarize_notes(notes: str):
    return {"summary": notes.upper(), "action_items": [notes]}


def translate_text(text: str, target_language: str):
    return f"[{target_language}] {text}"


def make_tools():
    tools = ToolRegistry()
    tools.register("summarize_notes", summarize_notes)
    tools.register("translate_text", translate_text)
    return tools


def test_compat_runtime_execute_false_only_plans(tmp_path):
    runtime = CompatRuntime(tmp_path / "state.db", make_tools())

    result = runtime.run_local("Summarize these notes", inputs={"notes": "hello"}, execute=False)

    assert result.status == "planned"
    assert "execution" not in result.payload
    runtime.close()


def test_compat_runtime_execute_true_runs_local_registered_tools(tmp_path):
    runtime = CompatRuntime(tmp_path / "state.db", make_tools())

    result = runtime.run_local("Summarize these notes", inputs={"notes": "hello"}, execute=True)

    assert result.status == "completed"
    assert result.text == "I completed the planned work."
    assert result.payload["execution"]["outputs"]["node_1"] == {"summary": "HELLO", "action_items": ["hello"]}
    runtime.close()


def test_compat_runtime_execute_true_keeps_input_required_status(tmp_path):
    runtime = CompatRuntime(tmp_path / "state.db", make_tools())

    result = runtime.run_local("Translate this into spanish", execute=True)

    assert result.status == "input_required"
    assert "execution" not in result.payload
    runtime.close()
