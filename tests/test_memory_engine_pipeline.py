from forge_agent.memory_engine import run_memory_engine, select_memory_context
from forge_agent.memory_verdict import should_adopt_verdict_reanchor
from forge_agent.models import MemoryRecallHit


def hit(key, content, score=1.0, **metadata):
    return MemoryRecallHit(
        layer="preference",
        scope="project",
        key=key,
        content=content,
        score=score,
        source_id=metadata.pop("source_id", key),
        metadata=metadata,
    )


def test_memory_engine_prefers_current_anchored_recent_memory():
    result = run_memory_engine(
        "email invoice reports to finance team",
        [
            hit("invoice workflow", "email invoice reports to the finance team", 0.6, updated_at="2026-05-20T00:00:00+00:00"),
            hit("unrelated travel", "book hotel near station", 1.0, updated_at="2026-05-21T00:00:00+00:00"),
        ],
        reference_time="2026-05-22T00:00:00+00:00",
    )

    assert result.verdict.used_memory is True
    assert [item.key for item in result.verdict.adopted] == ["invoice workflow"]
    assert result.ranked[0].hit.key == "invoice workflow"


def test_memory_engine_resolves_conflicting_slots_by_freshness():
    result = run_memory_engine(
        "use my preferred report format",
        [
            hit("report format", "preferred report format is csv", 0.9, slot="report-format", updated_at="2026-04-01T00:00:00+00:00", source_id="old"),
            hit("report format", "preferred report format is xlsx", 0.7, slot="report-format", updated_at="2026-05-21T00:00:00+00:00", source_id="new"),
        ],
        reference_time="2026-05-22T00:00:00+00:00",
    )

    assert [item.source_id for item in result.verdict.adopted] == ["new"]
    assert [item.source_id for item in result.resolution.suppressed] == ["old"]
    assert result.verdict.warnings


def test_select_memory_context_respects_limit():
    selected = select_memory_context(
        "organize project files",
        [
            hit("project files", "organize project files by month", 1.0),
            hit("project folders", "project files live in local folders", 0.8),
        ],
        limit=1,
    )

    assert len(selected) == 1


def test_verdict_reanchor_requires_adopted_memory_and_no_quarantine():
    result = run_memory_engine("remember invoice rule", [hit("invoice rule", "remember invoice rule", 1.0)])

    assert should_adopt_verdict_reanchor(result.verdict) is True
    assert should_adopt_verdict_reanchor(result.verdict, current_quarantine={"blocked": True}) is False
