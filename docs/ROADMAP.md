# Roadmap

## V1 (current) — Trustworthy core
- [x] Provider abstraction + Claude Agent SDK reference provider
- [x] Task ledger + orchestrator state machine
- [x] Systems team + Critic review loop
- [x] Three-tier memory, skill distillation
- [x] FastAPI + WebSocket event bus
- [x] Next.js dashboard (chat, activity, ledger, skills, approvals)
- [x] Eval harness: 5 scored RA regression tasks in CI
- [x] OpenTelemetry export wired to Langfuse

## V2 — Breadth
- [x] Comms team: Gmail watcher for key contacts, draft replies, human-approved send
- [x] Universal ingestion: video (subtitles/Whisper), PDF (incl. OCR), PPTX/DOCX/XLSX, web → semantic memory
- [x] Procedure extractor: tutorial video/doc → draft skill playbook
- [x] Research team definition + routing (Playwright tool wiring: V2.1)
- [x] Ops team (Windows control: PowerShell, pywinauto; screen tier behind approval)
- [x] LangGraph provider + local-model provider (Ollama)
- [ ] Eval dashboard: score trends across versions

## V3 — Scale & polish
- [ ] Multi-goal concurrency with VRAM-aware scheduling
- [ ] TouchDesigner deep integration: StreamDiffusionTD real-time pipeline, network generation via td Python API
- [ ] Shareable skill playbook format
- [ ] Notification surface: Telegram alerts for approvals/escalations (adapter pattern from job-sentinel)
