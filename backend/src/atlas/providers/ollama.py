"""Local-model provider via the Ollama HTTP API. Zero-cost, fully offline runs.

Simpler agent loop than the Claude provider (no native tool orchestration);
suitable for drafting, summarization, and Critic duty on local models.
"""

from __future__ import annotations

import asyncio
import json
import urllib.request
from collections.abc import AsyncIterator
from typing import Any

from atlas.events import AgentEvent, EventType


class OllamaProvider:
    name = "ollama"

    def __init__(self, model: str | None = None, base_url: str | None = None) -> None:
        from atlas.config import settings

        self._model = model if model is not None else settings.ollama_model
        self._base = base_url if base_url is not None else settings.ollama_base_url

    async def run(
        self,
        task_id: str,
        system_prompt: str,
        goal: str,
        tools: list[dict[str, Any]],
        context: str,
    ) -> AsyncIterator[AgentEvent]:
        prompt = f"{context}\n\n# Goal\n{goal}" if context else goal
        body = json.dumps(
            {
                "model": self._model,
                "system": system_prompt,
                "prompt": prompt,
                "stream": False,
            }
        ).encode()
        req = urllib.request.Request(
            f"{self._base}/api/generate", data=body,
            headers={"Content-Type": "application/json"},
        )
        def _blocking_call() -> str:
            with urllib.request.urlopen(req, timeout=600) as resp:
                return str(json.loads(resp.read())["response"])

        try:
            # Generation takes seconds-to-minutes; a blocking urlopen here would
            # freeze the whole event loop (API + dashboard) for that long.
            text = await asyncio.to_thread(_blocking_call)
            yield AgentEvent(
                type=EventType.MESSAGE_DELTA, task_id=task_id,
                agent="ollama", payload={"text": text},
            )
            yield AgentEvent(type=EventType.DONE, task_id=task_id, agent="ollama")
        except Exception as exc:
            yield AgentEvent(
                type=EventType.ERROR, task_id=task_id,
                agent="ollama", payload={"error": str(exc)},
            )
