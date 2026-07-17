"""Episodic memory: the task ledger (SQLite). Single source of truth for all runs."""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel

_SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    goal TEXT NOT NULL,
    team TEXT NOT NULL,
    state TEXT NOT NULL,
    result TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL REFERENCES tasks(id),
    type TEXT NOT NULL,
    payload TEXT NOT NULL,
    ts TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_steps_task ON steps(task_id);
"""


class TaskState(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    RUNNING = "running"
    REVIEW = "review"
    DONE = "done"
    FAILED = "failed"
    BLOCKED = "blocked"
    ESCALATED = "escalated"


class Task(BaseModel):
    id: str
    goal: str
    team: str
    state: TaskState
    result: str | None = None
    created_at: str
    updated_at: str


class Ledger:
    """Append-only record of everything ATLAS does. Auditable by design."""

    def __init__(self, db_path: str) -> None:
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.executescript(_SCHEMA)

    def create_task(self, goal: str, team: str) -> Task:
        now = datetime.now(timezone.utc).isoformat()
        task = Task(
            id=uuid.uuid4().hex[:12], goal=goal, team=team,
            state=TaskState.PENDING, created_at=now, updated_at=now,
        )
        self._conn.execute(
            "INSERT INTO tasks VALUES (?,?,?,?,?,?,?)",
            (task.id, goal, team, task.state, None, now, now),
        )
        self._conn.commit()
        return task

    def set_state(self, task_id: str, state: TaskState, result: str | None = None) -> None:
        self._conn.execute(
            "UPDATE tasks SET state=?, result=COALESCE(?, result), updated_at=? WHERE id=?",
            (state, result, datetime.now(timezone.utc).isoformat(), task_id),
        )
        self._conn.commit()

    def log_step(self, task_id: str, type_: str, payload: dict[str, Any]) -> None:
        self._conn.execute(
            "INSERT INTO steps (task_id, type, payload, ts) VALUES (?,?,?,?)",
            (task_id, type_, json.dumps(payload), datetime.now(timezone.utc).isoformat()),
        )
        self._conn.commit()

    def get_task(self, task_id: str) -> Task | None:
        row = self._conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
        return _to_task(row) if row else None

    def list_tasks(self, limit: int = 100) -> list[Task]:
        rows = self._conn.execute(
            "SELECT * FROM tasks ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
        return [_to_task(r) for r in rows]


def _to_task(row: tuple[Any, ...]) -> Task:
    return Task(
        id=row[0], goal=row[1], team=row[2], state=TaskState(row[3]),
        result=row[4], created_at=row[5], updated_at=row[6],
    )
