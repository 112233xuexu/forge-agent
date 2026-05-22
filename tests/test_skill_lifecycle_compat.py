from forge_agent.models import StepExecution
from forge_agent.skill_lifecycle import SkillLifecycleEngine, SkillLibrary, TaskTrace
from forge_agent.tool_registry import ToolRegistry
from forge_agent.workflow_executor import WorkflowExecutor


def trace(trace_id: str, customer: str, notes: str) -> TaskTrace:
    return TaskTrace(
        trace_id=trace_id,
        session_id="sess_1",
        task_text=f"Summarize notes and draft follow-up for {customer}",
        goal_key="summarize_notes_draft_followup",
        plan_objective="summarize notes and draft follow-up",
        plan_intent="followup_notes",
        succeeded=True,
        steps=[
            StepExecution(
                name="extract actions",
                tool_name="summarize_notes",
                args={"notes": notes},
                result={"action_items": [f"send deck to {customer}"], "summary": notes},
            ),
            StepExecution(
                name="draft reply",
                tool_name="draft_followup",
                args={"customer": customer, "action_items": [f"send deck to {customer}"]},
                result=f"Reply to {customer}",
            ),
        ],
    )


def tools() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register("summarize_notes", lambda notes: {"action_items": [f"send deck to {notes}"], "summary": notes})
    registry.register("draft_followup", lambda customer, action_items: f"Reply to {customer}: {', '.join(action_items)}")
    return registry


def test_lifecycle_promotes_repeated_successful_workflow():
    t1 = trace("t1", "Acme", "acme")
    t2 = trace("t2", "Beta", "beta")

    decision = SkillLifecycleEngine(repeat_threshold=2).consider(t2, [t1, t2])

    assert decision.accepted is True
    assert decision.reason == "promote_repeated_workflow"
    assert decision.skill is not None
    assert decision.skill.input_variables == ["notes", "customer"]
    assert decision.skill.steps[0].args["notes"] == {"$var": "notes"}
    assert decision.skill.steps[1].args["customer"] == {"$var": "customer"}
    assert decision.skill.steps[1].args["action_items"] == {"$ref": {"step": "extract actions", "path": ["action_items"]}}


def test_skill_plan_can_execute_as_workflow():
    t1 = trace("t1", "Acme", "acme")
    t2 = trace("t2", "Beta", "beta")
    skill = SkillLifecycleEngine(repeat_threshold=2).consider(t2, [t1, t2]).skill
    assert skill is not None

    result = WorkflowExecutor(tools()).execute(skill.to_workflow(inputs={"notes": "gamma", "customer": "Gamma"}))

    assert result.status == "completed"
    assert "Reply to Gamma" in result.outputs["node_2"]


def test_skill_library_matches_records_and_roundtrips_jsonl():
    t1 = trace("t1", "Acme", "acme")
    t2 = trace("t2", "Beta", "beta")
    skill = SkillLifecycleEngine(repeat_threshold=2).consider(t2, [t1, t2]).skill
    assert skill is not None

    library = SkillLibrary()
    library.add(skill)
    matched = library.find_best(task_text="Please summarize notes and draft a follow-up", tool_names=["summarize_notes", "draft_followup"])

    assert matched is not None
    assert matched.skill_id == skill.skill_id
    updated = library.record_outcome(skill.skill_id, success=True)
    assert updated is not None
    assert updated.success_count == skill.success_count

    restored = SkillLibrary.from_jsonl(library.to_jsonl())
    assert restored.get(skill.skill_id).steps[0].tool_name == "summarize_notes"


def test_lifecycle_upgrades_existing_skill():
    t1 = trace("t1", "Acme", "acme")
    t2 = trace("t2", "Beta", "beta")
    engine = SkillLifecycleEngine(repeat_threshold=2)
    existing = engine.consider(t2, [t1, t2]).skill
    assert existing is not None

    decision = engine.consider(trace("t3", "Gamma", "gamma"), [t1, t2], existing_skill=existing)

    assert decision.accepted is True
    assert decision.reason == "upgrade_existing_skill"
    assert decision.skill is not None
    assert decision.skill.version == existing.version + 1
