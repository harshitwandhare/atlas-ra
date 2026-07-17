"""Research team: web browsing, paper/tutorial ingestion, knowledge distillation."""

from __future__ import annotations

from typing import Any

SYSTEM_PROMPT = """\
You are the ATLAS Research Team. You gather, verify, and distill knowledge for a
Generative-AI research assistant working on real-time diffusion, ComfyUI, LoRA
training, video models, and TouchDesigner.

Rules:
1. Prefer primary sources (papers, official repos/docs) over blog summaries.
2. Every claim you store must carry its source URL.
3. Route tutorials (video/pdf/pptx) through the ingest pipeline so procedures are
   extracted into draft skills.
4. Summarize into semantic memory — dense, factual, no filler.
"""


class ResearchTeam:
    name = "research"
    system_prompt = SYSTEM_PROMPT
    tools: list[dict[str, Any]] = [
        {"name": "browser", "tier": 3, "risk": "safe"},
        {"name": "ingest_source", "tier": 1, "risk": "safe"},
        {"name": "search_memory", "tier": 1, "risk": "safe"},
    ]
