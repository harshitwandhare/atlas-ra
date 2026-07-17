---
name: comfyui-lora-training
version: 1.0.0
triggers: lora, comfyui, lora training
---
# ComfyUI — LoRA training workflow (10GB VRAM budget)

## Setup
- ComfyUI portable (Windows) + ComfyUI-Manager for node installs.
- Trainer nodes: kohya-based custom nodes, or run kohya_ss/sd-scripts alongside and load
  the resulting .safetensors in ComfyUI.

## Dataset
- 15–40 curated images; consistent subject; varied backgrounds/angles.
- Captioning: WD14 tagger for anime/stylized, BLIP for photo; always hand-fix top tags.
- Trigger word: unique token not in the base vocab.

## Training params that fit 10GB
- SDXL LoRA: rank 8–16, batch 1, gradient checkpointing ON, fp16/bf16, cache latents.
- SD1.5 LoRA: rank 16–32, batch 2 fits comfortably.
- LR 1e-4 (unet) / 5e-5 (text encoder), cosine schedule, 1500–3000 steps typical.

## Pitfalls (learned)
- OOM on SDXL: enable gradient checkpointing + cache latents to disk before lowering rank.
- Overfit tell: samples reproduce training backgrounds → cut steps or add regularization images.

## Verify
Generate a 4-image grid with/without the LoRA at weight 0.8; confirm subject fidelity
and no style bleed. Save grid to the task artifacts.
