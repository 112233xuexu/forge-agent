from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json
import uuid


@dataclass
class TaskResult:
    """Result returned by the lightweight public Forge runtime."""

    task_id: str
    goal: str
    status: str
    created_at: str
    evidence: dict[str, Any] = field(default_factory=dict)


class ForgeRuntime:
    """Small public runtime facade.

    The full RC10 source package is preserved under `source-archive/` as a
    reconstructed zip archive. This facade keeps the public package installable
    while the full historical tree is being unpacked and reviewed into normal
    source files.
    """

    def __init__(self, workspace: str | Path = ".forge-agent") -> None:
        self.workspace = Path(workspace)
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.ledger_path = self.workspace / "tasks.jsonl"

    def do(self, goal: str, **metadata: Any) -> TaskResult:
        if not goal or not goal.strip():
            raise ValueError("goal must be a non-empty string")
        result = TaskResult(
            task_id=str(uuid.uuid4()),
            goal=goal.strip(),
            status="accepted",
            created_at=datetime.now(timezone.utc).isoformat(),
            evidence={"metadata": metadata, "workspace": str(self.workspace)},
        )
        with self.ledger_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(result.__dict__, ensure_ascii=False) + "\n")
        return result
