"""Provider protocol — the only surface the rest of ATLAS may depend on (ADR-0001)."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any, Protocol, runtime_checkable

from atlas.events import AgentEvent


@runtime_checkable
class AgentProvider(Protocol):
    """Any agent framework adapted to ATLAS implements this."""

    name: str

    def run(
        self,
        task_id: str,
        system_prompt: str,
        goal: str,
        tools: list[dict[str, Any]],
        context: str,
    ) -> AsyncIterator[AgentEvent]:
        """Execute a task, yielding normalized events until DONE or ERROR."""
        ...
