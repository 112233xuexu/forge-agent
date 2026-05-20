from __future__ import annotations

from forge_agent.brain import BrainPlan
from forge_agent.task_card import TaskCard, TaskCardImpact, make_preview_card


def build_task_card_for_plan(plan: BrainPlan) -> TaskCard:
    if plan.intent == "organize_files":
        return make_preview_card(
            title="Organize your files",
            user_request=plan.goal,
            plan=[
                "Look at the selected folder",
                "Group invoice or receipt files by month",
                "Show the file move plan before changing files",
            ],
            impacts=[TaskCardImpact(summary="File locations may change after you approve the plan", level="medium", reversible=True)],
            boundaries=["I will not change file contents", "I will not upload files"],
            needs_confirmation=False,
        )
    if plan.intent == "make_ppt":
        return make_preview_card(
            title="Create a slide outline",
            user_request=plan.goal,
            plan=["Create a local slide outline", "Keep it in your Forge workspace", "Show you the saved artifact path"],
            impacts=[TaskCardImpact(summary="A local artifact file will be created", level="low", reversible=True)],
            boundaries=["I will not send or publish the slides"],
            needs_confirmation=False,
        )
    if plan.intent == "make_report":
        return make_preview_card(
            title="Create a report draft",
            user_request=plan.goal,
            plan=["Create a local report draft", "Use a simple report structure", "Show you the saved artifact path"],
            impacts=[TaskCardImpact(summary="A local artifact file will be created", level="low", reversible=True)],
            boundaries=["I will not send the report anywhere"],
            needs_confirmation=False,
        )
    if plan.intent == "make_news":
        return make_preview_card(
            title="Create a news brief template",
            user_request=plan.goal,
            plan=["Create a local brief template", "Use your topic as the brief focus", "Show you the saved artifact path"],
            impacts=[TaskCardImpact(summary="A local artifact file will be created", level="low", reversible=True)],
            boundaries=["I will not fetch live news yet"],
            needs_confirmation=False,
        )
    if plan.intent == "make_storyboard":
        return make_preview_card(
            title="Create a storyboard draft",
            user_request=plan.goal,
            plan=["Create a local storyboard draft", "Break the idea into scenes", "Show you the saved artifact path"],
            impacts=[TaskCardImpact(summary="A local artifact file will be created", level="low", reversible=True)],
            boundaries=["I will not render a video yet"],
            needs_confirmation=False,
        )
    return make_preview_card(
        title="Prepare this task",
        user_request=plan.goal,
        plan=["Record the task locally", "Keep the request available for follow-up work"],
        impacts=[TaskCardImpact(summary="A local task record may be created", level="low", reversible=True)],
        boundaries=["I will not use outside apps without a clear next step"],
        needs_confirmation=False,
    )
