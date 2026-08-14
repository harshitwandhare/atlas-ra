"use client";

import { useEffect, useState } from "react";

import { subscribeDemo } from "@/lib/api";

const REPO = "https://github.com/harshitwandhare/atlas-ra";

/**
 * Shown only when the dashboard could not reach a backend. Everything on
 * screen is sample data in that case, and saying so plainly is better than
 * letting someone read fictional runs as real ones.
 */
export function DemoBanner() {
  const [demo, setDemo] = useState(false);
  const [dismissed, setDismissed] = useState(false);

  useEffect(() => subscribeDemo(setDemo), []);

  if (!demo || dismissed) return null;

  return (
    <div className="mb-6 rounded-xl border border-amber-500/25 bg-amber-500/[0.07] p-4">
      <div className="flex items-start gap-3">
        <span aria-hidden="true" className="mt-0.5 text-amber-400">
          ●
        </span>
        <div className="min-w-0 flex-1">
          <p className="text-sm font-medium text-ink">
            Hosted preview — showing sample data
          </p>
          <p className="mt-1 text-sm leading-relaxed text-muted">
            ATLAS runs on your own machine, so this deployment has no backend to talk to. The tasks,
            skills, and approvals below are realistic examples, not live runs, and controls here
            will not change anything. This page cannot reach a backend on your machine either —
            browsers block an https site from calling{" "}
            <code className="rounded bg-raised px-1.5 py-0.5 font-mono text-xs text-brand-300">
              localhost
            </code>
            . To see your own runs, clone the repo and open the dashboard locally.
          </p>
          <a
            href={`${REPO}#quickstart`}
            target="_blank"
            rel="noopener noreferrer"
            className="mt-2 inline-block text-sm text-amber-300 underline-offset-4 hover:underline"
          >
            Set it up locally ↗
          </a>
        </div>
        <button
          onClick={() => setDismissed(true)}
          aria-label="Dismiss preview notice"
          className="shrink-0 rounded px-2 py-1 text-sm text-faint transition-colors hover:text-muted"
        >
          ✕
        </button>
      </div>
    </div>
  );
}
