from forge_agent.memory_continuity import build_memory_continuity, compare_memory_continuity
from forge_agent.memory_quarantine import apply_memory_quarantine, build_memory_quarantine_snapshot
from forge_agent.memory_recovery import build_memory_recovery_state, should_adopt_reanchor
from forge_agent.memory_soak import build_memory_soak_snapshot, update_memory_soak_window
from forge_agent.models import MemoryRecallHit


def hit(source_id, path, layer="archive", *, bucket="fresh"):
    return MemoryRecallHit(
        layer=layer,
        scope="session:s1",
        key=source_id,
        content=f"content for {source_id}",
        score=1.0,
        source_id=source_id,
        metadata={"path": path, "freshness_bucket": bucket, "resolution_slot": "customer-focus"},
    )


def test_memory_continuity_detects_focus_drift():
    previous = build_memory_continuity(
        {
            "palace_path": "relationships/customers/acme",
            "active_context": {
                "defaults": {"customer": "Acme"},
                "recall_hits": [{"layer": "core", "key": "customer", "content": "Acme"}],
            },
        }
    )
    current = build_memory_continuity(
        {
            "palace_path": "relationships/customers/beta",
            "active_context": {
                "defaults": {"customer": "Beta"},
                "recall_hits": [{"layer": "core", "key": "customer", "content": "Beta"}],
            },
        }
    )

    comparison = compare_memory_continuity(previous, current)

    assert comparison["status"] == "drifted"
    assert "focus_path" in comparison["changed_sections"]


def test_memory_soak_scores_drift_and_becomes_ready_after_stable_low_risk_runs():
    risky = build_memory_soak_snapshot(
        memory_engine={
            "profile": {"current_intent": True},
            "continuity_focus_path": "relationships/customers/beta",
            "top_bucket": "stale",
            "freshness": {"stale_top_hits": 2},
            "resolution": {"conflict_top_hits": 1},
        },
        recall_hits=[{"metadata": {"path": "relationships/customers/acme"}}],
    )
    assert risky["continuity_drift"] is True
    assert risky["risk_level"] == "high"

    low = build_memory_soak_snapshot(
        memory_engine={"profile": {"current_intent": True}, "continuity_focus_path": "relationships/customers/beta"},
        recall_hits=[{"metadata": {"path": "relationships/customers/beta"}}],
    )
    window = None
    for _ in range(3):
        window = update_memory_soak_window(window, low)
    assert window["soak_ready"] is True


def test_memory_recovery_adopts_valid_reanchor_candidate():
    state = build_memory_recovery_state(
        continuity_focus_path="relationships/customers/acme",
        current_focus_path="relationships/customers/beta",
        memory_soak={"risk_level": "medium", "continuity_drift": True},
    )

    assert state["mode"] == "guarded_reanchor"
    assert state["recommend_reanchor"] is True
    assert (
        should_adopt_reanchor(
            state,
            anchored_compare={"current_focus_path": "relationships/customers/acme", "alignment_score": state["alignment_score"]},
            anchored_soak={"risk_level": "low"},
        )
        is True
    )


def test_memory_quarantine_filters_off_focus_trace_hits():
    hits = [
        hit("acme-note", "relationships/customers/acme", bucket="stale"),
        hit("beta-note", "relationships/customers/beta", layer="core"),
    ]
    quarantine = build_memory_quarantine_snapshot(
        hits,
        memory_engine={"profile": {"current_intent": True}, "continuity_focus_path": "relationships/customers/beta"},
        memory_soak={"risk_level": "high", "contamination_score": 5},
    )
    filtered, state = apply_memory_quarantine(hits, quarantine)

    assert quarantine["active"] is True
    assert state["filtered_count"] == 1
    assert [item.source_id for item in filtered] == ["beta-note"]
    assert filtered[0].metadata["memory_quarantine_active"] is True
