#!/usr/bin/env python3
"""
PreCompact hook — fires before Claude compresses context.
Saves a session snapshot to knowledge/sessions/[date].md.
Keeps only the 30 most recent session files — auto-cleans older ones.
"""

import json, sys, os
from datetime import date, datetime
from pathlib import Path

PROJ = str(Path(__file__).parent.parent.parent)
SESSIONS_DIR = os.path.join(PROJ, "knowledge/sessions")
SCRATCHPAD = os.path.join(PROJ, ".claude/scratch/SCRATCHPAD.md")
STATE_FILE = os.path.join(PROJ, ".claude/scratch/AGENT_STATE.json")
MAX_SESSION_FILES = 30


def cleanup_old_sessions():
    """Keep only the MAX_SESSION_FILES most recent session files."""
    try:
        files = sorted([
            f for f in os.listdir(SESSIONS_DIR)
            if f.endswith(".md") and f != "README.md"
        ])
        if len(files) > MAX_SESSION_FILES:
            to_delete = files[:len(files) - MAX_SESSION_FILES]
            for f in to_delete:
                os.remove(os.path.join(SESSIONS_DIR, f))
            return len(to_delete)
    except Exception:
        pass
    return 0


def main():
    try:
        json.load(sys.stdin)
    except Exception:
        pass

    today = date.today().isoformat()
    session_file = os.path.join(SESSIONS_DIR, f"{today}.md")
    os.makedirs(SESSIONS_DIR, exist_ok=True)

    scratchpad_content = ""
    if os.path.exists(SCRATCHPAD):
        with open(SCRATCHPAD) as f:
            scratchpad_content = f.read()

    state = {}
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                state = json.load(f)
        except Exception:
            pass

    turn_count = state.get("session_turn_count", "?")
    persona = state.get("active_persona", "none")
    session_id = state.get("session_id", "unknown")

    snapshot = f"""# Session Snapshot — {today}

*Auto-saved by PreCompact hook before context compression.*

## Metadata
- Session: {session_id} | Turns: {turn_count} | Persona: {persona}
- Saved at: {datetime.now().strftime('%H:%M')}

## SCRATCHPAD
{scratchpad_content if scratchpad_content else '*(empty)*'}

---
*Review this file if session context feels thin after /compact.*
"""

    mode = "a" if os.path.exists(session_file) else "w"
    with open(session_file, mode) as f:
        if mode == "a":
            f.write("\n\n---\n\n")
        f.write(snapshot)

    deleted = cleanup_old_sessions()
    cleanup_note = f" | Cleaned {deleted} old files." if deleted else ""
    print(f"[session-backup] Snapshot → knowledge/sessions/{today}.md "
          f"(turn {turn_count}){cleanup_note}")


if __name__ == "__main__":
    main()
