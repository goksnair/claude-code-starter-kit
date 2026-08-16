#!/usr/bin/env bash
# score-starter-kit.sh — Benchmark the Claude Code Starter Kit install
# Usage: bash score-starter-kit.sh
# Run from the templates root (where install.sh lives) — not from an installed project copy.

set -euo pipefail

JSON_MODE=false
for arg in "$@"; do
  case "$arg" in
    --json) JSON_MODE=true ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
INSTALL_PATH="/tmp/sk-score-$(date +%Y%m%d-%H%M%S)"
INSTALL_SCRIPT="$SCRIPT_DIR/install.sh"
SCORECARD="$(pwd)/.claude/scratch/starter-kit-benchmark-scorecard.md"

# Dimension scores and evidence
declare -a DIM_SCORES
declare -a DIM_EVIDENCE
declare -a DIM_NAMES

# ── Helper ────────────────────────────────────────────────────────────────────

record() {
  local idx=$1 score=$2 evidence=$3
  DIM_SCORES[$idx]=$score
  DIM_EVIDENCE[$idx]="$evidence"
}

# ── DIM 1: Install success ────────────────────────────────────────────────────

DIM_NAMES[1]="Install success"
set +e
bash "$INSTALL_SCRIPT" "ScoreTest" "$INSTALL_PATH" "Test User" > /tmp/sk-install.log 2>&1
INSTALL_EXIT=$?
set -e

if [[ $INSTALL_EXIT -eq 0 ]]; then
  record 1 10 "exit 0"
else
  record 1 0 "exit $INSTALL_EXIT"
fi

# ── DIM 2: Placeholder substitution ──────────────────────────────────────────

DIM_NAMES[2]="Placeholder substitution"
set +e
# Only check substitution-target files: hooks, memory, settings.json, CLAUDE.md
# Scripts/docs/infra-config intentionally contain {{}} as literal syntax examples
UNRESOLVED=$(grep -rn '{{PROJECT_PATH}}\|{{PROJECT_NAME}}\|{{USER_NAME}}\|{{DATE}}' \
  "$INSTALL_PATH/.claude/hooks/" \
  "$INSTALL_PATH/.claude/memory/" \
  "$INSTALL_PATH/.claude/settings.json" \
  "$INSTALL_PATH/CLAUDE.md" \
  2>/dev/null \
  | grep -v '\.pyc' \
  | wc -l | tr -d ' ')
set -e

if [[ "$UNRESOLVED" -eq 0 ]]; then
  record 2 10 "0 unresolved {{}} tokens"
else
  record 2 6 "$UNRESOLVED unresolved {{}} token(s) found"
fi

# ── DIM 3: Hook file completeness ─────────────────────────────────────────────

DIM_NAMES[3]="Hook file completeness"
SETTINGS="$INSTALL_PATH/.claude/settings.json"
set +e
if [[ -f "$SETTINGS" ]]; then
  HOOK_CHECK=$(python3 - "$SETTINGS" "$INSTALL_PATH/.claude/hooks" <<'PY'
import sys, json, os

settings_path = sys.argv[1]
hooks_dir = sys.argv[2]

with open(settings_path) as f:
    data = json.load(f)

hooks_block = data.get("hooks", {})
all_hooks = []

for event, matchers in hooks_block.items():
    for matcher in matchers:
        for hook in matcher.get("hooks", []):
            cmd = hook.get("command", "")
            for part in cmd.split():
                if part.endswith(".py"):
                    fname = os.path.basename(part)
                    all_hooks.append(fname)

total = len(all_hooks)
present = sum(1 for h in all_hooks if os.path.isfile(os.path.join(hooks_dir, h)))
print(f"{present}/{total}")
PY
)
  PRESENT=$(echo "$HOOK_CHECK" | cut -d/ -f1)
  TOTAL=$(echo "$HOOK_CHECK" | cut -d/ -f2)
  if [[ "$TOTAL" -gt 0 ]]; then
    SCORE=$(python3 -c "print(round($PRESENT/$TOTAL * 10))")
  else
    SCORE=0
  fi
  record 3 "$SCORE" "$PRESENT/$TOTAL hook files present"
else
  record 3 0 "settings.json missing"
fi
set -e

# ── DIM 4: Hook runtime ───────────────────────────────────────────────────────

DIM_NAMES[4]="Hook runtime (5 hooks)"
HOOKS_DIR="$INSTALL_PATH/.claude/hooks"
TEST_HOOKS=(
  "session-start.py"
  "bash-tool-guard.py"
  "large-file-guard.py"
  "memory-validator.py"
  "stale-template-check.py"
)

HOOK_FAILURES=0
HOOK_DETAIL=""
for hook in "${TEST_HOOKS[@]}"; do
  HOOK_PATH="$HOOKS_DIR/$hook"
  if [[ -f "$HOOK_PATH" ]]; then
    set +e
    echo '{}' | python3 "$HOOK_PATH" > /tmp/sk-hook-out.txt 2>&1
    EXIT=$?
    set -e
    if [[ $EXIT -ne 0 ]]; then
      HOOK_FAILURES=$((HOOK_FAILURES + 1))
      HOOK_DETAIL="$HOOK_DETAIL $hook(exit $EXIT)"
    fi
  else
    HOOK_FAILURES=$((HOOK_FAILURES + 1))
    HOOK_DETAIL="$HOOK_DETAIL $hook(missing)"
  fi
done

HOOK_SCORE=$((10 - HOOK_FAILURES * 2))
[[ $HOOK_SCORE -lt 0 ]] && HOOK_SCORE=0
if [[ $HOOK_FAILURES -eq 0 ]]; then
  record 4 "$HOOK_SCORE" "all 5 hooks exited 0"
else
  record 4 "$HOOK_SCORE" "$HOOK_FAILURES failure(s):$HOOK_DETAIL"
fi

# ── DIM 5: /work pipeline completeness ───────────────────────────────────────

DIM_NAMES[5]="/work pipeline completeness"
AGENTS_DIR="$INSTALL_PATH/.claude/agents"
set +e
HAS_PE=0; HAS_COORD=0; AGENT_COUNT=0
if [[ -d "$AGENTS_DIR" ]]; then
  [[ -f "$AGENTS_DIR/prompt-engineer.md" ]] && HAS_PE=1
  [[ -f "$AGENTS_DIR/coordinator.md" ]] && HAS_COORD=1
  AGENT_COUNT=$(ls "$AGENTS_DIR"/*.md 2>/dev/null | wc -l | tr -d ' ')
fi
set -e

if [[ $HAS_PE -eq 1 && $HAS_COORD -eq 1 && $AGENT_COUNT -ge 5 ]]; then
  record 5 10 "PE + coordinator + $AGENT_COUNT total agents"
elif [[ $HAS_PE -eq 1 && $HAS_COORD -eq 1 ]]; then
  record 5 7 "PE + coordinator present, only $AGENT_COUNT agents (need 5)"
elif [[ $HAS_PE -eq 1 || $HAS_COORD -eq 1 ]]; then
  record 5 4 "only PE=$HAS_PE coordinator=$HAS_COORD present"
else
  record 5 0 "PE and coordinator both missing"
fi

# ── DIM 6: Memory routing ─────────────────────────────────────────────────────

DIM_NAMES[6]="Memory routing"
MEM_FILES=(
  "$INSTALL_PATH/.claude/memory/STATUS.md"
  "$INSTALL_PATH/.claude/memory/goals.md"
  "$INSTALL_PATH/.claude/status/SESSION_HANDOFF.md"
  "$INSTALL_PATH/.claude/status/CURRENT_STATE.md"
  "$INSTALL_PATH/.claude/scratch/AGENT_STATE.json"
)

MEM_MISSING=0
for f in "${MEM_FILES[@]}"; do
  [[ -f "$f" ]] || MEM_MISSING=$((MEM_MISSING + 1))
done

MEM_SCORE=$((10 - MEM_MISSING * 2))
[[ $MEM_SCORE -lt 0 ]] && MEM_SCORE=0
PRESENT_COUNT=$((5 - MEM_MISSING))
record 6 "$MEM_SCORE" "$PRESENT_COUNT/5 memory files present"

# ── DIM 7: README quality ─────────────────────────────────────────────────────

DIM_NAMES[7]="README quality"
README="$INSTALL_PATH/README.md"
if [[ -f "$README" ]]; then
  LINE_COUNT=$(wc -l < "$README" | tr -d ' ')
  if [[ $LINE_COUNT -gt 300 ]]; then
    # Expected README headings (update these if README structure changes):
    #   HAS_QS: '^## Install' — matches "## Install — Step by Step"
    #   HAS_WI: '^## What.s included' — matches "## What's included"
    #   HAS_CMD: '^## Command list' — matches "## Command list"
    HAS_QS=$(grep -ci '^## Install' "$README" 2>/dev/null || true)
    HAS_WI=$(grep -ci "^## What.s included" "$README" 2>/dev/null || true)
    HAS_CMD=$(grep -ci '^## Command list' "$README" 2>/dev/null || true)
    if [[ "$HAS_QS" -gt 0 && "$HAS_WI" -gt 0 && "$HAS_CMD" -gt 0 ]]; then
      record 7 10 "README.md $LINE_COUNT lines with all required sections"
    else
      record 7 9 "README.md $LINE_COUNT lines, missing required headings"
    fi
  elif [[ $LINE_COUNT -gt 100 ]]; then
    record 7 7 "README.md exists, $LINE_COUNT lines (101-300)"
  else
    record 7 5 "README.md exists but only $LINE_COUNT lines (<=100)"
  fi
else
  record 7 0 "README.md absent"
fi

# ── DIM 8: Cold-user UX ───────────────────────────────────────────────────────

DIM_NAMES[8]="Cold-user UX"
CLAUDE_MD="$INSTALL_PATH/CLAUDE.md"
set +e
if [[ -f "$CLAUDE_MD" ]]; then
  HAS_PLACEHOLDER=$(grep -c '{{PROJECT_NAME}}' "$CLAUDE_MD" 2>/dev/null || true)
  HAS_SESSION_START=$(grep -c '## Session Start' "$CLAUDE_MD" 2>/dev/null || true)
  if [[ "$HAS_PLACEHOLDER" -eq 0 && "$HAS_SESSION_START" -gt 0 ]]; then
    record 8 10 "CLAUDE.md substituted with Session Start section"
  elif [[ "$HAS_PLACEHOLDER" -eq 0 ]]; then
    record 8 9 "CLAUDE.md exists and {{PROJECT_NAME}} is substituted"
  else
    record 8 4 "CLAUDE.md exists but {{PROJECT_NAME}} not substituted"
  fi
else
  record 8 0 "CLAUDE.md absent"
fi
set -e

# ── DIM 9: Error recovery (vault missing) ────────────────────────────────────

DIM_NAMES[9]="Error recovery"
MV_HOOK="$INSTALL_PATH/.claude/hooks/memory-validator.py"
set +e
if [[ -f "$MV_HOOK" ]]; then
  # Temporarily rename vault if it exists
  VAULT_PATH="$HOME/.vault"
  VAULT_TMP=""
  if [[ -d "$VAULT_PATH" ]]; then
    VAULT_TMP="$HOME/.vault-sk-score-tmp"
    mv "$VAULT_PATH" "$VAULT_TMP"
  fi

  MV_OUT=$(echo '{"tool_name":"Write","tool_input":{"file_path":"/tmp/test.md","content":"test"}}' | python3 "$MV_HOOK" 2>&1)
  MV_EXIT=$?

  if [[ -n "$VAULT_TMP" ]]; then
    mv "$VAULT_TMP" "$VAULT_PATH"
  fi

  if [[ $MV_EXIT -eq 0 ]] && echo "$MV_OUT" | grep -qi "vault not found"; then
    record 9 10 "exit 0, output contains 'vault not found'"
  elif [[ $MV_EXIT -eq 0 ]]; then
    record 9 6 "exit 0 but output did not contain 'vault not found'"
  else
    record 9 2 "exit $MV_EXIT — hook errored"
  fi
else
  record 9 0 "memory-validator.py missing"
fi
set -e

# ── DIM 10: Drift detection ───────────────────────────────────────────────────

DIM_NAMES[10]="Drift detection"
STC_HOOK="$INSTALL_PATH/.claude/hooks/stale-template-check.py"
set +e
if [[ -f "$STC_HOOK" ]]; then
  echo '{}' | python3 "$STC_HOOK" > /tmp/sk-stale.txt 2>&1
  STC_EXIT=$?
  if [[ $STC_EXIT -eq 0 ]]; then
    record 10 10 "stale-template-check.py exited 0"
  else
    record 10 0 "stale-template-check.py exited $STC_EXIT"
  fi
else
  record 10 0 "stale-template-check.py missing"
fi
set -e

# ── Scorecard render ──────────────────────────────────────────────────────────

TOTAL=0
for i in $(seq 1 10); do
  TOTAL=$((TOTAL + DIM_SCORES[$i]))
done

render_scorecard() {
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "CLAUDE CODE STARTER KIT — BENCHMARK"
  echo "Install path: $INSTALL_PATH"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  printf " %-2s  %-32s  %-7s  %s\n" "#" "Dimension" "Score" "Evidence"
  echo "────────────────────────────────────────────────────────────────"
  for i in $(seq 1 10); do
    printf " %-2s  %-32s  %2s/10   %s\n" \
      "$i" "${DIM_NAMES[$i]}" "${DIM_SCORES[$i]}" "${DIM_EVIDENCE[$i]}"
  done
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "TOTAL: $TOTAL/100"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

if [[ "$JSON_MODE" == true ]]; then
  PASS_ITEMS=()
  FAIL_ITEMS=()
  WARN_ITEMS=()
  for i in $(seq 1 10); do
    name="${DIM_NAMES[$i]}"
    score="${DIM_SCORES[$i]}"
    if [[ "$score" -eq 10 ]]; then
      PASS_ITEMS+=("$name")
    elif [[ "$score" -ge 5 ]]; then
      WARN_ITEMS+=("$name")
    else
      FAIL_ITEMS+=("$name")
    fi
  done

  json_array() {
    local arr=("$@")
    local out="["
    local first=true
    for item in "${arr[@]}"; do
      if [[ "$first" == true ]]; then
        first=false
      else
        out+=","
      fi
      out+="\"$(echo "$item" | sed 's/"/\\"/g')\""
    done
    out+="]"
    echo "$out"
  }

  echo "{\"score\": ${TOTAL}, \"pass\": $(json_array "${PASS_ITEMS[@]}"), \"fail\": $(json_array "${FAIL_ITEMS[@]}"), \"warn\": $(json_array "${WARN_ITEMS[@]}")}"

  rm -rf "$INSTALL_PATH"
  exit 0
fi

# Print to stdout
render_scorecard

# Write to scorecard file
mkdir -p "$(dirname "$SCORECARD")"
{
  echo "# Starter Kit Benchmark Scorecard"
  echo "Generated: $(date)"
  echo ""
  echo '```'
  render_scorecard
  echo '```'
} > "$SCORECARD"

echo ""
echo "Scorecard written to: $SCORECARD"
echo "Install path before cleanup: $INSTALL_PATH"
echo ""

# Cleanup
rm -rf "$INSTALL_PATH"
echo "Cleaned up: $INSTALL_PATH"
