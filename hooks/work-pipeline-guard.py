#!/usr/bin/env python3
"""
work-pipeline-guard.py — Stop hook
Observes /work invocations and logs any that completed without producing
a WORKORDER.json file (evidence the PE pipeline was bypassed).

Non-blocking — always exits 0. Append-only log for metrics.
"""
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

PROJ = Path(os.environ.get("PROJECT_PATH", os.getcwd()))
WORKORDER_PATH = PROJ / ".claude" / "scratch" / "WORKORDER.json"
LOG_PATH = PROJ / ".claude" / "logs" / "pipeline-bypass.log"


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    prompt = data.get("prompt", "") or ""
    if not re.search(r"(?m)^/work\b", prompt):
        sys.exit(0)

    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        directive = prompt[:200].replace("\n", " ")
        entry = {
            "ts": datetime.now().isoformat(timespec="seconds"),
            "directive": directive,
            "workorder_present_at_stop": WORKORDER_PATH.exists(),
        }
        with open(LOG_PATH, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
