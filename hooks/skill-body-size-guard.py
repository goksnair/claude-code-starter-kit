#!/usr/bin/env python3
"""
skill-body-size-guard.py — PostToolUse:Write hook
Warns when a skill/command file exceeds the line limit after a write.
Non-blocking — always exits 0.

Thresholds:
  WARNING  > 200 lines — approaching heavy
  ERROR    > 300 lines — heavy; context cost is significant
"""
import json
import os
import sys

PROJECT_ROOT = os.environ.get("PROJECT_ROOT", os.getcwd())

WARNING_LINES = 200
ERROR_LINES = 300

WATCHED_DIRS = [
    os.path.join(PROJECT_ROOT, ".claude", "commands") + os.sep,
]


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    file_path = data.get("tool_input", {}).get("file_path", "")
    if not file_path:
        sys.exit(0)

    # Only watch .claude/commands/
    if not any(file_path.startswith(d) for d in WATCHED_DIRS):
        sys.exit(0)

    # Only .md files
    if not file_path.endswith(".md"):
        sys.exit(0)

    try:
        with open(file_path) as f:
            lines = f.readlines()
        count = len(lines)
    except Exception:
        sys.exit(0)

    fname = os.path.basename(file_path)

    if count > ERROR_LINES:
        print(f"🔴 SKILL SIZE: {fname} is {count} lines (limit: {ERROR_LINES}). "
              f"Heavy skill bodies burn context on every invocation. "
              f"Consider extracting logic to a script or subagent.")
    elif count > WARNING_LINES:
        print(f"⚠️  SKILL SIZE: {fname} is {count} lines (warning at {WARNING_LINES}). "
              f"Consider trimming before it grows further.")

    sys.exit(0)


if __name__ == "__main__":
    main()
