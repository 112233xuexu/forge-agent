from forge_agent.memory import MemoryStore


def test_memory_store_add_list_show_search_forget_and_audit(tmp_path):
    store = MemoryStore(tmp_path / "workspace")

    item = store.add(
        "Forge should keep memory visible and forgettable",
        scope="project",
        room="roadmap",
        closet="v2.5",
        drawer="memory-palace",
    )

    assert item.id.startswith("mem_")
    assert item.status == "active"
    assert store.root.exists()
    assert store.palace_path.exists()
    assert store.index_path.exists()
    assert store.audit_path.exists()
    assert (store.wings_path / "project").exists()

    listed = store.list()
    assert [memory.id for memory in listed] == [item.id]

    shown = store.show(item.id)
    assert shown.content == "Forge should keep memory visible and forgettable"

    matches = store.search("forgettable")
    assert [memory.id for memory in matches] == [item.id]

    forgotten = store.forget(item.id)
    assert forgotten.status == "forgotten"
    assert store.list() == []
    assert [memory.id for memory in store.list(include_inactive=True)] == [item.id]

    audit_actions = [row["action"] for row in store.audit()]
    assert "add" in audit_actions
    assert "search" in audit_actions
    assert "forget" in audit_actions


def test_memory_store_doctor_initializes_palace(tmp_path):
    store = MemoryStore(tmp_path / "workspace")

    status = store.doctor()

    assert status["ok"] is True
    assert status["total"] == 0
    assert status["active"] == 0
    assert "project" in status["wings"]
    palace = store.palace()
    assert palace["version"] == 1
    assert "wing" in palace["hierarchy"]
