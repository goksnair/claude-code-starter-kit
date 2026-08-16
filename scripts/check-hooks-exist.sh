#!/usr/bin/env bash
set -euo pipefail

if [[ -n "${GITHUB_WORKSPACE:-}" ]]; then
  REPO_ROOT="$GITHUB_WORKSPACE"
else
  REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fi

SETTINGS="$REPO_ROOT/.claude/settings.json"

if [[ ! -f "$SETTINGS" ]]; then
  echo "settings.json not found at $SETTINGS"
  exit 1
fi

HOOK_LIST=$(python3 -c "
import json, sys
with open('$SETTINGS') as f:
    s = json.load(f)
seen = set()
for entries in (s.get('hooks') or {}).values():
    for entry in entries:
        for h in entry.get('hooks', []):
            for tok in (h.get('command','')).split():
                if tok.endswith('.py') or tok.endswith('.sh'):
                    seen.add(tok)
for h in sorted(seen):
    print(h)
")

missing=""
not_exec=""
count=0
while IFS= read -r hook; do
  [[ -z "$hook" ]] && continue
  count=$((count + 1))
  if [[ "$hook" == *".claude/hooks/"* ]]; then
    tail="${hook#*.claude/hooks/}"
    resolved="$REPO_ROOT/.claude/hooks/$tail"
  else
    resolved="$hook"
  fi
  if [[ ! -f "$resolved" ]]; then
    missing="$missing  $hook"$'\n'
  elif [[ ! -x "$resolved" ]]; then
    not_exec="$not_exec  $hook"$'\n'
  fi
done <<< "$HOOK_LIST"

echo "Checked $count hook path(s) from settings.json"

if [[ -n "$missing" ]]; then
  echo "MISSING:"
  printf "%s" "$missing"
fi

if [[ -n "$not_exec" ]]; then
  echo "NOT EXECUTABLE:"
  printf "%s" "$not_exec"
fi

if [[ -z "$missing" && -z "$not_exec" ]]; then
  echo "All hooks present and executable"
  exit 0
fi
exit 1
