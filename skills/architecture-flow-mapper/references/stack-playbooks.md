# Stack playbooks

What to look for, per technology, when tracing a flow. Use the sections that match what `scan_stack.py` found. These describe how the technologies work in general; always confirm against the actual code, because every app wires them differently.

Contents: Convex · Modal · R2 / S3 storage · Auth, guests and accounts · Billing · Queues and background jobs · Generic web backends · Tracing ownership between entities

---

## Convex

**Where things live**
- `convex/schema.ts`: tables via `defineTable({...})`. Convex does not enforce foreign keys. A relationship exists only where a field is `v.id("otherTable")` (or an id stored inside an array/object). Two tables with no `v.id` pointing either way are independent.
- `convex/*.ts`: functions. The kind decides behavior:
  - `query`: read-only, reactive; the UI re-renders when its data changes.
  - `mutation`: transactional write. Runs inside the database and cannot call external APIs.
  - `action`: may call external services and other functions (`ctx.runQuery/runMutation/runAction`), but is not transactional. Anything touching R2, Modal, Stripe or an LLM is usually an action.
  - `internalQuery/internalMutation/internalAction`: callable only from other backend code, never from the browser. Referenced as `internal.file.fn`; public ones as `api.file.fn`.
  - `httpAction` registered in `convex/http.ts` via `http.route({ path, method, handler })`: public HTTP endpoints. Webhooks (payments, Modal callbacks) arrive here.
- `convex/crons.ts`: scheduled jobs.
- `ctx.scheduler.runAfter(ms, internal.x.y, args)` / `runAt`: an async hop. When called from a mutation, the scheduled job is committed together with the mutation. Treat each as a dashed arrow.
- `convex/convex.config.ts`: installed components (R2, rate limiter, workflow, …). A component can hide whole sub-flows; read its docs section if one is in play.
- `convex/auth.config.ts`, `convex/auth.ts`, `ctx.auth.getUserIdentity()`: how identity is established and checked. Look at what each function does when there is no identity (guest path).

**Client side**: trace from the UI by names. `useMutation(api.files.createUpload)`, `useQuery(api.chats.list)`, `useAction(...)`. Grep the exact `api.<file>.<fn>` string to find the UI caller. A function with no callers anywhere is a dead-code candidate: list it under open questions.

**Questions to answer**: which function creates each row, which actions leave Convex (and to where), which scheduled jobs exist, which HTTP routes call back into the system.

---

## Modal

**Mental model** (the usual source of confusion)
- The unit of deployment is an **App**: `app = modal.App("name")`. `modal deploy path/to/file.py` publishes it under that name.
- An App holds **Functions** (`@app.function(...)`) and **Classes** (`@app.cls(...)` with methods). There is no standalone "worker" object. Each Function gets its own autoscaling pool of containers, built from the `Image` it declares, and a container is started on demand when something calls it.
- So "one worker with multiple apps" almost always means one of: (a) several `modal.App(...)` names in different files, each deployed separately; (b) one App with many Functions; (c) one App that pulls others in with `app.include(...)`. Count distinct `modal.App(` names, find how each is deployed (CI workflows, `package.json` scripts, Makefile, README), and list the Functions under each. That list is the answer.
- Environments (`modal deploy --env`) can host the same app name for dev and prod; check scripts for `--env` or `MODAL_ENVIRONMENT`.

**How a Function is triggered** (each is a different kind of arrow)
- `fn.remote(...)`: caller waits for the result (sync).
- `fn.spawn(...)` / `fn.spawn_map(...)`: fire and forget; returns a call id, result fetched later or reported by callback (async).
- `fn.map(...)` / `starmap`: fan-out.
- Web endpoints: `@modal.fastapi_endpoint`, `@modal.asgi_app`, `@modal.web_server`, `@modal.wsgi_app`: the backend or browser calls an HTTPS URL. Find where that URL is configured (env var names help).
- `schedule=modal.Cron(...)` or `modal.Period(...)`: time-triggered, no caller.
- From outside Modal (a Convex action, a Node server) the caller uses Modal's client or HTTP. In Python, `modal.Function.from_name("app-name", "function-name")` is a cross-app lookup; the two strings tell you which App and Function are called.

**What the workers can reach** (read `modal.Secret.from_name(...)`, `modal.Volume`, `modal.CloudBucketMount`, env reads): R2/S3 credentials, a callback URL or deploy key for the backend, LLM keys. Secrets are the quickest way to see which systems a worker talks to. Never print secret values; names only.

**Questions to answer**: which Modal apps exist and which are actually deployed, who calls each Function and how, how results come back (callback HTTP route, polling a table, return value), what happens on failure or timeout (retries are configured on the Function).

---

## R2 / S3 / object storage

- Direct-to-bucket upload with a **presigned URL**: backend signs a PUT URL (`getSignedUrl`, `generate_presigned_url`, `createPresignedPost`, `generateUploadUrl` on the R2 component), the browser PUTs the bytes straight to the bucket. The backend never sees the bytes. Alternative: the backend receives the file and writes it itself. Find out which; the architecture differs.
- Typical three-step shape: (1) create an upload record and URL, (2) client uploads, (3) client or a bucket event confirms. Check what happens if step 3 never arrives (orphaned objects, rows stuck in "uploading").
- Record: bucket name (usually an env var), object-key scheme (which ids it embeds), public vs private access, who reads objects (workers, browser via signed GET), who deletes (cleanup jobs, cascade on row delete).
- The database row holds the object key. The key plus bucket is the join between the database and storage.

---

## Auth, guests and accounts

- Identify the identity provider and where a request becomes "a user" (`getUserIdentity`, middleware, session cookie, JWT verify).
- Guest/anonymous access: look for anonymous sign-in, guest tokens or passes, a quota or expiry field, and a purge job. The key question is **what happens to guest data at sign-up**: search for words like `claim`, `merge`, `migrate`, `transfer`, `upgrade`. If nothing exists, say so explicitly (that is a finding).
- Sign-up side effects: default rows created (workspace, project, chat, settings), emails sent, billing customer created.
- Entitlement checks: which functions check plan or quota, and which skip it.

---

## Billing

- Checkout creation (server asks the provider for a session/URL), the provider-hosted page, then the **webhook** that actually grants the plan. The browser redirect back is not proof of payment; trace the webhook.
- For each webhook handler: signature verification, idempotency (what if the event arrives twice), which event names are handled (`checkout.session.completed`, `customer.subscription.*`, `invoice.*`), what it writes (plan, credits, ledger rows).
- Where entitlement state lives and who reads it (upload path, model calls, limits).
- Customer portal, cancellation and failed-payment handling if present.

---

## Queues and background jobs

Treat every deferral as a dashed arrow: scheduler calls, queue publishes (SQS, BullMQ, Inngest, Celery `.delay`), cron entries, `spawn`, webhooks, database triggers, polling loops. Record who enqueues, who consumes, the payload, the callback path, and the retry/failure behavior. If a "queue" is really a table that a worker polls, say so.

---

## Generic web backends (Express, FastAPI, Next.js routes, Rails, Django)

Entry points are route definitions (`app.get/post`, `@app.post`, `app/**/route.ts`, `pages/api/**`, `urls.py`, `routes.rb`). For each flow, follow route → handler → service/domain function → data access → outbound calls. Middleware (auth, rate limit, tenancy) belongs on the path: record it as a node if it can reject the request.

---

## Tracing ownership between entities (the "how do chats and projects relate" question)

Do not assume a hierarchy from names. Establish it from evidence:
1. Read the schema: which tables hold an id of which other table? Record each as a relation. A table with no pointers to or from another is independent.
2. Read the creation paths: in the function a flow runs, list every row inserted and which ids are written into it. If a function inserts both a chat and a project, check whether either row stores the other's id.
3. Read the consumers: which queries list or filter by each id (by project, by chat, by user)? If the UI only ever lists chats by user and never by project, the project is not a parent in practice.
4. Look for leftovers: a table that is still written but never read (or read but no longer written) is `legacy`. Say so with the evidence (the writer's and reader's file:line, or their absence).
Report the result in one sentence per pair of entities: "chats belong to users only; projects hold files and have no link to chats."
