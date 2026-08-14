"""Capture the README screenshots.

Runs against a URL (the deployment by default, or a local dev server) and writes
PNGs into docs/screenshots/. Committing this next to the images keeps them
reproducible instead of one-off artifacts that drift as the UI changes.

    uv run python scripts/capture_screens.py
    uv run python scripts/capture_screens.py --base-url http://localhost:3000

Requires Playwright's chromium:

    uv run python -m playwright install chromium
"""

from __future__ import annotations

import argparse
from pathlib import Path

from playwright.sync_api import sync_playwright

DEFAULT_BASE_URL = "https://atlas-ra.vercel.app"
OUT_DIR = Path(__file__).resolve().parent.parent / "docs" / "screenshots"

# Viewport is 2x-scaled at capture time, so these are CSS pixels. Dashboard
# screens are shorter than the landing hero because they carry less content —
# a taller frame is mostly empty background.
HERO_VIEWPORT = {"width": 1440, "height": 900}
APP_VIEWPORT = {"width": 1440, "height": 760}

# Sections of the landing page, captured by anchor id rather than as one very
# tall full-page stitch: the marquee animates, so a stitched capture tears, and
# a 12000px image renders unreadably small in a README.
LANDING_SHOTS: list[tuple[str, str | None]] = [
    ("landing.png", None),  # hero, viewport-sized
    ("lifecycle.png", "#how"),
    ("architecture.png", "#architecture"),
]

APP_SHOTS: list[tuple[str, str]] = [
    ("/console", "console.png"),
    ("/ledger", "ledger.png"),
    ("/activity", "activity.png"),
    ("/skills", "skills.png"),
    ("/approvals", "approvals.png"),
]

# Freeze animation so captures are deterministic and nothing is caught
# mid-transition. Reveal-on-scroll sections are forced visible.
FREEZE_CSS = """
  *, *::before, *::after {
    animation-play-state: paused !important;
    animation-delay: -1s !important;
    transition: none !important;
  }
  .reveal { opacity: 1 !important; transform: none !important; }
"""


def capture(base_url: str) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    base = base_url.rstrip("/")

    with sync_playwright() as p:
        browser = p.chromium.launch()

        # Landing page — hero plus two named sections.
        page = browser.new_page(viewport=HERO_VIEWPORT, device_scale_factor=2)
        page.goto(f"{base}/", wait_until="networkidle")
        # Let the event-stream replay reach a populated state before freezing.
        page.wait_for_timeout(9000)
        page.add_style_tag(content=FREEZE_CSS)

        for name, anchor in LANDING_SHOTS:
            if anchor:
                page.evaluate(
                    "(sel) => document.querySelector(sel)"
                    "?.scrollIntoView({block: 'start', behavior: 'instant'})",
                    anchor,
                )
                page.wait_for_timeout(600)
            page.screenshot(path=str(OUT_DIR / name))
            print(f"{name:<18} /{anchor or ''}")
        page.close()

        # Dashboard screens.
        page = browser.new_page(viewport=APP_VIEWPORT, device_scale_factor=2)
        for route, name in APP_SHOTS:
            page.goto(f"{base}{route}", wait_until="networkidle")
            page.wait_for_timeout(2000)
            page.add_style_tag(content=FREEZE_CSS)
            page.screenshot(path=str(OUT_DIR / name))
            print(f"{name:<18} {route}")

        browser.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    args = parser.parse_args()
    capture(args.base_url)
    print(f"\nwrote {len(LANDING_SHOTS) + len(APP_SHOTS)} screenshots to {OUT_DIR}")


if __name__ == "__main__":
    main()
