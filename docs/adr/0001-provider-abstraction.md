# ADR-0001: Provider abstraction over agent frameworks

- Status: Accepted
- Date: 2026-07-17

## Context
We want Claude Agent SDK's agentic quality now, but must not couple the orchestrator,
teams, or memory to one vendor. Future targets: LangGraph, local models (Ollama).

## Decision
Define a minimal `AgentProvider` protocol (`run(task, tools, context) -> AsyncIterator[AgentEvent]`)
plus a normalized `AgentEvent` union (message_delta, tool_call, tool_result, checkpoint,
done, error). All framework-specific code lives in `atlas/providers/<name>.py`.
Providers register by name and are selected via `ATLAS_PROVIDER` config.

## Consequences
- (+) Swapping/adding frameworks is additive; core untouched.
- (+) Events normalized once → tracing/UI/ledger work for every provider.
- (−) Lowest-common-denominator interface: provider-unique features must be adapted
  or exposed via capability flags.

## Alternatives considered
Direct SDK usage everywhere (lock-in leaks into every module); LangGraph-only
(vendor-neutral but re-implements agentic behavior the SDK already does better today).
