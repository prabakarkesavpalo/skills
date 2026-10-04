#!/usr/bin/env python3
"""Fast first pass over a codebase: which stack is this, and where are the entry points?

It does NOT understand the code. It finds signals and candidate starting points so the real
reading (done by Claude) starts in the right files instead of grepping blindly.

Usage:
    python scan_stack.py /path/to/repo            # markdown report on stdout
    python scan_stack.py /path/to/repo --json out.json
    python scan_stack.py /path/to/repo --max 60   # more items per list
"""
import argparse
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

SKIP_DIRS = {".git", "node_modules", "dist", "build", ".next", ".nuxt", ".venv", "venv", "__pycache__",
             ".turbo", ".cache", "coverage", "_generated", "vendor", ".pnpm-store", "target", ".idea", ".vscode",
             # tests, fixtures, docs and translations describe or mock the app; they are not the app
             "tests", "test", "__tests__", "tests-js", "e2e", "__mocks__", "fixtures", "locales", "i18n", "website", "docs"}
CODE_EXT = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".py", ".go", ".rb", ".java", ".kt", ".rs", ".php", ".cs", ".sql", ".prisma", ".toml", ".yaml", ".yml", ".json"}
JSON_OK = {"package.json", "wrangler.json", "vercel.json", "convex.json"}   # other .json is usually data, not code
TEST_NAME = re.compile(r"(^test_|_test\.|\.test\.|\.spec\.|^conftest\.py$)")
LOCKFILE = re.compile(r"(lock\.ya?ml|lock\.json|-lock\.|\.lock$)")
MAX_BYTES = 400_000

# (signal, category, regex searched in code and dependency files)
SIGNALS = [
    ("Convex", "backend/db", r"from ['\"]convex/|@convex-dev/|\bdefineTable\("),
    ("Supabase", "backend/db", r"@supabase/|supabase\.co|createClient\(.*supabase"),
    ("Firebase", "backend/db", r"firebase-admin|firebase/app|firebase/firestore"),
    ("Prisma", "db", r"@prisma/client|prisma\.schema|^model\s+\w+\s*\{"),
    ("Drizzle", "db", r"drizzle-orm"),
    ("SQLAlchemy/Django ORM", "db", r"sqlalchemy|from django\.db import models"),
    ("Postgres/MySQL driver", "db", r"\bpg\b.*require|psycopg|asyncpg|mysql2"),
    ("Next.js", "frontend", r"\"next\"\s*:\s*\"[\^~]?\d|from ['\"]next/"),
    ("React", "frontend", r"\"react\"\s*:"),
    ("Express/Fastify/Hono", "backend", r"from ['\"](express|fastify|hono)['\"]|require\(['\"]express['\"]\)"),
    ("FastAPI/Flask", "backend", r"from fastapi|import fastapi|from flask|import flask"),
    ("Clerk", "auth", r"@clerk/|clerk\.dev|clerk\.com"),
    ("Auth.js / NextAuth", "auth", r"next-auth|@auth/core|@convex-dev/auth"),
    ("Auth0 / Cognito / WorkOS", "auth", r"auth0|amazon-cognito|@workos-inc"),
    ("Anonymous / guest access", "auth", r"signInAnonymously|isAnonymous|anonymous[_-]?(user|session|id)|guest[_-]?(pass|session|user|token|id)|guestPass|GuestPass"),
    ("Stripe", "billing", r"from ['\"]stripe['\"]|require\(['\"]stripe['\"]\)|^\s*import stripe\b|\"stripe\"\s*:|stripe-signature|checkout\.sessions|api\.stripe\.com"),
    ("Polar / Lemon Squeezy / Paddle", "billing", r"@polar-sh|polar\.sh|lemonsqueezy|paddle"),
    ("Cloudflare R2", "storage", r"r2\.cloudflarestorage\.com|@convex-dev/r2|\bR2_[A-Z_]+|r2_bucket"),
    ("AWS S3 / compatible", "storage", r"@aws-sdk/client-s3|boto3|s3\.amazonaws\.com|getSignedUrl|createPresignedPost|generate_presigned"),
    ("Uploadthing / Vercel Blob / GCS", "storage", r"uploadthing|@vercel/blob|@google-cloud/storage"),
    ("Modal", "compute", r"^\s*import modal\b|from modal import|modal\.App\(|modal\.Function"),
    ("Celery / RQ / Dramatiq", "queue", r"celery|\brq\b.*Queue|dramatiq"),
    ("BullMQ / Inngest / Trigger.dev", "queue", r"bullmq|inngest|@trigger\.dev"),
    ("SQS / Pub/Sub / Kafka", "queue", r"@aws-sdk/client-sqs|client\(['\"]sqs['\"]|@google-cloud/pubsub|google\.cloud import pubsub|kafkajs|confluent_kafka"),
    ("Vercel / Cloudflare Workers / Lambda", "compute", r"wrangler\.toml|vercel\.json|serverless\.yml|aws-lambda|\bexport default \{\s*fetch"),
    ("Docker / Kubernetes", "infra", r"^FROM\s+\S+:\S+|^FROM\s+\S+\s+AS\s+\w+|apiVersion:\s*apps/v1"),
    ("LLM providers", "ai", r"anthropic|openai|@ai-sdk/|google-genai|vertexai"),
    ("Webhooks", "events", r"['\"/]webhooks?['\"/]|WEBHOOK_SECRET|webhook_secret"),
]

PATTERNS = {
    "convex_functions": (re.compile(r"export\s+(?:const|default)\s+(\w+)?\s*=?\s*(query|mutation|action|internalQuery|internalMutation|internalAction|httpAction)\s*\("), "convex/"),
    "convex_tables": (re.compile(r"^\s*(\w+)\s*:\s*defineTable\(", re.M), "convex/"),
    "convex_crons": (re.compile(r"crons\.(interval|cron|daily|hourly|weekly|monthly)\(\s*['\"]([^'\"]+)"), "convex/"),
    "convex_http_routes": (re.compile(r"path:\s*['\"]([^'\"]+)['\"]\s*,\s*method:\s*['\"](\w+)['\"]", re.S), "convex/"),
    "convex_scheduler": (re.compile(r"scheduler\.(runAfter|runAt)\(\s*[^,]*,\s*((?:internal|api)\.[\w.]+)"), "convex/"),
    "modal_apps": (re.compile(r"modal\.App\(\s*(?:name\s*=\s*)?['\"]([^'\"]+)['\"]"), None),
    "modal_functions": (re.compile(r"^@(\w+)\.(function|cls)\b[^\n]*\n(?:@[^\n]*\n)*\s*(?:async\s+)?(?:def|class)\s+(\w+)", re.M), None),
    "modal_web_endpoints": (re.compile(r"@modal\.(fastapi_endpoint|asgi_app|wsgi_app|web_server|web_endpoint)"), None),
    "modal_cross_app_lookup": (re.compile(r"modal\.(?:Function|Cls)\.(?:from_name|lookup)\(\s*['\"]([^'\"]+)['\"]\s*,\s*['\"]([^'\"]+)"), None),
    "modal_invocations": (re.compile(r"\.(spawn|remote|starmap|spawn_map)\("), None),
    "modal_schedules": (re.compile(r"modal\.(Cron|Period)\(([^)]*)\)"), None),
    "modal_volumes_secrets": (re.compile(r"modal\.(Volume|Secret|CloudBucketMount)\.\w+\(\s*['\"]?([^'\")]*)"), None),
    "next_or_api_routes": (re.compile(r"(?!)"), None),  # filled by path rules below
    "presign_or_upload_url": (re.compile(r"generateUploadUrl|getSignedUrl|createPresignedPost|generate_presigned_url|createUploadUrl|uploadUrl"), None),
    "stripe_webhook_events": (re.compile(r"['\"]((?:checkout\.session|customer\.subscription|invoice|payment_intent)\.[a-z_.]+)['\"]"), None),
}
ROUTE_PATH = re.compile(r"(^|/)(app/.*/route\.(ts|js)|pages/api/.*\.(ts|js)|src/app/.*/route\.(ts|js)|routes?/.*\.(ts|js|py))$")


def walk(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            p = Path(dirpath) / fn
            if TEST_NAME.search(fn) or LOCKFILE.search(fn):
                continue
            if p.suffix.lower() == ".json" and fn not in JSON_OK:
                continue
            if p.suffix.lower() in CODE_EXT or fn in {"Dockerfile", "wrangler.toml", ".env.example", "package.json"}:
                try:
                    if p.stat().st_size <= MAX_BYTES:
                        yield p
                except OSError:
                    pass


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", type=Path)
    ap.add_argument("--json", type=Path)
    ap.add_argument("--max", type=int, default=40, help="max items listed per section")
    a = ap.parse_args()
    root = a.root.resolve()
    if not root.is_dir():
        print(f"not a directory: {root}", file=sys.stderr)
        return 2

    sig_files = defaultdict(list)
    found = defaultdict(list)
    env_names, route_files, top_dirs = set(), [], set()
    n_files = 0
    compiled = [(s, c, re.compile(rx, re.I | re.M) if s in ("Anonymous / guest access", "Webhooks") else re.compile(rx, re.M)) for s, c, rx in SIGNALS]

    for p in walk(root):
        n_files += 1
        rel = str(p.relative_to(root))
        parts = rel.split("/")
        if len(parts) > 1:
            top_dirs.add(parts[0])
        if ROUTE_PATH.search(rel):
            route_files.append(rel)
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if p.name == ".env.example":
            env_names.update(m.group(1) for m in re.finditer(r"^\s*([A-Z][A-Z0-9_]+)\s*=", text, re.M))
        for name, cat, rx in compiled:
            if rx.search(text):
                sig_files[(name, cat)].append(rel)
        for key, (rx, scope) in PATTERNS.items():
            if scope and scope not in rel:
                continue
            if key == "next_or_api_routes":
                continue
            if key.startswith("modal_") and not (p.suffix == ".py" and "modal" in text):
                continue   # Modal is Python-first; avoids matching unrelated .spawn()/.remote() calls
            for m in rx.finditer(text):
                line = text.count("\n", 0, m.start()) + 1
                parts = [g for g in m.groups() if g] or [m.group(0).strip()[:60]]
                found[key].append({"file": rel, "line": line, "match": parts})

    out = {
        "root": str(root),
        "files_scanned": n_files,
        "top_level_dirs": sorted(top_dirs),
        "signals": [{"name": n, "category": c, "files": len(f), "examples": f[:4]} for (n, c), f in sorted(sig_files.items(), key=lambda kv: (kv[0][1], -len(kv[1])))],
        "route_files": route_files[: a.max],
        "env_var_names": sorted(env_names)[: a.max * 2],
        "entry_points": {k: v[: a.max] for k, v in found.items() if v and k != "modal_invocations"},
        "modal_invocation_count": len(found.get("modal_invocations", [])),
    }
    if a.json:
        a.json.write_text(json.dumps(out, indent=2))

    L = [f"# Stack scan: {root.name}", f"{n_files} source files scanned. Top-level dirs: {', '.join(out['top_level_dirs']) or '(flat)'}", ""]
    L.append("## Stack signals (category | signal | files | examples)")
    if not out["signals"]:
        L.append("- none detected. This repo may not contain the app you are looking for; ask the user before going further.")
    for s in out["signals"]:
        L.append(f"- {s['category']} | **{s['name']}** | {s['files']} | {', '.join(s['examples'])}")
    if out["env_var_names"]:
        L += ["", "## Env var names from .env.example (names only: hints at integrations)", ", ".join(out["env_var_names"])]
    if out["route_files"]:
        L += ["", "## Route files"] + [f"- {r}" for r in out["route_files"]]
    titles = {
        "convex_tables": "Convex tables (schema)", "convex_functions": "Convex functions (query/mutation/action)",
        "convex_http_routes": "Convex HTTP routes (webhooks, API)", "convex_crons": "Convex cron jobs",
        "convex_scheduler": "Convex scheduler calls (async hops)", "modal_apps": "Modal apps (deployment units)",
        "modal_functions": "Modal functions/classes (decorator, kind, name)", "modal_web_endpoints": "Modal web endpoints",
        "modal_cross_app_lookup": "Modal cross-app lookups (app, function)", "modal_schedules": "Modal schedules",
        "modal_volumes_secrets": "Modal volumes / secrets / bucket mounts", "presign_or_upload_url": "Upload URL / presign call sites",
        "stripe_webhook_events": "Billing webhook event names",
    }
    for k, title in titles.items():
        items = out["entry_points"].get(k)
        if not items:
            continue
        L += ["", f"## {title}"]
        for it in items:
            L.append(f"- {it['file']}:{it['line']}  {' · '.join(it['match'])}")
    if out["modal_invocation_count"]:
        L += ["", f"Modal `.spawn/.remote` call sites: {out['modal_invocation_count']} (grep for them when tracing who triggers which function)"]
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
