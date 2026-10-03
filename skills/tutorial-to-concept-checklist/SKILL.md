---
name: tutorial-to-concept-checklist
description: Turn a programming course video into a learning app and a concept checklist with evidence, a mobile-friendly HTML page and an architecture canvas. Use when asked to build a demo app from a YouTube course, list the concepts covered, or prove coverage.
---

# Tutorial to concept checklist

1. Get the course outline and transcript (chapters). Build the app in small slices that match the chapters; keep backend in `services/api`, frontend in `apps/web`.
2. List concepts, not chapters. One row per concept with: name, where it is in code (`file:line`), how it is proven (test or screenshot), status.
3. Prove each row. Backend: `node --test` against the real app. Frontend: Vitest and Testing Library. UI: Playwright screenshots.
4. Produce one self-contained `concept-checklist.html` (no external assets, readable on a phone) with the table, screenshots and links.
5. Add the `architecture-canvas` skill output for a mobile-friendly architecture view. Edit the model JSON, not the HTML. Edges must point at nodes, so add store nodes for data.
6. Keep honest status: confirmed, partial, not implemented. Say which chapters were skipped.

Gotchas: stale in-memory API state breaks Playwright runs, so restart the API between runs; after login, navigate explicitly and wait for the destination; a channel's React course needs its own checklist and its own redesign pass.
