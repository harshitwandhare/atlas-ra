import type { Metadata } from "next";
import { IBM_Plex_Mono, IBM_Plex_Sans, Space_Grotesk } from "next/font/google";

import "./globals.css";

// Plex is the working typeface — an engineering face for an instrument panel.
// Space Grotesk carries the display voice. Both self-host at build time, so
// nothing is fetched from a third party at runtime.
const sans = IBM_Plex_Sans({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-sans",
  display: "swap",
});

const display = Space_Grotesk({
  subsets: ["latin"],
  weight: ["500", "600", "700"],
  variable: "--font-display",
  display: "swap",
});

const mono = IBM_Plex_Mono({
  subsets: ["latin"],
  weight: ["400", "500"],
  variable: "--font-mono",
  display: "swap",
});

export const metadata: Metadata = {
  metadataBase: new URL("https://atlas-ra.vercel.app"),
  title: {
    default: "ATLAS — Autonomous Task & Lab Assistant System",
    template: "%s · ATLAS",
  },
  description:
    "A multi-team, multi-provider agent system: an orchestrator decomposes goals, routes them to specialist teams, verifies results with a Critic before marking anything done, and compounds what it learns into versioned procedural memory.",
  openGraph: {
    title: "ATLAS — Autonomous Task & Lab Assistant System",
    description:
      "Multi-team agent orchestration with three-tier memory, approval-gated execution, and verification before completion.",
    type: "website",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${sans.variable} ${display.variable} ${mono.variable}`}>
      <body className="font-sans">{children}</body>
    </html>
  );
}
