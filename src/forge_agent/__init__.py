"""Forge Agent public package surface."""

from __future__ import annotations

__version__ = "1.0.0rc10"

from .desktop_adapter import DesktopAdapter, DesktopRequest, DesktopResponse
from .http_adapter import HttpAdapter, HttpRequestEnvelope, HttpResponseEnvelope
from .models import ExecutionCheckpoint, MemoryRecallHit, MessageRecord, SessionRecord, StepExecution, TaskPlan
from .planner import PlannerResult, SimplePlanner
from .runtime import ForgeRuntime, TaskResult
from .runtime_compat import CompatRuntime, RuntimeTurnResult
from .session_state import StateStore
from .tool_registry import RegisteredTool, ToolRegistry

__all__ = [
    "CompatRuntime",
    "DesktopAdapter",
    "DesktopRequest",
    "DesktopResponse",
    "ExecutionCheckpoint",
    "ForgeRuntime",
    "HttpAdapter",
    "HttpRequestEnvelope",
    "HttpResponseEnvelope",
    "MemoryRecallHit",
    "MessageRecord",
    "PlannerResult",
    "RegisteredTool",
    "RuntimeTurnResult",
    "SessionRecord",
    "SimplePlanner",
    "StateStore",
    "StepExecution",
    "TaskPlan",
    "TaskResult",
    "ToolRegistry",
    "__version__",
]
