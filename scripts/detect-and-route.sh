#!/usr/bin/env bash
# detect-and-route.sh — Detect project setup state and print the correct upgrade route.
#
# Usage:
#   bash detect-and-route.sh [project-path]   # defaults to current directory
#
# Routes:
#   fresh-install        — no .claude/ directory
#   pre-existing-setup   — .claude/ present, no KIT_VERSION
#   standard-upgrade     — KIT_VERSION present, memory not yet configured
#   configured           — KIT_VERSION present, memory populated and handoff clear

set -e

PROJECT="${1:-$(pwd)}"
PROJECT="${PROJECT/#\~/$HOME}"

HAS_CLAUDE_DIR=false
HAS_KIT_VERSION=false
GOALS_POPULATED=false
HANDOFF_INITIALIZED=false

[[ -d "$PROJECT/.claude" ]] && HAS_CLAUDE_DIR=true
[[ -f "$PROJECT/KIT_VERSION" ]] && HAS_KIT_VERSION=true
[[ -f "$PROJECT/.claude/memory/goals.md" ]] && ! grep -q "(fill in)" "$PROJECT/.claude/memory/goals.md" && GOALS_POPULATED=true
[[ -f "$PROJECT/.claude/status/SESSION_HANDOFF.md" ]] && grep -q "project initialized" "$PROJECT/.claude/status/SESSION_HANDOFF.md" && HANDOFF_INITIALIZED=true

echo ""
echo "Project: $PROJECT"
echo "─────────────────────────────────────"

if [[ "$HAS_CLAUDE_DIR" == false ]]; then
  echo "ROUTE: fresh-install"
  echo "No .claude/ directory found."
  echo "Run: bash install.sh"

elif [[ "$HAS_KIT_VERSION" == false ]]; then
  echo "ROUTE: pre-existing-setup"
  echo "Existing setup detected (no KIT_VERSION)."
  echo "Run: bash install.sh --upgrade --selective $PROJECT"

elif [[ "$GOALS_POPULATED" == false || "$HANDOFF_INITIALIZED" == true ]]; then
  echo "ROUTE: standard-upgrade"
  echo "Kit install detected. Memory files not yet configured."
  echo "Run: bash install.sh --upgrade $PROJECT"

else
  echo "ROUTE: configured"
  echo "Setup looks complete."
  echo "Run /start to begin your session."
fi

echo "─────────────────────────────────────"
echo ""
