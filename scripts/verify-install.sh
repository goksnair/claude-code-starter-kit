#!/usr/bin/env bash
# verify-install.sh — End-to-end test for fresh install + upgrade path
# Usage: bash scripts/verify-install.sh
# Exit: 0 if all checks pass, 1 if any fail

set -e

TEMPLATES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PASS=0
FAIL=0
ERRORS=()

pass() { echo "  ✓ $1"; PASS=$((PASS + 1)); }
fail() { echo "  ✗ $1"; ERRORS+=("$1"); FAIL=$((FAIL + 1)); }

check_file()     { [[ -f "$1" ]] && pass "exists: $1" || fail "missing: $1"; }
check_contains() { grep -q "$2" "$1" 2>/dev/null && pass "contains '$2': $1" || fail "missing '$2' in $1"; }

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STARTER KIT INSTALL VERIFICATION"
echo "Kit version: $(cat "$TEMPLATES_DIR/KIT_VERSION" 2>/dev/null || echo 'MISSING')"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ── TEST A: Fresh install ──────────────────────────────────────────────────────
echo ""
echo "TEST A — Fresh install"
FRESH=$(mktemp -d)
trap 'rm -rf "$FRESH" "$OLD" 2>/dev/null || true' EXIT

bash "$TEMPLATES_DIR/install.sh" --non-interactive FreshTest "$FRESH" "Test User" &>/dev/null

check_file "$FRESH/.claude/settings.json"
check_file "$FRESH/KIT_VERSION"
check_file "$FRESH/.claude/hooks/session-start.py"
check_file "$FRESH/.claude/hooks/bash-tool-guard.py"
check_file "$FRESH/.claude/hooks/memory-validator.py"
check_file "$FRESH/.claude/hooks/implementation-audit.py"
check_file "$FRESH/.claude/memory/STATUS.md"
check_file "$FRESH/.claude/memory/goals.md"
check_file "$FRESH/.claude/status/SESSION_HANDOFF.md"
check_contains "$FRESH/.claude/settings.json" "session-start.py"
check_contains "$FRESH/.claude/settings.json" "bash-tool-guard.py"
check_contains "$FRESH/KIT_VERSION" "20"

# No unresolved placeholders in installed hooks/memory/settings
if grep -r "{{PROJECT_PATH}}\|{{PROJECT_NAME}}\|{{USER_NAME}}" \
    "$FRESH/.claude/hooks/" "$FRESH/.claude/memory/" "$FRESH/.claude/settings.json" 2>/dev/null | grep -v ".pyc"; then
  fail "Unresolved placeholders found in installed files"
else
  pass "No unresolved placeholders in hooks/memory/settings"
fi

A_PASS=$PASS
A_FAIL=$FAIL
echo ""
echo "TEST A result: $A_PASS passed, $A_FAIL failed"

# ── TEST B: Upgrade path ───────────────────────────────────────────────────────
echo ""
echo "TEST B — Upgrade path (simulated prior install)"
B_PASS_START=$PASS
B_FAIL_START=$FAIL

OLD=$(mktemp -d)

# Install baseline (the "older" state)
bash "$TEMPLATES_DIR/install.sh" --non-interactive OldKit "$OLD" "Test User" &>/dev/null

# Simulate user customization: add a custom Stop hook entry
jq '.hooks.Stop[0].hooks += [{"type":"command","command":"echo user-custom-hook","timeout":5,"async":true}]' \
  "$OLD/.claude/settings.json" > "$OLD/.claude/settings.json.tmp" && \
  mv "$OLD/.claude/settings.json.tmp" "$OLD/.claude/settings.json"

# Run upgrade
bash "$TEMPLATES_DIR/install.sh" --upgrade "$OLD" &>/dev/null

# Verify post-upgrade state
[[ -f "$OLD/.claude/settings.json" ]] && pass "settings.json still present after upgrade" || fail "settings.json missing after upgrade"
ls "$OLD/.claude/settings.json.backup-"* &>/dev/null && pass "backup created" || fail "no backup found"
grep -q "user-custom-hook" "$OLD/.claude/settings.json" && pass "user customization preserved" || fail "user customization LOST"
[[ -f "$OLD/KIT_VERSION" ]] && pass "KIT_VERSION present after upgrade" || fail "KIT_VERSION missing after upgrade"
[[ -f "$OLD/.claude/hooks/implementation-audit.py" ]] && pass "implementation-audit.py present after upgrade" || fail "implementation-audit.py missing after upgrade"
grep -q "implementation-audit.py" "$OLD/.claude/settings.json" \
  && pass "TEST B: implementation-audit.py wired in settings.json" \
  || fail "TEST B: implementation-audit.py missing from settings.json — jq merge may have failed"

B_PASS=$((PASS - B_PASS_START))
B_FAIL=$((FAIL - B_FAIL_START))
echo ""
echo "TEST B result: $B_PASS passed, $B_FAIL failed"

# ── SUMMARY ───────────────────────────────────────────────────────────────────
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [[ $FAIL -eq 0 ]]; then
  echo "ALL CHECKS PASSED — kit is ready for user testing"
  echo "Total: $PASS passed, 0 failed"
  exit 0
else
  echo "FAILURES DETECTED ($FAIL total):"
  for e in "${ERRORS[@]}"; do echo "  ✗ $e"; done
  echo "Total: $PASS passed, $FAIL failed"
  exit 1
fi
