#!/usr/bin/env python3
"""
PostToolUse hook — mcp-result-logger.py
Fires after every tool call. If tool_name starts with 'mcp__', appends one
NDJSON line to $HOME/.claude/scratch/mcp-tool-results.jsonl.
Append-only — never reads, never truncates.
Exits 0 always — must never block a tool call.
"""
import json
import os
import sys
import time
from pathlib import Path


def main() -> None:
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    if not tool_name.startswith("mcp__"):
        sys.exit(0)

    try:
        result = data.get("tool_result", "") or data.get("result", "")
        result_str = json.dumps(result) if not isinstance(result, str) else result
        record = {
            "tool": tool_name,
            "result": result_str[:500],
            "ts": int(time.time()),
        }
        sidecar = Path(os.path.expanduser("~")) / ".claude" / "scratch" / "mcp-tool-results.jsonl"
        sidecar.parent.mkdir(parents=True, exist_ok=True)
        with sidecar.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record) + "\n")
    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
