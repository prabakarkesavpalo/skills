# Architecture model schema

`scripts/build_canvas.py` renders one JSON file into the canvas. Everything except `title`, `lanes` and `nodes` is optional. Run `python scripts/build_canvas.py model.json --check` to validate.

## Top level

| key | type | meaning |
|---|---|---|
| `title` | string | Shown in the header and the browser tab. |
| `subtitle` | string | One line under the title: what this map covers, and when it was made. |
| `generated_from` | string | Repo and commit (or "pasted files") the map was built from. Shown in the footer so readers know how fresh it is. |
| `lanes` | array | Swimlanes, one per system or runtime (browser, backend, database, storage, workers, external). Rendered top to bottom in the order given. |
| `flows` | array | The user journeys: sign up, pay, guest pass, upload. Each becomes a tab. |
| `nodes` | array | The boxes: steps, functions, endpoints, workers, buckets, UI screens. |
| `edges` | array | The arrows between nodes. |
| `entities` | array | Tables or collections, shown on the "Data model" tab. |
| `relations` | array | Foreign keys between entities. |
| `open_questions` | array | Things the code did not settle. Shown behind the `?` button. |

## lanes
`{ "id": "workers", "label": "Modal workers", "color": "#8f3fd1" }` — `color` is optional; a palette is applied automatically.

Pick lanes by where the code runs, not by team or folder. A reader should be able to see every boundary a request crosses.

## flows
`{ "id": "upload", "label": "Upload a file", "description": "optional" }`

## nodes
```json
{
  "id": "files_done",
  "label": "files.markUploaded",
  "lane": "backend",
  "kind": "mutation",
  "flows": ["upload"],
  "order": 4,
  "summary": "Creates the file row and enqueues processing.",
  "details": "Longer notes shown in the side panel. Say what it reads and writes, and any condition that changes the path.",
  "refs": [{ "path": "api/files.ts", "line": 80, "note": "inserts into files" }],
  "status": "confirmed"
}
```
- `id`: unique, shared id space with entities.
- `lane`: must match a lane id.
- `kind`: free text badge. Useful values: `ui`, `query`, `mutation`, `action`, `http`, `webhook`, `cron`, `queue`, `worker`, `bucket`, `table`, `auth`, `external`.
- `flows`: flow ids this step belongs to. A node may belong to several flows. Use `["*"]` for shared infrastructure that should appear in every flow.
- `order`: number. Left-to-right position within a flow. Nodes in the same lane with the same order stack vertically. Ties across lanes line up in one column, so use equal orders for steps that happen "at the same point" in time.
- `summary`: at most about 70 characters. It is cut off on the box.
- `refs`: file path (relative to the repo root) plus line. Every `confirmed` node needs at least one.
- `status`:
  - `confirmed`: you read the code that does this.
  - `inferred`: strongly implied (a call to an external service you cannot see into, a naming convention) but not read directly. Drawn dashed.
  - `unknown`: you know something must happen here but could not find it. Drawn dotted with a `?`.
  - `legacy`: code exists but nothing reaches it any more. Drawn faded.

## edges
```json
{ "from": "files_done", "to": "queue", "label": "enqueue job", "flows": ["upload"], "kind": "call", "async": true, "data": ["files"] }
```
- `label`: what is passed or why. An unlabeled arrow teaches the reader nothing.
- `kind`: `call` (default), `write` (blue, changes stored data), `read` (thin).
- `async`: true for anything that does not block the caller: scheduled functions, queues, webhooks, `spawn`, callbacks. Drawn dashed. Getting this right is most of what makes the map useful.
- `data`: entity ids read or written; they appear under "Touched by" on the entity.

## entities and relations
```json
{ "id": "files", "label": "files", "lane": "backend", "fields": [{ "name": "workspaceId", "type": "id(workspaces)", "note": "optional" }], "refs": [...], "status": "confirmed" }
{ "from": "files", "to": "workspaces", "label": "belongs to", "cardinality": "N:1" }
```
Relations point from the table that holds the foreign key to the table it references. Draw only relations the schema actually declares or the code clearly relies on. Two tables that never reference each other are independent, and showing that is the point.

## open_questions
`{ "text": "What happens to guest files at sign-up?", "refs": ["api/auth.ts:40"] }` or plain strings.
