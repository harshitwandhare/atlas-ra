"""Orchestrator: decompose → route → supervise → verify → distill.

Owns the task lifecycle; all state transitions go through the ledger so the
dashboard and audit trail are always consistent.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Callable, Coroutine
from typing import Any

from atlas.config import settings
from atlas.events import AgentEvent, EventType
from atlas.memory import Ledger, SkillStore
from atlas.memory.episodic import TaskState
from atlas.observability import traced_event
from atlas.providers import get_provider
from atlas.teams import Team
from atlas.teams.critic import Critic
from atlas.teams.ops import OpsTeam
from atlas.teams.research import ResearchTeam
from atlas.teams.systems import SystemsTeam

EventSink = Callable[[AgentEvent], Coroutine[Any, Any, None]]


class Orchestrator:
    def __init__(self, ledger: Ledger, skills: SkillStore, sink: EventSink) -> None:
        self._ledger = ledger
        self._skills = skills
        self._sink = sink
        self._provider = get_provider(settings.provider)
        self._teams: dict[str, Team] = {
            "systems": SystemsTeam(),
            "research": ResearchTeam(),
            "ops": OpsTeam(),
        }
        self._critic = Critic()

    async def submit_goal(self, goal: str) -> str:
        """Create and run a task, routed to the best-matching team."""
        team_name = self._route(goal)
        task = self._ledger.create_task(goal=goal, team=team_name)
        asyncio.create_task(self._supervised_run(task.id, goal, team_name))
        return task.id

    async def _supervised_run(self, task_id: str, goal: str, team_name: str) -> None:
        """Containment boundary: a crash anywhere below must never orphan the task
        in RUNNING or escape the asyncio task as an unretrieved exception."""
        try:
            await self._run(task_id, goal, team_name)
        except Exception as exc:
            await self._sink(
                AgentEvent(
                    type=EventType.ERROR,
                    task_id=task_id,
                    payload={"error": f"{type(exc).__name__}: {exc}"},
                )
            )
            await self._transition(
                task_id, TaskState.ESCALATED, result=f"Unhandled error: {exc}"
            )

    @staticmethod
    def _route(goal: str) -> str:
        """Keyword router. V3: replace with LLM classification (same signature)."""
        lowered = goal.lower()
        research_hints = ("research", "find", "paper", "compare", "read", "summarize", "watch")
        ops_hints = (
            "install driver",
            "uninstall",
            "clean up",
            "organize files",
            "windows settings",
        )
        if any(hint in lowered for hint in ops_hints):
            return "ops"
        if any(hint in lowered for hint in research_hints):
            return "research"
        return "systems"

    async def _run(self, task_id: str, goal: str, team_name: str = "systems") -> None:
        team = self._teams[team_name]
        matched = self._skills.match(goal)
        context = "\n\n".join(f"# Skill: {s.name} v{s.version}\n{s.body}" for s in matched)

        for _attempt in range(settings.max_retries + 1):
            await self._transition(task_id, TaskState.RUNNING)
            transcript: list[str] = []
            failed = False

            events: AsyncIterator[AgentEvent] = self._provider.run(
                task_id=task_id,
                system_prompt=team.system_prompt,
                goal=goal,
                tools=team.tools,
                context=context,
            )
            async for event in events:
                with traced_event(event.type, task_id, event.agent):
                    self._ledger.log_step(task_id, event.type, event.payload)
                    await self._sink(event)
                if event.type == EventType.MESSAGE_DELTA:
                    transcript.append(str(event.payload.get("text", "")))
                elif event.type == EventType.ERROR:
                    failed = True

            if failed:
                continue  # retry

            await self._transition(task_id, TaskState.REVIEW)
            verdict = await self._critic.review(goal, "".join(transcript))
            if verdict.approved:
                await self._transition(task_id, TaskState.DONE, result=verdict.summary)
                return
            goal = f"{goal}\n\n# Reviewer feedback (address this):\n{verdict.feedback}"

        await self._transition(task_id, TaskState.ESCALATED, result="Retries exhausted")

    async def _transition(
        self, task_id: str, state: TaskState, result: str | None = None
    ) -> None:
        self._ledger.set_state(task_id, state, result)
        await self._sink(
            AgentEvent(
                type=EventType.TASK_STATE,
                task_id=task_id,
                payload={"state": state, "result": result},
            )
        )
