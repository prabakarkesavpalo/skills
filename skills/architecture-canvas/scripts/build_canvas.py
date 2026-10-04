#!/usr/bin/env python3
"""Validate an architecture model (JSON) and render it as a self-contained, zoomable HTML canvas.

Usage:
    python build_canvas.py model.json -o architecture.html
    python build_canvas.py model.json --check      # validate only

Exit codes: 0 ok (warnings allowed), 1 errors found, 2 usage / IO problem.
The model format is documented in references/model-schema.md.
"""
import argparse
import html
import json
import sys
from pathlib import Path

STATUSES = {"confirmed", "inferred", "unknown", "legacy"}
TEMPLATE = Path(__file__).resolve().parent.parent / "assets" / "canvas_template.html"


def validate(m):
    errors, warnings = [], []

    def err(msg):
        errors.append(msg)

    def warn(msg):
        warnings.append(msg)

    if not isinstance(m, dict):
        return ["model must be a JSON object"], []
    for key in ("title", "lanes", "nodes"):
        if key not in m:
            err(f"missing top-level key: {key}")
    if errors:
        return errors, warnings

    lane_ids = [l.get("id") for l in m["lanes"]]
    if len(set(lane_ids)) != len(lane_ids):
        err("duplicate lane ids")
    flow_ids = {f.get("id") for f in m.get("flows", [])}

    ids = set()
    for n in m["nodes"]:
        nid = n.get("id")
        if not nid:
            err(f"node without id: {n.get('label')!r}")
            continue
        if nid in ids:
            err(f"duplicate node id: {nid}")
        ids.add(nid)
        if n.get("lane") not in lane_ids:
            err(f"node {nid}: unknown lane {n.get('lane')!r}")
        status = n.get("status", "confirmed")
        if status not in STATUSES:
            err(f"node {nid}: status {status!r} not in {sorted(STATUSES)}")
        if "order" in n and not isinstance(n["order"], (int, float)):
            err(f"node {nid}: order must be a number")
        flows = n.get("flows")
        if not flows:
            warn(f"node {nid}: no flows listed (use ['*'] for shared infrastructure)")
        else:
            for f in flows:
                if f != "*" and f not in flow_ids:
                    err(f"node {nid}: unknown flow {f!r}")
        if status == "confirmed" and not n.get("refs"):
            warn(f"node {nid}: marked confirmed but has no refs (file:line). Add refs or mark it inferred/unknown")
        if not n.get("summary"):
            warn(f"node {nid}: no summary")

    ent_ids = set()
    for e in m.get("entities", []):
        eid = e.get("id")
        if not eid:
            err(f"entity without id: {e.get('label')!r}")
            continue
        if eid in ent_ids or eid in ids:
            err(f"duplicate id (entities share the id space with nodes): {eid}")
        ent_ids.add(eid)
        if e.get("lane") and e["lane"] not in lane_ids:
            err(f"entity {eid}: unknown lane {e['lane']!r}")
        if e.get("status", "confirmed") == "confirmed" and not e.get("refs"):
            warn(f"entity {eid}: confirmed but no refs")

    for i, ed in enumerate(m.get("edges", [])):
        for end in ("from", "to"):
            if ed.get(end) not in ids:
                err(f"edge #{i}: {end}={ed.get(end)!r} is not a node id")
        for f in ed.get("flows", []) or []:
            if f != "*" and f not in flow_ids:
                err(f"edge #{i}: unknown flow {f!r}")
        for d in ed.get("data", []) or []:
            if d not in ent_ids:
                err(f"edge #{i}: data entity {d!r} not found")
        if not ed.get("label"):
            warn(f"edge #{i} ({ed.get('from')} -> {ed.get('to')}): no label; say what is passed or why")

    for i, r in enumerate(m.get("relations", [])):
        for end in ("from", "to"):
            if r.get(end) not in ent_ids:
                err(f"relation #{i}: {end}={r.get(end)!r} is not an entity id")

    connected = {e.get("from") for e in m.get("edges", [])} | {e.get("to") for e in m.get("edges", [])}
    for nid in ids - connected:
        warn(f"node {nid}: no edges (isolated)")
    return errors, warnings


def build(model, out_path):
    tpl = TEMPLATE.read_text(encoding="utf-8")
    payload = json.dumps(model, ensure_ascii=False).replace("</", "<\\/").replace("<!--", "<\\!--")
    page = tpl.replace("__TITLE__", html.escape(str(model.get("title", "Architecture")))).replace("__MODEL_JSON__", payload)
    out_path.write_text(page, encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("model", type=Path)
    ap.add_argument("-o", "--out", type=Path, default=None, help="output HTML (default: <model>.html)")
    ap.add_argument("--check", action="store_true", help="validate only, write nothing")
    args = ap.parse_args()
    try:
        model = json.loads(args.model.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"cannot read model: {exc}", file=sys.stderr)
        return 2
    errors, warnings = validate(model)
    for w in warnings:
        print(f"warning: {w}")
    for e in errors:
        print(f"ERROR: {e}")
    if errors:
        print(f"{len(errors)} error(s); canvas not written.")
        return 1
    n, e = len(model.get("nodes", [])), len(model.get("edges", []))
    if args.check:
        print(f"ok: {n} nodes, {e} edges, {len(model.get('entities', []))} entities, {len(warnings)} warning(s)")
        return 0
    out = args.out or args.model.with_suffix(".html")
    build(model, out)
    print(f"wrote {out} ({n} nodes, {e} edges, {len(model.get('entities', []))} entities, {len(warnings)} warning(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
