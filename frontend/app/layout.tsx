import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "ATLAS",
  description: "Autonomous Task & Lab Assistant System",
};

const nav = [
  { href: "/", label: "Chat" },
  { href: "/activity", label: "Activity" },
  { href: "/ledger", label: "Ledger" },
  { href: "/skills", label: "Skills" },
  { href: "/approvals", label: "Approvals" },
];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="flex min-h-screen">
        <aside className="w-52 shrink-0 border-r border-zinc-800 p-4">
          <div className="mb-6 flex items-center gap-2 text-lg font-bold tracking-wide">
            <svg width="22" height="22" viewBox="0 0 64 64" fill="none" aria-hidden="true">
              <path
                d="M13 52 L32 12 L51 52"
                stroke="currentColor"
                strokeWidth="7"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <circle cx="32" cy="41" r="5.5" fill="#10b981" />
            </svg>
            ATLAS<span className="text-emerald-400">.</span>
          </div>
          <nav className="space-y-1">
            {nav.map((n) => (
              <Link
                key={n.href}
                href={n.href}
                className="block rounded px-3 py-2 text-sm text-zinc-300 hover:bg-zinc-800"
              >
                {n.label}
              </Link>
            ))}
          </nav>
        </aside>
        <main className="flex-1 p-6">{children}</main>
      </body>
    </html>
  );
}
