from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
import uuid


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


CHECKPOINT_SCHEMA_VERSION = 2


def _migrate_step_attempt_payload(payload: dict[str, Any]) -> dict[str, Any]:
    migrated = dict(payload or {})
    tool_name = str(migrated.get("tool_name", migrated.get("tool", migrated.get("requested_tool_name", ""))) or "")
    if tool_name and "tool_name" not in migrated:
        migrated["tool_name"] = tool_name
    if "requested_tool_name" not in migrated:
        migrated["requested_tool_name"] = tool_name
    migrated.setdefault("args", {})
    return migrated


def _migrate_step_execution_payload(payload: dict[str, Any]) -> dict[str, Any]:
    migrated = dict(payload or {})
    tool_name = str(migrated.get("tool_name", migrated.get("tool", migrated.get("resolved_tool_name", ""))) or "")
    if tool_name and "tool_name" not in migrated:
        migrated["tool_name"] = tool_name
    if tool_name and "requested_tool_name" not in migrated:
        migrated["requested_tool_name"] = tool_name
    if tool_name and "resolved_tool_name" not in migrated:
        migrated["resolved_tool_name"] = tool_name
    migrated.setdefault("name", migrated.get("step_name", tool_name or "step"))
    migrated.setdefault("args", {})
    migrated["attempts"] = [_migrate_step_attempt_payload(item) for item in migrated.get("attempts", [])]
    return migrated


BUNDLE_MIGRATION_FIELDS = (
    "preferred_palace_path",
    "context_hint_text",
    "memory_continuity",
    "memory_continuity_resume",
    "memory_recovery",
    "memory_verdict",
    "memory_verdict_ledger",
    "governance_verdict_trust",
)


def normalize_memory_bundle_payload(payload: dict[str, Any] | None) -> dict[str, Any]:
    """Normalize RC10 memory bundle payloads from schema v1/v2 containers."""

    raw = dict(payload or {})
    migrated = dict(raw)
    legacy_context = dict(raw.get("memory_context") or {})
    if legacy_context:
        for key in BUNDLE_MIGRATION_FIELDS:
            if key in legacy_context and key not in migrated:
                migrated[key] = legacy_context[key]
    meta = dict(migrated.get("memory_bundle_meta") or {})
    migrated_fields = sorted([key for key in BUNDLE_MIGRATION_FIELDS if key in migrated and key not in raw])
    declared_schema_version = int(meta.get("schema_version", CHECKPOINT_SCHEMA_VERSION) or CHECKPOINT_SCHEMA_VERSION)
    if "source_schema_version" in meta:
        source_schema_version = int(meta.get("source_schema_version", declared_schema_version) or declared_schema_version)
    elif legacy_context and "schema_version" not in meta:
        source_schema_version = 1
    else:
        source_schema_version = declared_schema_version
    meta["schema_version"] = max(CHECKPOINT_SCHEMA_VERSION, declared_schema_version)
    meta["source_schema_version"] = max(1, source_schema_version)
    meta["legacy_source"] = bool(legacy_context) or bool(meta.get("legacy_source", False))
    if migrated_fields:
        existing = [str(item) for item in meta.get("migrated_fields", []) if str(item)]
        meta["migrated_fields"] = sorted(set(existing + migrated_fields))
    migrated["memory_bundle_meta"] = meta
    return migrated


def normalize_bundle_container_payload(payload: dict[str, Any] | None) -> dict[str, Any]:
    """Extract and normalize a memory bundle from new or legacy container shapes."""

    raw = dict(payload or {})
    if raw.get("memory_bundle") is not None:
        bundle_payload = raw.get("memory_bundle")
    elif raw.get("memory_context") is not None:
        bundle_payload = {"memory_context": raw.get("memory_context") or {}}
    else:
        bundle_payload = {}
    migrated = normalize_memory_bundle_payload(bundle_payload)
    promoted_fields: list[str] = []
    for key in BUNDLE_MIGRATION_FIELDS:
        if key in raw and key not in migrated:
            migrated[key] = raw[key]
            promoted_fields.append(key)
    if promoted_fields:
        meta = dict(migrated.get("memory_bundle_meta") or {})
        existing = [str(item) for item in meta.get("migrated_fields", []) if str(item)]
        meta["migrated_fields"] = sorted(set(existing + promoted_fields))
        meta["legacy_source"] = True
        meta["schema_version"] = max(CHECKPOINT_SCHEMA_VERSION, int(meta.get("schema_version", CHECKPOINT_SCHEMA_VERSION) or CHECKPOINT_SCHEMA_VERSION))
        meta["source_schema_version"] = int(meta.get("source_schema_version", 1) or 1)
        migrated["memory_bundle_meta"] = meta
    return migrated


def migrate_checkpoint_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Migrate legacy checkpoint payloads into the schema v2 shape."""

    raw = dict(payload or {})
    plan_payload = dict(raw.get("plan") or {})
    if not plan_payload:
        plan_payload = {
            "objective": raw.get("plan_objective", raw.get("objective", raw.get("task_text", ""))),
            "steps": raw.get("steps", []),
            "meta": raw.get("plan_meta", raw.get("meta", {})),
        }
    else:
        plan_payload.setdefault("objective", raw.get("task_text", ""))
        plan_payload.setdefault("steps", [])
        plan_payload.setdefault("meta", {})
    plan_payload["steps"] = [_migrate_step_execution_payload(item) for item in plan_payload.get("steps", [])]
    completed_steps = [_migrate_step_execution_payload(item) for item in raw.get("completed_steps", [])]

    status = str(raw.get("status", raw.get("phase", "")) or "").strip()
    if not status:
        total_steps = len(plan_payload.get("steps", []))
        next_step_index = int(raw.get("next_step_index", 0) or 0)
        status = "completed" if total_steps and next_step_index >= total_steps else "open"

    legacy_bundle_payload = raw.get("memory_bundle") if raw.get("memory_bundle") is not None else ({"memory_context": raw.get("memory_context") or {}} if raw.get("memory_context") is not None else {})
    memory_bundle = normalize_memory_bundle_payload(legacy_bundle_payload)
    context_hint_text = str(raw.get("context_hint_text", memory_bundle.get("context_hint_text", "")) or "")
    preferred_palace_path = str(raw.get("preferred_palace_path", memory_bundle.get("preferred_palace_path", "")) or "")

    return {
        "checkpoint_id": str(raw["checkpoint_id"]),
        "session_id": str(raw["session_id"]),
        "task_text": str(raw.get("task_text", plan_payload.get("objective", ""))),
        "status": status,
        "plan": plan_payload,
        "inputs": raw.get("inputs", raw.get("resolved_inputs", {})),
        "memory_bundle": memory_bundle,
        "completed_steps": completed_steps,
        "next_step_index": int(raw.get("next_step_index", 0) or 0),
        "failed_step_name": raw.get("failed_step_name"),
        "error_summary": raw.get("error_summary", raw.get("failure_reason")),
        "origin": raw.get("origin", "plan"),
        "related_skill_id": raw.get("related_skill_id"),
        "run_id": raw.get("run_id"),
        "scheduled_task_id": raw.get("scheduled_task_id"),
        "context_hint_text": context_hint_text,
        "preferred_palace_path": preferred_palace_path,
        "created_at": raw.get("created_at", utc_now()),
        "updated_at": raw.get("updated_at", utc_now()),
        "schema_version": max(CHECKPOINT_SCHEMA_VERSION, int(raw.get("schema_version", CHECKPOINT_SCHEMA_VERSION) or CHECKPOINT_SCHEMA_VERSION)),
    }


class SkillKind(str, Enum):
    PROMPT_PATTERN = "prompt_pattern"
    WORKFLOW = "workflow_skill"
    TOOL_BACKED = "tool_backed_skill"
    MICRO_SCRIPT = "micro_script_skill"


@dataclass(slots=True)
class SessionRecord:
    session_id: str
    channel: str
    user_id: str
    created_at: str
    updated_at: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class MessageRecord:
    message_id: str
    session_id: str
    role: str
    content: str
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class StepAttempt:
    attempt_no: int
    requested_tool_name: str
    tool_name: str
    args: dict[str, Any]
    success: bool
    result: Any = None
    error: str | None = None
    transient: bool = False
    fallback: bool = False
    cache_hit: bool = False
    started_at: str = field(default_factory=utc_now)
    finished_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "StepAttempt":
        data = _migrate_step_attempt_payload(payload)
        return cls(
            attempt_no=int(data.get("attempt_no", 1) or 1),
            requested_tool_name=str(data.get("requested_tool_name", data.get("tool_name", "")) or ""),
            tool_name=str(data.get("tool_name", "") or ""),
            args=dict(data.get("args", {}) or {}),
            success=bool(data.get("success", False)),
            result=data.get("result"),
            error=data.get("error"),
            transient=bool(data.get("transient", False)),
            fallback=bool(data.get("fallback", False)),
            cache_hit=bool(data.get("cache_hit", False)),
            started_at=str(data.get("started_at", utc_now())),
            finished_at=str(data.get("finished_at", utc_now())),
        )


@dataclass(slots=True)
class StepExecution:
    name: str
    tool_name: str
    args: dict[str, Any]
    result: Any = None
    success: bool = True
    error: str | None = None
    requested_tool_name: str | None = None
    resolved_tool_name: str | None = None
    attempts: list[StepAttempt] = field(default_factory=list)
    retryable_failure: bool = False
    cache_hit: bool = False

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["attempts"] = [attempt.to_dict() for attempt in self.attempts]
        return data

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "StepExecution":
        data = _migrate_step_execution_payload(payload)
        return cls(
            name=str(data.get("name", "step") or "step"),
            tool_name=str(data.get("tool_name", "") or ""),
            args=dict(data.get("args", {}) or {}),
            result=data.get("result"),
            success=bool(data.get("success", True)),
            error=data.get("error"),
            requested_tool_name=data.get("requested_tool_name"),
            resolved_tool_name=data.get("resolved_tool_name"),
            attempts=[StepAttempt.from_dict(item) for item in data.get("attempts", [])],
            retryable_failure=bool(data.get("retryable_failure", False)),
            cache_hit=bool(data.get("cache_hit", False)),
        )


@dataclass(slots=True)
class TaskPlan:
    objective: str
    steps: list[StepExecution]
    meta: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"objective": self.objective, "steps": [step.to_dict() for step in self.steps], "meta": self.meta}

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "TaskPlan":
        data = dict(payload or {})
        return cls(
            objective=str(data.get("objective", "") or ""),
            steps=[StepExecution.from_dict(step) for step in data.get("steps", [])],
            meta=dict(data.get("meta", {}) or {}),
        )


@dataclass(slots=True)
class TaskRunResult:
    session_id: str
    task_text: str
    status: str
    output: Any
    trace_id: str | None = None
    generated_skill_id: str | None = None
    reused_skill_id: str | None = None
    missing_inputs: list[str] = field(default_factory=list)
    planner_used: bool = False
    match_debug: dict[str, Any] = field(default_factory=dict)
    retryable: bool = False
    error_summary: str | None = None
    run_id: str | None = None
    checkpoint_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class RunRecord:
    run_id: str
    session_id: str
    task_text: str
    status: str
    created_at: str
    trace_id: str | None = None
    generated_skill_id: str | None = None
    reused_skill_id: str | None = None
    planner_used: bool = False
    retryable: bool = False
    error_summary: str | None = None
    scheduled_task_id: str | None = None
    checkpoint_id: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_result(cls, result: TaskRunResult, *, scheduled_task_id: str | None = None, created_at: str | None = None) -> "RunRecord":
        return cls(
            run_id=result.run_id or f"run_{uuid.uuid4().hex[:12]}",
            session_id=result.session_id,
            task_text=result.task_text,
            status=result.status,
            created_at=created_at or utc_now(),
            trace_id=result.trace_id,
            generated_skill_id=result.generated_skill_id,
            reused_skill_id=result.reused_skill_id,
            planner_used=result.planner_used,
            retryable=result.retryable,
            error_summary=result.error_summary,
            scheduled_task_id=scheduled_task_id,
            checkpoint_id=result.checkpoint_id,
            payload=result.to_dict(),
        )


@dataclass(slots=True)
class TaskRequestRecord:
    request_id: str
    session_id: str
    task_text: str
    status: str
    inputs: dict[str, Any] = field(default_factory=dict)
    due_at: str | None = None
    cadence_seconds: int | None = None
    route_action: str = ""
    preflight: dict[str, Any] = field(default_factory=dict)
    last_result: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)
    resolution_count: int = 0
    last_error: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "TaskRequestRecord":
        data = dict(payload or {})
        return cls(
            request_id=str(data["request_id"]),
            session_id=str(data["session_id"]),
            task_text=str(data["task_text"]),
            status=str(data.get("status", "open") or "open"),
            inputs=dict(data.get("inputs", {}) or {}),
            due_at=data.get("due_at"),
            cadence_seconds=data.get("cadence_seconds"),
            route_action=str(data.get("route_action", "") or ""),
            preflight=dict(data.get("preflight", {}) or {}),
            last_result=dict(data.get("last_result", {}) or {}),
            created_at=str(data.get("created_at", utc_now())),
            updated_at=str(data.get("updated_at", utc_now())),
            resolution_count=int(data.get("resolution_count", 0) or 0),
            last_error=str(data.get("last_error", "") or ""),
        )

    @classmethod
    def new(cls, *, session_id: str, task_text: str, status: str, inputs: dict[str, Any] | None = None) -> "TaskRequestRecord":
        return cls(request_id=f"req_{uuid.uuid4().hex[:12]}", session_id=session_id, task_text=task_text, status=status, inputs=inputs or {})


@dataclass(slots=True)
class ExecutionCheckpoint:
    checkpoint_id: str
    session_id: str
    task_text: str
    status: str
    plan: TaskPlan
    inputs: dict[str, Any]
    memory_bundle: dict[str, Any] = field(default_factory=dict)
    completed_steps: list[StepExecution] = field(default_factory=list)
    next_step_index: int = 0
    failed_step_name: str | None = None
    error_summary: str | None = None
    origin: str = "plan"
    related_skill_id: str | None = None
    run_id: str | None = None
    scheduled_task_id: str | None = None
    context_hint_text: str = ""
    preferred_palace_path: str = ""
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)
    schema_version: int = CHECKPOINT_SCHEMA_VERSION

    def to_dict(self) -> dict[str, Any]:
        return {
            "checkpoint_id": self.checkpoint_id,
            "session_id": self.session_id,
            "task_text": self.task_text,
            "status": self.status,
            "plan": self.plan.to_dict(),
            "inputs": self.inputs,
            "memory_bundle": self.memory_bundle,
            "completed_steps": [step.to_dict() for step in self.completed_steps],
            "next_step_index": self.next_step_index,
            "failed_step_name": self.failed_step_name,
            "error_summary": self.error_summary,
            "origin": self.origin,
            "related_skill_id": self.related_skill_id,
            "run_id": self.run_id,
            "scheduled_task_id": self.scheduled_task_id,
            "context_hint_text": self.context_hint_text,
            "preferred_palace_path": self.preferred_palace_path,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "schema_version": self.schema_version,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ExecutionCheckpoint":
        data = migrate_checkpoint_payload(payload)
        return cls(
            checkpoint_id=data["checkpoint_id"],
            session_id=data["session_id"],
            task_text=data["task_text"],
            status=data["status"],
            plan=TaskPlan.from_dict(data["plan"]),
            inputs=dict(data.get("inputs", {}) or {}),
            memory_bundle=dict(data.get("memory_bundle", {}) or {}),
            completed_steps=[StepExecution.from_dict(step) for step in data.get("completed_steps", [])],
            next_step_index=int(data.get("next_step_index", 0) or 0),
            failed_step_name=data.get("failed_step_name"),
            error_summary=data.get("error_summary"),
            origin=str(data.get("origin", "plan") or "plan"),
            related_skill_id=data.get("related_skill_id"),
            run_id=data.get("run_id"),
            scheduled_task_id=data.get("scheduled_task_id"),
            context_hint_text=str(data.get("context_hint_text", "") or ""),
            preferred_palace_path=str(data.get("preferred_palace_path", "") or ""),
            created_at=str(data.get("created_at", utc_now())),
            updated_at=str(data.get("updated_at", utc_now())),
            schema_version=int(data.get("schema_version", CHECKPOINT_SCHEMA_VERSION) or CHECKPOINT_SCHEMA_VERSION),
        )

    @classmethod
    def new(
        cls,
        *,
        session_id: str,
        task_text: str,
        plan: TaskPlan,
        inputs: dict[str, Any],
        memory_bundle: dict[str, Any] | None = None,
        completed_steps: list[StepExecution] | None = None,
        next_step_index: int = 0,
        failed_step_name: str | None = None,
        error_summary: str | None = None,
        origin: str = "plan",
        related_skill_id: str | None = None,
        run_id: str | None = None,
        scheduled_task_id: str | None = None,
        context_hint_text: str = "",
        preferred_palace_path: str = "",
    ) -> "ExecutionCheckpoint":
        return cls(
            checkpoint_id=f"ckpt_{uuid.uuid4().hex[:12]}",
            session_id=session_id,
            task_text=task_text,
            status="open",
            plan=plan,
            inputs=dict(inputs),
            memory_bundle=memory_bundle or {},
            completed_steps=list(completed_steps or []),
            next_step_index=next_step_index,
            failed_step_name=failed_step_name,
            error_summary=error_summary,
            origin=origin,
            related_skill_id=related_skill_id,
            run_id=run_id,
            scheduled_task_id=scheduled_task_id,
            context_hint_text=context_hint_text,
            preferred_palace_path=preferred_palace_path,
        )


@dataclass(slots=True)
class MemoryRecallHit:
    """A normalized memory recall candidate passed through the memory pipeline."""

    layer: str
    scope: str
    key: str
    content: str
    score: float
    reason: str = ""
    source_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
