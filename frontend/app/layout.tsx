import type { Metadata } from "next";
import "./globals.css";

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
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
