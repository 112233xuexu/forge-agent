from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from .models import StepExecution, TaskPlan
from .normalization import tokenize
from .tool_registry import ToolRegistry


@dataclass(slots=True)
class PlannerResult:
    plan: TaskPlan | None
    missing_inputs: list[str]
    reason: str


class SimplePlanner:
    """Small RC10 planner subset for ordinary text tasks.

    The full archive planner also covers workspace workflows. This migrated
    subset keeps the stable one-shot task planning surface that can be tested
    before gateway/runtime wiring.
    """

    def __init__(self, tools: ToolRegistry) -> None:
        self.tools = tools

    def build_plan(self, task_text: str, inputs: dict[str, Any] | None = None) -> PlannerResult:
        provided = self._infer_common_inputs(task_text, dict(inputs or {}))
        lowered = task_text.lower()
        tokens = set(tokenize(task_text))

        if self._looks_like_followup(tokens, lowered) and self.tools.has("summarize_notes") and self.tools.has("draft_followup"):
            needs = ["notes", "customer"]
            intent = "followup_notes"
            steps = [
                StepExecution("extract actions", "summarize_notes", {"notes": {"$var": "notes"}}),
                StepExecution(
                    "draft reply",
                    "draft_followup",
                    {
                        "customer": {"$var": "customer"},
                        "action_items": {"$ref": {"step": "extract actions", "path": ["action_items"]}},
                    },
                ),
            ]
            if self._looks_like_translation(tokens, lowered) and self.tools.has("translate_text"):
                needs.append("target_language")
                intent = "followup_translate"
                steps.append(
                    StepExecution(
                        "translate follow-up",
                        "translate_text",
                        {
                            "text": {"$ref": {"step": "draft reply", "path": []}},
                            "target_language": {"$var": "target_language"},
                        },
                    )
                )
            missing = self._missing(needs, provided)
            if missing:
                return PlannerResult(None, missing, "missing_inputs")
            return PlannerResult(
                TaskPlan(
                    objective="summarize notes and draft follow-up",
                    steps=steps,
                    meta={"planner": "simple", "intent": intent, "input_names": needs},
                ),
                [],
                f"planned_{intent}",
            )

        if self._looks_like_notes_summary(tokens, lowered) and self.tools.has("summarize_notes"):
            needs = ["notes"]
            intent = "summarize_notes"
            objective = "summarize notes"
            steps = [StepExecution("summarize notes", "summarize_notes", {"notes": {"$var": "notes"}})]
            if self._looks_like_translation(tokens, lowered) and self.tools.has("translate_text"):
                needs.append("target_language")
                intent = "summarize_translate"
                objective = "summarize and translate notes"
                steps.append(
                    StepExecution(
                        "translate summary",
                        "translate_text",
                        {
                            "text": {"$ref": {"step": "summarize notes", "path": ["summary"]}},
                            "target_language": {"$var": "target_language"},
                        },
                    )
                )
            missing = self._missing(needs, provided)
            if missing:
                return PlannerResult(None, missing, "missing_inputs")
            return PlannerResult(TaskPlan(objective, steps, {"planner": "simple", "intent": intent, "input_names": needs}), [], f"planned_{intent}")

        if self._looks_like_action_extraction(tokens, lowered) and self.tools.has("summarize_notes"):
            missing = self._missing(["notes"], provided)
            if missing:
                return PlannerResult(None, missing, "missing_inputs")
            return PlannerResult(
                TaskPlan(
                    "extract action items",
                    [StepExecution("extract actions", "summarize_notes", {"notes": {"$var": "notes"}})],
                    {"planner": "simple", "intent": "extract_actions", "input_names": ["notes"]},
                ),
                [],
                "planned_extract_actions",
            )

        if self._looks_like_translation(tokens, lowered) and self.tools.has("translate_text"):
            missing = self._missing(["text", "target_language"], provided)
            if missing:
                return PlannerResult(None, missing, "missing_inputs")
            return PlannerResult(
                TaskPlan(
                    "translate text",
                    [
                        StepExecution(
                            "translate text",
                            "translate_text",
                            {"text": {"$var": "text"}, "target_language": {"$var": "target_language"}},
                        )
                    ],
                    {"planner": "simple", "intent": "translate_text", "input_names": ["text", "target_language"]},
                ),
                [],
                "planned_translate_text",
            )

        if self._looks_like_paraphrase(tokens, lowered) and self.tools.has("paraphrase_text"):
            missing = self._missing(["text"], provided)
            if missing:
                return PlannerResult(None, missing, "missing_inputs")
            return PlannerResult(
                TaskPlan(
                    "paraphrase text",
                    [StepExecution("paraphrase text", "paraphrase_text", {"text": {"$var": "text"}, "style": {"$var": "style"}})],
                    {"planner": "simple", "intent": "paraphrase_text", "input_names": ["text", "style"]},
                ),
                [],
                "planned_paraphrase_text",
            )

        return PlannerResult(None, [], "no_plan")

    def _infer_common_inputs(self, task_text: str, provided: dict[str, Any]) -> dict[str, Any]:
        customer_match = re.search(r"\bfor\s+([A-Z][A-Za-z0-9_-]+)", task_text)
        if customer_match and "customer" not in provided:
            provided["customer"] = customer_match.group(1)
        notes_match = re.search(r"(?:notes|bullets|transcript)\s*[:=-]\s*(.+)$", task_text, flags=re.IGNORECASE)
        if notes_match and "notes" not in provided:
            provided["notes"] = notes_match.group(1).strip()
        quoted_match = re.search(r"['\"]([^'\"]+)['\"]", task_text)
        lowered = task_text.lower()
        if quoted_match and "text" not in provided and (self._looks_like_translation(set(tokenize(task_text)), lowered) or self._looks_like_paraphrase(set(tokenize(task_text)), lowered)):
            provided["text"] = quoted_match.group(1).strip()
        text_match = re.search(r"text\s*[:=-]\s*(.+?)(?:\s+(?:into|to)\s+[A-Za-z]+)?$", task_text, flags=re.IGNORECASE)
        if text_match and "text" not in provided:
            provided["text"] = text_match.group(1).strip()
        if "target_language" not in provided:
            language = self._infer_language(task_text)
            if language:
                provided["target_language"] = language
        provided.setdefault("style", self._infer_style(task_text))
        return provided

    def _infer_language(self, task_text: str) -> str:
        matches = re.findall(r"\b(?:into|to)\s+([A-Za-z]+)\b", task_text, flags=re.IGNORECASE)
        for candidate in reversed(matches):
            lowered = candidate.lower()
            if lowered not in {"a", "an", "the"}:
                return lowered
        return ""

    def _infer_style(self, task_text: str) -> str:
        lowered = task_text.lower()
        if any(term in lowered for term in ("warm", "warmer", "friendly", "friendlier")):
            return "warm"
        if any(term in lowered for term in ("short", "shorter", "concise", "brief")):
            return "concise"
        if any(term in lowered for term in ("professional", "formal")):
            return "professional"
        return "clear"

    def _looks_like_followup(self, tokens: set[str], lowered: str) -> bool:
        return (
            "follow-up" in lowered
            or ("notes" in tokens and "followup" in tokens)
            or ("actions" in tokens and "followup" in tokens)
            or ("followup" in tokens and "customer" in tokens)
        )

    def _looks_like_action_extraction(self, tokens: set[str], lowered: str) -> bool:
        return "follow-up" not in lowered and (("actions" in tokens and "notes" in tokens) or ("extract" in tokens and "actions" in tokens) or ("todo" in lowered and "notes" in lowered))

    def _looks_like_notes_summary(self, tokens: set[str], lowered: str) -> bool:
        return not self._looks_like_followup(tokens, lowered) and not self._looks_like_action_extraction(tokens, lowered) and (("summarize" in tokens and "notes" in tokens) or ("recap" in lowered and "notes" in lowered))

    def _looks_like_translation(self, tokens: set[str], lowered: str) -> bool:
        return "translate" in tokens or lowered.startswith("translate ") or bool(re.search(r"\b(?:into|to)\s+(spanish|french|german|japanese|english)\b", lowered))

    def _looks_like_paraphrase(self, tokens: set[str], lowered: str) -> bool:
        return "paraphrase" in tokens or "rewrite" in lowered or "reword" in lowered or "polish" in lowered

    def _missing(self, names: list[str], values: dict[str, Any]) -> list[str]:
        missing: list[str] = []
        for name in names:
            if name not in values or values.get(name) in ("", None):
                missing.append(name)
        return missing
