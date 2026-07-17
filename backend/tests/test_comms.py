import asyncio

import pytest

from atlas.comms.email_adapter import Email
from atlas.comms.email_watcher import EmailWatcher
from atlas.executors.approvals import ApprovalQueue


class FakeAdapter:
    def __init__(self):
        self.sent = []
        self._drafts = {}

    def fetch_unread_from(self, sender_filter):
        return [
            Email(
                id="1",
                sender="afs140330@utdallas.edu",
                subject="Onboarding",
                body=(
                    "Welcome!\nYour first task will be a local installation "
                    "of stream diffusion.\nSee you Tuesday."
                ),
            )
        ]

    def create_draft(self, to, subject, body):
        self._drafts["d1"] = (to, subject, body)
        return "d1"

    def send(self, draft_id):
        self.sent.append(draft_id)


@pytest.mark.asyncio
async def test_action_item_extraction():
    watcher = EmailWatcher(FakeAdapter(), ApprovalQueue(), ["utdallas.edu"])
    items = watcher.poll()
    assert any("stream diffusion" in i.text.lower() for i in items)


@pytest.mark.asyncio
async def test_email_never_sent_without_approval():
    adapter = FakeAdapter()
    queue = ApprovalQueue()
    watcher = EmailWatcher(adapter, queue, ["utdallas.edu"])

    async def deny():
        await asyncio.sleep(0.05)
        queue.resolve(queue.pending()[0].id, approved=False)

    asyncio.get_event_loop().create_task(deny())
    result = await watcher.send_reply("prof@utd.edu", "Re: Task", "On it.")
    assert "HELD" in result and adapter.sent == []


@pytest.mark.asyncio
async def test_email_sent_after_human_approval():
    adapter = FakeAdapter()
    queue = ApprovalQueue()
    watcher = EmailWatcher(adapter, queue, ["utdallas.edu"])

    async def approve():
        await asyncio.sleep(0.05)
        queue.resolve(queue.pending()[0].id, approved=True)

    asyncio.get_event_loop().create_task(approve())
    result = await watcher.send_reply("prof@utd.edu", "Re: Task", "On it.")
    assert "SENT" in result and adapter.sent == ["d1"]
