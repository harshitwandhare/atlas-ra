# Contributing

## Workflow

1. Branch from `main`; open a PR — direct pushes to `main` are for release commits only.
2. [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`,
   `docs:`, `ci:`, `test:`); releases are semver tags with a `CHANGELOG.md` entry.
3. CI must be green: it runs exactly the commands below.

## Gates (run locally before pushing)

```bash
# backend
cd backend
uv sync --all-extras
uv run ruff check .
uv run mypy src          # strict — new code must be fully typed
uv run pytest -q
uv run python -m evals.run_evals   # behavioral evals must not regress

# frontend
cd ../frontend
npm ci
npm run lint && npm run build
```

## Rules of the codebase

- **Every behavior change ships with a test.** The suite covers the orchestrator
  lifecycle, providers, memory tiers, API, CLI, and an e2e path — extend the closest
  file in `backend/tests/`.
- **Providers stay behind the `AgentProvider` protocol** (ADR-0001). Framework
  imports must not leak outside `atlas/providers/<name>.py`, and a provider
  terminates with a normalized `DONE`/`ERROR` event — it never raises through the
  stream.
- **Destructive tools go through the approval queue** — enforced in
  `ToolRegistry.execute`, not in prompts. New tools must declare tier + risk.
- **Design decisions get an ADR** in `docs/adr/`; document reality, not aspiration
  (see `docs/REQUIREMENTS_AUDIT.md` for the standard of honesty expected).
- **Skill playbooks** (`skills/*.md`) are versioned front-matter markdown and go
  through PR review like code — bump `version` on edit.
