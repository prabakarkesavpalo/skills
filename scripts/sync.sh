#!/usr/bin/env bash
# Sync skills between this repo (skills/) and ~/.claude/skills.
# Usage: scripts/sync.sh pull|push [--apply]
#   pull  repo -> ~/.claude/skills   (install on a new machine)
#   push  ~/.claude/skills -> repo   (capture local edits, then git commit)
# Dry-run unless --apply. Only touches skills that already exist on the source side.
set -eu
HERE="$(cd "$(dirname "$0")/.." && pwd)"
REPO="$HERE/skills"
LOCAL="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
dir="${1:-}"; apply=0
[ "${2:-}" = "--apply" ] && apply=1
case "$dir" in
  pull) src="$REPO"; dst="$LOCAL" ;;
  push) src="$LOCAL"; dst="$REPO" ;;
  *) echo "usage: $0 pull|push [--apply]" >&2; exit 2 ;;
esac
mkdir -p "$dst"
for d in "$REPO"/*/; do
  name="$(basename "$d")"
  [ -f "$src/$name/SKILL.md" ] || continue
  if [ -f "$dst/$name/SKILL.md" ] && cmp -s "$src/$name/SKILL.md" "$dst/$name/SKILL.md"; then
    echo "same     $name"; continue
  fi
  if [ "$apply" = 1 ]; then
    mkdir -p "$dst/$name"; cp -R "$src/$name/." "$dst/$name/"; echo "copied   $name"
  else
    echo "would copy $name ($dir)"
  fi
done
[ "$apply" = 1 ] || echo "(dry run; add --apply)"
