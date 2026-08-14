"use client";
import { useEffect, useState } from "react";
import { listTasks, Task } from "@/lib/api";

const stateColor: Record<string, string> = {
  done: "text-ok-400",
  running: "text-sky-400",
  failed: "text-red-400",
  escalated: "text-amber-400",
};

const STATES = ["all", "pending", "assigned", "running", "review", "done", "failed", "blocked", "escalated"];

export default function LedgerPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [filter, setFilter] = useState("all");

  useEffect(() => {
    const load = () =>
      listTasks(filter === "all" ? undefined : filter)
        .then(setTasks)
        .catch(() => {});
    load();
    const t = setInterval(load, 3000);
    return () => clearInterval(t);
  }, [filter]);

  return (
    <div>
      <div className="mb-4 flex items-center justify-between">
        <h1 className="text-xl font-semibold">Task ledger</h1>
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="rounded border border-line bg-surface px-2 py-1 text-sm text-muted"
        >
          {STATES.map((s) => (
            <option key={s} value={s}>
              {s === "all" ? "All states" : s}
            </option>
          ))}
        </select>
      </div>
      <table className="w-full text-left text-sm">
        <thead className="text-faint">
          <tr><th className="py-2">ID</th><th>Goal</th><th>Team</th><th>State</th><th>Updated</th></tr>
        </thead>
        <tbody>
          {tasks.map((t) => (
            <tr key={t.id} className="border-t border-line">
              <td className="py-2 font-mono text-xs">{t.id}</td>
              <td className="max-w-md truncate">{t.goal}</td>
              <td>{t.team}</td>
              <td className={stateColor[t.state] ?? "text-muted"}>{t.state}</td>
              <td className="text-faint">{new Date(t.updated_at).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
