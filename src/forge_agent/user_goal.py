from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .governance import GovernanceEngine, GovernanceVerdict
from .models import TaskPlan, utc_now
from .planner import SimplePlanner
from .skill_lifecycle import SkillDefinition, SkillLibrary
from .tool_registry import ToolRegistry
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
            "created_at": self.created_at,
        }


class UserGoalRunner:
    """Plain-user entrypoint for the zero-config skill autopilot path.

    The runner prefers a reusable skill when one matches. Otherwise it falls
    back to SimplePlanner. It can explain, preview, or execute through local
    registered tools. It does not require users to know about skills, tools,
    gateways, or workflow internals.
    """

    def __init__(self, tools: ToolRegistry, *, skills: SkillLibrary | None = None, governance: GovernanceEngine | None = None) -> None:
        self.tools = tools
        self.skills = skills or SkillLibrary()
        self.planner = SimplePlanner(tools)
        self.governance = governance or GovernanceEngine()
        self.executor = WorkflowExecutor(tools)

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
        if skill is not None:
            self.skills.record_outcome(skill.skill_id, success=status == "completed")
        return UserGoalResult(goal, status, text, normalized_mode, plan=plan, skill=skill, governance=verdict, execution=execution)


def explain_plan(plan: TaskPlan, *, skill: SkillDefinition | None = None, source: str = "planner") -> str:
    intro = "I found a reusable skill." if skill else "I made a plan."
    steps = "; ".join(f"{index + 1}. {step.name}" for index, step in enumerate(plan.steps))
    return f"{intro} Source: {source}. I will do {len(plan.steps)} step(s): {steps}."


def _missing_text(missing: list[str]) -> str:
    if not missing:
        return "I need more information before I continue."
    return "I need this first: " + ", ".join(missing) + "."
