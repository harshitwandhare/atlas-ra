"""FastAPI gateway: REST for goals/tasks/skills + WebSocket event bus."""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from atlas.config import settings
from atlas.executors.approvals import ApprovalQueue
from atlas.events import AgentEvent
from atlas.memory import Ledger, SkillStore
from atlas.orchestrator import Orchestrator


class Bus:
    """Fan-out of AgentEvents to all connected dashboard clients."""

    def __init__(self) -> None:
        self._clients: set[WebSocket] = set()

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self._clients.add(ws)

    def disconnect(self, ws: WebSocket) -> None:
        self._clients.discard(ws)

    async def publish(self, event: AgentEvent) -> None:
        dead = []
        for ws in self._clients:
            try:
                await ws.send_text(event.model_dump_json())
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)


bus = Bus()
approvals = ApprovalQueue()
ledger = Ledger(settings.db_path)
skills = SkillStore(settings.skills_dir)
orchestrator = Orchestrator(ledger, skills, bus.publish)


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[no-untyped-def]
    yield


app = FastAPI(title="ATLAS", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware, allow_origins=["http://localhost:3000"],
    allow_methods=["*"], allow_headers=["*"],
)


class GoalIn(BaseModel):
    goal: str


@app.post("/goals")
async def submit_goal(body: GoalIn) -> dict[str, str]:
    task_id = await orchestrator.submit_goal(body.goal)
    return {"task_id": task_id}


@app.get("/tasks")
async def list_tasks() -> list[dict[str, Any]]:
    return [t.model_dump() for t in ledger.list_tasks()]


@app.get("/tasks/{task_id}")
async def get_task(task_id: str) -> dict[str, Any]:
    task = ledger.get_task(task_id)
    return task.model_dump() if task else {"error": "not found"}


@app.get("/skills")
async def list_skills() -> list[dict[str, Any]]:
    return [s.model_dump() for s in skills.load_all()]


@app.get("/approvals")
async def list_approvals() -> list[dict[str, Any]]:
    return [r.model_dump() for r in approvals.all()]


class ApprovalDecision(BaseModel):
    approved: bool


@app.post("/approvals/{request_id}")
async def decide_approval(request_id: str, body: ApprovalDecision) -> dict[str, Any]:
    return approvals.resolve(request_id, body.approved).model_dump()


class IngestIn(BaseModel):
    source: str


@app.post("/ingest")
async def ingest_source(body: IngestIn) -> dict[str, Any]:
    from atlas.ingest import ingest
    from atlas.memory.semantic import SemanticStore

    store = SemanticStore(".atlas_semantic")
    doc = ingest(body.source, store)
    return {"id": doc.id, "chars": len(doc.text), "procedure_draft": "procedure_draft" in doc.meta}


@app.websocket("/ws")
async def ws_events(ws: WebSocket) -> None:
    await bus.connect(ws)
    try:
        while True:
            await asyncio.sleep(30)
            await ws.send_text('{"type":"ping"}')
    except WebSocketDisconnect:
        bus.disconnect(ws)
