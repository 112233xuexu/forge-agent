from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any
import json

from .desktop_adapter import DesktopAdapter, DesktopRequest
from .models import utc_now


_CLIENT_ERROR_STATUSES = {"unsupported", "blocked"}


@dataclass(slots=True)
class HttpRequestEnvelope:
    method: str
    path: str
    headers: dict[str, str] = field(default_factory=dict)
    body: dict[str, Any] = field(default_factory=dict)
    received_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_json(cls, *, method: str, path: str, headers: dict[str, str] | None = None, body: str = "{}") -> "HttpRequestEnvelope":
        parsed = json.loads(body or "{}")
        if not isinstance(parsed, dict):
            raise ValueError("HTTP adapter body must be a JSON object")
        return cls(method=method.upper(), path=path, headers=dict(headers or {}), body=parsed)


@dataclass(slots=True)
class HttpResponseEnvelope:
    status_code: int
    body: dict[str, Any]
    headers: dict[str, str] = field(default_factory=lambda: {"content-type": "application/json"})

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.body, ensure_ascii=False, sort_keys=True)


class HttpAdapter:
    """Pure payload adapter for local tests; it does not run a web server."""

    def __init__(self, desktop: DesktopAdapter) -> None:
        self.desktop = desktop

    def handle(self, envelope: HttpRequestEnvelope) -> HttpResponseEnvelope:
        if envelope.method not in {"POST", "GET"}:
            return HttpResponseEnvelope(405, {"error": "method_not_allowed"})
        path = envelope.path.rstrip("/") or "/"
        if path in {"/health", "/ping"}:
            response = self.desktop.handle(DesktopRequest.new(action="health"))
            return HttpResponseEnvelope(200, response.to_dict())
        if path not in {"/run", "/plan", "/execute"}:
            return HttpResponseEnvelope(404, {"error": "not_found", "path": envelope.path})
        action = path.strip("/")
        payload = dict(envelope.body)
        payload.setdefault("action", action)
        response = self.desktop.handle(payload)
        status_code = 400 if response.status in _CLIENT_ERROR_STATUSES else 200
        return HttpResponseEnvelope(status_code, response.to_dict())
