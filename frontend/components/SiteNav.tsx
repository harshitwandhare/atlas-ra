"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { Logo } from "@/components/Logo";

const links = [
  { href: "#how", label: "How it works" },
  { href: "#architecture", label: "Architecture" },
  { href: "#capabilities", label: "Capabilities" },
  { href: "#engineering", label: "Engineering" },
];

export function SiteNav() {
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <header
      className={`sticky top-0 z-50 border-b transition-colors ${
        scrolled ? "border-line bg-bg/85 backdrop-blur-md" : "border-transparent bg-transparent"
      }`}
    >
      <div className="mx-auto flex max-w-6xl items-center justify-between px-5 py-4 sm:px-6">
        <Link href="/" className="flex items-center gap-2 text-lg font-bold tracking-wide">
          <Logo />
          ATLAS<span className="text-brand-400">.</span>
        </Link>

        <nav className="hidden items-center gap-7 md:flex">
          {links.map((l) => (
            <a key={l.href} href={l.href} className="text-sm text-muted transition-colors hover:text-ink">
              {l.label}
            </a>
          ))}
        </nav>

        <div className="flex items-center gap-3">
          <a
            href="https://github.com/harshitwandhare/atlas-ra"
            target="_blank"
            rel="noopener noreferrer"
            className="hidden text-sm text-muted transition-colors hover:text-ink sm:block"
          >
            GitHub ↗
          </a>
          <Link
            href="/console"
            className="rounded-lg bg-brand-500 px-4 py-2 text-sm font-medium text-black transition-colors hover:bg-brand-400"
          >
            Open dashboard
          </Link>
          <button
            onClick={() => setOpen((v) => !v)}
            aria-expanded={open}
            aria-label="Toggle navigation"
            className="rounded-lg border border-line px-2.5 py-2 text-sm md:hidden"
          >
            ≡
          </button>
        </div>
      </div>

      {open && (
        <nav className="border-t border-line bg-bg px-5 py-3 md:hidden">
          {links.map((l) => (
            <a
              key={l.href}
              href={l.href}
              onClick={() => setOpen(false)}
              className="block py-2 text-sm text-muted hover:text-ink"
            >
              {l.label}
            </a>
          ))}
        </nav>
      )}
    </header>
  );
}
