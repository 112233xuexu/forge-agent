from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any
import uuid

from .models import SessionRecord, utc_now
from .planner import PlannerResult, SimplePlanner
from .session_state import StateStore


@dataclass(slots=True)
class InboundMessage:
    event_id: str
    channel: str
    user_id: str
    text: str
    session_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now)

    @classmethod
    def new(
        cls,
        *,
        channel: str,
        user_id: str,
        text: str,
        session_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> "InboundMessage":
        return cls(
            event_id=f"evt_{uuid.uuid4().hex[:12]}",
            channel=channel,
            user_id=user_id,
            text=text,
            session_id=session_id,
            metadata=dict(metadata or {}),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class SessionBinding:
    session_id: str
    channel: str
    user_id: str
    binding_mode: str
    reused_existing: bool
    requested_session_id: str | None = None
    reason: str = ""
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class InboundEnvelope:
    envelope_id: str
    inbound: InboundMessage
    binding: SessionBinding
    route: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now)

    @classmethod
    def wrap(cls, inbound: InboundMessage, binding: SessionBinding, *, route: dict[str, Any] | None = None) -> "InboundEnvelope":
        return cls(envelope_id=f"env_{uuid.uuid4().hex[:12]}", inbound=inbound, binding=binding, route=dict(route or {}))

    def to_dict(self) -> dict[str, Any]:
        return {
            "envelope_id": self.envelope_id,
            "created_at": self.created_at,
            "inbound": self.inbound.to_dict(),
            "binding": self.binding.to_dict(),
            "route": dict(self.route),
        }


@dataclass(slots=True)
class GatewayReply:
    session_id: str
    channel: str
    user_id: str
    status: str
    text: str
    payload: dict[str, Any] = field(default_factory=dict)
    request_id: str | None = None
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class DeliveryResult:
    channel: str
    delivered: bool
    payload: dict[str, Any]
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class LocalChannel:
    def __init__(self, name: str = "local") -> None:
        self.name = name
        self.deliveries: list[GatewayReply] = []

    def build_inbound(
        self,
        *,
        user_id: str,
        text: str,
        session_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> InboundMessage:
        return InboundMessage.new(channel=self.name, user_id=user_id, text=text, session_id=session_id, metadata=metadata)

    def deliver(self, reply: GatewayReply) -> DeliveryResult:
        self.deliveries.append(reply)
        return DeliveryResult(
            channel=self.name,
            delivered=True,
            payload={"session_id": reply.session_id, "status": reply.status, "text": reply.text, "request_id": reply.request_id},
        )


class WebhookChannel(LocalChannel):
    """Generic payload adapter that normalizes common message shapes."""

    def __init__(self, name: str = "webhook") -> None:
        super().__init__(name=name)

    def build_inbound_from_payload(
        self,
        payload: dict[str, Any],
        *,
        default_user_id: str = "default-user",
        session_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> InboundMessage:
        normalized = self.normalize_payload(payload, default_user_id=default_user_id, session_id=session_id)
        combined_metadata = dict(metadata or {})
        combined_metadata.update(normalized.get("metadata") or {})
        return self.build_inbound(
            user_id=str(normalized.get("user_id") or default_user_id),
            text=str(normalized.get("text") or ""),
            session_id=normalized.get("session_id") or session_id,
            metadata=combined_metadata,
        )

    def normalize_payload(self, payload: dict[str, Any], *, default_user_id: str = "default-user", session_id: str | None = None) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise TypeError("payload must be a JSON object")
        message = payload.get("message") if isinstance(payload.get("message"), dict) else {}
        event = payload.get("event") if isinstance(payload.get("event"), dict) else {}
        user_obj = payload.get("user") if isinstance(payload.get("user"), dict) else {}
        user_token = payload.get("user") if isinstance(payload.get("user"), str) else None
        text = payload.get("text") or payload.get("body") or message.get("text") or message.get("body") or event.get("text") or event.get("body") or ""
        resolved_user = payload.get("user_id") or user_token or user_obj.get("id") or user_obj.get("user_id") or event.get("user_id") or default_user_id
        resolved_session = payload.get("session_id") or message.get("session_id") or event.get("session_id") or session_id
        return {
            "text": str(text or ""),
            "user_id": str(resolved_user or default_user_id),
            "session_id": str(resolved_session) if resolved_session else None,
            "metadata": {"source": "webhook", "payload_keys": sorted(str(key) for key in payload)},
        }


class GatewayRouter:
    """Bind inbound messages to sessions and optionally route through SimplePlanner."""

    def __init__(self, state: StateStore, *, planner: SimplePlanner | None = None) -> None:
        self.state = state
        self.planner = planner

    def bind_session(self, inbound: InboundMessage) -> SessionBinding:
        if inbound.session_id:
            requested = self.state.get_session(inbound.session_id)
            if requested is not None:
                return SessionBinding(
                    session_id=requested.session_id,
                    channel=inbound.channel,
                    user_id=inbound.user_id,
                    binding_mode="requested",
                    reused_existing=True,
                    requested_session_id=inbound.session_id,
                    reason="matched requested session",
                )
        latest = self.state.find_latest_session(inbound.channel, inbound.user_id)
        if latest is not None:
            return SessionBinding(
                session_id=latest.session_id,
                channel=inbound.channel,
                user_id=inbound.user_id,
                binding_mode="latest",
                reused_existing=True,
                requested_session_id=inbound.session_id,
                reason="reused latest session",
            )
        created = self.state.create_session(inbound.channel, inbound.user_id)
        return SessionBinding(
            session_id=created.session_id,
            channel=inbound.channel,
            user_id=inbound.user_id,
            binding_mode="created",
            reused_existing=False,
            requested_session_id=inbound.session_id,
            reason="created new session",
        )

    def route(self, inbound: InboundMessage, *, inputs: dict[str, Any] | None = None) -> tuple[InboundEnvelope, GatewayReply]:
        binding = self.bind_session(inbound)
        self.state.add_message(binding.session_id, "user", inbound.text)
        route = self._plan_route(inbound.text, inputs=inputs or {})
        envelope = InboundEnvelope.wrap(inbound, binding, route=route)
        reply = self._build_reply(inbound, binding, route)
        self.state.add_message(binding.session_id, "assistant", reply.to_dict())
        return envelope, reply

    def dispatch(self, channel: LocalChannel, inbound: InboundMessage, *, inputs: dict[str, Any] | None = None) -> DeliveryResult:
        _envelope, reply = self.route(inbound, inputs=inputs)
        return channel.deliver(reply)

    def _plan_route(self, text: str, *, inputs: dict[str, Any]) -> dict[str, Any]:
        if self.planner is None:
            return {"status": "accepted", "reason": "no planner configured"}
        result = self.planner.build_plan(text, inputs=inputs)
        if result.plan is None:
            return {"status": "input_required" if result.missing_inputs else "accepted", "reason": result.reason, "missing_inputs": result.missing_inputs}
        return {"status": "planned", "reason": result.reason, "missing_inputs": [], "plan": result.plan.to_dict()}

    def _build_reply(self, inbound: InboundMessage, binding: SessionBinding, route: dict[str, Any]) -> GatewayReply:
        status = str(route.get("status", "accepted"))
        if status == "planned":
            steps = (route.get("plan") or {}).get("steps") or []
            text = f"I made a plan with {len(steps)} step(s)."
        elif status == "input_required":
            missing = ", ".join(str(item) for item in route.get("missing_inputs", []))
            text = f"I need this first: {missing}." if missing else "I need more information first."
        else:
            text = "I received your request."
        return GatewayReply(
            session_id=binding.session_id,
            channel=inbound.channel,
            user_id=inbound.user_id,
            status=status,
            text=text,
            payload={"route": route},
            request_id=inbound.event_id,
        )
