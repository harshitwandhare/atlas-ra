"""CLI: python -m evals.run_evals  (offline mode scores skill routing + static checks)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from evals.harness import BASELINE, load_cases, record, score_skill_match  # noqa: E402


def main() -> int:
    skills_dir = str(Path(__file__).resolve().parents[2] / "skills")
    scores = {
        case.name: score_skill_match(case.goal, skills_dir) for case in load_cases()
    }
    mean = record("offline", scores)
    print(f"eval mean={mean:.3f} baseline={BASELINE} scores={scores}")
    return 0 if mean >= BASELINE else 1


if __name__ == "__main__":
    raise SystemExit(main())
