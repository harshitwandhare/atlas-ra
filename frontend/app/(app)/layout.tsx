import Link from "next/link";

import { Logo } from "@/components/Logo";

const nav = [
  { href: "/console", label: "Console" },
  { href: "/activity", label: "Activity" },
  { href: "/ledger", label: "Ledger" },
  { href: "/skills", label: "Skills" },
  { href: "/approvals", label: "Approvals" },
];

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen">
      <aside className="flex w-52 shrink-0 flex-col border-r border-line p-4">
        <Link href="/" className="mb-6 flex items-center gap-2 text-lg font-bold tracking-wide">
          <Logo />
          ATLAS<span className="text-brand-400">.</span>
        </Link>
        <nav className="space-y-1">
          {nav.map((n) => (
            <Link
              key={n.href}
              href={n.href}
              className="block rounded px-3 py-2 text-sm text-muted transition-colors hover:bg-raised hover:text-ink"
            >
              {n.label}
            </Link>
          ))}
        </nav>
        <Link
          href="/"
          className="mt-auto rounded px-3 py-2 text-xs text-faint transition-colors hover:text-muted"
        >
          ← Back to overview
        </Link>
      </aside>
      <main className="flex-1 p-6">{children}</main>
    </div>
  );
}
