"use client";
import { useEffect, useState } from "react";
import { API } from "@/lib/api";

interface Approval {
  id: string;
  tool_name: string;
  args: Record<string, unknown>;
  state: string;
  created_at: string;
}

export default function ApprovalsPage() {
  const [items, setItems] = useState<Approval[]>([]);
  const load = () =>
    fetch(`${API}/approvals`).then((r) => r.json()).then(setItems).catch(() => {});

  useEffect(() => {
    load();
    const t = setInterval(load, 2500);
    return () => clearInterval(t);
  }, []);

  const decide = async (id: string, approved: boolean) => {
    await fetch(`${API}/approvals/${id}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ approved }),
    });
    load();
  };

  return (
    <div>
      <h1 className="mb-4 text-xl font-semibold">Approvals</h1>
      <p className="mb-4 text-sm text-zinc-400">
        Destructive actions and outbound emails wait here. Nothing executes without you.
      </p>
      <div className="space-y-3">
        {items.map((a) => (
          <div key={a.id} className="rounded-lg border border-zinc-800 bg-zinc-900 p-4">
            <div className="mb-1 flex items-center gap-2">
              <span className="font-mono text-sm text-amber-400">{a.tool_name}</span>
              <span className={`rounded px-1.5 text-xs ${
                a.state === "pending" ? "bg-amber-900 text-amber-300"
                : a.state === "approved" ? "bg-emerald-900 text-emerald-300"
                : "bg-red-900 text-red-300"}`}>{a.state}</span>
            </div>
            <pre className="mb-3 max-h-32 overflow-auto text-xs text-zinc-400">
              {JSON.stringify(a.args, null, 2)}
            </pre>
            {a.state === "pending" && (
              <div className="flex gap-2">
                <button onClick={() => decide(a.id, true)}
                  className="rounded bg-emerald-700 px-4 py-1.5 text-sm hover:bg-emerald-600">Approve</button>
                <button onClick={() => decide(a.id, false)}
                  className="rounded bg-red-800 px-4 py-1.5 text-sm hover:bg-red-700">Deny</button>
              </div>
            )}
          </div>
        ))}
        {items.length === 0 && <p className="text-sm text-zinc-500">No pending approvals.</p>}
      </div>
    </div>
  );
}
