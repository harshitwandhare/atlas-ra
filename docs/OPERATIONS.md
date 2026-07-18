# Operating ATLAS

End-to-end guide for running ATLAS on a Windows workstation. Everything here was
executed and verified on the reference machine (Windows 10, NVIDIA GPU, Python 3.12
via uv, Node 20+).

## 1. Prerequisites

| Requirement | Version | Check |
|---|---|---|
| Python | ≥ 3.10 | `python --version` |
| [uv](https://docs.astral.sh/uv/) | latest | `uv --version` |
| Node.js | 20 LTS+ | `node --version` |
| Claude Code CLI | 2.x | `claude --version` — required only for `provider=claude` |
| Ollama (optional) | latest | `ollama --version` — required only for `provider=ollama` |

## 2. Install

```powershell
git clone https://github.com/harshitwandhare/atlas-ra.git
cd atlas-ra

# Backend — creates .venv and installs locked deps
cd backend
uv sync --all-extras

# Frontend
cd ../frontend
npm ci
```

## 3. Configure

Backend settings come from environment variables prefixed `ATLAS_` or a
`backend/.env` file (see `backend/.env.example`):

| Variable | Default | Meaning |
|---|---|---|
| `ATLAS_PROVIDER` | `claude` | Agent runtime: `claude` (Claude Agent SDK via local Claude Code auth), `langgraph`, or `ollama` (fully offline) |
| `ATLAS_DB_PATH` | `atlas.db` | SQLite ledger location |
| `ATLAS_SKILLS_DIR` | `../skills` | Procedural-memory playbooks directory |
| `ATLAS_MAX_RETRIES` | `2` | Critic-rejected attempts before a task escalates |

`provider=claude` needs no API key on a machine where Claude Code is signed in — the
SDK rides the local CLI auth. `provider=ollama` needs an Ollama daemon on
`localhost:11434`.

## 4. Run

Two processes:

```powershell
# Terminal 1 — API gateway + orchestrator (port 8000)
cd backend
uv run atlas serve            # or: uv run uvicorn atlas.api.main:app --port 8000

# Terminal 2 — dashboard (port 3000)
cd frontend
npm run dev
```

Open http://localhost:3000.

## 5. Operate

### Submit goals

- **Dashboard**: type a goal on the Chat page and hit **Run**.
- **CLI**: `uv run atlas goal "Summarize the VRAM budget for Wan 2.2 5B on a 10GB GPU"`
- **API**: `POST http://localhost:8000/goals` with `{"goal": "..."}`.

The orchestrator routes each goal to a team (`research` / `systems` / `ops`) by
keyword, injects matching skills from procedural memory as context, and streams the
provider's events to the ledger and the dashboard WebSocket.

### Watch progress

- **Activity** — live `AgentEvent` stream (state changes, message deltas, tool calls, errors).
- **Ledger** — every task with its current state. Lifecycle:
  `pending → running → review → done`, or `→ escalated` after `ATLAS_MAX_RETRIES`
  Critic rejections or an unrecoverable provider error.
- **CLI**: `uv run atlas tasks` prints the same table.

### Approvals (human-in-the-loop)

Destructive tools (`delete_path`, and anything registered `Risk.DESTRUCTIVE`) do not
execute until you approve them on the **Approvals** page (or
`POST /approvals/{id} {"approved": true|false}`). Reversible tools (`run_python`,
`run_powershell`) execute without a gate — see the security note in
[ARCHITECTURE.md](ARCHITECTURE.md) before pointing ATLAS at untrusted input.

### Memory

- **Episodic** — the SQLite ledger: every task and step, queryable forever.
- **Semantic** — `POST /ingest {"source": "<file path or video URL>"}` extracts text
  from PDF/PPTX/DOCX/subtitles into append-only JSONL memory; tutorial-style content
  also yields a draft procedure.
- **Procedural** — `skills/*.md` playbooks with front-matter (`name`, `version`,
  `triggers`). Matching skills are injected into every relevant run, which is how the
  system "keeps getting better": distill a finished task into a skill file and every
  future run benefits. See the four seeded playbooks in `skills/`.

### RA workloads (StreamDiffusion / ComfyUI / TouchDesigner)

- `workflows/comfyui/` — loadable workflow JSONs (Wan 2.2 i2v on a 10GB card, LoRA
  training) with model/custom-node requirements in the local README.
- `workflows/touchdesigner/` — operating TouchDesigner against the local
  StreamDiffusion install.
- `scripts/launch_streamdiffusion_demo.ps1` — activates the StreamDiffusion venv and
  runs its demo (expects the install documented in
  `skills/streamdiffusion-windows-install.md`).

## 6. Test / verify

```powershell
cd backend
uv run ruff check .          # lint
uv run mypy src              # strict types
uv run pytest -q             # unit + integration + e2e
uv run python -m evals.run_evals   # behavioral evals (must beat baseline)

cd ../frontend
npm run lint && npm run build
npm run storybook            # component workbench on :6006
```

CI runs the same gates on every push; deploys to Vercel happen automatically from
`main` (see `.github/workflows/`).

## 7. Troubleshooting

| Symptom | Cause / fix |
|---|---|
| Task stuck in `running` | Provider crashed pre-v0.2.1 (fixed: now escalates + emits ERROR). Check the Activity page for the ERROR payload. |
| `Claude Code returned an error result` | Claude Code CLI not signed in, or version mismatch with `claude-agent-sdk`. Run `claude --version`, sign in once interactively. |
| Dashboard shows no events | Backend not on :8000, or CORS origin ≠ localhost:3000. |
| `ollama` provider errors instantly | Ollama daemon not running: `ollama serve`, then `ollama pull llama3.1`. |
| Approval never resolves | Approvals are in-memory (v0.2): restarting the backend clears pending requests. Re-run the task. |
