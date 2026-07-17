"""Procedure extractor: turn tutorial transcripts/docs into draft skill playbooks.

Heuristic pass runs everywhere; when a provider is configured, an LLM pass
rewrites the draft into a proper playbook (same format as skills/*.md).
Drafts are never auto-promoted — a human reviews the skill PR.
"""

from __future__ import annotations

import re

_IMPERATIVE = re.compile(
    r"^\s*(?:\d+[.)]\s*)?(install|download|clone|run|open|create|set|add|enable|"
    r"copy|paste|select|click|type|launch|configure|pip|git|python|npm)\b",
    re.IGNORECASE,
)


def extract_procedure(text: str, min_steps: int = 3) -> str | None:
    """Extract ordered imperative steps; returns a draft playbook or None."""
    steps = []
    for line in text.splitlines():
        clean = re.sub(r"<[^>]+>", "", line).strip()  # strip srt/html tags
        if _IMPERATIVE.match(clean) and len(clean) > 12:
            steps.append(clean.rstrip("."))
    if len(steps) < min_steps:
        return None
    numbered = "\n".join(f"{i + 1}. {s}" for i, s in enumerate(dict.fromkeys(steps)))
    return (
        "---\nname: DRAFT-extracted-procedure\nversion: 0.0.1\ntriggers: \n---\n"
        "# DRAFT procedure (extracted; requires human review)\n\n" + numbered
    )
