from atlas.memory.episodic import Ledger, TaskState


def test_task_lifecycle(tmp_path):
    ledger = Ledger(str(tmp_path / "t.db"))
    task = ledger.create_task("install streamdiffusion", "systems")
    assert task.state == TaskState.PENDING

    ledger.set_state(task.id, TaskState.RUNNING)
    ledger.log_step(task.id, "tool_call", {"tool": "run_powershell"})
    ledger.set_state(task.id, TaskState.DONE, result="ok")

    reloaded = ledger.get_task(task.id)
    assert reloaded and reloaded.state == TaskState.DONE and reloaded.result == "ok"
    assert ledger.list_tasks()[0].id == task.id


def test_list_tasks_filters_by_state(tmp_path):
    ledger = Ledger(str(tmp_path / "t.db"))
    done_task = ledger.create_task("goal a", "systems")
    ledger.set_state(done_task.id, TaskState.DONE, result="ok")
    pending_task = ledger.create_task("goal b", "research")

    done_only = ledger.list_tasks(state=TaskState.DONE)
    assert [t.id for t in done_only] == [done_task.id]

    pending_only = ledger.list_tasks(state="pending")
    assert [t.id for t in pending_only] == [pending_task.id]

    assert len(ledger.list_tasks()) == 2
