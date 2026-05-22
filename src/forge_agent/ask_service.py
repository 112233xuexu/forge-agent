from __future__ import annotations

from pathlib import Path
from typing import Any

from .ask_options import AskOptions
from .ask_task_card import build_task_card_for_plan
from .brain import BrainAdapter, BrainPlan
from .context_builder import build_context_for_query
from .memory import MemoryStore
from .memory_engine import run_memory_engine
from .memory_models import MemoryRecall
from .models import MemoryRecallHit


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
    task_card = build_task_card_for_plan(plan).to_dict()
    task_card["memory_used"] = [item["id"] for item in plan.metadata.get("memory_used", []) if isinstance(item, dict) and item.get("id")]
    plan.metadata["task_card"] = task_card
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
    """Attach bounded memory and RC10 context metadata to a plan.

    The public ask behavior remains preview-only: memory can inform metadata, but
    it does not execute actions, approve actions, or bypass dry-run/rollback
    behavior.
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
        "engine": "rc10-memory-engine",
    }
    if not enabled or normalized_limit == 0:
        plan.metadata["memory_used"] = []
        plan.metadata["memory_verdict"] = {"used_memory": False, "adopted": [], "rejected": [], "warnings": []}
        plan.metadata["context_packs"] = []
        return

    store = MemoryStore(Path(workspace))
    matches = store.recall(
        plan.goal,
        limit=normalized_limit,
        include_sensitive=effective_include_sensitive,
        scopes=set(normalized_scopes),
        wings=set(normalized_wings),
    )
    rc10_hits = [_recall_to_hit(match) for match in matches]
    engine_result = run_memory_engine(
        plan.goal,
        rc10_hits,
        preferred_scopes=tuple(normalized_scopes),
        preferred_layers=tuple(normalized_wings),
        max_adopted=normalized_limit,
    )
    adopted_hits = engine_result.verdict.adopted
    context_result = build_context_for_query(plan.goal, adopted_hits or rc10_hits, fallback_path=_fallback_focus_path(matches), limit=normalized_limit)

    plan.metadata["memory_used"] = [_legacy_memory_summary(match) for match in matches]
    plan.metadata["memory_engine"] = engine_result.to_metadata()
    plan.metadata["memory_verdict"] = engine_result.verdict.to_metadata()
    plan.metadata["context_packs"] = [pack.to_dict() for pack in context_result.packs]
    plan.metadata["context_focus_path"] = context_result.focus_path


def _legacy_memory_summary(match: MemoryRecall) -> dict[str, Any]:
    memory = match.memory
    return {
        "id": memory.id,
        "scope": memory.scope,
        "wing": memory.wing,
        "room": memory.room,
        "safety": memory.safety,
        "score": match.score,
        "reasons": match.reasons,
    }


def _recall_to_hit(match: MemoryRecall) -> MemoryRecallHit:
    memory = match.memory
    path = _memory_palace_path(memory)
    metadata = dict(memory.metadata or {})
    metadata.update(
        {
            "path": path,
            "palace_path": path,
            "memory_id": memory.id,
            "wing": memory.wing,
            "room": memory.room,
            "closet": memory.closet,
            "drawer": memory.drawer,
            "safety": memory.safety,
            "created_at": memory.created_at,
            "last_used_at": memory.last_used_at,
        }
    )
    return MemoryRecallHit(
        layer=memory.wing,
        scope=memory.scope,
        key=memory.id,
        content=memory.content,
        score=match.score,
        reason="; ".join(match.reasons),
        source_id=memory.id,
        metadata=metadata,
    )


def _memory_palace_path(memory: Any) -> str:
    return "/".join(
        part.strip().replace(" ", "-").lower()
        for part in [memory.wing, memory.room, memory.closet, memory.drawer]
        if str(part).strip()
    )


def _fallback_focus_path(matches: list[MemoryRecall]) -> str:
    if not matches:
        return ""
    return _memory_palace_path(matches[0].memory)
