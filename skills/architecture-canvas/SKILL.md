---
name: architecture-canvas
description: Turn an architecture model (JSON of lanes, flow steps, arrows and tables) into one self-contained HTML canvas the user can zoom, pan, search and click through. Use this whenever the user wants a visual map, canvas, diagram or overview of how an app, system, backend, pipeline or data flow works, or says they are losing the overview of their architecture, even if they never say "diagram". Pairs with the architecture-flow-mapper skill, which builds the model from code; use this skill alone when the user already has the structure (or hands you a description) and just needs it drawn.
---

# Architecture canvas

Renders a JSON architecture model as a single HTML page with:
- one tab per user flow (sign up, pay, upload, …) plus an "Everything" tab and a "Data model" tab
- swimlanes per runtime (browser, backend, storage, workers, external), arrows labelled with what they carry, dashed for async
- drag to pan, scroll or pinch to zoom, Fit, search, arrow keys
- click any box for a side panel: summary, what it calls and what calls it, and the exact `file:line` references
- honest status styling: solid = confirmed in code, dashed = inferred, dotted with `?` = unknown
- an "open questions" button for anything the code did not settle

The page has no dependencies and works offline, on desktop and phone.

## Workflow

1. **Get a model.** If the structure comes from a codebase, use the `architecture-flow-mapper` skill first. If the user described the system in words, write the model from that description and mark every node `inferred` (nothing was read from code). Read `references/model-schema.md` for the format. `assets/example-model.json` is a small illustrative model you can copy from; never present its contents as real.
2. **Validate and build:**
   ```bash
   python scripts/build_canvas.py model.json --check
   python scripts/build_canvas.py model.json -o architecture.html
   ```
   Fix every ERROR. Read the warnings: "confirmed but has no refs" means the claim is unsupported, so either add the reference or downgrade the status.
3. **Deliver.** Publish `architecture.html` as an artifact (a canvas the user will revisit and share is exactly what artifacts are for). If artifacts are not available, send the file with SendUserFile. Say in a sentence or two what the page shows and, more importantly, the two or three things the map revealed that the user did not know. A diagram alone does not answer their questions; the answers do.
4. **Iterate by editing the JSON**, not the HTML. Rebuild after each change so the page always matches the model.

## Layout rules that keep maps readable

- 8 to 25 nodes per flow. If a flow needs more, split it into two flows or collapse repeated steps into one node with the detail in `details`.
- Lanes are runtimes, not folders. A request crossing a lane boundary is the interesting part of any architecture, so make every crossing an arrow.
- Give each arrow a label. Mark async arrows `"async": true`; the difference between "waits for" and "kicks off" is usually what the user is confused about.
- Order steps by time, left to right. Parallel steps share an `order` value and sit in different lanes or stack in one lane.
- Keep `summary` under about 70 characters; put the rest in `details`.

## Customizing

`assets/canvas_template.html` holds all styling and behavior. Lane colors come from the model (`lanes[].color`). Change the template only for behavior every future map should have; per-app tweaks belong in the model.
