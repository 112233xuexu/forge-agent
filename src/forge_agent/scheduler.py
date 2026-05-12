from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json
import uuid


@dataclass
class ScheduledTask:
    task_id: str
    command: str
    schedule: str
    status: str = "active"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ScheduledTask":
        return cls(
            task_id=str(data["task_id"]),
            command=str(data["command"]),
            schedule=str(data.get("schedule", "manual")),
            status=str(data.get("status", "active")),
            created_at=str(data.get("created_at", "")),
            metadata=dict(data.get("metadata", {})),
        )


class ScheduleStore:
    """Local schedule registry.

    v1.5 intentionally stores schedules rather than running a background daemon.
    The product contract is visible and safe: users can create, list, pause, and
    resume automations. A later desktop/background service can execute them.
    """

    def __init__(self, workspace: str | Path = ".forge-agent") -> None:
        self.workspace = Path(workspace)
        self.path = self.workspace / "schedules.jsonl"

    def init(self) -> None:
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.path.touch(exist_ok=True)

    def add(self, command: str, schedule: str) -> ScheduledTask:
        self.init()
        task = ScheduledTask(task_id=str(uuid.uuid4()), command=command.strip(), schedule=schedule.strip())
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(task.to_dict(), ensure_ascii=False) + "\n")
        return task

    def list(self) -> list[ScheduledTask]:
        if not self.path.exists():
            return []
        tasks: list[ScheduledTask] = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                tasks.append(ScheduledTask.from_dict(json.loads(line)))
            except (json.JSONDecodeError, KeyError, TypeError, ValueError):
                continue
        return tasks

    def set_status(self, task_id: str, status: str) -> ScheduledTask:
        if status not in {"active", "paused"}:
            raise ValueError("status must be active or paused")
        tasks = self.list()
        updated: ScheduledTask | None = None
        for task in tasks:
            if task.task_id == task_id or task.task_id.startswith(task_id):
                task.status = status
                updated = task
        if updated is None:
            raise KeyError(f"schedule not found: {task_id}")
        self._rewrite(tasks)
        return updated

    def _rewrite(self, tasks: list[ScheduledTask]) -> None:
        self.init()
        with self.path.open("w", encoding="utf-8") as fh:
            for task in tasks:
                fh.write(json.dumps(task.to_dict(), ensure_ascii=False) + "\n")
