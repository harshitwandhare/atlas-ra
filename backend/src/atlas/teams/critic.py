"""Critic: verifies work before completion and distills skills from successes.

V1 ships a heuristic reviewer so the loop is real end-to-end; swapping in an
LLM-backed review is a provider call away (same interface).
"""

from __future__ import annotations

from pydantic import BaseModel


class Verdict(BaseModel):
    approved: bool
    summary: str = ""
    feedback: str = ""


class Critic:
    async def review(self, goal: str, transcript: str) -> Verdict:
        if not transcript.strip():
            return Verdict(approved=False, feedback="Empty transcript: no work was produced.")
        # Heuristic floor; replace with LLM review (see docs/ROADMAP.md).
        if "error" in transcript.lower()[-500:]:
            return Verdict(
                approved=False,
                feedback="Transcript ends with an error; resolve it and re-verify.",
            )
        return Verdict(approved=True, summary=transcript[-1000:])
