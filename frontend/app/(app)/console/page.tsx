"use client";
import { useState } from "react";
import { submitGoal } from "@/lib/api";
import { useEvents } from "@/lib/useEvents";

const EXAMPLES = [
  "Summarize how to fit Wan 2.2 in a 10GB VRAM budget",
  "Install StreamDiffusion and run a smoke test",
  "Draft a TouchDesigner OSC bridge checklist",
];

export default function ConsolePage() {
  const [goal, setGoal] = useState("");
  const [taskId, setTaskId] = useState<string | null>(null);
  const events = useEvents();
  const mine = taskId ? events.filter((e) => e.task_id === taskId) : [];

  const send = async (text?: string) => {
    const value = (text ?? goal).trim();
    if (!value) return;
    const { task_id } = await submitGoal(value);
    setTaskId(task_id);
    setGoal("");
  };

  return (
    <div className="max-w-3xl">
      <h1 className="text-xl font-semibold">Submit a goal</h1>
      <p className="mt-1 text-sm text-muted">
        The orchestrator routes it to a team, injects any matching skills, and streams every step
        back here until the Critic signs off.
      </p>

      <div className="mt-6 flex gap-2">
        <input
          value={goal}
          onChange={(e) => setGoal(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
          placeholder='e.g. "Install StreamDiffusion and run a smoke test"'
          className="flex-1 rounded-lg border border-line bg-surface px-4 py-3 outline-none transition-colors focus:border-brand-500"
        />
        <button
          onClick={() => send()}
          className="rounded-lg bg-brand-600 px-5 font-medium text-white transition-colors hover:bg-brand-500"
        >
          Run
        </button>
      </div>

      {!taskId && (
        <div className="mt-3 flex flex-wrap gap-2">
          {EXAMPLES.map((e) => (
            <button
              key={e}
              onClick={() => send(e)}
              className="rounded-full border border-line px-3 py-1 text-xs text-faint transition-colors hover:border-brand-500/40 hover:text-muted"
            >
              {e}
            </button>
          ))}
        </div>
      )}

      {taskId && (
        <div className="mt-6 space-y-2">
          <div className="font-mono text-xs text-faint">task {taskId}</div>
          {taskId === "t_preview" ? (
            <p className="text-sm text-faint">
              Nothing ran — this preview has no backend. The stream above is sample data.
            </p>
          ) : (
            mine.length === 0 && <p className="text-sm text-faint">Waiting for the first event…</p>
          )}
          {mine
            .slice()
            .reverse()
            .map((e, i) => (
              <div key={i} className="rounded border border-line bg-surface p-3 text-sm">
                <span className="mr-2 rounded bg-raised px-1.5 py-0.5 font-mono text-xs text-brand-400">
                  {e.type}
                </span>
                {String(e.payload.text ?? e.payload.tool ?? e.payload.state ?? "")}
              </div>
            ))}
        </div>
      )}
    </div>
  );
}
