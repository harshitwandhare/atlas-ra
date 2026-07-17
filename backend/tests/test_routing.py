from atlas.orchestrator.core import Orchestrator


def test_keyword_router():
    route = Orchestrator._route
    assert route("Install StreamDiffusion and run the smoke test") == "systems"
    assert route("Research papers comparing AWQ and GPTQ quantization") == "research"
    assert route("Clean up my downloads and organize files by type") == "ops"
    assert route("Build a ComfyUI LoRA training workflow") == "systems"
