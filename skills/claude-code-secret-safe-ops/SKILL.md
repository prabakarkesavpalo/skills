---
name: claude-code-secret-safe-ops
description: Do local setup work around credentials and destructive cleanup without tripping auto-mode safety blocks, and report honestly when blocked. Use when a task needs credentials, ~/.hermes/.env, auth files, config reads or rm -rf of a .git directory.
---

# Secret-safe operations

Auto mode blocks credential reads, copies, writes to secret stores, and irreversible deletes. Do not work around a block. Plan around it:

- Never read or print `auth.json`, `.env`, or a global config that may hold keys. Use the tool's own getters (`hermes -p <bot> config get model`) and list only the names of settings (`grep -o '^NAME_[A-Z_]*'`).
- Make credential sharing an explicit opt-in script flag (`--share-auth`) that the user runs, not something you run.
- Do not edit secret files. Offer the user an exact edit with a backup and a restore step.
- For destructive cleanup (a stray `.git`, `rm -rf`), first inspect what it holds (`git log`, `git status`), make a tarball backup in `/tmp`, then delete when the user has clearly asked. If still blocked, hand the user the exact commands.
- When blocked, finish everything else, then state plainly: what you tried, why it matters, and the options (user does it, user sends a throwaway, user adds a permission rule).
- Do all verifiable work first; report which parts are unverified.
