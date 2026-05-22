from forge_agent.models import StepExecution, TaskPlan
from forge_agent.tool_registry import ToolRegistry
from forge_agent.workflow import WorkflowBundle, WorkflowNode
from forge_agent.workflow_executor import WorkflowExecutor


def collect_notes(notes: str):
    return {"summary": notes.upper(), "items": [notes]}


def draft_note(summary: str):
    return f"Draft: {summary}"


def explode():
    raise RuntimeError("boom")


def registry():
    tools = ToolRegistry()
    tools.register("collect_notes", collect_notes)
    tools.register("draft_note", draft_note)
    tools.register("explode", explode)
    return tools


def test_workflow_executor_runs_local_tools_with_refs():
    bundle = WorkflowBundle(
        workflow_id="wf_1",
        objective="prepare note",
        inputs={"notes": "hello"},
        nodes=[
            WorkflowNode("node_1", "collect", "collect_notes", {"notes": {"$var": "notes"}}),
            WorkflowNode("node_2", "draft", "draft_note", {"summary": {"$ref": {"step": "collect", "path": ["summary"]}}}, depends_on=["node_1"]),
        ],
    )

    result = WorkflowExecutor(registry()).execute(bundle)

    assert result.status == "completed"
    assert result.outputs["node_1"] == {"summary": "HELLO", "items": ["hello"]}
    assert result.outputs["node_2"] == "Draft: HELLO"
    assert [step.success for step in result.step_results] == [True, True]


def test_workflow_executor_reports_missing_input():
    bundle = WorkflowBundle(
        workflow_id="wf_1",
        objective="prepare note",
        nodes=[WorkflowNode("node_1", "collect", "collect_notes", {"notes": {"$var": "notes"}})],
    )

    result = WorkflowExecutor(registry()).execute(bundle)

    assert result.status == "input_required"
    assert result.missing_inputs == ["notes"]
    assert result.step_results == []


def test_workflow_executor_reports_unknown_tool():
    bundle = WorkflowBundle(
        workflow_id="wf_1",
        objective="prepare note",
        nodes=[WorkflowNode("node_1", "collect", "missing_tool", {})],
    )

    result = WorkflowExecutor(registry()).execute(bundle)

    assert result.status == "failed"
    assert result.step_results[0].success is False
    assert result.step_results[0].error == "unknown tool"


def test_workflow_executor_executes_task_plan_directly():
    plan = TaskPlan(
        objective="prepare note",
        steps=[
            StepExecution("collect", "collect_notes", {"notes": {"$var": "notes"}}),
            StepExecution("draft", "draft_note", {"summary": {"$ref": {"step": "collect", "path": ["summary"]}}}),
        ],
    )

    result = WorkflowExecutor(registry()).execute_plan(plan, inputs={"notes": "hello"})

    assert result.status == "completed"
    assert result.step_results[-1].output == "Draft: HELLO"
