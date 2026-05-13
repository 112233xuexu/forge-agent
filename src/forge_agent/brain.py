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
    notes: list[str] = field(default_factory=list)

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
            return BrainPlan(goal=goal, intent="unknown", next_step="doctor", needs_user_approval=False, confidence=0.0, notes=["empty goal"])
        if _contains_any(lower, ["organize", "整理", "invoice", "receipt", "发票", "收据"]):
            return BrainPlan(goal=text, intent="organize_files", next_step="preview organize plan", needs_user_approval=False, confidence=0.75, notes=["dry run first"])
        if _contains_any(lower, ["ppt", "slides", "presentation", "幻灯片", "汇报"]):
            return BrainPlan(goal=text, intent="make_ppt", next_step="create local ppt outline", needs_user_approval=False, confidence=0.70, notes=["local artifact"])
        if _contains_any(lower, ["report", "报告", "总结"]):
            return BrainPlan(goal=text, intent="make_report", next_step="create local report", needs_user_approval=False, confidence=0.70, notes=["local artifact"])
        if _contains_any(lower, ["news", "brief", "新闻", "简报"]):
            return BrainPlan(goal=text, intent="make_news", next_step="create local news brief", needs_user_approval=False, confidence=0.65, notes=["template only"])
        if _contains_any(lower, ["storyboard", "video", "视频", "脚本", "分镜"]):
            return BrainPlan(goal=text, intent="make_storyboard", next_step="create local storyboard", needs_user_approval=False, confidence=0.65, notes=["template only"])
        return BrainPlan(goal=text, intent="local_task", next_step="record local task", needs_user_approval=False, confidence=0.45, notes=["fallback"])


def _contains_any(text: str, candidates: list[str]) -> bool:
    return any(candidate in text for candidate in candidates)
