"use client";
import { useState } from "react";
import { submitGoal } from "@/lib/api";
import { useEvents } from "@/lib/useEvents";

export default function ChatPage() {
  const [goal, setGoal] = useState("");
  const [taskId, setTaskId] = useState<string | null>(null);
  const events = useEvents();
  const mine = taskId ? events.filter((e) => e.task_id === taskId) : [];

  const send = async () => {
    if (!goal.trim()) return;
    const { task_id } = await submitGoal(goal);
    setTaskId(task_id);
    setGoal("");
  };

  return (
    <div className="mx-auto max-w-3xl">
      <h1 className="mb-4 text-xl font-semibold">Submit a goal</h1>
      <div className="flex gap-2">
        <input
          value={goal}
          onChange={(e) => setGoal(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
          placeholder='e.g. "Install StreamDiffusion and run a smoke test"'
          className="flex-1 rounded-lg border border-zinc-700 bg-zinc-900 px-4 py-3 outline-none focus:border-emerald-500"
        />
        <button onClick={send} className="rounded-lg bg-emerald-600 px-5 font-medium hover:bg-emerald-500">
          Run
        </button>
      </div>
      {taskId && (
        <div className="mt-6 space-y-2">
          <div className="text-xs text-zinc-500">task {taskId}</div>
          {mine.slice().reverse().map((e, i) => (
            <div key={i} className="rounded border border-zinc-800 bg-zinc-900 p-3 text-sm">
              <span className="mr-2 rounded bg-zinc-800 px-1.5 py-0.5 text-xs text-emerald-400">{e.type}</span>
              {String(e.payload.text ?? e.payload.tool ?? e.payload.state ?? "")}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
