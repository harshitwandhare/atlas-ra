# Changelog

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
