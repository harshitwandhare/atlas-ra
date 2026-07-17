"""Eval harness: scored regression cases proving ATLAS improves across versions.

Each case is a YAML-ish markdown file in evals/cases/ with a goal and checks.
Scores are written to evals/results.jsonl — CI fails if the mean score regresses
below the recorded baseline.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

CASES_DIR = Path(__file__).parent / "cases"
RESULTS = Path(__file__).parent / "results.jsonl"
BASELINE = 0.6


@dataclass
class Case:
    name: str
    goal: str
    must_contain: list[str]
    must_not_contain: list[str]


def load_cases() -> list[Case]:
    cases = []
    for path in sorted(CASES_DIR.glob("*.md")):
        meta: dict[str, str] = {}
        for line in path.read_text(encoding="utf-8").splitlines():
            if ":" in line:
                key, _, value = line.partition(":")
                meta.setdefault(key.strip(), value.strip())
        cases.append(
            Case(
                name=path.stem,
                goal=meta.get("goal", ""),
                must_contain=[
                    s.strip() for s in meta.get("must_contain", "").split("|") if s.strip()
                ],
                must_not_contain=[
                    s.strip() for s in meta.get("must_not_contain", "").split("|") if s.strip()
                ],
            )
        )
    return cases


def score(case: Case, output: str) -> float:
    """Fraction of positive checks hit, zeroed if any negative check appears."""
    lowered = output.lower()
    if any(bad.lower() in lowered for bad in case.must_not_contain):
        return 0.0
    if not case.must_contain:
        return 1.0
    hits = sum(1 for req in case.must_contain if req.lower() in lowered)
    return hits / len(case.must_contain)


def score_skill_match(goal: str, skills_dir: str) -> float:
    """Offline eval: does the skill router surface the right playbook?"""
    from atlas.memory.procedural import SkillStore

    return 1.0 if SkillStore(skills_dir).match(goal) else 0.0


def record(version: str, scores: dict[str, float]) -> float:
    mean = sum(scores.values()) / max(len(scores), 1)
    with RESULTS.open("a", encoding="utf-8") as f:
        f.write(json.dumps({
            "version": version,
            "ts": datetime.now(timezone.utc).isoformat(),
            "mean": round(mean, 3),
            "scores": scores,
        }) + "\n")
    return mean


def strip_ansi(text: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", text)
