from __future__ import annotations

from pathlib import Path

from .ask_options import AskOptions
from .ask_task_card import build_task_card_for_plan
from .brain import BrainAdapter, BrainPlan
from .memory import MemoryStore


def build_ask_plan(goal: str, *, workspace: str, options: AskOptions) -> BrainPlan:
    plan = BrainAdapter().plan(goal)
    attach_memory_recall(
        plan,
        workspace=workspace,
        enabled=options.memory_enabled,
        limit=options.memory_limit,
        include_sensitive=options.include_sensitive_memory,
        scopes=options.memory_scopes,
        wings=options.memory_wings,
    )
    plan.metadata["task_card"] = build_task_card_for_plan(plan).to_dict()
    return plan


def attach_memory_recall(
    plan: BrainPlan,
    *,
    workspace: str,
    enabled: bool = True,
    limit: int = 5,
    include_sensitive: bool = False,
    scopes: set[str] | None = None,
    wings: set[str] | None = None,
) -> None:
    """Attach bounded memory recall metadata to a plan.

    Memory can inform planning metadata, but it does not execute actions,
    approve actions, or bypass dry-run/rollback behavior.
    """

    normalized_limit = max(0, limit)
    normalized_scopes = sorted(scopes or set())
    normalized_wings = sorted(wings or set())
    effective_include_sensitive = bool(include_sensitive and enabled and normalized_limit > 0)
    plan.metadata["memory_policy"] = {
        "enabled": enabled,
        "bounded": True,
        "limit": normalized_limit,
        "include_sensitive": effective_include_sensitive,
        "scope_filter": normalized_scopes,
        "wing_filter": normalized_wings,
        "sensitive_requires_explicit_recall": True,
    }
    if not enabled or normalized_limit == 0:
        plan.metadata["memory_used"] = []
        return
    store = MemoryStore(Path(workspace))
    matches = store.recall(
        plan.goal,
        limit=normalized_limit,
        include_sensitive=effective_include_sensitive,
        scopes=set(normalized_scopes),
        wings=set(normalized_wings),
    )
    plan.metadata["memory_used"] = [
        {
            "id": match.memory.id,
            "scope": match.memory.scope,
            "wing": match.memory.wing,
            "room": match.memory.room,
            "safety": match.memory.safety,
            "score": match.score,
            "reasons": match.reasons,
        }
        for match in matches
    ]
