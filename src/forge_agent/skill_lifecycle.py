from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any
import json
import uuid

from .models import SkillKind, StepExecution, TaskPlan, utc_now
from .workflow import WorkflowBundle
from .workflow_executor import WorkflowExecutionResult


_DYNAMIC_INPUT_NAMES = {"text", "notes", "customer", "target_language", "style", "tone", "subject", "body"}


@dataclass(slots=True)
class TaskTrace:
    trace_id: str
    session_id: str
    task_text: str
    goal_key: str
    plan_objective: str
    steps: list[StepExecution]
    succeeded: bool
    created_at: str = field(default_factory=utc_now)
    reused_skill_id: str | None = None
    plan_intent: str = ""
    memory_bundle: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "session_id": self.session_id,
            "task_text": self.task_text,
            "goal_key": self.goal_key,
            "plan_objective": self.plan_objective,
            "steps": [step.to_dict() for step in self.steps],
            "succeeded": self.succeeded,
            "created_at": self.created_at,
            "reused_skill_id": self.reused_skill_id,
            "plan_intent": self.plan_intent,
            "memory_bundle": dict(self.memory_bundle),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "TaskTrace":
        data = dict(payload or {})
        return cls(
            trace_id=str(data["trace_id"]),
            session_id=str(data["session_id"]),
            task_text=str(data["task_text"]),
            goal_key=str(data.get("goal_key", "") or ""),
            plan_objective=str(data.get("plan_objective", "") or ""),
            steps=[StepExecution.from_dict(step) for step in data.get("steps", [])],
            succeeded=bool(data.get("succeeded", False)),
            created_at=str(data.get("created_at", utc_now())),
            reused_skill_id=data.get("reused_skill_id"),
            plan_intent=str(data.get("plan_intent", "") or ""),
            memory_bundle=dict(data.get("memory_bundle", {}) or {}),
        )

    @classmethod
    def from_execution(
        cls,
        *,
        session_id: str,
        task_text: str,
        goal_key: str,
        plan: TaskPlan,
        execution: WorkflowExecutionResult,
        reused_skill_id: str | None = None,
        memory_bundle: dict[str, Any] | None = None,
    ) -> "TaskTrace":
        steps: list[StepExecution] = []
        for step_result in execution.step_results:
            steps.append(
                StepExecution(
                    name=step_result.name,
                    tool_name=step_result.tool_name,
                    args=step_result.attempts[-1].args if step_result.attempts else {},
                    result=step_result.output,
                    success=step_result.success,
                    error=step_result.error,
                    attempts=step_result.attempts,
                )
            )
        return cls(
            trace_id=f"trace_{uuid.uuid4().hex[:12]}",
            session_id=session_id,
            task_text=task_text,
            goal_key=goal_key,
            plan_objective=plan.objective,
            steps=steps,
            succeeded=execution.status == "completed",
            reused_skill_id=reused_skill_id,
            plan_intent=str(plan.meta.get("intent", "") or ""),
            memory_bundle=dict(memory_bundle or {}),
        )


@dataclass(slots=True)
class SkillDefinition:
    skill_id: str
    name: str
    kind: SkillKind
    goal_key: str
    trigger_text: str
    description: str
    steps: list[StepExecution]
    objective_key: str = ""
    intent_key: str = ""
    plan_signature: str = ""
    match_hints: list[str] = field(default_factory=list)
    tool_names: list[str] = field(default_factory=list)
    input_variables: list[str] = field(default_factory=list)
    example_inputs: dict[str, Any] = field(default_factory=dict)
    version: int = 1
    enabled: bool = True
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)
    success_count: int = 0
    failure_streak: int = 0
    source_trace_ids: list[str] = field(default_factory=list)
    lifecycle_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["kind"] = self.kind.value
        data["steps"] = [step.to_dict() for step in self.steps]
        return data

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "SkillDefinition":
        data = dict(payload or {})
        return cls(
            skill_id=str(data["skill_id"]),
            name=str(data.get("name", data["skill_id"])),
            kind=SkillKind(str(data.get("kind", SkillKind.WORKFLOW.value))),
            goal_key=str(data.get("goal_key", "") or ""),
            trigger_text=str(data.get("trigger_text", "") or ""),
            description=str(data.get("description", "") or ""),
            steps=[StepExecution.from_dict(step) for step in data.get("steps", [])],
            objective_key=str(data.get("objective_key", "") or ""),
            intent_key=str(data.get("intent_key", "") or ""),
            plan_signature=str(data.get("plan_signature", "") or ""),
            match_hints=[str(item) for item in data.get("match_hints", [])],
            tool_names=[str(item) for item in data.get("tool_names", [])],
            input_variables=[str(item) for item in data.get("input_variables", [])],
            example_inputs=dict(data.get("example_inputs", {}) or {}),
            version=int(data.get("version", 1) or 1),
            enabled=bool(data.get("enabled", True)),
            created_at=str(data.get("created_at", utc_now())),
            updated_at=str(data.get("updated_at", utc_now())),
            success_count=int(data.get("success_count", 0) or 0),
            failure_streak=int(data.get("failure_streak", 0) or 0),
            source_trace_ids=[str(item) for item in data.get("source_trace_ids", [])],
            lifecycle_notes=[str(item) for item in data.get("lifecycle_notes", [])],
        )

    @classmethod
    def new(
        cls,
        *,
        goal_key: str,
        trigger_text: str,
        description: str,
        steps: list[StepExecution],
        kind: SkillKind = SkillKind.WORKFLOW,
        source_trace_ids: list[str] | None = None,
        objective_key: str = "",
        intent_key: str = "",
        plan_signature: str = "",
        match_hints: list[str] | None = None,
        input_variables: list[str] | None = None,
        example_inputs: dict[str, Any] | None = None,
    ) -> "SkillDefinition":
        suffix = goal_key.replace("_", "-")[:32] or "skill"
        tool_names = sorted({step.tool_name for step in steps})
        return cls(
            skill_id=f"skill_{uuid.uuid4().hex[:10]}",
            name=f"{suffix}-{kind.value}",
            kind=kind,
            goal_key=goal_key,
            trigger_text=trigger_text,
            description=description,
            steps=steps,
            objective_key=objective_key,
            intent_key=intent_key,
            plan_signature=plan_signature or plan_signature_from_steps(steps),
            match_hints=sorted(set(match_hints or tokenize_skill_text(trigger_text + " " + description))),
            tool_names=tool_names,
            input_variables=list(input_variables or []),
            example_inputs=dict(example_inputs or {}),
            source_trace_ids=list(source_trace_ids or []),
        )

    def to_plan(self, *, inputs: dict[str, Any] | None = None) -> TaskPlan:
        meta = {
            "skill_id": self.skill_id,
            "skill_version": self.version,
            "intent": self.intent_key,
            "input_names": list(self.input_variables),
        }
        if inputs:
            meta["provided_inputs"] = sorted(inputs)
        return TaskPlan(objective=self.objective_key or self.description or self.trigger_text, steps=[StepExecution.from_dict(step.to_dict()) for step in self.steps], meta=meta)

    def to_workflow(self, *, inputs: dict[str, Any] | None = None) -> WorkflowBundle:
        return WorkflowBundle.from_task_plan(self.to_plan(inputs=inputs), inputs=inputs)


@dataclass(slots=True)
class PromotionDecision:
    accepted: bool
    reason: str
    skill: SkillDefinition | None = None

    def to_dict(self) -> dict[str, Any]:
        return {"accepted": self.accepted, "reason": self.reason, "skill": self.skill.to_dict() if self.skill else None}


class SkillLifecycleEngine:
    def __init__(self, repeat_threshold: int = 2) -> None:
        self.repeat_threshold = max(1, repeat_threshold)

    def consider(self, trace: TaskTrace, prior_successes: list[TaskTrace], existing_skill: SkillDefinition | None = None) -> PromotionDecision:
        if not trace.succeeded:
            return PromotionDecision(False, "trace_failed")
        if trace.reused_skill_id:
            return PromotionDecision(False, "already_skill_driven")
        if not trace.steps:
            return PromotionDecision(False, "no_steps")
        successful = [item for item in prior_successes if item.succeeded and plan_signature_from_steps(item.steps) == plan_signature_from_steps(trace.steps)]
        if existing_skill is not None:
            upgraded = SkillDefinition.from_dict(existing_skill.to_dict())
            upgraded.version += 1
            upgraded.updated_at = utc_now()
            upgraded.success_count += 1
            upgraded.source_trace_ids = _merge_unique(upgraded.source_trace_ids, [trace.trace_id])
            upgraded.lifecycle_notes.append("upgraded from successful trace")
            return PromotionDecision(True, "upgrade_existing_skill", upgraded)
        if len(successful) < self.repeat_threshold:
            return PromotionDecision(False, f"needs_{self.repeat_threshold}_successful_traces")
        window = successful[-self.repeat_threshold:]
        template_steps, input_variables, example_inputs = template_steps_from_traces(window)
        skill = SkillDefinition.new(
            goal_key=trace.goal_key,
            trigger_text=trace.task_text,
            description=f"Repeat this workflow for {trace.plan_objective}",
            steps=template_steps,
            kind=SkillKind.WORKFLOW,
            source_trace_ids=[item.trace_id for item in window],
            objective_key=normalize_key(trace.plan_objective),
            intent_key=trace.plan_intent or normalize_key(trace.plan_objective),
            plan_signature=plan_signature_from_steps(template_steps),
            match_hints=tokenize_skill_text(trace.task_text + " " + trace.plan_objective),
            input_variables=input_variables,
            example_inputs=example_inputs,
        )
        skill.success_count = len(window)
        skill.lifecycle_notes.append("promoted from repeated successful traces")
        return PromotionDecision(True, "promote_repeated_workflow", skill)


class SkillLibrary:
    def __init__(self) -> None:
        self._skills: dict[str, SkillDefinition] = {}

    def add(self, skill: SkillDefinition) -> SkillDefinition:
        self._skills[skill.skill_id] = skill
        return skill

    def get(self, skill_id: str) -> SkillDefinition | None:
        return self._skills.get(skill_id)

    def list(self) -> list[SkillDefinition]:
        return sorted(self._skills.values(), key=lambda item: (item.goal_key, item.name, item.skill_id))

    def find_best(self, *, task_text: str, tool_names: list[str] | None = None) -> SkillDefinition | None:
        candidates = [skill for skill in self._skills.values() if skill.enabled]
        if not candidates:
            return None
        desired_tools = set(tool_names or [])
        scored: list[tuple[float, SkillDefinition]] = []
        for skill in candidates:
            score = token_overlap(task_text, skill.match_hints)
            if desired_tools:
                skill_tools = set(skill.tool_names)
                score += len(desired_tools & skill_tools) / max(1, len(desired_tools | skill_tools))
            score += min(skill.success_count, 5) / 10.0
            scored.append((score, skill))
        scored.sort(key=lambda item: (item[0], item[1].success_count, item[1].updated_at), reverse=True)
        return scored[0][1] if scored and scored[0][0] > 0 else None

    def record_outcome(self, skill_id: str, *, success: bool) -> SkillDefinition | None:
        skill = self._skills.get(skill_id)
        if skill is None:
            return None
        skill.updated_at = utc_now()
        if success:
            skill.success_count += 1
            skill.failure_streak = 0
        else:
            skill.failure_streak += 1
        return skill

    def to_jsonl(self) -> str:
        return "\n".join(json.dumps(skill.to_dict(), ensure_ascii=False, sort_keys=True) for skill in self.list()) + ("\n" if self._skills else "")

    @classmethod
    def from_jsonl(cls, content: str) -> "SkillLibrary":
        library = cls()
        for line in content.splitlines():
            if not line.strip():
                continue
            library.add(SkillDefinition.from_dict(json.loads(line)))
        return library


def template_steps_from_traces(traces: list[TaskTrace]) -> tuple[list[StepExecution], list[str], dict[str, Any]]:
    if not traces:
        return [], [], {}
    base = traces[-1]
    input_variables: list[str] = []
    example_inputs: dict[str, Any] = {}
    steps: list[StepExecution] = []
    previous_names = {step.name for step in base.steps}
    for index, step in enumerate(base.steps):
        args: dict[str, Any] = {}
        for key, value in step.args.items():
            variable_name = key if key in _DYNAMIC_INPUT_NAMES else ""
            if variable_name:
                args[key] = {"$var": variable_name}
                if variable_name not in input_variables:
                    input_variables.append(variable_name)
                    example_inputs[variable_name] = value
                continue
            ref = _find_previous_result_ref(value, traces, step_index=index, previous_names=previous_names)
            args[key] = ref if ref is not None else value
        steps.append(StepExecution(name=step.name, tool_name=step.tool_name, args=args))
    return steps, input_variables, example_inputs


def plan_signature_from_steps(steps: list[StepExecution]) -> str:
    return " >> ".join(f"{step.tool_name}:{','.join(sorted(step.args))}" for step in steps)


def normalize_key(text: str) -> str:
    tokens = tokenize_skill_text(text)
    return "_".join(tokens)[:96]


def tokenize_skill_text(text: str) -> list[str]:
    import re

    stop = {"a", "an", "and", "for", "from", "in", "of", "on", "or", "the", "to", "with", "this", "that"}
    return [item for item in re.findall(r"[a-z0-9]+", text.lower()) if item and item not in stop]


def token_overlap(text: str, hints: list[str]) -> float:
    tokens = set(tokenize_skill_text(text))
    hint_tokens = set(hints)
    if not tokens or not hint_tokens:
        return 0.0
    return len(tokens & hint_tokens) / len(tokens | hint_tokens)


def _merge_unique(left: list[str], right: list[str]) -> list[str]:
    output = list(left)
    for item in right:
        if item not in output:
            output.append(item)
    return output


def _find_previous_result_ref(value: Any, traces: list[TaskTrace], *, step_index: int, previous_names: set[str]) -> dict[str, Any] | None:
    if step_index <= 0:
        return None
    for trace in traces:
        if step_index >= len(trace.steps):
            continue
        for prior in trace.steps[:step_index]:
            if prior.name not in previous_names:
                continue
            path = _path_to_value(prior.result, value)
            if path is not None:
                return {"$ref": {"step": prior.name, "path": path}}
    return None


def _path_to_value(container: Any, expected: Any) -> list[Any] | None:
    if container == expected:
        return []
    if isinstance(container, dict):
        for key, value in container.items():
            nested = _path_to_value(value, expected)
            if nested is not None:
                return [key] + nested
    if isinstance(container, list):
        for index, value in enumerate(container):
            nested = _path_to_value(value, expected)
            if nested is not None:
                return [index] + nested
    return None
