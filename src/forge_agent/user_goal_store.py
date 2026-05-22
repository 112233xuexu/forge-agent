from __future__ import annotations

from pathlib import Path
from typing import Any

from .session_state import StateStore
from .skill_lifecycle import SkillLibrary, TaskTrace


class UserGoalStore:
    """Persistence helper for plain user-goal learning.

    It stores successful task traces and the reusable skill library through the
    RC10 StateStore document layer. This keeps the user-facing path simple while
    letting repeated successful work become reusable later.
    """

    def __init__(self, path: str | Path | StateStore) -> None:
        self.state = path if isinstance(path, StateStore) else StateStore(path)
        self._owns_state = not isinstance(path, StateStore)

    def close(self) -> None:
        if self._owns_state:
            self.state.close()

    def load_skills(self) -> SkillLibrary:
        return self.state.load_skill_library(key="user_goals")

    def save_skills(self, library: SkillLibrary) -> None:
        self.state.save_skill_library(library, key="user_goals")

    def append_trace(self, trace: TaskTrace) -> None:
        self.state.upsert_document("user_goal_trace", trace.trace_id, trace.to_dict())

    def list_traces(self, *, goal_key: str | None = None) -> list[TaskTrace]:
        traces = [TaskTrace.from_dict(item) for item in self.state.list_documents("user_goal_trace")]
        if goal_key is not None:
            traces = [trace for trace in traces if trace.goal_key == goal_key]
        traces.sort(key=lambda item: item.created_at)
        return traces

    def to_status(self) -> dict[str, Any]:
        skills = self.load_skills().list()
        traces = self.list_traces()
        return {"skill_count": len(skills), "trace_count": len(traces)}
