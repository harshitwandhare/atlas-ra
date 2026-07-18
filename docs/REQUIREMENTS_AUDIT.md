# Requirements audit

Honest mapping of the original project brief to what ATLAS implements as of v0.3.0.
"✅" means implemented and tested; "◐" means partially implemented with the gap named;
"🗺" means designed (interfaces/docs exist) but not yet executable. No claim below is
aspirational — each row was verified against the source.

| # | Original requirement | Status | Where / gap |
|---|---|---|---|
| 1 | Multi-team environment of agents | ✅ | Three teams (`systems`, `research`, `ops`) + a Critic reviewer; keyword router assigns goals (`orchestrator/core.py`). Router is deliberately simple — LLM-based routing is the documented next step (ADR note in source). |
| 2 | Works end-to-end as a research assistant | ◐ | Goal → route → provider run → Critic review → ledger → dashboard works live (verified on this machine). The **tool-execution loop is not wired**: teams declare tool lists and `executors/registry.py` implements run_python/run_powershell/delete_path, but no provider currently invokes registry tools mid-run. Until then, tasks produce analysis/text, not host actions. |
| 3 | Full access over the laptop (screen control, browsing) | 🗺 | Tier model designed (1 Python → 2 PowerShell → 3 browser → 4 screen) and Tier 1–2 executors implemented + tested. Tier 3 (browser) and Tier 4 (screen/`pywinauto`) executors are roadmap (`docs/ROADMAP.md`). |
| 4 | Windows as a server | ✅ | Runs natively on Windows (verified); CI also proves Linux. |
| 5 | Highest quality / industry standard | ✅ | mypy `--strict`, ruff, pytest (unit + integration + e2e), behavioral evals gating CI, lockfiles committed, typed protocols at every seam, ADRs, CI/CD with Vercel deploys. |
| 6 | On GitHub as a package/library | ✅ | Private repo; backend is a proper hatchling package (`pip install ./backend` gives the `atlas` CLI). |
| 7 | Browse the internet | ◐ | Ingestion pipeline fetches video subtitles (yt-dlp) and parses PDF/PPTX/DOCX; general web browsing by agents is Tier 3 (roadmap). |
| 8 | Never forgets, keeps getting better | ◐ | Three-tier memory is real: episodic ledger (SQLite, permanent), semantic store (append-only JSONL + ingest), procedural skills (front-matter playbooks injected into matching runs). The **improvement loop is manual**: the ingest pipeline drafts procedures from tutorials, but auto-distilling a finished task into a new skill file is not implemented — the Critic's docstring mentions it; the code does not do it yet. |
| 9 | Human-in-the-loop safety | ✅ | Destructive tools block on the approval queue (dashboard + API); tested. Reversible-tier tools run ungated — documented trade-off. |
| 10 | FAANG-grade portfolio project, properly named | ✅ | ATLAS — Autonomous Task & Lab Assistant System. |
| 11 | StreamDiffusion installed and usable | ✅ | Installed and benchmarked on this machine (see `skills/streamdiffusion-windows-install.md`); `scripts/launch_streamdiffusion_demo.ps1` launches it. |
| 12 | ComfyUI workflows for LoRA training + video gen | ✅ | `workflows/comfyui/` — Wan 2.2 i2v within 10 GB VRAM and LoRA training, with exact model/custom-node requirements documented. |
| 13 | Operate TouchDesigner | ◐ | Full operating guide (`workflows/touchdesigner/`) against the local StreamDiffusion install; automated TD control by the ops team requires the Tier 3/4 executors (roadmap). |
| 14 | Proper versioning, no legacy/incompatible code | ✅ | `docs/VERSIONS.md` pins every runtime; uv + npm lockfiles committed; CI proves the pinned set on every push. |

## The three real gaps, in priority order

1. **Wire the tool loop** — pass team tools into the Claude Agent SDK run and route
   tool calls through `ToolRegistry` (approval-gated). This turns ATLAS from an
   analyst into an operator and is the highest-leverage remaining work.
2. **Auto-distillation** — on `DONE`, have the Critic write a versioned skill file
   from the transcript so the system compounds without manual curation.
3. **Tier 3/4 executors** — browser (Playwright) and screen (`pywinauto`) tools,
   which unlock requirements 3, 7, and 13 fully.
