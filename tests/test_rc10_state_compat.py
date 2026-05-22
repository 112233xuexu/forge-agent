from forge_agent.models import ExecutionCheckpoint, StepExecution, TaskPlan, normalize_bundle_container_payload
from forge_agent.session_state import StateStore


def test_legacy_checkpoint_payload_is_migrated():
    checkpoint = ExecutionCheckpoint.from_dict(
        {
            "checkpoint_id": "ckpt_1",
            "session_id": "sess_1",
            "task_text": "prepare customer note",
            "plan_objective": "prepare note",
            "steps": [{"name": "draft", "tool": "writer", "args": {"tone": "warm"}}],
            "memory_context": {"preferred_palace_path": "relationships/customers/acme"},
            "next_step_index": 0,
        }
    )

    assert checkpoint.schema_version == 2
    assert checkpoint.status == "open"
    assert checkpoint.plan.objective == "prepare note"
    assert checkpoint.plan.steps[0].tool_name == "writer"
    assert checkpoint.plan.steps[0].requested_tool_name == "writer"
    assert checkpoint.memory_bundle["preferred_palace_path"] == "relationships/customers/acme"
    assert checkpoint.memory_bundle["memory_bundle_meta"]["legacy_source"] is True


def test_state_store_sessions_messages_and_checkpoints_roundtrip(tmp_path):
    store = StateStore(tmp_path / "state.db")
    session = store.get_or_create_session("cli", "default-user")
    same_session = store.get_or_create_session("cli", "default-user")

    assert same_session.session_id == session.session_id

    store.add_message(session.session_id, "user", {"text": "hello"})
    store.add_message(session.session_id, "assistant", "hi")
    messages = store.get_messages(session.session_id)

    assert [message.role for message in messages] == ["user", "assistant"]
    assert '"text": "hello"' in messages[0].content

    checkpoint = ExecutionCheckpoint.new(
        session_id=session.session_id,
        task_text="organize files",
        plan=TaskPlan(objective="organize files", steps=[StepExecution(name="preview", tool_name="organizer", args={})]),
        inputs={"folder": "Downloads"},
        memory_bundle={"context_hint_text": "local files"},
    )
    store.upsert_checkpoint(checkpoint)
    loaded = store.get_checkpoint(checkpoint.checkpoint_id)

    assert loaded is not None
    assert loaded.task_text == "organize files"
    assert loaded.plan.steps[0].tool_name == "organizer"
    assert store.list_checkpoints(status="open")[0].checkpoint_id == checkpoint.checkpoint_id

    checkpoint.status = "completed"
    store.upsert_checkpoint(checkpoint)
    assert store.get_checkpoint(checkpoint.checkpoint_id).status == "completed"
    assert store.list_checkpoints(status="open") == []

    store.delete_checkpoint(checkpoint.checkpoint_id)
    assert store.get_checkpoint(checkpoint.checkpoint_id) is None
    store.close()


def test_bundle_container_promotes_legacy_top_level_fields():
    bundle = normalize_bundle_container_payload(
        {
            "memory_bundle": {"context_hint_text": "from bundle"},
            "preferred_palace_path": "relationships/customers/beta",
            "memory_verdict": {"used_memory": True},
        }
    )

    assert bundle["preferred_palace_path"] == "relationships/customers/beta"
    assert bundle["memory_verdict"]["used_memory"] is True
    assert "preferred_palace_path" in bundle["memory_bundle_meta"]["migrated_fields"]
