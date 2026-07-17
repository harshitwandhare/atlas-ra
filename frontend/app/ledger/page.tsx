"use client";
import { useEffect, useState } from "react";
import { listTasks, Task } from "@/lib/api";

const stateColor: Record<string, string> = {
  done: "text-emerald-400",
  running: "text-sky-400",
  failed: "text-red-400",
  escalated: "text-amber-400",
};

export default function LedgerPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  useEffect(() => {
    const load = () => listTasks().then(setTasks).catch(() => {});
    load();
    const t = setInterval(load, 3000);
    return () => clearInterval(t);
  }, []);

  return (
    <div>
      <h1 className="mb-4 text-xl font-semibold">Task ledger</h1>
      <table className="w-full text-left text-sm">
        <thead className="text-zinc-500">
          <tr><th className="py-2">ID</th><th>Goal</th><th>Team</th><th>State</th><th>Updated</th></tr>
        </thead>
        <tbody>
          {tasks.map((t) => (
            <tr key={t.id} className="border-t border-zinc-800">
              <td className="py-2 font-mono text-xs">{t.id}</td>
              <td className="max-w-md truncate">{t.goal}</td>
              <td>{t.team}</td>
              <td className={stateColor[t.state] ?? "text-zinc-300"}>{t.state}</td>
              <td className="text-zinc-500">{new Date(t.updated_at).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
