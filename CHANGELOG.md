# Changelog

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
