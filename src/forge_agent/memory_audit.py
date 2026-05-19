from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json


def append_audit_row(
    audit_path: Path,
    *,
    action: str,
    memory_id: str | None,
    metadata: dict[str, Any] | None = None,
) -> None:
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "memory_id": memory_id,
        "metadata": metadata or {},
    }
    with audit_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def read_audit_rows(audit_path: Path, *, limit: int = 50) -> list[dict[str, Any]]:
    if not audit_path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in audit_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows[-limit:]
