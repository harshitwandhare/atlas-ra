# ComfyUI workflows

Both files are ComfyUI **UI-format** graphs (`version: 0.4`) — load them with
**Workflow → Open** or drag-and-drop onto the canvas. Written and verified against
the official node specs on [docs.comfy.org](https://docs.comfy.org) (July 2026);
node *wiring* is the deliverable — if your ComfyUI build renders a widget in a
different order, re-pick the value shown in the tables below after loading.

## `wan22_ti2v_5b_10gb.json` — Wan 2.2 image-to-video on a 10 GB card

The official Wan 2.2 **5B TI2V** graph (the 14B MoE pair does not fit 10 GB without
heavy GGUF quantization; the 5B model is the correct choice for the lab's card —
see `skills/wan22-under-10gb.md`).

**ComfyUI**: any 2025-08+ build with native Wan 2.2 support (`Wan22ImageToVideoLatent`
is a built-in — no custom nodes required).

**Model files** (from the official
[Comfy-Org split_files repack](https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged)):

| File | Goes in |
|---|---|
| `wan2.2_ti2v_5B_fp16.safetensors` | `ComfyUI/models/diffusion_models/` |
| `umt5_xxl_fp8_e4m3fn_scaled.safetensors` | `ComfyUI/models/text_encoders/` |
| `wan2.2_vae.safetensors` | `ComfyUI/models/vae/` |

**Graph**: `UNETLoader → ModelSamplingSD3(shift 8) → KSampler(uni_pc/simple, 20 steps,
cfg 5)`, conditioned by `CLIPLoader(type=wan) → CLIPTextEncode` (positive+negative),
latents from `Wan22ImageToVideoLatent(vae, start_image)`, out through
`VAEDecode → SaveWEBM(vp9, 24 fps)`.

**10 GB VRAM notes**: defaults are the native 1280×704×121 frames — ComfyUI's
weight offloading makes this run on 8–10 GB, slowly. If you hit OOM or want faster
iterations, drop the `Wan22ImageToVideoLatent` widgets to **960×544, length 57**
(≈2.4 s @ 24 fps) first; resolution costs more than length. Keep batch at 1.

## `lora_train_sd15_native.json` — LoRA training, no custom nodes

Uses ComfyUI's **native training nodes**
([`TrainLoraNode`](https://docs.comfy.org/built-in-nodes/TrainLoraNode) +
`LoadImageSetFromFolderNode` + `SaveLoRANode` + `LossGraphNode`) — no Kohya wrapper
installs needed.

**Dataset**: put 10–30 images in `ComfyUI/input/atlas_lora_dataset/`. Optional
per-image captions: same-name `.txt` files. The `CLIPTextEncode` holds the fallback
caption/trigger (`photo of atlas_subject person`) — change the trigger token.

**Base model**: `v1-5-pruned-emaonly-fp16.safetensors` in `ComfyUI/models/checkpoints/`.
SD1.5 trains comfortably in ~6 GB. For SDXL on the 10 GB card, swap the checkpoint,
keep `gradient_checkpointing: true`, and lower `rank` to 8.

**Training widgets as saved**: batch 1, grad-accum 4, 800 steps, lr 5e-4, rank 16,
AdamW, MSE, bf16. Output lands in `ComfyUI/output/loras/atlas_subject_sd15.safetensors`
— move it to `models/loras/` to use it with a `LoraLoader`.

**Verification status**: node names and input/output types verified against
docs.comfy.org and the official workflow templates (July 2026). The
`TrainLoraNode` widget *order* in the JSON follows the documented parameter order;
ComfyUI tolerates re-mapping on load, but eyeball the values once before queueing.
