from forge_agent.ask_options import AskOptions
from forge_agent.ask_service import build_ask_plan
from forge_agent.memory import MemoryStore


def options(**overrides):
    base = {
        "wants_json": True,
        "memory_enabled": True,
        "memory_limit": 5,
        "include_sensitive_memory": False,
        "memory_scopes": set(),
        "memory_wings": set(),
        "goal_parts": [],
    }
    base.update(overrides)
    return AskOptions(**base)


def test_ask_plan_attaches_rc10_memory_context(tmp_path):
    store = MemoryStore(tmp_path)
    store.add(
        "Acme invoices should be grouped by month",
        scope="project",
        wing="project",
        room="customers",
        closet="acme",
        drawer="invoices",
    )

    plan = build_ask_plan("organize Acme invoices", workspace=str(tmp_path), options=options())

    assert plan.metadata["memory_used"]
    assert plan.metadata["memory_policy"]["engine"] == "rc10-memory-engine"
    assert plan.metadata["memory_verdict"]["used_memory"] is True
    assert plan.metadata["memory_engine"]["verdict"]["used_memory"] is True
    assert plan.metadata["context_focus_path"] == "project/customers/acme/invoices"
    assert plan.metadata["context_packs"][0]["focus_path"] == "project/customers/acme/invoices"
    assert plan.metadata["task_card"]["memory_used"] == [item["id"] for item in plan.metadata["memory_used"]]


def test_ask_plan_memory_disabled_preserves_empty_context_metadata(tmp_path):
    plan = build_ask_plan("organize Acme invoices", workspace=str(tmp_path), options=options(memory_enabled=False))

    assert plan.metadata["memory_used"] == []
    assert plan.metadata["memory_verdict"] == {"used_memory": False, "adopted": [], "rejected": [], "warnings": []}
    assert plan.metadata["context_packs"] == []
    assert plan.metadata["task_card"]["memory_used"] == []
