# ATLAS Architecture

## 1. Design goals

1. **Trustworthy autonomy** — every step observable, every completion verified, every
   destructive action gated behind human approval.
2. **Compounding competence** — successful runs are distilled into reusable, versioned
   procedural knowledge (skills), so recurring RA work gets faster and more reliable.
3. **Model/framework independence** — the agent runtime is an implementation detail
   behind `atlas.providers`.
4. **Cheapest-reliable-tier execution** — code before clicks.

## 2. Components

### 2.1 Orchestrator (`atlas/orchestrator`)
Receives a goal, decomposes it into tasks (persisted to the ledger), routes each task
to a team, supervises execution (retry with backoff, escalate to human on repeated
failure), and requests Critic review before marking anything complete.

Task state machine:

```
PENDING → ASSIGNED → RUNNING → REVIEW → DONE
                        │          │
                        ├→ FAILED ─┴→ ESCALATED (human)
                        └→ BLOCKED (awaiting approval)
```

### 2.2 Teams (`atlas/teams`)
A team is a provider-backed agent with a scoped system prompt, a tool allowlist, and
access to relevant skills. V1 ships:

- **SystemsTeam** — local GPU/ML engineering: environment setup, ComfyUI workflows,
  StreamDiffusion, LoRA training, quantization benchmarking under a VRAM budget.
- **Critic** — reviews artifacts and transcripts against the task's acceptance criteria;
  returns `approve` / `revise(feedback)` / `reject`. On approve, distills/updates a skill.

### 2.3 Memory (`atlas/memory`)

| Layer | Store | Content | Written by | Read by |
|---|---|---|---|---|
| Episodic | SQLite | every task: goal, steps, errors, outcome | Orchestrator | all |
| Semantic | LanceDB (local) | embedded notes, papers, past solutions | ingest | retrieval per task |
| Procedural | `skills/*.md` (git-versioned) | distilled playbooks | Critic on success | teams |

The **skill distillation loop** is the core learning mechanism: after a task passes
review, the Critic diff-updates or creates a playbook capturing prerequisites, exact
commands, pitfalls, and verification steps. Skills carry semver in front-matter and are
loaded into a team's context when the router matches their triggers.

Context management: long runs checkpoint a structured summary to the ledger every N
steps; on resume/compaction, the summary + relevant skills reconstruct working memory.
This is how ATLAS "doesn't forget."

### 2.4 Execution tiers (`atlas/executors`)
Policy enforced by the tool layer, not by prompting alone:

1. **API / library call** (Python)
2. **CLI** (PowerShell on the Windows host)
3. **Browser DOM** (Playwright)
4. **Screen control** (pixel-level; requires approval flag)

Each tool declares its tier and risk class (`safe`, `reversible`, `destructive`).
`destructive` tools enqueue an approval request instead of executing.

### 2.5 Providers (`atlas/providers`)
`AgentProvider` protocol: `run(task, tools, context) -> AsyncIterator[AgentEvent]`.
Reference implementation: **Claude Agent SDK**. Adding LangGraph/local models means one
new module implementing the protocol, registered in `providers/registry.py`, selected
via config — zero changes elsewhere (ADR-0001).

### 2.6 API & event bus (`atlas/api`)
FastAPI REST for goals/tasks/skills/approvals + a WebSocket fanning out `AgentEvent`s
(state changes, tool calls, tokens, approval requests) to the dashboard in real time.

### 2.7 Dashboard (`frontend/`)
Next.js App Router. Views: Chat (submit goals, streamed responses), Activity (live
event feed), Ledger (task table + states), Skills (procedural memory browser),
Approvals (pending destructive actions).

## 3. Observability & evals

Every provider event maps to an OpenTelemetry span (task → step → tool call), exported
via OTLP to Langfuse/Phoenix. `backend/evals/` holds scored regression tasks run in CI
so improvement across versions is proven, not asserted.

## 4. Security

- Secrets: OS credential store / runtime env; `.env` git-ignored.
- Tool allowlists per team; no blanket shell access.
- Full audit trail in the episodic ledger.
- Human-in-the-loop for the `destructive` risk class — non-negotiable default.

## 5. Comms team & universal ingestion (V2)

### Comms team (`atlas/teams/comms`) — email with human-gated send
Watches the user's inbox (Gmail API / MCP connector) for threads from configured
contacts (e.g. Prof. Scott). It classifies, extracts action items into the ledger,
and **drafts** replies. Sending is a `destructive`-class tool: every outbound email
sits in the dashboard Approvals queue until the human approves — no exceptions.

### Ingestion pipeline (`atlas/ingest`) — format-agnostic knowledge intake
Single `ingest(source) -> SemanticDocs + ProceduralCandidates` entrypoint:

| Source | Method |
|---|---|
| YouTube / video | subtitles via yt-dlp; fallback Whisper ASR; keyframe capture for visual steps |
| PDF | text + OCR (scanned) extraction |
| PPTX / DOCX / XLSX | python-pptx / python-docx / openpyxl extraction |
| Web pages | readability extraction via Playwright |

Tutorial-style videos (e.g. "StreamDiffusion install", "ComfyUI LoRA training") are
additionally run through a *procedure extractor* that converts the transcript into a
draft skill playbook — the system literally learns how to do what's in the video,
pending Critic + human review.
