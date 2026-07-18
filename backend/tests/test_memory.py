"""Memory tiers: ledger persistence semantics, semantic store, skill parsing edges."""

from __future__ import annotations

from atlas.memory import Ledger, SkillStore
from atlas.memory.episodic import TaskState
from atlas.memory.semantic import Doc, SemanticStore


def test_ledger_result_survives_later_stateonly_update(tmp_path):
    ledger = Ledger(str(tmp_path / "l.db"))
    task = ledger.create_task("g", "systems")

    ledger.set_state(task.id, TaskState.DONE, result="the answer")
    ledger.set_state(task.id, TaskState.DONE, result=None)  # COALESCE keeps old result

    assert ledger.get_task(task.id).result == "the answer"


def test_ledger_list_ordering_and_limit(tmp_path):
    ledger = Ledger(str(tmp_path / "l.db"))
    for i in range(5):
        ledger.create_task(f"goal {i}", "systems")

    assert len(ledger.list_tasks(limit=3)) == 3
    assert len(ledger.list_tasks()) == 5


def test_ledger_steps_roundtrip(tmp_path):
    ledger = Ledger(str(tmp_path / "l.db"))
    task = ledger.create_task("g", "ops")
    ledger.log_step(task.id, "message_delta", {"text": "unicode ✓ and \"quotes\""})

    row = ledger._conn.execute(
        "SELECT payload FROM steps WHERE task_id=?", (task.id,)
    ).fetchone()
    assert "unicode" in row[0]


def test_semantic_store_persists_across_reopen(tmp_path):
    path = str(tmp_path / "sem")
    SemanticStore(path).add(Doc(id="1", text="wan22 vram budget math", source="a"))

    reopened = SemanticStore(path)
    hits = reopened.search("vram budget")
    assert hits and hits[0].id == "1"


def test_semantic_search_ranks_by_overlap(tmp_path):
    store = SemanticStore(str(tmp_path / "sem"))
    store.add(Doc(id="lo", text="torch is a library", source="a"))
    store.add(Doc(id="hi", text="torch cuda vram tuning guide", source="b"))

    hits = store.search("cuda vram tuning")
    assert hits[0].id == "hi"


def test_semantic_search_empty_store(tmp_path):
    assert SemanticStore(str(tmp_path / "sem")).search("anything") == []


def test_skill_parse_full_frontmatter(tmp_path):
    (tmp_path / "s.md").write_text(
        "---\nname: my-skill\nversion: 2.1.0\ntriggers: lora, comfyui\n---\nBody here.",
        encoding="utf-8",
    )
    skills = SkillStore(str(tmp_path)).load_all()
    assert skills[0].name == "my-skill"
    assert skills[0].version == "2.1.0"
    assert skills[0].triggers == ["lora", "comfyui"]
    assert skills[0].body == "Body here."


def test_skill_without_frontmatter_is_skipped(tmp_path):
    (tmp_path / "plain.md").write_text("Just markdown, no front-matter.", encoding="utf-8")
    assert SkillStore(str(tmp_path)).load_all() == []


def test_skill_malformed_frontmatter_is_skipped(tmp_path):
    (tmp_path / "bad.md").write_text("---\nname: broken", encoding="utf-8")
    assert SkillStore(str(tmp_path)).load_all() == []


def test_skill_defaults_from_filename(tmp_path):
    (tmp_path / "fallback.md").write_text("---\n---\nBody.", encoding="utf-8")
    skill = SkillStore(str(tmp_path)).load_all()[0]
    assert skill.name == "fallback"
    assert skill.version == "0.1.0"
    assert skill.triggers == []


def test_skill_match_is_case_insensitive(tmp_path):
    (tmp_path / "s.md").write_text(
        "---\nname: sd\ntriggers: StreamDiffusion\n---\nB.", encoding="utf-8"
    )
    store = SkillStore(str(tmp_path))
    assert store.match("install STREAMDIFFUSION now")
    assert not store.match("unrelated goal")
