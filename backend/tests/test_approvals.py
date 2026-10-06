import pytest

from atlas.executors.approvals import ApprovalQueue, ApprovalState


class _Notifier:
    def __init__(self) -> None:
        self.messages: list[str] = []

    async def notify(self, text: str) -> None:
        self.messages.append(text)


async def test_request_starts_pending_and_is_listed():
    queue = ApprovalQueue()
    rid = await queue.request("delete_file", {"path": "a.txt"})
    assert [r.id for r in queue.pending()] == [rid]
    assert queue.all()[0].state == ApprovalState.PENDING


async def test_request_notifies_with_tool_and_id():
    notifier = _Notifier()
    queue = ApprovalQueue(notifier=notifier)
    rid = await queue.request("send_email", {"to": "x@example.com"})
    assert len(notifier.messages) == 1
    assert "send_email" in notifier.messages[0]
    assert rid in notifier.messages[0]


async def test_resolve_approved_unblocks_wait():
    queue = ApprovalQueue()
    rid = await queue.request("run_shell", {})
    queue.resolve(rid, approved=True)
    assert await queue.wait(rid, timeout=1.0) is True
    assert queue.pending() == []


async def test_resolve_denied_returns_false():
    queue = ApprovalQueue()
    rid = await queue.request("run_shell", {})
    queue.resolve(rid, approved=False)
    assert await queue.wait(rid, timeout=1.0) is False


async def test_wait_timeout_marks_request_denied():
    queue = ApprovalQueue()
    rid = await queue.request("run_shell", {})
    assert await queue.wait(rid, timeout=0.01) is False
    assert queue.all()[0].state == ApprovalState.DENIED
    assert queue.pending() == []


def test_resolve_unknown_id_raises():
    queue = ApprovalQueue()
    with pytest.raises(KeyError):
        queue.resolve("nope", approved=True)
