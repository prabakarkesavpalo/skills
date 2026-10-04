---
name: "notes-to-infographic"
description: "Turn any notes, transcript, report or summary (meeting, podcast, research, lecture, project, travel, etc.) into a polished one-page portrait infographic PNG."
---

# Notes to one-page infographic

Use when the user wants notes, a transcript, a report or any long text as a single visual page they can screenshot, print or share. Works for any category. The output is one portrait PNG (about 8.5:11), rendered from HTML so every number and word is exact.

## Step 0: Read everything first
Read the full source (attached files included). If a summary already exists in the conversation, build from the summary but check it against the original. Never ask the user to restructure notes.

## Step 1: Detect the category and pick a card plan
| Category | Header kicker | Typical cards |
|---|---|---|
| Meeting | MEETING NOTES | Context, decisions, action items (owner, date), risks, open questions, next steps |
| Podcast / interview | PODCAST NOTES | One card per theme, key numbers, speaker views, closing theme |
| Research / report | RESEARCH SUMMARY | Question, method, key findings, data, limits, implications |
| Lecture / course | STUDY NOTES | Concepts, definitions, examples, formulas, takeaways |
| Project / status | PROJECT UPDATE | Goal, progress, milestones, blockers, owners, timeline |
| Strategy / business | BRIEFING | Situation, options, trade-offs, recommendation as stated, risks |
| Personal / travel / event | PLAN | Schedule, places, costs, checklist, logistics |
| Other | NOTES | Group by the source's own themes |

Choose 8 to 16 cards. Merge repeated ideas, drop low-value detail, but do not drop a theme. Order cards the way the source flows, and put the biggest idea first.

## Step 2: Extract the information architecture
List: topic, person or source, date, 8 to 16 themes, every number, memorable quotes (only if actually in the source), risks and caveats, action items, closing theme, required disclaimer. Keep a list of anything unclear in the source (garbled transcript, ambiguous names) and phrase it cautiously or leave it out.

## Step 3: Compress
- 3 to 6 bullets per card, each at most about 12 words (fits in 2 lines).
- Bold the key number or phrase in a bullet. Use one callout line per card at most for the strongest statement.
- Preserve numbers exactly: ~15% stays ~15%, 3+ years stays 3+ years, ₹34,000 crore stays as written. Never invent numbers, quotes, owners, dates or conclusions.
- Attribute opinions: "His view", "The host noted", "The team decided". Do not turn a speaker's opinion into fact.
- Use a chart only when the source gives real values (bars, simple trend). Otherwise use an icon or a tile row. Never fake precision.

## Step 4: Colour by meaning, not at random
Blue = data, markets, facts. Green = growth, positive, done. Orange = options, sectors, categories. Purple = technology, global, ideas. Red = risks, warnings, blockers. Yellow = key callout or action item. Navy header and a dark closing card. Same category, same colour on every card.

## Step 5: Build the HTML
Write /tmp/infographic.html (use the scratchpad if one is listed). Page width 1900px, font Inter with DejaVu Sans fallback (supports the rupee sign), light background #f4f6fb.

Structure:
1. Header (about 15 to 20% of height): kicker, large title, person and role, subtitle with date, up to 3 stat chips with the most important numbers.
2. Body: rows in a 3-column CSS grid (gap 22px). Last row may be 7fr/5fr to hold a wide card plus the closing card. Each card: rounded 20px, 8px top border in its colour, number badge, heading, small line icon at top right, bullets.
3. Closing card (dark navy, yellow top border): the closing quote or theme in yellow, 3 to 5 takeaways.
4. Footer: disclaimer on the left, attribution note on the right.

CSS pattern to reuse: `.card{background:#fff;border-radius:20px;padding:22px 26px;border-top:8px solid var(--c)}` with colour classes that set `--c` (accent), `--t` (tint) and `--d` (dark text), e.g. `.blue{--c:#2f6fe4;--t:#e4eeff;--d:#1a4aa8}`. Bullets are `li` with a coloured dot via `:before`, 20.5px text. Callout is `.call{background:var(--t);color:var(--d);font-weight:800;border-radius:12px;padding:10px 14px}`. Tiles and mini bars use the same tokens.

Icons: hand-written inline SVG, viewBox 0 0 48 48, stroke currentColor, width 2.2, no fill, max about 6 path segments each. Pick one per card (up-trend, globe, gauge, calendar, checklist, people, shield, lightbulb, flag, clock, document, map pin, wallet, gear, flask).

No overlapping cards, no text touching card edges, no emoji, no photos, no decoration that carries no meaning.

## Step 6: Render
```python
from playwright.sync_api import sync_playwright
import os
os.makedirs("/tmp/outputs", exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1900, "height": 2200}, device_scale_factor=2)
    pg.goto("file:///tmp/infographic.html")
    pg.wait_for_timeout(500)
    print(pg.evaluate("document.querySelector('.page').getBoundingClientRect().height"))
    pg.locator(".page").screenshot(path="/tmp/outputs/<Topic>_Infographic.png")
    b.close()
```
Target height about 2400 to 2500 for width 1900 (8.5:11 is about 1.29). If much taller, widen the page or cut bullets. If playwright or chromium is missing, install it (pip install playwright, then playwright install chromium) or use headless Chrome.

## Step 7: Check before sending
Open the PNG with Read and verify:
- Topic and person are obvious; every major theme has a card; nothing important omitted.
- Every number matches the source; approximate stays approximate; nothing invented.
- No spelling errors, duplicated words, truncated bullets or overlaps; text readable at phone size.
- Colours consistent by meaning; icons match topics; cards aligned.
- Opinions attributed; no buy/sell language or forecasts added.
Fix and re-render if anything fails. Large empty gaps in a card mean the row should be rebalanced.

## Disclaimers by category
- Financial or investment talk: footer must read "Summary of a discussion — not investment advice." Keep views as the speaker's, add no recommendations or rankings.
- Medical or legal content: "Summary for information only — not medical (or legal) advice."
- Other categories: a short source line ("Summary of notes dated <date>") is enough.
If the source has its own stronger disclaimer, keep it.

## Delivery
Send the PNG with SendUserFile (display render) and give a two-line summary: what it contains and any parts of the source that were unclear. Offer a PDF copy (embed the PNG with reportlab or print the HTML to PDF) and a more detailed text version only if asked. On a phone, mention that a screenshot saves it to Photos.

## Do not
- Do not paste long paragraphs onto the image.
- Do not use image-generation for text-heavy pages; render HTML so text is exact.
- Do not add facts from outside the source.