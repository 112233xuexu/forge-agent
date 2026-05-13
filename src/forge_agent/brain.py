from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class BrainPlan:
    goal: str
    intent: str
    next_step: str
    needs_user_approval: bool
    confidence: float
    safety_level: str = "safe_preview"
    suggested_command: str | None = None
    notes: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class BrainAdapter:
    """Local deterministic planner for v1.9.

    The planner turns a plain-language goal into a previewable Forge Agent
    intent. It does not perform actions by itself.
    """

    def plan(self, goal: str) -> BrainPlan:
        text = " ".join(goal.strip().split())
        lower = text.lower()
        if not text:
            return BrainPlan(
                goal=goal,
                intent="unknown",
                next_step="doctor",
                needs_user_approval=False,
                confidence=0.0,
                safety_level="safe_preview",
                suggested_command="forge-agent doctor",
                notes=["empty goal"],
                metadata={"planner": "local-deterministic"},
            )
        if _contains_any(lower, ["organize", "整理", "invoice", "receipt", "发票", "收据"]):
            return BrainPlan(
                goal=text,
                intent="organize_files",
                next_step="preview organize plan",
                needs_user_approval=False,
                confidence=0.75,
                safety_level="dry_run_first",
                suggested_command="forge-agent organize <folder>",
                notes=["dry run first", "use --approve only after reviewing the plan"],
                metadata={"planner": "local-deterministic", "risk_boundary": "approval before file moves"},
            )
        if _contains_any(lower, ["ppt", "slides", "presentation", "幻灯片", "汇报"]):
            return BrainPlan(
                goal=text,
                intent="make_ppt",
                next_step="create local ppt outline",
                needs_user_approval=False,
                confidence=0.70,
                safety_level="local_artifact",
                suggested_command=f"forge-agent make ppt {text!r}",
                notes=["local artifact"],
                metadata={"planner": "local-deterministic"},
            )
        if _contains_any(lower, ["report", "报告", "总结"]):
            return BrainPlan(
                goal=text,
                intent="make_report",
                next_step="create local report",
                needs_user_approval=False,
                confidence=0.70,
                safety_level="local_artifact",
                suggested_command=f"forge-agent make report {text!r}",
                notes=["local artifact"],
                metadata={"planner": "local-deterministic"},
            )
        if _contains_any(lower, ["news", "brief", "新闻", "简报"]):
            return BrainPlan(
                goal=text,
                intent="make_news",
                next_step="create local news brief",
                needs_user_approval=False,
                confidence=0.65,
                safety_level="template_only",
                suggested_command=f"forge-agent make news {text!r}",
                notes=["template only", "does not fetch live news"],
                metadata={"planner": "local-deterministic"},
            )
        if _contains_any(lower, ["storyboard", "video", "视频", "脚本", "分镜"]):
            return BrainPlan(
                goal=text,
                intent="make_storyboard",
                next_step="create local storyboard",
                needs_user_approval=False,
                confidence=0.65,
                safety_level="template_only",
                suggested_command=f"forge-agent make storyboard {text!r}",
                notes=["template only", "does not render video"],
                metadata={"planner": "local-deterministic"},
            )
        return BrainPlan(
            goal=text,
            intent="local_task",
            next_step="record local task",
            needs_user_approval=False,
            confidence=0.45,
            safety_level="safe_preview",
            suggested_command=f"forge-agent do {text!r}",
            notes=["fallback"],
            metadata={"planner": "local-deterministic"},
        )


def _contains_any(text: str, candidates: list[str]) -> bool:
    return any(candidate in text for candidate in candidates)
