"""Email watcher: monitor key contacts, extract action items, draft replies.

HARD RULE enforced in code: EmailWatcher has no send path that bypasses the
ApprovalQueue. send_reply() parks the draft as a destructive-class approval
request; only a human resolution triggers adapter.send().
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from atlas.comms.email_adapter import Email, EmailAdapter
from atlas.executors.approvals import ApprovalQueue

_ACTION_HINTS = re.compile(
    r"\b(your (first |next )?task|please|deadline|due|by (mon|tues|wednes|thurs|fri)|"
    r"install|set ?up|build|watch|review|start date|meet)\b",
    re.IGNORECASE,
)


@dataclass
class ActionItem:
    email_id: str
    sender: str
    text: str


class EmailWatcher:
    def __init__(self, adapter: EmailAdapter, approvals: ApprovalQueue, contacts: list[str]) -> None:
        self._adapter = adapter
        self._approvals = approvals
        self._contacts = contacts

    def poll(self) -> list[ActionItem]:
        """Fetch unread mail from watched contacts and extract action items."""
        items: list[ActionItem] = []
        for contact in self._contacts:
            for mail in self._adapter.fetch_unread_from(contact):
                items.extend(self._extract(mail))
        return items

    @staticmethod
    def _extract(mail: Email) -> list[ActionItem]:
        return [
            ActionItem(email_id=mail.id, sender=mail.sender, text=line.strip())
            for line in mail.body.splitlines()
            if _ACTION_HINTS.search(line) and len(line.strip()) > 15
        ]

    async def send_reply(self, to: str, subject: str, body: str) -> str:
        """Draft + human-gated send. There is intentionally no direct-send method."""
        draft_id = self._adapter.create_draft(to, subject, body)
        request_id = await self._approvals.request(
            tool_name="send_email",
            args={"draft_id": draft_id, "to": to, "subject": subject, "preview": body[:400]},
        )
        approved = await self._approvals.wait(request_id)
        if not approved:
            return f"[HELD] Draft {draft_id} was not approved; email NOT sent."
        self._adapter.send(draft_id)
        return f"[SENT] {draft_id} to {to}"
