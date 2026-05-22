from forge_agent.models import StepExecution
from forge_agent.skill_lifecycle import SkillDefinition, SkillLibrary
from forge_agent.tool_registry import ToolRegistry
from forge_agent.user_goal import UserGoalRunner
from forge_agent.user_goal_store import UserGoalStore


def make_tools():
    tools = ToolRegistry()
    tools.register("summarize_notes", lambda notes: {"summary": notes, "action_items": [notes]})
    tools.register("paraphrase_text", lambda text, style="clear": f"[{style}] {text}")
    return tools


def test_user_goal_preview_uses_planner_when_no_skill():
    runner = UserGoalRunner(make_tools())

    result = runner.run("Summarize these notes", inputs={"notes": "ship update"}, mode="preview")

    assert result.status == "planned"
    assert result.plan is not None
    assert result.plan.steps[0].tool_name == "summarize_notes"
    assert result.skill is None
    assert "I made a plan" in result.text


def test_user_goal_execute_runs_local_tools():
    runner = UserGoalRunner(make_tools())

    result = runner.run("Summarize these notes", inputs={"notes": "ship update"}, mode="execute")

    assert result.status == "completed"
    assert result.execution is not None
    assert result.execution.outputs["node_1"] == {"summary": "ship update", "action_items": ["ship update"]}


def test_user_goal_reports_missing_inputs():
    runner = UserGoalRunner(make_tools())

    result = runner.run("Summarize these notes")

    assert result.status == "input_required"
    assert result.missing_inputs == ["notes"]
    assert "notes" in result.text


def test_user_goal_prefers_matching_skill_and_records_success():
    library = SkillLibrary()
    skill = SkillDefinition.new(
        goal_key="summarize_notes",
        trigger_text="summarize notes",
        description="Summarize notes for the user",
        steps=[StepExecution("summarize notes", "summarize_notes", {"notes": {"$var": "notes"}})],
        input_variables=["notes"],
    )
    library.add(skill)
    runner = UserGoalRunner(make_tools(), skills=library)

    result = runner.run("please summarize notes", inputs={"notes": "hello"}, mode="execute")

    assert result.status == "completed"
    assert result.skill is not None
    assert result.skill.skill_id == skill.skill_id
    assert library.get(skill.skill_id).success_count == 1


def test_user_goal_explain_does_not_execute():
    runner = UserGoalRunner(make_tools())

    result = runner.run('Rewrite "Need approval" in a warmer tone', mode="explain")

    assert result.status == "explained"
    assert result.execution is None
    assert "I made a plan" in result.text


def test_user_goal_store_records_traces_and_promotes_skill(tmp_path):
    store = UserGoalStore(tmp_path / "state.db")
    try:
        runner = UserGoalRunner(make_tools(), store=store)

        first = runner.run("Summarize these notes", inputs={"notes": "one"}, mode="execute")
        second = runner.run("Summarize these notes", inputs={"notes": "two"}, mode="execute")

        assert first.status == "completed"
        assert second.status == "completed"
        assert second.promoted_skill is not None
        assert store.to_status() == {"skill_count": 1, "trace_count": 2}
    finally:
        store.close()


def test_user_goal_store_loads_promoted_skill_for_next_runner(tmp_path):
    store = UserGoalStore(tmp_path / "state.db")
    try:
        runner = UserGoalRunner(make_tools(), store=store)
        runner.run("Summarize these notes", inputs={"notes": "one"}, mode="execute")
        runner.run("Summarize these notes", inputs={"notes": "two"}, mode="execute")
    finally:
        store.close()

    store = UserGoalStore(tmp_path / "state.db")
    try:
        runner = UserGoalRunner(make_tools(), store=store)
        result = runner.run("please summarize notes", inputs={"notes": "three"}, mode="execute")

        assert result.status == "completed"
        assert result.skill is not None
        assert result.skill.tool_names == ["summarize_notes"]
    finally:
        store.close()
