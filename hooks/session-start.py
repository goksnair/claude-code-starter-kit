#!/usr/bin/env python3
"""
session-start.py — SessionStart hook
Fires when Claude Code opens a session. Prints a morning briefing:
  - Project name, date, current git branch
  - IMMEDIATE NEXT TASK line from SESSION_HANDOFF.md
  - Any deadline/urgency lines from STATUS.md (if present)

Customize this file:
  - DEADLINE_KEYWORDS: add/remove words that trigger a deadline warning
  - MEMORY_FILE: change the path if your status/goals file lives elsewhere
  - HANDOFF_FILE: update if your handoff file is in a different location
"""

import json
import re
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

# ── Path setup ────────────────────────────────────────────────────────────────
# Hooks live at .claude/hooks/ — three parents up is project root
PROJ = Path(__file__).resolve().parents[2]

HANDOFF_FILE = PROJ / ".claude" / "status" / "SESSION_HANDOFF.md"
MEMORY_FILE  = PROJ / ".claude" / "memory" / "STATUS.md"

# ── Customize: keywords that flag a line as a deadline warning ────────────────
DEADLINE_KEYWORDS = ["DEADLINE", "ASAP", "OVERDUE", "days remaining", "DUE"]


# ── Helpers ───────────────────────────────────────────────────────────────────

def git_branch() -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(PROJ), "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, timeout=3
        )
        return result.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def read_next_task() -> str | None:
    """Return the IMMEDIATE NEXT TASK block from SESSION_HANDOFF.md, or first next-step line."""
    if not HANDOFF_FILE.exists():
        return None
    text = HANDOFF_FILE.read_text()
    # Try structured IMMEDIATE NEXT TASK section
    m = re.search(r"##\s+IMMEDIATE NEXT TASK\s*\n(.*?)(?=\n##|\Z)", text, re.DOTALL)
    if m:
        task = m.group(1).strip()
        return task[:200].rstrip() + ("..." if len(task) > 200 else "")
    # Fallback: first non-empty line under a "## Next" heading
    in_next = False
    for line in text.splitlines():
        if re.match(r"^##\s+Next", line):
            in_next = True
            continue
        if in_next and line.strip() and not line.startswith("#"):
            return line.strip()
    return None


def read_deadlines() -> list[str]:
    """Return lines from the memory file that contain deadline keywords."""
    if not MEMORY_FILE.exists():
        return []
    hits = []
    for line in MEMORY_FILE.read_text().splitlines():
        if any(kw.lower() in line.lower() for kw in DEADLINE_KEYWORDS):
            stripped = line.strip()
            if stripped:
                hits.append(stripped)
    return hits


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    # Consume stdin (Claude Code passes hook input via stdin)
    try:
        json.load(sys.stdin)
    except Exception:
        pass

    project_name = PROJ.name
    today        = date.today().isoformat()
    branch       = git_branch()

    lines = [
        f"-- Session start: {project_name} --",
        f"   Date   : {today}",
        f"   Branch : {branch}",
    ]

    # Next task from handoff file
    next_task = read_next_task()
    if next_task:
        lines.append(f"   Next   : {next_task}")
    elif not HANDOFF_FILE.exists():
        lines.append("   Note   : SESSION_HANDOFF.md not found — create it at .claude/status/SESSION_HANDOFF.md")

    # Deadline warnings from memory file
    deadlines = read_deadlines()
    if deadlines:
        lines.append("   -- Deadlines --")
        for dl in deadlines:
            lines.append(f"   !  {dl}")
    elif not MEMORY_FILE.exists():
        lines.append("   (STATUS.md not found at .claude/memory/STATUS.md — no deadline check)")

    lines.append("--")

    output = {
        "hookSpecificOutput": "\n".join(lines)
    }
    print(json.dumps(output))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # Never crash — print a warning and exit cleanly
        print(json.dumps({"hookSpecificOutput": f"session-start.py error: {e}"}))
        sys.exit(0)
