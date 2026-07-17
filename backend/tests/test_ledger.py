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
