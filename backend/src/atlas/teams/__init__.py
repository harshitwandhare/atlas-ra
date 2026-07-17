"""Team protocol shared by systems/research/ops so the orchestrator can be typed
against a single interface instead of three unrelated classes."""

from __future__ import annotations

from typing import Any, Protocol


class Team(Protocol):
    name: str
    system_prompt: str
    tools: list[dict[str, Any]]
