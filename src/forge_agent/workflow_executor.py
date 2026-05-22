from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .models import StepAttempt, StepExecution, TaskPlan, TaskRunResult, utc_now
from .tool_registry import ToolRegistry
from .workflow import WorkflowBundle, WorkflowNode, order_workflow_nodes, resolve_step_arguments


@dataclass(slots=True)
class WorkflowStepResult:
    node_id: str
    name: str
    tool_name: str
    success: bool
    output: Any = None
    error: str | None = None
    attempts: list[StepAttempt] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "name": self.name,
            "tool_name": self.tool_name,
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "attempts": [attempt.to_dict() for attempt in self.attempts],
        }


@dataclass(slots=True)
class WorkflowExecutionResult:
    workflow_id: str
    objective: str
    status: str
    step_results: list[WorkflowStepResult]
    outputs: dict[str, Any]
    missing_inputs: list[str] = field(default_factory=list)
    missing_references: list[str] = field(default_factory=list)
    error_summary: str | None = None
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "objective": self.objective,
            "status": self.status,
            "step_results": [item.to_dict() for item in self.step_results],
            "outputs": self.outputs,
            "missing_inputs": self.missing_inputs,
            "missing_references": self.missing_references,
            "error_summary": self.error_summary,
            "created_at": self.created_at,
        }

    def to_task_run_result(self, *, session_id: str, task_text: str) -> TaskRunResult:
        return TaskRunResult(
            session_id=session_id,
            task_text=task_text,
            status=self.status,
            output=self.to_dict(),
            planner_used=True,
            retryable=self.status == "failed",
            error_summary=self.error_summary,
        )


class WorkflowExecutor:
    """Execute a WorkflowBundle using only registered local callables."""

    def __init__(self, tools: ToolRegistry) -> None:
        self.tools = tools

    def execute(self, bundle: WorkflowBundle, *, inputs: dict[str, Any] | None = None) -> WorkflowExecutionResult:
        variables = dict(bundle.inputs)
        variables.update(dict(inputs or {}))
        outputs: dict[str, Any] = {}
        step_results: list[WorkflowStepResult] = []
        missing_inputs: list[str] = []
        missing_refs: list[str] = []

        for node in order_workflow_nodes(bundle.nodes):
            resolved = resolve_step_arguments(node.args, variables=variables, step_results=_results_by_node_and_name(bundle.nodes, outputs))
            if not resolved.ready:
                missing_inputs.extend(resolved.missing_inputs)
                missing_refs.extend(resolved.missing_references)
                return WorkflowExecutionResult(
                    workflow_id=bundle.workflow_id,
                    objective=bundle.objective,
                    status="input_required" if resolved.missing_inputs else "blocked",
                    step_results=step_results,
                    outputs=outputs,
                    missing_inputs=sorted(set(missing_inputs)),
                    missing_references=sorted(set(missing_refs)),
                    error_summary="missing inputs or step outputs",
                )

            result = self._run_node(node, resolved.args)
            step_results.append(result)
            if not result.success:
                return WorkflowExecutionResult(
                    workflow_id=bundle.workflow_id,
                    objective=bundle.objective,
                    status="failed",
                    step_results=step_results,
                    outputs=outputs,
                    error_summary=result.error,
                )
            outputs[node.node_id] = result.output

        return WorkflowExecutionResult(
            workflow_id=bundle.workflow_id,
            objective=bundle.objective,
            status="completed",
            step_results=step_results,
            outputs=outputs,
        )

    def execute_plan(self, plan: TaskPlan, *, inputs: dict[str, Any] | None = None) -> WorkflowExecutionResult:
        return self.execute(WorkflowBundle.from_task_plan(plan, inputs=inputs), inputs=inputs)

    def _run_node(self, node: WorkflowNode, args: dict[str, Any]) -> WorkflowStepResult:
        tool = self.tools.get(node.tool_name)
        if tool is None:
            attempt = StepAttempt(attempt_no=1, requested_tool_name=node.tool_name, tool_name=node.tool_name, args=args, success=False, error="unknown tool")
            return WorkflowStepResult(node.node_id, node.name, node.tool_name, False, error="unknown tool", attempts=[attempt])
        try:
            output = self.tools.run(node.tool_name, **args)
        except Exception as exc:  # noqa: BLE001 - store safe error summary for compatibility layer
            attempt = StepAttempt(attempt_no=1, requested_tool_name=node.tool_name, tool_name=node.tool_name, args=args, success=False, error=str(exc))
            return WorkflowStepResult(node.node_id, node.name, node.tool_name, False, error=str(exc), attempts=[attempt])
        attempt = StepAttempt(attempt_no=1, requested_tool_name=node.tool_name, tool_name=node.tool_name, args=args, success=True, result=output)
        return WorkflowStepResult(node.node_id, node.name, node.tool_name, True, output=output, attempts=[attempt])


def _results_by_node_and_name(nodes: list[WorkflowNode], outputs: dict[str, Any]) -> dict[str, Any]:
    results: dict[str, Any] = {}
    for node in nodes:
        if node.node_id in outputs:
            results[node.node_id] = outputs[node.node_id]
            results[node.name] = outputs[node.node_id]
    return results
