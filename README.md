# skills

Personal Claude Code skills. One folder per skill in `skills/<name>/SKILL.md`
(frontmatter `name` + `description`, then steps and gotchas).

## Skills

| Skill | Use it for |
| --- | --- |
| `hermes-bot-onboarding` | Install Hermes bots from profile distributions, set model, board, smoke task |
| `hermes-kanban-test-round` | Chained probe tasks across all bots; diagnose stuck or slow tasks |
| `hermes-dashboard-access` | Hermes dashboard login facts and the screenshot fallback |
| `portable-macos-shell` | bash 3.2 / zsh-safe scripts, `sed -i ''`, dry-run pattern |
| `claude-code-secret-safe-ops` | Credentials and destructive cleanup under auto-mode blocks |
| `gen-e2-template-conversion` | Move a repo to the Gen-e2 layout, add `.loop/`, stay lint-clean |
| `tutorial-to-concept-checklist` | Course video to app, concept checklist, mobile HTML, canvas |
| `sprint-review-demo-video` | Small narrated demo video with Playwright, `say`, ffmpeg |
| `first-ai-agent-onboarding` | Build a first AI agent end to end: one job, base LLM, tools, loop, memory, interface |
| `architecture-canvas` | Turn an architecture model (JSON) into one zoomable, searchable HTML canvas |
| `architecture-flow-mapper` | Trace real user flows in a codebase into a grounded architecture model with file:line refs |
| `daily-newspaper` | Build the one-page 8am morning newspaper (tech, Hermes/Claude, Indian markets) |
| `notes-to-infographic` | Turn notes, transcripts or reports into a one-page portrait infographic PNG |
| `stock-news-timeline` | Timeline of news and price impact for any stocks or IBKR holdings, with your trades overlaid |

## Maintain

```bash
scripts/sync.sh pull --apply   # repo -> ~/.claude/skills (new machine)
scripts/sync.sh push --apply   # ~/.claude/skills -> repo (after editing a skill)
git add -A && git commit -m "skill: <name> - <what changed>" && git push
```

Add a skill: create `skills/<name>/SKILL.md`, add a row above, run `pull --apply`.
Keep skills short and free of secrets, tokens and machine-specific paths.
