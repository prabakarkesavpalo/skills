# Worked example — Makan Mate (2026-10-04)

Repo: `Desktop/Palo IT/code/experiements/gen-e2-fun-app`. Built in one session from the Gen-e2 project template zip.

## Product in one line

For hungry, indecisive office teams, Makan Mate spins a roulette over the team's own curated hawker stalls, remembers
every visit and rating, and ranks the stalls on a leaderboard.

## Stories → endpoints → UI

| Story | Capability | Endpoints | UI |
| --- | --- | --- | --- |
| 001 | Stall directory (add / filter / remove, must-try dish, price band) | `GET/POST /stalls`, `GET/DELETE /stalls/{id}` | Stalls tab, AddStallForm, ConfirmDialog |
| 002 | Lunch Roulette (server-side random pick, filters, exclusions) | `POST /roulette/spin` | SVG Wheel, WinnerCard, aria-live |
| 003 | Log a visit with 1–5 stars and note | `GET/POST /visits` | LogVisitDialog, Visits feed |
| 004 | Leaderboard by Makan Score + team stats | `GET /leaderboard` | StatTiles, podium list |

## Numbers

- 17 seeded stalls, 51 visits, 25 spins
- 44 API tests (vitest + supertest, temp `db.json`) + 8 web tests = 52, one per AC scenario
- 0 npm vulnerabilities after upgrading vitest and dropping markdownlint-cli2 from devDependencies
- 5 conventional commits, all passing the template hooks
- Demo: 97 s, 1280×800, ~5 MB mp4

## Decisions worth reusing

- **Makan Score** `(v/(v+m))·R + (m/(v+m))·C` with a *fixed* neutral prior `C = 3.0`, `m = 3`; unrated stalls score 0.
  A team-average prior fails the "one lucky 5★ must not beat a steady 4.6★" rule when the team rates generously.
- Winner chosen server-side so every client sees the same result and spins are auditable.
- Stall identity = `name + hawkerCentre`, case- and whitespace-insensitive → `409 DUPLICATE_STALL`.
- Deleting a stall cascades to its visits and spins (recorded as decision D-004).
- Diner's first name remembered in `localStorage`; no accounts (ADR-004).

## File tree (trimmed)

```text
docs/requirements/_overview/00..05, 99
docs/requirements/epic-001-lunch-roulette/{overview,story-001..004,story-00N-plan}.md
docs/architecture/{overview.md, decisions/ADR-001..004}
docs/api/contracts/makan-mate-api.yaml
docs/demo/{sprint-1-demo.mp4, roulette.png, leaderboard.png}
apps/design/DESIGN.md
apps/web/src/{App.tsx, api/client.ts, hooks.ts, types.ts, components/*, features/{roulette,stalls,visits,leaderboard}, styles/{tokens,app}.css}
services/api/src/{app.ts, server.ts, domain/types.ts, db/json-store.ts, middleware/{app-error,error-handler}.ts, routes/*.router.ts, routes/schemas.ts, services/*.service.ts, services/makan-score.ts}
services/api/{data/seed.json, tests/{helpers,stalls,roulette,visits,leaderboard}.test.ts}
scripts/{setup.sh, record-demo.py}
.github/instructions/typescript.instructions.md
```

## Demo scene order (97 s)

Title card → spin (no filters) → filtered spin (Indian, `$`) → "I ate here" rating dialog → Stalls: empty submit shows
per-field errors → fill and add → remove with confirmation dialog → Leaderboard (scroll) → Visits feed →
"Under the hood" card (contract-first, ADRs, 52 tests, JSON db, tokens) → "npm install && npm run dev" end card.
