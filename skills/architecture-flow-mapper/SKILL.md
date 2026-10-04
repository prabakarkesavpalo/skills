---
name: architecture-flow-mapper
description: Trace what actually happens in a codebase for end-to-end user flows (sign up, sign in, guest or anonymous access, payment, creating or uploading something, background processing) and record it as a grounded architecture model with file:line references, then draw it as a zoomable canvas. Use this whenever the user wants to understand or get an overview of how their app really works, says the architecture changed and they are losing track, asks what happens when a user does X, asks how services connect (Convex, Modal, R2, S3, Stripe, queues, workers, serverless functions, microservices), asks how entities like chats, projects or files relate, or wants a flow map, system map or architecture diagram of existing code. Works on any stack; has extra playbooks for Convex, Modal, R2/S3, auth and billing.
---

# Architecture flow mapper

Goal: give the user an accurate picture of how their system behaves, built from the code rather than from assumptions, and finish with their own questions answered. Maps are only useful if they can be trusted, so every box is tied to a file and line, or is openly marked as not confirmed.

## 0. Make sure you are looking at the right code

Nothing below works without the actual source. Before tracing:
- Confirm you can read the repo or folder. If the code is not available (empty workspace, device not connected, repo not accessible), say so and ask for access or for the key files. Do not draw a plausible-looking architecture from the user's description alone; a confident wrong map is worse than none.
- Run the scanner and check it against what the user described: `python scripts/scan_stack.py <repo-root>`. If the user says "Convex, R2 and Modal" and the scan finds none of them, this is the wrong repo. Stop and say what you found instead of continuing.
- Monorepos: the app may sit in a subfolder. The scan's top-level directories and signal examples show where.

## 1. Pick the flows

Default set, adapted to what exists in the code:
1. **Identity**: sign up and sign in
2. **Guest / anonymous access**, and what happens to guest data later
3. **Billing**: upgrade, payment confirmation, entitlement
4. **Core create or upload action**, through storage and background processing, to the result the user sees

Add or swap flows if the user names others (e.g. "share a project", "delete account"). Do not interview the user about flows unless the request is truly ambiguous; state your choice and proceed.

## 2. Orient (read before tracing)

- The scan report: stack signals, entry points (functions, routes, crons, schedulers, workers), env var names.
- Any `README`, `AGENTS.md`, `CLAUDE.md`, `docs/` that describe the intended design. Treat them as claims to verify, not as truth: the user said a lot has changed.
- Deploy and runtime config: CI workflows, `wrangler.toml`, Dockerfiles, `modal deploy` scripts, `vercel.json`. They show which runtimes exist and what is actually shipped.
- The data schema (see step 3).
- `references/stack-playbooks.md`: read the sections for the technologies the scan found. They say what each technology can hide and which questions to answer.

## 3. Data first

List every table or collection and every declared relationship. Mark which entities are independent of each other. Do this before tracing, because flows are mostly "who creates which rows", and it settles questions like "are chats tied to projects" early. The ownership procedure is at the bottom of the playbooks file.

## 4. Trace each flow, boundary by boundary

Start at the trigger in the UI (button handler, form submit) and follow it:
UI → client call → server function → each thing it **writes, reads, schedules, enqueues or calls** → external service → how the result returns (callback route, polling, reactive query) → what the UI shows.

Method:
- At each hop, grep the exact name of the callee (e.g. `api.files.markUploaded`, `process_upload.spawn`) to find callers and callees instead of guessing from folder names.
- Every time control crosses a runtime (browser → backend → storage → worker → backend), make a node on each side and a labelled arrow. Mark arrows `async` when the caller does not wait.
- Record conditions that change the path (plan checks, quota, guest vs user). Branches are what users forget.
- Note failure behavior at async hops: retries, timeouts, what the user sees if the job dies.
- For large codebases, trace one flow per subagent in parallel. Each returns nodes and edges in the model format below; merge them and reconcile duplicate ids yourself.

## 5. Record the model

Write `architecture-model.json` in the format described in the architecture-canvas skill (`references/model-schema.md` there). Essentials:
- `lanes` = runtimes; `flows` = the journeys; `nodes` with `lane`, `kind`, `flows`, `order`, `summary`, `refs`, `status`; `edges` with `label` and `async`; `entities` and `relations` from the schema; `open_questions`.
- `status` discipline: `confirmed` only if you read the code that does it and can cite `refs` (path and line). `inferred` for what is strongly implied but not read (an external API's internals). `unknown` when something must happen but you could not find it. `legacy` for code nothing reaches any more.
- Put what you could not resolve in `open_questions` with the places you looked. "I searched `convex/` for claim/merge/migrate and found nothing: guest data is likely abandoned at sign-up" is a finding, not a gap.

## 6. Cross-check before drawing

The user said the architecture drifted, so reconcile the map against the inventory:
- Every table in the schema appears as an entity.
- Every function, route, cron and worker function from the scan is either in a flow or listed as "not reached by any flow" in `open_questions` (dead-code candidates).
- Every node that writes data has an edge with `data` pointing at the entity.
- Every `confirmed` node has refs. `build_canvas.py --check` flags the ones that do not.

## 7. Render and deliver

Use the architecture-canvas skill: validate with `--check`, build the HTML, publish it as an artifact (or send the file). Then reply with a short written summary that **answers the user's actual questions** in plain words (for example "chats and projects are independent; projects own files and nothing links them to chats; the upload creates both"), followed by the open questions. The canvas shows the structure; the summary delivers the understanding. Mention the commit or snapshot the map was built from, since it goes stale as the code changes.

## Re-running later

Because the model is a JSON file, an update is: re-scan, diff against the previous model (new functions, removed tables, changed arrows), edit the JSON, rebuild. Keep the previous model next to the new one when the user wants to see what changed.
