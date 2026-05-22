from forge_agent.governance import GovernancePolicy
from forge_agent.runtime_compat import CompatRuntime
from forge_agent.tool_registry import ToolRegistry


def summarize_notes(notes: str):
    return {"summary": notes}


def make_tools():
    tools = ToolRegistry()
    tools.register("summarize_notes", summarize_notes)
    return tools


def test_runtime_policy_allows_low_risk_route(tmp_path):
    runtime = CompatRuntime(tmp_path / "state.db", make_tools())

    result = runtime.run_local("Summarize these notes", inputs={"notes": "hello"}, govern=True, execute=True)

    assert result.status == "completed"
    assert result.payload["governance"]["decision"] == "allow"
    assert result.payload["execution"]["status"] == "completed"
    runtime.close()


def test_runtime_policy_confirmation_pauses_local_route(tmp_path):
    runtime = CompatRuntime(
        tmp_path / "state.db",
        make_tools(),
        policy=GovernancePolicy(allow_autorun_low_risk=False),
    )

    result = runtime.run_local("Summarize these notes", inputs={"notes": "hello"}, govern=True, execute=True)

    assert result.status == "confirmation_required"
    assert result.payload["governance"]["decision"] == "confirm"
    assert "execution" not in result.payload
    runtime.close()
