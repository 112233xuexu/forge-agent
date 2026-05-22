from forge_agent.gateway import GatewayRouter, LocalChannel, WebhookChannel
from forge_agent.runtime_compat import CompatRuntime
from forge_agent.session_state import StateStore
from forge_agent.tool_registry import ToolRegistry


def summarize_notes(notes: str):
    return {"summary": notes, "action_items": [item.strip() for item in notes.split(";") if item.strip()]}


def translate_text(text: str, target_language: str):
    return f"[{target_language}] {text}"


def make_tools():
    tools = ToolRegistry()
    tools.register("summarize_notes", summarize_notes)
    tools.register("translate_text", translate_text)
    return tools


def test_gateway_reuses_existing_session_and_records_messages(tmp_path):
    store = StateStore(tmp_path / "state.db")
    router = GatewayRouter(store)
    channel = LocalChannel()

    inbound = channel.build_inbound(user_id="u1", text="hello")
    envelope, reply = router.route(inbound)
    second = channel.build_inbound(user_id="u1", text="again")
    second_envelope, _second_reply = router.route(second)

    assert envelope.binding.reused_existing is False
    assert second_envelope.binding.reused_existing is True
    assert second_envelope.binding.session_id == reply.session_id
    assert [message.role for message in store.get_messages(reply.session_id)] == ["user", "assistant", "user", "assistant"]
    store.close()


def test_webhook_channel_normalizes_nested_payload():
    channel = WebhookChannel()
    inbound = channel.build_inbound_from_payload(
        {"message": {"text": "Summarize notes", "session_id": "sess_external"}, "user": {"id": "u2"}, "source": "unit"}
    )

    assert inbound.text == "Summarize notes"
    assert inbound.user_id == "u2"
    assert inbound.session_id == "sess_external"
    assert inbound.metadata["source"] == "webhook"


def test_compat_runtime_plans_when_inputs_are_available(tmp_path):
    runtime = CompatRuntime(tmp_path / "state.db", make_tools())
    result = runtime.run_local("Summarize these notes", inputs={"notes": "send deck; confirm date"})

    assert result.status == "planned"
    assert result.payload["route"]["plan"]["steps"][0]["tool_name"] == "summarize_notes"
    assert runtime.state.get_messages(result.session_id)
    runtime.close()


def test_compat_runtime_reports_missing_inputs(tmp_path):
    runtime = CompatRuntime(tmp_path / "state.db", make_tools())
    result = runtime.run_webhook({"text": "Translate this into spanish", "user_id": "u3"})

    assert result.status == "input_required"
    assert result.payload["route"]["missing_inputs"] == ["text"]
    assert "I need this first" in result.text
    runtime.close()
