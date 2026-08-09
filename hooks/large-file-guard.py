#!/usr/bin/env python3
"""
large-file-guard.py — PreToolUse(Read) hook

Fires before every Read tool call. If the target file exceeds the line
threshold AND no offset/limit was supplied, injects a warning that tells
Claude to use targeted reads instead of loading the whole file.

Enforces: ai-workflow.md § "Keep reads targeted (offset/limit, not full files)"

Hook type: PreToolUse
Matcher: Read
Severity: non-blocking (warn only — never block legitimate reads)

Thresholds:
  WARN  > 200 lines  — suggest offset/limit
  HARD  > 800 lines  — strong warning, cost/context impact noted
"""

import json
import os
import sys
from pathlib import Path

WARN_THRESHOLD = 200   # lines — suggest targeted read
HARD_THRESHOLD = 800   # lines — strong warning

def count_lines(path: str) -> int:
    """Count lines in file. Returns 0 if file doesn't exist or can't be read."""
    try:
        with open(path, "r", errors="replace") as f:
            return sum(1 for _ in f)
    except Exception:
        return 0


def main() -> None:
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        sys.exit(0)

    tool_input = data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")
    if not file_path:
        sys.exit(0)

    # If offset or limit already provided — user is being targeted, no warn needed
    if tool_input.get("offset") is not None or tool_input.get("limit") is not None:
        sys.exit(0)

    # Resolve path
    cwd = data.get("cwd", os.getcwd())
    if not os.path.isabs(file_path):
        file_path = os.path.join(cwd, file_path)

    if not os.path.isfile(file_path):
        sys.exit(0)  # File doesn't exist yet — let Read handle the error

    line_count = count_lines(file_path)

    if line_count <= WARN_THRESHOLD:
        sys.exit(0)  # Small file — no issue

    rel = os.path.relpath(file_path, cwd)

    if line_count > HARD_THRESHOLD:
        level = "LARGE FILE WARNING 🔴"
        impact = f"~{line_count} lines will consume significant context window."
        advice = (
            f"Use offset+limit to read only the section you need:\n"
            f"  Read(file_path='{rel}', offset=<start_line>, limit=<num_lines>)\n"
            f"  Or use Grep to find the relevant section first."
        )
    else:
        level = "LARGE FILE NOTICE ⚠️"
        impact = f"~{line_count} lines — consider targeted read."
        advice = (
            f"If you only need part of this file, use:\n"
            f"  Read(file_path='{rel}', offset=<start_line>, limit=<num_lines>)"
        )

    message = (
        f"{level}: `{rel}` has ~{line_count} lines. {impact}\n"
        f"{advice}\n"
        f"Proceeding with full read anyway — this is a warning, not a block."
    )

    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": message
        }
    }
    print(json.dumps(output))
    sys.exit(0)


if __name__ == "__main__":
    main()
