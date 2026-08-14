import Link from "next/link";

import { ArchitectureDiagram } from "@/components/ArchitectureDiagram";
import { LifecycleDemo } from "@/components/LifecycleDemo";
import { Pipeline } from "@/components/Pipeline";
import { Reveal } from "@/components/Reveal";

const REPO = "https://github.com/harshitwandhare/atlas-ra";

const heroStats = [
  { value: "3", label: "swappable providers" },
  { value: "3", label: "memory tiers" },
  { value: "4", label: "execution tiers" },
  { value: "0", label: "unapproved destructive calls" },
];

const marquee = [
  "mypy --strict",
  "ruff lint + format",
  "pytest + pytest-asyncio",
  "scored eval regressions",
  "next lint + build",
  "OpenTelemetry spans",
  "Pydantic v2 boundaries",
  "uv lockfile",
  "Storybook + a11y addon",
  "Conventional Commits",
  "MIT licensed",
];

const problems = [
  {
    stat: "Stateless",
    label: "every run starts from zero",
    body: "A frontier model that solved your problem last week remembers none of it today. Nothing accumulates, so the same mistakes get made at the same cost, forever.",
  },
  {
    stat: "Unverified",
    label: "confident output, no second look",
    body: "Agents mark their own homework. Without an independent reviewer between the run and the result, a plausible-sounding failure is indistinguishable from success.",
  },
  {
    stat: "Unbounded",
    label: "delete first, ask never",
    body: "Give an agent shell access and the blast radius is your filesystem. Prompting it to be careful is not a control — enforcement has to live in code.",
  },
];

const capabilities: { title: string; body: string; mono: string; span?: string }[] = [
  {
    title: "Provider abstraction, not provider lock-in",
    body: "AgentProvider is a Protocol with one method. Claude Agent SDK, LangGraph, and a zero-dependency Ollama HTTP client all satisfy it, and ATLAS_PROVIDER picks between them at runtime. Nothing above the protocol knows which one is running.",
    mono: "ATLAS_PROVIDER=ollama",
    span: "lg:col-span-2",
  },
  {
    title: "Memory in three tiers",
    body: "Episodic runs live in SQLite, semantic documents in a keyword-overlap store shaped for a drop-in vector backend, and procedural know-how in git-versioned markdown playbooks.",
    mono: "skills/*.md",
  },
  {
    title: "Approval queue, enforced in code",
    body: "Tools declare a risk class. Destructive ones route through ApprovalQueue and block on an asyncio.Event until a human clicks approve or deny in the dashboard.",
    mono: "Risk.DESTRUCTIVE",
  },
  {
    title: "Critic before completion",
    body: "The reviewer reads the transcript and answers approve or revise. A task reaches DONE only through approval — a revise verdict costs a retry with feedback attached.",
    mono: "approve | revise",
  },
  {
    title: "Ingestion that drafts its own playbooks",
    body: "Feed it a PDF, deck, doc, or video transcript; the pipeline extracts imperative steps into a draft skill. Drafts are never auto-promoted — you review before they join procedural memory.",
    mono: "POST /ingest",
    span: "lg:col-span-2",
  },
];

const engineering = [
  {
    k: "strict",
    v: "mypy across the backend",
    d: "Pydantic v2 models at every boundary; the provider seam is a typed Protocol",
  },
  {
    k: "evals",
    v: "scored regressions in CI",
    d: "backend/evals runs on every push, results tracked in results.jsonl",
  },
  {
    k: "2 jobs",
    v: "gate every pull request",
    d: "backend: ruff → mypy → pytest → evals · frontend: next lint → next build",
  },
  {
    k: "audited",
    v: "every step is on the record",
    d: "each AgentEvent persists to the ledger and opens an OpenTelemetry span",
  },
];

export default function LandingPage() {
  return (
    <>
      {/* Hero */}
      <section className="relative overflow-hidden border-b border-line">
        <div className="bg-grid bg-grid-fade absolute inset-0" aria-hidden="true" />
        <div
          aria-hidden="true"
          className="absolute right-[-15%] top-[-10%] h-[460px] w-[460px] rounded-full bg-brand-500/15 blur-[130px]"
        />

        <div className="relative mx-auto grid max-w-6xl gap-12 px-5 py-20 sm:px-6 sm:py-28 lg:grid-cols-[1.05fr_0.95fr] lg:items-center">
          <div>
            <p className="inline-flex items-center gap-2 rounded-full border border-line bg-white/[0.03] px-3 py-1 text-xs font-medium tracking-wide text-brand-300">
              <span className="relative flex h-2 w-2">
                <span className="absolute h-full w-full animate-ping rounded-full bg-brand-400 opacity-60" />
                <span className="h-2 w-2 rounded-full bg-brand-400" />
              </span>
              Open source · MIT · runs fully local
            </p>

            <h1 className="mt-6 text-4xl font-bold leading-[1.05] tracking-tight sm:text-6xl">
              Autonomy you can
              <br />
              <span className="bg-gradient-to-r from-brand-400 to-brand-300 bg-clip-text text-transparent">
                actually audit.
              </span>
            </h1>

            <p className="mt-6 max-w-xl text-lg leading-relaxed text-muted">
              ATLAS is a multi-team agent system. An orchestrator decomposes each goal, routes it to
              a specialist team, gates destructive work behind human approval, and refuses to mark
              anything done until a{" "}
              <strong className="font-semibold text-ink">Critic has reviewed the transcript</strong>.
              Every step streams to a dashboard and lands in an append-only ledger.
            </p>

            <div className="mt-9 flex flex-wrap items-center gap-4">
              <Link
                href="/console"
                className="rounded-lg bg-brand-500 px-6 py-3 font-medium text-black shadow-glow transition-colors hover:bg-brand-400"
              >
                Open the dashboard
              </Link>
              <a
                href={REPO}
                target="_blank"
                rel="noopener noreferrer"
                className="rounded-lg border border-line px-6 py-3 font-medium text-ink transition-colors hover:bg-white/5"
              >
                Read the source ↗
              </a>
            </div>

            <dl className="mt-12 grid max-w-lg grid-cols-2 gap-x-8 gap-y-5 sm:grid-cols-4">
              {heroStats.map((s) => (
                /* Reversed so the value reads on top while dt still precedes dd. */
                <div key={s.label} className="flex flex-col-reverse">
                  <dt className="mt-0.5 text-xs leading-snug text-faint">{s.label}</dt>
                  <dd className="text-2xl font-bold text-ink">{s.value}</dd>
                </div>
              ))}
            </dl>
          </div>

          <div className="min-w-0 lg:pl-4">
            <LifecycleDemo />
          </div>
        </div>
      </section>

      {/* Quality marquee */}
      <section aria-label="Engineering quality checks" className="border-b border-line bg-surface py-5">
        <div className="relative overflow-hidden">
          <div className="animate-marquee flex w-max gap-3 motion-reduce:flex-wrap motion-reduce:justify-center">
            {[...marquee, ...marquee].map((b, i) => (
              <span
                key={`${b}-${i}`}
                aria-hidden={i >= marquee.length}
                className="whitespace-nowrap rounded-full border border-line bg-bg px-4 py-1.5 font-mono text-xs text-faint"
              >
                {b}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* The problem */}
      <section className="border-b border-line">
        <div className="mx-auto max-w-6xl px-5 py-16 sm:px-6 sm:py-24">
          <Reveal>
            <p className="font-mono text-sm font-medium uppercase tracking-widest text-brand-400">
              Why this exists
            </p>
            <h2 className="mt-3 max-w-2xl text-2xl font-bold tracking-tight sm:text-4xl">
              Frontier agents are powerful. They are also forgetful, unchecked, and unbounded.
            </h2>
            <p className="mt-4 max-w-2xl leading-relaxed text-muted">
              The model is rarely the bottleneck. What is missing is the engineering around it —
              the part that makes an autonomous system safe to leave running.
            </p>
          </Reveal>
          <div className="mt-12 grid gap-5 sm:grid-cols-3">
            {problems.map((p, i) => (
              <Reveal key={p.label} delay={i * 0.08}>
                <div className="h-full rounded-2xl border border-line bg-surface p-6">
                  <p className="text-3xl font-bold tracking-tight text-brand-400">{p.stat}</p>
                  <p className="mt-1.5 font-medium text-ink">{p.label}</p>
                  <p className="mt-3 text-sm leading-relaxed text-muted">{p.body}</p>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section id="how" className="relative border-b border-line bg-surface scroll-mt-16">
        <div className="bg-grid absolute inset-0 opacity-40" aria-hidden="true" />
        <div className="relative mx-auto max-w-6xl px-5 py-16 sm:px-6 sm:py-24">
          <Reveal>
            <p className="font-mono text-sm font-medium uppercase tracking-widest text-brand-400">
              How it works
            </p>
            <h2 className="mt-3 max-w-2xl text-2xl font-bold tracking-tight sm:text-4xl">
              One goal in. Five checkpoints before anything counts as done.
            </h2>
          </Reveal>
          <div className="mt-14">
            <Pipeline />
          </div>
        </div>
      </section>

      {/* Architecture */}
      <section id="architecture" className="border-b border-line scroll-mt-16">
        <div className="mx-auto max-w-6xl px-5 py-16 sm:px-6 sm:py-24">
          <Reveal>
            <p className="font-mono text-sm font-medium uppercase tracking-widest text-brand-400">
              Architecture
            </p>
            <h2 className="mt-3 max-w-2xl text-2xl font-bold tracking-tight sm:text-4xl">
              Six layers, one seam that matters.
            </h2>
            <p className="mt-4 max-w-2xl leading-relaxed text-muted">
              Everything above the provider protocol is ours: routing, memory, approvals,
              verification, observability. Everything below it is replaceable. Swap the agent
              runtime and the guarantees do not move.
            </p>
          </Reveal>
          <Reveal delay={0.1}>
            <div className="mt-12">
              <ArchitectureDiagram />
            </div>
          </Reveal>
          <Reveal delay={0.16}>
            <div className="mt-6 flex flex-wrap gap-4 text-sm">
              <a
                href={`${REPO}/blob/main/docs/ARCHITECTURE.md`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-muted underline-offset-4 transition-colors hover:text-brand-300 hover:underline"
              >
                Full task lifecycle and memory paths ↗
              </a>
              <a
                href={`${REPO}/tree/main/docs/adr`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-muted underline-offset-4 transition-colors hover:text-brand-300 hover:underline"
              >
                Architecture decision records ↗
              </a>
            </div>
          </Reveal>
        </div>
      </section>

      {/* Capabilities */}
      <section id="capabilities" className="border-b border-line bg-surface scroll-mt-16">
        <div className="mx-auto max-w-6xl px-5 py-16 sm:px-6 sm:py-24">
          <Reveal>
            <p className="font-mono text-sm font-medium uppercase tracking-widest text-brand-400">
              Capabilities
            </p>
            <h2 className="mt-3 max-w-2xl text-2xl font-bold tracking-tight sm:text-4xl">
              The engineering that makes autonomy trustworthy.
            </h2>
          </Reveal>
          <div className="mt-12 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {capabilities.map((c, i) => (
              <Reveal key={c.title} delay={i * 0.06} className={c.span}>
                <div className="h-full rounded-2xl border border-line bg-bg p-6 transition-colors hover:border-brand-500/30">
                  <h3 className="text-lg font-semibold tracking-tight text-ink">{c.title}</h3>
                  <p className="mt-2 text-sm leading-relaxed text-muted">{c.body}</p>
                  <code className="mt-4 inline-block rounded-md bg-raised px-2.5 py-1 font-mono text-xs text-brand-300">
                    {c.mono}
                  </code>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* Engineering */}
      <section id="engineering" className="relative overflow-hidden border-b border-line scroll-mt-16">
        <div className="bg-grid absolute inset-0 opacity-40" aria-hidden="true" />
        <div className="relative mx-auto max-w-6xl px-5 py-16 sm:px-6 sm:py-24">
          <Reveal>
            <p className="font-mono text-sm font-medium uppercase tracking-widest text-brand-400">
              Built like production software
            </p>
            <h2 className="mt-3 max-w-2xl text-2xl font-bold tracking-tight sm:text-4xl">
              Because the codebase is part of the argument.
            </h2>
            <p className="mt-4 max-w-2xl leading-relaxed text-muted">
              Open the repo and judge it the way a staff engineer would: typed end to end, tested,
              gated, documented, and honest about what is heuristic today versus what is finished.
            </p>
          </Reveal>
          <div className="mt-12 grid gap-px overflow-hidden rounded-2xl border border-line bg-line sm:grid-cols-2 lg:grid-cols-4">
            {engineering.map((e, i) => (
              <Reveal key={e.v} delay={i * 0.08}>
                <div className="h-full bg-surface p-6">
                  <p className="font-mono text-2xl font-bold text-brand-400">{e.k}</p>
                  <p className="mt-2 font-medium text-ink">{e.v}</p>
                  <p className="mt-1.5 text-xs leading-relaxed text-faint">{e.d}</p>
                </div>
              </Reveal>
            ))}
          </div>
          <Reveal delay={0.2}>
            <p className="mt-6 text-sm text-faint">
              The{" "}
              <a
                href={`${REPO}/blob/main/docs/REQUIREMENTS_AUDIT.md`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-muted underline underline-offset-4 transition-colors hover:text-brand-300"
              >
                requirements audit
              </a>{" "}
              maps every claim to the code that backs it — including the parts still heuristic.
            </p>
          </Reveal>
        </div>
      </section>

      {/* Quickstart + CTA */}
      <section>
        <div className="mx-auto max-w-6xl px-5 py-16 sm:px-6 sm:py-24">
          <div className="grid items-center gap-10 lg:grid-cols-2">
            <Reveal className="min-w-0">
              <p className="font-mono text-sm font-medium uppercase tracking-widest text-brand-400">
                Local by default
              </p>
              <h2 className="mt-3 text-2xl font-bold tracking-tight sm:text-4xl">
                Point it at Ollama and nothing leaves the machine.
              </h2>
              <p className="mt-4 leading-relaxed text-muted">
                The screenshots in the README come from a Windows workstation running{" "}
                <code className="rounded bg-raised px-1.5 py-0.5 font-mono text-xs text-brand-300">
                  llama3.2:3b
                </code>{" "}
                with zero cloud calls. Secrets come from the environment or the OS keyring, the
                ledger is a local SQLite file, and skills are plain markdown you can read in a
                diff.
              </p>
            </Reveal>
            <Reveal delay={0.1} className="min-w-0">
              <div className="rounded-2xl border border-line bg-surface p-5 shadow-card sm:p-8">
                <h3 className="text-xl font-semibold tracking-tight text-ink">Run it in a minute</h3>
                <pre className="mt-4 overflow-x-auto rounded-xl bg-bg p-4 font-mono text-xs leading-7 text-muted sm:text-sm">
                  <code>{`cd backend
uv sync --all-extras
cp .env.example .env     # ATLAS_PROVIDER=ollama
uv run atlas serve       # API on :8000
uv run atlas goal "..."  # watch it move`}</code>
                </pre>
                <div className="mt-6 flex flex-wrap gap-3">
                  <Link
                    href="/console"
                    className="rounded-lg bg-brand-500 px-5 py-2.5 text-sm font-medium text-black transition-colors hover:bg-brand-400"
                  >
                    Open the dashboard
                  </Link>
                  <Link
                    href="/ledger"
                    className="rounded-lg border border-line px-5 py-2.5 text-sm font-medium text-ink transition-colors hover:bg-white/5"
                  >
                    Browse the ledger
                  </Link>
                </div>
              </div>
            </Reveal>
          </div>
        </div>
      </section>
    </>
  );
}
