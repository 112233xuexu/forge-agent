from forge_agent.context_builder import build_context_for_query, build_context_pack, merge_context_packs
from forge_agent.models import MemoryRecallHit
from forge_agent.palace_graph import graph_from_recall_hits


def hit(key: str, path: str, score: float = 1.0) -> MemoryRecallHit:
    return MemoryRecallHit(
        layer="memory",
        scope="project",
        key=key,
        content=f"content for {key}",
        score=score,
        source_id=key,
        metadata={"path": path, "related_paths": ["relationships/customers/beta"] if key == "acme" else []},
    )


def test_build_context_for_query_selects_focus_and_hits():
    hits = [
        hit("acme", "relationships/customers/acme", 0.7),
        hit("acme-call", "relationships/customers/acme/calls", 1.0),
        hit("website", "projects/website", 0.9),
    ]

    result = build_context_for_query("acme customer", hits)

    assert result.focus_path == "relationships/customers/acme"
    assert result.packs[0].breadcrumbs == ["relationships", "relationships/customers", "relationships/customers/acme"]
    assert [item.key for item in result.packs[0].recall_hits] == ["acme-call", "acme"]


def test_build_context_pack_includes_related_paths():
    hits = [hit("acme", "relationships/customers/acme"), hit("beta", "relationships/customers/beta")]
    graph = graph_from_recall_hits(hits)

    pack = build_context_pack(focus_path="relationships/customers/acme", hits=hits, graph=graph)

    assert pack.focus_path == "relationships/customers/acme"
    assert pack.related_paths == ["relationships/customers/beta"]
    assert pack.metadata["hit_count"] == 1


def test_merge_context_packs_deduplicates_hits_and_paths():
    hits = [hit("acme", "relationships/customers/acme", 0.7), hit("acme-call", "relationships/customers/acme/calls", 1.0)]
    graph = graph_from_recall_hits(hits)
    pack1 = build_context_pack(focus_path="relationships/customers/acme", hits=hits, graph=graph)
    pack2 = build_context_pack(focus_path="relationships/customers/acme/calls", hits=hits, graph=graph)

    merged = merge_context_packs([pack1, pack2])

    assert merged.focus_path == "relationships/customers/acme"
    assert [item.key for item in merged.recall_hits] == ["acme-call", "acme"]
    assert "relationships/customers/acme/calls" in merged.breadcrumbs
    assert merged.metadata["merged_pack_count"] == 2
