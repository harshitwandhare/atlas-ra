from atlas.orchestrator.core import Orchestrator


def test_keyword_router():
    route = Orchestrator._route
    assert route("Install StreamDiffusion and run the smoke test") == "systems"
    assert route("Research papers comparing AWQ and GPTQ quantization") == "research"
    assert route("Clean up my downloads and organize files by type") == "ops"
    assert route("Build a ComfyUI LoRA training workflow") == "systems"


def test_router_ops_hints():
    route = Orchestrator._route
    assert route("Uninstall the old cuda driver") == "ops"
    assert route("install driver for my GPU") == "ops"
    assert route("windows settings for display") == "ops"


def test_router_research_hints():
    route = Orchestrator._route
    assert route("find the best quantization method") == "research"
    assert route("summarize the diffusion paper") == "research"
    assert route("watch this video about fine-tuning") == "research"


def test_router_defaults_to_systems():
    route = Orchestrator._route
    assert route("run a comfyui workflow for upscaling") == "systems"
    assert route("set up a new conda environment") == "systems"
