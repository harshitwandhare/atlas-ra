"""Orchestrator lifecycle: success, retry, escalation, crash containment, skills."""

from __future__ import annotations

from atlas.events import EventType
from atlas.memory import Ledger, SkillStore
from atlas.memory.episodic import TaskState
from atlas.orchestrator.core import Orchestrator
from tests.conftest import SUCCESS_SCRIPT, FakeProvider, SinkSpy, poll_until

ERROR_SCRIPT = [(EventType.ERROR, {"error": "boom"})]
BAD_TRANSCRIPT_SCRIPT = [
    (EventType.MESSAGE_DELTA, {"text": "tried but ended with an error"}),
    (EventType.DONE, {}),
]


def make_orchestrator(tmp_path, monkeypatch, provider):
    import atlas.orchestrator.core as core

    monkeypatch.setattr(core, "get_provider", lambda name: provider)
    ledger = Ledger(str(tmp_path / "test.db"))
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir(exist_ok=True)
    sink = SinkSpy()
    orch = Orchestrator(ledger, SkillStore(str(skills_dir)), sink)
    return orch, ledger, sink, skills_dir


async def test_success_lifecycle(tmp_path, monkeypatch):
    fake = FakeProvider()
    orch, ledger, sink, _ = make_orchestrator(tmp_path, monkeypatch, fake)

    task_id = await orch.submit_goal("Install StreamDiffusion")
    assert await poll_until(lambda: ledger.get_task(task_id).state == TaskState.DONE)

    states = sink.state_sequence()
    assert states == [TaskState.RUNNING, TaskState.REVIEW, TaskState.DONE]
    task = ledger.get_task(task_id)
    assert task.result and "Smoke test passed" in task.result
    assert len(fake.calls) == 1


async def test_provider_error_exhausts_retries_then_escalates(tmp_path, monkeypatch):
    fake = FakeProvider(scripts=[ERROR_SCRIPT])  # last script repeats every attempt
    orch, ledger, sink, _ = make_orchestrator(tmp_path, monkeypatch, fake)

    task_id = await orch.submit_goal("do something doomed")
    assert await poll_until(lambda: ledger.get_task(task_id).state == TaskState.ESCALATED)

    # max_retries=2 -> 3 attempts, each transitions to RUNNING, then final ESCALATED
    assert sink.state_sequence() == [TaskState.RUNNING] * 3 + [TaskState.ESCALATED]
    assert len(fake.calls) == 3
    assert ledger.get_task(task_id).result == "Retries exhausted"


async def test_critic_rejection_feeds_feedback_into_retry(tmp_path, monkeypatch):
    fake = FakeProvider(scripts=[BAD_TRANSCRIPT_SCRIPT, SUCCESS_SCRIPT])
    orch, ledger, _, _ = make_orchestrator(tmp_path, monkeypatch, fake)

    task_id = await orch.submit_goal("flaky first attempt")
    assert await poll_until(lambda: ledger.get_task(task_id).state == TaskState.DONE)

    assert len(fake.calls) == 2
    assert "Reviewer feedback" in fake.calls[1]["goal"]


async def test_provider_crash_is_contained_and_escalates(tmp_path, monkeypatch):
    class BoomProvider:
        name = "boom"

        async def run(self, task_id, system_prompt, goal, tools, context):
            raise RuntimeError("SDK exploded")
            yield  # pragma: no cover — makes this an async generator

    orch, ledger, sink, _ = make_orchestrator(tmp_path, monkeypatch, BoomProvider())

    task_id = await orch.submit_goal("crash me")
    assert await poll_until(lambda: ledger.get_task(task_id).state == TaskState.ESCALATED)

    errors = sink.of_type(EventType.ERROR)
    assert errors and "SDK exploded" in errors[0].payload["error"]
    assert "Unhandled error" in ledger.get_task(task_id).result


async def test_matching_skill_injected_into_context(tmp_path, monkeypatch):
    fake = FakeProvider()
    orch, ledger, _, skills_dir = make_orchestrator(tmp_path, monkeypatch, fake)
    (skills_dir / "sd.md").write_text(
        "---\nname: sd-install\nversion: 1.0.0\ntriggers: streamdiffusion\n---\n"
        "Use python 3.10 and install torch first.",
        encoding="utf-8",
    )

    task_id = await orch.submit_goal("Install StreamDiffusion on this box")
    assert await poll_until(lambda: ledger.get_task(task_id).state == TaskState.DONE)

    ctx = fake.calls[0]["context"]
    assert "sd-install" in ctx and "install torch first" in ctx


async def test_non_matching_skill_not_injected(tmp_path, monkeypatch):
    fake = FakeProvider()
    orch, ledger, _, skills_dir = make_orchestrator(tmp_path, monkeypatch, fake)
    (skills_dir / "other.md").write_text(
        "---\nname: other\nversion: 1.0.0\ntriggers: kubernetes\n---\nIrrelevant.",
        encoding="utf-8",
    )

    task_id = await orch.submit_goal("Install StreamDiffusion")
    assert await poll_until(lambda: ledger.get_task(task_id).state == TaskState.DONE)
    assert fake.calls[0]["context"] == ""


async def test_all_events_logged_to_ledger(tmp_path, monkeypatch):
    fake = FakeProvider()
    orch, ledger, _, _ = make_orchestrator(tmp_path, monkeypatch, fake)

    task_id = await orch.submit_goal("log everything")
    assert await poll_until(lambda: ledger.get_task(task_id).state == TaskState.DONE)

    rows = ledger._conn.execute(
        "SELECT type FROM steps WHERE task_id=? ORDER BY id", (task_id,)
    ).fetchall()
    types = [r[0] for r in rows]
    assert EventType.MESSAGE_DELTA in types and EventType.DONE in types


async def test_unknown_team_from_future_router_is_contained(tmp_path, monkeypatch):
    """A routing bug must escalate the task, not orphan it (supervision boundary)."""
    fake = FakeProvider()
    orch, ledger, sink, _ = make_orchestrator(tmp_path, monkeypatch, fake)
    monkeypatch.setattr(Orchestrator, "_route", staticmethod(lambda goal: "no-such-team"))

    task_id = await orch.submit_goal("anything")
    assert await poll_until(lambda: ledger.get_task(task_id).state == TaskState.ESCALATED)
    assert sink.of_type(EventType.ERROR)
