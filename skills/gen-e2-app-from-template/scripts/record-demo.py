#!/usr/bin/env python3
"""
Sprint demo recorder — drives the running app with Playwright, overlays
captions and title cards, and writes docs/demo/sprint-1-demo.mp4.

Prereqs: `npm run dev` running (web on :5173, API on :3001), Python Playwright
(`pip install playwright && playwright install chromium`) and ffmpeg on PATH.
Doubles as the E2E walkthrough for the four stories' happy paths.
"""
import asyncio
import pathlib
import shutil
import subprocess
import sys

from playwright.async_api import async_playwright

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "docs" / "demo"
BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5173/"
W, H = 1280, 800

OVERLAY_JS = r"""
(() => {
  if (document.getElementById('demo-caption')) return;
  const style = document.createElement('style');
  style.textContent = `
    #demo-caption { position: fixed; left: 50%; bottom: 28px; transform: translateX(-50%);
      max-width: 860px; padding: 14px 26px; border-radius: 999px; background: rgba(31,26,23,0.92);
      color: #fff; font: 600 19px/1.3 Inter, system-ui, sans-serif; z-index: 99999; opacity: 0;
      transition: opacity 250ms; text-align: center; box-shadow: 0 16px 40px rgba(0,0,0,.25); pointer-events: none; }
    #demo-caption.show { opacity: 1; }
    #demo-caption b { color: #F4B942; font-weight: 700; margin-right: 10px; }
    #demo-card { position: fixed; inset: 0; z-index: 100000; display: flex; flex-direction: column; align-items: center;
      justify-content: center; gap: 18px; background: #FFF8EE; color: #1F1A17; opacity: 0; transition: opacity 350ms;
      pointer-events: none; font-family: Inter, system-ui, sans-serif; text-align: center; padding: 40px; }
    #demo-card.show { opacity: 1; }
    #demo-card .kicker { color: #D7263D; font-weight: 700; letter-spacing: .14em; text-transform: uppercase; font-size: 15px; }
    #demo-card h1 { font: 700 58px/1.05 Fraunces, Georgia, serif; margin: 0; letter-spacing: -0.01em; }
    #demo-card p { font-size: 22px; color: #6B625B; margin: 0; max-width: 760px; }
    #demo-card ul { list-style: none; padding: 0; margin: 10px 0 0; display: grid; gap: 10px; font-size: 20px; text-align: left; }
    #demo-card li::before { content: '✓'; color: #1F7A6D; font-weight: 700; margin-right: 12px; }
    #demo-cursor { position: fixed; width: 22px; height: 22px; border-radius: 50%; background: rgba(215,38,61,.85);
      border: 2px solid #fff; box-shadow: 0 2px 8px rgba(0,0,0,.35); transform: translate(-50%,-50%);
      pointer-events: none; z-index: 99998; transition: transform 80ms; left: -100px; top: -100px; }
    #demo-cursor.click { transform: translate(-50%,-50%) scale(0.6); }
  `;
  document.head.appendChild(style);
  const cap = document.createElement('div'); cap.id = 'demo-caption'; document.body.appendChild(cap);
  const card = document.createElement('div'); card.id = 'demo-card'; document.body.appendChild(card);
  const cur = document.createElement('div'); cur.id = 'demo-cursor'; document.body.appendChild(cur);
  window.addEventListener('mousemove', e => { cur.style.left = e.clientX + 'px'; cur.style.top = e.clientY + 'px'; }, true);
  window.addEventListener('mousedown', () => cur.classList.add('click'), true);
  window.addEventListener('mouseup', () => setTimeout(() => cur.classList.remove('click'), 120), true);
  window.__demo = {
    caption(html) { cap.innerHTML = html; cap.classList.toggle('show', Boolean(html)); },
    card(html) { card.innerHTML = html; card.classList.toggle('show', Boolean(html)); },
  };
})();
"""


class Demo:
    def __init__(self, page):
        self.page = page

    async def install(self):
        await self.page.evaluate(OVERLAY_JS)

    async def caption(self, story, text, hold=0):
        await self.page.evaluate("([s,t]) => window.__demo.caption(s ? `<b>${s}</b>${t}` : t)", [story, text])
        if hold:
            await self.page.wait_for_timeout(hold)

    async def card(self, html, hold):
        await self.page.evaluate("h => window.__demo.card(h)", html)
        await self.page.wait_for_timeout(hold)
        await self.page.evaluate("() => window.__demo.card('')")
        await self.page.wait_for_timeout(400)

    async def move_to(self, selector):
        box = await self.page.locator(selector).first.bounding_box()
        if not box:
            raise RuntimeError(f"no element for {selector}")
        await self.page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2, steps=18)
        await self.page.wait_for_timeout(250)

    async def click(self, selector, settle=600):
        await self.move_to(selector)
        await self.page.locator(selector).first.click()
        await self.page.wait_for_timeout(settle)

    async def type_into(self, selector, text):
        await self.click(selector, settle=150)
        await self.page.locator(selector).first.fill("")
        await self.page.locator(selector).first.press_sequentially(text, delay=45)
        await self.page.wait_for_timeout(250)

    async def select(self, selector, value):
        await self.move_to(selector)
        await self.page.locator(selector).first.select_option(value)
        await self.page.wait_for_timeout(500)


async def run():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    video_dir = OUT_DIR / "_raw"
    shutil.rmtree(video_dir, ignore_errors=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(
            viewport={"width": W, "height": H},
            record_video_dir=str(video_dir),
            record_video_size={"width": W, "height": H},
            device_scale_factor=1,
        )
        page = await context.new_page()
        await page.goto(BASE_URL)
        await page.wait_for_selector("[data-testid=spin-button]")
        await page.wait_for_timeout(800)
        d = Demo(page)
        await d.install()
        await page.mouse.move(W / 2, H / 2)

        # ---- Title card
        await d.card(
            """<div class="kicker">Sprint 1 · Demo</div>
               <h1>Makan Mate</h1>
               <p>The team hawker-lunch picker — built on the Gen-e2 project template.<br>
               React + Express + a local JSON file as the database.</p>""",
            4200,
        )

        # ---- Story 002: spin
        await d.caption("Story 002", "Lunch Roulette — one click, the server picks fairly from every stall", 1800)
        await d.click("[data-testid=spin-button]", settle=4300)
        await d.caption("Story 002", "The wheel lands on the server's pick — must-try dish, price band and rating up front", 3200)

        # ---- Story 002: filters
        await d.caption("Story 002", "Filters narrow the pool: Indian, under S$5…", 800)
        await d.select("select >> nth=0", "indian")
        await d.select("select >> nth=1", "1")
        await page.wait_for_timeout(600)
        await d.click("[data-testid=spin-button]", settle=4300)
        await d.caption("Story 002", "…and the spin only considers matching stalls", 2600)

        # ---- Story 003: rate the winner
        await d.caption("Story 003", "Ate there? Log the visit straight from the winner card", 1200)
        await d.click("text=I ate here — rate it", settle=900)
        await d.click("label:has(input[value='5'])", settle=500)
        await d.type_into("input[placeholder='Priya']", "Priya")
        await d.type_into("input[placeholder^='Shiok']", "Thosai crispy, kopi strong. Shiok!")
        await d.caption("Story 003", "1–5 stars, your name, an optional note — validated field by field", 1400)
        await d.click("button:has-text('Save rating')", settle=2200)

        # ---- Story 001: stalls
        await d.caption("Story 001", "The stall directory — the team's shared food memory", 1000)
        await d.click("button.tab:has-text('Stalls')", settle=1200)
        await d.click("text=+ Add stall", settle=900)
        await d.caption("Story 001", "Submit an empty form: per-field errors mirror the API's validation details", 800)
        await d.click("button:has-text('Add stall') >> nth=0", settle=1800)
        await d.caption("Story 001", "Fill it in — a must-try dish is mandatory, that's the whole point", 600)
        await d.type_into("input[placeholder^='Tian Tian']", "Lau Pa Sat Satay Street")
        await d.type_into("input[placeholder='Maxwell Food Centre']", "Lau Pa Sat")
        await d.select("select >> nth=0", "malay")
        await d.select("select >> nth=1", "2")
        await d.type_into("input[placeholder^='Chicken rice']", "Mixed satay, 20 sticks for sharing")
        await d.click("button:has-text('Add stall') >> nth=0", settle=1800)
        await d.caption("Story 001", "New stall lands at the top of the grid and in tonight's roulette pool", 2600)

        # ---- Story 001: delete with confirmation
        await d.caption("Story 001", "Removing a stall goes through our own confirmation dialog — never window.confirm", 800)
        await d.click("button[aria-label='Remove Lau Pa Sat Satay Street']", settle=1400)
        await page.wait_for_timeout(1200)
        await d.click("button:has-text('Remove stall')", settle=1800)

        # ---- Story 004: leaderboard
        await d.caption("Story 004", "Leaderboard — ranked by Makan Score, a Bayesian average", 1000)
        await d.click("button.tab:has-text('Leaderboard')", settle=1500)
        await d.caption("Story 004", "One lucky 5★ visit can't outrank a steady 4.6★ stall · team stats and top diner up top", 3600)
        await page.mouse.wheel(0, 420)
        await page.wait_for_timeout(2200)
        await page.mouse.wheel(0, -420)
        await page.wait_for_timeout(600)

        # ---- Visits feed
        await d.caption("Story 003", "Every rating feeds the visits timeline", 600)
        await d.click("button.tab:has-text('Visits')", settle=2600)

        # ---- Under the hood card
        await d.caption("", "")
        await d.card(
            """<div class="kicker">Under the hood · Gen-e2</div>
               <h1>Contract-first, docs-with-code</h1>
               <ul>
                 <li>OpenAPI contract written before any endpoint · 4 ADRs (stack, JSON store, no-auth, OpenAPI)</li>
                 <li>1 epic · 4 stories with Given/When/Then AC · one implementation plan per story</li>
                 <li>52 automated tests — one per acceptance scenario, run against a temp db.json</li>
                 <li>Database = <code>services/api/data/db.json</code>, atomic writes, zero setup</li>
                 <li>Design tokens in DESIGN.md → tokens.css · keyboard + screen-reader friendly</li>
               </ul>""",
            6500,
        )
        await d.card(
            """<div class="kicker">Sprint 1 · Done</div>
               <h1>npm install && npm run dev</h1>
               <p>Next sprint candidates: export/import db.json · weekly digest · diner streaks</p>""",
            3800,
        )

        await context.close()
        await browser.close()

    raw = next(video_dir.glob("*.webm"))
    mp4 = OUT_DIR / "sprint-1-demo.mp4"
    subprocess.run(
        [
            "ffmpeg", "-y", "-i", str(raw),
            "-vf", "fps=30,format=yuv420p",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-movflags", "+faststart",
            str(mp4),
        ],
        check=True,
        capture_output=True,
    )
    shutil.rmtree(video_dir, ignore_errors=True)
    print(f"wrote {mp4}")


if __name__ == "__main__":
    asyncio.run(run())
