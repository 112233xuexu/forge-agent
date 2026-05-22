from __future__ import annotations

import json
import sqlite3
import uuid
from pathlib import Path
from typing import Any

from .models import ExecutionCheckpoint, MessageRecord, SessionRecord, utc_now


class StateStore:
    """Small RC10-compatible SQLite state store subset.

    Only sessions, messages, and checkpoints are migrated here. The full RC10
    store is intentionally left for later tested slices.
    """

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        if self.db_path.parent != Path(""):
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        self.conn.execute("CREATE TABLE IF NOT EXISTS sessions (session_id TEXT PRIMARY KEY, channel TEXT NOT NULL, user_id TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_channel_user_updated ON sessions(channel, user_id, updated_at DESC)")
        self.conn.execute("CREATE TABLE IF NOT EXISTS messages (message_id TEXT PRIMARY KEY, session_id TEXT NOT NULL, role TEXT NOT NULL, content TEXT NOT NULL, created_at TEXT NOT NULL)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_session_created ON messages(session_id, created_at ASC)")
        self.conn.execute("CREATE TABLE IF NOT EXISTS checkpoints (checkpoint_id TEXT PRIMARY KEY, session_id TEXT NOT NULL, task_text TEXT NOT NULL, status TEXT NOT NULL, payload TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_checkpoints_status_updated ON checkpoints(status, updated_at DESC)")
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    def create_session(self, channel: str, user_id: str) -> SessionRecord:
        now = utc_now()
        record = SessionRecord(session_id=f"sess_{uuid.uuid4().hex[:12]}", channel=channel, user_id=user_id, created_at=now, updated_at=now)
        self.conn.execute("INSERT INTO sessions(session_id, channel, user_id, created_at, updated_at) VALUES (?, ?, ?, ?, ?)", (record.session_id, record.channel, record.user_id, record.created_at, record.updated_at))
        self.conn.commit()
        return record

    def get_or_create_session(self, channel: str, user_id: str) -> SessionRecord:
        existing = self.find_latest_session(channel, user_id)
        if existing is not None:
            return existing
        return self.create_session(channel, user_id)

    def get_session(self, session_id: str) -> SessionRecord | None:
        row = self.conn.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,)).fetchone()
        return self._session_from_row(row) if row else None

    def find_latest_session(self, channel: str, user_id: str) -> SessionRecord | None:
        row = self.conn.execute("SELECT * FROM sessions WHERE channel = ? AND user_id = ? ORDER BY updated_at DESC LIMIT 1", (channel, user_id)).fetchone()
        return self._session_from_row(row) if row else None

    def list_sessions(self) -> list[SessionRecord]:
        rows = self.conn.execute("SELECT * FROM sessions ORDER BY updated_at DESC").fetchall()
        return [self._session_from_row(row) for row in rows]

    def add_message(self, session_id: str, role: str, content: str | dict[str, Any]) -> MessageRecord:
        now = utc_now()
        payload = json.dumps(content, ensure_ascii=False, sort_keys=True) if isinstance(content, dict) else str(content)
        record = MessageRecord(message_id=f"msg_{uuid.uuid4().hex[:12]}", session_id=session_id, role=role, content=payload, created_at=now)
        self.conn.execute("INSERT INTO messages(message_id, session_id, role, content, created_at) VALUES (?, ?, ?, ?, ?)", (record.message_id, record.session_id, record.role, record.content, record.created_at))
        self.conn.execute("UPDATE sessions SET updated_at = ? WHERE session_id = ?", (now, session_id))
        self.conn.commit()
        return record

    def get_messages(self, session_id: str) -> list[MessageRecord]:
        rows = self.conn.execute("SELECT * FROM messages WHERE session_id = ? ORDER BY created_at ASC", (session_id,)).fetchall()
        return [MessageRecord(message_id=row["message_id"], session_id=row["session_id"], role=row["role"], content=row["content"], created_at=row["created_at"]) for row in rows]

    def upsert_checkpoint(self, checkpoint: ExecutionCheckpoint) -> None:
        existing = self.get_checkpoint(checkpoint.checkpoint_id)
        payload = json.dumps(checkpoint.to_dict(), ensure_ascii=False, sort_keys=True)
        if existing is None:
            self.conn.execute("INSERT INTO checkpoints(checkpoint_id, session_id, task_text, status, payload, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)", (checkpoint.checkpoint_id, checkpoint.session_id, checkpoint.task_text, checkpoint.status, payload, checkpoint.created_at, checkpoint.updated_at))
        else:
            self.conn.execute("UPDATE checkpoints SET session_id = ?, task_text = ?, status = ?, payload = ?, updated_at = ? WHERE checkpoint_id = ?", (checkpoint.session_id, checkpoint.task_text, checkpoint.status, payload, checkpoint.updated_at, checkpoint.checkpoint_id))
        self.conn.commit()

    def get_checkpoint(self, checkpoint_id: str) -> ExecutionCheckpoint | None:
        row = self.conn.execute("SELECT payload FROM checkpoints WHERE checkpoint_id = ?", (checkpoint_id,)).fetchone()
        if row is None:
            return None
        return ExecutionCheckpoint.from_dict(json.loads(row["payload"]))

    def delete_checkpoint(self, checkpoint_id: str) -> None:
        self.conn.execute("DELETE FROM checkpoints WHERE checkpoint_id = ?", (checkpoint_id,))
        self.conn.commit()

    def list_checkpoints(self, limit: int = 20, *, status: str | None = None) -> list[ExecutionCheckpoint]:
        if status is None:
            rows = self.conn.execute("SELECT payload FROM checkpoints ORDER BY updated_at DESC LIMIT ?", (max(0, limit),)).fetchall()
        else:
            rows = self.conn.execute("SELECT payload FROM checkpoints WHERE status = ? ORDER BY updated_at DESC LIMIT ?", (status, max(0, limit))).fetchall()
        return [ExecutionCheckpoint.from_dict(json.loads(row["payload"])) for row in rows]

    def _session_from_row(self, row: sqlite3.Row) -> SessionRecord:
        return SessionRecord(session_id=row["session_id"], channel=row["channel"], user_id=row["user_id"], created_at=row["created_at"], updated_at=row["updated_at"])
