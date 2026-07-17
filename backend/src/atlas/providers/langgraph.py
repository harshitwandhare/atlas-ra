"""LangGraph provider: vendor-neutral graph runtime behind the same protocol.

Builds a minimal ReAct-style graph. Optional dependency — module imports lazily
so the rest of ATLAS never requires langgraph to be installed.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from atlas.events import AgentEvent, EventType


class LangGraphProvider:
    name = "langgraph"

    def __init__(self, model: str = "anthropic:claude-sonnet-4-5") -> None:
        self._model = model

    async def run(
        self,
        task_id: str,
        system_prompt: str,
        goal: str,
        tools: list[dict[str, Any]],
        context: str,
    ) -> AsyncIterator[AgentEvent]:
        try:
            from langchain.chat_models import init_chat_model
            from langgraph.prebuilt import create_react_agent
        except ImportError as exc:
            yield AgentEvent(
                type=EventType.ERROR, task_id=task_id, agent="langgraph",
                payload={"error": f"pip install langgraph langchain: {exc}"},
            )
            return

        agent = create_react_agent(
            model=init_chat_model(self._model), tools=[], prompt=system_prompt
        )
        prompt = f"{context}\n\n# Goal\n{goal}" if context else goal
        async for chunk in agent.astream({"messages": [("user", prompt)]}, stream_mode="values"):
            message = chunk["messages"][-1]
            if getattr(message, "content", None):
                yield AgentEvent(
                    type=EventType.MESSAGE_DELTA, task_id=task_id,
                    agent="langgraph", payload={"text": str(message.content)},
                )
        yield AgentEvent(type=EventType.DONE, task_id=task_id, agent="langgraph")
