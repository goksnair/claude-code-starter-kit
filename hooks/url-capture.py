#!/usr/bin/env python3
"""
UserPromptSubmit hook — URL auto-capture with intent detection.
Detects http/https URLs in user messages, infers intent from surrounding text,
and routes to LINK_INBOX.md with appropriate priority.

Intent signals → action-required:
  "implement", "add this", "use this", "build this", "wire this", "we should",
  "set this up", "install this", "integrate", "apply this", "do this"

action-required items also write an OPEN ITEM to SESSION_HANDOFF.md immediately.
"""
import json
import re
import sys
from datetime import datetime
from pathlib import Path

PROJ = Path(__file__).resolve().parents[2]
LINK_INBOX = PROJ / "knowledge" / "claude-ops" / "LINK_INBOX.md"
SESSION_HANDOFF = PROJ / ".claude" / "status" / "SESSION_HANDOFF.md"
PROJECT_NAME = PROJ.name

ACTION_SIGNALS = [
    "implement", "add this", "use this", "build this", "wire this",
    "we should", "set this up", "install this", "integrate", "apply this",
    "do this", "set up", "try this", "use for", "add to", "bring this in",
    "should we use", "can we use", "let's use", "let's add", "let's build",
]


def detect_intent(message: str) -> str:
    """Return 'action-required' if message contains implementation signals, else 'queue'."""
    lower = message.lower()
    for signal in ACTION_SIGNALS:
        if signal in lower:
            return "action-required"
    return "queue"


def extract_summary_hint(message: str, url: str) -> str:
    """Pull surrounding text near the URL as a summary hint."""
    idx = message.find(url)
    if idx == -1:
        return ""
    start = max(0, idx - 60)
    end = min(len(message), idx + len(url) + 60)
    context = message[start:end].replace(url, "").strip(" —:-\n")
    context = re.sub(r'\s+', ' ', context).strip()
    return context[:100] if context else ""


def append_open_item(url: str, summary_hint: str, today: str) -> None:
    """Write an OPEN ITEM entry to SESSION_HANDOFF.md under ## Open Items."""
    if not SESSION_HANDOFF.exists():
        return

    content = SESSION_HANDOFF.read_text()
    label = summary_hint if summary_hint else url[:80]
    new_item = f"- [ ] **[action-required]** {label} — {url} (captured {today})"

    if "## Open Items" not in content:
        content = content.rstrip() + f"\n\n## Open Items\n\n{new_item}\n"
    else:
        lines = content.splitlines()
        out = []
        inserted = False
        for i, line in enumerate(lines):
            out.append(line)
            if not inserted and line.strip() == "## Open Items":
                out.append("")
                out.append(new_item)
                inserted = True
        content = "\n".join(out) + "\n"

    SESSION_HANDOFF.write_text(content)


def main():
    try:
        hook_input = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    message = hook_input.get("prompt", "")
    urls = re.findall(r'https?://[^\s\)\]\'"<>]+', message)

    if not urls:
        sys.exit(0)

    if not LINK_INBOX.exists():
        sys.exit(0)

    today = datetime.now().strftime("%Y-%m-%d")
    priority = detect_intent(message)
    existing = LINK_INBOX.read_text()
    new_rows = []
    action_items = []

    for url in urls:
        if url in existing:
            continue
        summary_hint = extract_summary_hint(message, url)
        summary = f"[auto-captured: {PROJECT_NAME}]" + (f" — {summary_hint}" if summary_hint else "")
        row = f"| {today} | {url} | {summary} | pending | {priority} | pending |"
        new_rows.append((row, url, summary_hint))
        if priority == "action-required":
            action_items.append((url, summary_hint))

    if not new_rows:
        sys.exit(0)

    lines = existing.splitlines()
    output_lines = []
    inserted = False

    for i, line in enumerate(lines):
        output_lines.append(line)
        if not inserted and line.startswith("| ---") and i > 0 and "Pending" in "\n".join(lines[max(0, i - 5):i]):
            for row, url, hint in new_rows:
                output_lines.append(row)
            inserted = True

    if not inserted:
        output_lines.append("")
        for row, url, hint in new_rows:
            output_lines.append(row)

    LINK_INBOX.write_text("\n".join(output_lines) + "\n")

    for url, hint in action_items:
        append_open_item(url, hint, today)

    output = {
        "hookSpecificOutput": {
            "hookType": "UserPromptSubmit",
            "toolName": "url-capture",
            "output": ""
        }
    }
    lines_out = []
    for row, url, hint in new_rows:
        prio = "action-required" if priority == "action-required" else "queue"
        flag = " → OPEN ITEM added to SESSION_HANDOFF" if priority == "action-required" else ""
        lines_out.append(f"Captured [{prio}] {url}{flag}")

    output["hookSpecificOutput"]["output"] = "\n".join(lines_out)
    print(json.dumps(output))
    sys.exit(0)


if __name__ == "__main__":
    main()
