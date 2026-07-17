"use client";
import { useEvents } from "@/lib/useEvents";

export default function ActivityPage() {
  const events = useEvents();
  return (
    <div>
      <h1 className="mb-4 text-xl font-semibold">Live activity</h1>
      <div className="space-y-1 font-mono text-xs">
        {events.map((e, i) => (
          <div key={i} className="flex gap-3 rounded border border-zinc-800 bg-zinc-900 px-3 py-2">
            <span className="text-zinc-500">{new Date(e.ts).toLocaleTimeString()}</span>
            <span className="text-emerald-400">{e.agent}</span>
            <span className="text-sky-400">{e.type}</span>
            <span className="truncate text-zinc-300">{JSON.stringify(e.payload)}</span>
          </div>
        ))}
        {events.length === 0 && <p className="text-zinc-500">Waiting for events…</p>}
      </div>
    </div>
  );
}
