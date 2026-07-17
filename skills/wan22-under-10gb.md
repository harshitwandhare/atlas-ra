---
name: wan22-under-10gb
version: 1.0.0
triggers: wan 2.2, wan2.2, video generation, i2v
---
# Wan 2.2 video generation under a 10GB VRAM budget

## Model choice (VRAM math first)
- 14B models: will NOT fit in 10GB even at Q4 with activations — do not attempt locally.
- **TI2V-5B**: the correct choice. fp8/GGUF-quantized ~6–8GB peak with offloading.

## Setup (ComfyUI)
- Use the native Wan 2.2 ComfyUI workflow templates; download 5B checkpoint (fp8 or GGUF Q6/Q8)
  + umt5 text encoder + VAE into the standard model folders.
- Enable `--lowvram`; use tiled VAE decode for anything above 480p.

## Pitfalls (learned)
- Text-encoder VRAM spike at prompt encode: keep umt5 in a quantized/offloaded variant.
- 720p x 5s will crawl on 10GB — prototype at 480p, upscale after.

## Verify
Generate a 33-frame 480p i2v clip from a test image; confirm no OOM and note s/it.
