# Contributing

- Conventional Commits (`feat:`, `fix:`, `docs:`...); semver releases.
- Python: `uv sync`, then `uv run ruff check . && uv run mypy src && uv run pytest`.
- Frontend: `npm run lint && npm run build`.
- Every behavior change needs a test; every design decision an ADR in `docs/adr/`.
- Skill playbook changes go through PR review like code.
