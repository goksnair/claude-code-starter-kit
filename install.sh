#!/usr/bin/env bash
# install.sh — Install Claude Code Starter Kit into a new project
# Usage: ./install.sh [PROJECT_NAME] [PROJECT_PATH]
# Or run interactively (no args) to be prompted.

set -e

TEMPLATES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── 1. Collect project info ───────────────────────────────────────────────────

if [[ -n "$1" ]]; then
  PROJECT_NAME="$1"
else
  read -rp "Project name (e.g. my-project): " PROJECT_NAME
fi

if [[ -n "$2" ]]; then
  PROJECT_PATH="$2"
else
  read -rp "Project path (absolute, e.g. /Users/you/my-project): " PROJECT_PATH
fi

if [[ -n "$3" ]]; then
  USER_NAME="$3"
else
  read -rp "Your name (e.g. Jane Smith): " USER_NAME
fi

if [[ -z "$PROJECT_NAME" || -z "$PROJECT_PATH" || -z "$USER_NAME" ]]; then
  echo "ERROR: PROJECT_NAME, PROJECT_PATH, and USER_NAME are required."
  exit 1
fi

echo ""
echo "Installing Claude Code Starter Kit"
echo "  Project name : $PROJECT_NAME"
echo "  Project path : $PROJECT_PATH"
echo "  User name    : $USER_NAME"
echo ""

# ── 2. Create directory structure ─────────────────────────────────────────────

dirs=(
  ".claude/commands"
  ".claude/hooks"
  ".claude/agents"
  ".claude/rules"
  ".claude/memory"
  ".claude/scratch"
  ".claude/status"
  ".claude/sessions"
  "knowledge"
)

for d in "${dirs[@]}"; do
  mkdir -p "$PROJECT_PATH/$d"
done
echo "✓ Directory structure created"

# ── 3. Replace placeholders in a file ─────────────────────────────────────────

replace_placeholders() {
  local file="$1"
  local tmp="${file}.tmp"
  sed \
    -e "s|{{PROJECT_NAME}}|${PROJECT_NAME}|g" \
    -e "s|{{PROJECT_PATH}}|${PROJECT_PATH}|g" \
    -e "s|{{USER_NAME}}|${USER_NAME}|g" \
    -e "s|{{DATE}}|${TODAY}|g" \
    -e "s|{{VAULT_PATH}}|${HOME}/.vault|g" \
    "$file" > "$tmp" && mv "$tmp" "$file"
}

# ── 4. Copy and patch commands/ ───────────────────────────────────────────────

COMMANDS_SRC="$TEMPLATES_DIR/commands"
COMMANDS_DST="$PROJECT_PATH/.claude/commands"

if [[ -d "$COMMANDS_SRC" ]]; then
  for src in "$COMMANDS_SRC"/*.md; do
    fname="$(basename "$src")"
    dst="$COMMANDS_DST/$fname"
    cp "$src" "$dst"
    replace_placeholders "$dst"
    echo "  ✓ commands/$fname"
  done
fi

# ── 5. Copy and patch hooks/ ──────────────────────────────────────────────────

HOOKS_SRC="$TEMPLATES_DIR/hooks"
HOOKS_DST="$PROJECT_PATH/.claude/hooks"

if [[ -d "$HOOKS_SRC" ]]; then
  for src in "$HOOKS_SRC"/*.py; do
    [[ -f "$src" ]] || continue
    fname="$(basename "$src")"
    dst="$HOOKS_DST/$fname"
    cp "$src" "$dst"
    replace_placeholders "$dst"
    chmod +x "$dst"
    echo "  ✓ hooks/$fname"
  done
fi

# ── 6. Copy and patch agents/ ─────────────────────────────────────────────────

AGENTS_SRC="$TEMPLATES_DIR/agents"
AGENTS_DST="$PROJECT_PATH/.claude/agents"

if [[ -d "$AGENTS_SRC" ]]; then
  for src in "$AGENTS_SRC"/*.md; do
    [[ -f "$src" ]] || continue
    fname="$(basename "$src")"
    dst="$AGENTS_DST/$fname"
    cp "$src" "$dst"
    replace_placeholders "$dst"
    echo "  ✓ agents/$fname"
  done
fi

# ── 7. Copy and patch rules/ ──────────────────────────────────────────────────

RULES_SRC="$TEMPLATES_DIR/rules"
RULES_DST="$PROJECT_PATH/.claude/rules"

if [[ -d "$RULES_SRC" ]]; then
  for src in "$RULES_SRC"/*.md; do
    [[ -f "$src" ]] || continue
    fname="$(basename "$src")"
    dst="$RULES_DST/$fname"
    cp "$src" "$dst"
    replace_placeholders "$dst"
    echo "  ✓ rules/$fname"
  done
fi

# ── 8. Copy and patch config files ────────────────────────────────────────────

CONFIG_SRC="$TEMPLATES_DIR/config"

if [[ -d "$CONFIG_SRC" ]]; then
  # settings.json → .claude/settings.json
  if [[ -f "$CONFIG_SRC/settings.json" ]]; then
    dst="$PROJECT_PATH/.claude/settings.json"
    cp "$CONFIG_SRC/settings.json" "$dst"
    replace_placeholders "$dst"
    echo "  ✓ .claude/settings.json"
  fi

  # infra-config.json → project root
  if [[ -f "$CONFIG_SRC/infra-config.json" ]]; then
    dst="$PROJECT_PATH/infra-config.json"
    cp "$CONFIG_SRC/infra-config.json" "$dst"
    replace_placeholders "$dst"
    echo "  ✓ infra-config.json"
  fi
fi

# ── 9. Copy CLAUDE.md ─────────────────────────────────────────────────────────

if [[ -f "$TEMPLATES_DIR/CLAUDE.md" ]]; then
  dst="$PROJECT_PATH/CLAUDE.md"
  cp "$TEMPLATES_DIR/CLAUDE.md" "$dst"
  replace_placeholders "$dst"
  echo "  ✓ CLAUDE.md"
fi

# ── 10. Copy weekly health checklist ─────────────────────────────────────────

if [[ -f "$TEMPLATES_DIR/weekly-health-checklist.md" ]]; then
  dst="$PROJECT_PATH/weekly-health-checklist.md"
  cp "$TEMPLATES_DIR/weekly-health-checklist.md" "$dst"
  replace_placeholders "$dst"
  echo "  ✓ weekly-health-checklist.md"
fi

if [[ -f "$TEMPLATES_DIR/README.md" ]]; then
  dst="$PROJECT_PATH/README.md"
  cp "$TEMPLATES_DIR/README.md" "$dst"
  echo "  ✓ README.md"
fi

if [[ -f "$TEMPLATES_DIR/score-starter-kit.sh" ]]; then
  dst="$PROJECT_PATH/score-starter-kit.sh"
  cp "$TEMPLATES_DIR/score-starter-kit.sh" "$dst"
  chmod +x "$dst"
  echo "  ✓ score-starter-kit.sh"
fi

# ── 11. Bootstrap memory files ────────────────────────────────────────────────

bootstrap_file() {
  local path="$1"
  local content="$2"
  if [[ ! -f "$path" ]]; then
    echo "$content" > "$path"
    echo "  ✓ $(basename "$path") (bootstrapped)"
  else
    echo "  ↳ $(basename "$path") already exists — skipped"
  fi
}

TODAY=$(date +%Y-%m-%d)

bootstrap_file "$PROJECT_PATH/.claude/memory/STATUS.md" "# ${PROJECT_NAME} — Status
last_updated: ${TODAY}

## Active Decisions

| Decision | Deadline | Status |
|----------|----------|--------|
| (none yet) | — | — |

## Current Blockers

(none)
"

bootstrap_file "$PROJECT_PATH/.claude/memory/goals.md" "# ${PROJECT_NAME} — Goals
last_updated: ${TODAY}

## Primary Goals

1. (fill in)

## Milestones

| Milestone | Target Date | Status |
|-----------|-------------|--------|
| (none yet) | — | — |
"

bootstrap_file "$PROJECT_PATH/.claude/status/SESSION_HANDOFF.md" "# SESSION_HANDOFF — ${PROJECT_NAME}
**Last updated**: ${TODAY}
**Active work**: project initialized

## IMMEDIATE NEXT TASK

Set up memory files and run /start to begin.

## OPEN ITEMS

| Item | Priority | Status |
|------|----------|--------|
| Initialize STATUS.md | HIGH | open |
"

bootstrap_file "$PROJECT_PATH/.claude/status/CURRENT_STATE.md" "# CURRENT_STATE — ${PROJECT_NAME}
**Last Updated**: ${TODAY}
**Status**: initialized

## Intelligence Summary
**As of**: ${TODAY}
**Active decisions**: none yet
**Top open items**: see SESSION_HANDOFF.md

## Completed Work

### ${TODAY}
- Project initialized from Claude Code Starter Kit
"

bootstrap_file "$PROJECT_PATH/.claude/scratch/AGENT_STATE.json" '{
  "_schema_version": "2.0",
  "session_id": null,
  "active_task": {
    "agent": null,
    "status": "idle",
    "started_at": null
  },
  "completed_tasks": []
}'

bootstrap_file "$PROJECT_PATH/.claude/status/MILESTONE_REGISTRY.json" "{
  \"project\": \"${PROJECT_NAME}\",
  \"created\": \"${TODAY}\",
  \"milestones\": []
}"

# ── 12. Summary ───────────────────────────────────────────────────────────────

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "INSTALLATION COMPLETE — ${PROJECT_NAME}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Next steps:"
echo "  1. Edit $PROJECT_PATH/CLAUDE.md — review and customize"
echo "  2. Edit $PROJECT_PATH/.claude/memory/STATUS.md — fill in active decisions"
echo "  3. Edit $PROJECT_PATH/.claude/memory/goals.md — fill in project goals"
echo "  4. Review $PROJECT_PATH/.claude/settings.json — enable/disable hooks as needed"
echo "  5. Open Claude Code in $PROJECT_PATH and run /start"
echo ""
echo "Usage tip: bash install.sh [PROJECT_NAME] [PROJECT_PATH] [USER_NAME]"
echo ""
echo "Installed to: $PROJECT_PATH"
echo "Templates from: $TEMPLATES_DIR"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
