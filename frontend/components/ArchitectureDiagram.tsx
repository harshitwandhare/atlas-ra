const layers: { label: string; caption: string; nodes: string[]; accent?: boolean }[] = [
  {
    label: "Dashboard",
    caption: "Next.js 14 · App Router",
    nodes: ["Console", "Activity", "Ledger", "Skills", "Approvals"],
  },
  {
    label: "Gateway",
    caption: "FastAPI · REST + WebSocket",
    nodes: ["/goals", "/tasks", "/skills", "/approvals", "/ingest", "/ws"],
  },
  {
    label: "Orchestrator",
    caption: "route → run → review → transition",
    nodes: ["Router", "Runner", "Retry loop", "Critic gate"],
    accent: true,
  },
  {
    label: "Teams",
    caption: "prompts + declared tools per team",
    nodes: ["Systems", "Research", "Ops", "Critic"],
  },
  {
    label: "Providers",
    caption: "AgentProvider protocol · ATLAS_PROVIDER",
    nodes: ["Claude Agent SDK", "LangGraph", "Ollama"],
  },
  {
    label: "Memory",
    caption: "three tiers, three lifetimes",
    nodes: ["Episodic — SQLite", "Semantic — JSONL store", "Procedural — skills/*.md"],
  },
];

export function ArchitectureDiagram() {
  return (
    <div className="overflow-hidden rounded-2xl border border-line bg-surface">
      {layers.map((layer, i) => (
        <div
          key={layer.label}
          className={`relative border-line px-5 py-5 sm:px-7 ${i < layers.length - 1 ? "border-b" : ""} ${
            layer.accent ? "bg-brand-500/[0.06]" : ""
          }`}
        >
          <div className="grid gap-4 sm:grid-cols-[190px_1fr] sm:items-center">
            <div>
              <p
                className={`font-mono text-xs uppercase tracking-widest ${
                  layer.accent ? "text-brand-400" : "text-faint"
                }`}
              >
                {layer.label}
              </p>
              <p className="mt-1 text-xs leading-relaxed text-faint">{layer.caption}</p>
            </div>
            <div className="flex flex-wrap gap-2">
              {layer.nodes.map((n) => (
                <span
                  key={n}
                  className={`rounded-lg border px-3 py-1.5 font-mono text-xs ${
                    layer.accent
                      ? "border-brand-500/30 bg-brand-500/10 text-brand-300"
                      : "border-line bg-bg text-muted"
                  }`}
                >
                  {n}
                </span>
              ))}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
