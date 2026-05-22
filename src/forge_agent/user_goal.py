from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .governance import GovernanceEngine, GovernanceVerdict
from .models import TaskPlan, utc_now
from .planner import SimplePlanner
from .skill_lifecycle import SkillDefinition, SkillLifecycleEngine, SkillLibrary, TaskTrace, normalize_key
from .tool_registry import ToolRegistry
from .user_goal_store import UserGoalStore
from .workflow import WorkflowBundle
from .workflow_executor import WorkflowExecutionResult, WorkflowExecutor


@dataclass(slots=True)
class UserGoalResult:
    goal: str
    status: str
    text: str
    mode: str
    plan: TaskPlan | None = None
    skill: SkillDefinition | None = None
    governance: GovernanceVerdict | None = None
    execution: WorkflowExecutionResult | None = None
    missing_inputs: list[str] = field(default_factory=list)
    promoted_skill: SkillDefinition | None = None
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "goal": self.goal,
            "status": self.status,
            "text": self.text,
            "mode": self.mode,
            "plan": self.plan.to_dict() if self.plan else None,
            "skill": self.skill.to_dict() if self.skill else None,
            "governance": self.governance.to_dict() if self.governance else None,
            "execution": self.execution.to_dict() if self.execution else None,
            "missing_inputs": list(self.missing_inputs),
            "promoted_skill": self.promoted_skill.to_dict() if self.promoted_skill else None,
            "created_at": self.created_at,
        }


class UserGoalRunner:
    """Plain-user entrypoint for the zero-config skill path."""

    def __init__(
        self,
        tools: ToolRegistry,
        *,
        skills: SkillLibrary | None = None,
        governance: GovernanceEngine | None = None,
        store: UserGoalStore | None = None,
        lifecycle: SkillLifecycleEngine | None = None,
    ) -> None:
        self.tools = tools
        self.store = store
        self.skills = skills or (store.load_skills() if store else SkillLibrary())
        self.planner = SimplePlanner(tools)
        self.governance = governance or GovernanceEngine()
        self.executor = WorkflowExecutor(tools)
        self.lifecycle = lifecycle or SkillLifecycleEngine(repeat_threshold=2)

    def run(self, goal: str, *, inputs: dict[str, Any] | None = None, mode: str = "preview") -> UserGoalResult:
        normalized_mode = mode if mode in {"preview", "explain", "execute"} else "preview"
        provided = dict(inputs or {})
        skill = self.skills.find_best(task_text=goal)
        if skill is not None:
            plan = skill.to_plan(inputs=provided)
            source = "skill"
        else:
            planned = self.planner.build_plan(goal, inputs=provided)
            if planned.missing_inputs:
                return UserGoalResult(goal, "input_required", _missing_text(planned.missing_inputs), normalized_mode, missing_inputs=planned.missing_inputs)
            if planned.plan is None:
                return UserGoalResult(goal, "no_plan", "I do not yet know how to do that safely.", normalized_mode)
            plan = planned.plan
            source = "planner"

        verdict = self.governance.evaluate_plan(plan)
        if verdict.decision == "block":
            return UserGoalResult(goal, "blocked", "I cannot continue with that plan.", normalized_mode, plan=plan, skill=skill, governance=verdict)
        if normalized_mode == "explain":
            return UserGoalResult(goal, "explained", explain_plan(plan, skill=skill, source=source), normalized_mode, plan=plan, skill=skill, governance=verdict)
        if normalized_mode == "preview" or verdict.decision == "confirm":
            status = "confirmation_required" if verdict.decision == "confirm" else "planned"
            text = "Please confirm before I continue." if verdict.decision == "confirm" else explain_plan(plan, skill=skill, source=source)
            return UserGoalResult(goal, status, text, normalized_mode, plan=plan, skill=skill, governance=verdict)

        execution = self.executor.execute(WorkflowBundle.from_task_plan(plan, inputs=provided), inputs=provided)
        status = execution.status
        text = "I completed the work." if status == "completed" else "I could not complete the work."
        promoted = self._record(goal, plan, execution, skill=skill) if status == "completed" else None
        return UserGoalResult(goal, status, text, normalized_mode, plan=plan, skill=skill, governance=verdict, execution=execution, promoted_skill=promoted)

    def _record(self, goal: str, plan: TaskPlan, execution: WorkflowExecutionResult, *, skill: SkillDefinition | None) -> SkillDefinition | None:
        if skill is not None:
            self.skills.record_outcome(skill.skill_id, success=True)
            if self.store:
                self.store.save_skills(self.skills)
            return None
        if self.store is None:
            return None
        goal_key = str(plan.meta.get("intent") or normalize_key(plan.objective or goal))
        trace = TaskTrace.from_execution(session_id="user-goal", task_text=goal, goal_key=goal_key, plan=plan, execution=execution)
        self.store.append_trace(trace)
        prior = self.store.list_traces(goal_key=goal_key)
        decision = self.lifecycle.consider(trace, prior)
        if decision.accepted and decision.skill is not None:
            self.skills.add(decision.skill)
            self.store.save_skills(self.skills)
            return decision.skill
        return None


def explain_plan(plan: TaskPlan, *, skill: SkillDefinition | None = None, source: str = "planner") -> str:
    intro = "I found a reusable skill." if skill else "I made a plan."
    steps = "; ".join(f"{index + 1}. {step.name}" for index, step in enumerate(plan.steps))
    return f"{intro} Source: {source}. I will do {len(plan.steps)} step(s): {steps}."


def _missing_text(missing: list[str]) -> str:
    if not missing:
        return "I need more information before I continue."
    return "I need this first: " + ", ".join(missing) + "."
