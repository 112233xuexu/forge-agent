from forge_agent.governance import GovernanceEngine, build_execution_ledger, replay_ledger
from forge_agent.models import StepExecution, TaskPlan
from forge_agent.palace_graph import PalaceGraph, PalaceNode
from forge_agent.session_state import StateStore
from forge_agent.skill_lifecycle import SkillDefinition, SkillLibrary


def test_state_store_roundtrips_palace_graph(tmp_path):
    store = StateStore(tmp_path / "state.db")
    graph = PalaceGraph()
    graph.add_node(PalaceNode("relationships/customers/acme", "Acme"))
    graph.add_node(PalaceNode("projects/renewal", "Renewal"))
    graph.add_edge("relationships/customers/acme", "projects/renewal")

    store.save_palace_graph(graph)
    restored = store.load_palace_graph()

    assert restored is not None
    assert restored.get_node("relationships/customers/acme").title == "Acme"
    assert restored.shortest_path("relationships/customers/acme", "projects/renewal") == ["relationships/customers/acme", "projects/renewal"]
    store.close()


def test_state_store_roundtrips_skill_library(tmp_path):
    store = StateStore(tmp_path / "state.db")
    library = SkillLibrary()
    skill = SkillDefinition.new(
        goal_key="summarize_notes",
        trigger_text="summarize notes",
        description="Summarize notes",
        steps=[StepExecution("summarize", "summarize_notes", {"notes": {"$var": "notes"}})],
        input_variables=["notes"],
    )
    library.add(skill)

    store.save_skill_library(library)
    restored = store.load_skill_library()

    assert restored.get(skill.skill_id) is not None
    assert restored.get(skill.skill_id).steps[0].tool_name == "summarize_notes"
    store.close()


def test_state_store_roundtrips_ledger_entries(tmp_path):
    store = StateStore(tmp_path / "state.db")
    plan = TaskPlan("summarize notes", [StepExecution("summarize", "summarize_notes", {})])
    verdict = GovernanceEngine().evaluate_plan(plan)
    entries = build_execution_ledger(plan=plan, verdict=verdict)

    store.append_ledger_entries(entries)
    restored = store.list_ledger_entries()

    assert [entry.event_type for entry in restored] == ["plan", "governance_verdict"]
    assert replay_ledger(restored).valid is True
    store.close()


def test_state_store_generic_documents_can_update_and_delete(tmp_path):
    store = StateStore(tmp_path / "state.db")

    store.upsert_document("config", "default", {"version": 1})
    store.upsert_document("config", "default", {"version": 2})

    assert store.get_document("config", "default") == {"version": 2}
    assert store.list_documents("config") == [{"version": 2}]
    store.delete_document("config", "default")
    assert store.get_document("config", "default") is None
    store.close()
