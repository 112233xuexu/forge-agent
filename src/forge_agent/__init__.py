"""Forge Agent public package surface."""

from __future__ import annotations

__version__ = "1.0.0rc10"

from .runtime import ForgeRuntime, TaskResult

__all__ = ["ForgeRuntime", "TaskResult", "__version__"]
