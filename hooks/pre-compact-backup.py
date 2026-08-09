#!/usr/bin/env python3
"""
pre-compact-backup.py — PreCompact hook
Fires before Claude compresses context.
Saves SCRATCHPAD + session state snapshot to .claude/scratch/sessions/[date].md
Keeps only the 30 most recent session snapshots.

Hook type: PreCompact
"""

import json
import os
import sys
from datetime import date, datetime
from pathlib import Path

PROJECT_DIR = os.environ.get("CLAUDE_PROJECT_DIR", "")
if not PROJECT_DIR:
    PROJECT_DIR = str(Path(__file__).resolve().parent.parent.parent)

PROJ         = Path(PROJECT_DIR)
SESSIONS_DIR = PROJ / ".claude" / "scratch" / "sessions"
SCRATCHPAD   = PROJ / ".claude" / "scratch" / "SCRATCHPAD.md"
AGENT_STATE  = PROJ / ".claude" / "scratch" / "AGENT_STATE.json"
MAX_FILES    = 30


def cleanup_old_sessions():
    try:
        files = sorted([
            f for f in SESSIONS_DIR.iterdir()
            if f.suffix == ".md" and f.name != "README.md"
        ], key=lambda f: f.name)
        if len(files) > MAX_FILES:
            to_delete = files[:len(files) - MAX_FILES]
            for f in to_delete:
                f.unlink()
            return len(to_delete)
    except Exception:
        pass
    return 0


def main():
    try:
        json.load(sys.stdin)
    except Exception:
        pass

    today        = date.today().isoformat()
    session_file = SESSIONS_DIR / f"{today}.md"
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

    scratchpad_content = ""
    if SCRATCHPAD.exists():
        scratchpad_content = SCRATCHPAD.read_text()

    state = {}
    if AGENT_STATE.exists():
        try:
            state = json.loads(AGENT_STATE.read_text())
        except Exception:
            pass

    turn_count  = state.get("session_turn_count", "?")
    session_id  = state.get("session_id", "unknown")
    branch      = state.get("expected_branch", "unknown")
    active_task = state.get("active_task", {}).get("task_type") or "idle"

    snapshot = f"""# Session Snapshot — {today}

*Auto-saved by PreCompact hook before context compression.*

## Metadata
- Session: {session_id} | Branch: {branch} | Turns: {turn_count} | Active task: {active_task}
- Saved at: {datetime.now().strftime('%H:%M')}

## SCRATCHPAD
{scratchpad_content if scratchpad_content else '*(empty)*'}

---
*Review this file if session context feels thin after /compact.*
"""

    mode = "a" if session_file.exists() else "w"
    with open(session_file, mode) as f:
        if mode == "a":
            f.write("\n\n---\n\n")
        f.write(snapshot)

    deleted = cleanup_old_sessions()
    note = f" | Cleaned {deleted} old snapshots." if deleted else ""
    print(f"[pre-compact] Snapshot → .claude/scratch/sessions/{today}.md (turn {turn_count}){note}")


if __name__ == "__main__":
    main()
