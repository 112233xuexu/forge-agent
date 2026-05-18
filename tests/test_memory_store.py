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


def test_memory_store_quarantine_restore_and_export(tmp_path):
    store = MemoryStore(tmp_path / "workspace")
    item = store.add("Sensitive project rule", safety="sensitive")

    quarantined = store.quarantine(item.id)
    assert quarantined.status == "quarantined"
    assert store.list() == []

    restored = store.restore(item.id)
    assert restored.status == "active"
    assert [memory.id for memory in store.list()] == [item.id]

    bundle = store.export_bundle()
    assert bundle["version"] == 1
    assert bundle["doctor"]["sensitive"] == 1
    assert bundle["memories"][0]["id"] == item.id
    assert bundle["memories"][0]["safety"] == "sensitive"
    audit_actions = [row["action"] for row in store.audit()]
    assert "quarantine" in audit_actions
    assert "restore" in audit_actions
    assert "export" in audit_actions


def test_memory_store_recall_scores_reasons_and_last_used(tmp_path):
    store = MemoryStore(tmp_path / "workspace")
    invoice = store.add(
        "Invoices should be organized by month after approval",
        scope="project",
        room="files",
        closet="invoices",
        drawer="rules",
    )
    storyboard = store.add(
        "Storyboards use a 30-second structure",
        scope="skill",
        wing="skills",
        room="storyboard",
    )

    matches = store.recall("organize invoices by month", limit=2)

    assert [match.memory.id for match in matches] == [invoice.id]
    assert matches[0].score > 0
    assert any("content token match" in reason for reason in matches[0].reasons)
    assert store.show(invoice.id).last_used_at is not None
    assert store.show(storyboard.id).last_used_at is None
    assert "recall" in [row["action"] for row in store.audit()]


def test_memory_store_recall_is_bounded_and_excludes_sensitive_by_default(tmp_path):
    store = MemoryStore(tmp_path / "workspace")
    public = store.add("Use approval before organizing private files")
    sensitive = store.add("Sensitive approval secret", safety="sensitive")

    default_matches = store.recall("approval secret organizing", limit=5)
    assert [match.memory.id for match in default_matches] == [public.id]

    sensitive_matches = store.recall("approval secret organizing", limit=5, include_sensitive=True)
    assert {match.memory.id for match in sensitive_matches} == {public.id, sensitive.id}

    limited_matches = store.recall("approval secret organizing", limit=1, include_sensitive=True)
    assert len(limited_matches) == 1


def test_memory_store_recall_scope_and_wing_filters(tmp_path):
    store = MemoryStore(tmp_path / "workspace")
    project = store.add("Invoice approval project rule", scope="project", wing="project", room="invoices")
    skill = store.add("Invoice approval skill rule", scope="skill", wing="skills", room="invoices")
    operation = store.add("Invoice approval operation rule", scope="operation", wing="operations", room="invoices")

    project_matches = store.recall("invoice approval", scopes={"project"})
    assert [match.memory.id for match in project_matches] == [project.id]

    skill_wing_matches = store.recall("invoice approval", wings={"skills"})
    assert [match.memory.id for match in skill_wing_matches] == [skill.id]

    combined_matches = store.recall("invoice approval", scopes={"skill", "operation"}, wings={"operations"})
    assert [match.memory.id for match in combined_matches] == [operation.id]

    assert store.show(project.id).last_used_at is not None
    assert store.show(skill.id).last_used_at is not None
    assert store.show(operation.id).last_used_at is not None
    recall_audit = [row for row in store.audit() if row["action"] == "recall"][-1]
    assert recall_audit["metadata"]["scopes"] == ["operation", "skill"]
    assert recall_audit["metadata"]["wings"] == ["operations"]


def test_memory_store_doctor_initializes_palace(tmp_path):
    store = MemoryStore(tmp_path / "workspace")

    status = store.doctor()

    assert status["ok"] is True
    assert status["total"] == 0
    assert status["active"] == 0
    assert status["sensitive"] == 0
    assert "project" in status["wings"]
    palace = store.palace()
    assert palace["version"] == 1
    assert "wing" in palace["hierarchy"]
    assert palace["policy"]["restore_requires_explicit_command"] is True
    assert palace["policy"]["sensitive_recall_requires_explicit_flag"] is True
    assert palace["policy"]["scoped_recall_supported"] is True
