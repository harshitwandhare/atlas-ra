"""Shared test fixtures: scripted FakeProvider, event-sink spy, and API app factory."""

from __future__ import annotations

import asyncio
import importlib
from collections.abc import AsyncIterator, Callable
from typing import Any

import pytest

from atlas.events import AgentEvent, EventType

Script = list[tuple[EventType, dict[str, Any]]]

SUCCESS_SCRIPT: Script = [
    (EventType.MESSAGE_DELTA, {"text": "Installed and verified. Smoke test passed."}),
    (EventType.DONE, {}),
]


class FakeProvider:
    """AgentProvider double that replays one scripted event list per run() call.

    If run() is called more times than there are scripts, the last script repeats.
    Every call's kwargs are recorded in ``calls`` for assertions.
    """

    name = "fake"

    def __init__(self, scripts: list[Script] | None = None) -> None:
        self.scripts: list[Script] = scripts if scripts else [SUCCESS_SCRIPT]
        self.calls: list[dict[str, Any]] = []

    async def run(
        self,
        task_id: str,
        system_prompt: str,
        goal: str,
        tools: list[dict[str, Any]],
        context: str,
    ) -> AsyncIterator[AgentEvent]:
        self.calls.append(
            {
                "task_id": task_id,
                "system_prompt": system_prompt,
                "goal": goal,
                "tools": tools,
                "context": context,
            }
        )
        script = self.scripts[min(len(self.calls) - 1, len(self.scripts) - 1)]
        for event_type, payload in script:
            yield AgentEvent(type=event_type, task_id=task_id, agent="fake", payload=payload)


class SinkSpy:
    """Async event sink that records every AgentEvent passed to it."""

    def __init__(self) -> None:
        self.events: list[AgentEvent] = []

    async def __call__(self, event: AgentEvent) -> None:
        self.events.append(event)

    def of_type(self, event_type: EventType) -> list[AgentEvent]:
        return [e for e in self.events if e.type == event_type]

    def state_sequence(self) -> list[Any]:
        return [e.payload["state"] for e in self.of_type(EventType.TASK_STATE)]


async def poll_until(predicate: Callable[[], bool], timeout: float = 3.0) -> bool:
    """Poll a predicate until true, yielding to the event loop; no long sleeps."""
    loop = asyncio.get_event_loop()
    deadline = loop.time() + timeout
    while loop.time() < deadline:
        if predicate():
            return True
        await asyncio.sleep(0.01)
    return predicate()


@pytest.fixture
def make_app(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> Any:
    """Build a fresh atlas.api.main module wired to tmp paths and a FakeProvider.

    Returns (api_main_module, fake_provider). The module-level singletons (ledger,
    skills, orchestrator, bus, approvals) are recreated per call via importlib.reload.
    """

    def _make(
        provider: FakeProvider | None = None,
        skill_files: dict[str, str] | None = None,
    ) -> tuple[Any, FakeProvider]:
        from atlas.config import settings

        skills_dir = tmp_path / "skills"
        skills_dir.mkdir(exist_ok=True)
        for fname, content in (skill_files or {}).items():
            (skills_dir / fname).write_text(content, encoding="utf-8")

        monkeypatch.setattr(settings, "db_path", str(tmp_path / "atlas-test.db"))
        monkeypatch.setattr(settings, "skills_dir", str(skills_dir))

        import atlas.orchestrator.core as core

        fake = provider if provider is not None else FakeProvider()
        monkeypatch.setattr(core, "get_provider", lambda name: fake)

        import atlas.api.main as api_main

        api_main = importlib.reload(api_main)
        return api_main, fake

    return _make
