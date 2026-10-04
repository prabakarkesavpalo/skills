---
name: "daily-newspaper"
description: "Build the user's one-page morning newspaper (broadsheet HTML: trending tech, Jev/Hermes/Claude AI updates, Indian market sentiment from X, daily motivation). Use for morning paper, daily edition, /daily-newspaper, or the 8am scheduled task."
---

# Daily Newspaper

Produce a single-page morning newspaper the user reads over breakfast in Singapore. It is *one page*: skimmable in five minutes, every story sourced from today's web, laid out like a broadsheet front page. Freshness is the whole point — never fill a section from memory.

## Workflow

1. **Get the date/time** (current_time tool). The edition is dated in Asia/Singapore time. Use the date in every search so results are today's.
2. **Research all three sections** (run searches in parallel via subagents when the Agent tool exists; otherwise inline). Aim for 3–4 stories per section, each with a source link. Prefer primary outlets and the last 24–48 hours.
3. **Pick the motivation** — one short quote (pre-1929 or public-domain author, or paraphrase a modern one in your own words with attribution) plus one sentence on how it applies to the day. Never reproduce copyrighted lyrics or poems.
4. **Write the page** as a single self-contained `newspaper.html` (see Layout) and publish it with the Artifact tool. Title it `The Daily Edition — <Mon DD>`. Even if a Docs or Design artifact type is listed, use HTML: the broadsheet layout depends on it.
5. **Deliver**: after publishing, send a 4–6 line plain-text digest (one headline per section + the motivation line) with SendUserMessage so it reaches the phone even when the artifact card isn't opened. In a scheduled run, that message is the notification.

## Sections (fixed order, fixed names)

### 1. Tech Front — most trending topics
Rank by popularity/momentum (what's being covered most in the last day). Rotate across these beats and cover at least three of them:
- **Gadgets** — launches, reviews, hardware.
- **China innovation** — Chinese firms, chips, EVs, robotics, AI labs.
- **Agentic AI** — agents, tool use, enterprise rollouts, benchmarks.
- **Bots** — humanoid/consumer robots, chat/voice bots, automation.
Searches: `tech news today`, `China tech news today`, `agentic AI news`, `robotics news today`, `gadget launch this week`.

### 2. The AI Trio — Jev, Hermes & Claude
One short update for each. Search each name verbatim with "AI" (`Jev AI`, `Hermes AI model`, `Claude Anthropic news`) plus a recency word. Hermes = the Nous Research model family unless the user has said otherwise. If nothing new exists for one of the three today, say so in one line ("Quiet day for Hermes") rather than padding with old news. Do not invent releases. If "Jev" returns nothing recognisable across two searches, print a one-line note asking the user to confirm what Jev refers to, and keep the other two.

### 3. Dalal Street — Indian market sentiment
Report **facts first, mood second**, and label which is which:
- **Numbers**: Nifty 50 and Sensex close/latest, gold (MCX and international), INR/USD, FII/DII flows if reported. Search `Nifty Sensex today`, `gold price India today`, `FII DII flow today`.
- **Sentiment from X.com**: what the finance/investing community on X is talking about. Use an X/Twitter connector if one is connected; otherwise search `Nifty X sentiment today`, `stock market twitter India today`, and news roundups that quote X posts. Summarise the mood in your own words (bullish / cautious / fearful) with 2–3 themes; don't quote individual posts beyond a few words.
- **Drivers**: global uncertainties (Fed, oil, geopolitics, US tariffs), Indian government/RBI/SEBI actions, sector movers.
- **Portfolio note**: a generic "what this means for a typical Indian retail portfolio" line — no personal financial advice, no buy/sell calls; note you're not an adviser.

### 4. Daily Motivation
A boxed sidebar: the quote, its author, and one line tying it to today.

## Layout (Straits Times-style broadsheet)

Write plain HTML + CSS in one file, no frameworks. The look:

- **Masthead**: paper name in a heavy serif (Playfair Display / Georgia fallback), centred, black on cream/white, with thin double rules above and below. Under it a dateline strip: `Monday, 28 September 2026 · Singapore · Morning Edition`. The paper is named **The Daily Edition** — do not use the Straits Times name, logo, wordmark or blue masthead; the resemblance is layout and typography only.
- **Grid**: 3 columns on desktop, 1 column on phones (most reads are on the mobile app: 16px gutters, no horizontal scroll, headlines wrap). Section names as small-caps kickers with a rule underneath.
- **Lead story**: the single most important item across all sections goes above the fold, spanning two columns, with a larger headline and a 2-sentence deck.
- **Stories**: headline (serif, bold), 2–4 sentence body in a readable serif at 16–17px, a source line `— Reuters, 07:40 SGT` linking to the article. Keep bodies short; the page must not scroll more than ~2 screens on a phone.
- **Market box**: a small table for the numbers (index, level, change) with green/red change colouring, then the sentiment paragraph.
- **Motivation box**: shaded sidebar with a large opening quotation mark.
- **Footer**: "Compiled by Claude at HH:MM SGT · Sources linked inline · Not financial advice."
- Dark-mode friendly: define colours as CSS variables and provide a `prefers-color-scheme: dark` override.

## Quality bar

- Every story links to a real, fetched source; if a search returns nothing solid, write fewer stories, not vaguer ones.
- Don't copy article sentences — rewrite in a newspaper voice (short, active, present tense for headlines).
- Keep total length to roughly 700–900 words of body text.
- If the same story would appear in two sections, put it in the more specific one and cross-reference.