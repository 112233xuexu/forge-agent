from forge_agent.benchmark import CompatibilityBenchmark, default_benchmark_cases, run_memory_context_smoke, run_state_store_smoke
from forge_agent.models import MemoryRecallHit


def test_compatibility_benchmark_runs_default_cases(tmp_path):
    report = CompatibilityBenchmark().run_cases(default_benchmark_cases(), state_path=tmp_path / "state.db")

    assert report.passed is True
    assert [result.name for result in report.results] == ["summarize", "translate_missing", "paraphrase"]
    assert [result.status for result in report.results] == ["completed", "input_required", "completed"]


def test_memory_context_smoke_uses_focus_path():
    hit = MemoryRecallHit(
        layer="project",
        scope="project",
        key="acme",
        content="Acme invoice preference",
        score=1.0,
        source_id="mem_1",
        metadata={"path": "project/customers/acme/invoices"},
    )

    result = run_memory_context_smoke("Acme invoice", [hit])

    assert result.passed is True
    assert result.details["used_memory"] is True
    assert result.details["focus_path"] == "project/customers/acme/invoices"


def test_state_store_smoke_records_message(tmp_path):
    result = run_state_store_smoke(tmp_path / "state.db")

    assert result.passed is True
    assert result.details["message_count"] == 1
