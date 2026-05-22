from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any
import hashlib
import json
import uuid

from .models import ExecutionCheckpoint, TaskPlan, utc_now
from .workflow_executor import WorkflowExecutionResult


RISK_RANK = {"low": 1, "medium": 2, "high": 3, "critical": 4}


@dataclass(slots=True)
class GovernancePolicy:
    require_confirmation_for: set[str] = field(default_factory=lambda: {"write", "delete", "send", "external"})
    blocked_tools: set[str] = field(default_factory=set)
    high_risk_tools: set[str] = field(default_factory=set)
    allow_autorun_low_risk: bool = True
    max_auto_risk: str = "low"

    def to_dict(self) -> dict[str, Any]:
        return {
            "require_confirmation_for": sorted(self.require_confirmation_for),
            "blocked_tools": sorted(self.blocked_tools),
            "high_risk_tools": sorted(self.high_risk_tools),
            "allow_autorun_low_risk": self.allow_autorun_low_risk,
            "max_auto_risk": self.max_auto_risk,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "GovernancePolicy":
        data = dict(payload or {})
        return cls(
            require_confirmation_for={str(item) for item in data.get("require_confirmation_for", [])},
            blocked_tools={str(item) for item in data.get("blocked_tools", [])},
            high_risk_tools={str(item) for item in data.get("high_risk_tools", [])},
            allow_autorun_low_risk=bool(data.get("allow_autorun_low_risk", True)),
            max_auto_risk=str(data.get("max_auto_risk", "low") or "low"),
        )


@dataclass(slots=True)
class GovernanceVerdict:
    decision: str
    risk_level: str
    reasons: list[str] = field(default_factory=list)
    required_confirmations: list[str] = field(default_factory=list)
    blocked_tools: list[str] = field(default_factory=list)
    tool_names: list[str] = field(default_factory=list)
    summary: str = ""

    @property
    def allowed(self) -> bool:
        return self.decision in {"allow", "confirm"}

    @property
    def needs_confirmation(self) -> bool:
        return self.decision == "confirm"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class LedgerEntry:
    entry_id: str
    event_type: str
    subject_id: str
    payload: dict[str, Any]
    created_at: str = field(default_factory=utc_now)
    previous_hash: str = ""
    entry_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def new(cls, *, event_type: str, subject_id: str, payload: dict[str, Any], previous_hash: str = "") -> "LedgerEntry":
        entry = cls(
            entry_id=f"ledger_{uuid.uuid4().hex[:12]}",
            event_type=event_type,
            subject_id=subject_id,
            payload=dict(payload),
            previous_hash=previous_hash,
        )
        entry.entry_hash = hash_ledger_entry(entry)
        return entry

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "LedgerEntry":
        data = dict(payload or {})
        return cls(
            entry_id=str(data["entry_id"]),
            event_type=str(data["event_type"]),
            subject_id=str(data["subject_id"]),
            payload=dict(data.get("payload", {}) or {}),
            created_at=str(data.get("created_at", utc_now())),
            previous_hash=str(data.get("previous_hash", "") or ""),
            entry_hash=str(data.get("entry_hash", "") or ""),
        )


@dataclass(slots=True)
class LedgerReplayResult:
    valid: bool
    entries_checked: int
    broken_entry_ids: list[str] = field(default_factory=list)
    last_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class GovernanceEngine:
    def __init__(self, policy: GovernancePolicy | None = None) -> None:
        self.policy = policy or GovernancePolicy()

    def evaluate_plan(self, plan: TaskPlan, *, memory_verdict: dict[str, Any] | None = None) -> GovernanceVerdict:
        tool_names = [step.tool_name for step in plan.steps]
        blocked = sorted(set(tool_names) & self.policy.blocked_tools)
        reasons: list[str] = []
        confirmations: list[str] = []
        risk_level = "low"

        for tool_name in tool_names:
            lowered = tool_name.lower()
            if tool_name in self.policy.high_risk_tools or any(term in lowered for term in ("delete", "send", "pay", "purchase", "external")):
                risk_level = _max_risk(risk_level, "high")
            elif any(term in lowered for term in ("write", "draft", "update", "move", "organize")):
                risk_level = _max_risk(risk_level, "medium")
            if _requires_confirmation(tool_name, self.policy):
                confirmations.append(tool_name)

        memory = dict(memory_verdict or {})
        if memory.get("warnings"):
            risk_level = _max_risk(risk_level, "medium")
            reasons.append("memory warnings present")
        if blocked:
            return GovernanceVerdict("block", "critical", reasons + ["blocked tool requested"], confirmations, blocked, tool_names, "Blocked because a requested tool is not allowed.")
        max_auto = self.policy.max_auto_risk
        if confirmations or not self.policy.allow_autorun_low_risk or RISK_RANK.get(risk_level, 1) > RISK_RANK.get(max_auto, 1):
            if confirmations:
                reasons.append("confirmation required for requested tool")
            if RISK_RANK.get(risk_level, 1) > RISK_RANK.get(max_auto, 1):
                reasons.append("risk exceeds automatic-run threshold")
            return GovernanceVerdict("confirm", risk_level, reasons, sorted(set(confirmations)), [], tool_names, "Confirmation is required before continuing.")
        return GovernanceVerdict("allow", risk_level, reasons or ["low risk plan"], [], [], tool_names, "Allowed to continue.")

    def evaluate_checkpoint(self, checkpoint: ExecutionCheckpoint) -> GovernanceVerdict:
        return self.evaluate_plan(checkpoint.plan, memory_verdict=checkpoint.memory_bundle.get("memory_verdict"))


def build_execution_ledger(
    *,
    checkpoint: ExecutionCheckpoint | None = None,
    plan: TaskPlan | None = None,
    verdict: GovernanceVerdict | None = None,
    execution: WorkflowExecutionResult | None = None,
) -> list[LedgerEntry]:
    entries: list[LedgerEntry] = []
    previous = ""
    if checkpoint is not None:
        entry = LedgerEntry.new(event_type="checkpoint", subject_id=checkpoint.checkpoint_id, payload=checkpoint.to_dict(), previous_hash=previous)
        entries.append(entry)
        previous = entry.entry_hash
    if plan is not None:
        entry = LedgerEntry.new(event_type="plan", subject_id=checkpoint.checkpoint_id if checkpoint else "plan", payload=plan.to_dict(), previous_hash=previous)
        entries.append(entry)
        previous = entry.entry_hash
    if verdict is not None:
        entry = LedgerEntry.new(event_type="governance_verdict", subject_id=checkpoint.checkpoint_id if checkpoint else "verdict", payload=verdict.to_dict(), previous_hash=previous)
        entries.append(entry)
        previous = entry.entry_hash
    if execution is not None:
        entry = LedgerEntry.new(event_type="execution_result", subject_id=execution.workflow_id, payload=execution.to_dict(), previous_hash=previous)
        entries.append(entry)
    return entries


def replay_ledger(entries: list[LedgerEntry]) -> LedgerReplayResult:
    previous = ""
    broken: list[str] = []
    for entry in entries:
        expected = hash_ledger_entry(entry, override_hash="")
        if entry.previous_hash != previous or entry.entry_hash != expected:
            broken.append(entry.entry_id)
        previous = entry.entry_hash
    return LedgerReplayResult(valid=not broken, entries_checked=len(entries), broken_entry_ids=broken, last_hash=previous)


def serialize_ledger(entries: list[LedgerEntry]) -> str:
    return "\n".join(json.dumps(entry.to_dict(), ensure_ascii=False, sort_keys=True) for entry in entries) + ("\n" if entries else "")


def parse_ledger(content: str) -> list[LedgerEntry]:
    return [LedgerEntry.from_dict(json.loads(line)) for line in content.splitlines() if line.strip()]


def hash_ledger_entry(entry: LedgerEntry, *, override_hash: str | None = None) -> str:
    payload = entry.to_dict()
    payload["entry_hash"] = "" if override_hash is None else override_hash
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _requires_confirmation(tool_name: str, policy: GovernancePolicy) -> bool:
    lowered = tool_name.lower()
    return any(term in lowered for term in policy.require_confirmation_for)


def _max_risk(left: str, right: str) -> str:
    return left if RISK_RANK.get(left, 0) >= RISK_RANK.get(right, 0) else right
