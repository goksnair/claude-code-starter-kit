#!/usr/bin/env python3
"""
PostToolUse:Write hook — wiki-ingest-guard.
Fires when signal-inbox.md is written. Counts entries missing wiki-ingested marker.
If > WARN_THRESHOLD un-ingested entries exist, emits a hookSpecificOutput nudge.

Adapt SIGNAL_INBOX path to your project's knowledge structure.
"""
import json
import os
import re
import sys
from pathlib import Path

PROJECT_ROOT = os.environ.get("PROJECT_ROOT", os.getcwd())

# Adapt this path to your project's signal inbox location
SIGNAL_INBOX = Path(PROJECT_ROOT) / "knowledge" / "indie" / "signal-inbox.md"
WARN_THRESHOLD = 5


def count_unindexed(content: str) -> int:
    """Count ### entries where processed_by does not contain wiki-ingested."""
    unindexed = 0
    # Split on entry headers
    entries = re.split(r"^### ", content, flags=re.MULTILINE)
    for entry in entries[1:]:  # skip preamble before first ###
        processed_match = re.search(r"^- processed_by:\s*\[([^\]]*)\]", entry, re.MULTILINE)
        if processed_match:
            processors = processed_match.group(1)
            if "wiki-ingested" not in processors:
                unindexed += 1
        else:
            # Entry exists but has no processed_by line — counts as un-ingested
            unindexed += 1
    return unindexed


def main():
    try:
        hook_input = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    if hook_input.get("tool_name") not in ("Write", "Edit"):
        sys.exit(0)

    file_path = hook_input.get("tool_input", {}).get("file_path", "")
    if "signal-inbox.md" not in file_path:
        sys.exit(0)

    # Use the actual file path from the hook input if the default doesn't exist
    inbox_path = Path(file_path) if os.path.exists(file_path) else SIGNAL_INBOX
    if not inbox_path.exists():
        sys.exit(0)

    content = inbox_path.read_text()
    count = count_unindexed(content)

    if count > WARN_THRESHOLD:
        output = {
            "hookSpecificOutput": (
                f"⚠️ wiki-ingest-guard: {count} signal-inbox entries lack wiki-ingested marker. "
                f"Run your ingest command and answer y to ingest top signals into wiki pages."
            )
        }
        print(json.dumps(output))

    sys.exit(0)


if __name__ == "__main__":
    main()
