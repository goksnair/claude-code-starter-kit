#!/usr/bin/env python3
"""
{{PROJECT_NAME}} Document Governance Hook
Fires on PostToolUse(Write) — injects a DOCUMENT_MAP reminder when a new
business-content .md file is written without being registered.

Hook event: PostToolUse
Matcher: Write
"""
import json
import os
import sys

# Paths that DON'T need DOCUMENT_MAP registration (infrastructure)
EXEMPT_SEGMENTS = [
    '/.claude/agents/',
    '/.claude/commands/',
    '/.claude/plugins/',
    '/.claude/rules/',
    '/.claude/scratch/',
    '/.claude/status/',
    '/.claude/templates/',
    '/.claude/hooks/',
    '/.claude/personas/',
    '/.claude/memory/',
    '/archive/',
    '/.git/',
    '/knowledge/sources/',
    '/knowledge/wiki/raw/',
]

# Paths where .md files DO need DOCUMENT_MAP registration
BUSINESS_PATHS = [
    'knowledge/wiki/',
    'knowledge/ventures/',
    'projects/',
]


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    file_path = data.get('tool_input', {}).get('file_path', '')
    if not file_path:
        sys.exit(0)

    # Only check .md files
    if not file_path.endswith('.md'):
        sys.exit(0)

    # Normalize to absolute path
    cwd = data.get('cwd', os.getcwd())
    if not os.path.isabs(file_path):
        file_path = os.path.join(cwd, file_path)

    # Normalize path separators for pattern matching
    normalized = file_path.replace(os.sep, '/')

    # Skip infrastructure / exempt paths
    if any(seg in normalized for seg in EXEMPT_SEGMENTS):
        sys.exit(0)

    # Only warn for business content paths
    if not any(p in normalized for p in BUSINESS_PATHS):
        sys.exit(0)

    # Check DOCUMENT_MAP registration
    doc_map_path = os.path.join(cwd, '.claude', 'DOCUMENT_MAP.md')
    rel_path = os.path.relpath(file_path, cwd)
    filename = os.path.basename(file_path)

    if os.path.exists(doc_map_path):
        with open(doc_map_path) as f:
            content = f.read()
        # Registered if filename OR relative path appears in DOCUMENT_MAP
        if filename in content or rel_path.replace(os.sep, '/') in content:
            sys.exit(0)  # Already registered — no reminder needed

    # File is not registered — inject reminder into Claude's context
    message = (
        f"DOCUMENT_MAP ACTION REQUIRED: `{rel_path}` was just written but is NOT "
        f"registered in `.claude/DOCUMENT_MAP.md`. Add an entry now (before /end) "
        f"so future sessions can discover this file. "
        f"See knowledge/wiki/ or knowledge/ventures/ sections in DOCUMENT_MAP.md for format reference."
    )

    output = {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": message
        }
    }
    print(json.dumps(output))
    sys.exit(0)


if __name__ == '__main__':
    main()
