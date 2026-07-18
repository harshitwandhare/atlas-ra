"""End-to-end: real ledger + skills + API + WebSocket, FakeProvider only. No network."""

from __future__ import annotations

from fastapi.testclient import TestClient

from tests.conftest import FakeProvider
from tests.test_api import wait_for_state

SD_SKILL = (
    "---\nname: streamdiffusion-windows-install\nversion: 1.2.0\n"
    "triggers: streamdiffusion, stream diffusion\n---\n"
    "Pin torch 2.1.2+cu121 BEFORE installing streamdiffusion."
)


def test_full_pipeline_goal_to_done_with_skill_injection(make_app):
    fake = FakeProvider()
    api_main, _ = make_app(provider=fake, skill_files={"sd.md": SD_SKILL})

    with TestClient(api_main.app) as client:
        with client.websocket_connect("/ws") as ws:
            # 1. Submit through the public API, exactly as the dashboard does.
            task_id = client.post(
                "/goals", json={"goal": "Install StreamDiffusion and run a smoke test"}
            ).json()["task_id"]

            # 2. Task completes: routed to systems, critic-approved.
            task = wait_for_state(client, task_id, "done")
            assert task["team"] == "systems"

            # 3. Procedural memory reached the provider: skill body was in context.
            assert "Pin torch 2.1.2+cu121" in fake.calls[0]["context"]

            # 4. Episodic memory: every event was journaled to the steps table.
            steps = api_main.ledger._conn.execute(
                "SELECT type FROM steps WHERE task_id=? ORDER BY id", (task_id,)
            ).fetchall()
            assert [s[0] for s in steps][-1] == "done"

            # 5. The WebSocket bus streamed the lifecycle to the dashboard.
            states = []
            for _ in range(30):
                event = ws.receive_json()
                if event.get("type") == "task_state":
                    states.append(event["payload"]["state"])
                if "done" in states:
                    break
            assert states[0] == "running" and states[-1] == "done"

        # 6. The REST surface agrees with the ledger.
        listing = client.get("/tasks").json()
        assert listing[0]["id"] == task_id and listing[0]["state"] == "done"
