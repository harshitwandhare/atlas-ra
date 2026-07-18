# Security policy

## Reporting a vulnerability

Email **harshitwandhare45@gmail.com** with a description and reproduction steps.
You will get an acknowledgement within 72 hours. Please do not open a public issue
for anything exploitable.

## Threat model (read before deploying)

ATLAS is an agent system that can execute code on its host — that is its purpose,
and it changes what "secure deployment" means:

- **`run_python` / `run_powershell` are arbitrary code execution by design.** They
  are tagged `Risk.REVERSIBLE` and run **without** a human approval gate (only
  `Risk.DESTRUCTIVE` tools block on the `ApprovalQueue`). Never expose the API
  (`:8000`) beyond localhost, and never feed the orchestrator goals from untrusted
  input, unless you first re-tag those tools as `DESTRUCTIVE` or add authentication.
- **The API has no auth layer.** It binds `127.0.0.1` by default; keep it that way
  or put it behind an authenticating reverse proxy.
- **Prompt injection**: content ingested via `/ingest` (PDFs, subtitles, web
  tutorials) becomes provider context. Treat ingested third-party documents as
  untrusted instructions; the approval queue is the backstop for destructive
  actions, not a substitute for caution.
- **Secrets** are read from environment / OS keyring only. `.env` is git-ignored;
  `backend/.env.example` documents every variable with placeholders. CI deploys use
  GitHub Actions repo secrets.

## Supported versions

Only the latest tagged release receives fixes.
