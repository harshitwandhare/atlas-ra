# Version matrix

Every runtime the project depends on, what pins it, and the exact resolved version.
Rule: **nothing floats untracked** — Python deps resolve through `backend/uv.lock`,
Node deps through `frontend/package-lock.json`, CI installs from those lockfiles, and
the GPU stack below is a frozen, working set (do not "upgrade casually": the
StreamDiffusion pin order is load-bearing, see `skills/streamdiffusion-windows-install.md`).

## ATLAS backend (pinned by `backend/uv.lock`)

| Package | Constraint | Locked |
|---|---|---|
| Python | ≥ 3.10 (CI: 3.12) | 3.12 |
| fastapi | ≥ 0.111 | 0.139.2 |
| uvicorn | ≥ 0.30 | 0.51.0 |
| pydantic | ≥ 2.7 | 2.13.4 |
| pydantic-settings | ≥ 2.3 | 2.14.2 |
| claude-agent-sdk | ≥ 0.1 | 0.2.121 (against Claude Code CLI 2.1.58) |
| lancedb | ≥ 0.8 | 0.34.0 |
| typer | ≥ 0.12 | 0.27.0 |
| opentelemetry-api/sdk | ≥ 1.25 | 1.44.0 |
| pytest / mypy / ruff (dev) | ≥ 8 / ≥ 1.10 / ≥ 0.5 | 9.1.1 / 2.3.0 / 0.15.22 |

## ATLAS frontend (pinned by `frontend/package-lock.json`)

| Package | Version | Note |
|---|---|---|
| Node.js | 20 (CI + Vercel) | |
| Next.js | **14.2.35** exact | 14.2.5→14.2.35 closed a critical CVE cluster (cache poisoning, auth bypass, SSRF) |
| React | ^18.3.1 | |
| Storybook | ^9.1.20 | 8.x broke against Next 14.2.35's webpack; essentials/interactions merged into core in v9 |
| eslint-config-next | 14.2.35 exact | must track the Next version |
| Tailwind | ^3.4.4 | |

## GPU / RA stack (host installs, outside this repo)

| Component | Version | Where |
|---|---|---|
| StreamDiffusion venv Python | 3.10.11 | `D:\Github\StreamDiffusion\.venv` |
| torch | 2.1.0+cu121 | pinned **before** streamdiffusion install (order matters) |
| xformers | 0.0.22.post7 | matches torch 2.1.0 ABI |
| CUDA runtime | 12.1 | |
| TinyVAE | `madebyollin/taesd` | decode 200 ms → 5 ms |
| ComfyUI | 2025-08+ build | needs native Wan 2.2 nodes + native `TrainLoraNode` |
| Wan 2.2 TI2V | 5B fp16 (`Comfy-Org/Wan_2.2_ComfyUI_Repackaged`) | the 14B MoE pair does not fit 10 GB unquantized |

## Known risks

- `claude-agent-sdk` tracks a fast-moving CLI; the provider now degrades to a
  normalized ERROR event on any SDK failure (regression-tested), so a CLI/SDK skew
  can never wedge a task again.
- Storybook 9 pulls `webpack 5.108` alongside Next's bundled webpack — build-tested
  in CI (`build-storybook`) so a future Next bump that reintroduces the 8.x clash
  fails loudly.
- The StreamDiffusion stack is deliberately **frozen** (torch 2.1.0 era). Do not let
  ATLAS "helpfully" upgrade it; that is why `run_python`/`run_powershell` guidance in
  the ops team prompt says to justify tier use and log commands.
