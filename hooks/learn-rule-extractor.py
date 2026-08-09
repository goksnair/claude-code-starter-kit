#!/usr/bin/env python3
"""
learn-rule-extractor.py — Stop hook
Scans the session transcript for [LEARN] tags and appends them to
.claude/rules/execution.md under a ## Learned Rules section.

Usage during session: write corrections as:
  [LEARN] Never use /work for single-file edits — overhead exceeds savings
  [LEARN] Always read STATUS.md before making project decisions

The hook auto-extracts and persists these as durable rules on every Stop event.
Non-blocking — always exits 0.
"""
import json
import os
import re
import sys
from datetime import date
from pathlib import Path

PROJ = Path(os.environ.get("PROJECT_PATH", os.getcwd()))
RULES_FILE = PROJ / ".claude" / "rules" / "execution.md"
LEARNED_HEADER = "## Learned Rules"


def extract_learn_tags(transcript: str) -> list[str]:
    pattern = re.compile(r'\[LEARN\]\s+(.+)', re.IGNORECASE)
    return [m.group(1).strip() for m in pattern.finditer(transcript)]


def get_existing_learned_rules(content: str) -> set[str]:
    in_section = False
    rules = set()
    for line in content.splitlines():
        if line.strip() == LEARNED_HEADER:
            in_section = True
            continue
        if in_section:
            if line.startswith("## ") and line.strip() != LEARNED_HEADER:
                break
            m = re.match(r'^-\s+\*\*\d{4}-\d{2}-\d{2}\*\*:\s+(.+)', line)
            if m:
                rules.add(m.group(1).strip().lower())
    return rules


def append_learned_rules(new_rules: list[str]) -> int:
    if not RULES_FILE.exists():
        return 0

    content = RULES_FILE.read_text()
    existing = get_existing_learned_rules(content)

    to_add = [r for r in new_rules if r.lower() not in existing]
    if not to_add:
        return 0

    today = date.today().isoformat()
    lines_to_add = [f"- **{today}**: {r}" for r in to_add]

    if LEARNED_HEADER in content:
        parts = content.split(LEARNED_HEADER, 1)
        after = parts[1]
        updated = parts[0] + LEARNED_HEADER + "\n" + "\n".join(lines_to_add) + after
    else:
        updated = content.rstrip() + f"\n\n{LEARNED_HEADER}\n" + "\n".join(lines_to_add) + "\n"

    RULES_FILE.write_text(updated)
    return len(to_add)


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    transcript = (
        data.get("transcript", "")
        or data.get("session_text", "")
        or data.get("prompt", "")
        or ""
    )

    messages = data.get("messages", [])
    if messages and not transcript:
        transcript = " ".join(
            m.get("content", "") if isinstance(m.get("content"), str)
            else " ".join(c.get("text", "") for c in m.get("content", []) if isinstance(c, dict))
            for m in messages
        )

    if not transcript:
        sys.exit(0)

    new_rules = extract_learn_tags(transcript)
    if not new_rules:
        sys.exit(0)

    added = append_learned_rules(new_rules)
    if added > 0:
        print(f"📚 Learned {added} new rule(s) → .claude/rules/execution.md")

    sys.exit(0)


if __name__ == "__main__":
    main()
