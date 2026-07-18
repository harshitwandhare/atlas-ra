# Operating TouchDesigner + StreamDiffusion (ATLAS ops runbook)

How the ops team drives the **local StreamDiffusion install** (`D:\Github\StreamDiffusion`,
Python 3.10.11 venv, torch 2.1.0+cu121, xformers 0.0.22.post7) into TouchDesigner.
Everything below references files that exist in that repo and was benchmarked on the
resident RTX 2060 (6 GB) — expect proportionally better numbers on a 10 GB lab card.

## Architecture (PNG bridge — no extra SDKs)

```
Webcam ──► td_bridge.py (venv, GPU inference ~4.1 fps)
              │  writes td_out/input_frame.png  + td_out/output_frame.png
              │
              ◄── OSC :9000   TD sends  /prompt /strength /seed /model /pause
              ──► OSC :9001   TD reads  /fps /vram_used /status /model_name
                    │
             TouchDesigner:  Movie File In TOPs (the two PNGs) + OSC In/Out CHOPs
```

## Start the backend

```powershell
# from anywhere — or use scripts/launch_streamdiffusion_demo.ps1 in this repo
cd D:\Github\StreamDiffusion
.venv\Scripts\activate
python touchdesigner/td_bridge.py --config configs/sdturbo_fast.yaml --webcam 0 --no-window
```

Ready when it prints `[INIT] Model ready.` / `[RUN] Streaming.`

## Build the TD side

Two options, both scripted (no manual node wiring):

1. **Full control panel (recommended)** — inside TouchDesigner's Textport:
   run `D:\Github\StreamDiffusion\touchdesigner\build_component.py`. Builds the
   complete network: file-in TOPs on `td_out/`, OSC prompt/strength/seed controls,
   FPS + VRAM readouts.
2. **Minimal network** — `touchdesigner/td_network_builder.py`, same idea, fewer ops.

TouchDesigner is driven through its own Python (`td` module) by these scripts —
that is the project's "operate TouchDesigner via code, not clicks" tier in practice.

## Alternative: NDI bridge

`touchdesigner/td_ndi_bridge.py` streams frames as an NDI source (needs the NDI SDK
installed) — use when you want TD's **NDI In TOP** instead of PNG polling.

## Mode reference (from the install's own `docs/all-run-modes.md`)

| Mode | Script | Status on this machine |
|---|---|---|
| TD PNG bridge | `touchdesigner/td_bridge.py` | ✅ 4.14 fps |
| TD NDI bridge | `touchdesigner/td_ndi_bridge.py` | ✅ (NDI SDK required) |
| Webcam → browser | `demo/realtime-img2img/main.py` | ✅ 4.14 fps |
| Screen capture | `examples/screen/main.py` | ✅ |
| vid2vid / img2img / txt2img | `examples/…` | ✅ (txt2img: Kohaku model only) |
| realtime-txt2img demo | `demo/realtime-txt2img/main.py` | ❌ upstream TS build error |

Configs: `sdturbo_fast.yaml` (speed), `kohaku_quality.yaml` (quality),
`sdturbo_tensorrt.yaml` (TensorRT engines, +2–4× once built).

## VRAM guidance

512×512 real-time on 6 GB; TinyVAE (`madebyollin/taesd`) is what makes decode ~5 ms.
On the lab's 10 GB card 768×768 becomes viable — raise resolution in the config, not
batch size.
