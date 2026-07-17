---
name: streamdiffusion-windows-install
version: 1.0.0
triggers: streamdiffusion, stream diffusion, real-time diffusion
---
# StreamDiffusion — Windows install (NVIDIA, ~10GB VRAM)

## Prerequisites (verify, don't assume)
- `nvidia-smi` → driver OK, note VRAM free.
- Python 3.10 (StreamDiffusion is pinned; 3.11+ breaks builds). Use a dedicated venv/conda env.
- CUDA toolkit matching the torch build you install (check `torch.version.cuda`).
- Git + VS Build Tools (C++ workload) for any source builds.

## Install
```powershell
git clone https://github.com/harshitwandhare/StreamDiffusion   # personal fork (already validated on target laptop)
cd StreamDiffusion
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
pip install -e .
python -m streamdiffusion.tools.install-tensorrt   # optional; big speedup, large download
```

## Pitfalls (learned)
- torch/CUDA mismatch is the #1 failure: install torch with the explicit cu12x index URL BEFORE `pip install -e .`.
- TensorRT engines are resolution-specific; rebuilding on resolution change is expected, not a bug.
- 10GB VRAM: use SD-Turbo / LCM at 512x512; leave >1.5GB headroom for TensorRT workspace.

## Verify (smoke test)
```powershell
python examples/screen/main.py   # or examples/img2img
```
Success = sustained fps output without CUDA OOM. Record fps in the task result.
