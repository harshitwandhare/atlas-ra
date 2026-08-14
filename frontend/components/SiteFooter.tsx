import Link from "next/link";

import { Logo } from "@/components/Logo";

const REPO = "https://github.com/harshitwandhare/atlas-ra";

const columns: { heading: string; items: { label: string; href: string; external?: boolean }[] }[] = [
  {
    heading: "Dashboard",
    items: [
      { label: "Console", href: "/console" },
      { label: "Live activity", href: "/activity" },
      { label: "Task ledger", href: "/ledger" },
      { label: "Skills", href: "/skills" },
      { label: "Approvals", href: "/approvals" },
    ],
  },
  {
    heading: "Documentation",
    items: [
      { label: "Architecture", href: `${REPO}/blob/main/docs/ARCHITECTURE.md`, external: true },
      { label: "Data models", href: `${REPO}/blob/main/docs/DATA_MODELS.md`, external: true },
      { label: "Operations", href: `${REPO}/blob/main/docs/OPERATIONS.md`, external: true },
      { label: "ADRs", href: `${REPO}/tree/main/docs/adr`, external: true },
      { label: "Requirements audit", href: `${REPO}/blob/main/docs/REQUIREMENTS_AUDIT.md`, external: true },
    ],
  },
  {
    heading: "Project",
    items: [
      { label: "Source on GitHub", href: REPO, external: true },
      { label: "Security policy", href: `${REPO}/blob/main/SECURITY.md`, external: true },
      { label: "Contributing", href: `${REPO}/blob/main/CONTRIBUTING.md`, external: true },
      { label: "Releases", href: `${REPO}/releases`, external: true },
    ],
  },
];

export function SiteFooter() {
  return (
    <footer className="border-t border-line bg-surface">
      <div className="mx-auto max-w-6xl px-5 py-14 sm:px-6">
        <div className="grid gap-10 lg:grid-cols-[1.4fr_1fr_1fr_1fr]">
          <div>
            <div className="flex items-center gap-2 text-lg font-bold tracking-wide">
              <Logo />
              ATLAS<span className="text-brand-400">.</span>
            </div>
            <p className="mt-3 max-w-xs text-sm leading-relaxed text-muted">
              Autonomous Task &amp; Lab Assistant System — a multi-team, multi-provider agent
              runtime with verification, approval gates, and memory that compounds.
            </p>
          </div>

          {columns.map((col) => (
            <div key={col.heading}>
              <h3 className="text-xs font-medium uppercase tracking-widest text-faint">{col.heading}</h3>
              <ul className="mt-4 space-y-2.5">
                {col.items.map((item) => (
                  <li key={item.label}>
                    {item.external ? (
                      <a
                        href={item.href}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm text-muted transition-colors hover:text-ink"
                      >
                        {item.label} ↗
                      </a>
                    ) : (
                      <Link href={item.href} className="text-sm text-muted transition-colors hover:text-ink">
                        {item.label}
                      </Link>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-12 flex flex-col gap-2 border-t border-line pt-6 text-xs text-faint sm:flex-row sm:items-center sm:justify-between">
          <p>MIT licensed © Harshit Wandhare</p>
          <p className="font-mono">Python 3.10+ · FastAPI · Next.js 14 · SQLite · OpenTelemetry</p>
        </div>
      </div>
    </footer>
  );
}
