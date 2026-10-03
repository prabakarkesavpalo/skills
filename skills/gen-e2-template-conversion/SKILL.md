---
name: gen-e2-template-conversion
description: Convert an existing app repo to the Gen-e2 project template layout and keep docs lint-clean. Use when asked to restructure a repo the Gen-e2 way, align to the Gen-e2 template or hub, or add the .loop delivery-loop folder to a product repo.
---

# Convert a repo to the Gen-e2 template

1. Use the newest template export the user gives you. A first pass on an older template was redone; ask which version is current before starting.
2. Layout: `.github/instructions/*.instructions.md` (with `applyTo`) indexed in `AGENTS.md`, `.github/skills/`, `docs/requirements/_overview`, `epic-NNN-*/` with `story-NNN.md` and `story-NNN-plan.md`, `docs/architecture` with ADRs, `docs/api/contracts` (OpenAPI, validate it), hooks via `core.hooksPath`, `CLAUDE.md` importing `AGENTS.md`.
3. Roles: the human is the Navigator, the AI is Crew. Conventional commits `type(scope): emoji description`. Story first, then plan, then code.
4. Keep the working app and its evidence (checklists, demo) as is; move code to the template paths and repoint CI globs.
5. For a delivery loop add `.loop/` (README, routing.yaml, state schema and state.json, gates, inbox, evidence, reviews). Gates must be bash-3.2 portable.
6. Lint before committing, because the hook blocks bad commits: markdownlint line limit 400, table rows cannot wrap, code fences need a language, no trailing spaces, no duplicate headings, dot-directories need explicit globs.
7. Record decisions in ADRs and a decision log; do not rewrite a user-supplied source document, even when you rename a term elsewhere.
