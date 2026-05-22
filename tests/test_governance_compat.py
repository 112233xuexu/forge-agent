from forge_agent.governance import GovernanceEngine, GovernancePolicy, build_execution_ledger, parse_ledger, replay_ledger, serialize_ledger
from forge_agent.models import ExecutionCheckpoint, StepExecution, TaskPlan
from forge_agent.workflow import WorkflowBundle, WorkflowNode
from forge_agent.workflow_executor import WorkflowExecutor
from forge_agent.tool_registry import ToolRegistry


def plan_with(tool_name: str) -> TaskPlan:
    return TaskPlan(objective="do work", steps=[StepExecution("step", tool_name, {})])


def test_governance_allows_low_risk_plan():
    verdict = GovernanceEngine().evaluate_plan(plan_with("summarize_notes"))

    assert verdict.decision == "allow"
    assert verdict.allowed is True
    assert verdict.needs_confirmation is False
    assert verdict.risk_level == "low"


def test_governance_requires_confirmation_for_write_or_send_tools():
    verdict = GovernanceEngine().evaluate_plan(plan_with("send_message"))

    assert verdict.decision == "confirm"
    assert verdict.needs_confirmation is True
    assert verdict.risk_level == "high"
    assert verdict.required_confirmations == ["send_message"]


def test_governance_blocks_disallowed_tools_and_checkpoint_eval():
    policy = GovernancePolicy(blocked_tools={"delete_file"})
    engine = GovernanceEngine(policy)
    checkpoint = ExecutionCheckpoint.new(
        session_id="sess_1",
        task_text="remove file",
        plan=plan_with("delete_file"),
        inputs={},
    )

    verdict = engine.evaluate_checkpoint(checkpoint)

    assert verdict.decision == "block"
    assert verdict.risk_level == "critical"
    assert verdict.blocked_tools == ["delete_file"]


def test_ledger_replay_roundtrip_and_tamper_detection():
    tools = ToolRegistry()
    tools.register("summarize_notes", lambda: {"summary": "ok"})
    execution = WorkflowExecutor(tools).execute(
        WorkflowBundle(workflow_id="wf_1", objective="do work", nodes=[WorkflowNode("node_1", "step", "summarize_notes")])
    )
    plan = plan_with("summarize_notes")
    checkpoint = ExecutionCheckpoint.new(session_id="sess_1", task_text="do work", plan=plan, inputs={})
    verdict = GovernanceEngine().evaluate_checkpoint(checkpoint)

    ledger = build_execution_ledger(checkpoint=checkpoint, plan=plan, verdict=verdict, execution=execution)
    restored = parse_ledger(serialize_ledger(ledger))

    assert replay_ledger(restored).valid is True
    restored[1].payload["objective"] = "changed"
    replay = replay_ledger(restored)
    assert replay.valid is False
    assert restored[1].entry_id in replay.broken_entry_ids
