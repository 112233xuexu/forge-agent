from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json
import re
import uuid


@dataclass
class Skill:
    """A reusable capability discovered or created by Forge Agent."""

    skill_id: str
    name: str
    description: str
    triggers: list[str]
    steps: list[str]
    status: str = "draft"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    uses: int = 0
    success_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Skill":
        return cls(
            skill_id=str(data["skill_id"]),
            name=str(data["name"]),
            description=str(data.get("description", "")),
            triggers=[str(item) for item in data.get("triggers", [])],
            steps=[str(item) for item in data.get("steps", [])],
            status=str(data.get("status", "draft")),
            created_at=str(data.get("created_at", "")),
            updated_at=str(data.get("updated_at", data.get("created_at", ""))),
            uses=int(data.get("uses", 0)),
            success_count=int(data.get("success_count", 0)),
            metadata=dict(data.get("metadata", {})),
        )


class SkillStore:
    """Local skill library with automatic draft-skill creation.

    This is the first practical version of Forge Agent's key idea: the user
    should not have to install skills manually. The runtime searches local
    skills; when none match, it creates a readable draft skill that can be
    validated and reused later.
    """

    def __init__(self, workspace: str | Path) -> None:
        self.workspace = Path(workspace)
        self.skills_dir = self.workspace / "skills"
        self.index_path = self.skills_dir / "index.jsonl"

    def init(self) -> None:
        self.skills_dir.mkdir(parents=True, exist_ok=True)
        self.index_path.touch(exist_ok=True)

    def list(self) -> list[Skill]:
        if not self.index_path.exists():
            return []
        skills: list[Skill] = []
        for line in self.index_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                skills.append(Skill.from_dict(json.loads(line)))
            except (json.JSONDecodeError, KeyError, TypeError, ValueError):
                continue
        return skills

    def find(self, goal: str) -> Skill | None:
        goal_tokens = set(_tokenize(goal))
        if not goal_tokens:
            return None
        candidates: list[tuple[int, Skill]] = []
        for skill in self.list():
            searchable = " ".join([skill.name, skill.description, *skill.triggers])
            score = len(goal_tokens.intersection(_tokenize(searchable)))
            if score > 0 and skill.status in {"draft", "validated", "promoted"}:
                candidates.append((score, skill))
        if not candidates:
            return None
        candidates.sort(key=lambda item: (item[0], item[1].success_count, item[1].uses), reverse=True)
        return candidates[0][1]

    def get_or_create_for_goal(self, goal: str) -> tuple[Skill, bool]:
        existing = self.find(goal)
        if existing is not None:
            return existing, False
        return self.create_draft(goal), True

    def create_draft(self, goal: str) -> Skill:
        self.init()
        now = datetime.now(timezone.utc).isoformat()
        skill = Skill(
            skill_id=str(uuid.uuid4()),
            name=_name_from_goal(goal),
            description=f"Draft skill automatically created for goal: {goal.strip()}",
            triggers=_tokenize(goal)[:12],
            steps=[
                "Clarify the user's goal in ordinary language.",
                "Identify the safest local action that can move the goal forward.",
                "Ask for approval before any risky file, network, shell, or repository operation.",
                "Record evidence, result, and reusable lessons in the local workspace.",
            ],
            status="draft",
            created_at=now,
            updated_at=now,
            metadata={"source": "auto-created", "original_goal": goal.strip()},
        )
        self._upsert(skill)
        self._write_skill_file(skill)
        return skill

    def mark_used(self, skill_id: str, *, success: bool = False) -> Skill | None:
        skills = self.list()
        updated: Skill | None = None
        now = datetime.now(timezone.utc).isoformat()
        for skill in skills:
            if skill.skill_id == skill_id:
                skill.uses += 1
                if success:
                    skill.success_count += 1
                if skill.success_count >= 3 and skill.status == "draft":
                    skill.status = "validated"
                skill.updated_at = now
                updated = skill
        self._rewrite(skills)
        if updated is not None:
            self._write_skill_file(updated)
        return updated

    def _upsert(self, skill: Skill) -> None:
        skills = [existing for existing in self.list() if existing.skill_id != skill.skill_id]
        skills.append(skill)
        self._rewrite(skills)

    def _rewrite(self, skills: list[Skill]) -> None:
        self.init()
        with self.index_path.open("w", encoding="utf-8") as fh:
            for skill in skills:
                fh.write(json.dumps(skill.to_dict(), ensure_ascii=False) + "\n")

    def _write_skill_file(self, skill: Skill) -> None:
        safe_name = re.sub(r"[^a-zA-Z0-9_.-]+", "-", skill.name.lower()).strip("-") or "skill"
        path = self.skills_dir / f"{safe_name}-{skill.skill_id[:8]}.md"
        steps = "\n".join(f"{idx}. {step}" for idx, step in enumerate(skill.steps, start=1))
        path.write_text(
            f"# {skill.name}\n\n"
            f"Status: `{skill.status}`\n\n"
            f"Skill ID: `{skill.skill_id}`\n\n"
            f"## Description\n\n{skill.description}\n\n"
            f"## Triggers\n\n{', '.join(skill.triggers) or 'none'}\n\n"
            f"## Steps\n\n{steps}\n",
            encoding="utf-8",
        )


def _tokenize(text: str) -> list[str]:
    return [token.lower() for token in re.findall(r"[\w\u4e00-\u9fff]+", text) if len(token.strip()) >= 2]


def _name_from_goal(goal: str) -> str:
    tokens = _tokenize(goal)
    if not tokens:
        return "Untitled Skill"
    return " ".join(tokens[:6]).title()
