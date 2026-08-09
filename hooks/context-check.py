#!/usr/bin/env python3
"""
context-check.py — Stop hook
Fires after every Claude response. Reads session_turn_count from AGENT_STATE.json
and warns when context is getting heavy, suggesting /compact.

Equivalent to ECC's strategic compaction hook, adapted for ElderWorld's
Python-based hook infrastructure.

Thresholds (matching CLAUDE_OPS rules):
  - Turn 10: YELLOW — consider /compact
  - Turn 15: ORANGE — strongly recommend /compact before next task
  - Turn 20+: RED — compact now or risk context degradation

Hook type: Stop
Trigger: Every session stop event
"""

import json
import os
import sys
from pathlib import Path

PROJECT_DIR = os.environ.get("CLAUDE_PROJECT_DIR", "")
if not PROJECT_DIR:
    PROJECT_DIR = str(Path(__file__).resolve().parent.parent.parent)

AGENT_STATE_PATH = Path(PROJECT_DIR) / ".claude" / "scratch" / "AGENT_STATE.json"

THRESHOLDS = {
    20: ("RED 🔴", "Compact NOW — context degradation likely at this turn count."),
    15: ("ORANGE 🔶", "Strongly recommend /compact before starting your next task."),
    10: ("YELLOW ⚠️", "Consider running /compact soon to keep context fresh."),
}


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        data = {}

    # Read current turn count
    turn_count = 0
    try:
        if AGENT_STATE_PATH.exists():
            with open(AGENT_STATE_PATH) as f:
                state = json.load(f)
            turn_count = state.get("session_turn_count", 0)
    except Exception:
        pass

    # Emit warning at threshold crossings
    for threshold, (level, message) in sorted(THRESHOLDS.items(), reverse=True):
        if turn_count >= threshold:
            sys.stderr.write(
                f"Context: {level} (turn {turn_count}) — {message}\n"
            )
            break

    sys.stdout.write(json.dumps(data) if data else "")
    sys.exit(0)


if __name__ == "__main__":
    main()
