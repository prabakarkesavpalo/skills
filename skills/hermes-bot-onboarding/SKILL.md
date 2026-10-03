---
name: hermes-bot-onboarding
description: Onboard a set of Hermes Agent bots from a git repo with no manual copying - profile distributions, model default, credentials, Kanban board and a smoke task. Use when asked to install, create or onboard Hermes bots or profiles locally, or when a new Hermes profile crashes with 'not connected to any AI provider'.
---

# Onboard Hermes bots

Use profile distributions, not hand-copied files. One folder per bot, installed with one command.

## Layout per bot

```text
profiles/<bot>/distribution.yaml   name, version, description, hermes_requires, env_requires
profiles/<bot>/config.yaml         MUST set the model (model.default and model.provider)
profiles/<bot>/SOUL.md             identity and rules
profiles/<bot>/skills/<name>/SKILL.md
profiles/<bot>/.gitignore          .env, auth.json, memories/, sessions/
```

## Steps

1. Write an installer that is dry-run by default and takes `--apply`.
2. Per bot run `hermes profile install <dir> --name <bot> --alias -y --force`, then `hermes profile describe <bot> --text "<desc>"`. `--force` keeps user data.
3. After install verify the model: `hermes -p <bot> config get model`. If empty, set `model.default` and `model.provider` with `hermes -p <bot> config set`.
4. Credentials are the user's step. Offer an explicit `--share-auth` flag that copies the default profile's auth file, or `hermes -p <bot> auth add`. Never read, print or copy credentials yourself.
5. Prove each bot answers: `hermes -p <bot> -z 'Reply with exactly: OK'`.
6. Create a Kanban board for the product repo: `hermes kanban boards create <slug> --default-workdir <repo> --switch`. Queue a smoke task with `--assignee`, `--workspace dir:<repo>`, `--max-retries 2`, `--idempotency-key`.
7. Run it: `hermes kanban dispatch --max 1`.

## Gotchas

- A profile with no model crashes the task twice, then the task goes to blocked. Ship the model in `config.yaml`, then `hermes kanban unblock <id>`.
- The board list and dashboard show only the active board. Use `hermes kanban boards switch <slug>` if tasks seem missing.
- Renaming a bot means `hermes profile delete <old> -y` then installing the new name; old tasks keep the old assignee name.
- Use `sed -i ''` on macOS and `while read` loops, because zsh does not word-split unquoted variables.
