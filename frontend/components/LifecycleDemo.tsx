"use client";

import { useEffect, useState } from "react";

type Step = { type: string; agent: string; text: string; tone?: "brand" | "sky" | "amber" };

// Mirrors a real captured run: goal -> route -> skill injection -> model output
// -> critic review -> done. Same event names the WebSocket bus emits.
const STEPS: Step[] = [
  { type: "task_created", agent: "orchestrator", text: "Fit Wan 2.2 5B into a 10GB VRAM budget", tone: "sky" },
  { type: "routed", agent: "orchestrator", text: "team=research (keyword match)", tone: "sky" },
  { type: "skill_matched", agent: "memory", text: "touchdesigner-pipeline v1.2.0 injected", tone: "brand" },
  { type: "message_delta", agent: "research", text: "Load the 5B checkpoint in fp8, offload the text encoder..." },
  { type: "state_change", agent: "orchestrator", text: "running → review", tone: "amber" },
  { type: "critic_review", agent: "critic", text: "approve — transcript grounded, no errors", tone: "brand" },
  { type: "state_change", agent: "orchestrator", text: "review → done", tone: "brand" },
];

const toneClass: Record<string, string> = {
  brand: "bg-brand-500/15 text-brand-300",
  sky: "bg-sky-500/15 text-sky-300",
  amber: "bg-amber-500/15 text-amber-300",
};

export function LifecycleDemo() {
  const [count, setCount] = useState(0);

  useEffect(() => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      setCount(STEPS.length);
      return;
    }
    if (count >= STEPS.length) {
      const restart = setTimeout(() => setCount(0), 5200);
      return () => clearTimeout(restart);
    }
    const next = setTimeout(() => setCount((c) => c + 1), count === 0 ? 500 : 900);
    return () => clearTimeout(next);
  }, [count]);

  return (
    <div className="w-full overflow-hidden rounded-2xl border border-line bg-surface shadow-card">
      <div className="flex items-center gap-2 border-b border-line bg-raised px-4 py-3">
        <span className="relative flex h-2 w-2">
          <span className="absolute h-full w-full animate-ping rounded-full bg-brand-400 opacity-60" />
          <span className="h-2 w-2 rounded-full bg-brand-400" />
        </span>
        <span className="font-mono text-xs text-muted">ws://localhost:8000/ws</span>
        <span className="ml-auto font-mono text-[10px] uppercase tracking-widest text-faint">live</span>
      </div>

      <ul className="min-h-[332px] space-y-2 p-4">
        {STEPS.slice(0, count).map((s, i) => (
          <li
            key={i}
            className="reveal is-in rounded-lg border border-line bg-bg px-3 py-2.5"
            style={{ transitionDelay: "0s" }}
          >
            <div className="flex items-center gap-2">
              <span
                className={`rounded px-1.5 py-0.5 font-mono text-[10px] ${toneClass[s.tone ?? ""] ?? "bg-white/5 text-muted"}`}
              >
                {s.type}
              </span>
              <span className="font-mono text-[10px] text-faint">{s.agent}</span>
            </div>
            <p className="mt-1.5 text-sm leading-snug text-muted">{s.text}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}
