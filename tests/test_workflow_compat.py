from forge_agent.models import StepExecution, TaskPlan
from forge_agent.workflow import WorkflowBundle, WorkflowNode, inspect_workflow_readiness, order_workflow_nodes, resolve_step_arguments


def test_workflow_bundle_roundtrips_task_plan():
    plan = TaskPlan(
        objective="prepare note",
        steps=[
            StepExecution("collect", "collect_notes", {"notes": {"$var": "notes"}}),
            StepExecution("draft", "draft_note", {"summary": {"$ref": {"step": "collect", "path": ["summary"]}}}),
        ],
        meta={"intent": "note"},
    )

    bundle = WorkflowBundle.from_task_plan(plan, inputs={"notes": "hello"})
    restored = bundle.to_task_plan()

    assert bundle.objective == "prepare note"
    assert [node.tool_name for node in bundle.nodes] == ["collect_notes", "draft_note"]
    assert restored.objective == plan.objective
    assert [step.name for step in restored.steps] == ["collect", "draft"]


def test_resolve_step_arguments_finds_variables_and_refs():
    args = {
        "customer": {"$var": "customer"},
        "summary": {"$ref": {"step": "collect", "path": ["summary"]}},
        "items": [{"$ref": {"step": "collect", "path": ["items", 0]}}],
    }

    result = resolve_step_arguments(
        args,
        variables={"customer": "Acme"},
        step_results={"collect": {"summary": "done", "items": ["first"]}},
    )

    assert result.ready is True
    assert result.args == {"customer": "Acme", "summary": "done", "items": ["first"]}


def test_resolve_step_arguments_reports_missing_values():
    result = resolve_step_arguments(
        {"customer": {"$var": "customer"}, "summary": {"$ref": {"step": "collect", "path": ["summary"]}}},
        variables={},
        step_results={},
    )

    assert result.ready is False
    assert result.missing_inputs == ["customer"]
    assert result.missing_references == ["collect"]


def test_workflow_readiness_orders_dependencies():
    bundle = WorkflowBundle(
        workflow_id="wf_1",
        objective="prepare note",
        nodes=[
            WorkflowNode("node_2", "draft", "draft_note", depends_on=["node_1"]),
            WorkflowNode("node_1", "collect", "collect_notes"),
        ],
    )

    assert [node.node_id for node in order_workflow_nodes(bundle.nodes)] == ["node_1", "node_2"]
    first = inspect_workflow_readiness(bundle)
    assert first.ready_nodes == ["node_1"]
    assert first.blocked_nodes == {"node_2": ["node_1"]}
    second = inspect_workflow_readiness(bundle, completed_nodes=["node_1"])
    assert second.ready_nodes == ["node_2"]
