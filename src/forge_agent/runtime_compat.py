from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .gateway import GatewayReply, GatewayRouter, InboundMessage, LocalChannel, WebhookChannel
from .governance import GovernanceEngine, GovernancePolicy
from .planner import SimplePlanner
from .session_state import StateStore
from .tool_registry import ToolRegistry
from .workflow import WorkflowBundle
from .workflow_executor import WorkflowExecutor


@dataclass(slots=True)
class RuntimeTurnResult:
    session_id: str
    status: str
    text: str
    payload: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {"session_id": self.session_id, "status": self.status, "text": self.text, "payload": self.payload}


class CompatRuntime:
    """Minimal RC10-compatible runtime facade for planner/gateway integration tests."""

    def __init__(self, state: StateStore | str | Path, tools: ToolRegistry | None = None, policy: GovernancePolicy | None = None) -> None:
        self.state = state if isinstance(state, StateStore) else StateStore(state)
        self.tools = tools or ToolRegistry()
        self.planner = SimplePlanner(self.tools)
        self.executor = WorkflowExecutor(self.tools)
        self.governance = GovernanceEngine(policy)
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
        execute: bool = False,
        govern: bool = False,
    ) -> RuntimeTurnResult:
        inbound = InboundMessage.new(channel=channel, user_id=user_id, text=text, session_id=session_id)
        _envelope, reply = self.router.route(inbound, inputs=inputs or {})
        result = self._from_reply(reply)
        result = self._maybe_govern(result) if govern else result
        return self._maybe_execute(result, inputs=inputs or {}) if execute else result

    def run_task(
        self,
        session_id: str,
        text: str,
        *,
        inputs: dict[str, Any] | None = None,
        execute: bool = False,
        govern: bool = False,
    ) -> RuntimeTurnResult:
        return self.run_turn(session_id, text, inputs=inputs, execute=execute, govern=govern)

    def run_local(
        self,
        text: str,
        *,
        user_id: str = "default-user",
        inputs: dict[str, Any] | None = None,
        execute: bool = False,
        govern: bool = False,
    ) -> RuntimeTurnResult:
        channel = LocalChannel()
        inbound = channel.build_inbound(user_id=user_id, text=text)
        _envelope, reply = self.router.route(inbound, inputs=inputs or {})
        channel.deliver(reply)
        result = self._from_reply(reply)
        result = self._maybe_govern(result) if govern else result
        return self._maybe_execute(result, inputs=inputs or {}) if execute else result

    def run_webhook(
        self,
        payload: dict[str, Any],
        *,
        default_user_id: str = "default-user",
        inputs: dict[str, Any] | None = None,
        execute: bool = False,
        govern: bool = False,
    ) -> RuntimeTurnResult:
        channel = WebhookChannel()
        inbound = channel.build_inbound_from_payload(payload, default_user_id=default_user_id)
        _envelope, reply = self.router.route(inbound, inputs=inputs or {})
        channel.deliver(reply)
        result = self._from_reply(reply)
        result = self._maybe_govern(result) if govern else result
        return self._maybe_execute(result, inputs=inputs or {}) if execute else result

    def close(self) -> None:
        self.state.close()

    def _from_reply(self, reply: GatewayReply) -> RuntimeTurnResult:
        return RuntimeTurnResult(session_id=reply.session_id, status=reply.status, text=reply.text, payload=reply.payload)

    def _maybe_govern(self, result: RuntimeTurnResult) -> RuntimeTurnResult:
        route = dict(result.payload.get("route") or {})
        plan_payload = route.get("plan")
        if result.status != "planned" or not isinstance(plan_payload, dict):
            return result
        from .models import TaskPlan

        verdict = self.governance.evaluate_plan(TaskPlan.from_dict(plan_payload))
        payload = dict(result.payload)
        payload["governance"] = verdict.to_dict()
        if verdict.decision == "allow":
            return RuntimeTurnResult(result.session_id, result.status, result.text, payload)
        if verdict.decision == "confirm":
            return RuntimeTurnResult(result.session_id, "confirmation_required", "Please confirm before I continue.", payload)
        return RuntimeTurnResult(result.session_id, "blocked", "I cannot continue with that plan.", payload)

    def _maybe_execute(self, result: RuntimeTurnResult, *, inputs: dict[str, Any]) -> RuntimeTurnResult:
        if result.status != "planned":
            return result
        route = dict(result.payload.get("route") or {})
        plan_payload = route.get("plan")
        if not isinstance(plan_payload, dict):
            return result
        from .models import TaskPlan

        plan = TaskPlan.from_dict(plan_payload)
        execution = self.executor.execute(WorkflowBundle.from_task_plan(plan, inputs=inputs), inputs=inputs)
        payload = dict(result.payload)
        payload["execution"] = execution.to_dict()
        status = execution.status
        text = "I completed the planned work." if status == "completed" else result.text
        return RuntimeTurnResult(session_id=result.session_id, status=status, text=text, payload=payload)
