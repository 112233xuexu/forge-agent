from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
import json
import uuid


@dataclass
class TaskResult:
    """Durable task record returned by the public Forge runtime."""

    task_id: str
    goal: str
    status: str
    created_at: str
    updated_at: str
    evidence: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TaskResult":
        return cls(
            task_id=str(data["task_id"]),
            goal=str(data["goal"]),
            status=str(data.get("status", "unknown")),
            created_at=str(data.get("created_at", "")),
            updated_at=str(data.get("updated_at", data.get("created_at", ""))),
            evidence=dict(data.get("evidence", {})),
        )


@dataclass
class WorkspaceStatus:
    """Human-readable workspace health status."""

    workspace: str
    workspace_exists: bool
    config_exists: bool
    ledger_exists: bool
    task_count: int
    ready: bool
    messages: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ForgeRuntime:
    """Local-first runtime facade for the public Forge Agent MVP.

    The runtime intentionally starts small: it creates a local workspace,
    persists task records, lists task history, and reports health. This gives
    non-technical users a reliable first surface while the larger RC10 source
    tree is normalized into regular public files.
    """

    def __init__(self, workspace: str | Path = ".forge-agent") -> None:
        self.workspace = Path(workspace)
        self.config_path = self.workspace / "config.json"
        self.ledger_path = self.workspace / "tasks.jsonl"

    def init_workspace(self, *, profile: str = "local", force: bool = False) -> WorkspaceStatus:
        """Create a local Forge workspace and return its health status."""

        self.workspace.mkdir(parents=True, exist_ok=True)
        if force or not self.config_path.exists():
            config = {
                "profile": profile,
                "created_at": self._now(),
                "format_version": 1,
                "approval_mode": "ask-before-risky-actions",
            }
            self.config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        self.ledger_path.touch(exist_ok=True)
        return self.doctor()

    def do(self, goal: str, **metadata: Any) -> TaskResult:
        """Accept a plain-language goal and persist it as a task record."""

        if not goal or not goal.strip():
            raise ValueError("goal must be a non-empty string")
        self.init_workspace()
        now = self._now()
        result = TaskResult(
            task_id=str(uuid.uuid4()),
            goal=goal.strip(),
            status="accepted",
            created_at=now,
            updated_at=now,
            evidence={
                "metadata": metadata,
                "workspace": str(self.workspace),
                "next_step": "planning",
            },
        )
        self._append_task(result)
        return result

    def list_tasks(self, *, limit: int | None = None) -> list[TaskResult]:
        """Return persisted task history, newest first."""

        if not self.ledger_path.exists():
            return []
        tasks: list[TaskResult] = []
        for line in self.ledger_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                tasks.append(TaskResult.from_dict(json.loads(line)))
            except (json.JSONDecodeError, KeyError, TypeError, ValueError):
                # Keep the CLI resilient if an operator manually edited the ledger.
                continue
        tasks.reverse()
        if limit is not None:
            return tasks[: max(0, limit)]
        return tasks

    def doctor(self) -> WorkspaceStatus:
        """Inspect local runtime readiness."""

        workspace_exists = self.workspace.exists()
        config_exists = self.config_path.exists()
        ledger_exists = self.ledger_path.exists()
        task_count = len(self.list_tasks()) if ledger_exists else 0
        messages: list[str] = []
        if not workspace_exists:
            messages.append("Workspace has not been initialized. Run `forge-agent init`.")
        if workspace_exists and not config_exists:
            messages.append("Workspace config is missing. Run `forge-agent init` to repair it.")
        if workspace_exists and not ledger_exists:
            messages.append("Task ledger is missing. Run `forge-agent init` to create it.")
        if workspace_exists and config_exists and ledger_exists:
            messages.append("Workspace is ready.")
        return WorkspaceStatus(
            workspace=str(self.workspace),
            workspace_exists=workspace_exists,
            config_exists=config_exists,
            ledger_exists=ledger_exists,
            task_count=task_count,
            ready=workspace_exists and config_exists and ledger_exists,
            messages=messages,
        )

    def _append_task(self, result: TaskResult) -> None:
        self.workspace.mkdir(parents=True, exist_ok=True)
        with self.ledger_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(result.to_dict(), ensure_ascii=False) + "\n")

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()
