from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any
import time

from .context_builder import build_context_for_query
from .memory_engine import run_memory_engine
from .models import MemoryRecallHit
from .runtime_compat import CompatRuntime
from .session_state import StateStore
from .tool_registry import ToolRegistry


@dataclass(slots=True)
class BenchmarkCase:
    name: str
    task_text: str
    inputs: dict[str, Any] = field(default_factory=dict)
    expected_status: str = "planned"
    requires_tools: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class BenchmarkResult:
    name: str
    passed: bool
    status: str
    duration_ms: float
    details: dict[str, Any] = field(default_factory=dict)
    error: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class BenchmarkReport:
    suite: str
    results: list[BenchmarkResult]

    @property
    def passed(self) -> bool:
        return all(result.passed for result in self.results)

    def to_dict(self) -> dict[str, Any]:
        return {"suite": self.suite, "passed": self.passed, "results": [result.to_dict() for result in self.results]}


class CompatibilityBenchmark:
    """Local benchmark/smoke harness for migrated RC10 compatibility slices."""

    def __init__(self, tools: ToolRegistry | None = None) -> None:
        self.tools = tools or default_benchmark_tools()

    def run_cases(self, cases: list[BenchmarkCase], *, state_path: str | Path) -> BenchmarkReport:
        results: list[BenchmarkResult] = []
        runtime = CompatRuntime(state_path, self.tools)
        try:
            for case in cases:
                started = time.perf_counter()
                try:
                    missing = [tool for tool in case.requires_tools if not self.tools.has(tool)]
                    if missing:
                        results.append(BenchmarkResult(case.name, False, "missing_tools", _elapsed_ms(started), {"missing_tools": missing}))
                        continue
                    result = runtime.run_local(case.task_text, inputs=case.inputs, execute=case.expected_status == "completed", govern=True)
                    results.append(
                        BenchmarkResult(
                            name=case.name,
                            passed=result.status == case.expected_status,
                            status=result.status,
                            duration_ms=_elapsed_ms(started),
                            details={"session_id": result.session_id, "payload_keys": sorted(result.payload)},
                        )
                    )
                except Exception as exc:  # noqa: BLE001 - benchmark records failures without hiding them
                    results.append(BenchmarkResult(case.name, False, "error", _elapsed_ms(started), error=str(exc)))
        finally:
            runtime.close()
        return BenchmarkReport("compatibility", results)


def run_memory_context_smoke(query: str, hits: list[MemoryRecallHit]) -> BenchmarkResult:
    started = time.perf_counter()
    try:
        engine = run_memory_engine(query, hits)
        context = build_context_for_query(query, engine.verdict.adopted or hits)
        passed = bool(engine.verdict.adopted or not hits) and (bool(context.focus_path) or not hits)
        return BenchmarkResult(
            name="memory_context_smoke",
            passed=passed,
            status="passed" if passed else "failed",
            duration_ms=_elapsed_ms(started),
            details={"used_memory": engine.verdict.used_memory, "focus_path": context.focus_path},
        )
    except Exception as exc:  # noqa: BLE001
        return BenchmarkResult("memory_context_smoke", False, "error", _elapsed_ms(started), error=str(exc))


def run_state_store_smoke(state_path: str | Path) -> BenchmarkResult:
    started = time.perf_counter()
    store = StateStore(state_path)
    try:
        session = store.get_or_create_session("benchmark", "local-user")
        store.add_message(session.session_id, "user", "hello")
        messages = store.get_messages(session.session_id)
        passed = bool(session.session_id and messages)
        return BenchmarkResult("state_store_smoke", passed, "passed" if passed else "failed", _elapsed_ms(started), {"session_id": session.session_id, "message_count": len(messages)})
    except Exception as exc:  # noqa: BLE001
        return BenchmarkResult("state_store_smoke", False, "error", _elapsed_ms(started), error=str(exc))
    finally:
        store.close()


def default_benchmark_tools() -> ToolRegistry:
    tools = ToolRegistry()
    tools.register("summarize_notes", lambda notes: {"summary": notes, "action_items": [notes]})
    tools.register("translate_text", lambda text, target_language: f"[{target_language}] {text}")
    tools.register("paraphrase_text", lambda text, style="clear": f"[{style}] {text}")
    return tools


def default_benchmark_cases() -> list[BenchmarkCase]:
    return [
        BenchmarkCase("summarize", "Summarize these notes", {"notes": "prepare update"}, "completed", ["summarize_notes"]),
        BenchmarkCase("translate_missing", "Translate this into spanish", {}, "input_required", ["translate_text"]),
        BenchmarkCase("paraphrase", 'Rewrite "Need approval" in a warmer tone', {"text": "Need approval", "style": "warm"}, "completed", ["paraphrase_text"]),
    ]


def _elapsed_ms(started: float) -> float:
    return round((time.perf_counter() - started) * 1000.0, 3)
