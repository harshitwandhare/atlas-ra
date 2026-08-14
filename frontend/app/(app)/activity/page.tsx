"use client";
import { useEvents } from "@/lib/useEvents";

export default function ActivityPage() {
  const events = useEvents();
  return (
    <div>
      <h1 className="mb-4 text-xl font-semibold">Live activity</h1>
      <div className="space-y-1 font-mono text-xs">
        {events.map((e, i) => (
          <div key={i} className="flex gap-3 rounded border border-line bg-surface px-3 py-2">
            <span className="text-faint">{new Date(e.ts).toLocaleTimeString()}</span>
            <span className="text-brand-400">{e.agent}</span>
            <span className="text-sky-400">{e.type}</span>
            <span className="truncate text-muted">{JSON.stringify(e.payload)}</span>
          </div>
        ))}
        {events.length === 0 && <p className="text-faint">Waiting for events…</p>}
      </div>
    </div>
  );
}
