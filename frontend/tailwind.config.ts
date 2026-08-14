import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: "var(--bg)",
        surface: "var(--surface)",
        raised: "var(--raised)",
        ink: "var(--ink)",
        muted: "var(--muted)",
        faint: "var(--faint)",
        line: "var(--line)",
        brand: {
          DEFAULT: "var(--brand)",
          300: "#b3a9ff",
          400: "#9587ff",
          500: "#7c6cff",
          600: "#6350e6",
        },
        // Semantic success — verified, approved, done. Never used as identity.
        ok: {
          DEFAULT: "var(--ok)",
          300: "#6ee7b7",
          400: "#34d399",
          500: "#10b981",
        },
      },
      fontFamily: {
        sans: ["var(--font-sans)", "ui-sans-serif", "system-ui", "Segoe UI", "sans-serif"],
        display: ["var(--font-display)", "var(--font-sans)", "ui-sans-serif", "sans-serif"],
        mono: ["var(--font-mono)", "ui-monospace", "SFMono-Regular", "Consolas", "monospace"],
      },
      boxShadow: {
        card: "0 1px 2px rgba(0,0,0,0.4), 0 12px 32px -16px rgba(0,0,0,0.7)",
        glow: "0 0 0 1px rgba(124,108,255,0.22), 0 8px 40px -12px rgba(124,108,255,0.4)",
      },
      animation: {
        marquee: "marquee 32s linear infinite",
        pulseDot: "pulseDot 2.4s ease-in-out infinite",
      },
      keyframes: {
        marquee: {
          from: { transform: "translateX(0)" },
          to: { transform: "translateX(-50%)" },
        },
        pulseDot: {
          "0%, 100%": { opacity: "0.35" },
          "50%": { opacity: "1" },
        },
      },
    },
  },
  plugins: [],
};

export default config;
