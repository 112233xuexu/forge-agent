from forge_agent.memory_models import MemoryItem
from forge_agent.memory_recall import normalize_filter, recall_memories, score_item, tokens_for


def make_memory(
    content: str,
    *,
    memory_id: str,
    scope: str = "project",
    wing: str = "project",
    room: str = "general",
    safety: str = "normal",
    confidence: float = 1.0,
) -> MemoryItem:
    return MemoryItem(
        id=memory_id,
        scope=scope,
        wing=wing,
        room=room,
        closet="default",
        drawer="inbox",
        content=content,
        created_at="2026-01-01T00:00:00+00:00",
        safety=safety,
        confidence=confidence,
    )


def test_tokens_for_normalizes_words():
    assert tokens_for("Invoice approval, by-month!") == {"invoice", "approval", "by", "month"}


def test_normalize_filter_strips_empty_values():
    assert normalize_filter({" project ", "", "skills"}) == {"project", "skills"}
    assert normalize_filter(None) == set()


def test_score_item_uses_content_and_path_matches():
    item = make_memory("Invoice approval project rule", memory_id="mem_1", room="invoices")

    score, reasons = score_item(item, {"invoice", "approval", "invoices"})

    assert score == 5.0
    assert "content token match: approval, invoice" in reasons
    assert "palace path match: invoices" in reasons


def test_score_item_applies_confidence_adjustment():
    item = make_memory("Invoice approval", memory_id="mem_1", confidence=0.5)

    score, reasons = score_item(item, {"invoice", "approval"})

    assert score == 2.0
    assert "confidence adjusted: 0.5" in reasons


def test_recall_memories_excludes_sensitive_by_default():
    public = make_memory("Invoice public rule", memory_id="mem_public")
    sensitive = make_memory("Invoice secret rule", memory_id="mem_sensitive", safety="sensitive")

    matches = recall_memories([public, sensitive], "invoice secret", include_sensitive=False)

    assert [match.memory.id for match in matches] == [public.id]


def test_recall_memories_can_include_sensitive():
    public = make_memory("Invoice public rule", memory_id="mem_public")
    sensitive = make_memory("Invoice secret rule", memory_id="mem_sensitive", safety="sensitive")

    matches = recall_memories([public, sensitive], "invoice secret", include_sensitive=True)

    assert {match.memory.id for match in matches} == {public.id, sensitive.id}


def test_recall_memories_filters_scope_and_wing():
    project = make_memory("Invoice approval rule", memory_id="mem_project", scope="project", wing="project")
    skill = make_memory("Invoice approval rule", memory_id="mem_skill", scope="skill", wing="skills")
    operation = make_memory("Invoice approval rule", memory_id="mem_operation", scope="operation", wing="operations")

    scoped = recall_memories([project, skill, operation], "invoice approval", scopes={"skill"})
    winged = recall_memories([project, skill, operation], "invoice approval", wings={"operations"})

    assert [match.memory.id for match in scoped] == [skill.id]
    assert [match.memory.id for match in winged] == [operation.id]


def test_recall_memories_honors_limit_and_empty_query():
    first = make_memory("Invoice approval first", memory_id="mem_1")
    second = make_memory("Invoice approval second", memory_id="mem_2")

    limited = recall_memories([first, second], "invoice approval", limit=1)
    empty = recall_memories([first, second], "", limit=5)

    assert len(limited) == 1
    assert empty == []
