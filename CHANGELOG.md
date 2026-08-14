# Changelog

## 0.4.1 — 2026-08-14
### Fixed
- Landing page claimed **4 execution tiers**. `executors/registry.py` documents
  four (1=API/code, 2=CLI, 3=browser, 4=screen), but `default_registry()` only
  registers tools at tiers 1 and 2 — tiers 3 and 4 are roadmap, as
  `docs/REQUIREMENTS_AUDIT.md` already stated. Now reads "2 execution tiers
  live".
- Hero stats used `flex-col-reverse`, which packs from the bottom, so the one
  label wrapping to two lines pushed its number out of line with the other
  three. Ordering within a normal column packs from the top instead.
- Dashboard: `/console` centred itself in `max-w-3xl` while the preview banner
  filled the whole `main`, so their left edges did not align. All dashboard
  screens now share one `max-w-6xl` container.
### Added
- `scripts/capture_screens.py` — reproducible README screenshots via headless
  chromium, with animations frozen so reruns are deterministic. Writes to
  `docs/screenshots/preview/`, kept separate from the real-run captures it
  cannot reproduce.
- README: landing-page hero plus a gallery of the site and dashboard.

## 0.4.0 — 2026-08-14
### Added
- Landing page at `/` — what ATLAS is, why it exists, the five-checkpoint task
  lifecycle, a layer diagram of the architecture, capabilities, and the
  engineering gates. Previously the root route was the goal-submission view, so
  anyone opening the deployed site landed on an unexplained text input.
- Hosted-preview mode: when the dashboard cannot reach a backend it serves
  sample tasks, skills, approvals, and events, and shows a notice explaining
  that the data is illustrative and that ATLAS runs locally. Detection is
  per-request, so a local run with `atlas serve` up shows real data with no
  configuration, and starting the server swaps the samples out without a
  reload.
### Changed
- Goal submission moved from `/` to `/console`; dashboard screens now live in an
  `(app)` route group behind the existing sidebar.
- Dashboard styling moved onto CSS custom properties wired into Tailwind
  (`bg`/`surface`/`raised`/`ink`/`muted`/`faint`/`line`/`brand`), replacing
  ad-hoc `zinc-*` classes.
### Fixed
- API: `GET /tasks/{task_id}` returned HTTP 200 with an `{"error": "not found"}`
  body for an unknown id, so callers had to inspect the payload to tell a miss
  from a hit. Now returns 404.
- API: `POST /approvals/{request_id}` indexed the request dict directly, so an
  unknown id raised a bare `KeyError` that surfaced as an unhandled 500. Now
  returns 404, with `ApprovalQueue.resolve()` raising an explicit `KeyError`.
- Landing page: hero stats paired an `sr-only` `<dt>` with a visible `<dd>`
  holding the same text, so screen readers announced every label twice.
- `backend/uv.lock` still pinned `atlas-ra` at 0.3.1 after the v0.3.2 release.

## 0.3.2 — 2026-07-30
### Added
- Ledger: `GET /tasks` accepts a `state` query param so the dashboard can filter
  the task table by status instead of always showing everything.

## 0.3.1 — 2026-07-23
### Fixed
- Semantic memory: `SemanticStore.search` skips blank or half-written lines in
  the append-only `docs.jsonl` instead of raising `JSONDecodeError`, so a write
  interrupted by a crash can no longer take down retrieval. Matches how the
  skill store already tolerates malformed files.
### Added
- Brand: geometric peak logo (light/dark) wired into the README and dashboard.
- Docs: SECURITY.md policy and an expanded CONTRIBUTING guide for the public
  open-source release.

## 0.3.0 — 2026-07-18
### Fixed
- Claude provider: SDK stream failures now yield a normalized ERROR event instead of
  raising out of the async generator (observed live: "Claude Code returned an error
  result" with SDK 0.2.121 / CLI 2.1.58)
- Orchestrator: task runs are supervised — any provider crash transitions the task to
  ESCALATED and emits ERROR through the event bus; previously the asyncio task died
  silently and the ledger row was stuck in RUNNING forever
- Ollama provider: blocking urllib call moved off the event loop (asyncio.to_thread);
  the API and dashboard no longer freeze for the duration of a local generation
### Added
- CLI: `atlas goal "…"` and `atlas tasks` (the docstring advertised goal; now it exists)
- Config: `ATLAS_OLLAMA_MODEL` / `ATLAS_OLLAMA_BASE_URL`
- Test suite 15 → 55: orchestrator lifecycle (success/retry/escalate/crash/skills),
  providers (registry, Ollama paths, Claude SDK failure + normalization), API endpoints
  incl. WebSocket, CLI (all commands, offline), memory tiers, and a full-stack e2e test
- ComfyUI workflows: Wan 2.2 5B i2v within 10 GB VRAM; LoRA training on native
  TrainLoraNode — with model/custom-node requirement docs
- TouchDesigner runbook against the local StreamDiffusion install + PowerShell launcher
- Docs: OPERATIONS.md, REQUIREMENTS_AUDIT.md (honest brief-vs-built), VERSIONS.md
- README: real dashboard screenshots from a fully local run (Ollama llama3.2:3b)

## 0.2.0 — 2026-07-17
### Added
- Tiered tool executors (run_python, run_powershell) with hard timeouts
- ApprovalQueue: destructive actions + outbound email are human-gated in code, not prompts
- Universal ingestion: PDF/PPTX/DOCX/TXT/SRT + video subtitles (yt-dlp); procedure
  extractor turns tutorials into draft skill playbooks
- Comms: email adapter protocol (IMAP reference), watcher with action-item extraction,
  send path that cannot bypass approval; Telegram notifier
- Providers: Ollama (local/offline) and LangGraph (vendor-neutral) alongside Claude
- Teams: Research and Ops definitions; keyword task router in the orchestrator
- Eval harness with scored regression cases, wired into CI (fails on regression)
- OpenTelemetry span per agent event (no-op without an exporter)
- Functional Approvals dashboard page; /approvals and /ingest API endpoints

## 0.1.0 — 2026-07-17
Initial scaffold: provider abstraction (Claude Agent SDK), task ledger, skills store,
orchestrator + Systems team + Critic loop, FastAPI + WebSocket bus, Next.js dashboard,
4 RA skill playbooks, CI, docs + ADRs.
