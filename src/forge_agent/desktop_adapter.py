from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any
import json
import uuid

from .models import utc_now
from .runtime_compat import CompatRuntime


@dataclass(slots=True)
class DesktopRequest:
    request_id: str
    action: str
    text: str = ""
    user_id: str = "desktop-user"
    session_id: str | None = None
    inputs: dict[str, Any] = field(default_factory=dict)
    options: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now)

    @classmethod
    def new(cls, *, action: str, text: str = "", user_id: str = "desktop-user", session_id: str | None = None, inputs: dict[str, Any] | None = None, options: dict[str, Any] | None = None) -> "DesktopRequest":
        return cls(
            request_id=f"desk_{uuid.uuid4().hex[:12]}",
            action=action,
            text=text,
            user_id=user_id,
            session_id=session_id,
            inputs=dict(inputs or {}),
            options=dict(options or {}),
        )

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "DesktopRequest":
        data = dict(payload or {})
        return cls(
            request_id=str(data.get("request_id") or f"desk_{uuid.uuid4().hex[:12]}"),
            action=str(data.get("action") or data.get("command") or "plan"),
            text=str(data.get("text", "") or ""),
            user_id=str(data.get("user_id", "desktop-user") or "desktop-user"),
            session_id=data.get("session_id"),
            inputs=dict(data.get("inputs", {}) or {}),
            options=dict(data.get("options", {}) or {}),
            created_at=str(data.get("created_at", utc_now())),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class DesktopResponse:
    request_id: str
    status: str
    text: str
    payload: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True)


class DesktopAdapter:
    """Small local-client adapter around CompatRuntime."""

    def __init__(self, runtime: CompatRuntime) -> None:
        self.runtime = runtime

    def handle(self, request: DesktopRequest | dict[str, Any]) -> DesktopResponse:
        envelope = request if isinstance(request, DesktopRequest) else DesktopRequest.from_dict(request)
        action = envelope.action.lower().strip()
        if action in {"ping", "health"}:
            return DesktopResponse(envelope.request_id, "ok", "Forge Agent is ready.", {"action": action})
        if action not in {"plan", "run", "execute"}:
            return DesktopResponse(envelope.request_id, "unsupported", f"Unsupported action: {envelope.action}", {"action": envelope.action})
        result = self.runtime.run_turn(
            envelope.session_id,
            envelope.text,
            channel="desktop",
            user_id=envelope.user_id,
            inputs=envelope.inputs,
            execute=action == "execute" or bool(envelope.options.get("execute", False)),
            govern=bool(envelope.options.get("govern", False)),
        )
        return DesktopResponse(envelope.request_id, result.status, result.text, result.to_dict())

    def handle_json(self, content: str) -> str:
        return self.handle(json.loads(content)).to_json()
