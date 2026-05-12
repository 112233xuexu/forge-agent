from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json
import re
import uuid


@dataclass
class GeneratedArtifact:
    artifact_id: str
    kind: str
    title: str
    path: str
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ContentPack:
    """Local content-generation skill packs for ordinary users.

    v1.6-v1.8 provide deterministic, offline artifacts first. Later versions can
    connect model providers, slide renderers, TTS, FFmpeg, and web search.
    """

    def __init__(self, workspace: str | Path = ".forge-agent") -> None:
        self.workspace = Path(workspace)
        self.artifacts_dir = self.workspace / "artifacts"

    def make_ppt_outline(self, topic: str) -> GeneratedArtifact:
        title = topic.strip() or "Untitled Presentation"
        slides = [
            ("Title", title),
            ("Problem", f"What problem does {title} solve?"),
            ("Audience", "Who needs this and why now?"),
            ("Solution", "Core idea, workflow, and user value."),
            ("Demo", "Show the simplest end-to-end path."),
            ("Next Steps", "Roadmap, validation, and release plan."),
        ]
        content = "# PPT Outline: " + title + "\n\n" + "\n\n".join(f"## Slide {idx}: {name}\n\n{body}" for idx, (name, body) in enumerate(slides, start=1)) + "\n"
        return self._write("ppt", title, content, suffix="md", metadata={"slides": len(slides)})

    def make_report(self, topic: str) -> GeneratedArtifact:
        title = topic.strip() or "Untitled Report"
        content = f"# Report: {title}\n\n## Executive Summary\n\nSummarize the goal, current evidence, and recommended decision.\n\n## Findings\n\n- Key finding 1\n- Key finding 2\n- Key finding 3\n\n## Risks\n\n- What can go wrong?\n- What needs approval?\n- What can be rolled back?\n\n## Next Actions\n\n1. Validate inputs.\n2. Run a dry-run.\n3. Approve execution if the plan is safe.\n4. Record evidence.\n"
        return self._write("report", title, content, suffix="md")

    def make_news_brief(self, topic: str) -> GeneratedArtifact:
        title = topic.strip() or "Daily Brief"
        content = f"# News Brief: {title}\n\n> Offline draft brief. Connect web/news sources in a later release before using this as a live-news product.\n\n## What to monitor\n\n- Major announcements\n- Product releases\n- Security or policy changes\n- Funding and ecosystem signals\n\n## Briefing Template\n\n1. Top story\n2. Why it matters\n3. Who is affected\n4. What to watch next\n5. Source links and confidence\n"
        return self._write("news", title, content, suffix="md", metadata={"live_sources": False})

    def make_storyboard(self, topic: str) -> GeneratedArtifact:
        title = topic.strip() or "Untitled Video"
        content = f"# Video Storyboard: {title}\n\n## 30-second structure\n\n| Time | Visual | Voiceover | Notes |\n|---|---|---|---|\n| 0-5s | Hook/problem | Start with the pain point. | Use a clear title card. |\n| 5-12s | Current workflow | Show the old/manual way. | Make friction obvious. |\n| 12-22s | Forge workflow | Show command, preview, approval, result. | Keep it simple. |\n| 22-28s | Evidence | Show manifest/history/rollback. | Build trust. |\n| 28-30s | CTA | Try the demo or read the README. | End cleanly. |\n\n## Asset checklist\n\n- Screen recording\n- Logo/title card\n- Captions\n- Voiceover script\n- Background music optional\n"
        return self._write("storyboard", title, content, suffix="md")

    def _write(self, kind: str, title: str, content: str, *, suffix: str, metadata: dict[str, Any] | None = None) -> GeneratedArtifact:
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        artifact_id = str(uuid.uuid4())
        safe_title = re.sub(r"[^a-zA-Z0-9_.-]+", "-", title.lower()).strip("-") or kind
        path = self.artifacts_dir / f"{kind}-{safe_title}-{artifact_id[:8]}.{suffix}"
        path.write_text(content, encoding="utf-8")
        index = self.artifacts_dir / "index.jsonl"
        artifact = GeneratedArtifact(artifact_id=artifact_id, kind=kind, title=title, path=str(path), metadata=metadata or {})
        with index.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(artifact.to_dict(), ensure_ascii=False) + "\n")
        return artifact
