---
name: portable-macos-shell
description: Write shell scripts and one-liners that run on macOS bash 3.2 and zsh. Use when writing gate scripts, installers or sed/array code that must work on a Mac, or when a script fails with declare -A, mapfile, sed or word-splitting errors.
---

# Portable shell on macOS

- No `declare -A` and no `mapfile` in bash 3.2. Use scalar variables, `case`, or a `while read` loop that builds the list.
- `sed -i ''` (empty suffix) on macOS; GNU `sed -i` fails with a confusing 'undefined label'.
- zsh does not split unquoted variables, so `for f in $files` runs once with a newline-joined string. Use `grep ... | while read -r f; do ...; done`.
- No `timeout` on macOS; run in the background and kill, or use a loop with a deadline.
- Dry-run by default for anything that changes state: a `run()` helper that prints with `printf '%q'` unless `--apply`.
- After a command chain with `;`, a later step runs even if an earlier one failed. Use `&&` when a commit depends on a passing test.
- Check with `bash -n script.sh` and run pytest or shellcheck-style tests that assert flags like `--apply` exist.
- Do not use `sleep` in a chain to wait; use a background run or a poll loop with a deadline.
