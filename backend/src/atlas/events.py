"""Normalized event model shared by providers, ledger, tracing, and the WebSocket bus."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class EventType(str, Enum):
    TASK_STATE = "task_state"
    MESSAGE_DELTA = "message_delta"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    CHECKPOINT = "checkpoint"
    APPROVAL_REQUEST = "approval_request"
    DONE = "done"
    ERROR = "error"


class AgentEvent(BaseModel):
    """One normalized step emitted by any provider (ADR-0001)."""

    type: EventType
    task_id: str
    agent: str = "system"
    payload: dict[str, Any] = Field(default_factory=dict)
    ts: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
