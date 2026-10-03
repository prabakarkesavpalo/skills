---
name: hermes-dashboard-access
description: Get into the Hermes web dashboard (Kanban page) and know what is and is not possible. Use when asked to open, log in to or screenshot the Hermes dashboard.
---

# Hermes dashboard access

- Start: `hermes dashboard --no-open --port 9119`; stop: `hermes dashboard --stop`; list: `hermes dashboard --status`.
- There is no sign-up. Username and password come from `HERMES_DASHBOARD_BASIC_AUTH_USERNAME` plus `..._PASSWORD` or `..._PASSWORD_HASH`, and `..._SECRET`, in `~/.hermes/.env`. The alternative is OAuth through `hermes dashboard register`.
- Values in `~/.hermes/.env` override the process environment, so passing different credentials on the command line does not work when the file already defines them. `--isolated` does not change this.
- `/api/status` shows `auth_required` and `auth_providers` without logging in.
- Never read or edit `~/.hermes/.env` yourself. Ask the user to sign in, to send a throwaway login, or to swap one in themselves (back up the file, add a plaintext `..._PASSWORD`, restore afterwards).
- If the dashboard is unavailable, render the board from `hermes kanban list --json` into an HTML page and screenshot that with headless Chrome (`--headless=new --screenshot=out.png --window-size=1400,900`). Label it as a drawing of the data, not the dashboard.
