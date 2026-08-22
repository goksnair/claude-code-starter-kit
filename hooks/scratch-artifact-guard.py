#!/usr/bin/env python3
"""PreToolUse(Write) — warns when permanent artifacts are written to auto-purged scratch/.

Run with --test to verify the hook logic without a live Claude Code Write call:
  python3 scratch-artifact-guard.py --test
"""

import fnmatch
import json
import os
import sys
from pathlib import Path

# Exact filenames that are safe to write to scratch/ — will not trigger warning.
# Add new agent output files here when they are introduced.
SAFE_FILENAMES = {
    "AGENT_STATE.json",
    "SCRATCHPAD.md",
    "WORKORDER.json",
    "CONTEXT_AUDIT.md",
    "IE_OUTPUT.md",
}

# Glob patterns for safe temp files. *_OUTPUT.md and *-output-*.md cover
# agent output files (e.g. FOO_OUTPUT.md, harness-optimizer-output-20260823.md).
# Add patterns here rather than individual filenames when a whole class is safe.
SAFE_GLOB_PATTERNS = [
    "*_OUTPUT.md",       # agent output files (uppercase convention)
    "*-output-*.md",     # dated output files
    "*-backup-*.md",     # pre-compact backups
    "*.json",            # all JSON files in scratch are working state
    "*.tmp",
]

# (filename patterns, suggested destination)
ROUTING_TABLE = [
    (["*-instructions.md", "*-guide.md", "*-doc.md", "*-onboarding*.md"], "knowledge/user-docs/"),
    (["*-plan.md", "*-strategy.md"], "knowledge/claude-ops/ or knowledge/indie/"),
    (["*-research*.md", "*-signal*.md"], "knowledge/indie/signal-inbox.md or knowledge/wiki/"),
    (["*-audit*.md"], ".claude/status/ or knowledge/claude-ops/"),
]


def is_in_scratch(abs_path: str) -> bool:
    """Return True if path contains /.claude/scratch/ as a component.

    Detects scratch regardless of the OS project folder name or base path,
    so the hook works even if the project is not at ~/gokul-os.
    """
    parts = Path(abs_path).parts
    for i, part in enumerate(parts):
        if part == ".claude" and i + 1 < len(parts) and parts[i + 1] == "scratch":
            return True
    return False


def suggest_destination(filename: str) -> str:
    lower = filename.lower()
    for patterns, dest in ROUTING_TABLE:
        for pat in patterns:
            if fnmatch.fnmatch(lower, pat):
                return dest
    return "knowledge/ (general)"


def check_path(file_path: str) -> bool:
    """Return True if a warning should fire for this path. Used by main() and --test."""
    if not file_path:
        return False
    abs_path = os.path.normpath(os.path.expanduser(file_path))
    if not is_in_scratch(abs_path):
        return False
    filename = Path(abs_path).name
    if filename in SAFE_FILENAMES:
        return False
    for pattern in SAFE_GLOB_PATTERNS:
        if fnmatch.fnmatch(filename, pattern):
            return False
    return True


def run_tests() -> None:
    """Self-test mode: verify hook logic without a live Write call."""
    cases = [
        # (path, should_warn, label)
        ("~/.claude/scratch/AGENT_STATE.json", False, "safe: AGENT_STATE.json"),
        ("~/.claude/scratch/WORKORDER.json", False, "safe: WORKORDER.json"),
        ("~/.claude/scratch/FOO_OUTPUT.md", False, "safe: *_OUTPUT.md pattern"),
        ("~/.claude/scratch/harness-optimizer-output-20260823.md", False, "safe: *-output-*.md"),
        ("~/.claude/scratch/pre-compact-backup-001.md", False, "safe: *-backup-*.md"),
        ("~/.claude/scratch/viresha-onboarding-instructions.md", True, "warn: onboarding doc"),
        ("~/.claude/scratch/audit-results.md", True, "warn: audit file"),
        ("~/gokul-os/knowledge/user-docs/guide.md", False, "safe: outside scratch"),
        ("~/gokul-os/.claude/scratch/session-plan.md", True, "warn: plan in scratch"),
    ]
    passed = failed = 0
    for path, expect_warn, label in cases:
        got = check_path(path)
        ok = got == expect_warn
        status = "✅" if ok else "❌"
        print(f"  {status} {label}")
        if ok:
            passed += 1
        else:
            failed += 1
            print(f"     expected warn={expect_warn}, got {got} for: {path}")
    print(f"\n{passed}/{passed+failed} tests passed")
    sys.exit(0 if failed == 0 else 1)


def main() -> None:
    if "--test" in sys.argv:
        run_tests()

    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        sys.exit(0)

    file_path = data.get("tool_input", {}).get("file_path", "")
    if not check_path(file_path):
        sys.exit(0)

    filename = Path(os.path.expanduser(file_path)).name
    dest = suggest_destination(filename)
    print(
        f"WARNING: SCRATCH ARTIFACT GUARD -- possible permanent file written to scratch/\n"
        f"   File: {filename}\n"
        f"   Scratch/ is auto-wiped at /end and /checkpoint -- this file WILL be deleted.\n"
        f"\n"
        f"   Suggested destination based on file type:\n"
        f"   {dest}\n"
        f"\n"
        f"   Proceeding with write -- move this file after writing if it should persist.\n"
        f"   To silence: add filename to SAFE_FILENAMES or SAFE_GLOB_PATTERNS in\n"
        f"   infra/hooks/scratch-artifact-guard.py",
        file=sys.stderr,
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
