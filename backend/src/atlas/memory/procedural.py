"""Procedural memory: versioned skill playbooks — how ATLAS gets better over time."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel


class Skill(BaseModel):
    name: str
    version: str
    triggers: list[str]
    body: str


class SkillStore:
    """Loads markdown playbooks with YAML-ish front-matter from the skills directory."""

    def __init__(self, skills_dir: str) -> None:
        self._dir = Path(skills_dir)

    def load_all(self) -> list[Skill]:
        skills = []
        for path in sorted(self._dir.glob("*.md")):
            skill = self._parse(path)
            if skill:
                skills.append(skill)
        return skills

    def match(self, goal: str) -> list[Skill]:
        """Return skills whose triggers appear in the goal (case-insensitive)."""
        goal_lower = goal.lower()
        return [
            s for s in self.load_all()
            if any(t.lower() in goal_lower for t in s.triggers)
        ]

    @staticmethod
    def _parse(path: Path) -> Skill | None:
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---"):
            return None
        try:
            _, front, body = text.split("---", 2)
        except ValueError:
            return None
        meta: dict[str, str] = {}
        for line in front.strip().splitlines():
            if ":" in line:
                key, _, value = line.partition(":")
                meta[key.strip()] = value.strip()
        return Skill(
            name=meta.get("name", path.stem),
            version=meta.get("version", "0.1.0"),
            triggers=[t.strip() for t in meta.get("triggers", "").split(",") if t.strip()],
            body=body.strip(),
        )
