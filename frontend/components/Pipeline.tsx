import { Reveal } from "@/components/Reveal";

const stages: { n: string; title: string; body: string; mono: string }[] = [
  {
    n: "01",
    title: "Decompose & route",
    body: "The orchestrator writes the goal into the SQLite ledger as a task, then keyword-routes it to a specialist team: systems, research, or ops.",
    mono: "_route(goal) -> team",
  },
  {
    n: "02",
    title: "Recall what it knows",
    body: "Procedural memory matches versioned markdown playbooks by trigger keyword and injects them into the prompt, so past lessons show up in the next run.",
    mono: "SkillStore.match(goal)",
  },
  {
    n: "03",
    title: "Execute behind a gate",
    body: "The team runs against whichever provider is configured. Tools declare a tier and a risk class; destructive ones stop at the approval queue until a human decides.",
    mono: "Risk.DESTRUCTIVE -> ApprovalQueue",
  },
  {
    n: "04",
    title: "Verify before done",
    body: "A Critic reads the run transcript and returns approve or revise. Only approval moves a task to DONE; revise sends it back with feedback for another attempt.",
    mono: "Critic.review(goal, transcript)",
  },
  {
    n: "05",
    title: "Persist & stream",
    body: "Every normalized AgentEvent lands in the episodic ledger, gets wrapped in an OpenTelemetry span, and fans out over WebSocket to the dashboard as it happens.",
    mono: "AgentEvent -> ledger + /ws",
  },
];

export function Pipeline() {
  return (
    <ol className="relative space-y-4 border-l border-line pl-6 sm:pl-8">
      {stages.map((s, i) => (
        <Reveal key={s.n} delay={i * 0.06}>
          <li className="relative">
            <span className="absolute -left-[33px] top-5 h-2.5 w-2.5 rounded-full bg-brand-500 ring-4 ring-bg sm:-left-[41px]" />
            <div className="rounded-2xl border border-line bg-surface p-5 sm:p-6">
              <div className="flex flex-wrap items-baseline gap-3">
                <span className="font-mono text-xs text-brand-400">{s.n}</span>
                <h3 className="text-lg font-semibold tracking-tight text-ink">{s.title}</h3>
              </div>
              <p className="mt-2 max-w-2xl text-sm leading-relaxed text-muted">{s.body}</p>
              <code className="mt-4 inline-block rounded-md bg-bg px-2.5 py-1 font-mono text-xs text-brand-300">
                {s.mono}
              </code>
            </div>
          </li>
        </Reveal>
      ))}
    </ol>
  );
}
