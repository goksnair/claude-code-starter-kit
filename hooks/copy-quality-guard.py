#!/usr/bin/env python3
"""
copy-quality-guard.py
PostToolUse hook — fires on Write/Edit to content-adjacent file paths.
Injects a /copy-check reminder before external-facing copy leaves the session.
"""
import json
import re
import sys

# Paths/patterns that suggest external-facing copy
CONTENT_PATTERNS = [
    r'/tmp/',
    r'draft',
    r'email',
    r'proposal',
    r'pitch',
    r'social',
    r'\.txt$',
    r'copy[-_]',
    r'[-_]copy',
    r'\bcontent\b',
    r'campaign',
    r'newsletter',
    r'announcement',
    r'press[-_]release',
    r'blog',
    r'landing',
    r'onboarding',
    r'welcome[-_]kit',
    r'investor',
]

# Paths that are always internal — never flag these
EXEMPT_PATTERNS = [
    r'\.claude/',
    r'/infra/',
    r'knowledge/wiki/',
    r'knowledge/security/',
    r'/hooks/',
    r'/commands/',
    r'COPY_QUALITY_INDEX',
    r'copy-check\.md',
    r'humanize\.md',
    r'\.py$',
    r'\.json$',
    r'\.sh$',
    r'\.lock$',
    r'node_modules',
    r'CLAUDE\.md$',
    r'SESSION_HANDOFF',
    r'AGENT_STATE',
    r'career\.md$',
    r'goals\.md$',
    r'MEMORY\.md$',
]


def is_content_file(path: str) -> bool:
    path_lower = path.lower()
    for pat in EXEMPT_PATTERNS:
        if re.search(pat, path_lower):
            return False
    for pat in CONTENT_PATTERNS:
        if re.search(pat, path_lower):
            return True
    return False


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    tool_input = data.get('tool_input', {})
    file_path = tool_input.get('file_path', '')

    if not file_path or not is_content_file(file_path):
        sys.exit(0)

    output = {
        "hookEventName": "PostToolUse",
        "additionalContext": (
            f"⚠️  COPY QUALITY GATE — {file_path}\n"
            "This file looks like external-facing copy. Before sharing or publishing:\n"
            "→ Run /copy-check (≥22 PASS, 0 FAIL required)\n"
            "→ Run /humanize first if voice calibration is needed"
        )
    }
    print(json.dumps(output))
    sys.exit(0)


if __name__ == '__main__':
    main()
