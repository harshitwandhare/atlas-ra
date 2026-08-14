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
          <div key={s.name} className="rounded-lg border border-line bg-surface p-4">
            <div className="mb-1 flex items-center gap-2">
              <span className="font-medium">{s.name}</span>
              <span className="rounded bg-raised px-1.5 text-xs text-brand-400">v{s.version}</span>
            </div>
            <div className="mb-2 text-xs text-faint">triggers: {s.triggers.join(", ")}</div>
            <pre className="max-h-48 overflow-auto whitespace-pre-wrap text-xs text-muted">{s.body}</pre>
          </div>
        ))}
      </div>
    </div>
  );
}
