"""Reference provider: Claude Agent SDK.

Adapts SDK stream events to the normalized AgentEvent model. Framework-specific
code must not leak beyond this module.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from atlas.events import AgentEvent, EventType


class ClaudeProvider:
    name = "claude"

    async def run(
        self,
        task_id: str,
        system_prompt: str,
        goal: str,
        tools: list[dict[str, Any]],
        context: str,
    ) -> AsyncIterator[AgentEvent]:
        try:
            from claude_agent_sdk import ClaudeAgentOptions, query
        except ImportError as exc:  # pragma: no cover
            yield AgentEvent(
                type=EventType.ERROR,
                task_id=task_id,
                payload={"error": f"claude-agent-sdk not installed: {exc}"},
            )
            return

        options = ClaudeAgentOptions(system_prompt=system_prompt)
        prompt = f"{context}\n\n# Goal\n{goal}" if context else goal

        async for message in query(prompt=prompt, options=options):
            for event in _normalize(task_id, message):
                yield event
        yield AgentEvent(type=EventType.DONE, task_id=task_id)


def _normalize(task_id: str, message: Any) -> list[AgentEvent]:
    """Map an SDK message to zero or more normalized events."""
    events: list[AgentEvent] = []
    for block in getattr(message, "content", []) or []:
        if getattr(block, "text", None):
            events.append(
                AgentEvent(
                    type=EventType.MESSAGE_DELTA,
                    task_id=task_id,
                    agent="claude",
                    payload={"text": block.text},
                )
            )
        elif getattr(block, "name", None):
            events.append(
                AgentEvent(
                    type=EventType.TOOL_CALL,
                    task_id=task_id,
                    agent="claude",
                    payload={"tool": block.name, "input": getattr(block, "input", {})},
                )
            )
    return events
