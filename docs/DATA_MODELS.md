# Data models

Every model actually defined in the codebase, grouped by domain. Backend models are
Pydantic `BaseModel`s or `@dataclass`es (verified by grep across
`backend/src/atlas/**/*.py`); frontend models are TypeScript interfaces in
`frontend/lib/*.ts` and page components under `frontend/app/**/*.tsx`.

## Task / Ledger

### `Task` — `backend/src/atlas/memory/episodic.py`
Pydantic `BaseModel`. One row in the `tasks` SQLite table.

| Field | Type | Notes |
|---|---|---|
| `id` | `str` | `uuid4().hex[:12]`, primary key |
| `goal` | `str` | The user-submitted goal text |
| `team` | `str` | `"systems" \| "research" \| "ops"`, set by `Orchestrator._route` |
| `state` | `TaskState` | See enum below |
| `result` | `str \| None` | Critic summary or escalation reason |
| `created_at` | `str` | ISO-8601 UTC |
| `updated_at` | `str` | ISO-8601 UTC |

### `TaskState` — `backend/src/atlas/memory/episodic.py`
`str, Enum`: `PENDING, ASSIGNED, RUNNING, REVIEW, DONE, FAILED, BLOCKED, ESCALATED`.
Only `PENDING → RUNNING → REVIEW → DONE` and `RUNNING → RUNNING` (retry) /
`… → ESCALATED` are actually driven by `Orchestrator._run`; `ASSIGNED`, `FAILED`,
and `BLOCKED` are declared in the enum (and in the state-machine diagram in
`docs/ARCHITECTURE.md`) but are not currently set anywhere in `orchestrator/core.py`.

### `Ledger` — `backend/src/atlas/memory/episodic.py`
Not a data model itself, but owns the schema: `tasks` table above plus a `steps`
table (`id, task_id, type, payload JSON, ts`) written by `log_step()` on every
`AgentEvent`.

## Events

### `AgentEvent` — `backend/src/atlas/events.py`
Pydantic `BaseModel`. The single normalized event shape emitted by every provider,
persisted by the ledger, wrapped in a trace span, and serialized to the dashboard.

| Field | Type | Notes |
|---|---|---|
| `type` | `EventType` | See enum below |
| `task_id` | `str` | |
| `agent` | `str` | Defaults to `"system"`; providers set `"claude"` / `"langgraph"` / `"ollama"` |
| `payload` | `dict[str, Any]` | Free-form; shape depends on `type` (e.g. `{"text": ...}` for `MESSAGE_DELTA`, `{"tool": ..., "input": ...}` for `TOOL_CALL`) |
| `ts` | `datetime` | UTC, defaults to now |

### `EventType` — `backend/src/atlas/events.py`
`str, Enum`: `TASK_STATE, MESSAGE_DELTA, TOOL_CALL, TOOL_RESULT, CHECKPOINT,
APPROVAL_REQUEST, DONE, ERROR`. Note: `TOOL_RESULT`, `CHECKPOINT`, and
`APPROVAL_REQUEST` are declared but not currently emitted anywhere in
`providers/*.py` or `orchestrator/core.py` — they exist as forward-declared surface
for the tool-execution and checkpointing work described in `docs/ROADMAP.md`.

## Memory

### `Doc` — `backend/src/atlas/memory/semantic.py`
`@dataclass`. A unit of semantic memory.

| Field | Type | Notes |
|---|---|---|
| `id` | `str` | |
| `text` | `str` | Extracted/ingested text |
| `source` | `str` | File path or URL |
| `meta` | `dict[str, str]` | e.g. `{"procedure_draft": "..."}` set by the ingest pipeline |

Persisted append-only as JSON lines by `SemanticStore` (`docs.jsonl`); `search()`
does keyword-overlap scoring, not vector similarity, in the current implementation.

### `Skill` — `backend/src/atlas/memory/procedural.py`
Pydantic `BaseModel`. Parsed from front-matter markdown files in `skills/`.

| Field | Type | Notes |
|---|---|---|
| `name` | `str` | From front-matter, falls back to filename stem |
| `version` | `str` | Semver-ish string, e.g. `"0.1.0"` |
| `triggers` | `list[str]` | Comma-split keywords; `SkillStore.match()` substring-matches against the goal |
| `body` | `str` | Markdown body after the front-matter block |

## Provider

### `AgentProvider` — `backend/src/atlas/providers/base.py`
`typing.Protocol` (not a data model, but the contract every provider implements):
`name: str` plus `run(task_id, system_prompt, goal, tools, context) -> AsyncIterator[AgentEvent]`.
Implementations: `ClaudeProvider`, `LangGraphProvider`, `OllamaProvider`
(`providers/claude.py`, `providers/langgraph.py`, `providers/ollama.py`), each a
plain class (not a Pydantic model) with a `name` class attribute and constructor
args for model selection (`LangGraphProvider(model=...)`, `OllamaProvider(model=...,
base_url=...)`).

### `Settings` — `backend/src/atlas/config.py`
Pydantic `BaseSettings`, env-prefixed `ATLAS_`, loaded from `.env`.

| Field | Type | Default |
|---|---|---|
| `provider` | `str` | `"claude"` |
| `db_path` | `str` | `"atlas.db"` |
| `skills_dir` | `str` | `"../skills"` |
| `max_retries` | `int` | `2` |
| `checkpoint_every_n_steps` | `int` | `20` (declared; not yet read by orchestrator code — checkpointing is described as a design intent in `docs/ARCHITECTURE.md` §2.3 but `_run()` does not currently call it) |

## Executor / Approvals

### `Tool` — `backend/src/atlas/executors/registry.py`
`@dataclass`. One entry in the `ToolRegistry`.

| Field | Type | Notes |
|---|---|---|
| `name` | `str` | e.g. `"run_python"` |
| `description` | `str` | |
| `tier` | `int` | `1` API/code, `2` CLI, `3` browser DOM, `4` screen control |
| `risk` | `Risk` | See enum below |
| `handler` | `Callable[..., Awaitable[str]]` | Async function actually executed |
| `schema` | `dict[str, Any]` | Default `{}` — tool-call JSON schema, currently unused by the shipped tools |

Shipped instances (`default_registry()`): `run_python` (tier 1, reversible),
`run_powershell` (tier 2, reversible), `delete_path` (tier 2, destructive).

### `Risk` — `backend/src/atlas/executors/registry.py`
`str, Enum`: `SAFE, REVERSIBLE, DESTRUCTIVE`. `ToolRegistry.execute()` routes
`DESTRUCTIVE` tools through the `ApprovalQueue` before invoking the handler.

### `ApprovalRequest` — `backend/src/atlas/executors/approvals.py`
Pydantic `BaseModel`.

| Field | Type | Notes |
|---|---|---|
| `id` | `str` | `uuid4().hex[:10]` |
| `tool_name` | `str` | e.g. `"delete_path"`, `"send_email"` |
| `args` | `dict[str, Any]` | Tool call arguments awaiting approval |
| `state` | `ApprovalState` | Default `PENDING` |
| `created_at` | `str` | ISO-8601 UTC |

### `ApprovalState` — `backend/src/atlas/executors/approvals.py`
`str, Enum`: `PENDING, APPROVED, DENIED`.

## Teams / Critic

### `Verdict` — `backend/src/atlas/teams/critic.py`
Pydantic `BaseModel`. Return type of `Critic.review()`.

| Field | Type | Notes |
|---|---|---|
| `approved` | `bool` | |
| `summary` | `str` | Default `""`; last 1000 chars of transcript on approval |
| `feedback` | `str` | Default `""`; reason for rejection, appended to the retry goal |

`SystemsTeam`, `ResearchTeam`, `OpsTeam` (`teams/systems.py`, `teams/research.py`,
`teams/ops.py`) are plain classes with class-level `name: str`, `system_prompt: str`,
and `tools: list[dict[str, Any]]` — not Pydantic models, just static declarations of
prompt + tool/tier/risk metadata consumed by the orchestrator and (in principle) the
provider's tool-call layer.

## Comms

### `Email` — `backend/src/atlas/comms/email_adapter.py`
`@dataclass`.

| Field | Type | Notes |
|---|---|---|
| `id` | `str` | IMAP message number |
| `sender` | `str` | |
| `subject` | `str` | |
| `body` | `str` | First `text/plain` part |
| `thread_id` | `str` | Default `""` — not populated by `ImapAdapter` |

### `EmailAdapter` — `backend/src/atlas/comms/email_adapter.py`
`typing.Protocol`: `fetch_unread_from(sender_filter) -> list[Email]`,
`create_draft(to, subject, body) -> str`, `send(draft_id) -> None`. Implemented by
`ImapAdapter` (IMAP fetch / SMTP send, password from OS keyring via the `keyring`
package).

### `ActionItem` — `backend/src/atlas/comms/email_watcher.py`
`@dataclass`. Output of `EmailWatcher._extract()` — one regex-matched line from an
unread email that looks like an actionable instruction.

| Field | Type | Notes |
|---|---|---|
| `email_id` | `str` | |
| `sender` | `str` | |
| `text` | `str` | The matched line |

## Frontend (TypeScript)

### `Task` — `frontend/lib/api.ts`
Mirrors the backend `Task` model field-for-field (`id, goal, team, state, result:
string \| null, created_at, updated_at`), all typed `string` (backend enums cross
the wire as plain strings).

### `AgentEvent` — `frontend/lib/api.ts`
Mirrors the backend `AgentEvent` model: `type: string, task_id: string, agent:
string, payload: Record<string, unknown>, ts: string`.

### `Skill` — `frontend/lib/api.ts`
Mirrors the backend `Skill` model: `name, version: string, triggers: string[],
body: string`.

### `Approval` — `frontend/app/approvals/page.tsx` (page-local, not exported)
`{ id: string; tool_name: string; args: Record<string, unknown>; state: string;
created_at: string }` — mirrors `ApprovalRequest`; declared inline in the page
component rather than in `lib/api.ts`.

No other TypeScript interfaces/types are defined in the frontend as of this
writing — `frontend/components/` does not exist; all views are page-level
components under `frontend/app/**/page.tsx` using the three shared interfaces
above plus the page-local `Approval` type.
