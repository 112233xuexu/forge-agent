from forge_agent.models import MemoryRecallHit
from forge_agent.palace_graph import PalaceGraph, PalaceNode, choose_palace_focus, graph_from_recall_hits, normalize_palace_path, recall_hits_for_path


def hit(key: str, path: str, score: float = 1.0) -> MemoryRecallHit:
    return MemoryRecallHit(
        layer="memory",
        scope="project",
        key=key,
        content=f"content about {key}",
        score=score,
        metadata={"path": path, "related_paths": ["relationships/customers/beta"] if "acme" in path else []},
    )


def test_palace_path_normalization_and_parent_nodes():
    graph = PalaceGraph()
    graph.add_node(PalaceNode("Relationships / Customers / Acme", "Acme", tags=["VIP", "customer"]))

    assert normalize_palace_path("Relationships / Customers / Acme") == "relationships/customers/acme"
    assert graph.get_node("relationships") is not None
    assert graph.get_node("relationships/customers") is not None
    assert graph.get_node("relationships/customers/acme").tags == ["customer", "vip"]


def test_palace_search_and_focus_choice():
    graph = PalaceGraph()
    graph.add_node(PalaceNode("relationships/customers/acme", "Acme Customer", summary="pricing renewal notes", tags=["renewal"]))
    graph.add_node(PalaceNode("projects/website", "Website", summary="landing page"))

    results = graph.search("acme renewal")

    assert results[0].node.path == "relationships/customers/acme"
    assert choose_palace_focus("acme renewal", graph=graph) == "relationships/customers/acme"
    assert choose_palace_focus("missing", graph=graph, fallback="Inbox / General") == "inbox/general"


def test_palace_neighbors_shortest_path_and_json_roundtrip():
    graph = PalaceGraph()
    graph.add_node(PalaceNode("relationships/customers/acme", "Acme"))
    graph.add_node(PalaceNode("projects/renewal", "Renewal"))
    graph.add_node(PalaceNode("archive/calls/acme", "Acme Calls"))
    graph.add_edge("relationships/customers/acme", "projects/renewal", relation="related")
    graph.add_edge("projects/renewal", "archive/calls/acme", relation="related")

    assert [node.path for node in graph.neighbors("projects/renewal")] == ["archive/calls/acme", "relationships/customers/acme"]
    assert graph.shortest_path("relationships/customers/acme", "archive/calls/acme") == [
        "relationships/customers/acme",
        "projects/renewal",
        "archive/calls/acme",
    ]
    restored = PalaceGraph.from_json(graph.to_json())
    assert restored.shortest_path("relationships/customers/acme", "archive/calls/acme")[-1] == "archive/calls/acme"


def test_graph_from_recall_hits_and_path_filtering():
    hits = [
        hit("acme", "relationships/customers/acme", 0.8),
        hit("acme-call", "relationships/customers/acme/calls", 1.0),
        hit("beta", "relationships/customers/beta", 0.9),
    ]

    graph = graph_from_recall_hits(hits)
    selected = recall_hits_for_path(hits, "relationships/customers/acme")

    assert graph.get_node("relationships/customers/acme") is not None
    assert graph.neighbors("relationships/customers/acme")[0].path == "relationships/customers/beta"
    assert [item.key for item in selected] == ["acme-call", "acme"]
