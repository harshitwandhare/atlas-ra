# ADR-0002: Three-tier memory (episodic / semantic / procedural)

- Status: Accepted
- Date: 2026-07-17

## Context
Context windows are finite; naive agents forget across sessions and re-derive
solutions. The system must demonstrably improve at recurring RA work.

## Decision
1. **Episodic** — SQLite ledger of every task run (goal, steps, errors, outcome, checkpoints).
2. **Semantic** — LanceDB local vector store; top-k retrieval into task context.
3. **Procedural** — git-versioned markdown playbooks in `skills/`, written/updated by
   the Critic after successful runs, loaded by trigger-matching at task start.

Long runs checkpoint structured summaries to the ledger every N steps for lossless resume.

## Consequences
- (+) Learning is inspectable and diffable (skills are reviewable markdown, not weights).
- (+) All stores local/embedded — no external services, works offline.
- (−) Skill quality depends on Critic prompts; mitigated by human review of skill diffs.
