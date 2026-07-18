"""API gateway: REST endpoints against a FakeProvider-wired app."""

from __future__ import annotations

import asyncio
import time

from fastapi.testclient import TestClient

SKILL = "---\nname: demo\nversion: 1.0.0\ntriggers: demo\n---\nDemo body."


def wait_for_state(client: TestClient, task_id: str, state: str, timeout: float = 5.0) -> dict:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        task = client.get(f"/tasks/{task_id}").json()
        if task.get("state") == state:
            return task
        time.sleep(0.02)
    raise AssertionError(f"task {task_id} never reached {state}: {task}")


def test_submit_goal_and_lifecycle(make_app):
    api_main, fake = make_app()
    with TestClient(api_main.app) as client:
        resp = client.post("/goals", json={"goal": "Install StreamDiffusion"})
        assert resp.status_code == 200
        task_id = resp.json()["task_id"]

        task = wait_for_state(client, task_id, "done")
        assert task["team"] == "systems"
        assert "Smoke test passed" in task["result"]

        listing = client.get("/tasks").json()
        assert any(t["id"] == task_id for t in listing)


def test_get_unknown_task(make_app):
    api_main, _ = make_app()
    with TestClient(api_main.app) as client:
        assert client.get("/tasks/doesnotexist").json() == {"error": "not found"}


def test_skills_endpoint_lists_seeded_skill(make_app):
    api_main, _ = make_app(skill_files={"demo.md": SKILL})
    with TestClient(api_main.app) as client:
        skills = client.get("/skills").json()
        assert [s["name"] for s in skills] == ["demo"]
        assert skills[0]["triggers"] == ["demo"]


def test_approvals_roundtrip(make_app):
    api_main, _ = make_app()
    request_id = asyncio.run(
        api_main.approvals.request("delete_path", {"path": "C:/tmp/x"})
    )
    with TestClient(api_main.app) as client:
        pending = client.get("/approvals").json()
        assert pending[0]["id"] == request_id
        assert pending[0]["state"] == "pending"

        resolved = client.post(f"/approvals/{request_id}", json={"approved": True}).json()
        assert resolved["state"] == "approved"

        assert client.get("/approvals").json()[0]["state"] == "approved"


def test_ingest_endpoint_text_file(make_app, tmp_path, monkeypatch):
    api_main, _ = make_app()
    monkeypatch.chdir(tmp_path)
    source = tmp_path / "notes.txt"
    source.write_text("Wan 2.2 fits in 10GB with the 5B model.", encoding="utf-8")

    with TestClient(api_main.app) as client:
        result = client.post("/ingest", json={"source": str(source)}).json()
        assert result["chars"] > 0 and "id" in result


def test_websocket_receives_task_events(make_app):
    api_main, _ = make_app()
    with TestClient(api_main.app) as client:
        with client.websocket_connect("/ws") as ws:
            task_id = client.post("/goals", json={"goal": "stream me"}).json()["task_id"]
            wait_for_state(client, task_id, "done")

            seen_states = []
            for _ in range(20):
                event = ws.receive_json()
                if event.get("type") == "task_state":
                    seen_states.append(event["payload"]["state"])
                if "done" in seen_states:
                    break
            assert "done" in seen_states
