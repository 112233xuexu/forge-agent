from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json
import uuid


DEFAULT_WINGS = ["user", "project", "skills", "operations", "sessions"]
VALID_SCOPES = {"user", "project", "session", "skill", "operation"}
VALID_SAFETY = {"normal", "sensitive"}
VALID_STATUS = {"active", "forgotten", "quarantined"}


@dataclass
class MemoryItem:
    """A visible, forgettable memory item in the local Forge memory palace."""

    id: str
    scope: str
    wing: str
    room: str
    closet: str
    drawer: str
    content: str
    source: str = "manual"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_used_at: str | None = None
    confidence: float = 1.0
    safety: str = "normal"
    status: str = "active"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MemoryItem":
        return cls(
            id=str(data["id"]),
            scope=str(data.get("scope", "project")),
            wing=str(data.get("wing", data.get("scope", "project"))),
            room=str(data.get("room", "general")),
            closet=str(data.get("closet", "default")),
            drawer=str(data.get("drawer", "inbox")),
            content=str(data.get("content", "")),
            source=str(data.get("source", "manual")),
            created_at=str(data.get("created_at", "")),
            last_used_at=data.get("last_used_at"),
            confidence=float(data.get("confidence", 1.0)),
            safety=str(data.get("safety", "normal")),
            status=str(data.get("status", "active")),
            metadata=dict(data.get("metadata", {})),
        )


class MemoryStore:
    """Local-first controlled memory palace store.

    The store is intentionally simple for v2.5: JSON/JSONL files, visible data,
    explicit governance operations, and an append-only audit log.
    """

    def __init__(self, workspace: str | Path) -> None:
        self.workspace = Path(workspace)
        self.root = self.workspace / "memory"
        self.index_path = self.root / "index.jsonl"
        self.audit_path = self.root / "audit.jsonl"
        self.palace_path = self.root / "palace.json"
        self.user_md_path = self.root / "USER.md"
        self.memory_md_path = self.root / "MEMORY.md"
        self.wings_path = self.root / "wings"

    def init(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.wings_path.mkdir(parents=True, exist_ok=True)
        for wing in DEFAULT_WINGS:
            (self.wings_path / wing).mkdir(parents=True, exist_ok=True)
        self.index_path.touch(exist_ok=True)
        self.audit_path.touch(exist_ok=True)
        if not self.palace_path.exists():
            self.palace_path.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "hierarchy": ["palace", "wing", "room", "closet", "drawer", "memory"],
                        "wings": DEFAULT_WINGS,
                        "policy": {
                            "default_scope": "project",
                            "default_safety": "normal",
                            "forgotten_memories_are_excluded": True,
                            "quarantined_memories_are_excluded": True,
                            "restore_requires_explicit_command": True,
                        },
                    },
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
        if not self.user_md_path.exists():
            self.user_md_path.write_text("# User memory\n\nVisible long-term user preferences can be summarized here.\n", encoding="utf-8")
        if not self.memory_md_path.exists():
            self.memory_md_path.write_text("# Project memory\n\nVisible project context and decisions can be summarized here.\n", encoding="utf-8")

    def add(
        self,
        content: str,
        *,
        scope: str = "project",
        wing: str | None = None,
        room: str = "general",
        closet: str = "default",
        drawer: str = "inbox",
        source: str = "manual",
        confidence: float = 1.0,
        safety: str = "normal",
        metadata: dict[str, Any] | None = None,
    ) -> MemoryItem:
        self.init()
        normalized_content = content.strip()
        if not normalized_content:
            raise ValueError("memory content cannot be empty")
        if scope not in VALID_SCOPES:
            raise ValueError(f"invalid memory scope: {scope}")
        if safety not in VALID_SAFETY:
            raise ValueError(f"invalid memory safety: {safety}")
        item = MemoryItem(
            id=f"mem_{uuid.uuid4().hex[:12]}",
            scope=scope,
            wing=wing or scope,
            room=room,
            closet=closet,
            drawer=drawer,
            content=normalized_content,
            source=source,
            confidence=confidence,
            safety=safety,
            metadata=metadata or {},
        )
        self._append_item(item)
        self._audit("add", item.id, {"scope": item.scope, "wing": item.wing, "source": item.source})
        return item

    def list(self, *, include_inactive: bool = False) -> list[MemoryItem]:
        self.init()
        items = self._read_items()
        if include_inactive:
            return items
        return [item for item in items if item.status == "active"]

    def show(self, memory_id: str) -> MemoryItem:
        for item in self._read_items():
            if item.id == memory_id:
                return item
        raise KeyError(f"memory not found: {memory_id}")

    def forget(self, memory_id: str) -> MemoryItem:
        return self._set_status(memory_id, "forgotten", action="forget")

    def quarantine(self, memory_id: str) -> MemoryItem:
        return self._set_status(memory_id, "quarantined", action="quarantine")

    def restore(self, memory_id: str) -> MemoryItem:
        return self._set_status(memory_id, "active", action="restore")

    def search(self, query: str, *, limit: int = 10) -> list[MemoryItem]:
        self.init()
        q = query.strip().lower()
        if not q:
            return []
        matches: list[MemoryItem] = []
        for item in self.list():
            haystack = " ".join([item.content, item.scope, item.wing, item.room, item.closet, item.drawer]).lower()
            if q in haystack:
                matches.append(item)
            if len(matches) >= limit:
                break
        self._audit("search", None, {"query": query, "count": len(matches)})
        return matches

    def palace(self) -> dict[str, Any]:
        self.init()
        return json.loads(self.palace_path.read_text(encoding="utf-8"))

    def export_bundle(self, *, include_inactive: bool = True, audit_limit: int = 1000) -> dict[str, Any]:
        self.init()
        items = self.list(include_inactive=include_inactive)
        bundle = {
            "version": 1,
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "workspace": str(self.workspace),
            "palace": self.palace(),
            "memories": [item.to_dict() for item in items],
            "audit": self.audit(limit=audit_limit),
            "doctor": self.doctor(),
        }
        self._audit("export", None, {"count": len(items), "include_inactive": include_inactive})
        return bundle

    def audit(self, *, limit: int = 50) -> list[dict[str, Any]]:
        self.init()
        rows: list[dict[str, Any]] = []
        for line in self.audit_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return rows[-limit:]

    def doctor(self) -> dict[str, Any]:
        self.init()
        items = self._read_items()
        active_count = len([item for item in items if item.status == "active"])
        forgotten_count = len([item for item in items if item.status == "forgotten"])
        quarantined_count = len([item for item in items if item.status == "quarantined"])
        sensitive_count = len([item for item in items if item.safety == "sensitive"])
        return {
            "ok": True,
            "root": str(self.root),
            "index_exists": self.index_path.exists(),
            "audit_exists": self.audit_path.exists(),
            "palace_exists": self.palace_path.exists(),
            "wings": DEFAULT_WINGS,
            "total": len(items),
            "active": active_count,
            "forgotten": forgotten_count,
            "quarantined": quarantined_count,
            "sensitive": sensitive_count,
        }

    def _set_status(self, memory_id: str, status: str, *, action: str) -> MemoryItem:
        self.init()
        if status not in VALID_STATUS:
            raise ValueError(f"invalid memory status: {status}")
        items = self._read_items()
        updated: MemoryItem | None = None
        previous_status: str | None = None
        for item in items:
            if item.id == memory_id:
                previous_status = item.status
                item.status = status
                updated = item
                break
        if updated is None:
            raise KeyError(f"memory not found: {memory_id}")
        self._write_items(items)
        self._audit(action, updated.id, {"scope": updated.scope, "wing": updated.wing, "from": previous_status, "to": status})
        return updated

    def _read_items(self) -> list[MemoryItem]:
        if not self.index_path.exists():
            return []
        items: list[MemoryItem] = []
        for line in self.index_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                item = MemoryItem.from_dict(json.loads(line))
            except (json.JSONDecodeError, KeyError, TypeError, ValueError):
                continue
            if item.status in VALID_STATUS:
                items.append(item)
        return items

    def _append_item(self, item: MemoryItem) -> None:
        with self.index_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(item.to_dict(), ensure_ascii=False) + "\n")

    def _write_items(self, items: list[MemoryItem]) -> None:
        self.init()
        with self.index_path.open("w", encoding="utf-8") as fh:
            for item in items:
                fh.write(json.dumps(item.to_dict(), ensure_ascii=False) + "\n")

    def _audit(self, action: str, memory_id: str | None, metadata: dict[str, Any] | None = None) -> None:
        self.init()
        row = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "memory_id": memory_id,
            "metadata": metadata or {},
        }
        with self.audit_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
