"use client";
import { useEffect, useState } from "react";
import { listSkills, Skill } from "@/lib/api";

export default function SkillsPage() {
  const [skills, setSkills] = useState<Skill[]>([]);
  useEffect(() => {
    listSkills().then(setSkills).catch(() => {});
  }, []);

  return (
    <div>
      <h1 className="mb-4 text-xl font-semibold">Procedural memory (skills)</h1>
      <div className="grid gap-4 md:grid-cols-2">
        {skills.map((s) => (
          <div key={s.name} className="rounded-lg border border-zinc-800 bg-zinc-900 p-4">
            <div className="mb-1 flex items-center gap-2">
              <span className="font-medium">{s.name}</span>
              <span className="rounded bg-zinc-800 px-1.5 text-xs text-emerald-400">v{s.version}</span>
            </div>
            <div className="mb-2 text-xs text-zinc-500">triggers: {s.triggers.join(", ")}</div>
            <pre className="max-h-48 overflow-auto whitespace-pre-wrap text-xs text-zinc-300">{s.body}</pre>
          </div>
        ))}
      </div>
    </div>
  );
}
