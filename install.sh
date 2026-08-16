#!/usr/bin/env bash
# install.sh — Install Claude Code Starter Kit into a new project
#
# Usage (human):
#   bash install.sh                                        # interactive prompts
#   bash install.sh MyOS ~/my-os "Jane Smith"              # positional args
#
# Usage (Claude / non-interactive):
#   bash install.sh --non-interactive MyOS ~/my-os "Jane Smith"
#   bash install.sh --print-plan MyOS ~/my-os "Jane Smith" # dry-run, no writes
#
# Flags:
#   --non-interactive   Skip all prompts. Requires PROJECT_NAME, PROJECT_PATH,
#                       USER_NAME as positional args (after the flag).
#   --print-plan        Print what would be installed and exit. No files written.

set -e

# ── Dependency check ──────────────────────────────────────────────────────────
if ! command -v jq &>/dev/null; then
  echo "ERROR: jq is required. Install with: brew install jq"
  exit 1
fi

TEMPLATES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NON_INTERACTIVE=false
PRINT_PLAN=false
UPGRADE_MODE=false

# ── Parse flags ───────────────────────────────────────────────────────────────

POSITIONAL=()
for arg in "$@"; do
  case "$arg" in
    --non-interactive) NON_INTERACTIVE=true ;;
    --print-plan)      PRINT_PLAN=true; NON_INTERACTIVE=true ;;
    --upgrade)         UPGRADE_MODE=true ;;
    *) POSITIONAL+=("$arg") ;;
  esac
done
set -- "${POSITIONAL[@]}"

# ── Upgrade mode: early-exit before project info collection ──────────────────

merge_settings() {
  local template_settings="$1"
  local project_settings="$2"
  local backup="${project_settings}.backup-$(date +%Y%m%d)"

  # Backup existing
  trap 'rm -f "${project_settings}.tmp"' ERR
  cp "$project_settings" "$backup"
  echo "  ✓ Backed up settings.json → $(basename "$backup")"

  # Merge: union permissions.allow, append missing hook groups by command basename
  jq -s '
    .[0] as $user | .[1] as $tmpl |
    ($user.permissions.allow + $tmpl.permissions.allow | unique) as $merged_allow |
    reduce ($tmpl.hooks // {} | to_entries[]) as $entry (
      $user;
      .hooks[$entry.key] = (
        ($user.hooks[$entry.key] // []) +
        ($entry.value | map(
          . as $tmpl_group |
          ($user.hooks[$entry.key] // []) |
          map(.hooks // [] | map(.command | split("/") | last)) | flatten as $user_basenames |
          $tmpl_group |
          select(
            (.hooks // [] | map(.command | split("/") | last) | any(. as $b | $user_basenames | any(. == $b))) | not
          )
        ))
      )
    ) |
    .permissions.allow = $merged_allow
  ' "$project_settings" "$template_settings" > "${project_settings}.tmp"

  mv "${project_settings}.tmp" "$project_settings"
  echo "  ✓ Merged settings.json (backup kept at $(basename "$backup"))"
}

run_upgrade() {
  local project_path="$1"

  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "UPGRADE MODE"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

  if [[ ! -f "$project_path/KIT_VERSION" ]]; then
    echo "  ⚠️  No KIT_VERSION found — this may be a very old install or a manual setup."
    echo "  Proceeding with upgrade anyway."
  else
    local installed_version
    installed_version=$(cat "$project_path/KIT_VERSION")
    local current_version
    current_version=$(cat "$TEMPLATES_DIR/KIT_VERSION")
    echo "  Installed: $installed_version"
    echo "  Current:   $current_version"
  fi

  echo ""
  echo "Upgrading hooks..."
  cp "$TEMPLATES_DIR/hooks/"*.py "$project_path/.claude/hooks/" 2>/dev/null || true
  chmod +x "$project_path/.claude/hooks/"*.py 2>/dev/null || true
  echo "  ✓ Hooks updated"

  echo "Upgrading commands..."
  cp "$TEMPLATES_DIR/commands/"*.md "$project_path/.claude/commands/" 2>/dev/null || true
  echo "  ✓ Commands updated"

  echo "Upgrading scripts..."
  cp "$TEMPLATES_DIR/scripts/"*.py "$project_path/.claude/scripts/" 2>/dev/null || true
  cp "$TEMPLATES_DIR/scripts/"*.sh "$project_path/.claude/scripts/" 2>/dev/null || true
  echo "  ✓ Scripts updated"

  echo "Merging settings.json..."
  local template_settings="$TEMPLATES_DIR/config/settings.json"
  local project_settings="$project_path/.claude/settings.json"
  if [[ -f "$project_settings" ]] && [[ -f "$template_settings" ]]; then
    local tmp_template
    tmp_template=$(mktemp)
    cp "$template_settings" "$tmp_template"
    sed -i.bak "s|{{PROJECT_PATH}}|$project_path|g" "$tmp_template"
    merge_settings "$tmp_template" "$project_settings"
    rm -f "$tmp_template" "${tmp_template}.bak"
  else
    echo "  ⚠️  settings.json not found in project — skipping merge"
  fi

  echo "Updating KIT_VERSION..."
  cp "$TEMPLATES_DIR/KIT_VERSION" "$project_path/KIT_VERSION"
  echo "  ✓ KIT_VERSION updated"

  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "UPGRADE COMPLETE"
  echo "Next: run 'bash score-starter-kit.sh' to verify your installation"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

if [[ "$UPGRADE_MODE" == true ]]; then
  if [[ -n "${1:-}" ]]; then
    UPGRADE_TARGET="$1"
  else
    read -rp "Path to existing project to upgrade: " UPGRADE_TARGET
  fi
  UPGRADE_TARGET="${UPGRADE_TARGET/#\~/$HOME}"
  if [[ ! -d "$UPGRADE_TARGET/.claude" ]]; then
    echo "ERROR: '$UPGRADE_TARGET' does not look like a Claude Code Starter Kit project (no .claude/ directory)"
    exit 1
  fi
  run_upgrade "$UPGRADE_TARGET"
  exit 0
fi

# ── 1. Collect project info ───────────────────────────────────────────────────

if [[ -n "${1:-}" ]]; then
  PROJECT_NAME="$1"
elif [[ "$NON_INTERACTIVE" == true ]]; then
  echo "ERROR: --non-interactive requires PROJECT_NAME as first positional arg."
  echo "  Example: bash install.sh --non-interactive MyOS ~/my-os \"Jane Smith\""
  exit 1
else
  read -rp "Project name (e.g. my-project): " PROJECT_NAME
fi

if [[ -n "${2:-}" ]]; then
  PROJECT_PATH="$2"
elif [[ "$NON_INTERACTIVE" == true ]]; then
  echo "ERROR: --non-interactive requires PROJECT_PATH as second positional arg."
  echo "  Example: bash install.sh --non-interactive MyOS ~/my-os \"Jane Smith\""
  exit 1
else
  read -rp "Project path (absolute, e.g. /Users/you/my-project): " PROJECT_PATH
fi

if [[ -n "${3:-}" ]]; then
  USER_NAME="$3"
elif [[ "$NON_INTERACTIVE" == true ]]; then
  echo "ERROR: --non-interactive requires USER_NAME as third positional arg."
  echo "  Example: bash install.sh --non-interactive MyOS ~/my-os \"Jane Smith\""
  exit 1
else
  read -rp "Your name (e.g. Jane Smith): " USER_NAME
fi

if [[ -z "$PROJECT_NAME" || -z "$PROJECT_PATH" || -z "$USER_NAME" ]]; then
  echo "ERROR: PROJECT_NAME, PROJECT_PATH, and USER_NAME are required."
  exit 1
fi

# ── Print plan and exit if --print-plan ──────────────────────────────────────

if [[ "$PRINT_PLAN" == true ]]; then
  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "INSTALL PLAN (dry-run — no files written)"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "  Project name : $PROJECT_NAME"
  echo "  Project path : $PROJECT_PATH"
  echo "  User name    : $USER_NAME"
  echo "  Templates    : $TEMPLATES_DIR"
  echo ""
  echo "Would create directories:"
  echo "  $PROJECT_PATH/.claude/{commands,hooks,agents,rules,memory,scratch,status,sessions,scripts,tests}"
  echo "  $PROJECT_PATH/knowledge/{wiki,claude-ops,projects}"
  echo ""
  echo "Would copy and patch:"
  echo "  commands/*.md  hooks/*.py  agents/*.md  rules/*.md  scripts/*.py  scripts/*.sh  tests/fixtures/*.json"
  echo "  .claude/settings.json  infra-config.json  CLAUDE.md  REPO_MAP.md  SETUP_PHASES.md"
  echo "  weekly-health-checklist.md  README.md  score-starter-kit.sh"
  echo ""
  echo "Would bootstrap memory files:"
  echo "  .claude/memory/STATUS.md"
  echo "  .claude/memory/goals.md"
  echo "  .claude/status/SESSION_HANDOFF.md"
  echo "  .claude/status/CURRENT_STATE.md"
  echo "  .claude/scratch/AGENT_STATE.json"
  echo "  .claude/status/MILESTONE_REGISTRY.json"
  echo "  knowledge/wiki/claude-ops.md"
  echo "  knowledge/wiki/projects.md"
  echo "  knowledge/claude-ops/deferred-triggers.md"
  echo "  knowledge/claude-ops/PROJECT_REGISTRY.md"
  echo ""
  echo "Run without --print-plan to execute."
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  exit 0
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
  ".claude/scripts"
  ".claude/tests"
  ".claude/tests/fixtures"
  ".claude/tests/results"
  "knowledge"
  "knowledge/wiki"
  "knowledge/claude-ops"
  "knowledge/projects"
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

# ── 8. Copy scripts/ ──────────────────────────────────────────────────────────

SCRIPTS_SRC="$TEMPLATES_DIR/scripts"
SCRIPTS_DST="$PROJECT_PATH/.claude/scripts"

if [[ -d "$SCRIPTS_SRC" ]]; then
  for src in "$SCRIPTS_SRC"/*.py "$SCRIPTS_SRC"/*.sh; do
    [[ -f "$src" ]] || continue
    fname="$(basename "$src")"
    dst="$SCRIPTS_DST/$fname"
    cp "$src" "$dst"
    chmod +x "$dst"
    echo "  ✓ scripts/$fname"
  done
fi

# ── 8b. Copy test fixtures ───────────────────────────────────────────────────

FIXTURES_SRC="$TEMPLATES_DIR/.claude/tests/fixtures"
FIXTURES_DST="$PROJECT_PATH/.claude/tests/fixtures"

if [[ -d "$FIXTURES_SRC" ]]; then
  for src in "$FIXTURES_SRC"/*.json; do
    [[ -f "$src" ]] || continue
    fname="$(basename "$src")"
    dst="$FIXTURES_DST/$fname"
    cp "$src" "$dst"
    replace_placeholders "$dst"
    echo "  ✓ tests/fixtures/$fname"
  done
fi

# ── 9. Copy and patch config files ────────────────────────────────────────────

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

# KIT_VERSION → project root (enables upgrade detection)
if [[ -f "$TEMPLATES_DIR/KIT_VERSION" ]]; then
  cp "$TEMPLATES_DIR/KIT_VERSION" "$PROJECT_PATH/KIT_VERSION"
  echo "  ✓ KIT_VERSION"
fi

# ── 9. Copy CLAUDE.md and REPO_MAP.md ────────────────────────────────────────

if [[ -f "$TEMPLATES_DIR/CLAUDE.md" ]]; then
  dst="$PROJECT_PATH/CLAUDE.md"
  cp "$TEMPLATES_DIR/CLAUDE.md" "$dst"
  replace_placeholders "$dst"
  echo "  ✓ CLAUDE.md"
fi

if [[ -f "$TEMPLATES_DIR/REPO_MAP.md" ]]; then
  dst="$PROJECT_PATH/REPO_MAP.md"
  cp "$TEMPLATES_DIR/REPO_MAP.md" "$dst"
  replace_placeholders "$dst"
  echo "  ✓ REPO_MAP.md"
fi

if [[ -f "$TEMPLATES_DIR/SETUP_PHASES.md" ]]; then
  dst="$PROJECT_PATH/SETUP_PHASES.md"
  cp "$TEMPLATES_DIR/SETUP_PHASES.md" "$dst"
  replace_placeholders "$dst"
  echo "  ✓ SETUP_PHASES.md"
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

if [[ -f "$TEMPLATES_DIR/CLAUDE_ONBOARDING.md" ]]; then
  dst="$PROJECT_PATH/CLAUDE_ONBOARDING.md"
  cp "$TEMPLATES_DIR/CLAUDE_ONBOARDING.md" "$dst"
  replace_placeholders "$dst"
  echo "  ✓ CLAUDE_ONBOARDING.md"
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

bootstrap_file "$PROJECT_PATH/knowledge/wiki/claude-ops.md" "# Claude Ops Wiki — ${PROJECT_NAME}
last_updated: ${TODAY}

## System Notes

Add notes about your Claude Code setup here — what works, what to avoid, decisions made.

## Hook Inventory

| Hook | Event | Purpose |
|------|-------|---------|
| session-start.py | SessionStart | Loads memory, warns on deadlines |
| memory-validator.py | PreToolUse | Guards wrong-path writes |
| stale-template-check.py | PreCompact | Detects template drift |

## Commands Added

| Command | Purpose |
|---------|---------|
| /start | Morning briefing |
| /work | Task pipeline |
| /checkpoint | Session close |
| /recall | Search past sessions |
| /query | Search wiki |
"

bootstrap_file "$PROJECT_PATH/knowledge/wiki/projects.md" "# Projects Wiki — ${PROJECT_NAME}
last_updated: ${TODAY}

## Active Projects

| Project | Status | Next action |
|---------|--------|-------------|
| (add your projects here) | — | — |

## Decisions Log

| Decision | Date | Outcome |
|----------|------|---------|
| (none yet) | — | — |
"

bootstrap_file "$PROJECT_PATH/knowledge/claude-ops/deferred-triggers.md" "# Deferred Triggers — ${PROJECT_NAME}
last_updated: ${TODAY}

Tracks items that are waiting on a condition before action is taken.

## Active Deferrals

| ID | Item | Type | Condition | Status | Source |
|----|------|------|-----------|--------|--------|
| D-P01 | Install graphify for knowledge graph queries | MANUAL | When ready to explore codebase relationships | waiting | README |
| D-P02 | Install last30days plugin for /research command | MANUAL | When ready for market/signal research | waiting | README |
| D-P03 | Install autoresearch plugin for scheduled research loops | MANUAL | When ready for automated research | waiting | README |

## Completed Deferrals

(none yet)

---

## Plugin Install Commands (when ready)

**graphify** — knowledge graph over your codebase:
\`\`\`bash
npm install -g graphify-cli
graphify init .
\`\`\`

**last30days** — Reddit/X/YouTube signal research:
\`\`\`bash
claude plugins install mvanhorn/last30days-skill
\`\`\`

**autoresearch** — scheduled research loops:
\`\`\`bash
claude plugins install uditgoenka/autoresearch
\`\`\`
"

bootstrap_file "$PROJECT_PATH/knowledge/claude-ops/PROJECT_REGISTRY.md" "# Project Registry — ${PROJECT_NAME}
last_updated: ${TODAY}

Tracks active projects. Use /pivot project:<name> to load context.

## Registry

| Name | Type | Status | Gate condition |
|------|------|--------|----------------|
| (add projects here) | — | NOT STARTED | — |

## How to add a project

1. Create \`~/projects/<name>/CONTEXT.md\` with phase, status, key people
2. Add a row to this registry
3. Run: /pivot project:<name>
"

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
