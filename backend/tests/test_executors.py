import asyncio

import pytest

from atlas.executors.approvals import ApprovalQueue
from atlas.executors.registry import default_registry


@pytest.mark.asyncio
async def test_run_python_tier1():
    reg = default_registry()
    out = await reg.execute("run_python", code="print(2 + 2)")
    assert "4" in out


@pytest.mark.asyncio
async def test_destructive_requires_approval_and_denial_blocks(tmp_path):
    reg = default_registry()
    queue = ApprovalQueue()
    victim = tmp_path / "keep.txt"
    victim.write_text("important")

    async def deny_soon():
        await asyncio.sleep(0.05)
        queue.resolve(queue.pending()[0].id, approved=False)

    asyncio.get_event_loop().create_task(deny_soon())
    out = await reg.execute("delete_path", approval_queue=queue, path=str(victim))
    assert "DENIED" in out and victim.exists()


@pytest.mark.asyncio
async def test_destructive_approved_executes(tmp_path):
    reg = default_registry()
    queue = ApprovalQueue()
    victim = tmp_path / "gone.txt"
    victim.write_text("bye")

    async def approve_soon():
        await asyncio.sleep(0.05)
        queue.resolve(queue.pending()[0].id, approved=True)

    asyncio.get_event_loop().create_task(approve_soon())
    out = await reg.execute("delete_path", approval_queue=queue, path=str(victim))
    assert "deleted" in out and not victim.exists()
