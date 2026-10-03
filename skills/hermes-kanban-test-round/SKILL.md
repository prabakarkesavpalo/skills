---
name: hermes-kanban-test-round
description: Run and read a test round across all Hermes bots using chained Kanban probe tasks, and diagnose slow or stuck tasks. Use when asked to test that every bot can perform its duty, why a Kanban task is stuck or slow, or to verify a multi-bot hand-off.
---

# Kanban test round

One harmless probe task per bot, chained with `--parent` in lane order, each reviewed by the coordinator.

## Create

- Round id like `round-MMDD-HHMM`; output dir `<repo>/.loop/inbox/<round>/` (git-ignore it).
- Per bot: `hermes kanban create "<round> <bot> probe" --assignee <bot> --workspace dir:<repo> --body <b> --max-retries 2 --max-runtime 10m --idempotency-key <round>-<bot> --json [--parent <prev-id>]`. The JSON reply has `id`.
- Body must give the bot everything: its SOUL.md path (`$HOME/.hermes/profiles/<bot>/SOUL.md`) and "do not search the disk", the previous bot's file to read, the exact four-line output, and "request review from the coordinator".
- Output format: `# <bot> probe`, `role: ...`, `received-from: <previous PROBE line or none>`, `PROBE-OK <bot>`.

## Run and check

- Loop `hermes kanban dispatch --max 1` every 15 s until no task is ready, running, review or todo; cap the total time.
- Pass = the probe file has `PROBE-OK <bot>` AND the Kanban task is `done`.
- Read stuck tasks with `hermes kanban show <id>` (events, runs) and `hermes kanban log <id>`.

## Reading the symptoms

| Symptom | Cause | Fix |
| --- | --- | --- |
| `timed_out` at the runtime cap | Bot searched the disk or hung in an API call | Give exact paths in the body |
| `protocol_violation` | Worker exited without a kanban tool call | Retry; tighten the SOUL's Kanban section |
| Chained task stays `todo` | Parent not done yet | Normal; the chain is serial, so wall time is the sum |
| Crashed twice, then blocked | No model or no credentials | See the onboarding skill, then unblock |

The first review of a round is slow (several minutes); later ones take about 30 s. Report that before calling anything stuck.
