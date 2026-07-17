---
name: touchdesigner-streamdiffusion-pipeline
version: 1.0.0
triggers: touchdesigner, touch designer, td, streamdiffusiontd
---
# TouchDesigner ↔ StreamDiffusion real-time pipeline

## Principle
TouchDesigner is fully scriptable (built-in Python `td` module). Prefer generating
networks via script over UI clicks — reproducible and version-controllable.

## Integration options (in order of preference)
1. **StreamDiffusionTD** (dotsimulate) — TD component wrapping StreamDiffusion; feeds any
   TOP as input, returns diffused frames as a TOP. Runs SD in a separate Python process.
2. Spout/NDI bridge — TD → Spout out → StreamDiffusion screen/pipe example → Spout back in.
   More moving parts, but framework-agnostic.

## VRAM budgeting (shared GPU!)
TD compositing + SD inference share the 10GB card. Keep TD render resolution modest
(720p TOPs), SD at 512x512, and monitor with `nvidia-smi dmon`.

## Scripting TD
- Every operator is creatable/parameterizable from Python: `op('/project1').create(top.rendertop, 'render1')`.
- Store pipeline setup in a startup script inside the .toe or an external .py run by an Execute DAT,
  and keep .toe files under git (binary, so also export .tox components for diffable structure).

## Verify
Webcam TOP → StreamDiffusionTD → out. Success = live stylized output ≥ 8fps at 512x512.
