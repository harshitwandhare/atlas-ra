"""Human-in-the-loop approval queue for destructive actions and outbound email."""

from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ApprovalState(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"


class ApprovalRequest(BaseModel):
    id: str
    tool_name: str
    args: dict[str, Any]
    state: ApprovalState = ApprovalState.PENDING
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ApprovalQueue:
    """In-process queue; requests surface on the dashboard and optionally via Telegram."""

    def __init__(self, notifier: Any = None) -> None:
        self._requests: dict[str, ApprovalRequest] = {}
        self._events: dict[str, asyncio.Event] = {}
        self._notifier = notifier

    async def request(self, tool_name: str, args: dict[str, Any]) -> str:
        req = ApprovalRequest(id=uuid.uuid4().hex[:10], tool_name=tool_name, args=args)
        self._requests[req.id] = req
        self._events[req.id] = asyncio.Event()
        if self._notifier is not None:
            await self._notifier.notify(
                f"ATLAS approval needed: {tool_name}({args}) — id {req.id}"
            )
        return req.id

    async def wait(self, request_id: str, timeout: float = 3600.0) -> bool:
        try:
            await asyncio.wait_for(self._events[request_id].wait(), timeout)
        except asyncio.TimeoutError:
            self._requests[request_id].state = ApprovalState.DENIED
            return False
        return self._requests[request_id].state == ApprovalState.APPROVED

    def resolve(self, request_id: str, approved: bool) -> ApprovalRequest:
        req = self._requests[request_id]
        req.state = ApprovalState.APPROVED if approved else ApprovalState.DENIED
        self._events[request_id].set()
        return req

    def pending(self) -> list[ApprovalRequest]:
        return [r for r in self._requests.values() if r.state == ApprovalState.PENDING]

    def all(self) -> list[ApprovalRequest]:
        return list(self._requests.values())
