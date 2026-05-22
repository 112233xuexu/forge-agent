from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .gateway import GatewayReply, GatewayRouter, InboundMessage, LocalChannel, WebhookChannel
from .planner import SimplePlanner
from .session_state import StateStore
from .tool_registry import ToolRegistry


@dataclass(slots=True)
class RuntimeTurnResult:
    session_id: str
    status: str
    text: str
    payload: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {"session_id": self.session_id, "status": self.status, "text": self.text, "payload": self.payload}


class CompatRuntime:
    """Minimal RC10-compatible runtime facade for planner/gateway integration tests.

    This facade intentionally does not replace the public ForgeRuntime in
    runtime.py. It gives follow-up migration PRs a safe place to test gateway,
    state, planner, and registry wiring before default command behavior changes.
    """

    def __init__(self, state: StateStore | str | Path, tools: ToolRegistry | None = None) -> None:
        self.state = state if isinstance(state, StateStore) else StateStore(state)
        self.tools = tools or ToolRegistry()
        self.planner = SimplePlanner(self.tools)
        self.router = GatewayRouter(self.state, planner=self.planner)

    def get_or_create_session(self, *, channel: str = "local", user_id: str = "default-user"):
        return self.state.get_or_create_session(channel, user_id)

    def run_turn(
        self,
        session_id: str | None,
        text: str,
        *,
        channel: str = "local",
        user_id: str = "default-user",
        inputs: dict[str, Any] | None = None,
    ) -> RuntimeTurnResult:
        inbound = InboundMessage.new(channel=channel, user_id=user_id, text=text, session_id=session_id)
        _envelope, reply = self.router.route(inbound, inputs=inputs or {})
        return self._from_reply(reply)

    def run_task(
        self,
        session_id: str,
        text: str,
        *,
        inputs: dict[str, Any] | None = None,
    ) -> RuntimeTurnResult:
        return self.run_turn(session_id, text, inputs=inputs)

    def run_local(self, text: str, *, user_id: str = "default-user", inputs: dict[str, Any] | None = None) -> RuntimeTurnResult:
        channel = LocalChannel()
        inbound = channel.build_inbound(user_id=user_id, text=text)
        _envelope, reply = self.router.route(inbound, inputs=inputs or {})
        channel.deliver(reply)
        return self._from_reply(reply)

    def run_webhook(self, payload: dict[str, Any], *, default_user_id: str = "default-user", inputs: dict[str, Any] | None = None) -> RuntimeTurnResult:
        channel = WebhookChannel()
        inbound = channel.build_inbound_from_payload(payload, default_user_id=default_user_id)
        _envelope, reply = self.router.route(inbound, inputs=inputs or {})
        channel.deliver(reply)
        return self._from_reply(reply)

    def close(self) -> None:
        self.state.close()

    def _from_reply(self, reply: GatewayReply) -> RuntimeTurnResult:
        return RuntimeTurnResult(session_id=reply.session_id, status=reply.status, text=reply.text, payload=reply.payload)
