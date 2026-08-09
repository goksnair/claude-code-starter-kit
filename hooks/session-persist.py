#!/usr/bin/env python3
"""
session-persist.py — Stop hook
Fires after every Claude response. Checks if SESSION_HANDOFF.md is getting stale
and reminds the user to update it. Also logs turn count to AGENT_STATE.json.

Equivalent to ECC's stop:session-end memory persistence hook, adapted for
ElderWorld's Python-based hook infrastructure and SESSION_HANDOFF workflow.

Hook type: Stop
Trigger: Every session stop event
"""

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = os.environ.get("CLAUDE_PROJECT_DIR", "")
if not PROJECT_DIR:
    # Try to infer from script location
    PROJECT_DIR = str(Path(__file__).resolve().parent.parent.parent)

AGENT_STATE_PATH = Path(PROJECT_DIR) / ".claude" / "scratch" / "AGENT_STATE.json"
SESSION_HANDOFF_PATH = Path(PROJECT_DIR) / ".claude" / "status" / "SESSION_HANDOFF.md"

# Warn if SESSION_HANDOFF hasn't been modified in this many minutes
STALENESS_WARN_MINUTES = 90


def load_agent_state() -> dict:
    try:
        if AGENT_STATE_PATH.exists():
            with open(AGENT_STATE_PATH) as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def save_agent_state(state: dict) -> None:
    try:
        AGENT_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        tmp = AGENT_STATE_PATH.with_suffix(".json.tmp")
        with open(tmp, "w") as f:
            json.dump(state, f, indent=2)
        tmp.rename(AGENT_STATE_PATH)
    except Exception:
        pass


def check_session_handoff_staleness() -> str | None:
    """Return a warning string if SESSION_HANDOFF.md is stale, else None."""
    try:
        if not SESSION_HANDOFF_PATH.exists():
            return None
        mtime = SESSION_HANDOFF_PATH.stat().st_mtime
        age_minutes = (datetime.now().timestamp() - mtime) / 60
        if age_minutes > STALENESS_WARN_MINUTES:
            return (
                f"⚠️  SESSION_HANDOFF.md last updated {int(age_minutes)}m ago. "
                "Consider updating before ending the session."
            )
    except Exception:
        pass
    return None


def extract_completed_block(handoff_path: Path) -> str:
    """Extract the COMPLETED THIS SESSION block from SESSION_HANDOFF.md."""
    try:
        text = handoff_path.read_text(encoding="utf-8")
        # Find first COMPLETED THIS SESSION heading
        match = re.search(
            r"(##\s+COMPLETED THIS SESSION.*?)(?=^##\s|\Z)",
            text,
            re.MULTILINE | re.DOTALL
        )
        if match:
            return match.group(1).strip()
    except Exception:
        pass
    return ""


def should_prompt_graph_capture(state: dict, completed_block: str) -> bool:
    """
    Prompt for graph capture if:
    - There is a non-empty COMPLETED THIS SESSION block
    - We haven't already prompted this session
    """
    if not completed_block or len(completed_block) < 100:
        return False
    last_graph_prompt = state.get("last_graph_capture_prompt", "")
    today = datetime.now().strftime("%Y-%m-%d")
    return last_graph_prompt != today


def build_graph_capture_prompt(completed_block: str) -> str:
    return (
        "\n[graph-capture] New completed work detected in SESSION_HANDOFF.md.\n"
        "Scan the block below for decisions, milestones, or dependencies worth adding to the ECC graph.\n"
        "For each candidate, show:\n"
        "  • Entity name\n"
        "  • Type (decision / milestone / dependency / person)\n"
        "  • 1-2 observations\n"
        "  • Suggested relations\n"
        "Then ask for approval before adding anything.\n\n"
        f"--- COMPLETED BLOCK ---\n{completed_block[:1500]}\n--- END ---\n"
        "\nReply with: GRAPH ADD [entity list] or GRAPH SKIP to skip."
    )


def main():
    # Read Stop hook input from stdin (contains transcript_path etc.)
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        data = {}

    # Increment session turn count
    state = load_agent_state()
    turn_count = state.get("session_turn_count", 0) + 1
    state["session_turn_count"] = turn_count
    state["last_stop_at"] = datetime.now(timezone.utc).isoformat()

    # Check staleness and emit warning if needed
    warning = check_session_handoff_staleness()
    if warning:
        sys.stderr.write(warning + "\n")

    # Layer 3 — graph capture prompt
    completed_block = extract_completed_block(SESSION_HANDOFF_PATH)
    if should_prompt_graph_capture(state, completed_block):
        prompt = build_graph_capture_prompt(completed_block)
        sys.stderr.write(prompt + "\n")
        state["last_graph_capture_prompt"] = datetime.now().strftime("%Y-%m-%d")

    save_agent_state(state)

    # Pass through — Stop hooks must write the input back to stdout unchanged
    sys.stdout.write(json.dumps(data) if data else "")
    sys.exit(0)


if __name__ == "__main__":
    main()
