from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Iterable

from .models import MemoryRecallHit
from .palace_graph import PalaceGraph, choose_palace_focus, graph_from_recall_hits, normalize_palace_path, recall_hits_for_path


@dataclass(slots=True)
class ContextPack:
    focus_path: str
    title: str
    summary: str
    recall_hits: list[MemoryRecallHit] = field(default_factory=list)
    related_paths: list[str] = field(default_factory=list)
    breadcrumbs: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "focus_path": self.focus_path,
            "title": self.title,
            "summary": self.summary,
            "recall_hits": [hit.to_dict() for hit in self.recall_hits],
            "related_paths": list(self.related_paths),
            "breadcrumbs": list(self.breadcrumbs),
            "metadata": dict(self.metadata),
        }


@dataclass(slots=True)
class ContextBuildResult:
    query: str
    focus_path: str
    packs: list[ContextPack]
    graph: PalaceGraph

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "focus_path": self.focus_path,
            "packs": [pack.to_dict() for pack in self.packs],
            "graph": self.graph.to_dict(),
        }


def build_context_pack(
    *,
    focus_path: str,
    hits: Iterable[MemoryRecallHit],
    graph: PalaceGraph | None = None,
    include_descendants: bool = True,
    limit: int = 5,
) -> ContextPack:
    normalized = normalize_palace_path(focus_path)
    graph = graph or graph_from_recall_hits(hits)
    selected = recall_hits_for_path(hits, normalized, include_descendants=include_descendants)[: max(0, limit)]
    node = graph.get_node(normalized)
    title = node.title if node else normalized.rsplit("/", 1)[-1].replace("-", " ").title()
    summary = node.summary if node else ""
    neighbors = [node.path for node in graph.neighbors(normalized)]
    breadcrumbs = [ancestor.path for ancestor in graph.ancestors(normalized)] + ([normalized] if normalized else [])
    return ContextPack(
        focus_path=normalized,
        title=title,
        summary=summary,
        recall_hits=selected,
        related_paths=neighbors,
        breadcrumbs=breadcrumbs,
        metadata={"include_descendants": include_descendants, "hit_count": len(selected)},
    )


def build_context_for_query(
    query: str,
    hits: Iterable[MemoryRecallHit],
    *,
    fallback_path: str = "",
    limit: int = 5,
) -> ContextBuildResult:
    hit_list = list(hits)
    graph = graph_from_recall_hits(hit_list)
    focus_path = choose_palace_focus(query, graph=graph, fallback=fallback_path)
    packs = [build_context_pack(focus_path=focus_path, hits=hit_list, graph=graph, limit=limit)] if focus_path else []
    return ContextBuildResult(query=query, focus_path=focus_path, packs=packs, graph=graph)


def merge_context_packs(packs: Iterable[ContextPack], *, limit: int = 10) -> ContextPack:
    pack_list = list(packs)
    if not pack_list:
        return ContextPack(focus_path="", title="", summary="")
    primary = pack_list[0]
    hits: list[MemoryRecallHit] = []
    seen_sources: set[str] = set()
    related: list[str] = []
    breadcrumbs: list[str] = []
    for pack in pack_list:
        for hit in pack.recall_hits:
            key = hit.source_id or f"{hit.scope}:{hit.layer}:{hit.key}"
            if key in seen_sources:
                continue
            seen_sources.add(key)
            hits.append(hit)
        for path in pack.related_paths:
            if path not in related:
                related.append(path)
        for path in pack.breadcrumbs:
            if path not in breadcrumbs:
                breadcrumbs.append(path)
    hits.sort(key=lambda item: item.score, reverse=True)
    return ContextPack(
        focus_path=primary.focus_path,
        title=primary.title,
        summary=primary.summary,
        recall_hits=hits[: max(0, limit)],
        related_paths=related,
        breadcrumbs=breadcrumbs,
        metadata={"merged_pack_count": len(pack_list), "hit_count": min(len(hits), max(0, limit))},
    )
