from __future__ import annotations

from collections import deque
from dataclasses import asdict, dataclass, field
from typing import Any, Iterable
import json
import re

from .models import MemoryRecallHit, utc_now


_TOKEN_RE = re.compile(r"[a-z0-9]+", re.IGNORECASE)


@dataclass(slots=True)
class PalaceNode:
    path: str
    title: str
    kind: str = "topic"
    summary: str = ""
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "PalaceNode":
        data = dict(payload or {})
        return cls(
            path=normalize_palace_path(str(data["path"])),
            title=str(data.get("title") or data["path"]),
            kind=str(data.get("kind", "topic") or "topic"),
            summary=str(data.get("summary", "") or ""),
            tags=sorted({str(tag).strip().lower() for tag in data.get("tags", []) if str(tag).strip()}),
            metadata=dict(data.get("metadata", {}) or {}),
            created_at=str(data.get("created_at", utc_now())),
            updated_at=str(data.get("updated_at", utc_now())),
        )


@dataclass(slots=True)
class PalaceEdge:
    source: str
    target: str
    relation: str = "related"
    weight: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "PalaceEdge":
        data = dict(payload or {})
        return cls(
            source=normalize_palace_path(str(data["source"])),
            target=normalize_palace_path(str(data["target"])),
            relation=str(data.get("relation", "related") or "related"),
            weight=float(data.get("weight", 1.0) or 1.0),
            metadata=dict(data.get("metadata", {}) or {}),
            created_at=str(data.get("created_at", utc_now())),
        )


@dataclass(slots=True)
class PalaceSearchResult:
    node: PalaceNode
    score: float
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {"node": self.node.to_dict(), "score": self.score, "reason": self.reason}


class PalaceGraph:
    """Small in-memory palace/context graph compatibility layer."""

    def __init__(self) -> None:
        self.nodes: dict[str, PalaceNode] = {}
        self.edges: list[PalaceEdge] = []

    def add_node(self, node: PalaceNode) -> PalaceNode:
        node.path = normalize_palace_path(node.path)
        node.tags = sorted({str(tag).strip().lower() for tag in node.tags if str(tag).strip()})
        self.nodes[node.path] = node
        self._ensure_parent_nodes(node.path)
        return node

    def get_node(self, path: str) -> PalaceNode | None:
        return self.nodes.get(normalize_palace_path(path))

    def add_edge(self, source: str, target: str, relation: str = "related", *, weight: float = 1.0, metadata: dict[str, Any] | None = None) -> PalaceEdge:
        source_path = normalize_palace_path(source)
        target_path = normalize_palace_path(target)
        if source_path not in self.nodes:
            self.add_node(PalaceNode(source_path, title=_title_from_path(source_path), kind="folder"))
        if target_path not in self.nodes:
            self.add_node(PalaceNode(target_path, title=_title_from_path(target_path), kind="folder"))
        edge = PalaceEdge(source_path, target_path, relation=relation, weight=weight, metadata=dict(metadata or {}))
        self.edges.append(edge)
        return edge

    def neighbors(self, path: str, *, relation: str | None = None) -> list[PalaceNode]:
        normalized = normalize_palace_path(path)
        paths: list[str] = []
        for edge in self.edges:
            if relation is not None and edge.relation != relation:
                continue
            if edge.source == normalized:
                paths.append(edge.target)
            elif edge.target == normalized:
                paths.append(edge.source)
        return [self.nodes[item] for item in sorted(set(paths)) if item in self.nodes]

    def ancestors(self, path: str) -> list[PalaceNode]:
        parts = normalize_palace_path(path).split("/")
        paths = ["/".join(parts[:index]) for index in range(1, len(parts))]
        return [self.nodes[item] for item in paths if item in self.nodes]

    def descendants(self, path: str) -> list[PalaceNode]:
        prefix = normalize_palace_path(path).rstrip("/") + "/"
        return [self.nodes[key] for key in sorted(self.nodes) if key.startswith(prefix)]

    def shortest_path(self, source: str, target: str) -> list[str]:
        source_path = normalize_palace_path(source)
        target_path = normalize_palace_path(target)
        if source_path not in self.nodes or target_path not in self.nodes:
            return []
        queue: deque[tuple[str, list[str]]] = deque([(source_path, [source_path])])
        seen = {source_path}
        while queue:
            current, path = queue.popleft()
            if current == target_path:
                return path
            for neighbor in self.neighbors(current):
                if neighbor.path in seen:
                    continue
                seen.add(neighbor.path)
                queue.append((neighbor.path, path + [neighbor.path]))
        return []

    def search(self, query: str, *, limit: int = 5) -> list[PalaceSearchResult]:
        query_tokens = _tokens(query)
        results: list[PalaceSearchResult] = []
        for node in self.nodes.values():
            candidate_tokens = _tokens(" ".join([node.path, node.title, node.summary, " ".join(node.tags)]))
            if not query_tokens or not candidate_tokens:
                continue
            overlap = query_tokens & candidate_tokens
            if not overlap:
                continue
            score = len(overlap) / max(1, len(query_tokens | candidate_tokens))
            if node.path in query.lower():
                score += 1.0
            depth_bonus = min(node.path.count("/"), 8) * 0.01
            results.append(PalaceSearchResult(node=node, score=round(score + depth_bonus, 4), reason="token overlap"))
        results.sort(key=lambda item: (item.score, item.node.updated_at, item.node.path), reverse=True)
        return results[: max(0, limit)]

    def to_dict(self) -> dict[str, Any]:
        return {"nodes": [self.nodes[key].to_dict() for key in sorted(self.nodes)], "edges": [edge.to_dict() for edge in self.edges]}

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "PalaceGraph":
        graph = cls()
        for node in payload.get("nodes", []) or []:
            graph.add_node(PalaceNode.from_dict(node))
        for edge in payload.get("edges", []) or []:
            parsed = PalaceEdge.from_dict(edge)
            graph.add_edge(parsed.source, parsed.target, parsed.relation, weight=parsed.weight, metadata=parsed.metadata)
        return graph

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True)

    @classmethod
    def from_json(cls, content: str) -> "PalaceGraph":
        return cls.from_dict(json.loads(content))

    def _ensure_parent_nodes(self, path: str) -> None:
        parts = path.split("/")
        for index in range(1, len(parts)):
            parent = "/".join(parts[:index])
            if parent not in self.nodes:
                self.nodes[parent] = PalaceNode(parent, title=_title_from_path(parent), kind="folder")


def normalize_palace_path(path: str) -> str:
    raw = str(path or "").strip().replace("\\", "/")
    raw = re.sub(r"/+", "/", raw).strip("/")
    parts = [part.strip().lower().replace(" ", "-") for part in raw.split("/") if part.strip()]
    return "/".join(parts)


def graph_from_recall_hits(hits: Iterable[MemoryRecallHit]) -> PalaceGraph:
    graph = PalaceGraph()
    for hit in hits:
        metadata = dict(hit.metadata or {})
        path = normalize_palace_path(str(metadata.get("path") or metadata.get("palace_path") or ""))
        if not path:
            continue
        title = str(metadata.get("title") or hit.key or _title_from_path(path))
        graph.add_node(PalaceNode(path=path, title=title, kind=str(metadata.get("kind", hit.layer or "memory")), summary=hit.content, tags=[hit.scope, hit.layer]))
        for related in metadata.get("related_paths", []) or []:
            graph.add_edge(path, str(related), relation="related")
    return graph


def recall_hits_for_path(hits: Iterable[MemoryRecallHit], path: str, *, include_descendants: bool = True) -> list[MemoryRecallHit]:
    normalized = normalize_palace_path(path)
    selected: list[MemoryRecallHit] = []
    for hit in hits:
        metadata = dict(hit.metadata or {})
        hit_path = normalize_palace_path(str(metadata.get("path") or metadata.get("palace_path") or ""))
        if hit_path == normalized or (include_descendants and hit_path.startswith(normalized.rstrip("/") + "/")):
            selected.append(hit)
    selected.sort(key=lambda item: item.score, reverse=True)
    return selected


def choose_palace_focus(query: str, *, graph: PalaceGraph, fallback: str = "") -> str:
    results = graph.search(query, limit=1)
    if results:
        return results[0].node.path
    return normalize_palace_path(fallback)


def _tokens(text: str) -> set[str]:
    return {token.lower() for token in _TOKEN_RE.findall(str(text or "")) if token.strip()}


def _title_from_path(path: str) -> str:
    return normalize_palace_path(path).rsplit("/", 1)[-1].replace("-", " ").title()
