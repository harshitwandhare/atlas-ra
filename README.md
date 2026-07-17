# ATLAS — Autonomous Task & Lab Assistant System

> A production-grade, multi-team agent system that works as a Generative-AI research assistant:
> planning, executing, verifying, and **remembering** — with a live control dashboard.

![CI](https://img.shields.io/badge/CI-GitHub_Actions-blue)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Why ATLAS exists

Frontier agents are powerful but stateless and unaccountable. ATLAS wraps a model-agnostic
agent core in the engineering that makes autonomy trustworthy:

- **Multi-team orchestration** — an Orchestrator decomposes goals and routes work to
  specialist teams (Systems, Research, Ops, Critic). V1 ships Orchestrator + Systems + Critic.
- **Three-tier memory** — episodic (task ledger), semantic (local vector store), and
  procedural (versioned skill playbooks distilled from successful runs). The system
  measurably improves at recurring work instead of rediscovering it.
- **Tiered execution policy** — every action is attempted at the cheapest, most reliable
  tier first: API/code → CLI → browser DOM → screen control.
- **Verification before completion** — a Critic agent reviews outputs; nothing is marked
  done on the agent's own say-so.
- **Full observability** — every agent step is traced and streamed live to the dashboard
  over WebSocket.
- **Provider abstraction** — Claude Agent SDK is the reference implementation; the
  `providers/` interface allows LangGraph or local models without touching the core.

## Architecture

```
┌────────────────────────── Next.js Dashboard ──────────────────────────┐
│  Chat · Live agent feed · Task ledger · Memory & skills · Approvals   │
└───────────────▲───────────────────────────────▲───────────────────────┘
                │ REST                          │ WebSocket (events)
┌───────────────┴───────────────────────────────┴───────────────────────┐
│                        FastAPI Gateway (backend/)                      │
├────────────────────────────────────────────────────────────────────────┤
│  Orchestrator ──► Task Ledger (SQLite)                                 │
│      │ decompose / route / retry / escalate                            │
│      ├──► Systems Team   (GPU / ComfyUI / StreamDiffusion executor)    │
│      ├──► Critic         (verifies before completion)                  │
│      └──► [Research, Ops — V2]                                         │
├────────────────────────────────────────────────────────────────────────┤
│  Memory: episodic (SQLite) · semantic (LanceDB) · procedural (skills/) │
│  Providers: ClaudeAgentSDK (reference) · <pluggable>                   │
└────────────────────────────────────────────────────────────────────────┘
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) and [docs/adr/](docs/adr/).

## Quickstart

```bash
# Backend
cd backend
uv sync
cp .env.example .env          # add ANTHROPIC_API_KEY
uv run atlas serve            # FastAPI on :8000

# Frontend
cd ../frontend
npm install
npm run dev                   # dashboard on :3000
```

## Repository layout

```
backend/    Typed Python package (uv, ruff, mypy, pytest)
frontend/   Next.js 14 dashboard (App Router, Tailwind, WebSocket client)
skills/     Procedural memory — versioned playbooks the system learns and uses
docs/       Architecture, ADRs, roadmap
```

## Safety model

Destructive actions (file deletion, system changes) require human approval via the
dashboard approval queue. All actions are logged to the episodic ledger. Secrets live
in the OS credential store, never in the repo.

## License

MIT © Harshit Wandhare
