"""Local-model provider via the Ollama HTTP API. Zero-cost, fully offline runs.

Simpler agent loop than the Claude provider (no native tool orchestration);
suitable for drafting, summarization, and Critic duty on local models.
"""

from __future__ import annotations

import json
import urllib.request
from collections.abc import AsyncIterator
from typing import Any

from atlas.events import AgentEvent, EventType


class OllamaProvider:
    name = "ollama"

    def __init__(self, model: str = "llama3.1", base_url: str = "http://localhost:11434") -> None:
        self._model = model
        self._base = base_url

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
        try:
            with urllib.request.urlopen(req, timeout=600) as resp:
                text = json.loads(resp.read())["response"]
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
