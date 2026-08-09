#!/usr/bin/env python3
"""
git-recent-wins.py — PostToolUse hook (Write events on knowledge/ files)
Auto-generates knowledge/wiki/recent-wins.md from git log after commits.
Filters to public-safe commits only — excludes client/financial/personal data.
Non-blocking — always exits 0.
"""
import subprocess
import os
import sys
import json
from datetime import datetime
from pathlib import Path

PROJ = Path(os.environ.get("PROJECT_PATH", os.getcwd()))
OUT = PROJ / "knowledge" / "wiki" / "recent-wins.md"

INCLUDE_SCOPES = {"feat", "fix", "infra", "loops", "hooks", "agents", "scripts", "docs", "chore"}

EXCLUDE_KEYWORDS = {
    "client", "invoice", "payment", "revenue", "income", "salary",
    "finance", "consulting", "contract", "private", "confidential"
}


def get_recent_commits(n=20):
    result = subprocess.run(
        ["git", "-C", str(PROJ), "log", "--oneline", f"-{n}", "--format=%h %s"],
        capture_output=True, text=True
    )
    return result.stdout.strip().split("\n") if result.stdout.strip() else []


def is_public_safe(message: str) -> bool:
    msg_lower = message.lower()
    for kw in EXCLUDE_KEYWORDS:
        if kw in msg_lower:
            return False
    for scope in INCLUDE_SCOPES:
        if msg_lower.startswith(f"{scope}(") or msg_lower.startswith(f"{scope}:"):
            return True
    return False


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    commits = get_recent_commits(20)
    public_commits = []
    for line in commits:
        if not line.strip():
            continue
        parts = line.split(" ", 1)
        if len(parts) < 2:
            continue
        sha, message = parts[0], parts[1]
        if is_public_safe(message):
            public_commits.append((sha, message))

    today = datetime.now().strftime("%Y-%m-%d")
    lines = [
        "# Recent Wins — Shipped Work",
        f"_Auto-generated from git log on {today}. Do not edit manually._",
        "",
        "## Recent Commits",
        "",
    ]

    if public_commits:
        for sha, msg in public_commits[:10]:
            lines.append(f"- `{sha}` {msg}")
    else:
        lines.append("_No commits in last 20._")

    lines.append("")
    lines.append(f"_Last updated: {today}_")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n")
    print(f"[git-recent-wins] wrote {len(public_commits)} entries to {OUT}")
    sys.exit(0)


if __name__ == "__main__":
    main()
