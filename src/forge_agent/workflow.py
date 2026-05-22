from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any
import uuid

from .models import StepExecution, TaskPlan, utc_now


@dataclass(slots=True)
class WorkflowNode:
    node_id: str
    name: str
    tool_name: str
    args: dict[str, Any] = field(default_factory=dict)
    depends_on: list[str] = field(default_factory=list)
    description: str = ""
    optional: bool = False
    timeout_seconds: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "WorkflowNode":
        data = dict(payload or {})
        return cls(
            node_id=str(data.get("node_id") or data.get("id") or f"node_{uuid.uuid4().hex[:8]}"),
            name=str(data.get("name") or data.get("step_name") or data.get("tool_name") or "step"),
            tool_name=str(data.get("tool_name") or data.get("tool") or ""),
            args=dict(data.get("args", {}) or {}),
            depends_on=[str(item) for item in data.get("depends_on", [])],
            description=str(data.get("description", "") or ""),
            optional=bool(data.get("optional", False)),
            timeout_seconds=data.get("timeout_seconds"),
            metadata=dict(data.get("metadata", {}) or {}),
        )

    @classmethod
    def from_step(cls, step: StepExecution, *, index: int = 0) -> "WorkflowNode":
        metadata = {"source": "task_plan", "step_index": index}
        return cls(
            node_id=f"node_{index + 1}",
            name=step.name,
            tool_name=step.tool_name,
            args=dict(step.args),
            depends_on=_infer_dependencies(step.args),
            metadata=metadata,
        )

    def to_step(self) -> StepExecution:
        return StepExecution(name=self.name, tool_name=self.tool_name, args=dict(self.args))


@dataclass(slots=True)
class WorkflowBundle:
    workflow_id: str
    objective: str
    nodes: list[WorkflowNode]
    inputs: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now)
    schema_version: int = 1

    def to_dict(self) -> dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "objective": self.objective,
            "nodes": [node.to_dict() for node in self.nodes],
            "inputs": dict(self.inputs),
            "metadata": dict(self.metadata),
            "created_at": self.created_at,
            "schema_version": self.schema_version,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "WorkflowBundle":
        data = dict(payload or {})
        return cls(
            workflow_id=str(data.get("workflow_id") or data.get("bundle_id") or f"wf_{uuid.uuid4().hex[:12]}"),
            objective=str(data.get("objective", "") or ""),
            nodes=[WorkflowNode.from_dict(item) for item in data.get("nodes", [])],
            inputs=dict(data.get("inputs", {}) or {}),
            metadata=dict(data.get("metadata", {}) or {}),
            created_at=str(data.get("created_at", utc_now())),
            schema_version=int(data.get("schema_version", 1) or 1),
        )

    @classmethod
    def from_task_plan(cls, plan: TaskPlan, *, inputs: dict[str, Any] | None = None) -> "WorkflowBundle":
        return cls(
            workflow_id=f"wf_{uuid.uuid4().hex[:12]}",
            objective=plan.objective,
            nodes=[WorkflowNode.from_step(step, index=index) for index, step in enumerate(plan.steps)],
            inputs=dict(inputs or {}),
            metadata={"source": "task_plan", "plan_meta": dict(plan.meta)},
        )

    def to_task_plan(self) -> TaskPlan:
        return TaskPlan(
            objective=self.objective,
            steps=[node.to_step() for node in order_workflow_nodes(self.nodes)],
            meta={"workflow_id": self.workflow_id, **dict(self.metadata)},
        )


@dataclass(slots=True)
class StepResolutionResult:
    args: dict[str, Any]
    missing_inputs: list[str] = field(default_factory=list)
    missing_references: list[str] = field(default_factory=list)

    @property
    def ready(self) -> bool:
        return not self.missing_inputs and not self.missing_references

    def to_dict(self) -> dict[str, Any]:
        return {"args": self.args, "missing_inputs": self.missing_inputs, "missing_references": self.missing_references, "ready": self.ready}


@dataclass(slots=True)
class WorkflowReadiness:
    ready_nodes: list[str]
    blocked_nodes: dict[str, list[str]]
    completed_nodes: list[str]

    @property
    def ready(self) -> bool:
        return bool(self.ready_nodes) or not self.blocked_nodes

    def to_dict(self) -> dict[str, Any]:
        return {"ready_nodes": self.ready_nodes, "blocked_nodes": self.blocked_nodes, "completed_nodes": self.completed_nodes, "ready": self.ready}


def resolve_step_arguments(args: dict[str, Any], *, variables: dict[str, Any], step_results: dict[str, Any] | None = None) -> StepResolutionResult:
    missing_inputs: list[str] = []
    missing_refs: list[str] = []

    def resolve(value: Any) -> Any:
        if isinstance(value, dict) and set(value) == {"$var"}:
            name = str(value["$var"])
            if name not in variables or variables.get(name) in (None, ""):
                missing_inputs.append(name)
                return None
            return variables[name]
        if isinstance(value, dict) and set(value) == {"$ref"}:
            ref = dict(value["$ref"] or {})
            step_name = str(ref.get("step", "") or "")
            path = list(ref.get("path", []) or [])
            results = dict(step_results or {})
            if step_name not in results:
                missing_refs.append(step_name)
                return None
            current = results[step_name]
            for part in path:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                elif isinstance(current, list) and isinstance(part, int) and 0 <= part < len(current):
                    current = current[part]
                else:
                    missing_refs.append(f"{step_name}:{'.'.join(str(item) for item in path)}")
                    return None
            return current
        if isinstance(value, dict):
            return {key: resolve(item) for key, item in value.items()}
        if isinstance(value, list):
            return [resolve(item) for item in value]
        return value

    resolved = resolve(args)
    return StepResolutionResult(args=dict(resolved or {}), missing_inputs=sorted(set(missing_inputs)), missing_references=sorted(set(missing_refs)))


def order_workflow_nodes(nodes: list[WorkflowNode]) -> list[WorkflowNode]:
    by_id = {node.node_id: node for node in nodes}
    ordered: list[WorkflowNode] = []
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: WorkflowNode) -> None:
        if node.node_id in visited:
            return
        if node.node_id in visiting:
            raise ValueError(f"workflow dependency cycle at {node.node_id}")
        visiting.add(node.node_id)
        for dep in node.depends_on:
            if dep in by_id:
                visit(by_id[dep])
        visiting.remove(node.node_id)
        visited.add(node.node_id)
        ordered.append(node)

    for node in nodes:
        visit(node)
    return ordered


def inspect_workflow_readiness(bundle: WorkflowBundle, *, completed_nodes: list[str] | None = None) -> WorkflowReadiness:
    completed = set(completed_nodes or [])
    ready: list[str] = []
    blocked: dict[str, list[str]] = {}
    for node in order_workflow_nodes(bundle.nodes):
        if node.node_id in completed:
            continue
        missing = [dep for dep in node.depends_on if dep not in completed]
        if missing:
            blocked[node.node_id] = missing
        else:
            ready.append(node.node_id)
    return WorkflowReadiness(ready_nodes=ready, blocked_nodes=blocked, completed_nodes=sorted(completed))


def _infer_dependencies(value: Any) -> list[str]:
    deps: set[str] = set()

    def walk(item: Any) -> None:
        if isinstance(item, dict):
            if "$ref" in item and isinstance(item["$ref"], dict):
                step_name = str(item["$ref"].get("step", "") or "")
                if step_name:
                    deps.add(_node_id_from_step_name(step_name))
            for nested in item.values():
                walk(nested)
        elif isinstance(item, list):
            for nested in item:
                walk(nested)

    walk(value)
    return sorted(deps)


def _node_id_from_step_name(step_name: str) -> str:
    normalized = step_name.strip().lower().replace(" ", "_").replace("-", "_")
    return normalized or "step"
