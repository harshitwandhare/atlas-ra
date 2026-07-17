from atlas.memory.procedural import SkillStore


def test_skill_parse_and_match(tmp_path):
    (tmp_path / "demo.md").write_text(
        "---\nname: demo\nversion: 1.0.0\ntriggers: streamdiffusion, comfyui\n---\n# Steps\nDo X.",
        encoding="utf-8",
    )
    store = SkillStore(str(tmp_path))
    skills = store.load_all()
    assert skills[0].name == "demo" and skills[0].version == "1.0.0"
    assert store.match("Install StreamDiffusion on Windows")
    assert not store.match("write a poem")
